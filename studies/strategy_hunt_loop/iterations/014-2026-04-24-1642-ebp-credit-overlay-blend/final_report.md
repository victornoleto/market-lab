# Iteration 014 — Final Report

**Date:** 2026-04-24 16:42
**Hypothesis:** Mandatory pre-validation gate + binary EBP
(Gilchrist-Zakrajšek 2012 Excess Bond Premium) credit-cycle haircut
overlay on iter 008's pre-committed vol-managed SPY+TLT blend
(`vt15_L21_cap20`). Haircut applied to equity leg only on `EBP_z_252 ≥ 1.0`.
Pre-validation screen (built-in **Kill #PV**) measures 60-day rolling
|ρ(EBP_z, σ²_port(blend))|; aborts iteration if fraction of bars
exceeding 0.30 > 20 % on ANY dataset.
**Cumulative n_trials after iter 014:** 4255 (unchanged — no backtest
trials committed).

---

## Verdict

❌ **FAIL** (pre-validation screen failure — `total_score=0`,
`winner_conditions_met=False`, 0/5 winner conditions met,
**Kill #PV triggered**).

**No backtest was executed. No DSR budget spent. No G1-G7 battery run.**

### Pre-validation results (60-day rolling correlation)

| dataset | exceed_frac (vs 20 %) | max \|ρ\| | mean \|ρ\| | n_valid_windows | screen |
|---|---|---|---|---|---|
| educational | **0.684** (3.4× cap) | 0.958 | 0.469 | 5656 | ❌ FAIL |
| spy_real    | **0.691** (3.4× cap) | 0.958 | 0.472 | 3915 | ❌ FAIL |
| ndx_real    | **0.706** (3.5× cap) | 0.942 | 0.482 | 3755 | ❌ FAIL |

EBP's 60-day rolling correlation with blend realised-variance is
empirically too tight to add orthogonal signal — mean magnitude ≈ 0.47,
peaking at ≈ 0.96 in stress windows. This is the same cointegration
pattern that killed iter 009 (T10Y3M 21d symmetric), iter 012 (T10Y3M
5d asymmetric), and iter 013 (LR meta with ρ_60 + VIX z-score).

---

## Core structural finding

**EBP (Gilchrist-Zakrajšek 2012 residual) is empirically cointegrated
with realised portfolio variance of the vol-managed SPY+TLT blend at
the 60-day business-cycle timescale on all three datasets.** The
decomposition that strips expected-default risk from corporate bond
spreads [GZ2012] leaves a credit-risk-premium residual that was
hypothesised to fire on credit-specific episodes (LTCM 1998, GFC 2008,
COVID 2020, 2022 rate-hike stress) partially independent of
broad-equity realised volatility. **This hypothesis is falsified on
this mechanism**: the fire-episodes of EBP_z ≥ 1.0 overwhelmingly
coincide with the blend's own de-lever windows (high σ²_port).

This is the **fourth consecutive macro-/cross-asset signal tested as
an overlay on iter 008's blend** to fail on the same business-cycle
cointegration diagnostic:

| iter | signal family | closure mechanism | score |
|---|---|---|---|
| 009 | T10Y3M, 21d EMA, symmetric haircut | 100 % bottom-20 overlap | 64/100 |
| 012 | T10Y3M, 5d EMA, asymmetric equity-only | 100 % bottom-20 overlap | 58/100 |
| 013 | LR meta-label w/ ρ_60 + VIX_z_252 | 100 % bottom-20 overlap | 64/100 |
| 014 | **EBP credit-cycle binary, asymmetric** | **pre-val |ρ|>0.3 on 68-71 % bars** | **0/100 (aborted)** |

The pre-validation gate changed iter 014's position in this sequence:
it detected the cointegration BEFORE a 3-trial DSR budget was spent,
saving `cumulative_n_trials` from 4255 → 4258 and preventing the
familiar 64/100 PROMISING verdict from re-appearing.

---

## Why the result is structural, not parametric

EBP was specifically chosen because GZ2012 decomposition REMOVES the
component of credit spreads that tracks expected defaults (equity-
linked). The residual is supposed to be "pure" credit-risk premium —
investor risk appetite driven by dealer balance sheets, insurance-
company demand, and bank capital cycles. Three pieces of evidence
establish that this residual still cointegrates with σ²_port at the
60-day scale:

1. **mean |ρ| ≈ 0.47 across all 3 datasets** — roughly 1.5× the
   threshold, with very low variance across datasets (0.469-0.482).
   The consistency suggests a common structural driver, not
   dataset-specific noise.

2. **|ρ| can reach 0.96** in stress windows — EBP-z and σ²_port are
   effectively the same signal during the most policy-relevant
   regimes (2008 Q3-Q4, 2020 Q1, 2022 Q4 late-hike).

3. **Educational's longer sample (2002-2026)** exhibits an almost
   identical signature (0.684 exceed, 0.469 mean |ρ|) to spy_real
   (0.691, 0.472) and ndx_real (0.706, 0.482). If the cointegration
   were a post-2008 monetary-policy-regime artifact, educational's
   2002-2007 pre-GFC sample would dilute it; it doesn't.

The Lo [adaptive_markets, p.131-132, ch.11] framing of "credit cycle
as a distinct adaptive axis" is correct at the multi-year regime
level (LTCM 1998 hedge-fund attrition was a clean credit event
`[adaptive_markets, p.244-246, ch.7]`); but at the 60-day window scale
that matters for a daily vol-managed blend's de-lever dynamics, the
credit cycle and equity-vol cycle are measurably co-moving.

---

## Secondary finding — pre-validation gate methodology is productive

The pre-validation gate itself is the iteration's positive
contribution. For future overlay iterations on iter 008's blend (or
its 3-leg iter 010 extension), the gate provides:

1. **Cheap early-abort** — 2-3 minutes of compute vs 15-30 minutes
   for a full 3-dataset backtest + 7-gate battery.
2. **No `cumulative_n_trials` inflation** on structurally doomed
   signals — preserves DSR budget for genuinely orthogonal candidates.
3. **Crisper structural categorisation** — "signal X has mean |ρ| =
   0.47 with σ²_port" is more actionable than "signal X scored 64/100
   with 100 % bottom-20 overlap".

The gate now supersedes the "run full iteration first, observe overlap
in post-hoc diagnostic" pattern used by iter 009/012/013. Any future
candidate feature for a meta-label or overlay on the vol-managed blend
should run the screen first.

---

## What worked / what didn't

**Worked**:

- Test-driven development: 9 new TDD specs for EBP alignment,
  z-score, gate, asymmetric haircut, numpy parity — all pass.
  Baseline 823 → 832, no regression.
- Pre-validation gate methodology — clean, fast, decisive.
- Diagnosis of saturation artifact on initial σ²_port proxy
  (`target_var / scale` saturates at blend cap); migrated to rolling
  realised-variance of blend net returns. Both proxies returned the
  same qualitative verdict (fail), but the second is cleaner.

**Didn't work**:

- The core hypothesis: EBP's decomposition to isolate credit-risk
  premium does NOT produce a 60-day-scale signal orthogonal to
  realised portfolio vol on a vol-managed SPY+TLT blend. The
  decomposition that mathematically strips expected-default variation
  still leaves a residual that swings WITH equity-vol regimes
  empirically.

---

## Main lesson (for future iterations)

**The vol-managed SPY+TLT blend's σ²_port(t) cointegrates at
business-cycle (60-252 day) scales with ALL observed macro /
cross-asset signals tested to date: yield-curve slope (iter 009/012),
SPY-TLT correlation (iter 013), VIX z-score (iter 013), and now
credit-risk-premium residual (iter 014).** This is not the fault of
any one decomposition or smoothing choice — it is a property of the
portfolio's response function: a vol-managed blend self-adjusts on
the same macro-risk gradient that drives all these signals.

Productive directions from this lesson:

1. **Mechanism change, not overlay change** — stop adding overlays to
   iter 008's blend. Next iteration should test either (a) a
   structurally different primitive (Option G — return-stacked ETF
   rotation), (b) a different universe (cross-sectional
   heterogeneity, e.g., single stocks), or (c) a different asset
   class altogether (FX carry, commodity momentum, options skew).

2. **Cross-sectional signals** — any "regime" signal on a 2-leg
   stock-bond portfolio is subject to the above cointegration. A
   signal derived from ranking *across* assets (breadth, dispersion,
   factor-momentum, factor-carry) has a different information
   structure and is a candidate for future meta-labeling on a
   cross-sectional primary.

3. **Keep the pre-validation gate** — for any future overlay/meta-
   label iteration on a vol-managed blend, run the 60-day
   |ρ(feature, σ²_port)| > 0.30 screen first. Budget threshold: <
   20 % of bars exceeding. Feature-sets failing the screen are
   rejected before full test.

---

## Structural dead-ends discovered

Add to `DEAD_ENDS.md`:

- **EBP (Gilchrist-Zakrajšek 2012 residual) binary haircut overlay on
  a vol-managed SPY+TLT blend** — pre-validation screen rejects:
  |ρ(EBP_z_252, σ²_port(blend))| > 0.30 on 68-71 % of 60-day rolling
  windows across all 3 datasets; mean |ρ| ≈ 0.47, max 0.96. The GZ2012
  decomposition's "pure credit-risk premium" residual is empirically
  co-moving with blend realised variance at business-cycle scale.

- **Any macro / cross-asset signal** used as a binary-haircut or
  meta-label overlay on the vol-managed SPY+TLT (or SPY+TLT+GLD)
  blend at 60-day observation scale — four independent attempts
  (iter 009, 012, 013, 014) now document structural cointegration
  with σ²_port. The overlay family is closed; mechanism change
  required. **Pre-validation gate is mandatory** for any future
  proposal in this family.

---

## Citations used

**Primary**:

- `[adaptive_markets, p.131-132, ch.11]` — Lo's countercyclical
  capital buffers / credit cycle as distinct adaptive axis.

**Supporting**:

- `[adaptive_markets, p.244-246, ch.7]` — LTCM 1998 fixed-income-arb
  attrition as canonical pure credit-event.
- `[risk_parity, p.23-24, ch.2]` — HY bonds co-move with equity at
  Sharpe level — motivates using EBP (residual), not raw HY spread.
- `[ml_for_algo_trading, ch.23, p.716]` — prioritise economically-
  motivated hypotheses over data-mining.
- `[advances_fin_ml, p.162-164]` — lag rule extended to macro data.
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7
  — not executed; pre-val abort precedes G7).
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials (not
  incremented — pre-val abort).
- `[systematic_trading, p.144, ch.9]` — tier-2 half-exposure haircut.

**Web**:

- Gilchrist, S. & Zakrajšek, E. (2012), "Credit Spreads and Business
  Cycle Fluctuations", *American Economic Review* 102(4), 1692-1720.
  DOI [10.1257/aer.102.4.1692](https://doi.org/10.1257/aer.102.4.1692).

- Federal Reserve Board EBP monthly series (updated 2016):
  <https://www.federalreserve.gov/econresdata/notes/feds-notes/2016/updating-the-recession-risk-and-the-excess-bond-premium-20161006.html>.

---

## Next iteration suggestions

Iter 014 closes the final remaining overlay on iter 008's blend that
was in the top priority queue. Three productive directions remain,
ordered by structural novelty:

1. **[OPTION G — return-stacked ETF rotation]** (primary
   recommendation for iter 015). NTSX/NTSI/NTSE (90 % equity + 60 %
   UST futures stacked). Structurally new primitive — built-in
   leverage via futures stacking, distinct from iter 008's explicit
   vol-scaling + risk-parity weighting. `[risk_parity, p.5]` +
   `[leverage_for_the_long_run, p.19-20]`. Data history: NTSX
   launched Aug 2018, NTSI Feb 2021, NTSE Feb 2021; synthetic proxies
   required for pre-2021 window (90 % SPY/EFA/EEM + 60 % IEF).
   Represents a true mechanism change, not an overlay.

2. **[CROSS-SECTIONAL FACTOR MOMENTUM]** — skip the 2-leg universe
   entirely. Universe: heterogeneous factor ETFs (MTUM, QUAL, VLUE,
   USMV, SIZE, SPMO — 6+ distinct Fama-French-style tilts). Signal:
   12-1 momentum on factor returns; portfolio: top-K long, bottom-K
   cash or short. `[ml_for_algo_trading, ch.4]` for 12-1 canonical,
   `[advances_fin_ml, ch.7]` for purged CV on cross-sectional
   features. Uses ranking (which needs heterogeneity — see iter 003
   dead-end), but factor ETFs ARE heterogeneous (unlike sector ETFs
   that were too market-factor-dominated).

3. **[OPTIONS SKEW / VIX TERM STRUCTURE SIGNAL ON PLAIN SPY]** —
   single-asset primary (not blend), daily SPY returns conditioned on
   VIX/VIX3M ratio crossing threshold. Structurally distinct because
   the primary is NOT vol-managed — no σ²_port cointegration axis.
   `[volatility_trading, ch.4-5]`. Uses the options-implied
   information axis iter 013 discussed as potentially orthogonal.

All three break the "overlay on iter 008's blend" pattern that has
now failed 4× consecutively with the same structural diagnostic.
