# USDJPY 1h — T5 BollingerMR + regime overlay

**Window:** 2020-01-06 → 2026-04-14 (38713 bars, 1h forex)
**Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `bmr_rv_highvol_30d` — **NO PASS**

## Cross-config gates
- PBO across 5 configs: **0.0516** (pass=True)

## All configs — OOS metrics + 5-gate

| Config | Regime | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| `bmr_canonical` | none | -4.49 | -27.77 | -49.06 | 434 | 0.62 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_regime_sma200` | sma_trend | -4.28 | -20.51 | -37.75 | 272 | 0.62 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_rv_lowvol_30d` | rv_lowvol | -3.87 | -16.19 | -30.72 | 260 | 0.62 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_rv_highvol_30d` | rv_highvol | -2.62 | -13.74 | -26.75 | 178 | 0.62 | 1.000 | 2/8 | ✗ | ✓ | ✓ | **fail** |
| `bmr_regime_combo` | sma_trend_AND_rv_lowvol | -3.77 | -12.77 | -24.65 | 169 | 0.67 | 1.000 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### bmr_canonical (none)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38713 | -4.51 | -27.13 | -86.86 | 1364 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24518 | -4.49 | -26.95 | -72.23 | 869 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -4.49 | -27.77 | -49.06 | 434 | 0.62 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -5.39 | -25.75 | -8.51 | 60 | 0.62 |

### bmr_regime_sma200 (sma_trend)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38713 | -3.98 | -19.06 | -74.18 | 849 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24518 | -3.76 | -18.25 | -56.17 | 535 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -4.28 | -20.51 | -37.75 | 272 | 0.62 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -5.06 | -20.02 | -6.45 | 42 | 0.62 |

### bmr_rv_lowvol_30d (rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38713 | -4.10 | -15.50 | -65.98 | 723 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24518 | -4.09 | -14.40 | -46.89 | 418 | 0.58 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -3.87 | -16.19 | -30.72 | 260 | 0.62 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -6.00 | -25.19 | -8.31 | 45 | 0.62 |

### bmr_rv_highvol_30d (rv_highvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38713 | -2.25 | -11.68 | -56.63 | 601 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24518 | -2.19 | -11.51 | -41.42 | 405 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -2.62 | -13.74 | -26.75 | 178 | 0.62 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | 0.27 | 0.70 | -1.44 | 17 | 0.50 |

### bmr_regime_combo (sma_trend_AND_rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 38713 | -3.48 | -10.54 | -51.21 | 457 | 0.62 |
| IS | 2020-01-06 | 2023-12-31 | 24518 | -3.14 | -8.82 | -31.57 | 259 | 0.62 |
| OOS | 2024-01-01 | 2025-12-31 | 12440 | -3.77 | -12.77 | -24.65 | 169 | 0.67 |
| FWD | 2026-01-01 | 2026-04-14 | 1755 | -5.59 | -18.10 | -5.81 | 29 | 0.62 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-42.38%** | IR: **-2.286** | Corr: **+0.017** | Beta: **+0.006**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Regime-aware features: `[advances_fin_ml, ch.17]`
- SMA trend regime: `[stocks_on_the_move, p.110]`
- Realized-vol regime: `[volatility_trading]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
