"""Alpaca historical data loader.

v1.6 scope:
- Download Alpaca historical stock bars.
- Normalize the returned bar data into a stable tabular format.
- Save raw bars and provenance metadata.
- Do not train models.
- Do not submit orders.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
from dotenv import load_dotenv


STANDARD_COLUMNS = [
    "timestamp",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "trade_count",
    "vwap",
]

NUMERIC_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "trade_count",
    "vwap",
]


@dataclass(frozen=True)
class AlpacaHistoricalDataConfig:
    symbols: list[str]
    start: str
    end: str
    timeframe: str = "1H"
    feed: str = "iex"
    output_dir: str = "data/alpaca_historical/raw"
    env_path: str = ".env"


def parse_symbols(values: Iterable[str] | str) -> list[str]:
    """Parse symbols from comma-separated strings or iterable inputs."""
    if isinstance(values, str):
        raw = values.replace(",", " ").split()
    else:
        raw = []
        for value in values:
            raw.extend(str(value).replace(",", " ").split())

    symbols = [item.strip().upper() for item in raw if item.strip()]
    unique_symbols = list(dict.fromkeys(symbols))

    if not unique_symbols:
        raise ValueError("At least one symbol is required.")

    return unique_symbols


def parse_datetime_utc(value: str) -> datetime:
    """Parse date/datetime text into a timezone-aware UTC datetime."""
    cleaned = str(value).strip()

    if not cleaned:
        raise ValueError("Datetime value cannot be empty.")

    if len(cleaned) == 10:
        cleaned = f"{cleaned}T00:00:00+00:00"

    cleaned = cleaned.replace("Z", "+00:00")
    dt = datetime.fromisoformat(cleaned)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def resolve_alpaca_timeframe(timeframe: str):
    """Resolve supported local timeframe text to alpaca-py TimeFrame."""
    from alpaca.data.timeframe import TimeFrame

    normalized = str(timeframe).strip().lower()

    if normalized in {"1h", "1hour", "hour", "hourly"}:
        return TimeFrame.Hour

    if normalized in {"1d", "day", "daily"}:
        return TimeFrame.Day

    raise ValueError(
        f"Unsupported timeframe for v1.6: {timeframe}. "
        "Supported values: 1H, 1D."
    )


def resolve_alpaca_feed(feed: str):
    """Resolve feed text to alpaca-py DataFeed enum when available."""
    if feed is None:
        return None

    normalized = str(feed).strip().lower()

    if normalized in {"", "none", "auto"}:
        return None

    from alpaca.data.enums import DataFeed

    if normalized == "iex":
        return DataFeed.IEX

    if normalized == "sip":
        return DataFeed.SIP

    raise ValueError(f"Unsupported Alpaca feed: {feed}. Use iex, sip, or auto.")


def get_alpaca_data_client(env_path: str = ".env"):
    """Create an Alpaca historical data client from environment variables."""
    load_dotenv(env_path, override=True)

    api_key = os.getenv("APCA_API_KEY_ID") or os.getenv("ALPACA_API_KEY_ID")
    api_secret = os.getenv("APCA_API_SECRET_KEY") or os.getenv("ALPACA_API_SECRET_KEY")

    if not api_key or not api_secret:
        raise EnvironmentError(
            "Missing Alpaca API credentials. Expected APCA_API_KEY_ID/APCA_API_SECRET_KEY "
            "or ALPACA_API_KEY_ID/ALPACA_API_SECRET_KEY."
        )

    from alpaca.data.historical import StockHistoricalDataClient

    return StockHistoricalDataClient(api_key, api_secret)


def normalize_alpaca_bars_dataframe(
    raw_df: pd.DataFrame,
    *,
    expected_symbols: list[str] | None = None,
) -> pd.DataFrame:
    """Normalize alpaca-py bars DataFrame into a stable schema.

    alpaca-py usually returns a DataFrame indexed by symbol and timestamp.
    This function handles MultiIndex, single-index, and already-flat data.
    """
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    df = raw_df.copy()

    if isinstance(df.index, pd.MultiIndex):
        df = df.reset_index()
    else:
        df = df.reset_index()

    rename_map = {}
    for col in df.columns:
        lower = str(col).strip().lower()

        if lower in {"index", "time", "datetime", "date"}:
            rename_map[col] = "timestamp"
        elif lower in {"level_0"}:
            rename_map[col] = "symbol"
        elif lower in {"level_1"}:
            rename_map[col] = "timestamp"
        else:
            rename_map[col] = lower

    df = df.rename(columns=rename_map)

    if "symbol" not in df.columns:
        if expected_symbols and len(expected_symbols) == 1:
            df["symbol"] = expected_symbols[0]
        else:
            raise ValueError("Could not determine symbol column from Alpaca bars data.")

    if "timestamp" not in df.columns:
        raise ValueError("Could not determine timestamp column from Alpaca bars data.")

    df["symbol"] = df["symbol"].astype(str).str.upper()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
        df[col] = pd.to_numeric(df[col], errors="coerce")

    out = df[STANDARD_COLUMNS].copy()
    out = out.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

    return out


def validate_bars_dataframe(
    df: pd.DataFrame,
    *,
    expected_symbols: list[str] | None = None,
) -> dict[str, Any]:
    """Validate normalized bar data and return a validation summary."""
    missing_columns = [col for col in STANDARD_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if df.empty:
        raise ValueError("Bars dataframe is empty.")

    if df["timestamp"].isna().any():
        raise ValueError("Bars dataframe contains missing timestamps.")

    if df["symbol"].isna().any():
        raise ValueError("Bars dataframe contains missing symbols.")

    duplicate_count = int(df.duplicated(subset=["symbol", "timestamp"]).sum())
    if duplicate_count:
        raise ValueError(f"Duplicate symbol/timestamp rows found: {duplicate_count}")

    actual_symbols = sorted(df["symbol"].astype(str).str.upper().unique().tolist())
    expected = sorted(parse_symbols(expected_symbols or actual_symbols))

    missing_symbols = sorted(set(expected) - set(actual_symbols))
    if missing_symbols:
        raise ValueError(f"Missing expected symbols: {missing_symbols}")

    for col in ["open", "high", "low", "close"]:
        if df[col].isna().any():
            raise ValueError(f"Missing values in required OHLC column: {col}")

    invalid_ohlc = df[
        (df["high"] < df["low"])
        | (df["open"] <= 0)
        | (df["high"] <= 0)
        | (df["low"] <= 0)
        | (df["close"] <= 0)
    ]

    if not invalid_ohlc.empty:
        raise ValueError("Invalid OHLC values detected.")

    return {
        "passed": True,
        "rows": int(len(df)),
        "symbols": actual_symbols,
        "min_timestamp_utc": df["timestamp"].min().isoformat(),
        "max_timestamp_utc": df["timestamp"].max().isoformat(),
        "duplicate_count": duplicate_count,
    }


def build_provenance(
    *,
    config: AlpacaHistoricalDataConfig,
    df: pd.DataFrame,
    validation: dict[str, Any],
) -> dict[str, Any]:
    """Build provenance metadata for a saved Alpaca historical dataset."""
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": "alpaca_historical_stock_bars",
        "symbols": config.symbols,
        "start": config.start,
        "end": config.end,
        "timeframe": config.timeframe,
        "feed": config.feed,
        "rows": int(len(df)),
        "columns": list(df.columns),
        "validation": validation,
        "notes": [
            "Raw Alpaca historical bar dataset.",
            "No model training performed in v1.6.",
            "No orders submitted.",
        ],
    }


def dataset_file_stem(config: AlpacaHistoricalDataConfig) -> str:
    symbols = "_".join(config.symbols)
    start = config.start[:10].replace("-", "")
    end = config.end[:10].replace("-", "")
    timeframe = config.timeframe.lower().replace(" ", "")
    feed = config.feed.lower()

    return f"alpaca_bars_{symbols}_{timeframe}_{feed}_{start}_{end}"


def save_bars_dataset(
    df: pd.DataFrame,
    *,
    config: AlpacaHistoricalDataConfig,
    validation: dict[str, Any],
) -> tuple[Path, Path]:
    """Save normalized bars and provenance metadata."""
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = dataset_file_stem(config)
    csv_path = output_dir / f"{stem}.csv"
    provenance_path = output_dir / f"{stem}_provenance.json"

    df.to_csv(csv_path, index=False)

    provenance = build_provenance(
        config=config,
        df=df,
        validation=validation,
    )

    provenance_path.write_text(
        json.dumps(provenance, indent=2),
        encoding="utf-8",
    )

    return csv_path, provenance_path


def download_alpaca_historical_bars(
    config: AlpacaHistoricalDataConfig,
) -> pd.DataFrame:
    """Download historical bars from Alpaca and return normalized bars."""
    from alpaca.data.requests import StockBarsRequest

    client = get_alpaca_data_client(config.env_path)

    request_kwargs = {
        "symbol_or_symbols": config.symbols,
        "timeframe": resolve_alpaca_timeframe(config.timeframe),
        "start": parse_datetime_utc(config.start),
        "end": parse_datetime_utc(config.end),
    }

    feed = resolve_alpaca_feed(config.feed)
    if feed is not None:
        request_kwargs["feed"] = feed

    request = StockBarsRequest(**request_kwargs)
    bars = client.get_stock_bars(request)

    return normalize_alpaca_bars_dataframe(
        bars.df,
        expected_symbols=config.symbols,
    )


def run_download(
    config: AlpacaHistoricalDataConfig,
) -> tuple[pd.DataFrame, dict[str, Any], Path, Path]:
    """Download, validate, and save Alpaca historical bars."""
    df = download_alpaca_historical_bars(config)
    validation = validate_bars_dataframe(df, expected_symbols=config.symbols)
    csv_path, provenance_path = save_bars_dataset(
        df,
        config=config,
        validation=validation,
    )

    return df, validation, csv_path, provenance_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download Alpaca historical stock bars for PPO retraining."
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        required=True,
        help="Symbols to download, for example: AAPL AMD MRK PFE UNH XOM",
    )
    parser.add_argument("--start", required=True, help="Start date/datetime.")
    parser.add_argument("--end", required=True, help="End date/datetime.")
    parser.add_argument("--timeframe", default="1H", help="Default: 1H")
    parser.add_argument("--feed", default="iex", help="Default: iex")
    parser.add_argument(
        "--output-dir",
        default="data/alpaca_historical/raw",
    )
    parser.add_argument("--env-path", default=".env")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = AlpacaHistoricalDataConfig(
        symbols=parse_symbols(args.symbols),
        start=args.start,
        end=args.end,
        timeframe=args.timeframe,
        feed=args.feed,
        output_dir=args.output_dir,
        env_path=args.env_path,
    )

    df, validation, csv_path, provenance_path = run_download(config)

    print("=" * 80)
    print("v1.6 ALPACA HISTORICAL DATA LOADER")
    print("=" * 80)
    print(f"symbols: {config.symbols}")
    print(f"timeframe: {config.timeframe}")
    print(f"feed: {config.feed}")
    print(f"rows: {len(df)}")
    print(f"min_timestamp_utc: {validation['min_timestamp_utc']}")
    print(f"max_timestamp_utc: {validation['max_timestamp_utc']}")
    print(f"saved_csv: {csv_path}")
    print(f"saved_provenance: {provenance_path}")


if __name__ == "__main__":
    main()
