# SUMMARY - Phase 3 Iteration 001

## Verdict

`economic_beater_not_validated`. No winner, no deploy implication, mandate remains 100% Plano C.

## Tested

Six pre-registered Nasdaq LETF volatility-targeting configs over `QLD`/`TQQQ`, with one-bar-lagged realized-volatility weights, capped LETF allocation and optional crash drawdown multiplier. The mechanism was chosen because Phase 3 requires a buy-and-hold beating return engine rather than another defensive long/flat filter `[leverage_for_the_long_run, p.13]`, `[systematic_trading, p.137-148]`.

Physical daily-file audit was completed for the Phase 3 required asset set. Required tested files (`SPY`, `QQQ`, `QLD`, `TQQQ`, `SHV`) were present. Crypto files exist as lowercase `btcusd`/`ethusd`; uppercase `BTCUSD`/`ETHUSD` are absent, which is recorded but not blocking for this LETF iteration.

## Benchmark Comparison

Best config: `qld_vt35_rv21_dd25_half`.

- Strategy: CAGR `22.12%`, terminal wealth `52.01x`, Sharpe `0.870`, MDD `-48.14%`.
- Primary `QQQ` buy-and-hold on aligned dates: CAGR `17.16%`, terminal wealth `22.90x`, Sharpe `0.829`, MDD `-53.41%`.
- Same LETF `QLD` buy-and-hold context: CAGR `26.69%`, terminal wealth `107.48x`, MDD `-83.16%`.

The Phase 3 economic gate passed versus primary `QQQ` buy-and-hold in CAGR and terminal wealth, but the same-LETF context shows the result is not superior to simply holding `QLD`.

## Gates

- IS MCPT: fail, `p=0.050` vs required `<=0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.310` vs required `<=0.05` `[testing_tuning, p.318-320]`.
- PBO: pass, `0.421 < 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.1472` with cumulative `n_trials=222` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, `13/16` positive.
- OOS, FWD 63d, bootstrap and cross-lib: pass.

## Lessons

Controlled LETF volatility targeting can beat `QQQ` economically, unlike most Phase 2 defensive filters, but this first family did not survive MCPT/DSR and gives up large terminal wealth versus `QLD` buy-and-hold. The MCPT fix used log-shifted positive price paths because direct simple-return permutations of LETFs can create nonpositive synthetic prices; this conservative ambiguity is recorded and does not promote the result.

## Next Step

Stress a distinct S&P LETF volatility-targeting mechanism (`SPY -> SSO/UPRO`) or move to semis LETF exposure per Phase 3 recommended iterations. Do not locally tune the `QLD` vol-lookback/target/drawdown variants without a new mechanism `[testing_tuning, p.327-335]`.
