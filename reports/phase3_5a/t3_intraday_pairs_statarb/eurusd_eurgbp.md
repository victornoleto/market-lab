# EURUSD_EURGBP 1h — T3 cointegration pair-trade

**Legs:** Y=`eurusd` / X=`eurgbp` | **Asset class:** forex
**Window:** 2020-01-06 → 2026-04-14 (38564 aligned bars, 1h)
**Costs:** half_spread=2.0bps/leg, swap=0.0050%/day/leg, commission=$3.5/side

**Best config:** `ols_z2_exit0` — **NO PASS**

## Cointegration (IS 2020-2023)
- Engle-Granger ADF stat: **-1.4998** | p-value: **0.1253** | Cointegrated @ 5%: **✗**

## Cross-config gates
- PBO across 3 configs: **0.6905** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | Coint | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `ols_z2_exit0` | -1.55 | -4.44 | -10.40 | 115 | 2.42 | 0.998 | 1/8 | ✗ | ✗ | ✗ | ✓ | **fail** |
| `kalman_z2_exit0` | -1.78 | -4.30 | -9.86 | 163 | 1.17 | 0.989 | 1/8 | ✗ | ✗ | ✗ | ✓ | **fail** |
| `kalman_z2_exit0p5` | -1.97 | -4.28 | -9.57 | 182 | 0.85 | 0.997 | 1/8 | ✗ | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### ols_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38564 | -1.17 | -4.19 | -26.96 | 500 | 0.81 |
| IS | 2020-01-06 | 2023-12-31 | 24368 | -0.96 | -3.75 | -17.86 | 369 | 0.21 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -1.55 | -4.44 | -10.40 | 115 | 2.42 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -2.40 | -8.39 | -2.69 | 16 | 3.00 |

### kalman_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38564 | -0.90 | -3.11 | -19.20 | 482 | 1.58 |
| IS | 2020-01-06 | 2023-12-31 | 24368 | -0.63 | -2.52 | -11.29 | 294 | 1.85 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -1.78 | -4.30 | -9.86 | 163 | 1.17 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -1.03 | -2.82 | -1.86 | 25 | 1.08 |

### kalman_z2_exit0p5

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38564 | -1.07 | -3.28 | -19.82 | 544 | 0.98 |
| IS | 2020-01-06 | 2023-12-31 | 24368 | -0.82 | -2.85 | -12.87 | 334 | 1.12 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -1.97 | -4.28 | -9.57 | 182 | 0.85 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -0.86 | -2.11 | -1.54 | 28 | 0.94 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-18.98%** | IR: **-0.994** | Corr: **+0.007** | Beta: **+0.001**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Engle-Granger cointegration (ADF on OLS residuals): `[algo_trading_chan, p.42-54, ch.2]`
- Bollinger-band pair-trade entry/exit: `[algo_trading_chan, p.71-73, ch.3]`
- Kalman dynamic hedge-ratio δ=1e-4, Ve=1e-3: `[algo_trading_chan, p.75-80, ch.3]`
- KF state-space overfit warning (EWA-EWC): `[machine_trading, p.76-79, ch.3]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
