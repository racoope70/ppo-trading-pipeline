"""Build a paper-trading execution plan from dry-run target outputs.

This script reads the broker-connected dry-run outputs and converts model target
weights into buy/sell/hold rebalance intents.

It does NOT connect to Alpaca.
It does NOT submit orders.

Input:
- dry_run_targets.csv
- dry_run_summary.json

Output:
- execution_plan.csv
- execution_plan_summary.json
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from src.paper_trading.execution import (
    ExecutionConfig,
    build_rebalance_intents_from_targets,
    summarize_intents,
)


DEFAULT_RUN_DIR = Path("reports/paper_trading_dry_runs/latest")


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return bool(default)
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return float(default)


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return int(default)


def load_dotenv_if_available(env_path: str | Path) -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return

    path = Path(env_path)
    if path.exists():
        load_dotenv(path, override=True)
    else:
        load_dotenv(override=True)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")

    return payload


def build_execution_config(args: argparse.Namespace) -> ExecutionConfig:
    return ExecutionConfig(
        min_notional=float(
            args.min_notional
            if args.min_notional is not None
            else _env_float("REBALANCE_MIN_NOTIONAL", 25.0)
        ),
        max_abs_weight=float(
            args.max_abs_weight
            if args.max_abs_weight is not None
            else _env_float("WEIGHT_CAP", 0.40)
        ),
        allow_shorts=bool(
            args.allow_shorts
            if args.allow_shorts
            else _env_bool("ALLOW_SHORTS", False)
        ),
        use_fractionals=bool(
            args.use_fractionals
            if args.use_fractionals
            else _env_bool("USE_FRACTIONALS", True)
        ),
        qty_precision=int(
            args.qty_precision
            if args.qty_precision is not None
            else _env_int("QTY_PRECISION", 6)
        ),
        dry_run=True,
    )


def load_dry_run_outputs(run_dir: str | Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    root = Path(run_dir)
    targets_path = root / "dry_run_targets.csv"
    summary_path = root / "dry_run_summary.json"

    if not targets_path.exists():
        raise FileNotFoundError(f"Missing dry-run targets file: {targets_path}")

    if not summary_path.exists():
        raise FileNotFoundError(f"Missing dry-run summary file: {summary_path}")

    targets = pd.read_csv(targets_path)
    summary = read_json(summary_path)

    if targets.empty:
        raise ValueError(f"Dry-run targets file is empty: {targets_path}")

    return targets, summary


def validate_dry_run_is_safe(targets: pd.DataFrame, summary: dict[str, Any]) -> None:
    """Fail fast if dry-run outputs are not safe to convert into an execution plan."""
    if int(summary.get("orders_submitted", -1)) != 0:
        raise ValueError(f"Dry-run summary indicates orders were submitted: {summary.get('orders_submitted')}")

    if int(summary.get("error_count", -1)) != 0:
        raise ValueError(f"Dry-run summary indicates errors: {summary.get('error_count')}")

    required_columns = [
        "symbol",
        "target_weight",
        "actual_qty",
        "actual_market_value",
        "latest_price",
        "equity",
        "order_submitted",
        "note",
    ]

    missing = [col for col in required_columns if col not in targets.columns]
    if missing:
        raise ValueError(f"Dry-run targets missing required columns: {missing}")

    if not (pd.to_numeric(targets["order_submitted"], errors="coerce").fillna(0) == 0).all():
        raise ValueError("Dry-run targets contain row-level order_submitted != 0")

    notes = targets["note"].astype(str)
    if notes.str.contains("dry_run_error", case=False, na=False).any():
        raise ValueError("Dry-run targets contain dry_run_error rows")

    if not (notes == "dry_run_predict_ok").all():
        raise ValueError(f"Dry-run targets contain non-ok notes: {sorted(notes.unique())}")


def build_execution_plan(
    run_dir: str | Path = DEFAULT_RUN_DIR,
    output_dir: str | Path | None = None,
    config: ExecutionConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build execution-plan dataframe and summary from dry-run output files."""
    root = Path(run_dir)
    out_root = Path(output_dir) if output_dir is not None else root

    targets, dry_run_summary = load_dry_run_outputs(root)
    validate_dry_run_is_safe(targets, dry_run_summary)

    exec_config = config or ExecutionConfig(dry_run=True)

    plan = build_rebalance_intents_from_targets(
        targets,
        config=exec_config,
    )

    # Preserve useful model/debug columns from dry-run output.
    passthrough_cols = [
        "selected_prefix",
        "raw_action",
        "confidence",
        "latest_bar_time",
        "note",
    ]

    merge_cols = ["symbol"] + [col for col in passthrough_cols if col in targets.columns]
    plan = plan.merge(
        targets[merge_cols],
        on="symbol",
        how="left",
    )

    plan["order_submitted"] = False
    plan["execution_note"] = plan["reason"].where(
        ~plan["should_order"].astype(bool),
        "execution_plan_only_no_order_submitted",
    )

    intent_summary = summarize_intents(plan)

    summary = {
        "source_run_dir": str(root),
        "output_dir": str(out_root),
        "orders_submitted": 0,
        "dry_run_summary": dry_run_summary,
        "execution_config": {
            "min_notional": exec_config.min_notional,
            "max_abs_weight": exec_config.max_abs_weight,
            "allow_shorts": exec_config.allow_shorts,
            "use_fractionals": exec_config.use_fractionals,
            "qty_precision": exec_config.qty_precision,
            "dry_run": exec_config.dry_run,
        },
        "execution_plan": intent_summary,
    }

    return plan, summary


def write_execution_plan(
    plan: pd.DataFrame,
    summary: dict[str, Any],
    output_dir: str | Path,
) -> tuple[Path, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    plan_path = root / "execution_plan.csv"
    summary_path = root / "execution_plan_summary.json"

    plan.to_csv(plan_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    return plan_path, summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build paper-trading execution plan from dry-run targets."
    )
    parser.add_argument(
        "--run-dir",
        default=str(DEFAULT_RUN_DIR),
        help="Dry-run output directory containing dry_run_targets.csv and dry_run_summary.json.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Execution-plan output directory. Default: same as --run-dir.",
    )
    parser.add_argument(
        "--env",
        default=".env",
        help="Optional .env path for execution sizing settings.",
    )
    parser.add_argument(
        "--min-notional",
        type=float,
        default=None,
        help="Minimum rebalance notional. Default: REBALANCE_MIN_NOTIONAL env var or 25.",
    )
    parser.add_argument(
        "--max-abs-weight",
        type=float,
        default=None,
        help="Maximum absolute target weight. Default: WEIGHT_CAP env var or 0.40.",
    )
    parser.add_argument(
        "--allow-shorts",
        action="store_true",
        help="Allow negative target weights in the execution plan.",
    )
    parser.add_argument(
        "--use-fractionals",
        action="store_true",
        help="Use fractional share quantities. Default: USE_FRACTIONALS env var or true.",
    )
    parser.add_argument(
        "--qty-precision",
        type=int,
        default=None,
        help="Fractional quantity precision. Default: QTY_PRECISION env var or 6.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_dotenv_if_available(args.env)

    config = build_execution_config(args)
    output_dir = Path(args.output_dir) if args.output_dir else Path(args.run_dir)

    print("=" * 80)
    print("PAPER-TRADING EXECUTION PLAN")
    print("=" * 80)
    print(f"Run dir: {args.run_dir}")
    print(f"Output dir: {output_dir}")
    print("Orders submitted: 0")
    print()

    plan, summary = build_execution_plan(
        run_dir=args.run_dir,
        output_dir=output_dir,
        config=config,
    )

    plan_path, summary_path = write_execution_plan(plan, summary, output_dir)

    display_cols = [
        "symbol",
        "side",
        "qty",
        "price",
        "target_weight",
        "actual_weight",
        "delta_notional",
        "should_order",
        "reason",
        "execution_note",
    ]

    print(plan[display_cols].to_string(index=False))
    print()
    print("Execution-plan summary:")
    for key, value in summary["execution_plan"].items():
        print(f"{key}: {value}")

    print()
    print(f"Saved execution plan: {plan_path}")
    print(f"Saved execution summary: {summary_path}")
    print()
    print("Execution plan complete. No orders were submitted.")


if __name__ == "__main__":
    main()
