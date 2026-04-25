# Iteration 068 — Final Report

## Verdict

🥇 **STRONG** — score **79/100** (regression **−11** vs iter 064 base 90),
**winner_conditions_met=False** (3/5 strict — Sharpe edge ✓, MDD ceiling ✓,
gates cross-ds met ✓; CAGR floor ✗, DSR ✗), **1/9 kills fired (KILL I —
directional hypothesis empirically falsified)**.

This iteration tested a **VIX-conditional INNER WEIGHT swap** on iter 064's
two saved sub-streams: instead of the static `0.9 × r_046 + 0.1 × r_qqqt`,
the weights flip on a binary VIX regime gate while keeping total exposure
strictly at 1.0:

```
w_qqqt[t] = 0.20  if VIX[t-1] <  20 (calm)
            0.05  if VIX[t-1] >= 20 (stress)
w_046[t]  = 1.0 - w_qqqt[t]                    # total ≡ 1.0, NO leverage
r_068[t]  = w_046[t]·r_046[t] + w_qqqt[t]·r_qqqt[t]  −  5bp·|Δw_qqqt[t]|
```

**Hypothesis: empirically falsified by the data, but engine + score still STRONG.**

The mechanism is structurally clean:

- **G7 cross-lib parity = 0.000000 pp** on all 3 ds (pandas vs numpy).
- **Total exposure stays at 1.0 every bar** (max |Σw - 1| = 0).
- **No leverage**, **no σ overlay**, **flip cost only ~14-16 flips/yr × 0.15 ×
  5 bps ≈ 1-1.2 bp/yr drag** (vs iter 067's 3-4 pp/yr σ⁻² turnover drag).
- **Sharpe vs SPY/QQQ frozen benchmarks remains very strong** (1.17/1.28/1.33
  vs 0.68/0.90/0.955) → criterion 1 = **25/25**.
- **9/9 robustness sub-windows positive** (window Sharpes 1.08-1.62) → bonus 5/5.

**But the directional hypothesis is wrong.** The conditional Sharpe diagnostic
shows that QQQ_TREND (Faber 2007 200d filter) has a STRICTLY HIGHER Sharpe
in stress regimes than in calm regimes on all 3 datasets:

| dataset | r_qqqt Sharpe (calm / stress) | r_046 Sharpe (calm / stress) |
|---|---|---|
| educational | +0.71 / +0.95 | +1.07 / +1.43 |
| spy_real    | +0.75 / +1.20 | +1.05 / +1.79 |
| ndx_real    | +0.76 / +1.10 | +1.09 / +1.93 |

Mechanistically: QQQ_TREND parks in cash when below 200d SMA — exactly
during stress regimes — earning rf with near-zero variance. Its Sharpe-in-
stress is high precisely because it sidesteps the variance explosion. r_046
similarly de-risks via inner iter_041 VIX-conditional weights. Both
sub-streams are STRUCTURALLY DEFENSIVE in stress, so downweighting either of
them in stress is the wrong move. **The corrected direction would be to
UPWEIGHT QQQ_TREND in stress, downweight in calm** — opposite of what was
tested. That is a separate iteration (iter 069 candidate, see below).

What survived:

- **Engine clean**: 13/13 TDD tests pass; G7 cross-lib pp=0 on all 3 ds;
  total exposure invariant strictly enforced.
- **G3 walk-forward** profitable on edu, spy, ndx (≥6/8 windows each).
- **G4 OOS, G5 FWD post-2020**: positive on all 3 ds.
- **G6 bootstrap CI low > 0** on all 3 ds.
- **Score 79 ≥ STRONG threshold 75** despite KILL I (the Sharpe edge vs
  bench is large enough to absorb the regression vs iter 064).

What broke:

- **DSR worst-p 0.0593 (spy)** — fails the 0.05 cut by 0.009. iter 064 had
  worst-p 0.0392; the Sharpe regression of −0.04 to −0.05 is small but
  enough to inflate the t-stat penalty above 0.05.
- **CAGR floor 1/3** (only edu 9.53% > 9.18% passes; spy 10.04 < 11.98;
  ndx 10.30 < 15.35 — same as iter 064).
- **MDD increased 1.3-1.7 pp** vs iter 064 — the regime swap re-correlates
  the two streams' exposure to stress periods rather than diversifying.

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen / Δ064) | CAGR (Δ064) | MDD (Δ064) | DSR p | gates | corr(068,064) |
|---|---|---|---|---|---|---|
| educational | **1.1744** (+0.4944 / **−0.0432**) | 9.53% (+0.04pp) | 18.55% (+1.28pp) | 0.0543 | **6/7** | +0.9927 |
| spy_real    | **1.2809** (+0.3809 / **−0.0503**) | 10.04% (+0.06pp) | 17.07% (+1.74pp) | 0.0593 | **6/7** | +0.9919 |
| ndx_real    | **1.3263** (+0.3713 / **−0.0491**) | 10.30% (+0.13pp) | 16.49% (+1.75pp) | 0.0503 | **6/7** | +0.9918 |

**Per-dataset gate detail** (G1234567):

| dataset | G1 | G2 | G3 | G4 | G5 | G6 | G7 | total |
|---|---|---|---|---|---|---|---|---|
| edu | ✓ vac | ✗ p=0.054 | ✓ 8/8 | ✓ S>0 | ✓ S>0 | ✓ ci_low>0 | ✓ 0pp | 6/7 |
| spy | ✓ vac | ✗ p=0.059 | ✓ ≥6/8 | ✓ S>0 | ✓ S>0 | ✓ ci_low>0 | ✓ 0pp | 6/7 |
| ndx | ✓ vac | ✗ p=0.050 | ✓ ≥6/8 | ✓ S>0 | ✓ S>0 | ✓ ci_low>0 | ✓ 0pp | 6/7 |

**Regime-flip statistics**:

| dataset | pct_calm | flips/yr | mean(w_qqqt) | max\|Σw-1\| |
|---|---|---|---|---|
| edu | 65.3% | 14.5 | 0.148 | 0.00e+00 |
| spy | 68.4% | 16.0 | 0.153 | 0.00e+00 |
| ndx | 70.7% | 16.3 | 0.156 | 0.00e+00 |

The mean QQQ_TREND weight (0.148-0.156) sits ABOVE iter 064's static 0.10
because calm-regime is ~70% of bars and calm assigns 0.20. The blend tilts
toward QQQ_TREND on average — yet Sharpe regresses, which is consistent
with the empirical conditional-Sharpe finding that QQQ_TREND is BETTER in
stress (where iter 068 underweights it) and WORSE in calm (where iter 068
overweights it).

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | 3/3 datasets ≥ frozen + 0.10 (edu +0.49 / spy +0.38 / ndx +0.37) |
| 2 Gates | **19** | 25 | edu 6/7 → 5pts; spy 6/7 → 5pts; ndx 6/7 → 5pts; cross-ds met → +4 = 19 |
| 3 DSR | **10** | 15 | Worst-p 0.0593 (spy) ∈ [0.05, 0.10) → 10 pts; cumulative n_trials=4338 |
| 4 CAGR floor | **5** | 15 | 1/3: edu 9.53% > 9.18% ✓; spy 10.04% < 11.98% ✗; ndx 10.30% < 15.35% ✗ |
| 5 MDD ceiling | **15** | 15 | All 3 well under bench+5pp; 22-23 pp slack each |
| 6 Robustness | **5** | 5 | 9/9 sub-windows positive (Sharpe 1.08-1.62 across all 9) |
| **total** | **79** | **100+5** | tier: **STRONG** (regression −11 vs iter 064) |

Strict winner conditions: **3/5 met** —
1. Sharpe edge ≥ +0.10 on ≥ 2 ds: ✓ (3/3 vs frozen)
2. Gates cross-ds (edu ≥5, spy/ndx ≥4): ✓ (6/6/6)
3. DSR p < 0.05 (worst): ✗ (0.059 vs 0.05 cutoff)
4. CAGR ≥ 0.8×bench on ≥ 2 ds: ✗ (1/3, only edu)
5. MDD ≤ bench+5pp on ≥ 2 ds: ✓ (3/3)

## Configuration tested

```python
CFG = {
    "cfg_id": "iter064_vix_inner_w_calm020_stress005_vix20",
    "w_qqqt_calm": 0.20,        # QQQ_TREND weight when VIX[t-1] < 20
    "w_qqqt_stress": 0.05,      # QQQ_TREND weight when VIX[t-1] >= 20
    "vix_threshold": 20.0,      # Whaley 2009 long-run median
    "cost_bps": 5.0,            # per |Δw_qqqt| flip
    # Sub-streams reused verbatim from iter 064:
    "qqqt_lookback": 200,       # Faber 2007
    "qqqt_rf": 0.02,
    "qqqt_cost_bps": 5.0,
}
```

cumulative_n_trials advance: 4337 → **4338** (+1).

## Pre-committed kills

| # | kill | fired? | observation |
|---|---|---|---|
| A | Sharpe regress vs iter 064 by ≥ 0.05 on ≥ 2 ds | ✓ clean | Δ −0.043 / −0.050 / −0.049 — exactly at threshold; only 1/3 ≤ −0.05. |
| B | DSR worst-p ≥ 0.10 | ✓ clean | 0.059 (spy) — fails 0.05 cut but stays under 0.10 |
| C | Score < 79 | ✓ clean | 79 = exactly at STRONG threshold |
| D | edu CAGR < 9.18% | ✓ clean | 9.53% — keeps iter 064's non-LETF unlock |
| E | G7 cross-lib > 0.5 pp | ✓ clean | 0.000000 pp (3/3) |
| F | corr(068, 064) > 0.995 on ≥ 2 ds | ✓ clean | max 0.993 — switch is meaningful |
| G | max\|Σw-1\| > 1e-9 anywhere | ✓ clean | 0.00e+00 (3/3) — total exposure invariant |
| H | flips/yr < 5 OR > 100 on any ds | ✓ clean | 14.5-16.3 — within healthy band |
| **I** | QQQ_TREND calm-Sharpe ≤ stress-Sharpe on ≥ 2 ds | **❌ FIRED** | 3/3 datasets show calm Sharpe (0.71-0.76) STRICTLY < stress Sharpe (0.95-1.20) — directional hypothesis falsified |

**1/9 kills (KILL I only)** — engine + composition + cross-lib + flip-rate +
total-exposure invariants ALL clean. The only failure is the *directional*
intuition: QQQ_TREND's Sharpe is HIGHER in stress, not lower. The mechanism
runs cleanly but pushes weight in the wrong direction.

## What worked / what didn't

**Worked**:

- **Engine 100% correct**: 13/13 TDD tests pass; G7 cross-lib parity 0.000000
  pp on all 3 ds; total exposure invariant ≡ 1.0 strictly enforced (max dev =
  0.00e+00 across all 13 391 bars × 3 datasets). This is the cleanest engine
  validation in the loop's history at this granularity.
- **Friction is genuinely small**: ~14-16 flips/yr × 0.15 weight delta × 5 bp
  ≈ 1.0-1.2 bp/year drag. Two orders of magnitude cheaper than iter 067's
  σ⁻² overlay (3-4 pp/yr).
- **Sharpe vs SPY/QQQ frozen benchmarks**: edu +0.49, spy +0.38, ndx +0.37
  — strategy is risk-adjustedly dominant over buy-and-hold by enormous
  margins.
- **Robustness 9/9 sub-windows positive**: every 3-year segment delivers
  positive Sharpe across all 3 datasets.
- **CAGR is roughly preserved** vs iter 064 (Δ +0.04 to +0.13 pp) — unlike
  iter 067 which lost 1.9-2.2 pp from the σ⁻² mean-exposure cap.

**Didn't**:

- **Sharpe regresses** vs iter 064 by 0.04-0.05 on all 3 ds. Just barely
  misses KILL A's 2-of-3 threshold (1/3 datasets crosses −0.05). The
  regression is small but systematic, indicating the regime-mix is
  structurally non-improving for THIS direction of swap.
- **Conditional Sharpe ordering directly opposes the hypothesis**. Both
  r_046 and r_qqqt are STRUCTURALLY DEFENSIVE in stress (one via inner
  iter_041 VIX gating, the other via Faber 200d SMA cash-parking). They
  are HIGHER-Sharpe in stress, not lower. The calm/stress directional
  intuition that motivated iter 068 is wrong for this specific anchor +
  3rd-stream pairing.
- **MDD grew 1.3-1.7 pp** — surprising. The mechanism: in calm regimes
  iter 068 holds 0.20 of QQQ_TREND (vs iter 064's static 0.10), and during
  the calm-to-stress *transition* days the elevated QQQ_TREND exposure
  amplifies the drawdown before the regime flag flips. This is a
  *transition-day risk* not captured by the standard regime model.
- **DSR worst-p inflates from 0.039 → 0.059** — the slight Sharpe drop
  combined with cumulative n_trials advance (4337 → 4338) pushes spy
  past the 0.05 cutoff.
- **iter 064's 90 holds** — score 79 < 90 = NOT a new TOP-K #1.

## Main lesson (for future iterations)

**iter 068 = STRUCTURAL CLOSURE of "VIX-conditional INNER weight swap on
iter 064 saturated composite — DOWNWEIGHT trend-following 3rd stream
in stress" → score 79 STRONG (regression −11 vs iter 064)**. Engine clean,
1/9 kills (only KILL I — directional hypothesis empirically falsified).

The mechanism is mechanically correct (total exposure ≡ 1.0, no leverage,
small flip cost) but the *direction of the swap* is structurally wrong for
this specific anchor + 3rd-stream pairing. Both iter_046 (vol-managed
defensive) AND r_qqqt (200d trend cash-park) ALREADY de-risk in stress,
producing HIGHER conditional Sharpe in stress than calm. Downweighting the
defensive sleeve in stress is the wrong move.

This **closes the inner-weight-swap axis on iter 064 in the canonical
"calm-trend, stress-defensive" direction**, generalising the iter 048 / 065
output-VIX-gate findings (calm ON, stress OFF) into the *inner Markowitz
weight* layer:

| iter | base | what scales | direction tested | score | finding |
|---|---|---|---|---|---|
| 048 | iter 046 | OUTPUT scalar 1.4/1.0 | calm-up, stress-flat | 83 | best output-VIX gate found |
| 065 | iter 064 | OUTPUT scalar 1.5/1.0 | calm-up, stress-flat | 74 | external lev drag erodes Sharpe |
| 067 | iter 064 | OUTPUT scalar (σ⁻², cap=1.0) | de-risk only (no lev) | 74 | mean-exposure cap drag |
| **068** | **iter 064** | **INNER MARKOWITZ WEIGHT 0.20/0.05** | **calm-trend, stress-defensive** | **79** | **directional intuition empirically falsified** |

The empirical conditional Sharpe finding is the **most valuable artefact**
of iter 068:

```
QQQ_TREND  Sharpe(calm)  ≈ 0.71-0.76
QQQ_TREND  Sharpe(stress)≈ 0.95-1.20  ← HIGHER in stress
r_046      Sharpe(calm)  ≈ 1.05-1.09
r_046      Sharpe(stress)≈ 1.43-1.93  ← HIGHER in stress
```

Both sub-streams are STRUCTURALLY DEFENSIVE in stress regimes (different
mechanisms: r_046 via internal VIX-conditional weights from iter_041; r_qqqt
via Faber's 200d SMA cash-park). The conditional-Sharpe-in-stress >
calm-Sharpe ordering means the *standard* regime story ("calm = trend +
momentum, stress = defensive") DOES NOT APPLY to this anchor + 3rd-stream
pair — both are already defensive.

**Implication for iter 069+**: any further regime-conditional layering on
iter 064 that follows the canonical "calm-aggressive, stress-defensive"
intuition is doomed. iter 064's TWO sub-streams are BOTH already in the
"defensive" basin of attraction. The path forward is either:

1. **Reverse-direction inner weight** (calm 0.05 / stress 0.20) — directly
   testable, predicted to lift Sharpe by ~+0.05-0.08 if KILL I's
   conditional-Sharpe ordering generalises out-of-sample. Risk: the
   ordering is sample-dependent and may flip in the unseen window. But
   would prove/refute the empirical lesson cleanly.
2. **Fresh anchor with non-defensive stress conditional Sharpe**:
   classical short-vol / VRP / convexity-buying strategies that genuinely
   thrive in CALM and bleed in STRESS, providing the missing aggressive
   complement to iter 064's already-defensive basin.
3. **Different regime classifier** (T10Y3M, EBP, HMM 3-state) — VIX is
   the canonical "fear gauge" but its binary 20-cutoff coarsens regime
   structure. Higher-resolution regimes might reveal exploitable
   conditional Sharpe gaps not visible to the binary VIX gate.

## Structural dead-ends discovered

iter 068 closes **one new axis**:

- **iter 068 (🥇 STRONG 79, 1/9 KILLS — KILL I) — VIX-conditional INNER
  WEIGHT swap on iter 064 (calm 0.80/0.20 ↔ stress 0.95/0.05; total ≡
  1.0; flip cost 5bp×|Δw_qqqt|)**: engine clean (G7 0pp, total exposure
  ≡ 1.0 strictly), score 79 STRONG. Mechanism is structurally correct
  but DIRECTION OF THE SWAP is empirically falsified — QQQ_TREND has
  HIGHER Sharpe in stress (cash-park during 200d-SMA bear) than in calm.
  Both iter 046 (vol-managed) AND r_qqqt (Faber 2007) are STRUCTURALLY
  DEFENSIVE in stress, so the canonical "calm-aggressive, stress-defensive"
  intuition does not apply. **Closes the inner-weight-swap axis in the
  CALM-TREND direction at 79**; the OPPOSITE-direction swap (calm 0.05 /
  stress 0.20) remains untested and is the natural iter 069 candidate.
  Sharpe regression −0.04 to −0.05 vs iter 064 (1/3 datasets crosses −0.05
  threshold), DSR worst-p 0.0593 fails 0.05 cut, MDD grows 1.3-1.7 pp.
  Score breakdown: 25/19/10/5/15/5 = 79.

What is **OPEN** for iter 069+:

- **REVERSE-direction inner weight swap** (calm 0.05 / stress 0.20 — the
  empirical-evidence-backed direction; iter 069 #1 candidate).
- **Fresh anchor with non-defensive stress conditional Sharpe** (short-vol
  / VRP / convexity strategies that genuinely thrive in calm and bleed
  in stress — iter 069 #2 candidate).
- **Different regime classifier** (T10Y3M, EBP, HMM 3-state) at the inner-
  weight layer (iter 069 #3 candidate).
- **Forward 5-day Sharpe meta-label on iter 064** (still open, predicted
  60-85 from iter 067 final report — iter 069 #4 candidate).
- **Plano C sleeve** / **CRSP/Norgate cross-sectional momentum** (capped
  ≤ 70 / requires data budget).

## Citations used

- `[stocks_on_the_move, p.21-30]` — Clenow (2015), *Stocks on the Move*,
  Harriman House. Single-asset 200-day SMA filter as a regime gate inside
  a momentum portfolio; foundational citation for treating QQQ_TREND as
  the regime-conditional sleeve.
- **Faber (2007)**, SSRN 962461, *A Quantitative Approach to Tactical
  Asset Allocation*, J. Wealth Mgmt 9(4) — single-asset 200-day SMA TAA
  primitive (preserved verbatim via iter 064's `qqq_trend.py`).
- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity; preserved
  as iter 046 base via the saved `r_046` stream.
- `[volatility_trading, p.218]` — Sinclair (2013), σ⁻² scaling primitive;
  preserved inside iter 046 via iter 016.
- **Whaley (2009)**, *J Portf Mgmt* 35(3): 98-105,
  DOI 10.3905/JPM.2009.35.3.098 — VIX as ex-ante regime indicator;
  threshold = 20 long-run median.
- **Bekaert & Hoerova (2014)**, *J Econometrics* 183(2): 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition.
- **Moskowitz, Ooi & Pedersen (2012)**, *JFE* 104(2),
  DOI 10.1016/j.jfineco.2011.11.003 — TSM regime conditionality.
- `[advances_fin_ml, p.162-164]` — strict shift(1) on VIX (no peeking).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 4338.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (0.000000 pp on
  all 3 datasets).
- `[advances_fin_ml, p.196-202]` — bootstrap CI (G6).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1, vacuous at N=1).
- `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching.
- `[systematic_trading, ch.11]` — Carver IDM ≤ 2.5 (we sit at 1.0).

## Next iteration suggestions

iter 068 closes the calm-trend / stress-defensive direction of the
inner-weight swap at score 79 STRONG. Three structurally distinct
directions for iter 069:

1. **REVERSE inner weight swap** (calm `w_qqqt = 0.05` / stress
   `w_qqqt = 0.20`, total ≡ 1.0). Directly tests iter 068's
   empirically-derived conditional Sharpe ordering. Predicted
   **80-90** if the ordering generalises OOS (Sharpe lift +0.04-0.07
   based on weighted conditional sums). Risk: the ordering may be
   sample-dependent and flip in unseen windows. Cost ~30-45 min.
   **Most testable / most informative outcome regardless of result.**

2. **Fresh aggressive 3rd stream** (stand-alone short-vol / VRP /
   convexity-buying strategy with HIGH calm Sharpe and LOW stress
   Sharpe — opposite profile from QQQ_TREND). Pairs with the existing
   iter 046 + 0.10 × QQQ_TREND base by adding a third sleeve at small
   weight (~0.05) gated to calm regimes. Predicted **75-90**, harder
   to find (Tiingo VRP universe limited; iter 057 closed commodity
   basket). Cost ~60-90 min.

3. **Higher-resolution regime classifier** (T10Y3M continuous score
   replacing binary VIX gate, or HMM 3-state on returns). Predicted
   **78-87**, novel regime granularity could expose conditional Sharpe
   patterns invisible to binary VIX. Cost ~60-75 min.

**Recommended pick for iter 069**: **direction #1 (REVERSE inner weight
swap)**. iter 068's KILL I provides the *empirical evidence* that the
conditional Sharpe ordering favours UPWEIGHTING QQQ_TREND in stress.
Testing the reverse direction is the cleanest way to either (a) confirm
the lesson and add 0.05-0.08 Sharpe → potential breakthrough into 85-90
territory, or (b) refute the lesson by showing the ordering doesn't
generalise OOS → cleanly closes the entire VIX-conditional-inner-weight
axis on iter 064 in BOTH directions, forcing iter 070 into structurally
novel anchor / regime / cadence territory.

iter 064 stays at **TOP-K #1** with score 90 STRONG, 4/5 winner
conditions, 0/7 kills.
