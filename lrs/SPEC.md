# SPEC - LRS Restart

## Mission

Restart the LRS research line from the original Gayed premise and evolve it into
a practical weekly strategy candidate. The target is a long-horizon strategy that
can beat buy-and-hold of the underlying index after Brazilian tax, while keeping
drawdown and risk-adjusted metrics materially better than raw leveraged
buy-and-hold.

The starting rule is intentionally simple: if the underlying closes above its
SMA200, hold leveraged exposure; otherwise hold a defensive sleeve
`[leverage_for_the_long_run, p.13]`. Gayed frames the moving average mainly as a
volatility/downside-regime proxy, not as a bull-market return booster
`[leverage_for_the_long_run, p.7-8]`.

This is research-only and does not override maintenance mode.

## Operating Constraints

- Execution cadence is weekly, using the first trading day of each week.
- Signals are lagged by one daily bar: the portfolio can only act on information
  available at the previous close `[testing_tuning, p.327-335]`.
- Settlement/operational lag `n` is tested from `0` through `5` daily bars.
- During `n > 0`, the portfolio sits in `CASHX` after liquidating the old sleeve
  before entering the new sleeve.
- Strategy grammar should remain common across SPY, QQQ and XLK; parameters may
  differ per asset if evidence supports that split.
- Annual Brazilian tax is modeled with Lei 14.754/2023: 15% on realized net gains,
  same-year netting, indefinite loss carry-forward and final liquidation.

## Phase 0 - Original Gayed Baseline

Purpose: create a clean benchmark for the restart.

Rules:

- `signal = underlying.shift(1) > SMA200.shift(1)`.
- Weekly state update only.
- Risk-on: available branch-native LETF proxy.
- Risk-off: `CASHX`.
- `n = 0..5` settlement lag.

Initial available branches from `data/testfolio/cache/history.parquet`:

| Branch | Underlying | Risk-on | Leveraged B&H benchmark |
|---|---|---|---|
| SPY 2x | `SPYSIM` | `SSOSIM` | `SSOSIM` |
| SPY 3x | `SPYSIM` | `UPROSIM` | `UPROSIM` |
| QQQ 2x | `QQQSIM` | `QLDSIM` | `QLDSIM` |
| QQQ 3x | `QQQSIM` | `TQQQSIM` | `TQQQSIM` |

XLK is deferred until `XLKSIM?L=2/3` or equivalent TECL synthetic series is
present in the cache.

## Phase 1 - Risk-Off Alternatives

Test defensive sleeves before expanding indicators, because prior evidence in
this repository suggests risk-off selection dominates small MA variations.

Candidate sleeves:

- `CASHX`;
- underlying index;
- `GLDSIM`;
- `IEFSIM`;
- `ZROZSIM`;
- `TLTSIM` and `TMFSIM` if pulled from Testfol.io;
- fixed baskets such as `60 ZROZ / 40 GLD`;
- trailing-momentum off-leg among `ZROZ / IEF / GLD / TLT`.

## Phase 2 - Target Leverage And Volatility Throttle

Before adding more indicators, vary exposure geometry directly:

- target leverage from `1.25x` through `3.00x` using adjacent ETF sleeves and no
  negative cash;
- selected Phase 1 risk-off sleeves only;
- simple realized-volatility gates such as `RV21 <= 30%` and `RV63 <= 40%`.

This follows the same LRS premise while directly addressing Gayed's observation
that high volatility is the enemy of leveraged compounding
`[leverage_for_the_long_run, p.4-7]`. Leverage reduction under higher risk is
also consistent with conservative position-sizing practice `[systematic_trading,
p.137-148]`.

## Phase 3 - Sparse Risk-On Filters

Risk-on filters must be sparse and structurally distinct. Candidate blocks:

- trend: SMA/EMA length and exit hysteresis;
- volatility: realized volatility, ATR percentage, VIX filter;
- streak/momentum quality: ROC, regression slope times R-squared, AR(1);
- trend strength: ADX as a confirmation filter.

Large unconstrained grids of RSI/MACD/ADX/CCI/Williams/ROC combinations are an
overfit risk and should be avoided unless they are converted into a small
pre-registered vote family `[trading_systems_methods, p.939]`,
`[advances_fin_ml, p.208-211]`.

## Phase 4 - Bear-Market Sleeve

Bear-market logic is a separate module, not the mirror image of the bull rule.

Candidate bear regime features:

- price below a long moving average;
- long moving average falling;
- realized volatility or VIX elevated;
- negative momentum/streak features.

Candidate actions:

- stay defensive;
- hold inverse ETF exposure such as `SH/SDS/SPXU`, `PSQ/QID/SQQQ`, or synthetic
  `?L=-1/-2/-3` series when available;
- cap inverse sizing because bear-market rallies create short-convexity risk.

## Phase 5 - RSC Overlay Rebuilt-Sleeve Diagnostic

Purpose: after standalone LRS fails validation gates, test whether a small LRS or
T3d-style sleeve adds value as a satellite around RSC-US `35/40/25` instead of as
a replacement.

Rules:

- Use the local RSC-US sleeve-return matrix for `GDESIM`, `RSSTSIM`, and
  `ZROZSIM`; current `RSSTSIM` is the user-requested Testfol.io tracking proxy
  `SPYSIM + 0.70*DBMFSIM + 0.30*KMLMSIM - (CASHX + 0.0200/252)`, equivalent to
  `100% SPY + 70% DBMF + 30% KMLM - 100% CASHX?E=-2`, not a live ETF backfill
  `[risk_parity, p.80-81]`, `[systematic_trading, p.185-188]`.
- Test only small pre-specified satellite weights (`10%`, `20%`, `30%`) to avoid
  re-opening a broad search.
- Report time underwater, max recovery time, turnover and relative drawdown versus
  RSC, because headline CAGR/MDD is not enough for sequence-risk assessment
  `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`.
- Treat monthly rebalancing as an allocation-control proxy, not account-level tax
  implementation; exact promotion would require account-level tax/friction
  recomputation and mandate gates `[systematic_trading, p.185-188]`.

## Score

The primary score is after-tax and benchmark-relative. Reports must include:

- CAGR after tax;
- max drawdown;
- Calmar and Sortino;
- terminal wealth vs underlying buy-and-hold;
- terminal wealth vs leveraged buy-and-hold;
- rolling 3/5/10/15/20-year hit rates vs underlying;
- relative equity drawdown;
- turnover per year;
- total tax paid;
- sensitivity to `n = 0..5`.

## Drawdown Objective

The Phase 0 baseline is allowed to have ruin-level drawdown because it is a
reference point, not a candidate. The evolved strategy should aim for drawdowns
that are psychologically survivable, not merely better than raw leveraged
buy-and-hold. Gayed's 3x buy-and-hold example shows that near-total drawdowns are
functionally ruin even if the equity curve eventually recovers
`[leverage_for_the_long_run, p.19-20]`.

Working drawdown tiers for this restart:

| Tier | Max drawdown | Interpretation |
|---|---:|---|
| Preferred | `<= 40%` | Psychologically plausible for an aggressive LETF strategy. |
| Tolerable research target | `40%..50%` | Still harsh, but potentially acceptable if CAGR/Calmar dominate. |
| Warning | `50%..65%` | Research-only; needs strong mitigation or sizing changes. |
| Ruin territory | `> 65%` | Not a practical candidate; useful only as diagnostic baseline. |

These tiers guide evolution and reporting. They are not a replacement for the
repository mandate gates if any future promotion claim is made.

Validation diagnostics are recorded, not used to stop evolution. A future
promotion claim still requires the mandate gates: PBO, DSR, walk-forward, OOS,
forward stress, bootstrap and cross-library agreement `[advances_fin_ml,
p.208-211]`, `[advances_fin_ml, p.222-223]`.
