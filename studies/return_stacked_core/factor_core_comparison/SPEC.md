# Factor Core Comparison Spec

Status: research-only diagnostic. No deployment, paper-trade label, capital
allocation change, or mandate override is authorized by this study.

## Question

Compare the current Return-Stacked Core (RSC) portfolios against simple
factor-tilted ETF portfolios centered on Avantis/Dimensional-style equity
exposure. The immediate user-provided lead is a short live-history Testfol.io
comparison where `60% AVUS / 20% AVUV / 20% SPMO` beat the RSC tracking
implementation over the common live window.

This study is distinct from `us_core/factor_sleeve_diagnostics/`, which asked
whether small AVUV/SPMO sleeves should be inserted inside the RSC-US portfolio.
Here the question is whether a standalone passive factor core is a better or
more practical alternative to RSC-US/RSC-Global.

## Pre-Registered Cases

### Case 1: US short live Testfol.io

Source: user-provided Testfol.io payload, sanitized before saving. The pasted
Bearer token must never be persisted. The runner first attempts the request
without authentication and falls back only to local `TESTFOLIO_TOKEN` or the
gitignored `.testfolio_token` if the no-auth request fails.

Portfolio set:

| Label | Allocation | Role |
|---|---|---|
| `AVUS` | `100% AVUS` | Avantis US core standalone. |
| `AVUV` | `100% AVUV` | US small-cap value standalone. |
| `SPMO` | `100% SPMO` | US large-cap momentum standalone. |
| `AVUS_AVUV_SPMO_60_20_20` | `60% AVUS / 20% AVUV / 20% SPMO` | User-proposed US factor core. |
| `RSC_US_TRACKING` | `35% GDE / 40% RSST tracking / 25% ZROZ` | RSC-US tracking expression. |

The RSC tracking expression expands the `40% RSST` sleeve as:

```text
40% SPY + 28% DBMF + 12% KMLM - 40% CASHX?E=-2
```

This matches the current RSC RSST tracking convention (`SPY + 70% DBMF + 30%
KMLM - CASHX?E=-2`) documented in the RSC folder. Financing sign matters;
older `CASHX?E=2` results are stale and invalid `[systematic_trading,
p.185-188]`.

Rebalance frequency follows the user payload: yearly. Monthly is supported as a
follow-up sensitivity, but the initial verdict must label yearly vs monthly
explicitly.

## Factor Rationale

The factor core is a portfolio-construction hypothesis, not an optimized signal.

| Design choice | Rationale |
|---|---|
| Use AVUS as broad US core | Avantis-style broad equity exposure with mild profitability/value tilts; treated as the investable core sleeve rather than a timing signal. |
| Add AVUV/SCV | Size, value, profitability and investment are recognized Fama-French style factors `[ml_for_algo_trading, ch.7 p.190-191]`. |
| Add SPMO/momentum | Momentum is empirically documented, but remains equity-beta-heavy and can break down in bear regimes `[stocks_on_the_move, p.58-60]`, `[stocks_on_the_move, p.63-65]`. |
| Use fixed 60/20/20 | A simple core/satellite tilt, not a fitted optimum. Avoid local weight optimization because best-of-grid selection is overfit-prone `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. |

## Metrics

For each case, report:

- common-window CAGR, MDD, volatility, Sharpe, Sortino, Calmar, Ulcer and
  terminal wealth;
- terminal relative wealth of factor core versus RSC;
- rolling 1y/3y/5y metrics when the window is long enough;
- stress windows with non-empty overlap;
- correlation matrix over common daily returns.

Metrics are diagnostic. Short live windows do not validate a long-horizon
portfolio. A result under five years is especially a regime sample, not a
mandate-grade conclusion `[advances_fin_ml, p.208-211]`.

## Data Caveats

- Testfol.io live ETF common window is constrained by the youngest instrument in
  the portfolio, likely GDE/RSST-related live history.
- Testfol.io payloads are external-engine artifacts; saved JSON responses are
  preserved only if they contain no credentials.
- The repository's global Testfol.io cache is currently minimal; long-history
  factor proxy work must be a separate case with explicit proxy caveats.
- yfinance can be used only for non-promotion diagnostics and must be marked as
  biased/current-universe data `[advances_fin_ml, p.208-211]`.
