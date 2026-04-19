# SPY_QQQ 1h — T3 cointegration pair-trade

**Legs:** Y=`SPY` / X=`QQQ` | **Asset class:** equity
**Window:** 2020-01-06 → 2026-04-14 (9456 aligned bars, 1h)
**Costs:** half_spread=10.0bps/leg, swap=0.0050%/day/leg, commission=$3.5/side

**Best config:** `kalman_z2_exit0` — **NO PASS**

## Cointegration (IS 2020-2023)
- Engle-Granger ADF stat: **-1.7846** | p-value: **0.0706** | Cointegrated @ 5%: **✗**

## Cross-config gates
- PBO across 3 configs: **0.3571** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | Coint | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `ols_z2_exit0` | -2.75 | -10.20 | -5.47 | 31 | 12.92 | 0.967 | 3/8 | ✗ | ✗ | ✗ | ✗ | **fail** |
| `kalman_z2_exit0` | 0.13 | 0.65 | -3.93 | 36 | 9.04 | 0.764 | 3/8 | ✗ | ✓ | ✓ | ✗ | **fail** |
| `kalman_z2_exit0p5` | -0.48 | -2.98 | -4.22 | 38 | 7.10 | 0.929 | 1/8 | ✗ | ✗ | ✗ | ✗ | **fail** |

## Per-config window breakdown

### ols_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | -1.47 | -9.92 | -18.36 | 101 | 12.00 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | -1.07 | -8.63 | -12.12 | 67 | 9.00 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -2.75 | -10.20 | -5.47 | 31 | 12.92 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | -6.45 | -24.22 | -1.94 | 3 | 22.96 |

### kalman_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | -0.58 | -5.34 | -19.95 | 101 | 10.83 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | -0.90 | -8.89 | -19.95 | 57 | 14.00 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | 0.13 | 0.65 | -3.93 | 36 | 9.04 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | 1.05 | 7.08 | -1.59 | 8 | 5.98 |

### kalman_z2_exit0p5

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | -1.18 | -9.18 | -20.73 | 110 | 7.08 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | -1.39 | -11.91 | -20.05 | 64 | 7.52 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -0.48 | -2.98 | -4.22 | 38 | 7.10 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | -2.35 | -12.33 | -1.78 | 8 | 1.44 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-17.23%** | IR: **-0.841** | Corr: **-0.264** | Beta: **-0.048**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Engle-Granger cointegration (ADF on OLS residuals): `[algo_trading_chan, p.42-54, ch.2]`
- Bollinger-band pair-trade entry/exit: `[algo_trading_chan, p.71-73, ch.3]`
- Kalman dynamic hedge-ratio δ=1e-4, Ve=1e-3: `[algo_trading_chan, p.75-80, ch.3]`
- KF state-space overfit warning (EWA-EWC): `[machine_trading, p.76-79, ch.3]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
