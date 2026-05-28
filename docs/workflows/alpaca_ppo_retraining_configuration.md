# v1.8.2 Standalone Alpaca PPO Retraining Configuration

**Date:** 2026-05-27
**Status:** Implementation checkpoint
**Scope:** Configuration only

---

## Purpose

Create a centralized configuration layer for the upcoming standalone Alpaca PPO retraining pipeline.

This checkpoint follows:

```text
v1.8.1 Alpaca PPO training dataset builder
```

This checkpoint does **not** train PPO models.

---

## Why This Exists

The project is moving from validated paper-trading deployment with existing PPO artifacts into a new standalone PPO retraining phase using Alpaca historical 1-hour data.

Before training, the retraining run must define:

* dataset path
* dataset provenance path
* artifact directory
* results directory
* symbol universe
* train/eval split settings
* embargo settings
* holdout reservation settings
* top-N candidate settings
* smoke-test vs full-training mode

---

## Main Module

```text
src/alpaca_ppo_retraining_config.py
```

---

## Generated Config

Default output:

```text
config/alpaca_ppo_retraining_config.json
```

This JSON config is safe to commit because it does not contain API keys or secrets.

---

## Default Symbols

* AAPL
* AMD
* MRK
* PFE
* UNH
* XOM

---

## Default Paths

```python
dataset_path = "data/alpaca_training/model_ready/alpaca_ppo_training_dataset.csv"

dataset_provenance_path = (
    "data/alpaca_training/model_ready/"
    "alpaca_ppo_training_dataset_provenance.json"
)

artifacts_dir = "models/alpaca_ppo_models_master"

results_dir = "reports/alpaca_ppo_retraining"
```

---

## Default Validation Settings

```python
train_fraction = 0.80
embargo_rows = 5

min_train_rows = 60
min_eval_rows = 60

holdout_fraction = 0.20
holdout_min_rows_per_symbol = 60

top_n_windows = 3

walkforward_window_size = 720
walkforward_step_size = 120
```

---

## Default Training Settings

```python
smoke_test_timesteps = 2000
training_timesteps = 100000

test_mode = True
random_seed = 42
```

These settings can be adjusted before full training.

---

## Create Config Command

```bash
python -m src.alpaca_ppo_retraining_config \
  --output-config config/alpaca_ppo_retraining_config.json \
  --create-dirs
```

---

## Strict Validation Command

Use this only after the model-ready dataset and provenance files exist:

```bash
python -m src.alpaca_ppo_retraining_config \
  --output-config config/alpaca_ppo_retraining_config.json \
  --require-dataset \
  --create-dirs
```

---

## Safety Rules

This checkpoint does **not**:

* train PPO
* select candidates
* run holdout validation
* update paper-trading manifest
* submit orders
* add Random Forest or XGBoost gates

---

## Next Step

Recommended next checkpoint:

```text
v1.8.3 Standalone Alpaca PPO training loop integration
```

Do not start full training until:

* the configuration file exists
* tests pass
* the generated config has been reviewed
