"""Standalone Alpaca PPO retraining configuration.

v1.8.2 scope:
- Define a centralized, auditable configuration object for the upcoming
  standalone Alpaca PPO retraining pipeline.
- Validate paths, symbols, split settings, embargo settings, holdout settings,
  and output directories.
- Write/load a JSON config file.

This module does not train PPO.
This module does not submit orders.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


CONFIG_VERSION = "v1.8.2"
DEFAULT_SYMBOLS = ("AAPL", "AMD", "MRK", "PFE", "UNH", "XOM")


@dataclass(frozen=True)
class AlpacaPPORetrainingConfig:
    """Configuration for standalone Alpaca PPO retraining."""

    config_version: str = CONFIG_VERSION
    run_name: str = "standalone_alpaca_ppo_v1_8"
    data_source: str = "alpaca_historical_1h"
    timeframe: str = "1H"

    dataset_path: str = "data/alpaca_training/model_ready/alpaca_ppo_training_dataset.csv"
    dataset_provenance_path: str = (
        "data/alpaca_training/model_ready/alpaca_ppo_training_dataset_provenance.json"
    )

    artifacts_dir: str = "models/alpaca_ppo_models_master"
    results_dir: str = "reports/alpaca_ppo_retraining"

    symbols: tuple[str, ...] = DEFAULT_SYMBOLS

    train_fraction: float = 0.80
    embargo_rows: int = 5
    min_train_rows: int = 60
    min_eval_rows: int = 60

    holdout_fraction: float = 0.20
    holdout_min_rows_per_symbol: int = 60

    top_n_windows: int = 3

    walkforward_window_size: int = 720
    walkforward_step_size: int = 120

    smoke_test_timesteps: int = 2_000
    training_timesteps: int = 100_000

    random_seed: int = 42
    test_mode: bool = True

    notes: tuple[str, ...] = (
        "v1.8.2 configuration only.",
        "No PPO training performed in this checkpoint.",
        "Final holdout validation is required before paper-trading redeployment.",
        "Generated datasets and model artifacts should not be committed to Git.",
    )


def normalize_symbols(symbols: Iterable[str] | str) -> tuple[str, ...]:
    """Normalize symbol input into an uppercase, de-duplicated tuple."""
    if isinstance(symbols, str):
        raw = symbols.replace(",", " ").split()
    else:
        raw = []
        for value in symbols:
            raw.extend(str(value).replace(",", " ").split())

    normalized = [item.strip().upper() for item in raw if item.strip()]
    unique = tuple(dict.fromkeys(normalized))

    if not unique:
        raise ValueError("At least one symbol is required.")

    return unique


def config_to_dict(config: AlpacaPPORetrainingConfig) -> dict[str, Any]:
    """Convert config dataclass to JSON-friendly dictionary."""
    payload = asdict(config)
    payload["symbols"] = list(config.symbols)
    payload["notes"] = list(config.notes)
    payload["generated_utc"] = datetime.now(timezone.utc).isoformat()
    return payload


def config_from_dict(payload: dict[str, Any]) -> AlpacaPPORetrainingConfig:
    """Create config from a dictionary, ignoring unknown keys."""
    allowed = {field.name for field in fields(AlpacaPPORetrainingConfig)}
    filtered = {key: value for key, value in payload.items() if key in allowed}

    if "symbols" in filtered:
        filtered["symbols"] = normalize_symbols(filtered["symbols"])

    if "notes" in filtered:
        filtered["notes"] = tuple(filtered["notes"])

    return AlpacaPPORetrainingConfig(**filtered)


def validate_config(
    config: AlpacaPPORetrainingConfig,
    *,
    check_dataset_exists: bool = False,
) -> dict[str, Any]:
    """Validate retraining configuration and return a summary."""
    symbols = normalize_symbols(config.symbols)

    if len(symbols) != len(set(symbols)):
        raise ValueError("Duplicate symbols are not allowed.")

    invalid_symbols = [
        symbol
        for symbol in symbols
        if not symbol.replace(".", "").replace("-", "").isalnum()
    ]
    if invalid_symbols:
        raise ValueError(f"Invalid symbols found: {invalid_symbols}")

    if not 0 < config.train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1.")

    if not 0 < config.holdout_fraction < 1:
        raise ValueError("holdout_fraction must be between 0 and 1.")

    if config.embargo_rows < 0:
        raise ValueError("embargo_rows must be non-negative.")

    positive_int_fields = {
        "min_train_rows": config.min_train_rows,
        "min_eval_rows": config.min_eval_rows,
        "holdout_min_rows_per_symbol": config.holdout_min_rows_per_symbol,
        "top_n_windows": config.top_n_windows,
        "walkforward_window_size": config.walkforward_window_size,
        "walkforward_step_size": config.walkforward_step_size,
        "smoke_test_timesteps": config.smoke_test_timesteps,
        "training_timesteps": config.training_timesteps,
    }

    for name, value in positive_int_fields.items():
        if int(value) <= 0:
            raise ValueError(f"{name} must be positive.")

    if config.walkforward_step_size > config.walkforward_window_size:
        raise ValueError("walkforward_step_size cannot exceed walkforward_window_size.")

    dataset_path = Path(config.dataset_path)
    dataset_provenance_path = Path(config.dataset_provenance_path)

    if check_dataset_exists and not dataset_path.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {dataset_path}")

    if check_dataset_exists and not dataset_provenance_path.exists():
        raise FileNotFoundError(
            f"Dataset provenance path does not exist: {dataset_provenance_path}"
        )

    return {
        "passed": True,
        "config_version": config.config_version,
        "run_name": config.run_name,
        "data_source": config.data_source,
        "timeframe": config.timeframe,
        "symbols": list(symbols),
        "dataset_path": str(dataset_path),
        "dataset_exists": dataset_path.exists(),
        "dataset_provenance_path": str(dataset_provenance_path),
        "dataset_provenance_exists": dataset_provenance_path.exists(),
        "artifacts_dir": str(Path(config.artifacts_dir)),
        "results_dir": str(Path(config.results_dir)),
        "train_fraction": config.train_fraction,
        "embargo_rows": config.embargo_rows,
        "holdout_fraction": config.holdout_fraction,
        "top_n_windows": config.top_n_windows,
        "walkforward_window_size": config.walkforward_window_size,
        "walkforward_step_size": config.walkforward_step_size,
        "smoke_test_timesteps": config.smoke_test_timesteps,
        "training_timesteps": config.training_timesteps,
        "test_mode": config.test_mode,
    }


def ensure_output_dirs(config: AlpacaPPORetrainingConfig) -> list[Path]:
    """Create artifact/results directories for retraining outputs."""
    paths = [
        Path(config.artifacts_dir),
        Path(config.results_dir),
    ]

    for path in paths:
        path.mkdir(parents=True, exist_ok=True)

    return paths


def write_config_json(
    config: AlpacaPPORetrainingConfig,
    output_path: str | Path,
) -> Path:
    """Write retraining config JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config_to_dict(config), indent=2), encoding="utf-8")
    return path


def load_config_json(path: str | Path) -> AlpacaPPORetrainingConfig:
    """Load retraining config JSON."""
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")

    payload = json.loads(p.read_text(encoding="utf-8"))
    return config_from_dict(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create/validate standalone Alpaca PPO retraining config."
    )
    parser.add_argument(
        "--output-config",
        default="config/alpaca_ppo_retraining_config.json",
    )
    parser.add_argument(
        "--dataset-path",
        default="data/alpaca_training/model_ready/alpaca_ppo_training_dataset.csv",
    )
    parser.add_argument(
        "--dataset-provenance-path",
        default=(
            "data/alpaca_training/model_ready/"
            "alpaca_ppo_training_dataset_provenance.json"
        ),
    )
    parser.add_argument(
        "--artifacts-dir",
        default="models/alpaca_ppo_models_master",
    )
    parser.add_argument(
        "--results-dir",
        default="reports/alpaca_ppo_retraining",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=list(DEFAULT_SYMBOLS),
    )
    parser.add_argument("--train-fraction", type=float, default=0.80)
    parser.add_argument("--embargo-rows", type=int, default=5)
    parser.add_argument("--holdout-fraction", type=float, default=0.20)
    parser.add_argument("--top-n-windows", type=int, default=3)
    parser.add_argument("--walkforward-window-size", type=int, default=720)
    parser.add_argument("--walkforward-step-size", type=int, default=120)
    parser.add_argument("--smoke-test-timesteps", type=int, default=2_000)
    parser.add_argument("--training-timesteps", type=int, default=100_000)
    parser.add_argument(
        "--require-dataset",
        action="store_true",
        help="Require dataset/provenance files to exist during validation.",
    )
    parser.add_argument(
        "--create-dirs",
        action="store_true",
        help="Create configured artifact/results directories.",
    )
    parser.add_argument(
        "--full-mode",
        action="store_true",
        help="Set test_mode=False in the generated config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = AlpacaPPORetrainingConfig(
        dataset_path=args.dataset_path,
        dataset_provenance_path=args.dataset_provenance_path,
        artifacts_dir=args.artifacts_dir,
        results_dir=args.results_dir,
        symbols=normalize_symbols(args.symbols),
        train_fraction=args.train_fraction,
        embargo_rows=args.embargo_rows,
        holdout_fraction=args.holdout_fraction,
        top_n_windows=args.top_n_windows,
        walkforward_window_size=args.walkforward_window_size,
        walkforward_step_size=args.walkforward_step_size,
        smoke_test_timesteps=args.smoke_test_timesteps,
        training_timesteps=args.training_timesteps,
        test_mode=not args.full_mode,
    )

    validation = validate_config(
        config,
        check_dataset_exists=args.require_dataset,
    )

    if args.create_dirs:
        ensure_output_dirs(config)

    config_path = write_config_json(config, args.output_config)

    print("=" * 80)
    print("v1.8.2 STANDALONE ALPACA PPO RETRAINING CONFIGURATION")
    print("=" * 80)
    print(f"config_path: {config_path}")
    print(f"validation_passed: {validation['passed']}")
    print(f"symbols: {validation['symbols']}")
    print(f"dataset_path: {validation['dataset_path']}")
    print(f"dataset_exists: {validation['dataset_exists']}")
    print(f"artifacts_dir: {validation['artifacts_dir']}")
    print(f"results_dir: {validation['results_dir']}")
    print(f"train_fraction: {validation['train_fraction']}")
    print(f"embargo_rows: {validation['embargo_rows']}")
    print(f"holdout_fraction: {validation['holdout_fraction']}")
    print(f"top_n_windows: {validation['top_n_windows']}")
    print(f"test_mode: {validation['test_mode']}")


if __name__ == "__main__":
    main()