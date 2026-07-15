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

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
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

RAW_BAR_FREQUENCY = pd.Timedelta(hours=1)
MISSING_BAR_MEASUREMENT_METHOD = "per_symbol_observed_date_session_1h_range"

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

# v3.08 superseding reconstruction contract. These constants are intentionally
# inert: importing this module performs no network, calendar, or filesystem I/O.
RECONSTRUCTION_CLASSIFICATION = "SUPERSEDING_GOVERNED_ALPACA_ALIGNED_RECONSTRUCTION"
OUTPUT_PATH = Path(
    "data/processed/ppo_v2/"
    "v3_08_superseding_alpaca_aligned_no_submit_training_input.parquet"
)
OLD_MISSING_PATH = Path("data/processed/ppo_v2/v3_07_no_submit_training_input.parquet")
OLD_PATH_AS_OUTPUT_TARGET = "PROHIBITED"
SYMBOLS: tuple[str, ...] = ("AAPL", "AMD", "MRK", "PFE", "UNH", "XOM")
SYMBOL_ORDER = "PRESERVED_AS_LISTED"
RAW_REQUEST_START = "2022-12-01T00:00:00Z"
RAW_REQUEST_END = "2025-06-30T20:00:00Z"
CONTRACT_START = "2023-01-03T14:30:00Z"
CONTRACT_END = "2025-06-30T20:00:00Z"
CANONICAL_DATASET_WINDOW = "[contract_start, contract_end)"
MINIMUM_OBSERVED_WARMUP_BARS_PER_SYMBOL = 50
CALENDAR_LIBRARY = "exchange_calendars"
CALENDAR_IDENTIFIER = "XNYS"
CALENDAR_VERSION = "4.13.2"
SESSION_POLICY = "REGULAR_CORE_SESSION_ONLY"

FINAL_COLUMNS: tuple[str, ...] = (
    "Symbol", "Datetime", "Open", "High", "Low", "Close", "Volume",
    "return_1h", "log_return_1h", "sma_10", "sma_20", "sma_50",
    "ema_12", "ema_26", "rsi_14", "macd", "macd_signal", "macd_hist",
    "atr_14", "realized_volatility_20", "volume_zscore_20",
    "close_to_sma20", "close_to_sma50", "hour_sin", "hour_cos",
    "day_of_week_sin", "day_of_week_cos",
)
ENGINEERED_FEATURE_COLUMNS: tuple[str, ...] = FINAL_COLUMNS[7:]

MISSING_EXPECTED_SLOT_TOLERANCE = 0
CROSS_SYMBOL_ROW_COUNT_MISMATCH_TOLERANCE = 0
SYNTHETIC_BARS = "PROHIBITED"
FORWARD_FILL = "PROHIBITED"
BACKFILL = "PROHIBITED"
INTERPOLATION = "PROHIBITED"
DUPLICATE_SYMBOL_DATETIME = "REJECT"
MISSING_EXPECTED_SLOT = "REPORT_AND_FAIL_CLOSED"
GAP_REASON_CODES: tuple[str, ...] = (
    "OBSERVED", "MISSING_EXPECTED_SLOT", "NON_SESSION",
    "INELIGIBLE_PARTIAL_SESSION_EDGE", "DUPLICATE_SYMBOL_DATETIME",
    "INSUFFICIENT_WARMUP",
)
GAP_EVIDENCE_FIELDS: tuple[str, ...] = (
    "symbol", "session_label", "expected_timestamp_utc",
    "expected_interval_end_utc", "session_open_utc", "session_close_utc",
    "calendar_library", "calendar_version", "calendar_identifier", "timeframe",
    "feed", "adjustment", "raw_request_start", "raw_request_end", "observed",
    "gap_reason_code", "per_symbol_expected_count", "per_symbol_observed_count",
    "per_symbol_missing_count", "total_missing_count",
)


class GovernedContractError(ValueError):
    """Raised when data violates the governed v3.08 contract."""


def validate_output_path(path: str | Path) -> Path:
    """Require the new v3.08 identity and prohibit the missing v3.07 path."""

    candidate = Path(path)
    if candidate == OLD_MISSING_PATH:
        raise GovernedContractError("the missing v3.07 path is prohibited as an output target")
    if candidate != OUTPUT_PATH:
        raise GovernedContractError(f"output path must be {OUTPUT_PATH.as_posix()}")
    return candidate


def validate_reconstructed_frame(data: pd.DataFrame) -> None:
    """Fail closed unless a frame satisfies the exact final dataset contract."""

    if tuple(data.columns) != FINAL_COLUMNS:
        raise GovernedContractError("columns must match the governed 27-column order exactly")
    if data.empty:
        raise GovernedContractError("reconstructed data must not be empty")
    if data.isna().any().any():
        raise GovernedContractError("null or NaN values are prohibited")
    if not isinstance(data["Symbol"].dtype, pd.StringDtype):
        raise GovernedContractError("Symbol must use pandas string dtype")
    symbols = data["Symbol"]
    if not symbols.map(lambda value: isinstance(value, str) and value == value.upper()).all():
        raise GovernedContractError("Symbol values must be non-null uppercase strings")
    datetime_dtype = data["Datetime"].dtype
    if not isinstance(datetime_dtype, pd.DatetimeTZDtype) or str(datetime_dtype.tz) != "UTC":
        raise GovernedContractError("Datetime must be timezone-aware UTC")
    if data.duplicated(["Symbol", "Datetime"]).any():
        raise GovernedContractError("duplicate Symbol/Datetime rows are prohibited")

    for column in OHLCV_COLUMNS + ENGINEERED_FEATURE_COLUMNS:
        if data[column].dtype != np.dtype("float64"):
            raise GovernedContractError(f"{column} must have float64 dtype")
        values = data[column].to_numpy(dtype="float64", copy=False)
        if not np.isfinite(values).all():
            raise GovernedContractError(f"{column} must contain only finite values")
        if column in OHLCV_COLUMNS and (values < 0).any():
            raise GovernedContractError(f"{column} must be nonnegative")

    object_columns = [column for column in data.columns if data[column].dtype == object]
    if object_columns:
        raise GovernedContractError("object dtype is prohibited")


def validate_gap_evidence(record: Mapping[str, object]) -> None:
    """Require complete, controlled gap evidence with zero missing-slot tolerance."""

    missing = [field for field in GAP_EVIDENCE_FIELDS if field not in record]
    if missing:
        raise GovernedContractError("missing gap evidence fields: " + ", ".join(missing))
    if record["gap_reason_code"] not in GAP_REASON_CODES:
        raise GovernedContractError("uncontrolled gap_reason_code")
    if int(record["total_missing_count"]) > MISSING_EXPECTED_SLOT_TOLERANCE:
        raise GovernedContractError("missing expected slots must be reported and fail closed")


@dataclass(frozen=True)
class PPOV2MissingBarCoverageReport:
    """Measured missing-bar coverage for the static raw-data contract."""

    expected_symbol_bar_count: int
    observed_symbol_bar_count: int
    missing_bar_count: int
    missing_bars_by_symbol: Mapping[str, tuple[pd.Timestamp, ...]]
    measurement_method: str = MISSING_BAR_MEASUREMENT_METHOD


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

    missing_bar_report = _measure_missing_bar_coverage(data, parsed_datetime)
    if missing_bar_report.missing_bar_count:
        errors.append(_format_missing_bar_coverage_error(missing_bar_report))

    return errors


def measure_missing_bar_coverage(data: pd.DataFrame) -> PPOV2MissingBarCoverageReport:
    """Measure missing bars within observed symbol/date sessions only.

    The measurement is intentionally scoped to each symbol's observed intraday
    date/session range. It does not infer overnight, weekend, cross-date, or
    full market open-to-close coverage unless a separate session calendar or
    reviewed coverage manifest defines those expected bounds.
    """

    if "Datetime" not in data.columns or "Symbol" not in data.columns or data.empty:
        return PPOV2MissingBarCoverageReport(
            expected_symbol_bar_count=0,
            observed_symbol_bar_count=0,
            missing_bar_count=0,
            missing_bars_by_symbol={},
        )

    parsed_datetime = pd.to_datetime(data["Datetime"], errors="coerce", format="mixed")
    return _measure_missing_bar_coverage(data, parsed_datetime)


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
            f"forbidden PPO observation columns present: {', '.join(forbidden_present)}"
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


def _measure_missing_bar_coverage(
    data: pd.DataFrame,
    parsed_datetime: pd.Series,
) -> PPOV2MissingBarCoverageReport:
    coverage_frame = pd.DataFrame(
        {
            "Symbol": data["Symbol"],
            "Datetime": parsed_datetime,
        }
    ).dropna(subset=["Symbol", "Datetime"])

    if coverage_frame.empty:
        return PPOV2MissingBarCoverageReport(
            expected_symbol_bar_count=0,
            observed_symbol_bar_count=0,
            missing_bar_count=0,
            missing_bars_by_symbol={},
        )

    coverage_frame = coverage_frame.assign(
        Symbol=coverage_frame["Symbol"].astype(str),
        Datetime=pd.to_datetime(coverage_frame["Datetime"], errors="coerce"),
    ).dropna(subset=["Datetime"])

    missing_bars_by_symbol: dict[str, tuple[pd.Timestamp, ...]] = {}
    expected_symbol_bar_count = 0
    observed_symbol_bar_count = 0

    coverage_frame = coverage_frame.assign(
        _ObservedDate=coverage_frame["Datetime"].dt.date,
    )

    for symbol in sorted(coverage_frame["Symbol"].drop_duplicates()):
        symbol_frame = coverage_frame.loc[coverage_frame["Symbol"] == symbol]

        for observed_date in sorted(symbol_frame["_ObservedDate"].drop_duplicates()):
            session_timestamps = tuple(
                sorted(
                    pd.Timestamp(timestamp)
                    for timestamp in symbol_frame.loc[
                        symbol_frame["_ObservedDate"] == observed_date,
                        "Datetime",
                    ].drop_duplicates()
                )
            )

            if not session_timestamps:
                continue

            observed_timestamp_set = set(session_timestamps)
            expected_timestamps = tuple(
                pd.date_range(
                    start=session_timestamps[0],
                    end=session_timestamps[-1],
                    freq=RAW_BAR_FREQUENCY,
                )
            )
            expected_timestamp_set = set(
                pd.Timestamp(timestamp) for timestamp in expected_timestamps
            )

            observed_symbol_bar_count += len(observed_timestamp_set)
            expected_symbol_bar_count += len(expected_timestamp_set)

            missing_timestamps = tuple(
                sorted(expected_timestamp_set.difference(observed_timestamp_set))
            )
            if missing_timestamps:
                existing = missing_bars_by_symbol.get(symbol, ())
                missing_bars_by_symbol[symbol] = existing + missing_timestamps

    missing_bar_count = sum(len(timestamps) for timestamps in missing_bars_by_symbol.values())

    return PPOV2MissingBarCoverageReport(
        expected_symbol_bar_count=expected_symbol_bar_count,
        observed_symbol_bar_count=observed_symbol_bar_count,
        missing_bar_count=missing_bar_count,
        missing_bars_by_symbol=missing_bars_by_symbol,
    )

def _format_missing_bar_coverage_error(
    report: PPOV2MissingBarCoverageReport,
) -> str:
    affected_symbols = ", ".join(report.missing_bars_by_symbol)
    examples: list[str] = []

    for symbol, timestamps in report.missing_bars_by_symbol.items():
        for timestamp in timestamps:
            examples.append(f"{symbol}@{pd.Timestamp(timestamp).isoformat()}")
            if len(examples) == 3:
                break
        if len(examples) == 3:
            break

    return (
        "missing 1-hour bars measured and reported: "
        f"missing_bar_count={report.missing_bar_count}; "
        f"expected_symbol_bar_count={report.expected_symbol_bar_count}; "
        f"observed_symbol_bar_count={report.observed_symbol_bar_count}; "
        f"measurement_method={report.measurement_method}; "
        f"symbols={affected_symbols}; "
        "examples=" + ", ".join(examples)
    )


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
