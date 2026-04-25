# Iteration 054 — Cross-sectional 12-1 momentum on Tiingo single-stock universe

## Hypothesis

**Cross-sectional momentum** — rank the universe by trailing 12-month
total return (skipping the most-recent month to avoid 1m reversal
`[stocks_on_the_move, p.76-77]`), buy equal-weighted top-K (K∈{20, 50}),
hold one month, rebalance monthly. Long-only, fully-invested, no
leverage, no overlay, no regime filter. This is the canonical
Jegadeesh-Titman (1993) 12-1 momentum mechanism transplanted to a
heterogeneous single-stock universe of ~1300 Tiingo-cached US tickers.

The single-stock cross-section produces ranking dispersion that ETF
baskets can't (iter 002/003 closure: ≤20-asset homogeneous universes
are dominated by aggregate market factor → ranking signal = noise).
With 1300+ idiosyncratic return processes, top-K vs bottom-K should
show meaningful UMD factor premium `[Carhart 1997, JoF 52]`.

## Primary citation

`[stocks_on_the_move, p.76-77]` — adjusted-slope momentum formula and
12-month / 1-month skip convention. Clenow's exact recipe was designed
for S&P 500 single-stock universes with 500+ heterogeneous constituents.

## Additional citations

- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6 (overlap with prev iters).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- Jegadeesh, N. & Titman, S. (1993). "Returns to Buying Winners and
  Selling Losers", *Journal of Finance* 48(1) 65–91.
- Carhart, M. M. (1997). "On Persistence in Mutual Fund Performance",
  *Journal of Finance* 52(1) 57–82 — UMD (momentum) factor.
- Asness, C. S., Moskowitz, T. J., & Pedersen, L. H. (2013). "Value and
  Momentum Everywhere", *Journal of Finance* 68(3) 929–985 — pervasive
  momentum premium evidence across asset classes.

## Edge source

SPY 1× captures aggregate market beta. Cross-sectional momentum
captures **idiosyncratic return persistence** within the equity
cross-section — winners keep winning over 3-12m horizons by ~1pp/month
risk-adjusted (Carhart 1997 UMD = ~8%/yr long-short). A long-only
top-K version harvests the long leg of UMD without short funding,
giving an axis SPY structurally cannot expose.

## Datasets

The Tiingo equity cache constrains start dates per ticker. We use the
LARGEST point-in-time-honest universe at each backtest start.

- **educational**: SPYSIM synth 1986+ N/A for single-stock momentum.
  We substitute an **educational-analog**: 36 Tiingo tickers with
  `first_dt ≤ 2006-01-01`, backtested 2007-01-01 → 2026-04-20
  (~19y, includes 2008 GFC). Universe small (escapes iter 003's ≤20-
  ETF-asset closure because these are heterogeneous *single stocks*,
  not basket ETFs — different mechanism).
- **spy_real**: 1300+ tickers with `first_dt ≤ 2013-12-31`,
  backtested 2015-01-01 → 2026-04-20 (~11y). Benchmark SPY b&h on
  same window (re-measured for honest comparison; fixed benchmark
  0.90 reported for cross-iter scoring).
- **ndx_real**: same universe, same window, benchmark QQQ b&h on
  same window (re-measured + fixed 0.955 reported).

Window mismatch vs scoring.py BENCHMARKS is a known caveat; reported
both for transparency. The "is the strategy better than SPY in the
window we could test" question is what the data permits.

## Kill criteria (pre-committed)

The hypothesis is **falsified** if:

- **Kill A** — top-K equal-weight 12-1 monthly Sharpe < benchmark + 0.05
  in 2 of 3 datasets after 5 bps roundtrip cost. (i.e., the basic
  ranking premium isn't there even on the heterogeneous universe.)
- **Kill B** — DSR worst p-value > 0.30 across all 3 datasets at
  cumulative n_trials. (Statistical noise, not signal.)
- **Kill C** — score < 60 (fails to clear PROMISING tier). Means the
  strategy doesn't even rise to "informs future iterations" level.

If ANY of A/B/C fires, document as DEAD_END with the structural reason.

## Expected budget

- Configs: 4 (top_k ∈ {20, 50}, lookback ∈ {252-21, 126-21}).
  Small grid for clean PBO; primary cfg pre-committed top_k=20 / 12-1.
- Wall-time: ~30-45 min impl + 30-60 min compute (1300 tickers ×
  3000 bars × monthly rebal × 4 cfgs × 3 datasets).
- Files: `run_backtest.py` (load tickers, compute returns, rank,
  rebalance, simulate), `compute_gates_and_score.py` (PBO/DSR/WF/etc.),
  `results.json`, `verdict.json`, `final_report.md`.

## Implementation plan

1. **Load universe**: read `data/tiingo/manifest.json`; filter to
   tickers with `first_dt ≤ T_start - 12mo` (for momentum lookback);
   load adjusted close from parquet files.
2. **Build wide returns matrix**: forward-fill within ticker; resample
   to monthly close; compute 1m returns.
3. **Generate signal**: 12-1 momentum = `cumret(t-12m, t-1m) - 1`
   (i.e., trailing 12m skipping most-recent 1m).
4. **Rank + select top-K**: each month-end, rank universe by signal
   among tickers with full lookback present; equal-weight top-K.
5. **Simulate**: monthly rebalance; 5 bps cost on each side of any
   weight delta; compute equity curve.
6. **Cross-lib reference**: numpy-only re-implementation; assert
   ±3 pp CAGR parity on educational dataset.
7. **Metrics**: Sharpe, CAGR, MDD per dataset.
8. **Gates**: PBO (CSCV on 4-cfg grid), DSR (cumulative n_trials =
   4320 + 4 = 4324), WF 8 windows, OOS 70/30, FWD post-2020,
   bootstrap 99.9% CI low, cross-lib parity.
9. **Score**: import `scoring.score_strategy()`, write
   `verdict.json`.
10. **TDD safety**: at minimum, a smoke test verifying signal +
    rebalance against a synthetic 5-ticker case with known winners.
    Baseline pytest must stay ≥ 796 passing.
