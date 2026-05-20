import json
from pathlib import Path

import pandas as pd
import pytest

from src.paper_trading.build_execution_plan import (
    build_execution_plan,
    load_dry_run_outputs,
    validate_dry_run_is_safe,
    write_execution_plan,
)
from src.paper_trading.execution import ExecutionConfig


def _write_dry_run_outputs(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    targets = pd.DataFrame(
        [
            {
                "symbol": "AMD",
                "selected_prefix": "ppo_AMD_window3",
                "latest_bar_time": "2026-05-20T00:00:00+00:00",
                "latest_price": 100.0,
                "equity": 100_000.0,
                "raw_action": 0.50,
                "confidence": 0.50,
                "target_weight": 0.20,
                "actual_qty": 0.0,
                "actual_market_value": 0.0,
                "actual_weight": 0.0,
                "intended_notional": 20_000.0,
                "dry_run": 1,
                "order_submitted": 0,
                "note": "dry_run_predict_ok",
            },
            {
                "symbol": "PFE",
                "selected_prefix": "ppo_PFE_window1",
                "latest_bar_time": "2026-05-20T00:00:00+00:00",
                "latest_price": 50.0,
                "equity": 100_000.0,
                "raw_action": 0.0001,
                "confidence": 0.0001,
                "target_weight": 0.0001,
                "actual_qty": 0.0,
                "actual_market_value": 0.0,
                "actual_weight": 0.0,
                "intended_notional": 10.0,
                "dry_run": 1,
                "order_submitted": 0,
                "note": "dry_run_predict_ok",
            },
        ]
    )

    targets.to_csv(run_dir / "dry_run_targets.csv", index=False)

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


def test_load_dry_run_outputs_reads_files(tmp_path):
    _write_dry_run_outputs(tmp_path)

    targets, summary = load_dry_run_outputs(tmp_path)

    assert len(targets) == 2
    assert summary["orders_submitted"] == 0


def test_validate_dry_run_is_safe_passes_for_clean_outputs(tmp_path):
    _write_dry_run_outputs(tmp_path)

    targets, summary = load_dry_run_outputs(tmp_path)

    validate_dry_run_is_safe(targets, summary)


def test_validate_dry_run_is_safe_fails_when_orders_submitted(tmp_path):
    _write_dry_run_outputs(tmp_path)

    targets, summary = load_dry_run_outputs(tmp_path)
    summary["orders_submitted"] = 1

    with pytest.raises(ValueError, match="orders were submitted"):
        validate_dry_run_is_safe(targets, summary)


def test_validate_dry_run_is_safe_fails_on_error_note(tmp_path):
    _write_dry_run_outputs(tmp_path)

    targets, summary = load_dry_run_outputs(tmp_path)
    targets.loc[0, "note"] = "dry_run_error: failed"

    with pytest.raises(ValueError, match="dry_run_error"):
        validate_dry_run_is_safe(targets, summary)


def test_build_execution_plan_creates_buy_and_hold_intents(tmp_path):
    _write_dry_run_outputs(tmp_path)

    plan, summary = build_execution_plan(
        run_dir=tmp_path,
        config=ExecutionConfig(
            min_notional=25.0,
            max_abs_weight=0.40,
            allow_shorts=False,
            use_fractionals=True,
            qty_precision=6,
            dry_run=True,
        ),
    )

    by_symbol = {row["symbol"]: row for _, row in plan.iterrows()}

    assert by_symbol["AMD"]["side"] == "buy"
    assert by_symbol["AMD"]["should_order"] is True
    assert by_symbol["AMD"]["qty"] == 200.0
    assert by_symbol["AMD"]["execution_note"] == "execution_plan_only_no_order_submitted"

    assert by_symbol["PFE"]["side"] == "hold"
    assert by_symbol["PFE"]["should_order"] is False
    assert by_symbol["PFE"]["reason"] == "below_min_notional"

    assert summary["orders_submitted"] == 0
    assert summary["execution_plan"]["rows"] == 2
    assert summary["execution_plan"]["orders_required"] == 1


def test_write_execution_plan_outputs_files(tmp_path):
    _write_dry_run_outputs(tmp_path)

    plan, summary = build_execution_plan(
        run_dir=tmp_path,
        config=ExecutionConfig(min_notional=25.0, dry_run=True),
    )

    out_dir = tmp_path / "plan"
    plan_path, summary_path = write_execution_plan(plan, summary, out_dir)

    assert plan_path.exists()
    assert summary_path.exists()

    written = pd.read_csv(plan_path)
    written_summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert len(written) == 2
    assert written_summary["orders_submitted"] == 0
