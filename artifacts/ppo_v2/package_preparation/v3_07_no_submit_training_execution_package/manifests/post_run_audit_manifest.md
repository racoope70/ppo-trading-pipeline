# Post-Run Audit Manifest

```text
run_id = v3_07_no_submit_ppo_v2_training_execution_001
v3_08_post_run_audit_required = true
metrics_before_v3_08_authorized = false
reports_before_v3_08_authorized = false
model_promotion_before_v3_08_authorized = false
deployment_before_v3_08_authorized = false
paper_orders_before_v3_08_authorized = false
live_orders_before_v3_08_authorized = false
controlled_submit_before_v3_08_authorized = false
ppo_rf_before_v3_08_authorized = false
ppo_xgboost_before_v3_08_authorized = false
trading_edge_claims_before_v3_08_authorized = false
profitability_claims_before_v3_08_authorized = false
```

If a later sealed checkpoint authorizes and completes one-time no-submit PPO v2 training, a v3.08 post-run audit is required before metrics, reports, promotion, deployment, orders, controlled submit, hybrid models, or trading-edge/profitability claims are considered.
