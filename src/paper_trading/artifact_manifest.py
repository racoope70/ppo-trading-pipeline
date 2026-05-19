"""Artifact manifest utilities for Alpaca paper trading.

This module loads and validates the six-ticker paper-trading manifest used by
the VS Code Alpaca paper-trading layer.

It intentionally does not connect to Alpaca and does not load PPO models. Its
job is only to make sure the selected model-window mapping is explicit and that
the expected artifact files are present before broker-connected inference runs.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST_PATH = Path("config/paper_trading_six_ticker_manifest.json")


@dataclass(frozen=True)
class PaperTradingManifest:
    """Validated paper-trading artifact manifest."""

    path: Path
    baseline_name: str
    universe: list[str]
    selected_models: dict[str, str]
    source_git_tag: str
    source_validation: dict[str, Any]
    raw: dict[str, Any]

    def selected_prefix(self, symbol: str) -> str:
        """Return the selected artifact prefix for a ticker."""
        symbol_u = symbol.upper()
        if symbol_u not in self.selected_models:
            raise KeyError(f"{symbol_u} is not present in selected_models.")
        return self.selected_models[symbol_u]


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Manifest field '{name}' must be an object/dict.")
    return value


def _require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"Manifest field '{name}' must be a list.")
    return value


def load_manifest(path: str | Path = DEFAULT_MANIFEST_PATH) -> PaperTradingManifest:
    """Load and validate a paper-trading artifact manifest."""
    manifest_path = Path(path)

    if not manifest_path.exists():
        raise FileNotFoundError(f"Paper-trading manifest not found: {manifest_path}")

    with manifest_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, dict):
        raise ValueError("Paper-trading manifest root must be a JSON object.")

    universe_raw = _require_list(raw.get("universe"), "universe")
    universe = [str(symbol).upper().strip() for symbol in universe_raw if str(symbol).strip()]

    if not universe:
        raise ValueError("Manifest universe cannot be empty.")

    selected_models_raw = _require_dict(raw.get("selected_models"), "selected_models")
    selected_models = {
        str(symbol).upper().strip(): str(prefix).strip()
        for symbol, prefix in selected_models_raw.items()
        if str(symbol).strip() and str(prefix).strip()
    }

    missing = sorted(set(universe) - set(selected_models))
    extra = sorted(set(selected_models) - set(universe))

    if missing:
        raise ValueError(f"Manifest selected_models is missing symbols: {missing}")

    if extra:
        raise ValueError(f"Manifest selected_models has symbols not in universe: {extra}")

    baseline_name = str(raw.get("baseline_name", "")).strip()
    if not baseline_name:
        raise ValueError("Manifest field 'baseline_name' is required.")

    source_git_tag = str(raw.get("source_git_tag", "")).strip()
    if not source_git_tag:
        raise ValueError("Manifest field 'source_git_tag' is required.")

    source_validation = _require_dict(raw.get("source_validation"), "source_validation")

    return PaperTradingManifest(
        path=manifest_path,
        baseline_name=baseline_name,
        universe=universe,
        selected_models=selected_models,
        source_git_tag=source_git_tag,
        source_validation=source_validation,
        raw=raw,
    )


def _first_match(artifacts_dir: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        matches = sorted(artifacts_dir.glob(pattern))
        if matches:
            return matches[0]
    return None


def resolve_artifact_paths(
    artifacts_dir: str | Path,
    selected_prefix: str,
) -> dict[str, Path | None]:
    """Resolve model, VecNormalize, and feature files for a selected prefix."""
    root = Path(artifacts_dir)

    return {
        "model_zip": _first_match(
            root,
            [
                f"{selected_prefix}_model*.zip",
                f"{selected_prefix}*model*.zip",
            ],
        ),
        "vecnormalize_pkl": _first_match(
            root,
            [
                f"{selected_prefix}_vecnorm*.pkl",
                f"{selected_prefix}*vecnorm*.pkl",
                f"{selected_prefix}_vecnormalize*.pkl",
                f"{selected_prefix}*vecnormalize*.pkl",
            ],
        ),
        "features_json": _first_match(
            root,
            [
                f"{selected_prefix}_features*.json",
                f"{selected_prefix}*features*.json",
            ],
        ),
    }


def verify_manifest_artifacts(
    manifest: PaperTradingManifest,
    artifacts_dir: str | Path,
) -> list[dict[str, Any]]:
    """Return artifact availability rows for each manifest symbol."""
    root = Path(artifacts_dir)

    rows: list[dict[str, Any]] = []

    for symbol in manifest.universe:
        prefix = manifest.selected_prefix(symbol)
        paths = resolve_artifact_paths(root, prefix)

        row = {
            "symbol": symbol,
            "selected_prefix": prefix,
            "model_zip": str(paths["model_zip"]) if paths["model_zip"] else "",
            "vecnormalize_pkl": str(paths["vecnormalize_pkl"]) if paths["vecnormalize_pkl"] else "",
            "features_json": str(paths["features_json"]) if paths["features_json"] else "",
            "model_zip_exists": paths["model_zip"] is not None,
            "vecnormalize_pkl_exists": paths["vecnormalize_pkl"] is not None,
            "features_json_exists": paths["features_json"] is not None,
        }

        row["all_required_artifacts_exist"] = bool(
            row["model_zip_exists"]
            and row["vecnormalize_pkl_exists"]
            and row["features_json_exists"]
        )

        rows.append(row)

    return rows


def assert_all_required_artifacts_exist(
    manifest: PaperTradingManifest,
    artifacts_dir: str | Path,
) -> None:
    """Raise if any required artifacts are missing."""
    rows = verify_manifest_artifacts(manifest, artifacts_dir)
    missing = [row for row in rows if not row["all_required_artifacts_exist"]]

    if missing:
        details = [
            {
                "symbol": row["symbol"],
                "selected_prefix": row["selected_prefix"],
                "model_zip_exists": row["model_zip_exists"],
                "vecnormalize_pkl_exists": row["vecnormalize_pkl_exists"],
                "features_json_exists": row["features_json_exists"],
            }
            for row in missing
        ]
        raise FileNotFoundError(f"Missing required paper-trading artifacts: {details}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate paper-trading artifact manifest and artifact files."
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Path to paper-trading manifest JSON.",
    )
    parser.add_argument(
        "--artifacts-dir",
        default="artifacts",
        help="Directory containing PPO paper-trading artifacts.",
    )
    parser.add_argument(
        "--require-files",
        action="store_true",
        help="Fail if model, VecNormalize, or feature files are missing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    manifest = load_manifest(args.manifest)
    rows = verify_manifest_artifacts(manifest, args.artifacts_dir)

    print("=" * 80)
    print("PAPER-TRADING ARTIFACT MANIFEST")
    print("=" * 80)
    print(f"Manifest: {manifest.path}")
    print(f"Baseline: {manifest.baseline_name}")
    print(f"Source tag: {manifest.source_git_tag}")
    print(f"Universe: {', '.join(manifest.universe)}")
    print(f"Artifacts dir: {Path(args.artifacts_dir)}")
    print()

    for row in rows:
        status = "PASS" if row["all_required_artifacts_exist"] else "MISSING"
        print(
            f"{status:8} {row['symbol']:5} {row['selected_prefix']} | "
            f"model={row['model_zip_exists']} "
            f"vecnorm={row['vecnormalize_pkl_exists']} "
            f"features={row['features_json_exists']}"
        )

    if args.require_files:
        assert_all_required_artifacts_exist(manifest, args.artifacts_dir)

    print()
    print("Manifest validation complete.")


if __name__ == "__main__":
    main()
