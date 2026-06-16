# Momentum 13612 Universe Study Report

Status: research-only. No deployment, paper-trade label or mandate change.

## Verdict

Screen-only FAIL: no result row is promotion-eligible. yfinance/current-list and unaudited Postgres 1m rows cannot support a winner without PIT/delisted and corporate-action validation `[advances_fin_ml, p.208-211]`.

## Method

Pure monthly 13612U cross-sectional rotation: rank each universe by the equal-weighted mean of 1/3/6/12-month returns, hold top-N equal weight, and apply month-end weights only to subsequent daily returns. Momentum and monthly cadence are anchored in `[stocks_on_the_move, p.60]` and `[stocks_on_the_move, p.98-99]`; validation diagnostics follow `[advances_fin_ml, p.208-211]` and `[advances_fin_ml, p.273-275]`.

## Results

| Config | Variant | Source | Assets | Window | CAGR | SPY CAGR | Excess CAGR | MDD | SPY MDD | Sharpe | SPY Sharpe | Calmar | Gates ex-PBO | Promotion eligible | Plot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom13612_us_stocks_top4 | us_stocks | yfinance | 120 | 2011-01-31..2026-06-15 | 32.07% | 14.22% | 17.85% | -41.72% | -33.72% | 1.023 | 0.863 | 0.769 | 6/6 | False | [mom13612_us_stocks_top4_vs_SPY.png](us/stocks/plots/base/mom13612_us_stocks_top4_vs_SPY.png) |
| mom13612_us_stocks_top10 | us_stocks | yfinance | 120 | 2011-01-31..2026-06-15 | 26.16% | 14.22% | 11.94% | -37.16% | -33.72% | 1.072 | 0.863 | 0.704 | 6/6 | False | [mom13612_us_stocks_top10_vs_SPY.png](us/stocks/plots/base/mom13612_us_stocks_top10_vs_SPY.png) |
| mom13612_us_stocks_top20 | us_stocks | yfinance | 120 | 2011-01-31..2026-06-15 | 21.85% | 14.22% | 7.63% | -36.68% | -33.72% | 1.060 | 0.863 | 0.596 | 6/6 | False | [mom13612_us_stocks_top20_vs_SPY.png](us/stocks/plots/base/mom13612_us_stocks_top20_vs_SPY.png) |
| mom13612_us_etfs_top4 | us_etfs | yfinance | 60 | 2011-01-31..2026-06-15 | 9.94% | 14.22% | -4.28% | -39.76% | -33.72% | 0.551 | 0.863 | 0.250 | 4/6 | False | [mom13612_us_etfs_top4_vs_SPY.png](us/etfs/plots/base/mom13612_us_etfs_top4_vs_SPY.png) |
| mom13612_us_etfs_top10 | us_etfs | yfinance | 60 | 2011-01-31..2026-06-15 | 10.71% | 14.22% | -3.51% | -30.37% | -33.72% | 0.723 | 0.863 | 0.353 | 5/6 | False | [mom13612_us_etfs_top10_vs_SPY.png](us/etfs/plots/base/mom13612_us_etfs_top10_vs_SPY.png) |
| mom13612_us_etfs_top20 | us_etfs | yfinance | 60 | 2011-01-31..2026-06-15 | 10.95% | 14.22% | -3.27% | -21.57% | -33.72% | 0.817 | 0.863 | 0.508 | 6/6 | False | [mom13612_us_etfs_top20_vs_SPY.png](us/etfs/plots/base/mom13612_us_etfs_top20_vs_SPY.png) |
| mom13612_us_mixed_top4 | us_mixed | yfinance | 180 | 2011-01-31..2026-06-15 | 32.75% | 14.22% | 18.53% | -39.64% | -33.72% | 1.037 | 0.863 | 0.826 | 6/6 | False | [mom13612_us_mixed_top4_vs_SPY.png](us/mixed/plots/base/mom13612_us_mixed_top4_vs_SPY.png) |
| mom13612_us_mixed_top10 | us_mixed | yfinance | 180 | 2011-01-31..2026-06-15 | 24.37% | 14.22% | 10.15% | -37.16% | -33.72% | 1.010 | 0.863 | 0.656 | 6/6 | False | [mom13612_us_mixed_top10_vs_SPY.png](us/mixed/plots/base/mom13612_us_mixed_top10_vs_SPY.png) |
| mom13612_us_mixed_top20 | us_mixed | yfinance | 180 | 2011-01-31..2026-06-15 | 20.71% | 14.22% | 6.49% | -34.44% | -33.72% | 1.015 | 0.863 | 0.601 | 6/6 | False | [mom13612_us_mixed_top20_vs_SPY.png](us/mixed/plots/base/mom13612_us_mixed_top20_vs_SPY.png) |

## PBO

| Item | Value |
|---|---|
| pbo | 0.503968253968254 |
| n_combinations | 252 |
| pass_gate | False |

## Errors / Data Blocks

_No run errors._

## Caveats

- Results are gross of transaction costs and taxes in this first scaffold.
- Benchmark comparison uses SPY adjusted close as the S&P 500 proxy.
- yfinance rows require `--allow-biased-yfinance` and are current-universe/survivorship-biased screens only.
- BR Postgres 1m rows use the last intraday bar as daily close; adjusted-price, split/dividend and PIT membership audits remain required.
- CAGR/MDD are warning tiers under the mandate, not standalone promotion gates.
