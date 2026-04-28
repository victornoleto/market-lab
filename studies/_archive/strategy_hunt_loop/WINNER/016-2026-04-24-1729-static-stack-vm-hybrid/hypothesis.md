# Iteration 016 — Static 90/60 SPY+IEF stack × Moreira-Muir variance-target scaling (hybrid)

## Hypothesis

Combine iter 015's **static fixed-ratio stack** (0.9 SPY + 0.6 IEF,
ratio 90:60 preserved constant) with iter 008's **Moreira-Muir
portfolio-level variance-target scaling**. At each bar the overall
gross exposure is rescaled by `scale[t] = clip(target_vol² /
σ²_port[t-1], 0, max_lev)` while the 60:40 NORMALISED weight ratio
stays locked. Mechanism math:

    w_eq_fixed = 0.6   # normalised (0.9 / 1.5)
    w_bd_fixed = 0.4   # normalised (0.6 / 1.5)
    σ²_port[t-1] = 0.36·σ²_eq[t-1] + 0.16·σ²_bd[t-1]
                 + 2·0.6·0.4·cov_eq_bd[t-1]
    scale[t] = clip(target_vol² / σ²_port[t-1], 0, max_lev)
    pos_eq[t] = 0.6 · scale[t]      # iter 015 reproduced at scale=1.5
    pos_bd[t] = 0.4 · scale[t]

When `scale[t] = 1.5`, the strategy reproduces iter 015's static stack
exactly. When realised vol is low, `scale` expands (up to `max_lev`
cap) to compensate for the conservative static 1.5× leverage; when
vol spikes, `scale` contracts below 1.5 to cut exposure. This attacks
the DSR ceiling via the observed-Sharpe side by buying low-vol regime
uplift without reopening the cointegration trap — unlike iter
009/012/013/014, Option P adds NO external signal: `scale[t]` IS the
only dynamic rule, and it's a function of the portfolio's OWN
realised vol (the thing a vol-target should respond to).

The rationale: iter 015 scores 77/100 STRONG, clears +0.10 Sharpe on
3/3 datasets, but fails DSR (worst p=0.548). Static leverage is
constant 1.5× regardless of regime. Post-2010 the realised σ²_port
averaged ~0.10² (half the target_vol²) — meaning iter 015 was
routinely under-levered during low-vol regimes. Rescaling would
lift gross exposure to ~2.0× during those stretches and cut it
during 2008/2020/2022 spikes — multiplicative Sharpe uplift expected
where low-vol regimes dominate.

## Primary citation

`[risk_parity, p.10-11, ch.1]` — fixed-weight stacking; also
`[systematic_trading, p.40, ch.2]` — variance standardisation as
sizing primitive.

## Additional citations

- `[risk_parity, p.5, ch.1]` — Asness-Frazzini-Pedersen risk-parity
  leverage argument on diversified base.
- `[leverage_for_the_long_run, p.19-20]` — leverage on diversified
  base captures duration premium without market-timing.
- `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 hard cap on
  total gross exposure (we use 2.0).
- `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` lag (no look-ahead).
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
- `[advances_fin_ml, p.208-211]` — single-cfg vacuous PBO PASS.
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials accounting.
- Web: Moreira, A., & Muir, T. (2017). "Volatility-Managed
  Portfolios." *Journal of Finance* 72(4), 1611-1644.
  DOI [10.1111/jofi.12513](https://doi.org/10.1111/jofi.12513).
- Web: Asness, C., Frazzini, A., & Pedersen, L. (2012). "Leverage
  Aversion and Risk Parity." *FAJ* 68(1), 47-59. SSRN 1728082.

## Edge source

SPY 1x buy-hold fails to capture **low-vol-regime leverage expansion**
(post-2017 realised vol ~0.11, far below the 0.15 target) AND fails
to capture **stock-bond diversification** (SPY-IEF ρ ≈ −0.30). The
hybrid simultaneously exploits both: iter 015 captured the
diversification axis at constant 1.5× exposure; Option P adds the
low-vol expansion axis on top. Dynamic leverage on a diversified
base — the same reason iter 008 beat single-asset vol-scaling
(iter 004/005).

## Datasets

- **educational**: SPY + IEF, 2006-01-03 → 2026-04-15, ~5100 bars
  (IEF-inception-aligned; same window as iter 015 for apples-to-apples
  comparison)
- **spy_real**: SPY + IEF, 2009-06-25 → 2026-04-15, ~4226 bars
  (post-GFC, same as iter 015)
- **ndx_real**: QQQ + IEF, 2010-02-12 → 2026-04-15, ~4066 bars
  (tech-heavy, same as iter 015)

Cross-dataset is non-negotiable. Iter 015 comparison windows are
preserved.

## Kill criteria (pre-committed)

Falsify this hypothesis IF any of the following holds at end of
Stage 3:

- **Kill #1**: Sharpe regresses vs iter 015 by > 0.02 on ≥ 2 of 3
  datasets → vol-mgmt provides no uplift on top of static stack
  (either redundant or harmful). Treat as FAIL, add "static × vol-mgmt
  hybrid" as the 5th closed overlay family on iter 008-lineage.
- **Kill #3**: Total score < 72 (> 5 pts below iter 015's 77).
  Indicates one of the criteria regressed materially.
- **Kill #4**: MDD regresses vs iter 015 by > 5 pp on ≥ 2 datasets →
  the vol-mgmt is degrading (not improving) downside protection,
  suggesting the scaling rule is destabilising exposure in stressed
  regimes rather than dampening it.

If ANY of these triggers, iter 016 is FAIL regardless of the other
criteria, and the lesson recorded is that combining iter 008's
scaling with iter 015's ratio lock-in does NOT produce additive
edge — the two mechanisms are fungible, not complementary.

## Expected budget

- Configs to test: **1** pre-committed (`ntsx_vm_vt15_L21_cap20`),
  matching iter 008 params (target_vol=0.15, lookback=21, max_lev=2.0)
  so the only structural change vs iter 008 is the fixed vs dynamic
  weight ratio.
- Trials: 1 cfg × 3 datasets = **3** trials; cumulative n_trials
  4258 → 4261.
- Wall-time: ~20 minutes (reuse iter 015 scaffolding + iter 008
  scaling logic).
- Files to create:
  - `static_stack_vm.py` — simulator combining iter 015's ratio with
    iter 008's scaling
  - `numpy_reference_stack_vm.py` — hand-rolled numpy parity check (G7)
  - `run_backtests.py` — adapted from iter 015
  - `compute_gates_and_score.py` — adapted from iter 015
  - `results.json`, `verdict.json`, `final_report.md`
  - `tests/test_static_stack_vm.py` — TDD specs (≥ 8 specs for the
    new simulator math + edge cases)

## Implementation plan

1. Write TDD spec file `tests/test_static_stack_vm.py` with at
   least: (a) constant-ratio assertion, (b) scale formula invariant
   vs manual calc, (c) no-lookahead (bar `t` uses `σ̂_{t-1}`), (d)
   cost accounting, (e) degenerate `σ² == 0` handled, (f) cap
   binding, (g) recovers iter 015 when `max_lev = 1.5` AND
   `target_vol = ∞` (i.e., scale always hits cap), (h) cross-lib
   parity within 1e-9.
2. Implement `static_stack_vm.py::apply_static_stack_vol_managed(...)`.
3. Write `numpy_reference_stack_vm.py` — independent hand-rolled
   implementation in pure numpy arrays (no pandas).
4. Adapt `run_backtests.py` from iter 015, run on 3 datasets, dump
   to `results.json`.
5. Adapt `compute_gates_and_score.py` to run 7-gate battery + score.
6. Write `final_report.md` + `verdict.json`.
7. Update `BASE_MEMORY.md` (frontmatter, iteration log, top-K,
   directions, dead-ends if applicable) and apply the 18 KB
   auto-prune rule.

## Structural novelty check vs DEAD_ENDS.md

- **Iter 007 (TS momentum on vol-managed blend)**: iter 016 adds NO
  external signal; scaling is intrinsic to portfolio vol, not a
  momentum overlay. ✅ distinct.
- **Iter 009/012/013/014 (overlays on iter 008 blend)**: those
  failures all add an EXTERNAL signal (T10Y3M, LR classifier, EBP)
  on top of a vol-managed blend. Iter 016 has no such second signal.
  ✅ distinct.
- **Iter 011 (weekly cadence)**: iter 016 is daily. ✅ distinct.
- **Iter 006 (12-cfg grid)**: iter 016 is single-cfg pre-committed.
  ✅ distinct (and learns from iter 008's single-cfg discipline).
- **Iter 010 (3-leg blend)**: iter 016 is 2-leg. ✅ distinct.

**Novelty relative to closest neighbours**:

- Vs iter 008 (inverse-variance weights + scaling): iter 016 locks
  RATIO to iter 015's NTSX 60:40, preserving static-stack's
  cointegration-free property while adding iter 008's dynamic
  exposure. Different σ²_port formula (fixed vs dynamic weights).
- Vs iter 015 (fixed weights, constant 1.5×): iter 016 adds vol-
  responsive exposure scaling. Same ratio, different total leverage.
