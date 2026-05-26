"""Paper-trading run summary dashboard.

This utility creates a compact Markdown/JSON dashboard for the Alpaca
paper-trading deployment milestones.

It does not submit orders.
It does not call Alpaca.
It only reads local run files and milestone documentation.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


MILESTONE_DOCS = {
    "v1.1": "docs/runs/v1.1_controlled_alpaca_paper_order_test.md",
    "v1.2": "docs/runs/v1.2_post_order_monitoring_and_rebalance_test.md",
    "v1.3": "docs/runs/v1.3_short_monitored_paper_trading_session.md",
}


def read_json_if_exists(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}

    payload = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {p}")
    return payload


def read_csv_if_exists(path: str | Path) -> list[dict[str, str]]:
    p = Path(path)
    if not p.exists():
        return []

    with p.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def doc_status(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    exists = p.exists()
    text = p.read_text(encoding="utf-8") if exists else ""
    lower_text = text.lower()

    return {
        "path": str(p),
        "exists": exists,
        "line_count": len(text.splitlines()) if exists else 0,
        "mentions_passed": "passed" in lower_text,
        "mentions_open_orders_none": "open_orders = none" in lower_text
        or "open orders = none" in lower_text,
    }


def summarize_milestones() -> dict[str, Any]:
    return {
        milestone: doc_status(path)
        for milestone, path in MILESTONE_DOCS.items()
    }


def _truthy_csv_value(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"true", "1", "yes"}


def summarize_latest_run(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)

    dry_summary = read_json_if_exists(root / "dry_run_summary.json")
    execution_summary = read_json_if_exists(root / "execution_plan_summary.json")
    order_summary = read_json_if_exists(root / "paper_order_run_summary.json")
    checklist = read_json_if_exists(root / "pre_trade_checklist_report.json")
    audit = read_json_if_exists(root / "paper_trade_audit_log.json")

    execution_plan_rows = read_csv_if_exists(root / "execution_plan.csv")
    paper_order_rows = read_csv_if_exists(root / "paper_order_run.csv")

    order_candidates = [
        row
        for row in execution_plan_rows
        if _truthy_csv_value(row.get("should_order"))
    ]

    submitted_orders = [
        row
        for row in paper_order_rows
        if _truthy_csv_value(row.get("order_submitted"))
    ]

    return {
        "run_dir": str(root),
        "run_dir_exists": root.exists(),
        "dry_run_rows": dry_summary.get("rows"),
        "dry_run_predict_ok_count": dry_summary.get("predict_ok_count"),
        "dry_run_error_count": dry_summary.get("error_count"),
        "execution_orders_required": execution_summary.get("execution_plan", {}).get("orders_required"),
        "execution_gross_intended_notional": execution_summary.get("execution_plan", {}).get(
            "gross_intended_notional"
        ),
        "paper_submit_orders": order_summary.get("submit_orders"),
        "paper_orders_required": order_summary.get("orders_required"),
        "paper_orders_submitted": order_summary.get("orders_submitted"),
        "paper_risk_passed": order_summary.get("risk_passed"),
        "checklist_result": checklist.get("result", checklist.get("passed")),
        "audit_risk_passed": audit.get("risk_passed"),
        "audit_orders_submitted": audit.get("orders_submitted"),
        "order_candidates": order_candidates,
        "submitted_orders": submitted_orders,
    }


def build_dashboard_payload(run_dir: str | Path) -> dict[str, Any]:
    milestone_summary = summarize_milestones()
    latest_run_summary = summarize_latest_run(run_dir)

    docs_complete = all(item["exists"] for item in milestone_summary.values())
    latest_run_exists = bool(latest_run_summary["run_dir_exists"])
    risk_passed = latest_run_summary.get("paper_risk_passed")

    deployment_status = "READY_FOR_TRAINING_PIPELINE_PHASE"
    if not docs_complete:
        deployment_status = "MISSING_MILESTONE_DOCS"
    elif not latest_run_exists:
        deployment_status = "MISSING_LATEST_RUN"
    elif risk_passed is False:
        deployment_status = "RISK_REVIEW_REQUIRED"

    return {
        "dashboard_name": "v1.4_paper_trading_run_summary_dashboard",
        "deployment_status": deployment_status,
        "milestones": milestone_summary,
        "latest_run": latest_run_summary,
        "recommendation": (
            "Current paper-trading deployment checkpoint is documented. "
            "Next major phase should be Alpaca historical-data PPO retraining with "
            "embargo and VecNormalize validation hardening before hybrid models."
        ),
    }


def _bool_icon(value: Any) -> str:
    if value is True:
        return "PASS"
    if value is False:
        return "FAIL"
    return "N/A"


def _safe(value: Any) -> str:
    if value is None:
        return "N/A"
    return str(value)


def markdown_order_rows(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "```text\nnone\n```"

    lines = [
        "| symbol | side | qty | price | target_weight | actual_weight | delta_notional | order_submitted |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]

    for row in rows:
        lines.append(
            "| {symbol} | {side} | {qty} | {price} | {target_weight} | {actual_weight} | "
            "{delta_notional} | {order_submitted} |".format(
                symbol=row.get("symbol", ""),
                side=row.get("side", ""),
                qty=row.get("qty", ""),
                price=row.get("price", ""),
                target_weight=row.get("target_weight", ""),
                actual_weight=row.get("actual_weight", ""),
                delta_notional=row.get("delta_notional", ""),
                order_submitted=row.get("order_submitted", ""),
            )
        )

    return "\n".join(lines)


def render_markdown_dashboard(payload: dict[str, Any]) -> str:
    latest = payload["latest_run"]
    milestones = payload["milestones"]

    milestone_lines = [
        "| milestone | doc exists | path |",
        "|---|---:|---|",
    ]

    for name, item in milestones.items():
        milestone_lines.append(
            f"| {name} | {_bool_icon(item['exists'])} | `{item['path']}` |"
        )

    return f"""# v1.4 Paper-Trading Run Summary / Monitoring Dashboard

## Purpose

Summarize the current Alpaca paper-trading deployment after the controlled paper-order milestones.

This dashboard does not submit orders. It summarizes local documentation and latest paper-trading run files.

## Deployment Status

```text
{payload["deployment_status"]}
```

## Milestone Documentation

{chr(10).join(milestone_lines)}

## Latest Run Directory

```text
{latest["run_dir"]}
```

## Latest Run Summary

```text
run_dir_exists = {latest["run_dir_exists"]}
dry_run_rows = {_safe(latest["dry_run_rows"])}
dry_run_predict_ok_count = {_safe(latest["dry_run_predict_ok_count"])}
dry_run_error_count = {_safe(latest["dry_run_error_count"])}
execution_orders_required = {_safe(latest["execution_orders_required"])}
execution_gross_intended_notional = {_safe(latest["execution_gross_intended_notional"])}
paper_submit_orders = {_safe(latest["paper_submit_orders"])}
paper_orders_required = {_safe(latest["paper_orders_required"])}
paper_orders_submitted = {_safe(latest["paper_orders_submitted"])}
paper_risk_passed = {_safe(latest["paper_risk_passed"])}
checklist_result = {_safe(latest["checklist_result"])}
audit_risk_passed = {_safe(latest["audit_risk_passed"])}
audit_orders_submitted = {_safe(latest["audit_orders_submitted"])}
```

## Latest Order Candidates

{markdown_order_rows(latest["order_candidates"])}

## Latest Submitted Orders

{markdown_order_rows(latest["submitted_orders"])}

## Interpretation

The paper-trading deployment has now demonstrated:

```text
environment/key loading
Alpaca paper broker connection
bar fetching
model artifact loading
model.predict() execution
target-weight generation
execution-plan generation
risk-control checks
guarded paper-order submission
audit logging
broker verification after submit
open-order handling
existing-position handling
```

## Recommendation

{payload["recommendation"]}

## Next Step

Recommended next checkpoint:

```text
v1.5 Alpaca historical-data PPO retraining roadmap
```

Do not move to unattended trading yet.
"""


def write_dashboard(
    *,
    run_dir: str | Path,
    output_json: str | Path,
    output_md: str | Path,
) -> tuple[dict[str, Any], Path, Path]:
    payload = build_dashboard_payload(run_dir)

    json_path = Path(output_json)
    md_path = Path(output_md)

    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_dashboard(payload), encoding="utf-8")

    return payload, json_path, md_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create v1.4 paper-trading run summary dashboard."
    )
    parser.add_argument(
        "--run-dir",
        default="reports/paper_trading_dry_runs/latest",
    )
    parser.add_argument(
        "--output-json",
        default="reports/paper_trading_monitoring/v1_4_run_summary_dashboard.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/runs/v1.4_paper_trading_run_summary_dashboard.md",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    payload, json_path, md_path = write_dashboard(
        run_dir=args.run_dir,
        output_json=args.output_json,
        output_md=args.output_md,
    )

    print("=" * 80)
    print("v1.4 PAPER-TRADING RUN SUMMARY DASHBOARD")
    print("=" * 80)
    print(f"deployment_status: {payload['deployment_status']}")
    print(f"json: {json_path}")
    print(f"markdown: {md_path}")


if __name__ == "__main__":
    main()
