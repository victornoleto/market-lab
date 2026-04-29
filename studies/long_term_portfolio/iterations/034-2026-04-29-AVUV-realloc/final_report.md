# Iter 034 — Final Report — `AVUV-realloc`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 86/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **STRONG 86/100** — `winner_conditions_met=True`.

**Primary citation**: [risk_parity, ch.2, p.37-41]

---

## Selected config: `avuv10_subGDE`

Weights:

```json
{
  "NTSXSIM": 0.25,
  "GDESIM": 0.15,
  "KMLMSIM": 0.35,
  "TLTSIM": 0.15,
  "AVUVSIM": 0.1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.168 | 10.96% | 20.07% | 7/7 | 1.31e-10 |
| **vt_real** | 0.975 | 9.34% | 16.51% | 6/7 | 5.74e-04 |
| **ndx_real** | 1.122 | 9.92% | 12.43% | 6/7 | 1.53e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| avuv10_subNTSX | 1.132 | 0.984 | 1.119 |
| avuv10_subGDE | 1.168 | 0.975 | 1.122 |
| avuv10_subKMLM | 1.083 | 0.968 | 1.133 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.168 | +0.488 | [OK] |
| vt_real | 0.900 | 0.950 | 0.975 | +0.075 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.122 | +0.222 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **AVUVSIM** = `VBRSIM + 75bps/y tilt premium`. INCOMPLETE — VBRSIM is passive small-cap value (no quality screen); 75bps tilt premium estimates Avantis active-management edge (size+value+profitability multifactor) per [risk_parity, ch.2, p.37-41]. Real AVUV live since 2019; synth long-history backfill assumes constant tilt premium.

## Substitution source comparison (fixed 10% AVUV weight)

| sub source | NTSX | GDE | KMLM | Sharpe lh_56y | Sharpe vt_real | Sharpe ndx_real | Δ vs iter 023 |
|---|---:|---:|---:|---:|---:|---:|---|
| **subGDE** *(best, selected)* | 25% | 15% | 35% | 1.1681 | 0.9753 | 1.1219 | −0.021 / −0.029 / −0.013 |
| subNTSX | 15% | 25% | 35% | 1.1324 | 0.9841 | 1.1194 | −0.057 / −0.020 / −0.016 |
| subKMLM | 25% | 25% | 25% | 1.0832 | 0.9683 | 1.1327 | −0.106 / −0.036 / −0.002 |

**Iter 023 baseline**: lh_56y=1.189, vt_real=1.004, ndx_real=1.135. **All 3 sub sources beat iter 023 on 0/3 datasets.**

## Phase 1A vs Phase 1B comparison

| metric | Phase 1A iter 028 best (`avuv_lite`, 5%, sub NTSX+KMLM 50/50) | Phase 1B iter 034 best (`avuv10_subGDE`, 10%, sub GDE) |
|---|---|---|
| Sharpe lh_56y | 1.116 | 1.168 |
| Sharpe vt_real | 0.996 | 0.975 |
| Sharpe ndx_real | 1.140 | 1.122 |
| Δ vs iter 023 | −0.074 / −0.008 / +0.005 | −0.021 / −0.029 / −0.013 |
| Datasets beating 023 | 1/3 (cosmetic) | 0/3 |

Phase 1B `subGDE` at 10% **substantially improves lh_56y (+0.052)** vs Phase 1A best — the cleanest sub-source improvement in Phase 1B for any sleeve. But it loses the cosmetic +0.005 ndx_real edge that Phase 1A had, and degrades vt_real (−0.021). Net: closer to iter 023 on lh_56y but no positive Δ on any dataset.

## Lesson

**KILL #1 (no-positive-config) ✅ FIRED** under all 3 sub sources. No config beats iter 023 on any dataset (criterion ≥1/3). Phase 1B's `subGDE` recovered most of the lh_56y gap but at the cost of the cosmetic ndx_real edge that Phase 1A produced.

- **Best sub source**: `subGDE` lh_56y 1.168 — substantially closer to iter 023 (1.189) than Phase 1A's 1.116. Substitution from GDE (gold-leveraged) is least costly on long-history because GDE's gold leg has weaker correlation with AVUV's SCV factor than KMLM's CTA does.
- **Worst sub source**: `subKMLM` lh_56y 1.083 (Δ−0.106). Same pattern as iter 033: cutting KMLM is structurally costly on long-history.
- **vt_real** all 3 sub sources cluster within 0.016 — sub-source has minimal effect on live windows.
- **AVUV sleeve subordinate to iter 023 across all sub sources.** Although subGDE gets close to parity on lh_56y, it never crosses the +signal threshold. F2 US Factor-only (iter 033 in original SWEEP_PLAN) probability remains low — at 1× notional AVUV cannot beat 1.5×-leveraged iter 023.
- For Phase 2 hybrid construction, AVUV at 5% in F3 US Hybrid (iter 034 of original sweep) remains plausible per Phase 1A's marginal cosmetic edge. The Phase 1B finding **does not re-open the AVUV sleeve as a winner candidate.**
- Citation `[risk_parity, ch.2, p.37-41]` Fama-French SCV framework is honest; the issue is the post-2008 "death of value" regime that lh_56y partially captures.
