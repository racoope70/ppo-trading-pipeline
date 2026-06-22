from src.ppo_v2_controlled_training_execution_wrapper import (
    PPOV2ControlledExecutionWrapperRequest,
    build_ppo_v2_controlled_execution_wrapper,
)


def test_default_wrapper_manifest_passes_and_is_non_executing():
    result = build_ppo_v2_controlled_execution_wrapper()

    assert result.boundary_decision == "PASS"
    assert result.errors == ()
    assert result.wrapper_manifest is not None

    manifest = result.wrapper_manifest
    assert manifest["schema_version"] == "v2.01"
    assert manifest["wrapper_status"] == "SCAFFOLD_ONLY"
    assert manifest["execution_performed"] is False
    assert manifest["training_execution_authorized"] is False
    assert manifest["data_fetching_authorized"] is False
    assert manifest["dataset_generation_authorized"] is False
    assert manifest["model_artifact_creation_authorized"] is False
    assert manifest["model_promotion_authorized"] is False
    assert manifest["paper_order_authorized"] is False
    assert manifest["live_order_authorized"] is False
    assert manifest["controlled_submit_authorized"] is False
    assert manifest["ppo_rf_unblocked"] is False
    assert manifest["ppo_xgboost_unblocked"] is False
    assert manifest["no_submit_default"] is True
    assert manifest["output_classification"] == "QUARANTINED_TRAINING_OUTPUT_ONLY"
    assert "--no-submit" in manifest["command_specification"]["command_tokens"]
    assert manifest["command_specification"]["execution_mode"] == "scaffold_only"


def test_wrapper_manifest_contains_required_capture_paths():
    result = build_ppo_v2_controlled_execution_wrapper()
    assert result.wrapper_manifest is not None

    capture_paths = result.wrapper_manifest["capture_paths"]
    expected = {
        "configuration_snapshot_path",
        "training_input_manifest_path",
        "runtime_log_path",
        "stdout_capture_path",
        "stderr_capture_path",
        "artifact_inventory_path",
        "checksum_manifest_path",
        "metrics_output_path",
        "post_training_audit_package_path",
    }
    assert set(capture_paths) == expected
    assert all("quarantine" in value for value in capture_paths.values())


def test_wrapper_rejects_training_execution_permission():
    request = PPOV2ControlledExecutionWrapperRequest(allow_training_execution=True)

    result = build_ppo_v2_controlled_execution_wrapper(request)

    assert result.boundary_decision == "REJECT"
    assert result.wrapper_manifest is None
    assert "training execution request is not authorized in v2.01" in result.errors


def test_wrapper_rejects_data_fetching_permission():
    request = PPOV2ControlledExecutionWrapperRequest(allow_data_fetching=True)

    result = build_ppo_v2_controlled_execution_wrapper(request)

    assert result.boundary_decision == "REJECT"
    assert result.wrapper_manifest is None
    assert "data fetching request is not authorized in v2.01" in result.errors


def test_wrapper_rejects_dataset_generation_permission():
    request = PPOV2ControlledExecutionWrapperRequest(allow_dataset_generation=True)

    result = build_ppo_v2_controlled_execution_wrapper(request)

    assert result.boundary_decision == "REJECT"
    assert result.wrapper_manifest is None
    assert "dataset generation request is not authorized in v2.01" in result.errors


def test_wrapper_rejects_model_artifact_creation_permission():
    request = PPOV2ControlledExecutionWrapperRequest(allow_model_artifact_creation=True)

    result = build_ppo_v2_controlled_execution_wrapper(request)

    assert result.boundary_decision == "REJECT"
    assert result.wrapper_manifest is None
    assert "model artifact creation request is not authorized in v2.01" in result.errors


def test_wrapper_rejects_broker_and_hybrid_permissions():
    request = PPOV2ControlledExecutionWrapperRequest(
        allow_paper_orders=True,
        allow_live_orders=True,
        allow_controlled_submit=True,
        allow_ppo_rf=True,
        allow_ppo_xgboost=True,
    )

    result = build_ppo_v2_controlled_execution_wrapper(request)

    assert result.boundary_decision == "REJECT"
    assert result.wrapper_manifest is None
    assert "paper order request is not authorized" in result.errors
    assert "live order request is not authorized" in result.errors
    assert "controlled submit request is not authorized" in result.errors
    assert "PPO + RF request is not authorized" in result.errors
    assert "PPO + XGBoost request is not authorized" in result.errors


def test_wrapper_rejects_missing_no_submit():
    request = PPOV2ControlledExecutionWrapperRequest(
        command_tokens=(
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution_wrapper",
            "--mode",
            "scaffold-only",
        )
    )

    result = build_ppo_v2_controlled_execution_wrapper(request)

    assert result.boundary_decision == "REJECT"
    assert result.wrapper_manifest is None
    assert "command_tokens must include --no-submit" in result.errors


def test_wrapper_rejects_non_scaffold_mode():
    request = PPOV2ControlledExecutionWrapperRequest(
        command_tokens=(
            "python",
            "-m",
            "src.ppo_v2_controlled_training_execution_wrapper",
            "--mode",
            "execute",
            "--no-submit",
        )
    )

    result = build_ppo_v2_controlled_execution_wrapper(request)

    assert result.boundary_decision == "REJECT"
    assert result.wrapper_manifest is None
    assert "command_tokens must use scaffold-only mode" in result.errors


def test_wrapper_rejects_prohibited_command_tokens():
    request = PPOV2ControlledExecutionWrapperRequest(
        command_tokens=(
            "python",
            "-m",
            "src.train",
            "--mode",
            "scaffold-only",
            "--no-submit",
            "--submit-orders",
        )
    )

    result = build_ppo_v2_controlled_execution_wrapper(request)

    assert result.boundary_decision == "REJECT"
    assert result.wrapper_manifest is None
    assert "command_tokens contain prohibited token: --submit-orders" in result.errors


def test_wrapper_rejects_paths_outside_quarantine():
    request = PPOV2ControlledExecutionWrapperRequest(
        runtime_log_path="artifacts/ppo_v2/runtime_log.json"
    )

    result = build_ppo_v2_controlled_execution_wrapper(request)

    assert result.boundary_decision == "REJECT"
    assert result.wrapper_manifest is None
    assert "runtime_log_path must remain under a quarantine path" in result.errors


def test_wrapper_rejects_missing_guardrails():
    request = PPOV2ControlledExecutionWrapperRequest(guardrails=("require_clean_git_state",))

    result = build_ppo_v2_controlled_execution_wrapper(request)

    assert result.boundary_decision == "REJECT"
    assert result.wrapper_manifest is None
    assert "required guardrails are incomplete" in result.errors


def test_wrapper_rejects_invalid_request_type():
    result = build_ppo_v2_controlled_execution_wrapper(request={"bad": "input"})

    assert result.boundary_decision == "REJECT"
    assert result.wrapper_manifest is None
    assert "request must be PPOV2ControlledExecutionWrapperRequest" in result.errors
