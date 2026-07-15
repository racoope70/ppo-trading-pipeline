# PPO Walk-Forward Trading Pipeline

This repository contains a modular VS Code implementation of a governed PPO-based trading research and validation-readiness pipeline.

The project converts an earlier Google Colab research workflow into a local Python codebase with structured modules for data preparation, feature engineering, walk-forward PPO training, prediction, diagnostics, and downstream execution adapters. Under the current v3.06 state, those modules are not automatically authorized for training, data generation, artifact creation, paper orders, live orders, or controlled submit.

The current goal of this repository is to preserve a governed implementation layer for research, auditability, validation readiness, and future review. It is not currently an authorized live/paper trading deployment or PPO v2 training execution repository.

This project is for research and educational purposes only. It is not financial advice and does not guarantee profitable trading results.

---

## Current Governance Status

Read [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) before making training, retraining, paper-trading, or deployment recommendations. `PROJECT_CONTEXT.md` is the controlling source of truth.

Current state is controlled by `PROJECT_CONTEXT.md`. The README intentionally defers current milestone and checkpoint labels to `PROJECT_CONTEXT.md` to avoid current-stage drift. Durable blocked authorization boundaries remain:

```text
current_state_source = PROJECT_CONTEXT.md
active_milestone = see PROJECT_CONTEXT.md
next_checkpoint = see PROJECT_CONTEXT.md
v3.07_status = BLOCKED
NO_SUBMIT = DEFAULT
ppo_v2_training_execution = NOT_AUTHORIZED
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf = BLOCKED
ppo_xgboost = BLOCKED
```

Legacy PPO is an infrastructure fixture only, not a promoted trading model.

PPO v2 training, training command execution, data fetching, dataset generation, model artifact creation, paper orders, live orders, controlled submit, PPO + Random Forest, and PPO + XGBoost remain blocked unless a later sealed checkpoint explicitly authorizes them.

Passing tests prove infrastructure, control, and reporting stability. They do not prove trading profitability, model promotion, deployment readiness, or trading edge.

---

## Workflows

- [Six-Ticker Quality Baseline](docs/workflows/six_ticker_quality_baseline.md)

## Governance documents

- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) — current active checkpoint, source of truth, and authorization boundary.
- [Milestone Review Reference Map](docs/workflows/milestone_review_reference_map.md) — roadmap navigation and checkpoint reference map.
- [Future Validation and Training Reference Map](docs/workflows/future_validation_training_reference_map.md) — future validation, training, holdout, candidate-selection, and paper-trading reference guide.

## Audit Archive

Evidence Contract Usage Chain: v2.76-v3.02, result `PASS_READ_ONLY_NO_SUBMIT`. Detailed milestone files are preserved under `docs/runs` and `docs/reviews`; a grouped summary is available in [docs/archive/evidence_contract_usage_chain_v2_76_v3_02.md](docs/archive/evidence_contract_usage_chain_v2_76_v3_02.md).

## Status

This repository is currently a production-oriented implementation in progress.

Historical / infrastructure components present in the codebase:

- Local project paths and configuration
- Data download and preparation modules
- Feature engineering modules
- Custom continuous-position PPO environment
- PPO walk-forward training modules
- Model artifact path and metadata helpers
- Latest-signal prediction modules
- Diagnostics
- QuantConnect signal export adapter
- Alpaca paper-trading API utility adapter

Presence of these components does not mean they are currently authorized for PPO v2 training, data fetching, dataset generation, model artifact creation, paper orders, live orders, controlled submit, model promotion, or hybrid deployment.

In progress:

- Full Alpaca paper-trading runner
- Production-grade monitoring
- Improved model selection rules
- Expanded reporting and attribution
- Additional model families such as XGBoost, LightGBM, SAC, TD3, and Deep SARSA

---

## Repository Purpose

This repo is intended to make the trading pipeline easier to run, test, debug, and extend locally.

The earlier Colab workflow was useful for experimentation. This VS Code version is designed for:

- Modular Python development
- Governed validation-readiness review
- Cleaner artifact management
- Safer environment-variable handling
- QuantConnect signal export scaffolding
- Alpaca paper-trading integration scaffolding
- Future publication or portfolio presentation

Reproducible training, prediction runs that create new outputs, data fetching, dataset generation, and model artifact creation require explicit authorization from a later sealed checkpoint before they may be treated as current workflow steps.

---

## Core Workflow

Historical / general architecture:

```text
Data download
  -> Feature engineering
  -> Walk-forward PPO training
  -> Artifact saving
  -> Latest prediction
  -> Diagnostics
  -> QuantConnect / Alpaca integration
```

Current v3.06 interpretation: the architecture above is not current authorization to fetch data, generate datasets, train PPO v2, create model artifacts, produce new validation reports from PPO v2 outputs, promote models, submit paper/live orders, use controlled submit, or deploy PPO + RF / PPO + XGBoost.

---

## Repo Layout

Generated folders such as `data/`, `models/`, `reports/`, and `logs/` are intentionally ignored by Git.

```text
ppo_research_pipeline/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── paths.py
│   ├── config.py
│   ├── data_download.py
│   ├── prepare_data.py
│   ├── features.py
│   ├── env.py
│   ├── artifacts.py
│   ├── train.py
│   ├── predict.py
│   ├── diagnostics.py
│   ├── training_utils.py
│   └── adapters/
│       ├── __init__.py
│       ├── quantconnect.py
│       └── alpaca.py
├── quantconnect/
│   └── ExternalSignalConsumer.py
├── configs/
├── docs/
├── data/
├── models/
├── reports/
└── logs/
```

---

## Main Modules

| Module | Purpose |
|---|---|
| `src/paths.py` | Defines project-relative paths and creates the expected local folder structure. |
| `src/config.py` | Stores runtime settings, ticker lists, walk-forward settings, PPO hyperparameters, paths, and result-folder helpers. |
| `src/data_download.py` | Downloads market data for configured symbols. |
| `src/prepare_data.py` | Runs the data preparation workflow and saves processed datasets. |
| `src/features.py` | Builds technical indicators, regime features, denoised price features, and other model inputs. |
| `src/env.py` | Defines the custom continuous-position trading environment used by PPO. |
| `src/artifacts.py` | Handles model artifact paths, model metadata, feature lists, probability configuration, and saved PPO artifacts. |
| `src/train.py` | Runs walk-forward PPO training, evaluation, metric logging, model selection, and artifact saving. |
| `src/predict.py` | Loads saved PPO artifacts, selects the best available model by metadata, generates the latest signal, and saves prediction outputs. |
| `src/diagnostics.py` | Checks project health, data availability, model artifacts, latest reports, and prediction outputs. |
| `src/adapters/quantconnect.py` | Exports prediction outputs into a QuantConnect-compatible `live_signals.json` file. |
| `src/adapters/alpaca.py` | Provides safe Alpaca API utilities for paper-account connection checks, positions, prices, recent bars, basic order helpers, and future paper-trading integration. |
| `quantconnect/ExternalSignalConsumer.py` | Reference QuantConnect/LEAN algorithm that consumes external JSON signals and maps them into portfolio targets. This file is meant to run inside QuantConnect, not as a normal local Python script. |

---

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a local `.env` file for credentials and runtime settings.

Do not commit `.env`.

Example:

```env
ALPACA_API_KEY=your_paper_key_here
ALPACA_SECRET_KEY=your_paper_secret_here
APCA_API_BASE_URL=https://paper-api.alpaca.markets

GITHUB_TOKEN=your_gist_token_here

TICKERS=UNH,GE
DATA_TIMEFRAME=1H
TRAIN_TIMEFRAME=1H
EQUITY_TIMEFRAME=5Min

ENTER_CONF_MIN=0.02
ENTER_WEIGHT_MIN=0.002
REBALANCE_MIN_NOTIONAL=25.00
RAW_POS_MIN=0.00
RAW_NEG_MAX=0.00

GE_ENTER_CONF_MIN=0.22
GE_ENTER_WEIGHT_MIN=0.04
GE_REBALANCE_MIN_NOTIONAL=75
GE_RAW_POS_MIN=0.18
GE_RAW_NEG_MAX=0.10

UNH_ENTER_CONF_MIN=0.08
UNH_ENTER_WEIGHT_MIN=0.02
UNH_REBALANCE_MIN_NOTIONAL=50
UNH_RAW_POS_MIN=0.00
UNH_RAW_NEG_MAX=0.20

START_FLAT=0
```

---

## Usage

### Current v3.06 usage boundary

Current authorized work is limited to governed review, documentation remediation, source inspection, and explicitly no-submit/read-only checks that do not fetch new market data, generate datasets, create model artifacts, create quarantine outputs, generate validation reports from new PPO v2 outputs, promote models, or submit orders.

### Currently blocked commands

The following commands are retained as legacy/general historical examples only. They are not current PPO v2 authorization:

```text
python -m src.prepare_data  # BLOCKED: data fetching / dataset generation not authorized
python -m src.train         # BLOCKED: PPO v2 training / model artifact creation not authorized
```

Do not run these commands unless a later sealed checkpoint explicitly authorizes them.

### Future-only / separately reviewed commands

Prediction, diagnostics, QuantConnect export, and Alpaca adapter commands may create outputs, inspect broker state, or depend on generated artifacts. Treat them as future-only or separately reviewed unless the current milestone explicitly authorizes the exact command and mode.

```text
python -m src.predict
python -m src.diagnostics
python -m src.adapters.quantconnect --symbols GE,UNH
python -m src.adapters.quantconnect --symbols GE,UNH --publish-gist
python -m src.adapters.alpaca
```

No command in this README authorizes paper orders, live orders, controlled submit, model promotion, PPO + RF, PPO + XGBoost, or v3.07.

---

## QuantConnect Integration

The local adapter:

```bash
python -m src.adapters.quantconnect --symbols GE,UNH
```

creates a JSON file similar to:

```text
reports/backtests/quantconnect_signals_YYYYMMDD_HHMMSS/live_signals.json
```

The QuantConnect algorithm in:

```text
quantconnect/ExternalSignalConsumer.py
```

can consume that JSON through a raw Gist URL.

Typical QuantConnect parameters:

```text
SignalsUrl = <raw live_signals.json URL>
Symbols = GE,UNH
PollingMinutes = 60
SizingMode = threshold
WeightCap = 0.60
ConfidenceFloor = 0.55
Mode = json-live
```

---

## Alpaca Integration

The current Alpaca module is a safe adapter layer, not the full live trading bot.

It currently supports:

- Environment loading
- Paper-account connection
- Account snapshot checks
- Open position reads
- Latest price lookup
- Recent bar downloads
- Basic market order helpers
- Flatten-symbol helper

The larger paper-trading execution loop is still being tuned separately before being migrated into this repository.

---

## Artifact Policy

Model artifacts, processed data, reports, logs, and credentials are intentionally not committed.

Ignored examples:

```text
.env
.env.*
data/raw/
data/processed/
models/
trained_models/
reports/
logs/
*.zip
*.pkl
*.csv
live_signals.json
gist_metadata.json
```

This keeps the repository focused on source code and reproducible workflows.

---

## Current Limitations

- PPO is the primary implemented model.
- The current local test mode may use a limited ticker list.
- Existing model artifacts are not included in the repository.
- The Alpaca live execution loop is not finalized in this repo yet.
- Model performance must be validated with walk-forward testing, paper trading, and out-of-sample evaluation before any real-money use.

---

## Roadmap

Planned improvements:

- Full Alpaca paper-trading runner
- Better model selection using Sharpe, drawdown, and stability filters
- Enhanced performance attribution
- Automated report generation
- CI checks for module imports and syntax
- QuantConnect packaging improvements
- Additional supervised and reinforcement learning models
- Publication-ready methodology notes

---

## Disclaimer

This repository is for research, education, and software development practice. Trading involves risk, and model outputs may be wrong, unstable, or unsuitable for live trading.

---

## Paper-Trading Reporting Chain

The paper-trading reporting chain converts a completed no-submit paper-trading run into auditable decision artifacts.

This workflow is reporting-only.

It does not connect to Alpaca, does not submit orders, and does not alter broker state.

### Reporting Chain Artifacts

After a paper-trading dry run and pre-trade checklist have completed, the reporting chain can produce:

```text
decision_state_report.json
paper_trading_run_summary.json
reporting_chain_smoke_test_report.json
docs/runs/paper_trading_decision_dashboard_with_state.md
```

### Standard Reporting Commands

Run from the repository root:

```bash
python -m src.paper_trading.pipeline_decision_state_hook \
  --run-dir reports/paper_trading_dry_runs/latest \
  --prior-symbol AMD \
  --prior-side buy

python -m src.paper_trading.build_run_summary_with_decision_state \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.build_decision_dashboard_with_state \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.reporting_chain_smoke_test \
  --run-dir reports/paper_trading_dry_runs/latest \
  --prior-symbol AMD \
  --prior-side buy
```

### Expected Safe Output

The default safe reporting output is:

```text
decision = NO_SUBMIT
submit_allowed = False
```

A reporting artifact is not trade approval.
A controlled submit still requires a separate controlled-submit checkpoint, fresh validation, manual approval, exact run-directory confirmation, broker verification, and documentation.

### Reporting Runbook

Full operational instructions are documented here:

```text
docs/workflows/paper_trading_operational_reporting_runbook.md
```

Latest reporting-chain checkpoints:

```text
v1.34 = decision-state classifier
v1.35 = decision_state_report.json writer
v1.36 = post-checklist classification hook
v1.37 = run summary includes decision state
v1.38 = dashboard reads decision state
v1.39 = reporting chain smoke test
v1.40 = operational reporting runbook
```
