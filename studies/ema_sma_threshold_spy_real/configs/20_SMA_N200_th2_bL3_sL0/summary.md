# Config SMA_N200_th2_bL3_sL0 — rank 20/384  (REAL SPY (S&P 500))

> Real-ETF validation of the SPYSIM synth study. Buy leg uses **real Tiingo returns**; sell leg is cash or synth inverse (inverse LETFs absent from cache). Educational — not production.

## Parameters

| param | value | source |
|---|---|---|
| MA filter | SMA | `[leverage_for_the_long_run, p.8]` |
| lookback | 200 bars | `[leverage_for_the_long_run, p.14, Table 6]` |
| threshold | ±2% | `[leverage_for_the_long_run, p.11]` |
| buy leg | ×3 = **UPRO** (real Tiingo) | Tiingo storage |
| sell leg | ×0 = cash (0.0% annual) | synth via `[p.16, fn.22]` if <0 |
| annual fee (synth sell only) | 0.95% | `[p.16, fn.23]` |
| switch cost | 15 bps/transition | mirror `letf_rotation.py` |

## Metrics — pure vs tax=15% vs SPY buy-hold

| metric | pure | tax=15% | SPY B&H | tax drag |
|---|---|---|---|---|
| CAGR | +18.19% | +15.25% | +15.00% | +2.94% |
| Sharpe | 0.65 | 0.58 | 0.90 | 0.07 |
| Max Drawdown | +57.43% | +59.93% | +33.70% | — |
| Calmar | 0.32 | 0.25 | 0.45 | — |
| Sortino | 0.88 | 0.77 | 1.27 | — |
| Volatility | +35.35% | +36.00% | +17.15% | — |
| n_switches | 26 | 26 | 0 | — |

*Tax drag = +2.94% CAGR = 16.2% of the pure edge.*

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

- **Total trades**: 27 (14 long, 13 short/cash)
- **Long-leg profitable**: 8/14 (57.1%)
- **Short-leg profitable**: 0/13 (0.0%)
- **Avg hold — long**: 240 bars (1.0 years)
- **Avg hold — short/cash**: 52 bars (0.2 years)
- **Cumulative tax paid (tax=15%)**: 2.1979 (absolute equity units)


See `trades.csv` for the complete regime-block ledger.

## Plot

![equity curve](equity.png)

---

*Real-data source: Tiingo daily prices for UPRO (buy) + SPY (signal). Inverse LETFs absent from cache → synth fallback for sell_leverage < 0.*