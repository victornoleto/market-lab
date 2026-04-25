# Iteration 059 — HYG long-only with 90d boolean trend filter as 3rd stream on iter 037 (w=0.10)

## Hypothesis

iter 058 (🥇 STRONG, 85/100, TOP-K #1 tied with iter 046) confirmed
constructively that a higher-Sharpe credit-carry 3rd stream (HYG_TSM,
standalone Sharpe ≈ 0.87-0.99) added at w=0.10 to a static-stack base
is a Pareto improvement on Sharpe + MDD axes. The **only** strict-
winner gap on iter 058 was **CAGR floor 0/15** because iter 046's
own standalone CAGR (~9.5%) is below the 0.8 × benchmark floor on
all 3 datasets, and adding HYG_TSM (CAGR ~5%) at any positive weight
strictly worsens combined CAGR.

This iteration substitutes the **anchor**: pair HYG_TSM at w=0.10
with **iter 037** (`ntsx_3leg_preserved_60_45_45_spy_ief_gld`,
3-leg 1.5×-leverage SPY+IEF+GLD) instead of iter 046. Iter 037's
standalone CAGR is **14.16% / 15.53% / 17.76%** on edu/spy/ndx —
**4.7-7.0 pp above** iter 046's 9.07/9.45/9.76% — and clears the
0.8×-bench CAGR floor on all 3 datasets even if combined CAGR drops
0.5-1.0 pp from HYG drag.

The mechanism is structurally identical to iter 058:

```
pos_HYG[t] = 1 if (HYG[t-1] / HYG[t-1-90] - 1) > 0 else 0
r_HYG_TSM[t] = pos_HYG[t] * r_HYG[t] + (1 - pos_HYG[t]) * rf_d
              − cost_bps × |Δpos_HYG[t]|

r_combined[t] = w_037 * r_037[t] + w_HYG * r_HYG_TSM[t]
```

with `w_037 = 0.90, w_HYG = 0.10` — single pre-committed config,
identical weight to iter 058 for direct anchor-substitution
comparison. The HYG_TSM engine is **vendored verbatim** from iter
058 (no re-implementation; G7 already passed at 0.0000 pp). The
iter 037 stream is **loaded from its saved `returns_series`** in
`iterations/037-*/results.json` (no re-implementation).

The thesis: replacing iter 046 with iter 037 trades **0.10-0.20 Sharpe
down** (iter 037 standalone S=0.98/1.15/1.17 vs iter 046's
1.20/1.32/1.38) for **+5-7 pp CAGR** (iter 037's higher equity weight
at preserved 1.5× lev). Sharpe-edge criterion 1 may drop from 25/25 to
15-25/25; gates criterion 2 from 25/25 to 17-25/25; DSR criterion 3
from 15/15 to 0-15/15 (iter 037's standalone DSR worst-p was 0.222 vs
iter 046's 0.042); but **CAGR floor criterion 4 jumps from 0/15 to
15/15**, MDD ceiling stays 15/15 (iter 037 cleared all 3, +5pp slack).

Expected score: 80-88 frozen. **Path to WINNER (≥ 90 frozen + 5/5
strict)** if HYG_TSM lifts iter 037's Sharpe enough to push DSR
worst-p < 0.05 across all 3 datasets — a credible outcome because
iter 037's worst-p was 0.222 with Sharpe 0.98 on edu, and the
Markowitz-predicted lift (HYG_TSM standalone S~0.87) at w=0.10
should add ~+0.03-0.05 to combined Sharpe, pushing combined edu
Sharpe to ~1.01-1.03. Whether that is enough to clear DSR p < 0.05
with `cumulative_n_trials = 4329` is the empirical question this
iteration tests.

## Primary citation

`[risk_parity, ch.5]` + Asvanunt-Richardson 2017 JPM 43(2)
DOI 10.3905/jpm.2017.43.2.090 — Asness-Frazzini-Pedersen 2012 risk-
parity multi-leg decomposition (iter 037 anchor) combined with
Asvanunt-Richardson's quantification of credit risk premium
(~2-4% net of defaults). The chapter's analysis of variance
contribution at preserved total leverage justifies the 0.10
diversifier weight; A-R §3 (p.97-99) justifies the 90d trend filter
for stress avoidance.

## Additional citations

- `[risk_parity, p.5, p.10-11, ch.1]` — Asness-Frazzini-Pedersen 2012,
  *FAJ* 68(1) 47-59, SSRN 1728082. Static-stack mechanism (iter 037
  base architecture preserved verbatim via saved stream).
- `[risk_parity, p.80-84]` — funding-cost framework (iter 037 inherits
  iter 015's 1.5× leverage budget, identical drag).
- `[leverage_for_the_long_run, p.19-20]` — Hsiao & Williams 2017,
  *J. Index Investing*. 1.5× is optimal-leverage zone for a 3-asset
  base (iter 037 anchor).
- `[systematic_trading]` (Carver) — generic TSM single-asset boolean
  trend rule, applied to credit (HYG_TSM engine vendored from iter 058).
- `[stocks_on_the_move, p.76-77]` (Clenow) — boolean trend on log price.
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (4328 → 4329).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (numpy ref).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- Markowitz (1952), JoF 7(1) 77-91 — convex combination Sharpe
  identity (kill D).
- Web: Asvanunt, A. & Richardson, S. 2017, "The Credit Risk Premium",
  JPM 43(2), https://doi.org/10.3905/jpm.2017.43.2.090.
- Web: Asness, C., Moskowitz, T. & Pedersen, L. 2013, "Value and
  Momentum Everywhere", JoF 68(3) 929-985, DOI 10.1111/jofi.12021 —
  credit TSM positive Sharpe in 2007-2026 (Table III).
- Web: Moskowitz, Ooi & Pedersen 2012, JFE 104(2) 228-250,
  DOI 10.1016/j.jfineco.2011.11.003 — TSM canonical reference.

## Edge source

SPY 1x buy-hold misses **two structurally-positive return sources**
that this iteration combines orthogonally:

1. **Risk-parity premium across SPY/IEF/GLD at preserved 1.5× lev**
   — iter 037's 3-leg static stack delivers Sharpe 0.98-1.17 with
   CAGR 14-18% and MDD ≤ 33%, dominating SPY 1x by +0.20-0.30 Sharpe
   and −2 to −22 pp MDD. The diversifier-sleeve variance reduction
   (ρ_bd_gld ≈ +0.21-0.28) is the structural Sharpe lever.
2. **Credit risk premium net of defaults (HYG)** — Asvanunt-
   Richardson 2017 quantifies a 2-4%/yr structural premium with a
   trend filter for stress avoidance; iter 058 confirmed standalone
   Sharpe 0.87-0.99 and CAGR 4.75-5.08% net of cost on 2007-2026
   real data, with corr ≈ 0.40-0.48 vs iter 046.

The expected combined edge over SPY 1x: Sharpe **+0.20-0.35** on each
dataset, CAGR **−1 to +3 pp** (vs SPY's 11.5/15.0/19.2%), MDD
**−3 to −22 pp** (vs SPY's 55/34/35%). The path to WINNER hinges on
DSR — whether the additional ~+0.03-0.05 Sharpe from HYG_TSM on top
of iter 037's 0.98-1.17 baseline pushes deflated p across 0.05.

## Datasets

- educational (SPYSIM synth 40y, **windowed**): iter 037's stream
  spans 2006-01-04 → 2026-04-15 (5101 bars). HYG starts 2007-04-12 in
  Tiingo, so the inner-join effective educational window is
  ~2007-04 → 2026-04 (~19y, ~4787 bars — same as iter 058's edu).
  The educational benchmark is recomputed on this windowed range
  (custom benchmark for HYG-aligned comparison; frozen 1986-2026
  benchmark used for tier determination per `scoring.py`).
- spy_real (2009-06-25 → 2026-04-15): post-GFC SPY-anchored test;
  HYG full coverage. iter 037 stream spans 4226 bars; combined ~4226.
- ndx_real (2010-02-12 → 2026-04-15): post-GFC QQQ-anchored test;
  HYG full coverage. iter 037 stream spans 4066 bars; combined ~4066.

All 3 datasets use the same pre-committed cfg
`iter037_plus_hyg_tsm_w010_lookback90`.

## Kill criteria (pre-committed)

If any of the following observable patterns holds at end of Stage 4,
the hypothesis is falsified regardless of secondary metrics:

| # | Kill | Threshold | Rationale |
|---|---|---|---|
| A | Combined Sharpe regress vs iter 037 | Drop ≥ 0.10 on ≥ 2 of 3 datasets | Mirrors iter 058 kill A; large drag falsifies "HYG_TSM as Pareto-positive 3rd stream" |
| B | DSR worst-p ≥ iter 037's 0.222 | worst p ≥ 0.222 across 3 datasets | If adding HYG_TSM doesn't even improve DSR vs the bare anchor, the higher-Sharpe-3rd-stream thesis fails on this anchor |
| C | Score < iter 037's 79 (anchor baseline) | total_score < 79 | If the iter 037+HYG combo can't beat iter 037 alone, the 3rd-stream addition is a regression |
| D | Markowitz formula mispredicts observed combined Sharpe | abs residual ≥ 0.05 on ≥ 2 datasets | Closes the closed-form composition pattern (mirrors iter 058 D) |
| E | G7 cross-lib > 3 pp | abs CAGR diff > 3 pp on any dataset | Engine bug in HYG_TSM or combine logic (HYG_TSM engine already validated 0.0000 pp on iter 058; this kill protects against regression in the iter-037 stream loader) |
| F | corr(r_HYG_TSM, r_037) > 0.85 | average corr across 3 datasets > 0.85 | HYG behaves as equity proxy on this anchor; no real diversification |
| G | CAGR floor regress vs iter 037 | combined CAGR < 0.8×bench on ≥ 2 datasets | The iter 037 anchor's main appeal is its CAGR; if HYG drag pushes ≥ 2 datasets below the floor, the anchor advantage evaporates |

**Falsification threshold**: ≥ 4/7 kills fired = hypothesis refuted
(matching iter 058's standard scaled to 7 kills).

## Expected budget

- Configs to test: **1** (pre-committed, no grid)
- cumulative_n_trials advance: 4328 → **4329** (+1)
- Wall-time: ~5-10 minutes (HYG TSM is one numpy loop, iter 037
  stream is loaded from saved JSON, scoring is the existing helper)
- Files to create:
  - `hyg_tsm.py` — vendored verbatim from iter 058 (re-imported via
    file copy for self-containment; G7 parity preserved)
  - `numpy_reference_iter059.py` — vendored verbatim from iter 058's
    `numpy_reference_iter058.py` (renamed for clarity)
  - `combined_037_plus_hyg.py` — convex combination wrapper
    (analog of `combine_046_plus_hyg`)
  - `tests/test_iter_059_iter037_plus_hyg.py` — TDD specs (≥ 12
    tests covering indexing, no-lookahead, warmup, cost, weighting,
    G7 parity)
  - `run_backtests.py` — runs the 3 datasets, writes `results.json`
  - `compute_gates_and_score.py` — 7-gate battery + score, writes
    `verdict.json`
  - `final_report.md` — Stage 5 narrative

## Implementation plan

1. **TDD**: write `tests/test_iter_059_iter037_plus_hyg.py` mirroring
   `iter058/tests/test_iter_058_hyg_tsm.py` with appropriate
   anchor-substitution. Confirm failure before writing impl.
2. **Vendor HYG_TSM engine**: copy `hyg_tsm.py` and
   `numpy_reference_iter058.py` from iter 058 (or import from there
   if path layout permits) — preserves G7 0.0000 pp invariant.
3. **Combiner**: `combined_037_plus_hyg.py::combine_037_plus_hyg(r_037, r_hyg, *, w_037, w_hyg)`
   — convex combo (analog of `combine_046_plus_hyg`).
4. **Run all tests** — should be 12+ tests, all passing.
5. **Run backtests**: `run_backtests.py` over 3 datasets, write
   `results.json` with required `returns_series` schema. Loads iter
   037 saved stream from `iterations/037-*/results.json`.
6. **Compute gates + score**: copy `compute_gates_and_score.py` from
   iter 058, swap iter 046→037 and iter 050→046 reference points,
   recompute against fresh data, write `verdict.json` with the 7
   pre-committed kills evaluated.
7. **Plots**: `uv run python studies/strategy_hunt_loop/plot_helper.py --iter 059`.
8. **Final report + memory update + auto-prune**.
