# SUMMARY - Phase 3 Iteration 020

## Verdict

`fail`. No strict winner, no candidate/watchlist label, no paper-trade label, no
deploy implication. Capital remains 100% Plano C.

## Tested

Pre-registered dynamic risk-parity LETF sleeves: monthly inverse-volatility weights
over `UPRO/TLT/GLD` or `SSO/TLT/GLD`, using 63d or 126d realized-vol windows, gross
`1.00` or `1.25`, and explicit 5% annual financing drag above gross 1.0. Four
configs were tested `[leverage_for_the_long_run, p.13]`, `[risk_parity, p.80-81]`,
`[systematic_trading, p.137-148]`.

Best config: `upro_rp126_g125`.

## Benchmark Comparison

Aligned window: 2010-01-06 to 2026-05-13.

- Strategy CAGR: 12.13%; terminal wealth: 6.48x.
- Primary equal-weight `UPRO/TLT/GLD` B&H CAGR: 17.28%; terminal wealth: 13.48x.
- `SPY` opportunity B&H CAGR: 14.20%; terminal wealth: 8.74x.
- Context `UPRO` B&H CAGR: 29.51%; terminal wealth: 68.04x.

The Phase 3 economic kill rule fired: the strategy lost to both the primary
equal-weight buy-and-hold benchmark and SPY in CAGR and terminal wealth.

## Gates

- Physical daily files: pass for `SPY`, `UPRO`, `SSO`, `TLT`, `GLD`, `SHV`.
- Economic CAGR/terminal wealth vs primary equal-weight universe: fail.
- Economic CAGR/terminal wealth vs SPY opportunity: fail.
- IS MCPT: fail (`p=0.745`; required `<=0.010`).
- WF MCPT: fail (`p=0.680`; required `<=0.050`).
- PBO: pass (`0.000`; required `<0.500`).
- DSR: fail (`p=0.2752`; required `<0.050`, `cumulative_n_trials=296`).
- WF windows: pass (`9/13` positive).
- OOS: pass (`+87.42%`).
- FWD 63d: fail (`-0.77%`).
- Bootstrap 99.9% mean daily CI: fail (`low=-0.0000137`).
- Cross-lib/reference parity: pass (`0.00pp` CAGR delta).

## Lessons

Inverse-vol risk budgeting reduced drawdown versus raw `UPRO`, but it shifted too
much average capital to `TLT`/`GLD` and gave up the return engine needed to beat
buy-and-hold. This is another example where improved ride quality is not enough for
Phase 3 if CAGR and terminal wealth do not beat aligned B&H `[systematic_trading,
p.40]`.

## Next Step

Do not locally tune risk-parity lookbacks, gross caps or the same `UPRO/SSO` +
`TLT/GLD` inverse-vol family. Since 20 Phase 3 iterations have not produced a strict
winner, prefer a consolidation/closure audit or only a genuinely new mechanism with
pre-registered rationale `[testing_tuning, p.327-335]`.
