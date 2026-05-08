# iter 023 — B7 NTSX-anchored low-leverage static + MF dose-response

**Date**: 2026-04-30
**Slug**: `B7-ntsx-anchored-low-leverage-mf`
**Cumulative n_trials**: 80 (iter 022) → **86** (iter 023, +6)

---

## Hypothesis

The iter 022 KILL #79 finding established the empirical generalization
**MF crisis-alpha effectiveness is INVERSELY proportional to backbone
notional leverage**: at HFEA classical (≥300% notional via 165% UPRO +
135% TMF) KMLM was Sharpe-flat-to-negative, while at HFEA-modest (200%
notional via 150% UPRO + 50% TLT) KMLM lifts Sharpe by +0.038 to
+0.084. The B5 axis (200% notional barbell) capped at gross score 58
because:
1. CAGR axis 18/30 (mean 14.13% gives ~60% of anchor span)
2. **MDD axis 5/20 driven by anchor [0.7, 0.15]** — even passing 55.17%
   bar at 54.47% the rubric only gives 5pts since 50%+ MDD is in penalty
   zone
3. Sharpe axis 2/10 at 0.736 (well below meta-axis 1.025+)

iter 023 tests whether moving DOWN one further notional-leverage step
(150% via NTSX 100% internal 90/60 stack) flips the Sharpe-axis
mathematics. Predicted mechanism per `[risk_parity, ch.5, p.10]`
Carlson: **NTSX is the most capital-efficient SPY-anchored stacking
vehicle below the static-barbell axis**, and per the iter 022 KILL #79
generalization, KMLM should lift Sharpe even more pronouncedly at 150%
than at 200%.

**Core hypothesis**: NTSX-anchored static portfolios at 1.5× notional
leverage with 20-30% MF dose can reach mean Sharpe ≥ 0.95 AND mean MDD
≤ 30% (vs B5's 0.736/54.47%) WHILE staying above CAGR bar 11.21%.

Score implications under spy_beater rubric (anchors saturated at meta-
axis):
- CAGR axis (anchor [0.05, 0.20]): NTSX 100% predicted 12.5% → 18/30;
  NTSX80+KMLM20 predicted 11.0% → 15/30 (TIGHT on CAGR bar)
- MDD axis (anchor [0.5, 0.1]): predicted 25-30% MDD → 12-14/20 (vs
  B5's 5/20 at 54.47%; vs meta-axis 15/20 at 28.5%)
- Gates 13/20 retained; DSR 10/10; Sharpe 6-8/10 at 0.95-1.05;
  Robustness 9-10/10
- Net estimated score 65-72 → **PROMISING tier achievable, ceiling
  break at 71 unlikely**

**This is a static-axis exploration of the MF-effectiveness curve
extension**, NOT a meta-axis variant — does NOT violate KILL #71.

---

## Configs (N=6)

Anchor: NTSX 100% baseline. Doses sweep KMLM (Mount Lucas TF index) /
DBMF (broader CTA basket) / TLT (1× duration extension) at MF total
weight 0-30%.

| config | NTSX | KMLM | DBMF | TLT | notional¹ |
|---|---:|---:|---:|---:|---:|
| `b7_ntsx100` | 1.00 | 0.00 | 0.00 | 0.00 | 150% |
| `b7_ntsx80_kmlm20` | 0.80 | 0.20 | 0.00 | 0.00 | 120% |
| `b7_ntsx80_dbmf20` | 0.80 | 0.00 | 0.20 | 0.00 | 120% |
| `b7_ntsx70_kmlm20_tlt10` | 0.70 | 0.20 | 0.00 | 0.10 | 105% + 10% UST |
| `b7_ntsx70_kmlm15_dbmf15` | 0.70 | 0.15 | 0.15 | 0.00 | 105% |
| `b7_ntsx70_kmlm10_dbmf10_tlt10` | 0.70 | 0.10 | 0.10 | 0.10 | 105% + 10% UST |

¹ Notional = NTSX_weight × 1.5. NTSX is internal 90/60 SPY/UST stack
per `[risk_parity, ch.5]` Carlson canonical formulation.

All 6 configs are `spec.type = "static"` — buy-hold, max tax efficiency
per `tax_layer.py` (drag predicted 0.55-0.75pp).

---

## KILL conditions (numbered after KILL #82 from iter 022)

| KILL # | Trigger | Implication |
|---:|---|---|
| **#83** | iter-023 max gross score ≤ 65 | NTSX-anchored static at 1.5× notional INFERIOR to B5 200% notional (KMLM effectiveness improves with lower leverage but ABSOLUTE CAGR too low) → axis CLOSED |
| **#84** | iter-023 max gross score ≥ 70 | NTSX-anchored static at 1.5× notional + 20-30% MF dose lifts past B5 ceiling 58 by ≥ 12pts → NEW architectural sub-axis (B7) VIABLE; HUNT REOPENS at low-leverage static-axis |
| **#85** | b7_ntsx80_kmlm20 mean Sharpe ≥ baseline b7_ntsx100 + 0.05 | KILL #79 generalization extends to 1.5× notional regime — MF lift confirmed at 150% leverage CONFIRMED |
| **#86** | b7_ntsx100 PASSES CAGR bar at 11.21% as standalone (no MF, no leverage above 1.5×) | Pure NTSX is MINIMUM viable static for spy_beater CAGR bar — establishes lower bound on architectural taxonomy |
| **#87** | b7_ntsx70_kmlm15_dbmf15 mean Sharpe ≥ b7_ntsx80_kmlm20 mean Sharpe + 0.03 | Multi-source MF (KMLM + DBMF) decorrelation effect at 1.5× notional CONFIRMED — split MF dose Pareto-improves single-source |
| **#88** | iter-023 max gross score ≥ 75 | STRONG tier reached on B7 axis — would be FIRST STRONG tier in entire spy_beater hunt across 23 iters; would force mandate §7 override request |

KILL #83 is the EXPECTED outcome (estimated 60-70% probability based on
B5 ceiling at 58 + CAGR-axis penalty of moving from 200%→150%
notional). KILL #84 is the AMBITIOUS outcome (estimated 25-30% prob).
KILL #88 is the WINNER outcome (estimated 5% prob).

---

## Expected outcomes

### Most likely (prob ≈ 60%)
- b7_ntsx100 baseline: CAGR ~12.5%, MDD ~30%, Sharpe ~0.85, score ~62
- b7_ntsx80_kmlm20: CAGR ~11.0%, MDD ~25%, Sharpe ~0.95, score ~65
- KILL #83 NOT FIRED, KILL #84 NOT FIRED → axis lands MARGINAL/PROMISING
- closest-to-winner UNCHANGED (iter-019 71 retained)

### Plausible (prob ≈ 25%)
- b7_ntsx80_kmlm20 hits CAGR ~11.5% AND Sharpe ~1.05 → score 70
- KILL #84 FIRES → axis viable, hunt reopens for iter 024+ exploration
  of NTSX + multi-MF combinations

### Unlikely (prob ≈ 5%)
- Score ≥ 75 → STRONG tier → mandate §7 override request

### Failure mode (prob ≈ 10%)
- NTSX 100% standalone fails CAGR bar (CAGR < 11.21%) → KILL #86 NOT
  FIRED, NTSX is BELOW spy_beater minimum viable threshold; B7 axis
  CLOSED at all 6 configs FAIL bars

---

## INCOMPLETE flags

- **NTSX synth (lh_56y)**: NTSXSIM testfolio cache covers 1986+. The
  synth approximates 90% SPYSIM + 60% IEFSIM with monthly rebalance and
  −0.20%/y expense ratio. ER drag understates real-world ETF tracking
  error by ~5-10 bps. Not material for spy_beater rubric.
- **MF synth (KMLMSIM)**: 1986-1988 uses Fama-French momentum proxy
  (annualized 18%); 1989-2024 uses MLM index (Mount Lucas Managed
  Futures). 2008/2022 stress periods have actual MLM data. INCOMPLETE
  by ~3y at start of synth.
- **DBMFSIM**: synth from 2010+ via DBi Managed Futures benchmark; pre-
  2010 backfilled via cross-section of CTA factor returns. iMGP DBi
  itself launched 2019, so pre-2019 is reconstructed.
- **DSR cumulative_n_trials = 86**: tightens p-threshold under
  Bonferroni to ~0.05/86 = 5.81e-04. iter 022 worst p was 1.54e-02
  (passes single-comparison but tight under multiple-testing). Iter 023
  expected worst p in similar 1e-04 to 1e-02 range; if any config p >
  6e-04, mark INCOMPLETE.
- **Tax classification**: all 6 configs `spec.type = "static"`,
  buy_hold (terminal DARF settlement). Drag predicted 0.55-0.75pp.

---

## Citations

- `[risk_parity, ch.5, p.10]` Carlson — NTSX as canonical capital-
  efficient SPY-anchored stack (90% SPY + 60% UST internal = 150%
  notional with single ER charge)
- `[ilmanen_expected_returns, ch.19]` — MF crisis-alpha role; KMLM as
  factor exposure
- `[ilmanen_expected_returns, ch.20]` — Gold + commodities crisis-alpha
  alternatives (excluded from this iter; B6 hypothetical exploration)
- `[advances_fin_ml, p.31-34]` factor framework — combining MF families
  for decorrelated alpha
- `[advances_fin_ml, p.208-211]` PBO via CSCV N=6 grid
- `[advances_fin_ml, p.222-223]` DSR with cumulative n_trials = 86
- HFEA Bogleheads 2019 — leverage-backbone reference (B5 modest-HFEA at
  200% notional caps at 58; B7 explores 150% one step lower)
- iter 022 KILL #79 finding — MF effectiveness ∝ inverse leverage
  generalization extension test

---

## Methodology notes

- Reuses existing 'static' spec type from iter 008/022 — NO new infra,
  NO TDD required.
- All 6 assets DIRECT in testfolio cache: NTSXSIM, KMLMSIM, DBMFSIM,
  TLTSIM. No synth construction needed.
- Datasets: lh_56y (40y synth) + spy_real (22.7y Tiingo daily). 2-
  dataset framework unchanged.
- Run via `studies.spy_beater_hunt.run_iter.run_iter_spy_beater(...)` —
  scoring + gates + tax-layer + plots automatic.
- 771 tests baseline preserved (no changes to engine code).

---

## Pre-commitment

This hypothesis is committed BEFORE running the backtest. Any KILL
firing will be reported with FIRED/NOT FIRED designation in
`final_report.md` lesson section. No retroactive KILL revision.
