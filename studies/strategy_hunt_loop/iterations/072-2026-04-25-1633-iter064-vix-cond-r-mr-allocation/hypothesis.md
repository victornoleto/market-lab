# Iteration 072 — VIX-conditional allocation of validated calm-aggressive r_mr on iter 064 base

## Hypothesis

iter 071 closed the **calm-aggressive 3rd-stream axis on iter 064** at 90 STRONG ceiling (4-way TOP-K #1 with iter 064/069/070). The empirical evidence vindicated the structural thesis (KILL D clean: r_mr conditional Sharpe calm 0.82-0.93 vs stress 0.32-0.70 on 3/3 datasets) but the static blend hit a Pareto trade-off: small w_mr=0.05 lifts Sharpe under +0.02 (KILL A fired), while moderate w_mr=0.10 lifts Sharpe by +0.025-0.033 but breaks edu CAGR floor (KILL H, score 85).

**Iter 072 hypothesis:** Replacing the static w_mr with a **VIX-binary regime-conditional allocation** (w_mr_calm > 0, w_mr_stress = 0) extracts the calm-regime portion of r_mr's Sharpe contribution while avoiding the stress-regime CAGR dilution. The composition activates the validated calm-aggressive stream only in the regime where its conditional Sharpe is statistically dominant (calm > stress on 3/3 ds confirmed in iter 071).

```
gate_stress[t] = (VIX[t-1] >= 20)                       # Whaley 2009 long-run median
w_mr[t]    = w_mr_stress if gate_stress[t] else w_mr_calm
w_046[t]   = (1 - w_mr[t]) * 0.90                       # preserve iter 064 9:1 ratio
w_qqqt[t]  = (1 - w_mr[t]) * 0.10
cost[t]    = cost_bps * 1e-4 * |w_mr[t] - w_mr[t-1]|    # flip cost on regime change
r_072[t]   = w_046[t]·r_046[t] + w_qqqt[t]·r_qqqt[t]
             + w_mr[t]·r_mr[t] - cost[t]
```

This is structurally distinct from prior iterations:

* iter 064: STATIC 2-stream (90% r_046 + 10% r_qqqt), no regime
* iter 069: regime classifier modulating INNER weight BETWEEN iter 064 sub-streams (r_046 ↔ r_qqqt)
* iter 070: continuous T10Y3M z-score modulating INNER weights (same axis as 069, different classifier)
* iter 071: STATIC adding of r_mr as 3rd stream (no regime)
* **iter 072: regime classifier modulating the 3rd-stream WEIGHT (composes iter 069's classifier with iter 071's validated r_mr) — hierarchical regime allocation**

The expected behaviour: in calm regime (~70% of time), w_mr=w_mr_calm captures the high calm-Sharpe; in stress regime (~30%), w_mr=w_mr_stress (typically 0) collapses the composition to iter 064 base — fully defensive. The mechanism is the literal "extract the calm portion of r_mr without the stress drag."

## Primary citation

`[algo_trading_chan, p.95, p.153-154]` — Chan: momentum filter on mean-reversion entry + mean-reversion + momentum complementarity in regime-based portfolio allocation. The Chan p.153-154 thesis is exactly hierarchical: when the momentum trend is intact (calm regime), allocate to mean-reversion; when the momentum breaks (stress), withdraw to defensive. iter 072 implements this verbatim with a VIX-binary classifier.

## Additional citations

- Whaley, R. E. (2009). "Understanding the VIX." *Journal of Portfolio Management*, 35(3): 98-105. DOI 10.3905/JPM.2009.35.3.098 — VIX threshold = 20 (long-run median); ex-ante regime gate.
- Bekaert, G., & Hoerova, M. (2014). "The VIX, the variance premium and stock market volatility." *Journal of Econometrics*, 183(2): 181-192. SSRN 2294327 — VIX as risk-aversion + uncertainty proxy; structural justification for regime conditioning of risk-on streams.
- Connors, L., & Alvarez, C. (2009). *Short Term Trading Strategies That Work*. ISBN 978-0-9755513-2-7. Connors-Alvarez also describe a **VIX-percentile timing rule** for RSI(2) entries — direct precedent for VIX-conditioning a Connors-style mean-reversion stream.
- Lo, A. W., & MacKinlay, A. C. (1988). "Stock Market Prices Do Not Follow Random Walks." *Review of Financial Studies*, 1(1): 41-66. DOI 10.1093/rfs/1.1.41 — empirical short-horizon mean-reversion underlying r_mr's edge.
- Moskowitz, T., Ooi, Y. H., & Pedersen, L. H. (2012). "Time series momentum." *Journal of Financial Economics*, 104(2): 228-250. DOI 10.1016/j.jfineco.2011.11.003 — TSM regime conditionality; supports regime-aware allocation logic.
- `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base preserved verbatim (saved return stream).
- Faber (2007), SSRN 962461 + `[stocks_on_the_move, p.21-30]` — Faber QQQ-200d-trend preserved verbatim (computed from QQQ via iter 064 module).
- `[advances_fin_ml, ch.17-18]` — regime detection / structural breaks.
- `[advances_fin_ml, p.162-164]` — strict shift(1) on VIX (BOTH VIX and RSI/SMA at t-1).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 4348.
- `[advances_fin_ml, p.31-34]` — G7 cross-lib parity (numpy reference).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV gate G1.
- iter 064/069/070/071 final reports — TOP-K #1 baselines + structural diagnoses.

## Edge source

SPY 1x buy-hold misses the **calm-regime, daily-oversold mean-reversion bounce** — a structural pattern documented by Connors-Alvarez (2009) and Lo-MacKinlay (1988). iter 071 verified this stream exists in r_mr (calm Sharpe 0.82-0.93 cross 3 ds) but SPY buy-hold captures it as undifferentiated trend + noise. iter 072 isolates ONLY the calm-regime portion via a triple-gate (VIX<20 risk-aversion + SPY>200d-SMA momentum + RSI2<10 dip), avoiding both the stress-regime drag and the buy-hold dilution.

## Datasets

- **educational** (SPYSIM synth 40y, 2006-2026): the longest history. iter 064 base saturates here at edu Sharpe 1.20 / CAGR 9.49% / MDD 17%. The CAGR-Sharpe Pareto front is most binding here (KILL H boundary). Target: edu CAGR ≥ 9.18% AND Sharpe lift ≥ +0.02 vs iter 064.
- **spy_real** (Tiingo SPY 2009-06-25 → 2026-04-15): the canonical real-data validation set. iter 064 saturates at Sharpe 1.33 / CAGR 9.97% / MDD 15%. CAGR floor 11.98% is unmet by all 4-way TIES; not a kill criterion this iter (CAGR floor failure is invariant under composition). Target: Sharpe lift ≥ +0.02 vs iter 064.
- **ndx_real** (Tiingo QQQ 2010-02-12 → 2026-04-15): NDX-tracking validation. iter 064 saturates at Sharpe 1.38 / CAGR 10.17% / MDD 15%. Same CAGR-floor invariance as spy_real. Target: Sharpe lift ≥ +0.02 vs iter 064.

Cross-dataset Sharpe lift on ≥ 2 of 3 ds is the binding gate.

## Kill criteria (pre-committed)

| # | criterion | threshold | rationale |
|---|---|---|---|
| **A** | **Δ064 Sharpe < +0.02 on ≥ 2 ds** | best cfg | the binding criterion — iter 071's KILL A; if regime-conditioning fails to clear it, the 90 ceiling is hard-anchored in the iter 046 base regardless of structural ingredient. |
| B | edu CAGR < 9.18% on best cfg | iter 064 unlock | preserve the non-LETF unlock (iter 071 KILL H equivalent). |
| C | Δ071_th10w005 Sharpe < +0.005 on ≥ 2 ds | mechanism efficacy | regime-conditioning must amplify ABOVE iter 071's static — otherwise dynamic allocation is no better than static at average w. |
| D | corr(072, 064_static) > 0.99 on ≥ 2 ds | structural inertness | regime-conditioning must lift the portfolio path enough to be visible. |
| E | conditional ratio (calm_S/stress_S) of r_072 < 1.3 on ≥ 2 ds | regime mechanism check | confirms the composition's regime-conditional structure is operative (not dampened by base). |
| F | PBO grid-level > 0.5 on any ds | overfit gate | usual G1; with 4 cfgs PBO should be low. |
| G | DSR worst p > 0.05 at cumulative_n_trials = 4348 | usual G2 | DSR with cumulative penalty. |
| H | G7 cross-lib > 0.5 pp on any ds | engine integrity | mandatory if new combiner module — must be < 0.5 pp absolute. |
| I | r_mr cond ratio (calm_S/stress_S) < 1.5 on ≥ 2 ds | r_mr structural sanity | confirms iter 071's KILL D vindication still holds (stream still calm-aggressive). |
| J | Score < 75 (drops below STRONG) | safety regression check | don't crash to PROMISING from 90. |

**Kill A is the headline.** If iter 072 also fires KILL A on ≥ 2 ds, the 90 ceiling is provably structural in the iter 046 base — no further composition on this anchor is worth attempting, and direction #2 (fresh higher-CAGR anchor, 5+ iter cost) is the ONLY remaining lever.

## Expected budget

- **Configs to test**: 4 (small grid, deliberate to control PBO and n_trials inflation; reuses iter 071's RSI threshold = 10 best cfg; sweeps w_mr_calm and w_mr_stress only).
- **Wall-time**: ~75-90 min (engine reuse: r_046 saved, r_qqqt module reused, r_mr module reused; only the new 3-stream regime-conditional combiner is added).
- **Files to create**:
  - `regime_conditional_3leg.py` — new combiner module
  - `numpy_reference_iter072.py` — cross-lib reference for the new combiner
  - `tests/test_regime_conditional_3leg.py` — 12-15 TDD tests (weight invariants, no-peek shift(1), regime-conditional flip cost, w_mr_stress=0 collapse to iter 064 base, sum-to-1 invariant, w_mr_calm=w_mr_stress collapse to iter 071 static)
  - `run_backtests.py` — 3-dataset × 4-cfg orchestration (mirrors iter 071 pattern, adds VIX loading)
  - `compute_gates_and_score.py` — gate battery + scoring orchestration
  - `final_report.md` + `verdict.json` + `plot_vs_benchmark_*.png`
- **cumulative_n_trials**: 4344 + 4 = **4348**.

## Implementation plan

1. **TDD tests first** — write `tests/test_regime_conditional_3leg.py` with 12+ tests:
   - `test_combine_w_mr_stress_eq_w_mr_calm_recovers_iter071_static` — when w_mr_calm = w_mr_stress, output ≡ iter 071 static blend.
   - `test_combine_w_mr_stress_eq_zero_collapses_in_stress` — when stress regime active and w_mr_stress=0, w_046 = 0.90, w_qqqt = 0.10 (iter 064 base) on those bars.
   - `test_no_peek_vix_uses_lagged` — VIX[t-1] determines weights at t (strict shift(1)).
   - `test_weight_sum_invariant` — w_046 + w_qqqt + w_mr ≡ 1.0 every bar.
   - `test_iter064_recovery_w_mr_calm_eq_zero` — when w_mr_calm = w_mr_stress = 0, output exactly equals iter 064 static (90% r_046 + 10% r_qqqt — no MR).
   - `test_flip_cost_charged_on_regime_transition` — cost > 0 only on bars where w_mr changes (i.e., regime transitions).
   - `test_zero_cost_in_constant_regime` — if VIX never crosses threshold, total cost = 0.
   - `test_inner_join_index` — output index is intersection of r_046, r_qqqt, r_mr indices.
   - `test_value_error_on_negative_weight` — raises on w_mr_calm < 0 etc.
   - `test_value_error_on_w_mr_calm_above_one` — raises on w_mr_calm > 1.
   - `test_diagnostics_attach` — return_diagnostics=True attaches arrays.
   - `test_vix_alignment_ffill_bfill` — VIX missing days handled properly.

2. **Combiner module** `regime_conditional_3leg.py`:
   - One function `combine_regime_cond_3leg(r_046, r_qqqt, r_mr, vix, *, w_mr_calm, w_mr_stress, vix_threshold=20.0, cost_bps=5.0, return_diagnostics=False)`.
   - Mirrors iter 068's `combine_with_vix_inner_weight` pattern but operates on 3 streams instead of 2.
   - VIX shift(1) + bfill (same convention as iter 068/069).

3. **Numpy reference** `numpy_reference_iter072.py`:
   - Pure-numpy implementation of the same combiner (no pandas index ops; pre-aligned arrays only).
   - G7 parity check: max abs return diff < 1e-10 expected (engine is just weighted-sum + cost, deterministic).

4. **run_backtests.py**:
   - Reuse iter 071's r_046 loading, r_qqqt computation, r_mr computation.
   - Add VIX loading (from `data/external/macro/vix.parquet`; reuse iter 068/069 loading pattern).
   - 4 cfgs:
     - cfg1 `iter064_vix_cond_calm010_stress000` — primary: w_calm=0.10, w_stress=0.00
     - cfg2 `iter064_vix_cond_calm015_stress000` — aggressive calm
     - cfg3 `iter064_vix_cond_calm010_stress005` — partial stress preservation
     - cfg4 `iter064_vix_cond_calm020_stress000` — most aggressive
   - All cfgs fix RSI threshold = 10 (iter 071 best); vix_threshold = 20.0; cost_bps = 5.0.
   - Compute combined Sharpe / CAGR / MDD; conditional Sharpe (calm vs stress); corr(072, iter064_static); corr(072, iter071_static).
   - G7 cross-lib parity per cfg.

5. **compute_gates_and_score.py**:
   - Run all 7 gates (G1-G7) per cfg per dataset.
   - PBO via CSCV across the 4 cfgs (per dataset, grid-level).
   - DSR per dataset with `cumulative_n_trials=4348`.
   - WF 8-window per cfg.
   - OOS 70/30 + FWD post-2020.
   - Bootstrap 99.9% CI low > 0 (mean-shift bootstrap with 5000 resamples).
   - Robustness 9 sub-windows (1.875y each across 17y window).
   - Score via `scoring.py` for each cfg; pick best by composite (highest min-Sharpe across 3 ds; tiebreak by Sharpe-sum).

6. **final_report + verdict + plot + memory updates** — per Stage 5 spec.

**Acceptance for STAGE 3 success**: all TDD tests pass, G7 cross-lib < 0.5 pp on 3/3 ds, results.json with `returns_series` populated, gate battery produces evaluable metrics. **Acceptance for promotion to STRONG/WINNER tier**: KILL A clears (Sharpe lift ≥ +0.02 on ≥ 2 ds vs iter 064) AND KILL B clean (edu CAGR ≥ 9.18%) AND KILL C clears (Sharpe lift ≥ +0.005 on ≥ 2 ds vs iter 071 static).

**Falsification path**: if KILL A fires, this confirms the 90 ceiling is hard-anchored in iter 046 base composition — final report recommends pivoting to direction #2 (fresh higher-CAGR anchor) for iter 073+.
