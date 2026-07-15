# PROJECT_CONTEXT.md

Authoritative source of truth for `racoope70/ppo-trading-pipeline`.

Detailed v3.07 history is archived at `docs/archive/v3_07_validation_readiness_chain_summary.md`. The missing v3.07 dataset remains historical context only.

---

## 1. Current source-of-truth summary

```text
current_workstream = PPO_V2_SUPERSEDING_DATASET_RECONSTRUCTION
active_phase = v3.08 XNYS Runtime Verification Review Remediation
latest_completed_checkpoint = v3.08 Independent XNYS Runtime Verification Review
latest_completed_commit = 3583380824a46f6f603cbe6812c715e044fc3233
latest_completed_decision = FAIL_INDEPENDENT_XNYS_RUNTIME_VERIFICATION_REVIEW_REQUIRES_REMEDIATION
latest_completed_ci = NOT_INDEPENDENTLY_VERIFIED_IN_THIS_CHECKPOINT
current_active_checkpoint = v3.08 XNYS Runtime Verification Review Remediation
next_checkpoint = v3.08 XNYS Runtime Verification Review Remediation
```

Dependency installation and XNYS runtime-verification execution are complete. Runtime execution reported PASS, but independent review failed because the durable evidence package and active governance records required remediation. Implementation remains unauthorized.

## 2. Governing reconstruction classification

```text
reconstruction_classification = SUPERSEDING_GOVERNED_ALPACA_ALIGNED_RECONSTRUCTION
original_dataset_recovered = FALSE
byte_identical_original_dataset_recovery = NOT_CLAIMED
byte_identical_recovery_claim = PROHIBITED
historical_equivalence_claim = NOT_PROVEN
new_dataset_identity_required = TRUE
```

## 3. Dataset identity

```text
output_path = data/processed/ppo_v2/v3_08_superseding_alpaca_aligned_no_submit_training_input.parquet
old_missing_path = data/processed/ppo_v2/v3_07_no_submit_training_input.parquet
old_path_usage = HISTORICAL_MISSING_ARTIFACT_REFERENCE_ONLY
old_path_as_output_target = PROHIBITED
new_run_id_required = TRUE
new_manifest_required = TRUE
new_checksum_required = TRUE
```

No dataset-generation authority has been granted.

## 4. Canonical contract and implementation state

```text
canonical_final_contract_record = docs/runs/v3.08_dataset_reconstruction_contract_resolution.md
requested_nonexistent_final_contract_path = docs/runs/v3.08_dataset_reconstruction_final_contract_resolution.md
requested_nonexistent_path_status = NOT_CREATED
duplicate_contract_record_created = NO
path_mismatch_resolution = CANONICALIZE_REFERENCES_TO_EXISTING_CONTRACT_RESOLUTION_RECORD
final_contract_resolution_review_status = PASSED_INDEPENDENT_REVIEW_AFTER_REMEDIATION
implementation_planning_authorization_decision = PASS_IMPLEMENTATION_PLANNING_AUTHORIZATION_ONLY
implementation_plan_decision = PASS_IMPLEMENTATION_PLAN_FOR_FUTURE_AUTHORIZATION_REVIEW_ONLY
implementation_plan_file = docs/runs/v3.08_dataset_reconstruction_implementation_plan.md
implementation_plan_review_status = PASSED_FOR_DEPENDENCY_REQUIREMENTS_AUTHORIZATION_CHECKPOINT
implementation_readiness = NOT_ESTABLISHED
implementation_authorization = NOT_AUTHORIZED
implementation_authorized = NO
```

The existing contract-resolution record is canonical. No duplicate final-contract record is created.

## 5. Dependency, calendar, and runtime status

```text
requirements_pin = exchange-calendars==4.13.2
exchange_calendars_installed = YES
exchange_calendars_installed_version = 4.13.2
dependency_installation_execution_result = PASS_EXACT_EXCHANGE_CALENDARS_INSTALLATION_COMPLETED
XNYS_local_runtime_verification = COMPLETED_PENDING_REVIEW_REMEDIATION
XNYS_runtime_verification_execution_result = PASS_XNYS_RUNTIME_VERIFICATION_COMPLETED
calendar_runtime_verified = REPORTED_PASS_PENDING_REPEAT_INDEPENDENT_REVIEW
independent_xnys_runtime_verification_review = FAILED_REQUIRES_REMEDIATION
independent_xnys_runtime_verification_review_record = docs/audits/v3.08_independent_xnys_runtime_verification_review.md
runtime_verification_remediation_record = docs/runs/v3.08_xnys_runtime_verification_review_remediation.md
```

The runtime execution reported PASS, but that result is not independently accepted until remediation is completed and a repeat independent review passes.

## 6. Completed dependency and runtime chain

1. `docs/audits/v3.08_independent_dataset_reconstruction_implementation_plan_review_repeat_after_remediation.md`
2. `docs/runs/v3.08_dataset_reconstruction_dependency_requirements_authorization.md`
3. `docs/runs/v3.08_requirements_dependency_change_authorization.md`
4. Requirements dependency-file update adding `exchange-calendars==4.13.2`.
5. `docs/runs/v3.08_dependency_installation_authorization_exchange_calendars.md`
6. `docs/runs/v3.08_dependency_installation_execution_exchange_calendars.md`
7. `docs/runs/v3.08_xnys_runtime_verification_authorization.md`
8. `docs/runs/v3.08_xnys_runtime_verification_execution.md`
9. `docs/audits/v3.08_independent_xnys_runtime_verification_review.md`
10. Active: `docs/runs/v3.08_xnys_runtime_verification_review_remediation.md`.

## 7. Forward roadmap

1. v3.08 XNYS Runtime Verification Review Remediation.
2. v3.08 Independent XNYS Runtime Verification Review Repeat After Remediation.
3. Implementation authorization consideration only if the repeat review passes.
4. Source/test implementation only if separately authorized.
5. Mocked unit and contract testing.
6. Data-fetch authorization.
7. Dataset-generation authorization and execution.
8. Dataset evidence review.
9. Dataset-validation authorization and execution.
10. Validation-only preflight authorization and execution.
11. Training authorization and execution.
12. Artifact/model review.
13. Paper-trading authorization.

Every step requires its own explicit authorization and any specified independent review.

## 8. Hard non-authorization boundary

```text
code_implementation = NOT_AUTHORIZED
source_code_changes = NOT_AUTHORIZED
test_changes = NOT_AUTHORIZED
requirements_change = NOT_PERFORMED
dependency_file_edit = NOT_PERFORMED
dependency_installation = NOT_PERFORMED
data_fetching = NOT_AUTHORIZED
data_downloading = NOT_AUTHORIZED
dataset_generation = NOT_AUTHORIZED
sealed_dataset_creation = NOT_AUTHORIZED
dataset_validation = NOT_AUTHORIZED
sealed_dataset_validation = NOT_PROVEN
validation_only_preflight_rerun = NOT_AUTHORIZED
training = NOT_AUTHORIZED
model_fitting = NOT_AUTHORIZED
model_artifact_creation = NOT_AUTHORIZED
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
deployment = NOT_AUTHORIZED
tagging = NOT_AUTHORIZED
```

## 9. Freshness guardrail

```bash
git fetch origin
git status --short
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 3583380824a46f6f603cbe6812c715e044fc3233 HEAD
echo $?
```

Proceed only when the working tree is clean, `HEAD` equals `origin/main`, and the merge-base exit code is `0`.

## 10. Current bottom line

```text
current_active_checkpoint = v3.08 XNYS Runtime Verification Review Remediation
next_checkpoint = v3.08 XNYS Runtime Verification Review Remediation
runtime_evidence_status = REPORTED_PASS_UNDER_REMEDIATION
implementation_readiness = NOT_ESTABLISHED
implementation_authorization = NOT_AUTHORIZED
implementation_authorized = NO
```

The active action is evidence and governance remediation followed by repeat independent review, not implementation.
