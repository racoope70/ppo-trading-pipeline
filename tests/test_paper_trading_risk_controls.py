import json
from pathlib import Path

import pandas as pd
import pytest

from src.paper_trading.risk_controls import (
    RiskContext,
    RiskControlConfig,
    assert_risk_report_passes,
    evaluate_execution_plan_risk,
    load_execution_plan_for_risk,
)


def _sample_plan() -> pd.DataFrame:
    return pd.DataFrame(
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
                "should_order": True,
                "order_submitted": False,
                "latest_bar_time": "2026-05-20T14:00:00+00:00",
            },
            {
                "symbol": "XOM",
                "side": "buy",
                "qty": 22.15,
                "price": 162.61,
                "equity": 100_000.0,
                "target_weight": 0.0384,
                "actual_weight": 0.0,
                "target_notional": 3_840.0,
                "actual_notional": 0.0,
                "delta_notional": 3_840.0,
                "should_order": True,
                "order_submitted": False,
                "latest_bar_time": "2026-05-20T14:00:00+00:00",
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
                "should_order": False,
                "order_submitted": False,
                "latest_bar_time": "2026-05-20T14:00:00+00:00",
            },
        ]
    )


def _sample_summary() -> dict:
    return {
        "orders_submitted": 0,
        "execution_plan": {
            "rows": 3,
            "orders_required": 2,
        },
    }


def _check(report, name: str):
    matches = [check for check in report.checks if check.name == name]
    assert matches, f"Missing check {name}"
    return matches[0]


def test_evaluate_execution_plan_risk_passes_for_clean_plan():
    report = evaluate_execution_plan_risk(
        _sample_plan(),
        _sample_summary(),
        config=RiskControlConfig(require_flat_start=True),
        context=RiskContext(
            account_equity=100_000.0,
            positions_count=0,
            open_orders_count=0,
        ),
    )

    assert report.passed is True
    assert_risk_report_passes(report)


def test_risk_fails_when_single_symbol_weight_too_large():
    plan = _sample_plan()
    plan.loc[0, "target_weight"] = 0.60

    report = evaluate_execution_plan_risk(
        plan,
        _sample_summary(),
        config=RiskControlConfig(max_abs_symbol_weight=0.40),
    )

    assert report.passed is False
    assert _check(report, "single_symbol_target_weight_within_limit").passed is False


def test_risk_fails_when_gross_exposure_too_large():
    plan = _sample_plan()
    plan.loc[0, "target_weight"] = 0.60
    plan.loc[1, "target_weight"] = 0.60

    report = evaluate_execution_plan_risk(
        plan,
        _sample_summary(),
        config=RiskControlConfig(max_abs_symbol_weight=1.0, max_gross_target_weight=1.0),
    )

    assert report.passed is False
    assert _check(report, "gross_target_weight_within_limit").passed is False


def test_risk_fails_when_prior_order_submitted_flag_exists():
    plan = _sample_plan()
    plan.loc[0, "order_submitted"] = True

    report = evaluate_execution_plan_risk(plan, _sample_summary())

    assert report.passed is False
    assert _check(report, "no_prior_order_submitted_flags").passed is False


def test_risk_fails_when_open_orders_exist_in_context():
    report = evaluate_execution_plan_risk(
        _sample_plan(),
        _sample_summary(),
        context=RiskContext(open_orders_count=2),
    )

    assert report.passed is False
    assert _check(report, "no_open_orders_in_account").passed is False


def test_risk_fails_when_flat_start_required_but_actual_weight_exists():
    plan = _sample_plan()
    plan.loc[0, "actual_weight"] = 0.05

    report = evaluate_execution_plan_risk(
        plan,
        _sample_summary(),
        config=RiskControlConfig(require_flat_start=True),
        context=RiskContext(positions_count=1),
    )

    assert report.passed is False
    assert _check(report, "account_positions_flat").passed is False
    assert _check(report, "plan_actual_weights_flat").passed is False


def test_risk_fails_when_plan_is_stale():
    report = evaluate_execution_plan_risk(
        _sample_plan(),
        _sample_summary(),
        config=RiskControlConfig(max_plan_age_minutes=30),
        context=RiskContext(now_utc="2026-05-20T16:00:00+00:00"),
    )

    assert report.passed is False
    assert _check(report, "plan_not_stale").passed is False


def test_load_execution_plan_for_risk_reads_files(tmp_path):
    plan = _sample_plan()
    summary = _sample_summary()

    plan.to_csv(tmp_path / "execution_plan.csv", index=False)
    (tmp_path / "execution_plan_summary.json").write_text(
        json.dumps(summary),
        encoding="utf-8",
    )

    loaded_plan, loaded_summary = load_execution_plan_for_risk(tmp_path)

    assert len(loaded_plan) == 3
    assert loaded_summary["orders_submitted"] == 0


def test_assert_risk_report_passes_raises_on_failure():
    plan = _sample_plan()
    plan.loc[0, "target_weight"] = 0.60

    report = evaluate_execution_plan_risk(
        plan,
        _sample_summary(),
        config=RiskControlConfig(max_abs_symbol_weight=0.40),
    )

    with pytest.raises(RuntimeError, match="Risk controls failed"):
        assert_risk_report_passes(report)
