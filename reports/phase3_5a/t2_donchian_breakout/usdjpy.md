# USDJPY 1h — T2 Donchian/ATR-Chandelier breakout

**Window:** 2020-01-06 → 2026-04-14 (38713 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `donchian_20_10_long` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.5476** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `donchian_10_5_long` | long | -2.11 | -11.60 | -24.64 | 340 | 0.54 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `donchian_20_10_long` | long | -2.08 | -11.23 | -23.76 | 204 | 0.90 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `atr_chandelier_long` | long | -2.31 | -13.54 | -29.28 | 170 | 1.33 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### donchian_10_5_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38713 | -2.62 | -14.18 | -62.64 | 1049 | 0.50 |
| IS | 2020-01-06 | 2023-12-31 | 24518 | -2.77 | -15.02 | -48.60 | 656 | 0.50 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -2.11 | -11.60 | -24.64 | 340 | 0.54 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -4.62 | -20.15 | -6.32 | 53 | 0.42 |

### donchian_20_10_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38713 | -2.25 | -11.89 | -56.13 | 615 | 0.92 |
| IS | 2020-01-06 | 2023-12-31 | 24518 | -2.28 | -12.04 | -41.38 | 378 | 0.92 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -2.08 | -11.23 | -23.76 | 204 | 0.90 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.27 | -14.06 | -4.77 | 32 | 0.67 |

### atr_chandelier_long (long)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38713 | -2.39 | -13.27 | -60.66 | 523 | 1.17 |
| IS | 2020-01-06 | 2023-12-31 | 24518 | -2.35 | -12.86 | -44.02 | 326 | 1.04 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -2.31 | -13.54 | -29.28 | 170 | 1.33 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.73 | -16.65 | -5.18 | 26 | 0.96 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-29.18%** | IR: **-1.520** | Corr: **+0.025** | Beta: **+0.007**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Donchian 10/5 & 20/10: `[trading_systems_methods, p.353]`
- Chandelier trailing ATR: `[volatility_trading]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
