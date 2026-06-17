# PROJECT_CONTEXT.md

Authoritative reference document for `racoope70/ppo-trading-pipeline`.

This document defines the current system architecture, validation standards, deployment constraints, research progression, operational guardrails, and active development state for the PPO trading pipeline.

It should be reviewed before modifying training logic, validation methodology, deployment workflows, artifact management, or broker integration behavior.

---

# 1. Current Development State

## Active Operational Milestone

`v1.67 PPO v2 Retraining Authorization Review`

## Status

READY FOR PPO V2 RETRAINING AUTHORIZATION REVIEW

## Latest Completed Paper-Trading Milestone

`v1.66 PPO v2 Retraining Design`

Latest sealed checkpoint:

```txt
v1.66-ppo-v2-retraining-design
latest sealed commit = 94f2a8c
tests = 227 passed, 2 warnings
```

Current documented local test status:

```txt
227 passed, 2 warnings
```

Known non-blocking warnings from the latest local test run:

* websockets.legacy deprecation warning
* protobuf utcfromtimestamp deprecation warning

## Current Paper-Trading Source of Truth

Before making any paper-trading recommendation, review these files first:

```txt
docs/workflows/signal_persistence_candidate_stability_policy.md
docs/workflows/multi_order_candidate_handling_policy.md
docs/workflows/paper_trading_decision_state_machine.md
docs/workflows/paper_trading_session_policy.md
docs/workflows/paper_trading_operational_reporting_runbook.md
docs/workflows/paper_trading_reporting_artifact_retention_policy.md
docs/workflows/ppo_paper_trading_observation_protocol.md
docs/workflows/README.md
docs/runs/paper_trading_decision_dashboard.md
docs/runs/paper_trading_decision_dashboard_with_state.md
docs/runs/v1.28_controlled_single_order_submit_decision.md
docs/runs/v1.29_signal_persistence_candidate_stability_policy.md
docs/runs/v1.30_candidate_stability_review_no_submit_fresh_cycle.md
docs/runs/v1.31_multi_order_candidate_handling_policy.md
docs/runs/v1.32_multi_order_filter_precheck_no_filter_no_submit.md
docs/runs/v1.33_paper_trading_decision_state_machine.md
docs/runs/v1.34_state_machine_dry_run_classification_utility.md
docs/runs/v1.35_decision_state_classification_report_integration.md
docs/runs/v1.36_paper_trading_pipeline_classification_hook_no_submit.md
docs/runs/v1.37_paper_trading_run_summary_includes_decision_state.md
docs/runs/v1.38_paper_trading_dashboard_reads_decision_state.md
docs/runs/v1.39_paper_trading_reporting_chain_smoke_test_no_submit.md
docs/runs/v1.40_paper_trading_operational_reporting_runbook.md
docs/runs/v1.41_paper_trading_reporting_chain_readme_update.md
docs/runs/v1.42_paper_trading_reporting_artifact_retention_policy.md
docs/runs/v1.43_reporting_artifact_retention_gitignore_review.md
docs/runs/v1.44_paper_trading_reporting_chain_final_audit_summary.md
docs/runs/v1.45_paper_trading_reporting_phase_closeout_transition_plan.md
docs/runs/v1.46_ppo_paper_trading_observation_protocol_confirmation_window_definition.md
docs/runs/v1.47_fresh_no_submit_market_session_review_using_completed_reporting_stack.md
docs/runs/v1.48_multi_session_ppo_paper_trading_observation_interim_summary.md
docs/runs/v1.49_ppo_stability_controlled_submit_eligibility_review.md
docs/runs/v1.50_ppo_readiness_decision_continue_observation_decision.md
docs/runs/v1.51_ppo_only_baseline_performance_package_continued_observation_plan.md
docs/runs/v1.52_ppo_continued_no_submit_observation_cycle_3_candidate_persistence_tracking.md
docs/runs/v1.53_ppo_candidate_persistence_review_observation_window_extension_decision.md
docs/runs/v1.54_ppo_continued_no_submit_observation_cycle_4_consecutive_persistence_test.md
docs/runs/v1.55_ppo_observation_window_interim_baseline_summary_continue_no_submit_decision.md
docs/runs/v1.56_ppo_continued_no_submit_observation_cycle_5_adjacent_candidate_persistence_test.md
docs/runs/v1.57_ppo_multi_order_recurrence_review_continue_no_submit_decision.md
docs/runs/v1.58_ppo_continued_no_submit_observation_cycle_6_amd_recurrence_confirmation_test.md
docs/runs/v1.59_ppo_amd_recurrence_multi_order_instability_review.md
docs/runs/v1.60_legacy_ppo_baseline_reclassification_no_submit_observation_closeout.md
docs/runs/v1.61_ppo_baseline_model_quality_audit_scope.md
docs/runs/v1.62_ppo_baseline_artifact_inventory.md
docs/runs/v1.63_ppo_baseline_model_quality_audit_report.md
docs/runs/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/standards/v1.64_ppo_promotion_standard_acceptance_criteria.md
docs/runs/v1.65_legacy_ppo_final_audit_decision.md
docs/decisions/v1.65_legacy_ppo_final_audit_decision.md
docs/runs/v1.66_ppo_v2_retraining_design.md
docs/designs/v1.66_ppo_v2_retraining_design.md
docs/runs/v1.67_ppo_v2_retraining_authorization_review.md
docs/decisions/v1.67_ppo_v2_retraining_authorization_review.md
```

Important context:

```txt
v1.27 candidate = UNH sell
v1.28 fresh candidate = AMD buy
v1.28 decision = NO-SUBMIT
v1.29 policy = candidate persistence required before controlled submit review
v1.30 fresh plan = PFE buy + UNH sell
v1.30 decision = NO-SUBMIT multi-order plan
v1.31 policy = do not submit multi-order plans directly
v1.32 fresh plan = orders_required 0
v1.32 decision = NO-SUBMIT absent / hold
v1.33 policy = paper-trading decision state machine
v1.34 utility = read-only dry-run decision-state classifier
v1.35 = classifier report writer
v1.36 = post-checklist classification hook
v1.37 = run summary includes decision state
v1.38 = dashboard reads decision state
v1.39 = reporting chain smoke test
v1.40 = operational reporting runbook
v1.41 = README / workflow index update
v1.42 = reporting artifact retention policy
v1.43 = .gitignore retention review
v1.44 = final reporting-chain audit summary
v1.45 = reporting phase closeout / transition plan
v1.46 = PPO observation protocol / confirmation window definition
v1.47 = MULTI_ORDER_PLAN / NO_SUBMIT / PFE buy + UNH sell
v1.48 = SINGLE_NEW_CANDIDATE / NO_SUBMIT / AMD buy
v1.49 = PPO stability review / controlled-submit eligibility blocked
v1.50 = PPO readiness decision / continue observation
v1.51 = PPO-only baseline package plan / continued observation plan
v1.52 = SINGLE_NEW_CANDIDATE / NO_SUBMIT / UNH sell
v1.53 = EXTEND_NO_SUBMIT_OBSERVATION_WINDOW
v1.54 = SINGLE_NEW_CANDIDATE / NO_SUBMIT / AMD buy
v1.55 = CONTINUE_NO_SUBMIT_OBSERVATION
v1.56 = MULTI_ORDER_PLAN / NO_SUBMIT / AAPL buy + AMD buy
v1.57 = CONTINUE_NO_SUBMIT_OBSERVATION after multi-order recurrence review
v1.58 = MULTI_ORDER_PLAN / NO_SUBMIT / AMD buy + UNH sell
v1.59 = CONTINUE_NO_SUBMIT_OBSERVATION after AMD recurrence and multi-order instability review
v1.60 = legacy PPO baseline reclassification / no-submit observation closeout
v1.61 = PPO baseline model-quality audit scope
v1.62 = PPO baseline artifact inventory
v1.63 = PPO baseline model-quality audit report
v1.64 = PPO promotion standard / acceptance criteria
v1.65 = legacy PPO final audit decision
v1.66 = PPO v2 retraining design
v1.67 = PPO v2 retraining authorization review
```

Do not rely on stale checkpoint candidates. Do not submit from prior checkpoint plans.

## Current Interpretation

The PPO-only paper-trading infrastructure is operationally and reporting-stable.

The PPO trading edge failed under the v1.63 stricter audit standard.

The current PPO model is reclassified as a legacy baseline / infrastructure validation fixture.

The current PPO model remains useful as a test fixture, infrastructure validation artifact, audit baseline, and evidence source for PPO v2 standards.

It should not be treated as paper-submit ready.

Current candidate persistence findings:

```txt
v1.47 = MULTI_ORDER_PLAN / NO_SUBMIT / PFE buy + UNH sell
v1.48 = SINGLE_NEW_CANDIDATE / NO_SUBMIT / AMD buy
v1.52 = SINGLE_NEW_CANDIDATE / NO_SUBMIT / UNH sell
v1.53 = EXTEND_NO_SUBMIT_OBSERVATION_WINDOW
v1.54 = SINGLE_NEW_CANDIDATE / NO_SUBMIT / AMD buy
v1.55 = CONTINUE_NO_SUBMIT_OBSERVATION
v1.56 = MULTI_ORDER_PLAN / NO_SUBMIT / AAPL buy + AMD buy
v1.57 = CONTINUE_NO_SUBMIT_OBSERVATION after multi-order recurrence review
v1.58 = MULTI_ORDER_PLAN / NO_SUBMIT / AMD buy + UNH sell
v1.59 = CONTINUE_NO_SUBMIT_OBSERVATION after AMD recurrence and multi-order instability review
AMD_buy_recurrent = true
AMD_buy_seen_in_v1_48 = true
AMD_buy_seen_in_v1_54 = true
AMD_buy_seen_in_v1_56 = true
AMD_buy_seen_in_v1_58 = true
UNH_sell_recurrent = true
UNH_sell_seen_in_v1_47 = true
UNH_sell_seen_in_v1_52 = true
UNH_sell_seen_in_v1_58 = true
AAPL_buy_disappeared_after_v1_56 = true
multi_order_instability = true
consecutive_single_candidate_persistence = false
controlled_submit_eligibility = BLOCKED
hybrid_gate_status = BLOCKED
NO-SUBMIT remains default
```

Current classification:

```txt
PPO model = legacy baseline / infrastructure validation fixture
PPO trading edge = failed under v1.63 stricter audit standard
controlled paper submit = blocked
paper order submission = not authorized
live orders = not authorized
PPO + Random Forest deployment = blocked
PPO + XGBoost deployment = blocked
retraining = not authorized by v1.67
NO-SUBMIT = default
```

Current v1.65 final audit decision:

```txt
legacy_ppo_final_classification = INFRASTRUCTURE_FIXTURE_ONLY
infrastructure_baseline_decision = PASS
offline_model_quality_decision = FAIL
trading_edge_decision = FAIL_FOR_TRADING_EDGE
no_submit_observation_decision = FAILED_TO_ESTABLISH_STABLE_PROMOTION_EVIDENCE
controlled_submit_decision = REJECT_FOR_CONTROLLED_SUBMIT
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
ppo_rf_deployment_decision = BLOCKED
ppo_xgboost_deployment_decision = BLOCKED
legacy_ppo_retraining_decision = DO_NOT_RETRAIN_LEGACY_MODEL
ppo_v2_retraining_design_decision = AUTHORIZED_FOR_DESIGN_ONLY
actual_retraining_execution = NOT_AUTHORIZED_BY_v1.65
```

Current v1.66 design decision:

```txt
ppo_v2_retraining_design_decision = AUTHORIZED_FOR_DESIGN_ONLY
legacy_ppo_retraining_decision = DO_NOT_RETRAIN_LEGACY_MODEL
actual_retraining_execution = NOT_AUTHORIZED_BY_v1.66
controlled_submit_decision = BLOCKED
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
ppo_rf_deployment_decision = BLOCKED
ppo_xgboost_deployment_decision = BLOCKED
```

Current v1.67 authorization review decision:

```txt
v1.66_design_review_decision = SUFFICIENT_FOR_CONTROLLED_IMPLEMENTATION_PLAN
ppo_v2_retraining_implementation_plan_decision = AUTHORIZED_FOR_PLANNING_ONLY
actual_retraining_execution = NOT_AUTHORIZED_BY_v1.67
generated_dataset_creation = NOT_AUTHORIZED_BY_v1.67
model_artifact_creation = NOT_AUTHORIZED_BY_v1.67
controlled_submit_decision = BLOCKED
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
ppo_rf_deployment_decision = BLOCKED
ppo_xgboost_deployment_decision = BLOCKED
```

Current v1.62 inventory summary:

```txt
manifest_path = config/paper_trading_six_ticker_manifest.json
symbols = AAPL, AMD, MRK, PFE, UNH, XOM
artifact_dirs_found = models/alpaca_ppo_models_master, trained_models
inventory_rows = 120
complete_artifact_rows = 18
incomplete_or_missing_rows = 102
AAPL rows = 20, complete_artifact_sets = 3
AMD rows = 20, complete_artifact_sets = 3
MRK rows = 20, complete_artifact_sets = 3
PFE rows = 20, complete_artifact_sets = 3
UNH rows = 20, complete_artifact_sets = 3
XOM rows = 20, complete_artifact_sets = 3
```

Passing tests proves code, control, and reporting stability. It does not prove trading profitability.

## Current Transition Plan

Latest completed milestone:

```txt
v1.66 PPO v2 Retraining Design
```

Current active checkpoint:

```txt
v1.67 PPO v2 Retraining Authorization Review
```

v1.44 closes the paper-trading reporting-control phase from v1.34 through v1.44.

It confirms that the no-submit reporting stack, decision-state visibility, artifact flow, smoke-test coverage, documentation, and repository hygiene are mature enough to support supervised paper-trading review.

v1.44 does not prove that the PPO strategy is stable, profitable, or ready for broader controlled submit usage.

Reporting stability must not be treated as strategy-performance stability.

Current transition direction:

```txt
v1.66 designed PPO v2 retraining only.
v1.67 reviews whether v1.66 is sufficient to authorize a controlled PPO v2 retraining implementation plan.
v1.67 authorization is planning-only.
actual retraining execution requires a later checkpoint.
generated dataset creation remains unauthorized.
model artifact creation remains unauthorized.
controlled submit remains blocked.
paper orders remain unauthorized.
live orders remain unauthorized.
PPO + RF and PPO + XGBoost remain blocked.
```

Hybrid model integration remains blocked until a standalone PPO baseline has enough validation, audit, and supervised paper-trading evidence to justify comparison or extension.

Default posture remains:

```txt
NO-SUBMIT unless a separate controlled-submit checkpoint explicitly authorizes otherwise.
```

---

# 2. Current Objective

Current operational focus:

Review whether v1.66 is sufficient to authorize a controlled PPO v2 retraining implementation plan.

The v1.34 through v1.44 milestones completed the engineering, safety, reporting-control, and artifact-governance layer.

This proves that the no-submit reporting stack, decision-state reporting, artifact flow, smoke tests, operational reporting chain, and repository hygiene are working.

This does not prove that the PPO strategy is stable, profitable, or ready for broader controlled submit usage.

Next objective:

Complete v1.67 PPO v2 Retraining Authorization Review before any implementation-plan work, retraining execution, generated dataset creation, model artifact creation, controlled submit, paper order authorization, live order authorization, or hybrid gate work becomes active.

Current observation findings:

```txt
v1.47 = MULTI_ORDER_PLAN / NO_SUBMIT / PFE buy + UNH sell
v1.48 = SINGLE_NEW_CANDIDATE / NO_SUBMIT / AMD buy
v1.52 = SINGLE_NEW_CANDIDATE / NO_SUBMIT / UNH sell
v1.53 = EXTEND_NO_SUBMIT_OBSERVATION_WINDOW
v1.54 = SINGLE_NEW_CANDIDATE / NO_SUBMIT / AMD buy
v1.55 = CONTINUE_NO_SUBMIT_OBSERVATION
v1.56 = MULTI_ORDER_PLAN / NO_SUBMIT / AAPL buy + AMD buy
v1.57 = CONTINUE_NO_SUBMIT_OBSERVATION after multi-order recurrence review
v1.58 = MULTI_ORDER_PLAN / NO_SUBMIT / AMD buy + UNH sell
v1.59 = CONTINUE_NO_SUBMIT_OBSERVATION after AMD recurrence and multi-order instability review
AMD_buy_recurrent = true
AMD_buy_seen_in_v1_48 = true
AMD_buy_seen_in_v1_54 = true
AMD_buy_seen_in_v1_56 = true
AMD_buy_seen_in_v1_58 = true
UNH_sell_recurrent = true
UNH_sell_seen_in_v1_47 = true
UNH_sell_seen_in_v1_52 = true
UNH_sell_seen_in_v1_58 = true
AAPL_buy_disappeared_after_v1_56 = true
multi_order_instability = true
consecutive_single_candidate_persistence = false
controlled_submit_eligibility = BLOCKED
hybrid_gate_status = BLOCKED
NO-SUBMIT remains default
```

Current classification:

```txt
PPO model = legacy baseline / infrastructure validation fixture
PPO trading edge = failed under v1.63 stricter audit standard
controlled paper submit = blocked
paper order submission = not authorized
live orders = not authorized
PPO + Random Forest deployment = blocked
PPO + XGBoost deployment = blocked
retraining = not authorized by v1.67
NO-SUBMIT = default
```

The default operating posture remains:

```txt
default decision = NO-SUBMIT
classification required before any future submit review
controlled submit remains a separate checkpoint
PPO + RF deployment remains blocked until PPO-only evidence is complete
PPO + XGBoost deployment remains blocked until PPO-only and PPO + RF readiness are clearer
feature importance must not be used as evidence of trading edge
v1.67 does not run training
v1.67 does not create generated datasets
v1.67 does not create model artifacts
v1.67 does not authorize paper orders
v1.67 does not authorize live orders
v1.67 does not authorize controlled submit
v1.67 does not unblock PPO + RF
v1.67 does not unblock PPO + XGBoost
```

Near-term operating path:

```txt
v1.67 reviews whether v1.66 is sufficient to authorize a controlled PPO v2 retraining implementation plan.
v1.67 authorization is planning-only.
v1.68 may define the controlled PPO v2 retraining implementation plan.
actual retraining execution requires a later checkpoint.
generated dataset creation remains unauthorized.
model artifact creation remains unauthorized.
controlled submit remains blocked.
paper orders remain unauthorized.
live orders remain unauthorized.
PPO + RF and PPO + XGBoost remain blocked.
```

The required PPO-only evidence package must include:

```txt
historical embargo-aware walk-forward validation
untouched holdout validation
leakage review
train-only normalization / preprocessing controls
backtest-style performance metrics
fresh supervised paper-trading observation results
multi-session stability review
PPO-only performance package review
```

The PPO-only baseline package should review:

```txt
walk-forward returns
holdout behavior
Sharpe / Sortino
max drawdown
win rate
turnover
trade frequency
slippage / cost assumptions
candidate persistence
decision-state distribution
paper-trading P&L
paper-trading drawdown
paper-trading turnover
changed candidates
multi-order plans
broker-state observations
```

The intended promotion path is:

```txt
Completed PPO-only model + reporting stack
-> walk-forward validation review
-> holdout validation review
-> leakage / normalization controls review
-> supervised paper-trading observation
-> stability review
-> PPO-only baseline performance package
-> then consider PPO + RF / PPO + XGBoost gate candidates
```

This is explicitly not the intended promotion path:

```txt
Backtest -> paper trade -> move to hybrid gate
```

PPO + Random Forest should be treated as an extension candidate, not as a replacement for PPO-only validation.

PPO + XGBoost remains a later comparison path after PPO-only and PPO + Random Forest readiness are clearer.

This phase establishes:

* fresh-run discipline
* candidate persistence review
* no-submit default behavior
* stale-plan prevention
* multi-order handling discipline
* single-order filtering discipline
* state-machine decision classification
* risk-control and checklist enforcement
* broker-state verification
* auditable paper-trading decisions
* reporting-chain auditability
* artifact governance
* PPO-only evidence requirements before hybrid gates

A controlled paper submit is not the current default objective.

Any future controlled submit requires a separate decision checkpoint after the full safety stack passes.

## Parallel Research Track

The longer-term research track remains:

Develop and validate a standalone PPO baseline trained on Alpaca historical 1-hour bars using embargo-aware walk-forward evaluation.

This research track includes:

* reproducible retraining configuration
* artifact isolation
* validation consistency
* retraining governance
* holdout reservation standards
* deployment separation from previously validated models

Full retraining, model promotion, and hybrid model work must not bypass paper-trading, holdout-validation, leakage-control, or PPO-only baseline evidence guardrails.

---

# 3. Strategic Research Direction

## Near-Term Operational Objective

Review whether v1.66 is sufficient to authorize a controlled PPO v2 retraining implementation plan.

Next operational checkpoint:

```txt
v1.68 PPO v2 Controlled Retraining Implementation Plan
```

The goal is to formally document:

* v1.66 design sufficiency for controlled implementation planning
* PPO v2 retraining implementation plan authorization is planning-only
* actual retraining execution remains unauthorized
* generated dataset creation remains unauthorized
* model artifact creation remains unauthorized
* paper order authorization remains unauthorized
* live order authorization remains unauthorized
* controlled submit remains blocked
* PPO + RF and PPO + XGBoost remain blocked

Near-term operating path:

```txt
v1.67 reviews whether v1.66 is sufficient to authorize a controlled PPO v2 retraining implementation plan.
v1.67 authorization is planning-only.
v1.68 may define the controlled PPO v2 retraining implementation plan.
actual retraining execution requires a later checkpoint.
generated dataset creation remains unauthorized.
model artifact creation remains unauthorized.
controlled submit remains blocked.
paper orders remain unauthorized.
live orders remain unauthorized.
PPO + RF and PPO + XGBoost remain blocked.
```

---

## Near-Term Research Objective

Review the standalone PPO baseline as a complete evidence package before considering hybrid gates.

The PPO-only baseline evidence package must combine:

```txt
historical walk-forward validation
untouched holdout validation
leakage review
train-only normalization / preprocessing controls
backtest-style performance metrics
fresh paper-trading observation results
multi-session stability review
```

Promotion requirements:

* embargo-aware walk-forward validation
* untouched holdout validation
* leakage-control review
* locked train-only normalization / preprocessing controls
* supervised paper-trading verification
* candidate stability review
* PPO-only baseline performance package
* deployment review
* manual approval before any controlled paper submit

---

## Medium-Term Objective

After standalone PPO stabilization, observation, and baseline-performance review:

```txt
PPO
  ↓
PPO + Random Forest gate
  ↓
PPO + XGBoost gate
```

Hybrid systems should only be evaluated for deployment after the standalone Alpaca PPO baseline has completed retraining, validation, holdout review, leakage review, supervised paper deployment review, multi-session paper-trading behavior review, and PPO-only baseline performance review.

Do not move to hybrid systems prematurely.

## Future Phase: Feature Importance / Model Interpretability

Feature importance and model interpretability should be treated as a later post-validation research phase.

This phase is not part of the current PPO-only v1.45 through v1.60 closeout or the v1.61 through v1.67 audit and retraining-governance roadmap.

The purpose is different from PPO-only validation:

```txt
PPO-only validation asks:
Does the system work, generalize, and behave safely over time?

Feature importance / interpretability asks:
Why does the model work, and which features or regimes are driving decisions?
```

Potential future methods:

```txt
Random Forest MDI / feature_importances_
MDA / permutation importance
XGBoost feature importance
SHAP analysis
PPO feature ablation studies
regime-specific feature review
feature-importance stability across walk-forward windows
```

Feature importance should not be used as proof of profitability or deployment readiness.

Feature importance can explain which features influence a validated or candidate-valid model, but it does not replace:

```txt
walk-forward validation
holdout validation
leakage review
train-only normalization / preprocessing controls
paper-trading observation
stability review
PPO-only baseline performance review
```

Feature importance should be considered during or after PPO + Random Forest and PPO + XGBoost validation, not as a shortcut around PPO-only baseline evidence.

---

# 4. Validation Hierarchy

Validation hierarchy must remain strictly enforced:

```txt
train_df   = model fitting only
embargo    = temporal gap
eval_df    = walk-forward evaluation
holdout_df = untouched final validation
```

Rules:

* no temporal overlap
* no leakage
* holdout isolation required
* evaluation uses locked train-only normalization / preprocessing statistics
* no repeated tuning against holdout
* no model promotion without deployment review

---

# 5. Core System Architecture

```txt
Market Data Layer
    ↓
Feature Engineering Layer
    ↓
Safe Feature Manifest
    ↓
PPO Training Layer
    ↓
Validation + Candidate Selection
    ↓
Paper-Trading Dry Run
    ↓
Dry-Run Evaluation
    ↓
Execution Plan
    ↓
Risk Controls
    ↓
Pre-Trade Checklist
    ↓
Supervised Paper-Order Runner
    ↓
Broker Verification
    ↓
Audit + Monitoring
    ↓
Decision Documentation
```

The architecture is intentionally staged so that model output is never treated as immediate trade approval.

---

# 6. Critical Modules

## Data Layer

```txt
src/data/alpaca_historical_data.py
src/data/alpaca_training_dataset.py
```

Responsibilities:

* Alpaca historical ingestion
* normalization
* provenance tracking
* model-ready dataset generation

---

## Feature Engineering

```txt
src/features.py
src/feature_manifest.py
```

Responsibilities:

* technical indicators
* regime features
* denoising
* target labeling
* safe feature selection
* leakage prevention

---

## Training + Validation

```txt
src/train.py
src/training_splits.py
src/vecnormalize_utils.py
src/env.py
```

Responsibilities:

* walk-forward PPO training
* embargo enforcement
* VecNormalize management
* candidate tracking
* evaluation isolation

---

## Alpaca Adapter Layer

```txt
src/adapters/alpaca.py
```

Responsibilities:

* paper-account connection
* Alpaca endpoint enforcement
* account snapshots
* position reads
* recent bar downloads
* latest price lookup
* controlled market-order helper
* no live-money endpoint usage for paper-trading workflows

Required Alpaca endpoint:

```txt
https://paper-api.alpaca.markets
```

---

## Paper-Trading Deployment Layer

```txt
src/paper_trading/paper_trade_dry_run.py
src/paper_trading/evaluate_dry_run.py
src/paper_trading/build_execution_plan.py
src/paper_trading/risk_controls.py
src/paper_trading/filter_execution_plan.py
src/paper_trading/paper_trade_loop.py
src/paper_trading/pre_trade_checklist.py
src/paper_trading/logging_utils.py
```

Responsibilities:

* broker-connected no-order dry-run inference
* dry-run validation
* execution-plan generation
* single-order filtering
* risk-control enforcement
* stale-plan prevention
* explicit run-directory confirmation
* supervised Alpaca paper-order submission only when intentionally approved
* broker-state verification
* audit logging

---

## Paper-Trading Reporting Layer

```txt
src/paper_trading/classify_decision_state.py
src/paper_trading/pipeline_decision_state_hook.py
src/paper_trading/build_run_summary_with_decision_state.py
src/paper_trading/build_decision_dashboard_with_state.py
src/paper_trading/reporting_chain_smoke_test.py
```

Responsibilities:

* classify paper-trading decision state
* write decision_state_report.json
* build paper_trading_run_summary.json
* build dashboard with decision state
* run reporting-chain smoke tests
* preserve NO-SUBMIT default
* avoid broker calls and order submission in reporting utilities

---

# 7. Safe Feature Standards

The following fields must never enter model feature inputs:

```txt
Target
Return
Datetime
Symbol
```

These columns are permitted for:

* labeling
* evaluation
* grouping
* auditing
* reporting

Leakage prevention is enforced through:

```txt
src/feature_manifest.py
```

---

# 8. Current PPO Workflow

Current training workflow:

1. construct walk-forward window
2. split into train / embargo / eval
3. train PPO on train only
4. persist VecNormalize train statistics
5. evaluate using locked eval statistics
6. rank candidate windows
7. save metrics and artifacts
8. reserve untouched holdout for final validation
9. deploy only after review

Evaluation constraints:

```txt
eval_env.training = False
eval_env.norm_reward = False
```

---

# 9. Current Paper-Trading Workflow

Normal monitoring cycle is no-submit by default:

```bash
python -m src.paper_trading.paper_trade_dry_run \
  --manifest config/paper_trading_six_ticker_manifest.json \
  --artifacts-dir models/alpaca_ppo_models_master

python -m src.paper_trading.evaluate_dry_run \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.build_execution_plan \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.risk_controls \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/latest

python -m src.paper_trading.pre_trade_checklist \
  --run-dir reports/paper_trading_dry_runs/latest \
  --check-broker \
  --expected-equity 100000 \
  --equity-tolerance-pct 0.05 \
  --allow-open-positions
```

Expected no-submit pass conditions:

```txt
Evaluation result = PASS
Risk result = PASS
Checklist result = PASS
predict_ok_count = expected universe size
error_count = 0
orders_submitted = 0
submit_orders = False
broker_open_orders_zero = PASS
broker_snapshot_errors_empty = PASS
```

Hard stop conditions:

```txt
dry-run evaluation fails
risk controls fail
pre-trade checklist fails
broker open orders are unexpected
execution plan is stale
market data is unavailable
candidate changed unexpectedly
orders_required > 1 and no single-order filter was used
manual approval is missing
```

---

# 10. Candidate Stability Policy

Current active policy:

```txt
docs/workflows/signal_persistence_candidate_stability_policy.md
```

Core rule:

```txt
A candidate must be revalidated on a fresh future run before any submit decision.
Do not submit from a prior checkpoint's execution plan.
Do not assume a prior candidate remains valid.
```

Candidate definition:

```txt
should_order = True
side in {buy, sell}
orders_required >= 1
```

Changed candidate conditions:

```txt
symbol changes
side changes
candidate disappears
orders_required changes from 1 to multiple
candidate becomes below_min_notional
risk fails
checklist fails
plan becomes stale
```

Candidate stability levels:

```txt
Level 0 = one-time candidate; review only
Level 1 = revalidated candidate; eligible for controlled review
Level 2 = submit-eligible candidate; requires full safety stack and manual approval
```

Default action when uncertain:

```txt
NO-SUBMIT
```

---

# 11. Controlled Submit Requirements

Controlled paper submits are not automatic.

A controlled submit may only be considered after all conditions below are true:

```txt
fresh dry run completed
dry-run evaluation passed
execution plan rebuilt from the fresh dry run
candidate persisted or was freshly revalidated
orders_required = 1, or a reviewed single-order filtered directory exists
risk controls passed
pre-trade checklist passed
plan_not_stale = PASS
execution_plan_not_stale = PASS
broker open orders = 0
selected order is explicitly identified
manual review completed
manual approval is explicit
post-submit broker verification is planned
```

Controlled submit commands are intentionally omitted from this context file.

Any future controlled-submit command must be generated only inside a separate controlled-submit checkpoint after the required evidence, safety stack, manual approval, and broker-state verification are complete.

Never submit against an old checkpoint plan.

Never submit against `reports/paper_trading_dry_runs/latest` when the original plan has more than one eligible order.

Never treat risk/checklist pass as trade approval by itself.

---

# 12. Current Training Parameters

Defined in:

```txt
src/env.py
```

Current operational parameters:

```txt
window_size=10
cost_rate=0.0002
slip_rate=0.0003
k_alpha=0.20
k_mom=0.05
mom_lookback=20
min_trade_delta=0.01
cooldown=5
reward_clip=1.0
```

---

# 13. Canonical Data Source

Current planned retraining source:

```txt
Alpaca historical 1-hour stock bars
```

Canonical baseline universe:

```txt
AAPL
AMD
MRK
PFE
UNH
XOM
```

v1.67 does not authorize data extraction, generated dataset creation, training execution, or model artifact creation.

---

# 14. Artifact Governance

Validated artifacts must not be overwritten.

Current validated artifact directory:

```txt
models/ppo_models_master
```

Current Alpaca PPO paper-trading artifact directory:

```txt
models/alpaca_ppo_models_master
```

Expected isolated retraining directories for a future implementation plan:

```txt
models/alpaca_ppo_models_master
reports/alpaca_ppo_retraining
```

Generated datasets, model artifacts, run outputs, reports, logs, and credentials should remain excluded from version control unless intentionally documented otherwise.

v1.67 does not authorize creating generated datasets, model artifacts, or retraining reports.

---

# 15. Deployment Constraints

Current deployment policy:

* supervised paper trading only
* no real-money trading
* no unattended execution
* no automatic multi-order submission
* no stale-plan submission
* no forced cleanup of residual positions
* no automatic exits after recent entries
* manual order review required
* broker-state verification required
* audit logging required
* documentation required for milestone decisions

Approved behavior:

```txt
supervised no-submit cycles
controlled one-order paper submit tests only after a separate approval checkpoint
single-order filtered review tests
post-submit monitoring only after a separately approved controlled-submit checkpoint
residual position monitoring
candidate stability review
decision logging
```

Not approved:

```txt
unattended trading
real-money trading
automatic multi-order submission
submitting stale candidates
submitting changed candidates
submitting from prior checkpoint plans
forced residual cleanup
automatic entries
automatic exits
```

---

# 16. Testing + CI Standards

Primary local test command:

```bash
python -m pytest
```

Requirements before milestone promotion:

* local tests passing
* GitHub Actions passing when available
* clean git state
* reviewed artifact changes
* no generated datasets committed
* no credentials committed
* paper-trading docs updated after operational milestones

CI workflow:

```txt
.github/workflows/tests.yml
```

---

# 17. Repository Standards

Expected repository root:

```txt
ppo_research_pipeline/
```

Before modifications:

```bash
pwd
git rev-parse --show-toplevel
git status --short
```

Files must not be created outside:

```txt
ppo_research_pipeline
```

---

# 18. Generated Data Policy

Generated data must remain excluded from version control.

Ignored paths:

```txt
data/raw/*
data/processed/*
data/alpaca_historical/*
data/alpaca_training/*
reports/*
logs/*
models/*
```

Large artifacts generally excluded:

```txt
*.zip
*.pt
*.pth
*.onnx
*.joblib
*.pkl
*.csv
```

Never commit:

```txt
.env
.env.*
API keys
broker credentials
raw account exports
large generated run outputs
```

---

# 19. Active Deliverables

Current operational deliverables:

```txt
v1.67 PPO v2 Retraining Authorization Review
review whether v1.66 is sufficient to authorize a controlled PPO v2 retraining implementation plan
v1.66_design_review_decision = SUFFICIENT_FOR_CONTROLLED_IMPLEMENTATION_PLAN
ppo_v2_retraining_implementation_plan_decision = AUTHORIZED_FOR_PLANNING_ONLY
actual_retraining_execution = NOT_AUTHORIZED_BY_v1.67
generated_dataset_creation = NOT_AUTHORIZED_BY_v1.67
model_artifact_creation = NOT_AUTHORIZED_BY_v1.67
controlled_submit_decision = BLOCKED
paper_order_authorization = NOT_AUTHORIZED
live_order_authorization = NOT_AUTHORIZED
ppo_rf_deployment_decision = BLOCKED
ppo_xgboost_deployment_decision = BLOCKED
do not run training
do not create generated datasets
do not create model artifacts
do not submit orders
preserve NO-SUBMIT default
keep controlled submit blocked
keep PPO + RF and PPO + XGBoost blocked
```

Next operational deliverables:

```txt
v1.68 PPO v2 Controlled Retraining Implementation Plan
define implementation files, planned configuration, tests, validation utilities, runbook steps, artifact paths, and safety checks
implementation planning only
actual retraining execution requires a later checkpoint
generated dataset creation requires a later checkpoint
model artifact creation requires a later checkpoint
controlled submit remains blocked
paper orders remain unauthorized
live orders remain unauthorized
PPO + RF and PPO + XGBoost remain blocked

later PPO-Only Baseline Performance Package Completion
combine historical validation, holdout evidence, leakage controls, normalization controls, backtest-style metrics, and supervised paper-trading observation evidence after PPO v2 completes the required offline and no-submit gates
```

Current hardening candidates before any future controlled submit:

```txt
make submit mode fail closed if broker account/positions/open-order reads fail
add runner-level max_orders_to_submit=1 default
add post-submit order-status reconciliation by order id
keep PROJECT_CONTEXT.md aligned with latest paper-trading policy
```

Longer-term research deliverables:

```txt
future controlled PPO v2 retraining implementation plan
future standalone Alpaca PPO training integration
future Alpaca PPO retrain smoke test
future final holdout validation
future PPO-only baseline performance package
future PPO + Random Forest gate readiness review
future PPO + XGBoost gate comparison
future Feature Importance / Model Interpretability phase
```

---

# 20. Planned Milestones

Operational paper-trading milestones:

```txt
v1.45 Paper-Trading Reporting Phase Closeout / Transition Plan
v1.46 PPO Paper-Trading Observation Protocol / Confirmation Window Definition
v1.47 Fresh No-Submit Market-Session Review Using Completed Reporting Stack
v1.48 Multi-Session PPO Paper-Trading Observation and Interim Summary
v1.49 PPO Paper-Trading Stability Review / Controlled Submit Eligibility Review
v1.50 PPO Paper-Trading Readiness Decision
v1.51 PPO-Only Baseline Performance Package / Continued Observation Plan
v1.52 PPO Continued No-Submit Observation Cycle 3 / Candidate Persistence Tracking
v1.53 PPO Candidate Persistence Review / Observation Window Extension Decision
v1.54 PPO Continued No-Submit Observation Cycle 4 / Consecutive Persistence Test
v1.55 PPO Observation Window Interim Baseline Summary / Continue No-Submit Decision
v1.56 PPO Continued No-Submit Observation Cycle 5 / Adjacent Candidate Persistence Test
v1.57 PPO Multi-Order Recurrence Review / Continue No-Submit Decision
v1.58 PPO Continued No-Submit Observation Cycle 6 / AMD Recurrence Confirmation Test
v1.59 PPO AMD Recurrence / Multi-Order Instability Review
v1.60 Legacy PPO Baseline Reclassification / No-Submit Observation Closeout
v1.61 PPO Baseline Model Quality Audit Scope
v1.62 PPO Baseline Artifact Inventory
v1.63 PPO Baseline Model Quality Audit Report
v1.64 PPO Promotion Standard / Acceptance Criteria
v1.65 Legacy PPO Final Audit Decision
v1.66 PPO v2 Retraining Design
v1.67 PPO v2 Retraining Authorization Review
v1.68 PPO v2 Controlled Retraining Implementation Plan
```

Research milestones:

```txt
Standalone Alpaca PPO training integration
Alpaca PPO retrain smoke test
Final holdout validation
Alpaca PPO paper-trading redeployment review
PPO-Only Baseline Performance Package
PPO + Random Forest Gate
PPO + XGBoost Gate
Feature Importance / Model Interpretability Phase
```

Hybrid model milestones must remain blocked until standalone PPO validation and supervised paper-trading observation are complete.

PPO + Random Forest remains the next hybrid candidate, but it should not be deployed until PPO-only behavior has been observed across a meaningful paper-trading window and reviewed in a PPO-only baseline performance package.

PPO + XGBoost remains a later comparison path after PPO-only and PPO + Random Forest readiness are clearer.

Feature Importance / Model Interpretability is a later post-validation research phase.

It should not be used as proof of profitability, generalization, or deployment readiness.

---

# 21. Operational Guardrails

Do not:

* bypass holdout validation
* repeatedly tune against holdout
* overwrite validated artifacts
* commit generated datasets
* commit credentials
* enable unattended execution
* move to hybrid systems prematurely
* submit paper orders without review
* submit stale candidates
* submit changed candidates
* submit from prior checkpoint plans
* submit from unfiltered multi-order plans
* treat candidate identification as trade approval
* treat risk/checklist pass as trade approval by itself
* run PPO v2 training before a later checkpoint authorizes execution
* create PPO v2 generated datasets before a later checkpoint authorizes execution
* create PPO v2 model artifacts before a later checkpoint authorizes execution
* unblock PPO + RF from the legacy PPO
* unblock PPO + XGBoost from the legacy PPO

When in doubt:

```txt
NO-SUBMIT
rerun a fresh dry run
review the execution plan
verify broker state
document the decision
```

---

# 22. Maintenance Requirements

Update this document when:

* milestones complete
* validation methodology changes
* deployment workflows change
* schemas change
* architecture changes
* operational constraints change
* artifact structure changes
* paper-trading policy changes
* latest candidate decision changes
* test status changes

This document functions as the authoritative operational and research reference for the repository.
