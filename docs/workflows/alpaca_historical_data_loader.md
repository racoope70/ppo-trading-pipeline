# v1.6 Alpaca Historical Data Loader

Date: 2026-05-26  
Status: Implementation checkpoint  
Scope: Data ingestion only

## Purpose

Create a dedicated Alpaca historical-data loader for the next standalone PPO
retraining phase.

This is the first implementation step after the v1.5 Alpaca historical-data PPO
retraining roadmap.

## Scope

This checkpoint handles only historical data ingestion.

It does not:

```text
train PPO models
change the paper-trading manifest
submit orders
modify risk controls
introduce Random Forest or XGBoost gates
```

## Module

```text
src/data/alpaca_historical_data.py
```

Responsibilities:

```text
connect to Alpaca historical data using .env keys
download historical stock bars
support 1-hour bars for the standalone PPO baseline
normalize alpaca-py output into stable columns
validate raw bar data
save CSV output
save provenance metadata
```

## Standard Output Columns

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

## Default Universe

The first retraining baseline should continue with the six-ticker deployment
universe:

```text
AAPL
AMD
MRK
PFE
UNH
XOM
```

## Example Download Command

```bash
python -m src.data.alpaca_historical_data \
  --symbols AAPL AMD MRK PFE UNH XOM \
  --start 2024-01-01 \
  --end 2026-05-26 \
  --timeframe 1H \
  --feed iex \
  --output-dir data/alpaca_historical/raw
```

## Expected Outputs

```text
data/alpaca_historical/raw/alpaca_bars_<SYMBOLS>_1h_iex_<START>_<END>.csv
data/alpaca_historical/raw/alpaca_bars_<SYMBOLS>_1h_iex_<START>_<END>_provenance.json
```

## Provenance Metadata

Each downloaded dataset saves metadata including:

```text
created_utc
source
symbols
start
end
timeframe
feed
rows
columns
validation result
notes
```

## Validation Rules

The loader checks:

```text
required columns exist
data is non-empty
timestamps are valid
symbols are valid
no duplicate symbol/timestamp rows
expected symbols are present
OHLC fields are valid
```

## Why This Matters

The prior PPO artifacts were validated through the Alpaca paper-trading
deployment process.

The next model-quality phase requires retraining PPO using Alpaca historical
data so the training source better aligns with:

```text
paper-trading inference bars
Alpaca broker environment
future deployment data path
```

This does not guarantee better performance, but it improves consistency and
auditability.

## Next Step

Recommended next checkpoint:

```text
v1.7 Embargo + VecNormalize Validation Hardening
```
