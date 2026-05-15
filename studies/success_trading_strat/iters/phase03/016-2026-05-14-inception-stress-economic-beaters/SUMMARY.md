# SUMMARY - Phase 3 Iteration 016

## Verdict

`fail`. No winner, no candidate/watchlist label, no deploy implication, mandate
remains 100% Plano C.

## Tested

Pre-registered inception-window sensitivity audit across five prior Phase 3
economic beaters: iter 010 `UPRO/TLT/GLD`, iter 011 `SSO/TLT/GLD`, iter 012
`UPRO/TMF/GLD`, iter 013 Nasdaq crash-rearm booster, and iter 014 `UPRO/TLT`
changed; this was a stress/consolidation audit, not a new strategy search
`[testing_tuning, p.327-335]`, `[leverage_for_the_long_run, p.13]`,
`[leverage_space, p.149-167]`.

Physical daily benchmark files existed for all required tickers: `SPY`, `QQQ`,
`UPRO`, `SSO`, `QLD`, `TQQQ`, `TLT`, `TMF`, `GLD` and `SHV`.

## Benchmark Comparison

Stress windows were full saved history, `2010-01-01`, `2015-01-01` and
`2020-01-01`, each requiring CAGR and terminal wealth above both the same-market
buy-and-hold benchmark and the equal-weight opportunity benchmark.

Result: 19/20 config-window rows passed the economic stress, but one failed the
pre-registered kill rule. `012_upro50_tmf30_gld20_quarterly` from `2020-01-01`
had CAGR 14.56% and terminal wealth 2.36x versus `SPY` buy-and-hold CAGR 15.22%
and terminal wealth 2.44x. That single aligned-window failure is enough for the
iteration verdict to remain `fail`.

## Gates

- Economic inception stress: fail, 1/20 rows failed.
- MCPT/PBO/DSR/WF/OOS/FWD/bootstrap/cross-lib: not recomputed in this audit.
- Prior validation failures remain binding: yes.
- New strategy trials: 0; cumulative trials remain 284.

## Lessons

Most prior economic beaters remained economically above their benchmarks under
coarse inception shifts, but robustness is not sufficient for promotion because
their original MCPT/DSR and other hard-gate failures still block them. The HFEA
`UPRO/TMF/GLD` sleeve also fails the 2020 inception economic test versus `SPY`,
confirming that at least one apparent beater is start-date fragile.

## Next Step

Do not promote or paper-trade any audited beater. If Phase 3 continues, use a
genuinely different mechanism or a stricter robustness audit; do not locally tune
balanced-sleeve weights, rebalance cadence, crash-rearm triggers, volatility caps,
gross weights or financing assumptions.
