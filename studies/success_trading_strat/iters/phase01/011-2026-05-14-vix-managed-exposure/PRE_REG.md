# PRE_REG — 011 VIX-managed exposure

## Hypothesis

Test whether a simple VIX-managed equity exposure improves risk-adjusted returns
versus buy-and-hold by scaling exposure down when implied volatility is elevated.
This is a mechanism pivot away from local price-only ETF technical rules after
iteration 010. The design follows the VIX-managed portfolio thesis: inverse
exposure to previous-month VIX can improve net Sharpe with lower turnover than
realized-volatility scaling `[paper.bozovic_2024_vix_managed, §methodology]`.
The use of small fixed configs and hard MCPT/PBO/DSR gates follows Masters and
Lopez de Prado `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Data and Window

- Prices: local Tiingo daily adjusted close for `SPY`, `QQQ`, and `SHV`.
- VIX: local `data/phase3_7/vix/VIXCLS.parquet`.
- Window: common daily intersection from `2010-01-01` onward.
- Timing: VIX signal is shifted by one trading day before execution to avoid
  same-close lookahead `[advances_fin_ml, p.196-202]`.

## Exact Configs

Exposure rule for asset `A`:

`weight_t = clip(vix_anchor / mean(VIX_{t-21:t-1}), 0, 1)`

Daily return:

`weight_t * A_return_t + (1 - weight_t) * SHV_return_t`

Pre-registered configs:

| name | asset | vix_window | vix_anchor | cap |
|---|---:|---:|---:|---:|
| `spy_vix15_w21` | `SPY` | 21 | 15 | 1.0 |
| `spy_vix20_w21` | `SPY` | 21 | 20 | 1.0 |
| `qqq_vix15_w21` | `QQQ` | 21 | 15 | 1.0 |
| `qqq_vix20_w21` | `QQQ` | 21 | 20 | 1.0 |

The 21-day window approximates the previous trading month described in the VIX
paper. Anchors 15 and 20 are fixed low/normal VIX levels for a small smoke, not
optimized after seeing this iteration's results `[paper.bozovic_2024_vix_managed,
§methodology]`, `[testing_tuning, p.327-335]`.

## Benchmark

- Same-asset buy-and-hold (`SPY` or `QQQ`) on the same common window.
- `SHV` as cash/opportunity-cost diagnostic.
- Economic pass requires best config Sharpe > same-asset buy-and-hold Sharpe.

## Planned Gates

- IS MCPT on best fixed config: 200 permutations, pass if `p <= 0.01` when
  feasible `[testing_tuning, p.318-320]`.
- WF MCPT on best fixed config: 100 permutations, 1008d train / 252d test / 252d
  step, pass if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO over the four configs with 8 blocks, pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR with cumulative trials after this iteration, pass if `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6/8 positive windows `[testing_tuning, p.148-150]`.
- OOS: final 20% total return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% CI low of mean daily return > 0 `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy path CAGR within +/-3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If VIX or required ETF data are unavailable, stop as `data_blocked`; do not
  substitute `VIXY`, `VXX`, or realized-vol filters after pre-registration.
- If the best config fails benchmark Sharpe, MCPT, PBO, or DSR, record `fail` and
  do not locally tune anchors/windows in this iteration.
- If VIX timing cannot be shifted by one bar, record `fail` because lookahead risk
  invalidates the claim.

## Trial Accounting

- `cumulative_n_trials` before: 28.
- `n_trials` this iteration: 4.
- `cumulative_n_trials` after: 32.

## Capital Guard

Research-only. Capital remains 100% Plano C; no deployment authorization.
