# T3d-K2 vs Iter030 vs Selected Top Configs

Status: comparative research report, not a validation verdict.

## TL;DR

This report compares the existing LETF anchors, **T3d-K2** and **iter030**, against
five concrete top configurations found in the QQQ/QLD/TQQQ technical vote search.

- In the Tiingo 2010+ real-ETF window, the selected technical configs dominate the
  QLD-based T3d/iter030 proxies on Sortino and CAGR.
- In the testfolio 1986+ stress window, only close-only configs can be replicated;
  those replicable configs lose decisively to T3d-K2 and iter030.
- The practical conclusion is unchanged: these configs are high-performance
  modern-regime leads, not robust replacements for the long-history anchors.

## Selected Configs

| ID | Source | Risk-on | k | Signals |
|---|---|---|---:|---|
| Cfg01 | TQQQ cash+lag1 rank #1 | TQQQ | 3 | `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70` |
| Cfg02 | TQQQ cash+lag1 rank #3 | TQQQ | 3 | `px_gt_sma20|sma100_gt_sma250|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70` |
| Cfg03 | TQQQ cash+lag1 k=1 variant | TQQQ | 1 | `px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100` |
| Cfg04 | QLD full-window OHLC rank #1 | QLD | 2 | `roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0` |
| Cfg05 | QLD same-window rank #1 | QLD | 3 | same signal set as Cfg01 |

Cfg01/Cfg02/Cfg05 are close-only and can be stress-tested on testfolio 1986+.
Cfg03/Cfg04 use OHLC-derived `CCI20` or `ATR14%`, so they are only evaluated in
the Tiingo panel.

## Tiingo 2010+ Panel

Common window: `2010-02-12..2026-04-14` for selected configs. Config rows use
`CASH_USD + extra_lag_days=1`. T3d/iter030 rows are QQQ/QLD Tiingo proxies;
iter030-like uses the existing state-machine proxy and should be read as a
directional reference, not bit-exact equivalence to the original testfolio run.

| Strategy | Risk-on | Sortino | CAGR | MDD | Calmar | End mult |
|---|---|---:|---:|---:|---:|---:|
| Cfg05 QLD common vote | QLD | 1.7066 | 36.27% | -37.54% | 0.9662 | 147x |
| Cfg01 TQQQ common vote | TQQQ | 1.6949 | 53.02% | -51.03% | 1.0389 | 955x |
| Cfg02 TQQQ SMA20 vote | TQQQ | 1.6811 | 52.30% | -48.23% | 1.0844 | 886x |
| Cfg03 TQQQ defensive k1 | TQQQ | 1.5569 | 52.51% | -55.28% | 0.9499 | 905x |
| Cfg04 QLD full-window OHLC | QLD | 1.5043 | 34.68% | -53.09% | 0.6532 | 122x |
| iter030-like proxy QLD/CASH | QLD | 1.3157 | 30.02% | -56.14% | 0.5348 | 69x |
| T3d-K2 proxy QLD/CASH | QLD | 1.2500 | 28.26% | -45.53% | 0.6207 | 56x |
| iter030-like proxy QLD/ZROZ | QLD | 1.2417 | 28.61% | -67.88% | 0.4214 | 58x |
| T3d-K2 proxy QLD/ZROZ | QLD | 1.1965 | 27.37% | -54.42% | 0.5029 | 50x |

### Performance Plot

![Tiingo 2010 equity and drawdown](plots/tiingo_2010_equity_drawdown.png)

### Rolling Windows

![Tiingo 2010 rolling windows](plots/tiingo_2010_rolling_3y.png)

## Testfolio 1986+ Panel

Common window: `1986-01-03..2026-04-17`. This panel compares canonical T3d-K2 and
iter030 against only the selected configs that can be represented with close-only
testfolio data. It is the stronger regime stress because it includes 1987,
2000-2002, and 2008.

| Strategy | Risk-on | Sortino | CAGR | MDD | Calmar | End mult |
|---|---|---:|---:|---:|---:|---:|
| iter030 canonical QLD/ZROZ LRS1.20 | QLD | 1.3839 | 36.68% | -55.48% | 0.6612 | 290,557x |
| T3d-K2 canonical QLD/ZROZ | QLD | 1.3240 | 31.08% | -64.50% | 0.4819 | 53,861x |
| Cfg02 TQQQ SMA20 vote / ZROZSIM | TQQQ | 0.9580 | 23.97% | -85.07% | 0.2818 | 5,701x |
| Cfg05 QLD common vote / ZROZSIM | QLD | 0.9387 | 19.19% | -67.65% | 0.2837 | 1,172x |
| Cfg05 QLD common vote / CASHX | QLD | 0.8994 | 17.06% | -76.73% | 0.2223 | 569x |
| Cfg01 TQQQ common vote / ZROZSIM | TQQQ | 0.8867 | 21.07% | -90.35% | 0.2332 | 2,198x |
| Cfg02 TQQQ SMA20 vote / CASHX | TQQQ | 0.8808 | 20.36% | -91.29% | 0.2231 | 1,746x |
| Cfg01 TQQQ common vote / CASHX | TQQQ | 0.8396 | 18.90% | -93.95% | 0.2012 | 1,067x |

### Performance Plot

![Testfolio 1986 equity and drawdown](plots/testfolio_1986_equity_drawdown.png)

### Rolling Windows

![Testfolio 1986 rolling windows](plots/testfolio_1986_rolling_10y.png)

## Interpretation

The selected configs are excellent in the post-2010 real-ETF sample, but the
long-history stress separates **modern performance** from **structural robustness**.
T3d-K2 and iter030 remain the better long-history anchors because their signal
structure survives older crisis and whipsaw regimes. The selected configs look
more like post-GFC QQQ/LETF regime specialists.

This does not make the configs useless. It changes the research question:

- Bad question: "Does Cfg01 replace iter030?"
- Better question: "Can a regime gate identify when the post-2010 technical vote
  family is valid?"

## Artifacts

Tables:

- `tables/tiingo_2010_comparison.csv`
- `tables/testfolio_1986_comparison.csv`

Plots:

- `plots/tiingo_2010_equity_drawdown.png`
- `plots/tiingo_2010_rolling_3y.png`
- `plots/testfolio_1986_equity_drawdown.png`
- `plots/testfolio_1986_rolling_10y.png`

## Verdict

Keep T3d-K2 and iter030 as the robust reference set. Carry Cfg01-Cfg05 into the
next validation panel as modern-regime challengers, not as promoted winners.
Promotion remains blocked unless a candidate clears OOS/WF/FWD, bootstrap, PBO,
DSR and execution realism gates `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
