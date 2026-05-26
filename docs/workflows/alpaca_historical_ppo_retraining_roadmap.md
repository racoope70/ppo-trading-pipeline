# v1.5 Alpaca Historical-Data PPO Retraining Roadmap

Date: 2026-05-26  
Status: Roadmap checkpoint  
Scope: Standalone PPO retraining foundation before hybrid models

## Purpose

Define the next model-quality phase after the Alpaca paper-trading deployment reached a stable checkpoint.

The current deployment process has validated that existing PPO artifacts can be loaded, evaluated, converted into target weights, passed through risk controls, submitted to Alpaca Paper Trading, monitored, rebalanced, and summarized.

The next phase is to rebuild the standalone PPO training pipeline using Alpaca historical 1-hour bars so that the training data source better matches the live paper-trading data and broker execution environment.

## Current Completed Deployment Chain

The current paper-trading deployment chain is complete through v1.4:

```text
v1.0 QuantConnect execution-path retest
v1.1 controlled Alpaca paper-order test
v1.2 post-order monitoring and rebalance test
v1.3 short monitored paper-trading session
v1.4 paper-trading run summary dashboard
```

The system has demonstrated:

```text
.env key loading
Alpaca paper broker connection
Alpaca bar fetching
model artifact loading
model.predict() execution
target-weight generation
execution-plan generation
risk-control checks
guarded paper-order submission
audit logging
broker-state verification
open-order handling
existing-position handling
run-summary dashboard generation
```

## Strategic Decision

Before moving to PPO + Random Forest or PPO + XGBoost hybrids, the standalone PPO baseline should be retrained and revalidated on Alpaca historical 1-hour data.

This avoids adding hybrid model complexity before the standalone baseline is aligned with the broker/data environment used in paper trading.

## Why Move From Yahoo/Prepared Data to Alpaca Historical Data?

The current validated PPO deployment used existing trained artifacts from the earlier training process.

The next retrain should use Alpaca historical bars because the live paper-trading system already uses Alpaca for broker interaction and market data.

This reduces mismatch between:

```text
training data source
paper-trading inference data source
broker execution environment
future deployment data path
```

This does not guarantee improved returns, but it improves system consistency, auditability, and deployment realism.

## Required Validation Hardening Before Retraining

### 1. Embargo Gap Between Train and Evaluation Slices

A small embargo gap should be added between the training slice and evaluation slice.

Reason:

```text
rolling indicators can carry information near split boundaries
forward-return labels can create boundary leakage
normalization windows may indirectly reflect nearby observations
```

Planned behavior:

```text
train_slice = earlier portion of window
embargo_gap = skipped boundary period
eval_slice = later portion of window
```

Example:

```text
train_end = 2025-01-31 16:00
embargo_gap = 5 to 20 bars
eval_start = train_end + embargo_gap
```

The exact embargo size should be configurable.

### 2. VecNormalize Train-Only Statistics

VecNormalize statistics must be fit only on the training environment.

Required behavior:

```text
fit VecNormalize on train_slice only
save train VecNormalize statistics
create eval environment separately
load/copy train VecNormalize statistics into eval environment
set eval VecNormalize to training=False
set norm_reward=False during evaluation/inference
```

The evaluation environment should not update normalization statistics.

### 3. Safe Feature Manifest Remains Required

The safe feature manifest must remain enforced.

The model feature list must exclude:

```text
Target
Return
Symbol
Datetime
future-looking labels
metadata columns
any post-outcome fields
```

The saved feature list should represent only valid model-observable inputs.

### 4. Top-N Window Saving Remains Candidate Selection, Not Final Expected Performance

The training pipeline can continue saving top-N windows by Sharpe or risk-adjusted score.

However:

```text
best Sharpe window = candidate selection result
best Sharpe window != unbiased expected live performance
```

The selected model still needs:

```text
out-of-sample evaluation
temporal stability review
paper-trading dry-run validation
controlled paper-order validation
```

## Planned v1.5+ Roadmap

### v1.5 - Alpaca Historical-Data PPO Retraining Roadmap

Document the next phase.

Deliverable:

```text
docs/workflows/alpaca_historical_ppo_retraining_roadmap.md
```

No retraining code yet.

### v1.6 - Alpaca Historical Data Loader

Create a dedicated Alpaca historical-data download module.

Expected deliverables:

```text
src/data/alpaca_historical_data.py
tests/test_alpaca_historical_data.py
docs/workflows/alpaca_historical_data_loader.md
```

Responsibilities:

```text
connect to Alpaca historical data client
download 1-hour bars
support six-ticker baseline universe
standardize columns
save raw data with provenance
avoid live order logic
avoid training logic
```

### v1.7 - Embargo + VecNormalize Validation Hardening

Add validation hardening before retraining.

Expected deliverables:

```text
src/training_splits.py updates
VecNormalize train/eval utility
tests/test_training_splits.py updates
tests/test_vecnormalize_eval_mode.py
docs/workflows/ppo_validation_hardening.md
```

Required checks:

```text
train/eval slices do not overlap
embargo gap exists between train and eval
VecNormalize is fit only on train
eval VecNormalize does not update statistics
safe feature manifest excludes leakage columns
```

### v1.8 - Standalone Alpaca PPO Retrain

Retrain standalone PPO on Alpaca historical 1-hour bars.

Expected deliverables:

```text
new Alpaca-trained PPO artifacts
model metadata
feature manifest
VecNormalize files
training summary
out-of-sample evaluation summary
```

Training should remain standalone PPO only.

No Random Forest or XGBoost gate yet.

### v1.9 - Alpaca PPO Candidate Selection + Paper-Trading Redeploy

Repeat the validated deployment chain using the new Alpaca-trained PPO artifacts.

Expected sequence:

```text
candidate selection
manifest update
temporal stability validation
QuantConnect execution-path retest
paper-trading dry-run chain
controlled paper-order test
post-order monitoring
short monitored session
summary dashboard
```

### v2.0 - PPO + Random Forest Gate

After the standalone Alpaca-trained PPO baseline is stable, add a Random Forest gate.

Concept:

```text
Random Forest decides trade / no-trade
PPO sizes the position only after the gate allows exposure
```

### v2.1 - PPO + XGBoost Gate

After PPO + Random Forest is evaluated, add PPO + XGBoost.

Concept:

```text
XGBoost decides trade / no-trade
PPO sizes the position only after the gate allows exposure
```

### Later - Multi-Timeframe Research

Do not add this yet.

Potential future design:

```text
1-hour bars = context/features/regime
15-minute bars = execution timing or gate labels
```

This should only be evaluated after the standalone Alpaca PPO and hybrid gates are stable.

## What Not To Do Yet

Do not immediately jump to:

```text
PPO + Random Forest
PPO + XGBoost
multi-timeframe execution
unattended paper trading
full live deployment
```

Those are later phases.

## Success Criteria for the Next Major Phase

The Alpaca-trained standalone PPO baseline should be considered stable only after it has passed:

```text
Alpaca historical data ingestion
leakage-safe feature generation
embargoed train/eval split
train-only VecNormalize validation
out-of-sample walk-forward evaluation
candidate selection
manifest update
temporal stability validation
execution-path retest
paper-trading dry run
controlled paper order
post-order monitoring
short monitored session
summary dashboard
```

## Final Decision

The correct next path is:

```text
finish and seal paper-trading deployment through v1.4
document Alpaca retraining roadmap in v1.5
build Alpaca historical data loader
add embargo and VecNormalize validation hardening
retrain standalone PPO on Alpaca historical 1-hour data
redeploy and revalidate standalone PPO
only then move to PPO + RF / PPO + XGBoost hybrids
```
