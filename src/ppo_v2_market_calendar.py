"""Lazy, deterministic XNYS slot helpers for the governed v3.08 contract."""

from __future__ import annotations

from importlib.metadata import version
from typing import Any

import pandas as pd

from src.ppo_v2_data_contract import CALENDAR_IDENTIFIER, CALENDAR_VERSION

BAR_INTERVAL = pd.Timedelta(hours=1)
EXPECTED_FULL_SESSION_SLOTS = 6
EXPECTED_13_00_EARLY_CLOSE_SLOTS = 3


class CalendarContractError(RuntimeError):
    """Raised when the pinned calendar contract cannot be satisfied."""


def load_xnys_calendar() -> Any:
    """Load pinned XNYS lazily; importing this module does not load a calendar."""

    installed = version("exchange-calendars")
    if installed != CALENDAR_VERSION:
        raise CalendarContractError(
            f"exchange-calendars=={CALENDAR_VERSION} required; found {installed}"
        )
    try:
        import exchange_calendars as xcals
    except ImportError as exc:
        raise CalendarContractError("exchange_calendars is required when XNYS is loaded") from exc
    return xcals.get_calendar(CALENDAR_IDENTIFIER)


def whole_interval_hour_starts(
    session_open: pd.Timestamp | str,
    session_close: pd.Timestamp | str,
) -> tuple[pd.Timestamp, ...]:
    """Return UTC open timestamps whose full hour lies within the session."""

    open_utc = _as_utc(session_open)
    close_utc = _as_utc(session_close)
    if close_utc <= open_utc:
        raise CalendarContractError("session_close must be later than session_open")
    timestamp = open_utc.ceil("h")
    starts: list[pd.Timestamp] = []
    while timestamp + BAR_INTERVAL <= close_utc:
        starts.append(timestamp)
        timestamp += BAR_INTERVAL
    return tuple(starts)


def expected_slots_for_schedule(schedule: pd.DataFrame) -> tuple[pd.Timestamp, ...]:
    """Derive deterministic expected slots; absent sessions produce no gaps."""

    if schedule.empty:
        return ()
    open_column = _find_column(schedule, ("open", "market_open", "session_open"))
    close_column = _find_column(schedule, ("close", "market_close", "session_close"))
    slots: list[pd.Timestamp] = []
    for _, row in schedule.sort_index().iterrows():
        slots.extend(whole_interval_hour_starts(row[open_column], row[close_column]))
    return tuple(slots)


def _as_utc(value: pd.Timestamp | str) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        raise CalendarContractError("session timestamps must be timezone-aware")
    return timestamp.tz_convert("UTC")


def _find_column(frame: pd.DataFrame, candidates: tuple[str, ...]) -> object:
    lookup = {str(column).lower(): column for column in frame.columns}
    for candidate in candidates:
        if candidate in lookup:
            return lookup[candidate]
    raise CalendarContractError(f"schedule lacks required columns; found {list(frame.columns)}")
