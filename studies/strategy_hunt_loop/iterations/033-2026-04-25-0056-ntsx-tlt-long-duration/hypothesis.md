# Iteration 033 — NTSX long-duration variant: 0.9 SPY + 0.6 TLT static stack

**Date:** 2026-04-25 00:56
**Slug:** `ntsx-tlt-long-duration`
**Cumulative n_trials before iter 033:** 4285

---

## Hypothesis

Test the **simplest possible structural extension of iter 015 NTSX**:
swap the bond leg from IEF (7-10y, ~6y duration) to **TLT (20-30y,
~17-18y duration)** while keeping equity weight, leverage, and
"static, no timing" discipline identical to iter 015.

```
iter 015 cfg: 0.9 × SPY + 0.6 × IEF   (total leverage 1.5×)
iter 033 cfg: 0.9 × SPY + 0.6 × TLT   (total leverage 1.5×)
```

Per iter 032's headline lesson, future winners need a CAGR mechanism
that is **distribution-orthogonal to equity beta on stress days**
(NOT a short-vol overlay that amplifies equity drawdowns). Bond
duration returns track yield-curve shifts (slow, persistent,
macro-driven) rather than equity-vol spikes (fast, beta-driven). The
long end of the curve is where the **term premium** is largest — the
canonical "carry" return-predictor in cross-asset literature
[Koijen-Moskowitz-Pedersen-Vrugt 2018; Ilmanen 2011 ch.6-7].

The hypothesis is that TLT's larger term premium harvest unlocks
**criterion 4 (CAGR floor 0/15 → potentially 15/15)** which iter 015
nearly cleared (Sharpe edge 4/5 winner conditions, capped at 77 by
CAGR floor on educational), without re-introducing the DSR collapse
seen on iter 032 (because no short-vol overlay is added — the
duration tilt's realized higher moments are much milder than
short-vol writers'). The trade-off: 2022 was uniquely punishing for
TLT (-31% peak-to-trough) and may breach the MDD ceiling on ndx_real.

This is **mechanism-change vs iter 015** (different bond ticker =
different duration regime = different carry premium magnitude),
**not** a parameter sweep on iter 015. The 90/60 weights are
preserved verbatim from NTSX prospectus.

---

## Primary citation

`[risk_parity, p.5, p.10-11, ch.1]` — Asness-Frazzini-Pedersen
(2012) risk-parity argument: levering up the diversified portfolio
captures more diversification per unit of total risk than leaving it
unlevered. Static stacking is the simplest empirical instantiation,
and **the choice of bond duration determines how much of the term
premium the levered base actually harvests** (longer duration =
larger expected term premium per unit notional, per Cochrane-Piazzesi
2005 + Ilmanen 2011).

## Additional citations

- `[risk_parity, ch.5]` — bond term-premium decomposition for the
  diversifying leg of a levered stack.
- `[leverage_for_the_long_run, p.19-20]` — leverage on a diversified
  base captures duration risk-premium without market-timing.
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials.
- Asness, Frazzini & Pedersen (2012). "Leverage Aversion and Risk
  Parity." *Financial Analysts Journal* 68(1): 47-59. SSRN
  [1728082](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1728082).
- **Koijen, Moskowitz, Pedersen & Vrugt (2018). "Carry."** *Journal
  of Financial Economics* 127(2): 197-225. DOI:
  [10.1016/j.jfineco.2017.11.002](https://doi.org/10.1016/j.jfineco.2017.11.002).
  Establishes carry as a robust return-predictor across bonds, FX,
  commodities, and equities. For US Treasury bonds, the carry
  premium is largest at the 20-30y duration band (TLT), declining
  with shorter duration.
- **Cochrane & Piazzesi (2005). "Bond Risk Premia."** *American
  Economic Review* 95(1): 138-160. DOI:
  [10.1257/0002828053828581](https://doi.org/10.1257/0002828053828581).
  Term-structure factor predicts bond excess returns over cash.
- **Ilmanen (2011). *Expected Returns: An Investor's Guide to
  Harvesting Market Rewards.*** Wiley. Chapter 6-7 on term premium
  and bond carry as a primary expected-return source.
- WisdomTree NTSX prospectus — 90 % equity + 60 % UST futures
  weights (manufacturer-prescribed, preserved verbatim from iter 015).

## Edge source

In ONE sentence: **iter 015 NTSX 0.9 SPY + 0.6 IEF stacks 7-10y bond
exposure on top of equity but leaves the steepest term-premium harvest
(20-30y TLT) untouched; iter 033 swaps IEF → TLT to capture the
larger term premium at the long end of the yield curve, providing a
CAGR boost via duration-orthogonal mechanism (yield-curve shifts vs
equity-vol spikes) without adding a short-vol overlay that would
re-introduce iter 032's DSR-collapse pathology.**

---

## Why this is structurally different from prior iterations

| iteration | bond leg | mechanism | iter 033 vs |
|---|---|---|---|
| **iter 015** | IEF static | static stacking | **same mechanism, different duration** ← novelty axis |
| iter 016 | TLT in vol-managed blend | dynamic vol-target | iter 033 is STATIC — no Moreira-Muir scaling, no σ²_port feedback |
| iter 018 | IEF static + funding cost | iter 015 + r_Tbill drag | iter 033 keeps iter 015's funding-cost simplification |
| iter 020/021 | iter 016 + put-spread | vol-managed + short-vol overlay | iter 033 has NO overlay, NO put-spreads |
| iter 024 | TLT or SHV (timing) | T10Y3M-allocated bond mix | iter 033 has NO timing — pure static TLT |
| iter 027 | T-bill + put-spread, levered | T-bill collateral | iter 033 has actual long-duration bond, not T-bill |
| iter 032 | NTSX + put-spread overlay | iter 015 base + iter 031 VRP | iter 033 has NO put-spread overlay (DSR-orthogonal) |

The structurally novel axis: **bond duration choice on a static
return-stack with no timing/overlay layer**. iter 015 used IEF (~6y
duration); iter 033 uses TLT (~17-18y duration). All other
parameters preserved verbatim.

DEAD_ENDS check: no entry forbids long-duration bond on a static
stack. Iter 016 used TLT inside a *vol-managed* blend (different
mechanism); iter 024 used TLT inside a *T10Y3M-timed* allocation
(different mechanism). Pure static SPY+TLT stack at fixed 0.9/0.6
weights has not been tested.

---

## Datasets

| dataset | window | universe | rationale |
|---|---|---|---|
| educational | 2002-07-26 → 2026-04-15 | SPY + TLT | TLT-inception-aligned (~24y; 4y longer than iter 015's IEF window) |
| spy_real | 2009-06-25 → 2026-04-15 | SPY + TLT | 17y post-GFC, full benchmark window |
| ndx_real | 2010-02-12 → 2026-04-15 | QQQ + TLT | 16y tech-heavy |

Educational benchmark is **re-measured on the TLT-aligned window**
(matches iter 015/024's `build_custom_benchmarks` pattern). spy_real
and ndx_real benchmarks remain frozen to `scoring.BENCHMARKS`. The
canonical winner check uses **FROZEN** benchmarks per
WINNER_AND_RANKING.md.

---

## Pre-committed single config

| param | value | rationale / citation |
|---|---|---|
| `cfg_id` | `ntsx_synth_90_60_spy_tlt` | descriptive |
| `equity_symbol` | SPY (edu, spy_real), QQQ (ndx_real) | matches iter 015 |
| `bond_symbol` | **TLT** | NEW — iShares 20+ Year Treasury Bond ETF |
| `equity_weight` | 0.90 | NTSX prospectus exact (verbatim from iter 015) |
| `bond_weight` | 0.60 | NTSX prospectus exact (verbatim from iter 015) |
| `total_leverage` | 1.50 | sum of legs |
| `rebalance` | daily | maintain fixed weights |
| `cost_bps_per_leg` | 0.0002 | 2 bps per unit per-leg ∆position (iter 015 cost model) |
| `funding_cost` | NOT modeled | iter 015 simplification preserved; iter 018-style funded variant deferred |

**Why a single config (no grid)**: NTSX has prescribed weights baked
into the product (90/60 is the manufacturer's choice — same as iter
015). The novelty is purely in the bond ticker swap. NO PBO concern
beyond cumulative_n_trials accounting (3 trials added: 1 cfg × 3
datasets). Mirror of iter 015's single-cfg discipline.

**Funding-cost simplification**: real NTSX-equivalent on TLT would
pay ~0.5 × short-rate as implicit financing on the 50% additional
notional. Synthetic version ignores this for cleanliness, which
**OVERESTIMATES** the strategy's edge by an estimated 50-100 bps
annually depending on regime (same magnitude as iter 015). A
sensitivity comment in the final report will quantify the impact,
mirroring iter 015 → iter 018's funded-replay convention.

---

## Kill criteria (pre-committed; binary, observable post-Stage-3)

If any of these triggers, the iteration is falsified independent of
secondary metrics:

| kill | criterion | rationale |
|---|---|---|
| **A** | Sharpe Δ vs iter 015 frozen reference (edu ~0.83 / spy ~1.04 / ndx ~1.16) < 0 on ≥ 2/3 datasets | **TLT swap doesn't add Sharpe** — extra duration vol cancels carry premium gain; iter 015's IEF was already Sharpe-optimal |
| **B** | ndx MDD > 50 % | **Duration drawdown too painful** — 2022 dual rate-spike-+-tech-selloff produces unacceptable composite drawdown |
| **C** | DSR worst-p > 0.20 | **Distribution unacceptable** — even without overlay, duration's left tail is too heavy |
| **D** | G7 cross-lib diff > 3 pp CAGR | **Engine bug** (would invalidate all metrics) |
| **E** | Total score < 60 | **Below PROMISING** — iter 015 achieved 77, so a TLT swap that scores < 60 is a strict regression |
| **F** | Robustness < 7/9 sub-windows positive | **Strategy has a regime where it systematically loses** (defensive — bond-duration-positive periods may be too narrow) |

Pre-commitment note: Kill A's threshold is **Sharpe < iter 015** (not
"< iter 015 − 0.05") because iter 015 is the direct mechanism-comparison
benchmark; if TLT doesn't beat IEF on Sharpe, the bond duration
choice is the wrong axis to pull. Kill B's 50% threshold is generous
vs iter 032's 40% (which was the +5pp ceiling on ndx) because we
already know 2022 will be punishing — the question is whether it's
*absorbable* (~45-50%, recoverable) vs *catastrophic* (>50%).

Crucially: **score < 80 is NOT an automatic kill** for this
iteration — the value is in establishing whether duration swap on a
static stack is structurally additive (vs iter 015's 77 plateau) or
neutral (vs iter 032's 72 PROMISING ceiling on layered composition).
A score of 75-79 STRONG that cleanly characterises the duration-tilt
axis is more informative than a forced higher score via parameter
tweaking.

---

## Expected budget

- Configs to test: **1** (single pre-committed cfg, mirrors iter 015)
- Datasets: 3 → **3 cumulative n_trials added** (4285 → 4288)
- Wall-time estimate: **30-45 min total**
  - Implementation: ~5 min (literally swap "IEF"→"TLT" in iter 015's
    `run_backtests.py` + adjust dates; reuse `synth_stacked_etf.py`
    + `numpy_reference_stacked.py` directly)
  - TDD specs: ~5 min (lock TLT-data-loader semantics + bond-symbol
    propagation; reuse iter 015's stacking-math specs unchanged)
  - Run + gates: ~5 min (no lookback dependencies)
  - Final report + BASE_MEMORY update + plots: ~15-25 min

- Files to create:
  - `run_backtests.py` — adapted from iter 015 (bond_symbol=TLT, edu start=2002-07-26)
  - `compute_gates_and_score.py` — adapted from iter 015 (cumulative_n_trials, iter-015 reference metrics for Δ comparison)
  - `tests/test_iter033_ntsx_tlt.py` — TDD specs (≥ 4 specs covering: TLT data load, bond-symbol propagation, no parameter inflation, cross-lib parity at iter 033 cfg)
  - `results.json` + `verdict.json` — outputs
  - `final_report.md` — prose verdict
  - `plot_vs_benchmark_spy_real.png` + `plot_vs_benchmark_ndx_real.png`

- Files to **REUSE directly from iter 015** (no copy needed):
  - `synth_stacked_etf.py::apply_static_stack` — generic 2-leg stacker
  - `numpy_reference_stacked.py::apply_static_stack_np` + `cagr_np` — G7 reference

---

## Implementation plan

1. **Write TDD specs** (`tests/test_iter033_ntsx_tlt.py`) — ≥ 4 specs:
   - `test_iter033_loads_tlt_for_all_datasets` — iter 033's `run_backtests.py` loads TLT (not IEF) for educational/spy_real/ndx_real
   - `test_iter033_edu_window_starts_2002_07_26` — TLT-inception alignment (4y longer than iter 015's IEF-aligned 2006)
   - `test_iter033_uses_iter015_stacking_engine` — confirms iter 033 imports `apply_static_stack` from iter 015 (no re-implementation)
   - `test_iter033_cross_lib_parity_under_5_pp_smoke` — smoke test on synth data (≤5pp tolerance, real test in G7 ≤3pp)

2. **Implement `run_backtests.py`** — adapt iter 015's verbatim, change:
   - `DATASETS["educational"]["bond_symbol"] = "TLT"`, `start = "2002-07-26"`
   - `DATASETS["spy_real"]["bond_symbol"] = "TLT"`
   - `DATASETS["ndx_real"]["bond_symbol"] = "TLT"`
   - `CFG["cfg_id"] = "ntsx_synth_90_60_spy_tlt"`
   - Import `apply_static_stack` from `iterations/015-2026-04-24-1704-return-stacked-static-ntsx/synth_stacked_etf.py`

3. **Implement `compute_gates_and_score.py`** — adapt iter 015's
   verbatim, change:
   - `CUMULATIVE_N_TRIALS = 4285 + 1 * 3` (=4288)
   - `iter015_reference_metrics` dict (read from iter 015's `results.json`)
   - Reference deltas updated for `delta_vs_iter015` block
   - Import `apply_static_stack_np` + `cagr_np` from iter 015's
     `numpy_reference_stacked.py`
   - `verdict["primary_citation"]` updated to mention KMPV 2018 + TLT

4. **Run pytest** — confirm new specs pass + baseline unchanged
   (current baseline ~793 collected post-iter-032; iter 033 adds ~4-5
   specs).

5. **Run backtests** — `uv run python run_backtests.py` produces
   `results.json`.

6. **Run gates + scoring** — `uv run python compute_gates_and_score.py`
   produces `verdict.json` + console summary.

7. **Generate plots** — `uv run python plot_helper.py --iter 033`.

8. **Write `final_report.md`** — prose verdict honestly comparing to
   iter 015 (+ Δ Sharpe / CAGR / MDD per dataset) + iter 032 (+ Δ
   score with respect to layered composition) + structural lesson.

9. **Update `BASE_MEMORY.md`** — bump iter, append entry, prune if
   needed (file size 18 KB ceiling), update top-K + promising
   directions.

10. **Update `DEAD_ENDS.md`** — add structural finding only if FAIL
    or new closure (e.g., "TLT static stack at 0.6 weight" with
    specific kill that fired).

11. **Update `jornada/`** — write entry per CLAUDE.md Regra 1.

---

## What outcome teaches us

| outcome | interpretation | next iter direction |
|---|---|---|
| Score ≥ 90 + winner conditions met | **WINNER** — TLT duration tilt unlocks all 5 conditions; deployment candidate (still requires mandate §7) | shell loop halts; user decides |
| Score 80-89 STRONG, 4/5 conditions | **Top-K leader** — TLT swap improves on iter 015 plateau; investigate funding-cost-funded variant (iter 018 analog) | iter 034: SPY+TLT funded variant (subtract r_Tbill) |
| Score 75-79 STRONG, 3-4/5 | **Tied iter 015 plateau** — TLT swap is duration-axis equivalent to IEF on Sharpe, with possible CAGR/MDD trade-off | iter 034: bond-mix sweep (e.g., 0.3 IEF + 0.3 TLT) |
| Score 65-74 PROMISING | **CAGR up, but MDD or DSR offset** — duration tilt buys CAGR at cost of higher MDD on ndx (2022) | iter 034: lower TLT weight (0.4 instead of 0.6) or duration-targeting overlay |
| Score 50-64 MARGINAL | **TLT vol cost > carry premium** — duration swap is net-negative; iter 015's IEF was Sharpe-optimal | iter 034: cross-asset carry (FX/commodity); close TLT swap path |
| Score < 50 NEAR_FAIL/FAIL (Kill A or B fires hard) | **Structural failure** — duration risk dominates carry premium on test windows; close static-TLT-stack path | iter 034: bond carry SLEEVE (zero-net-notional spread) instead of full duration swap |

The most informative outcomes are scores in the 70-79 range —
they tell us whether the duration axis is *equivalent* to iter 015
(implying we need a different lever entirely) or *additive* (implying
we should pursue funded/sweep variants). A score >85 would be the
biggest finding of the loop to date; a score <60 would close the
"static stack with longer-duration bond" path entirely.
