# spy_beater_hunt iter 004 — Final Report — `A3-kmlm-dose-response`

**Tier**: **PROMISING** — `score=66/100`, `winner_conditions_met=True`

**Strict bars** (CAGR-anchored, spy_beater rubric):
- CAGR bar (mean ≥ 13.80%): PASS (mean = 14.39%)
- MDD bar (mean ≤ 40.85%): PASS (mean = 36.79%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking

---

## Selected config: `a4_lrs_split_kmlm30`

Spec:

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {
    "UPROSIM": 0.35,
    "SSOSIM": 0.35,
    "KMLMSIM": 0.3
  },
  "off_weights": {
    "IEFSIM": 1.0
  },
  "signal_ticker": "SPYSIM",
  "lag_days": 1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 0.765 | 15.13% | 37.39% | 6/7 | 6.53e-05 |
| **spy_real** | 0.722 | 13.65% | 36.20% | 6/7 | 5.56e-03 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| a4_lrs_split_kmlm25 | 0.741 | 0.706 |
| a4_lrs_split_kmlm30 | 0.765 | 0.722 |
| a4_lrs_split_tlt20 | 0.724 | 0.698 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 19 | 30 | mean = 14.39%, bar = 11.21% |
| 2. MDD vs SPY | 12 | 20 | mean = 36.79%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 5.56e-03, n_trials = 17 |
| 5. Sharpe | 2 | 10 | mean = 0.744 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 83.3% | 37.39% |
| 10y | 100.0% | 37.39% |
| 15y | 100.0% | 37.39% |
| 20y | 100.0% | 37.39% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

- KMLMSIM real KMLM inception 2020-12; pre-2020 is testfolio synth via
  FF MoM proxy. Both lh_56y and spy_real (2003+) windows rely on the
  synth for ~80%+ of the timeline.
- TLTSIM real TLT inception 2002-07; lh_56y pre-2002 is synth.
- LRS rebalance instantaneous, no transaction costs modelled. Multi-ticker
  ON sleeves (UPRO/SSO/KMLM at 35/35/30) imply daily fixed-weight
  rebalance — real ETF spread + trading drag absent.
- spy_real window (2003+) excludes 1973-74 stagflation / 2000-02 dot-com
  regimes; lh_56y synth is the only pre-2003 stress proxy.
- PBO grid was N=3 configs (warning emitted by run_iter): CSCV is
  statistically unstable below N=4. The PBO score should be treated as
  informative only — it's the cross-iter cumulative grid (n_trials=17
  feeding DSR) that carries the anti-overfit weight here.

## Lesson

### Score lift over iter 003 (a3_lrs_split_kmlm20, 64/100)

| criterion | iter 003 a3_kmlm20 | iter 004 a4_kmlm30 | delta |
|---|---:|---:|---:|
| 1. CAGR | 20 (mean 14.99%) | 19 (mean 14.39%) | −1 |
| 2. MDD  | 10 (mean 41.87%) | 12 (mean 36.79%) | **+2** |
| 3. Gates | 13 (6+6, cross_met) | 13 (6+6, cross_met) | 0 |
| 4. DSR  | 10 (n=14, worst p 1.39e-02) | 10 (n=17, worst p 5.56e-03) | 0 |
| 5. Sharpe | 1 (mean 0.705) | 2 (mean 0.744) | **+1** |
| 6. Robustness | 10 | 10 | 0 |
| 7. Extra | 0 | 0 | 0 |
| **Total** | **64** | **66** | **+2** |

The MDD continued to drop (5.08pp from 41.87% → 36.79%) and Sharpe lifted
mechanically (mean 0.705 → 0.744, +0.04). CAGR drag was only 0.60pp from
KMLM 20% → 30%, much milder than the 1.24pp drag from 0% → 20% in iter
003. **KMLM dose-response is monotonic positive ALL THE WAY from 0% to
30%, and the dose curve is concave (diminishing CAGR drag, sustained
MDD relief)** — this is the structural pattern that mirrors the F1+SPLIT
incumbent's KMLM 17.5% choice but goes substantially further.

### KILL conditions outcomes

- **KILL #6 (CAGR floor)** NOT FIRED — all 3 configs CAGR ≥ 14.39% >> 11.21% bar.
- **KILL #13 (KMLM inflection at 25%)** NOT FIRED — `a4_kmlm25`
  Sharpe (0.741, 0.706) > `a3_kmlm20` Sharpe (0.719, 0.692) in BOTH
  datasets. Direction CONTINUES monotonic positive 20→25%.
- **KILL #14 (KMLM 30% vs 25% inflection)** NOT FIRED — `a4_kmlm30`
  Sharpe (0.765, 0.722) > `a4_kmlm25` Sharpe (0.741, 0.706) in BOTH
  datasets. Direction CONTINUES monotonic positive 25→30%. **Try 35%
  and 40% in iter 005 to find the actual inflection point.**
- **KILL #15 (TLT 20% structurally dominated by KMLM 20%)** NOT FIRED —
  `a4_tlt20` Sharpe (0.724, 0.698) actually slightly EXCEEDS `a3_kmlm20`
  Sharpe (0.719, 0.692) in BOTH datasets, though TLT 20% MDD (42.59%)
  is marginally worse than KMLM 20% MDD (41.87%). However, KMLM
  scales further (KMLM 25/30% beat TLT 20% on both Sharpe AND MDD), so
  KMLM is the better dose-response asset. TLT direction NOT closed —
  could test TLT 25-30% or KMLM+TLT blends in iter 006+.

### KMLM dose-response curve (4 data points across iter 003 + 004)

| KMLM % | mean CAGR | mean MDD | mean Sharpe | source |
|---:|---:|---:|---:|---|
| 0 | 16.23% | 51.60% | 0.657 | iter 001 a1_lrs_split |
| 10 | 15.47% | 46.65% | 0.673 | iter 003 a3_kmlm10 |
| 20 | 14.99% | 41.87% | 0.706 | iter 003 a3_kmlm20 |
| 25 | 14.70% | 39.37% | 0.724 | iter 004 a4_kmlm25 |
| 30 | 14.39% | 36.79% | 0.744 | iter 004 a4_kmlm30 |

**Pattern**: marginal cost ~0.6pp CAGR per +5% KMLM, marginal benefit
~2.5-5pp MDD per +5% KMLM. Sharpe rises monotonically. The curve has
not inflected — KMLM 35% and 40% are unexplored zones.

### Closest-to-winner update

Iter 004 `a4_lrs_split_kmlm30` is the **new closest-to-winner**:
- Bars 3/3 PASS (CAGR 14.39%, MDD 36.79%, gates 6+6 cross_met)
- Score 66/100 (PROMISING; tier WINNER requires score ≥ 90)
- Gap to WINNER: −24 pts. Realistic levers remaining:
  - **MDD pts 12 → 16+** (target MDD ~25-30%): plausible via KMLM 35-40%
    if monotonic continues. But CAGR drag may push mean below SPY bar.
  - **CAGR pts 19 → 23-25** (target CAGR ~16-17%): difficult — KMLM dose
    inversely related; would need a different lever (e.g., concentrated
    growth or stronger leverage) which conflicts with MDD goal.
  - **Sharpe pts 2 → 5+** (target mean Sharpe ~0.95): follows MDD drop
    mechanically. At KMLM 30% Sharpe is 0.744; needs +0.21 to hit 0.95.
- Realistic ceiling for this strategy family looks like **70-75 in 2-3
  more iters** if the dose-response continues. Still short of WINNER 90.
  Pure A3 KMLM-extended pathway alone unlikely to deliver WINNER; a
  structurally different idea (vol-targeting, momentum overlay, or
  TQQQ-track) probably needed for the final +20-25 pts.

### Direction status updates for BASE_MEMORY

- A1_200d_SMA_3x_UPRO: **CLOSED** (was iter 001's closest, displaced by
  iter 003's KMLM20 then iter 004's KMLM30).
- A2_lower_leverage (2× SSO): **CLOSED** (iter 002 bars 3/3 but score < 60).
- A3_mixed_gayed_crisis_alpha (KMLM 10-20%): **DOMINATED** by KMLM 30%
  (iter 004); same structural pattern, lower scores.
- **A3_kmlm_dose_response (>20% KMLM)**: **PROMISING (best so far)** —
  KMLM 30% is new closest-to-winner. Direction NOT closed; iter 005
  should probe 35% and 40%.
- A3_kmlm_extreme (>30% KMLM): **NEW PROMISING** — dose curve has not
  inflected; iter 005 should test the inflection point.
- A3_tlt_dose_response: **PROMISING but subordinate to KMLM** — TLT 20%
  marginally beats KMLM 20% on Sharpe but loses on MDD; KMLM scales
  better. Could revisit with TLT + KMLM blend in iter 006+.
- B1_HFEA_classical, A2_TQQQ_track, C1_vol_targeted: not yet run.

### Citations validated

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed regime gate —
  unchanged across iter 001-004.
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking —
  **further validated**: the KMLM dose-response curve shows consistent
  marginal benefit across 0-30% range. The pattern matches Carlson's
  rationale that uncorrelated trend-following (CTA-style) absorbs
  drawdowns from a leveraged equity sleeve without proportional CAGR
  cost.
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials —
  cumulative n=17, worst DSR p = 5.56e-03 still well below 0.05 bar.
  Headroom for ~3-4 more iters at 3 configs each before tightening
  becomes acute (n=27-30 zone).

### Suggested iter 005

**Direction**: A3 KMLM dose-response — probe inflection point.

Candidate configs (3 to maintain n_trials growth at 3 per iter):
- `a5_lrs_split_kmlm35` — ON: 32.5% UPRO + 32.5% SSO + 35% KMLM
- `a5_lrs_split_kmlm40` — ON: 30% UPRO + 30% SSO + 40% KMLM
- `a5_lrs_split_kmlm30_tlt10` — ON: 30% UPRO + 30% SSO + 30% KMLM + 10% TLT
  (tests whether adding TLT on top of best KMLM 30% gives further MDD relief)

KILL #16 candidate: KMLM 35% inflection — if `a5_kmlm35` Sharpe <
`a4_kmlm30` Sharpe in BOTH datasets, the inflection is between 30-35%.
KILL #17: if `a5_kmlm40` Sharpe < `a5_kmlm35`, inflection is 35-40%.
KILL #18: if `a5_kmlm30_tlt10` Sharpe < `a4_kmlm30` Sharpe in BOTH ds,
TLT-on-top-of-KMLM doesn't help → close that direction.
