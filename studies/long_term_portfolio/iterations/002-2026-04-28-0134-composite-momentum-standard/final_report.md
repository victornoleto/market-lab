# Final Report — Iter 002 Composite Momentum Standard

## Verdict

**MARGINAL — 55/100. Not a winner.**

Composite Momentum Standard passed the full 7-gate battery on all three datasets, but failed the pre-committed kill criterion: educational net Sharpe was **0.940**, below iter 009 HAA+Gold **1.120**. The mechanism is statistically clean and drawdown-aware, but annual DARF plus the 60/40 IEF/gold risk-off sleeve leave too much CAGR behind to advance the Sharpe frontier `[stocks_on_the_move, p.21-30]`.

## Headline Metrics vs Iter 009

All candidate metrics are net of annual DARF via `AnnualDarfEngine`.

| dataset | candidate Sharpe | iter 009 Sharpe | Delta Sharpe | candidate CAGR | iter 009 CAGR | Delta CAGR | candidate MDD | iter 009 MDD | Delta MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| educational | 0.940 | 1.120 | -0.180 | 9.25% | 13.89% | -4.64pp | 20.76% | 20.81% | -0.05pp |
| vt_real | 0.958 | 1.061 | -0.103 | 9.94% | 12.87% | -2.93pp | 20.76% | 14.20% | +6.56pp |
| ndx_real | 0.957 | 0.954 | +0.003 | 9.59% | 10.55% | -0.96pp | 20.76% | 14.20% | +6.56pp |

Gross results were closer but still not enough: Sharpe **1.063 / 1.080 / 1.080**, CAGR **10.53% / 11.30% / 10.90%**.

## Score Breakdown

| criterion | points | note |
|---|---:|---|
| Sharpe edge | 0/25 | 0 datasets beat iter 009 by +0.10 |
| Gates | 25/25 | 7/7 on educational, vt_real, and ndx_real |
| DSR | 15/15 | worst p = 1.08e-04 `[advances_fin_ml, p.222-223]` |
| CAGR floor | 5/15 | only ndx_real cleared 0.8 x iter 009 CAGR |
| MDD ceiling | 5/15 | only educational stayed within iter 009 MDD + 5pp |
| Robustness bonus | 5/5 | 33/33 rolling 5y educational Sharpe windows positive |

## Gates

| dataset | gates | DSR p | G6 CI low | G7 gross CAGR parity |
|---|---:|---:|---:|---:|
| educational | 7/7 | 6.12e-09 | 0.4619 | np 10.50% vs pandas 10.53% |
| vt_real | 7/7 | 4.80e-05 | 0.3665 | np 11.26% vs pandas 11.30% |
| ndx_real | 7/7 | 1.08e-04 | 0.3690 | np 10.89% vs pandas 10.90% |

## Config Tested

- Regime: `SPYSIM` above/below 200-day SMA at month end.
- Risk-on: top 4 from `SPYSIM`, `QQQSIM`, `VEASIM`, `TLTSIM`, `IEFSIM`, `GLDSIM`, `KMLMSIM` by positive 8-month return.
- Sizing: inverse 63-day volatility among selected assets.
- Risk-off: 60% `IEFSIM` + 40% `GLDSIM`.
- Tax: `AnnualDarfEngine`.
- Configs tested: 1.

## What Worked

The signal is robust in the validation sense. DSR passed on all datasets, bootstrap 99.9% CI lows were positive, walk-forward passed 8/8 or 7/8 profitable windows, and the numpy reference stayed within the required +/-3pp gross CAGR band `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## What Did Not Work

The SPY 200-day gate and IEF/gold defensive sleeve avoided deep drawdowns but created a return ceiling. Net CAGR missed iter 009 by **2.9-4.6pp/y** on the two global datasets, and vt_real/ndx_real MDD rose above the iter 009 + 5pp ceiling. Annual DARF widened the gap: educational gross Sharpe **1.063** became net **0.940**.

## Lesson

Composite Momentum Standard is robust but structurally subordinate to HAA+Gold for this mandate objective. HAA's `VWOSIM` canary plus fixed KMLM/gold sleeves extracts more CAGR at similar or better drawdown, while Composite Momentum spends too much time in low-return defensive holdings. Do not re-test this exact SPY200/top4/inverse-vol/IEF+gold architecture without a materially different offensive universe or a lower-turnover tax design.

## Citations

- Momentum selection and relative strength: `[stocks_on_the_move, p.21-30]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Next Directions

1. Test static capital-efficient `NTSXSIM + GDESIM + KMLMSIM`; lower turnover directly targets the DARF drag seen in BAA and Composite Momentum.
2. Test HAA offensive-sleeve factor tilt (`VEASIM` blended with `VBRSIM`/value proxy) rather than another broad SPY-gated allocator.
3. Only revisit Composite Momentum if `VNQ`/`DBC` real or synthetic data are added; the current proxy universe is too bond/gold-heavy in risk-off states.
