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

# ---------------------------------------------------------------------------
# v2.59 PPO v2 validation reporting scaffold evidence contract tests
# ---------------------------------------------------------------------------

import importlib.util as _v259_importlib_util
import sys as _v259_sys
from pathlib import Path as _V259Path


def _load_v259_reporting_module():
    repo_root = _V259Path(__file__).resolve().parents[1]
    module_path = repo_root / "src" / "ppo_v2_validation_reporting_scaffold.py"
    spec = _v259_importlib_util.spec_from_file_location(
        "ppo_v2_validation_reporting_scaffold_v259",
        module_path,
    )
    module = _v259_importlib_util.module_from_spec(spec)
    _v259_sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _v259_complete_manifest(module):
    return {
        key: {
            "path": f"artifacts/ppo_v2/quarantine/example/{key}.json",
            "sha256": "0" * 64,
        }
        for key in module.EVIDENCE_CONTRACT_REQUIRED_KEYS
    }


def test_v259_evidence_contract_defaults_fail_closed():
    module = _load_v259_reporting_module()

    result = module.validate_evidence_contract({})

    assert result.passed is False
    assert result.decision == module.EvidenceContractDecision.FAIL_CLOSED_MISSING_EVIDENCE
    assert tuple(result.missing_evidence_keys) == tuple(module.EVIDENCE_CONTRACT_REQUIRED_KEYS)
    assert result.no_submit_preserved is True
    assert result.controlled_submit_blocked is True
    assert result.paper_orders_blocked is True
    assert result.live_orders_blocked is True
    assert result.model_promotion_blocked is True
    assert result.hybrid_unblock_blocked is True
    assert result.read_only is True


def test_v259_evidence_contract_requires_all_evidence_domains():
    module = _load_v259_reporting_module()
    manifest = _v259_complete_manifest(module)
    removed_key = module.EVIDENCE_CONTRACT_REQUIRED_KEYS[0]
    manifest.pop(removed_key)

    result = module.validate_evidence_contract(manifest)

    assert result.passed is False
    assert removed_key in result.missing_evidence_keys
    assert result.domain_status[removed_key] == module.EvidenceDomainStatus.MISSING


def test_v259_evidence_contract_fails_when_path_missing():
    module = _load_v259_reporting_module()
    manifest = _v259_complete_manifest(module)
    broken_key = module.EVIDENCE_CONTRACT_REQUIRED_KEYS[1]
    manifest[broken_key] = {"sha256": "1" * 64}

    result = module.validate_evidence_contract(manifest)

    assert result.passed is False
    assert broken_key in result.missing_path_keys
    assert result.path_status[broken_key] == module.EvidencePathStatus.MISSING


def test_v259_evidence_contract_fails_when_hash_missing():
    module = _load_v259_reporting_module()
    manifest = _v259_complete_manifest(module)
    broken_key = module.EVIDENCE_CONTRACT_REQUIRED_KEYS[2]
    manifest[broken_key] = {"path": f"artifacts/ppo_v2/quarantine/example/{broken_key}.json"}

    result = module.validate_evidence_contract(manifest)

    assert result.passed is False
    assert broken_key in result.missing_hash_keys
    assert result.hash_status[broken_key] == module.EvidenceHashStatus.MISSING


def test_v259_evidence_contract_passes_with_complete_manifest():
    module = _load_v259_reporting_module()

    result = module.validate_evidence_contract(_v259_complete_manifest(module))

    assert result.passed is True
    assert result.decision == module.EvidenceContractDecision.PASS_READ_ONLY_NO_SUBMIT
    assert result.missing_evidence_keys == ()
    assert result.missing_path_keys == ()
    assert result.missing_hash_keys == ()
    assert all(status == module.EvidenceDomainStatus.PRESENT for status in result.domain_status.values())
    assert result.no_submit_preserved is True
    assert result.controlled_submit_blocked is True
    assert result.paper_orders_blocked is True
    assert result.live_orders_blocked is True
    assert result.model_promotion_blocked is True
    assert result.hybrid_unblock_blocked is True
    assert result.read_only is True


def test_v259_evidence_contract_no_submit_boundary_fails_closed_when_relaxed():
    module = _load_v259_reporting_module()
    contract = module.EvidenceContract(controlled_submit_blocked=False)

    result = module.validate_evidence_contract_no_submit_boundary(contract)

    assert result.passed is False
    assert result.decision == module.EvidenceContractDecision.FAIL_CLOSED_NO_SUBMIT_BOUNDARY


def test_v259_evidence_contract_exposes_required_domains():
    module = _load_v259_reporting_module()

    expected = {
        "training_outputs_inventory",
        "quarantine_output_manifest",
        "dataset_boundary_manifest",
        "leakage_control_evidence",
        "normalization_evidence",
        "locked_eval_stats_evidence",
        "untouched_holdout_evidence",
        "ppo_only_baseline_evidence",
        "post_run_audit",
    }

    assert expected.issubset(set(module.EVIDENCE_CONTRACT_REQUIRED_KEYS))


def test_v259_evidence_contract_source_has_no_broker_training_fetch_or_write_calls():
    module_path = (
        _V259Path(__file__).resolve().parents[1]
        / "src"
        / "ppo_v2_validation_reporting_scaffold.py"
    )
    source = module_path.read_text(encoding="utf-8")

    forbidden_tokens = [
        "from alpaca",
        "import alpaca",
        "TradingClient(",
        "StockHistoricalDataClient(",
        "submit_order(",
        "PPO.load(",
        "PPO(",
        ".learn(",
        ".fit(",
        "joblib.dump(",
        "torch.save(",
        "pickle.dump(",
        ".to_csv(",
        ".to_parquet(",
        "read_csv(",
        "read_parquet(",
        "requests.get(",
    ]

    for token in forbidden_tokens:
        assert token not in source


# ---------------------------------------------------------------------------
# v2.79 PPO v2 validation reporting scaffold evidence contract usage tests
# ---------------------------------------------------------------------------


def test_v279_usage_adapter_missing_manifest_fails_closed():
    module = _load_v259_reporting_module()

    result = module.validate_evidence_contract_usage(None)

    assert isinstance(result, module.EvidenceContractResult)
    assert result.passed is False
    assert result.decision == module.EvidenceContractDecision.FAIL_CLOSED_MISSING_EVIDENCE
    assert tuple(result.missing_evidence_keys) == tuple(module.EVIDENCE_CONTRACT_REQUIRED_KEYS)
    assert result.read_only is True
    assert result.no_submit_preserved is True
    assert result.controlled_submit_blocked is True


def test_v279_usage_adapter_missing_required_domain_fails_closed():
    module = _load_v259_reporting_module()
    manifest = _v259_complete_manifest(module)
    removed_key = module.EVIDENCE_CONTRACT_REQUIRED_KEYS[0]
    manifest.pop(removed_key)

    result = module.validate_evidence_contract_usage(manifest)

    assert result.passed is False
    assert removed_key in result.missing_evidence_keys
    assert result.domain_status[removed_key] == module.EvidenceDomainStatus.MISSING


def test_v279_usage_adapter_missing_path_metadata_fails_closed():
    module = _load_v259_reporting_module()
    manifest = _v259_complete_manifest(module)
    broken_key = module.EVIDENCE_CONTRACT_REQUIRED_KEYS[1]
    manifest[broken_key] = {"sha256": "1" * 64}

    result = module.validate_evidence_contract_usage(manifest)

    assert result.passed is False
    assert broken_key in result.missing_path_keys
    assert result.path_status[broken_key] == module.EvidencePathStatus.MISSING


def test_v279_usage_adapter_missing_hash_metadata_fails_closed():
    module = _load_v259_reporting_module()
    manifest = _v259_complete_manifest(module)
    broken_key = module.EVIDENCE_CONTRACT_REQUIRED_KEYS[2]
    manifest[broken_key] = {
        "path": f"artifacts/ppo_v2/quarantine/example/{broken_key}.json"
    }

    result = module.validate_evidence_contract_usage(manifest)

    assert result.passed is False
    assert broken_key in result.missing_hash_keys
    assert result.hash_status[broken_key] == module.EvidenceHashStatus.MISSING


def test_v279_usage_adapter_no_submit_relaxation_fails_closed():
    module = _load_v259_reporting_module()
    contract = module.EvidenceContract(controlled_submit_blocked=False)

    result = module.validate_evidence_contract_usage(
        _v259_complete_manifest(module),
        contract=contract,
    )

    assert result.passed is False
    assert result.decision == module.EvidenceContractDecision.FAIL_CLOSED_NO_SUBMIT_BOUNDARY
    assert result.controlled_submit_blocked is False


def test_v279_usage_adapter_complete_manifest_passes_read_only_no_submit():
    module = _load_v259_reporting_module()

    result = module.validate_evidence_contract_usage(_v259_complete_manifest(module))

    assert result.passed is True
    assert result.decision == module.EvidenceContractDecision.PASS_READ_ONLY_NO_SUBMIT
    assert result.missing_evidence_keys == ()
    assert result.missing_path_keys == ()
    assert result.missing_hash_keys == ()
    assert result.read_only is True
    assert result.no_submit_preserved is True
    assert result.controlled_submit_blocked is True
    assert result.paper_orders_blocked is True
    assert result.live_orders_blocked is True
    assert result.model_promotion_blocked is True
    assert result.hybrid_unblock_blocked is True


def test_v279_usage_adapter_returns_evidence_contract_result_only():
    module = _load_v259_reporting_module()

    result = module.build_read_only_evidence_contract_usage_result(
        _v259_complete_manifest(module)
    )

    assert type(result) is module.EvidenceContractResult


def test_v279_usage_adapter_has_no_broker_training_fetch_or_write_calls():
    source = source_text()

    forbidden_tokens = [
        "from alpaca",
        "import alpaca",
        "TradingClient(",
        "StockHistoricalDataClient(",
        "submit_order(",
        "PPO.load(",
        "PPO(",
        ".learn(",
        ".fit(",
        "joblib.dump(",
        "torch.save(",
        "pickle.dump(",
        ".to_csv(",
        ".to_parquet(",
        "read_csv(",
        "read_parquet(",
        "requests.get(",
    ]

    for token in forbidden_tokens:
        assert token not in source


def test_v279_usage_adapter_does_not_generate_reports_metrics_plots_or_dashboards():
    module = _load_v259_reporting_module()

    result = module.validate_evidence_contract_usage(_v259_complete_manifest(module))

    assert isinstance(result, module.EvidenceContractResult)
    assert not hasattr(result, "metrics")
    assert not hasattr(result, "report")
    assert not hasattr(result, "plot")
    assert not hasattr(result, "dashboard")


def test_v279_usage_adapter_blocks_model_promotion_and_orders():
    module = _load_v259_reporting_module()

    result = module.validate_evidence_contract_usage(_v259_complete_manifest(module))

    assert result.model_promotion_blocked is True
    assert result.paper_orders_blocked is True
    assert result.live_orders_blocked is True


def test_v279_usage_adapter_preserves_controlled_submit_block():
    module = _load_v259_reporting_module()

    result = module.validate_evidence_contract_usage(_v259_complete_manifest(module))

    assert result.controlled_submit_blocked is True
    assert result.no_submit_preserved is True


def test_v279_usage_adapter_preserves_hybrid_blocks():
    module = _load_v259_reporting_module()

    result = module.validate_evidence_contract_usage(_v259_complete_manifest(module))

    assert result.hybrid_unblock_blocked is True
