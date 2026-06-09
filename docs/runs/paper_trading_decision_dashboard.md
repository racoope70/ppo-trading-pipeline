# Paper-Trading Decision Dashboard

Status: Active summary dashboard  
Scope: PPO-only Alpaca supervised paper trading  
Current latest checkpoint: v1.25  
Dashboard checkpoint: v1.26  

## Purpose

Provide a compact decision dashboard for the recent PPO-only Alpaca paper-trading safety workflow.

This dashboard summarizes controlled submits, no-submit monitoring sessions, rebalance reviews, and decision classifications.

It is intended as a quick operating reference before future controlled submit tests.

## Current Operating State

Approved:

```text
supervised no-submit monitoring
controlled one-order paper submits
single-order filtered submit tests
post-submit monitoring
rebalance proposal documentation
hold-vs-exit policy review
decision logging
```

Not approved:

```text
unattended trading
real-money trading
automatic multi-order submission
submitting from stale plans
submitting without explicit run-dir confirmation
forced cleanup of residual positions
automatic exits after recent entries
```

## Recent Decision Summary

| Checkpoint | Date | Mode | Orders Required | Orders Submitted | Decision | Risk | Checklist | Broker Open Orders | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v1.21 | 2026-06-05 | Controlled submit | 1 | 1 | Approved controlled UNH buy | PASS | PASS before submit | 0 | Passed |
| v1.22 | 2026-06-08 | Post-submit monitoring | 1 | 0 | Hold / no-submit UNH sell proposal | PASS | PASS | 0 | Passed |
| v1.23 | 2026-06-08 | Policy documentation | N/A | 0 | Hold-vs-exit policy adopted | N/A | N/A | N/A | Passed |
| v1.24 | 2026-06-08 | No-submit rebalance review | 2 | 0 | Skip multi-order AAPL/AMD buy proposal | PASS | PASS | 0 | Passed |
| v1.25 | 2026-06-08 | Decision log | N/A | 0 | Consolidated decision log created | N/A | N/A | N/A | Passed |

## Detailed Notes

### v1.21 Controlled Submit

Decision:

```text
APPROVED CONTROLLED SUBMIT
```

Summary:

```text
UNH buy
qty = 0.333295
orders_required = 1
orders_submitted = 1
```

The order was submitted only after:

```text
fresh dry run
single-order filter
risk controls
pre-submit checklist
--max-plan-age-minutes 90
--confirm-run-dir exact filtered directory
broker verification
```

### v1.22 Post-Submit Monitoring

Decision:

```text
HOLD / NO-SUBMIT
```

Summary:

```text
UNH sell/rebalance proposed
orders_required = 1
orders_submitted = 0
risk = PASS
checklist = PASS
broker_open_orders = 0
```

Interpretation:

The model recognized the UNH position and proposed an exit/rebalance.
The session was monitoring-only, so no submit was allowed.

### v1.23 Hold-vs-Exit Policy

Decision:

```text
POLICY ADOPTED
```

Summary:

```text
Model-generated exits are not automatic submit decisions.
Exit/rebalance proposals require separate review.
```

### v1.24 Post-Policy No-Submit Review

Decision:

```text
SKIP / NO-SUBMIT
```

Summary:

```text
AAPL buy proposed
AMD buy proposed
orders_required = 2
orders_submitted = 0
risk = PASS
checklist = PASS
broker_open_orders = 0
```

Interpretation:

The model generated a multi-order rebalance proposal.
Under policy, multi-order plans are not eligible for direct submit.

### v1.25 Decision Log

Decision:

```text
DECISION LOG CREATED
```

Summary:

```text
v1.21 through v1.24 outcomes were consolidated into one audit trail.
```

## Current Risk Posture

The workflow has validated:

```text
fresh-run discipline
risk-control enforcement
stale-plan prevention
explicit run-dir confirmation
single-order filtering
controlled submit testing
post-submit monitoring
hold-vs-exit policy
rebalance decision logging
```

## Current Position Interpretation

The paper account has recently held:

```text
tiny AMD residual
small UNH position from v1.21
```

These are acceptable in the current supervised paper-trading state.
No cleanup or rebalance should be submitted automatically.

## Future Submit Rule

Before any future submit, verify:

```text
fresh dry run completed
evaluation passed
execution plan reviewed
orders_required is exactly 1, or plan is filtered to one order
risk controls passed
checklist passed
plan_not_stale = PASS
execution_plan_not_stale = PASS
--max-plan-age-minutes 90 is used
--confirm-run-dir matches exact reviewed run directory
broker open orders = 0
manual approval is explicit
post-submit broker verification is planned
```

If any condition fails:

```text
do not submit
```

## Next Recommended Checkpoint

v1.27 Controlled Single-Order Rebalance Candidate Review

Purpose:
Review a future fresh no-submit plan and determine whether a single candidate order is eligible for controlled submit under the full v1.18-v1.23 safety framework.
This should begin as no-submit review only.
