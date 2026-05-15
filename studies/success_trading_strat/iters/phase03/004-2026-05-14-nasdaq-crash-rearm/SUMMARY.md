# SUMMARY - Phase 3 Iteration 004

## Verdict

`economic_beater_not_validated`. No winner, no deploy implication, mandate remains 100% Plano C.

## Tested

Six pre-registered Nasdaq crash-rearm configs that hold `QQQ` by default and switch temporarily to `QLD` after `QQQ` suffers a fixed drawdown and recovers above a 50d or 100d SMA. This is a distinct mechanism from the prior continuous LETF volatility-target families: it uses post-stress re-risking rather than persistent vol scaling or cash defense `[leverage_for_the_long_run, p.16-17]`, `[systematic_trading, p.119]`, `[testing_tuning, p.327-335]`.

Physical daily-file audit confirmed `QQQ`, `QLD`, `SPY` and `SHV` parquets exist through 2026-05-13 with usable `close`/`adj_close` columns.

## Benchmark Comparison

Best config by pre-registered Sharpe selection: `qqq_qld_rearm_dd35_sma100_h189`.

- Strategy: CAGR `18.64%`, terminal wealth `27.79x`, Sharpe `0.831`, MDD `-62.20%`.
- Primary `QQQ` buy-and-hold on aligned dates: CAGR `16.39%`, terminal wealth `19.18x`, Sharpe `0.797`, MDD `-53.41%`.
- Context `QLD` buy-and-hold: CAGR `25.03%`, terminal wealth `77.21x`, MDD `-83.16%`.
- `SPY` opportunity cost: CAGR `11.05%`, terminal wealth `7.69x`.

The Phase 3 economic gate passed versus primary `QQQ` buy-and-hold in both CAGR and terminal wealth. The rule did not beat raw `QLD` buy-and-hold, and it had worse MDD than `QQQ`.

## Gates

- IS MCPT: fail, `p=0.135` vs required `<=0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.550` vs required `<=0.05` `[testing_tuning, p.318-320]`.
- PBO: pass, `0.230 < 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.2006` with cumulative `n_trials=240` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, `15/16` positive.
- OOS and FWD 63d: pass.
- Bootstrap: pass, 99.9% mean daily CI low `0.0000253`.
- Cross-lib/vector parity: pass.
- Joint-path MCPT caveat: fail by construction; MCPT used synthetic 2x `QQQ` booster proxy because joint `QQQ`/`QLD` path permutation is not implemented.

## Lessons

Crash rearm produced a genuine economic beater versus `QQQ`, but the statistical profile is weak: both MCPT gates and DSR failed, so the observed Sharpe is not sufficiently unusual after permutation and cumulative trial accounting. The caveated MCPT proxy also blocks any strict promotion even if the numeric gates had passed.

## Next Step

Continue Phase 3 with a different mechanism rather than local tuning. The next recommended branch is high-beta relative rotation over `QQQ`/`SMH`/`SOXX`/`XLK` or crypto/equity rotation if physical files are confirmed, because Phase 3 needs return-engine diversity after four LETF/crash-management iterations `[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`.
