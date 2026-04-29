# Iter 036 — Final Report — `SPMO-realloc`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 86/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **STRONG 86/100** — `winner_conditions_met=True`.

**Primary citation**: [stocks_on_the_move, p.21-30]

---

## Selected config: `spmo10_subGDE`

Weights:

```json
{
  "NTSXSIM": 0.25,
  "GDESIM": 0.15,
  "KMLMSIM": 0.35,
  "TLTSIM": 0.15,
  "SPMOSIM": 0.1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.161 | 11.12% | 19.87% | 7/7 | 1.73e-10 |
| **vt_real** | 0.987 | 9.38% | 15.99% | 6/7 | 4.96e-04 |
| **ndx_real** | 1.157 | 10.27% | 10.38% | 6/7 | 9.45e-05 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| spmo10_subNTSX | 1.130 | 1.000 | 1.159 |
| spmo10_subGDE | 1.161 | 0.987 | 1.157 |
| spmo10_subKMLM | 1.087 | 0.994 | 1.179 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.161 | +0.481 | [OK] |
| vt_real | 0.900 | 0.950 | 0.987 | +0.087 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.157 | +0.257 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **SPMOSIM** = `SPYSIM + 0.60 × UMD_KF − 35bps/y`. INCOMPLETE — UMD_KF = Ken French long-short academic momentum factor; 0.60 capture coefficient per Frazzini-Israel-Moskowitz 2018 long-only constraint estimate. 35bps/y = SPMO TER + estimated implementation drag. Real SPMO live since 2015 has Sharpe ~0.7-0.9, matching the synth standalone Sharpe 0.828.

## Substitution source comparison (fixed 10% SPMO weight)

| sub source | NTSX | GDE | KMLM | Sharpe lh_56y | Sharpe vt_real | Sharpe ndx_real | Δ vs iter 023 |
|---|---:|---:|---:|---:|---:|---:|---|
| **subGDE** *(best, selected)* | 25% | 15% | 35% | 1.1611 | 0.9873 | 1.1570 | −0.028 / −0.017 / **+0.022** |
| subNTSX | 15% | 25% | 35% | 1.1300 | 0.9998 | 1.1587 | −0.059 / −0.004 / **+0.024** |
| subKMLM | 25% | 25% | 25% | 1.0869 | 0.9939 | 1.1789 | −0.102 / −0.010 / **+0.044** ⭐ |

**Iter 023 baseline**: lh_56y=1.189, vt_real=1.004, ndx_real=1.135. **All 3 sub sources beat iter 023 on ndx_real (1/3 datasets).** subKMLM produces the strongest ndx_real edge (+0.044, larger than Phase 1A's +0.032).

## Phase 1A vs Phase 1B comparison

| metric | Phase 1A iter 030 best (`spmo_lite`, 5%, balanced sub) | Phase 1B iter 036 best (`spmo10_subGDE`, 10%, sub GDE) | Phase 1B max-ndx (`spmo10_subKMLM`, 10%, sub KMLM) |
|---|---|---|---|
| Sharpe lh_56y | 1.117 | 1.161 | 1.087 |
| Sharpe vt_real | 1.009 | 0.987 | 0.994 |
| Sharpe ndx_real | 1.167 | 1.157 | **1.179** |
| Δ vs iter 023 | −0.072 / +0.005 / +0.032 | −0.028 / −0.017 / +0.022 | −0.102 / −0.010 / +0.044 |
| Datasets beating 023 | 2/3 | 1/3 | 1/3 |

Phase 1B `subGDE` at 10% **substantially improves lh_56y (+0.044)** vs Phase 1A best (1.117 → 1.161). But it loses Phase 1A's cosmetic vt_real +0.005 edge and ndx_real edge drops slightly (+0.032 → +0.022).

Phase 1B `subKMLM` at 10% **maximizes ndx_real edge (+0.044, larger than Phase 1A's +0.032)** at the cost of lh_56y −0.102 (worst across Phase 1B SPMO sub sources). Same KMLM-cost pattern as iters 033/034/035.

## Lesson

**KILL #1 SURVIVES under all 3 sub sources. ndx_real +signal CONFIRMED ROBUST across substitution patterns.** SPMO is the **only** Phase 1A/1B sleeve to produce ndx_real +signal under every reallocation tested.

- **Phase 1B reaffirms SPMO as the single most-promising sleeve in the entire Phase 1 sweep.** ndx_real +signal is structural (cross-sectional momentum on QQQ universe), not substitution-source artifact. Range across 6 SPMO configs (Phase 1A 4 + Phase 1B 3 minus duplicates): +0.022 to +0.044.
- **Trade-off matrix per sub source**:
  - `subGDE` (selected by run_iter): best lh_56y/vt_real preservation; ndx_real +0.022 (smallest Phase 1B SPMO edge)
  - `subKMLM`: maximizes ndx_real edge (+0.044) but worst lh_56y (−0.102)
  - `subNTSX`: middle ground; lh_56y −0.059, ndx_real +0.024
- **Phase 2 candidate selection**:
  - Phase 1A `spmo_lite` (5% SPMO, balanced sub) remains the highest 2/3-dataset config (+0.005 vt_real cosmetic + +0.032 ndx_real). Best blend.
  - For F2 US Factor-only / F3 US Hybrid: **SPMO at 5-10% is the strongest single Phase 1 finding**.
  - subGDE 10% is the best lh_56y-preserving variant; subKMLM 10% is the ndx_real maximizer.
- Citation `[stocks_on_the_move, p.21-30]` Clenow + Jegadeesh-Titman 1993 confirmed empirically robust: the +signal is invariant to substitution-source choice in this configuration space.
