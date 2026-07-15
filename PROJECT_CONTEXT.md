# PROJECT_CONTEXT.md

Authoritative source of truth for `racoope70/ppo-trading-pipeline`.

Detailed v3.07 history is archived at `docs/archive/v3_07_validation_readiness_chain_summary.md`. The missing v3.07 dataset remains historical context only.

---

## 1. Current source-of-truth summary

```text
current_workstream = PPO_V2_SUPERSEDING_DATASET_RECONSTRUCTION
active_phase = v3.08 Dataset Reconstruction Source/Test Implementation
latest_completed_checkpoint = v3.08 Dataset Reconstruction Implementation Authorization
latest_completed_commit = abcef2b0f6a6f64a9701fbe53f545dc41cdc55c6
latest_completed_decision = PASS_DATASET_RECONSTRUCTION_IMPLEMENTATION_AUTHORIZATION_FOR_SOURCE_TEST_IMPLEMENTATION_CHECKPOINT_ONLY
latest_completed_ci = NOT_INDEPENDENTLY_VERIFIED_IN_THIS_CHECKPOINT
current_active_checkpoint = v3.08 Dataset Reconstruction Source/Test Implementation
next_checkpoint = v3.08 Dataset Reconstruction Source/Test Implementation
```

The next allowed work is source and test implementation only. No data, validation, training, trading, deployment, or tagging authority is implied.

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

Dataset generation remains unauthorized.

## 4. Canonical contract and implementation authorization

```text
canonical_final_contract_record = docs/runs/v3.08_dataset_reconstruction_contract_resolution.md
requested_nonexistent_final_contract_path = docs/runs/v3.08_dataset_reconstruction_final_contract_resolution.md
requested_nonexistent_path_status = NOT_CREATED
duplicate_contract_record_created = NO
path_mismatch_resolution = CANONICALIZE_REFERENCES_TO_EXISTING_CONTRACT_RESOLUTION_RECORD
implementation_plan_file = docs/runs/v3.08_dataset_reconstruction_implementation_plan.md
implementation_authorization_record = docs/runs/v3.08_dataset_reconstruction_implementation_authorization.md
implementation_authorization_decision = PASS_DATASET_RECONSTRUCTION_IMPLEMENTATION_AUTHORIZATION_FOR_SOURCE_TEST_IMPLEMENTATION_CHECKPOINT_ONLY
future_source_test_implementation_authorized_for_next_checkpoint = YES
implementation_scope = SOURCE_AND_TEST_IMPLEMENTATION_ONLY
source_test_implementation_performed = NO
```

Authorization is limited to the next source/test implementation checkpoint. Later execution activities remain separately governed.

## 5. Dependency and runtime prerequisites

```text
requirements_pin = exchange-calendars==4.13.2
exchange_calendars_installed = YES
exchange_calendars_installed_version = 4.13.2
dependency_installation_execution_result = PASS_EXACT_EXCHANGE_CALENDARS_INSTALLATION_COMPLETED
XNYS_runtime_verification_execution_result = PASS_XNYS_RUNTIME_VERIFICATION_COMPLETED
independent_xnys_runtime_verification_review_repeat_after_remediation = PASSED
runtime_prerequisite_for_source_test_implementation = SATISFIED
```

## 6. Completed governance chain

The completed chain includes dependency/requirements authorization, the exact requirements pin, dependency installation authorization and execution, XNYS runtime-verification authorization and execution, evidence remediation, repeat independent runtime review, and dataset reconstruction implementation authorization.

The controlling authorization record is `docs/runs/v3.08_dataset_reconstruction_implementation_authorization.md`.

## 7. Forward roadmap

1. v3.08 Dataset Reconstruction Source/Test Implementation.
2. Mocked unit and contract testing.
3. Data-fetch authorization.
4. Dataset-generation authorization and execution.
5. Dataset evidence review.
6. Dataset-validation authorization and execution.
7. Validation-only preflight authorization and execution.
8. Training authorization and execution.
9. Artifact/model review.
10. Paper-trading authorization.

Every later step requires its own explicit authorization and any specified independent review.

## 8. Current authorization boundary

```text
source_test_implementation = AUTHORIZED_FOR_CURRENT_CHECKPOINT_ONLY
data_fetching_in_future_checkpoint = NOT_AUTHORIZED
Alpaca_API_calls_in_future_checkpoint = NOT_AUTHORIZED
dataset_generation_in_future_checkpoint = NOT_AUTHORIZED
dataset_validation_in_future_checkpoint = NOT_AUTHORIZED
training_in_future_checkpoint = NOT_AUTHORIZED
orders_in_future_checkpoint = NOT_AUTHORIZED
deployment_in_future_checkpoint = NOT_AUTHORIZED
tagging_in_future_checkpoint = NOT_AUTHORIZED
```

## 9. Alignment checkpoint action confirmations

```text
source_code_changed = NO
tests_changed = NO
requirements_changed = NO
dependencies_installed = NO
runtime_verification_rerun = NO
exchange_calendars_imported = NO
XNYS_get_calendar_called = NO
XNYS_schedule_constructed = NO
market_data_accessed = NO
Alpaca_API_called = NO
datasets_created = NO
artifacts_created = NO
validation_run = NO
training_run = NO
orders_submitted = NO
deployment_performed = NO
tag_created = NO
```

## 10. Freshness guardrail

```bash
git fetch origin
git status --short
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor abcef2b0f6a6f64a9701fbe53f545dc41cdc55c6 HEAD
echo $?
```

Proceed only when the working tree is clean, `HEAD` equals `origin/main`, and the merge-base exit code is `0`.

## 11. Current bottom line

```text
current_active_checkpoint = v3.08 Dataset Reconstruction Source/Test Implementation
next_checkpoint = v3.08 Dataset Reconstruction Source/Test Implementation
implementation_scope = SOURCE_AND_TEST_IMPLEMENTATION_ONLY
source_test_implementation_performed = NO
runtime_prerequisite_for_source_test_implementation = SATISFIED
```

The active next action is source/test implementation within the authorized contract. No later activity is authorized.
