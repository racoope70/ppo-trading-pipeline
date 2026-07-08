# Milestone Review Reference Map

This file is a navigation map only.

PROJECT_CONTEXT.md controls the current project state, active milestone, latest checkpoint, authorization boundaries, blocked actions, and PPO v2 roadmap.

Long-form v3.07 validation-readiness history is archived here:

docs/archive/v3_07_validation_readiness_chain_summary.md

This map does not authorize validation-only preflight reruns, PPO v2 training, sealed training command execution, data fetching, data downloading, dataset generation, model promotion, paper orders, live orders, controlled submit, PPO + Random Forest, or PPO + XGBoost.

---

## Current Controlling State

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

---

## Current Active Review Path

### v3.07 Explicit Validation-Only Preflight Rerun Authorization Checkpoint

Use this path only when reviewing whether a validation-only preflight rerun may be considered after the sealed dataset local placement requirement was documented and reviewed.

This map does not authorize the rerun.

---

## Files to Review First

PROJECT_CONTEXT.md
docs/workflows/milestone_review_reference_map.md
docs/archive/v3_07_validation_readiness_chain_summary.md
docs/runs/v3.07_documentation_slimming_source_of_truth_refactor_authorization_checkpoint.md
docs/runs/v3.07_sealed_dataset_availability_path_local_placement_remediation.md

---

## Historical Phase Map

Detailed chronology is preserved here:

docs/archive/v3_07_validation_readiness_chain_summary.md

Condensed phase map:

v3.07 initial authorization review = FAIL
v3.07 static no-submit package preparation = COMPLETED
v3.07 independent package authorization review = FAIL
v3.07 source-code execution compatibility checkpoint = COMPLETED
v3.07 independent source-code compatibility review = PASS_SOURCE_CODE_COMPATIBILITY_ONLY
v3.07 sealed authorization/preflight readiness review = FAIL_READINESS
v3.07 sealed preflight evidence remediation plan = RECORDED
v3.07 validation-only preflight readiness scaffold = IMPLEMENTED
v3.07 scaffold review = PASS_SCAFFOLD_ONLY
v3.07 R1 preflight blocker typo fix = COMPLETED
v3.07 sealed preflight evidence remediation review = PASS_EVIDENCE_REMEDIATION_REVIEW_ONLY
v3.07 explicit validation-only preflight authorization checkpoint = PASS_VALIDATION_ONLY_PREFLIGHT_AUTHORIZATION
v3.07 validation-only preflight execution = PARTIAL_FAIL
v3.07 fail-closed evidence review = PASS_FAIL_CLOSED_EVIDENCE_REVIEW_ONLY
v3.07 sealed dataset local placement remediation = DOCUMENTED_MISSING_LOCAL_PLACEMENT_REQUIREMENT
v3.07 sealed dataset local placement evidence review = PASS_DOCUMENTED_LOCAL_PLACEMENT_REQUIREMENT_ONLY
v3.07 documentation slimming authorization checkpoint = PASS_DOCS_ONLY_REFACTOR_AUTHORIZATION

---

## Special Review Paths

### Validation-only preflight rerun authorization review

Before any rerun can be considered, confirm:

validation_only_preflight_rerun = NOT_AUTHORIZED
preflight_readiness = NOT_PASSED
sealed_dataset_validation = NOT_PROVEN

### Training or sealed training command review

Stop unless a later sealed checkpoint explicitly authorizes it.

ppo_v2_training_execution = NOT_AUTHORIZED
sealed_training_command_execution = NOT_AUTHORIZED
training_command_execution = NOT_AUTHORIZED
model_learn = NOT_AUTHORIZED
model_fitting = NOT_AUTHORIZED

### Dataset or data movement review

Stop unless a later checkpoint explicitly authorizes it.

data_fetching = NOT_AUTHORIZED
data_downloading = NOT_AUTHORIZED
dataset_generation = NOT_AUTHORIZED
dataset_backfill = NOT_AUTHORIZED
dataset_mutation_or_rewrite = NOT_AUTHORIZED

---

## Global Guardrail

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

Any contradiction between archived records and this guardrail is resolved in favor of PROJECT_CONTEXT.md.
