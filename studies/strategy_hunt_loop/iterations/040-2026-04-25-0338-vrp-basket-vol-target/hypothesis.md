# Iteration 040 — Vol-target wrapper around iter 039 cross-asset VRP basket (Moreira-Muir σ⁻²-scaling on basket realized vol)

## Hypothesis

Take iter 039's pre-committed cross-asset VRP basket
(`vrp_basket_eq3_5_10_1m`: T-bill collateral + 1/3-equal short
5/10 % OTM 21-DTE put credit spreads on SPY, QQQ, IWM with
`iv_scales = (1.0, 1.10, 1.25)`) and apply the
**Moreira-Muir 2017** countercyclical variance-target sizing
discipline on the **basket overlay realized variance** rather than
on a static notional:

> r_strategy[t] = rf_daily + scale[t] · harvest_notional · (− Σᵢ wᵢ · overlayᵢ[t])
>
> where σ̂²_overlay[t-1] = realized 21-day annualised variance of the
> unscaled (-Σᵢ wᵢ · overlayᵢ) series, and
>
> scale[t] = clip( target_vol² / σ̂²_overlay[t-1], 0, max_lev )

When realized basket-overlay vol is **low** (calm regime, e.g. 2017,
2021Q1) the strategy levers up to `max_lev = 2.0×` — harvesting more
short-vol premium per unit of capital. When realized basket-overlay
vol is **high** (stress, e.g. 2008Q4, 2020Q1) `scale[t]` shrinks below
1.0 — protecting capital against the spike in short-side gamma.

This combines:

- **iter 016's MM 2017 mechanism** (vol-target × static stack → 4/5 winner-conds, score 79, the loop-record-tying STRONG ceiling), but applied to the basket overlay variance rather than the equity+bond stack;
- **iter 039's cross-asset basket** (Sharpe 1.14/1.29/**1.561** loop-record + DSR 0.075/0.061/**0.006 ndx** + 9/9 robust + G7 0.0000pp);
- **a structurally different absorption mechanism** vs iter 032 (which composed iter 015 + iter 031 VRP overlay on top of equity stack and saturated at 72 due to corr_SPY ≈ 0.97 absorbing put-spread variance into σ²_port). Here there is **no equity stack underneath** — the basket itself is the strategy, and σ²_overlay is the only variance being scaled. The σ²_port-absorption mechanism that closed iter 032 is structurally absent.

The mechanism: short-vol P&L distributions are well-known to have
**time-varying conditional variance** (Bondarenko 2014 §V; Moreira-Muir
2017 Table 4, equity-vol-managed Sharpe boost +0.20-0.30). A linear
constant-`harvest_notional` size is sub-optimal because it under-bets
in calm regimes and over-bets right before stress events. The MM
inverse-variance scaling is a **direct Sharpe lever** in any return
stream whose conditional vol is auto-correlated and predictable —
which is precisely the case for short-put-spread basket P&L (vol
clustering on VIX/VXN/RVX is well-documented).

Iter 027 (constant 3.5× leverage on iter 026) already closed the
**linear leverage path** at 74 because the rf-bonus diluted with
leverage. The MM sizing differs structurally: it is **adaptive**
(scale varies bar-to-bar with σ̂²_{t-1}), so it is NOT the same as
constant linear leverage. MM 2017 §IV proves the Sharpe-lever
property holds for any series with autocorrelated conditional
variance.

## Primary citation

`[volatility_trading, p.218]` — Sinclair (2013), *Volatility Trading*
2nd ed., Wiley, ch.7-8: cross-asset VRP harvest preserves systematic
short-vol premium while reducing idiosyncratic blow-up risk.

**+ Moreira & Muir (2017)**, *Journal of Finance* 72(4): 1611-1644.
DOI 10.1111/jofi.12513. "Volatility-Managed Portfolios" — the
canonical MM 2017 paper; Table 4 reports +0.20-0.30 Sharpe gain on
equity vol-managed; the inverse-variance scaling is structurally
applicable to ANY return stream whose conditional variance is
autocorrelated.

## Additional citations

- `[volatility_trading, ch.3, p.41, p.217]` — Sinclair (2013) — VRP
  mechanics + SPX kurtosis 21.3 + canonical short-vol-harvest rule.
- `[risk_parity, p.10-11, ch.1]` — naïve risk parity + fixed-weight
  (preserved from iter 016; vol-target is the dynamic modulator on top).
- `[risk_parity, p.80-81, ch.4]` — diversification benefit (cross-asset
  basket lowers σ_basket vs single-leg).
- `[systematic_trading, p.40, ch.2]` — Carver volatility standardisation
  primitive.
- `[systematic_trading, p.170-171, ch.11]` — Carver IDM ≤ 2.5 hard cap on
  leverage (we choose `max_lev = 2.0` ≤ IDM ≤ 2.5).
- **Bondarenko (2014)** *QJF* 4(3): 1450015. DOI 10.1142/S2010139214500153.
  "Why Are Put Options So Expensive?" — empirical SPX VRP magnitude.
- **Carr & Wu (2009)** *RFS* 22(3): 1311-1341. DOI 10.1093/rfs/hhn038.
  Variance risk premia structural foundation.
- **Driessen, Maenhout & Vilkov (2009)** *J. Finance* 64(4): 1377-1406.
  DOI 10.1111/j.1540-6261.2009.01467.x. "The Price of Correlation
  Risk: Evidence from Equity Options" — cross-sectional decomposition.
- **Bakshi & Madan (2006)** *JFE* 81(2): 471-518. DOI
  10.1016/j.jfineco.2005.10.006. Cross-asset implied-vol premia
  decomposition.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (G2).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` lag rule (no look-ahead).

## Edge source

SPY 1× buy-and-hold extracts equity-risk-premium only; the iter 039
basket extracts variance-risk-premium across three uncorrelated stress
profiles (large-cap, tech, small-cap) at constant notional. Iter 040
adds a **second axis of edge**: countercyclical sizing of the
short-vol bet against realized basket vol. This converts a portion of
iter 039's *static* variance into *predictable* variance — exactly
the MM 2017 lever — without changing the underlying mechanism. The
combination is structurally additive: iter 039's diversification
lowers σ_basket vs single-leg (constant); iter 040's vol-target
scales the *exposure* dynamically to that lower σ_basket.

## Datasets

Same 3 datasets as iter 039 (preserves direct comparability):

- **educational** (SPY/QQQ/IWM + VIX from 2006-01-03 to 2026-04-14):
  ~20y window includes 2008 GFC + 2020 COVID + 2022 rate-hike. The
  Achilles heel of iter 039 was edu DSR p=0.075 (above strict 0.05) —
  driven by 2008Q4 cluster where ρ→1 in stress. MM scaling should
  shrink exposure precisely during 2008Q4 (σ̂²_overlay spikes), so
  Kill A's expected outcome is edu DSR < 0.05 PASS.
- **spy_real** (2009-06-25 → 2026-04-14): 17y post-GFC. Iter 039
  Sharpe 1.288 already exceeded benchmark by +0.39; MM scaling
  expected to add another +0.05-0.15 by harvesting low-vol regimes
  (2017 scale → 2.0× cap).
- **ndx_real** (2010-02-12 → 2026-04-14): 16y. Iter 039 Sharpe
  **1.561** loop-record + DSR p=0.006 (loop-record). MM may improve
  CAGR (currently 6.35 %, below 0.8 × 19.18 % = 15.35 % floor) at the
  cost of the already-tight DSR. **High-risk axis.**

The same single strategy (`vrp_basket_vt_eq3_5_10_1m_t05_L21_cap20`)
runs on all 3 windows. Each dataset differs only by the window cut and
the benchmark mapped in `scoring.BENCHMARKS`. This convention matches
iter 039.

## Kill criteria (pre-committed)

If at the end of Stage 3 ANY of the following holds, this hypothesis
is falsified regardless of secondary metrics (do NOT post-hoc tune
parameters):

- **Kill A (MM-absorbs-Sharpe)**: vol-target Sharpe < iter 039 Sharpe
  by ≥ 0.10 on **≥ 2 of 3 datasets**. Indicates MM scaling absorbs
  the basket harvest into σ²-canceling artefacts (analogous to iter
  032's σ²_port absorption, but on basket-only variance).
- **Kill B (DSR-no-improvement)**: DSR worst-p > 0.10 across the 3
  datasets. The whole point of MM here is to break iter 039's edu
  DSR=0.075 ceiling; if worst-p stays > 0.10, MM did not help.
- **Kill C (MDD-blows-out)**: any dataset's MDD > 25 % (over 1.7×
  iter 039's 14.32 % educational MDD). MM scaling is supposed to
  REDUCE MDD; a blow-out means scale[t] is amplifying rather than
  damping (likely indicates wrong target_vol or lookback).
- **Kill D (G7-cross-lib)**: max abs |CAGR_pandas − CAGR_numpy| > 3 pp
  on any dataset. Numerics broken.
- **Kill E (score-regression-vs-iter-039)**: score < 76 (iter 039
  was 76). Iteration is strictly worse than the un-scaled basket.
- **Kill F (sub-window-collapse)**: < 6/9 sub-windows Sharpe > 0
  across 3 datasets × 3 sub-windows each. Robustness collapse.
- **Kill G (lookahead/sign violation)**: G7 numpy parity passes but
  tests reveal use of σ̂² at bar `t` instead of bar `t-1` in scale
  formula (lookahead bug).

If multiple kills fire, document all but classify per the most
conservative tier in scoring.

## Expected budget

- **Configs to test**: **1** (single pre-committed cfg
  `vrp_basket_vt_eq3_5_10_1m_t05_L21_cap20`); cumulative_n_trials
  advances 4304 → 4305.
- **Wall-time estimate**: ~30-60 min (3× iter 039 pricer cost +
  rolling vol — pure-numpy is dominated by BS evaluations, vol
  rolling is O(N·W) cheap). Total ~6300 bars × 3 legs.
- **Files to create**:
  1. `vrp_basket_vm.py` — pandas implementation of vol-managed
     basket on top of iter 039's `compute_vrp_basket_returns`-style
     overlay aggregation.
  2. `numpy_reference_basket_vm.py` — pure-numpy reference for G7
     parity (rolling-var on the unscaled basket overlay + scale + apply).
  3. `run_backtests.py` — single pre-committed cfg, 3 datasets,
     writes `results.json` with `returns_series` populated for plot
     helper compatibility.
  4. `compute_gates_and_score.py` — 7-gate battery + scoring +
     writes `verdict.json`.
  5. `final_report.md` + plot PNGs (auto-generated from
     `plot_helper.py --iter 040`).
  6. `tests/test_iter_040_vrp_basket_vm.py` — 5 TDD specs:
     (a) zero-target = original iter 039 basket scaled to zero
     scale; (b) max_lev → ∞ + small target_vol → unbounded scale (clamp); (c) no-lookahead identity (scale uses σ̂²_{t-1}); (d) G7 parity pandas vs numpy; (e) param domain errors raise.

## Implementation plan

1. Add `vrp_basket_vm.py` exposing
   `compute_vrp_basket_vm_returns(prices, iv_series, *, target_vol,
   lookback, max_lev, harvest_notional, weights, iv_scales, …)`. It
   reuses iter 020's `compute_put_spread_daily_returns` 3 times
   (per leg), aggregates them via `weighted_overlay = Σᵢ wᵢ overlayᵢ`,
   computes annualised rolling 21d variance of `(-harvest_notional ×
   weighted_overlay)`, shifts by 1 bar (`σ̂²_{t-1}`), produces
   `scale[t] = clip(target_vol² / σ̂²_{t-1}, 0, max_lev)`, and returns
   `rf_daily + scale[t] × (-harvest_notional × weighted_overlay[t])`.
2. Add `numpy_reference_basket_vm.py` mirroring step 1 in pure numpy
   + `math.erf` (no pandas) for G7 cross-lib parity.
3. Author `run_backtests.py` (mirrors iter 039 modulo cfg + module
   import). Persists `results.json` with the canonical
   `returns_series` schema.
4. Add 5-spec TDD file `tests/test_iter_040_vrp_basket_vm.py`. All
   pass before running the production backtest.
5. Author `compute_gates_and_score.py` (mirrors iter 039 verbatim
   modulo `CUMULATIVE_N_TRIALS = 4304 + 1 = 4305`).
6. Run `plot_helper.py --iter 040` to generate
   `plot_vs_benchmark_*.png`.
7. Author `final_report.md` honestly using `score_strategy` result;
   do NOT post-hoc rationalize if kill criteria fire.

## Why this is structurally novel vs DEAD_ENDS.md

- **Not iter 016/018/020/021**: iter 016 base is 60:40 SPY+IEF
  static-stack with vol-target on equity+bond σ²_port; iter 040 has
  NO equity stack, the basket itself is the strategy. The σ²_port
  absorption mechanism that limited iter 032 is structurally
  absent here.
- **Not iter 026/027/028/029/030/031/039**: iter 026-031 are
  single-asset SPY VRP at constant notional. Iter 039 introduces
  cross-asset basket but at constant notional. Iter 040 adds the
  **MM 2017 dynamic-sizing axis** to iter 039's basket; the lever is
  inverse-variance scaling, NOT constant linear leverage (closed by
  iter 027) and NOT a binary VIX gate (closed by iter 028-031).
- **Not iter 032** (composed iter 015 + iter 031 VRP overlay on top
  of equity stack at score 72): iter 032 had ρ_SPY ≈ 0.97
  put-spread absorbing into σ²_port. Here the basket overlay is the
  ENTIRE return stream; there is no equity-stack absorbent.
- **Not iter 035/037/038** (static-stack family at 77/79 ceiling):
  iter 040 is in the VRP family, not static-stack family.

This direction is **explicitly listed as iter 040 RECOMMENDED in
`BASE_MEMORY.md` line 130** ("Vol-target wrapper around iter 039
basket: Moreira-Muir σ⁻²-scaling on basket realized vol… Predicted:
edu DSR < 0.05 credible PASS, score 78-82 → potential WINNER").

## Pre-committed configuration

```python
CFG = {
    "cfg_id": "vrp_basket_vt_eq3_5_10_1m_t05_L21_cap20",
    # Inherited from iter 039 (preserved verbatim) — basket harvest mechanics:
    "rf": 0.02,
    "harvest_notional": 1.0,
    "weights": {"SPY": 1/3, "QQQ": 1/3, "IWM": 1/3},
    "iv_scales": {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
    "k_long_pct": 0.95,
    "k_short_pct": 0.90,
    "dte_days": 21,
    "cost_bps_per_roll": 5.0,
    # NEW — Moreira-Muir vol-target wrapper:
    "target_vol": 0.05,    # 5% ann; matches iter 039 basket realized vol
                            # (edu/spy/ndx implied vol ≈ 4.0-4.5% ann from
                            # iter 039 Sharpe & CAGR)
    "lookback": 21,        # matches iter 016 (monthly window)
    "max_lev": 2.0,        # ≤ IDM 2.5 [systematic_trading, p.170]
}
```

This is the **only** configuration that will be tested. No grid, no
sweep, no post-hoc parameter tuning. If kill criteria fire, the
hypothesis is falsified — `DEAD_ENDS.md` gets a new section closing
"MM 2017 vol-target wrapper on cross-asset VRP basket".
