# Milestone Review Reference Map

## Source-of-Truth Note

`PROJECT_CONTEXT.md` controls the current project state, active milestone, latest checkpoint, authorization boundaries, blocked actions, and PPO v2 roadmap.

This file is a navigation map only. It does not authorize work, execution, data fetching, model promotion, paper orders, live orders, controlled submit, PPO + Random Forest, or PPO + XGBoost.

Current controlling state:

```txt
latest_completed_milestone = v3.05 PPO v2 No-Submit Training Package Readiness Review
latest_completed_tag = v3.05-ppo-v2-no-submit-training-package-readiness-review
latest_completed_commit = c9f2c71292a82ee5d528ab179a17792dbff4f477
active_milestone = v3.06 PPO v2 Independent Full-System Pre-Retraining Audit
next_checkpoint = v3.06 PPO v2 Independent Full-System Pre-Retraining Audit
NO_SUBMIT = DEFAULT
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf_deployment_decision = BLOCKED
ppo_xgboost_deployment_decision = BLOCKED
ppo_v2_training_execution = NOT_AUTHORIZED
```

Always read `PROJECT_CONTEXT.md` first. Then use this map to identify supporting historical files.

---

## Current Active Review Path

### v3.06 — PPO v2 Independent Full-System Pre-Retraining Audit

**Use when reviewing**

* current readiness before any PPO v2 no-submit retraining execution
* whether v3.05 package readiness was sufficient for independent audit
* whether source, tests, documentation, historical summaries, no-submit boundaries, and artifact policies align
* whether stale v1.x/v2.x active-state references remain in current-state docs
* whether broker/order/submit/hybrid gates remain blocked
* whether generated artifacts or quarantine outputs were unintentionally created
* whether v3.07 may be considered later

**Review first**

```txt
PROJECT_CONTEXT.md
docs/reviews/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
docs/runs/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
docs/reviews/v3.04_ppo_v2_evidence_gap_review.md
docs/runs/v3.04_ppo_v2_evidence_gap_review.md
docs/archive/evidence_contract_usage_chain_v2_76_v3_02.md
```

**Also review for audit coverage**

```txt
docs/workflows/milestone_review_reference_map.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/decisions/v1.65_legacy_ppo_final_audit_decision.md
docs/designs/v1.66_ppo_v2_retraining_design.md
docs/decisions/v1.67_ppo_v2_retraining_authorization_review.md
docs/audits/v1.71_ppo_v2_scaffold_safety_audit_and_execution_boundary_review.md
docs/specifications/v1.72_ppo_v2_controlled_retraining_data_contract_and_split_specification.md
docs/reviews/v2.59_ppo_v2_validation_reporting_scaffold_evidence_contract_implementation_checkpoint.md
docs/reviews/v2.79_ppo_v2_validation_reporting_scaffold_evidence_contract_usage_implementation_checkpoint.md
docs/reviews/v2.83_ppo_v2_validation_reporting_scaffold_evidence_contract_usage_post_implementation_audit.md
```

**v3.06 boundary**

```txt
training_execution = NOT_AUTHORIZED
command_execution = NOT_AUTHORIZED
data_fetching = NOT_AUTHORIZED
dataset_generation = NOT_AUTHORIZED
model_artifact_creation = NOT_AUTHORIZED
quarantine_training_outputs = NOT_AUTHORIZED
metric_computation_from_new_outputs = NOT_AUTHORIZED
report_generation_from_new_outputs = NOT_AUTHORIZED
model_promotion = NOT_AUTHORIZED
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf = BLOCKED
ppo_xgboost = BLOCKED
NO_SUBMIT = DEFAULT
```

**Then move to**

v3.07 only if v3.06 independently passes and explicitly authorizes a one-time no-submit PPO v2 training execution. Otherwise remain in audit/remediation.

---

## Near-Term PPO v2 Roadmap

```txt
v3.02 = final administrative closeout of archived evidence-contract usage chain
v3.03 = archived-chain transition review; workstream moved to PPO v2 validation readiness
v3.04 = evidence gap review; PPO v2 executable validation evidence not yet generated
v3.05 = no-submit training package readiness review; ready for independent audit only
v3.06 = independent full-system pre-retraining audit; active checkpoint
v3.07 = one-time no-submit PPO v2 training execution; not active and not authorized
v3.08 = post-run audit of generated PPO v2 evidence; future only
v3.09 = validation report generation from real evidence; future only
v3.10 = PPO v2 model evidence decision; future only
```

v3.07 is not active. A future v3.07 must remain one-time, no-submit, explicitly authorized, and quarantined. It must not imply paper orders, live orders, controlled submit, model promotion, PPO + RF, or PPO + XGBoost.

---

## Main PPO v2 Phase Map

### v1.60-v1.65 — Legacy PPO Audit and Governance Reset

**Use when reviewing**

* legacy PPO status
* why the legacy PPO is not trading-ready
* model-quality audit findings
* promotion standards
* why the project moved to PPO v2

**Review first**

```txt
docs/runs/v1.63_ppo_baseline_model_quality_audit_report.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/decisions/v1.65_legacy_ppo_final_audit_decision.md
```

**Summary**

```txt
legacy_ppo_final_classification = INFRASTRUCTURE_FIXTURE_ONLY
infrastructure_baseline_decision = PASS
offline_model_quality_decision = FAIL
trading_edge_decision = FAIL_FOR_TRADING_EDGE
controlled_submit_decision = REJECT_FOR_CONTROLLED_SUBMIT
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
ppo_rf_deployment_decision = BLOCKED
ppo_xgboost_deployment_decision = BLOCKED
legacy_ppo_retraining_decision = DO_NOT_RETRAIN_LEGACY_MODEL
```

---

### v1.66-v1.72 — PPO v2 Retraining Governance and Data-Contract Design

**Use when reviewing**

* PPO v2 retraining design
* retraining authorization boundaries
* scaffold safety
* data-contract design
* train / embargo / eval / holdout split rules
* pre-training governance

**Review first**

```txt
docs/designs/v1.66_ppo_v2_retraining_design.md
docs/decisions/v1.67_ppo_v2_retraining_authorization_review.md
docs/audits/v1.71_ppo_v2_scaffold_safety_audit_and_execution_boundary_review.md
docs/specifications/v1.72_ppo_v2_controlled_retraining_data_contract_and_split_specification.md
```

---

### v1.73-v1.83 — Data Contract, Data Preparation, and Training Input Handoff

**Use when reviewing**

* data-contract tests
* schema validation
* split-boundary validation
* leakage checks
* holdout / embargo enforcement
* data-preparation interface
* training-input handoff planning

**Review first**

```txt
docs/runs/v1.73_ppo_v2_data_contract_validation_tests.md
docs/reviews/v1.74_ppo_v2_data_contract_validation_review_next_implementation_boundary.md
docs/plans/v1.75_ppo_v2_controlled_data_preparation_interface_boundary_plan.md
docs/runs/v1.76_ppo_v2_controlled_data_preparation_interface_scaffold_and_tests.md
docs/reviews/v1.77_ppo_v2_data_preparation_interface_scaffold_review_next_boundary_decision.md
docs/plans/v1.78_ppo_v2_data_preparation_interface_integration_boundary_plan.md
docs/runs/v1.79_ppo_v2_data_preparation_interface_integration_scaffold_and_tests.md
docs/reviews/v1.80_ppo_v2_data_preparation_integration_scaffold_review_next_boundary_decision.md
```

---

### v1.84-v2.38 — Training Configuration, Controlled Execution Scaffolds, and No-Run Chain

**Use when reviewing**

* PPO v2 training configuration
* hyperparameter governance
* artifact isolation design
* controlled execution wrappers
* one-time no-submit controlled execution package planning
* why prior controlled execution checkpoints closed with no training run

**Review first**

```txt
PROJECT_CONTEXT.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/specifications/v1.72_ppo_v2_controlled_retraining_data_contract_and_split_specification.md
docs/plans/v1.84_ppo_v2_training_configuration_boundary_plan.md
docs/runs/v1.85_ppo_v2_training_configuration_scaffold_and_tests.md
docs/reviews/v1.86_ppo_v2_training_configuration_review_execution_readiness_boundary.md
docs/reviews/v1.95_ppo_v2_controlled_training_execution_authorization_review.md
docs/plans/v1.96_ppo_v2_controlled_training_execution_checkpoint_design_plan.md
docs/reviews/v1.97_ppo_v2_controlled_training_execution_checkpoint_design_review.md
docs/reviews/v2.35_ppo_v2_one_time_no_submit_controlled_training_execution_checkpoint.md
docs/reviews/v2.36_ppo_v2_one_time_no_submit_controlled_training_execution_post_run_audit_checkpoint.md
docs/reviews/v2.37_ppo_v2_one_time_controlled_training_execution_chain_closeout_review.md
docs/reviews/v2.38_ppo_v2_controlled_training_execution_chain_archive_review.md
```

**Summary**

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

v1.96 and v1.97 are historical design-plan and design-review checkpoints only. Do not treat them as the active state.

---

### v2.39-v3.03 — Validation Reporting, Evidence Contract, and Archived-Chain Transition

**Use when reviewing**

* validation-reporting scaffold history
* evidence contract implementation and usage
* read-only evidence-contract usage adapter
* post-implementation audit result
* grouped presentation for repetitive archived-chain milestone files
* whether the evidence-contract chain authorized training, artifacts, reports, submit, or hybrid work

**Review first**

```txt
PROJECT_CONTEXT.md
docs/archive/evidence_contract_usage_chain_v2_76_v3_02.md
docs/reviews/v2.59_ppo_v2_validation_reporting_scaffold_evidence_contract_implementation_checkpoint.md
docs/reviews/v2.79_ppo_v2_validation_reporting_scaffold_evidence_contract_usage_implementation_checkpoint.md
docs/reviews/v2.83_ppo_v2_validation_reporting_scaffold_evidence_contract_usage_post_implementation_audit.md
docs/reviews/v2.86_ppo_v2_validation_reporting_scaffold_evidence_contract_usage_chain_archive_review.md
docs/reviews/v3.02_ppo_v2_validation_reporting_scaffold_evidence_contract_usage_archived_chain_final_administrative_closeout_review.md
docs/reviews/v3.03_ppo_v2_archived_chain_transition_review.md
```

**Public summary**

```txt
Evidence Contract Usage Chain: v2.76-v3.02, result PASS_READ_ONLY_NO_SUBMIT.
v3.03 transitioned the project out of archived-chain closeout and into PPO v2 validation readiness.
```

**Historical chain guide**

```txt
v2.76-v2.78  authorization and implementation approval path
v2.79        read-only usage adapter implementation
v2.80        implementation review
v2.81-v2.82  post-implementation audit planning and review
v2.83        audit completed with PASS_READ_ONLY_NO_SUBMIT
v2.84        audit review accepted
v2.85-v2.86  chain closed and archived
v2.87-v3.01  administrative archived-chain final/terminal closeout sequence
v3.02        final administrative closeout
v3.03        transition review; archived chain remained closed
```

The adapter wraps the existing v2.59 evidence contract, uses static evidence manifest input only, returns `EvidenceContractResult` only, fails closed, and remains read-only and no-submit.

No checkpoint in this chain authorized PPO training, data fetching, dataset generation, model artifact creation, quarantine output creation, metric computation, report/plot/dashboard generation, model promotion, paper orders, live orders, controlled submit, PPO + RF unblock, or PPO + XGBoost unblock.

---

### v3.04-v3.05 — Evidence Gap and No-Submit Training Package Readiness

**Use when reviewing**

* evidence gaps before PPO v2 training
* whether the no-submit package is ready for independent audit
* static input, feature, config, runtime, seed, output, logging, manifest, hash, and failure-handling requirements
* confirmation that package readiness is not execution authorization

**Review first**

```txt
PROJECT_CONTEXT.md
docs/reviews/v3.04_ppo_v2_evidence_gap_review.md
docs/runs/v3.04_ppo_v2_evidence_gap_review.md
docs/reviews/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
docs/runs/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
```

**Summary**

```txt
v3.04 primary_gap = PPO_V2_EXECUTABLE_VALIDATION_EVIDENCE_NOT_YET_GENERATED
v3.04 training_readiness = NOT_READY
v3.05 training_package_status = READY_FOR_INDEPENDENT_FULL_SYSTEM_PRE_RETRAINING_AUDIT
v3.05 training_execution_status = NOT_AUTHORIZED
```

**Then move to**

v3.06 independent full-system pre-retraining audit.

---

## Older Paper-Trading / Safety History: v0.3-v1.59

Review v0.3-v1.59 only when the task involves:

* paper-trading safety
* broker-order mechanics
* submit-mode preflight
* stale-plan prevention
* candidate stability
* multi-order handling
* reporting dashboards
* historical no-submit observation evidence

### Condensed range guide

```txt
v0.3-v1.0    early safety chain, research hardening, six-ticker retrain, temporal validation
v1.3-v1.9    early Alpaca observation, holdout validation, candidate selection, no-submit redeployment
v1.10-v1.22  controlled paper-order tests, preflight, post-submit monitoring
v1.23-v1.33  rebalance policy, candidate persistence, multi-order policy, decision-state governance
v1.34-v1.44  reporting-chain implementation and artifact governance
v1.45-v1.59  PPO no-submit observation and candidate recurrence history
```

Do not use v0.3-v1.59 evidence to override the v1.60-v1.65 legacy PPO audit conclusions.

For model promotion, retraining, PPO v2, hybrid deployment, or trading-edge claims, start with v1.60-v1.65 as the controlling governance reset.

---

## Special Review Paths

### Paper-Trading Safety

**Review first**

```txt
PROJECT_CONTEXT.md
docs/workflows/paper_trading_session_policy.md
docs/workflows/single_order_submit_guard.md
docs/workflows/submit_mode_preflight.md
docs/workflows/stale_plan_prevention.md
docs/workflows/signal_persistence_candidate_stability_policy.md
docs/workflows/multi_order_candidate_handling_policy.md
docs/workflows/paper_trading_decision_state_machine.md
docs/workflows/paper_trading_operational_reporting_runbook.md
docs/workflows/paper_trading_reporting_artifact_retention_policy.md
docs/workflows/ppo_paper_trading_observation_protocol.md
```

### Evidence Contract / Validation Reporting

**Review first**

```txt
PROJECT_CONTEXT.md
docs/archive/evidence_contract_usage_chain_v2_76_v3_02.md
docs/reviews/v2.59_ppo_v2_validation_reporting_scaffold_evidence_contract_implementation_checkpoint.md
docs/reviews/v2.79_ppo_v2_validation_reporting_scaffold_evidence_contract_usage_implementation_checkpoint.md
docs/reviews/v2.83_ppo_v2_validation_reporting_scaffold_evidence_contract_usage_post_implementation_audit.md
```

### Hybrid Gate or Feature Importance Requests

**Review first**

```txt
PROJECT_CONTEXT.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/decisions/v1.65_legacy_ppo_final_audit_decision.md
```

Hybrid gate work remains blocked until PPO-only evidence exists. Feature importance and model interpretability are later research phases, not proof of trading edge or deployment readiness.

---

## Global Guardrail

```txt
NO_SUBMIT = DEFAULT
training_execution = NOT_AUTHORIZED unless a later sealed checkpoint explicitly authorizes one-time no-submit execution
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf = BLOCKED
ppo_xgboost = BLOCKED
```
