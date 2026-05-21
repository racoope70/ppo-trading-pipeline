"""Guarded paper-order runner for Alpaca paper trading.

This script reads an execution plan and optionally submits paper orders.

Safety rules:
- Default mode submits no orders.
- Real paper orders require --submit-orders.
- Alpaca paper endpoint is required before submitting.
- Execution plan must be clean and generated from the dry-run/evaluation/execution-plan chain.
- Submit mode is blocked unless risk controls pass.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.adapters.alpaca import create_alpaca_clients
from src.paper_trading.execution import RebalanceIntent, execute_rebalance_intent
from src.paper_trading.logging_utils import build_and_write_audit_record, snapshot_broker_state
from src.paper_trading.risk_controls import (
    RiskContext,
    RiskControlConfig,
    assert_risk_report_passes,
    evaluate_execution_plan_risk,
)


DEFAULT_RUN_DIR = Path("reports/paper_trading_dry_runs/latest")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def load_execution_plan(run_dir: str | Path = DEFAULT_RUN_DIR) -> tuple[pd.DataFrame, dict[str, Any]]:
    root = Path(run_dir)
    plan_path = root / "execution_plan.csv"
    summary_path = root / "execution_plan_summary.json"

    if not plan_path.exists():
        raise FileNotFoundError(f"Missing execution plan file: {plan_path}")
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing execution plan summary file: {summary_path}")

    plan = pd.read_csv(plan_path)
    summary = read_json(summary_path)

    if plan.empty:
        raise ValueError(f"Execution plan is empty: {plan_path}")

    return plan, summary


def validate_execution_plan(plan: pd.DataFrame, summary: dict[str, Any]) -> None:
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
        "min_notional",
        "max_abs_weight",
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

    if not plan["order_submitted"].astype(str).str.lower().isin(["false", "0"]).all():
        raise ValueError("Execution plan contains order_submitted rows before runner execution.")

    bad_sides = sorted(set(plan["side"].astype(str).str.lower()) - {"buy", "sell", "hold"})
    if bad_sides:
        raise ValueError(f"Execution plan contains invalid sides: {bad_sides}")

    qty_values = pd.to_numeric(plan["qty"], errors="coerce")
    if qty_values.isna().any() or (qty_values < 0).any():
        raise ValueError("Execution plan contains invalid qty values.")

    should_order = plan["should_order"].astype(str).str.lower().isin(["true", "1"])
    invalid_order_rows = plan[
        should_order & ~plan["side"].astype(str).str.lower().isin(["buy", "sell"])
    ]
    if not invalid_order_rows.empty:
        raise ValueError("Rows requiring orders must have side buy or sell.")


def row_to_intent(row: pd.Series, *, submit_orders: bool) -> RebalanceIntent:
    """Convert an execution-plan row back into a RebalanceIntent.

    dry_run is forced to True unless submit_orders=True.
    """
    return RebalanceIntent(
        symbol=str(row["symbol"]).upper(),
        side=str(row["side"]).lower(),
        qty=float(row["qty"]),
        price=float(row["price"]),
        equity=float(row["equity"]),
        target_weight=float(row["target_weight"]),
        actual_weight=float(row["actual_weight"]),
        target_notional=float(row["target_notional"]),
        actual_notional=float(row["actual_notional"]),
        delta_notional=float(row["delta_notional"]),
        min_notional=float(row["min_notional"]),
        max_abs_weight=float(row["max_abs_weight"]),
        should_order=str(row["should_order"]).strip().lower() in {"true", "1"},
        reason=str(row["reason"]),
        dry_run=not bool(submit_orders),
    )


def build_risk_context(
    trading_client: Any | None,
    *,
    submit_orders: bool,
) -> RiskContext:
    """Build optional broker context for risk controls.

    In dry-run mode this intentionally avoids broker calls.
    In submit mode this attempts to capture current account state.
    """
    if not submit_orders or trading_client is None:
        return RiskContext(submit_orders=submit_orders)

    account_equity = None
    cash = None
    positions_count = None
    open_orders_count = None

    try:
        account = trading_client.get_account()
        account_equity = float(getattr(account, "equity", 0.0) or 0.0)
        cash = float(getattr(account, "cash", 0.0) or 0.0)
    except Exception:
        pass

    try:
        positions = trading_client.get_all_positions() or []
        positions_count = len(positions)
    except Exception:
        pass

    try:
        open_orders = trading_client.get_orders() or []
        open_orders_count = len(open_orders)
    except Exception:
        pass

    return RiskContext(
        account_equity=account_equity,
        cash=cash,
        positions_count=positions_count,
        open_orders_count=open_orders_count,
        now_utc=utc_now_iso(),
        submit_orders=submit_orders,
    )


def run_paper_order_plan(
    *,
    run_dir: str | Path = DEFAULT_RUN_DIR,
    output_dir: str | Path | None = None,
    submit_orders: bool = False,
    env_path: str | Path = ".env",
    trading_client: Any | None = None,
    risk_config: RiskControlConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Run an execution plan in guarded dry-run or submit mode."""
    root = Path(run_dir)
    out_root = Path(output_dir) if output_dir is not None else root

    plan, plan_summary = load_execution_plan(root)
    validate_execution_plan(plan, plan_summary)

    if submit_orders and trading_client is None:
        trading_client, _ = create_alpaca_clients(
            env_path=env_path,
            require_paper=True,
        )

    broker_state_before = (
        snapshot_broker_state(trading_client)
        if trading_client is not None
        else {}
    )

    risk_ctx = build_risk_context(
        trading_client,
        submit_orders=submit_orders,
    )

    report = evaluate_execution_plan_risk(
        plan,
        plan_summary,
        config=risk_config or RiskControlConfig(),
        context=risk_ctx,
    )

    if submit_orders:
        assert_risk_report_passes(report)

    results: list[dict[str, Any]] = []

    for _, row in plan.iterrows():
        intent = row_to_intent(row, submit_orders=submit_orders)
        result = execute_rebalance_intent(
            trading_client=trading_client,
            intent=intent,
            submit_orders=submit_orders,
        )
        result["datetime_utc"] = utc_now_iso()
        result["source_reason"] = str(row["reason"])
        result["risk_passed"] = bool(report.passed)
        results.append(result)

    result_df = pd.DataFrame(results)

    order_submitted_count = (
        int(result_df["order_submitted"].astype(bool).sum())
        if not result_df.empty
        else 0
    )
    should_order_count = (
        int(result_df["should_order"].astype(bool).sum())
        if not result_df.empty
        else 0
    )

    broker_state_after = (
        snapshot_broker_state(trading_client)
        if trading_client is not None
        else {}
    )

    summary = {
        "datetime_utc": utc_now_iso(),
        "source_run_dir": str(root),
        "output_dir": str(out_root),
        "submit_orders": bool(submit_orders),
        "orders_submitted": order_submitted_count,
        "orders_required": should_order_count,
        "rows": int(len(result_df)),
        "paper_endpoint_required": True,
        "risk_passed": bool(report.passed),
        "risk_report": report.to_dict(),
        "risk_context": {
            "account_equity": risk_ctx.account_equity,
            "cash": risk_ctx.cash,
            "positions_count": risk_ctx.positions_count,
            "open_orders_count": risk_ctx.open_orders_count,
            "now_utc": risk_ctx.now_utc,
            "submit_orders": risk_ctx.submit_orders,
        },
        "broker_state_before": broker_state_before,
        "broker_state_after": broker_state_after,
        "plan_summary": plan_summary,
    }

    return result_df, summary


def write_order_run(
    results: pd.DataFrame,
    summary: dict[str, Any],
    output_dir: str | Path,
) -> tuple[Path, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    results_path = root / "paper_order_run.csv"
    summary_path = root / "paper_order_run_summary.json"

    results.to_csv(results_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    build_and_write_audit_record(
        run_dir=root,
        output_dir=root,
        broker_state_before=summary.get("broker_state_before", {}),
        broker_state_after=summary.get("broker_state_after", {}),
        metadata={
            "source": "paper_trade_loop",
            "summary_path": str(summary_path),
            "results_path": str(results_path),
        },
    )

    return results_path, summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Guarded paper-order runner from execution_plan.csv."
    )
    parser.add_argument(
        "--run-dir",
        default=str(DEFAULT_RUN_DIR),
        help="Directory containing execution_plan.csv and execution_plan_summary.json.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Default: same as --run-dir.",
    )
    parser.add_argument(
        "--env",
        default=".env",
        help="Path to local .env file for Alpaca credentials.",
    )
    parser.add_argument(
        "--submit-orders",
        action="store_true",
        help="Submit real Alpaca paper orders. Omit this flag for no-order dry-run mode.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir) if args.output_dir else Path(args.run_dir)

    print("=" * 80)
    print("GUARDED ALPACA PAPER-ORDER RUNNER")
    print("=" * 80)
    print(f"Run dir: {args.run_dir}")
    print(f"Output dir: {output_dir}")
    print(f"Submit orders: {bool(args.submit_orders)}")
    print()

    results, summary = run_paper_order_plan(
        run_dir=args.run_dir,
        output_dir=output_dir,
        submit_orders=bool(args.submit_orders),
        env_path=args.env,
    )

    results_path, summary_path = write_order_run(results, summary, output_dir)

    display_cols = [
        "symbol",
        "side",
        "qty",
        "should_order",
        "order_submitted",
        "order_id",
        "risk_passed",
        "execution_note",
    ]

    print(results[display_cols].to_string(index=False))
    print()
    print("Risk controls:")
    print(f"risk_passed={summary['risk_passed']}")
    print()
    print("Paper-order run summary:")
    print(f"rows={summary['rows']}")
    print(f"orders_required={summary['orders_required']}")
    print(f"orders_submitted={summary['orders_submitted']}")
    print(f"submit_orders={summary['submit_orders']}")
    print()
    print(f"Saved order run: {results_path}")
    print(f"Saved order summary: {summary_path}")
    print(f"Saved audit log: {output_dir / 'paper_trade_audit_log.json'}")

    if not args.submit_orders:
        print()
        print("Dry-run mode complete. No orders were submitted.")


if __name__ == "__main__":
    main()
