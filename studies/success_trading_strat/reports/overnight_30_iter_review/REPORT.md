# Overnight 30-Iteration Review

## Verdict

The 30-iteration loop closed with `closed_no_winner`: 100 strategy configs were tested and zero strict winners were found. This report is descriptive and does not authorize live deployment. Strict gates remain informative, but the report also adds a pragmatic `candidate_watchlist` layer so good but imperfect strategies are not discarded automatically `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

## Files

- `summary_table.csv`: one row per iteration result.
- `curve_metrics.csv`: recomputed metrics for plotted candidates and aligned SPY benchmark.
- `rolling_windows.csv`: rolling 1/3/5/10/15y CAGR diagnostics versus SPY.
- `plots/equity_vs_spy.png`: selected candidate equity curves versus aligned SPY.
- `plots/equity_over_spy.png`: relative wealth versus SPY.
- `plots/drawdowns.png`: drawdown curves.
- `plots/rolling_*y_cagr.png`: rolling CAGR windows.
- `plots/gate_fail_counts.png`: parsed gate failure counts.

## Classification Rules

- `strict_winner`: original `winner=true`; none found.
- `candidate_watchlist`: Sharpe >= 0.9, MDD better than -40%, and at least three of PBO/DSR/FWD/bootstrap parsed as passing.
- `infrastructure_only`: data/scaffold/audit iterations.
- `data_blocked`: pre-registered inputs unavailable.
- `reject`: everything else.

## Watchlist

- `014-2026-05-14-crypto-vol-target-momentum` / `btc_mom63_vt20`: CAGR `25.57%` Sharpe `1.377` MDD `-22.70%`; failed `is_mcpt,wf_mcpt,pbo,walk_forward`.
- `013-2026-05-14-crypto-donchian-trend` / `eth_don20`: CAGR `66.12%` Sharpe `1.364` MDD `-35.51%`; failed `walk_forward,fwd_63d`.
- `023-2026-05-14-obv-volume-confirmation` / `qqq_obv21`: CAGR `14.09%` Sharpe `1.136` MDD `-21.25%`; failed `is_mcpt,wf_mcpt`.
- `005-2026-05-14-vol-target-static-sleeves` / `vt_35spy_15qqq_30ief_20gld`: CAGR `10.39%` Sharpe `1.005` MDD `-20.34%`; failed `is_mcpt,wf_mcpt,pbo,cross_lib`.
- `018-2026-05-14-ehlers-cycle-mode` / `qqq_ehlers_c30_t15`: CAGR `12.51%` Sharpe `1.004` MDD `-18.48%`; failed `is_mcpt,wf_mcpt`.
- `021-2026-05-14-intraday-overnight-decomposition` / `qqq_close_to_open`: CAGR `12.44%` Sharpe `0.998` MDD `-27.43%`; failed `is_mcpt,wf_mcpt,dsr`.
- `011-2026-05-14-vix-managed-exposure` / `qqq_vix15_w21`: CAGR `14.10%` Sharpe `0.945` MDD `-27.01%`; failed `fwd_stress`.

## Top Recomputed Curves

| label                   |   strategy_cagr |   strategy_sharpe |   strategy_mdd |   strategy_terminal_multiple |   spy_cagr |   spy_sharpe |   spy_mdd |   spy_terminal_multiple |
|:------------------------|----------------:|------------------:|---------------:|-----------------------------:|-----------:|-------------:|----------:|------------------------:|
| 011 qqq_vix15_w21       |          0.1410 |            0.9451 |        -0.2701 |                       8.4301 |     0.1397 |       0.8513 |   -0.3370 |                  8.4577 |
| 013 eth_don20           |          0.6612 |            1.3641 |        -0.3551 |                     179.9037 |     0.0984 |       0.7352 |   -0.3370 |                  4.6251 |
| 014 btc_mom63_vt20      |          0.2557 |            1.3766 |        -0.2270 |                       9.5633 |     0.0920 |       0.6984 |   -0.3370 |                  4.2049 |
| 018 qqq_ehlers_c30_t15  |          0.1251 |            1.0040 |        -0.1848 |                       6.7401 |     0.1444 |       0.8759 |   -0.3370 |                  9.0421 |
| 021 qqq_close_to_open   |          0.1244 |            0.9983 |        -0.2743 |                       6.7803 |     0.1422 |       0.8617 |   -0.3370 |                  8.7613 |
| 023 qqq_obv21           |          0.1409 |            1.1355 |        -0.2125 |                       8.6028 |     0.1422 |       0.8617 |   -0.3370 |                  8.7613 |
| 028 qld_qqq_sma200_rv70 |          0.2264 |            0.9774 |        -0.3454 |                      27.3474 |     0.1455 |       0.8814 |   -0.3370 |                  9.1903 |

## Rolling Window Summary

| label                   |   window_years |   strategy_median_cagr |   strategy_min_cagr |   spy_median_cagr |   spy_min_cagr |   share_beating_spy |
|:------------------------|---------------:|-----------------------:|--------------------:|------------------:|---------------:|--------------------:|
| 011 qqq_vix15_w21       |              1 |                 0.1606 |             -0.2622 |            0.1581 |        -0.1973 |              0.4952 |
| 011 qqq_vix15_w21       |              3 |                 0.1421 |              0.0121 |            0.1334 |         0.0038 |              0.5834 |
| 011 qqq_vix15_w21       |              5 |                 0.1405 |              0.0641 |            0.1393 |         0.0322 |              0.5229 |
| 011 qqq_vix15_w21       |             10 |                 0.1421 |              0.1195 |            0.1333 |         0.0888 |              0.9105 |
| 011 qqq_vix15_w21       |             15 |                 0.1408 |              0.1261 |            0.1407 |         0.1213 |              0.6553 |
| 013 eth_don20           |              1 |                 0.4111 |             -0.3489 |            0.1667 |        -0.2064 |              0.7301 |
| 013 eth_don20           |              3 |                 0.5136 |             -0.0920 |            0.1383 |         0.0030 |              0.6692 |
| 013 eth_don20           |              5 |                 0.2940 |              0.0507 |            0.1478 |         0.0903 |              0.9651 |
| 013 eth_don20           |             10 |                 0.5580 |              0.5438 |            0.1512 |         0.1404 |              1.0000 |
| 014 btc_mom63_vt20      |              1 |                 0.2079 |             -0.2255 |            0.1651 |        -0.2064 |              0.6388 |
| 014 btc_mom63_vt20      |              3 |                 0.2035 |              0.0700 |            0.1368 |         0.0030 |              0.8177 |
| 014 btc_mom63_vt20      |              5 |                 0.1875 |              0.0934 |            0.1466 |         0.0903 |              0.8863 |
| 018 qqq_ehlers_c30_t15  |              1 |                 0.1139 |             -0.1547 |            0.1584 |        -0.1973 |              0.3171 |
| 018 qqq_ehlers_c30_t15  |              3 |                 0.1036 |              0.0282 |            0.1336 |         0.0038 |              0.2295 |
| 018 qqq_ehlers_c30_t15  |              5 |                 0.1161 |              0.0432 |            0.1390 |         0.0322 |              0.4101 |
| 018 qqq_ehlers_c30_t15  |             10 |                 0.1208 |              0.0968 |            0.1334 |         0.0888 |              0.0269 |
| 018 qqq_ehlers_c30_t15  |             15 |                 0.1186 |              0.1076 |            0.1402 |         0.1213 |              0.0000 |
| 021 qqq_close_to_open   |              1 |                 0.1410 |             -0.2244 |            0.1586 |        -0.1973 |              0.4082 |
| 021 qqq_close_to_open   |              3 |                 0.1182 |             -0.0140 |            0.1336 |         0.0038 |              0.2760 |
| 021 qqq_close_to_open   |              5 |                 0.1166 |              0.0512 |            0.1393 |         0.0322 |              0.2743 |
| 021 qqq_close_to_open   |             10 |                 0.1162 |              0.0947 |            0.1337 |         0.0888 |              0.0426 |
| 021 qqq_close_to_open   |             15 |                 0.1215 |              0.1098 |            0.1402 |         0.1213 |              0.0000 |
| 023 qqq_obv21           |              1 |                 0.1200 |             -0.2125 |            0.1586 |        -0.1973 |              0.3554 |
| 023 qqq_obv21           |              3 |                 0.1359 |              0.0233 |            0.1336 |         0.0038 |              0.3933 |
| 023 qqq_obv21           |              5 |                 0.1291 |              0.0245 |            0.1393 |         0.0322 |              0.4028 |
| 023 qqq_obv21           |             10 |                 0.1276 |              0.0821 |            0.1337 |         0.0888 |              0.4527 |
| 023 qqq_obv21           |             15 |                 0.1312 |              0.1158 |            0.1402 |         0.1213 |              0.0090 |
| 028 qld_qqq_sma200_rv70 |              1 |                 0.2354 |             -0.3222 |            0.1584 |        -0.1973 |              0.6480 |
| 028 qld_qqq_sma200_rv70 |              3 |                 0.2848 |             -0.0204 |            0.1336 |         0.0038 |              0.7953 |
| 028 qld_qqq_sma200_rv70 |              5 |                 0.2473 |              0.0701 |            0.1391 |         0.0322 |              0.8571 |
| 028 qld_qqq_sma200_rv70 |             10 |                 0.2824 |              0.1599 |            0.1334 |         0.0888 |              1.0000 |
| 028 qld_qqq_sma200_rv70 |             15 |                 0.2414 |              0.2274 |            0.1402 |         0.1213 |              1.0000 |

## Interpretation

The strongest strict-gate near miss remains `011 qqq_vix15_w21`: it passed IS MCPT, WF MCPT, PBO, DSR, WF, OOS, bootstrap and cross-lib, but failed the latest 63-day forward stress. `013 eth_don20` and `023 qqq_obv21` are economically interesting, but each failed at least one non-negotiable validation gate. Future work should separate strict research proof from pragmatic paper-trading triage, then evaluate candidates forward without retrofitting thresholds.
