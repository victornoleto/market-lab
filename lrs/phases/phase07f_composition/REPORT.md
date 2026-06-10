# Phase 7F - Composition of the Round Winners (DIAGNOSTIC)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

Composes the two orthogonal round winners with FROZEN parameters: 7A ensemble fraction (narrow set {150,175,200,225}) `[systematic_trading, p.118-119, p.129-133]` x 7D quadratic vol-target (sigma 40% / RV21) `[volatility_trading, p.135, p.138-140]`. Only the lag is swept; no new parameter search `[advances_fin_ml, p.208-211]`.

Pre-registered grid: 2 branches x 2 variants x 6 lags = 24 rows. **n_trials ledger: 4353 + 24 = 4377.**

**Built-in sanity (f_t forced to 1 vs pure quadratic ladder pipeline):** SPY: max abs diff 0; QQQ: max abs diff 0.

## Executive Conclusion

Pre-registered screen (best trial row per branch by WF beats, tie-break Calmar): **0/2 branches SUCCESS**. Criteria: WF beats strictly above the round best (SPY 13/17 from 7A, QQQ 8/11 from 7D) AND CAGR >= headline - 1pp AND MDD >= -50%. Either way, the round closes into the consolidated decision table for the user's Phase 8 pick. NOT a gate pass, NOT a promotion `[advances_fin_ml, p.208-211]`.


## Screen Result

| Branch | Best config | WF vs round best | CAGR vs headline-1pp | MDD >= -50% | Screen |
|---|---|---|---|---|---|
| SPY | ens_x_quad_gated / lag 2 | 12/17 vs 13 F | 14.30% F | -43.81% P | FAIL |
| QQQ | ens_x_quad / lag 0 | 6/11 vs 8 F | 20.16% P | -43.36% P | FAIL |

## Plots

| Plot | File |
|---|---|
| Best-row composed exposure f*L | [plots/phase07f_exposure_series.png](plots/phase07f_exposure_series.png) |
| Equity/drawdown vs binary headline | [plots/phase07f_equity_dd.png](plots/phase07f_equity_dd.png) |
| WF beat-count vs round best | [plots/phase07f_wf_comparison.png](plots/phase07f_wf_comparison.png) |
| CAGR x MDD frontier | [plots/phase07f_frontier.png](plots/phase07f_frontier.png) |

## Top SPY Rows (by WF beats, then Calmar)

| Variant | Lag | WF | CAGR | MDD | Sharpe | Calmar | Mean exposure | Turnover/y |
|---|---|---|---|---|---|---|---|---|
| ens_x_quad_gated | 2 | 12/17 | 14.30% | -43.81% | 0.688 | 0.327 | 1.46 | 12.12 |
| ens_x_quad | 2 | 12/17 | 14.17% | -48.12% | 0.682 | 0.294 | 1.46 | 12.24 |
| ens_x_quad_gated | 4 | 11/17 | 13.98% | -44.38% | 0.687 | 0.315 | 1.46 | 11.10 |
| ens_x_quad_gated | 3 | 11/17 | 13.85% | -44.07% | 0.676 | 0.314 | 1.46 | 12.09 |
| ens_x_quad | 3 | 11/17 | 13.83% | -44.07% | 0.674 | 0.314 | 1.46 | 12.21 |
| ens_x_quad | 4 | 11/17 | 13.97% | -45.55% | 0.686 | 0.307 | 1.46 | 11.18 |
| ens_x_quad_gated | 1 | 11/17 | 13.82% | -45.58% | 0.664 | 0.303 | 1.46 | 12.12 |
| ens_x_quad | 5 | 11/17 | 13.17% | -43.58% | 0.661 | 0.302 | 1.46 | 4.96 |

## Top QQQ Rows (by WF beats, then Calmar)

| Variant | Lag | WF | CAGR | MDD | Sharpe | Calmar | Mean exposure | Turnover/y |
|---|---|---|---|---|---|---|---|---|
| ens_x_quad | 0 | 6/11 | 20.16% | -43.36% | 0.761 | 0.465 | 1.26 | 3.56 |
| ens_x_quad | 2 | 6/11 | 19.79% | -42.89% | 0.766 | 0.461 | 1.26 | 14.55 |
| ens_x_quad | 1 | 6/11 | 19.76% | -43.26% | 0.757 | 0.457 | 1.26 | 14.55 |
| ens_x_quad_gated | 0 | 6/11 | 19.57% | -43.36% | 0.751 | 0.451 | 1.24 | 3.32 |
| ens_x_quad_gated | 1 | 5/11 | 19.29% | -43.26% | 0.751 | 0.446 | 1.24 | 13.27 |
| ens_x_quad_gated | 3 | 5/11 | 18.10% | -41.47% | 0.729 | 0.437 | 1.24 | 13.27 |
| ens_x_quad | 3 | 5/11 | 18.02% | -41.47% | 0.720 | 0.435 | 1.26 | 14.55 |
| ens_x_quad_gated | 5 | 5/11 | 16.94% | -41.01% | 0.706 | 0.413 | 1.24 | 6.04 |

## Phase Verdict

| Question | Verdict |
|---|---|
| SPY: composition beats the round best on WF? | No (12/17 vs 13). |
| QQQ: composition beats the round best on WF? | No (6/11 vs 8). |
| Screen successes? | 0/2. |
| Did we promote anything? | No - diagnostic only. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
