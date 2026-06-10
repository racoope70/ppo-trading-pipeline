from __future__ import annotations

import csv
import json
from pathlib import Path

from src.paper_trading.classify_decision_state import classify_run


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_plan_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "symbol",
        "side",
        "qty",
        "delta_notional",
        "should_order",
        "reason",
        "execution_note",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _base_run(tmp_path: Path, orders_required: int, rows: list[dict], error_count: int = 0) -> Path:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    _write_json(
        run_dir / "dry_run_summary.json",
        {
            "rows": 6,
            "predict_ok_count": 6 - error_count,
            "error_count": error_count,
            "orders_submitted": 0,
        },
    )
    _write_json(
        run_dir / "execution_plan_summary.json",
        {
            "orders_submitted": 0,
            "execution_plan": {
                "rows": 6,
                "orders_required": orders_required,
                "buy_count": sum(1 for row in rows if row["side"] == "buy" and row["should_order"] is True),
                "sell_count": sum(1 for row in rows if row["side"] == "sell" and row["should_order"] is True),
            },
        },
    )
    _write_plan_csv(run_dir / "execution_plan.csv", rows)
    return run_dir


def test_classifies_no_candidate_hold(tmp_path: Path) -> None:
    run_dir = _base_run(
        tmp_path,
        orders_required=0,
        rows=[
            {
                "symbol": "AAPL",
                "side": "hold",
                "qty": "0",
                "delta_notional": "0",
                "should_order": False,
                "reason": "below_min_notional",
                "execution_note": "below_min_notional",
            }
        ],
    )

    result = classify_run(run_dir)

    assert result.state == "NO_CANDIDATE_HOLD"
    assert result.decision == "NO_SUBMIT"
    assert result.submit_allowed is False


def test_classifies_multi_order_plan(tmp_path: Path) -> None:
    run_dir = _base_run(
        tmp_path,
        orders_required=2,
        rows=[
            {
                "symbol": "PFE",
                "side": "buy",
                "qty": "1.0",
                "delta_notional": "45",
                "should_order": True,
                "reason": "rebalance_required",
                "execution_note": "execution_plan_only_no_order_submitted",
            },
            {
                "symbol": "UNH",
                "side": "sell",
                "qty": "0.3",
                "delta_notional": "-135",
                "should_order": True,
                "reason": "rebalance_required",
                "execution_note": "execution_plan_only_no_order_submitted",
            },
        ],
    )

    result = classify_run(run_dir)

    assert result.state == "MULTI_ORDER_PLAN"
    assert result.decision == "NO_SUBMIT"
    assert len(result.candidates) == 2


def test_classifies_changed_candidate(tmp_path: Path) -> None:
    run_dir = _base_run(
        tmp_path,
        orders_required=1,
        rows=[
            {
                "symbol": "AMD",
                "side": "buy",
                "qty": "1.0",
                "delta_notional": "500",
                "should_order": True,
                "reason": "rebalance_required",
                "execution_note": "execution_plan_only_no_order_submitted",
            }
        ],
    )

    result = classify_run(run_dir, prior_symbol="UNH", prior_side="sell")

    assert result.state == "CHANGED_CANDIDATE"
    assert result.decision == "NO_SUBMIT"


def test_classifies_persistent_candidate(tmp_path: Path) -> None:
    run_dir = _base_run(
        tmp_path,
        orders_required=1,
        rows=[
            {
                "symbol": "AMD",
                "side": "buy",
                "qty": "1.0",
                "delta_notional": "500",
                "should_order": True,
                "reason": "rebalance_required",
                "execution_note": "execution_plan_only_no_order_submitted",
            }
        ],
    )

    result = classify_run(run_dir, prior_symbol="AMD", prior_side="buy")

    assert result.state == "PERSISTENT_REVALIDATED_CANDIDATE"
    assert result.decision == "CONTROLLED_REVIEW_ELIGIBLE"
    assert result.submit_allowed is False


def test_ignores_non_rebalance_or_zero_quantity_order_rows(tmp_path: Path) -> None:
    run_dir = _base_run(
        tmp_path,
        orders_required=1,
        rows=[
            {
                "symbol": "AMD",
                "side": "buy",
                "qty": "0",
                "delta_notional": "500",
                "should_order": True,
                "reason": "rebalance_required",
                "execution_note": "execution_plan_only_no_order_submitted",
            },
            {
                "symbol": "UNH",
                "side": "sell",
                "qty": "0.3",
                "delta_notional": "-135",
                "should_order": True,
                "reason": "below_min_notional",
                "execution_note": "below_min_notional",
            },
        ],
    )

    result = classify_run(run_dir)

    assert result.state == "ABORTED_INVALID_FRESH_CYCLE"
    assert result.reason == "Expected exactly one candidate for orders_required=1; found 0."
    assert result.candidates == []


def test_classifies_invalid_fresh_cycle_on_dry_run_errors(tmp_path: Path) -> None:
    run_dir = _base_run(
        tmp_path,
        orders_required=0,
        rows=[],
        error_count=4,
    )

    result = classify_run(run_dir)

    assert result.state == "ABORTED_INVALID_FRESH_CYCLE"
    assert result.decision == "NO_SUBMIT"
    assert result.submit_allowed is False


def test_writes_decision_state_report(tmp_path: Path) -> None:
    from src.paper_trading.classify_decision_state import (
        classify_run,
        write_decision_state_report,
    )

    run_dir = _base_run(
        tmp_path,
        orders_required=0,
        rows=[
            {
                "symbol": "AAPL",
                "side": "hold",
                "qty": "0",
                "delta_notional": "0",
                "should_order": False,
                "reason": "below_min_notional",
                "execution_note": "below_min_notional",
            }
        ],
    )

    result = classify_run(run_dir)
    report_path = write_decision_state_report(result, run_dir)

    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["state"] == "NO_CANDIDATE_HOLD"
    assert payload["decision"] == "NO_SUBMIT"
    assert payload["submit_allowed"] is False
