import json
from pathlib import Path

import pandas as pd
import pytest

from src.paper_trading.paper_trade_loop import (
    assert_submit_run_dir_confirmed,
    normalize_run_dir_confirmation_value,
    run_paper_order_plan,
)


def _write_hold_only_plan(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    plan = pd.DataFrame(
        [
            {
                "symbol": "AMD",
                "side": "hold",
                "qty": 0.0,
                "price": 525.57,
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
                "latest_bar_time": "2026-06-04T15:00:00+00:00",
                "order_submitted": False,
                "execution_note": "below_min_notional",
            }
        ]
    )
    plan.to_csv(run_dir / "execution_plan.csv", index=False)

    summary = {
        "orders_submitted": 0,
        "execution_plan": {
            "rows": 1,
            "orders_required": 0,
            "gross_intended_notional": 0.0,
            "buy_count": 0,
            "sell_count": 0,
        },
    }

    (run_dir / "execution_plan_summary.json").write_text(
        json.dumps(summary),
        encoding="utf-8",
    )


def test_normalize_run_dir_confirmation_value_preserves_relative_path():
    value = normalize_run_dir_confirmation_value("reports/paper_trading_dry_runs/latest")
    assert value == "reports/paper_trading_dry_runs/latest"


def test_submit_run_dir_confirmation_allows_exact_match():
    assert_submit_run_dir_confirmed(
        run_dir="reports/paper_trading_dry_runs/v1_19_single_order_AMD_buy",
        confirm_run_dir="reports/paper_trading_dry_runs/v1_19_single_order_AMD_buy",
    )


def test_submit_run_dir_confirmation_blocks_missing_confirmation():
    with pytest.raises(ValueError, match="requires explicit run-dir confirmation"):
        assert_submit_run_dir_confirmed(
            run_dir="reports/paper_trading_dry_runs/latest",
            confirm_run_dir=None,
        )


def test_submit_run_dir_confirmation_blocks_mismatch():
    with pytest.raises(ValueError, match="confirmation mismatch"):
        assert_submit_run_dir_confirmed(
            run_dir="reports/paper_trading_dry_runs/v1_19_single_order_AMD_buy",
            confirm_run_dir="reports/paper_trading_dry_runs/latest",
        )


def test_run_paper_order_plan_submit_mode_requires_confirmed_run_dir(tmp_path):
    _write_hold_only_plan(tmp_path)

    with pytest.raises(ValueError, match="requires explicit run-dir confirmation"):
        run_paper_order_plan(
            run_dir=tmp_path,
            submit_orders=True,
            trading_client=object(),
            max_plan_age_minutes=90,
        )


def test_run_paper_order_plan_submit_mode_accepts_confirmed_run_dir(tmp_path):
    _write_hold_only_plan(tmp_path)

    results, summary = run_paper_order_plan(
        run_dir=tmp_path,
        submit_orders=True,
        trading_client=object(),
        max_plan_age_minutes=1_000_000_000,
        confirm_run_dir=tmp_path,
    )

    assert summary["submit_orders"] is True
    assert summary["orders_required"] == 0
    assert summary["orders_submitted"] == 0
    assert summary["confirmed_run_dir"] == str(tmp_path)
    assert len(results) == 1
