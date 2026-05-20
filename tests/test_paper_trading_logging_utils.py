import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.paper_trading.logging_utils import (
    build_and_write_audit_record,
    build_audit_record,
    count_csv_rows,
    snapshot_account,
    snapshot_broker_state,
    snapshot_order,
    snapshot_position,
    summarize_file,
    to_json_safe,
    write_audit_record,
)


@dataclass
class ExampleData:
    name: str
    value: int


class FakeAccount:
    status = "ACTIVE"
    currency = "USD"
    equity = "100000"
    cash = "100000"
    buying_power = "200000"
    portfolio_value = "100000"


class FakePosition:
    symbol = "AMD"
    qty = "10"
    side = "long"
    market_value = "4440"
    avg_entry_price = "444"


class FakeOrder:
    id = "abc-123"
    symbol = "AMD"
    side = "buy"
    qty = "10"
    status = "accepted"
    filled_qty = "0"


class FakeClient:
    def get_account(self):
        return FakeAccount()

    def get_all_positions(self):
        return [FakePosition()]

    def get_orders(self):
        return [FakeOrder()]


def _write_run_outputs(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        [
            {"symbol": "AMD", "target_weight": 0.10},
            {"symbol": "PFE", "target_weight": 0.00},
        ]
    ).to_csv(run_dir / "dry_run_targets.csv", index=False)

    (run_dir / "dry_run_summary.json").write_text(
        json.dumps(
            {
                "rows": 2,
                "predict_ok_count": 2,
                "error_count": 0,
                "orders_submitted": 0,
            }
        ),
        encoding="utf-8",
    )

    pd.DataFrame(
        [
            {"symbol": "AMD", "side": "buy", "should_order": True},
            {"symbol": "PFE", "side": "hold", "should_order": False},
        ]
    ).to_csv(run_dir / "execution_plan.csv", index=False)

    (run_dir / "execution_plan_summary.json").write_text(
        json.dumps(
            {
                "orders_submitted": 0,
                "execution_plan": {
                    "rows": 2,
                    "orders_required": 1,
                },
            }
        ),
        encoding="utf-8",
    )

    pd.DataFrame(
        [
            {
                "symbol": "AMD",
                "side": "buy",
                "should_order": True,
                "order_submitted": False,
                "risk_passed": True,
            },
            {
                "symbol": "PFE",
                "side": "hold",
                "should_order": False,
                "order_submitted": False,
                "risk_passed": True,
            },
        ]
    ).to_csv(run_dir / "paper_order_run.csv", index=False)

    (run_dir / "paper_order_run_summary.json").write_text(
        json.dumps(
            {
                "rows": 2,
                "orders_required": 1,
                "orders_submitted": 0,
                "submit_orders": False,
                "risk_passed": True,
                "risk_report": {"passed": True, "checks": []},
            }
        ),
        encoding="utf-8",
    )


def test_to_json_safe_handles_dataclass_and_path():
    payload = {
        "path": Path("abc"),
        "data": ExampleData(name="x", value=1),
    }

    safe = to_json_safe(payload)

    assert safe["path"] == "abc"
    assert safe["data"] == {"name": "x", "value": 1}


def test_count_csv_rows_and_summarize_file(tmp_path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame([{"a": 1}, {"a": 2}]).to_csv(csv_path, index=False)

    assert count_csv_rows(csv_path) == 2

    summary = summarize_file(csv_path)
    assert summary.exists is True
    assert summary.rows == 2
    assert summary.size_bytes is not None


def test_summarize_missing_file(tmp_path):
    summary = summarize_file(tmp_path / "missing.csv")

    assert summary.exists is False
    assert summary.rows is None


def test_snapshot_account_position_and_order():
    account = snapshot_account(FakeAccount())
    position = snapshot_position(FakePosition())
    order = snapshot_order(FakeOrder())

    assert account["status"] == "ACTIVE"
    assert account["equity"] == "100000"
    assert position["symbol"] == "AMD"
    assert order["id"] == "abc-123"


def test_snapshot_broker_state_uses_fake_client():
    snapshot = snapshot_broker_state(FakeClient())

    assert snapshot["account"]["status"] == "ACTIVE"
    assert snapshot["positions_count"] == 1
    assert snapshot["open_orders_count"] == 1
    assert snapshot["positions"][0]["symbol"] == "AMD"
    assert snapshot["open_orders"][0]["id"] == "abc-123"


def test_build_audit_record_reads_run_outputs(tmp_path):
    _write_run_outputs(tmp_path)

    record = build_audit_record(
        run_dir=tmp_path,
        metadata={"tag": "unit_test"},
    )

    assert record["audit_type"] == "paper_trading_run"
    assert record["metadata"]["tag"] == "unit_test"
    assert record["dry_run_summary"]["rows"] == 2
    assert record["execution_plan_summary"]["execution_plan"]["orders_required"] == 1
    assert record["paper_order_run_summary"]["risk_passed"] is True
    assert record["risk_passed"] is True
    assert record["orders_submitted"] == 0
    assert record["files"]["dry_run_targets"]["rows"] == 2


def test_write_audit_record_outputs_json(tmp_path):
    record = {"audit_type": "paper_trading_run", "orders_submitted": 0}

    output_path = write_audit_record(record, tmp_path)

    assert output_path.exists()

    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["orders_submitted"] == 0


def test_build_and_write_audit_record_outputs_file(tmp_path):
    _write_run_outputs(tmp_path)

    record, output_path = build_and_write_audit_record(
        run_dir=tmp_path,
        metadata={"tag": "integration_test"},
    )

    assert output_path.exists()
    assert record["metadata"]["tag"] == "integration_test"
    assert record["orders_required"] == 1
    assert record["orders_submitted"] == 0