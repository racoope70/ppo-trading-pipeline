import json
from pathlib import Path

import pandas as pd
import pytest

from src.paper_trading.evaluate_dry_run import validate_dry_run


def _write_valid_dry_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "symbol": "AAPL",
                "selected_prefix": "ppo_AAPL_window1",
                "latest_bar_time": "2026-05-19T14:00:00+00:00",
                "raw_action": -1.0,
                "confidence": 1.0,
                "target_weight": 0.0,
                "actual_weight": 0.0,
                "intended_notional": 0.0,
                "dry_run": 1,
                "order_submitted": 0,
                "note": "dry_run_predict_ok",
            },
            {
                "symbol": "PFE",
                "selected_prefix": "ppo_PFE_window1",
                "latest_bar_time": "2026-05-19T14:00:00+00:00",
                "raw_action": 0.004,
                "confidence": 0.004,
                "target_weight": 0.0016,
                "actual_weight": 0.0,
                "intended_notional": 160.0,
                "dry_run": 1,
                "order_submitted": 0,
                "note": "dry_run_predict_ok",
            },
        ]
    )

    df.to_csv(run_dir / "dry_run_targets.csv", index=False)

    summary = {
        "rows": 2,
        "predict_ok_count": 2,
        "error_count": 0,
        "orders_submitted": 0,
    }

    (run_dir / "dry_run_summary.json").write_text(
        json.dumps(summary),
        encoding="utf-8",
    )


def _passed(checks, name: str) -> bool:
    matches = [check for check in checks if check.name == name]
    assert matches, f"Missing check {name}"
    return matches[0].passed


def test_validate_dry_run_passes_for_valid_outputs(tmp_path):
    _write_valid_dry_run(tmp_path)

    checks, df, summary = validate_dry_run(
        run_dir=tmp_path,
        expected_symbols=["AAPL", "PFE"],
        manifest_path=None,
    )

    assert not df.empty
    assert summary["orders_submitted"] == 0
    assert all(check.passed for check in checks)


def test_validate_dry_run_fails_when_order_submitted(tmp_path):
    _write_valid_dry_run(tmp_path)

    df = pd.read_csv(tmp_path / "dry_run_targets.csv")
    df.loc[0, "order_submitted"] = 1
    df.to_csv(tmp_path / "dry_run_targets.csv", index=False)

    checks, _, _ = validate_dry_run(
        run_dir=tmp_path,
        expected_symbols=["AAPL", "PFE"],
        manifest_path=None,
    )

    assert _passed(checks, "row_orders_submitted_zero") is False
    assert all(check.passed for check in checks) is False


def test_validate_dry_run_fails_on_error_note(tmp_path):
    _write_valid_dry_run(tmp_path)

    df = pd.read_csv(tmp_path / "dry_run_targets.csv")
    df.loc[1, "note"] = "dry_run_error: model failed"
    df.to_csv(tmp_path / "dry_run_targets.csv", index=False)

    checks, _, _ = validate_dry_run(
        run_dir=tmp_path,
        expected_symbols=["AAPL", "PFE"],
        manifest_path=None,
    )

    assert _passed(checks, "no_dry_run_errors") is False
    assert _passed(checks, "all_predict_ok") is False


def test_validate_dry_run_fails_on_missing_expected_symbol(tmp_path):
    _write_valid_dry_run(tmp_path)

    checks, _, _ = validate_dry_run(
        run_dir=tmp_path,
        expected_symbols=["AAPL", "PFE", "UNH"],
        manifest_path=None,
    )

    assert _passed(checks, "expected_symbols_present") is False
    assert _passed(checks, "one_row_per_expected_symbol") is False


def test_validate_dry_run_fails_when_summary_orders_nonzero(tmp_path):
    _write_valid_dry_run(tmp_path)

    summary_path = tmp_path / "dry_run_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["orders_submitted"] = 1
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    checks, _, _ = validate_dry_run(
        run_dir=tmp_path,
        expected_symbols=["AAPL", "PFE"],
        manifest_path=None,
    )

    assert _passed(checks, "summary_orders_submitted_zero") is False
