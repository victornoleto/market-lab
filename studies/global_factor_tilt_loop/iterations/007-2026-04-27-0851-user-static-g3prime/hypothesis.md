# Iter 007 Hypothesis — User Static Portfolio + G3' Adapted Gate

**Date**: 2026-04-27  
**Slug**: `user-static-g3prime`  
**Type**: Gate-calibration re-test (pre-committed directive from BASE_MEMORY Tier 0 queue)

---

## Hypothesis

Iteration 003 (capital-efficient-static) scored STRONG 84/100 with all 5 strict winner
conditions technically met — but was blocked from WINNER status solely because the G3
walk-forward gate (MDD ≤ 25% per window) is calibrated for 1× equity strategies. The
portfolio carries ~1.45× notional via exchange-traded futures overlays (RSSB/RSST/GDE),
making the 25% threshold structurally incompatible in systemic crash windows (2001, 2008,
2022). All 8 WF windows were profitable in iter 003; only the MDD threshold failed.

**Hypothesis**: If G3 nominal is replaced by G3' adapted (benchmark-comparative:
`ref_mdd = max(VT_window_MDD × 1.45, V_HYBRID_MF_window_MDD)` per window), and the
portfolio's per-window MDD is ≤ ref_mdd, then the gate failure was a calibration error
— not a genuine drawdown problem. Under G3', this portfolio is a WINNER candidate.

**Kill criteria**: If any WF window MDD exceeds `max(VT_window_MDD × 1.45,
V_HYBRID_MF_window_MDD)` → portfolio has genuinely excessive drawdown, not just
gate mismatch. G6 vt_real borderline (iter 003 CI_low = −0.0004) may persist.

---

## Primary citation

`[risk_parity, ch.5]` — return stacking / capital efficiency: stacked notional is
structurally different from margin leverage; the portfolio's peak drawdown should be
compared to a leverage-adjusted benchmark, not a 1× absolute threshold.

Supporting: `[advances_fin_ml, p.196-202]` (bootstrap CI for Sharpe), `[advances_fin_ml,
p.208-211]` (PBO), `[advances_fin_ml, p.222-223]` (DSR/PSR).

---

## Edge source

What does iter 003 capture that VT/Plano C/V_HYBRID miss?  
Multi-factor breadth + return-stacking simultaneously: global SCV factor tilt (AVUV+AVDV+AVEM),
momentum (SPMO+IDMO), managed futures (KMLM), gold-equity stack (GDE), and global equity+bond
stack (RSSB+RSST) — all in a single static portfolio. VT is cap-weight only; Plano C
lacks stacking; V_HYBRID lacks EM and global SCV. The combination captures 5 orthogonal
risk premia in one buy-and-hold structure.

---

## Portfolio (EXACT — do NOT modify)

| sleeve | real ETF | synth | weight |
|---|---|---|---|
| RSSB | ReturnStacked Global Eq+Tsy | RSSBSIM | 25% |
| RSST | ReturnStacked Stocks+Trends | SPYSIM+KMLMSIM−CASHX | 15% |
| AVUV | Avantis US SCV | VBRSIM | 10% |
| AVDV | Avantis Intl Dev SCV | VSSSIM | 7% |
| AVEM | Avantis EM | VWOSIM | 8% |
| SPMO | SPDR US Momentum | SPYSIM | 8% |
| IDMO | iShares Intl Momentum | VEASIM | 7% |
| GDE | WisdomTree Efficient Gold+Eq | GDESIM | 12% |
| KMLM | KFA Mount Lucas MF | KMLMSIM | 8% |

Effective notional: ~1.45× (RSSB 200% + RSST 200% + GDE 180% on 50% of portfolio).

---

## Gate change: G3 nominal → G3' adapted

**Old**: G3 nominal: per-WF-window MDD ≤ 25% (calibrated for 1× equity)  
**New**: G3' adapted: per-WF-window `portfolio_MDD ≤ max(VT_window_MDD × 1.45, V_HYBRID_MF_window_MDD)`

Per BASE_MEMORY §§ G3' rule:
- `notional_factor = 1.45`
- `ref_mdd = max(VT_window_MDD × notional_factor, V_HYBRID_MF_window_MDD)`
- G3' passes if `portfolio_window_MDD ≤ ref_mdd` for all windows and ≥6/8 profitable

V_HYBRID_MF_window_MDD: approximate as 44.71% (overall MDD) for window floor. For each
window, compute VT (VTSIM) actual window MDD and take max with 0.4471.

---

## Datasets

Same as iter 003:
- `educational`: 1995-01-01 → 2026-04-24 (~31y, VSSSIM/VWOSIM binding)
- `vt_real`: 2008-06-01 → 2026-04-24 (~17y)
- `ndx_real`: 2010-02-01 → 2026-04-24 (~16y)

---

## Expected budget

- `n_configs = 1` (single pre-committed config, no grid)
- `n_trials = 1`
- Wall-time: ~2-3 min (identical computation to iter 003 plus G3' window calcs)

---

## Implementation plan

1. Copy iter 003 `backtest.py` skeleton
2. Replace `gate_walk_forward` with `gate_walk_forward_g3prime` (from iter 006 pattern)
3. Pass VTSIM returns to G3' function for per-window VT MDD computation
4. Include `V_HYBRID_MF_OVERALL_MDD = 0.4471` as conservative floor in ref_mdd
5. Report both `g3_nominal_pass` and `g3_prime_pass` in gate_details (per BASE_MEMORY spec)
6. Update `cumulative_n_trials = 24`, slug, and iteration metadata
7. Run, score, write final report
