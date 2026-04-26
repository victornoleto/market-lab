# Iteration 019 — IC-7 Markowitz tangency on RSI(2)+SMA(200) MR (iter 003) + COT z-score positioning (iter 018)

## Hypothesis

iter 018 confirmed at a 2nd independent measurement that iter 003's RSI(2)
mean-reversion stream and iter 018's rolling-156w z-score COT-positioning
stream are **structurally orthogonal at consistent daily granularity**:
ρ(gld_long) = +0.013 (n=5 384), ρ(xauusd_real) = +0.004 (n=1 700). Both
streams have *positive standalone Sharpes* on gold buy-hold-net-of-cost
(iter 003: +0.299/+0.193 gld/xauusd; iter 018: +0.352/+0.289). This is
the **first iteration in the loop's 18-iter history** with both
standalone Sharpes positive AND ρ < 0.05 simultaneously.

Per Lopez de Prado's combined-Sharpe formula
`[advances_fin_ml, p.222-223]`, when ρ → 0 a 2-stream tangency portfolio
delivers Sharpe ≤ √(S_A² + S_B²). For gld_long the upper bound is
**√(0.299² + 0.352²) ≈ 0.46** — still below buy-hold + 0.10 = 0.78,
so this iteration cannot realistically score WINNER, but it should
deliver:
- the loop's first composed Sharpe ≥ 0.45 on gld_long,
- DSR p-value drop toward ~0.10 (1 − ρ²)^0.5 uplift on the n_trials=19
  cumulative penalty, possibly to within G2's 0.05 threshold,
- MDD compression by uncorrelated-risk diversification (iter 003 ~12.5%
  MDD + iter 018 ~25.3% MDD → expected ≤ 20% with positive weight on
  both),
- an empirical anchor for iter 020+'s 3-stream composition (003+011+018,
  or 003+018+DCOT-money-manager).

The composition reuses each stream's already-cost-net-of-Pepperstone-CFD
daily returns at full-sample Markowitz tangency weights w ∝ Σ⁻¹μ; no
new cost is introduced (composition is capital allocation, not a new
trade).

## Primary citation

`[advances_fin_ml, p.222-223]` — López de Prado: Deflated Sharpe Ratio
with cumulative n_trials; combined-Sharpe upper bound under ρ-bounded
2-asset portfolios is the canonical reference. Sister loop empirical
IC-7 (sessions 045/046) confirms ρ < 0.50 + proportional-Sharpe weights
(Markowitz, NOT 50/50 per IC-3) compounds DSR.

## Additional citations

- `[advances_fin_ml, p.31-34]` — cost realism: composition introduces
  no new turnover; reuses each stream's pre-deducted Pepperstone costs.
- `[short_term_trading_strategies, p.106]` (Connors) — RSI(2)<5 +
  SMA(200) regime filter (iter 003 base).
- `[trading_systems_methods, p.639-640]` (Kaufman) — COT positioning
  z-score variant (iter 018 base; de Roon-Nijman-Veld 2000 citation).
- IC-7 sister-loop empirical (`studies/strategy_hunt_loop/` 045/046) —
  out-of-family ρ < 0.50 streams compound DSR via Markowitz tangency.
- IC-3 sister-loop closure (049) — Markowitz proper (NOT 50/50) when
  Sharpes differ.

## Edge source

Single-stream gold strategies have plateaued at Sh ≈ 0.55 (iter 011
vol-regime max + GS-14 ceiling). Buy-hold drift on gold is +0.68 on
gld_long. The gap of 0.13 cannot be closed by any modulation of an
existing single-stream signal; it requires **adding a genuinely
orthogonal return source**. iter 018's ρ ≈ 0 result on iter 003 RSI MR
is the loop's only confirmed structurally-orthogonal pair, and this
iteration tests whether their tangency combination converts that
orthogonality into a measurable Sharpe lift toward the Sh-0.78 winner
threshold and the DSR-0.05 significance bar.

## Datasets

- **gld_long (PRIMARY, GLD daily 21.4y)**: `[advances_fin_ml, p.222-223]`
  DSR mathematics is most credible on the longest sample. ρ confirmed
  at 2 independent measurements (iter 017 +0.003, iter 018 +0.013).
- **xauusd_real (CORROBORATING, XAUUSD daily 6.3y)**: ρ confirmed
  +0.004 (n=1700) — relaxed gates (G6 bootstrap CI low > 0, G2 DSR
  p < 0.20) per v2 rules suffice.
- **xauusd_intraday: NOT AVAILABLE.** iter 018 did not run on
  intraday (its run_backtest.py only loads `gld_long` + `xauusd_real`),
  so the composition cannot include this dataset. Adding it would
  require re-running iter 018's 1h pipeline first (separate iter or
  data-infra spillover). The v2 relaxed-rules path (1 primary +
  ≥1 corroborating) is satisfied without it.

## Timeframes used

`["1d"]` only. Both component streams are at daily granularity; the
composition is a daily-bar weighted sum.

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A only). Both component
returns series are already net of Pepperstone CFD costs (8 bps spread
RT + −1 bps/cal-night swap). Composition introduces no new trades.

Track B (Inter ETF) is **not modelled** here for two reasons:
1. iter 003 and iter 018 components both include short-side trades
   (RSI MR has shorts when RSI > 95; COT extreme-bullish entries are
   long-only but the iter 003 base mixes both directions). Inter is
   long-only.
2. DARF 15% on monthly net profits would be a non-trivial re-run of
   each component under Inter cost-model, not a composition step.
   Defer to a separate Track B iter only if Track A composition
   delivers an above-threshold result.

## Hold-time profile (HARD GATE)

- **Declared track**: `medium_swing` (10 ≤ mean ≤ 30 trading days).
- **Reasoning**: composition inherits a weighted blend of iter 003's
  ~4d MR holds and iter 018's ~28d positioning holds. With Markowitz
  tangency at ρ ≈ 0, weights are roughly proportional to Sharpe per
  unit risk; if w_003 ≈ 0.5 and w_018 ≈ 0.5, the exposure-weighted
  mean hold ≈ 16d → medium_swing.
- **Verification**: post-run, compute the composite "exposure days"
  metric (= weighted-avg of component mean holds × respective weights).
  If observed falls in [2,10]: re-classify as short_swing (no penalty,
  just bucket update). If observed falls in [10,30]: pass medium_swing.
  Mismatch only fires if observed < 2d or > 30d.

The composition is NOT intraday (medium_swing → Track A overnight swap
applies; preserved in component cost models).

## Pre-validation screen (mandatory for overlays per IC-6)

- IC-6 applies to **overlay/composition** strategies. This is a
  composition (additive return streams), so pre-val is mandatory.
- The relevant pre-val signal is **ρ(stream_A, stream_B)** at
  consistent daily granularity. Iter 018 already measured this in
  its `correlation_diagnostic`:
  - gld_long (n=5384): **ρ(iter003, iter018) = +0.013**
  - xauusd_real (n=1700): **ρ(iter003, iter018) = +0.004**
- IC-6 threshold: `exceed_frac(|ρ_rolling60d| > 0.30) > 20%` would
  abort. The iter-018 measurement is full-sample static ρ; rolling
  60d ρ is recomputed in this iter as a process safeguard. If rolling
  ρ > 0.30 on > 20% of bars on PRIMARY, iter ABORTS at Stage 3.
- Cost-magnitude gate (IC-6 augmented, GS-9 corollary): both streams
  individually already passed cost-magnitude with positive standalone
  Sharpes; the composition adds no turnover.

## Cost model

**Track A (Pepperstone CFD)**: 8 bps spread RT + −1 bps/cal-night swap.
Both component returns are pre-deducted; composition is a linear sum
of net daily PnL. No additional cost is added.

Composition does NOT incur:
- Re-balancing turnover (held at full-sample Markowitz weights, which
  are static by definition; intra-rebal would require a rolling-window
  re-fit not specified here).
- Margin doubling (full-investment normalization w_A + w_B = 1; total
  capital exposure ≤ |w_A| + |w_B| = 1.0 if both weights positive).

If Markowitz tangency produces a negative weight on either stream
(possible when one stream's Sharpe / σ ratio dwarfs the other), clamp
to (1.0, 0.0) corner — i.e., disable IC-7 and report the non-clamped
stream's standalone metrics. iter 012's clamp logic is reused.

## Kill criteria (pre-committed)

This iteration is FALSIFIED at Stage 3 (and tier auto-downgraded to
NEAR_FAIL) if any of these fire on the **gld_long primary dataset**:

1. **Composition Sharpe destruction** — combined Sh < max(Sh_003, Sh_018) − 0.05.
   The IC-7 hypothesis is that combination LIFTS Sharpe; if it
   *destroys* even by 5 bp vs the best component, the orthogonality
   measurement was an artifact and the iter is closed.
2. **Markowitz weight collapse** — tangency forces |w_negative| > 0.05
   (i.e., a negative weight large enough to materially short one
   stream). Pre-committed semantics is "additive long combination";
   negative weights mean the data wants to *invert* a stream, which
   is a different hypothesis (closes the additive 003+018 path).
3. **DSR no-progress** — combined DSR p > 0.20 (no improvement vs
   iter 018's 0.354 within 17pp of relaxation threshold). The IC-7
   hypothesis is that ρ ≈ 0 uplifts DSR via Bonferroni-deflator
   relief; absence of any improvement closes the path.
4. **Pre-val rolling-ρ violation** — `exceed_frac(|ρ_60d| > 0.30) > 20%`
   on gld_long. Static ρ ≈ 0 may mask occasional regime co-movement;
   if rolling ρ violates IC-6, the orthogonality assumption is wrong
   and the static-ρ Markowitz weights are mis-specified.

If any kill fires, Stage 4 runs with the FAIL flag for accounting
purposes but the lesson recorded in BASE_MEMORY is the kill, not the
score.

## Expected budget

- **Configs to test**: 1 (single Markowitz tangency cfg, IC-8 honored).
- **Wall-time**: ~5-10 minutes (loading 2 saved returns series + 2
  joins + 2 7-gate batteries + 1 pre-val rolling check).
- **Files to create**:
  - `iterations/019-*/run_backtest.py`
  - `iterations/019-*/test_composition.py` (TDD on tangency + compose)
  - `iterations/019-*/results.json`
  - `iterations/019-*/verdict.json`
  - `iterations/019-*/final_report.md`

## Implementation plan

1. **TDD primitives** (`test_composition.py`):
   - `test_markowitz_tangency_uncorrelated`: at ρ=0, weights ∝ μ/σ²;
     verify analytical match.
   - `test_compose_returns_inner_join`: weighted-sum on intersection
     of two indices; verify length and value at known dates.
   - `test_load_iter003_schema_a`: `results.json[returns_series][ds][cfg_id]`.
   - `test_load_iter018_schema_b`: `results.json[datasets][ds][returns_series]`.
   - `test_rolling_rho_60d`: 60-bar rolling Pearson ρ on uncorrelated
     synthetic streams stays |ρ| < 0.30 most bars.
2. **Loader functions**: schema-aware reader for both iter 003 (Schema A)
   and iter 018 (Schema B); return `pd.Series` indexed by daily date
   in tz-naive UTC.
3. **Composition pipeline** (`run_backtest.py`):
   - Load `gld_long` and `xauusd_real` daily nets from iter 003 + iter 018.
   - Join inner; compute μ_A, μ_B, σ_A, σ_B, ρ; fit tangency weights;
     clamp if negative.
   - Pre-val: rolling 60d ρ exceedance; abort iter if > 20%.
   - Compose: w_A·r_A + w_B·r_B (new daily series).
   - Run 7-gate battery (PBO N/A by convention — IC-8 single cfg;
     DSR with n_trials=19; WF 8 windows; OOS 70/30; FWD post-2022;
     bootstrap 99.9% CI; cross-lib pandas vs numpy CAGR).
   - Fire kill checks; record verdict.
   - Compute exposure-weighted hold days for hold-time gate.
4. **v2 scoring**:
   - `score_strategy_v2(metrics, gates, n_trials=19, declared_primary="gld_long",
     declared_corroborating=["xauusd_real"])`.
   - Tier from rubric.
5. **Cumulative `n_trials`**: 18 (prior) + 1 (this composition) = 19.
6. **Hold-time bucket validation**: post-run, compare observed
   exposure-weighted hold to declared bucket.
7. **Output**: `results.json` (full diagnostics + returns_series for
   future iter 020 3-stream composition), `verdict.json` (v2 schema +
   composition-specific fields: weights, ρ, kill outcomes), and
   `final_report.md` (verdict + lesson + dead-end if applicable).

Citations recap (every implementation-decision touchpoint):
- Markowitz tangency formula: `[advances_fin_ml, p.222-223]` (DSR +
  combined-Sharpe upper bound) + classical mean-variance optimization
  in any of the absorbed books (e.g., `[risk_parity, ch.2]`).
- Cost realism: `[advances_fin_ml, p.31-34]`.
- Streams' base citations carry over: `[short_term_trading_strategies,
  p.106]` (RSI MR), `[trading_systems_methods, p.639-640]` (COT z-score),
  `[volatility_trading, p.58-59]` (regime filter context), de Roon-Nijman-
  Veld 2000 (positioning hedge-pressure).
