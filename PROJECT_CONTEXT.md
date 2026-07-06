# PROJECT_CONTEXT.md

Authoritative source-of-truth document for `racoope70/ppo-trading-pipeline`.

This file defines the current project state, active milestone, validation standards, deployment constraints, blocked actions, research progression, and audit boundaries for the PPO trading pipeline.

Before modifying training logic, validation methodology, deployment workflows, artifact management, broker integration, or milestone documentation, review this file first and then use `docs/workflows/milestone_review_reference_map.md` for supporting historical navigation.

---

## 1. Current Source-of-Truth Summary

```txt
latest_completed_milestone = v3.07 Sealed Preflight Readiness Scaffold Review
latest_completed_decision = PASS_SCAFFOLD_ONLY
latest_completed_audit_tag = NOT_TAGGED
latest_completed_audit_record = docs/audits/v3.07_sealed_preflight_readiness_scaffold_review.md
latest_completed_run_record = docs/runs/v3.07_sealed_preflight_readiness_scaffold_review.md
latest_successful_sealed_readiness_tag = v3.05-ppo-v2-no-submit-training-package-readiness-review
latest_successful_sealed_readiness_commit = c9f2c71292a82ee5d528ab179a17792dbff4f477
latest_successful_sealed_readiness_commit_short = c9f2c71
active_milestone = v3.07 Sealed Preflight Evidence Remediation Review
next_checkpoint = sealed preflight evidence remediation review before any validation-only preflight can be considered
current_workstream = PPO_V2_VALIDATION_READINESS
current_phase = scaffold reviewed and accepted for scaffold-only safety; R1-R6 evidence remains absent
v3.07_status = BLOCKED
NO_SUBMIT = DEFAULT
training_command_execution = NOT_AUTHORIZED
preflight_readiness = NOT_PASSED
sealed_dataset_validation = NOT_PROVEN
data_fetching = NOT_AUTHORIZED
dataset_generation = NOT_AUTHORIZED
model_artifact_creation = NOT_AUTHORIZED
quarantine_output_creation = NOT_AUTHORIZED
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf_deployment_decision = BLOCKED
ppo_xgboost_deployment_decision = BLOCKED
ppo_rf = BLOCKED
ppo_xgboost = BLOCKED
legacy_ppo_classification = INFRASTRUCTURE_FIXTURE_ONLY
legacy_ppo_retraining_decision = DO_NOT_RETRAIN_LEGACY_MODEL
ppo_v2_training_execution = NOT_AUTHORIZED
ppo_v2_training_outputs = NOT_CREATED
ppo_v2_executable_validation_evidence = NOT_YET_GENERATED
v3_06_remediation_implementation_record = COMPLETED
v3_06_remediation_completion_record = docs/runs/v3.06_remediation_completion_record.md
v3_06_remediation_completion_tag = v3.06-remediation-completion-record
v3_06_remediation_completion_commit = 115629c5edcb6d294c846f57a01de8c063878c5b
v3_06_independent_remediation_review = PASS
v3_06_post_remediation_audit = PASS
v3_06_remediation_review_follow_up_evidence = docs/runs/v3.06_remediation_review_follow_up_evidence.md
v3_06_remediation_review_follow_up_commit = d00d8fff076c70385fc5a6303b18493be267a199
v3_06_post_remediation_pass_audit_record = docs/audits/v3.06_remediation_review_post_remediation_audit_pass.md
v3_06_post_remediation_pass_run_record = docs/runs/v3.06_remediation_review_post_remediation_audit_pass.md
v3_06_post_remediation_pass_commit = 62cc3b2
v3_07_authorization_review = FAIL
v3_07_authorization_review_audit_record = docs/audits/v3.07_no_submit_ppo_v2_training_authorization_review.md
v3_07_authorization_review_run_record = docs/runs/v3.07_no_submit_ppo_v2_training_authorization_review.md
v3_07_authorization_review_commit = 703cfd9
v3_07_package_preparation_record = docs/runs/v3.07_no_submit_training_execution_package_preparation.md
v3_07_package_preparation_root = artifacts/ppo_v2/package_preparation/v3_07_no_submit_training_execution_package/
v3_07_package_preparation_commit = ebc38047dd4c0ad1642a9d7feb5e330b5a243c33
v3_07_package_preparation_ci = Tests #328 green on commit ebc3804
v3_07_independent_package_authorization_review = FAIL
v3_07_independent_package_authorization_review_audit_record = docs/audits/v3.07_independent_package_authorization_review.md
v3_07_independent_package_authorization_review_run_record = docs/runs/v3.07_independent_package_authorization_review.md
v3_07_independent_package_authorization_review_commit = 4b32e4d35ba4e55a47555eab15e7e851c23649b3
v3_07_source_code_execution_compatibility_checkpoint = COMPLETED_FOR_REVIEW
v3_07_source_code_execution_compatibility_remediation = COMPLETED_FOR_REVIEW
v3_07_source_code_execution_compatibility_record = docs/runs/v3.07_source_code_execution_compatibility_checkpoint.md
source_code_compatibility_commit = b17fc83
source_code_compatibility_ci = Tests #332 green
source_code_compatibility_review_commit = 3e71623
source_code_compatibility_review_ci = Tests #335 green
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
v3_07_sealed_preflight_evidence_remediation_review = NEXT_REQUIRED_CHECKPOINT
latest_ci_evidence = Tests #341 green on preflight blocker typo fix commit f7e8cbc
```

The repository completed the v3.06 independent full-system pre-retraining audit with a `FAIL` decision, then completed remediation and a post-remediation audit rerun with a `PASS` decision. A separate v3.07 No-Submit PPO v2 Training Authorization Review was completed with a `FAIL` decision. A corrective v3.07 static package-preparation record was then created at `docs/runs/v3.07_no_submit_training_execution_package_preparation.md`. The independent v3.07 package authorization review then failed. The v3.07 source-code execution compatibility checkpoint was completed for independent review, and the independent v3.07 source-code compatibility review then passed for source-code compatibility only. The sealed authorization/preflight readiness review then failed because R1-R6 evidence was absent. A documentation-only remediation plan was recorded, a validation-only preflight readiness scaffold was implemented, and an independent scaffold review passed with `PASS_SCAFFOLD_ONLY`. The non-blocking R1 preflight blocker constant typo was fixed afterward. The scaffold pass is not a readiness pass: R1-R6 evidence remains absent, preflight has not executed, the sealed dataset has not been read or validated, v3.07 remains blocked, and PPO v2 training and training command execution remain not authorized. The next checkpoint is `v3.07 Sealed Preflight Evidence Remediation Review`. Only after that review may the repository consider whether to proceed to an explicitly authorized validation-only preflight. Even validation-only preflight must not authorize PPO v2 training or execute the sealed training command.

## v3.06 Audit Result

The following block is a historical snapshot from the v3.06 PASS checkpoint. It is preserved for audit traceability only and does not override the current source-of-truth summary in Section 1.

```txt
historical_snapshot = v3.06 Remediation Review / Post-Remediation Audit Rerun
historical_snapshot_scope = preserved audit state at v3.06 PASS
latest_completed_milestone_at_snapshot = v3.06 Remediation Review / Post-Remediation Audit Rerun
latest_completed_decision_at_snapshot = PASS
latest_completed_audit_tag_at_snapshot = v3.06-ppo-v2-independent-full-system-pre-retraining-audit-fail
latest_successful_sealed_readiness_tag_at_snapshot = v3.05-ppo-v2-no-submit-training-package-readiness-review
latest_successful_sealed_readiness_commit_at_snapshot = c9f2c71292a82ee5d528ab179a17792dbff4f477
latest_successful_sealed_readiness_commit_short_at_snapshot = c9f2c71
active_milestone_at_snapshot = v3.07 Consideration / Authorization Review
next_checkpoint_at_snapshot = separate v3.07 consideration / authorization review
v3.07_status_at_snapshot = BLOCKED
ppo_v2_training_execution_at_snapshot = NOT_AUTHORIZED
paper_order_authorization_at_snapshot = NOT_AUTHORIZED
live_order_authorization_at_snapshot = NOT_AUTHORIZED
controlled_submit_at_snapshot = BLOCKED
ppo_rf_at_snapshot = BLOCKED
ppo_xgboost_at_snapshot = BLOCKED
```

The v3.06 independent full-system pre-retraining audit completed with a `FAIL` decision.

The repository is not ready for v3.07 consideration until blocking audit findings are remediated and reviewed.

Blocking findings:

```txt
B1 = paper-trading workflow authorization conflicts
B2 = README training/data-command ambiguity
B3 = PPO v2 quarantine/log ignore-policy gap
B4 = missing-bar coverage requirement not implemented/tested
B5 = tracked package-preparation artifact policy ambiguity
```

The v3.06 audit does not authorize PPO v2 training, data fetching, dataset generation, model artifact creation, paper orders, live orders, controlled submit, PPO + RF, PPO + XGBoost, or legacy PPO retraining.

This is important because `PROJECT_CONTEXT.md` is the controlling source of truth. The reference map controls supporting navigation only; it does not override current state, authorization boundaries, blocked actions, or the PPO v2 roadmap.

---

## 2. Active Milestone: v3.07 Sealed Preflight Evidence Remediation Review

v3.06 remediation implementation closeout has been completed and accepted, the initial v3.07 authorization review failed, the v3.07 static package-preparation record was completed, the independent v3.07 package authorization review failed, the v3.07 source-code execution compatibility checkpoint was completed for independent review, and the independent v3.07 source-code compatibility review passed for source-code compatibility only. The sealed v3.07 authorization/preflight readiness review then failed because R1-R6 evidence was absent. The repository recorded a documentation-only sealed preflight evidence remediation plan, implemented a validation-only preflight readiness scaffold, and recorded an independent scaffold review with `PASS_SCAFFOLD_ONLY`. The scaffold pass means only that the Phase 2 scaffold safely implements a validation-only, fail-closed structure for future R1-R6 evidence review. It does not mean readiness passed, preflight executed, preflight passed, the sealed dataset was read or validated, v3.07 was authorized, PPO v2 training was authorized, or training command execution was authorized.

This closeout is documented in:

```txt
docs/runs/v3.06_remediation_completion_record.md
tag = v3.06-remediation-completion-record
commit = 115629c5edcb6d294c846f57a01de8c063878c5b
failed_audit_cleanup_evidence = docs/runs/v3.06_remediation_review_follow_up_evidence.md
failed_audit_cleanup_commit = d00d8fff076c70385fc5a6303b18493be267a199
```

The closeout record and v3.06 remediation PASS are not authorization for v3.07 execution. The failed-audit cleanup follow-up is documented in `docs/runs/v3.06_remediation_review_follow_up_evidence.md`, the passing post-remediation audit rerun is documented in `docs/audits/v3.06_remediation_review_post_remediation_audit_pass.md` and `docs/runs/v3.06_remediation_review_post_remediation_audit_pass.md`, the initial failed v3.07 authorization review is documented in `docs/audits/v3.07_no_submit_ppo_v2_training_authorization_review.md` and `docs/runs/v3.07_no_submit_ppo_v2_training_authorization_review.md`, the v3.07 package-preparation record is documented in `docs/runs/v3.07_no_submit_training_execution_package_preparation.md`, the failed independent package authorization review is documented in `docs/audits/v3.07_independent_package_authorization_review.md` and `docs/runs/v3.07_independent_package_authorization_review.md`, the source-code execution compatibility checkpoint is documented in `docs/runs/v3.07_source_code_execution_compatibility_checkpoint.md`, the narrow source-code compatibility review PASS is documented in `docs/audits/v3.07_independent_source_code_compatibility_review.md` and `docs/runs/v3.07_independent_source_code_compatibility_review.md`, and the scaffold-only review PASS is documented in `docs/audits/v3.07_sealed_preflight_readiness_scaffold_review.md` and `docs/runs/v3.07_sealed_preflight_readiness_scaffold_review.md`. The next required checkpoint is `v3.07 Sealed Preflight Evidence Remediation Review` before any validation-only preflight can be considered.

The independent package authorization review found that the v3.07 package is materially more complete than the prior failed package, but authorization still failed because:

```txt
B1 = selected command still points to a non-executing scaffold
B2 = sealed command arguments are not implemented by the target module
B3 = preflight evidence has not passed
B4 = package itself says B3/B5 are not fully resolved
B5 = package remains static preparation only / do-not-run
B6 = sealed local input dataset is not proven available or validated
```

The next checkpoint may inspect source-code execution compatibility and command-argument compatibility. It must not run training, fetch data, generate datasets, create model artifacts, create quarantine outputs, submit paper/live orders, authorize controlled submit, authorize PPO + RF/XGBoost, or mark v3.07 as authorized.

The source-code execution compatibility checkpoint addressed the source-code compatibility portion of the failed package review by adding fail-closed CLI compatibility validation for the sealed v3.07 command target. The selected sealed command path remains `src.ppo_v2_controlled_training_execution`; it was not revised to `src.train.py`. The compatibility layer validates the sealed `--mode`, `--run-id`, `--config`, `--quarantine-root`, `--log-root`, `--stdout-path`, `--stderr-path`, `--artifact-inventory-path`, `--checksum-manifest-path`, and `--no-submit` arguments. This compatibility checkpoint does not claim preflight passed, does not prove the sealed dataset exists or is validated, does not authorize training command execution, and does not authorize creation of model artifacts or quarantine outputs.

The independent source-code compatibility review accepted the source-code/CLI compatibility remediation for this narrow checkpoint only. It resolved the command-target/CLI argument compatibility blocker for the sealed command target. It did not authorize v3.07 execution, did not authorize PPO v2 training, did not authorize training command execution, did not prove preflight passed, did not prove sealed dataset availability or validation, did not prove execution readiness, did not authorize model artifact creation, and did not authorize quarantine output creation.

The sealed authorization/preflight readiness review found that R1-R6 evidence remained absent. The documentation-only remediation plan was recorded in commit `1b3a7fc`, the validation-only preflight readiness scaffold was implemented in commit `bc3bf9c`, the independent scaffold review passed with `PASS_SCAFFOLD_ONLY` in commit `59167c0`, and the non-blocking R1 preflight blocker constant typo was fixed in commit `f7e8cbc` with Tests #341 green. The scaffold review pass does not authorize readiness, preflight execution, sealed dataset reads, sealed dataset validation, v3.07 execution, PPO v2 training, training command execution, data fetching, dataset generation, model artifact creation, quarantine output creation, stdout/stderr/log/checksum/inventory writes, paper/live orders, controlled submit, PPO + RF, or PPO + XGBoost.

The broader R1-R6 readiness blockers remain open for the next sealed preflight evidence remediation review.

The completed remediation implementation covered:

```txt
B1 paper-trading workflow authorization conflicts
B2 README training/data-command ambiguity
B3 PPO v2 quarantine/log ignore-policy gap
B4 missing-bar coverage requirement not implemented/tested
B5 tracked package-preparation artifact policy ambiguity
H1 future no-submit command-boundary cleanup
non-blocking cleanup backlog items
B4 corrective follow-up observed-session missing-bar scope correction
failed-audit cleanup for M1 stale test-count, README current-stage drift, and exact command-level evidence
```

v3.06 remediation review / post-remediation audit may inspect the remediation commits and completion record. It must not train PPO, fetch market data, generate datasets, create model artifacts, compute validation metrics from new PPO v2 outputs, generate reports from new PPO v2 outputs, promote models, submit paper/live orders, authorize controlled submit, authorize v3.07, or unblock hybrid models unless a later sealed checkpoint explicitly changes the authorization state.

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

## Future Hardening / Post-Remediation Backlog

### Future Hardening — Alpaca-Aligned Exchange Calendar Coverage

Current B4 remediation uses observed symbol/date session missing-bar coverage. This prevents false missing-bar failures across overnight, weekend, and cross-date gaps while preserving detection of missing bars inside observed intraday sessions.

Before production-grade PPO v2 retraining expansion, paper-trading expansion, or controlled-submit consideration, add a reviewed Alpaca-aligned exchange-calendar coverage check. The future check should compare observed bars against expected Alpaca/market-session bars, including regular trading sessions, holidays, early closes, and any explicitly authorized extended-hours assumptions.

This is a future hardening item only. It does not authorize v3.07 training, data fetching, dataset generation, model artifact creation, paper orders, live orders, controlled submit, PPO + RF, or PPO + XGBoost.

---


## 4. Latest Completed Milestone: v3.06 Audit

v3.06 completed the independent full-system pre-retraining audit and returned a `FAIL` decision.

```txt
latest_completed_milestone = v3.06 Remediation Review / Post-Remediation Audit Rerun
latest_completed_decision = PASS
latest_completed_audit_tag = v3.06-ppo-v2-independent-full-system-pre-retraining-audit-fail
v3_06_decision = FAIL
v3_07_status = BLOCKED
training_execution_status = NOT_AUTHORIZED
next_required_checkpoint = v3.06 Audit Remediation Plan
source_code_modified_in_v3_06_audit = NO
training_execution = NOT_PERFORMED
command_execution = NOT_PERFORMED
data_fetching = NOT_PERFORMED
dataset_generation = NOT_PERFORMED
model_artifact_creation = NOT_PERFORMED
quarantine_training_outputs = NOT_CREATED
metric_computation_from_new_outputs = NOT_PERFORMED
report_generation_from_new_outputs = NOT_PERFORMED
model_promotion = NOT_AUTHORIZED
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf = BLOCKED
ppo_xgboost = BLOCKED
NO_SUBMIT = DEFAULT
```

Blocking findings from v3.06:

```txt
B1 = paper-trading workflow authorization conflicts
B2 = README training/data-command ambiguity
B3 = PPO v2 quarantine/log ignore-policy gap
B4 = missing-bar coverage requirement not implemented/tested
B5 = tracked package-preparation artifact policy ambiguity
```

Primary v3.06 documents:

```txt
docs/audits/v3.06_ppo_v2_independent_full_system_pre_retraining_audit.md
docs/runs/v3.06_ppo_v2_independent_full_system_pre_retraining_audit.md
```

Most recent sealed successful readiness milestone:

```txt
v3.05 = PPO v2 No-Submit Training Package Readiness Review
latest_successful_sealed_readiness_tag = v3.05-ppo-v2-no-submit-training-package-readiness-review
latest_successful_sealed_readiness_commit = c9f2c71292a82ee5d528ab179a17792dbff4f477
latest_successful_sealed_readiness_commit_short = c9f2c71
v3.05_test_evidence = 531 passed, 2 warnings
```

---

## 5. Recent Roadmap Position

```txt
v3.02 = final administrative closeout of archived evidence-contract usage chain
v3.03 = archived-chain transition review; active workstream moved to PPO v2 validation readiness
v3.04 = evidence gap review; confirmed PPO v2 lacks executable validation evidence
v3.05 = no-submit training package readiness review; ready for independent audit only
v3.06 = independent full-system pre-retraining audit completed, FAIL
v3.06 remediation planning = active
v3.06 remediation implementation closeout = completed
v3.06 independent remediation review / post-remediation audit = required
v3.07 initial no-submit PPO v2 training authorization review = FAIL
v3.07 sealed no-submit training execution package preparation = completed as static package-preparation only
v3.07 independent package authorization review = FAIL
v3.07 source-code execution compatibility checkpoint = completed for independent review
v3.07 independent source-code compatibility review = PASS_SOURCE_CODE_COMPATIBILITY_ONLY
v3.07 sealed authorization/preflight readiness review = FAIL_READINESS
v3.07 sealed preflight evidence remediation plan = recorded
v3.07 sealed preflight readiness scaffold = implemented
v3.07 sealed preflight readiness scaffold review = PASS_SCAFFOLD_ONLY
v3.07 sealed preflight evidence remediation review = next required checkpoint
v3.07 validation-only preflight = NOT_AUTHORIZED
v3.07 execution = BLOCKED until a later sealed checkpoint explicitly authorizes one-time no-submit PPO v2 training
v3.08 = post-run audit of generated PPO v2 evidence, only after v3.07 is authorized and completed
v3.09 = validation report generation from real evidence, only after post-run audit
v3.10 = PPO v2 model evidence decision, only after validation reporting
```

v3.07 execution is not active. The v3.07 package-preparation record exists, the independent package authorization review failed, the source-code execution compatibility checkpoint was completed for independent review, the independent source-code compatibility review passed for source-code compatibility only, the sealed authorization/preflight readiness review failed, the sealed preflight evidence remediation plan was recorded, the validation-only preflight readiness scaffold was implemented, and the independent scaffold review passed for scaffold-only safety. The scaffold pass is not a readiness pass. R1-R6 evidence remains absent, preflight has not executed, the sealed dataset has not been read or validated, and the next checkpoint is `v3.07 Sealed Preflight Evidence Remediation Review`. PPO v2 training and training command execution remain blocked unless a later sealed checkpoint explicitly authorizes one-time no-submit PPO v2 training.

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

### Evidence Gap and Training Package Readiness: v3.04-v3.06

```txt
v3.04 primary_gap = PPO_V2_EXECUTABLE_VALIDATION_EVIDENCE_NOT_YET_GENERATED
v3.04 training_readiness = NOT_READY
v3.05 training_package_status = READY_FOR_INDEPENDENT_FULL_SYSTEM_PRE_RETRAINING_AUDIT
v3.05 training_execution_status = NOT_AUTHORIZED
v3.06 audit_decision = FAIL
v3.06 remediation_status = REQUIRED_BEFORE_v3.07
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

Before any one-time no-submit PPO v2 training execution can be considered, remediation and later review must confirm:

```txt
v3.06 blocking findings remediated
reviewed training command
reviewed no-submit execution wrapper or command boundary
validated static data input contract, including missing-bar coverage/reporting
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
independent remediation review before execution
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

Current v3.06 docs:

```txt
docs/audits/v3.06_ppo_v2_independent_full_system_pre_retraining_audit.md
docs/runs/v3.06_ppo_v2_independent_full_system_pre_retraining_audit.md
```

Most recent sealed successful readiness docs:

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

## 11. Core Architecture and Critical Module Inventory

The intended architecture remains staged so model output is never treated as immediate trade approval.

```txt
Market Data Layer
Feature Engineering Layer
Safe Feature Manifest
PPO Training Layer
Validation + Candidate Selection
Paper-Trading Dry Run
Dry-Run Evaluation
Execution Plan
Risk Controls
Pre-Trade Checklist
Supervised Paper-Order Runner
Broker Verification
Audit + Monitoring
Decision Documentation
```

Module map for onboarding and audit review:

```txt
Data Layer:
  src/data/alpaca_historical_data.py
  src/data/alpaca_training_dataset.py

Feature Engineering:
  src/features.py
  src/feature_manifest.py

Training and Validation:
  src/train.py
  src/training_splits.py
  src/vecnormalize_utils.py
  src/env.py

Alpaca Adapter Layer:
  src/adapters/alpaca.py

Paper-Trading Deployment Layer:
  src/paper_trading/paper_trade_dry_run.py
  src/paper_trading/evaluate_dry_run.py
  src/paper_trading/build_execution_plan.py
  src/paper_trading/risk_controls.py
  src/paper_trading/filter_execution_plan.py
  src/paper_trading/paper_trade_loop.py
  src/paper_trading/pre_trade_checklist.py
  src/paper_trading/logging_utils.py

Paper-Trading Reporting Layer:
  src/paper_trading/classify_decision_state.py
  src/paper_trading/pipeline_decision_state_hook.py
  src/paper_trading/build_run_summary_with_decision_state.py
  src/paper_trading/build_decision_dashboard_with_state.py
  src/paper_trading/reporting_chain_smoke_test.py
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

## 12. Paper-Trading Operational Runbook Preservation

Normal paper-trading monitoring remains no-submit by default. The detailed no-submit monitoring workflow should remain in `docs/workflows/paper_trading_operational_reporting_runbook.md`, not repeated as the main source-of-truth narrative.

Expected no-submit pass conditions:

```txt
Evaluation result = PASS
Risk result = PASS
Checklist result = PASS
predict_ok_count = expected universe size
error_count = 0
orders_submitted = 0
submit_orders = False
broker_open_orders_zero = PASS
broker_snapshot_errors_empty = PASS
```

Hard stop conditions:

```txt
dry-run evaluation fails
risk controls fail
pre-trade checklist fails
broker open orders are unexpected
execution plan is stale
market data is unavailable
candidate changed unexpectedly
orders_required > 1 and no single-order filter was used
manual approval is missing
```

This runbook preservation does not authorize paper orders, live orders, controlled submit, or PPO v2 retraining.

---

## 13. Candidate Stability Policy

Candidate stability details should remain in `docs/workflows/signal_persistence_candidate_stability_policy.md`, but the core source-of-truth policy is:

```txt
A candidate must be revalidated on a fresh future run before any submit decision.
Do not submit from a prior checkpoint's execution plan.
Do not assume a prior candidate remains valid.
```

Candidate definition:

```txt
should_order = True
side in {buy, sell}
orders_required >= 1
```

Changed candidate conditions:

```txt
symbol changes
side changes
candidate disappears
orders_required changes from 1 to multiple
candidate becomes below_min_notional
risk fails
checklist fails
plan becomes stale
```

Candidate stability levels:

```txt
Level 0 = one-time candidate; review only
Level 1 = revalidated candidate; eligible for controlled review
Level 2 = submit-eligible candidate; requires full safety stack and manual approval
```

Default action when uncertain:

```txt
NO-SUBMIT
```

---

## 14. Paper-Trading and Submit Constraints

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

Future controlled-submit hardening candidates to preserve for backlog or v3.06 audit review:

```txt
make submit mode fail closed if broker account/positions/open-order reads fail
add runner-level max_orders_to_submit=1 default
add post-submit order-status reconciliation by order id
keep PROJECT_CONTEXT.md aligned with latest paper-trading policy
```

These are hardening candidates only. They do not authorize submit, broker execution, or model promotion.

---

## 15. Artifact and Generated Data Policy

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

## 16. Testing and CI Standards

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

## 17. Future Phase: Statistical Backtest Evidence / Model Comparison Package

After PPO-only, PPO + Random Forest Gate, and PPO + XGBoost Gate have completed their respective validation packages, compare candidate models using a standardized statistical evidence layer.

This layer should include:

```txt
raw Sharpe
annualized Sharpe
Sortino
Probabilistic Sharpe Ratio
Deflated Sharpe Ratio
max drawdown
Calmar ratio
turnover
average holding period
frequency of bets
long ratio
correlation to underlying
implementation shortfall / slippage sensitivity
attribution by ticker and regime
paper-trading stability metrics
```

For RF/XGBoost gate models, also include:

```txt
accuracy
precision
recall
F1
confusion matrix
false positive / false negative review
probability calibration where applicable
```

These metrics are for post-validation comparison and promotion review only. They must not be used for repeated tuning against the holdout set, as a shortcut around PPO-only evidence, or as standalone proof of trading edge.

This phase is not active implementation scope. It does not authorize PPO v2 training, model promotion, paper orders, live orders, controlled submit, PPO + RF deployment, or PPO + XGBoost deployment.

---

## 18. Publication and Portfolio Framing

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
v3.06 audit failure recorded before v3.07
v3.06 remediation planning active
preserved operational runbook and candidate-stability policy
future statistical/model-comparison package defined as post-validation only
```

Remaining before model-performance claims:

```txt
v3.06 blocking findings remediated and reviewed
one-time no-submit PPO v2 training execution, only if later authorized
post-run audit of generated evidence
validation reporting from real evidence
PPO-only model evidence decision
hybrid comparison only after PPO-only evidence passes
standardized statistical evidence package after validated model packages exist
```

---

## 19. Maintenance Requirements

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

## 20. Current Bottom Line

```txt
v3.06 audit completed with decision FAIL.
v3.06 audit remediation planning is active.
v3.07 is blocked.
PPO v2 training is not authorized.
No paper/live/controlled submit is authorized.
PPO + RF and PPO + XGBoost remain blocked.
The project is not ready for one-time no-submit PPO v2 training execution.
Blocking audit findings B1-B5 must be remediated and reviewed before v3.07 can be reconsidered.
Operational runbook, candidate-stability, module-inventory, and hardening-candidate details are preserved in summary form.
The future statistical/model-comparison package is defined as post-validation scope only.
```
