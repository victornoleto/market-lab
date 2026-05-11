# Iter 032 — Taxed T3d-K2 Underlying/Risk-On Variants

**Iter:** `032-2026-05-10-taxed-underlying-riskon-variants`
**Phase:** 4 — tax-aware implementation diagnostics
**Primary citation:** `[leverage_for_the_long_run, ch.4-5, p.40-60]`

## Hypothesis

After iter 031 showed that tax-aware comparisons materially compress the gross
iter 030 edge, test whether simpler T3d-K2 variants with different risk-on legs
perform better under the same annual Brazilian tax model.

## Variants

All dynamic strategies pay annual 15% tax on realized net gains. Static
buy-and-hold SPY/NDX benchmarks pay no interim tax because no sale event occurs.

| Variant | Signal Underlying | Risk-on | Risk-off |
|---|---|---|---|
| T3d-K2 annual-tax baseline | QLD/NDX proxy | QLD | ZROZ |
| Iter 30 annual-tax proxy | QLD/NDX proxy | QLD or 80% TQQQ + 20% CASHX turbo | ZROZ |
| T3d-K2 TQQQ | QLD/NDX proxy | TQQQ | ZROZ |
| T3d-K2 SPY/SSO | SPY | SSO | ZROZ |
| T3d-K2 SPY/UPRO | SPY | UPRO | ZROZ |

## Report Requirements

- Compare equity curves.
- Compare benchmark-relative equity against taxed T3d-K2, SPY buy-and-hold and
  NDX/QQQ buy-and-hold.
- Compare rolling 1/3/5/10y win rates and mean end ratios.

## Scope

This is a tax-aware diagnostic, not a deployment decision. Mandate §1 remains
100% Plano C.
