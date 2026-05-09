# 001-2026-05-09-adaptive-off-yieldcurve — HYPOTHESIS

**Iter:** 001 / 50 (loop)
**Slug:** adaptive-off-yieldcurve
**Date (UTC):** 2026-05-09
**n_configs:** 6 (≤ 8 protocol cap)
**cumulative_n_trials_global before:** 426
**cumulative_n_trials_global after:** 432

## Hypothesis

The study winner `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` (Sortino_lh56y
1.3246) loses 2 of 4 crisis windows: 2000_dotcom and **2022_rates**. The 2022
loss is mechanistic — when trend signal flips OFF, the strategy parks 100% in
ZROZ (25y zero-coupon STRIPS) precisely as the Fed begins its fastest hiking
cycle since the 1980s; ZROZ duration ~25y means a ~25× exposure to the parallel
rate shift, and the equity curve bleeds while equity-LETF is sidelined.

A *term-premium-aware* OFF-asset rotation — keep ZROZ when the curve is
upward-sloping (positive term premium, "bonds compensate for duration risk"),
swap to short-duration cash (BIL/CASHX) when the curve is flat or inverted —
should rescue 2022 without sacrificing 2008/2020 (where curves were positively
sloped and ZROZ provided strong negative-correlation alpha).

This is a Carver carry-style regime gate applied to the *defensive* leg only.
Trend signal (vote-of-K) controls equity exposure timing; carry/yield-curve
slope controls bond-vs-cash timing during defensive periods.

**Primary citation:** `[systematic_trading, ch.9 p.180-190]` — Carver carry
forecast framework (yield - financing-cost), here adapted as a regime gate
rather than continuous forecast magnitude.

**Secondary citations:**
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1 framework)
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
- `[leverage_for_the_long_run, p.5-6]` — vol gate context (inherited from winner signal stack)

## Configs

All configs share the trend ON signal `vote-of-2 of {SMA250, SMA100, vol_21d<40%,
AR(1)_30d>0}` on QLD (winner replica). Only the OFF leg varies.

Term-premium proxy = `10y CMT yield - 3m CMT yield` (in pp / decimal annual).

| # | Name | OFF rule | Description |
|---|---|---|---|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz_baseline` | always ZROZ | Winner replica (control) |
| 2 | `qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_ts000` | ZROZ if (10y - 3m) > 0.0pp else CASHX | Term-premium gate, threshold 0pp |
| 3 | `qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_ts050` | ZROZ if (10y - 3m) > 0.5pp else CASHX | Threshold 0.5pp |
| 4 | `qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_ts100` | ZROZ if (10y - 3m) > 1.0pp else CASHX | Threshold 1.0pp |
| 5 | `qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_ts150` | ZROZ if (10y - 3m) > 1.5pp else CASHX | Threshold 1.5pp (most conservative) |
| 6 | `qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_lvltrnd` | ZROZ if 10y < 252d-SMA(10y) else CASHX | Level-vs-trend (rate-falling regime) |

Configs differ in exactly one dimension at a time (threshold τ, except #6 which
swaps the regime definition entirely as a robustness probe). The threshold
sweep follows the protocol's "symmetric naming, single-axis" guidance.

## Datasets

Mirrors closed-study set for direct comparability:
- `lh_56y`: 1970-01-01 → 2026-04-30 (SPYSIM/QLDSIM/ZROZSIM/CASHX, 10y/3m CMT)
- `modern_1990`: 1990-01-01 → 2026-04-30 (eliminates pre-1990 synth uncertainty)
- `spy_real`: 2003-01-01 → 2026-04-30 (real SPY post-inception)
- `ndx_real`: 2010-02-01 → 2026-04-30 (real QQQ post-inception)

Note on early lh_56y window: 30y CMT only starts 1977-02-15. We use 10y - 3m
spread (both available 1962+), which is the more common "term premium" proxy in
Ilmanen-style literature anyway. Pre-1962 fallback is not needed (lh_56y starts
1970).

## Pre-registered KILL_LOOP conditions

- **KILL_LOOP #1 (success-tag):** if any config has Sortino_lh56y > 1.3746
  AND `winner_conditions_met=True` AND pct_time_above_benchmark_lh56y ≥ 0.95
  → record `beats_winner=true` (loop continues per protocol §"Beats-winner test").
- **KILL_LOOP #2 (decisive-fail):** if all 6 configs return Sortino_lh56y < 1.10
  → hypothesis dead (term-premium-aware OFF substantially harms vs winner's
  flat-ZROZ baseline; mark tier FAIL and skip family in next iters).
- **KILL_LOOP #3 (replica-sanity):** if config #1 (baseline replica)
  Sortino_lh56y differs from 1.3246 by > 0.05 absolute → engine drift; flag
  INCOMPLETE and trust comparative deltas across configs only (not absolute).

## Expected outcomes (pre-registration; honest band)

- **Sortino_lh56y range expected:** 1.10–1.45 across all 6 configs.
- **Best plausible scenario:** mid-threshold (ts050 or ts100) gains ~0.05–0.10
  Sortino over baseline by recovering 2022; loses ~0.02–0.04 elsewhere from
  rare false-flat-curve flips (e.g., 1989, 2000, 2006 brief inversions).
- **Plausible failure mode:** baseline beats all variants because (a) ZROZ's
  multi-decade alpha is dominated by 2008/2020 not 2022, and (b) any threshold
  introduces a slow lag (CMT yields update slowly) that mistimes regime flips.
- **WC compliance:** trend ON signal unchanged → pct_time_above_benchmark
  should hold ≥ 0.95 on lh_56y. WC failure would indicate the OFF mix is
  significantly worse than ZROZ-only on average (interesting but unexpected).
- **Beats-winner probability:** **~15%**. Crisis attribution rescue alone
  yields +2.5 pts (criterion 6) but Sortino edge needs real economic lift.
  Most realistic outcome: tier STRONG/PROMISING with sortino_edge_vs_winner in
  [-0.05, +0.10] band — useful negative result if no config beats; useful
  positive result if mid-threshold improves 2022 without 1980s drag.

## INCOMPLETE flags / caveats

- **Synth caveat:** lh_56y pre-1985 uses formula-derived QLDSIM/ZROZSIM
  (calibrated UGL synth not used here). Carry behavior pre-1985 not separately
  validated; 1985+ matches real-ETF era.
- **CMT yields:** sourced from `yfinance` ^TNX/^IRX (cached parquet); minor
  gaps on holidays handled via ffill.
- **CASHX (FFR proxy) as OFF:** acts as risk-free placeholder; real-money
  alternative would be SHV/BIL ETFs (post-2007). For lh_56y consistency we use
  CASHX. Expected impact: negligible (CASHX ≈ FFR ≈ SHV yield in non-crisis
  periods).
- **Tax/fees:** gross only this iter (matching study convention; net layer is
  monotonic shift downstream — doesn't affect rankings or `beats_winner` test).
- **No carry-driven ON signal modification.** Only OFF leg changes. Combining
  carry into ON gating (e.g. "ON only if equity carry positive") is reserved
  for a separate iter.

## Beats-winner test (frozen per protocol §"Beats-winner test")

```python
beats_winner = (
    sortino_lh56y > 1.3746              # 1.3246 + 0.05 anti-curve-fit margin
    and winner_conditions_met
    and pct_time_above_benchmark_lh56y >= 0.95
)
sortino_edge_vs_winner = sortino_lh56y - 1.3246
```

`winner_benchmark_sortino = 1.3246`, `winner_benchmark_iter =
"022-2026-05-06-T3d-extended-grid"`, `winner_benchmark_config =
"qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"`.
