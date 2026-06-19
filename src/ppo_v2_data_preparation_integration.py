"""PPO v2 controlled data-preparation integration scaffold.

v1.79 safety boundary:
- This module coordinates already-loaded in-memory data only.
- It calls the existing PPO v2 data-preparation interface.
- It does not fetch data.
- It does not generate or write datasets.
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

from src.ppo_v2_data_preparation_interface import (
    PPOV2DataPreparationRequest,
    PPOV2DataPreparationResult,
    build_ppo_v2_data_preparation_interface,
)


ALLOWED_INTEGRATION_EXECUTION_MODES: tuple[str, ...] = (
    "dry_run",
    "validation_only",
)


@dataclass(frozen=True)
class PPOV2DataPreparationIntegrationRequest:
    """Integration request for the controlled PPO v2 data-preparation scaffold."""

    data_preparation_request: PPOV2DataPreparationRequest
    run_identifier: str = "ppo_v2_data_preparation_integration"
    execution_mode: str = "validation_only"


@dataclass(frozen=True)
class PPOV2DataPreparationIntegrationResult:
    """Fail-closed result for the PPO v2 data-preparation integration scaffold."""

    data_preparation_result: PPOV2DataPreparationResult | None
    integration_errors: tuple[str, ...]
    integration_metadata: Mapping[str, object]
    boundary_decision: str

    @property
    def errors(self) -> tuple[str, ...]:
        """Return integration errors and downstream data-preparation errors."""

        data_preparation_errors: tuple[str, ...] = ()
        if self.data_preparation_result is not None:
            data_preparation_errors = self.data_preparation_result.errors

        return self.integration_errors + data_preparation_errors

    @property
    def is_valid(self) -> bool:
        """Return True only when integration and data preparation both pass."""

        return (
            self.boundary_decision == "PASS"
            and not self.integration_errors
            and self.data_preparation_result is not None
            and self.data_preparation_result.is_valid
        )


def run_ppo_v2_data_preparation_integration(
    request: PPOV2DataPreparationIntegrationRequest,
) -> PPOV2DataPreparationIntegrationResult:
    """Run the controlled in-memory integration scaffold.

    The integration layer validates its own orchestration boundary first. If the
    integration boundary fails, it does not call the data-preparation interface.

    If the integration boundary passes, it calls the existing v1.76
    data-preparation interface and preserves its fail-closed result.
    """

    integration_errors = tuple(_validate_integration_request(request))

    if integration_errors:
        return PPOV2DataPreparationIntegrationResult(
            data_preparation_result=None,
            integration_errors=integration_errors,
            integration_metadata=_metadata(
                request=request,
                called_data_preparation_interface=False,
                data_preparation_result=None,
            ),
            boundary_decision="REJECTED_FAIL_CLOSED",
        )

    data_preparation_result = build_ppo_v2_data_preparation_interface(
        request.data_preparation_request
    )

    boundary_decision = (
        "PASS"
        if data_preparation_result.is_valid
        else "REJECTED_DATA_PREPARATION_ERRORS"
    )

    return PPOV2DataPreparationIntegrationResult(
        data_preparation_result=data_preparation_result,
        integration_errors=(),
        integration_metadata=_metadata(
            request=request,
            called_data_preparation_interface=True,
            data_preparation_result=data_preparation_result,
        ),
        boundary_decision=boundary_decision,
    )


def _validate_integration_request(
    request: PPOV2DataPreparationIntegrationRequest,
) -> list[str]:
    errors: list[str] = []

    if not request.run_identifier.strip():
        errors.append("run_identifier must be non-empty")

    if request.execution_mode not in ALLOWED_INTEGRATION_EXECUTION_MODES:
        errors.append(
            "execution_mode must be one of: "
            + ", ".join(ALLOWED_INTEGRATION_EXECUTION_MODES)
        )

    return errors


def _metadata(
    *,
    request: PPOV2DataPreparationIntegrationRequest,
    called_data_preparation_interface: bool,
    data_preparation_result: PPOV2DataPreparationResult | None,
) -> Mapping[str, object]:
    data_preparation_is_valid = (
        data_preparation_result.is_valid
        if data_preparation_result is not None
        else False
    )

    data_preparation_error_count = (
        len(data_preparation_result.errors)
        if data_preparation_result is not None
        else 0
    )

    return MappingProxyType(
        {
            "execution_boundary": "non_executing_in_memory_integration_only",
            "run_identifier": request.run_identifier,
            "execution_mode": request.execution_mode,
            "allowed_execution_modes": ALLOWED_INTEGRATION_EXECUTION_MODES,
            "called_data_preparation_interface": called_data_preparation_interface,
            "data_preparation_is_valid": data_preparation_is_valid,
            "data_preparation_error_count": data_preparation_error_count,
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
    "ALLOWED_INTEGRATION_EXECUTION_MODES",
    "PPOV2DataPreparationIntegrationRequest",
    "PPOV2DataPreparationIntegrationResult",
    "run_ppo_v2_data_preparation_integration",
]
