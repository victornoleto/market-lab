# Iteration 011 — Weekly-rebalance 3-leg vol-managed SPY+TLT+GLD blend

## Hypothesis

Apply iter 010's 3-leg vol-managed inverse-variance blend (SPY+TLT+GLD,
naïve risk parity + Moreira-Muir portfolio variance-scaling) to
**weekly-sampled returns** instead of daily. Single pre-committed cfg
`vt15_Lw4_cap20_3leg_weekly`: identical `target_vol=0.15`,
`max_leverage=2.0`, `lookback=4 weeks` (calendar-equivalent of iter
010's 21 trading days), rebalance cadence W-FRI (Friday close),
`periods_per_year=52` for annualisation. No grid, no sweep, single
trial per dataset (3 total, cumulative n_trials 4246 → 4249).

The hypothesis is that weekly execution (a) better aligns with the
Moreira-Muir 2017 monthly-scale canonical regime the paper's
variance-scaling was derived on, (b) materially reduces turnover
(52×/yr vs 252×/yr) removing transaction-noise drag, and (c) tests
directly whether the DSR ceiling iter 008 + iter 010 hit (worst
p=0.332-0.368) is structural to the daily timeframe or robust across
rebalance cadences.

## Primary citation

`[systematic_trading, p.144, ch.9]` — target_vol 15% is calibrated for
mid-institutional risk across ANY rebalance cadence (Carver treats
lookback as a volatility-estimation window, not tied to execution
frequency).

## Additional citations

- `[risk_parity, p.10-11, ch.1]` — naïve risk parity N-asset inverse-
  variance form generalises to any sampling frequency.
- `[risk_parity, p.80-81, ch.4]` — SPY-TLT diversification holds at
  any rebalance cadence (correlations measured cross-frequency are
  stable).
- `[systematic_trading, p.170-171, ch.11]` — IDM cap ≤ 2.5 is a
  portfolio-level constraint frequency-independent.
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag (no look-ahead).
- `[advances_fin_ml, p.208-211]` — G1 PBO N=1 vacuous.
- `[advances_fin_ml, p.222-223]` — G2 DSR deflator with cumulative
  n_trials.
- `[advances_fin_ml, p.31-34]` — G7 cross-lib parity required on new
  simulator.
- `[leverage_for_the_long_run, p.9]` — SPY regime asymmetry is the
  underlying information source at ANY timeframe (daily vol-regime
  persistence is measurable on weekly sampling too).
- Web: Moreira & Muir (2017), *JoF* 72(4), 1611-1644, DOI
  [10.1111/jofi.12513](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12513)
  — the paper's original analysis uses *monthly* returns with 12-month
  lookback; moving from daily (iter 010) to weekly (iter 011) is one
  step back toward the paper's native regime.

## Edge source

SPY buy-hold Sharpe ~0.90 fails to exploit (a) cross-asset
diversification with TLT/GLD, (b) leg-level volatility regime
persistence via inverse-variance weighting, and (c) portfolio-level
variance-scaling per Moreira-Muir. The structural question iter 011
asks: does measuring + rebalancing these signals on weekly scale
deliver the same edge as daily, with (potentially) lower DSR penalty
and lower turnover?

## Datasets

- **educational** (SPY+TLT+GLD 2004-11-18 → 2026-04-15, 21y weekly
  ≈ 1113 bars): GLD-constrained start mirrors iter 010 exactly for
  like-for-like Sharpe comparison.
- **spy_real** (SPY+TLT+GLD 2009-06-25 → 2026-04-15, 17y weekly
  ≈ 875 bars): canonical hunt-loop real-data SPY slot.
- **ndx_real** (QQQ+TLT+GLD 2010-02-12 → 2026-04-15, 16y weekly
  ≈ 844 bars): tech-heavy universe where iter 010 regressed
  (Sharpe 1.021 → 0.995).

## Structural-novelty check (vs `DEAD_ENDS.md`)

- Not daily EMA/SMA+LETF+stop (iter 001).
- Not single-asset vol-adaptation on SPY/QQQ (iter 004/005).
- Not Clenow / sector rotation / ≤20-asset ranking (iter 002/003).
- Not momentum-overlay redundant-with-variance-scaling (iter 007).
- Not monthly-EMA smoothing of macro signal (iter 009).
- Not 3-leg blend with param variations at daily horizon (iter 010
  DEAD_ENDS explicitly carves out minor variations; weekly rebalance
  is a **timeframe change**, not a param variation — the iter 010
  dead-end clause covers "different target_vol / lookback / tickers"
  but the path-forward section explicitly lists "weekly or monthly
  rebalance" as the untested direction).

## Kill criteria (pre-committed)

Written *before* running any backtest — binding.

- **Kill #1 (thesis-falsification)**: if weekly Sharpe regresses
  vs iter 010's 3-leg daily on **BOTH** real-data slots (spy Δ < 0
  AND ndx Δ < 0), the "weekly rebalance preserves edge" core claim
  is empirically falsified → write Option F off as a dead-end for
  this blend mechanism.
- **Kill #2 (CAGR catastrophic)**: if weekly CAGR < 0.75 × bench on
  ≥ 2 datasets, structural cost of less-frequent rebalance dominates
  edge.
- **Kill #3 (no score improvement)**: if total score < 70 (≤ iter 010's
  74 − 4 pts = losing ground) → Option F direction is done.
- **Kill #4 (gate erosion)**: if any dataset gates drop < 5/7,
  structural regression vs iter 010's 6/6/5 baseline.
- **Kill #5 (cross-lib breakage)**: if G7 cross-lib |ΔCAGR| > 3 pp,
  weekly-resample implementation has a bug → block report.
- **Success criterion (partial)**: if DSR worst p-value < iter 010's
  0.368 → theoretical attack on DSR ceiling partially succeeds, even
  if other gates tie or regress slightly.

## Expected budget

- Configs to test: 1 (pre-committed ex-ante, no sweep)
- Datasets: 3 (edu / spy / ndx)
- Total new trials: 3
- Wall-time: ~5-10 min (weekly sampling → smaller datasets, faster
  backtest than iter 010)

## Files to create

```
iterations/011-2026-04-24-1527-weekly-three-leg-blend/
├── hypothesis.md                    (this file)
├── weekly_three_leg_blend.py        (weekly-resample wrapper)
├── numpy_reference_weekly.py        (cross-lib reference)
├── test_weekly_three_leg_blend.py   (TDD — must pass BEFORE runs)
├── run_backtests.py                 (3-dataset runner)
├── compute_gates_and_score.py       (7-gate + score_strategy)
├── results.json                     (generated)
├── verdict.json                     (generated)
└── final_report.md                  (generated)
```

## Implementation plan

1. **TDD specs first** (`test_weekly_three_leg_blend.py`). Required
   properties:
   - Weekly resample uses W-FRI last-close per leg → compounded
     weekly return is exact `prod(1 + daily) - 1`.
   - `apply_weekly_blend(...)` == `apply_blend_variance_target_3leg
     (..., periods_per_year=52)` on pre-resampled weekly returns
     (i.e. the weekly wrapper is thin).
   - No look-ahead: σ²_{t-1} on weekly grid — at week t, only weeks
     ≤ t-1 used for variance.
   - Lookback L=4 weeks produces valid weights from week L+1 onward.
   - Degenerate case: 2-leg limit (σ²_gld → ∞) recovers iter 006
     weekly (sanity check on naïve RP).
   - Cost model: 2 bps/leg per unit position change applies at
     weekly cadence (turnover measured weekly).

2. **Implementation** (`weekly_three_leg_blend.py`). Two-stage:
   - `resample_returns_weekly(...)` — price-level compound resample
     to W-FRI last close per leg, then pct_change, then align on
     intersection.
   - `apply_weekly_blend(...)` — delegates to
     `three_leg_blend.apply_blend_variance_target_3leg` with
     `periods_per_year=52`.

3. **Cross-lib reference** (`numpy_reference_weekly.py`). Pure-numpy
   weekly resample (from daily prices → last-Friday prices via
   python loop, then returns, then iter-010 numpy 3-leg). Check CAGR
   parity ≤ 3 pp per G7.

4. **Run backtests** (`run_backtests.py`). 3 datasets, single cfg,
   save `results.json` with per-dataset metrics + custom weekly
   benchmarks.

5. **Gates + score** (`compute_gates_and_score.py`). Adapted for
   weekly annualisation:
   - G1 PBO: vacuous PASS (N=1).
   - G2 DSR: uses `periods_per_year` irrelevant (DSR is periodic),
     n_trials=4249 cumulative.
   - G3 WF 6/8: on weekly bars, per-block MDD < 25%.
   - G4 OOS 70/30: Sharpe > 0 on post-split weekly returns.
   - G5 FWD post-2020: Sharpe > 0 on post-2020 weekly returns.
   - G6 bootstrap 99.9%: stationary block bootstrap on weekly
     returns; ci_low > 0.
   - G7 cross-lib: pandas vs numpy-loop weekly ΔCAGR ≤ 3 pp.

6. **Custom benchmarks**: weekly SPY b&h on each dataset's window
   (since Sharpe(weekly) ≠ Sharpe(daily) generally). Use `run_backtests`
   to compute these live, not `scoring.BENCHMARKS` (which are daily).

7. **Score**: `score_strategy(..., benchmarks=custom_weekly_benchmarks)`
   with robustness bonus on 3-non-overlap sub-windows per dataset.

## Notes on the DSR theoretical claim

BASE_MEMORY (iter 010 final report) conjectures weekly reduces DSR
penalty by reducing effective n_trials. On closer reading of
`dsr.py`: DSR is a PSR evaluated at benchmark `E[SR_max]`, where the
expected-max is computed with variance `1/(T-1)` and T = number of
return observations. Weekly has T ≈ 1/5 of daily, so `1/(T-1)` is
~5× larger → benchmark SR periodic grows by sqrt(5) ≈ 2.24×. Observed
periodic Sharpe grows by sqrt(5/1) = 2.24× (because annualised SR =
periodic SR × sqrt(periods_per_year)). These cancel at first order.

**Second-order effects** may favour weekly: (a) lower transaction
cost drag, (b) reduced autocorrelation noise, (c) better skewness/
kurtosis behaviour if weekly compounds daily shocks. These are
empirical questions; the hypothesis treats this as a structural
experiment to *measure* whether weekly sampling helps, not to
assume it.

If the result is "weekly matches daily on Sharpe but turnover drops
5× and cost drag drops proportionally", that's still a structurally
useful finding even without breaking the DSR ceiling — informs
future iterations about cadence-sensitivity of the blend family.
