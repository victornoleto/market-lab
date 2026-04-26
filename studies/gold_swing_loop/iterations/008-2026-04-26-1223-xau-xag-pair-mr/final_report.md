# Iteration 008 — Final Report

## Verdict

❌ **FAIL** (score 0/100, winner_conditions_met=false, hold_time_gate=N/A — auto-aborted at pre-val)

The hypothesis — "**XAU/XAG ratio is a stationary spread; z-score MR
on it produces per-trade reversion magnitudes large enough to clear
the GS-7 cost cliff**" — was **falsified at pre-validation on all 3
datasets simultaneously**. The augmented cost-aware pre-val template
(adopted this iter per iter 007 GS-7 corollary) caught a **directional
inversion** before any full backtest ran:

| dataset | ADF p (log-ratio) | n_entries (\|z\|>2) | mean signed fwd-N-bar (bps) | t-stat | hit-rate | verdict |
|---|---:|---:|---:|---:|---:|---|
| gld_long (1d, fwd-10d)         | **0.0516** | 671  | **−41.55** | −1.00  | 45.5% | ✗ inverted |
| xauusd_real (1d, fwd-10d)      | **0.2012** | 215  | **−97.64** | **−3.05** | 45.1% | ✗ inverted (significant) |
| xauusd_intraday (1h, fwd-24h)  | **0.2003** | 4346 | **−7.67**  | **−2.93** | 49.2% | ✗ inverted (significant) |

The "signed fwd-N-bar" column is the **return on the position the
hypothesis would take**: `signed_fwd = -sign(z) × (log_ratio[t+timeout]
− log_ratio[t])`. A positive value means "ratio reverted in the expected
direction"; a **negative value means the ratio EXTENDED** (trend
continuation, opposite of MR). All 3 datasets show negative signed
fwd, with statistical significance ≥ |t|=2.9 on the 2 short-window
datasets (215 + 4346 events).

Combined with **ADF stationarity REJECTED on all 3 datasets** (p ≥
0.05; even the 20-y gld_long dataset is just barely above the 5%
threshold, p=0.0516), this is a clean structural closure: the XAU/XAG
spread is **not stationary on Tiingo's available data window** AND
behaves as a **trend-continuation regime**, not a mean-reversion regime,
at the |z|>2 entry trigger.

This is the **5th consecutive cross-dataset failure** (GS-4 VIX, GS-5
DXY, GS-6 FOMC, GS-7 z-score MR, GS-8 XAU/XAG MR) where a signal that
should work according to textbook theory **inverts on the 2020+ Tiingo
window** — but for the first time, the failure pattern is stronger
than just "weak edge vs cost": the spread itself is non-stationary,
ruling out the entire family of **single-pair MR formulations** on
this asset combo on this data.

The auto-abort fired BEFORE Stage 3 backtest, saving compute time and
DSR-trial budget compared to running the full engine. Kill criterion
#3 from `hypothesis.md` ("ADF rejected on ≥ 2 of 3 datasets AND
gross-Sharpe negative on those datasets") was effectively triggered;
the cost-aware fwd-edge gate then independently confirmed the
directional inversion on all 3.

## Pre-validation diagnostics (full)

```
gld_long:
  ADF stat = -2.849, p = 0.0516, n_obs = 5022 (failed 5% threshold)
  cost-aware: n=671 entries, mean signed_fwd = -41.55 bps, std = 1074.80,
              t = -1.00, hit-rate = 45.5%, required edge ≥ 45 bps

xauusd_real:
  ADF stat = -2.214, p = 0.2012, n_obs = 1699 (clearly non-stationary)
  cost-aware: n=215 entries, mean signed_fwd = -97.64 bps, std = 469.88,
              t = -3.05, hit-rate = 45.1%, required edge ≥ 45 bps
              (statistically significant directional INVERSION)

xauusd_intraday:
  ADF stat = -2.217, p = 0.2003, n_obs = 32161 (clearly non-stationary)
  cost-aware: n=4346 entries, mean signed_fwd = -7.67 bps, std = 172.70,
              t = -2.93, hit-rate = 49.2%, required edge ≥ 45 bps
              (statistically significant directional INVERSION)
```

## Score breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge | 0 | 25 | no backtest run (auto-aborted at pre-val) |
| 2 Gates | 0 | 25 | no backtest run |
| 3 DSR | 0 | 15 | no backtest run |
| 4 CAGR floor | 0 | 15 | no backtest run |
| 5 MDD ceiling | 0 | 15 | no backtest run |
| 6 Robustness | 0 | 5 | no backtest run |
| **total** | **0** | **100+5** | tier: **FAIL** |
| (hold-time gate) | N/A | — | no trades; hold metric undefined |

## Configuration tested

```yaml
config_id: xau_xag_pair_mr_lb60_z2_zexit05_to10
params:
  z_entry: 2.0
  z_exit: 0.5
  timeout: 10  # daily; 24 on 1h
  per_tf:
    gld_long:        {tf: 1d, lookback: 60, timeout: 10, ann: 252}
    xauusd_real:     {tf: 1d, lookback: 60, timeout: 10, ann: 252}
    xauusd_intraday: {tf: 1h, lookback: 60, timeout: 24, ann: 5119}
cumulative_n_trials: 8
broker_track: pepperstone_cfd  # Track A only — Track B blocked (no shorting silver on Inter)
timeframes_used: [1d, 1h]
cost_model:
  pair_spread_rt_bps: 30.0    # gold 8 + silver 20 + slip 2
  pair_swap_long_bps_per_night: -0.8
  pair_swap_short_bps_per_night: +0.5  # (positive = drag in this codebase)
auto_aborted_at_pre_val: true
```

## What worked / what didn't

**What worked**:

- **Augmented pre-val (Option C from iter 007) paid off immediately.**
  This was the first iter to apply the cost-aware fwd-N-bar gate; it
  caught a directional inversion that legacy pre-val (mean-fwd > 0,
  t > 0.5, hit > 0.45) might have missed at the gld_long borderline
  (mean −41 bps fails the > 0 sub-clause; legacy would have caught
  this case anyway — but the magnitude check is the principled
  formulation). On the two 2020+ datasets the inversion is stark
  enough that any pre-val template would catch it.
- **ADF stationarity test correctly diagnosed the failure mode**.
  All 3 datasets ADF p > 0.05, with the short-window 2020+ datasets
  at p ≈ 0.20 (clearly non-stationary). The borderline gld_long case
  (p = 0.0516, just above 5% with 5022 observations) confirms the
  spread has **historical multi-decade quasi-stationary behavior but
  fails to be stationary on any subset that includes the 2020+ regime
  shift**.
- **Engine cleanliness**: 17/17 unit tests pass on the pair signal +
  cost-aware pre-val primitives. The strategy is structurally novel
  (first 2-asset, long+short, dollar-neutral pair iter in this loop),
  so this scaffolding becomes reusable infra for any future pair-MR
  or spread-strategy iter.
- **Compute efficiency**: pre-val + ADF on all 3 datasets ran in
  ~6 seconds total — very cheap closure of a high-priority direction
  with strong evidence (n_events totals 5232 across the 3 datasets).

**What didn't**:

- **The XAU/XAG spread is not stationary on Tiingo's data window.**
  Chan's GLD-USO worked in 2009-2011 because (a) USO is a futures-rolled
  ETF whose tracking error introduces extra mean reversion, and (b)
  the 2009-2011 period was a relatively stable post-GFC commodity
  bull market. The 2020+ XAU/XAG window includes the COVID volatility
  spike (silver crashed 35% in March 2020 then rallied 75% by August
  2020 — gold stayed flat), the 2021 Reddit silver-squeeze pump
  (silver spiked 25% in 2 days, gold barely moved), and the 2022-2026
  period of divergent macro drivers (gold = ATH on safe-haven flows,
  silver = lagging on industrial-demand weakness). These regime shifts
  break the stationarity prerequisite for ratio MR.
- **Trend continuation, not mean reversion, at extreme z**. The
  signed-fwd-N-bar return at |z|>2 is **strongly negative** (in MR
  convention) on the 2020+ datasets — meaning when the ratio is
  extreme, it tends to **extend further**, not revert. This is the
  opposite of the textbook prediction. Iter 009 should consider this
  regime-conditional behavior carefully (see "Next iteration
  suggestions").
- **Track B blocked by long-only restriction**. Even if the strategy
  had worked on Track A, Track B (Inter ETF) would never have been
  viable: pair MR requires shorting silver (SLV/XAGUSD), which is
  blocked for Brazilian retail US accounts per `INFRASTRUCTURE.md`
  Track B section. So the strategy was Track-A-only by construction;
  this iter's failure does not affect the Track B coverage map.

## Main lesson (for future iterations)

**The augmented cost-aware pre-val + ADF stationarity check is now
proven as the discipline for any spread/pair candidate.** The template
exists in `iterations/008-*/run_backtest.py:cost_aware_pre_val_gate`
and `run_pre_val_for_dataset` and should be lifted into a shared
helper in `studies/gold_swing_loop/pre_val_helpers.py` so iter 009+
can `from pre_val_helpers import cost_aware_pre_val_gate, adf_test`.
This is the same Option C from iter 007's final_report.md, now
empirically validated on a real failure case.

The deeper takeaway:

> Five consecutive cross-dataset failures (GS-4 VIX, GS-5 DXY, GS-6
> FOMC, GS-7 z-score MR, GS-8 XAU/XAG MR) on Tiingo's 2020+ window
> share a common pattern: **textbook signal → 2020+ regime inverts
> direction or stationarity**. The 2020-2026 window contains COVID,
> stagflation, rate-cut anticipation, and gold's ATH cycle — these
> regimes have no precedent in any of the source-of-citation books
> (most absorbed pre-2018). **A robust gold-swing winner cannot rely
> on borrowing equity-literature signals or commodity-pair-MR templates
> AS-IS without empirical 2020+ pre-val.**

The augmented pre-val now bakes this discipline into the loop's
process: future iters will catch their own regime-invert failures
in 6 seconds instead of 6 hours of full backtest + DSR drain.

## Structural dead-end discovered: GS-8

**GS-8 — XAU/XAG ratio mean-reversion is non-stationary AND
directionally inverted on Tiingo's 2020+ window across all 3 datasets;
single-pair MR formulations on commodity-spot data are structurally
closed for this loop's data window.**

The mechanism (z = (log_ratio − rolling_mean(60)) / rolling_std(60);
short ratio at z>+2, long ratio at z<−2; |z|≤0.5 exit OR 10-bar
timeout) is **falsified** by both:

1. **ADF stationarity**: p = 0.20 on the 2 short-window datasets and
   p = 0.052 on the 20-y dataset — the spread fails the cointegration
   prerequisite for Chan's framework on the available data window.
2. **Directional inversion**: signed-fwd-N-bar return is statistically
   significantly NEGATIVE at |z|>2 entries on 2 of 3 datasets
   (xauusd_real t=−3.05, xauusd_intraday t=−2.93) — the ratio extends
   rather than reverts.

**Closes**:

- z-score MR with z>±2 entry, |z|≤0.5 exit, 10-d/24-bar timeout on
  XAU/XAG ratio (this iter)
- Variants on `(z_entry ∈ {1.5, 2.0, 2.5}, z_exit ∈ {0, 0.5, 1.0},
  lookback ∈ {30, 60, 90, 120}, timeout ∈ {5, 10, 15, 20})` — covered
  by IC-8 (parameter sweeps within a closed family are negative-EV
  while DSR drains).
- Bollinger-band reformulation of the same XAU/XAG ratio (band-edge
  re-entry; z-score family).
- Half-life-fitted lookback variants — half-life only matters when
  the spread is empirically stationary; ADF rejected on all 3 datasets.

**Does NOT close**:

- **TREND-FOLLOWING the XAU/XAG ratio at extreme z**. The pre-val's
  signed-fwd inversion implies the OPPOSITE direction (long ratio at
  z>+2, short ratio at z<−2) has roughly the **same magnitude with
  flipped sign**: gld_long +41.5 bps mean fwd-10d, xauusd_real +97.6
  bps mean fwd-10d, xauusd_intraday +7.7 bps mean fwd-24h. Two of
  three are above the 30-bps cost floor on raw magnitude. This is
  **iter 009 candidate #1 (PROMOTED)** — same data, different
  signal-construction grammar, structurally novel vs everything in
  GS-1..GS-8.
- **Pair MR on a stationary spread that ISN'T XAU/XAG**. E.g., gold
  vs gold-miner ETF (GLD vs RGLD or GDX), where the spread might
  actually cointegrate (one is the underlying, the other a leveraged
  equity claim). Caution: sister-loop iter 003 closed cross-sectional
  miner-basket ranking on survivorship grounds — but a pure 2-asset
  GLD/GDX spread is structurally different.
- **Pair MR with a Kalman-filtered hedge ratio** (Chan p.81-87, Engle-
  Granger 2-step). This iter used a 1:1 ratio (raw log of price ratio);
  a Kalman/OLS-fitted hedge ratio could in principle restore stationarity
  if the structural mismatch is in the hedge ratio rather than the
  underlying assets. Higher complexity; defers DSR cost compounding.
- **Multi-spread Markowitz composition** (e.g., XAU/XAG + GLD/GDX +
  GLD/copper) — same family but combining multiple non-stationary
  spreads might net out to stationarity. Out of scope until at least
  one single-spread base works.

## Citations used

- `[algo_trading_chan, p.51-58, ch.2]` — Bollinger MR on cointegrated
  pairs (PRIMARY citation; falsified by ADF rejection on all 3
  datasets — Chan's framework requires the spread to be empirically
  stationary, which fails on this asset combo on this data window).
- `[algo_trading_chan, p.71-73, ch.3]` — z-score grammar (entry/exit
  thresholds; structurally correct, but applied to a non-stationary
  series).
- `[algo_trading_chan, p.47, ch.2]` — half-life lookback rule (60-d
  default; not tested because stationarity prerequisite failed).
- `[algo_trading_chan, p.183-184, ch.8]` — time-based exit > stop-loss
  (used; would have applied if backtest had run).
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
  (drove the pair-cost combined RT 30 bps stack).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 8`
  (this iter increments to 8; auto-abort still counts as 1 trial per
  iter 005 precedent).
- DEAD_ENDS GS-7 — augmented pre-val template (this iter's auto-abort
  validates iter 007's Option C methodology recommendation).

## Next iteration suggestions

After 5 consecutive cross-dataset failures (GS-4 VIX, GS-5 DXY, GS-6
FOMC, GS-7 z-score MR, GS-8 XAU/XAG MR) the binding constraint can
now be sharpened:

> Any signal — single-asset OR pair — derived from price-action,
> cross-asset, calendar-event, or commodity-spread MR templates
> ported from pre-2018 literature **fails on Tiingo's 2020+ window**.
> The path forward must (a) deliver per-trade gross edge > 30 bps
> with t-stat > 1.0 on the 2020+ window (verifiable in pre-val), AND
> (b) have a domain-specific reason to avoid the regime-inversion
> mechanism that has now killed 5 consecutive iters.

### Option A (highest priority, NEW PROMOTION): trend-follow XAU/XAG ratio at extreme z

**This iter's pre-val inversion data is itself a leading indicator**.
The signed-fwd-N-bar return at |z|>2 is **+41.5 bps (gld_long) /
+97.6 bps (xauusd_real) / +7.7 bps (xauusd_intraday)** in the
trend-following direction. Two of three are above the 30-bps cost
floor; xauusd_real is above the 1.5× margin (45 bps required) and is
statistically significant (t=+3.05 in trend-follow direction).

Iter 009 candidate: **REVERSE-DIRECTION same signal**:
- z[t] > +2 → LONG ratio (LONG XAU + SHORT XAG, betting ratio extends)
- z[t] < −2 → SHORT ratio (SHORT XAU + LONG XAG, betting ratio extends)
- Exit when |z[t]| > 3 (parabolic exhaustion) OR fixed N-bar timeout
  OR z reverts past a threshold

Why structurally novel:
- **Different signal-construction grammar** (trend-continuation vs
  mean-reversion at extreme levels)
- **Empirical evidence available** from this iter's pre-val (no
  additional fwd-edge measurement needed; just flip sign)
- **Cost cliff potentially clearable** on xauusd_real (97.6 bps mean
  fwd-10d > 45 bps required edge)
- **Risks acknowledged**: gld_long magnitude (+41 bps) below 1.5× cost
  floor (only 1.39× — borderline); xauusd_intraday too small (+7.7 bps);
  hold-time may exceed 5d if "extend" event takes longer than 10
  bars to manifest.

Pre-val grammar: same template as iter 008 with sign-flip on `signed_fwd`.

### Option B (secondary, infra): land cost-aware pre-val helper as shared module

Per iter 007 final_report Option C — now justified. Move
`cost_aware_pre_val_gate`, `run_pre_val_for_dataset`, and
`adf_test_helper` from iter 008's `run_backtest.py` into
`studies/gold_swing_loop/pre_val_helpers.py` so iter 009+ can:

```python
from pre_val_helpers import cost_aware_pre_val_gate, run_pre_val_for_dataset
```

without re-copying. NOT a strategy iter; a 30-min refactor that pays
back at every future iter. Tests live alongside.

### Option C (secondary): realized-vol regime gate (BASE_MEMORY #13)

**Candidate #13 unchanged from iter 007 recommendation**. Long gold
ONLY when `σ_60d > σ_252d` (vol-expansion regime). Pure price signal;
buy-hold-bias regime overlay; mean hold = duration of vol regime.

Why this is now MORE attractive than before iter 008:
- Doesn't rely on cross-asset / calendar / spread data (sidesteps
  GS-4/5/6/8 cross-dataset failure modes)
- Single-asset gold (no Track-B short-restriction issue; LONG-ONLY
  by construction → both tracks viable)
- Long-bias-during-uptrend captures gold's persistent drift instead
  of fighting it (key insight from iter 003's escape — being WITH
  the trend matters)

Lower priority than Option A only because Option A has empirical
evidence in hand from this iter's pre-val.

### Option D (later): GLD/GDX or GLD/copper Kalman-filtered pair

**Different asset pair on the same family**. Gold vs gold-miner
(GLD/RGLD or GLD/GDX) might cointegrate where XAU/XAG didn't because
the miner is a leveraged equity claim on the underlying. Or gold vs
copper (intermarket complement). Requires Kalman filter or OLS hedge
ratio for proper spread construction. Higher complexity; defer until
Option A delivers a baseline.

### NOT recommended

- **Parameter sweeps on XAU/XAG MR** — IC-8 closes (variants on z, lb,
  timeout within the closed MR family are negative-EV).
- **Pre-FOMC drift / VIX / DXY variants** — GS-4/5/6 close.
- **z-score MR on single-asset gold (1d/1h)** — GS-7 closes.
- **Connors RSI parameter sweeps** — GS-1/3 close.

The cumulative Pareto cone of closed structural families now spans:
single-asset MR, single-asset trend, cross-asset macro/calendar,
single-asset z-score MR, and 2-asset commodity-pair MR. The next
structurally novel direction is **regime-conditional position sizing
without a selective-entry signal** (Option C) OR **trend-follow on
the same closed-family signal in the OPPOSITE direction** (Option A,
empirically supported by this iter's pre-val numbers).
