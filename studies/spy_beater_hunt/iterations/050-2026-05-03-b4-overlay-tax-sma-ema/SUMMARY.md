# Iter 050 - B4 overlay tax and SMA/EMA sensitivity

**Date:** 2026-05-03
**Tax model:** 15% annual tax on positive realized gains from monthly rebalances; losses offset gains within the same year only.
**Note:** static row is forced monthly rebalance for tax comparability. Live lazy-rebal static can defer tax more than this.

## Ranking By Net Sharpe

| # | strategy | net CAGR | net MDD | net Sharpe | gross CAGR | tax paid |
|---:|---|---:|---:|---:|---:|---:|
| 1 | overlay_sma150_12mdd_10pp | 12.35% | -28.00% | 0.901 | 13.34% | $101,808 |
| 2 | overlay_sma126_12mdd_10pp | 12.32% | -27.61% | 0.901 | 13.31% | $102,083 |
| 3 | overlay_ema150_12mdd_10pp | 12.28% | -27.97% | 0.897 | 13.29% | $101,057 |
| 4 | overlay_sma180_12mdd_10pp | 12.26% | -27.65% | 0.895 | 13.24% | $98,843 |
| 5 | overlay_ema126_12mdd_10pp | 12.20% | -27.59% | 0.894 | 13.26% | $101,145 |
| 6 | overlay_ema200_12mdd_10pp | 12.24% | -27.98% | 0.893 | 13.20% | $98,465 |
| 7 | overlay_ema210_12mdd_10pp | 12.23% | -27.94% | 0.893 | 13.18% | $98,092 |
| 8 | overlay_ema180_12mdd_10pp | 12.22% | -27.94% | 0.892 | 13.16% | $97,528 |
| 9 | overlay_sma200_12mdd_10pp | 12.22% | -27.75% | 0.892 | 13.19% | $98,028 |
| 10 | overlay_sma210_12mdd_10pp | 12.22% | -27.75% | 0.892 | 13.19% | $98,028 |
| 11 | overlay_sma252_12mdd_10pp | 12.23% | -27.75% | 0.892 | 13.16% | $91,096 |
| 12 | overlay_ema252_12mdd_10pp | 12.17% | -27.79% | 0.888 | 13.10% | $89,824 |
| 13 | static_b4_forced_monthly | 12.18% | -30.88% | 0.880 | 12.88% | $74,272 |

## Verdict

Forced-monthly static B4 after tax: 12.18% CAGR / -30.88% MDD / 0.880 Sharpe.
Best after-tax overlay: `overlay_sma150_12mdd_10pp` at 12.35% CAGR / -28.00% MDD / 0.901 Sharpe.

## Interpretation

If multiple nearby SMA/EMA windows work, the overlay is less likely to be a single 200d crowding artifact. If only one window works, treat it as parameter fragility.
