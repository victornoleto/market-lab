# Final Report — Iter 005 HAA RSST/RSSB/CTA Stack

## Verdict

**PROMISING — 70/100. Not a winner.**

The selected config was `rssb_cta_balanced`: HAA+Gold shell unchanged, with
`RSSBSIM`, `NTSXSIM`, `CTAPSIM`, and `GDESIM` as the offensive candidates.
It passed **7/7 gates on all three datasets**, including PBO, DSR, walk-forward,
bootstrap, and cross-lib CAGR parity. The pre-committed kill still fired:
educational net Sharpe was **0.953**, below iter 004's **0.990** and far below
iter 009 HAA+Gold's **1.120**. The strategy was robust, but it did not advance
the Sharpe frontier `[advances_fin_ml, p.208-211, p.222-223]`.

## Headline Metrics vs Iter 009

All candidate metrics are net of annual DARF via `AnnualDarfEngine`.

| dataset | candidate Sharpe | iter 009 Sharpe | Delta Sharpe | candidate CAGR | iter 009 CAGR | Delta CAGR | candidate MDD | iter 009 MDD | Delta MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| educational | 0.953 | 1.120 | -0.167 | 11.11% | 13.89% | -2.78pp | 16.98% | 20.81% | -3.83pp |
| vt_real | 1.028 | 1.061 | -0.033 | 11.99% | 12.87% | -0.88pp | 13.97% | 14.20% | -0.23pp |
| ndx_real | 0.946 | 0.954 | -0.008 | 10.12% | 10.55% | -0.43pp | 13.97% | 14.20% | -0.23pp |

## Score Breakdown

| criterion | points | note |
|---|---:|---|
| Sharpe edge | 0/25 | 0 datasets beat iter 009 by +0.10 |
| Gates | 25/25 | 7/7 on all datasets |
| DSR | 15/15 | worst p = 4.55e-03 with 4 configs tested `[advances_fin_ml, p.222-223]` |
| CAGR floor | 10/15 | vt_real and ndx_real cleared 0.8 x iter 009; educational missed by less than 1 bp |
| MDD ceiling | 15/15 | all datasets stayed within iter 009 MDD + 5pp |
| Robustness bonus | 5/5 | educational rolling 5y Sharpe windows were 100% positive |

## Gates

| dataset | gates | PBO | DSR p | G3 max WF MDD | G6 CI low | G7 np CAGR |
|---|---:|---:|---:|---:|---:|---:|
| educational | 7/7 | 0.298 | 1.74e-05 | 16.98% | 0.4911 | 12.60% |
| vt_real | 7/7 | 0.409 | 8.75e-04 | 13.97% | 0.3490 | 13.38% |
| ndx_real | 7/7 | 0.437 | 4.55e-03 | 13.97% | 0.3595 | 11.32% |

## Configs Tested

Four pre-committed HAA offensive sets were tested:

| config | offensive candidates |
|---|---|
| `rsst_rssb_core` | `RSSBSIM`, `RSST_PROXY`, `NTSXSIM`, `GDESIM` |
| `rsst_rssb_intl` | `RSSBSIM`, `RSST_PROXY`, `NTSI`, `GDESIM` |
| `rsst_cta_core` | `RSSBSIM`, `RSST_PROXY`, `CTAPSIM`, `GDESIM` |
| `rssb_cta_balanced` | `RSSBSIM`, `NTSXSIM`, `CTAPSIM`, `GDESIM` |

Selection rule: maximum mean Sharpe divided by iter 009 Sharpe across
`educational`, `vt_real`, and `ndx_real`.

## What Worked

The HAA canary plus return-stacked candidates produced a statistically clean
run. PBO was below 0.5 in all datasets, the DSR p-values were comfortably below
0.05, post-2020 Sharpe stayed positive, and MDD improved slightly versus iter
009. This confirms that putting stacked sleeves inside the HAA shell avoids
the drawdown failure of the plain static stack `[risk_parity, ch.5]`.

## What Did Not Work

Return was too diluted. `CTAPSIM` and `RSSBSIM` reduced volatility and drawdown,
but they did not add enough independent CAGR to overcome the fixed KMLM/gold
sleeves and annual DARF drag. The result is a smoother but lower-return HAA
variant: good robustness, no Sharpe edge.

## Lesson

HAA can absorb RSST/RSSB/CTA candidates cleanly, but the simple stacked
offensive substitution is not the missing bestfolio gap. The frontier problem
is no longer just drawdown control; it requires incremental return that does
not dilute the offensive sleeve. More managed-futures exposure inside HAA
mostly trades CAGR for MDD.

## Citations

- Return stacking and capital-efficient sleeve construction: `[risk_parity, ch.5]`.
- Momentum/trend premise: `[stocks_on_the_move, p.21-30]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Next Directions

1. Test a HAA defensive-sleeve variant that targets Sharpe, not CAGR: KMLM-only
   or CASHX-dominant defensive state before adding high-duration assets.
2. Test a dual-canary HAA variant (`VWOSIM` + `VTISIM`) to reduce false
   defensive states without replacing the offensive sleeve.
3. Defer RSIT until real ETF data exists; if synthetic RSIT is used, mark it
   incomplete and treat it as exploratory only.
