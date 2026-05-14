# PRE_REG — 012 VIX-managed stress

## Hypothesis

Iteration 011 found the strongest statistical evidence in this study but failed
the latest 63-trading-day forward-stress gate. This iteration keeps the same
VIX-managed mechanism and tests whether the failure was caused by too much
recent de-risking, too short a VIX averaging window, or an overly concentrated
`QQQ` sleeve. The mechanism remains inverse exposure to previous VIX
`[paper.bozovic_2024_vix_managed, §methodology]`; stress/robustness follow-up
after a promising result follows Masters' rule that the next test must be
explicitly pre-registered rather than locally tuned after validation feedback
`[testing_tuning, p.327-335]`.

Hard gates remain MCPT, PBO, DSR, WF, OOS, FWD, bootstrap and cross-lib
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Data and Window

- Prices: local Tiingo daily adjusted close for `SPY`, `QQQ`, and `SHV`.
- VIX: local `data/phase3_7/vix/VIXCLS.parquet`.
- Window: common daily intersection from `2010-01-01` onward.
- Timing: VIX signal is shifted by one trading day before execution to avoid
  same-close lookahead `[advances_fin_ml, p.196-202]`.

## Exact Configs

Exposure rule for risk sleeve `R`:

`raw_t = clip(vix_anchor / mean(VIX_{t-window:t-1}), 0, 1)`

`weight_t = equity_floor + (1 - equity_floor) * raw_t`

Daily return:

`weight_t * R_return_t + (1 - weight_t) * SHV_return_t`

Pre-registered configs:

| name | sleeve | vix_window | vix_anchor | equity_floor |
|---|---:|---:|---:|---:|
| `qqq_vix15_w21_floor25` | `100% QQQ` | 21 | 15 | 0.25 |
| `qqq_vix15_w21_floor50` | `100% QQQ` | 21 | 15 | 0.50 |
| `qqq_vix15_w42_floor25` | `100% QQQ` | 42 | 15 | 0.25 |
| `basket_vix15_w21_floor25` | `50% SPY / 50% QQQ` | 21 | 15 | 0.25 |

The 21-day and 42-day windows represent one and two trading months; the floor
variants stress whether always keeping a partial equity allocation is more robust
than full de-risking, while the basket variant stresses concentration risk. These
are fixed before testing and consume four new trials `[paper.bozovic_2024_vix_managed,
§methodology]`, `[testing_tuning, p.327-335]`.

## Benchmark

- Same risk sleeve buy-and-hold on the same common window.
- `SHV` as cash/opportunity-cost diagnostic.
- Economic pass requires best config Sharpe > same-sleeve buy-and-hold Sharpe.

## Planned Gates

- IS MCPT on best fixed config: 200 permutations, pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT on best fixed config: 100 permutations, 1008d train / 252d test / 252d
  step, pass if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO over the four configs with 8 blocks, pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR with cumulative trials after this iteration (`36`), pass if `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6/8 positive windows `[testing_tuning, p.148-150]`.
- OOS: final 20% total return positive `[advances_fin_ml, p.196-202]`.
- FWD stress hard gate: latest 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Additional FWD diagnostics: latest 126d and 252d total returns; failure here is
  recorded but does not override the mandate's 63d hard gate unless 63d fails.
- Bootstrap: 99.9% CI low of mean daily return > 0 `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy path CAGR within +/-3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If VIX or required ETF data are unavailable, stop as `data_blocked`; do not
  substitute realized-vol, `VIXY`, or `VXX` after pre-registration.
- If the best config fails FWD 63d, record `fail` even if other gates pass.
- If the best config fails benchmark Sharpe, MCPT, PBO, or DSR, record `fail` and
  do not locally tune floors/windows in this iteration.
- If VIX timing cannot be shifted by one bar, record `fail` because lookahead risk
  invalidates the claim.

## Trial Accounting

- `cumulative_n_trials` before: 32.
- `n_trials` this iteration: 4.
- `cumulative_n_trials` after: 36.

## Capital Guard

Research-only. Capital remains 100% Plano C; no deployment authorization.
