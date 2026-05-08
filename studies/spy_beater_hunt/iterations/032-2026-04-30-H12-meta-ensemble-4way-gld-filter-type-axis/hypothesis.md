# Iter 032 — H12 META-ENSEMBLE 4-WAY GLD-FILTER-TYPE AXIS at 4th constituent

**Date**: 2026-04-30
**Slug**: `H12-meta-ensemble-4way-gld-filter-type-axis`
**cumulative_n_trials before**: 120
**cumulative_n_trials after**: 124 (+4 configs)
**Iter type**: 16th iter at meta-axis — sub-axis (GLD-source FILTER-TYPE variation; signal-asset fixed at GLDSIM per iter 030 KILL #125; lookback-window held at ~6m peak per iter 031 KILL #130)

---

## Hypothesis

Iter 030 KILL #125 FIRED — established **ORTHOGONAL-ASSET-CLASS-TSMOM-SOURCE BONUS at 4-way meta-ensemble**: GLD-momentum-126d signal on TQQQ-stack sleeve outperforms QQQ-momentum-126d baseline by +1pt (+0.74pp CAGR / +0.083 Sharpe at 25% dose). FIRST ceiling-breach in 9 sequential meta-axis iters.

Iter 031 KILL #130 FIRED — established **TSMOM-LOOKBACK INVERTED-U IS ASSET-INVARIANT at meta-axis 4-way structure** (Principle D): the lookback-peak-optimum at the 4th constituent slot is at ~6m regardless of signal-asset choice (QQQ per iter 029 H6.4; GLD per iter 031 H11.2). Iter 029 KILL #119's "lookback-peak shifts with signal-asset volatility" generalization is FALSIFIED for QQQ/GLD pair.

Iter 030 KILL #124 NOT FIRED ESTABLISHED **NEW PRINCIPLE B — TRIPLE-GRANULARITY DISTINCTNESS** at 4-way meta-ensemble: signal-source-distinctness operates at 3 axes — (asset × filter × lookback). SPY-momentum-126d (iter 030 H10.spy) preserved +1pt bonus DESPITE signal-asset matching G2's SPYSIM, because filter-type (momentum vs SMA) AND lookback (126d vs 200d) provided distinctness on 2/3 axes.

**Iter 032 directly tests Principle B at GLD-source** by varying filter-type at the 4th constituent slot:
- holding signal_ticker FIXED at GLDSIM (per iter 030 KILL #125 ceiling-breach)
- holding lookback FIXED at peak ~6m per iter 031 KILL #130 (where viable)
- varying filter-type across {momentum, sma, ema} at canonical windows

The mechanism hypothesis decomposes the +1pt orthogonality bonus along filter-type axis:
- **If +1pt is FILTER-TYPE-INVARIANT** (asset-axis alone drives bonus) → all GLD filter-type variants score 72 (KILL #133 fires; asset-class orthogonality bonus is filter-type-decoupled)
- **If +1pt is FILTER-TYPE-COUPLED** (filter-type axis distinctness participates in the bonus) → some variants lose +1pt (KILL #135 fires; bonus depends on filter-type at GLD source)
- **If filter-type axis enables joint-orthogonality bonus extension** → max H12 > 72 (KILL #134 fires; filter-type axis is a new ceiling-breach mechanism — would imply orthogonality bonus is COMPOSITIONAL across asset+filter+lookback axes)

The borderline cases test triple-granularity Principle B's robustness:
- **GLD-SMA-126d**: asset distinct, filter-type matches A2/G2 (both SMA), lookback distinct — 2/3 axes distinct → expected score 72 if Principle B holds
- **GLD-SMA-200d**: asset distinct, filter-type matches A2/G2, lookback ALSO matches A2/G2 (200d) → only 1/3 axes distinct → expected score < 72 if Principle B requires ≥ 2/3 axes
- **GLD-EMA-126d**: asset distinct, filter-type alternative (EMA), lookback distinct — 3/3 axes distinct → expected score 72 (or +0/+1 vs baseline)

If GLD-SMA-200d preserves score 72 → Principle B requires only 1/3 axes (asset-class alone is sufficient). If GLD-SMA-200d falls to ~71 → Principle B requires ≥ 2/3 axes (filter-type or lookback must be distinct).

**Citation**:
- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction multi-alpha streams (4-way meta-ensemble 16th iter — GLD-source filter-type sub-axis exploration)
- `[ivy_portfolio]` Faber GTAA single-asset 6-10m moving average (commodity proxy DBC-10m — GLD-SMA-200d ≈ Faber commodity gate)
- **Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250** — TSMOM canonical (GLD-momentum-126d retained as baseline)
- `[asness_value_momentum]` momentum-everywhere across asset classes (commodity TSMOM premium structure preserved across filter-types)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate (A2 + G2 baseline retained — both SPY/QQQ-track 200d-SMA)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking (F1 stack always-on retained at 3rd constituent)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in A2/G2/E1 ON-state)
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way)
- iter 030 KILL #124 NOT FIRED — Principle B (triple-granularity distinctness asset × filter × lookback)
- iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt at signal-asset granularity for GLD)
- iter 031 KILL #130 (TSMOM-lookback inverted-U is ASSET-INVARIANT at 6m peak)

---

## Configs (4)

All share constituents A2 (25%), G2 (25%), F1 (25%), with 4th constituent E1-GLD-variant (25%). Signal-asset FIXED at GLDSIM (per iter 030 KILL #125 ceiling-breach finding). ON-sleeve identical to iter 030 H10.4 / iter 031 H11.2 (TQQQSIM 30 + QLDSIM 30 + KMLMSIM 30 + TLTSIM 10) holding sleeve constant — isolating filter-type effect.

| config | filter | param | rationale |
|---|---|---|---|
| `h12_meta_4way_25a2_25g2_25f1_25e1gld_mom126` | momentum | lookback=126d (~6m) | BASELINE — replicates iter 030 H10.4 (selected closest-to-winner at score 72) |
| `h12_meta_4way_25a2_25g2_25f1_25e1gld_sma126` | sma | window=126d (~6m) | filter-type substitution at lookback peak; 2/3 axes distinct (asset+lookback distinct, filter matches A2/G2) |
| `h12_meta_4way_25a2_25g2_25f1_25e1gld_ema126` | ema | window=126d (~6m) | EMA alternative trend filter; 3/3 axes distinct via EMA-not-SMA distinction |
| `h12_meta_4way_25a2_25g2_25f1_25e1gld_sma200` | sma | window=200d (~10m) | Faber GTAA canonical commodity 10m moving average; 1/3 axes distinct (asset only — filter+lookback both match A2/G2) |

The 4 configs span the 3-axis distinctness ladder:
- **3/3 distinct**: mom126 (momentum filter, 126d lookback, GLD asset) and ema126 (EMA filter, 126d window, GLD asset) — different filter-types from A2/G2's SMA
- **2/3 distinct**: sma126 (SMA filter MATCHES A2/G2 but at 126d lookback distinct from 200d) — only filter-type axis lost
- **1/3 distinct**: sma200 (SMA filter MATCHES A2/G2 + 200d window MATCHES A2/G2) — only asset-class distinct

---

## KILL conditions pre-committed

Numbered following iter 031's last #132; iter 032 starts at #133.

- **KILL #133 (META-AXIS CEILING — 16th confirmation at ceiling 72; bonus FILTER-TYPE-INVARIANT)**: if max H12 ≤ 72 AND max H12 = 72 (i.e., baseline mom126 reproduces 72 AND no variant exceeds it) → 16th meta-axis confirmation; ceiling 72 STRICT holds across 12 sequential meta-axis iters; the orthogonal-asset-class bonus is FILTER-TYPE-INVARIANT — asset-axis alone drives the +1pt bonus regardless of filter-type/lookback combination at GLD source.

- **KILL #134 (CEILING BREACH — filter-type axis EXTENDS ceiling above 72)**: if max H12 > 72 strict → ceiling 72 FALSIFIED; filter-type axis on GLD-source breaks new ceiling. Implication: orthogonality bonus is COMPOSITIONAL across asset+filter+lookback axes — filter-type distinctness AT GLD source enables joint-axis bonus extension. Would re-open hunt aggressively at filter-type × asset × lookback joint surface.

- **KILL #135 (BONUS FILTER-TYPE-COUPLED — at least one variant LOSES +1pt)**: if max H12 = 72 AND min H12 < 72 (i.e., baseline reproduces 72 but at least one variant scores ≤ 71) → orthogonality bonus is FILTER-TYPE-COUPLED, not invariant. Identifies which filter-type configurations PRESERVE the bonus and which LOSE it. **Highest-credibility positive outcome** for variant-distinctness investigation.

- **KILL #136 (FILTER-TYPE AXIS RUBRIC-NEUTRAL on GLD-source — 9th class of RUBRIC SATURATION)**: if all 4 H12 variants score within ±1pt → 9th class of RUBRIC SATURATION: filter-type axis on GLD-source is RUBRIC-NEUTRAL within meta-axis 4-way structure. Replicates iter 029 KILL #120 (raw-metric vs gate-axis decoupling) and iter 031 KILL #131 (lookback-axis rubric-neutral) on filter-type axis. Implication: rubric anchoring scales saturate the +1pt orthogonality bonus regardless of filter-type chosen.

- **KILL #137 (PRINCIPLE B 2/3-AXIS REQUIREMENT EMPIRICAL TEST)**: if score(sma200) < score(mom126) by ≥ 1pt AND score(sma126) ≥ score(mom126) - 0.5pt → empirical confirmation of Principle B's 2/3-axis distinctness requirement: bonus retained if ≥ 2/3 axes distinct, LOST if only 1/3 axis distinct. Sharpens iter 030 KILL #124 NOT FIRED finding from "filter-type and lookback alone preserve distinctness" to "≥ 2/3 axes alone preserve distinctness". **Strong-form Principle B refinement**.

- **KILL #138 (SMA-200 LOSES BONUS but sma126 PRESERVES)**: if score(sma200) < 72 AND score(sma126) ≥ 72 → confirms KILL #137 specifically; the asset-class-orthogonality is INSUFFICIENT alone (1/3 axis); ≥ 2/3 axes required (asset + lookback at minimum). Provides operational guidance: at GLD source, lookback distinctness is REQUIRED to retain bonus when filter-type matches A2/G2.

---

## Expected outcomes

| config | expected score | reasoning |
|---|---:|---|
| h12 e1gld mom126 (BASELINE) | 72 | direct replication of iter 030 H10.4 / iter 031 H11.2 selected configs |
| h12 e1gld sma126 | 71-72 | 2/3 axes distinct; Principle B suggests bonus preserved at 2/3 |
| h12 e1gld ema126 | 71-72 | 3/3 axes distinct via EMA; bonus preserved or +0/+1 vs mom126 |
| h12 e1gld sma200 | 70-71 | 1/3 axes distinct (only asset-class); bonus likely LOST per Principle B |

Highest expected score: 73 (KILL #134 fires unlikely) or 72 (KILL #133 fires — ceiling holds). Most likely outcomes:
- **Most credible**: KILL #133 + KILL #135 + KILL #137 + KILL #138 fire jointly → ceiling 72 confirmed AND filter-type-coupling demonstrated AND Principle B's 2/3-axis requirement empirically refined; sma200 LOSES bonus (~71) while ema126/sma126/mom126 PRESERVE (~72).
- **Most informative if ALL preserve**: KILL #133 + KILL #136 jointly fire → orthogonality bonus is FILTER-TYPE-INVARIANT (asset-axis alone is sufficient); Principle B's 2/3-axis requirement REVISED to "1/3 (asset alone) is sufficient at GLD source"; suggests the +1pt is purely asset-class-axis driven, not compositional.
- **Most informative if some FAIL**: KILL #135 + KILL #137 fire → identifies SPECIFIC filter-type configurations that lose bonus; sharpens Principle B; future signal-asset variations should preserve filter-type axis distinctness from existing constituents.
- **Ceiling-breach (low credibility)**: KILL #134 fires → filter-type axis enables joint-axis bonus extension; would imply additive orthogonality across filter-type axis.

---

## Stress windows expected

Same 4 stress windows as prior iters. The filter-type variation should differ in:

- **2008 GFC**: gold rallied 2008-09 → all GLD variants likely keep gate ON during NDX crash, but DIFFERENT timing of regime transition. SMA-200 (slower) may retain ON longer than EMA-126 (faster); momentum-126 distinct from both due to relative-trend signal nature. Expected MDD spread modest (33-36% across variants).
- **2020 COVID**: brief gold dip then rapid recovery → momentum-126 may flip OFF/ON whipsaw; SMA-126/SMA-200 likely smoother; EMA-126 in-between. Sharpe-axis sensitivity test.
- **2022 inflation**: GLD largely flat → SMA-126/SMA-200 likely stay ON (price near MA); momentum-126 ambiguous (relative-trend); EMA-126 similar to SMA-126. Critical regime where filter-type may differ MEANINGFULLY.
- **2000-02 dot-com**: gold rallied 2001-2003 → all GLD variants gate ON during sustained gold uptrend regardless of NDX crash. Sleeve-incoherence (KILL #126) compounds across all filter-types similarly.

---

## INCOMPLETE flags

- **GLDSIM coverage**: 1986-01 to 2026-04, 10151 trading days — covers full lh_56y dataset. Same coverage as iter 030/031. No coverage gap.
- **Filter-type implementations bounded by `lrs_engine.py`**: `studies/spy_beater_hunt/lrs_engine.py` supports {sma, ema} filter types via `gayed_200d_sma_gate(filter_type=...)`; `studies/spy_beater_hunt/run_iter.py` line 173-210 routes spec["filter"] to {sma, sma_band, ema, ema_band, momentum} variants. EMA implementation uses `ewm(span=window).mean()` adjust=False (standard pandas EMA).
- **No new infra**: reuses 'blend' + 'lrs' (sma + ema + momentum filters) + 'static' spec types from iter 014/018-031. **771 tests baseline preserved**.
- **DSR Bonferroni at n_trials=124**: threshold 0.05/124 = 4.03e-04. Worst per-config DSR p must be < 4.03e-04 to PASS Bonferroni; tighter than iter 031's 4.17e-04 by 0.14e-04 (3.4% margin reduction). iter 031 H11.2 worst was 6.55e-05 → 6.4× margin remaining; if H12 baseline reproduces H11.2 measurement, 6.1× margin will persist.
- **Tax classification**: meta-blend with LRS-gate constituents (sma/ema/momentum filters) → annual_realize. Drag expected ~2.0-2.2pp similar to iter 030/031 H10.4/H11.2 (2.13pp).
- **Position-invariance** (iter 028 KILL #114): 4th-position constituent at 25% weight is signal-rubric-neutral with respect to permutation; only filter-type/window parameter changes within fixed sleeve composition.
- **F1 stack retained at 3rd position** — septuple-confirmed uniquely-Pareto-optimal per iter 027 KILL #110 + iter 028/029/030/031 implicit. Not re-tested in iter 032.
- **H12.4 sma200 = Faber commodity gate**: matches A2/G2's 200d-SMA-on-equity baseline structure but on commodity asset. Tests if signal-asset axis ALONE (without filter-type or lookback distinctness) is sufficient. Mirror inverse of iter 030 H10.spy (which had ASSET MATCH but filter+lookback DISTINCT — preserved bonus per KILL #124).

---

## Prior-iter context

Direct parents:
- **iter 030 H10.4** (4-way 25a2_25g2_25f1_25e1gld @ momentum-126d, score **72** — closest-to-winner). Iter 032 holds H10.4 framework constant, varies ONLY the GLD-side filter-type at fixed lookback peak.
- **iter 031 H11.2** (4-way 25a2_25g2_25f1_25e1gld @ momentum-126d, score 72 — REPLICATES iter 030 H10.4 exactly). Provides reproducibility anchor.
- **iter 030 H10.spy** (4-way 25a2_25g2_25f1_25e1spy @ momentum-126d, score est 71 — NEW PRINCIPLE B established): SPY-momentum-126d preserved bonus despite asset-axis match with G2; demonstrated TRIPLE-granularity distinctness.
- **iter 026 H6.4** (gate-source-distinctness +1pt KILL #102 at 4-way; QQQ-momentum-126d baseline at score 71). Iter 030 H10.4 surpassed by +1pt via asset-class-orthogonality; iter 032 tests if filter-type axis can extend ceiling further OR if 2/3-axis principle bounds the bonus.

If KILL #134 fires (max > 72) → architecture re-opens at filter-type × asset × lookback joint surface. If KILL #133 + (#135 or #136 or #137) fires → 16th meta-axis ceiling confirmation + Principle B refinement at filter-type granularity. If KILL #138 fires → operational guidance: at GLD source, lookback distinctness REQUIRED when filter-type matches existing constituents.

cumulative_n_trials = 120 → 124 with iter 032. Bonferroni 4.03e-04 maintained as long as worst p < 4.03e-04 (iter 031 worst was 6.55e-05 → 6.4× margin remaining; expected to remain similar).
