# PROJECT_CONTEXT.md

Authoritative source of truth for `racoope70/ppo-trading-pipeline`.

Detailed v3.07 history is archived at `docs/archive/v3_07_validation_readiness_chain_summary.md`. The v3.07 validation-only preflight path and missing dataset path are historical context only; they are not the active milestone or current output target.

---

## 1. Current Source-of-Truth Summary

```text
current_workstream = PPO_V2_SUPERSEDING_DATASET_RECONSTRUCTION
active_phase = v3.08 Dataset Reconstruction Implementation Planning / Independent Review
latest_completed_checkpoint = v3.08 Dataset Reconstruction Implementation Plan Remediation
latest_completed_commit = e035cb022c06ce10a4d08d81df345a9da22cdebb
latest_completed_ci = NOT_RECORDED_IN_SOURCE_OF_TRUTH_FOR_E035CB0
current_active_checkpoint = v3.08 Independent Dataset Reconstruction Implementation Plan Review Repeat After Remediation
next_checkpoint = v3.08 Independent Dataset Reconstruction Implementation Plan Review Repeat After Remediation
```

The final contract resolution passed independent review after documentation remediation. Implementation planning was then authorized, and the documentation-only implementation plan was created and cleaned. Its independent review failed, the required documentation remediation is complete, and the repeated independent implementation-plan review is now active. No implementation or runtime activity is authorized.

## 2. Governing Reconstruction Classification

```text
reconstruction_classification = SUPERSEDING_GOVERNED_ALPACA_ALIGNED_RECONSTRUCTION
original_dataset_recovered = FALSE
byte_identical_original_dataset_recovery = NOT_CLAIMED
byte_identical_recovery_claim = PROHIBITED
historical_equivalence_claim = NOT_PROVEN
new_dataset_identity_required = TRUE
```

The selected path is a new governed Alpaca-aligned reconstruction standard, not recovery of the missing original v3.07 dataset.

## 3. Dataset Identity

```text
output_path = data/processed/ppo_v2/v3_08_superseding_alpaca_aligned_no_submit_training_input.parquet
old_missing_path = data/processed/ppo_v2/v3_07_no_submit_training_input.parquet
old_path_usage = HISTORICAL_MISSING_ARTIFACT_REFERENCE_ONLY
old_path_as_output_target = PROHIBITED
new_run_id_required = TRUE
new_manifest_required = TRUE
new_checksum_required = TRUE
```

The v3.07 missing path must not be used as an output target.

## 4. Governing Review and Implementation-Plan State

```text
final_contract_resolution_review_status = PASSED_INDEPENDENT_REVIEW_AFTER_REMEDIATION
final_contract_review_record = docs/audits/v3.08_independent_dataset_reconstruction_final_contract_resolution_review_repeat_after_remediation.md
implementation_planning_authorization_decision = PASS_IMPLEMENTATION_PLANNING_AUTHORIZATION_ONLY
implementation_plan_decision = PASS_IMPLEMENTATION_PLAN_FOR_FUTURE_AUTHORIZATION_REVIEW_ONLY
implementation_plan_file = docs/runs/v3.08_dataset_reconstruction_implementation_plan.md
implementation_plan_status = REMEDIATED_AWAITING_REPEATED_INDEPENDENT_REVIEW
implementation_readiness = NOT_ESTABLISHED
next_checkpoint = v3.08 Independent Dataset Reconstruction Implementation Plan Review Repeat After Remediation
```

The independent plan review may evaluate progression toward a later implementation-authorization checkpoint. It does not itself implement the plan.

## 5. Calendar and Runtime Status

```text
exchange_calendars_installed = NO
XNYS_local_runtime_verification = NOT_PERFORMED
calendar_runtime_verified = NO
calendar_version_status = GOVERNANCE_SELECTED_DEPENDENCY_PIN_PENDING_FUTURE_INSTALL_AND_RUNTIME_VERIFICATION
```

The final contract requires `exchange-calendars==4.13.2`, but dependency installation, requirements changes, and runtime verification remain separately governed future gates.

## 6. Hard Non-Authorization Boundary

```text
code_implementation = NOT_AUTHORIZED
source_code_changes = NOT_AUTHORIZED
test_changes = NOT_AUTHORIZED
dependency_installation = NOT_AUTHORIZED
requirements_change = NOT_AUTHORIZED
data_fetching = NOT_AUTHORIZED
data_downloading = NOT_AUTHORIZED
dataset_generation = NOT_AUTHORIZED
sealed_dataset_creation = NOT_AUTHORIZED
dataset_copy = NOT_AUTHORIZED
dataset_restore = NOT_AUTHORIZED
dataset_repair = NOT_AUTHORIZED
dataset_regeneration = NOT_AUTHORIZED
dataset_mutation = NOT_AUTHORIZED
dataset_rewrite = NOT_AUTHORIZED
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

No source, test, dependency, data, validation, training, model, trading, deployment, or tagging authority is implied by the completed documentation checkpoints.

## 7. Governing Chain

1. `docs/runs/v3.08_dataset_reconstruction_executive_contract_decision.md`
2. `docs/runs/v3.08_dataset_reconstruction_exchange_calendar_version_selection.md`
3. `docs/runs/v3.08_dataset_reconstruction_contract_literal_binding_remediation.md`
4. `docs/runs/v3.08_dataset_reconstruction_conditional_technical_literal_verification.md`
5. `docs/runs/v3.08_dataset_reconstruction_contract_resolution.md`
6. `docs/audits/v3.08_independent_dataset_reconstruction_final_contract_resolution_review.md`
7. `docs/audits/v3.08_independent_dataset_reconstruction_final_contract_resolution_review_repeat_after_remediation.md`
8. `docs/runs/v3.08_dataset_reconstruction_implementation_planning_authorization.md`
9. `docs/runs/v3.08_dataset_reconstruction_implementation_plan.md`

## 8. Forward Roadmap

1. v3.08 Independent Dataset Reconstruction Implementation Plan Review Repeat After Remediation.
2. If the repeated review passes: v3.08 Dataset Reconstruction Dependency/Requirements Authorization.
3. v3.08 Dataset Reconstruction Dependency Installation and XNYS Runtime Verification.
4. v3.08 Dataset Reconstruction Implementation Authorization.
5. v3.08 Dataset Reconstruction Source/Test Implementation.
6. Unit-test and contract-test checkpoint with mocked data only.
7. Data-fetch authorization checkpoint.
8. Dataset-generation authorization checkpoint.
9. Dataset-generation execution.
10. Dataset evidence review.
11. Dataset-validation authorization.
12. Dataset-validation execution.
13. Validation-only preflight authorization.
14. Validation-only preflight execution.
15. Training authorization.
16. Training execution.
17. Artifact/model review.
18. Paper-trading authorization.

Every step remains contingent on its own explicit authorization and any required independent review. Steps may be split further when risk requires.

Dependency/requirements authorization and completed dependency installation/XNYS runtime verification are prerequisites before implementation authorization can be reconsidered. Implementation authorization remains `NOT_ALLOWED / NOT_AUTHORIZED` until the repeated independent implementation-plan review passes and dependency/runtime verification is completed.

## 9. Freshness Guardrail

Before the current independent plan review from a local checkout:

```bash
git fetch origin
git status --short
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor e035cb022c06ce10a4d08d81df345a9da22cdebb HEAD
echo $?
```

Proceed only when the working tree is clean, `HEAD` equals `origin/main`, and the merge-base exit code is `0`.

## 10. Current Bottom Line

```text
implementation_plan_status = REMEDIATED_AWAITING_REPEATED_INDEPENDENT_REVIEW
current_active_checkpoint = v3.08 Independent Dataset Reconstruction Implementation Plan Review Repeat After Remediation
next_checkpoint = v3.08 Independent Dataset Reconstruction Implementation Plan Review Repeat After Remediation
implementation_authorization = NOT_ALLOWED / NOT_AUTHORIZED
implementation_authorized = NO
runtime_execution_authorized = NO
```

The active next action is the independent implementation-plan review repeat after remediation, not implementation or execution.
