# SPEC - static_spy_beater_portfolio

## Mission

Find robust static monthly-rebalanced ETF portfolios that beat the no-margin core
benchmark `35% GDESIM / 40% RSSTSIM / 25% ZROZSIM` across rolling equity-dominance
diagnostics. `SPYSIM` buy-and-hold remains a public baseline, but the internal target
is now to improve the core by window-by-window relative wealth, not by minimizing MDD
alone. This is discovery research only; it does not authorize capital allocation and
does not override the project mandate.

The study uses a genetic algorithm because the discrete long-only portfolio search
space is combinatorially large once 5% weight increments and 18-25 assets are used.
Optimization remains a discovery tool; promotion requires separate validation and
multiple-testing controls `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Portfolio Rules

- Monthly rebalance.
- Long-only.
- Weights are multiples of 5%.
- Weights sum to 100%.
- Portfolios may hold 1-20 assets.
- External margin and shorting are not allowed; embedded ETF leverage is allowed when
  represented by an explicit synthetic or testfol.io series.
- Effective exposure by economic family must be reported, because stacked and LETF
  products can hide large notional exposure `[risk_parity, ch.5, p.10]`,
  `[leverage_for_the_long_run, p.13]`.

## Universes

### `core_1986`

`SPYSIM`, `SSOSIM`, `UPROSIM`, `QQQSIM`, `QLDSIM`, `TQQQSIM`, `TLTSIM`, `TMFSIM`,
`ZROZSIM`, `GLDSIM`, `GDESIM`, `NTSXSIM`, `RSSBSIM`, `IEFSIM`, `BNDSIM`, `CASHX`,
`VTISIM`, `VTSIM`, `UGLSIM`.

### `mf_1988`

`core_1986` plus `KMLMSIM`, `RSSTSIM`.

### `global_1994`

`mf_1988` plus `NTSESIM`, `VEASIM`, `VWOSIM`, `VXUSSIM`, `EFVSIM`, `VBRSIM`.

### `full_2000`

`global_1994` plus `DBMFSIM`.

`CTAPSIM` and `RSSXSIM` are intentionally excluded until local cache coverage exists.

### Curated Universes

The original broad universes remain for reproducibility. Curated universes are added
for focused searches that reduce redundant broad-market noise while preserving the
1x/2x/3x leverage ladders. Keeping `SPYSIM/SSOSIM/UPROSIM` and
`QQQSIM/QLDSIM/TQQQSIM` allows the optimizer to synthesize intermediate leverage via
weights, rather than forcing a single discrete ETF leverage level
`[leverage_for_the_long_run, p.13]`.

- `minimal_aggressive`: US equity leverage ladders, duration ladder (`TLTSIM`,
  `ZROZSIM`, `TMFSIM`), gold/GDE, managed futures (`KMLMSIM`, `DBMFSIM`, `RSSTSIM`)
  and `CASHX`.
- `levered_hedge_core`: focused testbed for the leveraged-equity-plus-hedge thesis:
  US/Nasdaq 1x/2x/3x ladders, duration ladder, gold/2x gold, `GDESIM`, `RSSTSIM`
  and `CASHX`.
- `levered_hedge_no_tmf`: same hypothesis without `TMFSIM`, for testing whether
  duration protection must survive using `TLTSIM`/`ZROZSIM` rather than 3x Treasury.
- `lead_family_focused`: focused refinement universe around the current no-TMF lead
  family (`GDESIM`, `RSSTSIM`, `ZROZSIM`, gold, Nasdaq booster, cash).
- `lead_family_no_3x_booster`: same focused universe without `TQQQSIM`, to test
  whether 2x Nasdaq exposure is enough for the return engine.
- `core_beater_no_margin`: focused no-margin search universe for beating the new core
  benchmark with `GDESIM`, `RSSTSIM`, `KMLMSIM`, `ZROZSIM`, US/Nasdaq equity leverage
  ladders, `IEFSIM`, and `CASHX`. `CASHX` is long-only cash; no negative cash or
  external margin is allowed, while embedded ETF leverage remains explicit and
  reported `[leverage_for_the_long_run, p.13]`, `[risk_parity, p.80-81]`.
- `balanced_no_3x`: excludes 3x equity/Treasury/gold products but keeps 1x/2x
  equity ladders, duration, gold/GDE, MF, NTSX/RSSB and cash.
- `stacked_core`: capital-efficient/stacked and diversifier products only:
  `NTSXSIM`, `GDESIM`, `RSSTSIM`, `RSSBSIM`, `ZROZSIM`, `KMLMSIM`, `DBMFSIM`,
  `CASHX`.
- `global_core`: global equity/factor set plus 1x/2x US equity ladders, duration,
  gold/GDE, managed futures and cash. `VTISIM` is intentionally omitted from curated
  universes because `SPYSIM` is the primary benchmark and US equity base.

`CASHX` is kept because it is a risk-free/cash sleeve, not equivalent to `BNDSIM`.
`BNDSIM` is omitted from curated universes because the focused duration set already
has `TLTSIM`, `ZROZSIM` and `TMFSIM`; aggregate bonds can be revisited in a
conservative-only universe if needed.

## Rolling Fitness

Each candidate is evaluated over the full aligned period and all possible rolling
windows for these horizons:

| horizon | score weight |
|---|---:|
| 1y | 2.5% |
| 3y | 7.5% |
| 5y | 15.0% |
| 10y | 25.0% |
| 15y | 25.0% |
| 20y | 25.0% |

For each horizon and metric, the rolling score is:

```text
window_score = 0.50 * mean(relative_metric_score)
             + 0.25 * median(relative_metric_score)
             + 0.25 * p10(relative_metric_score)
```

The `p10` term penalizes portfolios whose average is good but whose bad-regime
outcomes are weak `[testing_tuning, p.327-335]`.

Operationally, GA discovery may use monthly-sampled rolling starts (`rolling_step=21`)
to avoid wasting compute on weak candidates. The reported finalist table must then
re-rank the top sampled portfolios with exact rolling starts (`rolling_step=1`), so
final portfolio comparisons still use all possible windows.

GA runs may stop early when best fitness fails to improve by at least `min_delta`
for `patience` generations. This is an engineering stop rule only; it saves compute
after convergence and does not turn a discovery result into a validated winner.

The balanced fitness families must not be winnable by cash-like defensive
underperformance. Positive Sortino/Calmar credit is therefore muted unless the
portfolio is also positive on relative CAGR and relative wealth versus the target
benchmark; otherwise defensive metrics become diagnostics, not return substitutes.

`fast-discovery` mode may skip rolling MDD/Calmar during GA candidate search to
reduce runtime. This mode is only a search accelerator: reported finalists must be
re-ranked with exact rolling drawdown enabled (`finalist_exact`), and sampled GA
rankings from this mode must not be treated as final. Under `fast-discovery` the
skipped MDD/Calmar arrays are NaN (not zero); downstream weighting and the
balanced-beater guard treat NaN as "not contributing" so the discovery landscape
is not biased toward zero spreads.

The monthly rebalance engine is vectorized by month, and GA candidate scoring can
run with threaded `--jobs` for discovery speed. Parallelism is an engineering
acceleration only; it does not change validation requirements or trial accounting.

## Fitness Families

- `cagr_robust`.
- `sharpe_robust`.
- `sortino_robust`.
- `calmar_robust`.
- `relative_wealth_spy`.
- `relative_wealth_qqq`.
- `core_relative_wealth_dominance`.
- `balanced_spy_beater`.
- `spy_beater_mdd_guard`.
- `spy_beater_calmar_guard`.
- `spy_beater_consistency_guard`.
- `spy_beater_p10_mdd_guard`.
- `balanced_dual_beater`.
- `min_regret`.

Terminal wealth is reported, but it is not a separate absolute fitness because it
is monotonic with CAGR over a fixed date range. Relative wealth versus `SPYSIM` and
`QQQSIM` is an explicit fitness input; the current primary discovery fitness is
relative wealth and rolling win-rate versus the no-margin core.

`core_relative_wealth_dominance` treats MDD as a guardrail/penalty, not the primary
objective. It rewards rolling windows where candidate terminal wealth beats the
`35/40/25` core, especially 5y+ p10 relative wealth and aggregate win-rate, because a
portfolio that has higher equity than the benchmark in most windows is more useful
than one that only minimizes drawdown `[testing_tuning, p.327-335]`.

Only `balanced_spy_beater`, `spy_beater_mdd_guard`, `spy_beater_calmar_guard`,
`spy_beater_consistency_guard`, `spy_beater_p10_mdd_guard`, `balanced_dual_beater`,
`relative_wealth_spy`, `relative_wealth_qqq` and `min_regret` are CASHX-proof. The simple `*_robust` families (`cagr_robust`,
`sharpe_robust`, `sortino_robust`, `calmar_robust`) are raw clipped rolling-window
spreads versus `SPYSIM` and can be maximized by defensive/cash-like portfolios with
near-zero drawdown. When the GA is run with those families as the selector, the
resulting top is a defensive-bias trace, not a SPY-beater candidate
`[testing_tuning, p.327-335]`.

`spy_beater_mdd_guard` is the long-term efficient-beater objective: it rewards
rolling relative wealth/CAGR versus `SPYSIM`, but rejects portfolios whose
full-period MDD is worse than `SPYSIM` and penalizes rolling MDD worse than
`SPYSIM`. Use it when the question is "beat SPY without accepting a worse drawdown
profile" rather than maximum terminal wealth.

`spy_beater_calmar_guard` applies the same full-period MDD guard and also rejects
full-period CAGR below `SPYSIM`; among feasible candidates it ranks by rolling Calmar
spread, then relative CAGR and wealth.

`spy_beater_consistency_guard` keeps the same full-period guard, requires the latest
3y window to beat `SPYSIM`, and penalizes poor 10th-percentile rolling CAGR/wealth/MDD
across 3y+ horizons. This is designed to catch HFEA-like regime death that can be
hidden by strong early full-period history.

`spy_beater_p10_mdd_guard` is stricter: it rejects candidates whose 5y+ rolling p10
MDD spread versus `SPYSIM` is negative. This prioritizes window-independent drawdown
robustness over full-period terminal wealth.

## Benchmarks

- `SPYSIM` buy-and-hold.
- Core no-margin benchmark: 35% `GDESIM`, 40% `RSSTSIM`, 25% `ZROZSIM`.
- `QQQSIM` buy-and-hold.
- Equal-weight of the active universe.
- B4 reference when all required legs exist: 25% `NTSXSIM`, 25% `GDESIM`,
  25% `RSSTSIM`, 25% `ZROZSIM`.

## Guardrails

Hard blocks are intentionally limited to invalid data or invalid portfolio encoding.
Concentration and effective exposure are primarily scored and reported, not hidden.

- Required assets must exist locally; no post-hoc substitutions.
- A portfolio must have enough common data for the requested rolling horizon.
- Weights must be valid 5% units and sum to 100%.
- Report family concentration and effective exposure for every selected candidate.

## Outputs

- Universe audit tables.
- Top portfolios by fitness family.
- Full-period metrics.
- Rolling-window aggregate metrics.
- Pareto frontiers for CAGR/MDD, CAGR/Sharpe, CAGR/Calmar, relative wealth vs MDD,
  and long-window score vs short-window score.
- Explicit benchmark comparison against `SPYSIM`, `QQQSIM`, equal-weight, and B4 when
  available.
