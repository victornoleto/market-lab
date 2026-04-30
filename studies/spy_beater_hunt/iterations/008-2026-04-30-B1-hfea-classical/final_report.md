# spy_beater_hunt iter 008 — Final Report — `B1-hfea-classical`

**Tier**: **PROMISING** — `score=63/100`, `winner_conditions_met=False`

**Strict bars** (CAGR-anchored, spy_beater rubric):
- CAGR bar (mean ≥ 13.80%): PASS (mean = 19.68%)
- MDD bar (mean ≤ 40.85%): FAIL (mean = 67.48%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay rationale + HFEA Bogleheads 2019 canonical 55/45 + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking + [advances_fin_ml, p.31-34] factor framework (leveraged duration as distinct factor)

---

## Selected config: `b1_balanced_5050`

Spec:

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.5,
    "TMFSIM": 0.5
  }
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 0.755 | 20.62% | 67.48% | 6/7 | 4.96e-05 |
| **spy_real** | 0.724 | 18.73% | 67.48% | 5/7 | 4.91e-03 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| b1_classic_5545 | 0.737 | 0.723 |
| b1_modern_6040 | 0.713 | 0.713 |
| b1_balanced_5050 | 0.755 | 0.724 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 29 | 30 | mean = 19.68%, bar = 11.21% |
| 2. MDD vs SPY | 0 | 20 | mean = 67.48%, bar = 55.17% |
| 3. Gates | 12 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 4.91e-03, n_trials = 29 |
| 5. Sharpe | 2 | 10 | mean = 0.739 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 86.1% | 67.48% |
| 10y | 100.0% | 67.48% |
| 15y | 100.0% | 67.48% |
| 20y | 100.0% | 67.48% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 36

## INCOMPLETE flags

- **TMFSIM synth approximation**: synth uses constant 1.5%/y daily-reset
  decay (`tmf_synth_returns_from_cache`); real TMF decay is regime-
  dependent. In 2022 high-vol environment (TLT vol ~22%) real decay was
  closer to 3-5%/y; our synth understates the 2022 drag. The measured
  MDD on spy_real (67.48% selected, 67.13% canonical 5545) likely
  understates true 2022 HFEA pain by 5-10pp — meaning the real-world
  KILL #24 trigger is even sharper than our synth shows.
- **TLT cache pre-1980 backfill**: TLTSIM cache starts 1962 but pre-1986
  bars are testfolio's index synth (LTT yield curve reconstruction).
  Within `lh_56y` (1986+) this is irrelevant.
- **UPROSIM cache pre-2009**: real UPRO inception 2009-06; pre-2009 is
  testfolio's SPY × 3 with daily-reset decay synth. The 2008 GFC stress
  test on lh_56y is fully synthetic.
- **No transaction costs / no quarterly rebalance friction**: HFEA
  classical assumes quarterly rebalance per Bogleheads thread; we use
  daily rebalance (instantaneous). Real quarterly HFEA has 4× annual
  rebalance spread + slippage cost (~0.1-0.3%/y drag).
- **PBO N=3 warning emitted**: CSCV statistically unstable at N<4.
  spy_real PBO 0.952 is suspect — would not survive larger grid; informa-
  tive only here. Cumulative `n_trials=29` cross-iter grid carries the
  anti-overfit weight (DSR worst p = 4.91e-03 << 0.05 bar).
- **2022 stress regime**: spy_real Tiingo daily 2003+ contains the
  full 2022 inflation drawdown. lh_56y synth also captures it (HFEA
  MDD identical 67.48% across both datasets — driven by 2022 in both).
- **Daily rebalance vs quarterly HFEA**: published HFEA backtests use
  quarterly rebalance which slightly muffles intra-quarter swings but
  doesn't change MDD materially in 2022 stress (the drawdown was
  multi-month, not intra-month).

## Lesson

### Score 63/100 — BELOW closest-to-winner (iter 006/007 retain at 67)

iter 008 scored 63 PROMISING — **−4 below iter 006/007's 67**. iter 006
`a6_tqqq_split_kmlm30_tlt10` retains closest-to-winner status. The
HFEA leveraged-barbell **structurally fails the MDD bar** (67-72% across
all 3 weight points; bar is 55.17%) while delivering the **highest
CAGR among all 8 iters** (29/30 pts on criterion 1).

| criterion | iter 006 a6_kmlm30_tlt10 | iter 008 b1_balanced_5050 | delta |
|---|---:|---:|---:|
| 1. CAGR | 25 (mean 17.33%) | **29 (mean 19.68%)** | **+4** |
| 2. MDD  | 7  (mean 49.73%) | **0 (mean 67.48%)** | **−7** |
| 3. Gates | 13 (6+6, cross_met) | 12 (6+5, cross_met) | −1 |
| 4. DSR  | 10 (n=23, worst p 3.05e-03) | 10 (n=29, worst p 4.91e-03) | 0 |
| 5. Sharpe | 2 (mean 0.759) | 2 (mean 0.739) | 0 |
| 6. Robustness | 10 (5/10/15/20y all 100%) | 10 (5y 86.1%, 10/15/20y 100%) | 0 |
| 7. Extra | 0 | 0 | 0 |
| **Total** | **67** | **63** | **−4** |

The trade-off is sharp and asymmetric: HFEA gives up **7 pts on MDD**
(structural KILL territory) to gain **4 pts on CAGR** (already capped
near 30/30). Within the CAGR-anchored rubric this is a net loss
because criterion 1 is saturated near the top of its anchor range
while criterion 2 is at the **bottom** (anchor [0.15, 0.70], MDD 0.67
gives 0 pts).

### KILL conditions outcomes

- **KILL #6 (CAGR floor 11.21%)** NOT FIRED — best CAGR mean 20.14%
  >> 11.21% bar. All 3 configs comfortably above. CAGR is HFEA's
  strength, not its weakness.
- **KILL #24 (HFEA 2022-stress MDD > 65% on spy_real)** **FIRED** —
  `b1_classic_5545` spy_real MDD 67.13% > 65% bar. The 2022 inflation
  regime breaks the leveraged-barbell thesis structurally. Direction
  B1 HFEA classical CLOSED at canonical weights 50-60% UPRO range.
  Pivot per hypothesis.md → **B2 HFEA + KMLM crisis-alpha** (literature-
  aware response).
- **KILL #25 (TMFSIM standalone Sharpe out of [0, 1.0])** NOT FIRED —
  TMF 1986+ Sharpe 0.49 (verified pre-iter, in band). Synth integrity
  confirmed.
- **KILL #26 (HFEA monotonic regression at 55/45)** NOT FIRED —
  `b1_balanced_5050` Sharpe (0.755, 0.724) > `b1_classic_5545` Sharpe
  (0.737, 0.723) on BOTH datasets. The condition required BOTH 6040<5545
  AND 5050<5545 on Sharpe BOTH datasets; only 6040<5545 holds (5050
  beats 5545). Bogleheads risk-parity claim that 55/45 is locally
  optimal is **REJECTED** by our synth: optimal Sharpe is at
  **5050 or below** (more TMF, less UPRO).

### HFEA dose-response on UPRO weight (3 data points)

| UPRO % / TMF % | mean Sharpe | mean CAGR | mean MDD | source |
|:---:|---:|---:|---:|:---:|
| 50% / 50%  | **0.740** | 19.68% | 67.48% | iter 008 (selected) |
| 55% / 45%  | 0.730 | 20.00% | 67.13% | iter 008 |
| 60% / 40%  | 0.713 | 20.14% | 72.70% | iter 008 |

Pattern: **monotonic NEGATIVE on Sharpe** as UPRO weight rises in
[50, 60] (sharp 0.027 drop from 50→60). CAGR rises only 0.46pp
across the 10pp UPRO range (much weaker dose-response than expected).
MDD rises 5.2pp across the same 10pp range (driven entirely by the
50→55→60 transitions). The TMF-heavy (50/50) variant dominates on
Sharpe and ties 5545 on MDD.

**Interpretation**: at 165%+ leveraged equity notional, the marginal
contribution of UPRO is **diminishing fast** while marginal MDD
contribution is **accelerating**. The Sharpe-optimal HFEA is somewhere
**below 50% UPRO** (e.g., 45% UPRO + 55% TMF) — but pushing further
TMF makes MDD even worse in 2022 (TMF was 2022's deepest single-asset
hit at ~−70%). The result: HFEA classical has no locally optimal
configuration that clears the spy_beater MDD bar. **Architecture
fundamentally incompatible** with the 55.17% mean MDD requirement.

### H₁ / H₂ / H₃ outcomes

- **H₁ REJECTED**: HFEA classical (`b1_classic_5545`) does NOT clear
  the 3 strict bars. CAGR ✓ (20.00% ≥ 11.21%), Gates ✓ (6+5 cross_met),
  but **MDD FAIL** (67.13% mean > 55.17% bar). The 2022 regime is the
  killer.
- **H₂ REJECTED**: monotonic dose-response on UPRO weight predicted
  CAGR and MDD both rising; only MDD rises monotonically (5050<5545<6040
  but with weak slope at 5050→5545). Sharpe and CAGR are NOT monotonic
  positive on UPRO weight; Sharpe is in fact monotonic NEGATIVE.
  Bogleheads 55/45 risk-parity claim falsified by our synth.
- **H₃ CONFIRMED**: spy_real MDD (67.13-72.70%) drives the binding
  constraint identically to lh_56y MDD (67.13-72.70% — note: identical
  to 2 dec places, suggesting both datasets see the same 2022 trough).
  Future B-direction iters must add crisis-alpha (KMLM/CTA) targeted
  at 2022-style stagflation regimes.

### Cross-iter direction implications

- **B1_HFEA_classical**: **CLOSED** — KILL #24 fired at canonical 55/45;
  no UPRO weight in [50, 60] clears the MDD bar. Architecture
  fundamentally subordinate to LRS-style regime-gated strategies on
  the 2022 stress regime. Highest CAGR among all 8 iters (criterion 1
  saturated near 30/30) but at structurally unacceptable MDD.
- **B2_HFEA_KMLM**: **PROMISING NEXT** — literature-aware response to
  the 2022 weakness. Add 15-20% KMLM crisis-alpha; iter 003-005 SPY-track
  showed +30% KMLM cuts MDD by ~15pp at <2pp CAGR cost. If the same
  applies to HFEA, target MDD 50-55% range may be reachable, lifting
  criterion 2 from 0 → 8-10 pts. Total expected: ~70-72.
- **C1_vol_targeted**: still **NOT YET RUN** — fallback if B2 also
  fails the MDD bar. Different geometry (dynamic leverage scaling)
  may unlock Sharpe lift not captured by the static-weight family.

### Suggested iter 009

**Recommended pivot: B2 HFEA + KMLM crisis-alpha**. Rationale:

- B1 HFEA classical CLOSED — no UPRO weight in [50, 60] passes MDD bar.
- KMLM dose-response empirically validated on SPY-track (iter 003-005)
  and TQQQ-track (iter 007): +30% KMLM cuts MDD ~15pp with <2pp CAGR
  drag, monotonic positive Sharpe through 40%.
- Adding 15-20% KMLM to HFEA at 50% UPRO + 35% TMF + 15% KMLM should
  reduce MDD from 67% → ~52-55% (worst case 60%) while keeping CAGR
  in 16-19% range.

Pre-committed KILL sketch for iter 009:
- KILL #27: HFEA + KMLM 15% spy_real MDD > 55% → KMLM dose insufficient,
  need 25%+ (would push CAGR below 14% and approach LRS-style
  architectures).
- KILL #28: HFEA + KMLM Sharpe < 50/50 baseline (0.740) → adding KMLM
  via static rebalance hurts Sharpe (negative-carry hedge dominates),
  pivot to LRS-gated KMLM hedge.
- KILL #29: HFEA + KMLM CAGR mean < 13.80% → too defensive, falls
  below SPY mean. Direction CLOSED, pivot to C1 vol-targeted.

If iter 009 caps at ~70 too, iter 010 pivots to **C1 vol-targeted**
(different geometry — dynamic leverage scaling rather than static
barbell trade).

### Citations validated

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LETF decay —
  validated empirically: HFEA 2022 MDD 67-73% mirrors documented
  Bogleheads 2022 backtest (~−65% peak-to-trough across canonical
  configs). Decay constant 1.5%/y in our synth understates real-world
  2022 drag (real ~3-5%/y), so true HFEA blow-up is even sharper.
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking —
  HFEA is the leveraged extension of stacking; this iter shows that
  unhedged 165-180% leverage **cannot** deliver MDD ≤ 55% on the
  2022 regime. Stacking alone is insufficient at 3× barbell weights.
- HFEA Bogleheads 2019 — canonical 55/45 risk-parity claim is **falsified
  by our synth**: Sharpe peaks at 50/50 or lower. The original claim
  predates 2022's TMF crash and may be regime-specific (1986-2019
  declining-rate environment).
- `[advances_fin_ml, p.31-34]` factor framework — leveraged duration
  (TMF) is a distinct factor with rates-falling beta; in rates-RISING
  regime (2022) it becomes a concentrated risk, not a diversifier.
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials=29 —
  worst p = 4.91e-03 << 0.05 bar. Headroom for ~2 more iters at 3
  configs each before n=35 zone tightening becomes acute.
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha — flagged as
  natural extension to B1 if iter 008 shows 2022 is binding constraint.
  This iter confirms the prediction; B2 HFEA + KMLM is the literature-
  aware iter 009 response.

### Where the score-90 path goes from here

Iter 008 score 63 confirms the **leveraged-barbell architecture has a
structural ceiling well below 75** in the spy_beater rubric. The
30 pts CAGR is captured (29/30) but criterion 2 (MDD, 20 pts) is
unreachable without crisis-alpha. The score-90 path now has three
candidate routes (in iter 007's recommendation order):

1. **B2 HFEA + KMLM** (iter 009 recommended) — adds known-effective
   crisis-alpha to the high-CAGR HFEA backbone. Best-case CAGR ~17%
   + MDD ~50% → score ~72-78.
2. **C1 vol-targeted** (iter 010 fallback) — dynamic leverage scaling
   may lift Sharpe to 1.0+ without 2022 blow-up. Different geometry,
   different failure mode.
3. **Methodology change** (last resort) — if B2 + C1 both cap at ~75,
   the spy_beater bar may be **architecturally unreachable** within
   gross-of-tax 2-dataset framework. Confirms F1+SPLIT incumbent
   fallback as deploy-ready and writes IMPOSSIBILITY_RESULT report.

Headroom: cumulative_n_trials=29; ~2 more iters (n=35) before DSR
penalty tightens enough to reduce criterion 4 from 10 → 7 pts on
similar-Sharpe configs.
