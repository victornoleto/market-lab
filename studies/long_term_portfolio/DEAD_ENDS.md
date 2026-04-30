# Dead ends — Long-Term Portfolio Loop

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

**Origin**: long_term_portfolio iter 001 — baa-g12-balanced  
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

**Origin**: long_term_portfolio iter 002 — composite-momentum-standard
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

**Origin**: long_term_portfolio iter 003 — global-factor-cta-stack  
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

**Origin**: long_term_portfolio iter 004 — haa-global-factor-tilt  
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

**Origin**: long_term_portfolio iter 005 — haa-rsst-rssb-cta  
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

**Origin**: long_term_portfolio iter 006 — haa-rsit-synth  
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

**Origin**: long_term_portfolio iter 007 — haa-defensive-kmlm-cash
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

---

## DE-010 — Simple HAA dual broad-equity canary (`VWOSIM` + `VTISIM`)

**Origin**: long_term_portfolio iter 008 — haa-dual-canary
**Score**: 73/100 PROMISING
**Date**: 2026-04-28

### What was tested

- Iter 009 HAA+Gold assets retained exactly: offensive `NTSXSIM`, `NTSI`,
  `NTSE`, `GDESIM`; defensive `IEFSIM`, `BNDSIM`, `CASHX`; fixed 10%
  `KMLMSIM` + 5% `GLDSIM`.
- Changed only the binary HAA risk-on/risk-off trigger.
- Tested four canary modes:
  - `vwo_only`: original `VWOSIM` HAA momentum > 0.
  - `vti_only`: `VTISIM` HAA momentum > 0.
  - `either_vwo_vti`: either canary > 0.
  - `both_vwo_vti`: both canaries > 0.
- Selected config: `vwo_only`, by maximum mean Sharpe divided by iter 009
  Sharpe across the three datasets.
- Net-of-tax via `AnnualDarfEngine`.
- Sources: `[stocks_on_the_move, ch.6]`; `[stocks_on_the_move, p.63-65]`.

### Why it fails structurally

Adding `VTISIM` as a second broad-equity canary did not reduce false-defensive
drag. The original `VWOSIM` canary was selected again and produced net Sharpe
**0.983 / 0.954 / 0.860** versus iter 009 HAA+Gold **1.120 / 1.061 / 0.954**.
Zero datasets beat iter 009 by the required +0.10 Sharpe edge.

`vti_only` was worse on all datasets. The permissive `either_vwo_vti` rule
held risk assets too often and raised real-window MDD to **18.93%** while
lowering Sharpe. The strict `both_vwo_vti` rule cut drawdown in real windows
but sacrificed too much CAGR and Sharpe. The ndx_real PBO failed at **0.552**,
so even the grid-level canary choice was not stable enough
`[advances_fin_ml, p.208-211]`.

**Structural insight**: in this HAA universe, a second broad-equity absolute
momentum canary is not the missing timing edge. `VWOSIM` remains the best
simple binary risk-state trigger; next canary work must use a qualitatively
different trend/regime input rather than another equity index.

### What CAN be tried instead

- Gayed/SPY/VT moving-average trend input as an HAA canary, not as standalone
  2x equity.
- A tightly pre-committed volatility throttle on the HAA dynamic sleeve.
- A CAGR-first HAA variant only if the loop objective explicitly changes away
  from Sharpe frontier hunting.

### Results summary

| dataset | net Sharpe | net CAGR | net MDD | Gates |
|---|---:|---:|---:|---:|
| educational | 0.983 | 12.15% | 20.81% | 7/7 |
| vt_real | 0.954 | 11.49% | 14.20% | 7/7 |
| ndx_real | 0.860 | 9.44% | 14.20% | 6/7 |

---

## DE-011 — Simple Gayed SPY/VT trend input as HAA canary

**Origin**: long_term_portfolio iter 009 — haa-gayed-trend-canary
**Score**: 73/100 PROMISING
**Date**: 2026-04-28

### What was tested

- Iter 009 HAA+Gold assets retained exactly: offensive `NTSXSIM`, `NTSI`,
  `NTSE`, `GDESIM`; defensive `IEFSIM`, `BNDSIM`, `CASHX`; fixed 10%
  `KMLMSIM` + 5% `GLDSIM`.
- Changed only the binary HAA risk-on/risk-off trigger.
- Tested four canary modes:
  - `vwo_original`: original `VWOSIM` HAA momentum > 0.
  - `spy_trend`: `SPYSIM` above 10-month trend.
  - `vt_trend`: `VTSIM` above 10-month trend.
  - `vwo_and_spy_trend`: both original `VWOSIM` momentum and `SPYSIM`
    trend positive.
- Net-of-tax via `AnnualDarfEngine`.
- Sources: `[leverage_for_the_long_run, p.40-60]`; `[stocks_on_the_move, ch.6]`.

### Why it fails structurally

The original `VWOSIM` canary was selected again. The selected config produced
net Sharpe **0.983 / 0.954 / 0.860** versus iter 009 **1.120 / 1.061 /
0.954**, with zero datasets beating the required +0.10 Sharpe edge.

`SPYSIM` trend was too permissive in real windows, lowering Sharpe and raising
MDD to **18.93%**. `VTSIM` trend modestly improved ndx_real Sharpe versus the
selected original canary, but still stayed below iter 009 and below winner
thresholds. Strict `VWOSIM` + `SPYSIM` confirmation cut too much CAGR.

**Structural insight**: simple broad-equity moving-average trend is not a
better state classifier than HAA's emerging-market `VWOSIM` canary in this
universe. Future timing work needs a qualitatively different regime variable,
not another simple broad-equity price trend `[leverage_for_the_long_run, p.40-60]`.

### What CAN be tried instead

- A tightly pre-committed volatility throttle on the HAA dynamic sleeve.
- Real VT/VXUS data acquisition to reduce proxy uncertainty before more
  timing variants.
- A new non-price macro/regime input only if it is literature-driven and
  kept to a very small grid.

### Results summary

| dataset | net Sharpe | net CAGR | net MDD | Gates |
|---|---:|---:|---:|---:|
| educational | 0.983 | 12.15% | 20.81% | 7/7 |
| vt_real | 0.954 | 11.49% | 14.20% | 7/7 |
| ndx_real | 0.860 | 9.44% | 14.20% | 6/7 |

---

## DE-012 — Simple HAA dynamic-sleeve volatility throttle

**Origin**: long_term_portfolio iter 010 — haa-vol-throttle  
**Score**: 60/100 PROMISING  
**Date**: 2026-04-28

### What was tested

- Iter 009 HAA+Gold assets retained exactly: offensive `NTSXSIM`, `NTSI`,
  `NTSE`, `GDESIM`; defensive `IEFSIM`, `BNDSIM`, `CASHX`; fixed 10%
  `KMLMSIM` + 5% `GLDSIM`.
- Canary retained exactly: original `VWOSIM` HAA momentum > 0.
- Added a trailing 63-trading-day realized-volatility throttle to only the
  85% dynamic sleeve.
- Tested four pre-committed configs:
  - `no_throttle`
  - `vol12`
  - `vol15`
  - `vol18`
- Selected config: `vol12`, by maximum mean Sharpe divided by iter 009 Sharpe
  across the three datasets.
- Net-of-tax via `AnnualDarfEngine`.
- Sources: `[systematic_trading, p.137-148]`; `[systematic_trading, p.196-197]`;
  `[stocks_on_the_move, ch.6]`.

### Why it fails structurally

The volatility throttle improved drawdown but did not create enough return.
Selected `vol12` passed **7/7 gates on all three datasets**, but net Sharpe was
only **1.020 / 0.955 / 0.881** versus iter 009 HAA+Gold **1.120 / 1.061 /
0.954**. Zero datasets beat iter 009 by the required +0.10 Sharpe edge.

The pre-committed kill fired because educational Sharpe improved only **+0.037**
versus the `no_throttle` baseline, below the required +0.05. More importantly,
the selected config failed the 0.8 x iter009 CAGR floor on every dataset:
**10.10% / 9.19% / 8.23%** net CAGR.

**Structural insight**: a simple volatility throttle on HAA is a capital
preservation overlay. It cuts high-volatility risk-on exposure and improves
MDD, but it also removes too much of the return engine. For this Sharpe-frontier
mission, the missing edge must add return or improve timing quality, not merely
de-risk the already robust HAA+Gold shell.

### What CAN be tried instead

- Add real VT/VXUS data to reduce proxy uncertainty before further HAA timing
  variants.
- Use a genuinely new non-price regime input if the hunt continues.
- Revisit `vol12` only under a drawdown-minimization or capital-preservation
  objective, not as a Sharpe-frontier candidate.

### Results summary

| dataset | net Sharpe | net CAGR | net MDD | Gates |
|---|---:|---:|---:|---:|
| educational | 1.020 | 10.10% | 14.86% | 7/7 |
| vt_real | 0.955 | 9.19% | 11.13% | 7/7 |
| ndx_real | 0.881 | 8.23% | 11.13% | 7/7 |

---

## DE-013 — NTSX + GDE + RSSB + KMLM 4-asset global capital-efficient stack

**Origin**: long_term_portfolio iter 012 — ntsx-gde-rssb-kmlm-global-stack
**Score**: 88/100 STRONG (winner_conds_met=true vs avg(SPY,VT)) — Pre-committed Kill #1 fired
**Date**: 2026-04-28

### What was tested

- Iter 011's NTSX+GDE+KMLM static capital-efficient stack architecture
  retained, with `RSSBSIM` (Return Stacked Global Stocks & Bonds, 200%
  notional — ~100% global equity + 100% Treasury) added as a 4th
  sleeve.
- Tested 4 pre-committed weight grids:
  - `rssb_balanced_30303010` = 30% NTSX / 30% GDE / 30% RSSB / 10% KMLM
  - `rssb_moderate_25252525` = 25% NTSX / 25% GDE / 25% RSSB / 25% KMLM
  - `rssb_iter011_clone_30202525` = 30% NTSX / 20% GDE / 25% RSSB / 25% KMLM
  - `rssb_lite_30253015` = 30% NTSX / 25% GDE / 30% RSSB / 15% KMLM
- Selected config: `rssb_moderate_25252525`, by max mean(gross_Sharpe /
  avg(SPY,VT)_Sharpe) across 3 datasets.
- Datasets: lh_56y (1986-2026, 40y eff. SPYSIM-bounded), vt_real (17y),
  ndx_real (16y).
- Sources: `[risk_parity, ch.5, p.10]` (Carlson capital-efficient stacking);
  `[ilmanen, ch.19]` (global equity diversification);
  `[stocks_on_the_move, p.21-30]` (KMLM crisis-alpha).

### Why it fails structurally

The strategy clears all 5 strict winner conditions vs the loop's
primary benchmark avg(SPY,VT) — beats it by +0.340/+0.144 Sharpe on
lh_56y/vt_real (criterion 1: 2/3 datasets ≥ +0.10), passes 6/7/7 gates
(criterion 2), DSR p worst 5.6e-3 (criterion 3), CAGR floor on 2/3
(criterion 4), MDD ceiling on 3/3 (criterion 5). Score 88/100 STRONG.

**But it loses to iter 011 on Sharpe across every dataset**:

| dataset | iter 012 selected S | iter 011 incumbent S | Δ vs iter 011 |
|---|---:|---:|---:|
| lh_56y    | 1.011 | 1.046 | −0.035 |
| vt_real   | 0.851 | 0.960 | −0.109 |
| ndx_real  | 1.021 | 1.104 | −0.083 |

Best across the 4-config grid on lh_56y is **1.016** (`rssb_iter011_clone_30202525`),
still below iter 011's 1.046 — pre-committed kill #1 triggered (best-config
Sharpe regression on lh_56y).

**Structural insight**: RSSB does not improve the iter 011 architecture
because:

1. **Treasury overlap**: NTSX already provides 60% IEFSIM exposure. RSSB
   adds another ~50% Treasury overlay. The composite portfolio ends
   30-50% Treasury — duration-heavy. Post-2022 rate hikes create the
   Sharpe drag.
2. **Intl-equity drag (2010-2026)**: RSSB's ~50% intl-equity sleeve
   underperformed US equity for the live windows. lh_56y is less
   affected but still loses.
3. **KMLM dilution**: iter 011's 40% KMLM provided crisis-alpha. iter
   012 dilutes KMLM to 25% (or lower) — lower crisis-alpha + extra
   duration is the wrong direction for Sharpe.
4. **iter 011's pure-US capital-efficient stack is hard to beat with
   naive global tilts**. Adding leveraged-equity sleeves with embedded
   Treasury is **structurally subordinate** to iter 011's NTSX + GDE +
   KMLM mix.

### What CAN be tried instead

- **Direction A3 (now higher priority)**: NTSX + VXUSSIM (1× intl,
  no Treasury overlap) + GDE + KMLM — isolates the intl-equity tilt
  from RSSB's Treasury overlap. Tests if the failure mode is RSSB
  specifically or intl-equity broadly.
- **Direction B (factor tilts on iter 011 base)**: replace 50% of NTSX
  SPY-side with VBRSIM (US small-cap value) + VSSSIM (intl small-cap).
  Factor premium may be the missing edge that intl-equity beta is not.
- **Direction A1 (NTSX + NTSI + NTSE + GDE + KMLM)**: requires NTSI/NTSE
  proxy synthesis (not in testfolio cache). Defer until proxies built.

### Results summary

Selected: `rssb_moderate_25252525` = 25% NTSX + 25% GDE + 25% RSSB + 25% KMLM.

| dataset | gross Sharpe | gross CAGR | gross MDD | Gates | DSR p |
|---|---:|---:|---:|---:|---:|
| lh_56y    | 1.011 | 12.20% | 32.45% | 6/7 | 5.59e-11 |
| vt_real   | 0.851 | 11.52% | 30.77% | 7/7 | 5.57e-3 |
| ndx_real  | 1.021 | 12.59% | 20.20% | 7/7 | 1.29e-3 |

Net ≈ gross (static stack, year-end-only DARF, daily-Sharpe tax-neutral).

---

## DE-014 — Constant-weight US factor tilt (VBRSIM) on iter 011 base

**Origin**: long_term_portfolio iter 013 — factor-tilt-on-iter011
**Score**: 91/100 WINNER (tier; vs avg(SPY,VT) all 5 strict conditions met)
— but does NOT advance iter 011 incumbent
**Date**: 2026-04-28

### What was tested

- Iter 011's NTSX + GDE + KMLM static capital-efficient stack architecture
  retained, with `VBRSIM` (US Small-Cap Value, AVUV synth proxy, 99y
  inception) added as a factor-tilt sleeve at 4 intensity levels.
- Tested 4 pre-committed weight grids:
  - `factor_lite_30253510` = 30% NTSX / 25% GDE / 35% KMLM / 10% VBRSIM
  - `factor_moderate_25253020` = 25% NTSX / 25% GDE / 30% KMLM / 20% VBRSIM
  - `factor_balanced_25202530` = 25% NTSX / 20% GDE / 30% KMLM / 25% VBRSIM
  - `factor_heavy_20203030` = 20% NTSX / 20% GDE / 30% KMLM / 30% VBRSIM
- Selected config: `factor_lite_30253510` (10% VBRSIM), by max
  mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets.
- Datasets: lh_56y (1986-2026, 40y eff. SPYSIM-bounded), vt_real (17y),
  ndx_real (16y).
- Rationale: VBRSIM is **1× notional**, **zero Treasury** — qualitatively
  different from iter 012's RSSB (DE-013, 200% notional with embedded
  Treasury). Tests user's literature thesis (AVUV/AVDE/SPMO factor ETFs).
- Sources: `[risk_parity, ch.5, p.10]` (cap-efficient core retained);
  `[risk_parity, ch.2, p.37-41]` (factor premium framework);
  `[stocks_on_the_move, ch.6, p.21-30]` (cross-sectional ranking edges).

### Why it fails to advance the incumbent

The strategy clears all 5 strict winner conditions vs the loop's primary
benchmark avg(SPY,VT) — beats it +0.454/+0.216/+0.152 Sharpe across the
3 datasets, passes 5/7/7/7 gates, DSR p worst 2.29e-3, robustness 5/5
(52/52 rolling-5y windows positive). Score 91 = tier WINNER per scoring
rubric.

**But it ties iter 011's score (91 = 91, NOT >) and fails the +0.10
incumbent edge gate on every dataset**:

| dataset | iter 013 selected S | iter 011 incumbent S | Δ vs iter 011 |
|---|---:|---:|---:|
| lh_56y    | 1.126 | 1.046 | +0.080 (close, not ≥0.10) |
| vt_real   | 0.923 | 0.960 | −0.037 |
| ndx_real  | 1.075 | 1.104 | −0.029 |

**Cross-config monotonic finding (the structural insight)**:

| config | VBR % | lh_56y S | Δ iter011 | vt_real S | Δ iter011 | ndx_real S | Δ iter011 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `factor_lite_30253510`     | 10% | 1.126 | +0.080 | 0.923 | −0.037 | 1.075 | −0.029 |
| `factor_moderate_25253020` | 20% | 1.106 | +0.060 | 0.874 | −0.086 | 1.032 | −0.072 |
| `factor_balanced_25202530` | 25% | 1.125 | +0.079 | 0.846 | −0.114 | 1.005 | −0.099 |
| `factor_heavy_20203030`    | 30% | 1.131 | +0.085 | 0.825 | −0.135 | 0.979 | −0.125 |

Across the entire grid, factor tilt **monotonically** helps lh_56y but
**monotonically** hurts both live windows.

### Structural insight (why it's a dead-end)

1. **Factor premium IS alive on long-history (1986-2026)**: cross-config
   monotonic improvement on lh_56y is robust evidence that `[risk_parity,
   ch.2, p.37-41]`-style factor premium frameworks have empirical support.
2. **Post-2008 "death of value"**: 2009-2020 was the worst decade for
   size+value premium since Fama-French published; partial recovery
   2021-2024 hasn't reversed the live-window damage. Constant-weight
   VBRSIM imports this regression directly into the portfolio.
3. **iter 011 captures the dominant post-GFC regime**: NTSX (90% SPY +
   60% IEF) + GDE (90% S&P + 90% gold) + KMLM are precisely tuned to
   the 2009-2026 US-large-cap-with-stacked-overlays regime. Adding
   VBRSIM dilutes that exposure with one that hasn't paid for ~17 years.
4. **The Sharpe-helping (lh_56y) gain is smaller in absolute terms than
   the Sharpe-hurting (vt + ndx) loss**: any practitioner who weights
   recent windows ≥ historical sees factor tilt as net negative.

### What CAN be tried instead

- **UMD (momentum factor) overlay on iter 011** — different factor with
  different post-2008 behavior (momentum had positive 2017-2024 while
  size+value lagged). Different regime mismatch profile.
- **Factor with regime filter** — VBRSIM weight conditional on a value
  spread (CAPE differential) or factor-momentum (12-1 factor return)
  signal. Factor sleeve only active when premium is "live"; KMLM/GDE
  cover otherwise. Pre-commit ≤ 3 configs to avoid the strategy_hunt_loop
  "regime gate on existing winner" DSR-regression trap.
- **Direction A1 (NTSX/NTSI/NTSE/GDE/KMLM)** — international leveraged-
  equity stack via WisdomTree NTSI (1.5× intl developed) + NTSE (1.5×
  EM) instead of factor tilt. Requires NTSI/NTSE proxy synthesis first.

### Results summary

Selected: `factor_lite_30253510` = 30% NTSX + 25% GDE + 35% KMLM + 10% VBRSIM.

| dataset | gross Sharpe | gross CAGR | gross MDD | Gates | DSR p |
|---|---:|---:|---:|---:|---:|
| lh_56y    | 1.126 | 12.32% | 25.73% | 5/7 | 2.86e-13 |
| vt_real   | 0.923 | 11.27% | 24.45% | 7/7 | 2.29e-3 |
| ndx_real  | 1.075 | 12.06% | 18.00% | 7/7 | 6.24e-4 |

Net ≈ gross (static stack, year-end DARF, daily-Sharpe tax-neutral).

---

## DE-015 — Constant-weight international equity tilt (VXUSSIM) on iter 011 base

**Origin**: long_term_portfolio iter 014 — intl-equity-tilt-on-iter011
**Score**: 93/100 WINNER (tier; vs avg(SPY,VT) all 5 strict conditions met;
mechanically advanced iter 011 incumbent on score gate but FAILS the
substantive Sharpe-edge gate on the live windows)
**Date**: 2026-04-28

### What was tested

- Iter 011's NTSX + GDE + KMLM static capital-efficient stack architecture
  retained, with `VXUSSIM` (Total International ex-US Stock Market,
  testfolio synth analog of Vanguard VXUS — 1× notional, zero embedded
  Treasury) added as a 4th sleeve at 4 intensity levels.
- Tested 4 pre-committed weight grids:
  - `intl_lite_35253010`     = 35% NTSX / 10% VXUSSIM / 25% GDE / 30% KMLM
  - `intl_moderate_30202525` = 30% NTSX / 20% VXUSSIM / 25% GDE / 25% KMLM
  - `intl_balanced_25252525` = 25% NTSX / 25% VXUSSIM / 25% GDE / 25% KMLM
  - `intl_heavy_25302025`    = 25% NTSX / 30% VXUSSIM / 20% GDE / 25% KMLM
- Selected config: `intl_lite_35253010` (10% VXUSSIM), by max
  mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets.
- Datasets: lh_56y (1986-2026, 40y eff. SPYSIM-bounded), vt_real (17y),
  ndx_real (16y).
- Rationale: VXUSSIM is **1× notional** with **zero Treasury** —
  qualitatively different from iter 012's RSSB (DE-013, 200% notional with
  embedded Treasury overlap with NTSX's IEF) AND from iter 013's VBRSIM
  (DE-014, US factor sleeve subject to post-2008 "death of value"). VXUSSIM
  isolates pure broad intl-equity diversification.
- Sources: `[risk_parity, ch.5, p.10]` (cap-efficient core retained);
  `[ilmanen, ch.19]` (global equity diversification rationale);
  `[stocks_on_the_move, p.21-30]` (KMLM crisis-alpha retained).

### Why it fails to substantively advance the incumbent

The strategy clears all 5 strict winner conditions vs the loop's primary
benchmark avg(SPY,VT) — beats it +0.384/+0.178/+0.129 Sharpe across the
3 datasets, passes 6/7/7/7 gates, DSR p worst 3.66e-3, robustness 5/5
(52/52 rolling-5y windows positive). Score 93/100 = tier WINNER per
scoring rubric. Score advances iter 011's 91 → mechanically takes
incumbent slot per `BASE_MEMORY.md` rule (score-OR clause).

**But it LOSES Sharpe to iter 011 on the deploy-relevant live windows**:

| dataset | iter 014 selected S | iter 011 incumbent S | Δ vs iter 011 |
|---|---:|---:|---:|
| lh_56y    | 1.055 | 1.046 | +0.009 (within noise) |
| vt_real   | 0.885 | 0.960 | **−0.075** |
| ndx_real  | 1.052 | 1.104 | **−0.052** |

**0/3 datasets clear the +0.10 substantive incumbent edge gate.** The
score advance 93 > 91 is partially a benchmark-migration artifact — iter
011 was originally scored on the legacy `educational` window, iter 014 on
the new lh_56y framework with different per-criterion scaling. Within
the new framework, iter 014 is mildly stronger than iter 013 (gates
23 vs 21) but mildly weaker than iter 011 on raw Sharpe.

**Cross-config monotonic finding (the key structural insight)**:

| config | VXUS % | lh_56y S | Δ iter011 | vt_real S | Δ iter011 | ndx_real S | Δ iter011 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `intl_lite_35253010`     | 10% | 1.055 | +0.009 | 0.885 | −0.075 | 1.052 | −0.052 |
| `intl_moderate_30202525` | 20% | 1.004 | −0.042 | 0.811 | −0.149 | 0.985 | −0.119 |
| `intl_balanced_25252525` | 25% | 0.995 | −0.051 | 0.781 | −0.179 | 0.953 | −0.151 |
| `intl_heavy_25302025`    | 30% | 0.989 | −0.057 | 0.744 | −0.216 | 0.917 | −0.187 |

Across the entire grid, intl-equity tilt **monotonically REDUCES Sharpe
on ALL 3 datasets** as VXUSSIM weight rises. This is a stronger structural
signal than iter 013 (where factor tilt monotonically helped lh_56y and
hurt live windows). intl-equity tilt is even less compatible with iter
011's architecture than US factor tilt was.

### Structural insight (why it's a dead-end)

1. **iter 011 is the architectural ceiling for constant-weight stacks**:
   012 (RSSB) lost on all 3 datasets, 013 (VBRSIM) lost on 2 of 3, and
   014 (VXUSSIM) loses on 2 of 3 (with the lh_56y "win" inside noise).
   3 consecutive sleeve-injection iters confirm: any sleeve added to
   iter 011's NTSX+GDE+KMLM stack at constant weight DRAGS the deploy-
   relevant 2010-2026 windows.
2. **Treasury overlap was NOT the dominant iter 012 failure mode**:
   stripping RSSB's Treasury overlay (going to 1× VXUSSIM with zero
   Treasury) helps modestly on lh_56y (1.055 vs 1.011) but does NOT
   recover the iter 011 vt_real / ndx_real Sharpe. The intl-equity drag
   is an independent failure axis.
3. **Factor premium and intl-equity premium are BOTH dormant in 2010-2026**:
   the post-GFC US-large-cap regime is so dominant that any non-US,
   non-cap-weighted equity sleeve drags Sharpe.
4. **The score-vs-substance gap is real**: iter 014 scores 93 because
   the new lh_56y avg(SPY,VT) baseline is low (Sharpe 0.671), making
   it easy to beat by +0.10. But the deploy-relevant comparison is vs
   iter 011 (Sharpe 0.96-1.10 on live windows), and iter 014 fails that.

### What CAN be tried instead

- **B.6 — Regime-conditional factor tilt** (highest priority): VBRSIM
  weight = f(value spread or factor momentum signal). Pre-commit ≤ 3
  configs. The factor sleeve only fires when the premium is "live"; KMLM/
  GDE cover otherwise. `[advances_fin_ml, p.208-211]` discipline + `[risk_parity, ch.2]`.
- **A.1 — NTSI / NTSE proxy synthesis** (deferred dependency): build
  testfolio-style synth for NTSI (1.5× intl developed) and NTSE (1.5× EM)
  so the literal user thesis (5-asset NTSX + NTSI + NTSE + GDE + KMLM
  global stack) becomes testable. Needed for direction A.1.
- **C — Replace iter 011 sleeves, not augment** (architectural pivot):
  swap NTSX out for NTSI entirely; test whether the leverage architecture
  transports across geographies. Structurally different from iter 012/013/014
  (which all augment iter 011 with a new sleeve).
- Antonacci GEM-style cross-class top-K (iter 079 archive style) or
  vol-managed 60/40 (iter 006 archive) as completely different mechanism.

### Results summary

Selected: `intl_lite_35253010` = 35% NTSX + 10% VXUSSIM + 25% GDE + 30% KMLM.

| dataset | gross Sharpe | gross CAGR | gross MDD | Gates | DSR p |
|---|---:|---:|---:|---:|---:|
| lh_56y    | 1.055 | 11.78% | 29.52% | 6/7 | 7.74e-12 |
| vt_real   | 0.885 | 11.14% | 27.99% | 7/7 | 3.66e-3 |
| ndx_real  | 1.052 | 12.11% | 18.40% | 7/7 | 8.53e-4 |

Net ≈ gross (static stack, year-end DARF, daily-Sharpe tax-neutral).

---

## DE-016 — A.1 — 5-asset global capital-efficient stack (NTSX + NTSI + NTSE + GDE + KMLM, component-swap inside the 1.5× wrapper)

**Origin**: long_term_portfolio iter 015 — A1-5asset-global-stack
(2026-04-28). Pivot from sleeve-injection failures (012 RSSB / 013
VBRSIM / 014 VXUSSIM) to **architectural rebalance** of the equity
sleeve INSIDE the 1.5× capital-efficient wrapper. Tested the literal
user thesis (NTSX + NTSI + NTSE + GDE + KMLM, 5-asset global stack)
by synthesizing NTSI/NTSE testfolio-style for the first time:

  - NTSI = 0.90 VEASIM + 0.60 IEFSIM − 0.50 CASHX  (intl-developed 1.5× stack)
  - NTSE = 0.90 VWOSIM + 0.60 IEFSIM − 0.50 CASHX  (EM 1.5× stack)

Same 90/60/−50 WisdomTree blueprint as NTSX (validated deploy_studies
2026-04-26). New shared module `studies/long_term_portfolio/proxies.py`
hosts the synth.

### Pre-committed grid

Mix of 4-asset (no NTSE, full lh_56y) and 5-asset (with NTSE, 1994+
eff via VWOSIM bottleneck) to isolate EM-as-component contribution:

  - `intl_dev_3025_GK_2025`        = 30% NTSX / 25% NTSI / 0% NTSE / 20% GDE / 25% KMLM (4-asset)
  - `intl_dev_lite_3515_GK_2030`   = 35% NTSX / 15% NTSI / 0% NTSE / 20% GDE / 30% KMLM (4-asset)
  - `global_lit_3015_10_GK_2520`   = 30% NTSX / 15% NTSI / 10% NTSE / 25% GDE / 20% KMLM (5-asset)
  - `global_em_heavy_2520_15_2020` = 25% NTSX / 20% NTSI / 15% NTSE / 20% GDE / 20% KMLM (5-asset)

Selected: `intl_dev_lite_3515_GK_2030` (4-asset variant) by max mean
selection rule.

### Why it's a dead-end

#### KILL #2 fired: 5-asset configs uniformly Sharpe-regress vs 4-asset

| metric | best 4-asset | best 5-asset | Δ |
|---|---:|---:|---:|
| lh_56y    | 1.081 | 0.964 | −0.117 |
| vt_real   | 0.877 | 0.796 | −0.081 |
| ndx_real  | 1.048 | 0.974 | −0.074 |

EM exposure within the 1.5× wrapper is structurally subordinate to no-EM
variants on every dataset.

#### KILL #3 fired: cross-config monotonic regression with intl-equity weight

| config | NTSI+NTSE % | lh_56y S | vt_real S | ndx_real S |
|---|---:|---:|---:|---:|
| `intl_dev_lite_3515_GK_2030`   | 15% | **1.081** | **0.877** | **1.048** |
| `intl_dev_3025_GK_2025`        | 25% | 1.034 | 0.820 | 0.995 |
| `global_lit_3015_10_GK_2520`   | 25% | 0.964 | 0.796 | 0.974 |
| `global_em_heavy_2520_15_2020` | 35% | 0.958 | 0.739 | 0.915 |

Sharpe monotonically decreases on ALL 3 datasets as intl-equity weight rises.
Same monotonic pattern as iter 014 (VXUSSIM at 1× notional outside wrapper) —
now confirmed inside the leveraged wrapper too.

### Comparison vs iter 011 (substantive incumbent)

| dataset | iter 015 selected | iter 011 (loose) | Δ vs iter 011 (loose) | iter 011 (strict) | Δ vs iter 011 (strict) |
|---|---:|---:|---:|---:|---:|
| lh_56y    | 1.081 | 1.046 | **+0.035** | 1.045 | **−0.038** (strict, honest) |
| vt_real   | 0.877 | 0.960 | **−0.083** | n/a   | (strict ≈ loose, no NaN legs) |
| ndx_real  | 1.048 | 1.104 | **−0.056** | n/a   | (strict ≈ loose, no NaN legs) |

Loose convention (used by 011/012/013/014/015 for cross-iter consistency)
gives a +0.035 win on lh_56y, but this is an artifact of partial-stack
pre-1986 Sharpe inflation. Strict convention (drops rows with any-leg-NaN)
shows iter 015 LOSES iter 011 on ALL 3 datasets.

### Comparison vs iter 014 (mechanical incumbent)

| dataset | iter 015 | iter 014 | Δ vs iter 014 |
|---|---:|---:|---:|
| lh_56y    | 1.081 | 1.055 | +0.026 (within noise) |
| vt_real   | 0.877 | 0.885 | −0.008 |
| ndx_real  | 1.048 | 1.052 | −0.004 |

Score TIES at 93=93, fails the +0.10 Sharpe-edge gate on all 3.

### Structural insight (why it's a dead-end)

1. **Direction A is now CLOSED end-to-end.** Both structural variants of
   the global+factor thesis on iter 011's architecture have been exhausted:
     - **Sleeve-add** (012 RSSB / 013 VBRSIM / 014 VXUSSIM): adding a
       constant-weight sleeve at 1× or 2× notional outside the wrapper
       drags every live window.
     - **Component-swap** (015 NTSI/NTSE): moving the equity sleeve from
       US to intl inside the 1.5× wrapper drags every live window.
2. **The lesson is now overdetermined** (4 consecutive iters, same
   conclusion): the 2010-2026 US-large-cap-dominant regime is so strong
   that ANY deviation from pure US equity in the equity sleeve costs
   Sharpe — whether the deviation is at 1× notional outside the wrapper
   or at 1.5× notional inside it.
3. **Iter 011 NTSX is the architectural ceiling for static cap-efficient
   stacks in this regime.** Pure-US equity in the leveraged wrapper +
   GDE + KMLM is genuinely the local optimum.
4. **EM-as-component is independently dead** (KILL #2): NTSE adds no
   value at any tested weight, even inside the wrapper. EM premium is
   too dormant in 2010-2026 to justify the basis-point allocation.

### What CAN be tried instead

- **B.6 — Regime-conditional factor tilt** (highest priority): VBRSIM
  weight = f(value spread or factor momentum 12-1). Pre-commit ≤ 3
  configs. Factor sleeve only fires when premium is "live"; KMLM/GDE
  cover otherwise. `[advances_fin_ml, p.208-211]` (PBO discipline) +
  `[risk_parity, ch.2]` (factor framework). Carries DSR-regression
  trap risk from strategy_hunt_loop "regime gate on existing winner"
  experience — must keep grid small.
- **C — Fundamentally different mechanism**: Antonacci GEM cross-class
  top-K (iter 079 archive style) or vol-managed 60/40 (iter 006
  archive). Different optimization target entirely. Would break out
  of the static-cap-efficient-stack frame that iter 011 anchors.
- **Stop hunting; declare iter 011 deploy-ready**: 4 consecutive iters
  fail to substantively beat iter 011, the literature thesis has been
  fully tested at the static-stack level. Defensible to prepare
  mandate §7 override request and reactivate hunting in 6-12 months
  when post-2026 OOS data is meaningful.

### Results summary

Selected: `intl_dev_lite_3515_GK_2030` = 35% NTSX + 15% NTSI + 20% GDE + 30% KMLM (4-asset variant).

| dataset | gross Sharpe (loose) | gross Sharpe (strict) | gross CAGR | gross MDD | Gates | DSR p |
|---|---:|---:|---:|---:|---:|---:|
| lh_56y    | 1.081 | 1.007 | 11.63% | 27.99% | 6/7 | 2.03e-12 |
| vt_real   | 0.877 | 0.877 | 10.64% | 26.50% | 7/7 | 4.00e-3  |
| ndx_real  | 1.048 | 1.048 | 11.57% | 17.54% | 7/7 | 9.03e-4  |

Net ≈ gross (static stack, year-end DARF, daily-Sharpe tax-neutral).

---

## DE-017 — B.6 — VBRSIM regime-gated factor tilt (worse than constant-weight iter 013)

**Origin**: long_term_portfolio iter 017 — B6-VBRSIM-regime-gated (2026-04-28).

Test: does a binary regime gate on VBRSIM (weight = 25% when signal ON, 0% when OFF, KMLM absorbs slack) recover iter 013's lh_56y advantage without the live-window cost?

3 pre-committed configs (≤3 to limit DSR penalty per `[advances_fin_ml, p.222-223]`):
- mom12: VBRSIM trailing 12-1m return > 0
- value: VBRSIM trailing 36m Sharpe > 0.5
- dual: mom12 OR value

Selected: `vbrsim_value` (pct_on avg 66%).

### Why it's a dead-end

Regime gate makes things **worse** than constant-weight iter 013 on EVERY dataset:

| dataset | iter 013 (constant) | iter 017 (gated) | Δ |
|---|---:|---:|---:|
| lh_56y | 1.126 | 1.043 | **−0.083** |
| vt_real | 0.923 | 0.884 | −0.039 |
| ndx_real | 1.075 | 0.967 | **−0.108** |

Three failure mechanisms:
1. **Signal lag**: 36m Sharpe / 12-1m return turn ON 6-12m after the regime starts, missing the early premium reset.
2. **Whipsaw cost**: ON→OFF→ON transitions are rebalances; +5-15bp/yr in deploy via DARF.
3. **Regime classification noise**: ~30y data → wide CIs on Sharpe estimates → gate fires on noise.

Classic "regime-gate-on-existing-winner" DSR-regression trap that PBO discipline (López de Prado p.208-211) was designed to detect. PBO doesn't fire here only because N=3 triggers the framework's CSCV-instability warning.

### KILL #1 fired

Best-of-grid loses iter 011 substantively on 3/3 strict AND fails to match iter 013's +0.080 lh_56y advantage (iter 017 is +0.003 vs iter 013's +0.080).

### Family-level conclusion

**B-direction is now CLOSED end-to-end**:
- B.4 constant-weight VBRSIM (iter 013): tier WINNER but no advance vs iter 011
- B.5 UMD overlay direct (iter 016): WINNER tier 91/100, **first positive signal — only B-direction with real edge**
- B.6 VBRSIM regime-gated (iter 017): STRONG, worse than B.4

The only B-direction with a genuine substantive edge is **B.5 UMD overlay**.

### What CAN be tried instead

- Investable momentum sub-iter (deferred): test MTUM/SPMO/IDMO live (2013+) instead of academic UMD; quantify how much B.5 edge survives long-only constraint + transaction costs.
- C-direction breadth (iters 018-022 per the loop plan).

### Results summary

Selected: `vbrsim_value` = signal `VBRSIM 36m Sharpe > 0.5`, weights ON/OFF skeletons.

| dataset | gross Sharpe (loose) | gross Sharpe (strict) | gross CAGR | gross MDD | gates |
|---|---:|---:|---:|---:|---:|
| lh_56y | 1.043 | 0.970 | 12.15% | 26.39% | 5/7 |
| vt_real | 0.884 | 0.886 | 11.20% | 22.49% | 6/7 |
| ndx_real | 0.967 | 0.969 | 11.37% | 22.49% | 6/7 |

`[advances_fin_ml, p.208-211]`, `[stocks_on_the_move, p.21-30]`, `[risk_parity, ch.5, p.10]`

---

## DE-018 — C.1 — Antonacci GEM cross-class top-K (testfolio universe)

**Origin**: long_term_portfolio iter 018 (2026-04-28).

4 configs varying universe (5/6/7-asset) and K (top-K). Selected `gem_6asset_K2` (SPY/QQQ/VEA/TLT/GLD/KMLM, K=2, fallback KMLM).

**Why it's a dead-end**: best-of-grid (Sharpe 0.763/0.888/0.889) loses iter 011 substantively on lh_56y (−0.283) and ndx_real (−0.215). Only vt_real positive (+0.182, helped by 2008 crisis rotation). Sharpe-edge winner condition fails (only 1/3 +0.10).

Tier PROMISING 74/100, **winner_conditions_met=FALSE**.

**KILL #1 fired**.

**Why iter 079 archive (similar approach) was a winner but iter 018 isn't**:
1. iter 079 universe was wider (8-12 equity diversifiers); iter 018 only 5-7 broad asset classes.
2. iter 079 evaluated on Tiingo SPY 17y only; iter 018 includes lh_56y where 14y of US-equity dominance penalize monthly switching.
3. iter 079 may have used 1m/3m lookback; iter 018 uses 12-1m (Antonacci classic — known to lag in rapid regime shifts).

`[stocks_on_the_move, ch.6]`, Antonacci 2014.

---

## DE-024 — B.2 — MDD-trigger defensive (rare-event regime gate)

**Origin**: long_term_portfolio iter 024 (2026-04-29).

3 pre-committed configs (≤3 to limit DSR penalty per advances_fin_ml p.222):
mdd_trigger_10pct_TLT, _15pct_TLT, _15pct_CASH. Forward-looking signal
(`pct_change(21).shift(1)` — no peek). When SPY 21d < threshold, reduce 50%
NTSX, add 17.5% TLT or CASH defensive sleeve.

Selected `mdd_trigger_10pct_TLT`. Gross Sharpe 1.145 / 0.982 / 1.123. NEW
STRONG 82/100 winner_conds=True, LEGACY STRONG 87/100. vs iter 011: +0.099 /
+0.022 / +0.019 loose (3/3 marginal positive).

**Why it's a dead-end**: trigger fires only 1-2% of trading days (10% threshold
on SPY 21d return is rare event). Strategy is iter 011 base 99% of time +
brief defensive shifts during 2008/2020/2022. **Dominated by iter 023 TLT-static**
in every dataset:
- lh_56y: iter 023 1.189 > iter 024 1.145 (Δ +0.044)
- vt_real: 1.004 > 0.982 (Δ +0.022)
- ndx_real: 1.135 > 1.123 (Δ +0.012)

PBO N=3 warning (CSCV unstable below N=4) reported informationally.

**Lesson**: rare-event regime trigger fires too rarely to drive significant
alpha in long-history portfolio mandate. Continuous defensive sleeve (iter 023)
captures duration alpha better than gated defensive shift. **Direction B.2
(regime-trigger defensive on iter 011) closed.**

`[risk_parity, ch.5, p.10]`, `[systematic_trading, p.137-148]` Carver,
`[advances_fin_ml, p.208-211, p.222-223]`.

---

## DE-025 — B.3 — Continuous tail-hedge with deployable VXX

**Origin**: long_term_portfolio iter 025 (2026-04-29).

4 configs sweep VXX 2.5/5/7.5/10% on iter 011 base, substituting from KMLM.
**Methodological diagnostic** to quantify gap between iter 022's synthetic
+5pp Sharpe model artifact and deployable reality (VXX real, Tiingo cache,
inception 2009-01-30).

Pre-run no-free-lunch sanity check ✅: VXX standalone Sharpe **−0.738**, CAGR
**−51%/yr**, MDD **−100%** (legitimate destroyer of capital).

Selected `vxx_lite_3525_375_25` (2.5% VXX). Gross Sharpe 1.107 / 0.921 / 1.097.
NEW STRONG 83/100 (2/3 +0.05 vs SPY; vt_real misses by 0.029), LEGACY WINNER
93/100. vs iter 011: +0.061 / **−0.039** / **−0.007** (1/3 positive substantively).

**KILL #1 (no-free-lunch monotonic) ✅ PASS**: Sharpe DECREASES monotonically
as VXX% rises 2.5% → 10% in ALL 3 datasets:
- lh_56y: 1.107 → 0.982 (Δ −0.125 over 7.5pp)
- vt_real: 0.921 → 0.641 (Δ −0.280)
- ndx_real: 1.097 → 0.854 (Δ −0.243)

**Quantified gap iter 022 synthetic vs iter 025 real (10% hedge)**:
- lh_56y: 1.520 → 0.982 (Δ −0.538)
- vt_real: 1.710 → 0.641 (Δ −1.069)
- ndx_real: 1.684 → 0.854 (Δ −0.830)

iter 022 synthetic model **overstated Sharpe by 0.5-1.1 points** across
datasets — confirms iter 022 score 100/100 was 100% model failure (4 bugs
documented: hindsight via 21d trigger, no vega cost, wrong path-dependence,
no spread/liquidity drag).

**Lesson**: continuous tail-hedge with deployable VXX is a net Sharpe loss
at every tested weight. Spitznagel's Universa real-implementation +1-2pp
CAGR uplift requires OTM puts + short-vol overlay, not VXX alone. iter 025
captures only the negative side of that ledger. **Direction B.3 (continuous
VXX hedge) closed.**

Spitznagel *Safe Haven* (2021); `[risk_parity, ch.5]`; `[advances_fin_ml,
p.208-211]` PBO + monotonic.

---

## DE-026 — B.4 — DATA-LIMITED dead-end (MTUM/SPMO/IDMO unavailable)

**Origin**: long_term_portfolio iter 026 (2026-04-29).

**Status**: backtest never run. Data unavailable.

**Plan**: test investable momentum (MTUM/SPMO/IDMO live) as deployable
substitute for iter 016's UMD academic factor (which showed +0.088 lh_56y
strict edge). 4 configs sweep MTUM 10-25% on iter 011 base.

**Pre-run inventory (2026-04-29 02:30 UTC)**:
- MTUM (iShares MSCI USA Momentum, live 2013-04+): ❌ Tiingo cache + ❌ testfolio
- SPMO (Invesco S&P 500 Momentum, live 2015-10+): ❌ ❌
- IDMO (Invesco S&P Intl Developed Momentum, live 2015-08+): ❌ ❌
- MTUMSIM (potential testfolio synth): n/a — not constructed
- TIINGO_API_KEY: ❌ empty (subscription cancelled)

Tiingo bulk download script (`scripts/tiingo_bulk_download.py`) inventory:
broad ETFs, sector SPDRs, bonds, commodities/vol, leveraged — **no factor ETFs**.

**Implications**:
1. iter 016 UMD academic edge (+0.088 lh_56y, +0.047 ndx_real, −0.016 vt_real
   strict) stays the standing momentum reference until investable data
   becomes available.
2. **B.5 momentum direction is paused, NOT closed** — per
   [stocks_on_the_move, p.21-30] Clenow + Frazzini-Israel-Moskowitz 2018
   (Trading Costs of Asset Pricing Anomalies), MTUM/SPMO capture ~60-70%
   of UMD edge after long-only constraint + 10-30bp/yr turnover.
   Estimated MTUM real edge: ~+0.05 lh_56y, marginal but positive.
3. Reactivation requires Tiingo subscription resumption OR MTUMSIM
   testfolio synth construction (would need iShares prospectus + MSCI
   Momentum Index history).

Similar to DE-021 (sector rotation 4-asset, Tiingo limited to 4 sectors
with full history). iter 026 has zero data, so no run was attempted.

`[stocks_on_the_move, p.21-30]` Clenow; Frazzini-Israel-Moskowitz 2018;
iter 016 UMD academic — proxy result.
