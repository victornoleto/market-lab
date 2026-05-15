# SUMMARY - Phase 3 Iteration 003

## Verdict

`economic_beater_not_validated`. No winner, no deploy implication, mandate remains 100% Plano C.

## Tested

Six pre-registered semiconductor/technology LETF volatility-targeting configs over `SOXL`/`TECL`, with one-bar-lagged realized-volatility weights, capped LETF allocation and optional crash drawdown multiplier. The mechanism was chosen because Phase 3 requires a buy-and-hold beating return engine and this is a distinct semis/tech LETF universe from the prior Nasdaq and S&P LETF tests `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.5-7]`, `[systematic_trading, p.137-148]`.

Physical daily-file audit confirmed required tested files (`SMH`, `SOXX`, `SOXL`, `TECL`, `QQQ`, `SHV`) and context files (`XLK`, `SPY`) exist through 2026-05-13 with usable close/adjusted-close columns.

## Benchmark Comparison

Best config: `tecl_vt40_rv63`.

- Strategy: CAGR `34.00%`, terminal wealth `148.14x`, Sharpe `0.922`, MDD `-49.24%`.
- Primary `QQQ` buy-and-hold on aligned dates: CAGR `21.02%`, terminal wealth `25.99x`, Sharpe `1.032`, MDD `-35.12%`.
- Primary equal-weight `SMH/SOXX` buy-and-hold on aligned dates: CAGR `27.89%`, terminal wealth `66.76x`, Sharpe `0.986`, MDD `-45.52%`.
- Same LETF `TECL` buy-and-hold context: CAGR `47.33%`, terminal wealth `748.52x`, MDD `-77.96%`.
- `SPY` opportunity cost on aligned dates: CAGR `15.71%`, terminal wealth `12.09x`.

The Phase 3 economic gate passed versus both primary buy-and-hold benchmarks in CAGR and terminal wealth. It did not beat simply holding `TECL`.

## Gates

- IS MCPT: fail, `p=0.490` vs required `<=0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.670` vs required `<=0.05` `[testing_tuning, p.318-320]`.
- PBO: pass, `0.206 < 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.1636` with cumulative `n_trials=234` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, `10/14` positive.
- OOS and FWD 63d: pass.
- Bootstrap: pass, 99.9% mean daily CI low `0.000299`.
- Cross-lib/vector parity: pass.

## Lessons

Semis/tech LETF volatility targeting is economically powerful versus unlevered `QQQ` and `SMH/SOXX`, but the validation profile is still not close: MCPT sees the observed Sharpe as common under the permuted null, and DSR remains above the hard threshold after cumulative trial accounting. The overlay also gives up massive terminal wealth versus raw `TECL` buy-and-hold.

## Next Step

Move away from local LETF volatility-target variants. A crash-rearmed core/booster rule is the next distinct Phase 3 mechanism, because it changes the exposure logic from continuous vol scaling to explicit re-risking after stress `[testing_tuning, p.327-335]`.
