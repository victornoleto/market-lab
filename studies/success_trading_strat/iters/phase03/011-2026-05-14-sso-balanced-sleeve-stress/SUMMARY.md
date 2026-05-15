# SUMMARY - Phase 3 Iteration 011

## Verdict

`economic_beater_not_validated`. No winner, no deploy implication, mandate remains
100% Plano C.

## Tested

Robustness stress of the fixed levered balanced-sleeve family: replaced `UPRO`
with lower-leverage real `SSO` in fixed `SSO/TLT/GLD` monthly/quarterly sleeves.
Four configs were pre-registered. The mechanism remained embedded leverage plus
structural diversification, not a daily long/flat filter `[leverage_for_the_long_run,
p.13]`, `[systematic_trading, p.137-148]`, `[leverage_space, p.149-167]`.

## Benchmark Comparison

Best config: `sso75_tlt15_gld10_quarterly`.

- Strategy CAGR: 14.76%.
- Strategy terminal wealth: 14.27x.
- Conservative primary `SPY` buy-and-hold CAGR/terminal wealth: 10.97% / 7.45x.
- Conservative primary equal-weight `SSO/TLT/GLD` CAGR/terminal wealth: 12.06% / 9.00x.
- Strategy MDD: -71.22% vs `SPY` -55.20% and equal-weight -34.21%.
- `SSO` buy-and-hold context was slightly higher CAGR/terminal wealth: 14.88% / 14.55x.

The Phase 3 economic gate passed under the conservative dual-primary rule, but
validation did not pass.

## Gates

- Economic CAGR vs `SPY`: pass.
- Economic terminal wealth vs `SPY`: pass.
- Economic CAGR vs equal-weight `SSO/TLT/GLD`: pass.
- Economic terminal wealth vs equal-weight `SSO/TLT/GLD`: pass.
- MDD not worse than 1.5x primary benchmark MDD: pass.
- IS MCPT: fail (`p=0.035`; pass requires `p <= 0.01`).
- WF MCPT: fail (`p=0.420`; pass requires `p <= 0.05`).
- PBO: pass (`0.389`; pass requires `<0.5`).
- DSR: fail (`p=0.51230`; cumulative trials after = 268).
- Walk-forward windows: pass (`13/16` positive).
- OOS: pass (`+144.94%`).
- FWD 63d: pass (`+9.41%`).
- Bootstrap 99.9% mean daily CI: fail (low `-0.0000809`).
- Cross-lib/reference parity: pass (`0.0pp` CAGR delta).

## Lessons

Lower leverage preserved the broad economic edge versus `SPY` and the diversified
opportunity basket, but the signal was not statistically defensible. DSR degraded
materially versus the `UPRO` sleeve, WF-MCPT remained weak, and bootstrap crossed
zero. The best `SSO` sleeve also failed to beat raw `SSO` buy-and-hold context.

## Next Step

Do not promote or paper trade. The balanced-sleeve family now has two economic
beaters with repeated WF-MCPT/DSR fragility; next Phase 3 work should pivot to a
different Track C mechanism or a pre-registered inception-window sensitivity, not
local weight/rebalance tuning `[testing_tuning, p.327-335]`.
