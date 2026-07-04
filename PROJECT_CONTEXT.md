# PROJECT_CONTEXT.md

Authoritative source-of-truth document for `racoope70/ppo-trading-pipeline`.

This file defines the current project state, active milestone, validation standards, deployment constraints, blocked actions, research progression, and audit boundaries for the PPO trading pipeline.

Before modifying training logic, validation methodology, deployment workflows, artifact management, broker integration, or milestone documentation, review this file first and then use `docs/workflows/milestone_review_reference_map.md` for supporting historical navigation.

---

## 1. Current Source-of-Truth Summary

```txt
latest_completed_milestone = v3.05 PPO v2 No-Submit Training Package Readiness Review
latest_completed_tag = v3.05-ppo-v2-no-submit-training-package-readiness-review
latest_completed_commit = c9f2c71292a82ee5d528ab179a17792dbff4f477
latest_completed_commit_short = c9f2c71
active_milestone = v3.06 PPO v2 Independent Full-System Pre-Retraining Audit
next_checkpoint = v3.06 PPO v2 Independent Full-System Pre-Retraining Audit
current_workstream = PPO_V2_VALIDATION_READINESS
current_phase = independent full-system audit before any PPO v2 retraining execution
NO_SUBMIT = DEFAULT
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf_deployment_decision = BLOCKED
ppo_xgboost_deployment_decision = BLOCKED
legacy_ppo_classification = INFRASTRUCTURE_FIXTURE_ONLY
legacy_ppo_retraining_decision = DO_NOT_RETRAIN_LEGACY_MODEL
ppo_v2_training_execution = NOT_AUTHORIZED
ppo_v2_training_outputs = NOT_CREATED
ppo_v2_executable_validation_evidence = NOT_YET_GENERATED
latest_test_evidence = 531 passed, 2 warnings
```

The repository has completed readiness documentation for the PPO v2 no-submit training package. It has **not** executed PPO v2 training. The next milestone is a full independent system audit before any one-time no-submit training execution can be considered.

---

## 2. Active Milestone: v3.06 Independent Full-System Pre-Retraining Audit

v3.06 must act as an independent audit gate.

The v3.06 audit should verify:

```txt
PROJECT_CONTEXT.md is current and non-redundant
milestone reference map is consistent
historical chain summaries are correctly grouped
training package boundaries are documented
no-submit defaults remain enforced
broker/order/submit paths remain blocked
PPO + RF and PPO + XGBoost remain blocked
source/test/docs align with current state
stale v1.x active milestone language is removed from current-state sections
no generated artifacts or quarantine outputs were unintentionally created
pre-training evidence requirements are complete and reviewable
```

v3.06 may produce audit documentation. It must not train PPO, fetch market data, generate datasets, create model artifacts, compute validation metrics, generate reports, promote models, submit paper/live orders, authorize controlled submit, or unblock hybrid models.

---

## 3. Current Hard Blocks

The following actions are blocked until a later sealed checkpoint explicitly authorizes them:

```txt
run PPO v2 training
release or execute a training command
fetch new market data
generate training datasets
create model artifacts
create quarantine training outputs
compute new validation metrics from PPO v2 outputs
generate validation reports from real PPO v2 evidence
promote any model
submit paper orders
submit live orders
authorize controlled submit
unblock PPO + Random Forest
unblock PPO + XGBoost
retrain the legacy PPO model
```

Passing unit tests proves infrastructure, control, reporting, and documentation stability. It does **not** prove trading profitability, generalization, deployment readiness, or a trading edge.

---

## 4. Latest Completed Milestone: v3.05

v3.05 completed the no-submit training package readiness review.

```txt
v3_05_decision = PPO_V2_NO_SUBMIT_TRAINING_PACKAGE_READINESS_REVIEW_COMPLETED
training_package_status = READY_FOR_INDEPENDENT_FULL_SYSTEM_PRE_RETRAINING_AUDIT
training_execution_status = NOT_AUTHORIZED
next_required_checkpoint = v3.06 PPO v2 Independent Full-System Pre-Retraining Audit
source_code_modified_in_v3_05 = NO
test_code_modified_in_v3_05 = NO
training_execution = NOT_PERFORMED
command_execution = NOT_PERFORMED
data_fetching = NOT_PERFORMED
dataset_generation = NOT_PERFORMED
model_artifact_creation = NOT_PERFORMED
quarantine_training_outputs = NOT_CREATED
metric_computation = NOT_PERFORMED
report_generation = NOT_PERFORMED
model_promotion = NOT_AUTHORIZED
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf = BLOCKED
ppo_xgboost = BLOCKED
NO_SUBMIT = DEFAULT
```

Validation evidence for v3.05:

```txt
targeted_reporting_scaffold_tests = 37 passed
targeted_preparation_scaffold_tests = 18 passed
targeted_package_tests = 15 passed
existing_wrapper_tests = 13 passed
full_test_suite = 531 passed, 2 warnings
precise_executable_call_scan = no unsafe output
artifact_changes = none
quarantine_training_outputs = none
```

Primary v3.05 documents:

```txt
docs/reviews/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
docs/runs/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
```

---

## 5. Recent Roadmap Position

```txt
v3.02 = final administrative closeout of archived evidence-contract usage chain
v3.03 = archived-chain transition review; active workstream moved to PPO v2 validation readiness
v3.04 = evidence gap review; confirmed PPO v2 lacks executable validation evidence
v3.05 = no-submit training package readiness review; ready for independent audit only
v3.06 = independent full-system pre-retraining audit
v3.07 = one-time no-submit PPO v2 training execution, only if v3.06 passes and explicitly authorizes execution
v3.08 = post-run audit of generated PPO v2 evidence
v3.09 = validation report generation from real evidence
v3.10 = PPO v2 model evidence decision
```

v3.07 is not active. It can only be considered after v3.06 completes cleanly and explicitly authorizes a one-time no-submit PPO v2 training execution.

---

## 6. Historical Phase Summary

Detailed milestone records are preserved under `docs/runs`, `docs/reviews`, `docs/plans`, `docs/decisions`, `docs/standards`, and `docs/archive`. This source-of-truth file intentionally summarizes history instead of repeating every milestone line.

### Legacy PPO Audit and Governance Reset: v1.60-v1.65

```txt
legacy_ppo_final_classification = INFRASTRUCTURE_FIXTURE_ONLY
infrastructure_baseline_decision = PASS
offline_model_quality_decision = FAIL
trading_edge_decision = FAIL_FOR_TRADING_EDGE
no_submit_observation_decision = FAILED_TO_ESTABLISH_STABLE_PROMOTION_EVIDENCE
controlled_submit_decision = REJECT_FOR_CONTROLLED_SUBMIT
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
ppo_rf_deployment_decision = BLOCKED
ppo_xgboost_deployment_decision = BLOCKED
legacy_ppo_retraining_decision = DO_NOT_RETRAIN_LEGACY_MODEL
```

The legacy PPO system remains useful as an infrastructure fixture and audit baseline, but not as a trading-ready model.

### PPO v2 Data, Configuration, and Execution Governance: v1.66-v2.38

This phase created and reviewed PPO v2 design, data contracts, data-preparation interfaces, training configuration scaffolds, controlled execution wrappers, package preparation, and no-submit execution checkpoint documentation.

Result:

```txt
ppo_v2_infrastructure_scaffold = CREATED_AND_TESTED
ppo_v2_training_execution = NOT_PERFORMED
ppo_v2_data_fetching = NOT_PERFORMED
ppo_v2_dataset_generation = NOT_PERFORMED
ppo_v2_model_artifact_creation = NOT_PERFORMED
ppo_v2_quarantine_training_outputs = NOT_CREATED
controlled_submit = BLOCKED
hybrid_models = BLOCKED
```

The v2.35-v2.38 chain closed as `CLOSED_NO_RUN`: no PPO v2 training command was executed and no training outputs existed to audit.

### Validation Reporting and Evidence Contract: v2.39-v3.03

This phase created a non-executing validation reporting scaffold, implemented the evidence contract, implemented read-only evidence-contract usage, audited that usage, archived the chain, and transitioned out of the repetitive closeout sequence.

Key technical checkpoints:

```txt
v2.45 = validation reporting scaffold source/tests created
v2.59 = evidence contract implemented
v2.79 = read-only evidence-contract usage adapter implemented
v2.83 = post-implementation audit result PASS_READ_ONLY_NO_SUBMIT
v2.86 = chain archived as ARCHIVED_CLOSED_PASS_READ_ONLY_NO_SUBMIT
v3.02 = final administrative closeout
v3.03 = transition to PPO v2 validation readiness
```

Grouped archive summary:

```txt
docs/archive/evidence_contract_usage_chain_v2_76_v3_02.md
```

The archived evidence-contract usage chain did not authorize training, data fetching, dataset generation, model artifact creation, quarantine output creation, metric computation, report generation, model promotion, paper orders, live orders, controlled submit, PPO + RF, or PPO + XGBoost.

### Evidence Gap and Training Package Readiness: v3.04-v3.05

v3.04 identified the primary gap:

```txt
primary_gap = PPO_V2_EXECUTABLE_VALIDATION_EVIDENCE_NOT_YET_GENERATED
training_readiness = NOT_READY
```

v3.05 concluded the no-submit training package is ready for independent audit, not execution.

```txt
training_package_status = READY_FOR_INDEPENDENT_FULL_SYSTEM_PRE_RETRAINING_AUDIT
training_execution_status = NOT_AUTHORIZED
```

---

## 7. Evidence Contract Status

The evidence contract is a fail-closed reporting gate. It prevents validation reporting from proceeding unless required training, data-lineage, split-boundary, leakage-control, normalization, holdout, baseline, audit, path, and hash evidence exists.

Implemented components include:

```txt
EvidenceContract
EvidenceContractResult
EvidenceDomainStatus
EvidencePathStatus
EvidenceHashStatus
EvidenceContractDecision
build_evidence_contract
validate_evidence_contract
build_fail_closed_evidence_contract_result
validate_evidence_contract_no_submit_boundary
validate_evidence_contract_usage
build_read_only_evidence_contract_usage_result
```

Current evidence-contract usage boundaries:

```txt
input = static evidence manifest only
output = EvidenceContractResult only
failure_mode = fail closed
side_effects = none
file_writes = none
broker_calls = none
training_calls = none
data_fetching = none
metric_computation = none
report_generation = none
model_promotion = none
order_submission = none
controlled_submit = blocked
hybrid_unblock = blocked
```

The evidence contract protects future validation reporting. It does not itself prove model quality or trading edge.

---

## 8. PPO v2 Evidence Needed Before Training Execution

Before any one-time no-submit PPO v2 training execution can be considered, the audit must confirm:

```txt
reviewed training command
reviewed no-submit execution wrapper or command boundary
validated static data input contract
frozen feature set
reproducible training config
runtime environment and dependency confirmation
seed policy or documented stochastic policy
quarantine-only artifact output location
training log path and retention requirements
run-summary requirements
evidence manifest fields
hash requirements for config, data manifest, and outputs
fail-closed execution failure policy
explicit no broker calls
explicit no paper/live orders
explicit no controlled submit
explicit no model promotion
PPO + RF / PPO + XGBoost remain blocked
independent full-system audit before execution
```

---

## 9. Current Repository Navigation

Current source of truth:

```txt
PROJECT_CONTEXT.md
```

Phase navigation:

```txt
docs/workflows/milestone_review_reference_map.md
```

Evidence-contract usage archive summary:

```txt
docs/archive/evidence_contract_usage_chain_v2_76_v3_02.md
```

Current v3.05 docs:

```txt
docs/reviews/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
docs/runs/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
```

Key legacy PPO governance docs:

```txt
docs/runs/v1.63_ppo_baseline_model_quality_audit_report.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/decisions/v1.65_legacy_ppo_final_audit_decision.md
```

Key PPO v2 data/governance docs:

```txt
docs/designs/v1.66_ppo_v2_retraining_design.md
docs/decisions/v1.67_ppo_v2_retraining_authorization_review.md
docs/audits/v1.71_ppo_v2_scaffold_safety_audit_and_execution_boundary_review.md
docs/specifications/v1.72_ppo_v2_controlled_retraining_data_contract_and_split_specification.md
```

---

## 10. Validation Hierarchy

Validation hierarchy must remain strictly enforced:

```txt
train_df   = model fitting only
embargo    = temporal gap
eval_df    = walk-forward evaluation
holdout_df = untouched final validation
```

Rules:

```txt
no temporal overlap
no leakage
holdout isolation required
no repeated tuning against holdout
evaluation uses locked train-only normalization/preprocessing statistics
no model promotion without deployment review
```

Safe feature standards:

```txt
Target, Return, Datetime, and Symbol must never enter model feature inputs.
```

These columns may be used for labeling, evaluation, grouping, auditing, and reporting.

---

## 11. Core Architecture

The intended architecture remains staged so model output is never treated as immediate trade approval.

```txt
Market Data Layer
    ↓
Feature Engineering Layer
    ↓
Safe Feature Manifest
    ↓
PPO Training Layer
    ↓
Validation + Candidate Selection
    ↓
Paper-Trading Dry Run
    ↓
Dry-Run Evaluation
    ↓
Execution Plan
    ↓
Risk Controls
    ↓
Pre-Trade Checklist
    ↓
Supervised Paper-Order Runner
    ↓
Broker Verification
    ↓
Audit + Monitoring
    ↓
Decision Documentation
```

Current planned retraining data source:

```txt
Alpaca historical 1-hour stock bars
```

Canonical baseline universe:

```txt
AAPL
AMD
MRK
PFE
UNH
XOM
```

---

## 12. Paper-Trading and Submit Constraints

Current default posture:

```txt
NO-SUBMIT
```

Controlled paper submits are not automatic. A controlled submit may only be considered after a separate controlled-submit checkpoint and after fresh evidence confirms:

```txt
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

Controlled submit commands are intentionally omitted from this context file. Never submit from an old checkpoint plan, stale candidate, changed candidate, or unfiltered multi-order plan.

---

## 13. Artifact and Generated Data Policy

Generated data and model artifacts must remain excluded from version control unless a later checkpoint explicitly documents otherwise.

Ignored/generated categories include:

```txt
data/raw/*
data/processed/*
data/alpaca_historical/*
data/alpaca_training/*
reports/*
logs/*
models/*
artifacts/ppo_v2/quarantine/*
*.zip
*.pt
*.pth
*.onnx
*.joblib
*.pkl
*.csv
```

Never commit:

```txt
.env
.env.*
API keys
broker credentials
raw account exports
large generated run outputs
```

Validated historical model artifacts must not be overwritten.

---

## 14. Testing and CI Standards

Primary local test command:

```bash
python -m pytest
```

Requirements before milestone promotion:

```txt
local tests passing
GitHub Actions passing when available
clean git state
reviewed artifact changes
no generated datasets committed
no credentials committed
paper-trading docs updated after operational milestones
```

Passing tests supports code/control stability only. It does not establish trading edge.

---

## 15. Publication and Portfolio Framing

The project should be presented as:

```txt
A production-style PPO trading research pipeline focused on validation governance, leakage prevention, evidence contracts, auditability, no-submit boundaries, and safe model-promotion controls.
```

It should not be presented as:

```txt
A proven profitable trading bot.
```

Current publishable strengths:

```txt
legacy model audit and reclassification
strict validation hierarchy
evidence-contract reporting gate
read-only fail-closed usage adapter
no-submit default
blocked paper/live/controlled submit
blocked hybrid gates until PPO-only evidence exists
audit archive and milestone reference navigation
pre-retraining independent audit gate
```

Remaining before model-performance claims:

```txt
one-time no-submit PPO v2 training execution
post-run audit of generated evidence
validation reporting from real evidence
PPO-only model evidence decision
hybrid comparison only after PPO-only evidence passes
```

---

## 16. Maintenance Requirements

Update this document when:

```txt
milestones complete
active checkpoint changes
validation methodology changes
deployment workflows change
schemas change
architecture changes
operational constraints change
artifact structure changes
paper-trading policy changes
test status changes
```

When a historical chain becomes long or repetitive, keep detailed records in `docs/runs`, `docs/reviews`, or `docs/archive`, and summarize the chain here. Do not turn `PROJECT_CONTEXT.md` into a repeated line-by-line milestone log.

---

## 17. Current Bottom Line

```txt
v3.05 is sealed.
v3.06 is active.
PPO v2 training is not authorized.
No paper/live/controlled submit is authorized.
PPO + RF and PPO + XGBoost remain blocked.
The project is ready for an independent full-system pre-retraining audit, not training execution.
```
