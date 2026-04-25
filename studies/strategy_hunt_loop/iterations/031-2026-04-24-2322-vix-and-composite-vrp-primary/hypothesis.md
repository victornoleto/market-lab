# Iteration 031 — VIX AND-composite (R-1 level+persistence × R-2 z-score) VRP-primary

## Hypothesis

Gate a new short 5/10-% put-credit-spread open only when BOTH axes fire
simultaneously:

  * **R-1** (level + persistence, iter 029): `vix[i] >= 35` for 3 consecutive bars
  * **R-2** (z-score, iter 030): `rolling_zscore(vix, 60)[i] >= 2.0`

Composite (AND): skip open iff `R-1(i) AND R-2(i)`. Otherwise open.

The intersection is strictly a subset of either single-axis gate. It
fires only during *absolute* shocks above 35 IV that are *also*
statistically extreme relative to the local 60d regime — the genuinely
worst regimes (Sep-Oct 2008 GFC initial ramp; Mar-2020 COVID) where
both axes agree. It stays silent (→ open) on:

- iter 026 baseline regimes (benign volatility; neither fires)
- sustained-high 2008-Q4 (R-1 fires but z<<2 once the 60d mean has
  absorbed the spike — iter 030's educational regression regime)
- ndx tech mini-spikes (VIX≈26, z=2.4: R-2 fires but R-1 silent —
  iter 030's ndx Kill A regime)
- fast transient shocks below VIX 35 (R-2 fires but R-1 silent —
  the bulk of iter 030's spy gain; composite gives up this gain in
  exchange for never triggering the cross-dataset Kill A+B)

## Primary citation

`[volatility_trading, p.217-218]` — Sinclair (2013) ch. 8 §§ "Hedging short
volatility positions" + "VIX-VXV term structure": establishes BOTH the
level filter (VIX < 35 entry threshold for short-index-vol writers) AND
the sustained-vs-transient distinction (vol persistence is the warning
sign, not one-day spikes). The AND-composite is the literature-faithful
intersection of both dimensions Sinclair explicitly describes.

## Additional citations

- `[volatility_trading, p.39]` — VIX vol-of-vol regime-dependent,
  motivates z-score normalization.
- `[volatility_trading, p.58-59]` — volatility cone 60d middle horizon
  (z_window anchor).
- `[volatility_trading, ch.3, p.41]` — VRP mechanics (unchanged from
  iter 026).
- `[advances_fin_ml, p.31-34]` — cross-library parity (G7 mandatory).
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials.
- Web: **Bondarenko, O. (2014). "Why Are Put Options So Expensive?"**
  *Quarterly Journal of Finance* 4(3): 1450015.
  DOI: 10.1142/S2010139214500153 — §3 establishes *both* level *and*
  persistence matter (explicit motivation for the AND-composite).
- Web: **Carr, P. & Wu, L. (2009). "Variance Risk Premiums."** *RFS*
  22(3): 1311-1341. DOI: 10.1093/rfs/hhn038 — VRP decomposition into
  level / persistence / innovation axes; iter 031 combines level and
  persistence axes while leaving innovation unfiltered.
- Web: **Whaley, R. E. (2009). "Understanding the VIX."** *Journal of
  Portfolio Management* 35(3): 98-105. DOI: 10.3905/JPM.2009.35.3.098
  — VIX innovation analysis using standardized deviations.

## Edge source (1 sentence)

SPY 1× buy-hold cannot harvest the variance risk premium at all;
iter 026 captures it fully but absorbs losses during the very worst
sustained-*and*-extreme regimes (Sep 2008, Mar 2020), and no
single-axis gate within the loop's 3-iteration single-axis family
(028/029/030) simultaneously optimizes all 3 hunt-loop datasets — the
*intersection* of level+persistence and z-score axes should filter
only the genuinely worst regimes, preserving iter 026's harvest
elsewhere.

## Datasets

- **educational** (SPY+VIX, 2006-01-03 → 2026-04-14, ~20y inc. GFC):
  test case for the sustained-high regime — AND-composite must at
  least fire Sep-Oct 2008 where both axes agree, and stay silent
  during the Nov-Dec 2008 sustained period where only R-1 fires
  (the regime where iter 030 hurt edu and iter 028 helped).
- **spy_real** (SPY+VIX Tiingo, 2009-06-25 → 2026-04-14, 17y):
  composite should fire in Mar-2020 (both axes) and probably in
  2015-Aug / 2018-Feb (level+persistence borderline; z definitely
  fires); the key question is whether giving up iter 030's spy
  gain (VIX<35 innovation shocks) costs more or less than the
  ndx preservation buys.
- **ndx_real** (QQQ+VIX×1.1 Tiingo, 2010-02-12 → 2026-04-14, 16y):
  critical test — composite should NOT fire on tech mini-spikes
  (VIX≈26, z≈2.4 pass R-2 but fail R-1) → preserves iter 026's ndx
  harvest, which is where iter 030 Kill A triggered cleanly.

## Kill criteria (pre-committed)

If ANY of the following holds at end of Stage 4, the hypothesis is
falsified regardless of secondary metrics:

- **Kill A** (composite-vacuous): AND-composite fires 0 rolls across
  the full 20y educational window. The intersection was designed to
  catch 2008-Q4 GFC initial ramp (Sep-Oct 2008) and Mar-2020 — both
  regimes where level AND z-score agree. A zero-fire composite means
  the intersection is empty by construction and adds nothing.
- **Kill B** (educational collapse): educational Sharpe < 1.03
  (= iter 026's 1.1334 − 0.10). AND-composite should preserve iter
  026 baseline by design (it's more permissive than iter 030); a
  collapse means a subtle bug or regime misclassification.
- **Kill C** (post-GFC regress): spy_real OR ndx_real Sharpe <
  (iter 026 baseline) − 0.05. Specifically spy floor 1.23, ndx floor
  1.32. Filtering at the genuinely worst regimes must NOT cost more
  than 5 bp vs no-filter on post-GFC datasets.
- **Kill D** (21d worst): any dataset has 21-day rolling sum < −30%.
  Composite should never produce catastrophic 21d losses since it's
  strictly more permissive than iter 026 on most regimes.
- **Kill E** (engine dirty): G7 cross-lib > 3 pp on any dataset
  (pandas engine vs numpy reference disagree beyond tolerance).
- **Kill F** (no score improvement): total canonical score < 76
  (iter 026 reference). The AND-composite axis must produce a
  strictly better score than no-filter, or it adds no structural
  value. (Note: this kill is a lower bar than the WINNER threshold
  of 90 — even a marginal improvement counts.)

## Decision logic

Given three sub-outcomes on {kill_A, kill_F}:

| kill_A | kill_F | interpretation |
|---|---|---|
| YES | YES | Intersection empty; AND-axis structurally closed. |
| YES | NO | Impossible (no-fire = iter 026 by construction; score 76 = kill_F boundary, so likely this combo → "ties iter 026 exactly"). |
| NO | YES | Composite fires but adds no value → likely filters good harvest; iter 026 remains top-K. |
| NO | NO | Structural novelty: composite improves over iter 026 AND at least preserves axes. Score >= 77 opens door to tier upgrade. |

## Expected budget

- Configs to test: **1** (single pre-committed cfg, no grid, no
  sweep — consistent with iter 028/029/030 pattern).
- Cumulative n_trials: 4283 + 1 = **4284**.
- Wall-time: < 2 min per dataset (3 datasets × ~5s simulation + DSR
  bootstrap G6 ~30s = ~2 min total).
- Files to create:
  - `vrp_and_composite.py` (pandas engine, ~280 lines)
  - `numpy_reference_and_composite.py` (G7 parity, ~180 lines)
  - `run_backtests.py` (3-dataset runner, ~420 lines)
  - `compute_gates_and_score.py` (~500 lines)
  - `tests/test_vrp_and_composite.py` (TDD, ~120 lines)
  - `results.json`, `verdict.json`, `final_report.md`
  - 2 PNG plots (via `plot_helper.py`)

## Implementation plan

1. **TDD**: write `tests/test_vrp_and_composite.py` with 5 specs BEFORE
   implementation:
   - reduction-parity-1: `vix_threshold=1e9` reproduces iter 026 exactly
     (R-1 can never fire → AND can never fire → no skip ever)
   - reduction-parity-2: `z_threshold=1e9` reproduces iter 026 exactly
     (R-2 can never fire → AND can never fire)
   - reduction-parity-3: `persistence_days=1, vix_threshold=0,
     z_threshold=0` with both gates permissive → still opens (both
     would fire → skip); but `vix_threshold=0` means R-1 always
     fires → composite depends on R-2 only — test this falls back
     to iter 030 semantics
   - composite-and-correctness: synthetic 5-day window with level
     AND z both firing only on day 2 → exactly 1 skip on day 2
   - G7-parity: numpy vs pandas engine ≤ 1e-10 on all 3 datasets

2. **Engine** (`vrp_and_composite.py`): copy iter 029's
   `vrp_persistence.py` as base, inject the z-score check into the
   open-gate condition. The gate fires (skip) iff
   `is_persistent_high(vix, i, threshold, persistence_days) AND
   is_z_high(z, i, z_threshold)`. Both helpers imported from their
   respective iter dirs.

3. **NumPy reference** (`numpy_reference_and_composite.py`): mirror
   iter 030's `numpy_reference_zscore.py` structure, add the
   persistence check inline.

4. **Run** (`run_backtests.py`): follow iter 030's pattern; use
   full-history VIX (from 1990-01-02) for z-score warmup.
   Diagnostics must report:
   - natural_rolls per dataset
   - rolls_skipped_composite (AND) count
   - rolls_skipped_persistence_only (R-1 isolated)
   - rolls_skipped_zscore_only (R-2 isolated)
   - dates where composite fired (with VIX + z values)

5. **Gates** (`compute_gates_and_score.py`): mirror iter 030's
   structure. Kill criteria evaluator specific to iter 031 (A-F).
   References: iter 026 (baseline), iter 028 (level), iter 029
   (level+persistence), iter 030 (z-score).

6. **Stage 5**: final_report.md, verdict.json, plot_helper.py,
   update BASE_MEMORY + DEAD_ENDS.

## Success/fail framing

- **Tier WINNER (🏆, score ≥ 90 + 5/5 strict)**: extraordinarily
  unlikely but not impossible — requires CAGR floor (criterion 4 =
  15) to clear in ≥ 2 datasets. All iter 026-family cfgs score 0/15
  on CAGR because harvest_notional=1.0 caps CAGR at ~5%/yr on
  T-bill+overlay. WINNER would need a separately-addressed leverage
  component, out of scope.
- **Tier STRONG (🥇, score 75-89)**: plausible. If the composite
  fires just a few times and avoids both iter 030 Kill cases, the
  score should match iter 026 (76) + potentially gain on DSR if the
  unblocked regimes don't dilute Sharpe edge.
- **Tier PROMISING (🥈, 60-74)**: the 4th consecutive 71 if the
  composite is too selective.
- **Tier ≤ MARGINAL**: only if Kill B or C trigger (unlikely).

The honest expected outcome is **STRONG ≈ 76** (matching iter 026),
with the structural finding being one of:

- Composite is genuinely novel — closes the AND-of-axes direction
  with a concrete score (iter 026 still top-K).
- Composite produces a slight DSR gain if the now-unskipped innovation
  shocks (that iter 030 skipped) happen to be regime-profitable.
- Composite fires zero times on educational → Kill A → full structural
  closure of single-axis-within-AND-composite family on iter 026 base.

All three outcomes are structurally informative.
