# Stage 2 Overnight Grid Consolidation

Status: discovery consolidation and backtest-mechanics audit. This is not a
validation verdict and does not authorize capital allocation.

## Runs Reviewed

| Run | Configs | Window | Output |
|---|---:|---|---|
| QQQ risk-ons + ZROZ, `n=1..5` | 16,868,018 | QLD 2009-11-05..2026-04-14; TQQQ 2010-02-12..2026-04-14 | `results/stage2_tiingo_ohlc/QQQ_QLD_TQQQ_ZROZ_n1_5/REPORT.md` |
| QQQ risk-ons + BIL, `n=1..5` | 16,868,018 | QLD 2007-05-31..2026-04-14; TQQQ 2010-02-12..2026-04-14 | `results/stage2_tiingo_ohlc/QQQ_QLD_TQQQ_BIL_n1_5/REPORT.md` |
| SPY risk-ons + ZROZ, `n=1..5` | 16,868,018 | SSO/UPRO 2009-11-05..2026-04-14 | `results/stage2_tiingo_ohlc/SPY_SSO_UPRO_ZROZ_n1_5/REPORT.md` |
| QQQ→TQQQ + ZROZ, `n=6` only | 64,425,438 | TQQQ 2010-02-12..2026-04-14 | `results/stage2_tiingo_ohlc/QQQ_TQQQ_ZROZ_n6_only/REPORT.md` |

Persisted grid trials reviewed: **115,029,492**. Minimum cumulative trial count
including prior Stage 1/Stage 2 work is **at least 122,583,546**, before adding
aborted/interrupted partial runs. DSR must use the cumulative count
`[advances_fin_ml, p.222-223]`.

## Headline Winners

| Family | Best risk-on | n/k | Sortino | CAGR | MDD | Calmar | Signals |
|---|---|---:|---:|---:|---:|---:|---|
| QQQ + ZROZ `n<=5` | TQQQ_3x | 5/2 | 1.6280 | 62.19% | -62.37% | 0.9971 | `px_gt_sma150|macd_hist_gt_0|rsi14_rising|ar1_30_gt_0|close_gt_prior_high55` |
| QQQ + ZROZ `n<=5`, best QLD | QLD_2x | 5/3 | 1.6162 | 40.94% | -52.47% | 0.7801 | `px_gt_sma150|macd_gt_signal|rsi14_rising|ar1_30_gt_0|adx14_gt_20` |
| QQQ + BIL `n<=5` | TQQQ_3x | 5/3 | 1.4697 | 56.16% | -44.70% | 1.2565 | `px_gt_sma20|sma50_gt_sma200|roc20_gt_0|ar1_30_gt_0|atr14_pct_lt_5` |
| SPY + ZROZ `n<=5` | UPRO_3x | 5/3 | 1.5331 | 50.07% | -47.30% | 1.0586 | `px_gt_sma50|roc20_gt_0|adx14_gt_20|adx14_gt_25|atr14_pct_lt_3` |
| SPY + ZROZ `n<=5`, best 2x | SSO_2x | 5/3 | 1.5325 | 34.85% | -34.21% | 1.0186 | `px_gt_sma50|roc20_gt_0|adx14_gt_20|adx14_gt_25|atr14_pct_lt_3` |
| QQQ→TQQQ + ZROZ `n=6` | TQQQ_3x | 6/2 | 1.6244 | 61.93% | -62.37% | 0.9929 | `px_gt_sma150|macd_gt_signal|rsi14_rising|ar1_30_gt_0|close_gt_prior_high20|close_gt_prior_high55` |

## Backtest Mechanics Audit

### What Was Checked

1. **Signal/return lag:** grid signal is computed on bar `t`, shifted by one bar,
   and earns return on bar `t+1`. This avoids same-close lookahead
   `[advances_fin_ml, p.31-34]`.
2. **Tiingo OHLC adjustment:** `open/high/low` are multiplied by
   `adj_close / close` before high/low indicators are computed. This keeps OHLC
   indicator levels consistent with adjusted-close returns `[quant_trading_chan,
   p.37]`.
3. **Return source:** risk-on/off/benchmark returns use Tiingo `adj_close` daily
   pct-change.
4. **Independent recomputation:** top candidates were recomputed with a separate
   pandas path. CAGR, MDD and Sharpe matched the grid output to rounding.

### Independent Recompute Results

| Candidate | Grid CAGR | Recomputed CAGR | Grid MDD | Recomputed MDD | Extra-lag CAGR | Extra-lag MDD |
|---|---:|---:|---:|---:|---:|---:|
| QQQ→TQQQ + ZROZ `n=5/k=2` | 62.19% | 62.19% | -62.37% | -62.37% | 15.61% | -71.59% |
| QQQ→TQQQ + BIL `n=5/k=3` | 56.16% | 56.16% | -44.70% | -44.70% | 38.31% | -57.90% |
| SPY→UPRO + ZROZ `n=5/k=3` | 50.07% | 50.07% | -47.30% | -47.30% | 39.12% | -68.34% |
| QQQ→TQQQ + ZROZ `n=6/k=2` | 61.93% | 61.93% | -62.37% | -62.37% | 15.10% | -71.59% |

## Settlement / Execution-Lag Stress

The base grid assumes a close-to-close regime: signal is known after close `t`,
then the strategy earns the next close-to-close return. This is acceptable for
research discovery, but a cash-account investor may face operational delay if
sale proceeds are not immediately reusable. US ETF settlement moved to T+1 in
2024, but broker-specific buying-power rules can still matter. Therefore, any
candidate that only works with zero extra delay is operationally fragile.

Stress file: `tables/execution_lag_stress.csv`.

| Candidate | Lag 0 CAGR | Lag 1 CAGR | Lag 2 CAGR | Lag 0 MDD | Lag 1 MDD | Lag 2 MDD | Operational Read |
|---|---:|---:|---:|---:|---:|---:|---|
| QQQ→TQQQ + ZROZ `n=5/k=2` | 62.19% | 15.61% | 13.30% | -62.37% | -71.59% | -78.44% | Fails settlement/execution stress |
| QQQ→QLD + ZROZ `n=5/k=3` | 40.94% | 9.31% | 8.57% | -52.47% | -61.07% | -65.98% | Fails settlement/execution stress |
| QQQ→TQQQ + BIL `n=5/k=3` | 56.16% | 38.31% | 37.79% | -44.70% | -57.90% | -63.44% | Still strong but drawdown worsens |
| SPY→UPRO + ZROZ `n=5/k=3` | 50.07% | 39.12% | 30.36% | -47.30% | -68.34% | -65.68% | Still strong, risk worsens |
| SPY→SSO + ZROZ `n=5/k=3` | 34.85% | 28.21% | 22.38% | -34.21% | -54.60% | -51.14% | Most robust 2x candidate |
| QQQ→TQQQ + ZROZ `n=6/k=2` | 61.93% | 15.10% | 13.15% | -62.37% | -71.59% | -78.44% | Fails settlement/execution stress |

Settlement interpretation: if the actual account cannot rotate from risk-on to
risk-off at the intended close-to-close boundary, the QQQ+ZROZ winners should be
discarded as operationally non-robust. QQQ+BIL and SPY+ZROZ are more robust to
one extra day, though both still suffer larger drawdowns. This execution stress
should be treated as a hard pre-validation screen, not a cosmetic sensitivity
table `[advances_fin_ml, p.31-34]`.

## BIL Versus Cash Proxy

Because `BIL` is primarily a cash/T-Bill proxy, the operational variant that may
matter most for a cash account is `OFF = USD cash`, not buying/selling `BIL`.
Cash avoids an extra ETF sale before re-entering risk-on and reduces tax/accounting
events from the off-leg. It also gives up the T-Bill return embedded in `BIL`.

Stress file: `tables/cash_proxy_stress.csv`.

For the top `QQQ→TQQQ+BIL` candidate
`px_gt_sma20|sma50_gt_sma200|roc20_gt_0|ar1_30_gt_0|atr14_pct_lt_5`, the cash
proxy is almost identical:

| Off mode | Extra lag | CAGR | Sortino | MDD | Calmar | ON share |
|---|---:|---:|---:|---:|---:|---:|
| BIL | 0 | 56.16% | 1.4697 | -44.70% | 1.2565 | 80.62% |
| CASH_USD | 0 | 55.76% | 1.4538 | -44.73% | 1.2468 | 80.62% |
| BIL | 1 | 38.31% | 1.1210 | -57.90% | 0.6615 | 80.60% |
| CASH_USD | 1 | 37.96% | 1.1071 | -57.92% | 0.6554 | 80.60% |
| BIL | 2 | 37.79% | 1.1018 | -63.44% | 0.5958 | 80.57% |
| CASH_USD | 2 | 37.45% | 1.0875 | -63.78% | 0.5871 | 80.57% |

Re-ranking only the BIL grid top-50 under `CASH_USD + extra_lag=1` found a
stronger operational candidate:

| Source rank | Risk-on | n/k | CAGR | Sortino | MDD | Signals |
|---:|---|---:|---:|---:|---:|---|
| 50 | TQQQ_3x | 5/1 | 51.01% | 1.3711 | -51.90% | `px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high20` |
| 24 | TQQQ_3x | 4/2 | 47.68% | 1.2919 | -49.08% | `sma100_gt_sma250|roc20_gt_0|rv21_pct_lt_70|ar1_30_gt_0` |
| 30 | TQQQ_3x | 5/2 | 47.14% | 1.2890 | -51.57% | `sma100_gt_sma250|roc20_gt_0|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100` |

This means `BIL` was not the source of the edge. The edge is mostly the risk-on
timing rule. Operationally, `CASH_USD + extra_lag=1` deserves its own exact grid
before validation.

### Audit Verdict

The reported CAGR numbers are mechanically reproducible. No immediate arithmetic
or same-close lookahead bug was found in the Stage 2 runner. However, the numbers
are **not yet reliable strategy evidence** because:

- the search evaluated over 115M persisted configurations;
- several top rows are duplicate-equivalent (`macd_gt_signal` and
  `macd_hist_gt_0` are mathematically identical here);
- nested conditions appear in winners, e.g. `adx14_gt_20` plus `adx14_gt_25`;
- the QQQ/TQQQ+ZROZ winners are extremely sensitive to one extra close-to-close
  delay;
- settlement/buying-power constraints may make the no-extra-delay assumption
  unavailable in a cash-only retail account;
- the backtest is gross of taxes, spreads, slippage and any execution mismatch
  between close signal and actual fill;
- all top rows are in-sample discovery and still require OOS/WF/bootstrap/PBO/DSR
  validation `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

## Interpretation

The overnight grids changed the picture: Stage 2 no longer looks like a weak
local refinement. It found strong in-sample candidates across QQQ and SPY, with
both duration-off (`ZROZ`) and cash-like (`BIL`) off-legs producing high-CAGR
TQQQ leads. That breadth reduces the chance that this is only a single QQQ/ZROZ
artifact, but it does not solve multiple-testing risk.

The recurring signal families are economically interpretable:

- trend: `SMA150`, `SMA50`, `SMA50>SMA200`, `SMA50>SMA150`;
- short momentum/confirmation: `ROC20`, `MACD`, `RSI rising`;
- volatility/range control: `ATR14% < 3/5`, `RV21` filters;
- trend strength: `ADX14` gates;
- serial dependence: `AR1_30 > 0`.

The two strongest QQQ/TQQQ+ZROZ tops are essentially the same rule family; the
`n=6` run did not discover a materially better candidate than the `n<=5` grid.
It mostly added redundant breakout confirmation to the same `SMA150 + MACD + RSI
rising + AR1` core.

## Recommended Next Steps

1. Deduplicate the signal universe before more search: remove one of
   `macd_gt_signal` / `macd_hist_gt_0`, collapse nested thresholds, and avoid
   counting equivalent candidates twice.
2. Run a dedicated operational grid with `OFF=CASH_USD` and `extra_lag=1`, because
   re-ranking the BIL top-50 already changed the best candidate.
3. Create a Stage 2 validation runner for selected candidates using OOS, FWD,
   walk-forward, bootstrap, PBO and DSR.
4. Validate a small candidate panel: QQQ/TQQQ+CASH_USD, QQQ/TQQQ+BIL,
   SPY/UPRO+ZROZ, SPY/SSO+ZROZ, and QQQ/QLD+ZROZ.
5. Include execution stress: one extra day of lag, close-to-next-open proxy if
   available, and costs/slippage.
6. Treat any DSR result with `n_trials < 122,583,546` as invalidly optimistic.

## Current Verdict

Stage 2 produced economically interesting and mechanically reproducible in-sample
leads. The backtest implementation is acceptable for discovery, but the reported
CAGR numbers are not validated evidence. The next blocker is statistical and
execution robustness, not a currently identified CAGR calculation bug.
