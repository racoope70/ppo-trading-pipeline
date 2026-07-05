# v1.18 Stale-Plan Prevention / Max-Plan-Age Enforcement

Status: Active no-submit safety control
Scope: Alpaca PPO paper-trading execution plans

## Current Authorization Boundary

Current source-of-truth authorization:

```text
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
NO_SUBMIT = DEFAULT
```

This document remains active for no-submit stale-plan prevention. Any submit-mode example is historical / future-only safety context and does not authorize paper orders or controlled submit.

## Purpose

Prevent stale execution plans from being used after the latest market bar becomes too old.

This protects against accidentally relying on an execution plan from an earlier hour, prior day, weekend, or failed workflow.

## Control

Execution plans include `latest_bar_time`.

Risk controls and checklist can enforce:

```text
max_plan_age_minutes
```

A plan is valid only if:

```text
current_utc_time - latest_bar_time <= max_plan_age_minutes
```

## Standard Setting

For the 1-hour strategy, use:

```text
--max-plan-age-minutes 90
```

This allows normal processing delay after an hourly bar but blocks stale plans.

## Required Commands

Risk controls:

```bash
python -m src.paper_trading.risk_controls \
  --run-dir reports/paper_trading_dry_runs/latest \
  --max-plan-age-minutes 90
```

No-submit paper loop:

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/latest \
  --max-plan-age-minutes 90
```

Pre-trade checklist:

```bash
python -m src.paper_trading.pre_trade_checklist \
  --run-dir reports/paper_trading_dry_runs/latest \
  --check-broker \
  --expected-equity 100000 \
  --equity-tolerance-pct 0.05 \
  --allow-open-positions \
  --max-plan-age-minutes 90
```

Historical / future-only submit-mode reference. Do not run under the current v3.06 state:

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir <filtered_or_reviewed_run_dir> \
  --submit-orders \
  --max-plan-age-minutes 90
```

## Hard Rule

Do not submit if:

```text
plan_not_stale = FAIL
execution_plan_not_stale = FAIL
latest_bar_time is missing
latest_bar_time is unparseable
```

## Operational Impact

A stale plan should stop the chain before any downstream review.

The correct response is:

```text
stop
rerun a fresh dry run
rebuild the execution plan
rerun risk controls
rerun checklist
review again
```
