# Config SMA_N150_th5_bL1_sL0 — rank 17/384  (REAL SPY (S&P 500))

> Real-ETF validation of the SPYSIM synth study. Buy leg uses **real Tiingo returns**; sell leg is cash or synth inverse (inverse LETFs absent from cache). Educational — not production.

## Parameters

| param | value | source |
|---|---|---|
| MA filter | SMA | `[leverage_for_the_long_run, p.8]` |
| lookback | 150 bars | `[leverage_for_the_long_run, p.14, Table 6]` |
| threshold | ±5% | `[leverage_for_the_long_run, p.11]` |
| buy leg | ×1 = **SPY** (real Tiingo) | Tiingo storage |
| sell leg | ×0 = cash (0.0% annual) | synth via `[p.16, fn.22]` if <0 |
| annual fee (synth sell only) | 0.95% | `[p.16, fn.23]` |
| switch cost | 15 bps/transition | mirror `letf_rotation.py` |

## Metrics — pure vs tax=15% vs SPY buy-hold

| metric | pure | tax=15% | SPY B&H | tax drag |
|---|---|---|---|---|
| CAGR | +8.33% | +7.13% | +15.00% | +1.20% |
| Sharpe | 0.73 | 0.62 | 0.90 | 0.11 |
| Max Drawdown | +23.93% | +23.93% | +33.70% | — |
| Calmar | 0.35 | 0.30 | 0.45 | — |
| Sortino | 0.99 | 0.82 | 1.27 | — |
| Volatility | +11.89% | +12.31% | +17.15% | — |
| n_switches | 17 | 17 | 0 | — |

*Tax drag = +1.20% CAGR = 14.4% of the pure edge.*

## Gates (informational; evaluated on PURE sweep, signal returns = real SPY)

| gate | verdict | citation |
|---|---|---|
| G1 PBO < 0.5 | PASS | `[advances_fin_ml, p.208-211]` |
| G2 DSR p < 0.05 | FAIL | `[advances_fin_ml, p.222-223]` |
| G3 Walk-Forward 6/8 + MDD<25% | FAIL | `[advances_fin_ml, ch.12]` |
| G4 OOS 70/30 Sharpe > 0 | PASS | `mandate §5` |
| G5 FWD stress post-2020 Sharpe > 0 | PASS | `mandate §5` |
| G6 Bootstrap 99.9% CI low > 0 | FAIL | `[advances_fin_ml, p.196-202]` |
| G7 Cross-lib ±3pp CAGR | PASS | `[advances_fin_ml, p.31-34]` |


**Gates passed: 4/7**

## Trade summary (regime blocks)

- **Total trades**: 18 (9 long, 9 short/cash)
- **Long-leg profitable**: 6/9 (66.7%)
- **Short-leg profitable**: 0/9 (0.0%)
- **Avg hold — long**: 362 bars (1.4 years)
- **Avg hold — short/cash**: 92 bars (0.4 years)
- **Cumulative tax paid (tax=15%)**: 0.4094 (absolute equity units)


See `trades.csv` for the complete regime-block ledger.

## Plot

![equity curve](equity.png)

---

*Real-data source: Tiingo daily prices for SPY (buy) + SPY (signal). Inverse LETFs absent from cache → synth fallback for sell_leverage < 0.*