import json
from pathlib import Path

import pandas as pd
import pytest

from src.alpaca_ppo_retraining_config import (
    AlpacaPPORetrainingConfig,
    write_config_json,
)
from src.alpaca_ppo_retraining_runner import (
    filter_dataset_for_config,
    load_model_ready_dataset,
    run_retraining_integration,
    summarize_training_dataset,
)


def _model_ready_dataset(symbols=("AAPL", "AMD"), rows_per_symbol=80):
    rows = []

    for symbol in symbols:
        for i in range(rows_per_symbol):
            price = 100 + i * 0.1

            rows.append(
                {
                    "Datetime": pd.Timestamp("2026-01-01", tz="UTC")
                    + pd.Timedelta(hours=i),
                    "Open": price,
                    "High": price + 1,
                    "Low": price - 1,
                    "Close": price + 0.2,
                    "Volume": 1000 + i,
                    "SMA_20": price,
                    "STD_20": 1.0,
                    "Upper_Band": price + 2,
                    "Lower_Band": price - 2,
                    "EMA_10": price,
                    "EMA_50": price,
                    "RSI": 50.0,
                    "ATR": 1.5,
                    "Volatility": 0.02,
                    "Denoised_Close": price,
                    "Delta": 0.01,
                    "Gamma": 0.001,
                    "Return": 0.01 if i % 2 == 0 else -0.01,
                    "Target": 1 if i % 3 == 0 else 0,
                    "Symbol": symbol,
                }
            )

    return pd.DataFrame(rows)


def test_load_model_ready_dataset_requires_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_model_ready_dataset(tmp_path / "missing.csv")


def test_load_model_ready_dataset_requires_columns(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"Datetime": ["2026-01-01"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        load_model_ready_dataset(path)


def test_filter_dataset_for_config_keeps_configured_symbols():
    df = _model_ready_dataset(symbols=("AAPL", "AMD", "XOM"))
    config = AlpacaPPORetrainingConfig(symbols=("AAPL", "AMD"))

    filtered = filter_dataset_for_config(df, config)

    assert set(filtered["Symbol"].unique()) == {"AAPL", "AMD"}


def test_filter_dataset_for_config_rejects_missing_symbols():
    df = _model_ready_dataset(symbols=("AAPL",))
    config = AlpacaPPORetrainingConfig(symbols=("AAPL", "AMD"))

    with pytest.raises(ValueError, match="missing configured symbols"):
        filter_dataset_for_config(df, config)


def test_summarize_training_dataset_excludes_leakage_from_safe_features():
    df = _model_ready_dataset()

    summary = summarize_training_dataset(df)

    assert summary["rows"] == 160
    assert summary["symbols"] == ["AAPL", "AMD"]
    assert "Target" not in summary["safe_features"]
    assert "Return" not in summary["safe_features"]
    assert "Datetime" not in summary["safe_features"]
    assert "Symbol" not in summary["safe_features"]


def test_run_retraining_integration_dry_run_writes_metadata(tmp_path):
    dataset_path = tmp_path / "dataset.csv"
    provenance_path = tmp_path / "provenance.json"
    config_path = tmp_path / "config.json"
    results_dir = tmp_path / "reports"
    artifacts_dir = tmp_path / "models"

    _model_ready_dataset().to_csv(dataset_path, index=False)
    provenance_path.write_text("{}", encoding="utf-8")

    config = AlpacaPPORetrainingConfig(
        dataset_path=str(dataset_path),
        dataset_provenance_path=str(provenance_path),
        results_dir=str(results_dir),
        artifacts_dir=str(artifacts_dir),
        symbols=("AAPL", "AMD"),
    )
    write_config_json(config, config_path)

    summary = run_retraining_integration(
        config_path=config_path,
        dry_run=True,
        smoke=True,
        create_dataset_snapshot=True,
        run_id="unit_test_run",
    )

    run_dir = Path(summary["run_dir"])

    assert summary["passed"] is True
    assert summary["training_status"] == "SKIPPED_DRY_RUN"
    assert run_dir.exists()
    assert (run_dir / "retraining_config_snapshot.json").exists()
    assert (run_dir / "dataset_summary.json").exists()
    assert (run_dir / "final_summary.json").exists()
    assert (run_dir / "alpaca_model_ready_dataset_snapshot.csv").exists()


def test_run_retraining_integration_can_skip_dataset_snapshot(tmp_path):
    dataset_path = tmp_path / "dataset.csv"
    provenance_path = tmp_path / "provenance.json"
    config_path = tmp_path / "config.json"

    _model_ready_dataset().to_csv(dataset_path, index=False)
    provenance_path.write_text("{}", encoding="utf-8")

    config = AlpacaPPORetrainingConfig(
        dataset_path=str(dataset_path),
        dataset_provenance_path=str(provenance_path),
        results_dir=str(tmp_path / "reports"),
        artifacts_dir=str(tmp_path / "models"),
        symbols=("AAPL", "AMD"),
    )
    write_config_json(config, config_path)

    summary = run_retraining_integration(
        config_path=config_path,
        dry_run=True,
        smoke=True,
        create_dataset_snapshot=False,
        run_id="unit_test_no_snapshot",
    )

    assert summary["dataset_snapshot_path"] is None


def test_call_existing_training_loop_uses_walkforward_ppo(monkeypatch, tmp_path):
    import sys
    import types

    from src.alpaca_ppo_retraining_runner import call_existing_training_loop

    calls = []

    fake_train = types.ModuleType("src.train")
    fake_train.FINAL_MODEL_DIR = Path("old_models")
    fake_train.TOP_N_WINDOWS = 99
    fake_train.WINDOW_SIZE = 999
    fake_train.STEP_SIZE = 999

    def fake_validate_symbol_data(df, symbol):
        return True

    def fake_pick_params(symbol):
        return {"lr": 0.001, "batch": 32}

    def fake_walkforward_ppo(**kwargs):
        calls.append(kwargs)
        return [
            {
                "Ticker": kwargs["ticker"],
                "Timesteps": kwargs["timesteps"],
                "WindowSize": kwargs["window_size"],
                "StepSize": kwargs["step_size"],
            }
        ]

    fake_train.validate_symbol_data = fake_validate_symbol_data
    fake_train.pick_params = fake_pick_params
    fake_train.walkforward_ppo = fake_walkforward_ppo

    monkeypatch.setitem(sys.modules, "src.train", fake_train)

    df = _model_ready_dataset(symbols=("AAPL", "AMD"), rows_per_symbol=80)

    config = AlpacaPPORetrainingConfig(
        symbols=("AAPL", "AMD"),
        artifacts_dir=str(tmp_path / "alpaca_models"),
        results_dir=str(tmp_path / "alpaca_reports"),
        walkforward_window_size=60,
        walkforward_step_size=20,
        smoke_test_timesteps=123,
        training_timesteps=999,
        top_n_windows=2,
    )

    results = call_existing_training_loop(
        df=df,
        config=config,
        smoke=True,
    )

    assert len(results) == 2
    assert len(calls) == 2
    assert {call["ticker"] for call in calls} == {"AAPL", "AMD"}
    assert all(call["timesteps"] == 123 for call in calls)
    assert all(call["window_size"] == 60 for call in calls)
    assert all(call["step_size"] == 20 for call in calls)

    assert fake_train.FINAL_MODEL_DIR == Path(config.artifacts_dir)
    assert fake_train.TOP_N_WINDOWS == 2
    assert fake_train.WINDOW_SIZE == 60
    assert fake_train.STEP_SIZE == 20
