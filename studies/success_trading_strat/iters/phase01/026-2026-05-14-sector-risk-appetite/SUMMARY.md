# SUMMARY — 026 sector risk appetite

## Verdict

`fail`. Sector relative-strength risk appetite reduced drawdown versus buy-and-hold
but did not beat same-asset Sharpe and failed IS MCPT, WF MCPT, PBO and DSR. No
winner claim.

## What Was Tested

Four pre-registered sector-pair filters: `XLY/XLP` gated `SPY`, and `XLK/XLU`
gated `QQQ`, each with 63d and 126d ratio momentum. Signals were lagged one bar
and idle capital held `SHV`. This was a distinct intermarket/sector leadership
information source `[trading_systems_methods, p.13]`, `[trading_systems_methods,
p.542-544]`.

## Benchmark Comparison

- Best `spy_xly_xlp_m126`: CAGR 8.18%, Sharpe 0.825, MDD -16.18%.
- Same-window `SPY` buy-and-hold: CAGR 14.22%, Sharpe 0.862, MDD -33.70%.
- The strategy improved drawdown but lost to SPY on CAGR and Sharpe.

## Gates

- Data freshness: pass, common data ended 2026-05-13.
- Economic Sharpe vs benchmark: fail, 0.825 < 0.862.
- IS MCPT: fail, `p=0.250` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.210` with 100 reps and 12 WF windows.
- PBO: fail, `0.800` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.2082` using cumulative `n_trials=92` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 10/12 positive versus required 6.
- OOS: pass, final 20% return +21.84%.
- FWD stress: pass, latest 63 observations +0.85%.
- Bootstrap: pass, 99.9% mean daily CI low `0.0000575`.
- Cross-lib: pass, NumPy-style CAGR delta 0.00pp.

## Lessons

Sector leadership behaved as another defensive drawdown reducer, not a robust
edge. High PBO and weak MCPT results show that the best pair/lookback selection is
noise-sensitive despite positive WF/OOS/FWD diagnostics.

## Next Step

Do not tune sector pairs, ratio lookbacks or zero-momentum thresholds locally. If
the study continues, pivot to a new information source or pause
`[testing_tuning, p.327-335]`.

## Ambiguity Note

The worktree already contained unrelated modified/untracked files before this
iteration. I did not revert them. I only wrote iteration 026 artifacts, updated
`MEMORY.md`, and made the required public-state note in `docs/CURRENT_STATE.md`.
