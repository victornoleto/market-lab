# Underlying Signal Audit

Status: focused audit requested after noticing that `iter030`, `T20D90` and `T20D120` compute their entry signals on `QLD`, not on the unlevered `QQQ` underlying.

## Verdict

The concern is valid. The iter030 family is **not** a clean Gayed-style LRS rule where regime is measured on the unlevered underlying index. It is a LETF-own-price regime rule: its SMA, realised-vol and AR(1) signals are computed on `QLD`, then the strategy trades `QLD` or `TQQQ`.

When the same three strategies are forced to use `QQQ` as the signal asset while keeping execution in `QLD/TQQQ/ZROZ/CASHX`, performance degrades materially. This means the high long-history metrics are dependent on using the LETF itself as the signal series, not only the unlevered underlying trend thesis `[leverage_for_the_long_run, p.13]`.

## Test Setup

Held constant:

- ON normal leg: `QLD`
- ON turbo leg: `TQQQ`
- OFF normal leg: `ZROZ`
- OFF override: `CASHX` when ZROZ rate-vol gate fires
- Entry vote: `K=2` of four signals
- LRS overlay: `1.20x` on ON days
- OFF override gamma: `0.25`
- Window: `1986-01-03..2026-04-17`

Only changed:

- Signal asset from `QLD` to `QQQ`.

Signal components:

- price > SMA250
- price > SMA100
- realised volatility 21d < 40% annualised
- AR(1) 30d > 0

## Results

| Strategy | Signal asset | Sortino | CAGR | Sharpe | MDD | Calmar | End multiple |
|---|---|---:|---:|---:|---:|---:|---:|
| iter030 T35D60 | QLD | 1.2073 | 36.66% | 0.9624 | -55.48% | 0.6608 | 290,557x |
| iter030 T35D60 | QQQ | 0.9641 | 28.38% | 0.7738 | -91.09% | 0.3116 | 23,479x |
| T20D90 | QLD | 1.2278 | 38.99% | 0.9752 | -55.48% | 0.7029 | 574,998x |
| T20D90 | QQQ | 0.9504 | 29.18% | 0.7704 | -93.72% | 0.3114 | 30,110x |
| T20D120 | QLD | 1.2074 | 39.01% | 0.9606 | -55.48% | 0.7032 | 577,835x |
| T20D120 | QQQ | 0.9642 | 30.22% | 0.7818 | -94.10% | 0.3211 | 41,534x |

## Interpretation

The QQQ-signal variants remain high-CAGR in absolute terms, but their drawdowns become extreme: about `-91%` to `-94%`. That is not an acceptable replacement for the QLD-signal versions under a long-term robustness lens.

This audit changes the conceptual label of the iter030 family:

- It should **not** be described as a pure LRS-underlying-index strategy.
- It should be described as a **LETF self-regime strategy**: the levered ETF's own price/vol/serial-dependence state determines exposure.
- The result may still be economically meaningful, because QLD's own decay, volatility and trend behavior are directly relevant to holding QLD/TQQQ.
- But the mechanism is less clean than the Gayed canonical rule and should carry an extra caveat in any long-term recommendation `[leverage_for_the_long_run, p.5-7]`, `[leverage_for_the_long_run, p.13]`.

## Recommendation Impact

Between the original three QLD-signal variants, the ranking is unchanged:

1. `T20D90` as best economic-first balance.
2. `T20D120` as best performance-first terminal-equity variant.
3. `iter030 canonical` as the least modified anchor.

But the confidence level is lower than if the same metrics survived with `QQQ` as the signal asset. The safest wording is: **best known variant inside the LETF-self-signal family**, not best clean LRS-underlying implementation.

## Command

The audit was run as an inline reproduction using the existing iter030 helpers and replacing only the signal series from `QLDSIM` to `QQQSIM`. No new search or optimization was performed, so this is a diagnostic comparison, not an additional trial grid.
