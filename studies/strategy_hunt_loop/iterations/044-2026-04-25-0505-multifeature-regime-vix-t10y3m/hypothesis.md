# Iteration 044 — Multi-feature composite regime gate (VIX + T10Y3M)

## Hypothesis

iter 041 (TOP-K #1, score 84) modulates iter 037's 3-leg static stack
(0.70 SPY + 0.40 IEF + 0.40 GLD calm; 0.30 SPY + 0.55 IEF + 0.55 GLD
stress) with a single-feature binary VIX gate at level 20. iter 042
and iter 043 both attempted to perturb the GATE TIMING (amplify
asymmetry, halve crossings via hysteresis) and both regressed
(74 / 79 vs 84). The joint lesson from iter 042+043 — encoded in
DEAD_ENDS.md and BASE_MEMORY's "84-STRONG ceiling" entry — is that
**iter 041's gate timing IS a local DSR optimum on a narrow ridge**:
any timing perturbation introduces a different variance source (path
variance from leverage swings; regime-lag variance from delayed
transitions) that dominates the gain.

The remaining axis is **information per bar at the gate computation**
— add a SECOND independent macro feature whose innovations are largely
orthogonal to VIX, so that the regime label has higher precision per
crossing without introducing any new variance source. The natural
candidate is the **3-month / 10-year Treasury term spread (T10Y3M)**:

- It is a leading recession/credit-stress indicator with a long
  empirical track record (Estrella-Hardouvelis 1991; Bauer-Mertens
  2018) — regime mechanism orthogonal to VIX's spot risk-aversion.
- T10Y3M innovations have low daily correlation with VIX innovations
  (typically |ρ| < 0.20 on daily Δ), so the composite stress score
  carries genuine extra signal.
- It is daily-frequency in `data/external/macro/t10y3m_daily.parquet`
  (FRED), covering 1982-2026 — fully overlaps all 3 datasets.

The construction is a deterministic (no fitting) **multi-feature
composite stress score** computed entirely from past data:

```
z_VIX_t   = (VIX_t   - μ_VIX(252d)) / σ_VIX(252d)         # rolling 252d expanding
z_neg_T_t = (-T10Y3M_t - μ(-T)(252d)) / σ(-T)(252d)
s_t       = 0.5 * z_VIX_t + 0.5 * z_neg_T_t              # equal-weight composite
regime_t  = 1 (calm) if s_{t-1} <  τ
            0 (stress) if s_{t-1} >= τ
            with τ = 0.0 (median split of 2-feature composite)
```

then apply iter 041's same calm/stress weights with the same 1-day lag.
This is iter 041's gate generalised from one feature (VIX level vs 20)
to a TWO-feature standardised composite — same instantaneous-update
property (the iter 041 lesson), no fitting (no lookahead concern, no
free CPCV), and one extra orthogonal info source per bar.

When `T10Y3M` is set to its long-run mean (so `z_neg_T = 0`), the
classifier reduces to a single-feature VIX-z-score gate — a strict
generalisation. When the equal-weight composite is replaced by
"VIX level vs 20 fixed", iter 041 is recovered exactly. This is the
**identity-reduction TDD spec** (see test file).

## Primary citation

`[advances_fin_ml, ch.17-18]` — López de Prado on multi-feature regime
detection: when the regime classifier is informative, increasing
feature density should monotonically improve the posterior precision,
and the posterior precision is the correct conditioning variable for
state-conditional weights. The iter 041 single-feature gate is a
1-feature special case; iter 044 is the 2-feature generalisation.

## Additional citations

- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack
  with regime-conditional weights at preserved leverage (same as iter
  041; the 3-leg base stays).
- `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (1-day shift
  on the regime label; rolling z-score uses past 252 days only).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials; the
  worst-p deflator is the criterion this iter targets (iter 041 0.168
  → goal 0.10-0.13).
- Estrella, A.; Hardouvelis, G.A. (1991). "The Term Structure as a
  Predictor of Real Economic Activity". *Journal of Finance* 46(2),
  555-576. DOI 10.1111/j.1540-6261.1991.tb04617.x — canonical
  reference for the term spread as a recession leading indicator.
- Bauer, M.D.; Mertens, T.M. (2018). "Economic Forecasts with the
  Yield Curve". FRBSF Economic Letter 2018-07. URL
  https://www.frbsf.org/economic-research/publications/economic-letter/2018/march/economic-forecasts-with-yield-curve/
  — modern empirical evidence that T10Y3M outperforms T10Y2Y for
  recession forecasting; supports daily-frequency use.
- Whaley (2009), JPM 35(3), 98-105, DOI 10.3905/JPM.2009.35.3.098 —
  VIX as ex-ante risk regime indicator (preserves iter 041 base).
- Bekaert, G.; Hoerova, M. (2014). "The VIX, the Variance Premium and
  Stock Market Volatility". *J. Econometrics* 183(2), 181-192. SSRN
  2294327 — VIX risk-aversion decomposition; orthogonality argument
  to bond-market signals like T10Y3M.
- Hamilton, J.D. (1989). "A New Approach to the Economic Analysis of
  Nonstationary Time Series and the Business Cycle". *Econometrica*
  57(2), 357-384. DOI 10.2307/1912559 — foundational regime-switching
  framework; iter 044's gate is a deterministic instantaneous Markov
  classifier with 2 emission features (no transition prior).
- Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 — gold's
  strategic role (preserves iter 037-041 GLD leg).
- Asness-Moskowitz-Pedersen (2013), JF 68(3), DOI 10.1111/jofi.12021
  — orthogonality of equity / bond / commodity risk premia (preserves
  iter 037-041 3-leg construction).

## Edge source

iter 041 misclassifies regime around the VIX-20 threshold: VIX can
spike to 21-22 on intraday ECB headline noise (no actual macro shift),
or sit at 18-19 during a yield-curve inversion building toward
recession. A VIX-only gate flips on/off based on noise; a
VIX+T10Y3M composite stress score requires BOTH the spot risk
indicator AND the bond-market recession signal to lean stress before
flipping to defensive weights. The orthogonality of T10Y3M (low
daily-Δ correlation with VIX) means each feature contributes
independent variance reduction at the regime label, raising the
information per bar at the gate without changing the gate's
instantaneous-update property.

What SPY 1x b&h misses: the same thing iter 041 captures — regime-
conditional weight tilts during high-stress / inverted-curve periods
that recover the equity exposure cost via uplifted bond + gold tilts.
The 044 delta over 041 is specifically the **information density at
the regime label**, not the mechanism class.

## Datasets

- **educational**: SPY+IEF+GLD 21y (2004-11-19 → 2026-04-15, GLD-aligned;
  same window iter 035-041). Tests the 2008/2018/2020 stress regimes
  with both VIX and T10Y3M moving simultaneously (corroborated signal)
  vs spurious VIX spikes.
- **spy_real**: SPY+IEF+GLD 17y post-GFC (2009-06-25 → 2026-04-15).
  Tests post-2009 era when T10Y3M inverted in 2019 and 2022-2023 —
  classic test of the term-spread leading indicator.
- **ndx_real**: QQQ+IEF+GLD 16y tech-heavy (2010-02-12 → 2026-04-15).
  Tech is more sensitive to rate regime; T10Y3M signal should add
  more value here than on SPY.

## Kill criteria (pre-committed)

| kill | description | observable | threshold | interpretation |
|---|---|---|---|---|
| **A** | Sharpe regression vs iter 041 | Δ Sharpe vs iter 041 < −0.05 on ≥ 2 datasets | ≥ 2 of 3 | Multi-feature gate destructively interferes with iter 041 |
| **B** | DSR no improvement vs iter 041 | worst DSR p-value across 3 datasets | ≥ 0.168 | "Info per bar" hypothesis FALSIFIED — adding T10Y3M adds zero DSR uplift |
| **C** | MDD breach on any dataset | MDD vs benchmark + 5pp | any 1 of 3 datasets breached | Multi-feature gate fails to protect tail |
| **D** | Score regression vs iter 041 | total_score | < 84 | Strict no-regression rule (iter 041 ceiling defended) |
| **E** | G7 cross-lib breach | max diff numpy_ref vs pandas engine CAGR | > 3.0 pp | Engine bug — composite gate construction differs across libs |
| **F** | Excessive churn | regime_round_trips_per_year on any dataset | > 12 | Composite gate is overfitting noise (way more transitions than iter 041's ~7-8/yr) |

**The hypothesis is CONFIRMED if Kill B and Kill D both stay clean.**
Kill A clean alone is insufficient — the question is whether adding
T10Y3M information to the gate computation lowers the worst DSR
p-value below iter 041's 0.168. If yes, the "info per bar" lesson is
confirmed and the path to break the 84 ceiling is opened (iter 045+
can stack additional orthogonal features).

If Kill B fires (DSR worst-p ≥ 0.168), then **the 84 ceiling is robust
to multi-feature gates as well** — the next axis to attack is
*architecture* (out-of-family return stream addition: factor timing,
cross-sectional momentum, options skew) rather than gate enrichment.

## Expected budget

- **Configs to test**: 1 (single pre-committed cfg, no grid, no sweep)
- **Wall-time**: ~30-45 minutes (3 datasets × 1 cfg, gate battery
  ~20-30s/dataset including bootstrap G6)
- **Files to create**:
  - `multifeature_regime_gate.py` — pandas engine
  - `numpy_reference_multifeature.py` — numpy reference for G7
  - `run_backtests.py` — single cfg, 3 datasets driver
  - `compute_gates_and_score.py` — gates + scoring + kill evaluation
  - `tests/test_iter_044_multifeature.py` — TDD specs (≥ 8)
  - `results.json`, `verdict.json`
  - `final_report.md`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
- **Cumulative n_trials**: 4308 → 4309 (+1, single cfg per spec
  convention since iter 037).

## Implementation plan

1. **TDD specs** (write FIRST, must pass before backtest):
   - identity reduction: when `t10y3m` is constant zero, the regime
     equals iter 041's VIX-z-score gate (same flips, identical weights)
   - identity reduction: when both feature weights are 0, regime is
     all-stress (uniform tilt) — the limit case
   - causality: regime[t] depends only on (VIX[s], T10Y3M[s]) for
     `s ≤ t-1` (rolling z-score uses past 252 only)
   - look-ahead: shifting VIX/T10Y3M back by 1 day shifts the regime
     trace by exactly 1 day
   - lag spec: regime[t] = f(features[t-1]) (1-day lag exact)
   - rolling z-score: at bar t with t < 252, the z-score uses bars
     [0, t] (expanding window) — no full-sample stat used
   - cost accounting: turnover cost equals
     `sum(|Δposition| * cost_bps_per_leg)` per bar
   - regime → weights mapping: regime=1 → calm_weights, regime=0 →
     stress_weights (binary, no interpolation)
   - integration: net returns identical to iter 041 when VIX-only
     equivalent inputs are passed
   - composite-score symmetry: swapping (VIX, T10Y3M) feature order
     while swapping (w_VIX, w_T10Y3M) leaves the regime trace
     unchanged (commutative under symmetric inputs)

2. **Pandas engine** (`multifeature_regime_gate.py`):
   - `apply_multifeature_regime_3leg(r_eq, r_bd, r_gld, vix, term_spread, ...)`
   - Returns `(net, positions, scale, regime, composite_score)`
   - Same 3-leg signature as `apply_regime_weights_3leg` from iter 041,
     adds `term_spread` Series + `feature_weights` mapping + `z_window` int

3. **Numpy reference** (`numpy_reference_multifeature.py`):
   - Build the regime mask in pure numpy (no pandas reindex; pre-aligned
     arrays), apply the same weight switching, compute net returns and
     CAGR. G7 cross-lib parity vs pandas ≤ 3 pp.

4. **Run driver** (`run_backtests.py`):
   - Load same 3 datasets / windows as iter 041
   - Load VIX from `vix_daily.parquet`, T10Y3M from `t10y3m_daily.parquet`
   - Apply engine, save `results.json` with `returns_series` for plot

5. **Gate battery + scoring** (`compute_gates_and_score.py`):
   - Same 7-gate code reused from iter 041 (G1 vacuous N=1, G2 DSR
     with cumulative_n_trials = 4308 + 1 = 4309, G3-G6 unchanged)
   - G7 cross-lib via numpy reference
   - Compute score with `scoring.score_strategy()` + 5 robustness bonus
   - Evaluate pre-committed kills A-F
   - Write `verdict.json` + print summary

6. **Final report + plots + memory update** (Stage 5).

## Pre-committed configuration

```python
CFG = {
    "cfg_id": "multifeature_vix_t10y3m_z252_eq_w_tau0_70_40_40_30_55_55",
    "z_window": 252,                                # rolling z-score lookback
    "feature_weights": {"vix": 0.5, "neg_t10y3m": 0.5},   # equal weight, sum=1
    "stress_threshold": 0.0,                        # composite > 0 → stress
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},
    "feature_lag_days": 1,                          # iter 041 convention
    "rebalance": "daily",
    "cost_bps_per_leg": 0.0002,
    "funding_cost_modeled": False,
}
```

**Free parameters audited**:
- z_window=252 — 1y lookback, standard FF regression window;
  not tuned, single value.
- feature_weights={0.5,0.5} — equal weighting; not tuned.
- stress_threshold=0.0 — median split of standardised composite; not
  tuned, has the principled interpretation "stress when composite
  z-score > 0".
- iter 041 weights preserved verbatim.

**Total degrees of freedom in pre-committed cfg vs iter 041**: 0
new sweepable parameters (z_window/weights/threshold all hard-coded
to principled defaults). The mechanism delta is purely
"single-feature gate → 2-feature standardised composite gate".
