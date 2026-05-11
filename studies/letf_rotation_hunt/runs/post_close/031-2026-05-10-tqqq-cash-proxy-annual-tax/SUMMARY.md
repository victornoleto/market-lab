# Iter 031 — TQQQ/CASH proxy plus annual DARF tax

**Iter:** `031-2026-05-10-tqqq-cash-proxy-annual-tax`
**Primary citation:** `[leverage_for_the_long_run, ch.4-5, p.40-60]`
**Cumulative global trials:** 614

## TL;DR

This iteration tests the execution concern that exiting turbo requires selling
TQQQ and buying QLD, creating realized P&L that is taxed annually at 15% if the
calendar-year net is positive. The fair panel also taxes T3d-K2 state changes and
keeps SPY/NDX buy-and-hold untaxed because there are no interim sale events.

Proxy tested:

| State | Weight |
|---|---:|
| OFF | 100% ZROZ |
| ON normal | 100% QLD |
| ON rearm/turbo | 80% TQQQ + 20% CASHX |

Tax model: all realized sale P&L is netted by calendar year; positive annual net
profit is taxed at 15% on the first trading day of the next year. Losses carry
forward.

## Results

| Config | Sortino | CAGR | MDD | End equity vs taxed T3d-K2 | PBO | DSR global | Score | Tier |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `t3d_k2_gross_reference` | 1.3246 | 31.09% | -64.50% | 8.602x | 0.0119 | 3.42e-03 | 76.5 | STRONG |
| `t3d_k2_state_annualtax` | 1.0826 | 24.24% | -59.43% | 1.000x | 0.0119 | 4.27e-02 | 71.5 | PROMISING |
| `iter030_gross_reference` | 1.3839 | 36.68% | -55.48% | 46.164x | 0.0119 | 1.49e-03 | 79.5 | STRONG |
| `spy_buyhold_static_notax` | 0.9574 | 11.47% | -55.14% | 0.013x | 0.0119 | 1.16e-01 | 36.0 | NEAR_FAIL |
| `ndx_qqq_buyhold_static_notax` | 0.9431 | 14.59% | -82.97% | 0.038x | 0.0119 | 1.44e-01 | 71.5 | PROMISING |
| `t35d60_tqqq80_cash20_proxy_daily_gross` | 1.3310 | 31.84% | -65.64% | 10.885x | 0.0119 | 3.10e-03 | 76.5 | STRONG |
| `t35d60_tqqq80_cash20_proxy_daily_annualtax` | 1.1018 | 25.02% | -59.18% | 1.285x | 0.0119 | 3.60e-02 | 71.5 | PROMISING |
| `t35d60_tqqq80_cash20_proxy_state_gross` | 1.2099 | 28.40% | -58.51% | 3.770x | 0.0119 | 1.24e-02 | 71.5 | PROMISING |
| `t35d60_tqqq80_cash20_proxy_state_annualtax` | 1.0966 | 25.05% | -59.29% | 1.299x | 0.0119 | 3.76e-02 | 71.5 | PROMISING |

## Implementation Drag

| Comparison | CAGR | Sortino | End equity vs taxed T3d-K2 |
|---|---:|---:|---:|
| Iter 030 gross reference | 36.68% | 1.3839 | 46.164x |
| T3d-K2 state-change annual-tax | 24.24% | 1.0826 | 1.000x |
| TQQQ/CASH proxy state-change gross | 28.40% | 1.2099 | 3.770x |
| TQQQ/CASH proxy state-change annual-tax | 25.05% | 1.0966 | 1.299x |
| TQQQ/CASH proxy daily-rebalance annual-tax | 25.02% | 1.1018 | 1.285x |
| SPY buy-and-hold static no-tax | 11.47% | 0.9574 | 0.013x |
| NDX/QQQ buy-and-hold static no-tax | 14.59% | 0.9431 | 0.038x |

T3d-K2 tax paid: `$11331694.62` on initial `$10000` scale across `31` tax years.
T3d-K2 realized sale events recorded: `366`.

State-change tax paid: `$14692114.92` on initial `$10000` scale across `31` tax years.
State-change realized sale events recorded: `378`.

Daily-rebalance stress tax paid: `$14477720.88` with `801` realized sale events.

## Verdict

`kill_rule_status`: **FIRES**.

The annual-tax proxy remains research-only and does not authorize deploy. It is
an execution-realism diagnostic for a future monitoring app; mandate §1 remains
100% Plano C.

## Files

- `verdict.json`
- `per_config_metrics.csv`
- `gates_pass_fail.csv`
- `annual_tax_events_state_change.csv`
- `realized_sale_events_state_change.csv`
- `annual_tax_events_t3d_k2.csv`
- `realized_sale_events_t3d_k2.csv`
- `annual_tax_events_daily_rebalance.csv`
- `realized_sale_events_daily_rebalance.csv`
- `proxy_target_weights.csv`
