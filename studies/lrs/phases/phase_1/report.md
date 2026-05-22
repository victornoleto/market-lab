# studies/lrs — Phase 1 Report (SMA/EMA × lookback × risk-off sweep)

Generated: 2026-05-22T18:40:39.991469+00:00  ·  sweep: 912 configs × 2 tax scenarios = 1824 score reports  ·  scoring window: 1980-01-02 → 2026-05-21 (11692 bars)

## Sweep grid

| Dimension | Values |
|---|---|
| Filter | SMA, EMA (2) |
| Lookback | 20..300 step 5 (57 values) |
| Risk-off | CASH, GLD, IEF, ZROZ (4) |
| On-leg | SSO, UPRO (2) |
| Tax scenario | tax_free, br_lei_14754 (2) |
| **Total** | **912** configs, **× 2** scenarios |

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

| # | filter | lookback | risk-off | final | 10y len | 15y len | 20y len | %win 20y | switches | tax events | tax drag |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | SMA | 295 | ZROZ | +0.4328 | +0.439 | +0.577 | +0.655 | 100% | 175 | 0 | 0.00 |
| 2 | SMA | 290 | ZROZ | +0.4281 | +0.434 | +0.576 | +0.652 | 100% | 167 | 0 | 0.00 |
| 3 | EMA | 50 | ZROZ | +0.3910 | +0.404 | +0.593 | +0.643 | 100% | 845 | 0 | 0.00 |
| 4 | SMA | 300 | ZROZ | +0.3897 | +0.391 | +0.520 | +0.628 | 100% | 167 | 0 | 0.00 |
| 5 | SMA | 285 | ZROZ | +0.3797 | +0.378 | +0.524 | +0.624 | 100% | 173 | 0 | 0.00 |
| 6 | SMA | 280 | ZROZ | +0.3620 | +0.359 | +0.506 | +0.612 | 100% | 179 | 0 | 0.00 |
| 7 | EMA | 55 | ZROZ | +0.3610 | +0.347 | +0.555 | +0.638 | 100% | 803 | 0 | 0.00 |
| 8 | SMA | 220 | ZROZ | +0.3455 | +0.338 | +0.486 | +0.579 | 100% | 261 | 0 | 0.00 |
| 9 | SMA | 240 | ZROZ | +0.3453 | +0.344 | +0.485 | +0.575 | 100% | 239 | 0 | 0.00 |
| 10 | EMA | 110 | ZROZ | +0.3398 | +0.310 | +0.511 | +0.587 | 100% | 479 | 0 | 0.00 |

### SSO on-leg, br_lei_14754

| # | filter | lookback | risk-off | final | 10y len | 15y len | 20y len | %win 20y | switches | tax events | tax drag |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | SMA | 295 | ZROZ | +0.3470 | +0.326 | +0.481 | +0.602 | 100% | 175 | 33 | 350.07 |
| 2 | SMA | 290 | ZROZ | +0.3395 | +0.317 | +0.474 | +0.597 | 100% | 167 | 33 | 342.97 |
| 3 | SMA | 300 | ZROZ | +0.3021 | +0.272 | +0.411 | +0.568 | 100% | 167 | 32 | 283.85 |
| 4 | EMA | 50 | ZROZ | +0.2964 | +0.288 | +0.473 | +0.563 | 99% | 845 | 47 | 328.97 |
| 5 | SMA | 285 | ZROZ | +0.2909 | +0.262 | +0.413 | +0.562 | 100% | 173 | 33 | 235.61 |
| 6 | SMA | 280 | ZROZ | +0.2693 | +0.237 | +0.391 | +0.545 | 100% | 179 | 34 | 199.03 |
| 7 | SMA | 240 | ZROZ | +0.2552 | +0.240 | +0.389 | +0.481 | 94% | 239 | 37 | 363.69 |
| 8 | EMA | 55 | ZROZ | +0.2521 | +0.195 | +0.421 | +0.539 | 98% | 803 | 47 | 331.93 |
| 9 | SMA | 220 | ZROZ | +0.2520 | +0.237 | +0.385 | +0.478 | 92% | 261 | 37 | 301.19 |
| 10 | EMA | 275 | ZROZ | +0.2511 | +0.212 | +0.319 | +0.511 | 86% | 239 | 39 | 261.97 |

### UPRO on-leg, tax_free

| # | filter | lookback | risk-off | final | 10y len | 15y len | 20y len | %win 20y | switches | tax events | tax drag |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | SMA | 295 | ZROZ | +0.4217 | +0.447 | +0.583 | +0.627 | 100% | 175 | 0 | 0.00 |
| 2 | SMA | 290 | ZROZ | +0.4202 | +0.441 | +0.584 | +0.627 | 100% | 167 | 0 | 0.00 |
| 3 | SMA | 300 | ZROZ | +0.3770 | +0.380 | +0.529 | +0.603 | 100% | 167 | 0 | 0.00 |
| 4 | SMA | 285 | ZROZ | +0.3729 | +0.378 | +0.535 | +0.599 | 100% | 173 | 0 | 0.00 |
| 5 | SMA | 240 | ZROZ | +0.3642 | +0.379 | +0.516 | +0.575 | 100% | 239 | 0 | 0.00 |
| 6 | SMA | 280 | ZROZ | +0.3596 | +0.363 | +0.522 | +0.588 | 100% | 179 | 0 | 0.00 |
| 7 | SMA | 220 | ZROZ | +0.3551 | +0.363 | +0.502 | +0.566 | 100% | 261 | 0 | 0.00 |
| 8 | EMA | 50 | ZROZ | +0.3412 | +0.314 | +0.532 | +0.593 | 100% | 845 | 0 | 0.00 |
| 9 | SMA | 240 | IEF | +0.3410 | +0.356 | +0.483 | +0.555 | 100% | 239 | 0 | 0.00 |
| 10 | SMA | 220 | IEF | +0.3378 | +0.352 | +0.481 | +0.547 | 100% | 261 | 0 | 0.00 |

### UPRO on-leg, br_lei_14754

| # | filter | lookback | risk-off | final | 10y len | 15y len | 20y len | %win 20y | switches | tax events | tax drag |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | SMA | 295 | ZROZ | +0.3572 | +0.342 | +0.527 | +0.589 | 100% | 175 | 33 | 676.68 |
| 2 | SMA | 290 | ZROZ | +0.3558 | +0.339 | +0.526 | +0.590 | 100% | 167 | 33 | 684.75 |
| 3 | SMA | 300 | ZROZ | +0.3067 | +0.278 | +0.448 | +0.559 | 100% | 167 | 35 | 499.21 |
| 4 | SMA | 285 | ZROZ | +0.3004 | +0.273 | +0.453 | +0.552 | 100% | 173 | 36 | 409.48 |
| 5 | SMA | 240 | ZROZ | +0.2973 | +0.300 | +0.442 | +0.510 | 100% | 239 | 37 | 982.76 |
| 6 | SMA | 220 | ZROZ | +0.2895 | +0.289 | +0.436 | +0.495 | 100% | 261 | 38 | 886.03 |
| 7 | SMA | 280 | ZROZ | +0.2830 | +0.254 | +0.436 | +0.534 | 100% | 179 | 37 | 343.53 |
| 8 | EMA | 275 | ZROZ | +0.2763 | +0.252 | +0.364 | +0.536 | 88% | 239 | 39 | 522.03 |
| 9 | EMA | 270 | ZROZ | +0.2720 | +0.245 | +0.364 | +0.532 | 88% | 239 | 40 | 529.23 |
| 10 | SMA | 240 | IEF | +0.2664 | +0.269 | +0.397 | +0.485 | 100% | 239 | 39 | 322.23 |

## Headline winners with neighbourhood robustness

Each panel's top config plus a cheap overfit-vs-plateau check: how many of its (filter, lookback ± 25) siblings also score positive.

| Panel | filter | LB | risk-off | final | neighbours | %positive | mean |
|---|---|---:|---|---:|---:|---:|---:|
| SSO · tax_free | SMA | 295 | ZROZ | +0.4328 | 7 | 100% | +0.3660 |
| SSO · br_lei_14754 | SMA | 295 | ZROZ | +0.3470 | 7 | 100% | +0.2751 |
| UPRO · tax_free | SMA | 295 | ZROZ | +0.4217 | 7 | 100% | +0.3563 |
| UPRO · br_lei_14754 | SMA | 295 | ZROZ | +0.3572 | 7 | 100% | +0.2821 |

## Caveats

- **Discovery-only**: the top configs here ARE expected to be overfit to the 1980-2026 regime pattern. No PBO/DSR/walk-forward adjustment was applied. Phase-2 will validate top-N via honest walk-forward + block bootstrap on the regime parameters.
- **No frictions modelled**: zero commission, zero spread, zero slippage. Whipsaw-heavy short-lookback configs will look better here than in production.
- **Pre-1980 SMA warmup buffer** is used for the long lookbacks (up to 300 days). Pre-1980 bars do not enter scores.
- **Synthetic pre-inception data**: SSO/UPRO/GLD pre-2006/2009/2004 are testfol.io modelled series.
- **No FX gain modelling** for USD/BRL; ranks of strategies are preserved because every strategy faces the same FX.

## Files

- [`results/sweep_full.csv`](./results/sweep_full.csv) — all 1824 rows.
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

