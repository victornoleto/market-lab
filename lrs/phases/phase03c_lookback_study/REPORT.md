# Phase 3C - Lookback Study (Robustness, Theory Anchor, Gated Adaptive)

Status: research-only. This report does not authorize deployment, paper trading or a mandate change.

Question: *why SMA 200?* The number 200 is community-popular (golden-cross folklore) but unexamined in this restart. We avoid two opposite overfit traps: (a) blindly trusting 200, and (b) sweeping windows and promoting the best. The robustness map is a DIAGNOSTIC and we pre-committed to NOT promoting the argmax `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`. Forms studied: SMA + EMA (Phase 3A-2 did not promote hysteresis). Mechanism unchanged from Phase 3A-2: the trend gate REPLACES the SMA level, `signal = G & vol_gate`, Phase 2 scoring verbatim.

Headline: by the strict pre-registered rule both primary SMA curves are narrow peaks (fragile), so the adaptive gate ran - but the vol-scaled window did NOT beat the fixed window net of turnover, and the empirical optimum (~175-225) is far longer than the vol-persistence anchor (~20-40d).

## Source And Rules

| Item | Value |
|---|---|
| Data | `data/testfolio/cache/history.parquet` (close-only equity curves) |
| Window grid | [50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 350, 400] (13 points) |
| Forms | SMA `[leverage_for_the_long_run, p.13]`, EMA `[systematic_trading, p.283]` |
| Surface read | best-score lag per (form, base, window) cell |
| Plateau rule | contiguous Calmar band within 10% of band-best, width >= 150 days; 200 in band? |
| Theory anchor | squared-return ACF decay half-life ~ GARCH alpha+beta `[volatility_trading, p.39, p.53-54]` |
| Adaptive | gated on fragility; vol-scaled window vs fixed-200 + best-fixed |


## Theory Anchor (ex-ante, no performance peeking)

| Branch | Vol half-life (d) | Return half-life (d) | tau=HL/ln2 (d) | EWMA span | SMA~2*HL | SMA plateau | EWMA in plateau | 2*HL in plateau |
|---|---|---|---|---|---|---|---|---|
| SPY | 10.9 | n/a | 15.7 | 31.5 | 21.8 | 200-225 | no | no |
| QQQ | 14.3 | n/a | 20.7 | 41.4 | 28.7 | 175-225 | no | no |

Return half-life `n/a` means signed daily returns show no positive decaying autocorrelation (near-white) - the trend signal is a price/regime *level* effect, not return persistence `[stocks_on_the_move, p.58, p.60]`. The volatility-persistence half-life and its EWMA-span / 2x-half-life mappings are the citable, non-arbitrary window anchors `[volatility_trading, p.39, p.53-54]`, `[systematic_trading, p.283]`.


## Robustness - primary base (per branch x form)

| Branch | Base | Form | Argmax W | Best Calmar | Plateau band | Width | Has plateau | 200 in band | Fragile |
|---|---|---|---|---|---|---|---|---|---|
| QQQ | qqq_top | EMA | 100 | 0.509 | 100-100 | 0 | no | no | yes |
| QQQ | qqq_top | SMA | 175 | 0.483 | 175-225 | 50 | no | no | yes |
| SPY | spy_top | EMA | 100 | 0.350 | 100-100 | 0 | no | no | yes |
| SPY | spy_top | SMA | 200 | 0.393 | 200-225 | 25 | no | no | yes |

## Robustness - across all bases (robustness of the verdict)

| Branch | Base | Form | Primary | Argmax W | Plateau band | Width | Has plateau | 200 in band | Fragile |
|---|---|---|---|---|---|---|---|---|---|
| QQQ | qqq_top | EMA | yes | 100 | 100-100 | 0 | no | no | yes |
| QQQ | qqq_alt_vol | EMA |  | 100 | 100-100 | 0 | no | no | yes |
| QQQ | qqq_lower_lev | EMA |  | 100 | 100-100 | 0 | no | no | yes |
| QQQ | qqq_top | SMA | yes | 175 | 175-225 | 50 | no | no | yes |
| QQQ | qqq_alt_vol | SMA |  | 175 | 175-225 | 50 | no | no | yes |
| QQQ | qqq_lower_lev | SMA |  | 175 | 175-225 | 50 | no | no | yes |
| SPY | spy_top | EMA | yes | 100 | 100-100 | 0 | no | no | yes |
| SPY | spy_alt_off | EMA |  | 100 | 100-125 | 25 | no | no | yes |
| SPY | spy_lower_lev | EMA |  | 125 | 100-125 | 25 | no | no | yes |
| SPY | spy_top | SMA | yes | 200 | 200-225 | 25 | no | no | yes |
| SPY | spy_alt_off | SMA |  | 200 | 200-225 | 25 | no | no | yes |
| SPY | spy_lower_lev | SMA |  | 200 | 200-225 | 25 | no | no | yes |

## Surface - SPY SMA (primary base spy_top, best lag per window)

| Window | Lag | Tier | CAGR | MDD | Calmar | Terminal/U | Score |
|---|---|---|---|---|---|---|---|
| 50 | 5 | tolerable | 10.45% | -48.39% | 0.216 | 0.94x | 1.344 |
| 75 | 0 | warning | 13.08% | -58.12% | 0.225 | 3.70x | 1.713 |
| 100 | 5 | warning | 12.67% | -54.67% | 0.232 | 3.00x | 1.769 |
| 125 | 5 | warning | 13.82% | -53.07% | 0.260 | 5.39x | 2.260 |
| 150 | 5 | tolerable | 13.39% | -45.68% | 0.293 | 4.34x | 2.950 |
| 175 | 5 | tolerable | 13.36% | -44.17% | 0.302 | 4.27x | 3.140 |
| 200 | 3 | preferred | 15.44% | -39.28% | 0.393 | 12.28x | 3.951 |
| 225 | 2 | preferred | 14.97% | -39.68% | 0.377 | 9.70x | 3.932 |
| 250 | 0 | tolerable | 14.82% | -44.48% | 0.333 | 8.99x | 3.716 |
| 275 | 5 | warning | 14.39% | -58.87% | 0.244 | 7.21x | 2.372 |
| 300 | 5 | warning | 15.11% | -58.87% | 0.257 | 10.37x | 2.511 |
| 350 | 0 | warning | 15.31% | -58.87% | 0.260 | 11.52x | 2.630 |
| 400 | 5 | warning | 13.85% | -58.87% | 0.235 | 5.50x | 2.213 |

## Surface - SPY EMA (primary base spy_top, best lag per window)

| Window | Lag | Tier | CAGR | MDD | Calmar | Terminal/U | Score |
|---|---|---|---|---|---|---|---|
| 50 | 5 | warning | 10.79% | -54.22% | 0.199 | 1.13x | 0.873 |
| 75 | 5 | tolerable | 12.08% | -46.55% | 0.260 | 2.21x | 2.203 |
| 100 | 3 | tolerable | 14.89% | -42.50% | 0.350 | 9.31x | 3.155 |
| 125 | 5 | tolerable | 14.21% | -45.51% | 0.312 | 6.58x | 3.054 |
| 150 | 4 | tolerable | 12.52% | -46.88% | 0.267 | 2.77x | 2.355 |
| 175 | 5 | tolerable | 13.11% | -48.58% | 0.270 | 3.76x | 2.604 |
| 200 | 5 | tolerable | 13.85% | -48.15% | 0.288 | 5.49x | 2.858 |
| 225 | 5 | warning | 14.39% | -51.00% | 0.282 | 7.21x | 2.887 |
| 250 | 5 | warning | 13.96% | -52.87% | 0.264 | 5.81x | 2.699 |
| 275 | 5 | warning | 14.22% | -52.87% | 0.269 | 6.61x | 2.767 |
| 300 | 5 | warning | 13.30% | -58.87% | 0.226 | 4.14x | 2.050 |
| 350 | 5 | warning | 13.34% | -58.87% | 0.227 | 4.24x | 2.052 |
| 400 | 0 | warning | 13.85% | -58.87% | 0.235 | 5.49x | 2.229 |

## Surface - QQQ SMA (primary base qqq_top, best lag per window)

| Window | Lag | Tier | CAGR | MDD | Calmar | Terminal/U | Score |
|---|---|---|---|---|---|---|---|
| 50 | 0 | warning | 17.93% | -50.61% | 0.354 | 3.47x | 2.393 |
| 75 | 0 | tolerable | 19.00% | -47.19% | 0.403 | 4.99x | 3.087 |
| 100 | 3 | tolerable | 17.50% | -41.45% | 0.422 | 2.99x | 2.846 |
| 125 | 3 | tolerable | 17.71% | -46.08% | 0.384 | 3.22x | 2.791 |
| 150 | 0 | tolerable | 18.62% | -46.28% | 0.402 | 4.39x | 3.295 |
| 175 | 0 | tolerable | 20.92% | -43.32% | 0.483 | 9.52x | 4.107 |
| 200 | 0 | tolerable | 19.46% | -42.58% | 0.457 | 5.82x | 3.830 |
| 225 | 5 | tolerable | 20.27% | -42.61% | 0.476 | 7.65x | 3.939 |
| 250 | 5 | warning | 19.19% | -58.37% | 0.329 | 5.31x | 2.295 |
| 275 | 5 | warning | 17.94% | -56.39% | 0.318 | 3.47x | 2.206 |
| 300 | 0 | warning | 18.63% | -59.13% | 0.315 | 4.39x | 2.383 |
| 350 | 0 | warning | 18.37% | -60.05% | 0.306 | 4.02x | 2.413 |
| 400 | 0 | warning | 18.30% | -57.20% | 0.320 | 3.93x | 2.609 |

## Surface - QQQ EMA (primary base qqq_top, best lag per window)

| Window | Lag | Tier | CAGR | MDD | Calmar | Terminal/U | Score |
|---|---|---|---|---|---|---|---|
| 50 | 0 | tolerable | 17.97% | -47.65% | 0.377 | 3.51x | 2.626 |
| 75 | 0 | tolerable | 19.05% | -43.09% | 0.442 | 5.07x | 3.527 |
| 100 | 0 | tolerable | 21.00% | -41.29% | 0.509 | 9.78x | 4.204 |
| 125 | 0 | tolerable | 19.40% | -48.56% | 0.399 | 5.71x | 3.240 |
| 150 | 0 | tolerable | 19.85% | -48.56% | 0.409 | 6.64x | 3.313 |
| 175 | 0 | tolerable | 20.38% | -46.15% | 0.442 | 7.94x | 3.664 |
| 200 | 0 | tolerable | 20.82% | -46.15% | 0.451 | 9.19x | 3.707 |
| 225 | 5 | tolerable | 20.27% | -42.67% | 0.475 | 7.65x | 3.840 |
| 250 | 5 | tolerable | 20.14% | -43.77% | 0.460 | 7.33x | 3.807 |
| 275 | 0 | warning | 19.09% | -51.62% | 0.370 | 5.15x | 3.167 |
| 300 | 0 | warning | 19.32% | -51.45% | 0.375 | 5.56x | 3.122 |
| 350 | 0 | warning | 18.66% | -51.58% | 0.362 | 4.44x | 3.124 |
| 400 | 0 | warning | 17.25% | -55.72% | 0.310 | 2.74x | 2.534 |

## Spin-off cross-check

The spun-off single-asset line (`studies/lrs/`, now canonical in `letf-lab`) swept lookbacks with the exact sweep-and-pick-best method this phase rejects, under different mechanics (single-asset, synthetic LETFs). Its empirical optima (SPY ~250-295, QQQ ~245) and the finding that **200 is the round popular number, not the empirical best**, are shown as plot markers - cross-checked, not inherited `[trading_systems_methods, p.27, p.917-919]`.


## Adaptive Window (Part 3 - triggered by fragility)

| Branch | Variant | Window | Mean W | Lag | CAGR | MDD | Calmar | Lev MDD | Turnover/yr | Score |
|---|---|---|---|---|---|---|---|---|---|---|
| SPY | adaptive-vol | adaptive | 234.5 | 5 | 15.01% | -52.84% | 0.284 | -88.27% | 3.56 | 2.881 |
| SPY | fixed-200 | 200 | 200.0 | 3 | 15.44% | -39.28% | 0.393 | -88.27% | 5.58 | 3.951 |
| SPY | best-fixed | 200 | 200.0 | 3 | 15.44% | -39.28% | 0.393 | -88.27% | 5.58 | 3.951 |
| QQQ | adaptive-vol | adaptive | 162.2 | 5 | 20.13% | -46.18% | 0.436 | -97.82% | 4.90 | 3.538 |
| QQQ | fixed-200 | 200 | 200.0 | 0 | 19.46% | -42.58% | 0.457 | -97.82% | 3.00 | 3.830 |
| QQQ | best-fixed | 175 | 175.0 | 0 | 20.92% | -43.32% | 0.483 | -97.82% | 3.05 | 4.107 |

The vol-scaled window is compared honestly vs fixed-200 and the best-fixed window, net of turnover. The spin-off found lookback-switch cost is amplified by leverage, so any adaptive edge must survive turnover to count `[leverage_for_the_long_run, p.4-7]`.


## Phase Verdict

| Question | Verdict |
|---|---|
| Is SMA200 inside a robust plateau on both branches? | No (SPY band 200-225 width 25, QQQ 175-225 width 50; min plateau width 150). |
| Are all primary-base curves robust (no narrow peak)? | No - fragile by the strict rule. |
| Is there a broad *adequate* region (tolerable+ MDD)? | Yes - ~150-250; long windows collapse (SPY >=275, QQQ >=250). |
| Did the theory anchor land inside the SMA plateau? | No - vol half-life (~11-14d) is far shorter than the empirical window (see theory table). |
| Was the adaptive window warranted / did it help? | No - it worsens MDD/Calmar net of turnover on both branches (the leverage-amplified lookback-switch cost the spin-off warned about). |
| Did we promote the argmax window? | No - pre-committed; the deliverable is the robustness verdict, not the best window. |
| Is this deployment-ready? | No. Diagnostic lookback study only. No deploy, no paper-trade label, no mandate change. |

"Why 200?" - the SMA Calmar surface is NOT a wide flat plateau - by the strict pre-registered rule both branches are fragile, because Calmar peaks fairly sharply near 200/175 and long windows (SPY >=275, QQQ >=250) collapse to ~-59% MDD on the leveraged sleeve (a late regime exit that leverage punishes). Yet within the adequate region (~150-250, tolerable/preferred MDD) 200 is at/near the Calmar-best (SPY argmax 200, QQQ 175/225 tied) and 225 is essentially tied. The gated adaptive vol-window does NOT help - it worsens MDD/Calmar net of turnover on both branches, and the theory anchor (vol half-life ~11-14d -> natural windows ~22-41d) is far shorter than 200 (signed returns are near-white), so 200 is a slow regime/level filter, not a persistence-matched horizon. Net: keep a FIXED window in ~175-225 (200 is a sound default), avoid windows >=250, treat exposure geometry as the real driver, and do NOT adopt adaptivity despite the fragility flag `[leverage_for_the_long_run, p.4-7]`, `[volatility_trading, p.39, p.53-54]`, `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`.
