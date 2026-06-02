"""Single-order execution-plan filter for Alpaca paper trading.

v1.13 scope:
- Read an existing paper-trading execution_plan.csv.
- Select exactly one reviewed order row by symbol and optional side.
- Keep all rows for audit visibility.
- Disable every non-selected order row.
- Write a filtered execution_plan.csv and execution_plan_summary.json.
- Copy dry-run inputs needed by downstream checklist tools.

This module does not connect to Alpaca.
This module does not submit orders.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_RUN_DIR = Path("reports/paper_trading_dry_runs/latest")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Missing JSON file: {p}")

    payload = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {p}")

    return payload


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return p


def bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})


def load_execution_plan(run_dir: str | Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    root = Path(run_dir)
    plan_path = root / "execution_plan.csv"
    summary_path = root / "execution_plan_summary.json"

    if not plan_path.exists():
        raise FileNotFoundError(f"Missing execution plan: {plan_path}")
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing execution-plan summary: {summary_path}")

    plan = pd.read_csv(plan_path)
    summary = read_json(summary_path)

    if plan.empty:
        raise ValueError(f"Execution plan is empty: {plan_path}")

    return plan, summary


def validate_plan(plan: pd.DataFrame, summary: dict[str, Any]) -> None:
    required_columns = [
        "symbol",
        "side",
        "qty",
        "price",
        "equity",
        "target_weight",
        "actual_weight",
        "target_notional",
        "actual_notional",
        "delta_notional",
        "should_order",
        "reason",
        "dry_run",
        "order_submitted",
        "execution_note",
    ]

    missing = [col for col in required_columns if col not in plan.columns]
    if missing:
        raise ValueError(f"Execution plan missing required columns: {missing}")

    if int(summary.get("orders_submitted", -1)) != 0:
        raise ValueError(
            f"Execution-plan summary already has orders_submitted={summary.get('orders_submitted')}"
        )

    if "execution_plan" not in summary:
        raise ValueError("Execution-plan summary missing execution_plan section.")

    prior_submitted = bool_series(plan["order_submitted"])
    if prior_submitted.any():
        raise ValueError("Execution plan already contains submitted order rows.")

    order_rows = plan[bool_series(plan["should_order"])]
    if order_rows.empty:
        raise ValueError("Execution plan has no eligible order rows to filter.")


def summarize_filtered_plan(plan: pd.DataFrame) -> dict[str, Any]:
    should_order = bool_series(plan["should_order"])
    order_rows = plan[should_order]

    sides = order_rows["side"].astype(str).str.lower() if not order_rows.empty else pd.Series(dtype=str)
    delta = pd.to_numeric(order_rows["delta_notional"], errors="coerce") if not order_rows.empty else pd.Series(dtype=float)

    return {
        "rows": int(len(plan)),
        "orders_required": int(should_order.sum()),
        "gross_intended_notional": float(delta.abs().sum()) if not delta.empty else 0.0,
        "buy_count": int((sides == "buy").sum()) if not sides.empty else 0,
        "sell_count": int((sides == "sell").sum()) if not sides.empty else 0,
    }


def filter_to_single_order(
    plan: pd.DataFrame,
    *,
    symbol: str,
    side: str | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return a filtered plan with exactly one selected order enabled."""
    filtered = plan.copy()
    filtered["symbol"] = filtered["symbol"].astype(str).str.upper()
    filtered["side"] = filtered["side"].astype(str).str.lower()

    selected_symbol = symbol.upper().strip()
    selected_side = side.lower().strip() if side else None

    should_order = bool_series(filtered["should_order"])

    mask = should_order & (filtered["symbol"] == selected_symbol)
    if selected_side:
        if selected_side not in {"buy", "sell"}:
            raise ValueError("--side must be buy or sell when provided.")
        mask = mask & (filtered["side"] == selected_side)

    selected = filtered[mask]

    if len(selected) != 1:
        available = filtered[should_order][["symbol", "side", "qty", "delta_notional"]].to_dict(orient="records")
        raise ValueError(
            f"Expected exactly one selected order for symbol={selected_symbol}, side={selected_side}; "
            f"found {len(selected)}. Available order rows: {available}"
        )

    selected_index = selected.index[0]

    original_order_rows = filtered[should_order].copy()
    disabled_indexes = [idx for idx in original_order_rows.index if idx != selected_index]

    for idx in disabled_indexes:
        filtered.loc[idx, "side"] = "hold"
        filtered.loc[idx, "qty"] = 0.0
        filtered.loc[idx, "should_order"] = False
        filtered.loc[idx, "reason"] = "filtered_out_by_single_order_guard"
        filtered.loc[idx, "execution_note"] = "filtered_out_by_single_order_guard"

    filtered.loc[selected_index, "should_order"] = True
    filtered.loc[selected_index, "execution_note"] = "single_order_selected_for_review"

    selected_row = filtered.loc[selected_index].to_dict()

    metadata = {
        "created_utc": utc_now_iso(),
        "selected_symbol": selected_symbol,
        "selected_side": str(filtered.loc[selected_index, "side"]),
        "selected_qty": float(filtered.loc[selected_index, "qty"]),
        "selected_delta_notional": float(filtered.loc[selected_index, "delta_notional"]),
        "original_orders_required": int(len(original_order_rows)),
        "disabled_order_count": int(len(disabled_indexes)),
        "disabled_orders": original_order_rows.loc[disabled_indexes][
            ["symbol", "side", "qty", "delta_notional"]
        ].to_dict(orient="records"),
        "selected_order": selected_row,
    }

    summary = summarize_filtered_plan(filtered)
    if int(summary["orders_required"]) != 1:
        raise RuntimeError(f"Filtered plan should have exactly one order, got: {summary}")

    return filtered, metadata


def copy_support_files(*, run_dir: str | Path, output_dir: str | Path) -> None:
    source = Path(run_dir)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    for name in ["dry_run_targets.csv", "dry_run_summary.json"]:
        src = source / name
        if not src.exists():
            raise FileNotFoundError(f"Missing required support file: {src}")
        shutil.copy2(src, target / name)


def write_filtered_outputs(
    *,
    filtered_plan: pd.DataFrame,
    original_summary: dict[str, Any],
    filter_metadata: dict[str, Any],
    run_dir: str | Path,
    output_dir: str | Path,
) -> dict[str, Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    filtered_summary = dict(original_summary)
    filtered_summary["source_run_dir"] = str(run_dir)
    filtered_summary["output_dir"] = str(out)
    filtered_summary["orders_submitted"] = 0
    filtered_summary["execution_plan"] = summarize_filtered_plan(filtered_plan)
    filtered_summary["single_order_filter"] = filter_metadata

    plan_path = out / "execution_plan.csv"
    summary_path = out / "execution_plan_summary.json"
    metadata_path = out / "single_order_filter_summary.json"

    filtered_plan.to_csv(plan_path, index=False)
    write_json(summary_path, filtered_summary)
    write_json(metadata_path, filter_metadata)

    return {
        "execution_plan": plan_path,
        "execution_plan_summary": summary_path,
        "single_order_filter_summary": metadata_path,
    }


def run_single_order_filter(
    *,
    run_dir: str | Path = DEFAULT_RUN_DIR,
    output_dir: str | Path,
    symbol: str,
    side: str | None = None,
) -> dict[str, Any]:
    plan, summary = load_execution_plan(run_dir)
    validate_plan(plan, summary)

    copy_support_files(run_dir=run_dir, output_dir=output_dir)

    filtered_plan, metadata = filter_to_single_order(
        plan,
        symbol=symbol,
        side=side,
    )

    outputs = write_filtered_outputs(
        filtered_plan=filtered_plan,
        original_summary=summary,
        filter_metadata=metadata,
        run_dir=run_dir,
        output_dir=output_dir,
    )

    result = {
        "run_dir": str(run_dir),
        "output_dir": str(output_dir),
        "selected_symbol": metadata["selected_symbol"],
        "selected_side": metadata["selected_side"],
        "orders_required": 1,
        "orders_submitted": 0,
        "outputs": {key: str(value) for key, value in outputs.items()},
    }

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filter a paper-trading execution plan to one selected order."
    )
    parser.add_argument(
        "--run-dir",
        default=str(DEFAULT_RUN_DIR),
        help="Directory containing execution_plan.csv and execution_plan_summary.json.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where the filtered single-order run will be written.",
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="Ticker symbol of the one order to keep.",
    )
    parser.add_argument(
        "--side",
        choices=["buy", "sell"],
        default=None,
        help="Optional side filter for the selected symbol.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    result = run_single_order_filter(
        run_dir=args.run_dir,
        output_dir=args.output_dir,
        symbol=args.symbol,
        side=args.side,
    )

    print("=" * 80)
    print("SINGLE-ORDER EXECUTION PLAN FILTER")
    print("=" * 80)
    print(f"source_run_dir: {result['run_dir']}")
    print(f"output_dir: {result['output_dir']}")
    print(f"selected_symbol: {result['selected_symbol']}")
    print(f"selected_side: {result['selected_side']}")
    print(f"orders_required: {result['orders_required']}")
    print(f"orders_submitted: {result['orders_submitted']}")
    print()
    for name, path in result["outputs"].items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
