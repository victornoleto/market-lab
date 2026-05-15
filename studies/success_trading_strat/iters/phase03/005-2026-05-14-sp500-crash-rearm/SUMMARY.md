# SUMMARY - Phase 3 Iteration 005

## Verdict

`economic_beater_not_validated`. No winner, no deploy implication, mandate remains 100% Plano C.

## Tested

Six pre-registered S&P crash-rearm configs that hold `SPY` by default and switch temporarily to `SSO` after `SPY` suffers a fixed drawdown and recovers above a 50d or 100d SMA. This tests post-stress re-risking on a broader S&P return engine rather than local-tuning the prior Nasdaq crash-rearm result `[leverage_for_the_long_run, p.16-17]`, `[systematic_trading, p.119]`, `[testing_tuning, p.327-335]`.

Physical daily-file audit confirmed `SPY`, `SSO`, `QQQ` and `SHV` parquets exist through 2026-05-13 with usable `close`/`adj_close` columns.

## Benchmark Comparison

Best config by pre-registered Sharpe selection: `spy_sso_rearm_dd35_sma100_h189`.

- Strategy: CAGR `13.05%`, terminal wealth `10.87x`, Sharpe `0.691`, MDD `-55.20%`.
- Primary `SPY` buy-and-hold on aligned dates: CAGR `11.05%`, terminal wealth `7.69x`, Sharpe `0.633`, MDD `-55.20%`.
- Context `SSO` buy-and-hold: CAGR `15.06%`, terminal wealth `15.32x`, MDD `-84.67%`.
- `QQQ` opportunity cost: CAGR `16.39%`, terminal wealth `19.18x`.

The Phase 3 economic gate passed versus primary `SPY` buy-and-hold in both CAGR and terminal wealth. The rule did not beat raw `SSO` or `QQQ` opportunity context.

## Gates

- IS MCPT: fail, `p=0.095` vs required `<=0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.500` vs required `<=0.05` `[testing_tuning, p.318-320]`.
- PBO: fail, `0.778 >= 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.4147` with cumulative `n_trials=246` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, `15/16` positive.
- OOS and FWD 63d: pass.
- Bootstrap: fail, 99.9% mean daily CI low `-0.00000847`.
- Cross-lib/vector parity: pass.
- Joint-path MCPT caveat: fail by construction; MCPT used synthetic 2x `SPY` booster proxy because joint `SPY`/`SSO` path permutation is not implemented.

## Lessons

S&P crash rearm produced a modest economic beater versus `SPY`, but the evidence is weaker than the Nasdaq version: both MCPT gates failed, PBO was high, DSR was far from passing and bootstrap crossed zero. The broad-market S&P variant appears too close to benchmark beta plus a few high-variance booster windows.

## Next Step

Pivot away from LETF vol-target/crash-rearm local variants. The next recommended branch is high-beta relative rotation over confirmed `QQQ`/`SMH`/`SOXX`/`XLK`, because Phase 3 needs a different return-selection mechanism after five LETF/crash-management iterations `[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`.
