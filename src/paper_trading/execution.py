"""Controlled execution utilities for Alpaca paper trading.

This module converts target weights into order intents and provides a guarded
execution function.

Safety principle:
- Building intents is always safe.
- Submitting orders requires explicit submit_orders=True.
- dry_run=True remains the default.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from src.adapters.alpaca import submit_market_order


@dataclass(frozen=True)
class ExecutionConfig:
    """Execution and sizing controls."""

    min_notional: float = 25.0
    max_abs_weight: float = 0.40
    allow_shorts: bool = False
    use_fractionals: bool = True
    qty_precision: int = 6
    dry_run: bool = True


@dataclass(frozen=True)
class RebalanceIntent:
    """A proposed rebalance order derived from target-vs-actual exposure."""

    symbol: str
    side: str
    qty: float
    price: float
    equity: float
    target_weight: float
    actual_weight: float
    target_notional: float
    actual_notional: float
    delta_notional: float
    min_notional: float
    max_abs_weight: float
    should_order: bool
    reason: str
    dry_run: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _is_finite_number(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        if math.isfinite(result):
            return result
    except Exception:
        pass
    return float(default)


def clamp_target_weight(
    target_weight: float,
    *,
    max_abs_weight: float,
    allow_shorts: bool,
) -> float:
    """Clamp target weight to configured exposure limits."""
    tw = _safe_float(target_weight, 0.0)
    cap = abs(_safe_float(max_abs_weight, 0.0))

    if cap <= 0:
        return 0.0

    tw = max(-cap, min(cap, tw))

    if not allow_shorts:
        tw = max(0.0, tw)

    return float(tw)


def round_quantity(
    qty: float,
    *,
    use_fractionals: bool,
    qty_precision: int,
) -> float:
    """Round order quantity based on fractional-share setting."""
    q = abs(_safe_float(qty, 0.0))

    if q <= 0:
        return 0.0

    if use_fractionals:
        return round(q, int(qty_precision))

    return float(math.floor(q))


def build_rebalance_intent(
    *,
    symbol: str,
    target_weight: float,
    actual_qty: float,
    price: float,
    equity: float,
    actual_market_value: float | None = None,
    config: ExecutionConfig | None = None,
) -> RebalanceIntent:
    """Convert target weight and current position into a proposed order intent."""
    cfg = config or ExecutionConfig()

    symbol_u = str(symbol).upper().strip()
    px = _safe_float(price, float("nan"))
    eq = _safe_float(equity, float("nan"))
    qty_now = _safe_float(actual_qty, 0.0)

    if not symbol_u:
        return RebalanceIntent(
            symbol="",
            side="hold",
            qty=0.0,
            price=px,
            equity=eq,
            target_weight=0.0,
            actual_weight=0.0,
            target_notional=0.0,
            actual_notional=0.0,
            delta_notional=0.0,
            min_notional=cfg.min_notional,
            max_abs_weight=cfg.max_abs_weight,
            should_order=False,
            reason="invalid_symbol",
            dry_run=cfg.dry_run,
        )

    if not _is_finite_number(px) or px <= 0:
        return RebalanceIntent(
            symbol=symbol_u,
            side="hold",
            qty=0.0,
            price=px,
            equity=eq,
            target_weight=0.0,
            actual_weight=0.0,
            target_notional=0.0,
            actual_notional=0.0,
            delta_notional=0.0,
            min_notional=cfg.min_notional,
            max_abs_weight=cfg.max_abs_weight,
            should_order=False,
            reason="invalid_price",
            dry_run=cfg.dry_run,
        )

    if not _is_finite_number(eq) or eq <= 0:
        return RebalanceIntent(
            symbol=symbol_u,
            side="hold",
            qty=0.0,
            price=px,
            equity=eq,
            target_weight=0.0,
            actual_weight=0.0,
            target_notional=0.0,
            actual_notional=0.0,
            delta_notional=0.0,
            min_notional=cfg.min_notional,
            max_abs_weight=cfg.max_abs_weight,
            should_order=False,
            reason="invalid_equity",
            dry_run=cfg.dry_run,
        )

    clipped_target_weight = clamp_target_weight(
        target_weight,
        max_abs_weight=cfg.max_abs_weight,
        allow_shorts=cfg.allow_shorts,
    )

    if actual_market_value is None:
        actual_notional = qty_now * px
    else:
        actual_notional = _safe_float(actual_market_value, qty_now * px)

    actual_weight = actual_notional / eq
    target_notional = clipped_target_weight * eq
    delta_notional = target_notional - actual_notional

    abs_delta = abs(delta_notional)

    if abs_delta < float(cfg.min_notional):
        return RebalanceIntent(
            symbol=symbol_u,
            side="hold",
            qty=0.0,
            price=px,
            equity=eq,
            target_weight=clipped_target_weight,
            actual_weight=actual_weight,
            target_notional=target_notional,
            actual_notional=actual_notional,
            delta_notional=delta_notional,
            min_notional=cfg.min_notional,
            max_abs_weight=cfg.max_abs_weight,
            should_order=False,
            reason="below_min_notional",
            dry_run=cfg.dry_run,
        )

    side = "buy" if delta_notional > 0 else "sell"
    raw_qty = abs_delta / px
    order_qty = round_quantity(
        raw_qty,
        use_fractionals=cfg.use_fractionals,
        qty_precision=cfg.qty_precision,
    )

    if order_qty <= 0:
        return RebalanceIntent(
            symbol=symbol_u,
            side="hold",
            qty=0.0,
            price=px,
            equity=eq,
            target_weight=clipped_target_weight,
            actual_weight=actual_weight,
            target_notional=target_notional,
            actual_notional=actual_notional,
            delta_notional=delta_notional,
            min_notional=cfg.min_notional,
            max_abs_weight=cfg.max_abs_weight,
            should_order=False,
            reason="rounded_qty_zero",
            dry_run=cfg.dry_run,
        )

    return RebalanceIntent(
        symbol=symbol_u,
        side=side,
        qty=order_qty,
        price=px,
        equity=eq,
        target_weight=clipped_target_weight,
        actual_weight=actual_weight,
        target_notional=target_notional,
        actual_notional=actual_notional,
        delta_notional=delta_notional,
        min_notional=cfg.min_notional,
        max_abs_weight=cfg.max_abs_weight,
        should_order=True,
        reason="rebalance_required",
        dry_run=cfg.dry_run,
    )


def build_rebalance_intents_from_targets(
    targets: pd.DataFrame,
    *,
    equity: float | None = None,
    config: ExecutionConfig | None = None,
) -> pd.DataFrame:
    """Build rebalance intents from a dry-run target dataframe."""
    cfg = config or ExecutionConfig()
    rows: list[dict[str, Any]] = []

    for _, row in targets.iterrows():
        row_equity = equity if equity is not None else row.get("equity")
        intent = build_rebalance_intent(
            symbol=row.get("symbol", ""),
            target_weight=row.get("target_weight", 0.0),
            actual_qty=row.get("actual_qty", 0.0),
            price=row.get("latest_price", float("nan")),
            equity=row_equity,
            actual_market_value=row.get("actual_market_value", None),
            config=cfg,
        )
        rows.append(intent.to_dict())

    return pd.DataFrame(rows)


def execute_rebalance_intent(
    trading_client: Any,
    intent: RebalanceIntent,
    *,
    submit_orders: bool = False,
) -> dict[str, Any]:
    """Execute or dry-run a rebalance intent.

    Guardrails:
    - If intent.should_order is False, no order is submitted.
    - If submit_orders is False, no order is submitted.
    - If intent.dry_run is True, no order is submitted.
    """
    result = intent.to_dict()
    result["order_submitted"] = False
    result["order_id"] = ""
    result["execution_note"] = ""

    if not intent.should_order:
        result["execution_note"] = intent.reason
        return result

    if intent.dry_run or not submit_orders:
        result["execution_note"] = "dry_run_no_order_submitted"
        return result

    order = submit_market_order(
        trading_client=trading_client,
        symbol=intent.symbol,
        side=intent.side,
        qty=float(intent.qty),
        dry_run=False,
    )

    result["order_submitted"] = True
    result["order_id"] = str(getattr(order, "id", "") or "")
    result["execution_note"] = "order_submitted"

    return result


def summarize_intents(intents: pd.DataFrame) -> dict[str, Any]:
    """Return a compact summary of proposed execution intents."""
    if intents.empty:
        return {
            "rows": 0,
            "orders_required": 0,
            "gross_intended_notional": 0.0,
            "buy_count": 0,
            "sell_count": 0,
        }

    should_order = intents["should_order"].astype(bool)

    return {
        "rows": int(len(intents)),
        "orders_required": int(should_order.sum()),
        "gross_intended_notional": float(
            intents.loc[should_order, "delta_notional"].abs().sum()
        ),
        "buy_count": int(((intents["side"] == "buy") & should_order).sum()),
        "sell_count": int(((intents["side"] == "sell") & should_order).sum()),
    }
