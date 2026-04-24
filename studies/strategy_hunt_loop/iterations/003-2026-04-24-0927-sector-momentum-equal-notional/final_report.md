# Iteration 003 — Final Report

## Verdict

**❌ FAIL (score 7/100, winner_conditions_met=False, tier=FAIL)**

Replacing Clenow's canonical 10 bps ATR-risk-parity sizing with
equal-notional 1/K sizing on the 11 SPDR sector ETFs **fixes the
under-deployment issue from iter 002** (median gross exposure rose from
0.25-0.37 to 1.00-1.76 across the grid) but **reveals that the adjusted-
slope × R² ranking signal itself has no measurable edge on sector ETFs**.
With full capital deployment, the 24-config grid still produces Sharpe
0.15-0.30 across all 3 datasets — roughly **one-third of the SPY/QQQ buy-
hold benchmark** (0.54/0.79/0.91). The kill criterion pre-committed in
`hypothesis.md` §1 fires on all 3 datasets. Sector momentum on the SPDR
universe is a **structural dead-end regardless of sizing rule**.

## Headline metrics (top candidate per dataset)

| dataset | cfg | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | deployment |
|---|---|---|---|---|---|---|
| educational (sectors_long 2006-2026 vs SPY) | k9_L20_lb60 | 0.298 (−0.238 vs 0.536) | 3.78% (−5.09pp vs 8.87%) | 48.52% (−7.95pp vs 56.47%) | 4/7 | 1.55 |
| spy_real (sectors_spy 2009-2026 vs SPY) | k9_L20_lb90 | 0.257 (−0.537 vs 0.793) | 2.96% (−9.97pp vs 12.93%) | 48.22% (+14.12pp vs 34.10%) | 3/7 | 1.75 |
| ndx_real (sectors_ndx 2010-2026 vs QQQ) | k9_L20_lb90 | 0.286 (−0.627 vs 0.913) | 3.57% (−14.58pp vs 18.15%) | 48.35% (+12.73pp vs 35.62%) | 2/7 | 1.76 |

Top configs are all `k9_L20_lb*` — `top_k=9` (nearly equal-weight all 9-11
sectors) + `buy_leverage=2.0` + `lookback_slope` either 60 or 90. The fact
that **near-equal-weight-everything wins the grid** is itself evidence the
ranking signal is not adding value — concentrating in top-3 or top-5 by
score underperforms holding almost all sectors unweighted.

## Score breakdown

Benchmarks **overridden** from `scoring.BENCHMARKS` to reflect measured
SPY 2006-2026 / SPY 2009-2026 / QQQ 2010-2026 over the same windows
(iter 002 established the same override pattern).

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 0 | 25 | 0/3 datasets beat bench + 0.10 (top Sharpe = 1/3 of bench on all 3) |
| 2 Gates | 2 | 25 | edu 4/7 (G3/G4/G5/G7) + spy 3/7 (G3/G5/G7) + ndx 2/7 (G5/G7); no cross-dataset bonus |
| 3 DSR | 0 | 15 | worst p = 0.992 with n_trials=4048 (cumulative) — no significance |
| 4 CAGR floor | 0 | 15 | 0/3 datasets reach 0.8 × benchmark CAGR |
| 5 MDD ceiling | 5 | 15 | 1/3 datasets (educational only — 48.5% ≤ 56.5%+5pp); spy/ndx top cfgs are k9_L20 with MDD 48%+ vs bench 34-36% |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **7** | **100+5** | tier: **❌ FAIL** |

Lower than iter 002's 17/100 mainly because (a) MDD ceiling loses 10 pts
— equal-notional with leverage 2× no longer "trivially passes MDD by being
idle" — and (b) PBO is worse on the larger, more dispersive grid.

## Gate detail (G1-G7)

Per top-candidate per dataset:

| gate | sectors_long | sectors_spy | sectors_ndx | meaning |
|---|---|---|---|---|
| G1 PBO grid < 0.5 | **FAIL** 0.635 | **FAIL** 0.770 | **FAIL** 0.905 | 24-config grid has real return dispersion (k3 concentration vs k9 near-EW), but IS-best / OOS-best rank inversion is severe → textbook overfitting signature `[advances_fin_ml, p.208-211]` |
| G2 DSR p < 0.05 | **FAIL** 0.982 | **FAIL** 0.992 | **FAIL** 0.988 | with n_trials=4048 the Sharpe must clear a high bar; 0.26-0.30 is far below `[advances_fin_ml, p.222-223]` |
| G3 WF 6/8 | PASS 6/8 | PASS 6/8 | **FAIL** 5/8 | passes 2/3 because leveraged deployment now contains drawdowns > 25% in some windows |
| G4 OOS 70/30 | PASS +0.141 | **FAIL** −0.049 | **FAIL** −0.175 | OOS goes negative on real data; signal does not persist into the holdout |
| G5 FWD post-2020 | PASS +0.046 | PASS +0.134 | PASS +0.133 | trivially positive but very small |
| G6 Bootstrap 99.9% CI low > 0 | **FAIL** −0.37 | **FAIL** −0.44 | **FAIL** −0.40 | distribution of resampled Sharpe straddles zero with wide margin — no statistical edge |
| G7 Cross-lib ±3pp CAGR | **PASS** 0.000pp | **PASS** 0.000pp | **PASS** 0.000pp | prod(1+r)^(252/n)-1 reference agrees with engine to 0.000pp — no arithmetic bug |

G7 clean means the weak signal is **real strategy behavior**, not an
engine artifact. This is the same clean-engine finding as iter 002 (both
iterations used the same Runner/Portfolio stack and share the numpy
reference in `tests/test_sector_momentum_equal_notional.py`).

## Configuration tested (grand champion)

- `k9_L20_lb90`: `top_k=9`, `buy_leverage=2.0`, `lookback_slope=90`
- Rest: `lookback_trend=100`, `lookback_regime=200`, `gap_threshold=0.15`,
  `rebalance_weekday=2` (Wed), `position_rebalance_every_n=2`
- Universe: 11 SPDR sectors (XLK/XLF/XLV/XLY/XLP/XLE/XLI/XLU/XLB + XLRE + XLC)
- Regime: SPY > 200d SMA
- Execution: zero commission (Inter-style), half_spread=0.005, slippage=0.005

Grid swept 24 configs = 4 × 3 × 2 (`top_k ∈ {3, 5, 7, 9}` × `lookback_slope
∈ {60, 90, 120}` × `buy_leverage ∈ {1.0, 2.0}`).

## What worked / what didn't

**What worked (partial credit):**

- Equal-notional sizing **fully deploys capital** as designed. Median
  gross-exposure / equity for top candidates is 1.55-1.76 (with
  `buy_leverage=2.0`); for unlevered top-9 configs it's 0.78-0.89 — vs
  iter 002's 0.25-0.37 across the board. Kill criterion #2 (deployment <
  85%) does **NOT** fire → the test is informative, not inconclusive.
- G7 cross-lib parity to 0.000pp on all 3 datasets — the Clenow adjusted-
  slope ranking + equal-notional sizing logic matches the pure numpy
  reference exactly. Any negative result is **real strategy behavior**.
- All 13 new unit tests pass (sizing primitive + strategy integration + G7
  parity). Project baseline stays green.

**What didn't work (the main finding):**

- **The ranking signal does not discriminate meaningfully on 11 SPDR
  sectors.** Sharpe across the 24-config grid spans only 0.15-0.30 on
  all 3 datasets — benchmarks are 0.54-0.91. The best configs across the
  grid are `top_k=9` (hold nearly all sectors, un-weighted by score),
  which means concentrating on top-3 to top-5 sectors by adjusted-slope
  rank actively reduces Sharpe relative to near-equal-weight. This is
  direct empirical evidence that the ranking signal provides no alpha on
  this universe.
- **G1 PBO is worse than iter 002** (0.63-0.91 vs 0.52-0.57). The 24-
  config grid now has real return dispersion (k3 concentration vs k9
  near-EW produce materially different portfolios), but the IS-best /
  OOS-best rank reversal is severe — the winner in-sample is rarely the
  winner OOS. This is the textbook PBO signature of overfitting, not of
  the "small-grid near-zero-regime" noise floor of iter 002.
- **G6 bootstrap 99.9% CI low ≈ −0.40** on all 3 datasets: the stationary
  bootstrap distribution of annualized Sharpe straddles zero with wide
  margin. No statistical evidence of edge even under favorable resampling.
- **G4 OOS 70/30 flips negative** on spy_real (−0.05) and ndx_real
  (−0.18). The late period (post-2019) is particularly bad for this
  strategy on real data; even the weak in-sample Sharpe evaporates.
- **MDD at leverage 2× is 48-72%** — no longer "trivially safe by being
  idle". The top candidates using `buy_leverage=2.0` are meaningfully
  worse than SPY on drawdown (14 pp worse on spy_real, 13 pp on ndx_real).

## Main lesson (for future iterations)

**Sector momentum on the 11 SPDR universe is a structural dead-end for
the cross-sectional-ranking mechanism, independent of sizing.**

The Clenow adjusted-slope × R² ranking was designed for the S&P 500
universe with ~500 constituents (the paper `[stocks_on_the_move, p.58-77]`
is explicit on this). On such a universe, top-10% = 50 names, enough
for the cross-section to spread momentum scores across a long tail — the
ranking has discriminatory power because constituents have idiosyncratic
return variance. On 11 sectors that are themselves diversified portfolios
of ~50-80 constituents each, the cross-sectional return dispersion
**collapses** — every sector's return is dominated by the aggregate
market factor, and idiosyncratic score signals are noise. Hence the
grid's best configs are "hold almost all of them unweighted" (top_k=9
near-EW) rather than "concentrate in the top-scoring few".

This generalizes: **cross-sectional momentum mechanisms need a large
universe with heterogeneous idiosyncratic components to produce a
rankable cross-section of returns.** ≤20-asset universes of
diversified baskets (sector ETFs, factor ETFs, country ETFs) are
structurally too homogeneous for this mechanism to produce alpha.
Future iterations that consider ETF-universe cross-sectional momentum
should either (a) expand the universe to 50+ heterogeneous assets
(single stocks, factor sleeves across multiple geographies, or
country-level ETFs) or (b) use a qualitatively different mechanism
(time-series vol targeting, regime switching, stacked exposure) rather
than cross-sectional ranking.

This finding also refines iter 002's lesson: the "ATR sizing calibration"
issue was real, but fixing it did not resurrect the signal — the signal
was absent in both iterations. Iter 002 masked this by under-deployment;
iter 003 confirms it with full deployment.

## Structural dead-ends discovered

Add to `DEAD_ENDS.md`:

1. **Clenow adjusted-slope × R² ranking with equal-notional 1/K sizing
   on the 11 SPDR sector ETFs** — ranking signal has no measurable edge
   (Sharpe 0.15-0.30 vs bench 0.54-0.91, DSR p > 0.98, bootstrap 99.9%
   CI low −0.37 to −0.44). The grid's best configs are k9 (near-EW
   everything) which is evidence against the ranking signal itself.
2. **Cross-sectional ranking momentum on any ≤20-asset ETF universe of
   diversified baskets** — universe too homogeneous; aggregate market
   factor dominates idiosyncratic score signal. Requires heterogeneous
   idiosyncratic components per asset (single stocks or country-level
   ETFs with dispersed returns) to produce rankable cross-section.

Combined with iter 002's dead-end, this closes the entire "sector
momentum on SPDR" direction regardless of sizing variant.

## Citations used

- Primary: `[stocks_on_the_move, p.70-77, p.82]` — adjusted slope × R²
  ranking formula
- `[stocks_on_the_move, p.60]` — Jegadeesh-Titman 1993 as academic
  foundation for equal-weight cross-sectional momentum
- `[stocks_on_the_move, p.66-67, p.98-99]` — SPY 200d SMA regime filter
- `[stocks_on_the_move, p.81]` — 100d SMA per-asset trend filter
- `[advances_fin_ml, p.298-299]` — Markowitz's curse / 1/N prior
  motivation for equal-notional sizing
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1)
- `[advances_fin_ml, p.222-223, p.275]` — DSR with cumulative n_trials (G2)
- `[advances_fin_ml, p.196-202]` — bootstrap CI for trade returns (G6)
- External: Jegadeesh & Titman (1993), *Journal of Finance* 48(1) 65-91,
  DOI 10.2307/2328882 — the academic origin of cross-sectional momentum.
  Their universe was NYSE/AMEX individual stocks, consistent with the
  "need heterogeneous idiosyncratic components" lesson above.

## Next iteration suggestions

Three structurally different directions that this iteration's findings
point toward:

1. **Volatility-managed SPY (continuous vol scaling)** —
   `[systematic_trading, ch.9, p.107-111]` Carver vol-targeting +
   Moreira-Muir-Muir 2017 *Journal of Finance* "Volatility-Managed
   Portfolios". Mechanism: scale SPY exposure by `target_vol /
   realised_vol_{t-1}` with leverage cap. No ranking, no cross-section,
   no threshold. Single asset, continuous signal. Existing infra:
   `src/ai_trade/backtest/metrics/vol_target.py` already implements the
   no-look-ahead vol-target primitive. Low implementation cost,
   ex-ante different mechanism than iter 001/002/003.

2. **Return-stacked rotation NTSX/NTSI/NTSE** — BASE_MEMORY direction #2.
   3-way rotation between return-stacked US/International/EM equity +
   bond products based on 6-month momentum. Different edge source
   (stacked exposure + geographic diversification). Data requires
   downloading NTSX/NTSI/NTSE (2018+ history; would need proxies or a
   shorter validation window).

3. **Stocks-bonds regime switching SPY ↔ TLT via correlation sign** —
   BASE_MEMORY direction #8. 60-day rolling correlation between SPY
   and TLT daily returns as regime signal: < 0 → 60/40 static,
   > 0 → reduce TLT weight. Different mechanism (correlation-based
   regime, not price-based). Citation: `[risk_parity]` or
   `[regime_change, ch.2]`. Data is available (SPY, TLT both cached
   17y). Qualitatively different from anything tested so far.

Pick one per future iteration. Do NOT mix. Iter 004 should pick **(1)
volatility-managed SPY** — simplest to implement, uses existing infra,
tests a structurally different mechanism (single-asset continuous
scaling vs cross-sectional ranking).
