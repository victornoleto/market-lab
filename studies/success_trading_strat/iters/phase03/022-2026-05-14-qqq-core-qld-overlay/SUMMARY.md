# SUMMARY - Phase 3 Iteration 022

## Verdict

`economic_beater_not_validated`. The best config beat `QQQ` buy-and-hold in CAGR
and terminal wealth, but failed strict validation gates. No `strict_winner`, no
`candidate_watchlist`, no `paper_trade_candidate`, and no deploy implication.
Capital remains 100% Plano C.

## Tested

Tested 4 pre-registered `QQQ` core + conditional `QLD` overlay configs. Signals used
lagged `QQQ` momentum and lagged realized volatility caps; gross exposure above 1.0
paid a 5% annual financing drag `[leverage_for_the_long_run, p.13]`,
`[leverage_for_the_long_run, p.7]`, `[systematic_trading, p.137-148]`.

Physical daily files existed for `QQQ`, `QLD`, `SPY` and `SHV` through 2026-05-13.

## Benchmark Comparison

Best config: `mom126_vol63_cap25`.

- Strategy: CAGR 23.19%, terminal wealth 56.02x, Sharpe 0.798, MDD -63.92%.
- Primary `QQQ` B&H: CAGR 16.31%, terminal wealth 18.46x, Sharpe 0.792, MDD -53.41%.
- Opportunity `SPY` B&H: CAGR 10.97%, terminal wealth 7.45x.
- Context `QLD` B&H: CAGR 24.84%, terminal wealth 72.37x, MDD -83.16%.

The Phase 3 economic gate passed versus `QQQ` and `SPY`, but the strategy did not
beat raw `QLD` context in CAGR/terminal wealth.

## Gates

- Economic CAGR/terminal vs `QQQ`: pass.
- Economic CAGR vs `SPY`: pass.
- MDD within 1.5x `QQQ` MDD: pass.
- IS MCPT: fail (`p=0.065`).
- WF MCPT: fail (`p=0.260`).
- PBO: fail (`0.738`).
- DSR: fail (`p=0.2723`, cumulative trials 300).
- WF windows: pass (`12/16`).
- OOS: pass (`+285.44%`).
- FWD 63d: pass (`+27.69%`).
- Bootstrap 99.9%: fail (CI low `-0.00000570`).
- Cross-lib/reference arithmetic: pass.

Kill switch: failed strict validation gates `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Lessons

A permanent `QQQ` core with `QLD` overlay can beat `QQQ` economically over the full
aligned window, but the edge looks selection-sensitive and overfit-prone under PBO,
MCPT, DSR and bootstrap. The result is research evidence only, not a promotion.

## Next Step

Do not locally tune the same `QQQ` momentum/vol overlay thresholds, lookbacks or
overlay sizes. Prefer a final closure audit or a genuinely different Phase 3
mechanism with new preregistration `[testing_tuning, p.327-335]`.
