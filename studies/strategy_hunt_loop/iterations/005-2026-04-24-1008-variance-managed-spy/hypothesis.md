# Iteration 005 — Moreira-Muir canonical variance-scaling on SPY

## Hypothesis

Replace iter 004's **vol-scaling** (`s_t = target_vol / σ̂_{t-1}`, Carver
form) with **variance-scaling** (`s_t = c / σ̂²_{t-1}`, Moreira-Muir
2017 canonical) applied to SPY and QQQ daily returns. The scale
constant is fixed at `c = target_vol²` so the average scale is ≈ 1 at
the target vol — same benchmark-comparability property as iter 004
with a different functional form.

Variance-scaling de-leverages harder during high-vol regimes (`σ̂ 2× bench → s=1/4` vs vol-scaling `s=1/2`) and levers up harder during
low-vol regimes. Moreira & Muir (2017) argue this is the
**mathematically-sharper specification** because realised variance is
more persistent than realised volatility — so a scale derived from
lagged variance tracks the "risk state" more tightly and gives a
stronger ex-ante Sharpe uplift.

## Primary citation

Moreira, A., & Muir, T. (2017). **"Volatility-Managed Portfolios."**
*Journal of Finance* 72(4), 1611-1644. DOI
[10.1111/jofi.12513](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12513).
The paper reports Sharpe gains of +0.20 to +0.40 on CRSP US equity
factor returns 1926-2015 when scaling by inverse-variance (not inverse-
vol). This is the canonical academic formulation of the mechanism
partially tested in iter 004.

## Additional citations

- `[systematic_trading, p.107-111]` — vol standardisation primitive:
  scale by target_vol / realised_vol. Iter 004 was this. Iter 005's
  variance-scaling uses the squared-denominator generalisation.
- `[systematic_trading, p.144-146 ch.9]` — target-vol as Half-Kelly
  proxy (applies equally to vol- and variance-scaling once `c` is
  calibrated).
- `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` (lagged, not contemporaneous)
  to guarantee no look-ahead in position sizing.
- `[advances_fin_ml, p.298-299]` — 1/N prior + double-margin promotion
  justifies the strict +0.10 Sharpe bar over baseline.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1 gate).
- `[advances_fin_ml, p.222-223, p.275]` — DSR with cumulative n_trials
  (G2 gate) — will NOT clear with this small uplift and cumulative
  trials ≈ 4192; documented upfront as a structural DSR cap on this
  mechanism family.
- `[advances_fin_ml, p.196-202]` — stationary bootstrap 99.9% CI (G6).
- `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
- Web / academic: Cederburg, O'Doherty, Wang, Yan (2020),
  [**"On the Performance of Volatility-Managed Portfolios"**](https://doi.org/10.1016/j.jfineco.2019.09.002),
  *Journal of Financial Economics* 138(1), 95-117 — critical replication
  that argues the Moreira-Muir effect is weaker than paper claims in OOS
  and on non-factor portfolios. Honest counter-evidence bar.

## Edge source

SPY buy-hold has a constant-unit-exposure risk profile: it pays the
same dollar-notional risk whether realised vol is 10% or 30%. Variance-
scaling compresses position aggressively when variance is high (which
empirically predicts low forward returns per Moreira-Muir Table III) and
expands it when variance is low (which predicts high forward returns).
The `1 / σ̂²` form is 4× more responsive than `1 / σ̂` to vol shocks —
should give larger drawdown-reduction on the same signal and therefore
better Sharpe.

## Datasets

All three datasets are re-used from iter 004 with identical windows
(frozen benchmarks):

- **educational** (SPYSIM synth 1986-01-02 → 2026-04-20, 40y) — longest
  OOS window, includes dot-com crash + GFC + COVID. Bench Sharpe 0.68 /
  CAGR 11.47% / MDD 55.14%. Tests whether variance-scaling's extra
  responsiveness helps in the big-MDD regimes.
- **spy_real** (SPY adj_close 2009-06-25 → 2026-04-20, 17y) — cached
  Tiingo parquet. Bench Sharpe 0.90. Same window as iter 004's primary
  strict-winner target.
- **ndx_real** (QQQ adj_close 2010-02-12 → 2026-04-20, 16y) — cached
  Tiingo parquet. Bench Sharpe 0.955. Cross-instrument generalisation
  check — if edge is only on SPY, variance-scaling is regime-specific,
  not mechanism-level.

## Kill criteria (pre-committed)

If any of the following happens at end of Stage 3, the hypothesis is
falsified regardless of secondary metrics:

1. **Kill #1 — Variance-scaling NOT sharper than vol-scaling**: top-
   candidate Sharpe edge on both spy_real AND ndx_real is ≤ iter 004's
   edge (+0.08 each). Moreira-Muir's "variance is more persistent"
   claim is empirically false on this data; direction closed.
2. **Kill #2 — Cap-hit pathology**: top config's `scale_cap_hit_frac >
   0.90` on any dataset. Variance-scaling pinned to cap is indistin-
   guishable from fixed-leverage buy-hold; mechanism is degenerate.
3. **Kill #3 — Real-data PBO regression**: G1 PBO on either spy_real OR
   ndx_real > 0.5 (vs iter 004's 0.31 / 0.35). Variance-scaling's tighter
   functional form is MORE overfit-sensitive; direction closed.

None of these is a trivial arithmetic outcome — each encodes a real
structural property of the mechanism family.

## Expected budget

- **Configs to test**: 12 (target_vol ∈ {0.15, 0.20} × lookback ∈ {21,
  63, 126} × max_leverage ∈ {1.5, 2.0}). Deliberately 3× smaller than
  iter 004's 36-config grid to preserve DSR headroom. `n_trials` after
  this iter: 4156 + 12 × 3 = **4192** (just +36 from iter 004).
- **Wall-time**: ~3-5 minutes (12 configs × 3 datasets × 3-5 k-bar
  series).
- **Files to create** under
  `iterations/005-2026-04-24-1008-variance-managed-spy/`:
  - `hypothesis.md` (this file)
  - `run_backtests.py` — grid runner + results.json
  - `numpy_reference.py` — hand-rolled numpy variance-scaling (G7)
  - `compute_gates_and_score.py` — 7-gate battery + scoring.py call
  - `results.json`, `verdict.json`, `final_report.md`
- **Simulator reuse**: `ai_trade.backtest.metrics.vol_target.apply_vol_target`
  won't work as-is (first-order form); will implement
  `apply_variance_target` as a small addition near it OR inline in
  `run_backtests.py` (prefer the latter to keep the production
  namespace unchanged).
- **Tests**: `tests/test_variance_target_sizing.py` with TDD — 5 specs
  covering the squared-denominator form, no-look-ahead, cap clipping,
  zero-vol degenerate case, and numeric agreement with Moreira-Muir
  Table I row 1.

## Structural novelty check

Iter 005 is **not a parameter variation** of iter 004. The functional
form changes from `σ^{-1}` to `σ^{-2}`:

| form | formula | responsiveness to 2× vol shock |
|---|---|---|
| iter 004 (Carver vol-scaling) | `s_t = target_vol / σ̂_{t-1}` | scale halves (2× ↔ 1/2) |
| iter 005 (Moreira-Muir variance-scaling) | `s_t = target_vol² / σ̂²_{t-1}` | scale quarters (2× ↔ 1/4) |

Different scaling exponent → different predicted alpha (per the
Moreira-Muir paper itself, their Table II shows `1/σ²` gains ~2× the
`1/σ` gains on CRSP). This is a qualitative change in mechanism, not a
grid sweep on iter 004.

DEAD_ENDS compliance (checked line-by-line):

- ✅ Not SMA/EMA+LETF+stop (iter 001)
- ✅ Not sector rotation on small universe (iter 002/003)
- ✅ Not "parameter variations of iter 004 base config" — different
  mathematical form
- ✅ Not "4-config grid on near-zero regime" (iter 002 warning) — 12
  configs with expected return dispersion (target_vol × max_leverage
  span 1.5× to 2×)
- ✅ Not a dead-end family — explicitly listed as "option 1: PICK
  FIRST" in iter 004's final_report.md and as direction `0a` in
  BASE_MEMORY.md

## Implementation plan

1. **TDD first**: write `tests/test_variance_target_sizing.py` with 5
   failing specs covering the variance-scaling contract. Red.
2. Implement `apply_variance_target(returns, target_vol, lookback,
   max_leverage)` inline in `run_backtests.py` (production-namespace
   change deferred — keeps `src/` unchanged for this iteration). Pass
   all 5 specs. Green.
3. Copy iter 004's `run_backtests.py` structure: same 3 datasets, same
   2 bps cost model, same output schema. Replace the sizing call with
   `apply_variance_target`. Generate 12 × 3 = 36 `(cfg, dataset)` runs.
4. `numpy_reference.py` — hand-rolled numpy implementation of variance-
   scaling + turnover cost + CAGR. Used by G7 cross-lib gate.
5. `compute_gates_and_score.py` — copy iter 004's gate harness verbatim,
   update `CUMULATIVE_N_TRIALS = 4156 + 36 = 4192`.
6. Final report + verdict.json.

## Confidence

Prior iteration evidence:

- Iter 004: vol-scaling gave +0.08 Sharpe on real data + 6/7 gates. The
  mechanism is partially validated.
- Moreira-Muir 2017 Table II: variance-scaling Sharpe uplift is +2× to
  +4× vol-scaling Sharpe uplift on CRSP factors.
- Cederburg et al. (2020) counterpoint: OOS variance-scaling is ~30%
  weaker than paper — but even at 30% attenuation, 2× uplift → ~+0.14
  expected edge, still clears +0.10 gate.

Expected outcome: Sharpe edge +0.10 to +0.15 on spy_real / ndx_real,
crosses winner threshold. DSR may still fail at n_trials=4192 (needs
Sharpe ~1.4, we'd be at ~1.05-1.10). **STRONG** or **PROMISING** tier
likely; WINNER possible if DSR p-value surprises downward.

## Post-mortem anchors

If **WINNER**: iter 005 closes the hunt. Paper-trading proposal is
OUT of scope (user-decision, mandate §7 override).

If **STRONG / PROMISING / MARGINAL** but kill criteria don't fire:
feed lessons back as direction "0c" — e.g., try **variance-scaling +
momentum signal** (Moreira-Muir full spec with skew / mom overlay) for
iter 006.

If **FAIL or kill criteria fire**: vol-adaptation single-asset family
is empirically closed on this data. Next iteration should pivot to
direction `2` (return-stacked NTSX rotation) or `5` (cross-asset carry),
both structurally unrelated.
