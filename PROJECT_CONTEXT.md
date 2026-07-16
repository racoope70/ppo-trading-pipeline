# PROJECT_CONTEXT.md

Authoritative source of truth for `racoope70/ppo-trading-pipeline`.

Detailed v3.07 history is archived at `docs/archive/v3_07_validation_readiness_chain_summary.md`. The missing v3.07 dataset remains historical context only.

---

## 1. Current source-of-truth summary

```text
current_workstream = PPO_V2_SUPERSEDING_DATASET_RECONSTRUCTION
active_phase = v3.08 Governed Targeted Missing-Slot Refetch and Raw Data-Completeness Remediation Execution
latest_completed_checkpoint = v3.08 Missing-Slot Remediation and Data-Completeness Authorization Consideration
latest_completed_commit = d3953eea67fb44f1c9c6ac6e983fbcec301262cb
latest_completed_decision = PASS_MISSING_SLOT_REMEDIATION_DATA_COMPLETENESS_AUTHORIZATION_CONSIDERATION_FOR_GOVERNED_TARGETED_REFETCH_RAW_REMEDIATION_EXECUTION_ONLY
latest_completed_record = docs/runs/v3.08_missing_slot_remediation_data_completeness_authorization_consideration.md
latest_completed_ci = NOT_INDEPENDENTLY_VERIFIED_IN_THIS_CHECKPOINT
current_active_checkpoint = v3.08 Governed Targeted Missing-Slot Refetch and Raw Data-Completeness Remediation Execution
next_checkpoint = v3.08 Governed Targeted Missing-Slot Refetch and Raw Data-Completeness Remediation Execution
```

Governed targeted missing-slot refetch and raw data-completeness remediation execution is current under the exact authorized scope. Dataset generation and all later execution remain unauthorized.

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
data_fetch_authorization_checkpoint = COMPLETED
data_fetch_authorization_record = docs/runs/v3.08_data_fetch_authorization.md
data_fetch_authorization_commit = d2b44e952a2350e312f6b7b4298beeea912a7e8f
data_fetch_authorization_result = PASS
data_fetch_authorization_decision = PASS_DATA_FETCH_AUTHORIZATION_FOR_DATA_FETCH_EXECUTION_CHECKPOINT_ONLY
data_fetch_authorization_consideration = PERMITTED_BY_MOCKED_UNIT_CONTRACT_TESTING_PASS
data_fetch_execution_checkpoint = COMPLETED
data_fetch_execution_record = docs/runs/v3.08_data_fetch_execution.md
data_fetch_execution_result = PASS_DATA_FETCH_EXECUTION_RAW_HISTORICAL_BARS_FETCH_COMPLETED
data_fetch_execution_commit = 3a49775514ff5c21a51ef192e970e269ed8b5ceb
dataset_generation_authorization_checkpoint = COMPLETED
dataset_generation_authorization_record = docs/runs/v3.08_dataset_generation_authorization.md
dataset_generation_authorization_commit = cfdb99543a886e1e4604443a520b006cf9587c15
dataset_generation_authorization_result = PASS
dataset_generation_authorization_decision = PASS_DATASET_GENERATION_AUTHORIZATION_FOR_DATASET_GENERATION_EXECUTION_CHECKPOINT_ONLY
dataset_generation_authorized = NO
dataset_generation_reexecution_authorization_checkpoint = COMPLETED
dataset_generation_reexecution_authorization_record = docs/runs/v3.08_dataset_generation_reexecution_authorization.md
dataset_generation_reexecution_authorization_commit = bb1f6f18107085154674a45f4f0b464c157559ec
dataset_generation_reexecution_authorization_result = PASS
dataset_generation_reexecution_authorization_decision = PASS_DATASET_GENERATION_REEXECUTION_AUTHORIZATION_FOR_DATASET_GENERATION_REEXECUTION_ONLY
dataset_generation_reexecution_checkpoint = COMPLETED_BLOCKED
dataset_generation_reexecution_record = docs/runs/v3.08_dataset_generation_reexecution.md
dataset_generation_reexecution_commit = a9f8bfe2425a154625f6fd5293330bc97ad7337f
dataset_generation_reexecution_result = BLOCK_DATASET_GENERATION_REEXECUTION_RAW_INPUT_MISSING_EXPECTED_SLOTS
dataset_generation_reexecution_complete = NO
dataset_generation_reexecution_authorized = NO
dataset_generation_reexecution_blocked_evidence_review_checkpoint = COMPLETED
dataset_generation_reexecution_blocked_evidence_review_record = docs/runs/v3.08_dataset_generation_reexecution_blocked_evidence_review.md
dataset_generation_reexecution_blocked_evidence_review_commit = bd5083e65d5d198f9e4eb159373f9c49fb73b2fe
dataset_generation_reexecution_blocked_evidence_review_result = PASS
dataset_generation_reexecution_blocked_evidence_review_decision = PASS_BLOCKED_DATASET_GENERATION_REEXECUTION_EVIDENCE_REVIEW_FOR_MISSING_SLOT_REMEDIATION_AUTHORIZATION_CONSIDERATION
missing_slot_root_cause_and_remediation_authorization_checkpoint = COMPLETED
missing_slot_root_cause_and_remediation_authorization_record = docs/runs/v3.08_missing_slot_root_cause_remediation_authorization_consideration.md
missing_slot_root_cause_and_remediation_authorization_commit = 81934d64010ac9771c0022ffacd18a5ab79035fa
missing_slot_root_cause_and_remediation_authorization_result = PASS
missing_slot_root_cause_and_remediation_authorization_decision = PASS_MISSING_SLOT_ROOT_CAUSE_REMEDIATION_AUTHORIZATION_CONSIDERATION_FOR_MISSING_SLOT_ROOT_CAUSE_ANALYSIS_ONLY
missing_slot_root_cause_analysis_checkpoint = COMPLETED
missing_slot_root_cause_analysis_record = docs/runs/v3.08_missing_slot_root_cause_analysis.md
missing_slot_root_cause_analysis_commit = db3b72a1f957499ea265dd51a8c5f7d8731c5e42
missing_slot_root_cause_analysis_result = PASS
missing_slot_root_cause_analysis_decision = PASS_MISSING_SLOT_ROOT_CAUSE_ANALYSIS_FOR_REMEDIATION_AUTHORIZATION_CONSIDERATION
missing_slot_root_cause_category = PROVIDER_OR_FEED_LEVEL_MISSING_BARS
missing_slot_root_cause_confidence = HIGH
missing_slot_root_cause_analysis_authorized = NO
missing_slot_remediation_authorization_checkpoint = COMPLETED
missing_slot_remediation_authorization_record = docs/runs/v3.08_missing_slot_remediation_data_completeness_authorization_consideration.md
missing_slot_remediation_authorization_commit = d3953eea67fb44f1c9c6ac6e983fbcec301262cb
missing_slot_remediation_authorization_result = PASS
missing_slot_remediation_authorization_decision = PASS_MISSING_SLOT_REMEDIATION_DATA_COMPLETENESS_AUTHORIZATION_CONSIDERATION_FOR_GOVERNED_TARGETED_REFETCH_RAW_REMEDIATION_EXECUTION_ONLY
governed_targeted_missing_slot_refetch_raw_remediation_checkpoint = CURRENT
governed_targeted_missing_slot_refetch_raw_remediation_record = NOT_CREATED
governed_targeted_missing_slot_refetch_raw_remediation_result = NOT_YET_PERFORMED
targeted_refetch_authorized = YES
raw_data_completeness_remediation_authorized = YES
missing_slot_remediation_authorized = YES
dataset_generation_remediation_authorized = NO
dependency_installation_authorized = NO
requirements_change_authorized = NO
data_fetch_authorized = YES
alpaca_api_calls_authorized = YES
dataset_generation_authorized = NO
contract_relaxation_authorized = NO
calendar_rule_change_authorized = NO
synthetic_fill_authorized = NO
authorized_current_execution_scope = GOVERNED_TARGETED_MISSING_SLOT_REFETCH_RAW_REMEDIATION_EXECUTION_ONLY
dataset_generation_execution_checkpoint = COMPLETED_BLOCKED
dataset_generation_execution_record = docs/runs/v3.08_dataset_generation_execution.md
dataset_generation_execution_result = BLOCK_DATASET_GENERATION_EXECUTION_REQUIRED_RUNTIME_DEPENDENCIES_NOT_INSTALLED
dataset_generation_execution_remediation_checkpoint = COMPLETED
dataset_generation_execution_remediation_record = docs/runs/v3.08_dataset_generation_execution_remediation.md
dataset_generation_execution_remediation_result = PASS_DATASET_GENERATION_EXECUTION_REMEDIATION_WORKSPACE_VENV_SELECTED_AND_IMPORTS_VERIFIED
selected_runtime_interpreter = ../.venv/bin/python
selected_runtime_imports_pass = YES
dependencies_installed_during_remediation = NO
requirements_changed_during_remediation = NO
raw_input_path = data/raw/ppo_v2/v3_08_alpaca_iex_hourly_raw_bars.parquet
raw_input_sha256 = 1694d9e706666c0718e940f40e28a8170b246ce7e2a07a570a5b122fd3c04e30
raw_input_sha256_match = YES
expected_slots_per_symbol = 3729
observed_expected_slots_per_symbol = 3718
missing_expected_slots_per_symbol = 11
total_missing_expected_slots = 66
missing_expected_slot_tolerance = 0
gap_contract_result = FAIL
final_dataset_created = NO
manifest_created = NO
checksum_created = NO
partial_outputs_remaining = NO
dataset_validation_authorized = NO
validation_only_preflight_authorized = NO
training_authorized = NO
orders_authorized = NO
deployment_authorized = NO
tagging_authorized = NO
```

The completed Data-Fetch Execution was limited to:

- the exact governed Alpaca historical bars request contract;
- the six-symbol universe only: AAPL, AMD, MRK, PFE, UNH, XOM;
- `TimeFrame.Hour` only;
- `DataFeed.IEX` only;
- `Adjustment.RAW` only;
- `Sort.ASC` only;
- `raw_request_start = 2022-12-01T00:00:00Z`;
- `raw_request_end = 2025-06-30T20:00:00Z`;
- timezone-aware UTC datetimes;
- no-submit / historical-data-only behavior;
- credentials loaded only for read-only historical data access;
- separately declared data-fetch execution evidence and raw-fetch output; and
- preservation of the old v3.07 path prohibition.

The completed Data-Fetch Execution remained prohibited from:

- generating the final dataset;
- writing the governed final Parquet dataset;
- writing the final manifest;
- writing the final checksum;
- treating fetched data as validated;
- running dataset validation;
- running validation-only preflight;
- running training;
- creating model artifacts;
- submitting paper or live orders;
- deploying; or
- tagging.

The blocked Dataset-Generation Execution checkpoint was authorized only to:

- read the local ignored raw parquet fetched under v3.08 Data-Fetch Execution;
- transform raw Alpaca bars into the governed v3.08 final dataset identity;
- apply the contract-defined canonical window, warmup, session policy, feature engineering, dtype rules, gap rules, and final column order;
- write only the governed final dataset path if all contract checks pass;
- write only the required v3.08 dataset-generation execution evidence; and
- write the required manifest/checksum only if explicitly included in the dataset-generation execution checkpoint.

The blocked Dataset-Generation Execution checkpoint did not:

- treat the dataset as validated;
- run dataset validation;
- run validation-only preflight;
- run training;
- create model artifacts;
- submit paper/live orders;
- deploy; or
- tag.

The current Governed Targeted Missing-Slot Refetch and Raw Data-Completeness Remediation Execution checkpoint may only:

- use Alpaca historical bars access for the governed six-symbol universe only: AAPL, AMD, MRK, PFE, UNH, XOM;
- use IEX feed only;
- use hourly bars only;
- use raw adjustment only;
- target only the affected sessions and missing-slot windows identified in the root-cause record: 2024-12-23 and 2025-03-10;
- attempt to recover only the exact missing expected symbol-slot observations listed in the root-cause record;
- compare recovered bars against the existing expected grid;
- preserve the original raw parquet unchanged;
- create a separately named raw remediation candidate file only if actual provider-returned bars support it;
- create a remediation evidence record documenting recovered and unrecovered slots; and
- create a checksum for any new raw remediation candidate file, if one is created.

The current Governed Targeted Missing-Slot Refetch and Raw Data-Completeness Remediation Execution checkpoint must not:

- modify the original raw parquet;
- synthesize, fill, interpolate, forward-fill, or backfill bars;
- alter calendar rules;
- loosen the zero-missing-slot contract;
- change source code, tests, requirements, or workflows;
- create a processed final dataset;
- create a processed dataset manifest;
- run dataset generation;
- run dataset validation;
- run validation-only preflight;
- run training;
- create model artifacts;
- submit orders;
- deploy; or
- tag.

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
14. Data-fetch authorization passed for data-fetch execution checkpoint only.
15. v3.08 Data-Fetch Execution Remediation — Alpaca Sort Import Compatibility; commit `9011751bb3d046954b200cd77838e8c5bfa1afda`; decision `PASS_ALPACA_SORT_IMPORT_COMPATIBILITY_REMEDIATION`; record `docs/runs/v3.08_data_fetch_execution_remediation_alpaca_sort_import.md`.
16. v3.08 Data-Fetch Execution; commit `3a49775514ff5c21a51ef192e970e269ed8b5ceb`; decision `PASS_DATA_FETCH_EXECUTION_RAW_HISTORICAL_BARS_FETCH_COMPLETED`; record `docs/runs/v3.08_data_fetch_execution.md`.
17. v3.08 Dataset-Generation Authorization; commit `cfdb99543a886e1e4604443a520b006cf9587c15`; decision `PASS_DATASET_GENERATION_AUTHORIZATION_FOR_DATASET_GENERATION_EXECUTION_CHECKPOINT_ONLY`; record `docs/runs/v3.08_dataset_generation_authorization.md`.
18. v3.08 Dataset-Generation Execution; commit `c6537943f48e2213bc5d67069da7ae81d4b314db`; decision `BLOCK_DATASET_GENERATION_EXECUTION_REQUIRED_RUNTIME_DEPENDENCIES_NOT_INSTALLED`; record `docs/runs/v3.08_dataset_generation_execution.md`.
19. v3.08 Dataset-Generation Execution Remediation Authorization; commit `ddcf80f47467bb7e1fc213b03d16bf99b3cd800a`; decision `PASS_DATASET_GENERATION_EXECUTION_REMEDIATION_AUTHORIZATION_FOR_RUNTIME_DEPENDENCY_REMEDIATION_ONLY`; record `docs/runs/v3.08_dataset_generation_execution_remediation_authorization.md`.
20. v3.08 Dataset-Generation Execution Remediation; commit `dbbc658fc04ad494ad86dbd6cf07137bed686f09`; decision `PASS_DATASET_GENERATION_EXECUTION_REMEDIATION_WORKSPACE_VENV_SELECTED_AND_IMPORTS_VERIFIED`; record `docs/runs/v3.08_dataset_generation_execution_remediation.md`.
21. v3.08 Dataset-Generation Re-Execution Authorization; commit `bb1f6f18107085154674a45f4f0b464c157559ec`; decision `PASS_DATASET_GENERATION_REEXECUTION_AUTHORIZATION_FOR_DATASET_GENERATION_REEXECUTION_ONLY`; record `docs/runs/v3.08_dataset_generation_reexecution_authorization.md`.
22. v3.08 Dataset-Generation Re-Execution; commit `a9f8bfe2425a154625f6fd5293330bc97ad7337f`; decision `BLOCK_DATASET_GENERATION_REEXECUTION_RAW_INPUT_MISSING_EXPECTED_SLOTS`; record `docs/runs/v3.08_dataset_generation_reexecution.md`.
23. v3.08 Dataset-Generation Re-Execution Blocked Evidence Review; commit `bd5083e65d5d198f9e4eb159373f9c49fb73b2fe`; decision `PASS_BLOCKED_DATASET_GENERATION_REEXECUTION_EVIDENCE_REVIEW_FOR_MISSING_SLOT_REMEDIATION_AUTHORIZATION_CONSIDERATION`; record `docs/runs/v3.08_dataset_generation_reexecution_blocked_evidence_review.md`.
24. v3.08 Missing-Slot Root-Cause and Remediation-Authorization Consideration; commit `81934d64010ac9771c0022ffacd18a5ab79035fa`; decision `PASS_MISSING_SLOT_ROOT_CAUSE_REMEDIATION_AUTHORIZATION_CONSIDERATION_FOR_MISSING_SLOT_ROOT_CAUSE_ANALYSIS_ONLY`; record `docs/runs/v3.08_missing_slot_root_cause_remediation_authorization_consideration.md`.
25. v3.08 Missing-Slot Root-Cause Analysis; commit `db3b72a1f957499ea265dd51a8c5f7d8731c5e42`; decision `PASS_MISSING_SLOT_ROOT_CAUSE_ANALYSIS_FOR_REMEDIATION_AUTHORIZATION_CONSIDERATION`; record `docs/runs/v3.08_missing_slot_root_cause_analysis.md`.
26. v3.08 Missing-Slot Remediation and Data-Completeness Authorization Consideration; commit `d3953eea67fb44f1c9c6ac6e983fbcec301262cb`; decision `PASS_MISSING_SLOT_REMEDIATION_DATA_COMPLETENESS_AUTHORIZATION_CONSIDERATION_FOR_GOVERNED_TARGETED_REFETCH_RAW_REMEDIATION_EXECUTION_ONLY`; record `docs/runs/v3.08_missing_slot_remediation_data_completeness_authorization_consideration.md`.

## 8. Forward roadmap

1. v3.08 Governed Targeted Missing-Slot Refetch and Raw Data-Completeness Remediation Execution.
2. Source-of-truth alignment after governed targeted missing-slot refetch/raw remediation execution.
3. Dataset-generation re-execution authorization reconsideration.
4. Dataset-generation re-execution.
5. Source-of-truth alignment after successful dataset generation, if generation passes.
6. Dataset evidence review.
7. Dataset-validation authorization.
8. Dataset-validation execution.
9. Validation-only preflight authorization.
10. Validation-only preflight execution.
11. Training authorization.
12. Training execution.
13. Artifact/model review.
14. Paper-trading authorization.

Every later milestone remains separately governed.

```text
future_validation_training_reference_map = docs/workflows/future_validation_training_reference_map.md
```

For future validation, embargo, VecNormalize, retraining, final holdout, candidate selection, paper trading, and universe-expansion guidance, use the future validation/training reference map. That file is guidance only and does not authorize execution.

## 9. Alignment checkpoint action confirmations

```text
source_code_changed = NO
tests_changed = NO
requirements_changed = NO
dependencies_installed = NO
py_compile_rerun = NO
pytest_rerun = YES
pytest_command = python -m pytest tests/test_ppo_v2_validation_reporting_scaffold.py
pytest_result = PASS_37_PASSED
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
git merge-base --is-ancestor d3953eea67fb44f1c9c6ac6e983fbcec301262cb HEAD
echo $?
```

## 11. Current bottom line

```text
current_active_checkpoint = v3.08 Governed Targeted Missing-Slot Refetch and Raw Data-Completeness Remediation Execution
next_checkpoint = v3.08 Governed Targeted Missing-Slot Refetch and Raw Data-Completeness Remediation Execution
dataset_generation_authorization_checkpoint = COMPLETED
dataset_generation_execution_checkpoint = COMPLETED_BLOCKED
dataset_generation_authorized = NO
dataset_generation_reexecution_authorization_checkpoint = COMPLETED
dataset_generation_reexecution_checkpoint = COMPLETED_BLOCKED
dataset_generation_reexecution_authorized = NO
dataset_generation_reexecution_blocked_evidence_review_checkpoint = COMPLETED
missing_slot_root_cause_and_remediation_authorization_checkpoint = COMPLETED
missing_slot_root_cause_analysis_checkpoint = COMPLETED
missing_slot_root_cause_analysis_authorized = NO
missing_slot_root_cause_category = PROVIDER_OR_FEED_LEVEL_MISSING_BARS
missing_slot_remediation_authorization_checkpoint = COMPLETED
governed_targeted_missing_slot_refetch_raw_remediation_checkpoint = CURRENT
targeted_refetch_authorized = YES
raw_data_completeness_remediation_authorized = YES
missing_slot_remediation_authorized = YES
dataset_generation_remediation_authorized = NO
authorized_current_execution_scope = GOVERNED_TARGETED_MISSING_SLOT_REFETCH_RAW_REMEDIATION_EXECUTION_ONLY
dataset_generation_execution_remediation_checkpoint = COMPLETED
dependency_installation_authorized = NO
requirements_change_authorized = NO
dataset_validation_authorized = NO
```

The current checkpoint authorizes only the governed targeted missing-slot refetch/raw remediation execution. Dataset generation, dataset validation, and all later activity remain separately governed and unauthorized.
