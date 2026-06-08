# Rebalance Decision Review / Hold-vs-Exit Policy

Version: v1.23  
Status: Active policy  
Scope: Alpaca PPO supervised paper trading  
Mode: Policy / operational control  

## Purpose

This policy defines how to handle cases where the Alpaca PPO paper-trading system proposes exiting, reducing, or reversing a position that was recently opened.

The purpose is to prevent unnecessary overtrading while preserving the ability to act on valid model-driven exit signals under controlled conditions.

This policy follows:

```text
v1.21 Controlled Submit Using Full v1.18 + v1.19 Safety Stack
v1.22 Post-Full-Safety-Stack Submit Monitoring
```

In v1.22, the system recognized the newly opened UNH position and proposed a UNH sell rebalance. The workflow correctly stayed no-submit because v1.22 was a monitoring checkpoint.

## Core Principle

A valid model-generated exit signal is not automatically a submit decision.

Every exit or rebalance must pass a separate decision review.

The system may propose:

```text
hold
buy / increase
sell / reduce
sell / exit
```

But the operator must decide whether the proposal is:

```text
actionable now
deferred until a later fresh bar
ignored because it is too small
skipped because it risks overtrading
```

## Definitions

### Hold

No order should be submitted.

Common reasons:

```text
below_min_notional
target and actual exposure are close enough
fresh risk/checklist conditions are not met
signal is too small or unstable
```

### Exit

The model target is zero and the current position is nonzero, producing a sell order for a long position.

Example:

```text
target_weight = 0
actual_weight > 0
side = sell
reason = rebalance_required
```

### Reduce

The model target is smaller than the current position but not necessarily zero.

### Overtrading Risk

Overtrading risk exists when the system opens a position and then proposes exiting it shortly afterward without enough time or new evidence to justify action.

## Review Requirements Before Any Exit Submit

An exit or reduce order may only be considered if all conditions below are true:

```text
fresh dry run completed
dry-run evaluation passed
execution plan was rebuilt from the fresh dry run
risk controls passed
pre-trade checklist passed before submit
plan_not_stale = PASS
execution_plan_not_stale = PASS
broker open orders = 0
position is visible in broker state
order is small and explainable
manual review completed
```

Submit mode must still require:

```text
--max-plan-age-minutes 90
--confirm-run-dir <exact reviewed run dir>
```

## Hold-vs-Exit Decision Rules

### Case 1: Below Minimum Notional

If the proposed trade is below min_notional, do not submit.

Expected plan behavior:

```text
side = hold
should_order = False
reason = below_min_notional
```

### Case 2: Immediate Exit After Recent Entry

If the model proposes exiting a position soon after it was opened, default to no-submit unless there is a clear reason to act.

Default action:

```text
hold / monitor
document the exit proposal
wait for a later fresh bar or separate review
```

Rationale:

```text
prevents churn
reduces unnecessary transaction noise
avoids reacting to one short-lived signal flip
```

### Case 3: Single Small Exit Order

A controlled exit may be considered if:

```text
only one order is proposed
the order closes or reduces one known paper position
risk controls pass
checklist passes
max-plan-age passes
broker open orders = 0
manual approval is explicit
```

Preferred execution path:

```text
single-order filtered run directory
not reports/paper_trading_dry_runs/latest
```

### Case 4: Multi-Order Rebalance

If more than one order is proposed, do not submit directly.

Action:

```text
review each order
select at most one order
use the single-order filter
rerun risk controls
rerun checklist
submit only after explicit approval
```

### Case 5: Conflicting Signals Across Consecutive Bars

If the system alternates between buy and sell across nearby bars, treat the signal as unstable.

Default action:

```text
no-submit
monitor for another fresh bar
document instability
```

## Required Exit Submit Pattern

If an exit is approved, use a named filtered directory.

Example:

```bash
python -m src.paper_trading.filter_execution_plan \
  --run-dir reports/paper_trading_dry_runs/latest \
  --output-dir reports/paper_trading_dry_runs/v_next_single_order_UNH_sell \
  --symbol UNH \
  --side sell
```

Then validate:

```bash
python -m src.paper_trading.risk_controls \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_UNH_sell \
  --max-plan-age-minutes 90
```

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_UNH_sell \
  --max-plan-age-minutes 90
```

```bash
python -m src.paper_trading.pre_trade_checklist \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_UNH_sell \
  --check-broker \
  --expected-equity 100000 \
  --equity-tolerance-pct 0.05 \
  --allow-open-positions \
  --max-plan-age-minutes 90
```

Submit only if the review is approved:

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_UNH_sell \
  --submit-orders \
  --max-plan-age-minutes 90 \
  --confirm-run-dir reports/paper_trading_dry_runs/v_next_single_order_UNH_sell
```

## Documentation Requirements

Any rebalance decision should document:

```text
starting tag
broker state before
fresh dry-run result
orders_required
proposed order details
reason for hold or submit
risk-control result
checklist result
broker state after
whether the position was held, reduced, or exited
```

## Current Policy Decision From v1.22

The v1.22 monitoring run proposed:

```text
UNH sell
qty approximately 0.333159
reason = rebalance_required
```

Decision:

```text
no-submit
document as post-submit monitoring
do not immediately exit from the monitoring checkpoint
```

Interpretation:

```text
The system recognized the UNH position correctly.
The proposed sell was valid as a model signal.
The operational policy requires a separate exit decision review before action.
```

## Guardrails

```text
Do not submit exits automatically.
Do not submit from stale plans.
Do not submit from latest if more than one order is present.
Do not immediately undo a recent controlled submit without a separate review.
Do not treat a monitoring checkpoint as approval to trade.
```

## Approved Current Behavior

Approved:

```text
documenting exit proposals
holding during monitoring checkpoints
using single-order filter for reviewed exits
requiring max-plan-age enforcement
requiring explicit run-dir confirmation
```

Not approved:

```text
unattended exits
automatic multi-order rebalances
submitting from stale plans
submitting from unfiltered multi-order plans
real-money trading
```

## Next Step

A future checkpoint may perform a controlled reviewed exit, but only after a fresh dry run and separate approval.

Recommended next checkpoint:

```text
v1.24 Post-Policy No-Submit Rebalance Review Session
```

Purpose: run one fresh no-submit cycle under this policy and document whether any proposed exit/rebalance is held, skipped, or eligible for later review.
