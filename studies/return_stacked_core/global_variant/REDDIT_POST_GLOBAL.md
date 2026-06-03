# A global version of the B4-v2 return-stacked portfolio

This is a follow-up to my B4-v2 work. The original version was:

```text
35% GDE / 40% RSST / 25% ZROZ
```

That portfolio is very U.S.-centric. I wanted to see whether the same idea can be made more global without losing the core structure: equity stacking, managed futures, gold and long-duration Treasuries.

The benchmarks here are:

```text
100% VT
66% VTI / 34% VEA
```

I include the `66/34 VTI/VEA` benchmark because this version mostly targets U.S. + developed international equities and mostly ignores EM.

The charts are embedded inline below in the same order I would upload them to a Reddit gallery.

## ETFs/proxies I considered

The most useful global stacked sleeves were:

- `NTSD`: roughly `90% SPY + 60% developed ex-US equity`.
- `RSIT`: roughly `100% international equities + 100% managed futures`.
- `NTSI`: roughly `90% developed ex-US equity + 60% Treasuries`.
- `NTSG`: roughly `90% global equities + 60% Treasuries`.
- `RSSB`: roughly `100% VT + 100% Treasuries`.

I also checked broader stacked/all-weather candidates like `ESBG`, `ALLW`, `GDT`, and `RSBT`. They are interesting, but they did not map as cleanly to the goal of globalizing the B4-v2 equity exposure.

## Main candidates

Common window: `1988-01-04..2026-05-21`.

| Portfolio               | CAGR   | MDD     |   Sharpe |   Calmar | Terminal   | US share   | Intl share   |
|:------------------------|:-------|:--------|---------:|---------:|:-----------|:-----------|:-------------|
| 100% VT                 | 8.77%  | -58.35% |    0.562 |    0.15  | 25.2x      | 60.00%     | 40.00%       |
| 66/34 VTI/VEA           | 9.88%  | -56.92% |    0.635 |    0.174 | 37.1x      | 66.00%     | 34.00%       |
| US B4-v2 35/40/25       | 14.30% | -31.66% |    0.96  |    0.452 | 168.7x     | 100.00%    | 0.00%        |
| Global simple NTSD/RSIT | 13.10% | -34.35% |    0.894 |    0.381 | 112.5x     | 63.98%     | 36.02%       |
| Global 60/40 lead       | 12.47% | -30.95% |    0.904 |    0.403 | 90.7x      | 55.94%     | 44.06%       |
| Global 66/34 lead       | 12.93% | -30.54% |    0.924 |    0.423 | 106.3x     | 66.43%     | 33.57%       |

Approximate effective exposure by candidate:

| Portfolio | US equity | Intl equity | Total equity | MF | Gold | Intermediate Treasuries | ZROZ | Positive exposure | Gross leverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| US B4-v2 35/40/25 | 71.5% | 0.0% | 71.5% | 40.0% | 31.5% | 0.0% | 25.0% | 168.0% | 1.68x |
| Global simple NTSD/RSIT | 51.5% | 29.0% | 80.5% | 40.0% | 18.0% | 0.0% | 25.0% | 163.5% | 1.64x |
| Global 66/34 lead | 47.5% | 24.0% | 71.5% | 40.0% | 22.5% | 6.0% | 25.0% | 165.0% | 1.65x |
| Global 60/40 lead | 40.0% | 31.5% | 71.5% | 40.0% | 18.0% | 9.0% | 25.0% | 163.5% | 1.64x |

This is why I separate `US share` from absolute exposure. For example, the simple NTSD/RSIT version is about `64% US / 36% international` as a share of equity, but its total equity exposure is about `80.5%` because the stacked funds also hold managed futures, gold and duration.


Chart 1 shows the main equity-curve comparison. The point is not that the global version beats the U.S.-only B4-v2; it does not. The point is whether it keeps the same return-stacked profile while adding international equity exposure.

![Global equity curves vs VT and 66/34 VTI/VEA](plots/01_global_equity_log.png)

Chart 2 compares the global candidates to the `66/34 VTI/VEA` benchmark, which is the cleaner benchmark for a U.S. + developed ex-U.S. portfolio.

![Global relative wealth vs 66/34 VTI/VEA](plots/02_global_equity_vs_66_34.png)

Chart 3 repeats the relative-wealth view versus `100% VT`.

![Global relative wealth vs VT](plots/03_global_equity_vs_vt.png)

Chart 4 shows drawdowns. This is where the global variants need to prove they did not simply globalize the portfolio by accepting SPY-like drawdown.

![Global drawdowns](plots/04_global_drawdowns.png)

## My preferred global version

The cleanest version I found is:

```text
20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ
```

Approximate equity split:

```text
~64% US / ~36% international
```

Why I like this one:

- `GDE` keeps the U.S. equity + gold stack.
- `NTSD` adds developed-market equity exposure without turning the portfolio into a pure international bet.
- `RSST + RSIT` keeps the managed-futures sleeve at 40%, but splits the equity wrapper between U.S. and international markets.
- `ZROZ` keeps the long-duration convexity sleeve.

Chart 5 is the rolling check versus `66/34 VTI/VEA`. I would read this as a robustness diagnostic, not as proof of an optimized global allocation.

![Global rolling relative wealth 3/5/10/15](plots/05_global_rolling_relative_wealth_2x2.png)

A more `66/33` version is:

```text
25% GDE / 10% NTSI / 25% RSST / 15% RSIT / 25% ZROZ
```

That one lands closer to the `66/34 VTI/VEA` benchmark split, but I think the `NTSD + RSIT` version is more intuitive.

## Monte Carlo Sequence-Risk Simulation

I also ran the same Monte Carlo sequence-risk simulation on the global candidates.

Method: 1,000 simulated 20-year paths using 21-trading-day block bootstrap. Returns were resampled in paired daily blocks across the benchmark and candidates.

| Portfolio | p10 terminal | median terminal | p10 CAGR | median MDD | Prob. terminal < 66/34 |
|---|---:|---:|---:|---:|---:|
| 66/34 VTI/VEA | 2.59x | 6.68x | 4.87% | -37.61% | — |
| Global simple NTSD/RSIT | 5.26x | 11.59x | 8.65% | -27.82% | 11.3% |
| Global 66/34 lead | 5.36x | 11.21x | 8.76% | -26.11% | 14.7% |
| Global 60/40 lead | 4.92x | 10.40x | 8.29% | -26.39% | 17.8% |
| US B4-v2 35/40/25 | 6.68x | 14.45x | 9.96% | -25.73% | 7.8% |

Chart 6 shows the Monte Carlo median paths, with 10th-90th percentile bands.

![Global Monte Carlo 20-year sequence-risk simulation](plots/06_global_monte_carlo_20y_sequence_risk.png)

The global versions still trail the U.S.-only B4-v2 in simulated terminal wealth, but they keep much better drawdown behavior than the `66/34 VTI/VEA` benchmark while adding international exposure. This remains a sequence-risk diagnostic, not a validated optimizer result `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

## Caveats

- This is not financial advice.
- Several sleeves are simulated from prospectus-level exposures, not live ETF histories.
- `RSIT` is proxied with international equities + KMLM-style managed futures to preserve long history.
- `GOVT` exposure is approximated with intermediate Treasuries.
- The result is not a validated optimum. It is a plausible globalized implementation of the B4-v2 idea.

Question: if you were globalizing the original `35 GDE / 40 RSST / 25 ZROZ`, would you prefer the cleaner `NTSD + RSIT` version, or the more benchmark-ratio-pure `NTSI + RSIT` version?
