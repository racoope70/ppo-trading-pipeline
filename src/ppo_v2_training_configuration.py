"""PPO v2 training configuration boundary.

This module defines a non-executing configuration boundary for PPO v2.

The boundary converts a valid PPO v2 training-input handoff result into a
validated configuration object for a future controlled training authorization
checkpoint.

It does not fetch data, write datasets, train models, save artifacts, or submit
orders.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd

from src.ppo_v2_training_input_handoff import PPOV2TrainingInputHandoffResult


ALLOWED_TRAINING_CONFIGURATION_EXECUTION_MODES: tuple[str, ...] = (
    "dry_run",
    "validation_only",
)

ALLOWED_PPO_ALGORITHM_FAMILIES: tuple[str, ...] = ("PPO",)

ALLOWED_POLICY_TYPES: tuple[str, ...] = ("MlpPolicy",)

ALLOWED_DEVICE_PREFERENCES: tuple[str, ...] = (
    "auto",
    "cpu",
    "cuda",
)

ALLOWED_ARTIFACT_POLICIES: tuple[str, ...] = ("disabled",)

FORBIDDEN_TRAINING_CONFIGURATION_COLUMNS: tuple[str, ...] = (
    "Target",
    "Return",
    "Datetime",
    "Symbol",
)

PASS_DECISION = "PASS"
REJECTED_FAIL_CLOSED_DECISION = "REJECTED_FAIL_CLOSED"


@dataclass(frozen=True)
class PPOV2TrainingConfiguration:
    """Validated non-executing PPO v2 training configuration."""

    ppo_algorithm_family: str
    policy_type: str
    total_timesteps: int
    learning_rate: float
    n_steps: int
    batch_size: int
    gamma: float
    gae_lambda: float
    clip_range: float
    ent_coef: float
    vf_coef: float
    max_grad_norm: float
    seed: int
    device_preference: str
    environment_id: str
    reward_contract_name: str
    risk_contract_name: str
    evaluation_frequency: int
    checkpoint_frequency: int
    early_stop_policy: Mapping[str, Any]
    allowed_artifact_policy: str
    observation_columns: tuple[str, ...]


@dataclass(frozen=True)
class PPOV2TrainingConfigurationRequest:
    """Request to build a non-executing PPO v2 training configuration."""

    training_input_handoff_result: PPOV2TrainingInputHandoffResult | None
    run_identifier: str = "ppo_v2_training_configuration"
    execution_mode: str = "validation_only"
    ppo_algorithm_family: str = "PPO"
    policy_type: str = "MlpPolicy"
    total_timesteps: int = 1_500_000
    learning_rate: float = 3e-4
    n_steps: int = 2_048
    batch_size: int = 64
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_range: float = 0.20
    ent_coef: float = 0.0
    vf_coef: float = 0.50
    max_grad_norm: float = 0.50
    seed: int = 42
    device_preference: str = "auto"
    environment_id: str = "ppo_v2_controlled_retraining_env"
    reward_contract_name: str = "ppo_v2_reward_contract"
    risk_contract_name: str = "ppo_v2_risk_contract"
    evaluation_frequency: int = 10_000
    checkpoint_frequency: int = 50_000
    early_stop_policy: Mapping[str, Any] | None = None
    allowed_artifact_policy: str = "disabled"
    request_training_execution: bool = False
    request_artifact_creation: bool = False
    request_paper_orders: bool = False
    request_live_orders: bool = False
    request_controlled_submit: bool = False


@dataclass(frozen=True)
class PPOV2TrainingConfigurationResult:
    """Result from the non-executing PPO v2 training configuration boundary."""

    training_configuration: PPOV2TrainingConfiguration | None
    configuration_errors: tuple[str, ...]
    configuration_metadata: Mapping[str, Any]
    boundary_decision: str


def build_ppo_v2_training_configuration(
    request: PPOV2TrainingConfigurationRequest,
) -> PPOV2TrainingConfigurationResult:
    """Build a fail-closed, non-executing PPO v2 training configuration."""

    errors: list[str] = []

    if not isinstance(request, PPOV2TrainingConfigurationRequest):
        metadata = _build_metadata(request=None, handoff_result=None)
        return PPOV2TrainingConfigurationResult(
            training_configuration=None,
            configuration_errors=("request must be a PPOV2TrainingConfigurationRequest",),
            configuration_metadata=metadata,
            boundary_decision=REJECTED_FAIL_CLOSED_DECISION,
        )

    handoff_result = request.training_input_handoff_result

    if not isinstance(request.run_identifier, str) or not request.run_identifier.strip():
        errors.append("run_identifier must be a non-empty string")

    if request.execution_mode not in ALLOWED_TRAINING_CONFIGURATION_EXECUTION_MODES:
        errors.append("execution_mode is not allowed for training configuration boundary")

    if request.ppo_algorithm_family not in ALLOWED_PPO_ALGORITHM_FAMILIES:
        errors.append("ppo_algorithm_family is not supported")

    if request.policy_type not in ALLOWED_POLICY_TYPES:
        errors.append("policy_type is not supported")

    if _is_not_positive_int(request.total_timesteps):
        errors.append("total_timesteps must be a positive integer")

    if _is_not_positive_number(request.learning_rate):
        errors.append("learning_rate must be positive")

    if _is_not_positive_int(request.n_steps):
        errors.append("n_steps must be a positive integer")

    if _is_not_positive_int(request.batch_size):
        errors.append("batch_size must be a positive integer")

    if not _is_number_between_zero_and_one(request.gamma, include_one=True):
        errors.append("gamma must be greater than 0 and less than or equal to 1")

    if not _is_number_between_zero_and_one(request.gae_lambda, include_one=True):
        errors.append("gae_lambda must be greater than 0 and less than or equal to 1")

    if not _is_number_between_zero_and_one(request.clip_range, include_one=True):
        errors.append("clip_range must be greater than 0 and less than or equal to 1")

    if _is_negative_number(request.ent_coef):
        errors.append("ent_coef must be non-negative")

    if _is_negative_number(request.vf_coef):
        errors.append("vf_coef must be non-negative")

    if _is_not_positive_number(request.max_grad_norm):
        errors.append("max_grad_norm must be positive")

    if not isinstance(request.seed, int) or request.seed < 0:
        errors.append("seed must be a non-negative integer")

    if request.device_preference not in ALLOWED_DEVICE_PREFERENCES:
        errors.append("device_preference is not supported")

    if not isinstance(request.environment_id, str) or not request.environment_id.strip():
        errors.append("environment_id must be a non-empty string")

    if not isinstance(request.reward_contract_name, str) or not request.reward_contract_name.strip():
        errors.append("reward_contract_name must be a non-empty string")

    if not isinstance(request.risk_contract_name, str) or not request.risk_contract_name.strip():
        errors.append("risk_contract_name must be a non-empty string")

    if _is_not_positive_int(request.evaluation_frequency):
        errors.append("evaluation_frequency must be a positive integer")

    if _is_not_positive_int(request.checkpoint_frequency):
        errors.append("checkpoint_frequency must be a positive integer")

    if request.allowed_artifact_policy not in ALLOWED_ARTIFACT_POLICIES:
        errors.append("allowed_artifact_policy must remain disabled")

    if request.request_training_execution:
        errors.append("training execution request is not authorized")

    if request.request_artifact_creation:
        errors.append("artifact creation request is not authorized")

    if request.request_paper_orders:
        errors.append("paper order request is not authorized")

    if request.request_live_orders:
        errors.append("live order request is not authorized")

    if request.request_controlled_submit:
        errors.append("controlled submit request is not authorized")

    observation_columns = _extract_observation_columns(handoff_result)
    errors.extend(_validate_handoff_result(handoff_result, observation_columns))

    metadata = _build_metadata(request=request, handoff_result=handoff_result)

    if errors:
        return PPOV2TrainingConfigurationResult(
            training_configuration=None,
            configuration_errors=tuple(errors),
            configuration_metadata=metadata,
            boundary_decision=REJECTED_FAIL_CLOSED_DECISION,
        )

    training_configuration = PPOV2TrainingConfiguration(
        ppo_algorithm_family=request.ppo_algorithm_family,
        policy_type=request.policy_type,
        total_timesteps=request.total_timesteps,
        learning_rate=float(request.learning_rate),
        n_steps=request.n_steps,
        batch_size=request.batch_size,
        gamma=float(request.gamma),
        gae_lambda=float(request.gae_lambda),
        clip_range=float(request.clip_range),
        ent_coef=float(request.ent_coef),
        vf_coef=float(request.vf_coef),
        max_grad_norm=float(request.max_grad_norm),
        seed=request.seed,
        device_preference=request.device_preference,
        environment_id=request.environment_id,
        reward_contract_name=request.reward_contract_name,
        risk_contract_name=request.risk_contract_name,
        evaluation_frequency=request.evaluation_frequency,
        checkpoint_frequency=request.checkpoint_frequency,
        early_stop_policy=dict(request.early_stop_policy or {}),
        allowed_artifact_policy=request.allowed_artifact_policy,
        observation_columns=observation_columns,
    )

    return PPOV2TrainingConfigurationResult(
        training_configuration=training_configuration,
        configuration_errors=(),
        configuration_metadata=metadata,
        boundary_decision=PASS_DECISION,
    )


def _validate_handoff_result(
    handoff_result: PPOV2TrainingInputHandoffResult | None,
    observation_columns: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []

    if handoff_result is None:
        return ["training_input_handoff_result must be present"]

    if not isinstance(handoff_result, PPOV2TrainingInputHandoffResult):
        return ["training_input_handoff_result must be a PPOV2TrainingInputHandoffResult"]

    if handoff_result.boundary_decision != PASS_DECISION:
        errors.append("training_input_handoff_result boundary_decision must be PASS")

    if tuple(handoff_result.handoff_errors):
        errors.append("training_input_handoff_result must not contain handoff_errors")

    for split_name, split_df in (
        ("train_df", handoff_result.train_df),
        ("eval_df", handoff_result.eval_df),
        ("holdout_df", handoff_result.holdout_df),
    ):
        if not isinstance(split_df, pd.DataFrame) or split_df.empty:
            errors.append(f"{split_name} must be a non-empty DataFrame")

    if not observation_columns:
        errors.append("observation_columns must be non-empty")

    forbidden_columns = set(FORBIDDEN_TRAINING_CONFIGURATION_COLUMNS)
    observed_forbidden_columns = tuple(
        column for column in observation_columns if column in forbidden_columns
    )

    if observed_forbidden_columns:
        errors.append("observation_columns contain forbidden training configuration columns")

    return errors


def _extract_observation_columns(
    handoff_result: PPOV2TrainingInputHandoffResult | None,
) -> tuple[str, ...]:
    if handoff_result is None:
        return ()

    if not hasattr(handoff_result, "observation_columns"):
        return ()

    return tuple(str(column) for column in handoff_result.observation_columns)


def _build_metadata(
    request: PPOV2TrainingConfigurationRequest | None,
    handoff_result: PPOV2TrainingInputHandoffResult | None,
) -> dict[str, Any]:
    return {
        "run_identifier": getattr(request, "run_identifier", None),
        "execution_mode": getattr(request, "execution_mode", None),
        "allowed_execution_modes": ALLOWED_TRAINING_CONFIGURATION_EXECUTION_MODES,
        "allowed_algorithm_families": ALLOWED_PPO_ALGORITHM_FAMILIES,
        "allowed_policy_types": ALLOWED_POLICY_TYPES,
        "allowed_device_preferences": ALLOWED_DEVICE_PREFERENCES,
        "allowed_artifact_policies": ALLOWED_ARTIFACT_POLICIES,
        "training_input_boundary_decision": getattr(handoff_result, "boundary_decision", None),
        "training_authorized": False,
        "training_execution_authorized": False,
        "artifact_creation_authorized": False,
        "data_fetching_authorized": False,
        "dataset_write_authorized": False,
        "paper_order_authorized": False,
        "live_order_authorized": False,
        "controlled_submit_authorized": False,
        "ppo_rf_unblocked": False,
        "ppo_xgboost_unblocked": False,
    }


def _is_not_positive_int(value: object) -> bool:
    return not isinstance(value, int) or value <= 0


def _is_not_positive_number(value: object) -> bool:
    return not isinstance(value, (int, float)) or value <= 0


def _is_negative_number(value: object) -> bool:
    return not isinstance(value, (int, float)) or value < 0


def _is_number_between_zero_and_one(value: object, *, include_one: bool) -> bool:
    if not isinstance(value, (int, float)):
        return False

    if include_one:
        return 0 < float(value) <= 1

    return 0 < float(value) < 1


__all__ = [
    "ALLOWED_ARTIFACT_POLICIES",
    "ALLOWED_DEVICE_PREFERENCES",
    "ALLOWED_POLICY_TYPES",
    "ALLOWED_PPO_ALGORITHM_FAMILIES",
    "ALLOWED_TRAINING_CONFIGURATION_EXECUTION_MODES",
    "FORBIDDEN_TRAINING_CONFIGURATION_COLUMNS",
    "PPOV2TrainingConfiguration",
    "PPOV2TrainingConfigurationRequest",
    "PPOV2TrainingConfigurationResult",
    "build_ppo_v2_training_configuration",
]
