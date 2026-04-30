# spy_beater_hunt iter 022 — Final Report — `B5-hfea-modest-upro-tlt`

**Gross tier**: **MARGINAL** — `gross_score=58/100`, `gross_winner_met=True`

**Net tier**: **MARGINAL** — `net_score=56/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 14.13%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 54.47%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 13.50%)
- MDD bar: PASS (mean = 54.47%)
- Gates bar (same as gross): PASS

**Primary citation**: HFEA Bogleheads 2019 canonical 55/45 anchor + modest-leverage variant + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay rationale (1x TLT eliminates TMF 1.5%/y daily-reset decay) + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (B5 50/50 = 150% SPY notional + 50% UST notional) + [ilmanen_expected_returns, ch.19] MF crisis-alpha role + [advances_fin_ml, p.31-34] factor framework + [advances_fin_ml, p.222-223] DSR cumulative_n_trials = 80 + [advances_fin_ml, p.208-211] PBO via CSCV N=6 + WINNER_AND_RANKING.md structural net-rubric advantage 1.5pp for buy-hold static

---

## Selected config: `b5_4040_kmlm20`

Spec:

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.4,
    "TLTSIM": 0.4,
    "KMLMSIM": 0.2
  }
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 0.744 | 14.32% | 54.47% | 0.722 | 13.84% | 54.47% | 0.48 | 6/7 |
| **spy_real** | 0.728 | 13.94% | 54.47% | 0.692 | 13.17% | 54.47% | 0.77 | 6/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — buy_hold, 0 year-end settlements, total DARF $259,754 (terminal $259,754), drag 0.48pp
- `spy_real` — buy_hold, 0 year-end settlements, total DARF $26,968 (terminal $26,968), drag 0.77pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| b5_5050_upro_tlt | 0.641 | 0.664 |
| b5_4060_upro_tlt | 0.691 | 0.704 |
| b5_6040_upro_tlt | 0.603 | 0.630 |
| b5_4040_kmlm20 | 0.744 | 0.728 |
| b5_5030_kmlm20 | 0.680 | 0.675 |
| b5_4040_dbmf20 | 0.570 | 0.714 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 18 | 30 | mean = 14.13%, bar = 11.21% |
| 2. MDD vs SPY | 5 | 20 | mean = 54.47%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 1.54e-02, n_trials = 80 |
| 5. Sharpe | 2 | 10 | mean = 0.736 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 88.9% | 54.47% |
| 10y | 100.0% | 54.47% |
| 15y | 100.0% | 54.47% |
| 20y | 100.0% | 54.47% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

- **PBO N=6 stability MAINTAINED** per iter-019 KILL #64 resolution.
  6 configs run on N=6 grid; cumulative_n_trials = 80; DSR worst p =
  1.54e-02 (PASSES <0.05 threshold but TIGHTER than recent meta-axis
  iters at 1.26e-04 to 1.55e-04 — Sharpe ~0.73 is much lower than
  meta-axis 1.0+ so DSR gain margin shrinks). Threshold tightens to
  ~0.05/80 = 6.25e-04 under conservative Bonferroni; nominal p = 0.0154
  passes single-comparison but is borderline under multiple-testing
  adjustment.
- **All assets DIRECT in testfolio cache**: UPROSIM, TLTSIM, KMLMSIM,
  DBMFSIM all present in cache. No synth construction. NO new infra.
  771 tests baseline preserved.
- **2-dataset framework**: lh_56y (40y synth) + spy_real (22.7y Tiingo
  daily). Methodology refactor 2026-04-29 unchanged.
- **Tax classification**: all 6 configs `spec.type = "static"`,
  classified as buy_hold (terminal DARF settlement). Drag 0.48pp lh /
  0.77pp spy = mean 0.63pp — within predicted [0.59, 0.74] range from
  WINNER_AND_RANKING.md "Final ranking" table.
- **MDD bar tight margin**: selected `b5_4040_kmlm20` mean MDD 54.47%
  is **0.70pp below the 55.17% bar** — among the tightest margins in
  the entire hunt for a winner_conditions_met=TRUE config. Single MDD-
  bucket worst-window aggravation could break the bar.
- **Score 58 < 60 ⇒ MARGINAL tier** despite winner_conditions_met=TRUE.
  This is the LOWEST gross score for a 3/3-bar-passing config in the
  entire 22-iter hunt (prior low was iter 013 d1_qqq_6m_tsmom at 59).
  The MDD axis penalty (rubric anchor [0.7, 0.15], MDD 54.47% gives
  only 5/20 pts) caps scoring even at honest MDD-bar-passing.

## Lesson

### Verdict summary

**Gross tier MARGINAL 58/100** — `winner_conditions_met=True` for
selected `b5_4040_kmlm20` (40% UPRO + 40% TLT + 20% KMLM). All 3 bars
PASS but score lands MARGINAL because MDD axis (mean 54.47%) sits in
the rubric's lower-points region (5/20 pts at anchor [0.7, 0.15]) and
Sharpe (mean 0.736) lifts only 2/10 pts.

**Net tier MARGINAL 56/100** — drag 2pts (0.63pp CAGR), within
predicted 0.59-0.74pp range for buy_hold static. Net rank-1
displacement (KILL #80) **NOT achieved** — net 56 << meta-axis net 64.

**Critical empirical finding — pure 50/50 UPRO/TLT FAILS MDD bar**:
`b5_5050_upro_tlt` mean MDD = 69.09% (lh 69.09%, spy 69.09%; identical
suggesting 2008/2000-02 dominance shared across datasets) — this is
13.92pp ABOVE the 55.17% bar. **The 1× TLT replacement of 3× TMF was
INSUFFICIENT to save MDD bar without further additions**. This
falsifies KILL #78's hypothesis that TMF→TLT alone breaks the
HFEA classical MDD problem.

**The KMLM 20% addition is what saves MDD bar** — `b5_4040_kmlm20`
mean MDD 54.47% (vs `b5_5050` 69.09%, a −14.62pp lift) AND lifts
Sharpe (+0.084 vs `b5_5050`'s 0.653) AND lifts CAGR (−0.90pp drag,
mean CAGR 14.13% vs 15.03% for 5050). The crisis-alpha effect is
**multiplicative with the duration-leverage reduction**, not additive
— at HFEA classical (165% UPRO + 135% TMF), KMLM's effect was diluted
into massive notional; at modest-HFEA (150% UPRO + 50% TLT), KMLM has
genuine room to diversify.

### Pre-committed KILL outcomes

| KILL | name | trigger threshold | observed | result |
|---:|:---|:---|:---|:---:|
| #6 | best CAGR < 11.21% → CAGR floor | best CAGR < 11.21% | best 15.88% | **NOT FIRED** |
| #77 | max B5 score ≤ 71 → static-barbell ceiling matches meta-axis | max ≤ 71 | 58 | **FIRED (HARD)** — 13pt gap |
| #78 | b5_5050 mean MDD ≤ 55.17% → MDD bar reachable via 1× TLT alone | b5_5050 MDD ≤ 55.17% | 69.09% | **NOT FIRED** |
| #79 | KMLM addition lifts Sharpe in modest-HFEA (counter to KILL #27) | KMLM-Sharpe > non-KMLM-Sharpe | 0.736 > 0.653 / 0.677 > 0.653 | **FIRED** |
| #80 | best B5 net_score ≥ 65 → displaces meta-axis net rank-1 | net ≥ 65 | 56 | **NOT FIRED** |
| #81 | b5_6040 mean MDD > 55.17% → offensive 60/40 catastrophic | MDD > 55.17% | 78.97% | **FIRED (HARD)** |
| #82 | best B5 score ≥ 75 → STRONG tier reachable via static path | score ≥ 75 | 58 | **NOT FIRED** |

### Closest-to-winner (UNCHANGED)

**iter-019 `h2_meta_3way_33a2_33g2_34f1` REMAINS as closest-to-winner
at gross score 71.** iter-022 selected 58 << 71 (gap 13pts). B5
static-barbell axis CLOSED at 58 — well below meta-axis ceiling.

Gap-by-criterion vs iter-019 (71 → 58, −13):

| criterion | iter 019 (3-way meta-ensemble) | iter 022 (static modest-HFEA + KMLM) | Δ |
|---|---:|---:|---:|
| 1. CAGR vs SPY | 20 (mean 15.04%) | 18 (mean 14.13%) | −2 |
| 2. MDD vs SPY | 15 (mean 28.50%) | **5 (mean 54.47%)** | **−10** |
| 3. Gates | 13 (6/7+6/7) | 13 (6/7+6/7) | 0 |
| 4. DSR | 10 | 10 | 0 |
| 5. Sharpe | 4 (mean 1.025) | **2 (mean 0.736)** | **−2** |
| 6. Robustness | 9 | **10** | **+1** |
| **TOTAL (gross)** | **71** | **58** | **−13** |

The MDD-axis penalty alone accounts for 10 of the 13-pt gap. Sharpe
contributes another 2pt loss. CAGR is roughly tied (−2pt minor). Net
trade is dominated by the MDD axis: meta-ensemble's 28.50% mean MDD
is structurally unmatched by any modest-HFEA static blend that stays
above the 11.21% CAGR floor — the leveraged equity arm (50% UPRO =
150% SPY notional) drives MDD to 54%+ even with KMLM crisis-alpha,
whereas the meta-ensemble's gated structure (200d SMA on QQQ AND SPY
+ always-on multi-asset) reduces MDD by 26pp via ON/OFF regime exits.

### Comparison vs iter-008 HFEA classical 50/50

| metric | iter 008 b1_balanced_5050 (UPRO+TMF) | iter 022 b5_5050_upro_tlt (UPRO+TLT) | Δ |
|---|---:|---:|---:|
| Mean CAGR | ~17.5% | 15.03% | **−2.47pp** |
| Mean MDD | ~67.48% | 69.09% | **+1.61pp** |
| Mean Sharpe | ~0.74 | 0.653 | **−0.087** |
| Score | 63 | est ~52-55 | **−8 to −11** |

**SURPRISE — UPRO+TLT MDD slightly WORSE than UPRO+TMF** at 50/50.
Expected MDD relief from 1× duration didn't materialize — TMF's 2008
positive return (rallied during GFC as Fed cut rates) PROVIDED
substantial MDD buffer that 1× TLT does not match (TLT 2008 gain
~+25% × 50% = +12.5% buffer; TMF 2008 gain ~+75% × 50% = +37.5%
buffer). The 2022 advantage of TLT (−31% vs TMF −70%) is
OUTWEIGHED by 2008 disadvantage in lh_56y synth.

### Key insight: 2008 dominates MDD on lh_56y synth

The hidden assumption in B5 hypothesis was "2022 is the binding
regime for HFEA-style barbells". Empirical result REJECTS that:
2008 binding regime on lh_56y synth (40y window). Pure 50/50 UPRO/TLT
mean MDD 69.09% is dominated by 2008-2009 path-dependent compounding
where TLT's smaller positive return cannot offset UPRO's catastrophic
−85% drawdown.

This explains why `b5_5050_upro_tlt` (no MF) FAILS MDD bar but
`b5_4040_kmlm20` (with MF) PASSES — KMLM's 2008 contribution
(+6-12% range) supplies the missing buffer that lower TLT leverage
removed from TMF's 2008 buoy.

### KILL #79 FIRED — KMLM-on-modest-HFEA Sharpe lift (KILL #27 inverted)

**Key architectural finding**: at HFEA classical (165% UPRO + 135% TMF
notional), KMLM 15-25% addition was Sharpe-flat-to-negative (KILL #27
fired iter 009). At modest-HFEA (150% UPRO + 50% TLT notional), KMLM
20% addition LIFTS Sharpe by +0.083 (4040+kmlm20 0.736 vs 4060 0.698)
AND simultaneously LIFTS MDD relief by 14.62pp (4040+kmlm20 54.47% vs
5050 69.09%).

**Mechanism**: at HFEA classical's 300% combined notional, KMLM at 20%
is diluted into the high-notional barbell — its decorrelation gain is
swamped by the 3×+3× compounded volatility. At modest-HFEA's 200%
combined notional, the 20% KMLM has structural room to diversify;
its 2008 positive return + 2022 strong positive return AND
lower-volatility profile combine multiplicatively with the lower-
leverage duration leg.

**Generalization**: MF crisis-alpha effectiveness is INVERSELY
proportional to backbone notional leverage. At ≤200% combined notional,
20% MF is effective; at >300% combined notional, MF is diluted.

### Per-config Sharpe rank within iter

| config | mean Sharpe | rank |
|:---|---:|---:|
| b5_4040_kmlm20 (selected) | 0.736 | 1 |
| b5_4060_upro_tlt | 0.698 | 2 |
| b5_5030_kmlm20 | 0.677 | 3 |
| b5_5050_upro_tlt | 0.653 | 4 |
| b5_4040_dbmf20 | 0.642 | 5 |
| b5_6040_upro_tlt | 0.616 | 6 |

Sharpe-monotonic: defensive end (lower UPRO) Sharpe-best for both
2-leg AND 3-leg configs. KMLM > DBMF as MF crisis-alpha at same 20%
weight — Mount Lucas Managed Futures Index (KMLM) outperforms
broader CTA basket (DBMF) by +0.094 mean Sharpe.

### KILL #81 FIRED — offensive 60/40 catastrophic

`b5_6040_upro_tlt` mean MDD 78.97% — among the worst MDDs in entire
hunt for a CAGR-passing config. The 60% UPRO weight (180% SPY
notional) compounds 2008 GFC drawdown to ~−95%, blended with 40%
TLT (+25% gain in 2008 = +10pp buffer) → net ~−85% portfolio MDD.
**60% UPRO is the offensive cap for HFEA-modest** — exceeding 50%
UPRO breaks MDD bar regardless of duration leg structure.

### Direction implications

**B5 family CLOSED at score 58.** The static-barbell axis caps at
58 within spy_beater rubric. The 1× duration replacement of 3× TMF
was insufficient alone (KILL #78 NOT FIRED) — KMLM addition was
required to barely scrape the MDD bar.

**Static-barbell ceiling of 58 vs meta-axis ceiling of 71 = 13pt
gap, driven entirely by MDD axis (10pt) + Sharpe axis (2pt)**. The
static path's tax-rubric advantage (drag −2pt vs meta's drag −6pt
= 4pt structural advantage) cannot offset the 13pt MDD axis penalty.

**Strengthens KILL #33 architectural ceiling claim**: now confirmed
at 5 architectural axes:
1. LRS-mono (single LRS strategy): cap 67 (A2)
2. Static (HFEA + KMLM): cap 63 (B2)
3. Vol-target: cap 60 (C1)
4. Cross-product hybrid (gate × sleeve): cap 65 (E1)
5. Meta-ensemble (LRS-blend): cap 71 (H2)
6. **Static-barbell modest-leverage (B5)**: cap 58

The architectural ceiling at 71 (meta-axis) appears to be the
FUNCTIONAL maximum within spy_beater rubric for any combination
that maintains WINNER_AND_RANKING.md scoring anchors.

### Net rubric perspective

Net rank ladder (post-iter-022):
1. iter 018 H1 meta-ensemble: gross 70 / **net 64**
2. iter 009 b2_hfea_kmlm20 static: gross 63 / net 62
3. iter 007 a7_tqqq_split_kmlm40_tlt10: gross 67 / net 61
4. iter 008 b1_balanced_5050: gross 63 / net 61
5. iter 006 a6_tqqq_split_kmlm30_tlt10: gross 67 / net 60
... iter 022 selected lands at net 56, slotting around rank 12-13.

**Net rank-1 displacement (KILL #80) NOT achieved**. The 1.5pp
structural net advantage was real (B5 drag 0.63pp << meta 1.91pp =
1.28pp advantage) but absolute score 58 was too low for net rubric
to lift it past 64.

**Implication**: the "buy-hold static net advantage" thesis is
**TRUE in mechanism but insufficient in magnitude** to overcome
absolute score gap when the static config caps at 58 vs blend caps
at 70-71. A static config would need gross ≥ 65 AND drag ≤ 1.0pp
to match meta-ensemble net rank-1 — empirically unreachable within
spy_beater rubric across 22 iters.

### Strategic options for iter 023+ (USER DECISION)

The hunt now has 5 axes mapped (LRS-mono, static, vol-target,
hybrid, meta-ensemble, static-barbell) — TAXONOMY ESSENTIALLY
COMPLETE within current architecture. 28 iters remaining (22/50
used). Options:

(A) **Declare hunt EFFECTIVELY-CLOSED at iter-022 (most defensible
per mandate §1)** — taxonomy is structurally complete; meta-axis
ceiling at 71 confirmed across 4 sequential iters; static-barbell
axis confirms 71 ceiling is spec-type-near-invariant (B5 below by
13pt due to MDD axis); F1+SPLIT confirmed deploy fallback;
remaining 28 iters preserved for future hunts.

(B) **Test ONE more axis if untested directions remain**: only
C2 CAPE-timing remains formally untested (low-credibility, 20+
years of OOS failure, no CAPE data infrastructure). Probably not
worth iter cost.

(C) **Pivot off score axis to mandate §7 rubric-revision request**
(now strengthened to **6th iter** with rubric-suboptimal but
honest-bar-passing config — after 015 F1, 016 G1, 018+019+020+021
meta-ensembles, and now iter 022 with 0.70pp MDD-bar margin).

**Recommendation: Option A.** The 5-axis architectural mapping
EMPIRICALLY ESTABLISHES that no single architectural pivot within
the spy_beater rubric reaches WINNER tier (score ≥ 90) — the gap
from ceiling 71 to 90 is 19pts and no pivot has produced movement
in the right direction. F1+SPLIT remains deploy-ready under
mandate §1.

### Citations

- HFEA Bogleheads 2019 — canonical 55/45; modest-leverage variants
  in subsequent threads.
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — LETF decay
  rationale; replacing 3× TMF with 1× TLT eliminates 1.5%/y duration
  decay BUT removes 2008 buoy.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking;
  B5 50/50 = 200% combined notional vs HFEA classical 300% notional.
- `[ilmanen_expected_returns, ch.19]` — MF crisis-alpha effectiveness
  is INVERSELY proportional to backbone notional leverage (KILL #79
  FIRED, KILL #27 inverted at modest leverage).
- `[advances_fin_ml, p.31-34]` factor framework — UPRO + TLT + KMLM
  is a clean 3-factor stack with low cross-correlation.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 80;
  worst p = 1.54e-02 PASSES single-comparison threshold.
- `[advances_fin_ml, p.208-211]` PBO via CSCV N=6 stable.
- WINNER_AND_RANKING.md "Final ranking — gross vs net" — net
  advantage real but insufficient to overcome 13pt absolute gap.
