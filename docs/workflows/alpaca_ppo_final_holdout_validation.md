# v1.8.5 Final Holdout Validation / Untouched Test Period

Date: 2026-05-28  
Status: Implementation checkpoint  
Scope: Holdout validation before candidate redeployment

## Purpose

Evaluate selected standalone Alpaca PPO candidates on a final untouched holdout period before any paper-trading redeployment.

This checkpoint follows:

```text
v1.8.1 Alpaca PPO training dataset builder
v1.8.2 Standalone Alpaca PPO retraining configuration
v1.8.3 Alpaca PPO training-loop integration
v1.8.4 Alpaca PPO retrain smoke test
```

## Why This Exists

The eval slices used during walk-forward training are out-of-sample relative to each training slice, but they are still used for candidate selection.

Once validation Sharpe or other validation metrics are used to rank/select candidate models, that validation set is no longer an unbiased final estimate.

Therefore, a later untouched holdout period is required before paper-trading redeployment.

## Main Module

```text
src/alpaca_ppo_holdout_validation.py
```

## Holdout Definition

The holdout period begins strictly after the latest `EvalEnd` found in the retraining run's `training_results.json`.

```text
holdout_start = max(training_results.EvalEnd)
holdout_df = rows where Datetime > holdout_start
```

This means holdout data is later than all walk-forward eval windows used during candidate ranking.

## Candidate Selection Rule

The module selects top-N candidates per ticker by validation Sharpe.

Default:

```text
top_n_per_symbol = config.top_n_windows
```

This mirrors the existing top-window candidate logic while keeping final holdout validation separate from candidate ranking.

## Dry-Run Command

Use this first:

```bash
python -m src.alpaca_ppo_holdout_validation \
  --config-path config/alpaca_ppo_retraining_config.json \
  --run-dir reports/alpaca_ppo_retraining/standalone_alpaca_ppo_v1_8_20260528_175838
```

Dry run checks:

- candidate selection works
- holdout rows exist
- required model artifacts exist
- summary files are written
- no PPO model is loaded
- no evaluation is performed

## Actual Holdout Evaluation Command

Only after dry-run passes:

```bash
python -m src.alpaca_ppo_holdout_validation \
  --config-path config/alpaca_ppo_retraining_config.json \
  --run-dir reports/alpaca_ppo_retraining/standalone_alpaca_ppo_v1_8_20260528_175838 \
  --evaluate
```

## Default Thresholds

```text
min_holdout_rows = 60
min_sharpe = -1.0
max_drawdown_pct = 5.0
min_final_portfolio = 95000
```

These are non-tuned safety thresholds. They should not be repeatedly adjusted against holdout performance.

## Outputs

Default output directory:

```text
<run_dir>/holdout_validation/
```

Expected files:

```text
holdout_validation_summary.json
holdout_candidate_results.csv
final_summary.json
*_holdout_predictions.csv
*_holdout_predictions_compat.csv
```

Prediction files are created only when `--evaluate` is used.

## Guardrails

This checkpoint does not:

- train PPO
- change hyperparameters
- tune thresholds based on holdout
- select final paper-trading candidates
- update paper-trading manifests
- submit orders
- add Random Forest or XGBoost gates

## Decision Rule

A candidate may move toward v1.9 only if it:

- passes final holdout checks
- has required artifacts
- has enough holdout rows
- does not collapse on holdout
- has controlled drawdown
- has acceptable holdout Sharpe under pre-defined thresholds

Candidates that fail holdout should not be tuned repeatedly on the holdout period.

## Next Step

After v1.8.5:

```text
v1.9 Alpaca PPO Candidate Selection + Paper-Trading Redeployment
```

Only candidates that pass holdout validation should be considered for paper-trading redeployment.
