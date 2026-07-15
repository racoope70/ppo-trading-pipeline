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
