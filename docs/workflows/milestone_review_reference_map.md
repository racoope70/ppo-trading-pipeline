# Milestone Review Reference Map

## Source-of-Truth Note

`PROJECT_CONTEXT.md` controls the current project state, active milestone, latest checkpoint, authorization boundaries, blocked actions, and PPO v2 roadmap.

This file does not authorize work. `PROJECT_CONTEXT.md` remains the controlling source of truth.

---

## Main PPO v2 Phase Map

### v1.60-v1.65 — Legacy PPO Audit and Governance Reset

**Use when reviewing**

* legacy PPO status
* legacy PPO promotion questions
* model-quality audit history
* promotion standards
* why the project moved from legacy PPO to PPO v2

**Review first**

```txt
docs/runs/v1.63_ppo_baseline_model_quality_audit_report.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/decisions/v1.65_legacy_ppo_final_audit_decision.md
```

Review v1.60-v1.62 artifact and scope docs if deeper audit context is needed.

**Then move to**

v1.66-v1.72 if the task involves PPO v2 design, retraining governance, or data-contract planning.

---

### v1.66-v1.72 — PPO v2 Retraining Governance and Data-Contract Design

**Use when reviewing**

* PPO v2 retraining design
* retraining authorization boundaries
* scaffold safety
* data-contract design
* train / embargo / eval / holdout split rules
* pre-training governance

**Review first**

```txt
docs/designs/v1.66_ppo_v2_retraining_design.md
docs/decisions/v1.67_ppo_v2_retraining_authorization_review.md
docs/audits/v1.71_ppo_v2_scaffold_safety_audit_and_execution_boundary_review.md
docs/specifications/v1.72_ppo_v2_controlled_retraining_data_contract_and_split_specification.md
```

Review v1.68-v1.70 implementation planning/scaffold docs if the task involves scaffold behavior.

**Then move to**

v1.73-v1.74 if the task involves validating the PPO v2 data contract.

---

### v1.73-v1.74 — PPO v2 Data-Contract Validation Layer

**Use when reviewing**

* data-contract tests
* schema validation
* split-boundary validation
* leakage checks
* holdout / embargo enforcement
* non-executing validation utilities

**Review first**

```txt
docs/runs/v1.73_ppo_v2_data_contract_validation_tests.md
docs/reviews/v1.74_ppo_v2_data_contract_validation_review_next_implementation_boundary.md
docs/specifications/v1.72_ppo_v2_controlled_retraining_data_contract_and_split_specification.md
```

**Then move to**

v1.75-v1.77 if the task involves the PPO v2 data-preparation interface.

---

### v1.75-v1.77 — PPO v2 Data-Preparation Interface

**Use when reviewing**

* data-preparation interface design
* in-memory PPO v2 data structures
* train / eval / holdout preparation boundaries
* interface scaffold and tests

**Review first**

```txt
docs/plans/v1.75_ppo_v2_controlled_data_preparation_interface_boundary_plan.md
docs/runs/v1.76_ppo_v2_controlled_data_preparation_interface_scaffold_and_tests.md
docs/reviews/v1.77_ppo_v2_data_preparation_interface_scaffold_review_next_boundary_decision.md
```

**Then move to**

v1.78-v1.80 if the task involves connecting data-contract validation outputs to data-preparation interface inputs.

---

### v1.78-v1.80 — PPO v2 Data-Preparation Integration

**Use when reviewing**

* data-contract to data-preparation integration
* in-memory integration scaffold
* integration tests
* data-preparation integration boundary review

**Review first**

```txt
docs/plans/v1.78_ppo_v2_data_preparation_interface_integration_boundary_plan.md
docs/runs/v1.79_ppo_v2_data_preparation_interface_integration_scaffold_and_tests.md
docs/reviews/v1.80_ppo_v2_data_preparation_integration_scaffold_review_next_boundary_decision.md
```

**Then move to**

v1.81-v1.83 if the task involves PPO v2 training-input handoff.

---

### v1.81-v1.83 — PPO v2 Training Input Handoff

**Use when reviewing**

* training-input handoff planning
* prepared-data handoff boundaries
* future training-input interface design
* handoff scaffold and review

**Review first**

```txt
PROJECT_CONTEXT.md
docs/reviews/v1.80_ppo_v2_data_preparation_integration_scaffold_review_next_boundary_decision.md
```

Review these when created:

```txt
docs/plans/v1.81_ppo_v2_training_input_handoff_boundary_plan.md
docs/runs/v1.81_ppo_v2_training_input_handoff_boundary_plan.md
docs/runs/v1.82_ppo_v2_training_input_handoff_interface_scaffold_and_tests.md
docs/reviews/v1.83_ppo_v2_training_input_handoff_review_next_boundary_decision.md
```

**Then move to**

v1.84-v1.86 if the task involves PPO v2 training configuration.

---

### v1.84-v1.86 — PPO v2 Training Configuration

**Use when reviewing**

* PPO v2 training configuration
* hyperparameter governance
* artifact isolation design
* validation configuration
* execution-readiness boundaries

**Review first**

```txt
PROJECT_CONTEXT.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/designs/v1.66_ppo_v2_retraining_design.md
docs/specifications/v1.72_ppo_v2_controlled_retraining_data_contract_and_split_specification.md
```

Review these when created:

```txt
docs/plans/v1.84_ppo_v2_training_configuration_boundary_plan.md
docs/runs/v1.85_ppo_v2_training_configuration_scaffold_and_tests.md
docs/reviews/v1.86_ppo_v2_training_configuration_review_execution_readiness_boundary.md
```

**Then move to**

v1.87-v1.90 if the task involves controlled PPO v2 training execution authorization planning, dry-run readiness, or non-executing scaffold review.

---

### v1.87-v1.90 - Controlled Training Execution Dry-Run and Scaffold Readiness

**Use when reviewing**

* controlled training execution authorization planning
* dry-run scaffold readiness
* non-executing scaffold behavior
* whether training execution remains blocked
* whether artifact creation, promotion, broker integration, submit, and hybrid paths remain disabled

**Review first**

```txt
PROJECT_CONTEXT.md
docs/plans/v1.87_ppo_v2_controlled_training_execution_authorization_plan.md
docs/plans/v1.88_ppo_v2_controlled_training_execution_scaffold_dry_run_plan.md
docs/runs/v1.89_ppo_v2_controlled_training_execution_dry_run_scaffold_and_tests.md
docs/reviews/v1.90_ppo_v2_controlled_training_execution_dry_run_review_next_boundary_decision.md
```

**Then move to**

v1.91-v1.94 if the task involves controlled training execution implementation scaffolding or authorization planning.

---

### v1.91-v1.94 - Controlled Training Execution Implementation and Authorization Planning

**Use when reviewing**

* controlled execution implementation scaffold
* execution boundary decisions
* future training execution authorization planning
* preconditions before any one-time controlled execution checkpoint can be considered
* quarantine, audit-package, model-quality, and hybrid-gate restrictions

**Review first**

```txt
PROJECT_CONTEXT.md
docs/plans/v1.91_ppo_v2_controlled_training_execution_implementation_plan.md
docs/runs/v1.92_ppo_v2_controlled_training_execution_implementation_scaffold_and_tests.md
docs/reviews/v1.93_ppo_v2_controlled_training_execution_scaffold_review_execution_boundary_decision.md
docs/plans/v1.94_ppo_v2_controlled_training_execution_authorization_plan.md
```

**Then move to**

v1.95-v1.97 if the task involves authorization review, checkpoint design planning, or design review.

---

### v1.95-v1.97 - Controlled Training Execution Checkpoint Design Review

**Use when reviewing**

* controlled training execution authorization review
* controlled execution checkpoint design requirements
* single-command specification requirements
* runtime capture, quarantine paths, artifact inventory, checksums, and fail-closed behavior
* whether the project may move to one-time controlled execution checkpoint planning

**Review first**

```txt
PROJECT_CONTEXT.md
docs/reviews/v1.95_ppo_v2_controlled_training_execution_authorization_review.md
docs/plans/v1.96_ppo_v2_controlled_training_execution_checkpoint_design_plan.md
docs/reviews/v1.97_ppo_v2_controlled_training_execution_checkpoint_design_review.md
```

**Then move to**

v1.98+ if the task involves planning a one-time controlled PPO v2 training execution checkpoint.

---

### v1.98+ - One-Time Controlled Training Execution Checkpoint Planning

**Use when reviewing**

* one-time controlled PPO v2 training execution checkpoint planning
* whether a future checkpoint may define an execution command
* source-of-truth, runtime capture, quarantine, artifact inventory, checksum, and post-training audit requirements
* preventing planning from being mistaken for permission to train

**Review first**

```txt
PROJECT_CONTEXT.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/specifications/v1.72_ppo_v2_controlled_retraining_data_contract_and_split_specification.md
docs/plans/v1.94_ppo_v2_controlled_training_execution_authorization_plan.md
docs/reviews/v1.95_ppo_v2_controlled_training_execution_authorization_review.md
docs/plans/v1.96_ppo_v2_controlled_training_execution_checkpoint_design_plan.md
docs/reviews/v1.97_ppo_v2_controlled_training_execution_checkpoint_design_review.md
```

**Then move to**

Stop unless the task is explicitly a v1.98 planning checkpoint. v1.98 planning does not automatically authorize PPO training. Actual PPO training execution remains blocked unless a later sealed checkpoint explicitly authorizes one-time controlled execution.

NO-SUBMIT remains default. Paper orders, live orders, controlled submit, PPO + Random Forest, and PPO + XGBoost remain blocked.

---

## Older Paper-Trading / Safety History: v0.3-v1.59

Review v0.3-v1.59 only when the task involves:

* paper-trading safety
* broker-order mechanics
* submit-mode preflight
* stale-plan prevention
* candidate stability
* multi-order handling
* reporting dashboards
* historical no-submit observation evidence

### Condensed range guide

```txt
v0.3-v1.0    early safety chain, research hardening, six-ticker retrain, temporal validation
v1.3-v1.9    early Alpaca observation, holdout validation, candidate selection, no-submit redeployment
v1.10-v1.22  controlled paper-order tests, preflight, post-submit monitoring
v1.23-v1.33  rebalance policy, candidate persistence, multi-order policy, decision-state governance
v1.34-v1.44  reporting-chain implementation and artifact governance
v1.45-v1.59  PPO no-submit observation and candidate recurrence history
```

Do not use v0.3-v1.59 evidence to override the v1.60-v1.65 legacy PPO audit conclusions.

For model promotion, retraining, PPO v2, hybrid deployment, or trading-edge claims, start with v1.60-v1.65 as the controlling governance reset.

---

## Special Review Paths

### Paper-Trading Safety

**Review first**

```txt
PROJECT_CONTEXT.md
docs/workflows/paper_trading_session_policy.md
docs/workflows/single_order_submit_guard.md
docs/workflows/submit_mode_preflight.md
docs/workflows/stale_plan_prevention.md
docs/workflows/signal_persistence_candidate_stability_policy.md
docs/workflows/multi_order_candidate_handling_policy.md
docs/workflows/paper_trading_decision_state_machine.md
docs/workflows/paper_trading_operational_reporting_runbook.md
docs/workflows/paper_trading_reporting_artifact_retention_policy.md
docs/workflows/ppo_paper_trading_observation_protocol.md
```

**Relevant milestone ranges**

```txt
v1.10-v1.22
v1.23-v1.33
v1.34-v1.44
v1.45-v1.59
```

---

### Legacy PPO Promotion

**Review first**

```txt
docs/runs/v1.63_ppo_baseline_model_quality_audit_report.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/decisions/v1.65_legacy_ppo_final_audit_decision.md
```

**Relevant milestone range**

```txt
v1.60-v1.65
```

---

### PPO v2 Training Execution

**Review first**

```txt
PROJECT_CONTEXT.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/specifications/v1.72_ppo_v2_controlled_retraining_data_contract_and_split_specification.md
docs/plans/v1.94_ppo_v2_controlled_training_execution_authorization_plan.md
docs/reviews/v1.95_ppo_v2_controlled_training_execution_authorization_review.md
docs/plans/v1.96_ppo_v2_controlled_training_execution_checkpoint_design_plan.md
docs/reviews/v1.97_ppo_v2_controlled_training_execution_checkpoint_design_review.md
```

**Relevant milestone ranges**

```txt
v1.60—v1.65  legacy PPO audit and governance reset
v1.66—v1.86  PPO v2 design, data-contract, validation, handoff, and training-configuration controls
v1.87—v1.97  controlled execution authorization, scaffold, checkpoint design, and design-review controls
v1.98+       one-time controlled training execution checkpoint planning
```

v1.98 planning does not automatically authorize PPO training.

Actual PPO training execution remains blocked unless a later sealed checkpoint explicitly authorizes one-time controlled execution.

NO-SUBMIT remains default.

Paper orders, live orders, controlled submit, PPO + RF, and PPO + XGBoost remain blocked.

---

### PPO + Random Forest / PPO + XGBoost

**Review first**

```txt
PROJECT_CONTEXT.md
docs/decisions/v1.65_legacy_ppo_final_audit_decision.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/specifications/v1.72_ppo_v2_controlled_retraining_data_contract_and_split_specification.md
docs/reviews/v1.95_ppo_v2_controlled_training_execution_authorization_review.md
docs/plans/v1.96_ppo_v2_controlled_training_execution_checkpoint_design_plan.md
docs/reviews/v1.97_ppo_v2_controlled_training_execution_checkpoint_design_review.md
future PPO-only baseline performance package
future PPO + Random Forest readiness review
future PPO + XGBoost comparison review
```

**Relevant milestone ranges**

```txt
v1.60-v1.65  legacy PPO audit and governance reset
v1.66-v1.86  PPO v2 design, data-contract, validation, handoff, and training-configuration controls
v1.87-v1.97  controlled execution authorization, scaffold, checkpoint design, and design-review controls
v1.98+       one-time controlled training execution checkpoint planning
future standalone PPO v2 validation and baseline performance package
future hybrid-gate readiness documents
```

v1.98 planning does not automatically authorize PPO training.

Actual PPO training execution remains blocked unless a later sealed checkpoint explicitly authorizes one-time controlled execution.

NO-SUBMIT remains default.

Paper orders, live orders, controlled submit, PPO + RF, and PPO + XGBoost remain blocked.

Do not unblock hybrid work from the legacy PPO or from v1.98 planning. Hybrid work requires a validated standalone PPO v2 baseline and a separate sealed hybrid authorization first.

---

### Feature Importance / Interpretability

**Review first**

```txt
PROJECT_CONTEXT.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/decisions/v1.65_legacy_ppo_final_audit_decision.md
future PPO-only baseline performance package
future PPO + RF / PPO + XGBoost validation documents
```

**Key caution**

Feature importance can explain model behavior after validation, but it must not be used to prove profitability, generalization, promotion readiness, or deployment readiness.
