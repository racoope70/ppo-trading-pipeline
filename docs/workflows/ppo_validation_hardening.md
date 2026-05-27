# v1.7 Embargo + VecNormalize Validation Hardening

**Date:** 2026-05-26  
**Status:** Implementation checkpoint  
**Scope:** Validation hardening before Alpaca PPO retraining  

---

## Purpose

Strengthen PPO walk-forward validation before retraining the standalone PPO model on Alpaca historical 1-hour data.

This checkpoint does **not** retrain PPO. It improves validation safety before the next standalone PPO retraining phase.

---

## Why This Matters

The project already fixed the major same-window validation issue by training on an earlier slice and evaluating on a later slice.

v1.7 adds two additional safeguards:

```text
1. Embargo gap between train and evaluation slices
2. Explicit VecNormalize train-only statistics and eval-mode locking
```

---

## Embargo Gap

A configurable embargo gap is now supported between train and evaluation slices.

### Concept

```text
train_slice    = rows used for PPO fitting
embargo_slice  = skipped rows between train and eval
eval_slice     = rows used only for out-of-sample evaluation
```

### Purpose

- reduce boundary leakage from rolling indicators
- reduce boundary leakage from forward-return labels
- reduce normalization-related boundary effects
- make out-of-sample evaluation more conservative

### Training CLI Support

```bash
python -m src.train --embargo-rows 5
```

---

## VecNormalize Hardening

Evaluation environments must use normalization statistics fit from the training environment only.

### Required Behavior

```text
train VecNormalize fits obs/return statistics during training
eval VecNormalize receives copied train statistics
eval_env.training = False
eval_env.norm_reward = False
eval data does not update normalization statistics
```

### Implemented Helper

```text
src/vecnormalize_utils.py
```

### Core Functions

```python
configure_eval_vecnormalize(...)
assert_eval_vecnormalize_locked(...)
```

---

## Updated Training Metadata

Walk-forward output metadata now records:

```text
TrainRows
EmbargoRows
EvalRows
TrainStart
TrainEnd
EvalStart
EvalEnd
```

This makes the validation boundary auditable.

---

## Tests

v1.7 adds or updates tests for:

- non-overlapping train/eval slices
- embargo row count
- embargo ordering
- embargo consuming too much eval data
- VecNormalize train-stat copying
- VecNormalize eval mode locking
- reward normalization disabled during eval

---

## What This Does Not Do

This checkpoint does **not**:

- download new Alpaca training data
- train PPO models
- change paper-trading manifest
- add Random Forest or XGBoost gates
- run live/paper orders

---

## Next Step

Recommended next checkpoint:

```text
v1.8 Standalone Alpaca PPO retrain preparation
```

The model should **not** be retrained until:

- Alpaca historical data loader is complete
- embargo split is tested
- VecNormalize eval behavior is tested
- safe feature manifest remains enforced