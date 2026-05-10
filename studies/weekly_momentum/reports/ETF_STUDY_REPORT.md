# Weekly Momentum ETF Study Report

## Scope

This report replicates the stock weekly-momentum variants on the cached ETF universe. The same honest daily-bar timing is used: Thursday signal, Friday sell, Monday buy. Momentum ranking follows `[stocks_on_the_move, p.60]`; SPY/SMA risk filter follows `[stocks_on_the_move, p.66-67, p.81]`.

## Variants

| variant | lookback | top_k | market filter | CAGR | MDD | Sharpe | Sortino | Calmar | Vol | VaR 5% | worst day |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline_top1_cash` | 4 | 1 | none | -14.43% | -99.46% | 0.032 | 0.047 | -0.145 | 59.37% | 5.93% | -23.25% |
| `short_mom_top5_sma100` | 4 | 5 | SPY>SMA100 | 0.25% | -65.91% | 0.120 | 0.166 | 0.004 | 21.59% | 2.15% | -12.24% |
| `aggressive_lb60_k3_sma200` | 60 | 3 | SPY>SMA200 | 12.93% | -52.03% | 0.555 | 0.763 | 0.248 | 30.21% | 3.04% | -20.53% |
| `balanced_lb60_k10_sma100` | 60 | 10 | SPY>SMA100 | 10.76% | -35.96% | 0.665 | 0.911 | 0.299 | 17.75% | 1.83% | -7.66% |

SPY over the aligned full window: CAGR 10.96%, MDD -55.20%, Sharpe 0.652.

## Subperiod Robustness

| variant | period | strategy CAGR | SPY CAGR | strategy MDD | SPY MDD | strategy Sharpe | SPY Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|
| `baseline_top1_cash` | 2014-2019 | -17.27% | 11.90% | -86.80% | -19.34% | -0.030 | 0.925 |
| `baseline_top1_cash` | 2014-2020 | -8.95% | 12.79% | -86.80% | -33.70% | 0.179 | 0.776 |
| `baseline_top1_cash` | 2021-2026 | -16.47% | 14.05% | -92.90% | -24.50% | 0.109 | 0.858 |
| `baseline_top1_cash` | 2022-2026 | -23.89% | 10.84% | -91.55% | -24.50% | 0.016 | 0.667 |
| `short_mom_top5_sma100` | 2014-2019 | 1.05% | 11.90% | -51.00% | -19.34% | 0.155 | 0.925 |
| `short_mom_top5_sma100` | 2014-2020 | -0.06% | 12.79% | -51.00% | -33.70% | 0.111 | 0.776 |
| `short_mom_top5_sma100` | 2021-2026 | 3.92% | 14.05% | -42.73% | -24.50% | 0.278 | 0.858 |
| `short_mom_top5_sma100` | 2022-2026 | 1.39% | 10.84% | -27.62% | -24.50% | 0.185 | 0.667 |
| `aggressive_lb60_k3_sma200` | 2014-2019 | 8.94% | 11.90% | -52.03% | -19.34% | 0.443 | 0.925 |
| `aggressive_lb60_k3_sma200` | 2014-2020 | 9.93% | 12.79% | -52.03% | -33.70% | 0.455 | 0.776 |
| `aggressive_lb60_k3_sma200` | 2021-2026 | 11.08% | 14.05% | -50.74% | -24.50% | 0.468 | 0.858 |
| `aggressive_lb60_k3_sma200` | 2022-2026 | 7.18% | 10.84% | -50.74% | -24.50% | 0.375 | 0.667 |
| `balanced_lb60_k10_sma100` | 2014-2019 | 5.52% | 11.90% | -35.96% | -19.34% | 0.416 | 0.925 |
| `balanced_lb60_k10_sma100` | 2014-2020 | 7.73% | 12.79% | -35.96% | -33.70% | 0.492 | 0.776 |
| `balanced_lb60_k10_sma100` | 2021-2026 | 9.70% | 14.05% | -34.52% | -24.50% | 0.541 | 0.858 |
| `balanced_lb60_k10_sma100` | 2022-2026 | 4.29% | 10.84% | -30.39% | -24.50% | 0.307 | 0.667 |

## Walk-Forward Diagnostic

ETF walk-forward report was generated under `studies/weekly_momentum/walk_forward/etfs/WALK_FORWARD_REPORT.md`; the bundle is not retained after final cleanup, but the decision metrics are preserved below.

Result: walk-forward CAGR 6.41%, MDD -48.64%, Sharpe 0.459 versus SPY CAGR 10.63%, MDD -55.20%, Sharpe 0.619.

## Verdict

- The ETF variants did not reproduce the stock-universe edge.
- The best replicated ETF variant by Sharpe is the balanced `lb60_k10_sma100`, but it still trails SPY materially in CAGR and Sharpe.
- ETF walk-forward is also weak, with lower Sharpe and worse MDD than SPY.
- Current conclusion: ETF migration should not proceed with this exact signal/filter set; it needs a distinct ETF-specific universe or signal design.

## Report Bundles

- `baseline_top1_cash`: `studies/weekly_momentum/results/etfs/lb4_sig3_sell1_sd0_k1_pos1_defcash_mf0/report.md`
- `short_mom_top5_sma100`: `studies/weekly_momentum/results/etfs/lb4_sig3_sell1_sd0_k5_pos1_defcash_mf100/report.md`
- `aggressive_lb60_k3_sma200`: `studies/weekly_momentum/results/etfs/lb60_sig3_sell1_sd0_k3_pos1_defcash_mf200/report.md`
- `balanced_lb60_k10_sma100`: `studies/weekly_momentum/results/etfs/lb60_sig3_sell1_sd0_k10_pos1_defcash_mf100/report.md`
