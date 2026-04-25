# Iteration 029 — VIX-persistence VRP-primary (R-1): only filter when VIX ≥ 35 for ≥ 3 consecutive days

## Hypothesis

Iter 028 established that the constant `VIX < 35` open-gate from
Sinclair `[volatility_trading, p.217]` is **regime-conditional**, not
universal. The filter delivered the first-ever 7/7 gates + sub-0.05
DSR p-value on `educational` (the GFC-inclusive sample) but
*regressed* `spy_real` (Sharpe −0.10) and `ndx_real` (Sharpe −0.07)
versus iter 026's stand-alone harvest. The asymmetry traces to the
**persistence** of the high-IV regime, not the level itself:

* **GFC era (2008-Q4)**: VIX 50-80 sustained for *weeks* → unfiltered
  spreads written into this regime systematically breach their cap →
  filter saves educational.
* **Post-GFC transient spikes (Mar-2020, 2022)**: VIX > 35 for *days*,
  not weeks → IV mean-reverts within the 21-DTE window → unfiltered
  spreads earn premium decay; iter 028's "skip" forfeits earned
  harvest → filter hurts spy/ndx.

This iteration replaces the constant gate with a **persistence
gate**: only skip the open when **VIX ≥ 35 for ≥ 3 consecutive
trading days at the natural roll bar**. Mechanically:

```
is_persistent_high_vix(i) = vix[i] >= 35 AND vix[i-1] >= 35 AND vix[i-2] >= 35
```

If `is_persistent_high_vix(i)` at a roll bar → skip the open
(HOLD-CASH until next eligible roll). Otherwise → open as iter 026.

This should:

1. **Preserve iter 028's educational lift** — the GFC has many 3+
   consecutive-day VIX ≥ 35 stretches (Sep 2008 → Mar 2009).
2. **Recover iter 026's spy/ndx behavior** — the Mar-2020 spike
   crossed 35 only on ~3-5 days total (cluster); even then the spread
   premium-decay was profitable (iter 026 evidence). The 2022
   "high-VIX" was never sustained at ≥ 35.

If the persistence theory is correct, iter 029 **should be the first
iteration of the loop where the strict 5-condition winner test is
plausible to clear** — DSR worst-p has been the sole gap since iter
026 (4/5 conditions met).

## Primary citation

`[volatility_trading, p.217]` — Sinclair (2013) "Volatility Trading"
ch. 8 §"Hedging short volatility positions": VIX < 35 entry filter
for short index-vol. Iter 028 established the rule is regime-
conditional; iter 029 refines the gate from level-only to
**level-AND-persistence** based on the empirical asymmetry the
2026-04-24 iter-028 boundary-finding result revealed.

## Additional citations

- `[volatility_trading, ch.3, p.41]` — VRP mechanics and SPX excess
  kurtosis 21.3 (capped-tail rationale; both unchanged from iter
  026/028).
- `[volatility_trading, p.218]` — Sinclair §"VIX-VXV term structure"
  notes that *sustained* high IV is the warning sign for short-vol
  writers, not single-day spikes (the persistence motivation comes
  from this paragraph plus Bondarenko 2014 §3).
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials`.
- Web: **Bondarenko, O. (2014). "Why Are Put Options So Expensive?"**
  *Quarterly Journal of Finance* 4(3): 1450015.
  DOI: 10.1142/S2010139214500153 — §3 documents that *persistent*
  high-IV regimes carry asymmetric tail risk for spread writers,
  while *transient* spikes rarely breach realised vol > implied gap
  in the next 21-day window.
- Web: **Carr, P. & Wu, L. (2009). "Variance Risk Premiums."**
  *Review of Financial Studies* 22(3): 1311-1341.
  DOI: 10.1093/rfs/hhn038 — establishes that VRP is decomposable
  into level and persistence components; iter 029 isolates the
  persistence component as the actionable signal.
- Web: **Whaley, R. E. (2009). "Understanding the VIX."**
  *Journal of Portfolio Management* 35(3): 98-105.
  DOI: 10.3905/JPM.2009.35.3.098 — characterizes VIX dynamics as
  spike-and-revert in normal regimes vs. persistent in crisis
  regimes, motivating the persistence threshold.

## Edge source

Same as iter 026 + 028: SPY 1× buy-and-hold sells nothing; the
stand-alone VRP harvest captures the unconditional implied-vs-
realised gap. Iter 028 added a constant-VIX gate that only paid off
in GFC-style regimes. **Iter 029 captures the conditional-on-
persistence gap**: filtering only when realised regime structure
warrants (3+ consecutive days), not when a single-bar IV spike fires.
The signal remains uncorrelated with SPY direction.

## Datasets

Identical to iter 028 (so the comparison is direct against both iter
026 and iter 028):

- **educational** (SPY+VIX 2006-01-03 → 2026-04-14, ~5100 bars):
  contains 2008-Q4 GFC where VIX is sustained ≥ 35 for many 3+ day
  windows. **Expected: filter triggers ≈ 80-90% of iter 028's skipped
  rolls** (mostly the GFC cluster).
- **spy_real** (SPY+VIX 2009-06-25 → 2026-04-14, ~4255 bars,
  post-GFC): Mar-2020 had VIX > 35 for ~10 trading days
  consecutively (Mar 12 → Mar 26 cluster). **Expected: persistence
  gate triggers on Mar-2020 cluster (1-3 rolls) but skips most of
  iter 028's other 4-5 transient triggers**. The Mar-2020 trigger may
  preserve iter 028's MDD improvement *or* may forgo iter 026's
  premium-decay rolls — the result settles which dominates.
- **ndx_real** (QQQ+VIX×1.1 2010-02-12 → 2026-04-14, ~4095 bars):
  same Mar-2020 cluster; VIX×1.1 unchanged for the gate (gate uses
  raw VIX per iter 028 convention).

## Kill criteria (pre-committed)

If any of the following triggers, the R-1 hypothesis is falsified
(regardless of how other metrics behave):

- **Kill A**: Sharpe regresses by **> 0.05** vs **iter 026** on
  **spy_real OR ndx_real**. The persistence gate is supposed to
  *recover* iter 026's post-GFC behavior; failing to do so means
  the persistence theory is wrong (transient vs sustained
  asymmetry is not the dominant axis).
- **Kill B**: Educational Sharpe falls below **iter 028 − 0.05 (=
  1.21)**. The persistence gate must keep the GFC lift; if iter 029
  educational regresses to iter 026 levels (~1.13), it means the
  3-day persistence threshold mis-classifies the GFC stretch as
  "transient" — the gate is too strict.
- **Kill C**: 21-day worst loss exceeds **30%** on any dataset
  (same as iter 028 Kill C — catastrophic per-cycle risk).
- **Kill D**: G7 cross-lib CAGR Δ **> 3 pp** on any dataset
  (engine dirty; standing G7 threshold).
- **Kill E**: Persistence gate triggers **0** rolls on **educational**.
  Educational MUST have multiple 3-day-persistent VIX ≥ 35 windows
  (Sep 2008 → Mar 2009 alone has dozens). Zero triggers means the
  gate is mis-implemented.

Each kill is checked in `compute_gates_and_score.py` and reported in
`verdict.json["kill_criteria"]`.

**Important asymmetry vs iter 028**: I expect the gate to trigger
**less** on spy/ndx than iter 028 (transient Mar-2020 single-day
spikes won't qualify; only sustained clusters will). This is *desired*
behavior — the goal is "filter only when sustained, allow transient
through". So unlike iter 028, **a low spy/ndx skip rate is NOT a
kill condition** — it means the gate is doing its job.

## Expected budget

- Configs to test: **1** (single pre-committed cfg
  `vrp_persistence_v35d3_h1_5_10_1m`). No grid, no sweep, no
  post-hoc selection.
- Cumulative `n_trials` advance: **4281 → 4282 (+1)**.
- Wall-time: ~3-5 minutes per dataset (mirrors iter 028).
- Files to create:
  1. `vrp_persistence.py` — pandas engine adding persistence-VIX
     filter to `compute_vrp_persistence_returns`.
  2. `numpy_reference_persistence.py` — pure-numpy reference for G7.
  3. `run_backtests.py` — runner across 3 datasets (mirrors iter 028).
  4. `compute_gates_and_score.py` — 7-gate battery + scoring + kill
     evaluation (mirrors iter 028 with iter 029-specific kills).
  5. `tests/test_iter029_vix_persistence.py` — TDD spec (5 tests:
     parity vs iter 026 at high threshold, parity vs iter 028 at
     persistence_days=1, persistence-skip on synthetic VIX cluster,
     pandas-numpy parity, no-skip when only 2 consecutive days).
  6. `results.json`, `verdict.json`, `final_report.md`,
     `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.

## Implementation plan

1. **TDD spec** (`tests/test_iter029_vix_persistence.py`) — write 5
   tests FIRST:
   - `test_persistence_off_at_high_threshold_matches_iter026` — when
     `vix_threshold = 1e9`, R-1 must reproduce iter 026 exactly to
     1e-12. (Sanity: persistence is irrelevant when level never
     hits.)
   - `test_persistence_days_1_matches_iter028` — when
     `persistence_days = 1` (single-bar trigger), R-1 must reproduce
     iter 028 exactly to 1e-12.
   - `test_synthetic_persistence_cluster_skips_open` — synthetic VIX
     scenario where vix=[40, 40, 40, 18, ...] forces persistence on
     bar 2 (3 consecutive days ≥ 35); the next roll falling in this
     window should be skipped. A scenario with vix=[40, 18, 40, 18,
     ...] (alternating) should NOT trigger persistence and the open
     should occur.
   - `test_pandas_numpy_parity_iter026_window` — pandas vs numpy
     engine on real iter 026 SPY+VIX window must differ by < 1e-12
     in maximum return.
   - `test_no_skip_when_only_two_consecutive_days` — synthetic VIX
     scenario vix=[40, 40, 18, 40, ...] — the 2-day cluster must
     NOT trigger persistence at bar 1 (need 3 consecutive). Confirms
     the persistence_days=3 threshold semantics.

2. **Implement `vrp_persistence.py`** — copy iter 028's
   `vrp_filtered.py` and replace the gate condition
   `iv_raw_arr[i] < vix_threshold` with
   `not is_persistent_high(iv_raw_arr, i, vix_threshold,
   persistence_days)` everywhere (3 sites: bar 0, roll bar inside
   OPEN branch, roll bar inside HOLD-CASH branch). The helper:

   ```python
   def is_persistent_high(vix, i, threshold, k):
       """True iff vix[i-k+1..i] are all >= threshold. False if i < k-1."""
       if i < k - 1:
           return False
       for j in range(i - k + 1, i + 1):
           if vix[j] < threshold:
               return False
       return True
   ```

3. **Implement `numpy_reference_persistence.py`** — pure-numpy
   mirror of step 2.

4. **Run on 3 datasets**, save full `results.json` with
   `returns_series` for the Stage 5 plot helper.

5. **G7 cross-lib check**: 0.0000 pp expected (deterministic engine).

6. **Compute 7-gate battery + scoring** identical to iter 028
   (`compute_gates_and_score.py`); cumulative `n_trials = 4282`.
   Add iter 028 reference dict for cross-comparison reporting.

7. **Generate plots** via `plot_helper.py --iter 029`.

8. **Final report** with score breakdown, comparisons against
   **both** iter 026 (the unfiltered baseline) and iter 028 (the
   constant-threshold variant). The structural finding is whether
   persistence-AND-level beats level-only (the central R-1 claim).

## Why iter 029 is structurally novel vs all DEAD_ENDS entries

The iter 028 dead-end entry says: **"constant VIX<35 entry filter
on iter 026 base is regime-conditional ... closes constant-threshold
V-3, opens regime-aware gates (R-1 persistence/R-2 z-score/R-3 term-
structure)"**. Iter 029 implements R-1 — explicitly opened by iter
028's closure.

Differences from iter 028's closed mechanism:

- **Persistence semantics, not level**: the gate now requires a
  *sequence* of high-VIX bars, not a single bar. This is a
  qualitatively different signal (state-dependent, not point-in-time).
- **One additional binary parameter** (`persistence_days = 3`). The
  value 3 is **not data-mined** — it is the smallest integer
  consistent with Sinclair p.218's prose ("sustained") and Bondarenko
  2014 §3's empirical persistence definition (≥ 3 days for high-IV
  classification). No grid; pre-committed.
- **Preserves iter 028's educational gate count, recovers iter
  026's spy/ndx behavior** — the predicted asymmetric outcome
  is structurally distinct from any closed iter (no closed iter
  achieves both simultaneously).
- **NOT covered by iter 019 dead-end** (HMM ρ stock-bond regime —
  σ²_port absorber): R-1 has no σ²_port (T-bill collateral only,
  same as iter 026/028), and the signal is on absolute VIX
  persistence, not on a derived correlation.

## What success looks like (numerically)

Best-case scenario (R-1 hypothesis fully validated):

| dataset | iter 026 Sh | iter 028 Sh | iter 029 target Sh | DSR p target |
|---|---|---|---|---|
| educational | 1.13 | 1.26 | **1.20-1.26** (preserve 028) | **< 0.05** (preserve 028) |
| spy_real | 1.28 | 1.18 | **1.25-1.28** (recover 026) | **< 0.10** |
| ndx_real | 1.37 | 1.30 | **1.35-1.37** (recover 026) | **< 0.05** (preserve 026) |

If achieved:
- Sharpe edge 3/3 vs frozen bench → **25 pts**
- Gates probably 7/7 + 6/7 + 7/7 → **~22 pts**
- DSR worst p < 0.05 → **15 pts**
- CAGR 0/3 (still N=1 ceiling) → **0 pts**
- MDD 3/3 → **15 pts**
- Robustness 9/9 → **5 pts**
- **Total ~82 STRONG (4/5 winner) OR if all 5 conditions hit → WINNER**

Realistic scenario (partial recovery):
- Sharpe spy/ndx recover ~50% of iter 028's regression → score
  76-78 (ties iter 026 at 76 or barely beats).

Failure scenario (Kill A or Kill B triggers): persistence theory
falsified — opens regime-aware paths R-2 (z-score) and R-3 (term
structure) for iter 030.
