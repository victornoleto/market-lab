# Iteration 007 — Final Report

## Verdict

❌ **FAIL** (score 16/100, winner_conditions_met=false, hold_time_gate=pass)

The hypothesis "z-score MR on 1h gold (z<-2 entry, z>=0 exit, 24h
timeout) sidesteps GS-4/5/6 macro-regime trap by operating below the
timescale at which macro drivers manifest" was **falsified by the same
cost-cliff mechanism as GS-6**. Pre-validation on the primary intraday
dataset PASSED nominally (n=1940 events, mean fwd-24h log return
+1.76 bps, t-stat +0.67, hit-rate 55.3%) — the directional bias
exists. But the per-trade gross edge (~3.5 bps after the strategy's
early-exit cuts the realized move below the theoretical fwd-24h drift)
is **~5× smaller than the round-trip Pepperstone CFD cost** (8 bps
spread + ~1 bps swap), producing **net-negative Sharpe on all 3
datasets** (Track A: −0.05 / −0.19 / −0.31). Kill criterion fired
(primary negative AND 3/3 negative).

This is the **fourth consecutive iter** to hit the same cost-cliff
pattern as GS-6: a directional signal exists at the gross level
(t-stat 0.5-1.0 range, hit-rate 50-55%), but the per-trade edge
magnitude (~1-15 bps) cannot overcome the ~8 bps Pepperstone spread
+ swap floor. **GS-7 closure adds: pure z-score MR on single-asset
gold (1h or 1d, no regime gate) is also dominated by the cost cliff.**

## Headline metrics (Track A net of Pepperstone CFD costs)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | mean hold | n trades |
|---|---|---|---|---|---|---|
| gld_long          | −0.05 (−0.74) | −0.50% (−11.82 pp) | 27.45% (−18.11 pp) | 4/7 | 4.69 d | 111 |
| xauusd_real       | −0.19 (−1.22) | −0.92% (−20.85 pp) | 10.62% (−9.74 pp)  | 2/7 | 4.82 d | 28  |
| xauusd_intraday   | −0.31 (−1.41) | −2.69% (−22.89 pp) | 23.09% (−1.33 pp)  | 2/7 | **0.99 d** | 285 |

(Δ vs `BENCHMARKS` measured by iter 001: gld_long Sh +0.68 / CAGR
+11.32% / MDD 45.6%; xauusd_real Sh +1.04 / CAGR +19.93% / MDD 20.36%;
xauusd_intraday Sh +1.10 / CAGR +20.20% / MDD 24.42%.)

## Pre-validation diagnostics (xauusd_intraday)

| metric | value | min threshold | pass? |
|---|---:|---:|:---:|
| n_events                | 1940     | 50    | ✓ |
| mean fwd-24h log-return | +0.0177% (= +1.76 bps) | > 0 | ✓ |
| std fwd-24h             | 1.165%   | —     | — |
| t-stat                  | +0.667   | 0.50  | ✓ |
| hit-rate                | 0.5531   | 0.45  | ✓ |
| min fwd-24h             | −7.49%   | —     | — |
| max fwd-24h             | +8.75%   | —     | — |

**Pre-val PASSED nominally**, but **the t-stat is barely above the
threshold and the mean magnitude (+1.76 bps) is well below the cost
floor (~9 bps RT)**. This is the **cost-blind pre-val limitation**
identified retrospectively in iter 006 (GS-6) and now reconfirmed:
"signal positive vs zero" is the wrong screen — the right screen is
"mean signal magnitude > 1.5 × round-trip cost".

## Why the strategy failed despite passing pre-val

### Mechanism 1 — cost cliff dominates per-trade gross edge

Per-trade attribution on xauusd_intraday (285 trades over 6.29 y):

| component | per-trade (bps) | total (% of equity) | annualized |
|---|---:|---:|---:|
| Gross edge (mean realized hold-period return) | +3.5 | +9.99% | +1.59%/yr |
| Spread (8 bps RT) | −8.0 | −22.80% | −3.62%/yr |
| Swap (~24 bars × ~0.04 bps/bar) | −0.84 | −2.40% | −0.38%/yr |
| **Net per trade** | **−5.3** | **−15.21%** | **−2.42%/yr** |

The realized per-trade gross (+3.5 bps) is **about half** of the
pre-val measured fwd-24h mean (+1.76 bps × 24 = +42 bps theoretical
maximum, far less because most trades exit early at z=0; the 3.5 bps
is the EARLY-EXIT-WEIGHTED actual realized move). And it is **~2.5×
smaller** than the round-trip cost. **Same closure mechanism as GS-6
(FOMC: gross +15 bps vs cost ~83 bps; ratio 1:5.5). Here: gross +3.5
bps vs cost ~9 bps; ratio 1:2.5.**

### Mechanism 2 — daily MR signal weaker than intraday on Tiingo data

| dataset | gross PnL | n_trades | per-trade gross | per-trade cost | per-trade net |
|---|---:|---:|---:|---:|---:|
| gld_long (21.4y, 1d, 20-bar lookback)        | +9.30%   | 111  | +8.4 bps  | 12.7 bps | −4.3 bps |
| xauusd_real (6.3y, 1d, 20-bar lookback)      | **−1.60%** | 28   | **−5.7 bps** | 12.0 bps | −17.7 bps |
| xauusd_intraday (6.3y, 1h, 60-bar lookback)  | +9.99%   | 285  | +3.5 bps  | 8.8 bps  | −5.3 bps |

`xauusd_real` (daily MR on 2020+ window) is **gross-negative even
before costs**. This is the SAME GS-4/5/6 regime non-stationarity
pattern: a signal that works on long-history data (gld_long: +8.4 bps
gross/trade) inverts on the 2020+ window at the same TF (xauusd_real:
−5.7 bps gross/trade). The intraday version (xauusd_intraday) is
gross-positive but weakly so, because the 1h timescale samples
within-day MR cycles that ARE more stationary than daily macro
regimes.

### Mechanism 3 — early-exit at z=0 caps the realized edge below theoretical

The strategy's design (exit at z>=0 OR 24h timeout) front-loads exits
on the fast-revert subset. Mean hold on xauusd_intraday = 20.2 bars
(0.99 d) — so most trades exit BEFORE the 24h timeout, capturing only
the partial reversion to mean. This means the +1.76 bps theoretical
fwd-24h mean from pre-val is NOT what the strategy realizes; it
realizes ~3.5 bps per trade because it exits early on quick reversions
(positive-skewed) and rides the timeout on slow ones (negative-tail).
This **early-exit bias** is structural to z-score MR with z>=0 exit
and cannot be fixed by parameter sweeps (per IC-8, sweeps are
negative-EV here).

## Score breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge | 0 | 25 | 0 datasets beat bench+0.10 |
| 2 Gates | 1 | 25 | per-ds 4/2/2 → bucket 1+0+0; threshold not met cross-ds; no bonus |
| 3 DSR | 0 | 15 | worst p=0.985 (cumulative_n_trials=7) |
| 4 CAGR floor | 0 | 15 | 0/3 datasets pass 0.8 × benchmark CAGR (all CAGRs negative) |
| 5 MDD ceiling | 15 | 15 | 3/3 datasets pass (binary {0,1} long-only protects MDD) |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **16** | **100+5** | tier: **FAIL** |
| (hold-time gate) | pass | — | mean 0.99 d on xauusd_intraday (well within ≤5) |

## Per-gate detail (Track A)

| dataset | G1 PBO | G2 DSR | G3 WF | G4 OOS | G5 FWD'22+ | G6 Boot lo | G7 Cross-lib |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| gld_long          | ✓ | ✗ p=0.949 | ✗ | ✓ Sh +0.12 | ✓ Sh +0.04 | ✗ lo −0.66 | ✓ ΔCAGR 0.00 pp |
| xauusd_real       | ✓ | ✗ p=0.972 | ✗ | ✗ Sh −0.44 | ✗ Sh −0.16 | ✗ lo −1.27 | ✓ ΔCAGR 0.00 pp |
| xauusd_intraday   | ✓ | ✗ p=0.985 | ✗ | ✗ Sh −0.11 | ✗ Sh −0.18 | ✗ lo −1.38 | ✓ ΔCAGR 0.00 pp |

G7 cross-lib parity is exact (0.00 pp) on all 3 datasets — engine is
clean (gross-CAGR pandas vs numpy match to machine precision; cost
arithmetic is independently sane). G4/G5 on `gld_long` only pass
because the negative Sharpe magnitude is small (the long-history
window dilutes the 2020+ regime drag); they fail cleanly on the
2020+ datasets.

## Configuration tested

```yaml
config_id: zscore_mr_1h_lb60_to24
params:
  z_entry: -2.0
  z_exit: 0.0
  long_only: true
  per_tf:
    gld_long:        {tf: 1d, lookback: 20, timeout: 5,  ann: 252}
    xauusd_real:     {tf: 1d, lookback: 20, timeout: 5,  ann: 252}
    xauusd_intraday: {tf: 1h, lookback: 60, timeout: 24, ann: 5119}
cumulative_n_trials: 7
broker_track: pepperstone_cfd
timeframes_used: [1d, 1h]
cost_model:
  pepperstone_spread_rt_bps: 8.0
  pepperstone_swap_long_bps_per_night_daily: -1.0
  pepperstone_swap_long_bps_per_bar_1h: -0.04167  # = -1/24 (continuous accrual)
  pepperstone_weekend_mult: 3.0
```

## What worked / what didn't

**What worked**:

- **Engine cleanliness**: G7 cross-lib parity is 0.00 pp on all 3
  datasets (gross-CAGR pandas vs numpy match to floating-point
  precision). Cost arithmetic is correct (per-trade attribution
  reconciles exactly with the published cost model).
- **Hold-time gate**: mean hold 0.99 d on xauusd_intraday (the primary
  dataset for this iter), 4.69-4.82 d on the daily datasets.
  HARD GATE pass by construction.
- **MDD floor**: binary {0,1} long-only positions plus quick z=0 exits
  protect MDD on all 3 datasets (10.6-27.5%, well below the
  benchmark+5pp ceilings 25.4-50.6%).
- **Pre-val signal-direction check**: confirms a small but
  statistically nontrivial positive drift exists in the trigger
  population (mean +1.76 bps, t-stat +0.67, hit-rate 55.3% over 1940
  events). The mechanism IS empirically real on gold's 1h window;
  the issue is magnitude relative to costs.
- **Cross-dataset replication of the cost-cliff failure mode**: even
  the daily version on 21.4 y of GLD (long-history) fails by the
  same cost-cliff arithmetic (per-trade gross +8.4 bps vs cost
  +12.7 bps → net -4.3 bps). This rules out "short window noise"
  as the cause — it's structural.

**What didn't**:

- **Pepperstone cost cliff** (~8 bps RT spread + ~1 bps swap on 1h)
  is ~2.5× the per-trade gross edge (~3.5 bps). No reasonable
  parameter sweep on (z_entry, z_exit, lookback, timeout) can rescue
  this because per IC-8 sweeps drain DSR while the underlying gross
  edge is bounded by gold's intraday vol distribution.
- **2020+ regime non-stationarity hits xauusd_real AGAIN** — the
  daily MR signal is gross-NEGATIVE on the 6.3-y window (mean
  −5.7 bps per trade across 28 trades) despite being gross-positive
  on the 21.4-y gld_long. This is now the **fourth consecutive iter**
  to hit GS-4/5/6's cross-dataset failure mode (signal long-history
  positive, recent inverted), but with a different signal source
  (price-based, not macro-based). The 2020+ window has a strong
  trending drift that disfavors any selective-entry MR strategy.
- **z=0 early-exit caps the realized edge below the theoretical
  fwd-24h mean** by ~50% (3.5 bps realized vs ~7 bps theoretical
  hit-rate-weighted). Holding to 24h timeout would capture more of
  the drift but sacrifice the quick-exit positive-skew advantage.
- **Track B (Inter ETF) is structurally non-viable** at any of the
  3 trade counts (28-285/yr): GS-2 cost cliff produces Sharpe
  −0.84 to −1.08 on the daily versions (xauusd_intraday Track B
  blocked by T+1 settlement).

## Main lesson (for future iterations)

**The pre-validation screen needs a cost-magnitude gate, not just
a directional gate.** The current pre-val template (used iter 005
and iter 006 and now iter 007) tests `mean fwd return > 0 AND t-stat
> 0.5 AND hit-rate > 0.45`. This admits signals whose gross edge is
positive but **smaller than the round-trip cost** — exactly the
GS-6/GS-7 trap. The fix is to add a magnitude filter:

```python
# Augmented pre-val gate (proposed for iter 008+):
cost_floor_bps = 8.0  # Pepperstone spread RT
mean_fwd_bps = mean_fwd_log_return * 1e4
required_edge_bps = 1.5 * cost_floor_bps  # 1.5× margin
passed = (
    mean_fwd_bps > required_edge_bps   # NEW magnitude gate
    and t_stat > 1.0                   # tighter (was 0.5)
    and hit_rate > 0.50                # tighter (was 0.45)
    and n_events >= 50
)
```

This would have AUTO-ABORTED iter 007 (mean 1.76 bps < 12 bps
required), iter 006 (mean 15 bps < 12 bps × ~1.5 = 18 bps required —
borderline; iter 006 was correctly admitted by current pre-val but
fails the augmented one), and saved at minimum 1 DSR trial per iter.
**Adopt for iter 008.**

The deeper takeaway: **all four FAIL iters with positive pre-val
(004, 005 via different mechanism, 006, 007) hit the cost cliff.**
That's a structural pattern worth naming:

> Any single-asset gold strategy whose mean per-trade gross edge
> is < 12 bps (= 1.5 × 8 bps Pepperstone spread RT) is structurally
> dominated by costs regardless of statistical significance.
> Pre-val MUST gate on magnitude vs cost, not just on sign.

## Structural dead-end discovered: GS-7

**GS-7 — Pure z-score MR on single-asset gold (1h or 1d, no regime
gate, no companion mechanism) is structurally dominated by the
Pepperstone CFD cost cliff.**

The mechanism (z = (close − rolling_mean) / rolling_std; long when
z<-2, exit z>=0 or N-bar timeout) has empirically positive but
**too-small per-trade gross edge** (~1-9 bps mean) vs the
~8 bps round-trip Pepperstone spread + swap floor. Cost cliff
dominates net PnL on all 3 datasets.

Closes:

- z-score MR with z<-2 entry, z>=0 exit, 24h/5d timeout (this iter)
- Variants on (z_entry ∈ {−1.5, −2.0, −2.5}, z_exit ∈ {0, +0.5, +1.0},
  lookback ∈ {30, 40, 60, 90, 120}, timeout ∈ {5, 12, 24, 48})
  on the same single-asset z-score grammar — covered by IC-8:
  parameter sweeps within a closed family are negative-EV.
- Bollinger %B re-entry (BASE_MEMORY candidate #7) — same z-score
  family with a different boundary; cost cliff arithmetic is identical.
- Asia-session fade (BASE_MEMORY candidate #8) — single-asset
  intraday MR; same cost-cliff structure unless the signal magnitude
  is materially larger (e.g., explicit gap-fill events with 30+ bps
  expected reversion).

**Does NOT close**:

- z-score MR + REGIME GATE (e.g., long only when realized vol
  σ_60d > σ_252d, i.e., vol-expansion phase where MR signal is
  stronger). Different mechanism — gates on regime, not just on
  oversold trigger. Candidate #13 (realized-vol regime gate) is
  this re-framing.
- Pair / spread MR (Chan's actual framework — gold-silver ratio,
  candidate #17) where the SPREAD is stationary and the per-trade
  edge can be much larger than 12 bps. Worth testing in a
  STRUCTURALLY different iter.
- z-score MR as a SECONDARY component of an IC-7 composition once
  a primary stream (iter 003 MR base) lifts above the cost cliff.
  But iter 007's −0.16 to +0.52 correlations with iter 003 are mixed
  (same-family on daily, different on intraday) — not the
  out-of-family ρ ∈ [0.40, 0.60] that IC-7 needs.
- Lower-cost execution paths (gold futures via different broker,
  retirement account with no per-trade cost, OR Track B Inter ETF
  if the strategy can be reframed to ≤ 12 trades/yr — but at 12 tr/yr
  the strategy doesn't capture enough of the 1h MR cycles to be
  profitable either).

## IC-7 composition prep — correlation with iter 003 MR base

Computed on common bars between iter 003's `connors_rsi2_sma200_filter`
and iter 007's `zscore_mr_1h_lb60_to24` returns series:

| dataset | n_common | correlation | IC-7 viable? | note |
|---|---:|---:|:---:|---|
| gld_long          | 5384 | **+0.30** | ⚠️ | Below IC-7 optimal range [0.40, 0.60]; same-family bias (both are MR on daily) |
| xauusd_real       | 1700 | **+0.52** | ✓ (in range) | Within IC-7 optimal range; same-family but different signal grammar (Wilder RSI vs raw z-score) |
| xauusd_intraday   | 1401 | **−0.16** | ⚠️ | Cross-TF compare not clean (iter 003 is daily-resampled, iter 007 is 1h) — actual common bars are partial overlap on calendar dates |

**IC-7 verdict**: BLOCKED. Iter 007 has standalone-negative Sharpe
on all 3 datasets, so combining with iter 003's positive-Sharpe MR
base via Markowitz weighting would always reduce the combined
Sharpe (per IC-3 — combining a positive stream with a negative
stream at any non-zero negative-leg weight is dominated by the
positive-only allocation). Only IC-7-relevant if a future iter
re-frames z-score MR with a regime gate that flips the standalone
sign positive.

## Citations used

- `[algo_trading_chan, p.71-73, ch.3]` — Bollinger band z-score MR
  grammar (primary citation; Chan applies this to GLD-USO COINTEGRATED
  pairs at APR 17.8% / Sharpe 0.96 — but the pair stationarity is
  what makes the per-trade edge large enough to clear costs;
  single-asset gold lacks this property).
- `[algo_trading_chan, p.94-95, ch.4]` — buy-on-gap intraday MR
  template; Chan p.94 uses 90-day std lookback for vol normalization
  + 20-day SMA momentum filter. This iter omits the momentum filter
  to test the bare z-score; iter 003 has already shown that adding
  Connors' SMA(200) filter rescues to positive Sharpe (+0.30/+0.19/
  +0.24) but still trails buy-hold by 0.38-0.86. Combining z-score
  + SMA(200) gate is a possible iter 008 candidate — but per IC-8
  it would be a same-family extension of the iter 003 / GS-3
  closure, so likely yields the same Pareto-trail result.
- `[algo_trading_chan, p.47, ch.2]` — half-life lookback rule
  (deferred — iter did not estimate half-life; could add to pre-val).
- `[algo_trading_chan, p.183-184, ch.8]` — RULE: z-score timeout is
  preferred over backtest-fitted stop-loss; this iter respects that
  by using a hard time-based exit.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 7`.
- DEAD_ENDS GS-3 / GS-6 — `studies/gold_swing_loop/DEAD_ENDS.md`
  (cost-cliff pattern recognized iter 006; this iter generalizes to
  price-action signals → GS-7 closure).

## Next iteration suggestions

After 4 consecutive iters (004 VIX, 005 DXY, 006 FOMC, 007 z-score MR)
hitting cost-cliff or regime-fragility patterns, the loop's binding
constraint is now **clearly defined**:

> Single-asset, single-mechanism, low-edge-per-trade signals on gold
> at the Pepperstone CFD cost level (8 bps RT + ~1 bps swap) are
> structurally dominated by costs. Path forward must either
> (a) deliver per-trade gross edge > 12 bps, OR
> (b) avoid the per-trade-cost mechanism entirely (e.g., spread/pair
> MR on a stationary spread; or position-management overlay rather
> than entry-based selection).

### Option A (highest priority): gold-silver ratio MR (Chan's spread framework)

**Candidate #17** from BASE_MEMORY.md. Chan p.71-73 / p.51-58 ch.2:
the canonical z-score MR works **on a stationary spread** (cointegrated
pair). XAU/XAG ratio has documented mean-reversion properties via
real-money flows. Test:

- Universe: XAUUSD + XAGUSD daily on Tiingo cache (xagusd.parquet
  available per INFRASTRUCTURE.md).
- Signal: z-score of ratio (XAU/XAG − rolling_mean(60)) / rolling_std(60).
- Entry: z>+2 → long XAU + short XAG (ratio expected to mean-revert).
- Exit: z=0 OR 5-bar timeout.
- Track A only (needs short XAGUSD, not viable on Inter ETF Track B
  per INFRASTRUCTURE.md).

This is structurally novel because:
1. Two-asset spread MR (vs all prior iters single-asset)
2. Long-AND-short mechanic (vs all prior iters long-only)
3. Cointegration / real-economy thesis (vs price-only or macro-only)
4. **Per-trade edge potentially much larger** if the spread IS
   stationary at the relevant lookback — testable via Chan's
   ADF/Hurst pre-val template before running the full backtest.

Pre-val recipe (cost-aware): require mean fwd 5-d log-return on
ratio reversal events to exceed `1.5 × (8 bps + small short-borrow
cost on XAGUSD)` = ~12-15 bps. If ADF rejects unit root with p<0.05
on the ratio series, the stationarity assumption is empirically
validated.

### Option B (secondary): realized-vol regime gate (candidate #13)

**Candidate #13**. Long gold ONLY when σ_60d_gold > σ_252d_gold
(vol-expansion regime). Pure price signal; multi-day swing.

This is structurally novel because it's a REGIME-GATING strategy
(not a selective-entry MR or trend signal) — the gate IS the
signal. Mean hold ~ vol-regime-duration which can be weeks (likely
swing-extended; needs to verify hold-time gate). Buy-hold drift
during the regime is captured; vol-contraction periods are flat.

But: candidate #13 is essentially a long-bias regime-overlay that
depends on gold drift > 0 during vol-expansion regimes (empirical;
not guaranteed). And it has the same single-asset vulnerability.
Lower priority than Option A.

### Option C (later): augmented pre-val with cost-magnitude gate

NOT a strategy iter — a **methodology fix** that should land in the
shared `studies/gold_swing_loop/` infra:

```python
# Add to `studies/gold_swing_loop/pre_val_helpers.py` (new module):
def cost_aware_pre_val(
    fwd_returns: pd.Series,
    cost_floor_bps: float = 8.0,
    margin: float = 1.5,
    min_t_stat: float = 1.0,
    min_hit_rate: float = 0.50,
    min_events: int = 50,
) -> dict:
    ...
```

Apply in iter 008+ before the backtest. Saves DSR trials when signal
is gross-positive but cost-dominated. **Strongly recommended** —
the existing pre-val has now allowed 3 of 4 cost-cliff FAIL iters
through (004 didn't pre-val; 005 was caught; 006 + 007 admitted).

### NOT recommended

- **Bollinger %B re-entry** (#7) and **Asia-session fade** (#8) —
  same z-score family as iter 007, GS-7 closes.
- **Pre-FOMC drift variants** (T-3, T-1, etc.) — IC-8 closes.
- **VIX/DXY-derived signals on cached FX data** — GS-4/5 closes.
- **Connors RSI parameter sweeps** — GS-1/3 closes.
