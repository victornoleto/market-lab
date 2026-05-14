# SPEC — success_trading_strat

## Mission

Find an efficient trading strategy using the development discipline from
Neurotrader's video `NLBXgSmRBgU` plus this repository's book-cited validation
stack.

This is research only. It does not authorize capital allocation, and it does not
override the project mandate: capital remains 100% Plano C unless a future human
mandate override says otherwise.

## Source Method

The video's four-step workflow is promoted to study protocol:

1. In-sample excellence: the strategy should be economically strong before any
   validation data are consumed.
2. In-sample Monte Carlo permutation test: re-run the full optimization process
   on permuted data and require the real result to sit in the extreme right tail.
3. Walk-forward test: simulate retraining/reselection on past data and adjacent
   unseen data.
4. Walk-forward Monte Carlo permutation test: permute the post-initial-training
   region and compare the real walk-forward result against the null distribution.

Masters provides the book basis for MCPT, walk-forward, guard buffers and
best-of-many selection-bias adjustment `[testing_tuning, p.143-144]`,
`[testing_tuning, p.148-150]`, `[testing_tuning, p.318-320]`,
`[testing_tuning, p.327-335]`.

## Validation Gates

A candidate is not a winner unless all applicable gates pass:

| gate | pass condition | citation |
|---|---|---|
| IS MCPT | `p <= 0.01` when feasible; early smoke may use fewer reps but cannot promote | `[testing_tuning, p.318-320]` |
| WF MCPT | `p <= 0.05` for short windows, preferred `p <= 0.01` for 2+ years | `[testing_tuning, p.318-320]` |
| PBO | `< 0.5` | `[advances_fin_ml, p.208-211]` |
| DSR | `p < 0.05` using cumulative trials | `[advances_fin_ml, p.222-223]` |
| Walk-forward | at least 6/8 windows positive | `[testing_tuning, p.148-150]` |
| OOS | single holdout positive | `[advances_fin_ml, p.196-202]` |
| FWD stress | recent forward/stress window positive | `[advances_fin_ml, p.196-202]` |
| Bootstrap | 99.9% CI low > 0 | `[testing_tuning, p.246-247]` |
| Cross-lib | CAGR within +/-3pp where feasible | `[advances_fin_ml, p.31-34]` |

If a gate cannot be computed in an early infrastructure iteration, the verdict is
`infrastructure_only` or `promising_not_validated`, never `winner`.

## Data Priority

The first phase is data preservation because the Tiingo subscription is expiring.
Iteration 001 audits and backs up local data before strategy optimization.

Primary local cache: `data/tiingo/`.

Critical coverage groups:

- S&P 500 and Nasdaq-100 constituents;
- broad US/index ETFs (`SPY`, `QQQ`, `IWM`, `DIA`, `VTI`);
- LETFs (`SSO`, `QLD`, `UPRO`, `TQQQ`, `SOXL`);
- semis/AI/crypto-linked ETFs (`SMH`, `SOXX`, `XSD`, `SOXQ`, `DRAM`, `AIS`, `POW`, `IBIT`, `ETHA`);
- bonds/defensives/commodities (`TLT`, `IEF`, `AGG`, `SHV`, `GLD`, `SLV`, `USO`, `VXX`);
- crypto and FX/metal pairs.

## Trial Accounting

Every tested config increments `cumulative_n_trials` in `MEMORY.md`. MCPT
permutations are reported separately as validation effort; strategy/config trials
feed DSR and selection-bias accounting `[advances_fin_ml, p.222-223]`.

## Winner Definition

`winner = true` only if all hold:

- economically beats the pre-registered benchmark on the same data window;
- IS MCPT and WF MCPT pass;
- PBO, DSR, WF, OOS, FWD, bootstrap and cross-lib pass;
- no known lookahead/data-window caveat invalidates the result;
- reproducible from saved iteration scripts.

## Kill Rules

- Do not continue local tuning after a family fails MCPT/PBO/DSR without a new
  mechanism.
- Do not promote a candidate that only works after shortening to a favorable
  modern window.
- Do not use validation/OOS results to redesign the same iteration.
- Do not treat testfolio, Tiingo or any single source as final without an audit
  of date range and execution lag.
