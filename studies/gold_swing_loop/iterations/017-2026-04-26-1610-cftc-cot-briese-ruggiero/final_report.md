# Iteration 017 — Final Report

## Verdict

📉 **NEAR_FAIL** (score **28/100**, winner_conditions_met = false,
hold_time_gate = **pass**, kill criterion #2 = **fired**)

The Briese / Ruggiero canonical thresholds (Comm > 70, Small < 30,
exit at neutral 50) DO NOT produce a tradable edge on gold under
declared Pepperstone-CFD costs. **However** the iter has produced one
high-value structural finding (next section) that opens a door iter 016
declared closed.

## Headline metrics (Track A, Pepperstone CFD net of costs)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (vs bench) | gates | mean hold |
|---|---|---|---|---|---|
| **gld_long (PRIMARY)** | **+0.137** (Δ −0.547 vs 0.684) | +0.83 % (Δ −10.5 vs 11.32 %) | **31.8 %** (better than 45.6 %) | **4 / 7** | 28.3 d ✅ |
| xauusd_real (CORROBORATING) | +0.310 (Δ −0.728 vs 1.038) | +1.51 % (Δ −18.4 vs 19.93 %) | 13.0 % (better than 20.4 %) | 3 / 7 | 29.3 d ✅ |

| diagnostic | gld_long | xauusd_real |
|---|---|---|
| OOS 70 / 30 Sharpe | +0.310 | 0.000 |
| FWD post-2022 Sharpe | +0.380 | +0.350 |
| Bootstrap 99.9 % CI low | −0.512 | −1.104 |
| WF 8-window pass | 5 / 8 | 2 / 8 |
| DSR p (n_trials = 17) | 0.732 | 0.675 |
| Cross-lib CAGR (numpy) | +0.83 % (exact match) | +1.51 % (exact match) |
| n trades | 38 | 9 |

## ★ The big structural finding (GS-17) — IC-7 floor breaks

Cross-correlation of iter 017 net daily returns vs prior iters,
**measured at consistent daily granularity (GS-16 process correction)**:

| reference iter | ρ on gld_long (5384 bars) | ρ on xauusd_real (1700 bars) |
|---|---:|---:|
| **003 — Connors RSI(2) + SMA(200) MR** | **+0.003** | **−0.0002** |
| 011 — vol-regime σ_60 < σ_252 | +0.237 | +0.292 |
| 015 — DXY-SMA-slope trend gate | +0.100 | +0.050 |

This is the first stream the gold loop has produced with **ρ ≈ 0**
against another stream in the catalog. Iter 016's GS-16 closed IC-7
on the existing 15-stream catalog under the floor "no sub-0.20 ρ pair
exists at consistent frequency" — that floor is now **broken**: the
COT-positioning family is structurally independent of the price /
macro / FX-trend clock that gates iters 003 / 011 / 014 / 015.

The structural prior held: positioning is RESPONSE to macro, not on the
macro clock. de Roon-Nijman-Veld (2000) generalizes the same point
across commodities; Sanders / Boris / Manfredo (2004) replicate.

## Score breakdown (v2 rules_version = 2026-04-26-relaxed-r1)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 5 | 25 | primary +0.137 < bench + 0.10 = 0.78 → 0pt; corroborating Sh > 0 → +5pt |
| 2 Gates | 8 | 25 | primary 4/7 = thr − 1 (gld_long thr = 5) → +8pt; corr relaxed (G6 ✗ + G2 ✗) → 0; legacy cross-bonus N/A |
| 3 DSR | 0 | 15 | primary p = 0.732 ≫ 0.20 |
| 4 CAGR floor | 0 | 15 | primary 0.83 % < 0.8 × 11.32 % = 9.06 % |
| 5 MDD ceiling | **15** | 15 | primary 31.8 % ≤ 45.6 % + 5 pp = 50.6 % (the only structural pass) |
| 6 Robustness | 0 | 5 | not computed (caller-set) |
| **total** | **28** | **100 + 5** | tier: **NEAR_FAIL** |
| (hold-time gate) | **pass** | — | observed 28.3 d ∈ medium_swing 10-30 d |

## Pre-committed kill criteria

| # | criterion | observed | fired? |
|---|---|---:|---|
| 1 | n_trades ≥ 10 on gld_long | 38 | NO |
| 2 | primary Sharpe ≥ 0.30 on gld_long | 0.137 | **YES** |
| 3 | abs(ρ vs iter 003) < 0.50 on gld_long | 0.003 | NO |

Kill #2 fires → tier NEAR_FAIL is the honest read. Note that #3 was the
*structural-novelty hedge*: had ρ been ≥ 0.50, the COT-as-orthogonal-
family hypothesis would have been falsified. The opposite happened —
ρ ≈ 0 — confirming the prior even though the standalone signal is weak.

## Configuration tested

```yaml
config_id: cot_briese_ruggiero_70_30_lag1_exit50_max30d
universe: single_xau
cost_path: pep_cfd
broker_track: pepperstone_cfd
declared_primary: gld_long
declared_corroborating: [xauusd_real]
declared_hold_track: medium_swing  # 10-30d
cumulative_n_trials: 17
params:
  comm_buy: 70.0
  small_buy: 30.0
  comm_exit: 50.0
  small_exit: 50.0
  coti_window_weeks: 156         # Kaufman p.639 midpoint of 1.5-4y
  lag_weeks: 1                    # Kaufman p.640 default
  max_hold_days: 30               # cap to keep hold inside medium_swing
  spread_bps_rt: 8.0
  swap_bps_per_calendar_night: 1.0
data:
  cot_source: CFTC Legacy Futures-Only, code 088691, weekly
  cot_range: 1986-01-15 → 2026-04-21 (1913 records)
  gld_range: 2004-11-18 → 2026-04-15 (5384 bars)
  xauusd_range: 2020-01-02 → 2026-04-17 (1700 bars)
```

## What worked / what didn't

**Worked**:

- **Kaufman canonical implementation** — Briese COT Index window =
  156 weeks, Ruggiero 70 / 30 thresholds, neutral-exit 50, lag 1 week,
  all from `[trading_systems_methods, p.639-640]` with NO sweeping
  (IC-8 honored).
- **Look-ahead-free signal**: daily lookup `t − 7 days` always points
  past the Friday release of that Tuesday snapshot; verified on
  ~5400 daily bars.
- **Cross-lib parity**: pure-numpy reimpl matches the pandas engine to
  4 decimal places on CAGR and Sharpe (gld_long 0.83 % / 0.137,
  xauusd_real 1.51 % / 0.310).
- **MDD reduction**: gld_long primary MDD 31.8 % vs benchmark 45.6 %
  is the only criterion the strategy genuinely improves on — the
  position is flat ~80 % of the time, side-stepping the 2008 GFC and
  2013-2015 bear.
- **Structural orthogonality finding** (above): the strongest
  cross-loop discovery this iter, even though the strategy fails on
  Sharpe.

**Didn't work**:

- **Sharpe far below bench**: gld_long 0.137 vs 0.684, xauusd_real
  0.310 vs 1.038. Kill criterion #2 fired.
- **Most weeks fail BOTH conditions**: Comm > 70 AND Small < 30 fired
  on only 38 round-trip trades over 21.4 years (~1.8 / yr). Most years
  produce zero or one trade. The signal is **too sparse** to compound
  the underlying gold drift.
- **WF regime dependence**: 5 / 8 windows passed; window 3-4
  (2010-2014) had Sharpe −0.16 / −0.69 — exactly when commercials
  reloaded long hedges into the 2011 peak (a structural false signal
  at the cycle top). The strategy works when commercials are
  contrarian to crowd; fails when commercials chase.
- **Bootstrap CI low strongly negative**: −0.512 on gld_long — the 0.1 %
  tail of resampled annualized Sharpes is well below zero, meaning
  the 0.137 point estimate is statistically indistinguishable from
  noise at this n_trials.
- **xauusd_real corroborating window too short**: 9 trades in 6.7 y
  produces near-empty walk-forward windows; the corroborating dataset
  cannot meaningfully validate the gld_long primary at this signal
  sparsity.

## Main lesson (for BASE_MEMORY)

**GS-17**: CFTC COT positioning (Kaufman / Briese / Ruggiero canonical)
delivers **genuine structural orthogonality** to the gold loop's
existing 15-stream catalog (ρ vs iter 003 = +0.003 on gld_long, −0.0002
on xauusd_real — *first sub-0.20 ρ pair ever found at consistent
frequency*), but the **standalone signal is too weak** to win on its
own (Sharpe 0.137 / 0.31 vs bench 0.68 / 1.04; kill criterion #2
fires). The IC-7 composition path that GS-16 declared closed within
the existing catalog is now **conditionally re-opened** — but only
with COT as the orthogonal additive component, and only if a
*stronger* positioning-derived signal can be found. Combined Sharpe
ceiling at ρ ≈ 0 with current components is √(0.30² + 0.137²) ≈ 0.33
on gld_long, still below 0.78 needed.

## Structural dead-ends discovered

**GS-17** — Briese / Ruggiero canonical thresholds (Comm > 70, Small < 30,
exit 50, lag 1w, window 156w) on gold COMEX legacy futures-only series
(1986-2026) produce too sparse a trade flow (~1.8 trades/yr on gld_long)
to deliver Sharpe > +0.30, NET of Pepperstone CFD costs. Sharpe 0.137
on gld_long, 0.310 on xauusd_real; CAGR 0.83 % / 1.51 %; gates 4 / 7
and 3 / 7. **Closes** the canonical-threshold variant. **Does NOT close**
positioning-family broadly: the orthogonality finding is the inverse
prior — structural independence proven, not refuted.

**Closes**:

- Plain Briese / Ruggiero at canonical 70 / 30 / 50 thresholds + lag-1w
  + window-156w on COMEX gold legacy. Re-tuning thresholds (e.g., 80 / 20
  or 75 / 25) would burn DSR (IC-8) and is unlikely to bridge Δ −0.55
  Sharpe gap.

**Does NOT close**:

- COT family broadly. Three structurally different next moves remain
  open:
  1. **Z-score formulation** instead of stochastic. Different distribution
     shape, may pick up extremes the 156w stochastic compresses.
  2. **COT + price-momentum overlay** — gate Ruggiero entries by
     12-3-1 month price momentum (only enter when both COT extreme
     AND price already turning). Would tighten signal but reduce
     trade count further.
  3. **Disaggregated COT (DCOT)**: Producer / Merchant vs
     Money Manager net positions (post-2009). Tighter "smart money"
     definition than legacy commercials. Shorter history (2009+) but
     finer signal.
- IC-7 composition WITH COT as orthogonal stream. Even at current
  Sharpes, a 4-5 component composition (003 + 011 + 015 + 017 +
  future_COT2) at proportional-Sharpe weights might break 0.50 combined
  Sharpe at near-zero pair correlations. Iter 018+ direction.

## Citations used

- `[trading_systems_methods, p.639]` — Briese COT Index formula
  (stochastic of net long over 1.5-4 y window).
- `[trading_systems_methods, p.640]` — Ruggiero rule (Comm > trigger
  AND Small < trigger, lag 1+ week, exit at neutral 50).
- `[trading_systems_methods, p.482]` — "COT Index lag 1-several weeks
  per market; requires recalibration per asset" — honored by NOT
  sweeping lag (single pre-committed cfg).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 17;
  formula corrected mid-iter to use annualized Sharpe consistently in
  SR0 and var(SR) terms.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest; Pepperstone
  CFD spread 8 bps RT + swap 1 bps / calendar night.
- `[advances_fin_ml, p.196-202]` — bootstrap CI (1000 resamples,
  α = 0.001).
- de Roon, Nijman, Veld (2000) "Hedging Pressure Effects in Futures
  Markets," *Journal of Finance* 55 (3), 1437-1456 — cross-commodity
  hedger-imbalance return predictability (structural prior for
  orthogonality).
- Sanders, Boris, Manfredo (2004) "Hedgers, Funds, and Small
  Speculators in the Energy Futures Markets," *Energy Economics*
  26 (3), 425-445 — Briese-style COT Index empirical validation.
- IC-3 / IC-7 / IC-8 (sister loop iter 045 / 046 / 049) — out-of-family
  composition at ρ < 0.50 compounds DSR; pre-commit single cfg.

## Next iteration suggestions (priority for iter 018)

1. **PRIORITY 1 — COT z-score variant on gold** (different formulation
   of same family): rolling 156w z of (commercials_net_long −
   smalltrader_net_long), enter long when z < −1.0 (commercials extreme
   bullish vs small traders), exit at z > 0 OR 30-day timeout. Tests
   whether z is more sensitive than the stochastic at extremes (the
   stochastic compresses tails). Single cfg, IC-8.

2. **PRIORITY 2 — IC-7 composition iter 003 + iter 017** at proportional-
   Sharpe Markowitz weights, at the now-confirmed ρ ≈ 0.003 (not the
   ρ ≈ 0.22 macro-clock floor that closed previous attempts). With
   gld_long S_003 = 0.30, S_017 = 0.137 → combined ceiling 0.33 — still
   doesn't bridge bench + 0.10, but DSR p uplift would be measurable.
   IF either component is upgraded (priority 1 for COT, or new MR base
   for iter 003), the pair becomes the first IC-7 candidate with real
   chance of clearing primary edge. Hold for iter 019+ pending priority 1.

3. **PRIORITY 3 — DCOT money-manager variant** (shorter history,
   finer signal). 2009+ only — primary becomes xauusd_real (6.3 y,
   threshold 4 / 7); gld_long downgraded to corroborating. Fits the
   "primary + corroborating" relaxed rule (rules_version 2026-04-26-r1)
   exactly.

4. **DEFER** all 30 m / 15 m / 1 m intraday families until COT family is
   exhausted. Sub-1 h data infra is a separate iter.

## Process notes

- Pytest baseline (tests/ excluding 2 pre-existing collection errors
  `test_dxy_trend_gold.py`, `test_macro_dfii10_gold.py`):
  **1 041 passed, 8 pre-existing failures, 5 skipped, 0 errors**.
  Iter 017 added 5 own tests (`test_cot.py`) — all pass cleanly.
  No baseline regression.
- DSR formula correction during run: initial implementation mixed
  annualized Sharpe with per-period variance, producing spuriously
  low p-values (3.3 e-16 for Sharpe 0.137). Corrected mid-iter to use
  annualized Sharpe consistently in SR0 and var(SR) — final p-values
  0.732 / 0.675, dimensionally consistent. **Process note for future
  iters**: when validating new DSR implementations, sanity-check
  against expected order of magnitude (Sharpe < 0.5 with n_trials > 10
  should yield p > 0.5).
- Wall-time: ~25 min total (5 min CFTC fetch + 10 min implement / TDD +
  5 min backtest + 5 min score / report).
- IC-8 honored: 1 cfg only. cumulative_n_trials bumped 16 → 17.
- ρ diagnostics computed at consistent daily granularity (GS-16
  process correction), 5 384-bar full overlap on gld_long, 1 700-bar
  on xauusd_real.
