# Iter 051 - LETF risk-on overlay

**Date:** 2026-05-03
**Tax model:** 15% annual tax on positive realized gains from monthly rebalances.
**Grid:** SSO/QLD/UPRO/TQQQ, 5-50% in 5pp steps, SMA/EMA 150/200, funded from ZROZ or NTSX only in risk-on state.

## Top 20 By Net Sharpe

| # | strategy | net CAGR | net MDD | net Sharpe | gross CAGR | tax paid |
|---:|---|---:|---:|---:|---:|---:|
| 1 | overlay_sma150_12mdd_10pp | 12.35% | -28.00% | 0.901 | 13.34% | $101,808 |
| 2 | qld_5_sma150_from_ZROZ | 12.87% | -28.92% | 0.900 | 13.92% | $121,043 |
| 3 | qld_5_sma150_from_NTSX | 12.75% | -28.54% | 0.899 | 13.76% | $114,788 |
| 4 | tqqq_5_sma150_from_ZROZ | 13.21% | -29.26% | 0.898 | 14.28% | $135,491 |
| 5 | tqqq_5_sma150_from_NTSX | 13.08% | -28.84% | 0.897 | 14.12% | $128,945 |
| 6 | qld_5_ema150_from_ZROZ | 12.80% | -28.90% | 0.897 | 13.87% | $119,741 |
| 7 | qld_5_ema150_from_NTSX | 12.68% | -28.51% | 0.896 | 13.71% | $113,225 |
| 8 | tqqq_5_ema150_from_ZROZ | 13.13% | -29.24% | 0.894 | 14.22% | $133,867 |
| 9 | qld_10_sma150_from_NTSX | 13.17% | -29.09% | 0.894 | 14.16% | $128,657 |
| 10 | tqqq_5_ema150_from_NTSX | 13.02% | -28.81% | 0.894 | 14.07% | $126,637 |
| 11 | qld_5_sma200_from_NTSX | 12.68% | -28.33% | 0.892 | 13.67% | $112,448 |
| 12 | overlay_sma200_12mdd_10pp | 12.22% | -27.75% | 0.892 | 13.19% | $98,028 |
| 13 | sso_5_sma150_from_ZROZ | 12.60% | -28.68% | 0.892 | 13.63% | $110,727 |
| 14 | qld_10_ema150_from_NTSX | 13.11% | -29.05% | 0.892 | 14.11% | $127,041 |
| 15 | qld_5_ema200_from_NTSX | 12.66% | -28.56% | 0.891 | 13.65% | $111,794 |
| 16 | tqqq_5_sma200_from_NTSX | 13.02% | -28.68% | 0.891 | 14.03% | $126,466 |
| 17 | sso_5_sma150_from_NTSX | 12.47% | -28.22% | 0.890 | 13.47% | $104,349 |
| 18 | qld_5_sma200_from_ZROZ | 12.76% | -28.78% | 0.890 | 13.78% | $116,737 |
| 19 | sso_5_ema150_from_ZROZ | 12.53% | -28.65% | 0.889 | 13.57% | $109,671 |
| 20 | qld_5_ema200_from_ZROZ | 12.74% | -29.00% | 0.888 | 13.76% | $115,958 |

## Top 10 LETF Rows By Net CAGR

| # | strategy | net CAGR | net MDD | net Sharpe | gross CAGR | tax paid |
|---:|---|---:|---:|---:|---:|---:|
| 1 | tqqq_45_sma150_from_NTSX | 16.78% | -44.64% | 0.742 | 18.24% | $491,433 |
| 2 | tqqq_50_sma150_from_NTSX | 16.78% | -44.64% | 0.732 | 18.24% | $491,195 |
| 3 | tqqq_45_sma200_from_NTSX | 16.75% | -44.64% | 0.736 | 18.18% | $484,412 |
| 4 | tqqq_50_sma200_from_NTSX | 16.72% | -44.64% | 0.725 | 18.16% | $480,091 |
| 5 | tqqq_45_ema150_from_NTSX | 16.69% | -44.64% | 0.741 | 18.14% | $473,463 |
| 6 | tqqq_50_ema150_from_NTSX | 16.66% | -44.64% | 0.729 | 18.12% | $469,591 |
| 7 | tqqq_40_sma200_from_NTSX | 16.64% | -43.86% | 0.749 | 18.11% | $476,330 |
| 8 | tqqq_40_sma150_from_NTSX | 16.62% | -43.86% | 0.753 | 18.11% | $474,857 |
| 9 | tqqq_40_ema150_from_NTSX | 16.55% | -43.86% | 0.752 | 18.04% | $460,051 |
| 10 | tqqq_35_sma200_from_NTSX | 16.51% | -42.92% | 0.769 | 18.05% | $465,981 |

## Best Row Per LETF

| LETF | best by Sharpe | net CAGR | net MDD | net Sharpe | best by CAGR | net CAGR | net MDD | net Sharpe |
|---|---|---:|---:|---:|---|---:|---:|---:|
| SSO | `sso_5_sma150_from_ZROZ` | 12.60% | -28.68% | 0.892 | `sso_40_sma150_from_ZROZ` | 13.31% | -30.67% | 0.832 |
| QLD | `qld_5_sma150_from_ZROZ` | 12.87% | -28.92% | 0.900 | `qld_50_sma150_from_NTSX` | 14.94% | -34.14% | 0.802 |
| UPRO | `upro_5_sma150_from_ZROZ` | 12.79% | -28.90% | 0.886 | `upro_50_sma150_from_NTSX` | 14.41% | -33.96% | 0.764 |
| TQQQ | `tqqq_5_sma150_from_ZROZ` | 13.21% | -29.26% | 0.898 | `tqqq_45_sma150_from_NTSX` | 16.78% | -44.64% | 0.742 |

## Verdict

Static forced-monthly B4: 12.18% / -30.88% / 0.880.
Best no-LETF overlay: `overlay_sma150_12mdd_10pp` at 12.35% / -28.00% / 0.901.
Best grid row by net Sharpe: `overlay_sma150_12mdd_10pp` at 12.35% / -28.00% / 0.901.
Best LETF by net Sharpe: `qld_5_sma150_from_ZROZ` at 12.87% / -28.92% / 0.900.
Best LETF by net CAGR: `tqqq_45_sma150_from_NTSX` at 16.78% / -44.64% / 0.742.

LETF rows beating the no-LETF overlay on both after-tax Sharpe and MDD: 0.
Conclusion: reject LETF sleeves for the balanced live candidate. The expanded 5-50% grid buys higher CAGR by accepting materially worse drawdown and lower risk-adjusted return versus the cleaner no-LETF overlay; this is a return-seeking variant only, not a core improvement.
