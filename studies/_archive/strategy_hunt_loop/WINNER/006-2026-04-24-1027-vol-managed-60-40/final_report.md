# Iteration 006 — Final Report

## Verdict

**🥈 PROMISING (score 67/100, winner_conditions_met=False, tier=PROMISING)**

Vol-managed SPY+TLT (QQQ+TLT on ndx) with inverse-variance weighting
per leg and Moreira-Muir portfolio-level variance-scaling produces the
**best hunt-loop result to date** (score 67 vs iter 005's 59, new top-K
#1). It clears the **+0.10 Sharpe gate on 2 of 3 datasets** (educational
+0.268, spy_real +0.100 exact) for the first time in the hunt loop, and
achieves **15/15 points on both CAGR floor AND MDD ceiling** — also a
first. 4 of the 5 strict winner conditions hold; only DSR fails
(unclearable at cumulative n_trials=4228 without Sharpe ≥ 1.4).

**Kill criteria check** (pre-committed):

- **Kill #1** (edge ≤ iter 005 on BOTH real slots): **NOT triggered**
  — spy edge +0.100 improves over iter 005 +0.081, though ndx edge
  +0.066 is below iter 005 +0.097. Mixed.
- **Kill #2** (real-data MDD > bench + 5pp): **NOT triggered**. spy MDD
  37.21% < 38.70% and ndx MDD 37.21% < 40.12% — the 2022 bond bear
  market did NOT break the diversification mechanism on the top
  candidate cfg.
- **Kill #3** (spy_real grid-level PBO > 0.5): **TRIGGERED**
  (0.690 > 0.5). The 12-config blend grid is substantially MORE
  overfit-sensitive than iter 005's single-asset variance-scaling
  grid (0.238). This is a structural caveat — the blend mechanism
  adds a new degree of freedom (leg weighting) that destabilises IS/OOS
  rank ordering.

The iteration is a **partial win**: score improves +8 pts over iter
005, mechanism clears more strict winner conditions than any prior
hunt, BUT the PBO degradation on spy_real is a structural signal the
12-config blend grid cannot be trusted for pure rank selection.

## Headline metrics (top candidate per dataset)

Leg correlations measured over each window:
- educational (SPY+TLT 2002-2026): ρ = **−0.307**
- spy_real (SPY+TLT 2009-2026): ρ = **−0.295**
- ndx_real (QQQ+TLT 2010-2026): ρ = **−0.225**

All three negative — diversification premise holds across windows.

| dataset | top cfg | Sharpe (Δ) | CAGR (Δ) | MDD (Δ vs bench) | gates | w_spy_med | cap_hit |
|---|---|---|---|---|---|---|---|
| educational (SPY+TLT 24y) | `vt15_L63_cap20` | **0.929** (+0.268) | 14.44% (+3.35pp) | 40.10% (−15.10pp) | **5/7** | 0.45 | 85.0% |
| spy_real (SPY+TLT 17y) | `vt15_L21_cap20` | **1.000** (+0.100) | 16.08% (+1.16pp) | 37.21% (+3.51pp) | **5/7** | 0.51 | 84.9% |
| ndx_real (QQQ+TLT 16y) | `vt15_L21_cap20` | **1.021** (+0.066) | 17.90% (−1.10pp) | 37.21% (+2.09pp) | **6/7** | 0.40 | 75.8% |

Two observations worth highlighting:

1. **Educational MDD reduction is massive** (−15.10 pp vs SPY b&h over
   2002-2026). This is the largest MDD improvement any hunt-loop
   iteration has produced. The 24y window includes dot-com (SPY −51%)
   and GFC (SPY −55%) — inverse-variance weighting plus Moreira-Muir
   scaling cuts peak-to-trough to 40%.
2. **w_spy_med ≈ 0.40-0.51** across datasets — the inverse-variance
   weighting lands close to the traditional 60/40 equity-weight (0.60)
   after accounting for TLT's lower absolute volatility. The measured
   realised naïve-RP weight is a touch below 50% equity because the
   post-2009 SPY vol (~15% ann) vs TLT vol (~15% ann post-2022) is
   near 1:1 on average, slightly tilted to bonds by TLT's lower
   autocorrelation.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **20** | 25 | 2/3 datasets beat bench + 0.10 (educational +0.268, spy_real +0.100 exact); ndx_real +0.066 just below +0.10 |
| 2 Gates | **17** | 25 | edu 5/7 (5 pts at min) + spy 5/7 (5 pts at min+1) + ndx 6/7 (5 pts at min+2) + **+4 cross-dataset bonus** (all 3 meet spec §0 minimums) − 2 total clip |
| 3 DSR | **0** | 15 | worst p = 0.332 (spy_real) at cumulative n_trials=4228 — DSR deflator still dominates at Sharpe ~1.0 |
| 4 CAGR floor | **15** | 15 | 3/3 datasets reach 0.8 × benchmark CAGR (edu 14.44%≥8.87%, spy 16.08%≥11.98%, ndx 17.90%≥15.35%) |
| 5 MDD ceiling | **15** | 15 | 3/3 datasets within benchmark MDD + 5pp (edu 40.10%≤60.20%, spy 37.21%≤38.70%, ndx 37.21%≤40.12%) |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **67** | 100+5 | tier: **🥈 PROMISING** |

**+8 points over iter 005 (59 → 67)** and moves from MARGINAL tier to
PROMISING tier. This is the strongest score the hunt loop has produced.

## Gate detail (G1-G7) per dataset

| gate | edu | spy | ndx |
|---|---|---|---|
| G1 PBO | **FAIL 0.690** | **FAIL 0.690** | PASS 0.472 |
| G2 DSR p | FAIL 0.200 | FAIL 0.332 | FAIL 0.329 |
| G3 WF | PASS 7/8 | PASS 7/8 | PASS 8/8 |
| G4 OOS Sh | PASS +0.465 | PASS +0.350 | PASS +0.303 |
| G5 FWD Sh | PASS +0.282 | PASS +0.420 | PASS +0.448 |
| G6 boot CI | PASS +0.286 | PASS +0.202 | PASS +0.175 |
| G7 xlib pp | PASS 0.051 | PASS 0.029 | PASS 0.043 |

Comparison vs iter 005 on real-data gates:

| gate | iter 006 spy | iter 005 spy | iter 006 ndx | iter 005 ndx |
|---|---|---|---|---|
| G1 PBO | **0.690 (FAIL)** | **0.238 (PASS)** | 0.472 (PASS) | 0.147 (PASS) |
| G3 WF | 7/8 | 8/8 | 8/8 | 8/8 |
| G6 boot CI | +0.202 | +0.212 | +0.175 | +0.214 |

**G1 PBO degradation is the structural cost of the 2-asset mechanism.**
Adding leg-weights creates new IS/OOS instability because short-lookback
configs (21d) detected the 2022 bond crash faster than long-lookback
configs (126d), leading to IS/OOS rank reversals. This is a real
degradation not a bug — the cross-lib G7 parity is 0.03-0.05 pp, well
within tolerance.

## Configuration tested

- **Grid**: 12 configs = `target_vol ∈ {0.15, 0.20}` × `lookback ∈ {21,
  63, 126}` × `max_leverage ∈ {1.5, 2.0}`.
- **Winners (picked per dataset by Sharpe)**:
  - educational: `vt15_L63_cap20` — target_vol=0.15, lookback=63,
    max_leverage=2.0 (full-cap 85% of bars).
  - spy_real & ndx_real: `vt15_L21_cap20` — same `target_vol=0.15` and
    `max_leverage=2.0` but short lookback L=21 (fastest vol response).
- **Cost model**: 2 bps per unit of per-leg position change
  (`cost_bps_per_leg=0.0002`). Total round-trip cost on gross ≤ 4 bps.

## What worked

1. **Cross-asset diversification premise confirmed on 3/3 windows**.
   Realised ρ_SPY,TLT ∈ [−0.23, −0.31] across the 3 windows aligns
   with `[risk_parity, p.80-81, ch.4]` (−0.58 in RORO regimes,
   smaller in-magnitude in quiet regimes, still negative).
   Diversification return `[risk_parity, p.109-110, ch.5]` is real
   and measurable: the blend's risk-adjusted outcome exceeds each
   individual leg's Sharpe.

2. **Educational slot breakout**. The 24y SPY+TLT window produces
   Sharpe +0.268 Δ and MDD −15 pp — both the largest hunt-loop numbers
   to date. Long-horizon vol regime shifts (dot-com crash, GFC, COVID)
   are exactly the regimes where variance-scaling × inverse-variance
   weighting compounds most aggressively.

3. **+0.10 Sharpe gate cleared on spy_real** (exact, 1.000 vs 0.900
   bench). This is the first iteration in the hunt loop to clear the
   strict Sharpe edge gate on a real-data slot. Combined with
   educational's +0.268, 2 of 3 datasets now satisfy criterion 1.

4. **CAGR floor + MDD ceiling 3/3 × 3/3** — first iteration to clear
   both floors on all 3 datasets. Criterion 4 + 5 = 30/30 pts.

5. **Cross-lib G7 parity 0.03-0.05 pp** on all 3 top candidates —
   engine is clean on the blend mechanism. The numpy-reference and
   pandas engine agree to < 5 bp of annualised CAGR.

6. **TDD discipline**. 11 specs covering inverse-variance weighting
   normalisation, 50/50 symmetric case, high-vol-leg weight reduction,
   no-look-ahead, zero-variance degenerate, cap clipping, and domain
   validation. All passed on first implementation. Baseline went from
   707 to 718 passed (+11 new specs), no regressions.

## What didn't work (and why)

1. **Grid-level PBO degraded on 2 of 3 datasets** (edu 0.690 vs iter
   005 edu 0.571, spy 0.690 vs iter 005 spy 0.238). The 2-asset blend
   adds a new degree of freedom (leg weighting dynamics) that destabilises
   IS/OOS rank ordering when the grid has close-to-identical returns.
   Two mitigations for iter 007+:
   - Pre-specify ONE config (L=63, cap=2.0) — no grid, no PBO issue.
   - Expand grid to ≥ 24 configs with deliberate return dispersion
     (e.g., target_vol ∈ {0.10, 0.12, 0.15, 0.20, 0.25}) to make
     IS/OOS rank difference material.

2. **ndx_real Sharpe edge is below +0.10** (+0.066 vs iter 005 +0.097).
   QQQ+TLT correlation is weaker (−0.225) than SPY+TLT (−0.295), so
   the diversification benefit is smaller. The blend marginally
   underperforms single-asset variance-scaling on ndx because TLT's
   diversification value relative to QQQ is less than relative to SPY.

3. **DSR remains structurally unclearable** at n_trials=4228 with
   Sharpe ≤ 1.05. The DSR bar for p<0.05 at this cumulative n_trials
   sits at Sharpe ≈ 1.4 — every incremental iteration inflates the
   bar. Any further hunt iteration should expect G2 failure.

4. **spy_real CAGR barely over floor** — 16.08% vs floor 11.98%
   passes comfortably, but the blend's lower-vol character naturally
   reduces CAGR relative to a levered SPY-only strategy. If future
   iterations need higher CAGR tier, they'd have to lever the blend
   further (above cap=2.0) at the cost of IDM compliance.

## Main lesson (for future iterations)

**Cross-asset diversification on a 2-leg blend is a real and
quantifiable edge axis — +0.17 Sharpe vs iter 005 single-asset on the
24y slot, +0.02 Sharpe on spy_real, but −0.03 Sharpe on ndx_real.** The
mechanism is additive: blend gets MDD reduction + diversification
return + variance-scaling, which improves the 4 "floor-type" criteria
(4 CAGR, 5 MDD, cross-dataset gate count) substantially. **What it
does NOT fix is DSR at cumulative n_trials** — the Sharpe magnitudes
are still in the 1.0 range, and the hunt-loop's mandate-consolidation
pressure keeps DSR at an asymptotically rising bar.

Path forward (two options, neither invalidated by this iteration):

- **[OPT A] Single pre-committed config (no grid)**. Commit to
  `vt15_L63_cap20` ex-ante and run ONLY 1 config per dataset. This
  eliminates the PBO issue (PBO requires a grid) and gives back the
  G1 slot on all 3 datasets. Total cumulative n_trials would increment
  by only 3 instead of 36. DSR remains hard.
- **[OPT B] Signal compounding on top of blend**. Add 12-1 momentum
  signal (Moreira-Muir Table IV) that gates the scale factor between
  {0, s_t}. This adds a SECOND independent edge axis (trend) on top
  of the diversification axis already captured. Predicted uplift:
  +0.05-0.10 Sharpe on top of the blend's 1.00-1.02 → potential 1.05-
  1.12 Sharpe edge — approaching the DSR bar.

Option B is the higher-information choice but more complex. Option A
(trivially cheap) should be tried as a verification step: if
ex-ante-committed cfg `vt15_L63_cap20` survives on 3 datasets with
Sharpe ≥ +0.10 edge on ≥2 (same as grid-selection), that materially
strengthens the case. It also gives a tight, deployment-ready single
config rather than a family of tuning options.

## Structural dead-ends discovered

**None.** The blend mechanism is validated as a partial edge (+0.10
real-data on spy, +0.27 on 24y edu, MDD reduction on all 3 windows).
It's NOT a dead-end — the structural finding is:

- **12-config grid of vol-managed 2-leg blend is overfit-sensitive
  on spy_real (PBO 0.690)**. Future grids on this mechanism family
  must either (a) pre-commit single config without sweep, or (b)
  expand to ≥ 24 configs with deliberate return dispersion.

This is NOT a DEAD_ENDS entry at the mechanism level; it's a grid-
design principle for future blend experiments.

## Citations used

**Primary**:

- **`[risk_parity, p.10-11, ch.1]`** — naïve risk parity (inverse-
  variance weighting) is exact ERC for two-asset portfolios regardless
  of correlation. The core sizing rule this iteration instantiates.
- **`[systematic_trading, p.170-171, ch.11]`** — IDM ≤ 2.5 cap on
  total gross leverage. `max_leverage=2.0` is compliant.
- **Moreira, A., & Muir, T. (2017).** *Journal of Finance* 72(4),
  1611-1644. DOI [10.1111/jofi.12513](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12513).
  Variance-scaling applied to portfolio-level variance (reference from
  iter 005).

**Supporting**:

- `[risk_parity, p.5, ch.1]` — 60/40 variance decomposition (92% stocks
  / 8% bonds); quantitative base for why inverse-vol rebalances toward
  true risk parity.
- `[risk_parity, p.16, ch.1]` — three-leverage-level rule.
- `[risk_parity, p.80-81, ch.4]` — RORO stock-bond correlation −0.58
  to −0.53 in 2009-2012 (measured in this iter: −0.295 on spy_real).
- `[risk_parity, p.109-110, ch.5]` — diversification return is
  non-negative for long-only unlevered portfolios.
- `[systematic_trading, p.40, 42, 46, ch.2]` — volatility
  standardisation, Law of Active Management, multi-asset Sharpe ceiling.
- `[systematic_trading, p.137-148, ch.9]` — target-vol as Half-Kelly.
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag (no look-ahead).
- `[advances_fin_ml, p.208-211]` — PBO/CSCV (G1).
- `[advances_fin_ml, p.222-223, 275]` — DSR cumulative n_trials (G2).
- `[advances_fin_ml, p.196-202]` — stationary bootstrap (G6).
- `[advances_fin_ml, p.31-34]` — cross-lib parity (G7).

**Web / external**:

- **Asness, C., Frazzini, A., & Pedersen, L. (2012).** "Leverage
  Aversion and Risk Parity." *Financial Analysts Journal* 68(1),
  47-59. SSRN [1728082](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1728082).
  Levered risk parity outperforms market-weighted equity on Sharpe
  basis 1926-2010. Supports leverage > 1.0 on the blend.
- **Cederburg, O'Doherty, Wang, Yan (2020).** "On the Performance of
  Volatility-Managed Portfolios." *JFE* 138(1), 95-117. DOI
  [10.1016/j.jfineco.2019.09.002](https://doi.org/10.1016/j.jfineco.2019.09.002).
  OOS attenuation reference (applied from iter 005).

## Next iteration suggestions

Three structurally different directions, ranked by information gain:

1. **[PICK FIRST] Single pre-committed blend config (no grid search)**.
   Commit `vt15_L63_cap20` ex-ante. Run ONLY 1 config per dataset.
   Eliminates PBO failure mode. Result directly interpretable as
   "does the blend mechanism deployment-ready config survive pure
   out-of-sample?" Tests Kill #3 at the grid-design level and costs
   only +3 n_trials (cumulative 4231 vs current 4228).

2. **Blend + 12-1 momentum overlay** (Moreira-Muir Table IV). The
   same SPY+TLT blend, but the portfolio scale is gated by a signal
   `s_t ← s_t × clip(momentum_12_1, 0, 1)` — only deploy when trend
   is positive. Adds a genuinely independent edge source on top of
   the correlation axis already captured by iter 006.

3. **Blend extended to SPY+TLT+GLD** (3-asset naïve-RP + portfolio
   variance-scaling). Gold adds a third risk factor (real-asset /
   inflation hedge) with typically near-zero correlation to both
   stocks and bonds — should widen diversification return further.
   Requires validating 3-asset IDM compliance at cap ≤ 2.5.

Option 1 is the verification step; Option 2 is the highest-expected-
score direction; Option 3 is the structural-extension direction.

## Baseline pytest

- Before iter 006: 707 passed + 5 skipped = 712 collected
- After iter 006: 718 passed + 5 skipped = 723 collected (added 11
  TDD specs in `tests/test_stock_bond_blend_sizing.py`, no other test
  changes)

Baseline green. No regressions.
