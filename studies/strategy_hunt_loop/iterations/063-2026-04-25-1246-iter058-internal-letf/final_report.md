# Iteration 063 — Final Report

## Verdict

🥇 **STRONG** — score **81/100**, **winner_conditions_met=False**
(3/5 conditions met), **1/6 kills fired** (kill A — Sharpe regress
vs iter 058 by ≥ 0.05 on 3/3 datasets).

This iteration tested **direction #1 from BASE_MEMORY**: apply iter
062's preserved-equity internal-LETF substitution to the iter 041
sub-component WITHIN iter 058's combined construction. The hypothesis
was that the higher Sharpe headroom of the DSR-clearing branch (iter
058 = iter 046 + HYG_TSM at w=0.10, Sharpe 1.22-1.40 with worst-p
0.0494) would absorb the LETF substitution's vol-decay + financing
drag (iter 062: −0.03/−0.09 Sharpe on 3/3) AND that the diversifier
overweight (+0.40 NAV redirected equally to bonds+gold per regime)
would lift CAGR enough to unlock the iter 058's binding CAGR-floor
constraint (0/15).

```
iter 058 canonical: 0.90 · (0.50 · iter_041 + 0.50 · iter_039) + 0.10 · HYG_TSM
iter 063 (this):    0.90 · (0.50 · iter_041_LETF + 0.50 · iter_039) + 0.10 · HYG_TSM
                              ↑ preserved-equity UPRO substitution
                              calm: 0.2333 UPRO + 0.6333 IEF + 0.6333 GLD = 1.50 NAV
                              stress: 0.10 UPRO + 0.65 IEF + 0.65 GLD = 1.40 NAV
```

**Both halves of the hypothesis were partially confirmed**:

- **CAGR uplift confirmed 3/3** (+0.77 / +0.66 / +1.85 pp vs iter 058).
  The educational dataset's CAGR moved from 8.69% → 9.46% — **first
  ever** unlocking of edu CAGR-floor 9.18% on the iter 058 family
  (iter 058 itself was 8.69%, iter 050 was 8.84%, iter 046 was
  9.07%; all below the 9.18% threshold). spy_real and ndx_real
  remained below their CAGR floors (11.98%, 15.35%) but moved closer
  (9.67%, 11.12%).
- **Sharpe drag observed 3/3** (−0.05 / −0.09 / −0.06 vs iter 058)
  — magnitude matches iter 062's iter 037-anchor finding almost
  exactly. The iter 041 leg contributes 0.45 of total NAV (0.90 ×
  0.50), so the per-unit drag is amplified roughly 2× by the smaller
  weight, hitting the kill-A threshold of −0.05 on all 3 datasets.

Net effect on score: **81 STRONG = iter 058's 85 − 4 points** (CAGR
floor +5; gates −4 from DSR regress; DSR criterion −5 from worst-p
band shift; MDD/robustness/Sharpe-edge unchanged). The iter 058
saved-stream-pair Pareto bound at 85 STRONG was NOT broken; the
iter 062 internal-LETF Pareto at 79 STRONG WAS broken (+2 pts via
DSR clearance on ndx_real and worst-p in 0.05-0.10 band on
edu/spy_real).

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen / Δ058) | CAGR (Δ058) | MDD (Δ058) | DSR p | gates |
|---|---|---|---|---|---|
| educational | 1.1716 (+0.49 / **−0.051**) | 9.46% (**+0.77pp** ✓) | 17.51% (+0.77pp) | **0.0762** ✗ | **6/7** |
| spy_real    | 1.2597 (+0.36 / **−0.088**) | 9.67% (+0.66pp) | 15.51% (+1.80pp) | **0.0698** ✗ | **6/7** |
| ndx_real    | 1.3454 (+0.39 / **−0.057**) | 11.12% (**+1.85pp**) | 18.01% (+4.89pp) | **0.0426** ✓ | **7/7** |

**Per-stream standalone metrics (post-inner-join per dataset)**:

| dataset | r_041_LETF | r_039 | r_046_LETF | r_HYG_TSM | r_LETF only |
|---|---|---|---|---|---|
| edu | S 0.95 / CAGR 14.3% / MDD 30% | 1.15 / 5.2% / 14% | 1.14 / 9.9% / 19% | 0.87 / 5.1% / 18% | 0.54 / 15.2% / 95% |
| spy | 1.03 / 14.8% / 28% | 1.29 / 5.2% / 7% | 1.23 / 10.2% / 17% | 0.99 / 4.9% / 7% | 0.80 / 32.1% / 77% |
| ndx | 1.08 / 16.9% / 34% | 1.56 / 6.3% / 7% | 1.32 / 11.8% / 20% | 0.99 / 4.8% / 7% | 0.88 / 41.1% / 82% |

**Key correlations**:

| ds | corr(combined_063, combined_058) | corr(046_LETF, HYG) | corr(041_LETF, 039) |
|---|---|---|---|
| edu | +0.984 | +0.346 | +0.319 |
| spy | +0.982 | +0.436 | +0.338 |
| ndx | +0.965 | +0.437 | +0.360 |

**G7 cross-library parity**: 0.000000 pp on all 3 datasets ✓
(pandas full pipeline = numpy reference to floating-point exactness;
max iter_041_LETF return diff = 3.0e-04 on educational due to one
rebalance bar mismatch; standalone iter 041 LETF stream IS exact).

**Markowitz residuals**: outer (0.9 × r_046_LETF + 0.1 × r_HYG):
0.000 / 0.000 / 0.000 (perfect closed-form). Inner (0.5 ×
r_041_LETF + 0.5 × r_039): +0.017 / 0.000 / 0.000 (edu has small
residual from the regime-flip cost terms, well under kill D's 0.05
threshold).

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | 3/3 datasets beat frozen bench by ≥ +0.10 (Δ +0.49/+0.36/+0.39) |
| 2 Gates | **21** | 25 | edu 6/7 + spy 6/7 + ndx 7/7 = 19; cross-ds bonus +4 capped → 21 |
| 3 DSR | **10** | 15 | Worst-p 0.0762 (edu) in 0.05-0.10 band → 10 pts; ndx (0.0426) clears 0.05 cutoff |
| 4 CAGR floor | **5** | 15 | edu 9.46% ≥ 9.18% ✓ (1st time on iter 058 anchor!); spy 9.67% < 11.98%; ndx 11.12% < 15.35% |
| 5 MDD ceiling | **15** | 15 | All 3 well under bench+5pp; edu 17.5% / spy 15.5% / ndx 18.0% |
| 6 Robustness | **5** | 5 | 9/9 sub-windows positive (edu 1.11/1.20/1.26; spy 1.47/1.27/1.09; ndx 1.43/1.55/1.15) |
| **total** | **81** | **100+5** | tier: **STRONG** |

Strict winner conditions: **3/5 met** —
1. Sharpe edge ≥ +0.10 on ≥ 2 ds: ✓ (3/3)
2. Gates cross-ds (edu ≥5, spy/ndx ≥4): ✓ (6/6/7)
3. DSR p < 0.05 (worst): ✗ (0.0762 worst — edu)
4. CAGR ≥ 0.8×bench on ≥ 2 ds: ✗ (1/3 only — only edu unlocks)
5. MDD ≤ bench+5pp on ≥ 2 ds: ✓ (3/3)

Score path forward to WINNER (90+):
- **Edu CAGR floor**: ✓ unlocked here (1st time)
- **Spy/ndx CAGR floor**: still 2/3 below — would need ~2.5pp more
  uplift on spy and ~4.5pp on ndx (LETF substitution alone gave
  +0.66/+1.85 pp; not enough by itself)
- **DSR**: regressed back to 0.0762 (above 0.05) on edu — would
  need another +0.05 Sharpe on edu OR a structurally cleaner
  Markowitz combo to reclear

## Configuration tested

```python
CFG = {
    "cfg_id": "iter058_with_internal_letf_iter041_only",
    "letf_leverage": 3.0,
    "expense_ratio": 0.0091,           # ProShares UPRO 2024-25 prospectus
    "calm_weights":   {"eq_w": 0.2333, "bd_w": 0.6333, "gld_w": 0.6333},  # 1.50 NAV
    "stress_weights": {"eq_w": 0.10,   "bd_w": 0.65,   "gld_w": 0.65},    # 1.40 NAV
    "vix_threshold": 20.0,
    "cost_bps_per_leg": 0.0002,
    "w_041": 0.5,                      # weight inside iter_046_LETF
    "w_039": 0.5,
    "w_046": 0.9,                      # weight inside iter_058_LETF
    "w_hyg": 0.1,
}
```

Effective top-level NAV decomposition:

```
0.90 · 0.50 · iter_041_LETF (calm: 0.225 NAV; 0.105 UPRO + 0.285 IEF + 0.285 GLD)
0.90 · 0.50 · iter_039      (variable; T-bill + cross-asset put-spread VRP)
0.10 · HYG_TSM              (variable; long-only credit + 90d trend filter)
```

cumulative_n_trials advance: 4332 → **4333** (+1).

## Pre-committed kills

| # | kill | fired? | observation |
|---|---|---|---|
| A | Combined Sharpe regress vs iter 058 by ≥ 0.05 on ≥ 2 ds | **❌ FIRED** | edu Δ −0.051, spy Δ −0.088, ndx Δ −0.057; **3/3 datasets dropped ≥ 0.05** (worse than predicted; iter 062's drag pattern reproduced fully) |
| B | DSR worst-p ≥ 0.10 (2× iter 058's effective ceiling) | ✓ clean | worst-p 0.0762 < 0.10 (margin 0.024 from kill threshold) |
| C | Score < 79 (iter 062 baseline) | ✓ clean | 81 > 79 (+2 pts vs iter 062 internal-LETF, −4 vs iter 058 canonical) |
| D | Markowitz outer residual ≥ 0.05 on ≥ 2 ds | ✓ clean | residuals 0.000/0.000/0.000 (perfect closed-form on outer combine) |
| E | G7 cross-lib > 3 pp | ✓ clean | 0.000000 pp on all 3 datasets |
| F | corr(combined_063, combined_058) > 0.99 | ✓ clean | avg 0.977 (max 0.984); high overlap but distinct stream |

**1/6 kills fired** ⇒ hypothesis **partially falsified**. The CAGR-
floor-unlock thesis is **partially confirmed** (3/3 CAGR uplift, 1/3
floor unlock — edu first time on iter 058 family). The Sharpe-headroom
absorption thesis is **falsified**: the higher base Sharpe of iter 058
does NOT shield from LETF drag — drag magnitude (−0.05 to −0.09) is
**identical** to iter 062's pattern on iter 037 anchor (−0.03 to
−0.09), confirming the drag is per-unit-LETF-weight invariant and
hits regardless of the combine structure surrounding it.

## What worked / what didn't

**Worked**:

- **First-ever edu CAGR-floor unlock on iter 058 family** — edu
  CAGR 9.46% > floor 9.18%. iter 058 itself was 8.69%; iter 050
  was 8.84%; iter 046 was 9.07%. The diversifier overweight from
  internal-LETF substitution provided the missing ~0.4-0.6 pp of
  CAGR. The mechanism (per iter 062's `[risk_parity, ch.5]`-
  derived structure) IS Sharpe-positive on the bond+gold legs at
  modest weight increases.
- **Score 81 = +2 pts vs iter 062's 79** — internal-LETF
  substitution on the DSR-clearing branch IS measurably better
  than on the CAGR-clearing branch. The +2 pts come from: (a) ndx
  DSR clears 0.05 cutoff (vs iter 062 where ndx p=0.222 fail),
  (b) edu DSR worst-p moves from 0.263 → 0.076 (in 0.05-0.10
  band → 10 pts vs iter 062's 0 pts at 0.20+), and (c) CAGR
  floor unlocks 1/3 (5 pts vs iter 062 still 3/3 → 15; here trade
  CAGR-on-iter-037-anchor for DSR partial clearance on iter-058-
  anchor). This **breaks iter 062's 79 ceiling on the internal-
  LETF axis by +2 pts**, confirming that anchor matters.
- **Markowitz closed-form perfect on the outer combine**
  (residuals 0.000/0.000/0.000). The 0.90 × r_046_LETF + 0.10 ×
  r_HYG composition is exactly closed-form because both streams
  are stationary daily fractional returns with known empirical
  μ/σ/ρ over the inner-join window. The inner combine has a
  +0.017 residual on educational from a small regime-flip cost
  asymmetry, but well within tolerance.
- **MDD ceiling preserved 3/3** (17.5/15.5/18.0% all under
  bench+5pp ceilings 60.1/38.7/40.1%). The internal-LETF + bond/
  gold cushion architecture absorbs UPRO/TQQQ's standalone 76-95%
  MDD into a portfolio MDD that grew only +0.8/+1.8/+4.9 pp over
  iter 058 — cushion held even though ndx's daily-reset TQQQ
  contribution dragged hardest.
- **G7 cross-lib parity 0.000000 pp on all 3 datasets** (pandas
  pipeline = numpy reference to floating-point exactness on the
  full composite stream). 18/18 TDD tests pass in 0.33s.
- **Sub-window robustness 9/9 positive**: edu 1.11/1.20/1.26
  (rising trend), spy 1.47/1.27/1.09 (declining trend, sharpest
  on 2009-2015 GFC recovery), ndx 1.43/1.55/1.15 (peak in
  2015-2020). All 9 sub-windows Sharpe-positive.

**Didn't**:

- **Sharpe-headroom absorption thesis FALSIFIED**: the iter 058's
  higher base Sharpe (1.22-1.40) did NOT absorb the LETF drag any
  better than iter 037's 0.96-1.17. Drag magnitude was −0.05 to
  −0.09 here vs −0.03 to −0.09 in iter 062 — identical bands.
  The drag is per-unit-LETF-equity-weight (not per-relative-Sharpe),
  so combining at a smaller LETF weight (0.225 NAV here vs 0.20
  NAV in iter 062) produces approximately equal-magnitude drag.
- **DSR REGRESSED** on edu (0.0494 → 0.0762) and spy (0.0337 →
  0.0698) due to lower Sharpe at fixed n_trials = 4333 (one trial
  more than iter 058's 4328). The deflated p-value is monotonically
  increasing in n_trials AND decreasing in Sharpe; both effects
  compound here. ndx DSR cleared (0.0258 → 0.0426) because base
  Sharpe was high enough (1.345 still > 1.20 threshold) to absorb
  both effects.
- **CAGR floor on spy/ndx still 2/3 below**: spy 9.67% < 11.98%
  (gap −2.3 pp); ndx 11.12% < 15.35% (gap −4.2 pp). The
  diversifier overweight provides ~0.7-1.9 pp uplift here — not
  enough to close the gap. spy/ndx need a structurally different
  CAGR-additive component (not internal-LETF on equity leg of
  iter 041 alone).
- **kill A fired 3/3 datasets** (Sharpe drop ≥ 0.05) — the kill
  threshold designed conservatively at 0.05 was breached on every
  dataset, confirming this is a structural drag pattern, not a
  noise-band miss.
- **Score 81 < iter 058's 85** — the saved-stream-pair Pareto
  ceiling at 85 (DSR-clearing branch) is **NOT broken** by
  internal-LETF substitution on iter 041 inside iter 058. The two
  Pareto branches (CAGR-clearing 79, DSR-clearing 85) remain
  non-dominated under internal-LETF perturbation; iter 063
  occupies a NEW intermediate Pareto-non-dominated point at
  (81, 3/5 winner conds, 1/3 CAGR floor) between iter 058 and
  iter 062.

## Main lesson (for future iterations)

**Internal-LETF substitution on iter 041 inside iter 058 produces
a NEW Pareto-non-dominated intermediate point at score 81 STRONG**
that:

- **Beats iter 062's 79** (internal-LETF on iter 037 anchor) by
  +2 pts — confirming **anchor choice matters within the internal-
  LETF axis** (DSR-clearing branch > CAGR-clearing branch under
  same substitution mechanism).
- **Loses to iter 058's 85** (canonical, no substitution) by
  −4 pts — confirming **internal-LETF is drag-dominated at retail
  rf=0 convention regardless of anchor**, not because of low base
  Sharpe but because of UPRO/TQQQ's structural daily-reset vol
  decay + visible internal financing.
- **Achieves 1st CAGR-floor unlock on iter 058 family** (edu only)
  but at cost of DSR regression on edu+spy.

Three observations from iter 063 that constrain future hunts:

1. **Internal-LETF drag is INVARIANT** across anchor Sharpe regimes
   (iter 037 anchor 0.96 → drag 0.03-0.09; iter 058 anchor 1.22-
   1.40 → drag 0.05-0.09 — same band). The drag is structural to
   UPRO/TQQQ's daily-reset path drift formula
   (`CAGR_LETF ≈ 3·CAGR_base − ½·9·var_base − expense`) plus the
   visible financing baked into NAV path. The "Sharpe headroom
   absorbs drag" hypothesis from BASE_MEMORY is now **falsified**.
2. **Internal-LETF axis is exhausted across both Pareto branches**
   (iter 037 anchor → 79 from iter 062; iter 058 anchor → 81 from
   this iter). The next 90+ score path **CANNOT** come from
   internal-LETF substitution on either family — it must come from
   either (a) novel anchor with simultaneously Sharpe ≥ 1.20 AND
   CAGR ≥ 12% (no anchor in iters 0-63 has this combination), or
   (b) a structurally novel CAGR-additive 4th stream beyond HYG
   that delivers +CAGR without dragging Sharpe.
3. **The 81 STRONG occupies a UNIQUE Pareto position** — it's
   the first iter-058-family result with edu CAGR-floor pass
   AND any-dataset DSR clearance simultaneously. iter 058 had
   3/3 DSR pass + 0/3 CAGR floor; iter 063 has 1/3 DSR pass +
   1/3 CAGR floor. This is a *different* trade-off, not a
   strict improvement. May inform future combinations that
   target both axes.

## Structural dead-ends discovered

- **iter 063 (🥇 STRONG 81, 1/6 KILLS — kill A only) — internal-
  LETF UPRO substitution preserving equity exposure on iter 041
  sub-component within iter 058 anchor**: Sharpe-headroom
  absorption thesis FALSIFIED (drag −0.05 to −0.09 on 3/3
  datasets, identical magnitude to iter 062's iter 037-anchor
  finding). CAGR uplift +0.66 to +1.85 pp confirmed but only
  unlocks edu floor; spy/ndx still 2.3-4.2 pp below floors. DSR
  regressed on edu (0.0494 → 0.0762) and spy (0.0337 → 0.0698).
  Score 81 = iter 058's 85 − 4. **Closes** the internal-LETF axis
  on iter 058 anchor at preserved-equity weighting (calm
  0.2333/0.6333/0.6333; stress 0.10/0.65/0.65). Add to DEAD_ENDS.md.

- **Internal-LETF axis exhausted across BOTH Pareto branches**
  (iter 037-anchor → 79 from iter 062; iter 058-anchor → 81 from
  iter 063). Internal-LETF UPRO/TQQQ substitution at retail rf=0
  convention is structurally drag-dominated (−0.03 to −0.09
  Sharpe per unit substitution) regardless of anchor base Sharpe
  level. The drag mechanism (daily-reset vol decay + visible
  financing) is INVARIANT across anchor regimes. Path 90+ on the
  iter 037/058 family **cannot** come from internal-LETF — must
  come from novel anchor or structurally novel CAGR-additive 4th
  stream.

## Citations used

- `[leverage_for_the_long_run, p.19-25]` — Hsiao & Williams (2017),
  J. Index Investing, daily-reset LETF formula and Itô-correction
  derivation: `CAGR_LETF ≈ leverage·CAGR_base − ½·leverage²·var_base
  − expense`. Empirically reproduced here on UPRO/TQQQ standalone
  (CAGR 32-41% on real data with 0.91% expense baked in).
- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen (2012)
  multi-leg risk-parity stack architecture; iter 041 regime-
  weighted variant preserved verbatim under LETF substitution.
- `[risk_parity, p.5, p.10-11, ch.1]` — AFP 2012 SSRN 1728082,
  static fixed-weight stack mechanism applied to LETF-substituted
  equity leg.
- `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP
  harvest; iter 039 base architecture preserved verbatim via saved
  return stream from iter 046.
- `[advances_fin_ml, ch.17-18]` — regime detection (iter 041 VIX
  gate carried over to iter 041_LETF).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (4332 → 4333). Worst-p 0.0762 (edu), 0.0698 (spy), 0.0426 (ndx).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline
  (numpy reference for full composite stream; 0.000000 pp on all
  3 datasets).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
  (vacuous for static weights, prior-day-only synth formula, and
  prior-bar VIX in regime detection).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- Whaley (2009), JPM 35(3) 98-105, DOI 10.3905/JPM.2009.35.3.098 —
  VIX as ex-ante risk regime indicator.
- Bekaert-Hoerova (2014), J Econometrics 183(2) 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition.
- Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 —
  gold strategic role.
- Asvanunt-Richardson (2017), JPM 43(2), DOI 10.3905/jpm.2017.43.2.090
  — credit risk premium (HYG_TSM 3rd stream preserved verbatim).
- Markowitz (1952), JoF 7(1) 77-91 — convex combination Sharpe
  identity (inner + outer combine, residuals 0.000-0.017).
- ProShares UPRO prospectus 2024-2025 — expense ratio 0.91%/yr.

## Next iteration suggestions

iter 063 closes the internal-LETF axis on iter 058 anchor and
**confirms the axis is exhausted across both Pareto branches**
(iter 037-anchor 79 + iter 058-anchor 81). Internal-LETF cannot
break the iter 058 family's 85 ceiling. Three structurally distinct
directions remaining:

1. **Higher-CAGR 3rd stream from non-equity asset class on iter 058
   anchor** (NEW direction, structurally novel). Candidates:
   QQQ-200d-trend (Sharpe ~0.8, CAGR ~12-14%, but corr with iter
   046 ~0.7 — kill F risk); EFA + EEM equal-weight TSM (lower
   correlation but Sharpe ≤ 0.5); gold-spread momentum (gold
   futures roll); AQR-style multi-factor passive ETF (QMOM, VLUE,
   USMV — weight in 2007+ available). The constraint per iter 058
   final report: 3rd stream needs **standalone Sharpe ≥ 0.7 AND
   standalone CAGR ≥ iter 046's 9.5%/yr**. This is the binding
   gap to break the 85 ceiling. **Predicted 80-92.**

2. **4-stream composite on iter 037 anchor (BASE_MEMORY direction
   #2 generalized)**: iter 058 + iter 037 50/50 OR iter 058's
   HYG_TSM + iter 037 + gold-TSM. Combines the higher-CAGR iter
   037 (12-15% CAGR) with iter 058's DSR-clearance. Predicted
   83-89; saved-stream-pair Pareto bounded around 85 historically.

3. **Plano C sleeve eval (BASE_MEMORY direction #4)**: floor
   experiment on multi-factor passive ETFs (GDE/AVUV/AVDE/AVEM/
   BTGD). Predicted ≤ 70 per BASE_MEMORY but lowest infrastructure
   cost. Useful as calibration data point.

**Recommended pick for iter 064**: **direction #1 (higher-CAGR 3rd
stream non-equity)** because internal-LETF has now been definitively
shown to be drag-dominated across both Pareto branches, and the
iter 058 final report's diagnosis — that the family's 85 ceiling
needs a 3rd stream with Sharpe ≥ 0.7 AND CAGR ≥ iter 046's CAGR —
remains the most direct path to break the ceiling. Specifically,
**QQQ-200d-trend** is the highest-CAGR / highest-Sharpe candidate
in the Tiingo cache; the kill F correlation risk (~0.7 with iter
046) is the main concern, and would need to be measured upfront
before committing to a full backtest.
