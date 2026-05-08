# Iter 018 — Final report: C.1 — Antonacci GEM cross-class top-K momentum

**Date**: 2026-04-28
**Slug**: `C1-Antonacci-GEM`
**Selected config**: `gem_6asset_K2` = SPY/QQQ/EFA(VEA)/TLT/GLD/KMLM, K=2 monthly top-K, abs-mom fallback KMLM

## Verdict

**Tier**: 🥈 **PROMISING** (score **74/100**, **winner_conditions_met=FALSE**) — fails Sharpe-edge gate (only 1/3 datasets +0.10 vs avg(SPY,VT)).

**Beats incumbent**: ❌ false on every dimension.

**KILL #1 fired**: best-of-grid loses iter 011 substantively on 2/3 datasets.

## Headline metrics

| dataset | gross S | edge vs avg(SPY,VT) | Δ vs iter 011 | gates |
|---|---:|---:|---:|---:|
| lh_56y    | 0.763 | +0.092 ⚠️ | **−0.283** | 5/7 |
| vt_real   | 0.888 | +0.182 ✓ | −0.072 | 7/7 |
| ndx_real  | 0.889 | −0.035 ✗ | **−0.215** | 6/7 |

Only vt_real clears the +0.10 edge (the 2008 crisis where GEM rotated to TLT
boosts vt_real). Sharpe-edge winner condition requires ≥2/3 — FAILS.

## Per-config grid

| config | universe | K | fallback | lh_56y | vt_real | ndx_real |
|---|---|---:|---|---:|---:|---:|
| `gem_5asset_K2` | SPY/QQQ/VEA/TLT/GLD | 2 | TLTSIM | 0.771 | 0.753 | 0.732 |
| `gem_6asset_K2` ✅ | + KMLM | 2 | KMLMSIM | 0.763 | **0.888** | **0.889** |
| `gem_5asset_K3` | SPY/QQQ/VEA/TLT/GLD | 3 | TLTSIM | 0.750 | 0.824 | 0.804 |
| `gem_7asset_K2` | + EEM | 2 | KMLMSIM | 0.755 | 0.847 | 0.833 |

Adding KMLM (gem_6asset) helps vt/ndx via crisis-alpha; adding EEM (gem_7asset)
slightly hurts (EM regime mismatch).

## Why GEM fails here vs iter 079 archive (Sharpe 1.094)

iter 079 was a strict 5/5 winner in `_archive/strategy_hunt_loop`. Why is iter 018 worse?

1. **Universe**: iter 079 tested 8-12 asset universes including more equity diversifiers (factors, sectors); iter 018 has only 5-7 broad asset classes.
2. **Window**: iter 079 evaluated on Tiingo SPY 17y (=vt_real era); iter 018 includes lh_56y 1986+ where long stretches of equity dominance penalize monthly switching.
3. **Lookback**: iter 079 may have used a different lookback (1m, 3m, 6m) — iter 018 uses 12-1m (Antonacci classic).
4. **Whipsaw cost**: iter 018's monthly switching incurs decision noise that static iter 011 avoids in 2010-2024 single-regime period.

## Pre-committed kill criteria

| KILL | criterion | status |
|---|---|---|
| **#1** | Best-of-grid loses iter 011 on ≥2/3 | **✅ FIRES** (loses lh_56y −0.283, ndx_real −0.215) |
| **#2** | K=1 dominates K=2,3 | **NOT TESTED** (only K=2,3 in grid; K=1 not pre-committed) |

KILL #1 fires → **C.1 Antonacci GEM in this universe is closed (DE-018).**

## Lesson

Cross-class top-K monthly momentum **does NOT beat static cap-efficient
stack iter 011** in the testfolio universe + lh_56y window. Three reasons:

1. **Equity-dominant regimes punish switching**: 2010-2024 was 14y of US-equity dominance; GEM rotated correctly into SPY but fees of monthly checks (whipsaw + DARF) eat the gross edge.
2. **Long-history reveals weakness**: iter 011's 1.046 lh_56y dominates GEM's 0.76 by a wide margin because static stacks with KMLM crisis-alpha capture the same regime-protection without monthly decision noise.
3. **vt_real-only positive**: vt_real (2008-2026) has the GFC + 2020 crash + 2022 rate hike — three distinct regime shifts where GEM's switching helps. The 17y window is too narrow to generalize.

**Next iter directions**: C.2 vol-managed 60/40 (different mechanism — risk-target instead of momentum-rotation).

## Citations

- `[stocks_on_the_move, ch.6, p.21-30]` Clenow cross-sectional momentum
- Antonacci 2014 *Dual Momentum Investing* (textbook GEM)
- `[risk_parity, ch.5]` static-stack alternative
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`

*Generated 2026-04-28 by long_term_portfolio loop iter 018.*
