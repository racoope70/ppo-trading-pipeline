"""Post-checklist decision-state classification hook.

This module is intentionally no-submit and broker-read-free.

It is designed to run after pre_trade_checklist and write:
decision_state_report.json

The hook does not connect to Alpaca.
The hook does not submit orders.
The hook only reads local run artifacts and writes a local report.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.paper_trading.classify_decision_state import (
    DEFAULT_REPORT_NAME,
    DecisionState,
    classify_run,
    write_decision_state_report,
)


def write_post_checklist_decision_state_report(
    run_dir: Path,
    prior_symbol: str | None = None,
    prior_side: str | None = None,
    filtered_review: bool = False,
    submit_checkpoint: bool = False,
    report_name: str = DEFAULT_REPORT_NAME,
    require_checklist_report: bool = True,
) -> tuple[DecisionState, Path]:
    """Classify a run directory and write a decision-state report.

    Parameters
    ----------
    run_dir:
        Paper-trading run directory.
    prior_symbol / prior_side:
        Prior candidate metadata used for persistence classification.
    filtered_review:
        True when classifying a filtered single-order review directory.
    submit_checkpoint:
        True only when a separate controlled-submit checkpoint explicitly allows it.
    report_name:
        Name of the JSON report file.
    require_checklist_report:
        When True, require pre_trade_checklist_report.json to exist before writing
        the classification report. This makes the hook explicitly post-checklist.
    """

    checklist_path = run_dir / "pre_trade_checklist_report.json"
    if require_checklist_report and not checklist_path.exists():
        raise FileNotFoundError(
            f"Missing required post-checklist artifact: {checklist_path}"
        )

    result = classify_run(
        run_dir=run_dir,
        prior_symbol=prior_symbol,
        prior_side=prior_side,
        filtered_review=filtered_review,
    )

    report_path = write_decision_state_report(
        result=result,
        run_dir=run_dir,
        report_name=report_name,
    )

    return result, report_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--prior-symbol", default=None)
    parser.add_argument("--prior-side", choices=["buy", "sell"], default=None)
    parser.add_argument("--filtered-review", action="store_true")
    parser.add_argument("--submit-checkpoint", action="store_true")
    parser.add_argument("--report-name", default=DEFAULT_REPORT_NAME)
    parser.add_argument(
        "--allow-missing-checklist",
        action="store_true",
        help="Allow writing a decision report before pre_trade_checklist_report.json exists.",
    )
    args = parser.parse_args()

    result, report_path = write_post_checklist_decision_state_report(
        run_dir=args.run_dir,
        prior_symbol=args.prior_symbol,
        prior_side=args.prior_side,
        filtered_review=args.filtered_review,
        submit_checkpoint=args.submit_checkpoint,
        report_name=args.report_name,
        require_checklist_report=not args.allow_missing_checklist,
    )

    print("=" * 80)
    print("POST-CHECKLIST DECISION STATE HOOK")
    print("=" * 80)
    print(f"Saved decision state report: {report_path}")
    print(f"state: {result.state}")
    print(f"decision: {result.decision}")
    print(f"reason: {result.reason}")
    print(f"orders_required: {result.orders_required}")
    print(f"submit_allowed: {result.submit_allowed}")


if __name__ == "__main__":
    main()
