# Iteration 012 — IC-7 composition: iter 003 (RSI(2)+SMA(200) MR) + iter 011 (inverse vol-regime σ_60<σ_252) at Markowitz proportional-Sharpe weights

## Hypothesis

Combine iter 011's **inverse vol-regime gate** (long XAUUSD when σ_60d < σ_252d;
slow regime, 41-53% time-in-market, 44-52d holds, swing-extended) with iter 003's
**Connors RSI(2)<5 + SMA(200) trend filter** (fast mean-reversion, ~5d holds,
gld_long single-mech +Sh standalone) at **per-dataset Markowitz tangency
weights** computed on the joined daily net-return series.

Mechanism: each stream operates a fraction (w_011, w_003) of capital in its own
sub-account with its own cost-stream. The composition's daily return is
`r_combined = w_011 · r_011_net + w_003 · r_003_net`. Costs are already
inside each component (cost-realistic per `cost_models.py`).

**Goal**: lift `gld_long` DSR p-value above the 0.05 threshold (currently 0.275 on
iter 011 standalone) while preserving xauusd_real / xauusd_intraday's already-
strong gates 7/7 + DSR p<0.05. Sister 045/046 IC-7 best result was ρ=0.41 →
DSR 0.222→0.041 (−81% improvement). Iter 011 reports ρ ≈ +0.10 / +0.10 / 0.00
vs iter 003 — squarely in IC-7's sweet spot.

## Primary citation

`[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials; the deflator
penalty for trial 12 is offset only if the composition's per-stream
diversification compounds Sharpe above each stream's standalone level.

Sister loop's IC-7 framework (iters 045/046) is the procedural template
(see `studies/strategy_hunt_loop/DEAD_ENDS.md` IC-7).

## Additional citations

- `[modern_portfolio_theory]` Markowitz tangency portfolio formula:
  for two streams with means μ_A,μ_B, vols σ_A,σ_B, correlation ρ, the
  max-Sharpe weights are `w = Σ⁻¹μ` normalized so `w_A + w_B = 1`.
- `[advances_fin_ml, p.196-202]` — bootstrap confidence intervals.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest (each component's
  net returns already pay Pepperstone CFD costs, so the combined series
  needs no additional cost layer beyond the components).
- `[short_term_trading_strategies, p.105-118]` — Connors regime-filter rule
  (the iter 003 component, here used unchanged).
- `[volatility_trading, p.58-59]` — Sinclair vol cone framework
  (the iter 011 component, here used unchanged).
- `[trading_systems_methods, p.13-14]` — Kaufman: "metals = low-noise →
  trending" (the iter 011 directional choice σ_60<σ_252, here used unchanged).
- IC-7 (sister iter 045/046) — out-of-family composition at corr<0.50
  compounds DSR proportionally to (1−ρ²)^0.5. Empirically validated.
- IC-3 (sister iter 049) — 50/50 weighting only when Sharpes similar.
  iter 011 (Sh ~1.4 on xauusd) and iter 003 (Sh ~0.2 on xauusd) have
  Sharpe ratio mismatch > 5×, so 50/50 is closed; Markowitz proper required.
- IC-8 (sister iter 046/047/050) — single pre-committed cfg per iter to
  avoid DSR drain. Here: ONE composition, ONE weight scheme (full-sample
  Markowitz tangency).

## Edge source

XAUUSD buy-hold misses risk-adjusted optimization across volatility regimes:
- iter 011 captures **slow regime drift** (low-σ trend periods)
- iter 003 captures **fast pullback reversals** within bull regimes
The two mechanisms fire on near-orthogonal time-windows (ρ ≈ +0.10), so
combining at proportional weights compresses portfolio variance while
preserving the dominant stream's mean drift. Buy-hold has no such
mechanism — it's exposed continuously to both up and down vol regimes.

## Datasets

- **gld_long** (GLD daily, 2004-11-18 → 2026-04-15, 21.4y) — primary
  diagnostic; iter 011 weak link (Sharpe +0.48 vs bench +0.68; DSR p=0.275).
  Composition's **decisive test** is whether ρ ≈ +0.10 with iter 003
  pushes p<0.05 here.
- **xauusd_real** (XAUUSD spot daily, 2020-01-02 → 2026-04-17, 6.3y) —
  iter 011 already 7/7 gates + DSR p=0.018; composition expected to
  preserve or marginally improve.
- **xauusd_intraday** (XAUUSD spot 1h, 2020-01-02 → 2026-04-17) — same
  as xauusd_real but at 1h frequency. iter 011 already 7/7 + p=0.009.
  iter 003 was tested on daily-resampled version of this dataset, so
  composition aggregates iter 011's 1h net-returns to daily and combines
  at daily granularity (the only frequency where both streams exist).

## Timeframes used

- **1d** (gld_long, xauusd_real, xauusd_intraday-as-daily-resampled)

iter 011's xauusd_intraday returns are 1h-frequency. To compose with
iter 003's daily-frequency returns, aggregate iter 011's 1h net-returns
to daily sums. The composition is therefore evaluated at daily resolution
across all 3 datasets (consistent with iter 003's resampled approach).
This does **not** lose information — the daily aggregate of 1h net returns
equals the strategy's day-by-day capital-account PnL.

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A primary).

Both iter 003 and iter 011 are LONG-ONLY {0,1} positions, so the
composition is also long-only. Track B (Inter ETF) is reported as
secondary diagnostic but not the primary track because:
- iter 011 already shows GLD-FX cliff partially erodes gld_long via
  Track B (Sh +0.22, MDD blown to 53.7%).
- DARF on monthly profits is structural drag.
- Composition's primary value-add (DSR uplift on gld_long) is on the
  Track-A net returns; Track B reporting doesn't change the IC-7
  hypothesis test.

## Hold-time profile

Expected mean hold (composition): ~30-40 days (weighted average of
iter 011's 44-52d at ~65-87% weight + iter 003's ~5d at the residual).

**Hold-time gate (≤ 5 trading days) is expected to FAIL** — composition
inherits iter 011's swing-extended mechanic. **Tier ceiling is therefore
STRONG with `swing-extended` tag**, NOT WINNER. This is a known mission-fit
limitation acknowledged in iter 011's report ("regime-gate mechanics are
fundamentally swing, not day"). The IC-7 test is still valuable because:
1. It **closes or opens** the 11-iter best path forward.
2. STRONG tier with rigorous DSR + cross-dataset gates = top-K winner
   for the next-phase reactivation slot (a swing complement to whatever
   eventual day-strategy passes the 5d gate).
3. The Markowitz-on-gold framework is reusable for future compositions.

## Kill criteria (pre-committed)

Falsified if **ANY** of:

1. **gld_long DSR p remains ≥ 0.05** AND iter 011 standalone xauusd_real DSR p
   degrades by ≥ 0.020 (i.e., 0.018 → 0.038+). Means composition adds
   variance without DSR uplift — IC-7 path closed for this combination.
2. **2/3 datasets show net-Sharpe < iter 011 standalone − 0.10**. Means
   adding iter 003 to iter 011 is value-destructive.
3. **Computed Markowitz weight w_003 < 0** (would imply shorting iter 003,
   inconsistent with this iter's framing). If the formula returns negative
   weight, abort and document — it would signal that on the joined sample
   the streams are anti-correlated enough that the right combination is
   long-iter_011 / short-iter_003. That is a different hypothesis.
4. **Composition gates (sum across 3 ds) < 14/21**. iter 011 alone already
   delivered 4+7+7 = **18/21**. Anything below 14/21 = composition
   destroyed gate count → IC-7 fails on gold for these specific bases.

If iter passes kill criteria but not WINNER conditions: tier per scoring;
default expected outcome is STRONG-with-swing-extended-tag.

## Pre-validation screen (IC-6)

**Already satisfied empirically by iter 011's IC-7 diagnostic**:

| dataset | ρ(iter 003, iter 011) | n bars | IC-6 threshold (|ρ|<0.30 on >80%) | pass? |
|---|---:|---:|---:|:---:|
| gld_long          | +0.104 | 5 384 | yes (single full-sample ρ already <0.30) | ✓ |
| xauusd_real       | +0.096 | 1 700 | yes | ✓ |
| xauusd_intraday   | +0.004 | 1 401 daily-resampled | yes | ✓ |

Composition will RE-VERIFY ρ on the joined daily series as a sanity check
in the runner. If any per-dataset ρ flips above 0.30 on the joined sample,
abort with documented mismatch (strict reproducibility check).

## Cost model

**Track A (Pepperstone CFD)**: each component's net returns ALREADY include
spread + swap per its own turnover profile. Combination at weights `w_A + w_B = 1`
is capital allocation, NOT additional positional cost — no new bps to deduct.

**Track B (Inter ETF, daily-only)**: same logic; iter 003 + iter 011 both
report Track B net returns; composition can also report Track B aggregate.

Combined cost summary (informational, computed in runner): per-dataset
weighted-sum of component cost summaries.

## Expected budget

- Configs to test: **1** (single Markowitz tangency weight scheme,
  pre-committed per IC-8). cumulative_n_trials = 11 + 1 = **12**.
- Wall-time: ~2-5 minutes (no new backtest; reuses existing component
  net-returns from `iterations/003-*/results.json` and
  `iterations/011-*/results.json`).
- Files to create:
  - `hypothesis.md` (this file)
  - `run_backtest.py`
  - `test_composition.py` (TDD)
  - `results.json`
  - `verdict.json`
  - `final_report.md`

## Implementation plan

1. **TDD first**: write `test_composition.py` covering:
   - `markowitz_tangency_weights(mu, cov)` → known closed-form for
     2-asset tangency portfolio with synthetic inputs.
   - `compose_returns(r_A, r_B, w_A, w_B)` → linearity + index alignment.
   - `aggregate_intraday_to_daily(r_1h)` → daily sums match expected.
2. **Loader** (`load_component_returns(iter_dir, ds, cfg_id)`): read
   `results.json` returns_series; return `pd.Series` with DatetimeIndex.
3. **Per-dataset composition runner**:
   - Inner-join r_011 + r_003 on common dates.
   - Compute mu_A, mu_B, σ_A, σ_B, ρ.
   - Compute Markowitz tangency w_A, w_B (clamp to [0,1] only if
     numerical noise pushes outside; document if real signal of
     anti-correlation).
   - Compute combined returns; aggregate to a `results.json` block per
     dataset including all 7 gates re-run on combined returns.
4. **Scoring**: feed combined per-dataset metrics into `score_strategy(...)`
   with `cumulative_n_trials=12`.
5. **Hold-time gate**: estimate combined mean hold as the weighted average
   of component holds (info; expected swing-extended).
6. **Cross-lib G7**: compute combined CAGR via pandas + numpy paths;
   confirm ±3 pp parity.
7. Write `final_report.md` with score breakdown, IC-7 ρ diagnostic, weights
   used, kill-criteria check, and structural finding (open or close IC-7
   on gold for these bases).

## Decision rule

After this iter:

- **WINNER** (score ≥ 90 + winner_conditions_met + hold≤5d): impossible by
  construction (hold-time fails). Tier capped at STRONG.
- **STRONG with swing-extended** (score 75-89, all 5 strict winner
  conditions met EXCEPT hold-gate): **IC-7 path validated on gold**;
  next iter = robust OOS validation (rolling-Markowitz weights) and/or
  3-stream composition (asymmetric vol-regime per BASE_MEMORY direction #3).
- **PROMISING** (score 60-74) or **MARGINAL** (40-59): composition lifts
  iter 011 numerically but doesn't clear all 5 strict conditions. Document
  which condition fails and pivot to next-priority direction
  (gld_long bear-regime fix per BASE_MEMORY direction #2 OR asymmetric
  vol-regime per #3).
- **FAIL / NEAR_FAIL** (< 40): IC-7 iter 003 + iter 011 on gold closed.
  GS-12 dead-end candidate. Pivot to BASE_MEMORY direction #2 (single-mech
  iter 011 + SMA(200) regime gate).
