# Iteration 077 — iter 064 + Long-Short MTUM/VLUE factor sleeve ensemble

## Hypothesis

Extend the iter 064 saved-stream (TOP-K #1, score 90 STRONG) with a
**dollar-neutral long-short MTUM−VLUE factor sleeve** as a 3rd-stream
ensemble leg. MTUM (iShares MSCI USA Momentum, 2013-04-16) and VLUE
(iShares MSCI USA Value, 2013-04-16) form a momentum-vs-value factor
pair whose long-short construction:

1. **Decorrelates from SPY by construction** (dollar-neutral, equity
   exposure cancels) — targets the iter 075/076 joint-constraint
   `ρ < 0.5`.
2. **Has documented standalone Sharpe ≥ 0.6** on the 2013-2026 window
   per Carhart (1997) momentum literature + AQR's Asness-Frazzini-
   Pedersen (2013) quality-momentum-value framework — targets the
   `pre-borrow Sharpe ≥ 0.7-1.0` half of the joint constraint that
   iter 076 vindicated as the binding gap.

The sleeve construction:

```
gross_t = adj_close_MTUM[t]/adj_close_MTUM[t-1] − adj_close_VLUE[t]/adj_close_VLUE[t-1]
size_t  = clip(target_vol / σ_lag, 0, leg_cap)        # vol-target sizing
borrow  = short_borrow_rate × size_t / 252             # daily borrow on short leg
cost    = 5 bps on signal-magnitude turnover           # transaction cost
r_sleeve_t = size_{t-1} · gross_t − borrow_{t-1} − cost_{t}
```

Ensemble (matches iter 074/075/076 outer-Markowitz convex blend):

```
r_077_t = w_064 · r_064_t + w_sleeve · r_sleeve_t
```

If MTUM−VLUE delivers Sharpe ≥ 0.5 net of 1% borrow with ρ ≈ 0 vs SPY,
this is the **first iter 077 candidate satisfying both halves of the
iter 075/076-derived joint constraint** — the path implied by iter 076
final report's "next iteration suggestions" #2.

## Primary citation

`[advances_fin_ml, ch.3 + p.222-223]` — de Prado (2018) Triple-barrier
labelling + DSR with per-iter n_trials. Specifically the meta-labelling
chapter on building factor ensembles where each leg has independent
mechanism (momentum vs value), and the DSR p-value relaxation
discipline this iteration follows (n_trials = 20 within hypothesis,
not cumulative).

Carhart, M. (1997). "On Persistence in Mutual Fund Performance."
*Journal of Finance* 52(1), 57-82. DOI 10.1111/j.1540-6261.1997.tb03808.x
— UMD momentum factor (long winners − short losers); the canonical
academic reference for momentum-as-factor with documented Sharpe
0.5-0.8 historical premium net of trading frictions.

## Additional citations

- **Asness, C., Moskowitz, T., Pedersen, L.** (2013). "Value and
  Momentum Everywhere." *Journal of Finance* 68(3), 929-985.
  DOI 10.1111/jofi.12021 — joint momentum-value strategy on US equity
  factors; reports Sharpe 0.7-1.1 on cross-sectional implementation
  with low correlation to SPY (~0.0-0.2 in 1980-2010 window).
- **Fama, E., French, K.** (1993). "Common Risk Factors in the Returns
  on Stocks and Bonds." *JFE* 33(1), 3-56. DOI 10.1016/0304-405X(93)90023-5
  — value premium primitive (HML); VLUE proxies HML on US large-cap.
- **Jegadeesh, N., Titman, S.** (1993). "Returns to Buying Winners and
  Selling Losers." *JoF* 48(1), 65-91. DOI 10.1111/j.1540-6261.1993.tb04702.x
  — momentum primitive (UMD); MTUM proxies UMD on US large-cap.
- `[stocks_on_the_move, p.21-30]` — Clenow's momentum framework (used
  in iter 064's QQQ-trend sub; here applied at factor-spread level).
- `[volatility_trading, p.218]` — Sinclair (2013) inverse-vol sizing
  primitive (sleeve sizing).
- **Frazzini, A., Pedersen, L.** (2014). "Betting Against Beta." *JFE*
  111(1), 1-25. DOI 10.1016/j.jfineco.2013.10.005 — borrow-friction
  primitive on long-short construction (iter 077 applies a 1%/yr short-
  borrow charge per the "retail short-stock-borrow rate on liquid
  ETFs" convention).
- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen 2012 FAJ 68(1);
  preserved verbatim via iter 064 saved stream (the 90% anchor).
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead).
- Markowitz, H. (1952). "Portfolio Selection." *J. Finance* 7(1), 77-91.
  DOI 10.1111/j.1540-6261.1952.tb01525.x — convex combination math.

## Edge source

What SPY 1x buy-hold misses: pure equity beta exposure misses the
**factor risk premia** that have historically rewarded momentum and
value tilts. A long-short MTUM−VLUE pair captures the spread between
these two factor anomalies — when momentum outperforms value (e.g.,
2017-2020) the sleeve gains; when value outperforms (e.g., 2022) the
sleeve loses. Crucially, the long-short construction is **dollar-neutral
on equity beta**, so the sleeve adds factor-spread returns without
duplicating SPY's directional exposure that iter 064 already harvests.
This is structurally what GLD/TLT (iter 075/076) attempted via
non-equity diversification but could not deliver due to the borrow-
Sharpe identity from `[leverage_for_the_long_run, ch.5]` (sleeve
standalone Sharpe ~0.5 too low for joint constraint).

## Datasets

- **educational** (SPYSIM 2006-01-03 → 2026-04-15, ~5105 bars):
  MTUM/VLUE start 2013-04-18, so the sleeve is **off (returns = 0)**
  for the first ~7 years and **on** for the remaining ~13 years. The
  ensemble degenerates to iter 064 for 2006-2013 and becomes
  iter 064 + sleeve for 2013-2026. Honest documentation of the data-
  asymmetry: this dataset's role here is robustness check on the
  combined behavior, not the primary edge test.
- **spy_real** (2009-06-25 → 2026-04-15, ~4226 bars): primary real-
  data benchmark. Sleeve off for 2009-06 → 2013-04 (~4 years),
  on for 2013-04 → 2026-04 (~13 years). The 13-year on-window covers
  3 distinct factor regimes (post-GFC growth 2013-2018, COVID
  inflection 2020, value-revival 2022-2024).
- **ndx_real** (2010-02-12 → 2026-04-15, ~4046 bars): NDX-anchored
  benchmark. Same temporal coverage as spy_real for the sleeve. NDX
  benchmark of 19% CAGR is the most demanding test of any addition.

## Kill criteria (pre-committed)

| # | Kill | Threshold |
|---|---|---|
| **A** | `ρ(r_sleeve, r_SPY) > 0.5` on ≥ 2 datasets | Falsifies "long-short construction decorrelates from SPY by construction" |
| **B** | Sleeve standalone Sharpe < 0.40 (net of 1% borrow + 5bps cost) on ≥ 2 datasets | Falsifies "factor pair has Sharpe ≥ 0.7" hypothesis (allowing 0.3 cushion below the required minimum) |
| **C** | Combined Sharpe regress vs iter 064 ≥ 0.05 on ≥ 2 datasets | Sleeve breaks the iter 064 anchor — net-harmful overlay |
| **D** | Best cfg score < 75 (below STRONG) | No new information vs iter 075's 81 floor |
| **E** | G7 cross-lib > 3pp on any cfg | Engine bug |
| **F** | PBO grid-level ≥ 0.5 on ≥ 2 datasets | Wide-grid (5×4=20) overfitting (iter 076 vindicated wider grids work) |
| **G** | DSR worst-p ≥ 0.05 on best cfg (v2 n=20) | Winner condition #3 falsified |
| **H** | Combined CAGR ≥ floor on 0/3 datasets (no improvement on 5th winner cond) | Same gap as iter 075/076 — joint-constraint hypothesis falsified |

If 0 kills fire AND score ≥ 90 AND all 5 winner conds met
⇒ **WINNER candidate** for shell-loop halt.

If only KILL B fires ⇒ closes the "high-Sharpe long-short factor
sleeve" path; iteration informative.

If KILL H fires alone ⇒ even with high-Sharpe + low-ρ sleeve, the
CAGR floor remains structural to the iter 064 framework, indicating
the path forward is NOT 2nd-leg ensembles regardless of which leg.

## Expected budget

- **Configs to test**: 5 target_vol × 4 w_sleeve = **20 cfgs** (matches
  iter 076 grid size; per-iter v2 DSR convention applies n=20).
- **Wall-time**: ~60-90 min (3 datasets × 20 cfgs gate batteries +
  G6 vectorized bootstrap + G7 cross-lib + Markowitz residual).
- **Files to create** in this iter dir:
  - `mtum_vlue_sleeve.py` — pandas long-short sleeve implementation
  - `numpy_reference_iter077.py` — pure-numpy reference for G7
  - `run_backtests.py` — orchestrator across 3 datasets × 20 cfgs
  - `compute_gates_and_score.py` — gates + scoring
  - `tests/test_iter077_sleeve.py` — TDD specs (≥ 18 tests)
  - `results.json` — full output schema (with `returns_series` key)
  - `verdict.json` — produced by `score_strategy()`
  - `final_report.md` — Stage 5 report
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
- **cumulative_n_trials advance**: 4462 → 4522 (+60 = 20 cfgs × 3 ds).

## Implementation plan

1. **Implement long-short sleeve** (`mtum_vlue_sleeve.py`):
   - Inputs: MTUM and VLUE adj_close series
   - Compute daily returns, gross spread = ret_MTUM − ret_VLUE
   - 21d trailing realized vol of gross_spread, annualized
   - Position size = target_vol / vol_lag, capped at leg_cap, T-1 lag
   - Apply 1% annualized borrow charge on short side: position × 0.01 / 252
   - Apply 5 bps transaction cost on |Δposition| (approximate turnover)
   - Return daily net returns aligned to MTUM/VLUE inner-join
2. **Implement pure-numpy reference** (`numpy_reference_iter077.py`):
   - Same logic in pure numpy for G7 cross-lib parity (target ≤ 1e-9)
3. **Implement combiner**: reuse pattern from iter 075's
   `combine_iter064_with_sleeve` (linear convex blend, inner-join)
4. **TDD tests** (`tests/test_iter077_sleeve.py`):
   - test gross spread = ret_A − ret_B on toy data
   - test vol-target sizing reaches target on synthetic vol cohort
   - test leg cap clamps on vol spike
   - test borrow charge applied to short side only
   - test transaction cost on signal flip
   - test T-1 lag enforced (no look-ahead)
   - test warmup emits 0 returns
   - test pure-numpy reference matches pandas within 1e-9
   - test inner-join with iter 064 stream preserves dates
   - test convex combine boundaries (w=0/1)
   - test negative-weight rejection
   - test borrow rate parameter is honored (changes sleeve return monotonically)
   - target ≥ 18 tests, all green in < 5 s
5. **Run** (`run_backtests.py`):
   - For each of 3 datasets, load iter 064 saved stream
   - Restrict MTUM/VLUE to dataset window
   - Compute sleeve once per dataset (both pandas + numpy)
   - For each of 20 cfgs (target_vol × w_sleeve), combine + metrics
   - Persist `returns_series` (per dataset, per cfg) + benchmarks +
     subcomponent_returns + crosslib + Markowitz residual
6. **Gates + score** (`compute_gates_and_score.py`):
   - For each cfg: G1 (PBO via CSCV n_blocks=10), G2 (DSR raw α=0.05
     with n=20), G3 (WF 6/8 + MDD<25%), G4 (OOS 70/30 Sharpe>0),
     G5 (FWD post-2020 Sharpe>0), G6 (vectorized bootstrap CI low),
     G7 (cross-lib ≤ 3pp)
   - Robustness sub-window bonus (3 thirds × 3 ds = 9 sub-windows)
   - Apply 8 pre-committed kill criteria (A-H) per cfg
   - `score_strategy(metrics, gates, cumulative_n_trials=4522)`
   - Pick best cfg by score, write `verdict.json`
7. **Plots**: invoke `studies/strategy_hunt_loop/plot_helper.py --iter 077`
8. **Report + memory**: write `final_report.md`, update `BASE_MEMORY.md`,
   append to `DEAD_ENDS.md` if structural closure (likely either
   "long-short factor sleeve at 1% borrow saturates at 85" or "joint-
   constraint hypothesis falsified — 5th winner cond structural").
