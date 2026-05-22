"""Select clean six-ticker PPO deployment candidates from a v0.8 retrain.

This selector reads a walk-forward summary file and chooses one model window
per ticker. It does not update the paper-trading manifest. It writes a proposed
selection review so the deployment manifest can be updated in a separate,
intentional checkpoint.

Selection logic:
- compute PPO return percentage
- compute excess return versus Buy & Hold
- compute a transparent risk-adjusted score
- select the highest-scoring window per ticker
- validate that selected artifacts exist
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


SIX_TICKERS = ["AAPL", "AMD", "MRK", "PFE", "UNH", "XOM"]

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

ARTIFACT_SUFFIXES = [
    "_model.zip",
    "_vecnorm.pkl",
    "_features.json",
    "_probability_config.json",
    "_model_info.json",
]


def latest_summary_path() -> Path:
    """Return the newest summary file under reports/backtests."""
    runs = sorted(
        Path("reports/backtests").glob("ppo_walkforward_results_*"),
        key=lambda path: path.stat().st_mtime,
    )

    if not runs:
        raise FileNotFoundError("No reports/backtests/ppo_walkforward_results_* folders found.")

    latest = runs[-1]

    for name in ["summary_test_mode.csv", "summary.csv"]:
        candidate = latest / name
        if candidate.exists():
            return candidate

    raise FileNotFoundError(f"No summary CSV found in {latest}")


def load_summary(summary_path: str | Path) -> pd.DataFrame:
    """Load and validate a PPO walk-forward summary file."""
    path = Path(summary_path)

    if not path.exists():
        raise FileNotFoundError(f"Summary file not found: {path}")

    df = pd.read_csv(path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Summary is missing required columns: {missing}")

    return df


def prepare_summary(
    df: pd.DataFrame,
    *,
    tickers: list[str] | None = None,
    initial_balance: float = 100_000.0,
) -> pd.DataFrame:
    """Add selection fields and artifact prefixes."""
    selected_tickers = tickers or SIX_TICKERS
    data = df[df["Ticker"].isin(selected_tickers)].copy()

    if data.empty:
        raise ValueError(f"No rows found for tickers: {selected_tickers}")

    for col in ["TrainRows", "EvalRows", "PPO_Portfolio", "BuyHold", "Sharpe", "Drawdown_%"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data["TrainStart"] = pd.to_datetime(data["TrainStart"], utc=True)
    data["TrainEnd"] = pd.to_datetime(data["TrainEnd"], utc=True)
    data["EvalStart"] = pd.to_datetime(data["EvalStart"], utc=True)
    data["EvalEnd"] = pd.to_datetime(data["EvalEnd"], utc=True)

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

    data["SelectionScore"] = (
        data["Sharpe"]
        - (0.03 * data["Drawdown_%"])
        + (0.005 * data["PPO_Return_%"])
        + data["PPO_Win"].astype(float) * 0.25
    )

    return data


def select_candidates(prepared_df: pd.DataFrame) -> pd.DataFrame:
    """Select the top-scoring model window per ticker."""
    ranked = prepared_df.sort_values(
        ["Ticker", "SelectionScore", "Sharpe", "Drawdown_%"],
        ascending=[True, False, False, True],
    ).copy()

    selected = ranked.groupby("Ticker", as_index=False).head(1)
    return selected.sort_values("Ticker").reset_index(drop=True)


def validate_selected_artifacts(
    selected_df: pd.DataFrame,
    *,
    model_dir: str | Path,
) -> tuple[pd.DataFrame, list[str]]:
    """Validate artifact files for selected model prefixes."""
    root = Path(model_dir)
    rows: list[dict[str, Any]] = []
    missing_messages: list[str] = []

    for _, row in selected_df.iterrows():
        prefix = str(row["ModelPrefix"])
        record: dict[str, Any] = {
            "Ticker": row["Ticker"],
            "ModelPrefix": prefix,
        }

        for suffix in ARTIFACT_SUFFIXES:
            path = root / f"{prefix}{suffix}"
            key = suffix.strip("_").replace(".", "_")
            exists = path.exists()
            record[key] = exists

            if not exists:
                missing_messages.append(f"{prefix}{suffix}")

        rows.append(record)

    return pd.DataFrame(rows), missing_messages


def build_manifest_patch(selected_df: pd.DataFrame, run_dir: str | Path) -> dict[str, Any]:
    """Build proposed manifest patch data without modifying the real manifest."""
    selected_models = {
        str(row["Ticker"]): str(row["ModelPrefix"])
        for _, row in selected_df.iterrows()
    }

    return {
        "artifact_manifest_version": "0.8-candidate-review",
        "baseline_name": "clean_six_ticker_ppo_v0_8_candidate_baseline",
        "source_git_tag": "v0.8-clean-six-ticker-ppo-baseline",
        "universe": SIX_TICKERS,
        "selected_models": selected_models,
        "source_validation": {
            "validation_type": "out_of_sample_eval_slice_six_ticker_retrain",
            "run_dir": str(run_dir),
            "rows": int(len(selected_df)),
            "selection_method": "risk_adjusted_score_v1",
        },
        "notes": [
            "This is a candidate patch only.",
            "Do not update config/paper_trading_six_ticker_manifest.json until the candidate review is accepted.",
            "Selection uses v0.8 clean retrain metrics with out-of-sample eval slices.",
        ],
    }


def _fmt_number(value: Any, decimals: int = 3) -> str:
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
                if col in {"PPO_Portfolio", "BuyHold"}:
                    values.append(_fmt_number(value, 2))
                else:
                    values.append(_fmt_number(value, 3))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def write_outputs(
    *,
    prepared_df: pd.DataFrame,
    selected_df: pd.DataFrame,
    artifact_df: pd.DataFrame,
    manifest_patch: dict[str, Any],
    output_dir: str | Path,
    doc_path: str | Path | None = None,
    source_summary_path: str | Path,
    run_dir: str | Path,
    missing_artifacts: list[str],
) -> dict[str, Path]:
    """Write selector CSV/JSON/Markdown outputs."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    ranked_path = root / "v0_8_all_windows_ranked.csv"
    selected_path = root / "v0_8_selected_candidates.csv"
    artifacts_path = root / "v0_8_selected_artifact_check.csv"
    manifest_patch_path = root / "v0_8_candidate_manifest_patch.json"

    ranked = prepared_df.sort_values(
        ["Ticker", "SelectionScore"],
        ascending=[True, False],
    )

    ranked.to_csv(ranked_path, index=False)
    selected_df.to_csv(selected_path, index=False)
    artifact_df.to_csv(artifacts_path, index=False)
    manifest_patch_path.write_text(
        json.dumps(manifest_patch, indent=2, default=str),
        encoding="utf-8",
    )

    final_doc_path = Path(doc_path) if doc_path is not None else root / "v0_8_candidate_selection.md"
    final_doc_path.parent.mkdir(parents=True, exist_ok=True)

    ppo_wins = int(prepared_df["PPO_Win"].sum())
    total_windows = int(len(prepared_df))
    selected_columns = [
        "Ticker",
        "Window",
        "WindowNumber",
        "ModelPrefix",
        "SelectionScore",
        "Sharpe",
        "Drawdown_%",
        "PPO_Return_%",
        "Excess_vs_BuyHold_%",
        "Winner",
    ]

    doc = f"""# v0.8 Clean Six-Ticker Candidate Selection

## Purpose

Select one clean PPO model-window candidate per ticker from the v0.8 retrain.

This is a candidate-selection review. It does not update the paper-trading deployment manifest.

## Source Run

```text
{run_dir}
```

Summary file:

```text
{source_summary_path}
```

## Selection Method

The selector uses a transparent risk-adjusted score:

```text
SelectionScore =
    Sharpe
    - 0.03 * Drawdown_%
    + 0.005 * PPO_Return_%
    + 0.25 if PPO beat Buy & Hold
```

This gives priority to Sharpe, penalizes drawdown, modestly rewards positive PPO return, and gives a small bonus when PPO beats Buy & Hold.

## Overall Window Summary

```text
Total evaluated windows: {total_windows}
PPO wins: {ppo_wins}
Buy & Hold wins: {total_windows - ppo_wins}
Average Sharpe: {_fmt_number(prepared_df["Sharpe"].mean(), 3)}
Average Drawdown %: {_fmt_number(prepared_df["Drawdown_%"].mean(), 2)}
Average SelectionScore: {_fmt_number(prepared_df["SelectionScore"].mean(), 3)}
```

## Selected Candidates

{markdown_table(selected_df, selected_columns)}

## Proposed selected_models Patch

```json
{json.dumps(manifest_patch["selected_models"], indent=2)}
```

## Artifact Validation

{markdown_table(artifact_df, list(artifact_df.columns))}

Artifact validation result:

```text
{"PASS" if not missing_artifacts else "FAIL"}
```

## Notes

Generated selector CSV/JSON files are local review outputs. The deployment manifest should be updated in a separate checkpoint only after this candidate review is accepted.

Recommended next checkpoint:

```text
v0.8 Step 3: Update paper trading manifest with selected v0.8 candidates
```
"""

    final_doc_path.write_text(doc, encoding="utf-8")

    return {
        "ranked_path": ranked_path,
        "selected_path": selected_path,
        "artifacts_path": artifacts_path,
        "manifest_patch_path": manifest_patch_path,
        "doc_path": final_doc_path,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select v0.8 clean six-ticker PPO deployment candidates."
    )
    parser.add_argument(
        "--summary-path",
        default=None,
        help="Path to summary_test_mode.csv or summary.csv. Default: latest backtest summary.",
    )
    parser.add_argument(
        "--model-dir",
        default="models/ppo_models_master",
        help="Directory containing PPO model artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        default="reports/model_selection/v0_8_clean_six_ticker",
        help="Directory for selector review outputs.",
    )
    parser.add_argument(
        "--doc-path",
        default="docs/runs/v0.8_clean_six_ticker_candidate_selection.md",
        help="Markdown note path to write for Git documentation.",
    )
    parser.add_argument(
        "--initial-balance",
        type=float,
        default=100_000.0,
        help="Initial balance used to compute PPO return percentage.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    summary_path = Path(args.summary_path) if args.summary_path else latest_summary_path()
    run_dir = summary_path.parent

    summary = load_summary(summary_path)
    prepared = prepare_summary(summary, initial_balance=args.initial_balance)
    selected = select_candidates(prepared)

    artifact_df, missing_artifacts = validate_selected_artifacts(
        selected,
        model_dir=args.model_dir,
    )

    manifest_patch = build_manifest_patch(selected, run_dir=run_dir)

    outputs = write_outputs(
        prepared_df=prepared,
        selected_df=selected,
        artifact_df=artifact_df,
        manifest_patch=manifest_patch,
        output_dir=args.output_dir,
        doc_path=args.doc_path,
        source_summary_path=summary_path,
        run_dir=run_dir,
        missing_artifacts=missing_artifacts,
    )

    print("=" * 80)
    print("v0.8 CLEAN SIX-TICKER CANDIDATE SELECTION")
    print("=" * 80)
    print(f"Summary path: {summary_path}")
    print(f"Model dir: {args.model_dir}")
    print()
    print(
        selected[
            [
                "Ticker",
                "Window",
                "WindowNumber",
                "ModelPrefix",
                "SelectionScore",
                "Sharpe",
                "Drawdown_%",
                "PPO_Return_%",
                "Excess_vs_BuyHold_%",
                "Winner",
            ]
        ].to_string(index=False)
    )
    print()
    print("Artifact validation:", "PASS" if not missing_artifacts else "FAIL")
    if missing_artifacts:
        for item in missing_artifacts:
            print("MISSING:", item)
        raise SystemExit(1)

    print()
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
