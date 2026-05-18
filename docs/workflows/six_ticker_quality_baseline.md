# Six-Ticker Quality Baseline Workflow

## Objective

This document defines the reproducible validation path for the six-ticker PPO quality baseline.

The purpose is to preserve the exact command sequence used to regenerate the selected data set, training artifacts, execution-realism diagnostics, LEAN-compatible signal payload, payload manifest, local mark-to-market simulation, and validation comparison summary.

The workflow avoids manual edits to `src/config.py` by using explicit CLI overrides. This keeps the research process auditable and reduces the risk of comparing artifacts from inconsistent ticker universes or run directories.

---

## Baseline Universe

Current baseline universe:

```text
AAPL, PFE, UNH, XOM, AMD, MRK
```

The six-ticker set was selected after comparing the four-ticker and eight-ticker dynamic signal simulations.

Excluded from the eight-ticker expansion:

```text
META, ORCL
```

Rationale: META and ORCL did not pass the moderate execution-realism filter. Their best moderate-scenario result favored Buy & Hold over PPO, so they were excluded from the quality-filtered baseline.

---

## Current Baseline Result

Six-ticker local mark-to-market simulation:

| Metric                 |      Value |
| ---------------------- | ---------: |
| Final equity           | 112,982.27 |
| Net PnL                |  12,982.27 |
| Net return             |     12.98% |
| Gross PnL before costs |  14,983.23 |
| Transaction costs      |   2,000.96 |
| Sharpe estimate        |       3.80 |
| Max drawdown           |      8.96% |
| Total turnover         |    36.8929 |
| Trade events           |        198 |
| Simulation rows        |        250 |

Comparison across validation sets:

| Validation set                        | Final equity | Net return | Sharpe estimate | Max drawdown | Trade events |
| ------------------------------------- | -----------: | ---------: | --------------: | -----------: | -----------: |
| UNH/XOM local MTM                     |   107,004.06 |      7.00% |            2.78 |        6.59% |           46 |
| Four-ticker selected local MTM        |   108,909.18 |      8.91% |            3.40 |        6.49% |          184 |
| Eight-ticker selected local MTM       |   107,686.02 |      7.69% |            2.03 |       10.19% |          547 |
| Six-ticker quality-filtered local MTM |   112,982.27 |     12.98% |            3.80 |        8.96% |          198 |

Conclusion: the six-ticker quality-filtered simulation is the primary local validation baseline.

---

## Reproducible Command Sequence

### 1. Confirm clean repository state

```bash
git status --short
```

Expected: no output.

---

### 2. Prepare feature-engineered data

```bash
python -m src.prepare_data \
  --tickers AAPL PFE UNH XOM AMD MRK
```

Expected log:

```text
Preparing data for 6 symbols: ['AAPL', 'PFE', 'UNH', 'XOM', 'AMD', 'MRK']
```

Primary outputs:

```text
data/processed/multi_stock_feature_engineered_dataset.csv
data/processed/train.csv
data/processed/val.csv
data/processed/features_full.parquet
data/processed/train.parquet
data/processed/val.parquet
```

---

### 3. Train PPO walk-forward models

```bash
python -m src.train \
  --tickers AAPL PFE UNH XOM AMD MRK
```

Expected log:

```text
Running in TEST_MODE on symbols: ['AAPL', 'PFE', 'UNH', 'XOM', 'AMD', 'MRK']
```

Training outputs are written to:

```text
reports/backtests/ppo_walkforward_results_<timestamp>/
```

Expected files:

```text
summary_test_mode.csv
*_predictions.csv
*_predictions_compat.csv
skipped_windows_global.csv
```

Note: if existing model artifacts are already present, some windows may be skipped. Confirm that the intended run folder still contains the required summary and prediction compatibility files.

---

### 4. Run execution-realism analysis

```bash
python -m src.analyze_execution_realism \
  --run-dir reports/backtests/ppo_walkforward_results_<timestamp>
```

Expected output:

```text
reports/backtests/ppo_walkforward_results_<timestamp>/execution_realism_analysis.csv
```

For the documented six-ticker baseline, the selected model metadata came from:

```text
reports/backtests/ppo_walkforward_results_20260512_8ticker_combined
```

---

### 5. Select quality-filtered tickers

After execution-realism analysis is complete, run the quality selector to choose the qualifying PPO model per ticker under the documented baseline rule.

```bash
python -m src.select_quality_tickers \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --scenario moderate \
  --output-dir reports/validation_summary
```

Default inclusion rule:

```text
Execution_Winner == PPO
Execution_Edge_vs_BuyHold > 0
```

Expected selected symbols:

```text
AAPL, AMD, MRK, PFE, UNH, XOM
```

Expected excluded symbols:

```text
META, ORCL
```

This reproduces the six-ticker quality baseline used for the validation workflow.

A stricter research screen can also be run by requiring non-negative estimated Sharpe:

```bash
python -m src.select_quality_tickers \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --scenario moderate \
  --min-sharpe 0 \
  --output-dir reports/validation_summary
```

Under this stricter screen, PFE is excluded because its moderate-scenario `Sharpe_Est` is negative. This variant is useful for sensitivity analysis, but the documented six-ticker baseline uses the execution-edge rule above.

---

### 6. Export selected dynamic LEAN signal payload

```bash
python -m src.export_selected_dynamic_lean_signals \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --symbols AAPL,PFE,UNH,XOM,AMD,MRK \
  --output quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json
```

Expected checks:

```text
Signal rows: 1500
Rows per symbol: 250
First timestamp: 2026-02-10T10:00:00+00:00
Last timestamp: 2026-03-31T14:00:00+00:00
```

Expected selected models:

```text
AAPL    ppo_AAPL_window1
PFE     ppo_PFE_window1
UNH     ppo_UNH_window1
XOM     ppo_XOM_window2
AMD     ppo_AMD_window3
MRK     ppo_MRK_window1
```

The exporter also writes a sidecar reproducibility manifest:

```text
quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.manifest.json
```

The manifest records the source run directory, selected models, payload path, SHA256 hash, symbol list, row count, timestamp range, export configuration, and required source files.

---

### 7. Verify payload structure and manifest metadata

```bash
python - <<'PY'
import json
from pathlib import Path

payload_path = Path("quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json")
manifest_path = Path("quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.manifest.json")

with payload_path.open() as f:
    payload = json.load(f)

with manifest_path.open() as f:
    manifest = json.load(f)

print("symbols:", payload["symbols"])
print("rows_per_symbol:", payload["rows_per_symbol"])
print("signal_rows:", len(payload["signals"]))
print("selected_models:", payload["selected_models"])
print("first_signal:", payload["signals"][0])
print("last_signal:", payload["signals"][-1])
print("manifest_artifact_type:", manifest["artifact_type"])
print("manifest_payload_sha256:", manifest["payload_sha256"][:16] + "...")
PY
```

Expected:

```text
symbols: ['AAPL', 'PFE', 'UNH', 'XOM', 'AMD', 'MRK']
rows_per_symbol: 250
signal_rows: 1500
manifest_artifact_type: dynamic_signal_payload_manifest
```

This check confirms that the exported payload and manifest are structurally present and internally readable.

---

### 8. Validate payload manifest

After exporting the payload and manifest, verify that the payload still matches the manifest record.

```bash
python -m src.validate_payload_manifest \
  --manifest quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.manifest.json
```

Expected checks:

```text
payload_exists: PASS
sha256_match: PASS
symbols_match: PASS
selected_models_match: PASS
rows_per_symbol_match: PASS
signal_rows_match: PASS
first_timestamp_match: PASS
last_timestamp_match: PASS
```

This closes the audit loop for the exported signal payload. The exporter writes the manifest, and the validator confirms that the payload file still matches the saved reproducibility record.

---

### 9. Run local mark-to-market dynamic signal simulation

```bash
python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json
```

Expected checks:

```text
Signal rows: 1500
Return rows: 1500
```

Expected outputs:

```text
reports/dynamic_signal_execution/selected_dynamic_signals_6ticker_quality_250marketbars_mtm_execution_summary.csv
reports/dynamic_signal_execution/selected_dynamic_signals_6ticker_quality_250marketbars_mtm_equity_curve.csv
reports/dynamic_signal_execution/selected_dynamic_signals_6ticker_quality_250marketbars_mtm_trade_ledger.csv
```

---

### 10. Regenerate validation comparison summary

```bash
python -m src.summarize_selected_dynamic_validation \
  --output-dir reports/validation_summary
```

Expected output:

```text
reports/validation_summary/selected_dynamic_validation_comparison.csv
```

The comparison should identify the six-ticker quality-filtered simulation as the primary baseline.

---

### 11. Run final lightweight test suite

```bash
python -m pytest tests -q
git log --oneline -6
```

Expected:

```text
26 passed
```

The documentation update does not affect baseline metrics.

---

## Orchestrated Validation Chain

The validation workflow can also be run through the orchestration wrapper:

```bash
python -m src.run_validation_chain \
  --tickers AAPL PFE UNH XOM AMD MRK \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --dry-run
```

The dry run prints the full command sequence without executing it.

For the current baseline, where data preparation, model training, and execution-realism analysis already exist, use:

```bash
python -m src.run_validation_chain \
  --tickers AAPL PFE UNH XOM AMD MRK \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --skip-data \
  --skip-train \
  --skip-execution-realism
```

This runs the downstream validation chain:

```text
quality selector
dynamic signal export
payload manifest generation
local mark-to-market simulation
validation comparison summary
```

The orchestrator does not replace the underlying scripts. It standardizes the sequence and arguments used to run them.

---

## Selection Rule

Future additions should be screened through the moderate execution-realism output before inclusion.

Minimum filter:

```text
Execution_Winner == PPO
Execution_Edge_vs_BuyHold > 0
```

Preferred secondary checks:

```text
Sharpe_Est > 0
Max_Drawdown_% is not excessive
Trade_Events and Total_Turnover remain controlled
```

---

## Five-Ticker Sharpe-Filtered Sensitivity Check

A stricter sensitivity test was run using the non-negative Sharpe filter:

```bash
python -m src.select_quality_tickers \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --scenario moderate \
  --min-sharpe 0 \
  --output-dir reports/validation_summary
```

This selected:

```text
AAPL, AMD, MRK, UNH, XOM
```

and excluded:

```text
META, ORCL, PFE
```

The five-ticker Sharpe-filtered payload was exported and simulated locally against the same run directory. The result was identical to the six-ticker quality-filtered baseline:

| Validation set                        | Final equity | Net return | Sharpe estimate | Max drawdown | Trade events |
| ------------------------------------- | -----------: | ---------: | --------------: | -----------: | -----------: |
| Five-ticker Sharpe-filtered local MTM |   112,982.27 |     12.98% |            3.80 |        8.96% |          198 |
| Six-ticker quality-filtered local MTM |   112,982.27 |     12.98% |            3.80 |        8.96% |          198 |

Interpretation: excluding PFE did not change the local mark-to-market result because PFE generated only `HOLD` signals in the exported six-ticker dynamic payload. Therefore, PFE contributed no active exposure, turnover, or PnL in the local MTM simulation.

The five-ticker payload was not committed because it is redundant with the documented six-ticker baseline under the current signal thresholding and execution simulator.

---

## Transaction-Cost Sensitivity Check

A transaction-cost sensitivity test was run against the six-ticker quality-filtered dynamic signal payload to evaluate whether the baseline remains viable under higher execution-cost assumptions.

The baseline local mark-to-market simulation uses:

```text
Cost bps: 5.00
```

Additional simulations were run at:

```text
10 bps
15 bps
```

Commands:

```bash
python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 10

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 15

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5
```

The final `--cost-bps 5` run restores the standard baseline output file after the higher-cost sensitivity runs.

| Cost assumption | Final equity | Net return | Sharpe estimate | Max drawdown | Transaction costs | Total turnover | Trade events |
| --------------: | -----------: | ---------: | --------------: | -----------: | ----------------: | -------------: | -----------: |
|           5 bps |   112,982.27 |     12.98% |          3.8048 |        8.96% |          2,000.96 |        36.8929 |          198 |
|          10 bps |   110,916.76 |     10.92% |          3.2663 |        9.17% |          3,965.18 |        36.8929 |          198 |
|          15 bps |   108,888.68 |      8.89% |          2.7275 |        9.38% |          5,893.32 |        36.8929 |          198 |

Interpretation: the strategy degrades as transaction costs rise, as expected, but remains positive under the tested 10 bps and 15 bps assumptions. The 15 bps stress case still produced an 8.89% net return and a 2.73 Sharpe estimate in the local mark-to-market simulation.

The cost sensitivity does not change turnover or trade count because it reuses the same dynamic signal payload and only changes the transaction-cost assumption.

---

## Weight-Cap Sensitivity Check

A weight-cap sensitivity test was run against the six-ticker quality-filtered dynamic signal payload to evaluate whether the strategy remains viable under more conservative position-sizing assumptions.

The standard payload uses the exported target weights directly. In this baseline, the effective maximum absolute target weight is approximately 25% per active symbol.

A simulator-level override was added:

```bash
--max-abs-weight
```

This allows the same dynamic signal payload to be tested under lower exposure caps without regenerating the signal file.

Example commands:

```bash
python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5 \
  --max-abs-weight 0.25

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5 \
  --max-abs-weight 0.15

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5 \
  --max-abs-weight 0.10

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5
```

The final command restores the standard payload-weight baseline output after the sensitivity runs.

| Weight assumption | Final equity | Net return | Sharpe estimate | Max drawdown | Transaction costs | Total turnover | Trade events |
| ----------------- | -----------: | ---------: | --------------: | -----------: | ----------------: | -------------: | -----------: |
| Payload weights   |   112,982.27 |     12.98% |          3.8048 |        8.96% |          2,000.96 |        36.8929 |          198 |
| 25% cap           |   112,982.27 |     12.98% |          3.8048 |        8.96% |          2,000.96 |        36.8929 |          198 |
| 15% cap           |   107,741.96 |      7.74% |          3.8242 |        5.44% |          1,203.65 |        22.8964 |          165 |
| 10% cap           |   105,106.90 |      5.11% |          3.8082 |        3.65% |            796.17 |        15.4000 |          149 |

Interpretation: reducing the maximum absolute position size lowers net return, turnover, transaction costs, and drawdown. However, the Sharpe estimate remains stable around 3.8 across the 25%, 15%, and 10% cap tests. This suggests that the signal quality is not solely dependent on aggressive sizing; the strategy remains risk-adjusted positive under more conservative exposure assumptions.

The 15% and 10% caps are not proposed replacements for the primary baseline at this stage. They are sensitivity checks showing how the same signal payload behaves when position sizing is reduced.

---

## Confidence-Threshold Sensitivity Check

A confidence-threshold sensitivity test was run against the six-ticker quality-filtered dynamic signal payload to evaluate whether filtering lower-confidence signals improves the local mark-to-market result.

The simulator now supports a confidence override:

```bash
--min-confidence
```

The rule is applied at the simulator level:

```text
If abs(confidence) < min_confidence:
    target_weight = 0.0
else:
    use the payload target weight
```

This allows the same exported signal payload to be tested under stricter confidence requirements without regenerating the signal file.

Example commands:

```bash
python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5 \
  --min-confidence 0.00

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5 \
  --min-confidence 0.10

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5 \
  --min-confidence 0.20

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5 \
  --min-confidence 0.30

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5
```

The final command restores the standard baseline output file after the sensitivity runs.

| Confidence threshold | Final equity | Net return | Sharpe estimate | Max drawdown | Transaction costs | Total turnover | Trade events |
| -------------------- | -----------: | ---------: | --------------: | -----------: | ----------------: | -------------: | -----------: |
| `conf >= 0.00`       |   112,982.27 |     12.98% |          3.8048 |        8.96% |          2,000.96 |        36.8929 |          198 |
| `conf >= 0.10`       |   112,982.27 |     12.98% |          3.8048 |        8.96% |          2,000.96 |        36.8929 |          198 |
| `conf >= 0.20`       |   112,698.56 |     12.70% |          3.7273 |        9.05% |          1,897.33 |        35.0915 |          157 |
| `conf >= 0.30`       |   112,073.16 |     12.07% |          3.5764 |        8.85% |          1,800.22 |        33.5000 |          133 |

Interpretation: confidence filtering reduces turnover, transaction costs, and trade count, but it does not improve the baseline risk-adjusted result in this sample. The 0.20 and 0.30 thresholds remove weaker signals and lower activity, but they also reduce net return and Sharpe estimate relative to the unfiltered baseline.

The 0.10 threshold is effectively equivalent to the baseline in this test window because the filtered-out signals do not change the final simulated path. The 0.20 and 0.30 thresholds are useful stress checks, but they are not proposed replacements for the primary six-ticker baseline at this stage.

The confidence-threshold logic is therefore retained as a simulator-level robustness tool rather than promoted to the default baseline configuration.

---

## Return-Window Sensitivity Check

A return-window sensitivity test was run against the six-ticker quality-filtered dynamic signal payload to evaluate whether the selected signal path remains positive across different local return windows.

The simulator now supports a return-window offset:

```bash
--window-offset
```

The offset controls which 250-row return window is aligned against the exported signal payload:

```text
--window-offset 0    uses the latest available 250-row return window
--window-offset 250  uses the prior 250-row return window
--window-offset 500  uses the 250-row window before that
```

This test is a local robustness check. It does not retrain the PPO models and does not regenerate the signal payload. Instead, it reuses the same selected signal path and evaluates how the mark-to-market result changes when aligned to earlier realized return windows.

Example commands:

```bash
python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5 \
  --window-offset 0

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5 \
  --window-offset 250

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5 \
  --window-offset 500

python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_8ticker_combined \
  --payload quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json \
  --cost-bps 5 \
  --window-offset 0
```

The final command restores the standard latest-window baseline output file after the sensitivity runs.

| Return window                 | Final equity | Net return | Sharpe estimate | Max drawdown | Transaction costs | Total turnover | Trade events |
| ----------------------------- | -----------: | ---------: | --------------: | -----------: | ----------------: | -------------: | -----------: |
| Latest window / offset 0      |   112,982.27 |     12.98% |          3.8048 |        8.96% |          2,000.96 |        36.8929 |          198 |
| Prior window / offset 250     |   101,981.37 |      1.98% |          0.6958 |       10.84% |          1,853.30 |        36.8929 |          198 |
| Two windows back / offset 500 |   117,016.03 |     17.02% |          4.3890 |        2.01% |          1,967.60 |        36.8929 |          198 |

Interpretation: the selected signal payload remained positive across all three tested return windows, but performance varied materially by market slice. The latest window and the two-windows-back test produced strong risk-adjusted results, while the prior 250-row window was only modestly positive and had the weakest Sharpe estimate and largest drawdown.

This result does not invalidate the six-ticker baseline, but it does show that the strategy is sensitive to the return window being tested. The correct conclusion is that the payload passes a basic profitability robustness check across these sampled windows, while also showing meaningful time-window sensitivity.

The `--window-offset` feature is retained as a simulator-level robustness tool. It should not be interpreted as a replacement for full walk-forward retraining or out-of-sample validation.

---

## Partial Independent Validation Check

A partial independent validation check was run to test whether the six-ticker quality baseline remained positive when evaluated using separate historical PPO run folders.

The available independent run folders did not contain all six baseline tickers in one unified run. Instead, the available runs were split by ticker group:

| Run folder | Available tickers | Quality-selected tickers |
|---|---|---|
| `reports/backtests/ppo_walkforward_results_20260512_203706` | AMD, META, MRK, ORCL | AMD, MRK |
| `reports/backtests/ppo_walkforward_results_20260509_172626` | AAPL, PFE, UNH, XOM | AAPL, PFE, UNH, XOM |

Because of this split, the test should be interpreted as **partial independent validation**, not a full unified six-ticker independent run.

### AMD/MRK independent validation group

The first independent group used:

```text
Run directory: reports/backtests/ppo_walkforward_results_20260512_203706
Symbols: AMD, MRK
Payload: quantconnect/test_payloads/selected_dynamic_signals_independent_amd_mrk_250marketbars.json
Manifest: quantconnect/test_payloads/selected_dynamic_signals_independent_amd_mrk_250marketbars.manifest.json
```

Export command:

```bash
python -m src.export_selected_dynamic_lean_signals \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_203706 \
  --symbols AMD,MRK \
  --scenario moderate \
  --output quantconnect/test_payloads/selected_dynamic_signals_independent_amd_mrk_250marketbars.json
```

Manifest validation command:

```bash
python -m src.validate_payload_manifest \
  --manifest quantconnect/test_payloads/selected_dynamic_signals_independent_amd_mrk_250marketbars.manifest.json
```

Simulation command:

```bash
python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260512_203706 \
  --payload quantconnect/test_payloads/selected_dynamic_signals_independent_amd_mrk_250marketbars.json \
  --cost-bps 5
```

Result:

| Validation group | Final equity | Net return | Sharpe estimate | Max drawdown | Transaction costs | Total turnover | Trade events |
| ---------------- | -----------: | ---------: | --------------: | -----------: | ----------------: | -------------: | -----------: |
| AMD/MRK | 103,754.64 | 3.75% | 1.9191 | 4.65% | 176.89 | 3.50 | 14 |

The AMD/MRK independent group passed manifest validation and produced a positive local mark-to-market result.

### AAPL/PFE/UNH/XOM independent validation group

The second independent group used:

```text
Run directory: reports/backtests/ppo_walkforward_results_20260509_172626
Symbols: AAPL, PFE, UNH, XOM
Payload: quantconnect/test_payloads/selected_dynamic_signals_independent_aapl_pfe_unh_xom_250marketbars.json
Manifest: quantconnect/test_payloads/selected_dynamic_signals_independent_aapl_pfe_unh_xom_250marketbars.manifest.json
```

Export command:

```bash
python -m src.export_selected_dynamic_lean_signals \
  --run-dir reports/backtests/ppo_walkforward_results_20260509_172626 \
  --symbols AAPL,PFE,UNH,XOM \
  --scenario moderate \
  --output quantconnect/test_payloads/selected_dynamic_signals_independent_aapl_pfe_unh_xom_250marketbars.json
```

Manifest validation command:

```bash
python -m src.validate_payload_manifest \
  --manifest quantconnect/test_payloads/selected_dynamic_signals_independent_aapl_pfe_unh_xom_250marketbars.manifest.json
```

Simulation command:

```bash
python -m src.simulate_dynamic_signal_execution \
  --run-dir reports/backtests/ppo_walkforward_results_20260509_172626 \
  --payload quantconnect/test_payloads/selected_dynamic_signals_independent_aapl_pfe_unh_xom_250marketbars.json \
  --cost-bps 5
```

Result:

| Validation group | Final equity | Net return | Sharpe estimate | Max drawdown | Transaction costs | Total turnover | Trade events |
| ---------------- | -----------: | ---------: | --------------: | -----------: | ----------------: | -------------: | -----------: |
| AAPL/PFE/UNH/XOM | 108,909.18 | 8.91% | 3.4037 | 6.49% | 1,806.12 | 33.3929 | 184 |

The AAPL/PFE/UNH/XOM independent group passed manifest validation and produced a positive local mark-to-market result.

### Combined interpretation

The six-ticker baseline could not be independently validated as one unified six-ticker run because the available historical run folders were split by ticker group. However, the two available independent validation groups collectively covered all six baseline names:

```text
AMD, MRK
AAPL, PFE, UNH, XOM
```

Both partial groups produced positive local mark-to-market results:

| Independent group | Net return | Sharpe estimate | Max drawdown |
| ----------------- | ---------: | --------------: | -----------: |
| AMD/MRK | 3.75% | 1.9191 | 4.65% |
| AAPL/PFE/UNH/XOM | 8.91% | 3.4037 | 6.49% |

This is a positive validation result, but it should be treated as **partial independent support**, not full out-of-sample confirmation.

---

## Unified Independent Six-Ticker Validation Check

A unified independent six-ticker validation run was completed to verify whether the full baseline universe could be retrained and validated together in a fresh run directory.

This check is stronger than the earlier partial independent validation because it uses one unified six-ticker run instead of split ticker-group runs.

### Run provenance

The independent run directory was:

```text
reports/backtests/ppo_walkforward_results_20260517_200251
```

Execution-realism analysis was generated successfully:

```text
reports/backtests/ppo_walkforward_results_20260517_200251/execution_realism_analysis.csv
```

The run used the six baseline symbols:

```text
AAPL, AMD, MRK, PFE, UNH, XOM
```

The fresh training run was enabled by the `--force-retrain` option:

```bash
python -m src.train \
  --tickers AAPL AMD MRK PFE UNH XOM \
  --force-retrain
```

This option forces PPO windows to retrain even when matching model artifacts already exist in `FINAL_MODEL_DIR`. That behavior is required for a clean independent run because the default resume logic correctly skips previously completed artifacts.

### Validation chain

The downstream validation chain completed successfully:

```text
selector → export → manifest validation → simulation → summary
```

The chain was run against the unified independent run folder:

```bash
python -m src.run_validation_chain \
  --tickers AAPL AMD MRK PFE UNH XOM \
  --run-dir reports/backtests/ppo_walkforward_results_20260517_200251 \
  --payload quantconnect/test_payloads/selected_dynamic_signals_unified_independent_250marketbars.json \
  --output-dir reports/validation_summary_unified_independent \
  --skip-data \
  --skip-train \
  --skip-execution-realism
```

The quality selector retained all six baseline tickers:

```text
AAPL, AMD, MRK, PFE, UNH, XOM
```

Selected models:

```text
AAPL    ppo_AAPL_window1
AMD     ppo_AMD_window3
MRK     ppo_MRK_window1
PFE     ppo_PFE_window1
UNH     ppo_UNH_window1
XOM     ppo_XOM_window1
```

### Manifest validation

The exported unified independent payload passed all manifest integrity checks:

| Check | Status |
| ----- | ------ |
| `payload_exists` | PASS |
| `sha256_match` | PASS |
| `symbols_match` | PASS |
| `selected_models_match` | PASS |
| `rows_per_symbol_match` | PASS |
| `signal_rows_match` | PASS |
| `first_timestamp_match` | PASS |
| `last_timestamp_match` | PASS |

This confirms that the exported signal payload matched the manifest record and that the validation was run against the intended ticker universe, selected models, row counts, and timestamp range.

### Unified independent local MTM result

The final unified independent local mark-to-market result was:

| Metric | Value |
| ------ | ----: |
| Final equity | 113,439.87 |
| Net PnL | 13,439.87 |
| Net return | 13.44% |
| Gross PnL before costs | 15,304.99 |
| Transaction costs | 1,865.13 |
| Sharpe estimate | 4.0243 |
| Max drawdown | 6.45% |
| Total turnover | 34.3483 |
| Trade events | 164 |
| Simulation rows | 250 |

### Comparison versus prior six-ticker baseline

The unified independent result was modestly stronger than the prior six-ticker quality baseline:

| Validation run | Final equity | Net return | Sharpe estimate | Max drawdown | Total turnover | Trade events |
| -------------- | -----------: | ---------: | --------------: | -----------: | -------------: | -----------: |
| Prior six-ticker quality baseline | 112,982.27 | 12.98% | 3.8048 | 8.96% | 36.8929 | 198 |
| Unified independent six-ticker run | 113,439.87 | 13.44% | 4.0243 | 6.45% | 34.3483 | 164 |

### Interpretation

The unified independent six-ticker run does not invalidate the existing baseline. It supports it.

Relative to the prior six-ticker baseline, the independent retrained run produced:

```text
higher final equity
higher net return
higher Sharpe estimate
lower maximum drawdown
lower turnover
fewer trade events
```

This is the strongest validation check completed so far because it moves beyond same-payload sensitivity analysis and beyond the earlier split-run partial validation. The full six-ticker universe was retrained together, selected together, exported together, manifest-validated together, and simulated through the same local mark-to-market execution path.

The result should be treated as independent support for the six-ticker research baseline. It is not a deployment claim. Additional validation should still be run across later market periods, broker-style simulation paths, and live-paper execution before treating the strategy as production-ready.

### Related code state

The `--force-retrain` PPO training improvement was committed separately:

```text
e43ee3f Add force retrain option to PPO training
```

That commit is appropriate because the training improvement is source-code functionality and should remain separate from generated research payloads.

### Generated payload cleanup

The unified independent payload files are currently generated artifacts:

```text
quantconnect/test_payloads/selected_dynamic_signals_unified_independent_250marketbars.json
quantconnect/test_payloads/selected_dynamic_signals_unified_independent_250marketbars.manifest.json
```

Do not commit these files unless they are intentionally being promoted to reusable fixtures.

Recommended cleanup:

```bash
rm quantconnect/test_payloads/selected_dynamic_signals_unified_independent_250marketbars.json
rm quantconnect/test_payloads/selected_dynamic_signals_unified_independent_250marketbars.manifest.json

git status --short
python -m pytest tests -q
git log --oneline -8
```

### Documentation status

This section should be treated as the primary independent support note for the six-ticker quality baseline until superseded by a broader walk-forward validation, later-period out-of-sample test, or live-paper execution result.

---

## Known Limitations

The six-ticker baseline is based on local mark-to-market simulation, not a full broker-accurate fill simulator.

QuantConnect validation has been used primarily for Object Store ingestion, timestamp alignment, payload compatibility, and order-path validation. Longer-window performance evaluation remains more reliable in the local/VS Code simulation environment until the QuantConnect data-availability limitation is resolved.

The documented six-ticker baseline uses a combined run folder:

```text
reports/backtests/ppo_walkforward_results_20260512_8ticker_combined
```

This combined folder was used to consolidate the original four selected tickers with the later AMD/MRK/META/ORCL expansion. Future runs should prefer a single run directory generated from the full intended ticker universe.

---

## Version-Control Notes

Do not commit regenerated report files unless intentionally adding ignored artifacts.

If a payload JSON changes only because `generated_utc` was refreshed, restore it unless the payload itself is intentionally being updated:

```bash
git restore quantconnect/test_payloads/selected_dynamic_signals_6ticker_quality_250marketbars.json
```

If the payload and manifest are intentionally updated together, commit both so the manifest hash matches the payload content.

Commit workflow documentation changes with:

```bash
git status --short
git add docs/workflows/six_ticker_quality_baseline.md
git commit -m "Document payload manifest validation workflow"
git pull --rebase origin main
git push
git status --short
```