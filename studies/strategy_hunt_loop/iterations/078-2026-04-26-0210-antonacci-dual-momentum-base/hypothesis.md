# Iteration 078 — Antonacci Dual Momentum (Global Equities Momentum, GEM) as STANDALONE BASE

## Hypothesis

**Antonacci's GEM (Global Equities Momentum) framework — combining
absolute momentum (own-asset trend filter) and relative momentum
(cross-asset ranking) on a 3-asset universe (US equity / Intl equity /
Aggregate bond) — delivers a **fundamentally different mechanism class**
from the iter-064 saved-stream lineage and is the **first standalone
base hypothesis tested in 12 iterations** (064/068-072 + 074-077 all
anchored on iter 064's static-stack stream).**

Mechanism in one paragraph: at each rebalance (monthly, last-business-
day close), compute the trailing N-month total return of US equity
(SPY) and developed-international equity (EFA). The "winner" is the
asset with the higher trailing return ((**relative** momentum). If the
winner's trailing return is also above the absolute-momentum threshold
(0% or T-bill proxy), allocate 100% to the winner; otherwise allocate
100% to AGG (aggregate bond — defensive sleeve). Hold the chosen
allocation until next month's rebalance. Costs: 5 bps on |Δposition|.

Why this should work (edge hypothesis): the 3-asset GEM design
exploits TWO independent risk-premia simultaneously: (1) the equity
trend / time-series momentum premium (Asness-Moskowitz-Pedersen 2013
JoF 68(3); Moskowitz-Ooi-Pedersen 2012 JFE 104(2)) which says assets
with positive trailing returns continue to outperform; (2) the
cross-sectional relative-strength premium (Jegadeesh-Titman 1993 JoF
48(1)) applied at asset-class level. The "exit to bonds" rule converts
the equity drawdown into a regime switch — the strategy holds AGG
during the worst quartile of equity returns, which historically is when
equities deliver negative tail returns and bonds rally on flight-to-
quality. Antonacci (2014) reports backtested CAGR 14-17% / Sharpe
0.85-1.0 / MDD ~22% on US data 1974-2014.

The hypothesis is **structurally novel** vs all 77 prior iterations
because (a) it uses an INTERNATIONAL equity rotation (no prior iter
included EFA in the universe), (b) it's a STANDALONE BASE not a sleeve
or overlay on iter 064, (c) the regime-switch is a HARD allocation
boundary (100/0 binary on relative + abs momentum) vs the soft
inverse-vol blends of the iter-064 family. **DEAD_ENDS.md does not
contain Antonacci, GEM, or any 3-asset hard-rotation pattern.**

## Primary citation

`[stocks_on_the_move, p.21-30]` — Clenow's framework on momentum as
the most robust market anomaly (used here for the cross-sectional
relative-momentum step; Clenow's "trade only what's strong" rule).

## Additional citations

- `[systematic_trading, p.42 (ch.2)]` — Carver's Law of Active
  Management: Sharpe ∝ √N independent bets — multi-asset diversification
  argument for the 3-asset universe.
- `[advances_fin_ml, p.222-223]` — DSR with per-iter n_trials.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead).
- `[leverage_for_the_long_run, ch.5]` — Gayed (2016) on regime-
  switching trend overlay (analogous mechanism class for context).
- Web: **Antonacci, G.** (2014). *Dual Momentum Investing: An
  Innovative Strategy for Higher Returns with Lower Risk.* McGraw-Hill.
  ISBN 978-0071849449. — primary GEM source.
- Web: **Antonacci, G.** (2017). "Risk Premia Harvesting Through Dual
  Momentum." *Journal of Portfolio Management* 16(1), 27-55.
  DOI 10.3905/joi.2017.16.1.027 — peer-reviewed academic version.
- Web: **Faber, M.** (2007). "A Quantitative Approach to Tactical
  Asset Allocation." *Journal of Wealth Management* 9(4), 69-79.
  DOI 10.3905/jwm.2007.690606 — absolute momentum (10-mo SMA timing
  filter; threshold equivalent in our spec).
- **Asness, C., Moskowitz, T., Pedersen, L.** (2013). "Value and
  Momentum Everywhere." *JoF* 68(3), 929-985. DOI 10.1111/jofi.12021.
- **Moskowitz, T., Ooi, Y. H., Pedersen, L.** (2012). "Time Series
  Momentum." *JFE* 104(2), 228-250. DOI 10.1016/j.jfineco.2011.11.003.
- **Jegadeesh, N., Titman, S.** (1993). "Returns to Buying Winners
  and Selling Losers." *JoF* 48(1), 65-91. DOI 10.1111/j.1540-6261.1993.tb04702.x.

## Edge source

SPY 1x buy-hold misses the **regime switch out of equity into bonds
during equity drawdowns** (defensive rotation). It also misses the
**relative-strength dispersion between US and international equity**
that materialized strongly in 2003-2007 (intl outperformance) and
2010-2020 (US outperformance) — capturing whichever leg leads in any
12-month window can lift CAGR through reduced opportunity cost.

## Datasets

- **educational** (SPY 2007-01-03 → 2026-04-15, ~19y): Tests Antonacci
  through GFC-2008 + COVID-2020 + 2022 bear, the only true equity
  drawdown trio in the available data window. AGG/IEF rotate-to-bonds
  rule has its strongest test here. Bench: SPY b&h. (Per the iter
  075-077 convention, "educational" uses SPY-real with the longest
  feasible history.)
- **spy_real** (SPY 2009-06-25 → 2026-04-15, ~17y): Post-GFC bull-bias
  window; the "rotate to bonds" rule will have FEWER triggers, testing
  whether GEM still adds value when equity doesn't drawdown deeply.
  Bench: SPY b&h. The hardest test for a defensive overlay strategy.
- **ndx_real** (SPY/EFA/AGG universe, 2010-02-12 → 2026-04-15, ~16y):
  Same universe as above (SPY/EFA/AGG — Antonacci canonical does NOT
  include QQQ), benchmarked against QQQ b&h. Tests whether GEM with
  US large-cap exposure can keep up with the QQQ tech bull-run; this
  is the **hostile test** because QQQ's 19% bench CAGR is hard to beat
  with any defensive rotation.

## Kill criteria (pre-committed)

The hypothesis is **falsified** if any of the following hold at end of
testing (no post-hoc rationalization allowed):

- **KILL A — relative-momentum signal degenerate**: SPY-vs-EFA winner
  flips < 4 times across the 17y spy_real window (i.e., the relative
  momentum is structurally non-informative — one leg dominates always
  and the strategy is just timing within that leg). Threshold: < 4
  flips on spy_real → falsified.
- **KILL B — absolute momentum filter inactive**: AGG allocation
  triggered < 5% of months on spy_real. If the bond rotation rule
  almost never fires, the strategy is essentially un-defended buy-hold
  with extra friction → falsified.
- **KILL C — Sharpe regress vs SPY b&h**: best cfg combined Sharpe
  is BELOW the dataset's bench by ≥ 0.10 on ≥ 2 of 3 datasets (i.e.,
  GEM is worse than just holding SPY/QQQ). Threshold: Sharpe loss ≥
  0.10 on ≥ 2 ds → falsified.
- **KILL D — total score < 60 (PROMISING tier)**: if the rubric scores
  < 60, GEM is no better than the iter 029-035 mid-tier closures.
- **KILL E — G7 cross-lib > 3 pp**: implementation bug, not a
  hypothesis kill but a STAGE 3 abort.
- **KILL F — PBO ≥ 0.5 on ≥ 2 datasets**: configuration overfit;
  the strategy's edge is parameter-tuning artifact rather than
  structural.
- **KILL G — DSR worst-p ≥ 0.05 with n_trials = 8 (per-iter v2)**:
  even with the tiny n_trials, the Sharpe edge is statistical noise.
- **KILL H — winner conditions met = TRUE for 0 cfgs**: even after
  all 8 cfgs scored, none satisfy 5/5 strict winner conditions —
  GEM's edge is real but insufficient to clear the strict threshold.
  (This is acceptable as a STRONG outcome; only catastrophic if the
  4/5-cond best cfg has a worse profile than iter 064 STRONG-tied
  family.)

The decisive question: **does Antonacci's GEM lift CAGR ≥ 12% on
spy_real (clearing iter 064's 9.97% ceiling) WHILE preserving Sharpe
edge ≥ 1.0?** That's the precise gap that all 10 iter-064-anchored
variants (064/068-072 + 074-077) failed to close.

## Expected budget

- **Configs to test:** 8 cfgs = 4 lookbacks (3 / 6 / 9 / 12 months) ×
  2 absolute-momentum thresholds (0% and IEF-trailing-return as
  T-bill proxy). Tight grid to keep n_trials small for v2 DSR.
- **Wall-time:** ~75-90 minutes (data loading + monthly rebalance loop
  is fast; 3 datasets × 8 cfgs = 24 trials).
- **Files to create:**
  - `hypothesis.md` (this file)
  - `antonacci_dual_momentum.py` — pandas implementation of GEM
    monthly-rebalance loop with absolute + relative momentum gate
  - `numpy_reference_iter078.py` — numpy-pure equivalent for G7 parity
  - `run_backtests.py` — driver: load prices, run 8 cfgs × 3 ds,
    compute crosslib parity, save returns_series + per-cfg metrics
  - `compute_gates_and_score.py` — gate battery + scoring wrapper
  - `tests/test_antonacci_iter078.py` — TDD spec for the rotation
    logic (T-1 lag, monthly rebalance, no look-ahead, abs+rel rule
    truth table)
  - `results.json`, `verdict.json`, `final_report.md`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
    (auto-generated by `plot_helper.py`)

## Implementation plan

1. **TDD first** — write `test_antonacci_iter078.py` with cases:
   (a) hand-computed rotation table on 13 monthly bars (3 deterministic
   periods: SPY-leads, EFA-leads, both-down);
   (b) T-1 lag verification (signal computed on last close of month M
   feeds allocation for month M+1);
   (c) absolute momentum filter inactive ⇒ pure relative-momentum
   degenerate test (always picks one leg);
   (d) cost calculation: |Δw| × 5 bps on rebalance;
   (e) numpy reference matches pandas to 1e-9 element-wise.
2. **Implementation** — `antonacci_dual_momentum.py`:
   - `compute_monthly_returns(prices: pd.Series) -> pd.Series`
   - `compute_lookback_return(monthly_rets: pd.Series, n_months: int)`
   - `gem_signal(spy_lb: pd.Series, efa_lb: pd.Series, threshold: pd.Series, t_minus_1_lag: bool = True) -> pd.Series`
     — returns "SPY" / "EFA" / "AGG" per month
   - `gem_returns(daily_returns: dict[str, pd.Series], signal: pd.Series, trans_cost_bps: float) -> pd.Series`
     — daily returns aligned to allocation, with cost on monthly turn
3. **Numpy reference** — same logic without pandas; vectorized.
4. **Driver** — load SPY/EFA/AGG/IEF for each dataset window,
   run 8 cfgs, save returns_series + per-cfg metrics + crosslib_diff.
5. **Gates + score** — re-use the same gate/score code pattern as iter
   075-077 (`compute_gates_and_score.py`) but with strategy-specific
   walk-forward / OOS / FWD splits.
6. **Pre-commit verification** — pytest baseline must stay green
   (currently ~796 collected); test_antonacci_iter078.py adds ~6
   tests (all green required).
