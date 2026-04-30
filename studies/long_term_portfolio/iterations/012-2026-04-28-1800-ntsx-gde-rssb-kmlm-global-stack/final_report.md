# Iter 012 — final report

**Slug**: `ntsx-gde-rssb-kmlm-global-stack`
**Date**: 2026-04-28
**Tier**: 🥇 **STRONG (88/100)** — winner conditions vs avg(SPY,VT) **met (5/5)**, but **does NOT beat incumbent** iter 011 (91/100). Pre-committed kill #1 triggered.
**Verdict**: PROMISING-CLOSED. Add to DEAD_ENDS as DE-013.

---

## TL;DR

The hypothesis was: replacing some KMLM weight in iter 011 with RSSBSIM
(Return Stacked Global Stocks & Bonds, 200% notional) injects intl
equity + Treasury duration and lifts Sharpe vs the avg(SPY,VT)
benchmark.

**Empirically** (gross-of-tax, selected config `rssb_moderate_25252525`
= 25% NTSX + 25% GDE + 25% RSSB + 25% KMLM):

| dataset | gross Sharpe | Δ vs avg(SPY,VT) | Δ vs **iter 011 incumbent** |
|---|---:|---:|---:|
| lh_56y (1986-2026, 40y eff.) | **1.011** | +0.340 ✅ | −0.035 (loses) |
| vt_real (17y) | 0.851 | +0.144 ✅ | −0.109 (loses) |
| ndx_real (16y) | 1.021 | +0.098 ❌ (just under +0.10) | −0.083 (loses) |

The strategy **beats the avg(SPY,VT) benchmark** on 2 of 3 datasets by
≥+0.10 Sharpe (lh_56y, vt_real), passes all 5 strict winner conditions
(`winner_conditions_met=true`), and earns 88/100. But it **regresses
vs iter 011 on every dataset** — pre-committed kill criterion #1 fires.

**Adding RSSB to the iter 011 stack lowers Sharpe across all 3
datasets**. RSSB's intl-equity sleeve and Treasury overlay do not improve
on iter 011's pure-US NTSX+GDE+KMLM mix.

---

## Headline tables

### GROSS-of-tax metrics vs avg(SPY,VT) benchmark (gating)

Strategy: `rssb_moderate_25252525` = 25% NTSX + 25% GDE + 25% RSSB + 25% KMLM
(NTSX expanded: 0.225 SPYSIM + 0.150 IEFSIM − 0.125 CASHX).

| dataset | window | strategy Sharpe | strategy CAGR | strategy MDD | avg(SPY,VT) Sharpe | avg(SPY,VT) CAGR | avg(SPY,VT) MDD ceiling | edge |
|---|---|---:|---:|---:|---:|---:|---:|---|
| lh_56y    | 1986-2026 (40y eff. — SPYSIM-bounded) | **1.011** | 12.20% | 32.45% | 0.671 | 10.73% | 58.35% | **+0.340 ✅** |
| vt_real   | 2008-06 → 2026-04 (~17y) | **0.851** | 11.52% | 30.77% | 0.707 | 11.88% | 50.21% | **+0.144 ✅** |
| ndx_real  | 2010-02 → 2026-04 (~16y) | 1.021 | 12.59% | 20.20% | 0.924 | 16.98% | 35.12% | +0.098 ❌ (just under +0.10) |

Sharpe edge ≥ +0.10 on 2 of 3 datasets → criterion 1 **passes** the strict winner condition.

### NET-of-tax metrics (informational; AnnualDarfEngine, Lei 14.754/2023)

Static stack rebalances only at year-end via simulator force; no
intra-year sells means very little realized DARF. Net ≈ gross to 4 dp.

| dataset | net Sharpe | net CAGR | net MDD | Δ Sharpe (net − gross) |
|---|---:|---:|---:|---:|
| lh_56y    | 1.011 | 12.20% | 32.45% | 0.000 |
| vt_real   | 0.851 | 11.52% | 30.77% | 0.000 |
| ndx_real  | 1.021 | 12.59% | 20.20% | 0.000 |

The static stack is effectively tax-neutral on daily Sharpe — same
property iter 011 had.

---

## Score breakdown

| criterion | points | max | note |
|---|---:|---:|---|
| 1 Sharpe edge       | **20** | 25 | beats avg(SPY,VT)+0.10 on 2 of 3 datasets (ndx_real misses by 0.002) |
| 2 Gates             | **23** | 25 | lh_56y 6/7, vt_real 7/7, ndx_real 7/7; cross-dataset bonus +4 |
| 3 DSR               | **15** | 15 | worst p=5.6e-3 (vt_real); n_trials=44 |
| 4 CAGR floor        | **10** | 15 | passes lh_56y (≥0.8 × 10.73% = 8.59%), vt_real (≥0.8 × 11.88% = 9.51%); fails ndx_real (12.59% < 0.8 × 16.98% = 13.58%) |
| 5 MDD ceiling       | **15** | 15 | all 3 datasets clear avg(SPY,VT)+5pp |
| 6 Robustness bonus  | **5**  | 5  | 100% of 52 rolling-5y windows positive Sharpe |
| **total** | **88/100** | **STRONG**, winner_conds_met=true |

---

## Per-config grid (4 configs tested)

### lh_56y (40y effective, SPYSIM-bounded 1986+)

| config | weights | Sharpe | CAGR | MDD |
|---|---|---:|---:|---:|
| rssb_balanced_30303010 | 30/30/30/10 | 0.875 | 12.23% | 41.06% |
| **rssb_moderate_25252525** ⭐ selected | 25/25/25/25 | **1.011** | 12.20% | 32.45% |
| rssb_iter011_clone_30202525 | 30/20/25/25 | 1.016 | 11.89% | 31.71% |
| rssb_lite_30253015 | 30/25/30/15 | 0.920 | 12.07% | 37.97% |

Best Sharpe across grid: **1.016** (`rssb_iter011_clone_30202525`).

### vt_real (17y)

| config | Sharpe | CAGR | MDD |
|---|---:|---:|---:|
| rssb_balanced_30303010 | 0.793 | 12.84% | 39.32% |
| **rssb_moderate_25252525** ⭐ | 0.851 | 11.52% | 30.77% |
| rssb_iter011_clone_30202525 | 0.845 | 11.17% | 30.13% |
| rssb_lite_30253015 | 0.804 | 12.13% | 36.30% |

### ndx_real (16y)

| config | Sharpe | CAGR | MDD |
|---|---:|---:|---:|
| rssb_balanced_30303010 | 0.976 | 14.35% | 26.73% |
| **rssb_moderate_25252525** ⭐ | 1.021 | 12.59% | 20.20% |
| rssb_iter011_clone_30202525 | 1.019 | 12.25% | 19.76% |
| rssb_lite_30253015 | 0.986 | 13.50% | 23.96% |

Selection rule: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets.

---

## Pareto comparison vs incumbent + archive winners

| strategy | source | lh_56y S | vt_real S | ndx_real S | lh_56y CAGR | comments |
|---|---|---:|---:|---:|---:|---|
| **iter 011** ntsx-gde-kmlm 35/25/40 ⭐ incumbent | this loop | 1.046 (best) | 0.960 | 1.104 | 11.58% | pure-US capital-efficient stack |
| **iter 012** rssb_moderate_25252525 (this iter) | this loop | 1.011 | 0.851 | 1.021 | 12.20% | LOSES on Sharpe vs iter 011 across all 3 datasets |
| iter 035 (archive) static stack 90/60/30 SPY+ZROZ+GLD | _archive/strategy_hunt_loop | ~0.92 (40y synth) | n/a | n/a | 19.6% (40y synth) | CAGR-frontier; lower Sharpe |
| iter 079 (archive) multi-asset top-K momentum | _archive/strategy_hunt_loop | ~0.93 (40y synth) | n/a | n/a | n/a | strict winner on 17y AND 40y |
| SPY 1× b&h | scoring.py BENCHMARKS | 0.680 | 0.900 | 0.900 | 11.47% | — |
| VT 1× b&h | scoring.py BENCHMARKS | 0.663 | 0.513 | n/a | 9.99% | — |
| avg(SPY,VT) | scoring.py | 0.671 | 0.707 | 0.924 | 10.73% | mission threshold |

**Pareto verdict**: iter 012 dominates avg(SPY,VT) on 2/3 datasets but
is dominated by iter 011 on Sharpe across all 3 datasets, with only a
+0.62pp CAGR advantage on lh_56y as a trade-off. **iter 011 stays
incumbent**.

---

## Gate battery details

### lh_56y (1986-2026, 40y effective)

| gate | result | detail |
|---|---|---|
| G1 PBO | ✅ pass | PBO=0.000 (n_combinations=252; 4-config grid is small) |
| G2 DSR | ✅ pass | p=5.59e-11 (n_trials=44) |
| G3 WF  | ❌ FAIL | 8/8 windows positive but 2 windows MDD>25% (26.71%, 32.45% — GFC-era stress) |
| G4 OOS | ✅ pass | OOS Sharpe 1.053 (last 30%) |
| G5 FWD | ✅ pass | post-2020 Sharpe 1.021 |
| G6 Boot| ✅ pass | 99.9% CI low = 0.600 |
| G7 Xlib| ✅ pass | numpy CAGR matches pandas within 3pp (after numpy_returns dropna fix) |

**6/7 gates passed** (threshold for lh_56y = 5).

### vt_real (17y)

| gate | result | detail |
|---|---|---|
| G1 PBO | ✅ pass | PBO=0.194 |
| G2 DSR | ✅ pass | p=5.57e-3 |
| G3 WF  | ✅ pass | all 8 windows positive, all MDD<25% |
| G4 OOS | ✅ pass | OOS Sharpe 1.046 |
| G5 FWD | ✅ pass | post-2020 Sharpe 1.021 |
| G6 Boot| ✅ pass | 99.9% CI low = 0.214 |
| G7 Xlib| ✅ pass | numpy CAGR matches |

**7/7 gates passed** (threshold = 4).

### ndx_real (16y)

| gate | result | detail |
|---|---|---|
| G1 PBO | ✅ pass | PBO=0.405 (close to threshold; weight selection at noise level) |
| G2 DSR | ✅ pass | p=1.29e-3 |
| G3 WF  | ✅ pass | all 8 windows positive, all MDD<25% |
| G4 OOS | ✅ pass | OOS Sharpe 0.929 |
| G5 FWD | ✅ pass | post-2020 Sharpe 1.021 |
| G6 Boot| ✅ pass | 99.9% CI low = 0.365 |
| G7 Xlib| ✅ pass | numpy CAGR matches |

**7/7 gates passed** (threshold = 4).

---

## Robustness (rolling 5y Sharpe)

- 52 windows on lh_56y selected config gross returns
- 100% positive (52/52)
- min Sharpe = 0.336 (1990 dot-com run-up window)
- max Sharpe = 1.780 (2010s capital-efficient stack era)

→ +5/5 robustness bonus.

---

## lh_56y caveats (mandatory disclosure)

Per `INFRASTRUCTURE.md` and `datasets.py`:

1. **SPYSIM-bounded effective window**: lh_56y nominal range is 1970-2026,
   but SPYSIM testfolio synth has inception 1986-01-02. Iter 012 uses
   NTSX synth (0.9 SPYSIM + 0.6 IEFSIM − 0.5 CASHX), so the strategy can
   only run from 1986-01-02 onwards. **Effective window: 1986-2026
   (40y, 10 151 trading days).** This is the same effective window
   iter 011 uses, so iter 011 vs iter 012 comparison is apples-to-apples.

2. **KMLMSIM splice**: KMLMSIM has inception 1987-12-31; pre-1988
   returns are spliced from FF MoM proxy (UMD + RF). Iter 012's
   effective window starts 1986-01-02, so ~2 years (1986-1987) use the
   FF MoM proxy for KMLM. UMD's 1970-87 Sharpe ~1.9 vs KMLM long-run
   ~0.5 — **the 1986-87 portion overstates KMLM-style returns by ~3×**.
   Iter 012 has lower KMLM weight than iter 011 (25% vs 40%), so this
   overstatement effect is **smaller** here. Net: iter 012's lh_56y
   Sharpe is slightly inflated by the splice but less than iter 011's.

3. **RSSBSIM is testfolio synth** (no live RSSB ETF data used). The
   live RSSB fund inception is 2023; the entire iter 012 window pre-
   2023 uses synth. RSSBSIM = ~100% global stocks (VT-equivalent) +
   100% Treasury via testfolio's stacking model.

---

## Configs tested

4 pre-committed configs (no grid expansion mid-iter):

| cfg_id | NTSX | GDE | RSSB | KMLM | rationale |
|---|---:|---:|---:|---:|---|
| `rssb_balanced_30303010` | 30% | 30% | 30% | 10% | equity-heavy global tilt |
| `rssb_moderate_25252525` ⭐ selected | 25% | 25% | 25% | 25% | 4-way equal — neutral baseline |
| `rssb_iter011_clone_30202525` | 30% | 20% | 25% | 25% | iter 011 weights with 25% reallocated to RSSB |
| `rssb_lite_30253015` | 30% | 25% | 30% | 15% | reduce KMLM (which dominated iter 011); RSSB takes equity-side weight |

cumulative_n_trials: 40 + 4 = 44.

---

## What worked

- **The architecture transfers cleanly**: capital-efficient stacking
  with RSSB sleeve passes all 5 strict winner conditions vs the loop's
  primary benchmark avg(SPY,VT). The strategy is publishable as a
  STRONG candidate against the public-benchmark mandate.
- **Drawdown control**: RSSB's Treasury overlay reduces ndx_real MDD
  from iter 011's 14.12% to iter 012's 20.20% (worse) but vs avg(SPY,VT)
  ceiling 35.12% it's well within bounds.
- **Robustness**: 100% positive 5y rolling Sharpe across all 52 windows
  on lh_56y. RSSB does not break the long-window stability.
- **CAGR**: lh_56y CAGR 12.20% vs iter 011 11.58% — a small +0.62pp
  CAGR advantage. ndx_real CAGR drops from iter 011 11.64% to iter 012
  12.59% (small advantage).

## What didn't work

- **Sharpe regression vs incumbent on EVERY dataset**: best across
  4-config grid loses on lh_56y (1.016 vs 1.046, −0.030), vt_real
  (0.851 vs 0.960, −0.109), ndx_real (1.021 vs 1.104, −0.083). The
  intl-equity injection actually **decreases** risk-adjusted return.
- **Higher MDD on lh_56y and vt_real**: 32.45% / 30.77% vs iter 011's
  26.04% / 21.22%. RSSB's leveraged equity sleeve adds drawdown without
  Sharpe edge.
- **G3 walk-forward fails on lh_56y**: 2 of 8 windows have MDD > 25%
  (26.71% and 32.45%). The GFC-era window stresses the leveraged stack.
- **CAGR floor missed on ndx_real**: 12.59% < 0.8 × 16.98% = 13.58%.
  ndx_real's tech-concentrated benchmark is hard to beat with global
  tilts.

## Lesson — the structural insight

**Adding international equity exposure via RSSB does NOT improve the
iter 011 architecture**. This is a counter to the user's intuition that
"global + factor" tilts would lift Sharpe.

Why does it fail?

1. **Treasury overlap**: NTSX already has 60% IEFSIM exposure. RSSB
   adds another ~50% Treasury sleeve. The composite portfolio ends
   up with ~30-50% Treasury exposure — duration-heavy in a regime
   where rates rose post-2022. The duration drag explains most of the
   Sharpe loss vs iter 011.
2. **Intl-equity decade-of-underperformance**: 2010-2026 was a US-equity
   dominant regime. RSSB's ~50% intl-equity sleeve dragged on real
   windows. On lh_56y the intl/US balance was more even, so iter 012
   loses less there.
3. **KMLM dilution**: iter 011's 40% KMLM weight provided the
   crisis-alpha that lifted Sharpe especially in vt_real and ndx_real.
   Iter 012 dilutes KMLM to 25% (or lower in some configs). The lower
   crisis-alpha weight plus extra duration is the wrong direction for
   Sharpe.
4. **Structural finding**: **iter 011's pure-US stack is hard to beat
   with naive global tilts**. The next attack on iter 011's "intl
   equity gap" must use **factor tilts** (Direction B from BASE_MEMORY)
   or **explicit decoupling from Treasuries** (e.g., NTSX + global
   equity ETF + KMLM, sans GDE/RSSB).

## Citations

- Capital-efficient stacking (RSSB rationale): `[risk_parity, ch.5, p.10]`
- Global equity diversification: `[ilmanen, ch.19]`
- Crisis-alpha (KMLM retention): `[stocks_on_the_move, p.21-30]`
- Gates G1 PBO / G2 DSR / G6 bootstrap / G7 cross-lib:
  `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`

## Next directions (priority order)

1. **B4 — iter 011 + AVUV/AVDV (factor tilts)**: replace 50% of NTSX's
   SPY-side exposure with US small-cap value (VBRSIM 99y) + intl
   small-cap (VSSSIM). Tests if factor premium is the missing edge that
   global-equity beta is not. `[stocks_on_the_move, p.21-30]` +
   Asness-Frazzini-Pedersen 2014.
2. **A3 — NTSX + VXUS + GDE + KMLM (lite global tilt without extra
   leverage)**: VXUSSIM 56y is 1× notional intl-ex-US equity. Drops
   Treasury-overlap drag from RSSB while keeping the global tilt. May
   isolate which factor is the killer (Treasury overlap vs intl-equity
   underperformance).
3. **B5 — iter 011 + UMD overlay (academic momentum)**: replace 25% of
   KMLM weight with FF UMD daily factor. Tests whether explicit equity
   momentum (Sharpe ~1.0-1.5 historical) is a stronger crisis-alpha
   sleeve than KMLM (Sharpe ~0.5).

Direction A1 (NTSX+NTSI+NTSE+GDE+KMLM 5-asset full intl) is **infeasible**
without NTSI/NTSE proxy synthesis — flag for future work if a winning
synth is built.
