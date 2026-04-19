# AUDUSD 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (38598 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `atr_chandelier_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.7778** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -3.80 | -19.11 | -35.35 | 347 | 0.46 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `donchian_20_10_long` | long | -3.47 | -16.57 | -31.15 | 200 | 0.67 | 1.000 | 0/8 | ✗ | ✓ | ✓ | **fail** |
| `atr_chandelier_long` | long | -3.13 | -16.03 | -31.09 | 171 | 1.00 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38598 | -3.26 | -19.22 | -74.81 | 1106 | 0.46 |
| IS | 2020-01-06 | 2023-12-31 | 24402 | -3.27 | -20.38 | -60.62 | 714 | 0.46 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.80 | -19.11 | -35.35 | 347 | 0.46 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -0.27 | -2.04 | -5.08 | 45 | 0.50 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38598 | -2.66 | -15.74 | -67.17 | 642 | 0.75 |
| IS | 2020-01-06 | 2023-12-31 | 24402 | -2.60 | -16.51 | -52.10 | 418 | 0.79 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.47 | -16.57 | -31.15 | 200 | 0.67 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | 0.39 | 2.52 | -4.62 | 24 | 0.83 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38598 | -2.62 | -16.42 | -68.61 | 556 | 1.00 |
| IS | 2020-01-06 | 2023-12-31 | 24402 | -2.57 | -17.31 | -54.29 | 361 | 1.00 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.13 | -16.03 | -31.09 | 171 | 1.00 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -0.87 | -6.25 | -6.00 | 24 | 0.96 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-34.27%** | IR: **-1.932** | Corr: **+0.235** | Beta: **+0.073**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
