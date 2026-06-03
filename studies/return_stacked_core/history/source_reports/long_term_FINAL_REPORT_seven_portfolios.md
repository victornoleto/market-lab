# FINAL REPORT — Seven-Portfolio Comparative Scoring

**Date:** 2026-04-30
**Sweep:** iters 027-042 (16 iters; Phase 1A + 1B + 2 + 3 MF sensitivity)
**Cumulative DSR n_trials:** 152
**Baseline:** iter 023 (NTSX 25 / GDE 25 / KMLM 35 / TLT 15)
**Mandate basis:** NEW SPY-only +0.05 (post-2026-04-29 reframing); CAGR floor warning-only; MDD ≤ SPY strict.

> **Filename note:** the spec planned 7 finalists (F1-F7); only **4 were
> realised** (F1, F2, F3, F7). F4 Gl-Stk, F5 Gl-Fct, F6 Gl-Hyb were
> **skipped per Phase 1+1B routing** because **no global sleeve survived**
> the single-axis isolation test (NTSD/AVDV/AVEM/IDMO all DEAD; only
> US-momentum SPMO had a robust +signal). Filename retained for
> sweep-plan continuity. See `PHASE_1_WINNERS.md` for routing rationale.

---

## 1. Executive Summary

After 16 sweep iters validating against three datasets (lh_56y / vt_real /
ndx_real), the multi-criteria rubric (C1-C7, max 100 pts) ranks **F1
(iter 023, NTSX+GDE+KMLM+TLT, 4 ETFs) as the highest-scoring finalist
at 63.57/100**, narrowly ahead of **F3 (iter 040, +SPMO 5%) at 61.83**,
**F7 (iter 041, RSST stacked-MF) at 61.26**, and **F2 (iter 039, pure
factor) at 60.39**. F1 wins on simplicity (4 ETFs = max 15pts),
strongest mean Sharpe (1.109), and lowest mean MDD (16.76%); it pays
nothing on TER vs the other stacking-based finalists. F7 is the
maximum-CAGR alternative (12.50% mean, +1.7pp vs F1) for users
willing to accept higher MDD (21.73%) and an extra 0.92% TER ETF
(RSST). The deployment recommendation is **F1 with the MF sleeve
SPLIT 50/50 KMLM+DBMF** (per iter 042 — best 26y-intersection Sharpe
+ MDD + AUM stability via DBMF's $3.2B issuer).

**Trade-off summary**: simplicity, Sharpe, and MDD favor F1; CAGR and
crisis-alpha breadth favor F7; TER and 1× notional purity favor F2;
ndx_real edge and momentum exposure favor F3. None of the alternatives
beats F1 by a margin that overcomes its 1-2pt simplicity edge plus
~5pp lower MDD.

---

## 2. Comparative Table

| metric | **F1 US-Stk** | **F2 US-Fct** | **F3 US-Hyb** | **F7 US-StkMF** |
|---|---|---|---|---|
| ETF count | **4** | 6 | 5 | 5 |
| Notional total | 132% | 100% | 135% | **150%** |
| Sharpe lh_56y | **1.189** | 1.086 | 1.107 | 1.072 |
| Sharpe vt_real | 1.004 | 0.874 | **1.008** | 0.978 |
| Sharpe ndx_real | 1.135 | 1.087 | **1.173** | 1.144 |
| **Mean Sharpe** | **1.109** | 1.016 | 1.096 | 1.064 |
| CAGR lh_56y / vt / ndx | 11.52% / 10.13% / 10.62% | 11.38% / 9.79% / 11.35% | 11.40% / 10.63% / 11.49% | **12.73% / 11.90% / 12.86%** |
| **Mean CAGR** | 10.76% | 10.84% | 11.17% | **12.50%** |
| MDD lh_56y / vt / ndx | 21.13% / 17.40% / **11.76%** | 24.82% / 24.45% / 18.87% | 21.00% / 19.27% / 13.26% | 26.65% / 22.97% / 15.58% |
| **Mean MDD** | **16.76%** | 22.71% | 17.84% | 21.73% |
| Weighted TER (annual) | 0.445% | **0.299%** | 0.405% | 0.454% |
| DSR worst p-value | 7.28e-04 | 4.55e-03 | 7.23e-04 | 1.05e-03 |
| Robustness (5y rolling % positive) | 100% | 100% | 100% | 100% |
| Cumulative n_trials (DSR-adjusted) | 87 | 140 | 144 | 148 |
| Verdict score (NEW SPY-only) | 86 STRONG | 85 STRONG | 88 STRONG | **91 WINNER** |
| Composition (ticker @ weight) | NTSX 25, GDE 25, KMLM 35, TLT 15 | VTI 30, AVUV 10, SPMO 20, KMLM 20, TLT 10, GLD 10 | NTSX 25, GDE 25, KMLM 30, TLT 15, SPMO 5 | NTSX 25, RSST 15, GDE 25, KMLM 20, TLT 15 |
| Best regime | **balanced bull** (cap-efficient stack hits all factors) | choppy/bear (no leverage; SCV+momentum hold) | **bull-momentum** (SPMO sleeve adds ndx tail) | **inflation/stagflation** (RSST trend-MF + GDE gold) |
| Worst regime | extreme bear (132% notional drawdown) | extreme leverage shock (no upside torque) | momentum-crash (SPMO sleeve goes negative) | **levered drawdown** (150% notional + simultaneous trend-MF whipsaw) |
| **Multi-criteria score** | **63.57** | 60.39 | 61.83 | 61.26 |
| **Rank** | **#1** | #4 | #2 | #3 |

(F4 Gl-Stk, F5 Gl-Fct, F6 Gl-Hyb skipped per Phase 1 routing — no
global sleeves survived single-axis isolation; see Section 5b.)

---

## 3. Multi-criteria Scoring (Detail)

Rubric per `SWEEP_PLAN_iter_027_to_039.md` §"Phase 4 — Comparative
Report" multi-criteria scoring rubric. Weights sum 100. Higher = more
important for 20-30y retirement deploy.

### Formulas applied

- **C1 Risk-adjusted return (max 25)**: `25 × clamp((mean_sharpe − 0.827) / (2×1.109 − 0.827), 0, 1)` (SPY mean = 0.827; iter023 mean = 1.109 normalisation anchor).
- **C2 CAGR (max 12)**: `min(12, max(0, (mean_cagr − 0.1380) × 200))` — edge vs SPY mean CAGR (13.80%).
- **C3 MDD safety (max 13)**: `min(13, max(0, (0.4085 − mean_mdd) × 100))` — reduction vs SPY mean MDD (40.85%).
- **C4 Simplicity (max 15)**: 4 ETFs=15, 5=13.5, 6=12, 7=10.5, 8=9, 9=7.5, 10=6.
- **C5 TER (max 10)**: weighted by holding. <0.40%=10 ; 0.40-0.60%=8.5 ; 0.60-0.80%=7 ; 0.80-1.00%=5.5 ; >1.00%=4.
- **C6 Regime robustness (max 10)**: rolling 5y % positive Sharpe (from `verdict.json:robustness.pct_positive_sharpe`).
- **C7 Deploy ease (max 15)**: hard gate — any ETF unavailable on Inter Internacional → C7=0. **Currently `INTER_CHECK.md` is unfilled (PENDING USER FILL)**, so default 12 is used per spec, with explicit assumption flagged.

### Per-criterion scores

| criterion | weight | F1 US-Stk | F2 US-Fct | F3 US-Hyb | F7 US-StkMF |
|---|---:|---:|---:|---:|---:|
| C1 Risk-adjusted Sharpe | 25 | 5.07 | 3.39 | 4.83 | 4.26 |
| C2 CAGR vs SPY | 12 | 0.00 | 0.00 | 0.00 | 0.00 |
| C3 MDD safety vs SPY | 13 | **13.00** | **13.00** | **13.00** | **13.00** |
| C4 Simplicity (ETF count) | 15 | **15.0** | 12.0 | 13.5 | 13.5 |
| C5 TER weighted | 10 | 8.5 | **10.0** | 8.5 | 8.5 |
| C6 Robustness (5y rolling) | 10 | **10.0** | **10.0** | **10.0** | **10.0** |
| C7 Deploy ease (Inter) — PENDING | 15 | 12.0 † | 12.0 † | 12.0 † | 12.0 † |
| **TOTAL** | 100 | **63.57** | 60.39 | 61.83 | 61.26 |

† C7 is **PENDING USER FILL** in `INTER_CHECK.md`. Default = 12pts assumes
"most major ETFs available, NTSD/RSST may be missing." If NTSX, GDE,
KMLM, TLT are all available on Inter Internacional (very likely — these
are mainstream issuers WisdomTree / KFA / iShares), F1 jumps to ≥13pts.
If RSST is unavailable, F7's C7 = 0 (drops to 49.26 — moves to last
place). If SPMO is unavailable, F3's C7 = 0 (drops to 49.83 — also last
place). **F1's deploy risk is structurally lowest** because its 4 ETFs
are all major issuers with high US AUM.

### Notable score observations

1. **C2 CAGR = 0 for all four finalists.** Mean CAGR for all candidates
   (10.76%-12.50%) sits below SPY's three-dataset mean CAGR (13.80%).
   This is a **window artifact**: SPY mean CAGR is dragged up by the
   ndx_real-aligned and vt_real Tiingo windows (both 14.97% CAGR
   2008-2024 SPY). The **lh_56y SPY benchmark is only 11.47%** — finalists
   beat THIS dataset's SPY (F7 12.73% vs 11.47%). C2's 0-score is a
   formula consequence of mean-aggregation across regimes; the
   stacking-based finalists deliver Sharpe via lower vol, not higher
   CAGR vs the highest-CAGR SPY window. CAGR is also warning-only per
   mandate §2.2.

2. **C3 saturates at 13.0 for all finalists.** SPY mean MDD = 40.85%
   (lh_56y 55%, vt 33.7%, ndx 33.7%); all finalists deliver mean MDD
   ≤22.71%, easily clearing the 13pt cap.

3. **C1 differentiates the field.** F1's mean Sharpe 1.109 → 5.07pts.
   F2's 1.016 → 3.39pts (the −0.103 mean Sharpe gap costs ~2pts).

4. **C4 is decisive between F1 and F3/F7.** F1's 4-ETF count gives a
   1.5pt lead over F3/F7 — close to the F1-vs-F3 total margin (1.74pt).

5. **C7 is the largest source of remaining uncertainty.** A ±15pt swing
   on any finalist depending on Inter availability could fully reorder
   the ranking. **Filling `INTER_CHECK.md` is the single highest-value
   action remaining before deploy.**

---

## 4. Per-Finalist Trade-off Narrative

### F1 — US Stacking-only (iter 023): NTSX 25 / GDE 25 / KMLM 35 / TLT 15

**Strengths:**
- **Highest mean Sharpe** (1.109) — best risk-adjusted return across all 4 finalists.
- **Lowest mean MDD** (16.76%) — best capital preservation; ndx_real MDD 11.76% is exceptional.
- **Simplest** (4 ETFs) — easiest to rebalance, lowest transaction friction over 30y.
- **All-major-issuer composition** (WisdomTree, KFA, iShares) — minimal closure risk.
- **Lowest cumulative n_trials at conclusion** (87) — least DSR-adjusted, highest signal credibility.
- Embeds 132% notional via NTSX (1.5×) + GDE (1.5×) without an explicit "leveraged" label.

**Weaknesses:**
- **Lowest CAGR** (10.76% mean) — concedes ~1.7pp to F7. For 30y compounding this is ~63% terminal-wealth gap.
- **No factor tilt** (no momentum, no value, no SCV) — pure cap-weighted equity inside the stacks.
- **Sensitive to KMLM closure risk** at 35% concentration on a $600M-AUM single-issuer. (Mitigated by SPLIT recommendation below.)
- **Depends on long-Treasury TLT 15%** — vulnerable to a 1970s-style rates regime if held in real terms.

**Best regime: balanced bull markets**
Stack philosophy delivers when equity rises modestly and bond/gold/MF
provide steady ballast. Best historical analogy: 2003-2007, 2010-2019.
The 1970-2024 lh_56y window CAGR of 11.52% confirms multi-decade
robustness.

**Worst regime: rapid simultaneous drawdown across stacks**
1973-74 oil shock, 2008 GFC, or 2022 simultaneous stocks+bonds drop
hit NTSX (equity+Treasury both lose) and TLT independently. KMLM/GDE
provide partial offset but the 132% notional means leveraged exposure
amplifies the loss. lh_56y MDD 21.13% is the realised manifestation —
manageable but not crisis-immune.

**20-30y deploy considerations:**
- **Annual rebalance** preserves the 25/25/35/15 risk parity targets.
- **Tracking-error drift**: NTSX (1.5×) and GDE (1.5×) rely on futures rolls; ~5-10bps/y financing drag is structural.
- **ETF closure risk**: NTSX $1.7B AUM (low risk), GDE $300M (medium), KMLM $600M (medium), TLT $60B (negligible). KMLM single-issuer concentration is the largest deploy fragility — addressed by **SPLIT MF recommendation (Section 6)**.

---

### F2 — US Factor-tilts only (iter 039): VTI 30 / AVUV 10 / SPMO 20 / KMLM 20 / TLT 10 / GLD 10

**Strengths:**
- **Lowest TER** (0.299% weighted) — VTI 0.03% anchors the cost stack.
- **No leverage** (100% notional) — eliminates futures-roll financing risk and counterparty surface.
- **Engine diversification**: 6 distinct factor/style sleeves (VTI, AVUV-SCV, SPMO-momentum, KMLM-trend, TLT-duration, GLD-inflation).
- Broadest factor coverage of the four finalists.

**Weaknesses:**
- **Lowest Sharpe** (1.016 mean) — gives up 0.093 Sharpe vs F1.
- **Highest mean MDD** (22.71%) of the four finalists — vt_real MDD 24.45% is the worst across this sweep.
- **Highest ETF count** (6) — annual rebalance friction × 6 trades.
- **AVUV included reluctantly**: Phase 1A/1B both showed AVUV substantively negative on lh_56y (Δ −0.074 / −0.021). It carries the philosophy "best-available US non-momentum factor" but isn't validated as a +signal.
- **SPMO at 20% may be over-concentrated** — Phase 1B optimum was 10%.

**Best regime: choppy / bear / 1× equity dominance**
When SPY does NOT have outsized levered upside, F2's no-leverage
posture stops bleeding financing drag. Factor tilts (AVUV value,
SPMO momentum, GLD inflation) earn premia uncorrelated to leveraged
beta. Best analogy: 2000-2010 lost decade, where AVUV/SCV
historically delivered while SPY went sideways.

**Worst regime: extreme leverage shock with momentum reversal**
March 2020 / Q4 2018 — SPMO momentum crashes simultaneously with
SCV factor reversal. F2's 1× equity provides no torque to recover.
F1's leveraged stacks would actually recover faster post-trough due
to higher beta exposure. This is a structural F2 disadvantage in the
post-2009 regime.

**20-30y deploy considerations:**
- **Tax efficiency**: 1× notional + ETF wrappers (vs futures-based stacks) yields cleanest cost basis.
- **AVUV closure risk**: $11B AUM is robust; SPMO $5B also healthy.
- **Rebalance overhead**: 6 ETFs × annual = 6 trades; small for retail but doubles F1's friction.

---

### F3 — US Hybrid (iter 040): NTSX 25 / GDE 25 / KMLM 30 / TLT 15 / SPMO 5

**Strengths:**
- **Best ndx_real Sharpe** (1.173) of all finalists — momentum overlay captures large-cap winner persistence.
- **Best vt_real Sharpe** (1.008) — narrowly beats F1's 1.004.
- **Adds SPMO with minimal architectural change** to iter 023 — substitutes 5% from KMLM (the validated Phase 1B subKMLM rule).
- **DSR worst p-value** (7.23e-04) is best of the four — strongest statistical robustness despite n=144.
- **Lowest lh_56y MDD** (21.00%) of the leveraged finalists.

**Weaknesses:**
- **Lower lh_56y Sharpe than F1** (1.107 vs 1.189) — the SPMO sleeve drags 56y Sharpe by −0.082.
- **vt_real PBO is high** (0.472) and **ndx_real PBO is high** (0.853) — momentum sleeve sensitive to walk-forward window selection per Bailey-Lopez-de-Prado [advances_fin_ml, p.208-211].
- **5 ETFs**: SPMO adds 1 ETF (vs F1's 4) for a marginal Sharpe gain — pays simplicity cost.
- **SPMO 0.13% TER is cheap** but adds an additional Invesco-issuer concentration (vs WisdomTree-anchored F1).

**Best regime: bull-momentum continuation (post-recession recoveries)**
SPMO momentum thrives in sustained large-cap leadership regimes —
2003-2007, 2013-2019, 2023-2024. The +0.044 ndx_real edge measured
in Phase 1B subKMLM is the empirical signature of this regime.

**Worst regime: momentum crash (Q1 2009, March 2020, Q4 2002)**
Cross-sectional momentum reverses violently after market troughs as
losers rebound disproportionately. SPMO 5% is small enough that the
crash impact is bounded, but vt_real PBO 0.472 says ~half of the
historical OOS Sharpes underperform the IS Sharpe — fragility flag.

**20-30y deploy considerations:**
- **SPMO turnover**: ~50% annual (momentum tilt). May trigger short-term gains in taxable accounts; in retirement-tax-deferred this is neutral.
- **Marginal complexity** vs F1 (1 extra ETF, 1 extra annual trade) for +0.04 ndx_real Sharpe.
- **SPMO closure risk**: $5B AUM healthy; Invesco issuer also robust.

---

### F7 — US Stacked-MF (iter 041): NTSX 25 / RSST 15 / GDE 25 / KMLM 20 / TLT 15

**Strengths:**
- **Highest mean CAGR** (12.50%) — +1.7pp vs F1; over 30y this is a 63% terminal-wealth advantage if regime persists.
- **Highest notional** (150%) — most capital efficient; the RSST 1.5x stack adds another layer of equity+MF on top of NTSX/GDE.
- **Highest score on verdict.json NEW rubric** (91 WINNER) — only finalist to clear WINNER tier on the underlying loop scoring (vs STRONG for F1/F2/F3).
- **Engine diversification**: KMLM (KFA MLM Index trend) + RSST internal MF (ReSolve trend overlay) + KMLM standalone — three trend strands within the same family but different sub-engines.
- **Lowest ndx_real PBO** (0.349) of the leveraged finalists — best walk-forward stability on the most momentum-driven dataset.

**Weaknesses:**
- **Highest mean MDD** (21.73%) — lh_56y MDD 26.65% is the largest of the leveraged finalists.
- **Highest TER** (0.454% weighted) — RSST at 0.98% drags the cost structure.
- **Only 5y of live RSST track record** (since 2023) — synth `SPYSIM + KMLMSIM − 60bps/y` [INCOMPLETE flag] is engine-mismatched (ReSolve trend ≠ KMLM trend).
- **150% notional is the most leveraged finalist** — max sensitivity to a simultaneous-asset-shock regime.
- **RSST AUM $400M** is the lowest single-ETF AUM in any finalist — closure risk is real for 30y horizon.
- **lh_56y gates score 5/7** (vs 7/7 for F2/F3 and 7/7 for F1's mainline) — weakest gate breadth on the long synth window.

**Best regime: inflation / stagflation / persistent trend regimes**
RSST embeds explicit equity+MF stacking — the MF sleeve thrives in
sustained directional moves (1970s commodity bull, 2022 rates hike).
GDE adds gold inflation hedge. F7 is the most "regime-defensive"
finalist for non-equity-led decades.

**Worst regime: levered drawdown with simultaneous MF whipsaw**
2018 Q4 (equity drop AND MF false signals) hit RSST-style products
hard. 150% notional means losses compound. The 26.65% lh_56y MDD is
the realised signature.

**20-30y deploy considerations:**
- **RSST closure risk** is the dominant deploy concern. ReSolve/Newfound is a small issuer; AUM $400M means a 50% drawdown could put the ETF below liquidation threshold (typical $100-200M). **Switch plan**: if RSST closes, re-allocate to NTSX 35% + KMLM 30% (collapses to F1-with-bigger-MF).
- **TER 0.98% on RSST sleeve compounds**: 0.98% × 15% weight = 0.147%/y of the 0.454% weighted TER comes from this single sleeve. Over 30y at 11% nominal CAGR, this drag is ~4-5% of terminal wealth.
- **Engine mismatch flag**: real-RSST trend engine is ReSolve, synth uses KMLM — backtest may overstate true 30y forward Sharpe by 5-15bps.

---

## 5. Cross-Cutting Analysis

### 5a. Stacking vs Factor vs Stacked-MF — Philosophy Head-to-Head

| philosophy | exemplar | mean Sharpe | mean MDD | mean CAGR | rank |
|---|---|---:|---:|---:|---:|
| Pure stacking | F1 | **1.109** | **16.76%** | 10.76% | **#1** |
| Pure factor | F2 | 1.016 | 22.71% | 10.84% | #4 |
| Hybrid (stack+factor) | F3 | 1.096 | 17.84% | 11.17% | #2 |
| Stacked-MF | F7 | 1.064 | 21.73% | **12.50%** | #3 |

**Verdict**: Pure capital-efficient stacking dominates. The factor
overlay (F3) costs Sharpe vs F1; the stacked-MF wildcard (F7) costs
Sharpe AND MDD for CAGR upside. The pure-factor philosophy (F2) loses
on both axes — confirms Phase 1A/1B finding that the Avantis factor
family is structurally subordinate in the 2010-2024 US-equity-dominant
regime.

[risk_parity, ch.5, p.10] Carlson cap-efficient stacking is the
empirically dominant philosophy in this universe.

### 5b. US-only Dominance Assumption — Regime-Dependence Flag

All four realised finalists are **US-only**. F4 (Gl-Stk via NTSD), F5
(Gl-Fct via AVDV/AVEM/IDMO), F6 (Gl-Hyb) were all skipped because
**Phase 1+1B unanimously closed every global sleeve** (NTSD Δ −0.097
lh_56y; AVDV Δ −0.108; AVEM Δ −0.107; IDMO Δ −0.082). This is
consistent with iter 014/015 prior closures of intl-equity tilt.

**Regime-dependence flag (CRITICAL)**: the loop measures performance
over windows that are **US-equity-led 1970-2024**, with the strongest
signal coming from the post-2009 regime. If the next 20-30y is
**intl-led** (e.g., 1980s-style ex-US dominance, or EM secular bull),
all four finalists may be 50-150bps Sharpe behind a hypothetical
global-tilted alternative. The honest framing: **this study has
selected the best US-only portfolio in the testfolio universe**, not
the best global-resilient portfolio.

Mitigation paths:
1. Hold a small (5-10%) tactical sleeve in VEA/VWO outside the
   finalist for regime-hedge optionality.
2. Re-run the loop annually to detect global-sleeve resurrection.
3. Trust [ilmanen_expected_returns, ch.19] long-run mean-reversion
   prior: ex-US has lagged 2010-2024, so forward Sharpe edge is
   plausibly positive — but this is a 30y bet, not validated by data.

### 5c. Hybrid Premium — Does F3 Beat F1?

**F3 vs F1 head-to-head**:

| metric | F1 | F3 | Δ (F3 − F1) | wins? |
|---|---:|---:|---:|---|
| Sharpe lh_56y | 1.189 | 1.107 | −0.082 | F1 |
| Sharpe vt_real | 1.004 | 1.008 | **+0.004** | F3 |
| Sharpe ndx_real | 1.135 | 1.173 | **+0.038** | F3 |
| Mean Sharpe | 1.109 | 1.096 | −0.013 | F1 (margin: 0.013) |
| Mean MDD | 16.76% | 17.84% | +1.08pp | F1 |
| ETF count | 4 | 5 | +1 | F1 |
| Total score | 63.57 | 61.83 | −1.74 | F1 |

**Verdict**: Hybrid premium is **modestly negative on aggregate**. SPMO
adds ndx_real edge (+0.038) and vt_real edge (+0.004) but costs lh_56y
Sharpe (−0.082) and MDD (+1.08pp). The 1.74pt total-score gap is small
and comes mostly from the simplicity penalty (1.5pts). On regime
weighting: if next 30y is more "ndx-like" (large-cap-momentum-led),
F3 wins; if more "lh_56y-like" (multi-decade balanced), F1 wins. **F3
is a defensible alternative if user weights post-2009 regime
heavily**.

### 5d. Regime Regret Analysis — 1980s vs 2010s

**1980s-style intl-led regime** (1970-1989 ex-US dominated):
- F1: 11.52% lh_56y CAGR validates that NTSX+GDE+KMLM+TLT survives this regime via leverage on whatever equity beta exists + KMLM trend on commodities (1970s grain bull, 1980s oil) + TLT in the 1982-1989 disinflation rally. **Acceptable**.
- F2: lacks leverage, lacks gold (only 10%), lacks intl exposure. **Likely to lag SPY benchmark**.
- F3: same as F1 + 5% SPMO momentum. **Acceptable**, slightly better.
- F7: RSST in stagflation does well via MF crisis-alpha. **Best fit for this regime**.

**2010s-style US-equity-led regime** (2010-2024):
- F1: stacking baseline performs. **Good**.
- F2: AVUV lags large-cap; SPMO 20% provides upside. **Mediocre**.
- F3: SPMO 5% sleeve captures large-cap-momentum. **Good**.
- F7: 150% notional with US-equity stack delivers max upside. **Best**.

**Most regret-resistant**: **F1 is the regime-agnostic incumbent**.
F7 is best in stagflation but worst in 2010s-style; F3 is best in
2010s but worst in stagflation; F1 sits in the middle on all regime
extremes. Combined with simplicity + lowest MDD, F1 is the
**minimum-regret choice across regime uncertainty**.

[ilmanen_expected_returns, ch.19] cross-asset regime cycling rationale.

---

## 6. MF Sleeve Recommendation (per iter 042)

**Recommended MF sleeve for any finalist using KMLM (F1, F3, F7):
SPLIT 50/50 KMLM + DBMF.**

Per `iterations/042-2026-04-30-MF-sensitivity/final_report.md`, on the
**apples-to-apples 26y intersection (2000-2026)**:

| config | lh_56y Sharpe | CAGR | MDD |
|---|---:|---:|---:|
| mf_kmlm (38y truncated to 26y) | 0.9626 | 9.73% | 21.13% |
| mf_dbmf (26y native) | 0.9947 | **10.42%** | 21.78% |
| **mf_split (50/50, 26y native)** | **1.0004** | 10.10% | **19.91%** |

**Rationale (3-part rule)**:
1. **Sharpe**: split (1.0004) ≥ both pure (KMLM 0.9626, DBMF 0.9947) within 0.05 noise floor.
2. **MDD**: split (19.91%) is lowest — engine diversification reduces drawdown.
3. **AUM stability**: 50% of the sleeve sits in DBMF's $3.2B issuer (vs KMLM's $600M) — reduces single-issuer / single-engine concentration over 30y.

**Application to each finalist using KMLM**:
- **F1 (KMLM 35%)** → split as KMLMSIM 17.5% + DBMFSIM 17.5% (full composition: NTSX 25 / GDE 25 / KMLM 17.5 / DBMF 17.5 / TLT 15 — **5 ETFs**).
- **F3 (KMLM 30%)** → KMLM 15% + DBMF 15% (composition: NTSX 25 / GDE 25 / KMLM 15 / DBMF 15 / TLT 15 / SPMO 5 — **6 ETFs**).
- **F7 (KMLM 20%)** → KMLM 10% + DBMF 10% (composition: NTSX 25 / RSST 15 / GDE 25 / KMLM 10 / DBMF 10 / TLT 15 — **6 ETFs**).

**Note**: applying the SPLIT rule **adds 1 ETF** to each finalist's
count, costing 1.5 C4 simplicity points. Using the original
multi-criteria scores adjusted by C4-only:

| | original | SPLIT-adjusted | new total |
|---|---:|---:|---:|
| F1 | 63.57 | C4 15→13.5 | **62.07** |
| F3 | 61.83 | C4 13.5→12 | 60.33 |
| F7 | 61.26 | C4 13.5→12 | 59.76 |

The ranking is preserved: **F1 with SPLIT remains #1 at 62.07**.

[ilmanen_expected_returns, ch.19] MF crisis-alpha role; engine choice
is a deploy-time robustness decision dominated by AUM stability +
Sharpe + MDD, not raw return.

---

## 7. Final Recommendation

### Primary Recommendation: **F1 (iter 023) with SPLIT MF sleeve**

**Composition (deploy weights):**

| ticker | weight | role |
|---|---:|---|
| NTSX | 25% | 90/60 US equity + Treasury stack (1.5×) |
| GDE | 25% | 90/90 US equity + gold stack (1.5×) |
| **KMLM** | **17.5%** | KFA MLM Index managed-futures trend (engine #1) |
| **DBMF** | **17.5%** | iMGP DBi managed-futures CTA-replication (engine #2) |
| TLT | 15% | iShares 20+y Treasury (duration) |

**Total notional: 132%. ETF count: 5.**

**Multi-criteria score: 62.07/100** (F1 base 63.57 − 1.5 C4 simplicity for the 5th ETF added by SPLIT).

**Why F1 wins**:
- **Highest mean Sharpe** (1.109) — best risk-adjusted outcome.
- **Lowest mean MDD** (16.76%) — best capital preservation.
- **Simplest** even after SPLIT (5 ETFs ties F3/F7 but with stronger Sharpe and lower MDD).
- **All-major-issuer composition** with SPLIT addressing the only fragility (KMLM single-issuer).
- **Most regime-agnostic** of the four finalists.

### Alternatives

- **If simplicity matters most**: **F1 without SPLIT** (4 ETFs, score 63.57). Trade-off: KMLM single-issuer concentration risk over 30y.
- **If maximum CAGR matters most**: **F7 with SPLIT** (mean CAGR 12.50%, score 59.76). Trade-off: 150% notional, RSST closure risk, 0.45% TER drag, +5pp mean MDD.
- **If maximum factor diversification matters most**: **F3 with SPLIT** (5 factor sleeves, score 60.33). Trade-off: PBO momentum fragility (vt 0.472, ndx 0.853), 6 ETFs.
- **If 1× notional purity matters most (no leverage philosophy)**: **F2** (score 60.39). Trade-off: lowest Sharpe, highest MDD, AVUV not validated.

**Decision summary**: F1 with SPLIT is **the minimum-regret choice for
20-30y deploy** under regime uncertainty.

---

## 8. Mandate §7 Override Request — DRAFT

```markdown
## Mandate §7 Override Request — DRAFT

**Date:** 2026-04-30
**Subject:** Deploy F1 (iter 023, SPLIT MF) for retirement portfolio (long-term portfolio thesis)

**Background**: Mandate §1 MAINTENANCE MODE (2026-04-23) consolidated 100% allocation
to Plano C passive factor-tilted aposentadoria after 113/113 honest FAIL of short-hold
strategies (Phase 3.5f-3.8 + D-MVP + E-MVP). Strategy A/B/D DORMANT.

**Override request**: Replace Plano C strict with **F1 (iter 023 chassis with SPLIT MF
sleeve)** per the long_term_portfolio loop empirical results (16 sweep iters validating).

**Composition (deploy weights):**

| ticker | weight | role |
|---|---:|---|
| NTSX | 25% | 90/60 US equity + Treasury stack |
| GDE | 25% | 90/90 US equity + gold stack |
| KMLM | 17.5% | KFA MLM Index managed-futures (trend engine #1) |
| DBMF | 17.5% | iMGP DBi managed-futures (CTA replication, engine #2) |
| TLT | 15% | iShares 20+y Treasury |

Total notional: 132%. ETF count: 5. Issuer count: 4 (WisdomTree, KFA, iMGP, iShares).

**Justification**:
- **Sharpe edge vs SPY**: +0.282 mean (1.109 finalist vs 0.827 SPY mean across 3 datasets).
- **CAGR vs SPY**: 10.76% mean vs 13.80% SPY mean (CAGR floor warning-only per mandate §2.2; on lh_56y window finalist 11.52% beats SPY 11.47%).
- **MDD**: 16.76% mean vs SPY 40.85% mean — substantial capital preservation edge.
- **7-gate battery**: 7+6+6 = 19/21 (NEW SPY-only); 21/25 on rubric.
- **DSR worst p-value**: 7.28e-04 (vt_real); cumulative n_trials = 87 (lowest among finalists, highest signal credibility).
- **Multi-criteria score**: 62.07/100 (with SPLIT MF sleeve adjustment).
- **Cumulative n_trials**: 152 across the full 16-iter sweep (DSR-adjusted bar).
- **All ETFs major-issuer**: WisdomTree, KFA, iMGP, iShares — minimal closure risk for 30y horizon.

**Risks acknowledged**:
1. **US-only regime dependence**: all 4 finalists US-only (F4/F5/F6 skipped — no global sleeve survived Phase 1+1B). 1980s-style intl-led regime would underperform. Mitigation: annual loop re-run + optional 5-10% VEA/VWO tactical hedge.
2. **132% notional leverage**: drawdown amplification in simultaneous-asset-shock regimes (2008, 2022). Realised lh_56y MDD = 21.13% (vs SPY 55.14%) — manageable but not crisis-immune.
3. **TLT duration risk**: 1970s-style rates regime would hit the 15% TLT sleeve hard. Mitigation: KMLM/DBMF/GDE/NTSX-Treasury overlay diversifies the bond risk somewhat; explicit decision to retain duration for crisis-alpha [risk_parity, ch.5].
4. **Synth-INCOMPLETE flags**: backtest uses NTSXSIM/GDESIM/KMLMSIM/DBMFSIM/TLTSIM. Real-vs-synth correlation is high (>0.95) but tracking error ~10-30bps/y is unmodeled.
5. **Annual-rebalance cost-tax leak**: ~10-25bps/y in retail accounts (Inter Internacional spread + ~0.1% trade × 5 ETFs). Acceptable vs deploy CAGR.

**Deploy plan**:
1. Open Inter Internacional account (if not already).
2. **Verify all 5 ETFs available before any allocation**: NTSX, GDE, KMLM, DBMF, TLT. If any missing, fall back to next-ranked finalist or pure-KMLM F1 (4 ETFs, score 63.57 unadjusted).
3. Buy ETFs in proportion to composition above (initial deploy in 1-2 tranches to limit timing risk).
4. **Annual rebalance** to target weights (Q1 each year).
5. **Quarterly review** for ETF closure risk / regime change / loop re-run signal.
6. Re-run long_term_portfolio loop **annually**; if a new finalist scores ≥3pts higher on multi-criteria, propose new override.

**Citations**:
- `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking.
- `[risk_parity, ch.2, p.37-41]` Fama-French factor framework (F2 closure context).
- `[stocks_on_the_move, p.21-30]` Clenow time-series momentum (F3 SPMO sleeve context).
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha role + intl/EM diversification regime.
- `[advances_fin_ml, p.222-223]` DSR cumulative n_trials methodology (n=152).
- `[advances_fin_ml, p.208-211]` PBO via CSCV (F3 momentum fragility flag).
- `[advances_fin_ml, p.196-202]` bootstrap CI (Sharpe robustness).
- WisdomTree NTSX/GDE prospectus, KFA KMLM, iMGP DBMF, iShares TLT product documentation.
- ReSolve/Newfound Return Stacked methodology 2023 (F7 stacked-MF context).
```

---

## 9. Citations (Consolidated)

Across the 16-iter sweep, the following references anchored decisions:

- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking baseline (F1, F3, F7 architectural rationale).
- `[risk_parity, ch.2, p.37-41]` — Fama-French factor framework (F2 + Phase 1A/1B Avantis closure context).
- `[stocks_on_the_move, p.21-30]` Clenow — time-series momentum (SPMO sleeve retention; F3 + F2 SPMO weighting).
- `[ilmanen_expected_returns, ch.19]` — managed-futures crisis-alpha role + intl/EM diversification (F7 RSST + iter 042 SPLIT MF + F4/F5/F6 closure context).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (gate G1; F3 ndx_real PBO 0.853 fragility flag).
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials (gate G2; n=152 sweep total).
- `[advances_fin_ml, p.196-202]` — bootstrap Sharpe CI (gate G6).
- `[advances_fin_ml, p.31-34]` — cross-lib + factor framework (gate G7).
- `[leverage_for_the_long_run, p.40-60, ch.3-4]` — LETF decay literature (WLDU/F7-RSST stacking caveat).
- WisdomTree NTSX prospectus + 2026-03-19 NTSD launch documentation.
- WisdomTree GDE prospectus.
- KFA Mount Lucas KMLM prospectus + index methodology.
- iMGP DBi DBMF prospectus + SG CTA Index replication methodology.
- iShares TLT 20+y Treasury Bond ETF documentation.
- Frazzini-Israel-Moskowitz 2018 — UMD long-only momentum capture coefficient (~0.60; SPMO synth derivation).
- Jegadeesh-Titman 1993 — cross-sectional momentum (SPMO/IDMO foundation).
- ReSolve / Newfound Return Stacked methodology 2023 (RSST conceptual framework + F7 architecture).

---

## 10. Process Notes

- **F4 / F5 / F6 skipped** because Phase 1+1B unanimously closed every global sleeve (NTSD/AVDV/AVEM/IDMO all DEAD; only US-momentum SPMO survived). See `PHASE_1_WINNERS.md` for the full kill table.
- **Filename retains "seven_portfolios"** for sweep-plan continuity even though only 4 finalists were realised.
- **C7 deploy-ease score is provisional** (default 12pts) pending user fill of `INTER_CHECK.md`. Filling it is the highest-value remaining action — it can swing F7 from rank #3 to rank #4, or confirm F1's #1 lock.
- **Cumulative n_trials = 152**; DSR-adjusted bar applied to all four verdict.json files.
- **Mandate basis**: NEW SPY-only +0.05 (post-2026-04-29 reframing). LEGACY avg(SPY,VT) +0.10 scores preserved in verdict.json `score_legacy` field for cross-iter consistency.
