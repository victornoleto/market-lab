# EURUSD 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (38648 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `donchian_20_10_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.7857** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -4.84 | -19.25 | -35.58 | 367 | 0.42 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `donchian_20_10_long` | long | -2.90 | -10.88 | -21.18 | 194 | 0.73 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `atr_chandelier_long` | long | -3.41 | -12.90 | -25.04 | 179 | 0.88 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38648 | -4.02 | -17.62 | -71.40 | 1103 | 0.46 |
| IS | 2020-01-06 | 2023-12-31 | 24451 | -3.76 | -17.37 | -54.03 | 692 | 0.46 |
| OOS | 2024-01-01 | 2025-12-31 | 12442 | -4.84 | -19.25 | -35.58 | 367 | 0.42 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -2.40 | -9.05 | -4.42 | 44 | 0.46 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38648 | -3.13 | -12.75 | -58.99 | 625 | 0.71 |
| IS | 2020-01-06 | 2023-12-31 | 24451 | -3.31 | -14.10 | -47.68 | 405 | 0.71 |
| OOS | 2024-01-01 | 2025-12-31 | 12442 | -2.90 | -10.88 | -21.18 | 194 | 0.73 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -1.90 | -6.79 | -2.90 | 26 | 0.75 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38648 | -3.07 | -13.15 | -60.44 | 537 | 0.96 |
| IS | 2020-01-06 | 2023-12-31 | 24451 | -3.04 | -13.85 | -46.66 | 335 | 0.96 |
| OOS | 2024-01-01 | 2025-12-31 | 12442 | -3.41 | -12.90 | -25.04 | 179 | 0.88 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -1.27 | -4.75 | -3.27 | 23 | 1.04 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-32.66%** | IR: **-1.771** | Corr: **+0.080** | Beta: **+0.019**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
