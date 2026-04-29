# Iter 017 — Final report: B.6 — VBRSIM regime-gated factor tilt

**Date**: 2026-04-28
**Slug**: `B6-VBRSIM-regime-gated`
**Selected config**: `vbrsim_value` = signal `VBRSIM 36m Sharpe > 0.5`, weights ON {35% NTSX + 25% GDE + 25% VBRSIM + 15% KMLM} / OFF {35% NTSX + 25% GDE + 0% VBRSIM + 40% KMLM}
**Selection rule**: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets

## Verdict

**Tier**: 🥇 **STRONG** (score **82/100**, 5/5 winner conds met but only 17/25 on gates).

**Beats incumbent**: ❌ **`false`** — both mechanically (score 82 < 93) AND substantively (loses iter 011 by −0.075 / −0.074 / −0.135 strict).

**KILL #1 fired** (partial→ effective): best-of-grid loses iter 011 substantively on 2/3 datasets AND fails to match iter 013's constant-weight +0.080 lh_56y advantage (iter 017 is +0.003 vs iter 013's +0.080 on lh_56y loose).

## Headline metrics

| dataset | gross S (loose) | strict | edge vs avg(SPY,VT) | Δ vs iter 011 (strict) | Δ vs iter 013 (loose) | gates | pct_on |
|---|---:|---:|---:|---:|---:|---:|---:|
| lh_56y    | **1.043** | **0.970** | +0.372 | **−0.075** | −0.083 | 5/7 | 74% |
| vt_real   | **0.884** | **0.886** | +0.177 | −0.074 | −0.039 | 6/7 | 62% |
| ndx_real  | **0.967** | **0.969** | +0.044 | −0.135 | −0.108 | 6/7 | 61% |

Net = Gross (dynamic gate but sleeve flips < 1× quarterly; AnnualDarfEngine remains tax-neutral on gross daily Sharpe).

## Comparison vs iter 013 (constant-weight VBRSIM, the natural baseline)

| dataset | iter 017 (gated) | iter 013 (constant) | Δ |
|---|---:|---:|---:|
| lh_56y    | 1.043 | 1.126 | **−0.083** |
| vt_real   | 0.884 | 0.923 | **−0.039** |
| ndx_real  | 0.967 | 1.075 | **−0.108** |

**Regime gate makes things WORSE than constant-weight on every dataset.**
The signal flips contaminate the equity curve — turning ON when momentum
is positive (chasing recent winners) and OFF when momentum turns negative
(by then the value-cycle drag has already happened). Classic
"regime-gate-on-existing-winner" DSR-regression trap.

## Per-config grid

| config | signal | lh_56y S | vt_real S | ndx_real S | pct_on (avg) |
|---|---|---:|---:|---:|---:|
| `vbrsim_mom12` | 12-1m return > 0 | 1.012 | 0.830 | 0.884 | 72% |
| `vbrsim_value` ✅ | 36m Sharpe > 0.5 | **1.043** | **0.884** | **0.967** | 66% |
| `vbrsim_dual` | mom12 OR value | 1.004 | 0.832 | 0.885 | 85% |

The `dual` signal (most permissive — ON 85% of the time) approaches
constant-weight behavior but underperforms `value` on all 3 datasets. The
`mom12` signal is the most reactive but performs worst on live windows.

**No signal recovers the iter 013 constant-weight performance.** Gate
addition is pure cost.

## Pre-committed kill criteria

| KILL | criterion | status |
|---|---|---|
| **#1** | Best-of-grid loses iter 011 on ≥2/3 AND fails iter 013 +0.080 lh_56y advantage | **✅ FIRES**: loses iter 011 on 3/3 strict; lh_56y −0.075 strict (no advantage). |
| **#2** | DSR-regression trap (PBO > 0.5 on all 3) | **NOT fully fired**: PBO 0/0/0 nominal but **N=3 configs triggers framework warning** (CSCV statistically unstable below N=4). PBO numbers are not informative here; the substantive degradation vs iter 013 is the real signal. |

KILL #1 fires → **B.6 regime-gated factor tilt is closed (DE-017).**

## Score breakdown

| # | criterion | iter 017 / max |
|---|---|---:|
| 1 | Sharpe edge vs avg(SPY,VT) | **25 / 25** |
| 2 | Gates | **17 / 25** (lh_56y 5/7, vt 6/7, ndx 6/7, no cross-ds bonus) |
| 3 | DSR | **15 / 15** (worst p=2.05e-3) |
| 4 | CAGR floor | **10 / 15** (lh_56y ✓, vt ✓, ndx ✗) |
| 5 | MDD ceiling | **15 / 15** |
| 6 | Robustness | **0 / 5** (rolling-5y Sharpes more volatile than iter 011/016 — pct_pos drops below 90%) |
| **total** | | **82 / 100** |

## Gate detail (selected `vbrsim_value`)

lh_56y: G1 PBO ✓, G2 ✓, **G3 WF ✗** (max win MDD 26.39% > 25%), G4 ✓, G5 ✓, G6 ✓, G7 ✓. **Robustness 0/5**: regime-gated returns are choppier than static stack.

## Lesson — DE-017

Regime-gating on a single existing-winner factor (VBRSIM) **does not recover
the dormant value premium** in this universe. Three reasons:

1. **Signal lag**: 36m Sharpe / 12-1m return signals turn ON ~6-12m after
   the regime starts, missing the early premium reset.
2. **Whipsaw cost**: each ON→OFF→ON transition is a portfolio rebalance
   that incurs implementation cost (zero in the abstract; +5-15bp/yr in
   practice via DARF if held in a taxable account).
3. **Regime classification noise**: with only ~30y of data, 36m Sharpe
   estimates have wide CIs; the gate fires on noise.

This is the canonical "regime gate on existing winner" trap that PBO
discipline (López de Prado p.208-211) was designed to detect. The PBO
gate doesn't fire because N=3 is too small for CSCV (the framework's own
warning). The substantive degradation vs iter 013 IS the answer:
adding ~50bp of complexity (the gate) costs −80bp of gross Sharpe on
lh_56y. The simpler constant-weight iter 013 was already a tier-WINNER
that didn't substantively advance iter 011; gating it doesn't help.

**Family-level conclusion**: B-direction is now **fully closed end-to-end**:
- B.4 constant-weight VBRSIM (iter 013): tier WINNER but no advance vs iter 011
- B.5 UMD overlay direct (iter 016): **WINNER tier 91/100, FIRST POSITIVE SIGNAL — only B-direction with a real edge**
- B.6 VBRSIM regime-gated (iter 017): STRONG, worse than B.4 constant-weight

The only B-direction with a genuine substantive edge is **B.5 (UMD overlay)**.

## Citations

- PBO/DSR discipline: `[advances_fin_ml, p.208-211, p.222-223]`
- Time-series momentum signal: `[stocks_on_the_move, p.21-30]`
- Capital-efficient stacking core: `[risk_parity, ch.5, p.10]`

## Next directions

iter 017 closes B.6. Continuing with breadth queue:
- iter 018 — C.1 Antonacci GEM cross-class top-K (qualitatively different mechanism)
- iter 019-022 — continue C-direction breadth.

After 016-022, the Pareto frontier should be clear. As of iter 017: only
iter 016 (UMD overlay) is a substantive positive vs iter 011.

*Generated 2026-04-28 by long_term_portfolio loop iter 017.*
