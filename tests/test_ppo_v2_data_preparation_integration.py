from pathlib import Path

import pandas as pd

from src.ppo_v2_data_contract import PPOV2SplitBoundarySpec
from src.ppo_v2_data_preparation_integration import (
    ALLOWED_INTEGRATION_EXECUTION_MODES,
    PPOV2DataPreparationIntegrationRequest,
    run_ppo_v2_data_preparation_integration,
)
from src.ppo_v2_data_preparation_interface import PPOV2DataPreparationRequest


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


def _data_preparation_request(**overrides) -> PPOV2DataPreparationRequest:
    values = {
        "raw_df": _valid_raw_data(),
        "split_boundary_spec": _valid_split_spec(),
        "observation_columns": ("Open", "High", "Low", "Close", "Volume"),
        "holdout_uses": ("final_validation",),
        "preprocessing_fit_split": "train_df",
    }
    values.update(overrides)

    return PPOV2DataPreparationRequest(**values)


def _integration_request(**overrides) -> PPOV2DataPreparationIntegrationRequest:
    values = {
        "data_preparation_request": _data_preparation_request(),
        "run_identifier": "v1_79_test_run",
        "execution_mode": "validation_only",
    }
    values.update(overrides)

    return PPOV2DataPreparationIntegrationRequest(**values)


def test_integration_accepts_valid_in_memory_data_and_calls_existing_interface():
    result = run_ppo_v2_data_preparation_integration(_integration_request())

    assert result.is_valid
    assert result.errors == ()
    assert result.boundary_decision == "PASS"
    assert result.data_preparation_result is not None
    assert result.data_preparation_result.is_valid
    assert len(result.data_preparation_result.train_df) == 4
    assert len(result.data_preparation_result.eval_df) == 4
    assert len(result.data_preparation_result.holdout_df) == 4
    assert result.integration_metadata["called_data_preparation_interface"] is True
    assert result.integration_metadata["execution_boundary"] == (
        "non_executing_in_memory_integration_only"
    )


def test_integration_fails_closed_for_invalid_execution_mode():
    result = run_ppo_v2_data_preparation_integration(
        _integration_request(execution_mode="submit_orders")
    )

    assert not result.is_valid
    assert result.data_preparation_result is None
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.integration_metadata["called_data_preparation_interface"] is False
    assert result.integration_errors == (
        "execution_mode must be one of: dry_run, validation_only",
    )


def test_integration_fails_closed_for_empty_run_identifier():
    result = run_ppo_v2_data_preparation_integration(
        _integration_request(run_identifier="   ")
    )

    assert not result.is_valid
    assert result.data_preparation_result is None
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.integration_metadata["called_data_preparation_interface"] is False
    assert result.integration_errors == ("run_identifier must be non-empty",)


def test_integration_propagates_raw_data_contract_errors():
    raw_df = _valid_raw_data()
    raw_df.loc[0, "Symbol"] = "TSLA"

    result = run_ppo_v2_data_preparation_integration(
        _integration_request(
            data_preparation_request=_data_preparation_request(raw_df=raw_df)
        )
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_DATA_PREPARATION_ERRORS"
    assert result.data_preparation_result is not None
    assert result.integration_metadata["called_data_preparation_interface"] is True
    assert any(
        "symbols outside approved PPO v2 universe" in error
        for error in result.errors
    )


def test_integration_propagates_observation_column_errors():
    result = run_ppo_v2_data_preparation_integration(
        _integration_request(
            data_preparation_request=_data_preparation_request(
                observation_columns=("Open", "Target")
            )
        )
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_DATA_PREPARATION_ERRORS"
    assert any("forbidden PPO observation columns present" in error for error in result.errors)


def test_integration_propagates_split_boundary_errors():
    invalid_spec = PPOV2SplitBoundarySpec(
        train_end="2024-01-03 16:00:00",
        eval_start="2024-01-04 09:30:00",
        eval_end="2024-01-05 16:00:00",
        holdout_start="2024-01-07 09:30:00",
        embargo_window="2 days",
    )

    result = run_ppo_v2_data_preparation_integration(
        _integration_request(
            data_preparation_request=_data_preparation_request(
                split_boundary_spec=invalid_spec
            )
        )
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_DATA_PREPARATION_ERRORS"
    assert "embargo gap is smaller than required embargo_window" in result.errors


def test_integration_propagates_holdout_policy_errors():
    result = run_ppo_v2_data_preparation_integration(
        _integration_request(
            data_preparation_request=_data_preparation_request(
                holdout_uses=("final_validation", "model_selection")
            )
        )
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_DATA_PREPARATION_ERRORS"
    assert any("holdout contains forbidden usage" in error for error in result.errors)


def test_integration_propagates_preprocessing_boundary_errors():
    result = run_ppo_v2_data_preparation_integration(
        _integration_request(
            data_preparation_request=_data_preparation_request(
                preprocessing_fit_split="holdout_df"
            )
        )
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_DATA_PREPARATION_ERRORS"
    assert "preprocessing must be fit on train_df only" in result.errors


def test_integration_metadata_preserves_non_authorizations():
    result = run_ppo_v2_data_preparation_integration(_integration_request())

    non_authorizations = result.integration_metadata["non_authorizations"]

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
    assert result.integration_metadata["allowed_execution_modes"] == (
        ALLOWED_INTEGRATION_EXECUTION_MODES
    )


def test_integration_is_deterministic_for_repeated_in_memory_calls():
    request = _integration_request()

    first = run_ppo_v2_data_preparation_integration(request)
    second = run_ppo_v2_data_preparation_integration(request)

    assert first.is_valid == second.is_valid
    assert first.boundary_decision == second.boundary_decision
    assert first.errors == second.errors
    assert first.integration_metadata["called_data_preparation_interface"] == (
        second.integration_metadata["called_data_preparation_interface"]
    )
    assert first.data_preparation_result is not None
    assert second.data_preparation_result is not None
    assert len(first.data_preparation_result.train_df) == len(
        second.data_preparation_result.train_df
    )
    assert len(first.data_preparation_result.eval_df) == len(
        second.data_preparation_result.eval_df
    )
    assert len(first.data_preparation_result.holdout_df) == len(
        second.data_preparation_result.holdout_df
    )


def test_integration_source_contains_no_execution_or_io_hooks():
    source_text = Path("src/ppo_v2_data_preparation_integration.py").read_text(
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
        "read_parquet",
        "requests.get",
        "alpaca",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source_text
