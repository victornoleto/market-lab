# B4-v2 Closing Summary

Status: concluded as a research-only robustness/publication package. This does not authorize deployment, paper trading or mandate changes.

## Final Verdict

The best B4-v2 expression is the simple US no-margin core:

| Sleeve | Weight |
|---|---:|
| GDE | 35% |
| RSST | 40% |
| ZROZ | 25% |

Conclusion: `35% GDE / 40% RSST / 25% ZROZ` is a strong long-horizon drawdown-efficient SPY challenger, but not a guaranteed modern-window CAGR maximizer. It is best described as a defensive return-stacked core, not as a pure replacement for SPY when the only objective is maximum return.

## Evidence Summary

- Full-history US result: B4-v2 `35/40/25` achieved `15.65%` CAGR versus SPY `11.35%`, with MDD `-29.94%` versus SPY `-55.14%`.
- Modern-window caveat: after 2010, the CAGR edge narrows materially and can disappear for some start dates, while drawdown remains better.
- Regime behavior: the strategy performs best as crisis dampening across dot-com, GFC, Covid and the 2022 rates shock, but can lag in strong equity recoveries.
- Fee/drag stress: the US core remains ahead of SPY under the tested extra-drag levels, though the edge compresses.
- Monte Carlo sequence-risk diagnostic supports lower downside terminal wealth risk than SPY, but it remains a diagnostic simulation rather than a proof of future superiority.

## Non-Lead Variants

- `CTAP` and `RSSX` variants are implementation candidates only. They improve some post-2010 terminal-wealth diagnostics, but add assumption sensitivity.
- Global variants are diversification variants. They improve drawdown versus `66/34 VTI/VEA` and `100% VT`, but do not replace the US core on return.

## Open Data Blockers

The following exact checks remain blocked by available artifacts, not by a negative result:

- Rebalance frequency: monthly versus quarterly/semiannual/annual.
- Remove-one-sleeve attribution.
- Rebalance threshold/tolerance-band behavior.

These require a canonical sleeve-level daily return matrix for `GDE`, `RSST`, `ZROZ`, `CTAP`, `RSSX_RP`, `NTSD`, `RSIT`, `NTSI`, `VTI`, `VEA` and `VT`.

## Final Research State

B4-v2 is closed as a documented research package. The next separate research question is whether a SPY/SSO/UPRO-based static or low-turnover strategy can beat SPY with a high rolling hit rate while controlling drawdowns. Robustness interpretation follows rolling-window and multiple-testing cautions `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`; LETF exposure/decay caveats follow `[leverage_for_the_long_run, p.13]`.
