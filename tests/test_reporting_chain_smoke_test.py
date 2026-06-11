from __future__ import annotations

import csv
import json
from pathlib import Path

from src.paper_trading.reporting_chain_smoke_test import (
    run_reporting_chain_smoke_test,
)


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


def _base_reporting_run(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    _write_json(
        run_dir / "dry_run_summary.json",
        {
            "datetime_utc": "2026-06-10T16:09:18+00:00",
            "predict_ok_count": 6,
            "error_count": 0,
            "orders_submitted": 0,
        },
    )

    _write_json(
        run_dir / "execution_plan_summary.json",
        {
            "orders_submitted": 0,
            "execution_plan": {
                "orders_required": 0,
                "gross_intended_notional": 0.0,
                "buy_count": 0,
                "sell_count": 0,
            },
        },
    )

    _write_plan_csv(
        run_dir / "execution_plan.csv",
        [
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

    _write_json(
        run_dir / "paper_order_run_summary.json",
        {
            "orders_required": 0,
            "orders_submitted": 0,
            "submit_orders": False,
            "risk_passed": True,
        },
    )

    _write_json(
        run_dir / "pre_trade_checklist_report.json",
        {
            "result": "PASS",
        },
    )

    return run_dir


def test_reporting_chain_smoke_test_writes_all_artifacts(tmp_path: Path) -> None:
    run_dir = _base_reporting_run(tmp_path)
    dashboard_path = tmp_path / "dashboard.md"

    result, smoke_report_path = run_reporting_chain_smoke_test(
        run_dir=run_dir,
        prior_symbol="AMD",
        prior_side="buy",
        dashboard_path=dashboard_path,
    )

    assert result.passed is True
    assert result.state == "NO_CANDIDATE_HOLD"
    assert result.decision == "NO_SUBMIT"
    assert result.orders_required == 0
    assert result.submit_allowed is False

    assert (run_dir / "decision_state_report.json").exists()
    assert (run_dir / "paper_trading_run_summary.json").exists()
    assert dashboard_path.exists()
    assert smoke_report_path.exists()

    payload = json.loads(smoke_report_path.read_text(encoding="utf-8"))
    assert payload["passed"] is True
    assert payload["state"] == "NO_CANDIDATE_HOLD"
    assert payload["decision"] == "NO_SUBMIT"

    dashboard_text = dashboard_path.read_text(encoding="utf-8")
    assert "NO_CANDIDATE_HOLD" in dashboard_text
    assert "NO_SUBMIT" in dashboard_text
