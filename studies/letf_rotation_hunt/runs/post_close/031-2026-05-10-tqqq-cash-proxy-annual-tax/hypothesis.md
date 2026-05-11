# Iter 031 — TQQQ/CASH proxy plus annual DARF tax for iter 030

**Iter:** `031-2026-05-10-tqqq-cash-proxy-annual-tax`
**Phase:** 4 — execution realism check for iter 030 winner
**Primary citation:** `[leverage_for_the_long_run, ch.4-5, p.40-60]`

## Hypothesis

Iter 030's research winner uses `T35D60 + LRS1.20`. Before any monitoring app
or deploy-like workflow, test whether the no-margin implementation proxy remains
economically viable after Brazilian annual foreign-investment tax drag.

## Mechanism Tested

Use the same T3d-K2 master signal and T35D60 rearm gate as iter 030, but replace
the abstract leverage overlay with executable ETF weights:

| State | Proxy weight |
|---|---:|
| OFF | 100% ZROZ |
| ON normal | 100% QLD |
| ON rearm/turbo | 80% TQQQ + 20% CASHX |

The proxy approximates `1.20 x QLD ~= 2.4 x NDX` without margin, since TQQQ is
approximately 3x NDX and `0.80 * 3.0 = 2.4`.

## Tax Model

Annual Brazilian foreign-investment tax model under Lei 14.754/2023:

1. Track realized gains/losses on every sale event during calendar year `Y`.
2. On the first trading day of `Y+1`, settle the net result of year `Y`.
3. If annual realized net P&L is positive, deduct `15% * net_profit` from equity.
4. If annual realized net P&L is negative, carry the loss forward.

This is more realistic than monthly swing-trade DARF and directly tests the user
concern: exiting turbo requires selling TQQQ and buying QLD, which can realize
taxable gains.

## Kill / Read Rules

- If the annual-tax proxy loses the iter 030 performance edge versus T3d-K2, the
  no-margin implementation is not equivalent to the gross research result.
- If the proxy remains above T3d-K2 but materially below iter 030 gross, report
  the tax/implementation drag as mandatory app caveat.
- If annual tax produces large realized drag concentrated in turbo exits, future
  work must test alternate execution routes before any monitor/deploy app.

## Scope

This iter is an execution-realism diagnostic, not a new broad hunt. It should not
change mandate §1: capital remains 100% Plano C, no automatic deploy.
