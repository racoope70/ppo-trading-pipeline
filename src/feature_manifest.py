"""Safe feature-manifest utilities for PPO training.

This module prevents label/leakage/metadata columns from entering the PPO
observation space or saved model feature lists.

The goal is simple:
- Return and Target are labels/diagnostics, not model inputs.
- Symbol and Datetime are metadata, not numeric PPO inputs.
- Saved feature manifests should contain only safe model features.
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd


FORBIDDEN_FEATURE_COLUMNS = frozenset(
    {
        "Datetime",
        "Date",
        "Timestamp",
        "Symbol",
        "Ticker",
        "Return",
        "Target",
        "Target_Mapped",
        "Label",
        "Labels",
        "Future_Return",
        "Forward_Return",
        "ForwardReturn",
        "Signal",
        "Prediction",
    }
)


def _normalize_column_name(column: str) -> str:
    """Normalize column names for case-insensitive comparison."""
    return str(column).strip().lower()


def normalized_forbidden_columns(
    extra_forbidden: Iterable[str] | None = None,
) -> set[str]:
    """Return normalized forbidden column names."""
    forbidden = set(FORBIDDEN_FEATURE_COLUMNS)

    if extra_forbidden:
        forbidden.update(str(col) for col in extra_forbidden)

    return {_normalize_column_name(col) for col in forbidden}


def is_forbidden_feature_column(
    column: str,
    *,
    extra_forbidden: Iterable[str] | None = None,
) -> bool:
    """Return whether a column is forbidden as a model feature."""
    normalized = _normalize_column_name(column)
    forbidden = normalized_forbidden_columns(extra_forbidden)

    if normalized in forbidden:
        return True

    # Defensive label naming guard.
    if normalized.startswith("target"):
        return True

    # Defensive future-looking naming guard.
    if "future" in normalized and "return" in normalized:
        return True

    if "forward" in normalized and "return" in normalized:
        return True

    return False


def assert_no_forbidden_features(
    feature_columns: Iterable[str],
    *,
    extra_forbidden: Iterable[str] | None = None,
) -> None:
    """Raise if any forbidden columns appear in a feature list."""
    bad_columns = [
        str(col)
        for col in feature_columns
        if is_forbidden_feature_column(col, extra_forbidden=extra_forbidden)
    ]

    if bad_columns:
        raise ValueError(f"Forbidden model feature columns detected: {bad_columns}")


def build_safe_feature_columns(
    df: pd.DataFrame,
    *,
    extra_forbidden: Iterable[str] | None = None,
    include_non_numeric: bool = False,
) -> list[str]:
    """Build an ordered list of safe model feature columns.

    By default this keeps numeric columns only and excludes known labels,
    future-looking diagnostics, and metadata columns.
    """
    if df.empty:
        raise ValueError("Cannot build feature columns from an empty dataframe.")

    feature_columns: list[str] = []

    for column in df.columns:
        if is_forbidden_feature_column(column, extra_forbidden=extra_forbidden):
            continue

        if include_non_numeric:
            feature_columns.append(str(column))
            continue

        if pd.api.types.is_numeric_dtype(df[column]):
            feature_columns.append(str(column))

    if not feature_columns:
        raise ValueError("No safe numeric feature columns were found.")

    assert_no_forbidden_features(
        feature_columns,
        extra_forbidden=extra_forbidden,
    )

    return feature_columns


def build_env_feature_frame(
    df: pd.DataFrame,
    *,
    feature_columns: Iterable[str] | None = None,
    extra_forbidden: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Return a dataframe containing only safe PPO environment features."""
    if df.empty:
        raise ValueError("Cannot build environment feature frame from an empty dataframe.")

    selected_columns = (
        list(feature_columns)
        if feature_columns is not None
        else build_safe_feature_columns(df, extra_forbidden=extra_forbidden)
    )

    assert_no_forbidden_features(
        selected_columns,
        extra_forbidden=extra_forbidden,
    )

    missing = [col for col in selected_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Selected feature columns missing from dataframe: {missing}")

    safe_df = df[selected_columns].copy()

    non_numeric = [
        col
        for col in safe_df.columns
        if not pd.api.types.is_numeric_dtype(safe_df[col])
    ]

    if non_numeric:
        raise ValueError(f"Non-numeric model feature columns detected: {non_numeric}")

    if "Close" not in safe_df.columns:
        raise ValueError("Safe environment feature frame must include Close.")

    return safe_df.reset_index(drop=True)
