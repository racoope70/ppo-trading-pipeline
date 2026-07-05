from src.ppo_v2_one_time_controlled_execution_package import (
    OUTPUT_CLASSIFICATION,
    PACKAGE_SCHEMA_VERSION,
    PACKAGE_STATUS,
    PPOV2OneTimeExecutionPackageRequest,
    build_ppo_v2_one_time_execution_package,
)


def test_default_package_scaffold_passes_and_is_non_executing():
    result = build_ppo_v2_one_time_execution_package()

    assert result.boundary_decision == "PASS"
    assert result.errors == ()
    assert result.package_manifest is not None

    manifest = result.package_manifest
    assert manifest["schema_version"] == PACKAGE_SCHEMA_VERSION
    assert manifest["package_status"] == PACKAGE_STATUS
    assert manifest["output_classification"] == OUTPUT_CLASSIFICATION
    assert manifest["training_execution_performed"] is False
    assert manifest["data_fetching_performed"] is False
    assert manifest["dataset_generation_performed"] is False
    assert manifest["model_artifact_creation_performed"] is False
    assert manifest["controlled_submit_authorized"] is False
    assert manifest["no_submit_default"] is True
    assert manifest["canonical_command_module"] == "src.ppo_v2_controlled_training_execution"
    assert manifest["command_boundary_status"] == "FUTURE_ONLY_NO_SUBMIT_REVIEW_BOUNDARY_NOT_AUTHORIZATION"


def test_manifest_outputs_are_quarantined():
    result = build_ppo_v2_one_time_execution_package()
    output_paths = result.package_manifest["output_paths"]

    assert output_paths
    for output_path in output_paths.values():
        assert output_path.startswith("artifacts/ppo_v2/quarantine/")


def test_missing_no_submit_fails_closed():
    request = PPOV2OneTimeExecutionPackageRequest(
        command=(
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution",
            "--mode",
            "controlled-training",
            "--run-id",
            "run_001",
            "--config",
            "configs/ppo_v2/config.yaml",
            "--quarantine-root",
            "artifacts/ppo_v2/quarantine/run_001",
        )
    )

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("--no-submit" in error for error in result.errors)


def test_missing_mode_fails_closed():
    request = PPOV2OneTimeExecutionPackageRequest(
        command=(
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution",
            "--run-id",
            "run_001",
            "--config",
            "configs/ppo_v2/config.yaml",
            "--quarantine-root",
            "artifacts/ppo_v2/quarantine/run_001",
            "--no-submit",
        )
    )

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("controlled-training mode" in error for error in result.errors)


def test_non_quarantined_root_fails_closed():
    request = PPOV2OneTimeExecutionPackageRequest(
        quarantine_root="artifacts/ppo_v2/promoted/run_001",
        command=(
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution",
            "--mode",
            "controlled-training",
            "--run-id",
            "run_001",
            "--config",
            "configs/ppo_v2/config.yaml",
            "--quarantine-root",
            "artifacts/ppo_v2/promoted/run_001",
            "--no-submit",
        ),
    )

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("quarantine_root" in error for error in result.errors)


def test_training_permission_fails_closed():
    request = PPOV2OneTimeExecutionPackageRequest(allow_training_execution=True)

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("training execution" in error for error in result.errors)


def test_artifact_creation_permission_fails_closed():
    request = PPOV2OneTimeExecutionPackageRequest(allow_model_artifact_creation=True)

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("model artifact creation" in error for error in result.errors)


def test_controlled_submit_permission_fails_closed():
    request = PPOV2OneTimeExecutionPackageRequest(allow_controlled_submit=True)

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("controlled submit" in error for error in result.errors)


def test_paper_and_live_permissions_fail_closed():
    request = PPOV2OneTimeExecutionPackageRequest(
        allow_paper_orders=True,
        allow_live_orders=True,
    )

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("paper orders" in error for error in result.errors)
    assert any("live orders" in error for error in result.errors)


def test_hybrid_permissions_fail_closed():
    request = PPOV2OneTimeExecutionPackageRequest(
        allow_ppo_rf=True,
        allow_ppo_xgboost=True,
    )

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("Random Forest" in error for error in result.errors)
    assert any("XGBoost" in error for error in result.errors)


def test_missing_package_item_fails_closed():
    request = PPOV2OneTimeExecutionPackageRequest(package_items=())

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("missing required package items" in error for error in result.errors)


def test_missing_guardrail_fails_closed():
    request = PPOV2OneTimeExecutionPackageRequest(guardrails=())

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("missing required guardrails" in error for error in result.errors)


def test_missing_output_file_fails_closed():
    request = PPOV2OneTimeExecutionPackageRequest(output_files=())

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("missing required output files" in error for error in result.errors)


def test_command_with_live_fragment_fails_closed():
    request = PPOV2OneTimeExecutionPackageRequest(
        command=(
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution",
            "--mode",
            "controlled-training",
            "--run-id",
            "run_001",
            "--config",
            "configs/ppo_v2/config.yaml",
            "--quarantine-root",
            "artifacts/ppo_v2/quarantine/run_001",
            "--no-submit",
            "--live",
        )
    )

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("prohibited fragment" in error for error in result.errors)


def test_command_with_submit_fragment_outside_no_submit_fails_closed():
    request = PPOV2OneTimeExecutionPackageRequest(
        command=(
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution",
            "--mode",
            "controlled-training",
            "--run-id",
            "run_001",
            "--config",
            "configs/ppo_v2/config.yaml",
            "--quarantine-root",
            "artifacts/ppo_v2/quarantine/run_001",
            "--no-submit",
            "--submit-preview",
        )
    )

    result = build_ppo_v2_one_time_execution_package(request)

    assert result.boundary_decision == "FAIL_CLOSED"
    assert any("submit outside no-submit" in error for error in result.errors)
