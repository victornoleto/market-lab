# Iteration 010 — Three-asset vol-managed SPY+TLT+GLD blend (N=1 ex-ante)

## Hypothesis

Iter 008 demonstrated that iter 006's vol-managed SPY+TLT blend edge is
**structural** (not grid-selected). Single-cfg pre-commitment preserved
Sharpe +0.20 / +0.10 / +0.07 on edu/spy/ndx, scored 74/100 PROMISING,
and left only **DSR** as the killer gate (worst p=0.332 at cumulative
n_trials=4240 — deflator structurally unreachable at Sharpe uplift
~+0.10).

Two overlay attempts since then — iter 007 (12-1 momentum) and iter 009
(T10Y3M smoothed term-spread) — **both failed** because the overlay was
REDUNDANT with the blend's own variance-scaling regime sensitivity
(both correlated + smoothed signals duplicate what σ²_port already
captures). Iter 009's final report explicitly concludes:

> "The productive path is structural extension (3-asset blend), not
> more overlays."

**Iter 010 claim:** adding a third leg (GLD) with near-zero correlation
to both SPY and TLT changes the diversification-return axis
structurally, not via signal overlay. The blend's inverse-variance
weighting naturally accommodates 3 legs (naïve risk parity generalises
to N≥2, `[risk_parity, p.10-11, ch.1]`), and the Moreira-Muir
portfolio-level variance-scaling applies unchanged to the 3-leg
σ²_port. Gold adds a real-asset / inflation-hedge factor uncorrelated
with both equity and Treasury-bond cycles — a structurally new
diversification axis.

**Expected effect** on iter 008 baseline:

- **Sharpe uplift +0.03 to +0.10** from real-asset diversification
  (Ilmanen *Expected Returns* and Asness-Frazzini-Pedersen 2012 risk-
  parity cross-asset literature).
- **MDD reduction** from 2008-2009 and 2022 equity + bond
  simultaneous drawdowns (gold held up in both).
- **CAGR neutral to +1pp** — target_vol cap (0.15) limits scale
  inflation even with extra diversification.
- **DSR path**: if Sharpe edu/spy/ndx climb by +0.03-0.05 respectively,
  the deflator's worst p-value should drop from 0.332 to ~0.20-0.25 —
  still not winning, but the trajectory matters.

This is the **structural-extension** path (Option D in BASE_MEMORY's
iter 010 candidate list), explicitly recommended by iter 009's orchestrator
as highest expected information gain.

## Primary citation

`[risk_parity, p.10-11, ch.1]` — naïve risk parity (inverse-variance
weighting) is the exact equal-risk-contribution solution for the
N-asset portfolio problem when the correlation matrix is diagonal.
Foundation of the iter 006/008 2-leg blend; generalises cleanly to
N=3 with the off-diagonal covariance terms added to σ²_port.

## Additional citations

- `[risk_parity, p.80-81, ch.4]` — SPY-TLT-GLD empirical correlations
  (ρ ≈ −0.2 to −0.3 SPY-TLT, ~0 SPY-GLD, ~0 TLT-GLD on 2004-2026
  windows). Three legs all with low pairwise ρ give
  diversification-return uplift at portfolio level.
- `[risk_parity, p.5, p.16, p.109-110]` — canonical risk-parity
  argument that multi-asset diversified portfolios produce higher
  risk-adjusted returns than concentrated equity exposure under
  variance-scaling.
- `[systematic_trading, p.40, ch.2]` — volatility standardisation.
- `[systematic_trading, p.144, ch.9]` — target_vol calibration
  (15% annualised mid-institutional equity).
- `[systematic_trading, p.170-171, ch.11]` — IDM cap ≤ 2.5 on total
  gross exposure. With 3 legs at lower individual vol the IDM cap is
  more likely to bind — we keep `max_leverage = 2.0` to stay below 2.5.
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag on rolling variance
  (no look-ahead).
- `[advances_fin_ml, p.208-211]` — G1 PBO via CSCV; N=1 vacuous PASS
  carried forward from iter 008.
- `[advances_fin_ml, p.222-223]` — G2 DSR with cumulative n_trials.
- `[advances_fin_ml, p.31-34]` — G7 cross-lib parity via numpy
  reference, extended here to 3 legs.
- `[leverage_for_the_long_run, p.9]` — SPY regime asymmetry
  (above-MA vs below-MA vol) is the same information variance-scaling
  exploits.
- `[ilmanen_expected_returns, ch.11]` — gold as portfolio
  diversifier; inflation-hedge risk-factor distinct from equity and
  bond duration factors.

**Web / external**:

- **Moreira & Muir (2017).** *JoF* 72(4), 1611-1644. DOI
  [10.1111/jofi.12513](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12513).
  Portfolio-level variance-scaling — form `s_t = c / σ²_{t-1}` is
  applied unchanged to the 3-leg σ²_port in iter 010.
- **Asness, Frazzini & Pedersen (2012).** *FAJ* 68(1). SSRN
  [1728082](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1728082).
  "Leverage Aversion and Risk Parity" — argues risk-parity across
  uncorrelated asset classes (equities + bonds + commodities) gives
  higher Sharpe than concentrated equity even after vol-targeting.
  Iter 010 operationalises this claim at N=3 with daily rebalance.
- **Qian (2005).** PanAgora Asset Management — original risk-parity
  formulation extending inverse-vol weighting to multi-asset classes
  (SPY + TLT + GLD is a canonical 3-leg test case).

## Edge source

What SPY 1x buy-hold fails to capture:

1. **GLD's flight-to-quality during stagflation / monetary stress**.
   2022 was the canonical counter-example — bonds AND equities fell
   simultaneously (−17% SPY, −31% TLT) while gold held +0.4%. A 2-leg
   blend (iter 008) had no inflation-hedge leg and suffered meaningful
   drawdown; a 3-leg blend with a ~20-30% gold weight reduces that
   drawdown structurally.
2. **Portfolio-level σ²_port smoothing** — with 3 low-correlation legs,
   each leg's individual variance shocks cancel more at the portfolio
   level. This means variance-scaling `target_vol² / σ²_port` stays
   closer to its maximum cap more of the time, reducing opportunity
   cost of de-levering.
3. **Real-asset factor** — gold responds to inflation expectations
   and USD weakness, which are orthogonal risk factors to equity
   earnings growth and bond duration. `[ilmanen_expected_returns, ch.11]`
   documents that gold's Sharpe over long windows is ~0.3-0.4 (low),
   but its *correlation* with equities and bonds hovers near zero —
   exactly the regime where risk-parity diversification return
   dominates.

**Structural difference from iter 006/008**: iter 006/008 had 2 legs
with ρ≈−0.30. Iter 010 adds a 3rd leg with ρ≈0 (to both others). The
correlation structure is qualitatively new (full 3×3 matrix with off-
diagonal ≈ 0), not a parameter variation of the 2-leg case. This is
the core reason iter 010 is in `## Promising unexplored directions`,
not `DEAD_ENDS.md`.

## Pre-committed configuration

**`vt15_L21_cap20_3leg`** (single cfg, no sweep):

| param | value | literature anchor |
|---|---|---|
| `target_vol` | 0.15 | `[systematic_trading, p.144]` mid-institutional equity; matches iter 006/008 for fair comparison |
| `lookback` | 21 | Moreira-Muir canonical 1-month vol window; matches iter 006/008 |
| `max_leverage` | 2.0 | ≤ 2.5 IDM cap `[systematic_trading, p.170-171]`; matches iter 006/008 |
| `cost_bps_per_leg` | 2 bps | matches iter 006/008 cost model (applied per-leg, so 3-leg turnover now incurs 3 × per-leg costs) |
| `legs` | SPY/QQQ + TLT + GLD | SPY for edu/spy, QQQ for ndx (equity-leg), TLT = bond leg (constant), GLD = commodity leg (constant) |

**Commitment timing**: the cfg above is declared BEFORE running any
3-leg backtest. It is the minimal literature-consistent extension of
iter 008's `vt15_L21_cap20` to 3 legs. No param tuning, no sweep, no
post-hoc selection.

**Discipline rationale**: the params are **identical** to iter 008's
2-leg cfg. Adding GLD as a third leg without also re-tuning params is
the honest ex-ante test — any Sharpe change is attributable to the
new leg, not to coincidental sweet-spot re-tuning.

## Datasets

Identical universe definitions to iter 008 but with GLD added as third
leg. **GLD availability constrains educational window from 2002-07-26
→ 2002-11-18 start**:

- **educational**: SPY+TLT+GLD, 2004-11-18 → 2026-04-15 (≈ 21y, GLD-
  constrained). Custom benchmark: SPY b&h on same window.
- **spy_real**: SPY+TLT+GLD, 2009-06-25 → 2026-04-15 (17y post-GFC).
  Benchmark: frozen `scoring.BENCHMARKS["spy_real"]` (SPY 0.90).
- **ndx_real**: QQQ+TLT+GLD, 2010-02-12 → 2026-04-15 (16y).
  Benchmark: frozen `scoring.BENCHMARKS["ndx_real"]` (QQQ 0.955).

Note: spy_real and ndx_real benchmarks are frozen at iter 008 values —
the only window that changes is educational, where the benchmark
must be re-measured on the shorter SPY window (`2004-11-18 → 2026-
04-15` vs iter 008's `2002-07-26 → 2026-04-15`).

## Kill criteria (pre-committed)

Hypothesis is **falsified** if ANY of the following fire:

1. **Kill #1 (no Sharpe uplift)**: combined 3-leg Sharpe ≤ iter 008's
   2-leg Sharpe on both spy_real AND ndx_real (within ± 0.02 tolerance).
   If adding GLD does NOT produce any Sharpe improvement on either
   real-data slot, the 3rd leg is pure drag — no diversification return.
2. **Kill #2 (CAGR catastrophic drop)**: 3-leg CAGR < 0.75 × benchmark
   on ≥ 2/3 datasets (stricter than the score's 0.8 floor). Indicates
   the 3-leg cost structure + permanent GLD allocation erodes returns
   substantially.
3. **Kill #3 (score regresses)**: total_score < 70 (iter 008 was 74).
   Any backward motion signals the mechanism is hurting more than
   helping.
4. **Kill #4 (gate regression)**: any dataset drops below 5/7 gates
   (iter 008 had 6/6/6). Stricter than cross-dataset minimum.
5. **Kill #5 (cross-lib divergence)**: G7 numpy-reference CAGR differs
   by > 3 pp from pandas engine — implementation mismatch.

If NONE fire AND score ≥ 75, the structural-extension hypothesis is
confirmed: 3-asset diversification compounds with vol-managed scaling.
If score ≥ 90 AND all 5 winner conditions met → WINNER.

## Expected budget

- **Configs to test**: 1 cfg × 3 datasets = 3 new trials. Cumulative
  n_trials: 4243 → **4246**.
- **Wall-time**: 3-5 min backtest (same cost as iter 008; adds
  cov-matrix computation but numerically trivial) + 3-5 min 7-gate
  battery.
- **Files to create**:
  - `three_leg_blend.py` — 3-leg inverse-variance + Moreira-Muir
    variance-scaling (pandas implementation)
  - `numpy_reference_3leg.py` — pure-numpy independent re-implementation
    for G7
  - `run_backtests.py` — dataset loader + single-cfg runner (reuses
    iter 008's dataset definitions with GLD added)
  - `compute_gates_and_score.py` — 7-gate battery (pattern from iter
    008, cross-lib call updated for 3 legs)
  - `test_three_leg_blend.py` — TDD unit tests (ERC sanity, 2-leg
    degenerate case matches iter 006, IDM cap respected)
  - `results.json`, `verdict.json`, `final_report.md`

**Baseline pytest** must stay green (currently 1 161 tests per the
prompt). New test file adds 5-8 specs.

## Implementation plan

1. **TDD first** — write `test_three_leg_blend.py` with:
   - `test_two_leg_degenerate_matches_iter_006` — passing σ²_gld = ∞
     (zero inverse-variance) should reproduce iter 006's 2-leg result
     to 1e-8 (soft-equivalence via `w_gld → 0`).
   - `test_erc_three_equal_vol_gives_uniform_weights` — three legs with
     identical σ² and zero cross-correlation should yield
     w_spy = w_tlt = w_gld = 1/3.
   - `test_inverse_variance_with_asymmetric_vols` — σ²_spy = 0.04,
     σ²_tlt = 0.01, σ²_gld = 0.02 should give weights in inverse
     proportion (verified analytically).
   - `test_scale_bounded_by_max_leverage` — sum of pos_spy + pos_tlt
     + pos_gld ≤ max_leverage at every bar.
   - `test_lookback_lag_no_lookahead` — first `lookback` bars dropped,
     `σ²_port[t]` uses returns from `[t-L, t-1]` only.
2. **Implement `three_leg_blend.py`** to satisfy tests; use matrix form
   `σ²_port = wᵀ Σ w` with full 3×3 covariance. Handle degenerate
   cases (zero variance per leg) consistently with iter 006.
3. **Implement `numpy_reference_3leg.py`** — independent pure-numpy loop
   over bars, using `np.cov(..., ddof=0)` for 3×3 blocks. Must agree
   with pandas version to 1e-8 per-bar scale.
4. **Data load**: extend iter 008's `load_paired_returns` to 3-column
   inner-join; verify GLD ticker index aligns.
5. **Run backtests** on 3 datasets (1 cfg × 3 datasets = 3 trials).
   Save `results.json`.
6. **7-gate battery**:
   - G1: N=1 vacuous PASS (carried from iter 008).
   - G2: DSR with cumulative_n_trials=4246.
   - G3-G6: identical to iter 008's gates (`compute_gates_and_score.py`
     pattern).
   - G7: call numpy reference with 3 legs; compare CAGR.
7. **Robustness bonus** (criterion 6): same 3 sub-window split per
   dataset; count Sharpe-positive windows across 9.
8. **Score**: call `score_strategy` with custom edu benchmark
   (2004-11-18 start) + frozen spy/ndx benchmarks. Add robustness
   bonus.
9. **Write final_report.md** with verdict, score breakdown, all 3
   datasets' headline metrics + Δ vs iter 008.
10. **Update BASE_MEMORY.md** (total_iterations=10, n_trials=4246, log
    entry, Top-K refresh, Option D consumed → DEAD_ENDS if FAIL /
    marked consumed if PROMISING).

**No modifications to `src/ai_trade/backtest/strategies/`** — this is a
study-level implementation reusing infra. If iter 010 becomes winner,
a follow-up PR promotes `three_leg_blend.py` to
`src/ai_trade/backtest/strategies/` after review.
