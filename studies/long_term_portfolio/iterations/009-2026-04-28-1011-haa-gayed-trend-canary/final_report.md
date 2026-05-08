# Final Report — Iter 009 HAA Gayed Trend Canary

## Verdict

**PROMISING — 73/100. Not a winner.**

The selected config was `vwo_original`, i.e. the original HAA canary. The
Gayed-style `SPYSIM` and `VTSIM` monthly trend filters did not improve
Sharpe; they either cut CAGR or raised real-window drawdown. The
pre-committed kill fired because educational net Sharpe was **0.983**, below
iter 009 HAA+Gold **1.120**, and zero datasets beat iter 009 by +0.10 Sharpe
`[leverage_for_the_long_run, p.40-60]`.

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
| educational | 7/7 | 0.317 | 8.88e-06 | 20.81% | 0.4969 | 13.70% |
| vt_real | 7/7 | 0.397 | 2.36e-03 | 14.20% | 0.3244 | 12.69% |
| ndx_real | 6/7 | 0.548 | 1.15e-02 | 14.20% | 0.2213 | 10.49% |

## Configs Tested

| config | canary rule | edu S/C/MDD | vt S/C/MDD | ndx S/C/MDD |
|---|---|---:|---:|---:|
| `vwo_original` | original `VWOSIM` HAA momentum > 0 | 0.983 / 12.15% / 20.81% | 0.954 / 11.49% / 14.20% | 0.860 / 9.44% / 14.20% |
| `spy_trend` | `SPYSIM` above 10-month trend | 0.896 / 11.06% / 20.81% | 0.802 / 9.82% / 18.93% | 0.750 / 8.60% / 18.93% |
| `vt_trend` | `VTSIM` above 10-month trend | 0.901 / 11.10% / 20.81% | 0.927 / 11.22% / 13.99% | 0.876 / 9.88% / 13.99% |
| `vwo_and_spy_trend` | `VWOSIM` momentum and `SPYSIM` trend both positive | 0.933 / 10.77% / 20.81% | 0.843 / 9.56% / 13.99% | 0.800 / 8.31% / 13.99% |

Selection rule: maximum mean Sharpe divided by iter 009 Sharpe across
`educational`, `vt_real`, and `ndx_real`.

## What Worked

The original HAA `VWOSIM` canary remained statistically robust: 7/7 gates in
educational and vt_real, DSR passed on all datasets, and the numpy reference
stayed inside the ±3pp CAGR cross-lib gate `[advances_fin_ml, p.31-34]`.

## What Did Not Work

The Gayed trend input did not reduce false defensive states enough to pay
for the lost risk-on exposure. `SPYSIM` trend was too permissive in real
windows and raised MDD to **18.93%** while lowering Sharpe; `VTSIM` trend
lowered drawdown but still missed Sharpe; strict `VWOSIM` + `SPYSIM`
confirmation cut CAGR too much `[leverage_for_the_long_run, p.40-60]`.

## Lesson

Simple moving-average trend on SPY/VT is not the missing HAA timing edge.
The `VWOSIM` HAA canary remains the best simple state classifier in this
universe. Future timing work should avoid another simple broad-equity trend
input and should only proceed with a qualitatively different regime variable.

## Citations

- Gayed moving-average risk management: `[leverage_for_the_long_run, p.40-60]`.
- HAA monthly momentum ranking: `[stocks_on_the_move, ch.6]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Next Directions

1. Test a tightly pre-committed volatility throttle on only the HAA dynamic
   sleeve, if kept to a tiny grid and cited from volatility/risk-control
   literature.
2. Add real VT/VXUS data and re-check whether the VTSIM proxy is hiding any
   real-data canary behavior before further timing variants.
3. Consider stopping the Sharpe-frontier hunt unless a new regime input comes
   from outside broad-equity price trend.
