# Design — Momentum 13612 Universe Study

- **Date:** 2026-06-16
- **Status:** Design implemented as research-only scaffold; ETF staggered follow-up
  failed and US stocks finalist evolution remains diagnostic only.
- **Scope:** Pure monthly 1/3/6/12 cross-sectional top-N momentum across US/BR
  stocks, ETFs and mixed universes.
- **Mandate:** Maintenance mode. No deploy, no paper-trade label, no capital
  allocation, no mandate change `[advances_fin_ml, p.208-211]`.

## Thesis

The study isolates the raw `13612U` ranking effect from HAA/VAA/DAA wrappers:
score each asset by the equal-weighted mean of 1, 3, 6 and 12 month returns, then
hold the monthly top-N equal weight. Cross-sectional momentum and monthly review
are grounded in `[stocks_on_the_move, p.60]` and `[stocks_on_the_move, p.98-99]`.

The first implementation intentionally excludes absolute-momentum cash filters.
If all assets have negative scores, it still holds the least-bad top-N names. This
keeps the experiment focused on the user's requested pure 1-3-6-12 ranker.

## Universes

| Variant | Data path |
|---|---|
| `us_stocks` | Tiingo manifest/cache or yfinance screen. |
| `us_etfs` | Tiingo manifest/cache or yfinance screen. |
| `us_mixed` | Union of the two US lists. |
| `br_stocks` | User's Postgres 1m quote DB, daily close = last intraday bar. |
| `br_etfs` | Curated current BR ETF list via yfinance. |
| `br_mixed` | BR stocks from Postgres + BR ETFs from yfinance. |

## Data Risk

yfinance/current-list and unaudited Postgres results are `promotion_eligible=false`.
Promotion would require PIT/delisted coverage, adjusted-price audit and explicit
cost/tax handling `[advances_fin_ml, p.208-211]`.

The US stock heatmap/evolution runners now accept
`--us-stock-universe sp500_wikipedia_pit`, which reconstructs a month-end eligible
S&P 500 set from Wikipedia's selected changes and masks rank candidates at each
rebalance. This reduces current-constituent leakage but is not survivorship-free:
Wikipedia changes are incomplete and yfinance can still miss removed/delisted
tickers or delisting returns `[advances_fin_ml, p.208-211]`.

They also accept `--max-abs-daily-return X`, a yfinance data-quality filter that
drops tickers with adjusted-close daily jumps above `X` in absolute value. This is
required for PIT-ish diagnostics when stale/reused tickers create impossible
series, and it is not a strategy signal `[advances_fin_ml, p.31-34]`,
`[advances_fin_ml, p.208-211]`.

## Implementation

- Study path: `studies/momentum_13612_universes/`.
- Core: `core.py`.
- Data/universes: `universes.py`.
- Runner/report: `run.py` writes `DATA_AUDIT.md`, `REPORT.md` and
  `us/base_results.json`, plus one SPY comparison PNG per config under
  `us/{stocks,etfs,mixed}/plots/base/` when plotting is enabled.
- Extensive runner: `run_extensive.py` produced the focused stocks-only
  mechanism/frequency grid evidence now organized under `us/stocks/`:
  `us/stocks/REPORT_EXTENSIVE.md`, `us/stocks/results/extensive_results.csv`,
  `us/stocks/results/extensive_pbo.json`, and plots under
  `us/stocks/plots/extensive/`.
- Stocks heatmap runner: `run_stocks_heatmap.py` writes an interactive HTML
  diagnostic to `us/stocks/HEATMAP.html`, full rows to
  `us/stocks/results/heatmap_results.csv`, and static heatmaps to
  `us/stocks/plots/heatmap/`. The grid crosses mechanism, lookback profile,
  top-N, rebalance frequency and offset, explicitly exposing timing/parameter
  luck `[advances_fin_ml, p.273-275]`. It can optionally apply the
  `sp500_wikipedia_pit` membership mask.
- ETF staggered runner: `run_etf_staggered.py` produced the timing-luck-resistant
  ETF follow-up now organized under `us/etfs/`: `us/etfs/REPORT_ETF_STAGGERED.md`,
  `us/etfs/results/staggered_etf_results.csv`,
  `us/etfs/results/staggered_etf_pbo.json`, aggregate plots under
  `us/etfs/plots/etf_staggered/`, and finalist plots under
  `us/etfs/plots/etf_staggered/finalists/`. Each rebalance offset
  is an equal-capital sleeve rather than a selectable winner `[advances_fin_ml,
  p.273-275]`.
- Stocks finalist evolution runner: `run_stocks_evolution.py` writes
  `us/stocks/EVOLUTION_REPORT.md`, `us/stocks/results/evolution_results.csv`,
  `us/stocks/results/evolution_pbo.json`, aggregate plots under
  `us/stocks/plots/evolution/`, and finalist plots under
  `us/stocks/plots/evolution/finalists/`. It tests selected heatmap finalists
  across fixed/staggered offsets and SPY SMA200 / stock SMA100 overlays grounded
  in Clenow/Gayed trend-filter literature `[stocks_on_the_move, p.66-67,
  p.81-82, p.98-99]`, `[leverage_for_the_long_run, p.9, p.13, p.16]`. It shares
  the optional `sp500_wikipedia_pit` membership mask.
- Tests: `tests/test_momentum_13612_universes.py`.

## Rolling Relative Dominance Metric

The shared result row now includes `rolling_rel_score`, a benchmark-relative
rolling-window diagnostic. For every monthly start and each horizon
`3/5/10/15/20y`, strategy and SPY equities are reset to `1.0` at the same start;
the window score is the share of observations where
`strategy_equity / SPY_equity >= 1.0`. Horizon summaries keep mean, p25 and min
scores, and the overall score weights horizon means as `10%/15%/25%/25%/25%` for
`3/5/10/15/20y`. There is no 30-year horizon. The metric answers whether a
strategy stayed above the benchmark across many start dates, but it remains a
diagnostic under the same overfit and data-bias constraints `[testing_tuning,
p.327-335]`, `[advances_fin_ml, p.273-275]`.

## Latest Result

The 2026-06-16 ETF-only staggered hypothesis tested raw 13612 and raw inverse-vol
sizing across top-N `{3,5,10}` and rebalance `{3,6,12}` from 2000. Best after-tax
row was `raw_inverse_vol_top10_reb3_staggered`, with CAGR `10.15%`, MDD
`-30.24%`, Sharpe `0.683`, and PBO `0.663` fail. This rejects the local ETF
staggered hypothesis; all yfinance/current-list rows remain `promotion_eligible=false`
`[advances_fin_ml, p.208-211]`.

The 2026-06-16 stocks heatmap rerun starts in 1990 and covers 4,092 rows. Best
Sharpe is `raw_equal_lb6_top5_reb3_off0` (`59.32%` CAGR, `-59.04%` MDD, Sharpe
`1.380`), while more balanced regions are `vol_adjusted_lb6_top5_reb3_off0`
(`35.18%`, `-43.98%`, Sharpe `1.110`) and `composite_lb12_top15_reb12_off6`
(`16.90%`, `-34.44%`, Sharpe `0.897`). This remains a biased current-universe
diagnostic, not validation `[advances_fin_ml, p.208-211]`.

The 2026-06-16 stocks finalist evolution covers 72 post-heatmap rows. Best
Sharpe is still aggressive:
`evo_aggressive_raw_lb6_top5_q_staggered_off0_stock_sma100` (`55.88%` CAGR,
`-62.36%` MDD, Sharpe `1.401`). The best constrained row with CAGR `>=15%` and
MDD `>=-40%` is
`evo_balanced_voladj_lb6_top5_q_staggered_off0_market_sma200_monthly` (`26.89%`,
`-39.35%`, Sharpe `1.085`). The best Sharpe row with MDD `>=-30%` is
`evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_daily`
(`11.12%`, `-24.15%`, Sharpe `0.859`). Overall PBO is `0.000`, but
mechanism-level PBO fails (`0.623` to `0.778`) and the effective trial count is
larger because finalists were chosen after the heatmap. No validation or
promotion follows `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.

Follow-up infrastructure adds `sp500_wikipedia_pit` as a bias-reduction mode for
US stocks. A small in-memory smoke over `2020-2021` verified the dynamic universe
path and exposed the expected limitation: removed names such as `ABMD`, `ADS` and
`AGN` can appear in the reconstructed membership, while yfinance may return no
price history. This is useful for measuring sensitivity to current-constituent
leakage, not for promotion `[advances_fin_ml, p.208-211]`.

The first full PIT-ish rerun without an extreme-return guard was invalidated by
yfinance adjusted-close artifacts: `CFC` and `TIE` produced impossible daily jumps
while held by the strategy. Use `--max-abs-daily-return 10` for this diagnostic
surface unless a better PIT/delisted price source is substituted `[advances_fin_ml,
p.31-34]`, `[advances_fin_ml, p.208-211]`.

The guarded focused rerun (`sp500_wikipedia_pit`, `lb6`, top5, quarterly offsets,
start `2000-01-01`) dropped `9` broken yfinance series
(`BMC/CBE/CFC/CPWR/MEE/MI/PTV/RSH/TIE`). Best row was `off0`: CAGR `29.35%`, MDD
`-65.68%`, Sharpe `0.880`, terminal/SPY `92.4x`; `off1` was `28.15%`/`-67.45%`/
`0.859`, and `off2` was `21.01%`/`-77.34%`/`0.692`. This materially lowers the
current-universe headline but remains diagnostic only because delisted returns are
still missing and drawdown is ruin-level `[advances_fin_ml, p.208-211]`.

## Validation

Diagnostics mirror the repo's hard-gate vocabulary: PBO, DSR/PSR, walk-forward,
OOS/FWD stress, bootstrap 99.9% low and vectorized-vs-loop cross-check
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`,
`[testing_tuning, p.318-320]`.
