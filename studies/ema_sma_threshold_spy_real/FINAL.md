# FINAL — Best strategies on REAL SPY (S&P 500) data

> Real-ETF validation of the SPYSIM synth study. Data window: **2009-06-26 → 2026-04-20** (4229 bars, ~16.8 years).  
> Signal asset: `SPY`. Buy tickers: L1=SPY, L2=SSO, L3=UPRO. Sell leg with L<0 uses synth inverse (absent in Tiingo cache).  
> Educational / experimental — does NOT claim PASS on the mandate.

## Benchmark: SPY buy-and-hold over the same window

| CAGR | Sharpe | Max DD | Calmar | Volatility |
|---|---|---|---|---|
| +15.00% | 0.90 | +33.70% | 0.45 | +17.15% |

## Top-20 by composite (PURE sweep)

| rank | cfg_id | CAGR pure | Sharpe pure | MDD | CAGR tax15 | Δ CAGR tax | gates | excess vs SPY |
|---|---|---|---|---|---|---|---|---|
| 1 | `EMA_N150_th5_bL2_sL0` | +15.10% | 0.71 | +39.11% | +13.25% | +1.85% | 4/7 | +0.10% |
| 2 | `SMA_N150_th2_bL2_sL0` | +15.10% | 0.73 | +43.43% | +12.67% | +2.42% | 5/7 | +0.10% |
| 3 | `EMA_N150_th5_bL1_sL0` | +9.20% | 0.79 | +21.15% | +8.03% | +1.17% | 4/7 | -5.79% |
| 4 | `EMA_N150_th5_bL3_sL0` | +20.25% | 0.70 | +54.23% | +17.87% | +2.38% | 3/7 | +5.25% |
| 5 | `SMA_N150_th2_bL3_sL0` | +20.36% | 0.71 | +58.21% | +17.20% | +3.16% | 3/7 | +5.37% |
| 6 | `SMA_N150_th2_bL1_sL0` | +9.00% | 0.80 | +24.06% | +7.48% | +1.51% | 5/7 | -6.00% |
| 7 | `SMA_N200_th2_bL2_sL0` | +13.73% | 0.66 | +42.13% | +11.44% | +2.29% | 4/7 | -1.27% |
| 8 | `EMA_N100_th5_bL2_sL0` | +14.50% | 0.70 | +49.71% | +12.42% | +2.07% | 4/7 | -0.50% |
| 9 | `SMA_N100_th0_bL3_sL0` | +17.67% | 0.66 | +50.23% | +13.09% | +4.59% | 4/7 | +2.68% |
| 10 | `SMA_N200_th0_bL2_sL0` | +13.25% | 0.65 | +38.96% | +10.49% | +2.76% | 4/7 | -1.74% |
| 11 | `SMA_N150_th0_bL2_sL0` | +13.32% | 0.66 | +42.66% | +10.34% | +2.98% | 4/7 | -1.67% |
| 12 | `EMA_N100_th5_bL1_sL0` | +8.78% | 0.77 | +28.27% | +7.45% | +1.33% | 4/7 | -6.21% |
| 13 | `SMA_N200_th2_bL1_sL0` | +8.45% | 0.74 | +23.52% | +6.99% | +1.46% | 4/7 | -6.54% |
| 14 | `SMA_N200_th0_bL3_sL0` | +17.82% | 0.65 | +52.42% | +14.16% | +3.66% | 3/7 | +2.83% |
| 15 | `SMA_N100_th0_bL2_sL0` | +12.62% | 0.65 | +36.68% | +9.36% | +3.27% | 5/7 | -2.37% |
| 16 | `EMA_N150_th2_bL1_sL0` | +8.70% | 0.76 | +30.75% | +7.15% | +1.55% | 5/7 | -6.30% |
| 17 | `SMA_N150_th5_bL1_sL0` | +8.33% | 0.73 | +23.93% | +7.13% | +1.20% | 4/7 | -6.66% |
| 18 | `EMA_N150_th2_bL2_sL0` | +14.34% | 0.69 | +52.64% | +11.85% | +2.49% | 4/7 | -0.66% |
| 19 | `SMA_N150_th5_bL2_sL0` | +13.41% | 0.65 | +43.26% | +11.55% | +1.86% | 4/7 | -1.58% |
| 20 | `SMA_N200_th2_bL3_sL0` | +18.19% | 0.65 | +57.43% | +15.25% | +2.94% | 3/7 | +3.19% |

## Top-20 by composite (TAX=15% sweep)

| rank | cfg_id | CAGR tax15 | Sharpe tax15 | MDD | CAGR pure | Δ CAGR tax | gates | excess vs SPY |
|---|---|---|---|---|---|---|---|---|
| 1 | `EMA_N150_th5_bL2_sL0` | +13.25% | 0.63 | +39.18% | +15.10% | +1.85% | 4/7 | -1.74% |
| 2 | `EMA_N150_th5_bL3_sL0` | +17.87% | 0.64 | +54.23% | +20.25% | +2.38% | 3/7 | +2.87% |
| 3 | `EMA_N150_th5_bL1_sL0` | +8.03% | 0.68 | +22.10% | +9.20% | +1.17% | 4/7 | -6.96% |
| 4 | `SMA_N150_th2_bL2_sL0` | +12.67% | 0.62 | +47.67% | +15.10% | +2.42% | 5/7 | -2.32% |
| 5 | `SMA_N150_th2_bL1_sL0` | +7.48% | 0.66 | +27.65% | +9.00% | +1.51% | 5/7 | -7.51% |
| 6 | `SMA_N150_th5_bL2_sL0` | +11.55% | 0.57 | +43.26% | +13.41% | +1.86% | 4/7 | -3.45% |
| 7 | `SMA_N150_th2_bL3_sL0` | +17.20% | 0.63 | +62.13% | +20.36% | +3.16% | 3/7 | +2.20% |
| 8 | `EMA_N100_th5_bL2_sL0` | +12.42% | 0.61 | +53.23% | +14.50% | +2.07% | 4/7 | -2.57% |
| 9 | `SMA_N200_th2_bL2_sL0` | +11.44% | 0.57 | +43.83% | +13.73% | +2.29% | 4/7 | -3.56% |
| 10 | `EMA_N100_th5_bL1_sL0` | +7.45% | 0.65 | +31.44% | +8.78% | +1.33% | 4/7 | -7.54% |
| 11 | `SMA_N150_th5_bL1_sL0` | +7.13% | 0.62 | +23.93% | +8.33% | +1.20% | 4/7 | -7.87% |
| 12 | `SMA_N150_th5_bL3_sL0` | +15.38% | 0.58 | +58.75% | +17.75% | +2.37% | 3/7 | +0.38% |
| 13 | `SMA_N200_th2_bL3_sL0` | +15.25% | 0.58 | +59.93% | +18.19% | +2.94% | 3/7 | +0.25% |
| 14 | `EMA_N200_th5_bL2_sL0` | +11.08% | 0.54 | +42.17% | +12.77% | +1.68% | 4/7 | -3.92% |
| 15 | `SMA_N200_th2_bL1_sL0` | +6.99% | 0.61 | +24.43% | +8.45% | +1.46% | 4/7 | -8.00% |
| 16 | `EMA_N200_th5_bL1_sL0` | +7.10% | 0.59 | +23.53% | +8.20% | +1.10% | 4/7 | -7.90% |
| 17 | `EMA_N150_th2_bL1_sL0` | +7.15% | 0.62 | +34.17% | +8.70% | +1.55% | 5/7 | -7.84% |
| 18 | `SMA_N200_th5_bL2_sL0` | +11.01% | 0.55 | +43.26% | +12.74% | +1.73% | 4/7 | -3.99% |
| 19 | `SMA_N200_th0_bL3_sL0` | +14.16% | 0.55 | +57.11% | +17.82% | +3.66% | 3/7 | -0.84% |
| 20 | `SMA_N200_th5_bL1_sL0` | +6.95% | 0.60 | +23.93% | +8.06% | +1.11% | 4/7 | -8.05% |

## Gate pass rates (out of 384, evaluated on PURE sweep)

| gate | pass count | pass rate |
|---|---|---|
| G1 PBO < 0.5 | 384/384 | 100.0% |
| G2 DSR p < 0.05 | 0/384 | 0.0% |
| G3 Walk-Forward 6/8 | 0/384 | 0.0% |
| G4 OOS 70/30 Sharpe > 0 | 217/384 | 56.5% |
| G5 FWD post-2020 Sharpe > 0 | 239/384 | 62.2% |
| G6 Bootstrap 99.9% CI > 0 | 6/384 | 1.6% |
| G7 Cross-lib ±3pp CAGR | 323/384 | 84.1% |

### Distribution of `gates_passed`

- **7/7**: 0 configs
- **6/7**: 0 configs
- **5/7**: 5 configs
- **4/7**: 143 configs
- **3/7**: 101 configs
- **2/7**: 134 configs
- **1/7**: 1 configs
- **0/7**: 0 configs

## Archetypes in the top-20 (PURE)

**By (filter, buy_leverage):**

- SMA + buy×2: 6 configs in the top-20
- SMA + buy×3: 4 configs in the top-20
- EMA + buy×1: 3 configs in the top-20
- EMA + buy×2: 3 configs in the top-20
- SMA + buy×1: 3 configs in the top-20
- EMA + buy×3: 1 configs in the top-20

**By threshold:**

- threshold 0%: 5 configs
- threshold 2%: 8 configs
- threshold 5%: 7 configs

**By sell leg:**

- cash: 20 configs

## Narrative conclusions

### 1. Best config PURE: `EMA_N150_th5_bL2_sL0`

- CAGR +15.10% vs SPY B&H +15.00% -> excess +0.10%.
- Sharpe 0.71 vs 0.90.
- MDD +39.11% vs +33.70%.
- Gates: 4/7.

### 2. Best config after 15% swing tax

- Same as PURE (`EMA_N150_th5_bL2_sL0`) — tax doesn't swap the winner (few taxable events in this config).

### 3. Real vs synth comparison caveat

Results on this window (short ~14-17y, post-GFC bull-heavy) are naturally more optimistic for long-only leveraged configs than the 40-year SPYSIM synth. Use both studies **together** — synth (40y) captures multi-regime history; real (this) captures actual ETF tracking vs the daily-rebal theoretical formula. Expect ~2-3pp CAGR drag in real UPRO/TQQQ vs theoretical daily-L × signal per `[leverage_for_the_long_run, p.21, Table 12]`.

### 4. Honest caveats

- **4229 bars (~16.8 years)** = far shorter than the 40y synth study. G3 Walk-Forward still needs ≥ 8 OOS windows (2y IS + 6mo OOS stride 6mo) — this gives only 28 windows, many still MDD > 25% for leveraged configs.
- Bull bias of 2009-2026 (post-GFC recovery + AI rally): SPY CAGR +15.00% vs long-term ~10%. Inflates any momentum/trend-following rule.
- Real SSO/UPRO/QLD/TQQQ have tracking error vs theoretical daily-L that shows up here (compare synth study ranks to real study ranks).
- **Does NOT change the mandate.** 100% Plano C maintenance remains the production decision.

---

*Real data: Tiingo parquet cache. Synth inverse formula: `[leverage_for_the_long_run, p.16, fn.22]`. Gates: PBO `[advances_fin_ml, p.208-211]`, DSR `[p.222-223]`, bootstrap `[p.196-202]`, cross-lib `[p.31-34]`.*