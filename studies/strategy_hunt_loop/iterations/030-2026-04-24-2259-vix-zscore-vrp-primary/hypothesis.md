# Iteration 030 — VIX z-score VRP-primary (R-2): only filter when VIX z-score over 60d > 2.0

## Hypothesis

Iter 028 (constant `VIX < 35`) and iter 029 (constant level + 3-day
persistence) both reach a score ceiling of 71/100 PROMISING because
the constant-parameter gate is **regime-conditional**: it correctly
identifies the GFC sustained-vol cluster (educational dataset) but
either misclassifies post-GFC transient spikes as benign (iter 026 →
spy/ndx Sharpe edge) or misclassifies them as malign (iter 028/029 →
spy/ndx Sharpe regression). Iter 029's structural finding is that the
3 hunt-loop datasets have qualitatively different high-VIX-event
regime structures (educational deeply-persistent GFC; spy_real mixed
transient/persistent post-GFC; ndx_real all-clustered post-GFC).

**A single constant absolute threshold cannot simultaneously optimize
all 3 datasets** because the threshold has no notion of *current
regime baseline*. A VIX of 36 in 2010 (post-GFC, when 60d-rolling-mean
is ~22) is a **2.5σ shock** (red flag). A VIX of 36 in late 2008 (when
60d-rolling-mean is ~50) is a **−1σ event** (regime is *softening*, not
spiking). Constant-level gates can't distinguish these.

This iteration replaces the constant gate with a **VIX z-score gate**:
filter the open only when the *standardized VIX deviation* exceeds
2.0σ relative to its 60-day trailing distribution. Mechanically:

```
vix_mu[i]   = mean(vix[i-59:i+1])
vix_sigma[i] = std(vix[i-59:i+1], ddof=1)
vix_z[i]    = (vix[i] - vix_mu[i]) / vix_sigma[i]

is_z_high(i) := vix_z[i] >= 2.0
```

If `is_z_high(i)` at a roll bar → skip the open (HOLD-CASH until next
eligible roll). Otherwise → open as iter 026.

This is **structurally orthogonal** to iter 028's level gate and iter
029's persistence gate:

- **Level (iter 028)**: `vix[i] >= 35` — fixed absolute threshold.
- **Persistence (iter 029)**: `vix[i-2:i+1] >= 35` — fixed absolute
  + temporal extent.
- **Z-score (iter 030)**: `(vix[i] - vix_60d_mean) / vix_60d_std >= 2`
  — **relative to current regime baseline**. No fixed absolute
  threshold. The same VIX value triggers different decisions in
  different macro regimes.

This should:

1. **Preserve iter 028's educational lift on the GFC ramp** — the
   *initial* 2008-Q4 VIX run-up (VIX from 25 → 80 over 6 weeks) is a
   high-z event; the rolling mean is still anchored at the 2008-Q3
   level (~25-30) when VIX hits 60+. Z-score correctly flags the
   onset.
2. **Recover spy_real's transient-spike behavior** — Mar-2020
   single-day spikes (VIX 80 from a baseline of ~16) have very high
   z (~5σ); these *should* still be filtered (they were genuine
   shocks). But the 2022 mini-spikes (VIX 30-35 from baseline 18-20)
   have z ~ 2-2.5; closer call. Possibly preserves more profitable
   rolls than iter 029 by being more discriminating on level alone.
3. **Avoid misclassifying late-2008 sustained-high as triggers** —
   by Q1 2009, the 60d-rolling-mean is ~55 and std ~15; even a VIX
   of 50 has z ~ −0.3 → does NOT trigger. This is the central honest
   risk: if the z-score gate fails to filter this period, educational
   may regress.

The mechanism prediction is therefore **subtle**: z-score may filter
the GFC *onset* (Sep-Oct 2008) but let the *sustained period*
(Nov-2008 → Mar-2009) through. If the harvest captures premium decay
in the sustained period (because realized vol < implied vol after the
panic settles), educational could match or beat iter 028. If realized
vol stays > implied vol (true tail in this period), educational
regresses to iter 026 baseline.

## Primary citation

`[volatility_trading, p.218]` — Sinclair (2013) "Volatility Trading"
ch. 8 §"VIX-VXV term structure": *sustained* high IV (not single-bar
spikes) is the warning sign for short-vol writers. Iter 028 closed
the constant-level interpretation; iter 029 partially refined to
constant-level + persistence; **iter 030 implements the
relative-shock interpretation**: a "high-IV warning" should be
defined relative to the prevailing regime baseline, not vs. an
absolute fixed level.

## Additional citations

- `[volatility_trading, p.39]` — Sinclair: VIX has annualized daily
  volatility of 0.96, weekly 0.84, monthly 0.59 (1990-2011 sample),
  illustrating regime-dependent dispersion. The high daily vol-of-vol
  motivates standardizing absolute moves by the rolling regime
  scale rather than using a static threshold.
- `[volatility_trading, p.58-59]` — Sinclair §"Volatility cone":
  realized-vol percentiles across horizons (20/40/60/120/240 days)
  used to place current IV in historical context. The 60d window
  for z-scoring directly mirrors Sinclair's middle horizon and is
  the canonical regime lookback in the cone framework.
- `[volatility_trading, p.214]` — Sinclair: variance premium is the
  *persistent* gap between IV and subsequent realized vol; rationale
  for the underlying iter 026 harvest (unchanged).
- `[volatility_trading, ch.3, p.41]` — VRP mechanics + SPX excess
  kurtosis 21.3 (capped-tail rationale; unchanged from iter
  026/028/029).
- `[volatility_trading, p.11]` — BSM pricing identity (unchanged).
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials`.
- Web: **Whaley, R. E. (2009). "Understanding the VIX."** *Journal of
  Portfolio Management* 35(3): 98-105.
  DOI: 10.3905/JPM.2009.35.3.098 — characterizes VIX dynamics as
  spike-and-revert in normal regimes vs. persistent in crisis
  regimes, using *standardized deviations* relative to recent
  history. Direct motivation for the 60d-rolling z-score lens.
- Web: **Bondarenko, O. (2014). "Why Are Put Options So Expensive?"**
  *Quarterly Journal of Finance* 4(3): 1450015.
  DOI: 10.1142/S2010139214500153 §3 — establishes that *both* level
  and persistence dimensions matter for spread-writer tail risk;
  iter 030's z-score conditions on level scaled by regime, providing
  a third orthogonal axis.
- Web: **Carr, P. & Wu, L. (2009). "Variance Risk Premiums."** *RFS*
  22(3): 1311-1341. DOI: 10.1093/rfs/hhn038 — VRP is decomposable
  into level, persistence, and *innovation* components; iter 030
  isolates the innovation (relative-shock) component.

## Edge source

Same as iter 026 + 028 + 029: SPY 1× buy-and-hold sells nothing; the
stand-alone VRP harvest captures the unconditional implied-vs-
realized gap. **Iter 030 captures the conditional-on-regime-shock
gap**: filtering only when realised-vol surprise warrants — i.e., the
current VIX move is unusual *relative to its own recent
distribution*. The signal remains uncorrelated with SPY direction;
the gate is fully orthogonal to iter 026's harvest mechanism (no
σ²_port to cointegrate with — see DEAD_ENDS line 1213-1217 for the
non-applicability of the σ²_port absorber to VRP-primary engines).

## Datasets

Identical to iter 028/029 (so the comparison is direct against iter
026, iter 028, and iter 029):

- **educational** (SPY+VIX 2006-01-03 → 2026-04-14, ~5100 bars):
  contains 2008-Q4 GFC. Z-score pre-computed using a buffered VIX
  series (extending back to 1990-01-02, the start of Tiingo VIX data,
  giving 16y warmup for the 60d rolling window).
- **spy_real** (SPY+VIX 2009-06-25 → 2026-04-14, ~4255 bars,
  post-GFC): z-score uses VIX history from 2009-04-01 (~3 months
  buffer) to ensure z is well-defined for the first aligned bar.
- **ndx_real** (QQQ+VIX×1.1 2010-02-12 → 2026-04-14, ~4095 bars):
  z-score on RAW VIX (not iv_scale × VIX) following iter 028/029
  convention — gate uses raw VIX for consistency across datasets.

## Kill criteria (pre-committed)

If any of the following triggers, the R-2 hypothesis is falsified
(regardless of how other metrics behave):

- **Kill A**: Sharpe regresses by **> 0.05** vs **iter 026** on
  **spy_real OR ndx_real**. The z-score gate is supposed to either
  recover or improve iter 026's post-GFC behavior; failing to do so
  means the relative-shock theory is no better than constant level.
- **Kill B**: Educational Sharpe falls below **iter 028 − 0.10
  (= 1.16)**. Looser than iter 029 Kill B because R-2 might
  legitimately let some sustained-period rolls through (low z), so
  educational could regress to iter 026 baseline (~1.13) without
  fully falsifying. We only fail if it falls below even that level.
- **Kill C**: 21-day worst loss exceeds **30%** on any dataset
  (catastrophic per-cycle risk; standing).
- **Kill D**: G7 cross-lib CAGR Δ **> 3 pp** on any dataset
  (engine dirty; standing G7 threshold).
- **Kill E**: Z-score gate triggers **0** rolls on **educational**.
  GFC contains genuine 2σ+ VIX shocks (Sep-Oct 2008 onset); zero
  triggers on educational means the gate is mis-implemented or the
  z window is wrong.
- **Kill F (NEW)**: Z-score gate triggers **0** rolls on **spy_real**
  AND **0** rolls on **ndx_real**. Mar-2020 had VIX go from 14 to 80
  in 3 weeks — that's a >5σ event. Zero triggers on both post-GFC
  datasets means the z window or threshold is mis-calibrated.

Each kill is checked in `compute_gates_and_score.py` and reported in
`verdict.json["kill_criteria"]`.

## Expected budget

- Configs to test: **1** (single pre-committed cfg
  `vrp_z_z2_h1_5_10_1m`). No grid, no sweep, no post-hoc selection.
- Cumulative `n_trials` advance: **4282 → 4283 (+1)**.
- Wall-time: ~3-5 minutes per dataset (mirrors iter 029).
- Files to create:
  1. `vrp_zscore.py` — pandas engine adding z-score VIX filter to
     `compute_vrp_zscore_returns`. Z-score series pre-computed once
     and passed in.
  2. `numpy_reference_zscore.py` — pure-numpy reference for G7.
  3. `run_backtests.py` — runner across 3 datasets.
  4. `compute_gates_and_score.py` — 7-gate battery + scoring + kill
     evaluation.
  5. `tests/test_iter030_vix_zscore.py` — TDD spec (5 tests:
     parity vs iter 026 at infinite-z threshold, parity vs unfiltered
     when sigma is huge, z-score correctness on synthetic VIX,
     pandas-numpy parity, kill detection).
  6. `results.json`, `verdict.json`, `final_report.md`,
     `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.

## Implementation plan

1. **TDD spec** (`tests/test_iter030_vix_zscore.py`) — write 5 tests
   FIRST:
   - `test_zscore_threshold_inf_matches_iter026` — when
     `z_threshold = 1e9`, R-2 must reproduce iter 026 exactly to
     1e-12. (Sanity: z-gate is irrelevant when threshold is
     unreachable.)
   - `test_zscore_correctness_on_synthetic_vix` — synthetic VIX
     scenario with deterministic mean/std, verify z = 2 exactly
     where expected, z < 2 elsewhere.
   - `test_zscore_window_60_skips_first_59` — first 59 bars have z
     undefined (insufficient history); the engine must NOT skip
     those bars (default to "open" when z is unavailable, mirroring
     iter 029's `is_persistent_high` behavior at i < k-1).
   - `test_pandas_numpy_parity_iter026_window` — pandas vs numpy
     engine on real iter 026 SPY+VIX window must differ by < 1e-12
     in maximum return.
   - `test_kill_F_synth_low_vol` — synthetic constant-VIX scenario
     produces zero gate triggers on all 3 datasets; the kill
     evaluation correctly flags Kill F.

2. **Implement `vrp_zscore.py`** — copy iter 029's `vrp_persistence.py`
   and replace the gate condition with a precomputed z-score lookup.
   Z-score is computed externally (in run_backtests.py from the
   buffered VIX) and passed as an additional argument
   `vix_zscore: pd.Series`. The engine just reads `z[i] >= threshold`
   at every roll-evaluation point. Bar 0 special-case: if z is NaN
   (insufficient history), do NOT skip (default to open).

3. **Implement `numpy_reference_zscore.py`** — pure-numpy mirror of
   step 2.

4. **Run on 3 datasets**: load buffered VIX (2 years before each
   dataset start, or from 1990-01-02 for educational). Compute z
   using rolling 60d mean+std. Reindex to price index. Pass to
   engine. Save full `results.json` with `returns_series` for
   the Stage 5 plot helper.

5. **G7 cross-lib check**: 0.0000 pp expected (deterministic engine).

6. **Compute 7-gate battery + scoring** identical to iter 029
   (`compute_gates_and_score.py`); cumulative `n_trials = 4283`.
   Add iter 026/028/029 reference dicts for cross-comparison
   reporting.

7. **Generate plots** via `plot_helper.py --iter 030`.

8. **Final report** with score breakdown, comparisons against
   **iter 026, iter 028, iter 029** (the relevant prior baselines).

## Why iter 030 is structurally novel vs all DEAD_ENDS entries

- **Not closed by iter 028** (`vix < 35` constant level): R-2 has no
  fixed absolute threshold; the same VIX value triggers different
  decisions in different regime baselines.
- **Not closed by iter 029** (level + 3-day persistence at constant
  threshold): R-2 has no temporal-window component; it's a
  single-bar (relative) trigger. iter 029 explicitly opens R-2 in
  its DEAD_ENDS entry (line 1991-1995).
- **Not closed by DEAD_ENDS line 1213-1217** ("VIX z-score (σ_eq
  proxy) on vol-managed 2-leg stack"): that entry is about overlays
  on σ²_port-bearing engines (iter 008/010/015/016). Iter 030 base
  is iter 026 VRP-primary (T-bill collateral; no σ²_port; no
  cointegration). The σ²_port absorber argument does not apply.
- **Not closed by DEAD_ENDS line 700-720** ("meta-labeling features
  on vol-managed blend"): iter 030 is not a meta-label classifier;
  it's a deterministic gate with one fixed parameter
  (z_threshold = 2.0).

## What success looks like (numerically)

Best-case scenario (R-2 hypothesis fully validated):

| dataset | iter 026 Sh | iter 028 Sh | iter 029 Sh | iter 030 target |
|---|---|---|---|---|
| educational | 1.13 | 1.26 | 1.27 | **1.20-1.27** |
| spy_real    | 1.28 | 1.18 | 1.23 | **1.27-1.30** (recover) |
| ndx_real    | 1.37 | 1.30 | 1.30 | **1.34-1.37** (recover) |

DSR p targets:
- educational < 0.05 (preserve iter 028/029 record).
- spy_real < 0.10 (the 0.0003-miss threshold).
- ndx_real < 0.05 (preserve iter 026 record).

If achieved:
- Sharpe edge 3/3 vs frozen bench → **25 pts**
- Gates probably 7/7 + 6/7 + 7/7 → **22 pts** (+ cross-bonus 4)
- DSR worst p < 0.05 → **15 pts**
- CAGR 0/3 (still N=1 ceiling) → **0 pts**
- MDD 3/3 → **15 pts**
- Robustness 9/9 → **5 pts**
- **Total ~82 STRONG (4/5 winner) OR if all 5 conditions hit → WINNER**

Realistic scenario (partial validation):
- educational holds 1.20-1.25 (z catches GFC onset; lets sustained
  through with mixed results); spy/ndx recover ~70% of iter 029's
  remaining gap → score 76-80 STRONG.

Failure scenario (Kill A or Kill B triggers): relative-shock theory
falsified or no better than iter 029. Opens R-3 (term structure) and
R-1+R-2 composite for iter 031.

## Risks pre-acknowledged

1. **First 59 bars per dataset have undefined z** (insufficient
   rolling-window history). Implementation default: do NOT skip
   when z is NaN. This means the GFC onset (Sep-Oct 2008) on
   educational has a partial warmup period — the 60d window is
   fully populated by mid-2006 at the latest. Not a real issue.
2. **The 60d window itself is a parameter choice** (literature
   supports 21d, 60d, 120d, 252d). Using 60d is anchored to
   `[volatility_trading, p.58-59]` (volatility cone middle horizon)
   and Sinclair's monthly-vol-of-VIX measure (p.39). Not data-mined.
3. **The z = 2.0 threshold is a parameter choice**. Anchored to
   "2σ shock = ~97.7th percentile of normal moves" — the canonical
   threshold in Whaley 2009 for VIX innovation analysis. Not
   data-mined.
4. **The 60d window may be too short for the GFC sustained period**:
   by Q1 2009, the 60d rolling mean is ~55, std ~15. A VIX of 50 has
   z ~ −0.3 → DOES NOT trigger. The harvest writes into this
   regime. If realized vol > implied (true tail), educational
   regresses. **This is the central empirical question of iter 030**.

The risk in (4) is genuine and pre-committed: if the experiment shows
educational regression to iter 026 levels (~1.13) on the sustained
GFC period, that *is* the data-driven answer that the relative-shock
component (R-2) is insufficient on its own — pointing to R-1+R-2
composite or R-3 term-structure as the next step.

## Conclusion

The pre-committed config tests one structurally novel parameter pair
(z_window=60, z_threshold=2.0) on the iter 026 base. The experiment
will resolve whether VIX z-score is the orthogonal regime axis that
unlocks the loop's first WINNER, or whether the dataset-asymmetry
finding from iter 029 dominates regardless of which constant-parameter
gate is used (pointing to composite or learned signals). Both
outcomes are honest, useful, and structurally distinct from prior
iterations.
