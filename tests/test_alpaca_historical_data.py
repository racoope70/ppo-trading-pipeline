import json

import pandas as pd
import pytest

from src.data.alpaca_historical_data import (
    AlpacaHistoricalDataConfig,
    build_provenance,
    dataset_file_stem,
    normalize_alpaca_bars_dataframe,
    parse_datetime_utc,
    parse_symbols,
    save_bars_dataset,
    validate_bars_dataframe,
)


def _sample_multiindex_bars() -> pd.DataFrame:
    index = pd.MultiIndex.from_tuples(
        [
            ("AAPL", pd.Timestamp("2026-01-02 14:30:00", tz="UTC")),
            ("AAPL", pd.Timestamp("2026-01-02 15:30:00", tz="UTC")),
            ("AMD", pd.Timestamp("2026-01-02 14:30:00", tz="UTC")),
        ],
        names=["symbol", "timestamp"],
    )

    return pd.DataFrame(
        {
            "open": [100.0, 101.0, 200.0],
            "high": [102.0, 103.0, 205.0],
            "low": [99.0, 100.0, 198.0],
            "close": [101.0, 102.0, 204.0],
            "volume": [1000, 1100, 2000],
            "trade_count": [10, 11, 20],
            "vwap": [100.5, 101.5, 202.0],
        },
        index=index,
    )


def test_parse_symbols_from_string_and_list():
    assert parse_symbols("aapl, amd AAPL") == ["AAPL", "AMD"]
    assert parse_symbols(["mrk", "pfe, unh"]) == ["MRK", "PFE", "UNH"]


def test_parse_symbols_rejects_empty():
    with pytest.raises(ValueError, match="At least one symbol"):
        parse_symbols("")


def test_parse_datetime_utc_date_only():
    dt = parse_datetime_utc("2026-01-02")

    assert dt.tzinfo is not None
    assert dt.isoformat() == "2026-01-02T00:00:00+00:00"


def test_normalize_multiindex_bars_dataframe():
    normalized = normalize_alpaca_bars_dataframe(
        _sample_multiindex_bars(),
        expected_symbols=["AAPL", "AMD"],
    )

    assert list(normalized.columns) == [
        "timestamp",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "trade_count",
        "vwap",
    ]
    assert set(normalized["symbol"]) == {"AAPL", "AMD"}
    assert str(normalized["timestamp"].dt.tz) == "UTC"


def test_validate_bars_dataframe_passes_for_valid_data():
    normalized = normalize_alpaca_bars_dataframe(
        _sample_multiindex_bars(),
        expected_symbols=["AAPL", "AMD"],
    )

    result = validate_bars_dataframe(
        normalized,
        expected_symbols=["AAPL", "AMD"],
    )

    assert result["passed"] is True
    assert result["rows"] == 3
    assert result["symbols"] == ["AAPL", "AMD"]


def test_validate_bars_dataframe_rejects_duplicates():
    normalized = normalize_alpaca_bars_dataframe(
        _sample_multiindex_bars(),
        expected_symbols=["AAPL", "AMD"],
    )
    duplicate = pd.concat([normalized, normalized.iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="Duplicate"):
        validate_bars_dataframe(duplicate, expected_symbols=["AAPL", "AMD"])


def test_validate_bars_dataframe_rejects_missing_symbol():
    normalized = normalize_alpaca_bars_dataframe(
        _sample_multiindex_bars(),
        expected_symbols=["AAPL", "AMD"],
    )

    with pytest.raises(ValueError, match="Missing expected symbols"):
        validate_bars_dataframe(normalized, expected_symbols=["AAPL", "AMD", "XOM"])


def test_dataset_file_stem_is_stable():
    config = AlpacaHistoricalDataConfig(
        symbols=["AAPL", "AMD"],
        start="2026-01-01",
        end="2026-01-31",
    )

    assert dataset_file_stem(config) == "alpaca_bars_AAPL_AMD_1h_iex_20260101_20260131"


def test_build_provenance_contains_core_fields():
    normalized = normalize_alpaca_bars_dataframe(
        _sample_multiindex_bars(),
        expected_symbols=["AAPL", "AMD"],
    )
    validation = validate_bars_dataframe(
        normalized,
        expected_symbols=["AAPL", "AMD"],
    )
    config = AlpacaHistoricalDataConfig(
        symbols=["AAPL", "AMD"],
        start="2026-01-01",
        end="2026-01-31",
    )

    provenance = build_provenance(
        config=config,
        df=normalized,
        validation=validation,
    )

    assert provenance["source"] == "alpaca_historical_stock_bars"
    assert provenance["symbols"] == ["AAPL", "AMD"]
    assert provenance["rows"] == 3
    assert provenance["validation"]["passed"] is True


def test_save_bars_dataset_writes_csv_and_provenance(tmp_path):
    normalized = normalize_alpaca_bars_dataframe(
        _sample_multiindex_bars(),
        expected_symbols=["AAPL", "AMD"],
    )
    validation = validate_bars_dataframe(
        normalized,
        expected_symbols=["AAPL", "AMD"],
    )
    config = AlpacaHistoricalDataConfig(
        symbols=["AAPL", "AMD"],
        start="2026-01-01",
        end="2026-01-31",
        output_dir=str(tmp_path),
    )

    csv_path, provenance_path = save_bars_dataset(
        normalized,
        config=config,
        validation=validation,
    )

    assert csv_path.exists()
    assert provenance_path.exists()

    saved_provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    assert saved_provenance["rows"] == 3
