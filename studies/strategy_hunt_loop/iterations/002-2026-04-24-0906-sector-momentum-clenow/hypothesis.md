# Iteration 002 — Clenow cross-sectional momentum on US sector ETFs

## Hypothesis

Run Clenow's book-canonical momentum strategy (annualized 90-day log-regression
slope × R², ATR risk-parity sizing, 200-day index regime filter) over the 11
SPDR US sector ETFs instead of S&P 500 single stocks. Hold the top-K ranked
sectors with weekly rebalance; add new positions only while SPY > 200d SMA;
size each by ATR (10 bps per position); no stop-loss. Expectation: sector
dispersion + equal-risk weighting + regime trim produces a risk-adjusted
edge vs cap-weighted SPY buy-hold without leverage.

## Primary citation

`[stocks_on_the_move, p.76-77, p.82, p.88-89, p.98-99]` — Clenow's full
ranking + sizing + regime filter spec.

## Additional citations

- `[stocks_on_the_move, p.66-67]` — index regime filter (SPY 200d MA)
- `[stocks_on_the_move, p.219-220]` — anti-optimization principle
  ("Optimizations are evil") — commits to minimal grid, no parameter tune
- `[stocks_on_the_move, p.221-223]` — risk-parity beats cap-weighting
  mechanically (equal-risk on sectors is the structural edge)
- `[stocks_on_the_move, p.229-230]` — portfolio size ≥ 10 stocks warning;
  adapted here as "hold top 3-5 of 11 sectors" is intentionally concentrated
  vs original 20-30 stocks — documented deviation
- `[stocks_on_the_move, p.94-96]` — no stop-loss, no trailing stop
- `[systematic_trading, ch.11]` — risk-parity / vol-targeting framework
  (Carver's parsimony principle aligns)
- `[advances_fin_ml, p.208-211]` — PBO gate reasoning for the grid
- Jegadeesh & Titman (1993) "Returns to Buying Winners and Selling Losers" —
  primary empirical source for cross-sectional momentum; cited by Clenow
  `[p.60]`

## Edge source

SPY is cap-weighted and ~30% mega-cap tech; sector-level momentum + ATR
risk-parity captures dispersion that SPY masks, and the 200d regime filter
trims bear-market drawdown mechanically — structurally different from
time-series trend-follow-on-SPY (iter 001 dead-ends).

## Datasets

The strategy is cross-sectional on sector ETFs — educational SPYSIM synth
(single ticker) **cannot** accommodate it. I adapt the 3-dataset structure
to preserve the cross-dataset non-negotiable constraint:

- **educational** → `sectors_long`: 9 original SPDR sectors
  (XLK/XLF/XLV/XLY/XLP/XLE/XLI/XLU/XLB) from **2006-01-03** (all-sectors
  data common start) to 2026-04-20 (~20y). Benchmark: SPY b&h over same
  window (Sharpe measured, NOT the 0.68 SPYSIM bench). Role: longer window
  with 2008-2009 GFC drawdown in-sample — structural stress test.
- **spy_real** → `sectors_spy_modern`: all 11 sectors (XLK/XLF/XLV/XLY/XLP/
  XLE/XLI/XLU/XLB + XLRE from 2015-10 + XLC from 2018-06) over 2009-06-25
  → 2026-04-20 (17y). Benchmark: SPY b&h Sharpe 0.90. Role: the primary
  "beat SPY" test.
- **ndx_real** → `sectors_ndx_modern`: same 11-sector strategy, same
  window as `ndx_real` (2010-02-12 → 2026-04-20). Benchmark: QQQ b&h
  Sharpe 0.955. Role: cross-benchmark stress — can sector rotation beat
  QQQ (harder bar)?

Benchmarks dict passed explicitly to `score_strategy()` with overridden
`educational` (measured SPY 2006-2026 Sharpe) since this iteration's
"educational" is not the 40y SPYSIM synth.

## Kill criteria (pre-committed)

If **spy_real Sharpe < 0.90** at canonical Clenow params (top-K ∈ {3, 5}),
hypothesis is falsified — the entire hunt mandate is "beat SPY on risk-
adjusted real data". No grid search to cure. If kill fires, strategy goes
to DEAD_ENDS under "Cross-sectional sector-ETF momentum (Clenow 2015
canonical)".

Secondary kill: if MDD > 40% on spy_real (> SPY bench 33.7% + 5pp
ceiling), also flag as failure axis.

## Expected budget

- **Configs tested: 4** (top-K ∈ {3, 5} × leverage ∈ {1×, 2×}) —
  deliberately minimal to respect Clenow's anti-optimization principle
  and keep DSR deflator tight. No parameter sweep on lookback/thresholds.
- **Wall-time:** ~20-40 min (3 datasets × 4 configs × ~6s per backtest +
  validation)
- **Files to create:**
  - `src/ai_trade/backtest/strategies/sector_momentum_clenow.py` —
    strategy module
  - `tests/test_sector_momentum_clenow.py` — TDD tests for adjusted-slope
    computation + ATR sizing + regime filter unit logic
  - `iterations/002-*/run_backtests.py` — per-dataset runner
  - `iterations/002-*/results.json` — raw metrics
  - `iterations/002-*/verdict.json` — scoring output
  - `iterations/002-*/final_report.md` — prose verdict

## Implementation plan

1. **TDD unit tests (tests/test_sector_momentum_clenow.py)**:
   - `test_adjusted_slope_on_known_series` — fit log-linear on a known
     exponential sequence; verify annualized slope matches (e^m)^250 - 1
     and R² ≈ 1.0
   - `test_adjusted_slope_penalizes_noisy_series` — compare smooth vs
     noisy-same-slope: R² drops → adjusted slope drops
   - `test_atr_twenty_days` — True Range + 20d mean against known OHLC
   - `test_position_size_risk_parity` — shares = floor(equity × 0.001 / ATR)
     matches Clenow's $100k/ATR 3.26 = 30 shares example [p.89]
   - `test_gap_filter_15pct` — series with a 20% daily move gets disqualified
   - `test_regime_filter_blocks_new_buys_below_sma200` — regime off = no
     new positions; existing positions remain
   - `test_rank_top_k_selection` — ranking picks top-K sectors correctly

2. **Strategy module**:
   - `SectorMomentumClenow(StrategyBase)` with params
     `{lookback_slope=90, lookback_trend=100, lookback_regime=200,
     lookback_atr=20, gap_threshold=0.15, risk_factor=0.001, top_k,
     buy_leverage, rebalance_weekday=2 (Wed), position_rebalance_interval=2}`
   - `on_rebalance()`:
     1. Compute adjusted_slope for all sectors with ≥90d history
     2. Apply disqualifications (below 100d SMA, gap >15% in 90d)
     3. Sort descending, take top-K
     4. Sell holdings outside top-K or disqualified or below 100d SMA
     5. If SPY close > SPY 200d SMA: buy new entries from top-K (ATR size)
     6. Every 2nd rebalance: rebalance existing positions to target ATR size

3. **Dataset runner (iterations/002-*/run_backtests.py)**:
   - Load sector parquets + SPY/QQQ benchmarks
   - Build `Portfolio` with cash, run `Runner` over each window
   - Compute per-dataset metrics via `performance.py`
   - Compute 7 gates: G1 PBO (within the 4-config grid), G2 DSR (with
     cumulative n_trials = 4020 + 4 from iter 002 = 4024), G3 Walk-forward
     (rolling 6 yrs train / 2 yrs test, 8 windows), G4 OOS 70/30, G5 FWD
     post-2020, G6 bootstrap 99.9% CI low > 0, G7 cross-lib (hand-rolled
     numpy pandas ref vs the engine implementation, ±3pp CAGR)

4. **Scoring**:
   - Import `scoring.score_strategy` with overridden benchmarks dict
     (educational = measured SPY 2006-2026 real Sharpe)
   - Write `verdict.json` + `results.json`

5. **Cross-lib G7**: the engine uses the existing Runner (already cross-lib
   validated for other strategies); for the new sector-momentum primitives
   (adjusted slope, ATR sizing, ranking), add a pandas/numpy-only
   independent implementation in the test file and verify parity on the
   primary config.

6. **Baseline guard**: run `pytest tests/ --ignore=tests/cross_lib -q`
   before and after; must stay at 725 pre → 725 + new_tests post.
