# Final Report — Iter 003 Global Factor + CTA Stack

## Verdict

**MARGINAL — 54/100. Not a winner.**

The static stack did what it was supposed to do on CAGR, but not on Sharpe or drawdown. The selected config (`stack_gde_heavy`) reached net CAGR **12.09% / 11.77% / 13.11%** and passed **6/7 gates** on all three datasets, but failed the pre-committed kill criterion: educational net Sharpe was **0.823**, far below iter 009 HAA+Gold **1.120**. The mechanism is lower-turnover, but the stacked equity/gold/factor exposure lets drawdowns expand to **27-42%**, so it is structurally subordinate for this Sharpe-frontier objective `[risk_parity, p.1-2, p.10]`.

## Headline Metrics vs Iter 009

All candidate metrics are net of annual DARF via `AnnualDarfEngine`.

| dataset | candidate Sharpe | iter 009 Sharpe | Delta Sharpe | candidate CAGR | iter 009 CAGR | Delta CAGR | candidate MDD | iter 009 MDD | Delta MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| educational | 0.823 | 1.120 | -0.297 | 12.09% | 13.89% | -1.80pp | 41.76% | 20.81% | +20.95pp |
| vt_real | 0.742 | 1.061 | -0.319 | 11.77% | 12.87% | -1.10pp | 40.41% | 14.20% | +26.21pp |
| ndx_real | 0.910 | 0.954 | -0.044 | 13.11% | 10.55% | +2.56pp | 27.49% | 14.20% | +13.29pp |

## Score Breakdown

| criterion | points | note |
|---|---:|---|
| Sharpe edge | 0/25 | 0 datasets beat iter 009 by +0.10 |
| Gates | 19/25 | 6/7 on educational, vt_real, and ndx_real |
| DSR | 15/15 | worst p = 3.40e-02 with 6 configs tested this iteration `[advances_fin_ml, p.222-223]` |
| CAGR floor | 15/15 | all datasets cleared 0.8 x iter 009 CAGR |
| MDD ceiling | 0/15 | all datasets breached iter 009 MDD + 5pp |
| Robustness bonus | 5/5 | 27/27 rolling 5y educational Sharpe windows positive |

## Gates

| dataset | gates | PBO | DSR p | G3 max WF MDD | G6 CI low | G7 np CAGR |
|---|---:|---:|---:|---:|---:|---:|
| educational | 6/7 | 0.405 | 5.26e-04 | 41.76% | 0.3302 | 12.09% |
| vt_real | 6/7 | 0.179 | 3.40e-02 | 27.49% | 0.0654 | 11.80% |
| ndx_real | 6/7 | 0.167 | 1.01e-02 | 27.49% | 0.2624 | 13.17% |

The repeated failed gate was G3: walk-forward returns were positive, but at least one window exceeded the 25% drawdown limit.

## Config Tested

Six pre-committed static stacks were tested. The selected config was `stack_gde_heavy`, chosen by maximum mean Sharpe divided by the iter 009 dataset Sharpe:

- `RSSBSIM` 25%
- `GDESIM` 30%
- `KMLMSIM` 15%
- `VBRSIM` 10%
- `VSSSIM` 6%
- `VWOSIM` 4%
- `SPYSIM` 10%

## What Worked

The low-turnover static premise helped CAGR. Unlike iter 001 and 002, all three datasets cleared the CAGR floor, and PBO stayed below 0.5 across datasets `[advances_fin_ml, p.208-211]`. The ndx_real stretch even beat iter 009 CAGR by **+2.56pp**.

## What Did Not Work

The portfolio is too equity/gold beta-heavy for a Sharpe-frontier target. Drawdowns were worse than iter 009 by **13-26pp**, and Sharpe never came close to the required `benchmark + 0.10`. The tax advantage of low turnover was not enough to offset the absence of HAA's `VWOSIM` canary and defensive switching.

## Lesson

Static global/factor/CTA stacking can be a CAGR-preserving allocation, but in this universe it does not replace HAA+Gold as a Sharpe maximizer. For future work, static stacks should only be revisited with an explicit drawdown-control overlay or a different objective; plain low-turnover stacking is now a dead end for beating iter 009.

## Citations

- Risk-budget diversification and capital efficiency: `[risk_parity, p.1-2, p.10]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Next Directions

1. Test HAA + global factor tilt (`VEASIM` blended with `VBRSIM`/`VSSSIM`) because the canary is still doing essential drawdown work.
2. Test the RSST/RSSB replacement idea only inside HAA or another risk-on/risk-off shell, not as a plain static stack.
3. Defer RSIT synth until real ETF data exists, unless the loop needs a clearly marked incomplete synthetic exploration.
