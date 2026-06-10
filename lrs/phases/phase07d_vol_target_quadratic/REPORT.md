# Phase 7D - Quadratic Vol-Targeting sigma^2/RV^2 (DIAGNOSTIC)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

Single variation on Phase 6B: the leverage scalar is the continuous-Kelly inverse-variance form `L_t = clip(sigma_target^2 / RV_t^2, 0, L_max)` `[volatility_trading, p.135, p.138]`, capped per fractional-Kelly practice `[volatility_trading, p.139-140]`, with 6B's 0.25-ladder quantization, inertia, SMA200 weekly gate, risk-off sleeves and DARF tax verbatim `[systematic_trading, p.137-148]`.

Pre-registered grid: 2 branches x 3 sigma_targets x 2 RV windows x 6 lags = 72 rows. **n_trials ledger: 4221 + 72 = 4293.** Binary-baseline rows and the 6B linear-best comparison are not trials.

## Executive Conclusion

Pre-registered screen (best row per branch by WF beats, tie-break Calmar): **1/2 branches SUCCESS**. Criteria: WF beats strictly above the better of {binary baseline, 6B linear best} AND after-tax CAGR >= headline - 1pp AND MDD >= -50%. A SUCCESS feeds the Phase 7F composition slot only - NOT a gate pass, NOT a promotion `[advances_fin_ml, p.208-211]`.


## Screen Result

| Branch | Best config | WF vs control | CAGR vs headline-1pp | MDD >= -50% | Screen |
|---|---|---|---|---|---|
| SPY | sigma 40% / RV21 / lag 3 | 12/17 vs 12 F | 15.34% vs 15.44% P | -39.28% P | FAIL |
| QQQ | sigma 40% / RV21 / lag 2 | 8/11 vs 7 P | 19.53% vs 19.46% P | -42.63% P | SUCCESS |

## Plots

| Plot | File |
|---|---|
| Best-row quadratic leverage series | [plots/phase07d_leverage_series.png](plots/phase07d_leverage_series.png) |
| Equity/drawdown vs binary baseline | [plots/phase07d_equity_dd.png](plots/phase07d_equity_dd.png) |
| WF beat-count: baseline vs 6B linear vs 7D quadratic | [plots/phase07d_wf_comparison.png](plots/phase07d_wf_comparison.png) |
| CAGR x MDD frontier | [plots/phase07d_frontier.png](plots/phase07d_frontier.png) |

## Top SPY Rows (by WF beats, then Calmar)

| Sigma | RV | Lag | WF | CAGR | MDD | Sharpe | Calmar | Mean L (on) | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|
| 40% | 21 | 3 | 12/17 | 15.34% | -39.28% | 0.714 | 0.390 | 2.00 | 5.67 |
| 40% | 63 | 2 | 12/17 | 15.15% | -45.08% | 0.705 | 0.336 | 1.99 | 5.69 |
| 35% | 21 | 2 | 12/17 | 15.02% | -45.32% | 0.702 | 0.331 | 1.99 | 6.12 |
| 40% | 21 | 2 | 12/17 | 15.06% | -46.91% | 0.700 | 0.321 | 2.00 | 5.68 |
| 35% | 21 | 3 | 11/17 | 15.51% | -39.28% | 0.723 | 0.395 | 1.99 | 6.12 |
| 35% | 21 | 4 | 11/17 | 15.46% | -40.39% | 0.725 | 0.383 | 1.99 | 5.88 |
| 30% | 21 | 3 | 11/17 | 14.55% | -38.08% | 0.695 | 0.382 | 1.98 | 7.35 |
| 30% | 63 | 2 | 11/17 | 14.84% | -40.29% | 0.702 | 0.368 | 1.97 | 6.44 |

Binary baseline: WF 12/17, CAGR 15.44%, MDD -39.28%. 6B linear best: sigma 40%/RV21/lag 2, WF 12/17, CAGR 14.55%, MDD -37.17%.

## Top QQQ Rows (by WF beats, then Calmar)

| Sigma | RV | Lag | WF | CAGR | MDD | Sharpe | Calmar | Mean L (on) | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|
| 40% | 21 | 2 | 8/11 | 19.53% | -42.63% | 0.747 | 0.458 | 1.70 | 8.64 |
| 40% | 21 | 1 | 8/11 | 19.30% | -45.17% | 0.735 | 0.427 | 1.70 | 8.64 |
| 40% | 21 | 3 | 8/11 | 18.01% | -42.62% | 0.709 | 0.423 | 1.70 | 8.64 |
| 35% | 63 | 1 | 7/11 | 18.47% | -42.22% | 0.723 | 0.437 | 1.66 | 7.69 |
| 35% | 21 | 1 | 7/11 | 17.65% | -42.32% | 0.704 | 0.417 | 1.67 | 10.70 |
| 35% | 21 | 4 | 7/11 | 17.29% | -41.71% | 0.716 | 0.414 | 1.67 | 10.30 |
| 35% | 21 | 3 | 7/11 | 17.32% | -42.62% | 0.707 | 0.406 | 1.67 | 10.70 |
| 30% | 21 | 1 | 7/11 | 18.14% | -45.01% | 0.749 | 0.403 | 1.61 | 13.02 |

Binary baseline: WF 6/11, CAGR 19.46%, MDD -42.58%. 6B linear best: sigma 40%/RV21/lag 1, WF 7/11, CAGR 19.14%, MDD -42.18%.

## Phase Verdict

| Question | Verdict |
|---|---|
| SPY: quadratic sizing beats binary AND 6B linear on WF? | No (12/17 vs control 12). |
| QQQ: quadratic sizing beats binary AND 6B linear on WF? | Yes (8/11 vs control 7). |
| Screen successes? | 1/2. |
| Did we promote anything? | No - diagnostic only. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
