# Unstacked Equity + Diversifier Grid

Status: research-only diagnostic. No deployment, paper-trade label or mandate change.

## Summary

- Testfol.io assets/custom tickers were downloaded one by one; raw payloads/responses live in `studies/return_stacked_core/us_core/unstacked_equity_diversifier_grid/raw`.
- Asset cache span after outer join: `1885-03-20..2026-06-17`.
- Grid: target LETF leverage `2.00..3.00` step `0.05`; diversifier simplex step `10%`; monthly rebalance.
- Best rank-fitness screen row: `kmlm_long` -> **33.33% UPRO-like / 6.67% GOLD / 20% ZROZ / 40% KMLM**, CAGR `13.69%`, MDD `-45.61%`, Sharpe `0.830`, Calmar `0.300`.
- The best row's scenario PBO is `0.480` (`pass`), so it is a screen result, not a promoted allocation.

## Verdict

The unstacked SSO/UPRO structure is a useful SPY-relative diagnostic, but it does **not** improve the current RSC-style risk/return profile. The closest user-style 1988+ row (`user_P4`) has CAGR `13.38%` and MDD `-46.65%`, but only `0.70x` terminal wealth versus the RSC-like reference on the common window. The RSC-like reference is CAGR `12.25%`, MDD `-30.76%`, Sharpe `0.829`. Among comparable 2000+ grids, the best screen row is `kmlm_dbmf_split_2000` at CAGR `10.57%` and MDD `-46.08%`, with PBO `0.794` (`reject`). The only scenario with PBO below 0.5 is `kmlm_long`, but it uses the KMLM-only 1988+ window and fails the WF positive-window threshold. Therefore the robust action remains: keep this as a diagnostic, not as an RSC replacement or mandate change `[advances_fin_ml, p.208-211]`, `[testing_tuning, p.327-335]`. CTA is not ranked in the primary grid because there is no comparable long-history Testfol.io simulated CTA sleeve; KMLM/DBMF are the long-history MF proxies used here.

The later fixed `25% ZROZ / 25% RSST70_30 / 30% GDE` proposal is more interesting than the plain unstacked grid because GDE/RSST supply embedded gold and MF while leaving room for a small LETF completion sleeve. The exact 100%-equity version with `16% UPRO + 4% ZROZ` reaches CAGR `12.40%`, MDD `-45.37%`, terminal `1.04x` vs RSC. The clean `16% UPRO + 4% CASH` version is CAGR `12.17%`, MDD `-46.18%`, terminal `0.98x` vs RSC. The highest CAGR variant among the 4%-top-up choices is `+GDE`, CAGR `12.70%`, MDD `-47.56%`, terminal `1.11x` vs RSC, but it lifts effective equity above 100%. The lower-vol `20% SSO` version gives CAGR `12.10%`, MDD `-41.64%`, terminal `0.97x` vs RSC. The fully allocated `20% UPRO` version is a different risk budget: effective equity `112.00%`, CAGR `12.57%`, MDD `-51.92%`, terminal `1.08x` vs RSC, with worse Sharpe/Calmar than the 16% UPRO variants. The 20%-cash base is defensive (CAGR `10.20%`, MDD `-22.73%`) but gives up too much terminal wealth. Net: the construction is a viable fixed reference row, but the RSC-like reference still has the superior drawdown/Sharpe/Calmar trade-off for this repo's current objective `[systematic_trading, p.185-188]`.

## Method

Each equity carrier is built from the user's Testfol.io custom tickers `SPYSIM?L=2&E=0.91` and `SPYSIM?L=3&E=0.91`. For a target internal LETF leverage `L` in `[2,3]`, capital weights are `(3-L)/L` in SSO-like and `(L-2)/L` in UPRO-like, giving effective equity beta `2*w_SSO + 3*w_UPRO = 1.0`. The leftover capital `1 - 1/L` is allocated across cash, gold, ZROZ and MF sleeves. LETF daily reset and cost caveats follow `[leverage_for_the_long_run, p.13]`; monthly rebalancing and robustness diagnostics follow `[systematic_trading, p.185-188]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Scenario Summary

| scenario | n_configs | top_portfolio | top_cagr | top_mdd | top_sharpe | top_calmar | pbo | pbo_gate | wf_positive_windows | wf_required_windows | wf_positive_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kmlm_long | 6006 | 33.33% UPRO-like / 6.67% GOLD / 20% ZROZ / 40% KMLM | 13.69% | -45.61% | 0.830 | 0.300 | 0.480 | pass | 11.0 | 12.0 | FAIL |
| dbmf_2000 | 6006 | 33.33% UPRO-like / 20% GOLD / 33.33% ZROZ / 13.33% DBMF | 11.01% | -49.61% | 0.664 | 0.222 | 0.714 | reject | 7.0 | 7.0 | PASS |
| mf_blend_2000 | 6006 | 33.33% UPRO-like / 20% GOLD / 26.67% ZROZ / 20% MF70/30 | 10.92% | -49.17% | 0.669 | 0.222 | 0.730 | reject | 7.0 | 7.0 | PASS |
| kmlm_dbmf_split_2000 | 21021 | 33.33% UPRO-like / 20% GOLD / 20% ZROZ / 26.67% KMLM | 10.57% | -46.08% | 0.665 | 0.229 | 0.794 | reject | 7.0 | 7.0 | PASS |

## Named References

| name | weights | effective_equity | effective_mf | effective_gold | effective_zroz | cagr | mdd | sharpe | calmar | terminal_vs_spy | terminal_vs_rsc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SPY_yearly | 100% SPY | 100.00% | 0.00% | 0.00% | 0.00% | 9.64% | -83.65% | 0.617 | 0.115 | 1.00x | 0.39x |
| user_P2_50_SSO_50_ZROZ | 50% SSO-like / 50% ZROZ | 100.00% | 0.00% | 0.00% | 50.00% | 10.41% | -62.67% | 0.575 | 0.166 | 0.93x | 0.54x |
| user_P3_34_UPRO_66_ZROZ | 34% UPRO-like / 66% ZROZ | 102.00% | 0.00% | 0.00% | 66.00% | 10.22% | -75.39% | 0.525 | 0.136 | 0.84x | 0.57x |
| user_P3_exact_1x_UPRO_ZROZ | 33.33% UPRO-like / 66.67% ZROZ | 100.00% | 0.00% | 0.00% | 66.67% | 10.16% | -75.52% | 0.523 | 0.135 | 0.81x | 0.56x |
| user_P4_UPRO_ZROZ_KMLM_GOLD | 33.34% UPRO-like / 22.22% ZROZ / 22.22% KMLM / 22.22% GOLD | 100.02% | 22.22% | 22.22% | 22.22% | 13.38% | -46.65% | 0.803 | 0.287 | 1.88x | 0.70x |
| user_P5_SSO_ZROZ_KMLM_GOLD | 50% SSO-like / 16.66% ZROZ / 16.67% KMLM / 16.67% GOLD | 100.00% | 16.67% | 16.67% | 16.66% | 12.94% | -48.29% | 0.785 | 0.268 | 1.63x | 0.62x |
| proposal_16UPRO_plus_GDE | 25% ZROZ / 25% RSST70/30 / 34% GDE / 16% UPRO-like | 103.60% | 25.00% | 30.60% | 25.00% | 12.70% | -47.56% | 0.705 | 0.267 | 2.84x | 1.11x |
| proposal_20UPRO | 25% ZROZ / 25% RSST70/30 / 30% GDE / 20% UPRO-like | 112.00% | 25.00% | 27.00% | 25.00% | 12.57% | -51.92% | 0.673 | 0.242 | 2.76x | 1.08x |
| proposal_16UPRO_split_4pct | 26.33% ZROZ / 26.33% RSST70/30 / 31.34% GDE / 16% UPRO-like | 102.54% | 26.33% | 28.21% | 26.33% | 12.54% | -46.80% | 0.706 | 0.268 | 2.73x | 1.07x |
| proposal_16UPRO_plus_RSST | 25% ZROZ / 29% RSST70/30 / 30% GDE / 16% UPRO-like | 104.00% | 29.00% | 27.00% | 25.00% | 12.50% | -47.47% | 0.699 | 0.263 | 2.71x | 1.06x |
| proposal_16UPRO_plus_ZROZ | 29% ZROZ / 25% RSST70/30 / 30% GDE / 16% UPRO-like | 100.00% | 25.00% | 27.00% | 29.00% | 12.40% | -45.37% | 0.711 | 0.273 | 2.64x | 1.04x |
| RSC_like_35_40_25 | 35% GDE / 40% RSST70/30 / 25% ZROZ | 71.50% | 40.00% | 31.50% | 25.00% | 12.25% | -30.76% | 0.829 | 0.398 | 2.55x | 1.00x |
| proposal_16UPRO_4CASH | 25% ZROZ / 25% RSST70/30 / 30% GDE / 16% UPRO-like / 4% CASH | 100.00% | 25.00% | 27.00% | 25.00% | 12.17% | -46.18% | 0.704 | 0.264 | 2.51x | 0.98x |
| proposal_20SSO | 25% ZROZ / 25% RSST70/30 / 30% GDE / 20% SSO-like | 92.00% | 25.00% | 27.00% | 25.00% | 12.10% | -41.64% | 0.731 | 0.291 | 2.47x | 0.97x |
| proposal_base_25Z_25R_30G_20CASH | 25% ZROZ / 25% RSST70/30 / 30% GDE / 20% CASH | 52.00% | 25.00% | 27.00% | 25.00% | 10.20% | -22.73% | 0.879 | 0.449 | 1.57x | 0.61x |

## Best CAGR By MDD Floor

| scenario | mdd_floor | portfolio | cagr | mdd | sharpe | calmar |
| --- | --- | --- | --- | --- | --- | --- |
| kmlm_long | -50.00% | 33.33% UPRO-like / 40% ZROZ / 26.67% KMLM | 13.90% | -43.69% | 0.798 | 0.318 |
| kmlm_dbmf_split_2000 | -50.00% | 33.33% UPRO-like / 40% GOLD / 13.33% ZROZ / 13.33% KMLM | 11.52% | -49.79% | 0.675 | 0.231 |
| dbmf_2000 | -50.00% | 33.33% UPRO-like / 33.33% GOLD / 33.33% ZROZ | 11.51% | -49.76% | 0.671 | 0.231 |
| mf_blend_2000 | -50.00% | 33.33% UPRO-like / 33.33% GOLD / 33.33% ZROZ | 11.51% | -49.76% | 0.671 | 0.231 |
| kmlm_long | -60.00% | 33.33% UPRO-like / 40% ZROZ / 26.67% KMLM | 13.90% | -43.69% | 0.798 | 0.318 |
| dbmf_2000 | -60.00% | 33.33% UPRO-like / 66.67% GOLD | 12.41% | -54.78% | 0.646 | 0.226 |
| kmlm_dbmf_split_2000 | -60.00% | 33.33% UPRO-like / 66.67% GOLD | 12.41% | -54.78% | 0.646 | 0.226 |
| mf_blend_2000 | -60.00% | 33.33% UPRO-like / 66.67% GOLD | 12.41% | -54.78% | 0.646 | 0.226 |

## Interpretation

This study answers a narrower question than RSC: can embedded SSO/UPRO capital efficiency carry 100% equity beta while diversifiers use the unencumbered capital? The screen can produce attractive SPY-relative rows, but any argmax must be discounted when PBO rejects or WF selection is unstable. Compare fixed/simple rows against the named references and the RSC-like row rather than treating the top grid row as a winner.

## Artifacts

- Asset curves: `studies/return_stacked_core/us_core/unstacked_equity_diversifier_grid/results/asset_equity_curves.csv`.
- Reference metrics: `studies/return_stacked_core/us_core/unstacked_equity_diversifier_grid/results/named_references.csv`.
- Grid summary: `studies/return_stacked_core/us_core/unstacked_equity_diversifier_grid/results/grid_summary.csv`.
- Scenario grids: `studies/return_stacked_core/us_core/unstacked_equity_diversifier_grid/results/grid_<scenario>.csv`.
- PBO summary: `studies/return_stacked_core/us_core/unstacked_equity_diversifier_grid/results/pbo_monthly_summary.csv`.
- Walk-forward windows: `studies/return_stacked_core/us_core/unstacked_equity_diversifier_grid/results/walk_forward_windows.csv`.
