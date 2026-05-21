import pandas as pd
import pytest

from src.training_splits import split_train_eval_window


def _sample_window(rows: int = 100) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Datetime": pd.date_range(
                "2026-01-01 09:30",
                periods=rows,
                freq="h",
                tz="UTC",
            ),
            "Close": range(rows),
            "Symbol": ["AAPL"] * rows,
        }
    )


def test_split_train_eval_window_creates_non_overlapping_slices():
    df = _sample_window(100)

    split = split_train_eval_window(
        df,
        train_fraction=0.80,
        min_train_rows=10,
        min_eval_rows=10,
    )

    assert split.train_rows == 80
    assert split.eval_rows == 20
    assert split.train_end < split.eval_start
    assert split.train_df["Datetime"].max() < split.eval_df["Datetime"].min()


def test_split_train_eval_window_sorts_by_datetime():
    df = _sample_window(100).sample(frac=1.0, random_state=42).reset_index(drop=True)

    split = split_train_eval_window(
        df,
        train_fraction=0.75,
        min_train_rows=10,
        min_eval_rows=10,
    )

    assert split.train_df["Datetime"].is_monotonic_increasing
    assert split.eval_df["Datetime"].is_monotonic_increasing
    assert split.train_end < split.eval_start


def test_split_train_eval_window_rejects_empty_dataframe():
    with pytest.raises(ValueError, match="empty"):
        split_train_eval_window(pd.DataFrame())


def test_split_train_eval_window_rejects_missing_datetime():
    df = pd.DataFrame({"Close": [1, 2, 3]})

    with pytest.raises(ValueError, match="Datetime"):
        split_train_eval_window(df)


def test_split_train_eval_window_rejects_bad_train_fraction():
    df = _sample_window(100)

    with pytest.raises(ValueError, match="train_fraction"):
        split_train_eval_window(df, train_fraction=1.0)


def test_split_train_eval_window_rejects_too_few_train_rows():
    df = _sample_window(100)

    with pytest.raises(ValueError, match="Training slice too small"):
        split_train_eval_window(
            df,
            train_fraction=0.20,
            min_train_rows=50,
            min_eval_rows=10,
        )


def test_split_train_eval_window_rejects_too_few_eval_rows():
    df = _sample_window(100)

    with pytest.raises(ValueError, match="Evaluation slice too small"):
        split_train_eval_window(
            df,
            train_fraction=0.95,
            min_train_rows=10,
            min_eval_rows=10,
        )


def test_split_train_eval_window_preserves_total_row_count():
    df = _sample_window(123)

    split = split_train_eval_window(
        df,
        train_fraction=0.80,
        min_train_rows=10,
        min_eval_rows=10,
    )

    assert split.total_rows == 123
    assert split.train_rows + split.eval_rows == 123
