# LETF rotation studies migrated to letf-lab

On **2026-05-23** the LETF (leveraged-ETF) rotation research was extracted
into a dedicated sibling repository at `/var/www/victor/finances/letf-lab`
so it can power a signal-monitoring webapp (Angular 21 + FastAPI) on top
of the existing CLI workbench.

## What moved (canonical now in letf-lab)

- `studies/lrs/`                          → `letf-lab/studies/lrs/`
- `studies/spy_leveraged_rotation_hunt/`  → `letf-lab/studies/spy_leveraged_rotation_hunt/`

Plus the LETF-specific test files (3 in `tests/`):

- `tests/test_studies_lrs_indicators.py`
- `tests/test_studies_lrs_voting.py`
- `tests/test_studies_lrs_ga.py`

## What stays here (cross-deps from other non-LETF studies)

### `studies/letf_rotation_hunt/`

Restored in market-lab because **4 non-LETF studies depend on individual
helpers** from `studies/letf_rotation_hunt/core/`:

- `studies/spy_beater_hunt_v2/iterations/*/run_*.py` (11 files) — imported
  `core/data_loader.load_testfolio_series`. **Rewritten on 2026-05-23 to
  use the canonical path `market_lab.backtest.data.testfolio_loader`**
  (the wrapper was a trivial passthrough).
- `studies/technical_signal_vote_hunt/runners/*.py` and `webapp/*.py` —
  import `core/data_loader.load_testfolio_series` AND
  `core/signals.{ar1_coefficient, realized_vol_gate, sma_gate, vote_of_k}`.
  The signal helpers stay here as live dependencies.
- `studies/success_trading_strat/iters/phase01/019-2026-05-14-yield-carry-rotation/run_iter019.py`
  imports `core/data_loader_yields`.
- `studies/weekly_momentum/core.py` imports `core/scoring.compute_metrics`.

The canonical research artifact + all 17 LRS phases now live in
**`letf-lab/studies/letf_rotation_hunt/`**. The copy here in market-lab
remains as **shared infrastructure** for the non-LETF studies above.

### Shared backtest infrastructure

- `src/market_lab/backtest/strategies/letf_rotation.py` — still imported by
  `studies/spy_beater_hunt_v2/iterations/*` and `studies/spy_beater_hunt/`
  for cross-strategy comparisons.
- `src/market_lab/backtest/helpers/synthetic_letf.py` — referenced by
  `tests/cross_lib/`, `spx_tr_loader.py`, `testfolio_loader.py`.
- `src/market_lab/backtest/grid/{letf_rotation_b1c,real_etf_*,ema_sma_threshold_grid}.py`
  — used by `spy_beater_hunt(_v2)` and `global_factor_tilt_loop`.
- `studies/_shared/` — used by `spy_beater_hunt/tax_layer.py` and
  `weekly_momentum/scripts/validate_candidates.py`.

These can be revisited later if those non-LETF studies are also retired
or refactored to remove the dependency.

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
