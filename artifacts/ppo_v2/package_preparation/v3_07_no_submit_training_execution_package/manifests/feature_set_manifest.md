# Feature Set Manifest

```text
run_id = v3_07_no_submit_ppo_v2_training_execution_001
feature_set_defined = true
feature_generation_performed = false
training_execution_authorized = false
```

## Sealed Intended Feature Columns

- `Open`
- `High`
- `Low`
- `Close`
- `Volume`
- `return_1h`
- `log_return_1h`
- `sma_10`
- `sma_20`
- `sma_50`
- `ema_12`
- `ema_26`
- `rsi_14`
- `macd`
- `macd_signal`
- `macd_hist`
- `atr_14`
- `realized_volatility_20`
- `volume_zscore_20`
- `close_to_sma20`
- `close_to_sma50`
- `hour_sin`
- `hour_cos`
- `day_of_week_sin`
- `day_of_week_cos`

## Requirements

The future preflight must confirm:

- all feature columns exist in the sealed local input dataset
- label/target leakage columns are excluded from observations
- `Symbol` and `Datetime` remain metadata only
- holdout rows are not used for preprocessing fit
- train-only preprocessing is enforced
- forbidden observation columns are rejected

No feature generation was performed in this task.
