# Weekly Momentum

Final report: `FINAL_REPORT.md` is the canonical closure document for this
study. It gives the TL;DR verdict, phase-by-phase evolution, final plots versus
SPY and the final rejection after Tiingo backfill plus expanded PIT rerun.

Study for weekly cross-sectional momentum across two variations:

- `stocks`: cached Tiingo tickers with `asset_class="equity"`.
- `etfs`: cached Tiingo tickers with `asset_class="etf"`.

Final consolidation: `reports/STRATEGY_TESTED_SUMMARY.md` summarizes all strategy
families tested so far, compares the top-6 decision-relevant variants against
SPY, and links the final plots. Verdict: no variant is deployable; the best
research lead is approximate-PIT `lb80/k5/SMA250`, still blocked by DSR and
survivorship-free/delisted data limitations `[advances_fin_ml, p.273-275]`.

Post-close ETF-specific evolution is summarized in
`reports/ETF_FOCUS_EVOLUTION_REPORT.md`. A focused ETF WF grid improved the ETF
diagnostic to 11.29% CAGR / 0.712 Sharpe versus SPY 10.63% / 0.619 when
leveraged/inverse ETFs are allowed, but falls to 6.65% CAGR without them. Verdict
remains research-only: the full-universe diagnostic fails DSR (`p=0.152`) and
the no-leverage diagnostic fails DSR/bootstrap `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.273-275]`. This post-close ETF branch is now closed; future
work requires a new pre-registered hypothesis, not more local sweeps.

Phase 4: `reports/PHASE4_REPORT.md` uses Tiingo online backfill plus expanded PIT loading
for current/start-date/selected-change S&P 500 names. Coverage improved to
745/769 tickers and 240/260 likely removed/renamed names, but the frozen
`lb80/k5` leads weakened and fail DSR/bootstrap. Verdict: stop the stock weekly
momentum family unless a new pre-registered hypothesis changes the signal.

Phase 5 branch: `reports/PHASE5B_ROBUSTNESS_REPORT.md` and
`reports/PHASE5C_ADV5M_OPTIMIZATION_REPORT.md` cover the distinct all-stocks
dynamic walk-forward hypothesis using PIT tradability filters (age, price,
ADV20) instead of S&P 500 membership. ADV5M is economically strong but fails
PBO/bootstrap, so it remains research-only.

Cleaned structure after closure:

- `core.py`, `data.py`, `reporting.py`: importable study package used by tests and runners.
- `scripts/`: operational runners, sweeps, validators and one-off analysis helpers.
- `reports/`: phase reports and strategy summaries retained as the audit trail.
- `evidence/`: small decision-relevant evidence bundles retained after cleanup.
- `plots/final/`: final report plots retained; bulk generated run folders were removed.
- `plots/phase5/`: Phase 5/5b/5c ADV5M comparison plots versus SPY.

For `stocks`, the default universe is the current S&P 500 constituent list
intersected with the Tiingo cache. Use `--stock-universe all` to disable that
filter.

Initial configuration:

- rank assets by adjusted-close appreciation over the last `4` trading days, using the Thursday close;
- hold the single strongest asset (`top_k=1`);
- compute the signal on Thursday, sell on Friday if the winner changes, and buy on Monday when `settlement_delay_days=0`;
- if the winner is unchanged, keep the position;
- if `settlement_delay_days=1`, stay in cash on Monday and buy Tuesday.
- if all ranked assets have non-positive trailing return, sell and stay in cash by default.

Parameters:

- `lookback_days`: momentum ranking lookback; initial value `4`, intended sweep `4..30`.
- `signal_weekday`: weekday used to compute the signal; initial value `3` (Thursday).
- `sell_delay_days`: trading bars after the signal before selling; initial value `1` (Friday after Thursday signal).
- `settlement_delay_days`: extra trading bars in cash after a sale; `0` buys on the next trading bar, `1` skips one trading bar.
- `require_positive_momentum`: enabled by default; if all candidates are negative, the target is cash.
- `defensive_asset`: optional defensive ticker (for example `ZROZ`) used instead of cash when all candidates are negative and the ticker is present in the price frame.
- `market_filter_sma_days`: optional market regime filter; when set, risk-on holdings are allowed only while SPY is above the chosen SMA window.
- `stock_universe`: `sp500` by default for stocks, or `all` to use every cached equity.
- `top_k`: number of top-ranked assets to hold equally weighted; initial value `1`.

Run example:

```bash
uv run python studies/weekly_momentum/scripts/run.py --variation etfs --lookback-days 4 --settlement-delay-days 0
```

New runs write generated outputs to:

```text
studies/weekly_momentum/results/{variation}/{config_slug}/
```

For the initial config this is:

```text
studies/weekly_momentum/results/stocks/lb4_sig3_sell1_sd0_k1_pos1_defcash_mf0/
```

Each run writes CSV/JSON artifacts, SPY benchmark files, plots and a deterministic
`report.md`. These generated bundles are not part of the cleaned final study
record. See `REPORT_SPEC.md` for the required report contract.

Research notes:

- Cross-sectional momentum ranking follows the baseline premise cited in `[stocks_on_the_move, p.60]`.
- Weekly review cadence follows Clenow's weekly rebalance convention, where weekday choice is operational rather than predictive `[stocks_on_the_move, p.98-99]`.
- Using Friday close to decide a Friday sale is look-ahead with daily data. The default therefore uses Thursday close for the signal and Friday for the sale.
- A future `lookback_days=5` run means a rolling 5-pregão signal ending Thursday, for example prior Friday through current Thursday.
- Candidate robustness filter from the first diagnostic pass: `--top-k 5 --market-filter-sma-days 100`, which diversified single-name risk and avoided risk-on exposure when SPY was below SMA100.
- The current data helper uses the cached current Tiingo universe, so reports must disclose survivorship bias unless replaced with a point-in-time universe.
- The S&P 500 filter is a current-constituent liquidity/quality filter, not a point-in-time universe; survivorship bias remains.
- The simulator is a daily close-to-close proxy. Open/close execution should be added before interpreting “Monday buy / Friday sell” operationally.
- Runtime LLM calls are intentionally excluded; interpretation can be added manually or by an agent after reading the deterministic report.
