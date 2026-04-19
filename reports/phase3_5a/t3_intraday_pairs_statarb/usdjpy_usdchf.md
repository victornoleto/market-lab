# USDJPY_USDCHF 1h — T3 cointegration pair-trade

**Legs:** Y=`usdjpy` / X=`usdchf` | **Asset class:** fx_cross
**Window:** 2020-01-06 → 2026-04-14 (38583 aligned bars, 1h)
**Costs:** half_spread=3.0bps/leg, swap=0.0050%/day/leg, commission=$3.5/side

**Best config:** `kalman_z2_exit0` — **NO PASS**

## Cointegration (IS 2020-2023)
- Engle-Granger ADF stat: **-0.6379** | p-value: **0.4387** | Cointegrated @ 5%: **✗**

## Cross-config gates
- PBO across 3 configs: **0.5317** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | Coint | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `ols_z2_exit0` | -1.45 | -6.75 | -14.12 | 175 | 0.42 | 0.989 | 1/8 | ✗ | ✗ | ✗ | ✓ | **fail** |
| `kalman_z2_exit0` | -1.10 | -6.20 | -15.56 | 159 | 1.12 | 1.000 | 1/8 | ✗ | ✗ | ✗ | ✓ | **fail** |
| `kalman_z2_exit0p5` | -1.17 | -5.96 | -14.51 | 178 | 0.71 | 0.999 | 1/8 | ✗ | ✗ | ✓ | ✓ | **fail** |

## Per-config window breakdown

### ols_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38583 | -0.90 | -4.59 | -27.55 | 547 | 0.46 |
| IS | 2020-01-06 | 2023-12-31 | 24388 | -0.67 | -3.56 | -22.29 | 345 | 0.46 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -1.45 | -6.75 | -14.12 | 175 | 0.42 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -0.68 | -3.32 | -3.53 | 27 | 1.00 |

### kalman_z2_exit0

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38583 | -1.35 | -7.42 | -39.46 | 453 | 1.88 |
| IS | 2020-01-06 | 2023-12-31 | 24388 | -1.52 | -8.21 | -30.29 | 268 | 2.46 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -1.10 | -6.20 | -15.56 | 159 | 1.12 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -0.85 | -5.24 | -3.96 | 26 | 2.71 |

### kalman_z2_exit0p5

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38583 | -1.20 | -5.96 | -35.31 | 515 | 1.04 |
| IS | 2020-01-06 | 2023-12-31 | 24388 | -1.41 | -6.87 | -26.86 | 307 | 1.17 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -1.17 | -5.96 | -14.51 | 178 | 0.71 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | 1.45 | 7.77 | -2.73 | 30 | 0.88 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-19.37%** | IR: **-0.997** | Corr: **+0.018** | Beta: **+0.005**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Engle-Granger cointegration (ADF on OLS residuals): `[algo_trading_chan, p.42-54, ch.2]`
- Bollinger-band pair-trade entry/exit: `[algo_trading_chan, p.71-73, ch.3]`
- Kalman dynamic hedge-ratio δ=1e-4, Ve=1e-3: `[algo_trading_chan, p.75-80, ch.3]`
- KF state-space overfit warning (EWA-EWC): `[machine_trading, p.76-79, ch.3]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
