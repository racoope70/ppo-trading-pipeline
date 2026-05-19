import json
from pathlib import Path

import pytest

from src.paper_trading.artifact_manifest import (
    assert_all_required_artifacts_exist,
    load_manifest,
    resolve_artifact_paths,
    verify_manifest_artifacts,
)


def _write_manifest(path: Path) -> None:
    payload = {
        "artifact_manifest_version": "0.3",
        "baseline_name": "six_ticker_ppo_validation_baseline",
        "source_git_tag": "v0.2-six-ticker-validation-baseline",
        "universe": ["AAPL", "AMD"],
        "selected_models": {
            "AAPL": "ppo_AAPL_window1",
            "AMD": "ppo_AMD_window3",
        },
        "source_validation": {
            "validation_type": "unit_test",
            "final_equity": 100000.0,
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_load_manifest_validates_selected_models(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path)

    manifest = load_manifest(manifest_path)

    assert manifest.baseline_name == "six_ticker_ppo_validation_baseline"
    assert manifest.source_git_tag == "v0.2-six-ticker-validation-baseline"
    assert manifest.universe == ["AAPL", "AMD"]
    assert manifest.selected_prefix("AAPL") == "ppo_AAPL_window1"
    assert manifest.selected_prefix("AMD") == "ppo_AMD_window3"


def test_load_manifest_rejects_missing_selected_model(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    payload = {
        "baseline_name": "bad_manifest",
        "source_git_tag": "v0.2",
        "universe": ["AAPL", "AMD"],
        "selected_models": {
            "AAPL": "ppo_AAPL_window1",
        },
        "source_validation": {},
    }
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="missing symbols"):
        load_manifest(manifest_path)


def test_resolve_artifact_paths_finds_expected_files(tmp_path):
    prefix = "ppo_AAPL_window1"

    model_path = tmp_path / f"{prefix}_model.zip"
    vecnorm_path = tmp_path / f"{prefix}_vecnorm.pkl"
    features_path = tmp_path / f"{prefix}_features.json"

    model_path.write_text("model", encoding="utf-8")
    vecnorm_path.write_text("vecnorm", encoding="utf-8")
    features_path.write_text("features", encoding="utf-8")

    paths = resolve_artifact_paths(tmp_path, prefix)

    assert paths["model_zip"] == model_path
    assert paths["vecnormalize_pkl"] == vecnorm_path
    assert paths["features_json"] == features_path


def test_verify_manifest_artifacts_reports_missing_and_present(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path)
    manifest = load_manifest(manifest_path)

    # AAPL complete
    for suffix in ["model.zip", "vecnorm.pkl", "features.json"]:
        (tmp_path / f"ppo_AAPL_window1_{suffix}").write_text("x", encoding="utf-8")

    # AMD incomplete
    (tmp_path / "ppo_AMD_window3_model.zip").write_text("x", encoding="utf-8")

    rows = verify_manifest_artifacts(manifest, tmp_path)
    by_symbol = {row["symbol"]: row for row in rows}

    assert by_symbol["AAPL"]["all_required_artifacts_exist"] is True
    assert by_symbol["AMD"]["all_required_artifacts_exist"] is False

    with pytest.raises(FileNotFoundError, match="Missing required paper-trading artifacts"):
        assert_all_required_artifacts_exist(manifest, tmp_path)
