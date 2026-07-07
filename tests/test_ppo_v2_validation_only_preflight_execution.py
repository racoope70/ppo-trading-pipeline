from pathlib import Path
import json
import re

import pandas as pd
import pytest

import src.ppo_v2_validation_only_preflight_execution as preflight


FEATURES = (
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "return_1h",
    "log_return_1h",
    "sma_10",
    "sma_20",
    "sma_50",
    "ema_12",
    "ema_26",
    "rsi_14",
    "macd",
    "macd_signal",
    "macd_hist",
    "atr_14",
    "realized_volatility_20",
    "volume_zscore_20",
    "close_to_sma20",
    "close_to_sma50",
    "hour_sin",
    "hour_cos",
    "day_of_week_sin",
    "day_of_week_cos",
)


def _fixture_frame():
    rows = []
    split_times = (
        "2023-01-03T15:30:00Z",
        "2024-06-24T14:30:00Z",
        "2024-12-23T15:30:00Z",
    )

    for symbol in ("AAPL", "AMD", "MRK", "PFE", "UNH", "XOM"):
        for index, timestamp in enumerate(split_times):
            row = {
                "Symbol": symbol,
                "Datetime": timestamp,
                "Open": 100.0 + index,
                "High": 101.0 + index,
                "Low": 99.0 + index,
                "Close": 100.5 + index,
                "Volume": 1_000_000 + index,
            }
            for feature in FEATURES:
                row.setdefault(feature, float(index + 1))
            rows.append(row)

    return pd.DataFrame(rows)


def _write_config(tmp_path, dataset_path, features=FEATURES, holdout_policy="final_validation_only"):
    config = {
        "io_boundary": {
            "local_input_dataset": str(dataset_path),
        },
        "universe": ["AAPL", "AMD", "MRK", "PFE", "UNH", "XOM"],
        "temporal_split": {
            "timezone": "UTC",
            "train_start": "2023-01-03T14:30:00Z",
            "train_end": "2024-06-14T20:00:00Z",
            "train_eval_embargo_start": "2024-06-17T13:30:00Z",
            "train_eval_embargo_end": "2024-06-21T20:00:00Z",
            "eval_start": "2024-06-24T13:30:00Z",
            "eval_end": "2024-12-13T21:00:00Z",
            "eval_holdout_embargo_start": "2024-12-16T14:30:00Z",
            "eval_holdout_embargo_end": "2024-12-20T21:00:00Z",
            "holdout_start": "2024-12-23T14:30:00Z",
            "holdout_end": "2025-06-30T20:00:00Z",
            "holdout_policy": holdout_policy,
        },
        "features": list(features),
        "training_parameters": {
            "no_submit": True,
        },
    }

    path = tmp_path / preflight.V3_07_CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def _request(tmp_path, dataset_reader=None, **kwargs):
    return preflight.ValidationOnlyPreflightRequest(
        run_id=preflight.V3_07_VALIDATION_RUN_ID,
        config_path=preflight.V3_07_CONFIG_PATH,
        output_root="artifacts/ppo_v2/preflight_validation/v3_07_validation_only_preflight",
        validation_only=True,
        no_submit=True,
        dataset_reader=dataset_reader,
        **kwargs,
    )


def test_request_requires_validation_only_and_no_submit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dataset_path = tmp_path / "input.parquet"
    dataset_path.write_bytes(b"fixture")
    _write_config(tmp_path, dataset_path)

    request = preflight.ValidationOnlyPreflightRequest(
        run_id=preflight.V3_07_VALIDATION_RUN_ID,
        config_path=preflight.V3_07_CONFIG_PATH,
        output_root="artifacts/ppo_v2/preflight_validation/v3_07_validation_only_preflight",
        validation_only=False,
        no_submit=False,
    )

    result = preflight.execute_validation_only_preflight(request)

    assert result.result == preflight.REJECTED_FAIL_CLOSED_RESULT
    assert "--validation-only is required" in result.errors
    assert "--no-submit is required" in result.errors
    assert result.created_files == ()


@pytest.mark.parametrize(
    "blocked_field",
    [
        "allow_sealed_training_command_execution",
        "allow_ppo_v2_training_execution",
        "allow_training_command_execution",
        "allow_model_learn",
        "allow_model_fitting",
        "allow_data_fetching",
        "allow_dataset_generation",
        "allow_model_artifact_creation",
        "allow_quarantine_model_output_creation",
        "allow_paper_orders",
        "allow_live_orders",
        "allow_controlled_submit",
        "allow_ppo_rf",
        "allow_ppo_xgboost",
        "allow_model_promotion",
        "allow_production_deployment",
        "allow_trading_edge_claims",
        "allow_profitability_claims",
    ],
)
def test_authorization_flags_fail_closed(tmp_path, monkeypatch, blocked_field):
    monkeypatch.chdir(tmp_path)
    dataset_path = tmp_path / "input.parquet"
    dataset_path.write_bytes(b"fixture")
    _write_config(tmp_path, dataset_path)

    result = preflight.execute_validation_only_preflight(
        _request(tmp_path, **{blocked_field: True})
    )

    assert result.result == preflight.REJECTED_FAIL_CLOSED_RESULT
    assert f"{blocked_field} must remain false" in result.errors
    assert result.created_files == ()


@pytest.mark.parametrize(
    "flag",
    [
        "--train",
        "--execute-sealed-training-command",
        "--model-learn",
        "--fit-model",
        "--fetch-data",
        "--generate-dataset",
        "--create-model-artifact",
        "--create-quarantine-model-output",
        "--paper-orders",
        "--live-orders",
        "--controlled-submit",
        "--ppo-rf",
        "--ppo-xgboost",
        "--promote-model",
    ],
)
def test_cli_rejects_training_submit_hybrid_and_artifact_flags(flag):
    exit_code = preflight.main(
        [
            "--run-id",
            preflight.V3_07_VALIDATION_RUN_ID,
            "--config",
            preflight.V3_07_CONFIG_PATH,
            "--output-root",
            "artifacts/ppo_v2/preflight_validation/v3_07_validation_only_preflight",
            "--validation-only",
            "--no-submit",
            flag,
        ]
    )

    assert exit_code == 2


def test_missing_dataset_fails_closed_without_reader_call(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    missing_dataset = tmp_path / "missing.parquet"
    _write_config(tmp_path, missing_dataset)

    def reader(_path):
        raise AssertionError("dataset reader should not be called when file is missing")

    result = preflight.execute_validation_only_preflight(
        _request(tmp_path, dataset_reader=reader)
    )

    assert result.result in {preflight.FAIL_RESULT, preflight.PARTIAL_FAIL_RESULT}
    assert result.evidence["R2"]["status"] == preflight.FAIL_RESULT
    assert "sealed dataset missing" in result.evidence["R2"]["errors"][0]
    assert result.evidence["R3"]["status"] == preflight.FAIL_RESULT
    assert result.evidence["R4"]["status"] == preflight.FAIL_RESULT
    assert result.evidence["R5"]["status"] == preflight.FAIL_RESULT
    assert result.evidence["R6"]["status"] == preflight.PASS_RESULT
    assert all("quarantine" not in path for path in result.created_files)


def test_valid_fixture_writes_only_validation_scoped_evidence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dataset_path = tmp_path / "input.parquet"
    dataset_path.write_bytes(b"fixture parquet placeholder")
    _write_config(tmp_path, dataset_path)

    result = preflight.execute_validation_only_preflight(
        _request(tmp_path, dataset_reader=lambda _path: _fixture_frame())
    )

    assert result.result == preflight.PASS_RESULT
    assert result.evidence["R1"]["status"] == preflight.PASS_RESULT
    assert result.evidence["R2"]["status"] == preflight.PASS_RESULT
    assert result.evidence["R3"]["status"] == preflight.PASS_RESULT
    assert result.evidence["R4"]["status"] == preflight.PASS_RESULT
    assert result.evidence["R5"]["status"] == preflight.PASS_RESULT
    assert result.evidence["R6"]["status"] == preflight.PASS_RESULT

    created = tuple(Path(path).name for path in result.created_files)
    assert "r1_preflight_result.json" in created
    assert "r2_sealed_dataset_identity.json" in created
    assert "r3_data_contract_coverage.json" in created
    assert "r4_temporal_split_embargo_holdout.json" in created
    assert "r5_training_input_handoff.json" in created
    assert "r6_runtime_dependency_git_state.json" in created
    assert "validation_inventory.json" in created
    assert "validation_checksums.sha256" in created

    assert all("preflight_validation" in path for path in result.created_files)
    assert all("quarantine" not in path for path in result.created_files)
    assert all(not path.endswith((".zip", ".pkl")) for path in result.created_files)


def test_forbidden_feature_input_columns_fail_r5(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dataset_path = tmp_path / "input.parquet"
    dataset_path.write_bytes(b"fixture parquet placeholder")
    _write_config(tmp_path, dataset_path, features=(*FEATURES, "Target"))

    result = preflight.execute_validation_only_preflight(
        _request(tmp_path, dataset_reader=lambda _path: _fixture_frame())
    )

    assert result.result in {preflight.FAIL_RESULT, preflight.PARTIAL_FAIL_RESULT}
    assert result.evidence["R5"]["status"] == preflight.FAIL_RESULT
    assert any(
        "forbidden feature input columns present" in error
        for error in result.evidence["R5"]["errors"]
    )


def test_invalid_holdout_policy_fails_r4(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dataset_path = tmp_path / "input.parquet"
    dataset_path.write_bytes(b"fixture parquet placeholder")
    _write_config(
        tmp_path,
        dataset_path,
        holdout_policy="model_selection_allowed",
    )

    result = preflight.execute_validation_only_preflight(
        _request(tmp_path, dataset_reader=lambda _path: _fixture_frame())
    )

    assert result.result in {preflight.FAIL_RESULT, preflight.PARTIAL_FAIL_RESULT}
    assert result.evidence["R4"]["status"] == preflight.FAIL_RESULT
    assert "holdout_policy must be final_validation_only" in result.evidence["R4"]["errors"]


def test_wrong_output_root_rejects_quarantine_and_model_artifact_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dataset_path = tmp_path / "input.parquet"
    dataset_path.write_bytes(b"fixture")
    _write_config(tmp_path, dataset_path)

    request = preflight.ValidationOnlyPreflightRequest(
        run_id=preflight.V3_07_VALIDATION_RUN_ID,
        config_path=preflight.V3_07_CONFIG_PATH,
        output_root="artifacts/ppo_v2/quarantine/v3_07_validation_only_preflight",
        validation_only=True,
        no_submit=True,
    )

    result = preflight.execute_validation_only_preflight(request)

    assert result.result == preflight.REJECTED_FAIL_CLOSED_RESULT
    assert "output_root must not use quarantine paths" in result.errors
    assert result.created_files == ()


def test_source_has_no_training_or_broker_execution_hooks():
    source = Path("src/ppo_v2_validation_only_preflight_execution.py").read_text(
        encoding="utf-8"
    )

    forbidden_patterns = [
        r"model\.learn",
        r"\.learn\(",
        r"\.fit\(",
        r"stable_baselines",
        r"submit_order",
        r"submit_orders",
        r"Alpaca",
        r"alpaca",
        r"requests\.",
        r"joblib\.dump",
        r"torch\.save",
        r"pickle\.dump",
    ]

    matches = [
        pattern
        for pattern in forbidden_patterns
        if re.search(pattern, source)
    ]

    assert matches == []


def test_source_does_not_use_model_artifact_or_quarantine_output_paths():
    source = Path("src/ppo_v2_validation_only_preflight_execution.py").read_text(
        encoding="utf-8"
    )

    assert "artifacts/ppo_v2/quarantine" not in source
    assert ".zip" not in source
    assert ".pkl" not in source
