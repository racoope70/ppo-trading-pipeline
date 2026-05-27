# v1.8.1 Alpaca Training Dataset Builder

Date: 2026-05-26
Status: Implementation checkpoint
Scope: Dataset builder only

---

## Purpose

Build a model-ready PPO training dataset from Alpaca historical 1-hour bars.

This checkpoint follows:

```text
v1.6 Alpaca Historical Data Loader
v1.7 Embargo + VecNormalize Validation Hardening
```

This checkpoint does not train PPO models.

---

## Input

The builder consumes normalized Alpaca historical bars created by v1.6.

Expected input columns:

```text
timestamp
symbol
open
high
low
close
volume
trade_count
vwap
```

---

## Output

The builder creates a model-ready PPO training dataset with the existing feature engineering pipeline.

Expected core output columns include:

```text
Datetime
Open
High
Low
Close
Volume
Target
Return
Symbol
```

Additional engineered features are included for model training.

---

## Safety Rule

`Target`, `Return`, `Datetime`, and `Symbol` are allowed to remain in the dataset for:

* labeling
* auditing
* grouping
* evaluation

However, they must not be included in the safe model feature list.

The builder validates that the safe feature manifest excludes:

```text
Target
Return
Datetime
Symbol
```

---

## Example Command

```bash
python -m src.data.alpaca_training_dataset \
  --input-csv data/alpaca_historical/raw/alpaca_bars_AAPL_AMD_MRK_PFE_UNH_XOM_1h_iex_20260501_20260526.csv \
  --output-csv data/alpaca_training/model_ready/alpaca_ppo_training_dataset.csv \
  --provenance-json data/alpaca_training/model_ready/alpaca_ppo_training_dataset_provenance.json
```

---

## Validation Checks

The builder verifies:

* input Alpaca columns exist
* output dataset is non-empty
* `Datetime` is parseable
* `Symbol` is present
* OHLCV values are valid
* `Target` is present
* `Return` is present
* no duplicate `Symbol/Datetime` rows exist
* safe feature list excludes leakage and metadata columns

---

## Provenance

The provenance JSON records:

```text
created_utc
input_csv
output_csv
source_rows
model_ready_rows
feature validation summary
safe feature count
target distribution
date range
symbols
```

---

## What This Does Not Do

This checkpoint does not:

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
v1.8.2 Standalone Alpaca PPO retraining configuration
```

Do not train until the dataset builder has been tested and the generated dataset has been reviewed.
