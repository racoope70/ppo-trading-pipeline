# Paper-Trading Reporting Artifact Retention Policy

Version: v1.42  
Status: Active policy  
Scope: PPO-only supervised paper-trading reporting  
Mode: Documentation / artifact governance  

## Purpose

This policy defines which paper-trading reporting artifacts should be committed, ignored, regenerated, archived, or kept local only.

The goal is to keep the repository auditable without filling it with transient run outputs.

This policy is documentation-only.

It does not authorize trades.

It does not submit orders.

## Core Principle

Commit stable documentation and curated summary artifacts.

Do not commit every generated runtime artifact.

Generated local run outputs should usually be reproducible from code and preserved locally unless intentionally promoted into documentation.

## Artifact Classes

### 1. Permanent Documentation

These files should generally be committed.

```text
docs/workflows/*.md
docs/runs/v*.md
README.md
PROJECT_CONTEXT.md
```

Purpose:

```text
document policies
document milestones
document run interpretations
document operational procedures
document project state
```

Retention decision:

```text
COMMIT
```

### 2. Curated Dashboard Artifacts

These files may be committed when they represent a stable reviewed checkpoint.

```text
docs/runs/paper_trading_decision_dashboard.md
docs/runs/paper_trading_decision_dashboard.csv
docs/runs/paper_trading_decision_dashboard_with_state.md
```

Purpose:

```text
summarize reviewed paper-trading decision state
provide portfolio-level reporting visibility
support audit trail
```

Retention decision:

```text
COMMIT WHEN CURATED
```

Do not commit dashboard files automatically after every run unless the result is intentionally reviewed and documented.

### 3. Local Run Artifacts

These files are generated inside run directories such as:

```text
reports/paper_trading_dry_runs/latest/
reports/paper_trading_dry_runs/<named_run>/
```

Common artifacts:

```text
dry_run_summary.json
dry_run_targets.csv
execution_plan_summary.json
execution_plan.csv
risk_controls_report.json
paper_order_run_summary.json
paper_order_audit_log.json
pre_trade_checklist_report.json
decision_state_report.json
paper_trading_run_summary.json
reporting_chain_smoke_test_report.json
```

Retention decision:

```text
KEEP LOCAL BY DEFAULT
DO NOT COMMIT BY DEFAULT
```

Reason:

```text
runtime artifacts can be regenerated
runtime artifacts may contain volatile market/account state
committing all run artifacts creates repository noise
```

### 4. Promoted Run Evidence

A generated run artifact may be promoted into documentation when it supports an important checkpoint.

Examples:

```text
summary values copied into docs/runs/v*.md
selected dashboard copied into docs/runs/
curated CSV force-added intentionally
```

Retention decision:

```text
PROMOTE SELECTIVELY
```

Promotion requires:

```text
manual review
clear checkpoint reason
test pass
commit message documenting purpose
```

### 5. Sensitive or Broker-Specific Runtime Data

Artifacts that may contain broker identifiers, account snapshots, order IDs, raw account details, or environment-specific information should not be broadly committed unless intentionally sanitized.

Retention decision:

```text
LOCAL ONLY OR SANITIZED SUMMARY
```

Examples:

```text
raw broker snapshots
raw order IDs
temporary logs
environment files
credentials
API keys
```

Never commit:

```text
.env
API keys
secret files
raw credential dumps
```

## Decision Matrix

| Artifact Type | Example | Default Retention |
| --- | --- | --- |
| Workflow policy | `docs/workflows/*.md` | Commit |
| Run note | `docs/runs/v*.md` | Commit |
| Main README | `README.md` | Commit |
| Project context | `PROJECT_CONTEXT.md` | Commit when updated |
| Curated dashboard markdown | `docs/runs/paper_trading_decision_dashboard_with_state.md` | Commit when reviewed |
| Curated dashboard CSV | `docs/runs/paper_trading_decision_dashboard.csv` | Commit when reviewed |
| Local JSON run output | `reports/.../decision_state_report.json` | Keep local |
| Local run summary | `reports/.../paper_trading_run_summary.json` | Keep local |
| Local smoke report | `reports/.../reporting_chain_smoke_test_report.json` | Keep local |
| Raw broker/account logs | `logs/`, raw snapshots | Local/sanitize |
| Secrets | `.env`, keys | Never commit |

## Standard Reporting Promotion Flow

When a reporting run is important enough to document:

1. Run reporting chain locally.
2. Inspect generated JSON/dashboard artifacts.
3. Copy key values into `docs/runs/v*.md`.
4. Commit the run note.
5. Commit curated dashboard only if intentionally reviewed.
6. Do not commit raw local run directory by default.

## Current Curated Reporting Artifacts

The following curated reporting artifacts are allowed to remain committed:

```text
docs/runs/paper_trading_decision_dashboard.md
docs/runs/paper_trading_decision_dashboard.csv
docs/runs/paper_trading_decision_dashboard_with_state.md
```

These are project-level reporting artifacts, not raw per-run runtime directories.

## Local Artifact Verification

To inspect local reporting artifacts:

```bash
cat reports/paper_trading_dry_runs/latest/decision_state_report.json
echo
cat reports/paper_trading_dry_runs/latest/paper_trading_run_summary.json
echo
cat reports/paper_trading_dry_runs/latest/reporting_chain_smoke_test_report.json
```

To inspect committed curated dashboard artifacts:

```bash
cat docs/runs/paper_trading_decision_dashboard_with_state.md
```

## No-Submit Guardrail

Artifact retention does not change trading authority.
A report, dashboard, run note, or smoke test does not authorize a trade.

Expected safe default:

```text
decision = NO_SUBMIT
submit_allowed = False
```

A controlled submit still requires a separate controlled-submit checkpoint.

## Git Hygiene

Before committing, check:

```bash
git status --short
```

If raw run artifacts appear under `reports/`, review carefully before adding.

Do not use broad commands like:

```bash
git add .
```

Prefer explicit adds:

```bash
git add docs/runs/<file>.md
git add docs/workflows/<file>.md
git add README.md
```

## Policy Decision

The repository should preserve:

```text
policy
run interpretation
curated dashboards
audit summaries
```

The repository should not preserve every transient runtime artifact.

This keeps the paper-trading project reproducible, auditable, and clean.
