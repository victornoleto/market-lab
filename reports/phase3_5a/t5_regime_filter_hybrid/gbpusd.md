# GBPUSD 1h — T5 BollingerMR + regime overlay

**Window:** 2020-01-06 → 2026-04-14 (38653 bars, 1h forex)
**Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `bmr_rv_highvol_30d` — **NO PASS**

## Cross-config gates
- PBO across 5 configs: **0.1667** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Regime | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| `bmr_canonical` | none | -4.45 | -19.63 | -36.71 | 470 | 0.58 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_regime_sma200` | sma_trend | -3.56 | -12.05 | -24.50 | 259 | 0.58 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_rv_lowvol_30d` | rv_lowvol | -3.60 | -12.56 | -25.21 | 313 | 0.58 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_rv_highvol_30d` | rv_highvol | -2.56 | -8.09 | -16.08 | 162 | 0.67 | 1.000 | 1/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_regime_combo` | sma_trend_AND_rv_lowvol | -3.15 | -8.35 | -18.07 | 171 | 0.58 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### bmr_canonical (none)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38653 | -3.92 | -23.15 | -81.62 | 1491 | 0.58 |
| IS | 2020-01-06 | 2023-12-31 | 24457 | -3.79 | -24.86 | -68.99 | 958 | 0.58 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -4.45 | -19.63 | -36.71 | 470 | 0.58 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -4.80 | -23.60 | -7.80 | 62 | 0.67 |

### bmr_regime_sma200 (sma_trend)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38653 | -2.90 | -13.05 | -59.30 | 811 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24457 | -2.71 | -13.63 | -45.10 | 526 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.56 | -12.05 | -24.50 | 259 | 0.58 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.33 | -12.00 | -3.69 | 25 | 0.67 |

### bmr_rv_lowvol_30d (rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38653 | -3.69 | -13.44 | -60.57 | 846 | 0.58 |
| IS | 2020-01-06 | 2023-12-31 | 24457 | -3.71 | -14.02 | -46.15 | 507 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.60 | -12.56 | -25.21 | 313 | 0.58 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -4.18 | -11.66 | -3.98 | 25 | 0.46 |

### bmr_rv_highvol_30d (rv_highvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38653 | -1.93 | -9.34 | -47.62 | 601 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24457 | -1.74 | -9.67 | -35.27 | 402 | 0.58 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -2.56 | -8.09 | -16.08 | 162 | 0.67 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.05 | -13.52 | -4.72 | 37 | 0.75 |

### bmr_regime_combo (sma_trend_AND_rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38653 | -2.70 | -7.48 | -39.92 | 461 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24457 | -2.44 | -7.02 | -27.09 | 277 | 0.67 |
| OOS | 2024-01-01 | 2025-12-31 | 12441 | -3.15 | -8.35 | -18.07 | 171 | 0.58 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -3.71 | -7.72 | -3.00 | 12 | 0.56 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-38.30%** | IR: **-2.087** | Corr: **+0.103** | Beta: **+0.036**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Regime-aware features: `[advances_fin_ml, ch.17]`
- SMA trend regime: `[stocks_on_the_move, p.110]`
- Realized-vol regime: `[volatility_trading]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
