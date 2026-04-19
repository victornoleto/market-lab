# EURJPY 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (38590 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `donchian_20_10_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.3175** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -3.12 | -15.77 | -30.81 | 344 | 0.50 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `donchian_20_10_long` | long | -2.44 | -12.27 | -25.30 | 195 | 0.96 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `atr_chandelier_long` | long | -2.85 | -14.71 | -29.27 | 174 | 1.38 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38590 | -2.70 | -13.78 | -61.59 | 1031 | 0.54 |
| IS | 2020-01-06 | 2023-12-31 | 24441 | -2.46 | -12.80 | -43.27 | 640 | 0.52 |
| OOS | 2024-01-01 | 2025-12-31 | 12396 | -3.12 | -15.77 | -30.81 | 344 | 0.50 |
| FWD | 2026-01-01 | 2026-04-14 | 1753 | -3.80 | -13.52 | -4.92 | 47 | 0.79 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38590 | -2.08 | -10.47 | -51.35 | 602 | 0.92 |
| IS | 2020-01-06 | 2023-12-31 | 24441 | -1.83 | -9.41 | -33.69 | 381 | 0.88 |
| OOS | 2024-01-01 | 2025-12-31 | 12396 | -2.44 | -12.27 | -25.30 | 195 | 0.96 |
| FWD | 2026-01-01 | 2026-04-14 | 1753 | -3.84 | -12.70 | -5.41 | 26 | 1.25 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38590 | -2.33 | -12.08 | -56.70 | 543 | 1.17 |
| IS | 2020-01-06 | 2023-12-31 | 24441 | -1.95 | -10.41 | -37.15 | 344 | 1.04 |
| OOS | 2024-01-01 | 2025-12-31 | 12396 | -2.85 | -14.71 | -29.27 | 174 | 1.38 |
| FWD | 2026-01-01 | 2026-04-14 | 1753 | -4.84 | -16.74 | -6.75 | 25 | 2.04 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-28.77%** | IR: **-1.536** | Corr: **+0.102** | Beta: **+0.028**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
