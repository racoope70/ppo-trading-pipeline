from src.ppo_v2_controlled_training_package_preparation import (
    PACKAGE_CLASSIFICATION,
    PREPARATION_SCHEMA_VERSION,
    PREPARATION_STATUS,
    PPOV2PreparationScaffoldRequest,
    build_ppo_v2_preparation_scaffold,
)


def test_default_preparation_scaffold_passes_and_is_non_executing():
    result = build_ppo_v2_preparation_scaffold()

    assert result.boundary_decision == "PASS"
    assert result.errors == ()
    assert result.preparation_manifest is not None

    manifest = result.preparation_manifest
    assert manifest["schema_version"] == PREPARATION_SCHEMA_VERSION
    assert manifest["preparation_status"] == PREPARATION_STATUS
    assert manifest["package_classification"] == PACKAGE_CLASSIFICATION
    assert manifest["training_execution_performed"] is False
    assert manifest["data_fetching_performed"] is False
    assert manifest["dataset_generation_performed"] is False
    assert manifest["model_artifact_creation_performed"] is False
    assert manifest["filesystem_writes_performed"] is False
    assert manifest["controlled_submit_authorized"] is False
    assert manifest["no_submit_default"] is True
    assert manifest["canonical_command_module"] == "src.ppo_v2_controlled_training_execution"
    assert manifest["command_boundary_status"] == "FUTURE_ONLY_NO_SUBMIT_REVIEW_BOUNDARY_NOT_AUTHORIZATION"


def test_preparation_paths_stay_under_package_preparation_root():
    result = build_ppo_v2_preparation_scaffold()
    paths = result.preparation_manifest["preparation_paths"]

    assert paths
    for path in paths.values():
        assert path.startswith("artifacts/ppo_v2/package_preparation/")


def test_quarantine_root_is_preserved_for_future_outputs_only():
    result = build_ppo_v2_preparation_scaffold()

    assert result.preparation_manifest["quarantine_root"].startswith(
        "artifacts/ppo_v2/quarantine/"
    )


def test_missing_no_submit_fails_closed():
    request = PPOV2PreparationScaffoldRequest(
        command=(
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution",
            "--mode",
            "controlled-training",
            "--run-id",
            "run_001",
            "--config",
            "artifacts/ppo_v2/package_preparation/run_001/config/controlled_training_config.yaml",
            "--quarantine-root",
            "artifacts/ppo_v2/quarantine/run_001",
        )
    )

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("--no-submit" in error for error in result.errors)


def test_missing_mode_fails_closed():
    request = PPOV2PreparationScaffoldRequest(
        command=(
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution",
            "--run-id",
            "run_001",
            "--config",
            "artifacts/ppo_v2/package_preparation/run_001/config/controlled_training_config.yaml",
            "--quarantine-root",
            "artifacts/ppo_v2/quarantine/run_001",
            "--no-submit",
        )
    )

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("controlled-training mode" in error for error in result.errors)


def test_non_preparation_root_fails_closed():
    request = PPOV2PreparationScaffoldRequest(
        preparation_root="artifacts/ppo_v2/promoted/run_001"
    )

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("preparation_root" in error for error in result.errors)


def test_non_quarantine_root_fails_closed():
    request = PPOV2PreparationScaffoldRequest(
        quarantine_root="artifacts/ppo_v2/promoted/run_001"
    )

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("quarantine_root" in error for error in result.errors)


def test_training_permission_fails_closed():
    request = PPOV2PreparationScaffoldRequest(allow_training_execution=True)

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("training execution" in error for error in result.errors)


def test_data_fetching_permission_fails_closed():
    request = PPOV2PreparationScaffoldRequest(allow_data_fetching=True)

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("data fetching" in error for error in result.errors)


def test_model_artifact_creation_permission_fails_closed():
    request = PPOV2PreparationScaffoldRequest(allow_model_artifact_creation=True)

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("model artifact creation" in error for error in result.errors)


def test_filesystem_write_permission_fails_closed():
    request = PPOV2PreparationScaffoldRequest(allow_filesystem_writes=True)

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("filesystem writes" in error for error in result.errors)


def test_controlled_submit_permission_fails_closed():
    request = PPOV2PreparationScaffoldRequest(allow_controlled_submit=True)

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("controlled submit" in error for error in result.errors)


def test_paper_and_live_permissions_fail_closed():
    request = PPOV2PreparationScaffoldRequest(
        allow_paper_orders=True,
        allow_live_orders=True,
    )

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("paper orders" in error for error in result.errors)
    assert any("live orders" in error for error in result.errors)


def test_hybrid_permissions_fail_closed():
    request = PPOV2PreparationScaffoldRequest(
        allow_ppo_rf=True,
        allow_ppo_xgboost=True,
    )

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("Random Forest" in error for error in result.errors)
    assert any("XGBoost" in error for error in result.errors)


def test_missing_required_preparation_files_fail_closed():
    request = PPOV2PreparationScaffoldRequest(preparation_files=())

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("missing required preparation files" in error for error in result.errors)


def test_missing_controlled_boundaries_fail_closed():
    request = PPOV2PreparationScaffoldRequest(controlled_boundaries=())

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("missing required controlled boundaries" in error for error in result.errors)


def test_command_with_live_fragment_fails_closed():
    request = PPOV2PreparationScaffoldRequest(
        command=(
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution",
            "--mode",
            "controlled-training",
            "--run-id",
            "run_001",
            "--config",
            "artifacts/ppo_v2/package_preparation/run_001/config/controlled_training_config.yaml",
            "--quarantine-root",
            "artifacts/ppo_v2/quarantine/run_001",
            "--no-submit",
            "--live",
        )
    )

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("prohibited fragment" in error for error in result.errors)


def test_command_with_submit_fragment_outside_no_submit_fails_closed():
    request = PPOV2PreparationScaffoldRequest(
        command=(
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution",
            "--mode",
            "controlled-training",
            "--run-id",
            "run_001",
            "--config",
            "artifacts/ppo_v2/package_preparation/run_001/config/controlled_training_config.yaml",
            "--quarantine-root",
            "artifacts/ppo_v2/quarantine/run_001",
            "--no-submit",
            "--submit-preview",
        )
    )

    result = build_ppo_v2_preparation_scaffold(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("submit outside no-submit" in error for error in result.errors)
