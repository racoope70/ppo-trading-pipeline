"""PPO v2 data-contract validation utilities.

v1.73 safety boundary:
- This module validates raw data-contract and split-specification rules only.
- It does not fetch data.
- It does not generate datasets.
- It does not train a model.
- It does not create model artifacts.
- It does not submit paper or live orders.
- It does not unblock PPO + RF or PPO + XGBoost.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

import pandas as pd

from src.ppo_v2_retraining_config import (
    CANONICAL_PPO_V2_SYMBOLS,
    FORBIDDEN_MODEL_INPUT_COLUMNS,
)


REQUIRED_RAW_COLUMNS: tuple[str, ...] = (
    "Datetime",
    "Symbol",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
)

OPTIONAL_RAW_COLUMNS: tuple[str, ...] = (
    "TradeCount",
    "VWAP",
)

OHLCV_COLUMNS: tuple[str, ...] = (
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
)

FORBIDDEN_HOLDOUT_USES: tuple[str, ...] = (
    "feature_selection",
    "hyperparameter_tuning",
    "reward_tuning",
    "threshold_tuning",
    "model_selection",
    "early_stopping",
    "normalization_fitting",
    "regime_fitting",
    "scaler_fitting",
    "manual_iteration",
)


@dataclass(frozen=True)
class PPOV2SplitBoundarySpec:
    """Time-ordered split boundary specification for future PPO v2 retraining."""

    train_end: pd.Timestamp | str
    eval_start: pd.Timestamp | str
    eval_end: pd.Timestamp | str
    holdout_start: pd.Timestamp | str
    embargo_window: pd.Timedelta | str


def validate_raw_data_contract(
    data: pd.DataFrame,
    *,
    approved_symbols: Sequence[str] = CANONICAL_PPO_V2_SYMBOLS,
    required_columns: Sequence[str] = REQUIRED_RAW_COLUMNS,
) -> list[str]:
    """Validate the v1.72 PPO v2 raw-data contract without fetching data."""

    errors: list[str] = []

    missing_columns = [column for column in required_columns if column not in data.columns]
    if missing_columns:
        errors.append(
            "missing required raw columns: " + ", ".join(sorted(missing_columns))
        )
        return errors

    if data.empty:
        errors.append("raw data must not be empty")
        return errors

    parsed_datetime = pd.to_datetime(data["Datetime"], errors="coerce", format="mixed")
    if parsed_datetime.isna().any():
        errors.append("Datetime must be parseable for every row")

    if data["Symbol"].isna().any():
        errors.append("Symbol must be non-null for every row")

    observed_symbols = set(data["Symbol"].dropna().astype(str))
    invalid_symbols = sorted(observed_symbols.difference(set(approved_symbols)))
    if invalid_symbols:
        errors.append(
            "symbols outside approved PPO v2 universe: " + ", ".join(invalid_symbols)
        )

    numeric_columns: dict[str, pd.Series] = {}
    for column in OHLCV_COLUMNS:
        numeric_values = pd.to_numeric(data[column], errors="coerce")
        numeric_columns[column] = numeric_values

        if numeric_values.isna().any():
            errors.append(f"{column} must be numeric for every row")

        if (numeric_values < 0).any():
            errors.append(f"{column} must be non-negative")

    high = numeric_columns["High"]
    low = numeric_columns["Low"]
    open_ = numeric_columns["Open"]
    close = numeric_columns["Close"]

    if (high < low).any():
        errors.append("High must be greater than or equal to Low")

    if (high < open_).any():
        errors.append("High must be greater than or equal to Open")

    if (high < close).any():
        errors.append("High must be greater than or equal to Close")

    if (low > open_).any():
        errors.append("Low must be less than or equal to Open")

    if (low > close).any():
        errors.append("Low must be less than or equal to Close")

    duplicate_mask = data.assign(_ParsedDatetime=parsed_datetime).duplicated(
        ["Symbol", "_ParsedDatetime"]
    )
    if duplicate_mask.any():
        errors.append("duplicate Symbol-Datetime rows are not allowed")

    if not _is_sorted_by_symbol_then_datetime(data, parsed_datetime):
        errors.append("rows must be sorted by Symbol ascending and Datetime ascending")

    return errors


def validate_observation_columns(
    observation_columns: Iterable[str],
    *,
    forbidden_columns: Sequence[str] = FORBIDDEN_MODEL_INPUT_COLUMNS,
) -> list[str]:
    """Validate that forbidden audit/index/target columns are excluded from inputs."""

    columns = set(observation_columns)
    forbidden_present = sorted(columns.intersection(set(forbidden_columns)))

    if forbidden_present:
        return [
            "forbidden PPO observation columns present: "
            + ", ".join(forbidden_present)
        ]

    return []


def validate_split_boundaries(spec: PPOV2SplitBoundarySpec) -> list[str]:
    """Validate time-ordered split boundaries and required embargo."""

    errors: list[str] = []

    train_end = pd.Timestamp(spec.train_end)
    eval_start = pd.Timestamp(spec.eval_start)
    eval_end = pd.Timestamp(spec.eval_end)
    holdout_start = pd.Timestamp(spec.holdout_start)
    embargo_window = pd.Timedelta(spec.embargo_window)

    if embargo_window <= pd.Timedelta(0):
        errors.append("embargo_window must be positive")

    if train_end >= eval_start:
        errors.append("train and eval windows must not overlap")

    if eval_end >= holdout_start:
        errors.append("eval and holdout windows must not overlap")

    actual_embargo = eval_start - train_end
    if actual_embargo < embargo_window:
        errors.append("embargo gap is smaller than required embargo_window")

    return errors


def validate_holdout_usage(holdout_uses: Iterable[str]) -> list[str]:
    """Validate that holdout is final-validation only."""

    uses = set(holdout_uses)
    forbidden_uses = sorted(uses.intersection(set(FORBIDDEN_HOLDOUT_USES)))

    if forbidden_uses:
        return ["holdout contains forbidden usage: " + ", ".join(forbidden_uses)]

    return []


def validate_preprocessing_fit_split(preprocessing_fit_split: str) -> list[str]:
    """Validate that preprocessing is fit on train_df only."""

    if preprocessing_fit_split != "train_df":
        return ["preprocessing must be fit on train_df only"]

    return []


def _is_sorted_by_symbol_then_datetime(
    data: pd.DataFrame,
    parsed_datetime: pd.Series,
) -> bool:
    if parsed_datetime.isna().any():
        return False

    sortable = pd.DataFrame(
        {
            "Symbol": data["Symbol"].astype(str).to_numpy(),
            "Datetime": parsed_datetime.to_numpy(),
        }
    )

    observed = list(sortable.itertuples(index=False, name=None))
    expected = sorted(observed, key=lambda row: (row[0], row[1]))

    return observed == expected
