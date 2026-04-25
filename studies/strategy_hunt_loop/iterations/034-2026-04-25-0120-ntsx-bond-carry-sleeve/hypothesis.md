# Iteration 034 — NTSX bond-carry sleeve (zero-net-notional duration spread on iter 015 base)

**Date:** 2026-04-25 01:20
**Slug:** `ntsx-bond-carry-sleeve`
**Cumulative n_trials before iter 034:** 4288

---

## Hypothesis

Iter 033 (full IEF→TLT swap at 0.6 weight) reached PROMISING 72/100
because **bond variance scales with duration² and offset the carry
premium gain along the Sharpe curve** (~7% IEF vol → ~14% TLT vol;
Sharpe Δ vs iter 015 ≈ 0). The structural lesson: full-duration
substitution is the wrong axis to pull on a static stack.

Iter 034 tests a **zero-net-notional duration spread** within the
bond sleeve of iter 015. Total bond exposure remains fixed at 0.6
notional (preserves iter 015's diversification weight); a fraction
α is reallocated from IEF (7-10y) to TLT (20-30y). The **spread
return** `r_TLT − r_IEF` carries the cross-sectional bond-carry
premium documented by Koijen-Moskowitz-Pedersen-Vrugt (2018), but
spread vol is much lower than TLT vol alone because IEF and TLT
share most yield-curve shocks (ρ ≈ 0.85+). The hypothesis: at
α = 0.2, the carry premium is harvested at a much smaller variance
penalty than iter 033's full swap, potentially restoring iter 015's
Sharpe while gaining a few bps of CAGR.

```
iter 015 cfg: 0.9 SPY + 0.6 IEF                               (1.5× total)
iter 033 cfg: 0.9 SPY + 0.6 TLT                                (1.5× total)
iter 034 cfg: 0.9 SPY + 0.4 IEF + 0.2 TLT                     (1.5× total, identical leverage)
              = 0.9 SPY + 0.6 IEF + 0.2 (r_TLT − r_IEF)       (algebraic identity)
```

The α = 0.2 split is the **midpoint** of BASE_MEMORY's recommended
range {0.1, 0.2, 0.3} — a Bayesian-symmetric pre-commit when no
strong prior favors any specific α. Single config; no sweep; no
post-hoc selection; n_trials inflation matches iter 033 (3 trials).

---

## Primary citation

`[risk_parity, ch.5]` — bond term-premium decomposition for the
diversifying leg of a levered stack. Asness-Frazzini-Pedersen
(2012) note that the **choice of duration within the bond sleeve**
determines how much of the term premium the levered base actually
harvests: longer duration → larger expected term premium per unit
notional, but only at the cost of higher bond-leg variance (per
Cochrane-Piazzesi 2005 forward-rate-loadings + Ilmanen 2011 ch.6-7).
The cross-sectional bond carry literature (KMPV 2018) explicitly
exploits the duration spread within a fixed-notional sleeve — this
iteration is the simplest single-asset analog on the iter 015 base.

## Additional citations

- `[risk_parity, p.5, p.10-11, ch.1]` — risk-parity static stack
  (preserved from iter 015 verbatim).
- `[leverage_for_the_long_run, p.19-20]` — leverage on a diversified
  base captures duration risk-premium without market-timing.
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- Asness, Frazzini & Pedersen (2012). "Leverage Aversion and Risk
  Parity." *Financial Analysts Journal* 68(1): 47-59. SSRN
  [1728082](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1728082).
- **Koijen, Moskowitz, Pedersen & Vrugt (2018). "Carry."** *Journal
  of Financial Economics* 127(2): 197-225. DOI:
  [10.1016/j.jfineco.2017.11.002](https://doi.org/10.1016/j.jfineco.2017.11.002).
  Cross-sectional carry within asset class (here: USTs across
  duration band) is the canonical primary citation — bond carry is
  largest at 20-30y and the spread (TLT − IEF) is the natural
  zero-net-notional way to harvest it without doubling variance.
- **Cochrane & Piazzesi (2005). "Bond Risk Premia."** *American
  Economic Review* 95(1): 138-160. DOI:
  [10.1257/0002828053828581](https://doi.org/10.1257/0002828053828581).
  Term-structure factor predicts bond excess returns over cash —
  forward-rate loadings concentrate in the long end.
- **Ilmanen (2011). *Expected Returns: An Investor's Guide to
  Harvesting Market Rewards.*** Wiley. Chapter 6-7 on term premium
  and bond carry. Empirical magnitudes: 20-30y term premium ~75-150
  bps/yr above 7-10y over the post-Volcker sample.

## Edge source

In ONE sentence: **iter 015 leaves the long-end term premium
untouched (IEF is 7-10y duration only) and iter 033 captures it but
doubles bond variance; iter 034 keeps iter 015's bond notional fixed
at 0.6 and rotates 1/3 of it into TLT — capturing α × (term-premium
spread) at a much smaller variance cost than iter 033 because the
spread return r_TLT − r_IEF has roughly 6-8% volatility (vs 14% for
TLT alone) due to high inter-treasury correlation.**

---

## Why this is structurally different from prior iterations

| iteration | bond exposure | mechanism | iter 034 vs |
|---|---|---|---|
| **iter 015** | 0.6 IEF only | static 2-leg stack | iter 034 splits the 0.6 sleeve into 0.4 IEF + 0.2 TLT — **3-leg generalization, identical total bond notional** |
| **iter 033** | 0.6 TLT only | 100% duration substitution | iter 034 retains 67% IEF (avoids the 14% TLT vol penalty), gets 33% TLT exposure for term-premium harvest |
| iter 016 | TLT in vol-managed blend | dynamic vol-target | iter 034 is STATIC — no Moreira-Muir scaling, no σ²_port feedback |
| iter 024 | TLT or SHV (timing) | T10Y3M-allocated bond mix | iter 034 has NO timing — pure static 0.4/0.2 split |
| iter 032 | NTSX + put-spread overlay | iter 015 base + iter 031 VRP | iter 034 has NO overlay, NO put-spreads |

The structurally novel axis: **3-leg static stack with a
zero-net-notional duration spread inside the bond sleeve**. Neither
iter 015 (single bond ticker) nor iter 033 (single bond ticker, just
swapped) has tested a bond mix at preserved total notional. Note: iter
024 used a 2-bond mix but with TIME-VARYING allocation (T10Y3M
indicator); iter 034 uses STATIC fixed weights, so the mechanism is
qualitatively different — it tests the spread premium at a fixed
duration barbell, not a yield-curve-timing signal.

DEAD_ENDS check: no entry forbids 3-leg static stack with two bonds.
The closest entry is iter 024's **T10Y3M-allocated bond mix** — that
closes "carry-as-allocation timing" but does NOT close "duration
spread at fixed weights" (which is a different mechanism, not
allocation timing).

---

## Datasets

| dataset | window | universe | rationale |
|---|---|---|---|
| educational | 2002-07-26 → 2026-04-15 | SPY + IEF + TLT | TLT-inception-aligned (24y, matches iter 033 window for direct Δ comparison) |
| spy_real | 2009-06-25 → 2026-04-15 | SPY + IEF + TLT | 17y post-GFC, full benchmark window |
| ndx_real | 2010-02-12 → 2026-04-15 | QQQ + IEF + TLT | 16y tech-heavy |

Educational benchmark is **re-measured on the TLT-aligned window**
(matches iter 015/024/033's `build_custom_benchmarks` pattern).
spy_real and ndx_real benchmarks remain frozen to
`scoring.BENCHMARKS`. The canonical winner check uses **FROZEN**
benchmarks per WINNER_AND_RANKING.md.

---

## Pre-committed single config

| param | value | rationale / citation |
|---|---|---|
| `cfg_id` | `ntsx_synth_90_spy_40_ief_20_tlt` | descriptive |
| `equity_symbol` | SPY (edu, spy_real), QQQ (ndx_real) | matches iter 015/033 |
| `bond_short_symbol` | IEF | iShares 7-10y Treasury (iter 015 baseline) |
| `bond_long_symbol` | TLT | iShares 20+y Treasury (carry-premium leg) |
| `equity_weight` | 0.90 | NTSX prospectus exact (verbatim from iter 015/033) |
| `bond_short_weight` | 0.40 | 0.6 × (1 − α) where α=0.2 |
| `bond_long_weight` | 0.20 | 0.6 × α where α=0.2 |
| **total bond notional** | **0.60** | **identical to iter 015 — preserves diversification weight** |
| `total_leverage` | 1.50 | sum of legs (identical to iter 015/033) |
| `rebalance` | daily | maintain fixed weights |
| `cost_bps_per_leg` | 0.0002 | 2 bps per unit per-leg ∆position (iter 015 cost model, applies per leg → 3× t=0 setup cost vs iter 015's 2×) |
| `funding_cost` | NOT modeled | iter 015 simplification preserved; iter 018-style funded variant deferred |

**Why a single α (no sweep)**: BASE_MEMORY's recommendation
explicitly listed {0.1, 0.2, 0.3} as candidates. Sweeping all 3
would inflate n_trials by 9 (3 cfg × 3 ds) and trigger PBO concerns
(N=3 grid is on the cusp of "small grid" risk per
`[advances_fin_ml, p.208-211]`). Pre-committing to α=0.2 (the
midpoint) is the Bayesian-symmetric choice when no specific α has
literature priority. If iter 034 PROMISING/STRONG, iter 035 can
revisit α-sweep with explicit grid PBO.

**Why 0.4/0.2 not 0.5/0.1 or 0.3/0.3**: α=0.2 gives a meaningful
TLT slice (33% of bond notional) without leaving IEF as the dominant
leg in name only. The variance math:
- σ_IEF ≈ 7%, σ_TLT ≈ 14%, ρ(IEF, TLT) ≈ 0.85.
- Bond leg vol(0.4 IEF + 0.2 TLT) ≈ √(0.16·49 + 0.04·196 + 2·0.4·0.2·0.85·7·14) = √29 ≈ 5.4%.
- iter 015 baseline (0.6 IEF only): 0.6 × 7 = 4.2%.
- iter 033 (0.6 TLT only): 0.6 × 14 = 8.4%.
- iter 034 sits at **5.4%** — only 28% above iter 015 (vs iter
  033's 100% above iter 015), so the variance penalty is much smaller.

**Funding-cost simplification**: real NTSX-equivalent on a
3-leg stack would pay ~0.5 × short-rate × 0.5 (additional notional)
as implicit financing. Synthetic version ignores this, which
**OVERESTIMATES** the strategy's edge by an estimated 50-100 bps
annually depending on regime (same magnitude as iter 015/033). A
sensitivity comment in the final report will quantify the impact,
mirroring iter 015 → iter 018's funded-replay convention.

---

## Kill criteria (pre-committed; binary, observable post-Stage-3)

If any of these triggers, the iteration is falsified independent of
secondary metrics:

| kill | criterion | rationale |
|---|---|---|
| **A** | Sharpe Δ vs iter 015 frozen reference < 0 on ≥ 2/3 datasets | **Spread doesn't add Sharpe** — variance penalty exceeds carry premium gain; bond duration tilt at any α is the wrong axis on static stack |
| **B** | ndx MDD > 45% | **Spread drawdown too painful** — 2022 dual rate-spike-+-tech-selloff produces unacceptable composite drawdown even at 0.2 TLT (iter 033 hit 47% at 0.6 TLT; iter 034 should benefit from much smaller TLT exposure) |
| **C** | DSR worst-p > 0.20 | **Distribution unacceptable** — even with smaller variance, spread's left tail is too heavy at this n_trials |
| **D** | G7 cross-lib diff > 3 pp CAGR | **Engine bug** (would invalidate all metrics) |
| **E** | Total score < 60 | **Below PROMISING** — iter 015 achieved 77, iter 033 achieved 72; a sleeve variant that scores < 60 is a structural regression that closes the bond-axis variation family completely |
| **F** | Robustness < 7/9 sub-windows positive | **Strategy has a regime where it systematically loses** — defensive pre-commit (iter 015 hit 9/9, iter 033 hit 9/9) |

Pre-commitment note: Kill A's threshold is **Sharpe < iter 015** (not
"Sharpe < iter 015 − 0.05") because iter 015 is the direct
mechanism-comparison benchmark. Kill B's 45% threshold is tighter
than iter 033's 50% because the variance argument predicts iter 034
should have a bond-leg vol of ~5.4% (vs iter 033's 8.4%) — if 2022
still produces a >45% MDD on ndx, the spread-premium hypothesis is
falsified at this preserved-notional design.

Crucially: **score < 80 is NOT an automatic kill** for this
iteration — the value is in establishing whether the
zero-net-notional spread is structurally additive (vs iter 015's 77
plateau) or neutral (vs iter 033's 72 PROMISING ceiling on full
substitution). A score of 75-79 STRONG that cleanly characterises
the spread-tilt axis is more informative than a forced higher score
via parameter tweaking.

---

## Expected budget

- Configs to test: **1** (single pre-committed cfg, mirrors iter 015/033)
- Datasets: 3 → **3 cumulative n_trials added** (4288 → 4291)
- Wall-time estimate: **30-45 min total**
  - Implementation: ~10 min (3-leg generalization of `apply_static_stack`
    + numpy reference; minimal extension of iter 015 module)
  - TDD specs: ~10 min (2-leg backwards-compat + 3-leg new specs)
  - Run + gates: ~5 min (no lookback dependencies)
  - Final report + BASE_MEMORY update + plots: ~15-20 min

- Files to create:
  - `synth_stacked_etf_3leg.py` — generic 3-leg stacker (mirrors iter 015's `synth_stacked_etf.py` pattern; preserves 2-leg via default α=0)
  - `numpy_reference_stacked_3leg.py` — pure-numpy G7 reference
  - `run_backtests.py` — adapted from iter 033 (3-leg cfg, IEF + TLT both loaded)
  - `compute_gates_and_score.py` — adapted from iter 033 (cumulative_n_trials=4291, iter 015 + iter 033 reference deltas)
  - `tests/test_iter034_ntsx_bond_carry_sleeve.py` — TDD specs (≥ 4 specs)
  - `results.json` + `verdict.json` — outputs
  - `final_report.md` — prose verdict
  - `plot_vs_benchmark_spy_real.png` + `plot_vs_benchmark_ndx_real.png`

- Files to **REUSE directly from iter 015** (no copy needed):
  - None — the 2-leg engine generalizes to 3 legs via new module
    (intentional: 3-leg has different cost-accounting at t=0 setup).
  - Iter 033's `compute_gates_and_score.py` skeleton (gates G1-G7,
    robustness) reused with cfg-name + n_trials adaptation.

---

## Implementation plan

1. **Write TDD specs** (`tests/test_iter034_ntsx_bond_carry_sleeve.py`)
   — ≥ 4 specs:
   - `test_3leg_stack_returns_match_2leg_when_alpha_zero` —
     equivalence check: `apply_static_stack_3leg` with `bd_long_w=0`
     == iter 015's `apply_static_stack` exactly (no spurious math).
   - `test_3leg_stack_preserves_total_bond_notional` — at α=0.2, `bd_short_w + bd_long_w == 0.6` exactly.
   - `test_3leg_stack_total_leverage_invariant` — sum of all three weights == 1.5 (matches iter 015/033).
   - `test_3leg_stack_cross_lib_parity_under_3pp` — pandas vs numpy
     reference agree to ≤3 pp CAGR on synthetic returns.

2. **Implement `synth_stacked_etf_3leg.py`** — generic 3-leg
   static stacker:
   ```python
   def apply_static_stack_3leg(r_eq, r_bd_short, r_bd_long, *,
                                eq_w=0.9, bd_short_w=0.4, bd_long_w=0.2,
                                cost_bps_per_leg=0.0002):
       ...
   ```
   Cost accounting at t=0: 3 legs × |w| × bps (one-time setup);
   t > 0 has zero turnover (static).

3. **Implement `numpy_reference_stacked_3leg.py`** — pure-numpy
   reference for G7. Mirrors iter 015's `numpy_reference_stacked.py`
   shape exactly.

4. **Implement `run_backtests.py`** — adapt iter 033's verbatim, change:
   - `DATASETS["educational"]["bond_short"] = "IEF"`, `bond_long = "TLT"`, `start = "2002-07-26"`
   - `DATASETS["spy_real"]["bond_short"] = "IEF"`, `bond_long = "TLT"`
   - `DATASETS["ndx_real"]["bond_short"] = "IEF"`, `bond_long = "TLT"`
   - `CFG["cfg_id"] = "ntsx_synth_90_spy_40_ief_20_tlt"`
   - Loader: `load_triple_returns(eq, bd_short, bd_long, start, end)` — inner-join 3 legs

5. **Implement `compute_gates_and_score.py`** — adapt iter 033's
   verbatim, change:
   - `CUMULATIVE_N_TRIALS = 4288 + 1 * 3` (=4291)
   - `iter015_reference_metrics` + `iter033_reference_metrics`
     dicts (read from each iter's `verdict.json`)
   - Reference deltas updated for `delta_vs_iter015` and
     `delta_vs_iter033` blocks
   - Import `apply_static_stack_3leg_np` + `cagr_np` from iter 034's
     `numpy_reference_stacked_3leg.py`
   - `verdict["primary_citation"]` updated to lead with
     `[risk_parity, ch.5]` + KMPV 2018 (cross-sectional carry).

6. **Run pytest** — confirm new specs pass + baseline unchanged
   (current baseline ~17 collected from clean tests + 82 pre-existing
   collection errors; iter 034 adds 4-5 new passing specs).

7. **Run backtests** — `uv run python run_backtests.py` produces
   `results.json` with `returns_series` schema for plot helper.

8. **Run gates + scoring** — `uv run python compute_gates_and_score.py`
   produces `verdict.json` + console summary.

9. **Generate plots** — `uv run python ../../plot_helper.py --iter 034`.

10. **Write `final_report.md`** — prose verdict honestly comparing to
    iter 015 (Δ Sharpe / CAGR / MDD per dataset) AND iter 033 (Δ
    score) + structural lesson.

11. **Update `BASE_MEMORY.md`** — bump iter, append 6-field entry,
    prune if needed (file size 18 KB ceiling), update top-K +
    promising directions.

12. **Update `DEAD_ENDS.md`** — add structural finding only if FAIL
    or new closure (e.g., "3-leg static stack with bond duration
    spread at α=0.2" with specific kill that fired).

13. **Update `jornada/`** — write entry per CLAUDE.md Regra 1.

---

## What outcome teaches us

| outcome | interpretation | next iter direction |
|---|---|---|
| Score ≥ 90 + winner conditions met | **WINNER** — duration spread at preserved notional unlocks all 5 conditions; deployment candidate (still requires mandate §7) | shell loop halts; user decides |
| Score 80-89 STRONG, 4/5 conditions | **Top-K leader** — spread is structurally additive; investigate funding-cost-funded variant + α-sweep | iter 035: SPY+IEF+TLT funded variant + α-sweep with grid PBO |
| Score 75-79 STRONG, 3-4/5 | **Tied iter 015 plateau** — spread is duration-axis equivalent on Sharpe; possible CAGR/MDD differential | iter 035: cross-asset sleeve (FX/commodity carry) — distribution-orthogonal axis |
| Score 65-74 PROMISING | **Spread captures carry but variance penalty consumes most of it** — TLT vol at α=0.2 still cancels term-premium gain | iter 035: cross-asset VRP IWM (different asset, different premium) |
| Score 50-64 MARGINAL | **Spread is net-negative on Sharpe** — bond-axis variations on static iter 015 base entirely closed | iter 035: non-static architecture (regime-aware, ML meta-label, cross-sectional factor timing) |
| Score < 50 NEAR_FAIL/FAIL (Kill A or B fires hard) | **Structural failure** — bond carry sleeve at any α on static stack is dead-end | iter 035: drop bond-axis entirely; pursue FX carry overlay (Lustig-Verdelhan 2007) or equity-index VRP IWM |

The most informative outcomes are scores in the 70-79 range — they
tell us whether the spread axis is *equivalent* to iter 015 (closing
all bond-axis variations) or *additive* (opening funded/sweep
variants). A score >85 would be the biggest finding of the loop to
date and the first STRONG above iter 016/018/021's 79 ceiling. A
score <60 would close the bond-axis variation family entirely and
point definitively to non-bond mechanisms.
