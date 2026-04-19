# EURUSD 1h — T4 session-based FX (ORB / NY-close MR / Asian fade)

**Window:** 2020-01-06 → 2026-04-14 (38648 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day, commission=$3.5/side

**Best config:** `ny_close_mr_1h` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.0** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Type | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| `london_orb_asian_range` | session_orb | both | -6.24 | -31.11 | -53.80 | 558 | 1.00 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `ny_close_mr_1h` | session_mr | both | -0.83 | -0.10 | -0.24 | 2 | 0.46 | 0.397 | 2/8 | ✗ | ✓ | ✓ | **fail** |
| `asian_range_fade_ny_range` | session_fade | both | -3.32 | -7.68 | -15.16 | 258 | 0.29 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### london_orb_asian_range (session_orb, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38648 | -4.91 | -28.27 | -88.49 | 1727 | 1.00 |
| IS | 2020-01-06 | 2023-12-31 | 24451 | -4.44 | -27.27 | -73.39 | 1094 | 1.00 |
| OOS | 2024-01-01 | 2025-12-31 | 12442 | -6.24 | -31.11 | -53.80 | 558 | 1.00 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.91 | -21.39 | -7.71 | 73 | 1.00 |

### ny_close_mr_1h (session_mr, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38648 | 0.10 | 0.01 | -0.40 | 4 | 0.46 |
| IS | 2020-01-06 | 2023-12-31 | 24451 | 0.32 | 0.02 | -0.07 | 1 | 0.46 |
| OOS | 2024-01-01 | 2025-12-31 | 12442 | -0.83 | -0.10 | -0.24 | 2 | 0.46 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | 1.55 | 0.74 | -0.13 | 1 | 0.46 |

### asian_range_fade_ny_range (session_fade, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38648 | -2.94 | -7.64 | -40.05 | 792 | 0.29 |
| IS | 2020-01-06 | 2023-12-31 | 24451 | -2.78 | -7.68 | -27.84 | 498 | 0.29 |
| OOS | 2024-01-01 | 2025-12-31 | 12442 | -3.32 | -7.68 | -15.16 | 258 | 0.29 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.33 | -6.84 | -2.50 | 36 | 0.29 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-43.48%** | IR: **-2.371** | Corr: **+0.008** | Beta: **+0.003**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Session ORB / breakout: `[trading_systems_methods, p.353]`
- Range fade / false-break mechanics: `[trading_systems_methods, p.326-329]`
- FX intraday parsimony ≤5 params: `[quant_trading_chan, p.43-53, ch.2-3]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- ATR / volatility filter: `[volatility_trading]`
- Hold ≤ 5d (T4 target ≤ 24h) swap-kill: `[systematic_trading, p.185-188]`
- PBO / DSR / WF gates: `[advances_fin_ml, ch.7, p.208-211]`
