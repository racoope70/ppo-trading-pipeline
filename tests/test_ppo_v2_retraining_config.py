from dataclasses import replace
from pathlib import Path

import pytest

from src.ppo_v2_retraining_config import (
    CANONICAL_PPO_V2_SYMBOLS,
    FORBIDDEN_MODEL_INPUT_COLUMNS,
    PPOV2ControlledRetrainingConfig,
    PPOV2SafetyFlags,
    build_default_ppo_v2_config,
    validate_config_safety,
)


def test_default_ppo_v2_config_is_fail_closed():
    config = build_default_ppo_v2_config()

    assert config.safety_flags.as_dict() == {
        "training_execution_enabled": False,
        "dataset_generation_enabled": False,
        "model_artifact_creation_enabled": False,
        "paper_order_submission_enabled": False,
        "live_order_submission_enabled": False,
        "controlled_submit_enabled": False,
        "hybrid_deployment_enabled": False,
    }

    assert validate_config_safety(config) == []
    config.validate_safety()


def test_default_ppo_v2_config_has_no_execution_commands():
    config = build_default_ppo_v2_config()

    assert config.training_command is None
    assert config.dataset_generation_command is None
    assert config.model_artifact_command is None
    assert config.paper_order_command is None


def test_default_ppo_v2_config_uses_six_ticker_baseline():
    config = build_default_ppo_v2_config()

    assert config.symbols == CANONICAL_PPO_V2_SYMBOLS
    assert set(config.symbols) == {"AAPL", "AMD", "MRK", "PFE", "UNH", "XOM"}


def test_default_ppo_v2_config_excludes_forbidden_model_input_columns():
    config = build_default_ppo_v2_config()

    assert set(FORBIDDEN_MODEL_INPUT_COLUMNS).issubset(
        set(config.model_input_exclusion_columns)
    )

    assert set(config.model_input_exclusion_columns) == {
        "Target",
        "Return",
        "Datetime",
        "Symbol",
    }


def test_default_ppo_v2_artifact_paths_are_isolated_from_legacy_paths():
    config = build_default_ppo_v2_config()

    assert config.model_artifact_root == Path("models/ppo_v2_controlled_retraining")
    assert config.report_root == Path("reports/ppo_v2_controlled_retraining")
    assert config.model_artifact_root not in config.legacy_artifact_roots
    assert config.report_root != config.model_artifact_root


@pytest.mark.parametrize(
    "unsafe_flag",
    [
        "training_execution_enabled",
        "dataset_generation_enabled",
        "model_artifact_creation_enabled",
        "paper_order_submission_enabled",
        "live_order_submission_enabled",
        "controlled_submit_enabled",
        "hybrid_deployment_enabled",
    ],
)
def test_safety_validation_rejects_enabled_flags(unsafe_flag):
    safe_config = build_default_ppo_v2_config()
    unsafe_flags = replace(safe_config.safety_flags, **{unsafe_flag: True})
    unsafe_config = replace(safe_config, safety_flags=unsafe_flags)

    errors = validate_config_safety(unsafe_config)

    assert errors
    assert unsafe_flag in errors[0]

    with pytest.raises(ValueError, match=unsafe_flag):
        unsafe_config.validate_safety()


@pytest.mark.parametrize(
    "command_field",
    [
        "training_command",
        "dataset_generation_command",
        "model_artifact_command",
        "paper_order_command",
    ],
)
def test_safety_validation_rejects_execution_commands(command_field):
    safe_config = build_default_ppo_v2_config()
    unsafe_config = replace(safe_config, **{command_field: "python forbidden.py"})

    errors = validate_config_safety(unsafe_config)

    assert errors
    assert command_field in errors[0]

    with pytest.raises(ValueError, match=command_field):
        unsafe_config.validate_safety()


def test_safety_validation_rejects_legacy_artifact_root():
    safe_config = build_default_ppo_v2_config()
    unsafe_config = replace(
        safe_config,
        model_artifact_root=Path("models/alpaca_ppo_models_master"),
    )

    errors = validate_config_safety(unsafe_config)

    assert errors
    assert "legacy artifact roots" in errors[0]


def test_safety_validation_rejects_non_baseline_universe():
    safe_config = build_default_ppo_v2_config()
    unsafe_config = replace(safe_config, symbols=("AAPL", "TSLA"))

    errors = validate_config_safety(unsafe_config)

    assert errors
    assert "six-ticker PPO v2 baseline universe" in errors[0]


def test_safety_validation_rejects_holdout_misuse():
    safe_config = build_default_ppo_v2_config()
    unsafe_config = replace(safe_config, holdout_usage="tuning")

    errors = validate_config_safety(unsafe_config)

    assert errors
    assert "holdout usage" in errors[0]