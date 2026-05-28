# PROJECT_CONTEXT.md

Authoritative reference document for `racoope70/ppo-trading-pipeline`.

This document defines the current system architecture, validation standards, deployment constraints, research progression, operational guardrails, and active development state for the PPO trading pipeline.

It should be reviewed before modifying training logic, validation methodology, deployment workflows, artifact management, or broker integration behavior.

---

# 1. Current Development State

## Active Milestone

`v1.8.2 Standalone Alpaca PPO Retraining Configuration`

## Status

IN PROGRESS

## Latest Completed Milestone

`v1.8.1 Alpaca PPO Training Dataset Builder`

Commit:

```txt id="7lfj48"
f89208b Add Alpaca PPO training dataset builder
```

Current local test status:

```txt id="sdf8fb"
160 passed, 2 warnings
```

Known non-blocking warnings:

* websockets.legacy deprecation warning
* protobuf utcfromtimestamp deprecation warning

---

# 2. Current Objective

Current development focus:

Build the retraining configuration layer for standalone Alpaca PPO retraining using historical 1-hour Alpaca market data.

This phase establishes:

* reproducible retraining configuration
* artifact isolation
* validation consistency
* retraining governance
* holdout reservation standards
* deployment separation from previously validated models

Full retraining is not part of this milestone.

---

# 3. Strategic Research Direction

## Near-Term Objective

Develop and validate a standalone PPO baseline trained on Alpaca historical 1-hour bars using embargo-aware walk-forward evaluation.

Promotion requirements:

* out-of-sample validation
* untouched holdout validation
* deployment review
* supervised paper-trading verification

---

## Medium-Term Objective

After standalone PPO stabilization:

```txt id="6vxwt2"
PPO
  ↓
PPO + Random Forest gate
  ↓
PPO + XGBoost gate
```

Hybrid systems should only be evaluated after the standalone Alpaca PPO baseline has completed retraining, validation, and supervised paper deployment review.

---

# 4. Validation Hierarchy

Validation hierarchy must remain strictly enforced:

```txt id="xhz7tt"
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

---

# 5. Core System Architecture

```txt id="2r8v3v"
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
Paper-Trading Deployment
    ↓
Broker Verification
    ↓
Audit + Monitoring
```

---

# 6. Critical Modules

## Data Layer

```txt id="5mjlwm"
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

```txt id="nl20nk"
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

```txt id="qm3eky"
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

## Deployment Layer

```txt id="5s6v0x"
src/paper_trading/
```

Responsibilities:

* dry-run execution
* execution planning
* risk controls
* broker-state verification
* supervised Alpaca paper trading

---

# 7. Safe Feature Standards

The following fields must never enter model feature inputs:

```txt id="vst4mk"
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

```txt id="0z72rm"
src/feature_manifest.py
```

---

# 8. Current PPO Workflow

Current workflow:

1. construct walk-forward window
2. split into train / embargo / eval
3. train PPO on train only
4. persist VecNormalize train statistics
5. evaluate using locked eval statistics
6. rank candidate windows
7. save metrics and artifacts

Evaluation constraints:

```txt id="h2x0g3"
eval_env.training = False
eval_env.norm_reward = False
```

---

# 9. Current Training Parameters

Defined in:

```txt id="79hl8n"
src/env.py
```

Current operational parameters:

```txt id="yjj1n5"
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

# 10. Canonical Data Source

Current retraining source:

```txt id="2ob57y"
Alpaca historical 1-hour stock bars
```

Canonical baseline universe:

```txt id="s3d0m0"
AAPL
AMD
MRK
PFE
UNH
XOM
```

---

# 11. Artifact Governance

Validated artifacts must not be overwritten.

Current validated artifact directory:

```txt id="0grqtx"
models/ppo_models_master
```

Expected isolated retraining directories:

```txt id="pq6tp7"
models/alpaca_ppo_models_master
reports/alpaca_ppo_retraining
```

---

# 12. Deployment Constraints

Current deployment policy:

* supervised paper trading only
* manual order review required
* broker state verification required
* no unattended execution

Required Alpaca endpoint:

```txt id="x6r1lu"
https://paper-api.alpaca.markets
```

---

# 13. Testing + CI Standards

Primary local test command:

```txt id="bt8zdn"
../.venv/bin/python -m pytest
```

Requirements before milestone promotion:

* local tests passing
* GitHub Actions passing
* clean git state
* reviewed artifact changes

CI workflow:

```txt id="5j7q4l"
.github/workflows/tests.yml
```

---

# 14. Repository Standards

Expected repository root:

```txt id="ic7w8e"
ppo_research_pipeline/
```

Before modifications:

```txt id="ol4u7t"
pwd
git rev-parse --show-toplevel
git status --short
```

Files must not be created outside:

```txt id="ujjjsy"
ppo_research_pipeline
```

---

# 15. Generated Data Policy

Generated data must remain excluded from version control.

Ignored paths:

```txt id="eg2bnm"
data/raw/*
data/processed/*
data/alpaca_historical/*
data/alpaca_training/*
```

Large artifacts generally excluded:

```txt id="7tcfz5"
*.zip
*.pt
*.pth
*.onnx
*.joblib
```

---

# 16. Active Deliverables

Current milestone deliverables:

```txt id="0e8h5n"
src/config/alpaca_ppo_retraining_config.py
tests/test_alpaca_ppo_retraining_config.py
docs/workflows/alpaca_ppo_retraining_configuration.md
```

Configuration layer should define:

* dataset paths
* artifact paths
* results paths
* embargo settings
* train/eval settings
* holdout settings
* smoke-test mode
* candidate-selection settings

---

# 17. Planned Milestones

```txt id="ol0z3y"
v1.8.3 Standalone Alpaca PPO training integration
v1.8.4 Alpaca PPO retrain smoke test
v1.8.5 Final holdout validation
v1.9   Alpaca PPO paper-trading redeployment
v2.0   PPO + Random Forest gate
v2.1   PPO + XGBoost gate
```

---

# 18. Operational Guardrails

Do not:

* bypass holdout validation
* repeatedly tune against holdout
* overwrite validated artifacts
* commit generated datasets
* enable unattended execution
* move to hybrid systems prematurely
* submit paper orders without review

---

# 19. Maintenance Requirements

Update this document when:

* milestones complete
* validation methodology changes
* deployment workflows change
* schemas change
* architecture changes
* operational constraints change
* artifact structure changes

This document functions as the authoritative operational and research reference for the repository.
