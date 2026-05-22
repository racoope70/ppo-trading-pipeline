import pandas as pd
import pytest

from src.model_selection.select_clean_six_ticker_candidates import (
    ARTIFACT_SUFFIXES,
    build_manifest_patch,
    prepare_summary,
    select_candidates,
    validate_selected_artifacts,
)


def _sample_summary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Ticker": "AAPL",
                "Window": "0-3500",
                "TrainRows": 2800,
                "EvalRows": 700,
                "TrainStart": "2023-01-01 00:00:00+00:00",
                "TrainEnd": "2023-06-01 00:00:00+00:00",
                "EvalStart": "2023-06-01 01:00:00+00:00",
                "EvalEnd": "2023-08-01 00:00:00+00:00",
                "ValidationMode": "out_of_sample_eval_slice",
                "PPO_Portfolio": 105000.0,
                "BuyHold": 103000.0,
                "Sharpe": 0.50,
                "Drawdown_%": 5.0,
                "Winner": "PPO",
            },
            {
                "Ticker": "AAPL",
                "Window": "500-4000",
                "TrainRows": 2800,
                "EvalRows": 700,
                "TrainStart": "2023-02-01 00:00:00+00:00",
                "TrainEnd": "2023-07-01 00:00:00+00:00",
                "EvalStart": "2023-07-01 01:00:00+00:00",
                "EvalEnd": "2023-09-01 00:00:00+00:00",
                "ValidationMode": "out_of_sample_eval_slice",
                "PPO_Portfolio": 110000.0,
                "BuyHold": 120000.0,
                "Sharpe": 1.20,
                "Drawdown_%": 3.0,
                "Winner": "Buy & Hold",
            },
            {
                "Ticker": "XOM",
                "Window": "0-3500",
                "TrainRows": 2800,
                "EvalRows": 700,
                "TrainStart": "2023-01-01 00:00:00+00:00",
                "TrainEnd": "2023-06-01 00:00:00+00:00",
                "EvalStart": "2023-06-01 01:00:00+00:00",
                "EvalEnd": "2023-08-01 00:00:00+00:00",
                "ValidationMode": "out_of_sample_eval_slice",
                "PPO_Portfolio": 125000.0,
                "BuyHold": 101000.0,
                "Sharpe": 1.30,
                "Drawdown_%": 6.0,
                "Winner": "PPO",
            },
        ]
    )


def test_prepare_summary_adds_scores_and_prefixes():
    prepared = prepare_summary(_sample_summary(), tickers=["AAPL", "XOM"])

    assert "SelectionScore" in prepared.columns
    assert "ModelPrefix" in prepared.columns
    assert prepared.loc[0, "ModelPrefix"] == "ppo_AAPL_window1"
    assert prepared.loc[1, "ModelPrefix"] == "ppo_AAPL_window2"
    assert prepared.loc[2, "ModelPrefix"] == "ppo_XOM_window1"


def test_select_candidates_selects_one_per_ticker():
    prepared = prepare_summary(_sample_summary(), tickers=["AAPL", "XOM"])
    selected = select_candidates(prepared)

    selected_map = dict(zip(selected["Ticker"], selected["ModelPrefix"]))

    assert selected_map["AAPL"] == "ppo_AAPL_window2"
    assert selected_map["XOM"] == "ppo_XOM_window1"


def test_prepare_summary_rejects_train_eval_overlap():
    df = _sample_summary()
    df.loc[0, "EvalStart"] = "2023-05-01 00:00:00+00:00"

    with pytest.raises(ValueError, match="overlap"):
        prepare_summary(df, tickers=["AAPL", "XOM"])


def test_prepare_summary_rejects_wrong_validation_mode():
    df = _sample_summary()
    df.loc[0, "ValidationMode"] = "in_sample"

    with pytest.raises(ValueError, match="ValidationMode"):
        prepare_summary(df, tickers=["AAPL", "XOM"])


def test_validate_selected_artifacts_detects_full_sets(tmp_path):
    prepared = prepare_summary(_sample_summary(), tickers=["AAPL", "XOM"])
    selected = select_candidates(prepared)

    for prefix in selected["ModelPrefix"]:
        for suffix in ARTIFACT_SUFFIXES:
            (tmp_path / f"{prefix}{suffix}").write_text("x", encoding="utf-8")

    artifact_df, missing = validate_selected_artifacts(selected, model_dir=tmp_path)

    assert missing == []
    assert len(artifact_df) == 2


def test_validate_selected_artifacts_reports_missing_files(tmp_path):
    prepared = prepare_summary(_sample_summary(), tickers=["AAPL", "XOM"])
    selected = select_candidates(prepared)

    artifact_df, missing = validate_selected_artifacts(selected, model_dir=tmp_path)

    assert not artifact_df.empty
    assert missing


def test_build_manifest_patch_contains_selected_models():
    prepared = prepare_summary(_sample_summary(), tickers=["AAPL", "XOM"])
    selected = select_candidates(prepared)
    patch = build_manifest_patch(selected, run_dir="reports/backtests/example")

    assert patch["selected_models"]["AAPL"] == "ppo_AAPL_window2"
    assert patch["selected_models"]["XOM"] == "ppo_XOM_window1"
    assert patch["source_validation"]["selection_method"] == "risk_adjusted_score_v1"
