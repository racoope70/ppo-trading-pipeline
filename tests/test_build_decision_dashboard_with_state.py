from __future__ import annotations

import json
from pathlib import Path

from src.paper_trading.build_decision_dashboard_with_state import (
    build_dashboard_rows,
    render_markdown_dashboard,
    write_dashboard,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_dashboard_rows_include_decision_state_from_run_summary(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    _write_json(
        run_dir / "paper_trading_run_summary.json",
        {
            "dry_run": {"datetime_utc": "2026-06-10T16:09:18+00:00"},
            "execution_plan": {
                "orders_required": 0,
                "buy_count": 0,
                "sell_count": 0,
            },
            "paper_order_run": {
                "orders_submitted": 0,
                "risk_passed": True,
            },
            "safe_default": {
                "decision": "NO_SUBMIT",
                "submit_allowed": False,
            },
            "decision_state": {
                "state": "NO_CANDIDATE_HOLD",
                "decision": "NO_SUBMIT",
                "reason": "No eligible order rows were present.",
                "orders_required": 0,
                "buy_count": 0,
                "sell_count": 0,
                "candidates": [],
                "submit_allowed": False,
            },
        },
    )

    rows = build_dashboard_rows([run_dir])

    assert len(rows) == 1
    assert rows[0]["state"] == "NO_CANDIDATE_HOLD"
    assert rows[0]["decision"] == "NO_SUBMIT"
    assert rows[0]["orders_required"] == 0
    assert rows[0]["submit_allowed"] is False


def test_dashboard_falls_back_to_decision_state_report(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    _write_json(
        run_dir / "decision_state_report.json",
        {
            "state": "MULTI_ORDER_PLAN",
            "decision": "NO_SUBMIT",
            "reason": "Fresh execution plan contains more than one eligible order.",
            "orders_required": 2,
            "buy_count": 1,
            "sell_count": 1,
            "candidates": [],
            "submit_allowed": False,
        },
    )

    rows = build_dashboard_rows([run_dir])

    assert rows[0]["state"] == "MULTI_ORDER_PLAN"
    assert rows[0]["decision"] == "NO_SUBMIT"
    assert rows[0]["orders_required"] == 2
    assert rows[0]["submit_allowed"] is False


def test_render_markdown_dashboard_contains_state_and_decision() -> None:
    markdown = render_markdown_dashboard(
        [
            {
                "run_dir": "reports/paper_trading_dry_runs/latest",
                "state": "NO_CANDIDATE_HOLD",
                "decision": "NO_SUBMIT",
                "reason": "No eligible order rows were present.",
                "orders_required": 0,
                "buy_count": 0,
                "sell_count": 0,
                "submit_allowed": False,
                "orders_submitted": 0,
                "risk_passed": True,
            }
        ]
    )

    assert "NO_CANDIDATE_HOLD" in markdown
    assert "NO_SUBMIT" in markdown
    assert "Submit Allowed" in markdown


def test_write_dashboard_creates_markdown_file(tmp_path: Path) -> None:
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

    output_path = tmp_path / "dashboard.md"
    write_dashboard([run_dir], output_path)

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "NO_CANDIDATE_HOLD" in content
    assert "NO_SUBMIT" in content
