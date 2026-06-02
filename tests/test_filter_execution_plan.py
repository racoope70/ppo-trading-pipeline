import json
from pathlib import Path

import pandas as pd
import pytest

from src.paper_trading.filter_execution_plan import (
    filter_to_single_order,
    run_single_order_filter,
    summarize_filtered_plan,
)


def _sample_plan():
    return pd.DataFrame(
        [
            {
                "symbol": "AAPL",
                "side": "hold",
                "qty": 0.0,
                "price": 100.0,
                "equity": 100000.0,
                "target_weight": 0.0,
                "actual_weight": 0.0,
                "target_notional": 0.0,
                "actual_notional": 0.0,
                "delta_notional": 0.0,
                "min_notional": 25.0,
                "max_abs_weight": 0.4,
                "should_order": False,
                "reason": "below_min_notional",
                "dry_run": True,
                "selected_prefix": "ppo_AAPL_window1",
                "raw_action": -0.01,
                "confidence": 0.01,
                "latest_bar_time": "2026-06-02T16:00:00+00:00",
                "note": "dry_run_predict_ok",
                "order_submitted": False,
                "execution_note": "below_min_notional",
            },
            {
                "symbol": "AMD",
                "side": "buy",
                "qty": 0.461577,
                "price": 516.49,
                "equity": 100000.0,
                "target_weight": 0.004,
                "actual_weight": 0.002,
                "target_notional": 400.0,
                "actual_notional": 200.0,
                "delta_notional": 238.40,
                "min_notional": 25.0,
                "max_abs_weight": 0.4,
                "should_order": True,
                "reason": "rebalance_required",
                "dry_run": True,
                "selected_prefix": "ppo_AMD_window14",
                "raw_action": 0.01,
                "confidence": 0.01,
                "latest_bar_time": "2026-06-02T16:00:00+00:00",
                "note": "dry_run_predict_ok",
                "order_submitted": False,
                "execution_note": "execution_plan_only_no_order_submitted",
            },
            {
                "symbol": "UNH",
                "side": "buy",
                "qty": 0.213447,
                "price": 376.725,
                "equity": 100000.0,
                "target_weight": 0.001,
                "actual_weight": 0.0,
                "target_notional": 100.0,
                "actual_notional": 0.0,
                "delta_notional": 80.41,
                "min_notional": 25.0,
                "max_abs_weight": 0.4,
                "should_order": True,
                "reason": "rebalance_required",
                "dry_run": True,
                "selected_prefix": "ppo_UNH_window20",
                "raw_action": 0.002,
                "confidence": 0.002,
                "latest_bar_time": "2026-06-02T16:00:00+00:00",
                "note": "dry_run_predict_ok",
                "order_submitted": False,
                "execution_note": "execution_plan_only_no_order_submitted",
            },
        ]
    )


def _sample_summary():
    return {
        "source_run_dir": "reports/paper_trading_dry_runs/latest",
        "output_dir": "reports/paper_trading_dry_runs/latest",
        "orders_submitted": 0,
        "dry_run_summary": {
            "rows": 3,
            "predict_ok_count": 3,
            "error_count": 0,
            "orders_submitted": 0,
        },
        "execution_config": {
            "min_notional": 25.0,
            "max_abs_weight": 0.4,
            "allow_shorts": False,
            "use_fractionals": True,
            "qty_precision": 6,
            "dry_run": True,
        },
        "execution_plan": {
            "rows": 3,
            "orders_required": 2,
            "gross_intended_notional": 318.81,
            "buy_count": 2,
            "sell_count": 0,
        },
    }


def test_filter_to_single_order_keeps_only_selected_order():
    filtered, metadata = filter_to_single_order(
        _sample_plan(),
        symbol="AMD",
        side="buy",
    )

    order_rows = filtered[filtered["should_order"].astype(bool)]
    assert len(order_rows) == 1
    assert order_rows.iloc[0]["symbol"] == "AMD"
    assert order_rows.iloc[0]["side"] == "buy"
    assert metadata["disabled_order_count"] == 1

    unh = filtered[filtered["symbol"] == "UNH"].iloc[0]
    assert unh["side"] == "hold"
    assert float(unh["qty"]) == 0.0
    assert bool(unh["should_order"]) is False
    assert unh["reason"] == "filtered_out_by_single_order_guard"


def test_filtered_plan_summary_has_one_required_order():
    filtered, _ = filter_to_single_order(
        _sample_plan(),
        symbol="AMD",
    )
    summary = summarize_filtered_plan(filtered)

    assert summary["orders_required"] == 1
    assert summary["buy_count"] == 1
    assert summary["sell_count"] == 0
    assert summary["gross_intended_notional"] == pytest.approx(238.40)


def test_filter_rejects_missing_selected_order():
    with pytest.raises(ValueError, match="Expected exactly one selected order"):
        filter_to_single_order(
            _sample_plan(),
            symbol="PFE",
            side="buy",
        )


def test_run_single_order_filter_writes_outputs(tmp_path):
    source = tmp_path / "source"
    output = tmp_path / "filtered"
    source.mkdir(parents=True)

    _sample_plan().to_csv(source / "execution_plan.csv", index=False)
    (source / "execution_plan_summary.json").write_text(
        json.dumps(_sample_summary()),
        encoding="utf-8",
    )
    (source / "dry_run_targets.csv").write_text("symbol\nAMD\n", encoding="utf-8")
    (source / "dry_run_summary.json").write_text(
        json.dumps({"rows": 3, "orders_submitted": 0, "error_count": 0}),
        encoding="utf-8",
    )

    result = run_single_order_filter(
        run_dir=source,
        output_dir=output,
        symbol="AMD",
        side="buy",
    )

    assert result["orders_required"] == 1
    assert (output / "execution_plan.csv").exists()
    assert (output / "execution_plan_summary.json").exists()
    assert (output / "single_order_filter_summary.json").exists()
    assert (output / "dry_run_targets.csv").exists()
    assert (output / "dry_run_summary.json").exists()

    summary = json.loads((output / "execution_plan_summary.json").read_text())
    assert summary["execution_plan"]["orders_required"] == 1
    assert summary["single_order_filter"]["selected_symbol"] == "AMD"
