# studies/lrs — Phase 0 Report (scoring-framework edition)

Generated: 2026-05-22T18:33:40.180925+00:00  ·  data: testfol.io  ·  scoring window: 1980-01-02 → 2026-05-21 (11692 bars)

## Hypothesis

When SPY closes above its 200-day SMA, a 2× or 3× S&P-500 LETF outperforms unlevered SPY net of BR taxes; when SPY closes below, holding cash dominates riding the LETF down. `[leverage_for_the_long_run, p.13]`

## Parameters

| Parameter | Value |
|---|---|
| Data source | testfol.io synthetic (SPYSIM / SSOSIM / UPROSIM) |
| Scoring window | 1980-01-02 → 2026-05-21 (11692 bars) |
| Filter / lookback / band | SMA / 200d / 0% |
| Execution | signal close T → exposure T+1 (no lookahead) |
| Cash off-leg yield | 0% |
| Commission / spread | 0 bps |
| Tax rate | 15% on net annual realised gain (Lei 14.754 art. 5°) |
| Tax cadence | annual settlement, first bar of next calendar year; loss carry-forward indefinite (Lei 14.754 art. 6°) |
| Window lengths | 1y, 3y, 5y, 10y, 15y, 20y, step ~21d (monthly) |
| Within-window weights | terminal 40%, time_above 25%, sortino 20%, calmar 15% (signed, tanh-squashed) |
| Per-length aggregation | 0.60·mean + 0.40·p25 |
| Across-length weights | 1y=5%, 3y=10%, 5y=15%, 10y=20%, 15y=25%, 20y=25% |
| Benchmark | B&H SPY (tax-free) for every strategy |

## Final scores

| Strategy | Tax-free | BR Lei 14.754 | Δ (tax cost) |
|---|---:|---:|---:|
| B&H SPY | +0.0000 | +0.0000 | +0.0000 |
| B&H SSO | +0.0313 | +0.0313 | +0.0000 |
| B&H UPRO | -0.1343 | -0.1343 | +0.0000 |
| LRS-SSO | +0.0819 | -0.0632 | -0.1451 |
| LRS-UPRO | +0.1235 | +0.0204 | -0.1031 |

- **Tax-free leader**: LRS-UPRO (score +0.1235).
- **BR Lei 14.754 leader**: B&H SSO (score +0.0313).

### Per-length aggregates — LRS-SSO

| Window | n | %win (free) | mean (free) | p25 (free) | length_score (free) | %win (tax) | mean (tax) | p25 (tax) | length_score (tax) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1y | 546 | 42% | -0.109 | -0.383 | -0.219 | 37% | -0.142 | -0.426 | -0.256 |
| 3y | 522 | 51% | +0.001 | -0.214 | -0.085 | 41% | -0.068 | -0.303 | -0.162 |
| 5y | 498 | 60% | +0.067 | -0.125 | -0.010 | 50% | -0.018 | -0.233 | -0.104 |
| 10y | 438 | 75% | +0.159 | -0.004 | +0.094 | 59% | +0.034 | -0.137 | -0.034 |
| 15y | 378 | 82% | +0.206 | +0.078 | +0.154 | 54% | +0.054 | -0.125 | -0.018 |
| 20y | 318 | 84% | +0.227 | +0.113 | +0.182 | 57% | +0.034 | -0.126 | -0.030 |

### Per-length aggregates — LRS-UPRO

| Window | n | %win (free) | mean (free) | p25 (free) | length_score (free) | %win (tax) | mean (tax) | p25 (tax) | length_score (tax) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1y | 546 | 40% | -0.108 | -0.413 | -0.230 | 38% | -0.128 | -0.443 | -0.254 |
| 3y | 522 | 54% | +0.025 | -0.188 | -0.060 | 50% | -0.023 | -0.254 | -0.115 |
| 5y | 498 | 65% | +0.107 | -0.141 | +0.008 | 56% | +0.048 | -0.202 | -0.052 |
| 10y | 438 | 78% | +0.227 | +0.051 | +0.156 | 70% | +0.141 | -0.056 | +0.062 |
| 15y | 378 | 83% | +0.266 | +0.110 | +0.203 | 72% | +0.173 | -0.061 | +0.080 |
| 20y | 318 | 82% | +0.294 | +0.137 | +0.231 | 70% | +0.165 | -0.045 | +0.081 |

## Companion full-window stats (context only — not part of the score)

| Strategy | Scenario | Terminal× | CAGR | MDD | Sortino | Switches | Tax events | Tax drag |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| B&H SPY | tax_free | 217.2× | 12.30% | 55.14% | 1.04 | 0 | 0 | 0.000 |
| B&H SPY | br_lei_14754 | 217.2× | 12.30% | 55.14% | 1.04 | 0 | 0 | 0.000 |
| B&H SSO | tax_free | 690.0× | 15.13% | 88.27% | 0.81 | 0 | 0 | 0.000 |
| B&H SSO | br_lei_14754 | 690.0× | 15.13% | 88.27% | 0.81 | 0 | 0 | 0.000 |
| B&H UPRO | tax_free | 438.0× | 14.01% | 98.31% | 0.73 | 0 | 0 | 0.000 |
| B&H UPRO | br_lei_14754 | 438.0× | 14.01% | 98.31% | 0.73 | 0 | 0 | 0.000 |
| LRS-SSO | tax_free | 597.8× | 14.78% | 55.02% | 0.97 | 265 | 0 | 0.000 |
| LRS-SSO | br_lei_14754 | 321.0× | 13.25% | 55.78% | 0.88 | 265 | 39 | 43.180 |
| LRS-UPRO | tax_free | 1,835.4× | 17.58% | 73.20% | 0.88 | 265 | 0 | 0.000 |
| LRS-UPRO | br_lei_14754 | 955.6× | 15.94% | 73.68% | 0.82 | 265 | 40 | 118.576 |

## Plots

Equity overlay (log scale, normalised at start):

![equity overlay](plots/equity_overlay.png)

Ratio to B&H SPY (log scale):

![ratio to SPY](plots/ratio_to_spy.png)

Rolling-window score timeline (one panel per window length, both tax scenarios):

![score timeline](plots/score_timeline.png)

Window-score distribution by length and tax scenario:

![score by length](plots/score_by_length.png)

## Sanity checks — all passed ✔

## Caveats

- Pre-2006/2009 SSO/UPRO bars are synthetic (Gayed `r = L·r_SPX − fee/252`), not measured.
- No commission / spread / slippage modelled — a whipsaw-heavy signal looks better here than in production.
- FX gain on USD/BRL is **not** modelled; real BR investors pay IR on FX appreciation. Ranks of strategies are preserved because all see the same FX.
- Tax base assumes long-term 15% (Lei 14.754 art. 5°); day-trade and the BR-domiciled R$ 35k/month rules don't apply to US-listed ETFs.
- B&H curves realise no gain during the window so their tax-free and taxed scores are identical — this matches a held-forever BR investor.
- Single-window descriptive run — no walk-forward, no PBO/DSR. See out-of-scope section in SPEC.md.

## Suggestions for phase 1+

- Layer realistic frictions: Inter Internacional commission, ~5 bps spread per switch.
- Cash off-leg via CASHX (Fed Funds proxy) — material when FFR > 3%.
- Walk-forward + block bootstrap on the regime parameters (lookback, band).
- Tiingo real-ETF overlay for 2009+ OOS sanity vs synthesised SSOSIM/UPROSIM.
- Sweep MA window {50, 100, 125, 150, 200} per Gayed Table 6 `[leverage_for_the_long_run, p.14]`.

## Citations

- SMA200 regime signal: `[leverage_for_the_long_run, p.13]`
- 2×/3× leverage tested in paper: `[leverage_for_the_long_run, p.17, Table 8]`
- Cash off-leg (not BIL): `[leverage_for_the_long_run, p.21]`
- Synthetic LETF formula: `[leverage_for_the_long_run, p.16]`
- Lei 14.754/2023 art. 5°/6° (BR offshore IR, 15%, indefinite loss carry-forward): https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14754.htm
- Sortino & Price (1994) — downside-only volatility, precedent in `[advances_fin_ml, p.41-43]`.
- Vectorized rolling-metric implementation precedent: `studies/static_spy_beater_portfolio/scripts/score_portfolio.py`.
- BR mandate context: `docs/investment-mandate.md` §1.

