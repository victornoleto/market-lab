# SUMMARY - 027 commodity macro filter

## Verdict

`data_blocked`. The pre-registered commodity macro filter could not be tested
honestly because `data/tiingo/daily/prices/DBC.parquet` is unavailable. No trials
were consumed and no winner claim is made.

## What Was Tested

Nothing was backtested. The pre-registered family required `SPY`, `TLT`, `SHV`,
`DBC` and `GLD` to test commodity momentum as an intermarket macro filter for
equity/bond exposure. The premise and sparse parameter count were chosen before
testing `[trading_systems_methods, p.939]`, with quarterly/semiannual lookbacks
as natural calendar horizons `[trading_systems_methods, p.285]`.

## Benchmark Comparison

Not computed. The intended benchmarks were same-window `SPY` buy-and-hold for
`SPY` configs and same-window `TLT` buy-and-hold for `TLT` configs.

## Gates

- Data availability: fail, `DBC.parquet` missing.
- IS MCPT: not computed.
- WF MCPT: not computed.
- PBO: not computed.
- DSR: not computed; cumulative `n_trials` remains 92.
- WF/OOS/FWD/bootstrap/cross-lib: not computed.

## Lessons

The commodity-macro mechanism is not rejected economically; it is blocked by the
pre-registered data requirement. The conservative rule is to avoid substituting
another commodity proxy after seeing the data problem `[testing_tuning, p.327-335]`.

## Next Step

If this study continues, either pre-register a commodity-proxy audit iteration or
pivot to another genuinely different information source with confirmed local data.

## Ambiguity Note

The worktree already contained unrelated modified/untracked files before this
iteration. I did not revert them. I only wrote iteration 027 artifacts and updated
the study memory/public-state notes. A preliminary shell existence check did not
surface the missing `DBC` file; the runner's explicit file load is treated as the
authoritative result, so the iteration is recorded as `data_blocked`.
