# Pareto/Regime Report - Static SPY Beater Portfolio

Generated from fixed candidate allocations over the common local data window `2000-01-04..2026-04-17`. This report is discovery-only: it compares path robustness and regimes before further local search, and does not validate or authorize any deployment `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Candidate Notes

| candidate               | kind                                | weights                                                                                              | note                                                                                               |
|:------------------------|:------------------------------------|:-----------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------|
| GA_aggressive           | long_only_static                    | {"GDESIM": 0.35, "RSSTSIM": 0.5, "TQQQSIM": 0.05, "ZROZSIM": 0.1}                                    | Consistency-guard GA lead; includes a small 3x Nasdaq sleeve.                                      |
| GA_robust               | long_only_static                    | {"GDESIM": 0.35, "RSSTSIM": 0.5, "SPYSIM": 0.1, "ZROZSIM": 0.05}                                     | Strict p10-MDD GA-family incumbent.                                                                |
| Refined_GA_robust       | long_only_static_artifact_confirmed | {"GDESIM": 0.35, "RSSTSIM": 0.5, "SPYSIM": 0.1, "ZROZSIM": 0.05}                                     | Same weights as GA_robust; confirmed against results/refine_robust artifact.                       |
| B4_like_testfolio       | stacked_leveraged_reference         | {"CASHX": -0.375, "GDESIM": 0.25, "IEFSIM": 0.15, "KMLMSIM": 0.25, "SPYSIM": 0.475, "ZROZSIM": 0.25} | Reference stacked portfolio with negative CASHX; not a pure long-only allocation.                  |
| B4_no_margin_lead       | long_only_static_no_external_margin | {"GDESIM": 0.35, "RSSTSIM": 0.4, "ZROZSIM": 0.25}                                                    | Best high-CAGR feasible row from local B4 no-margin Pareto search.                                 |
| SPYSIM_buy_hold         | benchmark_buy_hold                  | {"SPYSIM": 1.0}                                                                                      | Primary buy-and-hold benchmark.                                                                    |
| B4_original             | long_only_static                    | {"GDESIM": 0.25, "NTSXSIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25}                                  | Original B4 reference when all synthetic legs are available.                                       |
| GA_stacked_seed20260519 | long_only_static_stacked_proxy      | {"CTAPSIM": 0.05, "ESBGSIM": 0.2, "GDESIM": 0.25, "MATESIM": 0.05, "RSSTSIM": 0.3, "ZROZSIM": 0.15}  | Triage GA winner seed 20260519 from stacked-ETF expansion (local proxies; CAGR overstated ~3-6pp). |
| GA_stacked_seed20260520 | long_only_static_stacked_proxy      | {"CTAPSIM": 0.05, "ESBGSIM": 0.25, "GDESIM": 0.2, "MATESIM": 0.1, "RSSTSIM": 0.25, "ZROZSIM": 0.15}  | Triage GA winner seed 20260520 from stacked-ETF expansion (local proxies; CAGR overstated ~3-6pp). |
| GA_stacked_seed20260521 | long_only_static_stacked_proxy      | {"CTAPSIM": 0.05, "ESBGSIM": 0.25, "GDESIM": 0.2, "MATESIM": 0.05, "RSSTSIM": 0.3, "ZROZSIM": 0.15}  | Triage GA winner seed 20260521 from stacked-ETF expansion (local proxies; CAGR overstated ~3-6pp). |

`B4_like_testfolio` is explicitly a stacked/leveraged reference: it has `-37.5% CASHX`, gross weight `1.75`, and is not a pure long-only portfolio. The other portfolio weights are long-only sleeves, though several sleeves embed leverage/stacking internally `[risk_parity, p.80-81]`, `[leverage_for_the_long_run, p.13]`.

## Full-Period Metrics

| candidate               | kind                                |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   full_ulcer |   full_terminal_wealth |   gross_weight |
|:------------------------|:------------------------------------|------------:|-----------:|--------------:|---------------:|--------------:|-------------:|-----------------------:|---------------:|
| GA_stacked_seed20260521 | long_only_static_stacked_proxy      |    0.139074 |  -0.309737 |      0.904898 |       1.248238 |      0.449007 |     0.076769 |              30.450248 |       1.000000 |
| B4_no_margin_lead       | long_only_static_no_external_margin |    0.133862 |  -0.299406 |      0.903544 |       1.266272 |      0.447093 |     0.075881 |              26.998606 |       1.000000 |
| GA_stacked_seed20260520 | long_only_static_stacked_proxy      |    0.138333 |  -0.309856 |      0.900770 |       1.242553 |      0.446444 |     0.077195 |              29.934872 |       1.000000 |
| GA_stacked_seed20260519 | long_only_static_stacked_proxy      |    0.139715 |  -0.317004 |      0.897664 |       1.236026 |      0.440735 |     0.078815 |              30.902811 |       1.000000 |
| B4_original             | long_only_static                    |    0.121202 |  -0.279216 |      0.882281 |       1.238852 |      0.434078 |     0.074329 |              20.109833 |       1.000000 |
| B4_like_testfolio       | stacked_leveraged_reference         |    0.117200 |  -0.284228 |      0.863160 |       1.214189 |      0.412345 |     0.076128 |              18.309305 |       1.750000 |
| GA_robust               | long_only_static                    |    0.139054 |  -0.412016 |      0.800282 |       1.087114 |      0.337497 |     0.102626 |              30.436318 |       1.000000 |
| Refined_GA_robust       | long_only_static_artifact_confirmed |    0.139054 |  -0.412016 |      0.800282 |       1.087114 |      0.337497 |     0.102626 |              30.436318 |       1.000000 |
| GA_aggressive           | long_only_static                    |    0.143090 |  -0.493728 |      0.783811 |       1.074751 |      0.289815 |     0.127360 |              33.395261 |       1.000000 |
| SPYSIM_buy_hold         | benchmark_buy_hold                  |    0.082356 |  -0.551413 |      0.505935 |       0.643555 |      0.149355 |     0.161017 |               7.973955 |       1.000000 |

## Plots

Performance and rolling-window plots are saved as PNG artifacts. Equity and relative-equity plots use normalized wealth; the SPY-relative plot is `portfolio_equity / SPYSIM_equity` so values above `1.0` mean cumulative outperformance versus `SPYSIM`.

![Equity Curves](plots/equity_curves.png)

![Equity Vs Spy Ratio](plots/equity_vs_spy_ratio.png)

![Drawdowns](plots/drawdowns.png)

![Rolling Windows Relative Wealth Vs Spy](plots/rolling_windows_relative_wealth_vs_spy.png)

## Rolling Diagnostics

Rolling 3y/5y/10y CAGR, MDD, and relative wealth versus `SPYSIM`; p10 is retained to expose bad-window fragility rather than average-only performance `[testing_tuning, p.327-335]`.

| candidate               | horizon   | metric                 |    latest |    median |        min |       p10 |      worst |
|:------------------------|:----------|:-----------------------|----------:|----------:|-----------:|----------:|-----------:|
| B4_like_testfolio       | 10y       | cagr                   |  0.124206 |  0.126986 |   0.076771 |  0.103537 | nan        |
| B4_like_testfolio       | 10y       | mdd                    | -0.249060 | -0.261694 | nan        | -0.261694 |  -0.284228 |
| B4_like_testfolio       | 10y       | relative_wealth_vs_spy | -0.219101 |  0.304707 |  -0.273254 | -0.170473 | nan        |
| B4_like_testfolio       | 15y       | cagr                   |  0.132007 |  0.129097 |   0.102037 |  0.113906 | nan        |
| B4_like_testfolio       | 15y       | mdd                    | -0.249060 | -0.261694 | nan        | -0.264133 |  -0.284228 |
| B4_like_testfolio       | 15y       | relative_wealth_vs_spy | -0.090360 |  0.594820 |  -0.253935 | -0.120443 | nan        |
| B4_like_testfolio       | 3y        | cagr                   |  0.177058 |  0.119019 |  -0.036582 |  0.040236 | nan        |
| B4_like_testfolio       | 3y        | mdd                    | -0.141655 | -0.141724 | nan        | -0.261694 |  -0.284228 |
| B4_like_testfolio       | 3y        | relative_wealth_vs_spy | -0.100873 |  0.072020 |  -0.231802 | -0.158053 | nan        |
| B4_like_testfolio       | 5y        | cagr                   |  0.109050 |  0.120174 |   0.039648 |  0.088179 | nan        |
| B4_like_testfolio       | 5y        | mdd                    | -0.249060 | -0.203890 | nan        | -0.261694 |  -0.284228 |
| B4_like_testfolio       | 5y        | relative_wealth_vs_spy | -0.096136 |  0.064570 |  -0.318132 | -0.150084 | nan        |
| B4_no_margin_lead       | 10y       | cagr                   |  0.145256 |  0.138260 |   0.095895 |  0.117113 | nan        |
| B4_no_margin_lead       | 10y       | mdd                    | -0.214588 | -0.280222 | nan        | -0.280222 |  -0.299406 |
| B4_no_margin_lead       | 10y       | relative_wealth_vs_spy | -0.059925 |  0.320615 |  -0.231535 | -0.087601 | nan        |
| B4_no_margin_lead       | 15y       | cagr                   |  0.144496 |  0.139976 |   0.114443 |  0.124153 | nan        |
| B4_no_margin_lead       | 15y       | mdd                    | -0.214588 | -0.280222 | nan        | -0.298740 |  -0.299406 |
| B4_no_margin_lead       | 15y       | relative_wealth_vs_spy |  0.072387 |  0.826968 |  -0.185919 |  0.007045 | nan        |
| B4_no_margin_lead       | 3y        | cagr                   |  0.219239 |  0.125264 |  -0.028099 |  0.064329 | nan        |
| B4_no_margin_lead       | 3y        | mdd                    | -0.144136 | -0.151424 | nan        | -0.280222 |  -0.299406 |
| B4_no_margin_lead       | 3y        | relative_wealth_vs_spy | -0.000705 |  0.127067 |  -0.270743 | -0.119378 | nan        |
| B4_no_margin_lead       | 5y        | cagr                   |  0.150780 |  0.138606 |   0.056200 |  0.099952 | nan        |
| B4_no_margin_lead       | 5y        | mdd                    | -0.214588 | -0.199989 | nan        | -0.280222 |  -0.299406 |
| B4_no_margin_lead       | 5y        | relative_wealth_vs_spy |  0.087196 |  0.109771 |  -0.225821 | -0.130804 | nan        |
| B4_original             | 10y       | cagr                   |  0.128888 |  0.129771 |   0.082303 |  0.106984 | nan        |
| B4_original             | 10y       | mdd                    | -0.247509 | -0.272761 | nan        | -0.272761 |  -0.279216 |
| B4_original             | 10y       | relative_wealth_vs_spy | -0.185962 |  0.310253 |  -0.250068 | -0.154571 | nan        |
| B4_original             | 15y       | cagr                   |  0.134817 |  0.131542 |   0.105254 |  0.116039 | nan        |
| B4_original             | 15y       | mdd                    | -0.247509 | -0.272761 | nan        | -0.272761 |  -0.279216 |
| B4_original             | 15y       | relative_wealth_vs_spy | -0.055885 |  0.645460 |  -0.237917 | -0.096716 | nan        |
| B4_original             | 3y        | cagr                   |  0.187521 |  0.121016 |  -0.031525 |  0.046198 | nan        |
| B4_original             | 3y        | mdd                    | -0.138700 | -0.142339 | nan        | -0.272761 |  -0.279216 |
| B4_original             | 3y        | relative_wealth_vs_spy | -0.076683 |  0.084437 |  -0.233482 | -0.146977 | nan        |
| B4_original             | 5y        | cagr                   |  0.116310 |  0.123265 |   0.047002 |  0.093289 | nan        |
| B4_original             | 5y        | mdd                    | -0.247509 | -0.201391 | nan        | -0.272761 |  -0.279216 |
| B4_original             | 5y        | relative_wealth_vs_spy | -0.066163 |  0.067664 |  -0.295811 | -0.143085 | nan        |
| GA_aggressive           | 10y       | cagr                   |  0.192721 |  0.159001 |   0.065597 |  0.129339 | nan        |
| GA_aggressive           | 10y       | mdd                    | -0.263493 | -0.385565 | nan        | -0.385565 |  -0.493728 |
| GA_aggressive           | 10y       | relative_wealth_vs_spy |  0.410986 |  0.537078 |   0.047126 |  0.227968 | nan        |
| GA_aggressive           | 15y       | cagr                   |  0.178646 |  0.156349 |   0.102438 |  0.122718 | nan        |
| GA_aggressive           | 15y       | mdd                    | -0.263493 | -0.385565 | nan        | -0.438998 |  -0.493728 |
| GA_aggressive           | 15y       | relative_wealth_vs_spy |  0.666819 |  1.217587 |   0.376769 |  0.595619 | nan        |
| GA_aggressive           | 3y        | cagr                   |  0.294920 |  0.154021 |  -0.129974 |  0.053272 | nan        |
| GA_aggressive           | 3y        | mdd                    | -0.196847 | -0.195513 | nan        | -0.385565 |  -0.493728 |
| GA_aggressive           | 3y        | relative_wealth_vs_spy |  0.197169 |  0.171769 |  -0.196302 | -0.048594 | nan        |
| GA_aggressive           | 5y        | cagr                   |  0.206113 |  0.153561 |   0.008347 |  0.097726 | nan        |
| GA_aggressive           | 5y        | mdd                    | -0.209588 | -0.263493 | nan        | -0.385565 |  -0.493728 |
| GA_aggressive           | 5y        | relative_wealth_vs_spy |  0.374950 |  0.285639 |  -0.075878 |  0.039100 | nan        |
| GA_robust               | 10y       | cagr                   |  0.184494 |  0.145449 |   0.072485 |  0.117611 | nan        |
| GA_robust               | 10y       | mdd                    | -0.257427 | -0.376637 | nan        | -0.376637 |  -0.412016 |
| GA_robust               | 10y       | relative_wealth_vs_spy |  0.316635 |  0.363614 |  -0.115173 |  0.058149 | nan        |
| GA_robust               | 15y       | cagr                   |  0.166556 |  0.141588 |   0.101755 |  0.118570 | nan        |
| GA_robust               | 15y       | mdd                    | -0.257427 | -0.376637 | nan        | -0.402431 |  -0.412016 |
| GA_robust               | 15y       | relative_wealth_vs_spy |  0.427964 |  0.835997 |   0.137860 |  0.356358 | nan        |
| GA_robust               | 3y        | cagr                   |  0.287527 |  0.144745 |  -0.082951 |  0.050934 | nan        |
| GA_robust               | 3y        | mdd                    | -0.182150 | -0.182340 | nan        | -0.376637 |  -0.412016 |
| GA_robust               | 3y        | relative_wealth_vs_spy |  0.176781 |  0.153575 |  -0.237064 | -0.084463 | nan        |
| GA_robust               | 5y        | cagr                   |  0.209711 |  0.139393 |   0.036029 |  0.097344 | nan        |
| GA_robust               | 5y        | mdd                    | -0.183580 | -0.257427 | nan        | -0.376637 |  -0.412016 |
| GA_robust               | 5y        | relative_wealth_vs_spy |  0.395584 |  0.262687 |  -0.129639 | -0.040841 | nan        |
| GA_stacked_seed20260519 | 10y       | cagr                   |  0.164978 |  0.142758 |   0.097126 |  0.122773 | nan        |
| GA_stacked_seed20260519 | 10y       | mdd                    | -0.225075 | -0.317004 | nan        | -0.317004 |  -0.317004 |
| GA_stacked_seed20260519 | 10y       | relative_wealth_vs_spy |  0.115093 |  0.333951 |  -0.188400 | -0.027752 | nan        |
| GA_stacked_seed20260519 | 15y       | cagr                   |  0.154359 |  0.144053 |   0.115121 |  0.126883 | nan        |
| GA_stacked_seed20260519 | 15y       | mdd                    | -0.225075 | -0.317004 | nan        | -0.317004 |  -0.317004 |
| GA_stacked_seed20260519 | 15y       | relative_wealth_vs_spy |  0.219685 |  0.901709 |  -0.063832 |  0.133588 | nan        |
| GA_stacked_seed20260519 | 3y        | cagr                   |  0.260430 |  0.128167 |  -0.041120 |  0.072477 | nan        |
| GA_stacked_seed20260519 | 3y        | mdd                    | -0.152253 | -0.161996 | nan        | -0.317004 |  -0.317004 |
| GA_stacked_seed20260519 | 3y        | relative_wealth_vs_spy |  0.104036 |  0.146555 |  -0.265245 | -0.104635 | nan        |
| GA_stacked_seed20260519 | 5y        | cagr                   |  0.176895 |  0.146009 |   0.057626 |  0.101524 | nan        |
| GA_stacked_seed20260519 | 5y        | mdd                    | -0.205107 | -0.225075 | nan        | -0.317004 |  -0.317004 |
| GA_stacked_seed20260519 | 5y        | relative_wealth_vs_spy |  0.216288 |  0.149283 |  -0.198072 | -0.080215 | nan        |
| GA_stacked_seed20260520 | 10y       | cagr                   |  0.161386 |  0.141759 |   0.097002 |  0.121994 | nan        |
| GA_stacked_seed20260520 | 10y       | mdd                    | -0.220485 | -0.309856 | nan        | -0.309856 |  -0.309856 |
| GA_stacked_seed20260520 | 10y       | relative_wealth_vs_spy |  0.081183 |  0.334023 |  -0.194831 | -0.037322 | nan        |
| GA_stacked_seed20260520 | 15y       | cagr                   |  0.152248 |  0.143246 |   0.115071 |  0.126288 | nan        |
| GA_stacked_seed20260520 | 15y       | mdd                    | -0.220485 | -0.309856 | nan        | -0.309856 |  -0.309856 |
| GA_stacked_seed20260520 | 15y       | relative_wealth_vs_spy |  0.186649 |  0.880949 |  -0.083617 |  0.107166 | nan        |
| GA_stacked_seed20260520 | 3y        | cagr                   |  0.253205 |  0.127419 |  -0.038019 |  0.071430 | nan        |
| GA_stacked_seed20260520 | 3y        | mdd                    | -0.149995 | -0.160239 | nan        | -0.309856 |  -0.309856 |
| GA_stacked_seed20260520 | 3y        | relative_wealth_vs_spy |  0.085159 |  0.139043 |  -0.265388 | -0.106840 | nan        |
| GA_stacked_seed20260520 | 5y        | cagr                   |  0.171612 |  0.144479 |   0.057476 |  0.101066 | nan        |
| GA_stacked_seed20260520 | 5y        | mdd                    | -0.204432 | -0.220485 | nan        | -0.309856 |  -0.309856 |
| GA_stacked_seed20260520 | 5y        | relative_wealth_vs_spy |  0.189233 |  0.141631 |  -0.199393 | -0.086661 | nan        |
| GA_stacked_seed20260521 | 10y       | cagr                   |  0.162348 |  0.141977 |   0.098069 |  0.122148 | nan        |
| GA_stacked_seed20260521 | 10y       | mdd                    | -0.220484 | -0.309737 | nan        | -0.309737 |  -0.309737 |
| GA_stacked_seed20260521 | 10y       | relative_wealth_vs_spy |  0.090176 |  0.332099 |  -0.194904 | -0.036955 | nan        |
| GA_stacked_seed20260521 | 15y       | cagr                   |  0.152781 |  0.143496 |   0.115603 |  0.126555 | nan        |
| GA_stacked_seed20260521 | 15y       | mdd                    | -0.220484 | -0.309737 | nan        | -0.309737 |  -0.309737 |
| GA_stacked_seed20260521 | 15y       | relative_wealth_vs_spy |  0.194917 |  0.889123 |  -0.081293 |  0.111783 | nan        |
| GA_stacked_seed20260521 | 3y        | cagr                   |  0.255703 |  0.127517 |  -0.036729 |  0.072166 | nan        |
| GA_stacked_seed20260521 | 3y        | mdd                    | -0.149796 | -0.159716 | nan        | -0.309737 |  -0.309737 |
| GA_stacked_seed20260521 | 3y        | relative_wealth_vs_spy |  0.091659 |  0.141373 |  -0.265986 | -0.106485 | nan        |
| GA_stacked_seed20260521 | 5y        | cagr                   |  0.173261 |  0.144898 |   0.057744 |  0.101305 | nan        |
| GA_stacked_seed20260521 | 5y        | mdd                    | -0.204099 | -0.220484 | nan        | -0.309737 |  -0.309737 |
| GA_stacked_seed20260521 | 5y        | relative_wealth_vs_spy |  0.197622 |  0.143036 |  -0.200272 | -0.086202 | nan        |
| Refined_GA_robust       | 10y       | cagr                   |  0.184494 |  0.145449 |   0.072485 |  0.117611 | nan        |
| Refined_GA_robust       | 10y       | mdd                    | -0.257427 | -0.376637 | nan        | -0.376637 |  -0.412016 |
| Refined_GA_robust       | 10y       | relative_wealth_vs_spy |  0.316635 |  0.363614 |  -0.115173 |  0.058149 | nan        |
| Refined_GA_robust       | 15y       | cagr                   |  0.166556 |  0.141588 |   0.101755 |  0.118570 | nan        |
| Refined_GA_robust       | 15y       | mdd                    | -0.257427 | -0.376637 | nan        | -0.402431 |  -0.412016 |
| Refined_GA_robust       | 15y       | relative_wealth_vs_spy |  0.427964 |  0.835997 |   0.137860 |  0.356358 | nan        |
| Refined_GA_robust       | 3y        | cagr                   |  0.287527 |  0.144745 |  -0.082951 |  0.050934 | nan        |
| Refined_GA_robust       | 3y        | mdd                    | -0.182150 | -0.182340 | nan        | -0.376637 |  -0.412016 |
| Refined_GA_robust       | 3y        | relative_wealth_vs_spy |  0.176781 |  0.153575 |  -0.237064 | -0.084463 | nan        |
| Refined_GA_robust       | 5y        | cagr                   |  0.209711 |  0.139393 |   0.036029 |  0.097344 | nan        |
| Refined_GA_robust       | 5y        | mdd                    | -0.183580 | -0.257427 | nan        | -0.376637 |  -0.412016 |
| Refined_GA_robust       | 5y        | relative_wealth_vs_spy |  0.395584 |  0.262687 |  -0.129639 | -0.040841 | nan        |
| SPYSIM_buy_hold         | 10y       | cagr                   |  0.152356 |  0.092352 |  -0.016981 |  0.028743 | nan        |
| SPYSIM_buy_hold         | 10y       | mdd                    | -0.336941 | -0.514493 | nan        | -0.551413 |  -0.551413 |
| SPYSIM_buy_hold         | 10y       | relative_wealth_vs_spy |  0.000000 |  0.000000 |   0.000000 |  0.000000 | nan        |
| SPYSIM_buy_hold         | 15y       | cagr                   |  0.139176 |  0.094865 |   0.035363 |  0.051702 | nan        |
| SPYSIM_buy_hold         | 15y       | mdd                    | -0.336941 | -0.551413 | nan        | -0.551413 |  -0.551413 |
| SPYSIM_buy_hold         | 15y       | relative_wealth_vs_spy |  0.000000 |  0.000000 |   0.000000 |  0.000000 | nan        |
| SPYSIM_buy_hold         | 3y        | cagr                   |  0.219526 |  0.113325 |  -0.172408 | -0.059217 | nan        |
| SPYSIM_buy_hold         | 3y        | mdd                    | -0.187450 | -0.193190 | nan        | -0.507224 |  -0.551413 |
| SPYSIM_buy_hold         | 3y        | relative_wealth_vs_spy |  0.000000 |  0.000000 |   0.000000 |  0.000000 | nan        |
| SPYSIM_buy_hold         | 5y        | cagr                   |  0.131698 |  0.112740 |  -0.083214 | -0.001628 | nan        |
| SPYSIM_buy_hold         | 5y        | mdd                    | -0.244419 | -0.336941 | nan        | -0.551413 |  -0.551413 |
| SPYSIM_buy_hold         | 5y        | relative_wealth_vs_spy |  0.000000 |  0.000000 |   0.000000 |  0.000000 | nan        |

## Regime Windows

Named drawdown/bull/recovery regimes are diagnostics, not optimized gates; they are included to check whether full-period results depend on one market state `[testing_tuning, p.327-335]`.

| candidate               | regime                |      cagr |       mdd |    sharpe |   sortino |    calmar |   terminal_wealth |   wealth_vs_spy |
|:------------------------|:----------------------|----------:|----------:|----------:|----------:|----------:|------------------:|----------------:|
| GA_aggressive           | dot_com_drawdown      | -0.209817 | -0.493728 | -0.830311 | -1.380029 | -0.424965 |          0.550899 |        1.040695 |
| GA_aggressive           | gfc_drawdown          | -0.218376 | -0.385565 | -0.625604 | -0.999222 | -0.566378 |          0.706055 |        1.559261 |
| GA_aggressive           | qe_bull               |  0.158976 | -0.189927 |  1.070488 |  1.423962 |  0.837037 |          4.362418 |        1.224799 |
| GA_aggressive           | covid_crash           | -0.952399 | -0.263493 | -4.607606 | -6.321097 | -3.614508 |          0.748271 |        1.123139 |
| GA_aggressive           | inflation_rates_shock | -0.170599 | -0.209588 | -0.640659 | -0.947039 | -0.813971 |          0.857573 |        1.090963 |
| GA_aggressive           | recent_recovery       |  0.311039 | -0.196847 |  1.574039 |  2.171239 |  1.580110 |          2.426897 |        1.248908 |
| GA_robust               | dot_com_drawdown      | -0.150246 | -0.412016 | -0.663433 | -1.077259 | -0.364660 |          0.662199 |        1.250950 |
| GA_robust               | gfc_drawdown          | -0.211245 | -0.376637 | -0.597213 | -0.946786 | -0.560871 |          0.715172 |        1.579395 |
| GA_robust               | qe_bull               |  0.141161 | -0.182340 |  0.997118 |  1.313403 |  0.774163 |          3.737310 |        1.049293 |
| GA_robust               | covid_crash           | -0.952047 | -0.257427 | -4.656134 | -6.485797 | -3.698314 |          0.748796 |        1.123927 |
| GA_robust               | inflation_rates_shock | -0.101275 | -0.183580 | -0.352253 | -0.516540 | -0.551667 |          0.916026 |        1.165325 |
| GA_robust               | recent_recovery       |  0.295690 | -0.182150 |  1.605447 |  2.190258 |  1.623333 |          2.335107 |        1.201671 |
| Refined_GA_robust       | dot_com_drawdown      | -0.150246 | -0.412016 | -0.663433 | -1.077259 | -0.364660 |          0.662199 |        1.250950 |
| Refined_GA_robust       | gfc_drawdown          | -0.211245 | -0.376637 | -0.597213 | -0.946786 | -0.560871 |          0.715172 |        1.579395 |
| Refined_GA_robust       | qe_bull               |  0.141161 | -0.182340 |  0.997118 |  1.313403 |  0.774163 |          3.737310 |        1.049293 |
| Refined_GA_robust       | covid_crash           | -0.952047 | -0.257427 | -4.656134 | -6.485797 | -3.698314 |          0.748796 |        1.123927 |
| Refined_GA_robust       | inflation_rates_shock | -0.101275 | -0.183580 | -0.352253 | -0.516540 | -0.551667 |          0.916026 |        1.165325 |
| Refined_GA_robust       | recent_recovery       |  0.295690 | -0.182150 |  1.605447 |  2.190258 |  1.623333 |          2.335107 |        1.201671 |
| B4_like_testfolio       | dot_com_drawdown      | -0.081612 | -0.284228 | -0.447191 | -0.735218 | -0.287137 |          0.806104 |        1.522798 |
| B4_like_testfolio       | gfc_drawdown          | -0.138094 | -0.261694 | -0.568205 | -0.885288 | -0.527695 |          0.810632 |        1.790211 |
| B4_like_testfolio       | qe_bull               |  0.142732 | -0.135395 |  1.325931 |  1.855481 |  1.054190 |          3.788990 |        1.063802 |
| B4_like_testfolio       | covid_crash           | -0.851096 | -0.197564 | -4.315994 | -5.307080 | -4.307942 |          0.834121 |        1.251999 |
| B4_like_testfolio       | inflation_rates_shock | -0.284063 | -0.249060 | -1.699749 | -2.520943 | -1.140540 |          0.759959 |        0.966783 |
| B4_like_testfolio       | recent_recovery       |  0.194872 | -0.141655 |  1.307856 |  1.913099 |  1.375680 |          1.791162 |        0.921752 |
| B4_no_margin_lead       | dot_com_drawdown      | -0.079008 | -0.299406 | -0.402345 | -0.662033 | -0.263881 |          0.811905 |        1.533757 |
| B4_no_margin_lead       | gfc_drawdown          | -0.093852 | -0.280222 | -0.283079 | -0.455270 | -0.334920 |          0.870032 |        1.921391 |
| B4_no_margin_lead       | qe_bull               |  0.139983 | -0.146093 |  1.181640 |  1.629161 |  0.958176 |          3.698952 |        1.038523 |
| B4_no_margin_lead       | covid_crash           | -0.854603 | -0.199989 | -4.122513 | -4.944236 | -4.273246 |          0.832230 |        1.249160 |
| B4_no_margin_lead       | inflation_rates_shock | -0.212027 | -0.214588 | -1.137415 | -1.654621 | -0.988064 |          0.822227 |        1.045998 |
| B4_no_margin_lead       | recent_recovery       |  0.235684 | -0.144136 |  1.456158 |  2.075756 |  1.635147 |          1.999344 |        1.028884 |
| SPYSIM_buy_hold         | dot_com_drawdown      | -0.222169 | -0.473769 | -0.947977 | -1.511025 | -0.468940 |          0.529357 |        1.000000 |
| SPYSIM_buy_hold         | gfc_drawdown          | -0.429261 | -0.551413 | -1.283170 | -1.782912 | -0.778475 |          0.452814 |        1.000000 |
| SPYSIM_buy_hold         | qe_bull               |  0.135675 | -0.193190 |  0.939441 |  1.176371 |  0.702285 |          3.561742 |        1.000000 |
| SPYSIM_buy_hold         | covid_crash           | -0.985937 | -0.336941 | -5.365338 | -8.269999 | -2.926141 |          0.666232 |        1.000000 |
| SPYSIM_buy_hold         | inflation_rates_shock | -0.254007 | -0.244419 | -1.095328 | -1.676038 | -1.039227 |          0.786069 |        1.000000 |
| SPYSIM_buy_hold         | recent_recovery       |  0.224983 | -0.187450 |  1.406155 |  1.914441 |  1.200231 |          1.943216 |        1.000000 |
| B4_original             | dot_com_drawdown      | -0.076077 | -0.279216 | -0.407648 | -0.671030 | -0.272465 |          0.818463 |        1.546145 |
| B4_original             | gfc_drawdown          | -0.132988 | -0.272761 | -0.507281 | -0.793465 | -0.487562 |          0.817425 |        1.805213 |
| B4_original             | qe_bull               |  0.142952 | -0.133154 |  1.325556 |  1.855068 |  1.073582 |          3.796286 |        1.065851 |
| B4_original             | covid_crash           | -0.860298 | -0.198591 | -4.362428 | -5.291126 | -4.332007 |          0.829069 |        1.244416 |
| B4_original             | inflation_rates_shock | -0.282235 | -0.247509 | -1.670189 | -2.470065 | -1.140299 |          0.761553 |        0.968811 |
| B4_original             | recent_recovery       |  0.205647 | -0.138700 |  1.371912 |  2.006833 |  1.482672 |          1.844588 |        0.949245 |
| GA_stacked_seed20260519 | dot_com_drawdown      | -0.095876 | -0.308204 | -0.485863 | -0.788994 | -0.311081 |          0.774783 |        1.463629 |
| GA_stacked_seed20260519 | gfc_drawdown          | -0.137139 | -0.317004 | -0.425491 | -0.677183 | -0.432609 |          0.811902 |        1.793016 |
| GA_stacked_seed20260519 | qe_bull               |  0.142537 | -0.161996 |  1.144968 |  1.549731 |  0.879875 |          3.782533 |        1.061989 |
| GA_stacked_seed20260519 | covid_crash           | -0.910337 | -0.225075 | -4.555074 | -5.644087 | -4.044591 |          0.794784 |        1.192954 |
| GA_stacked_seed20260519 | inflation_rates_shock | -0.194520 | -0.205107 | -0.998236 | -1.461128 | -0.948381 |          0.837203 |        1.065050 |
| GA_stacked_seed20260519 | recent_recovery       |  0.272094 | -0.152253 |  1.594239 |  2.202540 |  1.787119 |          2.198753 |        1.131502 |
| GA_stacked_seed20260520 | dot_com_drawdown      | -0.092115 | -0.302184 | -0.470856 | -0.766909 | -0.304831 |          0.782970 |        1.479095 |
| GA_stacked_seed20260520 | gfc_drawdown          | -0.130593 | -0.309856 | -0.408392 | -0.650862 | -0.421464 |          0.820617 |        1.812262 |
| GA_stacked_seed20260520 | qe_bull               |  0.141914 | -0.160239 |  1.154798 |  1.565227 |  0.885639 |          3.762011 |        1.056228 |
| GA_stacked_seed20260520 | covid_crash           | -0.904652 | -0.220485 | -4.517710 | -5.574839 | -4.103000 |          0.799451 |        1.199959 |
| GA_stacked_seed20260520 | inflation_rates_shock | -0.196067 | -0.204432 | -1.028571 | -1.502133 | -0.959081 |          0.835882 |        1.063369 |
| GA_stacked_seed20260520 | recent_recovery       |  0.264658 | -0.149995 |  1.577619 |  2.186860 |  1.764443 |          2.156952 |        1.109991 |
| GA_stacked_seed20260521 | dot_com_drawdown      | -0.090726 | -0.300396 | -0.462024 | -0.752525 | -0.302021 |          0.786006 |        1.484830 |
| GA_stacked_seed20260521 | gfc_drawdown          | -0.130188 | -0.309737 | -0.406601 | -0.647975 | -0.420319 |          0.821157 |        1.813453 |
| GA_stacked_seed20260521 | qe_bull               |  0.141894 | -0.159716 |  1.154653 |  1.564961 |  0.888413 |          3.761350 |        1.056042 |
| GA_stacked_seed20260521 | covid_crash           | -0.904645 | -0.220484 | -4.517547 | -5.574562 | -4.103002 |          0.799456 |        1.199967 |
| GA_stacked_seed20260521 | inflation_rates_shock | -0.195698 | -0.204099 | -1.026220 | -1.498688 | -0.958837 |          0.836197 |        1.063770 |
| GA_stacked_seed20260521 | recent_recovery       |  0.267178 | -0.149796 |  1.590352 |  2.204473 |  1.783617 |          2.171055 |        1.117249 |

## Analysis

### Verdict: B4-v2 core (35% GDESIM / 40% RSSTSIM / 25% ZROZSIM) is the winner

`B4_no_margin_lead` (the **35/40/25 B4-v2 core**) is the strongest practical static portfolio across **4 distinct GA challenges**: (1) local B4-like no-margin Pareto, (2) factor/momentum probe with VBR/MTUM/EFV, (3) core-beater levered/cash GA, (4) stacked-ETF expansion triage (2026-05-19). On this 2000-2026 window: CAGR `13.39%`, MDD `-29.94%`, Calmar `0.447`, terminal wealth `27.0x`, gross `1.0`, no negative `CASHX`.

### Trade-off analysis

- Versus `B4_original`, `B4_no_margin_lead` adds `1.27%` CAGR and worsens MDD by `2.02%` points, Calmar `0.447` vs `0.434`.
- Rolling relative-wealth p10 vs `SPYSIM` for the core remains negative in 3y (`-11.94%`), 5y (`-13.08%`), 10y (`-8.76%`); turns positive at 15y.
- `B4_like_testfolio` is a lower-drawdown stacked reference but lower CAGR (`11.72%`), lower Calmar (`0.412`), and requires negative `CASHX`.
- `GA_robust` (`50 RSST / 35 GDE / 10 SPY / 5 ZROZ`) adds `2.19%` CAGR vs B4-like but MDD is `-12.78%` pp worse; 5y rel-wealth p10 `-4.08%`.
- `GA_aggressive` adds only `0.40%` CAGR vs `GA_robust` while changing MDD by `-8.17%` pp.
- `Refined_GA_robust` is intentionally identical to `GA_robust`; confirms the artifact.

### 2026-05-19 Stacked-ETF Triage GA winners

3 seeds against the expanded 21-ticker universe (B4-v2 core anchors + 8 local proxies CTAP/RSBT/RSIT/HOLD/MATE/ESBG/GDT/ALLW + NTSXSIM/NTSDSIM/NTSISIM/BTALSIM/IEISIM). All 3 winners converged on similar structure: keep core anchors, add ~20-25% ESBGSIM, accent with small CTAPSIM/MATESIM. On this 2000-2026 window the best (`GA_stacked_seed20260521`) shows CAGR `13.91%`, MDD `-30.97%`, Calmar `0.449`, terminal wealth `30.5x` — `0.52%` CAGR over core, `1.03%` pp worse MDD, Calmar `+0.002` vs core.

**Proxy bias caveat:** the 8 stacked proxies are local composition (e.g. `CTAPSIM = SPYSIM + DBMFSIM - 1.0×CASHX`). Sanity check against real `RSST` showed the same formula overstates CAGR by `~5.56pp` vs the real ETF. The marginal Calmar edge of the GA stacked candidates over the core (`+0.002` to `+0.003` Calmar) is **inside the proxy-bias error band** — likely vanishes once fund-level ER and strategy implementation drift are modeled.

Under the actual GA fitness `core_relative_wealth_dominance` (rolling p10 dominance vs the core), the core fitness `0.350` beat the GA best `0.268` decisively. See `results/ga_b4v2_stacked_triage/REPORT.md`.

### Status

Discovery-only. Mandate §1 unchanged: 100% capital remains in Plano C passive factor-tilted. The report clarifies trade-offs and consolidates 4 GA-challenge outcomes but does not run PBO/DSR/walk-forward/bootstrap validation or authorize any mandate change `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Artifacts

- `metrics.csv`: full-period metrics plus regime-window metrics.
- `rolling.csv`: long-form rolling summary metrics.

## Next Step

Do not promote a winner. If continuing, run no-margin sensitivity and implementation-realism checks on `B4_no_margin_lead`: start-date sensitivity, rebalance frequency, ETF availability, drag assumptions, remove-one-asset tests, then walk-forward/static selection before any validation claim `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
