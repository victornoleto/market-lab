# GBPUSD 1h — T4 session-based FX (ORB / NY-close MR / Asian fade)

**Window:** 2020-01-06 → 2026-04-14 (38653 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day, commission=$3.5/side

**Best config:** `ny_close_mr_1h` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.0** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Type | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| `london_orb_asian_range` | session_orb | both | -5.94 | -29.39 | -51.19 | 552 | 1.00 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `ny_close_mr_1h` | session_mr | both | -0.74 | -0.18 | -0.50 | 2 | 0.33 | 0.764 | 1/8 | ✗ | ✓ | ✓ | **fail** |
| `asian_range_fade_ny_range` | session_fade | both | -3.67 | -8.76 | -17.52 | 258 | 0.29 | 1.000 | 1/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### london_orb_asian_range (session_orb, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38653 | -4.47 | -29.89 | -90.46 | 1741 | 1.00 |
| IS | 2020-01-06 | 2023-12-31 | 24457 | -4.09 | -30.49 | -78.55 | 1110 | 1.00 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -5.94 | -29.39 | -51.19 | 552 | 1.00 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -4.18 | -24.94 | -9.21 | 79 | 1.00 |

### ny_close_mr_1h (session_mr, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38653 | -0.27 | -0.05 | -0.56 | 4 | 0.46 |
| IS | 2020-01-06 | 2023-12-31 | 24457 | -0.21 | -0.02 | -0.24 | 1 | 0.46 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -0.74 | -0.18 | -0.50 | 2 | 0.33 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | 1.38 | 0.54 | -0.10 | 1 | 0.46 |

### asian_range_fade_ny_range (session_fade, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38653 | -2.88 | -8.90 | -45.15 | 826 | 0.29 |
| IS | 2020-01-06 | 2023-12-31 | 24457 | -2.72 | -9.26 | -32.87 | 531 | 0.29 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.67 | -8.76 | -17.52 | 258 | 0.29 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -1.54 | -4.80 | -1.77 | 37 | 0.29 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-45.17%** | IR: **-2.332** | Corr: **-0.115** | Beta: **-0.046**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Session ORB / breakout: `[trading_systems_methods, p.353]`
- Range fade / false-break mechanics: `[trading_systems_methods, p.326-329]`
- FX intraday parsimony ≤5 params: `[quant_trading_chan, p.43-53, ch.2-3]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- ATR / volatility filter: `[volatility_trading]`
- Hold ≤ 5d (T4 target ≤ 24h) swap-kill: `[systematic_trading, p.185-188]`
- PBO / DSR / WF gates: `[advances_fin_ml, ch.7, p.208-211]`
