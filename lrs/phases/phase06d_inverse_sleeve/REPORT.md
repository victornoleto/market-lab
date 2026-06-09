# Phase 6D - Inverse Sleeve In Risk-Off (DIAGNOSTIC)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

Blends a capped synthetic inverse position (`r_inv = -r_underlying - 0.0095/252`, daily reset, in-memory only `[leverage_for_the_long_run, p.16, fn.22-23]`) into the headline risk-off sleeves: `risk_off' = (1-f)*risk_off + f*{INV}` `[trading_systems_methods, p.354]`, `[systematic_trading, p.137-148]`. Headline geometry and binary vol gate unchanged - the risk-off composition is the single mechanism family under test.

Pre-registered grid: 2 branches x f in {10%, 15%, 25%} x lag 0..5 = 36 rows (+36 to the n_trials ledger -> 3984 cumulative with Phase 6B). Screen read at the committed headline lag (SPY 3, QQQ 0); other lags are sensitivity only.

## Executive Conclusion

Branches passing the pre-registered screen (CAGR >= headline AND MDD strictly better, at the headline lag): **0/2**.

Sanity check: f=0 rows reproduce the Phase 4 headline metrics; max abs deviation spy_top `5.55e-17`, qqq_top `5.55e-17`.


## Plots

| Plot | File |
|---|---|
| Equity/drawdown best-f vs f=0 | [plots/phase06d_equity_dd.png](plots/phase06d_equity_dd.png) |
| Crisis-window zoom | [plots/phase06d_crisis_zoom.png](plots/phase06d_crisis_zoom.png) |
| CAGR/MDD vs inverse fraction | [plots/phase06d_f_sensitivity.png](plots/phase06d_f_sensitivity.png) |

## SPY At Headline Lag 3

| f | CAGR | MDD | Sharpe | Calmar | GFC ret | COVID ret | 2022 ret | Pass |
|---|---|---|---|---|---|---|---|---|
| 0% | 15.44% | -39.28% | 0.718 | 0.393 | -2.04% | -20.50% | -34.58% | - |
| 10% | 14.85% | -40.26% | 0.701 | 0.369 | 1.23% | -18.23% | -32.19% | no |
| 15% | 14.56% | -40.81% | 0.692 | 0.357 | 2.85% | -17.10% | -31.00% | no |
| 25% | 13.96% | -41.98% | 0.672 | 0.333 | 6.08% | -14.83% | -28.64% | no |

### SPY Lag Sensitivity

| f | Lags passing | Best lag CAGR | Worst lag MDD |
|---|---|---|---|
| 10% | 0/6 | 14.85% | -52.67% |
| 15% | 0/6 | 14.56% | -53.34% |
| 25% | 0/6 | 13.96% | -54.67% |

## QQQ At Headline Lag 0

| f | CAGR | MDD | Sharpe | Calmar | GFC ret | COVID ret | 2022 ret | Pass |
|---|---|---|---|---|---|---|---|---|
| 0% | 19.46% | -42.58% | 0.725 | 0.457 | -13.19% | -28.22% | -37.47% | - |
| 10% | 18.59% | -43.19% | 0.703 | 0.430 | -10.73% | -27.90% | -33.96% | no |
| 15% | 18.15% | -43.50% | 0.691 | 0.417 | -9.51% | -27.74% | -32.21% | no |
| 25% | 17.26% | -45.03% | 0.665 | 0.383 | -7.07% | -27.43% | -28.70% | no |

### QQQ Lag Sensitivity

| f | Lags passing | Best lag CAGR | Worst lag MDD |
|---|---|---|---|
| 10% | 0/6 | 18.59% | -44.82% |
| 15% | 0/6 | 18.15% | -45.90% |
| 25% | 0/6 | 17.26% | -48.04% |

## Phase Verdict

| Question | Verdict |
|---|---|
| SPY: does a capped inverse sleeve improve the headline? | No (0/3 fractions pass at lag 3). |
| QQQ: does a capped inverse sleeve improve the headline? | No (0/3 fractions pass at lag 0). |
| Screen successes? | 0/2. |
| Did we promote anything? | No - diagnostic only. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
