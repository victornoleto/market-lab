# spy_beater_hunt iter 020 — Final Report — `H3-meta-ensemble-4way-and-alt-3way-g1-ief`

**Gross tier**: **PROMISING** — `gross_score=67/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=62/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 13.95%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 26.17%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 12.15%)
- MDD bar: PASS (mean = 27.89%)
- Gates bar (same as gross): PASS

**Primary citation**: [advances_fin_ml, ch.16, p.241-256] portfolio construction over multiple alpha streams (4-way meta-ensemble at strategy-level) + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking generalized to 4-way strategy-level diversification + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate (A2 QQQ-track + G1/G2 SPY-track constituents — dual-SPY-gated test) + [ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in all 4 constituents) + Bridgewater All-Weather (Dalio 1996) F1 stack ON-state composition repeated in G1 IEF ON + [advances_fin_ml, p.31-34] factor framework — meta-ensemble axis 4-way structure depth probe + [advances_fin_ml, p.222-223] DSR cumulative_n_trials = 68 + [advances_fin_ml, p.208-211] PBO grid-level N=6 stability maintained per iter-019 KILL #64 resolution

---

## Selected config: `h3_meta_4way_25a2_25g1_25g2_25f1`

Spec:

```json
{
  "type": "blend",
  "constituents": [
    {
      "weight": 0.25,
      "spec": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {
          "TQQQSIM": 0.3,
          "QLDSIM": 0.3,
          "KMLMSIM": 0.3,
          "TLTSIM": 0.1
        },
        "off_weights": {
          "IEFSIM": 1.0
        },
        "signal_ticker": "QQQSIM",
        "lag_days": 1
      }
    },
    {
      "weight": 0.25,
      "spec": {
        "type": "lrs",
        "on_weights": {
          "NTSXSIM": 0.35,
          "GDESIM": 0.3,
          "TLTSIM": 0.2,
          "KMLMSIM": 0.15
        },
        "off_weights": {
          "IEFSIM": 1.0
        },
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "filter": "sma",
        "lag_days": 1
      }
    },
    {
      "weight": 0.25,
      "spec": {
        "type": "lrs",
        "on_weights": {
          "UPROSIM": 0.3,
          "TMFSIM": 0.25,
          "IEFSIM": 0.15,
          "UGLSIM": 0.15,
          "KMLMSIM": 0.15
        },
        "off_weights": {
          "IEFSIM": 1.0
        },
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "filter": "sma",
        "lag_days": 1
      }
    },
    {
      "weight": 0.25,
      "spec": {
        "type": "static",
        "weights": {
          "NTSXSIM": 0.35,
          "GDESIM": 0.3,
          "TLTSIM": 0.2,
          "KMLMSIM": 0.15
        }
      }
    }
  ]
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 1.045 | 14.31% | 26.17% | 0.918 | 12.48% | 27.89% | 1.83 | 6/7 |
| **spy_real** | 1.072 | 13.58% | 26.17% | 0.937 | 11.82% | 27.89% | 1.76 | 6/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $134,471 (terminal $2,350), drag 1.83pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $17,270 (terminal $0), drag 1.76pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| h3_meta_4way_25a2_25g1_25g2_25f1 | 1.045 | 1.072 |
| h3_meta_4way_30a2_20g1_25g2_25f1 | 1.022 | 1.052 |
| h3_meta_3way_33a2_33g1_34f1 | 1.014 | 1.045 |
| h3_meta_3way_50a2_25g1_25f1 | 0.926 | 0.957 |
| h3_meta_3way_33a2_33g1_34g2 | 0.989 | 1.002 |
| h3_meta_4way_35a2_15g1_25g2_25f1 | 0.999 | 1.031 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 18 | 30 | mean = 13.95%, bar = 11.21% |
| 2. MDD vs SPY | 15 | 20 | mean = 26.17%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 9.28e-05, n_trials = 68 |
| 5. Sharpe | 4 | 10 | mean = 1.058 |
| 6. Robustness | 7 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 55.6% | 26.17% |
| 10y | 69.2% | 26.17% |
| 15y | 75.0% | 26.17% |
| 20y | 100.0% | 26.17% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

- **PBO N=6 stability MAINTAINED**: lh_56y 0.044 (excellent) / spy_real 0.167
  (excellent) — both well below 0.5 strict threshold. Vs iter-019 N=6
  baseline (lh 0.0 / spy 0.0040) PBO marginally worsens but remains in
  comfortable strict-pass range. The 4-way structure adds a 4th constituent
  (G1 IEF) with similar gate signal (SPY-200d-SMA, same as G2 IEF) — slight
  PBO uptick consistent with reduced inter-constituent decorrelation gain
  vs iter-019's 3-way (where A2 QQQ-gate vs G2 SPY-gate was the only gate
  pair).
- **Cumulative n_trials = 68**, worst DSR p = 9.28e-05 << 0.05 — strong
  margin maintained despite +6 trials. iter-020 worst-p is *better* than
  iter-019's 1.55e-04 because 4-way Sharpe lift (1.058 vs 1.025) tightens
  per-dataset DSR stat.
- **Selected config gates 6/7 + 6/7 (margin of 1 on each ds)** — same as
  iter-019. Better than iter-018's thin 5/7 spy_real margin.
- **G3 walk-forward MDD bar at 25% — STILL FAILS** but BARELY: max wf_mdd
  25.37% lh_56y (0.37pp above bar) + 26.17% spy_real (1.17pp above bar).
  CLOSER to 25% bar than iter-019's 27.57%/28.50%. Adding G1 IEF (best
  walk-forward MDD constituent at 18.21% standalone) reduces aggregate
  wf_mdd but does not fully clear bar at 4-way 25/25/25/25 weights.
- **Identical lh_56y vs spy_real MDD (both 26.17%)**: 2008-09 GFC window
  dominates both datasets equally — same path-dependence artifact as
  iter-019. F1 stack always-on contributes its standalone 26.82% MDD AND
  the 3 gated constituents transition through 2008 in lockstep at the
  same window. Note: iter-020 4-way MDD (26.17%) is LOWER than iter-019
  3-way (28.50%) by 2.33pp because G1 IEF reduces the aggregate MDD via
  its 18.57% standalone profile.
- **Meta-ensemble combinatorial dimensions** (which 4 of 62 prior configs
  × what weight) NOT counted in DSR n_trials = 68. Honest n_trials likely
  larger; DSR margin is conservative-loose. Same caveat as iter 018/019.
- **Tax-layer drag 1.83pp lh / 1.76pp spy** — net score 62 vs gross 67
  (5pt drag). Net CAGR 12.15% still well above 11.21% bar; net MDD 27.89%
  / 27.89% well below 55.17% bar.
- **All assets DIRECT in testfolio cache**: TQQQSIM/QLDSIM/KMLMSIM/TLTSIM/
  IEFSIM/UPROSIM/TMFSIM/UGLSIM/SPYSIM/QQQSIM/NTSXSIM/GDESIM — all wired
  via long_term_portfolio.proxies + spy_beater_hunt.run_iter.
- **NO new infra**: reuses "blend" spec type from iter 018 (supports any
  number of constituents). 771 tests baseline preserved.
- **2-dataset framework**: lh_56y (40y synth) + spy_real (22.7y Tiingo
  daily). Methodology refactor 2026-04-29 unchanged.
- **lh_56y rolling = 0 windows**: rolling_metrics computes only on
  spy_real overlap; pass-rates from spy_real only (n=18/13/8/3 windows).
  5y/10y pass-rates 55.6%/69.2% reflect spy_real-only data — DROPPED vs
  iter-019's 83.3%/84.6% because adding G1 IEF (no-decay 1.41× stack)
  reduces 5y rolling CAGR via lower nominal mean than iter-019's
  G2 IEF (no-decay vs moderate-decay 2.25× LETF gives lower CAGR runway).

## Lesson

### Verdict summary

**Gross tier PROMISING 67/100** — `winner_conditions_met=True` for
ALL 6 configs (SECOND consecutive iter with 100% bar-pass sweep, vs
iter-019's first-ever 6/6 sweep). Selected `h3_meta_4way_25a2_25g1_25g2_25f1`
(4-way equal-weight blend) achieves **NEW BEST mean Sharpe 1.058** and
**NEW BEST mean MDD 26.17% among CAGR-passers** in entire spy_beater hunt
(20 iters / 68 cumulative trials), but the score **DROPS −4pts vs iter-019's
71** because the rubric-side CAGR loss (−2pts: 18 vs 20) and Robustness
loss (−2pts: 7 vs 9) are not offset by tied MDD/Sharpe pts (rubric anchors
near saturation in MDD bucket).

**Net tier PROMISING 62/100** — net-of-tax (Lei 14.754/2023, DARF 15%
annual) drag 1.79pp CAGR mean. Net score 62 BELOW iter-019's net 65 by
−3pts at meta-axis.

**KILL #66 (4-way ≤ 71 → meta-axis ceiling consolidates at 71) FIRED** —
max iter-020 score = 67 ≤ 71 AND no alt-3-way config exceeds 71. The
meta-ensemble axis ceiling is empirically established at **71** with
diminishing returns from additional structural complexity (4-way axis
adds Sharpe + MDD lift but does not break score-rubric ceiling).

**KILL #67 (best ≥ 75 → STRONG tier reachable) NOT FIRED** — score 67
<< 75. Tier STRONG remains 8pts above current iter-020 ceiling (4pts
below iter-019's 71). Meta-axis trajectory iter-018 → iter-019 → iter-020
(70 → 71 → 67) is **non-monotonic**: 3-way breaks 70-cap (+1pt), 4-way
DROPS −4pts. **The meta-axis Pareto frontier peaks at 3-way structure.**

**KILL #68 (alt 3-way with G1 IEF Pareto-dominates iter-019) NOT FIRED** —
`h3_meta_3way_33a2_33g1_34f1` (G1 IEF replaces G2 IEF) achieves Sharpe
1.029 + MDD 25.69% + CAGR 13.78% — Pareto-improvement on Sharpe (+0.004
vs iter-019) and MDD (−2.81pp) but CAGR LOSS (−1.26pp) is large enough
that score lands at ~66-67, NOT > 71. **Substituting G1 IEF for G2 IEF
in 3-way structure trades CAGR for Sharpe/MDD at 1:1 rate — Pareto-tied
within rubric, NOT Pareto-dominating.**

**KILL #69 (drop F1 stack → CAGR fails OR score < 70) PARTIAL FIRE** —
`h3_meta_3way_33a2_33g1_34g2` (no F1 stack, all-gated dual-LETF + 1×
stack) achieves CAGR 14.45% PASS bar (NOT failed), MDD 27.83%, Sharpe
0.996 → score ~67-68 < 70 (likely 67). **Dropping F1 stack does NOT fail
CAGR bar but score drops below iter-019's 71.** Confirms iter-019's
mechanism analysis: F1 stack always-on contributes structural CAGR-floor +
Sharpe lift via permanent multi-asset diversification, NOT just CAGR
runway. The −1pt Sharpe drop (1.025 → 0.996) and absence of always-on
diversifier reduces score by 4pts vs iter-019.

**KILL #70 (4-way Sharpe ≥ 1.05 → Sharpe Pareto frontier expands) FIRED** —
max 4-way Sharpe = 1.058 ≥ 1.05. Adding G1 IEF as 4th constituent lifts
Sharpe above iter-019's 1.025 by +0.033 (+3.2%). **Sharpe-axis Pareto
frontier expands at 4-way structure even though SCORE drops** (rubric
near-saturated for MDD/Sharpe buckets at iter-019 levels). Strengthens
mandate §7 rubric-revision review case.

### Pre-committed KILL outcomes

| KILL | name | trigger threshold | observed | result |
|---:|:---|:---|:---|:---:|
| #66 | 4-way ≤ 71 → meta-axis ceiling at 71 | max score ≤ 71 | 67 | **FIRED** |
| #67 | best ≥ 75 → STRONG tier reachable | max score ≥ 75 + bars 3/3 | 67 | **NOT FIRED** |
| #68 | alt 3-way with G1 IEF Pareto-dominates iter-019 | score > 71 + Sharpe > 1.025 | ~66-67 + 1.029 | **NOT FIRED** |
| #69 | drop F1 stack → CAGR fails OR score < 70 | h3.5 CAGR fails OR score < 70 | CAGR PASS, score ~67 | **PARTIAL FIRE** |
| #70 | 4-way Sharpe ≥ 1.05 | max 4-way Sharpe ≥ 1.05 | 1.058 | **FIRED** |

### Closest-to-winner (UNCHANGED)

**iter-019 `h2_meta_3way_33a2_33g2_34f1` REMAINS as closest-to-winner at
gross score 71.** iter-020 ceiling 67 < 71 → no displacement. iter-019's
33/33/34 (A2 + G2 IEF + F1 stack) STAYS as the apex of the meta-ensemble
axis Pareto frontier under spy_beater CAGR-anchored rubric.

Gap-by-criterion vs iter-019 (71 → 67):

| criterion | iter 019 (33/33/34 3way A2+G2+F1) | iter 020 (25/25/25/25 4way A2+G1+G2+F1) | Δ |
|---|---:|---:|---:|
| 1. CAGR vs SPY | 20 (mean 15.04%) | 18 (mean 13.95%) | **−2** |
| 2. MDD vs SPY | 15 (mean 28.50%) | 15 (mean 26.17%) | 0 |
| 3. Gates | 13 (6/7 + 6/7) | 13 (6/7 + 6/7) | 0 |
| 4. DSR | 10 | 10 | 0 |
| 5. Sharpe | 4 (mean 1.025) | 4 (mean 1.058) | 0 |
| 6. Robustness | 9 | 7 | **−2** |
| **TOTAL (gross)** | **71** | **67** | **−4** |

Net trade: **2 CAGR pts + 2 Robustness pts LOST** for **0 MDD pts + 0
Sharpe pts gained** (rubric near-saturated). The 4-way blend trades 1.09pp
CAGR + 27.7pp short-horizon robustness pass-rate for 2.33pp MDD relief +
0.033 Sharpe lift. Within rubric, **the trade is Pareto-tied on Sharpe/MDD
but Pareto-loss on CAGR/Robustness** because MDD/Sharpe buckets already
near-saturated at iter-019 levels.

### Comparison vs iter-019 3-way constituents (4-way structure adds G1 IEF)

| metric | iter 019 3way (A2+G2+F1) | iter 020 4way (A2+G1+G2+F1) | Δ |
|---|---:|---:|---:|
| Mean CAGR | 15.04% | 13.95% | **−1.09pp** |
| Mean MDD | 28.50% | 26.17% | **−2.33pp (better)** |
| Mean Sharpe | 1.025 | 1.058 | **+0.033 (better)** |
| Gates per ds | 6/7 + 6/7 | 6/7 + 6/7 | tied |
| Score | 71 | 67 | **−4** |
| 5y rolling pass-rate | 83.3% | 55.6% | **−27.7pp** |
| 10y rolling pass-rate | 84.6% | 69.2% | **−15.4pp** |
| 15y rolling pass-rate | 100.0% | 75.0% | **−25.0pp** |
| 20y rolling pass-rate | 100.0% | 100.0% | tied |

**Critical empirical findings**:

1. **4-way structure delivers NEW BEST Sharpe + MDD among CAGR-passers in
   entire 20-iter / 68-trial hunt** — Sharpe 1.058 (vs iter-019 1.025),
   MDD 26.17% (vs iter-019 28.50%, F1 stack 26.82%, G1 BLEND 19.77%
   no-CAGR-bar). G1 IEF as 4th constituent lifts both axes via best-in-hunt
   Sharpe 1.080 + best-in-hunt MDD 18.57% blended at 25% weight.
2. **Adding G1 IEF reduces CAGR aggregation by 1.09pp**, which directly
   maps to −2 CAGR pts in scoring rubric. G1 IEF's 10.34% standalone CAGR
   (FAILS bar alone) drags the blend below iter-019's 15.04%.
3. **Robustness DROPS dramatically at 4-way structure**: 5y pass-rate
   55.6% vs iter-019's 83.3% (−27.7pp). G1 IEF's no-decay 1.41× stack has
   lower CAGR runway than G2 IEF's moderate-decay 2.25× LETF in 5y rolling
   windows; 4-way blend inherits this short-horizon CAGR-volatility.
4. **G3 walk-forward MAX wf_mdd CLOSER to 25% bar but STILL FAILS**: lh
   25.37% (vs iter-019 27.57%, −2.20pp), spy 26.17% (vs iter-019 28.50%,
   −2.33pp). G1 IEF's no-decay sleeve reduces aggregate wf_mdd but not
   enough to clear bar.

### Why H3.1 (4-way 25/25/25/25) WINS over alternatives within iter-020

| config | mean CAGR | mean MDD | mean Sharpe | est gross score |
|:---|---:|---:|---:|---:|
| h3_meta_4way_25a2_25g1_25g2_25f1 | 13.95% | 26.17% | 1.058 | **67** (selected) |
| h3_meta_4way_30a2_20g1_25g2_25f1 | 14.35% | 27.07% | 1.037 | est 67-68 |
| h3_meta_3way_33a2_33g1_34f1 | 13.78% | 25.69% | 1.029 | est 66-67 |
| h3_meta_3way_50a2_25g1_25f1 | 14.88% | 32.44% | 0.941 | est 67-69 |
| h3_meta_3way_33a2_33g1_34g2 | 14.45% | 27.83% | 0.996 | est 67-68 |
| h3_meta_4way_35a2_15g1_25g2_25f1 | 14.74% | 28.06% | 1.015 | est 68-69 |

- Selection rule (max mean Sharpe / SPY_Sharpe across datasets) chose
  4-way 25/25/25/25 (Sharpe 1.058 highest).
- All 6 configs cluster at score 66-69 — **the 71 ceiling holds; iter-020
  meta-axis ceiling is at 67-69, BELOW iter-019's 71.**
- A2-tilted 4-way (H3.6 35/15/25/25) has higher CAGR 14.74% but lower
  Sharpe 1.015 — Pareto-trade not Pareto-improve.
- Alt 3-way with G1 IEF (H3.3 33/33/34) has best MDD 25.69% but CAGR
  drops 1.26pp vs iter-019 → score 66-67 < 71.
- All-gated 3-way without F1 stack (H3.5 33/33/34) has CAGR 14.45% PASS
  but Sharpe 0.996 (loses always-on diversifier benefit) → score 67-68
  < 71.

### Mechanism: why 4-way DROPS −4pts vs 3-way

**Pre-iter expectation** (hypothesis.md realistic case): 4-way scores
69-72 with G1 IEF lifting Sharpe + MDD. **Observed**: 67 — below realistic
case, matches "pessimistic" lower bound (67-71 range).

**Why CAGR drops 1.09pp at 4-way vs 3-way**:
- A2 weight reduces 33% → 25% (−8pp absolute weight on highest-CAGR
  constituent at 17.33%), losing 8% × 17.33% = 1.39pp expected aggregate
  CAGR contribution.
- G1 IEF added at 25% weight, contributing 25% × 10.34% = 2.59pp expected
  aggregate CAGR.
- F1 stack reduces 34% → 25% (−9pp absolute), losing 9% × 11.95% = 1.08pp.
- G2 IEF unchanged 33% → 25% (−8pp), losing 8% × 14.02% = 1.12pp.
- Net expected linear CAGR: +2.59 − 1.39 − 1.08 − 1.12 = **−1.0pp** —
  CLOSE to observed −1.09pp.

**Why Sharpe lifts +0.033 at 4-way**:
- G1 IEF Sharpe 1.080 at 25% weight × decorrelation gain.
- Linear expected: (0.804 + 1.080 + 0.970 + 1.018) / 4 = 0.968.
- Observed: 1.058 = +0.090 vs linear (+9.3% super-linear gain).
- Compare iter-019 3-way: linear 0.931 → observed 1.025 = +0.094 vs
  linear (+10.1%). **Super-linear decorrelation gain at 4-way is similar
  to 3-way (~10%) but base linear-mean is higher (0.968 vs 0.931) →
  observed Sharpe higher (1.058 vs 1.025).**

**Why Robustness drops 2pts**:
- 5y pass-rate 55.6% vs iter-019's 83.3% (−27.7pp, scoring impact
  3 → 1.7 ≈ 2 points lost).
- G1 IEF's no-decay 1.41× stack has lower 5y CAGR runway than G2 IEF's
  2.25× LETF; 4-way inherits this short-horizon CAGR-volatility.
- 10y pass-rate 69.2% vs 84.6% (−15.4pp); 15y 75% vs 100% (−25pp).
- Long-horizon (20y) tied at 100% — leverage compensates over decade-
  scale windows.

**Why MDD doesn't gain pts**: rubric anchor [0.7, 0.15] gives 26.17% →
20×(0.7−0.262)/0.55 = 15.94 → 15 pts (rounded down). iter-019's 28.50%
→ 20×(0.7−0.285)/0.55 = 15.09 → 15 pts. Both bucket at 15. The 2.33pp
absolute MDD lift is **invisible to the rubric** because both fall in
the same point bucket.

**Why Sharpe doesn't gain pts**: rubric anchor [0.5, 2.0] gives 1.058 →
10×(1.058−0.5)/1.5 = 3.72 → 4 pts. iter-019's 1.025 → 10×(0.525)/1.5 =
3.50 → 4 pts. Both bucket at 4. The 0.033 absolute Sharpe lift is
**invisible to the rubric** at this anchor range.

**The 4-way trade is Pareto-improved on Sharpe + MDD axes empirically
but Pareto-tied within scoring rubric** (anchors near saturation at the
iter-019 level). This documents a clear case of **rubric saturation**:
the meta-axis Pareto frontier extends further than the rubric measures.

### Architectural taxonomy diagnostic (UPDATED — 8 fams + 3 hybrids + 3-axis meta)

| family | best gross score | best Sharpe | best mean MDD |
|:---|---:|---:|---:|
| META-ENSEMBLE 3-WAY (iter 019) | **71** ⬅ STILL BEST | 1.025 | 28.50% |
| META-ENSEMBLE 4-WAY (NEW iter 020) | **67** ⬅ DROPS −4 | **1.058** ⬅ NEW BEST CAGR-passer | **26.17%** ⬅ NEW BEST CAGR-passer |
| META-ENSEMBLE 2-WAY (iter 018) | 70 | 0.933 | 34.83% |
| A2 TQQQ-track LRS (iter 006) | 67 | 0.804 | 49.73% |
| A1/A3 SPY-track LRS | 66 | 0.744 | 51.60% |
| E1 hybrid (TSMOM × A2 at 3× LETF) | 65 | 0.746 | 47.48% |
| G2 hybrid (SMA × F1 LETF at 2.25×) | 64 | 0.970 | 26.76% (G2 blend) |
| B1/B2 HFEA barbell | 63 | 0.739 | 67.48% |
| F1 Levered All-Weather (iter 015) | 61 | 1.018 | 26.82% |
| G1 hybrid (SMA × F1 stack at 1.41×) | 61 | **1.080** ⬅ STILL BEST OVERALL | **18.57%** ⬅ STILL BEST OVERALL |
| C1 vol-target | 60 | 0.721 | 41.86% |
| D1 concentrated+TSMOM (1×) | 59 | 0.779 | 35.27% |
| D2 stacked equity | 52 | 0.738 | 52.65% |

**The architectural ceiling claim (KILL #33) was REJECTED at meta-portfolio
axis at iter-018 + iter-019**; iter-020 EMPIRICALLY ESTABLISHES the
meta-axis ceiling at **71 within spy_beater rubric**. The trajectory
iter-018 → 019 → 020 (70 → 71 → 67) is non-monotonic; 3-way structure is
the local optimum. The Pareto frontier on Sharpe + MDD axes extends
further at 4-way (1.058 + 26.17%) but **the rubric is saturated** in
those buckets at iter-019's level.

### Statistical integrity (caveats)

- **Cumulative n_trials**: 62 → 68. DSR worst p = 9.28e-05 << 0.05.
  Strong margin maintained despite +6 trials; iter-020 worst-p tighter
  than iter-019's 1.55e-04 because Sharpe lift tightens stat.
- **PBO grid-level (N=6)**: lh_56y 0.044 (excellent); spy_real 0.167
  (excellent). Slightly worse than iter-019's 0.0 / 0.0040 — adding a
  second SPY-gated constituent (G1 IEF, dual-SPY-gate with G2 IEF) reduces
  inter-constituent gate-decorrelation gain; PBO uptick consistent with
  reduced 4-way decorrelation efficiency vs 3-way's QQQ × SPY × always-on
  triplet.
- **G3 walk-forward STILL FAILS 25% threshold** by 0.37pp on lh_56y
  (max wf_mdd 25.37%) and 1.17pp on spy_real (26.17%). CLOSER to bar than
  iter-019 by 2.20pp/2.33pp but still single worst window above bar.
- **Selected config gates 6/7 + 6/7** — same as iter-019.
- **G6 bootstrap CI low**: lh_56y 0.625, spy_real 0.350. Both COMFORTABLY
  > 0 (better than iter-019's 0.589 / 0.319). Sharpe lift translates to
  bootstrap CI lift.
- **G7 cross-lib ±3pp CAGR**: 0.0pp delta. Engine consistency excellent.

### Surprising findings

1. **4-way DROPS −4pts vs 3-way at meta-axis** — the meta-ensemble axis
   trajectory iter-018 → 019 → 020 is **non-monotonic**: 67 → 70 → 71 →
   67. 3-way 33/33/34 is the local optimum within spy_beater CAGR-anchored
   rubric. KILL #66 fires; meta-axis ceiling consolidates at 71.
2. **Sharpe + MDD axes Pareto-improve at 4-way but rubric is saturated** —
   1.058 Sharpe and 26.17% MDD are NEW BESTS for CAGR-passers but bucket
   at same rubric points as iter-019. The empirical Pareto frontier
   extends further than the rubric measures.
3. **G1 IEF substitution for G2 IEF in 3-way (H3.3) Pareto-trades CAGR
   for MDD/Sharpe at 1:1 — score lands at 66-67, NOT > 71**. Confirms
   iter-019's G2 IEF choice was rubric-optimal at 3-way structure even
   though G1 IEF has better solo Sharpe + MDD profile.
4. **Dropping F1 stack (H3.5 all-gated) does NOT fail CAGR bar** — CAGR
   14.45% PASSES, but score drops to ~67-68 < 71. F1 stack always-on
   contributes Sharpe lift via permanent multi-asset diversification, NOT
   just CAGR floor; removing it costs rubric pts via Sharpe drop.
5. **PBO N=6 marginally worse at 4-way (0.167 spy)** vs iter-019 N=6
   (0.0040 spy) — adding 4th constituent with same gate signal (SPY
   200d-SMA) as G2 IEF reduces gate-decorrelation efficiency. Suggests
   the 3-way's 3 distinct decorrelation sources (QQQ-gate × SPY-gate ×
   always-on) is the architectural sweet spot.
6. **6/6 configs PASS all 3 bars (SECOND consecutive iter)** — iter-019's
   first-ever 6/6 sweep is reproducible at iter-020 within meta-axis.
   Bar-passing region at 4-way structure is robust to weight perturbations.
7. **Robustness drops dramatically at 4-way** — 5y pass-rate 55.6% vs
   iter-019's 83.3% (−27.7pp). Adding G1 IEF (no-decay 1.41× stack)
   reduces short-horizon CAGR-runway vs iter-019's G2 IEF (moderate-decay
   2.25× LETF). The leverage-axis shift from 2.25× to 1.41× sleeve in
   G1 IEF degrades short-horizon SPY-beating ability.

### Direction implications

**META-ENSEMBLE 4-WAY family — CLOSED at gross score 67** (KILL #66
fired). The meta-axis ceiling consolidates at 71 (iter-019's 3-way
33/33/34) with empirical evidence that 4-way structure does NOT extend
the score-rubric Pareto frontier. iter-021+ exploration on 4-way axis
NOT recommended within spy_beater rubric.

**META-ENSEMBLE 3-WAY family — STILL OPEN at score 71** (iter-019's
ceiling preserved). The meta-axis Pareto frontier within rubric is at
3-way structure with constituent triplet (gate-A × gate-B × always-on)
and equal-weight 33/33/34. iter-021+ could explore:
- (a) Different always-on diversifier instead of F1 stack — e.g., F1 LETF
  2.25× (iter 017 G2 sleeve standalone) as 34% weight. Higher CAGR runway
  + similar diversification.
- (b) Asymmetric 3-way weights at narrower granularity (32/34/34, 30/35/35,
  etc.) to map the local optimum surface around 33/33/34.
- (c) Triple-gate 3-way with NO always-on constituent: A2 + G1 IEF + G2 IEF
  (already tested partially via H3.5; 14.45% CAGR but score < 71 confirms
  always-on contribution).

**Path to STRONG (≥75) at meta-axis**:
- iter-019's 71 + 4pts needed. Most plausible via Sharpe → 7pts (need
  mean Sharpe ≥ 1.4) OR Gates → 14pts (need 7/7 on at least one ds).
- 4-way at iter-020 lifted Sharpe to 1.058 but rubric awarded same 4pts.
  Need Sharpe ≥ 1.25 to bucket at 5pts (10×(1.25−0.5)/1.5 = 5).
- Realistic ceiling 72-73 via further 3-way weight optimization +
  alternative always-on constituent. STRONG MIGHT be reachable; WINNER
  (≥90) still architecturally out of reach within rubric.

**Path to WINNER (≥90) at meta-axis**: still architecturally out of
reach. iter-020's 4-way confirms: improving Sharpe/MDD beyond iter-019's
levels yields ZERO rubric pts at current anchors; CAGR is the binding
score-axis. Any meta-axis WINNER would require Sharpe ≥ 1.7 (from current
1.058, +0.6) OR CAGR ≥ 18% (from current 13.95%, +4pp). Both require
constituent-level architectural changes not currently available in
8-fam + 3-hybrid surface.

### Why this iter STRENGTHENS the rubric-revision review case

iter-020's 4-way 25/25/25/25 achieves NEW BEST Sharpe 1.058 + NEW BEST MDD
26.17% among CAGR-passers — under MDD-anchored or Sharpe-anchored rubric,
this would be the top-1 strategy in entire spy_beater hunt that ALSO
passes CAGR bar. The CAGR-anchored rubric:
- Fails to award rubric pts for the Sharpe lift (1.025 → 1.058) and MDD
  lift (28.50% → 26.17%) because anchors are saturated at iter-019 level.
- Awards iter-019's 71 because of CAGR 15.04% advantage (+1.09pp vs
  iter-020's 13.95%).

If user accepts CAGR floor of 14% (still 2.74pp above 11.21% bar) in
exchange for Sharpe ≥ 1.05 + MDD ≤ 27%, iter-020 selected 4-way 25/25/25/25
is a STRONG deploy candidate vs F1+SPLIT (CAGR 10.76%, MDD 16.76%, fails
13.80% original CAGR bar).

This is the FOURTH iter (after 015 F1 stand-alone, 016 G1 IEF, 018+019
meta-ensembles) to exhibit the pattern: rubric-suboptimal config with
strong Sharpe/MDD profile and >11.21% CAGR floor.

### Suggested iter 021+

Hunt status: meta-ensemble axis ceiling **EMPIRICALLY ESTABLISHED at 71**
within spy_beater rubric. The 3-way 33/33/34 (A2 + G2 IEF + F1 stack) at
iter-019 is the Pareto apex.

**Recommended iter 021** (if user authorizes continuation):
- 6 configs maintaining N=6 PBO stability.
- Test alternative always-on constituents in 3-way structure:
  - C₀ = F1 LETF 2.25× (iter 017 G2 sleeve standalone) at 34% weight
  - C₁ = F1 stack 2× variant (NTSX 50% + GDE 30% + KMLM 20%, no TLT)
  - C₂ = pure NTSX 100% as always-on (highest CAGR runway)
- Asymmetric 3-way weights: 30/35/35 (G2-heavy), 35/30/35 (F1-heavy),
  30/40/30 (G2-tilted), 35/35/30 (gates-heavier).
- Cumulative n_trials: 68 + 6 = 74.
- Pre-commit KILL: if iter-021 max score ≤ 71, the meta-axis ceiling
  is **definitive at 71** with no further exploration value within
  spy_beater rubric.

**However**: per CLAUDE.md mandate §1 + §7, iter-020 does NOT alter the
deploy decision. Score 67 < 90 WINNER threshold. F1+SPLIT incumbent
fallback retains deploy-ready status. Mandate §1 100% Plano C UNCHANGED.
iter-021+ exploration is RESEARCH ONLY.

**Alternative strategic pivot**: hunt budget shows 30 iters remaining
(20/50 used). Given meta-axis ceiling at 71 and architectural ceiling
at 67 single-axis, further iters within current architecture may yield
≤ 1pt gains. **Strategic option**: declare hunt EFFECTIVELY-CLOSED at
iter-020 with score 71 as ceiling, document IMPOSSIBILITY_RESULT-light,
F1+SPLIT confirmed deploy fallback. User decision needed.

### Citations

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over
  multiple alpha streams — 4-way meta-ensemble axis EMPIRICALLY TESTED;
  decorrelation gain on Sharpe (+0.090 super-linear, ~10%) consistent
  with iter-019's 3-way (+0.094, ~10%); base linear-mean lift (0.931
  → 0.968 with G1 IEF added) drives observed Sharpe 1.058 vs iter-019
  1.025. **CAGR axis: 4-way Pareto-loss confirms diminishing returns
  beyond 3-way structure within CAGR-anchored rubric.**
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking
  generalized to 4-way strategy-level: blending gated LETFs (A2 + G2 IEF)
  + gated stack (G1 IEF) + always-on stack (F1 stack) at equal-weight
  delivers Sharpe + MDD Pareto-improvement empirically but NOT in scoring
  rubric (anchor saturation).
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA gate
  at 4-way meta-ensemble: dual-SPY-gated (G1 IEF + G2 IEF) reduces
  inter-constituent gate-decorrelation efficiency vs iter-019's
  QQQ-vs-SPY decorrelation. Empirical evidence that **gate-source
  diversity > gate-recurrence at meta-axis**.
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM) — present in
  all 4 constituents (A2 30% ON, G1 IEF 15% ON, G2 IEF 15% ON, F1 stack
  15%). Crisis-alpha redundancy at 4-way may dilute signal vs iter-019's
  3-way KMLM dose pattern.
- Bridgewater All-Weather (Dalio 1996) — F1 stack ON-state composition
  doubled at G1 IEF ON-state (same NTSX/GDE/TLT/KMLM weights). 4-way
  blend has 50% gross weight allocated to All-Weather-derived
  constituents (G1 IEF 25% + F1 stack 25%) — concentration risk in
  All-Weather thesis.
- `[advances_fin_ml, p.31-34]` factor framework — 4-way meta-ensemble
  axis added to architectural taxonomy. Hunt's formal taxonomy now spans:
  8 single-axis families + 3 cross-product hybrids + 3-axis meta-ensemble
  (2-way iter-018 + 3-way iter-019 + 4-way iter-020). **Empirical evidence
  that meta-axis Pareto frontier within spy_beater rubric peaks at 3-way
  structure with diminishing returns at 4-way.**
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 68, worst
  p = 9.28e-05. Strong margin maintained.
- `[advances_fin_ml, p.208-211]` PBO grid-level — N=6 stability MAINTAINED:
  lh 0.044 / spy 0.167 (vs iter-019 N=6 lh 0.0 / spy 0.0040). Slight
  uptick consistent with reduced 4-way gate-decorrelation efficiency.
- `[advances_fin_ml, p.196-202]` bootstrap CI — G6 passed comfortably on
  both datasets (lh 0.625, spy 0.350). Sharpe lift translates to bootstrap
  CI lift.
- Lei 14.754/2023 (DARF 15% annual) — net-of-tax drag 1.79pp; net score
  62 vs gross 67. Net total_score below iter-019 net 65 by −3pts at
  meta-axis.
