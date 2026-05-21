# Research Hardening Roadmap

This roadmap tracks model-research issues that should be addressed before claiming stronger validation, running temporal stability tests, using QuantConnect as a broader execution comparison, or running longer Alpaca paper-trading sessions.

The current deployment safety chain is strong:

```text
dry run
dry-run evaluator
execution-plan builder
risk-control report
guarded paper-order runner
automatic audit log generation
pre-trade checklist
zero orders submitted by default
```

However, the research layer still needs hardening before stronger performance claims are made.

---

## Current Completed Safety Milestones

```text
v0.3 = Alpaca paper-trading safety chain
v0.4 = Risk-controlled paper runner
v0.5 = Audit logging integrated into paper_trade_loop.py
v0.6 Step 1 = Pre-trade checklist utility
v0.7 = Research-hardened PPO training pipeline
```

Current safety status:

```text
pre-trade checklist passes
broker check passes
paper account equity near $100,000
cash available
positions flat
open orders zero
risk controls pass
audit log generated
default mode submits zero orders
```

---

## v0.7 Research Hardening Completed

The first research-hardening phase is complete.

Completed fixes:

```text
1. Train/evaluate same-window issue fixed
2. Return/Target leakage risk reduced through safe feature manifest
3. Parent env hold-action fragility addressed with compatibility checks
```

Implemented commits:

```text
707dcaa Add out-of-sample train eval split for PPO windows
8b49560 Use safe feature manifest in PPO training
76c3bb3 Add parent environment action compatibility checks
```

Current validation status:

```text
109 passed, 1 warning
```

The remaining warning is a third-party websockets.legacy deprecation warning and does not indicate a project failure.

Next step:

Retrain the six-ticker PPO baseline using the hardened research pipeline.

---

## Priority 1: Train/Evaluate Same Window

### Current concern

The current PPO walk-forward training flow trains on a window and evaluates on the same window.

Current pattern:

```text
df_window = df.iloc[start:end]
train PPO on df_window
evaluate PPO on df_window
```

This is useful as a training diagnostic, but it is not true out-of-sample validation.

### Why it matters

If training and evaluation happen on the same slice, reported Sharpe, drawdown, winner, and portfolio metrics can overstate real generalization.

### Required fix

Split each walk-forward window into separate train and evaluation slices:

```text
window = df.iloc[start:end]

train_slice = earlier portion of window
eval_slice = later portion of window

train PPO on train_slice
evaluate PPO on eval_slice only
save metrics from eval_slice only
```

### Acceptance criteria

```text
Training rows are strictly earlier than evaluation rows.
Evaluation rows are never used by PPO during training.
Saved metrics are based only on evaluation rows.
Prediction files clearly identify evaluation period.
Tests prove train/eval timestamps do not overlap.
```

### Proposed files

```text
src/training_splits.py
tests/test_training_splits.py
```

---

## Priority 2: Leakage Risk from Return and Target

### Current concern

The feature pipeline creates future-looking columns:

```text
Return
Target
```

These are useful labels, but they should not be included in PPO observation features or saved model feature lists.

### Why it matters

`Return` is calculated using future close prices. `Target` is derived from that future return. If either is present in the model observation space or saved artifact feature list, it creates leakage risk.

### Required fix

Create an explicit safe feature manifest.

Always exclude:

```text
Return
Target
Symbol
Datetime
any label column
any future-looking diagnostic column
metadata columns
```

### Acceptance criteria

```text
PPO environment receives only safe feature columns.
Saved artifact feature list contains only safe model inputs.
Return is not in saved features.
Target is not in saved features.
Datetime is not in saved features.
Symbol is not in saved features.
Tests fail if any forbidden column appears in model features.
```

### Proposed files

```text
src/feature_manifest.py
tests/test_feature_manifest.py
```

---

## Priority 3: Parent Env Hold Action Fragility

### Current concern

The custom environment advances the parent `gym-anytrading` environment using:

```text
super().step(2)
```

This assumes that action value `2` is accepted by the parent environment as a hold/advance action.

### Why it matters

If the parent action mapping changes across `gym-anytrading` versions, the environment could become fragile or behave differently than expected.

### Required fix

Either:

```text
Option A: add a compatibility test proving action 2 works with the current dependency version
Option B: refactor parent stepping so it does not rely on a magic action value
```

### Acceptance criteria

```text
Environment tests confirm reset and step behavior.
Parent step compatibility is tested.
Action mapping assumptions are documented.
No hidden dependency on an untested magic action remains.
```

### Proposed file

```text
tests/test_env_parent_step_compatibility.py
```

---

## Recommended Sequence

```text
1. Add pre_trade_checklist.py
2. Create this research hardening roadmap
3. Fix train/evaluate same-window issue
4. Add explicit safe feature manifest
5. Fix or test parent environment hold action
6. Retrain six-ticker baseline
7. Rerun validation chain
8. Run temporal stability validation on a later market period
9. Retest QuantConnect execution path
10. Run one controlled intentional Alpaca paper-order test
```

---

## What Not To Do Yet

Do not treat the current PPO metrics as final out-of-sample performance.

Do not run a full paper-trading campaign before the research-hardening issues are addressed or explicitly documented as known limitations.

Do not use QuantConnect retesting as a substitute for fixing train/eval separation or feature leakage risk.

Do not use `--submit-orders` unless the pre-trade checklist, risk controls, and audit logging all pass.

---

## Current Safety Rule

```text
Default mode submits no orders.
Real Alpaca paper orders require --submit-orders.
Risk controls must pass before submit-orders mode.
Audit logs must record risk and order-submission state.
Pre-trade checklist should pass before any intentional submit-order test.
```
