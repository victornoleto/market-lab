# SUMMARY - Phase 3 Iteration 009

## Verdict

`fail`. No winner, no deploy implication, mandate remains 100% Plano C.

## Tested

High-beta relative-momentum long/short over `QQQ/SMH/SOXX/XLK` with explicit gross
exposure and a 5% annual financing/borrow proxy. Four configs used one-bar lagged
signals and stayed fully exposed with net exposure near zero `[stocks_on_the_move,
p.66-67]`, `[trading_systems_methods, p.542-544]`, `[systematic_trading,
p.137-148]`.

## Benchmark Comparison

Best config: `ls_m63_top1_bottom1_g100`.

- Strategy CAGR: -3.77%.
- Primary equal-weight `QQQ/SMH/SOXX/XLK` buy-and-hold CAGR: 19.18%.
- Strategy terminal wealth: 0.48x.
- Primary benchmark terminal wealth: 28.26x.
- Strategy MDD: -63.51% vs benchmark MDD -57.45%.
- SPY opportunity CAGR: 10.91%.

The Phase 3 economic kill rule fired: CAGR and terminal wealth were both below the
primary buy-and-hold benchmark, so no label above `fail` is allowed.

## Gates

- Economic CAGR vs primary B&H: fail.
- Economic terminal wealth vs primary B&H: fail.
- SPY opportunity CAGR: fail.
- IS MCPT: fail (`p=0.750`; pass requires `p <= 0.01`).
- WF MCPT: fail (`p=0.640`; pass requires `p <= 0.05`).
- PBO: pass (`0.433`; pass requires `<0.5`).
- DSR: fail (`p=0.999999`; cumulative trials after = 260).
- Walk-forward windows: fail (`5/16` positive; pass requires at least `6/8`).
- OOS: pass (`+17.08%`).
- FWD 63d: pass (`+10.96%`).
- Bootstrap 99.9% mean daily CI: fail (low `-0.000331`).
- Cross-lib/reference parity: pass (`0.0pp` CAGR delta).

## Lessons

Naive high-beta long/short relative momentum structurally failed to capture the
large common upside drift in semis/tech. The short book and financing proxy turned
the opportunity universe's strong long-only return into negative compound growth.

## Next Step

Do not tune long/short lookbacks, gross, top/bottom counts or financing in this
family. Continue Phase 3 with a different mechanism, preferably a non-local Track B
or Track C idea that keeps the common equity beta upside instead of shorting it
`[testing_tuning, p.327-335]`.
