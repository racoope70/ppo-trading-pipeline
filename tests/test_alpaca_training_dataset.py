import json
from pathlib import Path

import pandas as pd
import pytest

from src.data.alpaca_training_dataset import (
    AlpacaTrainingDatasetConfig,
    build_provenance,
    build_training_dataset,
    convert_alpaca_bars_to_ppo_schema,
    load_alpaca_bars_csv,
    run_builder,
    validate_model_ready_dataset,
)


def _sample_alpaca_bars(symbols=("AAPL", "AMD"), days=60) -> pd.DataFrame:
    rows = []
    base_price = {"AAPL": 100.0, "AMD": 200.0}

    dates = pd.bdate_range("2026-01-02", periods=days)
    intraday_times = ["14:30", "15:30", "16:30", "17:30", "18:30", "19:30"]

    for raw_symbol in symbols:
        symbol = str(raw_symbol).upper()
        counter = 0

        for date in dates:
            for time_text in intraday_times:
                ts = pd.Timestamp(f"{date.date()} {time_text}:00", tz="UTC")

                trend = counter * 0.03
                cycle = ((counter % 8) - 4) * 0.35
                alternating_close = 0.20 if counter % 2 == 0 else -0.20

                price = base_price.get(symbol, 150.0) + trend + cycle

                rows.append(
                    {
                        "timestamp": ts.isoformat(),
                        "symbol": raw_symbol,
                        "open": price,
                        "high": price + 1.0,
                        "low": price - 1.0,
                        "close": price + alternating_close,
                        "volume": 1000 + counter,
                        "trade_count": 10 + counter,
                        "vwap": price + 0.05,
                    }
                )
                counter += 1

    return pd.DataFrame(rows)

def test_load_alpaca_bars_csv_requires_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_alpaca_bars_csv(tmp_path / "missing.csv")


def test_convert_alpaca_bars_to_ppo_schema_creates_expected_columns():
    bars = _sample_alpaca_bars(symbols=("aapl",), days=5)

    converted = convert_alpaca_bars_to_ppo_schema(bars)

    assert list(converted.columns) == [
        "Datetime",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Symbol",
    ]
    assert converted["Symbol"].unique().tolist() == ["AAPL"]
    assert str(converted["Datetime"].dt.tz) == "UTC"


def test_convert_alpaca_bars_to_ppo_schema_rejects_missing_columns():
    bars = _sample_alpaca_bars().drop(columns=["close"])

    with pytest.raises(ValueError, match="missing required columns"):
        convert_alpaca_bars_to_ppo_schema(bars)


def test_build_training_dataset_creates_model_ready_dataset():
    bars = _sample_alpaca_bars()

    dataset, validation = build_training_dataset(
        bars,
        use_regime=True,
        use_sentiment=False,
    )

    assert not dataset.empty
    assert validation["passed"] is True
    assert set(validation["symbols"]) == {"AAPL", "AMD"}
    assert "Target" in dataset.columns
    assert "Return" in dataset.columns
    assert "Datetime" in dataset.columns
    assert "Symbol" in dataset.columns
    assert "Target" not in validation["safe_features"]
    assert "Return" not in validation["safe_features"]
    assert "Datetime" not in validation["safe_features"]
    assert "Symbol" not in validation["safe_features"]


def test_validate_model_ready_dataset_rejects_duplicate_symbol_datetime():
    bars = _sample_alpaca_bars()
    dataset, _validation = build_training_dataset(bars)

    duplicate = pd.concat([dataset, dataset.iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="Duplicate"):
        validate_model_ready_dataset(duplicate)


def test_build_provenance_contains_core_fields():
    bars = _sample_alpaca_bars()
    dataset, validation = build_training_dataset(bars)

    config = AlpacaTrainingDatasetConfig(
        input_csv="input.csv",
        output_csv="output.csv",
        provenance_json="provenance.json",
    )

    provenance = build_provenance(
        config=config,
        source_rows=len(bars),
        dataset=dataset,
        validation=validation,
    )

    assert provenance["source"] == "alpaca_historical_bars_to_ppo_training_dataset"
    assert provenance["source_rows"] == len(bars)
    assert provenance["model_ready_rows"] == len(dataset)
    assert provenance["validation"]["passed"] is True


def test_run_builder_writes_dataset_and_provenance(tmp_path):
    bars = _sample_alpaca_bars()
    input_csv = tmp_path / "alpaca_bars.csv"
    output_csv = tmp_path / "model_ready.csv"
    provenance_json = tmp_path / "provenance.json"

    bars.to_csv(input_csv, index=False)

    config = AlpacaTrainingDatasetConfig(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        provenance_json=str(provenance_json),
    )

    dataset, validation, saved_csv, saved_provenance = run_builder(config)

    assert saved_csv.exists()
    assert saved_provenance.exists()
    assert len(dataset) == validation["rows"]

    metadata = json.loads(Path(saved_provenance).read_text(encoding="utf-8"))
    assert metadata["validation"]["passed"] is True