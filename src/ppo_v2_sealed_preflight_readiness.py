"""v3.07 sealed preflight readiness scaffold.

This module defines a validation-only scaffold for a future v3.07 sealed
preflight evidence remediation checkpoint.

It does not run preflight, read the sealed dataset, execute the sealed training
command, train a model, fetch data, generate datasets, create model artifacts,
create quarantine outputs, write stdout/stderr/log/checksum/inventory files,
promote models, or submit orders.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


PASS_DECISION = "SCAFFOLD_DEFINED_NOT_EXECUTED"
REJECTED_FAIL_CLOSED_DECISION = "REJECTED_FAIL_CLOSED"

V3_07_RUN_ID = "v3_07_no_submit_ppo_v2_training_execution_001"
V3_07_CONFIG_PATH = (
    "artifacts/ppo_v2/package_preparation/"
    "v3_07_no_submit_training_execution_package/config/"
    "v3_07_no_submit_training_config.yaml"
)
V3_07_SEALED_DATASET_PATH = (
    "data/processed/ppo_v2/v3_07_no_submit_training_input.parquet"
)
V3_07_SEALED_COMMAND_FILE = (
    "artifacts/ppo_v2/package_preparation/"
    "v3_07_no_submit_training_execution_package/commands/"
    "one_time_no_submit_training_command.txt"
)

REQUIRED_READINESS_BLOCKERS: tuple[str, ...] = (
    "R1_PRELIGHT_PASS_EVIDENCE",
    "R2_SEALED_DATASET_EXISTENCE_AND_VALIDATION",
    "R3_DATA_CONTRACT_MISSING_BAR_COVERAGE_VALIDATION",
    "R4_TEMPORAL_SPLIT_EMBARGO_HOLDOUT_VALIDATION",
    "R5_TRAINING_INPUT_HANDOFF_VALIDATION",
    "R6_RUNTIME_DEPENDENCY_AND_GIT_STATE_EVIDENCE",
)


@dataclass(frozen=True)
class V307SealedPreflightReadinessRequest:
    """Request for a non-executing v3.07 preflight readiness scaffold."""

    run_id: str = V3_07_RUN_ID
    config_path: str = V3_07_CONFIG_PATH
    sealed_dataset_path: str = V3_07_SEALED_DATASET_PATH
    sealed_command_file: str = V3_07_SEALED_COMMAND_FILE
    required_readiness_blockers: tuple[str, ...] = REQUIRED_READINESS_BLOCKERS
    no_submit_default: bool = True
    allow_preflight_execution: bool = False
    allow_sealed_dataset_read: bool = False
    allow_training_command_execution: bool = False
    allow_training_execution: bool = False
    allow_data_fetching: bool = False
    allow_dataset_generation: bool = False
    allow_model_artifact_creation: bool = False
    allow_quarantine_output_creation: bool = False
    allow_stdout_stderr_log_checksum_inventory_writes: bool = False
    allow_paper_orders: bool = False
    allow_live_orders: bool = False
    allow_controlled_submit: bool = False
    allow_ppo_rf: bool = False
    allow_ppo_xgboost: bool = False
    allow_model_promotion: bool = False


@dataclass(frozen=True)
class V307SealedPreflightReadinessResult:
    """Result from the non-executing v3.07 readiness scaffold."""

    readiness_manifest: Mapping[str, Any] | None
    readiness_errors: tuple[str, ...]
    readiness_metadata: Mapping[str, Any]
    boundary_decision: str


def build_v3_07_sealed_preflight_readiness_scaffold(
    request: V307SealedPreflightReadinessRequest | None = None,
) -> V307SealedPreflightReadinessResult:
    """Build a fail-closed, non-executing readiness scaffold manifest."""

    if request is None:
        request = V307SealedPreflightReadinessRequest()

    if not isinstance(request, V307SealedPreflightReadinessRequest):
        return _reject(
            request=None,
            errors=("request must be a V307SealedPreflightReadinessRequest",),
        )

    errors: list[str] = []
    errors.extend(_validate_identity_fields(request))
    errors.extend(_validate_required_blockers(request))
    errors.extend(_validate_no_authorization_flags(request))

    if errors:
        return _reject(request=request, errors=tuple(errors))

    manifest = {
        "schema_version": "v3.07-sealed-preflight-readiness-scaffold",
        "scope": "validation_scaffold_only_not_preflight_execution",
        "run_id": request.run_id,
        "config_path": request.config_path,
        "sealed_dataset_path": request.sealed_dataset_path,
        "sealed_command_file": request.sealed_command_file,
        "v3_07_status": "BLOCKED",
        "no_submit_default": True,
        "preflight_readiness": "NOT_PASSED",
        "sealed_dataset_validation": "NOT_PROVEN",
        "preflight_executed": False,
        "preflight_passed": False,
        "sealed_dataset_read": False,
        "sealed_training_command_executed": False,
        "training_performed": False,
        "training_command_execution_authorized": False,
        "ppo_v2_training_execution_authorized": False,
        "v3_07_execution_authorized": False,
        "data_fetching_authorized": False,
        "dataset_generation_authorized": False,
        "model_artifact_creation_authorized": False,
        "quarantine_output_creation_authorized": False,
        "stdout_stderr_log_checksum_inventory_writes_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "ppo_rf_authorized": False,
        "ppo_xgboost_authorized": False,
        "model_promotion_authorized": False,
        "r1_preflight_pass_evidence": "ABSENT",
        "r2_sealed_dataset_evidence": "ABSENT",
        "r3_data_contract_missing_bar_coverage_evidence": "ABSENT",
        "r4_temporal_split_embargo_holdout_evidence": "ABSENT",
        "r5_training_input_handoff_evidence": "ABSENT",
        "r6_runtime_dependency_git_state_evidence": "ABSENT",
        "future_validation_only_preflight_required": True,
        "future_explicit_authorization_required_before_dataset_read": True,
        "future_independent_evidence_review_required": True,
        "required_next_checkpoint": (
            "v3.07 Sealed Preflight Evidence Remediation Review"
        ),
    }

    return V307SealedPreflightReadinessResult(
        readiness_manifest=manifest,
        readiness_errors=(),
        readiness_metadata=_build_metadata(request),
        boundary_decision=PASS_DECISION,
    )


def _validate_identity_fields(
    request: V307SealedPreflightReadinessRequest,
) -> tuple[str, ...]:
    errors: list[str] = []

    if request.run_id != V3_07_RUN_ID:
        errors.append("run_id must match sealed v3.07 run id")

    if request.config_path != V3_07_CONFIG_PATH:
        errors.append("config_path must match sealed v3.07 config path")

    if request.sealed_dataset_path != V3_07_SEALED_DATASET_PATH:
        errors.append("sealed_dataset_path must match sealed v3.07 dataset path")

    if request.sealed_command_file != V3_07_SEALED_COMMAND_FILE:
        errors.append("sealed_command_file must match sealed v3.07 command file")

    if request.no_submit_default is not True:
        errors.append("no_submit_default must remain true")

    return tuple(errors)


def _validate_required_blockers(
    request: V307SealedPreflightReadinessRequest,
) -> tuple[str, ...]:
    if tuple(request.required_readiness_blockers) != REQUIRED_READINESS_BLOCKERS:
        return ("required readiness blockers must match sealed R1-R6 blockers",)

    return ()


def _validate_no_authorization_flags(
    request: V307SealedPreflightReadinessRequest,
) -> tuple[str, ...]:
    blocked_flags = {
        "allow_preflight_execution": request.allow_preflight_execution,
        "allow_sealed_dataset_read": request.allow_sealed_dataset_read,
        "allow_training_command_execution": request.allow_training_command_execution,
        "allow_training_execution": request.allow_training_execution,
        "allow_data_fetching": request.allow_data_fetching,
        "allow_dataset_generation": request.allow_dataset_generation,
        "allow_model_artifact_creation": request.allow_model_artifact_creation,
        "allow_quarantine_output_creation": request.allow_quarantine_output_creation,
        "allow_stdout_stderr_log_checksum_inventory_writes": (
            request.allow_stdout_stderr_log_checksum_inventory_writes
        ),
        "allow_paper_orders": request.allow_paper_orders,
        "allow_live_orders": request.allow_live_orders,
        "allow_controlled_submit": request.allow_controlled_submit,
        "allow_ppo_rf": request.allow_ppo_rf,
        "allow_ppo_xgboost": request.allow_ppo_xgboost,
        "allow_model_promotion": request.allow_model_promotion,
    }

    errors = [
        f"{name} must remain false"
        for name, value in blocked_flags.items()
        if value is not False
    ]

    return tuple(errors)


def _build_metadata(
    request: V307SealedPreflightReadinessRequest | None,
) -> Mapping[str, Any]:
    return {
        "checkpoint": "v3.07_sealed_preflight_readiness_scaffold",
        "scope": "validation_scaffold_only",
        "request_present": request is not None,
        "execution_performed": False,
        "preflight_executed": False,
        "sealed_dataset_read": False,
        "training_performed": False,
        "model_artifact_creation_performed": False,
        "quarantine_output_creation_performed": False,
    }


def _reject(
    request: V307SealedPreflightReadinessRequest | None,
    errors: tuple[str, ...],
) -> V307SealedPreflightReadinessResult:
    return V307SealedPreflightReadinessResult(
        readiness_manifest=None,
        readiness_errors=errors,
        readiness_metadata=_build_metadata(request),
        boundary_decision=REJECTED_FAIL_CLOSED_DECISION,
    )


__all__ = [
    "PASS_DECISION",
    "REJECTED_FAIL_CLOSED_DECISION",
    "REQUIRED_READINESS_BLOCKERS",
    "V3_07_CONFIG_PATH",
    "V3_07_RUN_ID",
    "V3_07_SEALED_COMMAND_FILE",
    "V3_07_SEALED_DATASET_PATH",
    "V307SealedPreflightReadinessRequest",
    "V307SealedPreflightReadinessResult",
    "build_v3_07_sealed_preflight_readiness_scaffold",
]
