from pathlib import Path

import pandas as pd
import pytest

from src.ppo_v2_data_contract import PPOV2SplitBoundarySpec
from src.ppo_v2_data_preparation_interface import (
    PPOV2DataPreparationRequest,
    build_ppo_v2_data_preparation_interface,
)


def _valid_raw_data() -> pd.DataFrame:
    timestamps = [
        "2024-01-01 09:30:00",
        "2024-01-02 09:30:00",
        "2024-01-04 09:30:00",
        "2024-01-05 09:30:00",
        "2024-01-07 09:30:00",
        "2024-01-08 09:30:00",
    ]

    rows = []
    for symbol in ["AAPL", "AMD"]:
        for index, timestamp in enumerate(timestamps):
            open_price = 100.0 + index
            close_price = 100.5 + index
            rows.append(
                {
                    "Datetime": pd.Timestamp(timestamp),
                    "Symbol": symbol,
                    "Open": open_price,
                    "High": max(open_price, close_price) + 1.0,
                    "Low": min(open_price, close_price) - 1.0,
                    "Close": close_price,
                    "Volume": 1_000 + index,
                }
            )

    return pd.DataFrame(rows)


def _valid_split_spec() -> PPOV2SplitBoundarySpec:
    return PPOV2SplitBoundarySpec(
        train_end="2024-01-02 16:00:00",
        eval_start="2024-01-04 09:30:00",
        eval_end="2024-01-05 16:00:00",
        holdout_start="2024-01-07 09:30:00",
        embargo_window="1 days",
    )


def _valid_request(**overrides) -> PPOV2DataPreparationRequest:
    values = {
        "raw_df": _valid_raw_data(),
        "split_boundary_spec": _valid_split_spec(),
        "observation_columns": ("Open", "High", "Low", "Close", "Volume"),
        "holdout_uses": ("final_validation",),
        "preprocessing_fit_split": "train_df",
    }
    values.update(overrides)

    return PPOV2DataPreparationRequest(**values)


def test_data_preparation_interface_splits_valid_in_memory_data():
    result = build_ppo_v2_data_preparation_interface(_valid_request())

    assert result.is_valid
    assert result.errors == ()

    assert len(result.train_df) == 4
    assert len(result.eval_df) == 4
    assert len(result.holdout_df) == 4

    assert result.observation_columns == ("Open", "High", "Low", "Close", "Volume")
    assert "_PPOV2ParsedDatetime" not in result.train_df.columns
    assert "_PPOV2ParsedDatetime" not in result.eval_df.columns
    assert "_PPOV2ParsedDatetime" not in result.holdout_df.columns

    assert result.validation_metadata["execution_boundary"] == (
        "non_executing_in_memory_only"
    )
    assert result.validation_metadata["raw_rows"] == 12
    assert result.validation_metadata["train_rows"] == 4
    assert result.validation_metadata["eval_rows"] == 4
    assert result.validation_metadata["holdout_rows"] == 4
    assert result.validation_metadata["error_count"] == 0


def test_data_preparation_interface_fails_closed_for_invalid_raw_contract():
    raw_df = _valid_raw_data()
    raw_df.loc[0, "Symbol"] = "TSLA"

    result = build_ppo_v2_data_preparation_interface(_valid_request(raw_df=raw_df))

    assert not result.is_valid
    assert result.train_df.empty
    assert result.eval_df.empty
    assert result.holdout_df.empty
    assert any(
        "symbols outside approved PPO v2 universe" in error
        for error in result.data_contract_errors
    )
    assert result.validation_metadata["error_count"] >= 1


@pytest.mark.parametrize("forbidden_column", ["Target", "Return", "Datetime", "Symbol"])
def test_data_preparation_interface_fails_closed_for_forbidden_observation_columns(
    forbidden_column,
):
    result = build_ppo_v2_data_preparation_interface(
        _valid_request(observation_columns=("Open", forbidden_column))
    )

    assert not result.is_valid
    assert result.train_df.empty
    assert result.eval_df.empty
    assert result.holdout_df.empty
    assert any(
        "forbidden PPO observation columns present" in error
        for error in result.observation_column_errors
    )


def test_data_preparation_interface_fails_closed_for_missing_observation_columns():
    result = build_ppo_v2_data_preparation_interface(
        _valid_request(observation_columns=("Open", "missing_future_feature"))
    )

    assert not result.is_valid
    assert result.train_df.empty
    assert result.eval_df.empty
    assert result.holdout_df.empty
    assert any(
        "observation columns missing from raw data" in error
        for error in result.observation_column_errors
    )


def test_data_preparation_interface_fails_closed_for_invalid_split_boundary():
    invalid_spec = PPOV2SplitBoundarySpec(
        train_end="2024-01-03 16:00:00",
        eval_start="2024-01-04 09:30:00",
        eval_end="2024-01-05 16:00:00",
        holdout_start="2024-01-07 09:30:00",
        embargo_window="2 days",
    )

    result = build_ppo_v2_data_preparation_interface(
        _valid_request(split_boundary_spec=invalid_spec)
    )

    assert not result.is_valid
    assert result.train_df.empty
    assert result.eval_df.empty
    assert result.holdout_df.empty
    assert "embargo gap is smaller than required embargo_window" in (
        result.split_boundary_errors
    )


def test_data_preparation_interface_fails_closed_for_forbidden_holdout_usage():
    result = build_ppo_v2_data_preparation_interface(
        _valid_request(holdout_uses=("final_validation", "model_selection"))
    )

    assert not result.is_valid
    assert result.train_df.empty
    assert result.eval_df.empty
    assert result.holdout_df.empty
    assert any(
        "holdout contains forbidden usage" in error
        for error in result.holdout_policy_errors
    )


def test_data_preparation_interface_fails_closed_for_invalid_preprocessing_split():
    result = build_ppo_v2_data_preparation_interface(
        _valid_request(preprocessing_fit_split="holdout_df")
    )

    assert not result.is_valid
    assert result.train_df.empty
    assert result.eval_df.empty
    assert result.holdout_df.empty
    assert result.preprocessing_boundary_errors == (
        "preprocessing must be fit on train_df only",
    )


def test_data_preparation_interface_metadata_preserves_non_authorizations():
    result = build_ppo_v2_data_preparation_interface(_valid_request())

    non_authorizations = result.validation_metadata["non_authorizations"]

    assert "data_fetching" in non_authorizations
    assert "generated_dataset_creation" in non_authorizations
    assert "training_script_creation" in non_authorizations
    assert "actual_retraining_execution" in non_authorizations
    assert "model_artifact_creation" in non_authorizations
    assert "paper_order_submission" in non_authorizations
    assert "live_order_submission" in non_authorizations
    assert "controlled_submit" in non_authorizations
    assert "ppo_rf_deployment" in non_authorizations
    assert "ppo_xgboost_deployment" in non_authorizations


def test_data_preparation_interface_source_contains_no_execution_or_io_hooks():
    source_text = Path("src/ppo_v2_data_preparation_interface.py").read_text(
        encoding="utf-8"
    )

    forbidden_fragments = (
        "TradingClient",
        "StockHistoricalDataClient",
        "submit_order",
        "PPO.load",
        ".learn(",
        ".fit(",
        "joblib.dump",
        "torch.save",
        "pickle.dump",
        ".to_csv",
        ".to_parquet",
        "read_csv",
        "requests.get",
        "alpaca",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source_text
