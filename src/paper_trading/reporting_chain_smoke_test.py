"""Smoke test the paper-trading reporting chain.

This utility is reporting-only.

It runs the local reporting chain:

1. post-checklist decision-state hook
2. run summary with decision state
3. dashboard with decision state

It does not call Alpaca.
It does not submit orders.
It does not modify execution plans.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.paper_trading.build_decision_dashboard_with_state import write_dashboard
from src.paper_trading.build_run_summary_with_decision_state import write_run_summary
from src.paper_trading.pipeline_decision_state_hook import (
    write_post_checklist_decision_state_report,
)


DEFAULT_SMOKE_REPORT_NAME = "reporting_chain_smoke_test_report.json"
DEFAULT_DASHBOARD_PATH = Path("docs/runs/paper_trading_decision_dashboard_with_state.md")


@dataclass(frozen=True)
class ReportingChainSmokeTestResult:
    run_dir: str
    decision_state_report_exists: bool
    run_summary_exists: bool
    dashboard_exists: bool
    state: str | None
    decision: str | None
    orders_required: int | None
    submit_allowed: bool | None
    passed: bool
    reason: str


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_reporting_chain_smoke_test(
    run_dir: Path,
    prior_symbol: str | None = None,
    prior_side: str | None = None,
    dashboard_path: Path = DEFAULT_DASHBOARD_PATH,
    smoke_report_name: str = DEFAULT_SMOKE_REPORT_NAME,
) -> tuple[ReportingChainSmokeTestResult, Path]:
    """Run the no-submit reporting chain and write a smoke-test report."""

    decision_result, decision_report_path = write_post_checklist_decision_state_report(
        run_dir=run_dir,
        prior_symbol=prior_symbol,
        prior_side=prior_side,
    )

    run_summary_path = write_run_summary(run_dir=run_dir)
    dashboard_output_path = write_dashboard(run_dirs=[run_dir], output_path=dashboard_path)

    run_summary = _read_json(run_summary_path)
    decision_state = run_summary.get("decision_state") or {}

    state = decision_state.get("state")
    decision = decision_state.get("decision")
    orders_required = decision_state.get("orders_required")
    submit_allowed = decision_state.get("submit_allowed")

    dashboard_text = dashboard_output_path.read_text(encoding="utf-8")

    expected_fragments = [
        str(state),
        str(decision),
        str(submit_allowed),
    ]

    fragments_present = all(fragment in dashboard_text for fragment in expected_fragments)

    passed = (
        decision_report_path.exists()
        and run_summary_path.exists()
        and dashboard_output_path.exists()
        and state == decision_result.state
        and decision == decision_result.decision
        and submit_allowed is False
        and fragments_present
    )

    if passed:
        reason = "Reporting chain completed and dashboard agrees with decision-state summary."
    else:
        reason = "Reporting chain smoke test failed one or more artifact consistency checks."

    result = ReportingChainSmokeTestResult(
        run_dir=str(run_dir),
        decision_state_report_exists=decision_report_path.exists(),
        run_summary_exists=run_summary_path.exists(),
        dashboard_exists=dashboard_output_path.exists(),
        state=state,
        decision=decision,
        orders_required=orders_required,
        submit_allowed=submit_allowed,
        passed=passed,
        reason=reason,
    )

    smoke_report_path = run_dir / smoke_report_name
    smoke_report_path.write_text(
        json.dumps(asdict(result), indent=2) + "\n",
        encoding="utf-8",
    )

    return result, smoke_report_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--prior-symbol", default=None)
    parser.add_argument("--prior-side", choices=["buy", "sell"], default=None)
    parser.add_argument("--dashboard-path", type=Path, default=DEFAULT_DASHBOARD_PATH)
    parser.add_argument("--smoke-report-name", default=DEFAULT_SMOKE_REPORT_NAME)
    args = parser.parse_args()

    result, smoke_report_path = run_reporting_chain_smoke_test(
        run_dir=args.run_dir,
        prior_symbol=args.prior_symbol,
        prior_side=args.prior_side,
        dashboard_path=args.dashboard_path,
        smoke_report_name=args.smoke_report_name,
    )

    print("=" * 80)
    print("PAPER-TRADING REPORTING CHAIN SMOKE TEST")
    print("=" * 80)
    print(f"Saved smoke report: {smoke_report_path}")
    print(f"passed: {result.passed}")
    print(f"state: {result.state}")
    print(f"decision: {result.decision}")
    print(f"orders_required: {result.orders_required}")
    print(f"submit_allowed: {result.submit_allowed}")
    print(f"reason: {result.reason}")

    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
