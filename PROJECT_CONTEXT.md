# PROJECT_CONTEXT.md

Authoritative source-of-truth document for `racoope70/ppo-trading-pipeline`.

This file controls the current project state, active milestone, validation standards, blocked actions, and audit boundaries for the PPO trading pipeline.

Detailed v3.07 history is archived at:

`docs/archive/v3_07_validation_readiness_chain_summary.md`

---

## 1. Current Source-of-Truth Summary

```text
latest_completed_checkpoint = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review
latest_completed_commit = 3fb3974e66ddf279af640c79b10aa79df96db523
latest_completed_decision = FAIL_INDEPENDENT_FINAL_CONTRACT_RESOLUTION_REVIEW_REQUIRES_REMEDIATION
reviewed_contract_checkpoint = v3.08 Dataset Reconstruction Final Contract Resolution
reviewed_contract_commit = 71180efd5f5d2fdeae1d1cbb0f45742fc9bab6a2
reviewed_contract_decision = PASS_SUPERSEDING_DATASET_RECONSTRUCTION_CONTRACT_RESOLUTION_FOR_INDEPENDENT_REVIEW_ONLY
active_milestone = v3.08 Dataset Reconstruction Final Contract Resolution Review Remediation
next_checkpoint = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
current_workstream = PPO_V2_DATASET_RECONSTRUCTION_GOVERNANCE
current_phase = documentation-only remediation required before repeated independent review
```

The substantive reconstruction contract is complete at the documentation-governance level, but the independent review failed because the governance package was not fully deterministic and source-of-truth aligned.

The failed review identified four remediation items:

1. preserve `unresolved_conditional_technical_literals = NONE` in the final contract-resolution record;
2. preserve the canonical `calendar_version_status` field in the final contract-resolution record;
3. align this authoritative project context with the completed v3.08 chain;
4. align `docs/workflows/milestone_review_reference_map.md` with the completed v3.08 chain.

This update resolves items 3 and 4 only. Items 1 and 2 remain required in `docs/runs/v3.08_dataset_reconstruction_contract_resolution.md` before the repeated independent review.

---

## 2. Controlling Reconstruction Classification

```text
reconstruction_classification = SUPERSEDING_GOVERNED_ALPACA_ALIGNED_RECONSTRUCTION
original_dataset_recovered = FALSE
byte_identical_original_dataset_recovery = NOT_CLAIMED
byte_identical_recovery_claim = PROHIBITED
historical_equivalence_claim = NOT_PROVEN
new_dataset_identity_required = TRUE
```

The selected path is a new governed Alpaca-aligned reconstruction standard. It is not a recovery of the original missing v3.07 dataset and must not be described as byte-identical or historically equivalent.

---

## 3. Dataset Identity and Path State

```text
prospective_output_path = data/processed/ppo_v2/v3_08_superseding_alpaca_aligned_no_submit_training_input.parquet
old_missing_path = data/processed/ppo_v2/v3_07_no_submit_training_input.parquet
old_path_usage = HISTORICAL_MISSING_ARTIFACT_REFERENCE_ONLY
old_path_as_output_target = PROHIBITED
new_run_id_required = TRUE
new_manifest_required = TRUE
new_checksum_required = TRUE
```

The old v3.07 path remains relevant only as a historical reference to the missing sealed artifact. It is not the output target for any future governed reconstruction.

---

## 4. Current Contract Resolution Status

```text
nine_choices_governance_resolved = YES
conditional_technical_literal_values_resolved = YES
unresolved_conditional_technical_literals = NONE_IN_PREDECESSOR_RECORD
calendar_runtime_verified = NO
implementation_readiness = NOT_ESTABLISHED
current_source_contract_conformance = NOT_ESTABLISHED
current_tests_contract_conformance = NOT_ESTABLISHED
```

The nine technical choices are resolved for documentation-level contract review. Calendar runtime verification remains a separately governed hard gate. Current source code, tests, requirements, and runtime environment do not yet implement or verify the prospective contract.

The final contract-resolution record still requires exact remediation of these canonical fields:

```text
unresolved_conditional_technical_literals = NONE
calendar_version_status = GOVERNANCE_SELECTED_DEPENDENCY_PIN_PENDING_FUTURE_INSTALL_AND_RUNTIME_VERIFICATION
```

`exchange_calendars_status` may remain only as a documented alias after the canonical `calendar_version_status` field is restored.

---

## 5. Active Milestone

```text
active_milestone = v3.08 Dataset Reconstruction Final Contract Resolution Review Remediation
allowed_scope = DOCUMENTATION_ONLY
required_following_checkpoint = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
implementation_planning_authorization = NOT_YET_ALLOWED
```

The active milestone may only remediate the governance documents identified by the failed independent review and obtain green CI.

Only a passing repeated independent review may permit progression to:

```text
v3.08 Dataset Reconstruction Implementation Planning Authorization
```

That future checkpoint would authorize planning review only unless a separate decision explicitly changes another boundary.

---

## 6. Hard Non-Authorization Boundary

```text
NO_SUBMIT = DEFAULT
preflight_readiness = NOT_PASSED
sealed_dataset_validation = NOT_PROVEN
validation_only_preflight_rerun = NOT_AUTHORIZED
additional_validation_only_preflight_rerun = NOT_AUTHORIZED

code_implementation = NOT_AUTHORIZED
source_code_changes = NOT_AUTHORIZED
test_changes = NOT_AUTHORIZED
dependency_installation = NOT_AUTHORIZED
requirements_change = NOT_AUTHORIZED

market_data_access = NOT_AUTHORIZED
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

training = NOT_AUTHORIZED
ppo_v2_training_execution = NOT_AUTHORIZED
sealed_training_command_execution = NOT_AUTHORIZED
training_command_execution = NOT_AUTHORIZED
model_learn = NOT_AUTHORIZED
model_fitting = NOT_AUTHORIZED
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
deployment = NOT_AUTHORIZED
tagging = NOT_AUTHORIZED

trading_edge_claims = NOT_AUTHORIZED
profitability_claims = NOT_AUTHORIZED
deployment_readiness_claims = NOT_AUTHORIZED
legacy_ppo_retraining_decision = DO_NOT_RETRAIN_LEGACY_MODEL
```

These lines are controlling. Historical records, package manifests, scaffold records, audit records, and navigation maps do not override them.

---

## 7. Validation and Governance Hierarchy

```text
source_of_truth = PROJECT_CONTEXT.md
navigation_map = docs/workflows/milestone_review_reference_map.md
latest_final_contract_record = docs/runs/v3.08_dataset_reconstruction_contract_resolution.md
latest_independent_review = docs/audits/v3.08_independent_dataset_reconstruction_final_contract_resolution_review.md
historical_chain_archive = docs/archive/v3_07_validation_readiness_chain_summary.md
```

Current hierarchy:

1. `PROJECT_CONTEXT.md` controls current state and hard boundaries.
2. `docs/workflows/milestone_review_reference_map.md` provides navigation only.
3. The final contract-resolution record controls the prospective reconstruction contract, subject to the exact remediation required by the failed independent review.
4. The independent review controls whether progression is allowed.
5. Historical records remain evidence only and do not authorize current execution unless this file explicitly says so.

---

## 8. Required v3.08 Review Chain

The controlling v3.08 chain is:

1. `docs/runs/v3.08_dataset_reconstruction_executive_contract_decision.md`
2. `docs/runs/v3.08_dataset_reconstruction_exchange_calendar_version_selection.md`
3. `docs/runs/v3.08_dataset_reconstruction_contract_literal_binding_remediation.md`
4. `docs/runs/v3.08_dataset_reconstruction_conditional_technical_literal_verification.md`
5. `docs/runs/v3.08_dataset_reconstruction_contract_resolution.md`
6. `docs/audits/v3.08_independent_dataset_reconstruction_final_contract_resolution_review.md`

Supporting evidence includes:

- `docs/runs/v3.08_dataset_reconstruction_decision_evidence_index.md`
- `docs/runs/v3.08_dataset_reconstruction_codex_local_contract_decision_recommendation.md`
- `docs/research/v3.08_dataset_reconstruction_deep_research_external_contract_verification.md`
- `docs/audits/v3.08_dataset_reconstruction_independent_nine_choice_review.md`

---

## 9. Freshness and Independent Audit Guardrails

Before any authorized execution or repeated gate review from a local checkout:

```bash
git fetch origin
git status --short
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor <latest_required_authorization_or_review_commit> HEAD
echo $?
```

Proceed only if:

```text
working_tree = clean
HEAD = origin/main
merge_base_exit_code = 0
execution_head_includes_required_review_commit = TRUE
```

Independent audit is required for permission or gate changes including:

```text
NOT_AUTHORIZED -> AUTHORIZED
BLOCKED -> UNBLOCKED
NOT_PASSED -> PASSED
NOT_PROVEN -> PROVEN
NOT_READY -> READY
```

It is also required before authorizing or executing dataset recovery or reconstruction, dataset validation, validation-only reruns, PPO v2 training, model artifact creation, paper/live orders, model promotion, deployment, or readiness/edge/profitability claims.

---

## 10. Current Bottom Line

```text
current_bottom_line = documentation remediation remains incomplete until the final contract record restores the two canonical fields
next_allowed_checkpoint = v3.08 Dataset Reconstruction Final Contract Resolution Review Remediation
required_following_checkpoint = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
implementation_planning_authorization = NOT_YET_ALLOWED
```

The project is aligned to the completed v3.08 governance chain. The project remains blocked from implementation and all execution. The next work is documentation-only remediation of the final contract-resolution record, followed by green CI, fresh-head verification, and a repeated independent review.