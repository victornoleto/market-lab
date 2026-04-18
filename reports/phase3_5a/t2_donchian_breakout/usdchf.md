# USDCHF 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (38593 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `atr_chandelier_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.9444** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -3.77 | -15.61 | -30.38 | 329 | 0.50 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `donchian_20_10_long` | long | -3.33 | -13.26 | -26.10 | 193 | 0.83 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `atr_chandelier_long` | long | -3.19 | -13.95 | -27.29 | 155 | 1.08 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38593 | -4.28 | -18.14 | -72.15 | 1072 | 0.46 |
| IS | 2020-01-06 | 2023-12-31 | 24397 | -4.49 | -19.22 | -57.85 | 687 | 0.46 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.77 | -15.61 | -30.38 | 329 | 0.50 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -4.78 | -20.54 | -6.49 | 56 | 0.38 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38593 | -3.28 | -13.55 | -61.00 | 618 | 0.79 |
| IS | 2020-01-06 | 2023-12-31 | 24397 | -3.27 | -13.77 | -45.64 | 397 | 0.75 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.33 | -13.26 | -26.10 | 193 | 0.83 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -2.94 | -12.21 | -3.82 | 27 | 0.71 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38593 | -3.33 | -14.51 | -63.46 | 522 | 0.98 |
| IS | 2020-01-06 | 2023-12-31 | 24397 | -3.47 | -15.10 | -48.64 | 343 | 0.96 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.19 | -13.95 | -27.29 | 155 | 1.08 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -2.23 | -9.80 | -3.18 | 23 | 0.92 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-33.19%** | IR: **-1.753** | Corr: **-0.077** | Beta: **-0.017**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
