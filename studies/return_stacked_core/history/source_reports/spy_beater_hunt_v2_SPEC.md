# SPEC — spy_beater_hunt_v2

## Mission

Find one long-term strategy that:

1. Beats SPY buy-and-hold on long-term CAGR.
2. Survives hard overfit gates: PBO, DSR, walk-forward, OOS, forward stress,
   bootstrap and cross-library checks `[advances_fin_ml, p.196-202]`,
   `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

This is a research study. It does not authorize capital allocation.

## Benchmark

Primary benchmark: SPY buy-and-hold over the same date range and data source as
the candidate. When long-history synthetic data are available, prefer 1986+ or
longer testfolio history before relying on Tiingo real-inception windows.

Minimum benchmark fields per iteration:

- CAGR
- MDD
- Sharpe and/or Sortino
- terminal equity ratio candidate/SPY
- rolling 3y/5y/10y CAGR win rates vs SPY

## Hard Gates

A candidate is not a winner unless all applicable hard gates pass:

| gate | pass condition | citation |
|---|---|---|
| PBO | `< 0.5` | `[advances_fin_ml, p.208-211]` |
| DSR | `p < 0.05` using cumulative trials | `[advances_fin_ml, p.222-223]` |
| Walk-forward | at least 6/8 windows positive | `[testing_tuning, ch.12]` |
| OOS | single holdout positive | `[advances_fin_ml, p.196-202]` |
| FWD stress | recent forward/stress window positive | `[advances_fin_ml, p.196-202]` |
| Bootstrap | 99.9% CI low > 0 | `[advances_fin_ml, p.196-202]` |
| Cross-lib | CAGR within +/-3pp where feasible | `[advances_fin_ml, p.31-34]` |

If a gate cannot be computed in an early infrastructure iteration, the result is
`infrastructure_only` or `inconclusive`, never `winner`.

## Trial Accounting

Every tested config increments `cumulative_n_trials` in `MEMORY.md`. DSR claims
must use the global cumulative count, not only the current iteration
`[advances_fin_ml, p.222-223]`.

## Winner Definition

`winner = true` only if all conditions hold:

- candidate CAGR > SPY CAGR on the primary long-history panel;
- terminal equity ratio candidate/SPY > 1.0;
- PBO < 0.5;
- DSR p < 0.05 using cumulative trials;
- WF/OOS/FWD/bootstrap pass;
- no documented lookahead or data caveat invalidates the result;
- result is reproducible by the saved iteration script.

## Kill Rules

- If a family fails DSR/PBO after an honest top-k validation, do not continue
  local threshold/grid tuning in the same family without a new mechanism.
- If a candidate only wins after shortening the window to a favorable modern
  regime, mark it `modern_regime_only`, not winner.
- If extra signal lag collapses CAGR, treat the lead as execution-sensitive and
  require independent timing audit before further optimization.
- If the strategy depends on unavailable or undocumented data, mark it
  `data_blocked`.

## Initial Scope

Iteration 001 should be an audit/bootstrap iteration:

- inventory reusable runners and data;
- compute or locate SPY benchmark baselines;
- identify prior dead-end clusters to avoid;
- propose the first 2-3 citable hypothesis families.

It should not optimize a strategy unless the audit is already complete inside
the same small scope.
