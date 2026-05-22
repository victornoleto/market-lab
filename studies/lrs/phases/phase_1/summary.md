# studies/lrs Phase 1 — Summary

> Curated narrative of phase-1 findings.
> Companion to the auto-generated [`report.md`](./report.md) (data view)
> and [`../../SPEC.md`](../../SPEC.md) (methodology).

## TL;DR

- **Off-leg dominates everything.** Across 912 configurations the choice
  of risk-off asset matters far more than the choice of filter (SMA/EMA)
  or the choice of lookback. Mean final-score by off-leg, averaged across
  all lookbacks: **ZROZ ≫ IEF > GLD > CASH**.
- **ZROZ wins all four panels, comfortably.** Best config across the
  board: `SMA295 / ZROZ`. Final scores +0.43 (tax-free) / +0.35 (taxed)
  — vs phase-0's CASH-only winner at +0.12 / +0.02.
- **CASH is the worst off-leg.** Phase-0's default leaves most of the
  edge on the table: only 6–39% of CASH configs beat B&H SPY, vs
  77–95% of ZROZ configs.
- **Long lookbacks beat short lookbacks consistently.** The 200-day
  Gayed canonical sits in the middle of a positive plateau; the global
  maxima sit at 290–300 days. Short lookbacks (20–60) are universally
  bad, especially with CASH off-leg.
- **SMA beats EMA on most cells.** EMA's faster response generates more
  whipsaws, particularly at short lookbacks. The gap closes at long
  lookbacks (200+).
- The 100% win-rate on 20-year rolling windows for the top configs is
  striking — but this is **discovery-only** under mandate §1, and 912
  configurations is significant multiple-testing exposure. Phase-2
  must validate via honest walk-forward + block bootstrap before any
  edge claim is taken seriously.

## What was tested

The full grid:

| Dimension | Values |
|---|---|
| Filter | SMA, EMA (2) |
| Lookback | 20, 25, 30, …, 300 (57 values, step 5) |
| Risk-off | CASH (0%), GLD (GLDSIM), IEF (IEFSIM), ZROZ (ZROZSIM) (4) |
| On-leg | SSO (2× S&P), UPRO (3× S&P) (2) |
| Tax scenario | tax_free + br_lei_14754 (2) |
| **Total** | **2 × 57 × 4 × 2 = 912 configs × 2 scenarios = 1,824 reports** |

Same scoring framework as phase-0: rolling windows {1, 3, 5, 10, 15, 20}y
at monthly step; within-window composite `0.40·tanh(terminal_excess) +
0.25·time_above + 0.20·tanh(sortino_excess) + 0.15·tanh(calmar_excess)`;
per-length aggregation `0.60·mean + 0.40·p25`; across-length weights
`{1y:5%, 3y:10%, 5y:15%, 10y:20%, 15y:25%, 20y:25%}`. Benchmark = B&H SPY
(tax-free). Scoring window: **1980-01-02 → 2026-05-21** (~46 years).

Tax simulator extended to support non-cash off-legs: when transitioning
off→on, the off-leg lot is realised (positive or negative gain on the
held risk-off asset). For cash off-leg, this realisation is skipped
to preserve the BR external-cash tax-payment interpretation.

## Headline results

**Top-3 per panel:**

| Panel | #1 | #2 | #3 |
|---|---|---|---|
| SSO · tax_free | SMA295/ZROZ +0.4328 | SMA290/ZROZ +0.4281 | EMA50/ZROZ +0.3910 |
| SSO · br_lei_14754 | SMA295/ZROZ +0.3470 | SMA290/ZROZ +0.3395 | SMA300/ZROZ +0.3021 |
| UPRO · tax_free | SMA295/ZROZ +0.4217 | SMA290/ZROZ +0.4202 | SMA300/ZROZ +0.3770 |
| UPRO · br_lei_14754 | SMA295/ZROZ +0.3572 | SMA290/ZROZ +0.3558 | SMA300/ZROZ +0.3067 |

Three observations from this table:

1. **The top of every panel is dominated by `SMA290-300 / ZROZ`.** This is
   the same family of configs winning under every (on-leg × tax) combo.
2. **The top three configs are all neighbours.** SMA290, SMA295, SMA300
   — adjacent grid points with adjacent scores. This is the parameter-
   plateau signature: when a config wins because of luck, its neighbours
   usually don't. When a config wins because it's on a robust edge, its
   neighbours score similarly. The top three for every panel pass this
   smoke test.
3. **EMA50/ZROZ shows up at rank #3 in SSO tax-free** — the only EMA
   variant in the top-12. EMA's faster response apparently helps when the
   off-leg is ZROZ (which itself has fast moves on rate shocks). But the
   same EMA50 generates 845 switches over 46 years (vs 175 for SMA295),
   which would punish it badly with realistic frictions in phase-2.

## Off-leg analysis — the big finding

Averaging final_score across all 114 (filter × lookback) combinations
per panel:

| Off-leg | SSO·free | SSO·tax | UPRO·free | UPRO·tax | %win SSO·free |
|---|---:|---:|---:|---:|---:|
| **ZROZ** | **+0.219** | **+0.118** | **+0.177** | **+0.098** | **95%** |
| IEF      | +0.078 | -0.038 | +0.054 | -0.025 | 67% |
| GLD      | -0.062 | -0.159 | -0.042 | -0.109 | 46% |
| CASH     | -0.133 | -0.228 | -0.103 | -0.168 | 32% |

Reading this table:

- **ZROZ is in a class by itself.** Even random parameter picks within
  ZROZ off-leg score on average +0.22 (tax-free) — better than the *best*
  CASH config across the entire grid.
- **IEF is the natural alternative.** Less duration risk than ZROZ; still
  positive on average in the tax-free world, marginally negative under
  tax. A reasonable fallback if a future operational concern (e.g. 2022
  rate-shock magnitude on ZROZ) makes the long-duration risk unacceptable.
- **GLD is mediocre.** Despite gold's reputation as a flight-to-safety
  asset, the modern-era pattern doesn't favor it as an LRS off-leg.
  Likely because gold's macro driver is different from the SMA200 regime
  signal — they don't synchronize.
- **CASH is the bottom.** Phase-0's default was the worst choice on the
  menu. The reason: cash earns 0% during OFF periods, while ZROZ/IEF
  earn coupon yields plus capital appreciation when rates fall. Cash
  off-leg means the strategy is essentially "leveraged equity OR sitting
  out" — and "sitting out" is expensive in a 5% Treasury-yield world.

## Filter analysis — SMA modestly beats EMA

From the heatmaps:

- **At long lookbacks (200+)**, SMA and EMA cells are similar shades.
  The signal is dominated by the lookback length, not the filter shape.
- **At medium lookbacks (60–180)**, SMA is consistently bluer than EMA.
  EMA's faster response generates more false breaks here.
- **At short lookbacks (20–60)**, both are deep red but EMA is slightly
  worse. The fast EMA is in pure-whipsaw territory.

For phase-2 narrowing: drop EMA from the next iteration unless a specific
mechanistic argument resurfaces. The grid is essentially "SMA-on-the-long-side".

## Lookback analysis — the plateau is at 200–300

Looking at the heatmaps' colour gradient along the lookback axis:

- **Lookbacks 20–80**: deep red across most off-legs. Whipsaw zone.
- **Lookbacks 100–180**: variable. CASH still negative; ZROZ already
  positive but not peaked.
- **Lookbacks 200–250**: solid positive across ZROZ and IEF; Gayed's
  canonical 200 sits comfortably in this band.
- **Lookbacks 270–300**: the global maxima for ZROZ. Slightly longer
  than canonical Gayed. Likely captures more genuine regime changes
  while filtering out monthly-scale noise.

The 200-day canonical is **not** the best lookback found, but it's a
robust pick — score is positive across all four off-legs at SMA200,
and it sits on a wide plateau. Phase-2's walk-forward should not be
allowed to data-mine for SMA295 specifically.

## Tax friction analysis

Tax cost (tax-free minus taxed) by panel winner:

| Panel | Tax-free | Taxed | Δ (tax cost) |
|---|---:|---:|---:|
| SSO·SMA295/ZROZ | +0.4328 | +0.3470 | −0.0858 |
| UPRO·SMA295/ZROZ | +0.4217 | +0.3572 | −0.0645 |

Tax cost is meaningful (-0.07 to -0.09 score units) but **smaller as a
fraction of the total score** than in phase-0:

- Phase-0 LRS-SSO (CASH off-leg): tax cost was -0.145, on a base of +0.082
  → **tax destroyed nearly all the edge**.
- Phase-1 SMA295/ZROZ (best config): tax cost is -0.09, on a base of +0.43
  → **tax leaves 80% of the edge intact**.

ZROZ's higher absolute edge means the same proportional tax has less
impact on rankings. This is a major shift from phase-0's "tax kills the
strategy" verdict — with the right off-leg, the strategy survives the
BR tax model meaningfully positive.

## Worst configs (sanity check)

The five worst configs across all panels are short-lookback CASH
rotations:

- `SMA40 / CASH` on SSO: final −0.54 (937 switches over 46 years ≈ 20/year)
- `SMA20 / CASH` on UPRO: final −0.53 (1,353 switches ≈ 29/year)

These configs are pure whipsaw machines: short lookback fires false
regime changes every few weeks, and CASH off-leg earns nothing during
the off periods. The realised loss is paid every year as tax. Worst
of all worlds. Correctly identified as such by the score.

## Discovery-only caveat (read this before quoting any number)

912 configurations is significant multiple-testing exposure. Some of
the apparent edge in the top configs IS noise. Specifically:

- The framework as it stands has **no PBO/DSR adjustment**. The reported
  final_scores are raw. Real edge after multiple-testing correction will
  be lower.
- The 1980–2026 window is a single sample path. The fact that ZROZ
  worked over this 46-year span is partly a function of the secular
  bond bull market 1982–2020. Phase-2 must check whether the edge
  survives sub-periods.
- The neighbour-plateau check (SMA290/295/300 all winning together) IS
  evidence against pure luck, but doesn't substitute for a formal
  walk-forward.
- Switching costs and slippage are NOT modelled. EMA50/ZROZ with 845
  switches looks great at zero commission; at 5 bps/switch it would
  give back ~4.2% in trading costs total. Realistic frictions would
  reshuffle the ranking in favor of low-switch configs.

For these reasons phase-1's verdict is **"these are the candidates
worth validating", not "these are the deploy choices."**

## Implications for phase-2

Concrete next steps:

1. **Walk-forward** the top-20 per panel. The simplest version: 5y
   training / 5y test, rolled forward in 1y increments, ~7 folds over
   1980-2026. Strategies whose in-sample winner isn't a winner on the
   majority of out-of-sample folds drop out.
2. **Block bootstrap** the rolling-window scores on the SMA290–300 /
   ZROZ family to compute a 95% CI on the final_score. If the lower
   bound straddles zero, the edge is sampling noise.
3. **PBO via Bailey-López-de-Prado** on the full 912-config sweep.
   Reports a probability that the in-sample winner has a negative
   out-of-sample expected score. Acceptance threshold: PBO < 0.5.
4. **Add realistic frictions**: 5 bps per switch (commission + spread)
   on Inter Internacional. Re-rank. Expect EMA-fast configs to lose
   meaningfully.
5. **Real-ETF overlay** post-2009 (UPRO inception, ZROZ inception 2009-12).
   Use Tiingo if available; otherwise re-pull testfol.io's modern slice.
   Sanity-check synthetic vs real divergence.
6. **Sub-period analysis**: how does the edge look in 1980-2000, 2000-
   2010, 2010-2026? Does the ZROZ effect survive each? In particular,
   2022 (the long-duration crash) is the natural stress test.
7. **Drop EMA** from the grid unless a specific mechanistic argument
   resurfaces — the heatmaps show it adds noise without alpha.
8. **Tighten the lookback grid around 200–300** at step 1 or step 2,
   not step 5. Phase-1's step-5 grid may be missing the actual local
   optimum.

## Files

- [`run.py`](./run.py) — phase-1 sweep runner.
- [`report.md`](./report.md) — auto-generated tables + heatmap embeds.
- [`results/sweep_full.csv`](./results/sweep_full.csv) — all 1,824 rows,
  human-readable.
- [`results/sweep_top20.csv`](./results/sweep_top20.csv) — top-20 per
  (on_leg × tax_scenario), 80 rows.
- [`results/sweep_summary.json`](./results/sweep_summary.json) — top-5
  per panel for quick inspection.
- [`results/manifest.json`](./results/manifest.json) — runtime config
  including all 57 lookbacks, weights, data hash.
- 4 heatmap PNGs under [`plots/`](./plots/) — one per (on_leg × tax_scenario).

## Citations

- SMA / EMA regime signal: `[leverage_for_the_long_run, p.13]`
- 2×/3× leverage tested: `[leverage_for_the_long_run, p.17, Table 8]`
- MA-window sweep precedent (Table 6): `[leverage_for_the_long_run, p.14]`
- Cash off-leg precedent: `[leverage_for_the_long_run, p.21]`
- ZROZ / IEF / GLD as alternative off-legs: lrs phase-1 contribution
  (no direct Gayed precedent; Gayed only tested cash).
- Multiple-testing / PBO motivation for phase-2:
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- Lei 14.754/2023 art. 5°/6° (BR offshore IR with indefinite loss
  carry-forward): https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14754.htm
- BR mandate context: `docs/investment-mandate.md` §1.
