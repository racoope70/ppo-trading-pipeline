import json
from pathlib import Path

import pandas as pd
import pytest

from src.paper_trading.pre_trade_checklist import (
    PreTradeChecklistConfig,
    assert_checklist_passes,
    evaluate_pre_trade_checklist,
    write_checklist_report,
)


def _write_safe_outputs(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        [
            {"symbol": "AMD", "note": "dry_run_predict_ok"},
            {"symbol": "XOM", "note": "dry_run_predict_ok"},
        ]
    ).to_csv(run_dir / "dry_run_targets.csv", index=False)

    (run_dir / "dry_run_summary.json").write_text(
        json.dumps(
            {
                "rows": 2,
                "predict_ok_count": 2,
                "error_count": 0,
                "orders_submitted": 0,
            }
        ),
        encoding="utf-8",
    )

    pd.DataFrame(
        [
            {
                "symbol": "AMD",
                "should_order": True,
                "order_submitted": False,
            },
            {
                "symbol": "XOM",
                "should_order": False,
                "order_submitted": False,
            },
        ]
    ).to_csv(run_dir / "execution_plan.csv", index=False)

    (run_dir / "execution_plan_summary.json").write_text(
        json.dumps(
            {
                "orders_submitted": 0,
                "execution_plan": {
                    "rows": 2,
                    "orders_required": 1,
                },
            }
        ),
        encoding="utf-8",
    )

    pd.DataFrame(
        [
            {
                "symbol": "AMD",
                "should_order": True,
                "order_submitted": False,
                "risk_passed": True,
            },
            {
                "symbol": "XOM",
                "should_order": False,
                "order_submitted": False,
                "risk_passed": True,
            },
        ]
    ).to_csv(run_dir / "paper_order_run.csv", index=False)

    (run_dir / "paper_order_run_summary.json").write_text(
        json.dumps(
            {
                "rows": 2,
                "orders_required": 1,
                "orders_submitted": 0,
                "submit_orders": False,
                "risk_passed": True,
            }
        ),
        encoding="utf-8",
    )

    (run_dir / "paper_trade_audit_log.json").write_text(
        json.dumps(
            {
                "audit_type": "paper_trading_run",
                "orders_required": 1,
                "orders_submitted": 0,
                "submit_orders": False,
                "risk_passed": True,
            }
        ),
        encoding="utf-8",
    )


def _flat_broker_state() -> dict:
    return {
        "account": {
            "equity": "100000",
            "cash": "100000",
            "status": "ACTIVE",
        },
        "positions": [],
        "open_orders": [],
        "positions_count": 0,
        "open_orders_count": 0,
        "errors": [],
    }


def test_pre_trade_checklist_passes_for_safe_outputs(tmp_path):
    _write_safe_outputs(tmp_path)

    report = evaluate_pre_trade_checklist(run_dir=tmp_path)

    assert report.passed is True
    assert_checklist_passes(report)


def test_pre_trade_checklist_writes_report(tmp_path):
    _write_safe_outputs(tmp_path)

    report = evaluate_pre_trade_checklist(run_dir=tmp_path)
    output_path = write_checklist_report(report, tmp_path)

    assert output_path.exists()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["passed"] is True


def test_pre_trade_checklist_fails_without_audit_log(tmp_path):
    _write_safe_outputs(tmp_path)
    (tmp_path / "paper_trade_audit_log.json").unlink()

    report = evaluate_pre_trade_checklist(run_dir=tmp_path)

    assert report.passed is False
    failing_names = [check.name for check in report.checks if not check.passed]
    assert "paper_trade_audit_log.json_exists" in failing_names


def test_pre_trade_checklist_fails_when_risk_not_passed(tmp_path):
    _write_safe_outputs(tmp_path)

    (tmp_path / "paper_order_run_summary.json").write_text(
        json.dumps(
            {
                "rows": 2,
                "orders_required": 1,
                "orders_submitted": 0,
                "submit_orders": False,
                "risk_passed": False,
            }
        ),
        encoding="utf-8",
    )

    report = evaluate_pre_trade_checklist(run_dir=tmp_path)

    assert report.passed is False
    failing_names = [check.name for check in report.checks if not check.passed]
    assert "paper_order_risk_passed" in failing_names


def test_pre_trade_checklist_fails_when_orders_submitted(tmp_path):
    _write_safe_outputs(tmp_path)

    (tmp_path / "paper_order_run_summary.json").write_text(
        json.dumps(
            {
                "rows": 2,
                "orders_required": 1,
                "orders_submitted": 1,
                "submit_orders": True,
                "risk_passed": True,
            }
        ),
        encoding="utf-8",
    )

    report = evaluate_pre_trade_checklist(run_dir=tmp_path)

    assert report.passed is False
    failing_names = [check.name for check in report.checks if not check.passed]
    assert "paper_order_summary_orders_submitted_zero" in failing_names
    assert "paper_order_summary_no_order_mode" in failing_names


def test_pre_trade_checklist_broker_state_passes_when_flat(tmp_path):
    _write_safe_outputs(tmp_path)

    report = evaluate_pre_trade_checklist(
        run_dir=tmp_path,
        broker_state=_flat_broker_state(),
    )

    assert report.passed is True


def test_pre_trade_checklist_broker_state_fails_when_position_open(tmp_path):
    _write_safe_outputs(tmp_path)

    broker_state = _flat_broker_state()
    broker_state["positions_count"] = 1
    broker_state["positions"] = [{"symbol": "AMD", "qty": "10"}]

    report = evaluate_pre_trade_checklist(
        run_dir=tmp_path,
        broker_state=broker_state,
    )

    assert report.passed is False
    failing_names = [check.name for check in report.checks if not check.passed]
    assert "broker_positions_flat" in failing_names


def test_pre_trade_checklist_broker_state_fails_when_equity_far_from_expected(tmp_path):
    _write_safe_outputs(tmp_path)

    broker_state = _flat_broker_state()
    broker_state["account"]["equity"] = "90000"

    report = evaluate_pre_trade_checklist(
        run_dir=tmp_path,
        config=PreTradeChecklistConfig(
            expected_equity=100_000.0,
            equity_tolerance_pct=0.02,
        ),
        broker_state=broker_state,
    )

    assert report.passed is False
    failing_names = [check.name for check in report.checks if not check.passed]
    assert "broker_equity_near_expected" in failing_names


def test_assert_checklist_passes_raises_on_failure(tmp_path):
    _write_safe_outputs(tmp_path)
    (tmp_path / "paper_trade_audit_log.json").unlink()

    report = evaluate_pre_trade_checklist(run_dir=tmp_path)

    with pytest.raises(RuntimeError, match="Pre-trade checklist failed"):
        assert_checklist_passes(report)
