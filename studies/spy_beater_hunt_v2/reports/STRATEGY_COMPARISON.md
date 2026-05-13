# spy_beater_hunt_v2 — 10-Iteration Strategy Comparison

## Plots

![Equity curves](plots/01_equity_curves.png)

![Relative equity](plots/02_relative_equity_vs_spy.png)

![Rolling CAGR](plots/03_rolling_cagr_windows.png)

![Rolling max drawdown](plots/04_rolling_mdd_windows.png)

## Executive Summary

No strategy passed all hard gates. The best research lead is iteration 006, `clenow_relmom_90d_3x_cash`: it beat SPY by a wide margin and passed PBO, DSR, WF, OOS, FWD and cross-lib, but failed the 99.9% bootstrap lower-bound gate by a small amount. Under the project mandate, that remains a hard fail, not a winner `[advances_fin_ml, p.196-202]`.

Iteration 001 was infrastructure-only, so the plots compare SPY plus the best strategy config from iterations 002-010. Iteration 001 is documented in the strategy-by-strategy section below.

## Ranking Table

| iter | best config | CAGR | MDD | Sharpe | terminal/SPY | PBO | DSR p | WF | failed gates |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 001 | `None` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | none |
| 002 | `static_60_20_10_10` | 11.01% | -26.16% | 0.977 | 0.87x | 0.607 | 0.00000 | 3/8 | bootstrap, economic, fwd, oos, pbo, walk_forward |
| 003 | `gayed_lrs_sma200_upro_cash` | 16.40% | -71.20% | 0.605 | 5.67x | 0.000 | 0.00608 | 7/8 | bootstrap |
| 004 | `vt_lrs_upro_target25` | 12.41% | -36.44% | 0.638 | 1.39x | 0.000 | 0.00540 | 5/8 | bootstrap, fwd, walk_forward |
| 005 | `ewmac_32_128_upro_cash` | 8.98% | -39.48% | 0.500 | 0.40x | 0.000 | 0.05867 | 3/8 | bootstrap, dsr, economic, fwd, oos, walk_forward |
| 006 | `clenow_relmom_90d_3x_cash` | 22.12% | -88.88% | 0.660 | 39.14x | 0.000 | 0.00616 | 7/8 | bootstrap |
| 007 | `relmom90_3x_vt25_cash` | 14.69% | -41.75% | 0.718 | 3.12x | 0.000 | 0.00280 | 6/8 | bootstrap, fwd |
| 008 | `kama10_2_30_sso_cash` | 2.96% | -85.76% | 0.243 | 0.04x | 0.000 | 0.60188 | 1/8 | bootstrap, dsr, economic, fwd, oos, walk_forward |
| 009 | `hirsch_nov_apr_upro_cash` | 15.50% | -81.90% | 0.569 | 4.22x | 0.000 | 0.04079 | 6/8 | bootstrap, fwd, oos |
| 010 | `clenow_xasset_top1_cash` | 11.07% | -30.29% | 0.768 | 0.92x | 0.167 | 0.00281 | 4/8 | bootstrap, economic, fwd, oos, walk_forward |

## Strategy-by-Strategy Review

### 001 — Bootstrap/audit

Infrastructure-only audit: confirmed SPYSIM benchmark and validation modules. No strategy was tested.

- Best config: `None`
- Verdict: `infrastructure_only`; winner: `False`
- SPY same-window: CAGR 11.49%, MDD -55.14%, Sharpe 0.682
- Gates: pbo=NOT_COMPUTED, dsr=NOT_COMPUTED, walk_forward=NOT_COMPUTED, oos=NOT_COMPUTED, fwd=NOT_COMPUTED, bootstrap=NOT_COMPUTED, cross_lib=NOT_COMPUTED

### 002 — Static diversifier control

Constant-weight SPY/ZROZ/GLD/KMLM portfolio inspired by diversified futures/asset allocation controls `[systematic_trading, p.72-85]`. It improved drawdown but could not beat SPY CAGR and failed multiple gates.

- Best config: `static_60_20_10_10`
- Verdict: `fail`; winner: `False`
- Candidate: CAGR 11.01%, MDD -26.16%, Sharpe 0.977, terminal/SPY 0.87x
- SPY same-window: CAGR 11.36%, MDD -55.14%, Sharpe 0.691
- Gates: economic=FAIL, pbo=FAIL, dsr=PASS, walk_forward=FAIL, oos=FAIL, fwd=FAIL, bootstrap=FAIL, cross_lib=PASS
- Failed gates: bootstrap, economic, fwd, oos, pbo, walk_forward

### 003 — Canonical Gayed LRS

SPY above SMA200 gates exposure into UPRO, otherwise cash, with a one-day lag `[leverage_for_the_long_run, p.13]`. Strong CAGR and most gates passed, but bootstrap failed.

- Best config: `gayed_lrs_sma200_upro_cash`
- Verdict: `fail`; winner: `False`
- Candidate: CAGR 16.40%, MDD -71.20%, Sharpe 0.605, terminal/SPY 5.67x
- SPY same-window: CAGR 11.47%, MDD -55.14%, Sharpe 0.682
- Gates: economic=PASS, pbo=PASS, dsr=PASS, walk_forward=PASS, oos=PASS, fwd=PASS, bootstrap=FAIL, cross_lib=PASS
- Failed gates: bootstrap

### 004 — Vol-targeted LRS

Same Gayed SMA200 shell, but UPRO exposure is scaled by lagged realized volatility to a 25% target `[systematic_trading, p.137-148]`. It reduced drawdown but lost temporal robustness.

- Best config: `vt_lrs_upro_target25`
- Verdict: `fail`; winner: `False`
- Candidate: CAGR 12.41%, MDD -36.44%, Sharpe 0.638, terminal/SPY 1.39x
- SPY same-window: CAGR 11.47%, MDD -55.14%, Sharpe 0.682
- Gates: economic=PASS, pbo=PASS, dsr=PASS, walk_forward=FAIL, oos=PASS, fwd=FAIL, bootstrap=FAIL, cross_lib=PASS
- Failed gates: bootstrap, fwd, walk_forward

### 005 — Carver EWMAC trend

EWMAC forecast maps positive SPY trend strength into partial UPRO exposure `[systematic_trading, p.112-119]`. It failed economics and most gates.

- Best config: `ewmac_32_128_upro_cash`
- Verdict: `fail`; winner: `False`
- Candidate: CAGR 8.98%, MDD -39.48%, Sharpe 0.500, terminal/SPY 0.40x
- SPY same-window: CAGR 11.47%, MDD -55.14%, Sharpe 0.682
- Gates: economic=FAIL, pbo=PASS, dsr=FAIL, walk_forward=FAIL, oos=FAIL, fwd=FAIL, bootstrap=FAIL, cross_lib=PASS
- Failed gates: bootstrap, dsr, economic, fwd, oos, walk_forward

### 006 — Clenow SPY/QQQ relative momentum

Ranks SPY and QQQ by 90-day adjusted slope and holds the matching 3x LETF only when SPY is above SMA200 `[stocks_on_the_move, p.75-77]`. Best economic lead; failed only bootstrap 99.9%.

- Best config: `clenow_relmom_90d_3x_cash`
- Verdict: `fail`; winner: `False`
- Candidate: CAGR 22.12%, MDD -88.88%, Sharpe 0.660, terminal/SPY 39.14x
- SPY same-window: CAGR 11.47%, MDD -55.14%, Sharpe 0.682
- Gates: economic=PASS, pbo=PASS, dsr=PASS, walk_forward=PASS, oos=PASS, fwd=PASS, bootstrap=FAIL, cross_lib=PASS
- Failed gates: bootstrap

### 007 — Vol-scaled relative momentum

Iteration 006 mechanism with lagged realized-vol scaling to 25% target. It reduced drawdown but failed FWD and bootstrap.

- Best config: `relmom90_3x_vt25_cash`
- Verdict: `fail`; winner: `False`
- Candidate: CAGR 14.69%, MDD -41.75%, Sharpe 0.718, terminal/SPY 3.12x
- SPY same-window: CAGR 11.47%, MDD -55.14%, Sharpe 0.682
- Gates: economic=PASS, pbo=PASS, dsr=PASS, walk_forward=PASS, oos=PASS, fwd=FAIL, bootstrap=FAIL, cross_lib=PASS
- Failed gates: bootstrap, fwd

### 008 — Kaufman KAMA/ER trend

KAMA adaptive trend gate using Kaufman's efficiency ratio `[trading_systems_methods, p.780-781]`. It underperformed badly.

- Best config: `kama10_2_30_sso_cash`
- Verdict: `fail`; winner: `False`
- Candidate: CAGR 2.96%, MDD -85.76%, Sharpe 0.243, terminal/SPY 0.04x
- SPY same-window: CAGR 11.47%, MDD -55.14%, Sharpe 0.682
- Gates: economic=FAIL, pbo=PASS, dsr=FAIL, walk_forward=FAIL, oos=FAIL, fwd=FAIL, bootstrap=FAIL, cross_lib=PASS
- Failed gates: bootstrap, dsr, economic, fwd, oos, walk_forward

### 009 — Hirsch/Kaeppel seasonality

Holds UPRO during November-April and cash in May-October `[trading_systems_methods, p.480]`. Beat SPY economically but failed OOS/FWD/bootstrap.

- Best config: `hirsch_nov_apr_upro_cash`
- Verdict: `fail`; winner: `False`
- Candidate: CAGR 15.50%, MDD -81.90%, Sharpe 0.569, terminal/SPY 4.22x
- SPY same-window: CAGR 11.47%, MDD -55.14%, Sharpe 0.682
- Gates: economic=PASS, pbo=PASS, dsr=PASS, walk_forward=PASS, oos=FAIL, fwd=FAIL, bootstrap=FAIL, cross_lib=PASS
- Failed gates: bootstrap, fwd, oos

### 010 — Cross-asset Clenow momentum

Ranks SPY/ZROZ/GLD/KMLM by adjusted slope with SPY SMA200 regime filter `[stocks_on_the_move, p.83-89]`. Improved risk but did not beat SPY CAGR.

- Best config: `clenow_xasset_top1_cash`
- Verdict: `fail`; winner: `False`
- Candidate: CAGR 11.07%, MDD -30.29%, Sharpe 0.768, terminal/SPY 0.92x
- SPY same-window: CAGR 11.30%, MDD -55.14%, Sharpe 0.684
- Gates: economic=FAIL, pbo=PASS, dsr=PASS, walk_forward=FAIL, oos=FAIL, fwd=FAIL, bootstrap=FAIL, cross_lib=PASS
- Failed gates: bootstrap, economic, fwd, oos, walk_forward

## Interpretation

The main pattern is not lack of economic ideas. Several strategies beat SPY and pass DSR/PBO. The binding control is temporal robustness, especially bootstrap 99.9% and, for some variants, OOS/FWD. Iteration 006 deserves follow-up as a research lead, but only through a distinct robustness test or independent confirmation, not a local lookback/leverage grid that would inflate DSR and PBO risk `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

