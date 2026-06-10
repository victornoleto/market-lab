# Phase 7A - Ensemble Multi-Lookback Fractional Position (DIAGNOSTIC)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

Replaces the binary SMA200 gate with a combined forecast over N SMA windows: the risk-on fraction is the share of member signals on, `f_t = (1/N) sum_w 1[P.shift(1) > SMA_w.shift(1)]`, scaled by the base's binary vol gate `[systematic_trading, p.118-119, p.129-133]`, `[leverage_for_the_long_run, p.14, Table 6]`, `[testing_tuning, p.327-335]`. Weekly cadence, lag convention, risk-off sleeves, ladder and DARF tax unchanged. Hypothesis: averaging over window speeds reduces whipsaw/window-luck and lifts walk-forward consistency, the binding Phase 4 gate.

Pre-registered grid: 6 bases x 2 window sets x 6 lags = 72 rows. **n_trials ledger: 4005 + 72 = 4077.** Baseline rows (binary bases at committed lags, recomputed) are comparisons, not trials.

**Built-in sanity (degenerate set `{200}` vs binary base):** SPY: max abs diff 0; QQQ: max abs diff 0.

## Executive Conclusion

Pre-registered screen (best trial row per branch by WF beats, tie-break Calmar): **1/2 branches SUCCESS**. Criteria: WF beats strictly above the best binary baseline AND after-tax CAGR >= headline - 1pp AND MDD >= -50%. A SUCCESS feeds the Phase 7F composition slot only - it is NOT a gate pass (the actual G3 level would need SPY >= 13/17, QQQ >= 9/11) and NOT a promotion `[advances_fin_ml, p.208-211]`.


## Screen Result

| Branch | Best config | WF best vs base | CAGR vs headline-1pp | MDD >= -50% | Screen |
|---|---|---|---|---|---|
| SPY | spy_alt_off / narrow_150_225 / lag 2 | 13/17 vs 12/17 P | 14.49% vs 15.44% P | -43.16% P | SUCCESS |
| QQQ | qqq_alt_vol / narrow_150_225 / lag 0 | 7/11 vs 7/11 F | 19.26% vs 19.46% P | -43.76% P | FAIL |

## Plots

| Plot | File |
|---|---|
| Best-row ensemble fraction | [plots/phase07a_fraction_series.png](plots/phase07a_fraction_series.png) |
| Equity/drawdown vs binary headline | [plots/phase07a_equity_dd.png](plots/phase07a_equity_dd.png) |
| WF beat-count comparison | [plots/phase07a_wf_comparison.png](plots/phase07a_wf_comparison.png) |
| CAGR x MDD frontier | [plots/phase07a_frontier.png](plots/phase07a_frontier.png) |

## Top SPY Rows (by WF beats, then Calmar)

| Base | Set | Lag | WF | CAGR | MDD | Sharpe | Calmar | Mean f | Partial days | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|---|
| spy_alt_off | narrow_150_225 | 2 | 13/17 | 14.49% | -43.16% | 0.695 | 0.336 | 0.73 | 7.4% | 13.71 |
| spy_alt_off | wide_100_300 | 2 | 12/17 | 13.86% | -41.35% | 0.686 | 0.335 | 0.73 | 18.6% | 20.12 |
| spy_top | narrow_150_225 | 2 | 12/17 | 14.33% | -44.14% | 0.689 | 0.325 | 0.73 | 7.4% | 12.10 |
| spy_top | wide_100_300 | 2 | 12/17 | 13.75% | -42.96% | 0.682 | 0.320 | 0.73 | 18.6% | 17.96 |
| spy_alt_off | narrow_150_225 | 1 | 12/17 | 13.93% | -44.65% | 0.668 | 0.312 | 0.73 | 7.4% | 13.71 |
| spy_alt_off | wide_100_300 | 1 | 11/17 | 14.20% | -41.07% | 0.690 | 0.346 | 0.73 | 18.6% | 20.12 |
| spy_top | wide_100_300 | 1 | 11/17 | 14.10% | -41.68% | 0.687 | 0.338 | 0.73 | 18.6% | 17.96 |
| spy_alt_off | narrow_150_225 | 4 | 11/17 | 14.26% | -42.16% | 0.697 | 0.338 | 0.73 | 7.4% | 12.57 |

Best binary baseline (spy_top): WF 12/17, CAGR 15.44%, MDD -39.28%, Sharpe 0.718, Calmar 0.393.

## Top QQQ Rows (by WF beats, then Calmar)

| Base | Set | Lag | WF | CAGR | MDD | Sharpe | Calmar | Mean f | Partial days | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|---|
| qqq_alt_vol | narrow_150_225 | 0 | 7/11 | 19.26% | -43.76% | 0.759 | 0.440 | 0.68 | 5.5% | 3.65 |
| qqq_alt_vol | wide_100_300 | 0 | 7/11 | 18.44% | -44.01% | 0.748 | 0.419 | 0.68 | 15.5% | 3.77 |
| qqq_top | wide_100_300 | 1 | 6/11 | 18.93% | -44.38% | 0.748 | 0.427 | 0.71 | 18.3% | 19.82 |
| qqq_alt_vol | wide_100_300 | 2 | 6/11 | 16.95% | -41.56% | 0.720 | 0.408 | 0.68 | 15.5% | 19.22 |
| qqq_top | narrow_150_225 | 0 | 5/11 | 19.94% | -43.63% | 0.748 | 0.457 | 0.71 | 6.6% | 3.03 |
| qqq_lower_lev | wide_100_300 | 5 | 5/11 | 15.94% | -35.43% | 0.748 | 0.450 | 0.71 | 18.3% | 9.36 |
| qqq_top | narrow_150_225 | 3 | 5/11 | 18.66% | -41.57% | 0.724 | 0.449 | 0.71 | 6.6% | 11.69 |
| qqq_lower_lev | narrow_150_225 | 3 | 5/11 | 17.26% | -39.37% | 0.741 | 0.438 | 0.71 | 6.6% | 11.69 |

Best binary baseline (qqq_alt_vol): WF 7/11, CAGR 18.32%, MDD -42.80%, Sharpe 0.725, Calmar 0.428.

## Phase Verdict

| Question | Verdict |
|---|---|
| SPY: fractional ensemble beats binary on WF consistency? | Yes (13/17 vs 12/17). |
| QQQ: fractional ensemble beats binary on WF consistency? | No (7/11 vs 7/11). |
| Screen successes? | 1/2. |
| Did we promote anything? | No - diagnostic only. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
