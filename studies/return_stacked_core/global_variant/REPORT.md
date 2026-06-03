# RSC-Global Version Research

Status: discovery-only support for a potential Reddit follow-up. This is not a deployment recommendation.

## Objective

Build a more global version of the Return-Stacked Core idea while preserving the core economic sleeves:

- capital-efficient equity exposure;
- managed futures;
- gold;
- long-duration Treasury convexity;
- no external margin.

Benchmarks:

- `100% VT` (`VTSIM`)
- `66/34 VTI/VEA` (`66% VTISIM / 34% VEASIM`), because the core proposed global version mostly targets US + developed ex-US and largely ignores EM. An explicit EM/AVEM variant is evaluated separately below.

## Stacked ETFs/proxies considered

Primary useful sleeves:

- `NTSD`: proxied as `90% SPY + 60% VEA - 50% CASHX`.
- `NTSI`: proxied as `90% VEA + 60% IEF - 50% CASHX`.
- `NTSG`: proxied as `90% VT + 60% IEF - 50% CASHX`.
- `RSIT`: proxied as `100% VXUS + 100% KMLM - 100% CASHX`.
- `RSSB`: proxied as `100% VT + 100% IEF - 100% CASHX`.
- `AVEM`: proxied as `VWOSIM + 125bps/year` factor-tilt premium. This is used only for the optional EM sleeve because it bottlenecks the common window at 1994 and uses an incomplete Avantis-style factor approximation `[ilmanen_expected_returns, ch.19]`, `[advances_fin_ml, p.31-34]`.
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

Approximate equity split is `~64% US / 36% international`, close to the requested 60/40 or 66/33 target. It preserves the original RSC-US shape:

- GDE keeps the gold/equity stack;
- NTSD adds developed-market equity without creating a pure non-US sleeve;
- RSST/RSIT splits the managed-futures stack between US and international equity wrappers;
- ZROZ keeps the convex duration sleeve.

A slightly more benchmark-ratio-purist candidate is:

```text
25% GDE / 10% NTSI / 25% RSST / 15% RSIT / 25% ZROZ
```

This lands closer to `~67% US / 33% international`, but uses NTSI instead of NTSD. The NTSD/RSIT version is the cleaner narrative fit because it maps more directly to the requested `NTSD + RSIT` construction.

## Decision Standard And Evolution

The chosen global mix is **not** claimed to be the mathematical optimum across
all static portfolios. It is the best current **RSC-Global expression** under the
preferred design constraints:

| Constraint | Reason |
|---|---|
| Keep the RSC structure | Preserve the four useful economic sleeves: equity, managed futures, gold and long-duration Treasury convexity `[risk_parity, p.80-81]`, `[leverage_for_the_long_run, p.13]`. |
| No external margin | Stacking must come from ETF/futures overlays, not portfolio-level negative cash. This avoids the operational fragility that disqualified earlier negative-cash candidates `[leverage_for_the_long_run, p.13]`. |
| Five clean sleeves | Prefer an implementable allocation over a six-sleeve grid artifact unless the extra sleeve gives a large robustness gain `[testing_tuning, p.327-335]`. |
| 5% weight granularity | Avoid false precision from proxy data and short live histories `[advances_fin_ml, p.208-211]`. |
| Target US/developed ex-US balance | Aim near `60/40` to `66/34` equity geography, because the global version is meant to reduce US-only concentration rather than maximize US-led CAGR. |

The evolution was:

| Step | Candidate family | Resulting read |
|---|---|---|
| Original global-factor study | Broad global factor/static mixes with RSSB, Avantis proxies, factor sleeves, gold and managed futures. | Useful but too broad and proxy-heavy; the strongest early static result was a global capital-efficient stack, not a clean RSC variant. |
| RSC-US discovery | `35% GDE / 40% RSST / 25% ZROZ`. | Became the reference shape: gold/equity stack, stock/MF stack and ZROZ. |
| Simple global RSC port | `20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ`. | Best clean expression: keeps MF total at `40%`, keeps ZROZ at `25%`, adds developed ex-US via both NTSD and RSIT, and lands near `64/36` US/international equity. |
| Constrained grid | Top objective rows often used `30% ZROZ`, small `NTSI`/`NTSG`, and sometimes `RSSB`. | Better Calmar/MDD in some rows, but less clean as an RSC implementation and more proxy-dependent. |
| Benchmark-ratio alternative | `25% GDE / 10% NTSI / 25% RSST / 15% RSIT / 25% ZROZ`. | Closer to `66/34`, but less direct to the `NTSD + RSIT` thesis and slightly lower terminal/CAGR than the simple NTSD/RSIT candidate. |

## Why `20 / 15 / 20 / 20 / 25`

| Sleeve | Weight | Why this level |
|---|---:|---|
| `GDE` | `20%` | Keeps a material US equity + gold stack while freeing `15pp` from the US-only RSC sleeve for global equity. At `20%`, gold exposure remains meaningful (`~18%`) without dominating the global branch. |
| `NTSD` | `15%` | Adds developed ex-US equity inside a capital-efficient sleeve while retaining some US equity, which keeps the total equity mix near the desired `60/40` to `66/34` zone. |
| `RSST` | `20%` | Keeps half of the managed-futures stack in the original US equity wrapper instead of replacing the RSC-US thesis entirely. |
| `RSIT` | `20%` | Mirrors RSST with international equity + managed futures, so total MF exposure stays at `40%` while international equity becomes structurally embedded. |
| `ZROZ` | `25%` | Preserves the original RSC duration-convexity sleeve and keeps the global branch comparable to RSC-US. Pure Calmar optimization sometimes prefers `30%`, but that becomes a more defensive variant. |

Effective result: `~51.5%` US equity, `~29.0%` international equity,
`40%` managed futures, `18%` gold and `25%` ZROZ. Among the manual global
candidates, this has the highest CAGR/terminal wealth (`13.10%`, `112.5x`) while
still cutting US-only concentration materially. The cost is higher MDD than the
`Global 66/34 lead` (`-34.35%` vs `-30.54%`) and lower absolute return than
RSC-US (`14.30%`, `168.7x`).

So the exact wording should be:

```text
Best current clean RSC-Global proportion: 20 GDE / 15 NTSD / 20 RSST / 20 RSIT / 25 ZROZ.
```

Not:

```text
Best possible static global portfolio under every objective.
```

If the objective changes, the preferred mix changes:

| Objective | Better candidate |
|---|---|
| Highest Calmar / lower drawdown in the constrained grid | Top grid rows with `30% ZROZ` and small `NTSI`/`RSSB` sleeves. |
| Closer `66/34` equity geography | `25% GDE / 10% NTSI / 25% RSST / 15% RSIT / 25% ZROZ`. |
| Maximum long-run CAGR regardless of US concentration | RSC-US remains ahead. |
| Cleanest global RSC implementation | `20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ`. |

## Optional EM Sleeve: AVEM 10-15%

The clean RSC-Global allocation intentionally targets US + developed ex-US. It has
little/no explicit emerging-markets exposure. If the objective includes policy EM
exposure, the cleanest add-on is `AVEM`, modeled here as `VWOSIM + 125bps/year`
to approximate Avantis EM value/profitability tilts. This proxy starts only in
1994, so all rows below use the common `1994-05-05..2026-05-21` window. Earlier
long-term portfolio tests found AVEM/EM additions Sharpe-subordinate in the
1994-2026 US-led regime; this section therefore evaluates AVEM as a diversification
choice, not as a backtest-improving optimizer sleeve `[ilmanen_expected_returns,
ch.19]`, `[testing_tuning, p.327-335]`.

First-pass funding rule: fund AVEM pro-rata from the existing clean RSC-Global
portfolio. This avoids declaring in advance whether EM should come specifically
from GDE, NTSD, RSST, RSIT or ZROZ. It also keeps the test simple and prevents a
second optimization layer on a short/proxy-limited EM window `[advances_fin_ml,
p.208-211]`.

| Portfolio | Weights | CAGR | MDD | Sharpe | Sortino | Calmar | Terminal |
|---|---|---:|---:|---:|---:|---:|---:|
| RSC-Global base, 1994+ | `20 GDE / 15 NTSD / 20 RSST / 20 RSIT / 25 ZROZ` | 12.99% | -34.35% | 0.895 | 1.258 | 0.378 | 50.0x |
| RSC-Global + 10% AVEM | `18 GDE / 13.5 NTSD / 18 RSST / 18 RSIT / 22.5 ZROZ / 10 AVEM` | 12.67% | -37.10% | 0.872 | 1.209 | 0.341 | 45.7x |
| RSC-Global + 15% AVEM | `17 GDE / 12.75 NTSD / 17 RSST / 17 RSIT / 21.25 ZROZ / 15 AVEM` | 12.49% | -38.72% | 0.855 | 1.179 | 0.323 | 43.4x |
| `66/34 VTI/VEA`, 1994+ | benchmark | 9.60% | -56.92% | 0.603 | 0.761 | 0.169 | 18.9x |
| `100% VT`, 1994+ | benchmark | 8.74% | -58.35% | 0.553 | 0.694 | 0.150 | 14.6x |

Read: adding AVEM improves geographic completeness but **does not improve** the
historical RSC-Global backtest. The degradation is monotonic from 0% to 10% to
15% AVEM in this proxy window: lower CAGR, lower Sharpe/Sortino/Calmar and worse
drawdown. If EM exposure is required anyway, `10% AVEM` is the more defensible
policy sleeve; `15%` should be treated as an upper bound rather than a preferred
allocation.

If preserving the original `25% ZROZ` sleeve is more important than pro-rata
funding, the implementation variant to test next is:

```text
20% GDE / 10% NTSD / 20% RSST / 15% RSIT / 25% ZROZ / 10% AVEM
```

and the 15% upper-bound version is:

```text
20% GDE / 7.5% NTSD / 20% RSST / 12.5% RSIT / 25% ZROZ / 15% AVEM
```

Those keep the duration sleeve fixed and fund EM only from developed-market global
wrappers, but they need an exact component-level rerun before being treated as
metric-equivalent to the pro-rata table above.

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
- `AVEM` is proxied as `VWOSIM + 125bps/year`; this is an incomplete factor-premium approximation and starts only in 1994, so EM rows are not directly comparable to the 1988+ base table.
- `RSIT` uses `KMLMSIM` as the managed-futures proxy to preserve a 1988+ window. A DBMF version starts only in 2000.
- `GOVT` is approximated with `IEFSIM` because long synthetic GOVT history was not available.
- The optimizer/grid is discovery-only. Do not present the top grid row as a validated optimal portfolio.
- The global version gives up some US-only concentration but still depends on US-listed stacked ETF wrappers and U.S. Treasury duration.
