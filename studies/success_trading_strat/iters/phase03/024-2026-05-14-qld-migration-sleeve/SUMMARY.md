# SUMMARY - Phase 3 Iteration 024

## Verdict

`economic_beater_not_validated`. The best config beat both pre-registered primary
benchmarks in CAGR and terminal wealth, but failed strict validation gates and had
MDD worse than the Phase 3 1.5x primary-benchmark guard. No `strict_winner`, no
`candidate_watchlist`, no `paper_trade_candidate`, and no deploy implication.
Capital remains 100% Plano C.

## Tested

Tested 4 pre-registered monthly `QLD/TLT/GLD` sleeve configs with a small
drawdown-triggered `QLD` gross boost and 5% annual financing drag on gross exposure
above 1.0 `[leverage_space, p.149-167]`, `[leverage_for_the_long_run, p.13]`,
`[systematic_trading, p.137-148]`.

Physical daily files existed for `QLD`, `TLT`, `GLD`, `QQQ`, `SPY` and `SHV`.

## Benchmark Comparison

Best config: `qld70_tlt15_gld15_dd25_boost50`.

- Strategy: CAGR 23.62%, terminal wealth 59.95x, Sharpe 0.738, MDD -80.45%.
- Primary `QQQ` B&H: CAGR 16.31%, terminal wealth 18.46x, Sharpe 0.792, MDD -53.41%.
- Primary equal-weight `QLD/TLT/GLD` B&H: CAGR 15.78%, terminal wealth 16.90x, Sharpe 0.992, MDD -37.16%.
- Opportunity `SPY` B&H: CAGR 10.97%, terminal wealth 7.45x.
- Context `QLD` B&H: CAGR 24.84%, terminal wealth 72.37x, MDD -83.16%.

The Phase 3 economic gate passed versus the two primary benchmarks, but the result
did not beat raw `QLD` buy-and-hold context and accepted near-LETF-level drawdown.

## Gates

- Economic CAGR/terminal vs `QQQ`: pass.
- Economic CAGR/terminal vs equal-weight `QLD/TLT/GLD`: pass.
- Economic CAGR vs `SPY`: pass.
- MDD within 1.5x `QQQ` MDD: fail (`-80.45%` vs limit about `-80.11%`).
- IS MCPT: fail (`p=0.740`).
- WF MCPT: fail (`p=0.780`).
- PBO: pass (`0.135`).
- DSR: fail (`p=0.3668`, cumulative trials 308).
- WF windows: pass (`14/16`).
- OOS: pass (`+286.76%`).
- FWD 63d: pass (`+20.68%`).
- Bootstrap 99.9%: pass (CI low `0.0000335`).
- Cross-lib/reference arithmetic: pass.

Kill switches: MDD guard and strict validation gates `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.222-223]`.

## Lessons

The migration sleeve is an economic beater but mostly repackages high `QLD`
exposure: average `QLD` weight was 78.19%, gross max 1.5, and boost was active on
16.39% of days. MCPT and DSR reject promotion, and drawdown is essentially raw
LETF risk.

## Next Step

Do not locally tune `QLD/TLT/GLD` weights, drawdown triggers, boost sizes,
rebalance cadence or financing assumptions. Prefer a Phase 3 consolidation/closure
audit or a genuinely different mechanism `[testing_tuning, p.327-335]`.
