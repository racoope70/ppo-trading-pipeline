import pandas as pd
import pytest

from src.ppo_v2_market_calendar import (
    EXPECTED_13_00_EARLY_CLOSE_SLOTS,
    EXPECTED_FULL_SESSION_SLOTS,
    CalendarContractError,
    expected_slots_for_schedule,
    whole_interval_hour_starts,
)


def test_whole_interval_containment_returns_six_regular_session_slots():
    slots = whole_interval_hour_starts(
        "2023-01-03T14:30:00Z", "2023-01-03T21:00:00Z"
    )
    assert len(slots) == EXPECTED_FULL_SESSION_SLOTS == 6
    assert slots[0] == pd.Timestamp("2023-01-03T15:00:00Z")
    assert slots[-1] == pd.Timestamp("2023-01-03T20:00:00Z")


def test_whole_interval_containment_returns_three_early_close_slots():
    slots = whole_interval_hour_starts(
        "2023-07-03T13:30:00Z", "2023-07-03T17:00:00Z"
    )
    assert len(slots) == EXPECTED_13_00_EARLY_CLOSE_SLOTS == 3
    assert slots == (
        pd.Timestamp("2023-07-03T14:00:00Z"),
        pd.Timestamp("2023-07-03T15:00:00Z"),
        pd.Timestamp("2023-07-03T16:00:00Z"),
    )


def test_empty_non_session_schedule_produces_no_expected_gaps():
    assert expected_slots_for_schedule(pd.DataFrame(columns=["open", "close"])) == ()


def test_schedule_slot_construction_is_deterministic():
    schedule = pd.DataFrame(
        {
            "open": [pd.Timestamp("2023-01-03T14:30:00Z")],
            "close": [pd.Timestamp("2023-01-03T21:00:00Z")],
        },
        index=[pd.Timestamp("2023-01-03")],
    )
    assert expected_slots_for_schedule(schedule) == expected_slots_for_schedule(schedule)


def test_timezone_naive_session_edges_fail_closed():
    with pytest.raises(CalendarContractError):
        whole_interval_hour_starts("2023-01-03 09:30", "2023-01-03 16:00")
