# Iteration 061 — Equity-overweight iter 037 (0.75/0.40/0.40) + HYG_TSM at w=0.10

## Hypothesis

Re-weight iter 037's 3-leg static return-stack from its canonical
**0.60 SPY + 0.45 IEF + 0.45 GLD** (1.50× total notional) to an
**equity-overweight 0.75 SPY + 0.40 IEF + 0.40 GLD** (1.55× total
notional), then combine the resulting stream with HYG_TSM at w=0.10
(reusing the iter 058/059 vendored engine).

The mechanism: iter 037's standalone Sharpe (0.96-1.17 across the 3
datasets) is the binding ceiling that pinned iter 059 at score 79
despite its CAGR-floor advantage (15/15) over iter 058. Boosting
equity weight by +0.15 (0.60 → 0.75) raises the dominant-factor
exposure (SPY post-2009 Sharpe ~0.90 standalone) while trimming
bond/gold (0.45 → 0.40 each, total 0.90 → 0.80) sacrifices only
~0.5-1.0 pp CAGR (still well above floors) and ~0.05-0.10 Sharpe
of diversification benefit. Net target: standalone Sharpe 1.05-1.20.
Adding HYG_TSM at w=0.10 then layers iter 058's vindicated +0.02
Sharpe lift and 2-3 pp MDD relief on top. Combined target: Sharpe
1.10-1.25, CAGR 12-16%, DSR worst-p 0.10-0.18.

If the hypothesis holds, this **breaks the saved-stream-pair Pareto
ceiling at 85** (iter 058) by trading some of iter 037's CAGR cushion
for Sharpe headroom — the first config to plausibly clear DSR p<0.10
while keeping CAGR floor 3/3.

## Primary citation

`[risk_parity, ch.5]` Asness-Frazzini-Pedersen 2012 — multi-leg
risk-parity decomposition; the architecture allows arbitrary equity
weight up to total leverage cap, with the trade-off between equity
beta and diversification governed by the bond/gold weights. The
0.75/0.40/0.40 allocation is within the AFP "preserved-leverage"
zone (1.50-1.60× total) and within Hsiao-Williams 2017's NTSX-style
range.

## Additional citations

- `[risk_parity, p.5, p.10-11, ch.1]` — AFP 2012 SSRN 1728082,
  static-stack mechanism and equity-vs-diversifier weight trade-off.
- `[leverage_for_the_long_run, p.19-20]` Hsiao & Williams 2017,
  *J. Index Investing* — preserved-leverage zone (1.5-1.6× total)
  for diversified base; SPY-tilt up to 0.75 within optimal range.
- `[stocks_on_the_move, p.76-77]` Clenow — boolean trend on log price
  (HYG_TSM signal mechanism, vendored verbatim from iter 058/059).
- `[systematic_trading]` Carver — single-asset TSM rule (HYG_TSM).
- Asvanunt, A. & Richardson, S. 2017, "The Credit Risk Premium",
  JPM 43(2), DOI 10.3905/jpm.2017.43.2.090 — credit risk premium
  thesis underpinning HYG carry harvest after trend filter.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (4331 after this iteration).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline
  (linear convex combination → 0.0000 pp expected, same as iter 058/059/060).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- Markowitz (1952), JoF 7(1) 77-91 — closed-form Sharpe identity
  for convex combination (residual = 0.0000 expected).
- Erb, C.B. & Harvey, C.R. 2006, "The Strategic and Tactical Value
  of Commodity Futures", FAJ 62(2) 69-97 — gold strategic role
  (preserved through iter 037 anchor architecture).
- Koijen, Moskowitz, Pedersen, Vrugt 2018, "Carry", JFE 127(2)
  197-225 — gold spot-forward basis ≈ 0; bond term-premium
  decomposition.

## Edge source

What SPY 1× misses: SPY's standalone Sharpe ~0.90 post-2009 leaves
the DSR-cleaning bar (Sharpe ≥ 1.20) out of reach for any pure SPY
construction. Iter 037's diversification (bond/gold) reduced
volatility but at the cost of also reducing mean return — keeping
combined Sharpe ~1.0. **The proposed equity overweight (0.75 vs
0.60) shifts the variance-mean trade-off back toward higher mean
without giving up all the diversification benefit** (still 0.80
total bond+gold notional, vs iter 037's 0.90, vs pure SPY's 0.00),
plus the HYG_TSM stream injects a moderately uncorrelated (~0.40-0.45
ρ per iter 059) credit-carry edge that compounds via Markowitz to
~+0.02 Sharpe and ~2-3 pp MDD relief.

## Datasets

- **educational** (SPYSIM synth → SPY+IEF+GLD 21y, GLD-aligned start
  2004-11-19): tests pre-GFC + GFC + post-GFC regimes; HYG inner-join
  shortens to 2007-04+ (same windowing artefact as iter 059).
- **spy_real** (SPY+IEF+GLD 17y post-GFC, 2009-06-25 → 2026-04-15):
  the hardest benchmark (SPY post-GFC Sharpe 0.90, near top quartile
  of historical regimes); equity overweight tested against the
  toughest comparator.
- **ndx_real** (QQQ+IEF+GLD 16y, 2010-02-12 → 2026-04-15): tech-tilt
  variant; tests whether the equity-overweight thesis transports to
  a higher-beta universe (QQQ Sharpe 0.955 baseline).

## Kill criteria (pre-committed, 6 kills)

If ≥ 4 of 6 fire → hypothesis substantially falsified.

| # | Kill | Rationale |
|---|---|---|
| **A** | Combined Sharpe regress vs iter 037 by ≥ 0.10 on ≥ 2 datasets | Equity-overweight failed to lift Sharpe; iter 037 anchor architecture is Sharpe-optimal at 0.60 SPY |
| **B** | DSR worst-p ≥ 0.222 (no improvement vs iter 037 baseline) | The Pareto path is closed; equity overweight + HYG add nothing new vs the iter 037 anchor |
| **C** | Score < 79 (regression vs iter 037 standalone) | The combination is Pareto-dominated by bare iter 037 |
| **D** | G7 cross-lib > 3pp on any dataset | Engine bug; the linear transform should be exact (0.0000 pp expected) |
| **E** | MDD breach > bench+5pp on ≥ 2 datasets (i.e., MDD > 60.14 / 38.70 / 40.12% on ≥ 2 ds) | Equity overweight broke risk control beyond the project's gate ceiling |
| **F** | CAGR floor regress on ≥ 2 datasets (combined CAGR < 0.8×bench: 9.18 / 11.98 / 15.35% on ≥ 2 ds) | Bond/gold trim + HYG drag broke iter 037's CAGR-clearing branch |

**Kill F is the headline differentiator** — iter 060 closed external
leverage on iter 058 because CAGR floor remained 1/3-2/3 even with
+1.5× lev. Iter 061's prediction is that anchor-side equity
overweighting preserves CAGR floor 3/3 (because iter 037's anchor
already has +30-50% CAGR cushion vs floors) AND lifts Sharpe.

## Expected budget

- **Configs to test**: 1 (single pre-committed cfg, no grid sweep).
  cumulative_n_trials advance: 4330 → **4331** (+1).
- **Wall-time**: ~2-3 minutes (matches iter 058/059 wall-time;
  same engine, same datasets, same gates).
- **Files to create**:
  - `synth_stacked_etf_3leg_eq075.py` — vendored verbatim from iter 037
    (same `apply_static_stack_3leg` function, just called with new weights)
  - `hyg_tsm.py` — vendored verbatim from iter 059
  - `numpy_reference_iter061.py` — vendored verbatim from iter 059
  - `combined_eq075_plus_hyg.py` — convex combiner (vendored from iter 059)
  - `run_backtests.py` — main runner, builds eq075 stream + HYG TSM + combines
  - `compute_gates_and_score.py` — 7-gate battery + scoring + 6-kill eval
  - `tests/test_iter061.py` — TDD for the new weight choice + 2-stream
    combo (15+ tests; baseline pytest must stay green)
  - `results.json`, `verdict.json`, `final_report.md` — outputs
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
    (mandatory per Stage 5)

## Implementation plan

1. **Vendor** `apply_static_stack_3leg` from iter 037 (verbatim, no
   modifications — just call with eq_w=0.75, bd_short_w=0.40,
   bd_long_w=0.40 instead of iter 037's 0.60/0.45/0.45).
2. **Vendor** `compute_hyg_tsm_returns` + numpy reference from iter 059
   (verbatim; same lookback=90, rf=0.02, cost_bps=5.0).
3. **Build combiner** `combine_eq075_plus_hyg(r_eq075, r_hyg, w_eq075=0.9, w_hyg=0.1)`
   — same shape as iter 059's `combine_037_plus_hyg`.
4. **Run on 3 datasets** (educational/spy_real/ndx_real), each: load
   triple SPY+IEF+GLD (or QQQ+IEF+GLD) → compute eq075 stream → load
   HYG prices → compute HYG_TSM → combine → save `returns_series` per
   dataset for the top cfg.
5. **TDD**: pre-write 15+ tests covering:
   - eq075 stack reduces to expected returns under known inputs (5 tests)
   - eq075 weight raises NaN appropriately when inputs misalign (3 tests)
   - convex combiner closed-form matches Markowitz to 1e-12 (3 tests)
   - cross-lib numpy reference matches pandas to 1e-12 on HYG_TSM (2 tests)
   - dataset loading hits expected windows (2 tests)
6. **Gates**: vendored from iter 059's `compute_gates_and_score.py`
   (G1 vacuous PASS at N=1; G2 raw α=0.05 at n_trials=4331; G3-G6
   per project conventions; G7 vendored numpy ref → 0.0000 pp expected).
7. **Score**: call `score_strategy()` with metrics + gates +
   cumulative_n_trials=4331, frozen benchmarks; report custom-bench
   too (HYG-aligned edu starts 2007-04+).
8. **Kills**: pre-committed 6-kill panel evaluated post-score; report
   how many fired.
9. **Final report** + verdict.json + plots + BASE_MEMORY update +
   auto-prune if > 18 KB.
