# Iter 031 — H11 META-ENSEMBLE 4-WAY GLD-TSMOM LOOKBACK AXIS at 4th constituent

**Date**: 2026-04-30
**Slug**: `H11-meta-ensemble-4way-gld-tsmom-lookback-axis`
**cumulative_n_trials before**: 116
**cumulative_n_trials after**: 120 (+4 configs)
**Iter type**: 15th iter at meta-axis — sub-axis (GLD-source TSMOM lookback variation, signal-asset fixed at GLD per iter 030 KILL #125 ceiling-breach)

---

## Hypothesis

Iter 030 KILL #125 FIRED — established **ORTHOGONAL-ASSET-CLASS-TSMOM-SOURCE BONUS at 4-way meta-ensemble**: GLD-TSMOM-6m signal on TQQQ-stack sleeve outperforms QQQ-TSMOM-6m baseline by +1pt (+0.74pp CAGR / +0.083 Sharpe at 25% dose) on score axis. This was the FIRST ceiling-breach in 9 sequential meta-axis iters (sequence 018→030 = 70→71→67→70→70→71→70→69→69→**72**). The closest-to-winner shifted to iter 030 H10.4 (4-way 25/25/25/25 with GLD-TSMOM-6m at 4th constituent) at score 72.

Iter 029 KILL #119 FIRED — established **TSMOM-LOOKBACK INVERTED-U principle**: for QQQ-TSMOM gate at 4th constituent slot, score-axis as a function of lookback follows an inverted-U with peak at ~6m (3m H9.2 ~67-68 / 6m H6.4 71 / 12m H9.1 69). Generalization explicitly noted in iter 029: "**lookback-peak-optimum may differ for other signal-asset combinations** (e.g., SPY-SMA peaks at 200d ≈ 10m per Faber; QQQ-TSMOM peaks at 6m due to higher volatility)."

Iter 031 directly tests **the joint surface** of these two axes — holding signal-asset fixed at GLD (per iter 030 ceiling-breach) and varying TSMOM lookback (3m/6m/9m/12m). The mechanism hypothesis: **GLD has lower realized volatility than QQQ** (~14-18% vs ~22-28%), and lower-vol asset trends are typically slower-decaying → optimal lookback may be **longer** than QQQ's 6m peak. If GLD-TSMOM-9m or 12m exceeds the 6m baseline of 72, the new ceiling moves to 73+ — strong-form falsification of iter 030's borderline +1pt breach as a one-off.

Four lookback variants tested at the 4th constituent slot (signal_ticker=GLDSIM fixed, sleeve TQQQSIM 30 + QLDSIM 30 + KMLMSIM 30 + TLTSIM 10 fixed, weight 25% fixed = iter 030 H10.4 baseline):
- **GLD-TSMOM-3m** (lookback=63): short-lookback whipsaw test
- **GLD-TSMOM-6m** (lookback=126): BASELINE — replicates iter 030 H10.4 selected config (expected ≈72)
- **GLD-TSMOM-9m** (lookback=189): KEY HYPOTHESIS — GLD lower-vol → longer trend persistence
- **GLD-TSMOM-12m** (lookback=252): Moskowitz canonical TSMOM lookback

This isolates the GLD-source LOOKBACK axis from the SIGNAL-ASSET axis (iter 030 mapped QQQ/SPY/GLD at 6m fixed) and the SLEEVE axis (iter 026 KILL #105). If H11.6m baseline replicates iter 030 H10.4 score 72, AND H11.9m or H11.12m > 72 → asset-variant lookback-peak EMPIRICALLY CONFIRMED + iter 030 ceiling breach extends. If max H11 ≤ 72 → 15th meta-axis ceiling confirmation, GLD lookback-peak is also 6m (asset-INVARIANT lookback-peak).

**Citation**:
- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction multi-alpha streams (4-way meta-ensemble 15th iter — GLD-source lookback sub-axis exploration)
- **Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250** — TSMOM lookback robustness (1m/3m/6m/9m/12m sweep across asset classes, with 12m canonical lookback)
- `[ivy_portfolio]` Faber GTAA single-asset 6-10m moving average (GLD-source 6-12m bracket per Faber's commodity proxy DBC-10m)
- `[asness_value_momentum]` momentum-everywhere across asset classes (gold/commodity TSMOM premium structure)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA (A2 + G2 baseline retained)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking (F1 stack always-on retained at 3rd constituent)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in A2/G2/E1 ON-state)
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way)
- iter 029 KILL #119 (TSMOM-lookback inverted-U at 6m for QQQ; signal-asset generalization explicit)
- iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt at signal-asset granularity for GLD)

---

## Configs (4)

All share constituents A2 (25%), G2 (25%), F1 (25%), with 4th constituent E1-GLD-variant (25%) varied by `lookback_days` parameter only. Signal-asset FIXED at GLDSIM (per iter 030 KILL #125 ceiling-breach finding). ON-sleeve identical to iter 030 H10.4 E1_GLD (TQQQSIM 30 + QLDSIM 30 + KMLMSIM 30 + TLTSIM 10) holding sleeve constant — isolating lookback effect.

| config | 4th lookback | rationale |
|---|---:|---|
| `h11_meta_4way_25a2_25g2_25f1_25e1gld_3m` | 63 | short-lookback whipsaw (replicates iter 029 H9.4 pattern but on GLD) |
| `h11_meta_4way_25a2_25g2_25f1_25e1gld_6m` | 126 | BASELINE replicates iter 030 H10.4 (expected ≈72) |
| `h11_meta_4way_25a2_25g2_25f1_25e1gld_9m` | 189 | KEY HYPOTHESIS — GLD lower-vol → longer trend persistence (expected 72-73) |
| `h11_meta_4way_25a2_25g2_25f1_25e1gld_12m` | 252 | Moskowitz canonical TSMOM lookback |

---

## KILL conditions pre-committed

Numbered following iter 030's #126; iter 031 starts at #127.

- **KILL #127 (META-AXIS CEILING — 15th confirmation at NEW ceiling 72)**: if max H11 score ≤ 72 → 15th meta-axis confirmation; iter 030 ceiling-breach was BORDERLINE single-iter +1pt break; confirms ceiling 72 STRICT new ceiling across 11 sequential meta-axis iters (sequence 018→031 with iter 030 = 72 as new max). If GLD-source lookback-axis is bounded ≤ 72, iter 030's breach was specifically due to signal-asset-orthogonality at lookback=6m, NOT due to lookback-axis exploration on GLD source.

- **KILL #128 (META-AXIS CEILING — strong-form FALSIFICATION at NEW ceiling)**: if max H11 > 73 strict → ceiling 72 FALSIFIED; lookback-axis on GLD-source breaks new ceiling; confirms iter 029 KILL #119 generalization (asset-variant lookback peak) AND extends iter 030 KILL #125 (orthogonal-source bonus is additive across lookbacks). Would re-open hunt aggressively at signal-asset × lookback joint surface.

- **KILL #129 (LOOKBACK PEAK SHIFTS for GLD-source — asset-variant lookback)**: if argmax(score across H11 lookbacks) is 9m or 12m AND that score > H11.6m by ≥ 1pt → CRITICAL extension of iter 029 KILL #119: lookback-peak-optimum varies with signal-asset volatility characteristics. Empirical proof that GLD has different optimal lookback than QQQ. Score axis is ASSET-VARIANT in lookback dimension. **Highest-credibility positive outcome**.

- **KILL #130 (LOOKBACK INVERTED-U INVARIANT across signal-assets)**: if score(3m) < score(6m) AND score(9m) ≤ score(6m) AND score(12m) ≤ score(6m) (with 6m as max) → GLD-TSMOM has SAME inverted-U peak at 6m as QQQ-TSMOM; iter 029 KILL #119 generalization PARTIALLY FALSIFIED (asset-INVARIANT lookback peak, not asset-VARIANT). **Strongest empirical principle**: 6m is universally near-optimal for TSMOM gates at meta-axis 4-way structure regardless of signal-asset.

- **KILL #131 (LOOKBACK RUBRIC-NEUTRAL on GLD-source — 8th rubric saturation class)**: if all 4 GLD-lookback variants score within ±1pt → 8th class of RUBRIC SATURATION: lookback-axis on GLD-source is RUBRIC-NEUTRAL within meta-axis 4-way structure. The signal-asset orthogonality (KILL #125) saturates the rubric independent of lookback selection.

- **KILL #132 (CAGR-axis vs Sharpe-axis DECOUPLING on GLD-source)**: if mean Sharpe varies but mean CAGR stays within ±0.3pp across lookbacks → KILL #120 pattern (raw-metric vs gate-axis decoupling) replicates on GLD source. Lookback variations within asset-orthogonal signal source affect Sharpe-axis but not CAGR-axis.

---

## Expected outcomes

| config | expected score | reasoning |
|---|---:|---|
| h11 e1gld 3m | 70-71 | short-lookback whipsaw — Sharpe drag matches iter 029 H9.4 QQQ-3m pattern |
| h11 e1gld 6m | 72 | direct replication of iter 030 H10.4 selected config |
| h11 e1gld 9m | 71-73 | KEY HYPOTHESIS — GLD lower-vol → longer trend; could match or exceed 6m peak |
| h11 e1gld 12m | 70-72 | Moskowitz canonical; commodity TSMOM peak per [asness_value_momentum] |

Highest expected score: 73 (KILL #129 fires) or 72 (KILL #127 fires — ceiling holds). Most likely outcomes:
- **Most credible**: KILL #127 + KILL #130 fire jointly → ceiling 72 confirmed with GLD inverted-U peak also at 6m (asset-INVARIANT)
- **Most informative if true**: KILL #128 + KILL #129 fire jointly → asset-variant lookback peak, ceiling extends to 73+
- **Rubric-saturation case**: KILL #127 + KILL #131 fire → all 4 within ±1pt rubric-neutrality on lookback axis at GLD source

---

## Stress windows expected

Same 4 stress windows as prior iters (2008 GFC, 2020 COVID, 2022 inflation, 2000-02 dot-com). The lookback variation should differ in:

- **2008 GFC**: GLD rallied 2008-09 → all GLD-TSMOM variants likely KEEP gate ON during NDX crash; longer lookbacks (9m/12m) may be MORE persistent in keeping gate ON during early-2008 → could either help (capture late-2008 recovery on TQQQ) or hurt (catastrophic if recovery delays). MDD-axis sensitivity test.
- **2020 COVID**: brief 1-month gold dip then rapid recovery → 3m lookback may flip OFF/ON whipsaw; 12m lookback likely stays ON throughout. Sharpe-axis sensitivity test.
- **2022 inflation**: GLD largely flat ($1830→$1830 endpoints) while equities/bonds collapsed → 3m/6m lookbacks ambiguous; 9m/12m likely OFF (rolling 9-12m gold trend was modestly negative). Could DIFFER from QQQ-TSMOM-12m's clear OFF call.
- **2000-02 dot-com**: gold rallied 2001-2003 (post-dot-com USD weakness) → all GLD lookbacks gate ON during sustained gold uptrend, regardless of NDX crash. **Critical period**: gate-sleeve incoherence (KILL #126 from iter 030) is SHARPEST here because TQQQ was wiped while gold-trend signal said ON. Sleeve-incoherence may compound across lookbacks.

---

## INCOMPLETE flags

- **GLDSIM coverage**: 1986-01 to 2026-04, 10151 trading days — covers full lh_56y dataset. Same coverage as iter 030. No coverage gap.
- **Lookback range bounded by `momentum` filter implementation**: `studies/spy_beater_hunt/lrs_engine.py` (or wherever momentum is implemented) accepts lookback_days parameter; assumed range 21-504 valid. Iter 029 already tested 63 (3m) and 252 (12m); iter 031 adds 189 (9m) which is between iter 029 boundary points.
- **Joint signal-asset × lookback grid is partially explored**: iter 029 mapped QQQ × {3m, 6m, 12m} (3 cells); iter 030 mapped {QQQ, SPY, GLD} × 6m (3 cells); iter 031 maps GLD × {3m, 6m, 9m, 12m} (4 cells, with 6m duplicating iter 030 H10.4). Joint surface remains UNDER-MAPPED at QQQ × 9m, SPY × {3m, 9m, 12m}, GLD × 18m+. Future iters could complete the grid if iter 031 confirms asset-variant lookback peak.
- **No new infra**: reuses 'blend' + 'lrs' (momentum filter with `lookback_days` parameter varied) + 'static' spec types from iter 014/018-030. **771 tests baseline preserved**.
- **DSR Bonferroni at n_trials=120**: threshold 0.05/120 = 4.17e-04. Worst per-config DSR p must be < 4.17e-04 to PASS Bonferroni; tighter than iter 030's 4.31e-04 by 0.14e-04 (3.2% margin reduction).
- **Tax classification**: meta-blend with TSMOM-gate constituent (lrs/momentum filter) → annual_realize. Drag expected ~2.0-2.2pp similar to iter 030 H10.4 (2.13pp).
- **Position-invariance** (iter 028 KILL #114): 4th-position constituent at 25% weight is signal-rubric-neutral with respect to permutation; only lookback parameter changes within fixed sleeve composition.
- **F1 stack retained at 3rd position** — sextuple-confirmed uniquely-Pareto-optimal per iter 027 KILL #110 + iter 028/029/030 implicit. Not re-tested in iter 031.

---

## Prior-iter context

Direct parents:
- **iter 030 H10.4** (4-way 25a2_25g2_25f1_25e1gld @ 6m, score **72** — current closest-to-winner). Iter 031 holds H10.4 framework constant and varies ONLY the GLD-TSMOM lookback parameter.
- **iter 029 H9** (gate-LOOKBACK sub-axis on QQQ at 4th constituent — KILL #119 inverted-U peak at 6m for QQQ-TSMOM). Iter 031 extends KILL #119 generalization to GLD signal-source.
- **iter 026 H6.4** (gate-source-distinctness +1pt KILL #102 at 4-way; QQQ-TSMOM-6m baseline at score 71). Iter 030 H10.4 surpassed by +1pt; iter 031 tests if 6m is also peak for GLD or if peak shifts.

If KILL #128 fires (max > 73) → architecture re-opens at signal-asset × lookback joint surface. If KILL #127 + (#130 or #131) fires → 14-axis architectural taxonomy + 9th class of RUBRIC SATURATION (lookback-axis rubric-neutral on GLD source OR lookback inverted-U asset-invariant). Either outcome: hunt's empirical informational value continues at meta-principle level.

cumulative_n_trials = 116 → 120 with iter 031. Bonferroni 4.17e-04 maintained as long as worst p < 4.17e-04 (iter 030 worst was 6.55e-05 → 6.4× margin remaining).
