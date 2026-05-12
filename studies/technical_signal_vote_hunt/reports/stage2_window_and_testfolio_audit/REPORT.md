# Stage 2 Window And Testfolio Audit

Status: discovery audit, not a validation verdict.

## Question

QQQ->TQQQ showed much higher CAGR than QQQ->QLD while not having a worse max
drawdown in the first operational `CASH_USD + extra_lag_days=1` grids. This audit
checks whether that is mostly a window artifact and whether the same rule can be
tested on long-history testfolio data.

## Same-Window Tiingo Check

The original QLD grid used `2006-06-22..2026-04-14`, while TQQQ starts only on
`2010-02-12`. Re-running QLD on the TQQQ inception window changes the comparison
materially.

| Risk-on | Window | Best rule | Sortino | CAGR | MDD |
|---|---|---|---:|---:|---:|
| QLD | 2006-06-22..2026-04-14 | `roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0`, `k=2` | 1.3181 | 34.54% | -53.09% |
| QLD | 2010-02-12..2026-04-14 | `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3` | 1.4209 | 36.26% | -37.54% |
| TQQQ | 2010-02-12..2026-04-14 | `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3` | 1.4124 | 53.00% | -51.03% |

Interpretation: the apparent TQQQ MDD advantage was mostly not a leverage miracle;
it was an inception-window mismatch. On the same window, the best QLD rule is the
same as the best TQQQ rule and has a much smaller MDD, while TQQQ buys more CAGR
with a deeper drawdown.

## Fixed-Rule Transplants

Both rows use Tiingo, `CASH_USD`, `extra_lag_days=1`, and the TQQQ inception
window.

| Rule | Risk-on | Sortino | CAGR | Sharpe | MDD | Calmar |
|---|---|---:|---:|---:|---:|---:|
| TQQQ top / QLD truncated top | QLD | 1.4209 | 36.26% | 1.1900 | -37.54% | 0.9659 |
| QLD full-window top | QLD | 1.3339 | 34.67% | 1.0552 | -53.09% | 0.6530 |
| TQQQ top / QLD truncated top | TQQQ | 1.4124 | 53.00% | 1.1849 | -51.03% | 1.0386 |
| QLD full-window top | TQQQ | 1.3241 | 48.88% | 1.0476 | -69.81% | 0.7001 |

## Testfolio 1986+ Feasibility

The shared top rule is close-only and can be tested on testfolio long history.
The original full-window QLD top rule cannot be replicated exactly on testfolio
because it depends on OHLC-derived `ATR14%` and `CCI20` signals. Testfolio here
uses `QQQSIM`, `QLDSIM`, `TQQQSIM`, `CASHX`, and `ZROZSIM` with the same close-only
rule and `extra_lag_days=1`.

| Risk-on | Off leg | Window | Sortino | CAGR | Sharpe | MDD | Calmar |
|---|---|---|---:|---:|---:|---:|---:|
| QLDSIM | CASHX | 1986-01-03..2026-04-17 | 0.7194 | 17.06% | 0.6406 | -76.73% | 0.2223 |
| QLDSIM | ZROZSIM | 1986-01-03..2026-04-17 | 0.8993 | 19.19% | 0.6609 | -67.65% | 0.2837 |
| TQQQSIM | CASHX | 1986-01-03..2026-04-17 | 0.6725 | 18.90% | 0.5990 | -93.95% | 0.2012 |
| TQQQSIM | ZROZSIM | 1986-01-03..2026-04-17 | 0.8232 | 21.07% | 0.6290 | -90.35% | 0.2332 |

## Conclusion

- Same-window Tiingo comparison supports TQQQ as the higher-CAGR expression, but
  QLD is the cleaner risk-adjusted expression on MDD.
- The TQQQ headline CAGR remains suspect-by-default because it is post-2010,
  in-sample, and discovered after millions of trials `[advances_fin_ml, p.222-223]`.
- The 1986+ close-only proxy weakens the result materially and shows severe MDD
  for synthetic TQQQ, so it argues against treating the post-2010 TQQQ result as
  deployable without full validation `[advances_fin_ml, p.208-211]`.
