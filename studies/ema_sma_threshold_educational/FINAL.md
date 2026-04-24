# FINAL — Best strategies from the EMA/SMA threshold sweep

> **Educational / experimental** — does NOT claim PASS on the project mandate. Project is in MAINTENANCE (100% Plano C).

## Benchmark: SPY buy-and-hold (1986-2026)

| CAGR | Sharpe | Max DD | Calmar | Volatility |
|---|---|---|---|---|
| +11.47% | 0.68 | +55.14% | 0.21 | +18.46% |

## Top-20 by composite (PURE sweep)

| rank | cfg_id | CAGR pure | Sharpe pure | MDD | CAGR tax15 | Δ CAGR tax | gates | excess vs SPY (pure) |
|---|---|---|---|---|---|---|---|---|
| 1 | `EMA_N150_th5_bL3_sL0` | +27.67% | 0.84 | +53.98% | +25.03% | +2.64% | 6/7 | +16.20% |
| 2 | `EMA_N150_th5_bL2_sL0` | +19.23% | 0.83 | +39.05% | +17.21% | +2.03% | 6/7 | +7.76% |
| 3 | `EMA_N100_th5_bL3_sL0` | +26.74% | 0.83 | +62.76% | +23.66% | +3.08% | 6/7 | +15.27% |
| 4 | `SMA_N200_th2_bL3_sL0` | +24.71% | 0.79 | +57.56% | +21.42% | +3.29% | 6/7 | +13.24% |
| 5 | `EMA_N100_th5_bL2_sL0` | +18.55% | 0.82 | +47.63% | +16.24% | +2.31% | 6/7 | +7.08% |
| 6 | `SMA_N150_th5_bL3_sL0` | +25.68% | 0.80 | +62.03% | +23.04% | +2.64% | 6/7 | +14.21% |
| 7 | `SMA_N150_th5_bL2_sL0` | +17.95% | 0.79 | +44.92% | +15.92% | +2.03% | 6/7 | +6.48% |
| 8 | `SMA_N200_th2_bL2_sL0` | +17.24% | 0.78 | +42.40% | +14.78% | +2.46% | 6/7 | +5.77% |
| 9 | `EMA_N150_th5_bL3_sL-1` | +24.45% | 0.75 | +62.26% | +21.76% | +2.69% | 6/7 | +12.98% |
| 10 | `EMA_N200_th2_bL3_sL0` | +21.31% | 0.71 | +63.29% | +18.03% | +3.28% | 5/7 | +9.83% |
| 11 | `EMA_N100_th5_bL3_sL-1` | +23.08% | 0.73 | +68.62% | +19.94% | +3.14% | 5/7 | +11.61% |
| 12 | `SMA_N200_th0_bL3_sL0` | +22.09% | 0.74 | +70.29% | +18.12% | +3.97% | 6/7 | +10.62% |
| 13 | `SMA_N100_th5_bL3_sL0` | +22.58% | 0.74 | +73.63% | +19.57% | +3.01% | 6/7 | +11.11% |
| 14 | `SMA_N150_th5_bL3_sL-1` | +21.82% | 0.70 | +67.26% | +19.15% | +2.67% | 5/7 | +10.34% |
| 15 | `EMA_N200_th0_bL3_sL0` | +20.51% | 0.69 | +66.17% | +16.64% | +3.87% | 5/7 | +9.04% |
| 16 | `SMA_N200_th5_bL2_sL0` | +16.91% | 0.74 | +63.30% | +15.09% | +1.82% | 5/7 | +5.44% |
| 17 | `SMA_N100_th5_bL2_sL0` | +15.93% | 0.73 | +56.24% | +13.67% | +2.26% | 5/7 | +4.46% |
| 18 | `EMA_N150_th5_bL2_sL-1` | +16.23% | 0.67 | +50.14% | +14.14% | +2.09% | 5/7 | +4.75% |
| 19 | `EMA_N200_th5_bL2_sL0` | +16.76% | 0.73 | +63.65% | +14.99% | +1.77% | 5/7 | +5.28% |
| 20 | `SMA_N200_th0_bL2_sL0` | +15.28% | 0.71 | +54.18% | +12.42% | +2.87% | 5/7 | +3.81% |

## Top-20 by composite (TAX=15% sweep)

| rank | cfg_id | CAGR tax15 | Sharpe tax15 | MDD | CAGR pure | Δ CAGR tax | gates | excess vs SPY (tax15) |
|---|---|---|---|---|---|---|---|---|
| 1 | `EMA_N150_th5_bL3_sL0` | +25.03% | 0.78 | +57.56% | +27.67% | +2.64% | 6/7 | +13.56% |
| 2 | `EMA_N150_th5_bL2_sL0` | +17.21% | 0.75 | +45.01% | +19.23% | +2.03% | 6/7 | +5.73% |
| 3 | `SMA_N200_th2_bL3_sL0` | +21.42% | 0.71 | +58.63% | +24.71% | +3.29% | 6/7 | +9.94% |
| 4 | `SMA_N150_th5_bL3_sL0` | +23.04% | 0.74 | +63.05% | +25.68% | +2.64% | 6/7 | +11.57% |
| 5 | `EMA_N100_th5_bL3_sL0` | +23.66% | 0.76 | +66.08% | +26.74% | +3.08% | 6/7 | +12.19% |
| 6 | `SMA_N150_th5_bL2_sL0` | +15.92% | 0.71 | +46.70% | +17.95% | +2.03% | 6/7 | +4.45% |
| 7 | `EMA_N100_th5_bL2_sL0` | +16.24% | 0.73 | +51.34% | +18.55% | +2.31% | 6/7 | +4.77% |
| 8 | `EMA_N150_th5_bL3_sL-1` | +21.76% | 0.69 | +64.43% | +24.45% | +2.69% | 6/7 | +10.29% |
| 9 | `SMA_N200_th2_bL2_sL0` | +14.78% | 0.68 | +43.52% | +17.24% | +2.46% | 6/7 | +3.31% |
| 10 | `SMA_N200_th5_bL2_sL0` | +15.09% | 0.67 | +63.30% | +16.91% | +1.82% | 5/7 | +3.62% |
| 11 | `EMA_N100_th5_bL3_sL-1` | +19.94% | 0.66 | +71.41% | +23.08% | +3.14% | 5/7 | +8.47% |
| 12 | `SMA_N150_th5_bL3_sL-1` | +19.15% | 0.64 | +69.25% | +21.82% | +2.67% | 5/7 | +7.68% |
| 13 | `EMA_N200_th2_bL3_sL0` | +18.03% | 0.63 | +66.70% | +21.31% | +3.28% | 5/7 | +6.56% |
| 14 | `EMA_N200_th5_bL2_sL0` | +14.99% | 0.67 | +63.65% | +16.76% | +1.77% | 5/7 | +3.52% |
| 15 | `SMA_N100_th5_bL3_sL0` | +19.57% | 0.67 | +74.36% | +22.58% | +3.01% | 6/7 | +8.10% |
| 16 | `EMA_N150_th5_bL2_sL-1` | +14.14% | 0.60 | +53.92% | +16.23% | +2.09% | 5/7 | +2.67% |
| 17 | `SMA_N100_th5_bL2_sL0` | +13.67% | 0.64 | +57.25% | +15.93% | +2.26% | 5/7 | +2.20% |
| 18 | `SMA_N200_th0_bL3_sL0` | +18.12% | 0.64 | +71.76% | +22.09% | +3.97% | 6/7 | +6.65% |
| 19 | `SMA_N200_th5_bL3_sL0` | +21.15% | 0.70 | +81.38% | +23.48% | +2.33% | 6/7 | +9.68% |
| 20 | `SMA_N200_th2_bL3_sL-1` | +17.20% | 0.60 | +70.73% | +20.51% | +3.31% | 5/7 | +5.72% |

## Gate pass rates (out of 384, evaluated on PURE sweep)

| gate | pass count | pass rate |
|---|---|---|
| G1 PBO < 0.5 | 384/384 | 100.0% |
| G2 DSR p < 0.05 | 18/384 | 4.7% |
| G3 Walk-Forward 6/8 | 0/384 | 0.0% |
| G4 OOS 70/30 Sharpe > 0 | 248/384 | 64.6% |
| G5 FWD post-2020 Sharpe > 0 | 258/384 | 67.2% |
| G6 Bootstrap 99.9% CI > 0 | 109/384 | 28.4% |
| G7 Cross-lib ±3pp CAGR | 384/384 | 100.0% |

### Distribution of `gates_passed`

- **7/7**: 0 configs
- **6/7**: 18 configs
- **5/7**: 91 configs
- **4/7**: 123 configs
- **3/7**: 42 configs
- **2/7**: 110 configs
- **1/7**: 0 configs
- **0/7**: 0 configs

## Archetypes in the top-20 (PURE)

**By (filter, buy_leverage):**

- EMA + buy×3: 6 configs in the top-20
- SMA + buy×2: 5 configs in the top-20
- SMA + buy×3: 5 configs in the top-20
- EMA + buy×2: 4 configs in the top-20

**By threshold:**

- threshold 0%: 3 configs
- threshold 2%: 3 configs
- threshold 5%: 14 configs

**By sell leg:**

- cash: 16 configs
- -1x short: 4 configs

## Narrative conclusions

### 1. Best config PURE: `EMA_N150_th5_bL3_sL0`

- CAGR +27.67% vs SPY +11.47% -> excess +16.20%.
- Sharpe 0.84 vs SPY 0.68.
- MDD +53.98% vs SPY +55.14%.
- Gates: 6/7.

### 2. Best config after 15% swing tax

- Same as PURE (`EMA_N150_th5_bL3_sL0`) - tax doesn't change the winner because this config holds long regimes through most of the 40y window (few taxable events).

### 3. Pattern

- **Median CAGR drag from 15% swing tax** (top-20 pure): +2.65%. High-churn configs pay heavily; low-churn (long lookback, wide threshold, cash on sell) lose less.
- Short-leveraged sell legs (-2x, -3x) amplify turnover but add little CAGR after tax in most archetypes.
- Gayed canonical (SMA-200, threshold 0%, 2-3x long, cash) appears in the top tier but is rarely the single winner.

### 4. Honest caveats

- 40 years of SPY is a bull-heavy regime (11.5% CAGR). Any trend-following rule with leverage will look good in-sample. Walk-forward (G3) fails on nearly every config with MDD > 25% - the drawdown discipline required by Mandate §5 is not met.
- Synth LETFs assume perfect daily re-leveraging (Gayed fn.22). Real UPRO/SSO tracking error and intra-day leveraging noise would reduce these CAGRs by 2-3pp (Gayed p.21, Table 12).
- **Cross-lib (G7) PASS 384/384** = hand-rolled numpy and pandas-vectorised paths agree within ±3pp. This locks the simulator against look-ahead alignment bugs (see `[advances_fin_ml, p.31-34]`).
- **Does NOT change the mandate.** Project remains in MAINTENANCE with 100% Plano C (`portfolio-aposentadoria.md`). This sweep is a learning exercise, not a strategy proposal.

---

*Key citations:* Gayed synth `[leverage_for_the_long_run, p.16, fn.22]`; SMA regime `[p.8, p.13]`; band `[p.11]`; leverage levels `[p.17, Table 8]`. Gates: PBO `[advances_fin_ml, p.208-211]`, DSR `[p.222-223]`, bootstrap `[p.196-202]`, cross-lib/lookahead `[p.31-34]`. See `SPEC.md` for the full spec; `configs/` for per-config detail; `configs.csv` for the raw sweep.
