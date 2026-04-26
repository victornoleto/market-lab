# Iteration 016 — Final Report

## Verdict

📉 **NEAR_FAIL** (score 35/100, winner_conditions_met = false, hold_time_gate = fail)

All 3 pre-committed kill criteria fired. Composition produced an honest
empirical reading on IC-7 at the actual ρ available on gold day/swing
streams (re-measured at consistent daily granularity).

## Headline metrics (Track A, Pepperstone CFD net of costs)

| dataset | combined Sharpe (bench Δ) | combined CAGR (bench Δ) | combined MDD (bench Δ) | gates | mean hold (OR-indicator) |
|---|---|---|---|---|---|
| **xauusd_intraday (PRIMARY)** | **+0.381** (Δ −0.722 vs 1.103) | +1.92% (Δ −18.3 vs 20.2%) | 12.0% (vs 24.4%) | 4/7 | **37.9d** |
| gld_long (CORROBORATING) | +0.355 (Δ −0.329 vs 0.684) | +1.53% (vs 11.3%) | 16.5% (vs 45.6%) | 4/7 | 43.4d |
| xauusd_real (CORROBORATING) | +0.346 (Δ −0.692 vs 1.038) | +1.92% (vs 19.9%) | 12.8% (vs 20.4%) | 4/7 | 38.0d |

Per-dataset Markowitz tangency weights (full-sample): w_015 / w_003 =
0.22/0.78 (gld) / 0.40/0.60 (xauusd_real) / 0.34/0.66 (intraday). Iter
003's MR base receives the higher weight everywhere — its lower σ pays
better at this ρ than iter 015's higher Sharpe.

## Score breakdown (v2, rules_version 2026-04-26-relaxed-r1)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 5 | 25 | primary (intraday) Δ −0.72 → 0pt; 2 corroborating Sh > 0 capped at +5 |
| 2 Gates | 15 | 25 | primary 4/7 = threshold (intraday primary thr=4) → +15; corroborating relaxed-pass 0 (G2 DSR fails on both) → no +5; legacy cross-bonus N/A |
| 3 DSR | 0 | 15 | primary p = 0.7844 ≫ 0.20 |
| 4 CAGR floor | 0 | 15 | primary +1.92% < 0.8 × 20.20% = 16.16% |
| 5 MDD ceiling | 15 | 15 | primary 12.0% ≤ 24.4% + 5pp = 29.4% (the only structural advantage) |
| 6 Robustness | 0 | 5 | not computed (caller-set, optional) |
| **total** | **35** | **100+5** | tier: **NEAR_FAIL** |
| (hold-time gate) | **fail** | — | observed 37.9d ∉ medium_swing 10-30d |

(score from `scoring.score_strategy_v2`; full breakdown in
`results.json::score.criteria`.)

## Configuration tested

```yaml
config_id: ic7_iter003_iter015_markowitz_intra_primary
method: markowitz_tangency_full_sample
components:
  iter_003: connors_rsi2_sma200_filter      # RSI(2)<5 + SMA(200) trend filter
  iter_015: dxy_sma_slope_falling_200_20_long_only  # DXY SMA(200) slope falling 20d
weights_per_ds:
  gld_long:        {w_015: 0.2228, w_003: 0.7772}
  xauusd_real:     {w_015: 0.4024, w_003: 0.5976}
  xauusd_intraday: {w_015: 0.3351, w_003: 0.6649}
universe:        single_xau
cost_path:       pep_cfd
broker_track:    pepperstone_cfd
declared_primary:        xauusd_intraday
declared_corroborating: [gld_long, xauusd_real]
declared_hold_track:    medium_swing  # 10-30d
cumulative_n_trials:    16
```

## What worked / what didn't — and ONE big finding

**Worked**:

- Composition mathematically sound; tangency weights all stayed in
  positive corner (no shorting required); inner-join at daily granularity
  produced clean overlapping windows on all 3 datasets (1700-5384 bars).
- MDD on intraday primary cut from 24.4% (bench) to 12.0% (combined) —
  the only criterion the composition genuinely improved.

**Didn't work**:

- Combined Sharpe stayed within the √(S_A² + S_B²) ≈ 0.41-0.42 envelope
  on all 3 datasets, exactly as IC-3 predicts at these correlation
  levels. No diversification "magic" — the composition is doing what
  the math says it should, and the math says you cannot get from
  Sharpe ≤ 0.42 to Sharpe > 1.20 (intraday bench + 0.10) by mixing
  these two streams.
- DSR p-values WORSE than the individual streams' p-values for
  intraday (0.78 combined vs 0.52 for iter 015 alone). The
  cumulative_n_trials=16 deflator is now strong enough that adding a
  trial moves p in the WRONG direction unless the new candidate is
  strictly better than the prior best.

**The ONE big finding (structural, surfaces to GS-16)**: BASE_MEMORY's
claim that "ρ = −0.07 on xauusd_intraday is the highest-orthogonality
pair found" was a **frequency-mismatch artifact** in iter 015's
`ic7_diagnostic`. That diagnostic took iter 015's 32195-bar 1h returns
series and inner-joined directly with iter 003's 1700-bar
**daily-resampled** intraday series, then computed a Pearson correlation
on the join — yielding −0.07 because most timestamps were sparse
matches at hour-of-day intersections that don't represent the true
strategy correlation.

When re-measured at consistent daily granularity (iter 015's intraday
returns first aggregated to daily via `resample("D").sum()` keeping only
days with ≥ 1 input bar), the correlation on `xauusd_intraday` is
**+0.22**, identical to xauusd_real's +0.22. This means **all 3
datasets** show ρ between +0.17 and +0.22 — fully consistent with
GS-15's "macro-generic same-clock" finding (ρ ≈ +0.5 within macro
families) and well-correlated relative to IC-7's < 0.50 threshold for
DSR uplift.

The "highest-orthogonality discovered" entry in iter 015's BASE_MEMORY
update (line 150) was based on a measurement artifact, not a real
diversification opportunity. **There is currently NO sub-0.20 ρ pair
between any two streams the gold loop has produced** when correlations
are computed at consistent frequency.

## Main lesson (for BASE_MEMORY)

IC-7 composition cannot rescue DSR significance on gold day/swing
streams that share the macro-generic same-clock (ρ ≈ +0.17-0.22 is the
**floor**, not −0.07 as the iter 015 diagnostic suggested). The
`(1 − ρ²)^0.5` DSR uplift at ρ = +0.22 is only 0.976 — a 2.4%
diversification benefit, far too weak to bridge the n_trials=16
deflator. Composition family is closed for further iters until a
structurally orthogonal NEW stream is brought in (CFTC COT positioning
is the leading candidate — different family entirely from price/macro/FX).

## Structural dead-ends discovered

**GS-16** — IC-7 composition of single-stream gold strategies cannot lift
DSR below 0.05 within the gold loop's existing 15-stream inventory. The
BASE_MEMORY iter 015 ic7_diagnostic produced a freq-mismatch artefactual
ρ = −0.07 on xauusd_intraday; consistent daily-granularity re-measurement
gives ρ = +0.22, in line with the macro-generic same-clock floor (GS-15).

**Closes**:
- Any further IC-7 composition attempt within the existing 15-stream
  catalog of gold strategies (iters 001-015). Includes: 003+015 (this
  iter), 003+014, 011+014, 011+015, 013+014/015, etc. — all share the
  ρ ≥ +0.17 macro-clock floor and have S < 0.55 individually.
- The "highest-orthogonality intraday pair" claim from iter 015's
  diagnostic. Future iters MUST aggregate to consistent frequency before
  computing pair correlation.

**Does NOT close**:
- IC-7 with a fundamentally orthogonal new stream (CFTC COT / positioning,
  options-implied skew, or microstructure / 1m-data via cTrader). Those
  haven't been built yet; the closure applies only to the current
  catalog.

**How to escape (informs iter 017+)**:

1. **(NEW PRIORITY 1) CFTC COT non-comm net longs gold** (BASE_MEMORY
   prior priority 2 → promoted): weekly CFTC legacy reports back to 1986
   give full gld_long coverage. Positioning is **response** to macro,
   not on the macro clock itself — provides genuine structural
   orthogonality. Cordero 2017 / de Roon-Nijman-Veld 2000 *J Finance* /
   `[trading_systems_methods, p.700+]`.
2. **(NEW PRIORITY 2) Options-implied: gold vol surface / risk-reversal
   skew** — different family entirely. CME GVZ implied vol for gold
   has its own dynamics, plausibly orthogonal to spot-trend.
3. **(NEW PRIORITY 3) Microstructure / liquidity / time-of-day**
   intraday on 30m / 15m / 1m bars (requires "data infra" iter for
   cTrader fetch).

## Citations used

- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 16 (PRIMARY)
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest (each component net of PEP CFD)
- `[short_term_trading_strategies, p.105-118]` — iter 003 RSI(2)+SMA(200) base
- `[stocks_on_the_move, p.100]` — iter 015 DXY-SMA(200) slope grammar
- `[trading_systems_methods, p.13-14]` — gold/USD inverse coupling
- `[modern_portfolio_theory]` — 2-asset Markowitz tangency formula
- IC-3 / IC-7 / IC-8 (sister loop iter 045/046/049)
- López de Prado 2018 *The Sharpe Ratio Efficient Frontier* (SSRN 1821643)

## Next iteration suggestions

1. **Iter 017 — CFTC COT non-comm net longs (PROMOTED to priority 1)**.
   Different family entirely; weekly CFTC legacy reports back to 1986
   (full gld_long coverage). Single signal: long when non-comm net long
   z-score < threshold (commercials extreme short → non-comm overweight
   → mean-revert toward neutral). Expected ρ vs current 15-stream
   catalog: < 0.10 by structural-family argument. Cordero 2017 +
   de Roon-Nijman-Veld 2000 *J Finance*.

2. **Iter 018 (if 017 produces a positive-Sharpe stream) — IC-7 of
   COT + iter 003 (or iter 011)** at Markowitz tangency. The DSR
   threshold at n_trials = 17-18 will be tighter, but if COT delivers
   genuine ρ < 0.10, the diversification uplift is ~0.995 of orthogonal
   maximum — the first IC-7 composition with a real chance of clearing
   p < 0.05.

3. **Iter 019 (alternative) — CME GVZ implied-vol regime gate**
   (options-derived). FRED `GVZCLS` series back to 2008. Tests whether
   implied-vol regime acts orthogonally to realized-vol regime
   (iter 011's σ_60/σ_252) — if yes, second IC-7 candidate.

4. **DEFER all 30m / 15m / 1m intraday families** until a "data infra"
   iter fetches cTrader bars. Don't burn DSR on hypotheses we can't
   actually test against current data.

## Process notes

- Pytest baseline: 1063 passed, 8 **pre-existing** failures (verified
  pre-iter-016 via `git stash` round-trip). Iter 016's 6 own tests
  (`test_composition.py`) pass cleanly. **No baseline regression.**
- Wall-time: ~2 min (composition is purely additive on pre-saved
  per-iter returns; no new simulation).
- IC-8 honored: 1 cfg only, full-sample tangency. cumulative_n_trials
  bumped 15 → 16.
- Iter 016 surfaces an important honesty correction: BASE_MEMORY's
  "highest-orthogonality" entry from iter 015 was inaccurate. Future
  iters that compute IC-7 diagnostic correlations MUST aggregate to
  consistent frequency before joining.
