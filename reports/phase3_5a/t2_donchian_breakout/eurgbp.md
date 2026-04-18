# EURGBP 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (38590 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `atr_chandelier_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.7302** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -5.93 | -16.00 | -30.15 | 338 | 0.42 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `donchian_20_10_long` | long | -5.10 | -12.65 | -24.29 | 203 | 0.71 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `atr_chandelier_long` | long | -4.88 | -12.82 | -24.59 | 173 | 0.96 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38590 | -3.99 | -16.00 | -68.62 | 1082 | 0.42 |
| IS | 2020-01-06 | 2023-12-31 | 24394 | -3.43 | -15.85 | -52.42 | 691 | 0.42 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -5.93 | -16.00 | -30.15 | 338 | 0.42 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -7.25 | -17.97 | -5.74 | 53 | 0.33 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38590 | -3.41 | -12.95 | -61.18 | 639 | 0.75 |
| IS | 2020-01-06 | 2023-12-31 | 24394 | -2.97 | -13.05 | -46.51 | 409 | 0.75 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -5.10 | -12.65 | -24.29 | 203 | 0.71 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -5.82 | -13.58 | -4.22 | 27 | 0.67 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38590 | -3.38 | -12.75 | -59.20 | 562 | 0.92 |
| IS | 2020-01-06 | 2023-12-31 | 24394 | -2.83 | -12.31 | -42.65 | 360 | 0.94 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -4.88 | -12.82 | -24.59 | 173 | 0.96 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -8.98 | -18.18 | -5.73 | 29 | 0.50 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-31.04%** | IR: **-1.593** | Corr: **-0.190** | Beta: **-0.040**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
