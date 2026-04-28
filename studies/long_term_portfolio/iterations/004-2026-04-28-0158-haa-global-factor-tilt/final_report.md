# Final Report — Iter 004 HAA Global Factor Tilt

## Verdict

**PROMISING — 69/100. Not a winner.**

The selected config was `tilt_scv20`: the HAA+Gold shell from iter 009, but with the stacked international sleeve blended as 80% `VEASIM`, 10% `VBRSIM`, and 10% `VSSSIM`. It preserved drawdown control and CAGR floors, but failed both pre-committed kills: educational net Sharpe was **0.990**, below iter 009's **1.120**, and **0/3** datasets beat iter 009 by +0.10 Sharpe. The family also failed G1 PBO on all datasets, so the best tilt level is not stable enough to trust as a selected grid winner `[advances_fin_ml, p.208-211]`.

## Headline Metrics vs Iter 009

All candidate metrics are net of annual DARF via `AnnualDarfEngine`.

| dataset | candidate Sharpe | iter 009 Sharpe | Delta Sharpe | candidate CAGR | iter 009 CAGR | Delta CAGR | candidate MDD | iter 009 MDD | Delta MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| educational | 0.990 | 1.120 | -0.130 | 12.21% | 13.89% | -1.68pp | 20.71% | 20.81% | -0.10pp |
| vt_real | 0.955 | 1.061 | -0.106 | 11.49% | 12.87% | -1.38pp | 14.20% | 14.20% | +0.00pp |
| ndx_real | 0.861 | 0.954 | -0.093 | 9.41% | 10.55% | -1.14pp | 14.20% | 14.20% | +0.00pp |

## Score Breakdown

| criterion | points | note |
|---|---:|---|
| Sharpe edge | 0/25 | 0 datasets beat iter 009 by +0.10 |
| Gates | 19/25 | 6/7 on all datasets; repeated failure was G1 PBO |
| DSR | 15/15 | worst p = 1.15e-02 with 4 configs tested `[advances_fin_ml, p.222-223]` |
| CAGR floor | 15/15 | all datasets cleared 0.8 x iter 009 CAGR |
| MDD ceiling | 15/15 | all datasets stayed within iter 009 MDD + 5pp |
| Robustness bonus | 5/5 | educational rolling 5y Sharpe windows were >= 90% positive |

## Gates

| dataset | gates | PBO | DSR p | G3 max WF MDD | G6 CI low | G7 np CAGR |
|---|---:|---:|---:|---:|---:|---:|
| educational | 6/7 | 0.885 | 7.62e-06 | 20.71% | 0.5050 | 13.76% |
| vt_real | 6/7 | 0.869 | 2.32e-03 | 14.20% | 0.3337 | 12.68% |
| ndx_real | 6/7 | 0.694 | 1.15e-02 | 14.20% | 0.2402 | 10.45% |

## Configs Tested

Four pre-committed tilts were tested:

| config | international blend |
|---|---|
| `tilt_scv10` | 90% `VEASIM`, 5% `VBRSIM`, 5% `VSSSIM` |
| `tilt_scv20` | 80% `VEASIM`, 10% `VBRSIM`, 10% `VSSSIM` |
| `tilt_scv30` | 70% `VEASIM`, 15% `VBRSIM`, 15% `VSSSIM` |
| `tilt_scv40` | 60% `VEASIM`, 20% `VBRSIM`, 20% `VSSSIM` |

Selection rule: maximum mean Sharpe divided by iter 009 Sharpe across `educational`, `vt_real`, and `ndx_real`.

## What Worked

The HAA canary shell continued to control drawdown. MDD stayed essentially equal to iter 009, G3 passed, post-2020 Sharpe stayed positive, DSR passed, and CAGR remained above the 0.8 x benchmark floor. This confirms again that the HAA regime switch is the valuable part of the architecture `[stocks_on_the_move, ch.6]`.

## What Did Not Work

The factor tilt diluted return without adding enough diversification. All four tilt levels clustered below iter 009 Sharpe, and the best config varied enough across time blocks that PBO was far above 0.5 in every dataset. In practical terms, the international small/value tilt is not an additive edge inside this HAA offensive set; it mostly reshuffles the same risk-on sleeve.

## Lesson

Simple HAA offensive factor tilting is not the missing +0.10 Sharpe. The canary keeps MDD intact, but replacing plain `VEASIM` with small/value blends sacrifices too much CAGR/Sharpe and introduces selection instability. Future HAA variants need a qualitatively different return source, not just a different equity factor mix.

## Citations

- HAA relative/absolute momentum shell: `[stocks_on_the_move, ch.6]`.
- Stacked sleeve construction: `[leverage_for_the_long_run, p.40-60]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Next Directions

1. Test RSST/RSSB only inside the HAA shell, because static stacking failed but the risk-on/risk-off wrapper remains necessary.
2. Test a HAA defensive-sleeve change with ZROZ/TLT duration only if it targets CAGR frontier tradeoff explicitly; iter 009 already owns Sharpe/MDD balance.
3. Defer RSIT until real ETF data exists, or mark any synthetic RSIT run as incomplete.
