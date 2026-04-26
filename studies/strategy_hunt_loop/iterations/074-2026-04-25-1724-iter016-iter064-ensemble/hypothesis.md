# Iteration 074 — Saved-stream ensemble of iter 016 + iter 064 (low-corr Markowitz combine)

## Hypothesis

Combine the two highest-quality non-iter-064-base anchors discovered so
far via simple convex weighted blend of their pre-validated daily net
return streams:

```
r_074[t] = w_016 · r_016[t] + w_064 · r_064[t]   with w_016 + w_064 = 1
```

`r_016` = static 60:40 normalised SPY+IEF stack × Moreira-Muir
portfolio variance-target scaling (iter 016 pre-committed cfg
`ntsx_vm_vt15_L21_cap20`, score 79 STRONG, **0/7 KILLS** prior to
iter 073 confirming it's the highest-Sharpe non-iter-064 anchor).

`r_064` = `0.90 · iter_046 + 0.10 · QQQ_TREND(SMA=200)` (iter 064
pre-committed cfg `iter046_plus_qqq_trend_w010_lookback200`, score
**90 STRONG TOP-K #1**, 0/7 KILLS).

The two streams are **structurally orthogonal**:

| axis | iter 016 | iter 064 |
|---|---|---|
| equity exposure | SPY only (60% normalised) | SPY (via iter_041 inside iter_046) + QQQ (10% via QQQ_TREND) |
| bond exposure | IEF (40% normalised) | none |
| sizing rule | dynamic σ²_port-target Moreira-Muir | static convex 0.9/0.1 |
| regime gate | none (intrinsic vol) | binary VIX threshold (inside iter_041) |
| volatility risk premium | none | **cross-asset VRP basket** (iter_039) |
| trend filter | none | **single-asset QQQ 200d-SMA** (Faber 2007) |
| cointegration assumption | none (fixed normalised ratio) | none (saved streams) |

The two share SPY market beta (iter 064 carries it via iter_041's
regime-gated stack inside iter_046) but the IEF / VRP / QQQ-trend
overlays are independent. Predicted correlation: **0.60-0.80** (per
BASE_MEMORY direction #1 estimate).

The thesis: iter 064's joint TOP-K #1 90/100 is bottlenecked by **DSR
p=0.0394 spy** (just under 0.05) on cumulative n_trials=4334. Adding
a low-corr saved stream lifts observed Sharpe enough to cleanly drop
DSR worst-p below 0.05 across **all 3 datasets**, finally satisfying
strict winner condition #3. Iter 064's 4/5 winner condition gap is
exactly the DSR ≥ 0.05 on educational/ndx datasets — a moderate
Sharpe lift via Markowitz combine reaches winner.

The historical pattern of saved-stream combinations on this loop is
well-documented:

- **iter 045** (iter 037 + iter 039, ρ=0.58) → 81 STRONG (+2 vs iter 037 alone)
- **iter 046** (iter 041 + iter 039, ρ=0.41) → 85 STRONG (TOP-K #1 prior)
- **iter 058** (iter 046 + HYG_TSM, w=0.10) → 85 STRONG (Sharpe-additive,
  CAGR-dilutive)
- **iter 064** (iter 046 + QQQ_TREND, w=0.10) → **90 STRONG** (TOP-K #1)

Pattern: out-of-family additions with low correlation produce additive
Sharpe and a DSR-p-value reduction proportional to (1 - ρ) and the
new stream's standalone Sharpe. Iter 074's iter_016 has Sharpe ~1.14
(spy) — much higher than HYG_TSM (~0.99) or QQQ_TREND (~0.80) —
combined with predicted moderate ρ (0.6-0.8). If the pattern
generalises, this should reach **score 90+ with DSR<0.05 cross-dataset**
for the first time, satisfying strict winner conditions on all 5.

## Primary citation

`[risk_parity, ch.5]` + `[volatility_trading, p.218]` — Asness-Frazzini-
Pedersen risk-parity diversification (iter 016 base via NTSX-style
stack) and Sinclair (2013) volatility-arbitrage as orthogonal sleeve
(iter 064 via iter_046's iter_039 leg). Combined: the
diversification axis (iter 016) is mechanically independent from the
VRP-harvest + regime-equity axis (iter 064), satisfying Markowitz's
mean-variance benefit-of-low-corr [Markowitz 1952].

## Additional citations

- **Markowitz, H.** (1952). "Portfolio Selection." *Journal of Finance*
  7(1), 77-91. DOI [10.1111/j.1540-6261.1952.tb01525.x](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x).
  Foundation for convex-combination Sharpe of low-corr return streams.
- **Moreira, A., & Muir, T.** (2017). "Volatility-Managed Portfolios."
  *J. Finance* 72(4), 1611-1644. DOI 10.1111/jofi.12513. Iter 016's
  vol-target rule.
- **Faber, M.** (2007). "A Quantitative Approach to Tactical Asset
  Allocation." SSRN 962461 (J. Wealth Mgmt 2007). Iter 064's
  QQQ-200d-SMA filter.
- **Asness, C., Frazzini, A., & Pedersen, L.** (2012). "Leverage
  Aversion and Risk Parity." *FAJ* 68(1), 47-59. SSRN 1728082.
  Foundational risk-parity argument shared by both legs.
- **Whaley, R.** (2009). "Understanding the VIX." *JPM* 35(3), 98-105.
  DOI 10.3905/JPM.2009.35.3.098. Iter 064's VIX regime gate (inside
  iter_041).
- **Sinclair, E.** (2013). *Volatility Trading*, 2nd ed., Wiley.
  `[volatility_trading, p.218]`. Iter 064's VRP basket (inside iter_039).
- **Carver, R.** *Systematic Trading*. `[systematic_trading, p.40]`.
  Variance standardisation as sizing primitive (iter 016 base).
- `[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio with cumulative
  n_trials = 4360 (BASE_MEMORY frontmatter) + 21 trials this iter = **4381**.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV; with a real 7-cfg
  weight grid, PBO is now informatively non-trivial.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.162-164]` — no-lookahead T-1 lag on weight
  rebalance (saved streams already lagged; ensemble preserves).

## Edge source

What SPY 1x buy-hold misses that this strategy exploits: SPY-buy-hold
has only equity-market exposure. Iter 074 simultaneously captures:

1. **Stock-bond diversification under dynamic vol-target** (iter 016 leg)
   — when realised σ²_port is low, vol-target lifts gross exposure to
   ~2.0× on a SPY+IEF base; bond rallies in stress regimes counter-balance
   equity drawdowns.
2. **Cross-asset variance risk premium** (iter 064 → iter 039) —
   short-OTM-put credit spreads on SPY+QQQ+IWM harvest the vol-skew
   premium that pure equity exposure leaves on the table.
3. **VIX-regime-conditional equity tilt** (iter 064 → iter 041) —
   dynamic 70/40/40 calm vs 30/55/55 stress weight rotation among
   SPY+IEF+GLD captures regime-conditional Sharpe asymmetry.
4. **Single-asset Nasdaq trend filter** (iter 064 → QQQ_TREND) —
   200-day SMA gate on QQQ avoids tech bear markets cleanly.

The combined return stream has 4 mechanism axes orthogonal to SPY
buy-hold's pure passive equity beta. Each has independent literature
support and validated Sharpe edge in isolation.

## Datasets

- **educational** (2006-01-04 → 2026-04-15, ~5080 bars after
  inner-join): both iter 016 and iter 064 streams cover this range
  (iter 016 starts 2006-02-03 due to vol-target warmup; iter 064
  starts 2006-01-04 with longer pre-data warmup); inner-join gives
  ~5080 bars. This is iter 016's binding window where it lost edu
  CAGR by ~3pp vs spy/ndx (15.08% vs ~17-21%).
- **spy_real** (2009-07-28 → 2026-04-15, ~4205 bars after inner-join):
  primary 17y benchmark; iter 064 hits 1.33 here, iter 016 hits 1.14.
  At ρ=0.7, formula combined Sharpe ≈ 1.40 cross-dataset.
- **ndx_real** (2010-03-17 → 2026-04-15, ~4045 bars after inner-join):
  16y; iter 064 hits 1.38, iter 016 hits 1.19. Formula combined
  Sharpe ≈ 1.45 if ρ stays around 0.7.

The inner-join window slightly truncates each leg vs its native
window; this is acceptable since the truncation is at the leg with
longer warmup (iter 016).

## Kill criteria (pre-committed)

| # | Kill | Threshold |
|---|---|---|
| **A** | Combined Sharpe regress vs **iter 064** by ≥ 0.05 on ≥ 2 datasets | Iter 074 must beat iter 064 to justify additional complexity. Falsifies "low-corr ensemble lifts Sharpe". |
| **B** | DSR worst-p ≥ 0.05 on best cfg (winner cond #3 fails) | Falsifies "ensemble drops DSR below 0.05 cross-dataset". Iter 074's whole purpose is to break iter 064's DSR knife-edge. |
| **C** | Score < 90 (winner threshold) on best cfg | Iter 074 must reach 90+ to justify novelty over iter 064's 90. |
| **D** | corr(r_016, r_064) > 0.85 on ≥ 2 datasets | Streams are too similar; ensemble offers no diversification. Falsifies BASE_MEMORY's "0.6-0.8" prediction. |
| **E** | Markowitz outer residual ≥ 0.05 Sharpe abs | Indicates engine bug — convex combine of saved streams should match closed-form to high precision. |
| **F** | G7 cross-lib > 3 pp absolute CAGR difference (numpy reference) | Engine bug. |
| **G** | PBO grid-level ≥ 0.5 on ≥ 2 datasets | The 7-cfg weight grid produces in-sample/OOS rank reversal; ensemble is curve-fit to weight choice. Iter 064 had trivial PBO with N=1; iter 074's PBO is now meaningful. |
| **H** | edu CAGR < 9.18% on best cfg (winner cond #4) | Falsifies "ensemble preserves CAGR floor". |
| **I** | combined MDD on best cfg > 25% on ≥ 2 datasets (vs iter 064's 17/15/15) | Suggests one of the streams blows up the combined MDD. |

If 2+ kills fire ⇒ falsify ensemble-as-DSR-mechanism; iter 074 marked
as informative-but-not-winner. If only kill C fires (score 75-89) ⇒
STRONG saved, document the PBO/DSR axis as ceiling. **0 kills + score
≥ 90 + winner_conditions met ⇒ WINNER candidate** for shell-loop halt.

## Expected budget

- **Configs to test**: 7 — w_016 ∈ {0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80}
  with w_064 = 1 - w_016. The grid spans heavy-064 to heavy-016 to
  surface the Pareto frontier.
- **Trials advance**: 4360 → **4381** (+21 = 7 cfgs × 3 datasets,
  matching iter 073's per-dataset trial counting).
- **Wall-time**: ~25 min (saved streams reused; only G6 bootstrap,
  G3 walk-forward, G1 PBO need fresh compute).
- **Files to create**:
  - `iter074_ensemble.py` — pandas implementation of the weighted blend
  - `numpy_reference_iter074.py` — pure-numpy reference for G7
  - `run_backtests.py` — orchestrator across 3 datasets × 7 cfgs
  - `compute_gates_and_score.py` — gates + scoring helper invocation
  - `tests/test_iter074_ensemble.py` — TDD specs for blend math
  - `results.json` — full output (returns_series, runs, etc.)
  - `verdict.json` — produced by `score_strategy()`
  - `final_report.md` — Stage 5 report
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`

## Implementation plan

1. **TDD specs first** (`tests/test_iter074_ensemble.py`):
   - convex combo invariants (w_016=0 → exactly r_064; w_016=1 → exactly r_016)
   - inner-join correctness (output index = intersection)
   - weight invariance to scaling (5 specs minimum)
   - degenerate / error paths (negative weights, both 0)
2. **Implement `iter074_ensemble.py`** — `combine_iter016_iter064(...)`
   loading saved streams from each iter's `results.json`, applying
   inner-join, returning weighted blend.
3. **Implement `numpy_reference_iter074.py`** — pure-numpy reference for G7.
4. **`run_backtests.py`** — load r_016 from iter 016 results.json,
   r_064 from iter 064 results.json, combine 7 weight cfgs per dataset,
   compute Sharpe/CAGR/MDD/corr/Markowitz residual, persist
   `returns_series` per dataset per cfg + `subcomponent_returns`.
5. **`compute_gates_and_score.py`**:
   - G1 PBO: 7-cfg CSCV grid per dataset
   - G2 DSR: per-dataset cumulative n_trials = 4381
   - G3 WF: 8 walk-forward windows per dataset, MDD<25%, 6/8 pass
   - G4 OOS: 70/30 split, Sharpe>0
   - G5 FWD: post-2020-01-01 stress, Sharpe>0
   - G6 Bootstrap: 1000 resamples × 99.9% CI, low > 0
   - G7 Cross-lib: pandas vs numpy reference, ±3pp CAGR
   - Apply rolling-window robustness (3-window per dataset, 9 windows total)
   - Pick top cfg by composite (cross-dataset min-Sharpe), score it
6. **Plots**: invoke `plot_helper.py --iter 074`
7. **Report + memory**: write `final_report.md`, update `BASE_MEMORY.md`,
   append to `DEAD_ENDS.md` if new structural closure.

## Structural novelty check vs DEAD_ENDS.md

- **iter 045 (iter 037 + iter 039 saved-stream-pair)**: closed at 81 ceiling.
  Iter 074 uses a different anchor pair — iter 016 is a vol-managed
  stock-bond stack with NO equivalent in iter 037 (which was a static
  3-leg SPY+IEF+GLD with no vol-mgmt). ✅ structurally distinct.
- **iter 046 (iter 041 + iter 039 saved-stream-pair)**: same as 045
  but with iter_041 as anchor. Iter 074's iter 016 leg is again
  qualitatively different (no regime gate, has vol-target). ✅ distinct.
- **iter 058 (iter 046 + HYG_TSM)**: differs by 3rd-stream identity
  (HYG vs iter 016). HYG_TSM was a pure single-asset credit-trend filter;
  iter 016 is a 2-leg SPY+IEF + vol-target dynamic. ✅ distinct.
- **iter 064 (iter 046 + QQQ_TREND)**: differs by 3rd-stream identity
  (QQQ vs iter 016). QQQ_TREND is a pure single-asset equity-trend
  filter; iter 016 is a dynamic stock-bond stack. ✅ distinct.
- **iter 047-053 closed saved-stream-pair axes**: those tested
  iter_037+iter_026, iter_041+iter_026, iter_037+iter_046 — all share
  iter_026 or iter_046 as one leg. Iter 074 has neither iter_026 nor
  uses iter_046 directly (only via iter_064's saved stream). ✅ distinct.
- **Iter 073 (Gayed-MA-gate on iter 016)**: tested an OVERLAY on iter
  016, not an ENSEMBLE with another saved stream. ✅ distinct.

**Novelty relative to closest neighbours**: iter 074 is the **first**
saved-stream-pair to use **iter 016's vol-managed 2-leg stock-bond
stack** as a leg. All prior saved-stream pairs used static-stack legs
(iter 037/041) or VRP-basket legs (iter 039). The vol-managed leg is
qualitatively a different family. ✅ structurally novel.
