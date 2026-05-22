import pandas as pd
import pytest

from src.model_selection.temporal_stability_validation import (
    build_temporal_stability_report,
    prepare_temporal_summary,
    selected_rows_from_manifest,
)


def _sample_summary() -> pd.DataFrame:
    rows = []
    for ticker in ["AAPL", "XOM"]:
        for idx, sharpe in enumerate([0.4, 1.2, 0.8], start=1):
            rows.append(
                {
                    "Ticker": ticker,
                    "Window": f"{(idx - 1) * 500}-{3500 + (idx - 1) * 500}",
                    "TrainRows": 2800,
                    "EvalRows": 700,
                    "TrainStart": f"2023-0{idx}-01 00:00:00+00:00",
                    "TrainEnd": f"2023-0{idx}-20 00:00:00+00:00",
                    "EvalStart": f"2023-0{idx}-20 01:00:00+00:00",
                    "EvalEnd": f"2023-0{idx}-28 00:00:00+00:00",
                    "ValidationMode": "out_of_sample_eval_slice",
                    "PPO_Portfolio": 100000 + idx * 5000,
                    "BuyHold": 99000,
                    "Sharpe": sharpe,
                    "Drawdown_%": 5.0,
                    "Winner": "PPO",
                }
            )
    return pd.DataFrame(rows)


def test_prepare_temporal_summary_adds_metrics_and_prefixes():
    selected_models = {"AAPL": "ppo_AAPL_window2", "XOM": "ppo_XOM_window2"}

    prepared = prepare_temporal_summary(
        _sample_summary(),
        selected_models=selected_models,
    )

    assert "PPO_Return_%" in prepared.columns
    assert "Excess_vs_BuyHold_%" in prepared.columns
    assert "ModelPrefix" in prepared.columns
    assert "ppo_AAPL_window2" in set(prepared["ModelPrefix"])


def test_selected_rows_from_manifest_finds_selected_prefixes():
    selected_models = {"AAPL": "ppo_AAPL_window2", "XOM": "ppo_XOM_window2"}
    prepared = prepare_temporal_summary(
        _sample_summary(),
        selected_models=selected_models,
    )

    selected = selected_rows_from_manifest(prepared, selected_models)

    assert len(selected) == 2
    assert set(selected["ModelPrefix"]) == {"ppo_AAPL_window2", "ppo_XOM_window2"}


def test_selected_rows_from_manifest_raises_for_missing_prefix():
    selected_models = {"AAPL": "ppo_AAPL_window99"}
    prepared = prepare_temporal_summary(
        _sample_summary(),
        selected_models=selected_models,
    )

    with pytest.raises(ValueError, match="not found"):
        selected_rows_from_manifest(prepared, selected_models)


def test_build_temporal_stability_report_returns_one_row_per_ticker():
    selected_models = {"AAPL": "ppo_AAPL_window2", "XOM": "ppo_XOM_window2"}
    prepared = prepare_temporal_summary(
        _sample_summary(),
        selected_models=selected_models,
    )
    selected = selected_rows_from_manifest(prepared, selected_models)
    stability = build_temporal_stability_report(prepared, selected)

    assert len(stability) == 2
    assert set(stability["Ticker"]) == {"AAPL", "XOM"}
    assert "StabilityTier" in stability.columns


def test_prepare_temporal_summary_rejects_bad_validation_mode():
    df = _sample_summary()
    df.loc[0, "ValidationMode"] = "in_sample"

    with pytest.raises(ValueError, match="ValidationMode"):
        prepare_temporal_summary(
            df,
            selected_models={"AAPL": "ppo_AAPL_window2"},
        )


def test_prepare_temporal_summary_rejects_overlap():
    df = _sample_summary()
    df.loc[0, "EvalStart"] = "2023-01-19 00:00:00+00:00"

    with pytest.raises(ValueError, match="overlap"):
        prepare_temporal_summary(
            df,
            selected_models={"AAPL": "ppo_AAPL_window2"},
        )
