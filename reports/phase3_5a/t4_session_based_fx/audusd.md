# AUDUSD 1h — T4 session-based FX (ORB / NY-close MR / Asian fade)

**Window:** 2020-01-06 → 2026-04-14 (38598 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day, commission=$3.5/side

**Best config:** `ny_close_mr_1h` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.0** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Type | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| `london_orb_asian_range` | session_orb | both | -4.62 | -28.49 | -50.48 | 487 | 1.00 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `ny_close_mr_1h` | session_mr | both | 0.75 | 0.21 | -0.13 | 1 | 0.46 | 0.655 | 3/8 | ✓ | ✓ | ✓ | **fail** |
| `asian_range_fade_ny_range` | session_fade | both | -2.93 | -10.24 | -20.43 | 369 | 0.29 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### london_orb_asian_range (session_orb, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38598 | -3.32 | -25.77 | -86.86 | 1518 | 1.00 |
| IS | 2020-01-06 | 2023-12-31 | 24402 | -2.99 | -25.20 | -72.29 | 967 | 1.00 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -4.62 | -28.49 | -50.48 | 487 | 1.00 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -1.60 | -13.81 | -7.52 | 63 | 1.00 |

### ny_close_mr_1h (session_mr, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38598 | -0.16 | -0.07 | -1.50 | 10 | 0.46 |
| IS | 2020-01-06 | 2023-12-31 | 24402 | -0.45 | -0.22 | -1.50 | 8 | 0.46 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | 0.75 | 0.21 | -0.13 | 1 | 0.46 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | 0.05 | 0.03 | -0.25 | 1 | 0.46 |

### asian_range_fade_ny_range (session_fade, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38598 | -2.13 | -9.44 | -48.51 | 1159 | 0.29 |
| IS | 2020-01-06 | 2023-12-31 | 24402 | -1.97 | -9.54 | -35.15 | 737 | 0.29 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -2.93 | -10.24 | -20.43 | 369 | 0.29 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -0.40 | -2.00 | -2.06 | 53 | 0.29 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-40.90%** | IR: **-2.090** | Corr: **-0.033** | Beta: **-0.014**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Session ORB / breakout: `[trading_systems_methods, p.353]`
- Range fade / false-break mechanics: `[trading_systems_methods, p.326-329]`
- FX intraday parsimony ≤5 params: `[quant_trading_chan, p.43-53, ch.2-3]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- ATR / volatility filter: `[volatility_trading]`
- Hold ≤ 5d (T4 target ≤ 24h) swap-kill: `[systematic_trading, p.185-188]`
- PBO / DSR / WF gates: `[advances_fin_ml, ch.7, p.208-211]`
