# ETF Staggered Momentum 13612 Report

Status: research-only. No deployment, paper-trade label or mandate change.

## Verdict

Screen-only FAIL: yfinance/current ETF universe is non-promotable, and overall PBO is 0.663.

## Grid

- Universe: `us_etfs` current curated ETF list
- Top-N: `3,5,10`
- Rebalance frequencies: `3,6,12` months
- Offset policy: all offsets are equal-capital sleeves; no best-offset selection
- Mechanisms: `raw_equal, raw_inverse_vol`
- Rows: `18`
- Ranking metric: after-tax strategy returns under Brazil's annual 15% realized-gain rule
- Benchmark: SPY adjusted close as S&P 500 proxy

## Key Findings

- Melhor Sharpe after-tax: `mom13612_us_etfs_raw_inverse_vol_top10_reb3_staggered`, CAGR `10.15%`, MDD `-30.24%`, Sharpe `0.683`, turnover `2.192x/ano`.
- Nenhuma configuração manteve MDD acima de `-30%`.
- Frequência com maior Sharpe mediano: `6m`; menor turnover mediano: `12m`.
- PBO do painel staggered ETF: `0.663` sobre retornos after-tax. Ainda é yfinance/current-universe screen-only `[advances_fin_ml, p.208-211]`.

## Aggregate Plots

- [staggered_cagr_vs_mdd.png](plots/etf_staggered/staggered_cagr_vs_mdd.png)
- [staggered_sharpe_rank.png](plots/etf_staggered/staggered_sharpe_rank.png)
- [staggered_turnover_tax_drag.png](plots/etf_staggered/staggered_turnover_tax_drag.png)

## Top By After-Tax Sharpe

| Name | Mechanism | Top-N | Reb | Sleeves | CAGR | Gross CAGR | Tax Drag | SPY CAGR | Excess | MDD | Vol | Sharpe | Calmar | Turnover/yr | Above SPY |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom13612_us_etfs_raw_inverse_vol_top10_reb3_staggered | raw_inverse_vol | 10 | 3 | 3 | 10.15% | 11.44% | 1.29% | 9.75% | 0.39% | -30.24% | 16.04% | 0.683 | 0.336 | 2.192 | 95.33% |
| mom13612_us_etfs_raw_equal_top10_reb3_staggered | raw_13612 | 10 | 3 | 3 | 10.68% | 11.99% | 1.31% | 9.75% | 0.93% | -33.21% | 17.65% | 0.664 | 0.322 | 1.883 | 100.00% |
| mom13612_us_etfs_raw_inverse_vol_top10_reb6_staggered | raw_inverse_vol | 10 | 6 | 6 | 9.85% | 11.05% | 1.19% | 9.47% | 0.38% | -33.18% | 16.25% | 0.660 | 0.297 | 1.302 | 95.82% |
| mom13612_us_etfs_raw_inverse_vol_top10_reb12_staggered | raw_inverse_vol | 10 | 12 | 12 | 9.69% | 10.82% | 1.13% | 10.01% | -0.32% | -38.15% | 16.17% | 0.653 | 0.254 | 0.799 | 83.89% |
| mom13612_us_etfs_raw_equal_top10_reb6_staggered | raw_13612 | 10 | 6 | 6 | 10.34% | 11.56% | 1.22% | 9.47% | 0.87% | -40.60% | 17.94% | 0.639 | 0.255 | 1.162 | 100.00% |
| mom13612_us_etfs_raw_equal_top10_reb12_staggered | raw_13612 | 10 | 12 | 12 | 10.16% | 11.32% | 1.16% | 10.01% | 0.15% | -46.03% | 18.09% | 0.626 | 0.221 | 0.743 | 93.71% |
| mom13612_us_etfs_raw_inverse_vol_top5_reb6_staggered | raw_inverse_vol | 5 | 6 | 6 | 10.83% | 12.13% | 1.29% | 9.47% | 1.36% | -45.70% | 19.50% | 0.625 | 0.237 | 1.443 | 100.00% |
| mom13612_us_etfs_raw_inverse_vol_top5_reb12_staggered | raw_inverse_vol | 5 | 12 | 12 | 10.54% | 11.73% | 1.19% | 10.01% | 0.53% | -50.24% | 19.08% | 0.621 | 0.210 | 0.849 | 100.00% |
| mom13612_us_etfs_raw_inverse_vol_top5_reb3_staggered | raw_inverse_vol | 5 | 3 | 3 | 10.59% | 11.95% | 1.36% | 9.75% | 0.84% | -38.13% | 19.54% | 0.613 | 0.278 | 2.468 | 99.89% |
| mom13612_us_etfs_raw_equal_top5_reb6_staggered | raw_13612 | 5 | 6 | 6 | 11.14% | 12.44% | 1.30% | 9.47% | 1.67% | -49.53% | 20.78% | 0.613 | 0.225 | 1.337 | 100.00% |
| mom13612_us_etfs_raw_equal_top5_reb12_staggered | raw_13612 | 5 | 12 | 12 | 10.93% | 12.15% | 1.21% | 10.01% | 0.92% | -53.27% | 20.46% | 0.610 | 0.205 | 0.808 | 100.00% |
| mom13612_us_etfs_raw_equal_top5_reb3_staggered | raw_13612 | 5 | 3 | 3 | 10.81% | 12.16% | 1.35% | 9.75% | 1.05% | -42.39% | 20.76% | 0.599 | 0.255 | 2.229 | 100.00% |
| mom13612_us_etfs_raw_inverse_vol_top3_reb12_staggered | raw_inverse_vol | 3 | 12 | 12 | 10.91% | 12.13% | 1.22% | 10.01% | 0.90% | -54.84% | 21.01% | 0.598 | 0.199 | 0.857 | 100.00% |
| mom13612_us_etfs_raw_inverse_vol_top3_reb3_staggered | raw_inverse_vol | 3 | 3 | 3 | 11.26% | 12.74% | 1.48% | 9.75% | 1.51% | -44.21% | 22.09% | 0.594 | 0.255 | 2.546 | 99.97% |
| mom13612_us_etfs_raw_equal_top3_reb12_staggered | raw_13612 | 3 | 12 | 12 | 11.20% | 12.44% | 1.25% | 10.01% | 1.19% | -57.22% | 22.22% | 0.589 | 0.196 | 0.827 | 100.00% |
| mom13612_us_etfs_raw_equal_top3_reb3_staggered | raw_13612 | 3 | 3 | 3 | 11.32% | 12.79% | 1.47% | 9.75% | 1.57% | -45.59% | 23.23% | 0.579 | 0.248 | 2.339 | 95.55% |
| mom13612_us_etfs_raw_inverse_vol_top3_reb6_staggered | raw_inverse_vol | 3 | 6 | 6 | 10.70% | 12.03% | 1.32% | 9.47% | 1.23% | -54.16% | 21.65% | 0.578 | 0.198 | 1.541 | 100.00% |
| mom13612_us_etfs_raw_equal_top3_reb6_staggered | raw_13612 | 3 | 6 | 6 | 10.91% | 12.24% | 1.33% | 9.47% | 1.44% | -55.99% | 22.81% | 0.569 | 0.195 | 1.454 | 100.00% |

## Top By After-Tax Excess CAGR

| Name | Mechanism | Top-N | Reb | Sleeves | CAGR | Gross CAGR | Tax Drag | SPY CAGR | Excess | MDD | Vol | Sharpe | Calmar | Turnover/yr | Above SPY |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom13612_us_etfs_raw_equal_top5_reb6_staggered | raw_13612 | 5 | 6 | 6 | 11.14% | 12.44% | 1.30% | 9.47% | 1.67% | -49.53% | 20.78% | 0.613 | 0.225 | 1.337 | 100.00% |
| mom13612_us_etfs_raw_equal_top3_reb3_staggered | raw_13612 | 3 | 3 | 3 | 11.32% | 12.79% | 1.47% | 9.75% | 1.57% | -45.59% | 23.23% | 0.579 | 0.248 | 2.339 | 95.55% |
| mom13612_us_etfs_raw_inverse_vol_top3_reb3_staggered | raw_inverse_vol | 3 | 3 | 3 | 11.26% | 12.74% | 1.48% | 9.75% | 1.51% | -44.21% | 22.09% | 0.594 | 0.255 | 2.546 | 99.97% |
| mom13612_us_etfs_raw_equal_top3_reb6_staggered | raw_13612 | 3 | 6 | 6 | 10.91% | 12.24% | 1.33% | 9.47% | 1.44% | -55.99% | 22.81% | 0.569 | 0.195 | 1.454 | 100.00% |
| mom13612_us_etfs_raw_inverse_vol_top5_reb6_staggered | raw_inverse_vol | 5 | 6 | 6 | 10.83% | 12.13% | 1.29% | 9.47% | 1.36% | -45.70% | 19.50% | 0.625 | 0.237 | 1.443 | 100.00% |
| mom13612_us_etfs_raw_inverse_vol_top3_reb6_staggered | raw_inverse_vol | 3 | 6 | 6 | 10.70% | 12.03% | 1.32% | 9.47% | 1.23% | -54.16% | 21.65% | 0.578 | 0.198 | 1.541 | 100.00% |
| mom13612_us_etfs_raw_equal_top3_reb12_staggered | raw_13612 | 3 | 12 | 12 | 11.20% | 12.44% | 1.25% | 10.01% | 1.19% | -57.22% | 22.22% | 0.589 | 0.196 | 0.827 | 100.00% |
| mom13612_us_etfs_raw_equal_top5_reb3_staggered | raw_13612 | 5 | 3 | 3 | 10.81% | 12.16% | 1.35% | 9.75% | 1.05% | -42.39% | 20.76% | 0.599 | 0.255 | 2.229 | 100.00% |
| mom13612_us_etfs_raw_equal_top10_reb3_staggered | raw_13612 | 10 | 3 | 3 | 10.68% | 11.99% | 1.31% | 9.75% | 0.93% | -33.21% | 17.65% | 0.664 | 0.322 | 1.883 | 100.00% |
| mom13612_us_etfs_raw_equal_top5_reb12_staggered | raw_13612 | 5 | 12 | 12 | 10.93% | 12.15% | 1.21% | 10.01% | 0.92% | -53.27% | 20.46% | 0.610 | 0.205 | 0.808 | 100.00% |
| mom13612_us_etfs_raw_inverse_vol_top3_reb12_staggered | raw_inverse_vol | 3 | 12 | 12 | 10.91% | 12.13% | 1.22% | 10.01% | 0.90% | -54.84% | 21.01% | 0.598 | 0.199 | 0.857 | 100.00% |
| mom13612_us_etfs_raw_equal_top10_reb6_staggered | raw_13612 | 10 | 6 | 6 | 10.34% | 11.56% | 1.22% | 9.47% | 0.87% | -40.60% | 17.94% | 0.639 | 0.255 | 1.162 | 100.00% |
| mom13612_us_etfs_raw_inverse_vol_top5_reb3_staggered | raw_inverse_vol | 5 | 3 | 3 | 10.59% | 11.95% | 1.36% | 9.75% | 0.84% | -38.13% | 19.54% | 0.613 | 0.278 | 2.468 | 99.89% |
| mom13612_us_etfs_raw_inverse_vol_top5_reb12_staggered | raw_inverse_vol | 5 | 12 | 12 | 10.54% | 11.73% | 1.19% | 10.01% | 0.53% | -50.24% | 19.08% | 0.621 | 0.210 | 0.849 | 100.00% |
| mom13612_us_etfs_raw_inverse_vol_top10_reb3_staggered | raw_inverse_vol | 10 | 3 | 3 | 10.15% | 11.44% | 1.29% | 9.75% | 0.39% | -30.24% | 16.04% | 0.683 | 0.336 | 2.192 | 95.33% |
| mom13612_us_etfs_raw_inverse_vol_top10_reb6_staggered | raw_inverse_vol | 10 | 6 | 6 | 9.85% | 11.05% | 1.19% | 9.47% | 0.38% | -33.18% | 16.25% | 0.660 | 0.297 | 1.302 | 95.82% |
| mom13612_us_etfs_raw_equal_top10_reb12_staggered | raw_13612 | 10 | 12 | 12 | 10.16% | 11.32% | 1.16% | 10.01% | 0.15% | -46.03% | 18.09% | 0.626 | 0.221 | 0.743 | 93.71% |
| mom13612_us_etfs_raw_inverse_vol_top10_reb12_staggered | raw_inverse_vol | 10 | 12 | 12 | 9.69% | 10.82% | 1.13% | 10.01% | -0.32% | -38.15% | 16.17% | 0.653 | 0.254 | 0.799 | 83.89% |

## Finalists With Individual Plots

| Name | Mechanism | Top-N | Reb | Sleeves | CAGR | Excess | MDD | Sharpe | Calmar | Turnover/yr | Above SPY | Plot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom13612_us_etfs_raw_inverse_vol_top10_reb3_staggered | raw_inverse_vol | 10 | 3 | 3 | 10.15% | 0.39% | -30.24% | 0.683 | 0.336 | 2.192 | 95.33% | [mom13612_us_etfs_raw_inverse_vol_top10_reb3_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_inverse_vol_top10_reb3_staggered_vs_SPY.png) |
| mom13612_us_etfs_raw_equal_top10_reb3_staggered | raw_13612 | 10 | 3 | 3 | 10.68% | 0.93% | -33.21% | 0.664 | 0.322 | 1.883 | 100.00% | [mom13612_us_etfs_raw_equal_top10_reb3_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_equal_top10_reb3_staggered_vs_SPY.png) |
| mom13612_us_etfs_raw_inverse_vol_top10_reb6_staggered | raw_inverse_vol | 10 | 6 | 6 | 9.85% | 0.38% | -33.18% | 0.660 | 0.297 | 1.302 | 95.82% | [mom13612_us_etfs_raw_inverse_vol_top10_reb6_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_inverse_vol_top10_reb6_staggered_vs_SPY.png) |
| mom13612_us_etfs_raw_inverse_vol_top10_reb12_staggered | raw_inverse_vol | 10 | 12 | 12 | 9.69% | -0.32% | -38.15% | 0.653 | 0.254 | 0.799 | 83.89% | [mom13612_us_etfs_raw_inverse_vol_top10_reb12_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_inverse_vol_top10_reb12_staggered_vs_SPY.png) |
| mom13612_us_etfs_raw_equal_top10_reb6_staggered | raw_13612 | 10 | 6 | 6 | 10.34% | 0.87% | -40.60% | 0.639 | 0.255 | 1.162 | 100.00% | [mom13612_us_etfs_raw_equal_top10_reb6_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_equal_top10_reb6_staggered_vs_SPY.png) |
| mom13612_us_etfs_raw_equal_top10_reb12_staggered | raw_13612 | 10 | 12 | 12 | 10.16% | 0.15% | -46.03% | 0.626 | 0.221 | 0.743 | 93.71% | [mom13612_us_etfs_raw_equal_top10_reb12_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_equal_top10_reb12_staggered_vs_SPY.png) |
| mom13612_us_etfs_raw_inverse_vol_top5_reb6_staggered | raw_inverse_vol | 5 | 6 | 6 | 10.83% | 1.36% | -45.70% | 0.625 | 0.237 | 1.443 | 100.00% | [mom13612_us_etfs_raw_inverse_vol_top5_reb6_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_inverse_vol_top5_reb6_staggered_vs_SPY.png) |
| mom13612_us_etfs_raw_inverse_vol_top5_reb3_staggered | raw_inverse_vol | 5 | 3 | 3 | 10.59% | 0.84% | -38.13% | 0.613 | 0.278 | 2.468 | 99.89% | [mom13612_us_etfs_raw_inverse_vol_top5_reb3_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_inverse_vol_top5_reb3_staggered_vs_SPY.png) |
| mom13612_us_etfs_raw_equal_top5_reb6_staggered | raw_13612 | 5 | 6 | 6 | 11.14% | 1.67% | -49.53% | 0.613 | 0.225 | 1.337 | 100.00% | [mom13612_us_etfs_raw_equal_top5_reb6_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_equal_top5_reb6_staggered_vs_SPY.png) |
| mom13612_us_etfs_raw_equal_top5_reb3_staggered | raw_13612 | 5 | 3 | 3 | 10.81% | 1.05% | -42.39% | 0.599 | 0.255 | 2.229 | 100.00% | [mom13612_us_etfs_raw_equal_top5_reb3_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_equal_top5_reb3_staggered_vs_SPY.png) |
| mom13612_us_etfs_raw_inverse_vol_top3_reb12_staggered | raw_inverse_vol | 3 | 12 | 12 | 10.91% | 0.90% | -54.84% | 0.598 | 0.199 | 0.857 | 100.00% | [mom13612_us_etfs_raw_inverse_vol_top3_reb12_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_inverse_vol_top3_reb12_staggered_vs_SPY.png) |
| mom13612_us_etfs_raw_inverse_vol_top3_reb3_staggered | raw_inverse_vol | 3 | 3 | 3 | 11.26% | 1.51% | -44.21% | 0.594 | 0.255 | 2.546 | 99.97% | [mom13612_us_etfs_raw_inverse_vol_top3_reb3_staggered_vs_SPY.png](plots/etf_staggered/finalists/mom13612_us_etfs_raw_inverse_vol_top3_reb3_staggered_vs_SPY.png) |

## PBO Summary

| group | pbo | n_configs | n_obs | n_combinations | pass |
|---|---|---|---|---|---|
| all | 0.6626984126984127 | 18 | 6153 | 252 | False |
| mechanism:raw_13612 | 0.7023809523809523 | 9 | 6153 | 252 | False |
| mechanism:raw_inverse_vol | 0.8055555555555556 | 9 | 6153 | 252 | False |

## Caveats

- All rows are yfinance/current-universe screens and `promotion_eligible=false` until PIT/delisted validation exists `[advances_fin_ml, p.208-211]`.
- The staggered construction reduces timing-luck selection but does not remove data-mining risk or survivorship bias `[advances_fin_ml, p.273-275]`.
- Main rankings are after-tax for realized capital gains, but still gross of transaction costs/slippage.
- Tax model nets realized gains/losses annually at 15% and does not force a final liquidation of unrealized positions.
