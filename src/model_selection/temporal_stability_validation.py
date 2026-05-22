"""Temporal stability validation for the v0.8 clean six-ticker PPO baseline.

This module evaluates whether the selected v0.8 paper-trading candidates are
stable across multiple out-of-sample walk-forward windows.

It does not retrain models.
It does not update the deployment manifest.
It does not submit paper orders.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = [
    "Ticker",
    "Window",
    "TrainRows",
    "EvalRows",
    "TrainStart",
    "TrainEnd",
    "EvalStart",
    "EvalEnd",
    "ValidationMode",
    "PPO_Portfolio",
    "BuyHold",
    "Sharpe",
    "Drawdown_%",
    "Winner",
]


def load_summary(summary_path: str | Path) -> pd.DataFrame:
    """Load and validate the walk-forward summary file."""
    path = Path(summary_path)

    if not path.exists():
        raise FileNotFoundError(f"Summary file not found: {path}")

    df = pd.read_csv(path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Summary missing required columns: {missing}")

    return df


def load_manifest(manifest_path: str | Path) -> dict[str, Any]:
    """Load and validate the paper-trading model manifest."""
    path = Path(manifest_path)

    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")

    manifest = json.loads(path.read_text(encoding="utf-8"))

    if "selected_models" not in manifest:
        raise KeyError("Manifest missing selected_models.")

    return manifest


def prepare_temporal_summary(
    df: pd.DataFrame,
    *,
    selected_models: dict[str, str],
    initial_balance: float = 100_000.0,
) -> pd.DataFrame:
    """Prepare summary rows and attach model prefixes."""
    tickers = list(selected_models.keys())
    data = df[df["Ticker"].isin(tickers)].copy()

    if data.empty:
        raise ValueError("No matching ticker rows found in summary.")

    for col in ["TrainRows", "EvalRows", "PPO_Portfolio", "BuyHold", "Sharpe", "Drawdown_%"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    for col in ["TrainStart", "TrainEnd", "EvalStart", "EvalEnd"]:
        data[col] = pd.to_datetime(data[col], utc=True)

    overlap = data[data["TrainEnd"] >= data["EvalStart"]]
    if not overlap.empty:
        raise ValueError("Train/eval overlap detected.")

    bad_mode = data[data["ValidationMode"] != "out_of_sample_eval_slice"]
    if not bad_mode.empty:
        raise ValueError("Unexpected ValidationMode found.")

    data = data.sort_values(["Ticker", "TrainStart", "EvalStart"]).reset_index(drop=True)
    data["WindowNumber"] = data.groupby("Ticker").cumcount() + 1
    data["ModelPrefix"] = data.apply(
        lambda row: f"ppo_{row['Ticker']}_window{int(row['WindowNumber'])}",
        axis=1,
    )

    data["PPO_Return_%"] = ((data["PPO_Portfolio"] / float(initial_balance)) - 1.0) * 100.0
    data["BuyHold_Return_%"] = ((data["BuyHold"] / float(initial_balance)) - 1.0) * 100.0
    data["Excess_vs_BuyHold_%"] = data["PPO_Return_%"] - data["BuyHold_Return_%"]
    data["PPO_Win"] = data["Winner"].astype(str).eq("PPO")

    return data


def selected_rows_from_manifest(
    prepared_df: pd.DataFrame,
    selected_models: dict[str, str],
) -> pd.DataFrame:
    """Return the selected row for each ticker based on manifest prefixes."""
    rows = []
    missing = []

    for ticker, prefix in selected_models.items():
        match = prepared_df[
            (prepared_df["Ticker"] == ticker)
            & (prepared_df["ModelPrefix"] == prefix)
        ]

        if match.empty:
            missing.append(f"{ticker}: {prefix}")
            continue

        rows.append(match.iloc[0].to_dict())

    if missing:
        raise ValueError(f"Selected manifest prefixes not found in summary: {missing}")

    return pd.DataFrame(rows).sort_values("Ticker").reset_index(drop=True)


def classify_stability(row: pd.Series) -> tuple[str, list[str]]:
    """Classify ticker stability from full-window and selected-window metrics."""
    flags: list[str] = []

    if float(row["SelectedSharpe"]) <= 0:
        flags.append("selected_sharpe_non_positive")

    if float(row["SharpeMean"]) < 0:
        flags.append("negative_mean_sharpe")

    if float(row["SharpeMin"]) < 0:
        flags.append("negative_window_sharpe")

    if float(row["MaxDrawdown_%"]) > 20:
        flags.append("max_drawdown_above_20pct")

    if float(row["SelectedDrawdown_%"]) > 20:
        flags.append("selected_drawdown_above_20pct")

    if float(row["PPOWinRate"]) < 0.50:
        flags.append("ppo_win_rate_below_50pct")

    if str(row["SelectedWinner"]) != "PPO":
        flags.append("selected_window_lost_to_buy_hold")

    strong = (
        float(row["SelectedSharpe"]) >= 0.75
        and float(row["SharpeMean"]) >= 0.50
        and float(row["SharpeMin"]) >= 0.0
        and float(row["MaxDrawdown_%"]) <= 20
        and float(row["PPOWinRate"]) >= 0.50
        and str(row["SelectedWinner"]) == "PPO"
    )

    watch = (
        float(row["SelectedSharpe"]) > 0
        and float(row["SharpeMean"]) >= 0
        and float(row["SelectedDrawdown_%"]) <= 20
    )

    if strong:
        return "Strong", flags

    if watch:
        return "Watch", flags

    return "High Risk", flags


def build_temporal_stability_report(
    prepared_df: pd.DataFrame,
    selected_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build ticker-level temporal stability summary."""
    selected_map = {
        row["Ticker"]: row
        for _, row in selected_df.iterrows()
    }

    rows: list[dict[str, Any]] = []

    for ticker, group in prepared_df.groupby("Ticker"):
        selected = selected_map[ticker]

        row = {
            "Ticker": ticker,
            "SelectedPrefix": selected["ModelPrefix"],
            "SelectedWindow": selected["Window"],
            "SelectedSharpe": float(selected["Sharpe"]),
            "SelectedDrawdown_%": float(selected["Drawdown_%"]),
            "SelectedPPO_Return_%": float(selected["PPO_Return_%"]),
            "SelectedExcess_vs_BuyHold_%": float(selected["Excess_vs_BuyHold_%"]),
            "SelectedWinner": selected["Winner"],
            "WindowsEvaluated": int(len(group)),
            "PPOWins": int(group["PPO_Win"].sum()),
            "PPOWinRate": float(group["PPO_Win"].mean()),
            "SharpeMean": float(group["Sharpe"].mean()),
            "SharpeMedian": float(group["Sharpe"].median()),
            "SharpeMin": float(group["Sharpe"].min()),
            "SharpeMax": float(group["Sharpe"].max()),
            "SharpeStd": float(group["Sharpe"].std(ddof=0)),
            "AvgDrawdown_%": float(group["Drawdown_%"].mean()),
            "MaxDrawdown_%": float(group["Drawdown_%"].max()),
            "AvgPPO_Return_%": float(group["PPO_Return_%"].mean()),
            "MinPPO_Return_%": float(group["PPO_Return_%"].min()),
            "MaxPPO_Return_%": float(group["PPO_Return_%"].max()),
            "AvgExcess_vs_BuyHold_%": float(group["Excess_vs_BuyHold_%"].mean()),
        }

        tier, flags = classify_stability(pd.Series(row))
        row["StabilityTier"] = tier
        row["StabilityFlags"] = ", ".join(flags) if flags else "none"

        rows.append(row)

    tier_order = {"Strong": 0, "Watch": 1, "High Risk": 2}
    report = pd.DataFrame(rows)
    report["StabilityTierOrder"] = report["StabilityTier"].map(tier_order)
    report = report.sort_values(
        ["StabilityTierOrder", "SharpeMean"],
        ascending=[True, False],
    ).drop(columns=["StabilityTierOrder"])

    return report.reset_index(drop=True)


def _fmt(value: Any, decimals: int = 3) -> str:
    try:
        return f"{float(value):,.{decimals}f}"
    except Exception:
        return str(value)


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    """Create a markdown table without requiring tabulate."""
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines = [header, divider]

    for _, row in df.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                values.append(_fmt(value, 3))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def write_outputs(
    *,
    prepared_df: pd.DataFrame,
    selected_df: pd.DataFrame,
    stability_df: pd.DataFrame,
    output_dir: str | Path,
    doc_path: str | Path,
    summary_path: str | Path,
    manifest_path: str | Path,
) -> dict[str, Path]:
    """Write temporal stability CSV and Markdown review outputs."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    all_windows_path = root / "v0_9_all_windows_temporal_metrics.csv"
    selected_path = root / "v0_9_selected_windows_temporal_metrics.csv"
    stability_path = root / "v0_9_temporal_stability_by_ticker.csv"

    prepared_df.to_csv(all_windows_path, index=False)
    selected_df.to_csv(selected_path, index=False)
    stability_df.to_csv(stability_path, index=False)

    tier_counts = stability_df["StabilityTier"].value_counts().to_dict()

    doc = f"""# v0.9 Temporal Stability Validation

## Purpose

Evaluate whether the v0.8 selected six-ticker PPO candidates are stable across multiple out-of-sample walk-forward evaluation windows.

This validation does not retrain models, update the deployment manifest, or submit paper orders.

## Inputs

Summary file:

```text
{summary_path}
```

Manifest file:

```text
{manifest_path}
```

## Method

The validation compares each selected manifest model against the ticker's full set of out-of-sample evaluation windows.

For each ticker, the report checks:

```text
selected-window Sharpe
selected-window drawdown
selected-window PPO return
selected-window excess return versus Buy & Hold
mean/median/min/max Sharpe across all windows
max drawdown across all windows
PPO win rate across all windows
whether selected window beat Buy & Hold
```

## Stability Tiers

```text
Strong    = selected candidate and ticker history are consistently strong
Watch     = selected candidate is usable but has stability warnings
High Risk = weak average behavior, negative Sharpe behavior, or poor selected-window profile
```

## Tier Summary

```json
{json.dumps(tier_counts, indent=2)}
```

## Temporal Stability by Ticker

{markdown_table(stability_df, [
"Ticker",
"SelectedPrefix",
"SelectedWindow",
"StabilityTier",
"SelectedSharpe",
"SharpeMean",
"SharpeMin",
"PPOWinRate",
"SelectedDrawdown_%",
"MaxDrawdown_%",
"SelectedWinner",
"StabilityFlags",
])}

## Selected Candidate Metrics

{markdown_table(selected_df, [
"Ticker",
"ModelPrefix",
"Window",
"Sharpe",
"Drawdown_%",
"PPO_Return_%",
"Excess_vs_BuyHold_%",
"Winner",
])}

## Interpretation

This validation should be used as a stability screen before longer paper-trading sessions.

Suggested interpretation:

```text
Strong    = reasonable candidate for next paper-trading validation stage
Watch     = candidate can be tested carefully, but monitor risk and signal behavior
High Risk = do not promote without additional review or temporal retest
```

## Next Step

Use this report to decide whether to:

```text
keep the v0.8 manifest selections unchanged
downgrade unstable tickers
run a newer-data temporal stability retrain
or proceed to QuantConnect execution-path retest
```
"""

    final_doc = Path(doc_path)
    final_doc.parent.mkdir(parents=True, exist_ok=True)
    final_doc.write_text(doc, encoding="utf-8")

    return {
        "all_windows_path": all_windows_path,
        "selected_path": selected_path,
        "stability_path": stability_path,
        "doc_path": final_doc,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run temporal stability validation for v0.8 selected PPO candidates."
    )
    parser.add_argument(
        "--summary-path",
        default="reports/backtests/ppo_walkforward_results_20260521_210445/summary_test_mode.csv",
    )
    parser.add_argument(
        "--manifest",
        default="config/paper_trading_six_ticker_manifest.json",
    )
    parser.add_argument(
        "--output-dir",
        default="reports/model_selection/v0_9_temporal_stability",
    )
    parser.add_argument(
        "--doc-path",
        default="docs/runs/v0.9_temporal_stability_validation.md",
    )
    parser.add_argument(
        "--initial-balance",
        type=float,
        default=100_000.0,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    manifest = load_manifest(args.manifest)
    selected_models = manifest["selected_models"]

    summary = load_summary(args.summary_path)
    prepared = prepare_temporal_summary(
        summary,
        selected_models=selected_models,
        initial_balance=args.initial_balance,
    )
    selected = selected_rows_from_manifest(prepared, selected_models)
    stability = build_temporal_stability_report(prepared, selected)

    outputs = write_outputs(
        prepared_df=prepared,
        selected_df=selected,
        stability_df=stability,
        output_dir=args.output_dir,
        doc_path=args.doc_path,
        summary_path=args.summary_path,
        manifest_path=args.manifest,
    )

    print("=" * 80)
    print("v0.9 TEMPORAL STABILITY VALIDATION")
    print("=" * 80)
    print(
        stability[
            [
                "Ticker",
                "SelectedPrefix",
                "StabilityTier",
                "SelectedSharpe",
                "SharpeMean",
                "SharpeMin",
                "PPOWinRate",
                "SelectedDrawdown_%",
                "MaxDrawdown_%",
                "SelectedWinner",
                "StabilityFlags",
            ]
        ].to_string(index=False)
    )
    print()

    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
