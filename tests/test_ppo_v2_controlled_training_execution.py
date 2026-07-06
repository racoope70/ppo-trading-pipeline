from dataclasses import replace
from pathlib import Path
import re

import pandas as pd
import pytest

from src.ppo_v2_controlled_training_execution import (
    V3_07_SEALED_CLI_ARGUMENTS,
    V3_07_SEALED_CONFIG_PATH,
    V3_07_SEALED_QUARANTINE_ROOT,
    V3_07_SEALED_LOG_ROOT,
    V3_07_SEALED_STDOUT_PATH,
    V3_07_SEALED_STDERR_PATH,
    V3_07_SEALED_ARTIFACT_INVENTORY_PATH,
    V3_07_SEALED_CHECKSUM_MANIFEST_PATH,
    REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS,
    PPOV2ControlledTrainingExecutionRequest,
    build_ppo_v2_controlled_training_execution,
    build_v3_07_no_submit_cli_compatibility,
    main as ppo_v2_execution_main,
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


def _sealed_cli_args():
    return list(V3_07_SEALED_CLI_ARGUMENTS)


def _replace_cli_value(args, flag, value):
    updated = list(args)
    index = updated.index(flag)
    updated[index + 1] = value
    return updated


def test_v3_07_sealed_cli_arguments_are_accepted_without_execution():
    result = build_v3_07_no_submit_cli_compatibility(_sealed_cli_args())

    assert result.boundary_decision == "PASS"
    assert result.compatibility_errors == ()
    assert result.compatibility_manifest is not None
    assert result.compatibility_manifest["sealed_command_arguments_accepted"] is True
    assert result.compatibility_manifest["source_code_execution_compatibility_check_passed"] is True
    assert result.compatibility_manifest["execution_performed"] is False
    assert result.compatibility_manifest["training_performed"] is False
    assert result.compatibility_manifest["training_authorized"] is False
    assert result.compatibility_manifest["training_command_execution_authorized"] is False
    assert result.compatibility_manifest["ppo_v2_training_execution_authorized"] is False
    assert result.compatibility_manifest["v3_07_execution_authorized"] is False
    assert result.compatibility_manifest["preflight_executed"] is False
    assert result.compatibility_manifest["preflight_passed"] is False
    assert result.compatibility_manifest["execution_ready_proven"] is False
    assert result.compatibility_manifest["data_fetching_authorized"] is False
    assert result.compatibility_manifest["dataset_generation_authorized"] is False
    assert result.compatibility_manifest["model_artifact_creation_authorized"] is False
    assert result.compatibility_manifest["quarantine_output_creation_authorized"] is False
    assert result.compatibility_manifest["paper_order_authorized"] is False
    assert result.compatibility_manifest["live_order_authorized"] is False
    assert result.compatibility_manifest["controlled_submit_authorized"] is False
    assert result.compatibility_manifest["ppo_rf_unblocked"] is False
    assert result.compatibility_manifest["ppo_xgboost_unblocked"] is False


def test_v3_07_cli_entrypoint_accepts_sealed_arguments_without_running_training():
    assert ppo_v2_execution_main(_sealed_cli_args()) == 0


def test_v3_07_cli_missing_no_submit_fails_closed():
    args = [arg for arg in _sealed_cli_args() if arg != "--no-submit"]

    result = build_v3_07_no_submit_cli_compatibility(args)

    _assert_failed_with_cli(result, "--no-submit is required")


def test_v3_07_cli_wrong_run_id_fails_closed():
    args = _replace_cli_value(_sealed_cli_args(), "--run-id", "wrong_run_id")

    result = build_v3_07_no_submit_cli_compatibility(args)

    _assert_failed_with_cli(result, "run id must match sealed v3.07 run id")


def test_v3_07_cli_wrong_config_path_fails_closed():
    args = _replace_cli_value(_sealed_cli_args(), "--config", "config/wrong.yaml")

    result = build_v3_07_no_submit_cli_compatibility(args)

    _assert_failed_with_cli(result, "config path must match sealed v3.07 config path")


@pytest.mark.parametrize(
    ("flag", "unsafe_value", "expected_error"),
    [
        (
            "--quarantine-root",
            "/tmp/ppo_v2/quarantine/run",
            "quarantine root must remain relative",
        ),
        (
            "--quarantine-root",
            "../artifacts/ppo_v2/quarantine/run",
            "quarantine root must not contain path traversal",
        ),
        (
            "--log-root",
            "/tmp/ppo_v2/logs/run",
            "log root must remain relative",
        ),
        (
            "--log-root",
            "../artifacts/ppo_v2/logs/run",
            "log root must not contain path traversal",
        ),
    ],
)
def test_v3_07_cli_unsafe_quarantine_or_log_paths_fail_closed(
    flag,
    unsafe_value,
    expected_error,
):
    args = _replace_cli_value(_sealed_cli_args(), flag, unsafe_value)

    result = build_v3_07_no_submit_cli_compatibility(args)

    _assert_failed_with_cli(result, expected_error)


@pytest.mark.parametrize(
    "flag",
    [
        "--paper-orders",
        "--live-orders",
        "--controlled-submit",
        "--model-promotion",
        "--ppo-rf",
        "--ppo-xgboost",
    ],
)
def test_v3_07_cli_blocked_order_hybrid_promotion_flags_fail_closed(flag):
    result = build_v3_07_no_submit_cli_compatibility([*_sealed_cli_args(), flag])

    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.compatibility_manifest is None
    assert any(flag in error and "not authorized" in error for error in result.compatibility_errors)


def test_v3_07_cli_compatibility_mode_does_not_train():
    result = build_v3_07_no_submit_cli_compatibility(_sealed_cli_args())

    assert result.boundary_decision == "PASS"
    assert result.compatibility_manifest["execution_performed"] is False
    assert result.compatibility_manifest["training_performed"] is False
    assert result.compatibility_manifest["training_authorized"] is False
    assert result.compatibility_manifest["training_command_execution_authorized"] is False


def test_v3_07_cli_compatibility_mode_does_not_create_artifacts_or_quarantine_outputs():
    result = build_v3_07_no_submit_cli_compatibility(_sealed_cli_args())

    assert result.boundary_decision == "PASS"
    assert result.compatibility_manifest["model_artifact_creation_authorized"] is False
    assert result.compatibility_manifest["quarantine_output_creation_authorized"] is False
    assert result.compatibility_manifest["creates_model_artifacts"] is False
    assert result.compatibility_manifest["creates_quarantine_outputs"] is False
    assert result.compatibility_manifest["writes_stdout_path"] is False
    assert result.compatibility_manifest["writes_stderr_path"] is False
    assert result.compatibility_manifest["writes_artifact_inventory_path"] is False
    assert result.compatibility_manifest["writes_checksum_manifest_path"] is False
    assert result.compatibility_manifest["stdout_path"] == V3_07_SEALED_STDOUT_PATH
    assert result.compatibility_manifest["stderr_path"] == V3_07_SEALED_STDERR_PATH
    assert (
        result.compatibility_manifest["artifact_inventory_path"]
        == V3_07_SEALED_ARTIFACT_INVENTORY_PATH
    )
    assert (
        result.compatibility_manifest["checksum_manifest_path"]
        == V3_07_SEALED_CHECKSUM_MANIFEST_PATH
    )


def test_v3_07_cli_compatibility_manifest_preserves_sealed_paths():
    result = build_v3_07_no_submit_cli_compatibility(_sealed_cli_args())

    assert result.boundary_decision == "PASS"
    assert result.compatibility_manifest["config_path"] == V3_07_SEALED_CONFIG_PATH
    assert result.compatibility_manifest["quarantine_root"] == V3_07_SEALED_QUARANTINE_ROOT
    assert result.compatibility_manifest["log_root"] == V3_07_SEALED_LOG_ROOT


def test_v3_07_cli_compatibility_source_has_no_training_or_file_output_hooks():
    source = Path("src/ppo_v2_controlled_training_execution.py").read_text(
        encoding="utf-8"
    )
    forbidden_patterns = [
        r"\.learn\(",
        r"\.fit\(",
        r"\.save\(",
        r"open\(",
        r"\.write\(",
        r"write_text",
        r"mkdir",
        r"joblib\.dump",
        r"torch\.save",
        r"pickle\.dump",
        r"\.to_csv",
        r"\.to_parquet",
    ]

    matches = [
        pattern
        for pattern in forbidden_patterns
        if re.search(pattern, source)
    ]

    assert matches == []


def _assert_failed_with_cli(result, expected_error):
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.compatibility_manifest is None
    assert expected_error in result.compatibility_errors
