from dataclasses import replace
from pathlib import Path
import re

import pandas as pd
import pytest

from src.ppo_v2_controlled_training_execution_dry_run import (
    PPOV2ControlledTrainingExecutionDryRunRequest,
    build_ppo_v2_controlled_training_execution_dry_run,
)
from src.ppo_v2_training_configuration import (
    PPOV2TrainingConfigurationRequest,
    build_ppo_v2_training_configuration,
)
from src.ppo_v2_training_input_handoff import PPOV2TrainingInputHandoffResult


OBSERVATION_COLUMNS = ("Open", "High", "Low", "Close", "Volume", "SMA_20")


def _frame(columns=OBSERVATION_COLUMNS):
    return pd.DataFrame(
        {
            column: [1.0, 2.0, 3.0]
            for column in columns
        }
    )


def _valid_handoff_result(observation_columns=OBSERVATION_COLUMNS):
    return PPOV2TrainingInputHandoffResult(
        train_df=_frame(observation_columns),
        eval_df=_frame(observation_columns),
        holdout_df=_frame(observation_columns),
        observation_columns=tuple(observation_columns),
        handoff_errors=(),
        handoff_metadata={"training_authorized": False},
        boundary_decision="PASS",
    )


def _valid_training_configuration_result():
    result = build_ppo_v2_training_configuration(
        PPOV2TrainingConfigurationRequest(
            training_input_handoff_result=_valid_handoff_result(),
        )
    )

    assert result.boundary_decision == "PASS"
    assert result.configuration_errors == ()
    assert result.training_configuration is not None

    return result


def _valid_request():
    return PPOV2ControlledTrainingExecutionDryRunRequest(
        training_configuration_result=_valid_training_configuration_result(),
        expected_train_rows=3,
        expected_eval_rows=3,
        expected_holdout_rows=3,
        expected_observation_columns=OBSERVATION_COLUMNS,
    )


def _assert_failed_with(result, expected_error):
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.dry_run_manifest is None
    assert expected_error in result.dry_run_errors


def test_valid_dry_run_manifest_passes():
    result = build_ppo_v2_controlled_training_execution_dry_run(_valid_request())

    assert result.boundary_decision == "PASS"
    assert result.dry_run_errors == ()
    assert result.dry_run_manifest is not None
    assert result.dry_run_manifest["run_identifier"] == (
        "ppo_v2_controlled_training_execution_dry_run"
    )
    assert result.dry_run_manifest["training_configuration_summary"]["ppo_algorithm_family"] == "PPO"
    assert result.dry_run_manifest["training_input_summary"]["expected_train_rows"] == 3
    assert result.dry_run_manifest["training_input_summary"]["expected_eval_rows"] == 3
    assert result.dry_run_manifest["training_input_summary"]["expected_holdout_rows"] == 3
    assert result.dry_run_manifest["training_input_summary"]["observation_columns"] == (
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "SMA_20",
    )
    assert result.dry_run_manifest["training_execution_authorized"] is False
    assert result.dry_run_manifest["artifact_creation_authorized"] is False
    assert result.dry_run_manifest["controlled_submit_authorized"] is False


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_error"),
    [
        ("run_identifier", "", "run_identifier must be a non-empty string"),
        ("execution_mode", "train", "execution_mode is not allowed for dry-run boundary"),
        (
            "training_input_source_name",
            "",
            "training_input_source_name must be a non-empty string",
        ),
        (
            "artifact_quarantine_root",
            "",
            "artifact_quarantine_root must be a non-empty string",
        ),
        ("log_quarantine_root", "", "log_quarantine_root must be a non-empty string"),
        (
            "configuration_snapshot_name",
            "",
            "configuration_snapshot_name must be a non-empty string",
        ),
        (
            "data_contract_snapshot_name",
            "",
            "data_contract_snapshot_name must be a non-empty string",
        ),
        ("expected_train_rows", 0, "expected_train_rows must be a positive integer"),
        ("expected_eval_rows", 0, "expected_eval_rows must be a positive integer"),
        ("expected_holdout_rows", 0, "expected_holdout_rows must be a positive integer"),
    ],
)
def test_invalid_request_fields_fail_closed(field_name, invalid_value, expected_error):
    request = replace(_valid_request(), **{field_name: invalid_value})

    result = build_ppo_v2_controlled_training_execution_dry_run(request)

    _assert_failed_with(result, expected_error)


@pytest.mark.parametrize(
    ("field_name", "expected_error"),
    [
        ("allow_training_execution", "training execution request is not authorized"),
        ("allow_artifact_creation", "artifact creation request is not authorized"),
        ("allow_data_fetching", "data fetching request is not authorized"),
        ("allow_dataset_writes", "dataset write request is not authorized"),
        ("allow_paper_orders", "paper order request is not authorized"),
        ("allow_live_orders", "live order request is not authorized"),
        ("allow_controlled_submit", "controlled submit request is not authorized"),
        ("allow_deployment_update", "deployment update request is not authorized"),
    ],
)
def test_permission_request_flags_fail_closed(field_name, expected_error):
    request = replace(_valid_request(), **{field_name: True})

    result = build_ppo_v2_controlled_training_execution_dry_run(request)

    _assert_failed_with(result, expected_error)


def test_missing_training_configuration_result_fails_closed():
    request = replace(_valid_request(), training_configuration_result=None)

    result = build_ppo_v2_controlled_training_execution_dry_run(request)

    _assert_failed_with(result, "training_configuration_result must be present")


def test_invalid_training_configuration_result_type_fails_closed():
    request = replace(_valid_request(), training_configuration_result="invalid")

    result = build_ppo_v2_controlled_training_execution_dry_run(request)

    _assert_failed_with(
        result,
        "training_configuration_result must be a PPOV2TrainingConfigurationResult",
    )


def test_rejected_training_configuration_result_fails_closed():
    rejected_result = replace(
        _valid_training_configuration_result(),
        boundary_decision="REJECTED_FAIL_CLOSED",
    )
    request = replace(_valid_request(), training_configuration_result=rejected_result)

    result = build_ppo_v2_controlled_training_execution_dry_run(request)

    _assert_failed_with(result, "training_configuration_result boundary_decision must be PASS")


def test_training_configuration_errors_fail_closed():
    rejected_result = replace(
        _valid_training_configuration_result(),
        configuration_errors=("configuration error",),
    )
    request = replace(_valid_request(), training_configuration_result=rejected_result)

    result = build_ppo_v2_controlled_training_execution_dry_run(request)

    _assert_failed_with(
        result,
        "training_configuration_result must not contain configuration_errors",
    )


def test_missing_training_configuration_object_fails_closed():
    rejected_result = replace(
        _valid_training_configuration_result(),
        training_configuration=None,
    )
    request = replace(_valid_request(), training_configuration_result=rejected_result)

    result = build_ppo_v2_controlled_training_execution_dry_run(request)

    _assert_failed_with(result, "training_configuration must be present")


def test_empty_expected_observation_columns_fail_closed():
    request = replace(_valid_request(), expected_observation_columns=())

    result = build_ppo_v2_controlled_training_execution_dry_run(request)

    _assert_failed_with(result, "expected_observation_columns must be non-empty")


def test_expected_observation_columns_mismatch_fails_closed():
    request = replace(_valid_request(), expected_observation_columns=("Open", "Close"))

    result = build_ppo_v2_controlled_training_execution_dry_run(request)

    _assert_failed_with(
        result,
        "expected_observation_columns must match training configuration observation columns",
    )


def test_non_request_object_fails_closed():
    result = build_ppo_v2_controlled_training_execution_dry_run(None)

    _assert_failed_with(
        result,
        "request must be a PPOV2ControlledTrainingExecutionDryRunRequest",
    )


def test_metadata_preserves_non_authorizations():
    result = build_ppo_v2_controlled_training_execution_dry_run(_valid_request())

    assert result.boundary_decision == "PASS"
    assert result.dry_run_metadata["training_authorized"] is False
    assert result.dry_run_metadata["training_execution_authorized"] is False
    assert result.dry_run_metadata["artifact_creation_authorized"] is False
    assert result.dry_run_metadata["data_fetching_authorized"] is False
    assert result.dry_run_metadata["dataset_write_authorized"] is False
    assert result.dry_run_metadata["paper_order_authorized"] is False
    assert result.dry_run_metadata["live_order_authorized"] is False
    assert result.dry_run_metadata["controlled_submit_authorized"] is False
    assert result.dry_run_metadata["deployment_update_authorized"] is False
    assert result.dry_run_metadata["ppo_rf_unblocked"] is False
    assert result.dry_run_metadata["ppo_xgboost_unblocked"] is False


def test_repeated_calls_are_deterministic():
    request = _valid_request()

    first = build_ppo_v2_controlled_training_execution_dry_run(request)
    second = build_ppo_v2_controlled_training_execution_dry_run(request)

    assert first.boundary_decision == second.boundary_decision
    assert first.dry_run_errors == second.dry_run_errors
    assert first.dry_run_manifest == second.dry_run_manifest
    assert first.dry_run_metadata == second.dry_run_metadata


def test_dry_run_source_boundary_scan_has_no_execution_hooks():
    source = Path("src/ppo_v2_controlled_training_execution_dry_run.py").read_text(
        encoding="utf-8"
    )
    forbidden_patterns = [
        r"TradingClient",
        r"StockHistoricalDataClient",
        r"submit_order",
        r"PPO\.load",
        r"\.learn\(",
        r"\.fit\(",
        r"joblib\.dump",
        r"torch\.save",
        r"pickle\.dump",
        r"\.to_csv",
        r"\.to_parquet",
        r"read_csv",
        r"read_parquet",
        r"requests\.get",
        r"alpaca",
    ]

    matches = [
        pattern
        for pattern in forbidden_patterns
        if re.search(pattern, source)
    ]

    assert matches == []
