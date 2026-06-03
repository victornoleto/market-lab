# B4-v2 Discovery Lineage

Status: canonical consolidation of the former `static_spy_beater_portfolio/`
study into `b4-v2/`. This file preserves the discovery knowledge that produced
the `35% GDE / 40% RSST / 25% ZROZ` core. It does not authorize deployment,
paper trading, or any mandate change.

## Why This Exists

`static_spy_beater_portfolio/` and `b4-v2/` ended up documenting the same
strategy from different angles:

- `static_spy_beater_portfolio/` was the discovery/optimizer workbench that found
  and stress-compared the no-margin `35/40/25` core.
- `b4-v2/` was the robustness/publication package for that same core.

The canonical study is now `studies/b4-v2/`. The old static study path is kept
only as a redirect stub so prior references remain understandable.

## Discovery Objective

The original mission was to find robust static, long-only, monthly rebalanced ETF
portfolios that beat `SPYSIM` and later the internal B4-style core by rolling
equity dominance. Optimization was explicitly discovery-only; promotion would
require separate validation and multiple-testing controls `[advances_fin_ml,
p.208-211]`, `[advances_fin_ml, p.222-223]`.

Portfolio rules:

| Rule | Value |
|---|---|
| Rebalance | Monthly |
| Weights | Long-only, 5% units, sum to 100% |
| External margin | Not allowed |
| Embedded leverage | Allowed only through explicit synthetic/Testfol.io series |
| Primary late objective | Rolling equity dominance versus the `35/40/25` core |

Main rolling horizons: `1/3/5/10/15/20y`, with heavier emphasis on `10/15/20y`.
The p10 component intentionally penalized candidates with attractive averages but
bad adverse-window behavior `[testing_tuning, p.327-335]`.

## Final Discovery Winner

```text
35% GDESIM / 40% RSSTSIM / 25% ZROZSIM
```

Effective exposure per $1 portfolio:

| Exposure family | Approx. notional |
|---|---:|
| US large equity | `0.715` |
| Managed futures | `0.400` |
| Gold | `0.315` |
| Zero-coupon Treasury | `0.250` |
| Embedded cash/financing | `-0.680` |

The portfolio itself is long-only with gross fund weight `1.0`; the leverage is
embedded inside capital-efficient ETF simulations, not external negative cash
`[leverage_for_the_long_run, p.13]`.

## Main Exact Metrics

Common exact window: `1988-01-04..2026-04-17`.

| Portfolio | CAGR | MDD | Sharpe | Sortino | Calmar | Terminal wealth |
|---|---:|---:|---:|---:|---:|---:|
| `35/40/25` core | `15.70%` | `-29.94%` | `1.040` | `1.484` | `0.524` | `265x` |
| B4 original | `14.43%` | `-27.92%` | `1.018` | `1.449` | `0.517` | `174x` |
| B4-like stacked reference | `13.75%` | `-28.42%` | `0.981` | `1.400` | `0.484` | `139x` |
| SPYSIM buy-hold | `11.46%` | `-55.14%` | `0.691` | `0.884` | `0.208` | `64x` |
| GA robust lead | `16.81%` | `-41.20%` | `0.972` | `1.338` | `0.408` | `383x` |
| GA aggressive lead | `17.97%` | `-49.37%` | `0.972` | `1.351` | `0.364` | `558x` |

Interpretation:

- Versus B4 original, the core adds `+1.27pp` CAGR and higher terminal wealth
  with only `~2.02pp` worse full-period MDD.
- Versus SPY, the core adds `+4.24pp` CAGR, cuts full-period MDD by `~25.20pp`,
  and raises Calmar from `0.208` to `0.524`.
- GA robust/aggressive variants raise terminal wealth, but their MDD cost is too
  high and Calmar is worse.

## Rolling Behavior Versus SPY

| Horizon | CAGR p10 | CAGR median | MDD p10 | Relative wealth p10 vs SPY | Relative wealth median vs SPY | Latest relative wealth vs SPY |
|---|---:|---:|---:|---:|---:|---:|
| 3y | `6.42%` | `14.28%` | `-28.02%` | `-9.84%` | `+10.97%` | `-0.07%` |
| 5y | `8.71%` | `14.55%` | `-29.89%` | `-8.59%` | `+17.97%` | `+8.72%` |
| 10y | `11.49%` | `14.42%` | `-29.94%` | `-4.25%` | `+60.20%` | `-5.99%` |
| 15y | `12.37%` | `14.46%` | `-29.94%` | `+12.88%` | `+109.54%` | `+7.24%` |

This is not a flawless short-window dominator. Its strength is long-horizon
compounding with materially shallower full-period drawdown. The 15y p10 relative
wealth is positive, while 3y/5y/10y p10 rows can still lag SPY.

## Named Regime Diagnostics

| Regime | Core terminal wealth | Core MDD | Wealth vs SPY |
|---|---:|---:|---:|
| Dot-com drawdown | `0.812x` | `-29.94%` | `1.53x` |
| GFC drawdown | `0.870x` | `-28.02%` | `1.92x` |
| QE bull | `3.699x` | `-14.61%` | `1.04x` |
| Covid crash | `0.832x` | `-20.00%` | `1.25x` |
| Inflation/rates shock | `0.822x` | `-21.46%` | `1.05x` |
| Recent recovery | `1.999x` | `-14.41%` | `1.03x` |

The core beat SPY wealth in every named regime in the exact Pareto/regime report.
It also beat B4 original in GFC, inflation shock and recent recovery. B4 original
was slightly better in dot-com, QE bull and Covid crash.

## Search Path And Rejections

### Early Aggressive Barbell

The first broad GA sweep converged to high-CAGR LETF/duration barbells:

| Universe | Lead | CAGR | MDD | Terminal |
|---|---|---:|---:|---:|
| `core_1986` | `40% TQQQSIM / 60% TMFSIM` | `20.66%` | `-84.28%` | `1611x` |
| `mf_1988` | `35% TQQQSIM / 50% TMFSIM / 15% RSSTSIM` | `22.10%` | `-81.21%` | `2083x` |

These were economically interesting but rejected as practical/promotional leads
because drawdowns were extreme.

### No-TMF Consistency Guard Lead

`35% GDESIM / 50% RSSTSIM / 5% TQQQSIM / 10% ZROZSIM` reached CAGR `17.97%`,
MDD `-49.37%`, Sharpe `0.972`, Sortino `1.351`, Calmar `0.364`, terminal wealth
`558x`. It beat SPY in later 10y/15y diagnostics, but rolling MDD p10 remained
slightly worse than SPY and the drawdown trade-off was unattractive.

### Negative-Cash Stacked Candidate

The local B4-like search found a higher-return stacked point:

```text
35% GDESIM / 40% RSSTSIM / 5% SPYSIM / 45% ZROZSIM / -25% CASHX
```

Metrics: CAGR `17.35%`, MDD `-30.44%`, Calmar `0.570`, terminal wealth `456x`.
It was rejected because negative external cash/margin was not operationally
allowed.

### Levered-Equity Challengers

Small `QLDSIM`/`TQQQSIM` boosters repeatedly appeared, but did not beat the core
objective:

| Challenger | CAGR | MDD | Calmar |
|---|---:|---:|---:|
| `35 GDE / 40 RSST / 20 ZROZ / 5 QLD` | `16.56%` | `-40.04%` | `0.414` |
| `35 GDE / 35 RSST / 25 ZROZ / 5 TQQQ` | `16.52%` | `-41.96%` | `0.394` |
| `35 GDE / 45 RSST / 20 ZROZ` | `16.21%` | `-32.97%` | `0.492` |

They bought too little return for too much extra drawdown.

### Factor, Momentum And Stacked-ETF Probes

The factor/momentum probe added `VBRSIM`, `MTUMSIM` and `EFVSIM`; all three seeds
selected the original `35/40/25` core as exact rank 1 over the `1994-2026` common
window. `VBRSIM` appeared only in lower-ranked candidates and `MTUMSIM` did not
enter top-10 exact rows `[ml_for_algo_trading, ch.4 p.82-93]`.

The stacked-ETF expansion triage tested 3 seeds, 21 tickers and 8 local proxies
(`CTAP/RSBT/RSIT/HOLD/MATE/ESBG/GDT/ALLW` plus Testfol.io-style products). The
core survived: core fitness `0.3500` versus GA best `0.2681`. No alternative
stacked/international/alpha sleeve entered any seed's top-5.

## Implementation Risks Carried Forward

- Testfol.io histories are simulated proxies for long pre-inception periods.
- `GDESIM` and `RSSTSIM` are capital-efficient/stacked products; ETF tracking,
  financing, taxes, fund survival and manager risk matter.
- BR investor implementation needs broker access, tax handling and product
  availability review.
- Monthly rebalance still needs exact sensitivity against quarterly/yearly
  schedules.
- Formal validation gates were not run because the discovery work selected an
  internal static benchmark, not a deployable strategy `[advances_fin_ml,
  p.208-211]`.

## Consolidation Result

The discovery verdict is now part of `b4-v2/`:

- `B4_V2_STRATEGY.md` is the canonical strategy description.
- `ROBUSTNESS_REPORT.md` is the robustness/publication execution report.
- `CLOSING_SUMMARY.md` is the closed-state summary.
- This file preserves the optimizer lineage and rejected alternatives.

The old broad GA/result scripts were intentionally removed from the active tree.
They can be recovered from git history if a future pre-registered search needs to
restart the broad static optimizer, but broad optimization should not continue
without a new hypothesis `[testing_tuning, p.327-335]`.
