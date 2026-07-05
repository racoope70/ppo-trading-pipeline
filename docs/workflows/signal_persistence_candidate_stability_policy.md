# Signal Persistence / Candidate Stability Policy

Version: v1.29  
Status: Active no-submit policy  
Scope: PPO-only Alpaca supervised paper trading  
Mode: Policy / operational control  

## Current Authorization Boundary

Current source-of-truth authorization:

```text
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
NO_SUBMIT = DEFAULT
```

This policy is active only for no-submit candidate review, signal persistence analysis, and audit documentation.

Any language about controlled submit, submit eligibility, or `--submit-orders` is historical / future-only safety context. It is not active authorization to submit paper orders, live orders, or controlled-submit orders.

## Purpose

This policy defines how to classify model-generated paper-trading candidates during no-submit review.

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

Historical / future-only note: before any later checkpoint could even review controlled submit, a candidate would have needed to satisfy:

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
eligible for continued no-submit review
still not automatic approval
```

### Level 2: Submit-Eligible Candidate

Historical / future-only note: this level is superseded under the current v3.06 authorization boundary. No candidate is submit-eligible while paper orders are not authorized and controlled submit is blocked.

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
historical / future-only: would require a separate controlled-submit checkpoint
current v3.06 decision: NO_SUBMIT
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

## Historical / Future-Only Submit Pattern

This example is retained only as historical safety context for a future separately authorized checkpoint. Do not run this command under the current v3.06 state:

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
using single-order filtered directories for no-submit review only
requiring max-plan-age checks
requiring explicit run-dir confirmation
```

Not approved:

```text
paper orders
live orders
controlled submit
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
