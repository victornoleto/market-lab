# AUDUSD_NZDUSD 1h — T3 cointegration pair-trade

**Legs:** Y=`audusd` / X=`nzdusd` | **Asset class:** forex
**Window:** 2020-01-06 → 2026-04-14 (38523 aligned bars, 1h)
**Costs:** half_spread=2.0bps/leg, swap=0.0050%/day/leg, commission=$3.5/side

**Best config:** `ols_z2_exit0` — **NO PASS**

## Cointegration (IS 2020-2023)
- Engle-Granger ADF stat: **-3.1023** | p-value: **0.0019** | Cointegrated @ 5%: **✓**

## Cross-config gates
- PBO across 3 configs: **0.8016** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | Coint | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `ols_z2_exit0` | -1.70 | -4.01 | -8.28 | 188 | 0.31 | 1.000 | 0/8 | ✓ | ✗ | ✗ | ✓ | **fail** |
| `kalman_z2_exit0` | -2.63 | -4.62 | -9.79 | 156 | 1.65 | 1.000 | 0/8 | ✓ | ✗ | ✗ | ✓ | **fail** |
| `kalman_z2_exit0p5` | -3.27 | -5.05 | -10.19 | 178 | 0.92 | 1.000 | 0/8 | ✓ | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### ols_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38523 | -1.71 | -3.89 | -23.30 | 497 | 1.33 |
| IS | 2020-01-06 | 2023-12-31 | 24329 | -1.74 | -3.92 | -15.67 | 298 | 1.69 |
| OOS | 2024-01-01 | 2025-12-31 | 12439 | -1.70 | -4.01 | -8.28 | 188 | 0.31 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -1.31 | -2.45 | -1.45 | 11 | 4.58 |

### kalman_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38523 | -1.82 | -3.69 | -21.85 | 445 | 1.92 |
| IS | 2020-01-06 | 2023-12-31 | 24329 | -1.54 | -3.33 | -13.31 | 276 | 1.94 |
| OOS | 2024-01-01 | 2025-12-31 | 12439 | -2.63 | -4.62 | -9.79 | 156 | 1.65 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -1.01 | -1.92 | -1.52 | 13 | 3.88 |

### kalman_z2_exit0p5

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38523 | -2.24 | -4.05 | -23.47 | 512 | 1.12 |
| IS | 2020-01-06 | 2023-12-31 | 24329 | -1.91 | -3.72 | -14.49 | 317 | 1.33 |
| OOS | 2024-01-01 | 2025-12-31 | 12439 | -3.27 | -5.05 | -10.19 | 178 | 0.92 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -0.80 | -1.35 | -1.56 | 17 | 1.58 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-18.63%** | IR: **-0.983** | Corr: **-0.052** | Beta: **-0.006**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Engle-Granger cointegration (ADF on OLS residuals): `[algo_trading_chan, p.42-54, ch.2]`
- Bollinger-band pair-trade entry/exit: `[algo_trading_chan, p.71-73, ch.3]`
- Kalman dynamic hedge-ratio δ=1e-4, Ve=1e-3: `[algo_trading_chan, p.75-80, ch.3]`
- KF state-space overfit warning (EWA-EWC): `[machine_trading, p.76-79, ch.3]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
