# QQQ_XLK daily — V2-L5 Kalman pair cointegration (iter 61)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (6 gates)
**Config:** `kalman_eg_2sigma_30d` — EG ADF alpha=0.05, Kalman delta=1e-05, V_e=0.001, entry=±2.0σ, exit=0.0σ, stop=±4.0σ, hold cap=30d
**Window:** 2003-08-20 → 2026-04-14 (5698 bars)

## Cointegration gate (Engle-Granger two-step, full-series)

- OLS: `log(y) = 1.4858 + 1.0136 * log(x) + residuals`
- ADF on residuals: stat=-1.237, p-value=0.6576 → **FAIL** (alpha=0.05)
- Final Kalman beta: 0.9449

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2003-08-20 → 2019-06-24 | 3988 | 0.000 | 0.00% | 0.00% | 1.000 |
| OOS | 2019-06-25 → 2024-01-03 | 1140 | 0.000 | 0.00% | 0.00% | 1.000 |
| FWD | 2024-01-04 → 2026-04-14 | 570 | 0.000 | 0.00% | 0.00% | 1.000 |

## Walk-forward (8 windows)

- Profitable windows: **0.00** (target ≥ 0.75)
- Max window drawdown: **0.0%** (cap 25%)
- Pass: **NO**

## Hold / event diagnostics

- Median hold: **0.0 days** (target ≥ 3d, V2 spec §1)
- Entry signals observed: 0
- Round-trips executed: 0

## Cost breakdown (Pepperstone Razor retail, both legs)

- Cumulative transaction cost: **0.000%** of starting equity
- Cumulative overnight swap: **0.000%** of starting equity
- Spread half: 2.0 bps | commission RT per leg: 6.6 bps | slippage RT per leg: 3.0 bps | swap daily per leg: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 0.000 | ❌ |
| fwd_sharpe_gt_0 | 0.000 | ❌ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 0.0d | ❌ |
| oos_cagr_ge_30pct | 0.0% | ❌ |
| oos_sharpe_ge_2 | 0.000 | ❌ |
| oos_maxdd_le_25pct | 0.0% | ✅ |

**Subset FAIL** — 6 gate(s): oos_sharpe_gt_0, fwd_sharpe_gt_0, wf_pass, median_hold_ge_3d, oos_cagr_ge_30pct, oos_sharpe_ge_2.

## Citations

- Engle-Granger cointegration, ADF on residuals: `[algo_trading_chan, p.42-46]`.
- Kalman dynamic hedge ratio for pair trading: `[machine_trading_chan, ch.3]`.
- Z-score entry/exit at ±2σ: `[algo_trading_chan, p.47-54]`.
- Walk-forward 6/8 + MaxDD 25%: `[advances_fin_ml, ch.11]`.
- Hold economics (retail cost amortization): `[systematic_trading, p.185-188]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

