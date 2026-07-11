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

<!-- V3.08_CURRENT_PROJECT_CONTEXT_ALIGNMENT_START -->
# v3.08 Current Project Context / Roadmap Alignment

## Current Confirmed State

```text
v3.07 closeout_commit = 137be6f
v3.07 closeout_ci = Tests #373 green
v3.07 run-id/fail-closed remediation = COMPLETE
v3.07 validation-only rerun = CONSUMED
v3.07 validation-only rerun result = PARTIAL_FAIL
R1 = PASS
R2 = FAIL
R3 = FAIL
R4 = FAIL
R5 = FAIL
R6 = PASS
remaining_blocker = missing sealed dataset
missing_dataset_path = data/processed/ppo_v2/v3_07_no_submit_training_input.parquet
preflight_readiness = NOT_PASSED
sealed_dataset_validation = NOT_PROVEN
training = NOT_AUTHORIZED
```

## v3.08 Recovery / Diagnostics Chain

```text
diagnostics_authorization_commit = ba9f63a
diagnostics_authorization_ci = Tests #374 green

diagnostics_inspection_commit = 9c0b371
diagnostics_inspection_ci = Tests #375 green

recovery_strategy_commit = f7277aa
recovery_strategy_ci = Tests #376 green

trusted_external_artifact_source_authorization_commit = b500913
trusted_external_artifact_source_authorization_ci = Tests #377 green
```

## v3.08 Diagnostics Finding

```text
source_of_truth_issue_category = DATASET_PATH_APPEARS_GITIGNORED_OR_EXCLUDED
dataset_exists_locally = FALSE
dataset_tracked_by_git = FALSE
dataset_ignored_by_gitignore = TRUE
v3_07_config_points_to_missing_path = TRUE
another_copy_exists_under_data_or_artifacts = FALSE
git_history_shows_dataset_ever_committed_exact_path = FALSE
```

## Preserved Authorization State

```text
preflight_readiness = NOT_PASSED
sealed_dataset_validation = NOT_PROVEN

validation_only_preflight_rerun = NOT_AUTHORIZED
additional_validation_only_preflight_rerun = NOT_AUTHORIZED

sealed_dataset_recovery = NOT_AUTHORIZED
sealed_dataset_restore = NOT_AUTHORIZED
sealed_dataset_copy = NOT_AUTHORIZED
sealed_dataset_repair = NOT_AUTHORIZED
sealed_dataset_regeneration = NOT_AUTHORIZED
sealed_dataset_mutation_or_rewrite = NOT_AUTHORIZED
sealed_dataset_validation_execution = NOT_AUTHORIZED

ppo_v2_training_execution = NOT_AUTHORIZED
sealed_training_command_execution = NOT_AUTHORIZED
training = NOT_AUTHORIZED

model_artifact_creation = NOT_AUTHORIZED
quarantine_output_creation = NOT_AUTHORIZED
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
model_promotion = NOT_AUTHORIZED
production_deployment = NOT_AUTHORIZED
deployment_readiness_claims = NOT_AUTHORIZED
trading_edge_claims = NOT_AUTHORIZED
profitability_claims = NOT_AUTHORIZED
tagging = NOT_AUTHORIZED
```

## Immediate Next Investigation Direction

```text
next_checkpoint = v3.08 Repository Artifact Lineage / Model-Section Source Inspection
```

Purpose:

Inspect repository-controlled files and model-section artifacts across:

```text
racoope70/ppo-trading-pipeline
racoope70/quant-trading-model-validation, if available locally or through GitHub
```

Target lineage:

```text
data/processed/ppo_v2/v3_07_no_submit_training_input.parquet
```

The next search target is not random local folders. The target is repository/source-controlled lineage:

```text
configs
package-prep records
artifact manifests
checksum/inventory files
model-section docs
generation scripts
feature configs
ticker universe records
date range records
split/embargo/holdout rules
prior validation/training records
```

Do not proceed with broad local Desktop, Downloads, Google Drive, or CloudStorage artifact inspection unless exact approved locations are later provided in a separate authorized checkpoint.

## Command-Contract Guardrail

Verify that any command/run_id/path/config/output/evidence path in the checkpoint matches source code, config, command manifest, artifact manifest, or source-of-truth record.

Do not accept manually invented values.

If run_id is involved, confirm:

```text
authorized_command_run_id == source_required_run_id
```

## Execution-Head Freshness Guardrail

Before any authorized execution:

```bash
git fetch origin
git status --short
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor <latest_required_authorization_or_review_commit> HEAD
```

Execution may proceed only if:

```text
execution_head_includes_required_review_commit = TRUE
```

## Independent Audit Policy

Independent audit is for gate decisions, permission-state changes, and high-risk execution, not every routine documentation cleanup.

Independent audit is required when changing:

```text
NOT_AUTHORIZED -> AUTHORIZED
BLOCKED -> UNBLOCKED
NOT_PASSED -> PASSED
NOT_PROVEN -> PROVEN
NOT_READY -> READY
```

Independent audit is required when authorizing or executing:

```text
validation-only preflight rerun
sealed dataset recovery/regeneration
sealed dataset validation
PPO v2 training
model artifact creation
paper/live orders
model promotion
deployment/readiness/edge/profitability claims
```
<!-- V3.08_CURRENT_PROJECT_CONTEXT_ALIGNMENT_END -->
