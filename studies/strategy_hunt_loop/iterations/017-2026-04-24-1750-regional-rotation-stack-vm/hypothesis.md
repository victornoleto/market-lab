# Iteration 017 — 12-1 top-1 cross-sectional rotation on 3 regional synthetic stacks, iter 016 base

**Date:** 2026-04-24 17:50
**Status:** Pre-commit hypothesis (Stage 2)
**Slug:** `regional-rotation-stack-vm`
**Cfg id:** `nts_regional_top1_vm_vt15_L21_cap20`

---

## Hypothesis

Extend iter 016's STRONG (79/100, 4/5 winner) fixed-ratio × vol-target
primitive to a 3-universe cross-sectional rotation. The base mechanism
(0.6 equity + 0.4 bond normalised weights, scaled by
`target_vol² / σ²_port[t-1]` clipped to `[0, max_leverage=2.0]`) is
unchanged. What CHANGES is the equity universe: instead of a single
equity (SPY or QQQ), the strategy holds the iter 016 primitive on ONE
of three regional synthetic stacked products, selected by 12-1
absolute momentum (`r_{t-21} / r_{t-252} - 1` on the equity component),
rebalanced monthly (every 21 trading days). Bond leg (IEF) is constant
across regions.

The three regions are:

- **US**: SPY + IEF (on educational, spy_real); QQQ + IEF (on ndx_real
  — keeps the dataset's natural US-tech identity).
- **Developed ex-US**: EFA + IEF. EFA tracks MSCI EAFE (Japan, Europe,
  Australasia — approx $20T market cap).
- **Emerging markets**: EEM + IEF. EEM tracks MSCI Emerging (China,
  India, Brazil, etc — approx $8T market cap, tilted EM-tech +
  commodities).

At each monthly rebalance, rank the three regions by 12-1 equity-leg
momentum and hold iter 016's primitive on the winner for the next 21
trading days. Within the hold window, daily vol-target rescaling
applies (iter 016 mechanism unchanged).

The central conjecture: if cross-sectional regional dispersion in
equity returns contains orthogonal information to the vol-management
axis (which iter 016 captures via σ²_port scaling), then the rotation
should boost observed Sharpe beyond iter 016's 0.98 / 1.14 / 1.19,
potentially enough to break the DSR ceiling at
`cumulative_n_trials = 4264` post-iter-017.

## Primary citation

`[stocks_on_the_move, p.76-77]` — Clenow's cross-sectional ranking
framework. His canonical ranking is adjusted-slope × R² on S&P 500
constituents; here we substitute vanilla 12-1 momentum on 3 regional
ETF equities. Universe size departure from Clenow is intentional: the
iter 003 dead-end closes ≤ 20-asset HOMOGENEOUS baskets; regional
equity is not homogeneous (commodity beta on EEM, dollar exposure on
EFA, growth/tech on US).

## Additional citations

- `[risk_parity, p.10-11, ch.1]` — naïve risk parity, fixed-weight
  stack underlying iter 016's 0.6/0.4.
- `[systematic_trading, p.40, ch.2]` — volatility standardisation
  primitive (Moreira-Muir variant iter 016 inherits).
- `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 hard cap
  (iter 017 keeps `max_leverage=2.0`).
- `[ml_for_algo_trading, ch.4, p.86]` — 12-1 skip-a-month momentum
  canonical specification.
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials accounting.
- `[advances_fin_ml, p.208-211]` — single-cfg vacuous PBO PASS.
- `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` lag + `momentum_{t-1}`
  lag for no look-ahead.

Web:

- Asness, C., Moskowitz, T., Pedersen, L. (2013). "Value and Momentum
  Everywhere." *Journal of Finance* 68(3). SSRN
  [1363476](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1363476)
  — establishes cross-sectional momentum works across equities,
  bonds, currencies, commodities with cross-asset class evidence.
- Moskowitz, T., Ooi, Y. H., Pedersen, L. (2012). "Time Series
  Momentum." *Journal of Financial Economics* 104(2), 228-250 —
  12-month momentum standard. DOI
  [10.1016/j.jfineco.2011.11.003](https://doi.org/10.1016/j.jfineco.2011.11.003).
- Moreira, A., Muir, T. (2017). "Volatility-Managed Portfolios."
  *JoF* 72(4), 1611-1644. DOI
  [10.1111/jofi.12513](https://doi.org/10.1111/jofi.12513) —
  vol-managed × momentum combination canonical.

## Edge source

SPY buy-hold Sharpe 0.90 is dominated by US equity's regime since
2009; a cross-sectional rotation across US / developed-intl / EM
equity (stacked on a constant bond leg) captures three
non-identically-distributed equity return streams. When one region
leads (e.g., EEM during 2003-2007 commodities, US during 2010-2020
tech, EFA during certain dollar-weak phases), concentrating on that
region's iter 016 primitive gains uplift vs always-US. Vol-management
(inherited from iter 016) continues to cut exposure when any active
region enters a stress regime, so downside protection is preserved.

## Why this is NOT a re-test of iter 003 (sector ETFs)

Iter 003 dead-end (cross-sectional ranking on ≤ 20-asset homogeneous
baskets) argues the aggregate market factor dominates idiosyncratic
ranking signal when assets are diversified baskets of the same
economy (all 11 SPDR sectors track US large-cap). Regional equity
differs on three empirical axes:

1. **Currency exposure** — EFA is mostly EUR/JPY/GBP; EEM is BRL/CNY/
   INR; US is USD-denominated. Exchange-rate shocks move regions
   independently at quarterly+ horizons.
2. **Factor composition** — US is tech-heavy (~30% info tech); EFA is
   financials/industrials heavy (~30%); EEM is commodity-linked
   (~35% tech + materials + energy). Factor rotations within the
   global equity risk premium favour different regions.
3. **Macroeconomic heterogeneity** — US-JP-EZ-China business cycles
   are only partially synchronised; regional recessions can hit in
   sequence (2012 EU crisis, 2015 China slowdown, 2022 US rate hike).

However — a soft caveat documented: **over the IEF-aligned window
2006-2026, the three regions are highly correlated (ρ SPY-EFA = 0.883,
SPY-EEM = 0.821, EFA-EEM = 0.873)** and US has structurally dominated
(Sharpe 0.628 SPY vs 0.361 EFA vs 0.336 EEM on raw returns). This
means cross-sectional dispersion is weak in this window — the
empirical uplift from rotation may be modest. Kill criteria below
reflect this honest expectation.

## Datasets

- **educational**: SPY + EFA + EEM + IEF, 2006-01-04 → 2026-04-15
  (IEF-aligned, same window as iter 016 educational). 12-1 momentum
  requires 252-bar warmup → effective trading start ~ 2007-01-04.
  ~4850 trading bars post-warmup.
- **spy_real**: SPY + EFA + EEM + IEF, 2009-06-26 → 2026-04-15.
  Effective trading start ~ 2010-07-08. ~3980 trading bars post-warmup.
- **ndx_real**: QQQ + EFA + EEM + IEF, 2010-02-16 → 2026-04-15.
  US region is QQQ (tech-heavy). Effective trading start ~ 2011-02-16.
  ~3820 trading bars post-warmup.

All data sourced from `data/tiingo/daily/prices/*.parquet`
(Tiingo adjusted close, split + div adjusted, daily).

## Kill criteria (pre-committed)

Any of these at end of Stage 4 falsifies the hypothesis:

- **Kill #1 (Sharpe regression):** Sharpe regresses > 0.03 vs iter 016
  on ≥ 2 of 3 datasets. Concretely:
  - educational Sharpe < 0.953 (iter 016: 0.983)
  - spy_real Sharpe < 1.108 (iter 016: 1.138)
  - ndx_real Sharpe < 1.165 (iter 016: 1.195)
  If ≥ 2 of these fail → Kill #1.
  Rationale: +0.03 tolerance on regression is 50% of the reasonable
  noise band given monthly rebalance variance.
- **Kill #2 (winner conditions drop):** Winner conditions met < 4
  (iter 016 was 4/5). Even losing the gate or CAGR axis would be a
  structural failure.
- **Kill #3 (score drop):** Total score < 72 (> 7 below iter 016's
  79). Score ≥ 72 means the hypothesis at least preserves iter 016's
  headline tier; < 72 is a structural regression.
- **Kill #4 (MDD regression):** MDD regresses > 5 pp vs iter 016 on
  ≥ 2 of 3 datasets. Specifically:
  - educational MDD > 36.33% (iter 016: 31.33%)
  - spy_real MDD > 31.65% (iter 016: 26.65%)
  - ndx_real MDD > 28.23% (iter 016: 23.23%)
  ≥ 2 fails → Kill #4. Region switches introduce transition risk;
  this bounds how much we tolerate.
- **Kill #5 (turnover explosion):** Any dataset has turnover per year
  > 15 on equity leg. Iter 016 was 4.6-7.4/yr (daily vol-target
  only). Monthly rotation + daily vol-target should push ≤ 10/yr
  with some switch overhead. > 15 indicates the monthly cadence is
  too aggressive for the 12-1 signal on this universe — structurally
  broken, not parametric.

## Expected budget

- Configs to test: **1** (pre-committed, no grid, no sweep).
- Datasets: 3 (educational, spy_real, ndx_real).
- New trials added: 3. `cumulative_n_trials` 4261 → 4264.
- Wall-time: 5-10 minutes (3 parallel iter-016 runs × 3 datasets +
  monthly re-rank loop + 7-gate battery).
- New files:
  - `regional_rotation_stack.py` — engine (pandas)
  - `numpy_reference_regional.py` — G7 parity reference
  - `run_backtests.py` — 3-dataset runner
  - `compute_gates_and_score.py` — 7 gates + score via `scoring.py`
  - `hypothesis.md` (this file)
  - `results.json`, `verdict.json`, `final_report.md` (generated)
- Modified files:
  - `tests/test_regional_rotation_stack.py` — 10-12 TDD specs
  - `BASE_MEMORY.md` — iteration log + frontmatter
  - `DEAD_ENDS.md` — only if FAIL tier reached

Pytest baseline must stay at 775 passing + 5 skipped (iter 016 high)
or higher. New tests should ADD to count.

## Implementation plan

1. **Write TDD specs first** — `tests/test_regional_rotation_stack.py`:
   - spec 1: 12-1 momentum with 21d skip — golden path on constructed
     series
   - spec 2: top-1 selection picks region with highest momentum
   - spec 3: tie-break uses first-alphabetical (US, EFA, EEM) for
     determinism
   - spec 4: rebalance cadence every 21 bars (not daily)
   - spec 5: no look-ahead (momentum at bar t uses data up to t-1)
   - spec 6: switch cost applied on transition days
   - spec 7: iter 016 vol-target mechanism preserved within hold
     window
   - spec 8: degenerate single-region case → reduces to iter 016
     exactly (tolerance ≤ 1e-10)
   - spec 9: ValueError on misaligned indices
   - spec 10: ValueError on insufficient bars for warmup
   - spec 11: cross-lib parity vs numpy reference (≤ 1e-10)
   - spec 12: sane turnover bounds (≤ 15/yr on constructed input)

2. **Implement engine** `regional_rotation_stack.py`:
   - Input: three (equity, bond) return DataFrames (one per region),
     shared DatetimeIndex, same bond leg.
   - Step 1: compute 12-1 momentum on each region's equity.
   - Step 2: for each rebalance date (every 21 bars starting at bar
     252+21=273), pick region with highest momentum.
   - Step 3: within hold window, apply iter 016's
     `apply_static_stack_vol_managed` on the selected region's (eq, bd).
   - Step 4: concatenate per-hold-window segments; add one-off switch
     cost on transition bars.

3. **Numpy reference** `numpy_reference_regional.py`:
   - Re-implement from scratch using only numpy (no pandas).
   - Input: numpy arrays for each region's returns + dates.
   - Step-by-step equivalent; yields same CAGR ± 3 pp (G7 gate).

4. **Run backtests** `run_backtests.py`:
   - Load 4 parquet files per dataset.
   - Align to IEF-inception (same as iter 016).
   - Run `apply_regional_rotation_vm` → get net returns per dataset.
   - Write `results.json` with per-dataset metrics + region selection
     log per rebalance date.

5. **Compute gates + score** `compute_gates_and_score.py`:
   - G1 PBO vacuous PASS (single pre-committed cfg, per iter 016).
   - G2 DSR with `n_trials = 4264`.
   - G3 Walk-Forward 8/8 (monotonicity of iter 016's block structure
     inherited).
   - G4 OOS 70/30 Sharpe > 0.
   - G5 FWD post-2020 Sharpe > 0.
   - G6 Bootstrap 99.9% CI low > 0.
   - G7 Cross-lib ±3 pp CAGR vs numpy reference.
   - Score via `scoring.score_strategy(...)` + robustness bonus from
     9 sub-windows (3 per dataset).

6. **Write final_report.md + verdict.json** per PROMPT Stage 5.

## Expected outcome (honest assessment)

Given the high regional correlations (0.82-0.88) and US dominance
over 17y, the base case is that the rotation picks US most of the
time (> 70 % of rebalance dates). In those months, the strategy
matches iter 016 modulo turnover overhead. In the ~30 % of months
where EFA or EEM leads, the strategy earns uplift IF the 12-1 signal
is predictive; if it's noise, the strategy earns drag.

Expected total score range: **70-80** (STRONG or high PROMISING
tier). Most probable outcome:
- Sharpe: similar or -0.05 vs iter 016 (noise zone).
- CAGR: similar or -1-2 pp.
- MDD: similar or +2-5 pp (transition risk).
- Score: 73-77 (gates may drop 1 per dataset at G4/G5 from monthly
  switch variance).
- DSR: marginally worse (observed Sharpe unchanged, n_trials grows).
- Winner conditions: 4/5 → 3/5 likely (sharpe axis may lose 1 ds).

If the rotation clearly improves > +0.10 Sharpe on ≥ 2 datasets,
that breaks our prior and we learn something structural about
regional dispersion. If it regresses, we learn that cross-sectional
rotation on 3 regions is saturated by US dominance in this sample —
closing a structural option.
