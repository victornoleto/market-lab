# Iteration 009 — Term-spread (T10Y3M) macro overlay on iter 008 vol-managed SPY+TLT blend

## Hypothesis

Iter 008 confirmed iter 006's vol-managed SPY+TLT blend edge is **structural,
not grid-selected** — single pre-committed cfg `vt15_L21_cap20` reproduced
the +0.10-0.20 Sharpe uplift across all 3 datasets with PBO neutralized
(N=1), scoring **74/100 PROMISING** (hunt-loop high, 4/5 winner conditions
met). The **sole** failing condition was G2 DSR (worst p=0.332 at
cumulative_n_trials=4240); the deflator now requires Sharpe uplift ≳0.30
to clear p<0.05 on the current trial budget — **unreachable with
variance-scaling mechanism alone** (iter 008 final lesson).

**Iter 009 claim**: compounding iter 008's blend with a **structurally
orthogonal** macro regime signal — the 10-year-minus-3-month Treasury
spread (T10Y3M) — can push Sharpe through the DSR deflator while
preserving the N=1 PBO advantage. Iter 007 established that **correlated**
overlays (EMA/SMA/VIX/drawdown/12-1 momentum) are REDUNDANT with
variance-scaling because they track the same equity-vol information.
Term-spread is **not** in that redundancy set: it is a monetary-policy /
business-cycle indicator that *leads* realized equity volatility by
6-18 months `[Estrella & Mishkin 1998]`. The blend reacts AFTER vol rises;
the term-spread gate de-levers BEFORE vol rises. This is the textbook
definition of orthogonality.

Specifically: when smoothed T10Y3M ≤ 0 (yield curve inverted), halve the
blend's total scale. One ex-ante pre-committed overlay configuration
(single threshold = 0.0, single haircut = 0.5, single smoothing window =
21 days); no grid, no sweep, no post-hoc tuning. N=1 overlay preserves the
G1 PBO neutralization from iter 008.

This is **Option B — ORTHOGONAL SIGNAL** from iter 008's `## Paths
forward` and the explicit **PICK FIRST** recommendation in
`BASE_MEMORY.md` ## Iter 009 candidates.

## Primary citation

`[regime_change, p.5-6, ch.2]` (Chen & Tsang 2020) — Regime Change
(RC) defined as "a significant change in the collective trading
behaviour of market participants, observable through changes in
statistical properties of price movements." Two-state framework
(Normal / Abnormal) for any macro-regime indicator. Establishes the
principle that equity returns conditional on regime are meaningfully
different; the challenge is regime identification. Iter 009 uses
T10Y3M as the external macro indicator, mapped to a binary (inverted /
not-inverted) state via smoothed threshold.

## Additional citations

**Books (knowledge base)**:

- `[quant_trading_chan, p.25, p.104, p.119-126]` — regime shift
  (structural change in markets). Chan is skeptical of
  Markov-switching ("useless for actual trading purposes because of
  constant transition probabilities", p.121) but "open to data-mining
  turning points." Term-spread inversion IS a data-observable turning
  point; iter 009 treats it as such (binary gate, not HMM).
- `[risk_parity, p.10-11, ch.1]` — naïve risk parity (inverse-variance
  per leg) — inherited from iter 006/008 blend base.
- `[risk_parity, p.80-81, ch.4]` — SPY-TLT negative correlation
  (-0.23 to -0.31 measured iter 008) — cross-asset diversification
  axis of the base.
- `[systematic_trading, p.107-111, p.144 ch.9]` — volatility
  standardisation + target_vol calibration — inherited.
- `[systematic_trading, p.170-171, ch.11]` — IDM cap ≤ 2.5 — inherited
  (max_leverage = 2.0).
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag (no look-ahead) —
  inherited; **extended to term-spread**: T10Y3M_{t-1} signal (no
  look-ahead).
- `[advances_fin_ml, p.208-211]` — G1 PBO via CSCV. N=1 overlay +
  N=1 blend cfg = N=1 combined → PBO undefined (vacuous PASS), same
  treatment as iter 008.
- `[advances_fin_ml, p.222-223]` — G2 DSR deflator with cumulative
  n_trials across the entire hunt loop.
- Moreira & Muir (2017), *JoF* 72(4), 1611-1644. DOI
  [10.1111/jofi.12513](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12513)
  — portfolio-level variance-scaling form `s_t = c / σ²_{t-1}`.
  Inherited from iter 006/008.

**External (canonical term-spread literature)**:

- **Estrella & Mishkin (1998).** *Review of Economics and Statistics*
  80(1). "Predicting US Recessions: Financial Variables as Leading
  Indicators." Foundational demonstration that the 10Y-3M Treasury
  spread predicts recessions 12 months ahead. NBER working paper w5379.
  Widely cited in Federal Reserve research (NY Fed, SF Fed, Boston Fed)
  as the canonical term-spread recession predictor.
- **Estrella & Hardouvelis (1991).** *Journal of Finance* 46(2),
  555-576. "The Term Structure as a Predictor of Real Economic Activity."
  Earlier foundational paper; establishes term-spread as 4-6 quarter
  leading indicator of GDP.
- **Engstrom & Sharpe (2019).** Federal Reserve FEDS note. "The
  Near-Term Forward Yield Spread as a Leading Indicator." Modern
  refinement — argues near-term (18mo) forward spread has sharper
  predictive power than 10Y-3M, but the traditional 10Y-3M remains
  the academic/Fed standard. Iter 009 uses 10Y-3M (cleanest data
  series, matches NY Fed recession-probability model).

## Edge source

What SPY 1x buy-hold fails to capture (augmented from iter 008):

1. **[inherited iter 008]** TLT's partial hedge during equity
   drawdowns; SPY-TLT correlation ~-0.30 gives diversification return.
2. **[inherited iter 008]** Variance persistence — vol-managed
   portfolio deploys aggressively in low-vol regimes, de-levers in
   high-vol.
3. **[NEW iter 009]** Monetary-regime leading information —
   term-spread inversion precedes recessions by 12 months with high
   accuracy `[Estrella & Mishkin 1998]`. In the iter 008 real-data
   windows (17y, 16y, 24y), T10Y3M inverted in: ~2000, 2006-07, 2019
   (brief), 2022-23. Each inversion preceded either a crash (2001-2002
   dot-com, 2008 GFC) or elevated-risk regimes (2019-2020 COVID,
   2022-23 Fed hiking cycle). In these windows, realized SPY volatility
   was at or below the 17y median AT THE TIME of inversion — so the
   vol-managed blend was levering UP into these periods, not down.

The term-spread overlay adds an **exogenous monetary signal** that the
blend's endogenous realized-vol dynamics cannot see. This is the
orthogonality claim that iter 007 failed to establish with 12-1
momentum (price-action signals were still endogenous to equity-vol
regime).

## Pre-committed overlay configuration

**`ts_inv21_h50`**:

| param | value | literature anchor |
|---|---|---|
| `indicator` | T10Y3M daily | Estrella-Mishkin 1998 canonical; NY Fed recession-probability model |
| `smoothing_window` | 21 bars (≈ 1 trading month EMA) | Estrella-Mishkin use monthly data → 21d smoothing of daily T10Y3M emulates monthly without aliasing |
| `threshold` | 0.0 (percent) | Classical yield curve inversion threshold `[Estrella & Mishkin 1998]`; NY Fed recession model uses same breakpoint |
| `haircut_factor` | 0.5 (50%) | Halve exposure, do NOT cash out — keeps bond leg active for flight-to-quality. Symmetric (same for equity and bond legs in blend). 0.5 matches `[systematic_trading, p.144, ch.9]` tier-2 de-lever ("reduce exposure by half in turbulent regime"). |
| `lag` | 1 bar (σ̂_{t-1}) | `[advances_fin_ml, p.162-164]` no look-ahead — use T10Y3M value known at close of bar t-1 to size bar t. |

**Combined strategy bar-level position logic**:

```
# At each bar t:
# 1. Compute iter 008's vol-managed blend scale s_t, leg weights w_spy, w_tlt.
# 2. Compute overlay gate:
#    ts_21d = EMA21 of T10Y3M daily, lagged by 1 bar
#    gate = 1.0 if ts_21d > 0 else 0.5
# 3. Final positions:
#    pos_spy_t = s_t * w_spy * gate
#    pos_tlt_t = s_t * w_tlt * gate
# 4. Cost: transaction friction on (|Δpos_spy| + |Δpos_tlt|)
# 5. Return: pos_spy * r_spy + pos_tlt * r_tlt - cost
```

**Commitment timing**: the `ts_inv21_h50` cfg above is declared BEFORE
re-running any backtests. It is the ONLY overlay cfg simulated for iter
009. The 4 parameters have independent literature anchors (none
co-optimized). No sweep, no comparison among threshold/haircut/smoothing
variants, no post-hoc selection.

**Disclosure**: The threshold=0.0 is the *single* canonical value in
the literature (not a median of a tested grid). The haircut=0.5 matches
Carver `[systematic_trading, p.144]` tier-2 vol-reduction rule
(exposure halving is a textbook regime-aware de-lever magnitude).
Smoothing=21 is the 1-month monthly-data emulation (Estrella-Mishkin
worked on monthly series). All 4 params defensible ex-ante.

## Datasets

Identical to iter 008 (reproducibility is the point):

- **educational**: SPY+TLT 2002-07-26 → 2026-04-15 (24y). Custom
  benchmark SPY b&h on same window.
- **spy_real**: SPY+TLT 2009-06-25 → 2026-04-15 (17y post-GFC).
  Benchmark: frozen scoring.BENCHMARKS["spy_real"] (SPY 0.90).
- **ndx_real**: QQQ+TLT 2010-02-12 → 2026-04-15 (16y). Benchmark:
  frozen scoring.BENCHMARKS["ndx_real"] (QQQ 0.955).

T10Y3M source: `data/external/macro/t10y3m_daily.parquet` (FRED
series, 1982-01-04 → 2026-04-23, 11 559 bars). Covers all 3 datasets
fully.

**Expected term-spread gate fire-rate per dataset** (ex-ante estimate
from the 3 iter 008 windows):

- educational (2002-2026): inversions in ~2006-07, 2019-briefly, 2022-23
  → ~12-18% of bars below smoothed 21d threshold
- spy_real (2009-2026): inversions in 2019-briefly, 2022-23
  → ~6-10% of bars
- ndx_real (2010-2026): same inversion windows as spy_real
  → ~6-10% of bars

These fire-rates are *computed exogenously* (from the macro data
alone, no equity data), so they cannot leak into backtest selection.

## Kill criteria (pre-committed)

The hypothesis is **falsified** if ANY of the following fire:

1. **Kill #1 (regression on real data)**: Sharpe on spy_real drops
   below 0.950 (Δ ≤ -0.05 vs iter 008's 1.000) OR ndx_real drops
   below 0.970 (Δ ≤ -0.05 vs iter 008's 1.021). A material regression
   means the overlay costs more than it gains — term-spread signal
   is either (a) mistimed on this universe / window or (b) correlated
   with blend in a hidden way. Either falsifies the orthogonality claim.

2. **Kill #2 (CAGR drag)**: Any dataset CAGR drops below 0.75 ×
   benchmark (edu < 0.75 × 11.1% = 8.3%; spy < 11.2%; ndx < 14.4%).
   Binary haircut=0.5 gates on 6-18% of bars remove exposure during
   specific periods; if CAGR drops materially, the gate is removing
   good bars along with bad.

3. **Kill #3 (score regression)**: iter 009 total_score < 65 (below
   iter 008's 74). The overlay must either ADD value (score climb to
   75+ STRONG) or leave iter 008's score approximately intact
   (65-74 PROMISING, meaning DSR moved favourably even if Sharpe
   didn't). Below 65 means the overlay is actively harmful.

4. **Kill #4 (gate cross-dataset regression)**: G3 Walk-Forward
   profitable_windows drops below 5 on ANY dataset (vs iter 008's
   6/7/8 on edu/spy/ndx). WF window failure indicates the overlay
   destabilises window-level returns even if whole-sample Sharpe is
   preserved.

**Winner path**: If Kill #1-4 all hold AND score climbs to ≥ 75
(STRONG tier) AND DSR worst p drops below 0.10, iter 009 is a major
hunt-loop breakthrough — confirms orthogonal-signal compounding
works and points toward further macro signals (EBP, IHS, etc.).

**Intermediate-positive path**: Score stays in 65-74 PROMISING band
but DSR p drops (even slightly, to 0.15-0.25 range) — partial
validation of orthogonality; informs iter 010 (which macro signal
compounds best).

**Failure path**: Score regresses to ≤ 64 OR Kill #1 / #4 fires —
add to DEAD_ENDS.md with structural principle: "T10Y3M binary haircut
overlay on vol-managed blend does not improve risk-adjusted edge."

## Expected budget

- **Configs to test**: 1 overlay cfg × 1 base cfg × 3 datasets
  = 3 new trials.
- **Cumulative n_trials after iter 009**: 4240 + 3 = **4243**.
- **Wall-time**: ≈ 3-5 min backtest (reuses iter 008 data cache +
  loads T10Y3M once) + ≈ 3-5 min gate battery (G1 vacuous,
  G6 bootstrap 5000 resamples dominant cost).
- **Files to create**:
  - `run_backtests.py` — loads T10Y3M, applies overlay on top of
    iter 008's `apply_blend_variance_target`, runs 3 datasets
  - `numpy_reference.py` — pure-numpy reference mirroring the
    overlay + blend for G7 cross-lib parity check
  - `compute_gates_and_score.py` — 7-gate battery + scoring
  - `results.json`, `verdict.json`, `final_report.md`

**No new simulator in `src/`.** Pure reuse of iter 008's
`stock_bond_blend.py`; overlay logic is local to iter 009. No new
pytest specs required — baseline must stay green (currently 1161
tests per iter 008 final report).

## Implementation plan

1. **T10Y3M data load**: read
   `data/external/macro/t10y3m_daily.parquet`; filter index to the
   min(equity_start, 2002-07-26). Forward-fill any missing bars
   (weekends already skipped — FRED data is business-day).
2. **Align T10Y3M to equity bars**: reindex T10Y3M onto SPY (or QQQ)
   trading calendar via `reindex(method="ffill")`. Lag by 1 bar
   (`shift(1)`) for no-look-ahead.
3. **Smoothing**: EMA21 of T10Y3M (21-day trading-day half-life
   ≈ 1 month). Use pandas `.ewm(span=21, adjust=False).mean()`.
4. **Gate**: `gate_t = 1.0 if ts_ema21_{t-1} > 0 else 0.5`.
5. **Backtest**: call iter 008's `apply_blend_variance_target()` to
   get `(net_blend, pos_spy, pos_tlt, scale)`, then apply gate:
   `pos_spy_gated = pos_spy * gate`, `pos_tlt_gated = pos_tlt * gate`.
   Recompute gross = `pos_spy_gated * r_spy + pos_tlt_gated * r_tlt`.
   Recompute costs on the gated positions (overlay changes position
   deltas → more turnover some bars, less others).
6. **Metrics**: same as iter 008 (Sharpe, CAGR, MDD, turnover,
   gate_fire_rate as new diagnostic).
7. **Gate battery**:
   - G1 PBO: N=1 → vacuous PASS (same as iter 008).
   - G2 DSR: cumulative_n_trials = 4243.
   - G3-G7: identical harness to iter 008.
8. **Robustness bonus**: same 3-sub-window split as iter 008.
9. **Score**: `score_strategy()` with benchmarks (edu custom same as
   iter 008's window, spy/ndx frozen).
10. **Write outputs + update memory + dead-ends** per loop protocol.

## Orthogonality pre-check (diagnostic, not a gate)

Before scoring, compute and print:

- Correlation between `gate_series` (0/1 binary) and iter 008's
  `scale_series` (smooth realized-vol scale). If |ρ| < 0.3, the gate
  is orthogonal to realized-vol regime — confirms the
  non-redundancy hypothesis. If |ρ| > 0.5, the gate is partially
  redundant (would suggest overlay adds little).
- Fraction of gate-firing bars (expected 6-18% per dataset).
- Overlap with iter 008's bottom-20% scale bars (where blend has
  already de-levered naturally). High overlap (> 70%) = redundant;
  low overlap (< 30%) = truly additive.

These diagnostics go into `results.json` but do NOT affect the
pre-committed gate outcomes.
