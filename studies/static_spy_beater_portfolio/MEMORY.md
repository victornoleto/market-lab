---
mission: "Find robust static monthly-rebalanced ETF portfolios that beat SPYSIM"
status: core_benchmark_pivot
active_phase: 1
latest_run: "core_beater_stacked_expansion_core_relative_wealth_dominance_seed{20260519,20260520,20260521}"
latest_status: "discovery_only_not_validated"
latest_best_config: "Core benchmark 35 GDESIM / 40 RSSTSIM / 25 ZROZSIM survived stacked-ETF GA triage (3 seeds, 21 tickers, 8 proxies). Core fitness 0.350 vs GA best 0.268."
latest_best_score: 0.350
cumulative_n_trials: 0
---

# MEMORY - static_spy_beater_portfolio

Read this file before each fresh session. This study searches static, long-only,
monthly rebalanced ETF portfolios using a genetic algorithm over 5% weight units.

## Current State

Bootstrap scaffold and optimized smoke are complete. Initial scope:

- Universes: `core_1986`, `mf_1988`, `global_1994`, `full_2000`.
- Fitness families: robust CAGR, Sharpe, Sortino, Calmar, relative wealth versus
  `SPYSIM` and `QQQSIM`, balanced SPY/dual beaters, and min-regret.
- Rolling horizons: 1/3/5/10/15/20 years with heavier weights on 10-20y windows.
- Benchmarks: `SPYSIM`, `QQQSIM`, equal-weight universe, and B4 when available.

No result is validated or deployable until separate robustness validation is run.

## Latest Smoke

`results/ga/core_1986_balanced_spy_beater_seed7/` tested the optimized GA plumbing
with 7 unique evaluated portfolios, yearly-sampled GA windows (`rolling_step=252`)
and exact re-rank of the top finalist (`rolling_step=1`). This was an engineering
smoke only, not a research run or winner claim. The key performance fix is that GA
discovery defaults to monthly-sampled rolling windows while finalist reports can
still use all possible rolling start/end dates.

## 2026-05-15 Refactor

Performance + correctness refactor of the scoring stack (no winner, no mandate
change, no new trials consumed):

- `precompute_growth_matrix` shares within-month asset cumprod across all GA
  candidates; per-candidate scoring becomes a matrix-vector multiply.
- `_rolling_metrics_array` was split into `_series_cumulatives` (hoisted once per
  series) plus `_vectorized_mdd` (cache-tuned log-space chunking). End-to-end the
  exact-rerank scoring drops from ~2.58s to ~0.54s per candidate on `core_1986`,
  and the cached-rolling-step=21 sampled scoring drops to ~0.028s/candidate.
- `fast-discovery` MDD/Calmar arrays are now NaN (not zero) so the balanced
  guard skips them honestly.
- `score_named_benchmarks` now emits `spy_buy_hold` and `qqq_buy_hold` next to
  `equal_weight` (and `b4` when applicable).
- `run_ga.py` history records `mean_fitness`, `median_fitness`, `std_fitness`,
  `distinct_chromosomes` and `population_unique_share` per generation; the
  payload carries `discovery_only: true`; the parent pool scales with
  population (`max(elite_size*3, population_size // 2)`); `--patience 0` auto-selects
  `min(25, max(5, generations // 2))` and `--patience -1` disables early stop.
- Smoke run: `results/ga/core_1986_balanced_spy_beater_seed9999/` (pop=16,
  gens=3, fast-discovery, 54 unique candidates, 3 exact reranks, real wall time
  6.4s). The top-3 are research traces only and consume zero validation budget.

## 2026-05-15 Multi-Seed Discovery Sweep

Completed 6 discovery GA runs: 3 seeds (`20260515`, `20260516`, `20260517`) across
`core_1986` and `mf_1988`, all using `balanced_spy_beater`, `fast-discovery`,
`rolling_step=21`, `finalist_exact=200`, and exact finalist re-rank with
`rolling_step=1` and full drawdown/Calmar. All runs early-stopped after convergence;
no result is validated or deployable.

Results were highly convergent across seeds:

- `core_1986`: all 3 seeds selected `40% TQQQSIM / 60% TMFSIM` after exact re-rank.
  Full-period metrics: CAGR `20.66%`, MDD `-84.28%`, Sharpe `0.708`, Calmar `0.245`,
  terminal wealth `1611x` vs `SPYSIM` `65x` and `QQQSIM` `216x`.
- `mf_1988`: all 3 seeds selected `35% TQQQSIM / 50% TMFSIM / 15% RSSTSIM` after
  exact re-rank. Full-period metrics: CAGR `22.10%`, MDD `-81.21%`, Sharpe `0.788`,
  Calmar `0.272`, terminal wealth `2083x` vs `SPYSIM` `64x`, `QQQSIM` `202x`, and
  B4 `174x`.

Interpretation: the current unconstrained `balanced_spy_beater` frontier is dominated
by an aggressive LETF barbell: Nasdaq 3x return engine plus 3x long-Treasury convexity,
with `RSSTSIM` adding modest diversification once available. This is economically
interesting but drawdown is extreme (`~ -81%` to `-84%`), so the next research step
should compare against a diversified/constrained fitness or explicit family caps.
Discovery candidate counts were roughly `7.3k-8.1k` unique candidates per `core_1986`
run and `9.9k-11.9k` per `mf_1988` run; these are GA search breadth diagnostics, not
validated DSR trial counts until a candidate is promoted to formal validation.

## 2026-05-15 Consistency Guard Lead

After an external Testfol.io check showed recent underperformance in the
`65% RSSTSIM / 30% TMFSIM / 5% TQQQSIM` Calmar-guard lead, the study added
`spy_beater_consistency_guard` and a `levered_hedge_no_tmf` universe. The new score
keeps full-period CAGR/MDD guards versus `SPYSIM`, requires the latest 3y window to
beat `SPYSIM`, and penalizes poor p10 rolling outcomes across 3y+ horizons. This is
intended to avoid HFEA-like regime death hidden by strong early history
`[testing_tuning, p.327-335]`, `[risk_parity, p.80-81]`.

Run `results/ga/levered_hedge_no_tmf_spy_beater_consistency_guard_seed20260534/`
early-stopped at generation 78 after 29,515 unique candidates. Exact re-rank top:

- `35% GDESIM / 50% RSSTSIM / 5% TQQQSIM / 10% ZROZSIM`.
- Full-period 1988-01-04..2026-04-17: CAGR `17.97%`, MDD `-49.37%`, Sharpe `0.972`,
  Sortino `1.351`, Calmar `0.364`, terminal wealth `558x`.
- Same-window `SPYSIM`: CAGR `11.46%`, MDD `-55.14%`, terminal wealth `63.6x`.
- Latest 10y window beats `SPYSIM` by `+4.04pp` CAGR and `+41.1%` relative wealth;
  latest 15y beats by `+3.95pp` CAGR and `+66.7%` relative wealth. Rolling 10y/15y
  p10 MDD spread is still slightly negative (`-2.0pp`), so this remains a discovery
  lead, not a robust winner.

## 2026-05-15 Testfol.io B4-Like Check

External Testfol.io response saved at
`/tmp/opencode/testfolio_static_spy_beater_compare_20260515.json` compared five
component portfolios over 1987-12-31..2026-05-14. Key finding: a B4-like component
portfolio (`47.5% SPYSIM / 25% GDESIM / 25% KMLMSIM / 25% ZROZSIM / 15% IEFSIM /
-37.5% CASHX`, monthly rebalance) had CAGR `13.81%`, MDD `-28.42%`, Sharpe `0.776`,
Sortino `1.118`, Calmar `0.486`, and Ulcer `6.88`, versus `SPYSIM` CAGR `11.58%`,
MDD `-55.14%`, Calmar `0.210`. The higher-return similar no-ZROZ/less-duration mix
reached CAGR `14.50%` but with MDD `-41.59%` and Calmar `0.349`. Interpretation:
ZROZ materially improves path robustness; optimization should now be local/Pareto
around B4-like allocations rather than pure CAGR seeking `[risk_parity, p.80-81]`,
`[testing_tuning, p.327-335]`.

## 2026-05-15 Robust GA Local Refinement

For the higher-return GA branch, `spy_beater_p10_mdd_guard` was added to reject
candidates whose 5y+ rolling p10 MDD spread versus `SPYSIM` is negative. Focused
universes `lead_family_focused` and `lead_family_no_3x_booster` were added around
the converged `RSSTSIM/GDESIM/ZROZSIM` family. Medium GA attempts with this strict
fitness were too slow at exact rolling drawdown, but partial logs converged toward
`50% RSSTSIM / 35% GDESIM / 10% SPYSIM / 5% ZROZSIM`.

Local-only refinement around that incumbent completed in
`results/refine_robust/lead_family_focused_spy_beater_p10_mdd_guard_refine/` with
2,881 candidates (three 5% moves, exact top-50). Best exact candidate remained
`50% RSSTSIM / 35% GDESIM / 10% SPYSIM / 5% ZROZSIM`: CAGR `16.81%`, MDD `-41.20%`,
Sharpe `0.972`, Sortino `1.338`, Calmar `0.408`, terminal wealth `383x`, and strict
p10-MDD fitness `0.1730`. This suggests the small `TQQQSIM` booster is not necessary
once rolling drawdown robustness is prioritized.

## 2026-05-15 Pareto/Regime Report

Priority 1 from `NEXT_STEPS.md` completed in
`results/pareto_regime_report/` using fixed candidates only; no broad GA or fresh
optimization was run. Artifacts:

- `REPORT.md`
- `metrics.csv`
- `rolling.csv`

The report confirmed the refined robust artifact by checking
`results/refine_robust/lead_family_focused_spy_beater_p10_mdd_guard_refine/top_exact.csv`:
`35% GDESIM / 50% RSSTSIM / 10% SPYSIM / 5% ZROZSIM` is the same allocation as
`GA_robust`.

Main reading over the common local window `1988-01-04..2026-04-17`:

- `B4_original` had the best full-period Calmar among candidates (`0.517`) with CAGR
  `14.43%`, MDD `-27.92%`, Sharpe `1.018`, terminal wealth `174x`.
- `B4_like_testfolio` remained the closest stability/reference stack: CAGR `13.75%`,
  MDD `-28.42%`, Calmar `0.484`, terminal wealth `139x`. It is explicitly not a
  pure long-only portfolio because it uses `-37.5% CASHX` and gross weight `1.75`.
- `GA_robust` delivered higher return: CAGR `16.81%`, MDD `-41.20%`, Calmar `0.408`,
  terminal wealth `383x`. It buys about `+3.06pp` CAGR versus B4-like at the cost of
  about `12.78pp` worse MDD; 5y rolling relative-wealth p10 versus `SPYSIM` was
  slightly negative (`-0.36%`).
- `GA_aggressive` had the highest CAGR/terminal wealth (`17.97%`, `558x`) but only
  added about `+1.16pp` CAGR versus `GA_robust` while worsening MDD by about `8.17pp`
  to `-49.37%`. That weakens the case for the `5% TQQQSIM` booster unless a later
  local Pareto search finds a cleaner frontier point.
- Regime diagnostics: B4/B4-like protected dot-com/GFC/inflation drawdowns better,
  while GA variants dominated recent-recovery relative wealth. No candidate is a
  winner or deployable; this is still discovery-only `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

Next research step should be local Pareto search, not broad GA: either start with the
B4-like stability branch to seek `+0.5pp-1.5pp` CAGR without breaking `~28-32%` MDD,
or the GA robust branch if explicitly accepting `~40%` MDD as the trade-off.

## 2026-05-15 B4-Like Local Pareto Search

Priority 2 started with the B4-like stability branch in
`results/local_pareto_b4_like/`. The first implementation tried to score the full
`308,698`-row grid candidate-by-candidate and was too slow/heavy. It was corrected to
stream candidates, cap local portfolios at `6` active sleeves, batch full-period
metrics with bounded memory, compute rolling 5y CAGR/relative-wealth only after the
full-period MDD filter, and maintain an incremental Pareto frontier. Final local grid:
`90,449` rows, `62,441` feasible rows, `313` Pareto rows.

Key result over `1988-01-04..2026-04-17`:

- Defensive top-Calmar row: `15% GDESIM / 45% IEFSIM / 30% KMLMSIM / 10% SPYSIM`,
  CAGR `8.59%`, MDD `-10.50%`, Calmar `0.818`. This is too defensive to answer the
  SPY-beater objective, but confirms the Pareto includes low-volatility anchors.
- Highest-CAGR feasible row under MDD `<=32%`: `35% GDESIM / 40% RSSTSIM / 5% SPYSIM /
  45% ZROZSIM / -25% CASHX`, CAGR `17.35%`, MDD `-30.44%`, Calmar `0.570`, terminal
  wealth `456x`, rolling 5y CAGR p10 `10.26%`, but rolling 5y relative-wealth p10 vs
  `SPYSIM` remained negative (`-6.39%`). It is a stacked reference (`gross=1.5`,
  `CASHX=-25%`), not pure long-only.
- This materially improves the local B4-like frontier versus the prior Testfol.io
  reference (CAGR `13.75%`, MDD `-28.42%`, Calmar `0.484`) while keeping drawdown near
  the intended `28-32%` band, but the negative rolling relative-wealth p10 blocks any
  winner/deploy interpretation. Next step should be exact rolling/regime report on
  the top B4-like local candidates before any validation claim `[testing_tuning,
  p.327-335]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## 2026-05-15 B4-Like No-Margin Local Pareto Search

After clarifying that external margin is not available, the same local search was run
with `--no-margin`, writing to `results/local_pareto_b4_no_margin/`. This mode requires
`CASHX >= 0` and gross weight `1.0`; stacked exposure can still exist inside ETFs like
`GDESIM`/`RSSTSIM`, but the portfolio itself does not borrow through negative cash.

No-margin grid: `37,752` rows, `37,476` feasible rows, `272` Pareto rows. Key reading:

- Top Calmar defensive row: `10% CASHX / 15% GDESIM / 45% IEFSIM / 25% KMLMSIM /
  5% SPYSIM`, CAGR `7.86%`, MDD `-8.76%`, Calmar `0.896`; too defensive for a
  SPY-beater objective.
- Highest-CAGR feasible no-margin row: `35% GDESIM / 40% RSSTSIM / 25% ZROZSIM`,
  CAGR `15.70%`, MDD `-29.94%`, Calmar `0.524`, terminal wealth `265x`, rolling 5y
  CAGR p10 `8.71%`, rolling 5y relative-wealth p10 vs `SPYSIM` `-8.59%`.
- Compared with the margin/stacked-cash result (`17.35%`, MDD `-30.44%`), removing
  negative `CASHX` costs about `1.65pp` CAGR but preserves the same approximate MDD
  band. This no-margin row is the current practical B4-like local lead, still
  discovery-only and blocked by negative relative-wealth p10; next step is exact
  Pareto/regime report on top no-margin candidates `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## 2026-05-15 Exact Pareto/Regime Update With No-Margin Lead

`results/pareto_regime_report/` was regenerated with `B4_no_margin_lead` included and
rolling summaries extended to 15y. Direct comparison:

- `B4_no_margin_lead` (`35% GDESIM / 40% RSSTSIM / 25% ZROZSIM`): CAGR `15.70%`,
  MDD `-29.94%`, Calmar `0.524`, terminal wealth `265x`, gross `1.0`, no negative
  `CASHX`.
- `B4_original` (`25% NTSXSIM / 25% GDESIM / 25% RSSTSIM / 25% ZROZSIM`): CAGR
  `14.43%`, MDD `-27.92%`, Calmar `0.517`, terminal wealth `174x`.
- Interpretation: the no-margin lead adds `+1.27pp` CAGR and materially higher
  terminal wealth at the cost of about `2.02pp` worse MDD; Calmar is slightly higher.
  Rolling relative-wealth p10 vs `SPYSIM` improves versus B4 original across 3y/5y/10y
  and 15y, but remains negative at 3y (`-9.84%`), 5y (`-8.59%`) and 10y (`-4.25%`),
  turning positive only at 15y (`+12.88%`).
- Regimes: no-margin lead beat SPY wealth in all named regimes and beat B4 original in
  GFC, inflation shock and recent recovery, but B4 original was slightly better in
  dot-com, QE bull and Covid crash. Status remains discovery-only; next step is
  no-margin implementation/sensitivity checks (start dates, rebalance frequency, drag,
  remove-one-asset) before walk-forward selection `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

## 2026-05-15 Core-Beater Pivot + GA Smoke

The study objective pivoted from beating `SPYSIM`/B4-like references to beating the
new no-margin core benchmark: `35% GDESIM / 40% RSSTSIM / 25% ZROZSIM`. This core is
the internal benchmark, not a validated winner or deployment instruction. MDD is now
treated as a guardrail/penalty; the primary objective is rolling equity dominance:
candidate terminal wealth should exceed core terminal wealth across as many rolling
1/3/5/10/15/20y monthly windows as possible, with emphasis on 5y+ p10 and win-rate
`[testing_tuning, p.327-335]`.

Implementation changes:

- `README.md` now mentions `studies/static_spy_beater_portfolio/` and the `35/40/25`
  core as discovery-only.
- `SPEC.md` and `NEXT_STEPS.md` now define the core-beater objective.
- `universe.py` added `core_beater_no_margin`:
  `GDESIM, RSSTSIM, KMLMSIM, ZROZSIM, SPYSIM, SSOSIM, UPROSIM, QQQSIM, QLDSIM,
  TQQQSIM, IEFSIM, CASHX`.
- `score_portfolio.py` added `core_35_40_25` benchmark metrics, rolling
  `wealth_core_ratio_minus1`, `wealth_core_win`, `cagr_core_spread`,
  `mdd_minus_core_mdd`, `calmar_core_spread`, and fitness
  `core_relative_wealth_dominance`.

Smoke run:

`results/ga_smoke_core/core_beater_no_margin_core_relative_wealth_dominance_seed20260535/`
validated the new pipeline with pop `18`, gens `3`, max assets `10`, rolling step
`252`, exact top-3 rerank. The smoke evaluated `58` unique portfolios and found no
candidate beating the core; top exact had CAGR `15.30%`, MDD `-59.91%`, and fitness
`-1.446`. This is infrastructure-only, not evidence against the hypothesis. Next run
should use a serious population/generation budget and monthly sampled rolling windows
with exact rerank `[advances_fin_ml, p.222-223]`.

## 2026-05-16 Factor/Momentum Core-Beater Probe

`core_beater_factor_no_margin` was added as a discovery-only universe extending the
no-margin core-beater set with factor proxies `VBRSIM`, `MTUMSIM` and `EFVSIM`.
`MTUMSIM` was pulled into the local Testfol.io cache; the common factor-universe window
is `1994-06-02..2026-04-17` with `8,023` aligned rows. Factor sleeves are only
candidates; the benchmark remains `35% GDESIM / 40% RSSTSIM / 25% ZROZSIM`
`[ml_for_algo_trading, ch.4 p.82-93]`, `[testing_tuning, p.327-335]`.

Sweep `results/ga_core_factor_momentum_beater/` ran 3 seeds (`20260542..20260544`),
population `160`, generations `120`, `rolling_step=21`, exact top-100 rerank. All
three seeds converged back to the core as exact rank 1 with fitness `0.350000`.
Best non-core challengers were levered-equity tilts, not factor sleeves:

- `35% GDESIM / 35% RSSTSIM / 25% ZROZSIM / 5% QLDSIM`: CAGR `15.996%`, MDD
  `-37.31%`, fitness `0.133988`.
- `35% GDESIM / 40% RSSTSIM / 20% ZROZSIM / 5% QLDSIM`: CAGR `16.51%`, MDD
  `-40.04%`, fitness `0.098955`.
- Best visible `VBRSIM` rows were around fitness `0.084` or lower; `MTUMSIM` did not
  survive into top-10 exact rows.

Interpretation: small-value and momentum proxies did not improve rolling equity
dominance versus the core in this GA. The result supports keeping `35/40/25` as the
static benchmark and moving to implementation/sensitivity checks rather than forcing a
factor sleeve overfit. Status remains discovery-only; no winner/deploy and no mandate
change `[advances_fin_ml, p.222-223]`.

## 2026-05-16 Final Core Report

`FINAL_REPORT_35_40_25_CORE.md` consolidates the study around the internal research
winner `35% GDESIM / 40% RSSTSIM / 25% ZROZSIM`. The report focuses on why this
no-margin core beat B4 original and SPY on the relevant full-period trade-off, why
negative-cash, levered-equity and factor/momentum challengers were rejected, and why
the next step should be implementation realism rather than more broad static
optimization. It is explicitly discovery-only: no deploy authorization and no mandate
change `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

## 2026-05-19 Stacked-ETF Expansion Triage

Built 8 local composition proxies (`scripts/build_stacked_sim_proxies.py`) for stacked
ETFs absent from Testfol.io's native SIM catalog: CTAPSIM, RSBTSIM, RSITSIM, HOLDSIM,
MATESIM, ESBGSIM, GDTSIM, ALLWSIM. Formula: weighted daily returns of cached components
minus financing (excess leverage × CASHX). Also pulled 8 native Testfol.io tickers
(STIPSIM, GSGSIM, LTPZSIM, BTALSIM, NTSXSIM, NTSDSIM, NTSISIM, IEISIM). Parquet now at
46 columns.

**Proxy bias sanity check:** the formula `SPYSIM + DBMFSIM - 1.0×CASHX` against real
`RSST` (2023-09 to 2026-04) gives CAGR 25.54% vs real 19.98% — proxy **overestimates by
5.56pp**. Same bias likely applies to all 8 proxies. Discovery-only, not validation-grade
`[testing_tuning, p.327-335]`.

New universe `core_beater_stacked_expansion` (21 tickers: anchors + 8 proxies + RSSB +
NTSXSIM/NTSISIM/NTSDSIM + BTAL + DBMF + KMLM + IEISIM + IEFSIM + CASHX). Common window
2003-01-03..2026-04-17 (5859 bars, binding ALLWSIM/GDTSIM 2003+).

GA triage 3 seeds (`20260519/20260520/20260521`), pop 120, gens 80, max_assets 8,
fitness `core_relative_wealth_dominance`, fast-discovery, finalist exact top-80:

- **Core `35/40/25` fitness: 0.3500.** GA best across all seeds: `0.2681` (seed 20260521:
  `30 RSST / 25 ESBG / 20 GDE / 15 ZROZ / 5 CTAP / 5 MATE`). Delta `-0.0819` — **core
  survived again**.
- All seeds converged on similar structure: anchors retained (GDE 15-35%, RSST 15-30%,
  ZROZ 15%), with ESBGSIM tilt 10-30% in every top-5 and small CTAPSIM/MATESIM accents.
- Sleeves NEVER selected into any seed's top-5: RSBTSIM, RSITSIM, HOLDSIM, ALLWSIM,
  GDTSIM, BTALSIM, NTSXSIM, NTSDSIM, NTSISIM, RSSBSIM, KMLMSIM, DBMFSIM, IEISIM,
  IEFSIM, CASHX.
- GA candidates achieve `+0.79pp` CAGR over core but cost `+2.95pp` worse MDD and
  `-0.026` Calmar, with negative rolling p10 dominance — net negative fitness.

Interpretation: stacked-ETF expansion does NOT beat the 35/40/25 core. This is the
4th distinct GA challenge the core has resisted (after levered-equity, factor/momentum,
no-margin Pareto, and now stacked-ETF). Status: discovery-only, mandate §1 unchanged.
Report: `results/ga_b4v2_stacked_triage/REPORT.md` `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.222-223]`.
