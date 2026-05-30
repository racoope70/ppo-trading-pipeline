# v1.9 Alpaca PPO Candidate Selection + Paper-Trading Redeployment

Date: 2026-05-29  
Status: Implementation checkpoint  
Scope: Candidate selection + no-submit paper-trading redeployment dry run  

## Purpose

Promote one standalone Alpaca-trained PPO candidate per ticker after final holdout validation.

This checkpoint follows:

```text
v1.8.5 Final Holdout Validation / Untouched Test Period
```

## Main Module

```text
src/model_selection/select_alpaca_ppo_candidates.py
```

## Selection Input

The selector reads:

```text
reports/alpaca_ppo_retraining/standalone_alpaca_ppo_v1_8_20260528_175838/holdout_validation_final/final_summary.json
```

## Selection Rule

Candidates must:

- Evaluated = true
- PassedHoldout = true
- HoldoutRows >= 60
- Holdout Sharpe >= 0.0
- PPO_Portfolio >= 95000
- required paper-trading artifacts exist

The selector chooses one candidate per ticker using:

```text
PromotionScore =
    Holdout Sharpe
    - 0.10 * Holdout Drawdown %
    + 0.005 * PPO Return %
    + 0.25 if PassedHoldout
```

## Manifest Update

The paper-trading manifest is:

```text
config/paper_trading_six_ticker_manifest.json
```

The manifest points paper trading to:

```text
models/alpaca_ppo_models_master
```

when running dry-run inference.

## Safety Rule

v1.9 starts with no-submit dry-run redeployment only.

Do not submit orders until:

- artifact validation passes
- dry-run predict_ok_count = 6
- execution plan is reviewed
- risk controls pass
- pre-trade checklist passes
- manual review approves submit

## Canonical No-Submit Redeployment Chain

```bash
python -m src.paper_trading.paper_trade_dry_run \
  --manifest config/paper_trading_six_ticker_manifest.json \
  --artifacts-dir models/alpaca_ppo_models_master

python -m src.paper_trading.evaluate_dry_run \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.build_execution_plan \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.risk_controls \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.pre_trade_checklist \
  --run-dir reports/paper_trading_dry_runs/latest \
  --check-broker \
  --expected-equity 100000 \
  --equity-tolerance-pct 0.05 \
  --allow-open-positions
```

## What This Does Not Do

This checkpoint does not:

- submit paper orders
- start unattended trading
- add Random Forest or XGBoost gates
- approve live trading
