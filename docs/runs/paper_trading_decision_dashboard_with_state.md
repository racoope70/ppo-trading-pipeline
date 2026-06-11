# Paper-Trading Decision Dashboard With State

This dashboard includes the decision-state classification from each reviewed run.

No broker connection is required.

No orders are submitted by this dashboard.

| Run Dir | State | Decision | Orders Required | Buy | Sell | Submit Allowed | Orders Submitted | Risk Passed | Reason |
|---|---|---|---:|---:|---:|---|---:|---|---|
| reports/paper_trading_dry_runs/latest | NO_CANDIDATE_HOLD | NO_SUBMIT | 0 | 0 | 0 | False | 0 | True | No eligible order rows were present. |

## Safety Interpretation

The dashboard is reporting-only. A decision state of `NO_SUBMIT` means the run should not be submitted.

A `submit_allowed` value of `False` must be treated as a hard no-submit condition.

