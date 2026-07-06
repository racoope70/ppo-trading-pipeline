"""PPO v2 controlled training execution boundary.

This module defines a non-executing controlled execution scaffold for a future
PPO v2 training checkpoint.

The boundary validates controlled execution preconditions, historical validation
protections, quarantine metadata, and non-authorization flags.

It does not train a model, fetch data, write datasets, create model artifacts,
promote models, or submit orders.
"""

from __future__ import annotations

import argparse
import sys

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
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


V3_07_SEALED_RUN_ID = "v3_07_no_submit_ppo_v2_training_execution_001"
V3_07_SEALED_MODE = "controlled-training"
V3_07_SEALED_CONFIG_PATH = (
    "artifacts/ppo_v2/package_preparation/"
    "v3_07_no_submit_training_execution_package/config/"
    "v3_07_no_submit_training_config.yaml"
)
V3_07_SEALED_QUARANTINE_ROOT = (
    "artifacts/ppo_v2/quarantine/"
    "v3_07_no_submit_ppo_v2_training_execution_001"
)
V3_07_SEALED_LOG_ROOT = (
    "artifacts/ppo_v2/logs/"
    "v3_07_no_submit_ppo_v2_training_execution_001"
)
V3_07_SEALED_STDOUT_PATH = (
    "artifacts/ppo_v2/logs/"
    "v3_07_no_submit_ppo_v2_training_execution_001/stdout.txt"
)
V3_07_SEALED_STDERR_PATH = (
    "artifacts/ppo_v2/logs/"
    "v3_07_no_submit_ppo_v2_training_execution_001/stderr.txt"
)
V3_07_SEALED_ARTIFACT_INVENTORY_PATH = (
    "artifacts/ppo_v2/quarantine/"
    "v3_07_no_submit_ppo_v2_training_execution_001/"
    "manifests/artifact_inventory.json"
)
V3_07_SEALED_CHECKSUM_MANIFEST_PATH = (
    "artifacts/ppo_v2/quarantine/"
    "v3_07_no_submit_ppo_v2_training_execution_001/"
    "manifests/checksums.sha256"
)
V3_07_APPROVED_QUARANTINE_ROOT = "artifacts/ppo_v2/quarantine"
V3_07_APPROVED_LOG_ROOT = "artifacts/ppo_v2/logs"

V3_07_SEALED_CLI_ARGUMENTS: tuple[str, ...] = (
    "--mode",
    V3_07_SEALED_MODE,
    "--run-id",
    V3_07_SEALED_RUN_ID,
    "--config",
    V3_07_SEALED_CONFIG_PATH,
    "--quarantine-root",
    V3_07_SEALED_QUARANTINE_ROOT,
    "--log-root",
    V3_07_SEALED_LOG_ROOT,
    "--stdout-path",
    V3_07_SEALED_STDOUT_PATH,
    "--stderr-path",
    V3_07_SEALED_STDERR_PATH,
    "--artifact-inventory-path",
    V3_07_SEALED_ARTIFACT_INVENTORY_PATH,
    "--checksum-manifest-path",
    V3_07_SEALED_CHECKSUM_MANIFEST_PATH,
    "--no-submit",
)

V3_07_BLOCKED_CLI_FLAGS: tuple[str, ...] = (
    "--submit-orders",
    "--paper-order",
    "--paper-orders",
    "--live",
    "--live-order",
    "--live-orders",
    "--controlled-submit",
    "--enable-controlled-submit",
    "--model-promotion",
    "--promote-model",
    "--ppo-rf",
    "--ppo-random-forest",
    "--ppo-xgboost",
    "--xgboost",
)


@dataclass(frozen=True)
class PPOV2NoSubmitCLICompatibilityResult:
    """Result from the v3.07 sealed CLI compatibility check.

    This is a source-code compatibility boundary only. It accepts and validates
    the sealed v3.07 no-submit arguments without performing execution.
    """

    compatibility_manifest: Mapping[str, Any] | None
    compatibility_errors: tuple[str, ...]
    compatibility_metadata: Mapping[str, Any]
    boundary_decision: str


def build_v3_07_no_submit_argument_parser() -> argparse.ArgumentParser:
    """Build the fail-closed parser for the sealed v3.07 no-submit arguments."""

    parser = argparse.ArgumentParser(
        prog="python -m src.ppo_v2_controlled_training_execution",
        add_help=False,
        allow_abbrev=False,
        exit_on_error=False,
        description="Validate sealed v3.07 no-submit PPO v2 CLI compatibility.",
    )
    parser.add_argument("--mode")
    parser.add_argument("--run-id", dest="run_id")
    parser.add_argument("--config")
    parser.add_argument("--quarantine-root", dest="quarantine_root")
    parser.add_argument("--log-root", dest="log_root")
    parser.add_argument("--stdout-path", dest="stdout_path")
    parser.add_argument("--stderr-path", dest="stderr_path")
    parser.add_argument("--artifact-inventory-path", dest="artifact_inventory_path")
    parser.add_argument("--checksum-manifest-path", dest="checksum_manifest_path")
    parser.add_argument("--no-submit", action="store_true", default=False)
    return parser


def build_v3_07_no_submit_cli_compatibility(
    argv: Sequence[str] | None = None,
) -> PPOV2NoSubmitCLICompatibilityResult:
    """Validate the sealed v3.07 CLI arguments without executing training."""

    raw_args = tuple(str(arg) for arg in (argv or ()))
    parser = build_v3_07_no_submit_argument_parser()

    try:
        namespace, unknown_args = parser.parse_known_args(list(raw_args))
    except argparse.ArgumentError as exc:
        return _reject_v3_07_cli(raw_args, (f"sealed CLI arguments are invalid: {exc}",))
    except SystemExit as exc:
        return _reject_v3_07_cli(
            raw_args,
            (f"sealed CLI arguments are invalid: parser exited with code {exc.code}",),
        )

    errors: list[str] = []

    blocked_flags = _collect_v3_07_blocked_flags(raw_args)
    if blocked_flags:
        errors.append(
            "blocked order/hybrid/promotion flags are not authorized: "
            + ", ".join(blocked_flags)
        )

    if unknown_args:
        errors.append(
            "unsupported sealed compatibility arguments: "
            + ", ".join(str(arg) for arg in unknown_args)
        )

    if namespace.no_submit is not True:
        errors.append("--no-submit is required")

    _validate_exact_v3_07_value(errors, "mode", namespace.mode, V3_07_SEALED_MODE)
    _validate_exact_v3_07_value(
        errors,
        "run id",
        namespace.run_id,
        V3_07_SEALED_RUN_ID,
    )
    _validate_exact_v3_07_value(
        errors,
        "config path",
        namespace.config,
        V3_07_SEALED_CONFIG_PATH,
    )
    _validate_exact_v3_07_value(
        errors,
        "quarantine root",
        namespace.quarantine_root,
        V3_07_SEALED_QUARANTINE_ROOT,
    )
    _validate_exact_v3_07_value(
        errors,
        "log root",
        namespace.log_root,
        V3_07_SEALED_LOG_ROOT,
    )
    _validate_exact_v3_07_value(
        errors,
        "stdout path",
        namespace.stdout_path,
        V3_07_SEALED_STDOUT_PATH,
    )
    _validate_exact_v3_07_value(
        errors,
        "stderr path",
        namespace.stderr_path,
        V3_07_SEALED_STDERR_PATH,
    )
    _validate_exact_v3_07_value(
        errors,
        "artifact inventory path",
        namespace.artifact_inventory_path,
        V3_07_SEALED_ARTIFACT_INVENTORY_PATH,
    )
    _validate_exact_v3_07_value(
        errors,
        "checksum manifest path",
        namespace.checksum_manifest_path,
        V3_07_SEALED_CHECKSUM_MANIFEST_PATH,
    )

    path_fields = (
        ("config path", namespace.config, None),
        ("quarantine root", namespace.quarantine_root, V3_07_APPROVED_QUARANTINE_ROOT),
        ("log root", namespace.log_root, V3_07_APPROVED_LOG_ROOT),
        ("stdout path", namespace.stdout_path, V3_07_SEALED_LOG_ROOT),
        ("stderr path", namespace.stderr_path, V3_07_SEALED_LOG_ROOT),
        (
            "artifact inventory path",
            namespace.artifact_inventory_path,
            V3_07_SEALED_QUARANTINE_ROOT,
        ),
        (
            "checksum manifest path",
            namespace.checksum_manifest_path,
            V3_07_SEALED_QUARANTINE_ROOT,
        ),
    )

    for field_name, value, approved_root in path_fields:
        _validate_relative_v3_07_path(errors, field_name, value)
        if approved_root is not None:
            _validate_v3_07_path_under_root(errors, field_name, value, approved_root)

    if namespace.config == V3_07_SEALED_CONFIG_PATH and not Path(namespace.config).is_file():
        errors.append("sealed config path must exist in repository")

    if errors:
        return _reject_v3_07_cli(raw_args, tuple(errors))

    manifest = {
        "schema_version": "v3.07-source-code-execution-compatibility",
        "compatibility_scope": "sealed_cli_argument_validation_only",
        "selected_entrypoint": "src.ppo_v2_controlled_training_execution",
        "sealed_command_arguments_accepted": True,
        "source_code_execution_compatibility_check_passed": True,
        "execution_performed": False,
        "training_performed": False,
        "training_authorized": False,
        "training_command_execution_authorized": False,
        "ppo_v2_training_execution_authorized": False,
        "v3_07_execution_authorized": False,
        "preflight_executed": False,
        "preflight_passed": False,
        "execution_ready_proven": False,
        "data_fetching_authorized": False,
        "dataset_generation_authorized": False,
        "dataset_write_authorized": False,
        "model_artifact_creation_authorized": False,
        "quarantine_output_creation_authorized": False,
        "model_promotion_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
        "creates_model_artifacts": False,
        "creates_quarantine_outputs": False,
        "writes_stdout_path": False,
        "writes_stderr_path": False,
        "writes_artifact_inventory_path": False,
        "writes_checksum_manifest_path": False,
        "no_submit_required": True,
        "no_submit_present": True,
        "run_id": namespace.run_id,
        "config_path": namespace.config,
        "quarantine_root": namespace.quarantine_root,
        "log_root": namespace.log_root,
        "stdout_path": namespace.stdout_path,
        "stderr_path": namespace.stderr_path,
        "artifact_inventory_path": namespace.artifact_inventory_path,
        "checksum_manifest_path": namespace.checksum_manifest_path,
        "next_required_review": "independent v3.07 source-code compatibility review",
    }

    return PPOV2NoSubmitCLICompatibilityResult(
        compatibility_manifest=manifest,
        compatibility_errors=(),
        compatibility_metadata=_build_v3_07_cli_metadata(raw_args),
        boundary_decision=PASS_DECISION,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for v3.07 sealed argument compatibility only."""

    result = build_v3_07_no_submit_cli_compatibility(
        sys.argv[1:] if argv is None else argv
    )
    return 0 if result.boundary_decision == PASS_DECISION else 2


def _reject_v3_07_cli(
    raw_args: tuple[str, ...],
    errors: tuple[str, ...],
) -> PPOV2NoSubmitCLICompatibilityResult:
    return PPOV2NoSubmitCLICompatibilityResult(
        compatibility_manifest=None,
        compatibility_errors=errors,
        compatibility_metadata=_build_v3_07_cli_metadata(raw_args),
        boundary_decision=REJECTED_FAIL_CLOSED_DECISION,
    )


def _build_v3_07_cli_metadata(raw_args: tuple[str, ...]) -> Mapping[str, Any]:
    return {
        "checkpoint": "v3.07_source_code_execution_compatibility",
        "scope": "sealed_cli_argument_validation_only",
        "argument_count": len(raw_args),
        "execution_performed": False,
        "training_performed": False,
        "training_authorized": False,
        "training_command_execution_authorized": False,
        "ppo_v2_training_execution_authorized": False,
        "data_fetching_authorized": False,
        "dataset_generation_authorized": False,
        "model_artifact_creation_authorized": False,
        "quarantine_output_creation_authorized": False,
        "model_promotion_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
        "no_submit_default": True,
    }


def _validate_exact_v3_07_value(
    errors: list[str],
    field_name: str,
    value: object,
    expected_value: str,
) -> None:
    if _is_blank_string(value):
        errors.append(f"{field_name} must be provided")
        return

    if str(value) != expected_value:
        errors.append(f"{field_name} must match sealed v3.07 {field_name}")


def _validate_relative_v3_07_path(
    errors: list[str],
    field_name: str,
    value: object,
) -> None:
    if _is_blank_string(value):
        return

    path = PurePosixPath(str(value))
    if path.is_absolute():
        errors.append(f"{field_name} must remain relative")

    if ".." in path.parts:
        errors.append(f"{field_name} must not contain path traversal")


def _validate_v3_07_path_under_root(
    errors: list[str],
    field_name: str,
    value: object,
    approved_root: str,
) -> None:
    if _is_blank_string(value):
        return

    path_parts = PurePosixPath(str(value)).parts
    root_parts = PurePosixPath(approved_root).parts

    if path_parts[: len(root_parts)] != root_parts:
        errors.append(f"{field_name} must remain under {approved_root}")


def _collect_v3_07_blocked_flags(raw_args: tuple[str, ...]) -> tuple[str, ...]:
    blocked: list[str] = []

    for arg in raw_args:
        for flag in V3_07_BLOCKED_CLI_FLAGS:
            if arg == flag or arg.startswith(flag + "="):
                blocked.append(flag)

    return tuple(dict.fromkeys(blocked))

__all__ = [
    "ALLOWED_CONTROLLED_EXECUTION_SCAFFOLD_MODES",
    "V3_07_SEALED_CLI_ARGUMENTS",
    "V3_07_SEALED_RUN_ID",
    "V3_07_SEALED_CONFIG_PATH",
    "V3_07_SEALED_QUARANTINE_ROOT",
    "V3_07_SEALED_LOG_ROOT",
    "V3_07_SEALED_STDOUT_PATH",
    "V3_07_SEALED_STDERR_PATH",
    "V3_07_SEALED_ARTIFACT_INVENTORY_PATH",
    "V3_07_SEALED_CHECKSUM_MANIFEST_PATH",
    "REQUIRED_HISTORICAL_VALIDATION_PROTECTIONS",
    "PPOV2ControlledTrainingExecutionRequest",
    "PPOV2ControlledTrainingExecutionResult",
    "PPOV2NoSubmitCLICompatibilityResult",
    "build_ppo_v2_controlled_training_execution",
    "build_v3_07_no_submit_argument_parser",
    "build_v3_07_no_submit_cli_compatibility",
    "main",
]


if __name__ == "__main__":
    sys.exit(main())
