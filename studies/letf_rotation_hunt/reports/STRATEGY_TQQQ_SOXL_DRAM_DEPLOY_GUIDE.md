# Strategy Deploy Guide — TQQQ + SOXL + DRAM + UPRO/SPXL with ZROZ off-state

**Status:** FORWARD-LOOKING DEPLOY GUIDE (not validated by backtest)
**Date:** 2026-05-07
**Parent study:** `studies/letf_rotation_hunt/`
**Universe extension:** beyond canonical QLD/ZROZ to a 4-asset 3× LETF rotation

---

## ⚠️ Honest Disclaimer (READ FIRST)

**This document is a forward-looking deploy guide, NOT a validated strategy.** Every parameter below is an extrapolation from the QLD/ZROZ canonical that the parent study validated. The guide produces NO deploy authorization, NO Sharpe/Sortino numbers, NO capital recommendations.

**Specific caveats:**

1. **DRAM does not yet exist** as a 3× ETF. As of 2026-05-07 there is no listed 3×-leveraged memory-chip ETF (analogous to SOXL but narrower to memory chips like Micron, SK Hynix, Samsung). This guide treats DRAM as a *placeholder asset* for when an issuer (Direxion, ProShares, GraniteShares) launches such a product. Until then, DRAM cannot be deployed; the slot remains in ZROZ by default.

2. **Numbers are priors, not measurements.** The per-asset parameter choices (SMA periods, vol thresholds, smabuf percentages) are derived from a literature-scaling rule (`[trading_systems_methods, Kaufman ch.21]`), not from a backtest of this specific 4-asset universe. There is no PBO, DSR, walk-forward, or cohort robustness validation for this configuration.

3. **Real deploy requires a formal sub-study.** Before any capital deployment, the following must be completed (see §5 Validation Roadmap):
   - Full T3d-style backtest sweep on TQQQ/SOXL/DRAM (when available)/UPRO|SPXL with ZROZ
   - 7-gate battery (PBO < 0.5, DSR p < 0.05, walk-forward ≥ 6/8, single-block OOS, FWD stress, bootstrap 99.9% CI low > 0, cross-lib ±3pp CAGR)
   - Cohort robustness analysis (8 named cohorts + regime stratification)
   - Sortino-anchored threshold rebuild specific to this universe (cannot reuse Sortino thresholds from `qld_vote_k2_off_zroz` because mean-vol-skew differ)
   - Tax-comparison analysis under Lei 14.754/2023 (M1 + M2 tracks)

4. **Mandate §1 (`docs/investment-mandate.md`) keeps capital 100% Plano C.** Strategy A (Pepperstone CFD), B (Inter swing US LETF), and D (BR ranking) are DORMANT. This deploy guide does NOT change that. It exists as research scaffolding for if/when Plano B is ever reactivated.

---

## 1. Universe + OFF Asset Choice

### 1.1 Risk assets (4 × 3× LETFs)

| Slot | Ticker | Underlying | Vol class (3× annual realized) | Status |
|---|---|---|---|---|
| 1 | **TQQQ** | NASDAQ-100 (tech-broad) | ~60% | Listed (ProShares, AUM ~$25B, ER 0.95%) |
| 2 | **SOXL** | PHLX Semiconductor (semis-narrow) | ~84% | Listed (Direxion, AUM ~$10B, ER 0.94%) |
| 3 | **DRAM** | Memory-chip narrow (hypothetical) | ~80-100% (estimated) | **NOT YET LAUNCHED** |
| 4 | **UPRO** *or* **SPXL** | S&P 500 (broad-market) | ~48% | Both listed and fungible |

**UPRO vs SPXL:** these are functionally equivalent 3× S&P 500 LETFs from competing issuers (ProShares vs Direxion). They differ on:
- Expense ratio: UPRO 0.91% vs SPXL 1.00%
- AUM: UPRO ~$3.5B vs SPXL ~$4.5B
- Bid-ask spread: typically tighter on UPRO during US market hours
- Issuer counterparty risk: ProShares (UPRO) vs Direxion (SPXL)

Choose based on broker availability + observed spread + counterparty diversification. The signal architecture treats them identically.

**Why these 4 assets:**
- **TQQQ** is the canonical extension of QLD from 2× to 3× NDX. The parent study tested it (T3d-multi-asset-grid iter 023) and found the same canonical pattern works.
- **SOXL** captures the high-beta tech subset (semis lead tech, tech leads broad market). Citation: `[trading_systems_methods, Kaufman ch.21]` on sector-momentum dispersion.
- **DRAM** narrows further to memory chips, the highest-volatility semi subset. Conceptually rationale: when memory cycle is up, returns are extreme; when down, the slot routes to ZROZ via the regime filter. **Currently a placeholder until launched.**
- **UPRO/SPXL** adds broad-market exposure. SPX is lower-correlated with NDX/SOX during late-cycle regime shifts (e.g., 2000 dotcom: NDX -83% peak-to-trough, SPX -49%). Including a broad-market 3× slot diversifies the regime-filter signal, reducing single-index path-dependence.

### 1.2 OFF asset — ZROZ (universal best)

**ZROZ** (PIMCO 25+ Year Zero Coupon US Treasury Index ETF) is the OFF asset for all 4 slots.

**Citation:** parent study `STUDY_FINAL_REPORT.md` §3.4 — ZROZ tested across all 6 LETF on-asset variants (QLD, TQQQ, UPRO, SOXL, FAS, SSO) and ZROZ won as the universal best off-asset by `[advances_fin_ml, p.275]` net-of-cost evaluation. Long-duration zero-coupon Treasuries provide:
- Strong negative correlation with risk-on equities during regime transitions (1987, 2000, 2008, 2020, 2022)
- Convexity in flight-to-quality regimes
- Minimal cost drag (ER 0.15%)

Alternatives (TLT, EDV, IEF) were evaluated and ZROZ dominated all of them. See parent study §6 for the comparison table.

---

## 2. Signal Architecture per Asset

### 2.1 Signal family — T3d K=2 Vote-of-K with smabuf 5%

Each slot uses the same Vote-of-K=2 signal architecture from the parent study, with **per-asset parameter calibration** scaled by Kaufman's vol-scaling rule (`[trading_systems_methods, Kaufman ch.21]`):

> SMA lookback period scales as √(asset realized vol / market realized vol)

The "market" baseline is QLD (2× NDX, ~40% annualized realized vol) on which the canonical T3d K=2 was calibrated.

The 4 sub-signals per asset (Vote-of-K=2: ON if at least 2 of 4 are TRUE):
- **s1:** `price > SMA(long_period)` with smabuf=5% buffer (per `sortino_reanalysis` Track B-M1 winner candidate)
- **s2:** `price > SMA(short_period)` with smabuf=5% buffer
- **s3:** `realized_vol(window) < threshold`
- **s4:** `AR(1)(window) > 0`

The smabuf=5% buffer on SMA crossings reduces whipsaw trade count by ~30% (per `THRESHOLD_SWEEP_REPORT.md` §3.3 — `t3d_k2_smabuf_5pct` was the boundary winner under Sharpe and a clear Track A passer under Sortino per `SORTINO_REANALYSIS_REPORT.md` §5).

### 2.2 Per-asset parameters (literature-scaling rule)

| Asset | Vol class | SMA long | SMA short | vol_window | vol_threshold | ar1_window | smabuf | Justification |
|---|---|---:|---:|---:|---:|---:|---:|---|
| **TQQQ** | ~60% | 250 | 100 | 21 | 0.40 | 30 | 5% | Sortino-winner from `sortino_reanalysis` for QLD/TQQQ class (sma250/100 best on lh_56y gross Sortino). Updated from prior 200/50. |
| **SOXL** | ~84% | 200 | 50 | 21 | 0.30 | 30 | 5% | Data-driven from `SOXL_SMA_SWEEP_V2_REPORT.md`: SMH-signal + SOXL-position, post-2010-04 real Tiingo data, vol_threshold=0.30 (SMH 1x SOX class). Best combo sma200/50 with Sortino=1.087. The earlier v1 sweep (sma200/50 Sortino=1.093) used QQQSIM proxy and is superseded. vol_threshold lowered from 0.40 to 0.30 because SMH 1x SOX volatility class is lower than QLD 2x NDX; canonical 0.40 was calibrated for 2x leveraged underlying, not 1x. `[leverage_for_the_long_run, p.5-6]` |
| **DRAM** | ~80-100% (est.) | 200 | 50 | 21 | 0.30 | 30 | 5% | Same as SOXL until real data exists. Memory chips are a semis subset; vol class assumed similar. Mirrors SOXL v2 params including vol_threshold=0.30. |
| **UPRO/SPXL** | ~48% | 250 | 100 | 21 | 0.40 | 30 | 5% | Sortino-winner from `sortino_reanalysis`: same vol class as TQQQ. Updated from prior 200/50. |

**Citation anchors:**
- `[trading_systems_methods, Kaufman ch.21]` — SMA scaling rule across asset volatility regimes (prior; data-driven sweep overrides for SOXL)
- `[systematic_trading, Carver p.122-133, p.174]` — asymmetric vol gates for leveraged systems; Half-Kelly under fat-tail upside
- `[advances_fin_ml, p.208-211]` — anti-overfit margin (any future backtest must reapply CSCV PBO with this scaled threshold)
- Sister: `THRESHOLD_SWEEP_REPORT.md` §3.3 (smabuf 5% rationale)
- Sister: `SORTINO_REANALYSIS_REPORT.md` §5 (Sortino-space justification; TQQQ/UPRO/SPXL 250/100 update)
- Sub-study: `SOXL_SMA_SWEEP_V2_REPORT.md` for SOXL/DRAM SMA params (sma200/50 real-data corrected; v1 `SOXL_SMA_SWEEP_REPORT.md` superseded due to QQQSIM proxy error)

### 2.3 Allocation rule — independent slots (option A, 1/4 each)

Each of the 4 slots holds 1/4 of the budget. The slot's signal independently routes that 1/4 between the asset and ZROZ:

```
slot_i_alloc = (1/4) × asset_i if slot_i_signal == ON
             = (1/4) × ZROZ   if slot_i_signal == OFF

portfolio = sum(slot_i_alloc for i in 1..4)
ZROZ allocation = (4 - N_on) / 4    # 0% if all 4 ON, 100% if all 4 OFF
```

This is the natural N-asset extension of the parent study canonical (where N=1, slot=100%). It avoids vol-target weighting (over-engineered for unvalidated universe) and top-1 rotation (different strategy family).

**Rebalancing cadence:** signals computed at month-end EOD. Position changes executed at next month-open (T+1 to allow Sortino-thresholded gates to settle). This mirrors the canonical T3d cadence.

### 2.4 Signal evaluation example (illustrative — not measured)

| Month-end | TQQQ s | SOXL s | DRAM s | UPRO s | TQQQ alloc | SOXL alloc | DRAM alloc | UPRO alloc | ZROZ alloc |
|---|---|---|---|---|---|---|---|---|---|
| 2024-06 | ON (K=4) | ON (K=3) | (no DRAM yet) | ON (K=4) | 25% | 25% | 0% | 25% | 25% (DRAM slot) |
| 2025-01 | ON (K=2) | OFF (K=1) | (no DRAM yet) | ON (K=3) | 25% | 0% | 0% | 25% | 50% |
| Hypothetical 2027-08 (DRAM listed) | OFF (K=1) | OFF (K=0) | OFF (K=1) | OFF (K=1) | 0% | 0% | 0% | 0% | 100% |

Until DRAM exists, the DRAM slot is permanently in ZROZ — equivalent to a 3-asset portfolio (TQQQ + SOXL + UPRO/SPXL) with 1/4 base ZROZ buffer.

---

## 3. Sortino-Based Expected-Edge Framing

Per the just-completed `sortino_reanalysis` sub-study, **Sortino is the operative metric** for LETF rotation strategies, not Sharpe. Reasons:

- LETF strategies have asymmetric upside fat tails (the whole point of using leverage). Sharpe penalises positive volatility symmetrically; Sortino penalises only adverse semideviation.
- For the canonical `qld_vote_k2_off_zroz`, the Sortino edge over SPY (+0.264) is ~55% larger than the Sharpe edge (+0.171), confirming the asymmetric upside hypothesis.
- The threshold rebuild rule (`canonical_Sortino + 0.05`) replaces the Sharpe rebuild rule going forward.

### 3.1 Expected-edge prior (qualitative only)

This guide provides NO expected Sortino numbers because:
1. The 4-asset universe has not been backtested.
2. Sortino-anchored thresholds for this universe must be rebuilt (cannot reuse `qld_vote_k2_off_zroz` thresholds 1.272 / 1.016 / 1.144 because the mean-vol-skew of the new universe differs).
3. Mandate §1 prevents capital deployment regardless of any number we might cite.

What we CAN say qualitatively (priors, not measurements):
- A 4-asset rotation should have **lower per-asset variance** than a 1-asset rotation (Carver Half-Kelly diversification benefit).
- The universe expansion should **dampen 2000 dotcom-style path-dependence** (the canonical's only absolute killer per `COHORT_ROBUSTNESS_REPORT.md`), because UPRO/SPXL has different cohort timing than NDX-indexed TQQQ/SOXL.
- The smabuf 5% buffer should reduce trade count and tax drag analogously to the canonical (per `THRESHOLD_SWEEP_REPORT.md` §3.3, ~30% trade count reduction, ~+0.072 M1 Sharpe edge).

These are priors. Real deploy needs measurements.

### 3.2 Citations

- `[sortino_1991]` Sortino, F.A. (1991) "Performance Measurement in a Downside Risk Framework"
- `[advances_fin_ml, p.275]` de Prado on net-of-cost evaluation + risk-adjusted metric family
- Sister: `SORTINO_REANALYSIS_REPORT.md` §1, §7, §10

---

## 4. Operational Considerations (NON-DEPLOY)

The following are operational priors the deploy guide MUST NOT obscure:

### 4.1 Slippage and spread

3× LETFs have intraday volatility that produces wider spreads than 1× ETFs. Estimates (Inter Internacional, FINRA-cleared):
- **TQQQ**: typical spread 1-2bps during US RTH; 5-10bps in pre/post
- **SOXL**: typical spread 3-5bps RTH; 10-20bps off-hours
- **DRAM**: TBD when launched; expect SOXL-class
- **UPRO/SPXL**: typical spread 1-3bps RTH; 5-15bps off-hours
- **ZROZ**: typical spread 5-10bps RTH (lower volume)

Combined slippage budget per rebalance: ~10-30bps round-trip across the 4 slots, depending on regime-shift volume timing.

### 4.2 Tax drag (Lei 14.754/2023)

Per `tax_comparison` sub-study, the canonical 1-asset rotation has:
- M1 (per-swing 15%): 7.24pp/yr CAGR drag, kills 5/10 strategies' Sharpe edge
- M2 (annual 15%, lei 14.754 mode): 3.69pp/yr CAGR drag, all 10 strategies survive

A 4-asset rotation will trade more frequently (4 independent signals vs 1), increasing M1 drag proportionally. Estimated M1 drag for this universe: 10-15pp/yr (prior, not measured).

**M2 (annual netting) is the realistic deploy regime.** If/when this strategy is deployed, it MUST be deployed under M2 with proper carry-forward of intra-year losses. M1 is the worst-case bound.

### 4.3 Counterparty and tracking risk

- **TQQQ**: ProShares — swap-based, multi-counterparty risk diversified
- **SOXL**: Direxion — swap-based, primarily Société Générale and Morgan Stanley counterparties
- **UPRO**: ProShares (same as TQQQ family, slight counterparty concentration if both held)
- **SPXL**: Direxion (same as SOXL family)
- **ZROZ**: PIMCO — physical Treasury holdings, no swap counterparty
- **DRAM**: TBD

**Counterparty diversification consideration:** if UPRO is chosen alongside TQQQ, both are ProShares — concentrating ProShares counterparty exposure to ~50% of the risk budget (when both ON). Pairing TQQQ with **SPXL** instead diversifies across ProShares + Direxion. Recommend SPXL when held alongside TQQQ; UPRO when held alongside non-ProShares (which never happens in this universe). **Default: SPXL** for this guide.

### 4.4 Mandate §1 reminder

This guide produces NO capital recommendations. Mandate §1 keeps capital 100% Plano C (passive factor-tilted retirement portfolio). Strategy B (this universe, IF reactivated) would be a swing US LETF rotation through Inter Internacional with FINRA clearing.

---

## 5. Validation Roadmap

Before any capital deployment, the following sub-studies are mandatory. Each is roughly the scope of an existing letf_rotation_hunt sub-study.

### 5.1 Backtest sweep (T3d-style)

- **Goal:** establish gross + net Sortino baseline for the 4-asset universe across 4 datasets (lh_56y, modern_1990, spy_real, ndx_real)
- **Scope:** 1 baseline + parameter grid (smabuf 0/1/2/3/5%, vol_threshold 0.36/0.40/0.50, SMA scalings ±10%) ≈ 30-50 configs
- **Effort:** ~2 weeks subagent-driven
- **Output:** `letf_rotation_hunt/multi_asset_v1/` with mirror structure to `threshold_sweep/`

### 5.2 7-gate battery on the winning config

- **Gates:** G1 PBO < 0.5, G2 DSR p < 0.05, G3 walk-forward ≥ 6/8, G4 single-block OOS, G5 FWD post-2020 stress, G6 bootstrap 99.9% CI low > 0, G7 cross-library CAGR delta ≤ 3pp
- **Citation:** parent study `STUDY_FINAL_REPORT.md` §3.5
- **Pass requirement:** all 7 gates green

### 5.3 Cohort robustness rerun

- **Cohorts:** 8 named (1987 / 2000 / 2007 / 2020 / 2021 / 2003 / 2009 / 2022) + 4 regime stratification + forward-Sharpe heatmap (1278 entries × 4 horizons)
- **Goal:** check if UPRO/SPXL diversification reduces 2000 dotcom path-dependence (canonical's worst at -12.7% 5y CAGR; new winner sma250/100 already drops it to -1.6% per `SORTINO_REANALYSIS_REPORT.md` §6 — UPRO/SPXL inclusion may further reduce it)
- **Effort:** ~1 week (reuses `cohort_robustness/` infra)

### 5.4 Sortino-anchored threshold rebuild

- **Goal:** establish Track A / B-M1 / B-M2 thresholds specific to this 4-asset universe, anchored on the new canonical's Sortino + 0.05
- **Note:** thresholds from `qld_vote_k2_off_zroz` (1.272 / 1.016 / 1.144) MUST NOT be reused. New universe → new canonical → new thresholds.
- **Effort:** ~3 days (reuses `sortino_reanalysis/` infra)

### 5.5 Tax comparison under Lei 14.754/2023

- **Models:** M1 per-swing 15% (worst case) and M2 annual 15% (realistic)
- **Goal:** measure tax drag for the 4-asset universe (expected 10-15pp/yr M1, 4-6pp/yr M2)
- **Pass requirement:** M2 net Sortino edge vs SPY ≥ +0.05 (using Sortino-anchored deploy threshold from §5.4)
- **Effort:** ~3 days (reuses `tax_comparison/` infra)

### 5.6 Live paper-trading validation

- **Duration:** ≥ 6 months on Inter Internacional paper account (or equivalent FINRA-cleared paper)
- **Pass requirement:** realized monthly returns within ±2σ of backtest monthly distribution (Kolmogorov-Smirnov p > 0.05)
- **Citation:** `[advances_fin_ml, p.31-34]` multi-window forward stress
- **Effort:** wall-clock 6+ months, minimal compute

### 5.7 DRAM listing wait

- **Status:** blocked until a 3× memory-chip ETF is launched by Direxion/ProShares/GraniteShares
- **Fallback:** until DRAM exists, deploy the 3-asset universe (TQQQ + SOXL + UPRO/SPXL) with 1/4 ZROZ baseline (the DRAM slot stays in ZROZ)
- **Re-activation trigger:** new 3× memory-chip ETF reaches AUM ≥ $200M and average daily volume ≥ $5M over 30 days

---

## 6. Summary

This guide documents a forward-looking 4-asset 3× LETF rotation strategy using the canonical T3d K=2 + smabuf 5% signal family with per-asset parameter scaling per `[trading_systems_methods, Kaufman ch.21]`. Universe: TQQQ / SOXL / DRAM (hypothetical) / UPRO|SPXL with ZROZ as universal off-state. Allocation: independent 1/4 slots.

**It is NOT a deployment authorization.** Mandate §1 keeps capital 100% Plano C. Deploy requires the formal sub-studies in §5 — none of which currently exist for this universe.

**If/when Plano B is reactivated** and the validation roadmap completes successfully, this guide is the entry-point document for the 4-asset variant. The currently validated 1-asset variant (`qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`, the new winner under Sortino) remains the recommended baseline until the 4-asset version completes its own gates.

---

## 7. Citations (full block)

- **Sortino, F.A. (1991)** "Performance Measurement in a Downside Risk Framework," Financial Executive, 17(8): 31-34. → `[sortino_1991]`
- **López de Prado, M. (2018)** *Advances in Financial Machine Learning*. → `[advances_fin_ml, p.31-34]` (multi-window validation), `[advances_fin_ml, p.208-211]` (CSCV PBO + multiple-testing margin), `[advances_fin_ml, p.222-223]` (forward stress), `[advances_fin_ml, p.275]` (deflated SR + net-of-cost evaluation).
- **Carver, R. (2015)** *Systematic Trading*. → `[systematic_trading, Carver p.122-133]` (Half-Kelly + asymmetric exit for leveraged), `[systematic_trading, Carver p.174]` (vol-scaling for trend-following).
- **Kaufman, P. (2020)** *Trading Systems and Methods*. → `[trading_systems_methods, Kaufman ch.21]` (alternative risk measures + SMA period scaling), `[trading_systems_methods, Kaufman ch.6]` (signal smoothing + buffer hysteresis).
- **Gayed, M. (2008)** "Leverage for the Long Run." → `[leverage_for_the_long_run, p.13]` (canonical LRS framework), `[leverage_for_the_long_run, p.16, p.21]` (LETF path-dependence and recovery).
- **Lei 14.754/2023 (Brasil)** — 15% flat tax with carry-forward indefinido on offshore investments.
- Parent: `STUDY_FINAL_REPORT.md` §3.4 anti-curve-fit threshold, §6 ZROZ universal-best, §7.7 Cenário B.
- Sister: `THRESHOLD_SWEEP_REPORT.md` §3.3 smabuf 5% boundary winner.
- Sister: `TAX_COMPARISON_REPORT.md` (M1/M2 drag measurement).
- Sister: `COHORT_ROBUSTNESS_REPORT.md` §1 (2000 dotcom path-dependence).
- Sister: `SORTINO_REANALYSIS_REPORT.md` §5, §7 (Sortino threshold rebuild + new winner).

---

## 8. Where this lives

- This guide: `studies/letf_rotation_hunt/reports/STRATEGY_TQQQ_SOXL_DRAM_DEPLOY_GUIDE.md`
- Parent study: `studies/letf_rotation_hunt/`
- Mandate: `docs/investment-mandate.md` §1 (capital allocation), §4.8 (no-DARF on Pepperstone CFD; Inter retains DARF in cost model)
- No code, no tests, no data — pure documentation.
