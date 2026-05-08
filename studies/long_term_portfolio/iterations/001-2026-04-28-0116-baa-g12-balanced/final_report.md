# Final Report — Iter 001 BAA-G12 Balanced

## Verdict

**MARGINAL — 58/100. Not a winner.**

BAA-G12 Balanced passed most statistical gates but failed the pre-committed kill criterion: educational net Sharpe was **0.975**, below iter 009 HAA+Gold **1.120**. It also failed the strict winner Sharpe edge condition on all three datasets. The mechanism is robust as a drawdown reducer, but in this universe it is too defensive and too tax-dragged to advance the Sharpe frontier `[stocks_on_the_move, ch.6]`.

## Headline Metrics vs Iter 009

All candidate metrics are net of annual DARF via `AnnualDarfEngine`.

| dataset | candidate Sharpe | iter 009 Sharpe | Δ Sharpe | candidate CAGR | iter 009 CAGR | Δ CAGR | candidate MDD | iter 009 MDD | Δ MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| educational | 0.975 | 1.120 | -0.145 | 10.60% | 13.89% | -3.29pp | 16.34% | 20.81% | -4.47pp |
| vt_real | 0.792 | 1.061 | -0.269 | 8.42% | 12.87% | -4.45pp | 13.93% | 14.20% | -0.27pp |
| ndx_real | 0.782 | 0.954 | -0.172 | 7.66% | 10.55% | -2.89pp | 12.73% | 14.20% | -1.47pp |

Gross results were better but still not enough: educational gross Sharpe **1.101**, vt_real **0.893**, ndx_real **0.882**.

## Score Breakdown

| criterion | points | note |
|---|---:|---|
| Sharpe edge | 0/25 | 0 datasets beat iter 009 by +0.10 |
| Gates | 23/25 | 7/7 educational, 7/7 vt_real, 6/7 ndx_real |
| DSR | 15/15 | worst p = 0.00137 `[advances_fin_ml, p.222-223]` |
| CAGR floor | 0/15 | all three datasets below 0.8 x iter 009 CAGR |
| MDD ceiling | 15/15 | all three below iter 009 MDD + 5pp |
| Robustness bonus | 5/5 | 26/26 rolling 5y educational Sharpe windows positive |

## Gates

| dataset | gates | DSR p | G6 CI low | G7 gross CAGR parity |
|---|---:|---:|---:|---:|
| educational | 7/7 | 4.85e-08 | 0.4135 | np 12.36% vs pandas 12.08% |
| vt_real | 7/7 | 6.78e-04 | 0.1552 | np 9.71% vs pandas 9.61% |
| ndx_real | 6/7 | 1.37e-03 | 0.0842 | np 8.61% vs pandas 8.71% |

The ndx_real gate miss was G3': adapted walk-forward MDD. The headline issue is not that gate; it is the absence of any Sharpe edge and the CAGR shortfall.

## Config Tested

- Canary: `SPYSIM`, `VEASIM`, `VWOSIM`, `BNDSIM`.
- Canary signal: 13612W absolute momentum.
- Offensive: top 6 of 12 by SMA(12) relative momentum.
- Defensive: top 3 defensive-risk assets by SMA(12), replacing each with `CASHX` if below cash.
- Tax: `AnnualDarfEngine`.
- Configs tested: 1.

## What Worked

BAA-G12 reduced drawdowns consistently. Net MDD was **16.34% / 13.93% / 12.73%**, all inside the iter 009 + 5pp ceiling. Statistical evidence was also clean: DSR passed with per-iteration `n_trials=1`, bootstrap CI lows were positive, and numpy cross-library gross CAGR parity stayed inside ±3pp `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## What Did Not Work

The broader canary and defensive machinery spent too much time in low-return protection. That made BAA a good drawdown reducer but a poor frontier advancer. Against HAA+Gold, it sacrificed **3-4.5pp CAGR** and never closed the Sharpe gap. Annual DARF widened the gap: educational gross Sharpe **1.101** became net **0.975**.

## Lesson

For this synthetic/global universe, BAA-G12 is structurally subordinate to HAA+Gold for the current objective. The BAA mechanism buys smoother drawdowns, but iter 009 already has acceptable MDD while preserving materially higher CAGR and Sharpe. Do not re-test plain BAA-G12 Balanced in this universe unless the asset universe materially changes.

## Citations

- Keller, W.J. (2022), *Relative and Absolute Momentum in Times of Rising/Low Yields: Bold Asset Allocation (BAA)*, SSRN 4166845.
- Momentum rotation: `[stocks_on_the_move, ch.6]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Next Directions

1. Test static capital-efficient `NTSXSIM + GDESIM + KMLMSIM`; it is structurally different and directly targets lower turnover/tax drag.
2. Test Composite Momentum Standard only if kept simple: multi-lookback averaging without adding ML or regime stacks.
3. Revisit HAA offensive sleeves rather than BAA canary breadth; HAA’s binary canary remains the stronger Sharpe architecture in this universe.
