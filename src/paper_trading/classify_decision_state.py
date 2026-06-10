"""Classify paper-trading dry-run outputs using the v1.33 decision state machine.

This utility is read-only. It does not connect to Alpaca and does not submit orders.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_REPORT_NAME = "decision_state_report.json"


@dataclass(frozen=True)
class DecisionState:
    state: str
    decision: str
    reason: str
    orders_required: int | None
    buy_count: int | None
    sell_count: int | None
    candidates: list[dict[str, Any]]
    submit_allowed: bool


def decision_state_to_dict(result: DecisionState) -> dict[str, Any]:
    """Convert a DecisionState dataclass to a stable JSON-serializable dict."""
    return asdict(result)


def write_decision_state_report(
    result: DecisionState,
    run_dir: Path,
    report_name: str = DEFAULT_REPORT_NAME,
) -> Path:
    """Write the decision state classification report into the run directory."""
    output_path = run_dir / report_name
    output_path.write_text(
        json.dumps(decision_state_to_dict(result), indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")

    return payload


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _as_int(value: Any, default: int | None = None) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _candidate_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    for row in rows:
        if not _truthy(row.get("should_order")):
            continue

        side = str(row.get("side", "")).strip().lower()
        if side not in {"buy", "sell"}:
            continue

        if _as_float(row.get("qty")) <= 0.0:
            continue

        if str(row.get("reason", "")).strip().lower() != "rebalance_required":
            continue

        candidates.append(
            {
                "symbol": row.get("symbol"),
                "side": side,
                "qty": row.get("qty"),
                "delta_notional": row.get("delta_notional"),
                "reason": row.get("reason"),
                "execution_note": row.get("execution_note"),
            }
        )

    return candidates


def classify_run(
    run_dir: Path,
    prior_symbol: str | None = None,
    prior_side: str | None = None,
    filtered_review: bool = False,
) -> DecisionState:
    """Classify a paper-trading run directory.

    Parameters
    ----------
    run_dir:
        Directory containing dry_run_summary.json, execution_plan_summary.json,
        and execution_plan.csv.
    prior_symbol / prior_side:
        Optional prior candidate used to determine whether a single candidate is
        persistent or changed.
    filtered_review:
        True when the run directory is a filtered single-order review directory.
    """

    dry_summary_path = run_dir / "dry_run_summary.json"
    plan_summary_path = run_dir / "execution_plan_summary.json"
    plan_csv_path = run_dir / "execution_plan.csv"

    missing = [
        str(path.name)
        for path in [dry_summary_path, plan_summary_path, plan_csv_path]
        if not path.exists()
    ]
    if missing:
        return DecisionState(
            state="ABORTED_INVALID_FRESH_CYCLE",
            decision="NO_SUBMIT",
            reason=f"Missing required artifact(s): {', '.join(missing)}.",
            orders_required=None,
            buy_count=None,
            sell_count=None,
            candidates=[],
            submit_allowed=False,
        )

    dry_summary = _read_json(dry_summary_path)
    plan_summary = _read_json(plan_summary_path)
    rows = _read_csv_rows(plan_csv_path)

    error_count = _as_int(dry_summary.get("error_count"), default=0)
    dry_orders_submitted = _as_int(dry_summary.get("orders_submitted"), default=0)

    execution_plan = plan_summary.get("execution_plan", {})
    orders_required = _as_int(execution_plan.get("orders_required"), default=0)
    buy_count = _as_int(execution_plan.get("buy_count"), default=0)
    sell_count = _as_int(execution_plan.get("sell_count"), default=0)
    summary_orders_submitted = _as_int(plan_summary.get("orders_submitted"), default=0)

    candidates = _candidate_rows(rows)

    if error_count and error_count > 0:
        return DecisionState(
            state="ABORTED_INVALID_FRESH_CYCLE",
            decision="NO_SUBMIT",
            reason=f"Dry-run summary reported error_count={error_count}.",
            orders_required=orders_required,
            buy_count=buy_count,
            sell_count=sell_count,
            candidates=candidates,
            submit_allowed=False,
        )

    if dry_orders_submitted and dry_orders_submitted > 0:
        return DecisionState(
            state="ABORTED_INVALID_FRESH_CYCLE",
            decision="NO_SUBMIT",
            reason=f"Dry-run summary reported orders_submitted={dry_orders_submitted}.",
            orders_required=orders_required,
            buy_count=buy_count,
            sell_count=sell_count,
            candidates=candidates,
            submit_allowed=False,
        )

    if summary_orders_submitted and summary_orders_submitted > 0:
        return DecisionState(
            state="ABORTED_INVALID_FRESH_CYCLE",
            decision="NO_SUBMIT",
            reason=f"Execution-plan summary reported orders_submitted={summary_orders_submitted}.",
            orders_required=orders_required,
            buy_count=buy_count,
            sell_count=sell_count,
            candidates=candidates,
            submit_allowed=False,
        )

    if orders_required == 0:
        return DecisionState(
            state="NO_CANDIDATE_HOLD",
            decision="NO_SUBMIT",
            reason="No eligible order rows were present.",
            orders_required=orders_required,
            buy_count=buy_count,
            sell_count=sell_count,
            candidates=candidates,
            submit_allowed=False,
        )

    if orders_required is not None and orders_required > 1:
        return DecisionState(
            state="MULTI_ORDER_PLAN",
            decision="NO_SUBMIT",
            reason="Fresh execution plan contains more than one eligible order.",
            orders_required=orders_required,
            buy_count=buy_count,
            sell_count=sell_count,
            candidates=candidates,
            submit_allowed=False,
        )

    if filtered_review:
        return DecisionState(
            state="FILTERED_CANDIDATE_REVIEW",
            decision="NO_SUBMIT",
            reason="Single candidate was filtered for review only.",
            orders_required=orders_required,
            buy_count=buy_count,
            sell_count=sell_count,
            candidates=candidates,
            submit_allowed=False,
        )

    if len(candidates) != 1:
        return DecisionState(
            state="ABORTED_INVALID_FRESH_CYCLE",
            decision="NO_SUBMIT",
            reason=f"Expected exactly one candidate for orders_required=1; found {len(candidates)}.",
            orders_required=orders_required,
            buy_count=buy_count,
            sell_count=sell_count,
            candidates=candidates,
            submit_allowed=False,
        )

    candidate = candidates[0]
    current_symbol = str(candidate.get("symbol", "")).upper()
    current_side = str(candidate.get("side", "")).lower()

    if prior_symbol and prior_side:
        if current_symbol == prior_symbol.upper() and current_side == prior_side.lower():
            return DecisionState(
                state="PERSISTENT_REVALIDATED_CANDIDATE",
                decision="CONTROLLED_REVIEW_ELIGIBLE",
                reason="Same symbol and side reappeared on a fresh run.",
                orders_required=orders_required,
                buy_count=buy_count,
                sell_count=sell_count,
                candidates=candidates,
                submit_allowed=False,
            )

        return DecisionState(
            state="CHANGED_CANDIDATE",
            decision="NO_SUBMIT",
            reason=(
                f"Candidate changed from {prior_symbol.upper()} {prior_side.lower()} "
                f"to {current_symbol} {current_side}."
            ),
            orders_required=orders_required,
            buy_count=buy_count,
            sell_count=sell_count,
            candidates=candidates,
            submit_allowed=False,
        )

    return DecisionState(
        state="SINGLE_NEW_CANDIDATE",
        decision="NO_SUBMIT",
        reason="One candidate appeared, but no prior candidate was provided for persistence validation.",
        orders_required=orders_required,
        buy_count=buy_count,
        sell_count=sell_count,
        candidates=candidates,
        submit_allowed=False,
    )


def _print_text(result: DecisionState) -> None:
    print("=" * 80)
    print("PAPER-TRADING DECISION STATE CLASSIFICATION")
    print("=" * 80)
    print(f"state: {result.state}")
    print(f"decision: {result.decision}")
    print(f"reason: {result.reason}")
    print(f"orders_required: {result.orders_required}")
    print(f"buy_count: {result.buy_count}")
    print(f"sell_count: {result.sell_count}")
    print(f"submit_allowed: {result.submit_allowed}")

    print("\nCandidates:")
    if not result.candidates:
        print("(none)")
    else:
        for row in result.candidates:
            print(
                f"- {row.get('symbol')} {row.get('side')} "
                f"qty={row.get('qty')} "
                f"delta_notional={row.get('delta_notional')} "
                f"reason={row.get('reason')}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--prior-symbol", default=None)
    parser.add_argument("--prior-side", choices=["buy", "sell"], default=None)
    parser.add_argument("--filtered-review", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--write-report", action="store_true", help="Write decision_state_report.json into run directory.")
    parser.add_argument("--report-name", default=DEFAULT_REPORT_NAME, help="Report filename when --write-report is used.")
    args = parser.parse_args()

    result = classify_run(
        run_dir=args.run_dir,
        prior_symbol=args.prior_symbol,
        prior_side=args.prior_side,
        filtered_review=args.filtered_review,
    )

    if args.write_report:
        report_path = write_decision_state_report(
            result=result,
            run_dir=args.run_dir,
            report_name=args.report_name,
        )
        print(f"Saved decision state report: {report_path}")

    if args.json:
        print(json.dumps(decision_state_to_dict(result), indent=2))
    else:
        _print_text(result)


if __name__ == "__main__":
    main()
