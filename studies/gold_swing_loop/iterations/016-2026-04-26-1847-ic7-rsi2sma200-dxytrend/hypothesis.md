# Iteration 016 — IC-7 Markowitz tangency: iter 003 (RSI-MR + SMA200) + iter 015 (DXY-SMA-slope trend gate)

## Hypothesis

Compose the two highest-orthogonality single-stream gold strategies discovered
through iter 015 — iter 003's `connors_rsi2_sma200_filter` (mean-reversion
family) and iter 015's `dxy_sma_slope_falling_200_20_long_only` (USD-trend macro
family) — at full-sample Markowitz tangency weights. On `xauusd_intraday` the
pairwise daily-aggregated correlation is ρ = **−0.07** — the lowest |ρ|
between any two streams produced by this loop. Per IC-7 (sister 045/046) the
DSR uplift from out-of-family composition is approximately
`(1 − ρ²)^0.5 ≈ 0.998` of the orthogonal limit, i.e., this is structurally
the best IC-7 setup the gold loop can construct from existing inventory.

## Primary citation

`[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio with cumulative
n_trials; the explicit motivation for a composition that doesn't add a new
backtest signal yet attempts to clear DSR significance via diversification.

## Additional citations

- `[short_term_trading_strategies, p.105-118]` — Connors RSI(2) + SMA(200)
  trend-regime filter (iter 003 base)
- `[stocks_on_the_move, p.100]` — 200-day SMA canonical trend filter applied
  to DXY in slope grammar (iter 015 base)
- `[trading_systems_methods, p.13-14]` — gold/USD inverse coupling (iter 015 base)
- `[modern_portfolio_theory]` — 2-asset Markowitz tangency via Σ⁻¹μ normalized
  (composition math)
- IC-7 (sister loop iter 045/046) — out-of-family ρ < 0.50 unlocks DSR uplift
- IC-3 (sister loop iter 049) — Markowitz proper (NOT 50/50) when |ΔS| > 30%
- IC-8 (sister loop iter 046) — single pre-committed cfg per iter
- Web: López de Prado 2018 "The Sharpe Ratio Efficient Frontier"
  (https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643) — DSR
  diversification uplift bound

## Edge source

Gold buy-hold's drift on `xauusd_intraday` (Sharpe ~1.10, 6.3y) cannot be
matched by any single-mechanism stream this loop has produced (best individual
intraday Sharpe = +0.36 from iter 015), but a near-zero-correlation linear
composition might compress its variance enough to yield a DSR p-value below
the 0.05 threshold even if the absolute Sharpe stays well below benchmark —
the iter answers the question "does ρ ≈ 0 actually deliver IC-7's predicted
DSR uplift on real gold streams, or is the 0.43 Sharpe ceiling a hard
statistical wall?".

## Datasets

- **Primary**: `xauusd_intraday` — pairwise ρ = −0.07 (lowest), daily-aggregated
  for composition (1h native resampled to D — same convention as iter 012);
  the dataset where IC-7 uplift is theoretically maximized
- **Corroborating**: `gld_long` (ρ = +0.17, 21.4y) — robustness across the
  longest gold-history window
- **Corroborating**: `xauusd_real` (ρ = +0.22, 6.3y daily) — 2020+ regime
  cross-check on the actual instrument

## Timeframes used

`1d` (composition aggregates xauusd_intraday's hourly returns to daily before
joining with iter 003's daily-resampled signal). Aggregation pattern follows
iter 012 exactly. **No 30m / 15m / 1m data used** (cTrader fetch deferred).

## Universe

`single_xau` — both component streams operate on a single gold instrument per
dataset (GLD ETF, XAUUSD spot, XAUUSD intraday). No multi-asset basket.

## Broker tracks targeted

- **Primary: `pepperstone_cfd` (Track A)** — both component streams are
  already cost-included with Pepperstone CFD spread (8 bps RT) + swap
  (−1 bps long / +0.3 bps short per night). Composition is capital allocation
  only; no additional cost layer.
- **Track B (Inter ETF) reported as secondary** — long-only by construction
  (both component streams are long-only). DARF 15% / FX 100 bps RT applied to
  the *combined* daily returns. GS-2 cliff caveat: Inter would not be
  economically viable here regardless of iter 016's outcome.

## Hold-time bucket (declared, HARD GATE under v2 rules)

**`medium_swing` (10-30 trading days, declared)** — the composition's effective
hold profile is dominated by the higher-Sharpe stream (iter 015's
~113-day-on-intraday slow regime), partially shortened by iter 003's ~3.75-day
fast MR. The realistic mean is likely in the 30-80-day range.

**Honest disclosure**: the observed mean hold may exceed `medium_swing`'s
30-day upper bound. If observed > 30d → tier downgraded to NEAR_FAIL per
WINNER_AND_RANKING.md condition #6 (declaration mismatch). This is treated as
a process-level honest record, not a strategy result. The downstream insight
(IC-7 at ρ ≈ 0 lifts DSR or it doesn't) is independent of the hold-bucket
mismatch.

## Pre-validation screen (mandatory for overlays per IC-6)

Composition is NOT a regime overlay (it does not modulate one stream's
position by another's signal). It is an additive Markowitz portfolio of two
already-validated streams. The IC-6 correlation pre-screen (overlay-signal vs
base-position) does not apply directly. Instead, we report the **diagnostic**:

- Pairwise correlation ρ(r_003, r_015) on the inner-joined daily index, per
  dataset, must match (within ±0.05) the values measured by iter 015's
  `ic7_diagnostic` (gld +0.43 vs iter 011 in 015's report ≠ this iter's
  gld +0.17 vs iter 003 — those are correlations against *different* base
  streams; the +0.17/+0.22/−0.07 values from iter 015 vs **iter 003** are
  the relevant ones, per BASE_MEMORY iter 015 entry).

If observed |ρ| > 0.30 on the primary dataset (xauusd_intraday), the BASE_MEMORY
−0.07 figure is in error and the iter 016 thesis is re-considered.

## Cost model (per track)

**Track A (Pepperstone)**: each component stream has its costs already netted
(spread 8 bps RT + swap −1 bps long/+0.3 short per night, applied via
`cost_models.apply_pepperstone_costs` in iter 003 / iter 015). Composition adds
no further cost — Markowitz weights are capital-allocation, equivalent to
splitting capital between two strategies that each pay their own costs.

**Track B (Inter ETF)**: applied to the *combined* daily PnL, treating it
as if the gold-ETF position size were the combined w_A·pos_A + w_B·pos_B
exposure. FX 100 bps RT, DARF 15% on monthly net profit. Reported for
completeness; GS-2 cliff applies (>15 trades/yr drains CAGR).

## Expected budget

- Configs to test: 1 (single Markowitz tangency cfg per IC-8)
- Wall-time: ~3-5 min (no new simulation; just compose pre-saved returns)
- Files to create:
  - `hypothesis.md` (this file)
  - `test_composition.py` (TDD: tangency-weight properties + composition math)
  - `run_backtest.py` (mirror iter 012; swap iter 011 → iter 015; v2 scoring)
  - `results.json`, `verdict.json`, `final_report.md` (after run)

## Implementation plan

1. Reuse iter 012's `markowitz_tangency_weights`, `compose_returns`,
   `aggregate_intraday_to_daily` primitives via tested copy (TDD test verifies
   tangency formula on a known closed-form input).
2. Load iter 003 returns and iter 015 returns per dataset from each iter's
   `results.json` `returns_series` block.
3. Aggregate iter 015's `xauusd_intraday` 1h returns to daily; iter 003's
   `xauusd_intraday` is already daily-resampled (1700 bars); inner-join.
4. Fit Markowitz tangency at full-sample (per dataset); clamp to corner if
   either weight < 0.
5. Run 7-gate battery on combined returns at daily granularity (ann=252).
6. Compute mean-hold from a synthesized combined position series:
   `pos_combined[t] = sign(w_003·pos_003[t] + w_015·pos_015[t])` (treating
   the binary "in any trade" indicator) — diagnostic only.
7. Score with `scoring.score_strategy_v2(declared_primary="xauusd_intraday",
   declared_corroborating=["gld_long","xauusd_real"])` —
   `cumulative_n_trials = 16` (15 prior + 1 this iter).
8. Apply hold-time gate per declared `medium_swing` bucket; downgrade to
   NEAR_FAIL on mismatch.
9. Write `verdict.json` + `final_report.md`; update `BASE_MEMORY.md` (top-K,
   iteration log, cumulative_n_trials, frontmatter) + `DEAD_ENDS.md` if a
   new structural closure is established (likely: GS-16 = IC-7 at ρ≈0 on
   gold either delivers DSR<0.05 or doesn't — both outcomes are structural).

## Kill criteria (pre-committed)

This iter's primary value is information, not winning. Concrete kill checks:

1. **DSR no-progress kill** — if combined DSR p ≥ 0.20 on `xauusd_intraday`
   primary AND gld_long DSR p ≥ 0.20 → IC-7 at ρ≈0 cannot lift DSR on gold;
   composition family is closed for further iters. Pivot to BASE_MEMORY
   Priority 2 (CFTC COT positioning) in iter 017.
2. **Sharpe-ceiling-confirmed kill** — if combined Sharpe on
   `xauusd_intraday` < 0.50 (i.e., below the √(0.24²+0.36²) ≈ 0.43 naive
   bound + 17% Markowitz uplift slack), IC-7 confirms Sharpe ceiling
   structurally below intraday-bench's 1.10. (Expected, not strictly a kill;
   already foreseen in BASE_MEMORY.)
3. **Correlation drift kill** — if observed pairwise ρ on `xauusd_intraday`
   has |ρ| > 0.20 (significantly different from BASE_MEMORY's −0.07), the
   prior-iter ic7_diagnostic figure is stale; re-measure and re-evaluate
   before drawing conclusions.

## Risks & honesty checks

- **DSR n_trials drains** (IC-8): iter 016 brings cumulative to 16. The DSR
  threshold tightens by ~0.005 per trial; the composition needs Sharpe-ratio
  *with low variance* to clear p<0.05, not raw Sharpe.
- **Hold-bucket mismatch**: declared `medium_swing` will likely be observed
  as ~30-80d → NEAR_FAIL by mismatch. This is documented up-front; the
  primary deliverable is the IC-7 datapoint, not winner status.
- **Apples-to-oranges Sharpe (xauusd_intraday)**: BENCHMARKS["xauusd_intraday"]
  uses √5119 (hourly ann); composition uses √252 (daily ann). Iter 012
  established this convention; we maintain it for cross-iter comparison.
  Reported edge will be inflated relative to a strict same-frequency benchmark.
