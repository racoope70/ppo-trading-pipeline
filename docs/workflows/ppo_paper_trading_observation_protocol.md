# PPO Paper-Trading Observation Protocol

Version: v1.46  
Status: Active protocol  
Scope: PPO-only supervised paper-trading observation  
Mode: Documentation / no-submit observation protocol  

## Purpose

This protocol defines how PPO-only paper-trading behavior should be observed before any controlled-submit eligibility review or hybrid model work.

The purpose is to create a structured confirmation window for supervised PPO-only paper-trading behavior.

This protocol is documentation-only.

No broker connection is required for this checkpoint.

No fresh dry run is required for this checkpoint.

No paper orders are submitted by this checkpoint.

No source code is changed by this checkpoint.

## Core Principle

Reporting stability is not strategy stability.

The completed v1.34 through v1.45 reporting-control stack proves that the paper-trading reporting infrastructure, decision-state visibility, artifact flow, documentation controls, and repository hygiene are mature enough to support supervised review.

It does not prove that the PPO strategy is stable, profitable, or ready for controlled submit.

## Default Operating Posture

The default posture remains:

```text
NO-SUBMIT
```

unless a separate controlled-submit checkpoint explicitly authorizes otherwise.

The observation protocol does not authorize order submission.

The observation protocol does not bypass manual review.

The observation protocol does not activate hybrid model work.

## Observation Window

The PPO-only observation window should include multiple fresh supervised paper-trading review cycles.

The minimum recommended observation window is:

```text
minimum_cycles = 5 fresh market-session review cycles
minimum_days = enough distinct market sessions to avoid treating one session as stability evidence
submit_default = NO-SUBMIT
```

A cycle should only count toward the observation window if it is based on a fresh run and produces complete review artifacts.

A stale run must not count.

A prior checkpoint candidate must not count as a fresh observation.

## Valid Observation Cycle

A valid PPO-only observation cycle should include:

```text
fresh no-submit dry run
dry-run evaluation
execution-plan generation
risk-control review
paper-order runner in no-submit mode
pre-trade checklist
decision-state classification
run summary
decision dashboard
manual review note
```

A valid cycle should document:

```text
run timestamp
candidate symbol
candidate side
orders_required
decision state
submit_allowed
risk result
checklist result
broker state
candidate persistence status
changed-candidate status
multi-order status
P&L observation if available
drawdown observation if available
turnover observation if available
```

## Required Metrics

Each observation cycle should track:

```text
decision_state
submit_allowed
orders_required
candidate_symbol
candidate_side
candidate_changed
candidate_persisted
multi_order_plan
risk_result
checklist_result
plan_staleness
broker_open_orders
broker_snapshot_status
paper_trading_pnl
paper_trading_drawdown
turnover
trade_frequency
position_state
open_position_count
errors
warnings
```

The observation review should summarize these metrics across the full confirmation window.

## Required Artifacts

Each observation cycle should preserve or summarize the following generated artifacts:

```text
dry_run_predictions
dry_run_evaluation_report
execution_plan
risk_control_report
paper_order_summary
pre_trade_checklist_report
decision_state_report
paper_trading_run_summary
paper_trading_decision_dashboard_with_state
manual review note
```

Generated artifacts should remain excluded from version control unless intentionally curated into documentation.

The committed record should be the reviewed summary, not raw generated output.

## Candidate Persistence Rules

A candidate is not submit-eligible just because it appears once.

A candidate must be revalidated on a fresh future run before any submit decision.

Do not submit from a prior checkpoint execution plan.

Do not assume a prior candidate remains valid.

Candidate stability levels remain:

```text
Level 0 = one-time candidate; review only
Level 1 = revalidated candidate; eligible for controlled review
Level 2 = submit-eligible candidate; requires full safety stack and manual approval
```

Level 2 does not mean automatic submission.

Level 2 means a candidate may be reviewed in a separate controlled-submit checkpoint.

## Changed-Candidate Handling

A candidate should be treated as changed if any of the following occur:

```text
symbol changes
side changes
candidate disappears
orders_required changes from one to multiple
candidate becomes below minimum notional
risk controls fail
pre-trade checklist fails
plan becomes stale
broker state changes unexpectedly
```

Changed candidates should default to:

```text
NO-SUBMIT
```

A changed candidate resets submit consideration.

## Multi-Order Handling

A multi-order plan is any execution plan where:

```text
orders_required > 1
```

A multi-order plan is a review event, not a submit event.

A multi-order plan should not be submitted directly.

If a multi-order plan appears during the observation window, the review note should document:

```text
number of eligible orders
symbols
sides
notional exposure
existing positions
risk-control result
checklist result
decision state
reason for no-submit
```

Default action:

```text
NO-SUBMIT
```

## Pass Criteria for Observation Window

The PPO-only observation window may be considered ready for stability review only if the completed cycles show:

```text
all required artifacts produced
decision-state classification completed
run summaries produced
dashboard visibility maintained
no unexpected broker-state failures
no stale-plan submission attempts
no paper orders submitted by default
candidate behavior documented across cycles
multi-order plans handled as no-submit review events
changed candidates handled as no-submit review events
risk and checklist results reviewed
P&L, drawdown, and turnover observations summarized
```

Passing the observation window does not automatically authorize submit.

Passing the observation window only allows a later PPO paper-trading stability review / controlled-submit eligibility review.

## Fail Criteria for Observation Window

The observation window should fail or pause if any of the following occur:

```text
dry-run evaluation fails
risk controls fail without documented review
pre-trade checklist fails without documented review
decision-state classification is missing
run summary is missing
dashboard output is missing
broker state cannot be verified when required
execution plan is stale
candidate changes are ignored
multi-order plan is treated as submit approval
paper order submission occurs without separate controlled-submit checkpoint
generated artifacts are committed accidentally
source-code changes are introduced into the observation protocol checkpoint
```

A failed or paused observation window should lead to review, correction, or extended observation before any controlled-submit eligibility review.

## Controlled-Submit Boundary

Controlled submit remains outside this protocol.

A controlled submit may only be considered in a separate checkpoint after:

```text
fresh dry run completed
dry-run evaluation passed
execution plan rebuilt from the fresh dry run
candidate persisted or was freshly revalidated
orders_required = 1, or reviewed single-order filtered directory exists
risk controls passed
pre-trade checklist passed
plan_not_stale = PASS
execution_plan_not_stale = PASS
broker open orders = 0
selected order explicitly identified
manual review completed
manual approval explicit
post-submit broker verification planned
```

This protocol does not approve controlled submit.

## PPO-Only Evidence Gate Before Hybrid Work

Before PPO + Random Forest or PPO + XGBoost gate work is considered, the PPO-only baseline must pass through the full evidence gate:

```text
train_df model fitting only
    |
embargo gap
    |
eval_df / walk-forward validation
    |
untouched holdout validation
    |
leakage and train-only normalization / preprocessing review
    |
supervised no-submit paper-trading observation
    |
stability review
    |
PPO-only baseline performance package
    |
only then consider PPO + Random Forest / PPO + XGBoost gates
```

Hybrid models remain blocked until PPO-only behavior is sufficiently documented and reviewed.

## What This Protocol Proves

This protocol proves that the repository has a defined PPO-only paper-trading observation framework.

It proves that future fresh market-session reviews have explicit expectations for:

```text
minimum cycles
required metrics
required artifacts
pass criteria
fail criteria
candidate persistence
changed-candidate handling
multi-order handling
controlled-submit boundaries
hybrid gate boundaries
```

## What This Protocol Does Not Prove

This protocol does not prove:

```text
PPO strategy stability
PPO profitability
controlled-submit readiness
PPO + Random Forest readiness
PPO + XGBoost readiness
live-money readiness
```

Observation design is not performance evidence.

Performance evidence must come from future supervised PPO-only observation cycles and the later PPO-only baseline performance package.

## Recommended Next Checkpoint

```text
v1.47 Fresh No-Submit Market-Session Review Using Completed Reporting Stack
```

The v1.47 checkpoint should run the first fresh market-session review under this protocol.

The v1.47 default decision remains:

```text
NO-SUBMIT
```
