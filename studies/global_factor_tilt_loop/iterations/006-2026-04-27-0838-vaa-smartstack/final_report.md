# Iter 006 — VAA-G4 SmartStack — STRONG 85/100

**Date:** 2026-04-27  
**Slug:** vaa-smartstack  
**Status:** STRONG  
**Score:** 85/100  
**Tier:** STRONG  
**Winner conditions met:** No (CAGR floor fails 2/3 datasets)  
**Kill 1 triggered:** edu Sharpe 1.052 ≤ HAA 1.112 → structurally subordinate to HAA SmartStack

---

## Verdict

VAA-G4 SmartStack achieves **STRONG** status — passes all 7/7 gates across all 3 datasets,
delivers Sharpe well above VT/Plano C/V_HYBRID+MF on all datasets, and shows exceptional
MDD control (14.24% across all 3 datasets, vs HAA's 20.91%/15.05%). However it falls short
of **WINNER** on two counts:

1. **CAGR sacrifice is structural**: The breadth momentum rule with BNDSIM as the 4th
   offensive asset creates chronic partial-defensive allocation whenever bonds have negative
   momentum (rising rates). CAGR 6.53% on vt_real and 5.23% on ndx_real both miss the
   scoring floor (7.04% and 15.19% respectively). This is not a minor miss — CAGR is 14pp
   below HAA on educational (8.26% vs 14.14%).

2. **Kill criterion 1 triggered**: edu Sharpe 1.052 ≤ 1.112 (HAA SmartStack). VAA is
   structurally subordinate to HAA for risk-adjusted returns, even with the added gold sleeve.

The strategy is not a dead-end: it holds genuine value as a **maximum-drawdown-protection
variant** (14.24% MDD at acceptable Sharpe ~1.05) and confirms that all 7 gates are
simultaneously passable on this universe. But HAA is the dominant architecture.

---

## Headline metrics

| dataset | window | Sharpe | CAGR | MDD | Gates |
|---|---|---|---|---|---|
| educational | 1995-2026 (31y) | **1.0524** | 8.26% | **14.24%** | **7/7** |
| vt_real | 2008-2026 (~17y) | **0.8502** | 6.53% | **14.24%** | **7/7** |
| ndx_real | 2010-2026 (16y) | 0.7329 | 5.23% | **14.24%** | **7/7** |

ndx_real CAGR (5.23% vs QQQ 19.19%) and Sharpe (0.733 vs 0.958) both miss benchmarks.
vt_real CAGR (6.53%) is 0.5pp below the 7.04% floor — the breadth rule's defensiveness
is the structural cause across all datasets.

---

## Score breakdown

| criterion | points | max | note |
|---|---|---|---|
| 1 Sharpe edge | 20 | 25 | edu✓ (+0.506) + vt_real✓ (+0.337); ndx_real✗ (−0.225 vs QQQ) |
| 2 Gates | 25 | 25 | 7/7 × 3 datasets + cross-dataset bonus |
| 3 DSR | 15 | 15 | worst p=2.44e-3 (ndx_real); pre-committed n_trials=1 |
| 4 CAGR floor | 5 | 15 | edu✓ (8.26% > 7.99%); vt_real✗ (6.53% < 7.04%); ndx_real✗ |
| 5 MDD ceiling | 15 | 15 | all 3 datasets pass with huge margin (14.24% vs 40-63% ceilings) |
| 6 Robustness | 5 | 5 | 26/26 rolling-5y windows positive (100%) |
| **Total** | **85** | **100** | STRONG |

---

## Long-window comparison vs benchmarks (31y educational)

| | Sharpe | CAGR | MDD |
|---|---|---|---|
| **VAA SmartStack (iter 006)** | **1.052** | 8.26% | **14.24%** |
| HAA SmartStack (iter 005, 31y) | 1.112 | 14.14% | 20.91% |
| VT 1x b&h (VTSIM 31y proxy) | 0.546 | 8.64% | 58.35% |
| Plano C V3_1 v3.5 (32y) | 0.671 | 10.94% | 52.43% |
| V_HYBRID + 10% MF (32y) | 0.743 | 10.91% | 44.71% |

Verdict vs benchmarks:
- vs VT: +0.506 Sharpe / −0.38pp CAGR / −44.1pp MDD → **Pareto trade-off** (Sharpe/MDD win, CAGR slight loss)
- vs Plano C V3_1: +0.381 Sharpe / −2.68pp CAGR / −38.2pp MDD → **Pareto trade-off**
- vs V_HYBRID+MF: +0.309 Sharpe / −2.65pp CAGR / −30.5pp MDD → **Pareto trade-off**
- vs HAA SmartStack: −0.060 Sharpe / **−5.88pp CAGR** / **−6.67pp MDD** → **dominated by HAA** (HAA wins on all axes except MDD, where VAA is 6pp lower — but HAA's MDD is already excellent)

**Assessment**: VAA Pareto-dominates all 3 mandated benchmarks on Sharpe + MDD axes. However,
it does NOT dominate HAA on any axis except MDD margin (where improvement is modest).
HAA is Pareto-dominant over VAA across all three axes simultaneously.

---

## Gate details

### Educational (1995-2026, 31y)

| gate | result | detail |
|---|---|---|
| G1 PBO | PASS | n_configs=1, trivially passes |
| G2 DSR | PASS | p=3.76e-9 (pre-committed, n_trials=1) |
| G3 WF (nominal) | PASS | 8/8 profitable, max WF window MDD=8.83% ≤ 25% |
| G3' (adapted) | PASS | max_ref=79.81% (VT×1.45); portfolio MDD well below |
| G4 OOS 70/30 | PASS | OOS Sharpe=0.836 |
| G5 FWD >2020 | PASS | post-2020 Sharpe=0.689 |
| G6 Bootstrap | PASS | 99.9% CI low=0.486 > 0 |
| G7 Cross-lib | PASS | np=8.23% pd=8.26%, diff=0.03pp ≪ 3pp |

### vt_real (2008-2026, 17y)

| gate | result | detail |
|---|---|---|
| G1-G7 | ALL PASS | 7/7; OOS Sharpe=0.480; G6 CI_low=0.192; G7 diff=0.10pp |
| G3 WF | PASS | 6/8 profitable (meets 6/8 threshold), max WF MDD=10.78% |

### ndx_real (2010-2026, 16y)

| gate | result | detail |
|---|---|---|
| G1-G7 | ALL PASS | 7/7; OOS Sharpe=0.465; G6 CI_low=0.073; G7 diff=0.26pp |
| G3 WF | PASS | 6/8 profitable, max WF MDD=8.83% |

---

## Rolling robustness (educational, 5-year sliding windows)

- Windows: 26
- % positive Sharpe: **100.0%** (26/26)
- Min 5y Sharpe: **0.426**
- Max 5y Sharpe: 1.955

All windows profitable. Min 5y Sharpe (0.426) is lower than HAA's (0.654) — VAA's
over-defensiveness hurts in pure bull-run windows where staying in bonds foregoes returns.

---

## Config tested

Single pre-committed config (n_trials=1, no grid):

- Offensive G4: NTSXSIM (US 90/60), NTSI (Intl 90/60), NTSE (EM 90/60), BNDSIM (bond ETF)
- Defensive G3: IEFSIM, CASHX, BNDSIM
- Signal: 13612W `(12·r1 + 4·r3 + 2·r6 + r12) / 19` monthly
- Breadth rule: B = count(offensive with signal > 0);
  offensive_fraction = B/4; top-B offensive equally weighted;
  (4-B)/4 to top-1 defensive
- Sleeve: KMLMSIM 10% + GLDSIM 5% = 15% fixed always-on
- Dynamic: 85% per breadth rule
- Rebalance: monthly (end-of-month)
- Notional factor: ~1.45× average (same as HAA)

---

## Root cause analysis: why CAGR falls short

### 1. BNDSIM as 4th offensive asset

In the original VAA-G4, AGG (bonds) is the 4th offensive asset specifically because the
strategy is designed to hold bonds as a "soft defensive" option when equities are mixed.
When we apply VAA to a stacked universe with NTSXSIM/NTSI/NTSE (1.5× equity stacks),
adding BNDSIM (1× bonds) creates an asymmetry:

- When equities are strong and bonds weak (2013-2018, post-QE): BNDSIM gets negative
  signal → B=3 → 25% of dynamic goes to IEFSIM/CASHX → 25% "wasted" on defensive when
  equities were the place to be.
- When all 4 are positive (B=4): 85% concentrates into top-1. If that top-1 is BNDSIM,
  85% ends up in bonds during a bond bull market — defensive even in risk-on mode.

### 2. 13612W signal vs HAA's unweighted average

HAA's unweighted (r1+r3+r6+r12)/4 is more persistent — the long-lookback periods moderate
the 1-month noise. The 13612W weights recent 1-month returns 12× more, creating more
turnover. In stable bull markets, the faster signal may oscillate defensive/offensive,
incurring more defensive cash periods.

### 3. Concentrating at B=4

HAA top-2 offensive gives 45%/45% split (diversified at maximum bullishness). VAA top-1
at B=4 concentrates 85% into a single asset — whichever has highest 13612W score. If that
asset is BNDSIM (bonds up in a flight-to-safety context), CAGR suffers.

---

## What worked

1. **MDD control**: 14.24% uniform across all 3 datasets. Even in 2008, 2020, 2022, the
   breadth mechanism scaled exposure down aggressively, capping drawdowns.

2. **Gate sweep**: 7/7 gates across all 3 datasets — the breadth mechanism + pre-committed
   config is highly statistically robust.

3. **Robustness**: 100% of rolling-5y windows profitable. All 3 DSR p-values well below 0.05.

---

## What didn't work

1. **CAGR sacrifice vs HAA**: 8.26% vs 14.14% on educational — the breadth rule + BNDSIM
   as 4th offensive is the structural cause.

2. **vt_real CAGR floor miss**: 6.53% vs 7.04% floor — marginal miss (0.51pp) but still
   below threshold.

3. **Kills HAA structural advantage claim**: VAA SmartStack was hypothesized as a possible
   advance over HAA's single canary. The data shows HAA remains superior on Sharpe + CAGR.
   The only edge VAA has is 6-7pp lower MDD (14.24% vs 20.91%) — modest when HAA is
   already excellent.

---

## Lesson

**VAA-G4 + bond-as-4th-offensive = chronic over-defensiveness when equities diverge from bonds.**
The breadth mechanism is valid and statistically robust, but BNDSIM in the offensive universe
creates systematic signal dilution. The fix is clear: use a pure-equity offensive universe
(VAA-G3 with NTSXSIM/NTSI/NTSE only, no bond) to test if breadth without bond contamination
improves CAGR to HAA-competitive levels.

**HAA single-canary architecture remains superior** because: (1) the canary is a dedicated
risk-indicator (VWOSIM = global EM, the most risk-sensitive asset), not a mixed-role asset;
(2) the switch is binary (fully on / fully off) which avoids partial-defensive allocation
during bull runs; (3) the offensive universe (including GDESIM) has higher expected CAGR.

---

## Citations

- `[stocks_on_the_move, ch.6]` — breadth momentum mechanics (Clenow; multi-asset breadth)
- `[ilmanen_expected_returns, ch.19]` — MF+gold free-lunch sleeve
- `[leverage_for_the_long_run, p.40-60]` — stacking justification
- `[advances_fin_ml, p.208-211]` — G1 PBO (N/A with single config)
- `[advances_fin_ml, p.222-223]` — G2 DSR significance n_trials=1
- `[advances_fin_ml, p.196-202]` — G6 block-bootstrap 99.9% CI
- `[advances_fin_ml, p.31-34]` — G7 cross-lib ±3pp CAGR parity
- VAA SSRN 3002624 (Keller & Keuning 2017) — primary mechanism

---

## Next directions (2-3)

1. **Iter 007 — User static portfolio + G3' adapted**: exact 9-sleeve portfolio from iter 003
   (RSSB/RSST/AVUV/AVDV/AVEM/SPMO/IDMO/GDE/KMLM) with corrected G3' gate. Validates
   whether iter 003 STRONG 84 was a gate calibration issue vs genuine underperformance.

2. **VAA-G3 SmartStack** (post-queue): replace the 4-asset offensive with 3 pure-equity
   stacks (NTSXSIM, NTSI, NTSE; no BNDSIM). B ∈ {0,1,2,3}. Hypothesis: equity-only breadth
   removes the bond contamination and may restore CAGR to HAA-competitive levels while
   retaining VAA's superior MDD control. Single pre-committed config.

3. **HAA gold sleeve variant** (post-queue): add 5% GLDSIM to HAA SmartStack sleeve
   (same as this iter but with HAA canary instead of VAA breadth). This directly tests
   whether the gold sleeve closes the 0.07 Sharpe gap to bestfolio target (1.18). If yes,
   iter 005 HAA architecture is the definitive answer.
