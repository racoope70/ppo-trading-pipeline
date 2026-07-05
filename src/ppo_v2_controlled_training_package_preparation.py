"""
PPO v2 controlled training execution package preparation scaffold.

This module is intentionally non-executing. It validates the shape of a future
controlled training execution package preparation request and builds an in-memory
manifest only. It does not write files, fetch data, train models, create model
artifacts, promote models, or submit broker orders.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any, Mapping


PREPARATION_SCHEMA_VERSION = "v2.13"
PREPARATION_STATUS = "PREPARATION_SCAFFOLD_ONLY"
PACKAGE_CLASSIFICATION = "NON_EXECUTING_PREPARATION_MANIFEST_ONLY"
REQUIRED_NO_SUBMIT_FLAG = "--no-submit"
REQUIRED_MODE = "controlled-training"
REQUIRED_PREPARATION_PREFIX = "artifacts/ppo_v2/package_preparation"
REQUIRED_QUARANTINE_PREFIX = "artifacts/ppo_v2/quarantine"
CANONICAL_H1_COMMAND_MODULE = "src.ppo_v2_controlled_training_execution"
CANONICAL_H1_COMMAND_BOUNDARY_STATUS = "FUTURE_ONLY_NO_SUBMIT_REVIEW_BOUNDARY_NOT_AUTHORIZATION"
HISTORICAL_H1_COMMAND_SPELLINGS = (
    "ppo_v2_future_execution_entrypoint",
    "ppo_v2_controlled_training_execution",
    "src.ppo_v2_controlled_training_execution_wrapper",
    "python -m ppo_v2_controlled_training_execution",
)

REQUIRED_PREPARATION_DIRECTORIES = (
    "config",
    "manifests",
    "commands",
    "validation",
    "logs",
)

REQUIRED_PREPARATION_FILES = (
    "config/controlled_training_config.yaml",
    "manifests/data_source_manifest.json",
    "manifests/ticker_universe_manifest.json",
    "manifests/temporal_boundary_manifest.json",
    "manifests/feature_set_manifest.json",
    "manifests/normalization_policy_manifest.json",
    "manifests/locked_eval_stats_policy.json",
    "manifests/embargo_policy_manifest.json",
    "manifests/holdout_protection_manifest.json",
    "manifests/random_seed_manifest.json",
    "manifests/dependency_environment_snapshot.json",
    "manifests/output_inventory_plan.json",
    "manifests/checksum_manifest_policy.json",
    "commands/one_time_no_submit_command.txt",
    "validation/fail_closed_validation_checklist.json",
    "validation/pre_execution_validation_results.json",
    "logs/preparation_log.json",
)

REQUIRED_CONTROLLED_BOUNDARIES = (
    "ppo_only_scope",
    "legacy_ppo_infrastructure_fixture_only",
    "historical_data_source_only",
    "no_live_market_stream",
    "no_broker_trading_client",
    "train_only_normalization_required",
    "locked_evaluation_statistics_required",
    "embargo_required",
    "untouched_holdout_required",
    "quarantine_only_outputs",
    "no_model_promotion",
    "no_paper_orders",
    "no_live_orders",
    "no_controlled_submit",
    "no_ppo_rf",
    "no_ppo_xgboost",
)

PROHIBITED_COMMAND_FRAGMENTS = (
    "--submit",
    "--paper",
    "--live",
    "--controlled-submit",
    "--promote",
    "--ppo-rf",
    "--ppo-xgboost",
    "TradingClient",
    "StockHistoricalDataClient",
    "submit_order",
    "PPO.load",
    "learn(",
)


@dataclass(frozen=True)
class PPOV2PreparationScaffoldRequest:
    """Request for building a non-executing preparation scaffold manifest."""

    run_id: str = "ppo_v2_preparation_run_id_placeholder"
    preparation_root: str = (
        "artifacts/ppo_v2/package_preparation/ppo_v2_preparation_run_id_placeholder"
    )
    quarantine_root: str = (
        "artifacts/ppo_v2/quarantine/ppo_v2_preparation_run_id_placeholder"
    )
    command: tuple[str, ...] = (
        "python",
        "-m",
        CANONICAL_H1_COMMAND_MODULE,
        "--mode",
        "controlled-training",
        "--run-id",
        "ppo_v2_preparation_run_id_placeholder",
        "--config",
        "artifacts/ppo_v2/package_preparation/ppo_v2_preparation_run_id_placeholder/config/controlled_training_config.yaml",
        "--quarantine-root",
        "artifacts/ppo_v2/quarantine/ppo_v2_preparation_run_id_placeholder",
        "--no-submit",
    )
    preparation_directories: tuple[str, ...] = REQUIRED_PREPARATION_DIRECTORIES
    preparation_files: tuple[str, ...] = REQUIRED_PREPARATION_FILES
    controlled_boundaries: tuple[str, ...] = REQUIRED_CONTROLLED_BOUNDARIES

    allow_training_execution: bool = False
    allow_data_fetching: bool = False
    allow_dataset_generation: bool = False
    allow_model_artifact_creation: bool = False
    allow_model_promotion: bool = False
    allow_paper_orders: bool = False
    allow_live_orders: bool = False
    allow_controlled_submit: bool = False
    allow_ppo_rf: bool = False
    allow_ppo_xgboost: bool = False
    allow_filesystem_writes: bool = False


@dataclass(frozen=True)
class PPOV2PreparationScaffoldResult:
    """Result from the preparation scaffold validator."""

    boundary_decision: str
    preparation_manifest: Mapping[str, Any] | None = None
    errors: tuple[str, ...] = field(default_factory=tuple)


def build_ppo_v2_preparation_scaffold(
    request: PPOV2PreparationScaffoldRequest | None = None,
) -> PPOV2PreparationScaffoldResult:
    """Build an in-memory, non-executing preparation scaffold manifest."""

    request = request or PPOV2PreparationScaffoldRequest()
    errors = _validate_request(request)

    if errors:
        return PPOV2PreparationScaffoldResult(
            boundary_decision="FAIL_CLOSED",
            preparation_manifest=None,
            errors=tuple(errors),
        )

    return PPOV2PreparationScaffoldResult(
        boundary_decision="PASS",
        preparation_manifest=_build_manifest(request),
        errors=(),
    )


def _validate_request(request: PPOV2PreparationScaffoldRequest) -> list[str]:
    errors: list[str] = []

    if not isinstance(request.run_id, str) or not request.run_id.strip():
        errors.append("run_id must be a non-empty sealed identifier placeholder")

    if not _is_under_prefix(request.preparation_root, REQUIRED_PREPARATION_PREFIX):
        errors.append("preparation_root must stay under artifacts/ppo_v2/package_preparation")

    if not _is_under_prefix(request.quarantine_root, REQUIRED_QUARANTINE_PREFIX):
        errors.append("quarantine_root must stay under artifacts/ppo_v2/quarantine")

    if not request.command:
        errors.append("command must be non-empty")

    command_text = " ".join(request.command)

    if REQUIRED_NO_SUBMIT_FLAG not in request.command:
        errors.append("command must include --no-submit")

    if "--mode" not in request.command or REQUIRED_MODE not in request.command:
        errors.append("command must include controlled-training mode")

    if "--run-id" not in request.command:
        errors.append("command must include explicit run id")

    if "--config" not in request.command:
        errors.append("command must include explicit config path")

    if "--quarantine-root" not in request.command:
        errors.append("command must include explicit quarantine root")

    for fragment in PROHIBITED_COMMAND_FRAGMENTS:
        if fragment in command_text:
            errors.append(f"command contains prohibited fragment: {fragment}")

    if "submit" in command_text.replace("--no-submit", ""):
        errors.append("command contains submit outside no-submit guardrail")

    missing_dirs = sorted(
        set(REQUIRED_PREPARATION_DIRECTORIES).difference(request.preparation_directories)
    )
    if missing_dirs:
        errors.append("missing required preparation directories: " + ", ".join(missing_dirs))

    missing_files = sorted(
        set(REQUIRED_PREPARATION_FILES).difference(request.preparation_files)
    )
    if missing_files:
        errors.append("missing required preparation files: " + ", ".join(missing_files))

    missing_boundaries = sorted(
        set(REQUIRED_CONTROLLED_BOUNDARIES).difference(request.controlled_boundaries)
    )
    if missing_boundaries:
        errors.append("missing required controlled boundaries: " + ", ".join(missing_boundaries))

    permission_checks = {
        "training execution": request.allow_training_execution,
        "data fetching": request.allow_data_fetching,
        "dataset generation": request.allow_dataset_generation,
        "model artifact creation": request.allow_model_artifact_creation,
        "model promotion": request.allow_model_promotion,
        "paper orders": request.allow_paper_orders,
        "live orders": request.allow_live_orders,
        "controlled submit": request.allow_controlled_submit,
        "PPO plus Random Forest": request.allow_ppo_rf,
        "PPO plus XGBoost": request.allow_ppo_xgboost,
        "filesystem writes": request.allow_filesystem_writes,
    }

    for name, enabled in permission_checks.items():
        if enabled:
            errors.append(f"{name} must remain disabled in v2.13 scaffold")

    return errors


def _build_manifest(request: PPOV2PreparationScaffoldRequest) -> dict[str, Any]:
    preparation_paths = {
        file_name: str(PurePosixPath(request.preparation_root) / file_name)
        for file_name in request.preparation_files
    }

    return {
        "schema_version": PREPARATION_SCHEMA_VERSION,
        "preparation_status": PREPARATION_STATUS,
        "package_classification": PACKAGE_CLASSIFICATION,
        "run_id": request.run_id,
        "preparation_root": request.preparation_root,
        "quarantine_root": request.quarantine_root,
        "command": list(request.command),
        "canonical_command_module": CANONICAL_H1_COMMAND_MODULE,
        "command_boundary_status": CANONICAL_H1_COMMAND_BOUNDARY_STATUS,
        "historical_placeholder_command_spellings": list(HISTORICAL_H1_COMMAND_SPELLINGS),
        "preparation_directories": list(request.preparation_directories),
        "preparation_files": list(request.preparation_files),
        "preparation_paths": preparation_paths,
        "controlled_boundaries": list(request.controlled_boundaries),
        "training_execution_performed": False,
        "data_fetching_performed": False,
        "dataset_generation_performed": False,
        "model_artifact_creation_performed": False,
        "filesystem_writes_performed": False,
        "model_promotion_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
        "no_submit_default": True,
    }


def _is_under_prefix(path: str, prefix: str) -> bool:
    try:
        normalized = PurePosixPath(path)
    except TypeError:
        return False

    return str(normalized).startswith(prefix + "/")
