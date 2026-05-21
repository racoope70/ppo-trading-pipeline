import pandas as pd
import pytest

from src.feature_manifest import (
    assert_no_forbidden_features,
    build_env_feature_frame,
    build_safe_feature_columns,
    is_forbidden_feature_column,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Datetime": pd.date_range("2026-01-01", periods=3, tz="UTC"),
            "Symbol": ["AAPL", "AAPL", "AAPL"],
            "Open": [100.0, 101.0, 102.0],
            "High": [101.0, 102.0, 103.0],
            "Low": [99.0, 100.0, 101.0],
            "Close": [100.5, 101.5, 102.5],
            "Volume": [1000, 1100, 1200],
            "RSI": [50.0, 55.0, 60.0],
            "Return": [0.01, -0.02, 0.03],
            "Target": [1, -1, 0],
            "Target_Mapped": [2, 0, 1],
        }
    )


def test_is_forbidden_feature_column_detects_labels_and_metadata():
    assert is_forbidden_feature_column("Return") is True
    assert is_forbidden_feature_column("Target") is True
    assert is_forbidden_feature_column("Target_Mapped") is True
    assert is_forbidden_feature_column("Symbol") is True
    assert is_forbidden_feature_column("Datetime") is True
    assert is_forbidden_feature_column("Future_Return_5") is True


def test_build_safe_feature_columns_excludes_forbidden_columns():
    features = build_safe_feature_columns(_sample_df())

    assert "Open" in features
    assert "High" in features
    assert "Low" in features
    assert "Close" in features
    assert "Volume" in features
    assert "RSI" in features

    assert "Return" not in features
    assert "Target" not in features
    assert "Target_Mapped" not in features
    assert "Symbol" not in features
    assert "Datetime" not in features


def test_build_safe_feature_columns_preserves_order():
    features = build_safe_feature_columns(_sample_df())

    assert features[:6] == ["Open", "High", "Low", "Close", "Volume", "RSI"]


def test_assert_no_forbidden_features_raises_on_bad_columns():
    with pytest.raises(ValueError, match="Forbidden model feature columns"):
        assert_no_forbidden_features(["Open", "Close", "Return", "Target"])


def test_build_env_feature_frame_returns_safe_numeric_frame():
    env_df = build_env_feature_frame(_sample_df())

    assert "Close" in env_df.columns
    assert "Return" not in env_df.columns
    assert "Target" not in env_df.columns
    assert "Symbol" not in env_df.columns
    assert "Datetime" not in env_df.columns
    assert len(env_df) == 3


def test_build_env_feature_frame_rejects_explicit_forbidden_feature():
    with pytest.raises(ValueError, match="Forbidden model feature columns"):
        build_env_feature_frame(
            _sample_df(),
            feature_columns=["Open", "Close", "Return"],
        )


def test_build_env_feature_frame_rejects_missing_feature():
    with pytest.raises(ValueError, match="missing"):
        build_env_feature_frame(
            _sample_df(),
            feature_columns=["Open", "Close", "DoesNotExist"],
        )


def test_build_env_feature_frame_requires_close():
    with pytest.raises(ValueError, match="must include Close"):
        build_env_feature_frame(
            _sample_df(),
            feature_columns=["Open", "High", "Low", "Volume"],
        )


def test_build_safe_feature_columns_rejects_empty_dataframe():
    with pytest.raises(ValueError, match="empty"):
        build_safe_feature_columns(pd.DataFrame())
