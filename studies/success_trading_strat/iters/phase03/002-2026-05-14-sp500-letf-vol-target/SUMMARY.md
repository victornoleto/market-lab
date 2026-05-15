# SUMMARY - Phase 3 Iteration 002

## Verdict

`economic_beater_not_validated`. No winner, no deploy implication, mandate remains 100% Plano C.

## Tested

Six pre-registered S&P LETF volatility-targeting configs over `SSO`/`UPRO`, with one-bar-lagged realized-volatility weights, capped LETF allocation and optional crash drawdown multiplier. The mechanism was chosen because Phase 3 requires a buy-and-hold beating return engine and this is a distinct S&P LETF universe from the prior Nasdaq LETF test `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.5-7]`, `[systematic_trading, p.137-148]`.

Physical daily-file audit confirmed required tested files (`SPY`, `SSO`, `UPRO`, `SHV`) and context `QQQ` exist through 2026-05-13 with usable close/adjusted-close columns.

## Benchmark Comparison

Best config: `upro_vt40_rv63_dd30_half`.

- Strategy: CAGR `20.54%`, terminal wealth `22.19x`, Sharpe `0.717`, MDD `-46.48%`.
- Primary `SPY` buy-and-hold on aligned dates: CAGR `14.57%`, terminal wealth `9.56x`, Sharpe `0.880`, MDD `-33.70%`.
- Same LETF `UPRO` buy-and-hold context: CAGR `30.84%`, terminal wealth `86.57x`, MDD `-76.82%`.
- `QQQ` opportunity cost on aligned dates: CAGR `19.69%`, terminal wealth `19.76x`.

The Phase 3 economic gate passed versus primary `SPY` buy-and-hold in CAGR and terminal wealth. It also narrowly beat aligned `QQQ` terminal wealth and CAGR, but it did not beat simply holding `UPRO`.

## Gates

- IS MCPT: fail, `p=0.565` vs required `<=0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.370` vs required `<=0.05` `[testing_tuning, p.318-320]`.
- PBO: pass, `0.206 < 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.4551` with cumulative `n_trials=228` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, `9/13` positive.
- OOS and FWD 63d: pass.
- Bootstrap: fail, 99.9% mean daily CI low `-0.000171`.
- Cross-lib/vector parity: pass.

## Lessons

S&P LETF volatility targeting can beat `SPY` economically, but the validation profile is weaker than needed: MCPT sees the observed Sharpe as common under the permuted null, DSR is far from pass after cumulative trial accounting, and the bootstrap low is negative. The same-LETF context again shows the path-control overlay gives up large terminal wealth relative to leveraged buy-and-hold.

## Next Step

Move to semis LETF exposure (`SMH`/`SOXX -> SOXL`/`TECL`) or a crash-rearmed core/booster rule rather than tuning S&P/Nasdaq LETF volatility-target windows, target-vol levels or crash multipliers `[testing_tuning, p.327-335]`.
