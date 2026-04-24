# Config EMA_N200_th2_bL3_sL0 — rank 10/384

> Educational sweep — not a production strategy. Ranking by composite `0.4·rank(CAGR) + 0.4·rank(Sharpe) + 0.2·rank(1/|MDD|)` on the PURE (tax=0) sweep.

## Parameters

| param | value | citation |
|---|---|---|
| MA filter | EMA | `[leverage_for_the_long_run, p.8]` |
| lookback | 200 bars | `[leverage_for_the_long_run, p.14, Table 6]` |
| threshold | ±2% | `[leverage_for_the_long_run, p.11]` |
| buy leg | ×3 long synth LETF | `[leverage_for_the_long_run, p.17, Table 8]` |
| sell leg | ×0 (cash) | `[leverage_for_the_long_run, p.21]` |
| annual fee | 0.95% | `[leverage_for_the_long_run, p.16, fn.23]` |
| switch cost | 15 bps/transition | mirror `letf_rotation.py` |

## Metrics — pure (tax=0) vs tax=15% vs SPY buy-hold

| metric | pure | tax=15% | SPY buy-hold | tax drag |
|---|---|---|---|---|
| CAGR | +21.31% | +18.03% | +11.47% | +3.28% |
| Sharpe | 0.71 | 0.63 | 0.68 | 0.08 |
| Max Drawdown | +63.29% | +66.70% | +55.14% | — |
| Calmar | 0.34 | 0.27 | 0.21 | — |
| Sortino | 0.99 | 0.87 | 0.96 | — |
| Volatility | +36.85% | +37.51% | +18.46% | — |
| n_switches | 78 | 78 | 0 | — |

*Tax drag = +3.28% CAGR = 15.4% of the pure edge.*

## Gates (informational, not blocking; evaluated on PURE sweep)

| gate | verdict | citation |
|---|---|---|
| G1 PBO < 0.5 | PASS | `[advances_fin_ml, p.208-211]` |
| G2 DSR p < 0.05 | FAIL | `[advances_fin_ml, p.222-223]` |
| G3 Walk-Forward 6/8 + MDD<25% | FAIL | `[advances_fin_ml, ch.12]` |
| G4 OOS 70/30 Sharpe > 0 | PASS | `mandate §5` |
| G5 FWD stress post-2020 Sharpe > 0 | PASS | `mandate §5` |
| G6 Bootstrap 99.9% CI low > 0 | PASS | `[advances_fin_ml, p.196-202]` |
| G7 Cross-lib ±3pp CAGR | PASS | `[advances_fin_ml, p.31-34]` |


**Gates passed: 5/7**

> Partial gate-passer: key statistical checks pass but one or more critical filters reject.

## Trade summary (regime blocks)

- **Total trades**: 79 (40 long, 39 short/cash)
- **Long-leg profitable**: 20/40 (50.0%)
- **Short-leg profitable**: 0/39 (0.0%)
- **Avg hold — long**: 199 bars (0.8 years)
- **Avg hold — short/cash**: 51 bars (0.2 years)
- **Cumulative tax paid (tax=15%)**: 208.3621 (absolute equity units)


See `trades.csv` for the complete regime-block ledger with pure vs tax15 equity paths.

## Plot

![equity curve](equity.png)

---

*Citations: signal `[leverage_for_the_long_run, p.13]`; synth formula `[p.16, fn.22]`; band `[p.11]`; honest alignment `[advances_fin_ml, p.31-34]`; gates — see table above.*
