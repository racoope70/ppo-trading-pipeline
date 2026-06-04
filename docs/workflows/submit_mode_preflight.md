# v1.19 Submit-Mode Preflight / Explicit Run-Dir Confirmation

Status: Active safety control
Scope: Alpaca PPO paper-trading submit mode

## Purpose

Prevent accidental `--submit-orders` use against the wrong run directory.

This checkpoint adds an explicit run-directory confirmation requirement before submit mode can run.

## Rule

Submit mode requires:

```text
--confirm-run-dir <same value as --run-dir>
```

The normalized confirmation value must match the normalized run directory.

## Correct Submit Pattern

Example for a filtered single-order directory:

```bash
python -m src.paper_trading.paper_trade_loop \
  --run-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_buy \
  --submit-orders \
  --max-plan-age-minutes 90 \
  --confirm-run-dir reports/paper_trading_dry_runs/v_next_single_order_AMD_buy
```

## Blocked Submit Patterns

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

Both are required for controlled submit mode.

## Operating Policy

Do not submit from latest unless the runbook explicitly allows it and the plan has exactly one reviewed order.

Prefer submitting from a named filtered directory such as:

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
