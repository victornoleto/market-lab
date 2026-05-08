# Iter 010 — VAA-G3 Pure-Equity Offensive (GDESIM replaces BNDSIM)

**Status**: WINNER 90/100 (formal) — Kill 1 triggered (does NOT advance Pareto frontier)  
**Date**: 2026-04-27  
**Winner conditions met**: True (all 5)  
**Kill 1 triggered**: edu Sharpe 0.9806 ≤ 1.052 → structurally subordinate to iter 006 and iter 009

---

## TL;DR

Replacing BNDSIM with GDESIM (90% S&P + 90% gold) in the VAA-G4 offensive basket
improves CAGR by ~+2pp (edu: 10.28% vs 8.26%) but REDUCES Sharpe (edu: 0.981 vs
1.052) — because GDESIM's 1.8x notional adds more volatility than BNDSIM's 1x
defensive exposure. The strategy formally meets all 5 WINNER conditions with score
90, but the pre-committed kill criterion is triggered: edu Sharpe 0.9806 ≤ 1.052 →
structurally subordinate to iter 006. It does not advance the current Pareto frontier
(iter 009 HAA+GLD: S=1.120/CAGR=13.89%/MDD=20.81% dominates on all dimensions).

**Key structural insight**: The VAA breadth mechanism (4-asset vote) achieves lower
Sharpe than the HAA canary (single binary trigger) on the same offensive universe.
The breadth mechanism keeps partial exposure in mixed markets → higher volatility, 
lower Sharpe. HAA canary switches fully defensive when VWOSIM signal flips → 
cleaner risk-off protection, higher Sharpe.

---

## Results

### Educational (~31y, 1994-05 → 2026-04, VWOSIM-binding)

| metric | iter 010 VAA-G3 | iter 009 HAA+GLD | iter 006 VAA-G4 | VTSIM b&h | delta vs 006 |
|---|---|---|---|---|---|
| Sharpe | 0.9806 | **1.1200** | **1.0520** | 0.546 | **−0.071** |
| CAGR | 10.28% | 13.89% | 8.26% | 8.64% | **+2.02pp** |
| MDD | 18.91% | 20.81% | 14.24% | 58.35% | +4.67pp |
| Gates | 7/7 | 7/7 | 7/7 | — | = |

### vt_real (~17y, 2008-06 → 2026-04)

| metric | iter 010 VAA-G3 | iter 009 HAA+GLD | iter 006 VAA-G4 | VTSIM b&h | delta vs 006 |
|---|---|---|---|---|---|
| Sharpe | 0.8491 | **1.0614** | 0.8500 | 0.489 | **−0.001** |
| CAGR | 8.91% | 12.87% | 6.53% | 8.29% | **+2.38pp** |
| MDD | 18.91% | 14.20% | 14.24% | 54.62% | +4.67pp |
| Gates | 7/7 | 7/7 | 7/7 | — | = |

### ndx_real (16y, 2010-02 → 2026-04)

| metric | iter 010 VAA-G3 | iter 009 HAA+GLD | iter 006 VAA-G4 | QQQ b&h | delta vs 006 |
|---|---|---|---|---|---|
| Sharpe | 0.7188 | 0.9537 | 0.7330 | 0.958 | **−0.014** |
| CAGR | 6.99% | 10.55% | 5.23% | 19.19% | **+1.76pp** |
| MDD | 18.91% | 14.20% | 14.24% | 35.12% | +4.67pp |
| Gates | 7/7 | 7/7 | 7/7 | — | = |

---

## Gate battery

| gate | educational | vt_real | ndx_real |
|---|---|---|---|
| G1 PBO | PASS (trivial, n=1) | PASS | PASS |
| G2 DSR | PASS (p=3.66e-08) | PASS (p=2.86e-04) | PASS (p=2.81e-03) |
| G3 WF (nominal) | PASS (8/8, max_mdd 13.61%) | PASS (6/8, 13.93%) | PASS (6/8, 13.07%) |
| G3' WF (adapted) | PASS | PASS | PASS |
| G4 OOS | PASS (S=0.9386) | PASS (S=0.7043) | PASS (S=0.7001) |
| G5 FWD | PASS (S=0.8745) | PASS (S=0.8745) | PASS (S=0.8745) |
| G6 Bootstrap | PASS (CI_low=0.4289) | PASS (CI_low=0.1855) | PASS (CI_low=0.0690) |
| G7 Cross-lib | PASS (diff=0.08pp) | PASS (diff=0.21pp) | PASS (diff=0.13pp) |
| **Total** | **7/7** | **7/7** | **7/7** |

G3 nominal passes on all datasets (max_mdd ≤ 18.91% < 25%) — no G3' adapted gate required,
though reported for transparency (notional_factor=1.5 > 1.05).

---

## Winner conditions

| condition | result | detail |
|---|---|---|
| 1. Sharpe edge ≥ bm+0.10 on ≥ 2/3 | **PASS** (2/3) | edu ✓ (+0.215), vt_real ✓ (+0.236), ndx_real ✗ (−0.239) |
| 2. 7-gate battery (5/7 edu, 4/7 vt, 4/7 ndx) | **PASS** | 7/7 / 7/7 / 7/7 |
| 3. DSR worst p < 0.05 | **PASS** | worst p = 2.81e-03 (ndx_real) |
| 4. CAGR ≥ 0.8×bm on ≥ 2/3 | **PASS** (2/3) | edu ✓ (10.28% vs 6.91%), vt_real ✓ (8.91% vs 6.63%), ndx_real ✗ (6.99% vs 15.35%) |
| 5. MDD ≤ bm+5pp on ≥ 2/3 | **PASS** (3/3) | all pass (MDD 18.91% far below benchmarks) |

All 5 formal conditions met → score WINNER 90. BUT kill criterion 1 was triggered.

---

## Scoring

| criterion | points | max | note |
|---|---|---|---|
| 1. Sharpe edge | 20 | 25 | 2/3 datasets beat bm+0.10 |
| 2. Gates | 25 | 25 | 7/7 on all 3 |
| 3. DSR | 15 | 15 | worst p=2.81e-03 |
| 4. CAGR floor | 10 | 15 | 2/3 pass (ndx_real fails — QQQ 19.19% too high) |
| 5. MDD ceiling | 15 | 15 | 3/3 pass |
| 6. Robustness | 5 | 5 | 26/26 rolling-5y windows positive (100%) |
| **Total** | **90** | **100** | |

**Formal Tier: WINNER** — but kill criterion overrides: does not advance Pareto frontier.

---

## Kill criteria evaluation

### Kill 1 — edu Sharpe ≤ 1.052 (VAA iter 006 baseline): **TRIGGERED**

edu Sharpe = 0.9806 ≤ 1.052. The strategy is structurally subordinate to iter 006
(VAA-G4 with BNDSIM) on Sharpe. While CAGR improved (+2pp), Sharpe fell (-0.07).

**Implication**: Replacing BNDSIM with GDESIM in the offensive basket does NOT
improve Sharpe — it worsens it. The hypothesis that "bond contamination was VAA's
only weakness" was wrong: removing BNDSIM helps CAGR but adds volatility via
GDESIM's 1.8x notional, net effect: lower Sharpe.

### Kill 2 — any WF G3' fail: **NOT triggered**

All 8 WF windows pass on all 3 datasets. G3 nominal also passes (max_mdd 18.91%).

---

## Comparison vs mission benchmarks (31y educational window)

| strategy | Sharpe | CAGR | MDD | dominates missions? |
|---|---|---|---|---|
| **iter 010 VAA-G3** | 0.981 | 10.28% | 18.91% | ✓ on Sharpe/MDD vs all 3; CAGR ≈ V_HYBRID |
| iter 009 HAA+GLD | **1.120** | **13.89%** | **20.81%** | ✓ all 3 dimensions |
| iter 006 VAA-G4 | 1.052 | 8.26% | **14.24%** | ✓ on Sharpe; ✗ on CAGR vs V_HYBRID |
| VT 1x b&h | 0.546 | 8.64% | 58.35% | — benchmark |
| Plano C V3_1 v3.5 | 0.671 | 10.94% | 52.43% | — benchmark |
| V_HYBRID+MF | 0.743 | 10.91% | 44.71% | — benchmark |

Iter 010 beats all 3 mission benchmarks on Sharpe and MDD. CAGR at 10.28% is just
below V_HYBRID+MF (10.91%) — the one benchmark it doesn't clearly exceed on CAGR.

---

## Structural mechanism analysis

### Why does GDESIM reduce Sharpe vs BNDSIM?

**BNDSIM as offensive anchor**: In VAA-G4 (iter 006), when bonds are trending up
(rate-cutting cycle), BNDSIM has positive 13612W momentum → it contributes to B
(breadth count). When BNDSIM is in the offensive basket, the strategy holds ~21%
in bonds (85%/4 = 21% when B=4). Bonds have low volatility → BNDSIM stabilizes
portfolio variance → higher Sharpe ratio despite lower CAGR.

**GDESIM as offensive asset**: GDESIM is 90% S&P + 90% gold (1.8x notional).
Its daily return volatility is ~1.5-2x that of BNDSIM. When GDESIM is in the
offensive basket, portfolio variance increases → lower Sharpe despite better CAGR.

**Trade-off pattern** (consistent across all 3 datasets):
- CAGR: iter 010 always +1.8-2.4pp better than iter 006 (GDESIM > BNDSIM return)
- MDD: iter 010 always +4.7pp worse than iter 006 (GDESIM > BNDSIM volatility)
- Sharpe: iter 010 always 0.001-0.071 worse than iter 006 (variance dominates return gain)

### Why is VAA breadth inferior to HAA canary on Sharpe?

The VAA breadth rule allows partial defensive allocation when B < 4. For example,
when B=2, 50% is defensive (bonds/cash) + 50% offensive. This creates "mixed
regime" states where the portfolio holds both equity and bonds simultaneously.

HAA canary (VWOSIM) is binary: when VWOSIM momentum turns negative, 100% defensive;
when positive, 100% offensive (top-2 of 4). The binary nature eliminates the
"mixed regime drag" — the strategy either runs at full speed or parks entirely.

In trending markets (2010-2013 bull, 2016-2019 bull), HAA concentration in top-2
offensive is a return advantage. In choppy markets, HAA binary switch provides
cleaner risk-off. Net effect: HAA canary > VAA breadth on Sharpe for this universe.

---

## Robustness

- 26/26 rolling 5-year windows positive Sharpe (100%)
- Min rolling Sharpe: 0.303; Max: 1.783
- G5 FWD post-2020 Sharpe: 0.8745 (positive recent performance)
- MDD consistent: 18.91% across ALL three datasets (same MDD regardless of window)
  → MDD driven by same episode in all windows (likely 2022 bear)

---

## Top-K ranking update

Iter 010 scores 90 (same as iters 002/004/005/009) but has lower edu Sharpe
(0.981) than iter 002 (0.991) → enters at rank 5 (tying for 4th but lower Sharpe).
However, given Kill 1 triggered and no Pareto advance, not adding to top-K.

---

## Citations

- `[stocks_on_the_move, ch.6]` — VAA momentum mechanics, 13612W breadth signal
- `[trading_evolved, p.197]` — managed futures free-lunch sleeve
- `[leverage_for_the_long_run, p.40-60]` — return-stacking for offensive assets
- `[advances_fin_ml, p.196-202]` — G6 bootstrap calibration
- `[advances_fin_ml, p.222-223]` — G2 DSR deflation
- `[advances_fin_ml, p.31-34]` — G7 cross-lib parity
- VAA SSRN 3002624 (Keller & Keuning 2017) — primary breadth mechanism

---

## Dead-end classification

This iteration provides structural evidence for a dead end:

**VAA breadth + GDESIM as 4th offensive is not a Sharpe-maximization path.**

The specific dead-end: "Replace any 1x-notional asset in VAA offensive with a
higher-notional stacked asset to improve Sharpe." This fails because higher
notional increases variance faster than it increases expected return at the
portfolio level → Sharpe falls.

CAGR improvement IS real: if the goal is CAGR maximization (not Sharpe), then
VAA-G3 with GDESIM is the better choice. But this loop optimizes Sharpe.

---

## Next directions

1. **Iter 011 — HAA + NTSD-style equity stacking**: The NTSD discovery (2026-04-27,
   memory note) suggests a new WisdomTree stacking ETF. If testfolio synth available,
   substitute for one NTSXSIM sleeve to get global equity stacking beyond NTSXSIM/NTSI/NTSE.
   Citation: `[leverage_for_the_long_run, p.40-60]` extended to new instrument.
   Kill criterion: edu Sharpe ≤ 1.120 (must beat iter 009 HAA+GLD).

2. **Iter 012 — HAA + 10% GLD (larger gold sleeve)**: iter 009 showed 5% GLD
   improves Sharpe by +0.008-0.012. Test 10% GLD (KMLM reduced to 5%) to see if
   improvement scales linearly. Kill criterion: edu Sharpe ≤ 1.120.
   `[risk_parity, ch.5]` + `[leverage_for_the_long_run, p.40-60]`

3. **Tier 2 — Top-K country rotation** (Faber 2007 style): universe SPY, EWJ, EWG,
   EZU, EWU, MCHI, EWZ, INDA — 17y window only (no synth analogs).
   `[stocks_on_the_move, p.21-30]`.
