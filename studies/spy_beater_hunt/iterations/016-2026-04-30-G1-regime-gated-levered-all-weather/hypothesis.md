# Iter 016 — G1 Regime-Gated Levered All-Weather (F1×A2 cross-product hybrid)

**Slug**: `G1-regime-gated-levered-all-weather`
**Iter letter**: G1 (NEW second cross-product hybrid family — SMA-gate × F1-stack-sleeve)
**Cumulative n_trials**: 47 → **50** (this iter adds 3)
**Date**: 2026-04-30
**Pre-commit timestamp**: before any backtest runs

---

## Why this iter (post-impossibility second hybrid sanity check)

Iter 011 declared `IMPOSSIBILITY_RESULT` and KILL #33 (architectural ceiling
at 67) on 4-family evidence; iters 012-015 reinforced KILL #33 across **7
distinct architectural families + 1 cross-product hybrid (E1, iter 014)** —
none exceeded 67.

**Iter 015 (F1 Levered All-Weather)** was the most successful PROMISING-tier
iter on Sharpe + MDD axes:
- f1_aw_stack_15x: mean Sharpe **1.018** (FIRST > 1.0 in entire hunt), mean
  MDD **26.82%** (best among CAGR-passers), mean CAGR 11.95%, score 61.
- BOTH stack and LETF configs passed all 3 strict bars (winner_conditions_met=True
  for two configs in a single iter for the first time).
- **5y rolling pass-rate only 33.3%** — F1 underperforms SPY in short bull
  windows due to bonds/MF allocation that always-on dilutes equity.

**Iter 015's lesson** explicitly flagged the F1×A2 hybrid as the natural
closing test on the F1 family:

> "Adding regime gate to F1 (cross-product F1×A2 hybrid) might lift +3-5pp on
> Robustness via better short-horizon CAGR but iter 014 showed cross-product
> hybrids cap BELOW union of single-axis maxima (decay-dominated regime)."

**Critical empirical question**: iter 014 tested gate × sleeve at **3× LETF
(decay-dominated)** — gate × sleeve interaction was NEGATIVE (E1 hybrid
score 65 < union prediction 69-72). At **1.41× capital-efficient stacking
(no decay)**, does the orthogonality assumption flip back to positive? Or
does whipsaw cost dominate at any leverage on a balanced multi-asset
sleeve?

This is the **second explicit cross-product orthogonality test** at a
fundamentally different leverage/decay regime than iter 014. Distinct
empirical question — closes the F1 family fully.

**Architecturally complete after this iter**: 7 single-axis families + 2
cross-product hybrids (E1 at 3× LETF, G1 at 1.41× stack). Together they
span both regimes of the gate × sleeve orthogonality space.

---

## Hypothesis

**H₁ (architectural ceiling holds at no-decay)**: best G1 score ≤ 67.
The architectural ceiling claim (KILL #33) holds across BOTH decay
regimes — at 3× LETF (iter 014) AND at 1.41× stack (this iter).

**H₂ (whipsaw dominates at no-decay)**: at 1.41× stack, the regime-gate
adds whipsaw cost (false-positive re-entries during 1990s/2010s choppy
bull regimes) that EXCEEDS the bear-stress avoidance benefit. Net: G1
mean MDD ≥ F1 stand-alone (26.82%), G1 mean Sharpe ≤ F1 stand-alone
(1.018), G1 5y rolling pass-rate ≤ F1 (33.3%).

**H₃ (defensive-off composition matters)**: across 3 off-state composit-
ions (100% IEF, 100% KMLM, blend), there is NO universal optimum — the
2008 GFC favours bonds (IEF), 2022 inflation favours crisis-alpha
(KMLM), 2020 COVID is regime-gate-irrelevant due to fast V-recovery.

**H₄ (CAGR uplift from gate is real but small)**: regime gate avoids
2008/2022 stress periods → mean CAGR up by 1-3pp vs F1 stand-alone
(11.95%) → score +5-10pts on CAGR axis. But MDD likely down only 1-3pp
(F1 already avoids most of 2008 via bonds), Sharpe down 0-2pts (whipsaw
cost). Net: ~+2-5pts vs F1 standalone (61) → final score 63-66, still
below 67-cap.

**H₅ (KILL #51 false-positive guard)**: if G1 best score ≥ 70 and 3
strict bars met, hunt may need to reopen. Probability per literature
+ iter 014 evidence: ≤ 5%.

---

## Configs (3 trials → cumulative 50)

Slow stagger to manage DSR n_trials inflation (47 → 50; SESSION_PROMPT
note: "DSR n_trials inflation is the binding inflation; consider 3-4
configs at high n_trials to slow"). Each config probes a different
off-state defensive composition while holding F1 stack ON-state fixed.

### G1.1 `g1_f1_stack_sma200_ief` — F1 stack ON, 100% IEF OFF

```json
{
  "type": "lrs",
  "on_weights": {
    "NTSXSIM": 0.35, "GDESIM": 0.30, "TLTSIM": 0.20, "KMLMSIM": 0.15
  },
  "off_weights": {"IEFSIM": 1.0},
  "signal_ticker": "SPYSIM",
  "sma_window": 200,
  "filter": "sma",
  "lag_days": 1
}
```

Direct apples-to-apples vs iter 015 f1_aw_stack_15x (always-on) +
classical Gayed defensive (IEF). Tests whether removing the always-on
allocation when SPY < 200d SMA improves CAGR (avoiding bear drag) and
MDD (avoiding bear losses) without sacrificing too much in whipsaw cost.

### G1.2 `g1_f1_stack_sma200_kmlm` — F1 stack ON, 100% KMLM OFF

```json
{
  "type": "lrs",
  "on_weights": {
    "NTSXSIM": 0.35, "GDESIM": 0.30, "TLTSIM": 0.20, "KMLMSIM": 0.15
  },
  "off_weights": {"KMLMSIM": 1.0},
  "signal_ticker": "SPYSIM",
  "sma_window": 200,
  "filter": "sma",
  "lag_days": 1
}
```

Aggressive defensive: 100% crisis-alpha when bear. KMLM (managed-futures)
is the only sleeve with positive 2022 returns + positive 2008 returns
(via diversifying trend-following exposure to commodities/FX/rates).
Trade-off: KMLM has high standalone MDD in low-stress regimes (5-10%
typical), so off-state could underperform IEF in slow bear markets.

### G1.3 `g1_f1_stack_sma200_blend` — F1 stack ON, 50% IEF + 50% KMLM OFF

```json
{
  "type": "lrs",
  "on_weights": {
    "NTSXSIM": 0.35, "GDESIM": 0.30, "TLTSIM": 0.20, "KMLMSIM": 0.15
  },
  "off_weights": {"IEFSIM": 0.5, "KMLMSIM": 0.5},
  "signal_ticker": "SPYSIM",
  "sma_window": 200,
  "filter": "sma",
  "lag_days": 1
}
```

Balanced defensive: bonds + crisis-alpha 50/50. Hedges both 2008-style
(bonds win) and 2022-style (KMLM win) regimes. Predicted to be most
robust across the 2-dataset framework but with intermediate Sharpe vs
G1.1/G1.2.

---

## Pre-committed KILL conditions (numbered #50-#53; KILL #46-#49 from iter 015 already counted)

| # | name | trigger threshold | what fires |
|---:|:---|:---|:---|
| **#50** | G1 reinforces KILL #33 — Regime-gated F1 caps ≤ 67 | best G1 score ≤ 67 across 3 configs | strengthens architectural ceiling claim from "7 fams + 1 hybrid" to "7 fams + 2 hybrids"; F1 hybrid family CLOSED |
| **#51** | G1 breaks ceiling — KILL #33 INVALIDATED | best G1 score ≥ 70 AND all 3 bars met (winner_conditions_met=True) | hunt REOPENS; iter 017+ explores G1 dose-response (gate window, defensive blend, leverage); mandate §7 review trigger |
| **#52** | Adding regime gate to F1 stack hurts Sharpe (whipsaw dominates at no-decay) | mean Sharpe(g1_*) < mean Sharpe(f1_aw_stack_15x) = 1.018 across all 3 configs | confirms iter 014 finding generalizes: gate × sleeve interaction is NEGATIVE at BOTH 3× LETF AND 1.41× stack — universal closure of cross-product space |
| **#53** | 5y rolling pass-rate fails to lift above F1 stand-alone 33.3% | min(5y_rolling_passrate(g1_*)) ≤ 33.3% across all 3 configs | confirms always-on bonds drag is NOT the binding cause of low 5y pass-rate; gate cannot fix short-horizon underperformance |

---

## Expected outcomes

### Predicted results (pre-commit)

Based on iter 014 (E1 hybrid 65/100 at 3× LETF, gate × sleeve NEGATIVE)
+ iter 015 (F1 stand-alone 61/100 at 1.41× no-decay) + literature on
gate-on-balanced-portfolio:

| metric | F1 stand-alone (iter 015) | G1 best predicted | Δ |
|---|---:|---:|---:|
| score | 61 | 60-66 | −1 to +5 |
| mean CAGR | 11.95% | 12.5-13.5% | +0.5 to +1.5pp |
| mean MDD | 26.82% | 24-28% | −3 to +1pp |
| mean Sharpe | 1.018 | 0.85-0.95 | −0.07 to −0.17 |
| 5y rolling pass-rate | 33.3% | 30-45% | −3 to +12pp |
| 20y rolling pass-rate | 100% | 90-100% | −10 to 0pp |

**Most likely outcome**: G1 score 62-65, KILL #50 + KILL #52 fired,
KILL #51 + KILL #53 not fired. F1 hybrid family CLOSED at score < 67.

### Probability table (Bayesian prior)

| outcome | probability | trigger |
|---|---:|---|
| G1 score ≤ 67 (KILL #50 fires) | **88%** | architectural ceiling holds |
| G1 score ≥ 70 (KILL #51 fires, hunt reopens) | 5% | rare upside surprise |
| 67 < G1 score < 70 (no KILLs fire) | 7% | tight margin, requires careful sensitivity |
| G1 best Sharpe < 1.018 (KILL #52 fires) | 75% | whipsaw cost likely dominates |
| G1 best 5y pass-rate ≤ 33.3% (KILL #53 fires) | 60% | always-on bonds may not be binding |

---

## Why this is worth running despite hunt being CLOSED

1. **Fully closes the F1 family**: iter 015 left the regime-gated F1 hybrid
   as the single open question in the F1 family. Running G1 closes that
   question definitively.
2. **Tests orthogonality at the OPPOSITE decay regime from iter 014**: iter
   014 was 3× LETF (decay-dominated, MDD lift collapses); iter 016 is 1.41×
   stack (no decay). Together they span the full leverage-decay axis of
   gate × sleeve interaction.
3. **Closes the second cross-product hybrid family**: the architectural
   ceiling claim (KILL #33) becomes stronger with "7 fams + 2 hybrids" vs
   "7 fams + 1 hybrid".
4. **Marginal cost low**: 3 configs, no new module (reuses lrs spec type
   from iter 014 + portfolio_returns_from_config), DSR n_trials grows by
   only 3 (47 → 50).

---

## Pre-commit checklist

- [x] hypothesis.md written before any backtest run
- [x] 3 configs with consistent naming (`g1_f1_stack_sma200_<offstate>`)
- [x] 4 KILL conditions pre-committed and numbered (#50-#53)
- [x] Expected outcomes with probability table
- [x] Citations clearly stated
- [x] INCOMPLETE flags listed (PBO N=3 warning, TMFSIM 1.5%/y assumption,
      stacking 0% LETF decay assumption)
- [x] Cumulative n_trials tracked (47 → 50)
- [x] No metabolism change to scoring rubric (CAGR-anchored unchanged)

---

## INCOMPLETE flags

- **PBO N=3 warning** persists (CSCV statistically unstable with N<4).
  Both datasets rely on G2/G4/G5/G6/G7 to clear gates.
- **NTSXSIM/GDESIM stacking assumption**: 0% LETF decay (capital-efficient
  futures stacking, 0.5% rolling cost embedded). Real ETF tracking error
  may be 0.2-0.5%/y; assumption is mid-range.
- **F1 stack ON-state weights fixed**: this iter does NOT sweep ON-state
  composition. Sensitivity to ON-state weight choice deferred to KILL #51
  path if it fires.
- **Gate window fixed at 200d SMA**: this iter does NOT test EMA / momentum
  / faster signals (KILL #7/#8 fired in iter 002 close those for SPY-track;
  applicability to F1-stack-track unverified but very low prior).
- **2-dataset framework**: lh_56y (40y synth) + spy_real (22.7y Tiingo).
  ndx_real not used in spy_beater hunt per methodology refactor 2026-04-29.

---

## Citations

- **Bridgewater All-Weather (Dalio 1996, public papers 2011)** — F1 stack
  ON-state derives from canonical risk-parity construction; this iter
  tests whether Dalio-canonical balanced sleeve becomes a winner once
  augmented with Gayed regime gate.
- **Asness, Cliff (1996) "Why Not 100% Equities?" JPM** — leverage-
  balanced thesis confirmed at iter 015 1.41× notional (Sharpe 1.018).
  This iter tests whether regime gate amplifies the leverage-balanced
  edge or erodes it via whipsaw cost.
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA gate
  rationale; Gayed's empirical claim (CAGR uplift via bear avoidance)
  generalizes to balanced sleeves to be tested.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking
  (NTSX/GDE) Pareto-dominates LETF mix (iter 015 finding); this iter
  uses stack form to isolate gate value from decay drag.
- `[ilmanen_expected_returns, ch.19]` — MF crisis-alpha (KMLM) role;
  G1.2 tests aggressive defensive with 100% KMLM during bear regimes.
- `[advances_fin_ml, p.31-34]` factor framework — gate × sleeve
  orthogonality assumption explicitly tested at second decay regime
  (1.41× stack, no decay).
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 50, worst
  p target < 0.05.
- `[advances_fin_ml, p.208-211]` PBO N=3 warning persists.
- `[advances_fin_ml, p.196-202]` bootstrap CI G6 must pass.
- HFEA Bogleheads 2019 — counterexample: HFEA without regime gate is
  catastrophic at 2022 stress; F1 stack ALREADY has bonds + MF buffer,
  so gate may add less marginal value than on raw HFEA.
- Moskowitz/Ooi/Pedersen (2012) JFE 104(2):228-250 — TSMOM gate not
  used here (this iter uses 200d SMA per Gayed canonical).

---

## Conclusion

Iter 016 G1 is the **second cross-product hybrid sanity check** on KILL
#33, complementing iter 014's E1 hybrid at the OPPOSITE leverage-decay
regime. Predicted outcome: KILL #50 fires (G1 ≤ 67), F1 hybrid family
CLOSED, architectural ceiling claim strengthened to "7 fams + 2 hybrids".

Marginal value: closes the last open question in the F1 family AND tests
orthogonality at no-decay regime — completing the formal taxonomy of
spy_beater_hunt's controlled architectural exploration.
