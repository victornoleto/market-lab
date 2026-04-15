# Ehlers BP Swing — Multi-Asset Survey
Survey of the Ehlers Band-Pass Swing strategy (24-config grid: hp_period × lp_period × pct_of_dcp × stop_pct) against a curated basket of assets. Storage-first via Tiingo (survivorship-free for ETFs/crypto; equities-only universe still has minor residual). Each grid evaluated against PBO < 0.5, DSR p < 0.05, WF ≥ 6/8.
- **Assets evaluated:** 16 (most recent run per symbol)
- **Strategy:** EhlersBPSwingStrategy (single-instrument, long-flat)
- **Grid size:** 24 configs per asset
- **Data:** Tiingo daily OHLCV, `data/tiingo` canonical store, adj_close-rebased OHLC (commit `5ca9410`)
- **Generated:** by `scripts/build_ehlers_summary.py` from per-asset `reports/grid_ehlers_<symbol>_<ts>/diagnostic.md`

## TL;DR — 0 PASS / 16 FAIL

**Every asset failed the 3-gate framework.** The best Sharpe across the basket comes from BTCUSD (cyclical by nature) but still rejects on DSR and WF. The Ehlers BP Swing single-instrument strategy as currently parametrized does not exhibit exploitable edge in any of the tested regimes.

## Verdict table

| Symbol | Verdict | PBO | DSR | WF | Best Sharpe | Best CAGR | Best DD | Failure modes |
|---|---|---|---|---|---|---|---|---|
| **BTCUSD** | ❌ FAIL | 0.377 | 0/24 | 0/24 | 0.95 | 21.66% | 50.48% | DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **ETHUSD** | ❌ FAIL | 0.290 | 0/24 | 0/24 | 0.77 | 23.04% | 46.90% | DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **XLK** | ❌ FAIL | 0.563 | 0/24 | 0/24 | 0.73 | 13.51% | 38.69% | PBO_HIGH, DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **QQQ** | ❌ FAIL | 0.611 | 0/24 | 0/24 | 0.67 | 10.15% | 40.64% | PBO_HIGH, DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **SPY** | ❌ FAIL | 0.405 | 0/24 | 0/24 | 0.64 | 9.25% | 29.44% | DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **IWM** | ❌ FAIL | 0.964 | 0/24 | 0/24 | 0.39 | 5.76% | 41.25% | PBO_HIGH, DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **XLU** | ❌ FAIL | 0.734 | 0/24 | 0/24 | 0.37 | 4.90% | 37.54% | PBO_HIGH, DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **USO** | ❌ FAIL | 0.659 | 0/24 | 1/24 | 0.36 | 3.12% | 33.99% | PBO_HIGH, DSR_ALL_FAIL, COMBINED |
| **XLF** | ❌ FAIL | 0.298 | 0/24 | 0/24 | 0.35 | 5.65% | 43.82% | DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **XLE** | ❌ FAIL | 0.508 | 0/24 | 0/24 | 0.28 | 4.03% | 65.30% | PBO_HIGH, DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **EFA** | ❌ FAIL | 0.230 | 0/24 | 0/24 | 0.27 | 3.32% | 40.98% | DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **GLD** | ❌ FAIL | 0.698 | 0/24 | 0/24 | 0.21 | 1.25% | 14.45% | PBO_HIGH, DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **TLT** | ❌ FAIL | 0.278 | 0/24 | 0/24 | 0.13 | 0.81% | 50.50% | DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **EEM** | ❌ FAIL | 0.472 | 0/24 | 0/24 | 0.09 | -2.39% | 77.82% | DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **DBA** | ❌ FAIL | 0.524 | 0/24 | 0/24 | 0.04 | -0.20% | 46.41% | PBO_HIGH, DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |
| **SLV** | ❌ FAIL | 0.349 | 0/24 | 0/24 | -0.01 | -7.54% | 89.28% | DSR_ALL_FAIL, WF_INSUFFICIENT, COMBINED |

## Notes

- **Best Sharpe row** is the per-grid champion *ignoring* gates. It is the number you would have reported in a naive backtest; the gates exist to deflate it.
- **PBO** measures probability of backtest overfitting via combinatorial purged splits. < 0.5 is the gate; > 0.5 means the Sharpe ranking is essentially noise.
- **DSR** (Deflated Sharpe Ratio, López de Prado) tests Sharpe significance after correcting for multiple trials (24 here). p < 0.05 needed to reject the null of no skill.
- **WF** (walk-forward) requires ≥ 6/8 windows profitable AND drawdown ≤ 25% per window. Tests temporal generalization.
- All grids use **n_jobs=4**, ~5s wallclock per asset.

## Known issues (excluded from this run)

- **VXX**: hits `TypeError: float() not 'complex'` in `_safe_cagr` — equity curve goes near-zero (VXX decay), `cagr()` returns complex. Bug in `backtest/grid/runner.py:186`.
- **EURUSD / USDJPY / GBPUSD**: Tiingo FX endpoint returns 400 with current `_build_params`. Likely needs `resampleFreq=1day` added for forex (currently only set for crypto).

## Comparison vs pre-fix (yfinance Run 2, raw close)

This survey uses Tiingo's survivorship-free dataset WITH the `adjust_ohlc` fix (commit `5ca9410`). Pre-fix, the single-asset runs from 2026-04-14 showed best-Sharpe values in the 0.10–0.27 range across all ETFs; post-fix, SPY/QQQ/XLK/IWM all moved into the 0.39–0.73 band. Crypto (BTCUSD/ETHUSD) is unchanged because perpetual spot prices carry no dividend or split events.

The **gate verdicts did not change** — WF collapses on the longer 2005-2023 window for every ETF (2008-2009 crash + 2020 COVID + 2022 rate regime break generalization); DSR still deflates the improved Sharpes below p<0.05 at N=24 trials. The raw signal is materially better than pre-fix, but N is too small and T is not long enough to clear the statistical bar.

