# Iteration 062 — Internal-LETF UPRO substitution preserving equity exposure

## Hypothesis

Within the iter 037 saved-stream library (canonical static stack
0.60 SPY + 0.45 IEF + 0.45 GLD = 1.50 NAV, score 79), substitute the
unlevered SPY equity leg with the 3× LETF UPRO at a weight that
**preserves the SPY-equivalent equity exposure (0.60)** but uses the
NAV freed by the smaller equity weight to **overweight the bond/gold
diversifier legs** (preserving the 1.50 total NAV).

```
iter 037:  0.60 SPY  + 0.45 IEF + 0.45 GLD = 1.50 NAV  (eq SPY-equiv = 0.60)
iter 062:  0.20 UPRO + 0.65 IEF + 0.65 GLD = 1.50 NAV  (eq SPY-equiv = 0.60 = 3×0.20)
```

The structural change is **two-fold**:

1. **Internal-LETF financing replaces external rf=0 margin.** Iter
   037's implicit 0.50 borrow on a $1.50 NAV portfolio is at
   ``rf=0`` per the project's `_sharpe()` convention — invisible drag.
   Iter 062's UPRO leg has its swap-funding (≈ T-bill + 0.95%) and
   expense ratio (0.91%/yr) baked into the daily NAV — these costs
   ARE visible inside `r_UPRO`. Net visible UPRO drag at weight 0.20:
   ≈ 0.20 × 1.86%/yr ≈ **0.37%/yr** absolute drag.
2. **Diversifier overweight (+0.20 IEF + 0.20 GLD).** Iter 061
   empirically established that within the iter 037 stack, the bond
   and gold legs are **Sharpe-positive contributors** (not
   Sharpe-neutral diversifiers). Reducing them lowers combined
   Sharpe. By symmetry, raising them should lift combined Sharpe.
   Iter 062 raises both by +0.20 (from 0.45 to 0.65 each), funded
   by the 0.40 NAV released by replacing 0.60 SPY with 0.20 UPRO.

**Why it should work**: the iter 061 finding ΔCAGR/ΔSharpe ≈ 16
pp/Sharpe-unit (ratio of CAGR change to Sharpe change for equity-
weight perturbations on iter 037) implies the inverse direction —
diversifier-overweight — should LIFT Sharpe. Each +0.05 of
diversifier weight (Sharpe-positive contributor) is predicted to
add ~0.05 to combined Sharpe minus diversification-saturation
effects. With +0.40 total diversifier weight increase and modest
~0.37%/yr UPRO drag, predicted combined Sharpe lift on educational
≈ 0.96 → 1.10-1.20. At higher Sharpe with cumulative_n_trials=4332,
DSR worst-p should drop from iter 037's 0.222 toward 0.05-0.15.

The path-dependent **vol decay** of UPRO (well-documented
[leverage_for_the_long_run, p.20-25] for daily-reset LETFs) is the
main risk: in choppy regimes, 3× daily reset compounds to less than
3× simple return, lowering CAGR and potentially Sharpe. This is
counterbalanced by the diversifier overweight cushion.

## Primary citation

`[leverage_for_the_long_run, p.19-25]` — Hsiao & Williams (2017),
*J. Index Investing*. The "preserved-leverage zone" (1.5-2.0× total)
on a diversified equity+bond base is where LETF NAV-path financing
delivers Sharpe parity with cash-equity at preserved exposure.

## Additional citations

- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen (2012) multi-leg
  risk-parity decomposition. Diversifier-overweight derives from the
  same architecture as iter 037; the bond/gold legs harvest term and
  commodity premia at preserved correlations.
- `[risk_parity, p.5, p.10-11, ch.1]` — AFP 2012 SSRN 1728082, static
  fixed-weight stack mechanism.
- `[leverage_for_the_long_run, p.20-25]` — daily-reset LETF formula
  and vol decay derivation (`r_LETF[t] = 3·r_SPY[t] - 2·daily_rf -
  daily_expense`, where vol decay is captured by daily compounding
  of the multiplied series).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  penalty (n=4332 after this iteration).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity: numpy
  reference for the 3-leg static stack PLUS a separate parity check
  on the synth-UPRO formula r_synth = 3 r_SPY − k.
- `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (vacuous
  for static weights and prior-day-only synth formula).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- Erb, C.B. & Harvey, C.R. (2006), *FAJ* 62(2) 69-97,
  DOI 10.2469/faj.v62.n2.4084 — gold strategic role; preserves
  iter 037 architecture rationale.
- Koijen, Moskowitz, Pedersen, Vrugt (2018), *JFE* 127(2) 197-225,
  DOI 10.1016/j.jfineco.2017.11.002 — bond term-premium harvesting
  via duration leg (IEF) preserved.
- Markowitz (1952), *J. of Finance* 7(1) 77-91 — closed-form Sharpe
  identity for static linear combinations (used for sanity/G7).
- Web: ProShares UPRO prospectus 2024-2025, expense ratio 0.91%/yr,
  swap counterparty financing benchmark T-bill (3-month) + 0.95%.
  https://www.proshares.com/our-etfs/leveraged-and-inverse/upro

## Edge source

SPY 1× buy-hold collects equity beta directly. Iter 062 collects
equity beta via UPRO (3× daily-reset LETF, internal swap financing)
at preserved exposure, freeing 0.40 of NAV to **double-down on
Sharpe-positive bond/gold diversifier legs** within a 1.50× total
NAV stack. The edge is "more diversifier-leg Sharpe at preserved
equity exposure", financed by replacing external margin (rf=0
invisible) with internal LETF swap (1.86%/yr visible). The trade-off
is whether the diversifier-overweight Sharpe lift exceeds UPRO's
internal-financing visible drag plus vol decay.

## Datasets

- **educational** (2004-11-19 → 2026-04-15, 21y): synth UPRO from
  SPY pre-2009-06-25 (formula `r_synth_UPRO = 3·r_SPY − 0.91%/252`,
  rf=0 convention consistent with project), real UPRO post-2009-
  06-25. The joined series matches iter 037's educational window.
  Synth-UPRO pre-2009 covers 2008-09 GFC stress test (UPRO MDD
  ~−85% by mechanical formula); real UPRO post covers 2020 + 2022
  drawdowns. The benchmark is the FROZEN educational benchmark
  (Sharpe 0.68, CAGR 11.47%, MDD 55.14%) per `WINNER_AND_RANKING.md`.
- **spy_real** (2009-06-25 → 2026-04-15, 17y): real UPRO from
  inception. Matches iter 037 spy_real window exactly. Benchmark:
  SPY b&h Tiingo Sharpe 0.90.
- **ndx_real** (2010-02-12 → 2026-04-15, 16y): real TQQQ from
  2010-02-11 (1 day before window start). Matches iter 037 ndx_real
  window exactly. Benchmark: QQQ b&h Tiingo Sharpe 0.955.

## Pre-committed kills

| # | kill | trigger |
|---|---|---|
| A | Combined Sharpe regress vs iter 037 by ≥ 0.10 on ≥ 2 datasets | catastrophic vol decay or financing drag dominates |
| B | DSR worst-p ≥ iter 037 baseline 0.222 | hypothesis core fails (no Sharpe lift translates to no DSR improvement at fixed n_trials) |
| C | Score < iter 037 baseline 79 | substitution provides no improvement |
| D | G7 cross-lib > 3 pp on any dataset | engine bug or synth-UPRO formula mismatch |
| E | MDD breach > bench+5pp on ≥ 2 datasets | UPRO vol decay or 2008 synth blow-up amplifies portfolio MDD |
| F | CAGR floor regress on ≥ 2 datasets (CAGR < 0.8×bench) | combined CAGR drops below floor due to diversifier-overweight + UPRO drag |

If kill A AND kill B fire → hypothesis fully falsified (UPRO substitution + diversifier overweight delivers neither Sharpe lift nor DSR improvement).
If kill C fires → no improvement on iter 037 baseline (close internal-LETF axis on iter 037 anchor at this weight scheme).

## Expected budget

- Configs to test: **1** (single pre-committed cfg, no grid sweep,
  no post-hoc selection — same discipline as iter 037 / 058 / 059 /
  060 / 061).
- Wall-time: ~10-15 min for the simulator + gates + score + plots.
- Files to create:
  - `synth_letf_3leg.py` — synth-UPRO + 3-leg static stack
    (extends iter 037's primitive; reuses `apply_static_stack_3leg`
    on the UPRO-substituted streams).
  - `numpy_reference_iter062.py` — hand-rolled numpy reference for
    G7 parity (numpy formula for synth-UPRO and weighted sum).
  - `run_backtests.py` — single-cfg runner (model after iter 037).
  - `compute_gates_and_score.py` — gates + score (model after
    iter 058/059/061).
  - `tests/test_synth_letf_3leg.py` — TDD tests for synth-UPRO
    formula and stack identity.
  - `results.json` — full per-dataset metrics + returns_series.
  - `verdict.json` — score result (via `scoring.py`).
  - `final_report.md` — Stage 5 report.
  - `plot_vs_benchmark_spy_real.png` + `plot_vs_benchmark_ndx_real.png`.

cumulative_n_trials advance: 4331 → **4332** (+1).

## Implementation plan

1. **TDD**: write 12-15 tests under `tests/test_synth_letf_3leg.py`
   covering synth-UPRO formula, joined series alignment, weight
   identities, cost accounting, and reduce-to-iter-037 case.
2. Implement `synth_letf_3leg.py` with `synth_upro_returns(r_spy)`
   helper + `load_letf_3leg(...)` for the joined real+synth UPRO
   stream + a thin wrapper around iter 037's
   `apply_static_stack_3leg`.
3. Implement `numpy_reference_iter062.py` for G7 — numpy-pure
   replication of synth-UPRO formula AND weighted-sum stack.
4. Run `run_backtests.py` on all 3 datasets; produce
   `results.json` with per-dataset metrics + `returns_series` (top
   cfg per dataset, mandatory schema for plot helper).
5. Run `compute_gates_and_score.py` for the 7-gate battery + 0-100
   score using `scoring.py`. Cumulative n_trials = 4332.
6. Generate plots via `plot_helper.py --iter 062`.
7. Write `final_report.md` honest verdict.
8. Update `BASE_MEMORY.md` (add 6-field iter 062 entry, update
   frontmatter, refresh promising directions list, append 1-line
   to dead-ends if structural closure).

## Falsification clarity (anti-rationalization)

- **PASS**: score ≥ 80 AND DSR worst-p < 0.20 AND no kill A or kill B
  fired → meaningfully advances iter 037 ceiling.
- **WINNER**: score ≥ 90 AND all 5 strict winner conditions met
  (DSR worst-p < 0.05).
- **STRONG**: score 75-89, kill C clean.
- **FAIL or NEAR-FAIL**: score < 60 or kill A + kill B both fire →
  internal-LETF axis on iter 037 anchor closed at this weight scheme.

This iteration ends in ONE of: WINNER (halt), STRONG with new ceiling
(continue with internal-LETF on iter 058 anchor next), STRONG matching
iter 037 (close iter-037-anchor internal-LETF axis), or FAIL (close
internal-LETF axis on iter 037 anchor entirely).
