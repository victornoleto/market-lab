# Iteration 003 — Equal-notional sector rotation with Clenow adjusted-slope ranking

## Hypothesis

Clenow's adjusted-slope×R² ranking signal `[stocks_on_the_move, p.70-77, 82]`
does have cross-sectional predictive power on the 11 SPDR sector ETF
universe, but iter 002 could not measure it because the canonical 10 bps
ATR-risk-parity sizing under-deployed the portfolio by ~3× when transported
from single-stock (ATR ~1-3% of price) to sector-ETF (ATR ~0.3-1% of price)
universe — leaving 60-80% of capital in cash. Replacing the ATR sizing with
**equal-notional 1/K sizing** (each held sector gets exactly `equity / K` of
exposure, ignoring ATR) fully deploys capital and isolates the signal-edge
question from the sizing-calibration issue. If the ranking has edge, this
configuration should surface it; if it does not, sector momentum on the SPDR
universe is a structural dead-end regardless of sizing.

## Primary citation

`[stocks_on_the_move, p.70-77, p.82]` — adjusted slope (annualized 90d
exponential regression slope × R²) as the cross-sectional ranking score.
The book's ranking formula is used unchanged; only the sizing rule is
replaced. This directly tests iter 002's open question per its final-report
recommendation §"Next iteration suggestions" #1.

## Additional citations

- `[stocks_on_the_move, p.66-67, p.98-99]` — SPY 200d SMA regime filter
  (Clenow canonical; regime-off → no new buys, held positions not forced out).
- `[stocks_on_the_move, p.60]` — Jegadeesh & Titman (1993), the academic
  foundation of cross-sectional momentum. The original paper used
  **equal-weighted** deciles, so equal-notional sizing is the foundational
  academic implementation (ATR-risk-parity is Clenow's refinement for single
  stocks).
- `[stocks_on_the_move, p.81]` — 100d SMA trend filter (per-asset disqualifier).
- `[stocks_on_the_move, p.82]` — 90d |gap| > 15% disqualifier.
- `[advances_fin_ml, p.298-299]` — Markowitz's curse: with small N and noisy
  covariance estimation, the 1/N portfolio is a robust Bayesian prior. For
  N=3-9 sectors, equal-notional is statistically defensible vs any risk-based
  sizing derived from short-sample covariances.
- `[advances_fin_ml, p.208-211]` — PBO gate G1 (CSCV framework).
- `[advances_fin_ml, p.222-223, 275]` — DSR with cumulative n_trials
  (deflator for multiple-testing).
- `[advances_fin_ml, p.196-202]` — bootstrap CI for trade returns.
- External (classical, no date floor per loop prompt): Jegadeesh & Titman
  (1993), *Journal of Finance* 48(1) 65-91 — "Returns to Buying Winners and
  Selling Losers: Implications for Stock Market Efficiency". DOI
  10.2307/2328882. The 6-12 month formation × 3-12 month holding period
  framework is the empirical anchor; 90d formation in this iter sits at the
  short end of their grid.

## Edge source

SPY 1× buy-hold holds all sectors permanently at market-cap weights. Clenow
ranking concentrates exposure in the 3-9 top-momentum sectors while excluding
laggards — if cross-sectional momentum is persistent at weekly horizon on
sector ETFs, the equal-notional concentrated portfolio captures higher
risk-adjusted returns than the diffuse market-cap index.

## Datasets

All three loaded from `data/tiingo/daily/prices/*.parquet`, per
`BASE_MEMORY.md` "Infrastructure available".

- **educational (sectors_long 2006-2026 SPY)** — 9 original SPDR sectors
  (XLK/XLF/XLV/XLY/XLP/XLE/XLI/XLU/XLB) benchmarked vs SPY. Includes 2008
  GFC and COVID in-sample. Benchmark override: measured SPY 2006-2026
  Sharpe ~0.54 (iter 002's finding — different from synth SPYSIM 0.68).
- **spy_real (sectors_spy 2009-2026 SPY)** — 11 SPDR sectors vs SPY.
  Post-2009 bull-dominated period. Benchmark ~0.79-0.90 (iter 002 measured
  0.79 on this window; scoring.BENCHMARKS default 0.90 on a slightly
  different window).
- **ndx_real (sectors_ndx 2010-2026 QQQ)** — same universe, QQQ as
  benchmark/comparator. Sector portfolio vs tech-heavy index.

Same 3 datasets iter 002 used — apples-to-apples comparison of the sizing
change.

## Kill criteria (pre-committed)

At the end of Stage 3, the hypothesis is **falsified** if ANY of:

1. Best config on **spy_real** dataset delivers Sharpe < 0.85 (i.e., cannot
   even approach SPY Sharpe benchmark 0.79-0.90). At that point the signal
   is clearly not there regardless of further grid tuning.
2. Portfolio deployment fraction (median exposure / equity) remains < 85%
   across the grid — would indicate the equal-notional fix did not achieve
   full deployment as designed, meaning the test is inconclusive rather
   than informative. (Iter 002 median was 25-37%.)
3. Cross-lib G7 reference (pure numpy) disagrees with the strategy engine
   by > 3 pp CAGR on any dataset — would indicate engine bug, not strategy
   signal. Re-implementation required before continuing.

Kill case #1 → add "sector momentum on SPDR universe (all sizing variants)"
to `DEAD_ENDS.md` and close the direction.

## Expected budget

- Configs: 4 × 3 × 2 = **24 configs** (`top_k ∈ {3, 5, 7, 9}` ×
  `lookback_slope ∈ {60, 90, 120}` × `buy_leverage ∈ {1.0, 2.0}`).
  The grid spans material signal variations — top-3 is concentrated, top-9
  is nearly equal-weight-all — and thus has return dispersion, avoiding
  DEAD_ENDS #8 (small-grid near-zero regime).
- Wall-time: ~15 min for 24 configs × 3 datasets + ~10 min for gates on
  top-5.
- Files to create:
  - `src/ai_trade/backtest/strategies/sector_momentum_equal_notional.py`
    (new strategy reusing primitives from `sector_momentum_clenow`)
  - `tests/test_sector_momentum_equal_notional.py` (TDD)
  - `iterations/003-*/run_backtests.py`
  - `iterations/003-*/compute_gates_and_score.py`
  - `iterations/003-*/results.json`
  - `iterations/003-*/verdict.json`
  - `iterations/003-*/final_report.md`

## Implementation plan

1. **TDD pass**: write `tests/test_sector_momentum_equal_notional.py` first
   with 6-10 tests covering (a) equal-notional sizing math, (b) top-K
   selection, (c) regime gate, (d) per-position disqualifiers carried over
   from Clenow canonical, (e) engine integration on a toy 3-sector universe.
2. Implement `SectorMomentumEqualNotional` strategy. Reuse `adjusted_slope`,
   `disqualify_trend`, `disqualify_gap`, `regime_allows_new_buys`, and
   `top_k_ranks` from the existing `sector_momentum_clenow` module — only
   sizing changes. Internal shares computation: `shares = floor(equity × L /
   K / price)` where L=buy_leverage, K=top_k, price=current close.
3. Cross-lib G7 reference: pure numpy daily loop that reproduces
   end-of-period equity given the same ranking decisions. Compare CAGR
   to engine output; must agree to ± 3pp.
4. `run_backtests.py`: iterate over 24 configs × 3 datasets, record Sharpe,
   CAGR, MDD, deployment fraction, trade count. Save results.json.
5. `compute_gates_and_score.py`: run 7 gates on top-5 configs per dataset by
   composite score (Sharpe rank + CAGR rank), then pick the grand champion
   (best min-across-3-datasets Sharpe) and score it.
6. Stage 5 artifacts.

Pytest baseline: **must stay green** (currently 1 161). New tests add to
the count; existing tests must all pass.
