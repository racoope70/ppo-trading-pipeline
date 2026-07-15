# PROJECT_CONTEXT.md

Authoritative source of truth for `racoope70/ppo-trading-pipeline`.

Detailed v3.07 history is archived at `docs/archive/v3_07_validation_readiness_chain_summary.md`. The missing v3.07 dataset remains historical context only.

---

## 1. Current source-of-truth summary

```text
current_workstream = PPO_V2_SUPERSEDING_DATASET_RECONSTRUCTION
active_phase = v3.08 Data-Fetch Authorization
latest_completed_checkpoint = v3.08 Mocked Unit and Contract Testing
latest_completed_commit = 5cc08e0bcaa570b2fe01e0e984e3557f9e324856
latest_completed_decision = PASS_MOCKED_UNIT_CONTRACT_TESTING_FOR_DATA_FETCH_AUTHORIZATION_CONSIDERATION
latest_completed_ci = NOT_INDEPENDENTLY_VERIFIED_IN_THIS_CHECKPOINT
current_active_checkpoint = v3.08 Data-Fetch Authorization
next_checkpoint = v3.08 Data-Fetch Authorization
```

Data-fetch authorization consideration is current. Data fetching and all downstream execution remain unauthorized until separately approved.

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

## 4. Source/test implementation and mocked testing status

```text
source_test_implementation_checkpoint = v3.08 Dataset Reconstruction Source/Test Implementation
source_test_implementation_commit = 4cbb979a88176c252abcf5e1cd2f310c605573e9
source_test_implementation_performed = YES
mocked_unit_contract_testing_record = docs/runs/v3.08_mocked_unit_contract_testing.md
mocked_unit_contract_testing_commit = 5cc08e0bcaa570b2fe01e0e984e3557f9e324856
mocked_unit_contract_testing_result = PASS
mocked_unit_contract_testing_decision = PASS_MOCKED_UNIT_CONTRACT_TESTING_FOR_DATA_FETCH_AUTHORIZATION_CONSIDERATION
py_compile_result = PASS
targeted_pytest_result = PASS
targeted_mocked_unit_contract_tests_passed = 14
targeted_mocked_unit_contract_tests_failed = 0
full_pytest_suite_run = NO
```

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

## 6. Current authorization state

```text
data_fetch_authorization_checkpoint = CURRENT
data_fetch_authorization_record = NOT_CREATED
data_fetch_authorization_decision = NOT_YET_PERFORMED
data_fetch_authorization_consideration = PERMITTED_BY_MOCKED_UNIT_CONTRACT_TESTING_PASS
data_fetching_authorized = NO
Alpaca_API_calls_authorized = NO
live_Alpaca_client_authorized = NO
market_data_access_authorized = NO
dataset_generation_authorized = NO
dataset_validation_authorized = NO
validation_only_preflight_authorized = NO
training_authorized = NO
orders_authorized = NO
deployment_authorized = NO
tagging_authorized = NO
```

## 7. Completed governance chain

1. Dependency/requirements authorization.
2. Requirements dependency-change authorization.
3. Requirements dependency-file update adding `exchange-calendars==4.13.2`.
4. Dependency installation authorization.
5. Dependency installation execution.
6. XNYS runtime-verification authorization.
7. XNYS runtime-verification execution.
8. Failed independent XNYS runtime-verification review.
9. XNYS runtime-verification review remediation.
10. Repeat independent XNYS runtime-verification review passed.
11. Dataset reconstruction implementation authorization passed for source/test implementation only.
12. Source/test implementation completed.
13. Mocked unit and contract testing passed for data-fetch authorization consideration only.

## 8. Forward roadmap

1. v3.08 Data-Fetch Authorization.
2. v3.08 Data-Fetch Execution, only if data-fetch authorization passes.
3. Dataset-generation authorization.
4. Dataset-generation execution.
5. Dataset evidence review.
6. Dataset-validation authorization.
7. Dataset-validation execution.
8. Validation-only preflight authorization.
9. Validation-only preflight execution.
10. Training authorization.
11. Training execution.
12. Artifact/model review.
13. Paper-trading authorization.

Every later milestone remains separately governed.

## 9. Alignment checkpoint action confirmations

```text
source_code_changed = NO
tests_changed = NO
requirements_changed = NO
dependencies_installed = NO
py_compile_rerun = NO
pytest_rerun = NO
runtime_verification_rerun = NO
exchange_calendars_imported_for_runtime_verification = NO
XNYS_get_calendar_called = NO
XNYS_schedule_constructed_from_live_calendar = NO
market_data_accessed = NO
Alpaca_API_called = NO
live_Alpaca_client_created = NO
datasets_created = NO
data_directory_written = NO
artifacts_created = NO
artifacts_directory_written = NO
parquet_output_written = NO
manifest_created = NO
checksum_created = NO
dataset_validation_run = NO
validation_only_preflight_run = NO
training_run = NO
model_artifact_created = NO
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
git merge-base --is-ancestor 5cc08e0bcaa570b2fe01e0e984e3557f9e324856 HEAD
echo $?
```

## 11. Current bottom line

```text
current_active_checkpoint = v3.08 Data-Fetch Authorization
next_checkpoint = v3.08 Data-Fetch Authorization
data_fetch_authorization_checkpoint = CURRENT
data_fetching_authorized = NO
Alpaca_API_calls_authorized = NO
dataset_generation_authorized = NO
```

The current checkpoint may decide whether a later data-fetch execution can proceed. It does not authorize fetching itself.
