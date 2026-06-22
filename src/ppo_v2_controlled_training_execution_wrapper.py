"""
PPO v2 controlled training execution wrapper scaffold.

This module defines a fail-closed wrapper specification for a future
one-time controlled PPO v2 training execution. It does not train a model,
fetch data, generate datasets, create model artifacts, submit broker orders,
or promote any model.

The wrapper is intentionally non-executing in v2.01. It can build and validate
a command specification and preflight manifest for a later controlled execution
checkpoint.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


PROHIBITED_COMMAND_TOKENS: tuple[str, ...] = (
    "--submit-orders",
    "--live",
    "--paper-order",
    "--controlled-submit",
    "submit_order",
    "TradingClient",
    "StockHistoricalDataClient",
    "PPO.learn",
    ".learn",
    "joblib.dump",
    "torch.save",
    "pickle.dump",
    "to_csv",
    "to_parquet",
)

REQUIRED_CAPTURE_NAMES: tuple[str, ...] = (
    "configuration_snapshot_path",
    "training_input_manifest_path",
    "runtime_log_path",
    "stdout_capture_path",
    "stderr_capture_path",
    "artifact_inventory_path",
    "checksum_manifest_path",
    "metrics_output_path",
    "post_training_audit_package_path",
)

REQUIRED_GUARDRAILS: tuple[str, ...] = (
    "require_clean_git_state",
    "require_source_of_truth_docs",
    "require_sealed_v2_00_checkpoint",
    "require_quarantine_root",
    "require_no_submit_default",
    "block_model_promotion",
    "block_paper_orders",
    "block_live_orders",
    "block_controlled_submit",
    "block_ppo_rf",
    "block_ppo_xgboost",
    "classify_outputs_as_quarantined_training_output_only",
)


@dataclass(frozen=True)
class PPOV2ControlledExecutionWrapperRequest:
    """Request for building a non-executing controlled execution wrapper manifest."""

    command_name: str = "ppo-v2-controlled-training-execution"
    execution_mode: str = "scaffold_only"
    run_identifier: str = "ppo_v2_one_time_controlled_training_execution"
    ticker_universe: tuple[str, ...] = ("AAPL", "AMD", "MRK", "PFE", "UNH", "XOM")
    historical_data_source: str = "alpaca_historical_loader_controlled_source"
    train_period: str = "DEFINED_BY_FUTURE_EXECUTION_CHECKPOINT"
    embargo_period: str = "DEFINED_BY_FUTURE_EXECUTION_CHECKPOINT"
    evaluation_period: str = "DEFINED_BY_FUTURE_EXECUTION_CHECKPOINT"
    holdout_period: str = "UNTOUCHED_UNTIL_FINAL_VALIDATION"
    quarantine_root: str = "artifacts/ppo_v2/quarantine"
    configuration_snapshot_path: str = "artifacts/ppo_v2/quarantine/configuration_snapshot.json"
    training_input_manifest_path: str = "artifacts/ppo_v2/quarantine/training_input_manifest.json"
    runtime_log_path: str = "artifacts/ppo_v2/quarantine/runtime_log.json"
    stdout_capture_path: str = "artifacts/ppo_v2/quarantine/stdout.txt"
    stderr_capture_path: str = "artifacts/ppo_v2/quarantine/stderr.txt"
    artifact_inventory_path: str = "artifacts/ppo_v2/quarantine/artifact_inventory.json"
    checksum_manifest_path: str = "artifacts/ppo_v2/quarantine/checksum_manifest.json"
    metrics_output_path: str = "artifacts/ppo_v2/quarantine/metrics.json"
    post_training_audit_package_path: str = "artifacts/ppo_v2/quarantine/post_training_audit_package.json"
    guardrails: tuple[str, ...] = REQUIRED_GUARDRAILS
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
    command_tokens: tuple[str, ...] = field(
        default_factory=lambda: (
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution_wrapper",
            "--mode",
            "scaffold-only",
            "--run-id",
            "ppo_v2_one_time_controlled_training_execution",
            "--no-submit",
        )
    )


@dataclass(frozen=True)
class PPOV2ControlledExecutionWrapperResult:
    """Fail-closed wrapper scaffold result."""

    boundary_decision: str
    wrapper_manifest: Mapping[str, Any] | None
    errors: tuple[str, ...]
    metadata: Mapping[str, Any]


def build_ppo_v2_controlled_execution_wrapper(
    request: PPOV2ControlledExecutionWrapperRequest | None = None,
) -> PPOV2ControlledExecutionWrapperResult:
    """Build a non-executing fail-closed wrapper manifest."""

    if request is None:
        request = PPOV2ControlledExecutionWrapperRequest()

    if not isinstance(request, PPOV2ControlledExecutionWrapperRequest):
        return PPOV2ControlledExecutionWrapperResult(
            boundary_decision="REJECT",
            wrapper_manifest=None,
            errors=("request must be PPOV2ControlledExecutionWrapperRequest",),
            metadata=_build_metadata(None),
        )

    errors: list[str] = []
    errors.extend(_validate_required_text_fields(request))
    errors.extend(_validate_paths(request))
    errors.extend(_validate_guardrails(request))
    errors.extend(_validate_permissions(request))
    errors.extend(_validate_command_tokens(request))

    if errors:
        return PPOV2ControlledExecutionWrapperResult(
            boundary_decision="REJECT",
            wrapper_manifest=None,
            errors=tuple(errors),
            metadata=_build_metadata(request),
        )

    manifest: dict[str, Any] = {
        "schema_version": "v2.01",
        "wrapper_status": "SCAFFOLD_ONLY",
        "execution_performed": False,
        "training_execution_authorized": False,
        "data_fetching_authorized": False,
        "dataset_generation_authorized": False,
        "model_artifact_creation_authorized": False,
        "model_promotion_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
        "no_submit_default": True,
        "output_classification": "QUARANTINED_TRAINING_OUTPUT_ONLY",
        "command_specification": {
            "command_name": request.command_name,
            "execution_mode": request.execution_mode,
            "command_tokens": request.command_tokens,
        },
        "run_identifier": request.run_identifier,
        "ticker_universe": request.ticker_universe,
        "historical_data_source": request.historical_data_source,
        "temporal_boundaries": {
            "train_period": request.train_period,
            "embargo_period": request.embargo_period,
            "evaluation_period": request.evaluation_period,
            "holdout_period": request.holdout_period,
        },
        "quarantine_root": request.quarantine_root,
        "capture_paths": {
            "configuration_snapshot_path": request.configuration_snapshot_path,
            "training_input_manifest_path": request.training_input_manifest_path,
            "runtime_log_path": request.runtime_log_path,
            "stdout_capture_path": request.stdout_capture_path,
            "stderr_capture_path": request.stderr_capture_path,
            "artifact_inventory_path": request.artifact_inventory_path,
            "checksum_manifest_path": request.checksum_manifest_path,
            "metrics_output_path": request.metrics_output_path,
            "post_training_audit_package_path": request.post_training_audit_package_path,
        },
        "required_guardrails": request.guardrails,
        "next_required_review": "v2.02 controlled execution wrapper scaffold review",
    }

    return PPOV2ControlledExecutionWrapperResult(
        boundary_decision="PASS",
        wrapper_manifest=manifest,
        errors=(),
        metadata=_build_metadata(request),
    )


def _validate_required_text_fields(
    request: PPOV2ControlledExecutionWrapperRequest,
) -> tuple[str, ...]:
    errors: list[str] = []
    for field_name in (
        "command_name",
        "execution_mode",
        "run_identifier",
        "historical_data_source",
        "train_period",
        "embargo_period",
        "evaluation_period",
        "holdout_period",
        "quarantine_root",
    ):
        value = getattr(request, field_name)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field_name} must be a non-empty string")

    if not request.ticker_universe:
        errors.append("ticker_universe must not be empty")
    elif any(not isinstance(ticker, str) or not ticker.strip() for ticker in request.ticker_universe):
        errors.append("ticker_universe must contain non-empty strings")

    return tuple(errors)


def _validate_paths(request: PPOV2ControlledExecutionWrapperRequest) -> tuple[str, ...]:
    errors: list[str] = []
    for field_name in REQUIRED_CAPTURE_NAMES:
        value = getattr(request, field_name)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field_name} must be a non-empty string")
            continue
        path = Path(value)
        if path.is_absolute():
            errors.append(f"{field_name} must be relative and quarantined")
        if "quarantine" not in path.parts:
            errors.append(f"{field_name} must remain under a quarantine path")
    return tuple(errors)


def _validate_guardrails(request: PPOV2ControlledExecutionWrapperRequest) -> tuple[str, ...]:
    missing = [name for name in REQUIRED_GUARDRAILS if name not in request.guardrails]
    if missing:
        return ("required guardrails are incomplete",)
    return ()


def _validate_permissions(request: PPOV2ControlledExecutionWrapperRequest) -> tuple[str, ...]:
    permission_checks = (
        (request.allow_training_execution, "training execution request is not authorized in v2.01"),
        (request.allow_data_fetching, "data fetching request is not authorized in v2.01"),
        (request.allow_dataset_generation, "dataset generation request is not authorized in v2.01"),
        (request.allow_model_artifact_creation, "model artifact creation request is not authorized in v2.01"),
        (request.allow_model_promotion, "model promotion request is not authorized"),
        (request.allow_paper_orders, "paper order request is not authorized"),
        (request.allow_live_orders, "live order request is not authorized"),
        (request.allow_controlled_submit, "controlled submit request is not authorized"),
        (request.allow_ppo_rf, "PPO + RF request is not authorized"),
        (request.allow_ppo_xgboost, "PPO + XGBoost request is not authorized"),
    )
    return tuple(message for flag, message in permission_checks if flag is not False)


def _validate_command_tokens(request: PPOV2ControlledExecutionWrapperRequest) -> tuple[str, ...]:
    if not request.command_tokens:
        return ("command_tokens must not be empty",)

    command_text = " ".join(str(token) for token in request.command_tokens)

    errors: list[str] = []
    if "--no-submit" not in request.command_tokens:
        errors.append("command_tokens must include --no-submit")
    if "--mode" not in request.command_tokens:
        errors.append("command_tokens must include --mode")
    if "scaffold-only" not in request.command_tokens:
        errors.append("command_tokens must use scaffold-only mode")

    for token in PROHIBITED_COMMAND_TOKENS:
        if token in command_text:
            errors.append(f"command_tokens contain prohibited token: {token}")

    return tuple(errors)


def _build_metadata(
    request: PPOV2ControlledExecutionWrapperRequest | None,
) -> Mapping[str, Any]:
    return {
        "checkpoint": "v2.01",
        "scope": "controlled_training_execution_wrapper_scaffold",
        "execution_performed": False,
        "training_execution_authorized": False,
        "model_promotion_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
        "no_submit_default": True,
        "request_type": type(request).__name__ if request is not None else None,
    }
