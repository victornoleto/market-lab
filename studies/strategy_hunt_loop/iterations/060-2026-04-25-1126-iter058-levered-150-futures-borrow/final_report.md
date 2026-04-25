# Iteration 060 — Final Report

## Verdict

🥇 **STRONG** — score **79/100**, **winner_conditions_met=False**
(DSR worst-p 0.1251 ≥ 0.05 cutoff), **2/6 kills fired (A+B)**.

This iteration tested **direction #1 from BASE_MEMORY** (RECOMMENDED):
1.5× external leverage on iter 058's saved combined stream at **2.5%
futures-implied financing rate** (vs iter 056's 3.5% retail Reg-T
margin on iter 046 base). The structural distinction was the borrow
rate source — Treasury-futures roll cost (NTSX-style, Hsiao-Williams
2017) instead of retail margin spread — predicting a 3-5× lower
Sharpe drag than iter 056 measured.

**The empirical Sharpe drag was 5.2× larger than the analytical
prediction (0.117 observed vs 0.022 predicted)**, surfacing a
methodological discovery: the project's `_sharpe()` helper does NOT
subtract the risk-free rate (`risk_free=0.0` default), so the drag
formula ``(lev−1)×(b−rf)/(lev×σ)`` is wrong at this codebase's Sharpe
convention. The correct formula is ``(lev−1)/lev × daily_borrow ×
√252 / σ_daily`` — independent of rf — meaning **even risk-free borrow
(b=rf) imposes a 0.10+ Sharpe drag at 1.5× leverage on iter 058**.
This is a structural observation, not a bug: the codebase's Sharpe
convention treats the FULL borrow as drag, so any leverage at any
positive borrow rate degrades raw Sharpe.

Score 79 is **+5 over iter 056's 74** at the same leverage axis (1.5×
vs 1.3×, 2.5% vs 3.5% borrow on the iter-058-vs-iter-046 base) — the
lower borrow rate AND the iter 058 base's higher unlevered Sharpe
together produced a partial improvement, but not enough to break the
iter 056 closure pattern. **Score 79 < iter 058's 85**: leverage at
this rate doesn't break the saved-stream-pair Pareto ceiling.

This **closes the futures-leverage axis on iter 058 at borrow ≥ 2.0%
(any positive non-trivial spread)**. The next viable direction must
either find an anchor with simultaneously Sharpe ≥ 1.20 AND CAGR ≥
12% on real data WITHOUT external leverage, or pivot to a structurally
different mechanism (regime-conditional sizing, alternative 3rd
stream).

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen, Δ058) | CAGR (Δ058) | MDD (Δ058) | DSR p | gates |
|---|---|---|---|---|---|
| educational | 1.1054 (+0.4254, **−0.1171**) | 11.72% (**+3.03 pp** ✓) | 24.86% (**+8.12 pp**) | **0.1251** ✗ | **6/7** |
| spy_real    | 1.2220 (+0.3220, **−0.1254**) | 12.24% (**+3.23 pp** ✓) | 20.93% (**+7.22 pp**) | **0.0920** ✗ | **6/7** |
| ndx_real    | 1.2763 (+0.3213, **−0.1264**) | 12.64% (**+3.37 pp** ✗) | 20.11% (**+7.00 pp**) | **0.0733** ✗ | **6/7** |

iter 058 baseline (for delta reference): Sharpe 1.2225/1.3474/1.4027,
CAGR 8.69/9.01/9.27%, MDD 16.74/13.71/13.12%, DSR p
0.0494/0.0337/0.0258, gates 7/7/7.

CAGR floor pass: edu ✓ (11.72 ≥ 9.18), spy ✓ (12.24 ≥ 11.98), ndx ✗
(12.64 < 15.35). **2/3 datasets clear the floor** (vs iter 058's 0/3
and iter 056's 1/3) — leverage successfully converts MDD slack into
CAGR for edu/spy, but ndx's tighter floor (15.35%) requires more
leverage than the DSR-survival window allows.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | All 3 datasets beat frozen bench by ≥ 0.10 (Δ +0.43/+0.32/+0.32) |
| 2 Gates | **19** | 25 | 6/7 each (G1 PBO N=1 vacuous PASS, G2 DSR FAIL all 3) + cross-ds bonus +4 = 19/25 |
| 3 DSR | **5** | 15 | Worst-p 0.1251 (edu) ≥ 0.10 → bucket 5 (0.10 ≤ p < 0.20); n_trials=4330 |
| 4 CAGR floor | **10** | 15 | edu+spy ≥ 0.8×bench (11.72/12.24% vs 9.18/11.98%); ndx 12.64% < 15.35% |
| 5 MDD ceiling | **15** | 15 | All 3 ≤ bench+5pp (24.86/20.93/20.11% vs ceilings 60.14/38.70/40.12%) |
| 6 Robustness | **5** | 5 | 9/9 sub-windows positive (edu 1.03/1.20/1.17, spy 1.51/1.18/1.03, ndx 1.39/1.36/1.15) |
| **total** | **79** | **100+5** | tier: **STRONG** |

Strict winner conditions: **3/5 met** —
1. Sharpe edge ≥ +0.10 on ≥ 2 ds: ✓ (3/3)
2. Gates cross-ds (edu ≥5, spy/ndx ≥4): ✓ (6/6/6)
3. DSR p < 0.05 (worst): ✗ (0.1251)
4. CAGR ≥ 0.8×bench on ≥ 2 ds: ✓ (2/3)
5. MDD ≤ bench+5pp on ≥ 2 ds: ✓ (3/3)

DSR fails. Score 79 + winner_conds=False → **STRONG** (≥ 75, < 90).

## Configuration tested

```python
CFG = {
    "cfg_id": "iter058_levered_150_borrow_250bps",
    "lev": 1.5,                          # external leverage on iter 058
    "borrow_rate_annual": 0.025,         # NTSX futures-implied (T-bill 2% + 0.5% roll)
    "rf": 0.02,
    "iter058_cfg_id": "iter046_plus_hyg_tsm_w010_lookback90",  # base stream
}
```

cumulative_n_trials advance: 4329 → **4330** (+1).

## Pre-committed kills

| # | kill | fired? | observation |
|---|---|---|---|
| A | Sharpe regress vs iter 058 by ≥ 0.10 on ≥ 2 datasets | **❌ FIRED** | Δ −0.117/−0.125/−0.126 — all 3 datasets dropped > 0.10 vs iter 058 |
| B | DSR worst-p ≥ 0.10 | **❌ FIRED** | edu p 0.1251 ≥ 0.10 (spy 0.0920, ndx 0.0733 both below 0.10) |
| C | Score < 78 (iter 050 baseline) | ✓ clean | 79 ≥ 78 — narrowly above iter 050's 78 PROMISING ceiling |
| D | G7 cross-lib > 3pp | ✓ clean | 0.0000 pp on all 3 datasets (linear transform parity exact) |
| E | MDD breach > bench+5pp on ≥ 2 datasets | ✓ clean | 0/3 datasets breach (24.86/20.93/20.11% vs 60.14/38.70/40.12%) |
| F | CAGR floor 0/3 (no improvement) | ✓ clean | 2/3 floor pass (vs iter 058's 0/3) — leverage DOES propagate to CAGR |

**2/6 kills fired** (A+B) → hypothesis **PARTIALLY FALSIFIED**. The
expected mechanism (leverage converts MDD slack to CAGR) IS
empirically validated (kill F clean, +3pp CAGR per dataset, MDD
breach ≤ ceilings), but the Sharpe-drag prediction was wrong by 5×
because of the codebase Sharpe convention. The leverage axis at
futures-rate borrow on iter 058 is **not viable for WINNER**, but
**Pareto-dominates iter 056's same axis on iter 046**.

## What worked / what didn't

**Worked**:

- **Mechanics + G7 + tests**: 15/15 TDD tests pass in 0.32s. G7
  cross-lib parity 0.0000 pp on all 3 datasets (linear transform).
  Numpy reference matches pandas to 1e-12. Baseline pytest preserved
  (1024 collected, 3 pre-existing isolation failures unrelated to
  iter 060).
- **CAGR floor unlock partial (2/3 vs iter 058's 0/3)**: lever 1.5×
  successfully pushed CAGR from 8.69/9.01/9.27% (iter 058) to
  11.72/12.24/12.64% (iter 060). edu and spy clear the 0.8×bench
  floor (9.18 / 11.98%); ndx remains short of 15.35% (gap 2.71 pp).
  **The mechanism IS additive on CAGR — kill F clean.**
- **MDD breach kill clean (3/3 below ceiling)**: the iter 058 base
  has 22pp of MDD slack (vs benchmark+5pp ceilings), and 1.5× leverage
  converts ~7-8 pp of that slack into MDD with comfortable headroom
  (lev × MDD_unlev ≈ 25.11/20.57/19.68% vs ceilings 60.14/38.70/40.12%).
- **Score Pareto-dominates iter 056** (74 → 79, +5): same leverage
  axis on a higher-Sharpe base (iter 058 vs iter 046) at lower borrow
  (2.5% vs 3.5%) is empirically better, even though both fail to
  reach WINNER. Confirms the futures-borrow direction was structurally
  productive vs retail-margin direction.
- **Sub-window robustness 9/9 positive** at +1.5× scaled returns:
  iter 058's robustness inheritance is preserved post-leverage.
- **Markowitz-style closed-form math holds** for the linear transform
  (G7 = 0.0000pp, no per-bar drift between pandas and numpy
  implementations).

**Didn't**:

- **Sharpe drag formula wrong by 5.2×** (predicted 0.022, observed
  0.117). The analytical formula ``drag = (lev−1)×(b−rf)/(lev×σ_annual)``
  assumes the Sharpe metric is excess-return-based (mean−rf in
  numerator). The project's `ai_trade.backtest.metrics.performance.sharpe`
  uses ``risk_free=0.0`` default, treating raw mean as the numerator.
  **Empirical formula at this codebase**:
  ``drag = (lev−1)/lev × annualized_borrow / σ_annual``
  ≈ ``0.333 × 0.025 / 0.0703 = 0.118`` (matches observed 0.117 on edu).
  Same calculation on spy (σ=0.0656): 0.333 × 0.025 / 0.0656 = 0.127
  (matches observed 0.125). On ndx (σ=0.0651): 0.333 × 0.025 / 0.0651 =
  0.128 (matches observed 0.126).
- **DSR collapse on all 3 datasets**: with the corrected drag
  formula, even at b=rf=2.0% the drag would be ``0.333 × 0.020 /
  0.0703 = 0.094`` (edu) — pushing DSR worst-p from 0.0494 to ~0.10
  even at risk-free borrow. **The futures-leverage path is
  structurally non-viable on iter 058 at any positive borrow rate**,
  given the project's Sharpe convention.
- **ndx CAGR floor still failing**: 12.64% < 15.35%. To clear, would
  need lev ≈ 1.86× (Δ ndx CAGR ≈ +1.7 pp), but that adds another
  +0.04 to Sharpe drag, pushing DSR worst-p past 0.20 and dropping
  c3 from 5 to 0 pts (net Δ −5).
- **Score 79 < iter 058's 85**: the saved-stream-pair Pareto ceiling
  is **not broken** — leverage at this rate is a Pareto-dominated
  point relative to iter 058 unlevered.

## Main lesson (for future iterations)

**Pure external leverage on iter 058 at futures-implied financing
(2.5%) is non-viable for WINNER because of the project's Sharpe
convention.** The codebase's `_sharpe()` helper does not subtract rf
from the numerator, so the FULL annualized borrow rate becomes Sharpe
drag (not just the spread above rf). Empirically:

```
Sharpe_drag ≈ (lev − 1) / lev × annualized_borrow / σ_annual
            = 0.333 × 0.025 / 0.0703   (edu) = 0.118
            = 0.333 × 0.025 / 0.0656   (spy) = 0.127
            = 0.333 × 0.025 / 0.0651   (ndx) = 0.128
```

This 0.12-0.13 Sharpe drag is sufficient to push iter 058's DSR
worst-p from 0.0494 to 0.125 — past the 0.10 secondary cutoff for
criterion 3 (5 pts vs 15 pts unlevered). Even at b=rf=2.0% (risk-free
borrow, theoretically infeasible), drag would still be ~0.09 → DSR p
~0.085 → c3 = 10 pts — not enough to recover iter 058's 85.

**This closes the external-leverage axis on iter 058 at any positive
borrow rate ≥ 0.5pp above rf.** The lesson generalizes:

- **External-leverage axis closure** applies to ANY iter-058-derived
  combined stream at any borrow ≥ 0.5pp, regardless of whether the
  borrow source is retail margin (iter 056), futures-implied (this
  iter), or box spreads.
- **The codebase's Sharpe convention turns absolute borrow rate
  (not spread) into drag**: this is a project-level convention to
  preserve, since rebench-conventions across `_sharpe()`, DSR
  formulas, and gate evaluations are all consistent at `rf=0`.

The path to WINNER (90+) requires breaking the **CAGR-DSR dual
constraint** with a structurally different mechanism:

1. **A new base anchor with simultaneously Sharpe ≥ 1.20 AND CAGR ≥
   12% on real data**, before any leverage step. None of iters 0-58
   delivers this combination (iter 037 has CAGR ≥ 12% but Sharpe ~1.0;
   iter 046/058 has Sharpe ≥ 1.20 but CAGR ~9%).
2. **Internal leverage embedded at the asset level** (e.g., UPRO/TQQQ
   instead of SPY/QQQ in iter 041's calm regime), which is implicitly
   financed at the LETF's internal swap-funding rate (~T-bill + 0.95%
   for UPRO 2024-25 per ProShares prospectus). LETF financing is
   higher than futures-implied but is BAKED into the LETF's NAV path,
   so the project Sharpe convention measures it differently than
   external borrow. This is the iter 015/035 family's mechanism.
3. **Regime-conditional scaling** — apply leverage only in calm
   regime, deleverage in stress (iter 048 closed binary VIX-output
   gate at score 83, so a continuous z-score regime gate is dead-letter;
   but a TERM-spread gate or HMM-2 regime classifier was
   pre-disqualified by iter 019 and iter 044 closures, leaving few
   options).

The likely **viable directions for iter 061+** narrow to:

1. **Equity-overweight iter 037 + HYG_TSM** (BASE_MEMORY direction
   #2, untested). Predicted 82-87. Probably the highest-leverage
   path remaining within the saved-stream library.
2. **Internal-LETF base** (UPRO substituting SPY in iter 041's calm
   regime, financed via LETF NAV path). Untested — different from
   iter 056's external borrow because the funding cost is realized
   inside the LETF NAV (not subtracted as a borrow line item).
3. **Plano C sleeve eval** (predicted ≤ 70 per BASE_MEMORY). Floor
   direction.

## Structural dead-ends discovered

- **iter 060 (🥇 STRONG 79, 2/6 KILLS A+B fired) — iter 058 + 1.5×
  external leverage at 2.5% borrow**: the futures-implied financing
  rate (NTSX-style) does NOT break iter 056's closure pattern when
  applied to iter 058 instead of iter 046. **The project's Sharpe
  convention turns absolute borrow rate into drag, not just the
  spread above rf** — meaning external leverage on any iter-058-
  derived stream at any positive borrow rate ≥ 0.5pp above rf adds
  ≥ 0.10 Sharpe drag, pushing DSR worst-p ≥ 0.10. **Closes** the
  external-leverage axis on iter 058. Add to DEAD_ENDS.md.

- **CAGR-DSR dual constraint refined** (iter 060 confirms iter 059's
  finding): at n_trials=4330 and σ_annual ≈ 5.5-7%, the project's
  Sharpe convention combined with empirical leverage drag forces a
  trade-off: leverage adds CAGR (validated, kill F clean) but
  proportionally degrades Sharpe (validated, drag ~0.12 per 1.5×
  lev). The CAGR floor 3/3 pass is achievable at lev ≥ 1.86×, but
  DSR worst-p > 0.20 at that drag — c3 collapses to 0 pts.

## Citations used

- `[leverage_for_the_long_run, ch.5]` — Hsiao & Williams 2017
  *J. Index Investing*. NTSX architecture; futures-implied financing
  achieves leverage at T-bill + 30-50bps. **Hypothesis cited but
  empirically not the binding constraint** (the binding constraint
  was the codebase Sharpe convention, not the borrow rate).
- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen 2012 risk-parity
  stack (iter 041 base architecture, preserved verbatim via iter 046,
  preserved verbatim via iter 058 saved stream).
- `[volatility_trading, p.218]` — Sinclair 2013 cross-asset VRP (iter
  039 base preserved through iter 058).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (4330).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (0.0000 pp
  on all 3 datasets — linear transform identity).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
  (preserved through iter 058 saved stream).
- `[systematic_trading]` (Carver) — TSM single-asset rule (HYG_TSM
  engine vendored from iter 058).
- Asvanunt, A. & Richardson, S. 2017, "The Credit Risk Premium",
  JPM 43(2), DOI 10.3905/jpm.2017.43.2.090 — credit risk premium
  thesis (iter 058 HYG component).
- **Frazzini-Pedersen (2014), JFE 111(1) 1-25,
  DOI 10.1016/j.jfineco.2013.10.005 — borrow frictions on levered
  low-vol strategies. ITER 060 RE-VINDICATES THE THESIS: the borrow
  source matters less than the absolute borrow level given the
  project's Sharpe-without-rf convention.**
- IBKR Pro Tier 1 margin schedule (public, 2025-04) — 3.5% reference
  rate (iter 056 datum, contrast).
- Markowitz (1952), JoF 7(1) 77-91 — convex combination Sharpe
  identity (preserved through iter 058 saved stream).

## Next iteration suggestions

iter 060 closes the external-leverage axis on iter 058 at futures-
implied borrow rates. Three structurally distinct directions point
at the next binding constraint (**a base anchor with simultaneously
Sharpe ≥ 1.20 AND CAGR ≥ 12% on real data**):

1. **Equity-overweight iter 037 (0.75/0.40/0.40) + HYG_TSM**
   (BASE_MEMORY direction #2, RECOMMENDED for iter 061): trades MDD
   for Sharpe on the iter 037 anchor. Iter 037 standalone CAGR
   13.86/15.50/17.77% (3/3 floor passes); equity-overweight pushes
   Sharpe potentially toward 1.10-1.20 on edu. Adding HYG_TSM at
   w=0.10 may unlock DSR p < 0.10 on edu (criterion 3 = 10 pts vs 5
   pts). Predicted: **82-87** (per BASE_MEMORY estimate). **Highest
   information yield**: single mechanism, no leverage, tests whether
   anchor-side equity overweight breaks the CAGR-DSR Pareto.

2. **Internal-LETF base** (UPRO substituting SPY in iter 041's calm
   regime, TQQQ in basket, 3× LETF financed at internal NAV): UPRO's
   internal swap funding is ~T-bill + 0.95% (ProShares 2024-25
   prospectus), but the project Sharpe convention treats LETF NAV
   path differently than external borrow because no separate
   borrow-cost line is subtracted. The iter 015/035 family used SPY
   not UPRO; this would extend it. Predicted: **75-90**, but
   structurally novel and high-variance.

3. **Plano C passive sleeve eval** (BASE_MEMORY direction #4): a
   floor-experiment on multi-factor passive ETFs (GDE/AVUV/AVDE/
   AVEM/BTGD per the existing portfolio-aposentadoria.md skeleton).
   Predicted ≤ 70 per BASE_MEMORY but lowest infrastructure cost.
   Useful as a calibration data point against the Plano-A path.

**Recommended pick for iter 061**: **direction #1 (equity-overweight
iter 037 + HYG_TSM)** because it directly tests the highest-yield
remaining unexplored direction (single mechanism, established
infrastructure, predictable bounds). Direction #2 (internal LETF) is
the deeper-backlog reach if direction #1 plateaus at 84-85; direction
#3 is the floor calibration.
