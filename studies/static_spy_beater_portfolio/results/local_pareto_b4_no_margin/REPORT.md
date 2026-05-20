# B4-Like No-Margin Local Pareto Search

Fixed local grid over `1988-01-04..2026-04-17`. This search is constrained around the B4-like stability branch, not a broad GA. It uses 5% grid weights plus the original 2.5%-step Testfol.io reference as an anchor; negative `CASHX` means stacked/leverage reference, not pure long-only `[risk_parity, p.80-81]`, `[leverage_for_the_long_run, p.13]`.

This mode is implementation-constrained: `CASHX >= 0`, no negative cash, and gross weight is capped by non-negative weights.

## Search Rules

- Grid assets: `SPYSIM, GDESIM, KMLMSIM, RSSTSIM, ZROZSIM, IEFSIM, TLTSIM, CASHX`.
- GDESIM: `15-35%`.
- KMLMSIM + RSSTSIM: `15-40%`.
- ZROZSIM + IEFSIM + TLTSIM: `25-45%`.
- CASHX: `0%..10%` in 5% steps.
- Max active assets: `6` sleeves, to keep the search local around the compact B4-like stack.
- Feasible filter: full-period MDD no worse than `-32%` and rolling 5y CAGR p10 > `0`.
- Pareto objectives: maximize CAGR, MDD, Calmar, rolling 5y CAGR p10, and rolling 5y relative wealth p10 versus SPY `[testing_tuning, p.327-335]`.
- Rolling 5y MDD is not computed in this local screen; full-period MDD is the drawdown constraint. Use the separate Pareto/regime report for exact rolling MDD diagnostics.

## Counts

- Total rows scored: `37755`.
- Grid rows: `37752`.
- Feasible grid rows: `37476`.
- Pareto rows: `272`.

## References

| candidate                   |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   full_terminal_wealth |   rolling_5y_cagr_p10 |   rolling_5y_relative_wealth_spy_p10 |   cash_weight |   gross_weight | weights                                                                                              |
|:----------------------------|------------:|-----------:|--------------:|---------------:|--------------:|-----------------------:|----------------------:|-------------------------------------:|--------------:|---------------:|:-----------------------------------------------------------------------------------------------------|
| B4_like_testfolio_reference |    0.137542 |  -0.284228 |      0.981165 |       1.399840 |      0.483915 |             138.704709 |              0.073488 |                            -0.127681 |     -0.375000 |       1.750000 | {"CASHX": -0.375, "GDESIM": 0.25, "IEFSIM": 0.15, "KMLMSIM": 0.25, "SPYSIM": 0.475, "ZROZSIM": 0.25} |
| B4_original_reference       |    0.144308 |  -0.279216 |      1.017613 |       1.449482 |      0.516831 |             174.042047 |              0.078780 |                            -0.116198 |      0.000000 |       1.000000 | {"GDESIM": 0.25, "NTSXSIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25}                                  |
| SPYSIM_buy_hold             |    0.114583 |  -0.551413 |      0.691024 |       0.884039 |      0.207798 |              63.557308 |             -0.005341 |                            -0.000000 |      0.000000 |       1.000000 | {"SPYSIM": 1.0}                                                                                      |

## Top Pareto Rows

| candidate   |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   full_terminal_wealth |   rolling_5y_cagr_p10 |   rolling_5y_relative_wealth_spy_p10 |   cash_weight |   gross_weight | weights                                                                                          |
|:------------|------------:|-----------:|--------------:|---------------:|--------------:|-----------------------:|----------------------:|-------------------------------------:|--------------:|---------------:|:-------------------------------------------------------------------------------------------------|
| grid_06619  |    0.078571 |  -0.087644 |      1.328442 |       1.934329 |      0.896478 |              18.081855 |              0.043410 |                            -0.416343 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.15, "IEFSIM": 0.45, "KMLMSIM": 0.25, "SPYSIM": 0.05}                  |
| grid_15690  |    0.080130 |  -0.093909 |      1.253207 |       1.817101 |      0.853273 |              19.109867 |              0.044603 |                            -0.417480 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.2, "IEFSIM": 0.4, "KMLMSIM": 0.25, "TLTSIM": 0.05}                    |
| grid_06615  |    0.083633 |  -0.098953 |      1.301507 |       1.895653 |      0.845185 |              21.631137 |              0.049331 |                            -0.392147 |      0.050000 |       1.000000 | {"CASHX": 0.05, "GDESIM": 0.15, "IEFSIM": 0.4, "KMLMSIM": 0.25, "SPYSIM": 0.1, "TLTSIM": 0.05}   |
| grid_06038  |    0.088360 |  -0.104561 |      1.316063 |       1.915635 |      0.845055 |              25.551926 |              0.049818 |                            -0.384064 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.15, "IEFSIM": 0.45, "KMLMSIM": 0.2, "RSSTSIM": 0.1}                   |
| grid_06607  |    0.082317 |  -0.097867 |      1.313481 |       1.910254 |      0.841111 |              20.647832 |              0.049036 |                            -0.392954 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.15, "IEFSIM": 0.35, "KMLMSIM": 0.25, "SPYSIM": 0.1, "TLTSIM": 0.05}   |
| grid_16053  |    0.087767 |  -0.105237 |      1.237196 |       1.792504 |      0.833999 |              25.024782 |              0.050439 |                            -0.389022 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.2, "IEFSIM": 0.3, "KMLMSIM": 0.25, "RSSTSIM": 0.05, "TLTSIM": 0.1}    |
| grid_06609  |    0.084002 |  -0.100748 |      1.279327 |       1.866663 |      0.833776 |              21.914382 |              0.049484 |                            -0.390879 |      0.050000 |       1.000000 | {"CASHX": 0.05, "GDESIM": 0.15, "IEFSIM": 0.35, "KMLMSIM": 0.25, "SPYSIM": 0.1, "TLTSIM": 0.1}   |
| grid_14977  |    0.087863 |  -0.105956 |      1.250390 |       1.818693 |      0.829241 |              25.109070 |              0.051407 |                            -0.390648 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.2, "IEFSIM": 0.4, "KMLMSIM": 0.2, "RSSTSIM": 0.05, "ZROZSIM": 0.05}   |
| grid_05895  |    0.084468 |  -0.101903 |      1.337487 |       1.945688 |      0.828902 |              22.277903 |              0.050184 |                            -0.390452 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.15, "IEFSIM": 0.45, "KMLMSIM": 0.2, "RSSTSIM": 0.05, "SPYSIM": 0.05}  |
| grid_06670  |    0.084150 |  -0.101793 |      1.286788 |       1.876605 |      0.826682 |              22.029777 |              0.049353 |                            -0.390524 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.15, "IEFSIM": 0.35, "KMLMSIM": 0.25, "SPYSIM": 0.1, "ZROZSIM": 0.05}  |
| grid_06616  |    0.078950 |  -0.095535 |      1.304215 |       1.901283 |      0.826395 |              18.326472 |              0.043586 |                            -0.414846 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.15, "IEFSIM": 0.4, "KMLMSIM": 0.25, "SPYSIM": 0.05, "TLTSIM": 0.05}   |
| grid_06618  |    0.083253 |  -0.100766 |      1.320776 |       1.921844 |      0.826203 |              21.342403 |              0.049556 |                            -0.392394 |      0.050000 |       1.000000 | {"CASHX": 0.05, "GDESIM": 0.15, "IEFSIM": 0.45, "KMLMSIM": 0.25, "SPYSIM": 0.1}                  |
| grid_16067  |    0.088710 |  -0.107438 |      1.245777 |       1.805515 |      0.825681 |              25.868411 |              0.050860 |                            -0.388380 |      0.050000 |       1.000000 | {"CASHX": 0.05, "GDESIM": 0.2, "IEFSIM": 0.4, "KMLMSIM": 0.25, "RSSTSIM": 0.05, "TLTSIM": 0.05}  |
| grid_16081  |    0.089228 |  -0.108094 |      1.235044 |       1.793368 |      0.825469 |              26.343669 |              0.050786 |                            -0.387686 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.2, "IEFSIM": 0.35, "KMLMSIM": 0.25, "RSSTSIM": 0.05, "ZROZSIM": 0.05} |
| grid_06673  |    0.085453 |  -0.103714 |      1.272822 |       1.859645 |      0.823926 |              23.065649 |              0.049842 |                            -0.389170 |      0.050000 |       1.000000 | {"CASHX": 0.05, "GDESIM": 0.15, "IEFSIM": 0.4, "KMLMSIM": 0.25, "SPYSIM": 0.1, "ZROZSIM": 0.05}  |
| grid_06035  |    0.088738 |  -0.107741 |      1.298657 |       1.892548 |      0.823628 |              25.894302 |              0.050157 |                            -0.383462 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.15, "IEFSIM": 0.4, "KMLMSIM": 0.2, "RSSTSIM": 0.1, "TLTSIM": 0.05}    |
| grid_14957  |    0.086408 |  -0.105229 |      1.254794 |       1.820975 |      0.821144 |              23.855704 |              0.050937 |                            -0.392605 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.2, "IEFSIM": 0.35, "KMLMSIM": 0.2, "RSSTSIM": 0.05, "TLTSIM": 0.1}    |
| grid_15754  |    0.086645 |  -0.105583 |      1.235154 |       1.796522 |      0.820631 |              24.055368 |              0.050988 |                            -0.392484 |      0.050000 |       1.000000 | {"CASHX": 0.05, "GDESIM": 0.2, "IEFSIM": 0.4, "KMLMSIM": 0.25, "SPYSIM": 0.05, "ZROZSIM": 0.05}  |
| grid_15750  |    0.085345 |  -0.104416 |      1.246986 |       1.810190 |      0.817360 |              22.978560 |              0.050379 |                            -0.393969 |      0.100000 |       1.000000 | {"CASHX": 0.1, "GDESIM": 0.2, "IEFSIM": 0.35, "KMLMSIM": 0.25, "SPYSIM": 0.05, "ZROZSIM": 0.05}  |
| grid_16062  |    0.089075 |  -0.109785 |      1.228046 |       1.782977 |      0.811357 |              26.202560 |              0.050829 |                            -0.388151 |      0.050000 |       1.000000 | {"CASHX": 0.05, "GDESIM": 0.2, "IEFSIM": 0.35, "KMLMSIM": 0.25, "RSSTSIM": 0.05, "TLTSIM": 0.1}  |

## Highest-CAGR Feasible Rows

| candidate   |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   full_terminal_wealth |   rolling_5y_cagr_p10 |   rolling_5y_relative_wealth_spy_p10 |   cash_weight |   gross_weight | weights                                                                           |
|:------------|------------:|-----------:|--------------:|---------------:|--------------:|-----------------------:|----------------------:|-------------------------------------:|--------------:|---------------:|:----------------------------------------------------------------------------------|
| grid_33959  |    0.156997 |  -0.299406 |      1.039900 |       1.484318 |      0.524363 |             265.442795 |              0.087100 |                            -0.085894 |      0.000000 |       1.000000 | {"GDESIM": 0.35, "RSSTSIM": 0.4, "ZROZSIM": 0.25}                                 |
| grid_27657  |    0.155842 |  -0.305002 |      1.045635 |       1.492498 |      0.510954 |             255.485070 |              0.084116 |                            -0.089547 |      0.000000 |       1.000000 | {"GDESIM": 0.3, "RSSTSIM": 0.4, "SPYSIM": 0.05, "ZROZSIM": 0.25}                  |
| grid_33957  |    0.155261 |  -0.301555 |      1.042884 |       1.483000 |      0.514869 |             250.614575 |              0.084035 |                            -0.086957 |      0.000000 |       1.000000 | {"GDESIM": 0.35, "RSSTSIM": 0.4, "TLTSIM": 0.05, "ZROZSIM": 0.2}                  |
| grid_33958  |    0.154962 |  -0.300142 |      1.046273 |       1.485588 |      0.516294 |             248.140640 |              0.083576 |                            -0.088454 |      0.000000 |       1.000000 | {"GDESIM": 0.35, "IEFSIM": 0.05, "RSSTSIM": 0.4, "ZROZSIM": 0.2}                  |
| grid_19977  |    0.154634 |  -0.311065 |      1.049197 |       1.497407 |      0.497112 |             245.462400 |              0.081548 |                            -0.097884 |      0.000000 |       1.000000 | {"GDESIM": 0.25, "RSSTSIM": 0.4, "SPYSIM": 0.1, "ZROZSIM": 0.25}                  |
| grid_27661  |    0.154624 |  -0.281207 |      1.048791 |       1.512235 |      0.549858 |             245.380514 |              0.091549 |                            -0.123664 |      0.000000 |       1.000000 | {"GDESIM": 0.3, "RSSTSIM": 0.4, "ZROZSIM": 0.3}                                   |
| grid_27650  |    0.154106 |  -0.306799 |      1.048884 |       1.492347 |      0.502304 |             241.203975 |              0.081047 |                            -0.090769 |      0.000000 |       1.000000 | {"GDESIM": 0.3, "RSSTSIM": 0.4, "SPYSIM": 0.05, "TLTSIM": 0.05, "ZROZSIM": 0.2}   |
| grid_27653  |    0.153806 |  -0.304740 |      1.052341 |       1.494921 |      0.504711 |             238.810785 |              0.080399 |                            -0.091249 |      0.000000 |       1.000000 | {"GDESIM": 0.3, "IEFSIM": 0.05, "RSSTSIM": 0.4, "SPYSIM": 0.05, "ZROZSIM": 0.2}   |
| grid_33954  |    0.153491 |  -0.303736 |      1.044467 |       1.479813 |      0.505343 |             236.328499 |              0.081363 |                            -0.088706 |      0.000000 |       1.000000 | {"GDESIM": 0.35, "RSSTSIM": 0.4, "TLTSIM": 0.1, "ZROZSIM": 0.15}                  |
| grid_19987  |    0.153431 |  -0.287449 |      1.053279 |       1.518434 |      0.533766 |             235.857388 |              0.088652 |                            -0.128473 |      0.000000 |       1.000000 | {"GDESIM": 0.25, "RSSTSIM": 0.4, "SPYSIM": 0.05, "ZROZSIM": 0.3}                  |
| grid_11371  |    0.153374 |  -0.317107 |      1.050390 |       1.498144 |      0.483666 |             235.411790 |              0.078662 |                            -0.103336 |      0.000000 |       1.000000 | {"GDESIM": 0.2, "RSSTSIM": 0.4, "SPYSIM": 0.15, "ZROZSIM": 0.25}                  |
| grid_33955  |    0.153174 |  -0.302397 |      1.047199 |       1.480799 |      0.506533 |             233.858223 |              0.080511 |                            -0.091709 |      0.000000 |       1.000000 | {"GDESIM": 0.35, "IEFSIM": 0.05, "RSSTSIM": 0.4, "TLTSIM": 0.05, "ZROZSIM": 0.15} |
| grid_27659  |    0.152959 |  -0.282598 |      1.055781 |       1.517931 |      0.541259 |             232.193886 |              0.088923 |                            -0.122224 |      0.000000 |       1.000000 | {"GDESIM": 0.3, "RSSTSIM": 0.4, "TLTSIM": 0.05, "ZROZSIM": 0.25}                  |
| grid_33934  |    0.152910 |  -0.297839 |      1.027251 |       1.462183 |      0.513400 |             231.820750 |              0.083287 |                            -0.085756 |      0.000000 |       1.000000 | {"GDESIM": 0.35, "RSSTSIM": 0.35, "SPYSIM": 0.05, "ZROZSIM": 0.25}                |
| grid_19961  |    0.152899 |  -0.312501 |      1.052644 |       1.497488 |      0.489275 |             231.732488 |              0.078728 |                            -0.097912 |      0.000000 |       1.000000 | {"GDESIM": 0.25, "RSSTSIM": 0.4, "SPYSIM": 0.1, "TLTSIM": 0.05, "ZROZSIM": 0.2}   |
| grid_33956  |    0.152845 |  -0.301602 |      1.049320 |       1.481098 |      0.506776 |             231.314525 |              0.079854 |                            -0.091607 |      0.000000 |       1.000000 | {"GDESIM": 0.35, "IEFSIM": 0.1, "RSSTSIM": 0.4, "ZROZSIM": 0.15}                  |
| grid_27660  |    0.152698 |  -0.280908 |      1.061628 |       1.523672 |      0.543586 |             230.188533 |              0.088189 |                            -0.119465 |      0.000000 |       1.000000 | {"GDESIM": 0.3, "IEFSIM": 0.05, "RSSTSIM": 0.4, "ZROZSIM": 0.25}                  |
| grid_19967  |    0.152597 |  -0.310634 |      1.056134 |       1.500220 |      0.491244 |             229.421474 |              0.078269 |                            -0.098962 |      0.000000 |       1.000000 | {"GDESIM": 0.25, "IEFSIM": 0.05, "RSSTSIM": 0.4, "SPYSIM": 0.1, "ZROZSIM": 0.2}   |
| grid_27640  |    0.152337 |  -0.308961 |      1.050692 |       1.489233 |      0.493061 |             227.445701 |              0.078095 |                            -0.092245 |      0.000000 |       1.000000 | {"GDESIM": 0.3, "RSSTSIM": 0.4, "SPYSIM": 0.05, "TLTSIM": 0.1, "ZROZSIM": 0.15}   |
| grid_11390  |    0.152185 |  -0.293670 |      1.055378 |       1.520568 |      0.518217 |             226.299591 |              0.085808 |                            -0.131878 |      0.000000 |       1.000000 | {"GDESIM": 0.2, "RSSTSIM": 0.4, "SPYSIM": 0.1, "ZROZSIM": 0.3}                    |

## Plots

![CAGR vs MDD](plots/cagr_vs_mdd.png)

![Calmar vs CAGR](plots/calmar_vs_cagr.png)

## Reading

Top Pareto-by-Calmar candidate `grid_06619` reached CAGR `7.86%`, MDD `-8.76%`, Calmar `0.896`, and 5y CAGR p10 `4.34%`. It remains discovery-only. The highest-CAGR feasible row `grid_33959` reached CAGR `15.70%`, MDD `-29.94%`, Calmar `0.524`, and 5y relative-wealth p10 vs SPY `-8.59%`.

Status remains discovery-only: this is a local decision-quality screen, not PBO/DSR/walk-forward/bootstrap validation `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
