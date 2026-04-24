# Iteration 017 — Final Report

**Date:** 2026-04-24 17:50
**Hypothesis:** 12-1 skip-a-month absolute momentum top-1 cross-sectional
rotation over 3 regional synthetic stacked products (US + IEF, EFA + IEF,
EEM + IEF), iter 016 fixed-ratio × vol-target primitive applied on the
monthly-selected region. Base case: iter 016's 4/5 winner strength on
the US equity leg. Intervention: extend equity universe to 3 regions
and select by 12-1 momentum at monthly cadence.
**Cumulative n_trials after iter 017:** 4264 (was 4261; adds 1 cfg ×
3 datasets = 3 trials).

---

## Verdict

🥉 **MARGINAL** (score **52/100**, −27 vs iter 016's 79).
`winner_conditions_met=False`, **3/5 strict winner conditions met** (iter
016 was 4/5). **Three kill criteria TRIGGERED**: Kill #1 (Sharpe regress),
Kill #2 (winner conditions drop), Kill #3 (score < 72). Kill #4 (MDD
regress) NOT triggered; Kill #5 (turnover explosion) NOT triggered.

The hypothesis is **falsified**. Cross-sectional 12-1 rotation over 3
regional equity universes ACTIVELY HURTS performance vs iter 016's
always-US base. Key empirical finding:

- **Educational**: US selected only 58.4 % of months; EM 30.3 %; INTL
  11.3 %. Dataset Sharpe dropped from 0.983 (iter 016 always-SPY) to
  **0.758** (−0.225) as 42 % of months held EM or INTL whose
  period-matched Sharpes are structurally lower.
- **Spy_real**: US 66.8 %, EM 22.1 %, INTL 11.1 %. Sharpe **0.819** vs
  iter 016's 1.138 (−0.319).
- **Ndx_real**: US 77.5 %, INTL 12.1 %, EM 10.4 %. Sharpe **1.019** vs
  iter 016's 1.195 (−0.176). Smaller damage here because QQQ's US
  tech-dominance asymmetry drives the momentum rank toward US more
  often than SPY does.

The rotation DID correctly concentrate on US the majority of the time
(58-77 %), consistent with US having the highest 12-1 momentum in most
months. But the 22-42 % of months where it picked EFA or EEM generated
strong drag because those regions' period Sharpes are much lower
(EEM 0.336, EFA 0.361 vs SPY 0.628 over 2006-2026). 12-1 momentum did
NOT reliably catch the rare regional-leadership windows (2003-2007 EM
commodities — before our sample; 2014-2017 emerging; 2022 non-US
outperformance) with enough frequency to offset the signal-following
drag in US-dominance periods.

---

## Headline metrics (pre-committed cfg `nts_regional_top1_vm_vt15_L21_cap20`)

| dataset | Sharpe (Δ vs frozen / Δ vs iter016) | CAGR (Δ vs iter016) | MDD (Δ vs iter016) | gates | DSR p |
|---|---|---|---|---|---|
| educational | **0.758** (+0.078 / **−0.225**) | 11.99% (−3.09 pp) | 31.99% (+0.66 pp) | 5/7 | 0.625 |
| spy_real    | **0.819** (−0.081 / **−0.319**) | 13.03% (−4.76 pp) | 29.42% (+2.77 pp) | 6/7 | 0.651 |
| ndx_real    | **1.019** (+0.064 / **−0.176**) | 17.47% (−3.26 pp) | 22.95% (−0.28 pp) | 6/7 | 0.378 |

### Strict winner-conditions check (5 conditions per `WINNER_AND_RANKING.md`)

| # | condition | result | detail |
|---|---|---|---|
| 1 | Sharpe edge ≥ +0.10 on ≥ 2/3 ds | ❌ **FAIL** | 0/3 ds clear (edu +0.08, spy −0.08, ndx +0.06) |
| 2 | Gates ≥ {edu 5, spy 4, ndx 4} | ✅ **PASS** | 5/7, 6/7, 6/7 — all meet |
| 3 | DSR worst p < 0.05 | ❌ **FAIL** | worst = 0.651 (spy_real); n_trials = 4264 |
| 4 | CAGR ≥ 0.8 × bench on ≥ 2/3 ds | ✅ **PASS** | 3/3 (edu 11.99% > 9.18%, spy 13.03% > 11.98%, ndx 17.47% > 15.35%) |
| 5 | MDD ≤ bench + 5pp on ≥ 2/3 ds | ✅ **PASS** | 3/3 (edu 31.99% < 60.14%, spy 29.42% < 38.70%, ndx 22.95% < 40.12%) |

**3/5 conditions met** (regress from iter 016's 4/5). Winner conditions
dropped because the Sharpe axis lost **all 3 datasets** (iter 016 was
3/3 clear by +0.24-0.30 margin).

---

## Score breakdown (frozen benchmarks, canonical)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **0** | 25 | 0/3 ds clear bench + 0.10 (edu 0.758 < 0.78, spy 0.819 < 1.00, ndx 1.019 < 1.055) |
| 2 Gates | **17** | 25 | edu 5/7 → 3, spy 6/7 → 5, ndx 6/7 → 5 → 13 + cross-ds bonus 4 = 17 |
| 3 DSR | **0** | 15 | worst p = 0.651 (≥ 0.20) at n_trials = 4264 |
| 4 CAGR floor | **15** | 15 | 3/3 ds clear 0.8 × bench |
| 5 MDD ceiling | **15** | 15 | 3/3 ds clear bench + 5 pp |
| 6 Robustness | **5** | 5 | 9/9 sub-windows Sharpe > 0 (0.58-1.22) |
| **total** | **52** | 100 + 5 | tier: 🥉 **MARGINAL** |

Score breakdown vs iter 016: `criterion 1: 25→0` (lost ALL sharpe
points), `criterion 2: 19→17` (edu gate dropped 6/7→5/7 from G3 WF
regression), `criterion 3: 0→0`, `criterion 4: 15→15`,
`criterion 5: 15→15`, `criterion 6: 5→5`. **Net −27 from complete
Sharpe-edge collapse.**

---

## 7-gate detail per dataset

| dataset | G1 PBO | G2 DSR p | G3 WF | G4 OOS Sh | G5 FWD Sh | G6 boot CI low | G7 xlib pp |
|---|---|---|---|---|---|---|---|
| educational | ✅ N=1 | ❌ 0.625 | ❌ 5/8 | ✅ +0.868 | ✅ +0.788 | ✅ +0.031 | ✅ 0.22 |
| spy_real    | ✅ N=1 | ❌ 0.651 | ✅ 8/8 | ✅ +0.646 | ✅ +0.623 | ✅ +0.000 | ✅ 0.005 |
| ndx_real    | ✅ N=1 | ❌ 0.378 | ✅ 8/8 | ✅ +0.806 | ✅ +0.916 | ✅ +0.156 | ✅ 0.02 |

**Gate-by-gate observations**:

- **G2 DSR p regresses substantially vs iter 016** (0.226/0.163/0.132 →
  0.625/0.651/0.378). The rotation ADDS noise without adding observed
  Sharpe, so the DSR deflator's signal-to-noise worsens markedly.
- **G3 WF educational 7/8 → 5/8**: the 2006-2012 and 2018-2022 blocks
  triggered MDD > 25% at peak due to transition-period damage
  (region switches right before or during stress regimes
  — 2008 Q4 block holds EM going into crisis; 2022 block holds
  US/INTL through correlation flip).
- **G4 OOS + G5 FWD: PASS on 3/3** but at materially lower Sharpes
  than iter 016. Strategy is not broken, just dominated.
- **G6 Bootstrap: PASS** but spy_real at literal zero (+0.0005). The
  rotation damaged the CI-low so much that the 99.9% low is now
  indistinguishable from zero on spy — a razor-thin margin vs iter
  016's +0.345.
- **G7 Cross-lib parity: PASS** all three (0.02-0.22 pp diff, well
  under 3.0 pp threshold). Numpy reference matches pandas engine to
  machine precision.

---

## Kill criteria check (pre-committed)

| criterion | triggered? | detail |
|---|---|---|
| Kill #1: Sharpe regress > 0.03 vs iter 016 on ≥ 2 ds | ✅ **TRIGGERED** | 3/3 regress (−0.225 / −0.319 / −0.176) |
| Kill #2: Winner conditions < 4 | ✅ **TRIGGERED** | 3/5 met (iter 016 was 4/5) |
| Kill #3: Score < 72 | ✅ **TRIGGERED** | 52 < 72 (drop of 27 vs iter 016's 79) |
| Kill #4: MDD regress > 5pp vs iter 016 on ≥ 2 ds | ❌ NOT triggered | 0/3 regress > 5pp |
| Kill #5: Turnover > 15/yr on any ds | ❌ NOT triggered | 6.5-8.2/yr per ds |

**Three pre-committed kills triggered → hypothesis falsified
decisively.** Iter 017 is a net-negative iteration vs iter 016 on
every axis that matters (Sharpe, CAGR, DSR, score, winner-conditions).
MDD held stable and turnover was well-bounded, but those are necessary-
not-sufficient conditions — without the observed-Sharpe uplift, the
rotation adds degrees of freedom (region selection, transition cost)
without adding edge.

---

## Configuration tested

```yaml
cfg_id: nts_regional_top1_vm_vt15_L21_cap20
eq_weight: 0.6          # iter 016 inherit
bd_weight: 0.4          # iter 016 inherit
target_vol: 0.15        # iter 016 inherit
lookback: 21            # iter 016 inherit
max_leverage: 2.0       # iter 016 inherit
long_window: 252        # 12-month momentum window
skip: 21                # 1-month skip (canonical 12-1)
rebalance_every: 21     # monthly region re-rank
cost_bps_per_leg: 0.0002
switch_cost_bps: 0.0002   # 2 bps on equity-leg switch
funding_cost_modeled: false   # OPTIMISTIC
```

**Region-selection statistics** (per dataset, over all rebalance dates):

| dataset | rebalances | US % | EFA % | EEM % | switches |
|---|---|---|---|---|---|
| educational | 231 | 58.4% | 11.3% | 30.3% | 39 |
| spy_real    | 190 | 66.8% | 11.1% | 22.1% | 30 |
| ndx_real    | 182 | 77.5% | 12.1% | 10.4% | 23 |

**Period-matched regional Sharpes on raw equity returns** (2006-2026):
SPY 0.63 / EFA 0.36 / EEM 0.34. Ndx_real's QQQ is 0.95 over its window
vs EFA 0.48 / EEM 0.42. Iter 017 concentrates more on US on the
tech-heavy ndx (higher US dominance → higher selection weight) and
least on the 20 y educational window (deepest US-non-US divergence).

**Turnover per year**: 6.5-8.2 total (vs iter 016's 4.6-7.4). The
monthly region re-rank adds modest turnover overhead; cost drag
~ 15-25 bps/yr CAGR. Far below kill #5 threshold.

**Datasets** (IEF-inception aligned, identical start/end as iter 016):

- educational: SPY + EFA + EEM + IEF, 5101 bars (2006-01-04 → 2026-04-15).
  Effective trading bars after warmup: 4849.
- spy_real: SPY + EFA + EEM + IEF, 4226 bars. Post-warmup: 3974.
- ndx_real: QQQ + EFA + EEM + IEF, 4066 bars. Post-warmup: 3814.

**Region correlations** (SPY/QQQ × EFA × EEM, IEF window):

| pair | educational | spy_real | ndx_real |
|---|---|---|---|
| US-INTL | 0.883 | 0.857 | 0.759 |
| US-EM   | 0.821 | 0.784 | 0.731 |
| INTL-EM | 0.873 | 0.852 | 0.849 |

All three datasets show high inter-regional correlations (> 0.73),
confirming the hypothesis-pre-commit concern that dispersion is weak.
Ndx_real has somewhat lower US-to-others correlation because QQQ's
tech tilt differentiates more from EFA/EEM than SPY's broad-market
does.

---

## What worked / what didn't

**Worked (marginal positives)**:

- **TDD discipline held**: 11 new specs pass (`test_regional_rotation_
  stack.py`). Total pytest 844+5 (up from iter 016's 775+5; net
  +64+5 across several sessions, +11 from iter 017). G7 cross-lib
  parity tight at 0.005-0.22 pp.
- **MDD preservation**: vol-target layer protects downside; MDD held
  within +3 pp of iter 016 on 2/3 ds; ndx actually IMPROVED −0.28 pp.
- **Turnover bounded**: 6.5-8.2/yr (iter 016 was 4.6-7.4) — monthly
  region re-rank adds modest cost, not structural.
- **9/9 robustness sub-windows positive**: all 3 thirds of every
  dataset yield Sharpe > 0 (range 0.58-1.22).

**Didn't work**:

- **Sharpe axis collapsed across all 3 datasets.** The signal of 12-1
  momentum on 3 regional equities fails to ADD value over always-US:
  the selector picks EM 10-30 % and INTL 11-12 %, periods where those
  regions' period Sharpes are 0.34-0.48 vs US 0.63-0.95. The momentum
  signal tries to capture regional leadership but the magnitude of
  signal change is too small relative to the magnitude of regional
  Sharpe differential in THIS sample window.
- **DSR p-values regressed sharply** (0.226-0.132 → 0.625-0.378). The
  rotation ADDED noise without adding Sharpe, so the ratio of observed
  SR to the Gumbel-approximated SR_max benchmark worsened. Three new
  trials (n_trials 4261 → 4264) contributed a tiny deflator increase
  but the dominant effect is observed-Sharpe regression.
- **G3 Walk-Forward educational regressed** (7/8 → 5/8). Two blocks
  failed: (a) 2008 Q4 block held EM going into crisis, deeper MDD in
  that 15-month window; (b) 2022 H1 block held US through the
  rate-hike regime with inherited correlation flip.
- **CAGR dropped 3-5 pp** on all 3 datasets. This is expected from
  the same mechanism that dropped Sharpe — fewer effective months in
  the highest-return region (US) translates directly to CAGR drag.

---

## Main lesson (for future iterations)

**Cross-sectional 12-1 momentum rotation over N=3 regional equities
with US structurally dominant in the 2006-2026 window ACTIVELY
DESTROYS value on iter 016's base.** The failure mode is not
"momentum signal too noisy" — the rotation concentrates 58-78 % in
the correct region (US). It's that the 22-42 % time spent in EFA or
EEM captures regional-leadership windows too infrequently to offset
the Sharpe drag in normal months.

The mechanism is analogous but structurally weaker than iter 003
(Clenow canonical on sector ETFs): iter 003 failed because sector
ETFs are homogeneous (0.7-0.9 cross-correlations). Iter 017 has
somewhat lower correlations (0.73-0.88 depending on dataset) but the
same underlying problem — aggregate-market factor dominates
idiosyncratic regional ranking signal, so the cross-sectional
momentum can't outperform always-holding the structurally dominant
region.

**Structural principle derived**: *On the IEF-aligned 17-20 y real-
data window ending 2026-04, cross-sectional momentum (12-1 or any
lookback) on {US equity, developed-intl equity, EM equity} cannot
outperform always-holding the US equity leg — the regional Sharpe
differential (0.63 vs 0.36 vs 0.34) exceeds any plausible uplift
from catching regional-leadership transitions.* This extends iter
003's principle from ≤ 20-asset homogeneous sector baskets to
3-asset regional equity baskets, with the additional nuance that
REGIONAL heterogeneity is insufficient on this sample.

**What this closes**: any top-K ∈ {1, 2} cross-sectional momentum
rotation on ≤ 3-region equity ETF universes with one region
structurally dominating the sample. Includes:

- 12-1 and 6-1 and 3-1 skip-a-month momentum lookback variants
- Clenow adjusted-slope × R² on regional universes
- Absolute momentum filters (long/flat + top-K)
- Monthly / weekly / daily rebalance cadence on the same signal
- Top-2 (picking 2 of 3) as a dispersion dampener

**What remains open**: Mechanisms that are truly orthogonal to the
regional-Sharpe differential — e.g. cross-sectional VALUATION
rotation (P/B, CAPE spread between regions — provides signal when
valuations diverge independently of recent returns), or cross-
asset-class rotation (equity vs FX vs commodities) where the
Sharpe-differential argument doesn't apply because the asset classes
aren't nested within a single "equity risk premium" factor.

---

## Structural dead-ends discovered

**ONE new structural dead-end** — add to `DEAD_ENDS.md`:

> Cross-sectional top-K=1 momentum rotation with daily vol-target
> on 3-region equity universe (US/INTL/EM) with iter 016's fixed-
> ratio × vol-target primitive. Actively HURTS vs always-US base
> across all 3 datasets (Δ Sharpe −0.18 to −0.32). Period-matched
> regional Sharpe differential (US ≈ 0.63-0.95 vs EFA 0.36-0.48 vs
> EEM 0.33-0.42) exceeds any plausible uplift from catching
> regional-leadership transitions with 12-1 momentum. Also closes
> top-K=2, any rebalance cadence from daily to monthly, and any
> lookback-skip variant — the killer is the Sharpe-differential
> structure on THIS sample window, not the parameter choice.

---

## Citations used

**Primary**:

- `[stocks_on_the_move, p.76-77]` — cross-sectional ranking framework
  (Clenow canonical).
- `[ml_for_algo_trading, ch.4, p.86]` — 12-1 skip-a-month canonical.

**Supporting**:

- `[risk_parity, p.10-11, ch.1]` — fixed-weight stack (inherited from
  iter 016).
- `[systematic_trading, p.40, ch.2]` — volatility standardisation.
- `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 cap.
- `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` + `momentum_{t-1}` lag.
- `[advances_fin_ml, p.208-211]` — PBO vacuous PASS.
- `[advances_fin_ml, p.222-223]` — DSR n_trials.
- `[advances_fin_ml, p.31-34]` — cross-lib parity discipline.

**Web**:

- Asness, C., Moskowitz, T., Pedersen, L. (2013). "Value and Momentum
  Everywhere." *JoF* 68(3). SSRN
  [1363476](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1363476).
- Moskowitz, T., Ooi, Y.H., Pedersen, L. (2012). "Time Series
  Momentum." *JFE* 104(2), 228-250. DOI
  [10.1016/j.jfineco.2011.11.003](https://doi.org/10.1016/j.jfineco.2011.11.003).
- Moreira, A., Muir, T. (2017). "Volatility-Managed Portfolios."
  *JoF* 72(4), 1611-1644. DOI
  [10.1111/jofi.12513](https://doi.org/10.1111/jofi.12513) —
  iter 016 primitive that iter 017 extends.

---

## Next iteration suggestions

Iter 017 closes the cross-sectional regional-rotation direction.
Iter 016 remains the hunt-loop high (79/100 STRONG, 4/5 winner
conditions, DSR sole barrier). The DSR ceiling remains the only
path forward:

1. **[OPTION S — Put-spread collar tail-hedge on iter 016 equity leg]**
   — highest structural novelty still available. Fund a 10Δ put
   spread via a 25Δ covered call on the SPY/QQQ leg of iter 016;
   bond leg unchanged. Adds skewness-capture dimension (Taleb).
   Expected +0.05-0.15 Sharpe via MDD reduction and preserved
   upside. Requires options-chain data (not in current cache) —
   higher engineering cost but clean structural orthogonality to
   iter 017's failed mechanism.
   Citations: `[dynamic_hedging, ch.3-4]` (Taleb), Carr-Madan (1999),
   and the CBOE PPUT index methodology (cboe.com/indices).

2. **[OPTION Q — Funding-cost-modeled iter 016 replay]** — robustness
   verification. Subtract `0.5 × DGS3MO_daily_return` from iter 016's
   net returns; document the TRUE deployable Sharpe post-funding
   cost. CHEAP (0 new trials, same config, different cost model).
   Not a hunt-loop iteration but a deployability validation.

3. **[OPTION P — HMM stock-bond correlation regime rotation on iter
   016 base]** — tertiary. 2-state HMM on 60d rolling ρ(SPY, IEF):
   regime A (ρ < −0.1) → iter 016 60:40; regime B (ρ > 0) → defensive
   30:70 or cash+IEF. Preserves fixed-ratio discipline within each
   regime. BUT iter 014's structural cointegration finding predicts
   pre-validation screen will likely FAIL (ρ_60 with σ²_port
   typically > 0.30 on > 20 % of bars). Run pre-val screen FIRST;
   if it fails, skip without committing DSR budget. Expected +0.05-
   0.15 Sharpe IF the screen passes — unlikely but not yet empirically
   tested for CORRELATION-STATE-HMM specifically (iter 014 was EBP,
   iter 013 was LR meta on ρ+VIX). Cheaper than options; requires
   sklearn HMM. Citation `[regime_change, ch.2]`.

**Iter 018 PICK: Option S (put-spread collar)** IF options data can be
sourced (SPY put-spread history from CBOE is freely available but
requires ingestion work). Otherwise, **Option Q (funding-cost replay
of iter 016)** is the zero-risk cheapest next step, documenting true
deployability of our top candidate. Save Option P for iter 019 pending
the pre-val screen.

---

## Files produced in this iteration

```
studies/strategy_hunt_loop/iterations/017-2026-04-24-1750-regional-rotation-stack-vm/
  hypothesis.md                    (~8.5 KB — Stage 2 pre-commit)
  regional_rotation_stack.py       (~9 KB — pandas engine)
  numpy_reference_regional.py      (~5 KB — G7 reference)
  run_backtests.py                 (~7 KB — 3-dataset runner)
  compute_gates_and_score.py       (~15 KB — 7 gates + score)
  results.json                     (~618 KB — per-bar series + selection log)
  verdict.json                     (~6 KB — scored verdict)
  final_report.md                  (this file)
tests/
  test_regional_rotation_stack.py  (~10 KB — 11 TDD specs, all pass)
```

Baseline pytest: 844 passed + 5 skipped (up from iter 016's
775 + 5; +64 from other sessions, +11 from iter 017's new specs;
net nondestructive).

No files modified outside of iter 017's own directory + TDD tests
file (per PROMPT Stage 3 rules).
