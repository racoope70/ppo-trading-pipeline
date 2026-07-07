"""v3.07 validation-only preflight execution path.

This module is scoped only to R1-R6 validation evidence.

It is not a training runner. It does not execute the sealed training command,
call the forbidden training API, fit models, fetch data, generate datasets, create model
artifacts, create quarantine model outputs, submit orders, promote models,
or unblock controlled submit / PPO + RF / PPO + XGBoost.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path, PurePosixPath
from typing import Any


PASS_RESULT = "PASS"
FAIL_RESULT = "FAIL"
PARTIAL_FAIL_RESULT = "PARTIAL_FAIL"
REJECTED_FAIL_CLOSED_RESULT = "REJECTED_FAIL_CLOSED"

V3_07_VALIDATION_RUN_ID = "v3_07_validation_only_preflight_r1_r6_001"
V3_07_CONFIG_PATH = (
    "artifacts/ppo_v2/package_preparation/"
    "v3_07_no_submit_training_execution_package/config/"
    "v3_07_no_submit_training_config.yaml"
)
V3_07_DEFAULT_OUTPUT_ROOT = (
    "artifacts/ppo_v2/preflight_validation/v3_07_validation_only_preflight"
)
V3_07_DEFAULT_SEALED_DATASET_PATH = (
    "data/processed/ppo_v2/v3_07_no_submit_training_input.parquet"
)

REQUIRED_METADATA_COLUMNS: tuple[str, ...] = ("Symbol", "Datetime")
REQUIRED_OHLCV_COLUMNS: tuple[str, ...] = ("Open", "High", "Low", "Close", "Volume")
FORBIDDEN_FEATURE_INPUT_COLUMNS: tuple[str, ...] = (
    "Target",
    "Return",
    "Datetime",
    "Symbol",
)

EVIDENCE_FILE_NAMES: Mapping[str, str] = {
    "R1": "r1_preflight_result.json",
    "R2": "r2_sealed_dataset_identity.json",
    "R3": "r3_data_contract_coverage.json",
    "R4": "r4_temporal_split_embargo_holdout.json",
    "R5": "r5_training_input_handoff.json",
    "R6": "r6_runtime_dependency_git_state.json",
}

BLOCKED_CLI_FLAGS: tuple[str, ...] = (
    "--train",
    "--training",
    "--execute-training",
    "--execute-sealed-training-command",
    "--sealed-training-command",
    "--model-learn",
    "--fit-model",
    "--data-fetch",
    "--fetch-data",
    "--download-data",
    "--generate-dataset",
    "--create-dataset",
    "--create-model-artifact",
    "--create-quarantine-model-output",
    "--submit-orders",
    "--paper-order",
    "--paper-orders",
    "--live-order",
    "--live-orders",
    "--controlled-submit",
    "--enable-controlled-submit",
    "--ppo-rf",
    "--ppo-random-forest",
    "--ppo-xgboost",
    "--xgboost",
    "--promote-model",
    "--model-promotion",
)


@dataclass(frozen=True)
class ValidationOnlyPreflightRequest:
    """Request for v3.07 validation-only R1-R6 preflight evidence."""

    run_id: str
    config_path: str
    output_root: str
    validation_only: bool
    no_submit: bool
    command: tuple[str, ...] = ()
    dataset_reader: Callable[[Path], Any] | None = None
    allow_sealed_training_command_execution: bool = False
    allow_ppo_v2_training_execution: bool = False
    allow_training_command_execution: bool = False
    allow_model_learn: bool = False
    allow_model_fitting: bool = False
    allow_data_fetching: bool = False
    allow_dataset_generation: bool = False
    allow_model_artifact_creation: bool = False
    allow_quarantine_model_output_creation: bool = False
    allow_paper_orders: bool = False
    allow_live_orders: bool = False
    allow_controlled_submit: bool = False
    allow_ppo_rf: bool = False
    allow_ppo_xgboost: bool = False
    allow_model_promotion: bool = False
    allow_production_deployment: bool = False
    allow_trading_edge_claims: bool = False
    allow_profitability_claims: bool = False


@dataclass(frozen=True)
class ValidationOnlyPreflightResult:
    """Result from v3.07 validation-only R1-R6 preflight evidence."""

    result: str
    evidence: Mapping[str, Any]
    errors: tuple[str, ...]
    created_files: tuple[str, ...]
    metadata: Mapping[str, Any]


def execute_validation_only_preflight(
    request: ValidationOnlyPreflightRequest,
) -> ValidationOnlyPreflightResult:
    """Execute validation-only R1-R6 checks and write validation-scoped evidence."""

    request_errors = _validate_request(request)
    if request_errors:
        return _reject(request_errors)

    timestamp = _utc_timestamp()
    command = request.command or _default_command(request)

    config_path = Path(request.config_path)
    output_root = Path(request.output_root)

    config, config_errors = _load_config(config_path)
    if config is None:
        config = {}

    dataset_path = _resolve_dataset_path(config)
    features = tuple(_get_nested_list(config, ("features",)))
    universe = tuple(_get_nested_list(config, ("universe",)))
    temporal_split = _get_nested_mapping(config, ("temporal_split",))
    no_submit_config = _get_nested(config, ("training_parameters", "no_submit"))

    evidence: dict[str, Any] = {}

    r6 = _build_r6_runtime_git_state()
    evidence["R6"] = r6

    dataset_frame: Any | None = None
    r2_errors: list[str] = list(config_errors)

    r2_identity = _build_r2_dataset_identity(dataset_path)
    r2_errors.extend(r2_identity.get("errors", ()))

    if not r2_errors:
        dataset_frame, read_errors = _read_dataset(dataset_path, request.dataset_reader)
        r2_errors.extend(read_errors)

    evidence["R2"] = _with_status(r2_identity, r2_errors)

    if dataset_frame is None:
        dependency_error = "sealed dataset unavailable; dependent validation not executed"
        evidence["R3"] = _fail_evidence(dependency_error)
        evidence["R4"] = _fail_evidence(dependency_error)
        evidence["R5"] = _fail_evidence(dependency_error)
    else:
        evidence["R3"] = _validate_r3_data_contract_coverage(
            dataset_frame=dataset_frame,
            expected_features=features,
            expected_universe=universe,
        )
        evidence["R4"] = _validate_r4_temporal_split_embargo_holdout(
            dataset_frame=dataset_frame,
            temporal_split=temporal_split,
        )
        evidence["R5"] = _validate_r5_training_input_handoff(
            dataset_frame=dataset_frame,
            expected_features=features,
            no_submit_config=no_submit_config,
        )

    evidence["R1"] = _build_r1_preflight_result(
        evidence=evidence,
        command=command,
        timestamp=timestamp,
    )

    overall_result = _overall_result(evidence)
    evidence["summary"] = {
        "result": overall_result,
        "run_id": request.run_id,
        "timestamp_utc": timestamp,
        "validation_only_preflight": "AUTHORIZED_FOR_R1_R6_EVIDENCE_ONLY",
        "sealed_training_command_execution": "NOT_AUTHORIZED",
        "ppo_v2_training_execution": "NOT_AUTHORIZED",
        "training_command_execution": "NOT_AUTHORIZED",
        "model_learn": "NOT_AUTHORIZED",
        "model_fitting": "NOT_AUTHORIZED",
        "data_fetching": "NOT_AUTHORIZED",
        "dataset_generation": "NOT_AUTHORIZED",
        "model_artifact_creation": "NOT_AUTHORIZED",
        "quarantine_model_output_creation": "NOT_AUTHORIZED",
        "paper_orders": "NOT_AUTHORIZED",
        "live_orders": "NOT_AUTHORIZED",
        "controlled_submit": "BLOCKED",
        "ppo_rf": "BLOCKED",
        "ppo_xgboost": "BLOCKED",
        "model_promotion": "NOT_AUTHORIZED",
        "trading_edge_claims": "NOT_AUTHORIZED",
        "profitability_claims": "NOT_AUTHORIZED",
    }

    created_files, write_errors = _write_validation_evidence(output_root, evidence)
    if write_errors:
        evidence["write_errors"] = tuple(write_errors)
        overall_result = FAIL_RESULT

    return ValidationOnlyPreflightResult(
        result=overall_result,
        evidence=evidence,
        errors=tuple(write_errors),
        created_files=tuple(str(path) for path in created_files),
        metadata={
            "scope": "validation_only_preflight_r1_r6",
            "execution_performed": True,
            "training_performed": False,
            "sealed_training_command_executed": False,
            "model_learn_called": False,
            "model_fitting_performed": False,
            "data_fetching_performed": False,
            "dataset_generation_performed": False,
            "model_artifact_creation_performed": False,
            "quarantine_model_output_creation_performed": False,
            "paper_orders_submitted": False,
            "live_orders_submitted": False,
        },
    )


def build_argument_parser() -> argparse.ArgumentParser:
    """Build parser for the validation-only preflight CLI."""

    parser = argparse.ArgumentParser(
        prog="../.venv/bin/python -m src.ppo_v2_validation_only_preflight_execution",
        allow_abbrev=False,
        description="Run v3.07 validation-only preflight for R1-R6 evidence.",
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--validation-only", action="store_true", default=False)
    parser.add_argument("--no-submit", action="store_true", default=False)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for validation-only R1-R6 evidence execution."""

    raw_args = tuple(sys.argv[1:] if argv is None else argv)
    blocked_flags = _collect_blocked_flags(raw_args)
    if blocked_flags:
        return 2

    parser = build_argument_parser()
    namespace, unknown_args = parser.parse_known_args(list(raw_args))
    if unknown_args:
        return 2

    request = ValidationOnlyPreflightRequest(
        run_id=namespace.run_id,
        config_path=namespace.config,
        output_root=namespace.output_root,
        validation_only=namespace.validation_only,
        no_submit=namespace.no_submit,
        command=tuple(raw_args),
    )

    result = execute_validation_only_preflight(request)
    if result.result == PASS_RESULT:
        return 0
    if result.result in {FAIL_RESULT, PARTIAL_FAIL_RESULT}:
        return 1
    return 2


def _validate_request(request: ValidationOnlyPreflightRequest) -> tuple[str, ...]:
    errors: list[str] = []

    if not isinstance(request, ValidationOnlyPreflightRequest):
        return ("request must be a ValidationOnlyPreflightRequest",)

    if request.run_id != V3_07_VALIDATION_RUN_ID:
        errors.append("run_id must match v3.07 validation-only preflight run id")

    if request.config_path != V3_07_CONFIG_PATH:
        errors.append("config path must match v3.07 sealed config path")

    if request.validation_only is not True:
        errors.append("--validation-only is required")

    if request.no_submit is not True:
        errors.append("--no-submit is required")

    errors.extend(_validate_output_root(request.output_root))
    errors.extend(_validate_authorization_flags(request))
    return tuple(errors)


def _validate_output_root(output_root: str) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(output_root, str) or not output_root.strip():
        return ("output_root must be a non-empty string",)

    posix_path = PurePosixPath(output_root)
    parts = {part.lower() for part in posix_path.parts}

    if posix_path.is_absolute():
        errors.append("output_root must be relative")

    if ".." in posix_path.parts:
        errors.append("output_root must not contain path traversal")

    if "quarantine" in parts:
        errors.append("output_root must not use quarantine paths")

    if "models" in parts or "model_artifacts" in parts:
        errors.append("output_root must not use model artifact paths")

    return tuple(errors)


def _validate_authorization_flags(
    request: ValidationOnlyPreflightRequest,
) -> tuple[str, ...]:
    blocked_flags = {
        "allow_sealed_training_command_execution": (
            request.allow_sealed_training_command_execution
        ),
        "allow_ppo_v2_training_execution": request.allow_ppo_v2_training_execution,
        "allow_training_command_execution": request.allow_training_command_execution,
        "allow_model_learn": request.allow_model_learn,
        "allow_model_fitting": request.allow_model_fitting,
        "allow_data_fetching": request.allow_data_fetching,
        "allow_dataset_generation": request.allow_dataset_generation,
        "allow_model_artifact_creation": request.allow_model_artifact_creation,
        "allow_quarantine_model_output_creation": (
            request.allow_quarantine_model_output_creation
        ),
        "allow_paper_orders": request.allow_paper_orders,
        "allow_live_orders": request.allow_live_orders,
        "allow_controlled_submit": request.allow_controlled_submit,
        "allow_ppo_rf": request.allow_ppo_rf,
        "allow_ppo_xgboost": request.allow_ppo_xgboost,
        "allow_model_promotion": request.allow_model_promotion,
        "allow_production_deployment": request.allow_production_deployment,
        "allow_trading_edge_claims": request.allow_trading_edge_claims,
        "allow_profitability_claims": request.allow_profitability_claims,
    }

    return tuple(
        f"{name} must remain false"
        for name, value in blocked_flags.items()
        if value is not False
    )


def _collect_blocked_flags(raw_args: Sequence[str]) -> tuple[str, ...]:
    blocked = set(BLOCKED_CLI_FLAGS)
    return tuple(arg for arg in raw_args if arg in blocked)


def _load_config(path: Path) -> tuple[Mapping[str, Any] | None, tuple[str, ...]]:
    if not path.is_file():
        return None, (f"config file missing: {path}",)

    text = path.read_text(encoding="utf-8")
    try:
        if text.lstrip().startswith("{"):
            data = json.loads(text)
        else:
            import yaml  # type: ignore

            data = yaml.safe_load(text)
    except Exception as exc:  # pragma: no cover - exact parser errors vary
        return None, (f"config parse failed: {exc}",)

    if not isinstance(data, Mapping):
        return None, ("config root must be a mapping",)

    return data, ()


def _resolve_dataset_path(config: Mapping[str, Any]) -> Path:
    value = _get_nested(config, ("io_boundary", "local_input_dataset"))
    if isinstance(value, str) and value.strip():
        return Path(value)
    return Path(V3_07_DEFAULT_SEALED_DATASET_PATH)


def _build_r2_dataset_identity(dataset_path: Path) -> Mapping[str, Any]:
    evidence: dict[str, Any] = {
        "dataset_path": str(dataset_path),
        "exists": dataset_path.is_file(),
        "extension": dataset_path.suffix,
        "size_bytes": None,
        "sha256": None,
        "errors": (),
    }

    errors: list[str] = []

    if dataset_path.suffix != ".parquet":
        errors.append("sealed dataset must have .parquet extension")

    if not dataset_path.is_file():
        errors.append(f"sealed dataset missing: {dataset_path}")
        return {**evidence, "errors": tuple(errors)}

    size_bytes = dataset_path.stat().st_size
    evidence["size_bytes"] = size_bytes

    if size_bytes <= 0:
        errors.append("sealed dataset is empty")

    sha256, checksum_error = _sha256_file(dataset_path)
    evidence["sha256"] = sha256
    if checksum_error:
        errors.append(checksum_error)

    return {**evidence, "errors": tuple(errors)}


def _read_dataset(
    dataset_path: Path,
    dataset_reader: Callable[[Path], Any] | None,
) -> tuple[Any | None, tuple[str, ...]]:
    try:
        if dataset_reader is not None:
            return dataset_reader(dataset_path), ()

        import pandas as pd

        return pd.read_parquet(dataset_path), ()
    except Exception as exc:  # pragma: no cover - exact reader errors vary
        return None, (f"sealed dataset read failed: {exc}",)


def _validate_r3_data_contract_coverage(
    dataset_frame: Any,
    expected_features: tuple[str, ...],
    expected_universe: tuple[str, ...],
) -> Mapping[str, Any]:
    columns = _columns(dataset_frame)
    errors: list[str] = []

    required_columns = tuple(
        dict.fromkeys((*REQUIRED_METADATA_COLUMNS, *REQUIRED_OHLCV_COLUMNS, *expected_features))
    )
    missing_columns = tuple(column for column in required_columns if column not in columns)
    if missing_columns:
        errors.append("missing required columns: " + ", ".join(missing_columns))

    missing_ohlcv = tuple(column for column in REQUIRED_OHLCV_COLUMNS if column not in columns)
    if missing_ohlcv:
        errors.append("missing OHLCV columns: " + ", ".join(missing_ohlcv))

    duplicate_count = _duplicate_symbol_datetime_count(dataset_frame)
    if duplicate_count > 0:
        errors.append(f"duplicate Symbol/Datetime rows found: {duplicate_count}")

    universe_errors = _validate_universe(dataset_frame, expected_universe)
    errors.extend(universe_errors)

    coverage_summary, coverage_errors = _observed_coverage_summary(dataset_frame)
    errors.extend(coverage_errors)

    return {
        "status": PASS_RESULT if not errors else FAIL_RESULT,
        "required_columns": required_columns,
        "missing_columns": missing_columns,
        "expected_universe": expected_universe,
        "duplicate_symbol_datetime_count": duplicate_count,
        "coverage_scope": "observed_symbol_date_intraday_sessions",
        "coverage_summary": coverage_summary,
        "errors": tuple(errors),
    }


def _validate_r4_temporal_split_embargo_holdout(
    dataset_frame: Any,
    temporal_split: Mapping[str, Any],
) -> Mapping[str, Any]:
    errors: list[str] = []
    required_keys = (
        "train_start",
        "train_end",
        "train_eval_embargo_start",
        "train_eval_embargo_end",
        "eval_start",
        "eval_end",
        "eval_holdout_embargo_start",
        "eval_holdout_embargo_end",
        "holdout_start",
        "holdout_end",
        "holdout_policy",
    )

    missing_keys = tuple(key for key in required_keys if key not in temporal_split)
    if missing_keys:
        errors.append("missing temporal split keys: " + ", ".join(missing_keys))

    if temporal_split.get("holdout_policy") != "final_validation_only":
        errors.append("holdout_policy must be final_validation_only")

    timestamps: dict[str, Any] = {}
    if not missing_keys:
        try:
            import pandas as pd

            timestamps = {
                key: pd.Timestamp(str(temporal_split[key]))
                for key in required_keys
                if key != "holdout_policy"
            }
        except Exception as exc:  # pragma: no cover - exact parser errors vary
            errors.append(f"temporal split timestamp parse failed: {exc}")

    if timestamps:
        ordered_pairs = (
            ("train_start", "train_end"),
            ("train_end", "train_eval_embargo_start"),
            ("train_eval_embargo_start", "train_eval_embargo_end"),
            ("train_eval_embargo_end", "eval_start"),
            ("eval_start", "eval_end"),
            ("eval_end", "eval_holdout_embargo_start"),
            ("eval_holdout_embargo_start", "eval_holdout_embargo_end"),
            ("eval_holdout_embargo_end", "holdout_start"),
            ("holdout_start", "holdout_end"),
        )
        for left, right in ordered_pairs:
            if timestamps[left] >= timestamps[right]:
                errors.append(f"temporal boundary violation: {left} >= {right}")

        split_counts, split_errors = _split_row_counts(dataset_frame, timestamps)
        errors.extend(split_errors)
    else:
        split_counts = {}

    return {
        "status": PASS_RESULT if not errors else FAIL_RESULT,
        "temporal_split_keys_present": tuple(key for key in required_keys if key in temporal_split),
        "missing_temporal_split_keys": missing_keys,
        "holdout_policy": temporal_split.get("holdout_policy"),
        "split_row_counts": split_counts,
        "errors": tuple(errors),
    }


def _validate_r5_training_input_handoff(
    dataset_frame: Any,
    expected_features: tuple[str, ...],
    no_submit_config: Any,
) -> Mapping[str, Any]:
    columns = _columns(dataset_frame)
    errors: list[str] = []

    if no_submit_config is not True:
        errors.append("training_parameters.no_submit must be true")

    missing_features = tuple(feature for feature in expected_features if feature not in columns)
    if missing_features:
        errors.append("missing feature columns: " + ", ".join(missing_features))

    forbidden_present = tuple(
        feature for feature in expected_features if feature in FORBIDDEN_FEATURE_INPUT_COLUMNS
    )
    if forbidden_present:
        errors.append(
            "forbidden feature input columns present: " + ", ".join(forbidden_present)
        )

    metadata_missing = tuple(column for column in REQUIRED_METADATA_COLUMNS if column not in columns)
    if metadata_missing:
        errors.append("missing metadata columns: " + ", ".join(metadata_missing))

    return {
        "status": PASS_RESULT if not errors else FAIL_RESULT,
        "expected_features": expected_features,
        "missing_features": missing_features,
        "forbidden_feature_input_columns": FORBIDDEN_FEATURE_INPUT_COLUMNS,
        "forbidden_feature_input_columns_present": forbidden_present,
        "metadata_columns": REQUIRED_METADATA_COLUMNS,
        "metadata_columns_used_as_features": tuple(
            column for column in REQUIRED_METADATA_COLUMNS if column in expected_features
        ),
        "training_execution_performed": False,
        "model_fitting_performed": False,
        "errors": tuple(errors),
    }


def _build_r6_runtime_git_state() -> Mapping[str, Any]:
    package_names = ("pandas", "numpy", "pyarrow", "PyYAML", "pytest")
    packages = {
        name: _safe_package_version(name)
        for name in package_names
    }

    git_state = {
        "branch": _run_git(("branch", "--show-current")),
        "commit": _run_git(("rev-parse", "HEAD")),
        "status_short": _run_git(("status", "--short")),
    }
    git_state["working_tree_clean"] = git_state["status_short"] == ""

    return {
        "status": PASS_RESULT,
        "python_version": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
        "packages": packages,
        "git_state": git_state,
        "secrets_captured": False,
        "credentials_captured": False,
        "errors": (),
    }


def _build_r1_preflight_result(
    evidence: Mapping[str, Any],
    command: tuple[str, ...],
    timestamp: str,
) -> Mapping[str, Any]:
    statuses = {
        key: value.get("status")
        for key, value in evidence.items()
        if key in {"R2", "R3", "R4", "R5", "R6"} and isinstance(value, Mapping)
    }

    return {
        "status": PASS_RESULT,
        "validation_only_preflight_completed": True,
        "overall_preflight_result": _overall_result(evidence),
        "r2_to_r6_statuses": statuses,
        "command": command,
        "timestamp_utc": timestamp,
        "training_performed": False,
        "sealed_training_command_executed": False,
        "model_learn_called": False,
        "model_fitting_performed": False,
        "data_fetching_performed": False,
        "dataset_generation_performed": False,
        "model_artifact_creation_performed": False,
        "quarantine_model_output_creation_performed": False,
        "paper_orders_submitted": False,
        "live_orders_submitted": False,
        "controlled_submit_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
        "trading_edge_claims_made": False,
        "profitability_claims_made": False,
        "errors": (),
    }


def _write_validation_evidence(
    output_root: Path,
    evidence: Mapping[str, Any],
) -> tuple[tuple[Path, ...], tuple[str, ...]]:
    created: list[Path] = []
    errors: list[str] = []

    try:
        output_root.mkdir(parents=True, exist_ok=True)

        for key, file_name in EVIDENCE_FILE_NAMES.items():
            path = output_root / file_name
            _write_json(path, evidence[key])
            created.append(path)

        inventory_path = output_root / "validation_inventory.json"
        inventory = {
            "scope": "validation_only_preflight_r1_r6",
            "files": tuple(str(path) for path in created),
            "model_artifact_files_created": (),
            "quarantine_model_output_files_created": (),
        }
        _write_json(inventory_path, inventory)
        created.append(inventory_path)

        checksum_path = output_root / "validation_checksums.sha256"
        checksum_lines = []
        for path in created:
            digest, error = _sha256_file(path)
            if error:
                errors.append(error)
            else:
                checksum_lines.append(f"{digest}  {path.as_posix()}")
        checksum_path.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
        created.append(checksum_path)

    except Exception as exc:  # pragma: no cover - exact filesystem errors vary
        errors.append(f"validation evidence write failed: {exc}")

    return tuple(created), tuple(errors)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _json_ready(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _with_status(evidence: Mapping[str, Any], errors: Sequence[str]) -> Mapping[str, Any]:
    clean = {key: value for key, value in evidence.items() if key != "errors"}
    return {
        **clean,
        "status": PASS_RESULT if not errors else FAIL_RESULT,
        "errors": tuple(errors),
    }


def _fail_evidence(reason: str) -> Mapping[str, Any]:
    return {
        "status": FAIL_RESULT,
        "errors": (reason,),
    }


def _overall_result(evidence: Mapping[str, Any]) -> str:
    statuses = [
        value.get("status")
        for key, value in evidence.items()
        if key in {"R1", "R2", "R3", "R4", "R5", "R6"} and isinstance(value, Mapping)
    ]

    if statuses and all(status == PASS_RESULT for status in statuses):
        return PASS_RESULT

    if any(status == PASS_RESULT for status in statuses):
        return PARTIAL_FAIL_RESULT

    return FAIL_RESULT


def _reject(errors: Sequence[str]) -> ValidationOnlyPreflightResult:
    return ValidationOnlyPreflightResult(
        result=REJECTED_FAIL_CLOSED_RESULT,
        evidence={},
        errors=tuple(errors),
        created_files=(),
        metadata={
            "scope": "validation_only_preflight_r1_r6",
            "execution_performed": False,
            "training_performed": False,
            "sealed_training_command_executed": False,
        },
    )


def _columns(dataset_frame: Any) -> tuple[str, ...]:
    columns = getattr(dataset_frame, "columns", ())
    return tuple(str(column) for column in columns)


def _duplicate_symbol_datetime_count(dataset_frame: Any) -> int:
    columns = _columns(dataset_frame)
    if not all(column in columns for column in REQUIRED_METADATA_COLUMNS):
        return 0

    duplicates = dataset_frame.duplicated(subset=list(REQUIRED_METADATA_COLUMNS))
    return int(duplicates.sum())


def _validate_universe(dataset_frame: Any, expected_universe: tuple[str, ...]) -> tuple[str, ...]:
    if not expected_universe:
        return ("expected universe is missing from config",)

    columns = _columns(dataset_frame)
    if "Symbol" not in columns:
        return ("Symbol column missing; universe validation cannot run",)

    observed = set(str(value) for value in dataset_frame["Symbol"].dropna().unique())
    expected = set(expected_universe)

    errors: list[str] = []
    missing_symbols = tuple(sorted(expected - observed))
    unexpected_symbols = tuple(sorted(observed - expected))

    if missing_symbols:
        errors.append("missing expected symbols: " + ", ".join(missing_symbols))
    if unexpected_symbols:
        errors.append("unexpected symbols found: " + ", ".join(unexpected_symbols))

    return tuple(errors)


def _observed_coverage_summary(dataset_frame: Any) -> tuple[Mapping[str, Any], tuple[str, ...]]:
    columns = _columns(dataset_frame)
    if not all(column in columns for column in REQUIRED_METADATA_COLUMNS):
        return {}, ("Symbol/Datetime required for observed coverage validation",)

    try:
        import pandas as pd

        frame = dataset_frame.copy()
        frame["Datetime"] = pd.to_datetime(frame["Datetime"], utc=True, errors="coerce")
        if frame["Datetime"].isna().any():
            return {}, ("Datetime contains null or unparsable values",)

        frame["_date"] = frame["Datetime"].dt.date.astype(str)
        grouped = frame.groupby(["Symbol", "_date"]).size().reset_index(name="rows")
        zero_row_sessions = int((grouped["rows"] <= 0).sum())
        summary = {
            "symbol_date_session_count": int(len(grouped)),
            "min_rows_per_observed_symbol_date": int(grouped["rows"].min()),
            "max_rows_per_observed_symbol_date": int(grouped["rows"].max()),
            "zero_row_observed_sessions": zero_row_sessions,
        }
        errors = ()
        if zero_row_sessions:
            errors = ("observed symbol/date session has zero rows",)
        return summary, errors
    except Exception as exc:  # pragma: no cover - exact pandas errors vary
        return {}, (f"observed coverage validation failed: {exc}",)


def _split_row_counts(dataset_frame: Any, timestamps: Mapping[str, Any]) -> tuple[Mapping[str, int], tuple[str, ...]]:
    columns = _columns(dataset_frame)
    if "Datetime" not in columns:
        return {}, ("Datetime column missing; temporal split validation cannot run",)

    try:
        import pandas as pd

        frame = dataset_frame.copy()
        frame["Datetime"] = pd.to_datetime(frame["Datetime"], utc=True, errors="coerce")
        if frame["Datetime"].isna().any():
            return {}, ("Datetime contains null or unparsable values",)

        counts = {
            "train": int(
                (
                    (frame["Datetime"] >= timestamps["train_start"])
                    & (frame["Datetime"] <= timestamps["train_end"])
                ).sum()
            ),
            "eval": int(
                (
                    (frame["Datetime"] >= timestamps["eval_start"])
                    & (frame["Datetime"] <= timestamps["eval_end"])
                ).sum()
            ),
            "holdout": int(
                (
                    (frame["Datetime"] >= timestamps["holdout_start"])
                    & (frame["Datetime"] <= timestamps["holdout_end"])
                ).sum()
            ),
        }

        errors = tuple(
            f"{split_name} split contains zero rows"
            for split_name, row_count in counts.items()
            if row_count <= 0
        )
        return counts, errors
    except Exception as exc:  # pragma: no cover - exact pandas errors vary
        return {}, (f"temporal split validation failed: {exc}",)


def _get_nested(config: Mapping[str, Any], keys: Sequence[str]) -> Any:
    current: Any = config
    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    return current


def _get_nested_mapping(config: Mapping[str, Any], keys: Sequence[str]) -> Mapping[str, Any]:
    value = _get_nested(config, keys)
    return value if isinstance(value, Mapping) else {}


def _get_nested_list(config: Mapping[str, Any], keys: Sequence[str]) -> tuple[str, ...]:
    value = _get_nested(config, keys)
    if not isinstance(value, Sequence) or isinstance(value, str):
        return ()
    return tuple(str(item) for item in value)


def _sha256_file(path: Path) -> tuple[str | None, str | None]:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest(), None
    except Exception as exc:  # pragma: no cover - exact filesystem errors vary
        return None, f"sha256 failed for {path}: {exc}"


def _safe_package_version(package_name: str) -> str | None:
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return None


def _run_git(args: Sequence[str]) -> str | None:
    try:
        completed = subprocess.run(
            ("git", *args),
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None

    if completed.returncode != 0:
        return None

    return completed.stdout.strip()


def _default_command(request: ValidationOnlyPreflightRequest) -> tuple[str, ...]:
    return (
        "../.venv/bin/python",
        "-m",
        "src.ppo_v2_validation_only_preflight_execution",
        "--run-id",
        request.run_id,
        "--config",
        request.config_path,
        "--output-root",
        request.output_root,
        "--validation-only",
        "--no-submit",
    )


def _utc_timestamp() -> str:
    return datetime.now(UTC).isoformat()


__all__ = [
    "BLOCKED_CLI_FLAGS",
    "FAIL_RESULT",
    "PARTIAL_FAIL_RESULT",
    "PASS_RESULT",
    "REJECTED_FAIL_CLOSED_RESULT",
    "V3_07_CONFIG_PATH",
    "V3_07_DEFAULT_OUTPUT_ROOT",
    "V3_07_DEFAULT_SEALED_DATASET_PATH",
    "V3_07_VALIDATION_RUN_ID",
    "ValidationOnlyPreflightRequest",
    "ValidationOnlyPreflightResult",
    "build_argument_parser",
    "execute_validation_only_preflight",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
