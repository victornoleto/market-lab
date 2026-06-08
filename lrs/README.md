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
4. `phases/phase02_target_leverage_vol/REPORT.md` - latest phase report.
5. `results/phase02_target_leverage_vol.csv` - latest machine-readable table.
6. Earlier phase reports under `phases/phase00_*` and `phases/phase01_*`.

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
simple realized-volatility throttles before broad indicator work.

Latest result: Phase 2 evaluated 2,400 rows. The top score row is `SPY` target
leverage `2.00`, risk-off `50 ZROZ / 25 GLD / 25 CASH`, `RV21 <= 30%`, lag `3`,
after-tax CAGR `15.44%`, MDD `-39.28%` and Calmar `0.393`. Best QQQ is target
leverage `1.75`, risk-off `40 ZROZ / 40 GLD / 20 IEF`, `RV63 <= 40%`, lag `0`,
after-tax CAGR `19.46%`, MDD `-42.58%` and Calmar `0.457`. This is still
research-only and not deployment-ready.

## Plot Convention

Every phase should generate plots under its own `plots/` directory. At minimum,
phase reports should include:

- after-tax equity curves;
- drawdown curves;
- relative equity versus the aligned underlying benchmark;
- parameter/cadence sensitivity plots when applicable.
