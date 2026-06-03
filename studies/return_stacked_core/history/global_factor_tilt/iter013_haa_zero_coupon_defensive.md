# Iter 013 Final Report — HAA SmartStack + ZROZSIM Defensive

**Date**: 2026-04-27  
**Status**: WINNER 90/100 — Kill 1 TRIGGERED (no Sharpe advance vs iter 009 Pareto frontier)  
**Pareto note**: New CAGR frontier (+2.46pp) at cost of −0.109 Sharpe and +8.17pp MDD vs iter 009.

---

## TL;DR

Adding ZROZSIM (25y zero-coupon bond) to HAA's defensive palette achieves a **formal WINNER
90/100** — all 5 strict conditions met, 7/7 gates on all 3 datasets, 100% rolling-window
robustness. However, Kill 1 triggers: edu Sharpe 1.0113 < 1.120 (iter 009 Pareto frontier).

ZROZSIM's extraordinary crisis alpha (2008: +63.78%, 2020: +22.56%) raises portfolio CAGR by
+2.46pp on educational but simultaneously increases daily variance proportionally: 25y duration =
high rate sensitivity = high daily vol. The Sharpe formula penalizes this variance, producing
**lower Sharpe despite higher CAGR**. This is the CAGR–Sharpe tradeoff frontier at its most
explicit: iter 013 is the highest-CAGR winner found (16.35% edu), while iter 009 remains the
highest-Sharpe winner (S=1.120).

HAA's adaptive mechanism correctly avoids ZROZSIM in 2022 (selects CASHX +2.05% instead of
ZROZSIM −39.26%), so the 2022 inflationary bear causes no regression relative to iter 009.
The variance increase comes from ZROZSIM's large daily swings in ALL defensive periods, not
just crises.

---

## Headline metrics

| metric | iter 013 (edu) | iter 009 (edu) | Δ vs 009 | VT b&h (edu) |
|---|---|---|---|---|
| Sharpe     | 1.0113 | **1.1200** | **−0.109** | 0.546 |
| CAGR       | **16.35%** | 13.89% | **+2.46pp** | 8.64% |
| MDD        | 28.98% | **20.81%** | +8.17pp | 58.35% |
| Gates      | 7/7 | 7/7 | = | — |
| Kill 1     | TRIGGERED | N/A | — | — |

| dataset | Sharpe | CAGR | MDD | Gates |
|---|---|---|---|---|
| educational (~31y) | 1.0113 | **16.35%** | 28.98% | **7/7** |
| vt_real (~17y)     | 1.0015 | **15.36%** | 18.66% | **7/7** |
| ndx_real (~16y)    | 0.9003 | **13.25%** | 18.66% | **7/7** |

---

## Gate battery

| gate | educational | vt_real | ndx_real |
|---|---|---|---|
| G1 PBO      | PASS (n=1) | PASS | PASS |
| G2 DSR      | PASS p=9.17e-09 | PASS p=1.89e-05 | PASS p=2.13e-04 |
| G3 nominal  | PASS (8/8, max 23.64%) | PASS (8/8, 18.66%) | PASS (8/8, 18.66%) |
| G3' adapted | PASS (max_ref 79.81%) | PASS (49.63%) | PASS (49.63%) |
| G4 OOS      | PASS S=0.938 | PASS S=1.047 | PASS S=1.041 |
| G5 FWD 2020+| PASS S=0.992 | PASS S=0.992 | PASS S=0.992 |
| G6 Bootstrap| PASS CI_low=0.514 | PASS CI_low=0.417 | PASS CI_low=0.236 |
| G7 Cross-lib| PASS diff=0.30pp | PASS diff=0.19pp | PASS diff=0.06pp |
| **Total**   | **7/7** | **7/7** | **7/7** |

---

## Winner conditions

| condition | result | detail |
|---|---|---|
| 1. Sharpe edge ≥ bm+0.10 on ≥ 2/3 | **PASS** | edu ✓ (+0.249), vt ✓ (+0.388), ndx ✗ (−0.058 vs QQQ) |
| 2. 7-gate battery | **PASS** | 7/7 / 7/7 / 7/7 |
| 3. DSR worst p < 0.05 | **PASS** | worst p=2.13e-04 |
| 4. CAGR ≥ 0.8×bm on ≥ 2/3 | **PASS** | edu ✓ 16.35% > 7.99%, vt ✓ 15.36% > 7.04%, ndx ✗ 13.25% < 15.35% |
| 5. MDD ≤ bm+5pp on ≥ 2/3 | **PASS** | edu ✓ 28.98% vs 63.35%, vt ✓ 18.66% vs 59.62%, ndx ✓ 18.66% vs 40.12% |

All 5 conditions met → **formal WINNER** ✓

---

## Scoring

| criterion | points | max | note |
|---|---|---|---|
| Sharpe edge | 20 | 25 | 2/3 datasets beat bm+0.10 (ndx QQQ 0.958 hard to beat) |
| Gates | 25 | 25 | 7/7 × 3 datasets + cross-dataset bonus |
| DSR | 15 | 15 | worst p=2.13e-04 << 0.05 |
| CAGR floor | 10 | 15 | edu ✓ vt ✓ ndx ✗ |
| MDD ceiling | 15 | 15 | all 3 pass comfortably |
| Robustness | 5 | 5 | 26/26 rolling-5y positive (100%) |
| **Total** | **90** | **100** | **WINNER** |

---

## Kill criterion

| criterion | result |
|---|---|
| Kill 1 — edu Sharpe ≤ 1.120 (must beat iter 009 Pareto frontier) | **TRIGGERED** (1.0113 < 1.120) |
| Kill 2 — any WF G3' fail | NOT triggered |

Kill 1 triggered: iter 013 does NOT advance the Sharpe Pareto frontier. The strategy is
formally a WINNER but is **superseded by iter 009 on risk-adjusted return (Sharpe)**.

---

## Robustness

- 26/26 rolling 5-year windows with positive Sharpe (100%)
- Min rolling Sharpe: 0.624 (slightly below iter 009's 0.630)
- Max rolling Sharpe: 1.350 (below iter 009's 1.530)
- G5 FWD post-2020 Sharpe: 0.992 (vs iter 009's 1.207 — lower recent Sharpe)

The slightly lower recent-period Sharpe (0.992 vs 1.207) reflects that the post-2020 period
includes 2022, where ZROZSIM underperformed defensively relative to iter 009's defensive.
However, 0.992 > 0 → G5 still passes.

---

## Pareto analysis vs all winners

| iter | slug | Sharpe (edu) | CAGR (edu) | MDD (edu) | Pareto status |
|---|---|---|---|---|---|
| **009** | haa-gold-sleeve | **1.120** | 13.89% | **20.81%** | **Sharpe frontier** |
| 005 | haa-smartstack | 1.112 | 14.14% | 20.91% | superseded by 009 on Sharpe |
| **013** | haa-zero-coupon | 1.011 | **16.35%** | 28.98% | **CAGR frontier** |
| 002 | fixed-momentum-k2 | 0.991 | 12.0% | 23.4% | superseded |
| 010 | vaa-g3-pure-equity | 0.981 | 10.28% | 18.91% | Kill 1 triggered, Kill 2 ok |
| 004 | momentum-mf-sleeve | 0.885 | 9.51% | **20.77%** | superseded |

Iter 013 is Pareto-non-dominated vs iter 009 on CAGR alone (16.35% vs 13.89%), but is
Pareto-dominated on Sharpe AND MDD by iter 009. For retirement planning with max CAGR as
primary objective, iter 013 is relevant; for Sharpe-maximization, iter 009 wins.

---

## Mechanism analysis: why CAGR goes up but Sharpe goes down

**ZROZSIM adds large positive return outliers in crisis defensive periods:**
- 2008: ZROZSIM +63.78% vs IEFSIM +17.07% → HAA selects ZROZSIM → +46pp for that defensive year
- 2020: ZROZSIM +22.56% vs IEFSIM +9.50% → HAA selects ZROZSIM → +13pp for that defensive year

**But ZROZSIM also adds large daily variance:**
- ZROZSIM duration = 25y → 2.5× more rate sensitivity than IEF (7-10y)
- Daily vol of ZROZSIM ≈ 3× daily vol of IEFSIM (estimated)
- Sharpe formula: mean / stddev × sqrt(252) → higher stddev from ZROZSIM in defensive periods
  reduces Sharpe even when mean is higher

**2022 confirms adaptive protection works:**
- HAA selected CASHX (+2.05%) in 2022 → avoids ZROZSIM crash (−39.26%)
- G5 FWD post-2020 Sharpe = 0.992 → positive, but lower than iter 009's 1.207
- The lower recent Sharpe reflects transition periods where HAA was briefly in ZROZSIM
  before CASHX became the top defensive choice

**Net effect:** CAGR rises ~2.5pp (good for CAGR-maximizing investors) but Sharpe falls
~0.11 (bad for Sharpe/MDD-focused investors). The ZROZSIM-vs-IEFSIM Sharpe ratio tradeoff:
- IEFSIM Sharpe ≈ 0.6 (balanced, moderate vol)
- ZROZSIM Sharpe ≈ 0.4 (high vol, high return — Sharpe lower despite higher return)

Holding ZROZSIM in defensive reduces the defensive period Sharpe contribution, pulling down
the full-period portfolio Sharpe.

---

## Long-window comparison vs mission benchmarks

| strategy | Sharpe | CAGR | MDD | source |
|---|---|---|---|---|
| **iter 013 HAA+ZRO** | 1.011 | **16.35%** | 28.98% | this iter, edu 31y |
| iter 009 HAA+GLD | **1.120** | 13.89% | **20.81%** | PARETO SHARPE FRONTIER |
| iter 005 HAA | 1.112 | 14.14% | 20.91% | superseded by 009 |
| VT 1x b&h | 0.546 | 8.64% | 58.35% | beaten |
| Plano C V3_1 v3.5 | 0.671 | 10.94% | 52.43% | beaten |
| V_HYBRID + 10% MF | 0.743 | 10.91% | 44.71% | beaten |

Iter 013 dominates all 3 mission benchmarks on all 3 dimensions ✓. Does NOT advance
the Pareto frontier vs iter 009 on the primary metric (Sharpe).

---

## Config tested

Single pre-committed config (n_trials=1, no grid):
- Offensive: NTSXSIM, NTSI, NTSE, GDESIM (top-2 in HAA momentum rotation, same as iter 009)
- Defensive: **ZROZSIM, IEFSIM, BNDSIM, CASHX** (4 assets; iter 009 had 3)
- Canary: VWOSIM (avg 1m/3m/6m/12m returns)
- Fixed sleeves: KMLMSIM 10% + GLDSIM 5%
- Allocation: risk-ON → top-2 offensive 42.5%+42.5% + 10% KMLM + 5% GLD;
  risk-OFF → top-1 defensive 85% + 10% KMLM + 5% GLD
- Rebalance: monthly (end-of-month)
- Notional factor: 1.45× (unchanged from iter 009)

---

## Structural insight (not a dead-end)

This is NOT a dead-end: iter 013 IS a winner. The structural insight is:

**High-convexity long-duration bonds in HAA defensive = CAGR improvement, Sharpe regression.**

The ZROZSIM "trade" is: earn +46pp in 2008 crisis and +13pp in 2020 crisis, pay the price
of higher daily variance in ALL defensive periods. For investors prioritizing Sharpe
(mandate §1 Plano C), iter 009 remains dominant. For investors prioritizing maximum
long-run CAGR (mandate §7 aggressive override), iter 013 offers +2.5pp CAGR over iter 009.

This finding also explains why the bestfolio reference (S=1.18) almost certainly uses a
CASHX-dominated defensive rather than long-duration bonds — maximizing Sharpe requires
keeping defensive assets LOW variance, not just high return.

---

## 2-3 next directions (if loop continues)

1. **HAA with KMLMSIM-only defensive**: When canary fires, go to 85% KMLMSIM instead of
   top-1 of {IEFSIM, BNDSIM, CASHX}. Hypothesis: managed futures have positive Sharpe in
   both flight-to-safety AND inflationary bears (2008 AND 2022), potentially improving
   both CAGR and Sharpe vs CASHX. Kill: edu Sharpe ≤ 1.120.

2. **HAA with dual canary (VWOSIM + VTISIM)**: Use average momentum of EM + US markets
   as composite canary signal. Reduces false-defensive periods when only EM is weak (e.g.,
   2014-2015 EM crash, US strong). Potential Sharpe improvement via reduced time in low-return
   defensive states. Kill: edu Sharpe ≤ 1.120. `[stocks_on_the_move, ch.6]`

3. **HAA SmartStack with RSSBSIM in offensive**: Replace NTSXSIM (US+IEF 90/60) with RSSBSIM
   (global equity+Treasury 100/100) in the offensive universe. Tests whether global equity
   stacking (vs US-only) improves offensive return in risk-on regimes without increasing
   defensive period variance. Kill: edu Sharpe ≤ 1.120. `[risk_parity, ch.5]`

---

## Citations

- `[risk_parity, ch.5]` — zero-coupon bonds as crisis convexity instruments; Bridgewater
  All-Weather framework for long-duration defensive
- `[stocks_on_the_move, ch.6]` — HAA momentum mechanics (unchanged)
- `[trading_evolved, p.197]` — MF free-lunch (KMLM unchanged)
- `[leverage_for_the_long_run, p.40-60]` — stacking offensive (unchanged)
- `[advances_fin_ml, p.196-202]` — G6 bootstrap; `[p.208-211]` G1 PBO;
  `[p.222-223]` G2 DSR; `[p.31-34]` G7 cross-lib
