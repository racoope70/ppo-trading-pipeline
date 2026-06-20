from dataclasses import replace
from pathlib import Path

import pandas as pd

from src.ppo_v2_data_contract import PPOV2SplitBoundarySpec
from src.ppo_v2_data_preparation_integration import (
    PPOV2DataPreparationIntegrationRequest,
    PPOV2DataPreparationIntegrationResult,
    run_ppo_v2_data_preparation_integration,
)
from src.ppo_v2_data_preparation_interface import PPOV2DataPreparationRequest
from src.ppo_v2_training_input_handoff import (
    ALLOWED_HANDOFF_EXECUTION_MODES,
    ALLOWED_HOLDOUT_USES,
    PPOV2TrainingInputHandoffRequest,
    build_ppo_v2_training_input_handoff,
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


def _valid_integration_result():
    integration_request = PPOV2DataPreparationIntegrationRequest(
        data_preparation_request=_data_preparation_request(),
        run_identifier="v1_82_test_integration",
        execution_mode="validation_only",
    )

    return run_ppo_v2_data_preparation_integration(integration_request)


def _handoff_request(**overrides) -> PPOV2TrainingInputHandoffRequest:
    values = {
        "data_preparation_integration_result": _valid_integration_result(),
        "run_identifier": "v1_82_test_handoff",
        "execution_mode": "validation_only",
        "requested_holdout_uses": ("final_validation",),
    }
    values.update(overrides)

    return PPOV2TrainingInputHandoffRequest(**values)


def test_handoff_accepts_valid_in_memory_integration_result():
    result = build_ppo_v2_training_input_handoff(_handoff_request())

    assert result.is_valid
    assert result.errors == ()
    assert result.boundary_decision == "PASS"
    assert len(result.train_df) == 4
    assert len(result.eval_df) == 4
    assert len(result.holdout_df) == 4
    assert result.observation_columns == ("Open", "High", "Low", "Close", "Volume")
    assert result.handoff_metadata["training_authorized"] is False
    assert result.handoff_metadata["execution_boundary"] == (
        "non_executing_in_memory_training_input_handoff_only"
    )


def test_handoff_fails_closed_when_integration_result_is_missing():
    result = build_ppo_v2_training_input_handoff(
        _handoff_request(data_preparation_integration_result=None)
    )

    assert not result.is_valid
    assert result.train_df is None
    assert result.eval_df is None
    assert result.holdout_df is None
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.errors == ("data_preparation_integration_result must be present",)


def test_handoff_fails_closed_when_integration_result_is_invalid():
    invalid_integration_result = run_ppo_v2_data_preparation_integration(
        PPOV2DataPreparationIntegrationRequest(
            data_preparation_request=_data_preparation_request(),
            run_identifier="invalid_integration",
            execution_mode="submit_orders",
        )
    )

    result = build_ppo_v2_training_input_handoff(
        _handoff_request(
            data_preparation_integration_result=invalid_integration_result
        )
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert "data_preparation_integration_result must be valid" in result.errors
    assert "data_preparation_result must be present" in result.errors


def test_handoff_fails_closed_when_data_preparation_result_is_missing():
    invalid_result = PPOV2DataPreparationIntegrationResult(
        data_preparation_result=None,
        integration_errors=(),
        integration_metadata={},
        boundary_decision="PASS",
    )

    result = build_ppo_v2_training_input_handoff(
        _handoff_request(data_preparation_integration_result=invalid_result)
    )

    assert not result.is_valid
    assert "data_preparation_integration_result must be valid" in result.errors
    assert "data_preparation_result must be present" in result.errors


def test_handoff_fails_closed_for_empty_observation_columns():
    integration_result = _valid_integration_result()
    empty_column_result = replace(
        integration_result.data_preparation_result,
        observation_columns=(),
    )
    modified_integration_result = replace(
        integration_result,
        data_preparation_result=empty_column_result,
    )

    result = build_ppo_v2_training_input_handoff(
        _handoff_request(
            data_preparation_integration_result=modified_integration_result
        )
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert "observation_columns must be non-empty" in result.errors


def test_handoff_fails_closed_for_forbidden_observation_columns():
    integration_result = _valid_integration_result()
    forbidden_column_result = replace(
        integration_result.data_preparation_result,
        observation_columns=("Open", "Target"),
    )
    modified_integration_result = replace(
        integration_result,
        data_preparation_result=forbidden_column_result,
    )

    result = build_ppo_v2_training_input_handoff(
        _handoff_request(
            data_preparation_integration_result=modified_integration_result
        )
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert "forbidden training-input columns present: Target" in result.errors


def test_handoff_fails_closed_for_holdout_training_request():
    result = build_ppo_v2_training_input_handoff(
        _handoff_request(requested_holdout_uses=("training",))
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.errors == (
        "holdout usage is limited to final_validation; forbidden uses: training",
    )


def test_handoff_fails_closed_for_holdout_model_selection_request():
    result = build_ppo_v2_training_input_handoff(
        _handoff_request(requested_holdout_uses=("model_selection",))
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.errors == (
        "holdout usage is limited to final_validation; forbidden uses: model_selection",
    )


def test_handoff_fails_closed_for_invalid_execution_mode():
    result = build_ppo_v2_training_input_handoff(
        _handoff_request(execution_mode="train_model")
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.errors == (
        "execution_mode must be one of: dry_run, validation_only",
    )


def test_handoff_fails_closed_for_empty_run_identifier():
    result = build_ppo_v2_training_input_handoff(
        _handoff_request(run_identifier="   ")
    )

    assert not result.is_valid
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.errors == ("run_identifier must be non-empty",)


def test_handoff_metadata_preserves_non_authorizations():
    result = build_ppo_v2_training_input_handoff(_handoff_request())

    non_authorizations = result.handoff_metadata["non_authorizations"]

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
    assert result.handoff_metadata["allowed_execution_modes"] == (
        ALLOWED_HANDOFF_EXECUTION_MODES
    )
    assert result.handoff_metadata["allowed_holdout_uses"] == ALLOWED_HOLDOUT_USES


def test_handoff_is_deterministic_for_repeated_in_memory_calls():
    request = _handoff_request()

    first = build_ppo_v2_training_input_handoff(request)
    second = build_ppo_v2_training_input_handoff(request)

    assert first.is_valid == second.is_valid
    assert first.boundary_decision == second.boundary_decision
    assert first.errors == second.errors
    assert first.observation_columns == second.observation_columns
    assert len(first.train_df) == len(second.train_df)
    assert len(first.eval_df) == len(second.eval_df)
    assert len(first.holdout_df) == len(second.holdout_df)


def test_handoff_source_contains_no_execution_or_io_hooks():
    source_text = Path("src/ppo_v2_training_input_handoff.py").read_text(
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
