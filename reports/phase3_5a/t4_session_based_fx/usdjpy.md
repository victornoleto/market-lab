# USDJPY 1h — T4 session-based FX (ORB / NY-close MR / Asian fade)

**Window:** 2020-01-06 → 2026-04-14 (38713 bars, 1h forex)
**Asset class:** forex | **Costs:** half_spread=2.0bps, swap=0.0050%/day, commission=$3.5/side

**Best config:** `ny_close_mr_1h` — **NO PASS**

## Cross-config gates
- PBO across 3 configs: **0.0** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Type | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| `london_orb_asian_range` | session_orb | both | -3.13 | -21.34 | -40.67 | 470 | 1.00 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `ny_close_mr_1h` | session_mr | both | 0.27 | 0.18 | -0.75 | 3 | 0.46 | 0.563 | 1/8 | ✓ | ✗ | ✓ | **fail** |
| `asian_range_fade_ny_range` | session_fade | both | -3.11 | -12.97 | -25.03 | 405 | 0.29 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### london_orb_asian_range (session_orb, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38713 | -3.35 | -22.75 | -81.83 | 1502 | 1.00 |
| IS | 2020-01-06 | 2023-12-31 | 24518 | -3.49 | -23.82 | -69.10 | 966 | 1.00 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -3.13 | -21.34 | -40.67 | 470 | 1.00 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -2.78 | -16.39 | -6.56 | 64 | 1.00 |

### ny_close_mr_1h (session_mr, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38713 | -0.06 | -0.03 | -0.75 | 6 | 0.46 |
| IS | 2020-01-06 | 2023-12-31 | 24518 | -0.91 | -0.13 | -0.54 | 3 | 0.46 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | 0.27 | 0.18 | -0.75 | 3 | 0.46 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | 0.00 | 0.00 | 0.00 | 0 | 0.00 |

### asian_range_fade_ny_range (session_fade, both)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38713 | -3.23 | -12.51 | -57.70 | 1120 | 0.29 |
| IS | 2020-01-06 | 2023-12-31 | 24518 | -3.38 | -12.67 | -43.22 | 664 | 0.29 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -3.11 | -12.97 | -25.03 | 405 | 0.29 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -2.16 | -6.86 | -2.42 | 51 | 0.29 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-37.94%** | IR: **-1.988** | Corr: **+0.020** | Beta: **+0.008**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Session ORB / breakout: `[trading_systems_methods, p.353]`
- Range fade / false-break mechanics: `[trading_systems_methods, p.326-329]`
- FX intraday parsimony ≤5 params: `[quant_trading_chan, p.43-53, ch.2-3]`
- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`
- ATR / volatility filter: `[volatility_trading]`
- Hold ≤ 5d (T4 target ≤ 24h) swap-kill: `[systematic_trading, p.185-188]`
- PBO / DSR / WF gates: `[advances_fin_ml, ch.7, p.208-211]`
