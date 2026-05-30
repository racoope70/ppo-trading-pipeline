"""Final holdout validation for standalone Alpaca PPO candidates.

v1.8.5 scope:
- Load v1.8.4 smoke/full retraining results.
- Select top-N validation candidates per ticker.
- Define a later untouched holdout slice after all candidate-selection eval windows.
- Validate candidate artifacts exist.
- Optionally load PPO + VecNormalize artifacts and evaluate on holdout.
- Write holdout summaries and pass/fail flags.

This module does not train PPO.
This module does not tune thresholds.
This module does not submit orders.
This module does not update paper-trading manifests.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.alpaca_ppo_retraining_config import (
    AlpacaPPORetrainingConfig,
    load_config_json,
    validate_config,
)
from src.alpaca_ppo_retraining_runner import (
    filter_dataset_for_config,
    load_model_ready_dataset,
    summarize_training_dataset,
)


REQUIRED_TRAINING_RESULT_COLUMNS = [
    "Ticker",
    "Window",
    "EvalEnd",
    "Sharpe",
    "Drawdown_%",
    "PPO_Portfolio",
    "BuyHold",
    "Winner",
]


@dataclass(frozen=True)
class HoldoutThresholds:
    min_holdout_rows: int = 60
    min_sharpe: float = -1.0
    max_drawdown_pct: float = 5.0
    min_final_portfolio: float = 95_000.0


def utc_timestamp_for_path() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def read_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return p


def resolve_run_dir(
    *,
    config: AlpacaPPORetrainingConfig,
    run_dir: str | Path | None = None,
) -> Path:
    """Resolve a v1.8.4 retraining run directory."""
    if run_dir is not None:
        p = Path(run_dir)
        if not p.exists():
            raise FileNotFoundError(f"Run directory not found: {p}")
        return p

    results_root = Path(config.results_dir)
    if not results_root.exists():
        raise FileNotFoundError(f"Results directory not found: {results_root}")

    candidates = [
        path
        for path in results_root.iterdir()
        if path.is_dir() and (path / "training_results.json").exists()
    ]

    if not candidates:
        raise FileNotFoundError(
            f"No retraining run directories with training_results.json found under {results_root}"
        )

    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_training_results(path: str | Path) -> pd.DataFrame:
    """Load training results JSON into a dataframe."""
    payload = read_json(path)
    results = payload.get("results", [])

    if not results:
        raise ValueError(f"No training results found in {path}")

    df = pd.DataFrame(results)

    missing = [col for col in REQUIRED_TRAINING_RESULT_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Training results missing required columns: {missing}")

    df["Ticker"] = df["Ticker"].astype(str).str.upper()
    df["EvalEnd"] = pd.to_datetime(df["EvalEnd"], utc=True)
    df["Sharpe"] = pd.to_numeric(df["Sharpe"], errors="coerce")
    df["Drawdown_%"] = pd.to_numeric(df["Drawdown_%"], errors="coerce")
    df["PPO_Portfolio"] = pd.to_numeric(df["PPO_Portfolio"], errors="coerce")
    df["BuyHold"] = pd.to_numeric(df["BuyHold"], errors="coerce")

    if df["Sharpe"].isna().any():
        raise ValueError("Training results contain non-numeric Sharpe values.")

    return df.sort_values(["Ticker", "EvalEnd"]).reset_index(drop=True)


def compute_global_holdout_start(training_results: pd.DataFrame) -> pd.Timestamp:
    """Holdout begins after the latest eval end used during candidate selection."""
    if training_results.empty:
        raise ValueError("Cannot compute holdout start from empty training results.")

    return pd.to_datetime(training_results["EvalEnd"], utc=True).max()


def parse_window_index(window_text: str, *, step_size: int) -> int:
    """Derive 1-based walk-forward window index from 'start-end' text."""
    start_text = str(window_text).split("-", maxsplit=1)[0].strip()

    try:
        start_idx = int(start_text)
    except ValueError as exc:
        raise ValueError(f"Could not parse window start from: {window_text}") from exc

    if step_size <= 0:
        raise ValueError("step_size must be positive.")

    if start_idx % step_size != 0:
        raise ValueError(
            f"Window start {start_idx} is not divisible by step_size {step_size}."
        )

    return int(start_idx // step_size) + 1


def candidate_prefix(row: pd.Series | dict[str, Any], *, step_size: int) -> str:
    """Build artifact prefix for a selected candidate row."""
    ticker = str(row["Ticker"]).upper()
    window_idx = parse_window_index(str(row["Window"]), step_size=step_size)
    return f"ppo_{ticker}_window{window_idx}"


def select_top_candidates_per_symbol(
    training_results: pd.DataFrame,
    *,
    top_n_per_symbol: int,
    step_size: int,
) -> list[dict[str, Any]]:
    """Select top-N candidates per ticker by validation Sharpe."""
    if top_n_per_symbol <= 0:
        raise ValueError("top_n_per_symbol must be positive.")

    selected: list[dict[str, Any]] = []

    for ticker, group in training_results.groupby("Ticker", sort=True):
        ranked = group.sort_values("Sharpe", ascending=False).head(top_n_per_symbol)

        for rank, (_, row) in enumerate(ranked.iterrows(), start=1):
            item = row.to_dict()
            item["CandidateRankWithinTicker"] = rank
            item["Prefix"] = candidate_prefix(row, step_size=step_size)
            item["ValidationSharpe"] = float(row["Sharpe"])
            item["ValidationDrawdown_%"] = float(row["Drawdown_%"])
            selected.append(item)

    return selected


def slice_holdout_dataset(
    dataset: pd.DataFrame,
    *,
    ticker: str,
    holdout_start: pd.Timestamp,
) -> pd.DataFrame:
    """Return holdout rows for a ticker strictly after holdout_start."""
    data = dataset.copy()
    data["Datetime"] = pd.to_datetime(data["Datetime"], utc=True)
    data["Symbol"] = data["Symbol"].astype(str).str.upper()

    ticker = str(ticker).upper()

    holdout = data[
        (data["Symbol"] == ticker)
        & (data["Datetime"] > pd.to_datetime(holdout_start, utc=True))
    ].copy()

    return holdout.sort_values("Datetime").reset_index(drop=True)


def resolve_artifact_paths(
    *,
    prefix: str,
    artifacts_dir: str | Path,
) -> dict[str, Path]:
    """Resolve expected candidate artifact paths."""
    root = Path(artifacts_dir)

    return {
        "model_path": root / f"{prefix}_model.zip",
        "vecnorm_path": root / f"{prefix}_vecnorm.pkl",
        "features_path": root / f"{prefix}_features.json",
        "model_info_path": root / f"{prefix}_model_info.json",
        "probability_config_path": root / f"{prefix}_probability_config.json",
    }


def artifact_existence_summary(paths: dict[str, Path]) -> dict[str, Any]:
    """Summarize artifact existence.

    Model and VecNormalize files are required for holdout evaluation.
    Metadata files are useful but not required because train.py saves them only
    for selected top-window export artifacts.
    """
    required_keys = ["model_path", "vecnorm_path"]

    required_missing = [
        str(paths[key])
        for key in required_keys
        if not paths[key].exists()
    ]

    return {
        "required_artifacts_exist": not required_missing,
        "required_missing": required_missing,
        "paths": {key: str(value) for key, value in paths.items()},
        "exists": {key: value.exists() for key, value in paths.items()},
    }


def pass_fail_from_metrics(
    *,
    metrics: dict[str, Any],
    holdout_rows: int,
    thresholds: HoldoutThresholds,
) -> tuple[bool, list[str]]:
    """Apply simple non-tuned holdout pass/fail checks."""
    reasons: list[str] = []

    if holdout_rows < thresholds.min_holdout_rows:
        reasons.append(
            f"holdout_rows {holdout_rows} < min_holdout_rows {thresholds.min_holdout_rows}"
        )

    sharpe = float(metrics.get("Sharpe", 0.0))
    drawdown = float(metrics.get("Drawdown_%", 0.0))
    final_portfolio = float(metrics.get("PPO_Portfolio", 0.0))

    if sharpe < thresholds.min_sharpe:
        reasons.append(f"Sharpe {sharpe} < min_sharpe {thresholds.min_sharpe}")

    if drawdown > thresholds.max_drawdown_pct:
        reasons.append(
            f"Drawdown_% {drawdown} > max_drawdown_pct {thresholds.max_drawdown_pct}"
        )

    if final_portfolio < thresholds.min_final_portfolio:
        reasons.append(
            f"PPO_Portfolio {final_portfolio} < min_final_portfolio "
            f"{thresholds.min_final_portfolio}"
        )

    return not reasons, reasons


def make_holdout_env_from_vecnorm(
    *,
    holdout_df: pd.DataFrame,
    vecnorm_path: str | Path,
):
    """Create a holdout VecNormalize environment using saved train stats."""
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

    from src.config import ENABLE_SENTIMENT, ENABLE_SLO
    from src.env import ContinuousPositionEnv
    from src.feature_manifest import build_env_feature_frame

    env_df = build_env_feature_frame(holdout_df)

    if len(env_df) <= 60:
        raise ValueError(f"Holdout dataframe too small for evaluation: {len(env_df)} rows.")

    frame_bound = (50, len(env_df) - 3)

    base_env = DummyVecEnv(
        [
            lambda: ContinuousPositionEnv(
                df=env_df,
                frame_bound=frame_bound,
                window_size=10,
                cost_rate=(0.0002 if ENABLE_SLO else 0.0),
                slip_rate=(0.0003 if ENABLE_SLO else 0.0),
                k_alpha=0.20,
                k_mom=0.05,
                k_sent=(0.01 if ENABLE_SENTIMENT else 0.0),
                mom_source="denoised",
                mom_lookback=20,
                min_trade_delta=0.01,
                cooldown=5,
                reward_clip=1.0,
            )
        ]
    )

    env = VecNormalize.load(str(vecnorm_path), base_env)
    env.training = False
    env.norm_reward = False

    return env


def evaluate_candidate_on_holdout(
    *,
    candidate: dict[str, Any],
    holdout_df: pd.DataFrame,
    artifacts_dir: str | Path,
    output_dir: str | Path,
    thresholds: HoldoutThresholds,
) -> dict[str, Any]:
    """Evaluate one selected PPO candidate on holdout data."""
    from stable_baselines3 import PPO

    from src.train import evaluate_model_on_window

    prefix = str(candidate["Prefix"])
    paths = resolve_artifact_paths(prefix=prefix, artifacts_dir=artifacts_dir)
    artifact_summary = artifact_existence_summary(paths)

    if not artifact_summary["required_artifacts_exist"]:
        return {
            "Ticker": candidate["Ticker"],
            "Prefix": prefix,
            "HoldoutRows": int(len(holdout_df)),
            "Evaluated": False,
            "PassedHoldout": False,
            "FailureReasons": artifact_summary["required_missing"],
            "ArtifactSummary": artifact_summary,
        }

    env = None

    try:
        env = make_holdout_env_from_vecnorm(
            holdout_df=holdout_df,
            vecnorm_path=paths["vecnorm_path"],
        )
        model = PPO.load(str(paths["model_path"]), env=env)

        metrics, predictions_df, compat_df = evaluate_model_on_window(
            model=model,
            env=env,
            df_window=holdout_df,
        )

        output_root = Path(output_dir)
        output_root.mkdir(parents=True, exist_ok=True)

        predictions_path = output_root / f"{prefix}_holdout_predictions.csv"
        compat_path = output_root / f"{prefix}_holdout_predictions_compat.csv"

        predictions_df.to_csv(predictions_path, index=False)
        compat_df.to_csv(compat_path, index=False)

        passed, reasons = pass_fail_from_metrics(
            metrics=metrics,
            holdout_rows=len(holdout_df),
            thresholds=thresholds,
        )

        return {
            "Ticker": candidate["Ticker"],
            "Prefix": prefix,
            "ValidationSharpe": candidate["ValidationSharpe"],
            "ValidationDrawdown_%": candidate["ValidationDrawdown_%"],
            "HoldoutRows": int(len(holdout_df)),
            "HoldoutStart": str(holdout_df["Datetime"].min()),
            "HoldoutEnd": str(holdout_df["Datetime"].max()),
            "Evaluated": True,
            "PassedHoldout": bool(passed),
            "FailureReasons": reasons,
            "ArtifactSummary": artifact_summary,
            "PredictionsPath": str(predictions_path),
            "CompatPredictionsPath": str(compat_path),
            **metrics,
        }

    finally:
        try:
            if env is not None:
                env.close()
        except Exception:
            pass


def build_dry_run_candidate_summary(
    *,
    candidate: dict[str, Any],
    holdout_df: pd.DataFrame,
    artifacts_dir: str | Path,
    thresholds: HoldoutThresholds,
) -> dict[str, Any]:
    """Build candidate summary without loading PPO artifacts."""
    prefix = str(candidate["Prefix"])
    paths = resolve_artifact_paths(prefix=prefix, artifacts_dir=artifacts_dir)
    artifact_summary = artifact_existence_summary(paths)

    reasons = []

    if len(holdout_df) < thresholds.min_holdout_rows:
        reasons.append(
            f"holdout_rows {len(holdout_df)} < min_holdout_rows {thresholds.min_holdout_rows}"
        )

    if not artifact_summary["required_artifacts_exist"]:
        reasons.extend(artifact_summary["required_missing"])

    return {
        "Ticker": candidate["Ticker"],
        "Prefix": prefix,
        "CandidateRankWithinTicker": candidate["CandidateRankWithinTicker"],
        "ValidationSharpe": candidate["ValidationSharpe"],
        "ValidationDrawdown_%": candidate["ValidationDrawdown_%"],
        "ValidationWindow": candidate["Window"],
        "ValidationEvalEnd": str(candidate["EvalEnd"]),
        "HoldoutRows": int(len(holdout_df)),
        "HoldoutStart": str(holdout_df["Datetime"].min()) if not holdout_df.empty else None,
        "HoldoutEnd": str(holdout_df["Datetime"].max()) if not holdout_df.empty else None,
        "Evaluated": False,
        "PassedDryRunChecks": not reasons,
        "FailureReasons": reasons,
        "ArtifactSummary": artifact_summary,
    }


def run_holdout_validation(
    *,
    config_path: str | Path = "config/alpaca_ppo_retraining_config.json",
    run_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    evaluate: bool = False,
    top_n_per_symbol: int | None = None,
    thresholds: HoldoutThresholds = HoldoutThresholds(),
) -> dict[str, Any]:
    """Run holdout validation workflow."""
    config = load_config_json(config_path)
    validate_config(config, check_dataset_exists=True)

    resolved_run_dir = resolve_run_dir(config=config, run_dir=run_dir)
    training_results_path = resolved_run_dir / "training_results.json"

    training_results = load_training_results(training_results_path)
    holdout_start = compute_global_holdout_start(training_results)

    dataset = load_model_ready_dataset(config.dataset_path)
    dataset = filter_dataset_for_config(dataset, config)
    dataset_summary = summarize_training_dataset(dataset)

    n_per_symbol = top_n_per_symbol or config.top_n_windows

    candidates = select_top_candidates_per_symbol(
        training_results,
        top_n_per_symbol=n_per_symbol,
        step_size=config.walkforward_step_size,
    )

    actual_output_dir = (
        Path(output_dir)
        if output_dir is not None
        else resolved_run_dir / "holdout_validation"
    )
    actual_output_dir.mkdir(parents=True, exist_ok=True)

    candidate_results: list[dict[str, Any]] = []

    for candidate in candidates:
        holdout_df = slice_holdout_dataset(
            dataset,
            ticker=candidate["Ticker"],
            holdout_start=holdout_start,
        )

        if evaluate:
            result = evaluate_candidate_on_holdout(
                candidate=candidate,
                holdout_df=holdout_df,
                artifacts_dir=config.artifacts_dir,
                output_dir=actual_output_dir,
                thresholds=thresholds,
            )
        else:
            result = build_dry_run_candidate_summary(
                candidate=candidate,
                holdout_df=holdout_df,
                artifacts_dir=config.artifacts_dir,
                thresholds=thresholds,
            )

        candidate_results.append(result)

    evaluated_count = sum(1 for row in candidate_results if row.get("Evaluated"))
    pass_count = sum(1 for row in candidate_results if row.get("PassedHoldout"))
    dry_run_pass_count = sum(1 for row in candidate_results if row.get("PassedDryRunChecks"))

    summary = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "milestone": "v1.8.5",
        "mode": "evaluate" if evaluate else "dry_run",
        "config_path": str(config_path),
        "run_dir": str(resolved_run_dir),
        "training_results_path": str(training_results_path),
        "output_dir": str(actual_output_dir),
        "dataset_rows": dataset_summary["rows"],
        "symbols": dataset_summary["symbols"],
        "safe_feature_count": dataset_summary["safe_feature_count"],
        "candidate_count": len(candidate_results),
        "evaluated_count": evaluated_count,
        "pass_count": pass_count,
        "dry_run_pass_count": dry_run_pass_count,
        "holdout_start_after_global_eval_end": holdout_start.isoformat(),
        "top_n_per_symbol": n_per_symbol,
        "thresholds": {
            "min_holdout_rows": thresholds.min_holdout_rows,
            "min_sharpe": thresholds.min_sharpe,
            "max_drawdown_pct": thresholds.max_drawdown_pct,
            "min_final_portfolio": thresholds.min_final_portfolio,
        },
        "candidate_results": candidate_results,
        "notes": [
            "Holdout starts strictly after the latest EvalEnd used during candidate selection.",
            "Holdout validation does not train models.",
            "Holdout validation does not tune thresholds.",
            "Candidates are not approved for paper trading unless holdout validation passes.",
        ],
    }

    write_json(actual_output_dir / "holdout_validation_summary.json", summary)

    rows_path = actual_output_dir / "holdout_candidate_results.csv"
    pd.DataFrame(candidate_results).to_csv(rows_path, index=False)

    summary["candidate_results_csv"] = str(rows_path)

    write_json(actual_output_dir / "final_summary.json", summary)

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run final holdout validation for Alpaca PPO candidates."
    )
    parser.add_argument(
        "--config-path",
        default="config/alpaca_ppo_retraining_config.json",
    )
    parser.add_argument(
        "--run-dir",
        default=None,
        help="Retraining run directory. Defaults to latest run with training_results.json.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional holdout output directory.",
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Actually load PPO/VecNormalize artifacts and evaluate holdout.",
    )
    parser.add_argument("--top-n-per-symbol", type=int, default=None)
    parser.add_argument("--min-holdout-rows", type=int, default=60)
    parser.add_argument("--min-sharpe", type=float, default=-1.0)
    parser.add_argument("--max-drawdown-pct", type=float, default=5.0)
    parser.add_argument("--min-final-portfolio", type=float, default=95_000.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    thresholds = HoldoutThresholds(
        min_holdout_rows=args.min_holdout_rows,
        min_sharpe=args.min_sharpe,
        max_drawdown_pct=args.max_drawdown_pct,
        min_final_portfolio=args.min_final_portfolio,
    )

    summary = run_holdout_validation(
        config_path=args.config_path,
        run_dir=args.run_dir,
        output_dir=args.output_dir,
        evaluate=args.evaluate,
        top_n_per_symbol=args.top_n_per_symbol,
        thresholds=thresholds,
    )

    print("=" * 80)
    print("v1.8.5 FINAL HOLDOUT VALIDATION / UNTOUCHED TEST PERIOD")
    print("=" * 80)
    print(f"mode: {summary['mode']}")
    print(f"run_dir: {summary['run_dir']}")
    print(f"output_dir: {summary['output_dir']}")
    print(f"dataset_rows: {summary['dataset_rows']}")
    print(f"symbols: {summary['symbols']}")
    print(f"candidate_count: {summary['candidate_count']}")
    print(f"evaluated_count: {summary['evaluated_count']}")
    print(f"pass_count: {summary['pass_count']}")
    print(f"dry_run_pass_count: {summary['dry_run_pass_count']}")
    print(f"holdout_start_after_global_eval_end: {summary['holdout_start_after_global_eval_end']}")


if __name__ == "__main__":
    main()
