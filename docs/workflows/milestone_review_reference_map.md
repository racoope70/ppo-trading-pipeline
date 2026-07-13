# Milestone Review Reference Map

This file is a navigation map only. `PROJECT_CONTEXT.md` controls the current project state, active milestone, authorization boundaries, and roadmap.

Detailed v3.07 history is archived at `docs/archive/v3_07_validation_readiness_chain_summary.md`.

---

## 1. Current Controlling State

```text
latest_completed_governance_review = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review
latest_completed_review_commit = 3fb3974e66ddf279af640c79b10aa79df96db523
latest_completed_review_decision = FAIL_INDEPENDENT_FINAL_CONTRACT_RESOLUTION_REVIEW_REQUIRES_REMEDIATION
reviewed_contract_checkpoint = v3.08 Dataset Reconstruction Final Contract Resolution
reviewed_contract_commit = 71180efd5f5d2fdeae1d1cbb0f45742fc9bab6a2
contract_literal_remediation_commit = c484781c96e00809363d206202827ae0b9ab2b54
audit_remediation_items_completed = YES
recorded_audit_decision_superseded = NO
active_milestone = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
next_checkpoint = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
current_workstream = PPO_V2_DATASET_RECONSTRUCTION_GOVERNANCE
implementation_planning_authorization = NOT_YET_ALLOWED
```

The four documentation discrepancies identified by the failed review have been corrected. The existing `FAIL` decision remains controlling until a repeated independent review records a new decision.

---

## 2. Current Dataset Identity

```text
reconstruction_classification = SUPERSEDING_GOVERNED_ALPACA_ALIGNED_RECONSTRUCTION
new_dataset_identity_required = TRUE
prospective_output_path = data/processed/ppo_v2/v3_08_superseding_alpaca_aligned_no_submit_training_input.parquet
old_missing_path = data/processed/ppo_v2/v3_07_no_submit_training_input.parquet
old_path_usage = HISTORICAL_MISSING_ARTIFACT_REFERENCE_ONLY
old_path_as_output_target = PROHIBITED
original_dataset_recovered = FALSE
byte_identical_recovery_claim = PROHIBITED
historical_equivalence_claim = NOT_PROVEN
```

---

## 3. Remediation Status and Active Review Path

Completed documentation remediation:

```text
project_context_alignment = COMPLETE
milestone_map_alignment = COMPLETE
unresolved_conditional_technical_literals = NONE
calendar_version_status = GOVERNANCE_SELECTED_DEPENDENCY_PIN_PENDING_FUTURE_INSTALL_AND_RUNTIME_VERIFICATION
exchange_calendars_status_alias_retained = YES
audit_remediation_items_completed = YES
```

The next checkpoint is:

```text
v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
```

The repeated review is an independent documentation and governance review. It does not authorize source changes, dependencies, requirements changes, data access, dataset creation, validation, training, artifacts, orders, deployment, or tagging.

Only a passing repeated independent review may permit consideration of:

```text
v3.08 Dataset Reconstruction Implementation Planning Authorization
```

---

## 4. Files to Review First

1. `PROJECT_CONTEXT.md`
2. `docs/workflows/milestone_review_reference_map.md`
3. `docs/runs/v3.08_dataset_reconstruction_contract_resolution.md`
4. `docs/audits/v3.08_independent_dataset_reconstruction_final_contract_resolution_review.md`
5. `docs/runs/v3.08_dataset_reconstruction_conditional_technical_literal_verification.md`
6. `docs/runs/v3.08_dataset_reconstruction_exchange_calendar_version_selection.md`

---

## 5. Required v3.08 Contract Chain

1. `docs/runs/v3.08_dataset_reconstruction_executive_contract_decision.md`
2. `docs/runs/v3.08_dataset_reconstruction_exchange_calendar_version_selection.md`
3. `docs/runs/v3.08_dataset_reconstruction_contract_literal_binding_remediation.md`
4. `docs/runs/v3.08_dataset_reconstruction_conditional_technical_literal_verification.md`
5. `docs/runs/v3.08_dataset_reconstruction_contract_resolution.md`
6. `docs/audits/v3.08_independent_dataset_reconstruction_final_contract_resolution_review.md`
7. repeated independent review after remediation

Supporting evidence:

- `docs/runs/v3.08_dataset_reconstruction_decision_evidence_index.md`
- `docs/runs/v3.08_dataset_reconstruction_codex_local_contract_decision_recommendation.md`
- `docs/research/v3.08_dataset_reconstruction_deep_research_external_contract_verification.md`
- `docs/audits/v3.08_dataset_reconstruction_independent_nine_choice_review.md`

Earlier diagnostics, recovery-strategy, artifact-lineage, and trusted-source records remain historical inputs. They are not the active checkpoint.

---

## 6. Contract Resolution Snapshot

```text
nine_choices_governance_resolved = YES
conditional_technical_literal_values_resolved = YES
unresolved_conditional_technical_literals = NONE
calendar_version_status = GOVERNANCE_SELECTED_DEPENDENCY_PIN_PENDING_FUTURE_INSTALL_AND_RUNTIME_VERIFICATION
calendar_runtime_verified = NO
implementation_readiness = NOT_ESTABLISHED
current_source_contract_conformance = NOT_ESTABLISHED
current_tests_contract_conformance = NOT_ESTABLISHED
```

Calendar runtime verification remains a separately authorized future hard gate.

---

## 7. Hard Non-Authorization Guardrail

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
model_learn = NOT_AUTHORIZED
model_fitting = NOT_AUTHORIZED
model_artifact_creation = NOT_AUTHORIZED
quarantine_model_output_creation = NOT_AUTHORIZED
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
ppo_rf = BLOCKED
ppo_xgboost = BLOCKED
model_promotion = NOT_AUTHORIZED
production_deployment = NOT_AUTHORIZED
tagging = NOT_AUTHORIZED
trading_edge_claims = NOT_AUTHORIZED
profitability_claims = NOT_AUTHORIZED
deployment_readiness_claims = NOT_AUTHORIZED
```

This map does not authorize any listed activity.

---

## 8. Freshness Guardrail

Before the repeated review from a local checkout:

```bash
git fetch origin
git status --short
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor <latest_documentation_remediation_commit> HEAD
echo $?
```

Proceed only if the working tree is clean, `HEAD` equals `origin/main`, and the merge-base exit code is `0`.

---

## 9. Current Bottom Line

```text
audit_remediation_items_completed = YES
repeated_independent_review = PENDING
recorded_audit_decision = FAIL_INDEPENDENT_FINAL_CONTRACT_RESOLUTION_REVIEW_REQUIRES_REMEDIATION
recorded_audit_decision_superseded = NO
active_milestone = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
implementation_planning_authorization = NOT_YET_ALLOWED
```

Use `PROJECT_CONTEXT.md` for controlling state. The next action is the repeated independent review, not implementation planning or execution.