"""Standalone Alpaca PPO retraining runner.

v1.8.3 scope:
- Load v1.8.2 Alpaca PPO retraining config.
- Load v1.8.1 Alpaca model-ready dataset.
- Validate dataset/config compatibility.
- Create a run directory and write run metadata.
- Provide a dry-run mode for CI and safety.
- Provide a smoke-training integration path using existing train.py functions.

This module does not submit orders.
This module does not update paper-trading manifests.
This module does not perform final holdout validation.
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.alpaca_ppo_retraining_config import (
    AlpacaPPORetrainingConfig,
    load_config_json,
    validate_config,
)
from src.feature_manifest import build_safe_feature_columns


REQUIRED_DATASET_COLUMNS = [
    "Datetime",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Target",
    "Return",
    "Symbol",
]


def utc_timestamp_for_path() -> str:
    """Return filesystem-safe UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def load_model_ready_dataset(path: str | Path) -> pd.DataFrame:
    """Load model-ready Alpaca PPO dataset."""
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"Model-ready dataset not found: {p}")

    df = pd.read_csv(p)

    missing = [col for col in REQUIRED_DATASET_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Model-ready dataset missing required columns: {missing}")

    df["Datetime"] = pd.to_datetime(df["Datetime"], utc=True)
    df["Symbol"] = df["Symbol"].astype(str).str.upper()

    return df.sort_values(["Symbol", "Datetime"]).reset_index(drop=True)


def filter_dataset_for_config(
    df: pd.DataFrame,
    config: AlpacaPPORetrainingConfig,
) -> pd.DataFrame:
    """Filter model-ready dataset to configured symbol universe."""
    wanted = set(symbol.upper() for symbol in config.symbols)
    data = df[df["Symbol"].isin(wanted)].copy()

    if data.empty:
        raise ValueError("No rows remain after filtering dataset to configured symbols.")

    found = set(data["Symbol"].unique().tolist())
    missing_symbols = sorted(wanted - found)

    if missing_symbols:
        raise ValueError(f"Dataset missing configured symbols: {missing_symbols}")

    return data.sort_values(["Symbol", "Datetime"]).reset_index(drop=True)


def summarize_training_dataset(df: pd.DataFrame) -> dict[str, Any]:
    """Summarize model-ready training dataset."""
    if df.empty:
        raise ValueError("Cannot summarize empty dataset.")

    safe_features = build_safe_feature_columns(df)

    forbidden = {"Target", "Return", "Datetime", "Symbol"}
    leaked = sorted(forbidden.intersection(safe_features))
    if leaked:
        raise ValueError(f"Unsafe columns found in safe feature list: {leaked}")

    per_symbol_rows = {
        str(k): int(v)
        for k, v in df["Symbol"].value_counts().sort_index().to_dict().items()
    }

    target_counts = {
        str(k): int(v)
        for k, v in df["Target"].value_counts().sort_index().to_dict().items()
    }

    return {
        "rows": int(len(df)),
        "symbols": sorted(df["Symbol"].unique().tolist()),
        "per_symbol_rows": per_symbol_rows,
        "min_datetime_utc": df["Datetime"].min().isoformat(),
        "max_datetime_utc": df["Datetime"].max().isoformat(),
        "target_counts": target_counts,
        "safe_feature_count": int(len(safe_features)),
        "safe_features": safe_features,
    }


def create_retraining_run_dir(
    config: AlpacaPPORetrainingConfig,
    *,
    run_id: str | None = None,
) -> Path:
    """Create a timestamped retraining run directory."""
    actual_run_id = run_id or f"{config.run_name}_{utc_timestamp_for_path()}"
    run_dir = Path(config.results_dir) / actual_run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    """Write JSON payload."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return p


def write_run_metadata(
    *,
    run_dir: Path,
    config: AlpacaPPORetrainingConfig,
    config_validation: dict[str, Any],
    dataset_summary: dict[str, Any],
    dry_run: bool,
    smoke: bool,
) -> dict[str, Path]:
    """Write run metadata files."""
    config_snapshot = asdict(config)
    config_snapshot["symbols"] = list(config.symbols)
    config_snapshot["notes"] = list(config.notes)
    config_snapshot["created_utc"] = datetime.now(timezone.utc).isoformat()

    run_summary = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "milestone": "v1.8.3",
        "run_name": config.run_name,
        "dry_run": bool(dry_run),
        "smoke": bool(smoke),
        "status": "DRY_RUN_COMPLETE" if dry_run else "TRAINING_REQUESTED",
        "config_version": config.config_version,
        "dataset_rows": dataset_summary["rows"],
        "symbols": dataset_summary["symbols"],
        "safe_feature_count": dataset_summary["safe_feature_count"],
        "train_fraction": config.train_fraction,
        "embargo_rows": config.embargo_rows,
        "holdout_fraction": config.holdout_fraction,
        "top_n_windows": config.top_n_windows,
        "artifacts_dir": config.artifacts_dir,
        "results_dir": config.results_dir,
        "note": (
            "Dry-run mode validates config/dataset/run metadata only."
            if dry_run
            else "Training mode delegates to existing PPO training integration."
        ),
    }

    return {
        "config_snapshot": write_json(run_dir / "retraining_config_snapshot.json", config_snapshot),
        "config_validation": write_json(run_dir / "config_validation.json", config_validation),
        "dataset_summary": write_json(run_dir / "dataset_summary.json", dataset_summary),
        "run_summary": write_json(run_dir / "run_summary.json", run_summary),
    }


def copy_dataset_snapshot(
    *,
    df: pd.DataFrame,
    run_dir: Path,
    filename: str = "alpaca_model_ready_dataset_snapshot.csv",
) -> Path:
    """Write a dataset snapshot into the run directory."""
    path = run_dir / filename
    df.to_csv(path, index=False)
    return path


def call_existing_training_loop(
    *,
    df: pd.DataFrame,
    config: AlpacaPPORetrainingConfig,
    smoke: bool,
) -> list[dict[str, Any]]:
    """Delegate to existing train.py training loop.

    This wrapper intentionally imports src.train lazily so dry-run tests do not
    need to initialize the PPO training stack.

    v1.8.3 integration keeps full training guarded behind --train.
    """
    import src.train as train_module

    timesteps = config.smoke_test_timesteps if smoke else config.training_timesteps

    if hasattr(train_module, "run_parallel_training"):
        return train_module.run_parallel_training(
            df,
            symbols=list(config.symbols),
            timesteps=timesteps,
            max_workers=1 if smoke else None,
            force_retrain=True,
            embargo_rows=config.embargo_rows,
        )

    if hasattr(train_module, "train_all_tickers"):
        return train_module.train_all_tickers(
            df,
            symbols=list(config.symbols),
            timesteps=timesteps,
            force_retrain=True,
            embargo_rows=config.embargo_rows,
        )

    raise AttributeError(
        "Could not find a supported training entry point in src.train. "
        "Expected run_parallel_training(...) or train_all_tickers(...)."
    )


def run_retraining_integration(
    *,
    config_path: str | Path = "config/alpaca_ppo_retraining_config.json",
    dry_run: bool = True,
    smoke: bool = True,
    create_dataset_snapshot: bool = True,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Run v1.8.3 integration workflow."""
    config = load_config_json(config_path)

    config_validation = validate_config(
        config,
        check_dataset_exists=True,
    )

    dataset = load_model_ready_dataset(config.dataset_path)
    dataset = filter_dataset_for_config(dataset, config)
    dataset_summary = summarize_training_dataset(dataset)

    run_dir = create_retraining_run_dir(config, run_id=run_id)

    metadata_paths = write_run_metadata(
        run_dir=run_dir,
        config=config,
        config_validation=config_validation,
        dataset_summary=dataset_summary,
        dry_run=dry_run,
        smoke=smoke,
    )

    dataset_snapshot_path = None
    if create_dataset_snapshot:
        dataset_snapshot_path = copy_dataset_snapshot(df=dataset, run_dir=run_dir)

    training_results: list[dict[str, Any]] = []
    training_status = "SKIPPED_DRY_RUN"

    if not dry_run:
        training_results = call_existing_training_loop(
            df=dataset,
            config=config,
            smoke=smoke,
        )
        training_status = "TRAINING_COMPLETE"

        write_json(
            run_dir / "training_results.json",
            {
                "training_status": training_status,
                "result_count": len(training_results),
                "results": training_results,
            },
        )

    final_summary = {
        "passed": True,
        "milestone": "v1.8.3",
        "run_dir": str(run_dir),
        "dry_run": bool(dry_run),
        "smoke": bool(smoke),
        "training_status": training_status,
        "dataset_rows": dataset_summary["rows"],
        "symbols": dataset_summary["symbols"],
        "safe_feature_count": dataset_summary["safe_feature_count"],
        "metadata_paths": {key: str(value) for key, value in metadata_paths.items()},
        "dataset_snapshot_path": str(dataset_snapshot_path) if dataset_snapshot_path else None,
    }

    write_json(run_dir / "final_summary.json", final_summary)

    return final_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run standalone Alpaca PPO retraining integration."
    )
    parser.add_argument(
        "--config-path",
        default="config/alpaca_ppo_retraining_config.json",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Actually invoke PPO training. Default is dry-run only.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Use full training timesteps instead of smoke-test timesteps.",
    )
    parser.add_argument(
        "--no-dataset-snapshot",
        action="store_true",
        help="Do not write dataset snapshot into run directory.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional deterministic run directory name for tests/smoke runs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    summary = run_retraining_integration(
        config_path=args.config_path,
        dry_run=not args.train,
        smoke=not args.full,
        create_dataset_snapshot=not args.no_dataset_snapshot,
        run_id=args.run_id,
    )

    print("=" * 80)
    print("v1.8.3 STANDALONE ALPACA PPO TRAINING LOOP INTEGRATION")
    print("=" * 80)
    print(f"passed: {summary['passed']}")
    print(f"run_dir: {summary['run_dir']}")
    print(f"dry_run: {summary['dry_run']}")
    print(f"smoke: {summary['smoke']}")
    print(f"training_status: {summary['training_status']}")
    print(f"dataset_rows: {summary['dataset_rows']}")
    print(f"symbols: {summary['symbols']}")
    print(f"safe_feature_count: {summary['safe_feature_count']}")


if __name__ == "__main__":
    main()