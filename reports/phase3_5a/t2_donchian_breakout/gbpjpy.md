# GBPJPY 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (38422 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `donchian_20_10_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.6905** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -2.91 | -15.06 | -30.31 | 350 | 0.58 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `donchian_20_10_long` | long | -2.56 | -12.91 | -26.38 | 204 | 1.00 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `atr_chandelier_long` | long | -2.83 | -15.04 | -30.05 | 180 | 1.12 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38422 | -2.89 | -16.12 | -67.60 | 1075 | 0.54 |
| IS | 2020-01-06 | 2023-12-31 | 24235 | -2.84 | -16.68 | -51.94 | 674 | 0.54 |
| OOS | 2024-01-01 | 2025-12-31 | 12432 | -2.91 | -15.06 | -30.31 | 350 | 0.58 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -4.22 | -16.15 | -6.61 | 51 | 0.58 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38422 | -2.14 | -11.54 | -54.51 | 621 | 0.96 |
| IS | 2020-01-06 | 2023-12-31 | 24235 | -1.94 | -10.95 | -37.65 | 392 | 0.92 |
| OOS | 2024-01-01 | 2025-12-31 | 12432 | -2.56 | -12.91 | -26.38 | 204 | 1.00 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -2.43 | -10.23 | -4.86 | 25 | 1.00 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38422 | -2.02 | -11.64 | -54.85 | 533 | 1.12 |
| IS | 2020-01-06 | 2023-12-31 | 24235 | -1.67 | -10.18 | -35.87 | 332 | 1.08 |
| OOS | 2024-01-01 | 2025-12-31 | 12432 | -2.83 | -15.04 | -30.05 | 180 | 1.12 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -1.74 | -7.29 | -3.56 | 21 | 2.17 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-31.14%** | IR: **-1.714** | Corr: **+0.188** | Beta: **+0.057**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
