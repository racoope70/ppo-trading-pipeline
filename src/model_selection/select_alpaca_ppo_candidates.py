"""Select Alpaca PPO candidates for paper-trading redeployment.

v1.9 scope:
- Read v1.8.5 final holdout validation results.
- Select one paper-trading candidate per ticker.
- Require candidates to pass holdout validation.
- Prefer higher holdout Sharpe, lower drawdown, and stable final portfolio.
- Validate required paper-trading artifacts exist.
- Build a proposed or actual paper-trading manifest update.

This module does not submit orders.
This module does not run live/paper inference.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.paper_trading.artifact_manifest import resolve_artifact_paths


SIX_TICKERS = ["AAPL", "AMD", "MRK", "PFE", "UNH", "XOM"]

REQUIRED_HOLDOUT_COLUMNS = [
    "Ticker",
    "Prefix",
    "ValidationSharpe",
    "Sharpe",
    "Drawdown_%",
    "PPO_Portfolio",
    "BuyHold",
    "PassedHoldout",
    "Evaluated",
    "HoldoutRows",
]


def read_json(path: str | Path) -> dict[str, Any]:
    """Read a JSON object from disk."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {p}")

    payload = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {p}")

    return payload


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    """Write a JSON object to disk."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return p


def load_holdout_candidates(summary_path: str | Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load v1.8.5 final holdout summary candidate rows."""
    summary = read_json(summary_path)
    rows = summary.get("candidate_results", [])

    if not rows:
        raise ValueError(f"No candidate_results found in {summary_path}")

    df = pd.DataFrame(rows)

    missing = [col for col in REQUIRED_HOLDOUT_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Holdout candidate results missing columns: {missing}")

    df["Ticker"] = df["Ticker"].astype(str).str.upper()
    df["Prefix"] = df["Prefix"].astype(str)

    for col in [
        "ValidationSharpe",
        "Sharpe",
        "Drawdown_%",
        "PPO_Portfolio",
        "BuyHold",
        "HoldoutRows",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["PassedHoldout"] = df["PassedHoldout"].astype(bool)
    df["Evaluated"] = df["Evaluated"].astype(bool)

    return df, summary


def prepare_candidates(
    df: pd.DataFrame,
    *,
    universe: list[str] | None = None,
    min_holdout_rows: int = 60,
    min_promotion_sharpe: float = 0.0,
    min_final_portfolio: float = 95_000.0,
) -> pd.DataFrame:
    """Filter and score candidates for promotion."""
    selected_universe = universe or SIX_TICKERS
    data = df[df["Ticker"].isin(selected_universe)].copy()

    if data.empty:
        raise ValueError(f"No holdout candidates found for universe: {selected_universe}")

    for col in [
        "ValidationSharpe",
        "Sharpe",
        "Drawdown_%",
        "PPO_Portfolio",
        "BuyHold",
        "HoldoutRows",
    ]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    eligible = (
        data["Evaluated"].astype(bool)
        & data["PassedHoldout"].astype(bool)
        & (data["HoldoutRows"] >= int(min_holdout_rows))
        & (data["Sharpe"] >= float(min_promotion_sharpe))
        & (data["PPO_Portfolio"] >= float(min_final_portfolio))
    )
    data["EligibleForPromotion"] = eligible.map(bool).astype(object)

    data["PPO_Return_%"] = ((data["PPO_Portfolio"] / 100_000.0) - 1.0) * 100.0
    data["BuyHold_Return_%"] = ((data["BuyHold"] / 100_000.0) - 1.0) * 100.0
    data["Excess_vs_BuyHold_%"] = data["PPO_Return_%"] - data["BuyHold_Return_%"]

    # Holdout Sharpe dominates, drawdown is penalized, positive final portfolio helps.
    data["PromotionScore"] = (
        data["Sharpe"]
        - 0.10 * data["Drawdown_%"]
        + 0.005 * data["PPO_Return_%"]
        + data["PassedHoldout"].astype(float) * 0.25
    )

    missing_tickers = sorted(set(selected_universe) - set(data["Ticker"].unique()))
    if missing_tickers:
        raise ValueError(f"Missing tickers from holdout candidate results: {missing_tickers}")

    eligible_by_ticker = data.groupby("Ticker")["EligibleForPromotion"].sum()
    no_eligible = sorted(eligible_by_ticker[eligible_by_ticker == 0].index.tolist())

    if no_eligible:
        raise ValueError(f"No eligible holdout-passing candidates for: {no_eligible}")

    return data.sort_values(["Ticker", "PromotionScore"], ascending=[True, False])


def select_one_per_ticker(prepared_df: pd.DataFrame) -> pd.DataFrame:
    """Select one eligible candidate per ticker."""
    eligible = prepared_df[prepared_df["EligibleForPromotion"].astype(bool)].copy()

    selected = (
        eligible.sort_values(
            ["Ticker", "PromotionScore", "Sharpe", "Drawdown_%", "PPO_Portfolio"],
            ascending=[True, False, False, True, False],
        )
        .groupby("Ticker", as_index=False)
        .head(1)
        .sort_values("Ticker")
        .reset_index(drop=True)
    )

    return selected


def validate_selected_artifacts(
    selected_df: pd.DataFrame,
    *,
    artifacts_dir: str | Path,
) -> tuple[pd.DataFrame, list[str]]:
    """Validate model, VecNormalize, and features artifacts for selected candidates."""
    root = Path(artifacts_dir)
    rows: list[dict[str, Any]] = []
    missing: list[str] = []

    for _, row in selected_df.iterrows():
        prefix = str(row["Prefix"])
        paths = resolve_artifact_paths(root, prefix)

        record = {
            "Ticker": row["Ticker"],
            "Prefix": prefix,
            "model_zip": str(paths["model_zip"]) if paths["model_zip"] else "",
            "vecnormalize_pkl": str(paths["vecnormalize_pkl"]) if paths["vecnormalize_pkl"] else "",
            "features_json": str(paths["features_json"]) if paths["features_json"] else "",
            "model_zip_exists": paths["model_zip"] is not None,
            "vecnormalize_pkl_exists": paths["vecnormalize_pkl"] is not None,
            "features_json_exists": paths["features_json"] is not None,
        }

        record["all_required_artifacts_exist"] = bool(
            record["model_zip_exists"]
            and record["vecnormalize_pkl_exists"]
            and record["features_json_exists"]
        )

        if not record["all_required_artifacts_exist"]:
            missing.append(prefix)

        rows.append(record)

    return pd.DataFrame(rows), missing


def build_manifest(
    *,
    selected_df: pd.DataFrame,
    holdout_summary: dict[str, Any],
    holdout_summary_path: str | Path,
    artifacts_dir: str | Path,
    candidate_selection_doc: str | Path,
) -> dict[str, Any]:
    """Build v1.9 paper-trading manifest payload."""
    selected_models = {
        str(row["Ticker"]): str(row["Prefix"])
        for _, row in selected_df.iterrows()
    }

    return {
        "artifact_manifest_version": "1.9",
        "baseline_name": "standalone_alpaca_ppo_v1_9_holdout_selected",
        "source_git_tag": "v1.8.5-alpaca-ppo-final-holdout-validation",
        "universe": SIX_TICKERS,
        "selected_models": selected_models,
        "artifact_requirements": {
            "model_zip": True,
            "vecnormalize_pkl": True,
            "features_json": True,
        },
        "paper_trading_defaults": {
            "data_timeframe": "1H",
            "train_timeframe": "1H",
            "bars_feed": "iex",
            "dry_run": True,
            "auto_run_live": False,
            "allow_shorts": False,
            "use_fractionals": True,
            "require_paper_endpoint": True,
        },
        "source_validation": {
            "validation_type": "alpaca_ppo_final_holdout_validation",
            "holdout_summary_file": str(holdout_summary_path),
            "candidate_selection_doc": str(candidate_selection_doc),
            "artifact_source_dir": str(artifacts_dir),
            "selection_method": "holdout_promotion_score_v1",
            "holdout_start_after_global_eval_end": holdout_summary.get(
                "holdout_start_after_global_eval_end"
            ),
            "candidate_count": int(holdout_summary.get("candidate_count", 0)),
            "evaluated_count": int(holdout_summary.get("evaluated_count", 0)),
            "pass_count": int(holdout_summary.get("pass_count", 0)),
            "selected_windows": int(len(selected_df)),
            "unit_tests": "pytest tests/test_select_alpaca_ppo_candidates.py",
        },
        "notes": [
            "This manifest promotes standalone Alpaca-trained PPO candidates that passed v1.8.5 final holdout validation.",
            "Selection uses holdout_promotion_score_v1 and selects one candidate per ticker.",
            "These candidates are approved only for controlled no-submit paper-trading dry runs until v1.9 broker checks pass.",
            "Default paper-trading mode remains dry-run only unless --submit-orders is explicitly used.",
        ],
    }


def _fmt(value: Any, decimals: int = 3) -> str:
    try:
        return f"{float(value):,.{decimals}f}"
    except Exception:
        return str(value)


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    """Create a markdown table without requiring tabulate."""
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]

    for _, row in df.iterrows():
        vals = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                if col in {"PPO_Portfolio", "BuyHold"}:
                    vals.append(_fmt(value, 2))
                else:
                    vals.append(_fmt(value, 3))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")

    return "\n".join(lines)


def write_outputs(
    *,
    prepared_df: pd.DataFrame,
    selected_df: pd.DataFrame,
    artifact_df: pd.DataFrame,
    manifest_payload: dict[str, Any],
    output_dir: str | Path,
    doc_path: str | Path,
    holdout_summary_path: str | Path,
    missing_artifacts: list[str],
) -> dict[str, Path]:
    """Write selector outputs."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    ranked_path = root / "v1_9_alpaca_candidates_ranked.csv"
    selected_path = root / "v1_9_selected_paper_trading_candidates.csv"
    artifact_path = root / "v1_9_selected_artifact_check.csv"
    manifest_patch_path = root / "v1_9_paper_trading_manifest.json"

    prepared_df.sort_values(
        ["Ticker", "PromotionScore"],
        ascending=[True, False],
    ).to_csv(ranked_path, index=False)

    selected_df.to_csv(selected_path, index=False)
    artifact_df.to_csv(artifact_path, index=False)
    write_json(manifest_patch_path, manifest_payload)

    selected_columns = [
        "Ticker",
        "Prefix",
        "ValidationSharpe",
        "Sharpe",
        "Drawdown_%",
        "PPO_Portfolio",
        "BuyHold",
        "PromotionScore",
    ]

    doc = f"""# v1.9 Alpaca PPO Candidate Selection + Paper-Trading Redeployment

## Purpose

Select one standalone Alpaca PPO candidate per ticker for controlled paper-trading redeployment.

This checkpoint uses candidates that passed:

```text
v1.8.5 Final Holdout Validation / Untouched Test Period
```

This document does not record a paper order submission.

## Source Holdout Summary

{holdout_summary_path}

## Selection Method

Candidates must:

- have Evaluated = true
- have PassedHoldout = true
- meet minimum promotion Sharpe
- meet minimum final portfolio threshold
- have required model, VecNormalize, and features artifacts

Promotion score:

```text
PromotionScore =
    Holdout Sharpe
    - 0.10 * Holdout Drawdown %
    + 0.005 * PPO Return %
    + 0.25 if PassedHoldout
```

## Selected Candidates

{markdown_table(selected_df, selected_columns)}

## Manifest selected_models

```json
{json.dumps(manifest_payload["selected_models"], indent=2)}
```

## Artifact Validation

{markdown_table(artifact_df, list(artifact_df.columns))}

Artifact validation: {"PASS" if not missing_artifacts else "FAIL"}

## Guardrails

These candidates are promoted only into controlled paper-trading dry-run validation.

Do not submit paper orders until:

- artifact manifest validation passes
- broker-connected dry run succeeds
- execution plan is reviewed
- risk controls pass
- pre-trade checklist passes
- manual review approves submit

## Next Step

Run no-submit paper-trading redeployment dry run with:

```bash
python -m src.paper_trading.paper_trade_dry_run \\
  --manifest config/paper_trading_six_ticker_manifest.json \\
  --artifacts-dir models/alpaca_ppo_models_master
```
"""

    final_doc_path = Path(doc_path)
    final_doc_path.parent.mkdir(parents=True, exist_ok=True)
    final_doc_path.write_text(doc, encoding="utf-8")

    return {
        "ranked_path": ranked_path,
        "selected_path": selected_path,
        "artifact_path": artifact_path,
        "manifest_patch_path": manifest_patch_path,
        "doc_path": final_doc_path,
    }


def run_selection(
    *,
    holdout_summary_path: str | Path,
    artifacts_dir: str | Path = "models/alpaca_ppo_models_master",
    output_dir: str | Path = "reports/model_selection/v1_9_alpaca_ppo",
    doc_path: str | Path = "docs/runs/v1.9_alpaca_ppo_candidate_selection.md",
    manifest_path: str | Path = "config/paper_trading_six_ticker_manifest.json",
    update_manifest: bool = False,
    min_promotion_sharpe: float = 0.0,
    min_final_portfolio: float = 95_000.0,
) -> dict[str, Any]:
    """Run candidate selection and optionally update the paper-trading manifest."""
    candidates, holdout_summary = load_holdout_candidates(holdout_summary_path)

    prepared = prepare_candidates(
        candidates,
        min_promotion_sharpe=min_promotion_sharpe,
        min_final_portfolio=min_final_portfolio,
    )
    selected = select_one_per_ticker(prepared)

    artifact_df, missing_artifacts = validate_selected_artifacts(
        selected,
        artifacts_dir=artifacts_dir,
    )

    manifest_payload = build_manifest(
        selected_df=selected,
        holdout_summary=holdout_summary,
        holdout_summary_path=holdout_summary_path,
        artifacts_dir=artifacts_dir,
        candidate_selection_doc=doc_path,
    )

    outputs = write_outputs(
        prepared_df=prepared,
        selected_df=selected,
        artifact_df=artifact_df,
        manifest_payload=manifest_payload,
        output_dir=output_dir,
        doc_path=doc_path,
        holdout_summary_path=holdout_summary_path,
        missing_artifacts=missing_artifacts,
    )

    if missing_artifacts:
        raise FileNotFoundError(f"Missing artifacts for selected candidates: {missing_artifacts}")

    if update_manifest:
        write_json(manifest_path, manifest_payload)

    return {
        "selected_models": manifest_payload["selected_models"],
        "missing_artifacts": missing_artifacts,
        "outputs": {key: str(value) for key, value in outputs.items()},
        "manifest_updated": bool(update_manifest),
        "manifest_path": str(manifest_path),
    }


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Select Alpaca PPO candidates for paper-trading redeployment."
    )
    parser.add_argument("--holdout-summary", required=True)
    parser.add_argument("--artifacts-dir", default="models/alpaca_ppo_models_master")
    parser.add_argument("--output-dir", default="reports/model_selection/v1_9_alpaca_ppo")
    parser.add_argument("--doc-path", default="docs/runs/v1.9_alpaca_ppo_candidate_selection.md")
    parser.add_argument("--manifest-path", default="config/paper_trading_six_ticker_manifest.json")
    parser.add_argument("--update-manifest", action="store_true")
    parser.add_argument("--min-promotion-sharpe", type=float, default=0.0)
    parser.add_argument("--min-final-portfolio", type=float, default=95_000.0)
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()

    result = run_selection(
        holdout_summary_path=args.holdout_summary,
        artifacts_dir=args.artifacts_dir,
        output_dir=args.output_dir,
        doc_path=args.doc_path,
        manifest_path=args.manifest_path,
        update_manifest=args.update_manifest,
        min_promotion_sharpe=args.min_promotion_sharpe,
        min_final_portfolio=args.min_final_portfolio,
    )

    print("=" * 80)
    print("v1.9 ALPACA PPO CANDIDATE SELECTION")
    print("=" * 80)
    print("selected_models:")
    print(json.dumps(result["selected_models"], indent=2))
    print()
    print(f"manifest_updated: {result['manifest_updated']}")
    print(f"manifest_path: {result['manifest_path']}")
    print("artifact_validation: PASS")
    print()
    for name, path in result["outputs"].items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
