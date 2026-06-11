# PPO Walk-Forward Trading Pipeline

This repository contains a modular VS Code implementation of a PPO-based trading research and deployment-preparation pipeline.

The project converts an earlier Google Colab research workflow into a local Python codebase with structured modules for data preparation, feature engineering, walk-forward PPO training, prediction, diagnostics, and downstream execution adapters.

The goal of this repository is to serve as a production-oriented implementation layer between exploratory research and live/paper trading deployment.

This project is for research and educational purposes only. It is not financial advice and does not guarantee profitable trading results.

---

## Workflows

- [Six-Ticker Quality Baseline](docs/workflows/six_ticker_quality_baseline.md)

## Status

This repository is currently a production-oriented implementation in progress.

Completed core components:

- Local project paths and configuration
- Data download and preparation
- Feature engineering
- Custom continuous-position PPO environment
- PPO walk-forward training
- Model artifact saving
- Latest-signal prediction
- Diagnostics
- QuantConnect signal export adapter
- Alpaca paper-trading API utility adapter

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
- Reproducible training and prediction runs
- Cleaner artifact management
- Safer environment-variable handling
- QuantConnect signal export
- Alpaca paper-trading integration
- Future publication or portfolio presentation

---

## Core Workflow

The main workflow is:

```text
Data download
  -> Feature engineering
  -> Walk-forward PPO training
  -> Artifact saving
  -> Latest prediction
  -> Diagnostics
  -> QuantConnect / Alpaca integration
```

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

### 1. Prepare data

```bash
python -m src.prepare_data
```

### 2. Train PPO models

```bash
python -m src.train
```

### 3. Generate latest prediction

```bash
python -m src.predict
```

### 4. Run diagnostics

```bash
python -m src.diagnostics
```

### 5. Export QuantConnect signals

```bash
python -m src.adapters.quantconnect --symbols GE,UNH
```

To publish the signal file to GitHub Gist:

```bash
python -m src.adapters.quantconnect --symbols GE,UNH --publish-gist
```

### 6. Test Alpaca paper connection

```bash
python -m src.adapters.alpaca
```

This command only tests connection, positions, and latest price access. It does not place trades.

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
