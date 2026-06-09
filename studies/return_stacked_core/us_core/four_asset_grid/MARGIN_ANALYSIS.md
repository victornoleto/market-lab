# Margin Leverage Analysis

Status: research-only diagnostic. No deployment, paper-trade label or mandate change.

## Summary

The canonical four-asset grid was rerun with the corrected financing leg
`CASHX?E=-2`. The previous `CASHX?E=2` margin numbers are invalid/stale because they
used the wrong financing sign.

Under the corrected grid, the top row is `40% GDESIM / 25% RSST70_30 / 35% ZROZSIM`.
External margin is much less attractive than in the stale run: `1.25x` reaches only
CAGR `13.97%` with MDD `-34.14%`, while `1.50x` reaches CAGR `15.66%` with MDD
`-40.18%`. `2.00x+` quickly moves into liquidation/ruin territory and remains an
upper-bound diagnostic only `[systematic_trading, p.185-188]`,
`[leverage_for_the_long_run, p.4-7]`.

## Corrected Leverage Sweep

Exact scaling uses the corrected top grid row:

`SPYSIM = 25L`, `DBMFSIM = 17.5L`, `KMLMSIM = 7.5L`, `GDESIM = 40L`,
`ZROZSIM = 35L`, `CASHX?E=-2 = 100 - 125L`.

The sweep is a Testfol.io monthly-rebalanced account-level diagnostic. Sharpe and
related ratios are Testfol.io stats, so they are directionally comparable to the
grid but not identical to the local rank-grid metrics.

| External leverage | CAGR | MDD | Vol | Sharpe | Sortino | Calmar | Terminal |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.00x | 12.17% | -27.66% | 14.73% | 0.725 | 1.038 | 0.440 | 20.80x |
| 1.10x | 12.90% | -30.30% | 16.22% | 0.713 | 1.021 | 0.426 | 24.71x |
| 1.20x | 13.62% | -32.88% | 17.71% | 0.703 | 1.007 | 0.414 | 29.20x |
| 1.25x | 13.97% | -34.14% | 18.46% | 0.699 | 1.000 | 0.409 | 31.69x |
| 1.30x | 14.32% | -35.38% | 19.21% | 0.695 | 0.995 | 0.405 | 34.34x |
| 1.40x | 15.00% | -37.82% | 20.71% | 0.687 | 0.985 | 0.397 | 40.18x |
| 1.50x | 15.66% | -40.18% | 22.22% | 0.681 | 0.976 | 0.390 | 46.76x |
| 1.75x | 17.23% | -45.96% | 26.00% | 0.669 | 0.960 | 0.375 | 66.84x |
| 2.00x | 18.69% | -51.98% | 29.83% | 0.661 | 0.948 | 0.360 | 92.51x |
| 2.25x | 20.01% | -57.51% | 33.70% | 0.654 | 0.940 | 0.348 | 123.96x |
| 2.50x | 21.19% | -62.58% | 37.63% | 0.649 | 0.935 | 0.339 | 160.75x |
| 3.00x | 23.13% | -71.40% | 45.69% | 0.643 | 0.929 | 0.324 | 244.52x |

## Margin-Call Cushion

Approximate liquidation cushion for an external leverage `L`, assuming a fixed
maintenance margin `m`, is:

`portfolio_drop_to_call = (1 - mL) / (L * (1 - m))`.

This is an approximation; IBKR house requirements vary by product, concentration,
portfolio margin eligibility, volatility and account type. GDE/RSST/ZROZ may not all
receive plain vanilla ETF treatment, so actual thresholds can be worse.

| External leverage | Call if maintenance 25% | Call if maintenance 30% | Call if maintenance 50% |
|---:|---:|---:|---:|
| 1.25x | -73.33% | -71.43% | -60.00% |
| 1.50x | -55.56% | -52.38% | -33.33% |
| 1.75x | -42.86% | -38.78% | -14.29% |
| 2.00x | -33.33% | -28.57% | ~0.00% |
| 2.25x | -25.93% | -20.63% | ~0.00% |
| 2.50x | -20.00% | -14.29% | ~0.00% |
| 3.00x | -11.11% | -4.76% | ~0.00% |

Reading:

- `1.10x` to `1.25x` is the only plausible research band after the corrected run;
  even `1.25x` already pushes historical MDD to `-34.14%`.
- `1.50x` is no longer a clean practical bound: the backtest MDD is `-40.18%`, and
  under 50% maintenance the approximate call threshold is only `-33.33%`.
- `1.75x` has MDD `-45.96%`; if maintenance is punitive, the historical path would
  already be near or through plausible liquidation thresholds.
- `2.00x+` is backtest-only. At `2.00x`, historical MDD is `-51.98%`, and the 30%
  maintenance call threshold is only about `-28.57%` on the underlying portfolio.
- `3.00x` is not operationally credible for this sleeve stack: historical MDD is
  `-71.40%`, before taxes, real financing, forced-liquidation mechanics or stress
  gaps `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Practical Verdict

Margin remains technically possible, but the corrected data removes the attractive
headline. If this line is revisited, the next research sweep should focus only on
`1.10x..1.25x` with real IBKR maintenance, financing rates, liquidation logic,
tax/friction and mandate-style validation gates. `1.50x+` should be treated as
diagnostic stress, not an implementation plan.

Artifacts:

- Payloads: `raw/testfolio_margin_e_minus_2_payloads.json`.
- Responses: `raw/testfolio_margin_e_minus_2_responses.json`.
- Table: `results/margin_sweep_e_minus_2.csv`.
