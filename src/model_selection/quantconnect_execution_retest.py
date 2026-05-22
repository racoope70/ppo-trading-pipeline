"""QuantConnect execution-path retest and broker-simulation comparison.

This module validates the local QuantConnect-style signal path without importing
QuantConnect LEAN modules such as AlgorithmImports.

It does not run a LEAN backtest.
It does not submit Alpaca orders.
It does not update the paper-trading manifest.

Validation flow:
1. Read paper-trading dry-run targets.
2. Build a QuantConnect-compatible signal payload.
3. Independently simulate execution from those signals using the same execution
   rules as the paper-trading execution layer.
4. Compare the simulated QuantConnect-style execution plan to the local
   paper-trading execution_plan.csv.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

from src.adapters.quantconnect import build_quantconnect_payload
from src.paper_trading.execution import (
    ExecutionConfig,
    build_rebalance_intents_from_targets,
    summarize_intents,
)


REQUIRED_TARGET_COLUMNS = [
    "symbol",
    "selected_prefix",
    "raw_action",
    "confidence",
    "target_weight",
    "actual_weight",
    "intended_notional",
    "note",
]

REQUIRED_PLAN_COLUMNS = [
    "symbol",
    "side",
    "qty",
    "price",
    "target_weight",
    "actual_weight",
    "delta_notional",
    "should_order",
]


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a JSON object from disk."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def load_manifest_selected_models(manifest_path: str | Path) -> dict[str, str]:
    """Load selected model prefixes from a paper-trading manifest."""
    manifest = load_json(manifest_path)
    selected = manifest.get("selected_models")

    if not isinstance(selected, dict) or not selected:
        raise ValueError("Manifest missing selected_models.")

    return {str(k).upper(): str(v) for k, v in selected.items()}


def load_dry_run_targets(run_dir: str | Path) -> pd.DataFrame:
    """Load dry-run target rows from a paper-trading run directory."""
    path = Path(run_dir) / "dry_run_targets.csv"

    if not path.exists():
        raise FileNotFoundError(f"Dry-run targets not found: {path}")

    df = pd.read_csv(path)

    missing = [col for col in REQUIRED_TARGET_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Dry-run targets missing columns: {missing}")

    return df


def load_paper_execution_plan(run_dir: str | Path) -> pd.DataFrame:
    """Load local paper-trading execution plan rows."""
    path = Path(run_dir) / "execution_plan.csv"

    if not path.exists():
        raise FileNotFoundError(f"Execution plan not found: {path}")

    df = pd.read_csv(path)

    missing = [col for col in REQUIRED_PLAN_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Execution plan missing columns: {missing}")

    return df


def action_to_qc_signal(action: float) -> str:
    """Convert PPO action into a simple external signal label."""
    value = float(action)

    if value > 0.10:
        return "BUY"

    if value < -0.30:
        return "SELL"

    return "HOLD"


def validate_manifest_prefixes(
    targets: pd.DataFrame,
    selected_models: dict[str, str],
) -> list[str]:
    """Return manifest mismatch messages."""
    mismatches: list[str] = []

    for _, row in targets.iterrows():
        symbol = str(row["symbol"]).upper()
        actual_prefix = str(row["selected_prefix"])
        expected_prefix = selected_models.get(symbol)

        if expected_prefix is None:
            mismatches.append(f"{symbol}: missing from manifest")
            continue

        if actual_prefix != expected_prefix:
            mismatches.append(
                f"{symbol}: target prefix={actual_prefix}, manifest prefix={expected_prefix}"
            )

    return mismatches


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        if math.isfinite(result):
            return result
    except Exception:
        pass
    return float(default)


def build_qc_models_from_targets(
    targets: pd.DataFrame,
    execution_plan: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Build QuantConnect-style model signals from dry-run target rows."""
    price_map = {
        str(row["symbol"]).upper(): _safe_float(row["price"])
        for _, row in execution_plan.iterrows()
        if pd.notna(row.get("price"))
    }

    models: list[dict[str, Any]] = []

    for _, row in targets.iterrows():
        symbol = str(row["symbol"]).upper()
        raw_action = _safe_float(row["raw_action"])
        timestamp = row.get("latest_bar_time", row.get("timestamp", ""))

        models.append(
            {
                "symbol": symbol,
                "prefix": str(row["selected_prefix"]),
                "timestamp": str(timestamp),
                "price": _safe_float(price_map.get(symbol, row.get("latest_price", 0.0))),
                "signal": action_to_qc_signal(raw_action),
                "confidence": _safe_float(row["confidence"]),
                "action": raw_action,
                "target_weight": _safe_float(row["target_weight"]),
                "actual_weight": _safe_float(row["actual_weight"]),
                "intended_notional": _safe_float(row["intended_notional"]),
                "source_note": str(row["note"]),
            }
        )

    return models


def prepare_targets_for_qc_execution(
    targets: pd.DataFrame,
    execution_plan: pd.DataFrame,
    *,
    equity: float = 100_000.0,
) -> pd.DataFrame:
    """Convert dry-run targets into the shape expected by execution utilities."""
    plan_by_symbol = {
        str(row["symbol"]).upper(): row
        for _, row in execution_plan.iterrows()
    }

    rows: list[dict[str, Any]] = []

    for _, row in targets.iterrows():
        symbol = str(row["symbol"]).upper()
        plan_row = plan_by_symbol.get(symbol, {})

        price = row.get("latest_price", plan_row.get("price", float("nan")))
        row_equity = row.get("equity", plan_row.get("equity", equity))
        actual_weight = _safe_float(row.get("actual_weight", 0.0))
        actual_market_value = row.get(
            "actual_market_value",
            actual_weight * _safe_float(row_equity, equity),
        )

        rows.append(
            {
                "symbol": symbol,
                "selected_prefix": str(row["selected_prefix"]),
                "target_weight": _safe_float(row.get("target_weight", 0.0)),
                "actual_weight": actual_weight,
                "actual_qty": _safe_float(row.get("actual_qty", 0.0)),
                "actual_market_value": _safe_float(actual_market_value),
                "latest_price": _safe_float(price, float("nan")),
                "equity": _safe_float(row_equity, equity),
            }
        )

    return pd.DataFrame(rows)


def simulate_qc_broker_execution(
    targets: pd.DataFrame,
    execution_plan: pd.DataFrame,
    *,
    equity: float = 100_000.0,
    min_notional: float = 25.0,
    max_abs_weight: float = 0.40,
    allow_shorts: bool = False,
    use_fractionals: bool = True,
) -> pd.DataFrame:
    """Simulate QuantConnect-style execution from target weights."""
    prepared_targets = prepare_targets_for_qc_execution(
        targets,
        execution_plan,
        equity=equity,
    )

    config = ExecutionConfig(
        min_notional=min_notional,
        max_abs_weight=max_abs_weight,
        allow_shorts=allow_shorts,
        use_fractionals=use_fractionals,
        dry_run=True,
    )

    return build_rebalance_intents_from_targets(
        prepared_targets,
        config=config,
    )


def _bool_value(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def compare_qc_to_paper_execution(
    qc_simulated: pd.DataFrame,
    paper_plan: pd.DataFrame,
    *,
    qty_tolerance: float = 1e-6,
    notional_tolerance: float = 1e-4,
) -> pd.DataFrame:
    """Compare simulated QuantConnect execution to local paper execution plan."""
    left = qc_simulated.copy()
    right = paper_plan.copy()

    left["symbol"] = left["symbol"].astype(str).str.upper()
    right["symbol"] = right["symbol"].astype(str).str.upper()

    merged = left.merge(
        right,
        on="symbol",
        how="outer",
        suffixes=("_qc", "_paper"),
        indicator=True,
    )

    rows: list[dict[str, Any]] = []

    for _, row in merged.iterrows():
        symbol = row["symbol"]

        qc_qty = _safe_float(row.get("qty_qc", 0.0))
        paper_qty = _safe_float(row.get("qty_paper", 0.0))
        qc_delta = _safe_float(row.get("delta_notional_qc", 0.0))
        paper_delta = _safe_float(row.get("delta_notional_paper", 0.0))

        side_match = str(row.get("side_qc", "")) == str(row.get("side_paper", ""))
        should_order_match = _bool_value(row.get("should_order_qc")) == _bool_value(
            row.get("should_order_paper")
        )
        qty_match = abs(qc_qty - paper_qty) <= qty_tolerance
        delta_match = abs(qc_delta - paper_delta) <= notional_tolerance
        merge_match = str(row.get("_merge")) == "both"

        all_match = all(
            [
                merge_match,
                side_match,
                should_order_match,
                qty_match,
                delta_match,
            ]
        )

        rows.append(
            {
                "symbol": symbol,
                "merge_status": row.get("_merge"),
                "qc_side": row.get("side_qc"),
                "paper_side": row.get("side_paper"),
                "side_match": side_match,
                "qc_should_order": _bool_value(row.get("should_order_qc")),
                "paper_should_order": _bool_value(row.get("should_order_paper")),
                "should_order_match": should_order_match,
                "qc_qty": qc_qty,
                "paper_qty": paper_qty,
                "qty_match": qty_match,
                "qc_delta_notional": qc_delta,
                "paper_delta_notional": paper_delta,
                "delta_notional_match": delta_match,
                "comparison_passed": all_match,
            }
        )

    return pd.DataFrame(rows).sort_values("symbol").reset_index(drop=True)


def summarize_retest(
    *,
    targets: pd.DataFrame,
    qc_payload: dict[str, Any],
    qc_simulated: pd.DataFrame,
    comparison: pd.DataFrame,
    prefix_mismatches: list[str],
) -> dict[str, Any]:
    """Build compact retest summary."""
    intent_summary = summarize_intents(qc_simulated)
    comparison_passed = bool(comparison["comparison_passed"].all())
    manifest_prefixes_passed = len(prefix_mismatches) == 0

    return {
        "rows": int(len(targets)),
        "payload_models": int(len(qc_payload.get("models", []))),
        "manifest_prefixes_passed": manifest_prefixes_passed,
        "prefix_mismatches": prefix_mismatches,
        "qc_orders_required": int(intent_summary["orders_required"]),
        "qc_gross_intended_notional": float(intent_summary["gross_intended_notional"]),
        "comparison_passed": comparison_passed,
        "comparison_failures": comparison.loc[
            ~comparison["comparison_passed"], "symbol"
        ].astype(str).tolist(),
        "retest_passed": bool(manifest_prefixes_passed and comparison_passed),
    }


def _markdown_list(lines: list[str]) -> str:
    if not lines:
        return "none"
    return "\n".join(lines)


def write_outputs(
    *,
    output_dir: str | Path,
    doc_path: str | Path,
    qc_payload: dict[str, Any],
    qc_simulated: pd.DataFrame,
    comparison: pd.DataFrame,
    summary: dict[str, Any],
    run_dir: str | Path,
    manifest_path: str | Path,
) -> dict[str, Path]:
    """Write retest outputs."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    payload_path = root / "quantconnect_signal_payload.json"
    simulated_path = root / "quantconnect_simulated_execution_plan.csv"
    comparison_path = root / "quantconnect_paper_execution_comparison.csv"
    summary_path = root / "quantconnect_execution_retest_summary.json"

    payload_path.write_text(
        json.dumps(qc_payload, indent=2, default=str),
        encoding="utf-8",
    )
    qc_simulated.to_csv(simulated_path, index=False)
    comparison.to_csv(comparison_path, index=False)
    summary_path.write_text(
        json.dumps(summary, indent=2, default=str),
        encoding="utf-8",
    )

    final_doc = Path(doc_path)
    final_doc.parent.mkdir(parents=True, exist_ok=True)

    selected_lines = [
        f"{model['symbol']}: {model['prefix']} | signal={model['signal']} | target_weight={model['target_weight']}"
        for model in qc_payload.get("models", [])
    ]

    doc = f"""# v1.0 QuantConnect Execution-Path Retest

## Purpose

Validate that the v0.8 selected paper-trading models can pass through a QuantConnect-style signal path and produce broker-simulation results consistent with the local paper-trading execution plan.

This is a local compatibility retest. It does not import `AlgorithmImports`, does not run a LEAN backtest, and does not submit orders.

## Inputs

Paper dry-run directory:

```text
{run_dir}
```

Manifest:

```text
{manifest_path}
```

## Selected Model Signals

```text
{_markdown_list(selected_lines)}
```

## Retest Summary

```json
{json.dumps(summary, indent=2)}
```

## Comparison Result

```text
{"PASS" if summary["retest_passed"] else "FAIL"}
```

## Local Outputs

```text
{payload_path}
{simulated_path}
{comparison_path}
{summary_path}
```

## Interpretation

This validates the execution-path compatibility layer:

```text
v0.8 manifest selections
paper dry-run target outputs
QuantConnect-style signal payload
local broker-simulation comparison
paper execution-plan parity check
```

A passing result means the selected v0.8 candidates can be represented as QuantConnect-style external signals and produce the same local execution intent behavior as the paper-trading execution plan.

## Next Step

If this passes, the next checkpoint can be either:

```text
v1.1 controlled Alpaca paper-order test
```

or a true QuantConnect/LEAN IDE backtest using the generated signal payload.
"""

    final_doc.write_text(doc, encoding="utf-8")

    return {
        "payload_path": payload_path,
        "simulated_path": simulated_path,
        "comparison_path": comparison_path,
        "summary_path": summary_path,
        "doc_path": final_doc,
    }


def run_quantconnect_execution_retest(
    *,
    run_dir: str | Path,
    manifest_path: str | Path,
    output_dir: str | Path,
    doc_path: str | Path,
    equity: float = 100_000.0,
    valid_minutes: int = 1440,
    interval: str = "1h",
) -> tuple[dict[str, Any], dict[str, Path]]:
    """Run complete QuantConnect execution-path retest."""
    selected_models = load_manifest_selected_models(manifest_path)
    targets = load_dry_run_targets(run_dir)
    paper_plan = load_paper_execution_plan(run_dir)

    prefix_mismatches = validate_manifest_prefixes(targets, selected_models)

    qc_models = build_qc_models_from_targets(targets, paper_plan)
    qc_payload = build_quantconnect_payload(
        predictions=qc_models,
        valid_minutes=valid_minutes,
        interval=interval,
        producer="ppo_research_pipeline_v1_0_execution_retest",
    )

    qc_simulated = simulate_qc_broker_execution(
        targets,
        paper_plan,
        equity=equity,
    )

    comparison = compare_qc_to_paper_execution(qc_simulated, paper_plan)

    summary = summarize_retest(
        targets=targets,
        qc_payload=qc_payload,
        qc_simulated=qc_simulated,
        comparison=comparison,
        prefix_mismatches=prefix_mismatches,
    )

    outputs = write_outputs(
        output_dir=output_dir,
        doc_path=doc_path,
        qc_payload=qc_payload,
        qc_simulated=qc_simulated,
        comparison=comparison,
        summary=summary,
        run_dir=run_dir,
        manifest_path=manifest_path,
    )

    return summary, outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run QuantConnect execution-path retest against paper execution plan."
    )
    parser.add_argument(
        "--run-dir",
        default="reports/paper_trading_dry_runs/latest",
    )
    parser.add_argument(
        "--manifest",
        default="config/paper_trading_six_ticker_manifest.json",
    )
    parser.add_argument(
        "--output-dir",
        default="reports/model_selection/v1_0_quantconnect_execution_retest",
    )
    parser.add_argument(
        "--doc-path",
        default="docs/runs/v1.0_quantconnect_execution_path_retest.md",
    )
    parser.add_argument(
        "--equity",
        type=float,
        default=100_000.0,
    )
    parser.add_argument(
        "--valid-minutes",
        type=int,
        default=1440,
    )
    parser.add_argument(
        "--interval",
        default="1h",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    summary, outputs = run_quantconnect_execution_retest(
        run_dir=args.run_dir,
        manifest_path=args.manifest,
        output_dir=args.output_dir,
        doc_path=args.doc_path,
        equity=args.equity,
        valid_minutes=args.valid_minutes,
        interval=args.interval,
    )

    print("=" * 80)
    print("v1.0 QUANTCONNECT EXECUTION-PATH RETEST")
    print("=" * 80)
    print(json.dumps(summary, indent=2))

    print()
    for name, path in outputs.items():
        print(f"{name}: {path}")

    if not summary["retest_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
