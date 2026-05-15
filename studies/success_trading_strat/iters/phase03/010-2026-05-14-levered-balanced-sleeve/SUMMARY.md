# SUMMARY - Phase 3 Iteration 010

## Verdict

`economic_beater_not_validated`. No winner, no deploy implication, mandate remains
100% Plano C.

## Tested

Fixed levered balanced sleeves using real `UPRO` with `TLT`/`GLD` diversifiers and
monthly or quarterly rebalance. Four configs were pre-registered. The mechanism was
embedded leverage plus structural diversification, not another daily long/flat
filter `[leverage_for_the_long_run, p.13]`, `[systematic_trading, p.137-148]`,
`[leverage_space, p.149-167]`.

## Benchmark Comparison

Best config: `upro50_tlt25_gld25_quarterly`.

- Strategy CAGR: 24.13%.
- Strategy terminal wealth: 38.16x.
- Conservative primary `SPY` buy-and-hold CAGR/terminal wealth: 15.23% / 10.89x.
- Conservative primary equal-weight `UPRO/TLT/GLD` CAGR/terminal wealth: 18.59% / 17.68x.
- Strategy MDD: -44.80% vs `SPY` -33.70% and equal-weight -36.47%.
- `UPRO` buy-and-hold context remained higher CAGR/terminal wealth: 33.20% / 125.26x.

The Phase 3 economic gate passed under the conservative dual-primary rule, but
validation did not pass.

## Gates

- Economic CAGR vs `SPY`: pass.
- Economic terminal wealth vs `SPY`: pass.
- Economic CAGR vs equal-weight `UPRO/TLT/GLD`: pass.
- Economic terminal wealth vs equal-weight `UPRO/TLT/GLD`: pass.
- MDD not worse than 1.5x primary benchmark MDD: pass.
- IS MCPT: pass (`p=0.000`; pass requires `p <= 0.01`).
- WF MCPT: fail (`p=0.490`; pass requires `p <= 0.05`).
- PBO: pass (`0.357`; pass requires `<0.5`).
- DSR: fail (`p=0.09769`; cumulative trials after = 264).
- Walk-forward windows: pass (`12/13` positive).
- OOS: pass (`+181.86%`).
- FWD 63d: pass (`+8.63%`).
- Bootstrap 99.9% mean daily CI: pass (low `0.000266`).
- Cross-lib/reference parity: pass (`0.0pp` CAGR delta).

## Lessons

The sleeve is the strongest Phase 3 diagnostic so far economically: it beat both
conservative primary B&H benchmarks with low turnover and no local signal tuning.
However, the WF-MCPT failure and DSR p-value above 0.05 keep it research-only.
It may be capturing favorable historical `UPRO`/bond/gold sequencing rather than a
statistically defensible timing edge.

## Next Step

Do not promote or paper trade. A next iteration may stress the same economic family
with a genuinely new pre-registered robustness question, such as inception-window
sensitivity, rebalance-frequency robustness, or replacing `UPRO` with `SSO`, but
must count new trials explicitly and preserve the same buy-and-hold kill rule
`[testing_tuning, p.327-335]`.
