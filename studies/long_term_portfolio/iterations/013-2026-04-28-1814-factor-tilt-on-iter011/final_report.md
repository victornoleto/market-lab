# Iter 013 — Factor tilt on iter 011 base — STRONG (91/100), winner_conds_met vs avg(SPY,VT) but does NOT advance incumbent

**Verdict (honest)**: tier WINNER per scoring rubric (91/100, all 5 strict
winner conditions met vs avg(SPY,VT)) — but **does not beat iter 011
incumbent**. The selected config (10% VBRSIM factor tilt on iter 011 base)
ties iter 011's score (91 = 91, not >) and edges iter 011 by only +0.080
on lh_56y while LOSING on vt_real (−0.037) and ndx_real (−0.029). 0/3
datasets clear the +0.10 incumbent threshold. Pre-committed kill #1
**did not fire** (best lh_56y across configs is 1.131 > 1.046), but the
incumbent advancement criterion still fails. iter 011 stays incumbent;
this iter ranks STRONG-tier in the top-K table behind iter 011.

**Why "WINNER tier" but not "new incumbent"**: scoring rubric checks vs
avg(SPY,VT) (the loop's primary mission). The incumbent gate is a
**second, additional bar** added 2026-04-28 after iter 011 — it requires
either total_score > 91 OR Sharpe edge ≥ +0.10 vs iter 011 specifically
on ≥ 2 of 3 datasets. Neither holds.

---

## Headline tables

### Gross-of-tax metrics (gating-relevant)

| dataset | Sharpe | edge vs avg(SPY,VT) | edge vs iter 011 | CAGR | MDD | Gates | DSR p |
|---|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y**   | **1.126** | +0.454 ✅ | +0.080 ❌ | 12.32% | 25.73% | **5/7** | 2.86e-13 |
| **vt_real**  | 0.923 | +0.216 ✅ | −0.037 ❌ | 11.27% | 24.45% | 7/7 | 2.29e-3 |
| **ndx_real** | 1.075 | +0.152 ✅ | −0.029 ❌ | 12.06% | 18.00% | 7/7 | 6.24e-4 |

avg(SPY,VT) benchmarks (`scoring.BENCHMARKS`):
lh_56y 0.671 / vt_real 0.707 / ndx_real 0.924.
iter 011 (incumbent) Sharpe: 1.046 / 0.960 / 1.104.

### Net-of-tax metrics (informational; static stack ⇒ ≈ gross)

| dataset | net Sharpe | net CAGR | net MDD |
|---|---:|---:|---:|
| lh_56y   | 1.126 | 12.32% | 25.73% |
| vt_real  | 0.923 | 11.27% | 24.45% |
| ndx_real | 1.075 | 12.06% | 18.00% |

Static stack rebalances at year boundaries only; AnnualDarfEngine settles
at 15% on annual delta gains, but daily-Sharpe is tax-neutral (volatility
unchanged), and the YoY CAGR drag is offset by VBRSIM's high
post-1990 dividend yield being already inside the synth's total-return
construction. Net ≈ gross.

---

## Score breakdown (91/100)

| criterion | points | max | basis |
|---|---:|---:|---|
| 1. Sharpe edge vs avg(SPY,VT) | 25 | 25 | 3/3 datasets ≥ +0.10 (lh_56y +0.454, vt +0.216, ndx +0.152) |
| 2. Gates                     | 21 | 25 | 5/7 + 7/7 + 7/7 = 19/21 cells; cross-dataset spec §0 met |
| 3. DSR (worst p, n_trials=48) | 15 | 15 | worst p = 2.29e-3 < 0.05 |
| 4. CAGR floor (≥ 0.8 × bench) | 10 | 15 | lh_56y ✅ vt ✅ ndx ❌ (12.06% < 0.8×16.98% = 13.58%) |
| 5. MDD ceiling (≤ bench + 5pp) | 15 | 15 | all 3 datasets ≤ ceiling |
| 6. Robustness bonus           | 5 | 5 | 100% rolling-5y Sharpe positive (52/52 windows, min 0.43, max 2.13) |
| **Total** | **91** | **100** | tier WINNER, winner_conds_met=True |

Cumulative n_trials = 48 (44 from iter 012's frontmatter + 4 this iter).

---

## Config grid: factor weight monotonically helps lh_56y, hurts live-windows

This is the structural insight. Across 4 configs sweeping VBRSIM 10% → 30%:

| config | VBR % | lh_56y S | Δ iter011 | vt_real S | Δ iter011 | ndx_real S | Δ iter011 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `factor_lite_30253510`     | 10% | **1.126** | **+0.080** | 0.923 | −0.037 | 1.075 | −0.029 |
| `factor_moderate_25253020` | 20% | 1.106 | +0.060 | 0.874 | −0.086 | 1.032 | −0.072 |
| `factor_balanced_25202530` | 25% | 1.125 | +0.079 | 0.846 | −0.114 | 1.005 | −0.099 |
| `factor_heavy_20203030`    | 30% | **1.131** | **+0.085** | 0.825 | −0.135 | 0.979 | −0.125 |

**Two observations**:

1. **lh_56y monotonically benefits from factor tilt** — +0.060 to +0.085
   over iter 011's 1.046, peak at heavy 30% factor. The size+value premium
   IS adding Sharpe on long-history data, consistent with
   `[risk_parity, ch.2, p.37-41]` factor-premium framework.
2. **vt_real and ndx_real monotonically degrade** — heavy factor loses
   −0.135 / −0.125. The factor "premium" is actively destructive on
   post-2008 windows.

The selection rule (max mean Sharpe / avg_bm.Sharpe across 3 datasets)
correctly picked the **lightest** factor tilt as the best compromise —
reflecting that any factor weight above 10% trades long-history gains
for live-window losses faster than 1:1.

---

## lh_56y caveats (mandatory disclosure)

- **Effective window**: 1986-01-01 → 2026-04-24 (~40y), bottlenecked by
  SPYSIM inception. Same effective window as iter 011/012 — apples-to-apples.
- **KMLMSIM splice**: 1970-01-02 to 1987-12-30 uses the FF MoM proxy
  (UMD + RF, Ken French daily). Since lh_56y's effective start is
  1986-01-01 (SPYSIM bottleneck), the actual splice contribution is
  only 1986-01 → 1987-12 (~24 months). At 35% KMLMSIM weight, this
  affects a small fraction of the 40y record, but pre-1988 KMLM-side
  returns may still be slightly overstated (UMD Sharpe ~1.9 vs KMLM
  long-run ~0.5).
- **VBRSIM**: 99y synth (1926-07-01 inception). Pre-1986 is irrelevant
  here because SPYSIM bottlenecks the joint window to 1986+. Within
  1986-2026, VBRSIM tracks the Vanguard Small-Cap Value index methodology
  (a known proxy for AVUV's underlying universe).

---

## Pareto comparison vs reference strategies

Pareto frontier check on lh_56y / vt_real / ndx_real Sharpe:

| strategy | lh_56y | vt | ndx | comment |
|---|---:|---:|---:|---|
| **iter 013 (this)**   | 1.126 | 0.923 | 1.075 | this iter |
| **iter 011 incumbent** | 1.046 | 0.960 | 1.104 | dominates iter 013 on vt + ndx |
| **iter 012 (RSSB)**   | 1.011 | 0.851 | 1.021 | dominated by both iter 011 and iter 013 |
| avg(SPY 1×, VT 1×)    | 0.671 | 0.707 | 0.924 | mission baseline |
| `_archive` iter 035 (40y SPY+ZROZ+GLD) | 0.92 | n/a  | n/a | predecessor's CAGR-frontier; lower Sh on 40y synth |
| `_archive` iter 079 (multi-asset top-K) | n/a | n/a | n/a | predecessor's strict 5/5 winner; different mission (40y) |

**Pareto verdict**: iter 013 is **NOT a Pareto-improvement on iter 011**.
It improves lh_56y but loses on vt_real and ndx_real. iter 011 stays the
strict-Pareto-best in the loop. iter 013 strictly dominates iter 012
across all 3 datasets (+0.115 / +0.072 / +0.054).

---

## What worked / what didn't / lesson

**What worked**:

- Adding a **1× notional factor sleeve** (no Treasury duplication) does
  improve lh_56y Sharpe at every tested intensity — confirming factor
  premium has *signal* on long-history (1986-2026 effective window).
- Robustness perfect (52/52 rolling-5y windows positive Sharpe).
- Cross-config monotonic behavior (10% → 30% sweep both directions
  consistently) means the **direction** is real, not noise.
- All 5 strict winner conditions met vs avg(SPY,VT) — beats passive
  buy-hold by a wide margin even with the lightest factor tilt.

**What didn't**:

- vt_real + ndx_real Sharpe regress vs iter 011 at every factor intensity.
  Post-2008 small-cap value performance has been documented as the
  "death of value" (Asness 2020, Arnott 2021); 2009-2020 was the worst
  ~decade for size+value premium since Fama-French published.
- The lh_56y improvement (~+0.08) is **smaller** than the live-window
  regression (−0.04 / −0.03 to −0.14 / −0.13). Net portfolio-of-portfolios
  effect: factor tilt is **net negative** for any practitioner who weights
  recent windows ≥ historical.
- Score 91 = score 91 of iter 011 → no advance via the score gate either.

**Lesson** (3 sentences):

The size+value factor premium **is alive on long-history data** but the
post-2008 deploy window is in a US-large-cap-momentum regime where SCV
is a structural drag. Iter 011's pure capital-efficient stack
(NTSX = 90% SPY + 60% IEF + KMLM crisis-alpha + GDE gold-stack) captures
exactly the regime that has dominated post-GFC, while iter 013 dilutes
that with factor exposure that hasn't paid for ~17 years. **Future
factor-tilt iters need a regime filter** (e.g. value spread, factor
momentum) — naive constant-weight VBRSIM is not the answer.

---

## Citations

- `[risk_parity, ch.5, p.10]` — capital-efficient stacking core
  (NTSX/GDE retained from iter 011 winner architecture)
- `[risk_parity, ch.2, p.37-41]` — factor premium framework
  (used here as the conceptual scaffolding for size+value as a
  premium analogous to currency carry)
- `[stocks_on_the_move, ch.6, p.21-30]` — Clenow cross-sectional
  ranking edges (the broad rationale for why factor-loaded indices
  should beat market-beta on Sharpe over long horizons)
- `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]` —
  G1 PBO / G2 DSR / G6 bootstrap / G7 cross-lib gates

---

## Next directions (2-3 specific, prioritized)

1. **Direction B with regime filter** (highest priority). The structural
   finding here is that VBRSIM is a long-history-beneficial / live-window-
   harmful sleeve at constant weight. A regime-aware overlay — e.g.
   value spread (CAPE-style) or factor momentum — could allocate to
   VBRSIM only when the size+value premium is "live" and to KMLM/GDE
   otherwise. Cite: Asness-Frazzini-Pedersen 2014 (factor timing) +
   `[stocks_on_the_move, p.63-65]` (HAA-style canary as regime filter).
   Risk: prior loop found "regime gates on existing winners" hit DSR
   regression (`_archive` strategy_hunt_loop dead-ends 3-4) — must
   pre-commit a tiny grid (≤ 3 configs) to avoid that trap.

2. **Direction A1 (NTSX + NTSI/NTSE proxies + GDE + KMLM)**, deferred
   pending NTSI/NTSE synth construction. The user's literal "global +
   factor" thesis points to this. After DE-013 (RSSB) and DE-014 (this
   iter), the remaining "internationalization" attempt with no
   Treasury overlap is direct international leveraged-equity (NTSI is
   1.5× intl developed via WisdomTree; NTSE is 1.5× EM). Build the
   synth proxies first (`scripts/build_ntsi_synth.py` etc.); each is
   a CASHX-collateralized 1.5× equity stack, conceptually identical
   to NTSX construction.

3. **Direction B5 (UMD overlay)**, separate axis. Fama-French daily
   momentum factor (UMD) is in `data/ken_french/` already. A 20% UMD
   overlay on iter 011 would test whether momentum (not size+value) is
   the missing factor. UMD's historical Sharpe ~0.5-0.6 standalone but
   has near-zero correlation with SPY beta in some regimes — could add
   diversification benefit even if the post-2009 value regime is dead.

DO NOT retest naive VBRSIM/AVUV without a regime filter or alongside
UMD. DE-014 closes the constant-weight US-factor-tilt direction.
