# Weekly Momentum Walk-Forward Report

## Setup

- Variation: `etfs` / universe `all_etfs`.
- Grid: lookbacks `60,80,100`, top_k `5,10,20`, market filters `sma200,sma250`, allow_negative `0`.
- Windows: `3`y train -> `1`y test, rolled by test window.
- Selection score: train Sharpe + train CAGR - abs(train MDD).
- Purpose: reduce parameter overfit by evaluating each selected config only in subsequent unseen windows `[advances_fin_ml, p.208-211]`.

## Walk-Forward Result

| metric | walk-forward | SPY |
|---|---:|---:|
| CAGR | 9.39% | 10.63% |
| MDD | -37.25% | -55.20% |
| Sharpe | 0.604 | 0.619 |
| Sortino | 0.816 | 0.874 |

![Walk-forward vs SPY](walk_forward_vs_spy.png)

## Window Selections

| train_start   | train_end   | test_start   | test_end   | selected_config                                |   selection_score |   train_cagr |   train_mdd |   train_sharpe |   test_cagr |   test_mdd |   test_sharpe |
|:--------------|:------------|:-------------|:-----------|:-----------------------------------------------|------------------:|-------------:|------------:|---------------:|------------:|-----------:|--------------:|
| 2002-07-26    | 2005-07-25  | 2005-07-26   | 2006-07-25 | lb80_sig3_sell1_sd0_k5_neg0_defcash_mfsma250   |          1.32461  |    0.0788476 |  -0.0602302 |       1.30599  |  0.192188   | -0.139876  |     1.3027    |
| 2003-07-26    | 2006-07-25  | 2006-07-26   | 2007-07-25 | lb80_sig3_sell1_sd0_k5_neg0_defcash_mfsma250   |          1.38013  |    0.144042  |  -0.139876  |       1.37596  |  0.264563   | -0.106677  |     1.62279   |
| 2004-07-26    | 2007-07-25  | 2007-07-26   | 2008-07-25 | lb80_sig3_sell1_sd0_k5_neg0_defcash_mfsma250   |          1.75134  |    0.236545  |  -0.139876  |       1.65468  |  0.114663   | -0.100404  |     0.792115  |
| 2005-07-26    | 2008-07-25  | 2008-07-26   | 2009-07-25 | lb80_sig3_sell1_sd0_k5_neg0_defcash_mfsma250   |          1.28532  |    0.188695  |  -0.141297  |       1.23792  |  0          |  0         |     0         |
| 2006-07-26    | 2009-07-25  | 2009-07-26   | 2010-07-25 | lb80_sig3_sell1_sd0_k10_neg0_defcash_mfsma250  |          1.00173  |    0.106909  |  -0.115347  |       1.01017  |  0.108247   | -0.130176  |     0.596908  |
| 2007-07-26    | 2010-07-25  | 2010-07-26   | 2011-07-25 | lb80_sig3_sell1_sd0_k20_neg0_defcash_mfsma250  |          0.636962 |    0.0713126 |  -0.0974137 |       0.663063 |  0.364174   | -0.0839271 |     2.14001   |
| 2008-07-26    | 2011-07-25  | 2011-07-26   | 2012-07-25 | lb80_sig3_sell1_sd0_k20_neg0_defcash_mfsma250  |          1.4381   |    0.175737  |  -0.0974137 |       1.35977  |  0.0367863  | -0.129828  |     0.35889   |
| 2009-07-26    | 2012-07-25  | 2012-07-26   | 2013-07-25 | lb80_sig3_sell1_sd0_k20_neg0_defcash_mfsma250  |          1.34641  |    0.18951   |  -0.129828  |       1.28673  |  0.0762608  | -0.120928  |     0.639736  |
| 2010-07-26    | 2013-07-25  | 2013-07-26   | 2014-07-25 | lb60_sig3_sell1_sd0_k10_neg0_defcash_mfsma250  |          1.33064  |    0.239622  |  -0.182866  |       1.27388  |  0.282253   | -0.0898499 |     1.68407   |
| 2011-07-26    | 2014-07-25  | 2014-07-26   | 2015-07-25 | lb100_sig3_sell1_sd0_k20_neg0_defcash_mfsma250 |          1.24969  |    0.153157  |  -0.116687  |       1.21322  | -0.0434785  | -0.102103  |    -0.24515   |
| 2012-07-26    | 2015-07-25  | 2015-07-26   | 2016-07-25 | lb100_sig3_sell1_sd0_k20_neg0_defcash_mfsma250 |          0.997819 |    0.125939  |  -0.102103  |       0.973983 | -0.0281785  | -0.132039  |    -0.204409  |
| 2013-07-26    | 2016-07-25  | 2016-07-26   | 2017-07-25 | lb100_sig3_sell1_sd0_k20_neg0_defcash_mfsma250 |          0.349406 |    0.0545592 |  -0.198753  |       0.493599 |  0.203216   | -0.0750539 |     1.60239   |
| 2014-07-26    | 2017-07-25  | 2017-07-26   | 2018-07-25 | lb100_sig3_sell1_sd0_k20_neg0_defcash_mfsma250 |          0.202724 |    0.0381385 |  -0.198753  |       0.363338 |  0.208751   | -0.142486  |     1.23639   |
| 2015-07-26    | 2018-07-25  | 2018-07-26   | 2019-07-25 | lb100_sig3_sell1_sd0_k20_neg0_defcash_mfsma250 |          0.91036  |    0.122248  |  -0.142486  |       0.930597 | -0.00077179 | -0.142144  |     0.0611948 |
| 2016-07-26    | 2019-07-25  | 2019-07-26   | 2020-07-25 | lb100_sig3_sell1_sd0_k10_neg0_defcash_mfsma250 |          0.957077 |    0.174985  |  -0.179523  |       0.961614 | -0.0969686  | -0.372548  |    -0.267507  |
| 2017-07-26    | 2020-07-25  | 2020-07-26   | 2021-07-25 | lb60_sig3_sell1_sd0_k10_neg0_defcash_mfsma200  |          0.478646 |    0.104503  |  -0.243785  |       0.617929 |  0.667982   | -0.198061  |     1.88328   |
| 2018-07-26    | 2021-07-25  | 2021-07-26   | 2022-07-25 | lb60_sig3_sell1_sd0_k20_neg0_defcash_mfsma200  |          1.19483  |    0.206973  |  -0.197955  |       1.18581  | -0.0643494  | -0.160037  |    -0.461588  |
| 2019-07-26    | 2022-07-25  | 2022-07-26   | 2023-07-25 | lb100_sig3_sell1_sd0_k20_neg0_defcash_mfsma200 |          0.978842 |    0.170899  |  -0.18596   |       0.993902 |  0.106286   | -0.115561  |     0.872906  |
| 2020-07-26    | 2023-07-25  | 2023-07-26   | 2024-07-25 | lb80_sig3_sell1_sd0_k5_neg0_defcash_mfsma250   |          1.39876  |    0.418587  |  -0.265841  |       1.24602  | -0.173177   | -0.279972  |    -0.395388  |
| 2021-07-26    | 2024-07-25  | 2024-07-26   | 2025-07-25 | lb100_sig3_sell1_sd0_k10_neg0_defcash_mfsma250 |          0.429679 |    0.0918277 |  -0.19655   |       0.534402 | -0.048079   | -0.185227  |    -0.195908  |

## Top Full-Period Configs In Grid

| config                                         |      cagr |       mdd |   sharpe |
|:-----------------------------------------------|----------:|----------:|---------:|
| lb80_sig3_sell1_sd0_k20_neg0_defcash_mfsma250  | 0.110315  | -0.249225 | 0.859655 |
| lb100_sig3_sell1_sd0_k20_neg0_defcash_mfsma250 | 0.110826  | -0.299258 | 0.84342  |
| lb60_sig3_sell1_sd0_k20_neg0_defcash_mfsma250  | 0.101677  | -0.276906 | 0.812651 |
| lb80_sig3_sell1_sd0_k10_neg0_defcash_mfsma250  | 0.130934  | -0.314256 | 0.783908 |
| lb100_sig3_sell1_sd0_k20_neg0_defcash_mfsma200 | 0.0989509 | -0.21172  | 0.781081 |
| lb80_sig3_sell1_sd0_k20_neg0_defcash_mfsma200  | 0.0964792 | -0.229551 | 0.773957 |
| lb100_sig3_sell1_sd0_k10_neg0_defcash_mfsma250 | 0.128135  | -0.372548 | 0.750832 |
| lb60_sig3_sell1_sd0_k20_neg0_defcash_mfsma200  | 0.0909187 | -0.263023 | 0.743925 |
| lb100_sig3_sell1_sd0_k10_neg0_defcash_mfsma200 | 0.123421  | -0.333204 | 0.737135 |
| lb60_sig3_sell1_sd0_k10_neg0_defcash_mfsma250  | 0.118094  | -0.357351 | 0.730583 |
| lb80_sig3_sell1_sd0_k10_neg0_defcash_mfsma200  | 0.119487  | -0.27256  | 0.72956  |
| lb60_sig3_sell1_sd0_k10_neg0_defcash_mfsma200  | 0.114862  | -0.330721 | 0.716466 |
| lb80_sig3_sell1_sd0_k5_neg0_defcash_mfsma250   | 0.151191  | -0.399335 | 0.695919 |
| lb80_sig3_sell1_sd0_k5_neg0_defcash_mfsma200   | 0.146064  | -0.409003 | 0.68402  |
| lb60_sig3_sell1_sd0_k5_neg0_defcash_mfsma200   | 0.138222  | -0.447285 | 0.6611   |

## Caveats

- This is walk-forward, not yet full CPCV/PBO/DSR/bootstrap validation.
- ETF cache coverage is not a point-in-time investable universe.
- Costs, slippage and taxes are still absent.
