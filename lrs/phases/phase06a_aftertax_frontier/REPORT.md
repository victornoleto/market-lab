# Phase 6A - After-Tax Frontier vs 3 Benchmarks (DIAGNOSTIC, REVISED)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

REVISION (2026-06-09, user correction): static portfolios rebalance with new contributions (aportes), not with sells - so the core pays NO intermediate DARF; only final liquidation is taxed. Tax model per leg: core = gross monthly rebalance + final 15% DARF; LRS satellites = full `AnnualDarfEngine` (the weekly rotation genuinely sells); B&H benchmarks = final DARF only; mixes = two-account convention with contribution-funded re-truing (`tax_method` column) `[testing_tuning, p.327-335]`. Part 2 simulates the user's real-world setup: 10k start + 1k/month, each month buying ONLY the most-underweight component (minimal trades), no sells, final DARF on gross components `[systematic_trading, p.185-188]`.

n_trials ledger: +21 (Part 2 re-prices the same mixes: +0) -> cumulative LRS lineage **4005** `[advances_fin_ml, p.273-275]`.

## Executive Conclusion

Part 1 benchmarks (after-tax, 2000-01-04..2026-05-21): RSC-US 35/40/25 CAGR 11.74% / MDD -30.76% / Calmar 0.382; SSO B&H 9.01% / -88.27% / 0.102; SPY B&H 7.81% / -55.14% / 0.142.

Constraint-passing mixes (MDD >= -50%): **18/18**. Mixes beating the RSC core on BOTH CAGR and Calmar: **13**.

Part 1 top-ranked mix (Calmar, then CAGR): `mix_lrs_spy_headline_20` - CAGR 12.12% (+0.38pp vs RSC), MDD -25.18% (+5.58pp vs RSC), Calmar 0.481 (RSC 0.382).

Part 2 (contribution sim): top IRR `mix_t3d_k2_saved_30` at 17.66% vs RSC 13.72%; terminal net $6,004,266 vs $2,962,366 on $326,000 contributed.

This is a decision input for the user. Nothing here is promoted: every LRS satellite failed (or never ran) the mandate gate suite, and any promotion claim requires the full SS5 suite with honest n_trials >= 4005.


## Plots

| Plot | File |
|---|---|
| Frontier (CAGR x MDD) | [plots/phase06a_frontier.png](plots/phase06a_frontier.png) |
| After-tax equity | [plots/phase06a_equity.png](plots/phase06a_equity.png) |
| Underwater chart | [plots/phase06a_underwater.png](plots/phase06a_underwater.png) |
| Crisis windows | [plots/phase06a_crisis_bars.png](plots/phase06a_crisis_bars.png) |
| Contribution sim IRR | [plots/phase06a_contribution_irr.png](plots/phase06a_contribution_irr.png) |

## Part 1 - Ranked Table (constraint-passing mixes + benchmarks)

| Candidate | w | CAGR | MDD | Sharpe | Calmar | UW | Recovery | vs RSC CAGR | vs RSC MDD | vs SSO CAGR | vs SPY CAGR | Tax | OK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mix_lrs_spy_headline_20 | 20% | 12.12% | -25.18% | 0.815 | 0.481 | 90% | 797 | +0.38pp | +5.58pp | +3.11pp | +4.32pp | two_account_contrib | yes |
| mix_lrs_spy_headline_25 | 25% | 12.20% | -25.82% | 0.812 | 0.472 | 90% | 798 | +0.45pp | +4.94pp | +3.18pp | +4.39pp | two_account_contrib | yes |
| mix_lrs_spy_headline_15 | 15% | 12.04% | -25.61% | 0.813 | 0.470 | 90% | 794 | +0.30pp | +5.15pp | +3.03pp | +4.23pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_25 | 25% | 12.68% | -27.05% | 0.812 | 0.469 | 91% | 799 | +0.93pp | +3.71pp | +3.66pp | +4.87pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_30 | 30% | 12.83% | -27.67% | 0.805 | 0.464 | 90% | 799 | +1.09pp | +3.09pp | +3.82pp | +5.02pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_20 | 20% | 12.51% | -27.06% | 0.816 | 0.462 | 90% | 798 | +0.77pp | +3.70pp | +3.50pp | +4.70pp | two_account_contrib | yes |
| mix_lrs_spy_headline_30 | 30% | 12.26% | -26.68% | 0.807 | 0.459 | 90% | 799 | +0.52pp | +4.08pp | +3.25pp | +4.45pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_15 | 15% | 12.34% | -27.35% | 0.815 | 0.451 | 90% | 797 | +0.59pp | +3.41pp | +3.32pp | +4.53pp | two_account_contrib | yes |
| mix_lrs_spy_headline_10 | 10% | 11.95% | -27.12% | 0.809 | 0.441 | 90% | 793 | +0.21pp | +3.64pp | +2.94pp | +4.14pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_10 | 10% | 12.15% | -28.23% | 0.811 | 0.430 | 90% | 794 | +0.41pp | +2.53pp | +3.14pp | +4.34pp | two_account_contrib | yes |
| mix_lrs_spy_headline_05 | 5% | 11.85% | -28.96% | 0.801 | 0.409 | 90% | 679 | +0.11pp | +1.80pp | +2.84pp | +4.04pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_05 | 5% | 11.95% | -29.50% | 0.802 | 0.405 | 90% | 792 | +0.21pp | +1.26pp | +2.94pp | +4.14pp | two_account_contrib | yes |
| mix_t3d_k2_saved_05 | 5% | 12.15% | -30.19% | 0.801 | 0.403 | 90% | 805 | +0.41pp | +0.57pp | +3.14pp | +4.34pp | two_account_contrib | yes |
| bench_rsc | 0% | 11.74% | -30.76% | 0.789 | 0.382 | 90% | 679 | +0.00pp | +0.00pp | +2.73pp | +3.93pp | final_darf_only | yes |
| mix_t3d_k2_saved_10 | 10% | 12.53% | -33.47% | 0.805 | 0.375 | 90% | 913 | +0.79pp | -2.70pp | +3.52pp | +4.72pp | two_account_contrib | yes |
| mix_t3d_k2_saved_15 | 15% | 12.89% | -37.52% | 0.801 | 0.344 | 90% | 943 | +1.15pp | -6.75pp | +3.88pp | +5.08pp | two_account_contrib | yes |
| mix_t3d_k2_saved_20 | 20% | 13.22% | -41.39% | 0.791 | 0.319 | 90% | 950 | +1.48pp | -10.63pp | +4.21pp | +5.41pp | two_account_contrib | yes |
| mix_t3d_k2_saved_25 | 25% | 13.52% | -45.11% | 0.777 | 0.300 | 90% | 1164 | +1.78pp | -14.35pp | +4.51pp | +5.71pp | two_account_contrib | yes |
| mix_t3d_k2_saved_30 | 30% | 13.80% | -48.65% | 0.760 | 0.284 | 90% | 1186 | +2.06pp | -17.89pp | +4.79pp | +5.99pp | two_account_contrib | yes |

## Part 1 - Full Table (including constraint violators)

| Candidate | w | CAGR | MDD | Sharpe | Calmar | UW | Recovery | vs RSC CAGR | vs RSC MDD | vs SSO CAGR | vs SPY CAGR | Tax | OK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mix_lrs_spy_headline_20 | 20% | 12.12% | -25.18% | 0.815 | 0.481 | 90% | 797 | +0.38pp | +5.58pp | +3.11pp | +4.32pp | two_account_contrib | yes |
| mix_lrs_spy_headline_25 | 25% | 12.20% | -25.82% | 0.812 | 0.472 | 90% | 798 | +0.45pp | +4.94pp | +3.18pp | +4.39pp | two_account_contrib | yes |
| mix_lrs_spy_headline_15 | 15% | 12.04% | -25.61% | 0.813 | 0.470 | 90% | 794 | +0.30pp | +5.15pp | +3.03pp | +4.23pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_25 | 25% | 12.68% | -27.05% | 0.812 | 0.469 | 91% | 799 | +0.93pp | +3.71pp | +3.66pp | +4.87pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_30 | 30% | 12.83% | -27.67% | 0.805 | 0.464 | 90% | 799 | +1.09pp | +3.09pp | +3.82pp | +5.02pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_20 | 20% | 12.51% | -27.06% | 0.816 | 0.462 | 90% | 798 | +0.77pp | +3.70pp | +3.50pp | +4.70pp | two_account_contrib | yes |
| mix_lrs_spy_headline_30 | 30% | 12.26% | -26.68% | 0.807 | 0.459 | 90% | 799 | +0.52pp | +4.08pp | +3.25pp | +4.45pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_15 | 15% | 12.34% | -27.35% | 0.815 | 0.451 | 90% | 797 | +0.59pp | +3.41pp | +3.32pp | +4.53pp | two_account_contrib | yes |
| mix_lrs_spy_headline_10 | 10% | 11.95% | -27.12% | 0.809 | 0.441 | 90% | 793 | +0.21pp | +3.64pp | +2.94pp | +4.14pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_10 | 10% | 12.15% | -28.23% | 0.811 | 0.430 | 90% | 794 | +0.41pp | +2.53pp | +3.14pp | +4.34pp | two_account_contrib | yes |
| mix_lrs_spy_headline_05 | 5% | 11.85% | -28.96% | 0.801 | 0.409 | 90% | 679 | +0.11pp | +1.80pp | +2.84pp | +4.04pp | two_account_contrib | yes |
| mix_lrs_qqq_voltarget_05 | 5% | 11.95% | -29.50% | 0.802 | 0.405 | 90% | 792 | +0.21pp | +1.26pp | +2.94pp | +4.14pp | two_account_contrib | yes |
| mix_t3d_k2_saved_05 | 5% | 12.15% | -30.19% | 0.801 | 0.403 | 90% | 805 | +0.41pp | +0.57pp | +3.14pp | +4.34pp | two_account_contrib | yes |
| bench_rsc | 0% | 11.74% | -30.76% | 0.789 | 0.382 | 90% | 679 | +0.00pp | +0.00pp | +2.73pp | +3.93pp | final_darf_only | yes |
| mix_t3d_k2_saved_10 | 10% | 12.53% | -33.47% | 0.805 | 0.375 | 90% | 913 | +0.79pp | -2.70pp | +3.52pp | +4.72pp | two_account_contrib | yes |
| mix_t3d_k2_saved_15 | 15% | 12.89% | -37.52% | 0.801 | 0.344 | 90% | 943 | +1.15pp | -6.75pp | +3.88pp | +5.08pp | two_account_contrib | yes |
| mix_t3d_k2_saved_20 | 20% | 13.22% | -41.39% | 0.791 | 0.319 | 90% | 950 | +1.48pp | -10.63pp | +4.21pp | +5.41pp | two_account_contrib | yes |
| mix_t3d_k2_saved_25 | 25% | 13.52% | -45.11% | 0.777 | 0.300 | 90% | 1164 | +1.78pp | -14.35pp | +4.51pp | +5.71pp | two_account_contrib | yes |
| mix_t3d_k2_saved_30 | 30% | 13.80% | -48.65% | 0.760 | 0.284 | 90% | 1186 | +2.06pp | -17.89pp | +4.79pp | +5.99pp | two_account_contrib | yes |
| bench_spy | 0% | 7.81% | -55.14% | 0.484 | 0.142 | 91% | 1654 | -3.93pp | -24.38pp | -1.20pp | +0.00pp | final_darf_only | NO |
| bench_sso | 0% | 9.01% | -88.27% | 0.417 | 0.102 | 94% | 3589 | -2.73pp | -57.51pp | +0.00pp | +1.20pp | final_darf_only | NO |

## Part 1 - Crisis Windows (pre-registered dates)

| Candidate | Dotcom ret/MDD | GFC ret/MDD | COVID ret/MDD | 2022 ret/MDD |
|---|---|---|---|---|
| bench_rsc | -21.49% / -26.09% | -22.30% / -30.76% | -21.83% / -24.85% | -20.31% / -21.87% |
| bench_sso | -78.76% / -79.01% | -84.08% / -84.37% | -58.43% / -58.82% | -45.78% / -46.40% |
| bench_spy | -47.06% / -47.38% | -54.72% / -55.14% | -33.38% / -33.69% | -24.00% / -24.44% |
| mix_lrs_qqq_voltarget_25 | -20.96% / -25.16% | -18.79% / -27.05% | -22.68% / -26.84% | -24.56% / -24.72% |
| mix_lrs_spy_headline_20 | -20.62% / -24.84% | -18.22% / -24.32% | -21.22% / -25.18% | -23.27% / -23.23% |
| mix_t3d_k2_saved_05 | -25.62% / -29.24% | -23.67% / -30.19% | -22.75% / -26.06% | -22.93% / -23.46% |

## Part 2 - Contribution Simulation (10k + 1k/month, buy-most-underweight, no sells)

*Path MDD is mechanically softened by monthly inflows - compare candidates against each other, not against Part 1 MDDs. Weight dev = mean absolute deviation from target weights (quality of buy-only rebalancing).

| Candidate | w | Terminal net | Contributed | Wealth ratio | IRR (annual) | Final tax | Path MDD* | Weight dev |
|---|---|---|---|---|---|---|---|---|
| mix_t3d_k2_saved_30 | 30% | $6,004,266 | $326,000 | 18.42x | 17.66% | $364,750 | -50.32% | 7.25% |
| mix_t3d_k2_saved_25 | 25% | $5,514,740 | $326,000 | 16.92x | 17.19% | $381,761 | -47.67% | 7.10% |
| mix_t3d_k2_saved_20 | 20% | $5,030,528 | $326,000 | 15.43x | 16.68% | $396,391 | -44.53% | 6.85% |
| mix_t3d_k2_saved_15 | 15% | $4,562,659 | $326,000 | 14.00x | 16.13% | $413,218 | -40.61% | 6.36% |
| bench_sso | 0% | $4,306,415 | $326,000 | 13.21x | 15.81% | $702,426 | -80.78% | 0.00% |
| mix_t3d_k2_saved_10 | 10% | $3,977,830 | $326,000 | 12.20x | 15.37% | $430,223 | -34.53% | 5.22% |
| mix_lrs_qqq_voltarget_30 | 30% | $3,867,315 | $326,000 | 11.86x | 15.21% | $321,889 | -28.36% | 3.51% |
| mix_lrs_qqq_voltarget_25 | 25% | $3,740,433 | $326,000 | 11.47x | 15.03% | $346,051 | -27.88% | 3.52% |
| mix_lrs_qqq_voltarget_20 | 20% | $3,586,025 | $326,000 | 11.00x | 14.79% | $369,298 | -27.26% | 3.38% |
| mix_lrs_qqq_voltarget_15 | 15% | $3,434,861 | $326,000 | 10.54x | 14.55% | $394,138 | -26.64% | 3.26% |
| mix_t3d_k2_saved_05 | 5% | $3,386,454 | $326,000 | 10.39x | 14.47% | $451,220 | -28.32% | 3.66% |
| mix_lrs_qqq_voltarget_10 | 10% | $3,268,574 | $326,000 | 10.03x | 14.27% | $419,197 | -25.88% | 3.07% |
| mix_lrs_spy_headline_30 | 30% | $3,129,059 | $326,000 | 9.60x | 14.03% | $332,636 | -25.68% | 2.65% |
| mix_lrs_qqq_voltarget_05 | 5% | $3,099,142 | $326,000 | 9.51x | 13.97% | $442,676 | -26.51% | 2.91% |
| mix_lrs_spy_headline_25 | 25% | $3,082,929 | $326,000 | 9.46x | 13.94% | $352,148 | -25.44% | 2.65% |
| mix_lrs_spy_headline_20 | 20% | $3,039,780 | $326,000 | 9.32x | 13.86% | $373,292 | -25.21% | 2.66% |
| mix_lrs_spy_headline_15 | 15% | $3,033,974 | $326,000 | 9.31x | 13.85% | $398,469 | -25.11% | 2.74% |
| mix_lrs_spy_headline_10 | 10% | $2,997,173 | $326,000 | 9.19x | 13.78% | $420,978 | -25.04% | 2.76% |
| mix_lrs_spy_headline_05 | 5% | $2,974,302 | $326,000 | 9.12x | 13.74% | $444,772 | -26.26% | 2.85% |
| bench_rsc | 0% | $2,962,366 | $326,000 | 9.09x | 13.72% | $465,241 | -27.55% | 3.76% |
| bench_spy | 0% | $1,751,962 | $326,000 | 5.37x | 10.72% | $251,640 | -48.17% | 0.00% |

## Phase Verdict

| Question | Verdict |
|---|---|
| Any mix with MDD >= -50% beating RSC on CAGR AND Calmar (Part 1)? | Yes (13). |
| Best risk-adjusted candidate (Part 1)? | mix_lrs_spy_headline_20. |
| Best money-weighted candidate (Part 2)? | mix_t3d_k2_saved_30 (17.66% IRR). |
| Did we promote anything? | No - decision table only; user chooses, gates still mandatory. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |
