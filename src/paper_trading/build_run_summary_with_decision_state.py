"""Build a consolidated paper-trading run summary including decision state.

This utility is no-submit and broker-read-free.

It reads local run artifacts and writes:

paper_trading_run_summary.json

The key addition is that the summary includes the decision-state report produced by
the v1.35/v1.36 classification utilities.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_NAME = "paper_trading_run_summary.json"
DECISION_STATE_REPORT_NAME = "decision_state_report.json"


def _read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_run_summary(run_dir: Path) -> dict[str, Any]:
    """Build a consolidated run summary from local paper-trading artifacts."""

    dry_run_summary = _read_json_if_exists(run_dir / "dry_run_summary.json")
    execution_plan_summary = _read_json_if_exists(run_dir / "execution_plan_summary.json")
    paper_order_summary = _read_json_if_exists(run_dir / "paper_order_run_summary.json")
    checklist_report = _read_json_if_exists(run_dir / "pre_trade_checklist_report.json")
    decision_state_report = _read_json_if_exists(run_dir / DECISION_STATE_REPORT_NAME)

    execution_plan_block = {}
    if execution_plan_summary:
        execution_plan_block = execution_plan_summary.get("execution_plan", {}) or {}

    paper_order_block = paper_order_summary or {}

    summary = {
        "run_dir": str(run_dir),
        "artifacts_present": {
            "dry_run_summary": dry_run_summary is not None,
            "execution_plan_summary": execution_plan_summary is not None,
            "paper_order_run_summary": paper_order_summary is not None,
            "pre_trade_checklist_report": checklist_report is not None,
            "decision_state_report": decision_state_report is not None,
        },
        "dry_run": {
            "datetime_utc": (dry_run_summary or {}).get("datetime_utc"),
            "predict_ok_count": (dry_run_summary or {}).get("predict_ok_count"),
            "error_count": (dry_run_summary or {}).get("error_count"),
            "orders_submitted": (dry_run_summary or {}).get("orders_submitted"),
        },
        "execution_plan": {
            "orders_required": execution_plan_block.get("orders_required"),
            "gross_intended_notional": execution_plan_block.get("gross_intended_notional"),
            "buy_count": execution_plan_block.get("buy_count"),
            "sell_count": execution_plan_block.get("sell_count"),
            "orders_submitted": (execution_plan_summary or {}).get("orders_submitted"),
        },
        "paper_order_run": {
            "orders_required": paper_order_block.get("orders_required"),
            "orders_submitted": paper_order_block.get("orders_submitted"),
            "submit_orders": paper_order_block.get("submit_orders"),
            "risk_passed": paper_order_block.get("risk_passed"),
        },
        "checklist": {
            "present": checklist_report is not None,
            "result": (checklist_report or {}).get("result")
            or (checklist_report or {}).get("checklist_result"),
        },
        "decision_state": decision_state_report,
        "safe_default": {
            "decision": (decision_state_report or {}).get("decision", "NO_SUBMIT"),
            "submit_allowed": bool((decision_state_report or {}).get("submit_allowed", False)),
        },
    }

    return summary


def write_run_summary(
    run_dir: Path,
    output_name: str = DEFAULT_OUTPUT_NAME,
) -> Path:
    """Write paper_trading_run_summary.json to the run directory."""
    summary = build_run_summary(run_dir)
    output_path = run_dir / output_name
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--output-name", default=DEFAULT_OUTPUT_NAME)
    args = parser.parse_args()

    output_path = write_run_summary(
        run_dir=args.run_dir,
        output_name=args.output_name,
    )

    summary = _read_json_if_exists(output_path) or {}
    decision_state = summary.get("decision_state") or {}

    print("=" * 80)
    print("PAPER-TRADING RUN SUMMARY WITH DECISION STATE")
    print("=" * 80)
    print(f"Saved run summary: {output_path}")
    print(f"state: {decision_state.get('state')}")
    print(f"decision: {decision_state.get('decision')}")
    print(f"orders_required: {decision_state.get('orders_required')}")
    print(f"submit_allowed: {decision_state.get('submit_allowed')}")


if __name__ == "__main__":
    main()
