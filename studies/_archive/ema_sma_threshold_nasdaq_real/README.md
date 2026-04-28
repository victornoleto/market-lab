# EMA/SMA Threshold Crossover — REAL NASDAQ-100 (Tiingo)

> Real-ETF replication of the SPY study on QQQ. Buy leg uses actual TQQQ/QLD/QQQ returns from Tiingo. Sell leg with L<0 uses synth inverse of real QQQ (inverse LETFs not cached).

## Contents
- `SPEC.md` — spec aligned with the SPY-real study.
- `FINAL.md` — top-20 ranked (pure + tax15) + narrative.
- `configs.csv` — every config's metrics + gates.
- `summary.json` — axes + top-K machine-readable.
- `configs/NN_<cfg_id>/` — per-config: summary.md, equity.png, trades.csv.
- `analyses/` — supplementary studies.

## Usage
```bash
.venv/bin/python studies/ema_sma_threshold_nasdaq_real/run_sweep.py
```

Data source: `data/tiingo/daily/prices/` (QQQ 2001+, QLD 2006+, TQQQ 2010+). Effective start: 2010-02-12 due to TQQQ inception.
