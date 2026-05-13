---
mission: "Find a long-term strategy that beats SPY buy-and-hold and passes hard overfit gates"
status: open
active_phase: 1
active_phase_name: "bootstrap and first honest hypotheses"
total_iterations: 10
target_total_iterations: 20
cumulative_n_trials: 20
latest_iteration: "010-2026-05-13-cross-asset-clenow-momentum"
latest_status: "fail"
latest_winner: false
latest_best_config: "clenow_xasset_top1_cash"
latest_best_cagr: 0.11065952324428685
latest_best_mdd: 0.3028792176379802
latest_best_sharpe: 0.7683131425160147
latest_pbo: 0.16666666666666666
latest_dsr_p_value: 0.002806068621460822
winner_iter: []
dead_end_families: ["pre-fixed static SPY/ZROZ/GLD/KMLM diversifier control", "canonical Gayed SPY LRS 2x/3x cash control failed bootstrap 99.9%", "volatility-targeted Gayed SPY LRS UPRO cash overlay failed WF/FWD/bootstrap", "single-index Carver EWMAC SPY trend forecast to UPRO/CASH failed economic/DSR/WF/OOS/FWD/bootstrap", "Clenow-style SPY/QQQ relative momentum passed most gates but failed bootstrap 99.9%", "volatility-scaled Clenow-style SPY/QQQ relative momentum failed FWD/bootstrap", "Kaufman KAMA/ER adaptive SPY trend gate failed economic/DSR/WF/OOS/FWD/bootstrap", "Hirsch/Kaeppel November-April leveraged SPY seasonal window passed economic/DSR/WF but failed OOS/FWD/bootstrap", "cross-asset Clenow adjusted-slope momentum/risk-parity over SPY/ZROZ/GLD/KMLM failed economic/WF/OOS/FWD/bootstrap"]
---

# MEMORY — spy_beater_hunt_v2

Read this file first in every fresh autonomous session. It is the short state
for the loop, not a replacement for `SPEC.md`.

## Current State

The study has completed iteration 010. The latest hypothesis, pre-fixed
Clenow-style cross-asset adjusted-slope momentum over SPY/ZROZ/GLD/KMLM with a
SPY SMA200 regime filter, improved drawdown and Sharpe but did not beat SPY CAGR
or terminal wealth and failed WF, OOS, final-3y forward-stress and bootstrap
99.9% hard gates.

Capital allocation is unchanged: 100% Plano C per `docs/investment-mandate.md`.
Any strategy found here is research evidence only and cannot trigger deploy by
itself `[advances_fin_ml, p.222-223]`.

## Permanent Rules

- Beat SPY buy-and-hold on long-term CAGR before considering promotion.
- Passing CAGR is not enough: PBO, DSR, WF, OOS, FWD, bootstrap and cross-library
  gates remain hard-blocks `[advances_fin_ml, p.196-202]`,
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- Every strategy, indicator, parameter and gate choice needs a book citation.
- One hypothesis family per iteration.
- Pre-register before running any test.
- Keep config count small; DSR uses cumulative trials.
- Do not accept a winner that only works in a short modern window.
- Do not repeat failed local optimizations from `technical_signal_vote_hunt`
  unless the new hypothesis has a distinct mechanism.
- Do not modify `docs/investment-mandate.md`.
- Do not commit or push automatically.

## Inherited Lessons

- `studies/spy_beater_hunt/` found useful static/stacked portfolios, but the
  original hunt is closed and its B4-style conclusions are historical context.
- `studies/technical_signal_vote_hunt/` found strong economic leads in technical
  vote families, but repeated validations failed DSR/PBO. More local grids/GA in
  the same signal cluster are disfavored unless diversity is explicit.
- `studies/letf_rotation_hunt/` post-close loop shows the preferred loop pattern:
  fresh agent sessions, short memory, pre-registration, per-iter artifacts, and
  global trial accounting.

## Hypotheses Tested

- **001-2026-05-13-bootstrap-audit:** infrastructure-only audit. Confirmed
  `SPYSIM` benchmark availability from `data/testfolio/cache/history.parquet`
  over 1986-01-02..2026-04-17, with CAGR 11.49%, MDD -55.14%, Sharpe 0.682,
  Sortino 0.957 and terminal equity 79.86x. Confirmed importable validation
  modules for PBO, DSR, WF, bootstrap, CPCV and permutation. `n_trials=0`, no
  strategy claim, no winner `[advances_fin_ml, p.196-202]`,
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- **002-2026-05-13-static-diversifier-control:** tested four pre-fixed
  Carver-style constant-weight diversifier stacks using `SPYSIM`, `ZROZSIM`,
  `GLDSIM`, and `KMLMSIM` over their common 1988-01-04..2026-04-17 window
  `[systematic_trading, p.72-85]`, `[systematic_trading, p.116]`. Best config
  `static_60_20_10_10` had CAGR 11.01%, MDD -26.16%, Sharpe 0.977, terminal
  55.50x vs SPY CAGR 11.36%, MDD -55.14%, Sharpe 0.691, terminal 63.56x. It
  failed economic, PBO (`0.607`), WF (3/8), OOS, FWD and bootstrap gates; DSR
  passed at cumulative `n_trials=4` (`p=3.12e-07`). Verdict: `fail`, no winner
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- **003-2026-05-13-gayed-lrs-control:** tested two pre-fixed canonical Gayed
  LRS controls: `SPYSIM > SMA200` then `SSOSIM` or `UPROSIM`, else `CASHX`, with
  one-day signal lag over 1986-01-03..2026-04-17
  `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.16-17]`,
  `[leverage_for_the_long_run, p.21]`. Best config
  `gayed_lrs_sma200_upro_cash` beat SPY CAGR (16.40% vs 11.47%) and terminal
  wealth (5.67x SPY), passed DSR (`p=0.00608`, cumulative `n_trials=6`), PBO
  (`0.000`, unstable with only 2 configs), WF (7/8), OOS, FWD and cross-lib, but
  failed bootstrap 99.9% excess-return CI (`low=-2.70%`). Verdict: `fail`, no
  winner `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.
- **004-2026-05-13-vol-targeted-lrs:** tested two pre-fixed Carver-style
  volatility-targeted overlays on Gayed LRS: `SPYSIM > SMA200` then `UPROSIM`
  scaled to 20% or 25% annualized vol using lagged 63-day close-to-close realized
  volatility, else `CASHX` `[systematic_trading, p.40]`,
  `[systematic_trading, p.137-148]`, `[volatility_trading, p.14]`. Best config
  `vt_lrs_upro_target25` beat SPY CAGR (12.41% vs 11.47%) and terminal wealth
  (1.39x SPY), with lower MDD than full-UPRO LRS (-36.44%), and passed DSR
  (`p=0.00540`, cumulative `n_trials=8`), PBO (`0.000`, unstable with only 2
  configs), OOS and cross-lib. It failed WF (5/8), FWD final 3y (20.28% vs SPY
  21.45%) and bootstrap 99.9% excess-return CI (`low=-7.40%`). Verdict: `fail`,
  no winner `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.
- **005-2026-05-13-carver-ewmac-trend:** tested two pre-fixed non-LRS Carver
  EWMAC trend-following variants on `SPYSIM`, with positive forecast strength
  mapped to next-day `UPROSIM` weight and residual allocation to `CASHX`
  `[systematic_trading, p.112-119]`, `[systematic_trading, p.155-157]`,
  `[systematic_trading, p.282-285]`. Best config `ewmac_32_128_upro_cash`
  failed the economic gate, with CAGR 8.98% vs SPY 11.47% and terminal wealth
  0.40x SPY. It passed only unstable two-config PBO (`0.000`) and cross-lib;
  it failed DSR (`p=0.05867`, cumulative `n_trials=10`), WF (3/8), OOS, FWD
  and bootstrap 99.9% excess-return CI (`low=-10.50%`). Verdict: `fail`, no
  winner `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.
- **006-2026-05-13-clenow-relative-momentum:** tested two pre-fixed
  Clenow-style relative-momentum controls over `SPYSIM` and `QQQSIM`, ranking the
  indices by 90-day adjusted slope and holding the corresponding 2x or 3x LETF
  only when SPY was above its SMA200 `[stocks_on_the_move, p.75-77]`,
  `[stocks_on_the_move, p.66-67]`. Best config
  `clenow_relmom_90d_3x_cash` beat SPY economically with CAGR 22.12% vs 11.47%
  and terminal wealth 39.14x SPY, and passed PBO (`0.000`, unstable with two
  configs), DSR (`p=0.00616`, cumulative `n_trials=12`), WF (7/8), OOS, FWD and
  cross-lib. It failed bootstrap 99.9% excess-return CI (`low=-0.20%`
  annualized), so the verdict is `fail`, no winner `[advances_fin_ml, p.196-202]`,
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- **007-2026-05-13-vol-scaled-relative-momentum:** tested two pre-fixed
  volatility-scaled variants of the iteration-006 relative-momentum mechanism:
  90-day adjusted-slope rank between `SPYSIM` and `QQQSIM`, `SPYSIM > SMA200`
  broad regime filter, and selected 3x LETF exposure scaled to 20% or 25%
  annualized vol with lagged 63-day realized volatility `[stocks_on_the_move,
  p.75-77]`, `[stocks_on_the_move, p.66-67]`, `[systematic_trading, p.137-148]`.
  Best config `relmom90_3x_vt25_cash` beat SPY economically with CAGR 14.69% vs
  11.47%, terminal wealth 3.12x SPY and MDD 41.75% absolute drawdown. It passed
  PBO (`0.000`, unstable with two configs), DSR (`p=0.00280`, cumulative
  `n_trials=14`), WF (6/8), OOS and cross-lib, but failed FWD final 3y (20.36%
  vs SPY 21.45%) and bootstrap 99.9% excess-return CI (`low=-5.49%` annualized).
  Verdict: `fail`, no winner `[advances_fin_ml, p.196-202]`,
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- **008-2026-05-13-kaufman-kama-er-trend:** tested two pre-fixed Kaufman KAMA/ER
  adaptive SPY trend gates: `SPYSIM > KAMA(ER=10, fast=2, slow=30)` then hold
  `SSOSIM` or `UPROSIM`, otherwise `CASHX` `[trading_systems_methods, p.10-11]`,
  `[trading_systems_methods, p.780-781]`. Best config `kama10_2_30_sso_cash`
  materially underperformed SPY with CAGR 2.96% vs 11.47%, terminal wealth
  0.04x SPY, MDD 85.76% and Sharpe 0.243. It passed only unstable two-config
  PBO (`0.000`) and cross-lib; it failed economic, DSR (`p=0.6019`, cumulative
  `n_trials=16`), WF (1/8), OOS, FWD and bootstrap 99.9% excess-return CI
  (`low=-15.96%` annualized). Verdict: `fail`, no winner
  `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.
- **009-2026-05-13-seasonal-hirsch-window:** tested two pre-fixed
  Hirsch/Kaeppel seasonal windows: hold `SSOSIM` or `UPROSIM` during
  November-April and `CASHX` during May-October `[trading_systems_methods,
  p.480]`. Best config `hirsch_nov_apr_upro_cash` beat SPY economically with
  CAGR 15.50% vs 11.47%, terminal wealth 4.22x SPY, and rolling CAGR win rates
  of 63.80%/70.23%/84.00% over 3y/5y/10y windows. It passed PBO (`0.000`,
  unstable with two configs), DSR (`p=0.0408`, cumulative `n_trials=18`), WF
  (6/8) and cross-lib, but failed OOS final 25% (12.92% vs SPY 15.32%), FWD
  final 3y (15.61% vs SPY 21.45%) and bootstrap 99.9% excess-return CI
  (`low=-5.71%` annualized). Verdict: `fail`, no winner
  `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.
- **010-2026-05-13-cross-asset-clenow-momentum:** tested two pre-fixed
  Clenow-style cross-asset momentum configs over `SPYSIM`, `ZROZSIM`, `GLDSIM`,
  `KMLMSIM`, and `CASHX`: top-1 adjusted-slope winner-take-all and top-2
  inverse-vol. The mechanism used 90-day adjusted slope `[stocks_on_the_move,
  p.75-77]`, SPY>SMA200 regime gating `[stocks_on_the_move, p.66-67]`, and
  risk-not-cash allocation for inverse-vol `[stocks_on_the_move, p.83-89]`.
  Best config `clenow_xasset_top1_cash` did not beat SPY: CAGR 11.07% vs SPY
  11.30%, terminal 0.92x SPY, MDD 30.29%, Sharpe 0.768. It passed DSR
  (`p=0.00281`, cumulative `n_trials=20`), unstable two-config PBO (`0.167`) and
  cross-lib, but failed economic, WF (4/8), OOS, FWD and bootstrap 99.9% excess
  CI (`low=-11.30%` annualized). Verdict: `fail`, no winner
  `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.

## Pending Hypothesis Queue

1. Bootstrap/audit iteration: establish SPY benchmark, available data, reusable
   validation primitives, and a minimal benchmark report without optimizing.
   **Done in iteration 001.**
2. Literature-driven candidate families only after the audit confirms feasible
   data and validation path. Static diversifier control failed in iteration 002;
    canonical Gayed SPY LRS failed bootstrap in iteration 003; volatility-targeted
    Gayed SPY LRS failed WF/FWD/bootstrap in iteration 004; single-index Carver
    EWMAC failed economic and hard gates in iteration 005. Clenow-style SPY/QQQ
    relative momentum was economically strong in iteration 006 but failed the
    bootstrap 99.9% hard gate; volatility-scaled relative momentum in iteration
    007 reduced drawdown but failed FWD/bootstrap. Kaufman KAMA/ER adaptive SPY
    trend gating failed economically and across most hard gates in iteration 008.
    Hirsch/Kaeppel seasonal timing in iteration 009 beat SPY economically but
    failed OOS/FWD/bootstrap. Cross-asset Clenow adjusted-slope momentum in
    iteration 010 improved drawdown and risk-adjusted metrics but failed
    economic/WF/OOS/FWD/bootstrap gates.

## Last Result

Iteration 010 closed `fail`. Artifacts:
`studies/spy_beater_hunt_v2/iterations/010-2026-05-13-cross-asset-clenow-momentum/`.
Two strategy configs were tested and cumulative trials are now 20.

## Next Step

Run iteration 011 with one distinct, citable mechanism and a strict trial budget.
Avoid repeating static SPY/ZROZ/GLD/KMLM mixes, local technical-signal grids/GA,
plain Gayed SMA/leverage controls, local target-vol tuning of iteration 004,
single-index EWMAC speed tuning from iteration 005, or local lookback/leverage
tuning around iteration 006. Also avoid local volatility-target tuning around
iteration 007, because the pre-fixed vol-scaled variant weakened FWD/bootstrap.
Avoid local KAMA/ER parameter tuning after iteration 008. Avoid local
Hirsch/Kaeppel calendar-boundary tuning after iteration 009 because the pre-fixed
seasonal variant failed OOS/FWD/bootstrap. Avoid local cross-asset adjusted-slope
momentum/risk-parity tuning after iteration 010 because it failed economic,
WF/OOS/FWD and bootstrap gates. Prefer a new literature-grounded mechanism rather
than another local variant of SPY/QQQ relative momentum, SPY-only trend gating,
simple calendar seasonality, or cross-asset adjusted-slope momentum.
