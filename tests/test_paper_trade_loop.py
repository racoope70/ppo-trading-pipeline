import json
from pathlib import Path

import pandas as pd
import pytest

from src.paper_trading.paper_trade_loop import (
    load_execution_plan,
    row_to_intent,
    run_paper_order_plan,
    validate_execution_plan,
    write_order_run,
)


def _write_execution_plan(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    plan = pd.DataFrame(
        [
            {
                "symbol": "AMD",
                "side": "buy",
                "qty": 44.25,
                "price": 414.18,
                "equity": 100_000.0,
                "target_weight": 0.1957,
                "actual_weight": 0.0,
                "target_notional": 19_570.0,
                "actual_notional": 0.0,
                "delta_notional": 19_570.0,
                "min_notional": 25.0,
                "max_abs_weight": 0.40,
                "should_order": True,
                "reason": "rebalance_required",
                "dry_run": True,
                "order_submitted": False,
                "execution_note": "execution_plan_only_no_order_submitted",
            },
            {
                "symbol": "PFE",
                "side": "hold",
                "qty": 0.0,
                "price": 25.68,
                "equity": 100_000.0,
                "target_weight": 0.0,
                "actual_weight": 0.0,
                "target_notional": 0.0,
                "actual_notional": 0.0,
                "delta_notional": 0.0,
                "min_notional": 25.0,
                "max_abs_weight": 0.40,
                "should_order": False,
                "reason": "below_min_notional",
                "dry_run": True,
                "order_submitted": False,
                "execution_note": "below_min_notional",
            },
        ]
    )

    plan.to_csv(run_dir / "execution_plan.csv", index=False)

    summary = {
        "orders_submitted": 0,
        "execution_plan": {
            "rows": 2,
            "orders_required": 1,
            "buy_count": 1,
            "sell_count": 0,
        },
    }

    (run_dir / "execution_plan_summary.json").write_text(
        json.dumps(summary),
        encoding="utf-8",
    )


def test_load_execution_plan_reads_files(tmp_path):
    _write_execution_plan(tmp_path)

    plan, summary = load_execution_plan(tmp_path)

    assert len(plan) == 2
    assert summary["orders_submitted"] == 0


def test_validate_execution_plan_passes_for_clean_plan(tmp_path):
    _write_execution_plan(tmp_path)

    plan, summary = load_execution_plan(tmp_path)
    validate_execution_plan(plan, summary)


def test_validate_execution_plan_fails_if_orders_already_submitted(tmp_path):
    _write_execution_plan(tmp_path)

    plan, summary = load_execution_plan(tmp_path)
    summary["orders_submitted"] = 1

    with pytest.raises(ValueError, match="orders_submitted"):
        validate_execution_plan(plan, summary)


def test_row_to_intent_forces_dry_run_without_submit_flag(tmp_path):
    _write_execution_plan(tmp_path)

    plan, _ = load_execution_plan(tmp_path)
    intent = row_to_intent(plan.iloc[0], submit_orders=False)

    assert intent.symbol == "AMD"
    assert intent.should_order is True
    assert intent.dry_run is True


def test_row_to_intent_allows_non_dry_run_with_submit_flag(tmp_path):
    _write_execution_plan(tmp_path)

    plan, _ = load_execution_plan(tmp_path)
    intent = row_to_intent(plan.iloc[0], submit_orders=True)

    assert intent.symbol == "AMD"
    assert intent.should_order is True
    assert intent.dry_run is False


def test_run_paper_order_plan_default_submits_no_orders(tmp_path):
    _write_execution_plan(tmp_path)

    results, summary = run_paper_order_plan(
        run_dir=tmp_path,
        submit_orders=False,
    )

    assert len(results) == 2
    assert summary["submit_orders"] is False
    assert summary["orders_required"] == 1
    assert summary["orders_submitted"] == 0
    assert results.loc[0, "execution_note"] == "dry_run_no_order_submitted"


def test_write_order_run_outputs_files(tmp_path):
    _write_execution_plan(tmp_path)

    results, summary = run_paper_order_plan(
        run_dir=tmp_path,
        submit_orders=False,
    )

    out_dir = tmp_path / "out"
    results_path, summary_path = write_order_run(results, summary, out_dir)

    assert results_path.exists()
    assert summary_path.exists()

    written_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert written_summary["orders_submitted"] == 0
