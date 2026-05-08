# Lead V2-L5 — Kalman pair cointegration (honest reconfirm, phase 3.5f)

**Phase:** phase_3_5f / honest_revalidation
**Lead:** V2-L5 (Kalman pair cointegration, daily, Tiingo)
**Date:** 2026-04-22
**F2 engine commit:** `7b90a8f` (look-ahead fix in `plano_a_leveraged_rotation.py:462`)
**Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`
**Slice:** F3 V2-L5 (plan §F3, §5.5)
**Original DEAD report:** `reports/phase3_5a_v2/v2_l5_equity_pairs/AGGREGATE.md` (iter 66, 2026-04-19)

---

## Verdict

**FAIL (reconfirmed — structural failure + engine was clean).**

Strategy has ZERO tradable pairs under the L5 universe/spec. The F2
look-ahead fix is irrelevant when there are no trades to simulate.
DEAD verdict is **structurally independent of engine math**.

---

## Why this reconfirm required zero simulation

F1 inventory (`docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md`)
audited `src/ai_trade/backtest/strategies/kalman_pair_cointegration.py`
and listed it as **CLEAN** — it is a pair stat-arb with a different
return computation (residual z-score on spread), not the `w_i × r_i`
leveraged-rotation pattern where the look-ahead bug lived. The F2 fix
at `plano_a_leveraged_rotation.py:462` (`7b90a8f`) does not touch this
strategy's code path.

Additionally, the original V2-L5 run (iter 66) established the failure
**upstream of the engine**: the Engle-Granger / ADF gate rejected all
6 candidate pairs (0 passed `p ≤ 0.05`). When ADF rejects, no trades
are generated — engine math is never exercised. A clean-engine re-run
would therefore reproduce exactly the same 0-trade, 0-metric result
with bit-identical numbers `[advances_fin_ml, p.31-34]`.

Per plan §F3 / §5.5 guidance and the F1 CLEAN verdict, no resimulation
was performed.

---

## Summary table (carried from iter 66 original DEAD)

Universe: 6 ETF pairs (Pepperstone-CFD-adjacent), daily Tiingo cache,
period 2001-05-14 → 2026-04-14. Spec: Engle-Granger OLS → ADF on
residual `u_t = log(y) - α - β·log(x)` → gate `p ≤ 0.05` → Kalman
β + 2σ/0σ/4σ bands + 30d hold cap + Pepperstone Razor costs.

| Pair    | Window (y) | Bars | ADF stat | ADF p   | OLS β  | Kalman β | Cointegrated | Trades | PASS |
|---------|------------|------|----------|---------|--------|----------|--------------|--------|------|
| GLD_SLV | 20.0       | 5021 | -2.239   | 0.192   | 0.898  | 0.485    | NO           | 0      | NO   |
| QQQ_XLK | 22.6       | 5698 | -1.237   | 0.658   | 1.014  | 0.945    | NO           | 0      | NO   |
| SPY_IWM | 24.9       | 6266 | -2.504   | 0.115   | 1.121  | 0.802    | NO           | 0      | NO   |
| TLT_IEF | 12.3       | 3088 | +0.819   | 0.992   | 1.675  | 1.671    | NO           | 0      | NO   |
| XLE_USO | 20.0       | 5034 | -1.546   | 0.511   | -0.137 | 0.536    | NO           | 0      | NO   |
| XLF_HYG | 12.3       | 3088 | -2.697   | 0.0746  | 2.666  | 1.563    | NO (closest) | 0      | NO   |

**Cointegrated pairs:** 0 / 6.
**Total trades generated:** 0.
**Metrics computable:** none (CAGR, Sharpe, MDD, hold, WF all undefined
with 0 trades — the engine is never entered).

---

## 13-gate checklist (phase 3.5f honest revalidation framework)

With 0 trades, no metric has a sample. Gates are N/A (no data to
evaluate) or FAIL-by-default where a positive threshold is required
and the absence of trades cannot satisfy it. CDI-floor soft-gate and
breadth-mode (user override locked 2026-04-22 Q&A) likewise cannot be
evaluated — there is no return series.

| # | Gate                                | Result | Reason                                                        |
|---|-------------------------------------|--------|---------------------------------------------------------------|
| 1 | `oos_sharpe_gt_0`                   | FAIL   | 0 trades → Sharpe undefined; fails-by-default.                |
| 2 | `oos_sharpe_ge_2`                   | FAIL   | Same — no distribution to score.                              |
| 3 | `oos_cagr_ge_30pct`                 | FAIL   | 0 trades → CAGR = 0 < 30%.                                    |
| 4 | `oos_cagr_ge_cdi` (CDI-floor soft)  | FAIL   | CAGR = 0 < CDI ≈ 13-14%/yr (user override, breadth mode).     |
| 5 | `oos_maxdd_le_25pct`                | N/A    | Trivially satisfied (no equity drawdown), not informative.    |
| 6 | `fwd_sharpe_gt_0`                   | FAIL   | Forward window has 0 trades.                                  |
| 7 | `wf_pass` (walk-forward ≥6/8)       | FAIL   | All 8 windows have 0 trades → 0/8.                            |
| 8 | `median_hold_ge_3d`                 | FAIL   | No trades → no hold distribution.                             |
| 9 | `pbo_lt_0_5` (PBO overfit)          | N/A    | No config-return matrix (all configs deterministically 0).    |
| 10| `dsr_p_lt_0_05` (Deflated Sharpe)   | N/A    | No Sharpe distribution to deflate.                            |
| 11| `single_block_oos`                  | FAIL   | No OOS returns in any contiguous block.                       |
| 12| `forward_window_stress`             | FAIL   | Stress window has 0 trades.                                   |
| 13| `structural_tradability`            | FAIL   | **Primary failure — 0/6 pairs pass ADF; no trades possible.** |

**Score:** 0 / 13 PASS. **Strategy DEAD.**

---

## Explicit statement (plan §F3 requirement 5)

> **Strategy V2-L5 (Kalman pair cointegration, daily) has ZERO tradable
> pairs under the L5 universe/spec (6 ETF pairs, ADF gate `p ≤ 0.05`).
> The F2 engine look-ahead fix (`7b90a8f`, `plano_a_leveraged_rotation.py:462`)
> is irrelevant when there are no trades to simulate. The DEAD verdict
> is structurally independent of engine math: the failure occurs
> upstream at the ADF cointegration gate, before any position, PnL, or
> return computation ever runs. F1 audit also confirmed
> `kalman_pair_cointegration.py` is CLEAN (different return-computation
> path; not the `w_i × r_i` leveraged-rotation pattern the bug lived
> in). No resimulation warranted.**

---

## Interpretation (carried; still correct)

The spreads tested are **I(1)** (random walks correlated), not
stationary `[algo_trading_chan, p.42-54]`, `[machine_trading_chan, ch.3]`.
Chan (2013) already refuted the same sector pairs. XLF/HYG was
closest (p=0.0746) but its β=2.67 is economically anomalous, and the
2022-2024 Fed hiking cycle broke parity (HYG ↓ by duration vs XLF ↑
by NIM expansion). The Pepperstone CFD universe (blue-chip global
ETFs + majors FX) structurally lacks the micro-cap / cross-listed
ADR instruments where pair-trading retains edge `[algo_trading_chan, p.46]`.

---

## Citations

- `[advances_fin_ml, p.31-34]` — audit / reconfirm discipline:
  distinguish upstream structural failure from engine-math failure;
  do not resimulate when gating stage rejects all candidates.
- `[advances_fin_ml, ch.7]` — non-stationarity in financial series;
  ADF requires structural stationarity over the sample.
- `[algo_trading_chan, p.42-54]` — pair-trading in liquid ETFs: edge
  erased by institutional arbitrage; cointegration test as primary
  gate (original spec anchor).
- `[machine_trading_chan, ch.3]` — Kalman dynamic β for pair trading;
  mature liquid ETFs routinely register as negative cases.
- `[systematic_trading, p.185-188]` — retail CFD cost structure;
  trade-infrequency intolerant without clear edge.

---

## Links

- Original DEAD report: `reports/phase3_5a_v2/v2_l5_equity_pairs/AGGREGATE.md`
- Original jornada (verdict narrative):
  `jornada/2026-04-19/05-phase3.5a-v2-L5-equity-pairs-DEAD.md`
- Original sweep-complete narrative (XLF/HYG as closest):
  `jornada/2026-04-19/04-phase3.5a-v2-L5-xlf-hyg-FAIL-sweep-complete.md`
- F1 engine scope finding (L5 listed CLEAN):
  `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md`
- F2 engine fix commit: `7b90a8f`
