# EMA/SMA Threshold Crossover — REAL SPY data (Tiingo)

> Real-ETF validation of the SPYSIM synth study. Buy leg uses actual UPRO/SSO/SPY returns from Tiingo. Sell leg with L<0 uses synth inverse of real SPY (inverse LETFs not cached).

## Contents
- `SPEC.md` — spec aligned with the synth study.
- `FINAL.md` — top-20 ranked (pure + tax15) + narrative.
- `configs.csv` — every config's metrics + gates.
- `summary.json` — axes + top-K machine-readable.
- `configs/NN_<cfg_id>/` — per-config: summary.md, equity.png, trades.csv.
- `analyses/` — supplementary studies (equity-vs-benchmark, rolling windows).

## Usage
```bash
.venv/bin/python studies/ema_sma_threshold_spy_real/run_sweep.py
.venv/bin/python studies/ema_sma_threshold_spy_real/run_sweep.py --smoke
```

Data source: `data/tiingo/daily/prices/` (SPY, SSO 2006+, UPRO 2009+). Effective start: 2009-06-26 due to UPRO inception.
