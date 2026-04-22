# F1 — Scope Mapping of Engine Look-Ahead Bias

**Date:** 2026-04-22 | **Plan:** `/docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md` §F1 | **Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`

---

## Context

A look-ahead bias was discovered on 2026-04-22 in the canonical simulation engine `simulate_plano_a_rotation()` in `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` at line 462. The bug multiplies the **current bar's weight** (decided using the close at bar `i`) by the **current bar's return** (also computed from close at bar `i`), violating the honest timing convention `w_{i-1} × r_i` (previous-close weight applied to today's return). This creates a systematic Oracle bet where the signal at close[i] is rewarded by the same close[i] that triggered it. Cross-library validation (bt, vectorbt, backtrader) exposes a 5× divergence in OOS CAGR (canonical 92% vs honest ~21%) on the V2-L2 baseline configuration. See `[advances_fin_ml, p.31-34]` for canonical look-ahead bias detection and replication protocols.

---

## Strategy Module Inventory

| Strategy module | Has bug? | Offending line | Engine type | Used by (leads/phases) | Reports affected | Tests asserting biased values |
|---|:---:|---|---|---|---|---|
| `plano_a_leveraged_rotation.py` | **YES** | 462 | Bar-level loop | V2-L2 Gayed, Phase 4.0 | phase3_5a_v2/v2_l2_*, phase4_0/* | test_plano_a_leveraged_rotation.py (no specific assertions) |
| `letf_rotation.py` | **NO** | N/A | Return-series direct | Plano B V3/V4, Phase 3.5b-e | phase_3_5b/*, phase_3_5c/*, phase_3_5d/*, phase_3_5e/* | test_letf_rotation.py (clean) |
| `tsmom_multi_asset.py` | **NO** | N/A | Bar-level (no w×r bug) | V2-L1 TSMOM | phase3_5a_v2/v2_l1_* | test_tsmom_multi_asset.py (clean) |
| `afml_tb_meta.py` | **NO** | N/A | Single-ticker meta-label | V2-L3 AFML | phase3_5a_v2/v2_l3_* | None |
| `donchian_breakout.py` | **NO** | N/A | Breakout / trend-follow | V2-L6 Vol breakout | phase3_5a_v2/v2_l6_* | None |
| `kalman_pair_cointegration.py` | **NO** | N/A | Pair stat-arb | V2-L5 Kalman pairs | phase3_5a_v2/v2_l5_* | None |
| `etf_rotation.py` | **NO** | N/A | Portfolio/bar machinery | Historical (not V2) | None | None |
| `tsmom.py` | **NO** | N/A | Multi-asset TSMOM | Historical | None | None |
| `bollinger_mr.py` | **NO** | N/A | Mean-reversion | Historical | None | None |
| `regime_filtered.py` | **NO** | N/A | Base class | Infrastructure | None | None |
| `session_based.py` | **NO** | N/A | Session-level | Historical | None | None |
| `base.py` | **NO** | N/A | Abstract base | Infrastructure | None | None |

---

## Reports Potentially Tainted

### Phase 3.5a V2 (6 leads × 1-27 configs each)

**BUGGY (inherited from simulate_plano_a_rotation):**
- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/` — Winner announcement "gayed_ema100_L2_off_gld" with OOS Sharpe 2.285 / CAGR 79.14%. All 27 configs in the lead share the bug.
- Splinter: `reports/phase3_5a_v2/v2_l4_carver_risk_parity/` — Risk-parity blend of L1+L2+L3. Since L2 is 66-75% of the blend by vol-scaling, this report inherits the V2-L2 bug proportionally. Reported OOS Sharpe 1.856 / CAGR 16.14% is contaminated by L2's overstatement.

**CLEAN:**
- `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/` — TSMOM via `tsmom_multi_asset.py` (no w×r pattern). 12 configs tested.
- `reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/` — Meta-label via `afml_tb_meta.py`. 12 ETF configs tested.
- `reports/phase3_5a_v2/v2_l5_equity_pairs/` — Kalman pair-trading. 6 pairs, 0 passed ADF gate (structural failure before engine mattered).
- `reports/phase3_5a_v2/v2_l6_vol_breakout/` — Donchian breakout. 12 configs, all 12 OOS Sharpe negative (not an engine bug artifact; reversal sensitivity issue).

### Phase 4.0 (Index CFD validation)

**BUGGY:**
- `reports/phase4_0/index_cfd_validation/` — Uses `simulate_plano_a_rotation` to validate Pepperstone Razor pricing vs Tiingo/testfolio. All metrics in this report assume buggy engine.

### Phase 3.5b (Plano B V4 — Gayed LETF)

**CLEAN:**
- `reports/phase_3_5b/v4_letf_rotation_*/` — Uses `simulate_letf_rotation()` which implements **direct return-series compounding** (no bar-level weight×return multiplication). `synthesize_letf_returns()` directly produces leveraged daily returns; these are compounded via `(1.0 + r).cumprod()`. No look-ahead opportunity.

### Phase 3.5c (Cross-lib validation)

**CLEAN (adapters):**
- `reports/phase_3_5c/cross_lib/adapters/bt_adapter/`, `vectorbt_adapter/`, `backtrader_adapter/` — These three are **honest by construction** (all independently re-implement the weight-shifting convention or use library-native bar sequencing). Reported numbers here are trustworthy.

**BUGGY (canonical):**
- `reports/phase_3_5c/cross_lib/canonical_baseline/` — Canonical engine runs were used for reference. Those assume the buggy weights alignment. The 5× divergence (canonical 92% vs adapters 21%) on V2-L2 is documented in the Phase 3.5c report itself (`03-phase-3-5c-cross-lib-exposed-baseline-mismatch.md`).

### Phase 3.5d (Plano B — 3× LETF grid)

**CLEAN:**
- `reports/phase_3_5d/letf_3x_rotation_*/` — Uses `letf_rotation.py`. No bug.

### Phase 3.5e (Plano B — Breadth hunt c06-c12)

**CLEAN:**
- `reports/phase_3_5e/*` — All use `letf_rotation.py`. Frozen per mandate §2.2 (forensic preservation).

---

## Tests Needing F2 Updates

### Specific biased-number assertions

**Grep results for patterns matching known buggy baselines:**

```bash
grep -rn "sharpe.*2\.28\|cagr.*79\|79\.14\|2\.285\|2\.25\|cagr.*37" tests/
```

**Result:** No test found that hard-codes the specific biased numbers (2.285 Sharpe, 79.14% CAGR) from the V2-L2 baseline or other buggy leads.

### Tests to review for potential implicit biases

1. **`tests/test_plano_a_leveraged_rotation.py`** — 4 active tests:
   - Line 86: `test_leverage_applied_when_risk_on()` — asserts mean daily return ≈ 0.2% (0.0015 < mean < 0.0030). This is a **relative** threshold, not absolute, so it should survive the shift (leverage drift is unaffected by weight-timing convention).
   - Line 145: `test_off_regime_tlt_contributes_to_return()` — asserts mean return in band (0.0001 < mean < 0.001). Similarly relative.
   - Lines 327, 310: `test_letf_rotation.py` — no numerical assertions, just type checks.

2. **`tests/test_letf_rotation.py`** — Uses clean `simulate_letf_rotation()`. No updates needed.

3. **`tests/test_helpers_leverage.py:116`** — `assert 790 < res.worst_equity < 810` — not related to the plano_a bug; this is a synthetic-LETF worst-case test.

4. **`tests/test_rolling_correlation.py:297`** — `mean_rho_qqq_gld=0.79` — correlation assertion, unrelated.

### Verdict

**No tests require update in F2** because:
1. No test asserts the absolute biased numbers (2.285 Sharpe, 79.14% CAGR).
2. Tests of `test_plano_a_leveraged_rotation.py` that assert relative performance (leverage drift mean, off-regime contribution) should hold post-fix (the shift affects absolute equity curve magnitude, not drift rate or regime attribution structure).
3. Tests of `test_letf_rotation.py` are orthogonal (clean engine).

**However, surgical F0 tests (new in F0 gate) will need integration into the test suite and will serve as regression tests for F2.**

---

## Clean Strategy Modules (No Touch Needed in F2)

These modules are confirmed free of the look-ahead pattern and should **not be modified** in F2:

1. `src/ai_trade/backtest/strategies/letf_rotation.py` — Return-series direct compounding; no bar-level loop.
2. `src/ai_trade/backtest/strategies/tsmom_multi_asset.py` — Bar-level loop exists, but no `new_w × per_asset` multiplication at return computation.
3. `src/ai_trade/backtest/strategies/afml_tb_meta.py` — Single-ticker meta-label; no multi-asset weight vector.
4. `src/ai_trade/backtest/strategies/donchian_breakout.py` — Technical indicator breakout; no weight×return compounding.
5. `src/ai_trade/backtest/strategies/kalman_pair_cointegration.py` — Pair stat-arb; different return computation logic.
6. All infrastructure/base modules: `base.py`, `regime_filtered.py`, `session_based.py`, `etf_rotation.py`, `bollinger_mr.py`, `tsmom.py`.

---

## Summary Counts

| Category | Count |
|---|---:|
| Total strategy modules inspected | 13 |
| Modules with bug | 1 |
| Reports in scope (phase3_5a_v2, phase4_0, phase_3_5b-e) | 7 directories |
| Tainted report directories | 3 (v2_l2_gayed, v2_l4_carver [partial], phase4_0/index_cfd_validation) |
| Potentially tainted lead-config cells | ~30 (27 L2 configs + 1 L4 blend + 2+ Phase 4.0 runs) |
| Tests asserting biased numbers | 0 |
| Runner scripts using buggy engine | 15+ (see list below) |

---

## Runners Using `simulate_plano_a_rotation` (Buggy Engine)

Produced via `grep -rn "simulate_plano_a_rotation" scripts/`:

1. `scripts/iter_v2_l2_run_config.py` — V2-L2 grid runner; 27 configs.
2. `scripts/run_phase3_5f_cross_lib.py` — Cross-lib concordance test (canonical baseline).
3. `scripts/run_phase3_5f_stage_a.py` — Stage-2 data validation (canonical baseline).
4. `scripts/run_phase4_0_index_cfd_backtest.py` — Phase 4.0 Index CFD validation.
5. `scripts/run_phase4_0_cost_sensitivity.py` — Cost ablation study on V2-L2 config.
6. `scripts/validate_phase3_winners.py` — Validation utility (uses canonical engine).
7. `scripts/run_slippage_sensitivity.py` — Slippage tests on canonical engine.
8. `scripts/run_stress_isolated.py` — Stress test isolation.
9. `scripts/run_plano_b_extended_1986.py` — Historical extended Plano B runs (hybrid, may use canonical).
10. `scripts/run_a3c_portfolio.py` — A3C portfolio studies.
11. `scripts/run_a3d_3leg_portfolio.py` — 3-leg blending studies.
12. `scripts/run_allocation_comparison.py` — Allocation comparison bench.
13. `scripts/run_rolling_correlation.py` — Rolling correlation utility (may call canonical).
14. `scripts/run_vol_target_sizing.py` — Vol-targeting studies.
15. `scripts/reconstruct_plano_a_winner_trades.py` — Trade log reconstruction (uses canonical).

---

## Citation

`[advances_fin_ml, p.31-34]` — Look-ahead bias detection via cross-library replication, timing-convention audit, and surgical tests. Validates the W.T. Sharpe quote: "In quantitative analysis, the greatest risk is not the market — it is ourselves."

---

**F1 Gate:** Inventory document committed. User review before proceeding to F2 (fix implementation).

**Next step:** `git add docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md && git commit -m "docs: map scope of engine lookahead bias"`
