# Milestone Review Reference Map

## Source-of-Truth Note

`PROJECT_CONTEXT.md` controls the current project state, active milestone, latest checkpoint, authorization boundaries, blocked actions, and PPO v2 roadmap.

This file is a navigation map only. It does not authorize work, execution, data fetching, model promotion, paper orders, live orders, controlled submit, PPO + Random Forest, or PPO + XGBoost.

Current controlling state:

```txt
latest_completed_milestone = v3.07 Validation-Only Preflight Evidence Review / R1-R6 Evidence Review
latest_completed_decision = PASS_FAIL_CLOSED_EVIDENCE_REVIEW_ONLY
latest_completed_audit_tag = NOT_TAGGED
latest_completed_audit_record = docs/audits/v3.07_validation_only_preflight_evidence_review_r1_r6.md
latest_completed_run_record = docs/runs/v3.07_validation_only_preflight_evidence_review_r1_r6.md
active_milestone = v3.07 Sealed Dataset Availability / Path / Local Placement Remediation
next_checkpoint = sealed dataset availability/path/local placement remediation before validation-only preflight rerun
current_workstream = PPO_V2_VALIDATION_READINESS
current_phase = fail-closed R1-R6 evidence accepted; sealed dataset availability/path/local placement remediation required before rerunning validation-only preflight
v3.07_status = BLOCKED
NO_SUBMIT = DEFAULT
validation_only_preflight = AUTHORIZED_FOR_R1_R6_EVIDENCE_ONLY
preflight_execution = AUTHORIZED_FOR_VALIDATION_ONLY_R1_R6_EVIDENCE
sealed_dataset_read = AUTHORIZED_FOR_VALIDATION_ONLY_INSPECTION_IF_NEEDED
validation_evidence_record_creation = AUTHORIZED_FOR_R1_R6_ONLY
runtime_dependency_git_state_capture = AUTHORIZED_FOR_VALIDATION_EVIDENCE_ONLY
checksum_inventory_capture = AUTHORIZED_FOR_VALIDATION_EVIDENCE_ONLY
sealed_training_command_execution = NOT_AUTHORIZED
ppo_v2_training_execution = NOT_AUTHORIZED
training_command_execution = NOT_AUTHORIZED
model_learn = NOT_AUTHORIZED
model_fitting = NOT_AUTHORIZED
preflight_readiness = NOT_PASSED
sealed_dataset_validation = NOT_PROVEN
R1 = PASS
R2 = FAIL_SEALED_DATASET_NOT_FOUND
R3 = FAIL_DEPENDS_ON_R2
R4 = FAIL_DEPENDS_ON_R2
R5 = FAIL_DEPENDS_ON_R2
R6 = PASS
data_fetching = NOT_AUTHORIZED
dataset_generation = NOT_AUTHORIZED
model_artifact_creation = NOT_AUTHORIZED
quarantine_model_output_creation = NOT_AUTHORIZED
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf_deployment_decision = BLOCKED
ppo_xgboost_deployment_decision = BLOCKED
ppo_rf = BLOCKED
ppo_xgboost = BLOCKED
model_promotion = NOT_AUTHORIZED
production_deployment = NOT_AUTHORIZED
trading_edge_claims = NOT_AUTHORIZED
profitability_claims = NOT_AUTHORIZED
legacy_ppo_retraining_decision = DO_NOT_RETRAIN_LEGACY_MODEL
```

Always read `PROJECT_CONTEXT.md` first. Then use this map to identify supporting historical files.

---

## Current Active Review Path

### v3.07 — Sealed Dataset Availability / Path / Local Placement Remediation

**Use when reviewing**


* narrow v3.07 source-code compatibility review PASS
* failed sealed v3.07 authorization/preflight readiness review
* sealed preflight evidence remediation plan
* validation-only preflight readiness scaffold
* scaffold-only independent review PASS
* evidence remediation governance review PASS
* explicit validation-only preflight authorization PASS
* fail-closed evidence review PASS
* accepted PARTIAL_FAIL evidence result
* R1/R6 PASS
* R2 failed because sealed local dataset was not found
* R3/R4/R5 failed because dependent on R2
* sealed dataset availability/path/local placement remediation
* future validation-only preflight rerun only after sealed dataset availability/path/local placement remediation
* whether sealed local dataset availability and validation are proven
* whether data-contract, missing-bar coverage, split, embargo, holdout, and handoff checks are recorded
* whether runtime/dependency and git-state evidence exists
* whether package status remains consistent with `PROJECT_CONTEXT.md`
* whether no-submit, no-order, no-promotion, no-hybrid boundaries are preserved
* whether v3.07 remains blocked unless a later sealed checkpoint explicitly authorizes one-time no-submit PPO v2 training


**Review first**

```txt
PROJECT_CONTEXT.md
docs/workflows/milestone_review_reference_map.md
docs/audits/v3.07_independent_source_code_compatibility_review.md
docs/runs/v3.07_independent_source_code_compatibility_review.md
docs/audits/v3.07_sealed_authorization_preflight_readiness_review.md
docs/runs/v3.07_sealed_authorization_preflight_readiness_review.md
docs/runs/v3.07_sealed_preflight_evidence_remediation_plan.md
docs/runs/v3.07_sealed_preflight_readiness_scaffold_record.md
docs/audits/v3.07_sealed_preflight_readiness_scaffold_review.md
docs/runs/v3.07_sealed_preflight_readiness_scaffold_review.md
docs/audits/v3.07_sealed_preflight_evidence_remediation_review.md
docs/runs/v3.07_sealed_preflight_evidence_remediation_review.md
docs/audits/v3.07_explicit_validation_only_preflight_authorization_checkpoint.md
docs/runs/v3.07_explicit_validation_only_preflight_authorization_checkpoint.md
docs/audits/v3.07_validation_only_preflight_evidence_review_r1_r6.md
docs/runs/v3.07_validation_only_preflight_evidence_review_r1_r6.md
docs/runs/v3.07_source_code_execution_compatibility_checkpoint.md
docs/audits/v3.07_independent_package_authorization_review.md
docs/runs/v3.07_independent_package_authorization_review.md
docs/runs/v3.07_no_submit_training_execution_package_preparation.md
artifacts/ppo_v2/package_preparation/v3_07_no_submit_training_execution_package/manifests/preflight_validation_manifest.md
artifacts/ppo_v2/package_preparation/v3_07_no_submit_training_execution_package/manifests/non_authorization_boundary_manifest.md
artifacts/ppo_v2/package_preparation/v3_07_no_submit_training_execution_package/commands/one_time_no_submit_training_command.txt
artifacts/ppo_v2/package_preparation/v3_07_no_submit_training_execution_package/config/v3_07_no_submit_training_config.yaml
```

**Then review remediation target files as needed**

```txt
artifacts/ppo_v2/package_preparation/v3_07_no_submit_training_execution_package/
artifacts/ppo_v2/package_preparation/v3_07_no_submit_training_execution_package/manifests/preflight_validation_manifest.md
artifacts/ppo_v2/package_preparation/v3_07_no_submit_training_execution_package/manifests/non_authorization_boundary_manifest.md
src/ppo_v2_controlled_training_execution.py
tests/test_ppo_v2_controlled_training_execution.py
src/ppo_v2_sealed_preflight_readiness.py
tests/test_ppo_v2_sealed_preflight_readiness.py
```

**v3.06 remediation implementation closeout**

```txt
v3_06_remediation_implementation_record = COMPLETED
v3_06_independent_remediation_review = PASS
v3_06_post_remediation_audit = PASS
v3_07_initial_authorization_review = FAIL
v3_07_initial_authorization_review_audit_record = docs/audits/v3.07_no_submit_ppo_v2_training_authorization_review.md
v3_07_initial_authorization_review_run_record = docs/runs/v3.07_no_submit_ppo_v2_training_authorization_review.md
v3_07_package_preparation_record = docs/runs/v3.07_no_submit_training_execution_package_preparation.md
v3_07_package_preparation_root = artifacts/ppo_v2/package_preparation/v3_07_no_submit_training_execution_package/
v3_07_package_preparation_commit = ebc38047dd4c0ad1642a9d7feb5e330b5a243c33
v3_07_independent_package_authorization_review = FAIL
v3_07_independent_package_authorization_review_audit_record = docs/audits/v3.07_independent_package_authorization_review.md
v3_07_independent_package_authorization_review_run_record = docs/runs/v3.07_independent_package_authorization_review.md
v3_07_independent_package_authorization_review_commit = 4b32e4d35ba4e55a47555eab15e7e851c23649b3
v3_07_source_code_execution_compatibility_checkpoint = COMPLETED_FOR_REVIEW
v3_07_source_code_execution_compatibility_remediation = COMPLETED_FOR_REVIEW
v3_07_source_code_execution_compatibility_record = docs/runs/v3.07_source_code_execution_compatibility_checkpoint.md
source_code_compatibility_commit = b17fc83
source_code_compatibility_ci = Tests #332 green
v3_07_independent_source_code_compatibility_review = PASS_SOURCE_CODE_COMPATIBILITY_ONLY
v3_07_independent_source_code_compatibility_review_audit_record = docs/audits/v3.07_independent_source_code_compatibility_review.md
v3_07_independent_source_code_compatibility_review_run_record = docs/runs/v3.07_independent_source_code_compatibility_review.md
v3_07_independent_source_code_compatibility_review_commit = 3e71623
v3_07_independent_source_code_compatibility_review_ci = Tests #335 green
v3_07_authorization_preflight_readiness_review = FAIL_READINESS
v3_07_sealed_preflight_evidence_remediation_plan = RECORDED
v3_07_sealed_preflight_evidence_remediation_plan_commit = 1b3a7fc
preflight_evidence_remediation_plan_commit = 1b3a7fc
v3_07_sealed_preflight_readiness_scaffold = IMPLEMENTED_FOR_REVIEW
v3_07_sealed_preflight_readiness_scaffold_commit = bc3bf9c
preflight_readiness_scaffold_commit = bc3bf9c
v3_07_sealed_preflight_readiness_scaffold_review = PASS_SCAFFOLD_ONLY
v3_07_sealed_preflight_readiness_scaffold_review_audit_record = docs/audits/v3.07_sealed_preflight_readiness_scaffold_review.md
v3_07_sealed_preflight_readiness_scaffold_review_run_record = docs/runs/v3.07_sealed_preflight_readiness_scaffold_review.md
v3_07_sealed_preflight_readiness_scaffold_review_commit = 59167c0
preflight_scaffold_review_commit = 59167c0
v3_07_preflight_blocker_typo_fix_commit = f7e8cbc
preflight_blocker_typo_fix_commit = f7e8cbc
v3_07_sealed_preflight_evidence_remediation_review = PASS_EVIDENCE_REMEDIATION_REVIEW_ONLY
v3_07_sealed_preflight_evidence_remediation_review_audit_record = docs/audits/v3.07_sealed_preflight_evidence_remediation_review.md
v3_07_sealed_preflight_evidence_remediation_review_run_record = docs/runs/v3.07_sealed_preflight_evidence_remediation_review.md
v3_07_sealed_preflight_evidence_remediation_review_commit = b8273a9
v3_07_sealed_preflight_evidence_remediation_review_ci = Tests #343 green
v3_07_sealed_training_command_execution = NOT_AUTHORIZED
v3_07_explicit_validation_only_preflight_authorization_checkpoint = PASS_VALIDATION_ONLY_PREFLIGHT_AUTHORIZATION
v3_07_explicit_validation_only_preflight_authorization_audit_record = docs/audits/v3.07_explicit_validation_only_preflight_authorization_checkpoint.md
v3_07_explicit_validation_only_preflight_authorization_run_record = docs/runs/v3.07_explicit_validation_only_preflight_authorization_checkpoint.md
v3_07_validation_only_preflight = AUTHORIZED_FOR_R1_R6_EVIDENCE_ONLY
v3_07_preflight_execution = AUTHORIZED_FOR_VALIDATION_ONLY_R1_R6_EVIDENCE
v3_07_sealed_dataset_read = AUTHORIZED_FOR_VALIDATION_ONLY_INSPECTION_IF_NEEDED
v3_07_validation_evidence_record_creation = AUTHORIZED_FOR_R1_R6_ONLY
v3_07_runtime_dependency_git_state_capture = AUTHORIZED_FOR_VALIDATION_EVIDENCE_ONLY
v3_07_checksum_inventory_capture = AUTHORIZED_FOR_VALIDATION_EVIDENCE_ONLY
v3_07_validation_only_preflight_evidence_review = PASS_FAIL_CLOSED_EVIDENCE_REVIEW_ONLY
v3_07_validation_only_preflight_evidence_review_audit_record = docs/audits/v3.07_validation_only_preflight_evidence_review_r1_r6.md
v3_07_validation_only_preflight_evidence_review_run_record = docs/runs/v3.07_validation_only_preflight_evidence_review_r1_r6.md
v3_07_validation_only_preflight_evidence_review_commit = a5a5d58
v3_07_validation_only_preflight_evidence_review_ci = Tests #348 green
v3_07_accepted_preflight_result = PARTIAL_FAIL
v3_07_R1 = PASS
v3_07_R2 = FAIL_SEALED_DATASET_NOT_FOUND
v3_07_R3 = FAIL_DEPENDS_ON_R2
v3_07_R4 = FAIL_DEPENDS_ON_R2
v3_07_R5 = FAIL_DEPENDS_ON_R2
v3_07_R6 = PASS
v3_07_sealed_dataset_availability_path_local_placement_remediation = NEXT_ACTIVE_MILESTONE
v3_07_validation_only_preflight_rerun = FUTURE_ONLY_AFTER_SEALED_DATASET_AVAILABILITY_PATH_LOCAL_PLACEMENT_REMEDIATION
v3.07 validation-only preflight evidence review = PASS_FAIL_CLOSED_EVIDENCE_REVIEW_ONLY
v3.07 accepted preflight result = PARTIAL_FAIL
v3.07 sealed dataset availability/path/local placement remediation = next active milestone
v3.07 validation-only preflight rerun = future only after sealed dataset availability/path/local placement remediation
v3.07 PPO v2 training = NOT_AUTHORIZED
sealed training command execution = NOT_AUTHORIZED
preflight_readiness = NOT_PASSED
sealed_dataset_validation = NOT_PROVEN
v3.07_status = BLOCKED
validation_only_preflight = AUTHORIZED_FOR_R1_R6_EVIDENCE_ONLY
preflight_execution = AUTHORIZED_FOR_VALIDATION_ONLY_R1_R6_EVIDENCE
sealed_dataset_read = AUTHORIZED_FOR_VALIDATION_ONLY_INSPECTION_IF_NEEDED
sealed_training_command_execution = NOT_AUTHORIZED
ppo_v2_training_execution = NOT_AUTHORIZED
training_command_execution = NOT_AUTHORIZED
model_learn = NOT_AUTHORIZED
model_fitting = NOT_AUTHORIZED
data_fetching = NOT_AUTHORIZED
dataset_generation = NOT_AUTHORIZED
model_artifact_creation = NOT_AUTHORIZED
quarantine_model_output_creation = NOT_AUTHORIZED
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf = BLOCKED
ppo_xgboost = BLOCKED
model_promotion = NOT_AUTHORIZED
production_deployment = NOT_AUTHORIZED
trading_edge_claims = NOT_AUTHORIZED
profitability_claims = NOT_AUTHORIZED
latest_ci_evidence = Tests #348 green on fail-closed preflight evidence review commit a5a5d58
```

The v3.06 remediation review / post-remediation audit passed, making the repository eligible for separate v3.07 consideration but not authorizing v3.07 execution. The initial v3.07 authorization review failed. A materially more complete v3.07 static no-submit package-preparation record was then created at `docs/runs/v3.07_no_submit_training_execution_package_preparation.md`. The independent v3.07 package authorization review also failed. The source-code execution compatibility checkpoint was then completed for independent review, and the independent source-code compatibility review passed for source-code compatibility only. That narrow PASS resolved the command-target/CLI argument compatibility blocker for the sealed command target. The sealed authorization/preflight readiness review then failed because R1-R6 evidence was absent. A documentation-only remediation plan was recorded, a validation-only preflight readiness scaffold was implemented, an independent scaffold review passed with `PASS_SCAFFOLD_ONLY`, the non-blocking R1 preflight blocker constant typo was fixed, the evidence remediation review passed with `PASS_EVIDENCE_REMEDIATION_REVIEW_ONLY`, the explicit validation-only preflight authorization checkpoint passed with `PASS_VALIDATION_ONLY_PREFLIGHT_AUTHORIZATION`, validation-only preflight produced PARTIAL_FAIL R1-R6 evidence, and the fail-closed evidence review passed with `PASS_FAIL_CLOSED_EVIDENCE_REVIEW_ONLY`. The PARTIAL_FAIL result is accepted as valid evidence, not readiness. R1 and R6 passed, R2 failed because the sealed local dataset was not found, and R3/R4/R5 failed because they depend on R2. Preflight readiness remains `NOT_PASSED`, sealed dataset validation remains `NOT_PROVEN`, PPO v2 training remains `NOT_AUTHORIZED`, and sealed training command execution remains `NOT_AUTHORIZED`. The next active remediation is sealed dataset availability/path/local placement only. Do not authorize data fetching, dataset generation, or training.

**M/L cleanup note**

```txt
v2_79_pending_evidence_references = SUPERSEDED_BY_v2_83_POST_IMPLEMENTATION_AUDIT
latest_historical_evidence_contract_usage_test_count = 531 passed, 2 warnings
broker_read_fail_closed_hardening = CONTROLLED_SUBMIT_BACKLOG_ONLY
non_authorization_language_policy = USE_PROJECT_CONTEXT_AND_GLOBAL_GUARDRAIL_AS_CURRENT_STATE
```

Use v2.83 when quoting the evidence-contract usage adapter's audited test evidence. Do not copy stale v2.79 pending evidence into active readiness summaries.

Broker-read fail-closed hardening remains a controlled-submit backlog item only. It does not authorize broker calls, broker reads, paper orders, live orders, or controlled submit.

To reduce drift risk, use `PROJECT_CONTEXT.md` plus this map's Global Guardrail for current authorization state instead of duplicating long non-authorization blocks from archived milestone files.


**Historical context for remediation**

```txt
docs/reviews/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
docs/runs/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
docs/reviews/v3.04_ppo_v2_evidence_gap_review.md
docs/runs/v3.04_ppo_v2_evidence_gap_review.md
docs/archive/evidence_contract_usage_chain_v2_76_v3_02.md
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

**v3.06 remediation boundary**

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
v3.07 = BLOCKED
NO_SUBMIT = DEFAULT
```

**Then move to**

Move only to `v3.07 Sealed Dataset Availability / Path / Local Placement Remediation`. The fail-closed PARTIAL_FAIL evidence review passed and accepted the result as valid evidence, not readiness. R1 and R6 passed, R2 failed because the sealed local dataset was not found, and R3/R4/R5 failed because they depend on R2. Validation-only preflight rerun is future-only after sealed dataset availability/path/local placement remediation. Do not authorize PPO v2 training, sealed training command execution, v3.07 training execution, data fetching, dataset generation, model artifacts, quarantine model outputs, paper/live orders, controlled submit, PPO + RF, PPO + XGBoost, model promotion, production deployment, trading-edge claims, or profitability claims.

---

## Near-Term PPO v2 Roadmap

```txt
v3.02 = final administrative closeout of archived evidence-contract usage chain
v3.03 = archived-chain transition review; workstream moved to PPO v2 validation readiness
v3.04 = evidence gap review; PPO v2 executable validation evidence not yet generated
v3.05 = no-submit training package readiness review; ready for independent audit only
v3.06 = independent full-system pre-retraining audit completed, FAIL
v3.06 remediation implementation closeout = completed
v3.06 remediation completion record = completed and tagged
v3.06 independent remediation review / post-remediation audit rerun = PASS
v3.07 initial authorization review = FAIL — do not authorize training
v3.07 sealed no-submit training execution package preparation = completed as static package-preparation only
v3.07 independent package authorization review = FAIL — do not authorize training
v3.07 source-code execution compatibility checkpoint = completed for independent review
v3.07 independent source-code compatibility review = PASS_SOURCE_CODE_COMPATIBILITY_ONLY
v3.07 sealed authorization/preflight readiness review = FAIL_READINESS
v3.07 sealed preflight evidence remediation plan = recorded
v3.07 sealed preflight readiness scaffold = implemented
v3.07 sealed preflight readiness scaffold review = PASS_SCAFFOLD_ONLY
v3.07 sealed preflight evidence remediation review = PASS_EVIDENCE_REMEDIATION_REVIEW_ONLY
v3.07 explicit validation-only preflight authorization checkpoint = PASS_VALIDATION_ONLY_PREFLIGHT_AUTHORIZATION
v3.07 validation-only preflight = AUTHORIZED_FOR_R1_R6_EVIDENCE_ONLY
v3.07 validation-only preflight execution = COMPLETED_WITH_PARTIAL_FAIL
v3.07 Validation-Only Preflight Evidence Review / R1-R6 Evidence Review = PASS_FAIL_CLOSED_EVIDENCE_REVIEW_ONLY
v3.07 accepted preflight result = PARTIAL_FAIL
v3.07 sealed dataset availability/path/local placement remediation = next active milestone
v3.07 validation-only preflight rerun = future only after sealed dataset availability/path/local placement remediation
v3.07 preflight execution = AUTHORIZED_FOR_VALIDATION_ONLY_R1_R6_EVIDENCE
v3.07 sealed dataset read = AUTHORIZED_FOR_VALIDATION_ONLY_INSPECTION_IF_NEEDED
v3.07 execution = BLOCKED for PPO v2 training
PPO v2 training = NOT_AUTHORIZED
sealed training command execution = NOT_AUTHORIZED
v3.08 = post-run audit of generated PPO v2 evidence; future only and only after v3.07 is authorized/completed
v3.09 = validation report generation from real evidence; future only
v3.10 = PPO v2 model evidence decision; future only
```

v3.07 execution is not active for PPO v2 training. The v3.07 package-preparation record exists, the independent package authorization review failed, the source-code execution compatibility checkpoint was completed for independent review, the independent source-code compatibility review passed for source-code compatibility only, the sealed authorization/preflight readiness review failed, the sealed preflight evidence remediation plan was recorded, the validation-only preflight readiness scaffold was implemented, the independent scaffold review passed for scaffold-only safety, the evidence remediation governance review passed, the explicit validation-only preflight authorization checkpoint passed, validation-only preflight produced PARTIAL_FAIL evidence, and the fail-closed evidence review passed. The PARTIAL_FAIL result is accepted as valid evidence, not readiness. R1 and R6 passed, R2 failed because the sealed local dataset was not found, and R3/R4/R5 failed because they depend on R2. Preflight readiness remains `NOT_PASSED`, sealed dataset validation remains `NOT_PROVEN`, and the next active remediation is sealed dataset availability/path/local placement only. PPO v2 training, sealed training command execution, paper/live orders, controlled submit, model promotion, PPO + RF, and PPO + XGBoost remain blocked.

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
v2.79        read-only usage adapter implementation; pending evidence references superseded by v2.83
v2.80        implementation review
v2.81-v2.82  post-implementation audit planning and review
v2.83        audit completed with PASS_READ_ONLY_NO_SUBMIT and 531 passed, 2 warnings
v2.84        audit review accepted
v2.85-v2.86  chain closed and archived
v2.87-v3.01  administrative archived-chain final/terminal closeout sequence
v3.02        final administrative closeout
v3.03        transition review; archived chain remained closed
```

The adapter wraps the existing v2.59 evidence contract, uses static evidence manifest input only, returns `EvidenceContractResult` only, fails closed, and remains read-only and no-submit.

No checkpoint in this chain authorized PPO training, data fetching, dataset generation, model artifact creation, quarantine output creation, metric computation, report/plot/dashboard generation, model promotion, paper orders, live orders, controlled submit, PPO + RF unblock, or PPO + XGBoost unblock.

---

### v3.04-v3.06 — Evidence Gap, Training Package Readiness, and Independent Audit

**Use when reviewing**

* evidence gaps before PPO v2 training
* whether the no-submit package was ready for independent audit
* why v3.06 failed
* remediation requirements before v3.07 can be reconsidered
* confirmation that package readiness and audit documentation are not execution authorization

**Review first**

```txt
PROJECT_CONTEXT.md
docs/reviews/v3.04_ppo_v2_evidence_gap_review.md
docs/runs/v3.04_ppo_v2_evidence_gap_review.md
docs/reviews/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
docs/runs/v3.05_ppo_v2_no_submit_training_package_readiness_review.md
docs/audits/v3.06_ppo_v2_independent_full_system_pre_retraining_audit.md
docs/runs/v3.06_ppo_v2_independent_full_system_pre_retraining_audit.md
```

**Summary**

```txt
v3.04 primary_gap = PPO_V2_EXECUTABLE_VALIDATION_EVIDENCE_NOT_YET_GENERATED
v3.04 training_readiness = NOT_READY
v3.05 training_package_status = READY_FOR_INDEPENDENT_FULL_SYSTEM_PRE_RETRAINING_AUDIT
v3.05 training_execution_status = NOT_AUTHORIZED
v3.06 audit_decision = FAIL
v3.06 remediation_status = REQUIRED_BEFORE_v3.07
```

**Then move to**

v3.06 audit remediation planning, implementation, and review. Do not move to v3.07 unless remediation passes and a later review explicitly authorizes one-time no-submit PPO v2 training execution.

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
v3.07 = BLOCKED for PPO v2 training until a later sealed checkpoint explicitly authorizes one-time no-submit training execution
validation_only_preflight = AUTHORIZED_FOR_R1_R6_EVIDENCE_ONLY
sealed_training_command_execution = NOT_AUTHORIZED
```
