# Alpaca PPO Retraining Validation Plan

Date: 2026-05-26  
Status: Updated validation roadmap  
Scope: Standalone Alpaca PPO retraining before paper-trading redeployment

## Purpose

Document the validation sequence for retraining the standalone PPO model on Alpaca historical 1-hour data.

This plan adds a final untouched holdout period between candidate selection and paper-trading redeployment.

## Validation Hierarchy

The standalone Alpaca PPO retraining process should use the following hierarchy:

```text
train_df   = model fitting only
embargo    = skipped gap to reduce boundary leakage
eval_df    = walk-forward validation and candidate ranking
holdout_df = final untouched test period before redeployment
```

## Why Add a Final Holdout?

The existing walk-forward evaluation slice is out-of-sample relative to its training slice.

However, once eval results are used to select top-N windows by Sharpe or another score, the eval period becomes part of the model-selection process.

Therefore, selected candidates should pass a later untouched holdout period before redeployment.

## Updated Roadmap

### v1.6 Alpaca Historical Data Loader

Completed.

Purpose:

- download Alpaca historical 1-hour bars
- normalize raw bar data
- save provenance metadata
- avoid training logic

### v1.7 Embargo + VecNormalize Validation Hardening

Completed.

Purpose:

- add embargo gap between train and eval slices
- copy train-only VecNormalize stats into eval env
- lock eval env with training=False
- disable reward normalization during eval

### v1.8 Standalone Alpaca PPO Retraining Pipeline

Next implementation phase.

Purpose:

- train standalone PPO models using Alpaca historical 1-hour data
- use safe feature manifest
- use embargoed train/eval splits
- use train-only VecNormalize statistics
- save model artifacts, VecNormalize state, features, metadata, and evaluation summaries
- save top-N candidate windows by validation metrics

The v1.8 output should produce candidate models, but those candidates should not yet be redeployed.

### v1.8.5 Final Holdout Validation / Untouched Test Period

Required after v1.8.

Purpose:

- freeze selected candidate list
- evaluate candidates on a later untouched holdout period
- do not tune features, thresholds, hyperparameters, or candidate ranking on holdout
- use holdout once as final pre-redeployment validation

Candidate pass criteria should include:

- holdout Sharpe is acceptable
- holdout drawdown is controlled
- trade count is not excessive
- portfolio does not collapse
- model behavior is directionally consistent with validation behavior

If a candidate fails holdout, do not repeatedly tune against the holdout. Return to the training/validation design and create a new experiment.

### v1.9 Alpaca PPO Candidate Selection + Paper-Trading Redeployment

Purpose:

- promote only validation winners that also pass final holdout testing
- update paper-trading manifest
- rerun temporal stability validation
- rerun QuantConnect execution-path retest
- rerun dry-run checks
- rerun risk controls
- rerun controlled paper-trading validation

Definition:

```text
Candidate selection = validation winners that also pass final holdout testing
```

## What Not To Do Yet

Do not move to:

- PPO + Random Forest
- PPO + XGBoost
- multi-timeframe execution
- unattended paper trading

until the standalone Alpaca PPO baseline passes v1.8, v1.8.5, and v1.9.

## Current Decision

The correct path is:

```text
v1.8   retrain standalone Alpaca PPO candidates
v1.8.5 validate candidates on untouched holdout
v1.9   redeploy only candidates that pass validation + holdout
v2.0   then consider PPO + Random Forest
v2.1   then consider PPO + XGBoost
```
