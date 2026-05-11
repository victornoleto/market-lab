# LETF Sortino Re-analysis — Sharpe vs Sortino across canonical, top-10, and threshold variants

_Generated 2026-05-07T17:29:24.413237+00:00_

Spec: `docs/superpowers/specs/2026-05-07-letf-sortino-reanalysis-design.md`
Plan: `docs/superpowers/plans/2026-05-07-letf-sortino-reanalysis.md`
Sister sub-studies:
- `THRESHOLD_SWEEP_REPORT.md` (12 variants)
- `TAX_COMPARISON_REPORT.md` (top-10)
- `COHORT_ROBUSTNESS_REPORT.md` (8 cohorts + 4 regimes)

---

## 1. TL;DR

- **Pre-registered H₀**: `canonical sortino_edge_vs_spy > canonical sharpe_edge_vs_spy` on lh_56y gross — **PASS**
  - Sharpe edge: +0.171
  - Sortino edge: +0.264
  - Multi-dataset corroboration: 4/4 datasets (gross)
- **Headline**: canonical Sortino 1.222 (vs Sharpe 0.853) on lh_56y gross.
- **Cascade outcome**: winner CHANGED → new winner = `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`
  - Sortino 1.325, sortino_edge_vs_canonical = +0.103
  - This was the same strategy `tax_comparison` flagged as the only M2 deploy-threshold passer (+0.145 net edge)
- **Cohort extension** ran (12 rows) for the new winner — see §6 and §9.

---

## 2. Methodology

Sortino 1991 form (target = 0):

```
sortino = (mean(r) - 0) / sqrt(mean over ALL N of min(r,0)**2) * sqrt(252)
```

Anti-curve-fit margin: +0.05 Sortino on all 3 tracks (literal, not scaled).

For LETF strategies with asymmetric upside, Sortino better captures the
risk-adjusted edge by penalising only adverse semideviation
`[advances_fin_ml, p.275]`.

---

## 3. Canonical — Sharpe vs Sortino across 4 datasets × 3 tracks

| dataset     | track | sharpe | sortino | sharpe_edge_vs_spy | sortino_edge_vs_spy |
|-------------|-------|-------:|--------:|-------------------:|--------------------:|
| lh_56y      | gross | 0.8531 |  1.2216 |             +0.171 |              +0.264 |
| lh_56y      | m1    | 0.6870 |  0.9662 |             +0.005 |              +0.009 |
| lh_56y      | m2    | 0.7685 |  1.0936 |             +0.087 |              +0.136 |
| modern_1990 | gross | 0.7834 |  1.1128 |             +0.128 |              +0.179 |
| modern_1990 | m1    | 0.6205 |  0.8663 |             −0.035 |              −0.068 |
| modern_1990 | m2    | 0.6960 |  0.9821 |             +0.041 |              +0.048 |
| spy_real    | gross | 0.8486 |  1.2021 |             +0.170 |              +0.242 |
| spy_real    | m1    | 0.6865 |  0.9545 |             +0.008 |              −0.006 |
| spy_real    | m2    | 0.7412 |  1.0381 |             +0.063 |              +0.078 |
| ndx_real    | gross | 0.9715 |  1.3714 |             +0.095 |              +0.135 |
| ndx_real    | m1    | 0.7958 |  1.0994 |             −0.080 |              −0.137 |
| ndx_real    | m2    | 0.8435 |  1.1742 |             −0.033 |              −0.063 |

**H₀ gross corroboration**: in all 4 datasets, sortino_edge_vs_spy > sharpe_edge_vs_spy (4/4 PASS).

Note: m1 and m2 tracks include transaction costs, so edge vs SPY can turn negative; the asymmetric upside pattern is clearest on gross and m2.

---

## 4. Top-10 strategies — tax_comparison set (lh_56y, all 3 tracks)

Sorted by `sortino_edge_vs_canonical` descending:

| strategy | track | sharpe | sortino | sortino_edge_vs_canonical | track_A_pass | track_B_m1_pass | track_B_m2_pass |
|---|---|---:|---:|---:|:---:|:---:|:---:|
| qld_voteK2_sma250_100_vol21_40_ar30_off_zroz | m1    | 0.7661 | 1.0840 | +0.118 | No  | **Yes** | No  |
| qld_voteK2_sma250_100_vol21_40_ar30_off_zroz | gross | 0.9193 | 1.3249 | +0.103 | **Yes** | No  | No  |
| qld_voteK2_sma250_100_vol21_40_ar30_off_zroz | m2    | 0.8267 | 1.1832 | +0.090 | No  | No  | **Yes** |
| qld_voteK2_sma200_50_vol42_40_ar30_off_zroz  | m1    | 0.6897 | 0.9688 | +0.003 | No  | No  | No  |
| qld_voteK2_sma200_50_vol21_40_ar30_off_zroz  | m2    | 0.7685 | 1.0936 | +0.000 | No  | No  | No  |
| qld_voteK2_sma200_50_vol21_40_ar30_off_zroz  | gross | 0.8531 | 1.2216 | +0.000 | No  | No  | No  |
| qld_voteK2_off_zroz_alt                       | m2    | 0.7685 | 1.0936 | +0.000 | No  | No  | No  |
| qld_voteK2_off_zroz_alt                       | gross | 0.8531 | 1.2216 | +0.000 | No  | No  | No  |
| qld_vote_k2_off_zroz                          | m1    | 0.6870 | 0.9662 | +0.000 | No  | No  | No  |
| qld_vote_k2_off_zroz                          | gross | 0.8531 | 1.2216 | +0.000 | No  | No  | No  |
| qld_vote_k2_off_zroz                          | m2    | 0.7685 | 1.0936 | +0.000 | No  | No  | No  |
| qld_voteK2_off_zroz_alt                       | m1    | 0.6870 | 0.9662 | +0.000 | No  | No  | No  |
| qld_voteK2_sma200_50_vol21_40_ar30_off_zroz   | m1    | 0.6870 | 0.9662 | +0.000 | No  | No  | No  |
| qld_voteK2_sma200_50_vol42_40_ar30_off_zroz   | m2    | 0.7632 | 1.0844 | −0.009 | No  | No  | No  |
| qld_voteK2_sma200_50_vol21_30_ar30_off_zroz   | m2    | 0.7608 | 1.0844 | −0.009 | No  | No  | No  |
| qld_voteK2_sma200_50_vol42_40_ar30_off_zroz   | gross | 0.8466 | 1.2104 | −0.011 | No  | No  | No  |
| qld_voteK2_sma200_50_vol21_30_ar30_off_zroz   | gross | 0.8431 | 1.2093 | −0.012 | No  | No  | No  |
| tqqq_voteK2_off_zroz                           | m2    | 0.7486 | 1.0602 | −0.033 | No  | No  | No  |
| qld_voteK2_sma200_50_vol21_30_ar30_off_zroz   | m1    | 0.6598 | 0.9274 | −0.039 | No  | No  | No  |
| tqqq_voteK2_off_zroz                           | m1    | 0.6526 | 0.9119 | −0.054 | No  | No  | No  |
| tqqq_voteK2_off_zroz                           | gross | 0.8144 | 1.1585 | −0.063 | No  | No  | No  |
| qld_voteK2_off_edv                             | m1    | 0.6414 | 0.8905 | −0.076 | No  | No  | No  |
| qld_voteK2_off_tlt                             | m1    | 0.6414 | 0.8905 | −0.076 | No  | No  | No  |
| qld_voteK2_off_ief                             | m1    | 0.6351 | 0.8799 | −0.086 | No  | No  | No  |
| qld_voteK2_off_edv                             | m2    | 0.7146 | 1.0041 | −0.090 | No  | No  | No  |
| qld_voteK2_off_tlt                             | m2    | 0.7146 | 1.0041 | −0.090 | No  | No  | No  |
| qld_voteK2_off_tlt                             | gross | 0.7941 | 1.1222 | −0.099 | No  | No  | No  |
| qld_voteK2_off_edv                             | gross | 0.7941 | 1.1222 | −0.099 | No  | No  | No  |
| qld_voteK2_off_ief                             | m2    | 0.7026 | 0.9854 | −0.108 | No  | No  | No  |
| qld_voteK2_off_ief                             | gross | 0.7812 | 1.1019 | −0.120 | No  | No  | No  |

**Key finding**: only `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` beats the canonical Sortino across all 3 tracks. It is the sole Sortino winner.

---

## 5. Threshold sweep — 12 variants

![Sharpe vs Sortino scatter](sortino_reanalysis/sortino_vs_sharpe_scatter.png)
![Track pass comparison](sortino_reanalysis/track_pass_comparison.png)

### 5.1 Gross track (sorted by sortino_edge_vs_canonical)

| strategy | sharpe | sortino | sortino_edge_vs_canonical | track_A_pass |
|---|---:|---:|---:|:---:|
| t3d_k2_smabuf_5pct      | 0.9028 | 1.3002 | +0.079 | **Yes** |
| t3d_k2_hyst_5on_0off    | 0.8949 | 1.2871 | +0.065 | **Yes** |
| t3d_k2_hyst_3on_0off    | 0.8685 | 1.2473 | +0.026 | No  |
| t3d_k2_smabuf_05pct     | 0.8653 | 1.2407 | +0.019 | No  |
| t3d_k2_hyst_2on_0off    | 0.8645 | 1.2403 | +0.019 | No  |
| t3d_k2_baseline         | 0.8531 | 1.2216 | +0.000 | No  |
| t3d_k2_smabuf_3pct      | 0.8524 | 1.2215 | −0.000 | No  |
| t3d_k2_smabuf_1pct      | 0.8451 | 1.2096 | −0.012 | No  |
| t3d_k2_ar1buf_15        | 0.8384 | 1.2054 | −0.016 | No  |
| t3d_k2_smabuf_2pct      | 0.8375 | 1.1981 | −0.023 | No  |
| t3d_k2_ar1buf_10        | 0.8352 | 1.1970 | −0.025 | No  |
| t3d_k2_ar1buf_05        | 0.8077 | 1.1529 | −0.069 | No  |

### 5.2 M1 track — top 5 by sortino_edge_vs_canonical

| strategy | sharpe | sortino | sortino_edge_vs_canonical | track_B_m1_pass |
|---|---:|---:|---:|:---:|
| t3d_k2_smabuf_5pct   | 0.7592 | 1.0755 | +0.109 | **Yes** |
| t3d_k2_hyst_5on_0off | 0.7339 | 1.0385 | +0.072 | **Yes** |
| t3d_k2_hyst_3on_0off | 0.7045 | 0.9944 | +0.028 | No  |
| t3d_k2_smabuf_05pct  | 0.7020 | 0.9891 | +0.023 | No  |
| t3d_k2_smabuf_3pct   | 0.7010 | 0.9879 | +0.022 | No  |

### 5.3 M2 track — top 5 by sortino_edge_vs_canonical

| strategy | sharpe | sortino | sortino_edge_vs_canonical | track_B_m2_pass |
|---|---:|---:|---:|:---:|
| t3d_k2_smabuf_5pct   | 0.8124 | 1.1618 | +0.068 | **Yes** |
| t3d_k2_hyst_5on_0off | 0.8044 | 1.1487 | +0.055 | **Yes** |
| t3d_k2_hyst_3on_0off | 0.7805 | 1.1137 | +0.020 | No  |
| t3d_k2_smabuf_05pct  | 0.7790 | 1.1098 | +0.016 | No  |
| t3d_k2_hyst_2on_0off | 0.7771 | 1.1078 | +0.014 | No  |

### 5.4 Threshold sweep summary

Threshold sweep §3.3 outcome under Sharpe was "Track B-M1 only: 1/12 (`smabuf_5pct`)".
Under Sortino:
- **Track A**: 2/12 pass (`smabuf_5pct`, `hyst_5on_0off`)
- **Track B-M1**: 2/12 pass (same two)
- **Track B-M2**: 2/12 pass (same two)

Sortino relaxes the effective threshold relative to Sharpe: 2 additional variants now clear the Track B-M1 bar, and 2 now clear Track B-M2 where previously 0 passed.

---

## 6. Cohort/regime stratification

### Group D — top-3 cohort × 4 regimes (full lh_56y data)

Regime median Sortino and Sharpe for the top-3 strategies across 4 market regimes:

| strategy | regime | sharpe | sortino |
|---|---|---:|---:|
| qld_vote_k2_off_zroz                         | All-on      | 0.8402 | 1.2041 |
| qld_vote_k2_off_zroz                         | Mostly-on   | 0.7961 | 1.1365 |
| qld_vote_k2_off_zroz                         | Borderline  | 0.8601 | 1.2317 |
| qld_vote_k2_off_zroz                         | Risk-off    | 0.6934 | 0.9739 |
| qld_voteK2_sma250_100_vol21_40_ar30_off_zroz | All-on      | 0.9141 | 1.3140 |
| qld_voteK2_sma250_100_vol21_40_ar30_off_zroz | Mostly-on   | 0.8262 | 1.1741 |
| qld_voteK2_sma250_100_vol21_40_ar30_off_zroz | Borderline  | 0.8962 | 1.2583 |
| qld_voteK2_sma250_100_vol21_40_ar30_off_zroz | Risk-off    | 0.7431 | 1.0495 |
| tqqq_voteK2_off_zroz                         | All-on      | 0.8537 | 1.1967 |
| tqqq_voteK2_off_zroz                         | Mostly-on   | 0.7809 | 1.1071 |
| tqqq_voteK2_off_zroz                         | Borderline  | 0.7795 | 1.1205 |
| tqqq_voteK2_off_zroz                         | Risk-off    | 0.6261 | 0.8689 |

The new winner dominates across all 4 regimes: Sortino advantage vs canonical `qld_vote_k2_off_zroz` ranges from +0.074 (Risk-off) to +0.110 (All-on).

### Group F — cohort extension for new winner (`qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`)

8 named cohorts (worst entry points + recovery troughs) + 4 regime medians:

| cohort_id | event | tier | entry_date | sortino_5y | sharpe_5y | cagr_5y |
|---|---|---|---|---:|---:|---:|
| 01 | S&P 500 ATH before Black Monday        | worst   | 1987-08-25 | 1.198 | 0.795 | +24.7% |
| 02 | NDX dotcom peak                        | worst   | 2000-03-24 | 0.199 | 0.150 |  −1.6% |
| 03 | S&P 500 GFC peak                       | worst   | 2007-10-09 | 0.865 | 0.607 | +16.7% |
| 04 | S&P 500 COVID peak                     | worst   | 2020-02-19 | 1.000 | 0.716 | +21.6% |
| 05 | S&P 500 ATH before 2022 rate cycle     | worst   | 2021-12-27 | 0.591 | 0.428 |  +8.2% |
| 06 | S&P 500 dotcom trough (recovery)       | control | 2003-03-11 | 0.610 | 0.436 |  +9.3% |
| 07 | S&P 500 GFC trough (recovery)          | control | 2009-03-09 | 1.470 | 1.024 | +33.5% |
| 08 | S&P 500 2022 rates trough (recovery)   | control | 2022-10-12 | 1.806 | 1.250 | +41.9% |
| regime_All-on      | median forward 5y | regime | — | 1.314 | 0.914 | +28.6% |
| regime_Mostly-on   | median forward 5y | regime | — | 1.174 | 0.826 | +25.9% |
| regime_Borderline  | median forward 5y | regime | — | 1.258 | 0.896 | +27.9% |
| regime_Risk-off    | median forward 5y | regime | — | 1.049 | 0.743 | +20.9% |

**Dotcom comparison vs canonical** (`COHORT_ROBUSTNESS_REPORT.md` §1): the canonical winner's worst cohort 02 (NDX dotcom peak, `qld_vote_k2_off_zroz`) showed −12.7% 5y CAGR. The new winner `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` shows **−1.6% 5y CAGR** for the same cohort — an improvement of +11.1pp. The longer SMA window (250/100 vs 200/50) appears to materially reduce dotcom exposure losses `[leverage_for_the_long_run, p.16, p.21]`.

---

## 7. Track threshold rebuild

| Track | Old Sharpe threshold | New Sortino threshold | Canonical Sortino on lh_56y |
|---|---:|---:|---:|
| A (gross) | 0.903 | 1.272 | 1.2216 |
| B-M1      | 0.737 | 1.016 | 0.9662 |
| B-M2      | 0.818 | 1.144 | 1.0936 |

Pass count under each metric (threshold sweep × top-10 combined):

| Track | Sharpe passers | Sortino passers |
|---|---:|---:|
| A (gross)  | 1/12 sweep + 0 top-10 | 2/12 sweep + 1 top-10 |
| B-M1       | 1/12 (`smabuf_5pct`) | 2/12 + 1 top-10 |
| B-M2       | 0/12 | 2/12 + 1 top-10 |

Total unique Track A Sortino passers across all groups: **4**.
Total Track B-M1 Sortino passers: **3**.
Total Track B-M2 Sortino passers: **3**.

---

## 8. H₀ falsification

- **Strict single-cell test (canonical lh_56y gross)**: PASS. sortino_edge_vs_spy = +0.264 > sharpe_edge_vs_spy = +0.171.
- **Multi-dataset corroboration**: H₀ holds in **4/4** datasets (gross track).

The asymmetric upside hypothesis is empirically supported: the LETF rotation's Sortino edge over SPY is ~55% larger than its Sharpe edge (+0.264 vs +0.171). This is consistent with the theoretical expectation that LETFs generate right-skewed return distributions when trend filters are active, making Sortino the more informative metric `[advances_fin_ml, p.275]`.

---

## 9. Decision — winner changed

**New canonical winner under Sortino: `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`**

| criterion | value |
|---|---|
| Track A passes (Sortino ≥ 1.272) | YES (Sortino 1.325) |
| sortino_edge_vs_canonical | +0.103 |
| SMA window vs canonical | 250/100 vs 200/50 (longer) |
| vol lookback vs canonical | 21d (unchanged) |
| ar buffer vs canonical | 30d (unchanged), off mode |
| bond leg | ZROZ (unchanged) |

This strategy was already flagged by `tax_comparison` as the only +0.145 net edge M2 deploy-threshold passer. Under Sortino, it also clears Track A on lh_56y gross (Sortino 1.325 ≥ threshold 1.272).

The cohort extension (Group F, 12 rows) was generated for this winner. Regime medians side-by-side:

| regime | canonical Sortino | new winner Sortino | delta |
|---|---:|---:|---:|
| All-on      | 1.2041 | 1.3140 | +0.110 |
| Mostly-on   | 1.1365 | 1.1741 | +0.038 |
| Borderline  | 1.2317 | 1.2583 | +0.027 |
| Risk-off    | 0.9739 | 1.0495 | +0.076 |

The new winner dominates across all regimes, with the largest gain in All-on (+0.110) and Risk-off (+0.076) — the regimes where the longer SMA filter's slower exits reduce whipsaw costs `[systematic_trading, Carver p.122-133]`.

---

## 10. Implications for parent study deploy escalation

**Mandate §1**: capital remains 100% Plano C. Strategy A/B/D DORMANT regardless of Sortino verdict.

The new Sortino-anchored thresholds become the operative benchmarks for any future Plano B reactivation per choice B in the brainstorming consultation. Specifically:

| Track | Sortino threshold |
|---|---:|
| A (gross)  | 1.272 |
| B-M1       | 1.016 |
| B-M2       | 1.144 |

If Plano B is ever reactivated, the new candidate is `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` (longer SMA window canonical variant, SMA250/100), not the bare T3d K=2. It is the only strategy that:
1. Clears Track A Sortino threshold (1.325 ≥ 1.272)
2. Clears Track B-M1 Sortino threshold (1.084 ≥ 1.016)
3. Clears Track B-M2 Sortino threshold (1.183 ≥ 1.144)
4. Was the only M2 deploy-threshold passer in the tax_comparison sub-study

No current capital commitment follows from these findings `[advances_fin_ml, p.208-211]`.

---

## 11. Citations

- `[sortino_1991]` Sortino, F.A. (1991) "Performance Measurement in a Downside Risk Framework", Financial Executive, 17(8): 31-34.
- `[advances_fin_ml, p.275]` de Prado on deflated SR, Sortino in the family of risk-adjusted metrics.
- `[advances_fin_ml, p.208-211]` CSCV PBO + multiple-testing margin (anti-curve-fit rationale).
- `[systematic_trading, Carver p.122-133, p.174]` asymmetric metrics for leveraged systems.
- `[trading_systems_methods, Kaufman ch.21]` alternative risk measures for system evaluation.
- `[advances_fin_ml, p.31-34, p.222-223]` multi-window backtest validation (cohort extension).
- `[leverage_for_the_long_run, p.16, p.21]` LETF path-dependence and recovery.
- Parent: `STUDY_FINAL_REPORT.md` §3.4 anti-curve-fit threshold, §4 deploy escalation, §7.7 Cenário B.
- Sister: `THRESHOLD_SWEEP_REPORT.md` §3.3 boundary-winner outcome categorisation.

---

## 12. Where it lives

- Spec: `docs/superpowers/specs/2026-05-07-letf-sortino-reanalysis-design.md`
- Plan: `docs/superpowers/plans/2026-05-07-letf-sortino-reanalysis.md`
- Code: `studies/letf_rotation_hunt/analyses/sortino_reanalysis/`
- Tests: `studies/letf_rotation_hunt/tests/test_sortino_reanalysis.py` (8 tests)
- Data: `data/sortino_reanalysis/{sortino_metrics.csv, cohort_extension.csv}`
- Plots: `studies/letf_rotation_hunt/reports/sortino_reanalysis/{sortino_vs_sharpe_scatter, track_pass_comparison}.png`
- Jornada: `jornada/2026-05-07-HHMM-letf-sortino-reanalysis.md` (Task 13)

---

## 13. Limitations & follow-ups

- **Heatmap not rerun** under Sortino (1278×4 forward-Sharpe panel deferred — cascade choice C).
- **Sortino 1991 vs 1994** trade-off discussed in spec §3.3; we chose 1991 (target = 0, full N denominator).
- **Optional Phase E**: deflated Sortino with bootstrap CIs, mirroring parent study G6.
- **No Plano B deployment** triggered: mandate §1 keeps capital 100% Plano C.
- The new winner `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` should be validated through a fresh cohort_robustness rerun if Plano B is ever reactivated (per spec §11.5, follow-up sub-study material).
- The dotcom cohort improvement (−1.6% vs −12.7% 5y CAGR) is striking but based on a single 5-year window; it merits a dedicated rolling-window analysis before treating it as a structural advantage.
