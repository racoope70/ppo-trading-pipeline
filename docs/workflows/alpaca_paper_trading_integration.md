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

## Current Status

v0.2 is complete and tagged:

```text
v0.2-six-ticker-validation-baseline
```

v0.3 starts with safe paper-trading integration scaffolding.

---

## Step 5 — validate and commit

Run:

```bash
python -m json.tool config/paper_trading_six_ticker_manifest.json > /dev/null
python -m pytest tests -q
git status --short
```