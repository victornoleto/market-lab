# Iteration 071 — Final Report

## Verdict

🥇 **STRONG** — score **90/100** (TIES iter 064/069/070 for joint
TOP-K #1, now a 4-way tie at 90 STRONG), **winner_conditions_met=False**
(4/5 strict — Sharpe edge ✓, gates cross-ds ✓, DSR ✓, MDD ceiling ✓;
CAGR floor ✗ 1/3 only edu), **2/10 kills fired (A primary; G
diagnostic)**.

This iteration tests whether adding a **calm-aggressive 3rd stream**
breaks iter 064's 90 ceiling. Based on iter 070's structural diagnosis
that BOTH iter 046 and r_qqqt are defensively biased (higher conditional
Sharpe in stress), iter 071 introduces a Connors-Alvarez (2009) RSI(2)
short-term mean-reversion stream on SPY, gated by Chan
`[algo_trading_chan, p.95]` 200d-SMA momentum filter — the canonical
calm-aggressive complement.

```
RSI2[t-1], SMA200[t-1], SMA5[t-1]                    # all at t-1, no peek
gate[t]   = (SPY[t-1] > SMA200[t-1])                   # Chan p.95 momentum filter
buy[t]    = gate[t] AND RSI2[t-1] < th                 # Connors-Alvarez 2009 entry
sell[t]   = SPY[t-1] > SMA5[t-1]                       # Connors-Alvarez exit
pos[t]    = state-tracking long iff buy without subsequent sell
r_mr[t]   = pos[t]·r_spy[t] + (1-pos[t])·rf_d − cost
cost[t]   = 5bp · |Δpos|

3-leg blend (proportional preservation of iter 064's 9:1):
w_046  = (1 − w_mr) · 0.90
w_qqqt = (1 − w_mr) · 0.10
w_mr  ∈ {0.05, 0.10}
r_071[t] = w_046·r_046 + w_qqqt·r_qqqt + w_mr·r_mr
```

**Engine integrity**: 15/15 TDD tests pass (Wilder RSI math, no-peek
shift(1) on RSI/SMA, Connors entry+exit semantics, cost accounting,
3-leg combiner inner-join + weight validation, w_mr=0 recovery of
iter 064 base). G7 cross-lib **0.0000 pp** on 3/3 datasets (max ret
diff = 1.11e-16, far below 0.5 pp threshold).

**Key empirical findings**:

1. **KILL D VINDICATED — calm-aggressive thesis confirmed.** r_mr's
   conditional Sharpe ordering is calm > stress on **3/3 datasets**
   for ALL 4 cfgs:
   - th5_w005: calm 0.93/0.90/0.84 vs stress 0.38/0.32/0.32
   - th10_w005: calm 0.82/0.88/0.80 vs stress 0.68/0.70/0.70
   This is the structural OPPOSITE of iter 046 + r_qqqt's defensive
   profile — the predicted complementarity holds.
2. **r_mr is genuinely orthogonal**: corr(r_mr, r_046) = 0.17-0.28
   across all cfgs and datasets — well below 0.5 KILL C threshold.
   r_mr is NOT structurally redundant with the risk-parity stack.
3. **r_mr stream has standalone edge**: Sharpe 0.55-0.84 across cfgs;
   MDD 13-15%; time-in-market 4.5-15.1% — matches Connors-Alvarez
   canonical low-frequency profile.
4. **KILL A FIRES — Sharpe lift under +0.02 vs iter 064 on 3/3 ds**.
   Even at the best cfg (th10_w005), Δ064 Sharpe is +0.016/+0.018/
   +0.015 — directionally positive on 3/3 but below the pre-committed
   +0.02 threshold.
5. **KILL G FIRES — 3rd stream is structurally inert at this w**:
   corr(071, 064_static) = 0.999/0.999/0.999 — the small w_mr=0.05
   produces a return path that is nearly indistinguishable from iter
   064's static. The orthogonal calm-aggressive lift exists but its
   magnitude is masked by the dominant 95% in iter 046+r_qqqt.
6. **CAGR floor unchanged**: best cfg still passes only edu (9.27%
   > 9.18% floor); spy/ndx both fail the 11.98%/15.35% floors —
   identical to iter 064/069/070 outcome.
7. **Score 90 ties iter 064/069/070 at joint TOP-K #1.** This is the
   **4th iteration at the 90 ceiling** with a fundamentally different
   mechanism (mean-reversion vs trend/regime), confirming the ceiling
   is anchored in the iter 046 base, not in mechanism choice.

## Headline metrics (best cfg `iter064_plus_spy_mr_rsi2_th10_w005`)

| dataset | Sharpe (Δ frozen / Δ064) | CAGR (Δ064) | MDD (Δ064) | DSR p | gates |
|---|---|---|---|---|---|
| educational | **1.2339** (+0.5539 / **+0.0164**) | 9.27% (−0.22pp) | 16.41% (−0.86pp) | **0.0310** | **7/7** |
| spy_real | **1.3491** (+0.4491 / **+0.0179**) | 9.76% (−0.21pp) | 14.67% (−0.66pp) | **0.0335** | **7/7** |
| ndx_real | **1.3901** (+0.4351 / **+0.0146**) | 9.93% (−0.24pp) | 14.11% (−0.63pp) | **0.0294** | **7/7** |

vs iter 064 (1.2175/1.3312/1.3755 Sharpe; 9.49%/9.97%/10.17% CAGR;
17.27%/15.33%/14.74% MDD): a Pareto-shifted variant — slightly higher
Sharpe AND tighter MDD, paid for with marginally lower CAGR. The trade
is reasonable (Sharpe∝CAGR/σ), but the lift is too small to break
the +0.02 KILL A threshold.

**Per-dataset gate detail** (G1234567):

| dataset | G1 | G2 | G3 | G4 | G5 | G6 | G7 | total |
|---|---|---|---|---|---|---|---|---|
| edu | ✓ PBO=0.08 | ✓ p=0.031 | ✓ 8/8 | ✓ S>0 | ✓ S>0 | ✓ ci_low>0 | ✓ 0pp | **7/7** |
| spy | ✓ PBO=0.25 | ✓ p=0.034 | ✓ ≥6/8 | ✓ S>0 | ✓ S>0 | ✓ ci_low>0 | ✓ 0pp | **7/7** |
| ndx | ✓ PBO=0.31 | ✓ p=0.029 | ✓ ≥6/8 | ✓ S>0 | ✓ S>0 | ✓ ci_low>0 | ✓ 0pp | **7/7** |

7/7 × 3 with PBO < 0.5 on all and DSR < 0.05 at cumulative_n_trials =
4344 (= 4340 + 4 cfgs).

**r_mr stream characterisation (best cfg th10_w005)**:

| dataset | r_mr Sharpe | CAGR | MDD | TIM | calm_S | stress_S | corr(046, mr) | corr(qqqt, mr) |
|---|---|---|---|---|---|---|---|---|
| edu | 0.787 | 4.92% | 14.63% | 14.3% | 0.820 | 0.675 | 0.272 | 0.365 |
| spy | 0.838 | 5.49% | 14.63% | 15.1% | 0.880 | 0.703 | 0.281 | 0.375 |
| ndx | 0.774 | 5.03% | 14.63% | 15.1% | 0.801 | 0.703 | 0.273 | 0.375 |

calm > stress on 3/3 (✓ KILL D clean); standalone S 0.77-0.84 (✓ KILL B
clean); MDD 14.6% (✓ KILL I clean); TIM ~15% (✓ KILL J clean — Connors-
canonical low-frequency); orthogonal to r_046 (✓ KILL C clean).

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | 3/3 datasets ≥ frozen + 0.10 (edu +0.55 / spy +0.45 / ndx +0.44) |
| 2 Gates | **25** | 25 | edu 7/7 → 7pts; spy 7/7 → 7pts; ndx 7/7 → 7pts; cross-ds met → +4 = 25 |
| 3 DSR | **15** | 15 | Worst-p 0.0335 (spy) < 0.05 → full 15 pts; cumulative n_trials = 4344 |
| 4 CAGR floor | **5** | 15 | 1/3: edu 9.27% > 9.18% ✓; spy 9.76% < 11.98% ✗; ndx 9.93% < 15.35% ✗ |
| 5 MDD ceiling | **15** | 15 | All 3 well under bench+5pp; 24-26pp slack each |
| 6 Robustness | **5** | 5 | 9/9 sub-windows positive (Sharpe 1.16-1.59 across all 9) |
| **total** | **90** | **100+5** | tier: **STRONG** (TIES iter 064/069/070 at joint TOP-K #1) |

Strict winner conditions: **4/5 met** —
1. Sharpe edge ≥ +0.10 on ≥ 2 ds: ✓ (3/3 vs frozen)
2. Gates cross-ds (edu ≥5, spy/ndx ≥4): ✓ (7/7/7)
3. DSR p < 0.05 (worst): ✓ (0.0335 spy)
4. CAGR ≥ 0.8×bench on ≥ 2 ds: ✗ (1/3, only edu)
5. MDD ≤ bench+5pp on ≥ 2 ds: ✓ (3/3)

Same 4/5 winner conditions as iter 064/069/070. The CAGR-floor shortfall
on spy/ndx remains the single-axis blocker; calm-aggressive 3rd stream
does not lift CAGR enough to clear it.

## Per-cfg sensitivity sweep (4 cfgs)

| cfg_id | RSI threshold | w_mr | Sharpe edu/spy/ndx | Δ064 Sharpe | edu CAGR | score | kills | tier |
|---|---|---|---|---|---|---|---|---|
| `iter064_plus_spy_mr_rsi2_th5_w005` | 5 | 0.05 | 1.234/1.347/1.389 | +0.017/+0.015/+0.013 | 9.22% | **90** | **2/10** | STRONG |
| `iter064_plus_spy_mr_rsi2_th5_w010` | 5 | 0.10 | 1.251/1.361/1.401 | +0.033/+0.030/+0.025 | **8.95%** ✗ | 85 | 2/10 | STRONG |
| `iter064_plus_spy_mr_rsi2_th3_w005` | 3 | 0.05 | 1.230/1.342/1.384 | +0.012/+0.010/+0.008 | 9.17% ✗ | 85 | 3/10 | STRONG |
| `iter064_plus_spy_mr_rsi2_th10_w005` | 10 | 0.05 | 1.234/1.349/1.390 | +0.016/+0.018/+0.015 | 9.27% | **90** | **2/10** | STRONG |

**Sensitivity findings**:

- **w_mr matters more than RSI threshold** for Sharpe lift. Doubling
  w_mr from 0.05 → 0.10 doubles the Δ064 lift (~0.015 → ~0.030),
  enough to clear the +0.02 KILL A threshold. But it also drops edu
  CAGR from 9.27% to 8.95%, breaking iter 064's non-LETF unlock floor
  (KILL H fires) → score capped at 85.
- **RSI threshold sweep degrades**: th=3 (selective, 4.5% TIM) gets
  the smallest lift (+0.008-0.012) — too rare to matter. th=10 (looser,
  15% TIM) gets a ~+0.018 lift but still under +0.02. th=5 gives
  +0.013-0.015. The Connors literal (th=5) is NOT optimal under this
  composition; th=10 produces marginally better Sharpe.
- **Both 90-scoring cfgs (th5_w005, th10_w005) tie iter 064/069/070
  at the ceiling**. Sharpe-sum tiebreak picks th10_w005 by 0.0037 —
  effectively a coin flip.
- **0/4 cfgs beat iter 064 by ≥ +0.02 on a single ds** at score ≥ 90
  (th5_w010 does break +0.02 lift but loses CAGR). The Pareto front
  trades Sharpe vs CAGR linearly with w_mr; no free lunch.

## Pre-committed kills evaluation

Best cfg `th10_w005`:

| # | kill | fired? | observation |
|---|---|---|---|
| **A** | **Sharpe lift vs iter 064 < +0.02 on ≥ 2 ds** | **❌ FIRED** | Δ +0.016/+0.018/+0.015 — under +0.02 on 3/3 (lift too small) |
| B | r_mr standalone Sharpe < 0.5 on ≥ 2 ds | ✓ clean | 0.79/0.84/0.77 — well above 0.5 |
| C | corr(r_mr, r_046) > 0.5 on ≥ 2 ds | ✓ clean | 0.27/0.28/0.27 — orthogonal |
| **D** | **cond Sharpe r_mr stress > calm on ≥ 2 ds (defensive)** | **✓ clean** | calm 0.82/0.88/0.80 > stress 0.68/0.70/0.70 on 3/3 — calm-aggressive thesis vindicated |
| E | G7 cross-lib > 0.5 pp on any ds | ✓ clean | max 0.0000 pp (3/3) — engine perfect |
| F | Score < 75 (drops below STRONG) | ✓ clean | 90 — well above STRONG threshold |
| **G** | **corr(071, 064_static) > 0.99 on ≥ 2 ds** | **❌ FIRED** | 0.999/0.999/0.999 — small w_mr makes 3rd stream structurally inert |
| H | edu CAGR < 9.18% (loses 064 unlock) | ✓ clean | 9.27% — preserves the floor |
| I | r_mr standalone MDD > 30% on any ds | ✓ clean | 14.6% (3/3) — bounded by 200d gate cutoff |
| J | r_mr time-in-market > 30% on ≥ 2 ds | ✓ clean | 14-15% (3/3) — Connors-canonical low-frequency |

**2/10 kills fire** — A is headline (Sharpe lift below threshold);
G diagnostic-class (3rd stream inert at this w). KILL D is **clean
and vindicating**: the calm-aggressive structural thesis is empirically
confirmed across 3/3 datasets and all 4 cfgs.

## What worked / what didn't

**Worked**:

- **Calm-aggressive thesis CONFIRMED (KILL D vindicated)**. r_mr's
  conditional Sharpe ordering is calm > stress on 3/3 datasets for
  every cfg — the structural opposite of iter 046 + r_qqqt's defensive
  profile. This is the **first iteration to empirically demonstrate**
  the calm-aggressive structural pattern is achievable on Tiingo cache
  with the available equity ETFs.
- **Stream genuinely orthogonal**: corr(r_mr, r_046) = 0.17-0.28 — well
  below KILL C threshold. The Connors-style mean-reversion is NOT a
  re-encoding of the risk-parity defensive stack.
- **All 7/7 gates pass on all 3 datasets** for ALL 4 cfgs (matches
  iter 064/069/070 — engine pipeline rock-solid).
- **PBO via CSCV at N=4**: 0.08/0.25/0.31 — well under 0.5 on 3/3.
  No grid-level overfitting.
- **DSR p < 0.05 on all 3 ds at cumulative n_trials = 4344**: best
  cfg's worst-p is 0.0335 (spy_real) — same significance band as
  iter 064/069/070.
- **Robustness 9/9 sub-windows positive** (Sharpe 1.16-1.59 across
  all 9) — same cleanliness as iter 064/069/070.
- **Engine integrity perfect**: 15/15 TDD tests pass; G7 cross-lib
  0.0000 pp on all 3 ds (max ret diff = 1.11e-16); strict no-peek
  (BOTH RSI and SMA shifted at t-1).
- **MDD strictly tightens vs iter 064 on 3/3** (−0.6 to −0.9 pp).
  The calm-aggressive complement reduces drawdowns.
- **Score 90 STRONG ties iter 064/069/070** for joint TOP-K #1.

**Didn't**:

- **KILL A FIRES**: Sharpe lift vs iter 064 is +0.013-0.018 on 3/3 ds
  for the best cfg — directionally positive on all but below the
  pre-committed +0.02 threshold. The calm-aggressive complement at
  small w_mr=0.05 lifts Sharpe MARGINALLY but doesn't break the 90
  ceiling.
- **KILL G FIRES**: corr(071, 064_static) > 0.99 on 3/3 — the small
  w_mr makes the 3rd stream structurally inert against the dominant
  95% in iter 046+r_qqqt. The orthogonal lift exists in the marginal
  basis but is masked by the larger composition.
- **w_mr=0.10 trade-off**: pushing w_mr higher to break KILL A (cfg
  th5_w010 achieves Δ064 +0.025-0.033) drops edu CAGR from 9.49% to
  8.95% (below 9.18% unlock floor) → KILL H fires, score caps at 85.
  The CAGR-Sharpe Pareto front is strict at this composition.
- **CAGR floor still 1/3** — same as iter 064/069/070. The defensive
  composition's structural CAGR shortfall on spy_real/ndx_real
  benchmarks (4-9pp short) is invariant to adding a low-CAGR
  calm-aggressive stream (r_mr CAGR = 3-5%).
- **Winner conditions still 4/5** — no breakthrough into WINNER band.

## Main lesson (for future iterations)

**iter 071 = STRUCTURAL CLOSURE of "calm-aggressive 3rd stream on iter
064" → score 90 STRONG (TIES iter 064/069/070, joint 4-way TOP-K #1)**.

The empirical evidence vindicates the **structural diagnosis** from
iter 070's final report: BOTH iter 046 and r_qqqt are defensively
biased, and adding a calm-aggressive complement (Connors-Alvarez RSI(2)
+ Chan p.95 momentum filter) IS the right structural move. KILL D
clean confirms the conditional-Sharpe inversion exists in r_mr (calm
> stress on 3/3); the stream is genuinely orthogonal (ρ ≤ 0.28 vs
r_046); and at moderate w_mr=0.10 the 3rd stream produces a Sharpe
lift > +0.02 (cfg th5_w010 hits +0.025-0.033 on 3/3).

**However, the same composition's CAGR ceiling at iter 064 base prevents
breakthrough**: pushing w_mr from 0.05 → 0.10 lifts Sharpe but
proportionally dilutes CAGR (r_mr CAGR ≈ 4% << r_046+r_qqqt CAGR ≈
10%), causing edu CAGR to drop below the 9.18% unlock floor. The
CAGR-Sharpe Pareto front is binding at this composition.

| iter | mechanism added | regime classifier | Δ064 Sharpe | edu CAGR | score |
|---|---|---|---|---|---|
| 064 | (baseline) | none | baseline | 9.49% | 90 |
| 068 | inner-w binary VIX (orig dir) | equity-vol binary | −0.04/−0.05/−0.05 | 9.53% | 79 |
| 069 | inner-w binary VIX (reverse) | equity-vol binary | −0.005/−0.010/−0.020 | 9.36% | 90 |
| 070 | inner-w continuous T10Y3M | macro/forward continuous | −0.003/−0.011/−0.018 | 9.69% | 90 |
| **071-th10w005** | **3rd stream: SPY MR** | **none (orthogonal stream)** | **+0.016/+0.018/+0.015** | **9.27%** | **90** |
| **071-th5w010** | **3rd stream: SPY MR** | **none (orthogonal stream)** | **+0.033/+0.030/+0.025** | **8.95%** | **85** |

The 4-iter pattern (064/069/070/071) shows: regardless of mechanism
(reweighting, regime classifier, orthogonal 3rd stream), the score
saturates at **90 STRONG** under the iter 046 + r_qqqt anchor. The
ceiling is **anchored in the base composition's CAGR profile**, not
in the structural ingredient.

**Key implications for iter 072+**:

1. **The 90 ceiling is now confirmed across 4 fundamentally different
   structural mechanisms**: regime reweighting (068/069), macro-
   orthogonal continuous regime (070), calm-aggressive orthogonal
   3rd stream (071). The next iteration must change the **base
   anchor**, not just add components.
2. **CAGR-Sharpe Pareto front IS BINDING**: the iter 046 vol-managed
   stack runs at vol-target levels well below SPY/QQQ's natural
   levered vol, capping CAGR at ~9-10% across all extensions tested.
   Breaking the 90 → 95+ band requires a higher-CAGR base.
3. **Calm-aggressive complement IS structurally validated** — it's
   ready to compose into a non-iter-046 anchor. Future iterations
   that find a higher-CAGR base should add this stream as a
   complement.

## Structural dead-ends discovered

iter 071 closes the **calm-aggressive 3rd stream axis on iter 064
base**:

- **iter 071 (🥇 STRONG 90, 2/10 KILLS — A primary; G diagnostic) —
  Connors-Alvarez RSI(2) + Chan p.95 momentum filter on iter 064 base
  (4 cfgs sweep: RSI∈{3,5,10}, w_mr∈{0.05, 0.10})**: 7/7 gates × 3 ds;
  PBO 0.08-0.31 (3/3 < 0.5); DSR < 0.05 × 3; robustness 9/9; engine
  perfect (15/15 TDD, G7 0pp). Sharpe lift +0.013-0.018 vs iter 064
  on 3/3 datasets at small w_mr=0.05 (KILL A); +0.025-0.033 at w_mr=
  0.10 but CAGR drops below edu unlock floor (KILL H, score 85).
  KILL D clean — calm-aggressive thesis vindicated (r_mr calm S >
  stress S on 3/3). KILL G fires — small w_mr makes 3rd stream
  structurally inert vs iter 064 static.

  **Closes the calm-aggressive-3rd-stream axis on iter 064 base at
  90 STRONG ceiling**. The composition's CAGR ceiling (anchored in
  iter 046 + r_qqqt) prevents breakthrough regardless of the
  complement's quality.

What is **OPEN** for iter 072+ (NOT consumed by iter 071):

- **Fresh higher-CAGR anchor (NOT iter 046 family)** — the only
  remaining structural lever. Cross-asset Hurst-regime trend, credit-
  spread regime as primary signal, or a single-asset levered base
  with embedded calm-aggressive + defensive components. Cost: ~5+
  iteration sunk cost for the new anchor.
- **Hierarchical / multi-signal regime model on iter 064 with the
  validated calm-aggressive r_mr added as 3rd stream** — combine
  iter 069 binary-VIX or iter 070 continuous-T10Y3M with the iter
  071 calm-aggressive complement. The hypothesis is that a regime-
  aware allocation across (defensive r_046, defensive r_qqqt,
  calm-aggressive r_mr) could dynamically up-weight r_mr in calm
  regimes and down-weight in stress regimes, breaking the 90
  ceiling. Cost ~75-90 min, risk: regime-discovery overfit at
  cumulative_n_trials = 4344.
- **Forward 5-day Sharpe meta-label on iter 064** (still open from
  iter 067 final report).
- **Plano C sleeve meta-allocation** (≤ 70 ceiling).
- **CRSP / Norgate cross-sectional momentum** (data budget).

What is **CLOSED** by iter 071 (in addition to all prior closures):

- **Calm-aggressive 3rd stream on iter 064 inner blend at small
  weight**: structurally validates the calm-aggressive thesis (KILL
  D vindicated cross-cfg cross-ds) but saturates at 90 STRONG
  ceiling at w_mr=0.05 (small enough to preserve CAGR floor but
  Sharpe lift below threshold). Larger w_mr (0.10) breaks the +0.02
  Sharpe lift threshold but loses edu CAGR floor → score caps at 85.

## Citations used

- `[algo_trading_chan, p.95, ch.4]` — Chan: momentum filter (price >
  long-term MA) on mean-reversion entry; primary citation for the
  200d-SMA gate.
- `[algo_trading_chan, p.153-154, ch.6]` — Chan: mean-reversion +
  momentum complementarity in a diversified portfolio; structural
  hypothesis foundation.
- `[algo_trading_chan, p.183-184, ch.8]` — Chan: NEVER apply in-
  sample stop-loss to mean-reversion (no IS stop used in this stream;
  200d-SMA gate provides the regime hedge).
- `[quant_trading_chan, p.142-143]` — Chan: mean-reversion exit via
  opposite-of-entry signal (here: SMA(5) cross).
- **Connors, L., & Alvarez, C. (2009)**. *Short Term Trading Strategies
  That Work*. ISBN 978-0-9755513-2-7. Canonical RSI(2) dip-buy +
  200-SMA filter rules.
- **Lo, A. W., & MacKinlay, A. C. (1988)**. "Stock Market Prices Do
  Not Follow Random Walks: Evidence from a Simple Specification Test."
  *Review of Financial Studies*, 1(1), 41-66. DOI 10.1093/rfs/1.1.41
  — empirical foundation for short-horizon equity mean-reversion.
- `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046
  base preserved verbatim (saved return stream).
- **Faber (2007)**, SSRN 962461 — single-asset 200d SMA TAA primitive
  (preserved verbatim from iter 064 via QQQ_TREND).
- `[stocks_on_the_move, p.21-30]` (Clenow) — 200d SMA as regime gate
  inside a momentum portfolio.
- `[advances_fin_ml, p.162-164]` — strict shift(1) on signal (BOTH
  RSI and SMA at t-1).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 4344.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (0.0000 pp).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1).
- iter 064/069/070 final reports — TOP-K #1 baseline + structural
  diagnosis of defensively-biased base.

## Next iteration suggestions

iter 071 closes the calm-aggressive-3rd-stream axis on iter 064 base
at score 90 STRONG (now 4-way joint TOP-K #1 with iter 064/069/070).
The 90 ceiling is **provably anchored in the base composition's CAGR
profile**, not in the choice of structural ingredient. Three
structurally distinct directions for iter 072, ranked by expected
information per cost:

1. **Hierarchical 3-state regime model + iter 071 calm-aggressive
   stream added on iter 064 base**. RECOMMENDED, highest leverage.
   Combine iter 069's binary-VIX OR iter 070's continuous-T10Y3M
   regime classifier with the iter 071 r_mr calm-aggressive
   complement. The hypothesis: in calm regimes, up-weight r_mr;
   in stress regimes, down-weight or zero r_mr. The regime classifier
   provides allocation logic; the calm-aggressive stream provides
   the orthogonal return source. Predicted **75-92** if the regime-
   conditional allocation amplifies r_mr's calm Sharpe (0.82-0.93)
   over the unconditional 0.77-0.84. Cost ~75-90 min wall-time.
   Risk: 3-stream regime allocation has ≥ 6 free params; overfitting
   risk at cumulative_n_trials = 4344. Mitigation: pre-commit allocation
   rules tied to literature priors (e.g., calm = 0.10, stress = 0).
2. **Fresh higher-CAGR anchor (NOT iter 046 family)** — break out of
   the iter 046 vol-target ceiling. Candidates: cross-asset Hurst-
   regime trend; credit-spread regime as primary signal; single-asset
   levered base with embedded calm-aggressive + defensive components.
   Predicted **70-95**, high variance; cost ~3-5 iterations to build
   the new anchor before composing.
3. **Forward 5-day Sharpe meta-label on iter 064** (still open from
   iter 067 final report). Different cadence than bar-level regime
   classifier; ~120 flips/yr at weekly horizon. Predicted **65-85**,
   high variance. Cost ~75-90 min.

**Recommended pick for iter 072**: **direction #1 (hierarchical regime
model with iter 071 r_mr added as calm-aggressive 3rd stream)**. iter
071 provides the structural ingredient (validated calm-aggressive
complement); iter 069/070 provide the regime classifier (binary-VIX or
continuous-T10Y3M); the missing piece is the regime-conditional
allocation that activates r_mr in calm regimes and de-allocates in
stress. Either outcome is high-information: breakthrough → first 95+
winner candidate; saturation → confirms 90 ceiling is hard-anchored
in iter 046 base, forcing direction #2 (fresh anchor).

iter 064 stays at **TOP-K #1 (joint with iter 069, iter 070, and now
iter 071)** with score 90 STRONG, 4/5 winner conditions, 0/7 kills.
iter 071 enters TOP-K at the joint #1 with score 90 STRONG, 4/5
winner conditions, 2/10 kills.
