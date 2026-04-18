# XAUUSD_XAGUSD 1h — T3 cointegration pair-trade

**Legs:** Y=`xauusd` / X=`xagusd` | **Asset class:** metal
**Window:** 2020-01-06 → 2026-04-14 (32054 aligned bars, 1h)
**Costs:** half_spread=5.0bps/leg, swap=0.0050%/day/leg, commission=$3.5/side

**Best config:** `ols_z2_exit0` — **NO PASS**

## Cointegration (IS 2020-2023)
- Engle-Granger ADF stat: **-1.4906** | p-value: **0.1275** | Cointegrated @ 5%: **✗**

## Cross-config gates
- PBO across 3 configs: **0.9921** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | Coint | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `ols_z2_exit0` | -0.88 | -17.24 | -40.26 | 202 | 0.08 | 0.984 | 1/8 | ✗ | ✗ | ✓ | ✓ | **fail** |
| `kalman_z2_exit0` | -1.66 | -35.94 | -62.89 | 143 | 2.25 | 0.841 | 1/8 | ✗ | ✗ | ✗ | ✓ | **fail** |
| `kalman_z2_exit0p5` | -1.34 | -27.27 | -52.94 | 162 | 1.15 | 0.995 | 0/8 | ✗ | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### ols_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32054 | -0.66 | -24.91 | -82.74 | 486 | 0.17 |
| IS | 2020-01-06 | 2023-12-31 | 18559 | -0.77 | -32.74 | -71.63 | 270 | 0.42 |
| OOS | 2024-01-01 | 2025-12-31 | 11840 | -0.88 | -17.24 | -40.26 | 202 | 0.08 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | 0.74 | 24.26 | -23.60 | 14 | 2.19 |

### kalman_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32054 | -0.51 | -22.54 | -86.71 | 408 | 1.65 |
| IS | 2020-01-06 | 2023-12-31 | 18559 | 0.11 | -1.87 | -45.16 | 242 | 1.23 |
| OOS | 2024-01-01 | 2025-12-31 | 11840 | -1.66 | -35.94 | -62.89 | 143 | 2.25 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | -1.66 | -78.81 | -46.97 | 23 | 1.67 |

### kalman_z2_exit0p5

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32054 | -1.11 | -25.99 | -82.76 | 450 | 1.00 |
| IS | 2020-01-06 | 2023-12-31 | 18559 | -0.80 | -16.21 | -44.67 | 265 | 0.96 |
| OOS | 2024-01-01 | 2025-12-31 | 11840 | -1.34 | -27.27 | -52.94 | 162 | 1.15 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | -2.28 | -79.23 | -45.83 | 23 | 0.96 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-41.37%** | IR: **-0.952** | Corr: **-0.229** | Beta: **-0.372**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Engle-Granger cointegration (ADF on OLS residuals): `[algo_trading_chan, p.42-54, ch.2]`
- Bollinger-band pair-trade entry/exit: `[algo_trading_chan, p.71-73, ch.3]`
- Kalman dynamic hedge-ratio δ=1e-4, Ve=1e-3: `[algo_trading_chan, p.75-80, ch.3]`
- KF state-space overfit warning (EWA-EWC): `[machine_trading, p.76-79, ch.3]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
