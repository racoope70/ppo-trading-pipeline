# PROJECT_CONTEXT.md

Authoritative source-of-truth document for `racoope70/ppo-trading-pipeline`.

This file controls the current project state, active milestone, validation standards, blocked actions, and audit boundaries for the PPO trading pipeline.

Long-form v3.07 validation-readiness history has been moved to:

docs/archive/v3_07_validation_readiness_chain_summary.md

---

## 1. Current Source-of-Truth Summary

latest_completed_milestone = v3.07 Sealed Dataset Local Placement Evidence Review
latest_completed_decision = PASS_DOCUMENTED_LOCAL_PLACEMENT_REQUIREMENT_ONLY
active_milestone = v3.07 Explicit Validation-Only Preflight Rerun Authorization Checkpoint
next_checkpoint = explicit authorization checkpoint before validation-only preflight rerun
current_workstream = PPO_V2_VALIDATION_READINESS
current_phase = sealed dataset local placement requirement documented and reviewed; validation-only preflight rerun requires explicit later authorization
v3.07_status = BLOCKED
NO_SUBMIT = DEFAULT
preflight_readiness = NOT_PASSED
sealed_dataset_validation = NOT_PROVEN
validation_only_preflight_rerun = NOT_AUTHORIZED
ppo_v2_training_execution = NOT_AUTHORIZED
sealed_training_command_execution = NOT_AUTHORIZED
training_command_execution = NOT_AUTHORIZED
model_learn = NOT_AUTHORIZED
model_fitting = NOT_AUTHORIZED
data_fetching = NOT_AUTHORIZED
data_downloading = NOT_AUTHORIZED
dataset_generation = NOT_AUTHORIZED
dataset_backfill = NOT_AUTHORIZED
dataset_mutation_or_rewrite = NOT_AUTHORIZED
model_artifact_creation = NOT_AUTHORIZED
quarantine_model_output_creation = NOT_AUTHORIZED
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf = BLOCKED
ppo_xgboost = BLOCKED
model_promotion = NOT_AUTHORIZED
production_deployment = NOT_AUTHORIZED
trading_edge_claims = NOT_AUTHORIZED
profitability_claims = NOT_AUTHORIZED
deployment_readiness_claims = NOT_AUTHORIZED
legacy_ppo_retraining_decision = DO_NOT_RETRAIN_LEGACY_MODEL
expected_sealed_dataset_path = data/processed/ppo_v2/v3_07_no_submit_training_input.parquet
accepted_preflight_result = PARTIAL_FAIL
R1 = PASS
R2 = FAIL_SEALED_DATASET_NOT_FOUND
R3 = FAIL_DEPENDS_ON_R2
R4 = FAIL_DEPENDS_ON_R2
R5 = FAIL_DEPENDS_ON_R2
R6 = PASS

The latest completed checkpoint documented and reviewed the missing local placement requirement for the sealed v3.07 dataset. The expected sealed dataset path remains:

data/processed/ppo_v2/v3_07_no_submit_training_input.parquet

The accepted validation-only preflight evidence remains `PARTIAL_FAIL`. R1 and R6 passed. R2 failed because the sealed local dataset was not found. R3, R4, and R5 failed because they depend on R2. This is valid fail-closed evidence, not readiness.

The active milestone is an explicit authorization checkpoint before any validation-only preflight rerun. This file does not authorize the rerun.

---

## 2. Active Milestone

active_milestone = v3.07 Explicit Validation-Only Preflight Rerun Authorization Checkpoint
next_checkpoint = explicit authorization checkpoint before validation-only preflight rerun

The active checkpoint may only review whether a validation-only preflight rerun should be explicitly authorized later. It does not authorize PPO v2 training, sealed training command execution, model fitting, data movement, artifact creation, orders, controlled submit, hybrid models, model promotion, production deployment, or readiness/edge/profitability claims.

---

## 3. Hard Non-Authorization Boundary

v3.07_status = BLOCKED
NO_SUBMIT = DEFAULT
preflight_readiness = NOT_PASSED
sealed_dataset_validation = NOT_PROVEN
validation_only_preflight_rerun = NOT_AUTHORIZED
ppo_v2_training_execution = NOT_AUTHORIZED
sealed_training_command_execution = NOT_AUTHORIZED
training_command_execution = NOT_AUTHORIZED
model_learn = NOT_AUTHORIZED
model_fitting = NOT_AUTHORIZED
data_fetching = NOT_AUTHORIZED
data_downloading = NOT_AUTHORIZED
dataset_generation = NOT_AUTHORIZED
dataset_backfill = NOT_AUTHORIZED
dataset_mutation_or_rewrite = NOT_AUTHORIZED
model_artifact_creation = NOT_AUTHORIZED
quarantine_model_output_creation = NOT_AUTHORIZED
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf = BLOCKED
ppo_xgboost = BLOCKED
model_promotion = NOT_AUTHORIZED
production_deployment = NOT_AUTHORIZED
trading_edge_claims = NOT_AUTHORIZED
profitability_claims = NOT_AUTHORIZED
deployment_readiness_claims = NOT_AUTHORIZED
legacy_ppo_retraining_decision = DO_NOT_RETRAIN_LEGACY_MODEL

These lines are controlling. Historical records, package manifests, scaffold records, and workflow maps do not override them.

---

## 4. Validation Hierarchy

source_of_truth = PROJECT_CONTEXT.md
navigation_map = docs/workflows/milestone_review_reference_map.md
historical_chain_archive = docs/archive/v3_07_validation_readiness_chain_summary.md

Current validation hierarchy:

1. `PROJECT_CONTEXT.md` controls the current state and hard boundaries.
2. `docs/workflows/milestone_review_reference_map.md` provides navigation only.
3. `docs/archive/v3_07_validation_readiness_chain_summary.md` preserves the detailed v3.07 historical chain.
4. Prior audit/run records remain historical evidence and do not authorize current execution unless this file says so.

---

## 5. Artifact and Generated Data Policy

The expected sealed dataset path is:

data/processed/ppo_v2/v3_07_no_submit_training_input.parquet

The repository has documented the missing local placement requirement for that path. This does not prove sealed dataset validation and does not authorize dataset creation, dataset movement, sealed dataset validation, or a validation-only preflight rerun.

Generated/local data remains local-only unless a later checkpoint explicitly authorizes a different policy. No data fetching, data downloading, dataset generation, dataset backfill, dataset mutation/rewrite, model artifact creation, or quarantine model output creation is authorized.

---

## 6. Core Navigation Links

v3_07_validation_readiness_chain_archive = docs/archive/v3_07_validation_readiness_chain_summary.md
documentation_slimming_authorization_record = docs/runs/v3.07_documentation_slimming_source_of_truth_refactor_authorization_checkpoint.md
sealed_dataset_local_placement_remediation_record = docs/runs/v3.07_sealed_dataset_availability_path_local_placement_remediation.md
milestone_reference_map = docs/workflows/milestone_review_reference_map.md

Use the archive when detailed v3.07 chronology is needed. Use this file for current authorization state.

---

## 7. Current Bottom Line

current_bottom_line = validation-only preflight rerun requires explicit later authorization

The project remains blocked for PPO v2 training and sealed training command execution. The explicit validation-only preflight rerun authorization checkpoint is the active milestone, but the rerun itself remains `NOT_AUTHORIZED` until a later checkpoint explicitly authorizes it.
