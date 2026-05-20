# Alpaca Paper-Trading Integration Workflow

## Objective

This document defines the v0.3 workflow for moving useful Alpaca paper-trading logic from the Colab prototype into the VS Code research repository.

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
1. Load validated model artifacts
2. Run broker-connected dry-run inference
3. Evaluate dry-run output
4. Convert target weights into execution intents
5. Build an execution plan
6. Submit paper orders only with an explicit opt-in flag
```

The first implementation must remain dry-run only.

---

## Safety Defaults

The v0.3 paper-trading layer should default to:

```text
DRY_RUN=1
AUTO_RUN_LIVE=0
REQUIRE_PAPER=1
ALLOW_SHORTS=0
```

Real paper-order submission should require an explicit command-line flag in a later phase, for example:

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

## Package Structure

Current implemented modules:

```text
src/paper_trading/
  __init__.py
  artifact_manifest.py
  paper_trade_dry_run.py
  evaluate_dry_run.py
  execution.py
  build_execution_plan.py
```

Planned future modules:

```text
src/paper_trading/risk_controls.py
src/paper_trading/logging_utils.py
src/paper_trading/paper_trade_loop.py
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

The evaluator and execution-plan builder do not require Alpaca credentials because they only read saved dry-run output files.

Credential check command:

```bash
python - <<'PY'
from dotenv import load_dotenv
import os
from alpaca.trading.client import TradingClient

load_dotenv(".env", override=True)

key = os.getenv("APCA_API_KEY_ID", "").strip()
secret = os.getenv("APCA_API_SECRET_KEY", "").strip()
base_url = os.getenv("APCA_API_BASE_URL", "").strip()

print("key_loaded:", bool(key), "key_len:", len(key))
print("secret_loaded:", bool(secret), "secret_len:", len(secret))
print("base_url:", base_url)

client = TradingClient(
    api_key=key,
    secret_key=secret,
    paper=True,
    url_override=base_url,
)

account = client.get_account()
print("account_status:", account.status)
print("account_currency:", account.currency)
print("credential_check: PASS")
PY
```

Expected result:

```text
credential_check: PASS
```

---

## Stage 1 Result: Scaffold

Stage 1 created the initial paper-trading integration scaffold.

Implemented files:

```text
docs/workflows/alpaca_paper_trading_integration.md
config/paper_trading_six_ticker_manifest.json
.env.example
src/paper_trading/__init__.py
```

This stage did not connect to Alpaca and did not place trades.

Commit:

```text
889ac57 Add Alpaca paper trading integration scaffold
```

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

Commits:

```text
f1ac28b Add Alpaca paper trading dry run
b5af6d5 Add paper trading dry run evaluator
afc2a11 Document Alpaca paper trading dry run checkpoint
```

Generated dry-run outputs are intentionally excluded from Git:

```text
reports/paper_trading_dry_runs/
```

---

## Stage 3 Result: Controlled Execution Intent Layer

Controlled execution logic was migrated into a dedicated module:

```text
src/paper_trading/execution.py
```

Test coverage:

```text
tests/test_paper_trading_execution.py
```

This module converts target weights into proposed buy/sell/hold intents.

It supports:

```text
target-weight clamping
short blocking by default
target notional calculation
actual exposure comparison
buy/sell/hold intent creation
minimum-notional filtering
fractional-quantity rounding
execution-intent summaries
guarded order execution
```

Safety guard:

```text
execute_rebalance_intent()
```

will not submit an order unless both conditions are true:

```text
submit_orders=True
dry_run=False
```

This means execution logic can be tested and audited without enabling real paper-order submission.

Commit:

```text
8708a43 Add controlled paper trading execution intents
```

---

## Stage 4 Result: Execution Plan Builder

The execution-plan builder was added:

```text
src/paper_trading/build_execution_plan.py
```

Test coverage:

```text
tests/test_build_execution_plan.py
```

This script reads dry-run target outputs and converts them into a structured execution plan.

It does not connect to Alpaca and does not submit orders.

Command sequence:

```bash
python -m src.paper_trading.paper_trade_dry_run \
  --artifacts-dir models/ppo_models_master

python -m src.paper_trading.evaluate_dry_run \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.build_execution_plan \
  --run-dir reports/paper_trading_dry_runs/latest
```

Latest validated result:

```text
Execution plan complete. No orders were submitted.
```

Example execution-plan output:

```text
AMD  buy   44.285365 shares
XOM  buy   22.148884 shares
AAPL hold
MRK  hold
PFE  hold
UNH  hold
```

Execution-plan summary:

```text
rows: 6
orders_required: 2
gross_intended_notional: 21943.7424
buy_count: 2
sell_count: 0
orders_submitted: 0
```

This confirms the bridge from model output to proposed execution is working:

```text
PPO prediction
target weight
actual exposure comparison
buy/sell/hold intent
execution plan
zero orders submitted
```

Commit:

```text
89bb0b9 Add paper trading execution plan builder
```

Generated execution-plan outputs are intentionally excluded from Git:

```text
reports/paper_trading_dry_runs/
```

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

## Current Status

v0.2 is complete and tagged:

```text
v0.2-six-ticker-validation-baseline
```

v0.3 has completed the first broker-connected paper-trading safety chain.

Completed v0.3 components:

```text
paper-trading scaffold
six-ticker artifact manifest
artifact manifest validator
broker-connected dry-run script
dry-run evaluator safety gate
controlled execution-intent module
execution-plan builder
```

Latest validation status:

```text
52 passed, 1 warning
```

The warning is from a dependency deprecation warning in `websockets.legacy` and does not block the test suite.

---

## Current Safe Command Chain

Run the full current paper-trading safety chain:

```bash
python -m src.paper_trading.paper_trade_dry_run \
  --artifacts-dir models/ppo_models_master

python -m src.paper_trading.evaluate_dry_run \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.build_execution_plan \
  --run-dir reports/paper_trading_dry_runs/latest
```

Expected result:

```text
Evaluation result: PASS
Execution plan complete. No orders were submitted.
orders_submitted=0
```

---

## Paper Account Baseline

A new Alpaca paper account was opened for the v0.3 six-ticker paper-trading validation.

Starting broker state:

```text
Equity: $100,000
Cash: $100,000
Positions: 0
Open orders: 0
```

This account serves as the clean baseline for future controlled six-ticker paper-trading tests.

The account should remain flat before any intentional paper-order test. Real paper orders must only be submitted through the guarded runner using the explicit `--submit-orders` flag.

---

## Next Planned Steptarget-weight clamping


The next phase should add controlled order-submission plumbing, but still keep real paper-order submission behind an explicit opt-in flag.

Planned module:

```text
src/paper_trading/paper_trade_loop.py
```

Required safety behavior:

```text
default mode submits no orders
real paper orders require --submit-orders
paper endpoint is required
dry-run/evaluator/execution-plan checks must pass before order submission
generated reports stay out of Git
```