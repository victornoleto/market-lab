# Iteration 074 — Final Report

**Date:** 2026-04-25 17:24
**Hypothesis:** Saved-stream ensemble of iter 016 (Moreira-Muir
vol-managed 60:40 SPY+IEF) and iter 064 (iter 046 + Faber QQQ-trend) —
7 weight cfgs ``w_016 ∈ {0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80}``,
expecting low-correlation Markowitz combine to lift DSR p < 0.05
across 3 datasets and break iter 064's joint TOP-K #1 ceiling at 90.
**Cumulative n_trials after iter 074:** 4381 (was 4360; +21 = 7 cfgs × 3 datasets).

---

## Verdict

🥇 **STRONG** (score **89/100** — 1 point shy of WINNER threshold;
`winner_conditions_met=False`, **4/5 strict winner conditions met**,
DSR is the sole strict failure).

**Best cfg: `iter074_ensemble_w016_050`** (50/50 blend of iter 016
and iter 064 saved streams).

The hypothesis was **partially validated and partially falsified**:

- ✅ Engine clean: Markowitz residual ≈ 0, G7 = 0 pp on all 3 datasets,
  15/15 TDD specs green (boundary cases + cross-lib parity + linearity
  + determinism).
- ✅ All gate thresholds reached on all 3 datasets cross-dataset spec §0
  bonus achieved (gates 6/6/6 ≥ {5/4/4} thresholds).
- ✅ G1 PBO: **0.04 / 0.13 / 0.17** — best PBO of any iteration in the
  hunt loop (iter 064 was vacuous N=1, iter 071 was 0.08-0.31). 7-cfg
  weight grid is honest CSCV-informative.
- ✅ MDD: 21.53 / 20.95 / 18.52 — comfortable below benchmarks.
- ✅ Robustness: 9/9 sub-windows positive → +5 bonus.
- ❌ **KILL A fired** — combined Sharpe regress vs iter 064 by ≥ 0.05
  on 3/3 datasets (Δedu −0.106, Δspy −0.090, Δndx −0.077).
- ❌ **KILL B fired** — DSR worst p = 0.0944 ≥ 0.05 on educational
  (best on ndx 0.065, spy 0.083). Sharpe ≈ 1.24-1.30 wasn't enough to
  break the cumulative-n_trials = 4381 threshold.
- ❌ **KILL C fired** — score 89 < 90 (winner threshold).

**No structural bug**: 6 of 9 kills clean, ρ legs 0.79-0.84 (above
predicted 0.6-0.8 range — explains why expected variance reduction
didn't materialise), Markowitz residual = 0 confirms the ensemble
math is exact, all 3 datasets pass 4/7 gate threshold cross-dataset.

---

## Headline metrics (best cfg `iter074_ensemble_w016_050`)

| dataset | Sharpe (Δ frozen / Δ064) | CAGR (Δ frozen) | MDD (Δ frozen) | gates | DSR p |
|---|---|---|---|---|---|
| educational | **1.1118** (+0.43 / −0.106) | 12.41% (+0.94 pp) | 21.53% (−33.6 pp) | 6/7 | 0.0944 |
| spy_real    | **1.2409** (+0.34 / −0.090) | 13.93% (−1.04 pp) | 20.95% (−12.7 pp) | 6/7 | 0.0832 |
| ndx_real    | **1.2982** (+0.34 / −0.077) | 15.47% (−3.71 pp) | 18.52% (−16.6 pp) | 6/7 | 0.0649 |

Robustness sub-windows (9 total, 9 positive): edu sharpes
[0.86, 1.41, 1.13]; spy [1.16, 1.45, 1.09]; ndx [1.31, 1.42, 1.16].

### Strict winner-conditions check (5 conditions per `WINNER_AND_RANKING.md`)

1. **Sharpe edge ≥ +0.10 on ≥ 2 of 3 datasets** ✅ — 3/3 pass (+0.43 / +0.34 / +0.34)
2. **Gate cross-dataset (edu ≥ 5/7, spy/ndx ≥ 4/7)** ✅ — 6/6/6 all clear
3. **DSR worst p < 0.05** ❌ — worst p = 0.0944 (educational); spy 0.0832; ndx 0.0649
4. **CAGR ≥ 0.8 × bench on ≥ 2 of 3 datasets** ✅ — 3/3 pass
5. **MDD ≤ bench + 5 pp on ≥ 2 of 3 datasets** ✅ — 3/3 pass (huge margin)

**4/5 strict winner conditions met. DSR is the sole gap.**

---

## Score breakdown (best cfg)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | 3/3 datasets clear bench+0.10 (full + bonus) |
| 2 Gates | **19** | 25 | edu 6/7 (+5) + spy 6/7 (+5) + ndx 6/7 (+5) + cross-ds bonus (+4) = 19 |
| 3 DSR | **10** | 15 | worst p=0.0944 (< 0.10), with cumulative n_trials=4381 |
| 4 CAGR floor | **15** | 15 | all 3 datasets pass (5+5+5) |
| 5 MDD ceiling | **15** | 15 | all 3 datasets pass (5+5+5) |
| 6 Robustness bonus | **5** | 5 | 9/9 sub-windows positive across datasets |
| **total** | **89** | **100+5** | tier: **🥇 STRONG**; 1 point from WINNER; DSR is the sole gap |

### Per-cfg score grid (full sweep)

| cfg | w_016 | S edu/spy/ndx | CAGR edu/spy/ndx | gates | kills | score |
|---|---|---|---|---|---|---|
| 020 | 0.20 | 1.193/1.305/1.359 | 10.69/11.53/12.22 | 7/6/7 | 2/9 | 83 |
| 030 | 0.30 | 1.169/1.286/1.343 | 11.27/12.33/13.31 | 6/6/7 | 2/9 | 86 |
| 040 | 0.40 | 1.141/1.264/1.321 | 11.84/13.13/14.39 | 6/6/6 | 3/9 | 84 |
| **050** | **0.50** | **1.112/1.241/1.298** | **12.41/13.93/15.47** | **6/6/6** | **3/9** | **89** |
| 060 | 0.60 | 1.083/1.218/1.275 | 12.96/14.71/16.54 | 6/6/6 | 3/9 | 84 |
| 070 | 0.70 | 1.056/1.196/1.253 | 13.51/15.49/17.60 | 6/6/6 | 3/9 | 84 |
| 080 | 0.80 | 1.030/1.176/1.232 | 14.04/16.27/18.65 | 6/6/6 | 3/9 | 84 |

**Pattern**: scores form an inverted U with peak at w_016=0.50. Below
0.50 the CAGR floor binds (low w_016 = mostly iter 064's lower-CAGR
combined stream); above 0.50 the Sharpe edge erodes faster than CAGR
adds. The peak at 0.50 is interpretable as the Markowitz minimum-variance
balance modulated by the strict winner gate constraints.

---

## Kill criteria evaluation (pre-committed)

| Kill | Threshold | Status | Detail |
|---|---|---|---|
| **A** | Sharpe regress vs iter 064 ≥ 0.05 on ≥ 2 ds | ❌ FIRED | Δedu −0.106, Δspy −0.090, Δndx −0.077 (3/3 below) |
| **B** | DSR worst p ≥ 0.05 on best cfg | ❌ FIRED | worst p = 0.0944 (edu); 0.0832 spy; 0.0649 ndx |
| **C** | Score < 90 (winner threshold) | ❌ FIRED | 89/100 (1 point gap) |
| **D** | corr(r_016, r_064) > 0.85 on ≥ 2 ds | ✓ clean | 0.79/0.84/0.79 (just below threshold; spy is highest) |
| **E** | Markowitz outer residual ≥ 0.05 abs | ✓ clean | residual = 0 on all 3 (linear combine of saved streams) |
| **F** | G7 cross-lib > 3 pp CAGR difference | ✓ clean | 0 pp on all 3 (saved streams + linear blend) |
| **G** | PBO grid-level ≥ 0.5 on ≥ 2 ds | ✓ clean | 0.04/0.13/0.17 (best PBO of any hunt-loop iter) |
| **H** | edu CAGR < 9.18% on best cfg | ✓ clean | 12.41% (clears with 3.23 pp margin) |
| **I** | combined MDD > 25% on ≥ 2 ds | ✓ clean | 21.5/21.0/18.5 (well below 25% on all 3) |

**3/9 kills fired.** A, B, C are causally linked: ρ legs = 0.79-0.84
(higher than BASE_MEMORY's 0.6-0.8 prediction) means the
variance-reduction benefit of the ensemble is small (~3-4%); combined
Sharpe ≈ weighted average of legs' Sharpes ≈ 1.24 spy < iter 064's
1.33; DSR p stays around 0.08-0.09 (above 0.05 threshold).

---

## What worked / what didn't

**Worked.** The ensemble math is mechanically perfect: Markowitz residuals
are 0 to floating-point precision, G7 cross-lib parity is exact, PBO
on the 7-cfg weight grid is the lowest of any iteration in the hunt
loop (educational 0.04). The ensemble PASSES all 5 of the soft
winner conditions on the best cfg; **only DSR fails the strict
winner cond #3** because cumulative n_trials = 4381 demands a higher
Sharpe ratio than the high-correlation ensemble can deliver. The 9/9
sub-window robustness check is also notable — across 3 datasets × 3
chronological thirds, every single sub-window has positive Sharpe,
validating the consistency of the edge.

**Didn't work.** The empirical correlation between iter 016 and iter
064 streams was **higher than predicted** (0.79-0.84 actual vs 0.6-0.8
predicted by BASE_MEMORY). This is qualitatively explainable: both
streams carry SPY market beta as a substantial factor (iter 016 via
0.6×SPY directly; iter 064 via iter_041 inside iter_046 also SPY-tilted
in calm regimes; both also share post-2009 broad market exposure).
The Moreira-Muir vol-target leverage in iter 016 doesn't decorrelate
from iter 064's regime-conditional weights as much as the orthogonal
overlay axes (VRP, QQQ-trend) might suggest. With ρ ≈ 0.81 average,
the variance-reduction benefit of a 50/50 ensemble is
(1-ρ²)/(1-ρ) × (something small) — explicitly: combined Sharpe ≈
0.5 × 1.14 + 0.5 × 1.33 = 1.235 spy (linear avg) vs actual 1.241
(+0.6% bonus from ρ-not-1). The ensemble is essentially a linear
interpolation between the two parents' Sharpes, not a Markowitz
super-additive lift.

This **does not falsify the ensemble mechanism** — it falsifies the
**specific stream choice**. Iter 074 establishes that **for this
ensemble to break the 90 ceiling, the second leg must have either
(a) ρ < 0.5 with iter 064**, or **(b) standalone Sharpe ≥ 1.30+ that
makes the linear-avg combined Sharpe naturally exceed 1.33**. Iter
016 has ρ ≈ 0.81 and S ≈ 1.14, which gives a linear-avg combined
S ≈ 1.24 — too low to crack DSR.

---

## Main lesson (for future iterations)

**Saved-stream ensemble of two iter-064-family-anchored streams runs
into a hard correlation floor of ρ ≈ 0.78-0.85 — both streams share
SPY market beta in their construction.** The Markowitz benefit-of-low-
correlation argument requires either an asset-class structurally
orthogonal to SPY (commodities? currencies? international equities?
crypto?) OR a long-short construction that cancels market beta in the
ensemble. **Direction shift implied**: future ensemble candidates must
choose a 2nd leg that has ρ < 0.5 with iter 064 OR Sharpe > 1.30
standalone. The 90 ceiling persists across NOT just regime-allocation
mechanism choices on iter 064 base (proven by iter 064/068/069/070/071/
072 5-iter pattern), but **also** across saved-stream ensembles with
SPY-co-exposed anchors. **The 90 → 95 unlock requires either a
fundamentally different anchor (Plano C sleeve / international /
non-equity) or a long-short market-beta-neutral overlay**.

---

## Structural dead-ends discovered

**Add to `DEAD_ENDS.md`**:

> **iter 074 (iter 016 + iter 064 saved-stream ensemble; 7 cfgs at
> w_016 ∈ {0.20-0.80}):** 89 STRONG, 3/9 KILLS A+B+C. Engine perfect
> (15/15 TDD, G7=0pp, PBO 0.04-0.17 = best of hunt loop); 4/5 strict
> winner conditions met (DSR sole gap). KILL A fires 3/3 — ensemble
> Sharpe 1.11-1.30 < iter 064 standalone 1.22-1.38. Root cause: ρ legs
> 0.79-0.84 (BASE_MEMORY predicted 0.6-0.8); both streams carry SPY
> market beta substantially. **Closes the SPY-co-exposed
> saved-stream-ensemble axis at 89.** Future ensemble candidates must
> choose a 2nd leg with corr < 0.5 vs iter 064 (non-equity anchor) OR
> standalone Sharpe > 1.30. **Validates BASE_MEMORY 5-iter pattern
> generalisation to ensembles**: 90 ceiling persists not just across
> overlay mechanisms on iter 064, but ALSO across SPY-co-exposed
> ensembles.

---

## Citations used

### Primary

- `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 016 +
  iter 064 sub-leg architectures preserved verbatim via saved streams.
- **Markowitz, H.** (1952). "Portfolio Selection." *Journal of Finance*
  7(1), 77-91. DOI 10.1111/j.1540-6261.1952.tb01525.x. Foundational
  convex combination Sharpe identity.

### Supporting

- **Moreira, A., & Muir, T.** (2017). "Volatility-Managed Portfolios."
  *J. Finance* 72(4), 1611-1644. DOI 10.1111/jofi.12513.
- **Faber, M.** (2007). "A Quantitative Approach to Tactical Asset
  Allocation." SSRN 962461.
- **Asness, C., Frazzini, A., & Pedersen, L.** (2012). "Leverage
  Aversion and Risk Parity." *FAJ* 68(1), 47-59. SSRN 1728082.
- **Whaley, R.** (2009). "Understanding the VIX." *JPM* 35(3), 98-105.
  DOI 10.3905/JPM.2009.35.3.098.
- **Sinclair, E.** (2013). *Volatility Trading*, 2nd ed., Wiley.
  `[volatility_trading, p.218]`.
- **Carver, R.** *Systematic Trading*. `[systematic_trading, p.40]`.
- `[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio with
  cumulative n_trials = 4381.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (CSCV with N=7 grid).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — no-lookahead T-1 lag.

---

## Next iteration suggestions

The 5-iter pattern from BASE_MEMORY (064/068/069/070/071/072 plus 074
now) confirms the **90 ceiling is hard-anchored in ANY iter-064-base
construction with SPY market beta retained**. Three structurally
distinct directions to explore:

1. **iter 075 — Long-short market-beta-neutral overlay on iter 064**:
   Add a long-short equity factor sleeve (e.g., AQR-style HML/UMD
   long-short on factor ETFs) sized to net to ~0% market beta when
   combined with iter 064. Mechanism: long-short cancellation
   decorrelates from iter 064 by construction (ρ predicted < 0.3).
   Citations: Asness-Moskowitz-Pedersen (2013) JoF 68(3), Carhart
   (1997) JoF 52(1). Would require Tiingo factor-ETF cache (MTUM,
   QUAL, USMV, VLUE, IWD, IWF) — **check cache before committing**.

2. **iter 075 — Plano C sleeve as 2nd leg** (per BASE_MEMORY direction
   #5; Plano C cap at score ≤ 70). Build a passive factor-tilted Plano
   C ETF sleeve (GDE/AVUV/AVDE/AVEM/BTGD per
   `portfolio-aposentadoria.md`) and ensemble with iter 064. Plano C
   is structurally divergent from iter 064: international + small-cap
   value + emerging + crypto-gold overlay. Predicted ρ < 0.5; CAGR
   floor likely contributes since Plano C targets 7-10% net.

3. **iter 075 — BTC/Gold (DBMF/GLD) as 2nd leg** — managed futures or
   gold-and-crypto overlay structurally orthogonal to SPY. Citations:
   Erb-Harvey (2006) FAJ 62(2), Asness-Moskowitz-Pedersen (2013).
   Tiingo cache likely has GLD; BTC is via overlay parquet. Predicted
   ρ < 0.4; preserves CAGR floor.

**Ranked recommendation**: #2 (Plano C sleeve) — directly cited in
BASE_MEMORY direction #5, infrastructure already exists in `reports/
portfolio_aposentadoria_v2/`, and Plano C is the consolidated
mandate §1 sleeve, so any composability finding is doubly useful
(both for hunt loop AND for Plano C tilt research). Cost: medium
(needs Tiingo factor-ETF cache verification + price loaders).
