"""Inert v3.08 reconstruction scaffolding; no fetch or write occurs by default."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.ppo_v2_data_contract import RAW_REQUEST_END, RAW_REQUEST_START, SYMBOLS

SOURCE_CLIENT = "alpaca.data.historical.StockHistoricalDataClient"
REQUEST_CLASS = "alpaca.data.requests.StockBarsRequest"
RETRIEVAL_METHOD = "StockHistoricalDataClient.get_stock_bars"
TIMEFRAME = "TimeFrame.Hour"
FEED = "DataFeed.IEX"
ADJUSTMENT = "Adjustment.RAW"
SORT = "Sort.ASC"
LIMIT = None
CURRENCY = None
ASOF = None
REQUEST_DATETIMES = "TIMEZONE_AWARE_UTC"


class ReconstructionAuthorizationError(RuntimeError):
    """Raised when a later governed action has not been authorized."""


class AlpacaDependencyError(RuntimeError):
    """Raised when request construction needs an unavailable Alpaca SDK."""


@dataclass(frozen=True)
class AlpacaRequestContract:
    symbols: tuple[str, ...] = SYMBOLS
    start: str = RAW_REQUEST_START
    end: str = RAW_REQUEST_END
    timeframe: str = TIMEFRAME
    feed: str = FEED
    adjustment: str = ADJUSTMENT
    sort: str = SORT
    limit: None = LIMIT
    currency: None = CURRENCY
    asof: None = ASOF


def describe_contract() -> dict[str, object]:
    """Return literals without importing Alpaca, loading XNYS, or writing files."""

    return {
        "source_client": SOURCE_CLIENT,
        "request_class": REQUEST_CLASS,
        "retrieval_method": RETRIEVAL_METHOD,
        "symbols": list(SYMBOLS),
        "raw_request_start": RAW_REQUEST_START,
        "raw_request_end": RAW_REQUEST_END,
        "timeframe": TIMEFRAME,
        "feed": FEED,
        "adjustment": ADJUSTMENT,
        "sort": SORT,
        "limit": LIMIT,
        "currency": CURRENCY,
        "asof": ASOF,
        "request_datetimes": REQUEST_DATETIMES,
    }


def construct_stock_bars_request() -> Any:
    """Construct, but never execute, the governed Alpaca request."""

    try:
        from alpaca.data.enums import Adjustment, DataFeed
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame
        from alpaca.common.enums import Sort
    except ImportError as exc:
        raise AlpacaDependencyError("alpaca-py is required to construct the governed request") from exc

    return StockBarsRequest(
        symbol_or_symbols=list(SYMBOLS),
        timeframe=TimeFrame.Hour,
        start=_utc_datetime(RAW_REQUEST_START),
        end=_utc_datetime(RAW_REQUEST_END),
        limit=None,
        adjustment=Adjustment.RAW,
        feed=DataFeed.IEX,
        sort=Sort.ASC,
        asof=None,
        currency=None,
    )


def fetch_market_data(*_: object, **__: object) -> None:
    """Fail closed until a separate data-fetch checkpoint authorizes execution."""

    raise ReconstructionAuthorizationError("market-data fetching is not authorized")


def generate_dataset(*_: object, **__: object) -> None:
    """Fail closed until a separate dataset-generation checkpoint."""

    raise ReconstructionAuthorizationError("dataset generation is not authorized")


def _utc_datetime(value: str):
    from datetime import datetime

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("request datetimes must be timezone-aware UTC")
    return parsed
