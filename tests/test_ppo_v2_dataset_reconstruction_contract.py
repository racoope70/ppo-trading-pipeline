from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.ppo_v2_data_contract import (
    FINAL_COLUMNS,
    GAP_EVIDENCE_FIELDS,
    OLD_MISSING_PATH,
    OUTPUT_PATH,
    RECONSTRUCTION_CLASSIFICATION,
    SYMBOLS,
    GovernedContractError,
    validate_gap_evidence,
    validate_output_path,
    validate_reconstructed_frame,
)
from src.ppo_v2_dataset_reconstruction import (
    ADJUSTMENT,
    FEED,
    REQUEST_CLASS,
    REQUEST_DATETIMES,
    RETRIEVAL_METHOD,
    SOURCE_CLIENT,
    TIMEFRAME,
    ReconstructionAuthorizationError,
    describe_contract,
    fetch_market_data,
    generate_dataset,
)


def _valid_frame() -> pd.DataFrame:
    data: dict[str, object] = {
        "Symbol": pd.Series(["AAPL"], dtype="string"),
        "Datetime": pd.Series(pd.to_datetime(["2023-01-03T15:00:00Z"])),
    }
    for column in FINAL_COLUMNS[2:]:
        data[column] = pd.Series([1.0], dtype="float64")
    return pd.DataFrame(data, columns=FINAL_COLUMNS)


def test_governed_identity_and_alpaca_literals_are_explicit():
    assert RECONSTRUCTION_CLASSIFICATION == "SUPERSEDING_GOVERNED_ALPACA_ALIGNED_RECONSTRUCTION"
    assert SYMBOLS == ("AAPL", "AMD", "MRK", "PFE", "UNH", "XOM")
    assert SOURCE_CLIENT == "alpaca.data.historical.StockHistoricalDataClient"
    assert REQUEST_CLASS == "alpaca.data.requests.StockBarsRequest"
    assert RETRIEVAL_METHOD == "StockHistoricalDataClient.get_stock_bars"
    assert TIMEFRAME == "TimeFrame.Hour"
    assert FEED == "DataFeed.IEX"
    assert ADJUSTMENT == "Adjustment.RAW"
    assert REQUEST_DATETIMES == "TIMEZONE_AWARE_UTC"
    assert describe_contract()["symbols"] == list(SYMBOLS)


def test_output_path_requires_v3_08_and_rejects_missing_v3_07_identity():
    assert validate_output_path(OUTPUT_PATH) == OUTPUT_PATH
    with pytest.raises(GovernedContractError):
        validate_output_path(OLD_MISSING_PATH)
    with pytest.raises(GovernedContractError):
        validate_output_path(Path("data/processed/ppo_v2/other.parquet"))


def test_exact_27_column_frame_contract_accepts_valid_frame():
    assert len(FINAL_COLUMNS) == 27
    validate_reconstructed_frame(_valid_frame())


def test_frame_contract_rejects_order_dtype_nonfinite_and_duplicates():
    with pytest.raises(GovernedContractError):
        validate_reconstructed_frame(_valid_frame()[list(reversed(FINAL_COLUMNS))])

    wrong_dtype = _valid_frame()
    wrong_dtype["Open"] = wrong_dtype["Open"].astype("float32")
    with pytest.raises(GovernedContractError):
        validate_reconstructed_frame(wrong_dtype)

    nonfinite = _valid_frame()
    nonfinite.loc[0, "return_1h"] = np.inf
    with pytest.raises(GovernedContractError):
        validate_reconstructed_frame(nonfinite)

    duplicate = pd.concat([_valid_frame(), _valid_frame()], ignore_index=True)
    with pytest.raises(GovernedContractError):
        validate_reconstructed_frame(duplicate)


def test_gap_evidence_is_complete_controlled_and_zero_tolerance():
    record = {field: 0 for field in GAP_EVIDENCE_FIELDS}
    record["gap_reason_code"] = "OBSERVED"
    validate_gap_evidence(record)

    record["total_missing_count"] = 1
    record["gap_reason_code"] = "MISSING_EXPECTED_SLOT"
    with pytest.raises(GovernedContractError):
        validate_gap_evidence(record)


def test_network_and_dataset_actions_fail_closed_without_side_effects():
    with pytest.raises(ReconstructionAuthorizationError):
        fetch_market_data()
    with pytest.raises(ReconstructionAuthorizationError):
        generate_dataset()
