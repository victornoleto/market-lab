# MEMORY - spy_beater_hunt_v2 Compact Closed State

Status: **compacted no-winner reference**.

This study completed 10 iterations and found no winner. The original autonomous
loop files and per-iteration directories were removed from the active tree on
2026-06-03 after their conclusions were consolidated here and in
`reports/STRATEGY_COMPARISON.md`.

Capital allocation is unchanged: 100% Plano C per `docs/investment-mandate.md`.
No result here authorizes deployment or paper trading.

## Final Summary

| Item | Value |
|---|---|
| Iterations | `10` |
| Cumulative trials | `20` |
| Winners | `0` |
| Best economic lead | Iter 006 `clenow_relmom_90d_3x_cash` |
| Main blocker | Bootstrap 99.9% lower-bound and temporal robustness gates |
| Latest lead | Iter 010 `clenow_xasset_top1_cash`: CAGR `11.07%` vs SPY `11.30%`, MDD `-30.29%`, DSR `p=0.00281`, PBO `0.167`, failed economic/WF/OOS/FWD/bootstrap |

## Tested Families

| Iter | Family | Best config | Verdict |
|---:|---|---|---|
| 001 | Infrastructure/bootstrap audit | none | Infrastructure only. |
| 002 | Static SPY/ZROZ/GLD/KMLM diversifier | `static_60_20_10_10` | Failed economic, PBO, WF, OOS, FWD and bootstrap. |
| 003 | Canonical Gayed SPY LRS | `gayed_lrs_sma200_upro_cash` | Strong CAGR, failed bootstrap 99.9%. |
| 004 | Vol-targeted Gayed LRS | `vt_lrs_upro_target25` | Failed WF, FWD and bootstrap. |
| 005 | Carver EWMAC SPY trend | `ewmac_32_128_upro_cash` | Failed economic, DSR, WF, OOS, FWD and bootstrap. |
| 006 | Clenow SPY/QQQ relative momentum | `clenow_relmom_90d_3x_cash` | Best economic lead; failed bootstrap 99.9%. |
| 007 | Vol-scaled relative momentum | `relmom90_3x_vt25_cash` | Failed FWD and bootstrap. |
| 008 | Kaufman KAMA/ER trend | `kama10_2_30_sso_cash` | Failed economic and most gates. |
| 009 | Hirsch/Kaeppel seasonal window | `hirsch_nov_apr_upro_cash` | Beat SPY economically, failed OOS/FWD/bootstrap. |
| 010 | Cross-asset Clenow momentum | `clenow_xasset_top1_cash` | Improved risk, failed economic/WF/OOS/FWD/bootstrap. |

## Reopen Rules

- Use a new literature-grounded mechanism, not a local variant of the failed
  families above.
- Pre-register the hypothesis and trial budget before testing.
- Preserve cumulative DSR/PBO discipline `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.
- Treat CAGR/MDD attractiveness as insufficient without bootstrap/OOS/FWD support
  `[advances_fin_ml, p.196-202]`.
