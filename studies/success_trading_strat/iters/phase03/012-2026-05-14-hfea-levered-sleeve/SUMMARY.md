# SUMMARY - Phase 3 Iteration 012

## Verdict

`economic_beater_not_validated`. No winner, no deploy implication, mandate remains
100% Plano C.

## Tested

HFEA-style fixed levered sleeves using real `UPRO` + real `TMF` + `GLD`, with
monthly or quarterly rebalance. Four configs were pre-registered. Physical daily
files existed for all required tickers, but `TMF` data ended at 2026-04-30, so the
aligned test window ended there.

The mechanism was leveraged equity plus leveraged Treasury/gold diversification,
not a daily long/flat filter `[leverage_for_the_long_run, p.13]`,
`[systematic_trading, p.137-148]`, `[leverage_space, p.149-167]`.

## Benchmark Comparison

Best config: `upro50_tmf30_gld20_quarterly`.

- Strategy CAGR: 24.43%.
- Strategy terminal wealth: 39.43x.
- Conservative primary `SPY` buy-and-hold CAGR/terminal wealth: 15.04% / 10.55x.
- Conservative primary equal-weight `UPRO/TMF/GLD` CAGR/terminal wealth: 18.53% / 17.43x.
- Strategy MDD: -58.69% vs `SPY` -33.70% and equal-weight -53.02%.
- `UPRO` buy-and-hold context was much higher CAGR/terminal wealth: 32.54% / 114.09x.

The Phase 3 economic gate passed under the conservative dual-primary rule, but
strict validation failed.

## Gates

- Economic CAGR vs `SPY`: pass.
- Economic terminal wealth vs `SPY`: pass.
- Economic CAGR vs equal-weight `UPRO/TMF/GLD`: pass.
- Economic terminal wealth vs equal-weight `UPRO/TMF/GLD`: pass.
- MDD not worse than 1.5x primary benchmark MDD: pass.
- IS MCPT: fail (`p=0.045`; pass requires `p <= 0.01`).
- WF MCPT: fail (`p=0.580`; pass requires `p <= 0.05`).
- PBO: pass (`0.087`; pass requires `<0.5`).
- DSR: fail (`p=0.11491`; cumulative trials after = 272).
- Walk-forward windows: pass (`12/13` positive).
- OOS: pass (`+101.39%`).
- FWD 63d: fail (`-0.42%`).
- Bootstrap 99.9% mean daily CI: pass (low `0.0001796`).
- Cross-lib/reference parity: pass (`0.0pp` CAGR delta).

## Lessons

Leveraged Treasury exposure improved the economic result versus the `SSO/TLT/GLD`
stress and cleared PBO/bootstrap, but the result remains statistically fragile:
both MCPT gates failed, DSR failed at cumulative `n_trials=272`, and the latest
63-day stress was slightly negative. The result also does not beat pure `UPRO`
buy-and-hold, so the diversification benefit does not dominate the highest-beta
context benchmark.

Public docs were already modified before this iteration and contain out-of-band
state; this loop did not edit them to avoid overwriting unrelated dirty-worktree
changes. The canonical loop update for this iteration is in `MEMORY.md`.

## Next Step

Do not promote or paper trade. Avoid local tuning of HFEA weights/rebalance cadence
after MCPT/DSR failure. Next Phase 3 work should pivot to a different mechanism,
such as a pre-registered inception-window sensitivity audit for the economic
beaters or a new Track C crash-rearm idea `[testing_tuning, p.327-335]`.
