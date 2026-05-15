# PRE_REG - Phase 3 Iteration 025

## Hypothesis

Prior Phase 3 economic beaters are leveraged or gross-exposure mechanisms whose
edge may be too thin after realistic extra frictions. This iteration does not tune
or introduce a new strategy. It audits whether all prior economic beaters remain
economic beaters after uniform additional strategy-only annual drag stresses of
25 bps, 50 bps and 100 bps. Leveraged ETF implementations can trail theory via
negative leverage premium `[leverage_for_the_long_run, p.21]`, retail costs can
dominate small active systems `[systematic_trading, p.185-188]`, and failed
families should be stress-tested or abandoned rather than locally tuned
`[testing_tuning, p.327-335]`.

## Configs

Stress prior Phase 3 economic beaters with saved `returns.csv` artifacts:

- `001_qld_vt35_rv21_dd25_half`: primary `QQQ` buy-and-hold.
- `002_upro_vt40_rv63_dd30_half`: primary `SPY` buy-and-hold.
- `003_tecl_vt40_rv63`: primary `QQQ` and equal-weight `SMH/SOXX`.
- `004_qqq_qld_rearm_dd35_sma100_h189`: primary `QQQ`.
- `005_spy_sso_rearm_dd35_sma100_h189`: primary `SPY`.
- `006_top2_m63`: primary equal-weight `QQQ/SMH/SOXX/XLK`.
- `008_top2_m63_dd15_boost125_cap150`: primary equal-weight `QQQ/SMH/SOXX/XLK`.
- `010_upro50_tlt25_gld25_quarterly`: primary `SPY` and equal-weight `UPRO/TLT/GLD`.
- `011_sso75_tlt15_gld10_quarterly`: primary `SPY` and equal-weight `SSO/TLT/GLD`.
- `012_upro50_tmf30_gld20_quarterly`: primary `SPY` and equal-weight `UPRO/TMF/GLD`.
- `013_qld_tqqq_dd25_recover_sma50_rv40`: primary `QQQ` and equal-weight `QQQ/QLD/TQQQ`.
- `014_upro125_tlt25_sma200`: primary `SPY` and equal-weight `UPRO/TLT/SHV`.
- `018_qqq_tqqq_vxx95_norm70_h126`: primary `QQQ`.
- `019_top2_m126_g125`: primary equal-weight `QLD/SSO/SMH/SOXX`.
- `022_mom126_vol63_cap25`: primary `QQQ`.
- `024_qld70_tlt15_gld15_dd25_boost50`: primary `QQQ` and equal-weight `QLD/TLT/GLD`.

Stress levels: `0.0025`, `0.0050`, `0.0100` annual drag, applied daily as
`annual_drag / 252` to strategy returns only. No MCPT/PBO/DSR is recomputed;
prior validation failures remain binding `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Data And Window

Use saved candidate returns from each source iteration and physical daily Tiingo
parquets for benchmark closes. Align each candidate to its own saved returns
index and benchmark availability. Audit required physical files before computing:
`SPY`, `QQQ`, `QLD`, `TQQQ`, `SSO`, `UPRO`, `SMH`, `SOXX`, `XLK`, `TECL`, `TLT`,
`TMF`, `GLD`, `SHV` and `VXX` where needed.

## Benchmarks

Benchmark hierarchy is candidate-specific and follows each source iteration's
primary Phase 3 benchmark. `SPY` buy-and-hold is also reported as opportunity
context when not already primary. The hard economic rule remains aligned CAGR and
terminal wealth versus the primary buy-and-hold benchmark(s)
`[systematic_trading, p.40]`.

## Kill Rule

If any prior economic beater has stressed CAGR or stressed terminal wealth less
than or equal to any of its primary buy-and-hold benchmarks under any stress
level, this audit closes `fail`. This is conservative because the Phase 3 rule
does not allow labels above `fail` without aligned CAGR and terminal wealth above
the primary benchmark.

## Planned Gates

- Physical data files present: required for benchmark reconstruction.
- Stressed economic CAGR: every candidate and stress level must beat all primary
  benchmarks.
- Stressed terminal wealth: every candidate and stress level must beat all primary
  benchmarks.
- Prior MCPT/PBO/DSR/WF/OOS/FWD/bootstrap/cross-lib failures remain binding and
  are not recomputed.

## Trial Accounting

- `cumulative_n_trials` before: 308.
- New strategy/config trials: 0, because this is an audit of saved prior configs.
- `cumulative_n_trials` after: 308.
