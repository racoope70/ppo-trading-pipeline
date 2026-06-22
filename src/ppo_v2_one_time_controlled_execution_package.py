"""
PPO v2 one-time controlled execution package scaffold.

This module is intentionally non-executing. It builds and validates a future
controlled training package manifest, but it does not train, fetch data, write
datasets, create model artifacts, submit broker orders, or promote models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any, Mapping, Sequence


PACKAGE_SCHEMA_VERSION = "v2.08"
PACKAGE_STATUS = "IMPLEMENTATION_SCAFFOLD_ONLY"
OUTPUT_CLASSIFICATION = "QUARANTINED_TRAINING_OUTPUT_ONLY"
REQUIRED_MODE = "controlled-training"
REQUIRED_NO_SUBMIT_FLAG = "--no-submit"
REQUIRED_QUARANTINE_PREFIX = "artifacts/ppo_v2/quarantine"


REQUIRED_PACKAGE_ITEMS = (
    "single_explicit_future_training_command",
    "command_mode_field",
    "no_submit_flag",
    "configuration_snapshot_manifest",
    "training_input_manifest",
    "temporal_boundary_manifest",
    "ticker_universe_manifest",
    "controlled_data_source_manifest",
    "feature_set_manifest",
    "normalization_policy_manifest",
    "embargo_policy_manifest",
    "holdout_protection_manifest",
    "random_seed_manifest",
    "dependency_environment_snapshot",
    "runtime_log_path",
    "stdout_capture_path",
    "stderr_capture_path",
    "quarantine_root",
    "artifact_inventory_path",
    "checksum_manifest_path",
    "metrics_output_path",
    "post_training_audit_package_path",
    "failure_flag_policy",
    "non_promotion_statement",
    "non_trading_statement",
    "non_hybrid_statement",
)

REQUIRED_GUARDRAILS = (
    "no_submit_default",
    "no_broker_orders",
    "no_live_orders",
    "no_paper_orders",
    "no_controlled_submit",
    "no_model_promotion",
    "no_hybrid_continuation",
    "ppo_only_scope",
    "train_only_normalization_required",
    "embargo_required",
    "untouched_holdout_required",
    "quarantine_only_outputs",
)

REQUIRED_OUTPUT_FILES = (
    "configuration_snapshot.json",
    "training_input_manifest.json",
    "temporal_boundary_manifest.json",
    "ticker_universe_manifest.json",
    "data_source_manifest.json",
    "normalization_policy_manifest.json",
    "embargo_policy_manifest.json",
    "holdout_protection_manifest.json",
    "runtime_log.json",
    "stdout.txt",
    "stderr.txt",
    "artifact_inventory.json",
    "checksum_manifest.json",
    "metrics.json",
    "post_training_audit_package.json",
    "failure_flags.json",
)

PROHIBITED_COMMAND_FRAGMENTS = (
    "--submit",
    "--live",
    "--paper",
    "--controlled-submit",
    "--promote",
    "--ppo-rf",
    "--ppo-xgboost",
    "submit",
    "order",
    "live",
    "paper",
    "promote",
    "xgboost",
    "random-forest",
)


@dataclass(frozen=True)
class PPOV2OneTimeExecutionPackageRequest:
    """Request for building a non-executing controlled package scaffold."""

    run_id: str = "ppo_v2_controlled_training_run_id_placeholder"
    command: tuple[str, ...] = (
        "python",
        "-m",
        "ppo_v2_future_execution_entrypoint",
        "--mode",
        "controlled-training",
        "--run-id",
        "ppo_v2_controlled_training_run_id_placeholder",
        "--config",
        "configs/ppo_v2/controlled_training_config_placeholder.yaml",
        "--quarantine-root",
        "artifacts/ppo_v2/quarantine/ppo_v2_controlled_training_run_id_placeholder",
        "--no-submit",
    )
    config_path: str = "configs/ppo_v2/controlled_training_config_placeholder.yaml"
    quarantine_root: str = "artifacts/ppo_v2/quarantine/ppo_v2_controlled_training_run_id_placeholder"
    package_items: tuple[str, ...] = REQUIRED_PACKAGE_ITEMS
    guardrails: tuple[str, ...] = REQUIRED_GUARDRAILS
    output_files: tuple[str, ...] = REQUIRED_OUTPUT_FILES

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


@dataclass(frozen=True)
class PPOV2OneTimeExecutionPackageResult:
    """Result from the package scaffold validator."""

    boundary_decision: str
    package_manifest: Mapping[str, Any] | None = None
    errors: tuple[str, ...] = field(default_factory=tuple)


def build_ppo_v2_one_time_execution_package(
    request: PPOV2OneTimeExecutionPackageRequest | None = None,
) -> PPOV2OneTimeExecutionPackageResult:
    """Build and validate a non-executing future execution package manifest."""

    request = request or PPOV2OneTimeExecutionPackageRequest()
    errors = _validate_request(request)

    if errors:
        return PPOV2OneTimeExecutionPackageResult(
            boundary_decision="FAIL_CLOSED",
            package_manifest=None,
            errors=tuple(errors),
        )

    manifest = _build_manifest(request)
    return PPOV2OneTimeExecutionPackageResult(
        boundary_decision="PASS",
        package_manifest=manifest,
        errors=(),
    )


def _validate_request(request: PPOV2OneTimeExecutionPackageRequest) -> list[str]:
    errors: list[str] = []

    if not isinstance(request.run_id, str) or not request.run_id.strip():
        errors.append("run_id must be a non-empty string")

    if not request.command:
        errors.append("command must be non-empty")

    command_text = " ".join(request.command).lower()

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
        if fragment == "--no-submit":
            continue
        if fragment in command_text and fragment not in {"submit"}:
            errors.append(f"command contains prohibited fragment: {fragment}")

    if "submit" in command_text.replace("--no-submit", ""):
        errors.append("command contains submit outside no-submit guardrail")

    if not _is_quarantined(request.quarantine_root):
        errors.append("quarantine_root must stay under artifacts/ppo_v2/quarantine")

    missing_items = sorted(set(REQUIRED_PACKAGE_ITEMS).difference(request.package_items))
    if missing_items:
        errors.append("missing required package items: " + ", ".join(missing_items))

    missing_guardrails = sorted(set(REQUIRED_GUARDRAILS).difference(request.guardrails))
    if missing_guardrails:
        errors.append("missing required guardrails: " + ", ".join(missing_guardrails))

    missing_outputs = sorted(set(REQUIRED_OUTPUT_FILES).difference(request.output_files))
    if missing_outputs:
        errors.append("missing required output files: " + ", ".join(missing_outputs))

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
    }

    for name, enabled in permission_checks.items():
        if enabled:
            errors.append(f"{name} must remain disabled in v2.08 scaffold")

    return errors


def _build_manifest(request: PPOV2OneTimeExecutionPackageRequest) -> dict[str, Any]:
    output_paths = {
        file_name: str(PurePosixPath(request.quarantine_root) / file_name)
        for file_name in request.output_files
    }

    return {
        "schema_version": PACKAGE_SCHEMA_VERSION,
        "package_status": PACKAGE_STATUS,
        "run_id": request.run_id,
        "command": list(request.command),
        "config_path": request.config_path,
        "quarantine_root": request.quarantine_root,
        "output_paths": output_paths,
        "package_items": list(request.package_items),
        "guardrails": list(request.guardrails),
        "output_classification": OUTPUT_CLASSIFICATION,
        "training_execution_performed": False,
        "data_fetching_performed": False,
        "dataset_generation_performed": False,
        "model_artifact_creation_performed": False,
        "model_promotion_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
        "no_submit_default": True,
    }


def _is_quarantined(path: str) -> bool:
    try:
        normalized = PurePosixPath(path)
    except TypeError:
        return False

    return str(normalized).startswith(REQUIRED_QUARANTINE_PREFIX + "/")
