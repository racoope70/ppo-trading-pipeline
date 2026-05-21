"""Pre-trade checklist for Alpaca paper-trading runs.

This module verifies that the no-order safety chain is ready before any
intentional --submit-orders paper-trading run.

It does not submit orders.
It can run without Alpaca credentials.
Broker checks are optional and only run when explicitly requested.
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

from src.adapters.alpaca import create_alpaca_clients
from src.paper_trading.logging_utils import snapshot_broker_state, to_json_safe


DEFAULT_RUN_DIR = Path("reports/paper_trading_dry_runs/latest")


@dataclass(frozen=True)
class PreTradeChecklistConfig:
    """Configuration for pre-trade readiness checks."""

    expected_equity: float = 100_000.0
    equity_tolerance_pct: float = 0.02
    require_flat_positions: bool = True
    require_no_open_orders: bool = True
    require_audit_log: bool = True
    require_risk_passed: bool = True
    require_no_orders_submitted: bool = True
    require_no_order_mode: bool = True


@dataclass(frozen=True)
class ChecklistCheck:
    """Single checklist result."""

    name: str
    passed: bool
    severity: str
    detail: str


@dataclass(frozen=True)
class ChecklistReport:
    """Full pre-trade checklist report."""

    checks: list[ChecklistCheck]
    run_dir: str
    datetime_utc: str

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "datetime_utc": self.datetime_utc,
            "run_dir": self.run_dir,
            "checks": [asdict(check) for check in self.checks],
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json_if_exists(path: str | Path) -> dict[str, Any]:
    p = Path(path)

    if not p.exists():
        return {}

    with p.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {p}")

    return payload


def _safe_float(value: Any, default: float = float("nan")) -> float:
    try:
        result = float(value)
        if math.isfinite(result):
            return result
    except Exception:
        pass

    return default


def _safe_int(value: Any, default: int = -1) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _bool_value(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _add_check(
    checks: list[ChecklistCheck],
    name: str,
    passed: bool,
    detail: str,
    severity: str = "ERROR",
) -> None:
    checks.append(
        ChecklistCheck(
            name=name,
            passed=bool(passed),
            severity=severity,
            detail=str(detail),
        )
    )


def evaluate_pre_trade_checklist(
    *,
    run_dir: str | Path = DEFAULT_RUN_DIR,
    config: PreTradeChecklistConfig | None = None,
    broker_state: dict[str, Any] | None = None,
) -> ChecklistReport:
    """Evaluate pre-trade readiness from run outputs and optional broker state."""
    cfg = config or PreTradeChecklistConfig()
    root = Path(run_dir)
    checks: list[ChecklistCheck] = []

    dry_run_targets_path = root / "dry_run_targets.csv"
    dry_run_summary_path = root / "dry_run_summary.json"
    execution_plan_path = root / "execution_plan.csv"
    execution_plan_summary_path = root / "execution_plan_summary.json"
    paper_order_run_path = root / "paper_order_run.csv"
    paper_order_run_summary_path = root / "paper_order_run_summary.json"
    audit_log_path = root / "paper_trade_audit_log.json"

    expected_paths = [
        dry_run_targets_path,
        dry_run_summary_path,
        execution_plan_path,
        execution_plan_summary_path,
        paper_order_run_path,
        paper_order_run_summary_path,
    ]

    if cfg.require_audit_log:
        expected_paths.append(audit_log_path)

    _add_check(
        checks,
        "run_dir_exists",
        root.exists(),
        str(root),
    )

    for path in expected_paths:
        _add_check(
            checks,
            f"{path.name}_exists",
            path.exists(),
            str(path),
        )

    if not root.exists():
        return ChecklistReport(
            checks=checks,
            run_dir=str(root),
            datetime_utc=utc_now_iso(),
        )

    dry_run_summary = read_json_if_exists(dry_run_summary_path)
    execution_summary = read_json_if_exists(execution_plan_summary_path)
    order_summary = read_json_if_exists(paper_order_run_summary_path)
    audit_log = read_json_if_exists(audit_log_path)

    if dry_run_targets_path.exists():
        dry_run_targets = pd.read_csv(dry_run_targets_path)
        _add_check(
            checks,
            "dry_run_targets_non_empty",
            not dry_run_targets.empty,
            f"rows={len(dry_run_targets)}",
        )

        if "note" in dry_run_targets.columns:
            notes = sorted(set(dry_run_targets["note"].astype(str)))
            _add_check(
                checks,
                "dry_run_predict_ok",
                set(notes) == {"dry_run_predict_ok"},
                f"notes={notes}",
            )

    if execution_plan_path.exists():
        execution_plan = pd.read_csv(execution_plan_path)
        _add_check(
            checks,
            "execution_plan_non_empty",
            not execution_plan.empty,
            f"rows={len(execution_plan)}",
        )

        if "order_submitted" in execution_plan.columns:
            submitted_count = int(
                execution_plan["order_submitted"]
                .astype(str)
                .str.lower()
                .isin({"true", "1"})
                .sum()
            )
            _add_check(
                checks,
                "execution_plan_no_submitted_orders",
                submitted_count == 0,
                f"submitted_count={submitted_count}",
            )

        if "should_order" in execution_plan.columns:
            should_order_count = int(
                execution_plan["should_order"]
                .astype(str)
                .str.lower()
                .isin({"true", "1"})
                .sum()
            )
            _add_check(
                checks,
                "execution_plan_review_required",
                should_order_count >= 0,
                f"orders_required={should_order_count}",
                severity="INFO",
            )

    dry_error_count = _safe_int(dry_run_summary.get("error_count", 0), default=0)
    _add_check(
        checks,
        "dry_run_error_count_zero",
        dry_error_count == 0,
        f"error_count={dry_error_count}",
    )

    dry_orders = _safe_int(dry_run_summary.get("orders_submitted", 0), default=0)
    _add_check(
        checks,
        "dry_run_orders_submitted_zero",
        dry_orders == 0,
        f"orders_submitted={dry_orders}",
    )

    execution_orders = _safe_int(execution_summary.get("orders_submitted", 0), default=0)
    _add_check(
        checks,
        "execution_summary_orders_submitted_zero",
        execution_orders == 0,
        f"orders_submitted={execution_orders}",
    )

    order_summary_orders = _safe_int(order_summary.get("orders_submitted", 0), default=0)
    _add_check(
        checks,
        "paper_order_summary_orders_submitted_zero",
        (order_summary_orders == 0 if cfg.require_no_orders_submitted else True),
        f"orders_submitted={order_summary_orders}",
    )

    order_summary_submit_orders = bool(order_summary.get("submit_orders", False))
    _add_check(
        checks,
        "paper_order_summary_no_order_mode",
        (order_summary_submit_orders is False if cfg.require_no_order_mode else True),
        f"submit_orders={order_summary_submit_orders}",
    )

    order_risk_passed = _bool_value(order_summary.get("risk_passed", False))
    _add_check(
        checks,
        "paper_order_risk_passed",
        (order_risk_passed if cfg.require_risk_passed else True),
        f"risk_passed={order_risk_passed}",
    )

    if cfg.require_audit_log:
        audit_risk_passed = _bool_value(audit_log.get("risk_passed", False))
        audit_orders = _safe_int(audit_log.get("orders_submitted", -1), default=-1)
        audit_submit_orders = bool(audit_log.get("submit_orders", True))

        _add_check(
            checks,
            "audit_log_risk_passed",
            (audit_risk_passed if cfg.require_risk_passed else True),
            f"risk_passed={audit_risk_passed}",
        )

        _add_check(
            checks,
            "audit_log_orders_submitted_zero",
            (audit_orders == 0 if cfg.require_no_orders_submitted else True),
            f"orders_submitted={audit_orders}",
        )

        _add_check(
            checks,
            "audit_log_no_order_mode",
            (audit_submit_orders is False if cfg.require_no_order_mode else True),
            f"submit_orders={audit_submit_orders}",
        )

    if broker_state is not None:
        account = broker_state.get("account", {})
        positions_count = _safe_int(broker_state.get("positions_count", 0), default=0)
        open_orders_count = _safe_int(broker_state.get("open_orders_count", 0), default=0)

        equity = _safe_float(account.get("equity"))
        cash = _safe_float(account.get("cash"))

        lower_bound = cfg.expected_equity * (1.0 - cfg.equity_tolerance_pct)
        upper_bound = cfg.expected_equity * (1.0 + cfg.equity_tolerance_pct)

        _add_check(
            checks,
            "broker_equity_near_expected",
            lower_bound <= equity <= upper_bound,
            (
                f"equity={equity}; expected={cfg.expected_equity}; "
                f"tolerance_pct={cfg.equity_tolerance_pct}"
            ),
        )

        _add_check(
            checks,
            "broker_cash_available",
            cash > 0,
            f"cash={cash}",
        )

        _add_check(
            checks,
            "broker_positions_flat",
            (positions_count == 0 if cfg.require_flat_positions else True),
            f"positions_count={positions_count}",
        )

        _add_check(
            checks,
            "broker_open_orders_zero",
            (open_orders_count == 0 if cfg.require_no_open_orders else True),
            f"open_orders_count={open_orders_count}",
        )

        broker_errors = broker_state.get("errors", [])
        _add_check(
            checks,
            "broker_snapshot_errors_empty",
            len(broker_errors) == 0,
            f"errors={broker_errors}",
        )

    return ChecklistReport(
        checks=checks,
        run_dir=str(root),
        datetime_utc=utc_now_iso(),
    )


def assert_checklist_passes(report: ChecklistReport) -> None:
    """Raise if any checklist check fails."""
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

    raise RuntimeError(f"Pre-trade checklist failed: {failures}")


def write_checklist_report(
    report: ChecklistReport,
    output_dir: str | Path,
    *,
    filename: str = "pre_trade_checklist_report.json",
) -> Path:
    """Write checklist report to JSON."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    output_path = root / filename
    output_path.write_text(
        json.dumps(to_json_safe(report.to_dict()), indent=2, default=str),
        encoding="utf-8",
    )

    return output_path


def print_checklist_report(report: ChecklistReport) -> None:
    print("=" * 80)
    print("PAPER-TRADING PRE-TRADE CHECKLIST")
    print("=" * 80)

    for check in report.checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status:5} {check.name:45} {check.detail}")

    print()
    print("Checklist result:", "PASS" if report.passed else "FAIL")


def build_broker_state_from_env(
    *,
    env_path: str | Path = ".env",
) -> dict[str, Any]:
    """Build broker state using local Alpaca paper credentials."""
    trading_client, _ = create_alpaca_clients(
        env_path=env_path,
        require_paper=True,
    )
    return snapshot_broker_state(trading_client)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run pre-trade readiness checks before any paper-order submission."
    )
    parser.add_argument(
        "--run-dir",
        default=str(DEFAULT_RUN_DIR),
        help="Run directory containing no-order chain outputs.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Default: same as --run-dir.",
    )
    parser.add_argument(
        "--env",
        default=".env",
        help="Path to local .env file for optional Alpaca broker checks.",
    )
    parser.add_argument(
        "--check-broker",
        action="store_true",
        help="Also check live Alpaca paper account state.",
    )
    parser.add_argument(
        "--expected-equity",
        type=float,
        default=100_000.0,
        help="Expected paper-account equity baseline.",
    )
    parser.add_argument(
        "--equity-tolerance-pct",
        type=float,
        default=0.02,
        help="Allowed equity deviation from expected baseline.",
    )
    parser.add_argument(
        "--allow-open-positions",
        action="store_true",
        help="Do not require flat broker positions.",
    )
    parser.add_argument(
        "--allow-open-orders",
        action="store_true",
        help="Do not require zero broker open orders.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else Path(args.run_dir)

    config = PreTradeChecklistConfig(
        expected_equity=float(args.expected_equity),
        equity_tolerance_pct=float(args.equity_tolerance_pct),
        require_flat_positions=not bool(args.allow_open_positions),
        require_no_open_orders=not bool(args.allow_open_orders),
    )

    broker_state = None
    if args.check_broker:
        broker_state = build_broker_state_from_env(env_path=args.env)

    report = evaluate_pre_trade_checklist(
        run_dir=args.run_dir,
        config=config,
        broker_state=broker_state,
    )

    output_path = write_checklist_report(report, output_dir)
    print_checklist_report(report)
    print()
    print(f"Saved checklist report: {output_path}")

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
