# FINAL — Best strategies on REAL QQQ (NASDAQ-100) data

> Real-ETF validation of the SPYSIM synth study. Data window: **2010-02-12 → 2026-04-20** (4070 bars, ~16.2 years).  
> Signal asset: `QQQ`. Buy tickers: L1=QQQ, L2=QLD, L3=TQQQ. Sell leg with L<0 uses synth inverse (absent in Tiingo cache).  
> Educational / experimental — does NOT claim PASS on the mandate.

## Benchmark: QQQ buy-and-hold over the same window

| CAGR | Sharpe | Max DD | Calmar | Volatility |
|---|---|---|---|---|
| +19.18% | 0.96 | +35.12% | 0.55 | +20.60% |

## Top-20 by composite (PURE sweep)

| rank | cfg_id | CAGR pure | Sharpe pure | MDD | CAGR tax15 | Δ CAGR tax | gates | excess vs QQQ |
|---|---|---|---|---|---|---|---|---|
| 1 | `SMA_N150_th0_bL2_sL0` | +25.32% | 0.91 | +40.53% | +21.03% | +4.30% | 5/7 | +6.14% |
| 2 | `SMA_N150_th0_bL3_sL0` | +35.76% | 0.91 | +55.08% | +29.85% | +5.91% | 4/7 | +16.57% |
| 3 | `EMA_N150_th5_bL2_sL0` | +23.82% | 0.86 | +41.45% | +20.82% | +3.00% | 5/7 | +4.64% |
| 4 | `EMA_N150_th0_bL2_sL0` | +23.11% | 0.84 | +41.04% | +18.67% | +4.44% | 5/7 | +3.93% |
| 5 | `EMA_N150_th0_bL3_sL0` | +32.26% | 0.85 | +55.33% | +26.15% | +6.11% | 4/7 | +13.08% |
| 6 | `EMA_N150_th5_bL3_sL0` | +32.45% | 0.85 | +56.28% | +28.67% | +3.79% | 4/7 | +13.27% |
| 7 | `SMA_N150_th2_bL2_sL0` | +21.93% | 0.82 | +40.71% | +18.43% | +3.50% | 5/7 | +2.74% |
| 8 | `SMA_N150_th2_bL3_sL0` | +29.75% | 0.81 | +55.30% | +25.19% | +4.56% | 4/7 | +10.57% |
| 9 | `SMA_N200_th0_bL2_sL0` | +21.70% | 0.80 | +42.72% | +18.21% | +3.49% | 4/7 | +2.52% |
| 10 | `EMA_N150_th2_bL2_sL0` | +21.57% | 0.80 | +43.53% | +18.26% | +3.31% | 5/7 | +2.38% |
| 11 | `SMA_N200_th0_bL3_sL0` | +29.58% | 0.80 | +56.96% | +25.10% | +4.48% | 3/7 | +10.40% |
| 12 | `SMA_N150_th0_bL1_sL0` | +13.85% | 0.94 | +22.34% | +11.40% | +2.45% | 6/7 | -5.33% |
| 13 | `EMA_N100_th0_bL3_sL0` | +26.55% | 0.77 | +47.41% | +20.24% | +6.30% | 4/7 | +7.36% |
| 14 | `EMA_N150_th2_bL3_sL0` | +29.18% | 0.80 | +58.93% | +24.88% | +4.30% | 4/7 | +10.00% |
| 15 | `EMA_N150_th5_bL1_sL0` | +13.70% | 0.92 | +23.11% | +11.81% | +1.89% | 6/7 | -5.48% |
| 16 | `EMA_N200_th2_bL2_sL0` | +21.56% | 0.79 | +46.11% | +18.41% | +3.15% | 5/7 | +2.38% |
| 17 | `EMA_N150_th0_bL1_sL0` | +12.80% | 0.87 | +22.85% | +10.26% | +2.54% | 6/7 | -6.38% |
| 18 | `EMA_N200_th2_bL3_sL0` | +28.95% | 0.79 | +61.11% | +24.95% | +4.00% | 4/7 | +9.77% |
| 19 | `SMA_N150_th0_bL3_sL-1` | +28.99% | 0.78 | +61.57% | +23.23% | +5.76% | 4/7 | +9.81% |
| 20 | `SMA_N150_th2_bL1_sL0` | +12.64% | 0.87 | +22.79% | +10.52% | +2.12% | 6/7 | -6.55% |

## Top-20 by composite (TAX=15% sweep)

| rank | cfg_id | CAGR tax15 | Sharpe tax15 | MDD | CAGR pure | Δ CAGR tax | gates | excess vs QQQ |
|---|---|---|---|---|---|---|---|---|
| 1 | `SMA_N150_th0_bL2_sL0` | +21.03% | 0.78 | +40.95% | +25.32% | +4.30% | 5/7 | +1.85% |
| 2 | `SMA_N150_th0_bL3_sL0` | +29.85% | 0.81 | +55.33% | +35.76% | +5.91% | 4/7 | +10.66% |
| 3 | `EMA_N150_th5_bL2_sL0` | +20.82% | 0.76 | +45.91% | +23.82% | +3.00% | 5/7 | +1.64% |
| 4 | `EMA_N150_th0_bL3_sL0` | +26.15% | 0.74 | +56.91% | +32.26% | +6.11% | 4/7 | +6.97% |
| 5 | `EMA_N150_th5_bL3_sL0` | +28.67% | 0.78 | +59.66% | +32.45% | +3.79% | 4/7 | +9.48% |
| 6 | `SMA_N150_th2_bL3_sL0` | +25.19% | 0.73 | +58.27% | +29.75% | +4.56% | 4/7 | +6.01% |
| 7 | `EMA_N150_th0_bL2_sL0` | +18.67% | 0.71 | +42.59% | +23.11% | +4.44% | 5/7 | -0.52% |
| 8 | `SMA_N150_th2_bL2_sL0` | +18.43% | 0.71 | +44.57% | +21.93% | +3.50% | 5/7 | -0.76% |
| 9 | `SMA_N200_th0_bL3_sL0` | +25.10% | 0.72 | +61.48% | +29.58% | +4.48% | 3/7 | +5.92% |
| 10 | `EMA_N150_th2_bL3_sL0` | +24.88% | 0.72 | +61.54% | +29.18% | +4.30% | 4/7 | +5.70% |
| 11 | `EMA_N150_th2_bL2_sL0` | +18.26% | 0.70 | +46.91% | +21.57% | +3.31% | 5/7 | -0.93% |
| 12 | `EMA_N150_th5_bL1_sL0` | +11.81% | 0.78 | +27.43% | +13.70% | +1.89% | 6/7 | -7.37% |
| 13 | `EMA_N200_th5_bL2_sL0` | +18.72% | 0.70 | +49.83% | +21.17% | +2.46% | 3/7 | -0.47% |
| 14 | `SMA_N150_th0_bL1_sL0` | +11.40% | 0.77 | +22.82% | +13.85% | +2.45% | 6/7 | -7.78% |
| 15 | `SMA_N200_th0_bL2_sL0` | +18.21% | 0.70 | +47.66% | +21.70% | +3.49% | 4/7 | -0.97% |
| 16 | `EMA_N200_th2_bL3_sL0` | +24.95% | 0.72 | +65.49% | +28.95% | +4.00% | 4/7 | +5.76% |
| 17 | `EMA_N200_th2_bL2_sL0` | +18.41% | 0.70 | +51.24% | +21.56% | +3.15% | 5/7 | -0.78% |
| 18 | `EMA_N200_th5_bL3_sL0` | +24.62% | 0.71 | +66.03% | +27.71% | +3.09% | 3/7 | +5.44% |
| 19 | `EMA_N200_th5_bL1_sL0` | +11.07% | 0.73 | +27.96% | +12.63% | +1.56% | 5/7 | -8.11% |
| 20 | `SMA_N150_th0_bL3_sL-1` | +23.23% | 0.68 | +61.79% | +28.99% | +5.76% | 4/7 | +4.05% |

## Gate pass rates (out of 384, evaluated on PURE sweep)

| gate | pass count | pass rate |
|---|---|---|
| G1 PBO < 0.5 | 384/384 | 100.0% |
| G2 DSR p < 0.05 | 0/384 | 0.0% |
| G3 Walk-Forward 6/8 | 8/384 | 2.1% |
| G4 OOS 70/30 Sharpe > 0 | 321/384 | 83.6% |
| G5 FWD post-2020 Sharpe > 0 | 318/384 | 82.8% |
| G6 Bootstrap 99.9% CI > 0 | 37/384 | 9.6% |
| G7 Cross-lib ±3pp CAGR | 311/384 | 81.0% |

### Distribution of `gates_passed`

- **7/7**: 0 configs
- **6/7**: 7 configs
- **5/7**: 19 configs
- **4/7**: 224 configs
- **3/7**: 83 configs
- **2/7**: 46 configs
- **1/7**: 5 configs
- **0/7**: 0 configs

## Archetypes in the top-20 (PURE)

**By (filter, buy_leverage):**

- EMA + buy×3: 5 configs in the top-20
- EMA + buy×2: 4 configs in the top-20
- SMA + buy×3: 4 configs in the top-20
- SMA + buy×2: 3 configs in the top-20
- EMA + buy×1: 2 configs in the top-20
- SMA + buy×1: 2 configs in the top-20

**By threshold:**

- threshold 0%: 10 configs
- threshold 2%: 7 configs
- threshold 5%: 3 configs

**By sell leg:**

- cash: 19 configs
- -1x synth: 1 configs

## Narrative conclusions

### 1. Best config PURE: `SMA_N150_th0_bL2_sL0`

- CAGR +25.32% vs QQQ B&H +19.18% -> excess +6.14%.
- Sharpe 0.91 vs 0.96.
- MDD +40.53% vs +35.12%.
- Gates: 5/7.

### 2. Best config after 15% swing tax

- Same as PURE (`SMA_N150_th0_bL2_sL0`) — tax doesn't swap the winner (few taxable events in this config).

### 3. Real vs synth comparison caveat

Results on this window (short ~14-17y, post-GFC bull-heavy) are naturally more optimistic for long-only leveraged configs than the 40-year SPYSIM synth. Use both studies **together** — synth (40y) captures multi-regime history; real (this) captures actual ETF tracking vs the daily-rebal theoretical formula. Expect ~2-3pp CAGR drag in real UPRO/TQQQ vs theoretical daily-L × signal per `[leverage_for_the_long_run, p.21, Table 12]`.

### 4. Honest caveats

- **4070 bars (~16.2 years)** = far shorter than the 40y synth study. G3 Walk-Forward still needs ≥ 8 OOS windows (2y IS + 6mo OOS stride 6mo) — this gives only 27 windows, many still MDD > 25% for leveraged configs.
- Bull bias of 2009-2026 (post-GFC recovery + AI rally): SPY CAGR +19.18% vs long-term ~10%. Inflates any momentum/trend-following rule.
- Real SSO/UPRO/QLD/TQQQ have tracking error vs theoretical daily-L that shows up here (compare synth study ranks to real study ranks).
- **Does NOT change the mandate.** 100% Plano C maintenance remains the production decision.

---

*Real data: Tiingo parquet cache. Synth inverse formula: `[leverage_for_the_long_run, p.16, fn.22]`. Gates: PBO `[advances_fin_ml, p.208-211]`, DSR `[p.222-223]`, bootstrap `[p.196-202]`, cross-lib `[p.31-34]`.*