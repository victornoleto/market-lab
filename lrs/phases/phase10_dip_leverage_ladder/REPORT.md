# Phase 10 - Drawdown-Contingent Leverage Ladder, "Buy the Dip" (DIAGNOSTIC, RETURN-FIRST)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

User-directed contrarian family: L_base most of the time, escalate to L_dip when the underlying's drawdown crosses -d, de-escalate on recovery (`ath` = new high; `half` = DD back to -d/2), hysteresis per `[trading_systems_methods, p.383]`. Equity indices are high-noise/countertrend-matching markets `[trading_systems_methods, p.13]`; the recorded counter-thesis is that dips are high-vol regimes where leveraged compounding is worst `[leverage_for_the_long_run, p.7-9]`. No SMA gate, no vol gate (clean isolation). Weekly cadence, lag 0..5, `AnnualDarfEngine`.

Pre-registered grid: 2 branches x 2 profiles x 3 triggers x 2 exits x 6 lags = 144 rows. **n_trials ledger: 4425 + 144 = 4569.** Constant-leverage B&H rows, underlying B&H and the LRS headline are comparisons, not trials.

**Built-in sanity (trigger 100% never fires vs constant L_base):** SPY: max abs diff 0; QQQ: max abs diff 0.

## Executive Conclusion

Return-first pre-registered screen (best CAGR among MDD>=-50% rows, vs the row's own constant-leverage benchmarks): **0/2 branches SUCCESS**. Criteria: CAGR strictly above constant L_base B&H AND MDD >= -50% AND MDD strictly better than constant L_dip B&H. NOT a gate pass either way `[advances_fin_ml, p.208-211]`.


## Screen Result

| Branch | Best eligible row | CAGR > const L_base | MDD >= -50% | MDD better than const L_dip | Screen |
|---|---|---|---|---|---|
| SPY | none (all rows breach the -50% floor) | F | F | F | FAIL |
| QQQ | none (all rows breach the -50% floor) | F | F | F | FAIL |

## Plots

| Plot | File |
|---|---|
| CAGR x MDD frontier | [plots/phase10_frontier.png](plots/phase10_frontier.png) |

## SPY: "what dip level is interesting?" (best row per trigger x profile)

| Trigger | Profile | Best exit/lag | CAGR | MDD | Floor | Calmar | Escalated days | Episodes |
|---|---|---|---|---|---|---|---|---|
| -10% | 1.0 -> 2.0 | ath / lag 5 | 10.01% | -85.04% | BREACH | 0.118 | 43.6% | 22 |
| -10% | 1.5 -> 3.0 | ath / lag 5 | 9.11% | -97.46% | BREACH | 0.093 | 43.6% | 22 |
| -20% | 1.0 -> 2.0 | ath / lag 3 | 11.07% | -81.24% | BREACH | 0.136 | 28.1% | 7 |
| -20% | 1.5 -> 3.0 | ath / lag 3 | 11.07% | -96.04% | BREACH | 0.115 | 28.1% | 7 |
| -30% | 1.0 -> 2.0 | ath / lag 0 | 11.86% | -69.77% | BREACH | 0.170 | 23.0% | 6 |
| -30% | 1.5 -> 3.0 | ath / lag 0 | 12.65% | -89.51% | BREACH | 0.141 | 23.0% | 6 |

## Top SPY Rows (by CAGR)

| Profile | Trigger | Exit | Lag | CAGR | MDD | Floor | WF | Calmar | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|
| 1.5->3.0 | -30% | ath | 0 | 12.65% | -89.51% | BREACH | 12/17 | 0.141 | 0.21 |
| 1.5->3.0 | -30% | ath | 3 | 12.43% | -90.23% | BREACH | 14/17 | 0.138 | 0.41 |
| 1.5->3.0 | -30% | ath | 1 | 12.33% | -93.35% | BREACH | 13/17 | 0.132 | 0.41 |
| 1.5->3.0 | -30% | ath | 2 | 11.89% | -93.26% | BREACH | 13/17 | 0.127 | 0.41 |
| 1.0->2.0 | -30% | ath | 0 | 11.86% | -69.77% | BREACH | 9/17 | 0.170 | 0.21 |
| 1.5->3.0 | -30% | ath | 5 | 11.74% | -91.83% | BREACH | 11/17 | 0.128 | 0.41 |
| 1.5->3.0 | -30% | ath | 4 | 11.70% | -91.52% | BREACH | 11/17 | 0.128 | 0.41 |
| 1.0->2.0 | -30% | ath | 1 | 11.63% | -76.57% | BREACH | 10/17 | 0.152 | 0.41 |
| 1.0->2.0 | -30% | ath | 3 | 11.63% | -69.94% | BREACH | 12/17 | 0.166 | 0.41 |
| 1.5->3.0 | -30% | half | 0 | 11.46% | -90.01% | BREACH | 11/17 | 0.127 | 0.21 |

## SPY Benchmarks (non-trial)

| Benchmark | CAGR | MDD | Sharpe | Calmar |
|---|---|---|---|---|
| underlying_bh | 10.56% | -55.14% | 0.670 | 0.192 |
| const_1.00 | 10.56% | -55.14% | 0.670 | 0.192 |
| const_1.50 | 11.15% | -70.87% | 0.558 | 0.157 |
| const_2.00 | 11.60% | -88.27% | 0.494 | 0.131 |
| const_3.00 | 9.20% | -98.31% | 0.435 | 0.094 |
| lrs_headline | 15.44% | -39.28% | 0.718 | 0.393 |

## QQQ: "what dip level is interesting?" (best row per trigger x profile)

| Trigger | Profile | Best exit/lag | CAGR | MDD | Floor | Calmar | Escalated days | Episodes |
|---|---|---|---|---|---|---|---|---|
| -10% | 1.0 -> 2.0 | ath / lag 2 | 14.86% | -98.85% | BREACH | 0.150 | 65.0% | 35 |
| -10% | 1.5 -> 3.0 | ath / lag 5 | 10.65% | -99.97% | BREACH | 0.107 | 65.0% | 35 |
| -20% | 1.0 -> 2.0 | ath / lag 1 | 12.74% | -98.90% | BREACH | 0.129 | 48.5% | 8 |
| -20% | 1.5 -> 3.0 | ath / lag 0 | 8.15% | -99.98% | BREACH | 0.082 | 48.5% | 8 |
| -30% | 1.0 -> 2.0 | half / lag 2 | 11.45% | -98.58% | BREACH | 0.116 | 39.0% | 5 |
| -30% | 1.5 -> 3.0 | half / lag 2 | 8.81% | -99.98% | BREACH | 0.088 | 39.0% | 5 |

## Top QQQ Rows (by CAGR)

| Profile | Trigger | Exit | Lag | CAGR | MDD | Floor | WF | Calmar | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|
| 1.0->2.0 | -10% | ath | 2 | 14.86% | -98.85% | BREACH | 7/11 | 0.150 | 3.47 |
| 1.0->2.0 | -10% | ath | 1 | 14.27% | -98.97% | BREACH | 7/11 | 0.144 | 3.47 |
| 1.0->2.0 | -10% | ath | 5 | 14.23% | -98.47% | BREACH | 7/11 | 0.145 | 3.27 |
| 1.0->2.0 | -10% | ath | 3 | 14.09% | -98.70% | BREACH | 7/11 | 0.143 | 3.47 |
| 1.0->2.0 | -10% | ath | 4 | 13.83% | -98.56% | BREACH | 7/11 | 0.140 | 3.47 |
| 1.0->2.0 | -10% | ath | 0 | 13.18% | -99.18% | BREACH | 7/11 | 0.133 | 1.73 |
| 1.0->2.0 | -10% | half | 2 | 13.12% | -98.80% | BREACH | 6/11 | 0.133 | 4.16 |
| 1.0->2.0 | -10% | half | 1 | 12.78% | -98.88% | BREACH | 7/11 | 0.129 | 4.16 |
| 1.0->2.0 | -20% | ath | 1 | 12.74% | -98.90% | BREACH | 8/11 | 0.129 | 0.79 |
| 1.0->2.0 | -20% | ath | 0 | 12.23% | -98.58% | BREACH | 7/11 | 0.124 | 0.40 |

## QQQ Benchmarks (non-trial)

| Benchmark | CAGR | MDD | Sharpe | Calmar |
|---|---|---|---|---|
| underlying_bh | 14.36% | -82.97% | 0.650 | 0.173 |
| const_1.00 | 14.36% | -82.97% | 0.650 | 0.173 |
| const_1.50 | 16.18% | -96.28% | 0.576 | 0.168 |
| const_2.00 | 17.30% | -98.85% | 0.569 | 0.175 |
| const_3.00 | 12.44% | -99.98% | 0.541 | 0.124 |
| lrs_headline | 19.46% | -42.58% | 0.725 | 0.457 |

## Phase Verdict

| Question | Verdict |
|---|---|
| SPY: does dip-escalation beat its own constant-leverage benchmarks within the floor? | No (no row inside the floor). |
| QQQ: does dip-escalation beat its own constant-leverage benchmarks within the floor? | No (no row inside the floor). |
| Screen successes? | 0/2. |
| Did we promote anything? | No - return-first diagnostic only. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
