# Phase 7B — Multi-Asset Portfolio of SMA200 Rotations (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Round order note:** Phase 7 round runs 7A → 7B → 7C → 7D → 7E → (7F) → 8.

## Question

Phase 4's binding gate is G3 walk-forward, and Phase 6C showed the single-asset
timing cost is structural in bull windows. The untested family is
**cross-instrument diversification of the rotation itself**: an equal-weight
portfolio of N single-asset Gayed rotations, where each leg times its own index.
Diversification across imperfectly correlated instruments is "the best source
of additional return" for a fixed rule `[systematic_trading, p.42]`, with the
risk reduction quantified by the instrument diversification multiplier
`[systematic_trading, p.170-171]`; cross-asset balance is the same logic the
RSC anchor uses `[risk_parity, p.80-81]`. Hypothesis under test: averaging the
rotation across underlyings smooths the OOS windows enough to lift
**walk-forward consistency** versus the same-window single-leg rotations.

**Grammar is uniform by design** — SMA200, one shared target leverage, one
shared risk-off (ZROZ), one shared vol-gate choice across all legs
`[leverage_for_the_long_run, p.13]`. No per-leg recipe fitting: per-leg
window/MA-type tuning is exactly the data-mined shape this phase refuses to
inherit `[advances_fin_ml, p.208-211]`.

## Mechanism (one family — EW portfolio of single-asset rotations)

- Leg rule (identical for every leg): `P_leg.shift(1) > SMA200(P_leg).shift(1)`
  AND optional shared vol gate (`RV63(P_leg) <= 40%`) → ladder risk-on at the
  shared `L`; else `100% ZROZ`. Weekly cadence, lag-through-CASHX, per-leg
  weight frames built with the standard `build_weekly_lagged_weights`.
- Portfolio target = equal-weight mean of the leg weight frames; the EW is
  re-trued at every weekly target change of any leg (single taxable account,
  `AnnualDarfEngine`, turnover taxed honestly).
- Legs with no cached leveraged proxy (IWM, XLK, GLD) use in-memory synthetic
  2x series `r_2x = 2*r_u - r_cash - 0.0095/252`
  (`lrs/lib/backtest.synth_leveraged_returns`)
  `[leverage_for_the_long_run, p.16, fn.22-23]`; SPY/QQQ legs use the cached
  `SSOSIM`/`QLDSIM`. Cache untouched (Phase 6D precedent). DISCLOSED LIMITATION:
  the synthetic understates real-ETF tracking frictions; results carry a
  synthetic-leverage disclaimer.

## Pre-registered grid — 72 rows (+72 to the n_trials ledger → 4077 + 72 = 4149)

| Axis | Values | Anchor |
|---|---|---|
| Composition | `EW5 = {SPY,QQQ,IWM,XLK,GLD}`; `EW4 = {SPY,IWM,XLK,GLD}` (no QQQ); `EW3 = {SPY,QQQ,GLD}` | EW5 = broadest cached set; EW4 removes the PBO/DSR-rejected QQQ; EW3 = minimal cross-asset (equity x2 + gold) |
| Shared target leverage | `1.75, 2.00` | the two Phase 2/4 headline levels |
| Shared vol gate | `none`, `RV63 <= 40%` | Phase 2 estimator, computed per leg on its own underlying |
| lag | `0..5` | restart convention |

Risk-off fixed at `100% ZROZ` (uniform; from the Phase 2 sleeve set).

**Windows (recorded, consequence of data):** each composition runs on the
common `dropna` window of its assets — EW5/EW3 are QQQ-limited (1986+, 11 WF
windows); EW4 is IWM-limited (1979+, ~13 WF windows). All comparisons are
intra-window; WF is compared as a ratio because window counts differ.

**Benchmarks (non-trial):** per composition, the EW buy-and-hold of the same
underlyings (no rebalance, after-tax = final-liquidation DARF only — the strong
no-timing benchmark, consistent with the 6A-revised tax convention). The
standalone-leg controls below double as the same-window single-asset
comparators.

**Paired controls (non-trial, computed for screen rows only):** for the best
trial row of each composition, every leg re-run as a STANDALONE rotation with
the same `L`/vol/lag on the same window, WF measured vs its own underlying B&H
after-tax.

**Built-in sanity (non-trial):** the degenerate composition `{SPY}` at
`L=2.00 / ZROZ / RV63<=40%` must reproduce `phase04.simulate_returns` for the
matching config byte-for-byte (max abs diff reported).

## Pre-registered screen (per composition, on the best trial row by WF ratio, tie-break Calmar)

1. WF beat **ratio** (vs the composition's EW-underlying B&H benchmark)
   **strictly greater** than the max standalone-leg WF ratio (each leg vs its
   own underlying) at the same `L`/vol/lag on the same window.
2. After-tax CAGR **strictly greater** than the EW-underlying B&H benchmark.
3. Portfolio MDD ≥ −50% (round constraint).

All three → diagnostic SUCCESS (feeds 7F). Any miss → honest FAIL. The G3-style
≥75% WF level is reported, not claimed. No deployment, no paper-trade label, no
mandate change `[advances_fin_ml, p.208-211]`.

## Outputs

`lrs/results/phase07b_multiasset_portfolio.csv`, `REPORT.md`, plots (equity/DD
vs EW benchmark, WF ratio comparison portfolio vs legs, frontier,
fraction-of-legs-risk-on series), `tests/test_lrs_phase07b.py`.
