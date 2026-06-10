# Phase 7C - Macro Growth-Trend-Timing Gate via UNRATE (DIAGNOSTIC)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

Applies the trend rule only when `UNRATE > SMA12m(UNRATE)` (publication-lagged 25 trading days); in expansions the target-leverage sleeve is held unconditionally (scope `trend_and_vol`) or gated by vol only (scope `trend_only`). **Citation EXCEPTION approved by the user (2026-06-09):** the rule is from the Philosophical Economics "Growth-Trend Timing" essay; the family anchors on the S&P-below-200dma recession/expansion asymmetry (68.2% vs 19.4%) `[leverage_for_the_long_run, p.9]`, honest alignment per `[advances_fin_ml, p.31-34]`. Vintage caveat: FRED serves revised UNRATE data (ALFRED point-in-time check = future work).

Pre-registered grid: 6 bases x 2 scopes x 6 lags = 72 rows. **n_trials ledger: 4149 + 72 = 4221.** Baseline rows are comparisons, not trials.

**Built-in sanity (macro_risk forced True vs binary base):** SPY: max abs diff 0; QQQ: max abs diff 0.

## Executive Conclusion

Pre-registered screen (best trial row per branch by WF beats, tie-break Calmar): **0/2 branches SUCCESS**. Criteria: WF beats strictly above the best binary baseline AND after-tax CAGR >= headline - 1pp AND MDD >= -50%. A SUCCESS feeds the Phase 7F composition slot only - NOT a gate pass, NOT a promotion `[advances_fin_ml, p.208-211]`.


## Screen Result

| Branch | Best config | WF best vs base | CAGR vs headline-1pp | MDD >= -50% | Screen |
|---|---|---|---|---|---|
| SPY | spy_top / trend_only / lag 0 | 14/17 vs 12/17 P | 16.56% vs 15.44% P | -58.87% F | FAIL |
| QQQ | qqq_lower_lev / trend_only / lag 4 | 10/11 vs 7/11 P | 21.76% vs 19.46% P | -52.14% F | FAIL |

## Plots

| Plot | File |
|---|---|
| Equity with macro-risk shading | [plots/phase07c_regime_equity.png](plots/phase07c_regime_equity.png) |
| Equity/drawdown vs binary headline | [plots/phase07c_equity_dd.png](plots/phase07c_equity_dd.png) |
| WF beat-count comparison | [plots/phase07c_wf_comparison.png](plots/phase07c_wf_comparison.png) |
| CAGR x MDD frontier | [plots/phase07c_frontier.png](plots/phase07c_frontier.png) |

## Top SPY Rows (by WF beats, then Calmar)

| Base | Scope | Lag | WF | CAGR | MDD | Sharpe | Calmar | Expansion days | Risk-on days | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|---|
| spy_top | trend_only | 0 | 14/17 | 16.56% | -58.87% | 0.689 | 0.281 | 62.7% | 84.6% | 1.77 |
| spy_alt_off | trend_only | 0 | 14/17 | 16.49% | -58.87% | 0.687 | 0.280 | 62.7% | 84.6% | 1.77 |
| spy_lower_lev | trend_only | 0 | 13/17 | 15.74% | -55.12% | 0.708 | 0.286 | 62.7% | 84.6% | 1.77 |
| spy_top | trend_only | 3 | 13/17 | 16.23% | -58.87% | 0.684 | 0.276 | 62.7% | 84.6% | 3.11 |
| spy_top | trend_only | 4 | 13/17 | 16.23% | -58.87% | 0.685 | 0.276 | 62.7% | 84.6% | 3.01 |
| spy_alt_off | trend_only | 4 | 13/17 | 16.22% | -58.87% | 0.685 | 0.275 | 62.7% | 84.6% | 3.44 |
| spy_alt_off | trend_only | 5 | 13/17 | 16.22% | -58.87% | 0.687 | 0.275 | 62.7% | 84.6% | 2.65 |
| spy_alt_off | trend_only | 3 | 13/17 | 16.18% | -58.87% | 0.682 | 0.275 | 62.7% | 84.6% | 3.55 |

Best binary baseline (spy_top): WF 12/17, CAGR 15.44%, MDD -39.28%, Sharpe 0.718, Calmar 0.393.

## Top QQQ Rows (by WF beats, then Calmar)

| Base | Scope | Lag | WF | CAGR | MDD | Sharpe | Calmar | Expansion days | Risk-on days | Turnover/y |
|---|---|---|---|---|---|---|---|---|---|---|
| qqq_lower_lev | trend_only | 4 | 10/11 | 21.76% | -52.14% | 0.802 | 0.417 | 66.8% | 82.8% | 2.63 |
| qqq_lower_lev | trend_only | 3 | 10/11 | 21.75% | -52.20% | 0.801 | 0.417 | 66.8% | 82.8% | 2.63 |
| qqq_lower_lev | trend_only | 2 | 10/11 | 21.52% | -52.06% | 0.793 | 0.413 | 66.8% | 82.8% | 2.63 |
| qqq_lower_lev | trend_only | 0 | 10/11 | 21.49% | -52.20% | 0.789 | 0.412 | 66.8% | 82.8% | 1.31 |
| qqq_lower_lev | trend_only | 1 | 10/11 | 21.32% | -52.12% | 0.787 | 0.409 | 66.8% | 82.8% | 2.63 |
| qqq_lower_lev | trend_only | 5 | 10/11 | 21.32% | -52.31% | 0.793 | 0.408 | 66.8% | 82.8% | 2.13 |
| qqq_top | trend_only | 4 | 10/11 | 23.62% | -58.23% | 0.788 | 0.406 | 66.8% | 82.8% | 2.63 |
| qqq_top | trend_only | 3 | 10/11 | 23.62% | -58.27% | 0.787 | 0.405 | 66.8% | 82.8% | 2.63 |

Best binary baseline (qqq_alt_vol): WF 7/11, CAGR 18.32%, MDD -42.80%, Sharpe 0.725, Calmar 0.428.

## Phase Verdict

| Question | Verdict |
|---|---|
| SPY: GTT macro gate beats binary on WF consistency? | Yes (14/17 vs 12/17). |
| QQQ: GTT macro gate beats binary on WF consistency? | Yes (10/11 vs 7/11). |
| Screen successes? | 0/2. |
| Did we promote anything? | No - diagnostic only. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
