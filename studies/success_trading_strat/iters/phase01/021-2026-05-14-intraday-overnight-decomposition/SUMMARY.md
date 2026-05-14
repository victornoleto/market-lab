# SUMMARY — 021 intraday/overnight decomposition

## Verdict

`fail`. The best config improved Sharpe and drawdown versus same-window `QQQ`
buy-and-hold, but failed IS MCPT, WF MCPT and DSR. No winner claim.

## What Was Tested

Four pre-registered daily adjusted-OHLC component rules decomposed `SPY` and
`QQQ` into close-to-open and open-to-close legs, with `SHV` only as the defensive
idle return for open-to-close configs. This was a new intraday/overnight
mechanism, not a local retune of prior VIX/carry/credit/crypto/Ehlers/calendar
families `[paper.zarattini_2024_intraday_spy, §methodology]`,
`[trading_systems_methods, p.939]`, `[testing_tuning, p.327-335]`.

## Benchmark Comparison

- Best `qqq_close_to_open`: CAGR 12.44%, Sharpe 0.998, MDD -27.43%.
- Same-window `QQQ` buy-and-hold benchmark: CAGR 19.25%, Sharpe 0.958, MDD -35.12%.
- The strategy passed the pre-registered Sharpe benchmark and reduced drawdown,
  but sacrificed CAGR and did not survive statistical validation.

## Gates

- Data freshness: pass, common data ended 2026-05-13.
- Economic Sharpe vs benchmark: pass, 0.998 > 0.958.
- IS MCPT: fail, `p=1.000` with 200 reps. Because the winning rule is an
  unconditional close-to-open component, row-order permutation preserves its
  return distribution and makes this MCPT intentionally conservative but not
  promotional `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.430` with 100 reps and 12 WF windows.
- PBO: pass, `0.086` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.0600` using cumulative `n_trials=72` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 11/12 positive versus required 6.
- OOS: pass, final 20% return +77.77%.
- FWD stress: pass, latest 63 observations +1.67%.
- Bootstrap: pass, 99.9% mean daily CI low `0.000147`.
- Cross-lib: pass, NumPy-style CAGR delta 0.00pp.

## Lessons

The close-to-open anomaly is economically real enough to lift Sharpe and reduce
drawdown, but as an unconditional component it is not a strategy winner under the
study's MCPT/DSR guardrails. The MCPT result also shows that component-only rules
without a timing decision are poor fits for this workflow unless a separate,
pre-registered selection signal is introduced.

## Next Step

Do not tune session definitions or add filters locally. If continuing, use a
genuinely different information source or explicitly pre-register a timing signal
whose decisions can be attacked by MCPT; otherwise pause rather than accumulating
more weak trials `[testing_tuning, p.327-335]`.

## Ambiguity Note

The worktree already had unrelated modified/untracked files before this iteration
(`docs/`, Tiingo data/script files, and the broader untracked study scaffold). I
did not revert them and only wrote the iteration artifacts plus study memory.
`docs/CURRENT_STATE.md` was also updated minimally because the repo rule treats a
run verdict as public project progress.
