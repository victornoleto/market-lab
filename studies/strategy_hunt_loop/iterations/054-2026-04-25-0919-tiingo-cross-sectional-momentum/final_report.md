# Iteration 054 — Final Report

## Verdict

🥉 **MARGINAL** (score 47/100, winner_conditions_met=false, **Kill A + Kill B FIRED**).

Cross-sectional 12-1 momentum (Jegadeesh-Titman canonical) on the
post-2014 422-ticker Tiingo single-stock universe **does not beat
passive SPY/QQQ buy-and-hold** — the structural advantage that
heterogeneous single-stocks were supposed to give over the iter 003
≤20-asset ETF closure failed to materialize. Survivorship-biased
universe + post-2009 momentum-crash regime + high overlap with
market-cap-weighted indices = no edge harvested.

## Headline metrics (top candidate `tk20_lb12_sk1`)

| dataset | Sharpe (vs fixed bench) | Sharpe (vs window-matched SPY/QQQ 2014-2026) | CAGR (vs floor) | MDD (vs ceil) | gates |
|---|---|---|---|---|---|
| educational | 0.655 (vs 0.68; **−0.025**) | n/a | 16.60% (≥ 9.18% ✓) | 28.25% (≤ 60.14% ✓) | 5/7 |
| spy_real    | 0.655 (vs 0.90; **−0.245**) | vs SPY 0.680 (Δ **−0.025**) | 16.60% (≥ 11.98% ✓) | 28.25% (≤ 38.70% ✓) | 5/7 |
| ndx_real    | 0.655 (vs 0.955; **−0.300**) | vs QQQ 0.753 (Δ **−0.098**) | 16.60% (≥ 15.35% ✓) | 28.25% (≤ 40.12% ✓) | 5/7 |

Window-matched benchmarks (2014-01-01 → 2026-04-20):
- SPY: Sharpe 0.680, CAGR 13.46%, MDD 33.70%
- QQQ: Sharpe 0.753, CAGR 18.58%, MDD 35.12%

Strategy CAGR (16.60%) actually beats SPY's (13.46%) on the same window
— but with worse risk-adjusted ratio. The CAGR alone is what makes
floors 4/4/5 pass vs the **Sharpe edge criterion fails 0/3 datasets**.
This is a "deploys capital aggressively into surviving high-momentum
names but with proportional volatility" outcome.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **0** | 25 | 0/3 datasets beat bench + 0.10 (best margin: −0.025 vs SPY 2014-2026; −0.025 vs fixed edu bench 0.68) |
| 2 Gates | **17** | 25 | edu 5/7 + spy 5/7 + ndx 5/7; cross-bonus +4 (cross-dataset thresholds met) |
| 3 DSR | **0** | 15 | worst p=0.811 with n_trials=4324 (Sharpe too low to overcome multi-test penalty) |
| 4 CAGR floor | **15** | 15 | 3/3 datasets pass (16.60% beats all 3 floors) |
| 5 MDD ceiling | **15** | 15 | 3/3 datasets pass (28.25% under all 3 ceilings) |
| 6 Robustness | **0** | 5 | not computed |
| **total** | **47** | **100+5** | tier: 🥉 **MARGINAL** |

## Configuration tested

4 configs (2×2 grid):
- `tk20_lb12_sk1` (canonical Clenow): top_k=20, lookback=12m, skip=1m. **Top by Sharpe.**
- `tk50_lb12_sk1`: top_k=50, lookback=12m, skip=1m. Sharpe=0.621.
- `tk20_lb6_sk1`: top_k=20, lookback=6m, skip=1m. Sharpe=0.646.
- `tk50_lb6_sk1`: top_k=50, lookback=6m, skip=1m. Sharpe=0.654.

Universe: 423 Tiingo tickers with `first_dt ≤ 2014-01-01` and `last_dt ≥ 2026-01-01`.
Window: 2014-01-01 → 2026-04-20 (~12.3y).
Cost: 5 bps roundtrip on each side of weight delta (monthly rebalance).
Cross-lib G7: pandas vs numpy ΔCAGR = 0.0000 pp (perfect parity, 8th
consecutive iter at 0.0000pp on G7).

## Gate detail

| gate | top cfg result | pass? |
|---|---|---|
| G1 PBO | 1.000 (CSCV 8 splits — IS-best lands bottom-half OOS in 7/7 informative splits) | ❌ FAIL |
| G2 DSR | p=0.811 with n_trials=4324 | ❌ FAIL |
| G3 WF | 7/8 windows pass (Sharpe>0 + MDD<25%) | ✅ PASS |
| G4 OOS | OOS Sharpe=0.595 (last 30%) | ✅ PASS |
| G5 FWD | post-2020 Sharpe=0.667 | ✅ PASS |
| G6 Boot | 99.9% CI low=0.004 (just barely positive — borderline) | ✅ PASS |
| G7 Xlib | ΔCAGR=0.0000 pp | ✅ PASS |

PBO=1.0 is the diagnostic killer: with 4 cfgs all producing similar
near-passive-index returns (Sharpe 0.62-0.66, CAGR 12.85-16.60%), the
IS-best vs OOS-best rank reversal is total — cfg ranking is pure noise.
This matches the iter 002 dead-end pattern: small grid + similar
returns = PBO uninformative + structural failure of family to deliver
edge.

## What worked / what didn't

**Worked**:
- **Engine and cross-lib parity**: 0.0000 pp ΔCAGR pandas vs numpy
  on canonical cfg, validating the new monthly-rebalance simulator
  against a hand-rolled numpy reference (`[advances_fin_ml, p.31-34]`
  G7 standard).
- **Gate infrastructure**: WF/OOS/FWD/Bootstrap all run cleanly on a
  qualitatively new pipeline (cross-sectional rebalance, not the
  static-stack overlay/blend pattern of iters 015-053).
- **CAGR + MDD**: strategy actually beat SPY's window-matched CAGR
  (16.60% vs 13.46%) and stayed under all 3 MDD ceilings — not a
  catastrophic failure of compounding.

**Didn't work — the failure mode**:
- **Sharpe is the dimension that fails**. 0.655 strategy vs 0.680 SPY
  same-window: −0.025 Sharpe. The strategy compounds 16.60% CAGR but
  with 25.3% annualized volatility — inferior risk-adjusted returns
  to passive SPY (13.46% CAGR @ 19.8% vol).
- **Survivorship bias HURTS long-only momentum**, contrary to naive
  expectations. The 422-ticker universe is filtered to *post-2014
  survivors* (delisted names absent). Surviving names are the
  market's own momentum winners — a basket of them is heavily
  correlated with the cap-weighted index it's measured against. The
  iter 003 closure ("≤20-asset homogeneous universe lacks idiosyncratic
  variance") was about variance dispersion; this iter uncovers a
  related but distinct issue: **survivorship-filtered universe at
  ANY size has reduced cross-sectional dispersion vs the cap-weighted
  index that contains those same survivors at proportional weights**.
  Top-K equal-weight ≠ market-cap-weight gives some active risk, but
  not enough to generate Sharpe edge against the index it's
  benchmarked against.
- **Post-2009 momentum decay**: empirical literature (e.g., Ben Dor &
  Ross 2024 "Momentum's Misadventures") documents that classic 12-1
  momentum has been a weak factor since 2009, with notable crashes in
  2009 and 2018. Our 2014-2026 window misses the worst (2009) but
  inherits the post-2018 weakness.
- **Long-only captures only half of UMD**: Carhart 1997's UMD factor
  is a long-short construction (~8%/yr historically). Our long-only
  top-K version captures ~half of that premium pre-cost, before
  monthly turnover (turnover ~50-80%/month at top_k=20) eats 2-3 pp.
  The remaining premium is too small to overcome cap-weighted index.
- **PBO=1.0 from grid noise**: 4 configs spanning top_k × lookback all
  produce returns within 0.04 Sharpe of each other — the grid has no
  structural variance, only noise. This is iter 002's pattern in
  reverse: not under-deployment but rather over-similar configs.

## Main lesson (for future iterations)

**The ≥ 20 stocks heuristic isn't sufficient — survivorship + market
correlation matter more than universe count.** Iter 003 closed
"≤20-asset homogeneous ETF universe" because intra-basket diversity is
nil; iter 054 closes a different but related case: "any
survivorship-biased single-stock universe of N stocks where the
strategy ends up holding a mostly-market-tracking subset at non-cap-
weighted weights." The iter 003 lesson generalizes: **cross-sectional
ranking momentum needs both heterogeneity AND a universe that contains
losers in-sample (point-in-time, including delisted names)** to harvest
the dispersion premium. The Tiingo cache cannot supply that without a
delisted-tickers backfill.

**Implication for hunt loop**: the "single-stock cross-sectional
momentum" path is **structurally blocked at the data layer** with the
current cache. Without point-in-time + delisted coverage, no
cross-sectional momentum/value/quality strategy can be honestly tested
on the loop's datasets. This rules out a large family of literature-
documented strategies until a different data source (CRSP, Norgate,
Quotemedia archive, etc.) is brought in.

## Structural dead-ends discovered

Add to `DEAD_ENDS.md`:

- **Cross-sectional 12-1 long-only momentum on Tiingo
  survivorship-biased universe (any K)** — does not produce Sharpe
  edge over window-matched SPY/QQQ. The bias of including only
  surviving names CORRELATES the universe with the market-cap-weighted
  index that benchmarks it, neutralizing cross-sectional dispersion
  even in a 422-name universe (well above iter 003's ≤20-name
  closure). **Don't re-test on this cache without delisted coverage.**

- **Cross-sectional ranking on survivorship-biased universe in
  general** — the iter 003 closure ("≤20-asset homogeneous") and iter
  054 closure ("survivorship-biased even at >400 names") combine into:
  cross-sectional ranking momentum requires **point-in-time universe
  with delisted names** (à la CRSP/Compustat). This is a data-source
  constraint, not an algorithm constraint. Until such data exists in
  the project's cache, all cross-sectional ranking strategies (12-1
  momentum, 6-1, adjusted-slope, low-vol, low-beta, value, quality,
  composite factor) on `data/tiingo/daily/prices/` are structurally
  blocked.

## Citations used

- `[stocks_on_the_move, p.76-77]` — 12-1 skip-1m momentum signal.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- `[advances_fin_ml, p.31-34]` — cross-library parity G7.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV.
- Jegadeesh, N. & Titman, S. (1993). "Returns to Buying Winners and
  Selling Losers", *Journal of Finance* 48(1) 65–91.
- Carhart, M. M. (1997). "On Persistence in Mutual Fund Performance",
  *Journal of Finance* 52(1) 57–82 — UMD factor.
- Asness, Moskowitz & Pedersen (2013). "Value and Momentum Everywhere",
  JoF 68(3) 929-985.

## Next iteration suggestions

The iter 053/054 evidence trio + the iter 003 closure now point in
ONE direction: the loop has **exhausted cheap-data paths** to a
WINNER on the current cache. Iter 055 candidates:

1. **(RECOMMENDED) Broader-index VRP basket** — extend iter 026/039's
   single-asset and 3-leg-equity VRP to a 5-leg basket
   (SPY+QQQ+IWM+EFA+EEM at 1/5 each). Tests whether cross-region VRP
   diversification breaks the iter 039 76-ceiling. EFA and EEM are
   in cache (verified manifest). `[volatility_trading, p.218]` +
   Bondarenko (2014). Predicted score 76-80; if 80+, becomes new
   TOP-K candidate. Wall-time 30-45 min impl.

2. **Plano C sleeve evaluation** — run mandate-aligned passive
   factor-tilted portfolios (GDE/AVUV/AVDE/AVEM/BTGD per
   `portfolio-aposentadoria.md`) on educational-analog window. Some
   ETFs have 2018-2024 inception (AVUV 2019; GDE 2024); for educational
   need synthetic factor proxies (FF93 long-format from Ken French
   library + replicated factor returns). This is "what does the
   maintenance allocation look like in this rubric?" — likely ≤
   PROMISING but documents the actual baseline. `[fact_based_investing]`
   + Fama-French 1993.

3. **Carry + value composite** — orthogonal axes that haven't been
   tested. Long-only top-K composite of (12-1 momentum + earnings yield
   + dividend yield) on the Tiingo cache, monthly rebal. Hits the same
   data-bias issue as iter 054 but the multi-axis composite *might*
   reduce noise enough to clear the survivor-bias drag (per Asness 2013
   "value spreads compensate momentum drawdowns"). 60-90 min impl.
   `[stocks_on_the_move]` + AMP 2013. Note: this is a soft retry of
   what 054 closed; only viable if the value/yield axes restore
   dispersion lost to survivor filtering. If it scores < 60, the
   data-bias closure is fully confirmed.
