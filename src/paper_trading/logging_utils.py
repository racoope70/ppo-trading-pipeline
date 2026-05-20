"""Audit logging utilities for Alpaca paper-trading runs.

This module builds a single auditable run record from the existing paper-trading
safety-chain outputs.

It does not submit orders.
It does not require Alpaca credentials.
It can optionally snapshot broker-like account/position/order objects when a
client is supplied by another module.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_RUN_DIR = Path("reports/paper_trading_dry_runs/latest")


@dataclass(frozen=True)
class AuditFileSummary:
    """Metadata for one run-output file."""

    path: str
    exists: bool
    size_bytes: int | None = None
    rows: int | None = None


def utc_now_iso() -> str:
    """Return current UTC timestamp as an ISO string."""
    return datetime.now(timezone.utc).isoformat()


def to_json_safe(value: Any) -> Any:
    """Convert common Python/pandas/numpy objects into JSON-safe values."""
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, (datetime, date, pd.Timestamp)):
        return str(value)

    if is_dataclass(value):
        return to_json_safe(asdict(value))

    if isinstance(value, dict):
        return {str(k): to_json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [to_json_safe(v) for v in value]

    # Handles numpy scalar values without importing numpy.
    if hasattr(value, "item"):
        try:
            return to_json_safe(value.item())
        except Exception:
            pass

    # Handles enum-like objects and Alpaca SDK objects.
    return str(value)


def read_json_if_exists(path: str | Path) -> dict[str, Any]:
    """Read a JSON object if it exists. Return an empty dict if missing."""
    p = Path(path)
    if not p.exists():
        return {}

    with p.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {p}")

    return payload


def count_csv_rows(path: str | Path) -> int | None:
    """Count rows in a CSV file. Return None if the file does not exist."""
    p = Path(path)
    if not p.exists():
        return None

    df = pd.read_csv(p)
    return int(len(df))


def summarize_file(path: str | Path) -> AuditFileSummary:
    """Create a compact file summary."""
    p = Path(path)

    if not p.exists():
        return AuditFileSummary(
            path=str(p),
            exists=False,
            size_bytes=None,
            rows=None,
        )

    rows = count_csv_rows(p) if p.suffix.lower() == ".csv" else None

    return AuditFileSummary(
        path=str(p),
        exists=True,
        size_bytes=int(p.stat().st_size),
        rows=rows,
    )


def _safe_getattr(obj: Any, name: str, default: Any = None) -> Any:
    try:
        return getattr(obj, name, default)
    except Exception:
        return default


def snapshot_account(account: Any) -> dict[str, Any]:
    """Convert an account-like object into a JSON-safe snapshot."""
    if account is None:
        return {}

    fields = [
        "id",
        "account_number",
        "status",
        "currency",
        "equity",
        "cash",
        "buying_power",
        "portfolio_value",
        "long_market_value",
        "short_market_value",
        "initial_margin",
        "maintenance_margin",
        "last_equity",
    ]

    return {
        field: to_json_safe(_safe_getattr(account, field))
        for field in fields
        if _safe_getattr(account, field) is not None
    }


def snapshot_position(position: Any) -> dict[str, Any]:
    """Convert a position-like object into a JSON-safe snapshot."""
    fields = [
        "symbol",
        "qty",
        "side",
        "market_value",
        "avg_entry_price",
        "current_price",
        "unrealized_pl",
        "unrealized_plpc",
        "cost_basis",
    ]

    return {
        field: to_json_safe(_safe_getattr(position, field))
        for field in fields
        if _safe_getattr(position, field) is not None
    }


def snapshot_order(order: Any) -> dict[str, Any]:
    """Convert an order-like object into a JSON-safe snapshot."""
    fields = [
        "id",
        "client_order_id",
        "symbol",
        "side",
        "qty",
        "filled_qty",
        "filled_avg_price",
        "type",
        "status",
        "time_in_force",
        "submitted_at",
        "filled_at",
        "canceled_at",
    ]

    return {
        field: to_json_safe(_safe_getattr(order, field))
        for field in fields
        if _safe_getattr(order, field) is not None
    }


def snapshot_broker_state(trading_client: Any) -> dict[str, Any]:
    """Snapshot broker state from a trading-client-like object.

    This function is read-only. It calls account, position, and order endpoints
    when a client is provided.
    """
    snapshot: dict[str, Any] = {
        "datetime_utc": utc_now_iso(),
        "account": {},
        "positions": [],
        "open_orders": [],
        "errors": [],
    }

    try:
        account = trading_client.get_account()
        snapshot["account"] = snapshot_account(account)
    except Exception as exc:
        snapshot["errors"].append(f"get_account_failed: {exc}")

    try:
        positions = trading_client.get_all_positions() or []
        snapshot["positions"] = [snapshot_position(p) for p in positions]
    except Exception as exc:
        snapshot["errors"].append(f"get_all_positions_failed: {exc}")

    try:
        open_orders = trading_client.get_orders() or []
        snapshot["open_orders"] = [snapshot_order(o) for o in open_orders]
    except Exception as exc:
        snapshot["errors"].append(f"get_orders_failed: {exc}")

    snapshot["positions_count"] = len(snapshot["positions"])
    snapshot["open_orders_count"] = len(snapshot["open_orders"])

    return to_json_safe(snapshot)


def build_audit_record(
    *,
    run_dir: str | Path = DEFAULT_RUN_DIR,
    output_dir: str | Path | None = None,
    broker_state_before: dict[str, Any] | None = None,
    broker_state_after: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one auditable paper-trading run record."""
    root = Path(run_dir)
    out_root = Path(output_dir) if output_dir is not None else root

    expected_files = {
        "dry_run_targets": root / "dry_run_targets.csv",
        "dry_run_summary": root / "dry_run_summary.json",
        "execution_plan": root / "execution_plan.csv",
        "execution_plan_summary": root / "execution_plan_summary.json",
        "paper_order_run": root / "paper_order_run.csv",
        "paper_order_run_summary": root / "paper_order_run_summary.json",
    }

    file_summaries = {
        name: asdict(summarize_file(path))
        for name, path in expected_files.items()
    }

    dry_run_summary = read_json_if_exists(expected_files["dry_run_summary"])
    execution_plan_summary = read_json_if_exists(expected_files["execution_plan_summary"])
    paper_order_run_summary = read_json_if_exists(expected_files["paper_order_run_summary"])

    audit_record = {
        "audit_type": "paper_trading_run",
        "datetime_utc": utc_now_iso(),
        "source_run_dir": str(root),
        "output_dir": str(out_root),
        "metadata": metadata or {},
        "files": file_summaries,
        "dry_run_summary": dry_run_summary,
        "execution_plan_summary": execution_plan_summary,
        "paper_order_run_summary": paper_order_run_summary,
        "risk_passed": paper_order_run_summary.get("risk_passed"),
        "orders_required": paper_order_run_summary.get("orders_required"),
        "orders_submitted": paper_order_run_summary.get("orders_submitted"),
        "submit_orders": paper_order_run_summary.get("submit_orders"),
        "broker_state_before": broker_state_before or {},
        "broker_state_after": broker_state_after or {},
    }

    return to_json_safe(audit_record)


def write_audit_record(
    audit_record: dict[str, Any],
    output_dir: str | Path,
    *,
    filename: str = "paper_trade_audit_log.json",
) -> Path:
    """Write audit record to JSON."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    output_path = root / filename
    output_path.write_text(
        json.dumps(to_json_safe(audit_record), indent=2, default=str),
        encoding="utf-8",
    )

    return output_path


def build_and_write_audit_record(
    *,
    run_dir: str | Path = DEFAULT_RUN_DIR,
    output_dir: str | Path | None = None,
    broker_state_before: dict[str, Any] | None = None,
    broker_state_after: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], Path]:
    """Build and write a paper-trading audit record."""
    root = Path(run_dir)
    out_root = Path(output_dir) if output_dir is not None else root

    record = build_audit_record(
        run_dir=root,
        output_dir=out_root,
        broker_state_before=broker_state_before,
        broker_state_after=broker_state_after,
        metadata=metadata,
    )
    output_path = write_audit_record(record, out_root)

    return record, output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an audit log from paper-trading run outputs."
    )
    parser.add_argument(
        "--run-dir",
        default=str(DEFAULT_RUN_DIR),
        help="Paper-trading run directory.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Default: same as --run-dir.",
    )
    parser.add_argument(
        "--tag",
        default=None,
        help="Optional metadata tag for this audit record.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else Path(args.run_dir)

    metadata = {}
    if args.tag:
        metadata["tag"] = args.tag

    record, output_path = build_and_write_audit_record(
        run_dir=args.run_dir,
        output_dir=output_dir,
        metadata=metadata,
    )

    print("=" * 80)
    print("PAPER-TRADING AUDIT LOG")
    print("=" * 80)
    print(f"Run dir: {args.run_dir}")
    print(f"Output dir: {output_dir}")
    print(f"Saved audit log: {output_path}")
    print()
    print(f"risk_passed={record.get('risk_passed')}")
    print(f"orders_required={record.get('orders_required')}")
    print(f"orders_submitted={record.get('orders_submitted')}")
    print(f"submit_orders={record.get('submit_orders')}")


if __name__ == "__main__":
    main()