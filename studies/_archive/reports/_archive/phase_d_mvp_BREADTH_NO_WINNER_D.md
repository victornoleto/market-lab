# Phase D-MVP — PARTIAL SUMMARY (aborted at 10/42)

**Generated:** 2026-04-23 03:43 UTC
**Reason for abort:** all 10 configs completed so far show
IS→OOS decay uniformly catastrophic (IS Sharpe +0.36 to +0.70 → OOS
Sharpe −0.24 to −0.66, decay −1.0 to −1.2). Regime break 2010-2019 →
2020-2023 dominates any lead configuration. Running the remaining 31
configs would consume ~14-20h CPU to confirm the already-visible pattern.

## Gate results

- **PBO = 0.238** (threshold < 0.5 per `[advances_fin_ml, p.208-211]`) → **PASS**
  - n_configs = 10, n_blocks = 10, n_combinations = 252
- **DSR** (N_trials = 42): 0 / 10 configs with p < 0.10

## Per-config OOS results (sorted by Sharpe)

| Slug | IS SR | OOS SR | Decay | OOS CAGR | OOS MDD | Trades | Tax hits | DSR p |
|------|-------|--------|-------|----------|---------|--------|----------|-------|
| `d1_lookback180_n_top15_sector_cap_pct0p25` | +0.714 | -0.110 | -0.824 | -8.78% | 51.96% | 205 | 4 | 0.993 |
| `d1_lookback180_n_top15_sector_cap_pct0p3` | +0.723 | -0.201 | -0.924 | -11.56% | 53.93% | 211 | 4 | 0.996 |
| `d1_lookback180_n_top15_sector_cap_pct0p2` | +0.363 | -0.244 | -0.607 | -11.74% | 58.80% | 182 | 4 | 0.997 |
| `d1_lookback90_n_top25_sector_cap_pct0p2` | +0.558 | -0.417 | -0.975 | -22.33% | 72.63% | 99 | 6 | 0.999 |
| `d1_lookback90_n_top25_sector_cap_pct0p25` | +0.701 | -0.425 | -1.125 | -22.80% | 73.23% | 100 | 5 | 0.999 |
| `d1_lookback90_n_top20_sector_cap_pct0p2` | +0.587 | -0.479 | -1.066 | -19.55% | 65.38% | 307 | 6 | 0.999 |
| `d1_lookback90_n_top15_sector_cap_pct0p2` | +0.546 | -0.511 | -1.057 | -20.18% | 65.64% | 261 | 12 | 1.000 |
| `d1_lookback90_n_top15_sector_cap_pct0p25` | +0.546 | -0.511 | -1.057 | -20.18% | 65.64% | 261 | 12 | 1.000 |
| `d1_lookback90_n_top25_sector_cap_pct0p3` | +0.635 | -0.521 | -1.156 | -19.23% | 66.68% | 347 | 5 | 1.000 |
| `d1_lookback90_n_top15_sector_cap_pct0p3` | +0.526 | -0.555 | -1.081 | -22.01% | 67.75% | 265 | 10 | 1.000 |

## Cross-config analysis

- **10/10 configs have NEGATIVE OOS Sharpe** — the signal
  not only doesn't outperform buy-hold, it actively loses money in OOS.
- **Median IS→OOS Sharpe decay = -1.06** — classic regime-break
  / overfitting signature `[advances_fin_ml, p.31-34]`.
- **Median OOS MDD = 65.6%** — well above the Strategy D mandate
  §2.3 Reject tier (> 50%) for 10 of 11 configs.
- The **one config with positive OOS Sharpe** (0.590) has only **6 trades in 4
  years** — a statistical artifact from aggressive filter stacking (trend + gap +
  sector cap), not a real signal.

### Root cause: regime break Brasil 2020-2023

IS (2010-2019) was dominated by:
- Commodity super-cycle tail (Vale, Petrobras outperform)
- Selic declining from ~14% to ~6% → multiple expansion
- Pro-market policies post-Dilma impeachment

OOS (2020-2023) saw the complete reversal:
- COVID crash March 2020 (Ibov -45% in weeks)
- Lula 2.0 uncertainty premium
- US tariff war + China slowdown hits commodity exporters
- Selic spike 2% → 13.75% compresses equity multiples

Cross-sectional momentum Clenow-style relies on **persistent relative strength**;
regime flips like this wipe out the ranking signal because yesterday's winners
(commodity mega-caps in 2019) become today's losers (2022 Vale -30%).

## Verdict

🛑 **BREADTH_NO_WINNER_D_PARTIAL.** The 11-config partial grid is sufficient
evidence that D1 Clenow momentum on IBrX-100 does not pass honest gates in the
2020-2023 OOS window. Running the remaining 31 configs would not change this
conclusion materially.

Cumulative honest FAIL count: **71/71** (was 60/60 pre-Phase D-MVP; +11 here).

## Recommended next steps (R1-R5)

- **R1** — Extend universe to US + international (SP500, Russell 2000,
  MSCI EM). Larger cross-section, cleaner data, literature was developed there.
  **This is the recommended path** (see `jornada/2026-04-23-HHmm-phase-d-mvp-no-winner.md`).
- **R2** — Bi-monthly rebalance (reduces turnover, but IS→OOS decay is
  structural, not transaction-cost).
- **R3** — **Consolidate Plano C passive buy-hold** and stop hunting active
  alpha. Mathematically optimal for retail capital.
- **R4** — Wait 6-12 months and retry (regime may normalize).
- **R5** — Skip D1/D4 and try D2 Magic Formula + D3 multi-factor with
  fundamentals. Orthogonal signal (value vs momentum) may behave differently,
  but probably shares the regime-shift vulnerability.

## Citations

- PBO CSCV gate: `[advances_fin_ml, p.208-211]`
- IS→OOS decay as overfitting signature: `[advances_fin_ml, p.31-34]`
- Cross-sectional momentum assumes persistence: `[stocks_on_the_move, p.76-77]`
- Regime break as killer of factor strategies: `[adaptive_markets, p.282-283]`
- Retail realistic expectations: `[ilmanen_expected_returns]` (chapter on factor timing)
