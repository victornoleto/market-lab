# SUMMARY — 007 volatility carry proxy

## Verdict

`data_blocked`. The hypothesis was pre-registered, but the required `VIXY`
adjusted-close file was not present under the local Tiingo price cache. To
preserve the pre-registration, the runner did not substitute `VXX` after the
block was discovered.

## What Was Tested

No strategy configs were tested. The intended family was a long-only equity
exposure filter using negative trailing `VIXY` returns as a volatility-carry proxy:
hold `SPY` or `QQQ` when the proxy was negative, otherwise hold `SHV`
`[systematic_trading, p.32-35]`, `[systematic_trading, p.119]`.

## Benchmark Comparison

Not computed because no return series was generated. `n_trials=0`; cumulative DSR
trial accounting remains `16`.

## Gates

No MCPT, PBO, DSR, WF, OOS, FWD, bootstrap or cross-lib gates were computed. The
kill switch `required_data_missing` fired before any strategy evaluation.

## Lessons

The conservative interpretation of the pre-registration rule matters: replacing
`VIXY` with available `VXX` after discovering the missing file would create an
unregistered data/indicator change. This iteration therefore records the data
block rather than converting it into an unplanned test.

## Next Step

If continuing the volatility-carry mechanism, pre-register a new iteration using
only confirmed available data such as `VXX`, or first audit/restore `VIXY` in an
infrastructure-only step. Do not count this blocked attempt as evidence for or
against the strategy family `[testing_tuning, p.327-335]`.
