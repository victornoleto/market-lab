# Iteration 075 — iter 064 + GLD/TLT trend sleeve ensemble (non-SPY-co-exposed 2nd leg)

## Hypothesis

Build a **non-SPY-co-exposed** 2nd leg by pairing two canonical
diversifiers — **GLD** (gold) and **TLT** (long-duration treasuries) —
into an equal-weight risk-parity sleeve with a Faber 2007 long-only
SMA-200 trend filter and 21d inverse-realized-vol scaling targeting
~10% annualized portfolio volatility. Linearly ensemble this sleeve
with iter 064's saved stream at 7 weight cfgs `w_sleeve ∈ {0.10,
0.15, 0.20, 0.25, 0.30, 0.35, 0.40}`.

The hypothesis directly tests **BASE_MEMORY direction shift**
following iter 074's closure of the SPY-co-exposed saved-stream-
ensemble axis at 89:

> "iter 075 must use 2nd leg ρ < 0.5 vs iter 064 (non-equity) OR
> S > 1.30 OR market-beta-neutral."

GLD + TLT is the canonical **non-equity non-SPY-co-exposed** anchor
[risk_parity, ch.5]; gold's strategic role and ρ ≈ 0 with SPY are
documented in Erb-Harvey (2006) FAJ 62(2); TLT's flight-to-quality
role gives ρ ≈ −0.2 to −0.3 with SPY in stress regimes
[risk_parity, p.80-81]. Faber's SMA-200 trend filter avoids the
2008/2022 bond drawdowns by sitting in cash when below the moving
average. Combined sleeve standalone Sharpe is expected ~0.4-0.6 —
not a winner alone, but enough to lift iter 064's ensemble Sharpe
via Markowitz benefit-of-low-correlation if ρ-leg is ≤ 0.3.

## Primary citation

`[stocks_on_the_move, p.81]` — trend lookback rationale for the
SMA-200 filter on each sleeve leg. Clenow uses 100-200 day lookbacks
for the universe-broad trend filter in Stocks on the Move; Faber
(2007) generalises this to non-equity assets.

## Additional citations

- **Faber, M.** (2007). "A Quantitative Approach to Tactical Asset
  Allocation." SSRN 962461. — Long-only SMA-200 trend filter on
  multi-asset baskets; reference paper for sleeve construction.
- **Erb, C., & Harvey, C.** (2006). "The Strategic and Tactical Value
  of Commodity Returns." *Financial Analysts Journal* 62(2), 69-97.
  DOI: 10.2469/faj.v62.i2.4084 — gold strategic-allocation role,
  inflation-hedge mechanism.
- `[risk_parity, ch.5]` — Asness, C., Frazzini, A., & Pedersen, L.
  (2012). "Leverage Aversion and Risk Parity." *FAJ* 68(1), 47-59.
  SSRN 1728082. — risk-parity rationale for equal-weighting GLD+TLT.
- **Markowitz, H.** (1952). "Portfolio Selection." *Journal of Finance*
  7(1), 77-91. DOI: 10.1111/j.1540-6261.1952.tb01525.x — convex-
  combination Sharpe identity (ensemble math, identical to iter 074).
- `[volatility_trading, p.218]` — Sinclair (2013), inverse-vol sizing
  primitive (sleeve scaling).
- `[advances_fin_ml, p.222-223]` — DSR with per-iteration n_trials
  (relaxed convention 2026-04-25; iter 075 uses native v2 convention
  with `n_trials = 7`).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV on 7-cfg grid.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.

## Edge source

What does SPY 1x miss that this captures? **Cross-asset
diversification benefit from a non-equity, non-SPY-co-exposed
2nd leg.** Iter 074 proved that an SPY-co-exposed 2nd leg
(iter 016 = 60% SPY direct) gives ρ ≈ 0.81 with iter 064 and
mostly recovers a linear-average Sharpe rather than the Markowitz
super-additive lift. GLD/TLT trend has documented ρ ≈ 0 with SPY
[risk_parity, p.80-81], so the variance-reduction benefit of
ensembling at moderate weight (0.10-0.40) should be measurably
larger and produce a Sharpe lift over iter 064's 1.33 spy / 1.38
ndx instead of regressing.

## Datasets

- **educational** (SPYSIM synth + iter 064 stream constrained by
  VRP basket to 2006+; effective window 2006-01-04 → 2026-04-15
  ≈ 20y after inner-join with GLD+TLT) — tests sleeve mechanism on
  the longest window iter 064 supports.
- **spy_real** (SPY/UPRO + iter 064 stream constrained to 2009-06-26
  → 2026-04-15 ≈ 17y) — primary winner-target dataset.
- **ndx_real** (QQQ/TQQQ + iter 064 stream 2010-02-16 → 2026-04-15
  ≈ 16y) — second-real-data dataset; tests ndx-period generalisation.

GLD inception 2004-11-18, TLT inception 2002-07-26 — both fully
cover all three iter 064 windows. Inner-join with iter 064 streams
loses no bars due to GLD/TLT availability.

## Kill criteria (pre-committed)

If any of the following holds at end of Stage 3, the hypothesis is
falsified regardless of secondary metrics:

- **A — ρ-floor not broken**: `corr(r_064, r_sleeve)` > 0.5 on ≥ 2 of
  3 datasets. Falsifies the non-SPY-co-exposed thesis (means GLD/TLT
  trend is too SPY-correlated to lift Sharpe via diversification).
- **B — Sleeve too weak**: 2nd leg standalone Sharpe < 0.20 on ≥ 2
  of 3 datasets. Sleeve adds drag without compensating diversification.
- **C — Sharpe regress**: best combined cfg's Sharpe < iter 064
  standalone Sharpe by ≥ 0.05 on ≥ 2 of 3 datasets (same as iter
  074's KILL A). Means the ensemble doesn't actually lift Sharpe.
- **D — Score below STRONG**: best cfg score < 75. Indicates the
  sleeve is structurally a drag on multiple criteria.
- **E — Cross-lib bug**: G7 > 3 pp CAGR difference on ≥ 1 dataset
  between full implementation and numpy-pure reference.
- **F — Overfit**: PBO grid-level > 0.5 on ≥ 2 of 3 datasets.
- **G — DSR fails**: best cfg DSR p-value > 0.05 worst-of-3 with
  per-iter `n_trials = 7` (v2 convention).

Pass condition that signals winner candidate: best cfg ALL of
{Sharpe ≥ bench + 0.10 on 2/3 datasets, gates 5+/4+/4+ cross-ds,
DSR p < 0.05, CAGR ≥ 0.8 × bench on 2/3, MDD ≤ bench + 5pp on 2/3,
score ≥ 90} → 🏆 WINNER under v2 convention.

## Expected budget

- Configs to test: **7** (`w_sleeve ∈ {0.10, 0.15, 0.20, 0.25, 0.30,
  0.35, 0.40}`)
- Wall-time: **~30-60 min** (sleeve sim + ensemble + gates × 7 cfgs ×
  3 datasets, mostly reusing iter 064 saved streams)
- Files to create:
  - `iter075_sleeve.py` — GLD/TLT trend sleeve simulator (new module)
  - `iter075_ensemble.py` — linear blend with iter 064 stream
    (mirrors iter 074 pattern)
  - `numpy_reference_iter075.py` — hand-rolled numpy reference for G7
  - `run_backtests.py` — driver across 3 datasets × 7 cfgs
  - `compute_gates_and_score.py` — gate battery + scoring with v2 DSR
  - `tests/test_iter075_sleeve.py` — TDD specs (14+ tests, mirroring
    iter 074 test conventions)
  - `results.json` — full backtest output with `returns_series` key
  - `verdict.json` (v1) + `verdict_v2.json` (per-iter DSR)
  - `final_report.md` + `plot_vs_benchmark_*.png`

## Implementation plan

1. **Write TDD spec** `tests/test_iter075_sleeve.py` (≥ 14 tests)
   - Sleeve construction: SMA-200 trend filter long-only correctness
   - Inverse-21d-vol scaling reaches target 10% portfolio vol
     (within ±2pp tolerance)
   - Equal-weight GLD+TLT inner construction (50/50 risk-budget)
   - Out-of-sample lag enforcement (T-1 signal → T return)
   - Kill-switch: when below SMA-200 → 0% allocation, returns ≈ 0
   - Boundary: SMA-200 not yet computable → 0% allocation
   - Cross-lib: numpy-pure reference matches main impl ±1e-9
   - Linearity: 2× weight → 2× returns (vol scaling preserves)
   - Determinism: same input → same output
   - Inner-join with iter 064 stream preserves date alignment
   - Combined sleeve at w_sleeve=0 → returns iter 064 only
   - Combined sleeve at w_sleeve=1 → returns sleeve only
   - Convex combination at w_sleeve=0.5 → linear avg of two streams
   - Cost model parity: G7 ≤ 3pp CAGR (Stage 3d cross-lib check)

2. **Implement** `iter075_sleeve.py`
   - Loads GLD + TLT prices from Tiingo cache
   - Computes daily returns
   - Applies SMA-200 trend filter (long-only): position = 1 if
     `price[T-1] > SMA-200[T-1]` else 0
   - Computes 21d trailing realized vol on each leg
   - Sizes each leg to target vol: `pos_t = TARGET_VOL / vol_t · trend_t`
   - Equal-weight blend: `r_sleeve = 0.5 · r_GLD_sized + 0.5 · r_TLT_sized`
   - Caps individual leg position at 1.0 (no leverage)
   - Returns daily net return stream

3. **Implement** `iter075_ensemble.py` (mirror iter 074 pattern)
   - Load iter 064 saved stream per dataset
   - Compute sleeve stream once per dataset
   - Linear blend at 7 weight cfgs
   - Save all streams to `results.json["returns_series"]`

4. **Implement** `numpy_reference_iter075.py`
   - Hand-rolled pure-numpy SMA-200 + vol scaling + ensemble
   - Compares CAGR with main impl: assert ≤ 3pp difference (G7)

5. **Run** `run_backtests.py` on all 3 datasets

6. **Compute gates and score** in `compute_gates_and_score.py`:
   - Gates G1-G7 per dataset on top-5 cfgs by Sharpe
   - DSR uses `n_trials = 7` (per-iter v2)
   - Robustness sub-windows (3 chronological thirds × 3 datasets)
   - Output `verdict.json` (v1: cumulative DSR) + `verdict_v2.json`
     (v2: per-iter DSR)

7. **Final report** + update BASE_MEMORY + plot

## Selection rationale

Per BASE_MEMORY direction #1, **Plano C sleeve** (GDE/AVUV/AVDE/AVEM
/BTGD) is the recommended 2nd leg. Those tickers are NOT in the
Tiingo cache (verified). The closest in-cache analog combining
**non-equity** (gold) + **non-SPY-co-exposed** (long bonds) +
**well-documented academic citation** (Faber 2007 + Erb-Harvey 2006
+ Asness-Frazzini-Pedersen 2012) is **GLD + TLT trend sleeve**. This
is structurally distinct from:

- iter 010 (3-leg blend SPY+TLT+GLD, **iter-064-blind**, structural
  saturation) — iter 075 ensembles iter 064's saved stream with the
  GLD+TLT-only sleeve
- iter 074 (iter 016 + iter 064 ensemble; iter 016 is SPY+IEF, **SPY-
  co-exposed**) — iter 075 swaps iter 016 for non-equity sleeve
- iter 022/023/024 (TOM modulator / TSM-PRIMARY 4-asset / bond-curve
  carry) — iter 075 uses Faber trend filter, not carry/TOM/TSM-as-
  primary

The structural novelty axis is: **first iter-064-anchored ensemble
with a 2nd leg that has documented ρ ≈ 0 to SPY**. Predicted ρ to
iter 064 is < 0.3 (vs iter 074's 0.81 with SPY-co-exposed iter 016).

If pre-committed kill A fires (ρ > 0.5), the BASE_MEMORY direction
itself is partially refuted (gold/bonds aren't enough decoupled to
break iter 064's market-beta-anchored equity exposure). If kill A
clears but kill C fires, sleeve standalone Sharpe is too weak.

If both clear, this is a structurally robust WINNER candidate that
beats iter 074 v2's fragility note.
