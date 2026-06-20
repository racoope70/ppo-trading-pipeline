"""PPO v2 controlled training execution boundary.

This module defines a non-executing controlled execution scaffold for a future
PPO v2 training checkpoint.

The boundary validates controlled execution preconditions, historical validation
protections, quarantine metadata, and non-authorization flags.

It does not train a model, fetch data, write datasets, create model artifacts,
promote models, or submit orders.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.ppo_v2_controlled_training_execution_dry_run import (
    PPOV2ControlledTrainingExecutionDryRunResult,
)
from src.ppo_v2_training_configuration import (
    PPOV2TrainingConfiguration,
    PPOV2TrainingConfigurationResult,
)


ALLOWED_CONTROLLED_EXECUTION_SCAFFOLD_MODES: tuple[str, ...] = (
    "dry_run",
    "validation_only",
)

REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS: tuple[str, ...] = (
    "Alpaca historical data loader is the controlled historical data source",
    "embargo gap is enforced between train and evaluation periods",
    "embargo compliance is tested or reviewed",
    "VecNormalize / normalization statistics are fit on train data only",
    "train-only VecNormalize / normalization controls are preserved",
    "evaluation uses locked train-only normalization statistics",
    "final holdout remains untouched until final validation",
    "final untouched holdout validation is required before promotion discussion",
    "candidate selection occurs only after holdout validation and audit review",
    "historical validation evidence is reviewed before any promotion discussion",
    "PPO-only baseline performance package is required before hybrid-gate discussion",
    "candidate stability review is required before controlled submit discussion",
    "fresh no-submit paper observation evidence is required before controlled submit discussion",
    "no-submit paper observation review is required before controlled submit discussion",
    "leakage prevention checks are passed before any training output can be reviewed",
)

PASS_DECISION = "PASS"
REJECTED_FAIL_CLOSED_DECISION = "REJECTED_FAIL_CLOSED"


@dataclass(frozen=True)
class PPOV2ControlledTrainingExecutionRequest:
    """Request for the non-executing controlled training execution scaffold."""

    dry_run_result: PPOV2ControlledTrainingExecutionDryRunResult | None
    training_configuration_result: PPOV2TrainingConfigurationResult | None
    run_identifier: str = "ppo_v2_controlled_training_execution"
    execution_mode: str = "validation_only"
    training_input_source_name: str = "validated_in_memory_training_input_handoff"
    training_input_reference: str = "in_memory_validated_training_input_handoff"
    artifact_quarantine_root: str = "artifacts/ppo_v2/quarantine"
    log_quarantine_root: str = "artifacts/ppo_v2/logs"
    configuration_snapshot_name: str = "ppo_v2_training_configuration_snapshot.json"
    data_contract_snapshot_name: str = "ppo_v2_data_contract_snapshot.json"
    model_output_name: str = "ppo_v2_model_quarantined.zip"
    training_log_name: str = "ppo_v2_training_log_quarantined.json"
    metrics_output_name: str = "ppo_v2_training_metrics_quarantined.json"
    seed: int = 42
    timeout_seconds: int = 3_600
    historical_validation_protections: tuple[str, ...] = (
        REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS
    )
    allow_training_execution: bool = False
    allow_artifact_creation: bool = False
    allow_model_promotion: bool = False
    allow_data_fetching: bool = False
    allow_dataset_writes: bool = False
    allow_paper_orders: bool = False
    allow_live_orders: bool = False
    allow_controlled_submit: bool = False
    allow_hybrid_continuation: bool = False


@dataclass(frozen=True)
class PPOV2ControlledTrainingExecutionResult:
    """Result from the non-executing controlled training execution scaffold."""

    execution_manifest: Mapping[str, Any] | None
    execution_errors: tuple[str, ...]
    execution_metadata: Mapping[str, Any]
    boundary_decision: str


def build_ppo_v2_controlled_training_execution(
    request: PPOV2ControlledTrainingExecutionRequest,
) -> PPOV2ControlledTrainingExecutionResult:
    """Build a fail-closed, non-executing controlled execution manifest."""

    if not isinstance(request, PPOV2ControlledTrainingExecutionRequest):
        return PPOV2ControlledTrainingExecutionResult(
            execution_manifest=None,
            execution_errors=("request must be a PPOV2ControlledTrainingExecutionRequest",),
            execution_metadata=_build_metadata(request=None, dry_run_result=None, configuration_result=None),
            boundary_decision=REJECTED_FAIL_CLOSED_DECISION,
        )

    errors: list[str] = []
    dry_run_result = request.dry_run_result
    configuration_result = request.training_configuration_result
    training_configuration: PPOV2TrainingConfiguration | None = None
    dry_run_manifest: Mapping[str, Any] | None = None

    errors.extend(_validate_request_fields(request))
    errors.extend(_validate_disabled_permissions(request))

    if dry_run_result is None:
        errors.append("dry_run_result must be present")
    elif not isinstance(dry_run_result, PPOV2ControlledTrainingExecutionDryRunResult):
        errors.append("dry_run_result must be a PPOV2ControlledTrainingExecutionDryRunResult")
    else:
        if dry_run_result.boundary_decision != PASS_DECISION:
            errors.append("dry_run_result boundary_decision must be PASS")

        if tuple(dry_run_result.dry_run_errors):
            errors.append("dry_run_result must not contain dry_run_errors")

        if not isinstance(dry_run_result.dry_run_manifest, Mapping):
            errors.append("dry_run_manifest must be present")
        else:
            dry_run_manifest = dry_run_result.dry_run_manifest
            errors.extend(_validate_dry_run_manifest(dry_run_manifest, request))

    if configuration_result is None:
        errors.append("training_configuration_result must be present")
    elif not isinstance(configuration_result, PPOV2TrainingConfigurationResult):
        errors.append(
            "training_configuration_result must be a PPOV2TrainingConfigurationResult"
        )
    else:
        if configuration_result.boundary_decision != PASS_DECISION:
            errors.append("training_configuration_result boundary_decision must be PASS")

        if tuple(configuration_result.configuration_errors):
            errors.append(
                "training_configuration_result must not contain configuration_errors"
            )

        if not isinstance(configuration_result.training_configuration, PPOV2TrainingConfiguration):
            errors.append("training_configuration must be present")
        else:
            training_configuration = configuration_result.training_configuration

    historical_protections = _normalize_text_tuple(
        request.historical_validation_protections
    )
    errors.extend(_validate_historical_protections(historical_protections))

    if training_configuration is not None and request.seed != training_configuration.seed:
        errors.append("seed must match training configuration seed")

    metadata = _build_metadata(
        request=request,
        dry_run_result=dry_run_result,
        configuration_result=configuration_result,
    )

    if errors:
        return PPOV2ControlledTrainingExecutionResult(
            execution_manifest=None,
            execution_errors=tuple(errors),
            execution_metadata=metadata,
            boundary_decision=REJECTED_FAIL_CLOSED_DECISION,
        )

    assert dry_run_manifest is not None
    assert training_configuration is not None

    manifest = {
        "run_identifier": request.run_identifier,
        "execution_mode": request.execution_mode,
        "training_input_source_name": request.training_input_source_name,
        "training_input_reference": request.training_input_reference,
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
            "allowed_artifact_policy": training_configuration.allowed_artifact_policy,
            "observation_columns": training_configuration.observation_columns,
        },
        "dry_run_manifest_summary": {
            "run_identifier": dry_run_manifest.get("run_identifier"),
            "execution_mode": dry_run_manifest.get("execution_mode"),
            "training_input_source_name": dry_run_manifest.get("training_input_source_name"),
            "artifact_quarantine_root": dry_run_manifest.get("artifact_quarantine_root"),
            "log_quarantine_root": dry_run_manifest.get("log_quarantine_root"),
        },
        "historical_validation_protections": historical_protections,
        "seed": request.seed,
        "timeout_seconds": request.timeout_seconds,
        "artifact_quarantine_root": request.artifact_quarantine_root,
        "log_quarantine_root": request.log_quarantine_root,
        "configuration_snapshot_name": request.configuration_snapshot_name,
        "data_contract_snapshot_name": request.data_contract_snapshot_name,
        "model_output_name": request.model_output_name,
        "training_log_name": request.training_log_name,
        "metrics_output_name": request.metrics_output_name,
        "training_authorized": False,
        "training_execution_authorized": False,
        "artifact_creation_authorized": False,
        "model_promotion_authorized": False,
        "data_fetching_authorized": False,
        "dataset_write_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "hybrid_continuation_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
    }

    return PPOV2ControlledTrainingExecutionResult(
        execution_manifest=manifest,
        execution_errors=(),
        execution_metadata=metadata,
        boundary_decision=PASS_DECISION,
    )


def _validate_request_fields(
    request: PPOV2ControlledTrainingExecutionRequest,
) -> list[str]:
    errors: list[str] = []

    string_fields = (
        ("run_identifier", request.run_identifier),
        ("training_input_source_name", request.training_input_source_name),
        ("training_input_reference", request.training_input_reference),
        ("artifact_quarantine_root", request.artifact_quarantine_root),
        ("log_quarantine_root", request.log_quarantine_root),
        ("configuration_snapshot_name", request.configuration_snapshot_name),
        ("data_contract_snapshot_name", request.data_contract_snapshot_name),
        ("model_output_name", request.model_output_name),
        ("training_log_name", request.training_log_name),
        ("metrics_output_name", request.metrics_output_name),
    )

    for field_name, field_value in string_fields:
        if _is_blank_string(field_value):
            errors.append(f"{field_name} must be a non-empty string")

    if request.execution_mode not in ALLOWED_CONTROLLED_EXECUTION_SCAFFOLD_MODES:
        errors.append("execution_mode is not allowed for controlled execution scaffold")

    if not isinstance(request.seed, int) or isinstance(request.seed, bool) or request.seed < 0:
        errors.append("seed must be a non-negative integer")

    if _is_not_positive_int(request.timeout_seconds):
        errors.append("timeout_seconds must be a positive integer")

    return errors


def _validate_disabled_permissions(
    request: PPOV2ControlledTrainingExecutionRequest,
) -> list[str]:
    errors: list[str] = []

    permission_checks = (
        (request.allow_training_execution, "training execution request is not authorized"),
        (request.allow_artifact_creation, "artifact creation request is not authorized"),
        (request.allow_model_promotion, "model promotion request is not authorized"),
        (request.allow_data_fetching, "data fetching request is not authorized"),
        (request.allow_dataset_writes, "dataset write request is not authorized"),
        (request.allow_paper_orders, "paper order request is not authorized"),
        (request.allow_live_orders, "live order request is not authorized"),
        (request.allow_controlled_submit, "controlled submit request is not authorized"),
        (request.allow_hybrid_continuation, "hybrid continuation request is not authorized"),
    )

    for permission_value, error_message in permission_checks:
        if permission_value is not False:
            errors.append(error_message)

    return errors


def _validate_dry_run_manifest(
    dry_run_manifest: Mapping[str, Any],
    request: PPOV2ControlledTrainingExecutionRequest,
) -> list[str]:
    errors: list[str] = []

    if dry_run_manifest.get("training_input_source_name") != request.training_input_source_name:
        errors.append("training_input_source_name must match dry_run_manifest")

    forbidden_authorization_fields = (
        "training_authorized",
        "training_execution_authorized",
        "artifact_creation_authorized",
        "data_fetching_authorized",
        "dataset_write_authorized",
        "paper_order_authorized",
        "live_order_authorized",
        "controlled_submit_authorized",
        "ppo_rf_unblocked",
        "ppo_xgboost_unblocked",
    )

    for field_name in forbidden_authorization_fields:
        if dry_run_manifest.get(field_name) is not False:
            errors.append(f"dry_run_manifest {field_name} must be False")

    return errors


def _validate_historical_protections(
    historical_protections: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []

    if not historical_protections:
        errors.append("historical validation protections must be present")
        return errors

    missing = tuple(
        protection
        for protection in REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS
        if protection not in historical_protections
    )
    unsupported = tuple(
        protection
        for protection in historical_protections
        if protection not in REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS
    )

    if missing:
        errors.append("historical validation protections are incomplete")

    if unsupported:
        errors.append("historical validation protections contain unsupported entries")

    if historical_protections != REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS:
        errors.append("historical validation protections must match required controls")

    return errors


def _build_metadata(
    request: PPOV2ControlledTrainingExecutionRequest | None,
    dry_run_result: PPOV2ControlledTrainingExecutionDryRunResult | None,
    configuration_result: PPOV2TrainingConfigurationResult | None,
) -> dict[str, Any]:
    return {
        "run_identifier": getattr(request, "run_identifier", None),
        "execution_mode": getattr(request, "execution_mode", None),
        "allowed_execution_modes": ALLOWED_CONTROLLED_EXECUTION_SCAFFOLD_MODES,
        "dry_run_boundary_decision": getattr(dry_run_result, "boundary_decision", None),
        "training_configuration_boundary_decision": getattr(
            configuration_result,
            "boundary_decision",
            None,
        ),
        "training_authorized": False,
        "training_execution_authorized": False,
        "artifact_creation_authorized": False,
        "model_promotion_authorized": False,
        "data_fetching_authorized": False,
        "dataset_write_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "hybrid_continuation_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
    }


def _normalize_text_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return ()

    try:
        return tuple(str(item) for item in value)
    except TypeError:
        return ()


def _is_blank_string(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def _is_not_positive_int(value: object) -> bool:
    return not isinstance(value, int) or isinstance(value, bool) or value <= 0


__all__ = [
    "ALLOWED_CONTROLLED_EXECUTION_SCAFFOLD_MODES",
    "REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS",
    "PPOV2ControlledTrainingExecutionRequest",
    "PPOV2ControlledTrainingExecutionResult",
    "build_ppo_v2_controlled_training_execution",
]
