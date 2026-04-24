# Iteration 007 — Vol-managed 60/40 SPY+TLT × time-series-momentum overlay

## Hypothesis

Take iter 006's vol-managed SPY+TLT blend (inverse-variance per leg +
Moreira-Muir portfolio variance-scaling) and gate the deployment by a
time-series momentum signal on the equity leg: deploy the blend only
when the canonical 12-1 (skip-a-month) momentum on SPY (or QQQ for the
ndx slot) is positive; otherwise hold cash. This compounds iter 006's
cross-asset diversification edge with an independent trend-timing edge
axis, aiming to push Sharpe on real data from the 1.00-1.02 range
toward 1.10+ — the only productive path left after iter 005 proved
single-asset vol-adaptation saturates at +0.08-0.10, and iter 006
showed that adding a 2nd asset alone still leaves 0.04 of headroom on
ndx and no headroom on DSR.

## Primary citation

`[ml_for_algo_trading, ch.4 p.86]` — **RULE**: "For momentum, use
12-month return EXCLUDING the most recent month (skip-a-month) to
avoid short-term reversal contamination." This is the canonical
Jegadeesh-Titman (1993) formulation transported into an applied ML
context. The skip-a-month detail is what separates modern time-series
momentum from the naïve 12-month return.

## Additional citations

- `[algo_trading_chan, p.133, ch.6]` — time series momentum definition:
  "past returns of a single instrument are positively correlated with
  future returns".
- `[algo_trading_chan, p.156-157, ch.6]` — TU Time Series Momentum
  Strategy as a concrete implementation template.
- `[algo_trading_chan, p.164, ch.6]` — **lookback=252, holddays=25**
  based on Moskowitz, Yao & Pedersen (2012); "low curve-fit risk:
  published, replicated across many markets". This anchors the 252-day
  (12-month) lookback choice to canonical academic literature, not
  parameter tuning.
- `[evidence_based_ta, p.398]` — MLM Index uses **12-month MA** on 25
  commodities as a trend benchmark; "extremely simplistic" but
  economically justified as a risk premium for hedger service (NOT
  curve-fit) `[p.380-384]`.
- `[leverage_for_the_long_run, p.7, footnote 12]` — Grinblatt &
  Moskowitz (2000) autocorrelation/momentum underpinning. Same book
  p.9 shows SMA regime filters: below-MA regimes exhibit 2-3× the
  volatility of above-MA regimes. The momentum overlay captures this
  asymmetry, gating off in high-vol regimes.
- `[risk_parity, p.10-11, ch.1]` (from iter 006) — naïve risk parity
  (inverse-variance weighting).
- `[systematic_trading, p.170-171, ch.11]` (from iter 006) — IDM ≤ 2.5
  hard cap.
- `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` lag / no look-ahead; also
  applies to momentum lag.
- `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]` — G1
  PBO, G2 DSR, G6 bootstrap, G7 cross-lib.

**Web / external**:

- Moreira, A., & Muir, T. (2017). *Journal of Finance* 72(4) 1611-1644.
  DOI [10.1111/jofi.12513](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12513).
  Table IV combines vol-managed portfolios with the momentum factor
  (MOM from Kenneth French) and reports Sharpe improvements over pure
  vol-managed alone.
- Moskowitz, T., Ooi, Y. H., & Pedersen, L. (2012). "Time Series
  Momentum." *Journal of Financial Economics* 104(2) 228-250. DOI
  [10.1016/j.jfineco.2011.11.003](https://doi.org/10.1016/j.jfineco.2011.11.003).
  12-month lookback validates across 58 instruments (equity index
  futures, bond futures, commodities, FX).
- Jegadeesh, N., & Titman, S. (1993). "Returns to Buying Winners and
  Selling Losers." *Journal of Finance* 48(1) 65-91. DOI
  [10.1111/j.1540-6261.1993.tb04702.x](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x).
  Original paper establishing the 6-12 month momentum anomaly;
  skip-a-month protocol.

## Edge source

**Independent trend-timing axis on top of cross-asset diversification.**
Iter 006's blend exploits negative SPY-TLT correlation (ρ = −0.23 to
−0.31). This iteration adds a second, orthogonal edge source: in
strong down-trend equity regimes (12-1 mom ≤ 0) the blend is flat,
sidestepping the worst loss paths; in up-trend regimes the blend
operates at full Moreira-Muir scale. SPY's realised below-MA
volatility is 2-3× its above-MA volatility `[leverage_for_the_long_run,
p.9]` — the skew between the two regimes is what buying-only-in-trend
captures.

## Datasets

- **educational** (SPY+TLT 2002-2026, 24y): longest TLT-paired window
  from iter 006 — reuses the same benchmark (SPY b&h over the window,
  Sharpe 0.661). Tests the mechanism across two major trend-reversals
  (dot-com 2000-02 and GFC 2007-09).
- **spy_real** (SPY+TLT 2009-06-25 → 2026-04-15): the hardest window.
  Post-GFC SPY Sharpe 0.90 benchmark. Iter 006 cleared +0.10 edge
  exact (1.000 vs 0.900). Momentum overlay needs to push this to
  ≥ 1.05 to materially clear (or restore after blend-cfg dilution).
- **ndx_real** (QQQ+TLT 2010-02-12 → 2026-04-15): iter 006 Sharpe
  1.021 vs QQQ 0.955 (+0.066, under +0.10 gate). Tech-heavy slot where
  the blend's bond leg dilutes the equity performance — momentum gate
  should reduce the dilution cost by skipping over trend-negative
  bond-adverse regimes (e.g., 2022).

## Kill criteria (pre-committed)

- **KILL #1**: If the top momentum-overlay cfg's Sharpe ≤ iter 006's
  blend Sharpe on BOTH real-data slots (spy_real ≤ 1.000 AND ndx_real
  ≤ 1.021), the overlay is dead-weight — adds complexity, no uplift.
  Hypothesis falsified for the momentum-compounding axis.
- **KILL #2**: If the momentum gate fires < 20% of bars OR > 95% of
  bars on any real-data slot, the gate is pathologically
  trivial/over-active. Either way the test is invalid.
- **KILL #3**: If grid-level PBO > 0.5 on 2 of 3 datasets with this
  3-config grid, the blend+momentum compound family exhibits the same
  overfit-sensitivity that killed iter 006's 12-config grid — the
  compound mechanism is structurally overfit-prone regardless of grid
  size.
- **KILL #4**: If the momentum overlay triggers > 20 regime switches
  per dataset (gross turnover > 4×/year on the gate), transaction
  costs on the full blend (2 bps per leg × full gross flip) exceed
  the realistic cost model, invalidating the net Sharpe numbers.

## Expected budget

- **Configs to test**: 3 momentum configs × 1 fixed blend cfg × 3
  datasets = **9 new trials**. Cumulative n_trials: 4228 + 9 = **4237**.
- **Wall-time**: ~15 min for backtests (reuse iter 006 scaffolding)
  + ~15 min for gate battery (PBO + bootstrap + WF dominate) + TDD ~20
  min + reporting ~30 min = **~80 min total** (well under 2h cap).
- **Files to create**:
  - `hypothesis.md` (this file)
  - `momentum_overlay.py` — momentum signal + gate function (new
    simulator logic, needs TDD).
  - `run_backtests.py` — driver adapting iter 006's run_backtests to
    apply momentum gate.
  - `numpy_reference.py` — hand-rolled reference for G7 cross-lib.
  - `compute_gates_and_score.py` — gate + score harness (adapted from
    iter 006).
  - `results.json` — per-dataset per-cfg metrics + return series.
  - `verdict.json` — score_strategy output.
  - `final_report.md` — prose summary.
  - `tests/test_momentum_overlay.py` — TDD specs (project-level).

## Implementation plan

### Grid — pre-committed for iter 007

- **Blend base** (pre-committed single cfg): `vt15_L21_cap20` from
  iter 006 — target_vol=0.15, lookback=21, max_leverage=2.0. This is
  iter 006's spy_real/ndx_real top (Sharpe 1.000 / 1.021); on
  educational it scores below `vt15_L63_cap20` but the momentum
  overlay is expected to compensate on the edu slot via regime
  avoidance.
- **Momentum overlay grid** (3 configs, all skip-1-month):
  - M1 `mom252_skip21` — canonical 12-1 momentum
    (`ml_for_algo_trading` ch.4 p.86; Jegadeesh-Titman 1993;
    Moskowitz-Ooi-Pedersen 2012).
  - M2 `mom126_skip21` — 6-1 momentum (shorter trend horizon,
    partial-year signal).
  - M3 `mom378_skip21` — 18-1 momentum (longer trend horizon, slower
    signal).
- **Threshold**: all 3 use threshold = 0 (binary gate: mom > 0 → ON,
  else → OFF = hold cash). Zero is the canonical threshold for
  "absolute momentum" / time-series momentum — `[algo_trading_chan,
  p.164, ch.6]` anchors this to Moskowitz et al. 2012.
- **Signal asset**: per-dataset equity leg (SPY for educational/
  spy_real, QQQ for ndx_real). Consistent with iter 006's
  per-dataset equity leg choice.

### Steps

1. **TDD** — write `tests/test_momentum_overlay.py` with specs:
   - Canonical 12-1 skip-a-month definition: `mom_t = P_{t-21} /
     P_{t-21-252} - 1`. Verify lag on a synthetic price path.
   - No look-ahead: at bar `t`, signal depends only on prices up to
     bar `t-21` (skip-a-month shift + lookback). The overlay-scale
     at bar `t` must use `mom_{t-1}` (shifted one more step to match
     iter 006's σ̂_{t-1} convention).
   - Binary gate: when `mom_{t-1} > 0`, return full blend scale;
     when `mom_{t-1} ≤ 0`, return 0.
   - Turn-on/turn-off behaviour at gate transitions: one-bar lag,
     no hysteresis (canonical).
   - Degenerate inputs: insufficient bars (< lookback + skip), missing
     values, flat price path.
2. **Implement** `momentum_overlay.py` with:
   - `time_series_momentum_gate(prices, lookback, skip)` → `pd.Series`
     of {0, 1} gate flags aligned with `prices.index`.
   - `apply_blend_with_momentum_overlay(r_spy, r_tlt, price_signal,
     blend_cfg, overlay_cfg)` → `(net, pos_spy, pos_tlt, scale, gate)`.
     Wraps iter 006's `apply_blend_variance_target` and multiplies
     the returned scale by the gate flag before computing per-leg
     positions. Cost model remains 2 bps per unit of per-leg
     position change (flips 0 ↔ full trigger full gross cost).
3. **Run backtests** with 3 configs × 3 datasets = 9 runs. Use iter
   006's `load_paired_returns` for SPY/TLT + QQQ/TLT windows.
   Produce `results.json` with per-cfg metrics + return series.
4. **Gate battery** (per dataset, top candidate by Sharpe):
   - G1 PBO: CSCV with n_blocks=10, 3 configs (minimum measurable).
   - G2 DSR: cumulative n_trials = 4237.
   - G3 WF: 8 windows, ≥ 6/8 profitable with MDD < 25% each.
   - G4 OOS: 70/30 split.
   - G5 FWD: post-2020 Sharpe > 0.
   - G6 Bootstrap: stationary bootstrap, 99.9% CI low > 0.
   - G7 Cross-lib: numpy-reference for the compound
     (blend × momentum) within ±3 pp CAGR.
5. **Score** via `scoring.score_strategy()` with custom benchmarks
   matching iter 006 (educational uses measured SPY 2002-2026 b&h
   bench; spy_real/ndx_real use frozen `BENCHMARKS`).
6. **Kill-criteria check** + final report + memory update.

### Cost model reminder

Using iter 006's 2 bps/unit-per-leg cost model. A regime flip
(gate 1 → 0 or 0 → 1) generates a full gross turnover of `pos_spy +
pos_tlt ≈ scale_blend` which can be 1.5-2.0 at cap. At 2 bps/unit the
per-flip cost is ~3-4 bps. Over 24y with ~10 flips (typical for 12-1
momentum on SPY) that's ~30-40 bps total — negligible. If KILL #4
triggers (> 20 flips), cost becomes material and must be re-examined.

## Cross-reference to iter 006 lessons

This iteration directly addresses iter 006's main limitations:

1. **Kill #3 (iter 006): spy_real grid-PBO 0.690.** Mitigated by
   pre-committing the blend cfg and sweeping only the momentum
   parameter (3 configs vs 12). Expected PBO regime: if the 3
   momentum lookbacks produce materially different return streams,
   PBO should be informative; if near-identical, PBO at noise floor
   (< 0.5 benign).
2. **DSR at n_trials=4228 (iter 006) unclearable at Sharpe ≤ 1.05.**
   This iteration targets Sharpe 1.10-1.15 on real data — still
   unlikely to clear p<0.05 at 4237 trials, but may clear p<0.10 (10
   pts instead of 0 on criterion 3).
3. **ndx_real edge +0.066 (iter 006) missed +0.10 gate.** Momentum
   overlay expected to add +0.05-0.10 on all 3 datasets, potentially
   pushing ndx edge to +0.12-0.17.

## Structural novelty check vs DEAD_ENDS

The closest dead-end family is "SMA/EMA crossover filter on SPY with
leverage" (iter 001 + category list). This iteration differs on FOUR
axes:

1. **Signal form**: 12-1 **momentum** (Jegadeesh-Titman /
   Moskowitz-Ooi-Pedersen canonical) — not SMA/EMA crossover. These
   are mathematically different operators: momentum is a lagged return
   differential, SMA is a running average. The skip-a-month lag also
   differentiates (no dead-end used skip-a-month).
2. **Target of the signal**: **vol-managed 2-asset blend** (SPY+TLT /
   QQQ+TLT with dynamic inverse-variance weights) — not single-asset
   SPY LETF. 2 assets, 2 dynamics: variance-weight + variance-scale.
3. **Leverage profile**: dynamic up to 2.0× (Moreira-Muir IDM-capped)
   — not fixed 2× or 3× LETF. The leverage is a function of realised
   volatility.
4. **No stop-loss overlay, no risk-composite**: the momentum gate IS
   the only off-switch. Dead-end family always combined trend filter +
   stop + risk signal — this iteration doesn't.

**Structural novelty: confirmed.** The mechanism has not been tested
in this project and is not structurally equivalent to any iter 001-006
approach. It's the explicit Option B path forward from iter 006's
final report.
