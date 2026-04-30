# Iter 018 — H1 META-ENSEMBLE (A2 closest-to-winner × G2 IEF Pareto-MDD × F1 stack always-on)

**Date**: 2026-04-30
**Cumulative n_trials before**: 53 (after iter 017)
**Cumulative n_trials after**: 53 + 3 = **56**
**Hunt status entering iter 018**: CLOSED (KILL #33 fired iter 011, reinforced 11 times across 8 fams + 3 hybrids)

---

## Why iter 018 at all

The hunt is formally CLOSED. Documentation through iter 017 explicitly
states "Suggested iter 018+: NONE — hunt remains CLOSED at 67-cap with
8 fams + 3 hybrids".

Iter 018 is run as a **post-impossibility META-LEVEL probe** on a
genuinely new orthogonal axis not yet mapped by the hunt: **portfolio-
of-strategies (meta-ensemble at strategy-level)** rather than asset-level
diversification. This is the only architectural axis that remains
untested in the formal taxonomy.

Per `[advances_fin_ml, ch.16, p.241-256]` portfolio-construction over
multiple alpha streams, and `[risk_parity, ch.5, p.10]` Carlson capital-
efficient stacking applied at strategy-level (not asset-level), low-
correlated strategies blended at meta-portfolio level CAN produce
Pareto-superior risk/return than any single constituent. The hunt's 8+3
empirical surface clusters in 52-67 score range — meta-ensemble of two
configs from this surface is genuinely untested.

---

## Hypothesis

**H1 (primary)**: A meta-ensemble of A2 closest-to-winner (CAGR-rich,
QQQ-gated 3× LETF + KMLM crisis-alpha) and G2 IEF (Sharpe/MDD-rich,
SPY-gated 2.25× LETF All-Weather + IEF defensive) at portfolio-of-
strategies level (50/50 or 70/30 blend) lifts the spy_beater score
above the 67-cap. Decorrelation arises from (a) different gate signals
(QQQ vs SPY; correlation ~0.85-0.90 but not 1.0), and (b) different
ON-state composition (concentrated NDX equity vs balanced multi-asset).

**H2 (orthogonal probe)**: A mixed-regime ensemble (60% A2 gated +
40% F1 stack always-on) tests whether always-on multi-asset diversifier
combined with regime-gated concentrated equity beats either alone in
spy_beater rubric. The always-on constituent NEVER goes defensive,
providing constant CAGR floor; the gated constituent provides bear-
avoidance and bull-rally CAGR upside.

**H3 (path-to-90 probe)**: If H1 score lifts to 68-72 range (above
67-cap), then KILL #33 INVALIDATED at meta-level and hunt REOPENS for
deeper meta-ensemble exploration (iter 019+ would sweep meta weights).
If H1 score caps ≤ 67, KILL #33 generalizes to meta-portfolio level
and the negative result is structurally STRENGTHENED across all
architectural axes (asset, gate, decay, AND meta).

---

## Configs (3 — minimal sweep to test H1/H2/H3)

| config | constituent A | weight | constituent B | weight | gate behavior |
|:-------|:-------------|-------:|:--------------|-------:|:-------------|
| h1_meta_50a2_50g2ief | iter 006 a6_tqqq_split_kmlm30_tlt10 (A2) | 0.50 | iter 017 g2_f1_letf_2x_sma200_ief (G2) | 0.50 | gates differ (QQQ vs SPY) |
| h1_meta_70a2_30g2ief | iter 006 A2 | 0.70 | iter 017 G2 IEF | 0.30 | gates differ (QQQ vs SPY) |
| h1_meta_60a2_40f1stack | iter 006 A2 | 0.60 | iter 015 f1_aw_stack_15x (F1 stack) | 0.40 | A2 gated, F1 stack always-on |

**Constituent A (A2 closest-to-winner)** spec:
```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {"TQQQSIM": 0.30, "QLDSIM": 0.30, "KMLMSIM": 0.30, "TLTSIM": 0.10},
  "off_weights": {"IEFSIM": 1.0},
  "signal_ticker": "QQQSIM",
  "lag_days": 1
}
```

**Constituent B1 (G2 IEF)** spec:
```json
{
  "type": "lrs",
  "on_weights": {"UPROSIM": 0.30, "TMFSIM": 0.25, "IEFSIM": 0.15, "UGLSIM": 0.15, "KMLMSIM": 0.15},
  "off_weights": {"IEFSIM": 1.0},
  "signal_ticker": "SPYSIM",
  "sma_window": 200,
  "filter": "sma",
  "lag_days": 1
}
```

**Constituent B2 (F1 stack)** spec:
```json
{
  "type": "static",
  "weights": {"NTSXSIM": 0.35, "GDESIM": 0.30, "TLTSIM": 0.20, "KMLMSIM": 0.15}
}
```

---

## Pre-committed KILL conditions

KILLs #1-#57 prior. New KILLs #58-#61:

### KILL #58 — META-ENSEMBLE caps ≤ 67 (KILL #33 generalizes to meta-level)

**Trigger**: `max(score across H1 configs) ≤ 67`

**Fires if**: best H1 score ≤ 67 (architectural ceiling holds at meta-level)

**Implication if FIRED**: KILL #33 strengthens from "8 fams + 3 hybrids"
to "8 fams + 3 hybrids + meta-ensemble". The architectural ceiling now
generalizes across asset-axis, gate-axis, decay-axis, AND meta-portfolio
axis. Hunt remains CLOSED.

### KILL #59 — META-ENSEMBLE breaks ceiling (KILL #33 INVALIDATED at meta-level)

**Trigger**: `max(H1 score) ≥ 70 AND winner_conditions_met=True`

**Fires if**: any H1 config scores ≥ 70 with all 3 strict bars met

**Implication if FIRED**: KILL #33 INVALIDATED at meta-level. Hunt REOPENS
for deeper meta-ensemble exploration (iter 019+ would sweep weights and
gate combinations). Mandate §7 review case becomes formal action.

### KILL #60 — Same-gate-family blend Pareto-dominates mixed-gate blend

**Trigger**: `score(h1_meta_50a2_50g2ief) > score(h1_meta_60a2_40f1stack)`
AND `mean Sharpe(h1_meta_50a2_50g2ief) > mean Sharpe(h1_meta_60a2_40f1stack)`

**Fires if**: gate-aligned (both LRS) blend beats mixed (gated + always-on)
on score AND Sharpe.

**Implication if FIRED**: when blending decorrelated regime-gated strategies,
gate alignment (both go defensive together) is preferred over diversifier
that never goes defensive. Suggests bear-avoidance dominates always-on
diversification at spy_beater rubric.

### KILL #61 — META-ENSEMBLE Sharpe Pareto-improves on best constituent

**Trigger**: `max(mean Sharpe across H1 configs) > 0.97` (G2 IEF best
Sharpe among CAGR-passers in iter 017)

**Fires if**: best H1 config has higher mean Sharpe than its best
constituent.

**Implication if FIRED**: meta-ensemble compresses vol via decorrelation;
true portfolio-of-strategies value at this leverage band. Validates
[advances_fin_ml, ch.16] thesis empirically.

---

## Expected outcomes (analytical, not pre-committed KILLs)

Linear-mean estimates (NOT path-aware; actual MDD is path-dependent):

| config | est CAGR | est MDD | est Sharpe | est score | bars |
|:-------|---------:|--------:|-----------:|----------:|:-----|
| h1_meta_50a2_50g2ief | 0.5×17.33 + 0.5×14.02 = **15.68%** | linear ~41.7% | ~0.86 | ~67-70 | 3/3 |
| h1_meta_70a2_30g2ief | 0.7×17.33 + 0.3×14.02 = **16.34%** | ~44.9% | ~0.81 | ~67-69 | 3/3 |
| h1_meta_60a2_40f1stack | 0.6×17.33 + 0.4×11.95 = **15.18%** | ~40.6% | ~0.89 | ~66-68 | 3/3 |

These are pure linear estimates ignoring (a) MDD path-dependence (likely
LOWER actual MDD when constituents decorrelate), (b) Sharpe vol-compression
via decorrelation (likely HIGHER actual Sharpe). So actual scores could
be 1-3pts above linear estimates if decorrelation works.

**Path-to-67-break analysis**:
- If actual h1_meta_50a2_50g2ief MDD = 38% (3pp better than linear) due
  to gate decorrelation, MDD pts → 12 (vs A2's 7) = +5. CAGR mean 15.68%
  → 21 pts (vs A2's 25) = -4. Sharpe ~0.95 → 3 pts (vs A2's 2) = +1.
  Net +2pts → score ~69. Could break 67-cap by 2pts.
- If MDD path-decorrelation gives only 1pp better than linear, score ~67
  (tied). KILL #58 fires.

---

## Anti-overfit posture

- **Pre-commit hypothesis BEFORE running** — 4 KILLs documented above.
- **Cumulative n_trials = 56** for DSR penalty per `[advances_fin_ml,
  p.222-223]`. DSR will tighten ~6% vs iter 017 (53 trials).
- **Constituents are existing iter-006 / iter-015 / iter-017 specs** —
  no new free parameters introduced; H1 only adds blend weights.
  Effective new parameters: 3 (one per config: 0.50, 0.70, 0.60).
- **Same anchor ranges + 2-dataset framework + 7-gate battery** as iter
  017 — no methodology drift.
- **Honest reporting**: if KILL #58 fires, the negative-result claim
  STRENGTHENS to architectural ceiling generalizes across meta-axis. If
  KILL #59 fires, hunt REOPENS legitimately.

---

## Why this iter (when hunt is CLOSED)

User explicitly requested iter 018 in session prompt. The most defensible
iter 018 hypothesis is one that:
1. Tests a NEW orthogonal architectural axis (meta-portfolio, not yet mapped).
2. Has clear literature backing ([advances_fin_ml ch.16, risk_parity ch.5]).
3. Has KILLs that can either reinforce or break the architectural ceiling.
4. Reuses existing infra (no new module if "blend" type added trivially).
5. Tests directly whether portfolio-of-strategies can break 67-cap.

H1 META-ENSEMBLE satisfies all 5. If KILL #58 fires (most likely), the
negative-result claim becomes empirically structural: "8 fams + 3 hybrids
+ meta-ensemble all cap ≤ 67". If KILL #59 fires (less likely but
possible per linear-estimate analysis), hunt REOPENS legitimately.

---

## INCOMPLETE flags (pre-acknowledged)

- **Linear-mean MDD estimate is conservative upper bound** — actual blended
  MDD is path-dependent and typically LOWER than linear due to decorrelation.
  Will report actual.
- **A2 + G2 IEF gate correlation ~0.85-0.90** (QQQ vs SPY): meta-ensemble
  decorrelation benefit will be moderate, not large. F1 stack always-on
  gives more decorrelation but at CAGR cost.
- **Cumulative n_trials = 56** lifts DSR penalty mildly but worst p was
  9.50e-05 in iter 017 — strong margin should survive.
- **NEW infra: "blend" spec type** added to `returns_from_spec` (≈30
  LOC) + 3 TDD tests. 765 → 768 tests baseline.
- **Sleeve effective leverage**: meta-ensemble = 0.5 × A2 (3.0× ON / 1× OFF)
  + 0.5 × G2 IEF (2.25× ON / 1× OFF). When BOTH gates ON: ~2.6× equity. When
  BOTH OFF: 1× IEF. When one ON one OFF (mixed regime): ~1.6× weighted.
- **Plot generation reuses existing run_iter plotting helper** — no new
  plot code.

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA gate
  rationale (both A2 QQQ-track and G2 SPY-track use this gate type).
- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction — multiple
  alpha streams blended at meta-level.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking thesis
  generalized to strategy-level diversification.
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM) — present
  in both A2 (30%) and G2 (15%) constituents.
- Bridgewater All-Weather (Dalio 1996) — F1 stack ON-state composition.
- HFEA Bogleheads 2019 — barbell logic generalized.
- `[advances_fin_ml, p.31-34]` factor framework — meta-ensemble adds
  the "ensemble axis" to the architectural taxonomy (asset, gate, decay,
  meta).
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 56 (53 + 3).
- `[advances_fin_ml, p.208-211]` PBO grid-level — N=3 warning persists.
- `[advances_fin_ml, p.196-202]` bootstrap CI G6 expected to pass.
