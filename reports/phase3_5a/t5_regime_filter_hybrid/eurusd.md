# EURUSD 1h — T5 BollingerMR + regime overlay

**Window:** 2020-01-06 → 2026-04-14 (38648 bars, 1h forex)
**Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `bmr_regime_combo` — **NO PASS**

## Cross-config gates
- PBO across 5 configs: **0.2579** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Regime | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| `bmr_canonical` | none | -4.70 | -21.23 | -38.98 | 489 | 0.62 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_regime_sma200` | sma_trend | -2.88 | -10.34 | -21.62 | 280 | 0.58 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_rv_lowvol_30d` | rv_lowvol | -4.39 | -13.24 | -25.86 | 312 | 0.62 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_rv_highvol_30d` | rv_highvol | -2.48 | -9.29 | -18.66 | 182 | 0.67 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_regime_combo` | sma_trend_AND_rv_lowvol | -2.31 | -5.51 | -12.69 | 191 | 0.54 | 1.000 | 1/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### bmr_canonical (none)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38648 | -4.12 | -20.79 | -77.46 | 1519 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24451 | -3.79 | -20.20 | -59.89 | 965 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 12442 | -4.70 | -21.23 | -38.98 | 489 | 0.62 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -5.60 | -25.20 | -8.21 | 65 | 0.67 |

### bmr_regime_sma200 (sma_trend)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38648 | -2.58 | -10.51 | -50.90 | 843 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24451 | -2.43 | -10.55 | -36.42 | 536 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 12442 | -2.88 | -10.34 | -21.62 | 280 | 0.58 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.29 | -10.75 | -3.32 | 27 | 0.71 |

### bmr_rv_lowvol_30d (rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38648 | -3.94 | -13.40 | -60.31 | 973 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24451 | -3.71 | -13.20 | -43.97 | 615 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 12442 | -4.39 | -13.24 | -25.86 | 312 | 0.62 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -4.43 | -16.77 | -5.47 | 46 | 0.69 |

### bmr_rv_highvol_30d (rv_highvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38648 | -1.77 | -7.10 | -37.97 | 516 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24451 | -1.37 | -5.77 | -21.94 | 314 | 0.58 |
| OOS | 2024-01-01 | 2025-12-31 | 12442 | -2.48 | -9.29 | -18.66 | 182 | 0.67 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.21 | -9.71 | -3.14 | 20 | 0.62 |

### bmr_regime_combo (sma_trend_AND_rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38648 | -2.56 | -6.92 | -37.59 | 544 | 0.58 |
| IS | 2020-01-06 | 2023-12-31 | 24451 | -2.72 | -7.77 | -28.42 | 337 | 0.58 |
| OOS | 2024-01-01 | 2025-12-31 | 12442 | -2.31 | -5.51 | -12.69 | 191 | 0.54 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -1.78 | -4.29 | -2.02 | 16 | 0.77 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-35.89%** | IR: **-1.919** | Corr: **+0.018** | Beta: **+0.005**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Regime-aware features: `[advances_fin_ml, ch.17]`
- SMA trend regime: `[stocks_on_the_move, p.110]`
- Realized-vol regime: `[volatility_trading]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
