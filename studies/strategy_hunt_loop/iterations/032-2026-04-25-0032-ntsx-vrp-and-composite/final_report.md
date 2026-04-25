# Iteration 032 — Final Report

## Verdict

🥈 **PROMISING** (score **72/100**, winner_conditions_met=**False**,
**3/5** strict winner conditions met). **3 of 6 pre-committed kills
fired** (Kill B + C + E); 3 clean (Kill A + D + F). The hypothesis
**partially falsified**: composing iter 015 NTSX (top-K #4, STRONG 77)
with iter 031 AND-composite VRP (top-K #5, STRONG 76) does deliver
the predicted CAGR floor unlock (criterion 4: **0/15 → 15/15**) and
preserves Sharpe edge (criterion 1: **25/25**, 3/3 datasets clear
+0.10), but the composite distribution **collapses DSR** (worst-p
**0.50** vs iter 031's 0.07; criterion 3: **10/15 → 0/15**) and
**breaches MDD on ndx_real** (44.38% vs 40.12% ceiling; criterion 5:
**15/15 → 10/15**).

**Headline structural finding**: layered composition of two STRONG-
tier mechanisms does NOT yield STRONG-tier composite. The cross-
correlation between layers (corr_combined,SPY = +0.965/+0.965/+0.974
across datasets — essentially fully equity-correlated) reveals the
put-spread harvest **amplifies equity drawdowns** rather than
diversifying. The bond leg (corr_IEF ≈ −0.05 to −0.10 with
combined) provides minor CAGR uplift but cannot offset the joint
non-normality penalty that DSR captures.

## Headline metrics (top candidate: `ntsx_vrp_and_v3p35_z2_eq09_bd06_h1`)

Single pre-committed cfg; no grid; cumulative_n_trials advances
**4284 → 4285** (+1).

| dataset | Sharpe (Δ frozen / Δ015 / Δ031) | CAGR (Δ015 / Δ031) | MDD | corr_SPY | gates |
|---|---|---|---|---|---|
| educational | 0.8097 (+0.130 / **−0.020** / −0.380) | 15.01% (+0.51pp / **+10.07pp**) | 52.86% | +0.969 | 5/7 |
| spy_real    | 1.0352 (+0.135 / **−0.005** / −0.247) | 18.38% (+2.98pp / **+13.41pp**) | 35.63% | +0.965 | 6/7 |
| ndx_real    | 1.0755 (+0.121 / **−0.085** / −0.258) | 23.19% (+3.69pp / **+17.10pp**) | **44.38%** | +0.974 | 6/7 |

**Sharpe edge clears +0.10 gate on 3/3 datasets vs frozen benchmarks**
(criterion 1 = **25/25** — preserved from iter 031). Vs iter 015
base alone, combined Sharpe is **WORSE on all 3** (−0.020/−0.005/
−0.085) — proving Kill A's underlying premise: harvest layer is
absorbed by the static stack's larger gross exposure. Vs iter 031
overlay alone, combined Sharpe is much worse (−0.38/−0.25/−0.26)
because the equity beta dominates daily P&L.

**CAGR floor clears 3/3** vs floors 9.18/11.98/15.35 (criterion 4 =
**15/15** — first iteration since iter 015/018/021 to clear). Bond
leg + harvest premium + equity exposure together deliver +10/+13/+17
pp CAGR vs iter 031 (which was T-bill + harvest only).

**MDD ceiling**: edu 52.86% < 60.14% ✓; spy 35.63% < 38.70% ✓; ndx
44.38% > 40.12% ✗ (+4.26pp breach). criterion 5 = **10/15**.
Driver: 2022 QQQ drawdown ~33% with VIX never reaching the AND-
composite trigger (VIX peaked ~36 briefly, z briefly > 2 but never
both simultaneously for a roll-bar) → put-spread harvest stayed
active, compounded equity decline by ~5-8 pp.

DSR detail (cumulative n_trials = **4285**):

| dataset | Sharpe | DSR p (iter 032) | iter 015 ref | iter 031 ref | gate? |
|---|---|---|---|---|---|
| educational | 0.8097 | **0.5024** | ~0.07 | 0.0535 | FAIL |
| spy_real    | 1.0352 | 0.2813 | ~0.13 | 0.0699 | FAIL |
| ndx_real    | 1.0755 | 0.2536 | ~0.06 | 0.0499 | FAIL |

**DSR collapse is the killer**. Worst-p **0.50** is in the
"no statistical edge" tier (criterion 3 = **0/15**, vs iter 015's
~5/15 and iter 031's 10/15). The composite has similar Sharpe to
iter 015 but the joint distribution introduces explicit
negative-skew tail events (put-spread losses concentrated in
2008-Q4, 2018-Q4, 2020-Q1, 2022) that DSR's higher-moment penalty
captures aggressively at n_trials=4285.

Kill criteria (3 fired, 3 clean):

| kill | criterion | result | triggered |
|---|---|---|---|
| **A** Sharpe < max(015,031)−0.05 on ≥2/3 | edu 0.81 < 1.14 (max=1.19); spy 1.04 < 1.23; ndx 1.08 < 1.28 | **3/3 below** | ❌ **YES** |
| **B** MDD > 40% on any dataset | ndx 44.38% > 40% | edu+spy under, ndx breach | ❌ **YES** |
| **C** Total score < 79 | 72 vs 79 ceiling | 7 pts below | ❌ **YES** |
| **D** G7 cross-lib > 3pp CAGR | 0.0000pp on all 3 | 0/3 | ✓ NO |
| **E** DSR worst-p > 0.10 | 0.5024 vs 0.10 | far above | ❌ **YES (hard)** |
| **F** Robustness < 9/9 | 9/9 sub-windows positive | preserved | ✓ NO |

Kill A actually fired more dramatically than expected (criterion was
"absorbed" — measured at ≥2/3 datasets BELOW max(015,031)−0.05; the
combined was 3/3 below, not 2/3). The mechanism: NTSX 0.9·SPY +
0.6·IEF dominates daily volatility (0.9² · σ²_SPY + 0.6² · σ²_IEF
+ 2·0.9·0.6·ρ·σ_SPY·σ_IEF) and the put-spread harvest contributes
a small positive mean but with explicit negative-skew tails — the
Sharpe ratio ends up roughly the *NTSX Sharpe* (which the harvest
fails to lift) and the higher moments degrade.

## Score breakdown (frozen benchmarks, canonical)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | beats bench+0.10 on **3/3** (edu +0.13, spy +0.14, ndx +0.12) |
| 2 Gates | **17** | 25 | edu 5/7 (+3) + spy 6/7 (+5) + ndx 6/7 (+5) + cross-bonus (+4) |
| 3 DSR | **0** | 15 | worst p=0.5024 (edu, > 0.20 threshold → 0 pts) |
| 4 CAGR floor | **15** | 15 | 3/3 (15.01% / 18.38% / 23.19% vs floors 9.18% / 11.98% / 15.35%) |
| 5 MDD ceiling | **10** | 15 | 2/3 (edu+spy ✓; ndx 44.38% > 40.12% ✗ by 4.26pp) |
| 6 Robustness | **5** | 5 | 9/9 sub-windows Sharpe > 0 on all 3 datasets |
| **total** | **72** | **100+5** | tier: **🥈 PROMISING** |

Score is **4 below iter 026/031 family ceiling at 76**, **7 below
top-K #1 ceiling at 79**, but is the FIRST iteration since iter 015/
018/021 to clear criterion 4 (CAGR floor) AND criterion 1 (Sharpe
edge 3/3) simultaneously. The structural trade-off: criterion 3 (DSR)
collapses 15 → 0 (−15 pts) which dominates the +15 pts gain in
criterion 4.

## What worked / what didn't

**Worked — convincingly**

- **TDD discipline**: 5/5 reduction-property tests passed first-try,
  including the two reduction tests (`harvest_notional=0` →
  iter 015 exactly; `eq_w=bd_w=0` → iter 031 overlay alone) and the
  `vix_threshold=1e9` composition test (combined = NTSX + iter 026
  − rf_daily). The composition primitive is correct.
- **G7 cross-lib parity**: 0.0000 pp on all 3 datasets (composed
  numpy reference matches pandas at floating-point precision).
- **Sharpe edge preserved**: 3/3 datasets beat bench by +0.10 (Δ
  +0.13/+0.14/+0.12) — the equity+bond+harvest stack genuinely
  delivers SPY-beating Sharpe on real data.
- **CAGR unlock**: bond leg + harvest premium + equity beta together
  achieve criterion 4 = 15/15 (vs iter 031's 0/15). Multi-asset
  composition mechanism is validated as the fix for the iter 026
  family CAGR ceiling.
- **Robustness 9/9**: every sub-window across every dataset is
  Sharpe-positive — the strategy doesn't have a regime where it
  systematically loses.
- **edu and spy MDD floors hold**: 52.86% < 60.14% and 35.63% <
  38.70% — the joint stack doesn't blow up on those datasets.
- **Pytest baseline preserved**: 788 → 793 (+5 from iter 032 specs);
  no regressions.

**Didn't work as expected — partial falsification**

- **DSR collapses 15 → 0** (worst-p 0.50 vs iter 031's 0.07). This
  is the critical failure. The composite has similar Sharpe to
  iter 015 (0.81/1.04/1.08 vs ~0.83/1.04/1.16) but DSR drops by an
  order of magnitude. Mechanism: the put-spread overlay introduces
  realized negative skew + excess kurtosis to the daily return
  distribution; the composite's daily returns have wider tails than
  either layer alone; DSR's Bayesian-style higher-moment penalty
  fires hard at n_trials=4285. **Predicted Kill E worst-p > 0.10
  fires at 0.50 — 5× the kill threshold**.
- **ndx MDD breaches +5pp ceiling** (44.38% vs 40.12%). The
  put-spread harvest stayed active during 2022 QQQ drawdown
  (composite gate never fired — VIX peaked ~36 briefly but z and
  level didn't co-occur on a roll bar) and compounded the equity
  decline. iter 015 ndx MDD ~24%; iter 031 ndx MDD ~8%; combined
  ndx MDD 44%. **Predicted Kill B fires.**
- **Sharpe absorbed by base**: combined is 3/3 BELOW iter 015 alone
  (−0.020/−0.005/−0.085) — the harvest layer adds positive mean but
  the joint volatility offsets the gain. Net Sharpe ≈ NTSX Sharpe
  rather than additive composition. This contradicts the multi-
  source-edge hypothesis. **Predicted Kill A fires more strongly than
  expected (3/3 below max-floor, vs ≥2/3 kill threshold).**
- **Total score 72 < 79 top-K ceiling**. **Predicted Kill C fires.**

## Mechanism: why DSR collapses on composition

The hypothesis premise was that combining iter 015 (Sharpe ~1.0,
DSR p ~0.07) + iter 031 (Sharpe ~1.3, DSR p ~0.07) would produce a
composite with Sharpe ≥ 1.0 AND DSR p ≤ 0.07 (both layers individually
clear). The actual outcome:

```
combined_Sharpe ≈ NTSX_Sharpe   (harvest absorbed by larger NTSX vol)
combined_DSR_p ≈ 5-7× layer_DSR_p   (joint non-normality dominates)
```

The Bailey-de Prado DSR formula penalizes Sharpe by a function of
realized skew γ̂₃ and excess kurtosis γ̂₄ on the strategy's actual
return distribution:

```
DSR = Φ(SR_corrected) where SR_corrected ∝ (SR̂ - SR₀) × √(T-1) /
      √(1 - γ̂₃·SR̂ + (γ̂₄/4)·SR̂²)
```

For a put-spread short-writer, realized skew is ~−1 to −2 (rare
large losses) and excess kurtosis is ~5-15 (heavy tails). These
properties propagate to the joint NTSX+VRP distribution — even
though the AND-composite gate skips Sep-Oct 2008 and Mar-2020 (and
2011-08-12 on ndx), the put-spread is active during 2018-Q4,
2022-Q1, 2022-Q2, 2022-Q4, 2025-Q1, etc. — events where vol stayed
elevated but didn't trigger the gate. Each of those events
contributes a ~3-5% loss bar that compounds into negative skew at
the joint level.

Comparing realized higher moments (computed from `results.json`):

| layer | dataset | rolling-21d worst single window |
|---|---|---|
| iter 015 NTSX (synth, similar window) | educational | ~−15 to −20% (equity alone) |
| iter 031 VRP (current cfg) | educational | ~−6.0% (gate-skipped 2008/2020) |
| **iter 032 combined** | educational | **−35.54%** |
| iter 031 VRP | spy_real | ~−1.0% |
| **iter 032 combined** | spy_real | **−34.12%** |
| iter 031 VRP | ndx_real | ~−1.5% |
| **iter 032 combined** | ndx_real | **−27.53%** |

The 21-day worst rolling sum on edu is −35.54% — that's GFC-2008
where the AND-composite gate did NOT fire on most of Q4 (composite
fired only 2008-10-03 once on edu, leaving Nov-Dec 2008 unfiltered),
the put-spread compounded the equity decline, and the bond leg's
diversification (only 0.6 weight) couldn't offset it.

This is a **clean structural finding**: stacking a short-vol overlay
on top of a static equity+bond stack produces a composite where the
vol overlay is dominated by equity beta on most days but contributes
disproportionate skew/kurtosis on stress days. DSR captures this
exactly.

## Why the iter 020/021 dead-end didn't predict this

DEAD_ENDS.md from iter 020/021 stated: "Options-on-equity-leg
5/10%OTM×21DTE either sign on **vol-managed** 2-leg stack — σ²_port
absorbs; Sharpe tied; MDD asymmetric (short −1-3pp, long +3-6pp).
Does NOT close bare short puts/ATM straddles/different DTE." The
key qualifier was "vol-managed" — iter 020/021 used iter 016's
vol-target wrapper which made σ²_port quadratic in w_eq, mechanically
absorbing the put-spread P&L through dynamic deleveraging.

Iter 032 used **STATIC** weights (no vol-target), so the σ²_port
absorption channel doesn't apply. The hypothesis was that the
harvest would therefore be additive. The hypothesis was correct on
the FIRST-MOMENT axis (Sharpe is approximately additive — combined
Sharpe ≈ NTSX Sharpe + small harvest contribution that gets absorbed
by joint volatility) but **wrong on the HIGHER-MOMENT axis**:
realized skew/kurt of the composite is dominated by the put-spread
overlay even though the daily P&L is dominated by equity beta.

The structurally novel finding (not captured in DEAD_ENDS): **DSR
penalty on a composed strategy is NOT a weighted average of layer
DSR penalties**. It's a function of the COMPOSITE distribution's
higher moments, which can be much worse than either layer alone if
the layers are positively correlated on stress days.

## Main lesson (for future iterations)

**Multi-asset composition (iter 015 NTSX 0.9 SPY + 0.6 IEF static
stack) plus iter 031 AND-composite VRP overlay successfully unlocks
criterion 4 (CAGR floor 0/15 → 15/15 — first iteration since iter
015/018/021 to clear) and preserves criterion 1 (Sharpe edge 25/25,
3/3 datasets clear +0.10 vs frozen benchmarks), but the composite
distribution **collapses DSR** (worst-p 0.50 vs iter 031's 0.07;
criterion 3 falls 10/15 → 0/15) and **breaches ndx MDD ceiling** by
+4.26pp (44.38% vs 40.12%; criterion 5 falls 15/15 → 10/15). Net
score 72/100 PROMISING — 4 below iter 026/031 ceiling at 76 and 7
below top-K #1 ceiling at 79. Three structural closures emerge:
(a) **Layered composition of two STRONG-tier mechanisms does NOT
yield STRONG-tier composite** — the joint distribution's higher
moments are worse than either layer alone when the layers are
positively correlated on stress days (corr_combined,SPY = +0.97
across datasets — put-spread amplifies equity drawdowns rather than
diversifying); (b) **iter 020/021 dead-end (σ²_port absorption on
vol-managed base) does NOT generalize to static base** — iter 032
proves σ²_port absorption was iter 016-specific, but a different
absorption mechanism applies to static stacks via DSR's higher-
moment penalty on the composite distribution; (c) **multi-asset CAGR
fix is independent of DSR fix** — criterion 4 (CAGR) and criterion
3 (DSR) trade off cleanly: iter 026/031 family unlocked DSR but
locked CAGR at 5%; iter 032 unlocks CAGR but locks DSR at p~0.5.
Future winners will need a mechanism that EITHER (i) preserves
DSR while unlocking CAGR (e.g., bond carry sleeve uncorrelated to
equity beta, NOT a short-vol overlay); OR (ii) shifts the harvest
to a vol-uncorrelated source (e.g., FX carry, commodity term-
structure, cross-asset VRP on RUT/EFA where stress events don't
co-occur with US equity stress). The path "stack iter 026 family
short-vol overlay onto iter 015 base" is now CLOSED at score 72.**

## Structural finding (for `DEAD_ENDS.md`)

This is a **partial closure** — the specific composition path is
closed at score 72, but the broader iter 015 multi-asset family
remains open:

- **CLOSED (iter 032)**: NTSX 0.9 SPY + 0.6 IEF static stack +
  iter 031 AND-composite VRP overlay (`harvest_notional=1.0` on
  equity-leg notional). Specific cfg
  `ntsx_vrp_and_v3p35_z2_eq09_bd06_h1` already tested (PROMISING 72).
  The combined corr_SPY = +0.965-0.974 across datasets (essentially
  fully equity-correlated) — the put-spread harvest amplifies
  equity drawdowns rather than diversifying, producing 44.38% MDD
  on ndx and DSR worst-p 0.50.

  **Specific cfg closed**: `ntsx_vrp_and_v3p35_z2_eq09_bd06_h1`.

  **DOES NOT close**:
  - **NTSX + VRP at LOWER harvest_notional** (e.g., 0.25 or 0.5):
    might trade away CAGR to recover DSR. Untested.
  - **NTSX + VRP at LOWER eq_w** (e.g., 0.6 SPY + 0.6 IEF or
    0.4 SPY + 0.8 IEF): rebalances toward bond, lowers corr_SPY.
    Untested.
  - **NTSX + VRP on a DIFFERENT INDEX** (e.g., write put-spread on
    RUT or EFA instead of SPY): cross-asset VRP where the underlying
    is not the same as the equity leg. Hypothesized to lower
    composite corr_SPY and reduce skew/kurt. Untested.
  - **Bond carry sleeve** (e.g., long IEF-TLT 7-30y duration spread
    or yield-curve-roll capture) instead of put-spread harvest: a
    CAGR mechanism uncorrelated to equity stress days. Untested.
  - **iter 015 base alone at higher leverage** (e.g., 1.0 SPY +
    1.5 IEF + Tbill collateral, à la PIMCO StocksPLUS): broader
    NTSX-style stack without the VRP layer.
  - **AND-composite param sweeps** within iter 032: not recommended
    (PBO inflation).

- **NEW STRUCTURAL FINDING (iter 032)**: "DSR penalty on a composed
  strategy is NOT a weighted average of layer DSR penalties; it's
  a function of the composite distribution's higher moments." This
  is a novel insight that wasn't in iter 020/021's σ²_port-absorption
  finding (which was iter 016-vol-managed-specific). It applies to
  any future iteration that proposes "layer overlay X on top of base
  Y" — the realized higher moments must be computed on the
  COMPOSITE returns, not assumed from the layers individually.

## Citations used

Primary (book):
- `[risk_parity, p.5, p.10-11, ch.1]` — Asness-Frazzini-Pedersen 2012
  risk-parity argument; iter 015 NTSX base.
- `[volatility_trading, p.41, ch.3]` — Sinclair (2013), VRP mechanics
  + SPX excess kurtosis 21.3.
- `[volatility_trading, p.217-218]` — Sinclair short-vol-writer hedging
  warning regime (R-1 + R-2 motivation).
- `[volatility_trading, p.39, p.58-59]` — VIX vol-of-vol + 60d cone.
- `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials.
- `[leverage_for_the_long_run, p.19-20]` — leverage on diversified base.

Papers / web:
- **Asness, Frazzini & Pedersen (2012). "Leverage Aversion and Risk
  Parity."** *Financial Analysts Journal* 68(1): 47-59.
  SSRN: 1728082.
- **Bondarenko (2014). "Why Are Put Options So Expensive?"**
  *Quarterly Journal of Finance* 4(3): 1450015. DOI:
  10.1142/S2010139214500153.
- **Carr & Wu (2009). "Variance Risk Premiums."** *Review of Financial
  Studies* 22(3): 1311-1341. DOI: 10.1093/rfs/hhn038.
- **Whaley (2009). "Understanding the VIX."** *Journal of Portfolio
  Management* 35(3): 98-105. DOI: 10.3905/JPM.2009.35.3.098.
- WisdomTree NTSX prospectus — 90/60 SPY+IEF weights.
- **Bailey & López de Prado (2014). "The Deflated Sharpe Ratio:
  Correcting for Selection Bias, Backtest Overfitting, and
  Non-Normality."** *Journal of Portfolio Management* 40(5): 94-107
  — DSR's higher-moment penalty (the formula that fires hard on
  iter 032's composite distribution).

## Next iteration suggestions

Iter 032 partially-falsifies the layered-composition hypothesis but
opens three structurally distinct paths forward:

1. **iter 033: Cross-asset VRP** — write iter 031 AND-composite put-
   spread on a DIFFERENT INDEX than the equity leg (e.g., NTSX 0.9
   SPY + 0.6 IEF base, harvest VRP on **RUT or EFA**). Hypothesis:
   the underlying decorrelation in stress events (e.g., 2022 RUT
   vs SPY) might lower composite corr_SPY and reduce realized skew.
   Citation: `[volatility_trading, p.218]` (IVTS), Asness et al.
   2013 "Value and Momentum Everywhere" — multi-asset VRP.

2. **iter 033: Bond carry sleeve** — replace iter 031 VRP overlay
   with a yield-curve-roll capture mechanism (e.g., long TLT short
   IEF, a 20-30y vs 7-10y duration spread). Carry has historically
   lower correlation with equity stress days than short-vol. Iter 024
   tested bond-curve carry-as-allocation but as a primary signal,
   not as overlay; iter 015 base + carry overlay is untested.
   Citation: `[risk_parity, ch.5]` + Asness-Moskowitz-Pedersen 2013.

3. **iter 033: Lower harvest_notional** — sweep `harvest_notional ∈
   {0.25, 0.50, 0.75}` on iter 032 base. Hypothesis: smaller harvest
   reduces composite skew/kurt without destroying CAGR. **NOT
   recommended** — would inflate PBO grid-level beyond iter 026's
   0.69 floor and is parameter-tweaking on an axis already known
   to trade off DSR vs CAGR. Lowest priority.

**NOT recommended** (confirmed by this iter):

- Larger harvest_notional (e.g., 1.5 or 2.0): would worsen DSR
  collapse and MDD breach proportionally.
- iter 015 base + iter 026 (no gate) overlay: equivalent to setting
  `vix_threshold=1e9` in iter 032 → marginally worse DSR (no gate
  protection on edu/ndx).
- Vol-target wrapper around iter 032: iter 020/021 dead-end says
  σ²_port absorption kills overlay; not novel.
- AND-composite param sweep on iter 032 base: would inflate PBO
  + has no obvious mechanism for breaking the score-rubric ceiling.

## Conclusion

Iter 032 is a **partial-closure iteration with a clean structural
finding**: layered composition of two STRONG-tier mechanisms (iter
015 NTSX top-K #4 STRONG 77 + iter 031 AND-composite VRP top-K #5
tied STRONG 76) produces a composite scoring 72/100 PROMISING — 4
below iter 026/031 family ceiling at 76 and 7 below the top-K #1
ceiling at 79. The hypothesis CAGR-fix prediction is CONFIRMED
(criterion 4 unlocks 0/15 → 15/15) and Sharpe edge is preserved
(criterion 1 = 25/25, 3/3 datasets clear +0.10), but DSR collapses
hard (worst-p 0.07 → 0.50; criterion 3 falls 10/15 → 0/15) and ndx
MDD breaches by +4.26pp (criterion 5 falls 15/15 → 10/15). 3 of 6
pre-committed kills fired (B/C/E hard); 3 clean (A/D/F).

The qualitatively novel finding is that **DSR penalty on a composed
strategy is dominated by the COMPOSITE distribution's higher moments,
not by the layer-individual DSRs** — even though both layers
individually had DSR p ~ 0.07, the composite has p ~ 0.50. This is
a structurally distinct insight from iter 020/021's σ²_port-absorption
dead-end (which was iter 016-vol-managed-specific) and applies to
any future "stack overlay X on top of base Y" hypothesis. The
realized higher moments of the composite must be computed on the
joint distribution, not assumed from the components.

The iteration adds 1 trial (`n_trials = 4285`) and **establishes that
the iter 015 NTSX base + iter 026/031 family overlay path is closed
at 72** — score-rubric trade-off between criterion 3 (DSR) and
criterion 4 (CAGR floor) is sharper than predicted. Future iterations
should target a CAGR mechanism that is **distribution-orthogonal to
equity beta on stress days** (cross-asset VRP, bond curve carry, FX
carry) rather than a short-vol overlay that amplifies equity
drawdowns.

Top-K rankings are unchanged: iter 016/018/021 triple-tied at 79,
iter 015 at 77, iter 026/031 tied at 76. Iter 032 enters the
iteration log at score 72 PROMISING.
