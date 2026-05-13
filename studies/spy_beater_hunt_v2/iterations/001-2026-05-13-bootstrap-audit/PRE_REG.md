# PRE_REG — 001-bootstrap-audit

## Hypothesis

This is an infrastructure-only bootstrap/audit iteration. The hypothesis is that
the repo already contains enough long-history data, benchmark tooling and hard
validation primitives to support later `spy_beater_hunt_v2` strategy iterations
without broad refactor. No strategy winner can be declared from this iteration.

Rationale: auditability and trial accounting must precede backtest-driven
research; every result must report all trials involved `[advances_fin_ml, p.276]`,
and PBO/DSR require ex-ante trial accounting `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

## Exact Configs

- Strategy configs tested: none.
- Benchmark config: SPYSIM buy-and-hold, daily returns from the repository
  testfolio cache when available.
- Audit inventory scope: reusable data loaders, validation modules, available
  SPY/QQQ/LETF/defensive long-history series, and prior-family dead ends.

## Data And Window

- Primary source: `data/testfolio/cache/history.parquet`, accessed through
  `studies.letf_rotation_hunt.core.data_loader.load_testfolio_series`.
- Primary benchmark ticker: `SPYSIM`.
- Secondary inventory tickers if present: `QQQSIM`, `QLDSIM`, `TQQQSIM`,
  `ZROZSIM`, `CASHX`, `GLDSIM`, `NTSX`, `GDE`, `RSST`, `KMLMSIM`.
- Date range: full available overlap per series; no truncation except per-series
  availability reporting.

## Planned Gates

- PBO: not computed; no strategy panel and `n_trials=0` `[advances_fin_ml, p.208-211]`.
- DSR: not computed; no candidate returns and `n_trials=0` `[advances_fin_ml, p.222-223]`.
- Walk-forward/OOS/FWD/bootstrap/cross-lib: not computed for a strategy; audit
  only confirms reusable modules and reports whether SPY benchmark metrics can
  be computed `[advances_fin_ml, p.196-202]`.

## Kill Rules

- If `SPYSIM` cannot be loaded honestly, mark `data_blocked` and do not proceed
  to strategy testing.
- If validation modules are absent or import-broken, mark `infrastructure_only`
  with blockers.
- If only short modern real-inception data are available, record that future
  iterations must avoid winner claims until long-history validation is possible.
- Do not optimize or test any candidate family in iteration 001.

## Trial Accounting

- `cumulative_n_trials_before`: 0
- `n_trials_this_iteration`: 0
- `cumulative_n_trials_after`: 0
