import json
from pathlib import Path

import pandas as pd

from src.model_selection.quantconnect_execution_retest import (
    build_qc_models_from_targets,
    compare_qc_to_paper_execution,
    load_manifest_selected_models,
    run_quantconnect_execution_retest,
    simulate_qc_broker_execution,
    validate_manifest_prefixes,
)


def _write_sample_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    targets = pd.DataFrame(
        [
            {
                "symbol": "AAPL",
                "selected_prefix": "ppo_AAPL_window2",
                "raw_action": 0.50,
                "confidence": 0.50,
                "target_weight": 0.10,
                "actual_weight": 0.00,
                "intended_notional": 10000.0,
                "note": "dry_run_predict_ok",
                "latest_price": 100.0,
                "equity": 100000.0,
            },
            {
                "symbol": "XOM",
                "selected_prefix": "ppo_XOM_window2",
                "raw_action": -1.00,
                "confidence": 1.00,
                "target_weight": 0.00,
                "actual_weight": 0.00,
                "intended_notional": 0.0,
                "note": "dry_run_predict_ok",
                "latest_price": 50.0,
                "equity": 100000.0,
            },
        ]
    )

    plan = pd.DataFrame(
        [
            {
                "symbol": "AAPL",
                "side": "buy",
                "qty": 100.0,
                "price": 100.0,
                "equity": 100000.0,
                "target_weight": 0.10,
                "actual_weight": 0.00,
                "delta_notional": 10000.0,
                "should_order": True,
                "reason": "rebalance_required",
            },
            {
                "symbol": "XOM",
                "side": "hold",
                "qty": 0.0,
                "price": 50.0,
                "equity": 100000.0,
                "target_weight": 0.00,
                "actual_weight": 0.00,
                "delta_notional": 0.0,
                "should_order": False,
                "reason": "below_min_notional",
            },
        ]
    )

    targets.to_csv(run_dir / "dry_run_targets.csv", index=False)
    plan.to_csv(run_dir / "execution_plan.csv", index=False)


def _write_manifest(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "selected_models": {
                    "AAPL": "ppo_AAPL_window2",
                    "XOM": "ppo_XOM_window2",
                }
            }
        ),
        encoding="utf-8",
    )


def test_load_manifest_selected_models(tmp_path):
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest)

    selected = load_manifest_selected_models(manifest)

    assert selected["AAPL"] == "ppo_AAPL_window2"
    assert selected["XOM"] == "ppo_XOM_window2"


def test_validate_manifest_prefixes_passes_for_matching_targets(tmp_path):
    run_dir = tmp_path / "run"
    _write_sample_run(run_dir)

    targets = pd.read_csv(run_dir / "dry_run_targets.csv")
    selected = {
        "AAPL": "ppo_AAPL_window2",
        "XOM": "ppo_XOM_window2",
    }

    assert validate_manifest_prefixes(targets, selected) == []


def test_build_qc_models_from_targets_creates_payload_models(tmp_path):
    run_dir = tmp_path / "run"
    _write_sample_run(run_dir)

    targets = pd.read_csv(run_dir / "dry_run_targets.csv")
    plan = pd.read_csv(run_dir / "execution_plan.csv")

    models = build_qc_models_from_targets(targets, plan)

    assert len(models) == 2
    assert models[0]["symbol"] == "AAPL"
    assert models[0]["signal"] == "BUY"
    assert models[1]["signal"] == "SELL"


def test_simulated_execution_matches_paper_plan(tmp_path):
    run_dir = tmp_path / "run"
    _write_sample_run(run_dir)

    targets = pd.read_csv(run_dir / "dry_run_targets.csv")
    plan = pd.read_csv(run_dir / "execution_plan.csv")

    simulated = simulate_qc_broker_execution(targets, plan, equity=100000.0)
    comparison = compare_qc_to_paper_execution(simulated, plan)

    assert comparison["comparison_passed"].all()


def test_full_quantconnect_execution_retest_passes(tmp_path):
    run_dir = tmp_path / "run"
    output_dir = tmp_path / "out"
    doc_path = tmp_path / "doc.md"
    manifest = tmp_path / "manifest.json"

    _write_sample_run(run_dir)
    _write_manifest(manifest)

    summary, outputs = run_quantconnect_execution_retest(
        run_dir=run_dir,
        manifest_path=manifest,
        output_dir=output_dir,
        doc_path=doc_path,
    )

    assert summary["retest_passed"] is True
    assert summary["payload_models"] == 2
    assert outputs["payload_path"].exists()
    assert outputs["comparison_path"].exists()
    assert outputs["doc_path"].exists()


def test_full_quantconnect_execution_retest_detects_mismatch(tmp_path):
    run_dir = tmp_path / "run"
    output_dir = tmp_path / "out"
    doc_path = tmp_path / "doc.md"
    manifest = tmp_path / "manifest.json"

    _write_sample_run(run_dir)
    _write_manifest(manifest)

    plan_path = run_dir / "execution_plan.csv"
    plan = pd.read_csv(plan_path)
    plan.loc[0, "side"] = "hold"
    plan.to_csv(plan_path, index=False)

    summary, _outputs = run_quantconnect_execution_retest(
        run_dir=run_dir,
        manifest_path=manifest,
        output_dir=output_dir,
        doc_path=doc_path,
    )

    assert summary["retest_passed"] is False
    assert "AAPL" in summary["comparison_failures"]
