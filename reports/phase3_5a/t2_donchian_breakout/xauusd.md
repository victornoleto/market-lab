# XAUUSD 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (32088 bars, 1h forex)
**Asset class:** metal | **Costs:** half_spread=5.0bps, swap=0.0050%/day

**Best config:** `atr_chandelier_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.6508** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -0.14 | -1.98 | -18.32 | 333 | 0.58 | 0.960 | 2/8 | ✗ | ✓ | ✓ | **fail** |
| `donchian_20_10_long` | long | 0.02 | -0.29 | -13.28 | 191 | 0.92 | 0.735 | 3/8 | ✓ | ✓ | ✓ | **fail** |
| `atr_chandelier_long` | long | 0.31 | 2.66 | -13.94 | 171 | 1.04 | 0.666 | 3/8 | ✓ | ✓ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32088 | -1.01 | -13.52 | -67.64 | 905 | 0.50 |
| IS | 2020-01-06 | 2023-12-31 | 18577 | -1.66 | -21.86 | -62.51 | 533 | 0.46 |
| OOS | 2024-01-01 | 2025-12-31 | 11856 | -0.14 | -1.98 | -18.32 | 333 | 0.58 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | 0.54 | 10.17 | -11.24 | 39 | 0.71 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32088 | -0.30 | -4.66 | -49.76 | 515 | 0.83 |
| IS | 2020-01-06 | 2023-12-31 | 18577 | -0.79 | -11.38 | -45.51 | 304 | 0.79 |
| OOS | 2024-01-01 | 2025-12-31 | 11856 | 0.02 | -0.29 | -13.28 | 191 | 0.92 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | 2.28 | 57.05 | -7.67 | 20 | 1.75 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32088 | -0.20 | -3.42 | -47.60 | 442 | 1.21 |
| IS | 2020-01-06 | 2023-12-31 | 18577 | -0.78 | -11.38 | -47.60 | 254 | 1.21 |
| OOS | 2024-01-01 | 2025-12-31 | 11856 | 0.31 | 2.66 | -13.94 | 171 | 1.04 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | 2.45 | 63.67 | -5.95 | 17 | 2.58 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-30.20%** | IR: **-1.442** | Corr: **+0.195** | Beta: **+0.136**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
