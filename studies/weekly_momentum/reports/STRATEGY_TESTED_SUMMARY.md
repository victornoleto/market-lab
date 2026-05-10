# Weekly Momentum Tested Strategy Summary

## Verdict

No weekly-momentum variant is deployable. The best current research lead is `lb80/k5/SMA250` over approximate PIT S&P 500 membership, but it fails DSR under the conservative 200-trial penalty and still depends on imperfect PIT/delisted coverage `[advances_fin_ml, p.273-275]`.

The study should pause broad sweeping. The next useful action is paid survivorship-free/PIT data or a delisting-aware reconstruction, then rerunning only the frozen `lb80/k5/SMA200-250` candidates `[advances_fin_ml, p.208-211]`.

Phase 4 completed the Tiingo data-validation path with `PHASE4_REPORT.md`: online backfill raised expanded S&P 500 coverage to 745/769 tickers and 240/260 likely removed/renamed names, then an expanded-cache PIT rerun weakened both frozen `lb80/k5` leads. They still beat SPY on full-period CAGR but have lower Sharpe than SPY and fail DSR/bootstrap, so the family remains rejected.

## What Was Tested

| stage                     | scope                                                            | result                                                                      | artifact                                 |
|:--------------------------|:-----------------------------------------------------------------|:----------------------------------------------------------------------------|:-----------------------------------------|
| Initial stocks/ETFs       | 4-day weekly momentum, top-1/top-5, cash/defensive, SMA filter   | Stocks looked promising; ETFs weak versus SPY.                              | `STUDY_REPORT.md`, `ETF_STUDY_REPORT.md` |
| Controlled sweeps         | 200 configs each for current S&P 500 and full stock cache        | High current-membership CAGR, but not honest enough for promotion.          | Summary retained in `STUDY_REPORT.md`    |
| Controlled walk-forward   | 3y train / 1y test dynamic selection                             | Attractive before PIT; later rejected under PIT.                            | Summary retained in `STUDY_REPORT.md`    |
| Candidate validation      | Fixed aggressive/balanced plus dynamic WF controls               | Costs, tax, PBO, DSR and bootstrap added; all remain research-only.         | Summary retained in `DEPLOY_CANDIDATES.md` |
| Phase 2 neighborhood      | Fixed-aggressive local sweep and all-stock liquidity filters     | Moved robust island toward `lb80/k5/SMA200-250`; all-stocks failed PBO/DSR. | `PHASE2_REPORT.md`                       |
| Phase 3 PIT approximation | Wikipedia selected-change S&P 500 membership at signal time      | Original lead weakened; `lb80/k5/SMA200-250` survived best but failed DSR.  | `PHASE3_REPORT.md`                       |
| Deep dive                 | DSR decomposition and all possible 1/3/5/10/15/20y entry windows | Standalone PSR is strong; DSR fails once 50+ trials are charged.            | Summary retained in `PHASE3_REPORT.md`   |

## Top-6 Decision-Relevant Comparison

These are not simply the highest-CAGR rows. They include the current leads, the prior promoted lead, dynamic-selection controls and rejected high-CAGR controls so the final conclusion is auditable.

| label                       | source                     | verdict                             | cagr   | mdd     |   sharpe | spy_cagr   |   dsr_p_value | bootstrap_cagr_ci_low_0p1pct   | cost10bps_tax_cagr   | OOS positive   |
|:----------------------------|:---------------------------|:------------------------------------|:-------|:--------|---------:|:-----------|--------------:|:-------------------------------|:---------------------|:---------------|
| PIT lb80/k5/SMA250          | Phase 3 PIT fixed          | best research lead; not deployable  | 26.57% | -32.24% |    1.053 | 14.03%     |         0.165 | 3.16%                          | 4.68%                | 7/9            |
| PIT lb80/k5/SMA200          | Phase 3 PIT fixed          | defensive alternate; not deployable | 25.20% | -28.45% |    1.03  | 14.03%     |         0.185 | 4.95%                          | -1.27%               | 7/9            |
| PIT original lb60/k3/SMA200 | Phase 3 PIT fixed          | rejected lead                       | 14.26% | -38.91% |    0.608 | 14.03%     |         0.728 | -8.47%                         | -8.45%               | 5/9            |
| PIT dynamic WF S&P          | Phase 3 PIT dynamic        | rejected                            | -3.33% | -63.14% |   -0.003 | 14.69%     |         0.997 | -22.34%                        | -30.22%              | 4/9            |
| Current lb60/k10/SMA100     | Current-membership control | survivorship-biased control         | 28.12% | -33.61% |    1.154 | 14.03%     |         0.092 | 4.89%                          | -3.38%               | 7/9            |
| All-stocks dynamic WF       | All-stock control          | statistically rejected control      | 61.83% | -60.52% |    1.2   | 14.69%     |         0.191 | 0.30%                          | 27.19%               | 7/9            |

## Plots

![Top-K equity vs SPY](../plots/final/topk_equity_vs_spy.png)

![Top-K relative equity to SPY](../plots/final/topk_equity_over_spy.png)

![Top-K drawdown vs SPY](../plots/final/topk_drawdown_vs_spy.png)

![Top-K rolling CAGR](../plots/final/topk_rolling_cagr_1_3_5_10y.png)

![Top-K metric bars](../plots/final/topk_metric_bars.png)

![Top-K gate matrix](../plots/final/topk_gate_matrix.png)

## Strategy Notes

- `PIT lb80/k5/SMA250`: Current best PIT approximation lead; fails DSR at 200 trials. Source summary: `reports/PHASE3_REPORT.md`.
- `PIT lb80/k5/SMA200`: Similar edge with lower MDD than SMA250; also fails DSR at 200 trials. Source summary: `reports/PHASE3_REPORT.md`.
- `PIT original lb60/k3/SMA200`: Original aggressive lead weakened materially after PIT membership. Source summary: `reports/PHASE3_REPORT.md`.
- `PIT dynamic WF S&P`: Dynamic selection process collapsed when current-membership bias was removed. Source summary: `reports/PHASE3_REPORT.md`.
- `Current lb60/k10/SMA100`: Useful balanced baseline, but not honest enough for promotion. Source summary: `reports/DEPLOY_CANDIDATES.md`.
- `All-stocks dynamic WF`: High gross CAGR but fails PBO and lacks PIT/delisted coverage. Source summary: `reports/DEPLOY_CANDIDATES.md`.

## Caveats

- Approximate PIT S&P membership is a robustness improvement, not a survivorship-free price feed.
- Current-membership and all-stocks controls remain biased by missing delisted/renamed securities.
- Rolling-window wins are overlapping samples, not independent evidence.
- Tax stress is a proxy based on annual DARF and fixed transaction costs; live brokerage mechanics are not modeled in full.
- ETF replication did not inherit the stock signal edge and needs a separate ETF-specific design.

## Source Reports

- `studies/weekly_momentum/reports/STUDY_REPORT.md`
- `studies/weekly_momentum/reports/DEPLOY_CANDIDATES.md`
- `studies/weekly_momentum/reports/PHASE2_REPORT.md`
- `studies/weekly_momentum/reports/PHASE3_REPORT.md`
- `studies/weekly_momentum/reports/PHASE4_REPORT.md`
- `studies/weekly_momentum/evidence/phase4_tiingo_survivorship_audit/TIINGO_SURVIVORSHIP_AUDIT.md`
- `studies/weekly_momentum/reports/ETF_STUDY_REPORT.md`
