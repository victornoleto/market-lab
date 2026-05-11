# Iter 032 — Taxed Underlying/Risk-On Variant Report

**Iter:** `032-2026-05-10-taxed-underlying-riskon-variants`
**Primary citation:** `[leverage_for_the_long_run, ch.4-5, p.40-60]`

## TL;DR

This report compares tax-aware T3d-K2 baseline and iter 30 proxy against three
requested variants: always-TQQQ risk-on, SPY/SSO risk-on, and SPY/UPRO risk-on.
Dynamic variants pay annual 15% tax on realized net gains; SPY and NDX/QQQ
buy-and-hold benchmarks are static and have no interim tax events.

## Metrics

| Config | CAGR | Sortino | MDD | End equity vs taxed T3d-K2 |
|---|---:|---:|---:|---:|
| `t3d_k2_tqqq_taxed` | 27.88% | 1.0279 | -70.74% | 3.194x |
| `iter30_proxy_taxed` | 25.05% | 1.0966 | -59.29% | 1.299x |
| `t3d_k2_taxed` | 24.24% | 1.0826 | -59.43% | 1.000x |
| `NDX/QQQ buyhold` | 14.59% | 0.9429 | -82.97% | 0.038x |
| `t3d_k2_spy_sso_taxed` | 13.12% | 0.7556 | -70.19% | 0.023x |
| `t3d_k2_spy_upro_taxed` | 13.08% | 0.6965 | -86.06% | 0.023x |
| `SPY buyhold` | 11.47% | 0.9571 | -55.14% | 0.013x |

## Tax Summary

| Config | Tax paid on $10k scale | Tax years paid | Sale events |
|---|---:|---:|---:|
| `t3d_k2_taxed` | $11331694.62 | 31 | 366 |
| `t3d_k2_tqqq_taxed` | $37766593.55 | 25 | 366 |
| `t3d_k2_spy_sso_taxed` | $252130.78 | 15 | 250 |
| `t3d_k2_spy_upro_taxed` | $248495.29 | 11 | 250 |

## Rolling Win Rates vs Taxed T3d-K2

| Config | 1y | 3y | 5y | 10y |
|---|---:|---:|---:|---:|
| `iter30_proxy_taxed` | 57.77% | 60.38% | 67.34% | 60.22% |
| `t3d_k2_spy_sso_taxed` | 39.46% | 22.40% | 18.68% | 15.63% |
| `t3d_k2_spy_upro_taxed` | 44.14% | 35.65% | 36.39% | 25.68% |
| `t3d_k2_taxed` | 0.00% | 0.00% | 0.00% | 0.00% |
| `t3d_k2_tqqq_taxed` | 55.70% | 68.91% | 66.72% | 77.37% |

## Plots

- ![Equity curves](plots/01_equity_curves.png)
- ![Relative vs SPY](plots/02_relative_vs_spy_buyhold.png)
- ![Relative vs NDX](plots/02_relative_vs_ndx_qqq_buyhold.png)
- ![Relative vs taxed T3d](plots/02_relative_vs_taxed_t3d-k2.png)
- ![Rolling vs taxed T3d](plots/03_rolling_winrate_vs_taxed_t3d-k2.png)
- ![Rolling vs SPY](plots/03_rolling_winrate_vs_spy_buyhold.png)
- ![Rolling vs NDX](plots/03_rolling_winrate_vs_ndx_qqq_buyhold.png)

## Tables

- `tables/metrics_summary.csv`
- `tables/tax_summary.csv`
- `tables/rolling_window_stats.csv`

## Caveat

These are tax-aware research diagnostics, not deployment authorization. Mandate
§1 remains 100% Plano C.
