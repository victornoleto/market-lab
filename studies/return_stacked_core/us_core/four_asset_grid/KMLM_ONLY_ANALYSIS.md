# KMLM-Only Managed-Futures Proxy Analysis

Status: research-only diagnostic. No deployment, paper-trade label or mandate change.

## Summary

This rerun replaces the corrected four-asset top row's `70% DBMF / 30% KMLM`
managed-futures sleeve with `100% KMLM`, while keeping the corrected financing sign
`CASHX?E=-2`. The earlier `CASHX?E=2` KMLM-only analysis is invalid/stale.

The KMLM-only proxy extends the Testfol.io window to `1987-12-31..2026-06-08` and
produces a solid unlevered profile: CAGR `13.00%`, MDD `-26.70%`, Calmar `0.487`.
It does not rescue the external-margin thesis: `1.25x` already reaches MDD
`-33.01%`, and `1.50x` reaches MDD `-38.92%`, with Sharpe/Calmar declining as
leverage rises `[systematic_trading, p.185-188]`,
`[leverage_for_the_long_run, p.4-7]`.

## Focused Leverage Sweep

Corrected scaling uses the KMLM-only counterpart to the top four-asset grid row:

`SPYSIM = 25L`, `KMLMSIM = 25L`, `GDESIM = 40L`, `ZROZSIM = 35L`,
`CASHX?E=-2 = 100 - 125L`.

The sweep is monthly-rebalanced in Testfol.io. Because the KMLM-only proxy starts in
1987 while `DBMFSIM` starts in 2000, comparisons against the `70/30 DBMF/KMLM`
proxy are directional, not apples-to-apples.

| Leverage | Window | CAGR | MDD | Vol | Sharpe | Sortino | Calmar | Terminal |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1.00x | 1987-12-31..2026-06-08 | 13.00% | -26.70% | 14.63% | 0.706 | 1.014 | 0.487 | 109.68x |
| 1.10x | 1987-12-31..2026-06-08 | 13.70% | -29.27% | 16.10% | 0.694 | 0.997 | 0.468 | 139.28x |
| 1.20x | 1987-12-31..2026-06-08 | 14.39% | -31.78% | 17.58% | 0.685 | 0.983 | 0.453 | 175.59x |
| 1.25x | 1987-12-31..2026-06-08 | 14.73% | -33.01% | 18.31% | 0.680 | 0.976 | 0.446 | 196.63x |
| 1.30x | 1987-12-31..2026-06-08 | 15.06% | -34.22% | 19.05% | 0.677 | 0.971 | 0.440 | 219.79x |
| 1.40x | 1987-12-31..2026-06-08 | 15.71% | -36.60% | 20.53% | 0.670 | 0.961 | 0.429 | 273.12x |
| 1.50x | 1987-12-31..2026-06-08 | 16.35% | -38.92% | 22.01% | 0.664 | 0.952 | 0.420 | 336.96x |
| 1.75x | 1987-12-31..2026-06-08 | 17.85% | -44.45% | 25.73% | 0.652 | 0.936 | 0.402 | 551.95x |
| 2.00x | 1987-12-31..2026-06-08 | 19.23% | -51.11% | 29.47% | 0.644 | 0.925 | 0.376 | 864.16x |
| 2.25x | 1987-12-31..2026-06-08 | 20.49% | -57.21% | 33.24% | 0.638 | 0.917 | 0.358 | 1,292.95x |
| 2.50x | 1987-12-31..2026-06-08 | 21.62% | -62.70% | 37.03% | 0.634 | 0.912 | 0.345 | 1,848.20x |
| 3.00x | 1987-12-31..2026-06-08 | 23.45% | -72.02% | 44.74% | 0.629 | 0.906 | 0.326 | 3,288.42x |

## Comparison Versus `70/30` MF Proxy

| Proxy | Leverage | Window | CAGR | MDD | Sharpe | Calmar | Reading |
|---|---:|---|---:|---:|---:|---:|---|
| `70/30 DBMF/KMLM` | 1.00x | 2000-2026 | 12.17% | -27.66% | 0.725 | 0.440 | Corrected top-grid margin base. |
| `70/30 DBMF/KMLM` | 1.25x | 2000-2026 | 13.97% | -34.14% | 0.699 | 0.409 | Already drawdown-heavy. |
| `70/30 DBMF/KMLM` | 1.50x | 2000-2026 | 15.66% | -40.18% | 0.681 | 0.390 | Upper-bound stress, not clean practical range. |
| `100% KMLM` | 1.00x | 1987-2026 | 13.00% | -26.70% | 0.706 | 0.487 | Longer-window lens with similar drawdown scale. |
| `100% KMLM` | 1.25x | 1987-2026 | 14.73% | -33.01% | 0.680 | 0.446 | Still not enough to justify default external margin. |
| `100% KMLM` | 1.50x | 1987-2026 | 16.35% | -38.92% | 0.664 | 0.420 | Diagnostic stress only. |

## Verdict

KMLM-only is useful as a longer-window robustness lens for the managed-futures
sleeve, but it does not change the practical conclusion from the corrected margin
sweep. Unlevered is the cleanest research profile. If external margin is revisited,
the only plausible range is still around `1.10x..1.25x`, and even that requires real
IBKR maintenance, financing, forced-liquidation, tax/friction and validation-gate
checks `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

Artifacts:

- Payloads: `raw/testfolio_kmlm_only_e_minus_2_payloads.json`.
- Responses: `raw/testfolio_kmlm_only_e_minus_2_responses.json`.
- Table: `results/kmlm_only_sweep_e_minus_2.csv`.
