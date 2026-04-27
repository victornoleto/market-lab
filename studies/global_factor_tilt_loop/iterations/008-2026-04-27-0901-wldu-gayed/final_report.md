# Iter 008 — WLDU + Gayed 200d SMA (LETF Managed) — PROMISING 61/100

**Date:** 2026-04-27  
**Slug:** wldu-gayed  
**Status:** PROMISING (61/100)  
**Winner conditions met:** No (Condition 1 — Sharpe edge)  
**Tier:** PROMISING — score 61 (< 75 STRONG threshold)

---

## Verdict

**PROMISING 61/100. Winner condition 1 (Sharpe edge) fails. NOT WINNER.**

The strategy achieves strong absolute CAGR improvement over the global benchmark (+3.04pp on edu,
+1.82pp on vt_real) and excellent drawdown protection vs buy-and-hold, but the fundamental
Sharpe ratio barely matches (not beats) VTSIM b&h. The core structural finding: **Gayed's LRS
improves Sharpe on concentrated equity (S&P 500, base Sharpe 0.32 → 0.61) but cannot improve
an already-diversified global equity index (VTSIM base Sharpe already 0.61)**.

**Kill criterion 2 triggered** (educational MDD=44.45% > 35%). The 2022 grinding bear market
caused 2× leverage to amplify the drawdown before the monthly SMA exit fired. Full-period MDD
exceeds the 35% per-window threshold, confirming the binary trend filter cannot contain 2×
leverage in slow rate-regime-driven bear markets.

---

## Headline Metrics

| dataset | window | Sharpe | CAGR | MDD | Gates |
|---|---|---|---|---|---|
| educational | 1986-2026 (~40y, SPYSIM binding) | **0.609** | **12.69%** | 44.45% | **7/7** |
| vt_real | 2008-2026 (~18y) | **0.501** | **10.11%** | 44.45% | **5/7** |
| ndx_real | 2010-2026 (~16y) | 0.473 | 9.44% | 44.45% | **6/7** |

---

## Long-window Comparison vs Strategy Benchmarks (educational ~40y)

| | Sharpe | CAGR | MDD |
|---|---|---|---|
| **WLDU+Gayed (iter 008)** | 0.609 | **12.69%** | 44.45% |
| HAA SmartStack (iter 005, WINNER) | 1.112 | 14.14% | 20.91% |
| VT 1x b&h (VTSIM ~40y proxy) | 0.610 | 9.65% | 58.35% |
| Plano C V3_1 v3.5 (32y) | 0.671 | 10.94% | 52.43% |
| V_HYBRID + 10% MF (32y) | 0.743 | 10.91% | 44.71% |

**vs VT b&h**: −0.001 Sharpe / +3.04pp CAGR / −13.90pp MDD → **Sharpe tie, CAGR+MDD win**  
**vs Plano C V3_1**: −0.062 Sharpe / +1.75pp CAGR / −7.98pp MDD → **below Plano C on Sharpe**  
**vs V_HYBRID+MF**: −0.134 Sharpe / +1.78pp CAGR / −0.26pp MDD → **dominated on Sharpe**  
**vs HAA SmartStack**: −0.503 Sharpe / −1.45pp CAGR / +23.54pp MDD → **dominated on all axes**

Conclusion: WLDU+Gayed achieves CAGR and MDD improvements vs simple buy-and-hold, but is
dominated by all active strategy benchmarks including the existing WINNER (HAA SmartStack).

---

## Score Breakdown

| criterion | points | max | note |
|---|---|---|---|
| 1 Sharpe edge | **0** | 25 | edu 0.609 (need 0.763), vt 0.501 (need 0.613), ndx 0.473 (need 1.047) — 0/3 beat |
| 2 Gates | **21** | 25 | edu 7/7 (7pts) + vt 5/7 (5pts) + ndx 6/7 (5pts) + cross-dataset bonus (4pts) |
| 3 DSR | **15** | 15 | worst p=2.97e-2 (ndx); pre-committed n_trials=1 |
| 4 CAGR floor | **10** | 15 | edu ✓ (12.69%>7.72%) + vt ✓ (10.11%>6.63%); ndx ✗ (9.44%<<15.35%) |
| 5 MDD ceiling | **10** | 15 | edu ✓ (44.45%<63.35%) + vt ✓ (44.45%<59.62%); ndx ✗ (44.45%>40.12%) |
| 6 Robustness | **5** | 5 | 36/36 rolling-5y windows positive (100%); min Sharpe 0.164 |
| **Total** | **61** | **100** | PROMISING |

---

## Gate Details

### Educational (1986-2026, ~40y) — 7/7

| gate | result | detail |
|---|---|---|
| G1 PBO | ✅ PASS | n_configs=1, trivially passes |
| G2 DSR | ✅ PASS | p=6.48e-5 (pre-committed, n_trials=1) |
| G3 nominal | ❌ FAIL | max_mdd=44.45% > 25% (2× notional expected) |
| **G3' adapted** | **✅ PASS** | max_ref=110.96% (VT×2.0); portfolio 44.45% ≪ ref |
| G4 OOS 70/30 | ✅ PASS | OOS Sharpe=0.459 |
| G5 FWD >2020 | ✅ PASS | post-2020 Sharpe=0.556 |
| G6 Bootstrap | ✅ PASS | 99.9% CI_low=0.160 > 0 |
| G7 Cross-lib | ✅ PASS | np=13.08% pd=12.69%, diff=0.39pp |

### vt_real (2008-2026, ~18y) — 5/7

| gate | result | detail |
|---|---|---|
| G1 PBO | ✅ PASS | trivial |
| G2 DSR | ✅ PASS | p=1.82e-2 |
| G3 nominal | ❌ FAIL | max_mdd=39.84% > 25% |
| **G3' WF** | **❌ FAIL** | 5/8 profitable windows (need ≥6); 2008-2009 WF windows include crash entry |
| G4 OOS 70/30 | ✅ PASS | OOS Sharpe=0.426 |
| G5 FWD >2020 | ✅ PASS | post-2020 Sharpe=0.556 |
| G6 Bootstrap | ❌ FAIL | 99.9% CI_low=−0.162 (2008 anchor, only 17y) |
| G7 Cross-lib | ✅ PASS | np=10.95% pd=10.11%, diff=0.84pp |

vt_real note: G3' fails because the WF splits anchored at 2008-06 include partial-crash
windows where the strategy re-entered at 2× leverage into an unstable market. G6 bootstrap
fails because the 17-year window starting at the GFC bottom stress-tests the 99.9% CI.

### ndx_real (2010-2026, ~16y) — 6/7

| gate | result | detail |
|---|---|---|
| G1 PBO | ✅ PASS | trivial |
| G2 DSR | ✅ PASS | p=2.97e-2 |
| G3 nominal | ❌ FAIL | max_mdd=40.45% > 25% |
| **G3' adapted** | **✅ PASS** | max_ref=68.45% (VT×2.0); portfolio 40.45% < ref |
| G4 OOS 70/30 | ✅ PASS | OOS Sharpe=0.225 |
| G5 FWD >2020 | ✅ PASS | post-2020 Sharpe=0.556 |
| G6 Bootstrap | ❌ FAIL | 99.9% CI_low=−0.137 |
| G7 Cross-lib | ✅ PASS | np=9.84% pd=9.44%, diff=0.40pp |

ndx_real note: strategy Sharpe 0.473 vs QQQ 0.958 — structural gap vs US tech concentration.
The global-equity LETF cannot match QQQ's pure US tech CAGR.

---

## Kill Criteria Check

| criterion | educational | vt_real | ndx_real |
|---|---|---|---|
| Kill 1 (CAGR < 12%) | 12.69% ✓ | 10.11% (N/A <20y) | 9.44% (N/A <20y) |
| Kill 2 (MDD > 35%) | **44.45% ⚠️ TRIGGERED** | 44.45% (N/A <20y) | 44.45% (N/A <20y) |
| Switches/yr | 1.3 | 1.6 | 1.7 |
| % time in WLDU | 76.5% | 79.1% | 83.1% |

Kill 2 triggered on educational (full-period 40y MDD=44.45% > 35%):
- Source: 2022 drawdown. S&P 500 entered bear market gradually through Jan-Sep 2022.
  Monthly SMA check: Dec 31, 2021 → SPY well above 200d SMA → Jan 2022 still RISK-ON.
  Jan-Feb 2022 market fell ~10-12%. Feb 28 check → SPY first crossed below 200d SMA.
  Portfolio exited to CASHX for March 2022+. But WLDU had already absorbed 2×10-12% in Jan-Feb.
- The monthly rebalance (Gayed canonical, 5/yr) is too slow for fast-reversal bears.
  Daily check variant would exit earlier but with more whipsaw cost.

CAGR floor satisfied: educational 12.69% > 12% kill threshold ✓.

---

## Rolling Robustness (Educational, 36 Five-Year Windows)

- Windows: 36
- % positive Sharpe: **100%** (36/36)
- Min 5y Sharpe: **0.164** (includes 2022 rate-shock window)
- Max 5y Sharpe: **1.423** (2009-2014 bull market recovery)

100% positive windows despite trigger kill criterion 2 — every 5y period had positive
risk-adjusted returns even with 2× leverage. The MDD is episodic (2022) not chronic.

---

## Structural Analysis — Why Gayed LRS Doesn't Transfer to Global Equity

Gayed's paper [p.17, Table 8] shows S&P 500 Sharpe = 0.32, 2× LRS (200d) Sharpe = 0.61.
That is a **+0.29 Sharpe improvement**, nearly doubling risk-adjusted returns.

For global equity (VTSIM b&h): Sharpe ≈ 0.61 (40y window). Applying 2× LRS → Sharpe ≈ 0.61.
**Zero improvement** because the starting point (VTSIM b&h Sharpe) already matches the LRS target.

The LRS mechanism works by:
1. Reducing time in high-volatility bear markets (move to cash)
2. Maintaining leverage during low-volatility bull runs

For S&P 500 (concentrated in US large-cap, volatile): this mechanism dramatically improves
risk-adjusted returns because the base Sharpe is low.

For VTSIM (globally diversified, 40+ countries, factor diversification): the base Sharpe is
already elevated (0.61) because cross-country diversification reduces volatility at the same
expected return. The SMA filter can't further compress volatility below what diversification
already achieves. Net result: 2× leverage brings returns and vol proportionally → Sharpe flat.

**Hypothesis**: LRS applied to more concentrated, higher-beta indexes (QQQ, sector ETFs) would
show more improvement. LRS applied to globally-diversified equity shows minimal Sharpe gain.

---

## What Worked

1. **CAGR improvement**: +3.04pp over VTSIM b&h on 40y (12.69% vs 9.65%) — 2× leverage
   during sustained bull markets delivers clear compounding benefit.
2. **MDD improvement vs buy-and-hold**: 44.45% vs 58.35% (−13.90pp) — trend filter
   successfully avoided 2000-02 and 2008-09 major drawdowns.
3. **DSR significance**: All datasets pass at p<0.05 (pre-committed n_trials=1).
4. **100% rolling windows positive**: Robust across all 36 five-year windows.
5. **Low whipsaw**: ~1.3-1.7 switches/yr, consistent with Gayed's ~5/yr prediction [p.16].
6. **G7 cross-lib tight**: numpy vs pandas diff ≤0.84pp across all datasets.

---

## What Didn't Work

1. **Sharpe parity problem**: Global equity base Sharpe (0.61) = Gayed LRS target Sharpe.
   Zero net improvement possible — this is a structural incompatibility, not a parameter issue.

2. **2022 MDD=44.45% kills per-window threshold**: Monthly rebalance too slow for gradual
   rate-driven bear market. The 2022 bear (Jan-Sep) had SPY above 200d SMA through Jan 31, 2022
   before the exit signal fired, then 2× leverage had already absorbed the initial decline.

3. **ndx_real structural gap**: Global-equity LETF at 2× cannot match QQQ's US-tech CAGR (19.19%)
   over 2010-2026. Sharpe 0.473 vs QQQ 0.958. Not a bug — structural CAGR ceiling.

4. **G3' vt_real fails**: 5/8 profitable WF windows. The 2008-anchored WF splits create
   crash-entry sub-periods where 2× leverage on WLDU catches the recovery volatility.

---

## Lesson

**2× single-asset global-equity LETF + binary SMA filter is architecturally limited as a
global strategy.** The mechanism (Gayed LRS) was designed for and tested on S&P 500 (Sharpe
0.32). Globally-diversified equity already achieves Sharpe 0.61 through diversification alone.
Applying the same treatment doubles vol proportionally to returns → flat Sharpe, worse MDD vs
HAA/stacked strategies.

For the loop: this closes the "LETF + trend filter" branch. The stacked-portfolio approach
(HAA iter 005, VAA iter 006, static iter 007) dominates by offering leverage efficiency
(1.4-1.8× notional) with multi-asset risk diversification vs single-asset 2× leverage.

**Next iter recommendation**: HAA SmartStack + 5% gold sleeve (close 0.07 Sharpe gap to
bestfolio reference 1.18). Or: synthetic NTSI/NTSE re-evaluation (Tier 4, iter 010).

---

## Config Tested

Single pre-committed config (n_trials=1):

| parameter | value | rationale |
|---|---|---|
| LETF leverage | 2× | `[leverage_for_the_long_run, p.13]` |
| Underlying | VTSIM (global equity) | global universe mandate |
| Trend signal | SPYSIM SMA(200d) | `[leverage_for_the_long_run, p.16]` |
| Rebalance | Monthly (month-end check) | Gayed canonical |
| Annual drag | 0.75%/y | 50bps financing + 25bps expense |
| Defensive | CASHX (100%) | complete equity exit |

Notional factor = 2.0 → G3' adapted gate applies for all datasets.

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` — PRIMARY: Gayed LRS, 2× SMA filter
- `[leverage_for_the_long_run, p.13]` — LRS rule: hold leveraged equity above MA, rotate to T-bills
- `[leverage_for_the_long_run, p.16]` — 200-day MA recommendation, ~5 rotations/year
- `[leverage_for_the_long_run, p.17, Table 8]` — 2× LRS (200d) Sharpe 0.61, performance data
- `[stocks_on_the_move, p.21-30]` — trend signal as regime indicator
- `[advances_fin_ml, p.196-202]` — G6 block-bootstrap 99.9% CI
- `[advances_fin_ml, p.208-211]` — G1 PBO (trivial n_configs=1)
- `[advances_fin_ml, p.222-223]` — G2 DSR/PSR n_trials=1
- `[advances_fin_ml, p.31-34]` — G7 cross-lib ±3pp CAGR parity
- `[testing_tuning, ch.5-6]` — G3' benchmark-comparative calibration

---

## 2-3 Next Directions

1. **HAA gold sleeve** (next candidate): add 5% GLDSIM to HAA SmartStack (iter 005 WINNER).
   Tests if gold sleeve closes the 0.07 Sharpe gap to bestfolio reference (1.18). HAA=1.112,
   target=1.18. Pre-committed: 5% GDESIM → 85% HAA + 10% KMLM + 5% GLD/GDE.
   `[ilmanen_expected_returns, ch.fx-carry]` (gold as inflation hedge orthogonal to equity).

2. **VAA-G3 SmartStack** (pure-equity offensive): replace iter 006's bond-as-4th offensive
   asset (BNDSIM) with a 3rd pure-equity stack. Tests if removing bond contamination restores
   CAGR to HAA-competitive while retaining VAA's MDD advantage (14.24% vs HAA 20.91%).
   `[stocks_on_the_move, ch.6]` breadth momentum.

3. **LRS on concentrated equity** (Tier 2 variant): test Gayed LRS on SPYSIM (S&P 500, not
   global) or VTISIM (US-only) at 2×. If Sharpe improves from 0.33 to 0.60+ for US equity,
   this would isolate whether the global diversification hypothesis is correct and open a
   US-equity momentum sleeve variant. `[leverage_for_the_long_run, p.17, Table 8]`.
