# SUMMARY - Phase 3 Iteration 023

## Verdict

`fail`. The best config beat `QQQ` and `SPY` buy-and-hold, but failed the
pre-registered primary equal-weight `SMH/SOXX` opportunity benchmark and failed
strict validation gates. No `strict_winner`, no `candidate_watchlist`, no
`paper_trade_candidate`, and no deploy implication. Capital remains 100% Plano C.

## Tested

Tested 4 pre-registered `QQQ` core + conditional `SOXL/TECL` overlay configs.
Signals used lagged `SMH` or `SOXX` relative strength versus `QQQ`, lagged LETF
realized-volatility caps, and 5% annual financing drag on gross exposure above
1.0 `[leverage_for_the_long_run, p.13]`, `[stocks_on_the_move, p.66-67]`,
`[systematic_trading, p.137-148]`.

Physical daily files existed for `QQQ`, `SMH`, `SOXX`, `SOXL`, `TECL`, `SPY` and
`SHV` through 2026-05-13.

## Benchmark Comparison

Best config: `soxx_qqq_m126_v63_tecl25`.

- Strategy: CAGR 20.93%, terminal wealth 21.48x, Sharpe 1.003, MDD -35.12%.
- Primary `QQQ` B&H: CAGR 19.34%, terminal wealth 17.37x, Sharpe 0.961, MDD -35.12%.
- Primary equal-weight `SMH/SOXX` B&H: CAGR 26.80%, terminal wealth 46.22x.
- Opportunity `SPY` B&H: CAGR 14.26%, terminal wealth 8.60x.
- Context `SOXL` B&H: CAGR 42.56%, terminal wealth 306.10x; `TECL` B&H: CAGR 41.15%, terminal wealth 260.82x.

The Phase 3 economic gate failed because the strategy did not beat the
pre-registered equal-weight semiconductor opportunity benchmark in CAGR or
terminal wealth.

## Gates

- Economic CAGR/terminal vs `QQQ`: pass.
- Economic CAGR/terminal vs equal-weight `SMH/SOXX`: fail.
- Economic CAGR vs `SPY`: pass.
- MDD within 1.5x `QQQ` MDD: pass.
- IS MCPT: pass (`p=0.000`).
- WF MCPT: fail (`p=0.680`).
- PBO: pass (`0.333`).
- DSR: fail (`p=0.1319`, cumulative trials 304).
- WF windows: pass (`11/13`).
- OOS: pass (`+139.23%`).
- FWD 63d: pass (`+16.72%`).
- Bootstrap 99.9%: pass (CI low `0.0001327`).
- Cross-lib/reference arithmetic: pass.

Kill switches: failed equal-weight `SMH/SOXX` economic gate and strict validation
gates `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.

## Lessons

Sector-leadership overlay improved `QQQ` modestly, but the overlay fired rarely
(`8.70%` of days for the best config) and could not compete with simply owning the
semiconductor opportunity universe. WF MCPT and DSR also reject promotion.

## Next Step

Do not locally tune `SMH/SOXX` relative-strength overlay lookbacks, vol caps,
overlay weights or `SOXL/TECL` variants. Prefer closure/consolidation or a truly
different Phase 3 mechanism `[testing_tuning, p.327-335]`.
