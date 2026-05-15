# SPEC - static_spy_beater_portfolio

## Mission

Find robust static monthly-rebalanced ETF portfolios that beat `SPYSIM` buy-and-hold
across full-period and rolling-window diagnostics. This is discovery research only;
it does not authorize capital allocation and does not override the project mandate.

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

## Fitness Families

- `cagr_robust`.
- `sharpe_robust`.
- `sortino_robust`.
- `calmar_robust`.
- `relative_wealth_spy`.
- `relative_wealth_qqq`.
- `balanced_spy_beater`.
- `balanced_dual_beater`.
- `min_regret`.

Terminal wealth is reported, but it is not a separate absolute fitness because it
is monotonic with CAGR over a fixed date range. Relative wealth versus `SPYSIM` and
`QQQSIM` is an explicit fitness input.

## Benchmarks

- `SPYSIM` buy-and-hold.
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
