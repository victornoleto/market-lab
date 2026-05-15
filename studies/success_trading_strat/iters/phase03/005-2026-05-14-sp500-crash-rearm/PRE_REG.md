# PRE_REG - Phase 3 Iteration 005

## Hypothesis

Test an S&P 500 crash-rearmed exposure rule: hold `SPY` as the core asset and switch temporarily to `SSO` only after a material `SPY` drawdown has recovered above a moving average. The mechanism is intended to beat buy-and-hold by adding controlled leverage after stress rather than by sitting in cash, consistent with Phase 3 Track C `[leverage_for_the_long_run, p.16-17]`, `[systematic_trading, p.119]`.

This is not a local tune of the prior Nasdaq rearm result. It tests the same economic mechanism on the broader S&P engine with a distinct traded booster and primary benchmark, preserving post-failure mechanism diversity `[testing_tuning, p.327-335]`.

## Data And Window

- Required physical daily parquets: `SPY`, `SSO`, `QQQ`, `SHV`.
- Use adjusted close when available; no intraday synthesis.
- Aligned test window is the intersection of `SPY` and `SSO`, after warmup.
- Audit must record rows, first/last date, columns, timezone and missing-business-day rate.

## Configs

Six pre-registered configs, all signals shifted by one completed daily bar:

| name | trigger_drawdown | recovery_sma | booster_hold |
|---|---:|---:|---:|
| `spy_sso_rearm_dd15_sma50_h63` | -15% | 50 | 63 |
| `spy_sso_rearm_dd20_sma50_h63` | -20% | 50 | 63 |
| `spy_sso_rearm_dd25_sma50_h126` | -25% | 50 | 126 |
| `spy_sso_rearm_dd20_sma100_h126` | -20% | 100 | 126 |
| `spy_sso_rearm_dd30_sma100_h126` | -30% | 100 | 126 |
| `spy_sso_rearm_dd35_sma100_h189` | -35% | 100 | 189 |

Drawdown trigger, SMA recovery and finite booster hold are the only strategy parameters. Drawdown re-risking follows the Phase 3 crash-rearm rationale `[leverage_for_the_long_run, p.16-17]`; SMA is used as a volatility/regime proxy rather than a return enhancer `[leverage_for_the_long_run, p.7-8]`; finite hold avoids an ordinary long/flat SMA system and records path-dependency risk `[systematic_trading, p.119]`.

## Benchmarks

- Primary: `SPY` buy-and-hold on the same aligned dates.
- Context: `SSO` buy-and-hold, because it is the traded booster.
- Opportunity cost: `QQQ` buy-and-hold.

## Economic Kill Rule

If strategy CAGR <= primary `SPY` buy-and-hold CAGR or strategy terminal wealth <= primary `SPY` buy-and-hold terminal wealth, verdict must be `fail`. No `economic_beater_not_validated`, `candidate_watchlist`, `paper_trade_candidate` or `strict_winner` is allowed without beating both economic gates `[systematic_trading, p.40]`.

## Validation Gates

- IS MCPT, preferred pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the six configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration `[advances_fin_ml, p.222-223]`.
- Walk-forward positives at repo threshold.
- OOS positive, latest 63d FWD positive, bootstrap 99.9% mean-return CI low > 0 and cross-lib/vector parity within +/-3pp CAGR `[advances_fin_ml, p.196-202]`, `[testing_tuning, p.246-247]`, `[advances_fin_ml, p.31-34]`.

## MCPT Caveat

MCPT will use a synthetic 2x `SPY` booster derived from the permuted `SPY` path because joint-path permutation for `SPY`/`SSO` is not implemented in the current scaffold. This caveat blocks `strict_winner` unless a future iteration implements joint-path MCPT before promotion.

## Trial Accounting

- `cumulative_n_trials` before: 240.
- New strategy configs: 6.
- `cumulative_n_trials` after: 246.

## Kill Rules

- Missing required daily parquet or close column => `data_blocked`.
- Economic gate failure versus primary `SPY` B&H => `fail`.
- Any hard validation gate failure after economic pass => at most `economic_beater_not_validated`.
- No deploy implication; capital remains 100% Plano C.
