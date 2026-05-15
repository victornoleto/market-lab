# SUMMARY - Phase 3 Iteration 014

## Verdict

`economic_beater_not_validated`. No winner, no deploy implication, mandate remains
100% Plano C.

## Tested

UPRO/TLT gross-exposure spread using real `SPY`, `UPRO`, `TLT` and `SHV` daily
data. Four configs were pre-registered. The strategy holds `SHV` in risk-off and,
when `SPY` is above its SMA, holds a leveraged equity/short-bond spread with a
5% annual financing/borrow proxy on gross exposure above 1.0 and short notional
`[leverage_for_the_long_run, p.4-7]`, `[leverage_for_the_long_run, p.13]`,
`[systematic_trading, p.137-148]`.

Physical daily files existed for all required tickers through 2026-05-13.

## Benchmark Comparison

Best config: `upro125_tlt25_sma200`.

- Strategy CAGR: 17.76%.
- Strategy terminal wealth: 15.70x.
- Primary `SPY` buy-and-hold CAGR/terminal wealth: 15.23% / 10.89x.
- Equal-weight `UPRO/TLT/SHV` CAGR/terminal wealth: 15.33% / 11.05x.
- Strategy MDD: -64.92% vs `SPY` -33.70% and equal-weight -34.25%.
- Raw `UPRO` buy-and-hold context was much stronger: 33.20% CAGR and 125.26x.

The Phase 3 economic CAGR/terminal-wealth gate passed versus the pre-registered
primary benchmarks, but strict validation failed.

## Gates

- Economic CAGR vs `SPY`: pass.
- Economic terminal wealth vs `SPY`: pass.
- Economic CAGR vs equal-weight `UPRO/TLT/SHV`: pass.
- Economic terminal wealth vs equal-weight `UPRO/TLT/SHV`: pass.
- MDD not worse than 1.5x primary benchmark MDD: fail.
- IS MCPT: fail (`p=0.540`; pass requires `p <= 0.01`).
- WF MCPT: fail (`p=0.220`; pass requires `p <= 0.05`).
- PBO: pass (`0.381`; pass requires `<0.5`).
- DSR: fail (`p=0.6641`; cumulative trials after = 280).
- Walk-forward windows: pass (`9/13` positive).
- OOS: pass (`+222.60%`).
- FWD 63d: pass (`+8.56%`).
- Bootstrap 99.9% mean daily CI: fail (low `-0.0001424`).
- Cross-lib/reference parity: pass (`0.0pp` CAGR delta).

## Lessons

The gross-exposure spread beat the conservative Phase 3 primary benchmarks but
did so with worse drawdown, weak MCPT evidence, failed DSR and failed bootstrap.
The short `TLT` hedge plus financing did not dominate raw `UPRO` buy-and-hold and
does not justify promotion or local tuning.

## Next Step

Do not promote or paper trade. Do not locally tune `UPRO/TLT` gross weights, SMA
windows or financing assumptions after MCPT/DSR/bootstrap failure. Next Phase 3
work should move to a genuinely different mechanism or run a pre-registered
inception-window sensitivity audit across prior economic beaters
`[testing_tuning, p.327-335]`.
