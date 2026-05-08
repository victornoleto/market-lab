# COPYABILITY_SCOREBOARD — MyFxBook v4 Fase 3b

Diagnostic offline scoring only. No paper/live, no AutoTrade real, no capital allocation, and no threshold changes after ranking.

## Summary

- Universe: `21` audit-only pre-screen GO systems.
- PASS: `4`.
- STOP: `17`.
- Verdict: `TOO_MANY_PASS_REQUIRES_REPORT_REVIEW`.
- Ranking warning: selection across systems is multiple testing / data-mining risk [advances_fin_ml, p.273-275] [evidence_based_ta, p.247-260].

## Table

| system_id | status | score | failed gates | pos months | med trades/mo | cost drag | net pips/trade | top symbol share | live |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 8577442 | PASS | 0.958673 | - | 0.966 | 13.0 | 0.035 | 28.502 | 0.422 | True |
| 1152318 | PASS | 0.940662 | - | 0.897 | 22.5 | 0.061 | 9.142 | 0.527 | True |
| 10067081 | PASS | 0.896255 | - | 1.000 | 294.0 | 0.146 | 5.001 | 0.415 | True |
| 10062918 | PASS | 0.892554 | - | 0.900 | 17.5 | 0.055 | 18.843 | 0.575 | True |
| 10249298 | STOP |  | operational_gap_gt_90d, single_asset_pnl_share_gt_80pct | 0.796 | 5.0 | 0.025 | 46.593 | 1.000 | True |
| 10281851 | STOP |  | single_asset_pnl_share_gt_80pct | 0.897 | 16.0 | 0.030 | 49.788 | 1.000 | True |
| 10563761 | STOP |  | monthly_stability_low, net_expectancy_non_positive_after_2pip_cost | 0.429 | 20.0 | 0.425 | -0.575 | 0.000 | True |
| 10734338 | STOP |  | single_asset_pnl_share_gt_80pct | 0.724 | 21.0 | 0.063 | 17.621 | 1.000 | False |
| 11155858 | STOP |  | single_asset_pnl_share_gt_80pct | 0.885 | 6.0 | 0.154 | 6.452 | 1.000 | True |
| 11206045 | STOP |  | single_asset_pnl_share_gt_80pct | 1.000 | 9.5 | 0.038 | 28.788 | 1.000 | True |
| 11207608 | STOP |  | single_asset_pnl_share_gt_80pct | 0.615 | 16.0 | 0.187 | 2.141 | 1.000 | True |
| 11628637 | STOP |  | single_asset_pnl_share_gt_80pct | 0.750 | 22.0 | 0.044 | 24.586 | 1.000 | True |
| 1407880 | STOP |  | monthly_stability_low, cost_drag_ratio_gte_50pct, net_expectancy_non_positive_after_2pip_cost | 0.000 | 34.0 | 1.669 | -0.802 | 0.000 | False |
| 1612420 | STOP |  | single_asset_pnl_share_gt_80pct | 0.646 | 11.0 | 0.111 | 16.061 | 1.000 | False |
| 2421356 | STOP |  | single_asset_pnl_share_gt_80pct | 0.990 | 17.0 | 0.001 | 2010.091 | 1.000 | False |
| 6541963 | STOP |  | single_asset_pnl_share_gt_80pct | 0.988 | 24.0 | 0.001 | 2047.220 | 1.000 | False |
| 8647517 | STOP |  | single_asset_pnl_share_gt_80pct | 0.814 | 17.0 | 0.009 | 157.958 | 1.000 | True |
| 9375654 | STOP |  | single_asset_pnl_share_gt_80pct | 0.870 | 17.0 | 0.031 | 41.536 | 1.000 | True |
| 9830783 | STOP |  | monthly_stability_low, cost_drag_ratio_gte_50pct, net_expectancy_non_positive_after_2pip_cost | 0.000 | 78.0 | 1.110 | -1.440 | 0.000 | True |
| 9841939 | STOP |  | monthly_stability_low, cost_drag_ratio_gte_50pct, net_expectancy_non_positive_after_2pip_cost | 0.000 | 222.5 | 1.197 | -1.127 | 0.000 | True |
| 9912554 | STOP |  | monthly_stability_low, operational_gap_gt_90d, trade_frequency_outside_5_300, single_asset_pnl_share_gt_80pct | 0.438 | 0.0 | 0.030 | 48.295 | 1.000 | True |

## Conclusion

4 systems passed the gates, above the planned 1-3 shortlist. A report task must review concentration/multiple-testing risk without changing thresholds.

Citations: MCPT [evidence_based_ta, p.325-328]; PSR [advances_fin_ml, p.260-263]; ranking/multiple-testing [advances_fin_ml, p.273-275]; copy cost/slippage [systematic_trading, p.182-197]; data-mining risk [evidence_based_ta, p.247-260].
