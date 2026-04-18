# NZDUSD 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (38578 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `atr_chandelier_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.4365** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -3.44 | -17.30 | -32.60 | 340 | 0.42 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `donchian_20_10_long` | long | -3.36 | -16.20 | -30.85 | 206 | 0.62 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `atr_chandelier_long` | long | -3.06 | -15.82 | -30.35 | 178 | 0.90 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38578 | -2.98 | -17.64 | -71.39 | 1071 | 0.46 |
| IS | 2020-01-06 | 2023-12-31 | 24384 | -2.85 | -18.05 | -55.73 | 684 | 0.46 |
| OOS | 2024-01-01 | 2025-12-31 | 12439 | -3.44 | -17.30 | -32.60 | 340 | 0.42 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -2.61 | -14.32 | -8.01 | 47 | 0.50 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38578 | -3.02 | -16.97 | -70.12 | 657 | 0.67 |
| IS | 2020-01-06 | 2023-12-31 | 24384 | -2.97 | -17.81 | -54.65 | 423 | 0.71 |
| OOS | 2024-01-01 | 2025-12-31 | 12439 | -3.36 | -16.20 | -30.85 | 206 | 0.62 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -1.92 | -10.46 | -6.59 | 28 | 0.73 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38578 | -2.78 | -16.87 | -69.54 | 564 | 0.92 |
| IS | 2020-01-06 | 2023-12-31 | 24384 | -2.62 | -17.07 | -53.39 | 359 | 0.92 |
| OOS | 2024-01-01 | 2025-12-31 | 12439 | -3.06 | -15.82 | -30.35 | 178 | 0.90 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.77 | -21.48 | -7.99 | 27 | 0.83 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-32.66%** | IR: **-1.819** | Corr: **+0.216** | Beta: **+0.066**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
