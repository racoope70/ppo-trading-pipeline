# Multi-Order Candidate Handling Policy

Version: v1.31  
Status: Active policy  
Scope: PPO-only Alpaca supervised paper trading  
Mode: Policy / operational control  

## Purpose

This policy defines how to handle fresh execution plans that produce more than one eligible order.

A multi-order plan is not automatically trade approval.

A multi-order plan should not be submitted directly.

## Background

This policy was created after v1.30, where the fresh no-submit execution plan produced two eligible orders:

```text
PFE buy
UNH sell
orders_required = 2
```

The correct v1.30 decision was:

```text
NO-SUBMIT
```

Reason:

```text
The plan contained multiple eligible orders and was not a stable single-order candidate.
```

## Core Rule

Do not submit a multi-order plan directly.
A multi-order plan must be reviewed, documented, and either skipped or reduced to a single reviewed candidate in a later checkpoint.

## Definitions

### Multi-Order Plan

A multi-order plan is any execution plan where:

```text
orders_required > 1
```

### Eligible Order

An eligible order is an execution-plan row where:

```text
should_order = True
side in {buy, sell}
qty > 0
reason = rebalance_required
```

### Review-Only Filter

A review-only filter is a named single-order directory created from a multi-order plan for analysis only.
It does not authorize submit.

## Default Decision

The default decision for a multi-order plan is:

```text
NO-SUBMIT
```

This applies even if:

```text
risk controls pass
checklist passes
plan is fresh
broker open orders = 0
```

Passing controls means the plan is structurally safe to review.
It does not mean the plan should be submitted.

## Multi-Order Handling Options

When a fresh plan has multiple orders, the approved handling options are:

```text
Option 1: Skip entire plan
Option 2: Document multi-order plan and stop
Option 3: Create one filtered candidate directory for review only
Option 4: Defer submit decision to a later checkpoint
```

The disallowed handling option is:

```text
Submit all orders directly
```

## Candidate Selection Priority

If a future checkpoint chooses to filter one order from a multi-order plan for review, use this priority order:

1. Exit / reduce existing exposure
2. Risk-reducing rebalance
3. Larger notional only if risk-reducing
4. New entry only after separate review

## Exit vs Entry Rule

An exit or reduction of an existing position generally has higher review priority than a new entry.

Example:

```text
UNH sell = exit / reduce existing position
PFE buy = new entry
```

In that case, the UNH sell may be selected for review first, but not automatically submitted.

## Notional Rule

Notional size can help prioritize review, but it should not override risk logic.
Use notional as supporting information only.
Do not select a trade only because it has the largest notional.

## Confidence Rule

Model confidence can be reviewed, but it should not be the only reason for selection.
Low-confidence signals should be treated cautiously.

## Stability Rule

A filtered candidate from a multi-order plan is still only a candidate.
Before any future controlled submit, it must satisfy:

```text
fresh dry run
single-order review
risk controls pass
pre-trade checklist pass
plan_not_stale = PASS
execution_plan_not_stale = PASS
broker open orders = 0
manual approval
```

## No-Submit Conditions

Do not submit if:

```text
orders_required > 1 and no single-order filter exists
candidate was selected only mechanically
candidate has not been manually reviewed
risk controls fail
checklist fails
plan is stale
broker has unexpected open orders
candidate changed from prior checkpoint
checkpoint is documentation-only
```

## Approved Review Workflow

For a multi-order plan, the safe review workflow is:

1. Run fresh no-submit dry run
2. Evaluate dry run
3. Build execution plan
4. Run risk controls
5. Run guarded paper-order runner in no-submit mode
6. Run pre-trade checklist
7. Classify as multi-order plan
8. Decide no-submit
9. Optionally create one filtered candidate directory in a later checkpoint
10. Document result

## Future Filtered Candidate Pattern

If a later checkpoint explicitly chooses one candidate from a multi-order plan, use a named directory:

```text
reports/paper_trading_dry_runs/vX_YY_single_order_<SYMBOL>_<SIDE>
```

Example:

```text
reports/paper_trading_dry_runs/v1_32_single_order_UNH_sell
```

Then rerun:

```text
risk controls
paper_trade_loop in no-submit mode
pre-trade checklist
```

Do not submit unless a separate controlled submit checkpoint explicitly authorizes it.

## v1.30 Reference Case

Fresh v1.30 plan:

```text
orders_required = 2
buy_count = 1
sell_count = 1
PFE buy
UNH sell
```

v1.30 classification:

```text
MULTI-ORDER PLAN
```

v1.30 decision:

```text
NO-SUBMIT
```

Reason:

```text
The plan had more than one eligible order and was not submit-eligible under the signal persistence policy.
```

## Policy Decision

For PPO-only paper trading, multi-order plans are review events, not submit events.
A multi-order plan can inform future review, but it cannot be submitted directly.

## Next Step

Recommended next checkpoint:

```text
v1.32 Multi-Order Filtered Candidate Review / No-Submit
```

Purpose: if a future multi-order plan appears again, select one candidate for review only, rerun controls on the filtered directory, and still submit no orders.
