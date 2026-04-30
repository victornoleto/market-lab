# Iter 030 — H10 META-ENSEMBLE 4-WAY SIGNAL-ASSET AXIS at TSMOM-6m 4th constituent

**Date**: 2026-04-30
**Slug**: `H10-meta-ensemble-4way-signal-asset-axis`
**cumulative_n_trials before**: 112
**cumulative_n_trials after**: 116 (+4 configs)
**Iter type**: 14th iter at meta-axis — sub-axis (signal-asset variation, lookback fixed at 6m)

---

## Hypothesis

Iter 029 KILL #119 FIRED — established TSMOM-LOOKBACK INVERTED-U principle: for QQQ-TSMOM gate at 4th constituent slot, score-axis as a function of lookback-length follows an inverted-U with peak at ~6m. Generalization explicitly noted: "**lookback-peak-optimum may differ for other signal-asset combinations** (e.g., SPY-SMA peaks at 200d ≈ 10m per Faber; QQQ-TSMOM peaks at 6m due to higher volatility)."

Iter 030 directly tests the **signal-asset sub-axis** holding lookback constant at 6m — extending iter 026 KILL #102 NEW PRINCIPLE (gate-source-distinctness +1pt at 4-way) at finer granularity. Three signal-source variants:
- **QQQ-TSMOM-6m** (baseline, replicates iter 026 H6.4 → expected ≈ 71)
- **SPY-TSMOM-6m** (signal-source DUPLICATES G2's SPY-200d-SMA → expected score loss via gate-source-redundancy)
- **GLD-TSMOM-6m** (signal-source ORTHOGONAL to QQQ/SPY → expected gate-source-distinctness preserved or strengthened, but signal-sleeve mismatch risk on TQQQ-track sleeve)

This isolates the SIGNAL-ASSET axis from LOOKBACK axis (iter 029) and SLEEVE axis (iter 026 KILL #105). If H10 e1qqq baseline replicates iter 026 H6.4 score 71, AND H10 e1spy < 71 by ≥ 2pt → signal-source-distinctness PRINCIPLE confirmed at signal-asset granularity. If H10 e1gld > 71 → orthogonal Gold-trend source exceeds equity-source-only ceiling.

**Citation**:
- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction multi-alpha streams (4-way meta-ensemble 14th iter — signal-asset sub-axis exploration)
- **Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250** — TSMOM signal-asset robustness across equity/bond/commodity/FX markets
- `[ivy_portfolio]` Faber GTAA multi-asset 6-10m moving average (5-asset breadth: SPY+EFA+VWO+IEF+DBC; iter 030 tests 3 signal sources within meta-ensemble)
- `[asness_value_momentum]` momentum-everywhere across asset classes
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA (A2 + G2 baseline)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking (F1 stack always-on retained)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way)
- iter 029 KILL #119 (TSMOM-lookback inverted-U, signal-asset generalization)

---

## Configs (4)

All share constituents A2 (30%), G2 (25%), F1 (25%), with 4th constituent E1-variant (20% or 25%) varied by `signal_ticker` only. TSMOM lookback FIXED at 126 (~6m) per iter 029 KILL #119 peak finding. ON-sleeve identical to iter 026 H6.4 E1 (TQQQSIM 30 + QLDSIM 30 + KMLMSIM 30 + TLTSIM 10) holding sleeve constant — isolating signal-asset effect.

| config | 4th wt | 4th signal | rationale |
|---|---:|---|---|
| `h10_meta_4way_30a2_25g2_25f1_20e1qqq` | 0.20 | QQQSIM | BASELINE — replicates iter 026 H6.4 (expected ≈71) |
| `h10_meta_4way_30a2_25g2_25f1_20e1spy` | 0.20 | SPYSIM | SPY-source duplicates G2's SPY-200d (expected ≤69) |
| `h10_meta_4way_30a2_25g2_25f1_20e1gld` | 0.20 | GLDSIM | Gold-source ORTHOGONAL to equity (expected 70-71) |
| `h10_meta_4way_25a2_25g2_25f1_25e1gld` | 0.25 | GLDSIM | higher dose of Gold-orthogonal-signal variant |

---

## KILL conditions pre-committed

Numbered following iter 029's #120; iter 030 starts at #121.

- **KILL #121 (META-AXIS CEILING — 14th confirmation)**: if max H10 score ≤ 71 → 14th meta-axis confirmation (sequence 018→019→020→021→025→026→027→028→029→**030** = 70→71→67→70→70→71→70→69-selected/71-est→69→**?**); ceiling 71 across **10 sequential meta-axis iters** STRENGTHENED to high-high-confidence DEFINITIVE.

- **KILL #122 (META-AXIS CEILING — strong-form FALSIFICATION)**: if max H10 score > 72 strict → ceiling 71 FALSIFIED, signal-asset axis opens NEW above-ceiling architecture; would re-open hunt.

- **KILL #123 (SIGNAL-ASSET RUBRIC-NEUTRAL)**: if |H10.spy − H10.qqq| ≤ 1pt AND |H10.gld − H10.qqq| ≤ 1pt → signal-source IRRELEVANT for gate behavior at TSMOM-6m within meta-axis 4-way structure; signal-asset sub-axis is RUBRIC-NEUTRAL (8th class of RUBRIC SATURATION).

- **KILL #124 (SIGNAL-SOURCE-REDUNDANCY CONFIRMED)**: if H10.spy ≤ H10.qqq − 2pt → signal-source-distinctness PRINCIPLE CONFIRMED at signal-asset granularity: SPY-TSMOM-6m duplicates G2's SPY-200d-SMA → gate-source-redundancy → score loss. **Extension of iter 026 KILL #102** to finer-grain signal-asset axis.

- **KILL #125 (ORTHOGONAL-SOURCE BONUS)**: if H10.gld ≥ H10.qqq + 1pt → orthogonal Gold-trend signal ADDS gate-source-distinctness beyond equity-source ceiling; signal-asset diversification across asset classes (equity vs gold/commodity) yields measurable rubric bonus. Would FALSIFY KILL #119 generalization that "lookback-peak shifts but score-axis stays bounded".

- **KILL #126 (SIGNAL-SLEEVE COHERENCE FAIL)**: if H10.gld ≤ H10.qqq − 2pt → Gold-trend signal MISMATCHES TQQQ-stack sleeve (gold rallies during NASDAQ corrections — gate fires WHEN tech is OFF, but sleeve is leveraged tech), breaking gate-sleeve coherence; orthogonal signal counter-productive when sleeve is single-asset-class.

---

## Expected outcomes

| config | expected score | reasoning |
|---|---:|---|
| h10 e1qqq baseline | 71 | direct replication of iter 026 H6.4 |
| h10 e1spy | 69-70 | SPY signal duplicates G2 → gate-source redundancy −1 to −2pt |
| h10 e1gld 20% | 70-71 | Orthogonal source preserves +1pt distinctness; sleeve-coherence risk |
| h10 e1gld 25% | 69-70 | Higher dose magnifies sleeve-coherence risk if KILL #126 fires |

Highest expected score: 71 (no falsification). Most likely outcomes: KILL #121 FIRED + (KILL #123 OR KILL #124 OR KILL #126).

---

## Stress windows expected

Same 4 stress windows as prior iters (2008 GFC, 2020 COVID, 2022 inflation, 2000-02 dot-com). The signal-asset variation should differ in:

- **2008 GFC**: GLD rallied while equities crashed → GLD-TSMOM may KEEP gate ON (gold trending up) while QQQ-TSMOM goes OFF (NASDAQ trending down). H10.gld variants may STAY in TQQQ-stack during 2008 → catastrophic if KILL #126 fires.
- **2022 inflation**: GLD largely flat while equities/bonds collapsed → GLD-TSMOM ambiguous; QQQ-TSMOM clearly OFF.
- **2020 COVID**: brief but sharp; both signals likely OFF for ~2 months.
- **2000-02 dot-com**: gold rallied 2001-2003 (post-dot-com USD weakness); QQQ-TSMOM clearly OFF.

---

## INCOMPLETE flags

- **GLDSIM coverage**: 1986-01 to 2026-04, 10151 trading days — covers full lh_56y dataset. No coverage gap.
- **Gold-trend ↔ TQQQ-stack coupling**: assigning a Gold-trend signal to a Tech-LETF sleeve is a NON-OBVIOUS architectural choice; the empirical question is whether this gates-vs-sleeve mismatch helps (orthogonal diversification) or hurts (incoherence). KILL #126 pre-committed.
- **No new infra**: reuses 'blend' + 'lrs' (momentum filter with `signal_ticker` parameter varied) + 'static' spec types from iter 014/018-029. 771 tests baseline preserved.
- **DSR Bonferroni at n_trials=116**: threshold 0.05/116 = 4.31e-04. Worst per-config DSR p must be < 4.31e-04 to PASS Bonferroni; tighter than iter 029's 4.46e-04 by 0.15e-04 (3% margin reduction).
- **Tax classification**: meta-blend with TSMOM-gate constituent (lrs/momentum filter) → annual_realize. Drag expected ~2.0-2.1pp similar to iter 029 H9.1 (2.07pp).
- **Position-invariance** (iter 028 KILL #114): 4th-position weight 20% vs 25% is signal-rubric-neutral (orthogonal to permutation symmetry). Non-permutation weight changes still measurable.

---

## Prior-iter context

Direct parent: iter 026 H6.4 (4-way 30a2_25g2_25f1_20e1, E1 = QQQ-TSMOM-6m gate) score 71 = Pareto-co-apex CAGR-leaning variant. Iter 029 H9 added gate-LOOKBACK sub-axis (3m/12m vs 6m baseline → KILL #119 inverted-U peak at 6m). Iter 030 H10 adds gate-SIGNAL sub-axis (SPY/GLD vs QQQ baseline → KILL #121-#126).

If KILL #122 fires (max > 72) → architecture re-opens. If KILL #121 + (#123 or #124) fires → 14-axis architectural taxonomy COMPLETE with 8th class of RUBRIC SATURATION (signal-asset rubric-neutral OR signal-source-redundancy confirmed). Either outcome: hunt's empirical informational value continues at meta-principle level.

cumulative_n_trials = 112 → 116 with iter 030. Bonferroni 4.31e-04 maintained as long as worst p < 4.31e-04 (iter 029 worst was 2.31e-04 → 1.86× margin remaining).
