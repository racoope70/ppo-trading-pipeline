import json
from pathlib import Path

import pandas as pd
import pytest

from src.alpaca_ppo_holdout_validation import (
    HoldoutThresholds,
    artifact_existence_summary,
    candidate_prefix,
    compute_global_holdout_start,
    load_training_results,
    parse_window_index,
    pass_fail_from_metrics,
    resolve_artifact_paths,
    run_holdout_validation,
    select_top_candidates_per_symbol,
    slice_holdout_dataset,
)
from src.alpaca_ppo_retraining_config import (
    AlpacaPPORetrainingConfig,
    write_config_json,
)


def _training_results_df():
    return pd.DataFrame(
        [
            {
                "Ticker": "AAPL",
                "Window": "0-720",
                "EvalEnd": "2026-01-01T15:00:00+00:00",
                "Sharpe": 1.0,
                "Drawdown_%": 1.0,
                "PPO_Portfolio": 100000,
                "BuyHold": 99000,
                "Winner": "PPO",
            },
            {
                "Ticker": "AAPL",
                "Window": "120-840",
                "EvalEnd": "2026-01-02T15:00:00+00:00",
                "Sharpe": 3.0,
                "Drawdown_%": 0.5,
                "PPO_Portfolio": 101000,
                "BuyHold": 100000,
                "Winner": "PPO",
            },
            {
                "Ticker": "AMD",
                "Window": "0-720",
                "EvalEnd": "2026-01-01T15:00:00+00:00",
                "Sharpe": -0.5,
                "Drawdown_%": 2.0,
                "PPO_Portfolio": 99900,
                "BuyHold": 100000,
                "Winner": "Buy & Hold",
            },
            {
                "Ticker": "AMD",
                "Window": "120-840",
                "EvalEnd": "2026-01-03T15:00:00+00:00",
                "Sharpe": 2.0,
                "Drawdown_%": 1.5,
                "PPO_Portfolio": 100500,
                "BuyHold": 100100,
                "Winner": "PPO",
            },
        ]
    )


def _model_ready_dataset(symbols=("AAPL", "AMD"), rows_per_symbol=100):
    rows = []

    for symbol in symbols:
        for i in range(rows_per_symbol):
            ts = pd.Timestamp("2026-01-04T15:00:00Z") + pd.Timedelta(hours=i)
            price = 100 + i * 0.1

            rows.append(
                {
                    "Datetime": ts,
                    "Open": price,
                    "High": price + 1,
                    "Low": price - 1,
                    "Close": price + 0.2,
                    "Volume": 1000 + i,
                    "SMA_20": price,
                    "STD_20": 1.0,
                    "Upper_Band": price + 2,
                    "Lower_Band": price - 2,
                    "EMA_10": price,
                    "EMA_50": price,
                    "RSI": 50.0,
                    "ATR": 1.5,
                    "Volatility": 0.02,
                    "Denoised_Close": price,
                    "Delta": 0.01,
                    "Gamma": 0.001,
                    "Return": 0.01,
                    "Target": 1,
                    "Symbol": symbol,
                }
            )

    return pd.DataFrame(rows)


def test_parse_window_index():
    assert parse_window_index("0-720", step_size=120) == 1
    assert parse_window_index("120-840", step_size=120) == 2
    assert parse_window_index("2280-3000", step_size=120) == 20


def test_parse_window_index_rejects_bad_step_alignment():
    with pytest.raises(ValueError, match="not divisible"):
        parse_window_index("121-841", step_size=120)


def test_candidate_prefix():
    row = {"Ticker": "aapl", "Window": "120-840"}
    assert candidate_prefix(row, step_size=120) == "ppo_AAPL_window2"


def test_compute_global_holdout_start():
    df = _training_results_df()
    assert compute_global_holdout_start(df) == pd.Timestamp(
        "2026-01-03T15:00:00Z"
    )


def test_select_top_candidates_per_symbol():
    df = _training_results_df()
    selected = select_top_candidates_per_symbol(
        df,
        top_n_per_symbol=1,
        step_size=120,
    )

    assert len(selected) == 2
    assert {row["Ticker"] for row in selected} == {"AAPL", "AMD"}
    assert {row["Prefix"] for row in selected} == {
        "ppo_AAPL_window2",
        "ppo_AMD_window2",
    }


def test_slice_holdout_dataset_uses_rows_after_global_eval_end():
    dataset = _model_ready_dataset()
    holdout = slice_holdout_dataset(
        dataset,
        ticker="AAPL",
        holdout_start=pd.Timestamp("2026-01-05T15:00:00Z"),
    )

    assert not holdout.empty
    assert holdout["Datetime"].min() > pd.Timestamp("2026-01-05T15:00:00Z")
    assert set(holdout["Symbol"].unique()) == {"AAPL"}


def test_artifact_existence_summary_requires_model_and_vecnorm(tmp_path):
    paths = resolve_artifact_paths(
        prefix="ppo_AAPL_window1",
        artifacts_dir=tmp_path,
    )

    summary = artifact_existence_summary(paths)

    assert summary["required_artifacts_exist"] is False
    assert len(summary["required_missing"]) == 2

    paths["model_path"].write_text("fake", encoding="utf-8")
    paths["vecnorm_path"].write_text("fake", encoding="utf-8")

    summary = artifact_existence_summary(paths)

    assert summary["required_artifacts_exist"] is True


def test_pass_fail_from_metrics():
    passed, reasons = pass_fail_from_metrics(
        metrics={
            "Sharpe": 0.2,
            "Drawdown_%": 1.0,
            "PPO_Portfolio": 100000,
        },
        holdout_rows=100,
        thresholds=HoldoutThresholds(
            min_holdout_rows=60,
            min_sharpe=-1.0,
            max_drawdown_pct=5.0,
            min_final_portfolio=95000,
        ),
    )

    assert passed is True
    assert reasons == []


def test_pass_fail_from_metrics_rejects_bad_metrics():
    passed, reasons = pass_fail_from_metrics(
        metrics={
            "Sharpe": -2.0,
            "Drawdown_%": 7.0,
            "PPO_Portfolio": 90000,
        },
        holdout_rows=10,
        thresholds=HoldoutThresholds(
            min_holdout_rows=60,
            min_sharpe=-1.0,
            max_drawdown_pct=5.0,
            min_final_portfolio=95000,
        ),
    )

    assert passed is False
    assert len(reasons) == 4


def test_load_training_results_validates_required_columns(tmp_path):
    path = tmp_path / "training_results.json"
    path.write_text(json.dumps({"results": [{"Ticker": "AAPL"}]}), encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        load_training_results(path)


def test_run_holdout_validation_dry_run(tmp_path):
    dataset_path = tmp_path / "dataset.csv"
    provenance_path = tmp_path / "provenance.json"
    config_path = tmp_path / "config.json"
    run_dir = tmp_path / "retraining_run"
    artifacts_dir = tmp_path / "models"

    dataset = _model_ready_dataset(rows_per_symbol=100)
    dataset.to_csv(dataset_path, index=False)
    provenance_path.write_text("{}", encoding="utf-8")

    config = AlpacaPPORetrainingConfig(
        dataset_path=str(dataset_path),
        dataset_provenance_path=str(provenance_path),
        artifacts_dir=str(artifacts_dir),
        results_dir=str(tmp_path / "reports"),
        symbols=("AAPL", "AMD"),
        top_n_windows=1,
        walkforward_step_size=120,
    )
    write_config_json(config, config_path)

    run_dir.mkdir(parents=True, exist_ok=True)
    training_results = {"results": _training_results_df().to_dict(orient="records")}
    (run_dir / "training_results.json").write_text(
        json.dumps(training_results, default=str),
        encoding="utf-8",
    )

    for prefix in ["ppo_AAPL_window2", "ppo_AMD_window2"]:
        paths = resolve_artifact_paths(prefix=prefix, artifacts_dir=artifacts_dir)
        paths["model_path"].parent.mkdir(parents=True, exist_ok=True)
        paths["model_path"].write_text("fake", encoding="utf-8")
        paths["vecnorm_path"].write_text("fake", encoding="utf-8")

    summary = run_holdout_validation(
        config_path=config_path,
        run_dir=run_dir,
        evaluate=False,
        top_n_per_symbol=1,
        thresholds=HoldoutThresholds(min_holdout_rows=10),
    )

    assert summary["mode"] == "dry_run"
    assert summary["candidate_count"] == 2
    assert summary["dry_run_pass_count"] == 2
    assert Path(summary["output_dir"]).exists()
    assert (Path(summary["output_dir"]) / "final_summary.json").exists()
