# LETF rotation studies migrated to letf-lab

On **2026-05-23** the LETF (leveraged-ETF) rotation research was fully
extracted into a dedicated sibling repository at
`/var/www/victor/finances/letf-lab` so it can power a signal-monitoring
webapp (Angular 21 + FastAPI) on top of the existing CLI workbench.

## Studies removed from market-lab (canonical now in letf-lab)

- `studies/lrs/`                          → `letf-lab/studies/lrs/`
- `studies/letf_rotation_hunt/`           → `letf-lab/studies/letf_rotation_hunt/`
- `studies/spy_leveraged_rotation_hunt/`  → `letf-lab/studies/spy_leveraged_rotation_hunt/`

Plus the LETF-specific test files:

- `tests/test_studies_lrs_indicators.py` (was untracked; existed in working tree)
- `tests/test_studies_lrs_voting.py`     (was untracked)
- `tests/test_studies_lrs_ga.py`         (was untracked)
- `tests/test_letf_rotation_hunt_loop_{002,003,004,005,006,007,008,010,011,012,015,022}.py` (12 files; tracked)

## Helpers extracted from `letf_rotation_hunt/core/` to shared market-lab locations

Several non-LETF studies (`technical_signal_vote_hunt`, `success_trading_strat`,
`weekly_momentum`, `spy_beater_hunt_v2`) imported individual helpers from
`studies.letf_rotation_hunt.core.*`. Those helpers were moved to canonical
shared locations so the non-LETF code keeps working after the deletion:

| Original | New canonical location |
|---|---|
| `studies/letf_rotation_hunt/core/signals.py` | `studies/_shared/signals.py` |
| `studies/letf_rotation_hunt/core/scoring.py` | `studies/_shared/scoring.py` |
| `studies/letf_rotation_hunt/core/plot_helper.py` | `studies/_shared/plot_helper.py` |
| `studies/letf_rotation_hunt/core/gates.py` | `studies/_shared/gates_letf.py` |
| `studies/letf_rotation_hunt/core/data_loader_yields.py` | `src/market_lab/backtest/data/yields.py` |

## Import rewrites (20 files in 4 non-LETF studies)

| Old import | New import |
|---|---|
| `from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series` | `from market_lab.backtest.data.testfolio_loader import load_testfolio_series` |
| `from studies.letf_rotation_hunt.core.signals import ar1_coefficient, realized_vol_gate, sma_gate, vote_of_k` | `from studies._shared.signals import ar1_coefficient, realized_vol_gate, sma_gate, vote_of_k` |
| `from studies.letf_rotation_hunt.core.data_loader_yields import load_constant_maturity_yield, load_dividend_yield` | `from market_lab.backtest.data.yields import load_constant_maturity_yield, load_dividend_yield` |
| `from studies.letf_rotation_hunt.core.scoring import compute_metrics` | `from studies._shared.scoring import compute_metrics` |

Files rewritten:

- 16 in `studies/technical_signal_vote_hunt/{runners,webapp}/`
- 11 in `studies/spy_beater_hunt_v2/iterations/*/` and `reports/`
- 1 in `studies/success_trading_strat/iters/phase01/019-2026-05-14-yield-carry-rotation/`
- 1 in `studies/weekly_momentum/core.py`

## Residual dead path strings (not removed)

8 files in `studies/technical_signal_vote_hunt/runners/` still contain
hard-coded `Path` constants that reference the deleted
`studies/letf_rotation_hunt/runs/post_close/030-2026-05-10-tcrash-scan-lrs120-rearmonly/`
directory (the iter-030 canonical artifacts) and the never-tracked
strategy_returns CSVs from iter-022 and iter-030.

These scripts were used for cross-strategy benchmarking against
iter-030 / iter-022 results. They now fail at **runtime** when invoked
(not at import time), because the referenced files no longer exist in
market-lab. The canonical copies live in
`letf-lab/studies/letf_rotation_hunt/runs/post_close/030-.../backtest.py`
(plus their plots + SUMMARY.md). The CSV files were always gitignored
and only existed transiently when the backtests were re-run.

If you want to revive those benchmarks, point the `Path` constants at
the letf-lab copies (cross-repo path) or copy the artifacts back to
market-lab under `studies/technical_signal_vote_hunt/_canonical/`.

Affected files:

- `compare_stage4_testfolio.py`
- `compare_stage4_equity.py`
- `run_iter030_td_sensitivity.py`
- `run_iter030_param_ga.py`
- `run_stage4_hybrid_ga.py`
- `run_stage4_inside_iter030.py`
- `run_stage4_pareto_hybrid_search.py`
- `run_repair_ga_evolutions.py`

## What still stays in market-lab (shared infra, not LETF research)

- `src/market_lab/backtest/strategies/letf_rotation.py` — still imported by
  `studies/spy_beater_hunt_v2/iterations/*` for cross-strategy comparisons.
- `src/market_lab/backtest/helpers/synthetic_letf.py` — referenced by
  `tests/cross_lib/`, `spx_tr_loader.py`, `testfolio_loader.py`.
- `src/market_lab/backtest/grid/{letf_rotation_b1c,real_etf_*,ema_sma_threshold_grid}.py`
  — used by `spy_beater_hunt(_v2)` and `global_factor_tilt_loop`.
- `studies/_shared/` — used by `spy_beater_hunt/tax_layer.py`,
  `weekly_momentum/scripts/validate_candidates.py`, and the helpers
  added in this migration (signals, scoring, plot_helper, gates_letf).

## Validation

- letf-lab: `uv run pytest tests/` → 279/279 passing.
- letf-lab: `uv run python -m studies.lrs.phases.phase_10_portfolio.run`
  → EQ5_3x CAGR=31.21%, PBO=0.041, bootstrap_mean=0.306, WF=5/6
  (identical to market-lab pre-migration numbers in CLOSING_SUMMARY.md).
- market-lab: `uv run pytest tests/ --ignore=tests/cross_lib --ignore=tests/myfxbook`
  → 754 passed, 19 failed (pre-existing failures unrelated to this
  migration: missing TLTSIM in testfolio cache; long_term_portfolio
  synths cache misses). Down from 24 failed before cleanup because the
  12 deleted loop tests had 5 pre-existing failures of their own.
- Smoke test: all 4 non-LETF consumer studies import cleanly after the
  rewrites.

## How to use letf-lab

```bash
cd /var/www/victor/finances/letf-lab
cat SETUP.md            # 15-section step-by-step install/run guide
cat REFACTOR-REPORT.md  # spin-off history + commits + architecture
```

CLI workbench preserves the market-lab ergonomics:

```bash
uv run python -m studies.lrs.phases.phase_10_portfolio.run
uv run pytest tests/
```

Plus a FastAPI + Angular 21 webapp that monitors strategies, generates
daily signals, and emails swing alerts (Resend / SMTP / console backends).
