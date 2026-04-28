# Final Report — Iter 007 HAA Defensive KMLM/CASH

## Verdict

**STRONG — 75/100. Not a winner.**

The selected config was `orig_ief_bnd_cash`, which is the original iter 009
defensive set: `IEFSIM`, `BNDSIM`, `CASHX`. The KMLM/CASH defensive variants
did not improve the frontier. This means the pre-committed kill fired:
educational net Sharpe was **0.983**, below iter 009 HAA+Gold **1.120**, and
zero datasets beat iter 009 by +0.10 Sharpe `[stocks_on_the_move, ch.6]`.

## Headline Metrics vs Iter 009

All candidate metrics are net of annual DARF via `AnnualDarfEngine`.

| dataset | candidate Sharpe | iter 009 Sharpe | Delta Sharpe | candidate CAGR | iter 009 CAGR | Delta CAGR | candidate MDD | iter 009 MDD | Delta MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| educational | 0.983 | 1.120 | -0.137 | 12.15% | 13.89% | -1.74pp | 20.81% | 20.81% | +0.00pp |
| vt_real | 0.954 | 1.061 | -0.107 | 11.49% | 12.87% | -1.38pp | 14.20% | 14.20% | +0.00pp |
| ndx_real | 0.860 | 0.954 | -0.094 | 9.44% | 10.55% | -1.11pp | 14.20% | 14.20% | +0.00pp |

## Pareto Comparison vs References

| reference | candidate relation |
|---|---|
| iter 009 HAA+Gold | Subordinate: lower Sharpe and CAGR on all three datasets, same MDD. |
| Plano C V3_1 v3.5 | Dominates risk-adjusted return in `vt_real`: Sharpe 0.954 vs 0.671, MDD 14.20% vs 52.43%. |
| VT 1x b&h | Dominates `vt_real`: Sharpe 0.954 vs 0.51 and much lower drawdown. |

## Score Breakdown

| criterion | points | note |
|---|---:|---|
| Sharpe edge | 0/25 | 0 datasets beat iter 009 by +0.10 |
| Gates | 25/25 | 7/7 gates on all datasets |
| DSR | 15/15 | worst p = 1.15e-02 with 4 configs tested `[advances_fin_ml, p.222-223]` |
| CAGR floor | 15/15 | all datasets cleared 0.8 x iter 009 |
| MDD ceiling | 15/15 | all datasets stayed within iter 009 MDD + 5pp |
| Robustness bonus | 5/5 | 26/26 educational rolling 5y Sharpe windows positive |

## Gates

| dataset | gates | PBO | DSR p | G3 max WF MDD | G6 CI low | G7 np CAGR |
|---|---:|---:|---:|---:|---:|---:|
| educational | 7/7 | 0.262 | 8.88e-06 | 20.81% | 0.4969 | 13.70% |
| vt_real | 7/7 | 0.270 | 2.36e-03 | 14.20% | 0.3244 | 12.69% |
| ndx_real | 7/7 | 0.313 | 1.15e-02 | 14.20% | 0.2213 | 10.49% |

## Configs Tested

| config | defensive candidates | edu S/C/MDD | vt S/C/MDD | ndx S/C/MDD |
|---|---|---:|---:|---:|
| `orig_ief_bnd_cash` | `IEFSIM`, `BNDSIM`, `CASHX` | 0.983 / 12.15% / 20.81% | 0.954 / 11.49% / 14.20% | 0.860 / 9.44% / 14.20% |
| `kmlm_cash` | `KMLMSIM`, `CASHX` | 0.856 / 12.11% / 27.49% | 0.792 / 10.73% / 27.49% | 0.680 / 8.62% / 27.49% |
| `kmlm_ief_cash` | `KMLMSIM`, `IEFSIM`, `CASHX` | 0.924 / 13.11% / 27.49% | 0.896 / 12.11% / 27.49% | 0.798 / 10.12% / 27.49% |
| `cash_only` | `CASHX` | 0.901 / 10.57% / 20.81% | 0.888 / 10.30% / 14.20% | 0.779 / 8.14% / 14.20% |

Selection rule: maximum mean Sharpe divided by iter 009 Sharpe across
`educational`, `vt_real`, and `ndx_real`.

## What Worked

The original defense remains statistically robust. PBO passed on all datasets
with a four-config grid, DSR passed with the relaxed per-iteration trial count,
post-2020 Sharpe stayed positive, bootstrap 99.9% CI lows were positive, and
numpy/pandas CAGR parity stayed inside the ±3pp gate `[advances_fin_ml,
p.208-211, p.222-223, p.196-202, p.31-34]`.

## What Did Not Work

KMLM-heavy defense raised drawdown sharply. `kmlm_cash` and `kmlm_ief_cash`
reached **27.49%** MDD in all datasets, above the iter 009 + 5pp ceiling for
the real windows, and still failed Sharpe edge. `cash_only` kept drawdown but
cut too much CAGR. The original bond/cash defense is not accidental; it is the
best Sharpe balance among these simple alternatives `[risk_parity, ch.5]`.

## Lesson

The missing bestfolio gap is not in a simple KMLM/CASH defensive-state swap.
HAA+Gold's original `IEFSIM`/`BNDSIM`/`CASHX` defense remains the best simple
risk-off set here. Future work should alter the canary signal itself rather
than replace the defensive assets after the signal has already fired.

## Citations

- HAA monthly momentum ranking: `[stocks_on_the_move, ch.6]`.
- Defensive diversifier/risk-budget rationale: `[risk_parity, ch.5]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Next Directions

1. Test a dual-canary HAA variant (`VWOSIM` plus `VTISIM`) that changes when
   the defensive state fires, while preserving the iter 009 offensive/defensive
   assets.
2. Test a Gayed-style trend input as the HAA canary, not as a standalone
   leveraged equity strategy, to address gradual bear markets.
3. Test a volatility-throttle overlay on the HAA dynamic sleeve only if it is
   pre-committed to one simple target and does not add a broad parameter grid.
