"""Risk-control checks for Alpaca paper-trading execution plans.

This module evaluates whether an execution plan is safe to submit.

It does not connect to Alpaca.
It does not submit orders.

The intended workflow is:

1. Build dry-run targets.
2. Evaluate dry-run targets.
3. Build execution plan.
4. Run risk controls.
5. Only then allow guarded paper-order submission.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_RUN_DIR = Path("reports/paper_trading_dry_runs/latest")


@dataclass(frozen=True)
class RiskControlConfig:
    """Risk-control thresholds for paper-trading execution plans."""

    max_abs_symbol_weight: float = 0.40
    max_gross_target_weight: float = 1.00
    max_net_target_weight: float = 0.80
    max_single_order_notional_pct: float = 0.40
    max_total_order_notional_pct: float = 1.00
    min_equity: float = 1.0
    require_no_open_orders: bool = True
    require_flat_start: bool = False
    actual_weight_tolerance: float = 1e-6
    max_plan_age_minutes: float | None = None


@dataclass(frozen=True)
class RiskContext:
    """Optional broker/account context for risk controls."""

    account_equity: float | None = None
    cash: float | None = None
    positions_count: int | None = None
    open_orders_count: int | None = None
    now_utc: str | None = None
    submit_orders: bool = False


@dataclass(frozen=True)
class RiskCheck:
    """Single risk-control check result."""

    name: str
    passed: bool
    severity: str
    detail: str


@dataclass(frozen=True)
class RiskReport:
    """Risk-control report."""

    checks: list[RiskCheck]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": [asdict(check) for check in self.checks],
        }


def _safe_float(value: Any, default: float = float("nan")) -> float:
    try:
        result = float(value)
        if math.isfinite(result):
            return result
    except Exception:
        pass
    return float(default)


def _bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})


def _numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(df[column], errors="coerce")


def _finite_column(df: pd.DataFrame, column: str) -> bool:
    values = _numeric_series(df, column)
    return bool(values.notna().all() and values.map(math.isfinite).all())


def _parse_timestamp_utc(value: Any) -> pd.Timestamp | None:
    try:
        ts = pd.Timestamp(value)
        if pd.isna(ts):
            return None
        if ts.tzinfo is None:
            return ts.tz_localize("UTC")
        return ts.tz_convert("UTC")
    except Exception:
        return None


def load_execution_plan_for_risk(run_dir: str | Path = DEFAULT_RUN_DIR) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load execution plan and summary from a run directory."""
    root = Path(run_dir)
    plan_path = root / "execution_plan.csv"
    summary_path = root / "execution_plan_summary.json"

    if not plan_path.exists():
        raise FileNotFoundError(f"Missing execution plan: {plan_path}")

    if not summary_path.exists():
        raise FileNotFoundError(f"Missing execution plan summary: {summary_path}")

    plan = pd.read_csv(plan_path)

    with summary_path.open("r", encoding="utf-8") as f:
        summary = json.load(f)

    if not isinstance(summary, dict):
        raise ValueError(f"Execution plan summary must be a JSON object: {summary_path}")

    return plan, summary


def evaluate_execution_plan_risk(
    plan: pd.DataFrame,
    summary: dict[str, Any] | None = None,
    *,
    config: RiskControlConfig | None = None,
    context: RiskContext | None = None,
) -> RiskReport:
    """Evaluate risk controls for an execution plan."""
    cfg = config or RiskControlConfig()
    ctx = context or RiskContext()
    checks: list[RiskCheck] = []

    def add(name: str, passed: bool, detail: str, severity: str = "ERROR") -> None:
        checks.append(
            RiskCheck(
                name=name,
                passed=bool(passed),
                severity=severity,
                detail=str(detail),
            )
        )

    required_columns = [
        "symbol",
        "side",
        "qty",
        "price",
        "equity",
        "target_weight",
        "actual_weight",
        "target_notional",
        "actual_notional",
        "delta_notional",
        "should_order",
        "order_submitted",
    ]

    add("plan_non_empty", not plan.empty, f"rows={len(plan)}")

    missing = [col for col in required_columns if col not in plan.columns]
    add("required_columns_present", not missing, f"missing={missing}")

    if plan.empty or missing:
        return RiskReport(checks)

    for column in ["qty", "price", "equity", "target_weight", "actual_weight", "delta_notional"]:
        add(f"{column}_finite", _finite_column(plan, column), column)

    equity_values = _numeric_series(plan, "equity")
    min_equity = float(equity_values.min())
    add(
        "equity_above_minimum",
        bool((equity_values >= cfg.min_equity).all()),
        f"min_equity={min_equity}; required={cfg.min_equity}",
    )

    target_weights = _numeric_series(plan, "target_weight")
    actual_weights = _numeric_series(plan, "actual_weight")
    delta_notional = _numeric_series(plan, "delta_notional")
    qty_values = _numeric_series(plan, "qty")

    max_abs_weight = float(target_weights.abs().max())
    add(
        "single_symbol_target_weight_within_limit",
        max_abs_weight <= cfg.max_abs_symbol_weight + 1e-12,
        f"max_abs_target_weight={max_abs_weight}; limit={cfg.max_abs_symbol_weight}",
    )

    gross_target_weight = float(target_weights.abs().sum())
    add(
        "gross_target_weight_within_limit",
        gross_target_weight <= cfg.max_gross_target_weight + 1e-12,
        f"gross_target_weight={gross_target_weight}; limit={cfg.max_gross_target_weight}",
    )

    net_target_weight = float(abs(target_weights.sum()))
    add(
        "net_target_weight_within_limit",
        net_target_weight <= cfg.max_net_target_weight + 1e-12,
        f"net_target_weight={net_target_weight}; limit={cfg.max_net_target_weight}",
    )

    should_order = _bool_series(plan["should_order"])
    order_submitted = _bool_series(plan["order_submitted"])

    add(
        "no_prior_order_submitted_flags",
        not bool(order_submitted.any()),
        f"prior_order_submitted_count={int(order_submitted.sum())}",
    )

    valid_sides = plan["side"].astype(str).str.lower().isin({"buy", "sell", "hold"})
    add(
        "valid_order_sides",
        bool(valid_sides.all()),
        f"invalid_sides={sorted(set(plan.loc[~valid_sides, 'side'].astype(str)))}",
    )

    order_rows = plan[should_order]
    order_sides_ok = order_rows["side"].astype(str).str.lower().isin({"buy", "sell"}).all()
    add(
        "order_rows_have_buy_or_sell_side",
        bool(order_sides_ok),
        f"order_rows={len(order_rows)}",
    )

    add(
        "quantities_non_negative",
        bool((qty_values >= 0).all()),
        f"min_qty={float(qty_values.min())}",
    )

    reference_equity = _safe_float(ctx.account_equity)
    if not math.isfinite(reference_equity):
        reference_equity = _safe_float(equity_values.iloc[0])

    total_order_notional = float(delta_notional[should_order].abs().sum())
    total_order_notional_pct = total_order_notional / reference_equity if reference_equity > 0 else float("inf")

    add(
        "total_order_notional_within_limit",
        total_order_notional_pct <= cfg.max_total_order_notional_pct + 1e-12,
        (
            f"total_order_notional={total_order_notional}; "
            f"pct={total_order_notional_pct}; "
            f"limit={cfg.max_total_order_notional_pct}"
        ),
    )

    single_order_notional_pct = (
        delta_notional[should_order].abs() / reference_equity
        if reference_equity > 0
        else pd.Series([float("inf")])
    )
    max_single_order_pct = float(single_order_notional_pct.max()) if len(single_order_notional_pct) else 0.0

    add(
        "single_order_notional_within_limit",
        max_single_order_pct <= cfg.max_single_order_notional_pct + 1e-12,
        f"max_single_order_pct={max_single_order_pct}; limit={cfg.max_single_order_notional_pct}",
    )

    if cfg.require_no_open_orders and ctx.open_orders_count is not None:
        add(
            "no_open_orders_in_account",
            int(ctx.open_orders_count) == 0,
            f"open_orders_count={ctx.open_orders_count}",
        )

    if cfg.require_flat_start:
        if ctx.positions_count is not None:
            add(
                "account_positions_flat",
                int(ctx.positions_count) == 0,
                f"positions_count={ctx.positions_count}",
            )

        max_actual_abs_weight = float(actual_weights.abs().max())
        add(
            "plan_actual_weights_flat",
            max_actual_abs_weight <= cfg.actual_weight_tolerance,
            (
                f"max_abs_actual_weight={max_actual_abs_weight}; "
                f"tolerance={cfg.actual_weight_tolerance}"
            ),
        )

    if cfg.max_plan_age_minutes is not None:
        if "latest_bar_time" not in plan.columns:
            add(
                "plan_timestamp_available",
                False,
                "latest_bar_time column missing",
            )
        else:
            timestamps = [
                _parse_timestamp_utc(value)
                for value in plan["latest_bar_time"].dropna().tolist()
            ]
            timestamps = [ts for ts in timestamps if ts is not None]

            if not timestamps:
                add(
                    "plan_timestamp_available",
                    False,
                    "no parseable latest_bar_time values",
                )
            else:
                latest_ts = max(timestamps)

                now = _parse_timestamp_utc(ctx.now_utc) if ctx.now_utc else pd.Timestamp(datetime.now(timezone.utc))
                assert now is not None

                age_minutes = (now - latest_ts).total_seconds() / 60.0

                add(
                    "plan_not_stale",
                    age_minutes <= cfg.max_plan_age_minutes + 1e-12,
                    f"age_minutes={age_minutes:.2f}; limit={cfg.max_plan_age_minutes}",
                )

    if summary is not None:
        summary_orders = _safe_float(summary.get("orders_submitted", float("nan")))
        add(
            "summary_orders_submitted_zero",
            summary_orders == 0.0,
            f"summary_orders_submitted={summary.get('orders_submitted')}",
        )

    return RiskReport(checks)


def assert_risk_report_passes(report: RiskReport) -> None:
    """Raise if a risk report contains failed checks."""
    if report.passed:
        return

    failures = [
        {
            "name": check.name,
            "severity": check.severity,
            "detail": check.detail,
        }
        for check in report.checks
        if not check.passed
    ]

    raise RuntimeError(f"Risk controls failed: {failures}")


def print_risk_report(report: RiskReport) -> None:
    print("=" * 80)
    print("PAPER-TRADING RISK CONTROL REPORT")
    print("=" * 80)

    for check in report.checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status:5} {check.name:45} {check.detail}")

    print()
    print("Risk result:", "PASS" if report.passed else "FAIL")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate risk controls for a paper-trading execution plan."
    )
    parser.add_argument(
        "--run-dir",
        default=str(DEFAULT_RUN_DIR),
        help="Directory containing execution_plan.csv and execution_plan_summary.json.",
    )
    parser.add_argument(
        "--max-abs-symbol-weight",
        type=float,
        default=0.40,
    )
    parser.add_argument(
        "--max-gross-target-weight",
        type=float,
        default=1.00,
    )
    parser.add_argument(
        "--max-net-target-weight",
        type=float,
        default=0.80,
    )
    parser.add_argument(
        "--max-single-order-notional-pct",
        type=float,
        default=0.40,
    )
    parser.add_argument(
        "--max-total-order-notional-pct",
        type=float,
        default=1.00,
    )
    parser.add_argument(
        "--require-flat-start",
        action="store_true",
        help="Require plan actual weights to be flat.",
    )
    parser.add_argument(
        "--max-plan-age-minutes",
        type=float,
        default=None,
        help="Optional staleness limit for latest_bar_time.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    plan, summary = load_execution_plan_for_risk(args.run_dir)

    config = RiskControlConfig(
        max_abs_symbol_weight=args.max_abs_symbol_weight,
        max_gross_target_weight=args.max_gross_target_weight,
        max_net_target_weight=args.max_net_target_weight,
        max_single_order_notional_pct=args.max_single_order_notional_pct,
        max_total_order_notional_pct=args.max_total_order_notional_pct,
        require_flat_start=bool(args.require_flat_start),
        max_plan_age_minutes=args.max_plan_age_minutes,
    )

    report = evaluate_execution_plan_risk(
        plan,
        summary,
        config=config,
    )

    print_risk_report(report)

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
