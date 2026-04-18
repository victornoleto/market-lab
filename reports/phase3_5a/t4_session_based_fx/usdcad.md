# USDCAD 1h — T4 session-based FX (ORB / NY-close MR / Asian fade)

**Window:** 2020-01-06 → 2026-04-14 (38587 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day, commission=$3.5/side

**Best config:** `ny_close_mr_1h` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.0** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Type | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| `london_orb_asian_range` | session_orb | both | -6.98 | -28.35 | -49.91 | 573 | 1.00 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `ny_close_mr_1h` | session_mr | both | -0.50 | -0.28 | -0.98 | 9 | 0.46 | 0.684 | 2/8 | ✗ | ✗ | ✓ | **fail** |
| `asian_range_fade_ny_range` | session_fade | both | -4.95 | -7.20 | -14.43 | 220 | 0.29 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### london_orb_asian_range (session_orb, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38587 | -5.92 | -29.24 | -89.01 | 1760 | 1.00 |
| IS | 2020-01-06 | 2023-12-31 | 24393 | -5.61 | -30.16 | -76.49 | 1114 | 1.00 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -6.98 | -28.35 | -49.91 | 573 | 1.00 |
| FWD | 2026-01-01 | 2026-04-14 | 1754 | -5.99 | -23.49 | -7.71 | 74 | 1.00 |

### ny_close_mr_1h (session_mr, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38587 | -0.19 | -0.07 | -1.01 | 13 | 0.46 |
| IS | 2020-01-06 | 2023-12-31 | 24393 | 0.24 | 0.04 | -0.37 | 4 | 0.46 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -0.50 | -0.28 | -0.98 | 9 | 0.46 |
| FWD | 2026-01-01 | 2026-04-14 | 1754 | 0.00 | 0.00 | 0.00 | 0 | 0.00 |

### asian_range_fade_ny_range (session_fade, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38587 | -3.81 | -7.61 | -39.69 | 762 | 0.29 |
| IS | 2020-01-06 | 2023-12-31 | 24393 | -3.42 | -7.74 | -27.86 | 509 | 0.29 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -4.95 | -7.20 | -14.43 | 220 | 0.29 |
| FWD | 2026-01-01 | 2026-04-14 | 1754 | -6.98 | -8.78 | -2.63 | 33 | 0.29 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-44.45%** | IR: **-2.433** | Corr: **-0.047** | Beta: **-0.014**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Session ORB / breakout: `[trading_systems_methods, p.353]`
- Range fade / false-break mechanics: `[trading_systems_methods, p.326-329]`
- FX intraday parsimony ≤5 params: `[quant_trading_chan, p.43-53, ch.2-3]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- ATR / volatility filter: `[volatility_trading]`
- Hold ≤ 5d (T4 target ≤ 24h) swap-kill: `[systematic_trading, p.185-188]`
- PBO / DSR / WF gates: `[advances_fin_ml, ch.7, p.208-211]`
