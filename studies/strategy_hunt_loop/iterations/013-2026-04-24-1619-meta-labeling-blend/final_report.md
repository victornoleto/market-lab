# Iteration 013 — Final Report

**Date:** 2026-04-24 16:19
**Hypothesis:** Meta-labeling classifier (AFML ch.3, p.50-56) — a
scikit-learn `LogisticRegression(C=1.0, penalty='l2')` trained on two
features orthogonal to the blend's realized-vol inputs (rolling 60-day
SPY-TLT correlation + VIX z-score over 252 bars) — decides bar-by-bar
whether to take iter 008's pre-committed vol-managed SPY+TLT blend or
go flat. Walk-forward retraining every 252 bars on a rolling 1000-bar
window, decision threshold p > 0.5. Single pre-committed combined cfg
`vt15_L21_cap20 × meta_lr_rho60_vixz252_w1000_r252`.
**Cumulative n_trials after iter 013:** 4255.

---

## Verdict

🥈 **PROMISING** (score **64/100**, `winner_conditions_met=False`,
**1/5** winner conditions met — regression from iter 008's 4/5).

**Kill criteria triggered** (pre-committed):

- ✅ **Kill #3 (score < 70)** — 64/100, 6 points shy of cutoff,
  10 points below iter 008/010 co-high.
- ❌ Kill #1 (regression > 0.02 on BOTH real slots) — not triggered
  (spy Δ = −0.010, ndx Δ = −0.014 — both under 0.02 threshold).
- ❌ Kill #2 (CAGR < 0.75 × bench) — not triggered (3/3 floor pass).
- ❌ Kill #4 (degenerate classifier) — not triggered (p_act std
  0.19-0.21 on all datasets, well above 0.05 floor).
- ❌ Kill #5 (cross-lib > 3 pp) — not triggered (max 0.45 pp).

**Core structural finding**: **Meta-labeling with ρ_60(SPY,TLT) +
VIX z-score features on a vol-managed SPY+TLT blend is REDUNDANT with
variance-scaling** — the meta-gate-off bars overlap 100% with the
bottom-20% blend-scale bars on educational + spy_real (62.5% on ndx).
This is the same failure diagnostic as iter 009/012's T10Y3M overlay
quadrant: the features the meta-model learned are cointegrated with
realized portfolio vol at the business-cycle timescale, so the
classifier's "go flat" decisions fire concurrently with the blend's
own de-lever — no orthogonal information added, only a small CAGR drag
from extra turnover.

**The classifier is NOT degenerate** (p_act std 0.19-0.21 shows it
IS learning patterns), but the patterns it learned are redundant with
what the blend already knows. Adding a decision stage with correlated
information forfeits residual positive drift without buying any
regime protection.

Score path: iter 008 = 74 → iter 010 = 74 (co-high, 3-leg tie) →
iter 011 = 52 (weekly) → iter 009 = 64 (T10Y3M 21d symmetric) →
iter 012 = 58 (T10Y3M 5d asymmetric) → iter 013 = **64**
(meta-labeling LR with 2 vol-proxy features).

---

## Headline metrics

Measured on the full dataset windows (daily returns, matching iter 008
convention). Custom educational benchmark (SPY b&h on TLT-aligned
window) + frozen spy_real / ndx_real benchmarks per
`WINNER_AND_RANKING.md`.

| dataset | Sharpe | Δ vs bench | Δ vs iter 008 | CAGR | MDD | gates | DSR p |
|---|---|---|---|---|---|---|---|
| educational | **0.853** | +0.191 vs 0.662 | **−0.012** | 12.54 % | 40.05 % | 6/7 | 0.311 |
| spy_real    | **0.990** | +0.090 vs 0.900 | **−0.010** | 15.23 % | 38.65 % | 6/7 | 0.347 |
| ndx_real    | **1.007** | +0.052 vs 0.955 | **−0.014** | 17.16 % | 37.21 % | 6/7 | 0.351 |

**Sharpe edge** (benchmark + 0.10 gate):

- edu 0.853 vs 0.78 → **PASS** (Δ vs gate +0.073)
- spy 0.990 vs 1.00 → **FAIL** (Δ vs gate −0.010)
- ndx 1.007 vs 1.055 → **FAIL** (Δ vs gate −0.048)

Only 1/3 passes. Iter 008 had 2/3. Meta-labeling pulled spy_real
below 1.00 on the edge gate by the exact Δ (−0.010) the meta-gate
cost.

**CAGR floor** (0.8 × bench): 3/3 pass. **MDD ceiling** (bench + 5pp):
3/3 pass (max gap 0.38 pp on spy).

---

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 10 | 25 | only edu clears +0.10 gate |
| 2 Gates | 19 | 25 | edu 6/7 + spy 6/7 + ndx 6/7 + 4 cross-ds bonus |
| 3 DSR | 0 | 15 | worst p = 0.351 (> 0.20 floor) |
| 4 CAGR floor | 15 | 15 | 3/3 datasets pass 0.8 × bench |
| 5 MDD ceiling | 15 | 15 | 3/3 datasets pass bench + 5 pp |
| 6 Robustness | 5 | 5 | 9/9 sub-windows positive Sharpe |
| **total** | **64** | **100+5** | **🥈 PROMISING** |

---

## Configuration tested

Exactly one pre-committed cfg `vt15_L21_cap20 × meta_lr_rho60_vixz252_w1000_r252`:

**Primary blend (iter 008 reused unchanged):**
- `target_vol = 0.15`, `lookback = 21`, `max_leverage = 2.0`

**Secondary classifier (iter 013 ex-ante):**
- Model: `sklearn.linear_model.LogisticRegression(C=1.0, penalty="l2", solver="lbfgs", max_iter=1000, random_state=42)`
- Features: `ρ_60(SPY, TLT)` (rolling 60d correlation, shift-1) + `vix_z_252` (rolling 252d z-score, shift-1)
- Label: `1` if `net_blend[t] > 0` else `0`
- Train window: 1000 bars rolling
- Retrain cadence: 252 bars (annual)
- Warmup: 1260 bars
- Decision threshold: `p > 0.5`

---

## Meta-classifier diagnostics

| dataset | gate-fire rate | p_act mean ± std | overlap bottom-20 scale | label base rate | turnover/yr |
|---|---|---|---|---|---|
| educational | 10.1 % | 0.635 ± 0.192 | **100.0 %** | 54.7 % | 26.8 |
| spy_real    | 6.3 %  | 0.678 ± 0.213 | **100.0 %** | 55.2 % | 25.7 |
| ndx_real    | 3.2 %  | 0.686 ± 0.213 | 62.5 %      | 55.2 % | 25.1 |

The overlap diagnostic is the same pattern observed on iter 009 and
iter 012. `ρ_60` and `VIX z-score` are business-cycle-scale regime
proxies; at those scales they are cointegrated with realized equity
vol, and the meta-model effectively learns the same de-lever rule
that variance-scaling already enforces. On ndx_real the overlap drops
to 62.5 % because QQQ's tech-specific vol shocks lead aggregate
equity vol, producing some orthogonality — but even there the gate
fires too sparsely (3.2 %) to add material uplift.

`p_act` mean 0.635-0.686 with std 0.19-0.21 confirms the classifier
is NOT collapsed to constant (Kill #4 clean). The learned decision
boundary is non-trivial; it's just pointing at the same information
variance-scaling already uses.

---

## What worked / what didn't

**Worked**: the pipeline (walk-forward retraining, no-look-ahead
lagging, numpy parity, baseline pytest preservation) is mechanically
clean. All 5 new TDD specs pass (feature-lag, future-independence,
numpy-reference CAGR parity). G7 cross-lib delta stays ≤ 0.45 pp
across all 3 datasets — engine numerics are correct. Robustness is
strong: 9/9 sub-window Sharpes positive across 3 datasets (best
robustness bonus in hunt-loop history).

**Didn't work**: the feature set. `ρ_60` changes slowly (60-day
window) and `vix_z_252` normalises VIX against a 1-year baseline —
both are regime-level indicators that move on the same business-cycle
timescale the blend's variance-scaling already reacts to. The
meta-classifier effectively re-learned "when portfolio vol is high,
go flat" — but the blend was already scaling positions down in
exactly those bars. Net effect: concentrated additional drag on bars
where the blend was already conservative (−0.01 Sharpe, −0.008 CAGR).

The 100 % overlap on edu + spy is the definitive diagnostic. It
matches iter 009's 100 % overlap at 21-day EMA smoothing and iter
012's 100 % overlap at 5-day EMA asymmetric. The common failure mode
is: **any regime-level signal on a vol-managed stock-bond blend
cointegrates with realized vol at the business-cycle scale**, whether
that signal is yield-curve slope, correlation, VIX level, or a
classifier trained on them.

The fix is not more regime-level features or a fancier classifier
(random forest, GBM). It's **genuinely different information**:
cross-sectional (breadth, factor spreads), credit-cycle (high-yield
spread distinct from rates), options-implied skew (VIX term
structure or put-call ratio), or cross-asset carry (FX, commodity)
— none of which cointegrate with SPY/TLT realized vol at
business-cycle timescales.

---

## Main lesson (for future iterations)

**Meta-labeling on iter 008's vol-managed SPY+TLT blend does NOT
generate orthogonal signal from the two most obvious "regime"
features (correlation + VIX z-score).** Both features collapse into
the same variance-scaling dimension the blend already exploits,
producing 100 % gate-fire/bottom-20%-scale overlap on SPY-based
datasets — the canonical redundancy diagnostic now seen across iter
009, 012, and 013.

This rules out the cheapest meta-labeling approach. It does NOT rule
out meta-labeling as a mechanism. A future iteration with
**demonstrably non-vol-cointegrated features** — for example,
high-yield credit spread (independent GFC / LTCM / COVID fire-episode
pattern vs rates), VIX term-structure slope (options risk premium
orthogonal to vol level), or cross-sectional factor momentum (a
return-based signal on a heterogeneous universe) — may still break
through. But it requires empirical pre-validation of
non-cointegration before committing DSR budget.

---

## Structural dead-ends discovered

Add to `DEAD_ENDS.md`:

- **Meta-labeling classifier (logistic regression or similar) with
  regime-level features (ρ_stockbond, VIX z-score, or any
  slow-moving cross-asset regime proxy) on a vol-managed 2-leg
  SPY/QQQ+TLT blend** — features are cointegrated with realized
  portfolio vol at the business-cycle scale; classifier learns a
  redundant de-lever rule that fires 100 % concurrently with the
  blend's own bottom-20% scale bars on SPY-based datasets.

- **Any derivative signal of SPY-TLT correlation** as a
  gate/modifier on a vol-managed stock-bond blend — the correlation
  regime is observable in variance-scaling's own output (via the
  covariance term in σ²_port), so adding it as a separate feature
  is double-counting, not orthogonality.

- **VIX level or its rolling z-score** as a standalone feature for
  a meta-model on a vol-managed blend — VIX is options-implied
  forward vol; on a 21-60-day scale it tracks realized vol closely
  enough that a classifier cannot separate them given ~17 years of
  training data.

---

## Citations used

**Primary**:
- `[advances_fin_ml, ch.3, p.50-56]` — meta-labeling architecture
  (López de Prado 2018).

**Supporting**:
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag rule, extended to
  feature lagging.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- `[advances_fin_ml, ch.7, p.103-112]` — walk-forward CV for
  financial ML.
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline
  (G7).
- `[regime_change, ch.2, p.5-6]` — regime-change principle.
- `[systematic_trading, ch.12, p.190-192]` — VIX as sizing
  covariate.
- `[risk_parity, p.10-11, ch.1]` — inverse-variance base blend.
- Moreira & Muir (2017), *JoF* 72(4), 1611-1644. DOI 10.1111/jofi.12513.
- López de Prado (2018) *Advances in Financial Machine Learning*,
  Wiley, ISBN 978-1119482086 — chapter 3 defines meta-labeling.

---

## Next iteration suggestions

Iter 013's failure is informative: the redundancy diagnostic now
covers THREE distinct "regime overlay / meta-model" approaches
(T10Y3M binary, T10Y3M asymmetric, LR-classifier on ρ + VIX).
**The vol-managed SPY+TLT blend at 74/100 is not going to be unlocked
by more vol-proxy signals.** The three viable paths forward:

1. **[OPTION E — EBP credit-spread overlay]** — Gilchrist-Zakrajšek
   (2012) excess bond premium. Credit-cycle fire-episodes (LTCM 1998,
   GFC 2008, COVID 2020) are partially independent of rates-term-
   structure — worth a pre-validation pass to measure
   EBP-vs-σ²_port correlation before spending DSR budget. If EBP's
   cointegration with realized equity vol is materially lower than
   T10Y3M's, the overlay is worth testing.

2. **[OPTION G — return-stacked ETF rotation]** — NTSX (90% US
   equity + 60% UST futures), NTSI (90% developed equity + 60% UST),
   NTSE (90% EM equity + 60% UST). Built-in leverage primitive,
   structurally distinct from iter 008's mechanism. Data start
   2018-2021 → limited history; may require synthetic proxies
   (90/60 combos of SPY/EFA/EEM + IEF) to get 17+ year backtests.

3. **[OPTION H — meta-labeling with ORTHOGONAL features]** —
   revisit meta-labeling but with features that have been
   **empirically validated as non-cointegrated with σ²_port**.
   Candidates to test (before spending DSR): high-yield spread
   (HYG/LQD ratio), VIX term-structure slope (VIX3M/VIX ratio),
   cross-sectional breadth (fraction of S&P components above
   200d MA), FX carry index (DB-G10-Carry or equivalent). Require
   a pre-iter screening step that measures each feature's 60-day
   rolling correlation with `σ²_port(blend)`; only proceed with
   those where |ρ| < 0.30 on ≥ 80% of bars.
