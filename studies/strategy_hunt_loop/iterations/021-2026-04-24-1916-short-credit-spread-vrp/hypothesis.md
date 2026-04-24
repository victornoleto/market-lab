# Iteration 021 — Short put credit spread (VRP harvest) overlay on iter 016 base

## Hypothesis

On the iter 016 base (static 60:40 SPY+IEF stack with Moreira-Muir
variance-target scaling at vt15/L21/cap20), **SELL** a monthly-rolled
5/10% OTM put credit spread on the equity leg instead of buying it.

Iter 020 showed that BUYING the exact same spread costs 3.0-4.1%/yr
(Sharpe regress −0.04 to −0.08, MDD WORSE 3-6pp) because convex
long-gamma P&L is redundant with vol-target's variance-responsive
de-leveraging — both fire on σ² spikes.

This iteration tests the **structurally opposite side**: collecting
the variance risk premium (VRP) by writing the spread. The
Bondarenko (2014) volatility risk premium estimate is +3%/yr for SPX
30-DTE ATM puts, and the CBOE PUT index (PUTW, WPUT) systematically
writes short-dated SPX puts with historical Sharpe 0.80-1.0 vs SPY.
Theta accrues during calm regimes (most months) in a P&L stream
structurally DIFFERENT from iter 016's realized-variance signal:
theta is forward-looking IV-driven, not backward-looking RV. The two
are empirically correlated during crashes but algebraically disjoint
at the feature level.

Mechanism (ceteris paribus vs iter 020, sign reversed):

- **Short** 1 put at `K_short_harvest = 0.95 × S_entry` (5% OTM)
- **Long** 1 put at `K_long_harvest = 0.90 × S_entry` (10% OTM, tail cap)
- Roll every 21 trading days (~1 month)
- IV = VIX (SPX), VIX×1.1 (NDX proxy)
- Cost 5 bps per roll (same as iter 020)

Implementation: reuse iter 020's `apply_put_spread_hedged_stack`
with `hedge_notional_ratio = −1.0`. Zero new simulator math — the
sign flip is the ceteris paribus test.

Kill criteria (pre-committed) — any ONE falsifies the hypothesis:

1. **Kill #1 (VRP fails to materialize)** — Overlay annualized
   return < +1.5%/yr on ≥ 2 of 3 ds. If VRP disappears (e.g.,
   because the 5/10% strikes price theta too low), mechanism is dead.
2. **Kill #2 (crash drag dominates theta)** — Δ Sharpe vs iter 016
   ≤ 0.00 on ≥ 2 of 3 ds. Any neutral-or-negative Sharpe delta kills.
3. **Kill #3 (DSR degrades)** — DSR worst p > 0.30 (worse than iter
   016's 0.226 by a meaningful margin).
4. **Kill #4 (MDD explodes)** — MDD > iter 016 + 5pp on ≥ 2 of 3 ds
   (crash months dominate beyond vol-target's offset).

## Primary citation

`[volatility_trading, ch.3]` — Variance Risk Premium harvesting
mechanics (IV systematically higher than subsequent RV; short-vol
premium; tail-risk characteristics).

## Additional citations

- `[volatility_trading, p.11]` — Black-Scholes pricing; IV as the σ
  reproducing market price.
- `[volatility_trading, p.41]` — SPX fat-tail kurtosis 21.3 — justifies
  capped (credit-spread) vs uncapped short put.
- `[risk_parity, p.10-11, ch.1]` — iter 016 base (fixed 60:40 stack).
- `[systematic_trading, p.40, ch.2]` — vol standardisation primitive
  (inherited unchanged from iter 016).
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag discipline on
  vol-target; IV is contemporaneous but pricing uses same-bar close
  (no future bar accessed in the overlay return stream).
- Bondarenko, O. (2014). **"Why Are Put Options So Expensive?"**
  Quarterly Journal of Finance, 4(3). SSRN: 1530766 — empirically
  establishes VRP ≈ 2-3%/yr annualized from systematic SPX put
  writing.
- Moreira & Muir (2017). JoF 72(4), 1611-1644 — vol-target scaling.
- Carr, P. & Madan, D. (1999). "Towards a Theory of Volatility
  Trading" — static replication of convex payoffs (structural
  orthogonality argument).
- CBOE PUT Index methodology paper — monthly ATM SPX put-write
  benchmark that CBOE has maintained since 1988; serves as empirical
  prior that VRP harvest is robust OOS.

## Edge source

SPY 1x buy-hold cannot separate *forward* implied volatility from
*backward* realized volatility. A short put credit spread explicitly
monetises the gap (IV − RV > 0 on average) through theta accrual
during calm regimes, in a way that's linearly independent from both
the long-equity premium (captured by the 60:40 ratio) and the
realized-variance term-structure (captured by vol-target). The two
scalers in iter 016 see σ²_RV; the VRP overlay sees σ²_IV − σ²_RV —
a different signal.

## Datasets

- **educational** (SPY+IEF 2006-01-03 → 2026-04-14, ~20y IEF-inception):
  contains 2008 GFC + 2011 eurozone + 2015-16 oil rout + 2018 Q4 +
  COVID 2020 + 2022 bear — 5 distinct crash regimes stress-test VRP
  harvest's tail exposure.
- **spy_real** (SPY+IEF 2009-06-25 → 2026-04-14): post-GFC-bull + 2018
  Q4 + COVID + 2022 — matches iter 016 frozen window exactly.
- **ndx_real** (QQQ+IEF 2010-02-12 → 2026-04-14): tech-heavy
  higher-vol regime (IV runs ~10% above SPX → `iv_scale=1.1`).

## Expected budget

- Configs to test: 1 single pre-committed cfg `ntsx_vm_vt15_L21_cap20_scs5_10_1m`
  (no grid, no sweep; minimum n_trials incremented +3 for cumulative)
- Wall-time: ~15-20 min (reuses iter 020 scaffolding 1:1)
- Files to create:
  - `short_credit_spread_overlay.py` — thin semantic wrapper (pins
    `hedge_notional_ratio=-1.0`)
  - `run_backtests.py` — 3-dataset single-cfg runner (copied from iter
    020 with renamed cfg)
  - `compute_gates_and_score.py` — 7-gate battery + scoring
  - `final_report.md` + `verdict.json`
- Test to add: `tests/test_short_credit_spread_overlay.py` (1 test —
  ratio -1.0 inverts overlay sign exactly)

## Implementation plan

1. TDD test `test_short_credit_spread_overlay.py` — given fixed
   (prices, VIX), assert `apply_short_credit_spread_stack` with
   default ratio returns NET stream equal to iter 020's
   `apply_put_spread_hedged_stack(..., hedge_notional_ratio=-1.0)`
   stream, modulo the equity leg (since both will be identical when
   the sign is properly flipped through the vol-target).
2. Implement `short_credit_spread_overlay.py` — import iter 020's
   `apply_put_spread_hedged_stack` and define
   `apply_short_credit_spread_stack(...)` pinning
   `hedge_notional_ratio=-1.0`. Document semantic shift in docstring
   (harvest vs hedge).
3. Implement `run_backtests.py` — copy iter 020's, change cfg_id +
   import source. Run 3 datasets. Save `results.json` with same
   schema + `returns_series[ds][cfg_id]`.
4. Implement `compute_gates_and_score.py` — copy iter 020's pattern
   for the 7 gates + scoring. Verify G7 cross-lib parity by calling
   iter 020's `apply_put_spread_hedged_stack_np` (numpy reference)
   with `hedge_notional_ratio=-1.0` — same ceteris paribus test.
   Bump `cumulative_n_trials = 4267 + 3 = 4270`.
5. Run `plot_helper.py --iter 021`. Write `final_report.md` +
   update `BASE_MEMORY.md`.
