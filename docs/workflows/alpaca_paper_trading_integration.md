# Alpaca Paper-Trading Integration Workflow

## Objective

This document defines the v0.4 workflow for integrating Alpaca paper trading into the validated six-ticker PPO research stack.

The objective is not immediate live execution. The objective is to establish a controlled, auditable broker-connected execution layer around the validated six-ticker baseline.

Validated universe:

```text
AAPL
AMD
MRK
PFE
UNH
XOM
````

Research checkpoints:

```text
v0.2-six-ticker-validation-baseline
v0.3-alpaca-paper-trading-safety-chain
```

---

## Research Context

The v0.2 workflow validated the six-ticker PPO baseline through:

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

The next phase connects the validated research baseline to Alpaca paper trading inside the VS Code research environment.

The original Colab implementation validated several broker-facing components:

```text
Alpaca paper endpoint setup
account and position checks
historical bar retrieval
PPO model loading
VecNormalize loading
live feature reconstruction
PPO inference
target-weight conversion
order submission
position reconciliation
flattening logic
run_summary.csv logging
trade_log_master.csv logging
post-run evaluation reporting
```

That implementation was intentionally not migrated directly because it mixed:

```text
notebook dependency installation
Google Drive paths
Colab upload/download helpers
live execution
evaluation logic
```

The v0.4 implementation separates these concerns into audited modules.

---

## System Design

The paper-trading layer is structured as a staged execution chain:

```text
1. Load validated model artifacts
2. Run broker-connected dry-run inference
3. Evaluate dry-run outputs
4. Convert target weights into execution intents
5. Build execution plans
6. Run risk controls
7. Submit paper orders only through explicit opt-in
```

Default behavior remains dry-run only.

---

## Safety Defaults

The paper-trading layer defaults to:

```text
DRY_RUN=1
AUTO_RUN_LIVE=0
REQUIRE_PAPER=1
ALLOW_SHORTS=0
```

Real paper-order submission requires an explicit command-line flag:

```bash
python -m src.paper_trading.paper_trade_loop --submit-orders
```

No module should submit orders implicitly during import or standard execution.

---

## Artifact Manifest

The paper-trading layer uses an explicit artifact manifest:

```text
config/paper_trading_six_ticker_manifest.json
```

Validated model selections:

```text
AAPL    ppo_AAPL_window1
AMD     ppo_AMD_window3
MRK     ppo_MRK_window1
PFE     ppo_PFE_window1
UNH     ppo_UNH_window1
XOM     ppo_XOM_window1
```

This prevents accidental selection of non-validated windows.

---

## Repository Structure

Implemented modules:

```text
src/paper_trading/
  __init__.py
  artifact_manifest.py
  paper_trade_dry_run.py
  evaluate_dry_run.py
  execution.py
  build_execution_plan.py
  risk_controls.py
  paper_trade_loop.py
```

Planned modules:

```text
src/paper_trading/logging_utils.py
```

---

## Alpaca Environment Configuration

Broker credentials are stored only in a local `.env` file.

Tracked:

```text
.env.example
```

Excluded from Git:

```text
.env
```

Required variables:

```env
APCA_API_KEY_ID=your_paper_key_here
APCA_API_SECRET_KEY=your_paper_secret_here
APCA_API_BASE_URL=https://paper-api.alpaca.markets
```

The dry-run layer requires Alpaca credentials because it connects to the paper account and retrieves account, position, and market-bar data.

Evaluation and execution-plan modules do not require broker credentials.

Credential validation:

```bash
python - <<'PY'
from dotenv import load_dotenv
import os
from alpaca.trading.client import TradingClient

load_dotenv(".env", override=True)

client = TradingClient(
    api_key=os.getenv("APCA_API_KEY_ID"),
    secret_key=os.getenv("APCA_API_SECRET_KEY"),
    paper=True,
    url_override=os.getenv("APCA_API_BASE_URL"),
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

# Stage 1 — Integration Scaffold

Implemented:

```text
docs/workflows/alpaca_paper_trading_integration.md
config/paper_trading_six_ticker_manifest.json
.env.example
src/paper_trading/__init__.py
```

This stage introduced the repository structure only.

No broker connection or order logic was enabled.

Commit:

```text
889ac57 Add Alpaca paper trading integration scaffold
```

---

# Stage 2 — Broker-Connected Dry Run

Implemented module:

```text
src/paper_trading/paper_trade_dry_run.py
```

Evaluator:

```text
src/paper_trading/evaluate_dry_run.py
```

The dry-run workflow:

```text
connects to Alpaca paper
loads validated PPO artifacts
retrieves recent market bars
runs PPO inference
compares target weights to actual exposure
writes dry-run reports
```

No orders are submitted.

Generated reports remain excluded from Git:

```text
reports/paper_trading_dry_runs/
```

---

# Stage 3 — Execution Intent Layer

Implemented module:

```text
src/paper_trading/execution.py
```

Test coverage:

```text
tests/test_paper_trading_execution.py
```

The execution layer converts target weights into structured execution intents.

Orders are only submitted when:

```text
submit_orders=True
dry_run=False
```

Commit:

```text
8708a43 Add controlled paper trading execution intents
```

---

# Stage 4 — Execution Plan Builder

Implemented module:

```text
src/paper_trading/build_execution_plan.py
```

Test coverage:

```text
tests/test_build_execution_plan.py
```

The execution-plan builder converts dry-run outputs into a structured execution plan.

It does not connect to Alpaca and does not submit orders.

Commit:

```text
89bb0b9 Add paper trading execution plan builder
```

---

# Stage 5 — Guarded Paper-Order Runner

Implemented module:

```text
src/paper_trading/paper_trade_loop.py
```

Test coverage:

```text
tests/test_paper_trade_loop.py
```

Default behavior submits no orders.

Operational rule:

```text
Do not use --submit-orders unless intentionally placing paper trades.
```

Commit:

```text
4e7b0cc Add guarded paper order runner
```

---

## Stage 6 Result: Risk Controls Integrated into Paper-Order Runner

Risk controls were integrated directly into the guarded paper-order runner.

Implemented module:

```text
src/paper_trading/risk_controls.py
```

Updated runner:

```text
src/paper_trading/paper_trade_loop.py
```

Test coverage:

```text
tests/test_paper_trading_risk_controls.py
tests/test_paper_trade_loop.py
```

The paper-order runner now evaluates risk controls before processing the execution plan.

Safety behavior:

```text
default mode:
  runs risk controls
  writes paper-order run output
  submits zero orders

--submit-orders mode:
  connects to Alpaca paper
  builds broker risk context
  runs risk controls
  blocks order submission if risk controls fail
  only submits paper orders if risk_passed=True
```

The risk-control layer checks:

```text
execution plan is non-empty
required execution-plan columns are present
quantity, price, equity, target weight, actual weight, and delta notional are finite
equity is above minimum threshold
single-symbol target weight is within limit
gross target exposure is within limit
net target exposure is within limit
no prior order_submitted flags exist in the execution plan
order sides are valid
rows requiring orders use buy or sell
quantities are non-negative
total order notional is within limit
single-order notional is within limit
flat-start requirements pass when enabled
execution-plan summary shows orders_submitted=0
```

Latest validated no-order command sequence:

```bash
python -m src.paper_trading.paper_trade_dry_run \
  --artifacts-dir models/ppo_models_master

python -m src.paper_trading.evaluate_dry_run \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.build_execution_plan \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.risk_controls \
  --run-dir reports/paper_trading_dry_runs/latest \
  --require-flat-start

python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/latest
```

Latest validated result:

```text
Risk result: PASS
risk_passed=True
orders_required=1
orders_submitted=0
submit_orders=False
Dry-run mode complete. No orders were submitted.
```

Current validation status:

```text
71 passed, 1 warning
```

The remaining warning is a third-party `websockets.legacy` deprecation warning and does not indicate a failed test.

Generated run outputs remain excluded from Git:

```text
reports/paper_trading_dry_runs/
```

Safety rule:

```text
Do not use --submit-orders unless intentionally placing Alpaca paper trades.
```

---

## QuantConnect Role

QuantConnect is not currently the primary validation environment because earlier LEAN runs encountered data-window availability issues.

QuantConnect remains useful for:

```text
Object Store validation
payload compatibility checks
timestamp alignment checks
execution-path smoke tests
```

Primary research validation remains local.

---

## Current Status

Research checkpoints:

```text
v0.2-six-ticker-validation-baseline
v0.3-alpaca-paper-trading-safety-chain
```

Current v0.4 progress:

```text
risk-control module implemented
risk controls integrated into guarded paper-order runner
submit-orders mode is blocked unless risk controls pass
```

Completed paper-trading components:

```text
paper-trading scaffold
artifact manifest
broker-connected dry run
dry-run evaluator
execution-intent layer
execution-plan builder
guarded paper-order runner
risk-control module
risk controls integrated into guarded runner
```

Current validation status:

```text
71 passed, 1 warning
```

The warning originates from a dependency deprecation in `websockets.legacy` and does not affect functionality.

---

## Current Safe Execution Chain

```bash
python -m src.paper_trading.paper_trade_dry_run \
  --artifacts-dir models/ppo_models_master

python -m src.paper_trading.evaluate_dry_run \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.build_execution_plan \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.risk_controls \
  --run-dir reports/paper_trading_dry_runs/latest \
  --require-flat-start

python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/latest
```

Expected result:

```text
Evaluation result: PASS
Execution plan complete. No orders were submitted.
Risk result: PASS
risk_passed=True
Dry-run mode complete. No orders were submitted.
orders_submitted=0
submit_orders=False
```

---

## Next Phase

The next phase should focus on execution audit logging before running extended paper-trading sessions.

Planned module:

```text
src/paper_trading/logging_utils.py
```

Required logging behavior:

```text
capture account state before execution
capture execution plan snapshot
capture risk-control report
capture paper-order runner output
capture submitted order ids when --submit-orders is used
capture final broker state after execution
write one auditable run record per paper-trading run
generated reports remain excluded from Git
```

Core safety requirements remain unchanged:

```text
default mode submits no orders
paper endpoint is mandatory
real paper orders require --submit-orders
risk controls must pass before submit-orders mode
generated reports remain excluded from Git
```
