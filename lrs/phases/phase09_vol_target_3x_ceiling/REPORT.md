# Phase 9 - Quadratic Vol-Targeting with a 3x Ceiling (DIAGNOSTIC, RETURN-FIRST)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

User-directed phase (2026-06-10): raise the 7D quadratic sizing cap so the ladder reaches the cached 3x sleeves (UPROSIM/TQQQSIM) only in calm regimes - the continuous-Kelly reading of when 3x is the right exposure `[volatility_trading, p.135, p.138]`, `[volatility_trading, p.139-140]`, `[systematic_trading, p.137-148]`. Mechanism verbatim from Phase 7D/6B; new axis values L_max {2.50, 3.00}, sigma_target 45%.

Pre-registered grid: 2 branches x 2 caps x 2 sigmas x 6 lags = 48 rows. **n_trials ledger: 4377 + 48 = 4425.** Binary headline and 7D winner rows are comparisons, not trials.

**Built-in sanity (7D winner re-run through this pipeline vs committed CSV):** SPY: max abs diff 2.78e-17; QQQ: max abs diff 2.78e-17.

## Executive Conclusion

Return-first pre-registered screen (best CAGR among MDD>=-50% rows): **1/2 branches SUCCESS**. Criteria: CAGR strictly above the branch 7D winner AND MDD >= -50% AND WF beats not worse. A SUCCESS is a return-first diagnostic lead only - NOT a gate pass; a promotion-grade claim would need the full SS5 suite at the grown ledger, where DSR only gets harder `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.


## Screen Result

| Branch | Best eligible row | CAGR vs 7D winner | MDD >= -50% | WF not worse | Screen |
|---|---|---|---|---|---|
| SPY | L_max 2.50 / sigma 40% / lag 3 | 16.81% vs 15.34% P | -47.47% P | 12/17 vs 12/17 P | SUCCESS |
| QQQ | none (all rows breach the -50% floor) | F | F | F | FAIL |

## Plots

| Plot | File |
|---|---|
| Best-row ceiling leverage series | [plots/phase09_leverage_series.png](plots/phase09_leverage_series.png) |
| Time share per ladder rung | [plots/phase09_rung_share.png](plots/phase09_rung_share.png) |
| Equity/drawdown vs 7D winner and binary headline | [plots/phase09_equity_dd.png](plots/phase09_equity_dd.png) |
| CAGR x MDD frontier by cap/sigma | [plots/phase09_frontier.png](plots/phase09_frontier.png) |

## Top SPY Rows (by CAGR; floor breaches marked)

| L_max | Sigma | Lag | CAGR | MDD | Floor | WF | Sharpe | Calmar | Mean L (on) | >2x days (on) | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00 | 40% | 4 | 18.15% | -55.19% | BREACH | 13/17 | 0.662 | 0.329 | 2.98 | 99.1% | 6.33 |
| 3.00 | 40% | 3 | 18.10% | -53.76% | BREACH | 12/17 | 0.659 | 0.337 | 2.98 | 99.1% | 6.64 |
| 3.00 | 40% | 5 | 18.09% | -55.94% | BREACH | 12/17 | 0.664 | 0.323 | 2.98 | 99.1% | 4.21 |
| 3.00 | 45% | 3 | 17.86% | -53.77% | BREACH | 12/17 | 0.650 | 0.332 | 2.99 | 99.6% | 6.02 |
| 3.00 | 45% | 4 | 17.40% | -56.88% | BREACH | 11/17 | 0.641 | 0.306 | 2.99 | 99.6% | 5.78 |
| 3.00 | 40% | 2 | 17.31% | -59.28% | BREACH | 12/17 | 0.637 | 0.292 | 2.98 | 99.1% | 6.64 |
| 3.00 | 45% | 5 | 17.27% | -55.94% | BREACH | 11/17 | 0.639 | 0.309 | 2.99 | 99.6% | 3.93 |
| 3.00 | 45% | 2 | 17.17% | -64.15% | BREACH | 12/17 | 0.631 | 0.268 | 2.99 | 99.6% | 6.02 |
| 2.50 | 40% | 3 | 16.81% | -47.47% | ok | 12/17 | 0.675 | 0.354 | 2.49 | 99.1% | 6.05 |
| 2.50 | 45% | 3 | 16.80% | -47.63% | ok | 12/17 | 0.673 | 0.353 | 2.50 | 99.6% | 5.67 |

7D winner (old cap): L_max 2.00, sigma 40%/RV21/lag 3: CAGR 15.34%, MDD -39.28%, WF 12/17.

## Top QQQ Rows (by CAGR; floor breaches marked)

| L_max | Sigma | Lag | CAGR | MDD | Floor | WF | Sharpe | Calmar | Mean L (on) | >2x days (on) | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00 | 40% | 1 | 24.74% | -61.76% | BREACH | 7/11 | 0.718 | 0.401 | 2.78 | 88.1% | 16.17 |
| 3.00 | 45% | 2 | 24.18% | -67.14% | BREACH | 9/11 | 0.701 | 0.360 | 2.85 | 92.9% | 13.26 |
| 3.00 | 45% | 0 | 23.91% | -63.67% | BREACH | 8/11 | 0.688 | 0.375 | 2.85 | 92.9% | 4.70 |
| 3.00 | 40% | 0 | 23.88% | -60.49% | BREACH | 8/11 | 0.697 | 0.395 | 2.78 | 88.1% | 5.35 |
| 2.50 | 40% | 2 | 23.41% | -57.95% | BREACH | 8/11 | 0.736 | 0.404 | 2.37 | 88.1% | 12.66 |
| 3.00 | 40% | 2 | 23.26% | -67.14% | BREACH | 8/11 | 0.698 | 0.346 | 2.78 | 88.1% | 16.17 |
| 2.50 | 45% | 0 | 22.92% | -55.92% | BREACH | 8/11 | 0.702 | 0.410 | 2.41 | 92.9% | 4.03 |
| 2.50 | 40% | 0 | 22.53% | -55.85% | BREACH | 8/11 | 0.706 | 0.403 | 2.37 | 88.1% | 4.38 |
| 3.00 | 45% | 1 | 22.24% | -64.24% | BREACH | 8/11 | 0.663 | 0.346 | 2.85 | 92.9% | 13.26 |
| 2.50 | 40% | 1 | 22.19% | -56.14% | BREACH | 8/11 | 0.704 | 0.395 | 2.37 | 88.1% | 12.66 |

7D winner (old cap): L_max 1.75, sigma 40%/RV21/lag 2: CAGR 19.53%, MDD -42.63%, WF 8/11.

## Phase Verdict

| Question | Verdict |
|---|---|
| SPY: does a 2.5x/3x ceiling add CAGR within the -50% floor without losing WF? | Yes (16.81% @ -47.47%, WF 12/17). |
| QQQ: does a 2.5x/3x ceiling add CAGR within the -50% floor without losing WF? | No (no row inside the floor). |
| Screen successes? | 1/2. |
| Did we promote anything? | No - return-first diagnostic only. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
