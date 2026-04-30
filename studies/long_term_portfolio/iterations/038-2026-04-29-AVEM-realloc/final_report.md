# Iter 038 — Final Report — `AVEM-realloc`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 79/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **STRONG 84/100** — `winner_conditions_met=True`.

**Primary citation**: [ilmanen_expected_returns, ch.19]

---

## Selected config: `avem10_subGDE`

Weights:

```json
{
  "NTSXSIM": 0.25,
  "GDESIM": 0.15,
  "KMLMSIM": 0.35,
  "TLTSIM": 0.15,
  "AVEMSIM": 0.1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.093 | 10.38% | 21.05% | 6/7 | 6.02e-08 |
| **vt_real** | 0.920 | 8.81% | 19.66% | 6/7 | 1.20e-03 |
| **ndx_real** | 1.070 | 9.32% | 10.85% | 6/7 | 3.27e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| avem10_subNTSX | 1.073 | 0.928 | 1.066 |
| avem10_subGDE | 1.093 | 0.920 | 1.070 |
| avem10_subKMLM | 1.025 | 0.918 | 1.088 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.093 | +0.413 | [OK] |
| vt_real | 0.900 | 0.950 | 0.920 | +0.020 | [--] |
| ndx_real | 0.900 | 0.950 | 1.070 | +0.170 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 27
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **AVEMSIM** = `VWOSIM + 125bps/y tilt premium`. INCOMPLETE — VWOSIM is passive EM (no quality screen); 125bps tilt premium is highest of AV* family (estimates Avantis EM size+value+profitability multifactor active edge). Real AVEM live since 2019.
- **WINDOW CAVEAT (CRITICAL)**: VWOSIM starts 1994-05-04 → effective lh_56y window is **32y (1994-2026)**, NOT 56y. Sub-source variation does not change this constraint. The 32y window 1994-2026 was a US-large-cap regime ~3-4pp/yr CAGR ahead of EM, biasing this test against EM-tilted portfolios. vt_real (2008+) and ndx_real (2010+) windows are unaffected (apples-to-apples vs other iters).

## Substitution source comparison (fixed 10% AVEM weight)

| sub source | NTSX | GDE | KMLM | Sharpe lh_56y (32y) | Sharpe vt_real | Sharpe ndx_real | Δ vs iter 023 |
|---|---:|---:|---:|---:|---:|---:|---|
| **subGDE** *(best, selected)* | 25% | 15% | 35% | 1.0928 | 0.9203 | 1.0704 | −0.096 / −0.084 / −0.065 |
| subNTSX | 15% | 25% | 35% | 1.0727 | 0.9284 | 1.0664 | −0.116 / −0.076 / −0.069 |
| subKMLM | 25% | 25% | 25% | 1.0247 | 0.9181 | 1.0879 | −0.164 / −0.086 / −0.047 |

**Iter 023 baseline**: lh_56y=1.189, vt_real=1.004, ndx_real=1.135. **All 3 sub sources beat iter 023 on 0/3 datasets.**

## Phase 1A vs Phase 1B comparison

| metric | Phase 1A iter 032 best (`avem_lite`, 5%, balanced sub) | Phase 1B iter 038 best (`avem10_subGDE`, 10%, sub GDE) |
|---|---|---|
| Sharpe lh_56y (32y) | 1.082 | 1.093 |
| Sharpe vt_real | 0.969 | 0.920 |
| Sharpe ndx_real | 1.115 | 1.070 |
| Δ vs iter 023 | −0.107 / −0.035 / −0.020 | −0.096 / −0.084 / −0.065 |
| Datasets beating 023 | 0/3 | 0/3 |

Phase 1B `subGDE` at 10% modestly improves lh_56y (+0.011) but degrades vt_real (−0.049) and ndx_real (−0.045) substantially vs Phase 1A best. Net: **worst Phase 1B result of any sleeve.**

## Lesson

**KILL #1 (no-positive-config) ✅ FIRES** under all 3 sub sources. AVEM sleeve closure REAFFIRMED. Worst Phase 1B sleeve overall.

- **Best sub source**: `subGDE` (selected). Same Phase 1B pattern (cuts GDE preserves long-history KMLM) but the EM beta cost dominates regardless.
- **Worst sub source**: `subKMLM` (lh_56y −0.164, ndx_real worsens −0.047 too). Same KMLM-cost pattern but compounded by EM weakness.
- **Window caveat dominates lh_56y test**: 1994-2026 was structurally biased against EM. But vt_real and ndx_real windows are apples-to-apples and **all 3 sub sources still lose substantially** (−0.076 to −0.086 vt_real, −0.047 to −0.069 ndx_real).
- **AVEM sleeve closure REAFFIRMED**, with BOTH live windows confirming subordination (window caveat does not save it).
- Combined Phase 1A+1B finding: **all 3 Avantis factor sleeves (AVUV/AVDV/AVEM) closed under sub-source variation**. F5 Global Factor-only finalist (iter 036 original sweep) cannot proceed with non-momentum factors — only SPMO remains positive. F5 should be skipped or rebuilt as SPMO-only.
- Citation `[ilmanen_expected_returns, ch.19]` intl + EM diversification framework is honest; the issue is the post-2010 EM regime drag + 1994-2026 window structural bias.
