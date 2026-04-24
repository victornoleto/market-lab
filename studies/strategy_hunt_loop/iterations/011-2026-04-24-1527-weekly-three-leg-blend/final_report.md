# Iteration 011 — Final Report

**Date:** 2026-04-24 15:27
**Hypothesis:** Weekly-rebalance 3-leg vol-managed SPY+TLT+GLD blend
with inverse-variance weighting + Moreira-Muir portfolio variance-
scaling, single pre-committed cfg `vt15_Lw4_cap20_3leg_weekly` (target_vol=0.15,
lookback=4 weeks, max_leverage=2.0, periods_per_year=52, W-FRI rebalance).
**Cumulative n_trials after iter 011:** 4249.

---

## Verdict

🥉 **MARGINAL** (score **52/100**, `winner_conditions_met=False`,
**3/5** winner conditions met — regression from iter 010's 4/5).

**Kill criteria triggered**:

- ✅ **Kill #1 (thesis-falsification)** — weekly Sharpe regressed vs
  iter 010's daily 3-leg on **BOTH** real-data slots (spy Δ = −0.021,
  ndx Δ = −0.097). The hypothesis "weekly rebalance preserves the
  blend edge" is empirically falsified.
- ✅ **Kill #3 (score < 70)** — 52/100, −22 pts vs iter 010. Direction
  is done for this blend mechanism.
- ❌ Kill #2 (CAGR < 0.75 × bench) — 3/3 pass 0.8× floor, not triggered.
- ❌ Kill #4 (any dataset < 5/7 gates) — min is 5/7 (edu, ndx); spy 6/7.
  Not triggered.
- ❌ Kill #5 (cross-lib > 3pp) — max ΔCAGR 0.20 pp. Not triggered.

**Core structural finding**: the MDD control that made iter 010's
daily blend tier PROMISING (MDD 33-37% on real data) **collapses
under weekly rebalance** (MDD 47-49%, +10-14 pp). Vol-targeting with
`target_vol²/σ²_port` requires **daily** cadence to react to
intra-week vol spikes; at weekly granularity, a regime change between
rebalance dates happens entirely unhedged inside the week.

**DSR theoretical claim also falsified**: BASE_MEMORY (iter 010)
conjectured weekly would reduce the DSR n_trials deflator penalty.
Empirically the opposite: worst DSR p went **0.368 (iter 010) →
0.515 (iter 011)**. Root cause is T dropping from ~4280 (daily) to
~880 (weekly) which inflates `E[SR_max]` variance at fixed n_trials.

---

## Headline metrics (pre-committed cfg `vt15_Lw4_cap20_3leg_weekly`)

Weekly-annualised Sharpe and CAGR (sqrt(52)); comparison against
**custom weekly benchmarks** (weekly SPY/QQQ b&h on same windows).
The frozen `scoring.BENCHMARKS` are daily-annualised and not directly
comparable; cross-frequency numbers appear in `verdict.json` under
`secondary_comparison_vs_frozen_daily_benchmarks` for transparency.

| dataset | Sharpe (Δ weekly bench) | CAGR | MDD | gates | DSR p | Δ vs iter 010 daily |
|---|---|---|---|---|---|---|
| educational | **0.942** (+0.277 vs 0.665) | 17.62% | **47.19%** | **5/7** | 0.235 | Sh −0.047 / MDD **+13.52 pp** |
| spy_real    | **1.019** (+0.087 vs 0.932) | 18.71% | **47.19%** | **6/7** | 0.298 | Sh −0.021 / MDD **+13.52 pp** |
| ndx_real    | **0.898** (−0.109 vs 1.008) | 17.53% | **48.99%** | **5/7** | 0.515 | Sh −0.097 / MDD **+11.56 pp** |

**Sharpe edge gate** (weekly bench + 0.10):
- edu Δ +0.277 → **PASS**
- spy Δ +0.087 → **FAIL** (short by 0.013)
- ndx Δ −0.109 → **FAIL** (negative)

**Only 1/3 passes**, down from iter 010's 2/3.

**CAGR floor** (0.8 × weekly bench): 3/3 pass.

**MDD ceiling** (weekly bench + 5 pp):
- edu 47.19% vs 54.62% + 5 = 59.62% → **PASS**
- spy 47.19% vs 31.81% + 5 = 36.81% → **FAIL** (+10.4 pp over ceiling)
- ndx 48.99% vs 35.06% + 5 = 40.06% → **FAIL** (+8.9 pp over ceiling)

**1/3 passes** on MDD ceiling (iter 010 had 3/3). This is the
sharpest regression — weekly rebalance abandons ~half the MDD control.

---

## Gates breakdown (detailed)

| gate | educational | spy_real | ndx_real |
|---|---|---|---|
| G1 PBO | PASS (N=1 vacuous) | PASS (N=1 vacuous) | PASS (N=1 vacuous) |
| G2 DSR | FAIL (p=0.235) | FAIL (p=0.298) | FAIL (p=0.515) |
| G3 WF 6/8 | **FAIL (5/8)** | PASS (6/8) | **FAIL (5/8)** |
| G4 OOS 70/30 | PASS (+0.646) | PASS (+0.654) | PASS (+0.627) |
| G5 FWD post-2020 | PASS (+0.599) | PASS (+0.599) | PASS (+0.644) |
| G6 boot 99.9% CI | PASS (+0.277) | PASS (+0.242) | PASS (+0.049) |
| G7 cross-lib ±3pp | PASS (0.021 pp) | PASS (0.195 pp) | PASS (0.053 pp) |
| **total** | **5/7** | **6/7** | **5/7** |

**New failure vs iter 010**: G3 WF on educational degrades 6/8 → 5/8;
ndx holds at 5/8; spy holds at 6/8 (was 7/8 in iter 010, now 6/8).

**DSR trajectory**:
- iter 008 (2-leg daily): worst p 0.332
- iter 010 (3-leg daily): worst p 0.368
- iter 011 (3-leg weekly): **worst p 0.515** — worst of the three.

The weekly cadence reduces T (number of return obs) from ~4280 to
~880, which inflates `E[SR_max]` at fixed n_trials=4249 per the DSR
formula. Periodic observed SR grows by √(252/52) ≈ 2.20, which is
almost exactly the √(T_daily/T_weekly) ≈ 2.21 the benchmark grows by
— net: nearly zero first-order change, but second-order terms
(G6 CI narrower margin on ndx, lower robustness multiplier on weekly
autocorrelation) push p-values slightly **worse**.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **10** | 25 | 1/3 datasets beat +0.10 (edu only) |
| 2 Gates | **17** | 25 | edu 5/7 (3 pts at threshold), spy 6/7 (5 pts), ndx 5/7 (5 pts at th+1), cross-ds bonus +4 |
| 3 DSR | 0 | 15 | worst p 0.515 (iter 010: 0.368); worst tier threshold not crossed |
| 4 CAGR floor | 15 | 15 | 3/3 datasets ≥ 0.8 × weekly bench |
| 5 MDD ceiling | **5** | 15 | 1/3 (only edu); spy + ndx both > bench + 5 pp |
| 6 Robustness | 5 | 5 | 9/9 sub-windows Sharpe > 0 (weekly-annualised) |
| **total** | **52** | 100+5 | tier: **MARGINAL** |

Delta vs iter 010: **Δ = −22 points**. The regression is concentrated
in (a) Sharpe edge −10 pts (iter 010 2/3 → iter 011 1/3), (b) Gates
−2 pts (iter 010 19 → iter 011 17 — edu drops from 6/7 to 5/7
effectively at threshold), (c) MDD ceiling −10 pts (iter 010 3/3 →
iter 011 1/3 — the largest single driver).

## Winner conditions

| condition | iter 010 | iter 011 | change |
|---|---|---|---|
| 1. Sharpe ≥ bench + 0.10 on ≥ 2/3 | ✅ (2/3) | ❌ (1/3) | **regression** |
| 2. Gate battery cross-dataset | ✅ | ✅ | held |
| 3. DSR worst p < 0.05 | ❌ (0.368) | ❌ (0.515) | worsened |
| 4. CAGR floor on ≥ 2/3 | ✅ (3/3) | ✅ (3/3) | held |
| 5. MDD ceiling on ≥ 2/3 | ✅ (3/3) | ❌ (1/3) | **regression** |
| **total** | **4/5** | **3/5** | −1 |

Two conditions regressed: Sharpe edge and MDD ceiling — both point to
the same root cause (weekly rebalance can't react to intra-week vol
regime changes).

---

## Portfolio diagnostics

### Weekly leg correlations (measured on each dataset's weekly window)

| dataset | ρ_w(eq, bd) | ρ_w(eq, gd) | ρ_w(bd, gd) |
|---|---|---|---|
| educational | −0.243 | +0.074 | +0.142 |
| spy_real    | −0.241 | +0.148 | +0.193 |
| ndx_real    | −0.163 | +0.107 | +0.214 |

Compared to daily (iter 010): SPY-TLT correlation is *weaker* at
weekly scale (−0.24 vs −0.30 daily). This is expected — daily
stock-bond flight-to-quality moves are concentrated on specific
stress days that partially smooth out on weekly compounding. The
diversification return from negative correlation is therefore
*reduced* at weekly cadence, contributing to the Sharpe regression.

### Median leg weights (weekly)

| dataset | SPY/QQQ | TLT | GLD |
|---|---|---|---|
| educational | 0.28 | 0.33 | 0.24 |
| spy_real    | 0.29 | 0.30 | 0.27 |
| ndx_real    | 0.21 | 0.34 | 0.31 |

Weights still cluster near 1/3 each (naïve RP fixed point), mirroring
iter 010. Ndx weights still under-allocate QQQ (0.21 vs iter 010
daily 0.24), for the same reason: QQQ realized vol is higher than
TLT/GLD on daily scale, and weekly resampling preserves most of that
asymmetry.

### Scale cap-hit + turnover

| dataset | cap_hit@2.0 | turnover/yr (3 legs summed, weekly cadence) |
|---|---|---|
| educational | **96.1%** | 41.3 |
| spy_real    | **96.7%** | 40.7 |
| ndx_real    | 93.7% | 41.2 |

**Cap-hit frequency jumped from ~86% daily to ~95% weekly.** At
weekly cadence, σ²_port over 4 weeks is structurally lower than
daily σ² over 21 days (more compounding smoothing), so the scale
`target_var²/σ²_port` saturates at 2.0 more often. The
vol-targeting mechanism is effectively neutered — the strategy runs
near max leverage most of the time, which explains the MDD
ballooning.

Turnover: 41/yr total across 3 legs ≈ **13.6/yr per leg** (vs iter
010 daily's ~10/yr per leg). Weekly cadence with 4-week lookback
changes weights more aggressively per rebalance because the
lookback window moves 25%/step vs daily's ~5%/step. **Turnover
went UP, not down**, contrary to the hypothesis that weekly reduces
friction. This is another structural surprise.

---

## What worked / what didn't

**What worked**:

- **Structural implementation is clean.** 8 TDD specs all green:
  weekly compound resample is exact, lookback lag prevents look-ahead,
  2-leg degenerate limit recovered, cost model applied at weekly
  cadence correctly. G7 cross-lib parity ≤ 0.20 pp on all 3 datasets.
- **G6 bootstrap CI still strictly positive** on all 3 datasets —
  the blend's *directional* edge survives weekly rebalance (ci_low
  +0.05 to +0.28); it's the *magnitude* that erodes.
- **Robustness bonus 5/5** held (9/9 sub-windows positive weekly
  Sharpe). The strategy is still not concentrated in a single
  sub-regime.
- **Educational Sharpe beats weekly bench +0.277** — on the 21y
  GLD-aligned window, the 3-leg weekly blend still delivers
  measurable diversification uplift vs weekly SPY b&h. Edu window is
  broad enough that low-frequency diversification dominates
  high-frequency vol-adaptation.
- **CAGR floor 3/3** — weekly rebalance doesn't destroy the
  compounding engine; returns are still in the 17-19% range annualised.

**What didn't work**:

- **MDD control collapses.** Across all 3 datasets, MDD jumps +10-14
  pp vs iter 010 daily. Root cause: vol-targeting's
  `target_var²/σ²_port` requires daily measurement + daily rebalance
  to capture regime shifts before they compound. At weekly cadence,
  a regime change between Fridays is entirely unhedged inside the
  week — the strategy sits at max leverage through the event.
  Cap-hit frequency climbed from 86% → 95%, confirming the vol-target
  is effectively not binding most of the time.
- **Cross-asset diversification weakens at weekly scale.** Weekly
  SPY-TLT correlation is −0.24 (vs daily −0.30); equity-gold and
  bond-gold correlations are both slightly more positive at weekly
  cadence. The diversification return
  `[risk_parity, p.5, p.109-110]` is smaller, reducing the blend's
  structural edge.
- **DSR got WORSE, not better.** Iter 010 conjecture ("weekly reduces
  DSR deflator") was theoretically mistaken and empirically falsified.
  The DSR formula uses T = number of observations; cutting T by ~5×
  inflates the expected-max benchmark by √5×, exactly cancelling the
  gain in periodic observed Sharpe. Worst p 0.368 → 0.515.
- **Turnover went UP, not down.** Weekly cadence with 4-week lookback
  moves weights ~25%/rebalance vs daily's ~5%/rebalance; per-leg
  turnover rose from ~10/yr to ~13.6/yr. Cost drag didn't go down —
  the structural argument for weekly as "less-friction" fails.
- **Kill #1 + Kill #3 triggered.** Pre-committed kill criteria
  executed as designed; no post-hoc rationalisation. The direction
  is a clean structural dead-end for this specific mechanism.

---

## Main lesson (for future iterations)

**Vol-managed variance-targeting requires DAILY cadence — it is NOT
cadence-agnostic.** The mechanism's edge comes from fast reaction to
realized-vol regime shifts; weekly rebalance surrenders the ability
to de-lever before a regime change compounds into drawdown. This is
structurally different from, say, cross-sectional momentum (which
Jegadeesh-Titman 1993 show works at monthly cadence) or value (which
works at annual cadence): **variance-scaling has a time-scale
intrinsic to its signal** and moving away from daily breaks the
mechanism.

Corollary: the iter 008 and iter 010 score tie at 74/100 is NOT a
"cadence-independent ceiling" — it's a **daily-specific ceiling on
the blend family**. Weekly, monthly, quarterly would each score
worse, not equal.

This is a structurally useful negative result. It tells us:

1. **DSR ceiling attacks via timeframe change are UNAVAILABLE for
   this mechanism.** The blend family must compound on daily
   information; DSR penalty at n_trials≈4250 is simply a fact of
   the hunt-loop budget.

2. **The productive path is orthogonal information** (Option C —
   meta-labeling on iter 008 daily, AFML ch.3) or **asymmetric
   overlays** (Option B' — raw T10Y3M + equity-only haircut on iter
   008 daily). Both preserve the daily cadence that makes
   vol-targeting work.

3. **Moreira-Muir (2017)'s canonical MONTHLY regime does NOT
   transfer to shorter rebalance frequencies + GLD leg.** The paper's
   claim that variance-scaling works across sampling frequencies is
   specific to their universe (Fama-French monthly factors) — for
   multi-asset blends with gold/bonds, the signal-execution cadence
   matters structurally.

---

## Structural observations (for DEAD_ENDS.md)

**New structural dead-end** (append to DEAD_ENDS.md under "From
iteration 011"):

> **Weekly-rebalance vol-managed 3-leg blend (SPY+TLT+GLD,
> inverse-variance + Moreira-Muir variance-scaling) at `W-FRI`
> cadence with 4-week lookback.** Sharpe regresses vs iter 010's
> daily counterpart on all 3 datasets (edu −0.047, spy −0.021,
> ndx −0.097). MDD ceiling jumps 10-14 pp on real data (37% → 47-49%)
> — vol-targeting mechanism requires daily cadence to react to
> intra-week regime shifts. Cap-hit frequency 86% → 95% at max
> leverage (vol-target no longer binding). DSR *worsens* (worst
> p 0.368 → 0.515) because reducing T inflates `E[SR_max]` at fixed
> n_trials per the DSR formula. Turnover goes UP (~10/yr per leg →
> ~13.6/yr per leg). Kill #1 + Kill #3 triggered. **DO NOT re-test
> with minor variations** (different resample cadence W-MON/W-WED,
> different lookback 2-8 weeks, different target_vol 0.10/0.20). The
> structural bottleneck is the cadence mismatch between signal
> (daily vol regime) and execution (weekly rebalance), not a
> parameter choice.

**By extension** (weaker claim, but worth noting): **any rebalance
cadence slower than daily is likely to regress for vol-managed
variance-targeting mechanisms on multi-asset blends.** Monthly
rebalance (~21 trading days) would likely score even lower than
weekly. Not tested, but the gradient of MDD-damage with cadence is
monotone by structural argument — slower rebalance = more regime
shifts occur unhedged.

---

## Citations used

**Books (absorbed knowledge base)**:

- `[systematic_trading, p.40, ch.2]` — volatility standardisation
  primitive, nominally cadence-agnostic (but the iteration shows
  otherwise for this specific blend mechanism).
- `[systematic_trading, p.144, ch.9]` — target_vol 15% calibration.
- `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 cap.
- `[risk_parity, p.5, p.16, p.80-81, p.109-110]` — diversification
  return, SPY-TLT-GLD multi-asset argument.
- `[risk_parity, p.10-11, ch.1]` — naïve risk parity N-asset form
  generalises to weekly (confirmed structurally but edge regresses).
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag on whichever cadence.
- `[advances_fin_ml, p.208-211]` — G1 PBO N=1 vacuous.
- `[advances_fin_ml, p.222-223]` — G2 DSR deflator (the **T** in the
  formula is the bottleneck that fell under weekly; iter 011 is the
  first hunt-loop iteration to stress-test this dimension empirically).
- `[advances_fin_ml, p.31-34]` — G7 cross-lib parity held at 0.02-0.20
  pp (weekly implementation correct).
- `[leverage_for_the_long_run, p.9]` — SPY regime asymmetry exists at
  all cadences, but **fast reaction to it** requires daily rebalance.

**External**:

- Moreira & Muir (2017), *JoF* 72(4), 1611-1644. DOI
  [10.1111/jofi.12513](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12513).
  Paper's canonical regime is *monthly* — iter 011's weekly test is
  partway between daily and monthly. The empirical result suggests the
  paper's variance-scaling edge is much stronger at monthly than daily
  (where it barely works on modern data — see iter 005 +0.09 Sharpe
  one-asset). The blend version doesn't transfer back to monthly-scale
  naturally.
- Carver (2015), *Systematic Trading* — target_vol is presented as
  cadence-independent but the book's live examples all use daily
  rebalance on directional signals, not portfolio-variance targeting.

---

## Next iteration suggestions

Iter 011 closes Option F as a dead-end for the blend mechanism.
**Two directions remain structurally untested**, both preserve daily
cadence:

1. **[OPTION C — META-LABELING on iter 008 blend]** (AFML ch.3).
   Secondary ML model predicts bar-level profitability of iter 008's
   daily 2-leg base using cross-sectional / macro features the
   blend can't see (cross-asset momentum, credit spreads via EBP,
   VIX term structure, breadth). Orthogonal by construction; only
   direction that adds *informationally independent* signal beyond
   vol-regime. Highest engineering cost (~2-3 h wall-time), highest
   potential Sharpe uplift (+0.20-0.30 if the meta-model works).
   Addresses the DSR ceiling via the observed-Sharpe side of the
   equation rather than the T side (which iter 011 just confirmed
   is not a viable attack).

2. **[OPTION B' — ASYMMETRIC MACRO OVERLAY on iter 008 blend]**
   (from iter 009 final_report, still untested). Raw (≤ 5d smoothed)
   T10Y3M + haircut on EQUITY LEG ONLY (bond leg keeps full weight
   during recessions). Addresses iter 009's two failure modes
   (smoothing destroyed lead-time, symmetric haircut forfeits
   flight-to-quality). Lowest engineering cost (~30 min),
   expected +0.03-0.08 Sharpe if asymmetry isolates benefit.

**Picking order for iter 012**: Option B' first (cheap confirmation
of the asymmetric-overlay principle — iter 009 ruled out smoothed
symmetric, but the remaining combinatorial quadrant is genuinely
novel), then Option C (higher-ceiling attack if B' succeeds or if
the hunt-loop wants to force a different information source).

**Also flagged as deeper backlog** in BASE_MEMORY but untested:
return-stacked ETF rotation (NTSX/NTSI/NTSE), HMM regime-switching
on stock-bond correlation. Both are structurally distinct enough
to merit exploration after B' + C.

---

## Hunt-loop picture after iter 011

- **iter 008** (3-leg 2-leg daily): 74/100, 4/5 winner conds
- **iter 010** (3-leg daily): 74/100, 4/5 winner conds (tied iter 008)
- **iter 011** (3-leg weekly): 52/100, 3/5 winner conds (**regression**)

The blend family's **daily-cadence ceiling is 74/100**; slower
cadences score STRICTLY worse. DSR at cumulative n_trials ≈ 4250 is
a structural bottleneck that **cannot be relaxed by timeframe
change**. Breaking through requires either (a) qualitatively
different information (meta-labeling, credit/macro overlay with
lead-time), or (b) a different universe / portfolio structure
(return-stacked ETFs, factor rotation). Iter 011 narrows the search
space by removing an entire direction (timeframe change) that looked
theoretically promising but empirically fails.
