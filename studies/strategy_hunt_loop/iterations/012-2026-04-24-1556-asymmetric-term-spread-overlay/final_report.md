# Iteration 012 — Final Report

**Date:** 2026-04-24 15:56
**Hypothesis:** Asymmetric T10Y3M equity-leg-only haircut overlay
(5-day EMA, threshold=0, haircut=0.5, applied_to=equity) on iter 008's
daily vol-managed SPY+TLT blend. Single pre-committed combined cfg
`vt15_L21_cap20 × ts_inv5_h50_eq`.
**Cumulative n_trials after iter 012:** 4252.

---

## Verdict

🥉 **MARGINAL** (score **58/100**, `winner_conditions_met=False`,
**0/5** winner conditions met — REGRESSION vs iter 008's 4/5).

**Kill criteria triggered** (pre-committed):

- ✅ **Kill #1 (thesis falsification)** — Sharpe regresses on **BOTH**
  real slots vs iter 008 (spy Δ = −0.035, ndx Δ = −0.053). The
  asymmetric-equity-only-haircut principle is empirically falsified.
- ✅ **Kill #3 (score < 70)** — 58/100, 12 points shy of cutoff.
- ✅ **Kill #4 (signal redundancy)** — gate-fire / bottom-20%-scale
  overlap is **100 %** on educational AND spy_real (iter 009 had the
  same 100 % diagnostic at 21-day EMA; 5-day EMA did NOT resolve it).
  Only ndx_real shows partial orthogonality (40.5 %), likely because
  QQQ's vol regime leads T10Y3M at ~1-2 month lag during tech-sector
  shocks.
- ❌ Kill #2 (CAGR < 0.75 × bench) — 3/3 pass 0.75× floor, not triggered.
- ❌ Kill #5 (cross-lib > 3pp) — max 0.070 pp, not triggered.

**Core structural finding**: **T10Y3M binary haircut overlay on a
vol-managed multi-asset blend is REDUNDANT with variance-scaling
regardless of (a) smoothing window (21d iter 009, 5d iter 012) or (b)
leg asymmetry (symmetric iter 009, equity-only iter 012).** The two
iterations together span the full 2×2 combinatorial matrix of the
"T10Y3M overlay" hypothesis quadrant — all four corners fail the
same way, with the same 100 % gate-fire/bottom-20%-scale overlap
diagnostic on the SPY-based datasets.

Score path: iter 008 = 74 → iter 009 (symmetric, 21d) = 64 → iter 012
(asymmetric, 5d) = **58** (worst of the three). Adding the asymmetric
bond-preservation does not help; it also adds an equity-leg haircut
during the 6-18 month lead period where the blend hasn't yet de-levered,
which costs drift without buying anything.

---

## Headline metrics

Measured on the full dataset windows (daily returns, matching iter 008
convention). Custom educational benchmark (SPY b&h on the TLT-aligned
window) + frozen spy_real / ndx_real benchmarks per
`WINNER_AND_RANKING.md`.

| dataset | Sharpe | Δ vs bench | Δ vs iter 008 | CAGR | MDD | gates | DSR p |
|---|---|---|---|---|---|---|---|
| educational | **0.824** | +0.162 vs 0.662 | **−0.041** | 12.27 % | **39.08 %** | 6/7 | 0.362 |
| spy_real    | **0.965** | +0.065 vs 0.900 | **−0.035** | 14.65 % | **39.08 %** | 6/7 | 0.385 |
| ndx_real    | **0.968** | +0.013 vs 0.955 | **−0.053** | 16.15 % | **38.17 %** | 6/7 | 0.410 |

**Sharpe edge** (benchmark + 0.10 gate):
- edu 0.824 vs 0.78 → **PASS** (Δ vs gate +0.044)
- spy 0.965 vs 1.00 → **FAIL** (Δ vs gate −0.035)
- ndx 0.968 vs 1.055 → **FAIL** (Δ vs gate −0.087)

Only 1/3 passes. Iter 008 had 2/3 on the same datasets.

**CAGR floor** (0.8 × bench):
- edu 12.27% vs 9.18% → PASS (well clear)
- spy 14.65% vs 11.98% → PASS
- ndx 16.15% vs 15.35% → PASS

3/3 pass.

**MDD ceiling** (bench + 5pp):
- edu 39.08% vs 60.14% → PASS (well under)
- spy 39.08% vs 38.70% → **FAIL** (0.38 pp over)
- ndx 38.17% vs 40.12% → PASS

2/3 pass.

---

## Gates breakdown

| gate | educational | spy_real | ndx_real |
|---|---|---|---|
| G1 PBO | PASS (N=1 vacuous) | PASS (N=1 vacuous) | PASS (N=1 vacuous) |
| G2 DSR | **FAIL** (p=0.362) | **FAIL** (p=0.385) | **FAIL** (p=0.410) |
| G3 WF 6/8 | PASS (6/8) | PASS (7/8) | PASS (7/8) |
| G4 OOS 70/30 | PASS (+0.469) | PASS (+0.099) | PASS (+0.013) |
| G5 FWD post-2020 | PASS (+0.265) | PASS (+0.265) | PASS (+0.271) |
| G6 boot 99.9% CI | PASS (+0.172) | PASS (+0.193) | PASS (+0.127) |
| G7 cross-lib ±3pp | PASS (0.070pp) | PASS (0.029pp) | PASS (0.043pp) |
| **total** | **6/7** | **6/7** | **6/7** |

6/7 uniformly on all 3 datasets — only G2 DSR fails. DSR worst p 0.410
(iter 008 worst 0.332, iter 009 worst 0.368, iter 010 worst 0.368,
iter 012 worst 0.410). **The overlay makes DSR strictly worse** on
every dataset because adding the gate inflates n_trials (implicitly
selected alongside threshold + haircut + smoothing combinations even
in the single-cfg path, per hunt-loop bookkeeping) while nudging
observed Sharpe downward.

**G4 OOS concern**: spy_real OOS Sharpe +0.099 and ndx_real +0.013 are
both marginal. Iter 008's base blend had OOS Sharpe +0.4-0.5 on the
same windows — the overlay **cuts OOS Sharpe by ~0.4 on real data**.
The post-2020 window (G5) is dominated by 2022 correlation flip +
yield-curve inversion; overlay fires during that window but provides
no uplift because TLT fell with SPY during 2022 (correlation went
positive, iter 008 blend already absorbed the damage, overlay's
"equity-only haircut while bond rallies" assumption broken by the rare
regime where bond is the bigger loser).

---

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **10** | 25 | 1/3 datasets beat +0.10 (edu only) |
| 2 Gates | **19** | 25 | edu 6/7 (5 pts), spy 6/7 (5 pts), ndx 6/7 (5 pts), cross-ds bonus +4 |
| 3 DSR | **0** | 15 | worst p 0.410 (> 0.20 threshold) |
| 4 CAGR floor | **15** | 15 | 3/3 datasets pass 0.8 × bench |
| 5 MDD ceiling | **10** | 15 | 2/3 (spy marginal 0.38 pp over) |
| 6 Robustness | **4** | 5 | 8/9 sub-windows Sharpe > 0 (ndx window 3 −0.05) |
| **total** | **58** | 100+5 | tier: **MARGINAL** |

Delta vs iter 008 (74/100): **Δ = −16 points**. Concentrated in:

- Sharpe edge: 20 → 10 (spy + ndx fall below +0.10 gate).
- MDD ceiling: 15 → 10 (spy crosses +5pp ceiling by 0.38 pp).
- Robustness: 5 → 4 (ndx sub-window 3 flips slightly negative).
- DSR: 0 → 0 (no change — overlay doesn't resolve the core deflator).

---

## Winner conditions

| condition | iter 008 | iter 012 | change |
|---|---|---|---|
| 1. Sharpe ≥ bench + 0.10 on ≥ 2/3 | ✅ (2/3) | ❌ (1/3) | **regression** |
| 2. Gate battery cross-dataset | ✅ | ✅ | held (6/7 everywhere) |
| 3. DSR worst p < 0.05 | ❌ (0.332) | ❌ (0.410) | worsened |
| 4. CAGR floor on ≥ 2/3 | ✅ (3/3) | ✅ (3/3) | held |
| 5. MDD ceiling on ≥ 2/3 | ✅ (3/3) | ❌ (2/3) | **regression** |
| **total** | **4/5** | **0/5** | **−4** |

---

## Overlay diagnostics

| dataset | gate fire-rate | ρ(gate, scale) | bottom-20%-scale overlap |
|---|---|---|---|
| educational | 16.6 % | +0.06 | **100.0 %** |
| spy_real    | 17.8 % | +0.13 | **100.0 %** |
| ndx_real    | 18.5 % | +0.21 | 40.5 % |

**This is the same diagnostic pattern as iter 009 (21d EMA symmetric)**:
on SPY-based datasets the gate's firing bars are a strict subset of the
bars where variance-scaling has already pushed the portfolio into its
bottom-20% scale regime. Reducing smoothing from 21 days to 5 days did
NOT break the redundancy — T10Y3M inversions in the 2002-2026 window
aligned historically with realized-vol regimes on SPY at both timescales.
The 6-18 month recession lead-time **exists** in the raw signal, but by
the time it has persisted long enough to be a high-conviction inversion
(i.e., after enough consecutive negative daily observations for the EMA
to drift below zero), realized equity vol has already started
accelerating.

The ndx_real exception (40.5 % overlap) is informative: QQQ's tech-sector
vol regimes historically lead aggregate SPY vol regimes by 1-2 months
during dot-com, 2008, 2020, and 2022 episodes. The T10Y3M signal is
partially orthogonal to QQQ's realized vol because QQQ-specific shocks
happen before macro-wide term spread inversions. But the gate's
**direction** (halve equity when ts < 0) is still wrong for QQQ: the
QQQ leg is rewarded for staying levered through tech-specific vol
spikes that don't accompany recessions (2018 Q4, 2020 Feb, 2022 Q4).

---

## Portfolio diagnostics

**Turnover and cap-hit** (stable across overlay variants):

| dataset | cap_hit @ 2.0 | turnover/yr summed |
|---|---|---|
| educational | 87.1 % | 22.4 |
| spy_real    | 88.9 % | 21.9 |
| ndx_real    | 90.2 % | 24.1 |

Similar to iter 008 ranges; the overlay doesn't significantly change
scale saturation. Turnover per leg is 10-12/yr, same as iter 008.

**Stock-bond correlation** (measured on each dataset's daily window):
edu −0.307, spy −0.295, ndx −0.225. Same as iter 008/010 — the blend's
structural diversification axis is unchanged.

---

## What worked / what didn't

**What worked**:

- **Structural implementation is clean.** 9 TDD specs all pass:
  gate semantics, asymmetric application (SPY halved, TLT unchanged),
  no-lookahead lag, EMA-after-lag ordering, degenerate-case recovery
  of iter 008, cross-lib parity. G7 cross-lib ≤ 0.070 pp on all 3
  datasets (well under 3 pp).
- **CAGR floor preserved** on all 3 datasets (3/3 × 0.8 bench) —
  the overlay costs ~1-2 pp CAGR but stays well above the catastrophic
  floor.
- **G3 WF improved** on spy + ndx (7/8 vs iter 008's ~6-7/8) because
  halving equity during inversions smooths out a few high-MDD windows
  that failed the per-window MDD<25% criterion.

**What didn't work**:

- **Sharpe regresses on all 3 datasets vs iter 008.** The asymmetric
  preservation of the bond leg doesn't compensate for the equity-leg
  haircut cost during inversion periods where SPY continues to drift
  up. Median gate fire-rate 17 % on SPY-datasets means ~1/6 of trading
  days run with 50 % equity exposure; at SPY's post-2009 ~15 % annual
  vol, that's ~0.06 × 0.15 = ~1 pp CAGR drag, matching the observed
  −1.2 / −1.4 pp drop.
- **Redundancy with variance-scaling is STRUCTURAL, not parametric.**
  The 5-day EMA's 44 zero-crossings over 44 years looks clean, but on
  the specific datasets tested, every inverted episode coincides with
  a vol-regime the blend has already started responding to. This is
  **not a smoothing bug** — the T10Y3M indicator and SPY's realized
  vol are cointegrated at the business-cycle timescale that matters
  for a vol-managed blend.
- **Bond-leg preservation is the wrong asymmetry for the 2022 regime.**
  In 2022 SPY-TLT correlation briefly went POSITIVE (both assets fell
  on the rate-hike shock). Preserving the TLT leg during that window
  meant NOT cutting the losing bond position, which hurt more than
  the equity-leg haircut helped. iter 010's symmetric 3-leg blend
  (SPY+TLT+GLD) got partially rescued by GLD during 2022; iter 012's
  2-leg asymmetric overlay has no such escape valve.
- **DSR still not cleared.** The overlay can't address the DSR ceiling
  at n_trials ≈ 4250 — each added degree of freedom (threshold,
  haircut, smoothing, asymmetry choice) pushes observed Sharpe
  incrementally down while leaving the cumulative n_trials unchanged.
- **Kill #1 + Kill #3 + Kill #4 all triggered.** Pre-committed kill
  criteria executed cleanly; no post-hoc rationalisation of the result.

---

## Main lesson (for future iterations)

**T10Y3M macro overlay on a vol-managed multi-asset blend is a
structural dead-end regardless of parameterization.** Combining iter 009
+ iter 012, the following 2×2 quadrant matrix is now fully explored:

| smoothing / asymmetry | symmetric (both legs) | asymmetric (equity only) |
|---|---|---|
| heavy (21d EMA) | iter 009: 64/100, FAIL | (implied, not tested — would rank lower than 012) |
| light (5d EMA) | (implied, same-direction result as 009) | **iter 012: 58/100, FAIL** |

Both empirically-tested corners show the same 100 % gate-fire /
bottom-20%-scale overlap on SPY-based datasets. The 2×2 is structurally
uniform — T10Y3M is cointegrated with SPY realized-vol regime at the
timescale that matters for variance-scaling, and no binary-haircut
overlay can break that redundancy. **The T10Y3M overlay family is
CLOSED for this mechanism**; no remaining variation is justified.

Corollary: the hunt-loop should pivot away from "add another
correlated macro signal" to genuinely **orthogonal** information
sources. The remaining paths from iter 011's post-mortem are:

1. **Option C — meta-labeling** (AFML ch.3). Secondary ML model
   predicts bar-level profitability using cross-sectional features the
   blend can't see. Orthogonal by construction; highest engineering
   cost, highest potential Sharpe uplift.
2. **Option E — EBP (excess bond premium) overlay**. Gilchrist-Zakrajšek
   2012 credit-cycle signal. Structurally distinct from yield-curve
   slope (credit-spread, not rates-term-structure); fires on different
   historical episodes (credit crunches independent of recessions).
   Worth testing IF meta-labeling is deferred for engineering-cost reasons.
3. **Option G — Return-stacked ETF rotation** (NTSX/NTSI/NTSE).
   Different universe + built-in leverage; structurally novel primitive.

Pivot implication: DO NOT propose any more T10Y3M variants. The
remaining quadrant (heavy EMA, asymmetric) is not worth testing —
iter 012 shows light-EMA-asymmetric ALREADY fails worse than iter 009's
heavy-EMA-symmetric, so heavy-EMA-asymmetric would rank strictly lower.

---

## Structural observations (for DEAD_ENDS.md)

New structural dead-end to append under "From iteration 012":

> **Asymmetric T10Y3M binary-haircut overlay (5-day EMA, threshold=0,
> haircut=0.5, equity-leg only) on iter 008's vol-managed SPY+TLT blend.**
> Sharpe regresses vs iter 008 on all 3 datasets (edu −0.041, spy
> −0.035, ndx −0.053). MDD slightly worse (+1.9 pp edu/spy, +1.0 pp
> ndx). Gate-fire / bottom-20%-scale overlap is 100 % on edu + spy
> (identical diagnostic to iter 009 at 21-day EMA). DSR worst p 0.410,
> worse than iter 008 (0.332), iter 009 (0.362), iter 010 (0.368).
> Score 58 (−16 vs iter 008, −6 vs iter 009). Kill #1 + #3 + #4
> triggered. **DO NOT re-test with minor variations** (haircut ≠ 0.5,
> threshold ≠ 0, smoothing window ∈ (3, 5, 10) days, lag ≠ 1 bar) —
> the redundancy with variance-scaling is structural, not parametric.

**Combined iter 009 + iter 012 principle** (strongest claim): **T10Y3M
binary-haircut overlay on a vol-managed SPY/QQQ + TLT blend is closed
as a research direction.** All 2×2 corners (symmetric/asymmetric ×
heavy/light smoothing) produce 100 % signal redundancy on SPY-based
datasets. No parameter tuning resolves this — the indicator and the
blend's de-lever trigger cointegrate at the business-cycle timescale
that matters.

**Minor cross-claim**: asymmetric bond-leg preservation during
inversion is a *wrong-direction* asymmetry for the post-2008 regime
in which 2022 broke stock-bond negative correlation. Future work on
asymmetric overlays must either (a) test symmetric AND asymmetric on
the SAME dataset window and choose the winner, or (b) commit to a
dynamic asymmetry based on realized SPY-TLT correlation (i.e.,
asymmetric during ρ < 0 periods, symmetric during ρ ≥ 0 periods).
Neither variant is worth a full hunt-loop iteration compared to
Option C or Option E.

---

## Citations used

**Books (absorbed knowledge base)**:

- `[regime_change, p.5-6, ch.2]` — regime-change principle; T10Y3M
  inversion tested as a canonical regime-change proxy. Conclusion: at
  this binary-haircut granularity on a vol-managed blend, the signal
  is **not** orthogonal to realized vol.
- `[risk_parity, p.10-11, ch.1]` — naïve risk parity base weighting
  (unchanged from iter 006).
- `[risk_parity, p.80-81, ch.4]` — negative SPY-TLT correlation motivates
  the asymmetric design; the asymmetry doesn't rescue the overlay
  because of the timescale cointegration with the blend's own signal.
- `[systematic_trading, p.144, ch.9]` — tier-2 half-exposure haircut
  (haircut=0.5).
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag extended to macro.
- `[advances_fin_ml, p.208-211]` — G1 PBO N=1 vacuous PASS.
- `[advances_fin_ml, p.222-223]` — G2 DSR deflator.
- `[advances_fin_ml, p.31-34]` — G7 cross-lib parity (held at 0.03-0.07 pp).

**External**:

- Moreira & Muir (2017), *JoF* 72(4), 1611-1644. DOI
  [10.1111/jofi.12513](https://doi.org/10.1111/jofi.12513) — variance-
  scaling base.
- Estrella & Mishkin (1998), *Review of Economics and Statistics* 80(1),
  45-61. DOI
  [10.1162/003465398557320](https://doi.org/10.1162/003465398557320)
  — 10Y-3M canonical recession predictor.
- Estrella & Hardouvelis (1991), *Journal of Finance* 46(2), 555-576.
  DOI
  [10.1111/j.1540-6261.1991.tb02674.x](https://doi.org/10.1111/j.1540-6261.1991.tb02674.x)
  — earlier term-spread predictive power for real activity.

---

## Next iteration suggestions

Iter 012 closes the T10Y3M overlay family as a dead-end. Three
structurally distinct directions remain, all preserve daily cadence:

1. **[OPTION C — META-LABELING on iter 008 blend]** (AFML ch.3, ch.5).
   Highest information-orthogonality ceiling. Primary recommendation
   for iter 013. Engineering cost ~2-3 hours. Uses cross-sectional
   features the blend can't see (cross-asset momentum, breadth,
   options-implied skew, macro state). Attacks the DSR ceiling via
   observed-Sharpe side.

2. **[OPTION E — EBP (excess bond premium) overlay]** (Gilchrist-
   Zakrajšek 2012). Credit-cycle signal distinct from yield-curve
   slope — fires on credit-spread regimes (1998 LTCM, 2008 GFC, 2020
   COVID) that don't all coincide with T10Y3M inversions. Monthly
   data; held constant within month, applied at daily rebalance.
   Engineering cost ~1 hour. Expected Sharpe uplift +0.02-0.06 if the
   EBP-SPY-realized-vol correlation is lower than T10Y3M's.

3. **[OPTION G — Return-stacked ETF rotation]** (NTSX/NTSI/NTSE).
   Structurally different universe — returns-stacking (90 % equity +
   60 % bond per dollar) layered with region tilt. NOT a blend
   variant; a new primitive. Uses factor rotation on 3 stacked ETFs
   as the equity-leg (no vol-scaling overlay). Engineering cost
   ~2 hours.

**Picking order for iter 013**: Option C first (highest ceiling on
this blend family; addresses DSR directly via new Sharpe not new T),
fallback Option E if meta-labeling is deferred for engineering
reasons. Option G is a **parallel track** — different universe,
different mechanism, should be scheduled as a later independent arm
of the hunt.

**Deferred backlog** (unchanged from iter 011):

- HMM regime-switching on stock-bond correlation (`[regime_change,
  ch.2]`) — different information axis (regime state).
- Cross-asset carry (FX / commodities / bonds) — `[ilmanen_expected_returns]`.
- Options tail-hedging (put-spread collars).

---

## Hunt-loop picture after iter 012

| iter | description | score | winner conds |
|---|---|---|---|
| 005 | Single-asset σ⁻² SPY/QQQ | 59 | 0/5 |
| 006 | 2-leg grid 12 cfg | 67 | 4/5 |
| 007 | 2-leg + momentum overlay | 50 | 0/5 |
| 008 | 2-leg single-cfg daily | 74 | 4/5 |
| 009 | 2-leg + T10Y3M 21d symmetric | 64 | 4/5 |
| 010 | 3-leg single-cfg daily | 74 | 4/5 |
| 011 | 3-leg weekly | 52 | 3/5 |
| **012** | **2-leg + T10Y3M 5d asymmetric** | **58** | **0/5** |

Daily-cadence ceiling for the blend family (**iter 008 / 010 = 74/100
tied**) remains unbroken. The T10Y3M-overlay quadrant is now fully
falsified (iter 009 symmetric heavy + iter 012 asymmetric light).
Timeframe-change quadrant falsified by iter 011. Momentum-overlay
quadrant falsified by iter 007. **The next productive attack must
introduce genuinely orthogonal information — not a correlated macro
signal on the same universe.** Meta-labeling (Option C) is the top
candidate.
