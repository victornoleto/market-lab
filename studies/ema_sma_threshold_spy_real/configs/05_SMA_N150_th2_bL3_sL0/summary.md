# Config SMA_N150_th2_bL3_sL0 — rank 5/384  (REAL SPY (S&P 500))

> Real-ETF validation of the SPYSIM synth study. Buy leg uses **real Tiingo returns**; sell leg is cash or synth inverse (inverse LETFs absent from cache). Educational — not production.

## Parameters

| param | value | source |
|---|---|---|
| MA filter | SMA | `[leverage_for_the_long_run, p.8]` |
| lookback | 150 bars | `[leverage_for_the_long_run, p.14, Table 6]` |
| threshold | ±2% | `[leverage_for_the_long_run, p.11]` |
| buy leg | ×3 = **UPRO** (real Tiingo) | Tiingo storage |
| sell leg | ×0 = cash (0.0% annual) | synth via `[p.16, fn.22]` if <0 |
| annual fee (synth sell only) | 0.95% | `[p.16, fn.23]` |
| switch cost | 15 bps/transition | mirror `letf_rotation.py` |

## Metrics — pure vs tax=15% vs SPY buy-hold

| metric | pure | tax=15% | SPY B&H | tax drag |
|---|---|---|---|---|
| CAGR | +20.36% | +17.20% | +15.00% | +3.16% |
| Sharpe | 0.71 | 0.63 | 0.90 | 0.08 |
| Max Drawdown | +58.21% | +62.13% | +33.70% | — |
| Calmar | 0.35 | 0.28 | 0.45 | — |
| Sortino | 0.97 | 0.85 | 1.27 | — |
| Volatility | +34.55% | +35.27% | +17.15% | — |
| n_switches | 34 | 34 | 0 | — |

*Tax drag = +3.16% CAGR = 15.5% of the pure edge.*

## Gates (informational; evaluated on PURE sweep, signal returns = real SPY)

| gate | verdict | citation |
|---|---|---|
| G1 PBO < 0.5 | PASS | `[advances_fin_ml, p.208-211]` |
| G2 DSR p < 0.05 | FAIL | `[advances_fin_ml, p.222-223]` |
| G3 Walk-Forward 6/8 + MDD<25% | FAIL | `[advances_fin_ml, ch.12]` |
| G4 OOS 70/30 Sharpe > 0 | PASS | `mandate §5` |
| G5 FWD stress post-2020 Sharpe > 0 | PASS | `mandate §5` |
| G6 Bootstrap 99.9% CI low > 0 | FAIL | `[advances_fin_ml, p.196-202]` |
| G7 Cross-lib ±3pp CAGR | FAIL | `[advances_fin_ml, p.31-34]` |


**Gates passed: 3/7**

## Trade summary (regime blocks)

- **Total trades**: 35 (18 long, 17 short/cash)
- **Long-leg profitable**: 11/18 (61.1%)
- **Short-leg profitable**: 0/17 (0.0%)
- **Avg hold — long**: 187 bars (0.7 years)
- **Avg hold — short/cash**: 42 bars (0.2 years)
- **Cumulative tax paid (tax=15%)**: 3.0107 (absolute equity units)


See `trades.csv` for the complete regime-block ledger.

## Plot

![equity curve](equity.png)

---

*Real-data source: Tiingo daily prices for UPRO (buy) + SPY (signal). Inverse LETFs absent from cache → synth fallback for sell_leverage < 0.*