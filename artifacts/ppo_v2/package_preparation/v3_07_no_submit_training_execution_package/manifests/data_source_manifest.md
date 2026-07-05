# Data Source Manifest

```text
run_id = v3_07_no_submit_ppo_v2_training_execution_001
data_source_defined = true
data_fetching_authorized = false
dataset_generation_authorized = false
training_execution_authorized = false
```

## Intended Data Source

```text
provider = Alpaca historical bars
bar_interval = 1h
hours_policy = regular_session_only_unless_future_review_explicitly_authorizes_otherwise
input_mode = pre_existing_local_input_only
sealed_input_dataset = data/processed/ppo_v2/v3_07_no_submit_training_input.parquet
```

This package does not fetch data and does not create the dataset.

## Future Preflight Requirements

The future authorization review must confirm:

- the sealed local input dataset exists before execution is authorized
- data source provenance is documented
- no unreviewed data-fetching step is introduced
- raw required columns are present
- `Datetime` is parseable and timezone-consistent
- `Symbol` values are non-null and limited to the sealed ticker universe
- OHLCV values are numeric and non-negative
- OHLC consistency passes
- duplicate `Symbol` / `Datetime` rows are rejected
