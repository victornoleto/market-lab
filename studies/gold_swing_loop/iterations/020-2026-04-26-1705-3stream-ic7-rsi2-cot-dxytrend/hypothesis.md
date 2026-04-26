# Iteration 020 — 3-stream IC-7 Markowitz tangency: iter 003 RSI MR + iter 018 COT z-score + iter 015 DXY trend gate

## Hypothesis

Compose three structurally orthogonal gold streams already absorbed by
the loop — iter 003 RSI(2)+SMA(200) mean-reversion (MR family),
iter 018 156-week z-score COT positioning (futures-positioning family),
and iter 015 DXY-MA-slope falling 200/20 trend gate (macro-FX family) —
at full-sample 3-asset Markowitz tangency weights `w ∝ Σ⁻¹μ` on
`gld_long` (PRIMARY) + `xauusd_real` (CORROBORATING). The combined
Sharpe ceiling under the closed-form tangency formula is
`√(S₀₀₃² + S₀₁₈² + S₀₁₅²)`, which on gld_long is
`√(0.30² + 0.35² + 0.24²) ≈ 0.52`. That ceiling is the **single most
informative test for the loop's DSR-deflator wall**: passing DSR < 0.05
at `n_trials = 20` would prove the wall is breakable within the
existing iter 001-019 stream catalog; failing definitively closes
2-and-3-stream IC-7 within the catalog and forces qualitatively new
mechanism families (DCOT money-manager, GVZ, GDX, futures-track A2)
or loop closure.

The 2-stream version (iter 019) hit 99.7% of its 2-stream tangency
ceiling (combined Sh +0.4584 vs analytical √(0.30² + 0.35²) = 0.460)
but failed DSR at p=0.4055. Adding a third stream at average pairwise
ρ ≈ 0.09 expands the analytical ceiling by `√(1 + S₀₁₅²/(S₀₀₃² + S₀₁₈²))
≈ √(1 + 0.0576/0.215) ≈ 1.13×`, giving combined ≤ 0.52, and the
expected DSR uplift from the additional uncorrelated component
proportional to `(1 − ρ²)^0.5` for the new pair joining; at ρ=0.09 that
factor ≈ 0.996 (essentially full).

## Primary citation

`[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials` plus
the multi-asset Markowitz tangency formula `w ∝ Σ⁻¹μ` and combined
Sharpe upper bound `S_combined ≤ √(Σ Sᵢ²)` for orthogonal streams.

## Additional citations

- `[advances_fin_ml, p.31-34]` — cost realism: composition adds zero
  turnover; reuses pre-deducted Pepperstone CFD costs from each stream.
- `[risk_parity, ch.2]` — multi-asset tangency / efficient-frontier
  generalization to N=3.
- `[short_term_trading_strategies, p.106]` — RSI(2) + SMA(200) MR
  base (iter 003 component).
- `[trading_systems_methods, p.639-640]` — COT z-score positioning
  variant (iter 018 component).
- `[trading_systems_methods, p.13-14]` — vol-regime + macro overlay
  conceptual grounding (iter 015 component family).
- de Roon, Nijman, Veld (2000) *Journal of Finance* — "Hedging Pressure
  Effects in Futures Markets" (z-score commercial net positioning).
- IC-7 sister-loop empirical (`studies/strategy_hunt_loop/` 045/046).
- IC-3 sister-loop closure (049) — Markowitz proper, NOT 50/50/50.
- IC-6 sister-loop closure (014/019) — rolling-ρ pre-val mandatory.
- IC-8 sister-loop closure (046) — single cfg per iter (we honor:
  ONE 3-asset full-sample tangency, no grid).

## Edge source

`gld_long` buy-hold captures gold's secular positive drift but not the
selectivity within drawdowns (RSI MR), the tactical re-loading at COT
positioning extremes (z-score), nor the dollar-weakness regime gating
(DXY-MA slope falling). The 3-stream weighted blend captures all three
edges simultaneously while diversifying their idiosyncratic noise via
near-zero pairwise ρ — yielding a portfolio whose combined Sharpe
approximates `√(S₀₀₃² + S₀₁₈² + S₀₁₅²)` and whose MDD compresses by
the diversification factor (~3×–4× from 2-stream in iter 019).

## Datasets

- `gld_long` (GLD daily 21.4 y) — **PRIMARY**. Longest sample; all 3
  components run on it directly; static tangency weights solve cleanly.
- `xauusd_real` (XAUUSD daily 6.3 y) — **CORROBORATING**. Iter 018
  doesn't run on intraday so 3-stream composition is daily-only;
  xauusd_real is the only intersect across all three Schema-A/B sources
  besides gld_long.
- ~~`xauusd_intraday`~~ — UNAVAILABLE. iter 018's COT z-score is
  daily-only by construction (CFTC weekly survey resampled forward),
  no 1h returns_series exists. Inheriting iter 019's 2-dataset
  configuration.
- ~~`gold_synth_40y`~~ — DEFERRED (not built). 3-stream IC-7 closure
  test does not require it.

## Timeframes used

`["1d"]`. All component streams resolve to daily net returns;
no fine-TF lookups.

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A only). Each component
stream's net returns are already pre-deducted of Pepperstone CFD
spread + swap (8 bps RT + −1 bps/night long swap), so the composition
inherits Track A costs identically. Track B (Inter ETF) NOT modeled
this iter; the 3-stream behavior identifies whether the IC-7
deflator-wall can be broken at all before re-pricing under DARF/long-
only/T+1.

Expected DARF drag on Track B: ~15% of positive months. Not relevant
for this iter's pass/fail since Track B blocks RSI MR's short
re-entries (long-only) and would also dilute via DARF ~15% — both make
Track B strictly inferior to Track A on this composition.

## Hold-time profile (HARD GATE)

- Expected weighted-avg mean hold (gld_long primary):
  - iter 003 base hold ≈ 4 d (RSI MR rapid re-entries)
  - iter 018 base hold ≈ 28 d (COT z-score slow swings)
  - iter 015 base hold ≈ 113 d (DXY trend persistent regime)
  - Predicted weights: ~0.5 / ~0.3 / ~0.2 (Markowitz proportional-
    Sharpe, since S₀₀₃ ≈ S₀₁₈ ≈ S₀₁₅×1.5)
  - Predicted weighted-avg = 0.5·4 + 0.3·28 + 0.2·113 ≈ 33 d
- **Declared `hold_time_track`: `medium_swing`** (10 ≤ mean ≤ 30).
- **Risk**: predicted weighted-avg ~33d may exceed 30d ceiling →
  bucket mismatch → score downgraded to NEAR_FAIL by the rules.
  Mitigation: post-run estimate exposure-weighted hold; if hold drifts
  above 30d but combined Sh edge > +0.10, hypothesis is still
  scientifically interesting (reports the closure of medium_swing
  bucket and points to swing-extended tracks). The hard gate fires
  formally; the lesson value remains.

## Kill criteria (pre-committed)

Reuse iter 019's framework, extended for 3 streams:

1. **Value-destruction**: combined Sharpe (PRIMARY) <
   `max(S₀₀₃, S₀₁₈, S₀₁₅) − 0.05`. Means tangency is destroying
   information rather than diversifying.
2. **Weight collapse**: any weight `wᵢ < −0.05` (large negative
   short on a stream that should be additive). For a 3-asset solver,
   this signals the covariance structure isn't well-conditioned at the
   tangency point.
3. **DSR no-progress**: PRIMARY DSR p > 0.20 with `n_trials = 20`. The
   iter 019 ceiling was p = 0.41; iter 020 needs p < 0.20 to register
   meaningful DSR uplift. p > 0.20 closes 3-stream IC-7 on this catalog.
4. **Pre-val rolling-ρ violation**: any pairwise rolling 60d
   `|ρ| > 0.30` exceeds 20% of joined bars across (003,018), (003,015),
   (018,015). Replicates IC-6 to 3-asset.

If any kill fires → record as the iter's verdict; do not retry with
different weights; flag the structural finding in DEAD_ENDS.md.

## Pre-validation screen (mandatory for overlays per IC-6)

Yes. Run rolling-60d ρ on each of three pairs:
- (iter003, iter018)
- (iter003, iter015)
- (iter018, iter015)

For each pair compute `exceed_frac = #{|ρ_60d| > 0.30} / N_bars`.
ABORT iter (mark `auto_aborted_at_pre_val: true`) if any pair has
`exceed_frac > 0.20` on the PRIMARY dataset. Iter 019 measured
003-018 at 1.5% on gld_long (PASS); 015 vs 003 was +0.17 static so
60d rolling will sit around there but should be well within 20%.

## Cost model (per track)

**Track A (Pepperstone)**: 8 bps spread RT + −1 bps/night swap on long
positions. Each component stream's published `net_returns` is already
inclusive of these costs (per iters 003, 018, 015 hypothesis files);
composition is a linear weighted sum that adds **zero turnover**, hence
zero additional cost. This is the same accounting iter 019 used and
which `[advances_fin_ml, p.31-34]` justifies.

Note: pure-rebalance turnover on the weighted blend is exactly zero
when weights are full-sample static (no in-sample/out-sample weight
re-optimization). If weights were re-fit per window, that would add
cost; but full-sample tangency is one-shot and adds none.

**Track B (Inter)**: NOT modeled. Even if applied, the composition
includes RSI MR short side (iter 003 trades both directions on its
SMA(200) regime gate), which Track B forbids. Track B would require
re-running iter 003's long-only-restricted variant, which is out of
scope.

## Expected budget

- Configs to test: **1** (single full-sample 3-asset tangency, IC-8
  honored).
- Wall-time: ~5 minutes (3-stream composition is essentially
  vectorized arithmetic on cached returns; bootstrap + DSR are O(N)).
- Files created:
  - `iterations/020-*/hypothesis.md` (this file)
  - `iterations/020-*/run_backtest.py` (3-stream composition)
  - `iterations/020-*/test_composition.py` (TDD 3-asset solver +
    rolling pre-val + tangency identity tests)
  - `iterations/020-*/results.json`
  - `iterations/020-*/verdict.json`
  - `iterations/020-*/final_report.md`

## Implementation plan

1. **TDD test_composition.py** (extends iter 019's tests):
   - 3-asset tangency weights solver: synthetic μ=[0.001, 0.001, 0.001]
     and Σ=I → equal weights 1/3 each.
   - 3-asset tangency on Σ with cross-correlations: solve `Σ⁻¹μ` and
     verify `Σ·w ∝ μ` numerically (`np.allclose` to 1e-10).
   - Negative-weight clamp: if one component yields negative tangency
     weight, clamp to a 2-asset corner solution.
   - Rolling-60d ρ on 3 pairs; verify each is bounded in [-1, 1].
2. **Adapt iter 019's `run_backtest.py` to 3 streams**:
   - Loaders: Schema-A for iter 003 + iter 015, Schema-B for iter 018.
   - 3-asset tangency: `np.linalg.solve(Σ, μ)` then normalize sum=1.
   - Pre-val: rolling 60d ρ on three pairs; abort if any exceeds 20%
     limit on PRIMARY dataset (gld_long).
   - 7 gates per dataset (PBO N/A by IC-8 single cfg).
   - Hold-time: weighted-avg of 3 component holds; observed bucket
     evaluated against `medium_swing` [10, 30].
   - score_strategy_v2 with `cumulative_n_trials=20`.
   - Kill criteria evaluator extended to 3-asset weight check.
3. **Write results.json + verdict.json**.
4. **Run pytest baseline** to confirm no regression, then run
   composition.
5. **Write final_report.md** capturing whichever outcome (3 cases:
   WINNER, NEAR_FAIL with kill, FAIL with abort).
