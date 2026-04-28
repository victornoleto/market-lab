# Final Report — Iter 010 HAA Volatility Throttle

## Verdict

**PROMISING — 60/100. Not a winner.**

The selected config was `vol12`: a 12% realized-volatility cap on the 85%
dynamic HAA sleeve, with unused dynamic allocation parked in `CASHX`.
It improved drawdown and slightly improved net Sharpe versus the local
`no_throttle` baseline, but it did not Pareto-advance iter 009 HAA+Gold and
failed the pre-committed kill: educational Sharpe improved only **+0.037**
versus baseline, below the required +0.05, and zero datasets beat iter 009 by
+0.10 Sharpe `[systematic_trading, p.137-148]`.

## Headline Metrics vs Iter 009

All candidate metrics are net of annual DARF via `AnnualDarfEngine`.

| dataset | candidate Sharpe | iter 009 Sharpe | Delta Sharpe | candidate CAGR | iter 009 CAGR | Delta CAGR | candidate MDD | iter 009 MDD | Delta MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| educational | 1.020 | 1.120 | -0.100 | 10.10% | 13.89% | -3.79pp | 14.86% | 20.81% | -5.95pp |
| vt_real | 0.955 | 1.061 | -0.106 | 9.19% | 12.87% | -3.68pp | 11.13% | 14.20% | -3.07pp |
| ndx_real | 0.881 | 0.954 | -0.073 | 8.23% | 10.55% | -2.32pp | 11.13% | 14.20% | -3.07pp |

## Score Breakdown

| criterion | points | note |
|---|---:|---|
| Sharpe edge | 0/25 | 0 datasets beat iter 009 by +0.10 |
| Gates | 25/25 | 7/7 educational, 7/7 vt_real, 7/7 ndx_real |
| DSR | 15/15 | worst p = 9.38e-03 with 4 configs tested `[advances_fin_ml, p.222-223]` |
| CAGR floor | 0/15 | all datasets fell below 0.8 x iter 009 |
| MDD ceiling | 15/15 | all datasets stayed inside iter 009 MDD + 5pp |
| Robustness bonus | 5/5 | 26/26 educational rolling 5y Sharpe windows positive |

## Gates

| dataset | gates | PBO | DSR p | G3 max WF MDD | G6 CI low | G7 np CAGR |
|---|---:|---:|---:|---:|---:|---:|
| educational | 7/7 | 0.032 | 3.67e-06 | 14.86% | 0.5536 | 11.47% |
| vt_real | 7/7 | 0.286 | 2.34e-03 | 11.13% | 0.3472 | 10.28% |
| ndx_real | 7/7 | 0.405 | 9.38e-03 | 11.13% | 0.2373 | 9.28% |

## Configs Tested

| config | rule | edu S/C/MDD | vt S/C/MDD | ndx S/C/MDD |
|---|---|---:|---:|---:|
| `no_throttle` | original HAA+Gold weights | 0.983 / 12.15% / 20.81% | 0.954 / 11.49% / 14.20% | 0.860 / 9.44% / 14.20% |
| `vol12` | cap dynamic sleeve at 12% trailing 63d vol | 1.020 / 10.10% / 14.86% | 0.955 / 9.19% / 11.13% | 0.881 / 8.23% / 11.13% |
| `vol15` | cap dynamic sleeve at 15% trailing 63d vol | 0.993 / 10.91% / 17.23% | 0.926 / 9.96% / 13.83% | 0.842 / 8.67% / 13.83% |
| `vol18` | cap dynamic sleeve at 18% trailing 63d vol | 0.984 / 11.37% / 20.08% | 0.929 / 10.56% / 14.20% | 0.842 / 8.99% / 14.20% |

Selection rule: maximum mean Sharpe divided by iter 009 Sharpe across
`educational`, `vt_real`, and `ndx_real`.

## What Worked

The volatility throttle did exactly what a risk-control overlay should do:
`vol12` cut educational MDD from **20.81%** to **14.86%** and real-window MDD
from **14.20%** to **11.13%**, while passing PBO, DSR, walk-forward, OOS,
forward, bootstrap, and cross-lib gates on all three datasets
`[advances_fin_ml, p.208-211, p.196-202, p.31-34]`.

## What Did Not Work

Scaling down risk-on exposure also scaled down the return engine. The selected
config failed the CAGR floor on all datasets and remained below iter 009 Sharpe
on all datasets. The modest Sharpe gain versus local baseline came from lower
volatility, not enough incremental return to close the bestfolio gap
`[systematic_trading, p.196-197]`.

## Lesson

A simple HAA dynamic-sleeve volatility throttle is a drawdown-control tool, not
a Sharpe-frontier advance in this universe. It may be useful for a capital
preservation objective, but it is structurally subordinate for the current
mission because it sacrifices too much CAGR.

## Citations

- Volatility-standardized sizing: `[systematic_trading, p.137-148]`.
- Volatility lookback for asset allocation: `[systematic_trading, p.196-197]`.
- HAA monthly momentum shell: `[stocks_on_the_move, ch.6]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Next Directions

1. Add real VT/VXUS data and re-check whether the current `VTSIM` proxy is
   obscuring real-data behavior before further HAA timing variants.
2. Stop the active Sharpe-frontier hunt unless a non-price regime input is
   introduced with literature support.
3. If objective changes to drawdown minimization, revisit `vol12` as a
   capital-preservation overlay rather than a winner candidate.
