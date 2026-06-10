# PROJECT_CONTEXT.md

Authoritative reference document for `racoope70/ppo-trading-pipeline`.

This document defines the current system architecture, validation standards, deployment constraints, research progression, operational guardrails, and active development state for the PPO trading pipeline.

It should be reviewed before modifying training logic, validation methodology, deployment workflows, artifact management, or broker integration behavior.

---

# 1. Current Development State

## Active Operational Milestone

`v1.30 Candidate Stability Review / No-Submit Fresh Cycle`

## Status

IN PROGRESS

## Latest Completed Paper-Trading Milestone

`v1.29 Signal Persistence / Candidate Stability Policy`

Latest paper-trading policy checkpoint:

```txt
A one-time candidate is not trade approval.
A candidate must be revalidated on a fresh future run before any controlled submit decision.
Changed symbol/side/default uncertainty = NO-SUBMIT.
```

Current documented local test status from the latest paper-trading decision cycle:

```txt
210 passed, 2 warnings
```

Known non-blocking warnings:

* websockets.legacy deprecation warning
* protobuf utcfromtimestamp deprecation warning

## Current Paper-Trading Source of Truth

Before making any paper-trading recommendation, review these files first:

```txt
docs/workflows/signal_persistence_candidate_stability_policy.md
docs/workflows/paper_trading_session_policy.md
docs/runs/paper_trading_decision_dashboard.md
docs/runs/v1.28_controlled_single_order_submit_decision.md
docs/runs/v1.29_signal_persistence_candidate_stability_policy.md
```

Important context:

```txt
v1.27 candidate = UNH sell
v1.28 fresh candidate = AMD buy
v1.28 decision = NO-SUBMIT
v1.29 policy = candidate persistence required before controlled submit review
v1.30 next step = fresh no-submit candidate stability review
```

Do not rely on stale checkpoint candidates. Do not submit from prior checkpoint plans.

---

# 2. Current Objective

Current operational focus:

Run a fresh no-submit paper-trading cycle under the v1.29 signal-persistence policy and classify the current candidate state as:

```txt
new
persistent
changed
absent
```

This phase establishes:

* fresh-run discipline
* candidate persistence review
* no-submit default behavior
* stale-plan prevention
* single-order review discipline
* risk-control and checklist enforcement
* broker-state verification
* auditable paper-trading decisions

A controlled paper submit is not the current default objective.

Any future controlled submit requires a separate decision checkpoint after the full safety stack passes.

## Parallel Research Track

The longer-term research track remains:

Develop and validate a standalone PPO baseline trained on Alpaca historical 1-hour bars using embargo-aware walk-forward evaluation.

This research track includes:

* reproducible retraining configuration
* artifact isolation
* validation consistency
* retraining governance
* holdout reservation standards
* deployment separation from previously validated models

Full retraining, model promotion, and hybrid model work must not bypass paper-trading or holdout-validation guardrails.

---

# 3. Strategic Research Direction

## Near-Term Operational Objective

Continue supervised Alpaca paper-trading monitoring with no-submit default behavior.

Next operational checkpoint:

```txt
v1.30 Candidate Stability Review / No-Submit Fresh Cycle
```

The goal is to determine whether the latest model-generated candidate is new, persistent, changed, or absent. It is not to force a trade.

---

## Near-Term Research Objective

Develop and validate a standalone PPO baseline trained on Alpaca historical 1-hour bars using embargo-aware walk-forward evaluation.

Promotion requirements:

* out-of-sample validation
* untouched holdout validation
* deployment review
* supervised paper-trading verification
* candidate stability review
* manual approval before any controlled paper submit

---

## Medium-Term Objective

After standalone PPO stabilization:

```txt
PPO
  ↓
PPO + Random Forest gate
  ↓
PPO + XGBoost gate
```

Hybrid systems should only be evaluated after the standalone Alpaca PPO baseline has completed retraining, validation, holdout review, and supervised paper deployment review.

Do not move to hybrid systems prematurely.

---

# 4. Validation Hierarchy

Validation hierarchy must remain strictly enforced:

```txt
train_df   = model fitting only
embargo    = temporal gap
eval_df    = walk-forward evaluation
holdout_df = untouched final validation
```

Rules:

* no temporal overlap
* no leakage
* holdout isolation required
* evaluation uses locked train-only normalization statistics
* no repeated tuning against holdout
* no model promotion without deployment review

---

# 5. Core System Architecture

```txt
Market Data Layer
    ↓
Feature Engineering Layer
    ↓
Safe Feature Manifest
    ↓
PPO Training Layer
    ↓
Validation + Candidate Selection
    ↓
Paper-Trading Dry Run
    ↓
Dry-Run Evaluation
    ↓
Execution Plan
    ↓
Risk Controls
    ↓
Pre-Trade Checklist
    ↓
Supervised Paper-Order Runner
    ↓
Broker Verification
    ↓
Audit + Monitoring
    ↓
Decision Documentation
```

The architecture is intentionally staged so that model output is never treated as immediate trade approval.

---

# 6. Critical Modules

## Data Layer

```txt
src/data/alpaca_historical_data.py
src/data/alpaca_training_dataset.py
```

Responsibilities:

* Alpaca historical ingestion
* normalization
* provenance tracking
* model-ready dataset generation

---

## Feature Engineering

```txt
src/features.py
src/feature_manifest.py
```

Responsibilities:

* technical indicators
* regime features
* denoising
* target labeling
* safe feature selection
* leakage prevention

---

## Training + Validation

```txt
src/train.py
src/training_splits.py
src/vecnormalize_utils.py
src/env.py
```

Responsibilities:

* walk-forward PPO training
* embargo enforcement
* VecNormalize management
* candidate tracking
* evaluation isolation

---

## Alpaca Adapter Layer

```txt
src/adapters/alpaca.py
```

Responsibilities:

* paper-account connection
* Alpaca endpoint enforcement
* account snapshots
* position reads
* recent bar downloads
* latest price lookup
* controlled market-order helper
* no live-money endpoint usage for paper-trading workflows

Required Alpaca endpoint:

```txt
https://paper-api.alpaca.markets
```

---

## Paper-Trading Deployment Layer

```txt
src/paper_trading/paper_trade_dry_run.py
src/paper_trading/evaluate_dry_run.py
src/paper_trading/build_execution_plan.py
src/paper_trading/risk_controls.py
src/paper_trading/filter_execution_plan.py
src/paper_trading/paper_trade_loop.py
src/paper_trading/pre_trade_checklist.py
src/paper_trading/logging_utils.py
```

Responsibilities:

* broker-connected no-order dry-run inference
* dry-run validation
* execution-plan generation
* single-order filtering
* risk-control enforcement
* stale-plan prevention
* explicit run-directory confirmation
* supervised Alpaca paper-order submission only when intentionally approved
* broker-state verification
* audit logging

---

# 7. Safe Feature Standards

The following fields must never enter model feature inputs:

```txt
Target
Return
Datetime
Symbol
```

These columns are permitted for:

* labeling
* evaluation
* grouping
* auditing
* reporting

Leakage prevention is enforced through:

```txt
src/feature_manifest.py
```

---

# 8. Current PPO Workflow

Current training workflow:

1. construct walk-forward window
2. split into train / embargo / eval
3. train PPO on train only
4. persist VecNormalize train statistics
5. evaluate using locked eval statistics
6. rank candidate windows
7. save metrics and artifacts
8. reserve untouched holdout for final validation
9. deploy only after review

Evaluation constraints:

```txt
eval_env.training = False
eval_env.norm_reward = False
```

---

# 9. Current Paper-Trading Workflow

Normal monitoring cycle is no-submit by default:

```bash
python -m src.paper_trading.paper_trade_dry_run \
  --manifest config/paper_trading_six_ticker_manifest.json \
  --artifacts-dir models/alpaca_ppo_models_master

python -m src.paper_trading.evaluate_dry_run \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.build_execution_plan \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.risk_controls \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.pre_trade_checklist \
  --run-dir reports/paper_trading_dry_runs/latest \
  --check-broker \
  --expected-equity 100000 \
  --equity-tolerance-pct 0.05 \
  --allow-open-positions
```

Expected no-submit pass conditions:

```txt
Evaluation result = PASS
Risk result = PASS
Checklist result = PASS
predict_ok_count = expected universe size
error_count = 0
orders_submitted = 0
submit_orders = False
broker_open_orders_zero = PASS
broker_snapshot_errors_empty = PASS
```

Hard stop conditions:

```txt
dry-run evaluation fails
risk controls fail
pre-trade checklist fails
broker open orders are unexpected
execution plan is stale
market data is unavailable
candidate changed unexpectedly
orders_required > 1 and no single-order filter was used
manual approval is missing
```

---

# 10. Candidate Stability Policy

Current active policy:

```txt
docs/workflows/signal_persistence_candidate_stability_policy.md
```

Core rule:

```txt
A candidate must be revalidated on a fresh future run before any submit decision.
Do not submit from a prior checkpoint's execution plan.
Do not assume a prior candidate remains valid.
```

Candidate definition:

```txt
should_order = True
side in {buy, sell}
orders_required >= 1
```

Changed candidate conditions:

```txt
symbol changes
side changes
candidate disappears
orders_required changes from 1 to multiple
candidate becomes below_min_notional
risk fails
checklist fails
plan becomes stale
```

Candidate stability levels:

```txt
Level 0 = one-time candidate; review only
Level 1 = revalidated candidate; eligible for controlled review
Level 2 = submit-eligible candidate; requires full safety stack and manual approval
```

Default action when uncertain:

```txt
NO-SUBMIT
```

---

# 11. Controlled Submit Requirements

Controlled paper submits are not automatic.

A controlled submit may only be considered after all conditions below are true:

```txt
fresh dry run completed
dry-run evaluation passed
execution plan rebuilt from the fresh dry run
candidate persisted or was freshly revalidated
orders_required = 1, or a reviewed single-order filtered directory exists
risk controls passed
pre-trade checklist passed
plan_not_stale = PASS
execution_plan_not_stale = PASS
broker open orders = 0
selected order is explicitly identified
manual review completed
manual approval is explicit
post-submit broker verification is planned
```

Submit command pattern:

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir <reviewed_single_order_run_dir> \
  --submit-orders \
  --max-plan-age-minutes 90 \
  --confirm-run-dir <reviewed_single_order_run_dir>
```

Never use `--submit-orders` against an old checkpoint plan.

Never use `--submit-orders` against `reports/paper_trading_dry_runs/latest` when the original plan has more than one eligible order.

Never treat risk/checklist pass as trade approval by itself.

---

# 12. Current Training Parameters

Defined in:

```txt
src/env.py
```

Current operational parameters:

```txt
window_size=10
cost_rate=0.0002
slip_rate=0.0003
k_alpha=0.20
k_mom=0.05
mom_lookback=20
min_trade_delta=0.01
cooldown=5
reward_clip=1.0
```

---

# 13. Canonical Data Source

Current retraining source:

```txt
Alpaca historical 1-hour stock bars
```

Canonical baseline universe:

```txt
AAPL
AMD
MRK
PFE
UNH
XOM
```

---

# 14. Artifact Governance

Validated artifacts must not be overwritten.

Current validated artifact directory:

```txt
models/ppo_models_master
```

Current Alpaca PPO paper-trading artifact directory:

```txt
models/alpaca_ppo_models_master
```

Expected isolated retraining directories:

```txt
models/alpaca_ppo_models_master
reports/alpaca_ppo_retraining
```

Generated datasets, model artifacts, run outputs, reports, logs, and credentials should remain excluded from version control unless intentionally documented otherwise.

---

# 15. Deployment Constraints

Current deployment policy:

* supervised paper trading only
* no real-money trading
* no unattended execution
* no automatic multi-order submission
* no stale-plan submission
* no forced cleanup of residual positions
* no automatic exits after recent entries
* manual order review required
* broker-state verification required
* audit logging required
* documentation required for milestone decisions

Approved behavior:

```txt
supervised no-submit cycles
controlled one-order paper submit tests
single-order filtered submit tests
post-submit monitoring
residual position monitoring
candidate stability review
decision logging
```

Not approved:

```txt
unattended trading
real-money trading
automatic multi-order submission
submitting stale candidates
submitting changed candidates
submitting from prior checkpoint plans
forced residual cleanup
automatic entries
automatic exits
```

---

# 16. Testing + CI Standards

Primary local test command:

```bash
../.venv/bin/python -m pytest
```

Requirements before milestone promotion:

* local tests passing
* GitHub Actions passing when available
* clean git state
* reviewed artifact changes
* no generated datasets committed
* no credentials committed
* paper-trading docs updated after operational milestones

CI workflow:

```txt
.github/workflows/tests.yml
```

---

# 17. Repository Standards

Expected repository root:

```txt
ppo_research_pipeline/
```

Before modifications:

```bash
pwd
git rev-parse --show-toplevel
git status --short
```

Files must not be created outside:

```txt
ppo_research_pipeline
```

---

# 18. Generated Data Policy

Generated data must remain excluded from version control.

Ignored paths:

```txt
data/raw/*
data/processed/*
data/alpaca_historical/*
data/alpaca_training/*
reports/*
logs/*
models/*
```

Large artifacts generally excluded:

```txt
*.zip
*.pt
*.pth
*.onnx
*.joblib
*.pkl
*.csv
```

Never commit:

```txt
.env
.env.*
API keys
broker credentials
raw account exports
large generated run outputs
```

---

# 19. Active Deliverables

Current operational deliverables:

```txt
v1.30 Candidate Stability Review / No-Submit Fresh Cycle
fresh no-submit paper-trading run documentation
candidate classification: new / persistent / changed / absent
risk-control result
pre-trade checklist result
broker-state verification
next decision classification
```

Current hardening candidates before any future controlled submit:

```txt
make submit mode fail closed if broker account/positions/open-order reads fail
add runner-level max_orders_to_submit=1 default
add post-submit order-status reconciliation by order id
keep PROJECT_CONTEXT.md aligned with latest paper-trading policy
```

Longer-term research deliverables:

```txt
src/config/alpaca_ppo_retraining_config.py
tests/test_alpaca_ppo_retraining_config.py
docs/workflows/alpaca_ppo_retraining_configuration.md
standalone Alpaca PPO training integration
Alpaca PPO retrain smoke test
final holdout validation
```

---

# 20. Planned Milestones

Operational paper-trading milestones:

```txt
v1.30 Candidate Stability Review / No-Submit Fresh Cycle
v1.31 Submit-mode hardening: broker fail-closed + max one order
v1.32 Post-submit order-status reconciliation
```

Research milestones:

```txt
Standalone Alpaca PPO training integration
Alpaca PPO retrain smoke test
Final holdout validation
Alpaca PPO paper-trading redeployment review
PPO + Random Forest gate
PPO + XGBoost gate
```

Hybrid model milestones must remain blocked until standalone PPO validation and supervised deployment review are complete.

---

# 21. Operational Guardrails

Do not:

* bypass holdout validation
* repeatedly tune against holdout
* overwrite validated artifacts
* commit generated datasets
* commit credentials
* enable unattended execution
* move to hybrid systems prematurely
* submit paper orders without review
* submit stale candidates
* submit changed candidates
* submit from prior checkpoint plans
* submit from unfiltered multi-order plans
* treat candidate identification as trade approval
* treat risk/checklist pass as trade approval by itself

When in doubt:

```txt
NO-SUBMIT
rerun a fresh dry run
review the execution plan
verify broker state
document the decision
```

---

# 22. Maintenance Requirements

Update this document when:

* milestones complete
* validation methodology changes
* deployment workflows change
* schemas change
* architecture changes
* operational constraints change
* artifact structure changes
* paper-trading policy changes
* latest candidate decision changes
* test status changes

This document functions as the authoritative operational and research reference for the repository.
