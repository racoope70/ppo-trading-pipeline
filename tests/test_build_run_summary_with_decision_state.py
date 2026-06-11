from __future__ import annotations

import json
from pathlib import Path

from src.paper_trading.build_run_summary_with_decision_state import (
    build_run_summary,
    write_run_summary,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_run_summary_includes_decision_state(tmp_path: Path) -> None:
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

    _write_json(
        run_dir / "decision_state_report.json",
        {
            "state": "NO_CANDIDATE_HOLD",
            "decision": "NO_SUBMIT",
            "reason": "No eligible order rows were present.",
            "orders_required": 0,
            "buy_count": 0,
            "sell_count": 0,
            "candidates": [],
            "submit_allowed": False,
        },
    )

    summary = build_run_summary(run_dir)

    assert summary["artifacts_present"]["decision_state_report"] is True
    assert summary["decision_state"]["state"] == "NO_CANDIDATE_HOLD"
    assert summary["decision_state"]["decision"] == "NO_SUBMIT"
    assert summary["safe_default"]["submit_allowed"] is False
    assert summary["execution_plan"]["orders_required"] == 0


def test_write_run_summary_writes_json_artifact(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    _write_json(
        run_dir / "decision_state_report.json",
        {
            "state": "NO_CANDIDATE_HOLD",
            "decision": "NO_SUBMIT",
            "reason": "No eligible order rows were present.",
            "orders_required": 0,
            "buy_count": 0,
            "sell_count": 0,
            "candidates": [],
            "submit_allowed": False,
        },
    )

    output_path = write_run_summary(run_dir)

    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["decision_state"]["state"] == "NO_CANDIDATE_HOLD"
    assert payload["safe_default"]["decision"] == "NO_SUBMIT"
