"""Build a paper-trading decision dashboard that includes decision state.

This utility is reporting-only.

It reads local run-summary artifacts and writes a markdown dashboard.

No broker connection.
No order submission.
No execution-plan modification.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_PATH = Path("docs/runs/paper_trading_decision_dashboard_with_state.md")
RUN_SUMMARY_NAME = "paper_trading_run_summary.json"
DECISION_STATE_REPORT_NAME = "decision_state_report.json"


def _read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_decision_state(run_dir: Path) -> dict[str, Any] | None:
    """Load decision state from run summary first, then fallback report."""
    run_summary = _read_json_if_exists(run_dir / RUN_SUMMARY_NAME)
    if run_summary and run_summary.get("decision_state"):
        return run_summary["decision_state"]

    return _read_json_if_exists(run_dir / DECISION_STATE_REPORT_NAME)


def build_dashboard_rows(run_dirs: list[Path]) -> list[dict[str, Any]]:
    """Build dashboard rows from one or more run directories."""
    rows: list[dict[str, Any]] = []

    for run_dir in run_dirs:
        run_summary = _read_json_if_exists(run_dir / RUN_SUMMARY_NAME) or {}
        decision_state = _load_decision_state(run_dir) or {}

        dry_run = run_summary.get("dry_run") or {}
        execution_plan = run_summary.get("execution_plan") or {}
        paper_order_run = run_summary.get("paper_order_run") or {}
        safe_default = run_summary.get("safe_default") or {}

        rows.append(
            {
                "run_dir": str(run_dir),
                "datetime_utc": dry_run.get("datetime_utc"),
                "state": decision_state.get("state"),
                "decision": decision_state.get("decision") or safe_default.get("decision"),
                "reason": decision_state.get("reason"),
                "orders_required": decision_state.get("orders_required")
                if decision_state.get("orders_required") is not None
                else execution_plan.get("orders_required"),
                "buy_count": decision_state.get("buy_count")
                if decision_state.get("buy_count") is not None
                else execution_plan.get("buy_count"),
                "sell_count": decision_state.get("sell_count")
                if decision_state.get("sell_count") is not None
                else execution_plan.get("sell_count"),
                "submit_allowed": decision_state.get("submit_allowed")
                if decision_state.get("submit_allowed") is not None
                else safe_default.get("submit_allowed", False),
                "orders_submitted": paper_order_run.get("orders_submitted"),
                "risk_passed": paper_order_run.get("risk_passed"),
            }
        )

    return rows


def render_markdown_dashboard(rows: list[dict[str, Any]]) -> str:
    """Render dashboard rows as markdown."""
    lines = [
        "# Paper-Trading Decision Dashboard With State",
        "",
        "This dashboard includes the decision-state classification from each reviewed run.",
        "",
        "No broker connection is required.",
        "",
        "No orders are submitted by this dashboard.",
        "",
        "| Run Dir | State | Decision | Orders Required | Buy | Sell | Submit Allowed | Orders Submitted | Risk Passed | Reason |",
        "|---|---|---|---:|---:|---:|---|---:|---|---|",
    ]

    for row in rows:
        lines.append(
            "| {run_dir} | {state} | {decision} | {orders_required} | {buy_count} | {sell_count} | {submit_allowed} | {orders_submitted} | {risk_passed} | {reason} |".format(
                run_dir=row.get("run_dir") or "",
                state=row.get("state") or "",
                decision=row.get("decision") or "",
                orders_required=row.get("orders_required")
                if row.get("orders_required") is not None
                else "",
                buy_count=row.get("buy_count") if row.get("buy_count") is not None else "",
                sell_count=row.get("sell_count") if row.get("sell_count") is not None else "",
                submit_allowed=str(row.get("submit_allowed")),
                orders_submitted=row.get("orders_submitted")
                if row.get("orders_submitted") is not None
                else "",
                risk_passed=str(row.get("risk_passed")),
                reason=(row.get("reason") or "").replace("|", "/"),
            )
        )

    lines.extend(
        [
            "",
            "## Safety Interpretation",
            "",
            "The dashboard is reporting-only. A decision state of `NO_SUBMIT` means the run should not be submitted.",
            "",
            "A `submit_allowed` value of `False` must be treated as a hard no-submit condition.",
            "",
        ]
    )

    return "\n".join(lines)


def write_dashboard(run_dirs: list[Path], output_path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    """Write the markdown dashboard."""
    rows = build_dashboard_rows(run_dirs)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown_dashboard(rows) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        action="append",
        required=True,
        type=Path,
        help="Run directory to include. Can be passed multiple times.",
    )
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    output_path = write_dashboard(run_dirs=args.run_dir, output_path=args.output_path)
    rows = build_dashboard_rows(args.run_dir)

    print("=" * 80)
    print("PAPER-TRADING DECISION DASHBOARD WITH STATE")
    print("=" * 80)
    print(f"Saved dashboard: {output_path}")

    for row in rows:
        print(
            f"{row['run_dir']} | state={row.get('state')} | "
            f"decision={row.get('decision')} | "
            f"orders_required={row.get('orders_required')} | "
            f"submit_allowed={row.get('submit_allowed')}"
        )


if __name__ == "__main__":
    main()
