# Iter 018 — Hypothesis: C.1 — Antonacci GEM cross-class top-K momentum

## Hypothesis (one paragraph)

**Pivot to a qualitatively different mechanism**: instead of a static
capital-efficient stack (iter 011 family) or constant-weight factor overlay
(iter 013-016), test **Gary Antonacci's Global Equities Momentum (GEM)**
style — monthly top-K selection across a multi-asset universe by trailing
12-1m momentum. Universe: SPYSIM (US large), QQQSIM (US tech), VTSIM
(global), VEASIM (intl developed), VWOSIM (EM), TLTSIM (LT Treasury),
GLDSIM (gold), KMLMSIM (managed futures). Selection: equal-weight top-K
each month, where K ∈ {1, 2, 3}. The hypothesis: dynamic asset-class
selection captures regime shifts that static stacks miss (equity in
2010-2024, gold in 2020+, bonds in 2009-2020, MF in 2022 rates spike) —
a structurally different alpha source than capital-efficient stacking.

## Primary citation

- `[stocks_on_the_move, ch.6, p.21-30]` — Clenow: cross-sectional
  momentum is the canonical mechanism; equal-weight top-K avoids
  optimization overfit.
- Antonacci 2014 *Dual Momentum Investing*: GEM is the textbook variant
  (top-1 monthly across SPY/EFA/AGG with abs-mom AGG fallback).
- `[risk_parity, ch.5]` — Carlson: contrast with static stacking.
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Edge source (1 sentence)

avg(SPY, VT) buy-hold misses the regime-rotation mechanism: top-K monthly
momentum captures the dominant asset class of each year, switches when
the dominant class changes — structurally different from any static
allocation.

## Datasets to test

- `lh_56y`: bottleneck depends on universe. **6-asset (no EM)** = SPYSIM
  bottleneck 1986+ (~40y eff). **7-asset (with EM)** = VWOSIM bottleneck
  1994+ (~32y eff). KMLMSIM via splice covers from 1970+.
- `vt_real` (2008-06+) — full data on all assets.
- `ndx_real` (2010-02+) — full data.

## Pre-committed kill criteria

**KILL #1**: Best-of-grid loses iter 011 on ≥ 2 of 3 datasets → Antonacci
GEM is structurally subordinate in this universe; close C.1.

**KILL #2**: Top-K=1 dominates top-K=2,3 on all datasets (concentration
beats diversification) → suggests overfitting to the dominant asset of
each window; revisit with K=2 fixed in iter 019.

## Configs (pre-committed grid — 4 configs)

| config | universe | K | abs-mom fallback | rationale |
|---|---|---:|---|---|
| `gem_5asset_K2`  | SPY/QQQ/EFA/TLT/GLD | 2 | TLTSIM if all neg-mom | classic Clenow universe |
| `gem_6asset_K2`  | SPY/QQQ/EFA/TLT/GLD/KMLM | 2 | KMLMSIM (crisis-alpha) | adds MF crisis sleeve |
| `gem_5asset_K3`  | SPY/QQQ/EFA/TLT/GLD | 3 | TLTSIM | more diversified |
| `gem_7asset_K2`  | SPY/QQQ/EFA/EEM/TLT/GLD/KMLM | 2 | KMLMSIM | full universe (1994+ eff) |

Notes:
- "EFA" → VEASIM (intl developed proxy)
- "EEM" → VWOSIM (EM proxy)
- "TLT" → TLTSIM
- "GLD" → GLDSIM
- "KMLM" → KMLMSIM (with lh_56y splice)
- abs-mom fallback: if best top-K assets have negative trailing 12-1m
  return, fallback to abs-mom asset (TLTSIM as classic safe-haven, or
  KMLMSIM for crisis-alpha variants).

**Selection rule**: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets.
**N_CONFIGS = 4** → DSR n_trials = 4.

## Implementation plan

New backtest pattern (dynamic, not static). Skeleton:
1. Load testfolio prices.
2. Compute monthly returns per asset; compute trailing 12-1m return per asset.
3. Each month-end: rank assets by 12-1m return, select top-K, equal-weight.
   If avg(top-K mom) < 0, switch to abs-mom fallback.
4. Hold portfolio for 1 month (no daily rebalance), then re-rank.
5. Convert monthly returns to daily by holding the daily returns of the
   selected assets through the month (not approximated monthly returns).
6. Standard 7-gate battery + scoring on the daily series.

Pytest baseline (461 tests) unchanged — new logic lives in iter 018 only.

## Expected budget

- Implementation: ~25 min (new dynamic backtest).
- Run wall-time: ~5-8 min.
- Plots + report: ~10 min.
- Total: ~45 min.

## Probability assessment (honest)

- **P(strict ADVANCE vs iter 011)**: ~30% — iter 079 archive (multi-asset
  top-K cross-class momentum) was the only strict winner in the 78-iter
  strategy_hunt_loop with Sharpe 1.094 on SPY-Tiingo 17y. GEM is a
  simplification of iter 079.
- **P(positive signal but no ADVANCE)**: ~25% — likely if GEM helps live
  windows but lh_56y bottlenecked by 1986+ coverage.
- **P(tier WINNER, no ADVANCE)**: ~20%.
- **P(STRONG, no winner conds)**: ~15%.
- **P(FAIL/kill fires)**: ~10%.
