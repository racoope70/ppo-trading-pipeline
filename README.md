# PPO Trading Pipeline — Historical Quantitative Research Repository

![Status](https://img.shields.io/badge/status-historical%20research-lightgrey)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)
[![Tests](https://github.com/racoope70/ppo-trading-pipeline/actions/workflows/tests.yml/badge.svg)](https://github.com/racoope70/ppo-trading-pipeline/actions/workflows/tests.yml)
![Model](https://img.shields.io/badge/model-PPO-blueviolet)
![Validation](https://img.shields.io/badge/validation-walk--forward-informational)

> **Status: Legacy / historical repository**
>
> This repository preserves the quantitative-trading research and engineering pipeline that preceded the current canonical project, [`racoope70/quantitative-trading-research-platform`](https://github.com/racoope70/quantitative-trading-research-platform).
>
> Public research lineage: [`racoope70/exploratory-daytrading`](https://github.com/racoope70/exploratory-daytrading) → [`racoope70/quant-trading-model-validation`](https://github.com/racoope70/quant-trading-model-validation) (preceding structured PPO / PPO + Random Forest validation) → this repository (later modular PPO implementation / execution research) → [`racoope70/quantitative-trading-research-platform`](https://github.com/racoope70/quantitative-trading-research-platform) (current canonical platform).
>
> It is retained as a historical research record and should not be interpreted as the current production or forward-development platform.

## Overview

This project documents the evolution of a reinforcement-learning trading pipeline centered on **Proximal Policy Optimization (PPO)**.

The work progressed from exploratory PPO experiments into a modular Python implementation covering market-data preparation, feature engineering, chronological walk-forward evaluation, execution-cost analysis, final-holdout testing, candidate qualification, model-artifact management, Alpaca Paper integration, QuantConnect/LEAN signal integration, and later PPO v2 retraining-design, package/preflight, and data-engineering investigations.

The repository preserves both favorable intermediate research results and the evidence that ultimately prevented the legacy PPO from being promoted as a reliable trading model.

## Quantitative Research Summary

| Research area               | Implementation                                                                            |
| --------------------------- | ----------------------------------------------------------------------------------------- |
| Primary model               | Stable-Baselines3 PPO with continuous target exposure in `[-1, 1]`                        |
| Feature pipeline            | Technical, denoised and regime-aware feature construction                                 |
| Validation design           | Chronological walk-forward training/evaluation with explicit time-ordered split utilities |
| Execution realism           | Turnover, transaction-cost, and slippage sensitivity analysis.                            |
| Final evaluation            | Later untouched holdout evaluated without PPO retraining                                  |
| Candidate qualification     | Holdout filtering, promotion scoring and required-artifact validation                     |
| Broker integration          | Alpaca Paper broker-connected no-submit inference and execution planning                  |
| External execution research | JSON signal bridge plus QuantConnect/LEAN consumer                                        |
| Final legacy conclusion     | Infrastructure and research value retained; stable trading edge not established           |

## Research Outcome

Intermediate experiments produced favorable candidate-level PPO results for selected symbols, but the evidence did not remain sufficiently stable across the full research process to support a deployment claim.

The later legacy-model quality audit found mixed benchmark performance across the complete artifact sets and concluded:

```text
infrastructure_baseline_decision = PASS
trading_edge_decision = FAIL_FOR_TRADING_EDGE
controlled_submit_decision = REJECT_FOR_CONTROLLED_SUBMIT
```

The legacy PPO was retained as an **infrastructure fixture and research artifact**, not promoted as evidence of a reliable trading edge. Favorable windows, positive Sharpe ratios, successful broker connectivity, or working code were not treated as sufficient evidence of deployability.

Representative records:

* [`docs/audits/v1.63_ppo_baseline_model_quality_audit_summary.md`](docs/audits/v1.63_ppo_baseline_model_quality_audit_summary.md)
* [`docs/runs/v1.65_legacy_ppo_final_audit_decision.md`](docs/runs/v1.65_legacy_ppo_final_audit_decision.md)

## Research Progression

### Walk-forward PPO research

The project used rolling chronological evaluation rather than a single in-sample backtest. Representative experiments include the [`10-ticker 50k validation`](docs/runs/2026-05-08_10ticker_50k_validation.md) and the later [`4-ticker 150k focused validation`](docs/runs/2026-05-09_4ticker_150k_focused_validation.md). Results were symbol-dependent: longer training improved several intermediate candidates, but turnover, drawdown and execution sensitivity remained material.

### Validation and execution realism

Training and evaluation were separated in time, with support for an embargo region between slices to reduce boundary-leakage risk. Follow-up analysis evaluated turnover, transaction costs, slippage assumptions, cost-adjusted performance and drawdown, making execution realism part of model interpretation rather than an afterthought.

### Final holdout and candidate qualification

Final-holdout evaluation was implemented separately in [`src/alpaca_ppo_holdout_validation.py`](src/alpaca_ppo_holdout_validation.py). The holdout began after the latest pre-holdout validation/evaluation period used to define the candidate set; previously trained PPO and VecNormalize artifacts were then loaded without PPO retraining or threshold tuning. Holdout completion was not automatic promotion: [`src/model_selection/select_alpaca_ppo_candidates.py`](src/model_selection/select_alpaca_ppo_candidates.py) applied separate eligibility and promotion scoring and validated required artifacts before downstream use. See [`v1.8.5 final holdout`](docs/runs/v1.8.5_final_holdout_validation.md) and [`v1.9 candidate selection`](docs/runs/v1.9_alpaca_ppo_candidate_selection.md).

### Alpaca Paper integration

[`src/paper_trading/paper_trade_dry_run.py`](src/paper_trading/paper_trade_dry_run.py) connects to Alpaca Paper, reads account and position state, retrieves recent bars, rebuilds features, runs PPO inference and constructs target-exposure/execution plans without submitting orders. The representative [`six-symbol no-submit redeployment run`](docs/runs/v1.9_alpaca_ppo_no_submit_redeployment_dry_run.md) produced valid predictions for all reviewed symbols with **zero submitted orders**.

### QuantConnect / LEAN integration

[`src/adapters/quantconnect.py`](src/adapters/quantconnect.py) exports PPO predictions as an external JSON signal feed, while [`quantconnect/ExternalSignalConsumer.py`](quantconnect/ExternalSignalConsumer.py) consumes that feed inside LEAN. This keeps local model inference separate from downstream portfolio-target and execution logic.

### Later PPO v2 and data investigations

Later work expanded into PPO v2 retraining design, controlled implementation planning, package/preflight preparation, and data-engineering investigations, including Alpaca historical-data alignment, dataset reconstruction, exchange-calendar handling, missing-bar investigation, provider/feed coverage and validation/reporting infrastructure. These records document investigation and preparation rather than a successfully trained or qualified PPO v2 model. Detailed records remain under `docs/`.

## Architecture

```text
Market data
  -> Data preparation
  -> Feature engineering
  -> Chronological walk-forward PPO training / evaluation
  -> Model + normalization artifacts
  -> Execution-realism analysis
  -> Later untouched holdout
  -> Candidate qualification
  -> Artifact-based inference
  -> Risk / execution planning
  -> Alpaca Paper or QuantConnect integration
  -> Model-quality audit / disposition
```

## Core Components

| Component                                             | Responsibility                                                                                |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `src/features.py`                                     | Constructs technical, denoised, regime and model-input features                               |
| `src/env.py`                                          | Implements the continuous-position PPO environment, including transaction-cost/slippage terms |
| `src/training_splits.py`                              | Enforces time-ordered train/embargo/evaluation partitioning                                   |
| `src/train.py`                                        | Performs walk-forward PPO training, evaluation, metric logging and artifact persistence       |
| `src/artifacts.py`                                    | Manages PPO, VecNormalize, feature, inference-config and metadata artifacts                   |
| `src/alpaca_ppo_holdout_validation.py`                | Evaluates frozen candidates on a later holdout without retraining                             |
| `src/model_selection/select_alpaca_ppo_candidates.py` | Applies holdout eligibility, promotion scoring and artifact validation                        |
| `src/predict.py`                                      | Loads selected artifacts, rebuilds inference features and emits model signals                 |
| `src/paper_trading/paper_trade_dry_run.py`            | Runs broker-connected Alpaca Paper inference/exposure planning without order submission       |
| `src/adapters/quantconnect.py`                        | Exports model predictions as QuantConnect-compatible JSON                                     |
| `quantconnect/ExternalSignalConsumer.py`              | Consumes external JSON signals inside LEAN and maps them to portfolio targets                 |

## Repository Navigation

* `src/` — research, data, model, validation and execution-support implementation
* `tests/` — automated tests
* `quantconnect/` — QuantConnect/LEAN integration
* `config/` — historical runtime and retraining configuration
* `docs/runs/`, `docs/audits/`, `docs/workflows/`, `docs/designs/` — research, validation, audit and design records
* `docs/reviews/`, `docs/plans/`, `docs/decisions/`, `docs/archive/` — detailed historical process and traceability records

## Historical & Reproducibility Notes

The canonical successor project's historical review used legacy snapshot `072103f43d8b2488c3efca183f637ab0508a193a`. That snapshot and its ancestry are intentionally preserved; no history rewrite is proposed.

Detailed research, validation, remediation, documentation and governance records remain in the repository for traceability. The successor platform was created partly to consolidate the resulting architecture and provide a cleaner forward engineering structure.

Large generated runtime artifacts were generally excluded, including many datasets, trained model binaries, processed outputs, backtest/paper-trading outputs, logs and credentials. This repository is therefore a historical implementation and research record rather than a complete binary reproduction package for every experiment.

AI tools were used to assist with drafting and bounded review of portions of the historical governance, evidence, and process documentation. Separate AI-assisted review contexts were also used for selected evidence and governance checks. Their findings and recommendations were advisory within an owner-controlled workflow and did not independently authorize project actions or determine project decisions. These materials are retained as part of the repository's development history. Current development continues in [`racoope70/quantitative-trading-research-platform`](https://github.com/racoope70/quantitative-trading-research-platform).

## Disclaimer

This repository is provided for quantitative-research, educational and software-engineering purposes. Historical backtests, validation metrics, model outputs and paper-trading tests do not guarantee future performance and should not be interpreted as evidence of a deployable or profitable trading strategy.

Nothing in this repository constitutes financial advice.
