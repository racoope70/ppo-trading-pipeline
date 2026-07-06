from pathlib import Path
import re

import pytest

from src.ppo_v2_sealed_preflight_readiness import (
    PASS_DECISION,
    REJECTED_FAIL_CLOSED_DECISION,
    REQUIRED_READINESS_BLOCKERS,
    V3_07_CONFIG_PATH,
    V3_07_RUN_ID,
    V3_07_SEALED_COMMAND_FILE,
    V3_07_SEALED_DATASET_PATH,
    V307SealedPreflightReadinessRequest,
    build_v3_07_sealed_preflight_readiness_scaffold,
)


def test_default_scaffold_is_defined_without_executing_preflight():
    result = build_v3_07_sealed_preflight_readiness_scaffold()

    assert result.boundary_decision == PASS_DECISION
    assert result.readiness_errors == ()
    assert result.readiness_manifest is not None
    assert result.readiness_manifest["scope"] == (
        "validation_scaffold_only_not_preflight_execution"
    )
    assert result.readiness_manifest["run_id"] == V3_07_RUN_ID
    assert result.readiness_manifest["config_path"] == V3_07_CONFIG_PATH
    assert result.readiness_manifest["sealed_dataset_path"] == V3_07_SEALED_DATASET_PATH
    assert result.readiness_manifest["sealed_command_file"] == V3_07_SEALED_COMMAND_FILE


def test_scaffold_preserves_current_hard_blocks():
    result = build_v3_07_sealed_preflight_readiness_scaffold()
    manifest = result.readiness_manifest

    assert manifest["v3_07_status"] == "BLOCKED"
    assert manifest["no_submit_default"] is True
    assert manifest["preflight_readiness"] == "NOT_PASSED"
    assert manifest["sealed_dataset_validation"] == "NOT_PROVEN"
    assert manifest["training_command_execution_authorized"] is False
    assert manifest["ppo_v2_training_execution_authorized"] is False
    assert manifest["v3_07_execution_authorized"] is False
    assert manifest["data_fetching_authorized"] is False
    assert manifest["dataset_generation_authorized"] is False
    assert manifest["model_artifact_creation_authorized"] is False
    assert manifest["quarantine_output_creation_authorized"] is False
    assert manifest["paper_order_authorized"] is False
    assert manifest["live_order_authorized"] is False
    assert manifest["controlled_submit_authorized"] is False
    assert manifest["ppo_rf_authorized"] is False
    assert manifest["ppo_xgboost_authorized"] is False


def test_scaffold_marks_r1_to_r6_evidence_absent_not_passed():
    result = build_v3_07_sealed_preflight_readiness_scaffold()
    manifest = result.readiness_manifest

    assert manifest["r1_preflight_pass_evidence"] == "ABSENT"
    assert manifest["r2_sealed_dataset_evidence"] == "ABSENT"
    assert manifest["r3_data_contract_missing_bar_coverage_evidence"] == "ABSENT"
    assert manifest["r4_temporal_split_embargo_holdout_evidence"] == "ABSENT"
    assert manifest["r5_training_input_handoff_evidence"] == "ABSENT"
    assert manifest["r6_runtime_dependency_git_state_evidence"] == "ABSENT"
    assert manifest["future_validation_only_preflight_required"] is True
    assert manifest["future_explicit_authorization_required_before_dataset_read"] is True
    assert manifest["future_independent_evidence_review_required"] is True


@pytest.mark.parametrize(
    "field_name",
    [
        "allow_preflight_execution",
        "allow_sealed_dataset_read",
        "allow_training_command_execution",
        "allow_training_execution",
        "allow_data_fetching",
        "allow_dataset_generation",
        "allow_model_artifact_creation",
        "allow_quarantine_output_creation",
        "allow_stdout_stderr_log_checksum_inventory_writes",
        "allow_paper_orders",
        "allow_live_orders",
        "allow_controlled_submit",
        "allow_ppo_rf",
        "allow_ppo_xgboost",
        "allow_model_promotion",
    ],
)
def test_scaffold_rejects_any_authorization_flag_fail_closed(field_name):
    request = V307SealedPreflightReadinessRequest(**{field_name: True})

    result = build_v3_07_sealed_preflight_readiness_scaffold(request)

    assert result.boundary_decision == REJECTED_FAIL_CLOSED_DECISION
    assert result.readiness_manifest is None
    assert f"{field_name} must remain false" in result.readiness_errors


@pytest.mark.parametrize(
    ("field_name", "bad_value", "expected_error"),
    [
        ("run_id", "wrong_run", "run_id must match sealed v3.07 run id"),
        (
            "config_path",
            "wrong/config.yaml",
            "config_path must match sealed v3.07 config path",
        ),
        (
            "sealed_dataset_path",
            "wrong/input.parquet",
            "sealed_dataset_path must match sealed v3.07 dataset path",
        ),
        (
            "sealed_command_file",
            "wrong/command.txt",
            "sealed_command_file must match sealed v3.07 command file",
        ),
    ],
)
def test_scaffold_rejects_wrong_sealed_identity_values(
    field_name,
    bad_value,
    expected_error,
):
    request = V307SealedPreflightReadinessRequest(**{field_name: bad_value})

    result = build_v3_07_sealed_preflight_readiness_scaffold(request)

    assert result.boundary_decision == REJECTED_FAIL_CLOSED_DECISION
    assert result.readiness_manifest is None
    assert expected_error in result.readiness_errors


def test_scaffold_rejects_modified_r1_to_r6_blocker_set():
    request = V307SealedPreflightReadinessRequest(
        required_readiness_blockers=REQUIRED_READINESS_BLOCKERS[:-1],
    )

    result = build_v3_07_sealed_preflight_readiness_scaffold(request)

    assert result.boundary_decision == REJECTED_FAIL_CLOSED_DECISION
    assert result.readiness_manifest is None
    assert (
        "required readiness blockers must match sealed R1-R6 blockers"
        in result.readiness_errors
    )


def test_scaffold_rejects_no_submit_default_false():
    request = V307SealedPreflightReadinessRequest(no_submit_default=False)

    result = build_v3_07_sealed_preflight_readiness_scaffold(request)

    assert result.boundary_decision == REJECTED_FAIL_CLOSED_DECISION
    assert result.readiness_manifest is None
    assert "no_submit_default must remain true" in result.readiness_errors


def test_scaffold_metadata_confirms_no_execution_or_side_effects():
    result = build_v3_07_sealed_preflight_readiness_scaffold()

    assert result.readiness_metadata["execution_performed"] is False
    assert result.readiness_metadata["preflight_executed"] is False
    assert result.readiness_metadata["sealed_dataset_read"] is False
    assert result.readiness_metadata["training_performed"] is False
    assert result.readiness_metadata["model_artifact_creation_performed"] is False
    assert result.readiness_metadata["quarantine_output_creation_performed"] is False


def test_scaffold_source_has_no_training_dataset_or_file_output_hooks():
    source = Path("src/ppo_v2_sealed_preflight_readiness.py").read_text(
        encoding="utf-8"
    )

    forbidden_patterns = [
        r"\.learn\(",
        r"\.fit\(",
        r"read_parquet",
        r"read_csv",
        r"open\(",
        r"\.write\(",
        r"write_text",
        r"mkdir",
        r"joblib\.dump",
        r"torch\.save",
        r"pickle\.dump",
        r"\.to_csv",
        r"\.to_parquet",
        r"requests\.",
    ]

    matches = [
        pattern
        for pattern in forbidden_patterns
        if re.search(pattern, source)
    ]

    assert matches == []
