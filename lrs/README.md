# LRS Restart

Research-only restart of the Gayed-style Leverage Rotation Strategy (LRS):
hold leveraged equity exposure when the underlying is above its moving average,
otherwise rotate defensively `[leverage_for_the_long_run, p.13]`.

No result in this folder authorizes live trading, paper trading, or a mandate
change. Overfit diagnostics such as PBO, DSR, walk-forward, OOS, bootstrap and
cross-library checks are recorded as diagnostics during evolution; any future
promotion claim must still clear the repository mandate gates
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Read Order

1. `SPEC.md` - scope, score, phases and constraints.
2. `MEMORY.md` - live ledger of decisions and results.
3. `NEXT_STEPS.md` - clean-session handoff and next verification checklist.
4. `phases/phase07f_composition/REPORT.md` + the 7A/7D reports - the Phase 7
   round survivors awaiting the user's Phase 8 pick.
5. `phases/phase06a_aftertax_frontier/REPORT.md` - the after-tax mix decision
   table from the Phase 6 round.
6. `TOP20_BY_CAGR.md` - return-first ranking requested by the user.
7. Earlier phase reports under `phases/phase00_*` .. `phases/phase07f_*`
   (Phase 6 run order: 6C -> 6B -> 6D -> 6A; Phase 7 order: 7A -> 7B -> 7C ->
   7D -> 7E -> 7F; READMEs are the authority).

## Current Status

The restart starts from the original LRS idea only:

- signal: underlying close above SMA200;
- cadence: weekly first trading day;
- risk-on: branch-native leveraged ETF proxy when available;
- risk-off: `CASHX`;
- operational settlement lag: `n = 0..5` daily bars between liquidating a sleeve
  and entering the new sleeve;
- tax: annual Brazilian DARF model via `AnnualDarfEngine`.

Phase 1 added risk-off alternatives. Phase 2 then varied target leverage and
simple realized-volatility throttles before broad indicator work. Phases 3A,
3A-2 and 3C tested filters, regime forms and lookbacks; none improved the
standalone base enough. Phase 4 ran mandate-style validation gates and closed
standalone LRS as research-only: `0/6` bases passed all gates.

Latest result: the Phase 7 round (7A -> 7B -> 7C -> 7D -> 7E -> 7F,
2026-06-09; trial ledger 4005 -> 4377) attacked the binding walk-forward gate
with six pre-registered mechanism families. Survivors: **7A ensemble
multi-lookback** on SPY (`spy_alt_off / narrow {150,175,200,225} / lag 2`, WF
**13/17 = 76.5%** - the restart's first row at the G3 level; CAGR 14.49%, MDD
-43.16%) and **7D quadratic vol-targeting** on QQQ (`sigma 40% / RV21 / lag 2`,
WF 8/11, CAGR 19.53%, MDD -42.63%). 7B (EW multi-asset portfolio), 7C (macro
GTT/UNRATE - biggest WF lift but breaks the MDD floor), and 7F (composition)
all failed their pre-registered screens honestly; 7E (managed-futures
risk-off) is a weak low-power SPY lead. Next honest step is Phase 8: the full
mandate gate suite with `n_trials = 4377` on at most 2 user-chosen configs.
Nothing is validated or promoted.

Previous round: the Phase 6 round (run order 6C -> 6B -> 6D -> 6A, 2026-06-09)
answered the user's actual question - "is any mix worth giving up part of a
100%-static position?". 6C showed the walk-forward failures are bull-window
concentrated (90.9%) with `bear_high` beat rate 100%; 6B's continuous
vol-targeting was a QQQ-only diagnostic SUCCESS (WF 7/11 vs 6/11); 6D's capped
inverse sleeve FAILED on both branches. Phase 6A (REVISED after the user's tax
correction: static cores rebalance via contributions -> no intermediate DARF,
final-liquidation DARF only; LRS satellites keep the annual engine) built the
after-tax frontier on 2000+: RSC is `11.74% / -30.76% / Calmar 0.382` and **13
of 18 mixes beat it on both CAGR and Calmar while reducing MDD** - top by
Calmar `80/20 RSC x SPY-headline` (`12.12%`, `-25.18%`, `0.481`). Part 2 (10k +
1k/month contributions, buy-most-underweight, no sells): **all 18 mixes beat
100% RSC on money-weighted IRR** (RSC `13.72%`; `70/30 RSC x QQQ-voltarget`
`15.21%` at RSC-like path risk). This is a decision table, not a promotion:
any chosen mix still requires the full mandate gate suite with `n_trials >=
4005` `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.273-275]`.

## Plot Convention

Every phase should generate plots under its own `plots/` directory. At minimum,
phase reports should include:

- after-tax equity curves;
- drawdown curves;
- relative equity versus the aligned underlying benchmark;
- parameter/cadence sensitivity plots when applicable.
