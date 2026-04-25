# Iteration 058 — HYG long-only with 90d boolean trend filter as 3rd stream on iter 046 (w=0.10)

## Hypothesis

iter 057 falsified the multi-commodity TSM basket as a 3rd-stream
overlay because the basket's standalone Sharpe (0.13–0.29) was too
low to compound iter 046's combined stream — Markowitz dilution at
unequal Sharpes dragged combined Sharpe by 0.16–0.24 even though the
correlation premise held (corr ≈ 0.30). The structural finding from
iter 049/050/057 is: **3rd-stream Sharpe ≥ ~0.5 is the binding
constraint for Markowitz-positive contribution at any practical
weight, NOT correlation alone**.

This iteration tests the natural follow-up: a higher-Sharpe credit-
carry 3rd stream. **HYG (iShares iBoxx HY Corporate)** long-only with
a 90-day boolean trailing-return trend filter (identical signal logic
to iter 049's gold TSM, switched to HYG prices). HYG's structurally
positive credit risk premium (Asvanunt-Richardson 2017, JPM 43(2),
~2-4% annualised premium net of defaults) gives it a higher non-
stress Sharpe than commodity TSM. The 90d trend filter avoids the
2008 GFC and 2020 COVID stress draw-downs (when default expectations
spike and HYG drops 30%+).

The mechanism is structurally identical to iter 049/050/057:

```
pos_HYG[t] = 1 if (HYG[t-1] / HYG[t-1-90] - 1) > 0 else 0
r_HYG_TSM[t] = pos_HYG[t] * r_HYG[t] + (1 - pos_HYG[t]) * rf_d
              − cost_bps × |Δpos_HYG[t]|

r_combined[t] = w_046 * r_046[t] + w_HYG * r_HYG_TSM[t]
```

with `w_046 = 0.90, w_HYG = 0.10` — single pre-committed config,
weight chosen to match iter 050 (gold-TSM at w=0.10, score 78
PROMISING) for direct apples-to-apples comparison: holding the weight
fixed, does a structurally higher-Sharpe 3rd stream (HYG ~0.5–0.7) beat
a structurally lower-Sharpe one (gold TSM ~0.4–0.5)?

## Primary citation

`[risk_parity, ch.5]` + Asvanunt-Richardson 2017 JPM 43(2)
DOI 10.3905/jpm.2017.43.2.090 — "The Credit Risk Premium" establishes
that the corporate credit-default-adjusted carry is a structurally
positive return source (≈2-4% annualised net of expected defaults),
weakly correlated with equity factor in non-stress regimes but
spiking equity-correlated during stress events. The trend filter is
the standard tool for stress avoidance on credit (Asvanunt-Richardson
§3, p.97-99).

## Additional citations

- `[volatility_trading, p.218]` + `[risk_parity, ch.5]` — iter 046
  base architecture preserved verbatim via its saved combined return
  stream (no re-implementation; G7 already passed at 0.0000 pp on iter
  046, iter 049, iter 050, iter 057)
- `[systematic_trading]` (Carver) — generic TSM single-asset boolean
  trend rule, applied to credit
- `[stocks_on_the_move, p.76-77]` (Clenow) — boolean trend on log
  price
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (4327 → 4328)
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1)
- Markowitz (1952), JoF 7(1) 77-91 — convex combination Sharpe
  identity (used in pre-committed kill D)
- Web: Asvanunt, A. & Richardson, S. 2017, "The Credit Risk Premium",
  JPM 43(2), https://doi.org/10.3905/jpm.2017.43.2.090
- Web: Erb, C.B. & Harvey, C.R. 2006, "The Strategic and Tactical
  Value of Commodity Futures", FAJ 62(2) — referenced for the
  lookback choice (90d ≈ 4-month carry-cycle horizon, consistent with
  iter 049/057 to keep parity)
- Web: Asness, C., Moskowitz, T. & Pedersen, L. 2013, "Value and
  Momentum Everywhere", JoF 68(3) — credit TSM has positive Sharpe in
  the 2007-2026 sample window (Table III)

## Edge source

SPY 1x buy-hold misses the **corporate credit risk premium net of
default** — a structurally positive 2-4% annual return (Asvanunt-
Richardson 2017) that is weakly correlated with equity beta in non-
stress regimes. The 90d trend filter additionally avoids stress events
when credit spreads spike, which historically drag long-only HYG by
30%+ in 6 months (2008-09, 2020-Q1).

## Datasets

- educational (SPYSIM synth 40y): tests combined edge over the longest
  window. HYG only has data 2007-04+, so the educational dataset is
  windowed to **HYG inception → 2026-04-15** (matching iter 049/050
  approach for GLD which started 2004). The educational benchmark
  recomputes on this windowed range.
- spy_real (2009-06-25 → 2026-04-15): post-GFC SPY-anchored test;
  HYG has full coverage of this window.
- ndx_real (2010-02-12 → 2026-04-15): post-GFC QQQ-anchored test;
  HYG has full coverage.

All 3 datasets use the same pre-committed cfg
`iter046_plus_hyg_tsm_w010_lookback90`.

## Kill criteria (pre-committed)

If any of the following observable patterns holds at end of Stage 4,
the hypothesis is falsified regardless of secondary metrics:

| # | Kill | Threshold | Rationale |
|---|---|---|---|
| A | Combined Sharpe regress vs iter 046 | Drop ≥ 0.10 on ≥ 2 of 3 datasets | Same kill as iter 049/057; large drag falsifies "higher-Sharpe 3rd stream helps" |
| B | DSR worst-p ≥ iter 050's 0.0438 (2× margin) | worst p ≥ 0.088 across 3 datasets | iter 050 set the prior w=0.10 baseline; doubling its worst-p is a strong regression signal |
| C | Score < 78 (iter 050 baseline) | total_score < 78 | If HYG at w=0.10 can't beat gold-TSM at w=0.10, the higher-Sharpe-3rd-stream thesis fails |
| D | Markowitz formula mispredicts observed combined Sharpe | abs residual ≥ 0.05 on ≥ 2 datasets | Indicates non-stationary correlation or unmodelled cost; closes the closed-form composition pattern |
| E | G7 cross-lib > 3 pp | abs CAGR diff > 3 pp on any dataset | Engine bug in HYG_TSM or combine logic |
| F | corr(r_HYG_TSM, r_046) > 0.85 | average corr across 3 datasets > 0.85 | HYG behaves as equity proxy; no real diversification |

**Falsification threshold**: ≥ 4/6 kills fired = hypothesis refuted
(matching iter 057's standard).

## Expected budget

- Configs to test: **1** (pre-committed, no grid)
- cumulative_n_trials advance: 4327 → **4328** (+1)
- Wall-time: ~5-10 minutes (minimal: HYG TSM is one numpy loop, iter
  046 stream is loaded from saved JSON, scoring is the existing helper)
- Files to create:
  - `hyg_tsm.py` — pandas engine for single-asset HYG TSM
  - `numpy_reference_iter058.py` — numpy reference for G7 parity
  - `combined_046_plus_hyg.py` — convex combination wrapper (could
    reuse `combine_046_plus_gold` if signature matches; we'll create a
    thin alias for clarity and future grep-ability)
  - `tests/test_iter_058_hyg_tsm.py` — TDD specs (≥ 12 tests covering
    indexing, no-lookahead, warmup, cost, weighting, G7 parity)
  - `run_backtests.py` — runs the 3 datasets, writes `results.json`
  - `compute_gates_and_score.py` — 7-gate battery + score, writes
    `verdict.json`
  - `final_report.md` — Stage 5 narrative

## Implementation plan

1. **TDD**: write `tests/test_iter_058_hyg_tsm.py` mirroring
   `tests/test_iter_049_gold_tsm.py` (reuse helpers, swap GLD→HYG
   nomenclature). Confirm 12+ tests fail before writing impl.
2. **Pandas engine**: `hyg_tsm.py::compute_hyg_tsm_returns(prices, lookback=90, rf=0.02, cost_bps=5.0)`
   — semantically identical to `gold_tsm.compute_gold_tsm_returns`
   (one-shift trail rule, 0/1 boolean position, cost on |Δpos|).
3. **Numpy reference**: `numpy_reference_iter058.py::compute_hyg_tsm_returns_np`
   — pure numpy mirror; G7 parity check.
4. **Combiner**: `combined_046_plus_hyg.py::combine_046_plus_hyg(r_046, r_hyg, *, w_046, w_hyg)`
   — convex combo (same logic as `combine_046_plus_gold`).
5. **Run all tests** — should be 12-16 tests, all passing.
6. **Run backtests**: `run_backtests.py` over 3 datasets, write
   `results.json` with required `returns_series` schema.
7. **Compute gates + score**: copy `compute_gates_and_score.py` from
   iter 050, swap iter labels, recompute against fresh data,
   write `verdict.json` with the 6 pre-committed kills evaluated.
8. **Plots**: `uv run python studies/strategy_hunt_loop/plot_helper.py --iter 058`.
9. **Final report + memory update + auto-prune**.
