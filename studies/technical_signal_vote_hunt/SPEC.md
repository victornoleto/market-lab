# Technical Signal Vote Hunt — Spec

## Purpose

Generalize the T3d-K2 result from `letf_rotation_hunt`: instead of a fixed
4-signal vote, evaluate many technical signals and all `k` thresholds for each
chosen subset size. The main research questions are:

1. Which indicators appear disproportionately often in the best results?
2. Which `n` and `k` values dominate by CAGR, Sharpe, Sortino, MaxDD and Calmar?
3. Are some indicators weak or poisonous when included in otherwise strong votes?

## Governance

This is research-only. PBO/DSR/walk-forward/bootstrap gates remain binding for
any final claim `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
CAGR and MDD are ranking/tier metrics, not hard gates, per mandate §2.2/§2.3.

## Stage 1: Testfolio Close-Only

Data source: `data/testfolio/cache/history.parquet` via the existing loader.

Branches:

| Branch | Signal series | 2x leg | 3x leg | Benchmark |
|---|---|---|---|---|
| SPY | `SPYSIM` | `SSOSIM` | `UPROSIM` | `SPYSIM` |
| QQQ | `QQQSIM` | `QLDSIM` | `TQQQSIM` | `QQQSIM` |

Risk-off legs:

| Off leg | Meaning |
|---|---|
| `ZROZSIM` | duration carry / crisis diversifier |
| `CASHX` | FFR cash proxy |

Initial signal universe:

| Family | Signals |
|---|---|
| Moving average | price > SMA/EMA `{5,10,20,50,100,150,200,250}` |
| MA cross | SMA short > SMA long for selected trend pairs |
| MACD | MACD > signal; histogram > 0 |
| Momentum | ROC `{10,20,60,120}` > 0 |
| RSI | RSI(14) > 50; RSI(14) rising |
| StochRSI | StochRSI(14) > 50 |
| Volatility | realized vol 21d < 40%; vol percentile gates |
| Serial dependence | AR(1) 30d > 0 |

Close-only indicators preserve the 1986+ QQQ window and the long-history
comparison against the existing LETF research. Moving-average and LRS choices
follow Gayed's trend-gated leverage framework `[leverage_for_the_long_run, p.13]`.
RSI/MACD/ROC definitions follow Kaufman `[trading_systems_methods, p.382-386]`.
Realized-vol gates follow the LETF decay rationale `[leverage_for_the_long_run, p.5-6]`.

## Branch-Native Benchmarks

Each branch compares only against native variants:

| Branch | Benchmark family |
|---|---|
| SPY | buy-hold SPY, LRS SPY->SSO/UPRO, T3d-K2-SPY, iter030-like-SPY |
| QQQ | buy-hold QQQ, LRS QQQ->QLD/TQQQ, T3d-K2-QQQ, iter030-like-QQQ |

This prevents the SPY branch from being judged against NDX-specific strategy
variants and keeps all comparisons apples-to-apples.

## Stage 2: Tiingo OHLC

Stage 2 will use Tiingo adjusted OHLC. Adjusted OHLC must be constructed before
computing high/low indicators:

```text
factor = adj_close / close
adj_open = open * factor
adj_high = high * factor
adj_low = low * factor
```

Candidate additions: ADX, ATR, Stochastic, Williams %R, CCI, Ultimate
Oscillator, High/Low breakout and Bull/Bear Power. Pivot points are excluded
because the study target is daily/long-horizon regime allocation, not short-term
support/resistance trading.
