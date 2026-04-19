# EURUSD_GBPUSD 1h — T3 cointegration pair-trade

**Legs:** Y=`eurusd` / X=`gbpusd` | **Asset class:** forex
**Window:** 2020-01-06 → 2026-04-14 (38632 aligned bars, 1h)
**Costs:** half_spread=2.0bps/leg, swap=0.0050%/day/leg, commission=$3.5/side

**Best config:** `ols_z2_exit0` — **NO PASS**

## Cointegration (IS 2020-2023)
- Engle-Granger ADF stat: **-2.4947** | p-value: **0.0122** | Cointegrated @ 5%: **✓**

## Cross-config gates
- PBO across 3 configs: **0.9048** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | Coint | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `ols_z2_exit0` | -1.95 | -3.75 | -7.81 | 154 | 1.29 | 0.999 | 0/8 | ✓ | ✗ | ✗ | ✓ | **fail** |
| `kalman_z2_exit0` | -2.69 | -4.67 | -9.61 | 165 | 0.96 | 0.997 | 1/8 | ✓ | ✗ | ✗ | ✓ | **fail** |
| `kalman_z2_exit0p5` | -3.05 | -4.77 | -9.81 | 179 | 0.83 | 1.000 | 1/8 | ✓ | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### ols_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38632 | -1.27 | -3.58 | -22.74 | 475 | 1.50 |
| IS | 2020-01-06 | 2023-12-31 | 24436 | -1.16 | -3.75 | -16.01 | 305 | 1.29 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -1.95 | -3.75 | -7.81 | 154 | 1.29 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -0.05 | -0.09 | -0.84 | 16 | 2.94 |

### kalman_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38632 | -1.11 | -2.81 | -17.24 | 510 | 1.25 |
| IS | 2020-01-06 | 2023-12-31 | 24436 | -0.58 | -1.70 | -7.53 | 314 | 1.77 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -2.69 | -4.67 | -9.61 | 165 | 0.96 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.31 | -4.78 | -1.47 | 31 | 0.67 |

### kalman_z2_exit0p5

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38632 | -1.58 | -3.64 | -21.18 | 560 | 1.00 |
| IS | 2020-01-06 | 2023-12-31 | 24436 | -1.10 | -2.93 | -11.62 | 348 | 1.08 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.05 | -4.77 | -9.81 | 179 | 0.83 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -4.14 | -5.38 | -1.61 | 33 | 0.58 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-18.32%** | IR: **-0.952** | Corr: **-0.107** | Beta: **-0.015**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Engle-Granger cointegration (ADF on OLS residuals): `[algo_trading_chan, p.42-54, ch.2]`
- Bollinger-band pair-trade entry/exit: `[algo_trading_chan, p.71-73, ch.3]`
- Kalman dynamic hedge-ratio δ=1e-4, Ve=1e-3: `[algo_trading_chan, p.75-80, ch.3]`
- KF state-space overfit warning (EWA-EWC): `[machine_trading, p.76-79, ch.3]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
