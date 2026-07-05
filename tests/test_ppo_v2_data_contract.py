import pandas as pd
import pytest

from src.ppo_v2_data_contract import (
    FORBIDDEN_HOLDOUT_USES,
    REQUIRED_RAW_COLUMNS,
    PPOV2SplitBoundarySpec,
    measure_missing_bar_coverage,
    validate_holdout_usage,
    validate_observation_columns,
    validate_preprocessing_fit_split,
    validate_raw_data_contract,
    validate_split_boundaries,
)


def _valid_raw_data() -> pd.DataFrame:
    rows = []
    timestamps = pd.date_range("2024-01-02 09:30:00", periods=3, freq="h")

    for symbol in ["AAPL", "AMD"]:
        for index, timestamp in enumerate(timestamps):
            open_price = 100.0 + index
            close_price = 100.5 + index

            rows.append(
                {
                    "Datetime": timestamp,
                    "Symbol": symbol,
                    "Open": open_price,
                    "High": max(open_price, close_price) + 1.0,
                    "Low": min(open_price, close_price) - 1.0,
                    "Close": close_price,
                    "Volume": 1_000 + index,
                }
            )

    return pd.DataFrame(rows)


def test_valid_raw_data_contract_passes():
    data = _valid_raw_data()

    assert validate_raw_data_contract(data) == []


@pytest.mark.parametrize("missing_column", REQUIRED_RAW_COLUMNS)
def test_raw_data_contract_rejects_missing_required_columns(missing_column):
    data = _valid_raw_data().drop(columns=[missing_column])

    errors = validate_raw_data_contract(data)

    assert errors
    assert "missing required raw columns" in errors[0]
    assert missing_column in errors[0]


def test_raw_data_contract_rejects_empty_data():
    data = _valid_raw_data().iloc[0:0]

    errors = validate_raw_data_contract(data)

    assert errors == ["raw data must not be empty"]


def test_raw_data_contract_rejects_invalid_datetime():
    data = _valid_raw_data()
    data["Datetime"] = data["Datetime"].astype("object")
    data.loc[0, "Datetime"] = "not-a-date"

    errors = validate_raw_data_contract(data)

    assert "Datetime must be parseable for every row" in errors


def test_raw_data_contract_rejects_invalid_symbol():
    data = _valid_raw_data()
    data.loc[0, "Symbol"] = "TSLA"

    errors = validate_raw_data_contract(data)

    assert any("symbols outside approved PPO v2 universe" in error for error in errors)
    assert any("TSLA" in error for error in errors)


@pytest.mark.parametrize("column", ["Open", "High", "Low", "Close", "Volume"])
def test_raw_data_contract_rejects_non_numeric_ohlcv(column):
    data = _valid_raw_data()
    data[column] = data[column].astype("object")
    data.loc[0, column] = "bad-value"

    errors = validate_raw_data_contract(data)

    assert f"{column} must be numeric for every row" in errors


@pytest.mark.parametrize("column", ["Open", "High", "Low", "Close", "Volume"])
def test_raw_data_contract_rejects_negative_ohlcv(column):
    data = _valid_raw_data()
    data.loc[0, column] = -1

    errors = validate_raw_data_contract(data)

    assert f"{column} must be non-negative" in errors


def test_raw_data_contract_rejects_high_below_low():
    data = _valid_raw_data()
    data.loc[0, "High"] = data.loc[0, "Low"] - 1

    errors = validate_raw_data_contract(data)

    assert "High must be greater than or equal to Low" in errors


def test_raw_data_contract_rejects_high_below_open():
    data = _valid_raw_data()
    data.loc[0, "High"] = data.loc[0, "Open"] - 1

    errors = validate_raw_data_contract(data)

    assert "High must be greater than or equal to Open" in errors


def test_raw_data_contract_rejects_high_below_close():
    data = _valid_raw_data()
    data.loc[0, "High"] = data.loc[0, "Close"] - 1

    errors = validate_raw_data_contract(data)

    assert "High must be greater than or equal to Close" in errors


def test_raw_data_contract_rejects_low_above_open():
    data = _valid_raw_data()
    data.loc[0, "Low"] = data.loc[0, "Open"] + 1

    errors = validate_raw_data_contract(data)

    assert "Low must be less than or equal to Open" in errors


def test_raw_data_contract_rejects_low_above_close():
    data = _valid_raw_data()
    data.loc[0, "Low"] = data.loc[0, "Close"] + 1

    errors = validate_raw_data_contract(data)

    assert "Low must be less than or equal to Close" in errors


def test_raw_data_contract_rejects_duplicate_symbol_datetime_rows():
    data = pd.concat([_valid_raw_data(), _valid_raw_data().iloc[[0]]], ignore_index=True)

    errors = validate_raw_data_contract(data)

    assert "duplicate Symbol-Datetime rows are not allowed" in errors


def test_raw_data_contract_rejects_unsorted_rows():
    data = _valid_raw_data().iloc[::-1].reset_index(drop=True)

    errors = validate_raw_data_contract(data)

    assert "rows must be sorted by Symbol ascending and Datetime ascending" in errors


def test_missing_bar_coverage_report_measures_symbol_datetime_gap():
    data = _valid_raw_data()
    missing_timestamp = pd.Timestamp("2024-01-02 10:30:00")
    data = data[
        ~((data["Symbol"] == "AAPL") & (data["Datetime"] == missing_timestamp))
    ].reset_index(drop=True)

    report = measure_missing_bar_coverage(data)

    assert report.measurement_method == "per_symbol_1h_timestamp_range"
    assert report.expected_symbol_bar_count == 6
    assert report.observed_symbol_bar_count == 5
    assert report.missing_bar_count == 1
    assert report.missing_bars_by_symbol == {"AAPL": (missing_timestamp,)}


def test_raw_data_contract_reports_missing_symbol_datetime_bar():
    data = _valid_raw_data()
    missing_timestamp = pd.Timestamp("2024-01-02 10:30:00")
    data = data[
        ~((data["Symbol"] == "AAPL") & (data["Datetime"] == missing_timestamp))
    ].reset_index(drop=True)

    errors = validate_raw_data_contract(data)

    assert any("missing 1-hour bars measured and reported" in error for error in errors)
    assert any("missing_bar_count=1" in error for error in errors)
    assert any("expected_symbol_bar_count=6" in error for error in errors)
    assert any("observed_symbol_bar_count=5" in error for error in errors)
    assert any("symbols=AAPL" in error for error in errors)
    assert any("AAPL@2024-01-02T10:30:00" in error for error in errors)


def test_raw_data_contract_reports_all_symbol_missing_hour_inside_range():
    rows = []
    timestamps = [
        pd.Timestamp("2024-01-02 09:30:00"),
        pd.Timestamp("2024-01-02 11:30:00"),
    ]

    for symbol in ["AAPL", "AMD"]:
        for index, timestamp in enumerate(timestamps):
            rows.append(
                {
                    "Datetime": timestamp,
                    "Symbol": symbol,
                    "Open": 100.0 + index,
                    "High": 102.0 + index,
                    "Low": 99.0 + index,
                    "Close": 101.0 + index,
                    "Volume": 1_000 + index,
                }
            )

    data = pd.DataFrame(rows)

    report = measure_missing_bar_coverage(data)
    errors = validate_raw_data_contract(data)

    assert report.expected_symbol_bar_count == 6
    assert report.observed_symbol_bar_count == 4
    assert report.missing_bar_count == 2
    assert report.missing_bars_by_symbol == {
        "AAPL": (pd.Timestamp("2024-01-02 10:30:00"),),
        "AMD": (pd.Timestamp("2024-01-02 10:30:00"),),
    }
    assert any("missing_bar_count=2" in error for error in errors)
    assert any("expected_symbol_bar_count=6" in error for error in errors)
    assert any("observed_symbol_bar_count=4" in error for error in errors)


def test_observation_columns_allow_safe_feature_columns():
    columns = ["lag_return_1", "rolling_volatility_20", "moving_average_distance"]

    assert validate_observation_columns(columns) == []


@pytest.mark.parametrize("forbidden_column", ["Target", "Return", "Datetime", "Symbol"])
def test_observation_columns_reject_forbidden_columns(forbidden_column):
    columns = ["lag_return_1", forbidden_column]

    errors = validate_observation_columns(columns)

    assert errors
    assert "forbidden PPO observation columns present" in errors[0]
    assert forbidden_column in errors[0]


def test_split_boundaries_accept_valid_order_and_embargo():
    spec = PPOV2SplitBoundarySpec(
        train_end="2024-03-01 16:00:00",
        eval_start="2024-03-04 09:30:00",
        eval_end="2024-04-01 16:00:00",
        holdout_start="2024-04-03 09:30:00",
        embargo_window="1 days",
    )

    assert validate_split_boundaries(spec) == []


def test_split_boundaries_reject_train_eval_overlap():
    spec = PPOV2SplitBoundarySpec(
        train_end="2024-03-05 16:00:00",
        eval_start="2024-03-04 09:30:00",
        eval_end="2024-04-01 16:00:00",
        holdout_start="2024-04-03 09:30:00",
        embargo_window="1 days",
    )

    errors = validate_split_boundaries(spec)

    assert "train and eval windows must not overlap" in errors


def test_split_boundaries_reject_eval_holdout_overlap():
    spec = PPOV2SplitBoundarySpec(
        train_end="2024-03-01 16:00:00",
        eval_start="2024-03-04 09:30:00",
        eval_end="2024-04-05 16:00:00",
        holdout_start="2024-04-03 09:30:00",
        embargo_window="1 days",
    )

    errors = validate_split_boundaries(spec)

    assert "eval and holdout windows must not overlap" in errors


def test_split_boundaries_reject_insufficient_embargo():
    spec = PPOV2SplitBoundarySpec(
        train_end="2024-03-01 16:00:00",
        eval_start="2024-03-02 09:30:00",
        eval_end="2024-04-01 16:00:00",
        holdout_start="2024-04-03 09:30:00",
        embargo_window="1 days",
    )

    errors = validate_split_boundaries(spec)

    assert "embargo gap is smaller than required embargo_window" in errors


def test_split_boundaries_reject_non_positive_embargo():
    spec = PPOV2SplitBoundarySpec(
        train_end="2024-03-01 16:00:00",
        eval_start="2024-03-04 09:30:00",
        eval_end="2024-04-01 16:00:00",
        holdout_start="2024-04-03 09:30:00",
        embargo_window="0 days",
    )

    errors = validate_split_boundaries(spec)

    assert "embargo_window must be positive" in errors


def test_holdout_usage_accepts_final_validation_only():
    assert validate_holdout_usage(["final_validation"]) == []


@pytest.mark.parametrize("forbidden_use", FORBIDDEN_HOLDOUT_USES)
def test_holdout_usage_rejects_forbidden_uses(forbidden_use):
    errors = validate_holdout_usage(["final_validation", forbidden_use])

    assert errors
    assert "holdout contains forbidden usage" in errors[0]
    assert forbidden_use in errors[0]


def test_preprocessing_fit_split_accepts_train_df_only():
    assert validate_preprocessing_fit_split("train_df") == []


@pytest.mark.parametrize("invalid_split", ["eval_df", "holdout_df", "full_dataset"])
def test_preprocessing_fit_split_rejects_non_train_fit(invalid_split):
    errors = validate_preprocessing_fit_split(invalid_split)

    assert errors == ["preprocessing must be fit on train_df only"]
