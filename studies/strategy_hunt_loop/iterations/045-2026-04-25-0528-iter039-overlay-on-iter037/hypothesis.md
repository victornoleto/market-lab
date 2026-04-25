# Iteration 045 — Out-of-family return-stream addition (50/50 convex combo of iter 037 static 3-leg stack + iter 039 VRP basket harvest)

## Hypothesis

**Layer iter 039 (cross-asset VRP basket harvester, T-bill collateral
+ 1/3 short SPY/QQQ/IWM 5/10 OTM 21DTE put credit spreads, DSR worst-p
~0.075) on top of iter 037 (3-leg static stack 0.6 SPY + 0.45 IEF +
0.45 GLD at 1.5× total leverage, DSR worst-p ~0.222) at 50/50 fixed
weights.** The combined daily return is the convex average:

```
r_combined[t] = 0.5 * r_037[t] + 0.5 * r_039[t]
```

Pre-committed single config; daily rebalance to fixed 50/50 (no
overlay-style additive composition that broke iter 032). All
sub-strategy hyperparameters preserve iter 037 and iter 039 verbatim
— no post-hoc tuning.

## Why this should work (and why it might not)

**The thesis**: iter 042 / 043 / 044 jointly localised iter 041's
84-ceiling on three structural axes (gate amplitude, frequency,
input — all regress DSR by 4-7pp). Any naive enrichment of iter 041's
gate fails. The remaining open path is **out-of-family return-stream
addition**: rather than refining a gate, add a SEPARATE DSR-positive
return source so the combined DSR worst-p compounds via cross-correlation.

iter 037 generates returns from term premium (IEF carry) +
commodity premium (GLD) + equity beta (SPY) at 1.5× lev. iter 039
generates returns from the variance risk premium (Bondarenko 2014;
Carr-Wu 2009) harvested via short put credit spreads on a 3-asset
basket (SPY + QQQ + IWM, weighted 1/3 each). The two mechanisms are
structurally orthogonal: iter 037's edge is buy-and-hold + leverage
on uncorrelated assets; iter 039's edge is selling cheap insurance
when implied vol exceeds realised vol.

**Why combined DSR may improve vs iter 037**:

If `corr(r_037, r_039)` is moderate (0.4-0.7), the combined Sharpe
benefits from diversification:

```
Sharpe_combined = (0.5 * S_037 + 0.5 * S_039 * σ_039 / σ_037) / sqrt(...)
```

with iter 037 Sharpe 0.98/1.15/1.17 and iter 039 Sharpe 1.14/1.29/
1.56, the 50/50 combined could land 1.05-1.30 on real data —
potentially above iter 041's 1.13/1.16 Sharpe and with a different
DSR profile.

**Why combined DSR may NOT improve (the iter 032 failure mode)**:

In iter 032, layering iter 015 (NTSX 90/60 SPY+IEF) + iter 031
(single-SPY VRP) failed: corr_combined,SPY = +0.97 across 3 datasets,
ndx_real MDD 44.38% breach (+4.26pp over ceiling), and DSR worst-p
collapsed to 0.50 (vs iter 015's ~0.07 alone). Reason: put-spread
losses concentrated in 2008-Q4 / 2018-Q4 / 2020-Q1 / 2022 explicitly
correlated with equity drawdowns in iter 015's stack, so the joint
distribution had heavy negative skew that DSR's higher-moment
deflator captured aggressively at n_trials=4285.

**iter 045 mitigates iter 032's failure mode by**:

1. **GLD diversification**: iter 037 includes 0.45 GLD (vs iter 015
   which had 0). GLD has near-zero corr with both equity DD and
   put-spread harvest losses (Erb-Harvey 2006).
2. **Basket VRP**: iter 039's per-leg DD is ~7-14% (much lower than
   iter 031's single-SPY ~16%) because the basket diversifies across
   SPY/QQQ/IWM with iv_scales 1.0/1.10/1.25 (Driessen-Maenhout-Vilkov
   2009). Lower per-leg tail → lower joint tail with iter 037.
3. **50/50 convex combo (not additive overlay)**: total leverage of
   the combined portfolio is `0.5 × 1.5 + 0.5 × 1.0 = 1.25` (modest;
   iter 032 was 1.5 + 1.0 = 2.5).
4. **Pre-committed weights**: no iteration over weight grids; single
   cfg `0.5/0.5` chosen on the principle of unbiased diversification
   between two STRONG-tier mechanisms.

The composition still risks DSR collapse if the joint distribution
introduces explicit negative skew. Pre-committed Kill F watches for
`corr(r_037, r_039) > 0.85` (iter 032's signature corr was 0.97).

## Primary citation

`[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack
(iter 037 base architecture: long-only weighted equity + bond + gold).

## Additional citations

- `[volatility_trading, p.218]` — Sinclair (2013) on cross-asset VRP
  harvesting (iter 039 basket architecture).
- `[volatility_trading, ch.3, p.41, p.217]` — VRP mechanics + capped
  tail of credit spreads.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
  combining low-correlation strategies improves the deflated p-value
  if the per-strategy Sharpes both exceed the deflator's threshold.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity gate.
- `[leverage_for_the_long_run, p.19-20]` — leverage on diversified
  base captures multiple risk premia (iter 037 inherits this).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 —
  strategic role of gold in long-horizon portfolios (orthogonality
  to equity beta and short-vol harvest).
- Bondarenko (2014), QJF 4(3) 1450015 — empirical SPX VRP magnitude
  + cluster behaviour (the failure-mode literature for put-writers).
- Carr-Wu (2009), RFS 22(3) 1311-1341 — variance risk premia
  structural framework.
- Driessen-Maenhout-Vilkov (2009), JoF 64(4) 1377-1406 —
  cross-sectional decomposition of index VRP into individual +
  correlation risk components (justifies the 3-leg basket vs single SPY).
- Asness-Moskowitz-Pedersen (2013), JoF 68(3) 929-985 — cross-asset
  diversification benefits.
- Markowitz (1952), JoF 7(1) — convex combination minimum-variance
  framework (single cfg w=0.5 is the symmetric default).

## Edge source

iter 037 captures unconditional equity-bond-gold risk premia at 1.5×
leverage on a diversified base; iter 039 captures the SPX-Russell-NDX
basket variance risk premium via short put credit spreads on T-bill
collateral. **SPY 1x buy-hold misses both** — the bond/gold premia
(iter 037 component) AND the volatility risk premium (iter 039
component). Combined at 50/50, the candidate exploits both
orthogonal sources simultaneously.

## Datasets

- **educational** (SPY+IEF+GLD+SPY+QQQ+IWM 2006-01-03 → 2026-04-14):
  inner-join start at iter 039's anchor (post-IWM availability +
  GLD-inception offset). Captures 2008 GFC stress test for the
  composition (the iter 032 failure period).
- **spy_real** (2009-06-25 → 2026-04-14): 17y post-GFC; matches
  iter 037 + iter 039 anchor. Tests composition through 2018-Q4 +
  2020-Q1 + 2022 stresses.
- **ndx_real** (2010-02-12 → 2026-04-14): 16y; bench QQQ. Tests
  composition through 2022 QQQ −33% drawdown — the iter 032 ndx_real
  44% MDD breach is the explicit risk we mitigate.

All three datasets use Tiingo daily adjusted-close + macro VIX
(iv_scale 1.0/1.10/1.25 for SPY/QQQ/IWM proxy of VIX/VXN/RVX). All
data is in `data/tiingo/daily/prices/` and
`data/external/macro/vix_daily.parquet`.

## Kill criteria (pre-committed)

| kill | criterion | threshold |
|---|---|---|
| **A** Sharpe regress vs best component | combined Sharpe < max(iter_037, iter_039) − 0.05 on ≥ 2/3 datasets | 50/50 broken — composition destructively interferes |
| **B** DSR regress vs iter 037 base | DSR worst-p ≥ iter 037's 0.222 (i.e., NO DSR improvement) | composition added trials without compounding edge |
| **C** MDD breach | combined MDD on ANY dataset > benchmark + 5pp | iter 032 risk re-trigger (joint negative skew) |
| **D** Score regress vs iter 037 | total score < 79 | composition is strictly worse than iter 037 alone |
| **E** G7 cross-lib | abs(CAGR pandas − CAGR numpy) > 3 pp | engine bug (cross-lib parity) |
| **F** Cross-strategy correlation | corr(r_037, r_039) > 0.85 on any dataset | composition not orthogonal as predicted (iter 032 signature) |

If **Kill A** OR **Kill B** OR **Kill C** OR **Kill D** fires, the
hypothesis is **partially falsified** (still PROMISING tier
possible). If **Kill F** fires AND **B** also fires, the hypothesis
is **structurally falsified** (the orthogonality premise is wrong
for this 037+039 pairing).

## Expected budget

- **Configs to test**: 1 (single pre-committed `iter039_on_iter037_50_50`)
- **Wall-time**: ~30-45 minutes (full pipeline: load 5 tickers + VIX,
  inner-join, run iter 037, run iter 039, combine, compute gates,
  cross-lib reference, plots)
- **Cumulative n_trials advance**: 4309 → 4310 (+1)
- **Files to create**:
  - `hypothesis.md` (this file)
  - `combined_037_039.py` — pandas engine (calls iter 037 +
    iter 039 helpers, then convex combo on inner-join)
  - `numpy_reference_combined.py` — pure numpy reference for G7
  - `run_backtests.py` — single cfg driver, 3 datasets
  - `compute_gates_and_score.py` — gates + scoring + kill evaluation
  - `tests/test_iter_045_combined.py` — TDD specs (≥ 6 tests
    covering reduction to iter 037 when w=0, reduction to iter 039
    when w=1, intersection-index handling, cost accounting,
    convex-combo invariants, cross-lib parity)
  - `results.json`, `verdict.json`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
  - `final_report.md`

## Implementation plan

1. **Write TDD specs first** (`tests/test_iter_045_combined.py`):
   - `test_reduces_to_iter_037_when_w039_zero` — w=0 → r_037 exactly
   - `test_reduces_to_iter_039_when_w037_zero` — w=1 → r_039 exactly
   - `test_combined_index_is_intersection_of_037_and_039` — handles
     differing inner-joins
   - `test_50_50_combo_returns_average_under_constant_inputs` —
     algebraic invariant
   - `test_cost_inheritance_from_subcomponents` — cost is
     intrinsic to each sub-strategy; combined is post-cost
   - `test_cross_lib_parity_within_3pp` — G7
2. **Implement `combined_037_039.py`**:
   - Imports `apply_static_stack_3leg` from iter 037
   - Imports `compute_vrp_basket_returns` from iter 039
   - Function signature:
     `compute_combined_returns(r_eq_037, r_bd_037, r_gld_037, prices_039_dict, vix, w_037=0.5, w_039=0.5, **iter_037_kwargs, **iter_039_kwargs) -> pd.Series`
   - Inner-join the iter 037 net (post-pct_change) with iter 039 net
     (raw price input); compute 50/50.
3. **Implement `numpy_reference_combined.py`** — full-pipeline
   numpy implementation (parity test for both subcomponents +
   convex combo).
4. **Run on 3 datasets** (`run_backtests.py`):
   - Load SPY/IEF/GLD/QQQ/IWM/VIX once per dataset window
   - Compute iter 037 net (using SPY+IEF+GLD)
   - Compute iter 039 net (using SPY+QQQ+IWM+VIX)
   - 50/50 combine on inner-join
   - Output `results.json` with `runs[ds][cfg_id]` schema and
     `returns_series[ds][cfg_id]={index, net_returns}` for plots.
5. **Compute gates + score** (`compute_gates_and_score.py`):
   - G1 PBO: skipped (n_configs=1, no grid → vacuous PASS by design)
   - G2 DSR: with cumulative_n_trials=4310
   - G3 WF: 8 windows, each 6/8 + MDD<25%
   - G4 OOS: 70/30 split, OOS Sharpe > 0
   - G5 FWD: post-2020 stress, Sharpe > 0
   - G6 Bootstrap 99.9% CI low > 0
   - G7 Cross-lib ±3pp CAGR
   - Robustness 9-window rolling Sharpe > 0
6. **Apply scoring helper** (`from scoring import score_strategy`)
   — same call pattern as iter 044.
7. **Write final report** + update `BASE_MEMORY.md` (advance
   `cumulative_n_trials` to 4310, append 6-field iter log entry,
   refresh top-K, refresh "Promising unexplored directions"
   removing the consumed iter 045 path).
8. **Generate plots**: `uv run python studies/strategy_hunt_loop/plot_helper.py --iter 045`.
