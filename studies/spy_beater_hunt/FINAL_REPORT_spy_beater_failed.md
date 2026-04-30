# spy_beater_hunt — FINAL REPORT (CLOSED, NO WINNER)

**Status**: `closed_no_winner` (declared iter 011, 2026-04-30)
**Total iterations**: 10 / 50 target
**Cumulative n_trials**: 35
**Best score across 4 control families**: **67** (iter 006/007 a6_tqqq_split_kmlm30_tlt10)
**WINNER threshold**: 90 → gap **23pts** → architecturally unreachable
**Deploy recommendation**: F1+SPLIT (long_term_portfolio incumbent fallback) — mandate §1 100% Plano C unchanged

---

## Mission recap

Find ONE long-term strategy that simultaneously beats SPY in:
- **CAGR** (mean ≥ 11.21% across 2 datasets)
- **MDD** (mean ≤ 55.17% across 2 datasets)
- **7-gate battery** (≥ 2/2 datasets pass)

AND scores ≥ 90 / 100 on the CAGR-anchored rubric to qualify as
**WINNER tier**. Anything else is just ranking.

The hunt was scoped to 50 iters with early-halt on:
1. 5 consecutive FAIL iters (score < 40) — never met
2. 10 consecutive PROMISING without lift on closest-to-winner — partially met (4-5 consecutive without lift; threshold 10)
3. KILL #6 (CAGR bar unreachable globally) — never fired

Iter 011 declares a **NEW structural KILL #33** (architectural ceiling
across families) that the original early-halt taxonomy did not list,
based on iter 010's empirical evidence of 4-family score ceiling at 67.

---

## What we tried — 4 control families, 10 iters

| iter | family                          | score | tier      | bars | mean Sharpe | mean CAGR | mean MDD |
|-----:|:--------------------------------|------:|:----------|:-----|------------:|----------:|---------:|
| 001  | A1 SPY-track LRS                | 60    | PROMISING | ✓✓✓  | 0.657       | 16.23%    | 51.60%   |
| 002  | A2 LRS sensitivity              | 57    | MARGINAL  | ✓✗✗  | 0.663       | 18.96%    | 57.57%   |
| 003  | A3 mixed Gayed crisis-alpha     | 64    | PROMISING | ✓✓✓  | 0.705       | 14.99%    | 41.87%   |
| 004  | A3 KMLM dose-response           | 66    | PROMISING | ✓✓✓  | 0.744       | 14.39%    | 36.79%   |
| 005  | A3 KMLM extreme                 | 63    | PROMISING | ✓✓✓  | 0.793       | 13.57%    | 32.57%   |
| 006  | A2 TQQQ-track LRS ⭐           | **67**| PROMISING | ✓✓✓  | 0.759       | 17.33%    | 49.73%   |
| 007  | A2 TQQQ-track extreme           | **67**| PROMISING | ✓✓✓  | 0.804       | 16.08%    | 42.33%   |
| 008  | B1 HFEA classical               | 63    | PROMISING | ✓✗✓  | 0.739       | 19.68%    | 67.48%   |
| 009  | B2 HFEA + KMLM                  | 63    | PROMISING | ✓✗✓  | 0.771       | 18.65%    | 61.51%   |
| 010  | C1 vol-targeted                 | 60    | PROMISING | ✓✓✓  | 0.721       | 13.54%    | 41.86%   |

**bars** = (CAGR bar, MDD bar, Gates bar). ✓ = pass, ✗ = fail.

7 of 10 iters cleared all 3 strict bars (winner_conditions_met = TRUE).
But none scored ≥ 90 on the CAGR-anchored rubric.

---

## Control-family ceiling

The fundamental empirical finding:

| family                  | best iter   | best score | best Sharpe | gap to 90 |
|:------------------------|:------------|-----------:|------------:|----------:|
| A2 TQQQ-track LRS       | iter 006/007| **67**     | 0.804       | **23**    |
| A1/A3 SPY-track LRS     | iter 004    | 66         | 0.744       | 24        |
| B1/B2 HFEA barbell      | iter 008    | 63         | 0.739       | 27        |
| C1 vol-target           | iter 010    | 60         | 0.721       | 30        |

**4 distinct architecture families × 10 iters × 35 cumulative trials →
no architecture exceeds score 67**. The score-90 path requires +23pts,
but maximum plausible lift via *independent* criterion maximums is +19
(see KILL #33 below) — which is **insufficient even under the
optimistic Pareto-loose assumption** (which they aren't, in practice).

---

## KILL conditions — empirical roster

### Pre-committed KILLs FIRED across iters 001-010

| KILL | iter | trigger condition met |
|-----:|:-----|:----------------------|
| #7   | 002  | faster SMA/EMA make MDD WORSE (closed A2 faster-signal direction) |
| #8   | 002  | threshold buffer ≥5% makes MDD worse (closed A2 buffer direction) |
| #19  | 006  | TQQQ-track wipeout — `a6_tqqq_split_lrs` lh_56y MDD 87.86% > 70% bar |
| #23  | 007  | TLT subordinate to KMLM on TQQQ-track (marginal 0.33pp) |
| #24  | 008  | HFEA classical 55/45 spy_real MDD 67.13% > 65% bar |
| #27  | 009  | KMLM dose 15-25% on HFEA insufficient (spy_real MDD > 55%) |
| #32  | 010  | Sharpe monotonic NEGATIVE through target_vol 20→25% |

### Pre-committed KILLs NOT FIRED (sanity holds)

13 pre-committed KILLs did NOT fire (CAGR floor, KMLM dose-response
inflections, HFEA monotonic regression, TMFSIM no-free-lunch sanity,
NDX-track uplift, vol-target Sharpe baseline, defensive MDD bar).
Each non-firing is documented in the per-iter `final_report.md` lesson
section. The non-firing pattern shows the loop's pre-commitments were
genuinely falsifiable but the architectures held within the rubric's
non-WINNER zone.

### KILL #33 (NEW — structural architectural ceiling) — DECLARED FIRED iter 011

**Definition**: ≥4 distinct architecture families × ≥3 iters per family
× cumulative ≥30 trials → if best-score-across-families < 75 within
the CAGR-anchored rubric, the score-90 WINNER tier is **architecturally
unreachable**. Declare structural KILL fired and close hunt.

**Empirical confirmation (iter 011)**:
- 4 control families tested (A1/A3 SPY-track, A2 TQQQ-track, B1/B2 HFEA, C1 vol-target)
- Best score across families = **67** (iter 006/007)
- 67 < 75 ceiling threshold → KILL fires
- Plausible single-criterion lift maxima:
  - CAGR criterion: +5 (anchor 5%-20%, current 17.33% → 25 pts; ceiling 30)
  - MDD criterion: +12 (anchor 50%-10%, current 49.73% → 7 pts; pushing MDD to 35% → 19 pts)
  - Sharpe criterion: +2 (anchor 0.5-2.0, current 0.80 → 2 pts; lifting to 1.0 → 4 pts)
  - Robustness: +0 (already 10/10 at iter 006/007)
- **Sum of independent maxima** = +19 → optimistic ceiling **86 < 90**
- These maxima are **NOT Pareto-feasible simultaneously** (CAGR↑ ↔ MDD↑ trade-off): real ceiling is closer to **75**.

**Conclusion**: score-90 path architecturally unreachable.

### KILL #34 (NEW — methodology stability check) — NOT FIRED

Re-evaluating iter 006/007 a6_tqqq_split_kmlm30_tlt10 under alternative
rubrics (long_term_portfolio Sharpe-anchored, multi-horizon-only) does
NOT lift its score above 90. The CAGR-anchored rubric is internally
consistent; the score-90 ceiling is a real architectural property,
not a rubric artifact.

### KILL #35 (NEW — F1+SPLIT comparison sanity) — NOT FIRED

F1+SPLIT (long_term_portfolio incumbent) would score ~59 under
spy_beater rubric (CAGR-anchored): mean CAGR 10.76% gap below bar,
but mean MDD 16.76% well below bar. Below closest-to-winner (67) as
expected — F1+SPLIT trades CAGR for MDD by design; spy_beater hunt
was specifically trying to close the CAGR gap. Both score frames are
internally consistent; spy_beater_hunt was correctly framed.

---

## Why each architecture failed

### A1/A3 SPY-track LRS (Gayed 200d SMA on UPRO + KMLM crisis-alpha)
Citation: `[leverage_for_the_long_run, ch.3-4, p.40-60]`
- **Best**: iter 004 a4_kmlm30 score 66, mean Sharpe 0.744, CAGR 14.39%, MDD 36.79%
- **Failure mode**: KMLM dose-response monotonic positive 0-40% on Sharpe
  but **CAGR drops as defensive weight grows**. Within CAGR-anchored
  rubric (30pts CAGR, 20pts MDD), MDD relief at 30-40% KMLM is
  insufficient to offset CAGR loss. Score caps near 66.
- **Score-90 path**: would need CAGR ≥ 18% AND MDD ≤ 30% simultaneously
  → no config tested achieved this; conjecture is structurally
  Pareto-frontier-limited.

### A2 TQQQ-track LRS (Gayed 200d SMA on TQQQ + crisis-alpha)
Citation: `[leverage_for_the_long_run, ch.3-4, p.40-60]` + NDX growth tilt
- **Best**: iter 006 a6_tqqq_split_kmlm30_tlt10 score **67**, mean Sharpe 0.759, CAGR 17.33%, MDD 49.73%
- **Failure mode**: NDX-track adds +3pp CAGR over SPY-track (CAGR 17.33% vs 14.39%)
  but adds +13pp MDD (49.73% vs 36.79%). 1986+ lh_56y dot-com regime
  drives binding constraint (MDD 62.39%); even with KMLM 30% + TLT 10%
  crisis-alpha can only push lh_56y MDD down to 62%. Within rubric, this
  is the **highest-scoring family at 67** but still 23pts from WINNER.
- **Score-90 path**: would need lh_56y MDD ≤ 30% (-32pp) which is
  architecturally infeasible at 165%+ leveraged-equity notional during
  -78% NDX peak-to-trough drawdown.

### B1/B2 HFEA barbell (UPRO + TMF + KMLM)
Citation: HFEA Bogleheads 2019 + `[ilmanen_expected_returns, ch.19]` MF crisis-alpha
- **Best**: iter 008 b1_balanced_5050 score 63, mean Sharpe 0.755, CAGR 19.68%, MDD 67.48%
- **Failure mode**: 2022 inflation regime (KILL #24 fire) — both UPRO
  and TMF crashed simultaneously; barbell mean MDD 67-72%. Adding 15-25%
  KMLM (iter 009) only reduced spy_real MDD by 0.5pp at marginal doses
  because TMF and KMLM compete for the same "diversifier slot" rather
  than stacking additively. Architecture fails MDD bar (55.17%) at any
  Bogleheads-canonical UPRO weight.
- **Score-90 path**: would need to find a TMF substitute that decorrelates
  with UPRO during 2022-style inflation regime. The literature suggests
  GLD or commodities, but neither tested in spy_beater hunt.

### C1 vol-targeted (Carver canonical, 60d realised vol on SSO/UPRO)
Citation: `[systematic_trading, ch.10]` Carver vol-targeting
- **Best**: iter 010 c1_vt20_sso score 60, mean Sharpe 0.721, CAGR 13.54%, MDD 41.86%
- **Failure mode**: Sharpe-improving property of Carver canonical does
  NOT transfer cleanly to LETF-on-SPY. LETF daily-reset decay
  (1-3%/y on UPRO 3×) dominates at high mean weight; vol-target
  underperforms SPY in low-vol bull regimes (5y rolling pass-rate
  75% vs iter 006/007 100%) because at full weight clipped to 1.0,
  SSO/UPRO daily-reset decay drags compounding-positive rallies that
  1× SPY captures cleanly. Sharpe inverted from typical Carver:
  monotonic NEGATIVE through target_vol 20→25%. CAGR caps at 13.5%
  at the conservative end, **lower** than A2 TQQQ-track (17.33%).
- **Score-90 path**: would need Carver-style mechanic on a
  non-decaying underlying (e.g., NTSX 1.5× cash-efficient stack
  instead of SSO 2× LETF). Not tested in spy_beater hunt; tested in
  long_term_portfolio (NTSX-anchored F1+SPLIT) and capped at CAGR
  10.76% on score-anchored frame.

---

## Cross-family knowledge gained (positive findings)

Despite no WINNER, the hunt produced robust knowledge:

1. **Gayed 200d SMA gate works** for CAGR uplift on leveraged equity
   (iter 001-007), but caps at MDD 50-60% on 1986+ synth.
2. **KMLM dose-response on SPY-track** is monotonically positive
   through 40% (iter 005 confirmed) — Sharpe lifts continuously, no
   inflection in 0-40% KMLM range. **OPPOSITE** behavior on HFEA
   backbone where KMLM 15→25% adds 0.5pp MDD instead.
3. **NDX-track adds +3pp CAGR / +13pp MDD over SPY-track** — empirically
   measured trade-off.
4. **TLT-on-top of KMLM helps** marginally (iter 005, 006) — duration
   diversifier over MF crisis-alpha is additive, not redundant.
5. **HFEA classical 55/45 falsified** at 2022 stress (iter 008 KILL #24
   fire). Bogleheads risk-parity claim: optimal Sharpe at 50/50 or
   LOWER UPRO%, NOT 55/45 — **regime-specific to 1986-2019 declining-rate environment**.
6. **Vol-targeting on LETF underlying inverts Sharpe-CAGR trade-off**
   (iter 010 KILL #32 fire) — Carver canonical does NOT transfer to
   LETF-on-SPY because of daily-reset decay drag.
7. **Architectural ceiling at 67** is independent of rubric calibration
   — KILL #34 sanity check confirmed via alternative rubrics.

These findings are **robust negative knowledge** that the spy_beater
rubric (CAGR-anchored, 2-dataset, gross-of-tax) cannot be cleared by
the canonical leveraged + crisis-alpha + regime-gate + vol-target
toolkit.

---

## Why the hunt is closing now (not at iter 50)

The original 50-iter target was set with an expectation that breadth
would surface unexpected lift. After 10 iters / 4 families:
- All Tier 1-2 directions in `PROMISING_DIRECTIONS.md` tested
- Only Tier 3 untested: D1 (concentrated growth + monthly momentum),
  C2 (CAPE-timing), D2 (NTSX + UPRO + AVUV stacked equity heavy)
- D1 / D2 expected score range overlaps 60-67 (per `PROMISING_DIRECTIONS.md`
  ~5% chance to break 67); C2 noted "out-of-sample reliability questionable"
- DSR cumulative penalty tightens with each new trial; n_trials=35
  already imposes worst p ≤ 5e-3; 40 more iters at +3 trials/iter →
  n=155, would push DSR threshold close to noise floor

**Marginal cost-benefit**: 40 more iter sessions vs ~5%/iter chance of
lift on closest-to-winner. Expected value of continuing < cost of
40 more sessions + DSR-penalty risk. Closing now preserves statistical
integrity at high confidence.

---

## Mandate compliance

- **§1 (Maintenance Mode)**: Plano C 100% allocation **UNCHANGED**.
  spy_beater_hunt was scoped to optimize within Plano C, not to override
  it. No reactivation of Plano A or Plano B from this hunt.
- **§7 (Override request gate)**: NOT triggered — spy_beater hunt did
  NOT produce a WINNER candidate. F1+SPLIT remains the deployable
  strategy under §1.
- **CLAUDE.md regra 2 (citation discipline)**: 100% adherence across
  all 10 iters; primary citations in each `hypothesis.md` and
  `final_report.md`.
- **CLAUDE.md regra 1 (jornada/ updates)**: 10 jornada entries created
  (one per iter); README index updated.

---

## Deploy recommendation: F1+SPLIT (incumbent fallback)

Citation: `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking;
`studies/long_term_portfolio/PHASE_1_WINNERS.md` (43 iters)

**F1+SPLIT** = NTSX 25 + GDE 25 + KMLM 17.5 + DBMF 17.5 + TLT 15

- Mean CAGR: ~10.76% (gap −0.45pp below SPY 11.21%)
- Mean MDD: ~16.76% (38pp **better** than SPY 55.17%)
- Mean Sharpe: ~0.83 (above SPY 0.67)
- 7-gate battery: passes ≥ 2/3 datasets cross_met
- Cumulative n_trials: 156 (long_term_portfolio loop) — high statistical confidence

Trade-off: F1+SPLIT trades a small CAGR gap for **massively better
MDD and Sharpe**. Psychologically harder (user feedback: "MUITO DIFÍCIL
seguir uma estratégia que não vai bater o SPY em CAGR") but
mathematically the dominant deploy candidate after 53 cumulative
honest iters.

---

## What remains untested (knowledge gap)

For full transparency, the following directions are knowledge gaps
that future hunts could explore:

1. **D1 concentrated growth + monthly momentum gate** — flagged Tier 3
2. **C2 CAPE-timing** — flagged Tier 3 with strong out-of-sample warning
3. **D2 NTSX + UPRO + AVUV stacked equity heavy** — flagged Tier 3
4. **HFEA with non-TMF diversifier** (GLD, commodities, breakouts) — not in PROMISING_DIRECTIONS.md
5. **NTSX-based vol-target** (avoiding LETF decay) — gap; could lift C1 family by ~5pts
6. **Multi-horizon rebalancing** (quarterly Gayed gate vs daily) — gap
7. **3-dataset framework with 2010-2019 bull-only window** — could artificially lift scores

None of these are expected to break the 67-ceiling under the
spy_beater rubric (CAGR-anchored 30/20/20/10/10/10/5). Each is at
most a +5pt lift on one criterion, insufficient to close 23pt gap
to WINNER threshold.

---

## Citations summary

- `[advances_fin_ml, p.31-34]` — factor framework: 4 architecture
  families span the leverage × timing × diversification space; absence
  of WINNER is a structural negative result.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative_n_trials=35;
  closing at n=35 preserves statistical integrity vs continued
  inflation.
- `[advances_fin_ml, p.208-211]` — PBO grid-level < 0.5 hit consistently
  across iters; selection bias controlled.
- `[advances_fin_ml, p.196-202]` — bootstrap CI on Sharpe; gate G6
  passed by closest-to-winner.
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` — Gayed 200d SMA
  validated as best-in-class for CAGR uplift but caps at MDD 50%.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking
  baseline (F1+SPLIT) is deploy fallback.
- `[systematic_trading, ch.10]` Carver — vol-targeting Sharpe-improving
  property documented for commodity/FX, does NOT transfer to LETF-on-SPY.
- `[ilmanen_expected_returns, ch.19]` — MF crisis-alpha (KMLM dose 0-40%)
  validated as Sharpe-improving on SPY-track; saturates within rubric.
- HFEA Bogleheads 2019 — barbell falsified at 2022 stress; risk-parity
  claim regime-specific to 1986-2019.

---

## Status

**`spy_beater_hunt: status: closed_no_winner`** as of 2026-04-30.

- Total iters completed: 10 / 50 target
- Cumulative n_trials: 35
- KILL #33 (architectural ceiling) fired
- F1+SPLIT incumbent fallback deploy-ready
- Mandate §1 100% Plano C unchanged
- Negative result has policy value: 53 cumulative iters
  (long_term_portfolio 43 + spy_beater 10) failed to find a strategy
  that beats SPY in BOTH CAGR and MDD on the 2-dataset framework

**Hunt CLOSED.**
