# Phase 7E - Managed-Futures Risk-Off Sleeve (DIAGNOSTIC, LOW-POWER)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

Swaps part of the headline bond/gold risk-off sleeve for managed-futures trend proxies (`DBMFSIM`/`KMLMSIM`, read-only from the RSC sleeve matrix): the MLM-style trend-following risk premium as crisis diversification `[evidence_based_ta, p.380-384, p.398]`, `[risk_parity, p.80-81]`. Risk-on geometry, vol gates, cadence and DARF tax verbatim from the headline bases.

Pre-registered grid: 2 branches x 5 sleeves x 6 lags = 60 rows. **n_trials ledger: 4293 + 60 = 4353.** DECLARED LOW-POWER: DBMFSIM starts 2000-01-03, so every row (controls included) runs on the 2000+ window with only ~6 WF windows; this phase can only yield a weak lead or weak negative.

**Built-in sanity (control sleeve at headline lag vs direct rerun on the same window):** SPY: max abs diff 0; QQQ: max abs diff 0.

## Executive Conclusion

Pre-registered screen (best non-control row per branch by WF beats, tie-break Calmar): **1/2 branches SUCCESS**. Criteria: WF beats strictly above the best control row AND MDD no worse than control AND MDD >= -50%. A SUCCESS is a weak lead only (it does NOT feed 7F - incompatible window). NOT a gate pass, NOT a promotion `[advances_fin_ml, p.208-211]`.


## Screen Result

| Branch | Best MF sleeve | WF vs control | MDD vs control | MDD >= -50% | Screen |
|---|---|---|---|---|---|
| SPY | 100% DBMF / lag 4 | 5/6 vs 4/6 P | -31.55% vs -39.28% P | P | SUCCESS |
| QQQ | 50 base / 50 DBMF / lag 3 | 4/6 vs 5/6 F | -41.86% vs -42.52% P | P | FAIL |

## Plots

| Plot | File |
|---|---|
| Equity/drawdown vs control sleeve | [plots/phase07e_equity_dd.png](plots/phase07e_equity_dd.png) |
| WF beat-count comparison | [plots/phase07e_wf_comparison.png](plots/phase07e_wf_comparison.png) |
| CAGR x MDD frontier by sleeve | [plots/phase07e_frontier.png](plots/phase07e_frontier.png) |

## Top SPY Rows (by WF beats, then Calmar; control rows marked)

| Sleeve | Lag | WF | CAGR | MDD | Sharpe | Calmar | Turnover/y |
|---|---|---|---|---|---|---|---|
| 100% DBMF | 4 | 5/6 | 13.45% | -31.55% | 0.686 | 0.426 | 6.08 |
| 50 base / 50 DBMF | 3 | 5/6 | 13.66% | -32.25% | 0.689 | 0.424 | 6.05 |
| 50 base / 50 MF-blend | 3 | 5/6 | 13.51% | -32.22% | 0.682 | 0.419 | 6.05 |
| 100% DBMF | 3 | 5/6 | 13.34% | -32.21% | 0.678 | 0.414 | 6.46 |
| 70 DBMF / 30 KMLM | 4 | 5/6 | 13.11% | -32.35% | 0.669 | 0.405 | 6.08 |
| 70 DBMF / 30 KMLM | 3 | 5/6 | 13.04% | -32.51% | 0.663 | 0.401 | 6.46 |
| 50 base / 50 DBMF | 4 | 4/6 | 13.70% | -34.89% | 0.694 | 0.393 | 5.69 |
| 50 base / 50 MF-blend | 4 | 4/6 | 13.53% | -35.19% | 0.686 | 0.384 | 5.69 |

## Top QQQ Rows (by WF beats, then Calmar; control rows marked)

| Sleeve | Lag | WF | CAGR | MDD | Sharpe | Calmar | Turnover/y |
|---|---|---|---|---|---|---|---|
| control | 3 | 5/6 | 15.29% | -42.52% | 0.660 | 0.360 | 5.70 |
| control | 0 | 5/6 | 15.30% | -42.56% | 0.655 | 0.359 | 2.85 |
| control | 5 | 5/6 | 15.04% | -45.36% | 0.658 | 0.332 | 4.33 |
| control | 4 | 5/6 | 15.10% | -45.74% | 0.657 | 0.330 | 5.39 |
| 50 base / 50 DBMF | 3 | 4/6 | 14.86% | -41.86% | 0.657 | 0.355 | 5.70 |
| 50 base / 50 MF-blend | 3 | 4/6 | 14.77% | -41.93% | 0.653 | 0.352 | 5.70 |
| 50 base / 50 DBMF | 5 | 4/6 | 14.63% | -41.59% | 0.655 | 0.352 | 4.33 |
| 50 base / 50 DBMF | 4 | 4/6 | 14.56% | -41.51% | 0.650 | 0.351 | 5.39 |

## Phase Verdict

| Question | Verdict |
|---|---|
| SPY: MF sleeve beats control on WF without worse MDD? | Yes (5/6 vs 4/6; MDD -31.55% vs -39.28%). |
| QQQ: MF sleeve beats control on WF without worse MDD? | No (4/6 vs 5/6; MDD -41.86% vs -42.52%). |
| Screen successes? | 1/2 (low-power window). |
| Did we promote anything? | No - diagnostic only. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
