"""PPO v2 controlled training execution dry-run boundary.

This module defines a non-executing dry-run scaffold for a future controlled
PPO v2 training execution checkpoint.

The boundary validates that training execution inputs are structurally present
and that all execution, artifact, data, broker, order, deployment, and hybrid
permissions remain disabled.

It does not train a model, fetch data, write datasets, create model artifacts,
or submit orders.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.ppo_v2_training_configuration import (
    PPOV2TrainingConfiguration,
    PPOV2TrainingConfigurationResult,
)


ALLOWED_DRY_RUN_EXECUTION_MODES: tuple[str, ...] = (
    "dry_run",
    "validation_only",
)

PASS_DECISION = "PASS"
REJECTED_FAIL_CLOSED_DECISION = "REJECTED_FAIL_CLOSED"


@dataclass(frozen=True)
class PPOV2ControlledTrainingExecutionDryRunRequest:
    """Request for the non-executing controlled training dry-run boundary."""

    training_configuration_result: PPOV2TrainingConfigurationResult | None
    run_identifier: str = "ppo_v2_controlled_training_execution_dry_run"
    execution_mode: str = "validation_only"
    training_input_source_name: str = "validated_in_memory_training_input_handoff"
    artifact_quarantine_root: str = "artifacts/ppo_v2/quarantine"
    log_quarantine_root: str = "artifacts/ppo_v2/logs"
    configuration_snapshot_name: str = "ppo_v2_training_configuration_snapshot.json"
    data_contract_snapshot_name: str = "ppo_v2_data_contract_snapshot.json"
    expected_train_rows: int = 1
    expected_eval_rows: int = 1
    expected_holdout_rows: int = 1
    expected_observation_columns: tuple[str, ...] = ()
    allow_training_execution: bool = False
    allow_artifact_creation: bool = False
    allow_data_fetching: bool = False
    allow_dataset_writes: bool = False
    allow_paper_orders: bool = False
    allow_live_orders: bool = False
    allow_controlled_submit: bool = False
    allow_deployment_update: bool = False


@dataclass(frozen=True)
class PPOV2ControlledTrainingExecutionDryRunResult:
    """Result from the non-executing controlled training dry-run boundary."""

    dry_run_manifest: Mapping[str, Any] | None
    dry_run_errors: tuple[str, ...]
    dry_run_metadata: Mapping[str, Any]
    boundary_decision: str


def build_ppo_v2_controlled_training_execution_dry_run(
    request: PPOV2ControlledTrainingExecutionDryRunRequest,
) -> PPOV2ControlledTrainingExecutionDryRunResult:
    """Build a fail-closed, non-executing dry-run manifest."""

    if not isinstance(request, PPOV2ControlledTrainingExecutionDryRunRequest):
        return PPOV2ControlledTrainingExecutionDryRunResult(
            dry_run_manifest=None,
            dry_run_errors=("request must be a PPOV2ControlledTrainingExecutionDryRunRequest",),
            dry_run_metadata=_build_metadata(request=None, configuration_result=None),
            boundary_decision=REJECTED_FAIL_CLOSED_DECISION,
        )

    errors: list[str] = []
    configuration_result = request.training_configuration_result
    training_configuration: PPOV2TrainingConfiguration | None = None

    if _is_blank_string(request.run_identifier):
        errors.append("run_identifier must be a non-empty string")

    if request.execution_mode not in ALLOWED_DRY_RUN_EXECUTION_MODES:
        errors.append("execution_mode is not allowed for dry-run boundary")

    if _is_blank_string(request.training_input_source_name):
        errors.append("training_input_source_name must be a non-empty string")

    if _is_blank_string(request.artifact_quarantine_root):
        errors.append("artifact_quarantine_root must be a non-empty string")

    if _is_blank_string(request.log_quarantine_root):
        errors.append("log_quarantine_root must be a non-empty string")

    if _is_blank_string(request.configuration_snapshot_name):
        errors.append("configuration_snapshot_name must be a non-empty string")

    if _is_blank_string(request.data_contract_snapshot_name):
        errors.append("data_contract_snapshot_name must be a non-empty string")

    if _is_not_positive_int(request.expected_train_rows):
        errors.append("expected_train_rows must be a positive integer")

    if _is_not_positive_int(request.expected_eval_rows):
        errors.append("expected_eval_rows must be a positive integer")

    if _is_not_positive_int(request.expected_holdout_rows):
        errors.append("expected_holdout_rows must be a positive integer")

    errors.extend(_validate_disabled_permissions(request))

    if configuration_result is None:
        errors.append("training_configuration_result must be present")
    elif not isinstance(configuration_result, PPOV2TrainingConfigurationResult):
        errors.append("training_configuration_result must be a PPOV2TrainingConfigurationResult")
    else:
        if configuration_result.boundary_decision != PASS_DECISION:
            errors.append("training_configuration_result boundary_decision must be PASS")

        if tuple(configuration_result.configuration_errors):
            errors.append("training_configuration_result must not contain configuration_errors")

        if not isinstance(configuration_result.training_configuration, PPOV2TrainingConfiguration):
            errors.append("training_configuration must be present")
        else:
            training_configuration = configuration_result.training_configuration

    expected_observation_columns = _normalize_observation_columns(
        request.expected_observation_columns
    )

    if not expected_observation_columns:
        errors.append("expected_observation_columns must be non-empty")

    if (
        training_configuration is not None
        and expected_observation_columns
        and expected_observation_columns != tuple(training_configuration.observation_columns)
    ):
        errors.append(
            "expected_observation_columns must match training configuration observation columns"
        )

    metadata = _build_metadata(
        request=request,
        configuration_result=configuration_result,
    )

    if errors:
        return PPOV2ControlledTrainingExecutionDryRunResult(
            dry_run_manifest=None,
            dry_run_errors=tuple(errors),
            dry_run_metadata=metadata,
            boundary_decision=REJECTED_FAIL_CLOSED_DECISION,
        )

    assert training_configuration is not None

    manifest = {
        "run_identifier": request.run_identifier,
        "execution_mode": request.execution_mode,
        "training_input_source_name": request.training_input_source_name,
        "training_configuration_summary": {
            "ppo_algorithm_family": training_configuration.ppo_algorithm_family,
            "policy_type": training_configuration.policy_type,
            "total_timesteps": training_configuration.total_timesteps,
            "learning_rate": training_configuration.learning_rate,
            "seed": training_configuration.seed,
            "device_preference": training_configuration.device_preference,
            "environment_id": training_configuration.environment_id,
            "reward_contract_name": training_configuration.reward_contract_name,
            "risk_contract_name": training_configuration.risk_contract_name,
        },
        "training_input_summary": {
            "expected_train_rows": request.expected_train_rows,
            "expected_eval_rows": request.expected_eval_rows,
            "expected_holdout_rows": request.expected_holdout_rows,
            "observation_column_count": len(expected_observation_columns),
            "observation_columns": expected_observation_columns,
        },
        "artifact_quarantine_root": request.artifact_quarantine_root,
        "log_quarantine_root": request.log_quarantine_root,
        "configuration_snapshot_name": request.configuration_snapshot_name,
        "data_contract_snapshot_name": request.data_contract_snapshot_name,
        "training_authorized": False,
        "training_execution_authorized": False,
        "artifact_creation_authorized": False,
        "data_fetching_authorized": False,
        "dataset_write_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "deployment_update_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
    }

    return PPOV2ControlledTrainingExecutionDryRunResult(
        dry_run_manifest=manifest,
        dry_run_errors=(),
        dry_run_metadata=metadata,
        boundary_decision=PASS_DECISION,
    )


def _validate_disabled_permissions(
    request: PPOV2ControlledTrainingExecutionDryRunRequest,
) -> list[str]:
    errors: list[str] = []

    permission_checks = (
        (request.allow_training_execution, "training execution request is not authorized"),
        (request.allow_artifact_creation, "artifact creation request is not authorized"),
        (request.allow_data_fetching, "data fetching request is not authorized"),
        (request.allow_dataset_writes, "dataset write request is not authorized"),
        (request.allow_paper_orders, "paper order request is not authorized"),
        (request.allow_live_orders, "live order request is not authorized"),
        (request.allow_controlled_submit, "controlled submit request is not authorized"),
        (request.allow_deployment_update, "deployment update request is not authorized"),
    )

    for permission_value, error_message in permission_checks:
        if permission_value is not False:
            errors.append(error_message)

    return errors


def _build_metadata(
    request: PPOV2ControlledTrainingExecutionDryRunRequest | None,
    configuration_result: PPOV2TrainingConfigurationResult | None,
) -> dict[str, Any]:
    return {
        "run_identifier": getattr(request, "run_identifier", None),
        "execution_mode": getattr(request, "execution_mode", None),
        "allowed_execution_modes": ALLOWED_DRY_RUN_EXECUTION_MODES,
        "training_configuration_boundary_decision": getattr(
            configuration_result,
            "boundary_decision",
            None,
        ),
        "training_authorized": False,
        "training_execution_authorized": False,
        "artifact_creation_authorized": False,
        "data_fetching_authorized": False,
        "dataset_write_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "deployment_update_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
    }


def _normalize_observation_columns(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return ()

    try:
        return tuple(str(column) for column in value)
    except TypeError:
        return ()


def _is_blank_string(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def _is_not_positive_int(value: object) -> bool:
    return not isinstance(value, int) or isinstance(value, bool) or value <= 0


__all__ = [
    "ALLOWED_DRY_RUN_EXECUTION_MODES",
    "PPOV2ControlledTrainingExecutionDryRunRequest",
    "PPOV2ControlledTrainingExecutionDryRunResult",
    "build_ppo_v2_controlled_training_execution_dry_run",
]
