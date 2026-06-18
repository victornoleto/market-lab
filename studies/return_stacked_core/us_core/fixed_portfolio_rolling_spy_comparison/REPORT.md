# Fixed Portfolio Rolling SPY Comparison

Status: research-only diagnostic. No deployment, paper-trade label or mandate change.

## TL;DR

Primary lens: duration-weighted geometric mean of terminal `equity/equity_benchmark` versus SPY across all monthly rolling `3/5/10/15/20y` windows. This describes historical path dependence and investor experience, not a guaranteed forecast.

1. **16 UPRO / 29 ZROZ / 25 RSST / 30 GDE**. Weighted average: `1.75x` vs SPY; hit rate `97.37%`; time above SPY `93.17%`; p25 terminal `1.50x`; mean relative MDD `-19.97%`. Full-period 2000-2026: CAGR `12.40%`, MDD `-45.37%`, terminal `2.64x` vs SPY. Strategy: Small UPRO sleeve used to complete 100% effective equity while keeping high ZROZ and RSST/GDE diversification. Forward expectation: Best candidate if the goal is to maximize rolling dominance versus SPY while accepting LETF-level absolute drawdown. The forward expectation is positive, but it depends on the UPRO sleeve not being punished by long sideways/high-volatility regimes. Why it got this result: It worked because it combines full effective equity beta with diversifier convexity: ZROZ helps in disinflationary crashes, GDE carries equity/gold, RSST adds managed futures, and UPRO adds upside when SPY compounds without consuming much capital.

2. **25 RSST / 50 GDE / 25 ZROZ**. Weighted average: `1.70x` vs SPY; hit rate `86.93%`; time above SPY `85.74%`; p25 terminal `1.35x`; mean relative MDD `-32.18%`. Full-period 2000-2026: CAGR `12.99%`, MDD `-33.07%`, terminal `3.04x` vs SPY. Strategy: No external LETF; concentrated in GDE, with RSST and ZROZ as counterweights. Forward expectation: Good candidate for investors who prefer to avoid UPRO/SSO and accept lower rolling consistency. Future performance should depend more on gold/GDE and the real-inflation regime. Why it got this result: It did very well full-period because GDE/gold captured a historically favorable decade and reduced the need for explicit leverage, but the rolling path was less uniform than the completion-sleeve versions.

3. **24 SSO / 21 ZROZ / 25 RSST / 30 GDE**. Weighted average: `1.67x` vs SPY; hit rate `97.62%`; time above SPY `93.25%`; p25 terminal `1.47x`; mean relative MDD `-16.52%`. Full-period 2000-2026: CAGR `12.20%`, MDD `-46.31%`, terminal `2.52x` vs SPY. Strategy: SSO version that keeps RSST/GDE equal to the UPRO case and reduces ZROZ to close 100% effective equity. Forward expectation: Best SSO candidate for relative investor experience: slightly lower return than UPRO, but smoother relative drawdown. Forward expectation is more balanced if behavioral tolerance matters. Why it got this result: It got this result because SSO delivers equity beta with less path-dependence than UPRO, while preserving RSST/GDE kept crisis and trend diversification. The trade-off was cutting ZROZ from 29% to 21%.

4. **SSO proportional core**. Weighted average: `1.63x` vs SPY; hit rate `97.37%`; time above SPY `93.16%`; p25 terminal `1.42x`; mean relative MDD `-17.57%`. Full-period 2000-2026: CAGR `11.89%`, MDD `-46.42%`, terminal `2.34x` vs SPY. Strategy: Proportional SSO version: scales the original ZROZ/RSST/GDE block to make room for SSO and close 100% effective equity. Forward expectation: Robust and clean alternative if the preference is not to choose which sleeve to cut. Forward expectation is good, but slightly diluted because all diversifiers are reduced together. Why it got this result: It stayed close to the leaders because it preserved the economic architecture of the UPRO case with a less aggressive LETF. It lagged the keep-RSST/GDE SSO version because it also cut RSST/GDE, which were valuable sleeves in the sample.

5. **SSO keep 29 ZROZ**. Weighted average: `1.59x` vs SPY; hit rate `96.05%`; time above SPY `92.84%`; p25 terminal `1.37x`; mean relative MDD `-18.89%`. Full-period 2000-2026: CAGR `11.56%`, MDD `-46.60%`, terminal `2.17x` vs SPY. Strategy: SSO version that preserves ZROZ at 29% and reduces RSST/GDE to close 100% effective equity. Forward expectation: More defensive against duration shocks, but less powerful if gold and managed futures keep adding value. Useful as a sensitivity, not as the best base case. Why it got this result: The result fell because preserving ZROZ required cutting RSST and GDE, reducing two sources that historically improved the return/risk profile in this data set.

6. **37.5 RSST / 37.5 GDE / 25 ZROZ**. Weighted average: `1.59x` vs SPY; hit rate `83.60%`; time above SPY `85.37%`; p25 terminal `1.27x`; mean relative MDD `-29.93%`. Full-period 2000-2026: CAGR `12.37%`, MDD `-31.14%`, terminal `2.63x` vs SPY. Strategy: Simple no-LETF rule: balanced RSST and GDE, with ZROZ fixed at 25%. Forward expectation: Good conservative/simplex reference. Forward expectation is stable if RSST/GDE remain complementary, but without full effective equity it should lag completion rows in bull markets. Why it got this result: It was consistent over longer horizons, but ranked lower because it has less effective equity and less growth engine than UPRO/SSO, compensated by lower absolute drawdown.

7. **50 RSST / 25 GDE / 25 ZROZ**. Weighted average: `1.48x` vs SPY; hit rate `82.41%`; time above SPY `84.57%`; p25 terminal `1.19x`; mean relative MDD `-28.76%`. Full-period 2000-2026: CAGR `11.72%`, MDD `-29.23%`, terminal `2.25x` vs SPY. Strategy: RSST-heavy rule, leaning more on managed futures stacked with equity. Forward expectation: May improve in strong macro-trend regimes, but it was not the best weighted-average result. Forward expectation depends heavily on persistent quality from the RSST70/30 proxy. Why it got this result: The high RSST weight increased trend diversification, but reduced exposure to GDE/gold, which explained a large part of the best full-period and rolling results.

8. **25 RSST / 25 NTSX / 25 GDE / 25 ZROZ**. Weighted average: `1.40x` vs SPY; hit rate `80.84%`; time above SPY `83.45%`; p25 terminal `1.10x`; mean relative MDD `-29.72%`. Full-period 2000-2026: CAGR `11.21%`, MDD `-29.26%`, terminal `1.99x` vs SPY. Strategy: Equal-weight 25/25/25/25 across NTSX, RSST, GDE and ZROZ. Forward expectation: Better as an educational benchmark than as the main choice. Forward expectation is defensive, but likely diluted if the objective is to beat SPY in rolling terminal wealth. Why it got this result: It ranked last because NTSX reduced the relative potency of the mix: it added intermediate-bond exposure and lower equity exposure, while the winning rows used UPRO/SSO or high GDE to capture more upside.


## Summary

- Asset cache span after outer join: `1885-03-20`..`2026-06-17`.
- Common rolling-window span used by all portfolios: `2000-01-04`..`2026-05-29`.
- Portfolios: `8` fixed monthly-rebalanced rules.
- Rolling rows: `7632` across horizons `[3, 5, 10, 15, 20]`.
- Final horizon weights: `3y=5.66%`, `5y=9.43%`, `10y=18.87%`, `15y=28.30%`, `20y=37.74%`.
- Top weighted terminal-ratio row: `p16_upro_29_zroz_25_rsst_30_gde` at `1.75x` weighted geometric terminal ratio vs SPY, hit rate `97.37%`, time above SPY `93.17%`.

## Method

Each portfolio is rebalanced monthly inside each rolling window, starting from target weights at that window's first trading day. The benchmark is SPY buy and hold over the same dates. The primary path object is the daily relative curve `portfolio_equity / spy_equity`; terminal ratio, time above SPY, relative drawdown and longest under-SPY streak are computed from that curve. RSST70/30 uses the same tracking proxy as the current RSC studies: `SPYSIM + 70% DBMFSIM + 30% KMLMSIM - CASHX?E=-2`. Rolling windows are calendar-month starts with horizons `3/5/10/15/20y`; horizon-level summaries are combined with linear duration weights. This is robustness description, not parameter selection `[systematic_trading, p.185-188]`, `[testing_tuning, p.327-335]`.

## Figures

![Final duration-weighted ranking by geometric terminal ratio vs SPY.](plots/final_weighted_ranking.png)

Final duration-weighted ranking by geometric terminal ratio vs SPY.

![Geometric terminal ratio by rolling horizon; top three rows are emphasized.](plots/horizon_terminal_ratios.png)

Geometric terminal ratio by rolling horizon; top three rows are emphasized.

![Hit rate by rolling horizon; values are the share of windows ending above SPY.](plots/horizon_hit_rates.png)

Hit rate by rolling horizon; values are the share of windows ending above SPY.

![Reward versus relative pain; bubble size is weighted hit rate.](plots/risk_reward_scatter.png)

Reward versus relative pain; bubble size is weighted hit rate.

![Full common-period CAGR/MDD context, with color and size by terminal vs SPY.](plots/full_period_cagr_mdd.png)

Full common-period CAGR/MDD context, with color and size by terminal vs SPY.

![Every rolling backtest endpoint by start month: one line per strategy, faceted by horizon.](plots/terminal_ratio_by_start_grid.png)

Every rolling backtest endpoint by start month: one line per strategy, faceted by horizon.

![Distribution of terminal ratios for the top five weighted rows, split into a horizon grid.](plots/terminal_ratio_boxplots_top5.png)

Distribution of terminal ratios for the top five weighted rows, split into a horizon grid.

## Portfolio Definitions

| portfolio | weights | effective_equity | effective_mf | effective_gold | effective_zroz | effective_intermediate_treasury |
| --- | --- | --- | --- | --- | --- | --- |
| p25_rsst_25_ntsx_25_gde_25_zroz | 25% RSST70/30 / 25% NTSX / 25% GDE / 25% ZROZ | 70.00% | 25.00% | 22.50% | 25.00% | 15.00% |
| p50_rsst_25_gde_25_zroz | 50% RSST70/30 / 25% GDE / 25% ZROZ | 72.50% | 50.00% | 22.50% | 25.00% | 0.00% |
| p25_rsst_50_gde_25_zroz | 25% RSST70/30 / 50% GDE / 25% ZROZ | 70.00% | 25.00% | 45.00% | 25.00% | 0.00% |
| p375_rsst_375_gde_25_zroz | 37.50% RSST70/30 / 37.50% GDE / 25% ZROZ | 71.25% | 37.50% | 33.75% | 25.00% | 0.00% |
| p16_upro_29_zroz_25_rsst_30_gde | 16% UPRO-like / 29% ZROZ / 25% RSST70/30 / 30% GDE | 100.00% | 25.00% | 27.00% | 29.00% | 0.00% |
| sso_proportional_scaled_core | 27.59% SSO-like / 25% ZROZ / 21.55% RSST70/30 / 25.86% GDE | 100.00% | 21.55% | 23.28% | 25.00% | 0.00% |
| sso_keep_rsst_gde_reduce_zroz | 24% SSO-like / 21% ZROZ / 25% RSST70/30 / 30% GDE | 100.00% | 25.00% | 27.00% | 21.00% | 0.00% |
| sso_keep_zroz_scale_rsst_gde | 31.17% SSO-like / 29% ZROZ / 18.10% RSST70/30 / 21.72% GDE | 100.00% | 18.10% | 19.55% | 29.00% | 0.00% |

## Final Weighted Ranking

| rank | portfolio | weighted_geo_terminal_ratio | weighted_hit_rate | weighted_time_above_spy | weighted_p25_terminal_ratio | weighted_mean_relative_mdd_vs_spy | weighted_mean_excess_cagr |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | p16_upro_29_zroz_25_rsst_30_gde | 1.75x | 97.37% | 93.17% | 1.50x | -19.97% | 4.31% |
| 2 | p25_rsst_50_gde_25_zroz | 1.70x | 86.93% | 85.74% | 1.35x | -32.18% | 4.06% |
| 3 | sso_keep_rsst_gde_reduce_zroz | 1.67x | 97.62% | 93.25% | 1.47x | -16.52% | 3.96% |
| 4 | sso_proportional_scaled_core | 1.63x | 97.37% | 93.16% | 1.42x | -17.57% | 3.77% |
| 5 | sso_keep_zroz_scale_rsst_gde | 1.59x | 96.05% | 92.84% | 1.37x | -18.89% | 3.56% |
| 6 | p375_rsst_375_gde_25_zroz | 1.59x | 83.60% | 85.37% | 1.27x | -29.93% | 3.52% |
| 7 | p50_rsst_25_gde_25_zroz | 1.48x | 82.41% | 84.57% | 1.19x | -28.76% | 2.94% |
| 8 | p25_rsst_25_ntsx_25_gde_25_zroz | 1.40x | 80.84% | 83.45% | 1.10x | -29.72% | 2.51% |

## Horizon Window Counts

| horizon_years | n_starts |
| --- | --- |
| 3 | 282 |
| 5 | 258 |
| 10 | 198 |
| 15 | 138 |
| 20 | 78 |

## Horizon Summary

| portfolio | horizon_years | n_windows | hit_rate | geo_mean_terminal_ratio | p25_terminal_ratio | median_terminal_ratio | mean_time_above_spy_pct | mean_relative_mdd_vs_spy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| p16_upro_29_zroz_25_rsst_30_gde | 3 | 282 | 75.89% | 1.12x | 1.02x | 1.16x | 68.79% | -13.98% |
| p16_upro_29_zroz_25_rsst_30_gde | 5 | 258 | 87.60% | 1.21x | 1.07x | 1.23x | 78.50% | -16.71% |
| p16_upro_29_zroz_25_rsst_30_gde | 10 | 198 | 99.49% | 1.48x | 1.18x | 1.53x | 90.16% | -19.28% |
| p16_upro_29_zroz_25_rsst_30_gde | 15 | 138 | 100.00% | 1.80x | 1.49x | 1.91x | 97.88% | -20.51% |
| p16_upro_29_zroz_25_rsst_30_gde | 20 | 78 | 100.00% | 2.19x | 1.85x | 2.09x | 98.47% | -21.64% |
| p25_rsst_25_ntsx_25_gde_25_zroz | 3 | 282 | 61.35% | 1.07x | 0.92x | 1.07x | 57.44% | -17.56% |
| p25_rsst_25_ntsx_25_gde_25_zroz | 5 | 258 | 57.36% | 1.12x | 0.92x | 1.05x | 62.64% | -22.10% |
| p25_rsst_25_ntsx_25_gde_25_zroz | 10 | 198 | 66.16% | 1.26x | 0.87x | 1.23x | 69.02% | -27.77% |
| p25_rsst_25_ntsx_25_gde_25_zroz | 15 | 138 | 76.81% | 1.40x | 1.10x | 1.47x | 86.47% | -31.18% |
| p25_rsst_25_ntsx_25_gde_25_zroz | 20 | 78 | 100.00% | 1.61x | 1.29x | 1.45x | 97.51% | -33.34% |
| p25_rsst_50_gde_25_zroz | 3 | 282 | 64.54% | 1.12x | 0.94x | 1.14x | 61.31% | -18.01% |
| p25_rsst_50_gde_25_zroz | 5 | 258 | 68.60% | 1.21x | 0.96x | 1.08x | 65.92% | -22.20% |
| p25_rsst_50_gde_25_zroz | 10 | 198 | 71.21% | 1.43x | 0.98x | 1.27x | 72.11% | -29.22% |
| p25_rsst_50_gde_25_zroz | 15 | 138 | 90.58% | 1.68x | 1.24x | 1.74x | 89.46% | -34.95% |
| p25_rsst_50_gde_25_zroz | 20 | 78 | 100.00% | 2.17x | 1.78x | 1.94x | 98.40% | -36.20% |
| p375_rsst_375_gde_25_zroz | 3 | 282 | 64.89% | 1.11x | 0.93x | 1.11x | 60.89% | -17.59% |
| p375_rsst_375_gde_25_zroz | 5 | 258 | 68.22% | 1.18x | 0.96x | 1.08x | 65.82% | -21.67% |
| p375_rsst_375_gde_25_zroz | 10 | 198 | 66.67% | 1.37x | 0.96x | 1.26x | 71.75% | -27.74% |
| p375_rsst_375_gde_25_zroz | 15 | 138 | 81.88% | 1.58x | 1.22x | 1.63x | 88.78% | -32.19% |
| p375_rsst_375_gde_25_zroz | 20 | 78 | 100.00% | 1.96x | 1.59x | 1.78x | 98.19% | -33.24% |
| p50_rsst_25_gde_25_zroz | 3 | 282 | 64.54% | 1.09x | 0.92x | 1.08x | 60.14% | -17.91% |
| p50_rsst_25_gde_25_zroz | 5 | 258 | 66.67% | 1.15x | 0.95x | 1.07x | 65.18% | -22.00% |
| p50_rsst_25_gde_25_zroz | 10 | 198 | 66.67% | 1.30x | 0.95x | 1.23x | 70.88% | -27.28% |
| p50_rsst_25_gde_25_zroz | 15 | 138 | 78.26% | 1.48x | 1.20x | 1.53x | 87.61% | -30.36% |
| p50_rsst_25_gde_25_zroz | 20 | 78 | 100.00% | 1.75x | 1.40x | 1.62x | 97.65% | -31.62% |
| sso_keep_rsst_gde_reduce_zroz | 3 | 282 | 77.66% | 1.11x | 1.01x | 1.15x | 69.60% | -11.59% |
| sso_keep_rsst_gde_reduce_zroz | 5 | 258 | 89.15% | 1.19x | 1.07x | 1.19x | 78.85% | -13.65% |
| sso_keep_rsst_gde_reduce_zroz | 10 | 198 | 99.49% | 1.43x | 1.17x | 1.43x | 89.83% | -15.92% |
| sso_keep_rsst_gde_reduce_zroz | 15 | 138 | 100.00% | 1.71x | 1.44x | 1.77x | 98.02% | -17.30% |
| sso_keep_rsst_gde_reduce_zroz | 20 | 78 | 100.00% | 2.07x | 1.81x | 1.99x | 98.54% | -17.70% |
| sso_keep_zroz_scale_rsst_gde | 3 | 282 | 75.89% | 1.09x | 1.00x | 1.12x | 67.72% | -12.97% |
| sso_keep_zroz_scale_rsst_gde | 5 | 258 | 83.72% | 1.17x | 1.05x | 1.20x | 78.02% | -15.72% |
| sso_keep_zroz_scale_rsst_gde | 10 | 198 | 94.44% | 1.39x | 1.15x | 1.47x | 89.73% | -18.05% |
| sso_keep_zroz_scale_rsst_gde | 15 | 138 | 100.00% | 1.65x | 1.39x | 1.75x | 97.64% | -19.04% |
| sso_keep_zroz_scale_rsst_gde | 20 | 78 | 100.00% | 1.90x | 1.61x | 1.82x | 98.27% | -20.89% |
| sso_proportional_scaled_core | 3 | 282 | 75.89% | 1.10x | 1.02x | 1.13x | 68.76% | -12.19% |
| sso_proportional_scaled_core | 5 | 258 | 87.60% | 1.18x | 1.06x | 1.20x | 78.45% | -14.61% |
| sso_proportional_scaled_core | 10 | 198 | 99.49% | 1.41x | 1.16x | 1.45x | 90.07% | -16.89% |
| sso_proportional_scaled_core | 15 | 138 | 100.00% | 1.68x | 1.42x | 1.76x | 97.91% | -18.04% |
| sso_proportional_scaled_core | 20 | 78 | 100.00% | 1.98x | 1.71x | 1.90x | 98.48% | -19.10% |

## Full Common Period Context

| portfolio | portfolio_cagr | spy_cagr | terminal_ratio_vs_spy | time_above_spy_pct | portfolio_mdd | relative_mdd_vs_spy |
| --- | --- | --- | --- | --- | --- | --- |
| p25_rsst_50_gde_25_zroz | 12.99% | 8.34% | 3.04x | 99.77% | -33.07% | -36.20% |
| p16_upro_29_zroz_25_rsst_30_gde | 12.40% | 8.34% | 2.64x | 99.56% | -45.37% | -25.17% |
| p375_rsst_375_gde_25_zroz | 12.37% | 8.34% | 2.63x | 99.83% | -31.14% | -33.24% |
| sso_keep_rsst_gde_reduce_zroz | 12.20% | 8.34% | 2.52x | 99.07% | -46.31% | -19.01% |
| sso_proportional_scaled_core | 11.89% | 8.34% | 2.34x | 99.65% | -46.42% | -22.34% |
| p50_rsst_25_gde_25_zroz | 11.72% | 8.34% | 2.25x | 99.83% | -29.23% | -33.73% |
| sso_keep_zroz_scale_rsst_gde | 11.56% | 8.34% | 2.17x | 99.76% | -46.60% | -25.56% |
| p25_rsst_25_ntsx_25_gde_25_zroz | 11.21% | 8.34% | 1.99x | 99.83% | -29.26% | -37.72% |

## Interpretation

The weighted rolling-window lens favors `p16_upro_29_zroz_25_rsst_30_gde`: it has the highest duration-weighted geometric terminal ratio versus SPY (`1.75x`) and very high weighted hit rate (`97.37%`). The full common-period leader is `p25_rsst_50_gde_25_zroz` at terminal `3.04x` versus SPY, but its rolling hit rate and relative drawdown are weaker than the UPRO/SSO completion rows. The least painful relative curve among the final weighted rows is `sso_keep_rsst_gde_reduce_zroz` with weighted mean relative MDD `-16.52%`. Because these rolling windows overlap heavily, the statistics describe path dependence and investor experience; they are not independent validation trials `[testing_tuning, p.318-320]`.

## Artifacts

- Asset curves: `studies/return_stacked_core/us_core/fixed_portfolio_rolling_spy_comparison/results/asset_equity_curves.csv`.
- Portfolio definitions: `studies/return_stacked_core/us_core/fixed_portfolio_rolling_spy_comparison/results/portfolio_definitions.csv`.
- Individual windows: `studies/return_stacked_core/us_core/fixed_portfolio_rolling_spy_comparison/results/rolling_windows.csv`.
- Horizon summary: `studies/return_stacked_core/us_core/fixed_portfolio_rolling_spy_comparison/results/horizon_summary.csv`.
- Final weighted summary: `studies/return_stacked_core/us_core/fixed_portfolio_rolling_spy_comparison/results/final_weighted_summary.csv`.
- Full-period context: `studies/return_stacked_core/us_core/fixed_portfolio_rolling_spy_comparison/results/full_period_summary.csv`.
- Plots: `studies/return_stacked_core/us_core/fixed_portfolio_rolling_spy_comparison/plots`.
