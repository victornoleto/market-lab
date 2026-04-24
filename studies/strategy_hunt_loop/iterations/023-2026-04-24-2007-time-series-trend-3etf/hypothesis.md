# Iteration 023 — Time-series trend-following on SPY+TLT+GLD with per-asset vol-targeting

## Hypothesis

Replace iter 016's 2-leg static-ratio × portfolio-σ² vol-managed stack
with a **standalone 3-asset time-series trend-following portfolio** on
{equity, TLT, GLD}, where (i) each asset carries its own sign signal
driven by 12-1 momentum (252-day lookback, 21-day skip), (ii) each
asset is **independently** vol-targeted to a per-leg annualised vol of
10 % (σ̂_{t−1} lag, same Moreira-Muir discipline as iter 008/016),
(iii) short positions are allowed when the trend signal is negative,
(iv) total gross leverage is capped at 2.0× to respect IDM
`[systematic_trading, p.170-171, ch.11]`.

Because each leg is scaled off its **own** σ̂_i[t−1] rather than the
portfolio-level σ²_port[t−1], the scale feedback that absorbed every
overlay tried on the iter 016 base (variance iter 019/020/021, credit
iter 014, correlation iter 019, calendar iter 022) no longer applies:
a shock in σ_eq rescales only the equity leg, leaving the TLT and GLD
legs untouched. The three legs can therefore add or subtract
exposure independently, producing a P&L stream with different
geometric properties (permits shorts, permits pure-cash states,
permits full-leverage in one leg while others idle).

The edge hypothesis is that **time-series momentum is an independent
risk premium** — per Moskowitz-Yao-Pedersen (2012) "Time Series
Momentum", JFE 104(2) 228-250 — that persists across equities, bonds,
commodities, and currencies with documented ~12-month lookback robust
across asset classes (Hurst-Ooi-Pedersen 2017 "A Century of Evidence
on Trend-Following Investing", JPM 44(1)). The 3-asset basket
{equity, TLT, GLD} spans 3 structurally distinct risk drivers (growth,
duration, inflation-hedge) so the trend signal can diversify across
regimes the SPY+IEF blend cannot (e.g., 2022 inflation shock where
both legs fell — trend would have gone SHORT TLT).

## Primary citation

`[algo_trading_chan, p.164, ch.6]` — "Cross-sectional momentum
lookback=252, holddays=25. Based on Moskowitz, Yao, and Pedersen
(2012); the 12-month lookback has academic support across many asset
classes. Curve-fit risk: low (published, replicated across many
markets)." This citation grounds the 252-day lookback + ~21-day
rebalance as the canonical academic anchor for time-series momentum,
allowing iter 023 to commit ex-ante to a single lookback without grid
search.

## Additional citations

- `[systematic_trading, p.40, ch.2]` — Volatility standardisation as
  the "single most powerful technique in the framework, enabling the
  same trading rule to be applied generically across all
  instruments". Justifies per-asset vol-targeting (each leg scaled to
  identical 10 % annualised vol before aggregation) instead of
  portfolio-level σ²_port.
- `[systematic_trading, p.137-148, ch.9]` — Volatility target
  percentage set once via Half-Kelly; 10 % per-asset × 3 assets ≈ 17 %
  aggregate (before correlation netting) matches iter 016's 15 %
  portfolio vol target within the same ballpark.
- `[systematic_trading, p.159-160, ch.10]` — Volatility scalar per
  instrument: position size = (daily cash vol target) / (instrument
  cash vol) — canonical per-asset sizing form used here.
- `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 hard cap on
  total leverage; we use 2.0 as iter 016 did.
- `[systematic_trading, p.118-119, ch.7] + p.282-284 (appendix B)` —
  EWMAC trend rule (exponentially weighted MA crossover), documented
  six lookback variants. Motivates trend-as-primary-mechanism rather
  than trend-as-overlay (iter 007 mistake).
- `[stocks_on_the_move, p.58, p.60]` — Momentum Effect (Levy 1967 /
  Jegadeesh-Titman 1993 / Clenow). Per-stock trend filter and 12-month
  lookback are the canonical long-horizon momentum operationalisations.
- `[stocks_on_the_move, p.81-82]` — Per-asset trend filter (100-day
  MA for the "failsafe" trend check).
- `[risk_parity, ch.5-7]` — Multi-asset risk-parity framework; here
  used conceptually (each leg contributes equal risk by construction
  via per-asset vol-target) rather than via dynamic covariance
  inversion.
- `[leverage_for_the_long_run, p.7, footnote 12]` — Grinblatt &
  Moskowitz 2000 autocorrelation / momentum footnote anchors the
  underlying return-autocorrelation basis of trend-following.
- `[advances_fin_ml, p.162-164]` — σ̂_{t−1} lag discipline to prevent
  look-ahead bias in vol-scaling.

### Web / paper citations

- **Moskowitz, T.J., Ooi, Y.H. & Pedersen, L.H. (2012)**. "Time Series
  Momentum." *Journal of Financial Economics* 104(2), 228-250. DOI:
  10.1016/j.jfineco.2011.11.003. — Core TSM factor paper.
- **Hurst, B., Ooi, Y.H. & Pedersen, L.H. (2017)**. "A Century of
  Evidence on Trend-Following Investing." *Journal of Portfolio
  Management* 44(1), 15-29. DOI: 10.3905/jpm.2017.44.1.015. —
  Out-of-sample validation across 100+ years / 67 markets.
- **Baltas, N. & Kosowski, R. (2020)**. "Demystifying Time-Series
  Momentum Strategies: Volatility Estimators, Trading Rules and
  Pairwise Correlations." *Management Science* 66(10), 4567-4596. —
  Modern (post-2015) TSM refinement confirming per-asset vol-target
  beats portfolio-level scaling on drawdown-matched comparisons.
- **Goyal, A. & Jegadeesh, N. (2018)**. "Cross-Sectional and
  Time-Series Tests of Return Predictability: What is the Difference?"
  *Review of Financial Studies* 31(5), 1784-1824. — Confirms TSM is a
  **distinct** factor from XSM (iter 003's closed direction).

## Edge source

**Time-series trend premium on non-equity legs**: SPY buy-hold already
captures the equity-trend premium (post-2009 Sharpe 0.90 is near the
informational ceiling per iter 001/004/005/007 closures); the genuine
orthogonal contribution comes from the **TLT-trend leg** (long bonds
in deflationary regimes 2008-2020; **short bonds in 2022**) and
**GLD-trend leg** (long gold in crisis / inflationary regimes
2007-2011, 2019-2022). iter 016's SPY+IEF 60:40 stack is
structurally long-only on both legs and got hurt by the 2022 stock-
bond double-draw; the trend signal on TLT would have flipped to
SHORT in late 2021, sidestepping the draw entirely. **This is the
variance-disjoint leg the memory repeatedly flagged as the forward
path (Option X).**

## Datasets

- **educational** (SPY+TLT+GLD 2006-01-03 → 2026-04-15): ~20y window
  spanning the 2008 GFC, 2011 Euro crisis, 2015 oil bust, 2020 COVID
  shock, 2022 inflation shock, 2023-2024 disinflation — every TSM
  regime the literature tests. GLD inception 2004-11-18 is >1 year
  before dataset start, giving full 252-day lookback coverage from
  day 1.
- **spy_real** (SPY+TLT+GLD 2009-06-25 → 2026-04-15): canonical post-
  GFC window; SPY buy-hold Sharpe 0.90 is the benchmark-to-beat. The
  TLT leg will have been long-biased 2009-2019 and short 2022, testing
  whether trend captures the bond crash cleanly.
- **ndx_real** (QQQ+TLT+GLD 2010-02-12 → 2026-04-15): tech-heavy
  equity; trend signal on QQQ should remain long through the mega-cap
  bull run; edge must come from TLT and GLD legs.

## Kill criteria (pre-committed)

Pre-committed — no post-hoc rationalisation allowed.

- **KILL A (Sharpe regress)**: if candidate Sharpe < SPY/QQQ benchmark
  on ≥ 2 of 3 datasets, the trend mechanism did not add value and the
  hypothesis is falsified. Still report honestly.
- **KILL B (degenerate signal — always long)**: if the composite trend
  signal is active-long on > 85 % of bars (i.e., effectively a static
  buy-hold 3-asset blend), the strategy reduces to iter 010 with extra
  steps and the "per-asset vol target escapes σ²_port absorption"
  thesis is unfalsifiable because no short state is ever tested. Score
  must be interpreted as belonging to iter 010's dead-end family.
- **KILL C (leverage-cap saturation)**: if the 2.0× leverage cap binds
  on > 80 % of bars, per-asset vol-targeting is degenerate (behaves
  as constant-leverage buy-hold blend) and the geometry claim is
  broken. Report as quasi-iter-010 outcome.

If none of A-C trigger, the iteration has cleanly tested the
"per-asset vol-targeted trend-following as portfolio-geometry change"
hypothesis, irrespective of the final score.

## Expected budget

- **Configs**: 1 pre-committed (`ts_trend_L252_skip21_vol10_cap20`).
  Cumulative n_trials 4273 → 4276 (+3).
- **Wall-time**: ≤ 30 min (data load, 3 datasets × 1 cfg, gates).
- **Files to create**:
  - `trend_3etf.py` — strategy module (per-asset vol-target + trend
    signal + total leverage cap).
  - `numpy_reference_3etf.py` — hand-rolled numpy reference for G7
    cross-lib parity (±3 pp CAGR).
  - `run_backtests.py` — runner loading 3-asset data + executing cfg.
  - `compute_gates_and_score.py` — 7-gate battery + score + verdict.
  - `tests/test_strategy_hunt_loop_iter023.py` — TDD specs (9 tests
    covering signal, vol-target per asset, leverage cap, short
    handling, cross-lib parity).
  - `results.json`, `verdict.json`, `final_report.md`,
    `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.

## Implementation plan

1. **TDD**: write `tests/test_strategy_hunt_loop_iter023.py` with 9
   specs:
   1. `test_trend_signal_sign_from_12_1_lookback` — signal = sign of
      (cum_return over [t−252, t−21]).
   2. `test_per_asset_vol_target_scales_exposure` — per-leg position =
      target_vol / σ̂_{t−1} (no look-ahead).
   3. `test_short_position_when_signal_negative` — when signal < 0,
      position is negative scalar × asset.
   4. `test_total_leverage_cap_enforced` — sum |pos_i| clipped to 2.0
      via proportional shrink across legs.
   5. `test_zero_signal_forces_zero_position` — at signal = 0, leg
      contributes no exposure.
   6. `test_returns_aggregate_across_legs` — net[t] = Σ pos_i[t] ×
      r_i[t] − cost[t].
   7. `test_cross_lib_parity_numpy_reference` — CAGR ±3 pp vs numpy
      hand-roll on random 3-asset synth.
   8. `test_signal_ignores_bars_before_lookback_plus_skip` — first
      valid bar is index (252 + 21).
   9. `test_cost_linear_in_position_change_per_leg` — 2 bps per unit
      ∆position per leg (same as iter 016).
2. **Implement `trend_3etf.py`** to pass the 9 specs. Vectorised
   pandas; σ̂ = rolling std × √252; signal = sign(return over window);
   per-leg position = signal × target_vol / σ̂; total-leverage-cap via
   proportional rescale when Σ |pos| > cap.
3. **Implement `numpy_reference_3etf.py`** — hand-rolled numpy loop
   reproducing the same mechanism for G7 parity test.
4. **Run `run_backtests.py`** on 3 datasets → `results.json` (per-cfg
   Sharpe/CAGR/MDD + scale diagnostics + returns_series).
5. **Run `compute_gates_and_score.py`** → G1-G7 + score + verdict.json.
6. **Plot** — `python studies/strategy_hunt_loop/plot_helper.py --iter 023`.
7. **Final report** + BASE_MEMORY update (newest first, auto-prune if
   > 18 KB).

## Expected outcome (honest)

Best case: trend signal correctly goes short TLT in 2022,
long GLD in 2007-2011, captures +0.15-0.20 Sharpe over iter 016 on
spy_real and ndx_real, ties or modestly improves educational. Score
75+/100 (STRONG tier).

Base case: trend signal primarily long on SPY/QQQ (equity drift),
modestly additive on TLT and GLD. Score ~60-72 (PROMISING) because
TSM on a small basket saturates similarly to iter 010. Would still be
a non-trivial finding: per-asset vol-target breaks σ²_port absorption,
but the absolute Sharpe improvement is bounded by the basket's
effective number of bets (~sqrt(3) per Carver's "Law of Active
Management" `[systematic_trading, p.42, ch.2]`).

Worst case: KILL A triggered — trend signal adds noise (transaction
cost drag + whipsaw) without compensating premium on this specific
basket in this specific window. Would close the "per-asset vol-target
as portfolio-geometry change" family on 3-asset ETF baskets. Still
useful: rules out the memory's #1 proposed forward path.
