# XAUUSD 1h — T5 BollingerMR + regime overlay

**Window:** 2020-01-06 → 2026-04-14 (32088 bars, 1h metal)
**Costs:** half_spread=5.0bps, swap=0.0050%/day

**Best config:** `bmr_rv_highvol_30d` — **NO PASS**

## Cross-config gates
- PBO across 5 configs: **0.5595** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | Regime | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| `bmr_canonical` | none | -3.65 | -34.93 | -59.34 | 452 | 0.58 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_regime_sma200` | sma_trend | -3.64 | -29.22 | -50.10 | 300 | 0.62 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_rv_lowvol_30d` | rv_lowvol | -2.76 | -15.08 | -29.99 | 184 | 0.62 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_rv_highvol_30d` | rv_highvol | -2.75 | -24.66 | -45.62 | 271 | 0.58 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_regime_combo` | sma_trend_AND_rv_lowvol | -2.89 | -14.13 | -28.78 | 137 | 0.67 | 1.000 | 1/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### bmr_canonical (none)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32088 | -3.25 | -39.15 | -92.95 | 1238 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 18577 | -3.10 | -38.70 | -78.09 | 722 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 11856 | -3.65 | -34.93 | -59.34 | 452 | 0.58 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | -3.85 | -65.35 | -27.95 | 64 | 0.58 |

### bmr_regime_sma200 (sma_trend)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32088 | -2.51 | -28.27 | -82.90 | 754 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 18577 | -2.21 | -27.08 | -62.41 | 411 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 11856 | -3.64 | -29.22 | -50.10 | 300 | 0.62 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | -1.88 | -34.35 | -13.47 | 43 | 0.58 |

### bmr_rv_lowvol_30d (rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32088 | -2.83 | -17.84 | -65.32 | 620 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 18577 | -3.01 | -20.94 | -51.60 | 436 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 11856 | -2.76 | -15.08 | -29.99 | 184 | 0.62 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | 0.00 | 0.00 | 0.00 | 0 | 0.00 |

### bmr_rv_highvol_30d (rv_highvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32088 | -2.51 | -22.09 | -74.39 | 570 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 18577 | -2.55 | -14.45 | -40.26 | 235 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 11856 | -2.75 | -24.66 | -45.62 | 271 | 0.58 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | -3.85 | -65.35 | -27.95 | 64 | 0.58 |

### bmr_regime_combo (sma_trend_AND_rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 32088 | -2.35 | -11.85 | -50.28 | 386 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 18577 | -2.13 | -11.37 | -32.11 | 249 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 11856 | -2.89 | -14.13 | -28.78 | 137 | 0.67 |
| FWD | 2026-01-01 | 2026-04-14 | 1655 | 0.00 | 0.00 | 0.00 | 0 | 0.00 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-55.40%** | IR: **-2.483** | Corr: **-0.123** | Beta: **-0.096**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Regime-aware features: `[advances_fin_ml, ch.17]`
- SMA trend regime: `[stocks_on_the_move, p.110]`
- Realized-vol regime: `[volatility_trading]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
