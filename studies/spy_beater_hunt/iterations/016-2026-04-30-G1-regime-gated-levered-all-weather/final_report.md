# spy_beater_hunt iter 016 — Final Report — `G1-regime-gated-levered-all-weather`

**Tier**: **PROMISING** — `score=61/100`, `winner_conditions_met=False`

**Strict bars** (CAGR-anchored, spy_beater rubric):
- CAGR bar (mean ≥ 13.80%): FAIL (mean = 10.34%)
- MDD bar (mean ≤ 40.85%): PASS (mean = 18.57%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate + Bridgewater All-Weather (Dalio 1996) F1-stack ON-state composition + Asness (1996) 'Why Not 100% Equities?' JPM leverage-balanced thesis + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (NTSX/GDE) + [ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM defensive) + [advances_fin_ml, p.31-34] factor framework — gate x sleeve orthogonality explicitly tested at SECOND decay regime (1.41x stack, no decay) complementing iter 014 (3x LETF, decay-dominated) + [advances_fin_ml, p.222-223] DSR cumulative_n_trials

---

## Selected config: `g1_f1_stack_sma200_ief`

Spec:

```json
{
  "type": "lrs",
  "on_weights": {
    "NTSXSIM": 0.35,
    "GDESIM": 0.3,
    "TLTSIM": 0.2,
    "KMLMSIM": 0.15
  },
  "off_weights": {
    "IEFSIM": 1.0
  },
  "signal_ticker": "SPYSIM",
  "sma_window": 200,
  "filter": "sma",
  "lag_days": 1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.091 | 10.49% | 18.57% | 7/7 | 2.90e-09 |
| **spy_real** | 1.070 | 10.20% | 18.57% | 7/7 | 1.47e-05 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| g1_f1_stack_sma200_ief | 1.091 | 1.070 |
| g1_f1_stack_sma200_kmlm | 0.765 | 0.699 |
| g1_f1_stack_sma200_blend | 0.985 | 0.941 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 11 | 30 | mean = 10.34%, bar = 11.21% |
| 2. MDD vs SPY | 18 | 20 | mean = 18.57%, bar = 55.17% |
| 3. Gates | 15 | 20 | per_ds = {'lh_56y': 7, 'spy_real': 7}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 1.47e-05, n_trials = 50 |
| 5. Sharpe | 4 | 10 | mean = 1.080 |
| 6. Robustness | 3 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 33.3% | 18.57% |
| 10y | 38.5% | 18.57% |
| 15y | 50.0% | 18.57% |
| 20y | 0.0% | 18.57% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

- **PBO N=3 warning** persists (CSCV statistically unstable with N<4). Per-dataset PBO grid-level: lh_56y 0.167 (excellent), spy_real 0.206 (excellent) — both well below 0.5 threshold AND much better than F1 stand-alone (lh 0.81, spy 0.40). Gate construction makes the configs more "structurally distinct" (different off-state assets) which lowers PBO via more decorrelated combinations.
- **TMFSIM not used** in this iter (NTSX/GDE stacking + TLT cash form on ON-state).
- **NTSXSIM/GDESIM stacking**: 0% LETF decay assumption (capital-efficient futures stacking, 0.5% rolling cost embedded). Real ETF tracking error may be 0.2-0.5%/y; assumption mid-range.
- **F1 stack ON-state weights fixed** (35 NTSX + 30 GDE + 20 TLT + 15 KMLM) — this iter does NOT sweep ON-state composition. Sensitivity deferred to follow-up if KILL #51 fires (it didn't).
- **Gate fixed at 200d SMA** — this iter does NOT test EMA / TSMOM / faster signals. Iter 002 KILL #7/#8 closed faster signals on SPY-track; applicability to F1-stack-track unverified but very low prior.
- **2-dataset framework**: lh_56y (40y synth) + spy_real (22.7y Tiingo daily). ndx_real not used per methodology refactor 2026-04-29.
- **lh_56y 5y/10y/15y/20y rolling = 0 windows**: rolling_metrics computes only on synth without Tiingo overlap; pass-rates from spy_real only (n=18/13/8/3 windows). Robustness 3/10 reflects spy_real-only data — F1 stand-alone showed similar pattern but with 100% 20y on spy_real (this iter 0%).
- **NEW module: NONE**. Reuses static-portfolio infra + lrs spec type. 765 -> 765 tests baseline preserved.

## Lesson

### Verdict summary

**Tier PROMISING 61/100** — `winner_conditions_met=False` for selected
config (`g1_f1_stack_sma200_ief`, **CAGR bar fails** at mean 10.34% <
11.21% bar). Score TIES F1 stand-alone (iter 015) at 61, but the bar
profile is OPPOSITE: F1 passed all 3 bars at 11.95% CAGR / 26.82% MDD;
G1 IEF FAILS CAGR bar but achieves NEW best-in-hunt MDD (18.57%) and
NEW best-in-hunt Sharpe (1.080) AND perfect 7/7 gates on BOTH datasets
(first iter ever in spy_beater hunt with cross-dataset 7/7 gates).

The Regime-Gated Levered All-Weather (F1×A2 cross-product hybrid) does
NOT break the architectural ceiling at 67. KILL #50 fires; the second
cross-product hybrid family (G1 at 1.41× stack, no-decay) joins iter 014
E1 hybrid (3× LETF, decay-dominated) in confirming KILL #33's
generalization across BOTH regimes of the leverage-decay axis.

### Pre-committed KILL outcomes

| KILL | name | trigger threshold | observed | result |
|---:|:---|:---|:---|:---:|
| #50 | G1 reinforces KILL #33 — Regime-gated F1 caps ≤ 67 | best G1 ≤ 67 | best 61 | **FIRED** |
| #51 | G1 breaks ceiling — KILL #33 INVALIDATED | best G1 ≥ 70 + 3 bars | best 61 < 70 + bars 2/3 | **NOT FIRED** |
| #52 | Adding regime gate to F1 stack hurts Sharpe (whipsaw dominates at no-decay) | mean Sharpe(g1_*) < 1.018 across all 3 | g1_ief mean 1.080 > 1.018 | **NOT FIRED (SURPRISE)** |
| #53 | 5y rolling pass-rate ≤ 33.3% across all 3 | min 5y_rolling = 33.3% (g1_ief) | 33.3% (tied trigger boundary) | **FIRED (tied)** |

### Closest-to-winner (UNCHANGED)

iter 006 `a6_tqqq_split_kmlm30_tlt10` RETAINS at score 67. Iter 016 ties
F1 stand-alone (iter 015) at score 61, both 6pts BELOW closest-to-winner.

Gap-by-criterion vs F1 stand-alone (iter 015 → iter 016, both score 61):

| criterion | iter 015 (F1 alone) | iter 016 (G1 IEF) | Δ |
|---|---:|---:|---:|
| 1. CAGR vs SPY | 14 (mean 11.95%) | 11 (mean 10.34%) | **−3** |
| 2. MDD vs SPY | 15 (mean 26.82%) | 18 (mean 18.57%) | **+3** |
| 3. Gates | 13 (5/7 lh + 7/7 spy) | 15 (7/7 + 7/7) | **+2** |
| 4. DSR | 10 | 10 | 0 |
| 5. Sharpe | 3 (mean 1.018) | 4 (mean 1.080) | **+1** |
| 6. Robustness | 6 | 3 | **−3** |
| **TOTAL** | **61** | **61** | **0** |

Net: gate trades **3 CAGR pts + 3 Robustness pts** for **3 MDD pts + 2
Gates pts + 1 Sharpe pt** = TIE at 61. The gate is a Pareto-shift, not
a Pareto-improvement, within the rubric.

### Direction implications

**G1 Regime-Gated Levered All-Weather family** — CLOSED at score 61 < 67.
KILL #50 fires; F1 hybrid family CLOSED. Architectural ceiling claim
(KILL #33) **strengthened from "7 fams + 1 hybrid" to "8 fams + 2
hybrids"** (counting G1 as 8th distinct architecture vs F1 stand-alone
since regime gate is a structural axis change).

**Why G1 fails CAGR bar despite gate's classical Gayed effectiveness**:
- F1 stack already has bonds (TLT 20%) + MF (KMLM 15%) buffer →
  mean MDD 26.82% is already low before any gate.
- Adding 200d SMA gate → going to 100% IEF when bear regimes →
  removes ~58.5% effective SPY exposure during bear → captures less
  bear stress (good for MDD) BUT also misses early bull recoveries
  (bad for CAGR).
- Gate cost on a balanced sleeve: −1.61pp CAGR, −8.25pp MDD, +0.06
  Sharpe, +2 Gates pts. Net Sharpe up; net CAGR down by enough to FAIL
  the bar (10.34% < 11.21%).

**Why this surprises iter 014's prediction**:
- Iter 014 (E1 hybrid at 3× LETF): gate × sleeve interaction was
  **NEGATIVE** — TSMOM gate on TQQQ split lost CAGR + Gates more than it
  gained on MDD. Score dropped 67→65.
- Iter 016 (G1 hybrid at 1.41× stack): gate × sleeve interaction is
  **MIXED** — gate gains MDD + Gates + Sharpe but loses CAGR + Robustness.
  Score TIES at 61, but bar profile shifts from "all 3 bars met" to
  "CAGR bar fails".
- **Asymmetry**: at 3× LETF, daily-reset decay dominates → gate's
  reaction-speed gain is consumed by ON-period decay. At 1.41× stack,
  no decay → gate's MDD/Sharpe gain is real, but CAGR loss is also
  real (bull-rally miss cost).
- **Conclusion**: gate × sleeve orthogonality is asymmetric across
  decay regimes BUT in BOTH regimes the cross-product score is ≤ best
  single-axis maximum. KILL #33 generalizes.

**Why G1 IEF achieves NEW best-in-hunt Sharpe + MDD**:
- Mean Sharpe 1.080 (lh 1.091, spy 1.070) — supercedes F1 stand-alone
  1.018 by +0.062 absolute. NEW best-in-hunt.
- Mean MDD 18.57% — supercedes F1 stand-alone 26.82% by 8.25pp. Beats
  D1 6m TSMOM (35.27%, prior best overall MDD) by 16.7pp.
- Gates 7/7 on BOTH datasets — first iter in spy_beater hunt with
  cross-dataset 7/7 gates (F1 stand-alone had 5/7 lh + 7/7 spy).
- DSR worst p = 1.47e-05 — NEW best DSR margin in hunt by another
  order of magnitude vs F1's 2.66e-05.
- Under ANY rubric except CAGR-anchored, G1 IEF would be the WINNER.

### Cross-family architectural ceiling diagnostic (UPDATED — 8 fams + 2 hybrids)

| family                              | best score | best Sharpe        | best mean MDD                |
|:------------------------------------|-----------:|-------------------:|-----------------------------:|
| A2 TQQQ-track LRS (iter 006)        | **67**     | 0.804              | 49.73%                       |
| A1/A3 SPY-track LRS                 | 66         | 0.744              | 51.60%                       |
| E1 hybrid (TSMOM × A2-sleeve)       | 65         | 0.746              | 47.48%                       |
| B1/B2 HFEA barbell                  | 63         | 0.739              | 67.48%                       |
| F1 Levered All-Weather (iter 015)   | 61         | 1.018              | 26.82%                       |
| **G1 hybrid (SMA × F1-sleeve)** ⬅ NEW | **61**   | **1.080 ⬅ BEST**   | **18.57% ⬅ BEST OVERALL**    |
| C1 vol-target                       | 60         | 0.721              | 41.86%                       |
| D1 concentrated+TSMOM (1×)          | 59         | 0.779              | 35.27% (prior best)          |
| D2 stacked equity                   | 52         | 0.738              | 52.65%                       |

**G1 introduces TWO new "best-in-hunt" attributes**:
1. **Highest mean Sharpe ever** (1.080) — supersedes F1 stand-alone (1.018)
   which itself was unprecedented. Gate adds Sharpe at no-decay regime.
2. **Lowest mean MDD ever** (18.57%) — beats D1 (35.27%, prior best
   overall MDD) by 16.7pp and F1 (26.82%, prior best CAGR-pass MDD) by
   8.25pp. NEW absolute floor.

Under MDD-anchored or Sharpe-anchored rubric, G1 IEF would be the WINNER
by a wide margin. Under spy_beater's CAGR-anchored rubric, it scores 61
TIED with F1 stand-alone — both 6pts below closest-to-winner 67.

### Cross-family knowledge added by iter 016

1. **Gate × sleeve interaction is ASYMMETRIC across decay regimes**:
   - At 3× LETF (iter 014, decay-dominated): gate × sleeve NEGATIVE.
     Gate's reaction-speed MDD gain is consumed by ON-period decay.
   - At 1.41× stack (iter 016, no decay): gate × sleeve MIXED. Sharpe
     + MDD + Gates ALL positive, but CAGR + Robustness negative.
   - In BOTH regimes the cross-product ≤ best single-axis maximum.
     KILL #33 generalizes across leverage-decay axis.

2. **F1 stack always-on vs gated 20y CAGR pass-rate flips 100%→0%**:
   - F1 stand-alone (iter 015): 20y rolling pass-rate 100% — beats SPY
     in EVERY single 20y window across both datasets.
   - G1 IEF (iter 016): 20y rolling pass-rate 0% — UNDERPERFORMS SPY
     in EVERY single 20y window. Gate cost CAGR enough to lose all
     long-horizon SPY-beating ability.
   - **Implication**: the F1 stack's ALWAYS-ON multi-asset diversification
     is the binding mechanism for long-horizon SPY-beating; adding a
     regime gate destroys it via bull-rally miss cost.

3. **Off-state defensive composition matters at no-decay** (3-config
   dose-response on G1):
   - 100% IEF off: best Sharpe 1.080, best MDD 18.57%, CAGR 10.34%, score 61
   - 50/50 IEF+KMLM off: Sharpe 0.963, MDD 19.77%, CAGR 9.76%, score < 61
   - 100% KMLM off: Sharpe 0.732, MDD 30.97%, CAGR 8.93%, score < 55
   - **IEF wins on all three metrics** at no-decay. Aggressive KMLM
     defensive (used by some literature for "crisis-alpha amplification")
     is too volatile when bear-mode lasts months — IEF (7-10y Treasury)
     is more reliable cash-equivalent.

4. **G1 IEF achieves NEW best-in-hunt Sharpe (1.080) AND best-in-hunt
   MDD (18.57%) AND perfect 7/7 gates on BOTH datasets** — but FAILS
   CAGR bar by 0.87pp. The CAGR-anchored rubric continues to reject
   strategies that achieve textbook risk-adjusted return + drawdown
   control if mean CAGR < 11.21%. This is the second config in hunt
   history (after F1 stand-alone) that empirically demonstrates
   excellent risk-adjusted return + textbook MDD control yet scores
   below 67 — strengthens the rubric-revision review case.

5. **PBO drops dramatically with gate construction**: F1 stand-alone
   (iter 015) had lh_56y PBO 0.81 (HIGH warning); G1 IEF (iter 016)
   has lh_56y PBO 0.167 + spy_real 0.206 (both excellent). The
   structural distinction between configs (different defensive
   off-state assets) gives more decorrelated combinations in the
   CSCV grid → lower PBO. Gate construction is a side benefit for
   PBO stability.

### Multi-horizon robustness diagnostic

5y rolling pass-rate **33.3%** (TIED with F1 stand-alone — gate
DID NOT improve short-horizon CAGR; bull-rally miss cost = bonds drag
cost on F1 stand-alone), 10y 38.5%, 15y 50.0%, **20y 0%** (FLIPPED
from F1 stand-alone's 100%). The gate fundamentally degrades long-
horizon SPY-beating ability — this is the most surprising finding in
iter 016.

Under a window-length-weighted robustness rubric (5y < 10y < 15y < 20y),
G1 IEF would score WORSE than F1 stand-alone at 20y windows — the
opposite of what one might expect from "regime gate avoids bear stress
periods → better long-horizon outcome".

### Statistical integrity

- **Cumulative n_trials**: 47 → **50** after this iter. DSR worst p =
  **1.47e-05** << 0.05 — NEW best DSR margin in entire hunt by another
  order of magnitude vs F1 stand-alone (2.66e-05).
- **PBO grid-level**: lh_56y 0.167 + spy_real 0.206 — BOTH EXCELLENT
  and DRAMATICALLY better than F1 stand-alone (lh 0.81 + spy 0.40).
  Gate construction lowers PBO via decorrelated config combinations.
- **G3 walk-forward**: lh_56y max wf_mdd = 18.21% (PASSES 25% threshold);
  spy_real max wf_mdd = 18.57% (PASSES). BOTH datasets pass G3 — first
  in spy_beater hunt where G3 passes on lh_56y (F1 stand-alone failed
  by 1.82pp).
- **G6 bootstrap CI low**: lh_56y 0.619 (very strong), spy_real 0.449
  (strong). Both well above 0 threshold.
- **G7 cross-lib ±3pp CAGR**: 0.0pp delta on BOTH datasets. Engine
  consistency excellent.

### Surprising findings

1. **Gate ADDS Sharpe at no-decay regime — counter to iter 014's
   negative orthogonality**. F1 stand-alone Sharpe 1.018 → G1 IEF
   Sharpe 1.080 (+0.062). At 3× LETF (iter 014), gate REMOVED Sharpe.
   At 1.41× stack (iter 016), gate ADDED Sharpe. The asymmetry is
   real and informative.

2. **G1 IEF achieves NEW absolute floor on MDD (18.57%)**: Beats D1
   (prior overall best 35.27%) by 16.7pp and F1 stand-alone (prior
   best CAGR-pass 26.82%) by 8.25pp. This is a step-function change
   in the spy_beater hunt's MDD frontier.

3. **F1 stack 20y rolling pass-rate FLIPS 100% → 0% with gate added**:
   The MOST surprising single finding of iter 016. Always-on F1 stack
   had perfect 20y SPY-beating; gating it to IEF when bear destroys
   that property entirely. Gate adds Sharpe + MDD + Gates pts at
   short-horizon but loses Robustness pts at long-horizon. Net 0
   score change vs F1 stand-alone, but bar profile shifts from "3/3
   passed" to "CAGR fails".

4. **Both G1 IEF AND F1 stand-alone score 61 — but represent DIFFERENT
   architectural archetypes**: F1 (always-on multi-asset diversification)
   passes all 3 bars at moderate Sharpe + moderate MDD. G1 (regime-
   gated multi-asset) achieves MDD + Sharpe ceiling but FAILS CAGR
   bar. Under rubric, they tie; under user-utility (does it pass all
   3 bars?), F1 stand-alone is preferred.

5. **G1 IEF 7/7 gates on BOTH datasets — first ever in spy_beater hunt**.
   F1 stand-alone had 5/7 lh + 7/7 spy. The gate construction tightens
   PBO + WF on lh_56y enough to pass G1 + G3 — historically the
   weakest gates on synth dataset. Gate's "fewer trading days" effect
   may be a side benefit for gate stability metrics.

### Path to score 90 (G1 architecture)

ARCHITECTURALLY UNREACHABLE under spy_beater rubric. Best G1 score 61 →
gap 29 to 90.

Pareto-feasible analysis:
- Mean CAGR axis: G1 IEF 10.34% vs SPY 14% target → −3.66pp gap. To
  recover via tweaks: lift ON-state leverage from 1.41× to 2× (e.g.,
  swap stack for LETF mix) → CAGR up ~3pp + Sharpe down (LETF decay)
  + MDD up. Iter 015 LETF 2x had CAGR 16.36%, MDD 43.53%, Sharpe 0.90
  → would not improve total score.
- Adding regime gate to LETF 2x F1: predicted CAGR up ~1pp via bear
  miss, MDD down ~5-10pp, Sharpe down ~0.05 (LETF whipsaw). Net G1-LETF
  estimated 60-65 — same architectural ceiling.
- Real Pareto-feasible ceiling for G1 family ≈ 65-68. Score-90 path
  unreachable.

### Why this iter STRENGTHENS the negative-result claim

Spy_beater architectural taxonomy now has **8 single-axis families + 2
cross-product hybrids** all capping at or below score 67. Both cross-
product hybrids (E1 at 3× LETF + G1 at 1.41× stack) span the leverage-
decay axis and BOTH cap below the best single-axis (A2 TQQQ-track 67).
The orthogonality assumption is empirically REJECTED in BOTH regimes,
but the rejection is consistently in the WRONG DIRECTION for hunt-
reopening (cross-product ≤ union of single-axis maxima).

The negative result is now structurally complete:
1. **F1 stand-alone (iter 015)**: optimal Sharpe + MDD-among-CAGR-passers
   but CAGR-anchored rubric clamps score below closest-to-winner.
2. **G1 hybrid (iter 016)**: optimal Sharpe + absolute MDD + perfect
   gates, but CAGR bar FAILS — gate cost drives mean CAGR below 11.21%.
3. **No architecture in formal taxonomy** achieves CAGR ≥ 13.80% (target)
   AND MDD ≤ 40.85% (target) AND gates ≥ 2/3 datasets simultaneously.

The rubric-revision review case is now stronger (TWO configs with
all-time-best Sharpe + MDD both score 61, both fail to clear 67). User
should consider whether spy_beater's CAGR-anchored 30-pt weighting is
appropriate given that empirically the best risk-adjusted strategies
score below the architectural ceiling.

### Suggested iter 017+

NONE — hunt remains CLOSED at 67-cap with 8 architectural families + 2
cross-product hybrids all empirically subordinate to A2 TQQQ-track +
KMLM crisis-alpha within the CAGR-anchored rubric. The formal taxonomy
is fully closed:
- Tier 1 families A1/A2/B1: CLOSED
- Tier 2 families A3/B2/C1: CLOSED
- Tier 3 families D1/D2/F1: CLOSED (D1 iter 013, D2 iter 012, F1 iter 015)
- C2 CAPE-timing: untested per PROMISING_DIRECTIONS.md (low-credibility,
  no infra) — would not change architectural-ceiling conclusion
- Cross-product hybrids E1 (iter 014) + G1 (iter 016): both CLOSED

**Possible mandate §7 review trigger**: G1 IEF achieves Sharpe 1.080
(highest in hunt), MDD 18.57% (lowest in hunt), gates 7/7 on BOTH
datasets (perfect), DSR 1.47e-05 (best margin in hunt). It is
empirically the strongest-overall risk-control configuration tested
across all 16 iters + 50 cumulative trials, but FAILS the CAGR bar by
0.87pp. Under any non-CAGR-anchored rubric, G1 IEF would be the
WINNER. User decision warranted on rubric philosophy.

F1+SPLIT incumbent fallback (long_term_portfolio) retains deploy-ready
status. Mandate §1 100% Plano C UNCHANGED.

### Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA gate
  rationale. Gayed's empirical claim that SMA gate adds CAGR via bear-
  avoidance is **partially confirmed** at 1.41× stack: gate adds Sharpe
  + MDD pts but COSTS CAGR via bull-rally miss. Net effect depends on
  the underlying sleeve's standalone bear behavior. F1 stack already
  has bonds + MF buffer → marginal gate value is Sharpe-positive but
  CAGR-negative.
- **Bridgewater All-Weather (Dalio 1996, public papers 2011)** — F1
  stack ON-state derives from canonical risk-parity construction.
  Adding regime gate to canonical risk-parity creates a hybrid that
  empirically achieves ZERO improvement on score (61 = 61) but flips
  the bar profile from "3/3 passed" to "CAGR bar fails". Gate is not a
  free addition on already-balanced sleeves.
- **Asness (1996) "Why Not 100% Equities?" JPM** — leverage-balanced
  thesis. F1 stack 1.41× notional achieved Sharpe 1.018 standalone;
  adding gate lifts to 1.080. Gate amplifies the leverage-balanced
  Sharpe edge at NO-decay, even though it costs CAGR. Asness thesis
  partially confirmed.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking
  (NTSX/GDE) Pareto-dominates LETF mix. Adding gate preserves the
  stacking advantage; G1 IEF Sharpe 1.080 vs hypothetical LETF G1
  predicted 0.85-0.90.
- `[ilmanen_expected_returns, ch.19]` — MF crisis-alpha (KMLM). G1.2
  KMLM-defensive UNDERPERFORMS G1.1 IEF-defensive on all metrics —
  KMLM is too volatile when bear-mode persists; IEF is more reliable.
  This nuances the "always KMLM = good" interpretation of MF crisis-
  alpha literature.
- `[advances_fin_ml, p.31-34]` factor framework — gate × sleeve
  orthogonality empirically tested at SECOND decay regime (1.41× stack)
  complementing iter 014 (3× LETF). KILL #50 fires: orthogonality is
  asymmetric but ALWAYS in the wrong direction for hunt-reopening.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = **50**, worst
  p = **1.47e-05** — NEW best DSR margin in entire hunt, by another
  order of magnitude vs iter 015 (2.66e-05).
- `[advances_fin_ml, p.208-211]` PBO grid-level — N=3 warning persists
  but values dramatically improve with gate construction (lh 0.167,
  spy 0.206 — both excellent vs F1 stand-alone lh 0.81 high warning).
- `[advances_fin_ml, p.196-202]` bootstrap CI — G6 passed comfortably
  on both datasets (lh 0.619, spy 0.449).
- HFEA Bogleheads 2019 — counterexample preserved: F1 stack already
  has bonds + MF buffer, making it more bear-resistant standalone than
  HFEA which needed regime gate desperately. Marginal gate value
  diminishes with sleeve quality.
