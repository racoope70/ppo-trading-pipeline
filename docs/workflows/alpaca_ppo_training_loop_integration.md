# v1.8.3 Standalone Alpaca PPO Training Loop Integration

Date: 2026-05-28
Status: Implementation checkpoint
Scope: Training-loop integration / smoke mode

---

## Purpose

Integrate the standalone Alpaca PPO retraining configuration with the existing PPO training stack.

This checkpoint follows:

```text
v1.8.1 Alpaca PPO training dataset builder
v1.8.2 Standalone Alpaca PPO retraining configuration
```

This checkpoint proves the retraining path can load:

```text
config/alpaca_ppo_retraining_config.json
data/alpaca_training/model_ready/alpaca_ppo_training_dataset.csv
```

and prepare a controlled retraining run directory.

---

## Main Module

```text
src/alpaca_ppo_retraining_runner.py
```

---

## What This Does

The runner:

* loads the v1.8.2 config
* validates dataset/provenance paths
* loads the v1.8.1 model-ready dataset
* filters configured symbols
* validates safe feature list
* creates a timestamped run directory
* writes config snapshot
* writes config validation output
* writes dataset summary
* writes final summary
* supports dry-run mode
* supports smoke-training mode

---

## Dry-Run Command

Default mode is dry-run only:

```bash
python -m src.alpaca_ppo_retraining_runner \
  --config-path config/alpaca_ppo_retraining_config.json
```

Expected behavior:

```text
training_status = SKIPPED_DRY_RUN
```

* no PPO training occurs
* metadata files are written
* dataset compatibility is verified

---

## Smoke Training Command

Only after dry-run passes:

```bash
python -m src.alpaca_ppo_retraining_runner \
  --config-path config/alpaca_ppo_retraining_config.json \
  --train
```

This should use `smoke_test_timesteps` from the config.

---

## Full Training Command

Do not run yet unless explicitly starting the full retraining milestone:

```bash
python -m src.alpaca_ppo_retraining_runner \
  --config-path config/alpaca_ppo_retraining_config.json \
  --train \
  --full
```

---

## Outputs

Default output root:

```text
reports/alpaca_ppo_retraining/
```

Each run directory should contain:

```text
retraining_config_snapshot.json
config_validation.json
dataset_summary.json
run_summary.json
final_summary.json
alpaca_model_ready_dataset_snapshot.csv
```

If training is invoked, it may also create:

```text
training_results.json
```

---

## What This Does Not Do

This checkpoint does not:

* perform full production retraining
* run final holdout validation
* select final candidates
* update paper-trading manifest
* submit orders
* add Random Forest or XGBoost gates

---

## Safety Rules

Use dry-run first.
Use smoke training before full training.
Do not redeploy anything to paper trading after v1.8.3.

The next required milestones are:

```text
v1.8.4 Alpaca PPO retrain smoke test
v1.8.5 Final holdout validation / untouched test period
v1.9 Candidate selection + paper-trading redeployment
```
