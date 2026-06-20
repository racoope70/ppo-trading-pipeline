# Workflow Documentation Index

This directory contains operational policies, runbooks, and workflow controls for the PPO-only supervised paper-trading pipeline.

## Milestone Review Reference Map

Before advancing, proposing, or implementing any milestone, review:

```text
docs/workflows/milestone_review_reference_map.md
```

This map identifies the relevant audit, standard, design, plan, run, and review documents for each project phase.

It does not authorize work. `PROJECT_CONTEXT.md` remains the controlling source of truth.

## Paper-Trading Safety and Reporting

### Decision and Candidate Policies

```text
paper_trading_decision_state_machine.md
multi_order_candidate_handling_policy.md
signal_persistence_candidate_stability_policy.md
rebalance_decision_policy.md
single_order_submit_guard.md
stale_plan_prevention.md
submit_mode_preflight.md
paper_trading_session_policy.md
```

### Reporting Chain


```text
paper_trading_operational_reporting_runbook.md
paper_trading_reporting_artifact_retention_policy.md
```

The reporting chain is no-submit and reporting-only.
It produces:

```text
decision_state_report.json
paper_trading_run_summary.json
reporting_chain_smoke_test_report.json
paper_trading_decision_dashboard_with_state.md
```

Standard reporting command sequence:

```bash
python -m src.paper_trading.pipeline_decision_state_hook \
  --run-dir reports/paper_trading_dry_runs/latest \
  --prior-symbol AMD \
  --prior-side buy

python -m src.paper_trading.build_run_summary_with_decision_state \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.build_decision_dashboard_with_state \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.reporting_chain_smoke_test \
  --run-dir reports/paper_trading_dry_runs/latest \
  --prior-symbol AMD \
  --prior-side buy
```

Expected safe output:

```text
decision = NO_SUBMIT
submit_allowed = False
```

## Guardrail

The reporting chain does not authorize trading.
Controlled submit requires a separate controlled-submit checkpoint.
