# Phase 4.0 — Index CFD substitution verdict (AGGREGATE)

**Status:** ✅ **CAMINHO 3 VIÁVEL**
**Date:** 2026-04-20
**Branch:** `phase4_0/index-cfd-validation`
**Gates passed:** 10/10

## 1. Executive summary

Substituting SPY/QQQ/GLD share CFDs with SPX TR / QQQ adj_close / GLD adj_close (proxies for US500 / USTEC / XAUUSD Index CFDs) **preserves or improves** the V2-L2 winner's gate-passing behavior.

Key numbers vs V2-L2 share-CFD baseline:

- OOS Sharpe: **2.400** (baseline 2.285)
- OOS CAGR: **85.76%** (baseline 79.14%)
- OOS MDD: **-21.51%** (baseline -21.02%)
- IR vs SPY (OOS): **2.333** (baseline 2.161)
- Bootstrap 99.9% CI low (full): **1.379** (baseline 0.962)

The improvement is driven by (a) commission assumed zero in Razor Index vs 6.6 bps in share CFD (−204 bps cumulative savings over 25y), partially offset by (b) ~60% higher cumulative swap drag (−73% vs −45%).

**Operational consequence:** live-trading Plano A at **$1.000** capital is viable on Index CFDs, conditional on T1 (rate card confirmation in live Pepperstone demo account) and T2 (dividend adjustment mechanics).

## 2. Gate-by-gate verdict

| Gate | Threshold | Observed | Pass |
|---|---|---:|:--:|
| Bootstrap 99.9% CI low (full) | > 0 | 1.379 | ✅ |
| Bootstrap 99.9% CI low (OOS only) | > 0 | 1.055 | ✅ |
| Walk-forward 6/8 profitable | ≥ 0.75 | 1.000 | ✅ |
| Walk-forward max DD | ≤ 25% | 22.61% | ✅ |
| OOS CAGR | ≥ 30% | 85.76% | ✅ |
| OOS Sharpe | ≥ 2.0 | 2.400 | ✅ |
| OOS MDD | ≤ 25% | -21.51% | ✅ |
| FWD Sharpe | > 0 | 1.797 | ✅ |
| Median hold | ≥ 3 days | 5.00 | ✅ |
| IR vs SPY (OOS) | ≥ 0.5 | 2.333 | ✅ |
| Cost sensitivity (swap 2×) | OOS Sharpe ≥ 1.5 & CAGR ≥ 30% | S=2.292 C=80.38% | ✅ |

## 3. Why PBO and DSR are excluded (n_trials=1)

Per spec `§3 T4`: PBO and DSR are multi-config tests. With a single substituted config, PBO has no cross-config sample and DSR's multi-hypothesis correction collapses to the standard Sharpe t-test (already implicit in bootstrap CI).

Bootstrap 99.9% CI low > 0 is the primary **distribution-free** robustness gate. Bootstrap is cited `[advances_fin_ml, p.196-202]` (Politis & Romano 1994 stationary block, block_mean=5, n_resamples=10000).

## 4. Known caveats (carry forward to Phase 4 paper)

1. **GLD proxy for XAUUSD.** GLD.adj_close used because xauusd.parquet only has 2020+ data. Post-2004 GLD behavior = spot gold minus 0.40% expense ratio; pre-2004 is silent-cash (same as V2-L2 caveat).
2. **Cost model assumes Razor Index commission-free.** T1 must validate this empirically in a live Pepperstone demo account before Phase 5.1 live.
3. **Dividend adjustment perfect.** SPX TR and QQQ adj_close include 100% dividend reinvestment. T2 must validate that Pepperstone's Index CFD dividend-adjustment mechanism passes through ≥ 95% of gross yield.
4. **Lot granularity at $1k:** 0.01 lot US500 ≈ $600 notional → 40% rounding vs target $1000. Residual lumpy but viable.
5. **Swap drag 60% higher than V2-L2.** Cumulative 73% vs 45%. If live swap is even worse than the −0.008%/day modeled, CAGR degrades further.

## 5. Next actions

1. **T5 — propagate verdict to docs** (strategy doc §4.2 + §6.3, mandate §3.6, Phase 4 spec §1, Phase 3.5a-V2 AGGREGATE §7.5).
2. **T1 — Pepperstone Razor Index rate card empirical validation** (requires demo account). Blocks Phase 5.1 live start.
3. **T2 — Dividend adjustment observation** (1 SPY ex-div cycle in demo). Blocks Phase 5.1 live start.
4. **Phase 4 paper trading** can start with Index CFD variant as soon as T1 is green. Spec update required in `phase_4_paper_trading.md §1`.

## 6. Artefact inventory

- `reports/phase4_0/index_cfd_validation/summary.json` (T3 output)
- `reports/phase4_0/index_cfd_validation/daily_returns.parquet` (T3 output)
- `reports/phase4_0/index_cfd_validation/standard_report.md` (T3 output)
- `reports/phase4_0/index_cfd_validation/gates.json` (T4 output)
- `reports/phase4_0/index_cfd_validation/AGGREGATE.md` (T4 output, this file)
- `scripts/run_phase4_0_index_cfd_backtest.py` (T3 code)
- `scripts/run_phase4_0_index_cfd_gates.py` (T4 code)

## 7. Citations

- EMA-100 regime signal: `[leverage_for_the_long_run, Gayed, p.11-14]`
- Leverage cap L=2: `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`
- Fixed commission at retail scale: `[systematic_trading, Carver, p.185-188]`
- Bootstrap CI (stationary block): `[advances_fin_ml, p.196-202]`
- Walk-forward 6/8 gate: `[advances_fin_ml, ch.11]`
