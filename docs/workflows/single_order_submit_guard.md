# v1.13 Single-Order Submit Guard / Execution Filter

Date: 2026-06-02  
Status: Implementation checkpoint  
Scope: Paper-trading execution safety  

## Purpose

Add a guard that allows a reviewed multi-order execution plan to be filtered down to one explicitly selected order before any possible submit.

This is needed because v1.12 produced safe multi-order plans, but the guarded paper-order runner submits every row where `should_order=True` when `--submit-orders` is used.

## Main Module

```text
src/paper_trading/filter_execution_plan.py
```

## Safety Rule

Never submit directly from a multi-order plan during controlled testing.

For controlled testing:

```text
fresh dry run
evaluate dry run
build execution plan
risk controls pass
manual review
filter to one selected order
rerun risk controls on filtered plan
run no-submit paper loop on filtered plan
pre-trade checklist passes
only then consider submit-orders on filtered run directory
```

## Example: Filter One AMD Buy From Latest Plan

```bash
python -m src.paper_trading.filter_execution_plan \
  --run-dir reports/paper_trading_dry_runs/latest \
  --output-dir reports/paper_trading_dry_runs/v1_13_single_order_AMD_buy \
  --symbol AMD \
  --side buy
```

Then validate filtered plan:

```bash
python -m src.paper_trading.risk_controls \
  --run-dir reports/paper_trading_dry_runs/v1_13_single_order_AMD_buy
```

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/v1_13_single_order_AMD_buy
```

```bash
python -m src.paper_trading.pre_trade_checklist \
  --run-dir reports/paper_trading_dry_runs/v1_13_single_order_AMD_buy \
  --check-broker \
  --expected-equity 100000 \
  --equity-tolerance-pct 0.05 \
  --allow-open-positions
```

Only if the filtered checklist passes should a controlled submit be considered:

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/v1_13_single_order_AMD_buy \
  --submit-orders
```

## What This Does Not Do

This module does not:

- connect to Alpaca
- submit orders
- pick the order automatically
- change model predictions
- change target weights
- approve unattended trading

## Guardrails

The selected order must be explicit.

Do not use this as an automatic order selector.

Do not submit filtered plans unless the filtered risk controls and checklist pass.
