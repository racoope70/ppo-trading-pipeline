"""Build model-ready PPO training datasets from Alpaca historical bars.

v1.8.1 scope:
- Read normalized Alpaca historical bars from v1.6.
- Convert lower-case Alpaca columns into the existing PPO feature schema.
- Apply existing feature engineering and labeling pipeline.
- Save model-ready CSV and provenance metadata.
- Do not train PPO.
- Do not submit orders.
"""

from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.feature_manifest import build_safe_feature_columns
from src.features import build_model_dataset, compute_enhanced_features


ALPACA_INPUT_COLUMNS = [
    "timestamp",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
]

PPO_BASE_COLUMNS = [
    "Datetime",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Symbol",
]

REQUIRED_MODEL_READY_COLUMNS = [
    "Datetime",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Target",
    "Return",
    "Symbol",
]


@dataclass(frozen=True)
class AlpacaTrainingDatasetConfig:
    input_csv: str
    output_csv: str = "data/alpaca_training/model_ready/alpaca_ppo_training_dataset.csv"
    provenance_json: str = "data/alpaca_training/model_ready/alpaca_ppo_training_dataset_provenance.json"
    use_regime: bool = True
    use_sentiment: bool = False


def load_alpaca_bars_csv(path: str | Path) -> pd.DataFrame:
    """Load normalized Alpaca historical bars from CSV."""
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"Alpaca bars CSV not found: {p}")

    df = pd.read_csv(p)

    missing = [col for col in ALPACA_INPUT_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Alpaca bars CSV missing required columns: {missing}")

    return df


def convert_alpaca_bars_to_ppo_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Convert normalized Alpaca bars into the existing PPO feature schema."""
    data = df.copy()

    missing = [col for col in ALPACA_INPUT_COLUMNS if col not in data.columns]
    if missing:
        raise ValueError(f"Input bars missing required columns: {missing}")

    out = pd.DataFrame(
        {
            "Datetime": pd.to_datetime(data["timestamp"], utc=True),
            "Open": pd.to_numeric(data["open"], errors="coerce"),
            "High": pd.to_numeric(data["high"], errors="coerce"),
            "Low": pd.to_numeric(data["low"], errors="coerce"),
            "Close": pd.to_numeric(data["close"], errors="coerce"),
            "Volume": pd.to_numeric(data["volume"], errors="coerce"),
            "Symbol": data["symbol"].astype(str).str.upper(),
        }
    )

    out = out.sort_values(["Symbol", "Datetime"]).reset_index(drop=True)

    return out[PPO_BASE_COLUMNS]


def build_feature_frames(
    ppo_bars: pd.DataFrame,
    *,
    use_regime: bool = True,
    use_sentiment: bool = False,
) -> list[pd.DataFrame]:
    """Compute feature frames symbol by symbol."""
    if ppo_bars.empty:
        raise ValueError("PPO bars dataframe is empty.")

    feature_frames: list[pd.DataFrame] = []

    for symbol, group in ppo_bars.groupby("Symbol", sort=True):
        symbol_df = group.sort_values("Datetime").reset_index(drop=True)

        if len(symbol_df) < 60:
            raise ValueError(
                f"Not enough rows for feature engineering: {symbol} has {len(symbol_df)} rows."
            )

        features = compute_enhanced_features(
            symbol_df,
            use_regime=use_regime,
            use_sentiment=use_sentiment,
            sentiment_pipeline=None,
        )

        if features.empty:
            raise ValueError(f"Feature engineering returned no rows for {symbol}.")

        feature_frames.append(features)

    return feature_frames


def validate_model_ready_dataset(df: pd.DataFrame) -> dict[str, Any]:
    """Validate model-ready PPO dataset."""
    if df.empty:
        raise ValueError("Model-ready dataset is empty.")

    missing = [col for col in REQUIRED_MODEL_READY_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Model-ready dataset missing columns: {missing}")

    data = df.copy()
    data["Datetime"] = pd.to_datetime(data["Datetime"], utc=True)

    duplicate_count = int(data.duplicated(subset=["Symbol", "Datetime"]).sum())
    if duplicate_count:
        raise ValueError(f"Duplicate Symbol/Datetime rows found: {duplicate_count}")

    if data["Symbol"].isna().any():
        raise ValueError("Model-ready dataset has missing symbols.")

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if data[col].isna().any():
            raise ValueError(f"Missing values found in {col}.")
        if col != "Volume" and (data[col] <= 0).any():
            raise ValueError(f"Non-positive prices found in {col}.")

    if data["Target"].isna().any():
        raise ValueError("Target contains missing values.")

    if data["Return"].isna().any():
        raise ValueError("Return contains missing values.")

    safe_features = build_safe_feature_columns(data)

    forbidden_features = {"Target", "Return", "Datetime", "Symbol"}
    leaked = sorted(forbidden_features.intersection(safe_features))
    if leaked:
        raise ValueError(f"Unsafe columns found in safe feature list: {leaked}")

    symbols = sorted(data["Symbol"].astype(str).str.upper().unique().tolist())

    return {
        "passed": True,
        "rows": int(len(data)),
        "symbols": symbols,
        "columns": list(data.columns),
        "safe_feature_count": int(len(safe_features)),
        "safe_features": safe_features,
        "target_counts": {
            str(k): int(v)
            for k, v in data["Target"].value_counts().sort_index().to_dict().items()
        },
        "min_datetime_utc": data["Datetime"].min().isoformat(),
        "max_datetime_utc": data["Datetime"].max().isoformat(),
        "duplicate_count": duplicate_count,
    }


def build_training_dataset(
    bars_df: pd.DataFrame,
    *,
    use_regime: bool = True,
    use_sentiment: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build and validate a model-ready PPO dataset from Alpaca bars."""
    ppo_bars = convert_alpaca_bars_to_ppo_schema(bars_df)

    feature_frames = build_feature_frames(
        ppo_bars,
        use_regime=use_regime,
        use_sentiment=use_sentiment,
    )

    dataset = build_model_dataset(feature_frames)
    dataset = dataset.sort_values(["Symbol", "Datetime"]).reset_index(drop=True)

    validation = validate_model_ready_dataset(dataset)

    return dataset, validation


def build_provenance(
    *,
    config: AlpacaTrainingDatasetConfig,
    source_rows: int,
    dataset: pd.DataFrame,
    validation: dict[str, Any],
) -> dict[str, Any]:
    """Build provenance metadata for the model-ready dataset."""
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": "alpaca_historical_bars_to_ppo_training_dataset",
        "input_csv": str(config.input_csv),
        "output_csv": str(config.output_csv),
        "source_rows": int(source_rows),
        "model_ready_rows": int(len(dataset)),
        "use_regime": bool(config.use_regime),
        "use_sentiment": bool(config.use_sentiment),
        "validation": validation,
        "notes": [
            "v1.8.1 dataset builder only.",
            "No PPO training performed.",
            "No orders submitted.",
            "Target and Return are retained for labeling/evaluation but excluded from safe model features.",
        ],
    }


def save_training_dataset(
    dataset: pd.DataFrame,
    *,
    config: AlpacaTrainingDatasetConfig,
    provenance: dict[str, Any],
) -> tuple[Path, Path]:
    """Save model-ready dataset and provenance metadata."""
    output_csv = Path(config.output_csv)
    provenance_json = Path(config.provenance_json)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    provenance_json.parent.mkdir(parents=True, exist_ok=True)

    dataset.to_csv(output_csv, index=False)
    provenance_json.write_text(json.dumps(provenance, indent=2), encoding="utf-8")

    return output_csv, provenance_json


def run_builder(config: AlpacaTrainingDatasetConfig) -> tuple[pd.DataFrame, dict[str, Any], Path, Path]:
    """Run the complete dataset builder."""
    bars = load_alpaca_bars_csv(config.input_csv)

    dataset, validation = build_training_dataset(
        bars,
        use_regime=config.use_regime,
        use_sentiment=config.use_sentiment,
    )

    provenance = build_provenance(
        config=config,
        source_rows=len(bars),
        dataset=dataset,
        validation=validation,
    )

    output_csv, provenance_json = save_training_dataset(
        dataset,
        config=config,
        provenance=provenance,
    )

    return dataset, validation, output_csv, provenance_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build PPO training dataset from Alpaca historical bars."
    )
    parser.add_argument("--input-csv", required=True)
    parser.add_argument(
        "--output-csv",
        default="data/alpaca_training/model_ready/alpaca_ppo_training_dataset.csv",
    )
    parser.add_argument(
        "--provenance-json",
        default="data/alpaca_training/model_ready/alpaca_ppo_training_dataset_provenance.json",
    )
    parser.add_argument(
        "--disable-regime",
        action="store_true",
        help="Disable regime feature generation.",
    )
    parser.add_argument(
        "--enable-sentiment",
        action="store_true",
        help="Enable sentiment feature generation. Default is disabled.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = AlpacaTrainingDatasetConfig(
        input_csv=args.input_csv,
        output_csv=args.output_csv,
        provenance_json=args.provenance_json,
        use_regime=not args.disable_regime,
        use_sentiment=args.enable_sentiment,
    )

    dataset, validation, output_csv, provenance_json = run_builder(config)

    print("=" * 80)
    print("v1.8.1 ALPACA PPO TRAINING DATASET BUILDER")
    print("=" * 80)
    print(f"input_csv: {config.input_csv}")
    print(f"output_csv: {output_csv}")
    print(f"provenance_json: {provenance_json}")
    print(f"rows: {len(dataset)}")
    print(f"symbols: {validation['symbols']}")
    print(f"safe_feature_count: {validation['safe_feature_count']}")
    print(f"min_datetime_utc: {validation['min_datetime_utc']}")
    print(f"max_datetime_utc: {validation['max_datetime_utc']}")
    print(f"target_counts: {validation['target_counts']}")


if __name__ == "__main__":
    main()
