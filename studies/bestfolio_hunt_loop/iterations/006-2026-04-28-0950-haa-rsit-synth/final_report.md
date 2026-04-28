# Final Report — Iter 006 HAA RSIT Synth

## Verdict

**PROMISING — 71/100. Not a winner.**

The selected config was `rsit_with_ntsi`: HAA+Gold shell unchanged, offensive
set `NTSXSIM`, `NTSI`, `RSIT_PROXY`, `GDESIM`. `RSIT_PROXY` is synthetic:
`VEASIM + KMLMSIM - 50bps/year`, so this result is an incomplete exploratory
proxy until live RSIT data exists. The pre-committed kill fired: educational
net Sharpe was **0.869**, below the iter 004 kill threshold **0.990** and far
below iter 009 HAA+Gold **1.120** `[risk_parity, ch.5]`.

## Headline Metrics vs Iter 009

All candidate metrics are net of annual DARF via `AnnualDarfEngine`.

| dataset | candidate Sharpe | iter 009 Sharpe | Delta Sharpe | candidate CAGR | iter 009 CAGR | Delta CAGR | candidate MDD | iter 009 MDD | Delta MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| educational | 0.869 | 1.120 | -0.251 | 11.13% | 13.89% | -2.76pp | 22.12% | 20.81% | +1.31pp |
| vt_real | 0.897 | 1.061 | -0.164 | 11.33% | 12.87% | -1.54pp | 15.58% | 14.20% | +1.38pp |
| ndx_real | 0.837 | 0.954 | -0.117 | 9.65% | 10.55% | -0.90pp | 14.01% | 14.20% | -0.19pp |

## Score Breakdown

| criterion | points | note |
|---|---:|---|
| Sharpe edge | 0/25 | 0 datasets beat iter 009 by +0.10 |
| Gates | 21/25 | 6/7, 6/7, 7/7; PBO failed on educational and vt_real `[advances_fin_ml, p.208-211]` |
| DSR | 15/15 | worst p = 1.52e-02 with 4 configs tested `[advances_fin_ml, p.222-223]` |
| CAGR floor | 15/15 | all datasets cleared 0.8 x iter 009 |
| MDD ceiling | 15/15 | all datasets stayed within iter 009 MDD + 5pp |
| Robustness bonus | 5/5 | 26/26 educational rolling 5y Sharpe windows positive |

## Gates

| dataset | gates | PBO | DSR p | G3 max WF MDD | G6 CI low | G7 np CAGR |
|---|---:|---:|---:|---:|---:|---:|
| educational | 6/7 | 0.714 | 1.23e-04 | 22.12% | 0.3545 | 12.48% |
| vt_real | 6/7 | 0.845 | 4.93e-03 | 13.59% | 0.2806 | 12.56% |
| ndx_real | 7/7 | 0.484 | 1.52e-02 | 13.59% | 0.2094 | 10.76% |

## Configs Tested

Four pre-committed RSIT-centered offensive sets were tested:

| config | offensive candidates |
|---|---|
| `rsit_core` | `NTSXSIM`, `RSIT_PROXY`, `NTSE`, `GDESIM` |
| `rsit_with_ntsi` | `NTSXSIM`, `NTSI`, `RSIT_PROXY`, `GDESIM` |
| `rsit_rssb` | `NTSXSIM`, `RSIT_PROXY`, `RSSBSIM`, `GDESIM` |
| `rsit_global_mix` | `NTSXSIM`, `NTSI`, `RSIT_PROXY`, `RSSBSIM` |

Selection rule: maximum mean Sharpe divided by iter 009 Sharpe across
`educational`, `vt_real`, and `ndx_real`.

## What Worked

The synthetic RSIT sleeve did not break the HAA shell. DSR passed on all three
datasets, post-2020 Sharpe stayed positive, bootstrap 99.9% CI lows were
positive, and MDD stayed inside the iter 009 + 5pp ceiling. The CAGR floor also
cleared all datasets, which is better than the prior RSST/RSSB/CTA offensive
substitution on the educational floor.

## What Did Not Work

Sharpe fell materially everywhere. The RSIT proxy adds managed-futures exposure
to the international sleeve, but HAA+Gold already has fixed KMLM and gold.
Adding another embedded MF layer lowered realized volatility only modestly while
giving up enough CAGR and ranking stability to miss the frontier. PBO failures
of **0.714** and **0.845** on the two VTSIM windows show unstable grid
selection, not a reliable new edge `[advances_fin_ml, p.208-211]`.

## Lesson

Synthetic RSIT does not solve the bestfolio gap in this HAA+Gold architecture.
The missing edge is not "more MF attached to equity"; it must either reduce
false defensive states without diluting the offensive sleeve, or add a genuinely
new return source. RSIT should wait for live ETF data before any retest.

## Citations

- Return-stacked / capital-efficient construction: `[risk_parity, ch.5]`.
- HAA monthly momentum ranking: `[stocks_on_the_move, ch.6]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Next Directions

1. Test HAA defensive-state changes focused on Sharpe, especially KMLM-only or
   CASHX-dominant defense, without changing the offensive sleeve.
2. Test a dual-canary HAA variant (`VWOSIM` + `VTISIM`) to reduce false
   defensive states while preserving iter 009 offensive exposure.
3. Defer RSIT until live ETF data exists; any future retest should compare live
   tracking against this synthetic proxy first.
