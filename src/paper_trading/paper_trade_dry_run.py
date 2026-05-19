"""Broker-connected Alpaca paper-trading dry run.

This script is the first safe bridge between the validated six-ticker PPO
baseline and the Alpaca paper-trading layer.

It does NOT submit orders.

It:
- loads the validated six-ticker artifact manifest
- verifies model / VecNormalize / feature artifacts exist
- connects to Alpaca paper
- fetches account, positions, and recent bars
- loads PPO models
- rebuilds live features
- runs predict()
- converts raw actions to target weights
- compares target weights to actual Alpaca positions
- writes dry-run target/exposure logs
"""

from __future__ import annotations

import argparse
import json
import os
import pickle
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.paper_trading.artifact_manifest import (
    DEFAULT_MANIFEST_PATH,
    assert_all_required_artifacts_exist,
    load_manifest,
    resolve_artifact_paths,
)


DEFAULT_ARTIFACTS_DIR = Path("models/ppo_models_master")
DEFAULT_OUTPUT_ROOT = Path("reports/paper_trading_dry_runs")


# ============================================================
# Small config helpers
# ============================================================

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return bool(default)
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return float(default)


def _env_str(name: str, default: str) -> str:
    return str(os.getenv(name, default)).strip()


def ensure_utc_timestamp(value: Any) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def load_dotenv_if_available(env_path: str | Path) -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return

    path = Path(env_path)
    if path.exists():
        load_dotenv(path, override=True)
    else:
        load_dotenv(override=True)


# ============================================================
# Model / artifact loading
# ============================================================

def _constant_schedule(value: float):
    return lambda _progress_remaining: float(value)


def load_ppo_model(model_path: Path):
    """Load PPO model while handling SB3 schedule serialization differences."""
    from stable_baselines3 import PPO

    custom_objects = {
        "lr_schedule": _constant_schedule(5e-5),
        "clip_range": _constant_schedule(0.2),
        "clip_range_vf": _constant_schedule(0.2),
    }
    return PPO.load(str(model_path), custom_objects=custom_objects)


def load_vecnormalize(vecnorm_path: Path | None):
    """Load VecNormalize state if available."""
    if vecnorm_path is None:
        return None

    try:
        with vecnorm_path.open("rb") as f:
            obj = pickle.load(f)

        if hasattr(obj, "training"):
            obj.training = False
        if hasattr(obj, "norm_reward"):
            obj.norm_reward = False

        return obj
    except Exception:
        pass

    try:
        from stable_baselines3.common.vec_env import VecNormalize

        obj = VecNormalize.load(str(vecnorm_path), venv=None)

        if hasattr(obj, "training"):
            obj.training = False
        if hasattr(obj, "norm_reward"):
            obj.norm_reward = False

        return obj
    except Exception as error:
        raise RuntimeError(f"Could not load VecNormalize file {vecnorm_path}: {error}") from error


def load_features(features_path: Path | None) -> Any:
    if features_path is None:
        return None

    with features_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def expected_obs_shape(model: Any, vecnorm: Any) -> tuple[int, ...] | None:
    """Infer expected observation shape from model or VecNormalize."""
    for src in (model, vecnorm):
        try:
            obs_space = getattr(src, "observation_space", None)
            shape = tuple(getattr(obs_space, "shape", ()) or ())
            if shape:
                return shape
        except Exception:
            continue

    return None


# ============================================================
# Live feature engineering
# ============================================================

FEATURE_ALIASES = {
    "SMA_50": "Rolling_Mean_50",
    "Rolling_Mean_50": "SMA_50",
}


def denoise_wavelet(series: pd.Series, wavelet: str = "db1", level: int = 2) -> pd.Series:
    s = pd.Series(series).astype(float).ffill().bfill()
    arr = s.to_numpy()

    try:
        import pywt

        w = pywt.Wavelet(wavelet)
        max_level = pywt.dwt_max_level(len(arr), w.dec_len)
        safe_level = int(max(0, min(level, max_level)))

        if safe_level < 1:
            return s

        coeffs = pywt.wavedec(arr, w, mode="symmetric", level=safe_level)
        for idx in range(1, len(coeffs)):
            coeffs[idx] = np.zeros_like(coeffs[idx])

        rec = pywt.waverec(coeffs, w, mode="symmetric")
        return pd.Series(rec[: len(arr)], index=s.index)

    except Exception:
        return s.ewm(span=5, adjust=False).mean()


def add_regime(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Vol20"] = df["Close"].pct_change().rolling(20).std()
    df["Ret20"] = df["Close"].pct_change(20)

    vol_hi = (df["Vol20"] > df["Vol20"].median()).astype(int)
    trend_hi = (df["Ret20"].abs() > df["Ret20"].abs().median()).astype(int)

    df["Regime4"] = vol_hi * 2 + trend_hi
    return df


def add_features_live(df: pd.DataFrame) -> pd.DataFrame:
    """Rebuild live features from Alpaca OHLCV bars."""
    df = df.copy().sort_index()

    rename_map = {}
    lower_to_original = {str(col).lower(): col for col in df.columns}

    for final_name, aliases in {
        "Open": ["open"],
        "High": ["high"],
        "Low": ["low"],
        "Close": ["close", "last"],
        "Adj Close": ["adj close", "adj_close", "adjclose", "adjusted close"],
        "Volume": ["volume", "vol"],
    }.items():
        for candidate in [final_name.lower(), *aliases]:
            if candidate in lower_to_original:
                rename_map[lower_to_original[candidate]] = final_name
                break

    df = df.rename(columns=rename_map)

    if "Adj Close" not in df.columns and "Close" in df.columns:
        df["Adj Close"] = df["Close"]

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Live bars are missing required columns: {missing}")

    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["STD_20"] = df["Close"].rolling(20).std()
    df["Upper_Band"] = df["SMA_20"] + 2 * df["STD_20"]
    df["Lower_Band"] = df["SMA_20"] - 2 * df["STD_20"]

    df["Lowest_Low"] = df["Low"].rolling(14).min()
    df["Highest_High"] = df["High"].rolling(14).max()
    denom = (df["Highest_High"] - df["Lowest_Low"]).replace(0, np.nan)
    df["Stoch"] = ((df["Close"] - df["Lowest_Low"]) / denom) * 100

    df["ROC"] = df["Close"].pct_change(10)

    signed_move = np.sign(df["Close"].diff().fillna(0))
    df["OBV"] = (signed_move * df["Volume"].fillna(0)).cumsum()

    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    sma_tp = typical_price.rolling(20).mean()
    mean_dev = (typical_price - sma_tp).abs().rolling(20).mean().replace(0, np.nan)
    df["CCI"] = (typical_price - sma_tp) / (0.015 * mean_dev)

    df["EMA_10"] = df["Close"].ewm(span=10, adjust=False).mean()
    df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD_Line"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD_Line"].ewm(span=9, adjust=False).mean()

    diff = df["Close"].diff()
    gain = diff.clip(lower=0)
    loss = -diff.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))

    true_range = pd.concat(
        [
            df["High"] - df["Low"],
            (df["High"] - df["Close"].shift()).abs(),
            (df["Low"] - df["Close"].shift()).abs(),
        ],
        axis=1,
    ).max(axis=1)

    df["ATR"] = true_range.ewm(alpha=1 / 14, adjust=False).mean()
    df["Volatility"] = df["Close"].pct_change().rolling(20).std()
    df["Denoised_Close"] = denoise_wavelet(df["Close"])

    df = add_regime(df)

    # Placeholder features used during training / live prototype.
    df["SentimentScore"] = 0.0
    df["Delta"] = df["Close"].pct_change(1).fillna(0.0)
    df["Gamma"] = df["Delta"].diff().fillna(0.0)

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    return df


def resolve_feature_alias(name: str, df: pd.DataFrame) -> str | None:
    if name in df.columns:
        return name

    alt = FEATURE_ALIASES.get(name)
    if alt and alt in df.columns:
        return alt

    return None


def normalize_feature_spec(features_hint: Any) -> list[str] | None:
    if features_hint is None:
        return None

    if isinstance(features_hint, dict):
        for key in ("features", "feature_names", "columns"):
            value = features_hint.get(key)
            if isinstance(value, list):
                return [str(item) for item in value]
        return None

    if isinstance(features_hint, list):
        return [str(item) for item in features_hint]

    return None


def compute_artifact_feature_order(features_hint: Any, df: pd.DataFrame) -> list[str]:
    requested = normalize_feature_spec(features_hint)

    if requested is None:
        return [
            col
            for col in df.columns
            if pd.api.types.is_numeric_dtype(df[col])
        ]

    drop_names = {"datetime", "symbol", "target", "return"}

    resolved: list[str] = []
    for feature in requested:
        if feature.lower() in drop_names:
            continue

        col = resolve_feature_alias(feature, df)
        if col and pd.api.types.is_numeric_dtype(df[col]):
            resolved.append(col)

    return resolved


def pick_columns_for_channels(features_hint: Any, df: pd.DataFrame, channels: int) -> list[str]:
    ordered = compute_artifact_feature_order(features_hint, df)

    if len(ordered) >= channels:
        return ordered[:channels]

    numeric = [
        col
        for col in df.columns
        if pd.api.types.is_numeric_dtype(df[col])
    ]

    preferred = ["Close", "Volume", "Adj Close", "Open", "High", "Low"]
    cols = [col for col in preferred if col in numeric]
    cols.extend([col for col in numeric if col not in cols])

    cols = cols[:channels]

    if cols:
        while len(cols) < channels:
            cols.append(cols[-1])

    return cols[:channels]


def prepare_observation_from_bars(
    bars_df: pd.DataFrame,
    features_hint: Any,
    expected_shape: tuple[int, ...] | None,
    min_required_rows: int = 60,
) -> tuple[np.ndarray, pd.Timestamp, float]:
    """Create PPO observation from recent bars."""
    features_df = add_features_live(bars_df)

    latest_ts = ensure_utc_timestamp(features_df.index[-1])
    latest_close = float(features_df["Close"].iloc[-1])

    if expected_shape is not None and len(expected_shape) == 2:
        lookback = int(expected_shape[0])
        channels = int(expected_shape[1])

        cols = pick_columns_for_channels(features_hint, features_df, channels)
        if not cols:
            raise ValueError("Could not resolve numeric feature columns for 2D observation.")

        window_df = features_df[cols].tail(lookback).fillna(0.0)
        arr = window_df.to_numpy(dtype=np.float32)

        if arr.shape[0] < lookback:
            padding = np.zeros((lookback - arr.shape[0], channels), dtype=np.float32)
            arr = np.vstack([padding, arr])

        obs = arr[-lookback:, :channels]
        return obs.astype(np.float32), latest_ts, latest_close

    feature_order = compute_artifact_feature_order(features_hint, features_df)

    if not feature_order:
        raise ValueError("No feature columns resolved for 1D observation.")

    features_df = features_df.dropna(subset=feature_order)

    if len(features_df) < max(20, min_required_rows):
        raise ValueError(f"Not enough feature rows after dropna: {len(features_df)}")

    latest_row = features_df.iloc[-1]

    values = []
    for col in feature_order:
        value = latest_row.get(col, 0.0)
        values.append(0.0 if pd.isna(value) else float(value))

    return np.asarray(values, dtype=np.float32), latest_ts, latest_close


# ============================================================
# Inference
# ============================================================

def action_to_weight(
    action: Any,
    *,
    weight_cap: float,
    sizing_mode: str,
    conf_floor: float,
    allow_shorts: bool,
) -> tuple[float, float, float]:
    """Convert PPO action into target weight, confidence, and raw action."""
    raw = float(np.asarray(action).reshape(-1)[0])
    clipped = float(np.clip(raw, -1.0, 1.0))
    confidence = float(min(1.0, abs(raw)))

    target_weight = clipped * float(weight_cap)

    if not allow_shorts:
        target_weight = max(0.0, target_weight)

    if str(sizing_mode).strip().lower() == "threshold":
        if confidence < conf_floor:
            target_weight = 0.0
        else:
            scale = (confidence - conf_floor) / max(1e-9, 1.0 - conf_floor)
            target_weight = (
                np.sign(target_weight)
                * float(weight_cap)
                * float(np.clip(scale, 0.0, 1.0))
            )

    return float(target_weight), float(confidence), float(raw)


def infer_target_weight(
    model: Any,
    vecnorm: Any,
    obs: np.ndarray,
    *,
    deterministic: bool,
    weight_cap: float,
    sizing_mode: str,
    conf_floor: float,
    allow_shorts: bool,
) -> tuple[float, float, float]:
    x = np.asarray(obs, dtype=np.float32)

    if (
        vecnorm is not None
        and hasattr(vecnorm, "normalize_obs")
        and getattr(vecnorm, "obs_rms", None) is not None
    ):
        try:
            x = vecnorm.normalize_obs(x)
        except Exception:
            try:
                x = vecnorm.normalize_obs(np.expand_dims(x, axis=0))[0]
            except Exception:
                pass

    try:
        action, _ = model.predict(x, deterministic=deterministic)
    except Exception:
        action, _ = model.predict(np.expand_dims(x, axis=0), deterministic=deterministic)
        action = np.asarray(action).reshape(-1)[0]

    return action_to_weight(
        action,
        weight_cap=weight_cap,
        sizing_mode=sizing_mode,
        conf_floor=conf_floor,
        allow_shorts=allow_shorts,
    )


# ============================================================
# Alpaca state
# ============================================================

def get_position_snapshot(trading_client: Any, symbols: list[str]) -> dict[str, dict[str, float]]:
    wanted = {symbol.upper() for symbol in symbols}

    snapshot = {
        symbol: {
            "qty": 0.0,
            "market_value": 0.0,
            "avg_entry_price": 0.0,
        }
        for symbol in wanted
    }

    try:
        positions = trading_client.get_all_positions() or []
    except Exception:
        return snapshot

    for position in positions:
        symbol = str(getattr(position, "symbol", "")).upper()

        if symbol not in wanted:
            continue

        try:
            snapshot[symbol]["qty"] = float(getattr(position, "qty", 0.0) or 0.0)
            snapshot[symbol]["market_value"] = float(getattr(position, "market_value", 0.0) or 0.0)
            snapshot[symbol]["avg_entry_price"] = float(getattr(position, "avg_entry_price", 0.0) or 0.0)
        except Exception:
            continue

    return snapshot


@dataclass
class DryRunConfig:
    manifest_path: Path
    artifacts_dir: Path
    env_path: Path
    output_root: Path
    bars_limit: int
    timeframe: str
    deterministic: bool
    weight_cap: float
    sizing_mode: str
    conf_floor: float
    allow_shorts: bool
    feed: str

def build_config(args: argparse.Namespace) -> DryRunConfig:
    return DryRunConfig(
        manifest_path=Path(args.manifest),
        artifacts_dir=Path(args.artifacts_dir),
        env_path=Path(args.env),
        output_root=Path(args.output_root),
        bars_limit=int(args.bars_limit),
        timeframe=str(args.timeframe),
        deterministic=not bool(args.stochastic),
        weight_cap=float(
            args.weight_cap
            if args.weight_cap is not None
            else _env_float("WEIGHT_CAP", 0.40)
        ),
        sizing_mode=str(
            args.sizing_mode
            if args.sizing_mode is not None
            else _env_str("SIZING_MODE", "linear")
        ),
        conf_floor=float(
            args.conf_floor
            if args.conf_floor is not None
            else _env_float("CONF_FLOOR", 0.00)
        ),
        allow_shorts=bool(
            args.allow_shorts
            if args.allow_shorts
            else _env_bool("ALLOW_SHORTS", False)
        ),
        feed=str(
            args.feed
            if args.feed is not None
            else _env_str("BARS_FEED", "iex")
        ),
    )


def make_output_dir(root: Path) -> Path:
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = root / run_id
    out_dir.mkdir(parents=True, exist_ok=False)
    return out_dir


def run_dry_run(config: DryRunConfig) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Run broker-connected dry-run inference for the manifest universe."""
    load_dotenv_if_available(config.env_path)
    os.environ["BARS_FEED"] = config.feed

    # Lazy import to keep tests / CI lightweight.
    from src.adapters.alpaca import (
        create_alpaca_clients,
        get_account_snapshot,
        get_recent_bars,
    )

    manifest = load_manifest(config.manifest_path)
    assert_all_required_artifacts_exist(manifest, config.artifacts_dir)

    trading_client, data_client = create_alpaca_clients(
        env_path=config.env_path,
        require_paper=True,
    )

    account = get_account_snapshot(trading_client)
    equity = float(account["equity"])

    position_snapshot = get_position_snapshot(trading_client, manifest.universe)

    rows: list[dict[str, Any]] = []

    for symbol in manifest.universe:
        prefix = manifest.selected_prefix(symbol)
        artifact_paths = resolve_artifact_paths(config.artifacts_dir, prefix)

        row_base = {
            "datetime_utc": utc_now_iso(),
            "symbol": symbol,
            "selected_prefix": prefix,
            "equity": equity,
            "dry_run": 1,
            "order_submitted": 0,
            "note": "",
        }

        try:
            model_path = artifact_paths["model_zip"]
            vecnorm_path = artifact_paths["vecnormalize_pkl"]
            features_path = artifact_paths["features_json"]

            if model_path is None or vecnorm_path is None or features_path is None:
                raise FileNotFoundError(f"Missing artifacts for {symbol}: {artifact_paths}")

            model = load_ppo_model(model_path)
            vecnorm = load_vecnormalize(vecnorm_path)
            features_hint = load_features(features_path)

            shape = expected_obs_shape(model, vecnorm)
            lookback = int(shape[0]) if shape and len(shape) == 2 else 60
            bars_limit = max(config.bars_limit, lookback * 3, 200)

            bars_df = get_recent_bars(
                data_client=data_client,
                symbol=symbol,
                limit=bars_limit,
                timeframe=config.timeframe,
                feed=config.feed,
            )

            if bars_df.empty:
                raise ValueError("No recent Alpaca bars returned.")

            obs, latest_bar_time, latest_close = prepare_observation_from_bars(
                bars_df=bars_df,
                features_hint=features_hint,
                expected_shape=shape,
                min_required_rows=max(20, lookback),
            )

            target_weight, confidence, raw_action = infer_target_weight(
                model=model,
                vecnorm=vecnorm,
                obs=obs,
                deterministic=config.deterministic,
                weight_cap=config.weight_cap,
                sizing_mode=config.sizing_mode,
                conf_floor=config.conf_floor,
                allow_shorts=config.allow_shorts,
            )

            pos = position_snapshot.get(symbol, {})
            actual_qty = float(pos.get("qty", 0.0))
            actual_market_value = float(pos.get("market_value", 0.0))
            actual_weight = actual_market_value / equity if equity > 0 else np.nan

            intended_delta_weight = target_weight - actual_weight
            intended_notional = intended_delta_weight * equity

            row = {
                **row_base,
                "latest_bar_time": latest_bar_time.isoformat(),
                "latest_price": latest_close,
                "observation_shape": str(tuple(np.asarray(obs).shape)),
                "model_path": str(model_path),
                "vecnorm_path": str(vecnorm_path),
                "features_path": str(features_path),
                "raw_action": raw_action,
                "confidence": confidence,
                "target_weight": target_weight,
                "actual_qty": actual_qty,
                "actual_market_value": actual_market_value,
                "actual_weight": actual_weight,
                "intended_delta_weight": intended_delta_weight,
                "intended_notional": intended_notional,
                "note": "dry_run_predict_ok",
            }

        except Exception as error:
            pos = position_snapshot.get(symbol, {})
            actual_market_value = float(pos.get("market_value", 0.0))
            actual_weight = actual_market_value / equity if equity > 0 else np.nan

            row = {
                **row_base,
                "latest_bar_time": "",
                "latest_price": np.nan,
                "observation_shape": "",
                "model_path": str(artifact_paths.get("model_zip", "")),
                "vecnorm_path": str(artifact_paths.get("vecnormalize_pkl", "")),
                "features_path": str(artifact_paths.get("features_json", "")),
                "raw_action": np.nan,
                "confidence": np.nan,
                "target_weight": np.nan,
                "actual_qty": float(pos.get("qty", 0.0)),
                "actual_market_value": actual_market_value,
                "actual_weight": actual_weight,
                "intended_delta_weight": np.nan,
                "intended_notional": np.nan,
                "note": f"dry_run_error: {str(error)[:300]}",
            }

        rows.append(row)

    df = pd.DataFrame(rows)

    config_dict = asdict(config)
    config_dict.update(
        {
            "manifest_path": str(config.manifest_path),
            "artifacts_dir": str(config.artifacts_dir),
            "env_path": str(config.env_path),
            "output_root": str(config.output_root),
        }
    )

    summary = {
        "datetime_utc": utc_now_iso(),
        "manifest": str(config.manifest_path),
        "artifacts_dir": str(config.artifacts_dir),
        "universe": manifest.universe,
        "selected_models": manifest.selected_models,
        "source_git_tag": manifest.source_git_tag,
        "source_validation": manifest.source_validation,
        "account": account,
        "config": config_dict,
        "rows": int(len(df)),
        "predict_ok_count": int((df["note"] == "dry_run_predict_ok").sum()),
        "error_count": int((df["note"] != "dry_run_predict_ok").sum()),
        "orders_submitted": 0,
    }

    return df, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Alpaca broker-connected dry-run inference for the six-ticker PPO baseline."
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Path to paper-trading manifest JSON.",
    )
    parser.add_argument(
        "--artifacts-dir",
        default=str(DEFAULT_ARTIFACTS_DIR),
        help="Directory containing selected PPO model artifacts.",
    )
    parser.add_argument(
        "--env",
        default=".env",
        help="Path to local .env file containing Alpaca paper credentials.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory where dry-run outputs will be written.",
    )
    parser.add_argument(
        "--bars-limit",
        type=int,
        default=250,
        help="Minimum number of recent bars requested per symbol.",
    )
    parser.add_argument(
        "--timeframe",
        default=os.getenv("DATA_TIMEFRAME", "1H"),
        help="Alpaca bar timeframe. Default: DATA_TIMEFRAME env var or 1H.",
    )
    parser.add_argument(
        "--feed",
        default=None,
        help="Alpaca data feed override, for example iex.",
    )
    parser.add_argument(
        "--weight-cap",
        type=float,
        default=None,
        help="Target absolute weight cap. Default: WEIGHT_CAP env var or 0.40.",
    )
    parser.add_argument(
        "--sizing-mode",
        default=None,
        help="Sizing mode, such as linear or threshold. Default: SIZING_MODE env var or linear.",
    )
    parser.add_argument(
        "--conf-floor",
        type=float,
        default=None,
        help="Confidence floor for threshold sizing. Default: CONF_FLOOR env var or 0.00.",
    )
    parser.add_argument(
        "--allow-shorts",
        action="store_true",
        help="Allow negative target weights during dry-run inference.",
    )
    parser.add_argument(
        "--stochastic",
        action="store_true",
        help="Use stochastic PPO prediction instead of deterministic prediction.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Load .env before building config so WEIGHT_CAP, SIZING_MODE, BARS_FEED, etc. are visible.
    load_dotenv_if_available(args.env)

    config = build_config(args)
    output_dir = make_output_dir(config.output_root)

    print("=" * 80)
    print("ALPACA PAPER-TRADING DRY RUN")
    print("=" * 80)
    print("Orders submitted: 0")
    print(f"Manifest: {config.manifest_path}")
    print(f"Artifacts dir: {config.artifacts_dir}")
    print(f"Output dir: {output_dir}")
    print()

    df, summary = run_dry_run(config)

    targets_path = output_dir / "dry_run_targets.csv"
    summary_path = output_dir / "dry_run_summary.json"

    df.to_csv(targets_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    latest_dir = config.output_root / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(latest_dir / "dry_run_targets.csv", index=False)
    (latest_dir / "dry_run_summary.json").write_text(
        json.dumps(summary, indent=2, default=str),
        encoding="utf-8",
    )

    display_cols = [
        "symbol",
        "selected_prefix",
        "raw_action",
        "confidence",
        "target_weight",
        "actual_weight",
        "intended_notional",
        "note",
    ]

    print(df[display_cols].to_string(index=False))
    print()
    print(f"Saved targets: {targets_path}")
    print(f"Saved summary: {summary_path}")
    print()
    print("Dry run complete. No orders were submitted.")

    if int(summary["error_count"]) > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()