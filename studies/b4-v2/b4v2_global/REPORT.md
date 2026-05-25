# B4-v2 Global Version Research

Status: discovery-only support for a potential Reddit follow-up. This is not a deployment recommendation.

## Objective

Build a more global version of the B4-v2 idea while preserving the core economic sleeves:

- capital-efficient equity exposure;
- managed futures;
- gold;
- long-duration Treasury convexity;
- no external margin.

Benchmarks:

- `100% VT` (`VTSIM`)
- `66/34 VTI/VEA` (`66% VTISIM / 34% VEASIM`), because the proposed global version mostly targets US + developed ex-US and largely ignores EM.

## Stacked ETFs/proxies considered

Primary useful sleeves:

- `NTSD`: proxied as `90% SPY + 60% VEA - 50% CASHX`.
- `NTSI`: proxied as `90% VEA + 60% IEF - 50% CASHX`.
- `NTSG`: proxied as `90% VT + 60% IEF - 50% CASHX`.
- `RSIT`: proxied as `100% VXUS + 100% KMLM - 100% CASHX`.
- `RSSB`: proxied as `100% VT + 100% IEF - 100% CASHX`.
- `ESBG`, `ALLW`, `GDT`, `RSBT`: tested as diversifier candidates, but not selected as primary global replacements.

Excluded from primary use: crypto stacks, oil/BTC stacks, miners, long/short thematic stacks, income variants, and strategy-specific short-history funds. They either do not solve the global-equity problem or require too many proprietary assumptions.

## Main Comparison

Common window: `1988-01-04..2026-05-21`.

| Portfolio               | CAGR   | MDD     |   Sharpe |   Calmar | Terminal   | US share   | Intl share   |
|:------------------------|:-------|:--------|---------:|---------:|:-----------|:-----------|:-------------|
| 100% VT                 | 8.77%  | -58.35% |    0.562 |    0.15  | 25.2x      | 60.00%     | 40.00%       |
| 66/34 VTI/VEA           | 9.88%  | -56.92% |    0.635 |    0.174 | 37.1x      | 66.00%     | 34.00%       |
| US B4-v2 35/40/25       | 14.30% | -31.66% |    0.96  |    0.452 | 168.7x     | 100.00%    | 0.00%        |
| Global simple NTSD/RSIT | 13.10% | -34.35% |    0.894 |    0.381 | 112.5x     | 63.98%     | 36.02%       |
| Global 60/40 lead       | 12.47% | -30.95% |    0.904 |    0.403 | 90.7x      | 55.94%     | 44.06%       |
| Global 66/34 lead       | 12.93% | -30.54% |    0.924 |    0.423 | 106.3x     | 66.43%     | 33.57%       |

## Approximate Effective Exposure

| Portfolio | US equity | Intl equity | Total equity | MF | Gold | Intermediate Treasuries | ZROZ | Positive exposure | Gross leverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| US B4-v2 35/40/25 | 71.5% | 0.0% | 71.5% | 40.0% | 31.5% | 0.0% | 25.0% | 168.0% | 1.68x |
| Global simple NTSD/RSIT | 51.5% | 29.0% | 80.5% | 40.0% | 18.0% | 0.0% | 25.0% | 163.5% | 1.64x |
| Global 66/34 lead | 47.5% | 24.0% | 71.5% | 40.0% | 22.5% | 6.0% | 25.0% | 165.0% | 1.65x |
| Global 60/40 lead | 40.0% | 31.5% | 71.5% | 40.0% | 18.0% | 9.0% | 25.0% | 163.5% | 1.64x |

## Candidate Read

The cleanest global candidate is:

```text
20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ
```

Approximate equity split is `~64% US / 36% international`, close to the requested 60/40 or 66/33 target. It preserves the original B4-v2 shape:

- GDE keeps the gold/equity stack;
- NTSD adds developed-market equity without creating a pure non-US sleeve;
- RSST/RSIT splits the managed-futures stack between US and international equity wrappers;
- ZROZ keeps the convex duration sleeve.

A slightly more benchmark-ratio-purist candidate is:

```text
25% GDE / 10% NTSI / 25% RSST / 15% RSIT / 25% ZROZ
```

This lands closer to `~67% US / 33% international`, but uses NTSI instead of NTSD. I prefer the NTSD/RSIT version narratively because it maps more directly to your requested `NTSD + RSIT` construction.

## Top Constrained Grid Rows

Grid constraints: 5% weights, max 6 active sleeves, `ZROZ 15%-30%`, `RSST+RSIT 30%-45%`, gold exposure `15%-35%`, equity US share `55%-72%`.

|   Rank |   Objective | CAGR   | MDD     |   Calmar | US share   | Weights                                                      |
|-------:|------------:|:-------|:--------|---------:|:-----------|:-------------------------------------------------------------|
|      1 |       0.648 | 12.90% | -27.94% |    0.462 | 68.15%     | 20 GDE / 5 NTSI / 15 RSIT_KMLM / 5 RSSB / 25 RSST / 30 ZROZ  |
|      2 |       0.645 | 12.83% | -27.91% |    0.459 | 68.21%     | 20 GDE / 5 NTSG / 5 NTSI / 15 RSIT_KMLM / 25 RSST / 30 ZROZ  |
|      3 |       0.643 | 12.72% | -27.84% |    0.457 | 64.18%     | 20 GDE / 10 NTSI / 15 RSIT_KMLM / 25 RSST / 30 ZROZ          |
|      4 |       0.641 | 12.72% | -27.64% |    0.46  | 68.66%     | 20 GDE / 10 NTSI / 10 RSIT_KMLM / 5 RSSB / 25 RSST / 30 ZROZ |
|      5 |       0.641 | 12.95% | -28.72% |    0.451 | 67.41%     | 25 GDE / 20 RSIT_KMLM / 5 RSSB / 20 RSST / 30 ZROZ           |
|      6 |       0.641 | 12.54% | -27.70% |    0.453 | 64.66%     | 20 GDE / 15 NTSI / 10 RSIT_KMLM / 25 RSST / 30 ZROZ          |
|      7 |       0.641 | 12.65% | -27.46% |    0.461 | 68.72%     | 20 GDE / 5 NTSG / 10 NTSI / 10 RSIT_KMLM / 25 RSST / 30 ZROZ |
|      8 |       0.641 | 12.88% | -28.54% |    0.451 | 67.46%     | 25 GDE / 5 NTSG / 20 RSIT_KMLM / 20 RSST / 30 ZROZ           |
|      9 |       0.64  | 13.08% | -29.11% |    0.449 | 67.65%     | 20 GDE / 20 RSIT_KMLM / 5 RSSB / 25 RSST / 30 ZROZ           |
|     10 |       0.639 | 12.67% | -28.21% |    0.449 | 64.78%     | 20 GDE / 10 NTSG / 20 RSIT_KMLM / 20 RSST / 30 ZROZ          |

## Plot Files

- `plots/01_global_equity_log.png`
- `plots/02_global_equity_vs_66_34.png`
- `plots/03_global_equity_vs_vt.png`
- `plots/04_global_drawdowns.png`
- `plots/05_global_rolling_relative_wealth_2x2.png`
- `plots/06_global_monte_carlo_20y_sequence_risk.png`

## Monte Carlo Sequence-Risk Simulation

Simulation design: 1,000 paired 20-year paths via 21-trading-day block bootstrap from daily returns. Benchmark is `66/34 VTI/VEA`. This is a path-ordering diagnostic, not a formal optimizer validation `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

| Portfolio | p10 terminal | median terminal | p10 CAGR | median MDD | Prob. terminal < 66/34 |
|---|---:|---:|---:|---:|---:|
| 66/34 VTI/VEA | 2.59x | 6.68x | 4.87% | -37.61% | — |
| Global simple NTSD/RSIT | 5.26x | 11.59x | 8.65% | -27.82% | 11.3% |
| Global 66/34 lead | 5.36x | 11.21x | 8.76% | -26.11% | 14.7% |
| Global 60/40 lead | 4.92x | 10.40x | 8.29% | -26.39% | 17.8% |
| US B4-v2 35/40/25 | 6.68x | 14.45x | 9.96% | -25.73% | 7.8% |

## Caveats

- `RSIT`, `NTSD`, `NTSI`, `NTSG`, `RSSB`, `ESBG`, `ALLW`, `GDT`, and `RSBT` are local prospectus-level proxies, not live ETF histories.
- `RSIT` uses `KMLMSIM` as the managed-futures proxy to preserve a 1988+ window. A DBMF version starts only in 2000.
- `GOVT` is approximated with `IEFSIM` because long synthetic GOVT history was not available.
- The optimizer/grid is discovery-only. Do not present the top grid row as a validated optimal portfolio.
- The global version gives up some US-only concentration but still depends on US-listed stacked ETF wrappers and U.S. Treasury duration.
