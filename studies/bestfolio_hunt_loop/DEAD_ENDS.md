# Dead ends — Bestfolio Hunt Loop

Read this before proposing a hypothesis. Any direction that matches
structurally with an entry below is **forbidden**.

Carry-over dead-ends from `global_factor_tilt_loop` are included here.
They apply to the same universe (global equity + stacked ETFs via
testfolio synth) and transfer directly.

---

## DE-001 — 2× single-asset global-equity LETF + binary SMA trend filter

**Origin**: global_factor_tilt_loop iter 008 — wldu-gayed
**Score**: 61/100 PROMISING
**Date**: 2026-04-27

### What was tested

- WLDU = 2× VTSIM daily-resetting (75bps/y drag: financing + expense)
- Signal: SPYSIM 200-day SMA, checked monthly (Gayed canonical)
- Allocation: 100% WLDU (risk-on) or 100% CASHX (risk-off)
- Based on: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed (2021)

### Why it fails structurally

**Primary structural barrier**: Global equity (VTSIM b&h) already achieves
Sharpe ≈ 0.61 through cross-country diversification. Gayed's LRS mechanism
improves Sharpe from 0.32 (S&P 500 concentrated) → 0.61 (LRS target). When
the starting index already has Sharpe 0.61, the LRS cannot improve further —
it merely doubles both returns and volatility proportionally.

**Quantitative proof** `[leverage_for_the_long_run, p.17, Table 8]`:
- S&P 500 b&h: Sharpe 0.32 → 2× LRS (200d): Sharpe 0.61 (+0.29)
- VTSIM b&h: Sharpe 0.61 → 2× LRS (200d): Sharpe 0.61 (+0.00) [iter 008 empirical]

**Secondary barrier**: 2022 grinding bear market. Monthly SMA check too slow
for gradual rate-regime-driven bear.

### What CAN be tried instead

- Gayed LRS on US equity (SPYSIM/VTISIM, base Sharpe ~0.33) — different starting point
- Multi-asset LRS (rotate across leveraged LETF alternatives when signal fires)
- Gayed signal as INPUT to HAA canary (replace VWOSIM canary with SMA-based signal)

### Results summary

| dataset | Sharpe | CAGR | MDD | Gates |
|---|---|---|---|---|
| educational (~40y) | 0.609 | 12.69% | 44.45% | 7/7 |
| vt_real (~18y) | 0.501 | 10.11% | 44.45% | 5/7 |
| ndx_real (~16y) | 0.473 | 9.44% | 44.45% | 6/7 |

---

## DE-002 — VAA breadth with higher-notional equity asset in offensive (for Sharpe-max)

**Origin**: global_factor_tilt_loop iter 010 — vaa-g3-pure-equity
**Score**: 90/100 WINNER (formal) — Kill 1 triggered (no Pareto advance vs iter 009)
**Date**: 2026-04-27

### What was tested

- VAA-G4 breadth (4-asset vote, partial defensive when B < 4)
- Offensive: NTSXSIM, NTSI, NTSE, GDESIM (all equity or equity+gold stacked)
- Replace BNDSIM (1x notional) in offensive with GDESIM (1.8x notional)
- Hypothesis: removing bond contamination from offensive improves Sharpe

### Why it fails to advance the Pareto frontier

GDESIM's 1.8x notional adds variance faster than returns at the portfolio
level. Net Sharpe effect: −0.071 vs iter 006 VAA-G4. CAGR improved +2pp
(bond drag removed) but Sharpe fell −0.07.

**Structural insight**: For Sharpe-maximization, HAA single-canary (binary
VWOSIM trigger) dominates VAA multi-vote breadth. The breadth mechanism
creates "mixed regime" states — partial equity + partial bonds simultaneously
— which increases realized variance vs HAA's clean binary switching.

### What CAN be tried instead

- HAA canary architecture with different offensive assets (iter 004 direction)
- VAA breadth with BNDSIM as one offensive asset (not a dead end)
- CAGR-maximization contexts where VAA+GDESIM's +2pp CAGR advantage is the goal

### Results summary

| dataset | Sharpe | CAGR | MDD | Gates | Note |
|---|---|---|---|---|---|
| educational (~31y) | 0.9806 | 10.28% | 18.91% | 7/7 | Kill triggered (0.981 ≤ 1.052) |
| vt_real (~17y) | 0.8491 | 8.91% | 18.91% | 7/7 | — |
| ndx_real (16y) | 0.7188 | 6.99% | 18.91% | 7/7 | — |

---

## DE-003 — Plain BAA-G12 Balanced in the current testfolio universe

**Origin**: bestfolio_hunt_loop iter 001 — baa-g12-balanced  
**Score**: 58/100 MARGINAL  
**Date**: 2026-04-28

### What was tested

- BAA-G12 Balanced, monthly.
- Canary: `SPYSIM`, `VEASIM`, `VWOSIM`, `BNDSIM`.
- Canary signal: 13612W absolute momentum.
- Offensive: top 6 of 12 by SMA(12) relative momentum.
- Defensive: top 3 defensive-risk assets by SMA(12), with `CASHX` replacement.
- Net-of-tax via `AnnualDarfEngine`.
- Sources: Keller BAA SSRN 4166845 + `[stocks_on_the_move, ch.6]`.

### Why it fails structurally

BAA-G12 is a good drawdown reducer but too defensive for the current
Sharpe/CAGR frontier. Net Sharpe was **0.975 / 0.792 / 0.782**, below iter
009 HAA+Gold **1.120 / 1.061 / 0.954** on all datasets. Net CAGR missed the
0.8 x iter009 floor on all three datasets. Gross educational Sharpe reached
1.101, but AnnualDarfEngine tax drag reduced it to 0.975.

**Structural insight**: HAA+Gold already gets enough crash protection from
the `VWOSIM` canary plus fixed diversifier sleeves. BAA's broader canary
breadth buys lower MDD, but it pays for that with too much low-return
defensive exposure. For this objective, that is subordinate to HAA's cleaner
binary canary architecture.

### What CAN be tried instead

- Static capital-efficient stack with lower turnover/tax drag.
- Composite multi-lookback momentum, if kept simple and not just BAA breadth.
- HAA offensive-sleeve changes; do not re-test plain BAA-G12 Balanced without
  a materially different asset universe.

### Results summary

| dataset | net Sharpe | net CAGR | net MDD | Gates |
|---|---:|---:|---:|---:|
| educational | 0.975 | 10.60% | 16.34% | 7/7 |
| vt_real | 0.792 | 8.42% | 13.93% | 7/7 |
| ndx_real | 0.782 | 7.66% | 12.73% | 6/7 |

---

## DE-004 — Composite Momentum Standard with SPY200 top-4 inverse-vol and IEF/gold defense

**Origin**: bestfolio_hunt_loop iter 002 — composite-momentum-standard
**Score**: 55/100 MARGINAL
**Date**: 2026-04-28

### What was tested

- Monthly SPY 200-day SMA risk gate.
- Risk-on: top 4 from `SPYSIM`, `QQQSIM`, `VEASIM`, `TLTSIM`, `IEFSIM`,
  `GLDSIM`, `KMLMSIM` by positive 8-month return.
- Sizing: inverse 63-day volatility.
- Risk-off: 60% `IEFSIM` + 40% `GLDSIM`.
- Net-of-tax via `AnnualDarfEngine`.
- Source: `[stocks_on_the_move, p.21-30]`.

### Why it fails structurally

Composite Momentum Standard is robust but return-capped in this universe.
It passed **7/7 gates on all three datasets**, but net Sharpe was only
**0.940 / 0.958 / 0.957**, below iter 009 HAA+Gold **1.120 / 1.061 /
0.954** and never beat by the required +0.10. Net CAGR also missed the
0.8 x iter009 floor on educational and vt_real.

**Structural insight**: the SPY200 gate plus 60/40 IEF/gold risk-off sleeve
avoids catastrophic drawdown, but it sits in low-return protection too often
and pays enough annual DARF drag to lose the Sharpe/CAGR frontier. HAA's
`VWOSIM` canary with fixed KMLM/gold sleeves preserves more upside while
keeping drawdown comparable.

### What CAN be tried instead

- Static capital-efficient stacks with lower turnover/tax drag.
- HAA offensive-sleeve changes, especially factor or return-stacked sleeves.
- Composite Momentum only after real/synthetic `VNQ` and broad-commodity
  (`DBC`) proxies are added; do not re-test the same SPY200/top4/inverse-vol
  architecture with this reduced universe.

### Results summary

| dataset | net Sharpe | net CAGR | net MDD | Gates |
|---|---:|---:|---:|---:|
| educational | 0.940 | 9.25% | 20.76% | 7/7 |
| vt_real | 0.958 | 9.94% | 20.76% | 7/7 |
| ndx_real | 0.957 | 9.59% | 20.76% | 7/7 |

---

## DE-005 — Plain static global/factor/CTA capital-efficient stack

**Origin**: bestfolio_hunt_loop iter 003 — global-factor-cta-stack  
**Score**: 54/100 MARGINAL  
**Date**: 2026-04-28

### What was tested

- Six pre-committed static capital-efficient stacks around `RSSBSIM`,
  `GDESIM`, `KMLMSIM`, `VBRSIM`, `VSSSIM`, `VWOSIM`, `SPYSIM`, and an
  `RSST_PROXY = SPYSIM + KMLMSIM - CASHX`.
- Selected config: `stack_gde_heavy`, chosen by maximum mean Sharpe divided
  by iter 009 Sharpe across the three datasets.
- Net-of-tax via `AnnualDarfEngine`.
- Source: `[risk_parity, p.1-2, p.10]`.

### Why it fails structurally

Static stacking can preserve CAGR, but it does not control drawdown enough
to compete with HAA+Gold's canary architecture. The selected config cleared
the CAGR floor on all datasets and passed 6/7 gates everywhere, but net
Sharpe was only **0.823 / 0.742 / 0.910** versus iter 009 **1.120 / 1.061 /
0.954**. MDD was **41.76% / 40.41% / 27.49%**, breaching the iter 009 + 5pp
ceiling on all datasets.

**Structural insight**: lower turnover is not enough. For this objective,
the `VWOSIM` canary and explicit defensive switching in HAA are doing
essential variance suppression. A plain static stack may be useful for CAGR,
but it is subordinate for Sharpe-frontier hunting.

### What CAN be tried instead

- HAA offensive-sleeve factor tilt, keeping the canary and fixed diversifiers.
- Return-stacked RSST/RSSB variants only inside a risk-on/risk-off shell.
- Static stacks only with an explicit drawdown-control overlay or a different
  CAGR-first objective.

### Results summary

| dataset | net Sharpe | net CAGR | net MDD | Gates |
|---|---:|---:|---:|---:|
| educational | 0.823 | 12.09% | 41.76% | 6/7 |
| vt_real | 0.742 | 11.77% | 40.41% | 6/7 |
| ndx_real | 0.910 | 13.11% | 27.49% | 6/7 |

---

## DE-006 — Simple HAA international small/value tilt

**Origin**: bestfolio_hunt_loop iter 004 — haa-global-factor-tilt  
**Score**: 69/100 PROMISING  
**Date**: 2026-04-28

### What was tested

- Iter 009 HAA+Gold shell retained: `VWOSIM` canary, top-2 offensive,
  top-1 defensive, 10% `KMLMSIM`, 5% `GLDSIM`.
- Replaced the plain international stacked offensive sleeve with four
  pre-committed `VEASIM` + `VBRSIM` + `VSSSIM` blends.
- Selected config: `tilt_scv20` = 80% `VEASIM`, 10% `VBRSIM`, 10% `VSSSIM`.
- Net-of-tax via `AnnualDarfEngine`.
- Sources: `[stocks_on_the_move, ch.6]`; `[leverage_for_the_long_run, p.40-60]`.

### Why it fails structurally

The HAA canary still controls drawdown, but the small/value tilt does not add
enough independent return to advance the Sharpe frontier. Net Sharpe was
**0.990 / 0.955 / 0.861** versus iter 009 **1.120 / 1.061 / 0.954**, with
zero datasets beating the required +0.10 Sharpe edge. G1 PBO also failed in
all three datasets (**0.885 / 0.869 / 0.694**), meaning the chosen tilt level
is an unstable grid selection `[advances_fin_ml, p.208-211]`.

**Structural insight**: within the existing HAA offensive set, changing the
international equity beta into a simple small/value blend mostly reshuffles
risk-on equity exposure. It preserves MDD but sacrifices CAGR/Sharpe, so it is
not the missing bestfolio.app +0.06 to +0.10 Sharpe gap.

### What CAN be tried instead

- Return-stacked RSST/RSSB variants inside a HAA shell, not as static stacks.
- A qualitatively different HAA offensive return source, not another simple
  developed/international factor blend.
- RSIT only after real ETF data exists, or explicitly marked as incomplete synth.

### Results summary

| dataset | net Sharpe | net CAGR | net MDD | Gates |
|---|---:|---:|---:|---:|
| educational | 0.990 | 12.21% | 20.71% | 6/7 |
| vt_real | 0.955 | 11.49% | 14.20% | 6/7 |
| ndx_real | 0.861 | 9.41% | 14.20% | 6/7 |

---

## DE-007 — Simple HAA RSST/RSSB/CTA offensive substitution

**Origin**: bestfolio_hunt_loop iter 005 — haa-rsst-rssb-cta  
**Score**: 70/100 PROMISING  
**Date**: 2026-04-28

### What was tested

- Iter 009 HAA+Gold shell retained: `VWOSIM` canary, top-2 offensive,
  top-1 defensive, 10% `KMLMSIM`, 5% `GLDSIM`.
- Replaced the risk-on offensive candidates with four pre-committed sets
  using `RSSBSIM`, `RSST_PROXY = SPYSIM + KMLMSIM - CASHX`, `CTAPSIM`,
  `NTSXSIM`, `NTSI`, and `GDESIM`.
- Selected config: `rssb_cta_balanced` = `RSSBSIM`, `NTSXSIM`, `CTAPSIM`,
  `GDESIM`.
- Net-of-tax via `AnnualDarfEngine`.
- Sources: `[risk_parity, ch.5]`; `[stocks_on_the_move, p.21-30]`.

### Why it fails structurally

The HAA shell handled the stacked sleeves cleanly, but the additional
managed-futures/return-stacked exposure diluted return more than it improved
risk. The selected config passed **7/7 gates on all three datasets**, but net
Sharpe was only **0.953 / 1.028 / 0.946** versus iter 009 HAA+Gold **1.120 /
1.061 / 0.954**. Zero datasets beat iter 009 by +0.10 Sharpe, and the
pre-committed kill fired because educational Sharpe was below iter 004's 0.990.

**Structural insight**: after iter 009, the frontier problem is not just adding
more convex diversifiers. HAA already has fixed KMLM/gold sleeves and strong
drawdown control; adding more MF/stacked sleeves inside the offensive rank
reduces volatility and MDD, but it also reduces CAGR enough to lose Sharpe.

### What CAN be tried instead

- HAA defensive-state changes that specifically target Sharpe, such as
  KMLM-only or CASHX-dominant defensive selection.
- HAA dual-canary variants that reduce false defensive states without diluting
  the offensive sleeve.
- RSIT only after real ETF data exists, or explicitly marked as incomplete
  synthetic exploration.

### Results summary

| dataset | net Sharpe | net CAGR | net MDD | Gates |
|---|---:|---:|---:|---:|
| educational | 0.953 | 11.11% | 16.98% | 7/7 |
| vt_real | 1.028 | 11.99% | 13.97% | 7/7 |
| ndx_real | 0.946 | 10.12% | 13.97% | 7/7 |

---

## DE-008 — Synthetic HAA RSIT offensive sleeve

**Origin**: bestfolio_hunt_loop iter 006 — haa-rsit-synth  
**Score**: 71/100 PROMISING  
**Date**: 2026-04-28

### What was tested

- Iter 009 HAA+Gold shell retained: `VWOSIM` canary, top-2 offensive,
  top-1 defensive, 10% `KMLMSIM`, 5% `GLDSIM`.
- Added synthetic `RSIT_PROXY = VEASIM + KMLMSIM - 50bps/year` as a rankable
  international-equity + managed-futures offensive candidate.
- Tested four RSIT-centered offensive sets using `NTSXSIM`, `NTSI`,
  `RSIT_PROXY`, `NTSE`, `GDESIM`, and `RSSBSIM`.
- Selected config: `rsit_with_ntsi` = `NTSXSIM`, `NTSI`, `RSIT_PROXY`,
  `GDESIM`.
- Net-of-tax via `AnnualDarfEngine`.
- Sources: `[risk_parity, ch.5]`; `[stocks_on_the_move, ch.6]`.
- Caveat: **INCOMPLETE synthetic** until live RSIT ETF data exists.

### Why it fails structurally

The RSIT-style sleeve clears many risk controls but does not add the missing
Sharpe edge. Net Sharpe was **0.869 / 0.897 / 0.837** versus iter 009 HAA+Gold
**1.120 / 1.061 / 0.954**, with zero datasets beating the required +0.10
Sharpe edge. The pre-committed kill fired because educational Sharpe was below
iter 004's **0.990**. PBO also failed on the two global windows
(**0.714 / 0.845**), so the selected RSIT mix is unstable
`[advances_fin_ml, p.208-211]`.

**Structural insight**: HAA+Gold already carries fixed managed-futures and gold
convexity. Embedding more managed futures inside international equity preserves
CAGR and MDD floors, but it lowers Sharpe and destabilizes selection. The
frontier gap is not another MF-overlay sleeve.

### What CAN be tried instead

- HAA defensive-state changes that reduce false defensive exposure without
  diluting the offensive sleeve.
- Dual-canary HAA variants that preserve iter 009 offensive exposure.
- Retest RSIT only after real ETF data exists, and only as a live-tracking
  comparison against this synthetic proxy.

### Results summary

| dataset | net Sharpe | net CAGR | net MDD | Gates |
|---|---:|---:|---:|---:|
| educational | 0.869 | 11.13% | 22.12% | 6/7 |
| vt_real | 0.897 | 11.33% | 15.58% | 6/7 |
| ndx_real | 0.837 | 9.65% | 14.01% | 7/7 |

---

## DE-009 — Simple HAA KMLM/CASH defensive-state swaps

**Origin**: bestfolio_hunt_loop iter 007 — haa-defensive-kmlm-cash
**Score**: 75/100 STRONG
**Date**: 2026-04-28

### What was tested

- Iter 009 HAA+Gold offensive shell retained: `VWOSIM` canary, top-2
  offensive, 10% `KMLMSIM`, 5% `GLDSIM`.
- Offensive candidates unchanged: `NTSXSIM`, `NTSI`, `NTSE`, `GDESIM`.
- Tested four defensive-state sets:
  - `orig_ief_bnd_cash`: `IEFSIM`, `BNDSIM`, `CASHX`
  - `kmlm_cash`: `KMLMSIM`, `CASHX`
  - `kmlm_ief_cash`: `KMLMSIM`, `IEFSIM`, `CASHX`
  - `cash_only`: `CASHX`
- Net-of-tax via `AnnualDarfEngine`.
- Sources: `[stocks_on_the_move, ch.6]`; `[risk_parity, ch.5]`.

### Why it fails structurally

The original iter 009 defense was selected again. The selected
`orig_ief_bnd_cash` config passed **7/7 gates on all three datasets**, but net
Sharpe was only **0.983 / 0.954 / 0.860** versus iter 009 **1.120 / 1.061 /
0.954**, with zero datasets beating the required +0.10 Sharpe edge.

KMLM-heavy defense did not solve false-defensive drag. It raised MDD to
**27.49%** on all datasets and still reduced Sharpe. Cash-only defense kept
drawdown controlled but cut CAGR. The original `IEFSIM`/`BNDSIM`/`CASHX`
defensive set remains the best simple Sharpe balance in this universe.

**Structural insight**: after iter 009, replacing defensive assets after the
canary fires is not enough. The next plausible edge must alter canary timing
or state classification itself, while preserving the proven offensive and
defensive sleeves `[stocks_on_the_move, ch.6]`.

### What CAN be tried instead

- Dual-canary HAA variants that preserve binary HAA switching and all iter 009
  assets.
- Gayed/SPY/VT trend signal as an HAA canary input, not as a standalone
  2x single-asset LETF strategy.
- A tightly pre-committed volatility throttle on the HAA dynamic sleeve, if it
  avoids broad parameter search.

### Results summary

| dataset | net Sharpe | net CAGR | net MDD | Gates |
|---|---:|---:|---:|---:|
| educational | 0.983 | 12.15% | 20.81% | 7/7 |
| vt_real | 0.954 | 11.49% | 14.20% | 7/7 |
| ndx_real | 0.860 | 9.44% | 14.20% | 7/7 |
