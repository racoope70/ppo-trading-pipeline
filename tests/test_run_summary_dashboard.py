import json
from pathlib import Path

from src.paper_trading.run_summary_dashboard import (
    build_dashboard_payload,
    read_csv_if_exists,
    read_json_if_exists,
    render_markdown_dashboard,
    summarize_latest_run,
    write_dashboard,
)


def _write_latest_run(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)

    (root / "dry_run_summary.json").write_text(
        json.dumps(
            {
                "rows": 6,
                "predict_ok_count": 6,
                "error_count": 0,
            }
        ),
        encoding="utf-8",
    )

    (root / "execution_plan_summary.json").write_text(
        json.dumps(
            {
                "execution_plan": {
                    "orders_required": 1,
                    "gross_intended_notional": 1000.0,
                }
            }
        ),
        encoding="utf-8",
    )

    (root / "paper_order_run_summary.json").write_text(
        json.dumps(
            {
                "submit_orders": True,
                "orders_required": 1,
                "orders_submitted": 1,
                "risk_passed": True,
            }
        ),
        encoding="utf-8",
    )

    (root / "pre_trade_checklist_report.json").write_text(
        json.dumps({"passed": True}),
        encoding="utf-8",
    )

    (root / "paper_trade_audit_log.json").write_text(
        json.dumps(
            {
                "risk_passed": True,
                "orders_submitted": 1,
            }
        ),
        encoding="utf-8",
    )

    (root / "execution_plan.csv").write_text(
        "symbol,side,qty,price,target_weight,actual_weight,delta_notional,should_order,order_submitted\n"
        "AMD,sell,1.0,500,0,0.1,-500,True,False\n",
        encoding="utf-8",
    )

    (root / "paper_order_run.csv").write_text(
        "symbol,side,qty,price,target_weight,actual_weight,delta_notional,should_order,order_submitted\n"
        "AMD,sell,1.0,500,0,0.1,-500,True,True\n",
        encoding="utf-8",
    )


def test_read_json_if_exists_returns_empty_for_missing_file(tmp_path):
    assert read_json_if_exists(tmp_path / "missing.json") == {}


def test_read_csv_if_exists_returns_rows(tmp_path):
    path = tmp_path / "x.csv"
    path.write_text("symbol,side\nAMD,sell\n", encoding="utf-8")

    rows = read_csv_if_exists(path)

    assert rows == [{"symbol": "AMD", "side": "sell"}]


def test_summarize_latest_run_extracts_key_metrics(tmp_path):
    run_dir = tmp_path / "latest"
    _write_latest_run(run_dir)

    summary = summarize_latest_run(run_dir)

    assert summary["dry_run_rows"] == 6
    assert summary["paper_orders_submitted"] == 1
    assert summary["paper_risk_passed"] is True
    assert len(summary["order_candidates"]) == 1
    assert len(summary["submitted_orders"]) == 1


def test_render_markdown_dashboard_contains_status(tmp_path):
    run_dir = tmp_path / "latest"
    _write_latest_run(run_dir)

    payload = build_dashboard_payload(run_dir)
    md = render_markdown_dashboard(payload)

    assert "v1.4 Paper-Trading Run Summary" in md
    assert "Latest Run Summary" in md


def test_write_dashboard_outputs_files(tmp_path):
    run_dir = tmp_path / "latest"
    out_json = tmp_path / "out" / "dashboard.json"
    out_md = tmp_path / "out" / "dashboard.md"

    _write_latest_run(run_dir)

    payload, json_path, md_path = write_dashboard(
        run_dir=run_dir,
        output_json=out_json,
        output_md=out_md,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert payload["latest_run"]["paper_orders_submitted"] == 1
