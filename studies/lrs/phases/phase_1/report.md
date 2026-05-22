# studies/lrs — Phase 1 Report (SMA/EMA × lookback × risk-off sweep)

Generated: 2026-05-22T18:56:54.446059+00:00  ·  sweep: 1552 configs × 2 tax scenarios = 3104 score reports  ·  scoring window: 1980-01-02 → 2026-05-21 (11692 bars)

## Sweep grid

| Dimension | Values |
|---|---|
| Filter | SMA, EMA (2) |
| Lookback | 20..500 step 5 (97 values) |
| Risk-off | CASH, GLD, IEF, ZROZ (4) |
| On-leg | SSO, UPRO (2) |
| Tax scenario | tax_free, br_lei_14754 (2) |
| **Total** | **1552** configs, **× 2** scenarios |

## Heatmaps

Each heatmap shows ``final_score`` over the ``(filter, lookback)`` grid for one 
``(on_leg, tax_scenario)`` cell; one panel per risk-off asset. Star = best 
config within that panel.

### SSO on-leg, tax_free

![heatmap_sso_tax_free.png](plots/heatmap_sso_tax_free.png)

### SSO on-leg, br_lei_14754

![heatmap_sso_br_lei_14754.png](plots/heatmap_sso_br_lei_14754.png)

### UPRO on-leg, tax_free

![heatmap_upro_tax_free.png](plots/heatmap_upro_tax_free.png)

### UPRO on-leg, br_lei_14754

![heatmap_upro_br_lei_14754.png](plots/heatmap_upro_br_lei_14754.png)

## Top-10 per (on_leg × tax_scenario)

### SSO on-leg, tax_free

| # | filter | LB | risk-off | final | 10y | 15y | 20y | %win 20y | switches/y | regime-d | tax drag |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | SMA | 295 | ZROZ | +0.4328 | +0.439 | +0.577 | +0.655 | 100% | 3.8 | 67 | 0.00 |
| 2 | SMA | 290 | ZROZ | +0.4281 | +0.434 | +0.576 | +0.652 | 100% | 3.6 | 70 | 0.00 |
| 3 | EMA | 50 | ZROZ | +0.3910 | +0.404 | +0.593 | +0.643 | 100% | 18.2 | 14 | 0.00 |
| 4 | SMA | 305 | ZROZ | +0.3901 | +0.389 | +0.521 | +0.630 | 100% | 3.5 | 73 | 0.00 |
| 5 | SMA | 300 | ZROZ | +0.3897 | +0.391 | +0.520 | +0.628 | 100% | 3.6 | 70 | 0.00 |
| 6 | SMA | 315 | ZROZ | +0.3878 | +0.379 | +0.514 | +0.627 | 100% | 3.4 | 74 | 0.00 |
| 7 | SMA | 310 | ZROZ | +0.3865 | +0.375 | +0.514 | +0.627 | 100% | 3.5 | 73 | 0.00 |
| 8 | SMA | 285 | ZROZ | +0.3797 | +0.378 | +0.524 | +0.624 | 100% | 3.7 | 68 | 0.00 |
| 9 | SMA | 350 | ZROZ | +0.3644 | +0.364 | +0.495 | +0.609 | 100% | 3.6 | 71 | 0.00 |
| 10 | SMA | 345 | ZROZ | +0.3638 | +0.355 | +0.490 | +0.610 | 100% | 3.3 | 75 | 0.00 |

### SSO on-leg, br_lei_14754

| # | filter | LB | risk-off | final | 10y | 15y | 20y | %win 20y | switches/y | regime-d | tax drag |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | SMA | 295 | ZROZ | +0.3470 | +0.326 | +0.481 | +0.602 | 100% | 3.8 | 67 | 350.07 |
| 2 | SMA | 290 | ZROZ | +0.3395 | +0.317 | +0.474 | +0.597 | 100% | 3.6 | 70 | 342.97 |
| 3 | SMA | 305 | ZROZ | +0.3024 | +0.275 | +0.410 | +0.571 | 100% | 3.5 | 73 | 280.90 |
| 4 | SMA | 300 | ZROZ | +0.3021 | +0.272 | +0.411 | +0.568 | 100% | 3.6 | 70 | 283.85 |
| 5 | SMA | 315 | ZROZ | +0.2993 | +0.272 | +0.400 | +0.570 | 100% | 3.4 | 74 | 285.40 |
| 6 | EMA | 50 | ZROZ | +0.2964 | +0.288 | +0.473 | +0.563 | 99% | 18.2 | 14 | 328.97 |
| 7 | SMA | 310 | ZROZ | +0.2963 | +0.266 | +0.396 | +0.567 | 100% | 3.5 | 73 | 293.93 |
| 8 | SMA | 285 | ZROZ | +0.2909 | +0.262 | +0.413 | +0.562 | 100% | 3.7 | 68 | 235.61 |
| 9 | SMA | 350 | ZROZ | +0.2781 | +0.252 | +0.385 | +0.553 | 97% | 3.6 | 71 | 169.02 |
| 10 | SMA | 355 | ZROZ | +0.2770 | +0.261 | +0.387 | +0.542 | 96% | 3.8 | 67 | 178.11 |

### UPRO on-leg, tax_free

| # | filter | LB | risk-off | final | 10y | 15y | 20y | %win 20y | switches/y | regime-d | tax drag |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | SMA | 295 | ZROZ | +0.4217 | +0.447 | +0.583 | +0.627 | 100% | 3.8 | 67 | 0.00 |
| 2 | SMA | 290 | ZROZ | +0.4202 | +0.441 | +0.584 | +0.627 | 100% | 3.6 | 70 | 0.00 |
| 3 | SMA | 315 | ZROZ | +0.3782 | +0.390 | +0.516 | +0.604 | 100% | 3.4 | 74 | 0.00 |
| 4 | SMA | 300 | ZROZ | +0.3770 | +0.380 | +0.529 | +0.603 | 100% | 3.6 | 70 | 0.00 |
| 5 | SMA | 310 | ZROZ | +0.3766 | +0.384 | +0.513 | +0.604 | 100% | 3.5 | 73 | 0.00 |
| 6 | SMA | 305 | ZROZ | +0.3747 | +0.377 | +0.519 | +0.606 | 100% | 3.5 | 73 | 0.00 |
| 7 | SMA | 285 | ZROZ | +0.3729 | +0.378 | +0.535 | +0.599 | 100% | 3.7 | 68 | 0.00 |
| 8 | SMA | 240 | ZROZ | +0.3642 | +0.379 | +0.516 | +0.575 | 100% | 5.2 | 49 | 0.00 |
| 9 | SMA | 280 | ZROZ | +0.3596 | +0.363 | +0.522 | +0.588 | 100% | 3.9 | 65 | 0.00 |
| 10 | SMA | 220 | ZROZ | +0.3551 | +0.363 | +0.502 | +0.566 | 100% | 5.6 | 45 | 0.00 |

### UPRO on-leg, br_lei_14754

| # | filter | LB | risk-off | final | 10y | 15y | 20y | %win 20y | switches/y | regime-d | tax drag |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | SMA | 295 | ZROZ | +0.3572 | +0.342 | +0.527 | +0.589 | 100% | 3.8 | 67 | 676.68 |
| 2 | SMA | 290 | ZROZ | +0.3558 | +0.339 | +0.526 | +0.590 | 100% | 3.6 | 70 | 684.75 |
| 3 | SMA | 305 | ZROZ | +0.3072 | +0.285 | +0.440 | +0.560 | 100% | 3.5 | 73 | 463.53 |
| 4 | SMA | 300 | ZROZ | +0.3067 | +0.278 | +0.448 | +0.559 | 100% | 3.6 | 70 | 499.21 |
| 5 | SMA | 310 | ZROZ | +0.3057 | +0.283 | +0.433 | +0.559 | 100% | 3.5 | 73 | 484.81 |
| 6 | SMA | 315 | ZROZ | +0.3055 | +0.288 | +0.432 | +0.557 | 100% | 3.4 | 74 | 487.70 |
| 7 | SMA | 285 | ZROZ | +0.3004 | +0.273 | +0.453 | +0.552 | 100% | 3.7 | 68 | 409.48 |
| 8 | SMA | 240 | ZROZ | +0.2973 | +0.300 | +0.442 | +0.510 | 100% | 5.2 | 49 | 982.76 |
| 9 | SMA | 220 | ZROZ | +0.2895 | +0.289 | +0.436 | +0.495 | 100% | 5.6 | 45 | 886.03 |
| 10 | SMA | 280 | ZROZ | +0.2830 | +0.254 | +0.436 | +0.534 | 100% | 3.9 | 65 | 343.53 |

## Headline winners with neighbourhood robustness

Each panel's top config plus a cheap overfit-vs-plateau check: how many of its (filter, lookback ± 25) siblings also score positive.

| Panel | filter | LB | risk-off | final | neighbours | %positive | mean |
|---|---|---:|---|---:|---:|---:|---:|
| SSO · tax_free | SMA | 295 | ZROZ | +0.4328 | 11 | 100% | +0.3700 |
| SSO · br_lei_14754 | SMA | 295 | ZROZ | +0.3470 | 11 | 100% | +0.2795 |
| UPRO · tax_free | SMA | 295 | ZROZ | +0.4217 | 11 | 100% | +0.3597 |
| UPRO · br_lei_14754 | SMA | 295 | ZROZ | +0.3572 | 11 | 100% | +0.2864 |

## Caveats

- **Discovery-only**: the top configs here ARE expected to be overfit to the 1980-2026 regime pattern. No PBO/DSR/walk-forward adjustment was applied. Phase-2 will validate top-N via honest walk-forward + block bootstrap on the regime parameters.
- **No frictions modelled**: zero commission, zero spread, zero slippage. Whipsaw-heavy short-lookback configs will look better here than in production.
- **Pre-1980 SMA warmup buffer** is used for the long lookbacks (up to 300 days). Pre-1980 bars do not enter scores.
- **Synthetic pre-inception data**: SSO/UPRO/GLD pre-2006/2009/2004 are testfol.io modelled series.
- **No FX gain modelling** for USD/BRL; ranks of strategies are preserved because every strategy faces the same FX.

## Files

- [`results/sweep_full.csv`](./results/sweep_full.csv) — all 3104 rows.
- [`results/sweep_top20.csv`](./results/sweep_top20.csv) — top-20 per panel.
- [`results/sweep_summary.json`](./results/sweep_summary.json) — top-5 per panel for quick inspection.
- [`results/manifest.json`](./results/manifest.json) — exact runtime config.
- 4 heatmap PNGs under `plots/`.

## Citations

- SMA / EMA regime signal: `[leverage_for_the_long_run, p.13]`
- 2×/3× leverage tested in paper: `[leverage_for_the_long_run, p.17, Table 8]`
- MA-window sweep: `[leverage_for_the_long_run, p.14, Table 6]`
- Cash off-leg precedent: `[leverage_for_the_long_run, p.21]`
- Lei 14.754/2023 art. 5°/6° (BR 15% annual + indefinite loss carry-forward): https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14754.htm
- Multiple-testing overfit concerns motivating phase-2 honest walk-forward: `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

