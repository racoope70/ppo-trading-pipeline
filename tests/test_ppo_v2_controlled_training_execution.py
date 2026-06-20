from dataclasses import replace
from pathlib import Path
import re

import pandas as pd
import pytest

from src.ppo_v2_controlled_training_execution import (
    REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS,
    PPOV2ControlledTrainingExecutionRequest,
    build_ppo_v2_controlled_training_execution,
)
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


def _valid_dry_run_result(training_configuration_result):
    result = build_ppo_v2_controlled_training_execution_dry_run(
        PPOV2ControlledTrainingExecutionDryRunRequest(
            training_configuration_result=training_configuration_result,
            expected_train_rows=3,
            expected_eval_rows=3,
            expected_holdout_rows=3,
            expected_observation_columns=OBSERVATION_COLUMNS,
        )
    )

    assert result.boundary_decision == "PASS"
    assert result.dry_run_errors == ()
    assert result.dry_run_manifest is not None

    return result


def _valid_training_pair():
    training_configuration_result = _valid_training_configuration_result()
    dry_run_result = _valid_dry_run_result(training_configuration_result)
    return training_configuration_result, dry_run_result


def _valid_request():
    training_configuration_result, dry_run_result = _valid_training_pair()
    return PPOV2ControlledTrainingExecutionRequest(
        dry_run_result=dry_run_result,
        training_configuration_result=training_configuration_result,
    )


def _assert_failed_with(result, expected_error):
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.execution_manifest is None
    assert expected_error in result.execution_errors


def test_valid_execution_manifest_passes():
    result = build_ppo_v2_controlled_training_execution(_valid_request())

    assert result.boundary_decision == "PASS"
    assert result.execution_errors == ()
    assert result.execution_manifest is not None
    assert result.execution_manifest["run_identifier"] == "ppo_v2_controlled_training_execution"
    assert result.execution_manifest["training_input_source_name"] == (
        "validated_in_memory_training_input_handoff"
    )
    assert result.execution_manifest["training_configuration_summary"]["ppo_algorithm_family"] == "PPO"
    assert result.execution_manifest["seed"] == 42
    assert result.execution_manifest["timeout_seconds"] == 3_600
    assert result.execution_manifest["historical_validation_protections"] == (
        REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS
    )
    assert result.execution_manifest["training_execution_authorized"] is False
    assert result.execution_manifest["artifact_creation_authorized"] is False
    assert result.execution_manifest["model_promotion_authorized"] is False
    assert result.execution_manifest["paper_order_authorized"] is False
    assert result.execution_manifest["live_order_authorized"] is False
    assert result.execution_manifest["controlled_submit_authorized"] is False
    assert result.execution_manifest["ppo_rf_unblocked"] is False
    assert result.execution_manifest["ppo_xgboost_unblocked"] is False


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_error"),
    [
        ("run_identifier", "", "run_identifier must be a non-empty string"),
        (
            "execution_mode",
            "controlled_training_execution",
            "execution_mode is not allowed for controlled execution scaffold",
        ),
        (
            "training_input_source_name",
            "",
            "training_input_source_name must be a non-empty string",
        ),
        (
            "training_input_reference",
            "",
            "training_input_reference must be a non-empty string",
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
        ("model_output_name", "", "model_output_name must be a non-empty string"),
        ("training_log_name", "", "training_log_name must be a non-empty string"),
        ("metrics_output_name", "", "metrics_output_name must be a non-empty string"),
        ("seed", -1, "seed must be a non-negative integer"),
        ("timeout_seconds", 0, "timeout_seconds must be a positive integer"),
    ],
)
def test_invalid_request_fields_fail_closed(field_name, invalid_value, expected_error):
    request = replace(_valid_request(), **{field_name: invalid_value})

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(result, expected_error)


@pytest.mark.parametrize(
    ("field_name", "expected_error"),
    [
        ("allow_training_execution", "training execution request is not authorized"),
        ("allow_artifact_creation", "artifact creation request is not authorized"),
        ("allow_model_promotion", "model promotion request is not authorized"),
        ("allow_data_fetching", "data fetching request is not authorized"),
        ("allow_dataset_writes", "dataset write request is not authorized"),
        ("allow_paper_orders", "paper order request is not authorized"),
        ("allow_live_orders", "live order request is not authorized"),
        ("allow_controlled_submit", "controlled submit request is not authorized"),
        ("allow_hybrid_continuation", "hybrid continuation request is not authorized"),
    ],
)
def test_permission_request_flags_fail_closed(field_name, expected_error):
    request = replace(_valid_request(), **{field_name: True})

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(result, expected_error)


def test_missing_dry_run_result_fails_closed():
    request = replace(_valid_request(), dry_run_result=None)

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(result, "dry_run_result must be present")


def test_invalid_dry_run_result_type_fails_closed():
    request = replace(_valid_request(), dry_run_result="invalid")

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(
        result,
        "dry_run_result must be a PPOV2ControlledTrainingExecutionDryRunResult",
    )


def test_rejected_dry_run_result_fails_closed():
    request = _valid_request()
    rejected_dry_run_result = replace(
        request.dry_run_result,
        boundary_decision="REJECTED_FAIL_CLOSED",
    )
    request = replace(request, dry_run_result=rejected_dry_run_result)

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(result, "dry_run_result boundary_decision must be PASS")


def test_dry_run_errors_fail_closed():
    request = _valid_request()
    rejected_dry_run_result = replace(
        request.dry_run_result,
        dry_run_errors=("dry-run error",),
    )
    request = replace(request, dry_run_result=rejected_dry_run_result)

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(result, "dry_run_result must not contain dry_run_errors")


def test_missing_dry_run_manifest_fails_closed():
    request = _valid_request()
    rejected_dry_run_result = replace(
        request.dry_run_result,
        dry_run_manifest=None,
    )
    request = replace(request, dry_run_result=rejected_dry_run_result)

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(result, "dry_run_manifest must be present")


def test_dry_run_manifest_authorization_fails_closed():
    request = _valid_request()
    manifest = dict(request.dry_run_result.dry_run_manifest)
    manifest["training_execution_authorized"] = True
    rejected_dry_run_result = replace(
        request.dry_run_result,
        dry_run_manifest=manifest,
    )
    request = replace(request, dry_run_result=rejected_dry_run_result)

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(
        result,
        "dry_run_manifest training_execution_authorized must be False",
    )


def test_training_input_source_mismatch_fails_closed():
    request = replace(_valid_request(), training_input_source_name="different-source")

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(result, "training_input_source_name must match dry_run_manifest")


def test_missing_training_configuration_result_fails_closed():
    request = replace(_valid_request(), training_configuration_result=None)

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(result, "training_configuration_result must be present")


def test_invalid_training_configuration_result_type_fails_closed():
    request = replace(_valid_request(), training_configuration_result="invalid")

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(
        result,
        "training_configuration_result must be a PPOV2TrainingConfigurationResult",
    )


def test_rejected_training_configuration_result_fails_closed():
    request = _valid_request()
    rejected_configuration_result = replace(
        request.training_configuration_result,
        boundary_decision="REJECTED_FAIL_CLOSED",
    )
    request = replace(request, training_configuration_result=rejected_configuration_result)

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(
        result,
        "training_configuration_result boundary_decision must be PASS",
    )


def test_training_configuration_errors_fail_closed():
    request = _valid_request()
    rejected_configuration_result = replace(
        request.training_configuration_result,
        configuration_errors=("configuration error",),
    )
    request = replace(request, training_configuration_result=rejected_configuration_result)

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(
        result,
        "training_configuration_result must not contain configuration_errors",
    )


def test_missing_training_configuration_object_fails_closed():
    request = _valid_request()
    rejected_configuration_result = replace(
        request.training_configuration_result,
        training_configuration=None,
    )
    request = replace(request, training_configuration_result=rejected_configuration_result)

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(result, "training_configuration must be present")


def test_seed_mismatch_fails_closed():
    request = replace(_valid_request(), seed=999)

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(result, "seed must match training configuration seed")


def test_missing_historical_validation_protection_fails_closed():
    request = replace(
        _valid_request(),
        historical_validation_protections=REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS[:-1],
    )

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(result, "historical validation protections are incomplete")


def test_unsupported_historical_validation_protection_fails_closed():
    request = replace(
        _valid_request(),
        historical_validation_protections=(
            *REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS,
            "unsupported protection",
        ),
    )

    result = build_ppo_v2_controlled_training_execution(request)

    _assert_failed_with(
        result,
        "historical validation protections contain unsupported entries",
    )


def test_non_request_object_fails_closed():
    result = build_ppo_v2_controlled_training_execution(None)

    _assert_failed_with(
        result,
        "request must be a PPOV2ControlledTrainingExecutionRequest",
    )


def test_metadata_preserves_non_authorizations():
    result = build_ppo_v2_controlled_training_execution(_valid_request())

    assert result.boundary_decision == "PASS"
    assert result.execution_metadata["training_authorized"] is False
    assert result.execution_metadata["training_execution_authorized"] is False
    assert result.execution_metadata["artifact_creation_authorized"] is False
    assert result.execution_metadata["model_promotion_authorized"] is False
    assert result.execution_metadata["data_fetching_authorized"] is False
    assert result.execution_metadata["dataset_write_authorized"] is False
    assert result.execution_metadata["paper_order_authorized"] is False
    assert result.execution_metadata["live_order_authorized"] is False
    assert result.execution_metadata["controlled_submit_authorized"] is False
    assert result.execution_metadata["hybrid_continuation_authorized"] is False
    assert result.execution_metadata["ppo_rf_unblocked"] is False
    assert result.execution_metadata["ppo_xgboost_unblocked"] is False


def test_repeated_calls_are_deterministic():
    request = _valid_request()

    first = build_ppo_v2_controlled_training_execution(request)
    second = build_ppo_v2_controlled_training_execution(request)

    assert first.boundary_decision == second.boundary_decision
    assert first.execution_errors == second.execution_errors
    assert first.execution_manifest == second.execution_manifest
    assert first.execution_metadata == second.execution_metadata


def test_controlled_training_execution_source_boundary_scan_has_no_execution_hooks():
    source = Path("src/ppo_v2_controlled_training_execution.py").read_text(
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
