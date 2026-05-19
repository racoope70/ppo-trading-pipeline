# Alpaca Paper-Trading Integration Workflow

## Objective

This document defines the v0.3 workflow for moving the useful Alpaca paper-trading logic from the Colab prototype into the VS Code research repository.

The goal is not to immediately enable live paper orders. The goal is to build a safe, auditable broker-connected paper-trading layer around the validated six-ticker PPO baseline.

Validated six-ticker universe:

```text
AAPL, AMD, MRK, PFE, UNH, XOM
```

Source checkpoint:

```text
v0.2-six-ticker-validation-baseline
```

---

## Why This Phase Exists

The v0.2 research workflow validated the six-ticker PPO baseline through:

```text
local mark-to-market simulation
payload manifest generation
payload manifest validation
transaction-cost sensitivity
weight-cap sensitivity
confidence-threshold sensitivity
return-window sensitivity
partial independent validation
unified independent six-ticker validation
```

The next step is to connect that validated research baseline to the Alpaca paper-trading layer in VS Code.

The previous Alpaca paper-trading implementation proved several broker-facing pieces in Colab, including:

```text
Alpaca paper endpoint setup
account and position checks
recent bar retrieval
PPO model loading
VecNormalize loading
live feature reconstruction
PPO predict()
target-weight conversion
order submission
position reconciliation
flattening logic
run_summary.csv logging
trade_log_master.csv logging
post-run evaluation reporting
```

However, the Colab version should not be copied directly into the repository as one large script because it mixes notebook dependency installation, Google Drive paths, Colab upload/download helpers, live execution, and post-run evaluation logic.

---

## Design Principle

The VS Code paper-trading system should be built in stages:

```text
1. Load
2. Predict
3. Compare
4. Log
5. Dry-run intended orders
6. Submit paper orders only with an explicit opt-in flag
```

The first implementation must be dry-run only.

---

## Safety Defaults

The v0.3 paper-trading layer should default to:

```text
DRY_RUN=1
AUTO_RUN_LIVE=0
REQUIRE_PAPER=1
ALLOW_SHORTS=0
```

Real paper order submission should require an explicit command-line flag in a later phase, for example:

```bash
python -m src.paper_trading.paper_trade_loop --submit-orders
```

No script should submit orders simply because it was imported or run without an explicit order flag.

---

## Artifact Manifest

The paper-trading layer uses an explicit artifact manifest:

```text
config/paper_trading_six_ticker_manifest.json
```

The manifest pins the validated model-window selections:

```text
AAPL    ppo_AAPL_window1
AMD     ppo_AMD_window3
MRK     ppo_MRK_window1
PFE     ppo_PFE_window1
UNH     ppo_UNH_window1
XOM     ppo_XOM_window1
```

This avoids accidentally selecting the highest available model window when that window was not the one selected by validation.

---

## Initial Package Structure

The paper-trading package starts here:

```text
src/paper_trading/
  __init__.py
```

Planned modules:

```text
src/paper_trading/config.py
src/paper_trading/artifact_manifest.py
src/paper_trading/artifact_loader.py
src/paper_trading/feature_engineering.py
src/paper_trading/inference.py
src/paper_trading/broker_state.py
src/paper_trading/execution.py
src/paper_trading/risk_controls.py
src/paper_trading/logging_utils.py
src/paper_trading/evaluator.py
src/paper_trading/paper_trade_dry_run.py
src/paper_trading/paper_trade_loop.py
```

---

## Stage 1: Scaffold

Stage 1 creates:

```text
docs/workflows/alpaca_paper_trading_integration.md
config/paper_trading_six_ticker_manifest.json
.env.example
src/paper_trading/__init__.py
```

This stage does not connect to Alpaca and does not place trades.

---

## Stage 2: Broker-Connected Dry Run

The first executable script should be:

```text
src/paper_trading/paper_trade_dry_run.py
```

Purpose:

```text
load .env
require Alpaca paper endpoint
load the six-ticker artifact manifest
verify required artifacts exist
fetch account and positions
fetch recent bars
compute live features
run PPO predictions
convert raw actions to target weights
compare target weights to actual weights
write dry-run logs
submit no orders
```

Expected command:

```bash
python -m src.paper_trading.paper_trade_dry_run
```

---

## Stage 3: Execution Logic Migration

After dry-run inference works, migrate the proven broker logic from the Colab script into dedicated modules:

```text
execution.py
risk_controls.py
logging_utils.py
evaluator.py
```

Useful logic to preserve:

```text
open-order checks
rebalance-to-target logic
strict flattening
exposure caps
take-profit / stop-loss handling
run_summary.csv logging
trade_log_master.csv logging
post-run evaluation reporting
```

---

## Stage 4: Controlled Paper-Order Submission

Only after dry-run behavior is verified should the project add:

```text
paper_trade_loop.py
```

Order submission should require an explicit flag:

```bash
python -m src.paper_trading.paper_trade_loop --submit-orders
```

Without that flag, the script should remain dry-run only.

---

## QuantConnect Role

QuantConnect is not the main performance backtest environment for this phase because the previous LEAN test had data-window availability issues.

QuantConnect remains useful for:

```text
Object Store loading checks
payload compatibility checks
timestamp alignment checks
execution-path smoke tests
```

Local VS Code validation remains the primary research benchmark until the QuantConnect data-window issue is resolved.

---

## Step 5 — validate and commit

Run:

```bash
python -m json.tool config/paper_trading_six_ticker_manifest.json > /dev/null
python -m pytest tests -q
git status --short
```

---

---

## Stage 2 Result: Broker-Connected Dry Run

The first broker-connected dry-run layer was implemented and validated.

Implemented module:

```text
src/paper_trading/paper_trade_dry_run.py
```

Safety-evaluation module:

```text
src/paper_trading/evaluate_dry_run.py
```

The dry-run command connects to Alpaca paper, loads the validated six-ticker PPO artifact manifest, verifies the selected artifacts, fetches recent bars, runs PPO inference, compares target weights to actual Alpaca positions, and writes dry-run logs.

It submits no orders.

Dry-run command:

```bash
python -m src.paper_trading.paper_trade_dry_run \
  --artifacts-dir models/ppo_models_master
```

Evaluation command:

```bash
python -m src.paper_trading.evaluate_dry_run \
  --run-dir reports/paper_trading_dry_runs/latest
```

The dry run successfully evaluated all six validated baseline tickers:

```text
AAPL
AMD
MRK
PFE
UNH
XOM
```

Safety checks passed:

```text
run_dir_exists: PASS
targets_csv_exists: PASS
summary_json_exists: PASS
targets_non_empty: PASS
required_columns_present: PASS
expected_symbols_present: PASS
one_row_per_expected_symbol: PASS
summary_rows_match_targets: PASS
summary_orders_submitted_zero: PASS
row_orders_submitted_zero: PASS
dry_run_flag_all_one: PASS
no_dry_run_errors: PASS
all_predict_ok: PASS
latest_bar_time_present: PASS
raw_action_finite: PASS
confidence_finite: PASS
target_weight_finite: PASS
actual_weight_finite: PASS
intended_notional_finite: PASS
confidence_between_0_and_1: PASS
target_weight_within_bound: PASS
summary_error_count_zero: PASS
summary_predict_ok_count_matches: PASS
```

Final evaluator result:

```text
Evaluation result: PASS
rows=6
predict_ok_count=6
error_count=0
orders_submitted=0
```

This confirms that the VS Code Alpaca paper-trading layer can load the validated six-ticker model artifacts, connect to Alpaca paper, run inference, compare intended exposure against current positions, and log results without submitting orders.

This is the required safety gate before migrating real order-execution logic from the Colab paper-trading prototype.

Generated dry-run outputs are intentionally excluded from Git:

```text
reports/paper_trading_dry_runs/
```

---

## Local Alpaca Environment File

Real Alpaca paper-trading credentials must be stored only in a local `.env` file.

The repository tracks:

```text
.env.example
```

The repository must not track:

```text
.env
```

Required local variables:

```env
APCA_API_KEY_ID=your_paper_key_here
APCA_API_SECRET_KEY=your_paper_secret_here
APCA_API_BASE_URL=https://paper-api.alpaca.markets
```

The dry-run script requires Alpaca credentials because it connects to the paper account and fetches account, position, and market-bar data.

The evaluator does not require Alpaca credentials because it only reads saved dry-run output files.

---

## Current Status

v0.3 has completed the first broker-connected paper-trading safety layer.

Completed v0.3 components:

```text
paper-trading scaffold
six-ticker artifact manifest
artifact manifest validator
broker-connected dry-run script
dry-run evaluator safety gate
```

Latest validated command sequence:

```bash
python -m src.paper_trading.paper_trade_dry_run \
  --artifacts-dir models/ppo_models_master

python -m src.paper_trading.evaluate_dry_run \
  --run-dir reports/paper_trading_dry_runs/latest
```

Expected result:

```text
Evaluation result: PASS
rows=6
predict_ok_count=6
error_count=0
orders_submitted=0
```

Next planned step:

```text
Migrate controlled execution logic from the Colab paper-trading prototype into dedicated VS Code modules, while keeping real paper-order submission behind an explicit opt-in flag.
```