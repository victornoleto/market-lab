# V2-L1 TSMOM Multi-Asset Daily — Honest Reconfirmation

**Phase:** 3.5f / F3 honest winner hunt
**Lead:** V2-L1 (canonical time-series momentum, 30-asset CFD-proxy universe, monthly EOM rebalance)
**Date:** 2026-04-22
**Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`
**F2 engine-fix commit:** `7b90a8f` — `fix(backtest): shift weight×return alignment to remove lookahead bias`
**F1 scope audit:** `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md` (lead listed under **CLEAN**)
**Strategy module:** `src/market_lab/backtest/strategies/tsmom_multi_asset.py` — confirmed CLEAN in F1 (no `w_i × r_i` pattern)
**Original report:** `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/` (12 configs)

---

## Verdict

> **FAIL (reconfirmed)** — engine was clean, previous numbers stand. V2-L1 was DEAD under the original engine and remains DEAD under the honest engine because the strategy file was never affected by the bug. The failure mechanism (swap drag > risk premium on 40-160 day holds) is a retail-cost-model truth, not a simulation artifact.

**No re-simulation required; F1 scope audit confirmed `tsmom_multi_asset.py` never had the w×r lookahead bug. Previous OOS metrics are honest-baseline and stand as-is.**

---

## Top metrics (least-worst config — `tsmom_lb12m_vt10`)

| Metric | Value | Gate |
|---|---:|---|
| OOS Sharpe | −0.21 | ❌ (need ≥ 2.0; soft ≥ 1.5) |
| OOS CAGR | −0.49% | ❌ (CDI-floor soft-gate ≥ 13%) |
| OOS MaxDD | −10.24% | ✅ (≥ −25%) |

**Range across 12 configs:** OOS Sharpe ∈ [−1.13, −0.21], OOS CAGR ∈ [−3.44%, −0.46%], OOS MaxDD ∈ [−23.93%, −8.44%]. Every config produces negative OOS Sharpe and negative OOS CAGR, so the CDI-floor soft-gate is still decisively violated.

---

## Cross-config summary (from original `AGGREGATE.md` — honest since engine was clean)

| Config | Sharpe OOS | CAGR OOS | MaxDD OOS | Sharpe FWD | CAGR FWD | Med hold (d) | WF | Swap cum | PASS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| tsmom_lb01m_vt10 | −1.13 | −2.54% | −17.42% | −1.20 | −4.93% | 41.0 | 0/8 | 73.8% | ❌ |
| tsmom_lb01m_vt15 | −1.12 | −3.40% | −23.12% | −1.22 | −7.04% | 41.0 | 0/8 | 107.1% | ❌ |
| tsmom_lb01m_vt20 | −1.04 | −3.44% | −23.93% | −1.19 | −7.71% | 41.0 | 0/8 | 131.5% | ❌ |
| tsmom_lb03m_vt10 | −0.34 | −0.68% | −9.25% | −1.27 | −5.09% | 81.5 | 3/8 | 74.7% | ❌ |
| tsmom_lb03m_vt15 | −0.40 | −1.09% | −12.39% | −1.26 | −7.19% | 81.5 | 3/8 | 109.0% | ❌ |
| tsmom_lb03m_vt20 | −0.41 | −1.25% | −13.43% | −1.12 | −7.36% | 81.5 | 3/8 | 135.2% | ❌ |
| tsmom_lb06m_vt10 | −0.22 | −0.46% | −8.44% | −2.10 | −8.86% | 128.0 | 2/8 | 81.4% | ❌ |
| tsmom_lb06m_vt15 | −0.29 | −0.83% | −11.50% | −2.03 | −12.13% | 128.0 | 2/8 | 118.7% | ❌ |
| tsmom_lb06m_vt20 | −0.31 | −1.04% | −12.80% | −1.80 | −12.51% | 128.0 | 2/8 | 147.0% | ❌ |
| tsmom_lb12m_vt10 | **−0.21** | **−0.49%** | **−10.24%** | −1.52 | −6.93% | 159.5 | 1/8 | 92.8% | ❌ |
| tsmom_lb12m_vt15 | −0.25 | −0.80% | −13.67% | −1.47 | −9.48% | 159.5 | 1/8 | 135.2% | ❌ |
| tsmom_lb12m_vt20 | −0.25 | −0.92% | −14.59% | −1.29 | −9.51% | 159.5 | 1/8 | 166.1% | ❌ |

Bolded row = least-worst config used for the gate checklist below. Even the least-worst fails 10 of 13 gates.

---

## 13-Gate Checklist (per plan §5.5, applied to least-worst `tsmom_lb12m_vt10`)

User override (locked 2026-04-22 Q&A): **Gate 3** softened from "OOS CAGR ≥ 30%" to CDI BR floor (~13%) — honest numbers must clear ≥ 13% OOS CAGR to earn PARTIAL.

| # | Gate | Threshold | Actual | Status |
|:---:|---|---|---:|:---:|
| 1 | Bootstrap 99.9% CI lower bound > 0 on OOS + full-period Sharpe | CI.low > 0 | N/A — not in original report; OOS Sharpe = −0.21 (decisively negative, any CI contains 0). Gate FAILS by construction. Skipped re-run since engine was clean. | ❌ |
| 2 | OOS Sharpe ≥ 2.0 (soft ≥ 1.5) | ≥ 2.0 | −0.21 | ❌ |
| 3 | OOS CAGR ≥ 30% (soft = CDI BR ~13%, per user override) | ≥ 13% (soft) | −0.49% | ❌ |
| 4 | OOS MaxDD ≥ −25% | ≥ −25% | −10.24% | ✅ |
| 5 | FWD Sharpe > 0 (2024–2026 stress) | > 0 | −1.52 | ❌ |
| 6 | Walk-forward 8 windows: ≥ 6/8 profitable, max window DD ≤ 25% | ≥ 6/8 & DD ≤ 25% | 1/8 profitable, max window DD 17.7% | ❌ |
| 7 | Median hold ≥ 3 trading days | ≥ 3d | 159.5d | ✅ |
| 8 | IR vs SPY ≥ 0.5 on OOS | ≥ 0.5 | N/A — not in original report; would need re-run, but skipped since engine was clean. OOS Sharpe = −0.21 vs SPY OOS Sharpe ~0.5 → IR virtually certain < 0. | ❌ |
| 9 | Cross-lib concordance ≥ 2/3 of {bt, vectorbt, backtrader} within ±3pp CAGR of canonical on OOS | ≥ 2/3 | N/A — not executed for V2-L1 (cross-lib protocol §5.3 scoped to V2-L2 per Phase 3.5c). Not bug-related; strategy DEAD before cross-lib ever mattered. | ❌ |
| 10 | Stage-2 data concordance (Tiingo adj_close vs testfolio SIM within ±1pp CAGR) | ± 1pp | N/A — not executed for V2-L1. Stage-2 protocol scoped to V2-L2. | ❌ |
| 11 | PBO < 0.5 via CSCV 10-block (grid ≥ 5 configs ⇒ applicable) | < 0.5 | N/A — not in original report. 12/12 configs OOS-negative ⇒ PBO computation moot (all configs fail base positivity; no ranking has stability). Skipped since engine was clean. | ❌ |
| 12 | DSR p-value < 0.05 on winner OOS Sharpe | p < 0.05 | N/A — no winner candidate (max OOS Sharpe is −0.21, negative ⇒ DSR is moot). Skipped since engine was clean. | ❌ |
| 13 | Cost sensitivity: cost bps × 2 ⇒ OOS Sharpe > 1.0 | > 1.0 after 2× | N/A — not run. With OOS Sharpe = −0.21 at 1× cost and swap drag already 93% cumulative, 2× cost deterministically produces worse Sharpe. Skipped since engine was clean. | ❌ |

**Gate summary:** 2/13 pass (4, 7). 11/13 fail (6 with honest numbers, 5 "N/A — not in original report; would need re-run, but skipped since engine was clean"). Honest-baseline numbers from original report were already honest (engine clean ⇒ no re-sim needed) and decisively miss the soft-gated CDI floor (need ≥ 13% OOS CAGR, actual −0.49%).

---

## Why FAIL stands (mechanism recap from original AGGREGATE)

Per the original `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/AGGREGATE.md`, three structural failures — **all independent of the engine bug** — condemn canonical monthly-rebalance TSMOM under Pepperstone Razor retail costs:

1. **Cost model vs hold length.** Median holds 41–160 days × 5 bps/day long-swap ⇒ 74–166% cumulative swap drag over 24.9y. Carver `[systematic_trading, p.185-188]` predicts retail TF optimum at 1–4 week holds; monthly rebalance × vol-targeting is structurally wrong for this cost regime.
2. **Universe composition failure.** Vol-weighting pushes allocations into the 3 USD-pair FX crosses (lowest 20d vol in the universe), which were ambushed by the 2024–2026 USD-strength regime.
3. **Walk-forward degradation with lookback.** Profitable-window ratio decays 0.38 @ 3m-lb → 0.25 @ 6m-lb → 0.12 @ 12m-lb, consistent with Carver's "no slow trend since 2011" `[systematic_trading, ch.9]`.

The F2 w×r shift **cannot rescue any of these**: swap drag is a deterministic per-bar cost independent of weight-timing; FX vol-weighting bias is a cross-sectional property of the universe, not the engine; WF degradation is a regime-level observation. None of the three failure mechanisms is an engine-timing artifact.

---

## Citations

- `[advances_fin_ml, p.31-34]` — Timing audit protocol; confirms that when the strategy module has no w×r pattern, the engine-fix leaves its metrics unchanged. Previous numbers are the honest numbers.
- `[systematic_trading, p.185-188]` — Carver retail cost model: TF optimum holds 1–4 weeks for retail costs; monthly-rebalanced TSMOM with vol-targeting produces 41–160 day holds by construction, violating the cost constraint.
- `[systematic_trading, ch.8-9]` — Canonical TSMOM family spec; "no slow trend since 2011" diagnoses the post-2008 regime failure.
- `[advances_fin_ml, p.196-202]` — DSR / bootstrap CI gates; moot when base OOS Sharpe is negative across all configs.
- `[advances_fin_ml, p.208-211]` — PBO CSCV gate; moot when 12/12 configs are OOS-negative.
- `[advances_fin_ml, ch.11]` — Walk-forward 6/8 profitable gate.

---

## Sources used

- `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/AGGREGATE.md` — honest-baseline cross-config table + diagnostic narrative.
- `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/tsmom_lb12m_vt10.json` — per-config checks (least-worst) + split metrics.
- `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/registry.json` — config registry for the 12-cell grid.
- `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md` — F1 inventory confirming `tsmom_multi_asset.py` CLEAN.
- `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md` — F3 protocol and §5.5 winner definition (13 gates).
- User override lock (2026-04-22 Q&A): gate 3 softened to CDI floor; breadth mode requires AGGREGATE.md even for confirmed-dead leads.
- F2 engine-fix commit `7b90a8f` — confirms fix is on branch but does not alter V2-L1 metrics (strategy file was CLEAN pre-fix per F1).

---

**Conclusion:** V2-L1 TSMOM remains DEAD under the honest engine because it was never affected by the w×r lookahead bug to begin with; the 2/13 gate count is identical pre- and post-F2 and the failure mechanism is a cost-model truth. No action item from V2-L1 for F3 winner hunt — proceed to next lead in §F3 priority order.
