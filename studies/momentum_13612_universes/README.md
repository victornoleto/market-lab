# Momentum 13612 Universes

Status: research-only. No deployment, no paper-trade label and no mandate change.

This folder tests pure cross-sectional momentum across US/BR stocks, ETFs and
mixed universes. The core idea is deliberately simpler than HAA: rank assets by
momentum, hold the top names, and compare the resulting return stream with SPY.
All yfinance/current-universe results are `promotion_eligible=false` until true
point-in-time membership, delisted returns and corporate-action validation exist
`[advances_fin_ml, p.208-211]`.

## Executive Verdict

The study found a strong diagnostic momentum signal in current-universe US stocks,
but no promotable strategy.

Main reasons:

- Current S&P 500 yfinance screens are heavily survivorship-biased.
- The most attractive stock rows have crisis drawdowns around `-55%` to `-70%`.
- The focused PIT-ish rerun still has ruin-level drawdown and no true delisted returns.
- ETF-only staggered-offset testing failed economically and statistically.
- Finalist evolution is post-heatmap selection; mechanism-level PBO fails.
- The focused `raw_abs_cash_lb6_top5_reb3_off0` cash filter never actually went to cash.

Practical conclusion: useful research signal, `0%` real-capital allocation under
the current evidence state.

## What Was Built

| File | Purpose |
|---|---|
| `core.py` | Pure 13612 monthly momentum engine, shifted weights, metrics. |
| `universes.py` | US/BR universe definitions, yfinance/Tiingo loaders, BR Postgres 1m daily-close hook, PIT-ish Wikipedia S&P 500 membership. |
| `extensive.py` | Extended mechanisms, inverse-vol sizing, absolute/cash filter, after-tax approximation, turnover, rolling relative dominance. |
| `run.py` | Base six-universe runner. |
| `run_extensive.py` | Broad US-only grid across universes/mechanisms/top-N/rebalance offsets. |
| `run_stocks_heatmap.py` | US stocks heatmap over lookbacks, mechanisms, top-N, rebalance frequency and offsets. |
| `run_stocks_evolution.py` | Post-heatmap finalist evolution with staggered offsets and SMA overlays. |
| `run_etf_staggered.py` | ETF-only test that combines all rebalance offsets as sleeves. |
| `run_stocks_strategy_analysis.py` | Focused deep dive for `raw_abs_cash_lb6_top5_reb3_off0`, including log plots, top-20 comparisons and sleeve blends. |
| `SPEC.md` | Technical spec, data policy, commands and validation notes. |
| `DATA_AUDIT.md` | Data-readiness audit. |
| `REPORT.md` | Initial base run report. |
| `docs/specs/momentum_13612_universes.md` | Public technical spec. |
| `tests/test_momentum_13612_universes.py` | Focused tests for tax, rolling relative, staggered offsets, PIT-ish membership and overlays. |

## Strategy Family

The base rule is pure monthly 13612U cross-sectional momentum:

1. At each month-end, compute each asset momentum as the average of 1, 3, 6 and
   12 month returns `[stocks_on_the_move, p.60]`.
2. Rank assets cross-sectionally by score descending.
3. Hold top-N assets equal weight.
4. Apply weights only to future daily returns to avoid lookahead
   `[advances_fin_ml, p.31-34]`.
5. Use SPY adjusted close as the US benchmark proxy.

Later diagnostics add:

- single-lookback profiles, especially `lb6`;
- inverse-volatility weights `[systematic_trading, p.137-148]`;
- Clenow trend score `[stocks_on_the_move, p.70-77, p.98]`;
- momentum plus low-vol composite;
- absolute/cash filter;
- fixed offsets and staggered offsets;
- SPY SMA200 and stock SMA100 overlays `[stocks_on_the_move, p.66-67, p.81-82, p.98-99]`, `[leverage_for_the_long_run, p.9, p.13, p.16]`;
- rolling relative dominance over `3/5/10/15/20y` windows `[testing_tuning, p.327-335]`.

## Data Policy

| Source | Status |
|---|---|
| US yfinance current S&P 500 | Screen-only; survivorship-biased; not promotable. |
| US yfinance curated ETFs | Screen-only; current curated list; not promotable. |
| Tiingo manifest | Can define universe, but price parquets are required for real runs. |
| Wikipedia S&P 500 PIT-ish | Reduces current-constituent leakage, but incomplete and still lacks true delisted returns. |
| BR Postgres 1m | Hook implemented; not promotion-ready until adjusted prices/corporate actions/PIT are audited. |
| BR ETFs yfinance | Curated current list; screen-only. |

## Timeline Of Work

| Step | Output | Reading |
|---|---|---|
| Base six-universe scaffold | `run.py`, `REPORT.md`, `us/base_results.json` | Initial proof that current-universe US stocks have high diagnostic momentum but no promotion eligibility. |
| Extensive US grid | `run_extensive.py`, `us/stocks/REPORT_EXTENSIVE.md` | Broad mechanisms/top-N/rebalance sweep; stocks/mixed subgroups remain biased and drawdown-heavy. |
| Stocks-only full S&P 500 rerun | `us/stocks/results/extensive_results.json` | Start 2000, 792 rows; strongest Sharpe row has extreme CAGR but ruin-adjacent MDD. |
| 1990+ heatmap | `run_stocks_heatmap.py`, `HEATMAP.html`, `HEATMAP_REPORT.md` | 4,092-row map; `lb6` is the strongest aggressive region. |
| Rolling relative dominance | `extensive.py`, heatmap/evolution outputs | Added reset-window relative equity score to measure strategy/SPY dominance across start dates. |
| Finalist plots | `us/stocks/plots/heatmap/finalists/` | Top Sharpe and Top Rolling Relative rows plotted vs SPY. |
| Finalist evolution | `run_stocks_evolution.py`, `EVOLUTION_REPORT.md` | Tested staggered offsets and SMA overlays on 72 rows. |
| ETF staggered follow-up | `run_etf_staggered.py`, `us/etfs/REPORT_ETF_STAGGERED.md` | Cleaner offset hypothesis failed. |
| PIT-ish follow-up | `--us-stock-universe sp500_wikipedia_pit` | Reduced current-constituent leakage, but drawdown remained ruin-level and yfinance artifacts required filtering. |
| Focused strategy analysis | `run_stocks_strategy_analysis.py`, `ANALYSIS_raw_abs_cash_lb6_top5_reb3_off0.md` | Showed the cash filter did not change holdings; added log plots and sleeve diagnostics. |

## Best And Most Important Results

### Initial Base Run

Initial US yfinance base run used limited US stocks/ETFs and pure 13612U.

| Row | CAGR | MDD | Sharpe | Promotion |
|---|---:|---:|---:|---|
| `mom13612_us_stocks_top4` | `32.07%` | `-41.72%` | `1.023` | No |
| `mom13612_us_stocks_top10` | `26.16%` | `-37.16%` | `1.072` | No |
| `mom13612_us_stocks_top20` | `21.85%` | `-36.68%` | `1.060` | No |
| `mom13612_us_etfs_top20` | `10.95%` | `-21.57%` | `0.817` | No |

PBO for the initial panel: `0.504`, fail.

### Stocks-Only Extensive Run, Start 2000

The user-directed full current-S&P-500 stocks-only run tested `792` after-tax rows.

| Best row | CAGR | MDD | Sharpe | PBO |
|---|---:|---:|---:|---:|
| `raw_inverse_vol_top3_reb3_off0` | `65.67%` | `-78.50%` | `1.359` | `0.321` |

Reading: huge current-universe headline, but drawdown is ruin-adjacent and the row
is not investable.

### 1990+ Stocks Heatmap, 4,092 Rows

This is the main diagnostic map for US stocks.

| Category | Row | CAGR | MDD | Sharpe | Notes |
|---|---|---:|---:|---:|---|
| Best Sharpe | `raw_equal_lb6_top5_reb3_off0` | `59.24%` to `59.32%` | `-59.04%` | `1.379` to `1.380` | Aggressive, current-universe biased. |
| Same path with cash filter | `raw_abs_cash_lb6_top5_reb3_off0` | `59.24%` to `59.32%` | `-59.04%` | `1.379` to `1.380` | Cash filter did not change holdings. |
| Best inverse-vol near top | `raw_inverse_vol_lb6_top5_reb3_off0` | `55.80%` | `-54.99%` | `1.355` | Slightly lower drawdown, similar dominance. |
| Balanced region | `vol_adjusted_lb6_top5_reb3_off0` | `35.18%` | `-43.98%` | `1.110` | Better risk/return trade-off. |
| Defensive region | `composite_lb12_top15_reb12_off6` | `16.90%` | `-34.44%` | `0.897` | Lower return, lower drawdown. |

Interpretation: `lb6` is the strongest discovered region, but this is exactly the
kind of result that needs PIT/delisted confirmation and overfit accounting
`[advances_fin_ml, p.273-275]`.

### Rolling Relative Dominance

Rolling relative dominance resets strategy and SPY to `1.0` at each monthly start
and measures how often `strategy/SPY >= 1.0`.

| Category | Row | Rolling Relative | P25 | Min | CAGR | MDD |
|---|---|---:|---:|---:|---:|---:|
| Best overall rolling relative | `raw_equal_lb1_3_6_12_top15_reb3_off0` | `96.75%` | `96.08%` | `32.32%` | `38.34%` | `-57.13%` |
| Top `top10 reb1` rolling relative | `clenow_equal_trend126d_top10_reb1_off0` | `96.69%` | `95.44%` | `40.53%` | `43.51%` | `-58.19%` |
| Target focused path | `raw_abs_cash_lb6_top5_reb3_off0` | `96.28%` | `95.17%` | `19.18%` | `59%+` | `-59.04%` |

Interpretation: many start windows beat SPY, especially over long horizons, but
short 3-year windows can still be weak. This is useful diagnostics, not a gate.

### Finalist Evolution, 72 Rows

Evolution tested selected heatmap finalists with fixed/staggered offsets and SMA
overlays. These rows are post-selection diagnostics.

| Category | Row | CAGR | MDD | Sharpe | Notes |
|---|---|---:|---:|---:|---|
| Best Sharpe | `aggressive_raw_lb6_top5_q_staggered_off0_stock_sma100` | `55.88%` | `-62.36%` | `1.401` | Still aggressive and high drawdown. |
| Best with CAGR >= 15% and MDD >= -40% | `balanced_voladj_lb6_top5_q_staggered_off0_market_sma200_monthly` | `26.89%` | `-39.35%` | `1.085` | Best constrained diagnostic. |
| Best Sharpe with MDD >= -30% | `defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_daily` | `11.12%` | `-24.15%` | `0.859` | Defensive, but return modest. |

Overall PBO over evolved rows was `0.000`, but mechanism-level PBO failed
(`0.623..0.778`) and the effective trial count includes the prior heatmap. No
promotion.

### ETF Staggered Follow-Up

ETF-only test combined every rebalance offset as equal-capital sleeves, avoiding
selection of a lucky month.

| Best row | CAGR | MDD | Sharpe | PBO | Verdict |
|---|---:|---:|---:|---:|---|
| `raw_inverse_vol_top10_reb3_staggered` | `10.15%` | `-30.24%` | `0.683` | `0.663` | FAIL |

Interpretation: the cleaner ETF hypothesis did not produce a useful candidate.

### PIT-ish S&P 500 Follow-Up

The PIT-ish path masks each rebalance to Wikipedia-reconstructed S&P 500 members.
It is still incomplete and lacks true delisted returns.

The first full rerun exposed impossible yfinance adjusted-close jumps in historical
tickers. The data-quality guard `--max-abs-daily-return 10` dropped `9` broken
series: `BMC`, `CBE`, `CFC`, `CPWR`, `MEE`, `MI`, `PTV`, `RSH`, `TIE`.

Focused result, start 2000, `lb6`, top5, quarterly:

| Offset | CAGR | MDD | Sharpe | Terminal/SPY | Rolling Relative |
|---:|---:|---:|---:|---:|---:|
| `0` | `29.35%` | `-65.68%` | `0.880` | `92.4x` | `91.52%` |
| `1` | `28.15%` | `-67.45%` | `0.859` | `75.6x` | `88.88%` |
| `2` | `21.01%` | `-77.34%` | `0.692` | `16.1x` | `72.55%` |

Interpretation: survivorship mitigation reduced the headline materially, but the
signal did not disappear. It remains non-promotable because drawdown is ruin-level
and true delisting returns are still missing.

### Focused `raw_abs_cash_lb6_top5_reb3_off0` Analysis

Report:
`us/stocks/ANALYSIS_raw_abs_cash_lb6_top5_reb3_off0.md`

Pinned rerun through `2026-06-15`:

| Metric | Value |
|---|---:|
| CAGR | `59.66%` |
| MDD | `-59.04%` |
| Sharpe | `1.386` |
| Rolling relative score | `96.28%` |
| Terminal/SPY | `190415x` |
| Daily weight differences vs raw equal | `0` |
| Rebalance differences vs raw equal | `0` |
| Min/avg gross exposure | `100%` |

Conclusion: the `raw_abs_cash` label is misleading for this exact path. The cash
filter never reduced exposure, so the row is equivalent to raw equal-weight `lb6`
top5 quarterly rotation.

Sleeve blend diagnostics versus SPY:

| Blend | CAGR | MDD | Sharpe | Terminal/SPY |
|---|---:|---:|---:|---:|
| `5% strategy / 95% SPY` | `13.20%` | `-54.01%` | `0.752` | `1.997x` |
| `10% strategy / 90% SPY` | `15.54%` | `-52.98%` | `0.846` | `3.954x` |
| `20% strategy / 80% SPY` | `20.28%` | `-52.50%` | `1.005` | `15.091x` |
| `30% strategy / 70% SPY` | `25.08%` | `-52.18%` | `1.125` | `55.601x` |

Reading: the biased sample makes small sleeves look attractive, but this is not
allocation evidence. Real-capital weight remains `0%` until PIT/delisted data,
independent validation, real friction/tax and actual-core portfolio testing exist.

## Important Plots And Reports

| Artifact | What it shows |
|---|---|
| `us/stocks/HEATMAP.html` | Interactive current-universe stocks heatmap. |
| `us/stocks/HEATMAP_REPORT.md` | Top 20 by Sharpe and rolling relative score. |
| `us/stocks/EVOLUTION_REPORT.md` | Finalist evolution and constrained rows. |
| `us/stocks/ANALYSIS_raw_abs_cash_lb6_top5_reb3_off0.md` | Focused target strategy deep dive. |
| `us/stocks/plots/analysis/*_log_equity.png` | Log-scale target vs SPY, Top-20, adjacent mechanisms and sleeve blends. |
| `us/etfs/REPORT_ETF_STAGGERED.md` | ETF staggered-offset failure. |

## Reproduction Commands

Base audit and US base screen:

```bash
uv run python studies/momentum_13612_universes/run.py --audit-only
uv run python studies/momentum_13612_universes/run.py --variant us_all --us-source yfinance --allow-biased-yfinance --max-us-stocks 120 --max-us-etfs 60
```

US stocks extensive run:

```bash
uv run python studies/momentum_13612_universes/run_extensive.py --allow-biased-yfinance --universes us_stocks --max-us-stocks 9999 --max-us-etfs 60 --top-n 1,3,5,10,15,20 --rebalance-months 1,3,6,12 --start 2000-01-01 --max-finalists 30
```

US stocks 1990 heatmap:

```bash
uv run python studies/momentum_13612_universes/run_stocks_heatmap.py --allow-biased-yfinance --max-us-stocks 9999 --top-n 1,3,5,10,15,20 --rebalance-months 1,3,6,12 --lookbacks 3,6,12,3_6_12,6_12,1_3_6_12 --start 1990-01-01
```

US stocks finalist evolution:

```bash
uv run python studies/momentum_13612_universes/run_stocks_evolution.py --allow-biased-yfinance --max-us-stocks 9999 --start 1990-01-01
```

ETF staggered follow-up:

```bash
uv run python studies/momentum_13612_universes/run_etf_staggered.py --allow-biased-yfinance --max-us-etfs 9999 --top-n 3,5,10 --rebalance-months 3,6,12 --start 2000-01-01 --max-finalists 12
```

PIT-ish focused rerun with data-quality guard:

```bash
uv run python studies/momentum_13612_universes/run_stocks_heatmap.py --allow-biased-yfinance --us-stock-universe sp500_wikipedia_pit --max-us-stocks 9999 --top-n 5 --rebalance-months 3 --lookbacks 6 --mechanisms raw_equal --start 2000-01-01 --max-abs-daily-return 10
```

Focused target strategy analysis:

```bash
uv run python studies/momentum_13612_universes/run_stocks_strategy_analysis.py --allow-biased-yfinance --max-us-stocks 9999 --start 1990-01-01 --end 2026-06-15
```

Verification used during development:

```bash
uv run ruff check studies/momentum_13612_universes tests/test_momentum_13612_universes.py
uv run pytest tests/test_momentum_13612_universes.py tests/test_haa_hybrid_asset_allocation.py
```

Latest focused verification result: `28 passed`.

## Final Reading

The study supports three conclusions:

1. Cross-sectional momentum in current-universe US stocks is a strong diagnostic
   signal, especially around `lb6` and top 5 to top 20 baskets.
2. Drawdown and data bias are too large for a real allocation decision.
3. The only acceptable next step would be a clean PIT/delisted dataset and a new
   pre-registered validation pass; until then this folder is evidence, not a
   strategy to trade.
