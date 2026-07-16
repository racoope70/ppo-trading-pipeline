# Milestone Review Reference Map

Navigation map for the active v3.08 superseding governed Alpaca-aligned reconstruction workstream. `PROJECT_CONTEXT.md` remains authoritative.

---

## 1. Current controlling state

```text
current_workstream = PPO_V2_SUPERSEDING_DATASET_RECONSTRUCTION
active_phase = v3.08 Source-of-Truth Alignment After Data-Fetch Execution
latest_completed_checkpoint = v3.08 Data-Fetch Execution
latest_completed_commit = 3a49775514ff5c21a51ef192e970e269ed8b5ceb
latest_completed_decision = PASS_DATA_FETCH_EXECUTION_RAW_HISTORICAL_BARS_FETCH_COMPLETED
latest_completed_record = docs/runs/v3.08_data_fetch_execution.md
latest_completed_ci = NOT_INDEPENDENTLY_VERIFIED_IN_THIS_CHECKPOINT
current_active_checkpoint = v3.08 Source-of-Truth Alignment After Data-Fetch Execution
next_checkpoint = v3.08 Dataset-Generation Authorization
```

The governed raw historical-bars data fetch is complete. This alignment checkpoint does not authorize dataset generation or any downstream execution.

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
dataset_generation_authorized = NO
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

The current alignment checkpoint records the completed data-fetch execution only. It does not authorize dataset generation. Dataset-generation authorization is the next checkpoint only after this alignment is committed.

## 6. Files to review first

1. `PROJECT_CONTEXT.md`
2. `docs/runs/v3.08_data_fetch_authorization.md`
3. `docs/runs/v3.08_mocked_unit_contract_testing.md`
4. `docs/runs/v3.08_dataset_reconstruction_implementation_authorization.md`
5. `src/ppo_v2_dataset_reconstruction.py`
6. `src/ppo_v2_data_contract.py`
7. `src/ppo_v2_market_calendar.py`
8. `src/ppo_v2_parquet_writer.py`

## 2v. Numbered Governance Lookup

Use this lookup to select the governance guidance for the requested class of work.

```text
source/test implementation                      -> 2v.10
mocked unit and contract testing                -> 2v.20
data-fetch authorization or execution           -> 2v.30
dataset-generation authorization/execution      -> 2v.40
dataset evidence review                         -> 2v.40
dataset validation or validation-only preflight -> 2v.50
embargo or VecNormalize hardening               -> 2v.60
PPO retraining authorization/execution          -> 2v.70
final holdout or candidate selection            -> 2v.80
paper trading, deployment, or live discussion   -> 2v.90
future universe expansion                       -> 2v.100
```

Read the latest applicable run, audit, review, plan, and authorization records if they exist. Absence of a record means the gate is not complete; do not invent a filename, decision, result, or authorization.

### 2v.00 Current source-of-truth entry point

- **When to use:** Before every task or checkpoint.
- **Read first:** `PROJECT_CONTEXT.md`, this milestone map, and the latest applicable authorization and review records.
- **Stop condition / gate:** Stop if freshness fails, the requested work is outside the active checkpoint, or a required record is absent.
- **Still prohibited unless separately authorized:** Any activity outside the exact authorization recorded in `PROJECT_CONTEXT.md`.

### 2v.10 Implementation and source/test checkpoints

- **When to use:** Planning, authorizing, implementing, or reviewing source/test changes.
- **Read first:** Current contract, implementation plan, implementation authorization, latest independent plan review, and applicable source/test evidence.
- **Stop condition / gate:** Stop unless the exact source/test scope and allowed files are authorized.
- **Still prohibited unless separately authorized:** Data access, dataset generation, validation, preflight, training, artifacts, orders, deployment, and tagging.

### 2v.20 Mocked unit and contract testing

- **When to use:** Testing governed behavior without live network access or output-producing execution.
- **Read first:** Source/test implementation evidence, implementation authorization, current contract and plan, and the latest mocked-testing record.
- **Stop condition / gate:** Stop unless tests are mocked, fail-closed, isolated from live APIs, and non-output-producing.
- **Still prohibited unless separately authorized:** Live clients, market-data access, dataset creation, validation, training, artifacts, orders, deployment, and tagging.

### 2v.30 Data-fetch authorization and market-data access

- **When to use:** Data-fetch authorization or execution, Alpaca historical access, credentials, pagination, or request-literal review.
- **Read first:** `PROJECT_CONTEXT.md`, mocked-testing evidence, implementation authorization, contract resolution, latest independent review, and applicable fetch authorization or execution records.
- **Stop condition / gate:** Stop unless separate authorization exists for the exact source, universe, timeframe, feed, adjustment, credentials, request, and output boundary.
- **Still prohibited unless separately authorized:** Dataset generation, validation, preflight, training, artifacts, orders, deployment, and tagging.

### 2v.40 Dataset generation and dataset evidence

- **When to use:** Dataset-generation authorization or execution, or review of manifests, checksums, provenance, schema, gaps, and run evidence.
- **Read first:** Data-fetch authorization and execution evidence, dataset contract, generation plan and authorization, run evidence, and latest independent dataset-evidence review.
- **Stop condition / gate:** Stop unless fetch and generation authority both exist; do not accept output unless its identity and evidence agree.
- **Still prohibited unless separately authorized:** Treating the dataset as validated, preflight, training, model artifacts, orders, deployment, and tagging.

### 2v.50 Dataset validation and validation-only preflight

- **When to use:** Dataset-validation or validation-only preflight authorization, execution, or review.
- **Read first:** Accepted dataset evidence, validation authorization and plan, exact dataset identity and checksum, validation results, preflight authorization, and split/feature controls.
- **Stop condition / gate:** Stop unless the exact validation or preflight action is separately authorized; preflight must not fit a model or consume the final holdout.
- **Still prohibited unless separately authorized:** PPO fitting, candidate promotion, model artifacts, paper orders, live orders, deployment, and tagging.

### 2v.60 Embargo and VecNormalize hardening

- **When to use:** Temporal leakage, train/evaluation separation, normalization-state handling, or pre-training validation design.
- **Read first:** The matching section of `docs/workflows/future_validation_training_reference_map.md`, `docs/workflows/ppo_validation_hardening.md`, split and lookback rules, and accepted preflight evidence.
- **Stop condition / gate:** Stop unless embargo rules are fixed and VecNormalize statistics are training-only and locked during evaluation and holdout.
- **Still prohibited unless separately authorized:** Holdout tuning, feature or parameter changes based on holdout, and training execution.

### 2v.70 PPO retraining authorization and execution

- **When to use:** PPO retraining planning, authorization, execution, configuration, artifact boundaries, or training audit.
- **Read first:** Accepted validation and preflight evidence, 2v.60 controls, training authorization, `docs/workflows/alpaca_ppo_retraining_validation_plan.md`, and the frozen training configuration.
- **Stop condition / gate:** Stop unless the dataset checksum, code commit, configuration, seeds, artifact paths, evaluation rules, and candidate-ranking rule are frozen and authorized.
- **Still prohibited unless separately authorized:** Holdout inspection during training, paper orders, live orders, deployment, universe expansion, and tagging.

### 2v.80 Final holdout and candidate selection

- **When to use:** Untouched holdout evaluation, candidate eligibility, ranking, promotion, or artifact review.
- **Read first:** Training execution and artifact review, `docs/workflows/alpaca_ppo_final_holdout_validation.md`, `docs/workflows/alpaca_ppo_candidate_selection_redeployment.md`, and frozen candidate and threshold records.
- **Stop condition / gate:** Stop if holdout data influenced features, parameters, thresholds, universe, or ranking rules; selection rules must predate holdout inspection.
- **Still prohibited unless separately authorized:** Repeated holdout tuning, paper orders, live orders, deployment, universe expansion, and tagging.

### 2v.90 Paper trading and deployment boundaries

- **When to use:** Dry-run inference, broker-connected checks, paper authorization, deployment readiness, or live-order discussion.
- **Read first:** Final-holdout acceptance, candidate-selection evidence, artifact review, `docs/workflows/alpaca_paper_trading_integration.md`, risk controls, execution plan, pre-trade checklist, and explicit authorization records.
- **Stop condition / gate:** Stop unless the exact candidate and artifacts are identified, paper-only and no-submit controls are proven, and the requested order or deployment mode is explicitly authorized.
- **Still prohibited unless separately authorized:** Implicit or unattended orders, live orders, production deployment, universe expansion, and tagging.

### 2v.100 Future universe expansion research

- **When to use:** Research beyond the governed six-symbol baseline.
- **Read first:** `PROJECT_CONTEXT.md`, `docs/workflows/six_ticker_quality_baseline.md`, accepted baseline validation, holdout, and paper evidence, plus a new expansion plan, contract, review, and authorization.
- **Stop condition / gate:** Stop unless expansion is isolated as a new research checkpoint with a separate universe contract and untouched evaluation design.
- **Still prohibited unless separately authorized:** Changing the current baseline contract, reusing its holdout, mixing expansion evidence into baseline acceptance, orders, deployment, and tagging.

This numbered lookup is a navigation aid only. It does not authorize source changes, test changes, requirements changes, dependency installation, data fetching, Alpaca API calls, dataset generation, validation, preflight, training, model artifacts, paper orders, live orders, deployment, or tagging.

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

## 8. Forward milestone roadmap

1. v3.08 Source-of-Truth Alignment After Data-Fetch Execution.
2. v3.08 Dataset-Generation Authorization.
3. v3.08 Dataset-Generation Execution.
4. v3.08 Dataset Evidence Review.
5. v3.08 Dataset-Validation Authorization.
6. v3.08 Dataset-Validation Execution.
7. v3.08 Validation-Only Preflight Authorization.
8. v3.08 Validation-Only Preflight Execution.
9. v3.08 Training Authorization.
10. v3.08 Training Execution.
11. v3.08 Artifact/Model Review.
12. v3.08 Paper-Trading Authorization.

Every later milestone remains separately governed.

## Future validation/training reference

For future validation, embargo, VecNormalize, retraining, final holdout, candidate selection, paper trading, and universe expansion guidance, read:

`docs/workflows/future_validation_training_reference_map.md`

This file is a reference guide only. It does not authorize any future work.

Before each future checkpoint, read:

1. `PROJECT_CONTEXT.md`.
2. This milestone map.
3. The matching section of `docs/workflows/future_validation_training_reference_map.md`.
4. The latest relevant run, audit, review, and authorization records.

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
git merge-base --is-ancestor 3a49775514ff5c21a51ef192e970e269ed8b5ceb HEAD
echo $?
```

## 11. Current bottom line

```text
current_active_checkpoint = v3.08 Source-of-Truth Alignment After Data-Fetch Execution
next_checkpoint = v3.08 Dataset-Generation Authorization
data_fetch_execution_checkpoint = COMPLETED
data_fetch_execution_result = PASS_DATA_FETCH_EXECUTION_RAW_HISTORICAL_BARS_FETCH_COMPLETED
dataset_generation_authorized = NO
```

The current alignment checkpoint does not authorize dataset generation. Dataset generation, validation, training, orders, deployment, and tagging remain unauthorized.
