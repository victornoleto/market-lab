# EMA/SMA Threshold Crossover — Educational Study

> Educational sweep on SPY with leveraged ETFs. Not a production strategy. Project mandate remains 100% Plano C (MAINTENANCE §1).

## Contents

- **`SPEC.md`** — full specification with citations.
- **`run_sweep.py`** — CLI to regenerate all artifacts.
- **`FINAL.md`** — ranked top-20 strategies + narrative.
- **`configs.csv`** — every config's metrics + gates.
- **`summary.json`** — machine-readable axes + top-20.
- **`configs/NN_<cfg_id>/`** — per-config deep-dives:
  - `summary.md` — metrics pure + tax15 vs SPY + gate breakdown.
  - `equity.png` — equity path vs SPY buy-hold (log scale).
  - `trades.csv` — regime-block ledger (pure + tax15 side-by-side).

## Usage

```bash
# Default: 384 configs x 2 tax regimes, top-20 per-config outputs (~12-15 min)
.venv/bin/python studies/ema_sma_threshold_educational/run_sweep.py

# Smoke (8 configs, ~1 min)
.venv/bin/python studies/ema_sma_threshold_educational/run_sweep.py --smoke

# Full grid (1512 configs, ~30-40 min)
.venv/bin/python studies/ema_sma_threshold_educational/run_sweep.py --full
```

Data source: `data/testfolio/cache/history.parquet` ticker `SPYSIM` (1986-2026, S&P 500 total return proxy, modelled). See `SPEC.md` for details.
