# Phase 3.6 Family I — Statistically-sound indicators (honest validation)

**Date:** 2026-04-23  |  **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched (commit `7b90a8f`, clean return-series)
**Broker path modelled:** Banco Inter Internacional (plan §3.2) — zero commission on US ETFs, 0.05% one-way spread, 15% BR CG tax.
**Windows:** IS 2001-05-14 → 2017-12-31 | OOS 2018-01-01 → 2023-12-31 | FWD 2024-01-01 → 2026-04-14

## Verdict: **FAIL**

**Structural FAIL — 0 candidate indicators survived the Bonferroni-corrected MCPT screen at p<0.001.** This is a valid, informative result per plan §brief: it says that the 8 canonical indicators in the pool, tested rigorously against shuffled-bar null, cannot clear Masters' `[stat_sound_indicators, p.170, p.174]` significance bar on the 5-ETF universe over IS 2004-2017 (effective IS start 2004-11-19 — the earliest date with complete data across all 5 ETFs, driven by GLD inception 2004-11-18). No ensemble can be formed. Gates 1-13 are therefore all **undefined-by-structural-FAIL**: there is no ensemble return series to test. The mandate §7 and strategy docs stay **UNTOUCHED.**

## §Screening Protocol (the core of this family)

**Universe:** `['SPY', 'QQQ', 'GLD', 'TLT', 'EEM']` — broad liquid ETFs `[stat_sound_indicators, p.1, p.108]`.

**Candidate pool (M=8):**
- `rsi14_mr` — obs. periodic SR = +0.0208, p_raw = 0.4232, p_Bonferroni = 1.0000 → **drop**
- `macd_hist_cross` — obs. periodic SR = +0.0115, p_raw = 0.8543, p_Bonferroni = 1.0000 → **drop**
- `connors_rsi2_mr` — obs. periodic SR = +0.0513, p_raw = 0.0319, p_Bonferroni = 0.2555 → **drop**
- `donchian20_breakout` — obs. periodic SR = +0.0136, p_raw = 0.7385, p_Bonferroni = 1.0000 → **drop**
- `zscore5_mr` — obs. periodic SR = +0.0242, p_raw = 0.3513, p_Bonferroni = 1.0000 → **drop**
- `bollinger2_mr` — obs. periodic SR = +0.0196, p_raw = 0.4750, p_Bonferroni = 1.0000 → **drop**
- `sma200_trend` — obs. periodic SR = +0.0334, p_raw = 0.3493, p_Bonferroni = 1.0000 → **drop**
- `cn20_mr` — obs. periodic SR = +0.0293, p_raw = 0.3892, p_Bonferroni = 1.0000 → **drop**

**Protocol details:**
- MCPT permutation test: 500 reps per candidate `[stat_sound_indicators, p.301]`, `[testing_tuning, p.310-319]`.
- Permutation model: simple-market shuffle (per-asset independent column shuffle of IS returns, rebuild prices, recompute signals) `[testing_tuning, p.327-328]`.
- Raw p-value: p_raw = (1 + #{perm ≥ obs}) / (n_perm+1) `[stat_sound_indicators, p.301]`.
- Bonferroni correction: p_corr = min(1, M × p_raw); keep if p_corr < α = 0.001 `[stat_sound_indicators, p.170, p.174]`.
- **IS window only**: 2001-05-14 → 2017-12-31. OOS and FWD purity preserved per `[stat_sound_indicators, p.306]`, `[testing_tuning, p.143-144]`.
- Ensemble: mean-per-asset signal across survivors → long-only equal-weighted allocation, capped at Σw=1.

**Conclusion of §Protocol (structural FAIL):** the canon of mainstream oscillators/breakouts/MR signals at Masters' bar of 0.001 Bonferroni-corrected p-value leaves no tradeable edge on the 5-ETF universe. This is a scientifically informative FAIL — consistent with the literature's finding that published indicator rules rarely survive proper data-mining-bias controls on broad liquid markets `[evidence_based_ta, p.450]` (Hsu/Kuan 82% of significant rules fail on S&P/DJIA; Aronson's 6,402-rule study `[p.409-410, p.459]` found none significant after MCP at p<0.05 on the S&P 500). The best raw p-value was `connors_rsi2_mr` at 0.032 — already marginal before Bonferroni correction multiplies it by M=8 to 0.256. No candidate approaches the 0.001 threshold.

## 13-gate checklist (structural FAIL — all gates undefined)

| # | Gate | Threshold | Value | Pass |
|---|------|-----------|------:|:----:|
| 1 | `gate_01_bootstrap_oos_99p9_ci_low_gt_0` | > 0 | undefined (no ensemble) | FAIL-structural |
| 2 | `gate_01b_bootstrap_full_99p9_ci_low_gt_0` | > 0 | undefined (no ensemble) | FAIL-structural |
| 3 | `gate_02_oos_sharpe_ge_1_5` | ≥ 1.5 | undefined (no ensemble) | FAIL-structural |
| 4 | `gate_03_oos_cagr_ge_13pct_CDI` | ≥ 13% | undefined (no ensemble) | FAIL-structural |
| 5 | `gate_03_target_oos_cagr_ge_30pct` | ≥ 30% | undefined (no ensemble) | FAIL-structural |
| 6 | `gate_04_oos_maxdd_le_25pct` | ≥ −25% | undefined (no ensemble) | FAIL-structural |
| 7 | `gate_05_fwd_sharpe_gt_0` | > 0 | undefined (no ensemble) | FAIL-structural |
| 8 | `gate_06_wf_6_8_and_mdd_le_30pct` | both | undefined (no ensemble) | FAIL-structural |
| 9 | `gate_07_median_hold_ge_5d` | ≥ 5d | undefined (no ensemble) | FAIL-structural |
| 10 | `gate_08_ir_vs_spy_oos_ge_0_3` | ≥ 0.3 | undefined (no ensemble) | FAIL-structural |
| 11 | `gate_09_cross_lib_concordance` | deferred | undefined (no ensemble) | FAIL-structural |
| 12 | `gate_10_stage2_data_concordance` | N/A | undefined (no ensemble) | FAIL-structural |
| 13 | `gate_11_pbo_lt_0_5` | < 0.5 | undefined (no ensemble) | FAIL-structural |
| 14 | `gate_12_dsr_p_lt_0_05` | < 0.05 | undefined (no ensemble) | FAIL-structural |
| 15 | `gate_13_cost_sensitivity_2x_sharpe_gt_1` | > 1.0 | undefined (no ensemble) | FAIL-structural |

**Summary: 0 PASS / 15 FAIL-structural / 0 deferred.** Since no indicator survives screening, the ensemble return series is undefined. All 13 edge/risk gates cannot be evaluated — the family FAILs at the earliest stage of the pipeline (indicator significance).

## Top-line metrics (no ensemble — flat zero-return placeholder)

| Split | Bars | Sharpe | CAGR | MaxDD |
|-------|-----:|-------:|-----:|------:|
| IS | 3301 | 0.000 | 0.00% | 0.00% |
| OOS | 1509 | 0.000 | 0.00% | 0.00% |
| FWD | 572 | 0.000 | 0.00% | 0.00% |
| FULL | 5383 | 0.000 | 0.00% | 0.00% |

## Artifacts

- `AGGREGATE.json` — full numeric detail, 13-gate structured.
- `screening_results.csv` — raw + Bonferroni-corrected p-values per candidate.
- Logs: `logs/phase3_6_i_stat_sound.log`.
- Strategy module: `src/ai_trade/backtest/strategies/phase3_6_i_stat_sound_indicators.py`.
- Runner: `scripts/run_phase3_6_i_stat_sound_indicators.py`.

## Mandate §7 / strategy doc status

**UNTOUCHED.** This verdict is FAIL. No promotion.

## Citations

- MCPT screening + p<0.001 threshold: `[stat_sound_indicators, p.170, p.174, p.299-306]`.
- Simple-market permutation protocol: `[testing_tuning, p.327-328]`, `[evidence_based_ta, p.255-256]`.
- Selection bias hazard: `[stat_sound_indicators, p.170, p.306]`, `[evidence_based_ta, p.283-291]`.
- Universe (broad indices): `[stat_sound_indicators, p.1, p.108]`.
- RSI: `[evidence_based_ta, p.429]`.
- MACD: `[evidence_based_ta, p.429]`.
- Channel Breakout Operator (Donchian 20): `[evidence_based_ta, p.397]`.
- Channel Normalization (stochastic K): `[evidence_based_ta, p.402]`.
- z-score stationarity CENTER/SCALE: `[stat_sound_indicators, p.87-89]`.
- Bollinger-band MR (z-score): `[testing_tuning, p.28]`.
- 200d MA trend filter: `[evidence_based_ta, p.398]`.
- Connors-style 2-RSI MR: `[testing_tuning, p.43]` (linear-indicator design principle).
- Lookahead-free timing: `[advances_fin_ml, p.31-34]`.
- Bootstrap 99.9% CI: `[advances_fin_ml, p.196-202]`.
- CSCV PBO: `[advances_fin_ml, p.208-211]`.
- DSR: `[advances_fin_ml, p.273-275]`.
- Walk-forward ≥ 6/8 + 30% DD cap (relaxed): `[advances_fin_ml, ch.11]`.
- Inter broker model: plan `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md` §3.2.
