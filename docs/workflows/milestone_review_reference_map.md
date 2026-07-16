# Milestone Review Reference Map

Navigation map for the active v3.08 superseding governed Alpaca-aligned reconstruction workstream. `PROJECT_CONTEXT.md` remains authoritative.

---

## 1. Current controlling state

```text
current_workstream = PPO_V2_SUPERSEDING_DATASET_RECONSTRUCTION
active_phase = v3.08 Dataset-Generation Execution
latest_completed_checkpoint = v3.08 Dataset-Generation Authorization
latest_completed_commit = cfdb99543a886e1e4604443a520b006cf9587c15
latest_completed_decision = PASS_DATASET_GENERATION_AUTHORIZATION_FOR_DATASET_GENERATION_EXECUTION_CHECKPOINT_ONLY
latest_completed_record = docs/runs/v3.08_dataset_generation_authorization.md
latest_completed_ci = NOT_INDEPENDENTLY_VERIFIED_IN_THIS_CHECKPOINT
current_active_checkpoint = v3.08 Dataset-Generation Execution
next_checkpoint = v3.08 Dataset-Generation Execution
```

Dataset-generation execution is current under the separately authorized governed contract. Validation and all later execution remain unauthorized.

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

## 3. Current authorization state

```text
data_fetch_authorization_checkpoint = COMPLETED
data_fetch_execution_checkpoint = COMPLETED
data_fetch_execution_record = docs/runs/v3.08_data_fetch_execution.md
data_fetch_execution_result = PASS_DATA_FETCH_EXECUTION_RAW_HISTORICAL_BARS_FETCH_COMPLETED
dataset_generation_authorization_checkpoint = COMPLETED
dataset_generation_authorization_record = docs/runs/v3.08_dataset_generation_authorization.md
dataset_generation_authorization_commit = cfdb99543a886e1e4604443a520b006cf9587c15
dataset_generation_authorization_result = PASS
dataset_generation_authorization_decision = PASS_DATASET_GENERATION_AUTHORIZATION_FOR_DATASET_GENERATION_EXECUTION_CHECKPOINT_ONLY
dataset_generation_authorized = YES
authorized_current_execution_scope = DATASET_GENERATION_EXECUTION_ONLY
dataset_generation_execution_checkpoint = CURRENT
dataset_generation_execution_record = NOT_CREATED
dataset_generation_execution_result = NOT_YET_PERFORMED
dataset_validation_authorized = NO
validation_only_preflight_authorized = NO
training_authorized = NO
orders_authorized = NO
deployment_authorized = NO
tagging_authorized = NO
```

The current Dataset-Generation Execution checkpoint may only:

- read the local ignored raw parquet produced by v3.08 Data-Fetch Execution;
- transform the governed six-symbol Alpaca bars into the v3.08 final dataset identity;
- apply the contract-defined canonical window, warmup, session policy, feature engineering, dtype rules, gap rules, and final column order;
- write the governed final dataset path only if every contract check passes;
- write the required dataset-generation execution evidence; and
- write the required manifest and checksum only when included in the execution checkpoint.

It must not treat the dataset as validated, run validation or preflight, train a model, create model artifacts, submit orders, deploy, or tag.

## 4. Files to review first

1. `PROJECT_CONTEXT.md`
2. `docs/runs/v3.08_dataset_generation_authorization.md`
3. `docs/runs/v3.08_data_fetch_execution.md`
4. `docs/runs/v3.08_data_fetch_execution_remediation_alpaca_sort_import.md`
5. `docs/runs/v3.08_data_fetch_authorization.md`
6. `docs/runs/v3.08_dataset_reconstruction_contract_resolution.md`
7. `docs/runs/v3.08_mocked_unit_contract_testing.md`
8. `docs/runs/v3.08_dataset_reconstruction_implementation_authorization.md`
9. `src/ppo_v2_dataset_reconstruction.py`
10. `src/ppo_v2_data_contract.py`
11. `src/ppo_v2_market_calendar.py`
12. `src/ppo_v2_parquet_writer.py`

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
- **Still prohibited unless separately authorized:** Anything outside the exact authorization in `PROJECT_CONTEXT.md`.

### 2v.10 Implementation and source/test checkpoints

- **When to use:** Planning, authorizing, implementing, or reviewing source/test changes.
- **Read first:** Current contract, implementation plan and authorization, latest independent review, and source/test evidence.
- **Stop condition / gate:** Stop unless the exact scope and allowed files are authorized.
- **Still prohibited unless separately authorized:** Data access, dataset generation, validation, preflight, training, artifacts, orders, deployment, and tagging.

### 2v.20 Mocked unit and contract testing

- **When to use:** Testing governed behavior without live network access or output-producing execution.
- **Read first:** Implementation evidence and authorization, current contract, and latest mocked-testing record.
- **Stop condition / gate:** Stop unless tests are mocked, fail-closed, isolated from live APIs, and non-output-producing.
- **Still prohibited unless separately authorized:** Live clients, market data, dataset creation, validation, training, artifacts, orders, deployment, and tagging.

### 2v.30 Data-fetch authorization and market-data access

- **When to use:** Data-fetch authorization or execution, credentials, pagination, or request-literal review.
- **Read first:** `PROJECT_CONTEXT.md`, mocked-testing evidence, implementation authorization, contract resolution, and applicable fetch records.
- **Stop condition / gate:** Stop unless authorization exists for the exact source, universe, timeframe, feed, adjustment, credentials, request, and output boundary.
- **Still prohibited unless separately authorized:** Dataset generation, validation, preflight, training, artifacts, orders, deployment, and tagging.

### 2v.40 Dataset generation and dataset evidence

- **When to use:** Dataset-generation authorization or execution, or review of manifests, checksums, provenance, schema, gaps, and run evidence.
- **Read first:** Fetch authorization and execution evidence, dataset contract, generation authorization, run evidence, and latest dataset-evidence review.
- **Stop condition / gate:** Stop unless fetch and generation authority both exist; do not accept output unless identity and evidence agree.
- **Still prohibited unless separately authorized:** Treating the dataset as validated, preflight, training, model artifacts, orders, deployment, and tagging.

### 2v.50 Dataset validation and validation-only preflight

- **When to use:** Dataset-validation or validation-only preflight authorization, execution, or review.
- **Read first:** Accepted dataset evidence, exact identity/checksum, validation plan and authorization, results, preflight authorization, and split controls.
- **Stop condition / gate:** Stop unless the exact action is separately authorized; preflight must not fit a model or consume final holdout.
- **Still prohibited unless separately authorized:** PPO fitting, candidate promotion, artifacts, orders, deployment, and tagging.

### 2v.60 Embargo and VecNormalize hardening

- **When to use:** Temporal leakage, train/evaluation separation, normalization-state handling, or pre-training validation design.
- **Read first:** The matching future-reference section, `docs/workflows/ppo_validation_hardening.md`, split/lookback rules, and accepted preflight evidence.
- **Stop condition / gate:** Stop unless embargo rules are fixed and VecNormalize statistics are training-only and locked during evaluation and holdout.
- **Still prohibited unless separately authorized:** Holdout tuning and training execution.

### 2v.70 PPO retraining authorization and execution

- **When to use:** PPO retraining planning, authorization, execution, configuration, artifact boundaries, or audit.
- **Read first:** Accepted validation and preflight evidence, 2v.60 controls, training authorization, retraining plan, and frozen configuration.
- **Stop condition / gate:** Stop unless dataset checksum, code commit, configuration, seeds, artifact paths, evaluation rules, and ranking rule are frozen and authorized.
- **Still prohibited unless separately authorized:** Holdout inspection during training, orders, deployment, universe expansion, and tagging.

### 2v.80 Final holdout and candidate selection

- **When to use:** Untouched holdout evaluation, candidate eligibility, ranking, promotion, or artifact review.
- **Read first:** Training execution and artifact review, final-holdout guide, candidate-selection guide, and frozen candidate/threshold records.
- **Stop condition / gate:** Stop if holdout influenced features, parameters, thresholds, universe, or ranking rules.
- **Still prohibited unless separately authorized:** Repeated holdout tuning, orders, deployment, universe expansion, and tagging.

### 2v.90 Paper trading and deployment boundaries

- **When to use:** Dry-run inference, broker-connected checks, paper authorization, deployment readiness, or live-order discussion.
- **Read first:** Final-holdout acceptance, candidate-selection evidence, artifact review, paper-trading guide, risk controls, and explicit authorization records.
- **Stop condition / gate:** Stop unless the exact candidate/artifacts are identified, no-submit controls are proven, and the requested mode is authorized.
- **Still prohibited unless separately authorized:** Unattended orders, live orders, production deployment, universe expansion, and tagging.

### 2v.100 Future universe expansion research

- **When to use:** Research beyond the governed six-symbol baseline.
- **Read first:** `PROJECT_CONTEXT.md`, six-ticker baseline, accepted baseline evidence, and a new expansion plan, contract, review, and authorization.
- **Stop condition / gate:** Stop unless expansion is isolated as a new checkpoint with a separate universe contract and untouched evaluation design.
- **Still prohibited unless separately authorized:** Changing the baseline contract, reusing its holdout, mixing evidence, orders, deployment, and tagging.

This numbered lookup is a navigation aid only. It does not authorize source changes, test changes, requirements changes, dependency installation, data fetching, Alpaca API calls, dataset generation, validation, preflight, training, model artifacts, paper orders, live orders, deployment, or tagging.

## 5. Completed governance chain

1. Dependency and runtime prerequisites completed.
2. Source/test implementation completed.
3. Mocked unit and contract testing passed.
4. Data-fetch authorization passed for data-fetch execution only.
5. Alpaca sort-import compatibility remediation passed.
6. Data-fetch execution completed under the governed historical-bars contract.
7. Dataset-generation authorization passed for dataset-generation execution only at commit `cfdb99543a886e1e4604443a520b006cf9587c15`.

## 6. Forward milestone roadmap

1. v3.08 Dataset-Generation Execution.
2. Source-of-truth alignment after dataset-generation execution.
3. Dataset Evidence Review.
4. Dataset-Validation Authorization.
5. Dataset-Validation Execution.
6. Validation-Only Preflight Authorization.
7. Validation-Only Preflight Execution.
8. Training Authorization.
9. Training Execution.
10. Artifact/Model Review.
11. Paper-Trading Authorization.

Every later milestone remains separately governed.

## Future validation/training reference

Read `docs/workflows/future_validation_training_reference_map.md` for future validation, embargo, VecNormalize, retraining, final holdout, candidate selection, paper trading, and universe-expansion guidance. It is guidance only and does not authorize work.

## 7. Alignment checkpoint action confirmations

```text
source_code_changed = NO
tests_changed = NO
requirements_changed = NO
dependencies_installed = NO
market_data_accessed = NO
Alpaca_API_called = NO
live_Alpaca_client_created = NO
datasets_created = NO
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

## 8. Freshness guardrail

```bash
git fetch origin
git status --short
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor cfdb99543a886e1e4604443a520b006cf9587c15 HEAD
echo $?
```

## 9. Current bottom line

```text
current_active_checkpoint = v3.08 Dataset-Generation Execution
next_checkpoint = v3.08 Dataset-Generation Execution
dataset_generation_authorization_checkpoint = COMPLETED
dataset_generation_execution_checkpoint = CURRENT
dataset_generation_authorized = YES
dataset_validation_authorized = NO
```

The current checkpoint authorizes only dataset-generation execution. Dataset validation, training, orders, deployment, and tagging remain unauthorized.
