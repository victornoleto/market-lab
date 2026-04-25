# Iteration 035 — Static stack with GLD replacing IEF (asset-class orthogonality test)

## Hypothesis

Replace iter 015's bond leg (IEF) with a **gold leg (GLD)** at the
identical 0.9 / 0.6 NTSX-style weight ratio, daily-rebalanced. Single
pre-committed config `static_stack_90_60_spy_gld` (no grid, no sweep).

The point is **diagnostic**: iter 032/033/034 closed every variation
of the bond axis (composition, full-duration substitution, zero-net-
notional spread sleeve) at score 72, all DSR-bound. The iter 015
plateau at 77 is now decisively the bond-axis efficient frontier.
But iter 034's lesson left an open question: was iter 015's edge
**bond-specific** (term-premium carry as the structural alpha) or
**diversifier-agnostic** (any low-correlation second leg works)?

A clean way to answer: hold the architecture and weights identical
to iter 015, swap the asset class. Gold has **zero coupon carry**
(contango ~−1%/yr on average per Erb-Harvey 2006), but historically
delivered a positive risk premium ~+5%/yr 2004-2026 driven by
real-rate decline + inflation hedge + safe-haven flows. Its
correlation to SPY (~−0.05 to +0.20) is qualitatively similar to
IEF's (~−0.27), but its crash distribution is **structurally
orthogonal** to bond duration — gold rallies in real-yield decline
regardless of inflation direction, while bonds collapse when
inflation surprises higher.

If iter 015's edge survives the swap → diversification is the
mechanism, gold/bonds are interchangeable second legs, opens
multi-asset diversifier basket as next direction.

If the swap collapses → bond carry IS the structural alpha source,
iter 015 plateau is genuinely term-premium-bound, and the loop
should pivot away from any static stack and toward non-static
architectures (regime/ML/CS factor timing).

If the swap matches or beats → gold may even be a **better**
diversifier than IEF (the variance-control hypothesis from iter 034
generalised cross-asset).

## Primary citation

`[risk_parity, ch.5]` — diversifier-leg variance decomposition;
risk-parity argument is mechanism-agnostic about the second leg's
specific asset class, only requiring low correlation and non-zero
expected return.

## Additional citations

- `[risk_parity, p.5, p.10-11, ch.1]` — Asness, Frazzini & Pedersen
  (2012). *FAJ* 68(1). "Leverage Aversion and Risk Parity." SSRN
  1728082. Static stack mechanism (preserved verbatim from iter 015).
- `[leverage_for_the_long_run, p.19-20]` — leverage on a diversified
  base captures duration risk-premium without market-timing.
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (G2).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- **Erb, C.B. & Harvey, C.R. (2006).** "The Strategic and Tactical
  Value of Commodity Futures." *FAJ* 62(2): 69-97. DOI
  10.2469/faj.v62.n2.4084. Gold's term-structure (gentle contango
  in normal conditions); commodity diversification benefit measured
  per Sharpe-ratio improvement on a 60/40 base.
- **Asness, C.S., Moskowitz, T.J. & Pedersen, L.H. (2013).** "Value
  and Momentum Everywhere." *JF* 68(3): 929-985. DOI
  10.1111/jofi.12021. SSRN 1363476. Cross-asset orthogonality
  argument: factor returns within an asset class share less common
  variance than across asset classes.
- **Koijen, R.S.J., Moskowitz, T.J., Pedersen, L.H. & Vrugt, E.B.
  (2018).** "Carry." *JFE* 127(2): 197-225. DOI
  10.1016/j.jfineco.2017.11.002. §3 frames gold's "carry" as
  spot-forward basis (storage cost net of lease income), historically
  near-zero or slightly negative — relevant to predicting whether
  gold can substitute for bond carry as a structural return source.
- **Ilmanen (2011).** *Expected Returns.* Wiley. ch.6 (term premium),
  ch.10 (commodity premium magnitudes).
- WisdomTree NTSX prospectus — 90/60 weights (preserved verbatim).
- Tiingo daily SPY / GLD / QQQ adjusted close (cache: `data/tiingo/
  daily/prices/`). GLD inception 2004-11-18 → educational window is
  21y vs iter 015's 20y.

## Edge source

Cross-asset orthogonality between equity beta and gold's real-yield-
decline + safe-haven premium. Distribution-orthogonal to both bond
duration (iter 015) and bond carry (iter 034) — gold's crash
patterns coincide with bonds in some risk-off regimes (2008-Q4,
2020-Mar) but diverge sharply in inflation shocks (2022 — gold flat,
TLT −31%, IEF −15%). What SPY-only buy-hold misses: a return source
whose drawdown timing partially anti-correlates with equity tail
events without the duration-rate-shock vulnerability of iter 015's
bond leg.

## Datasets

- **educational** (SPY+GLD, 2004-11-18 → 2026-04-15, 21y): GLD-inception-
  aligned. Covers 2008 GFC + 2020 COVID + 2022 inflation regime — full
  cross-regime stress. Slightly longer than iter 015's edu window
  (which started 2006-01-03 due to IEF inception). The 2 extra years
  bracket the 2004-2006 rate-rising regime.
- **spy_real** (SPY+GLD, 2009-06-25 → 2026-04-15, 17y): preserved
  exactly from iter 015 / 033 / 034 to enable apples-to-apples Sharpe
  comparison.
- **ndx_real** (QQQ+GLD, 2010-02-12 → 2026-04-15, 16y): preserved
  exactly from iter 015 / 033 / 034.

## Kill criteria (pre-committed)

The following six conditions are pre-committed before viewing any
result. If any fires, the corresponding finding is recorded
honestly without re-tuning.

- **Kill A (Sharpe regress vs iter 015)**: Sharpe Δ vs iter 015 < −0.05
  on ≥ 2 of 3 datasets → **bond carry was the structural alpha source**;
  GLD swap fails as drop-in replacement; closes "diversifier-agnostic"
  hypothesis.
- **Kill B (ndx MDD breach)**: MDD on ndx_real > 45% → gold-as-
  diversifier produces tail-risk worse than the +5pp ceiling (40.12%
  per scoring benchmark). Note: iter 034 ndx MDD was 42.11% — this is
  slightly looser than benchmark to allow comparison.
- **Kill C (DSR worst-p)**: DSR worst-p > 0.20 (n_trials=4294) → cross-
  asset orthogonality fails to shift DSR despite static stack family
  exhausted at this Sharpe ceiling.
- **Kill D (G7 cross-lib)**: any dataset's pandas-vs-numpy CAGR
  delta > 3.0 pp → engine bug (G7 hard fail).
- **Kill E (score below tier floor)**: total_score < 60 → drops to
  MARGINAL or worse; closes any further gold-as-diversifier path.
- **Kill F (robustness)**: < 7 / 9 sub-window Sharpes positive across
  3 datasets × 3 sub-windows → instability.

The MOST INFORMATIVE outcome is Kill A vs no-kill:
- If only Kill A fires (Sharpe regresses) → **bond-carry-bound result**;
  closes diversifier-agnostic hypothesis cleanly.
- If no kills fire and score ≥ 75 → **diversifier-agnostic result**;
  opens multi-asset diversifier basket direction.
- If 1-2 kills fire including C → consistent with iter 032/033/034
  pattern (DSR-bound at this Sharpe magnitude regardless of asset).

## Expected budget

- Configs to test: **1** (single pre-committed cfg, NO sweep)
- Wall-time: ~10-15 minutes (single backtest × 3 datasets +
  gates + scoring)
- Files to create:
  - `synth_stacked_etf.py` (re-export of iter 015 primitive — same
    function, asset-agnostic by design; copy or import)
  - `numpy_reference_stacked.py` (re-export of iter 015 numpy
    reference — for G7 cross-lib parity)
  - `run_backtests.py` (CFG + 3 datasets + load_pair_returns(SPY|QQQ,
    GLD))
  - `compute_gates_and_score.py` (7 gates + scoring + verdict.json)
  - `results.json`, `verdict.json`, `final_report.md`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`

## Implementation plan

1. **Stage 3a — engine reuse**: Copy iter 015's `apply_static_stack`
   and `apply_static_stack_np` into iter 035 directory (no edits — they
   are asset-agnostic). The function takes `r_eq` and `r_bd` Series; we
   just feed GLD returns where iter 015 fed IEF returns. No simulator
   changes; iter 015 already does the right thing.

2. **Stage 3b — datasets**: Preserve iter 015's spy_real and ndx_real
   windows verbatim. Educational: shift start to GLD inception
   (2004-11-18). Use `data/tiingo/daily/prices/SPY|QQQ|GLD.parquet`
   with `adj_close` + `pct_change()` (canonical iter 015 pipeline).

3. **Stage 3c — single cfg**: `static_stack_90_60_spy_gld` with
   `eq_w=0.90, bd_w=0.60, cost_bps_per_leg=0.0002`. Total leverage 1.5,
   identical to iter 015 / 033 / 034.

4. **Stage 4a — gates** (per dataset): G1 vacuous PASS (N=1, PBO
   undefined per iter 015/033/034 rationale), G2 DSR (n_trials=4294 —
   prior cumulative 4291 + 1 cfg × 3 datasets), G3 walk-forward 8
   blocks, G4 OOS 70/30, G5 FWD post-2020, G6 bootstrap 99.9% CI low,
   G7 cross-lib pandas-vs-numpy CAGR delta ≤ 3.0pp.

5. **Stage 4b — scoring**: `score_strategy()` with frozen benchmarks
   from `scoring.BENCHMARKS` (canonical) AND a custom-benchmark
   variant where educational uses the GLD-aligned SPY 21y benchmark
   (matches iter 034's pattern of reporting both). Robustness bonus
   from 3 sub-windows × 3 datasets.

6. **Stage 5 — reporting**: full `final_report.md` with score
   breakdown table, Δ vs iter 015 / iter 034 / iter 033, kill-criteria
   status, and structural lesson (bond-carry-bound vs diversifier-
   agnostic). Generate plots via `plot_helper.py --iter 035`. Update
   `BASE_MEMORY.md` with new entry + iteration log + top-K maintenance
   + closed-direction note.

Cumulative n_trials advance: **4291 → 4294** (iter 035 = +3, single
cfg × 3 datasets).
