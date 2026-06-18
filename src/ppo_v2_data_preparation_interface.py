"""PPO v2 controlled data-preparation interface scaffold.

v1.76 safety boundary:
- This module prepares already-loaded in-memory data only.
- It does not fetch data.
- It does not generate or write datasets.
- It does not train a model.
- It does not load PPO models.
- It does not create model artifacts.
- It does not submit paper or live orders.
- It does not authorize controlled submit.
- It does not unblock PPO + RF or PPO + XGBoost.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

import pandas as pd

from src.ppo_v2_data_contract import (
    PPOV2SplitBoundarySpec,
    REQUIRED_RAW_COLUMNS,
    validate_holdout_usage,
    validate_observation_columns,
    validate_preprocessing_fit_split,
    validate_raw_data_contract,
    validate_split_boundaries,
)
from src.ppo_v2_retraining_config import CANONICAL_PPO_V2_SYMBOLS


@dataclass(frozen=True)
class PPOV2DataPreparationRequest:
    """In-memory request for the controlled PPO v2 data-preparation scaffold."""

    raw_df: pd.DataFrame
    split_boundary_spec: PPOV2SplitBoundarySpec
    observation_columns: Sequence[str]
    holdout_uses: Sequence[str] = ("final_validation",)
    preprocessing_fit_split: str = "train_df"
    approved_symbols: Sequence[str] = CANONICAL_PPO_V2_SYMBOLS
    required_raw_columns: Sequence[str] = REQUIRED_RAW_COLUMNS


@dataclass(frozen=True)
class PPOV2DataPreparationResult:
    """Fail-closed output for the controlled PPO v2 data-preparation scaffold."""

    train_df: pd.DataFrame
    eval_df: pd.DataFrame
    holdout_df: pd.DataFrame
    observation_columns: tuple[str, ...]
    data_contract_errors: tuple[str, ...]
    observation_column_errors: tuple[str, ...]
    split_boundary_errors: tuple[str, ...]
    holdout_policy_errors: tuple[str, ...]
    preprocessing_boundary_errors: tuple[str, ...]
    validation_metadata: Mapping[str, object]

    @property
    def errors(self) -> tuple[str, ...]:
        """Return every validation error from the scaffold."""

        return (
            self.data_contract_errors
            + self.observation_column_errors
            + self.split_boundary_errors
            + self.holdout_policy_errors
            + self.preprocessing_boundary_errors
        )

    @property
    def is_valid(self) -> bool:
        """Return True only when the scaffold produced valid split outputs."""

        return len(self.errors) == 0


def build_ppo_v2_data_preparation_interface(
    request: PPOV2DataPreparationRequest,
) -> PPOV2DataPreparationResult:
    """Build split-specific PPO v2 dataframes from already-loaded in-memory data.

    This function is intentionally deterministic and fail-closed. It validates the
    raw data contract, observation-column boundary, split boundary, holdout usage,
    and preprocessing-fit boundary before returning split dataframes.

    It does not fetch, persist, train, create artifacts, or submit orders.
    """

    raw_df = request.raw_df.copy()

    data_contract_errors = tuple(
        validate_raw_data_contract(
            raw_df,
            approved_symbols=request.approved_symbols,
            required_columns=request.required_raw_columns,
        )
    )

    observation_column_errors = tuple(
        validate_observation_columns(request.observation_columns)
        + _validate_observation_columns_exist(raw_df, request.observation_columns)
    )

    split_boundary_errors = tuple(validate_split_boundaries(request.split_boundary_spec))
    holdout_policy_errors = tuple(validate_holdout_usage(request.holdout_uses))
    preprocessing_boundary_errors = tuple(
        validate_preprocessing_fit_split(request.preprocessing_fit_split)
    )

    all_errors = (
        data_contract_errors
        + observation_column_errors
        + split_boundary_errors
        + holdout_policy_errors
        + preprocessing_boundary_errors
    )

    if all_errors:
        return PPOV2DataPreparationResult(
            train_df=_empty_like(raw_df),
            eval_df=_empty_like(raw_df),
            holdout_df=_empty_like(raw_df),
            observation_columns=tuple(request.observation_columns),
            data_contract_errors=data_contract_errors,
            observation_column_errors=observation_column_errors,
            split_boundary_errors=split_boundary_errors,
            holdout_policy_errors=holdout_policy_errors,
            preprocessing_boundary_errors=preprocessing_boundary_errors,
            validation_metadata=_metadata(
                raw_df=raw_df,
                train_df=_empty_like(raw_df),
                eval_df=_empty_like(raw_df),
                holdout_df=_empty_like(raw_df),
                request=request,
                error_count=len(all_errors),
                excluded_row_count=0,
            ),
        )

    prepared_df = raw_df.assign(
        _PPOV2ParsedDatetime=pd.to_datetime(
            raw_df["Datetime"],
            errors="coerce",
            format="mixed",
        )
    )

    train_end = pd.Timestamp(request.split_boundary_spec.train_end)
    eval_start = pd.Timestamp(request.split_boundary_spec.eval_start)
    eval_end = pd.Timestamp(request.split_boundary_spec.eval_end)
    holdout_start = pd.Timestamp(request.split_boundary_spec.holdout_start)

    train_df = _drop_internal_columns(
        prepared_df.loc[prepared_df["_PPOV2ParsedDatetime"] <= train_end]
    )
    eval_df = _drop_internal_columns(
        prepared_df.loc[
            (prepared_df["_PPOV2ParsedDatetime"] >= eval_start)
            & (prepared_df["_PPOV2ParsedDatetime"] <= eval_end)
        ]
    )
    holdout_df = _drop_internal_columns(
        prepared_df.loc[prepared_df["_PPOV2ParsedDatetime"] >= holdout_start]
    )

    assigned_row_count = len(train_df) + len(eval_df) + len(holdout_df)
    excluded_row_count = len(raw_df) - assigned_row_count

    return PPOV2DataPreparationResult(
        train_df=train_df,
        eval_df=eval_df,
        holdout_df=holdout_df,
        observation_columns=tuple(request.observation_columns),
        data_contract_errors=data_contract_errors,
        observation_column_errors=observation_column_errors,
        split_boundary_errors=split_boundary_errors,
        holdout_policy_errors=holdout_policy_errors,
        preprocessing_boundary_errors=preprocessing_boundary_errors,
        validation_metadata=_metadata(
            raw_df=raw_df,
            train_df=train_df,
            eval_df=eval_df,
            holdout_df=holdout_df,
            request=request,
            error_count=0,
            excluded_row_count=excluded_row_count,
        ),
    )


def _validate_observation_columns_exist(
    raw_df: pd.DataFrame,
    observation_columns: Sequence[str],
) -> list[str]:
    missing_observation_columns = [
        column for column in observation_columns if column not in raw_df.columns
    ]

    if missing_observation_columns:
        return [
            "observation columns missing from raw data: "
            + ", ".join(sorted(missing_observation_columns))
        ]

    return []


def _empty_like(raw_df: pd.DataFrame) -> pd.DataFrame:
    return raw_df.iloc[0:0].copy()


def _drop_internal_columns(data: pd.DataFrame) -> pd.DataFrame:
    return data.drop(columns=["_PPOV2ParsedDatetime"]).copy()


def _metadata(
    *,
    raw_df: pd.DataFrame,
    train_df: pd.DataFrame,
    eval_df: pd.DataFrame,
    holdout_df: pd.DataFrame,
    request: PPOV2DataPreparationRequest,
    error_count: int,
    excluded_row_count: int,
) -> Mapping[str, object]:
    return MappingProxyType(
        {
            "execution_boundary": "non_executing_in_memory_only",
            "raw_rows": len(raw_df),
            "train_rows": len(train_df),
            "eval_rows": len(eval_df),
            "holdout_rows": len(holdout_df),
            "excluded_rows": excluded_row_count,
            "observation_column_count": len(tuple(request.observation_columns)),
            "error_count": error_count,
            "approved_symbols": tuple(request.approved_symbols),
            "preprocessing_fit_split": request.preprocessing_fit_split,
            "holdout_uses": tuple(request.holdout_uses),
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
    "PPOV2DataPreparationRequest",
    "PPOV2DataPreparationResult",
    "build_ppo_v2_data_preparation_interface",
]
