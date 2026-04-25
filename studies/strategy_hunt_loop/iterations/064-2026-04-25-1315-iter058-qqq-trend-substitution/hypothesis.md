# Iteration 064 — QQQ-200d-trend substitution for HYG_TSM in iter 058 anchor

## Hypothesis

Replace iter 058's HYG_TSM 3rd stream (long-only credit-carry trend) with
**QQQ-200d-trend** (long-only Nasdaq trend filter, Faber 2007 TAA): hold
QQQ when its close > 200d SMA at end of t-1, else hold T-bill (rf=0).
Cost 5 bps per signal flip.

The combined construction is identical to iter 058 in shape:

```
iter 058:  0.90 · iter_046 + 0.10 · HYG_TSM(L=90)
iter 064:  0.90 · iter_046 + 0.10 · QQQ_TREND(SMA=200)
```

The thesis: HYG_TSM had Sharpe ~0.99 but CAGR only ~4.85% — making it
**Sharpe-additive but CAGR-dilutive**. The iter 058 family's binding
constraint is the **CAGR floor (0/3)**, not Sharpe. QQQ-200d-trend has
standalone Sharpe ~0.80 (lower) but CAGR ~12-14% (much higher), making
it **CAGR-additive**. Trading a small amount of Sharpe (combined drag
~−0.02 per pre-val) for a large CAGR uplift (~+0.7-0.9 pp per pre-val)
should unlock the educational CAGR floor (9.18%) for the first time on
the iter 058 family **without** the internal-LETF substitution that
iter 063 used (which fired kill A on 3/3 datasets).

## Primary citation

`[stocks_on_the_move, p.21-30]` — Clenow's Channel-Index/200-day filter
for trend regime detection on equity universes; the SMA filter excludes
stocks below the trend regime to avoid bear-market participation.
The exact construction here (binary regime gate via 200-day SMA on a
single asset) is the **Faber 2007 TAA primitive** that Clenow extends.

## Additional citations

- **Faber (2007)** — Mebane Faber, *A Quantitative Approach to Tactical
  Asset Allocation*, SSRN 962461 (J. Wealth Mgmt 2007). Foundational
  paper for single-asset 200-day SMA trend filter. Reports Sharpe ~0.7-0.8
  on US equities with MDD reduction from ~50% to ~25% over 1972-2005.
- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen (2012) SSRN 1728082;
  preserved verbatim via iter_046 saved stream (the 90% anchor).
- `[volatility_trading, p.218]` — Sinclair (2013); preserved verbatim
  via iter_046's iter_039 sub-component (cross-asset VRP).
- Whaley (2009), JPM 35(3) 98-105, DOI 10.3905/JPM.2009.35.3.098 —
  VIX as ex-ante risk regime indicator; preserved via iter_041 leg
  inside iter_046.
- Asvanunt-Richardson (2017), JPM 43(2), DOI 10.3905/jpm.2017.43.2.090
  — credit risk premium thesis; the stream BEING REPLACED here.
- Carhart (1997), JoF 52(1) 57-82, DOI 10.1111/j.1540-6261.1997.tb03808.x
  — UMD momentum factor; trend-following primitive heritage.
- Moskowitz-Ooi-Pedersen (2012), JFE 104(2) 228-250, DOI
  10.1016/j.jfineco.2011.11.003 — Time-Series Momentum (TSM) with
  trend persistence and 12-month formation; rationalizes single-asset
  trend filters as economically motivated.
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
- `[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio with cumulative
  n_trials (4334).
- ProShares UPRO prospectus 2024-2025 — preserved expense-ratio context
  for any future LETF discussion (NOT used here; QQQ_trend uses
  unleveraged QQQ).

## Edge source

iter 058's CAGR floor is binding 0/3 because HYG_TSM is Sharpe-positive
but CAGR-near-zero (~4.85%). Substituting with QQQ-200d-trend (CAGR
~12-14% standalone) lifts the 3rd-stream CAGR contribution from
~0.49% to ~1.20-1.40% at w=0.10, lifting combined CAGR enough to
clear the educational floor (9.18%) for the first time without
sacrificing the diversification that iter 063 lost with internal-LETF.

What SPY 1x misses: SPY-buy-hold has no regime gate; QQQ-trend captures
**bull-market participation in tech** during regime ON, **avoids
bear-market drawdowns** when QQQ < 200d SMA. This is structurally a
**Faber TAA primitive** layered on top of iter 058's risk-parity + VRP
+ regime-equity stack.

## Datasets

- **educational** (2006-01-03 → 2026-04-15, ~5 105 bars): the 4-year
  warmup window where the iter 058 family's CAGR floor has been
  binding (8.69-9.07%). This is the **critical test bench** — if
  QQQ-trend lifts edu CAGR above 9.18%, we have first 1st CAGR-floor
  unlock on iter 058 family without internal-LETF.
- **spy_real** (2009-06-25 → 2026-04-15): post-GFC primary real-data
  benchmark; pre-val showed combined CAGR 9.94% (still below 11.98%
  floor by ~2 pp, but moving direction).
- **ndx_real** (2010-02-12 → 2026-04-15): QQQ benchmark; pre-val
  showed combined CAGR 10.14% (still 5.2 pp below 15.35% floor); QQQ
  beta in iter_046 is implicit via SPY-correlated regime equity, so
  ndx is the most demanding test of the QQQ-trend addition.

## Kill criteria (pre-committed)

| # | Kill | Threshold |
|---|---|---|
| A | Combined Sharpe regress vs iter 058 by ≥ 0.05 on ≥ 2 datasets | Falsifies "low-Sharpe-trend stream lifts CAGR cleanly" |
| B | DSR worst-p ≥ 0.10 (2× iter 058's 0.0494 ceiling) | Falsifies "Sharpe edge holds with cumulative n_trials=4334" |
| C | Score < 79 (iter 062/063 baseline at internal-LETF axis) | Then this iteration provides no new information vs internal-LETF |
| D | Markowitz outer residual ≥ 0.05 on ≥ 2 datasets | Falsifies "0.9·r_046 + 0.1·r_qqqt is closed-form combinable" |
| E | G7 cross-lib > 3 pp absolute CAGR difference (numpy reference) | Indicates engine bug |
| F | corr(iter_064, iter_058) > 0.99 | Means iter 064 is too close to iter 058 to claim novelty |
| G | edu CAGR < 8.69% (regression vs iter 058) | The whole point is to LIFT edu CAGR; if it drops, the substitution is broken |

If 2+ kills fire ⇒ hypothesis falsified, iteration marked aborted-with-
lesson. If only 1 kill fires (especially A or G), iteration still
informative. If 0 kills fire AND score ≥ 90 AND winner_conditions met
⇒ **WINNER candidate** for shell-loop halt.

## Expected budget

- **Configs to test**: 1 (single pre-committed cfg, no grid)
- **Wall-time**: ~30 min (single backtest × 3 datasets, plus G6 bootstrap
  + G3 walk-forward + G1 PBO trivial since N=1)
- **Files to create** in this iter dir:
  - `qqq_trend.py` — pandas implementation of 200d SMA trend filter
  - `numpy_reference_iter064.py` — pure-numpy reference for G7
  - `combined_046_plus_qqqt.py` — outer combine 0.9 · r_046 + 0.1 · r_qqqt
  - `run_backtests.py` — orchestrator across 3 datasets
  - `compute_gates_and_score.py` — gates + scoring helper invocation
  - `tests/test_qqq_trend.py` — TDD specs for the trend filter
  - `tests/test_combined.py` — TDD specs for the combine
  - `results.json` — full output schema (returns_series, runs, etc.)
  - `verdict.json` — produced by `score_strategy()`
  - `final_report.md` — Stage 5 report
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
- **cumulative_n_trials advance**: 4333 → 4334 (+1 single config)

## Implementation plan

1. **Implement QQQ_TREND in pandas** (`qqq_trend.py`):
   - Input: QQQ adj_close series
   - Compute 200-day SMA
   - Signal at end-of-t-1: 1 if close > SMA, 0 otherwise
   - Apply T+1 lag (signal[t-1] applied to ret[t])
   - Add cost 5 bps per signal flip (entry/exit transaction cost)
   - Return daily net returns series aligned to QQQ price index
2. **Implement pure-numpy reference** (`numpy_reference_iter064.py`):
   - Same logic in pure numpy arrays for G7 cross-lib parity
3. **Implement combiner** (`combined_046_plus_qqqt.py`):
   - Outer combine 0.9 · iter_046 + 0.1 · qqqt (inner-join on common
     dates)
4. **TDD tests** (`tests/test_*.py`):
   - test SMA computation correctness on toy data
   - test signal logic + lag + cost
   - test combiner inner-join + weight invariants
   - test G7 parity (pandas == numpy to within 1e-10)
   - target: 12-15 tests, all green in < 1s
5. **Run** (`run_backtests.py`):
   - Load iter_046 stream + QQQ prices for each dataset window
   - Compute QQQ_TREND and combined
   - Compute Sharpe / CAGR / MDD / corr / Markowitz residual
   - Run G6 bootstrap (1000 resamples, 99.9% CI)
   - Run G7 cross-lib check
   - Persist `returns_series` + `subcomponent_returns` + `runs`
6. **Gates + score** (`compute_gates_and_score.py`):
   - Compute G1-G7 per dataset (G1=PBO trivial; G2=DSR cumulative;
     G3=WF 6/8; G4=OOS 70/30; G5=FWD post-2020; G6=bootstrap;
     G7=cross-lib)
   - Apply rolling-window robustness check (3 sub-windows per dataset)
   - Call `score_strategy(metrics, gates, cumulative_n_trials=4334)`
   - Write `verdict.json`
7. **Plots**: invoke `plot_helper.py --iter 064`
8. **Report + memory**: write `final_report.md`, update `BASE_MEMORY.md`,
   append to `DEAD_ENDS.md` if new structural closure (likely the
   "low-CAGR 3rd stream sacrificed for high-CAGR equity-trend 3rd stream"
   trade-off).
