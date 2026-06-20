from dataclasses import replace
from pathlib import Path
import re

import pandas as pd
import pytest

from src.ppo_v2_training_configuration import (
    PPOV2TrainingConfigurationRequest,
    build_ppo_v2_training_configuration,
)
from src.ppo_v2_training_input_handoff import PPOV2TrainingInputHandoffResult


def _frame(columns=("Open", "High", "Low", "Close", "Volume", "SMA_20")):
    return pd.DataFrame(
        {
            column: [1.0, 2.0, 3.0]
            for column in columns
        }
    )


def _valid_handoff_result(
    *,
    observation_columns=("Open", "High", "Low", "Close", "Volume", "SMA_20"),
    boundary_decision="PASS",
    handoff_errors=(),
    train_df=None,
    eval_df=None,
    holdout_df=None,
):
    return PPOV2TrainingInputHandoffResult(
        train_df=_frame(observation_columns) if train_df is None else train_df,
        eval_df=_frame(observation_columns) if eval_df is None else eval_df,
        holdout_df=_frame(observation_columns) if holdout_df is None else holdout_df,
        observation_columns=tuple(observation_columns),
        handoff_errors=tuple(handoff_errors),
        handoff_metadata={"training_authorized": False},
        boundary_decision=boundary_decision,
    )


def _valid_request():
    return PPOV2TrainingConfigurationRequest(
        training_input_handoff_result=_valid_handoff_result(),
    )


def _assert_failed_with(result, expected_error):
    assert result.boundary_decision == "REJECTED_FAIL_CLOSED"
    assert result.training_configuration is None
    assert expected_error in result.configuration_errors


def test_valid_configuration_request_passes():
    result = build_ppo_v2_training_configuration(_valid_request())

    assert result.boundary_decision == "PASS"
    assert result.configuration_errors == ()
    assert result.training_configuration is not None
    assert result.training_configuration.ppo_algorithm_family == "PPO"
    assert result.training_configuration.policy_type == "MlpPolicy"
    assert result.training_configuration.total_timesteps == 1_500_000
    assert result.training_configuration.allowed_artifact_policy == "disabled"
    assert result.training_configuration.observation_columns == (
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "SMA_20",
    )
    assert result.configuration_metadata["training_authorized"] is False
    assert result.configuration_metadata["artifact_creation_authorized"] is False
    assert result.configuration_metadata["controlled_submit_authorized"] is False


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_error"),
    [
        ("run_identifier", "", "run_identifier must be a non-empty string"),
        (
            "execution_mode",
            "train",
            "execution_mode is not allowed for training configuration boundary",
        ),
        ("ppo_algorithm_family", "A2C", "ppo_algorithm_family is not supported"),
        ("policy_type", "CnnPolicy", "policy_type is not supported"),
        ("total_timesteps", 0, "total_timesteps must be a positive integer"),
        ("learning_rate", 0.0, "learning_rate must be positive"),
        ("n_steps", 0, "n_steps must be a positive integer"),
        ("batch_size", 0, "batch_size must be a positive integer"),
        ("gamma", 1.5, "gamma must be greater than 0 and less than or equal to 1"),
        ("gae_lambda", 0.0, "gae_lambda must be greater than 0 and less than or equal to 1"),
        ("clip_range", 0.0, "clip_range must be greater than 0 and less than or equal to 1"),
        ("ent_coef", -0.1, "ent_coef must be non-negative"),
        ("vf_coef", -0.1, "vf_coef must be non-negative"),
        ("max_grad_norm", 0.0, "max_grad_norm must be positive"),
        ("seed", -1, "seed must be a non-negative integer"),
        ("device_preference", "mps", "device_preference is not supported"),
        ("environment_id", "", "environment_id must be a non-empty string"),
        ("reward_contract_name", "", "reward_contract_name must be a non-empty string"),
        ("risk_contract_name", "", "risk_contract_name must be a non-empty string"),
        ("evaluation_frequency", 0, "evaluation_frequency must be a positive integer"),
        ("checkpoint_frequency", 0, "checkpoint_frequency must be a positive integer"),
        (
            "allowed_artifact_policy",
            "save_models",
            "allowed_artifact_policy must remain disabled",
        ),
    ],
)
def test_invalid_configuration_fields_fail_closed(field_name, invalid_value, expected_error):
    request = replace(_valid_request(), **{field_name: invalid_value})
    result = build_ppo_v2_training_configuration(request)

    _assert_failed_with(result, expected_error)


def test_missing_handoff_result_fails_closed():
    request = PPOV2TrainingConfigurationRequest(training_input_handoff_result=None)

    result = build_ppo_v2_training_configuration(request)

    _assert_failed_with(result, "training_input_handoff_result must be present")


def test_invalid_handoff_result_type_fails_closed():
    request = replace(_valid_request(), training_input_handoff_result="not-a-handoff-result")

    result = build_ppo_v2_training_configuration(request)

    _assert_failed_with(
        result,
        "training_input_handoff_result must be a PPOV2TrainingInputHandoffResult",
    )


def test_invalid_handoff_boundary_decision_fails_closed():
    request = replace(
        _valid_request(),
        training_input_handoff_result=_valid_handoff_result(
            boundary_decision="REJECTED_FAIL_CLOSED"
        ),
    )

    result = build_ppo_v2_training_configuration(request)

    _assert_failed_with(
        result,
        "training_input_handoff_result boundary_decision must be PASS",
    )


def test_handoff_errors_fail_closed():
    request = replace(
        _valid_request(),
        training_input_handoff_result=_valid_handoff_result(
            handoff_errors=("previous handoff error",)
        ),
    )

    result = build_ppo_v2_training_configuration(request)

    _assert_failed_with(result, "training_input_handoff_result must not contain handoff_errors")


@pytest.mark.parametrize(
    ("split_name", "expected_error"),
    [
        ("train_df", "train_df must be a non-empty DataFrame"),
        ("eval_df", "eval_df must be a non-empty DataFrame"),
        ("holdout_df", "holdout_df must be a non-empty DataFrame"),
    ],
)
def test_missing_or_empty_split_data_fails_closed(split_name, expected_error):
    handoff_kwargs = {split_name: pd.DataFrame()}
    request = replace(
        _valid_request(),
        training_input_handoff_result=_valid_handoff_result(**handoff_kwargs),
    )

    result = build_ppo_v2_training_configuration(request)

    _assert_failed_with(result, expected_error)


def test_empty_observation_columns_fail_closed():
    request = replace(
        _valid_request(),
        training_input_handoff_result=_valid_handoff_result(observation_columns=()),
    )

    result = build_ppo_v2_training_configuration(request)

    _assert_failed_with(result, "observation_columns must be non-empty")


def test_forbidden_training_columns_fail_closed():
    request = replace(
        _valid_request(),
        training_input_handoff_result=_valid_handoff_result(
            observation_columns=("Open", "Close", "Target")
        ),
    )

    result = build_ppo_v2_training_configuration(request)

    _assert_failed_with(
        result,
        "observation_columns contain forbidden training configuration columns",
    )


@pytest.mark.parametrize(
    ("field_name", "expected_error"),
    [
        ("request_training_execution", "training execution request is not authorized"),
        ("request_artifact_creation", "artifact creation request is not authorized"),
        ("request_paper_orders", "paper order request is not authorized"),
        ("request_live_orders", "live order request is not authorized"),
        ("request_controlled_submit", "controlled submit request is not authorized"),
    ],
)
def test_authorization_request_flags_fail_closed(field_name, expected_error):
    request = replace(_valid_request(), **{field_name: True})

    result = build_ppo_v2_training_configuration(request)

    _assert_failed_with(result, expected_error)


def test_non_request_object_fails_closed():
    result = build_ppo_v2_training_configuration(None)

    _assert_failed_with(
        result,
        "request must be a PPOV2TrainingConfigurationRequest",
    )


def test_metadata_preserves_non_authorizations():
    result = build_ppo_v2_training_configuration(_valid_request())

    assert result.boundary_decision == "PASS"
    assert result.configuration_metadata["training_authorized"] is False
    assert result.configuration_metadata["training_execution_authorized"] is False
    assert result.configuration_metadata["artifact_creation_authorized"] is False
    assert result.configuration_metadata["data_fetching_authorized"] is False
    assert result.configuration_metadata["dataset_write_authorized"] is False
    assert result.configuration_metadata["paper_order_authorized"] is False
    assert result.configuration_metadata["live_order_authorized"] is False
    assert result.configuration_metadata["controlled_submit_authorized"] is False
    assert result.configuration_metadata["ppo_rf_unblocked"] is False
    assert result.configuration_metadata["ppo_xgboost_unblocked"] is False


def test_repeated_calls_are_deterministic():
    request = _valid_request()

    first = build_ppo_v2_training_configuration(request)
    second = build_ppo_v2_training_configuration(request)

    assert first.boundary_decision == second.boundary_decision
    assert first.configuration_errors == second.configuration_errors
    assert first.training_configuration == second.training_configuration
    assert first.configuration_metadata == second.configuration_metadata


def test_training_configuration_source_boundary_scan_has_no_execution_hooks():
    source = Path("src/ppo_v2_training_configuration.py").read_text(encoding="utf-8")
    forbidden_patterns = [
        r"TradingClient",
        r"StockHistoricalDataClient",
        r"submit_order",
        r"PPO\.load",
        r"\.learn\(",
        r"\.fit\(",
        r"joblib\.dump",
        r"torch\.save",
        r"pickle\.dump",
        r"\.to_csv",
        r"\.to_parquet",
        r"read_csv",
        r"read_parquet",
        r"requests\.get",
        r"alpaca",
    ]

    matches = [
        pattern
        for pattern in forbidden_patterns
        if re.search(pattern, source)
    ]

    assert matches == []
