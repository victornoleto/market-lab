# SPY 1h — T5 BollingerMR + regime overlay

**Window:** 2020-01-06 → 2026-04-14 (9456 bars, 1h equity)
**Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `bmr_rv_lowvol_30d` — **NO PASS**

## Cross-config gates
- PBO across 5 configs: **0.119** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Regime | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| `bmr_canonical` | none | -0.84 | -9.63 | -22.39 | 108 | 3.06 | 0.907 | 2/8 | ✗ | ✓ | ✓ | **fail** |
| `bmr_regime_sma200` | sma_trend | -0.52 | -3.96 | -11.28 | 82 | 3.96 | 0.977 | 0/8 | ✗ | ✓ | ✓ | **fail** |
| `bmr_rv_lowvol_30d` | rv_lowvol | -0.46 | -3.86 | -13.74 | 71 | 3.00 | 0.346 | 3/8 | ✗ | ✓ | ✓ | **fail** |
| `bmr_rv_highvol_30d` | rv_highvol | -0.62 | -5.34 | -16.80 | 38 | 4.04 | 0.956 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_regime_combo` | sma_trend_AND_rv_lowvol | -0.69 | -4.10 | -11.49 | 55 | 4.00 | 0.665 | 2/8 | ✗ | ✓ | ✓ | **fail** |

## Per-config window breakdown

### bmr_canonical (none)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | -0.58 | -7.82 | -41.64 | 355 | 2.88 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | -0.57 | -8.28 | -30.30 | 234 | 2.15 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -0.84 | -9.63 | -22.39 | 108 | 3.06 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | 1.38 | 14.37 | -4.49 | 13 | 2.00 |

### bmr_regime_sma200 (sma_trend)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | -0.85 | -6.86 | -33.99 | 237 | 2.96 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | -1.06 | -8.93 | -30.31 | 150 | 2.21 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -0.52 | -3.96 | -11.28 | 82 | 3.96 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | 0.77 | 3.40 | -2.99 | 5 | 2.00 |

### bmr_rv_lowvol_30d (rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | 0.17 | 0.97 | -19.74 | 196 | 2.94 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | 0.31 | 1.84 | -13.75 | 114 | 2.85 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -0.46 | -3.86 | -13.74 | 71 | 3.00 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | 2.62 | 27.38 | -2.04 | 11 | 1.17 |

### bmr_rv_highvol_30d (rv_highvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | -0.74 | -5.77 | -27.44 | 99 | 2.17 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | -0.75 | -5.67 | -18.24 | 59 | 2.00 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -0.62 | -5.34 | -16.80 | 38 | 4.04 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | -2.88 | -10.21 | -2.99 | 2 | 6.00 |

### bmr_regime_combo (sma_trend_AND_rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | -0.18 | -1.06 | -14.17 | 140 | 3.00 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | -0.12 | -0.69 | -9.16 | 81 | 3.00 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -0.69 | -4.10 | -11.49 | 55 | 4.00 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | 4.66 | 17.46 | -0.14 | 4 | 1.50 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-21.39%** | IR: **-1.011** | Corr: **+0.149** | Beta: **+0.082**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Regime-aware features: `[advances_fin_ml, ch.17]`
- SMA trend regime: `[stocks_on_the_move, p.110]`
- Realized-vol regime: `[volatility_trading]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
