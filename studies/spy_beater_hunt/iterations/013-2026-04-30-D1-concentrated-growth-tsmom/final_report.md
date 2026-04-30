# spy_beater_hunt iter 013 — Final Report — `D1-concentrated-growth-tsmom`

**Tier**: **MARGINAL** — `score=59/100`, `winner_conditions_met=True`

**Strict bars** (CAGR-anchored, spy_beater rubric):
- CAGR bar (mean ≥ 13.80%): PASS (mean = 12.83%)
- MDD bar (mean ≤ 40.85%): PASS (mean = 35.27%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Primary citation**: Moskowitz, Ooi, Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 + Faber 2007 GTAA (10m TSMOM equivalent at monthly frequency) + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate-family rationale + [advances_fin_ml, p.222-223] DSR cumulative_n_trials

---

## Selected config: `d1_qqq_6m_tsmom`

Spec:

```json
{
  "type": "lrs",
  "on_weights": {
    "QQQSIM": 1.0
  },
  "off_weights": {
    "IEFSIM": 1.0
  },
  "signal_ticker": "QQQSIM",
  "filter": "momentum",
  "lookback_days": 126,
  "lag_days": 1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 0.791 | 14.10% | 36.49% | 5/7 | 1.94e-05 |
| **spy_real** | 0.766 | 11.56% | 34.04% | 5/7 | 2.99e-03 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| d1_qqq_6m_tsmom | 0.791 | 0.766 |
| d1_qqq_12m_tsmom | 0.792 | 0.704 |
| d1_qld_6m_tsmom | 0.652 | 0.684 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 16 | 30 | mean = 12.83%, bar = 11.21% |
| 2. MDD vs SPY | 12 | 20 | mean = 35.27%, bar = 55.17% |
| 3. Gates | 11 | 20 | per_ds = {'lh_56y': 5, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 2.99e-03, n_trials = 41 |
| 5. Sharpe | 2 | 10 | mean = 0.779 |
| 6. Robustness | 8 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 62.5% | 36.49% |
| 10y | 76.6% | 36.49% |
| 15y | 81.7% | 36.49% |
| 20y | 100.0% | 36.49% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 36

## INCOMPLETE flags

- **Stale bar text in template header**: the "CAGR bar (mean ≥
  13.80%)" / "MDD bar (mean ≤ 40.85%)" labels above are 3-dataset-era
  numbers. The actual evaluation uses 2-dataset bars (lh_56y +
  spy_real): **CAGR ≥ 11.21%, MDD ≤ 55.17%** per the 2026-04-29
  methodology refactor. All 3 bars correctly evaluated against the
  2-dataset framework: d1_qqq_6m_tsmom mean CAGR 12.83% ≥ 11.21% PASS;
  mean MDD 35.27% ≤ 55.17% PASS; gates cross_met=True PASS.
- **TSMOM operationalisation**: implemented as daily check `price[t]
  > price[t-lookback_days]` (Faber/Moskowitz monthly TSMOM equivalent
  at daily granularity). Standard practitioner adaptation; lit canonical
  is monthly check, but daily reduces transaction concentration risk.
- **QQQSIM/QLDSIM coverage**: testfolio cache. QQQSIM ~1985+ (NDX
  inception 1985-10-01, synth pre-1985). QLDSIM models 2× LETF daily
  decay (~1-2%/y baseline).
- **PBO N=3 warning**: G1 PBO 0.99/0.69 is the pre-existing CSCV
  small-N instability — same artefact across all iters with 3 configs.
  Not a D1-specific issue.
- **G3 WF MDD failures (real)**: TSMOM 6m gate has lag during bear
  market entry; walk-forward windows show MDD 36% (lh_56y) / 34%
  (spy_real) > 25% threshold. This is intrinsic to TSMOM lookback lag,
  not a config bug.
- **NEW module**: `momentum_gate` added to `lrs_engine.py` via TDD
  (3 tests added: test_momentum_gate_no_peek_ahead +
  _initial_lookback_false + _lookback_param). Wired into
  `_lrs_returns_from_spec` via `filter="momentum"` + `lookback_days`
  field. 762 → 765 tests baseline preserved. Backwards-compat for
  existing sma/ema/sma_band/ema_band filters unchanged.

## Lesson

### Tier MARGINAL 59/100 — all 3 bars met but score 5th-worst in entire hunt

iter 013 tested D1 (6th distinct architectural family: concentrated
growth on NDX with time-series momentum gate, single-anchor `price[t]
> price[t-lookback]` per Moskowitz/Ooi/Pedersen 2012). **Selected
config** `d1_qqq_6m_tsmom` (1× QQQ ON, IEF OFF, 126-day lookback)
passes all 3 strict bars (CAGR 12.83% ≥ 11.21%, MDD 35.27% ≤ 55.17%,
gates cross_met) but scores **59/100** — **8pts BELOW closest-to-winner
(iter 006/007 = 67)** and 1pt BELOW iter 010 vol-target (60). D1 sits
between C1 vol-target and D2 stacked-equity in the family ceiling
table.

### KILL conditions outcomes

- **KILL #39 (D1 reinforces KILL #33 — 6th family caps ≤ 67) FIRED**:
  best D1 score = 59 << 67 ceiling. Architectural ceiling claim from
  iter 011 **strengthened from 5-family to 6-family evidence**. Hunt
  remains CLOSED, status: closed_no_winner, KILL #33 (architectural
  ceiling) reinforced.
- **KILL #40 (sanity-check breaks ceiling) NOT FIRED**: no D1 config
  scored ≥ 75 (best 59); no D1 config met all 3 bars with score ≥ 75.
  KILL #33 stands. Hunt does NOT reopen.
- **KILL #41 (TSMOM lookback monotonic) NOT FIRED**: Sharpe direction
  is **mixed** across datasets:
  - lh_56y: 6m=0.7912 → 12m=0.7923 (+0.0011, very slight UP)
  - spy_real: 6m=0.7659 → 12m=0.7038 (−0.0621, DOWN)
  - Mixed direction → TSMOM lookback dose-response is **dataset-regime
    dependent** (12m better in 56y window, 6m better in 22y window).
    Direction inconclusive; both viable candidates within rubric.

### Per-config table (mean across datasets)

| config              | mean CAGR | mean MDD | mean Sharpe | bar pass? | score |
|:--------------------|----------:|---------:|------------:|:---------:|------:|
| **d1_qqq_6m_tsmom** | **12.83%**| **35.27%**| **0.779**  | **3/3 ✓** | **59**|
| d1_qqq_12m_tsmom    | 13.46%    | 39.80%   | 0.748       | 3/3 ✓     | ~57   |
| d1_qld_6m_tsmom     | 18.35%    | 62.28%   | 0.668       | 2/3 (MDD✗)| ~55   |

### Closest-to-winner gap (vs iter 006 a6_tqqq_split_kmlm30_tlt10)

| metric         | iter 006 (closest)| iter 013 (d1_qqq_6m_tsmom) | gap     |
|:---------------|------------------:|---------------------------:|--------:|
| score          | 67                | **59**                     | **−8**  |
| mean CAGR      | 17.33%            | 12.83%                     | −4.50pp |
| mean MDD       | 49.73%            | 35.27%                     | **+14.46pp** ⬅ BEST MDD |
| mean Sharpe    | 0.759             | 0.779                      | +0.020  |
| CAGR pts       | 25                | 16                         | **−9**  |
| MDD pts        | 7                 | 12                         | **+5**  |
| Sharpe pts     | 2                 | 2                          | 0       |
| Gates pts      | 13                | 11                         | −2      |
| DSR pts        | 10                | 10                         | 0       |
| Robustness pts | 10                | 8                          | −2      |

D1 trades **−9 CAGR pts for +5 MDD pts and +0.02 Sharpe** within
rubric. Net **−8** under the CAGR-anchored rubric — but interestingly,
**D1 has the BEST mean MDD across all 6 families tested** (35.27% vs
iter 006 closest 49.73%, iter 010 vol-target 41.86%, iter 012 D2
52.65%). TSMOM gate is *more conservative* than 200d SMA gate — fewer
false-positive trend signals → captures fewer drawdowns at cost of
some CAGR.

### Direction implications

- **D1 family CLOSED at score 59**. TSMOM gate + concentrated growth
  architecture is **decisively below 67-ceiling**. Not a viable
  spy_beater path under CAGR-anchored rubric.
- **Notable counterweight finding**: D1 has **best MDD score** in
  entire hunt — under a Sharpe-anchored or MDD-prioritising rubric,
  d1_qqq_6m_tsmom would rank significantly higher. This connects back
  to long_term_portfolio's Sharpe-anchored rubric: F1+SPLIT incumbent
  (mean MDD 16.76%) is a stronger MDD-first solution; D1 here would
  rank between F1+SPLIT and 200d-SMA gate strategies on Sharpe basis.
- **TSMOM vs SMA trade-off**: TSMOM gate captures trend with less
  noise (fewer whipsaw flips) but lags entry/exit more than SMA.
  Result: lower MDD (better drawdown control) but lower CAGR (slower
  re-entry after drawdowns). Architecturally complementary to SMA
  rather than dominant.
- **2× LETF (QLD) + TSMOM gate fails MDD bar**: d1_qld_6m_tsmom mean
  MDD 62.28% > 55.17%, lh_56y 69.18% > 70% almost-bar. Confirms KILL
  #38 finding from iter 012: pure LETF + factor/concentration without
  bonds = catastrophic MDD across LETF leverage levels (2× and 3×).
- **6-family architectural ceiling diagnostic (UPDATED)**:
  | family                  | best score | best Sharpe | best mean MDD |
  |:------------------------|-----------:|------------:|--------------:|
  | A2 TQQQ-track LRS       | **67**     | 0.804       | 49.73%        |
  | A1/A3 SPY-track LRS     | 66         | 0.744       | 51.60%        |
  | B1/B2 HFEA barbell      | 63         | 0.739       | 67.48%        |
  | C1 vol-target           | 60         | 0.721       | 41.86%        |
  | **D1 concentrated+TSMOM**| **59**    | 0.779       | **35.27%** ⬅  |
  | D2 stacked equity       | 52         | 0.738       | 52.65%        |

### Cross-family knowledge added by iter 013

1. **TSMOM gate is more conservative than SMA gate**: trades CAGR
   for MDD. Best MDD (35.27%) in entire hunt is achieved here via
   slow-reaction TSMOM 6m lookback on QQQ.
2. **TSMOM lookback dose-response is dataset-regime dependent**:
   12m wins lh_56y (40y), 6m wins spy_real (22y). Suggests longer
   lookbacks favour very-long-history datasets with multiple regime
   cycles; shorter lookbacks favour shorter recent samples. Validates
   `[advances_fin_ml, p.31-34]` factor framework concern: lookback
   choice introduces selection bias.
3. **NDX-track (D1) has worse score than NDX-track LETF (A2)** under
   CAGR-anchored rubric: D1 1× QQQ + TSMOM = 59; A2 3× TQQQ + 200d
   SMA = 67. Leverage + faster gate beats unleveraged + slower gate
   in this rubric — but at 49.73% MDD (A2) vs 35.27% MDD (D1).
4. **2× LETF (QLD) bridges the LETF vs unleveraged gap badly**:
   d1_qld_6m_tsmom CAGR 18.35% (close to TQQQ track) but MDD 62.28%
   (worse than UPRO 3× track). 2× LETF combines worst-of-both at this
   leverage level on TSMOM gate.

### Surprising findings

1. **D1 has BEST mean MDD across all 6 families tested** (35.27%).
   TSMOM gate's slower reaction (vs SMA) actually helps MDD by
   avoiding false-positive re-entries after partial recoveries during
   bear markets. Counter-intuitive vs literature suggestion that SMA
   "reacts faster = better drawdown control".
2. **G3 WF MDD failures persistent**: lh_56y 36.49% / spy_real 34.04%
   both > 25% threshold. TSMOM 6m gate has 1-2 month entry lag during
   bear market starts; walk-forward windows including 2008 GFC show
   sustained MDD > 25%. Sub-period MDD is structurally above gate
   threshold.
3. **5y robustness 62.5%** is LOW — D1 underperforms SPY in low-vol
   bull regimes (similar to D2 finding). Concentrated NDX + IEF
   off-sleeve produces inconsistent 5y windows because OFF state
   spends meaningful time in IEF (low-yield bonds) during bull markets.

### Path to 90 (D1 architecture)

**Architecturally unreachable** (KILL #33 framework). Best D1 score 59
→ gap 31 to score 90. Maximum plausible single-criterion lift:
CAGR +14 (16→30, requires CAGR ≥ 20% — needs LETF leverage which
fails MDD via QLD test) + MDD +8 (12→20, mean MDD ≤ 15% — physically
impossible at NDX exposure ≥ 50%) + Sharpe +8 + Gates +9 +
Robustness +2 = **+41 pts** at independent-maxima. Optimistic ceiling
100. Real Pareto-feasible ceiling ≈ 70 (CAGR↔MDD trade-off seen in
QLD config: +5pp CAGR brings +27pp MDD).

D1 ceiling lower than 5 prior families under CAGR-anchored rubric;
HIGHER than all 5 under Sharpe-anchored or MDD-anchored rubric.
Confirms KILL #33: rubric choice does not change underlying
infeasibility; under spy_beater rubric specifically, score 90 is
unreachable.

### Why this iter was worth doing despite hunt being CLOSED

iter 011 INCOMPLETE flags listed Tier 3 D1/C2/D2 as untested. Iter 012
tested D2 (5th family, score 52). This iter (013) tests D1 (6th family,
score 59). Closing both D1 and D2 strengthens the negative-result
policy claim from "5 families, 56 cumulative iters" to **"6 families,
57 cumulative iters"** — robust enough for mandate §1 confirmation.

DSR cumulative_n_trials = **41**, worst p-value = 2.99e-03 << 0.05.
Statistical confidence preserved.

Additional positive: D1 surfaced the **best-MDD strategy in the entire
spy_beater hunt** (35.27%, d1_qqq_6m_tsmom), which has independent
value as a candidate for an MDD-first rubric — could potentially
inform Sharpe-first / MDD-first variant studies in long_term_portfolio
follow-on work if user requests.

### Suggested iter 014+ (none — hunt remains CLOSED)

C2 CAPE-timing remains the only Tier 3 family untested. Per
PROMISING_DIRECTIONS.md: "CAPE has been 'high' for 20+ years and
timing has been wrong. Out-of-sample reliability questionable." Per
KILL #39 firing across 6 families, additional Tier 3 testing would
NOT change the architectural-ceiling conclusion. Hunt remains CLOSED.

If user requests further sanity checks (C2 CAPE-timing or D1
sensitivity sweep), template would be similar 3-config sanity-check
format with KILL #42+ pre-committed.

### Citations validated by iter 013

- Moskowitz, Ooi, Pedersen (2012) "Time Series Momentum" JFE
  104(2):228-250 — TSMOM gate canonical 12m lookback. Tested at 6m
  and 12m; both produce viable strategies but neither breaks score-67
  ceiling.
- Faber 2007 "A Quantitative Approach to Tactical Asset Allocation"
  (GTAA) — 6m TSMOM at monthly frequency equivalent. Daily
  operationalisation here produces similar regime-detection behaviour.
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed gate-family
  rationale — TSMOM is structurally complementary to 200d SMA (slower
  reaction, better drawdown control, lower CAGR).
- `[advances_fin_ml, p.31-34]` factor framework — gate-family
  dimension distinct from leverage/regime axes already explored;
  lookback choice introduces selection bias (validated by mixed
  6m/12m direction across datasets).
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 41, worst
  p = 2.99e-03 << 0.05 bar; statistical confidence preserved.
- `[advances_fin_ml, p.208-211]` PBO grid-level — N=3 warning
  pre-existing; CSCV unstable at small N but cross-config selection
  bias controlled at iter level.
- `[advances_fin_ml, p.196-202]` bootstrap CI — gate G6 99.9% CI low
  > 0 (passed for d1_qqq_6m_tsmom: lh_56y 0.3255, spy_real 0.0841).

### Status

**`spy_beater_hunt: status: closed_no_winner`** REMAINS as of 2026-04-30.

- Total iters: 13 / 50 target (closed at iter 011, sanity-checked at iter 012/013)
- Cumulative n_trials: 41
- KILL #33 (architectural ceiling) **REINFORCED across 6 families**
- KILL #39 fired (D1 ≤ 67)
- KILL #40 NOT fired (no D1 config ≥ 75)
- KILL #41 NOT fired (Sharpe direction mixed across datasets)
- F1+SPLIT incumbent fallback deploy-ready
- Mandate §1 100% Plano C unchanged
- **Notable**: D1 d1_qqq_6m_tsmom is the **best-MDD strategy in the
  entire spy_beater hunt** (35.27% mean MDD) — useful artefact even
  though it doesn't break score ceiling.

