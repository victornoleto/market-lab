# US Stocks 13612 Extensive Screen

Status: research-only diagnostic. No deployment, paper-trade label or mandate
change.

This folder contains the focused US stocks-only 13612 screen requested after the
broader US grid. The implementation remains in the shared study runner
`../../run_extensive.py`; this directory keeps the generated stock-universe
evidence together.

## Scope

- Universe: current S&P 500 via yfinance (`us_stocks`).
- Source: yfinance current universe, therefore `promotion_eligible=false` until
  PIT/delisted validation exists `[advances_fin_ml, p.208-211]`.
- Start: `2000-01-01`.
- Top-N: `1,3,5,10,15,20`.
- Rebalance frequencies: `1,3,6,12` months with all offsets.
- Mechanisms: raw 13612, 13612/vol, Clenow trend, 70/30 momentum+low-vol,
  inverse-vol weights, and raw absolute cash filter `[stocks_on_the_move, p.60]`,
  `[stocks_on_the_move, p.70-77, p.98]`, `[systematic_trading, p.137-148]`.
- Ranking metric: after-tax returns under Brazil's annual 15% realized-gain
  approximation.

## Command

```bash
uv run python studies/momentum_13612_universes/run_extensive.py --allow-biased-yfinance --universes us_stocks --max-us-stocks 9999 --max-us-etfs 60 --top-n 1,3,5,10,15,20 --rebalance-months 1,3,6,12 --start 2000-01-01 --max-finalists 30
```

## Verdict

Best after-tax Sharpe row:

- `mom13612_us_stocks_raw_inverse_vol_top3_reb3_off0`
- CAGR `65.67%`
- MDD `-78.50%`
- Sharpe `1.359`
- PBO all/stocks `0.321`

Conclusion: screen-only FAIL. The return is extreme, but drawdown is
ruin-adjacent and the data are current-universe/survivorship-biased. This is not
a promotable lead.

## Current-Universe Heatmap Diagnostics

The 2026-06-16 heatmap run expands the stocks-only study to `1990-01-01` using
the current S&P 500 yfinance universe. It tests lookback profiles
`3,6,12,3_6_12,6_12,1_3_6_12`, top-N `1,3,5,10,15,20`, rebalance frequencies
`1,3,6,12`, all offsets, and the existing mechanisms. Clenow is included once as
`trend126d` because it does not use the momentum lookback dimension.

Command:

```bash
uv run python studies/momentum_13612_universes/run_stocks_heatmap.py --allow-biased-yfinance --max-us-stocks 9999 --top-n 1,3,5,10,15,20 --rebalance-months 1,3,6,12 --lookbacks 3,6,12,3_6_12,6_12,1_3_6_12 --start 1990-01-01
```

Key readings:

- Best Sharpe: `raw_equal_lb6_top5_reb3_off0`, after-tax CAGR `59.32%`, MDD
  `-59.04%`, Sharpe `1.380`; GFC MDD also `-59.04%`.
- Better return/risk region: `vol_adjusted_13612_lb6_top5_reb3_off0`, CAGR
  `35.18%`, MDD `-43.98%`, Sharpe `1.110`.
- Defensive region: `composite_mom_lowvol_lb12_top15_reb12_off6`, CAGR `16.90%`,
  MDD `-34.44%`, Sharpe `0.897`.
- `23` rows reached CAGR `>=20%` with MDD `>=-50%`; `78` rows reached CAGR
  `>=12%` with MDD `>=-40%`.

The GFC window often dominates full-period MDD, but the 1990 extension is more
biased than PIT data because it uses current constituents only
`[advances_fin_ml, p.208-211]`.

## Focused `raw_abs_cash_lb6_top5_reb3_off0` Analysis

Command, pinned to the last completed yfinance session to avoid current-day cache
drift:

```bash
uv run python studies/momentum_13612_universes/run_stocks_strategy_analysis.py --allow-biased-yfinance --max-us-stocks 9999 --start 1990-01-01 --end 2026-06-15
```

The deep dive reconstructs `mom13612_us_stocks_raw_abs_cash_lb6_top5_reb3_off0`,
compares it with `raw_equal_lb6_top5_reb3_off0` and
`raw_inverse_vol_lb6_top5_reb3_off0`, and writes
`ANALYSIS_raw_abs_cash_lb6_top5_reb3_off0.md` plus CSV/JSON/PNG artifacts.

Key reading: the absolute/cash filter had no effect on this exact path. The
analysis found `0` differing daily weight rows, `0` differing rebalance rows,
`100%` average/min gross exposure and `0` rebalances below full exposure versus
the raw equal-weight row. The pinned rerun shows CAGR `59.66%`, MDD `-59.04%`,
Sharpe `1.386` and `rolling_rel_score` `96.28%`, but this is still an aggressive
current-universe yfinance result, not a promotable cash-filter improvement
`[stocks_on_the_move, p.60]`, `[advances_fin_ml, p.208-211]`.

The enhanced report adds log-scale plots for target vs SPY, adjacent mechanisms,
Top-20 After-Tax Sharpe, Top-20 Rolling Relative and SPY blends with `5/10/20/30%`
strategy sleeves. The sleeve conclusion is intentionally conservative: in the
biased sample, blends improve CAGR and terminal wealth, but this is not allocation
evidence. Real-capital weight remains `0%` until PIT/delisted data, independent
validation, real friction/tax and actual-core portfolio tests exist
`[advances_fin_ml, p.273-275]`.

## Wikipedia PIT-ish Follow-up

To test how much of the headline was caused by current-constituent leakage, the
stocks heatmap/evolution runners now accept `--us-stock-universe
sp500_wikipedia_pit`. This reconstructs S&P 500 membership by month-end from
Wikipedia's selected historical changes and masks rank candidates at each
rebalance. It reduces survivorship bias, but it is not a true survivorship-free
dataset: Wikipedia changes are incomplete, and yfinance still lacks many
removed/delisted price series and delisting returns `[advances_fin_ml, p.208-211]`.

The first PIT-ish run without a data-quality guard was invalidated. The strategy
held stale/broken yfinance adjusted-close series, especially `CFC` and `TIE`, on
days with impossible daily returns. The runners now support
`--max-abs-daily-return`, which drops tickers whose adjusted-close daily return
exceeds the threshold in absolute value. This is a data-quality filter, not a
strategy signal `[advances_fin_ml, p.31-34]`.

Focused rerun command:

```bash
uv run python studies/momentum_13612_universes/run_stocks_heatmap.py --allow-biased-yfinance --us-stock-universe sp500_wikipedia_pit --max-us-stocks 9999 --top-n 5 --rebalance-months 3 --lookbacks 6 --mechanisms raw_equal --start 2000-01-01 --max-abs-daily-return 10
```

Rerun confirmations:

- yfinance returned no data for historical `YHOO`, as expected for a delisted
  ticker in this source.
- The data-quality guard dropped `9` broken series: `BMC`, `CBE`, `CFC`, `CPWR`,
  `MEE`, `MI`, `PTV`, `RSH`, `TIE`.
- This focused PIT-ish rerun is a diagnostic comparison against the full
  current-universe heatmap, not a promotion dataset.

Focused PIT-ish results:

| Offset | CAGR | MDD | Sharpe | Terminal/SPY | Rolling Relative |
|---:|---:|---:|---:|---:|---:|
| 0 | `29.35%` | `-65.68%` | `0.880` | `92.4x` | `91.52%` |
| 1 | `28.15%` | `-67.45%` | `0.859` | `75.6x` | `88.88%` |
| 2 | `21.01%` | `-77.34%` | `0.692` | `16.1x` | `72.55%` |

Interpretation: the current-universe headline (`~59%` CAGR) was heavily inflated
by survivorship/data artifacts. The PIT-ish filtered rerun still shows a real
momentum signal, but drawdown is ruin-level (`-66%` to `-77%`) and true delisting
returns are still missing. This remains diagnostic only, not a promotable lead
`[advances_fin_ml, p.208-211]`.

## Finalist Evolution

The 2026-06-16 evolution runner starts from six heatmap finalists and tests
fixed vs staggered offsets plus SPY SMA200 and stock SMA100 overlays. These
filters are diagnostics grounded in Clenow/Gayed, not a promotion claim
`[stocks_on_the_move, p.66-67, p.81-82, p.98-99]`,
`[leverage_for_the_long_run, p.9, p.13, p.16]`.

Command:

```bash
uv run python studies/momentum_13612_universes/run_stocks_evolution.py --allow-biased-yfinance --max-us-stocks 9999 --start 1990-01-01
```

Key readings:

- Best Sharpe remains aggressive: `aggressive_raw_lb6_top5_q + stock_sma100 +
  staggered`, CAGR `55.88%`, MDD `-62.36%`, Sharpe `1.401`.
- Best return/risk trade-off under MDD near `-40%`: `balanced_voladj_lb6_top5_q +
  market_sma200_monthly + staggered`, CAGR `26.89%`, MDD `-39.35%`, Sharpe
  `1.085`, GFC MDD `-17.46%`.
- Defensive profile: `defensive_composite_lb6_12_top20_y + market_sma200_daily +
  staggered`, CAGR `11.12%`, MDD `-24.15%`, Sharpe `0.859`, GFC MDD `-8.04%`.
- Overall PBO is low, but mechanism-level PBO fails (`0.62` to `0.78`), so this
  is still post-selection diagnostics rather than validation.

## Rolling Relative Dominance

New reruns add `rolling_rel_score` columns to CSV/JSON outputs. The metric rolls
monthly windows of `3/5/10/15/20y`, resets strategy and SPY equity to `1.0` at
each window start, and scores the percentage of observations where
`strategy/SPY >= 1.0`. The overall score weights horizon means as
`10%/15%/25%/25%/25%`; p25 and min variants are kept as fragility diagnostics.
This directly captures whether a higher-drawdown strategy still stayed above the
benchmark across many start dates `[testing_tuning, p.327-335]`.

## Files

- `REPORT_EXTENSIVE.md`: full stocks-only report.
- `results/extensive_results.csv`: all 792 rows.
- `results/extensive_results.json`: JSON copy of all rows.
- `results/extensive_pbo.json`: PBO summary.
- `results/extensive_finalists.csv`: diagnostic finalists.
- `results/heatmap_results.csv`: latest heatmap run rows. The current full
  current-universe run has `4,092` rows; focused PIT-ish reruns should be treated
  as separate diagnostics if regenerated.
- `results/heatmap_results.json`: JSON copy of the latest heatmap rows.
- `results/evolution_results.csv`: all 72 finalist-evolution rows.
- `results/evolution_results.json`: JSON copy of evolution rows.
- `results/evolution_pbo.json`: PBO summary for evolved finalists.
- `results/analysis_raw_abs_cash_lb6_top5_reb3_off0_*.csv/json`: focused
  `raw_abs_cash_lb6_top5_reb3_off0` analysis artifacts.
- `plots/base/`: stock plots from the initial base `us_all` run.
- `plots/extensive/`: aggregate plots and finalist plots.
- `plots/heatmap/`: static heatmaps for Sharpe, CAGR, MDD, GFC MDD and dot-com MDD.
- `plots/evolution/`: scatter/bar plots and finalist equity plots for evolved rows.
- `plots/analysis/`: focused `raw_abs_cash_lb6_top5_reb3_off0` plots.
- `HEATMAP.html`: interactive local heatmap for the latest heatmap run.
- `HEATMAP_REPORT.md`: summary for the latest heatmap run.
- `EVOLUTION_REPORT.md`: finalist evolution report.
- `ANALYSIS_raw_abs_cash_lb6_top5_reb3_off0.md`: focused cash-filter audit.
