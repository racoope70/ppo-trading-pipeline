# Milestone Review Reference Map

This file is a navigation map only. `PROJECT_CONTEXT.md` controls the current project state, active milestone, authorization boundaries, and roadmap.

Detailed v3.07 history is archived at:

`docs/archive/v3_07_validation_readiness_chain_summary.md`

---

## 1. Current Controlling State

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
implementation_planning_authorization = NOT_YET_ALLOWED
```

The independent review failed because the package still requires deterministic documentation remediation. The substantive nine-choice contract remains resolved at the governance level, with calendar runtime verification deferred as a future hard gate.

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

The old v3.07 path is not the current output target and must not be treated as an active reconstruction destination.

---

## 3. Active Review Path

### v3.08 Dataset Reconstruction Final Contract Resolution Review Remediation

Allowed scope:

```text
documentation_only = YES
source_code_changes = NOT_AUTHORIZED
test_changes = NOT_AUTHORIZED
requirements_change = NOT_AUTHORIZED
dependency_installation = NOT_AUTHORIZED
data_or_execution = NOT_AUTHORIZED
```

Required remediation sequence:

1. Add the canonical conditional-literal closure field to `docs/runs/v3.08_dataset_reconstruction_contract_resolution.md`:

   ```text
   unresolved_conditional_technical_literals = NONE
   ```

2. Add the canonical calendar-status field to the same record:

   ```text
   calendar_version_status = GOVERNANCE_SELECTED_DEPENDENCY_PIN_PENDING_FUTURE_INSTALL_AND_RUNTIME_VERIFICATION
   ```

3. Preserve `exchange_calendars_status` only as a documented alias if retained.
4. Keep `PROJECT_CONTEXT.md` and this map aligned to the completed v3.08 chain.
5. Commit documentation only and obtain green CI.
6. Verify a clean, fresh local execution head.
7. Repeat the independent final contract-resolution review.

Only a passing repeated independent review may permit progression to:

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

### Controlling decision and resolution records

1. `docs/runs/v3.08_dataset_reconstruction_executive_contract_decision.md`
2. `docs/runs/v3.08_dataset_reconstruction_exchange_calendar_version_selection.md`
3. `docs/runs/v3.08_dataset_reconstruction_contract_literal_binding_remediation.md`
4. `docs/runs/v3.08_dataset_reconstruction_conditional_technical_literal_verification.md`
5. `docs/runs/v3.08_dataset_reconstruction_contract_resolution.md`
6. `docs/audits/v3.08_independent_dataset_reconstruction_final_contract_resolution_review.md`

### Supporting evidence

- `docs/runs/v3.08_dataset_reconstruction_decision_evidence_index.md`
- `docs/runs/v3.08_dataset_reconstruction_codex_local_contract_decision_recommendation.md`
- `docs/research/v3.08_dataset_reconstruction_deep_research_external_contract_verification.md`
- `docs/audits/v3.08_dataset_reconstruction_independent_nine_choice_review.md`
- `docs/runs/v3.08_dataset_reconstruction_documentation_package_remediation.md`
- `docs/runs/v3.08_exact_feature_formula_and_raw_source_specification.md`
- `docs/runs/v3.08_feature_formula_raw_source_specification_review.md`
- `docs/runs/v3.08_exact_dataset_recipe_reconstruction_plan.md`

Earlier v3.08 diagnostics, recovery-strategy, artifact-lineage, and trusted-source records remain historical inputs. They are not the active checkpoint and do not override the completed executive decision or final contract-resolution chain.

---

## 6. Contract Resolution Snapshot

```text
nine_choices_governance_resolved = YES
conditional_technical_literal_values_resolved = YES
calendar_runtime_verified = NO
implementation_readiness = NOT_ESTABLISHED
current_source_contract_conformance = NOT_ESTABLISHED
current_tests_contract_conformance = NOT_ESTABLISHED
```

Resolved governance choices cover:

1. Alpaca historical source/interface, `TimeFrame.Hour`, `DataFeed.IEX`, and `Sort.ASC`.
2. `Adjustment.RAW`.
3. Fixed warm-up request start and at least 50 observed pre-contract bars per symbol.
4. `exchange-calendars==4.13.2` with `XNYS`, pending separately authorized runtime verification.
5. UTC-aware request, provider, calendar-comparison, and serialization semantics.
6. Open timestamps and whole-interval session containment.
7. Zero missing-slot tolerance with no synthesis, filling, interpolation, or duplicate acceptance.
8. PyArrow 24.0.0 with no automatic engine or fastparquet fallback.
9. Fixed 27-column Arrow schema and explicit Parquet writer profile.

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

---

## 9. Independent Audit Policy

Independent audit is required for changes such as:

```text
NOT_AUTHORIZED -> AUTHORIZED
BLOCKED -> UNBLOCKED
NOT_PASSED -> PASSED
NOT_PROVEN -> PROVEN
NOT_READY -> READY
```

It is also required before authorizing or executing dataset recovery or reconstruction, dataset validation, validation-only preflight reruns, PPO v2 training, model artifact creation, paper/live orders, model promotion, deployment, or readiness/edge/profitability claims.

---

## 10. Current Bottom Line

```text
current_bottom_line = final contract record requires two canonical-field remediations before repeated independent review
active_milestone = v3.08 Dataset Reconstruction Final Contract Resolution Review Remediation
next_checkpoint = v3.08 Independent Dataset Reconstruction Final Contract Resolution Review — Repeat After Remediation
implementation_planning_authorization = NOT_YET_ALLOWED
```

Use `PROJECT_CONTEXT.md` for the controlling current state. Use this file to navigate the required review chain. Do not use obsolete artifact-lineage or v3.07 preflight checkpoints as the active roadmap.