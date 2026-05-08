# Iteration 006 — Vol-managed 60/40 SPY+TLT with inverse-variance weighting (naïve risk parity)

## Hypothesis

Iterations 004 and 005 established that **single-asset vol-adaptation on
SPY/QQQ is saturated at +0.08-0.10 Sharpe edge** regardless of the
exponent choice (`σ^{-1}` or `σ^{-2}`). The only path through the +0.10
strict gate is a **compounding mechanism** that adds an independent edge
source on top of vol-adaptation.

This iteration tests **cross-asset correlation diversification** as the
compounding axis. The strategy holds a 2-asset blend (SPY + TLT) where:

1. **Leg weights are set by naïve risk parity** — each leg's weight is
   proportional to its inverse realised variance (`w_i ∝ 1/σ²_{i,t-1}`).
   For two assets, inverse-vol weighting is the *exact* ERC solution
   (equal risk contribution) regardless of correlation
   `[risk_parity, p.10, ch.1]`.

2. **Portfolio-level leverage follows Moreira-Muir variance-scaling**
   (canonical `σ^{-2}` form from iter 005): the total gross exposure
   `s_t = clip(target_vol² / σ²_port_{t-1}, 0, cap)` — where
   `σ²_port` is the realised variance of the weighted blend over the
   same rolling window, and `cap ≤ 2.5` respects the IDM ceiling
   `[systematic_trading, p.170-171, ch.11]`.

3. **Final positions**: `position_spy_t = s_t · w_spy_t`,
   `position_tlt_t = s_t · w_tlt_t`. Total gross exposure = `s_t` (since
   weights sum to 1) — IDM-compliant by construction.

The edge source is structurally new vs iter 001-005: the **negative
stock-bond correlation** (2009-2026 realised correlation ≈ −0.4
`[risk_parity, p.80-81, ch.4]` — "USTs have strongly negative correlation
with risky assets −0.58 to −0.53 in RORO regimes") delivers
diversification return `[risk_parity, p.109-110, ch.5]`, allowing the
blend to achieve a higher Sharpe than either leg individually. Combined
with Moreira-Muir vol timing, the theoretical uplift per Carver's
multi-asset Sharpe ceiling is ~0.40 `[systematic_trading, p.46, ch.2]` —
well above SPY's benchmark 0.90.

## Primary citation

`[risk_parity, p.10-11, ch.1]` — naïve risk parity (inverse-vol
weighting) is exact ERC for two-asset portfolios regardless of
correlation. This is the canonical weighting mechanism.

## Additional citations

- `[risk_parity, p.5, ch.1]` — 60/40 variance decomposition (92% stocks /
  8% bonds risk contribution); quantitative base for why inverse-vol
  rebalances toward true risk parity.
- `[risk_parity, p.16, ch.1]` — three-leverage-level rule: unleveraged
  ~5% risk, 2:1 ~10% risk (balanced-portfolio substitute, Sharpe ~1.1
  over 1983-2004).
- `[risk_parity, p.80-81, ch.4]` — Risk-on/Risk-off regime: stock-bond
  correlation −0.58 to −0.53 in 2009-2012 (the spy_real window);
  diversification is strongest exactly when SPY is most volatile.
- `[risk_parity, p.109-110, ch.5]` — diversification return (geometric
  vs arithmetic weighted average) is non-negative for long-only
  unlevered portfolios.
- `[systematic_trading, p.40, ch.2]` — volatility standardisation is
  "the single most powerful technique" for multi-asset frameworks.
- `[systematic_trading, p.42, ch.2]` — Law of Active Management:
  Sharpe ∝ √(independent bets) — SPY + TLT ≈ 2 quasi-independent bets
  at ρ≈-0.4 → theoretical Sharpe uplift ≈ 1.4× over single-asset.
- `[systematic_trading, p.46, ch.2]` — multi-asset static portfolio
  Sharpe ceiling ≈ 0.40 (naïve); volatility-managed compound Sharpe
  target is higher.
- `[systematic_trading, p.137-148, ch.9]` — target vol as Half-Kelly.
- `[systematic_trading, p.170-171, ch.11]` — IDM max 2.5 (hard cap on
  total gross leverage to avoid correlation-crisis blow-up).
- `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` lag (no look-ahead).
- `[advances_fin_ml, p.208-211]` — PBO/CSCV (G1).
- `[advances_fin_ml, p.222-223, 275]` — DSR cumulative n_trials (G2).
- `[advances_fin_ml, p.196-202]` — stationary bootstrap (G6).
- `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
- **Moreira, A., & Muir, T. (2017).** *Journal of Finance* 72(4),
  1611-1644. DOI 10.1111/jofi.12513. Table II & IV — vol-managed
  portfolios reference; per-leg `σ^{-2}` scaling.
- **Asness, C., Frazzini, A., & Pedersen, L. (2012).** "Leverage
  Aversion and Risk Parity." *Financial Analysts Journal* 68(1),
  47-59. SSRN [1728082](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1728082).
  Shows that leveraged risk parity outperforms market-weighted equity
  on Sharpe basis 1926-2010 — supports leverage>1.0 on the blend.

## Edge source

**Negative stock-bond correlation** (ρ_SPY,TLT ≈ −0.3 to −0.5 post-2009)
produces diversification return that single-asset SPY vol-scaling cannot
touch. The Law of Active Management `[systematic_trading, p.42]`
predicts ~1.4× Sharpe uplift for 2 quasi-independent bets at ρ≈-0.4, so
the 60/40 blend with SPY 0.90 Sharpe + TLT 0.40 Sharpe should produce a
blend Sharpe ~0.75-0.85 unlevered and ~1.05-1.20 vol-managed.

## Datasets

TLT availability (2002-07-26 →) constrains the educational window.
For comparability with iter 004/005 slot semantics, retain the canonical
3-slot naming; document per-slot data:

- **educational**: SPY + TLT from 2002-07-26 to 2026-04-20 (24y window,
  longest fully-cached TLT span). Replaces iter 004/005 SPYSIM synth
  because no synth TLT exists. Custom benchmark = SPY b&h over same
  window (approx Sharpe 0.58-0.65 preliminary).
- **spy_real**: SPY + TLT from 2009-06-25 to 2026-04-20 (17y, frozen
  window). Benchmark = SPY 0.90 (frozen in scoring.BENCHMARKS).
- **ndx_real**: QQQ + TLT from 2010-02-12 to 2026-04-20 (16y, frozen
  window). Benchmark = QQQ 0.955 (frozen in scoring.BENCHMARKS).

The educational slot benchmark will be overridden via
`score_strategy(benchmarks=...)` with the measured SPY 2002-2026
benchmark; spy_real / ndx_real keep the frozen global benchmarks so the
+0.10 gate remains consistent with iter 005's scoring.

## Kill criteria (pre-committed)

If any of these triggers, the iteration is falsified independently of
secondary metrics:

1. **Sharpe edge on real data ≤ iter 005**: if `Sharpe_06_spy ≤ +0.081`
   (iter 005 spy edge) AND `Sharpe_06_ndx ≤ +0.097` (iter 005 ndx edge),
   then adding TLT did not add a compounding edge — cross-asset axis is
   exhausted at the vol-adaptation level, and the hunt must pivot to
   signal-compounding (momentum overlay) instead.
2. **Real-data MDD WORSE than bench** (`MDD_06_spy > 33.70% + 5pp =
   38.70%` OR `MDD_06_ndx > 35.12% + 5pp = 40.12%`): the 2022 bond
   crash (TLT drawdown ~-45%) made the blend MORE risky than SPY alone
   — diversification mechanism broken in this regime.
3. **Grid-level PBO on spy_real > 0.50**: the blend mechanism is as
   overfit-sensitive as single-asset — the 12-config grid didn't yield
   a structurally more stable IS/OOS ranking.

## Expected budget

- **Configs to test**: 12 (same grid shape as iter 005)
  - target_vol ∈ {0.15, 0.20} (2)
  - lookback ∈ {21, 63, 126} (3)
  - max_leverage ∈ {1.5, 2.0} (2) — both ≤ IDM ceiling 2.5
- **Trials added**: 12 × 3 datasets = 36 → cumulative 4192 + 36 = **4228**
- **Wall-time**: ~5-10 minutes (rolling variance × 24y × 12 configs
  is cheap; G6 bootstrap is the long pole at ~60s per dataset).
- **Files to create**:
  - `iterations/006-*/hypothesis.md` (this file)
  - `iterations/006-*/stock_bond_blend.py` (core sizing)
  - `iterations/006-*/run_backtests.py` (12-config grid × 3 datasets)
  - `iterations/006-*/numpy_reference.py` (G7 cross-lib)
  - `iterations/006-*/compute_gates_and_score.py` (7-gate harness)
  - `iterations/006-*/results.json` (per-run metrics)
  - `iterations/006-*/verdict.json` (score_strategy output)
  - `iterations/006-*/final_report.md` (prose)
  - `tests/test_stock_bond_blend_sizing.py` (TDD specs, ≥6)

## Implementation plan

1. **Stage 3a — TDD specs** (`tests/test_stock_bond_blend_sizing.py`):
   - `test_inverse_variance_weights_sum_to_one` — weights normalize.
   - `test_equal_variance_legs_give_5050_weights` — degenerate symmetric
     case.
   - `test_high_vol_leg_gets_smaller_weight` — monotone sanity check.
   - `test_portfolio_scale_uses_lagged_variance` — no look-ahead (the
     blend variance at bar t uses only [t-L, t-1]).
   - `test_zero_variance_port_goes_to_cap` — degenerate safety path.
   - `test_cap_clipping_respects_max_leverage` — strict upper bound.
   - `test_single_leg_degenerates_to_variance_target` — setting TLT
     returns = 0 and SPY returns ≠ 0 should reproduce iter 005 SPY-only.

2. **Stage 3b — Core sizing** (`stock_bond_blend.py`):
   - `apply_blend_variance_target(r_spy, r_tlt, target_vol, lookback,
     max_leverage)` returns `(net_returns, position_spy, position_tlt,
     scale)`.
   - Reuses `apply_variance_target` from iter 005 for leg-level rolling
     variance (imported via relative path).
   - 2 bps/unit-scale cost per leg (same as iter 005; total ≤ 4 bps
     round-trip on gross).

3. **Stage 3c — Backtest** (`run_backtests.py`):
   - Loads SPY + TLT aligned on intersection of trading days, 3 windows.
   - Loads QQQ + TLT for ndx_real.
   - Runs 12 configs × 3 datasets, writes `results.json`.

4. **Stage 3d — Numpy reference** (`numpy_reference.py`):
   - Pure-numpy re-implementation for G7 parity check (±3pp CAGR).

5. **Stage 3e — Gates + score** (`compute_gates_and_score.py`):
   - Mirrors iter 005 harness; passes custom `educational` benchmark
     derived from SPY 2002-2026 b&h at run time.
   - Writes `verdict.json` via `score_strategy().to_dict()`.

6. **Stage 4 — Evaluate** against kill criteria. Write final report.

7. **Stage 5 — Update BASE_MEMORY.md** + DEAD_ENDS.md if structural
   dead-end discovered.

## Risk to the hypothesis

- **2022 bond bear market**: TLT fell −45% peak-to-trough from 2020
  high to 2023 low. If the rolling variance lookback is too short (21d),
  the model may allocate too heavily to TLT right before the bond crash
  (when TLT vol was deceptively low from ZIRP-era). L=126 (6 months) is
  the robust default; L=21 is included for aggressiveness test.
- **Stock-bond correlation regime shift**: ρ_SPY,TLT was negative
  2002-2020 (~-0.4) but turned positive in 2022 (+0.2 to +0.3).
  If the 2022+ regime persists, the diversification edge shrinks. Test
  this with G5 FWD (post-2020 sub-sample) specifically.
- **DSR at n=4228**: The cumulative deflator at Sharpe ~1.0 requires
  ~1.4+ Sharpe to clear G2 p<0.05. Expect G2 FAIL; other 6 gates are
  the informative ones this iteration.

## Success scenarios

- **🏆 WINNER (score ≥ 90, all 5 strict conditions)**: Sharpe edge +0.10
  on ≥2 real-data slots, 5/7+4/7+4/7 gates, DSR clears, CAGR & MDD
  floors hold. Low prior (~10%) given single-asset ceiling at +0.10.
- **🥇 STRONG (75-89)**: Sharpe edge +0.10 on 1-2 slots but DSR fails;
  MDD clearly under bench. Likely outcome if the mechanism works.
- **🥈 PROMISING / 🥉 MARGINAL (40-74)**: Similar profile to iter 005
  but on a different axis — incremental knowledge, closes one more
  direction.
- **❌ FAIL (<20)**: Sharpe worse than iter 005, or blend mechanism
  confirms dead-end (TLT bear market dominates, correlation regime
  flip breaks the thesis).

## Baseline pytest

- Before iter 006: 765 passed + 5 skipped = 770 collected
- After iter 006: target 771+ passed + 5 skipped (adding 6-7 TDD
  specs in `tests/test_stock_bond_blend_sizing.py`).
