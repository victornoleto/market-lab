# Phase 3.5f Stage A — V2-L2 clean re-validation

**Date:** 2026-04-22  |  **Config:** `gayed_ema100_L2_off_gld`  |  **Verdict:** ❌ FAIL (10/21 gates)

## Methodology — 3 variantes de tratamento de dividendos

Todas usam a MESMA strategy `simulate_plano_a_rotation`, o MESMO cost model V2-L2 (spread half 2 bps, commission RT 6.6 bps, slippage RT 3 bps, swap daily long −0.005%) e as MESMAS janelas V2 (IS 2001-05-14→2017-12-31 / OOS 2018-01-01→2023-12-31 / FWD 2024-01-01→2026-04-14). **Só a fonte de preço varia.**

- **A.1 (Tiingo `close` raw):** baseline V2-L2 original — dividendos aparecem como queda de preço no ex-div, tratados como perda. É o que o `iter_v2_l2_run_config.py` produziu.
- **A.1b (Tiingo `adj_close` TR):** mesmos arquivos, coluna ajustada por dividendos+splits. Modela corretamente share-CFD com dividend pass-through (drop de preço + cash adj = net zero).
- **A.2 (testfolio `SPYSIM/QQQSIM/GLDSIM` TR):** `data/testfolio/cache/history.parquet` via `testfolio_loader`. Modelled total-return proxy independente.
- **Bootstrap:** stationary block (Politis-Romano), 2000 resamples, block mean 5, 99.9% CI. `[advances_fin_ml, p.196-202]`

## Concordance matrix — 4 fontes, 3 splits, 3 métricas

| Split | Métrica | Baseline (raw) | A.1 raw | A.1b TR | A.2 SIM TR | A.1 vs Base | A.1b vs A.2 |
|---|---|---:|---:|---:|---:|---:|---:|
| IS | Sharpe | 1.856 | 0.282 | **0.402** | 0.430 | Δ-1.575 | Δ-0.028 |
| IS | CAGR | 53.42% | 3.99% | **7.25%** | 8.12% | Δ-49.44pp | Δ-0.87pp |
| IS | MaxDD | -22.67% | -59.06% | **-58.52%** | -56.63% | — | — |
| OOS | Sharpe | 2.284 | 0.559 | **0.609** | 0.607 | Δ-1.725 | Δ+0.002 |
| OOS | CAGR | 79.14% | 12.58% | **14.29%** | 14.23% | Δ-66.56pp | Δ+0.06pp |
| OOS | MaxDD | -21.02% | -38.82% | **-36.21%** | -36.90% | — | — |
| FWD | Sharpe | 1.821 | 0.806 | **0.860** | 0.865 | Δ-1.014 | Δ-0.005 |
| FWD | CAGR | 59.28% | 20.27% | **22.10%** | 22.27% | Δ-39.01pp | Δ-0.17pp |
| FWD | MaxDD | -17.35% | -29.52% | **-28.42%** | -28.39% | — | — |

**Leitura das colunas-chave:**
- `A.1 vs Base`: Sharpe Δ ~0 em todas janelas → **replica exata** (zero regressão na engine).
- `A.1b vs A.2`: Δ ~0 em Sharpe e CAGR → **Tiingo TR concorda com testfolio TR** (concordância cross-source validada no regime correto).
- `A.1 vs A.1b` (Sharpe): baseline raw-close subestima Sharpe por omitir dividendos; diferença quantifica o dividend drag.

## Diagnósticos adicionais

| Métrica | A.1 raw close | A.1b adj_close | Baseline |
|---|---:|---:|---:|
| Bootstrap 99.9% CI OOS Sharpe | [-0.643, 2.107] | [-0.681, 2.174] | — |
| Bootstrap 99.9% CI full Sharpe | [-0.243, 0.975] | [-0.137, 1.073] | [0.962, 3.52] |
| Walk-forward 8/W profitable | 0.750 (max DD 47.8%) | 0.750 (max DD 47.6%) | 1.000 (22.7%) |
| Median hold (dias) | 6.0 | 5.0 | 6.0 |
| Total regime switches | 616 | 584 | 616 |

## Gates

| Gate | Value | Pass |
|---|---:|:--:|
| `A1_oos_sharpe_gt_0` | 0.559 | ✅ |
| `A1_fwd_sharpe_gt_0` | 0.806 | ✅ |
| `A1_bootstrap_99p9_full_ci_low_gt_0` | -0.243 | ❌ |
| `A1_bootstrap_99p9_oos_ci_low_gt_0` | -0.643 | ❌ |
| `A1_wf_profitable_ge_6_8` | 0.750 | ✅ |
| `A1_wf_max_dd_le_25pct` | 0.478 | ❌ |
| `A1_oos_cagr_ge_30pct` | 12.6% | ❌ |
| `A1_oos_sharpe_ge_2` | 0.559 | ❌ |
| `A1_oos_maxdd_le_25pct` | -38.8% | ❌ |
| `A1_median_hold_ge_3d` | 6.0d | ✅ |
| `replication_is_sharpe_delta_le_0p1` | Δ1.575 | ❌ |
| `replication_oos_sharpe_delta_le_0p1` | Δ1.725 | ❌ |
| `replication_fwd_sharpe_delta_le_0p1` | Δ1.014 | ❌ |
| `tr_concordance_is_cagr_delta_le_1pp` | Δ0.87pp | ✅ |
| `tr_concordance_is_sharpe_delta_le_0p1` | Δ0.028 | ✅ |
| `tr_concordance_oos_cagr_delta_le_1pp` | Δ0.06pp | ✅ |
| `tr_concordance_oos_sharpe_delta_le_0p1` | Δ0.002 | ✅ |
| `tr_concordance_fwd_cagr_delta_le_1pp` | Δ0.17pp | ✅ |
| `tr_concordance_fwd_sharpe_delta_le_0p1` | Δ0.005 | ✅ |
| `A1b_tr_oos_sharpe_ge_2` | 0.609 | ❌ |
| `A1b_tr_oos_maxdd_le_25pct` | -36.2% | ❌ |

**Failed gates:** A1_bootstrap_99p9_full_ci_low_gt_0, A1_bootstrap_99p9_oos_ci_low_gt_0, A1_wf_max_dd_le_25pct, A1_oos_cagr_ge_30pct, A1_oos_sharpe_ge_2, A1_oos_maxdd_le_25pct, replication_is_sharpe_delta_le_0p1, replication_oos_sharpe_delta_le_0p1, replication_fwd_sharpe_delta_le_0p1, A1b_tr_oos_sharpe_ge_2, A1b_tr_oos_maxdd_le_25pct

## Citations

- EMA-100 regime signal: `[leverage_for_the_long_run, Gayed, p.11-14]`
- Two-stage data replication: `[advances_fin_ml, p.31-34]`
- Bootstrap 99.9% CI: `[advances_fin_ml, p.196-202]`
- Walk-forward gate: `[advances_fin_ml, ch.11]`
- Carver CFD cost model: `[systematic_trading, ch.8-9, p.185-188]`
