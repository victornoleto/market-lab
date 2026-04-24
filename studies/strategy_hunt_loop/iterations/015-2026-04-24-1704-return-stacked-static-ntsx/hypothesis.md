# Iteration 015 — Static synthetic NTSX (90/60 SPY+IEF stack) buy-and-hold

**Date:** 2026-04-24 17:04
**Slug:** `return-stacked-static-ntsx`
**Cumulative n_trials before iter 015:** 4255

---

## Hypothesis

Test the **return-stacking primitive in pure form**: a synthetic NTSX
construct = `0.90 × equity + 0.60 × IEF` (intermediate UST), daily-
rebalanced to fixed weights, **single pre-committed config**, NO
overlay, NO vol-management, NO rotation. The intent is to quantify
whether the stacking primitive — fixed-weight 1.5× leveraged 60/40
exposure with intrinsic leverage that does NOT respond to portfolio
realised vol — provides a structurally distinct risk-adjusted
performance profile vs SPY 1× buy-hold AND vs iter 008's dynamic-
weight vol-managed blend.

This is a **mechanism-change iteration**: BASE_MEMORY identifies four
consecutive overlay failures on iter 008's blend (009 T10Y3M sym /
012 T10Y3M asym / 013 LR meta / 014 EBP credit) all closing with the
same business-cycle cointegration with σ²_port. The overlay family is
closed. Iter 015 must change MECHANISM, not decorate iter 008 again.
Static fixed-weight stacking has no σ²_port self-adjustment response,
so it is structurally outside the cointegration trap.

---

## Primary citation

`[risk_parity, p.5, ch.1]` — Asness-Frazzini-Pedersen (2012) risk-
parity argument: levering up the diversified portfolio captures more
diversification per unit of total risk than leaving it unlevered.
Static stacked exposure is the simplest empirical instantiation.

## Additional citations

- `[risk_parity, p.10-11, ch.1]` — naïve risk parity weights as
  diagonal-covariance optimum.
- `[leverage_for_the_long_run, p.19-20]` — leverage applied to a
  diversified base captures duration risk-premium without market-timing.
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials accounting.
- Asness, C., Frazzini, A., & Pedersen, L. (2012). "Leverage Aversion
  and Risk Parity." *Financial Analysts Journal* 68(1), 47-59.
  SSRN [1728082](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1728082).
- WisdomTree NTSX product literature: 90 % equity + 60 % UST futures
  stacked in single ETF wrapper, launched 2018-08-02. Synthetic proxy
  pre-2018 standard in industry studies.

## Edge source

In ONE sentence: **SPY 1× buy-hold is unhedged equity beta concentrated
100 % in one factor; static 1.5×-leveraged 90/60 SPY+IEF provides
constant 60 % bond-duration exposure that absorbs equity drawdowns
without any regime-detection lag because no signal/timing layer is
needed — the diversification is structural rather than dynamic.**

---

## Datasets

| dataset | window | universe | rationale |
|---|---|---|---|
| educational | 2006-01-03 → 2026-04-15 | SPY + IEF | IEF-inception-aligned (~20y); follows iter 010's window-constrain pattern |
| spy_real | 2009-06-25 → 2026-04-15 | SPY + IEF | 17y post-GFC, full benchmark window |
| ndx_real | 2010-02-12 → 2026-04-15 | QQQ + IEF | 16y tech-heavy, sanity check across equity universe |

Educational benchmark will be re-measured on the IEF-aligned window
(matches iter 010's `build_custom_benchmarks` pattern). Spy_real and
ndx_real benchmarks remain frozen to `scoring.BENCHMARKS`.

---

## Pre-committed single config

| param | value | citation / rationale |
|---|---|---|
| `cfg_id` | `ntsx_synth_90_60_daily` | descriptive |
| `equity_weight` | 0.90 | NTSX prospectus exact |
| `bond_weight` | 0.60 | NTSX prospectus exact |
| `total_leverage` | 1.50 | sum of legs (intrinsic via futures stacking in real NTSX) |
| `rebalance` | daily | maintain fixed weights against price drift |
| `cost_bps_per_leg` | 0.0002 | 2 bps per unit per-leg ∆position (same as iter 010) |
| `funding_cost` | NOT modeled | optimistic bias; documented in final report |

Funding-cost simplification: real NTSX pays ~0.5 × short-rate as
implicit financing on the 50 % additional notional. Synthetic version
ignores this for cleanliness, which OVERESTIMATES the strategy's
edge by an estimated 50-100 bps annually depending on regime. A
sensitivity comment in the final report will quantify the impact.

**Why a single config (no grid)**: NTSX has prescribed weights baked
into the product (90/60 is the manufacturer's choice). There is no
parameter to tune, no PBO concern, no DSR n_trials inflation beyond
the 3 datasets. Mirror of iter 008/010 single-cfg discipline.

---

## Kill criteria (pre-committed)

If any of these triggers, the iteration is falsified independent of
secondary metrics:

- **Kill #1 (PRIMITIVE-NEUTRAL)**: Sharpe Δ vs SPY < +0.05 on ≥ 2 of
  3 datasets. The stacking primitive in pure form does NOT add Sharpe
  beyond the equity benchmark; it functions only as a CAGR amplifier.
  Score will be capped MARGINAL.
- **Kill #2 (STACK-DOMINATED-BY-VOL-MGMT)**: Sharpe Δ vs iter 008's
  baseline (educational 0.865 / spy 1.000 / ndx 1.021) < −0.10 on ≥ 2
  of 3 datasets. The dynamic vol-management mechanism dominates static
  stacking on a like-for-like comparison. Future stacking iterations
  must add a timing/rotation layer to compete.
- **Kill #3 (SUB-MARGINAL)**: total score < 60.

Crucially: **score < 70 is NOT an automatic kill** for this iteration
— the value of the iteration is in establishing a baseline for the
stacking primitive, not in winning. A 50-65 score that cleanly
characterises the primitive is more useful than a 75 score on a
superseded mechanism.

---

## Expected budget

- Configs to test: 1 (single pre-committed cfg, mirrors iter 008/010)
- Datasets: 3 → 3 cumulative n_trials added (4255 → 4258)
- Wall-time estimate: 30-45 min total
  - Implementation + TDD specs: ~15 min (mechanism is trivially simpler than iter 010's vol-managed blend)
  - Run + gates: ~5 min (no lookback dependencies, fully vectorised)
  - Final report + BASE_MEMORY update: ~10 min
- Files to create:
  - `synth_stacked_etf.py` — pure-pandas synthetic NTSX
  - `numpy_reference_stacked.py` — pure-numpy hand-rolled reference for G7 cross-lib parity
  - `tests/test_synth_stacked_etf.py` — TDD specs (≥ 6 specs covering core math, weight invariance, no-lookahead, cost wiring, numpy parity, edge cases)
  - `run_backtests.py` — pattern from iter 010
  - `compute_gates_and_score.py` — pattern from iter 010
  - `results.json` + `verdict.json` — outputs
  - `final_report.md` — prose verdict

---

## Implementation plan

1. **Write TDD specs first** (`tests/test_synth_stacked_etf.py`) —
   lock semantics before implementation:
   - `test_static_weights_sum_to_total_leverage()` — at every bar, equity_pos + bond_pos == 1.5
   - `test_zero_returns_yields_zero_net_returns()` — pure stack of constant series
   - `test_equity_only_recovers_spy_at_eq_weight_one()` — degenerate eq_w=1.0, bd_w=0.0 mirrors SPY exactly
   - `test_no_lookahead_in_position_application()` — position at t applied to return at t (no t+1 sneak)
   - `test_cost_scales_with_position_change()` — daily rebalance cost = |∆pos| × bps × 2 legs
   - `test_numpy_reference_matches_pandas_engine_to_1e_10()` — G7-style parity at sample size
2. **Implement `synth_stacked_etf.py`** — `apply_static_stack(r_eq, r_bd, eq_w=0.9, bd_w=0.6, cost_bps=0.0002)` returns `(net_returns, positions, scale)` mirroring iter 010's signature for plug-and-play compatibility with `compute_gates_and_score.py`.
3. **Implement `numpy_reference_stacked.py`** — pure-numpy hand-rolled re-implementation, used by G7.
4. **Run pytest** — confirm all new specs pass + baseline unchanged.
5. **Run backtests** — `python3 run_backtests.py` produces `results.json`.
6. **Run gates + scoring** — `python3 compute_gates_and_score.py` produces `verdict.json`.
7. **Write `final_report.md`** — prose verdict with structural lessons.
8. **Update `BASE_MEMORY.md`** — bump iter, append entry, prune if needed, update top-K + promising directions.
9. **Update `DEAD_ENDS.md`** — add structural finding (only if FAIL).
10. **Update `jornada/`** — write entry per CLAUDE.md Regra 1.

---

## What outcome teaches us

| outcome | interpretation | next iter direction |
|---|---|---|
| Sharpe ≥ +0.10 vs SPY on ≥ 2 ds | **Stacking primitive alone wins** — surprising; investigate funding-cost robustness, then layer rotation for 90+ score | Test sensitivity to funding cost; iter 016 → add rotation across NTSX/NTSI/NTSE_synth |
| Sharpe edge +0.05 to +0.09 | Primitive helps, partially; static stack is a meaningful CAGR-vs-MDD trade vs SPY | Iter 016 → static stack + signal overlay (12-1 momentum or VIX term) |
| Sharpe edge < +0.05 (Kill #1) | Stacking alone doesn't add Sharpe; CAGR up + MDD up cancel. Must combine with timing | Iter 016 → require dynamic component (rotation, signal, vol-target) |
| Sharpe Δ vs iter 008 < −0.10 (Kill #2) | Dynamic vol-management dominates static stacking | Iter 016 → revert to vol-managed mechanism; explore options-implied or cross-sectional axes for orthogonal info |
