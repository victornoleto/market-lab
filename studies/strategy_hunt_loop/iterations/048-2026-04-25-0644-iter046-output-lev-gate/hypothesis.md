# Iteration 048 — VIX-regime OUTPUT leverage gate on iter 046 combined stream

## Hypothesis

iter 046 (the current TOP-K #1 at score 85, 50/50 convex combo of iter 041
regime-gated stack + iter 039 cross-asset VRP basket) trails the WINNER
threshold by exactly 5 points on the **CAGR floor** axis (0/15 — edu
9.16% vs floor 9.18%, spy 9.45% vs 11.98%, ndx 9.76% vs 15.35%).
iter 047 just CLOSED weight asymmetry as a CAGR-recovery mechanism
(Bonferroni cost of N=3 grids > Pareto-frontier gain).

**iter 048 tests a structurally distinct mechanism**: apply a **binary
VIX-regime LEVERAGE multiplier to the COMBINED output stream** (not to
the inputs):

```
r_iter048[t] = lev[t] * r_iter046[t]

where lev[t] = 1.4 if VIX[t-1] < 20.0
              1.0 if VIX[t-1] ≥ 20.0
```

This preserves iter 046's components verbatim, treats the combined stream
as a single asset, and applies an external regime-modulated multiplier.
The mechanism is structurally new in the loop — every prior regime-gated
strategy (iter 041 / 043 / 044) modulated **input** weights inside the
stack; every prior leverage gate (iter 038) acted on a single static
stack, not on a 2-component composite output.

**Why it should work**: in calm regimes (~70% of trading bars 2009-2026)
SPY's expected return is positive AND iter 046's volatility is low (the
50/50 averaging keeps σ_combined ≈ 7%). A 1.4× multiplier on calm bars
adds ≈ 0.4 × 7% × 0.7 ≈ +2pp annualised CAGR while only adding
≈ 0.4 × 7% ≈ +2.8pp annualised vol on those bars. On stress bars (VIX≥20,
~30% of history), keeping lev=1.0 avoids amplifying the drawdown tails
that iter 046 already absorbs via iter 041's regime-shift to bonds+gold.

**Predicted CAGR uplift** (envelope, not promise):
- iter 046 has CAGR ≈ 9.2% (edu) / 9.5% (spy) / 9.8% (ndx).
- ~70% calm × 1.4 + ~30% stress × 1.0 ≈ 1.28× CAGR weighting.
- Predicted iter 048 CAGR ≈ 11.7% (edu, clears 9.18 floor) / 12.1% (spy,
  clears 11.98 floor by ~0.1pp) / 12.5% (ndx, **still misses** 15.35 floor).

If realised, edu+spy clear → 2/3 datasets pass cond #4 (CAGR floor) → +10pp
on criterion 4 → total score 85 → 95 → tier 🏆 WINNER (subject to all
other gates holding).

If DSR regresses (the iter 044 risk: gate enrichment costs DSR), score
drops because criterion 3 falls from 15 → 10 (or 5). The kill criteria
below pre-commit the threshold.

**This is a SINGLE pre-committed cfg (N=1) — no grid, no sweep.**
cumulative_n_trials advances 4314 → 4315 (+1). Bonferroni penalty does
not apply. iter 047's lesson is honoured: keep N=1 in iter 046-base
research.

## Primary citation

`[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack
architecture (iter 041 component preserved verbatim; iter 046's static
50/50 scaffolding preserved verbatim).

## Additional citations

- `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching;
  binary VIX gate is a degenerate 2-state HMM with VIX as observed.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
  N=1 pre-commit avoids Bonferroni cost (iter 047's lesson).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.162-164]` — no-lookahead lag rule; `lev[t]` uses
  `VIX[t-1]` (already computed at t-1 close).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (single cfg → not gating
  factor; G1 reported but uninformative at N=1).
- `[volatility_trading, p.218]` — Sinclair (2013) on cross-asset VRP
  harvesting (iter 039 base, preserved verbatim).
- Whaley (2009), JPM 35(3) 98-105, DOI 10.3905/JPM.2009.35.3.098 —
  VIX as ex-ante risk regime indicator; threshold 20 = long-run median.
- Bekaert-Hoerova (2014), J Econometrics 183(2) 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition; the
  level-20 threshold separates calm (risk-aversion baseline) from
  stress (uncertainty-driven spikes).
- Markowitz (1952), JoF 7(1) 77-91 — convex combination architecture
  preserved (the leverage acts on the COMBINED stream, not on weights).

Web: no new arxiv/SSRN reference required; mechanism is a direct
recombination of cited primitives.

## Edge source

SPY 1x buy-hold compounds returns un-levered through both regimes;
iter 046's 50/50 scaffold halves the equity-leg's compounding (because
half the capital is in iter 039's T-bill-collateralised VRP harvest).
A regime-conditional output multiplier captures the equity premium on
calm bars without amplifying stress-bar drawdowns. SPY does NOT
modulate exposure with VIX; iter 048 does.

## Datasets

- **educational** (SPY+IEF+GLD 2006-2026 inner-join, ~5101 bars):
  20y combined; iter 041 stack + iter 039 basket; covers 2008+2020+2022
  stress regimes for the leverage gate's calm/stress regime to fire on.
- **spy_real** (2009-06-25 → 2026-04-15, ~4226 bars): 17y post-GFC
  combined; bench SPY; the principal real-data validation window.
- **ndx_real** (2010-02-12 → 2026-04-15, ~4066 bars): 16y; bench QQQ;
  iter 041 stack on SPY + iter 039 basket SPY/QQQ/IWM. Higher SPY-Sharpe
  bench tests robustness of the calm-leverage thesis cross-bench.

VIX[t-1] is the same series used by iter 041's regime gate (already
loaded + ffill/bfill aligned). Threshold 20.0 matches iter 041's
calm/stress dividing line — preserves consistency with the base.

## Kill criteria (pre-committed)

| kill | trigger | rationale |
|---|---|---|
| **A** | Sharpe regress vs iter 046 by ≥ 0.05 on ≥ 2 of 3 datasets | output-leverage destructively interferes with composition |
| **B** | DSR worst-p > iter 046's 0.0414 on educational | gate enrichment regresses DSR (iter 044 closure pattern reappears at output level) |
| **C** | MDD breach (> bench + 5pp) on any dataset | leverage amplifies drawdowns past the iter 032 risk threshold |
| **D** | Score < iter 046's 85 | output-leverage adds nothing (regression vs the unmodified base) |
| **E** | G7 cross-lib > 3 pp | engine bug; pure-numpy reference must agree to ±3pp CAGR |
| **F** | CAGR uplift < +2pp on ≥ 2 of 3 datasets | predicted edge does not materialise; thesis falsified |

Any of A/B/C/E firing → kill. D firing → strict regression, treat as
FAIL. F firing → mechanism does not deliver the CAGR-floor premise →
add to DEAD_ENDS. Single dataset breach on any kill (other than C, which
is per-dataset) is informational only.

## Expected budget

- Configs to test: **1** (single pre-committed cfg with calm 1.4 / stress 1.0
  at VIX threshold 20.0).
- Wall-time: ≤ 30 minutes (reuses iter 046's engine via direct import; the
  output-gate is a single multiplicative step on the existing return series).
- Files to create:
  - `output_lev_gate.py` — the multiplicative gate function (small).
  - `numpy_reference_iter048.py` — pure-numpy reference for G7.
  - `run_backtests.py` — single-cfg driver across 3 datasets.
  - `compute_gates_and_score.py` — gates + scoring + kill evaluation.
  - `tests/test_iter_048_output_lev_gate.py` — TDD specs.
  - `results.json`, `verdict.json`, `final_report.md`.
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.

## Implementation plan

1. **Tests first** (`tests/test_iter_048_output_lev_gate.py`):
   - Identity reduction: `lev_calm = lev_stress = 1.0` → output equals
     input (combined returns unchanged).
   - Lookahead causality: gate at bar `t` uses `vix[t-1]` not `vix[t]`.
   - Calm regime arithmetic: when all bars have `vix[t-1] < 20`, output
     equals `1.4 * combined` exactly.
   - Stress regime arithmetic: when all bars have `vix[t-1] ≥ 20`,
     output equals `combined` (lev_stress=1.0 default).
   - Threshold ordering: `lev_calm` and `lev_stress` are independently
     specified (not assumed `lev_calm > lev_stress`).
   - Cross-lib parity: numpy reference equals pandas to 1e-9 per-bar.
   - Index preservation: output index equals combined input index.
   - Empty/single-bar input raises ValueError.

2. **Engine** (`output_lev_gate.py`): single function
   `apply_output_lev_gate(combined, vix, lev_calm=1.4, lev_stress=1.0,
   vix_threshold=20.0)` taking iter 046's combined return Series and a
   VIX series (same length or reindexable), shifting `vix.shift(1)` for
   no-lookahead, and returning `lev * combined` element-wise. Cost
   bps not modelled (output-gate has no transaction cost beyond the
   one already inside iter 046's combined; multiplying a return stream
   does not generate trades, only re-scales position size at session
   close which is captured by treating each day's gross-of-cost return
   as already net).

3. **Numpy reference** (`numpy_reference_iter048.py`): same logic in
   pure numpy on `np.ndarray` inputs. Used by G7 cross-lib gate.

4. **Driver** (`run_backtests.py`): for each of 3 datasets:
   - Load SPY/IEF/GLD/QQQ/IWM prices + VIX (verbatim from iter 046's
     `run_backtests.py`).
   - Compute iter 046's combined stream (call iter 046 engine directly).
   - Apply `apply_output_lev_gate` with single pre-committed cfg.
   - Compute Sharpe, CAGR, MDD, corr_combined_spy, corr to base iter 046.
   - Compute G7 cross-lib parity (pandas vs numpy CAGR Δ).
   - Save returns_series + subcomponent (iter 046 base, lev arr).

5. **Gates + score** (`compute_gates_and_score.py`): re-use iter 046's
   `compute_gates_and_score.py` template:
   - G1 PBO (1-cfg → reported as N/A or 0; non-gating).
   - G2 DSR with cumulative n_trials = 4315 (4314 + 1).
   - G3 WF 8-window, MDD < 25% per window.
   - G4 OOS 70/30 Sharpe > 0.
   - G5 FWD post-2020 Sharpe > 0.
   - G6 Bootstrap 99.9% CI low > 0 (block bootstrap, 1000 reps).
   - G7 Cross-lib ≤ 3pp CAGR (already from driver).
   - Score via `scoring.score_strategy(...)`; bonus +5 if all 3
     sub-window Sharpe > 0 in 3-fold split.

6. **Final report** (`final_report.md`): score breakdown, headline
   table, kill status, lessons, citations.

7. **Plots** (`plot_vs_benchmark_spy_real.png`,
   `plot_vs_benchmark_ndx_real.png`) via
   `studies/strategy_hunt_loop/plot_helper.py --iter 048`.

8. **Update BASE_MEMORY**: bump iter count to 48, cumulative_n_trials
   4314 → 4315; insert top-K row if score warrants; append iteration
   log entry; auto-prune if file > 18 KB.
