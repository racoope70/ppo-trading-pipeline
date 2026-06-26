from __future__ import annotations

import importlib.util
import sys
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "src" / "ppo_v2_validation_reporting_scaffold.py"


def load_module():
    module_name = "ppo_v2_validation_reporting_scaffold"
    spec = importlib.util.spec_from_file_location(
        module_name,
        SOURCE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def source_text() -> str:
    return SOURCE_PATH.read_text(encoding="utf-8")


def test_module_loads():
    module = load_module()
    assert module.NO_SUBMIT_DEFAULT == "DEFAULT"


def test_default_status_is_fail_closed_without_evidence():
    module = load_module()
    status = module.build_reporting_scaffold_status()
    assert status.scaffold_implemented is True
    assert status.fail_closed is True
    assert status.evidence_check.audited_outputs_available is False


def test_required_evidence_keys_are_complete():
    module = load_module()
    assert module.REQUIRED_EVIDENCE_KEYS == (
        "training_outputs_inventory",
        "quarantine_output_manifest",
        "dataset_boundary_manifest",
        "leakage_control_evidence",
        "normalization_evidence",
        "locked_eval_stats_evidence",
        "untouched_holdout_evidence",
        "ppo_only_baseline_evidence",
        "post_run_audit",
    )


def test_evidence_check_marks_missing_paths_fail_closed(tmp_path):
    module = load_module()
    missing_path = tmp_path / "missing.json"
    evidence = {"training_outputs_inventory": missing_path}
    check = module.check_required_evidence(evidence)
    assert check.all_required_present is False
    assert check.audited_outputs_available is False
    assert "training_outputs_inventory" in check.missing_keys


def test_evidence_check_accepts_existing_read_only_paths(tmp_path):
    module = load_module()
    evidence = {}
    for key in module.REQUIRED_EVIDENCE_KEYS:
        path = tmp_path / f"{key}.json"
        path.touch()
        evidence[key] = path

    check = module.check_required_evidence(evidence)

    assert check.all_required_present is True
    assert check.audited_outputs_available is True
    assert check.missing_keys == ()


def test_status_with_existing_evidence_still_does_not_compute_or_generate_outputs(tmp_path):
    module = load_module()
    evidence = {}
    for key in module.REQUIRED_EVIDENCE_KEYS:
        path = tmp_path / f"{key}.json"
        path.touch()
        evidence[key] = path

    status = module.build_reporting_scaffold_status(evidence)

    assert status.fail_closed is False
    assert status.metrics_computed is False
    assert status.reports_generated is False
    assert status.plots_generated is False
    assert status.dashboards_generated is False


def test_no_submit_boundary_is_default():
    module = load_module()
    boundary = module.validate_no_submit_boundary()
    assert boundary["NO_SUBMIT"] == "DEFAULT"


def test_controlled_submit_paper_live_and_promotion_blocked():
    module = load_module()
    status = module.build_reporting_scaffold_status()
    assert status.controlled_submit == "BLOCKED"
    assert status.model_promotion == "NOT_AUTHORIZED"
    assert status.paper_orders == "NOT_AUTHORIZED"
    assert status.live_orders == "NOT_AUTHORIZED"


def test_hybrids_remain_blocked():
    module = load_module()
    status = module.build_reporting_scaffold_status()
    assert status.ppo_rf == "BLOCKED"
    assert status.ppo_xgboost == "BLOCKED"


def test_manifest_is_serializable_plain_dict():
    module = load_module()
    status = module.build_reporting_scaffold_status()
    manifest = status.to_manifest()
    json.dumps(manifest)
    assert manifest["fail_closed"] is True
    assert manifest["metrics_computed"] is False


def test_source_has_no_broker_or_network_imports():
    text = source_text()
    forbidden = [
        "alpaca",
        "TradingClient",
        "StockHistoricalDataClient",
        "submit_order",
        "requests",
    ]
    for token in forbidden:
        assert token not in text


def test_source_has_no_training_or_model_loading_calls():
    text = source_text()
    forbidden = [
        "stable_baselines3",
        "PPO(",
        "PPO.load",
        ".learn(",
        ".fit(",
        "joblib",
        "torch",
    ]
    for token in forbidden:
        assert token not in text


def test_source_has_no_artifact_write_calls():
    text = source_text()
    forbidden = [
        "write_text",
        "open(",
        "pickle.dump",
        "to_csv",
        "to_parquet",
    ]
    for token in forbidden:
        assert token not in text


def test_source_does_not_read_market_data_files():
    text = source_text()
    forbidden = [
        "read_csv",
        "read_parquet",
    ]
    for token in forbidden:
        assert token not in text


def test_public_api_exports_expected_symbols():
    module = load_module()
    exported = set(module.__all__)
    expected = {
        "EvidenceCheck",
        "ReportingScaffoldStatus",
        "build_reporting_scaffold_status",
        "check_required_evidence",
        "validate_no_submit_boundary",
    }
    assert expected.issubset(exported)


def test_failure_reason_names_missing_evidence():
    module = load_module()
    status = module.build_reporting_scaffold_status()
    assert "Missing audited PPO v2 evidence" in status.reason


def test_validate_no_submit_boundary_matches_status_defaults():
    module = load_module()
    status = module.build_reporting_scaffold_status()
    boundary = module.validate_no_submit_boundary()
    assert boundary["NO_SUBMIT"] == status.no_submit
    assert boundary["controlled_submit"] == status.controlled_submit
    assert boundary["ppo_rf"] == status.ppo_rf
    assert boundary["ppo_xgboost"] == status.ppo_xgboost
