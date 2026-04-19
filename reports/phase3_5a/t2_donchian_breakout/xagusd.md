# XAGUSD 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (32114 bars, 1h forex)
**Asset class:** metal | **Costs:** half_spread=5.0bps, swap=0.0050%/day

**Best config:** `atr_chandelier_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.4444** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -0.43 | -10.09 | -38.75 | 352 | 0.50 | 0.772 | 2/8 | ✗ | ✓ | ✓ | **fail** |
| `donchian_20_10_long` | long | -0.20 | -5.43 | -31.32 | 207 | 0.88 | 0.576 | 2/8 | ✗ | ✓ | ✓ | **fail** |
| `atr_chandelier_long` | long | 0.57 | 9.40 | -25.04 | 172 | 1.12 | 0.479 | 3/8 | ✓ | ✓ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32114 | -0.40 | -16.13 | -80.34 | 909 | 0.50 |
| IS | 2020-01-06 | 2023-12-31 | 18604 | -0.46 | -20.61 | -68.24 | 512 | 0.54 |
| OOS | 2024-01-01 | 2025-12-31 | 11855 | -0.43 | -10.09 | -38.75 | 352 | 0.50 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | 0.01 | -8.96 | -21.21 | 45 | 0.62 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32114 | -0.09 | -6.87 | -70.38 | 527 | 0.92 |
| IS | 2020-01-06 | 2023-12-31 | 18604 | -0.22 | -12.71 | -58.91 | 298 | 0.96 |
| OOS | 2024-01-01 | 2025-12-31 | 11855 | -0.20 | -5.43 | -31.32 | 207 | 0.88 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | 1.41 | 72.89 | -20.55 | 22 | 1.54 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32114 | 0.02 | -3.83 | -64.56 | 451 | 1.12 |
| IS | 2020-01-06 | 2023-12-31 | 18604 | -0.22 | -12.87 | -59.27 | 260 | 1.08 |
| OOS | 2024-01-01 | 2025-12-31 | 11855 | 0.57 | 9.40 | -25.04 | 172 | 1.12 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | 0.55 | 15.88 | -25.99 | 19 | 2.04 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-32.81%** | IR: **-0.985** | Corr: **+0.352** | Beta: **+0.580**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
