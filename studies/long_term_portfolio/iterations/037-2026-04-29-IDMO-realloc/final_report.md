# Iter 037 — Final Report — `IDMO-realloc`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 81/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **STRONG 86/100** — `winner_conditions_met=True`.

**Primary citation**: [ilmanen_expected_returns, ch.19] + [stocks_on_the_move, p.21-30]

---

## Selected config: `idmo10_subGDE`

Weights:

```json
{
  "NTSXSIM": 0.25,
  "GDESIM": 0.15,
  "KMLMSIM": 0.35,
  "TLTSIM": 0.15,
  "IDMOSIM": 0.1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.138 | 10.65% | 18.85% | 7/7 | 4.42e-10 |
| **vt_real** | 0.934 | 8.79% | 17.04% | 6/7 | 1.08e-03 |
| **ndx_real** | 1.102 | 9.66% | 10.95% | 6/7 | 2.22e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| idmo10_subNTSX | 1.103 | 0.946 | 1.103 |
| idmo10_subGDE | 1.138 | 0.934 | 1.102 |
| idmo10_subKMLM | 1.066 | 0.945 | 1.129 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.138 | +0.458 | [OK] |
| vt_real | 0.900 | 0.950 | 0.934 | +0.034 | [--] |
| ndx_real | 0.900 | 0.950 | 1.102 | +0.202 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **IDMOSIM** = `VEASIM + 0.60 × UMD_KF − 60bps/y`. INCOMPLETE — uses **US** UMD_KF as proxy for intl momentum factor (per Asness-Moskowitz-Pedersen 2013, intl momentum has ~0.5-0.7 correlation with US momentum, so this synth may overstate the edge by 10-30%). 60bps/y reflects IDMO's higher TER vs SPMO. Real IDMO live since 2017 has Sharpe ~0.5-0.7.

## Substitution source comparison (fixed 10% IDMO weight)

| sub source | NTSX | GDE | KMLM | Sharpe lh_56y | Sharpe vt_real | Sharpe ndx_real | Δ vs iter 023 |
|---|---:|---:|---:|---:|---:|---:|---|
| **subGDE** *(best, selected)* | 25% | 15% | 35% | 1.1375 | 0.9339 | 1.1019 | −0.052 / −0.070 / −0.033 |
| subNTSX | 15% | 25% | 35% | 1.1028 | 0.9465 | 1.1034 | −0.086 / −0.058 / −0.032 |
| subKMLM | 25% | 25% | 25% | 1.0659 | 0.9453 | 1.1291 | −0.123 / −0.059 / −0.006 |

**Iter 023 baseline**: lh_56y=1.189, vt_real=1.004, ndx_real=1.135. **All 3 sub sources beat iter 023 on 0/3 datasets.**

## Phase 1A vs Phase 1B comparison

| metric | Phase 1A iter 031 best (`idmo_lite`, 5%, balanced sub) | Phase 1B iter 037 best (`idmo10_subGDE`, 10%, sub GDE) |
|---|---|---|
| Sharpe lh_56y | 1.107 | 1.137 |
| Sharpe vt_real | 0.984 | 0.934 |
| Sharpe ndx_real | 1.140 | 1.102 |
| Δ vs iter 023 | −0.082 / −0.020 / +0.005 | −0.052 / −0.070 / −0.033 |
| Datasets beating 023 | 1/3 (cosmetic) | 0/3 |

Phase 1B `subGDE` at 10% improves lh_56y (+0.030) but **loses Phase 1A's cosmetic ndx_real +0.005 edge entirely** (drops to −0.033) and degrades vt_real by 0.05.

## Lesson

**KILL #1 (no-positive-config) ✅ FIRES under all 3 sub sources.** IDMO sleeve closure REAFFIRMED. Phase 1A's cosmetic ndx_real edge does not survive the move from 5% balanced-sub to 10% any-sub.

- **Best sub source**: `subGDE` (selected). Same Phase 1B pattern: cuts GDE preserves long-history KMLM.
- **Worst sub source**: `subKMLM` (lh_56y −0.123). Same KMLM-cost pattern.
- **IDMO clearly subordinate to SPMO** at every sub source. Where SPMO at 10% subKMLM gives ndx_real **+0.044**, IDMO at 10% subKMLM gives only **−0.006** (−0.050 worse). The intl momentum factor is structurally weaker than US momentum in this configuration space (consistent with AMP 2013 intl momentum lower premium + IDMOSIM's USD-denominated US-UMD proxy weakness).
- **IDMO sleeve closure REAFFIRMED.** F5 Global Factor-only / F6 Global Hybrid both confirmed without IDMO contribution. SPMO is the only momentum sleeve worth carrying into Phase 2.
- Citation `[ilmanen_expected_returns, ch.19]` intl factor diversification + `[stocks_on_the_move, p.21-30]` Clenow are honest; the issue is intl momentum's structurally weaker premium (per AMP 2013) compounded by IDMOSIM's US-UMD proxy weakness.
