"""Evaluate Alpaca paper-trading dry-run outputs.

This module validates the safety and completeness of a broker-connected dry run.

It checks:
- dry_run_targets.csv exists and is readable
- dry_run_summary.json exists and is readable
- expected symbols are present exactly once
- orders_submitted == 0
- no dry_run_error rows
- all rows have dry_run_predict_ok
- latest_bar_time exists
- target/action/confidence/weight fields are finite
- confidence is between 0 and 1
- target weights are within a configurable bound

This script does not connect to Alpaca and does not submit orders.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.paper_trading.artifact_manifest import DEFAULT_MANIFEST_PATH, load_manifest


DEFAULT_RUN_DIR = Path("reports/paper_trading_dry_runs/latest")


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")

    return payload


def _finite_series(df: pd.DataFrame, column: str) -> bool:
    values = pd.to_numeric(df[column], errors="coerce")
    return bool(np.isfinite(values.to_numpy(dtype=float)).all())


def _is_zero_like(value: Any) -> bool:
    try:
        return float(value) == 0.0
    except Exception:
        return False


def _expected_symbols_from_manifest(manifest_path: str | Path | None) -> list[str]:
    if manifest_path is None:
        return []

    path = Path(manifest_path)
    if not path.exists():
        return []

    manifest = load_manifest(path)
    return manifest.universe


def validate_dry_run(
    run_dir: str | Path = DEFAULT_RUN_DIR,
    expected_symbols: list[str] | None = None,
    manifest_path: str | Path | None = DEFAULT_MANIFEST_PATH,
    max_abs_target_weight: float = 1.0,
) -> tuple[list[CheckResult], pd.DataFrame, dict[str, Any]]:
    """Validate a dry-run output directory."""
    root = Path(run_dir)
    targets_path = root / "dry_run_targets.csv"
    summary_path = root / "dry_run_summary.json"

    checks: list[CheckResult] = []

    checks.append(
        CheckResult(
            "run_dir_exists",
            root.exists() and root.is_dir(),
            str(root),
        )
    )

    checks.append(
        CheckResult(
            "targets_csv_exists",
            targets_path.exists(),
            str(targets_path),
        )
    )

    checks.append(
        CheckResult(
            "summary_json_exists",
            summary_path.exists(),
            str(summary_path),
        )
    )

    if not targets_path.exists() or not summary_path.exists():
        return checks, pd.DataFrame(), {}

    df = pd.read_csv(targets_path)
    summary = _read_json(summary_path)

    checks.append(
        CheckResult(
            "targets_non_empty",
            not df.empty,
            f"rows={len(df)}",
        )
    )

    required_columns = [
        "symbol",
        "selected_prefix",
        "latest_bar_time",
        "raw_action",
        "confidence",
        "target_weight",
        "actual_weight",
        "intended_notional",
        "dry_run",
        "order_submitted",
        "note",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    checks.append(
        CheckResult(
            "required_columns_present",
            not missing_columns,
            f"missing={missing_columns}",
        )
    )

    if missing_columns or df.empty:
        return checks, df, summary

    # Expected symbols can be passed directly or inferred from the manifest.
    expected = [symbol.upper() for symbol in (expected_symbols or [])]
    if not expected:
        expected = _expected_symbols_from_manifest(manifest_path)

    actual_symbols = sorted(str(symbol).upper() for symbol in df["symbol"].dropna().unique())

    if expected:
        expected_sorted = sorted(expected)
        checks.append(
            CheckResult(
                "expected_symbols_present",
                actual_symbols == expected_sorted,
                f"actual={actual_symbols}; expected={expected_sorted}",
            )
        )

        symbol_counts = df["symbol"].astype(str).str.upper().value_counts().to_dict()
        duplicate_or_missing = {
            symbol: int(symbol_counts.get(symbol, 0))
            for symbol in expected_sorted
            if int(symbol_counts.get(symbol, 0)) != 1
        }
        checks.append(
            CheckResult(
                "one_row_per_expected_symbol",
                not duplicate_or_missing and len(df) == len(expected_sorted),
                f"counts={symbol_counts}",
            )
        )

    summary_rows = summary.get("rows")
    checks.append(
        CheckResult(
            "summary_rows_match_targets",
            int(summary_rows) == int(len(df)) if summary_rows is not None else False,
            f"summary_rows={summary_rows}; target_rows={len(df)}",
        )
    )

    summary_orders = summary.get("orders_submitted")
    checks.append(
        CheckResult(
            "summary_orders_submitted_zero",
            _is_zero_like(summary_orders),
            f"orders_submitted={summary_orders}",
        )
    )

    checks.append(
        CheckResult(
            "row_orders_submitted_zero",
            bool((pd.to_numeric(df["order_submitted"], errors="coerce").fillna(0) == 0).all()),
            f"unique={sorted(df['order_submitted'].astype(str).unique())}",
        )
    )

    checks.append(
        CheckResult(
            "dry_run_flag_all_one",
            bool((pd.to_numeric(df["dry_run"], errors="coerce").fillna(0) == 1).all()),
            f"unique={sorted(df['dry_run'].astype(str).unique())}",
        )
    )

    notes = df["note"].astype(str)
    checks.append(
        CheckResult(
            "no_dry_run_errors",
            not notes.str.contains("dry_run_error", case=False, na=False).any(),
            f"notes={sorted(notes.unique())}",
        )
    )

    checks.append(
        CheckResult(
            "all_predict_ok",
            bool((notes == "dry_run_predict_ok").all()),
            f"notes={sorted(notes.unique())}",
        )
    )

    latest_bar_time_ok = df["latest_bar_time"].astype(str).str.strip().ne("").all()
    latest_bar_time_ok = bool(latest_bar_time_ok and df["latest_bar_time"].notna().all())
    checks.append(
        CheckResult(
            "latest_bar_time_present",
            latest_bar_time_ok,
            f"missing={int(df['latest_bar_time'].isna().sum())}",
        )
    )

    finite_columns = [
        "raw_action",
        "confidence",
        "target_weight",
        "actual_weight",
        "intended_notional",
    ]

    for column in finite_columns:
        checks.append(
            CheckResult(
                f"{column}_finite",
                _finite_series(df, column),
                column,
            )
        )

    confidence_values = pd.to_numeric(df["confidence"], errors="coerce")
    confidence_ok = bool(((confidence_values >= 0.0) & (confidence_values <= 1.0)).all())
    checks.append(
        CheckResult(
            "confidence_between_0_and_1",
            confidence_ok,
            f"min={confidence_values.min()}; max={confidence_values.max()}",
        )
    )

    target_values = pd.to_numeric(df["target_weight"], errors="coerce")
    target_ok = bool((target_values.abs() <= float(max_abs_target_weight) + 1e-12).all())
    checks.append(
        CheckResult(
            "target_weight_within_bound",
            target_ok,
            f"max_abs={target_values.abs().max()}; bound={max_abs_target_weight}",
        )
    )

    summary_error_count = summary.get("error_count")
    checks.append(
        CheckResult(
            "summary_error_count_zero",
            _is_zero_like(summary_error_count),
            f"error_count={summary_error_count}",
        )
    )

    summary_predict_ok_count = summary.get("predict_ok_count")
    checks.append(
        CheckResult(
            "summary_predict_ok_count_matches",
            int(summary_predict_ok_count) == int(len(df)) if summary_predict_ok_count is not None else False,
            f"predict_ok_count={summary_predict_ok_count}; target_rows={len(df)}",
        )
    )

    return checks, df, summary


def print_report(checks: list[CheckResult], df: pd.DataFrame, summary: dict[str, Any]) -> None:
    print("=" * 80)
    print("ALPACA PAPER-TRADING DRY-RUN EVALUATION")
    print("=" * 80)

    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status:5} {check.name:35} {check.detail}")

    print()

    if not df.empty and "symbol" in df.columns:
        display_cols = [
            col
            for col in [
                "symbol",
                "selected_prefix",
                "raw_action",
                "confidence",
                "target_weight",
                "actual_weight",
                "intended_notional",
                "note",
            ]
            if col in df.columns
        ]

        print("Dry-run target summary:")
        print(df[display_cols].to_string(index=False))
        print()

    if summary:
        print("Summary:")
        print(f"rows={summary.get('rows')}")
        print(f"predict_ok_count={summary.get('predict_ok_count')}")
        print(f"error_count={summary.get('error_count')}")
        print(f"orders_submitted={summary.get('orders_submitted')}")
        print()

    passed = all(check.passed for check in checks)
    print("Evaluation result:", "PASS" if passed else "FAIL")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate Alpaca paper-trading dry-run output files."
    )
    parser.add_argument(
        "--run-dir",
        default=str(DEFAULT_RUN_DIR),
        help="Dry-run output directory containing dry_run_targets.csv and dry_run_summary.json.",
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Manifest used to infer expected symbols. Pass an empty string to disable.",
    )
    parser.add_argument(
        "--expected-symbols",
        nargs="*",
        default=None,
        help="Optional expected symbol list. Supports space-separated values.",
    )
    parser.add_argument(
        "--max-abs-target-weight",
        type=float,
        default=1.0,
        help="Maximum allowed absolute target weight.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    manifest_path: str | Path | None
    manifest_path = args.manifest if str(args.manifest).strip() else None

    checks, df, summary = validate_dry_run(
        run_dir=args.run_dir,
        expected_symbols=args.expected_symbols,
        manifest_path=manifest_path,
        max_abs_target_weight=args.max_abs_target_weight,
    )

    print_report(checks, df, summary)

    if not all(check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()