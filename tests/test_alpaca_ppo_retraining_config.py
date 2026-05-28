import json
from pathlib import Path

import pytest

from src.alpaca_ppo_retraining_config import (
    AlpacaPPORetrainingConfig,
    config_from_dict,
    config_to_dict,
    ensure_output_dirs,
    load_config_json,
    normalize_symbols,
    validate_config,
    write_config_json,
)


def test_normalize_symbols_handles_commas_spaces_and_duplicates():
    assert normalize_symbols(["aapl, amd", "AAPL", "xom"]) == ("AAPL", "AMD", "XOM")


def test_default_config_validates_without_requiring_dataset():
    config = AlpacaPPORetrainingConfig()

    summary = validate_config(config, check_dataset_exists=False)

    assert summary["passed"] is True
    assert summary["symbols"] == ["AAPL", "AMD", "MRK", "PFE", "UNH", "XOM"]
    assert summary["test_mode"] is True


def test_validate_config_can_require_dataset_files(tmp_path):
    dataset = tmp_path / "dataset.csv"
    provenance = tmp_path / "provenance.json"

    dataset.write_text("Datetime,Symbol,Close\n", encoding="utf-8")
    provenance.write_text("{}", encoding="utf-8")

    config = AlpacaPPORetrainingConfig(
        dataset_path=str(dataset),
        dataset_provenance_path=str(provenance),
    )

    summary = validate_config(config, check_dataset_exists=True)

    assert summary["dataset_exists"] is True
    assert summary["dataset_provenance_exists"] is True


def test_validate_config_rejects_bad_train_fraction():
    config = AlpacaPPORetrainingConfig(train_fraction=1.0)

    with pytest.raises(ValueError, match="train_fraction"):
        validate_config(config)


def test_validate_config_rejects_bad_holdout_fraction():
    config = AlpacaPPORetrainingConfig(holdout_fraction=0.0)

    with pytest.raises(ValueError, match="holdout_fraction"):
        validate_config(config)


def test_validate_config_rejects_negative_embargo():
    config = AlpacaPPORetrainingConfig(embargo_rows=-1)

    with pytest.raises(ValueError, match="embargo_rows"):
        validate_config(config)


def test_validate_config_rejects_step_larger_than_window():
    config = AlpacaPPORetrainingConfig(
        walkforward_window_size=100,
        walkforward_step_size=101,
    )

    with pytest.raises(ValueError, match="step_size"):
        validate_config(config)


def test_config_json_roundtrip(tmp_path):
    output_path = tmp_path / "config.json"

    config = AlpacaPPORetrainingConfig(
        symbols=("AAPL", "AMD"),
        artifacts_dir=str(tmp_path / "models"),
        results_dir=str(tmp_path / "reports"),
    )

    written = write_config_json(config, output_path)
    loaded = load_config_json(written)

    assert loaded.symbols == ("AAPL", "AMD")
    assert loaded.artifacts_dir == str(tmp_path / "models")
    assert loaded.results_dir == str(tmp_path / "reports")


def test_config_from_dict_ignores_unknown_keys():
    payload = {
        "symbols": ["aapl", "amd"],
        "train_fraction": 0.7,
        "unknown_key": "ignored",
    }

    config = config_from_dict(payload)

    assert config.symbols == ("AAPL", "AMD")
    assert config.train_fraction == 0.7


def test_config_to_dict_is_json_serializable():
    payload = config_to_dict(AlpacaPPORetrainingConfig())

    json.dumps(payload)

    assert payload["config_version"] == "v1.8.2"
    assert isinstance(payload["symbols"], list)


def test_ensure_output_dirs_creates_artifact_and_result_dirs(tmp_path):
    config = AlpacaPPORetrainingConfig(
        artifacts_dir=str(tmp_path / "models"),
        results_dir=str(tmp_path / "reports"),
    )

    paths = ensure_output_dirs(config)

    assert all(path.exists() for path in paths)
    assert Path(config.artifacts_dir).exists()
    assert Path(config.results_dir).exists()