# Signal Persistence / Candidate Stability Policy

Version: v1.29  
Status: Active policy  
Scope: PPO-only Alpaca supervised paper trading  
Mode: Policy / operational control  

## Purpose

This policy defines when a model-generated paper-trading candidate is stable enough to be considered for a future controlled submit.

A candidate appearing once is not automatically trade approval.

This policy was created after v1.28, where the prior v1.27 candidate changed from:

```text
v1.27 candidate = UNH sell
v1.28 fresh candidate = AMD buy
```

The correct v1.28 decision was no-submit because the original candidate did not persist.

## Core Rule

A candidate must be revalidated on a fresh future run before any submit decision.
Do not submit from a prior checkpoint's execution plan.
Do not assume a prior candidate remains valid.

## Definitions

### Candidate

A candidate is an execution-plan row where:

```text
should_order = True
side in {buy, sell}
orders_required >= 1
```

### Persistent Candidate

A persistent candidate is a candidate that appears across fresh runs with the same:

```text
symbol
side
general direction
risk/checklist pass status
```

### Changed Candidate

A candidate has changed if any of the following occur:

```text
symbol changes
side changes
candidate disappears
orders_required changes from 1 to multiple
candidate becomes below_min_notional
risk fails
checklist fails
plan becomes stale
```

## Stability Requirements

Before a candidate can be considered for controlled submit, it should satisfy:

```text
fresh dry run completed
evaluation passed
execution plan rebuilt
same symbol/side appears on a fresh run
orders_required = 1, or plan is filtered to one order
risk controls pass
pre-trade checklist passes
plan_not_stale = PASS
execution_plan_not_stale = PASS
broker open orders = 0
manual review completed
```

## Candidate Persistence Levels

### Level 0: One-Time Candidate

A candidate appears in one fresh run only.

Decision:

```text
review only
no automatic submit
document candidate
```

### Level 1: Revalidated Candidate

A candidate appears again on a later fresh run with the same symbol and side.

Decision:

```text
eligible for controlled submit review
still not automatic approval
```

### Level 2: Submit-Eligible Candidate

A candidate may be considered submit-eligible only after:

```text
same symbol/side persists or is freshly revalidated
risk controls pass
checklist passes
max-plan-age passes
single-order directory exists if needed
manual approval is explicit
broker verification plan exists
```

Decision:

```text
eligible for separate controlled submit checkpoint
```

## No-Submit Conditions

Do not submit if:

```text
candidate changed symbol
candidate changed side
candidate disappeared
candidate became below_min_notional
fresh plan has multiple orders and is not filtered
risk controls fail
checklist fails
plan is stale
broker has unexpected open orders
operator has not manually approved
checkpoint is not intended to submit
```

## v1.28 Reference Case

In v1.27, the candidate was:

```text
UNH sell
```

In v1.28, the fresh candidate became:

```text
AMD buy
```

The attempted UNH sell filter failed because no UNH sell order existed in the fresh plan.

Policy decision:

```text
NO-SUBMIT
```

Reason:

```text
The prior candidate did not persist.
The new AMD buy was a different candidate.
A changed signal must be documented and re-reviewed, not submitted automatically.
```

## Required Submit Pattern

Even if a candidate is stable, a controlled submit must still use:

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir <reviewed_single_order_run_dir> \
  --submit-orders \
  --max-plan-age-minutes 90 \
  --confirm-run-dir <reviewed_single_order_run_dir>
```

## Documentation Requirements

Each candidate review should document:

```text
starting tag
broker state before
fresh dry-run result
orders_required
candidate symbol
candidate side
candidate quantity
candidate notional
whether the candidate persisted
risk-control result
checklist result
decision classification
broker state after
whether any order was submitted
```

## Approved Behavior

Approved:

```text
reviewing one-time candidates
documenting changed signals
requiring fresh revalidation
using single-order filtered directories
requiring max-plan-age checks
requiring explicit run-dir confirmation
```

Not approved:

```text
submitting stale candidates
submitting changed candidates
submitting from prior checkpoint plans
submitting from unfiltered multi-order plans
automatic exits
automatic entries
unattended trading
real-money trading
```

## Next Step

Recommended next checkpoint:

```text
v1.30 Candidate Stability Review / No-Submit Fresh Cycle
```

Purpose: run a fresh no-submit cycle under this policy and classify whether the candidate is new, persistent, changed, or absent.
