# Paper-Trading Operational Reporting Runbook

Version: v1.40  
Status: Active runbook  
Scope: PPO-only Alpaca supervised paper-trading reporting  
Mode: No-submit reporting workflow  

## Current Authorization Boundary

Current source-of-truth authorization:

```text
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
NO_SUBMIT = DEFAULT
```

This runbook is reporting-only and no-submit only.

Any references to future controlled submit, broker verification after submit, or submit checkpoints are historical / future-only separation notes. They are not active operating instructions and do not authorize paper orders, live orders, controlled submit, model promotion, or v3.07.

## Purpose

This runbook defines the standard operating procedure for running the paper-trading reporting chain after a paper-trading dry run has completed.

The reporting chain converts local run artifacts into:

```text
decision_state_report.json
paper_trading_run_summary.json
paper_trading_decision_dashboard_with_state.md
reporting_chain_smoke_test_report.json
```

This runbook is reporting-only.
It does not authorize trades.
It does not submit orders.

## Safety Principle

The reporting chain is designed to preserve the default operating decision:

```text
NO_SUBMIT
```

A dashboard, report, summary, or passing smoke test is not trade approval.
Controlled submit is currently blocked and would require a later sealed checkpoint before it could be reconsidered.

## Required Starting Point

Before running the reporting chain, the paper-trading run directory should already contain the core no-submit artifacts:

```text
dry_run_summary.json
execution_plan_summary.json
execution_plan.csv
paper_order_run_summary.json
pre_trade_checklist_report.json
```

The run should already have completed:

```text
dry run
evaluation
execution plan
risk controls
paper_trade_loop in no-submit mode
pre-trade checklist
```

## Standard Run Directory

Default run directory:

```text
reports/paper_trading_dry_runs/latest
```

If reviewing a named run, replace latest with the exact run directory.

## Standard Reporting Chain

Run these commands from the repository root.

### 1. Write Decision-State Report

```bash
python -m src.paper_trading.pipeline_decision_state_hook \
  --run-dir reports/paper_trading_dry_runs/latest \
  --prior-symbol AMD \
  --prior-side buy
```

Expected output includes:

```text
Saved decision state report: reports/paper_trading_dry_runs/latest/decision_state_report.json
state: <STATE>
decision: <DECISION>
orders_required: <N>
submit_allowed: False
```

### 2. Write Consolidated Run Summary

```bash
python -m src.paper_trading.build_run_summary_with_decision_state \
  --run-dir reports/paper_trading_dry_runs/latest
```

Expected output includes:

```text
Saved run summary: reports/paper_trading_dry_runs/latest/paper_trading_run_summary.json
```

### 3. Write Dashboard With Decision State

```bash
python -m src.paper_trading.build_decision_dashboard_with_state \
  --run-dir reports/paper_trading_dry_runs/latest
```

Expected output includes:

```text
Saved dashboard: docs/runs/paper_trading_decision_dashboard_with_state.md
```

### 4. Run Reporting Chain Smoke Test

```bash
python -m src.paper_trading.reporting_chain_smoke_test \
  --run-dir reports/paper_trading_dry_runs/latest \
  --prior-symbol AMD \
  --prior-side buy
```

Expected output includes:

```text
passed: True
decision: NO_SUBMIT
submit_allowed: False
```

## Verification Commands

After running the reporting chain, inspect the generated artifacts:

```bash
cat reports/paper_trading_dry_runs/latest/decision_state_report.json
echo
cat reports/paper_trading_dry_runs/latest/paper_trading_run_summary.json
echo
cat reports/paper_trading_dry_runs/latest/reporting_chain_smoke_test_report.json
echo
cat docs/runs/paper_trading_decision_dashboard_with_state.md
```

## Expected Safe Output Pattern

For a no-candidate hold run, the expected classification is:

```text
state = NO_CANDIDATE_HOLD
decision = NO_SUBMIT
orders_required = 0
submit_allowed = False
```

For a multi-order plan, the expected classification is:

```text
state = MULTI_ORDER_PLAN
decision = NO_SUBMIT
orders_required > 1
submit_allowed = False
```

For a changed candidate, the expected classification is:

```text
state = CHANGED_CANDIDATE
decision = NO_SUBMIT
submit_allowed = False
```

For an invalid or incomplete run, the expected classification is:

```text
state = ABORTED_INVALID_FRESH_CYCLE
decision = NO_SUBMIT
submit_allowed = False
```

## Failure Handling

### Missing Checklist Report

If the classification hook fails because this file is missing:

```text
pre_trade_checklist_report.json
```

do not bypass the check during normal operations.

Correct response:

```text
Stop.
Run or rerun the pre-trade checklist.
Do not create a decision-state report until checklist exists.
```

### Smoke Test Fails

If the smoke test returns:

```text
passed = False
```

correct response:

```text
Stop.
Do not rely on dashboard output.
Inspect decision_state_report.json and paper_trading_run_summary.json.
Fix artifact mismatch before continuing.
```

### submit_allowed Is True

If submit_allowed appears as true unexpectedly:

```text
Stop.
Do not submit.
Investigate classifier inputs and checkpoint mode.
```

For standard reporting-only workflows, expected value is:

```text
submit_allowed = False
```

### Decision Is Not NO_SUBMIT

If the reporting chain returns anything other than NO_SUBMIT, treat it as review-only unless a separate controlled-submit checkpoint exists.

Correct response:

```text
Stop.
Document.
Do not submit from the reporting chain.
```

## No-Submit Guardrails

The reporting chain does not:

```text
connect to Alpaca
submit orders
alter broker state
change execution plans
approve trades
replace manual review
```

It only reads and writes local reporting artifacts.

## Controlled Submit Separation

Historical / future-only note: controlled submit is currently blocked. If a later sealed checkpoint ever reopens controlled-submit consideration, it would require all of the following:

```text
fresh dry run
evaluation pass
risk controls pass
pre-trade checklist pass
single-order reviewed directory
manual approval
--max-plan-age-minutes 90
--confirm-run-dir <exact reviewed run dir>
broker verification after submit
documentation
```

The reporting chain is not a submit checkpoint. It does not authorize controlled submit.

## Standard Validation Before Commit

Before committing reporting updates, run:

```bash
python -m pytest tests/test_reporting_chain_smoke_test.py
python -m pytest tests/test_build_decision_dashboard_with_state.py
python -m pytest tests/test_build_run_summary_with_decision_state.py
python -m pytest tests/test_pipeline_decision_state_hook.py
python -m pytest tests/test_classify_decision_state.py
python -m pytest
```

Historical / superseded evidence note:

```text
Earlier reporting-runbook validation referenced: 227 passed, 2 warnings
```

This embedded count is historical/superseded and must not be used as current readiness evidence. Current evidence must come from `PROJECT_CONTEXT.md` and the latest explicit evidence/run record, including `docs/runs/v3.06_remediation_review_follow_up_evidence.md` for this failed-audit cleanup.

## Operational Interpretation

This runbook standardizes the reporting process after paper-trading dry runs.
The goal is to make the system easier to audit:

```text
model output
execution plan
risk/checklist status
decision state
dashboard result
smoke-test result
```

The correct default is always:

```text
NO_SUBMIT
```

Controlled submit remains blocked unless a later sealed checkpoint explicitly changes the authorization state.
