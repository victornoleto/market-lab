# QQQ 1h — T5 BollingerMR + regime overlay

**Window:** 2020-01-06 → 2026-04-14 (9456 bars, 1h equity)
**Costs:** half_spread=2.0bps, swap=0.0050%/day

**Best config:** `bmr_rv_highvol_30d` — **NO PASS**

## Cross-config gates
- PBO across 5 configs: **0.5913** (pass=False)

## All configs — OOS metrics + 5-gate

| Config | Regime | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| `bmr_canonical` | none | -1.01 | -13.48 | -30.15 | 118 | 2.94 | 0.680 | 2/8 | ✗ | ✓ | ✓ | **fail** |
| `bmr_regime_sma200` | sma_trend | -0.87 | -8.36 | -20.56 | 85 | 2.21 | 0.920 | 2/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_rv_lowvol_30d` | rv_lowvol | -0.98 | -10.13 | -25.46 | 80 | 2.92 | 0.492 | 3/8 | ✗ | ✓ | ✓ | **fail** |
| `bmr_rv_highvol_30d` | rv_highvol | -0.69 | -6.05 | -15.16 | 39 | 2.92 | 0.781 | 1/8 | ✗ | ✗ | ✓ | **fail** |
| `bmr_regime_combo` | sma_trend_AND_rv_lowvol | -0.83 | -6.46 | -17.73 | 60 | 2.06 | 0.931 | 0/8 | ✗ | ✗ | ✓ | **fail** |

## Per-config window breakdown

### bmr_canonical (none)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | -0.20 | -4.11 | -31.38 | 379 | 2.08 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | 0.09 | 0.18 | -21.72 | 248 | 2.04 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -1.01 | -13.48 | -30.15 | 118 | 2.94 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | 1.41 | 17.66 | -4.27 | 13 | 2.00 |

### bmr_regime_sma200 (sma_trend)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | -0.61 | -6.47 | -32.54 | 242 | 2.12 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | -0.45 | -5.25 | -27.90 | 154 | 2.10 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -0.87 | -8.36 | -20.56 | 85 | 2.21 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | -1.06 | -5.57 | -3.12 | 2 | 3.60 |

### bmr_rv_lowvol_30d (rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | 0.01 | -0.37 | -26.45 | 214 | 2.56 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | 0.52 | 4.37 | -11.41 | 121 | 2.96 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -0.98 | -10.13 | -25.46 | 80 | 2.92 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | 1.41 | 17.66 | -4.27 | 13 | 2.00 |

### bmr_rv_highvol_30d (rv_highvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | -0.34 | -3.43 | -18.96 | 109 | 2.08 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | -0.19 | -2.33 | -16.31 | 70 | 2.00 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -0.69 | -6.05 | -15.16 | 39 | 2.92 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | 0.00 | 0.00 | 0.00 | 0 | 0.00 |

### bmr_regime_combo (sma_trend_AND_rv_lowvol)

| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| FULL | 2020-01-06 | 2026-04-14 | 9456 | -0.64 | -4.39 | -23.81 | 143 | 2.92 |
| IS | 2020-01-06 | 2023-12-31 | 6024 | -0.45 | -2.92 | -15.03 | 80 | 3.00 |
| OOS | 2024-01-01 | 2025-12-31 | 3012 | -0.83 | -6.46 | -17.73 | 60 | 2.06 |
| FWD | 2026-01-01 | 2026-04-14 | 420 | -1.06 | -5.57 | -3.12 | 2 | 3.60 |

## Benchmark — SPY buy & hold (same window)
- SPY Return / CAGR / MaxDD / Sharpe: **134.95%** / **14.64%/yr** / **33.70%** / **0.769**
- Strategy vs SPY — Excess CAGR: **-18.18%** | IR: **-0.780** | Corr: **+0.142** | Beta: **+0.102**
- _Strategy first-config equity resampled daily; SPY from Tiingo cache_

## Citations
- Regime-aware features: `[advances_fin_ml, ch.17]`
- SMA trend regime: `[stocks_on_the_move, p.110]`
- Realized-vol regime: `[volatility_trading]`
- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`
