# Future Validation and Training Reference Map

## Purpose

This file preserves future validation, training, final holdout, candidate-selection, and paper-trading reference guidance without bloating `PROJECT_CONTEXT.md`.

`PROJECT_CONTEXT.md` remains the current source of truth. `docs/workflows/milestone_review_reference_map.md` remains the broad navigation map. This file is a future reference guide only and does not authorize execution or replace a checkpoint-specific plan, run record, authorization, or independent review.

## Active-state source of truth

The current active checkpoint is always governed by `PROJECT_CONTEXT.md`.
This file should not be treated as the active-state source of truth.

Future validation, training, paper trading, universe expansion, and downstream execution remain separately governed and require their own authorization.

## General stop-and-review rule

Before any checkpoint moves from planning to execution, or from execution to acceptance, the model must read the relevant run, audit, review, and authorization records first.

If a required run, audit, review, or authorization record does not exist yet, treat it as a future prerequisite, not completed evidence. Do not invent a record path, decision, result, or authorization.

## Major stoppage points

1. **Before implementation authorization.** Confirm the controlling contract, implementation plan, prerequisite reviews, current source of truth, and exact allowed source/test scope.
2. **Before source/test implementation review.** Read the implementation authorization, implementation execution evidence, test evidence, and latest independent review before accepting the change.
3. **Before data-fetch authorization.** Confirm mocked contract tests, fail-closed network guards, request literals, credential boundaries, and the latest authorization state.
4. **Before dataset-generation execution.** Confirm separate data-fetch and dataset-generation authority, the governed dataset identity, the sealed contract, and the exact output boundary.
5. **Before accepting dataset-generation evidence.** Review execution records, provenance, manifest, checksum, gap evidence, schema evidence, and the latest independent dataset-evidence review.
6. **Before dataset validation.** Confirm the generated dataset has been accepted as the governed input and that a separate validation authorization exists.
7. **Before validation-only preflight.** Read dataset-validation evidence, split rules, embargo rules, VecNormalize rules, feature controls, and the preflight authorization record.
8. **Before training authorization.** Read accepted dataset-validation evidence, accepted preflight evidence, training configuration, split/embargo rules, VecNormalize controls, and no-submit guardrails.
9. **Before final holdout or candidate selection.** Confirm candidate and selection rules were frozen before holdout inspection and that the holdout remains untouched.
10. **Before paper-trading authorization.** Read final-holdout acceptance, candidate-selection evidence, model-artifact review, risk-control evidence, and the paper-order authorization record.
11. **Before deployment or live-order discussion.** Confirm paper-trading evidence, deployment-readiness review, explicit live-order authorization, and a preserved no-live-order default until that authorization exists.

## Future checkpoint reference sections

### 1. Source/Test Implementation

- **Purpose:** Implement only the source and test behavior allowed by a passed implementation-authorization checkpoint.
- **Read first:** `PROJECT_CONTEXT.md`, the milestone map, the dataset contract resolution, implementation plan, current implementation authorization, latest relevant independent audit, and existing source/test records.
- **Do not proceed unless:** Freshness and file scope are proven, the exact implementation checkpoint is authorized, and every change maps to the governed contract.
- **Still prohibited:** Data fetching, Alpaca API calls, dataset generation, validation, preflight, training, model artifacts, orders, deployment, and tagging unless separately authorized.

### 2. Mocked Unit and Contract Testing

- **Purpose:** Prove contract behavior, fail-closed guards, schema rules, calendar logic, request literals, and writer behavior without live network or output-producing execution.
- **Read first:** Current source/test implementation evidence, the implementation authorization, the contract resolution, the implementation plan, and the latest mocked-testing record.
- **Do not proceed unless:** Tests are isolated from live APIs and output-producing paths, required results are recorded, and failures are not hidden by mocks.
- **Still prohibited:** Live Alpaca clients, market-data access, dataset creation, validation, training, artifacts, orders, deployment, and tagging.

### 3. Data-Fetch Authorization

- **Purpose:** Decide whether a later, separately scoped data-fetch execution may access the governed historical source.
- **Read first:** `PROJECT_CONTEXT.md`, the milestone map, mocked unit/contract testing evidence, implementation authorization, dataset contract resolution, request-contract evidence, and the latest relevant independent review.
- **Do not proceed unless:** Request literals, universe, feed, adjustment, timeframe, timestamp, pagination, credential, no-submit, and fail-closed boundaries are fixed and reviewed.
- **Still prohibited:** Data fetching until execution is separately authorized, dataset generation, validation, preflight, training, artifacts, orders, deployment, and tagging.

### 4. Dataset Generation

- **Purpose:** Generate the governed dataset identity from separately authorized fetched data under the sealed reconstruction contract.
- **Read first:** Current data-fetch authorization and execution records, dataset-generation authorization, dataset contract resolution, implementation plan, runtime verification review, and applicable source/test evidence.
- **Do not proceed unless:** Both data-fetch and dataset-generation authority exist, the output path and universe are fixed, and manifest, checksum, provenance, gap, schema, and fail-closed requirements are defined.
- **Still prohibited:** Treating the output as validated, running preflight or training, creating model artifacts, submitting orders, deployment, and tagging.

### 5. Dataset Evidence Review

- **Purpose:** Decide whether dataset-generation evidence is complete, internally consistent, reproducible, and eligible for validation consideration.
- **Read first:** Dataset-generation authorization and execution records, manifest, checksum, provenance, gap report, schema evidence, run summary, and the latest independent dataset-evidence review or future record type.
- **Do not proceed unless:** Dataset identity, row coverage, timestamp rules, missing-slot policy, dtypes, sorting, duplication checks, and all evidence hashes agree.
- **Still prohibited:** Dataset validation until separately authorized, preflight, training, candidate selection, orders, deployment, and tagging.

### 6. Dataset Validation

- **Purpose:** Validate the accepted governed dataset against the sealed schema, quality, temporal, coverage, leakage, and reproducibility requirements.
- **Read first:** Dataset evidence acceptance, dataset-validation authorization, dataset contract resolution, validation plan, current dataset identity, and the latest relevant validation review or future record type.
- **Do not proceed unless:** The exact accepted dataset, manifest, checksum, and validation command are fixed before execution.
- **Still prohibited:** Training, model fitting, model-artifact creation, final candidate promotion, paper orders, live orders, deployment, and tagging.

### 7. Validation-Only Preflight

- **Purpose:** Prove the validated dataset and training configuration can enter the future training path without fitting a model or creating training artifacts.
- **Read first:** Accepted dataset-validation evidence, preflight authorization, training configuration, feature manifest, split definitions, embargo rules, VecNormalize rules, and the latest preflight review or future record type.
- **Do not proceed unless:** No fitting occurs, no final holdout is consumed, split boundaries are deterministic, and the preflight is explicitly validation-only.
- **Still prohibited:** PPO training, model selection, model artifacts, paper orders, live orders, deployment, and tagging.

### 8. Embargo + VecNormalize Validation Hardening

- **Purpose:** Prevent temporal and normalization leakage before training or model selection.
- **Read first:** `docs/workflows/ppo_validation_hardening.md`, the current split specification, feature/label lookback rules, training configuration, preflight evidence, and the latest relevant validation review.
- **Do not proceed unless:** Embargo separates train, evaluation, and holdout boundaries as required; VecNormalize statistics are fit on training data only; evaluation and holdout environments are locked from updating those statistics; and reward normalization is disabled where required.
- **Still prohibited:** Tuning on the final holdout or using final-holdout results to change features, hyperparameters, thresholds, the stock universe, or candidate-ranking rules.

Embargo reduces leakage across train, evaluation, and holdout periods. VecNormalize hardening prevents evaluation or holdout observations and rewards from changing training-fitted normalization statistics. These controls must be reviewed before training authorization and before model selection.

No tuning is allowed on the final holdout. Final-holdout results must not be used for candidate selection unless the selection rule and eligible candidate set were fixed before holdout inspection.

### 9. PPO Retraining

- **Purpose:** Fit PPO candidates only after the dataset, validation, preflight, embargo, VecNormalize, feature, risk, and artifact contracts have passed their own checkpoints.
- **Read first:** Training authorization, accepted dataset-validation and preflight evidence, `docs/workflows/alpaca_ppo_retraining_validation_plan.md`, training configuration, feature manifest, split/embargo specification, VecNormalize controls, and no-submit guardrails.
- **Do not proceed unless:** The exact dataset checksum, code commit, configuration, random-seed policy, artifact destinations, evaluation rules, and candidate-ranking rule are frozen and authorized.
- **Still prohibited:** Inspecting or tuning on the final holdout during training, paper-order submission, live orders, deployment, universe expansion, and tagging unless separately authorized.

### 10. Final Holdout / Untouched Test Period

- **Purpose:** Apply a final exam to frozen validation candidates after training and validation-based ranking are complete.
- **Read first:** Training execution and artifact review, `docs/workflows/alpaca_ppo_final_holdout_validation.md`, frozen candidate list, predeclared holdout window, fixed pass thresholds, and the final-holdout authorization/review future record types.
- **Do not proceed unless:** The holdout has not been used for feature selection, parameter tuning, manual iteration, candidate ranking, stock-universe changes, or prior performance inspection.
- **Still prohibited:** Repeatedly tuning against holdout results, changing the selection rule after inspection, paper orders, live orders, deployment, and tagging.

The final holdout is an untouched test period. It is not for feature selection, parameter tuning, manual iteration, model selection, or changing the stock universe. It is the final exam after candidate rules are already fixed.

### 11. Candidate Selection

- **Purpose:** Promote validation winners that also pass the final untouched holdout under a predeclared rule.
- **Read first:** Frozen validation ranking, final-holdout acceptance, `docs/workflows/alpaca_ppo_candidate_selection_redeployment.md`, model-artifact review, promotion-rule documentation, and the latest candidate-selection review or future record type.
- **Do not proceed unless:** Eligibility, tie-breaking, thresholds, promotion score, required artifacts, and one-candidate-per-symbol or other selection rules were documented before final-holdout inspection.
- **Still prohibited:** Revising the rule to rescue a failed candidate, paper orders without authorization, live orders, deployment, universe expansion, and tagging.

Candidate selection means validation winners that also pass final holdout testing. The candidate-selection rule must be documented and frozen before final-holdout inspection.

### 12. Paper-Trading Authorization

- **Purpose:** Decide whether a selected, reviewed candidate may enter a controlled paper-only execution checkpoint.
- **Read first:** Final-holdout acceptance, candidate-selection evidence, model-artifact review, `docs/workflows/alpaca_paper_trading_integration.md`, dry-run evidence, execution-plan review, risk controls, pre-trade checklist, deployment-readiness review, and the paper-trading authorization record or future record type.
- **Do not proceed unless:** A selected candidate and its exact artifacts are identified, paper-only broker enforcement is proven, no-submit/dry-run checks pass, the order boundary is explicit, and paper-order authorization is recorded.
- **Still prohibited:** Live orders, implicit submission, unattended expansion of scope, production deployment, universe expansion, and tagging unless separately authorized.

Paper trading requires a selected candidate, model-artifact review, final-holdout acceptance, paper-order authorization, a preserved no-live-order boundary, and deployment-readiness review. Paper authorization does not imply live-trading authorization.

### 13. Future Universe Expansion Research

- **Purpose:** Evaluate a larger research universe only after the governed six-symbol baseline path is functioning and accepted.
- **Read first:** `PROJECT_CONTEXT.md`, the milestone map, `docs/workflows/six_ticker_quality_baseline.md`, accepted baseline validation/holdout/paper evidence, a future universe-expansion research plan, and its future independent review and authorization record types.
- **Do not proceed unless:** Expansion is isolated as a new research checkpoint with a new contract, universe rationale, data-coverage review, selection-bias controls, compute plan, and untouched evaluation design.
- **Still prohibited:** Changing the current v3.08 six-symbol dataset contract, reusing the existing final holdout for a new universe, mixing expansion results into baseline acceptance, paper orders, live orders, deployment, and tagging.

Expansion from the governed six-symbol universe to a larger universe, such as 53 symbols, is future research. It must remain separate from the current v3.08 dataset contract and must not contaminate the baseline final holdout.

## Non-authorization boundary

This document does not authorize:

```text
source_code_changes
test_changes
requirements_change
dependency_installation
data_fetching
Alpaca_API_calls
dataset_generation
dataset_validation
preflight_execution
training
model_artifact_creation
paper_orders
live_orders
deployment
tagging
```
