# Iter 005 — HAA SmartStack

**Date:** 2026-04-27  
**Slug:** haa-smartstack  
**Status:** pre-committed single config, n_trials=1

---

## Hypothesis

Apply **Hybrid Asset Allocation (HAA)** (Keller & Keuning 2023, SSRN 4346906) on a
capital-efficient stacked-ETF offensive universe, plus a fixed 10% KMLMSIM sleeve.
HAA uses a single *canary asset* (VWOSIM) to determine monthly risk regime:
- **Risk-ON** (canary momentum > 0): hold top-2 offensive stacked assets, 45%+45%
- **Risk-OFF** (canary momentum ≤ 0): hold top-1 defensive asset at 90%
- **Always**: 10% KMLMSIM fixed (capital efficient, stacked)

Offensive assets (capital-efficient stacks):
| Synth | Formula | Notional |
|---|---|---|
| NTSXSIM | 0.90×SPYSIM + 0.60×IEFSIM − 0.50×CASHX | ~1.5× |
| NTSI-synth | 0.90×VEASIM + 0.60×IEFSIM − 0.50×CASHX | ~1.5× |
| NTSE-synth | 0.90×VWOSIM + 0.60×IEFSIM − 0.50×CASHX | ~1.5× |
| GDESIM | 90% S&P + 90% gold (cached) | ~1.8× |

Defensive assets: IEFSIM, BNDSIM, CASHX  
Canary: VWOSIM (raw, monthly avg of 1m/3m/6m/12m returns)  
Momentum formula: `(r1 + r3 + r6 + r12) / 4`

---

## Primary citation

- `[stocks_on_the_move, ch.6]` — Clenow momentum mechanics (dynamic vs static)
- `[ilmanen_expected_returns, ch.19]` — managed futures free-lunch sleeve
- `[leverage_for_the_long_run, p.40-60]` — return-stacking capital efficiency rationale
- `[advances_fin_ml, p.208-211/222-223/196-202/31-34]` — gates G1/G2/G6/G7
- HAA SSRN 4346906 — Keller & Keuning 2023 (supplementary, not in cache)

---

## Edge source (vs all three benchmarks)

**VT b&h** misses: (1) no downside protection — stays fully invested through crises;
(2) no stacking — 1× notional only; (3) no MF overlay.

**Plano C V3_1** misses: (1) no canary regime switch; (2) no stacking; (3) static weights.

**V_HYBRID+MF** misses: (1) no canary regime switch (always invested in equity factor);
(2) no stacking (1× notional on equity sleeve).

HAA SmartStack adds **all three** simultaneously: dynamic canary protection +
stacked 1.5× offensive notional + 10% MF always-on.

---

## Datasets

| dataset | window | effective start | binding ticker |
|---|---|---|---|
| educational | 1994-05 → 2026-04 | 1995-05 (after 12m lookback) | VWOSIM (1994-05-04) |
| vt_real | 2008-06 → 2026-04 | 2009-06 (after 12m lookback) | VWOSIM available |
| ndx_real | 2010-02 → 2026-04 | 2011-02 (after 12m lookback) | VWOSIM available |

---

## Pre-committed kill criteria

1. Educational Sharpe ≤ 1.00 → fail (same bar as iter 002 WINNER)
2. Any WF window MDD (G3' adapted) > VTSIM\_window\_MDD × 1.45 → fail

---

## Expected budget

- Configs: **1** (single pre-committed)
- n_trials: 1
- G3' adapted gate (notional_factor ≈ 1.45 when offensive)
- Wall-time estimate: ~10 min

---

## Implementation plan

1. Load testfolio parquet cache
2. Compute stacked daily return series: NTSXSIM, NTSI-synth, NTSE-synth
3. Cumulate to price series for monthly momentum computation
4. Monthly HAA: canary → regime → rank → allocate + KMLMSIM overlay
5. Gate battery G1-G7 (G3 nominal + G3' adapted for notional_factor=1.45)
6. Cross-lib numpy reference (G7)
7. Score via scoring.py
8. Save results.json, verdict.json
9. plot_helper.py → PNG charts
