"""PPO v2 training-input handoff scaffold.

v1.82 safety boundary:
- This module accepts already-prepared in-memory outputs only.
- It requires a valid PPO v2 data-preparation integration result.
- It packages train/eval/holdout splits for a future training-configuration layer.
- It does not fetch data.
- It does not write datasets.
- It does not train a model.
- It does not create model artifacts.
- It does not submit paper or live orders.
- It does not authorize controlled submit.
- It does not unblock hybrid deployment.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from src.ppo_v2_data_preparation_integration import (
    PPOV2DataPreparationIntegrationResult,
)


ALLOWED_HANDOFF_EXECUTION_MODES: tuple[str, ...] = (
    "dry_run",
    "validation_only",
)

FORBIDDEN_TRAINING_INPUT_COLUMNS: tuple[str, ...] = (
    "Target",
    "Return",
    "Datetime",
    "Symbol",
)

ALLOWED_HOLDOUT_USES: tuple[str, ...] = ("final_validation",)


@dataclass(frozen=True)
class PPOV2TrainingInputHandoffRequest:
    """Request for the controlled PPO v2 training-input handoff scaffold."""

    data_preparation_integration_result: PPOV2DataPreparationIntegrationResult | None
    run_identifier: str = "ppo_v2_training_input_handoff"
    execution_mode: str = "validation_only"
    requested_holdout_uses: tuple[str, ...] = ALLOWED_HOLDOUT_USES


@dataclass(frozen=True)
class PPOV2TrainingInputHandoffResult:
    """Fail-closed in-memory result for a future PPO v2 training-input boundary."""

    train_df: object | None
    eval_df: object | None
    holdout_df: object | None
    observation_columns: tuple[str, ...]
    handoff_errors: tuple[str, ...]
    handoff_metadata: Mapping[str, object]
    boundary_decision: str

    @property
    def errors(self) -> tuple[str, ...]:
        """Return fail-closed handoff errors."""

        return self.handoff_errors

    @property
    def is_valid(self) -> bool:
        """Return True only when the handoff passed every boundary check."""

        return (
            self.boundary_decision == "PASS"
            and not self.handoff_errors
            and self.train_df is not None
            and self.eval_df is not None
            and self.holdout_df is not None
            and bool(self.observation_columns)
        )


def build_ppo_v2_training_input_handoff(
    request: PPOV2TrainingInputHandoffRequest,
) -> PPOV2TrainingInputHandoffResult:
    """Build a controlled in-memory PPO v2 training-input handoff.

    A valid handoff means the prepared data is shaped for a future training
    configuration layer. It does not authorize training.
    """

    handoff_errors = tuple(_validate_handoff_request(request))

    if handoff_errors:
        return PPOV2TrainingInputHandoffResult(
            train_df=None,
            eval_df=None,
            holdout_df=None,
            observation_columns=(),
            handoff_errors=handoff_errors,
            handoff_metadata=_metadata(request=request, passed=False),
            boundary_decision="REJECTED_FAIL_CLOSED",
        )

    data_preparation_result = (
        request.data_preparation_integration_result.data_preparation_result
    )

    observation_columns = tuple(data_preparation_result.observation_columns)

    return PPOV2TrainingInputHandoffResult(
        train_df=data_preparation_result.train_df,
        eval_df=data_preparation_result.eval_df,
        holdout_df=data_preparation_result.holdout_df,
        observation_columns=observation_columns,
        handoff_errors=(),
        handoff_metadata=_metadata(request=request, passed=True),
        boundary_decision="PASS",
    )


def _validate_handoff_request(
    request: PPOV2TrainingInputHandoffRequest,
) -> list[str]:
    errors: list[str] = []

    if not request.run_identifier.strip():
        errors.append("run_identifier must be non-empty")

    if request.execution_mode not in ALLOWED_HANDOFF_EXECUTION_MODES:
        errors.append(
            "execution_mode must be one of: "
            + ", ".join(ALLOWED_HANDOFF_EXECUTION_MODES)
        )

    forbidden_holdout_uses = tuple(
        use for use in request.requested_holdout_uses if use not in ALLOWED_HOLDOUT_USES
    )
    if forbidden_holdout_uses:
        errors.append(
            "holdout usage is limited to final_validation; forbidden uses: "
            + ", ".join(forbidden_holdout_uses)
        )

    integration_result = request.data_preparation_integration_result
    if integration_result is None:
        errors.append("data_preparation_integration_result must be present")
        return errors

    if not integration_result.is_valid:
        errors.append("data_preparation_integration_result must be valid")

    data_preparation_result = integration_result.data_preparation_result
    if data_preparation_result is None:
        errors.append("data_preparation_result must be present")
        return errors

    if not _has_rows(data_preparation_result.train_df):
        errors.append("train_df must be present and non-empty")

    if not _has_rows(data_preparation_result.eval_df):
        errors.append("eval_df must be present and non-empty")

    if not _has_rows(data_preparation_result.holdout_df):
        errors.append("holdout_df must be present and non-empty")

    observation_columns = tuple(getattr(data_preparation_result, "observation_columns", ()))
    if not observation_columns:
        errors.append("observation_columns must be non-empty")

    forbidden_columns = tuple(
        column
        for column in observation_columns
        if column in FORBIDDEN_TRAINING_INPUT_COLUMNS
    )
    if forbidden_columns:
        errors.append(
            "forbidden training-input columns present: "
            + ", ".join(forbidden_columns)
        )

    return errors


def _has_rows(dataframe: object | None) -> bool:
    if dataframe is None:
        return False

    return not bool(getattr(dataframe, "empty", True))


def _metadata(
    *,
    request: PPOV2TrainingInputHandoffRequest,
    passed: bool,
) -> Mapping[str, object]:
    integration_result = request.data_preparation_integration_result
    integration_result_valid = (
        bool(integration_result.is_valid) if integration_result is not None else False
    )

    return MappingProxyType(
        {
            "execution_boundary": "non_executing_in_memory_training_input_handoff_only",
            "run_identifier": request.run_identifier,
            "execution_mode": request.execution_mode,
            "allowed_execution_modes": ALLOWED_HANDOFF_EXECUTION_MODES,
            "requested_holdout_uses": request.requested_holdout_uses,
            "allowed_holdout_uses": ALLOWED_HOLDOUT_USES,
            "integration_result_valid": integration_result_valid,
            "handoff_passed": passed,
            "training_authorized": False,
            "non_authorizations": (
                "data_fetching",
                "generated_dataset_creation",
                "training_script_creation",
                "actual_retraining_execution",
                "model_artifact_creation",
                "paper_order_submission",
                "live_order_submission",
                "controlled_submit",
                "ppo_rf_deployment",
                "ppo_xgboost_deployment",
            ),
        }
    )


__all__ = [
    "ALLOWED_HANDOFF_EXECUTION_MODES",
    "ALLOWED_HOLDOUT_USES",
    "FORBIDDEN_TRAINING_INPUT_COLUMNS",
    "PPOV2TrainingInputHandoffRequest",
    "PPOV2TrainingInputHandoffResult",
    "build_ppo_v2_training_input_handoff",
]
