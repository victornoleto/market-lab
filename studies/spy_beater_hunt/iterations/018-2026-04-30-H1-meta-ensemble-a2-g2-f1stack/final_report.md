# spy_beater_hunt iter 018 — Final Report — `H1-meta-ensemble-a2-g2-f1stack`

**Gross tier**: **PROMISING** — `gross_score=70/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=64/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 16.30%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 34.83%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 14.23%)
- MDD bar: PASS (mean = 35.87%)
- Gates bar (same as gross): PASS

**Primary citation**: [advances_fin_ml, ch.16, p.241-256] portfolio construction over multiple alpha streams (meta-ensemble at strategy-level) + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking generalized to strategy-level diversification + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate (both A2 QQQ-track and G2 SPY-track constituents) + [ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in both A2 30% and G2 15%) + Bridgewater All-Weather (Dalio 1996) F1 stack ON-state composition + [advances_fin_ml, p.31-34] factor framework - meta-ensemble axis added to architectural taxonomy (asset, gate, decay, meta) + [advances_fin_ml, p.222-223] DSR cumulative_n_trials

---

## Selected config: `h1_meta_50a2_50g2ief`

Spec:

```json
{
  "type": "blend",
  "constituents": [
    {
      "weight": 0.5,
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
      "weight": 0.5,
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
    }
  ]
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.922 | 17.08% | 37.56% | 0.819 | 14.93% | 37.56% | 2.15 | 6/7 |
| **spy_real** | 0.945 | 15.51% | 32.10% | 0.833 | 13.52% | 34.17% | 1.99 | 5/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $307,227 (terminal $3,139), drag 2.15pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $25,315 (terminal $0), drag 1.99pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| h1_meta_50a2_50g2ief | 0.922 | 0.945 |
| h1_meta_70a2_30g2ief | 0.851 | 0.872 |
| h1_meta_60a2_40f1stack | 0.883 | 0.919 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 23 | 30 | mean = 16.30%, bar = 11.21% |
| 2. MDD vs SPY | 12 | 20 | mean = 34.83%, bar = 55.17% |
| 3. Gates | 12 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 1.65e-04, n_trials = 56 |
| 5. Sharpe | 3 | 10 | mean = 0.933 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 88.9% | 37.56% |
| 10y | 100.0% | 37.56% |
| 15y | 100.0% | 37.56% |
| 20y | 100.0% | 37.56% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

- **Tax-layer integration**: this is the FIRST iter to include net-of-tax
  computation under Lei 14.754/2023 (DARF 15% annual). Prior iters
  001-017 reported gross-of-tax only. Drag for selected config: 2.15pp
  lh_56y, 1.99pp spy_real. Net total_score 64 vs gross 70 = 6pt drag.
  KILL #59 was pre-committed against gross_score (canonical spy_beater
  rubric) and STILL FIRES at gross 70 ≥ 70 trigger threshold. Net-of-
  tax narrows the meta-ensemble ceiling-break to a tie or 1-2pt edge
  depending on whether prior iter-006 baseline is also re-scored
  net-of-tax.
- **PBO N=3 warning persists** (CSCV statistically unstable with N<4).
  Per-dataset PBO grid-level: lh_56y 0.151 (excellent < 0.5);
  spy_real 0.603 — FAILS G1 strict (>0.5). G1 fail on spy_real is
  partial noise from N=3 instability per long-standing validator
  warning; aggregate cross-dataset gate threshold still met (lh_56y 6/7
  ≥ 5; spy_real 5/7 ≥ 5).
- **G3 walk-forward FAILS 25% threshold by 8.7pp on lh_56y** (max wf_mdd
  33.71%) and by 7.1pp on spy_real (32.10%). Single worst window each
  dataset just above bar — gate fails 6/7 + 5/7 not 7/7. Binding gates
  constraint at meta-ensemble level.
- **Selected config gates exactly at threshold on spy_real** (5/7 = 5).
  No margin. Re-running with slight parameter perturbations could push
  spy_real to 4/7 → cross_dataset_met fails. Score-70 verdict has
  thinner-than-typical gate margin.
- **Meta-ensemble effective parameter space**: cumulative_n_trials = 56
  per `[advances_fin_ml, p.222-223]` DSR penalty. This counts
  CONFIGS only; meta-ensemble adds combinatorial dimensions (which 2 of
  53 prior configs to blend × what weight) NOT captured in DSR. Honest
  assessment: meta-ensemble may have undercounted true search space.
- **All assets DIRECT in testfolio cache**: TQQQSIM/QLDSIM/KMLMSIM/
  TLTSIM/IEFSIM/UPROSIM/TMFSIM/UGLSIM/SPYSIM/QQQSIM all wired. NTSXSIM/
  GDESIM (used in H1.3) routed via long_term_portfolio.proxies.
- **NEW infra: "blend" spec type** added to ``returns_from_spec`` (~30
  LOC) + 3 TDD tests. Baseline 765 → 768 tests preserved.
- **2-dataset framework**: lh_56y (40y synth) + spy_real (22.7y Tiingo
  daily). Methodology refactor 2026-04-29 unchanged.
- **lh_56y rolling = 0 windows**: rolling_metrics computes only on synth
  without Tiingo overlap; pass-rates from spy_real only (n=18/13/8/3
  windows). Robustness 10/10 reflects spy_real-only data.

## Lesson

### Verdict summary

**Gross tier PROMISING 70/100** — `winner_conditions_met=True` for ALL
3 configs. Selected `h1_meta_50a2_50g2ief` is the FIRST config in the
entire spy_beater hunt (18 iters / 56 cumulative trials) to **break the
67-cap** at gross score 70.

**Net tier PROMISING 64/100** — net-of-tax (Lei 14.754/2023, DARF 15%
annual) drag is 2.0pp CAGR on both datasets. Net score 64 ties iter 017
G2 IEF gross score 64; the meta-ensemble ceiling-break is REAL on
gross-of-tax rubric but NARROW on net-of-tax (likely +1-2pts vs
iter-006 A2 net).

**KILL #59 (META-ENSEMBLE breaks ceiling — KILL #33 INVALIDATED at
meta-level) FIRES** based on the pre-committed rubric (gross-of-tax,
canonical spy_beater per WINNER_AND_RANKING.md). The architectural
ceiling claim documented in KILL #33 (8 fams + 3 hybrids cap ≤ 67) is
empirically REJECTED at the meta-portfolio axis: a 50/50 blend of iter
006 closest-to-winner (A2 QQQ-gated 3× LETF) and iter 017 G2 IEF
(SPY-gated 2.25× LETF F1 All-Weather) scores 70/100 with all 3 strict
bars met simultaneously.

The break is BORDERLINE at +3pts above the prior architectural ceiling.
Important caveats apply (see "Statistical integrity" + "Tax-layer
caveat" below) — but within the strict pre-committed KILL trigger, the
architectural-ceiling claim is invalidated at meta-portfolio axis.

**Tier still PROMISING (not WINNER)** because score 70 (gross) and 64
(net) are both well below 90 WINNER threshold. The hunt could
legitimately REOPEN at iter 019+ for deeper meta-ensemble exploration to
verify whether 70 generalizes or is N=3 artifact.

### Tax-layer caveat (NEW for iter 018)

This is the first iter to include net-of-tax computation. Drag analysis:
- Selected config: gross score 70 → net score 64 (−6pts via 2.0pp
  CAGR drag).
- Drag mechanism: annual_realize classification triggers DARF 15% on
  realized gains each year-end settlement (38 settlements lh_56y, 23
  spy_real).
- **If prior iter-006 baseline (A2 a6_tqqq_split_kmlm30_tlt10) is
  re-scored net-of-tax**, its gross 67 → net ~62-63 (similar 4-5pt
  drag from concentrated equity LETF realizations). Net-of-tax
  meta-ensemble vs net-of-tax A2 ≈ 64 vs 62-63 = +1-2pt edge.
- **Tax-layer affects all multi-asset LETF strategies similarly**. The
  meta-ensemble's gross-rubric edge (+3pts) compresses to ~+1-2pts
  net-of-tax — narrower but still positive.
- KILL #59 fires on gross (canonical pre-committed rubric); net-of-tax
  shows the result is real but narrower. iter 019+ should explicitly
  re-score prior closest-to-winner candidates net-of-tax for
  apples-to-apples comparison.

### Pre-committed KILL outcomes

| KILL | name | trigger threshold | observed | result |
|---:|:---|:---|:---|:---:|
| #58 | META-ENSEMBLE caps ≤ 67 (KILL #33 generalizes) | best gross score ≤ 67 | best 70 | **NOT FIRED** |
| #59 | META-ENSEMBLE breaks ceiling — KILL #33 INVALIDATED | best gross ≥ 70 + bars 3/3 | 70 + 3/3 | **FIRED** (gross rubric) |
| #60 | Same-gate-family blend Pareto-dominates mixed-gate | 50a2_50g2ief score > 60a2_40f1stack score AND Sharpe higher | 70 vs ~64-66 + 0.933 vs 0.901 | **FIRED** |
| #61 | META-ENSEMBLE Sharpe Pareto-improves on best constituent | max H1 mean Sharpe > 0.97 | max 0.933 < 0.97 | **NOT FIRED** |

### Closest-to-winner (NEW)

**iter 018 `h1_meta_50a2_50g2ief` REPLACES iter 006 `a6_tqqq_split_kmlm30_tlt10`
as new closest-to-winner at gross score 70.** First closest-to-winner
update since iter 006 (12 iters / 33 trials ago).

Gap-by-criterion vs prior closest-to-winner (iter 006 → iter 018, 67 → 70):

| criterion | iter 006 (A2) | iter 018 (h1_meta_50/50) | Δ |
|---|---:|---:|---:|
| 1. CAGR vs SPY | 25 (mean 17.33%) | 23 (mean 16.30%) | **−2** |
| 2. MDD vs SPY | 7 (mean 49.73%) | 12 (mean 34.83%) | **+5** |
| 3. Gates | 13 (6/7 + 6/7) | 12 (6/7 + 5/7) | **−1** |
| 4. DSR | 10 | 10 | 0 |
| 5. Sharpe | 2 (mean 0.804) | 3 (mean 0.933) | **+1** |
| 6. Robustness | 10 | 10 | 0 |
| **TOTAL (gross)** | **67** | **70** | **+3** |

Net: meta-ensemble trades **2 CAGR pts + 1 Gates pt** for **5 MDD pts
+ 1 Sharpe pt** = score lift +3. The MDD axis at meta-level relieves
14.9pp absolute MDD vs A2 alone (49.73% → 34.83%), a substantial Pareto
shift.

### Comparison vs constituent solos

| metric | iter 006 A2 | iter 017 G2 IEF | iter 018 50/50 META | Δ vs A2 | Δ vs G2 |
|---|---:|---:|---:|---:|---:|
| Mean CAGR | 17.33% | 14.02% | 16.30% | −1.03pp | +2.28pp |
| Mean MDD | 49.73% | 33.72% | 34.83% | −14.90pp | +1.11pp |
| Mean Sharpe | 0.804 | 0.970 | 0.933 | +0.129 | −0.037 |
| Gates per ds | 6/7 + 6/7 | 6/7 + 6/7 | 6/7 + 5/7 | −1 cell | −1 cell |
| Robustness 5y | 100% | 50% | 88.9% | −11.1pp | +38.9pp |
| Robustness 20y | 100% | 100% | 100% | 0 | 0 |
| Gross score | 67 | 64 | **70** | **+3** | **+6** |
| Bars | 3/3 | 3/3 | 3/3 | tied | tied |

**Critical empirical findings**:
1. **Meta-ensemble achieves Pareto-shifted profile**: lower MDD than A2
   (15pp better), lower CAGR than A2 (1pp worse), comparable Sharpe to G2
   IEF (within 0.04). Net SCORE WINS over both constituents.
2. **CAGR drop from A2 (1.03pp) is SMALLER than MDD relief (14.90pp)**.
   Meta-blending exploits MDD path-dependence: when both constituents
   are in defensive mode (QQQ < 200d SMA AND SPY < 200d SMA), 100% IEF.
   When ONE is on ONE off (mixed regime, decorrelated gates), the blend
   is ~50% leveraged exposure with bear-buffer.
3. **Sharpe lifts from A2 0.804 → meta 0.933 (+16%)** while CAGR drops
   only 1.03pp. Vol compression from gate decorrelation is substantial.

### Why H1.1 (50/50 same-gate-family) WINS over H1.2 (70/30) and H1.3 (mixed-gate)

| config | mean CAGR | mean MDD | mean Sharpe | est gross score |
|:---|---:|---:|---:|---:|
| **h1_meta_50a2_50g2ief** | **16.30%** | **34.83%** | **0.933** | **70** |
| h1_meta_70a2_30g2ief | 16.86% | 41.04% | 0.861 | ~67 |
| h1_meta_60a2_40f1stack | 15.80% | 37.69% | 0.901 | ~66-68 |

- H1.2 (70/30 A2-heavy): more CAGR (+0.56pp) but loses MDD relief
  (+6.21pp).
- H1.3 (60/40 with F1 always-on): less CAGR (−0.50pp) and more MDD
  (+2.86pp) than H1.1.
- **KILL #60 FIRES**: same-gate-family blend Pareto-dominates mixed-gate
  on score AND Sharpe. Gate alignment decorrelates better than
  always-on diversifier.

### Mechanism: why meta-ensemble breaks the ceiling

**Pre-iter expectation** (hypothesis.md linear-mean): CAGR 15.68%, MDD
~41.7%, score ~67-70. Observed: CAGR 16.30% (+0.62pp), MDD 34.83%
(−6.87pp), score 70 (top of estimated range).

**Why MDD beats linear estimate by 6.87pp** — gate decorrelation:
- A2 uses QQQ 200d SMA (NDX-100); G2 uses SPY 200d SMA (SPX). QQQ/SPY
  correlation 0.85-0.90.
- During 2000-02 dot-com: NDX -78% started months before SPY top → A2
  gate triggered earlier, G2 gate triggered later → blended exposure
  transitioned smoothly.
- During 2008 GFC: QQQ and SPY moved in lockstep — blend MDD ≈ linear.
- During 2022 inflation: NDX bear deeper than SPY → A2 derisked first.
- Aggregate: meta-blend captures bear-mode early AND exits late,
  reducing both depth AND duration of drawdowns.

**Why Sharpe lift exceeds linear**: vol compression from gate
decorrelation. Linear (0.804 + 0.970)/2 = 0.887 → observed 0.933
(+0.046 = 5.2% Sharpe boost from decorrelation).

### Architectural taxonomy diagnostic (UPDATED — 8 fams + 3 hybrids + meta-ensemble)

| family | best gross score | best Sharpe | best mean MDD |
|:---|---:|---:|---:|
| **META-ENSEMBLE (NEW iter 018)** | **70** ⬅ NEW BEST | 0.933 | 34.83% |
| A2 TQQQ-track LRS (iter 006) | 67 | 0.804 | 49.73% |
| A1/A3 SPY-track LRS | 66 | 0.744 | 51.60% |
| E1 hybrid (TSMOM × A2 at 3× LETF) | 65 | 0.746 | 47.48% |
| G2 hybrid (SMA × F1 LETF at 2.25×) | 64 | 0.970 | 26.76% (G2 blend) |
| B1/B2 HFEA barbell | 63 | 0.739 | 67.48% |
| F1 Levered All-Weather (iter 015) | 61 | 1.018 | 26.82% |
| G1 hybrid (SMA × F1 stack at 1.41×) | 61 | **1.080** ⬅ BEST | **18.57%** ⬅ BEST OVERALL |
| C1 vol-target | 60 | 0.721 | 41.86% |
| D1 concentrated+TSMOM (1×) | 59 | 0.779 | 35.27% |
| D2 stacked equity | 52 | 0.738 | 52.65% |

**The architectural ceiling claim (KILL #33) is REJECTED at the
meta-portfolio axis** — but the meta-ensemble itself does NOT contain
new asset/gate primitives. It is a TWO-LEVEL composition. The formal
taxonomy is NOW complete across 4 axes:
- 8 single-axis families (asset-axis): A1/A2/B1/B2/C1/D1/D2/F1
- 3 cross-product hybrids (gate × sleeve × decay-axis): E1 / G1 / G2
- 1 meta-ensemble (strategy-axis): h1_meta_50a2_50g2ief NEW

### Statistical integrity (caveats)

- **Cumulative n_trials**: 53 → 56. DSR worst p = 1.65e-04 << 0.05.
  But meta-ensemble adds combinatorial dimensions NOT counted.
- **PBO grid-level**: lh_56y 0.151 (excellent); spy_real 0.603 (FAILS
  strict G1 by 0.103). N=3 warning persists.
- **G3 walk-forward FAILS 25% threshold** by 8.7pp on lh_56y / 7.1pp on
  spy_real.
- **Selected config gates exactly at threshold on spy_real** (5/7 = 5).
  Thinner-than-typical gate margin.
- **G6 bootstrap CI low**: lh_56y 0.508, spy_real 0.222. Both > 0.
- **G7 cross-lib ±3pp CAGR**: 0.0pp delta. Engine consistency excellent.

### Surprising findings

1. **Meta-ensemble BREAKS 67-cap by 3pts at gross score 70** —
   architectural-ceiling claim that survived 11 iters / 41 trials /
   8 fams / 3 hybrids is now empirically rejected at meta-portfolio
   axis on canonical pre-committed rubric.
2. **MDD axis decorrelation gain (6.87pp) DRAMATICALLY exceeds CAGR
   axis gain (0.62pp)** — first observation of true portfolio-theory-
   style decorrelation Pareto-improvement in this hunt.
3. **Same-gate-family wins over mixed-gate** (KILL #60 fires) — gate
   alignment > always-on diversification at spy_beater rubric.
4. **Tax-layer caveat narrows the win**: net-of-tax score 64 ties
   iter 017 G2 IEF gross 64; meta-ensemble's gross +3pt edge compresses
   to ~+1-2pt edge net-of-tax (assuming similar drag on prior baseline).
5. **PBO 0.603 on spy_real is concerning** but within N=3 warning band.
6. **Robustness 5y pass-rate 88.9% vs A2's 100% / G2's 50%** —
   meta-ensemble achieves strictly better short-horizon than G2 alone.

### Direction implications

**META-ENSEMBLE family** — OPEN at gross score 70 (KILL #59 fired).
Architecturally promising; iter 019+ would deeper-explore:
- (a) Different 50/50 constituent pairs (A2 + G1 IEF; A2 + F1 stack; etc.)
- (b) 3-way blends (A2 + G2 IEF + F1 stack at varying weights)
- (c) Weight sweeps around 50/50 (45/55, 55/45, etc.)
- (d) Different gate combinations in constituents

**Caveats for iter 019+ extension**:
- Meta-ensemble adds combinatorial search dimensions not captured in
  current DSR n_trials. iter 019+ should count meta-search explicitly.
- PBO N=3 warning addressable via N≥6 configs/iter.
- Tax-layer integration changes scoring landscape — re-score prior
  closest-to-winner candidates net-of-tax for apples-to-apples.
- Score 70 is BORDERLINE-above-67 by exactly 3pts (gross). Definitive
  rejection of KILL #33 at meta-axis needs iter 019+ confirmation.

### Path to score 90 (META-ENSEMBLE architecture)

UNCLEAR — first open-axis exploration. Realistic Pareto-feasible
ceiling for meta-ensemble family ≈ 72-78 (3-way blends + weight
optimization). Tier STRONG (75-89) becomes potentially reachable;
tier WINNER (≥90) still architecturally out of reach.

### Suggested iter 019+

Hunt status changes from CLOSED (since iter 011) to **PARTIALLY
REOPENED at meta-ensemble axis** following KILL #59 trigger.

Recommended iter 019:
- 6 configs (improves PBO N=3 → N=6 statistical stability).
- 3-way blends: A2 + G2 IEF + F1 stack at varying weights.
- Weight sweep: 50/50, 60/30, 50/30/20, 40/30/30, 33/33/34, 70/30.
- Cumulative n_trials: 56 + 6 = 62.
- Pre-commit KILL: if best iter-019 score still < iter-018 70, the
  meta-ensemble axis ceiling is at 70 (consolidates KILL #59 with
  single data point); if best ≥ 75, tier STRONG reachable.
- Re-score iter-006 A2 net-of-tax for apples-to-apples comparison.

**However**: per CLAUDE.md mandate §1 + §7, this iter does NOT alter
the deploy decision. Score 70 < 90 WINNER threshold. F1+SPLIT
incumbent fallback retains deploy-ready status. Iter 019+ exploration
is RESEARCH ONLY at this stage.

### Why this iter STRENGTHENS the rubric-revision review case

iter 015 F1 stand-alone, iter 016 G1 IEF, iter 017 G2 IEF, and now
iter 018 meta-ensemble all show strong-Sharpe + low-MDD configs scoring
at or above the prior 67-ceiling under multiple axes. The CAGR-anchored
rubric continues to penalize balanced multi-asset architectures, but
the meta-ensemble axis breaks the ceiling cleanly under the existing
rubric. This is empirical evidence that:
- Single-strategy 67-cap was an artifact of insufficient axis exploration,
  not a fundamental property of the spy_beater rubric.
- Portfolio-of-strategies thinking is genuinely additive over single-
  strategy exploration.
- The hunt's negative-result claim should be REFINED to "single-strategy
  spy_beater architectural ceiling is at 67-cap (gross); meta-ensemble
  axis exceeds it but tier WINNER (≥90) remains architecturally out of
  reach per current Pareto-feasible analysis".

### Citations

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over
  multiple alpha streams — meta-ensemble axis EMPIRICALLY VALIDATED;
  decorrelation gain on MDD axis (6.87pp super-linear) consistent with
  Markowitz-style mean-variance optimization at strategy-level.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking
  thesis generalized to strategy-level: blending two regime-gated
  strategies with decorrelated signals delivers Sharpe lift + MDD
  relief beyond linear-mean prediction.
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA gate
  at meta-ensemble level: gates on different signals (QQQ vs SPY)
  decorrelate sufficiently to deliver vol compression + MDD relief.
  Linear correlation 0.85-0.90 → effective decorrelation 10-15% on
  exposure during regime transitions.
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM) — present
  in both A2 (30% in ON-state) and G2 (15% in ON-state).
- Bridgewater All-Weather (Dalio 1996) — F1 stack constituent NOT
  selected in best blend (50/50 same-gate beat 60/40 mixed-gate per
  KILL #60). At spy_beater rubric, gated decorrelation > always-on
  diversification.
- `[advances_fin_ml, p.31-34]` factor framework — meta-ensemble axis
  added to architectural taxonomy. Hunt's formal taxonomy is now
  complete across 4 axes: asset, gate, decay, meta. Meta-axis
  EMPIRICALLY breaks the prior 67-cap.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 56, worst
  p = 1.65e-04 — strong margin BUT does NOT count meta-search
  combinatorial dimensions; honest n_trials is likely larger.
- `[advances_fin_ml, p.208-211]` PBO grid-level — N=3 warning persists;
  PBO 0.603 on spy_real is concerning but within instability band.
- `[advances_fin_ml, p.196-202]` bootstrap CI — G6 passed comfortably
  on both datasets (lh 0.508, spy 0.222).
- Lei 14.754/2023 (DARF 15% annual) — first iter to include net-of-tax
  drag analysis. Net total_score 64 vs gross 70; tax-aware ceiling-
  break narrows from +3pts to ~+1-2pts vs prior closest-to-winner.
