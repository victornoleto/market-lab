# Iteration 003 — Capital-Efficient Global Factor-Tilted Static Portfolio

**Slug**: `capital-efficient-static`
**Date**: 2026-04-26
**Origin**: USER_SPECIFIED (Tier 0 from BASE_MEMORY.md Promising Directions)

---

## Hypothesis

A single-config static monthly-rebalanced portfolio combining nine sleeves
captures three independent return premia that VT, Plano C V3_1, and V_HYBRID+MF
each partially miss: **return-stacking** (RSSB, RSST, GDE deliver ~1.4-1.5×
notional on 1× capital via futures overlay), **factor breadth** across five
distinct value/momentum sleeves on four regions, and **diversifier load** (~25%
managed-futures + gold combined, vs 10-12% in benchmarks).

The hypothesis is that combining return-stacking with genuine factor tilts
(small-cap value, momentum across US/intl/EM) produces a long-window Sharpe
decisively above the three benchmarks while compressing MDD via diversification.
Pre-committed single config (no grid) → G1 PBO trivially passes.

## Primary citations

- Return stacking / capital efficiency: `[risk_parity, ch.5]`,
  `[leverage_for_the_long_run, p.40-60]`
- Small-cap value premium: `[advances_fin_ml, ch.10]` (Fama-French / DFA /
  Avantis methodology empirical evidence)
- Managed futures "free lunch": `[ilmanen_expected_returns, ch.19]`
- Momentum factor: `[stocks_on_the_move, p.21-30]`
- Multi-asset diversification: `[risk_parity, ch.3-5]`

## Edge source vs benchmarks

VT b&h is 100% equity passive (zero alternatives, zero leverage).
Plano C V3_1 v3.5 has ~10% MF + factor tilt but no return-stacking.
V_HYBRID+MF is similar with 10% MF, capped at ~1.0× notional.
This portfolio's edge: **stacking** (RSSB+RSST+GDE → ~1.4-1.5× notional),
**factor breadth** (5 distinct value/momo sleeves across regions), and
**diversifier load** (~25% combined MF+gold vs 10-12% in benchmarks).

## Exact weights (USER_SPECIFIED — DO NOT MODIFY)

| Ticker | Weight | Synth / cache |
|---|---|---|
| RSSB | 25% | RSSBSIM (direct: 100% VT-eq + 100% IEF) |
| RSST | 15% | SPYSIM + KMLMSIM − CASHX (return-stack formula) |
| AVUV | 10% | VBRSIM (US small-cap value proxy) |
| AVDV | 7% | VSSSIM (intl dev small-cap proxy) |
| AVEM | 8% | VWOSIM (EM proxy; Avantis tilt premium ~0.3%/y, undocumented gap) |
| SPMO | 8% | SPYSIM (US momentum proxy; momentum premium ~1-2%/y undocumented) |
| IDMO | 7% | VEASIM (intl momentum proxy) |
| GDE | 12% | GDESIM (direct: 90% SPY + 90% gold) |
| KMLM | 8% | KMLMSIM (direct) |

**Expanded underlying weights (after expanding RSST stacking):**

| Component | Effective weight | Note |
|---|---|---|
| RSSBSIM | 0.25 | direct |
| SPYSIM | 0.23 | 0.15 (RSST) + 0.08 (SPMO) |
| KMLMSIM | 0.23 | 0.15 (RSST) + 0.08 (KMLM direct) |
| CASHX | −0.15 | RSST stacking offset |
| VBRSIM | 0.10 | AVUV proxy |
| VSSSIM | 0.07 | AVDV proxy |
| VWOSIM | 0.08 | AVEM proxy |
| VEASIM | 0.07 | IDMO proxy |
| GDESIM | 0.12 | GDE direct |

Sum of positive weights: 1.15; net (−CASHX): 1.00.
Effective notional exposure: ~1.45× (RSSB 2×, RSST 2×, GDE 1.8× vs nominal).

## Datasets to test

| dataset | window | binding constraint |
|---|---|---|
| educational | 1995-01-01 → 2026-04-24 (~31y) | VSSSIM / VWOSIM start 1994-12 |
| vt_real | 2008-06-01 → 2026-04-24 (~17y) | standard |
| ndx_real | 2010-02-01 → 2026-04-24 (16y) | standard |

Note: educational benchmark is VTSIM over the same 1995-2026 window
(Sharpe 0.5533, CAGR 8.80%, MDD 58.35%), not the 56y window in the
default BENCHMARKS dict.

## Pre-committed kill criteria

Single observable: if 32-y synth Sharpe ≤ V_HYBRID+MF (0.743) on vt_real → FAIL.
If MDD > Plano C V3_1 (52.43%) on any single dataset → FAIL.

## Implementation plan

1. `backtest.py`: build RSST synthetic, assemble weighted daily return
   series, monthly rebalance, compute metrics + all 7 gates.
2. G7 cross-lib: numpy-pure reference replicating same weighted sum.
3. For G7, the numpy version must reproduce ±3pp CAGR vs pandas version.
4. Score via `scoring.py` with custom educational benchmark (1995-2026 VTSIM).
5. Produce `results.json` and `verdict.json`.

## Expected budget

- Configs: 1 (single pre-committed spec, no grid)
- n_trials: 1 (cumulative: 19 + 1 = 20)
- Wall-time: ~10 min
