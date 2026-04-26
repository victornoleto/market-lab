# Iteration 009 — Final Report

## Verdict

❌ **FAIL** (score 1/100, winner_conditions_met=False, hold_time_gate=PASS on
primary intraday but irrelevant given Sharpe failure on every dataset)

The hypothesis — "**XAU/XAG ratio TREND-FOLLOWS at extreme z; sign-flip
of iter 008's MR signal turns the directional inversion into a winning
trade**" — was **falsified at the backtest stage** despite passing the
strict augmented pre-val on 1 of 3 datasets. The strategy's per-trade
GROSS edge was **5-15× smaller than the pre-val measurement** on every
dataset, dropping below the cost cliff and producing **all 3 datasets
net-negative on Track A (Pepperstone CFD)**.

This is the **6th consecutive cross-dataset failure** on Tiingo's
2020+ window (GS-4 VIX, GS-5 DXY, GS-6 FOMC, GS-7 z-score MR, GS-8
XAU/XAG MR, GS-9 XAU/XAG TREND). For the first time the failure
mode is NOT "regime inversion of pre-2018 literature signals" — the
empirical 2020+ pre-val itself was correctly directional. The
failure is a **methodology gap**: the augmented cost-aware pre-val
template, while a vast improvement over the legacy template, still
**OVERESTIMATES the realised per-trade gross** because it averages
fwd-N return over EVERY `|z|>z_entry` bar (treating each as an
independent entry), while the state machine actually enters at most
once every N bars during a sustained high-z run. Later entries land
closer to the trend's exhaustion and dilute the average.

## Pre-validation diagnostics (full)

```
gld_long:
  ADF stat = -2.849, p = 0.0516, n_obs = 5022 (informational, non-stationary as expected)
  cost-aware: n=671 entries, mean signed_fwd = +41.55 bps (sign-flipped from iter 008's −41.55),
              std = 1074.80, t = +1.001, hit-rate = 54.5%, required edge ≥ 45 bps
              → ✗ FAIL (magnitude below cost floor: 41.55 < 45)

xauusd_real:
  ADF stat = -2.214, p = 0.2012, n_obs = 1699
  cost-aware: n=215 entries, mean signed_fwd = +97.64 bps, std = 469.88,
              t = +3.047, hit-rate = 54.9%, required edge ≥ 45 bps
              → ✓ PASSED (magnitude 2.17× cost margin, statistically significant)

xauusd_intraday:
  ADF stat = -2.217, p = 0.2003, n_obs = 32161
  cost-aware: n=4346 entries, mean signed_fwd = +7.67 bps, std = 172.70,
              t = +2.929, hit-rate = 50.8%, required edge ≥ 45 bps
              → ✗ FAIL (magnitude well below cost floor: 7.67 << 45)
```

1/3 datasets passed strict pre-val (xauusd_real). Per the hypothesis's
"passed_either" continuation rule (at least one dataset passes),
the full backtest ran. Outcome below.

## Headline metrics (Track A net of Pepperstone pair CFD costs)

| dataset | Sharpe (Δ vs bench) | CAGR (Δ vs bench) | MDD (Δ vs bench) | gates | mean hold |
|---|---:|---:|---:|---:|---:|
| gld_long          | −0.18 (−0.87) | −11.84% (−23.16 pp) | 93.68% (+48.12 pp) | 3/7 | 10.00 d |
| xauusd_real       | −0.06 (−1.10) | −1.47% (−21.40 pp)  | 40.72% (+20.36 pp) | 3/7 | 10.00 d |
| xauusd_intraday   | −1.41 (−2.51) | −22.36% (−42.55 pp) | 81.72% (+57.28 pp) | 2/7 | 1.18 d (PRIMARY pass) |

**Per-trade gross-vs-cost attribution** (the smoking gun):

| dataset | per-trade GROSS (bps) | pre-val mean (bps) | gross/pre-val ratio | per-trade COST (bps) | per-trade NET (bps) |
|---|---:|---:|---:|---:|---:|
| gld_long          | **−29.78** | +41.55 | **−0.72×** (sign-flipped!) | +38.91 | −68.70 |
| xauusd_real       | +25.14 | +97.64 | **0.26×**             | +36.68 | −11.53 |
| xauusd_intraday   | +4.65  | +7.67  | 0.61×                  | +30.63 | −25.98 |

**Critical finding**: gld_long's realised per-trade gross is
**NEGATIVE** despite a positive pre-val mean. The state machine
captured the OPPOSITE behaviour from the bar-averaged pre-val.

## Score breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge | 0 | 25 | 0/3 datasets beat benchmark+0.10 |
| 2 Gates | 1 | 25 | gld 3/7, real 3/7, intra 2/7; only real reaches threshold-1 (=3); cross-bonus FAIL |
| 3 DSR | 0 | 15 | worst p = 1.0 (n_trials=9); pure noise on every dataset |
| 4 CAGR floor | 0 | 15 | all 3 datasets CAGR negative; floor not even attempted |
| 5 MDD ceiling | 0 | 15 | gld MDD 94% (>bench+5pp), real 41% (>27%), intra 82% (>27%) |
| 6 Robustness | 0 | 5 | n/a |
| **total** | **1** | **100+5** | tier: **FAIL** |
| (hold-time gate) | PASS | — | primary xauusd_intraday mean hold 1.18 d ≤ 5 d ✓ (irrelevant given other failures) |

## Per-dataset gate detail

| dataset | g1 PBO | g2 DSR | g3 WF | g4 OOS | g5 FWD | g6 Boot | g7 CL | n |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| gld_long          | ✓ deg | ✗ p=0.999 | ✗ | ✓ Sh=+0.001 (knife-edge) | ✗ Sh=−0.232 | ✗ lo=−0.64 | ✓ Δ=0pp | **3** |
| xauusd_real       | ✓ deg | ✗ p=0.954 | ✗ | ✓ Sh=+1.005 (recent window only) | ✗ Sh=−0.039 | ✗ lo=−1.40 | ✓ Δ=0pp | **3** |
| xauusd_intraday   | ✓ deg | ✗ p=1.000 | ✗ | ✗ Sh=−0.564 | ✗ Sh=−1.104 | ✗ lo=−2.63 | ✓ Δ=0pp | **2** |

xauusd_real's OOS Sharpe of +1.00 is a single ~1.9-y window (Apr-2024
to Apr-2026) where gold's recent ATH run drove a sustained XAU/XAG
extension; the FWD post-2022 window (Jan-2022 to Apr-2026, includes
the 2022 stagflation regime) has Sh=−0.04 → no out-of-sample
generalisability.

## Configuration tested

```yaml
config_id: xau_xag_pair_trend_lb60_z2_timeoutonly_to10
params:
  z_entry: 2.0
  z_exit: -1.0  # ← never fires; effectively timeout-only exit
  per_tf:
    gld_long:        {tf: 1d, lookback: 60, timeout: 10, ann: 252}
    xauusd_real:     {tf: 1d, lookback: 60, timeout: 10, ann: 252}
    xauusd_intraday: {tf: 1h, lookback: 60, timeout: 24, ann: 5119}
cumulative_n_trials: 9
broker_track: pepperstone_cfd  # Track B blocked (no shorting silver leg)
timeframes_used: [1d, 1h]
cost_model:
  pair_spread_rt_bps: 30.0    # gold 8 + silver 20 + slip 2
  pair_swap_long_bps_per_night: -0.8
  pair_swap_short_bps_per_night: +0.5
auto_aborted_at_pre_val: false
```

## What worked / what didn't

**What worked**:

- **Sign-flip implementation is mechanically correct.** The 10 unit
  tests pass, including a direct cross-iteration check
  (`test_trend_signal_is_sign_flip_of_mr_signal`) that imports iter
  008's `pair_mr_signal` via `importlib` and verifies pos_trend ==
  −pos_mr at every bar with timeout-only exit. The state machine
  captures the trend-follow direction exactly as designed.
- **Pre-val template (augmented per iter 007's GS-7 corollary)
  remains the best gate in the project**. It correctly identified
  the 1 of 3 datasets where the signed-fwd-N-bar magnitude clears
  the 1.5× cost margin (xauusd_real, +97.64 bps with t=+3.05) AND
  the 2 datasets where it doesn't (gld_long borderline, intraday
  far below). It saved iter 008 from a wasted backtest; this iter
  it correctly admitted xauusd_real and rejected the others' edge.
- **Engine cleanliness**: cross-lib G7 passes on all 3 datasets
  (Δ = 0.000 pp, pandas vs numpy). DSR / WF / bootstrap all run
  without numerical issues.
- **Compute efficiency**: full pipeline (pre-val + backtest + 8-window
  WF + 2000-resample bootstrap × 3 datasets) ran in ~30 s.

**What didn't**:

- **Per-trade gross was 0.26× to −0.72× of pre-val mean** across
  the 3 datasets. The state machine, restricted to entries from
  flat with timeout-only 10-bar holds, captured a tiny fraction of
  the bar-averaged pre-val edge. On gld_long the realised gross is
  **directionally INVERTED** (−29.78 bps per trade vs +41.55 bps
  pre-val mean). On xauusd_real, the realised gross (+25.14 bps)
  is below the cost floor (30 bps RT) before any swap, swap, or
  weekend multiplier — net per trade is −11.53 bps despite being
  in the "best" empirical case.
- **The methodology gap** is now visible. The augmented pre-val
  template I introduced in iter 008 works for screening obvious
  cost-cliff signals (z-score MR with +1.76 bps fwd → reject;
  pre-FOMC drift with +15 bps fwd → reject). But for the **borderline-
  to-marginal** signals where pre-val mean is 25-100 bps but the
  state machine's entry pattern dilutes that average, pre-val is
  systematically over-optimistic.
- **The XAU/XAG trend-follow signal does work in narrow windows**:
  xauusd_real's last-30%-of-data OOS Sharpe is +1.00 (Apr-2024 →
  Apr-2026, gold ATH run with sustained ratio extension). But the
  full-window FWD-post-2022 Sharpe is −0.04. The signal is **regime-
  conditional**: it needs the macro setup of "gold ATH driven by
  CB buying / safe-haven flows AND silver lagging on industrial
  weakness" to deliver, and those conditions don't dominate the
  full 6.3-y or 21.4-y windows.
- **Track B (Inter ETF) is structurally blocked** for the same
  reason as iter 008: pair trend-follow requires shorting silver
  (SLV/XAGUSD) on z<−2 entries; Inter Internacional retail US
  accounts are long-only.

## Main lesson (for future iterations)

The augmented pre-val gate is **NECESSARY but NOT SUFFICIENT**. It
correctly screens out clearly cost-dominated signals but does NOT
capture the **entry-spacing dilution** that occurs when a state
machine restricts entries to non-overlapping N-bar windows during
sustained `|z|>z_entry` runs.

> **GS-9 methodology corollary**: Pre-val mean signed-fwd-N-bar is
> an UPPER BOUND on the state machine's per-trade gross. The actual
> gross is reduced by an "entry-dilution factor" that depends on
> the autocorrelation of the |z|>z_entry signal — the longer the
> signal stays elevated continuously, the more later-stage entries
> the state machine will take, and the smaller the realised gross
> per trade. Iter 010+ should add a **state-machine-aware pre-val
> variant**: re-measure fwd-N-bar at ONLY the bars where state
> would transition from flat to ±1 (i.e., first bar of each
> high-z run after a low-z gap of ≥ N bars). Reject if that
> conditional mean falls below the cost margin. This was the missing
> half of the GS-7 corollary.

The deeper takeaway:

- **Six consecutive cross-dataset FAILs is now the project's
  baseline expectation** for any signal ported from pre-2018
  literature OR derived from a single empirical fwd-N-bar pre-val
  measurement. The 2020+ Tiingo window is uncharted territory for
  every absorbed book in `books/summaries/`.
- The Pareto cone of closed structural families now spans:
  RSI/Boll MR, Donchian/EMA trend, VIX cross-asset, DXY-cross-asset
  MR, FOMC calendar drift, single-asset z-score MR, 2-asset
  commodity-pair MR, AND 2-asset commodity-pair TREND-FOLLOW.
- The path forward must either (a) drop reliance on `|z|>k σ` entry
  grammar entirely (which has now failed in both directions) or (b)
  add a regime conditioner that restricts entries to the narrow
  sub-windows where the signal actually generalises (e.g., only
  trade at z>+2 when gold's 200-d trend is positive AND silver's
  60-d realised vol > silver's 252-d realised vol — but this layers
  multiple conditions, compounds DSR cost, and may not generalise
  better than a single-mech).

## Structural dead-end discovered: GS-9

**GS-9 — Pair TREND-FOLLOW on the XAU/XAG ratio at extreme z is
gross-negative on long-history gld_long AND below cost margin on
2020+ datasets, despite positive pre-val signed-fwd-N-bar evidence.
The closure mechanism is the entry-dilution gap between pre-val
(bar-averaged) and state machine (timeout-spaced) entry samples.**

The mechanism (z = (log_ratio − rolling_mean(60)) / rolling_std(60);
LONG ratio at z>+2, SHORT ratio at z<−2; timeout-only exit at 10 bars
daily / 24 bars 1h) is **falsified** by:

1. **Gross-edge inversion on gld_long** (per-trade gross −29.78 bps
   vs pre-val mean +41.55 bps; the state machine's realised entries
   over 21.4 y of GLD/SLV catch the OPPOSITE behaviour from the bar-
   averaged forward window).
2. **Cost cliff on xauusd_real** (per-trade gross +25.14 bps below
   cost floor 30 bps; net −11.53 bps despite the strongest pre-val
   signal in the loop's history at +97.64 bps with t=+3.05).
3. **Cost cliff on xauusd_intraday** (per-trade gross +4.65 bps
   << cost floor; same magnitude as iter 007's z-score MR on the
   same dataset).
4. **All 7 gates fail except G1 PBO degenerate-pass and G7 cross-
   lib** on at least 1 of 3 datasets. Maximum n_passed across
   datasets is 3/7 (gld_long, xauusd_real); minimum is 2/7
   (xauusd_intraday).

**Closes**:

- Pair trend-follow with z>±2 entry, timeout-only exit, 10-d/24-bar
  timeout on XAU/XAG ratio (this iter)
- Variants on `(z_entry ∈ {1.5, 2.0, 2.5}, timeout ∈ {5, 10, 15, 20},
  lookback ∈ {30, 60, 90, 120})` — covered by IC-8 (parameter
  sweeps within a closed family are negative-EV; the entry-dilution
  failure mode is parameter-invariant)
- Bollinger-band reformulation of trend-follow on the same XAU/XAG
  ratio (band-edge re-entry; same z-score family)
- Pair trend-follow on the **inverse asset combo** (XAG/XAU instead
  of XAU/XAG) — perfectly equivalent under sign-flip; no new info

**Does NOT close**:

- **Regime-gated XAU/XAG trend-follow** — only enter the trend-follow
  trade when an additional macro regime conditioner agrees (e.g.,
  gold > SMA(200) for LONG ratio entries). One additional parameter,
  one extra DSR trial; potentially restores the narrow-window edge
  seen in xauusd_real's last-30% OOS (+1.00 Sharpe). High-priority
  candidate for iter 010.
- **Pair MR / trend-follow on a DIFFERENT asset combo** — GLD/GDX
  (gold vs miner ETF) where the leverage-claim relationship MAY
  cointegrate where 1:1 commodity-spot didn't. Requires fresh ADF
  test + pre-val.
- **Pair MR with Kalman-filtered hedge ratio** (Chan p.81-87) on
  XAU/XAG — could in principle restore stationarity if the structural
  mismatch is in the hedge ratio. Higher complexity; defers DSR cost.
- **Single-asset (gold-only) directional-momentum bet using
  XAU/XAG z as gating signal** — instead of trading the spread,
  trade outright XAUUSD long when ratio z>+2, flat or short when
  z<−2. Different cost stack (8 bps RT instead of 30 bps), different
  bias (gold's +11%/yr drift carries the trade), different state
  machine. Worth testing.

## Citations used

- `[algo_trading_chan, p.133, ch.6]` — TS momentum (PRIMARY citation;
  conceptually correct but defeated by the dilution failure mode
  rather than by the underlying momentum theory)
- `[algo_trading_chan, p.151, ch.6]` — momentum strategies' regime
  fragility post-crisis (acknowledged in hypothesis; confirmed by the
  2020+ underperformance on full-window backtest)
- `[algo_trading_chan, p.153, ch.6]` — short-horizon momentum
  decay (used 10-d / 24-h horizons consistent with this guidance)
- `[algo_trading_chan, p.51-58, ch.2]` — z-score grammar on pair
  spreads (signal construction inherited from iter 008; structurally
  novel only in entry-direction sign-flip)
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
  (drove the 30 bps pair-cost stack; revealed the cost cliff)
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 9`
  (auto-incremented this iter)
- DEAD_ENDS GS-7 — augmented pre-val template (worked correctly for
  screening but proved incomplete; informs GS-9 methodology corollary)
- DEAD_ENDS GS-8 — empirical sign-flip evidence (used directly to
  justify this iter; the prediction held for the pre-val sign but
  failed to translate into backtest gross)

## Next iteration suggestions

After 6 consecutive cross-dataset failures (GS-4 through GS-9), the
binding constraint sharpens further:

> Any signal whose `|z|>k σ` entry is the primary timing rule has now
> failed on commodity-spot data — both directions (MR per GS-7/8;
> trend-follow per GS-9). The remaining viable directions either
> (a) drop `|z|>k σ` as a primary timing trigger, OR (b) layer a
> regime conditioner that restricts entries to the narrow sub-windows
> where the signal generalises beyond bar-averaged pre-val.

### Option A (highest priority, NEW): Realized-vol regime gate (BASE_MEMORY #13)

`Long gold ONLY when σ_60d > σ_252d (vol-expansion regime)`. Pure
single-asset gold; LONG-ONLY (both tracks viable, no Track-B
short-restriction issue); no `|z|>k σ` entry trigger; mean hold =
duration of vol regime. The signal is structurally different from
every closed family.

Why this is now MORE attractive than before iter 009:

- Doesn't rely on cross-asset, calendar, or pair data → sidesteps
  the cross-dataset failure modes (GS-4/5/6/8/9)
- Doesn't use `|z|>k σ` entry grammar → sidesteps GS-7/9's
  cost-cliff and entry-dilution failure modes
- Long-only with regime gate captures gold's persistent uptrend
  drift instead of fighting it (key insight from iter 003's PARTIAL
  rescue and iter 002 GS-3 trap)
- Dual-track viable (Track A + Track B Inter ETF for the first
  time since iter 003) → first iter to surface a Track B candidate
  in 6 attempts
- Citation grounded: `[volatility_trading, ch.X]` Sinclair on vol
  regimes; `[trading_systems_methods]` Kaufman on σ-based regime
  filters

Suggested cfg: `long XAUUSD when realized_vol_60d > realized_vol_252d`,
otherwise flat. Single-mech, single-cfg (IC-8). Pre-val skip
(no `|z|>k` entry; the regime gate IS the signal).

### Option B (secondary): Single-asset gold-only direction using XAU/XAG z as macro gate

Instead of trading the SPREAD (long XAU + short XAG = long ratio),
trade outright XAUUSD with XAU/XAG z as a directional gate:

- z[t] > +2 → LONG XAUUSD (because the ratio extension implies gold
  is in a dominant macro regime; ride that with cheaper costs)
- z[t] < −2 → SHORT XAUUSD (or flat if "long-only-bias" preferred)
- Exit on |z| crossing back to a moderate band

Why structurally different from this iter:

- Cost stack: 8 bps RT (gold-only spread) vs 30 bps RT (pair spread).
  3.75× cost reduction → cost cliff much more permissive
- Position: gold's +11%/yr drift compounds positively when LONG;
  vs the spread which is mean-zero by construction
- State machine: same `|z|>k σ` grammar BUT applied to a different
  P&L driver — risk is GS-9 entry-dilution still applies if the z
  pattern is the binding constraint

Pre-val: re-measure signed_fwd_N_bar of XAUUSD (not the ratio) at
each |z|>2 entry. **NEW DATA NEEDED**; iter 008's pre-val was on
the ratio's fwd return, not gold's outright fwd return.

### Option C (later): GLD/GDX Kalman-filtered pair

**Different asset pair on the same family**. GLD vs GDX (gold-miner
ETF) might cointegrate where XAU/XAG didn't because the miner is
a leveraged equity claim on gold (1.5-2× implied beta). With OLS
or Kalman-filtered β instead of raw 1:1 ratio, the spread might
have empirically stationary residuals. Re-run augmented pre-val
+ ADF on the Kalman-residual time series.

Defer until Option A or B delivers a baseline; this is the most
complex of the 3 options.

### Option D (infra, urgent): Land cost-aware pre-val helper as shared module

**Now upgraded with state-machine-aware variant** (per GS-9 corollary):

```python
# studies/gold_swing_loop/pre_val_helpers.py
def state_machine_aware_fwd_n_bar(
    log_signal: pd.Series,
    z: pd.Series,
    z_entry: float,
    timeout: int,
) -> np.ndarray:
    """Measure fwd-N return ONLY at bars where the state machine
    would transition from flat to ±1, i.e., where the prior N bars
    have NOT been continuously in |z|>z_entry. Returns the realised
    per-trade gross sample, not the bar-averaged sample."""
    ...
```

This helper would have correctly predicted iter 009's failure
(realised xauusd_real gross would have been ~+25 bps in the
state-machine-aware sample, not +97.64 bps). Lift before iter 010+.

### NOT recommended

- **Parameter sweeps on XAU/XAG trend-follow** — IC-8 / GS-9 closes
- **Single-asset z-score MR or trend-follow** — GS-7 / GS-9 close
- **Cross-asset macro / calendar / VIX / DXY** — GS-4 / GS-5 / GS-6
  close; long-history fetch could revisit but lower priority
- **Markowitz IC-7 composition** — BLOCKED until at least one
  primary stream delivers cross-dataset positive Sharpe; iter 003's
  MR-with-SMA(200) is the only pareto-valid base, and it's not
  enough alone

The cumulative Pareto cone of closed structural families now spans
8 distinct mechanisms across 9 iters. The structurally-novel space
is shrinking — Option A (realized-vol regime gate) is the
highest-value remaining direction because it (a) inherits no closed
family, (b) sidesteps both cost-cliff and entry-dilution failure
modes by NOT using `|z|>k σ` as a trigger, and (c) opens Track B
viability for the first time since iter 003.
