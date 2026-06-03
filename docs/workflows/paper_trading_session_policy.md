# Paper-Trading Session Policy / Operational Runbook

Version: v1.16  
Status: Active operational policy  
Scope: Alpaca PPO paper-trading deployment  
Mode: Supervised paper trading only  

## Purpose

This runbook defines the operating rules for supervised Alpaca paper-trading sessions using the redeployed Alpaca-trained PPO system.

The goal is not to maximize trading activity. The goal is to ensure every paper-trading cycle is:

```text
fresh
reviewed
risk-controlled
auditable
manually approved before any submit
never unattended
```

This policy applies after the following completed checkpoints:

```text
v1.9  Alpaca PPO paper-trading redeployment
v1.10 Controlled Alpaca paper-order redeployment test
v1.11 Post-order monitoring / rebalance verification
v1.12 Short monitored Alpaca paper-trading session
v1.13 Single-order submit guard / execution filter
v1.14 Controlled single-order submit test
v1.15 Post-single-order residual monitoring
```

## Current Operating Status

The system is approved for supervised Alpaca paper-trading checks only.

The system is not approved for unattended trading.

The system is not approved for automatic multi-order submission.

The system is not approved for real-money trading.

## Core Operating Principle

Every cycle must begin with fresh broker-connected data.

Never submit from stale files.

Never submit directly from an old `reports/paper_trading_dry_runs/latest` plan without rerunning the full decision chain.

## Standard No-Submit Monitoring Cycle

Use this for normal monitoring.

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

```text
Evaluation result = PASS
Risk result = PASS
Checklist result = PASS
predict_ok_count = 6
error_count = 0
orders_submitted = 0
submit_orders = False
broker_open_orders_zero = PASS
broker_snapshot_errors_empty = PASS
```

## Submit Eligibility Rules

A paper order may only be considered if all conditions below are true:

```text
fresh dry run completed
dry-run evaluation passed
execution plan was built from the fresh dry run
risk controls passed
pre-trade checklist passed before submit
broker open orders = 0
order is small and explainable
manual review completed
selected order is explicitly identified
```

A submit is not allowed if any condition below is true:

```text
dry run failed
predict_ok_count < expected universe size
error_count > 0
risk controls failed
pre-trade checklist failed before submit
broker has unexpected open orders
execution plan is stale
market data is stale or unavailable
order size is not understood
more than one order would be submitted unintentionally
```

## Orders Required Decision Rules

### Case 1: orders_required = 0

Do not submit.

Interpretation:

```text
The system recommends hold.
Existing positions are either aligned with target or below minimum notional.
```

Action:

```text
Document as a clean no-submit monitoring cycle if this is part of a milestone.
```

### Case 2: orders_required = 1

A controlled submit may be considered only after review.

Action:

```text
Review execution_plan.csv
Confirm symbol, side, qty, price, target_weight, actual_weight, delta_notional
Confirm risk controls passed
Confirm checklist passed
Submit only if the order is small and justified
Verify broker state immediately after submit
```

### Case 3: orders_required > 1

Do not submit directly from the plan.

Action:

```text
Use the v1.13 single-order filter if one specific order is manually selected.
Otherwise skip submit and document the cycle as no-submit.
```

## Single-Order Filter Procedure

Use this only after a fresh full no-submit chain has passed.

Example for AMD buy:

```bash
python -m src.paper_trading.filter_execution_plan \
  --run-dir reports/paper_trading_dry_runs/latest \
  --output-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_buy \
  --symbol AMD \
  --side buy
```

Example for AMD sell:

```bash
python -m src.paper_trading.filter_execution_plan \
  --run-dir reports/paper_trading_dry_runs/latest \
  --output-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_sell \
  --symbol AMD \
  --side sell
```

After filtering, rerun validation on the filtered directory:

```bash
python -m src.paper_trading.risk_controls \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_sell

python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_sell

python -m src.paper_trading.pre_trade_checklist \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_sell \
  --check-broker \
  --expected-equity 100000 \
  --equity-tolerance-pct 0.05 \
  --allow-open-positions
```

Only after the filtered checklist passes may a controlled submit be considered.

Submit only against the filtered directory:

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_sell \
  --submit-orders
```

Never use `--submit-orders` against `latest` when the original plan has more than one eligible order.

## Broker Verification After Any Submit

Immediately after any submit, run a broker-state check:

```bash
python - <<'PY'
from dotenv import load_dotenv
import os

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

load_dotenv(".env", override=True)

client = TradingClient(
    api_key=os.getenv("APCA_API_KEY_ID"),
    secret_key=os.getenv("APCA_API_SECRET_KEY"),
    paper=True,
    url_override=os.getenv("APCA_API_BASE_URL"),
)

acct = client.get_account()
positions = client.get_all_positions() or []
open_orders = client.get_orders(
    filter=GetOrdersRequest(status=QueryOrderStatus.OPEN)
) or []

print("Account:")
print("status:", acct.status)
print("equity:", acct.equity)
print("cash:", acct.cash)
print("buying_power:", acct.buying_power)

print("\nPositions:")
if not positions:
    print("(none)")
else:
    for p in positions:
        print(
            p.symbol,
            "qty=", p.qty,
            "market_value=", p.market_value,
            "avg_entry=", p.avg_entry_price,
            "unrealized_pl=", p.unrealized_pl,
            "unrealized_plpc=", p.unrealized_plpc,
        )

print("\nOpen orders:")
if not open_orders:
    print("(none)")
else:
    for o in open_orders:
        print(o.symbol, o.side, o.qty, o.status, o.id)
PY
```

Required broker conditions after submit:

```text
account active
cash available
equity near expected range
open orders = none, unless the one submitted order is still pending and fully understood
no unexpected positions
```

## Post-Submit Checklist Interpretation

After a real submit, the checklist may report `FAIL` because no-submit checks are expected to fail.

Expected post-submit failures:

```text
paper_order_summary_orders_submitted_zero = FAIL
paper_order_summary_no_order_mode = FAIL
audit_log_orders_submitted_zero = FAIL
audit_log_no_order_mode = FAIL
```

These are acceptable only if:

```text
orders_submitted = 1
submit_orders = True
risk_passed = True
broker_open_orders_zero = PASS or one known order remains open
broker_snapshot_errors_empty = PASS
```

If broker checks fail, stop immediately.

## Residual Position Policy

Tiny residual positions can occur after fractional paper orders.

Residuals should not be manually cleaned up unless a fresh dry run recommends an eligible order and all controls pass.

If residual notional is below `REBALANCE_MIN_NOTIONAL`, expected behavior is:

```text
side = hold
should_order = False
reason = below_min_notional
```

Do not force cleanup trades for tiny residuals.

## Market Hours and Data Availability Policy

If Alpaca returns no recent bars, stop.

Do not treat the dry run as valid.

Do not build an execution plan from a failed dry run.

Do not submit.

Common causes:

```text
market closed
weekend
holiday
stale data window
Alpaca feed issue
```

Best action:

```text
wait for market hours
rerun fresh dry run
continue only after evaluation passes
```

## Session Frequency

For monitored paper trading:

```text
1-hour strategy = wait for a later 1-hour bar before repeating cycles
do not spam repeated cycles from the same bar
do not run full-day unattended sessions
```

For short monitored sessions:

```text
1 to 3 supervised cycles maximum
manual review after each cycle
broker verification after any submit
stop after unexpected behavior
```

## Hard Stop Rules

Stop immediately if any of these occur:

```text
dry-run evaluation fails
risk controls fail
pre-submit checklist fails
broker open orders are unexpected
order count is higher than intended
order size is not understood
execution plan is stale
market data is unavailable
any Python exception occurs during execution chain
Alpaca account status is not active
paper endpoint is not confirmed
```

Do not continue downstream commands after a failed step.

Prefer command chaining with `&&` when appropriate so later steps do not run after failure.

## Documentation Requirements

Document milestone sessions under:

```text
docs/runs/
```

Document workflow policies under:

```text
docs/workflows/
```

A run note should include:

```text
date
mode
purpose
starting tag
test result
dry-run result
execution-plan result
risk-control result
checklist result
submit decision
broker state before and after
interpretation
guardrails
next step
```

## Git / Release Procedure

For documentation-only checkpoints:

```bash
git status --short
python -m pytest

git add <new_doc_file>
git commit -m "<clear commit message>"

git pull --rebase origin main
git push

git status --short
python -m pytest
git log --oneline -10
```

After GitHub Actions passes:

```bash
git tag -a <tag-name> -m "<tag message>"
git push origin <tag-name>

git tag --points-at HEAD
python -m pytest
git log --oneline -10
```

## Current Approved State

Approved:

```text
supervised no-submit cycles
controlled one-order paper submit tests
single-order filtered submit tests
post-submit monitoring
residual position monitoring
```

Not approved:

```text
unattended trading
real-money trading
automatic multi-order submission
submitting from stale plans
forced residual cleanup
```

## Recommended Next Engineering Checkpoints

Possible next checkpoints:

```text
v1.17 Post-policy monitored session using the runbook
v1.18 Stale-plan prevention / max-plan-age enforcement
v1.19 Submit-mode preflight requiring explicit run-dir confirmation
v1.20 Paper-trading dashboard enhancement
```

## Final Operating Rule

When in doubt:

```text
do not submit
rerun a fresh dry run
review the execution plan
verify broker state
document the decision
```
