# PROJECT_CONTEXT.md

Authoritative source of truth for `racoope70/ppo-trading-pipeline`.

Detailed v3.07 history is archived at `docs/archive/v3_07_validation_readiness_chain_summary.md`. The missing v3.07 dataset remains historical context only.

---

## 1. Current source-of-truth summary

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

## 3. Completed prerequisites

```text
source_test_implementation_commit = 4cbb979a88176c252abcf5e1cd2f310c605573e9
mocked_unit_contract_testing_commit = 5cc08e0bcaa570b2fe01e0e984e3557f9e324856
mocked_unit_contract_testing_result = PASS
requirements_pin = exchange-calendars==4.13.2
XNYS_runtime_verification_execution_result = PASS_XNYS_RUNTIME_VERIFICATION_COMPLETED
data_fetch_authorization_commit = d2b44e952a2350e312f6b7b4298beeea912a7e8f
data_fetch_execution_commit = 3a49775514ff5c21a51ef192e970e269ed8b5ceb
data_fetch_execution_result = PASS_DATA_FETCH_EXECUTION_RAW_HISTORICAL_BARS_FETCH_COMPLETED
```

## 4. Current authorization state

```text
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

The current checkpoint must not:

- treat the dataset as validated;
- run dataset validation or validation-only preflight;
- run training or create model artifacts;
- submit paper or live orders;
- deploy; or
- tag.

## 5. Completed governance chain

1. Dependency and runtime prerequisites completed.
2. Dataset reconstruction source/test implementation completed.
3. Mocked unit and contract testing passed.
4. Data-fetch authorization passed for data-fetch execution only.
5. Alpaca sort-import compatibility remediation passed.
6. Data-fetch execution completed under the governed historical-bars contract.
7. Dataset-generation authorization passed for dataset-generation execution only at commit `cfdb99543a886e1e4604443a520b006cf9587c15`.

## 6. Forward roadmap

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

```text
future_validation_training_reference_map = docs/workflows/future_validation_training_reference_map.md
```

The future reference map is guidance only and does not authorize execution.

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

The current checkpoint authorizes only dataset-generation execution. Dataset validation and all later activity remain separately governed.
