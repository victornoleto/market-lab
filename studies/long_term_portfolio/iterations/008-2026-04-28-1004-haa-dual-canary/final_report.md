# Final Report — Iter 008 HAA Dual Canary

## Verdict

**PROMISING — 73/100. Not a winner.**

The selected config was `vwo_only`, i.e. the original iter 009 HAA canary.
Adding `VTISIM` as either a substitute, permissive second canary, or strict
confirmation canary reduced net Sharpe on all three datasets. The
pre-committed kill fired: educational net Sharpe was **0.983**, below iter 009
HAA+Gold **1.120**, and zero datasets beat iter 009 by +0.10 Sharpe
`[stocks_on_the_move, ch.6]`.

## Headline Metrics vs Iter 009

All candidate metrics are net of annual DARF via `AnnualDarfEngine`.

| dataset | candidate Sharpe | iter 009 Sharpe | Delta Sharpe | candidate CAGR | iter 009 CAGR | Delta CAGR | candidate MDD | iter 009 MDD | Delta MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| educational | 0.983 | 1.120 | -0.137 | 12.15% | 13.89% | -1.74pp | 20.81% | 20.81% | +0.00pp |
| vt_real | 0.954 | 1.061 | -0.107 | 11.49% | 12.87% | -1.38pp | 14.20% | 14.20% | +0.00pp |
| ndx_real | 0.860 | 0.954 | -0.094 | 9.44% | 10.55% | -1.11pp | 14.20% | 14.20% | +0.00pp |

## Score Breakdown

| criterion | points | note |
|---|---:|---|
| Sharpe edge | 0/25 | 0 datasets beat iter 009 by +0.10 |
| Gates | 23/25 | 7/7 educational, 7/7 vt_real, 6/7 ndx_real |
| DSR | 15/15 | worst p = 1.15e-02 with 4 configs tested `[advances_fin_ml, p.222-223]` |
| CAGR floor | 15/15 | all datasets cleared 0.8 x iter 009 |
| MDD ceiling | 15/15 | all datasets stayed within iter 009 MDD + 5pp |
| Robustness bonus | 5/5 | 26/26 educational rolling 5y Sharpe windows positive |

## Gates

| dataset | gates | PBO | DSR p | G3 max WF MDD | G6 CI low | G7 np CAGR |
|---|---:|---:|---:|---:|---:|---:|
| educational | 7/7 | 0.488 | 8.88e-06 | 20.81% | 0.4969 | 13.70% |
| vt_real | 7/7 | 0.468 | 2.36e-03 | 14.20% | 0.3244 | 12.69% |
| ndx_real | 6/7 | 0.552 | 1.15e-02 | 14.20% | 0.2213 | 10.49% |

## Configs Tested

| config | canary rule | edu S/C/MDD | vt S/C/MDD | ndx S/C/MDD |
|---|---|---:|---:|---:|
| `vwo_only` | risk-on if `VWOSIM` HAA momentum > 0 | 0.983 / 12.15% / 20.81% | 0.954 / 11.49% / 14.20% | 0.860 / 9.44% / 14.20% |
| `vti_only` | risk-on if `VTISIM` HAA momentum > 0 | 0.865 / 10.78% / 20.81% | 0.794 / 9.78% / 18.93% | 0.768 / 9.00% / 18.93% |
| `either_vwo_vti` | risk-on if either canary > 0 | 0.922 / 12.13% / 20.81% | 0.893 / 11.61% / 18.93% | 0.790 / 9.57% / 18.93% |
| `both_vwo_vti` | risk-on only if both canaries > 0 | 0.929 / 10.80% / 20.81% | 0.853 / 9.66% / 13.99% | 0.842 / 8.86% / 13.99% |

Selection rule: maximum mean Sharpe divided by iter 009 Sharpe across
`educational`, `vt_real`, and `ndx_real`.

## What Worked

The original `VWOSIM` canary remains robust on the validation battery:
educational and vt_real passed all 7 gates, DSR passed on all datasets, and
the numpy reference stayed inside the ±3pp CAGR cross-lib gate
`[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## What Did Not Work

`VTISIM` did not reduce false-defensive drag. The permissive `either` rule
held risk assets too often and raised real-window MDD to **18.93%** while
lowering Sharpe. The strict `both` rule lowered MDD in real windows but cut
CAGR and Sharpe. The `vti_only` rule was worst overall. The broad US canary
is not a simple improvement over emerging-market weakness as the HAA risk
state trigger `[stocks_on_the_move, p.63-65]`.

## Lesson

The HAA frontier is not missing a second broad-equity canary. Within this
asset universe, `VWOSIM` remains the best simple binary risk-state trigger;
adding `VTISIM` either admits too many risk-on months or filters too much
return. The next plausible timing edge should be a qualitatively different
trend input, not another broad-equity absolute-momentum canary.

## Citations

- HAA monthly momentum ranking and regime-filter rationale:
  `[stocks_on_the_move, ch.6]`, `[stocks_on_the_move, p.63-65]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Next Directions

1. Test a Gayed-style SPY/VT trend input as an HAA canary, not as standalone
   leveraged equity, to target gradual bear markets `[leverage_for_the_long_run, p.40-60]`.
2. Test a tightly pre-committed volatility throttle on only the HAA dynamic
   sleeve if it avoids broad parameter search.
3. Consider a CAGR-frontier variant only if the objective explicitly shifts
   away from Sharpe-first ranking.
