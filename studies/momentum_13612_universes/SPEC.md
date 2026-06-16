# Momentum 13612 Universe Study Spec

Status: active research-only scaffold, initiated 2026-06-15; ETF staggered
follow-up and US stocks finalist evolution completed on 2026-06-16 with no
promotion. No deployment, paper-trade label or mandate change.

## Objective

Test the pure 1/3/6/12 cross-sectional momentum effect across six requested
universes, without HAA's TIP canary or defensive sleeve.

| Variant | Universe | Preferred data |
|---|---|---|
| `us_stocks` | US stocks | Restored Tiingo parquets; yfinance screen only. |
| `us_etfs` | US ETFs | Restored Tiingo parquets; yfinance screen only. |
| `us_mixed` | US stocks + ETFs | Same source family as above. |
| `br_stocks` | BR stocks | Local Postgres 1m quote database collapsed to daily last-bar closes. |
| `br_etfs` | Curated current BR ETF list | yfinance screen only. |
| `br_mixed` | BR stocks + BR ETFs | Postgres stocks + yfinance ETFs by default. |

## Rule

At each month-end close:

1. Compute each asset's `13612U` score as the equal-weighted mean of 1, 3, 6 and
   12 month returns. Ranking momentum citation: `[stocks_on_the_move, p.60]`.
2. Rank cross-sectionally by score descending, tie-breaking alphabetically for
   deterministic reproducibility.
3. Hold top-N equal weight. The first registered grid is `top_n in {4, 10, 20}`;
   any expansion must pay trial accounting `[advances_fin_ml, p.273-275]`.
4. Do not use an absolute-momentum/cash filter in this first study. If all scores
   are negative, hold the least-bad top-N names so the test isolates the pure
   cross-sectional effect.
5. Apply month-end weights only to subsequent daily returns to avoid look-ahead
   `[advances_fin_ml, p.31-34]`.

Monthly review cadence follows `[stocks_on_the_move, p.98-99]`.

## Data Policy

- US source `auto` uses local Tiingo parquets if `data/tiingo/daily/prices/`
  exists; otherwise yfinance requires `--allow-biased-yfinance`. yfinance stock
  screens default to current S&P 500 (`--us-stock-universe sp500`), while ETF
  screens default to the curated liquid ETF list (`--us-etf-universe curated`).
- US stock heatmap/evolution runners also accept
  `--us-stock-universe sp500_wikipedia_pit`, which reconstructs a PIT-ish S&P 500
  eligible set per month-end from Wikipedia's selected historical changes and
  masks ranking candidates at each rebalance. This reduces current-constituent
  leakage, but remains non-promotable because Wikipedia is incomplete and
  yfinance still lacks true delisted prices/returns `[advances_fin_ml, p.208-211]`.
- Stocks-only runners accept `--max-abs-daily-return X` as a yfinance data-quality
  filter. It drops tickers whose adjusted-close daily return exceeds `X` in
  absolute value, catching stale ticker reuse and broken split/delisting series
  before they contaminate ranks. This is not a strategy rule
  `[advances_fin_ml, p.31-34]`, `[advances_fin_ml, p.208-211]`.
- Tiingo manifest may define the ticker universe, but the manifest alone is not
  a price source.
- yfinance rows are always `promotion_eligible=false` because current-universe
  membership and missing delisted symbols create survivorship bias
  `[advances_fin_ml, p.208-211]`.
- BR stocks default to Postgres 1m quotes. The runner does not assume the local
  schema: configure table/columns via CLI or `MARKET_LAB_BR_1M_*` env vars.
- Postgres BR rows are also non-promotable until the local database is audited for
  adjusted prices, split/dividend handling, survivorship/delisted coverage and PIT
  membership.

## BR Postgres Defaults

Defaults are conventional and must be overridden if the local schema differs:

```bash
--br-postgres-table quotes_1m
--br-postgres-ticker-col ticker
--br-postgres-ts-col ts
--br-postgres-close-col close
```

By default the query strips `.SA` before matching BR stock symbols (`PETR4.SA` ->
`PETR4`). Use `--br-postgres-keep-sa` if the DB stores Yahoo-style tickers.

## Validation Diagnostics

Any result above diagnostic status must report:

| Gate | Threshold | Citation |
|---|---|---|
| PBO | `< 0.5` over the declared variant matrix | `[advances_fin_ml, p.208-211]` |
| DSR | `p < 0.05` with honest `n_trials` | `[advances_fin_ml, p.273-275]` |
| Walk-forward | at least 6/8 positive OOS windows | `[testing_tuning, p.318-320]` |
| OOS | final 30% Sharpe positive | `[testing_tuning, p.327-335]` |
| FWD stress | post-2020 Sharpe positive | `[testing_tuning, p.327-335]` |
| Bootstrap | 99.9% CI low Sharpe > 0 | `[advances_fin_ml, p.196-202]` |
| Cross-implementation | vectorized vs holdings-loop CAGR delta <= 3pp | `[advances_fin_ml, p.31-34]` |

CAGR and MDD are warning tiers under the mandate, not standalone promotion gates.

## Rolling Relative Equity Dominance

Every future result row from the extensive helpers includes a rolling benchmark
dominance diagnostic. For each horizon `3/5/10/15/20y`, starts roll monthly and
both strategy and SPY benchmark equity are reset to `1.0` at the window start:

```text
relative_equity(t) =
  strategy_equity(t) / strategy_equity(window_start)
  ---------------------------------------------------
  benchmark_equity(t) / benchmark_equity(window_start)
```

Window score = percentage of observations with `relative_equity >= 1.0`. Horizon
columns report mean, p25 and minimum scores plus terminal/min-relative diagnostics.
`rolling_rel_score` is the weighted mean of horizon means with weights `3y=10%`,
`5y=15%`, `10y=25%`, `15y=25%`, `20y=25%`; there is intentionally no 30-year
horizon. This is a robustness/dominance diagnostic, not a promotion gate
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.273-275]`.

## Outputs

- `DATA_AUDIT.md`: source readiness and benchmark configuration.
- `REPORT.md`: result table, SPY benchmark comparison and plot links.
- `us/base_results.json`: machine-readable metrics and gates for the initial
  `us_all` base screen.
- `us/{stocks,etfs,mixed}/plots/base/*_vs_SPY.png`: equity, drawdown and
  relative-equity panels per base US config.
- `us/stocks/REPORT_EXTENSIVE.md`: focused US stocks-only extensive grid report.
- `us/stocks/results/extensive_results.csv`: all stocks-only extensive-grid rows.
- `us/stocks/results/extensive_pbo.json`: PBO for the stocks-only grid.
- `us/stocks/plots/extensive/*.png`: aggregate and finalist plots for the
  stocks-only grid.
- `us/stocks/HEATMAP.html`: interactive stocks-only heatmap across mechanism,
  lookback, top-N, rebalance frequency and offset.
- `us/stocks/results/heatmap_results.csv`: all stocks-only heatmap rows.
- `us/stocks/plots/heatmap/*.png`: static heatmaps for Sharpe, CAGR, MDD and
  crisis-window MDD diagnostics.
- `us/stocks/EVOLUTION_REPORT.md`: selected-finalist evolution report across
  fixed/staggered offsets and SPY/stock trend overlays.
- `us/stocks/results/evolution_results.csv` and
  `us/stocks/results/evolution_pbo.json`: machine-readable finalist-evolution
  diagnostics.
- `us/stocks/plots/evolution/*.png`: aggregate and finalist plots for the
  evolved stock rows.
- `us/etfs/REPORT_ETF_STAGGERED.md`: ETF-only follow-up that combines every rebalance
  offset as equal-capital sleeves to reduce timing-luck selection
  `[advances_fin_ml, p.273-275]`.
- `us/etfs/results/staggered_etf_results.csv` and
  `us/etfs/results/staggered_etf_pbo.json`:
  machine-readable ETF staggered diagnostics.
- `us/etfs/plots/etf_staggered/*.png`: aggregate and finalist plots for the ETF
  staggered hypothesis.

## Initial Commands

```bash
uv run python studies/momentum_13612_universes/run.py --audit-only
uv run python studies/momentum_13612_universes/run.py --variant us_all --us-source yfinance --allow-biased-yfinance --max-us-stocks 120 --max-us-etfs 60
uv run python studies/momentum_13612_universes/run.py --variant br_stocks --br-stock-source postgres --start 2010-01-01
uv run python studies/momentum_13612_universes/run.py --variant br_mixed --br-stock-source postgres --allow-biased-yfinance --start 2010-01-01
uv run python studies/momentum_13612_universes/run_extensive.py --allow-biased-yfinance --max-us-stocks 120 --max-us-etfs 60 --top-n 1,3,5,10,15,20 --rebalance-months 1,3,6,12 --start 2010-01-01
uv run python studies/momentum_13612_universes/run_etf_staggered.py --allow-biased-yfinance --max-us-etfs 9999 --top-n 3,5,10 --rebalance-months 3,6,12 --start 2000-01-01
uv run python studies/momentum_13612_universes/run_stocks_heatmap.py --allow-biased-yfinance --max-us-stocks 9999 --top-n 1,3,5,10,15,20 --rebalance-months 1,3,6,12 --lookbacks 3,6,12,3_6_12,6_12,1_3_6_12 --start 1990-01-01
uv run python studies/momentum_13612_universes/run_stocks_evolution.py --allow-biased-yfinance --max-us-stocks 9999 --start 1990-01-01
uv run python studies/momentum_13612_universes/run_stocks_heatmap.py --allow-biased-yfinance --us-stock-universe sp500_wikipedia_pit --max-us-stocks 9999 --top-n 5 --rebalance-months 3 --lookbacks 6 --mechanisms raw_equal --start 2000-01-01
uv run python studies/momentum_13612_universes/run_stocks_heatmap.py --allow-biased-yfinance --us-stock-universe sp500_wikipedia_pit --max-us-stocks 9999 --top-n 5 --rebalance-months 3 --lookbacks 6 --mechanisms raw_equal --start 2000-01-01 --max-abs-daily-return 10
```

## 2026-06-16 ETF Staggered Verdict

The focused ETF-only hypothesis tested raw 13612 and raw inverse-vol sizing over
top-N `{3,5,10}` and rebalance `{3,6,12}`. Each rebalance offset was an
equal-capital sleeve instead of a selectable parameter. Best after-tax Sharpe was
`raw_inverse_vol_top10_reb3_staggered`: CAGR `10.15%`, MDD `-30.24%`, Sharpe
`0.683`, turnover `2.19x/ano`. No row kept MDD above `-30%`, and panel PBO was
`0.663` fail. Verdict: screen-only FAIL; no further local promotion work without
PIT/delisted ETF data and a materially different hypothesis `[advances_fin_ml,
p.208-211]`.

## 2026-06-16 US Stocks Finalist Evolution Verdict

The selected-finalist evolution starts from six stocks heatmap finalists and
crosses fixed/staggered offsets with SPY SMA200 monthly/daily overlays, stock
SMA100 overlays and combinations. The overlays are diagnostics grounded in
Clenow/Gayed trend-filter literature, not promotion claims
`[stocks_on_the_move, p.66-67, p.81-82, p.98-99]`,
`[leverage_for_the_long_run, p.9, p.13, p.16]`.

Best after-tax Sharpe remains aggressive:
`evo_aggressive_raw_lb6_top5_q_staggered_off0_stock_sma100`, CAGR `55.88%`, MDD
`-62.36%`, Sharpe `1.401`. The best constrained row with CAGR `>=15%` and MDD
`>=-40%` is
`evo_balanced_voladj_lb6_top5_q_staggered_off0_market_sma200_monthly`, CAGR
`26.89%`, MDD `-39.35%`, Sharpe `1.085`, GFC MDD `-17.46%`. The best Sharpe row
with MDD `>=-30%` is
`evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_daily`,
CAGR `11.12%`, MDD `-24.15%`, Sharpe `0.859`.

Panel PBO over all `72` evolved rows is `0.000`, but mechanism-level PBO fails
(`0.623` to `0.778`) and the rows were selected after the heatmap. Verdict:
post-selection diagnostics only; no validation or promotion
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.

Follow-up infrastructure now supports `sp500_wikipedia_pit` for the stocks heatmap
and finalist-evolution runners. A small in-memory smoke over `2020-2021` confirmed
the dynamic universe path and exposed the expected residual blocker: removed or
delisted names such as `ABMD`, `ADS` and `AGN` can enter the reconstructed
eligible set, but yfinance may return no price history. This mode is therefore a
bias-reduction diagnostic, not a survivorship-free dataset `[advances_fin_ml,
p.208-211]`.

The first full PIT-ish rerun also exposed yfinance adjusted-close artifacts: the
strategy held `CFC`/`TIE` on days where cached adjusted prices imply impossible
daily returns. `--max-abs-daily-return 10` was added as an explicit data-quality
guard; reruns without it can produce meaningless million-percent CAGRs
`[advances_fin_ml, p.31-34]`, `[advances_fin_ml, p.208-211]`.

With that guard, the first focused PIT-ish rerun (`sp500_wikipedia_pit`, `lb6`,
top5, quarterly all offsets, start `2000-01-01`) dropped `9` broken yfinance
series (`BMC/CBE/CFC/CPWR/MEE/MI/PTV/RSH/TIE`). Best after-tax Sharpe was
`raw_equal_lb6_top5_reb3_off0`: CAGR `29.35%`, MDD `-65.68%`, Sharpe `0.880`,
terminal/SPY `92.4x`; the other offsets were `28.15%`/`-67.45%`/`0.859` and
`21.01%`/`-77.34%`/`0.692`. Reading: the current-universe headline was heavily
inflated, but the PIT-ish diagnostic still shows momentum signal with ruin-level
drawdown and no promotion path without true delisted/PIT data
`[advances_fin_ml, p.208-211]`.

## Caveats

- Extensive and staggered reports rank after Brazil's annual 15% realized-gain
  tax approximation, but remain gross of transaction costs/slippage.
- BR ETFs are a curated current list, not a PIT universe.
- US yfinance screens should be treated like discovery dashboards, not evidence.
