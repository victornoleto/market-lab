# Iteration 079 — Multi-asset Top-K Relative+Absolute Momentum on 5-asset Cross-class Universe

## Hypothesis

**Extend iter 078's Antonacci GEM (3-asset SPY/EFA/AGG) to a 5-asset
multi-asset-class universe {SPY, QQQ, EFA, TLT, GLD} with top-K∈{1,2,3}
equal-weight rotation and an absolute-momentum filter, plus an AGG
defensive fallback.** The 5 selectable assets span 3 distinct risk-
premium classes (US equity = SPY+QQQ for sector tilt dispersion, intl
equity = EFA, long-duration bonds = TLT, gold = GLD), explicitly
sidestepping iter 017's regional-equity-rotation dead-end (which only
applies to 3-region equity universes nested under a single equity risk-
premium factor) and structurally distinct from iter 025's slow-EWMAC
trend mechanism (long-only continuous EWMA crossover) by using a
HARD-ROTATION cross-sectional top-K mechanism (binary equal-weight per
selected asset).

Mechanism in one paragraph: at each rebalance (monthly, last business
day of month M), compute trailing N-month total return for each of the
5 selectable assets. Sort descending; pick the top-K assets. For each
of the top-K assets that ALSO has a positive trailing return ≥ 0%
(absolute-momentum filter, Faber 2007), allocate 1/K equal-weight to
that asset. For each of the top-K that fails the abs-mom gate, route
its 1/K share to AGG (defensive fallback). Hold until next month-end.
Cost: 5 bps on |Δposition| L1 norm.

Why this should work (edge hypothesis): SPY 1× misses three structural
sources of edge that this mechanism captures: (a) **QQQ
tech-leadership phases** (2010-2014, 2017-2020, 2023+) where QQQ's
trailing momentum persistently exceeds SPY's by 3-5pp/yr — top-K=1
selects QQQ in those windows, top-K=2 holds both. (b) **Bond/gold
defensive regimes** (2008-2011, 2020-Q1, 2022) where TLT and GLD
provided positive returns while equity drew down — top-K rotation
captures the Markowitz-style cross-asset diversification benefit
without forfeiting the ability to hold equity in normal markets.
(c) **The AGG defensive fallback during severe drawdowns** retains
iter 078's MDD-edge mechanism (lost equity exposure when all asset
classes are in negative trailing momentum) but applied PER-LEG (not
binary 100/0), preserving partial equity exposure when only some
assets fail abs-mom.

The hypothesis is **structurally novel** vs all 78 prior iterations
because:

1. **Cross-asset-class top-K relative+absolute momentum on 5-asset
   universe** has never been tested. Iter 078 was 2-asset relative
   momentum (SPY-vs-EFA only); this expands the relative-momentum
   step's dispersion from 2 candidates to 5. Iter 017 was 3-region
   equity rotation (US/INTL/EM with iter 016 vol-target stack) — a
   structurally different mechanism (vol-target × region) on a
   structurally different universe (3 equity regions only).
2. **Per-leg abs-mom routing** (each top-K leg routed to AGG
   independently if it fails abs-mom gate) — never tested. Iter 078's
   abs-mom rule was binary 100/0 (winner OR AGG, no partial).
3. **The 5-asset universe has 60% non-equity component** (TLT+GLD = 2
   of 5 selectable assets are not equity, plus EFA is intl-equity not
   nested under US risk-premium), addressing iter 017's documented
   failure mode head-on.

**DEAD_ENDS.md compatibility check** (verified before writing this
spec):

- ✅ **NOT** the iter 017 dead-end (3-region equity rotation US/INTL/EM
  with iter 016 vol-target stack): different universe (TLT+GLD non-
  equity), different mechanism (top-K hard rotation, not vol-target ×
  region). Iter 017 closure explicitly says cross-asset-class rotation
  is NOT dead.
- ✅ **NOT** the iter 025 dead-end (slow-EWMAC trend on 6-asset basket
  long-only with FDM=1.10): different mechanism (cross-sectional
  top-K relative momentum vs continuous EWMA trend signal),
  different sizing (equal-weight top-K vs portfolio vol-target),
  different universe overlap (this is 5 assets vs iter 025's 6, with
  QQQ+SPY and no EEM/IEF/AGG-as-asset; AGG only used as fallback here).
- ✅ **NOT** the iter 078 dead-end (3-asset Antonacci SPY/EFA/AGG with
  binary 100/0 allocation): expanded to 5 selectable assets,
  partial-allocation top-K mechanism, per-leg AGG routing.

## Primary citation

`[stocks_on_the_move, p.21-30]` — Clenow's framework on momentum as
the most robust market anomaly, applied here to multi-asset cross-
sectional ranking. `[p.81]` for the lookback-window rationale (90-day
or longer is the canonical cross-sectional momentum signal window).

## Additional citations

- **Antonacci, G.** (2014). *Dual Momentum Investing: An Innovative
  Strategy for Higher Returns with Lower Risk.* McGraw-Hill.
  ISBN 978-0071849449. — primary GEM source extended here from 3 to
  5+1 assets.
- **Antonacci, G.** (2017). "Risk Premia Harvesting Through Dual
  Momentum." *Journal of Portfolio Management* 16(1), 27-55.
  DOI 10.3905/joi.2017.16.1.027 — peer-reviewed version of GEM.
- **Faber, M.** (2007). "A Quantitative Approach to Tactical Asset
  Allocation." *J. Wealth Management* 9(4), 69-79.
  DOI 10.3905/jwm.2007.690606 — absolute-momentum filter (per-leg
  variant adopted here).
- **Asness, C., Moskowitz, T., Pedersen, L.** (2013). "Value and
  Momentum Everywhere." *JoF* 68(3), 929-985.
  DOI 10.1111/jofi.12021 — momentum applies cross-asset-class.
- **Moskowitz, T., Ooi, Y. H., Pedersen, L.** (2012). "Time Series
  Momentum." *JFE* 104(2), 228-250.
  DOI 10.1016/j.jfineco.2011.11.003 — TSM-as-abs-mom primitive.
- **Jegadeesh, N., Titman, S.** (1993). "Returns to Buying Winners
  and Selling Losers." *JoF* 48(1), 65-91.
  DOI 10.1111/j.1540-6261.1993.tb04702.x — cross-sectional ranking.
- **Markowitz, H.** (1952). "Portfolio Selection." *JoF* 7(1), 77-91.
  — top-K equal-weight is a constrained Markowitz with binary inclusion
  weights.
- **Hurst, B., Ooi, Y., Pedersen, L.** (2017). "A Century of Evidence
  on Trend-Following Investing." *J. Portfolio Management* 44(1),
  15-29. DOI 10.3905/jpm.2017.44.1.015 — trend on broad multi-asset.
- `[advances_fin_ml, p.222-223]` — DSR with per-iter n_trials.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead).
- `[systematic_trading, p.42 (ch.2)]` — Carver's Law of Active
  Management (multi-asset diversification for Sharpe ∝ √N).
- `[risk_parity, ch.5]` — equal-weight top-K is a degenerate risk-parity
  variant (volatility-equal weights collapse to equal-notional when
  cross-sectional vol differences are small over the rebalance window).

## Edge source

SPY 1× buy-hold misses: (i) **QQQ tech-leadership** when momentum
ranks QQQ above SPY for extended periods; (ii) **non-equity asset
classes** (TLT, GLD) during equity drawdowns when their trailing
returns turn positive while equity goes negative; (iii) **EFA's
intl-leadership** during US-underperformance windows; (iv) **the
AGG defensive routing** when all 5 selectable assets fail abs-mom
(severe cross-asset selloffs like 2008, 2020-Q1, 2022). The CAGR
unlock comes from (i)+(iii): tech and intl rotation can lift CAGR
above SPY 1×. The MDD edge comes from (ii)+(iv): non-equity rotation
during drawdowns + AGG fallback in severe regimes.

## Datasets

- **educational** (SPY/EFA/QQQ/TLT/GLD/AGG with windows 2007-01-03 →
  2026-04-15, ~19y): The longest window where all 6 ETFs have
  contemporaneous data (QQQ goes to 1999, GLD to 2004, EFA to 2001,
  TLT to 2002, AGG to 2003). Spans 2008 GFC + 2011 European debt +
  2020 COVID + 2022 bear — 4 distinct cross-asset regimes. Bench:
  SPY b&h on this window (consistent with iter 078 convention; the
  scoring helper compares against SPYSIM 1986+ benchmark which is a
  conservative bar — the 2007+ window has been a more bull-biased
  regime).
- **spy_real** (2009-06-25 → 2026-04-15, ~17y): Post-GFC bull-bias
  window; the dataset where iter 078 most clearly failed CAGR floor
  (11.42% vs 11.98% required). The 5-asset universe should restore
  CAGR by allowing top-K selection of QQQ during 2010-2020 tech bull.
  Bench: SPY b&h.
- **ndx_real** (2010-02-12 → 2026-04-15, ~16y): The hostile test —
  QQQ benchmark is hard to beat (19% CAGR, 0.955 Sharpe). Top-K=1
  with QQQ in universe should approximate QQQ b&h in tech-bull
  windows but rotate out during 2022 drawdown — testing whether the
  abs-mom filter saves enough drawdown to outweigh its cost. Bench:
  QQQ b&h.

## Kill criteria (pre-committed)

The hypothesis is **falsified** if any of the following hold at end of
testing (no post-hoc rationalization allowed):

- **KILL A — top-K degenerate**: top-1 picks SPY+QQQ COMBINED > 90% of
  months on spy_real (i.e., the cross-asset rotation degenerates to
  "buy US equity always", non-equity selections never win) →
  hypothesis falsified.
- **KILL B — abs-mom inactive**: AGG allocation triggered < 3% of
  months on spy_real (per-leg routing means each leg can independently
  route to AGG; aggregate AGG share < 3% means abs-mom filter rarely
  fires).
- **KILL C — Sharpe regress vs bench**: best cfg's combined Sharpe
  is BELOW the dataset's bench by ≥ 0.10 on ≥ 2 of 3 datasets (i.e.,
  worse than just holding SPY/QQQ).
- **KILL D — total score < 60 (below PROMISING)**: rubric scores
  best cfg < 60 → no informational edge above iter 078's 75 ceiling.
- **KILL E — G7 > 3 pp on any cfg**: implementation bug (numpy ≠ pandas).
- **KILL F — PBO ≥ 0.5 on ≥ 2 datasets**: configuration overfit.
- **KILL G — DSR worst-p ≥ 0.05 (n=9, v2 per-iter)**: even with the
  small n_trials, Sharpe edge is statistical noise.
- **KILL H — winner_conditions_met = false on ALL 9 cfgs**: best
  cfg passes 4/5 but no cfg gets 5/5 (acceptable as STRONG outcome
  if score ≥ 75).

The decisive question: **does adding 3 non-equity-or-non-LC asset
classes (QQQ, TLT, GLD) to the GEM-style top-K rotation lift CAGR
above iter 078's 11.42% on spy_real WHILE preserving gates 7/7/7 and
Sharpe edge ≥ 1.0?** That's the precise gap iter 078 left unfilled.

## Expected budget

- **Configs to test:** 9 cfgs = 3 lookbacks (3 / 6 / 12 months) ×
  3 top-K values (1 / 2 / 3). Tight grid keeps n_trials small for v2
  DSR. Trans cost fixed at 5 bps; abs-mom threshold fixed at 0%
  (per-leg routing variant; iter 078's KILL G test showed `ief`
  threshold made things slightly worse, so we drop it).
- **Wall-time:** ~70-90 minutes (similar to iter 078 — monthly
  rebalance loop is fast even with 5 selectable assets; 3 datasets ×
  9 cfgs = 27 dataset×cfg pairs).
- **Files to create:**
  - `hypothesis.md` (this file)
  - `multi_asset_topk_momentum.py` — pandas implementation (extends
    iter 078's `gem_signal` to top-K with per-leg AGG routing).
  - `numpy_reference_iter079.py` — numpy-pure equivalent for G7 parity.
  - `run_backtests.py` — driver: load 5-asset prices, run 9 cfgs × 3 ds,
    cross-lib parity, save returns_series + per-cfg metrics.
  - `compute_gates_and_score.py` — gate battery + scoring (reuse iter
    078 pattern).
  - `tests/test_multi_asset_topk_iter079.py` — TDD spec.
  - `results.json`, `verdict.json`, `final_report.md`.
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.

## Implementation plan

1. **TDD first** — `tests/test_multi_asset_topk_iter079.py`:
   (a) hand-computed top-K table on 13 monthly bars with 5 assets
       in 3 deterministic regimes (US-leads, intl-leads, all-down);
   (b) per-leg abs-mom routing: top-K=2, leg1 trailing > 0 → keep,
       leg2 trailing < 0 → AGG; verify 0.5 to leg1 + 0.5 to AGG;
   (c) T-1 lag verification (signal at close of M → allocation M+1);
   (d) cost calculation: |Δw| × 5 bps L1 norm across all 6 sleeves;
   (e) numpy reference matches pandas to 1e-9 element-wise.
2. **Implementation** — `multi_asset_topk_momentum.py`:
   - `compute_lookback_returns(monthly_prices: dict[str, pd.Series],
     n_months: int) -> pd.DataFrame` (cols = assets, rows = months)
   - `top_k_signal(lookback_df: pd.DataFrame, top_k: int,
     abs_threshold: float = 0.0) -> pd.DataFrame` returns
     {asset: weight} per month; weights ∈ {0, 1/K} per asset and
     remainder routed to AGG.
   - `compute_topk_returns(daily_returns: dict[str, pd.Series],
     signal_df: pd.DataFrame, trans_cost_bps: float) -> pd.Series`
     — daily returns aligned with cost on monthly turn.
3. **Numpy reference** — vectorized equivalent without pandas.
4. **Driver** — load all 6 ETFs (SPY/QQQ/EFA/TLT/GLD/AGG) for each
   dataset window with 24-month look-behind for warmup.
5. **Gates + score** — reuse iter 078's `compute_gates_and_score.py`
   pattern with strategy-specific WF/OOS/FWD splits.
6. **Pre-commit verification** — pytest baseline must stay green
   (~796 collected); `test_multi_asset_topk_iter079.py` adds ~6
   tests (all green required).

n_trials_per_iter = 9 (per-iteration v2 DSR convention).
cumulative_n_trials advance: 4546 → 4573 (+27 = 9 cfgs × 3 datasets).
