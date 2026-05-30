import json
from pathlib import Path

import pandas as pd

from src.model_selection.select_alpaca_ppo_candidates import (
    build_manifest,
    load_holdout_candidates,
    prepare_candidates,
    run_selection,
    select_one_per_ticker,
    validate_selected_artifacts,
)


def _holdout_summary():
    rows = [
        {
            "Ticker": "AAPL",
            "Prefix": "ppo_AAPL_window7",
            "ValidationSharpe": 4.0,
            "Sharpe": -0.1,
            "Drawdown_%": 0.1,
            "PPO_Portfolio": 99900,
            "BuyHold": 110000,
            "PassedHoldout": True,
            "Evaluated": True,
            "HoldoutRows": 100,
        },
        {
            "Ticker": "AAPL",
            "Prefix": "ppo_AAPL_window19",
            "ValidationSharpe": 2.0,
            "Sharpe": 0.7,
            "Drawdown_%": 0.3,
            "PPO_Portfolio": 100300,
            "BuyHold": 110000,
            "PassedHoldout": True,
            "Evaluated": True,
            "HoldoutRows": 100,
        },
        {
            "Ticker": "AMD",
            "Prefix": "ppo_AMD_window14",
            "ValidationSharpe": 2.2,
            "Sharpe": 1.4,
            "Drawdown_%": 1.1,
            "PPO_Portfolio": 102000,
            "BuyHold": 190000,
            "PassedHoldout": True,
            "Evaluated": True,
            "HoldoutRows": 100,
        },
    ]

    return {
        "milestone": "v1.8.5",
        "mode": "evaluate",
        "candidate_count": len(rows),
        "evaluated_count": len(rows),
        "pass_count": len(rows),
        "holdout_start_after_global_eval_end": "2026-01-14T15:00:00+00:00",
        "candidate_results": rows,
    }


def _write_artifacts(root: Path, prefix: str):
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{prefix}_model.zip").write_text("fake", encoding="utf-8")
    (root / f"{prefix}_vecnorm.pkl").write_text("fake", encoding="utf-8")
    (root / f"{prefix}_features.json").write_text("{}", encoding="utf-8")


def test_load_holdout_candidates(tmp_path):
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(_holdout_summary()), encoding="utf-8")

    df, summary = load_holdout_candidates(path)

    assert len(df) == 3
    assert summary["milestone"] == "v1.8.5"
    assert set(df["Ticker"]) == {"AAPL", "AMD"}


def test_prepare_candidates_filters_negative_sharpe_by_default():
    df = pd.DataFrame(_holdout_summary()["candidate_results"])

    prepared = prepare_candidates(
        df,
        universe=["AAPL", "AMD"],
        min_promotion_sharpe=0.0,
    )

    aapl = prepared[prepared["Ticker"] == "AAPL"]
    assert aapl[aapl["Prefix"] == "ppo_AAPL_window7"]["EligibleForPromotion"].iloc[0] is False
    assert aapl[aapl["Prefix"] == "ppo_AAPL_window19"]["EligibleForPromotion"].iloc[0] is True


def test_select_one_per_ticker_selects_best_eligible():
    df = pd.DataFrame(_holdout_summary()["candidate_results"])
    prepared = prepare_candidates(df, universe=["AAPL", "AMD"])
    selected = select_one_per_ticker(prepared)

    selected_models = dict(zip(selected["Ticker"], selected["Prefix"]))
    assert selected_models["AAPL"] == "ppo_AAPL_window19"
    assert selected_models["AMD"] == "ppo_AMD_window14"


def test_validate_selected_artifacts(tmp_path):
    df = pd.DataFrame(
        [
            {"Ticker": "AAPL", "Prefix": "ppo_AAPL_window19"},
            {"Ticker": "AMD", "Prefix": "ppo_AMD_window14"},
        ]
    )

    _write_artifacts(tmp_path, "ppo_AAPL_window19")
    _write_artifacts(tmp_path, "ppo_AMD_window14")

    artifact_df, missing = validate_selected_artifacts(df, artifacts_dir=tmp_path)

    assert missing == []
    assert artifact_df["all_required_artifacts_exist"].all()


def test_build_manifest_has_selected_models():
    selected = pd.DataFrame(
        [
            {"Ticker": "AAPL", "Prefix": "ppo_AAPL_window19"},
            {"Ticker": "AMD", "Prefix": "ppo_AMD_window14"},
            {"Ticker": "MRK", "Prefix": "ppo_MRK_window20"},
            {"Ticker": "PFE", "Prefix": "ppo_PFE_window11"},
            {"Ticker": "UNH", "Prefix": "ppo_UNH_window20"},
            {"Ticker": "XOM", "Prefix": "ppo_XOM_window15"},
        ]
    )

    manifest = build_manifest(
        selected_df=selected,
        holdout_summary=_holdout_summary(),
        holdout_summary_path="holdout.json",
        artifacts_dir="models/alpaca_ppo_models_master",
        candidate_selection_doc="docs/runs/v1.9_alpaca_ppo_candidate_selection.md",
    )

    assert manifest["artifact_manifest_version"] == "1.9"
    assert manifest["selected_models"]["AAPL"] == "ppo_AAPL_window19"
    assert manifest["source_git_tag"] == "v1.8.5-alpaca-ppo-final-holdout-validation"


def test_run_selection_updates_manifest(tmp_path):
    summary_rows = [
        {
            "Ticker": ticker,
            "Prefix": prefix,
            "ValidationSharpe": 2.0,
            "Sharpe": 0.5,
            "Drawdown_%": 0.2,
            "PPO_Portfolio": 100100,
            "BuyHold": 100000,
            "PassedHoldout": True,
            "Evaluated": True,
            "HoldoutRows": 100,
        }
        for ticker, prefix in {
            "AAPL": "ppo_AAPL_window19",
            "AMD": "ppo_AMD_window14",
            "MRK": "ppo_MRK_window20",
            "PFE": "ppo_PFE_window11",
            "UNH": "ppo_UNH_window20",
            "XOM": "ppo_XOM_window15",
        }.items()
    ]

    summary = {
        "candidate_count": len(summary_rows),
        "evaluated_count": len(summary_rows),
        "pass_count": len(summary_rows),
        "holdout_start_after_global_eval_end": "2026-01-14T15:00:00+00:00",
        "candidate_results": summary_rows,
    }

    holdout_path = tmp_path / "holdout_summary.json"
    holdout_path.write_text(json.dumps(summary), encoding="utf-8")

    artifacts_dir = tmp_path / "models"
    for row in summary_rows:
        _write_artifacts(artifacts_dir, row["Prefix"])

    manifest_path = tmp_path / "manifest.json"

    result = run_selection(
        holdout_summary_path=holdout_path,
        artifacts_dir=artifacts_dir,
        output_dir=tmp_path / "outputs",
        doc_path=tmp_path / "selection.md",
        manifest_path=manifest_path,
        update_manifest=True,
    )

    assert result["manifest_updated"] is True
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["selected_models"]["AAPL"] == "ppo_AAPL_window19"
    assert len(manifest["selected_models"]) == 6
