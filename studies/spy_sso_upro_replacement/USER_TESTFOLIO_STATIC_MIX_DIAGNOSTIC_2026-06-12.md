# User Testfol.io Static Mix Diagnostic (2026-06-12)

Status: research-only diagnostic. No Bearer token was used or stored. The token pasted in chat should be revoked/rotated outside this repo.

## Question

The user proposed two monthly static portfolios intended to keep roughly 1x SPY exposure through LETFs while adding diversifiers:

| ID | Allocation | Rebalance |
|---|---|---|
| SPY | `100% SPYSIM` | yearly |
| P2 | `50% SPYSIM?L=2&E=0.91`, `12.5% ZROZSIM`, `12.5% VBRSIM`, `12.5% GLDSIM`, `12.5% KMLMSIM` | monthly |
| P3 | `34% SPYSIM?L=3&E=0.91`, `16.5% ZROZSIM`, `16.5% VBRSIM`, `16.5% GLDSIM`, `16.5% KMLMSIM` | monthly |

The economic intuition is reasonable but not guaranteed: daily-reset leverage near 1x effective exposure can still lag SPY because CAGR depends on path, volatility decay, financing and rebalance interactions `[leverage_for_the_long_run, p.13]`, `[volatility_trading, p.135, p.138-140]`.

## Data

Source: Testfol.io `/api/backtest` with public browser headers, no authorization header. Limiting ticker: `KMLMSIM`. Window: `1987-12-31` to `2026-06-11`.

## Full-Window Metrics

| Series | CAGR | MDD | Sharpe | Calmar | Final/SPY |
|---|---:|---:|---:|---:|---:|
| SPY | 11.52% | -55.14% | 0.530 | 0.209 | 1.00x |
| P2 | 13.33% | -56.16% | 0.591 | 0.237 | 1.86x |
| P3 | 13.98% | -57.96% | 0.607 | 0.241 | 2.32x |

Relative equity diagnostics:

| Ratio | Final | Minimum | Relative MDD |
|---|---:|---:|---:|
| P2/SPY | 1.857 | 0.962 on 1990-10-16 | -10.82% |
| P3/SPY | 2.319 | 0.951 on 1990-10-16 | -13.99% |

The user's telltale observation is directionally correct: below-1 relative wealth is concentrated in the early 1988-1993 regime, with the minimum in 1990. That does not mean monotonic dominance; both lines still have meaningful relative drawdowns after becoming winners.

## Rolling Relative Performance

| Series | 12m beat rate | 36m beat rate | 60m beat rate | 120m beat rate |
|---|---:|---:|---:|---:|
| P2 vs SPY | 65.6% | 79.2% | 94.5% | 99.7% |
| P3 vs SPY | 66.3% | 79.2% | 93.8% | 100.0% |

Worst 60-month relative window ended 2025-07: both P2 and P3 lagged SPY by about `10pp` cumulative over that 5-year window.

## Comparable Later Starts

| Start | SPY CAGR/MDD | P2 CAGR/MDD | P3 CAGR/MDD | Local RSC gross CAGR/MDD |
|---|---:|---:|---:|---:|
| 2000 | 8.28% / -55.14% | 10.30% / -56.16% | 10.93% / -57.96% | 12.38% / -30.76% |
| 2006 | 11.21% / -55.14% | 12.77% / -56.16% | 13.36% / -57.96% | 13.60% / -30.76% |
| 2010 | 14.29% / -33.69% | 16.12% / -34.77% | 17.01% / -35.22% | 14.85% / -24.85% |

The 1988+ result is strong versus SPY. The repo-relevant comparison is weaker: from 2000+, P2/P3 do not beat the local RSC core on CAGR and they more than double max drawdown.

## Verdict

As an SPY replacement study, P2/P3 are interesting and explain why the relative line looks compelling. As a replacement for the current RSC-style profile, the trade is unattractive: accepting roughly `-56%` to `-58%` drawdown instead of about `-30%` does not buy enough CAGR in the comparable 2000+ window.

Conclusion: keep as a SPY-relative diagnostic, not a candidate for mandate change or RSC replacement `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
