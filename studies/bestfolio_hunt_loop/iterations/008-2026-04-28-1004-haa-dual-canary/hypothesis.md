# Hypothesis — Iter 008 HAA Dual Canary

## Hypothesis

Keep iter 009 HAA+Gold assets unchanged and alter only the binary HAA
risk-on/risk-off trigger. A second broad-equity canary (`VTISIM`) may reduce
false defensive states that the emerging-market canary (`VWOSIM`) creates,
while preserving HAA's simple monthly momentum ranking and the fixed 10%
`KMLMSIM` + 5% `GLDSIM` sleeves `[stocks_on_the_move, ch.6]`.

## Primary Citation

Clenow's momentum framework uses a market regime filter because momentum
portfolios break down in broad bear markets and correlations rise toward one
`[stocks_on_the_move, p.63-65]`. The HAA monthly relative/absolute momentum
architecture remains the strategy shell here `[stocks_on_the_move, ch.6]`.

## Edge Source

Iter 009 HAA+Gold may miss risk-on periods when `VWOSIM` is weak but broad US
equity (`VTISIM`) remains healthy; dual-canary timing attempts to avoid that
false-defensive Sharpe drag without changing the offensive or defensive
assets.

## Datasets

- `educational`: VTSIM synthetic global window, 1995-01-01 to 2026-04-24.
- `vt_real`: VTSIM proxy for live VT, 2008-06-01 to 2026-04-24.
- `ndx_real`: QQQSIM stretch window, 2010-02-01 to 2026-04-24.

## Pre-Committed Kill Criteria

Kill if the selected educational net Sharpe is `<= 1.120`, or if zero
datasets beat iter 009 HAA+Gold by at least `+0.10` Sharpe. Also kill any
candidate whose real-data MDD exceeds iter 009 MDD by more than 5pp.

## Expected Budget

- Configs: 4 canary modes (`vwo_only`, `vti_only`, `either_vwo_vti`,
  `both_vwo_vti`).
- Wall-time: under 20 minutes using existing loop-local simulator and
  validation battery.
- Tax: `AnnualDarfEngine` only, annual DARF settlement under Lei 14.754/2023.

## Implementation Plan

1. Reuse iter 007 HAA simulator, data loaders, metrics, PBO, DSR,
   walk-forward, bootstrap, and numpy cross-lib reference.
2. Replace only the canary decision in `monthly_weights` and
   `simulate_numpy`; keep offensive assets `NTSXSIM/NTSI/NTSE/GDESIM`,
   defensive assets `IEFSIM/BNDSIM/CASHX`, and fixed sleeves unchanged.
3. Select config by maximum mean Sharpe divided by iter 009 Sharpe across all
   three datasets.
4. Save `results.json`, `verdict.json`, plots, final report, and memory
   updates.
