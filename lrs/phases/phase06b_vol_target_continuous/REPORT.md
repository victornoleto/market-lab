# Phase 6B - Continuous Vol-Targeting (DIAGNOSTIC)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

Replaces the Phase 2 binary realized-vol gate with continuous vol-target sizing `L_t = clip(sigma_target / RV_t, 0, L_max)` on the risk-on sleeve, quantized to the 0.25 ladder grid with position inertia `[systematic_trading, p.137-148]`, `[systematic_trading, p.159]`, `[systematic_trading, p.174]`. SMA200 weekly gate, risk-off sleeves, lag convention and DARF tax unchanged. Hypothesis: smooth sizing improves walk-forward consistency, the binding Phase 4 gate `[leverage_for_the_long_run, p.4-7]`, `[testing_tuning, p.327-335]`.

Pre-registered grid: 2 branches x 3 sigma_targets x 2 RV windows x 6 lags = 72 rows. **n_trials ledger: 3876 + 72 = 3948.** Baseline rows (binary headline bases, recomputed) are comparisons, not trials.

## Executive Conclusion

Pre-registered screen (best row per branch by WF beats, tie-break Calmar): **1/2 branches SUCCESS**. Criteria: WF beats strictly above the binary baseline AND after-tax CAGR >= headline - 1pp AND MDD >= -50%. A SUCCESS is a diagnostic lead for Phase 6A's satellite set only - it is NOT a gate pass (the actual G3 gate would need >=13/17 SPY, >=9/11 QQQ) and NOT a promotion `[advances_fin_ml, p.208-211]`.


## Screen Result

| Branch | Best config | WF best vs base | CAGR best vs base | MDD >= -50% | Screen |
|---|---|---|---|---|---|
| SPY | sigma 40% / RV21 / lag 2 | 12/17 vs 12/17 F | 14.55% vs 15.44% P | -37.17% P | FAIL |
| QQQ | sigma 40% / RV21 / lag 1 | 7/11 vs 6/11 P | 19.14% vs 19.46% P | -42.18% P | SUCCESS |

## Plots

| Plot | File |
|---|---|
| Best-row leverage series | [plots/phase06b_leverage_series.png](plots/phase06b_leverage_series.png) |
| Equity/drawdown vs binary baseline | [plots/phase06b_equity_dd.png](plots/phase06b_equity_dd.png) |
| WF beat-count comparison | [plots/phase06b_wf_comparison.png](plots/phase06b_wf_comparison.png) |
| CAGR x MDD frontier | [plots/phase06b_frontier.png](plots/phase06b_frontier.png) |

## Top SPY Rows (by WF beats, then Calmar)

| Sigma | RV | Lag | WF | CAGR | MDD | Sharpe | Calmar | Mean L (on) | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|
| 40% | 21 | 2 | 12/17 | 14.55% | -37.17% | 0.690 | 0.392 | 1.98 | 7.16 |
| 40% | 21 | 3 | 12/17 | 14.67% | -38.34% | 0.698 | 0.383 | 1.98 | 7.16 |
| 30% | 63 | 3 | 12/17 | 14.04% | -38.79% | 0.697 | 0.362 | 1.90 | 7.97 |
| 40% | 63 | 2 | 11/17 | 14.84% | -39.22% | 0.701 | 0.378 | 1.97 | 6.32 |
| 30% | 63 | 2 | 11/17 | 14.31% | -38.31% | 0.704 | 0.374 | 1.90 | 7.97 |
| 40% | 21 | 4 | 11/17 | 14.86% | -40.89% | 0.711 | 0.363 | 1.98 | 6.85 |
| 40% | 63 | 1 | 11/17 | 14.28% | -40.43% | 0.677 | 0.353 | 1.97 | 6.32 |
| 40% | 21 | 1 | 11/17 | 13.81% | -40.73% | 0.658 | 0.339 | 1.98 | 7.16 |

Binary baseline: WF 12/17, CAGR 15.44%, MDD -39.28%, Sharpe 0.718, Calmar 0.393.

## Top QQQ Rows (by WF beats, then Calmar)

| Sigma | RV | Lag | WF | CAGR | MDD | Sharpe | Calmar | Mean L (on) | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|
| 40% | 21 | 1 | 7/11 | 19.14% | -42.18% | 0.746 | 0.454 | 1.67 | 9.93 |
| 40% | 21 | 0 | 7/11 | 19.08% | -43.21% | 0.738 | 0.441 | 1.67 | 3.67 |
| 40% | 21 | 2 | 7/11 | 18.30% | -42.16% | 0.729 | 0.434 | 1.67 | 9.93 |
| 40% | 21 | 3 | 7/11 | 16.97% | -43.21% | 0.693 | 0.393 | 1.67 | 9.93 |
| 40% | 63 | 0 | 6/11 | 18.70% | -42.28% | 0.728 | 0.442 | 1.66 | 3.32 |
| 40% | 63 | 1 | 6/11 | 18.20% | -42.18% | 0.719 | 0.431 | 1.66 | 7.83 |
| 30% | 21 | 0 | 6/11 | 17.53% | -41.09% | 0.742 | 0.427 | 1.56 | 4.39 |
| 40% | 63 | 2 | 6/11 | 17.36% | -42.21% | 0.698 | 0.411 | 1.66 | 7.83 |

Binary baseline: WF 6/11, CAGR 19.46%, MDD -42.58%, Sharpe 0.725, Calmar 0.457.

## Phase Verdict

| Question | Verdict |
|---|---|
| SPY: continuous sizing beats binary on WF consistency? | No (12/17 vs 12/17). |
| QQQ: continuous sizing beats binary on WF consistency? | Yes (7/11 vs 6/11). |
| Screen successes? | 1/2. |
| Did we promote anything? | No - diagnostic only. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
