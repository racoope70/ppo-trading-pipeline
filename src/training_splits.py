"""Train/evaluation split helpers for walk-forward PPO windows.

This module prevents evaluating a PPO model on the same rows used for training.
Each walk-forward window is split into:

- train_df: earlier rows used for PPO fitting
- eval_df: later rows used only for out-of-sample evaluation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class TrainEvalSplit:
    """Container for a single train/evaluation split."""

    train_df: pd.DataFrame
    eval_df: pd.DataFrame
    split_index: int
    total_rows: int
    train_rows: int
    eval_rows: int
    train_start: Any
    train_end: Any
    eval_start: Any
    eval_end: Any


def split_train_eval_window(
    df_window: pd.DataFrame,
    *,
    train_fraction: float = 0.80,
    min_train_rows: int = 60,
    min_eval_rows: int = 60,
    datetime_col: str = "Datetime",
    sort_by_datetime: bool = True,
) -> TrainEvalSplit:
    """Split one walk-forward window into train and evaluation slices.

    Parameters
    ----------
    df_window:
        One rolling walk-forward window.

    train_fraction:
        Fraction of rows used for training. The remaining later rows are used
        only for evaluation.

    min_train_rows:
        Minimum rows required in the training slice.

    min_eval_rows:
        Minimum rows required in the evaluation slice.

    datetime_col:
        Timestamp column used to verify non-overlap.

    sort_by_datetime:
        Whether to sort rows by datetime before splitting.

    Returns
    -------
    TrainEvalSplit
        Non-overlapping train/evaluation slices.

    Raises
    ------
    ValueError
        If the window cannot produce a valid split.
    """
    if df_window.empty:
        raise ValueError("df_window is empty.")

    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1.")

    if min_train_rows <= 0:
        raise ValueError("min_train_rows must be positive.")

    if min_eval_rows <= 0:
        raise ValueError("min_eval_rows must be positive.")

    if datetime_col not in df_window.columns:
        raise ValueError(f"df_window must contain {datetime_col!r}.")

    data = df_window.copy()

    data[datetime_col] = pd.to_datetime(data[datetime_col], utc=True)

    if sort_by_datetime:
        data = data.sort_values(datetime_col).reset_index(drop=True)
    else:
        data = data.reset_index(drop=True)

    total_rows = int(len(data))
    split_index = int(total_rows * train_fraction)

    train_rows = split_index
    eval_rows = total_rows - split_index

    if train_rows < min_train_rows:
        raise ValueError(
            f"Training slice too small: train_rows={train_rows}, "
            f"min_train_rows={min_train_rows}."
        )

    if eval_rows < min_eval_rows:
        raise ValueError(
            f"Evaluation slice too small: eval_rows={eval_rows}, "
            f"min_eval_rows={min_eval_rows}."
        )

    train_df = data.iloc[:split_index].reset_index(drop=True)
    eval_df = data.iloc[split_index:].reset_index(drop=True)

    train_start = train_df[datetime_col].iloc[0]
    train_end = train_df[datetime_col].iloc[-1]
    eval_start = eval_df[datetime_col].iloc[0]
    eval_end = eval_df[datetime_col].iloc[-1]

    if not train_end < eval_start:
        raise ValueError(
            "Train/evaluation split overlaps or is not strictly time ordered: "
            f"train_end={train_end}, eval_start={eval_start}."
        )

    return TrainEvalSplit(
        train_df=train_df,
        eval_df=eval_df,
        split_index=split_index,
        total_rows=total_rows,
        train_rows=int(len(train_df)),
        eval_rows=int(len(eval_df)),
        train_start=train_start,
        train_end=train_end,
        eval_start=eval_start,
        eval_end=eval_end,
    )
