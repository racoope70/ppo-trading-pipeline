from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from src.paper_trading.pipeline_decision_state_hook import (
    write_post_checklist_decision_state_report,
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


def _base_run(tmp_path: Path, include_checklist: bool = True) -> Path:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    _write_json(
        run_dir / "dry_run_summary.json",
        {
            "rows": 6,
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
                "rows": 6,
                "orders_required": 0,
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

    if include_checklist:
        _write_json(
            run_dir / "pre_trade_checklist_report.json",
            {
                "result": "PASS",
                "orders_submitted": 0,
            },
        )

    return run_dir


def test_post_checklist_hook_writes_decision_state_report(tmp_path: Path) -> None:
    run_dir = _base_run(tmp_path, include_checklist=True)

    result, report_path = write_post_checklist_decision_state_report(
        run_dir=run_dir,
        prior_symbol="AMD",
        prior_side="buy",
    )

    assert result.state == "NO_CANDIDATE_HOLD"
    assert result.decision == "NO_SUBMIT"
    assert result.submit_allowed is False

    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["state"] == "NO_CANDIDATE_HOLD"
    assert payload["decision"] == "NO_SUBMIT"
    assert payload["submit_allowed"] is False


def test_post_checklist_hook_requires_checklist_by_default(tmp_path: Path) -> None:
    run_dir = _base_run(tmp_path, include_checklist=False)

    with pytest.raises(FileNotFoundError):
        write_post_checklist_decision_state_report(run_dir=run_dir)


def test_post_checklist_hook_can_allow_missing_checklist(tmp_path: Path) -> None:
    run_dir = _base_run(tmp_path, include_checklist=False)

    result, report_path = write_post_checklist_decision_state_report(
        run_dir=run_dir,
        require_checklist_report=False,
    )

    assert result.state == "NO_CANDIDATE_HOLD"
    assert report_path.exists()
