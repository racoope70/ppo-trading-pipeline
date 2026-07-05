# v1.19 Submit-Mode Preflight / Explicit Run-Dir Confirmation

Status: Historical / future-only safety control
Scope: Alpaca PPO paper-trading submit-mode safety reference

## Current Authorization Boundary

Current source-of-truth authorization:

```text
paper_orders = NOT_AUTHORIZED
live_orders = NOT_AUTHORIZED
controlled_submit = BLOCKED
NO_SUBMIT = DEFAULT
```

This document is not an active submit-mode runbook. It is retained only as historical / future-only safety context for explicit run-directory confirmation.

Do not run `--submit-orders` from this document unless a later sealed checkpoint explicitly authorizes controlled submit.

## Purpose

Document the historical safety control intended to prevent accidental `--submit-orders` use against the wrong run directory.

This checkpoint added an explicit run-directory confirmation requirement for historical controlled-submit testing. Current v3.06 state blocks controlled submit.

## Rule

Submit mode requires:

```text
--confirm-run-dir <same value as --run-dir>
```

The normalized confirmation value must match the normalized run directory.

## Historical / Future-Only Submit Pattern

Historical example for a filtered single-order directory. Do not run under the current v3.06 state:

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_buy \
  --submit-orders \
  --max-plan-age-minutes 90 \
  --confirm-run-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_buy
```

## Blocked Submit Patterns

These remain blocked examples. The current state also blocks the otherwise “correct” submit pattern above.

Missing confirmation:

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_buy \
  --submit-orders \
  --max-plan-age-minutes 90
```

Wrong confirmation:

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_buy \
  --submit-orders \
  --max-plan-age-minutes 90 \
  --confirm-run-dir reports/paper_trading_dry_runs/latest
```

## Relationship to v1.18

v1.18 prevents stale-plan submission with:

```text
--max-plan-age-minutes 90
```

v1.19 prevents wrong-directory submission with:

```text
--confirm-run-dir <exact run dir>
```

Both would be required for a future separately authorized controlled-submit checkpoint. Controlled submit is currently blocked.

## Operating Policy

Do not submit from any run directory under the current v3.06 state.

## Backlog Note: Broker-Read Fail-Closed Hardening

Broker-read fail-closed hardening remains a future controlled-submit backlog item only.

This note does not authorize broker API calls, broker account reads, paper orders, live orders, or controlled submit.

If a later sealed checkpoint ever reconsiders controlled submit, broker-read failures should fail closed before order planning or submission can continue.

Historical / future-only reference: if a later sealed checkpoint ever authorizes controlled submit, named filtered directories are safer than `latest`, such as:

```text
reports/paper_trading_dry_runs/v_next_single_order_<SYMBOL>_<SIDE>
```

## Failure Response

If confirmation fails:

```text
stop
verify the intended run directory
rerun the no-submit chain if needed
rerun risk controls
rerun checklist
manually review again
```
