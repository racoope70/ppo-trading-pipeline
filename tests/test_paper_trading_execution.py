import pandas as pd

from src.paper_trading.execution import (
    ExecutionConfig,
    build_rebalance_intent,
    build_rebalance_intents_from_targets,
    clamp_target_weight,
    execute_rebalance_intent,
    summarize_intents,
)


def test_clamp_target_weight_blocks_shorts_by_default():
    assert clamp_target_weight(-0.25, max_abs_weight=0.40, allow_shorts=False) == 0.0


def test_clamp_target_weight_allows_shorts_when_enabled():
    assert clamp_target_weight(-0.25, max_abs_weight=0.40, allow_shorts=True) == -0.25


def test_clamp_target_weight_caps_large_positive_weight():
    assert clamp_target_weight(0.90, max_abs_weight=0.40, allow_shorts=False) == 0.40


def test_build_rebalance_intent_buy_required():
    intent = build_rebalance_intent(
        symbol="AMD",
        target_weight=0.20,
        actual_qty=0.0,
        price=100.0,
        equity=100_000.0,
        config=ExecutionConfig(min_notional=25.0, dry_run=True),
    )

    assert intent.symbol == "AMD"
    assert intent.side == "buy"
    assert intent.should_order is True
    assert intent.qty == 200.0
    assert intent.reason == "rebalance_required"
    assert intent.dry_run is True


def test_build_rebalance_intent_sell_required():
    intent = build_rebalance_intent(
        symbol="XOM",
        target_weight=0.05,
        actual_qty=100.0,
        price=100.0,
        equity=100_000.0,
        config=ExecutionConfig(min_notional=25.0, dry_run=True),
    )

    assert intent.side == "sell"
    assert intent.should_order is True
    assert intent.qty == 50.0
    assert intent.reason == "rebalance_required"


def test_build_rebalance_intent_below_min_notional_holds():
    intent = build_rebalance_intent(
        symbol="PFE",
        target_weight=0.0001,
        actual_qty=0.0,
        price=100.0,
        equity=100_000.0,
        config=ExecutionConfig(min_notional=25.0, dry_run=True),
    )

    assert intent.side == "hold"
    assert intent.should_order is False
    assert intent.reason == "below_min_notional"


def test_build_rebalance_intent_invalid_price_holds():
    intent = build_rebalance_intent(
        symbol="AAPL",
        target_weight=0.20,
        actual_qty=0.0,
        price=0.0,
        equity=100_000.0,
    )

    assert intent.should_order is False
    assert intent.reason == "invalid_price"


def test_build_rebalance_intents_from_targets_dataframe():
    targets = pd.DataFrame(
        [
            {
                "symbol": "AMD",
                "target_weight": 0.20,
                "actual_qty": 0.0,
                "actual_market_value": 0.0,
                "latest_price": 100.0,
                "equity": 100_000.0,
            },
            {
                "symbol": "XOM",
                "target_weight": 0.00,
                "actual_qty": 10.0,
                "actual_market_value": 1_000.0,
                "latest_price": 100.0,
                "equity": 100_000.0,
            },
        ]
    )

    intents = build_rebalance_intents_from_targets(
        targets,
        config=ExecutionConfig(min_notional=25.0, dry_run=True),
    )

    assert len(intents) == 2
    assert list(intents["symbol"]) == ["AMD", "XOM"]
    assert list(intents["side"]) == ["buy", "sell"]
    assert int(intents["should_order"].sum()) == 2


def test_execute_rebalance_intent_dry_run_submits_no_order():
    intent = build_rebalance_intent(
        symbol="AMD",
        target_weight=0.20,
        actual_qty=0.0,
        price=100.0,
        equity=100_000.0,
        config=ExecutionConfig(min_notional=25.0, dry_run=True),
    )

    result = execute_rebalance_intent(
        trading_client=object(),
        intent=intent,
        submit_orders=True,
    )

    assert result["order_submitted"] is False
    assert result["execution_note"] == "dry_run_no_order_submitted"


def test_execute_rebalance_intent_requires_submit_orders_flag():
    intent = build_rebalance_intent(
        symbol="AMD",
        target_weight=0.20,
        actual_qty=0.0,
        price=100.0,
        equity=100_000.0,
        config=ExecutionConfig(min_notional=25.0, dry_run=False),
    )

    result = execute_rebalance_intent(
        trading_client=object(),
        intent=intent,
        submit_orders=False,
    )

    assert result["order_submitted"] is False
    assert result["execution_note"] == "dry_run_no_order_submitted"


def test_summarize_intents_counts_orders():
    targets = pd.DataFrame(
        [
            {
                "symbol": "AMD",
                "target_weight": 0.20,
                "actual_qty": 0.0,
                "actual_market_value": 0.0,
                "latest_price": 100.0,
                "equity": 100_000.0,
            },
            {
                "symbol": "PFE",
                "target_weight": 0.0001,
                "actual_qty": 0.0,
                "actual_market_value": 0.0,
                "latest_price": 100.0,
                "equity": 100_000.0,
            },
        ]
    )

    intents = build_rebalance_intents_from_targets(
        targets,
        config=ExecutionConfig(min_notional=25.0, dry_run=True),
    )
    summary = summarize_intents(intents)

    assert summary["rows"] == 2
    assert summary["orders_required"] == 1
    assert summary["buy_count"] == 1
    assert summary["sell_count"] == 0
