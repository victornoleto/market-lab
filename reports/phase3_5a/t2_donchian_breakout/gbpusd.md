# GBPUSD 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (38653 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `atr_chandelier_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.373** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -4.14 | -16.04 | -30.21 | 352 | 0.46 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `donchian_20_10_long` | long | -3.52 | -13.27 | -25.63 | 204 | 0.79 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `atr_chandelier_long` | long | -3.41 | -13.42 | -25.89 | 180 | 1.00 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38653 | -3.48 | -17.35 | -71.35 | 1114 | 0.46 |
| IS | 2020-01-06 | 2023-12-31 | 24457 | -3.40 | -18.59 | -57.20 | 717 | 0.42 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -4.14 | -16.04 | -30.21 | 352 | 0.46 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -1.95 | -8.94 | -4.56 | 45 | 0.54 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38653 | -2.97 | -14.10 | -63.76 | 652 | 0.75 |
| IS | 2020-01-06 | 2023-12-31 | 24457 | -2.84 | -14.79 | -50.42 | 419 | 0.75 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.52 | -13.27 | -25.63 | 204 | 0.79 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -2.55 | -10.49 | -4.66 | 29 | 0.75 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38653 | -2.54 | -13.26 | -61.76 | 558 | 0.96 |
| IS | 2020-01-06 | 2023-12-31 | 24457 | -2.25 | -13.12 | -46.48 | 352 | 0.96 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.41 | -13.42 | -25.89 | 180 | 1.00 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.41 | -15.18 | -6.61 | 27 | 0.79 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-32.39%** | IR: **-1.762** | Corr: **+0.121** | Beta: **+0.033**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
