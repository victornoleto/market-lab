---
mission: "Find robust static monthly-rebalanced ETF portfolios that beat SPYSIM"
status: bootstrap_smoke_complete
active_phase: 1
latest_run: "core_1986_balanced_spy_beater_seed7"
latest_status: "smoke_only"
latest_best_config: "CASHX 5 / GDESIM 20 / GLDSIM 5 / QLDSIM 5 / RSSBSIM 10 / SSOSIM 5 / TMFSIM 5 / TQQQSIM 15 / UGLSIM 5 / VTISIM 5 / VTSIM 10 / ZROZSIM 10"
latest_best_score: 0.109503
cumulative_n_trials: 7
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
