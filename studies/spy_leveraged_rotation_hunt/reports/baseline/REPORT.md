# SPY Leveraged Rotation Baseline Report

Window: `1986-01-03..2026-04-17`
Risk-off leg: `CASHX`

## Initial Screen

Strategies beating `SPY buy_hold` on CAGR, Sharpe, Sortino and MaxDD: `0`.

No baseline strategy clears the full economic screen versus SPY.

## Headline Metrics

| label         |   cagr |   sharpe |   sortino |     mdd |   calmar |   end_mult |   end_rel_to_benchmark |   pct_above_benchmark |
|:--------------|-------:|---------:|----------:|--------:|---------:|-----------:|-----------------------:|----------------------:|
| SPY buy_hold  | 0.1149 |   0.6819 |    0.8418 | -0.5514 |   0.2083 |    79.8565 |                 1.0000 |                0.0000 |
| LRS SPY->SSO  | 0.1388 |   0.6643 |    0.7586 | -0.5167 |   0.2686 |   187.5242 |                 2.3483 |                0.9890 |
| T3d SPY->SSO  | 0.1545 |   0.6435 |    0.7537 | -0.6342 |   0.2437 |   326.1745 |                 4.0845 |                0.4948 |
| T3d SPY->UPRO | 0.1723 |   0.5927 |    0.6944 | -0.8239 |   0.2092 |   604.2331 |                 7.5665 |                0.4509 |
| T3d SSO->SSO  | 0.1242 |   0.6065 |    0.6916 | -0.6502 |   0.1910 |   111.6756 |                 1.3985 |                0.5789 |
| LRS SPY->UPRO | 0.1640 |   0.6048 |    0.6907 | -0.7120 |   0.2303 |   452.7404 |                 5.6694 |                0.9957 |
| SSO buy_hold  | 0.1459 |   0.5564 |    0.6889 | -0.8827 |   0.1653 |   241.1824 |                 3.0202 |                0.8514 |
| UPRO buy_hold | 0.1351 |   0.5145 |    0.6375 | -0.9831 |   0.1374 |   164.4419 |                 2.0592 |                0.4258 |
| T3d SSO->UPRO | 0.1411 |   0.5475 |    0.6243 | -0.8234 |   0.1713 |   203.3350 |                 2.5463 |                0.6087 |

## Minimum Rolling CAGR

| label         |   3y_min |   5y_min |   10y_min |   15y_min |
|:--------------|---------:|---------:|----------:|----------:|
| LRS SPY->SSO  |  -0.1878 |  -0.0936 |   -0.0484 |    0.0214 |
| LRS SPY->UPRO |  -0.3029 |  -0.1801 |   -0.1050 |   -0.0071 |
| SPY buy_hold  |  -0.1724 |  -0.0832 |   -0.0410 |    0.0354 |
| SSO buy_hold  |  -0.3969 |  -0.2365 |   -0.1634 |   -0.0073 |
| T3d SPY->SSO  |  -0.2695 |  -0.1444 |   -0.0306 |    0.0624 |
| T3d SPY->UPRO |  -0.4120 |  -0.2643 |   -0.0929 |    0.0280 |
| T3d SSO->SSO  |  -0.2636 |  -0.1377 |   -0.0645 |    0.0292 |
| T3d SSO->UPRO |  -0.3990 |  -0.2381 |   -0.1280 |    0.0015 |
| UPRO buy_hold |  -0.5940 |  -0.3966 |   -0.3050 |   -0.0950 |

## Method Notes

All switching signals are executed with a one-day lag. LRS uses `SPY > SMA200` per Gayed `[leverage_for_the_long_run, p.13]`. T3d-style votes use price/SMA, realized-volatility and AR(1) components; volatility gates reflect LETF decay risk `[leverage_for_the_long_run, p.5-7]`.
