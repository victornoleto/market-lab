# Factor Sleeve Diagnostics: AVUV / SPMO / VBR / Managed Futures

Status: exploratory diagnostic for possible RSC-US factor sleeves. This is not a portfolio change, not a validation pass, and not deployment authorization `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Execution

Two Testfol.io payloads supplied by the user were executed on 2026-06-05 without `authorization` and with a `sleep 6` delay between calls.

| Request | HTTP | Raw response | Window | Limiting ticker |
|---|---:|---|---|---|
| `factor_backtest_01_realish` | 200 | `raw/factor_backtest_01_realish.json` | 2015-10-12..2026-06-05 | `SPMO` |
| `factor_backtest_02_sims` | 200 | `raw/factor_backtest_02_sims.json` | 2000-01-03..2026-06-05 | `DBMFSIM` |

Saved artifacts:

| File | Purpose |
|---|---|
| `payloads/factor_backtest_01_realish.json` | Sanitized real/inception-constrained request body. |
| `payloads/factor_backtest_02_sims.json` | Sanitized simulated-factor request body. |
| `derived/factor_summary.csv` | Metrics for both backtests plus RSC same-window context. |
| `derived/factor_backtest_01_realish_correlations.csv` | Correlation matrix for the 2015+ panel. |
| `derived/factor_backtest_02_sims_correlations.csv` | Correlation matrix for the 2000+ simulated panel. |

## Backtest 1: Real/Inception-Constrained Panel

Common window: `2015-10-12..2026-06-05`, limited by `SPMO`.

| Portfolio | CAGR | MDD | Sharpe | Calmar | Terminal | Reading |
|---|---:|---:|---:|---:|---:|---|
| SPY | 14.83% | -33.70% | 0.745 | 0.440 | 4.36x | Strong bull/growth-era benchmark. |
| SSO | 23.02% | -59.34% | 0.702 | 0.388 | 9.08x | Higher return, worse risk-adjusted profile. |
| SPMO | 19.25% | -30.93% | 0.875 | 0.622 | 6.52x | Strongest standalone factor ETF in this short sample. |
| SPY + 50 KMLM + 50 DBMF - cash | 17.74% | -28.96% | 0.817 | 0.613 | 5.69x | Capital-efficient SPY + MF stack; good but margin-like. |
| AVUV?FB=VBRSIM | 12.82% | -49.42% | 0.531 | 0.259 | 3.61x | SCV had a poor 2015+ cycle vs large/growth/momentum. |

RSC same-window context from the saved full-equity series, ending `2026-04-17`:

| Portfolio | CAGR | MDD | Sharpe | Calmar | Terminal |
|---|---:|---:|---:|---:|---:|
| SPY | 14.73% | -33.69% | 0.861 | 0.437 | 4.24x |
| B4 original 25/25/25/25 | 13.23% | -24.92% | 0.968 | 0.531 | 3.69x |
| RSC-US 35/40/25 | 15.08% | -21.46% | 1.030 | 0.703 | 4.38x |

Reading: `SPMO` is impressive in the live-ish 2015+ panel, but RSC-US still has the better drawdown-adjusted profile. AVUV/VBR looks weak here, but this is not a structural rejection of SCV. It mostly says that the recent decade was unfavorable to small-cap value relative to large-cap momentum/growth.

## Backtest 2: Simulated Long-History Factor Panel

Common window: `2000-01-03..2026-06-05`, limited by `DBMFSIM`.

| Portfolio | CAGR | MDD | Sharpe | Calmar | Terminal | Reading |
|---|---:|---:|---:|---:|---:|---|
| SPMOSIM | 8.91% | -61.94% | 0.422 | 0.144 | 9.53x | Momentum proxy is not compelling standalone over 2000+. |
| VUGSIM | 8.23% | -60.06% | 0.392 | 0.137 | 8.08x | Similar growth exposure; worse than SPMO and VBR. |
| KMLMSIM | 4.20% | -32.00% | 0.226 | 0.131 | 2.97x | Low return standalone, but useful as a diversifier. |
| DBMFSIM | 6.73% | -20.44% | 0.529 | 0.329 | 5.59x | Best standalone risk-adjusted diversifier in this panel. |
| VBRSIM | 10.54% | -61.94% | 0.476 | 0.170 | 14.12x | Best equity-factor CAGR in the long panel, but with large drawdown. |

RSC same-window context from the saved full-equity series, ending `2026-04-17`:

| Portfolio | CAGR | MDD | Sharpe | Calmar | Terminal |
|---|---:|---:|---:|---:|---:|
| SPY | 8.22% | -55.14% | 0.506 | 0.149 | 7.97x |
| B4 original 25/25/25/25 | 11.91% | -28.14% | 0.870 | 0.423 | 19.25x |
| RSC-US 35/40/25 | 13.36% | -29.94% | 0.903 | 0.446 | 26.99x |

Reading: the long simulated factor panel argues more for SCV than for SPMO. `VBRSIM` beats `SPMOSIM` and `VUGSIM` on CAGR and terminal wealth, but all standalone equity-factor sleeves have severe drawdowns. They are not replacements for the return-stacked diversifiers.

## Correlation Notes

2015+ real-ish panel correlations:

| Pair | Correlation | Reading |
|---|---:|---|
| SPY / SSO | 0.999 | SSO is essentially levered SPY. |
| SPY / SPMO | 0.857 | SPMO is still equity beta-heavy. |
| SPMO / AVUV fallback | 0.625 | Momentum and SCV are meaningfully different in the recent panel. |
| SPY / SPY+MF stack | 0.815 | Managed futures stack diversifies but remains equity-linked. |

2000+ simulated panel correlations:

| Pair | Correlation | Reading |
|---|---:|---|
| SPMOSIM / VUGSIM | 0.902 | Momentum proxy overlaps heavily with growth. |
| SPMOSIM / VBRSIM | 0.765 | Momentum and SCV are less redundant than momentum/growth, but still equity-factor correlated. |
| VUGSIM / VBRSIM | 0.799 | Growth and SCV are not independent enough to count as true diversifiers. |
| DBMFSIM / VBRSIM | 0.034 | DBMF-style MF is a genuine diversifier. |
| KMLMSIM / VBRSIM | -0.229 | KMLM-style MF diversifies equity even if standalone return is weak. |

This matters more than standalone CAGR. SCV and momentum are factor tilts inside the equity sleeve. Managed futures and ZROZ are true cross-asset diversifiers. Factor sleeves can improve the equity component, but they should not be funded carelessly from the MF/duration sleeves `[risk_parity, p.80-81]`.

## Implications For B4-v2 / RSC-US

Current RSC-US `35% GDE / 40% RSST / 25% ZROZ` has approximate exposure:

```text
71.5% US large-cap equity
40.0% managed futures
31.5% gold
25.0% ZROZ
168.0% positive exposure
```

Adding `AVUV` or `SPMO` is not free. It spends fund-weight budget that currently buys embedded leverage through `GDE` or `RSST`, or duration convexity through `ZROZ`. That opportunity cost must be explicit `[systematic_trading, p.185-188]`.

Preferred next tests:

| Candidate | Why test | Main risk | Suggested funding source |
|---|---|---|---|
| `5% AVUV` | Adds SCV factor with modest leverage sacrifice. | Recent SCV underperformance may continue. | Mostly from `GDE`, maybe small from `ZROZ`. |
| `10% AVUV` | Meaningful SCV sleeve. | Larger loss of gold/embedded leverage if funded from `GDE`. | First test `30 GDE / 40 RSST / 20 ZROZ / 10 AVUV`. |
| `5% SPMO` | Tests large-cap momentum as a small equity tilt. | High overlap with growth/large-cap beta; momentum crash risk. | Only from large-cap equity/GDE, not from MF. |
| `5% AVUV + 5% SPMO` | Combines value and momentum factors. | Reduces stack leverage while keeping equity drawdown risk. | Fund from `GDE` first; avoid cutting `RSST`. |

SCV has the better strategic case because the Fama-French framework separates market, size, value, profitability and investment factors `[ml_for_algo_trading, ch.7 p.190-191]`. Momentum is also a legitimate factor, but the simulated `SPMOSIM` result is not strong enough to prioritize it over SCV, and momentum has well-known implementation/cycle risks `[stocks_on_the_move, p.60]`, `[ml_for_algo_trading, ch.4 p.86]`.

## Verdict

Do not add SPMO/FMTM to the core based only on these two backtests. The live-ish SPMO result is strong but starts in 2015, and the 2000+ simulated panel does not confirm a structural advantage over VBR/SCV.

AVUV/SCV deserves the next controlled portfolio-level test. The right question is not whether AVUV beats SPY or SPMO standalone. The right question is whether a small SCV sleeve improves the whole RSC portfolio after paying for the embedded leverage it displaces.

Practical next run: test `5%`, `10%`, and `15%` AVUV/VBR-funded variants, then add a second-stage `SPMO`/`FMTM` overlay only if the SCV sleeve survives the portfolio-level trade-off.

## Portfolio-Level Variant Run

Follow-up run executed on 2026-06-05. Testfol.io does not accept `RSSTSIM` directly (`Invalid ticker RSSTSIM`), so the RSC variants were rebuilt as an **effective exposure proxy**, not as exact ETF wrappers:

```text
GDE  ~= 90% SPY + 90% Gold
RSST ~= 100% SPY + 100% Managed Futures
```

The proxy uses `20% KMLMSIM + 20% DBMFSIM?FB=KMLMSIM` for the 40% managed-futures stack and `CASHX` negative to represent embedded financing. This is useful for relative tests among nearby variants, but it is not identical to owning `GDE` and `RSST` wrappers. Any promoted implementation would need wrapper-level tracking checks and financing/friction analysis `[systematic_trading, p.185-188]`, `[leverage_for_the_long_run, p.21]`.

Artifacts:

| File | Purpose |
|---|---|
| `payloads/rsc_avuv_variants.json` | Initial direct wrapper attempt; failed because `RSSTSIM` is invalid. |
| `raw/rsc_avuv_variants.json` | Error response documenting `Invalid ticker RSSTSIM`. |
| `payloads/rsc_avuv_effective_exposure_variants.json` | Valid effective-exposure AVUV test. |
| `raw/rsc_avuv_effective_exposure_variants.json` | Full response for AVUV variants. |
| `payloads/rsc_avuv_spmo_effective_exposure_variants.json` | Valid effective-exposure SPMO/AVUV+SPMO test. |
| `raw/rsc_avuv_spmo_effective_exposure_variants.json` | Full response for SPMO overlays. |
| `derived/rsc_factor_variant_summary.csv` | Consolidated variant metrics. |

### AVUV Sleeve Test

Common window: `1987-12-31..2026-06-05`, limited by `KMLMSIM`.

| Portfolio | CAGR | MDD | Sharpe | Sortino | Calmar | Terminal | Beta | Corr vs SPY |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 11.52% | -55.14% | 0.530 | 0.751 | 0.209 | 66.0x | 1.000 | 1.000 |
| RSC exposure proxy | 15.11% | -27.47% | 0.827 | 1.186 | 0.550 | 222.8x | 0.593 | 0.726 |
| RSC + 5% AVUV | 15.19% | -28.38% | 0.835 | 1.195 | 0.535 | 229.2x | 0.620 | 0.762 |
| RSC + 10% AVUV | 15.26% | -29.30% | 0.839 | 1.199 | 0.521 | 234.9x | 0.648 | 0.795 |
| RSC + 15% AVUV | 15.33% | -30.22% | 0.838 | 1.195 | 0.507 | 239.8x | 0.676 | 0.824 |

Reading: AVUV adds a small amount of CAGR and terminal wealth, but it monotonically worsens max drawdown, beta and correlation to SPY. Calmar falls as AVUV weight rises. This is a trade-off, not a dominance result.

### SPMO / AVUV+SPMO Overlay Test

Same common window: `1987-12-31..2026-06-05`, limited by `KMLMSIM`. `SPMOSIM` is accepted in this combined payload.

| Portfolio | CAGR | MDD | Sharpe | Sortino | Calmar | Terminal | Beta | Corr vs SPY |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RSC exposure proxy | 15.11% | -27.47% | 0.827 | 1.186 | 0.550 | 222.8x | 0.593 | 0.726 |
| RSC + 5% SPMO | 15.22% | -28.48% | 0.831 | 1.191 | 0.535 | 231.6x | 0.625 | 0.761 |
| RSC + 10% SPMO | 15.33% | -31.08% | 0.832 | 1.191 | 0.493 | 239.9x | 0.656 | 0.793 |
| RSC + 5% AVUV + 5% SPMO | 15.30% | -29.39% | 0.836 | 1.196 | 0.521 | 237.7x | 0.652 | 0.795 |
| RSC + 10% AVUV | 15.26% | -29.30% | 0.839 | 1.199 | 0.521 | 234.9x | 0.648 | 0.795 |

Reading: SPMO behaves similarly to AVUV in this proxy: it improves CAGR/terminal marginally but increases drawdown and equity beta. `5% AVUV + 5% SPMO` is nearly tied with `10% AVUV`, with slightly higher CAGR and terminal wealth but slightly worse drawdown and lower Sharpe/Sortino. The differences are too small to justify adding complexity.

## Portfolio-Level Verdict

No AVUV/SPMO factor variant dominates the RSC exposure proxy.

If optimizing for terminal wealth only, `10% SPMO` or `15% AVUV` look best, but both pay with materially worse drawdown and lower Calmar. If optimizing for Sharpe/Sortino among factor variants, `10% AVUV` is the cleanest small improvement, but it still loses to the baseline on Calmar and maximum drawdown.

Practical verdict: keep `35% GDE / 40% RSST / 25% ZROZ` as the headline core. SCV and momentum are still interesting factor diversifiers, but in this 100% fund-weight design their marginal benefit is not enough to justify reducing embedded return-stack leverage. The best use of this run is as a sensitivity note: factor sleeves can raise expected/realized terminal wealth a little, but they make the portfolio more equity-like.
