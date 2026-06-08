# Return-Stacked ETF Universe Screen

Status: research-only ETF universe triage for RSC-US. This is not a portfolio change, not a validation pass, and not deployment authorization `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Question

Can any currently visible return-stacked or capital-efficient ETF improve the RSC-US headline core, currently:

```text
35% GDE / 40% RSST / 25% ZROZ
```

The screen is intentionally pragmatic. A fund must either improve the core economic exposures or simplify implementation without sacrificing the RSC thesis: diversified stacked equity, managed futures, gold and long-duration exposure. Testfol.io results are treated as seed diagnostics only, not proof of robustness `[systematic_trading, p.185-188]`, `[advances_fin_ml, p.208-211]`.

## Sources

Public sources checked on 2026-06-05:

| Source | What it contributed |
|---|---|
| Return Stacked official site | `RSST`, `RSIT`, `RSSY`, `RSSX`, `RSBT`, `RSBY`, `RSBA`, `RSSB`, `BTGD`, `ISBG`, `ISSB`; exposures, net assets, inception context. |
| SignalBloom capital-efficiency list | Broad 104-ETF screen with AUM/expense snapshots. Useful for finding liquid names and excluding option-income/single-name leverage clutter. |
| WisdomTree search snippets | `NTSX` efficient core and related Efficient Core family framing. WisdomTree pages returned `403`, so this pass used search snippets plus existing RSC evidence. |
| Simplify CTAP/CTA pages and holdings workbook | `CTAP` as 100% large-cap US equity plus 100% systematic managed futures; CTAP/CTA fee context and CTA TRS financing labels. |
| UPAR/RPAR search snippets | Risk-parity exposure: equities, commodities, Treasuries and TIPS. |
| AlphaStacking MATE page | `MATE` as 100% S&P 500 plus 100% Man-managed trend-following futures, with very short live history. |
| JPMorgan page/search snippets | `JPFP` as a JPMorgan managed-futures plus ETF; page fetched but marketing content was not easily structured. |
| Direxion/SPXP search snippets | `SPXP` as S&P 500 plus managed futures, launched in 2026. |

This is a public-web inventory pass, not a prospectus-level legal review.

## Decision Rules

The screen used four rules:

| Rule | Reason |
|---|---|
| Prefer broad equity beta plus true diversifiers | RSC exists because stacked diversifiers can preserve core beta while adding independent return streams `[risk_parity, p.80-81]`. |
| Prefer managed futures trend over generic carry/income for the crash-hedge sleeve | Trend managed futures are closer to the existing RSC diversifier thesis; carry/yield and option income need separate cycle evidence `[systematic_trading, p.40]`. |
| Penalize tiny AUM, very short history and niche thematic exposures | Testfol.io or live-inception backtests are seed leads only; short histories are not validation `[testing_tuning, p.327-335]`. |
| Do not promote crypto-heavy wrappers to core | Prior RSSX work already limits BTC to optional small exposure; raw BTC history should not be extrapolated as a core assumption `[testing_tuning, p.327-335]`. |

## Universe Triage

The practical universe collapses into a small number of buckets.

| Bucket | Tickers | RSC reading |
|---|---|---|
| Current core | `GDE`, `RSST`, `ZROZ` | Keep. `GDE` and `RSST` are the cleanest liquid stack components; `ZROZ` supplies explicit duration convexity. |
| Direct US equity + managed futures substitutes | `CTAP`, `MATE`, `JPFP`, `SPXP`, `HOLD` | `CTAP` is the only near-term candidate already used as optional manager/process split. `MATE`, `JPFP`, `SPXP` are watchlist items because they are too new. |
| Equity + gold/BTC | `RSSX` | Already tested as optional small enhancement. It does not become headline core because the BTC sleeve needs conservative drift assumptions. |
| Global stock/bond efficient core | `RSSB`, `NTSX`, `NTSI`, `NTSE`, `NTSG`, `NTSD` | Useful for simpler/global variants, not a US-core improvement. They lack the MF/gold combination that drives RSC-US. |
| Risk parity/all-weather | `RPAR`, `UPAR`, `ALLW`, `ASGM` | Good defensive products to monitor, but lower-stack or prepackaged allocation makes them less targeted than the RSC mix. |
| Bond + alternatives stacks | `RSBT`, `RSBY`, `RSBA` | Potential satellites. `RSBT` could simplify bond+MF exposure; `RSBY`/`RSBA` use carry/merger-arb sleeves and need separate evidence. |
| Gold/miner/inflation/income | `GDMN`, `GDT`, `GOLY`, `YGLD`, `SPLS` | Mostly satellites or niche inflation/income products. None replaces the balanced equity/MF/gold/duration RSC core. |
| Crypto/income/option stacks | `BTGD`, `BEGS`, `ISBG`, `ISSB`, `OOSB`, `OOQB`, `WTIB`, `WTIP`, `ISBT` | Reject as core. Crypto-heavy and option-income mechanics add implementation/model risk beyond the RSC objective. |
| Not confirmed in this pass | `ESBG`, `HCMT`, `ISTG`, `ISSG`, `ISST`, `WTLS`, `WDIG`, `ENDW`, `LQPE` | Watchlist only until issuer docs, AUM and exposure mechanics are confirmed. |

Full manual classification: `derived/universe_classification.csv`.

## Testfol.io Availability Screen

Three small Testfol.io payloads were executed without `authorization`, with `sleep 6` between calls. All returned `HTTP 200`.

Artifacts:

| File | Purpose |
|---|---|
| `payloads/live_core_wrappers.json` | `SPY`, `NTSX`, `GDE`, `RSSB`, `RSST`. |
| `payloads/live_alternative_wrappers.json` | `SPY`, `CTAP`, `GDMN`, `RSBT`, `RSSY`. |
| `payloads/live_risk_parity_crypto_wrappers.json` | `SPY`, `RPAR`, `UPAR`, `RSSX`, `BTGD`. |
| `payloads/equity_mf_stack_vs_blend.json` | Support comparison for the Reddit equity+MF post: stacked SPY+MF proxies vs unstacked 50/50 blends. |
| `payloads/equity_mf_5050_stack.json` | Separate payload for the sixth curve because Testfol.io limits requests to 5 portfolios: `100% SPY + 50% KMLM + 50% DBMF - cash`. |
| `raw/*.json` | Raw Testfol.io responses. |
| `derived/live_wrapper_screen.csv` | Extracted common-window metrics. |
| `derived/equity_mf_stack_vs_blend.csv` | Extracted stack-vs-blend metrics. |
| `derived/ctap_trs_cost_snapshot.csv` | CTAP fee/TRS spread snapshot from Simplify pages and the 2026-06-05 holdings workbook. |
| `plots/equity_mf_stack_vs_blend_equity_curves.png` | Equity-curve plot used in the Reddit equity+MF draft. |

Important caveat: each payload uses a common window constrained by the newest ticker in that payload. These numbers confirm ticker availability and rough recent behavior only. They are not long-history evidence and should not be compared directly to the 1988+ RSC series `[testing_tuning, p.327-335]`.

| Payload | Common window | Limiting ticker | Ticker | CAGR | MDD | Calmar |
|---|---|---|---|---:|---:|---:|
| Core wrappers | 2023-12-05..2026-06-05 | `RSSB` | `SPY` | 22.67% | -18.76% | 1.209 |
| Core wrappers | 2023-12-05..2026-06-05 | `RSSB` | `NTSX` | 20.41% | -16.82% | 1.214 |
| Core wrappers | 2023-12-05..2026-06-05 | `RSSB` | `GDE` | 50.94% | -22.66% | 2.247 |
| Core wrappers | 2023-12-05..2026-06-05 | `RSSB` | `RSSB` | 19.79% | -16.18% | 1.223 |
| Core wrappers | 2023-12-05..2026-06-05 | `RSSB` | `RSST` | 23.34% | -30.80% | 0.758 |
| Alternative wrappers | 2025-12-09..2026-06-05 | `CTAP` | `SPY` | 18.44% | -8.88% | 2.076 |
| Alternative wrappers | 2025-12-09..2026-06-05 | `CTAP` | `CTAP` | 40.74% | -9.68% | 4.210 |
| Alternative wrappers | 2025-12-09..2026-06-05 | `CTAP` | `GDMN` | -14.51% | -42.63% | -0.340 |
| Alternative wrappers | 2025-12-09..2026-06-05 | `CTAP` | `RSBT` | 18.23% | -6.03% | 3.025 |
| Alternative wrappers | 2025-12-09..2026-06-05 | `CTAP` | `RSSY` | 69.53% | -4.46% | 15.595 |
| Risk parity/crypto | 2025-05-30..2026-06-05 | `RSSX` | `SPY` | 26.11% | -8.88% | 2.940 |
| Risk parity/crypto | 2025-05-30..2026-06-05 | `RSSX` | `RPAR` | 18.20% | -8.10% | 2.245 |
| Risk parity/crypto | 2025-05-30..2026-06-05 | `RSSX` | `UPAR` | 24.08% | -11.13% | 2.163 |
| Risk parity/crypto | 2025-05-30..2026-06-05 | `RSSX` | `RSSX` | 22.33% | -27.37% | 0.816 |
| Risk parity/crypto | 2025-05-30..2026-06-05 | `RSSX` | `BTGD` | -34.84% | -53.33% | -0.653 |

The recent live screen does not produce a core replacement. It mostly says that `GDE`, `CTAP`, `RSSY` and `RSBT` had strong very recent windows, while `RSSX`/`BTGD` show why crypto-heavy wrappers should not be core-rated off short samples.

### Stack vs Blend Support Check

For the shorter Reddit discussion draft, a separate Testfol.io payload compared rough RSST-style stacked exposure with plain 50/50 equity/managed-futures blends. Testfol.io does not accept `RSSTSIM`, so this is an effective-exposure concept check rather than a product simulation.

Common window: `2000-01-03..2026-06-05`, limited by `DBMFSIM`.

| Portfolio | CAGR | MDD | Calmar | Reading |
|---|---:|---:|---:|---|
| `100% SPY` | 8.33% | -55.14% | 0.151 | Baseline. |
| `100% SPY + 100% KMLM - cash` | 11.89% | -57.83% | 0.206 | Higher return, but no drawdown improvement in this proxy. |
| `50% SPY / 50% KMLM` | 7.20% | -29.99% | 0.240 | Much lower drawdown, lower CAGR. |
| `100% SPY + 100% DBMF - cash` | 13.59% | -44.64% | 0.304 | Best stacked result in this quick check. |
| `50% SPY / 50% DBMF` | 8.11% | -23.21% | 0.349 | Best drawdown/Calmar, but less growth than stacked exposure. |
| `100% SPY + 50% KMLM + 50% DBMF - cash` | 12.93% | -44.46% | 0.291 | Mixed MF stack; diversifies the MF sleeve but trails the DBMF-only stack in this proxy. |

The useful framing is not that stacked exposure is always better. The 50/50 blends are safer and have better Calmar in the DBMF case. The reason equity+MF stacks are still interesting is that they preserve far more equity participation while adding the diversifier. The implementation question is whether the overlay earns enough after financing, fees and tracking error `[systematic_trading, p.185-188]`, `[leverage_for_the_long_run, p.21]`.

Plot: `plots/equity_mf_stack_vs_blend_equity_curves.png`.

### CTAP Fee And Swap-Cost Note

A follow-up check looked at Simplify's CTAP/CTA public pages plus the Simplify holdings workbook downloaded on 2026-06-05. The main conclusion is that `CTAP` should not be evaluated only by its headline wrapper expense ratio. The managed-futures overlay is implemented through CTA total-return swaps, so the visible economic cost stack includes the wrapper fee, the embedded `CTA` fund fee and the TRS spread over SOFR. Financing/friction realism is central for leveraged or stacked products `[systematic_trading, p.185-188]`, and LETF/stacked implementations can lose material return to expense, tracking and financing drag `[leverage_for_the_long_run, p.21]`.

| Component | Estimate | Reading |
|---|---:|---|
| CTAP wrapper expense ratio | 0.10% current net / 0.28% gross | Waiver-dependent headline fund fee. |
| Embedded CTA expense ratio | 0.75% | Economic drag inside the CTA exposure referenced by the CTAP swaps. |
| CTA TRS spread over SOFR | ~94.5 bps | Market-exposure-weighted across 21 positive CTA TRS rows labeled `SOFR +75/+90/+99/+100`. |
| Simple visible non-SOFR drag | ~1.80% current net / ~1.98% gross | Sum of the three rows above; not an official total expense ratio and excludes SOFR base/collateral-yield mechanics, taxes and tracking slippage. |

This supports the Reddit critique directionally: `CTAP` is a clean implementation, but it is not a low-fee implementation. The DIY alternative of `CTA + SPXL` is not a clean apples-to-apples replacement either. `33% SPXL + 100% CTA` requires more than 100% capital unless the account also uses leverage, while `33% SPXL + 67% CTA` fits in 100% capital but gives only 67% CTA exposure. `SPXL` also adds daily-reset path dependency, its own expense/embedded financing costs and different tax mechanics. Therefore, `CTAP` remains useful as a possible manager/process split with `RSST`, not because it clearly wins on fee efficiency.

## Candidate Ranking

| Priority | Candidate | Verdict | Reason |
|---:|---|---|---|
| 1 | Keep `35% GDE / 40% RSST / 25% ZROZ` | Core headline unchanged | It still has the cleanest long-history evidence, simple exposure map and implementable wrappers. |
| 2 | `35 GDE / 20 RSST / 20 CTAP / 25 ZROZ` | Optional implementation refinement | Same broad exposure as core with managed-futures manager/process diversification. Not a fee-improvement claim; CTAP's visible cost stack is materially higher than the wrapper ER alone. |
| 3 | Small `RSSX` sleeve replacing part of `GDE` | Optional BTC-convexity satellite | Prior RSSX proxy improves post-2010 metrics under conservative BTC assumptions, but it is a BTC expression, not a required core component. |
| 4 | `MATE`, `JPFP`, `SPXP` | Watchlist | They are relevant RSST/CTAP-like products but are too new for core use. Revisit after AUM/history develop. |
| 5 | `RSSB`, `RSIT`, `NTSX/NTSI/NTSE/NTSG/NTSD` | Global/simplification candidates | Better for RSC-Global or a simpler balanced portfolio than for improving RSC-US. |
| 6 | `RSBT`, `RSBY`, `RSBA`, `UPAR/RPAR` | Satellite/watchlist | Interesting diversifiers, but no evidence here that they improve the RSC equity/MF/gold/duration balance. |
| 7 | Crypto, income/options, single-name leverage, niche commodity wrappers | Reject as core | Too narrow, too short-history, too income-mechanics-dependent, or too crypto-heavy for the RSC core objective. |

## Verdict

No newly found ETF replaces RSC-US `35% GDE / 40% RSST / 25% ZROZ` as the headline core.

The only actionable near-term refinement remains the already documented managed-futures split, `35% GDE / 20% RSST / 20% CTAP / 25% ZROZ`, if implementation wants manager diversification. That split is a diversification/process argument, not a cost argument: CTAP's simplified visible non-SOFR drag is roughly `1.80%` current net / `1.98%` gross before taxes, tracking and exact collateral mechanics. `RSSX` remains an optional small BTC-convexity sleeve, not the default. Newer equity+managed-futures wrappers such as `MATE`, `JPFP` and `SPXP` are useful watchlist additions, but not enough to change the core today.

No mandate allocation changes. No public deployment implication. Any future promotion would still require wrapper-level tracking, financing/friction analysis and the repository's robustness gates `[systematic_trading, p.185-188]`, `[leverage_for_the_long_run, p.21]`, `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
