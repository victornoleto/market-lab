# Iteration 070 — Continuous T10Y3M z-score regime classifier on iter 064

## Hypothesis

iter 069 closed the **binary VIX-cond inner-weight swap on iter 064 in
both directions** at score **90 STRONG** (joint TOP-K #1 with iter 064).
The 90 ceiling has two candidate explanations:

1. **Granularity** — binary VIX-20 cut is too coarse; continuous regime
   gradient might expose conditional-Sharpe gaps invisible to a
   2-state classifier.
2. **Signal redundancy** — VIX is an *equity-vol* (reactive) regime
   indicator and both iter 064 sub-streams (r_046 has σ⁻² scaling;
   r_qqqt has 200d-SMA filter) are *already* vol-adaptive, so VIX is
   informationally degenerate with the streams' own regime adaptation.

This iteration tests both at once by replacing binary VIX-20 with the
**continuous z-score of the 10Y-3M Treasury term spread (T10Y3M)** —
a macro/forward-looking, equity-vol-orthogonal regime signal — used
as a continuous map onto the same `(w_qqqt, w_046)` inner-weight axis
established in iter 068/069. If the 90 ceiling stems from binary
granularity OR equity-vol-redundancy, this iteration breaks it; if it
stems from the iter 064 composition itself being locally Sharpe-maximal,
this iteration saturates at 90 and closes the regime-classifier axis
entirely.

The mechanism preserves iter 069's reverse-direction bias (more
QQQ_TREND when curve flat/inverted ↔ recession risk) since iter 069
empirically beat iter 068 by +0.029 to +0.041 Sharpe on 3/3 datasets,
validating that calm-light / stress-heavy is the right direction.

```
z[t]      = (T10Y3M[t-1] - rolling_mean_5y[t-1]) / rolling_std_5y[t-1]
            (no peek; both lookback windows up to t-1 only)
f(z[t])   = clip(0.5 - α · z[t], 0, 1)        # negative z → high f
w_qqqt[t] = w_min + (w_max - w_min) · f(z[t]) # continuous in [w_min, w_max]
w_046[t]  = 1.0 - w_qqqt[t]                    # total ≡ 1.0, NO leverage
cost[t]   = cost_bps · 1e-4 · |w_qqqt[t] - w_qqqt[t-1]|
r_070[t]  = w_046[t]·r_046[t] + w_qqqt[t]·r_qqqt[t] − cost[t]
```

Defaults (Sharpe-anchored to iter 069's 0.05/0.20 envelope):

* `w_min = 0.05`, `w_max = 0.20`           → same range as iter 069
* `α = 0.25`                                → ±2σ z maps to ±0.5 swing in f
* `lookback_z = 1260` (≈ 5 trading years)  → standard rolling regime window
* `cost_bps = 5.0` per |Δw_qqqt|

## Primary citation

`[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching
methodology (the framework justifying continuous regime classifiers
over binary thresholds).

## Additional citations

* `[regime_change, p.27, ch.3]` — log-transformed continuous regime
  indicator construction (Tsang/Chen 2018 methodology).
* `[stocks_on_the_move, p.21-30]` — Clenow (2015), single-asset 200d
  SMA filter as regime gate (preserved via QQQ_TREND).
* Faber (2007), SSRN 962461, *A Quantitative Approach to Tactical Asset
  Allocation*, J. Wealth Mgmt 9(4) — single-asset 200d SMA TAA primitive
  (preserved verbatim via iter 064's `qqq_trend.py`).
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity (iter
  046 base preserved via the saved `r_046` stream).
* `[volatility_trading, p.218]` — Sinclair (2013), σ⁻² scaling
  (preserved inside iter 046 via iter 016).
* **Estrella & Mishkin (1998)**, "Predicting U.S. Recessions: Financial
  Variables as Leading Indicators", *Review of Economics and Statistics*
  80(1): 45-61, DOI 10.1162/003465398557320 — academic anchor for the
  10Y-3M term spread as the most accurate single recession-leading
  indicator (1-12 months ahead).
* **Estrella & Trubin (2006)**, "The Yield Curve as a Leading Indicator:
  Some Practical Issues", *FRBNY Current Issues* 12(5) — practical
  implementation guidance for T10Y3M as a real-time recession signal.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on regime signal
  (no peeking).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
* `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1, vacuous at N=1).
* `[systematic_trading, ch.11]` — Carver IDM ≤ 2.5 (we sit at 1.0).
* **iter 069 final report** — empirical KILL I conditional-Sharpe
  ordering vindicated reverse direction (calm-light, stress-heavy).
* **iter 068 final report** — bit-identical engine pattern reused.

## Edge source

SPY 1x buy-hold has no regime adaptation. iter 064 has indirect regime
adaptation through the sub-streams' own vol-targeting / 200d-SMA
filters, but no explicit composition-level regime gate. This iteration
adds a **macro-orthogonal forward-looking regime gate** at the
composition layer using a signal (T10Y3M) that does not enter any
sub-stream. If recession-risk dynamics differentially favour the
trend-following sub-stream over the risk-parity sub-stream (or vice
versa) in ways the streams' own adaptation cannot capture, the
composition Sharpe lifts above static.

## Datasets

* **educational** (SPYSIM synth 40y, 2006-01-03 → 2026-04-15): the
  iter 064 engine uses 2006+ for educational due to QQQ data
  availability; T10Y3M extends back to 1982 so warmup covers 5y
  rolling window comfortably.
* **spy_real** (Tiingo SPY/UPRO 17y, 2009-06-25 → 2026-04-15): same
  window as iter 064/068/069 for direct comparison.
* **ndx_real** (Tiingo QQQ/TQQQ 16y, 2010-02-12 → 2026-04-15): same.

## Kill criteria (pre-committed)

This iteration fails (and 1+ kill fires) if any of these are observed
at end of Stage 4. Multiple kills can fire simultaneously.

| # | kill | rationale |
|---|---|---|
| **A** | **Sharpe lift vs iter 064 < +0.02 on ≥ 2 ds** | reverse-direction continuous regime fails to break the 90 ceiling — iter 064 confirmed locally Sharpe-maximal under any inner-weight gate |
| **B** | **DSR worst-p ≥ 0.05 with cumulative n_trials = 4340** | DSR fails (degrades from iter 069's 0.0429) |
| **C** | **Total score < 75** | drops below STRONG tier — direction broken |
| **D** | **edu CAGR < 9.18%** | loses iter 064's non-LETF CAGR-floor unlock on educational |
| **E** | **G7 cross-lib > 0.5 pp** | engine bug (continuous z-score implementation drift) |
| **F** | **corr(070, 064) > 0.995 on ≥ 2 ds** | continuous gate has no effect — degenerate to no-op |
| **G** | **max\|Σw - 1\| > 1e-9** | composition bug (continuous mapping not bounded properly) |
| **H** | **flips/yr < 1 OR > 100 on any ds** | regime pathology (z continuous → expect SMOOTHER than VIX 14-16/yr; lower bound 1 means continuous isn't "stuck") |
| **I** | **mean(w_qqqt) outside [0.08, 0.13]** | continuous mapping doesn't preserve iter 064's static `w=0.10` time-mean → drift confounds with mechanism |
| **J** | **corr(z_t10y3m, vix_lag) > 0.7 on ≥ 2 ds** | T10Y3M signal is not actually orthogonal to VIX (would mean continuous-vs-binary, not signal-orthogonality, is the only test) — diagnostic only |
| **K** | **iter 070 Sharpe < iter 069 Sharpe on ≥ 2 ds** | continuous regime fails to even match the binary baseline — the granularity hypothesis is empirically falsified |

KILL A is the headline pass/fail. KILLs B-G are engine integrity. KILL
H confirms regime activity. KILL I confirms exposure preservation
(allowing apples-to-apples comparison vs iter 064's static w=0.10).
KILL J is **diagnostic, not blocking** — used to interpret KILL A's
outcome (orthogonality of the regime signal). KILL K is the
granularity-vs-saturation diagnostic.

## Expected budget

* Configs to test: **1** (single pre-committed cfg
  `iter064_t10y3m_cont_alpha025_lb1260_w005_020`). cumulative_n_trials
  advance: 4339 → **4340** (+1).
* Wall-time: ~25-40 min (similar to iter 068/069 since most expensive
  computation is iter 046 stream load + QQQ_TREND warmup + 7-gate
  battery; the inner-weight engine is O(N) cheap).
* Files to create:
  * `t10y3m_cont_inner_weight.py` — pandas combiner with continuous
    z-score → w_qqqt mapping (mirrors iter 068's `vix_inner_weight.py`
    structure)
  * `numpy_reference_iter070.py` — pure-numpy parity reference for G7
  * `tests/test_t10y3m_cont_blend.py` — TDD spec (coverage:
    parameter validation, no-peek shift(1), Σw≡1 invariant, bit-
    identity vs iter 069 in degenerate case, monotonicity, bounded
    output)
  * `run_backtests.py` — compute on 3 datasets, save results.json
    (with `returns_series` key for plot helper)
  * `compute_gates_and_score.py` — 7-gate battery + scoring
  * `final_report.md`, `verdict.json` — Stage 5 deliverables

## Implementation plan

1. **TDD spec first** — write `tests/test_t10y3m_cont_blend.py` with
   ≥ 8 tests covering parameter validation, no-peek (shift(1) on T10Y3M
   AND on rolling mean/std), Σw≡1 invariant, bounded output [w_min,
   w_max], monotonicity (z↑ → w_qqqt↓ when α>0), correct mean
   (E[f(z)]≈0.5 when z is mean-zero), and bit-identity check vs
   iter 069 in the degenerate case where α→∞ approximates a binary
   gate at z=0. Tests fail until implementation exists.
2. **Implementation** — `t10y3m_cont_inner_weight.py` with
   `combine_with_t10y3m_cont_inner_weight()` function. Pandas-based,
   no NaN propagation (T10Y3M ffill internally, then bfill any
   warmup NaNs after computing rolling stats).
3. **Numpy reference** — `numpy_reference_iter070.py` with same
   semantics, pure numpy. G7 parity ≤ 0.5pp.
4. **Run** — `run_backtests.py` loads iter 046 saved stream + QQQ
   prices + T10Y3M data, computes the continuous inner-weight blend
   on edu/spy/ndx, saves `results.json` (including `returns_series`
   key for the Stage-5 plot helper).
5. **Gates + score** — `compute_gates_and_score.py` runs G1-G7 + DSR
   + score_strategy() with cumulative_n_trials=4340.
6. **Final report + verdict + plots** — Stage 5 deliverables; update
   BASE_MEMORY.md (bump iteration counter, append entry, update top-K
   if score is competitive).

Engine integrity invariants (asserted in tests AND at runtime):

* `Σ_t |w_046[t] + w_qqqt[t] − 1.0| < 1e-12`
* `w_qqqt[t] ∈ [w_min, w_max]` for all t
* `corr(070, 069)` ≥ 0.90 on all ds (continuous is a regime-richer
  variant of the same blend, not a different strategy entirely)
* `max(rolling_z_mean_lookback)` ≤ t (no future leakage)

This is a structurally novel iteration on the **regime classifier
axis** — different signal (macro/forward T10Y3M vs equity-vol/reactive
VIX), different granularity (continuous vs binary). It does NOT
duplicate iters 068/069 (binary VIX), 048/065 (binary VIX × output
scalar), 067 (σ⁻² overlay), 066 (RF meta-label), or any previously
closed axis.
