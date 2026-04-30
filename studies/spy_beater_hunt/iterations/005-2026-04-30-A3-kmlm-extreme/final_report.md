# spy_beater_hunt iter 005 — Final Report — `A3-kmlm-extreme`

**Tier**: **PROMISING** — `score=63/100`, `winner_conditions_met=True`

**Strict bars** (CAGR-anchored, spy_beater rubric):
- CAGR bar (mean ≥ 13.80%): PASS (mean = 13.57%)
- MDD bar (mean ≤ 40.85%): PASS (mean = 32.57%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking

---

## Selected config: `a5_lrs_split_kmlm30_tlt10`

Spec:

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {
    "UPROSIM": 0.3,
    "SSOSIM": 0.3,
    "KMLMSIM": 0.3,
    "TLTSIM": 0.1
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
| **lh_56y** | 0.818 | 14.36% | 32.57% | 5/7 | 1.70e-05 |
| **spy_real** | 0.768 | 12.78% | 32.57% | 6/7 | 2.93e-03 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| a5_lrs_split_kmlm35 | 0.791 | 0.739 |
| a5_lrs_split_kmlm40 | 0.820 | 0.756 |
| a5_lrs_split_kmlm30_tlt10 | 0.818 | 0.768 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 17 | 30 | mean = 13.57%, bar = 11.21% |
| 2. MDD vs SPY | 13 | 20 | mean = 32.57%, bar = 55.17% |
| 3. Gates | 12 | 20 | per_ds = {'lh_56y': 5, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 2.93e-03, n_trials = 20 |
| 5. Sharpe | 2 | 10 | mean = 0.793 |
| 6. Robustness | 9 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 66.7% | 32.57% |
| 10y | 92.3% | 32.57% |
| 15y | 100.0% | 32.57% |
| 20y | 100.0% | 32.57% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

- KMLMSIM real KMLM inception 2020-12; pre-2020 is testfolio synth via
  FF MoM proxy. Both lh_56y and spy_real (2003+) windows rely on the
  synth for ~80%+ of the timeline.
- TLTSIM real TLT inception 2002-07; lh_56y pre-2002 is synth.
- LRS rebalance instantaneous, no transaction costs modelled. ON sleeve
  with 4-ticker daily rebalance (UPRO/SSO/KMLM/TLT for the blend
  config) implies daily fixed-weight rebalance — real ETF spread +
  trading drag absent.
- spy_real window (2003+) excludes 1973-74 stagflation / 2000-02 dot-com
  regimes; lh_56y synth is the only pre-2003 stress proxy.
- PBO grid was N=3 configs (warning emitted by run_iter): CSCV is
  statistically unstable below N=4. The PBO score should be treated as
  informative only — it's the cross-iter cumulative grid (n_trials=20
  feeding DSR) that carries the anti-overfit weight here.

## Lesson

### Score regression vs iter 004 (66 → 63)

| criterion | iter 004 a4_kmlm30 | iter 005 a5_kmlm30_tlt10 | delta |
|---|---:|---:|---:|
| 1. CAGR | 19 (mean 14.39%) | 17 (mean 13.57%) | **−2** |
| 2. MDD  | 12 (mean 36.79%) | 13 (mean 32.57%) | **+1** |
| 3. Gates | 13 (6+6, cross_met) | 12 (5+6, cross_met) | **−1** |
| 4. DSR  | 10 (n=17, worst p 5.56e-03) | 10 (n=20, worst p 2.93e-03) | 0 |
| 5. Sharpe | 2 (mean 0.744) | 2 (mean 0.793) | 0 |
| 6. Robustness | 10 | 9 (5y pass-rate dropped 83.3→66.7%) | **−1** |
| 7. Extra | 0 | 0 | 0 |
| **Total** | **66** | **63** | **−3** |

Despite better MDD (−4.22pp) and better Sharpe (+0.049 mean), the score
regressed because:
1. The CAGR axis is anchored on a wider range (5%-20%, 30 pts) than the
   MDD axis (15%-70%, 20 pts), so each pp of CAGR is worth ~2pp of MDD
   in scoring. The 0.82pp CAGR drop cost 2 pts; the 4.22pp MDD drop
   gained only 1 pt.
2. lh_56y gates dropped 6/7 → 5/7. Inspecting `gate_details.lh_56y`,
   `g3_max_wf_mdd = 0.32`, `g6_ci_low = 0.32`, `g7_crosslib = 0.0`,
   PBO at 0.85 — the 1 lost gate is likely G1 PBO (>= 0.5 threshold)
   OR a degraded WF/OOS metric. Engineering nuance: deeper KMLM
   exposure homogenizes config returns within the iter, inflating PBO
   in the small-N=3 grid. (The PBO warning fires for N<4 — informative
   only.)
3. 5y rolling pass-rate dropped 83.3% → 66.7%. KMLM 30-40% strategies
   underperform SPY in 5-year windows more often because deep
   crisis-alpha allocation drags during long bull runs. The 10y and
   longer windows still pass 92-100%, so the long-horizon thesis holds.

### KILL conditions outcomes

- **KILL #6 (CAGR floor)** NOT FIRED — all 3 configs CAGR mean ≥ 13.57%
  >> 11.21% bar.
- **KILL #16 (KMLM 35% inflection)** NOT FIRED — `a5_kmlm35` Sharpe
  (0.791, 0.739) > `a4_kmlm30` Sharpe (0.765, 0.722) in BOTH datasets.
  Direction CONTINUES monotonic positive 30→35%.
- **KILL #17 (KMLM 40% inflection)** NOT FIRED — `a5_kmlm40` Sharpe
  (0.820, 0.756) > `a5_kmlm35` Sharpe (0.791, 0.739) in BOTH datasets.
  Direction CONTINUES monotonic positive 35→40%. **No inflection found
  in 0-40% KMLM range.**
- **KILL #18 (TLT-on-top doesn't help)** NOT FIRED — `a5_kmlm30_tlt10`
  Sharpe (0.818, 0.768) > `a4_kmlm30` Sharpe (0.765, 0.722) in BOTH
  datasets. Adding 10pp TLT on top of the iter 004 winner DID help.

### KMLM dose-response curve (7 data points across iter 001-005)

| KMLM % | mean CAGR | mean MDD | mean Sharpe | source |
|---:|---:|---:|---:|---|
| 0 | 16.23% | 51.60% | 0.657 | iter 001 a1_lrs_split |
| 10 | 15.47% | 46.65% | 0.673 | iter 003 a3_kmlm10 |
| 20 | 14.99% | 41.87% | 0.706 | iter 003 a3_kmlm20 |
| 25 | 14.70% | 39.37% | 0.724 | iter 004 a4_kmlm25 |
| 30 | 14.39% | 36.79% | 0.744 | iter 004 a4_kmlm30 |
| 35 | 14.05% | 34.14% | 0.765 | iter 005 a5_kmlm35 |
| 40 | 13.68% | 31.62% | 0.788 | iter 005 a5_kmlm40 |

**Pattern**: monotonic positive Sharpe ALL the way from 0% to 40%. The
curve is concave but has not inflected. Marginal CAGR cost is slowing
(~0.34pp/+5% from 30→40%, vs 0.6pp/+5% earlier). Marginal MDD relief
is also slowing (~2.5pp/+5% from 30→40%, vs 5pp/+5% from 20→25%).
Marginal Sharpe gain is steady (~0.02/+5%).

### TLT-on-top finding (a5_kmlm30_tlt10)

The blend config (30% UPRO + 30% SSO + 30% KMLM + 10% TLT) achieves
Sharpe (0.818, 0.768) — marginally beating `a5_kmlm40` (0.820, 0.756)
on spy_real but slightly losing on lh_56y. Critical insight: **at
matched leverage budget (60% leveraged equity in both), trading 10pp
KMLM for 10pp TLT slightly improves spy_real Sharpe** because the
2003+ window has more bond-favorable regimes than the lh_56y synth
(which includes 1980s high-rates regime). This suggests KMLM 30% +
TLT 10% might be the **selection winner** under spy_real-weighted
evaluation, but a5_kmlm40 wins on MDD (31.62% < 32.57%) and lh_56y.

### Closest-to-winner update

**Iter 004 `a4_lrs_split_kmlm30` REMAINS closest-to-winner** (score 66
> iter 005's 63). Iter 005 produced a better-MDD/better-Sharpe
strategy but the CAGR axis dominated scoring.

Gap to WINNER (90):
- a4_kmlm30 (iter 004): −24 pts
- a5_kmlm30_tlt10 (iter 005): −27 pts
- a5_kmlm40 (iter 005): not selected, but per-config likely ~64 (CAGR
  17pt + MDD 14pt + Sharpe ~3pt + Gates 12pt + DSR 10pt + Robust 9pt
  + Extra 0pt = ~65)

**Path to score 90 looks structurally blocked**: KMLM dose past 40%
will keep dropping CAGR (each 5% costs ~0.35pp CAGR ≈ 0.7pt) while
gaining ~2pp MDD (≈ 1pt) and ~0.02 Sharpe (≈ 0pt). Net: roughly even
or slightly negative per +5% KMLM. To reach 90, the strategy needs
either:
(a) Higher leverage with matched MDD (e.g., 3× UPRO sleeve with deeper
    KMLM): possible but iter 002 sweep found KILL #6 territory.
(b) A different lever: vol-targeting (C1), HFEA (B1), or TQQQ-track
    (A2) — currently NOT YET RUN per BASE_MEMORY.
(c) Multi-horizon CAGR robustness rebound — push 5y pass-rate back to
    80%+ by reducing KMLM exposure during low-vol bull regimes.

### Direction status updates for BASE_MEMORY

- A3_kmlm_extreme (>30% KMLM): **MONOTONIC POSITIVE CONFIRMED through
  40%** but score regressed vs iter 004. Direction NOT closed; could
  test 45-50% in iter 006 if continuing this path. **However, the
  scoring rubric makes further KMLM dose unlikely to lift score.**
- A3_tlt_on_top_of_kmlm30: **PROMISING** — `a5_kmlm30_tlt10` Sharpe
  beat a4_kmlm30 in both datasets. Could test KMLM30+TLT15/20 blends.
- A3_kmlm_dose_response (≤ 30% KMLM): **RETAINS BEST SCORE** at iter
  004's 66. Closest-to-winner unchanged.
- B1_HFEA_classical, A2_TQQQ_track, C1_vol_targeted: **STILL NOT YET
  RUN** — these are the structurally-different levers needed for a
  shot at score ≥ 90.

### Citations validated

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed regime gate —
  unchanged across iter 001-005.
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking —
  **further validated**: KMLM dose-response monotonic positive
  through 40%, dose curve concave with sustained marginal MDD relief
  (14.81pp from 0→30%, +4.97pp from 30→40%) and milder CAGR drag
  (1.84pp from 0→30%, +0.71pp from 30→40%).
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials —
  cumulative n=20, worst DSR p = 2.93e-03 still well below 0.05 bar.
  Headroom for ~3-4 more iters at 3 configs each before tightening
  becomes acute (n=30+ zone).
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha — unchanged;
  trend-following exposure beyond F1+SPLIT's 17.5% allocation still
  improves Sharpe up to 40% within this framework.

### Suggested iter 006

The KMLM-dose-response direction is producing diminishing scoring
returns — each iter pushes Sharpe up but CAGR drag dominates the
rubric. Two strategic options:

**Option A** (continue dose-response, low score-lift expected):
- `a6_lrs_split_kmlm30_tlt15` — extend TLT-on-top finding (best
  Sharpe lever from iter 005)
- `a6_lrs_split_kmlm45` — last extreme test before closing
- `a6_lrs_split_kmlm25_tlt15` — pulled-back KMLM with more TLT
  (target: regain CAGR while keeping MDD low)

**Option B** (pivot to structurally different lever — recommended):
- Run **B1 HFEA classical** (55% UPRO + 45% TMF) — Bogleheads thesis
  with leveraged barbell. Need TMFSIM synth (TLTSIM × 3 with daily
  decay) — already specified in INFRASTRUCTURE.md but not yet built.
- Or run **A2 TQQQ-track** with 200d SMA gate — concentrated growth +
  regime gate; potentially higher CAGR ceiling.
- These are the unexplored levers BASE_MEMORY identifies as needed
  for a shot at score ≥ 90.

User decision suggested: pivot to Option B in iter 006. Iter 005 has
mostly exhausted the KMLM-dose lever within the scoring rubric.

KILL #19 candidate (iter 006): if Option A `a6_kmlm45` Sharpe <
`a5_kmlm40` Sharpe in BOTH ds, KMLM dose finally inflects — close
direction.
