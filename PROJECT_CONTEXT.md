# PROJECT_CONTEXT.md

Authoritative source of truth for `racoope70/ppo-trading-pipeline`.

Detailed v3.07 history is archived at `docs/archive/v3_07_validation_readiness_chain_summary.md`.

---

## 1. Current Source-of-Truth Summary

```text
latest_completed_governance_review = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review
latest_completed_review_commit = 3fb3974e66ddf279af640c79b10aa79df96db523
latest_completed_review_decision = FAIL_INDEPENDENT_FINAL_CONTRACT_RESOLUTION_REVIEW_REQUIRES_REMEDIATION
reviewed_contract_checkpoint = v3.08 Dataset Reconstruction Final Contract Resolution
reviewed_contract_commit = 71180efd5f5d2fdeae1d1cbb0f45742fc9bab6a2
reviewed_contract_decision = PASS_SUPERSEDING_DATASET_RECONSTRUCTION_CONTRACT_RESOLUTION_FOR_INDEPENDENT_REVIEW_ONLY
contract_literal_remediation_commit = c484781c96e00809363d206202827ae0b9ab2b54
audit_remediation_items_completed = YES
recorded_audit_decision_superseded = NO
active_milestone = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
next_checkpoint = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
current_workstream = PPO_V2_DATASET_RECONSTRUCTION_GOVERNANCE
current_phase = documentation remediation completed; repeated independent review pending
implementation_planning_authorization = NOT_YET_ALLOWED
```

All four remediation findings from the failed independent review have been addressed in the repository documents. This does not change or supersede the recorded `FAIL` decision. A repeated independent review is still required before any later checkpoint may be considered.

---

## 2. Reconstruction Classification

```text
reconstruction_classification = SUPERSEDING_GOVERNED_ALPACA_ALIGNED_RECONSTRUCTION
original_dataset_recovered = FALSE
byte_identical_original_dataset_recovery = NOT_CLAIMED
byte_identical_recovery_claim = PROHIBITED
historical_equivalence_claim = NOT_PROVEN
new_dataset_identity_required = TRUE
```

The selected path is a new governed Alpaca-aligned reconstruction standard. It is not recovery of the original missing v3.07 dataset.

---

## 3. Dataset Identity and Paths

```text
prospective_output_path = data/processed/ppo_v2/v3_08_superseding_alpaca_aligned_no_submit_training_input.parquet
old_missing_path = data/processed/ppo_v2/v3_07_no_submit_training_input.parquet
old_path_usage = HISTORICAL_MISSING_ARTIFACT_REFERENCE_ONLY
old_path_as_output_target = PROHIBITED
new_run_id_required = TRUE
new_manifest_required = TRUE
new_checksum_required = TRUE
```

---

## 4. Contract Resolution Status

```text
nine_choices_governance_resolved = YES
conditional_technical_literal_values_resolved = YES
unresolved_conditional_technical_literals = NONE
calendar_version_status = GOVERNANCE_SELECTED_DEPENDENCY_PIN_PENDING_FUTURE_INSTALL_AND_RUNTIME_VERIFICATION
exchange_calendars_status = GOVERNANCE_SELECTED_DEPENDENCY_PIN_PENDING_FUTURE_INSTALL_AND_RUNTIME_VERIFICATION
calendar_runtime_verified = NO
implementation_readiness = NOT_ESTABLISHED
current_source_contract_conformance = NOT_ESTABLISHED
current_tests_contract_conformance = NOT_ESTABLISHED
```

The canonical conditional-literal closure and calendar-version fields are present in `docs/runs/v3.08_dataset_reconstruction_contract_resolution.md`. Calendar runtime verification remains a separately governed hard gate.

---

## 5. Active Review Path

```text
active_milestone = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
allowed_scope = INDEPENDENT_DOCUMENTATION_AND_GOVERNANCE_REVIEW_ONLY
implementation_planning_authorization = NOT_YET_ALLOWED
```

The repeated review must evaluate the remediated package. Only a passing repeated independent review may permit consideration of `v3.08 Dataset Reconstruction Implementation Planning Authorization`. That later checkpoint would authorize planning review only unless another explicit decision changed a boundary.

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

These lines control current authorization state. Historical records, audit records, package manifests, and navigation maps do not override them.

---

## 7. Governance Hierarchy and Review Chain

```text
source_of_truth = PROJECT_CONTEXT.md
navigation_map = docs/workflows/milestone_review_reference_map.md
final_contract_record = docs/runs/v3.08_dataset_reconstruction_contract_resolution.md
independent_review_record = docs/audits/v3.08_independent_dataset_reconstruction_final_contract_resolution_review.md
historical_chain_archive = docs/archive/v3_07_validation_readiness_chain_summary.md
```

Required v3.08 chain:

1. `docs/runs/v3.08_dataset_reconstruction_executive_contract_decision.md`
2. `docs/runs/v3.08_dataset_reconstruction_exchange_calendar_version_selection.md`
3. `docs/runs/v3.08_dataset_reconstruction_contract_literal_binding_remediation.md`
4. `docs/runs/v3.08_dataset_reconstruction_conditional_technical_literal_verification.md`
5. `docs/runs/v3.08_dataset_reconstruction_contract_resolution.md`
6. `docs/audits/v3.08_independent_dataset_reconstruction_final_contract_resolution_review.md`
7. repeated independent review after remediation

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

Proceed only when the working tree is clean, `HEAD` equals `origin/main`, and the merge-base exit code is `0`.

---

## 9. Current Bottom Line

```text
audit_remediation_items_completed = YES
repeated_independent_review = PENDING
recorded_audit_decision = FAIL_INDEPENDENT_FINAL_CONTRACT_RESOLUTION_REVIEW_REQUIRES_REMEDIATION
recorded_audit_decision_superseded = NO
next_allowed_checkpoint = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
implementation_planning_authorization = NOT_YET_ALLOWED
```

The documentation discrepancies are corrected. The project remains blocked from implementation and execution. The next action is the repeated independent review, not implementation planning.