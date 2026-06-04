import json
from pathlib import Path

import pandas as pd
import pytest

from src.paper_trading.paper_trade_loop import run_paper_order_plan
from src.paper_trading.pre_trade_checklist import (
    PreTradeChecklistConfig,
    evaluate_pre_trade_checklist,
)
from src.paper_trading.risk_controls import (
    RiskContext,
    RiskControlConfig,
    evaluate_execution_plan_risk,
)


def _plan_with_latest_bar(latest_bar_time: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": "AMD",
                "side": "buy",
                "qty": 1.0,
                "price": 100.0,
                "equity": 100_000.0,
                "target_weight": 0.001,
                "actual_weight": 0.0,
                "target_notional": 100.0,
                "actual_notional": 0.0,
                "delta_notional": 100.0,
                "min_notional": 25.0,
                "max_abs_weight": 0.40,
                "should_order": True,
                "reason": "rebalance_required",
                "dry_run": True,
                "selected_prefix": "ppo_AMD_window14",
                "raw_action": 0.01,
                "confidence": 0.01,
                "latest_bar_time": latest_bar_time,
                "note": "dry_run_predict_ok",
                "order_submitted": False,
                "execution_note": "execution_plan_only_no_order_submitted",
            }
        ]
    )


def _summary() -> dict:
    return {
        "orders_submitted": 0,
        "execution_plan": {
            "rows": 1,
            "orders_required": 1,
            "gross_intended_notional": 100.0,
            "buy_count": 1,
            "sell_count": 0,
        },
    }


def _write_run_dir(run_dir: Path, latest_bar_time: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    plan = _plan_with_latest_bar(latest_bar_time)
    plan.to_csv(run_dir / "execution_plan.csv", index=False)

    (run_dir / "execution_plan_summary.json").write_text(
        json.dumps(_summary()),
        encoding="utf-8",
    )

    plan.to_csv(run_dir / "dry_run_targets.csv", index=False)

    (run_dir / "dry_run_summary.json").write_text(
        json.dumps(
            {
                "rows": 1,
                "predict_ok_count": 1,
                "error_count": 0,
                "orders_submitted": 0,
            }
        ),
        encoding="utf-8",
    )

    (run_dir / "paper_order_run.csv").write_text(
        "symbol,order_submitted\nAMD,False\n",
        encoding="utf-8",
    )

    (run_dir / "paper_order_run_summary.json").write_text(
        json.dumps(
            {
                "orders_submitted": 0,
                "orders_required": 1,
                "submit_orders": False,
                "risk_passed": True,
            }
        ),
        encoding="utf-8",
    )

    (run_dir / "paper_trade_audit_log.json").write_text(
        json.dumps(
            {
                "orders_submitted": 0,
                "submit_orders": False,
                "risk_passed": True,
            }
        ),
        encoding="utf-8",
    )


def _check(report, name: str):
    return next(check for check in report.checks if check.name == name)


def test_risk_controls_pass_fresh_plan_with_max_plan_age():
    plan = _plan_with_latest_bar("2026-06-04T14:00:00+00:00")

    report = evaluate_execution_plan_risk(
        plan,
        _summary(),
        config=RiskControlConfig(max_plan_age_minutes=90),
        context=RiskContext(now_utc="2026-06-04T14:30:00+00:00"),
    )

    check = _check(report, "plan_not_stale")
    assert check.passed is True
    assert report.passed is True


def test_risk_controls_fail_stale_plan_with_max_plan_age():
    plan = _plan_with_latest_bar("2026-06-04T14:00:00+00:00")

    report = evaluate_execution_plan_risk(
        plan,
        _summary(),
        config=RiskControlConfig(max_plan_age_minutes=30),
        context=RiskContext(now_utc="2026-06-04T15:01:00+00:00"),
    )

    check = _check(report, "plan_not_stale")
    assert check.passed is False
    assert report.passed is False


def test_paper_trade_loop_blocks_stale_submit_before_orders(tmp_path):
    _write_run_dir(tmp_path, "2026-06-04T14:00:00+00:00")

    with pytest.raises(RuntimeError, match="Risk controls failed"):
        run_paper_order_plan(
            run_dir=tmp_path,
            submit_orders=True,
            trading_client=object(),
            risk_config=RiskControlConfig(max_plan_age_minutes=30),
            max_plan_age_minutes=30,
        )


def test_pre_trade_checklist_fails_stale_execution_plan(tmp_path):
    _write_run_dir(tmp_path, "2000-01-01T14:00:00+00:00")

    report = evaluate_pre_trade_checklist(
        run_dir=tmp_path,
        config=PreTradeChecklistConfig(max_plan_age_minutes=30),
    )

    check = _check(report, "execution_plan_not_stale")
    assert check.passed is False
    assert report.passed is False
