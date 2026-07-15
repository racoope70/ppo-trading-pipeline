# Milestone Review Reference Map

Navigation map for the active v3.08 superseding governed Alpaca-aligned reconstruction workstream. `PROJECT_CONTEXT.md` remains authoritative.

---

## 1. Current controlling state

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

Data-fetch authorization consideration is current. Data fetching itself remains unauthorized.

## 2. Governing classification and dataset identity

```text
reconstruction_classification = SUPERSEDING_GOVERNED_ALPACA_ALIGNED_RECONSTRUCTION
original_dataset_recovered = FALSE
byte_identical_original_dataset_recovery = NOT_CLAIMED
byte_identical_recovery_claim = PROHIBITED
historical_equivalence_claim = NOT_PROVEN
new_dataset_identity_required = TRUE
output_path = data/processed/ppo_v2/v3_08_superseding_alpaca_aligned_no_submit_training_input.parquet
old_missing_path = data/processed/ppo_v2/v3_07_no_submit_training_input.parquet
old_path_usage = HISTORICAL_MISSING_ARTIFACT_REFERENCE_ONLY
old_path_as_output_target = PROHIBITED
new_run_id_required = TRUE
new_manifest_required = TRUE
new_checksum_required = TRUE
```

## 3. Source/test implementation and mocked testing status

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

## 4. Dependency and runtime prerequisites

```text
requirements_pin = exchange-calendars==4.13.2
exchange_calendars_installed = YES
exchange_calendars_installed_version = 4.13.2
dependency_installation_execution_result = PASS_EXACT_EXCHANGE_CALENDARS_INSTALLATION_COMPLETED
XNYS_runtime_verification_execution_result = PASS_XNYS_RUNTIME_VERIFICATION_COMPLETED
independent_xnys_runtime_verification_review_repeat_after_remediation = PASSED
runtime_prerequisite_for_source_test_implementation = SATISFIED
```

## 5. Current authorization state

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

## 6. Files to review first

1. `PROJECT_CONTEXT.md`
2. `docs/runs/v3.08_mocked_unit_contract_testing.md`
3. `docs/runs/v3.08_dataset_reconstruction_implementation_authorization.md`
4. `src/ppo_v2_dataset_reconstruction.py`
5. `src/ppo_v2_data_contract.py`
6. `src/ppo_v2_market_calendar.py`
7. `src/ppo_v2_parquet_writer.py`

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

## 8. Forward milestone roadmap

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

The current checkpoint may authorize a later data-fetch execution only. Data fetching, dataset generation, validation, training, orders, deployment, and tagging are not authorized.
