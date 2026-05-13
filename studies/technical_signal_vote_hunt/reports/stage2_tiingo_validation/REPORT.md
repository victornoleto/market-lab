# Stage 2 Tiingo Validation: Stage 3 Fixed-Rule Challengers

Status: real-ETF validation for Tiingo candidates derived from the Stage 3 shared
testfolio rule.

## Verdict

**0/80 candidates passed all hard gates.**

The Tiingo OHLC expansion around the shared Stage 3 rule did not produce a better
candidate than the existing Stage 2 Tiingo leads. All selected candidates passed
OOS, FWD and bootstrap, but failed DSR and PBO; many also failed the walk-forward
gate. This leaves the previous Tiingo configs as the better modern-regime leads,
while the Stage 3 rule remains useful only as a diagnostic bridge between
testfolio and Tiingo `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.208-211]`.

## Inputs

Base fixed rule from Stage 3:

`px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50`, `n=8/k=6`.

Tiingo diagnostic setup:

- `off_leg=CASH_USD`
- `extra_lag_days=1`
- one-edit OHLC neighborhood: drop/add/swap using adjusted OHLC indicators
- validation `n_trials=122,648,244`

## Local Search Results

| Run | Window | Base Sortino | Base CAGR | Base MDD | Best local Sortino | Best local CAGR | Best local MDD |
|---|---|---:|---:|---:|---:|---:|---:|
| QLD | 2010-02-12..2026-04-14 | 0.9697 | 21.63% | -39.82% | 1.2058 | 33.51% | -63.68% |
| TQQQ | 2010-02-12..2026-04-14 | 0.9584 | 30.31% | -54.02% | 1.1879 | 43.74% | -81.65% |

Best local rule in both panels replaced `rsi14_gt_50` with `atr14_pct_lt_5` and
used `k=1`. That is performance-improving in-sample, but structurally weak:
`k=1` effectively makes the strategy almost always-on once any broad trend or
volatility condition is true, and drawdown worsens materially.

## Gate Summary

| Run | Candidates | OOS pass | FWD pass | WF pass | Bootstrap pass | DSR pass | PBO pass | All pass | PBO | DSR p range |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| QLD top-40 | 40 | 40 | 40 | 26 | 40 | 0 | 0 | 0 | 0.6905 | 0.9324..0.9864 |
| TQQQ top-40 | 40 | 40 | 40 | 30 | 40 | 0 | 0 | 0 | 0.6746 | 0.9374..0.9875 |

## Comparison To Existing Tiingo Leads

The prior operational Stage 2 configs remain stronger:

- QLD same-window cash+lag1 lead: Sortino 1.4209, CAGR 36.26%, MDD -37.54%.
- TQQQ cash+lag1 lead: Sortino 1.4124, CAGR 53.00%, MDD -51.03%.

The Stage 3-derived Tiingo local candidates do not improve this frontier. The
best CAGR candidates have worse drawdowns, and the lower-drawdown candidates have
lower Sortino/CAGR than the existing leads.

## Artifacts

Local diagnostics:

- `../../results/stage2_tiingo_ohlc/stage3_fixed_rule_QQQ_QLD_CASH_USD_lag1_from20100212_local/REPORT.md`
- `../../results/stage2_tiingo_ohlc/stage3_fixed_rule_QQQ_TQQQ_CASH_USD_lag1_local/REPORT.md`

Validations:

- `stage3_fixed_rule_QQQ_QLD_CASH_USD_lag1_from20100212_top40/REPORT.md`
- `stage3_fixed_rule_QQQ_TQQQ_CASH_USD_lag1_top40/REPORT.md`

## Next Step

If continuing Tiingo discovery, do not expand this Stage 3 rule locally. The more
promising path is a constrained Tiingo GA/beam search seeded by the existing
Stage 2 winners and using OHLC features such as `ATR14%`, `ADX14`, `bear_power`
and `CCI20`, with strict `CASH_USD + extra_lag_days=1` and cumulative trial
accounting.

## Operational Stage 2 Winners Validation

User requested honest validation of the actual Stage 2 operational winners, not
only the Stage 3 fixed-rule Tiingo neighborhood. Validated top-200 from the two
`CASH_USD + extra_lag_days=1` exact grids:

- `QQQ_QLD_CASH_USD_lag1_n1_5_from20100212`
- `QQQ_TQQQ_CASH_USD_lag1_n1_5`

Validation used `n_trials=136,784,374`, including the known Stage 1/2/3 searches
plus these operational grids.

| Run | Candidates | OOS pass | FWD pass | WF pass | Bootstrap pass | DSR pass | PBO pass | All pass | PBO | DSR p range | Top Sortino | Top CAGR | Top MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Operational QLD | 200 | 200 | 200 | 187 | 200 | 0 | 0 | 0 | 0.6230 | 0.8339..0.9501 | 1.4209 | 36.26% | -37.54% |
| Operational TQQQ | 200 | 200 | 200 | 186 | 200 | 0 | 0 | 0 | 0.6349 | 0.8386..0.9541 | 1.4124 | 53.00% | -51.03% |

Interpretation: these are still the best modern-regime Tiingo leads by economic
metrics, but they do not pass honest validation. Compared with the Stage 3
fixed-rule Tiingo neighborhood, they are economically stronger but still fail the
same two overfit/data-mining gates.

Artifacts:

- `operational_QQQ_QLD_CASH_USD_lag1_n1_5_from20100212_top200/REPORT.md`
- `operational_QQQ_TQQQ_CASH_USD_lag1_n1_5_top200/REPORT.md`
