# Phase 3.5b-addendum — Operational variants (sub-index)

> **Path tag:** `[SWING BROKER]` (Plano B, BR stock broker, 15% IR, swap = 0).
> **Scope:** 3 user-driven operational "what if" investigations on top of the
> Phase 3.5b winner. None of these replace the production default — every
> result runs end-to-end and tags gate failures as ⚠️ FLAGs in its per-variant
> `flags.md`, per `specs/phase_3_5b_addendum_operational.md` §0.
> **Reference baseline:** `../portfolio_3leg_ew/summary.json` — 3-leg EW
> {LETF 2× + QQQ + GLD}, daily rebal, CAGR 25.56%, Sharpe **2.108**,
> MaxDD **10.86%** over 21.36 yrs (2004-11-18 → 2026-04-14).

## All-in comparative table

`Sharpe` / `MaxDD` in **bold** when they dominate the 3-leg winner. ⚠️ flags
are breached gates per the per-variant `flags.md`.

| # | Variant | Window (yrs) | CAGR | Sharpe | MaxDD | Vol ann. | IR vs SPY | Gates failed | Available in BR broker? | Recommended? |
|---|---|---|---|---|---|---|---|---|---|---|
| **W** | **3-leg EW {LETF+QQQ+GLD} daily** (winner) | 21.36 | 25.56% | **2.108** | **10.86%** | 11.10% | 0.722 | none | yes | **YES — prod default** |
| A | 2-leg EW {LETF+QQQ} daily | 24.87 | 31.59% | 1.888 | 14.41% | 15.16% | 1.158 | ⚠️ DR 1.121 < 1.20 | yes (drops GLD) | only if broker blocks GLD |
| B-1 | LETF 2× only (EMA100/0%) | 56.3 | 44.69% | 1.848 | 20.55% | 21.23% | **1.601** | none | yes (SSO since 2006) | as _sleeve_, not standalone |
| B-2 | LETF 2.5× synthetic | 56.3 | 58.89% | 1.882 | 24.65% | 26.48% | 1.837 | ⚠️ SYNTHETIC (no ETF); ⚠️ WF1 margin 0.35 pp | **no real ETF** | no — theory only |
| B-3 | LETF 3× | 56.3 | 74.17% | 1.910 | 28.45% | 31.72% | 1.963 | ⚠️ MaxDD 28.45% > 25%; ⚠️ WF gate 5/8 (breach WF1/WF2/WF7) | yes (UPRO since 2009) | only as escalation lever |
| C-1 | 3-leg EW + monthly_sell | 21.36 | 23.79% | 1.964 | 10.94% | 11.19% | — | — | yes | worse than daily by ~0.14 Sharpe + $30 k / yr IR |
| C-2 | 3-leg EW + monthly_cashflow $500 / mo | 21.36 | 40.47%* | 1.944 | 17.78% | 18.36% | — | — | yes | no — max drift 65% |
| C-3 | 2-leg EW + monthly_cashflow $500 / mo | 24.87 | 42.63%* | 1.881 | 18.15% | 19.96% | — | ⚠️ inherits 2-leg DR FAIL | yes | **yes** if DCA-ing and tax-averse |
| C-4 | 2-leg EW + monthly_sell | 24.87 | 29.94% | 1.800 | 14.46% | 15.20% | — | ⚠️ inherits 2-leg DR FAIL | yes | no — pays $145 k / yr IR |
| C-5 | 3-leg EW + threshold 5pp | 21.36 | 24.66% | 2.002 | 11.10% | 11.34% | — | — | yes | **yes** if daily rebal is operationally prohibitive (1.3 DARFs/yr, 95% of daily Sharpe) |
| C-6 | 3-leg EW + threshold 10pp | 21.36 | 25.47% | 1.990 | 11.12% | 11.76% | — | — | yes | aggressive-low-DARF fallback (0.6 DARFs/yr, 94% of daily Sharpe) |

*Cashflow CAGR is inflated by $6 k / yr of external deposits compounding
inside the equity curve. It is **not** pure-return alpha and is not
directly comparable to deposit-free modes; use Sharpe and MaxDD for
judgement. The daily mode on either blend is deposit-free by construction.

## Reading the table

- **W** is the published Phase 3.5b winner; every other row is a variant
  to be compared against it on Sharpe, MaxDD, and operational feasibility.
- **A** drops GLD. Sharpe moves from 2.108 to 1.888 (−0.22) and MaxDD
  from 10.86% to 14.41% (+3.55 pp). It also stops being genuinely
  diversified (DR 1.121 vs required 1.20 — both legs are long US equity).
  Deploy only if the broker does not offer GLD (or a synthetic gold ETF
  equivalent).
- **B-1/B-2/B-3** hold the EMA100/0%-band rotation and sweep the
  leverage factor on the synthetic SPX_TR series.
  Sharpe is essentially flat across the sweep (1.848 → 1.882 → 1.910),
  while MaxDD scales almost linearly (+4 pp per +0.5×). 2.5× has no live
  ETF to deploy in Brazil (would require a swap or a 2×+3× stack).
  3× trips the Phase 3 WF MaxDD ≤ 25% gate in 3 of 8 windows (WF1
  1970s, WF2 early 1980s, WF7 2018-2025) — see
  [`letf_leverage_comparison/README.md`](letf_leverage_comparison/README.md).
- **C-1…C-6** swap the rebalance cadence (daily → monthly_sell →
  monthly_cashflow $500 / mo → threshold_Xpp) on the 3-leg winner
  and, for calendar modes, the 2-leg Task A variant. The findings
  are detailed in [`rebalance_modes/README.md`](rebalance_modes/README.md)
  and [`rebalance_modes/threshold_sweep.md`](rebalance_modes/threshold_sweep.md).
  Core conclusions:
  - `monthly_sell` consistently drops Sharpe ~0.1 and leaks $30 k / yr
    (3-leg) or $145 k / yr (2-leg) in realised-gains IR; dominated
    by daily.
  - `monthly_cashflow` is tax-free by construction but grows drift
    unless deposit scales with equity. On 2-leg it preserves Sharpe
    (1.881 ≈ 1.888 daily) with only +3.74 pp MaxDD — the one non-daily
    calendar mode that survives as a realistic DCA pattern.
  - **`threshold Xpp` (C-5 / C-6, task C4 sweep)** are drift-triggered
    rebalances. At 5 pp they preserve **95% of daily Sharpe** (2.002 vs
    2.108) at just **1.31 DARFs/yr from the rebal layer** — a 9×
    reduction vs `monthly_sell` + materially cheaper tax bill. The
    recommended fallback when daily cadence is operationally
    impractical.

## Explainer — Diversification Ratio (DR)

Choueifaty & Coignard 2008 [`advances_fin_ml, p.310`]:

```
           Σᵢ wᵢ × σᵢ          (weighted-average leg volatility)
DR  =   ─────────────────
              σ_portfolio       (actual portfolio volatility)
```

- `DR = 1` iff all legs move in perfect lockstep (ρ = 1) — there is no
  vol compression; the portfolio is effectively a re-weighted single
  asset.
- `DR ≫ 1` iff legs decorrelate on the down-side — e.g. 3-leg EW with
  GLD anti-correlated to equity gives `DR ≈ 1.38` in-sample, `1.456`
  under HRP weights.
- Phase 3 A3c/A3d set the promotion gate at `DR ≥ 1.20` — 20% vol
  compression — as the signal that a multi-leg blend is *diversifying
  on a new factor*, not merely thickening exposure to the same one.
- 2-leg LETF+QQQ at `DR = 1.121` (full window) and `1.135` (IS) fails:
  Pearson ρ(LETF, QQQ) = 0.555 because both are long US equity; the
  blend buys a modest additive edge (~+0.11 Sharpe vs LETF-alone) but
  adds no factor diversification. Hence the 3-leg winner keeps GLD.

The full rationale lives in `letf_qqq_2leg_ew/flags.md`.

## Production recommendation

**Unchanged from Phase 3.5b main:** deploy the 3-leg EW
{LETF 2× + QQQ + GLD} winner with daily rebalance. The only addendum
variants worth considering in practice are:

1. **Escalate to 3× LETF leg** *only* with a hand-managed risk overlay
   (Kelly-fractional sizing < 0.5×, or regime-conditional entries that
   defuse WF1/WF2/WF7 breaches). Default position: do not. Every 0.5× of
   leverage buys ~15 pp of CAGR at the cost of ~4 pp of MaxDD, and
   Sharpe barely moves.
2. **Switch cadence to monthly_cashflow on 2-leg** *only* for a user
   doing $500 / mo DCA on a broker that does not offer GLD. Preserves
   Sharpe, stays tax-free at the rebal layer, accepts +3.74 pp MaxDD.
   Not an upgrade — an ergonomic fallback.
3. **Switch cadence to threshold 5-10 pp on 3-leg** *only* if daily
   rebalance is operationally prohibitive (too many DARFs, too much
   bookkeeping). Preserves 94-95% of daily Sharpe at 0.6-1.3 DARFs/yr
   from the rebal layer. Strictly dominates `monthly_sell` on both
   Sharpe and tax drag.

Everything else in this addendum is informational.

## Citations

- Naive EW (1/n) superiority vs Σ-based allocators:
  `[advances_fin_ml, p.298-299]`.
- Threshold rebalancing as institutional practice:
  `[advances_fin_ml, p.275-278]`.
- DR formula: `[advances_fin_ml, p.310]`.
- LETF synthetic formula & leverage grid:
  `[leverage_for_the_long_run, p.16-17, Table 8]`.
- Vol-drag scaling with L²: `[leverage_for_the_long_run, p.7-9]`.
- BR 15% IR on realised gains: `docs/investment-mandate.md` §4.
- WF MaxDD ≤ 25% gate: `docs/investment-mandate.md` §5 (Phase 3 B1c).

## Related jornadas

- [`../../../jornada/2026-04-17-2100-phase3.5b-addendum-task-a-2leg-letf-qqq.md`](../../../jornada/2026-04-17-2100-phase3.5b-addendum-task-a-2leg-letf-qqq.md) — Task A (2-leg DR FAIL).
- [`../../../jornada/2026-04-17-2130-phase3.5b-addendum-task-b2-letf-2_5x-synthetic.md`](../../../jornada/2026-04-17-2130-phase3.5b-addendum-task-b2-letf-2_5x-synthetic.md) — Task B2 (2.5× synthetic).
- [`../../../jornada/2026-04-17-2145-phase3.5b-addendum-task-b3-letf-3x.md`](../../../jornada/2026-04-17-2145-phase3.5b-addendum-task-b3-letf-3x.md) — Task B3 (3× WF FAIL).
- [`../../../jornada/2026-04-17-2200-phase3.5b-addendum-task-c1-rebalance-modes-module.md`](../../../jornada/2026-04-17-2200-phase3.5b-addendum-task-c1-rebalance-modes-module.md) — Task C1 (module).
- [`../../../jornada/2026-04-17-2215-phase3.5b-addendum-task-c2-rebalance-3leg.md`](../../../jornada/2026-04-17-2215-phase3.5b-addendum-task-c2-rebalance-3leg.md) — Task C2 (3-leg cadence).
- [`../../../jornada/2026-04-17-2230-phase3.5b-addendum-task-c3-rebalance-2leg.md`](../../../jornada/2026-04-17-2230-phase3.5b-addendum-task-c3-rebalance-2leg.md) — Task C3 (2-leg cadence).
- [`../../../jornada/2026-04-17-2245-phase3.5b-addendum-summary.md`](../../../jornada/2026-04-17-2245-phase3.5b-addendum-summary.md) — Task D (this sub-index).
- [`../../../jornada/2026-04-17-2315-phase3.5b-addendum-task-c4-threshold-rebalance.md`](../../../jornada/2026-04-17-2315-phase3.5b-addendum-task-c4-threshold-rebalance.md) — Task C4 (threshold sweep).
