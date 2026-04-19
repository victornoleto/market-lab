# USDCAD 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (38587 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `atr_chandelier_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.3413** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -6.48 | -18.86 | -35.29 | 370 | 0.44 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `donchian_20_10_long` | long | -5.52 | -15.69 | -29.98 | 216 | 0.75 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `atr_chandelier_long` | long | -5.28 | -16.11 | -30.69 | 188 | 0.88 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38587 | -4.56 | -17.52 | -70.77 | 1108 | 0.44 |
| IS | 2020-01-06 | 2023-12-31 | 24393 | -3.96 | -17.07 | -53.02 | 696 | 0.42 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -6.48 | -18.86 | -35.29 | 370 | 0.44 |
| FWD | 2026-01-01 | 2026-04-14 | 1754 | -4.83 | -14.18 | -4.68 | 42 | 0.50 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38587 | -4.23 | -15.44 | -65.87 | 674 | 0.71 |
| IS | 2020-01-06 | 2023-12-31 | 24393 | -3.87 | -15.66 | -49.85 | 433 | 0.67 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -5.52 | -15.69 | -29.98 | 216 | 0.75 |
| FWD | 2026-01-01 | 2026-04-14 | 1754 | -3.71 | -10.37 | -3.60 | 25 | 0.71 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38587 | -4.06 | -15.55 | -66.50 | 592 | 0.88 |
| IS | 2020-01-06 | 2023-12-31 | 24393 | -3.65 | -15.43 | -49.90 | 382 | 0.88 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -5.28 | -16.11 | -30.69 | 188 | 0.88 |
| FWD | 2026-01-01 | 2026-04-14 | 1754 | -4.38 | -13.27 | -4.47 | 22 | 1.15 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-32.53%** | IR: **-1.661** | Corr: **-0.259** | Beta: **-0.053**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
