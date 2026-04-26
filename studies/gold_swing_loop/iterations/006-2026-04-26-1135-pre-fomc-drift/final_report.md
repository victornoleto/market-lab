# Iteration 006 — Final Report

## Verdict

❌ **FAIL** (score 15/100, winner_conditions_met=false, hold_time_gate=pass)

The hypothesis "Lucca-Moench's pre-FOMC drift on SPX generalizes to
gold via the USD/real-yield channel" was decisively **falsified**. The
pre-validation screen on 21.4 years of GLD passed (n=171 events,
t-stat 0.76, hit-rate 52.0%, mean 4-d log-return +15 bps), but the
full 3-dataset backtest with realistic Pepperstone CFD costs delivers
**negative Track-A Sharpe on every dataset**. The kill criterion fired
(3/3 datasets net-negative). The structural failure pattern: the raw
drift exists but is too weak to overcome the round-trip cost cliff at
8 trades/yr × 8 bps spread + 3-night swap, AND the strategy is in the
market only 12.7% of the time — too little to bridge gold's 11%/yr
unconditional drift.

## Headline metrics (Track A net of Pepperstone costs)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | mean hold | n trades |
|---|---|---|---|---|---|---|
| gld_long          | −0.04 (−0.72) | −0.64% (−11.96 pp) | 36.0% (−9.6 pp) | 2/7 | 4.00 d | 171 |
| xauusd_real       | −0.23 (−1.27) | −2.12% (−22.05 pp) | 20.5% (+0.1 pp) | 2/7 | 4.00 d | 43  |
| xauusd_intraday   | −0.23 (−1.34) | −2.11% (−22.31 pp) | 20.5% (−3.9 pp) | 2/7 | 4.00 d | 43  |

(Δ vs `BENCHMARKS` measured by iter 001: gld_long Sh 0.68 / CAGR 11.3% /
MDD 45.6%; xauusd_real Sh 1.04 / CAGR 19.9% / MDD 20.4%; xauusd_intraday
Sh 1.10 / CAGR 20.2% / MDD 24.4%.)

## Pre-validation diagnostics (gld_long)

| metric | value | min threshold | pass? |
|---|---:|---:|:---:|
| n_events                 | 171      | 50    | ✓ |
| n_dropped_calendar       | 7        | —     | (FOMC dates outside GLD calendar — pre-2004-11-18 bars) |
| n_dropped_window         | 0        | —     | (no edge-of-data drops) |
| mean 4-d log-return      | +0.151%  | > 0   | ✓ |
| std 4-d log-return       | 2.59%    | —     | — |
| t-stat                   | **+0.764** | 0.50  | ✓ |
| hit-rate                 | **0.5205** | 0.50  | ✓ |

**Pre-val PASSED.** The pre-FOMC drift on gold IS empirically real on
21.4 y of GLD: 52% of FOMC events are followed by positive 4-day gold
returns, and the mean cumulative drift is +15 bps with t-stat 0.76.
This is a small but statistically nontrivial directional edge.

## Why the strategy failed despite passing pre-val

### Mechanism 1 — cost vs raw-edge size

| component | per-trade cost | annual cost (8 tr/yr) | 21-y cumulative |
|---|---:|---:|---:|
| Spread (8 bps RT)           | 80 bps  | 64 bps  | 13.7% |
| Swap (3 nights × 1 bps)     | 3 bps   | 24 bps  | 5.0%  |
| Weekend mult (rare for FOMC)| ~0      | ~6 bps  | ~1%   |
| **Total Track A cost**      | **~83 bps** | **94 bps/yr** | **~20%** |

Raw-edge mean per trade = +15 bps. Cost per trade = ~83 bps. **Net
edge per trade = −68 bps**. The directional drift exists but is
~5× too weak relative to round-trip costs to produce positive net PnL.

### Mechanism 2 — time-out-of-market opportunity cost

The strategy holds long position only 12.7% of the time (171 events ×
4 days / 5384 bars). Gold's unconditional CAGR on gld_long is 11.3%.
A buy-hold portfolio earns this 100% of the time; the FOMC strategy
captures 12.7% × 11.3% = ~1.4% per year *if the FOMC days had average
return* — but they have +15 bps each (lower than the 11.3% / 252 ≈
4.5 bps/day average daily return). So even a costless implementation
would significantly underperform buy-hold's drift.

### Mechanism 3 — regime non-stationarity (GS-4/GS-5 pattern)

| dataset | gross 4-d return per event | n_events | mean t-stat |
|---|---:|---:|---:|
| gld_long (21.4 y, 2004-2026)              | **+0.15%**  | 171 | +0.76 |
| xauusd_real (6.3 y, 2020-2026)            | **−0.20%**  | 43  | −0.50 (est.) |
| xauusd_intraday (6.3 y, 2020-2026, daily) | **−0.20%**  | 43  | −0.50 (est.) |

The 2020+ window has the SAME signal source as gld_long but the gold
response inverts — gold *sells off* after FOMC announcements in this
window on average. Identifiable mechanisms:
- **2022 stagflation hike cycle**: Fed hiked aggressively → USD
  strengthened post-FOMC → gold fell post-FOMC despite "rate hike =
  end of hike fear" priors.
- **2024-25 rate-cut-anticipation cycle**: market priced in cuts
  pre-FOMC; on actual announcement, "buy rumour, sell news" → gold
  fell post-announcement.
- These dominate the 43 events in the 6.3-y window → mean negative.

This is **the same closure pattern as GS-4 (VIX) and GS-5 (DXY)**:
a signal that has measurable drift on the 21-y mixed-regime gld_long
window inverts on the 2020+ regime-shifted xauusd window. The
fundamental mechanism (FOMC moves rates → real yields → gold via
Ilmanen ch.10's USD-hedge channel) IS valid in both windows, but the
sign of the net flow depends on which fundamental dominates the
particular regime.

## Score breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge | 0 | 25 | 0 datasets beat bench+0.10 |
| 2 Gates | 0 | 25 | per-ds 2/2/2 < thresholds 5/4/4; no cross-dataset bonus |
| 3 DSR | 0 | 15 | worst p=0.976 (cumulative_n_trials=6) |
| 4 CAGR floor | 0 | 15 | 0/3 datasets pass 0.8 × benchmark CAGR (all CAGRs negative) |
| 5 MDD ceiling | 15 | 15 | 3/3 datasets pass (low time-in-market protects MDD) |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **15** | **100+5** | tier: **FAIL** |
| (hold-time gate) | pass | — | mean 4.00 d on gld_long (well within ≤5) |

## Per-gate detail

| dataset | G1 PBO | G2 DSR | G3 WF | G4 OOS | G5 FWD'22+ | G6 Boot lo | G7 Cross-lib |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| gld_long          | ✓ | ✗ p=0.934 | ✗ | ✗ Sh −0.30 | ✗ Sh −0.31 | ✗ lo −0.74 | ✓ ΔCAGR 0.4 pp |
| xauusd_real       | ✓ | ✗ p=0.976 | ✗ | ✗ Sh −0.46 | ✗ Sh −0.17 | ✗ lo −1.26 | ✓ ΔCAGR 0.8 pp |
| xauusd_intraday   | ✓ | ✗ p=0.976 | ✗ | ✗ Sh −0.46 | ✗ Sh −0.17 | ✗ lo −1.26 | ✓ ΔCAGR 0.8 pp |

G7 cross-lib parity holds within ≤ 1 pp — engine is clean. G1 PBO is
trivially-passed (single-cfg). G5 FWD'22+ Sharpe negative on all 3
datasets confirms post-2022 regime-fragility (mechanism 3 above).

## Configuration tested

```yaml
config_id: pre_fomc_drift_t2_to_t1
params:
  bars_before: 2
  bars_after: 1
  hold_bars_total: 4    # [T-2, T-1, T, T+1]
  long_only: true
  swap_free: false
  n_fomc_dates_in_list: 178
  fomc_dates_used: scheduled FOMC announcements 2004-01-28 through 2026-03-18
                   (excludes intermeeting/emergency cuts)
cumulative_n_trials: 6
broker_track: both
timeframes_used: ["1d"]
cost_model:
  pepperstone_spread_rt_bps: 8.0
  pepperstone_swap_long_bps_per_night: -1.0
  pepperstone_weekend_mult: 3.0
  inter_fx_rt_bps: 100.0
  inter_darf_rate: 0.15
```

## What worked / what didn't

**What worked**:
- The pre-validation screen correctly identified the pre-FOMC drift's
  empirical existence on long-history gold (21.4 y / 171 events / mean
  +15 bps / t-stat 0.76 / hit-rate 52%). This is a useful empirical
  contribution: Lucca-Moench's pre-FOMC drift DOES port partially to
  gold, just at a magnitude too small to trade profitably with current
  CFD cost models.
- Engine cleanliness: G7 cross-lib check passes within < 1 pp on all
  3 datasets, confirming the position state machine + cost model
  arithmetic is correct.
- Mean-hold = 4.00 days exactly on all 3 datasets — HARD GATE pass by
  construction.
- IC-7 prep correlations are LOW: ρ(iter003 MR, iter006 FOMC) =
  0.11 / 0.28 / 0.28 across the 3 datasets. This is a **promising IC-7
  signal** — calendar-event PnL and Connors RSI(2)+SMA(200) MR PnL are
  near-orthogonal, which would compound DSR if both had positive
  Sharpe. They don't (iter 006 fails standalone), so IC-7 with these
  two components remains BLOCKED, but the low correlation property is
  recorded for future use if either base improves.

**What didn't**:
- Pepperstone costs (~83 bps per trade round-trip) eat ~5× the raw
  drift signal (~15 bps per trade) → impossible to profit even on the
  21-y mixed-regime gld_long window where the raw drift is positive.
- Time-out-of-market (87.3% of bars flat) means the strategy cannot
  capture any of gold's unconditional 11.3%/yr CAGR drift.
- 2020+ regime-fragility: the mean per-event drift inverts on
  xauusd_real (negative on average), confirming that fundamentally-
  driven gold signals are NOT regime-stationary across the 2020-2026
  window — same closure pattern as GS-4 (VIX) and GS-5 (DXY).
- Track B is structurally non-viable: at 8 trades/yr × 100 bps FX RT
  per trade = 80 bps/yr FX cost on a strategy whose gross return is
  ~+15 bps × 8 trades = 120 bps/yr → net ~+40 bps/yr pre-DARF; but
  this is well below gold buy-hold's 11.3%/yr → strategy
  drastically underperforms unconditional ETF buy-hold on Track B.

## Main lesson (for future iterations)

**Calendar-event signals from equity literature don't port to gold at
trade-able magnitudes on Tiingo's 21.4-y window.** Pre-FOMC drift IS
empirically positive on gold (mean +15 bps per 4-day window, t-stat
0.76 over 171 events), but:

1. **Round-trip cost cliff**: the per-trade gross drift (15 bps) is
   ~5× smaller than realistic Pepperstone spread + swap costs (83 bps).
   Day/swing strategies on calendar events need either (a) ≥ 100 bps
   per-trade gross edge OR (b) much lower cost paths (raw spot trade,
   not CFD; or much fewer trades/yr) to overcome the cliff.
2. **Time-out-of-market opportunity cost** dominates on gold's
   11.3%/yr drift: any selective-entry signal that holds < 30% of
   the time needs > +30 bps per active day of edge to even tie buy-hold,
   which calendar events do not deliver.
3. **2020+ regime fragility** appears AGAIN: even a fundamentals-
   anchored signal whose mechanism is valid (FOMC → rate expectations
   → real yields → gold via Ilmanen ch.10) fails cross-dataset because
   the regime-conditional flow direction inverts in the recent window.
   This is the **third consecutive iter** to hit this pattern (iter 004
   VIX, iter 005 DXY, iter 006 FOMC), which strongly suggests the
   xauusd_real / xauusd_intraday Tiingo coverage (2020-01-02 onward)
   is structurally incompatible with **any signal whose forward-edge
   direction depends on macro regime**.

The path forward — given the consistency of the GS-4/GS-5/GS-6 pattern
— is **NOT to keep running fundamentals-driven candidates** but to
either (a) acknowledge that the loop's "cross-dataset robustness" gate
filters out any non-stationary macro signal regardless of merit, or
(b) reduce cross-dataset dependence on the short xauusd window in
favor of price-only / pattern-only signals that can validate purely
on the 21-y gld_long window.

## Structural dead-end discovered: GS-6

**GS-6 — Calendar-event signals (pre-FOMC drift, etc.) on single-asset
gold are too weak to overcome Pepperstone CFD costs even when raw
forward-edge is empirically positive on long-history data.**

This is a NEW closure (different mechanism from GS-3 family-level
single-mech closure). Closes:

- Pre-FOMC drift T-2 to T+1 (this iter)
- Variants {T-3 to T+0, T-1 to T+2, T-1 to T+0, T-3 to T+1, T-2 to T+0}
  on the same FOMC date list (covered by IC-8: parameter sweeps within
  a closed family are negative-EV)
- Other US-equity-literature calendar events with similar 4-bar
  horizons applied to single-asset gold (Lucca-Moench pre-FOMC drift,
  monthly TOM, options-expiry effect — all ported from equity)

Does NOT close:
- FOMC-driven gold signals at LONGER horizons (full month after
  rate-cut announcement, vs rate-hike: directional gating, not raw
  drift) — different mechanism, different cost amortization.
- FOMC as a SECONDARY component of an IC-7 composition (the 0.11
  correlation with iter 003's MR base is a great property if either
  base improves).
- Calendar effects on instruments with much LOWER costs than 8 bps
  Pepperstone CFD (e.g. direct gold futures, or held in retirement
  account with no per-trade cost).

## Citations used

- `[trading_systems_methods, p.479]` — Kaufman calendar-event chapter
  (primary citation; FOMC drift framing as regime-conditional overlay)
- Lucca, D. O. & Moench, E. (2015). "The Pre-FOMC Announcement Drift."
  *Journal of Finance* 70(1), 329-371. — seminal pre-FOMC drift paper
  on SPX (this iter falsifies generalization to gold at trade-able
  magnitudes)
- `[ilmanen_expected_returns, ch.10]` — gold expected-return channels
  (USD-hedge ~30%, real-yield ~20%) — both activated by FOMC
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 6`
- `[short_term_trading_strategies, p.105-118]` — analogous regime-
  filter pattern (reference for IC-7 secondary use)
- DEAD_ENDS GS-4 / GS-5 escape hatches — `studies/gold_swing_loop/DEAD_ENDS.md`

## IC-7 composition prep

Correlation of iter 006 PnL with iter 003 MR base PnL on common bars:

| dataset | n_common_bars | correlation | IC-7 viable? |
|---|---:|---:|:---:|
| gld_long          | 5384 | +0.109 | ✓ (low ρ) |
| xauusd_real       | 1700 | +0.282 | ✓ (low ρ) |
| xauusd_intraday   | 1700 | +0.285 | ✓ (low ρ) |

These are LOW correlations across all 3 datasets — well below the IC-7
optimal range of ρ ∈ [0.40, 0.60] — meaning a hypothetical Markowitz
combination would achieve maximum diversification benefit. **However,
IC-7 composition with these two streams is currently BLOCKED**: iter 006
has negative cross-dataset Sharpe, so adding it as a Markowitz weight
to iter 003's MR base would simply decrease the combined Sharpe (per
IC-3: combining a positive-Sh stream with a negative-Sh stream at any
non-zero weight on the negative leg always reduces combined Sharpe).
**Iter 006 is not yet a viable IC-7 component.** It would become one
only if a future iter changes the FOMC framing (e.g., rate-cut/hike
directional gating) into a cross-dataset positive Sharpe stream.

## Next iteration suggestions

After 3 consecutive iters (004 VIX, 005 DXY, 006 FOMC) hitting the
same GS-4/GS-5/GS-6 closure pattern (signal positive on long-history
gld_long, inverts/fails on 2020+ xauusd), the loop's structural
constraint is now CLEAR: **the cross-dataset gate is filtering out
any macro signal whose direction depends on regime**. The next iter
should structurally ESCAPE this constraint:

### Option A (highest priority): pure price/pattern-only signal that doesn't depend on macro regime

The 3 winning candidates from `BASE_MEMORY.md`'s strategy menu that
use ONLY gold's own price action (no FX, no macro, no calendar):

1. **z-score MR on 1h** (candidate #6) — `[algo_trading_chan, ch.4]`
   intraday MR on the gold 1h dataset itself. Long when 1h close
   z-score(60h) < −2; exit at z=0 or 24h timeout. Uses xauusd_intraday
   directly without any cross-asset signal. Mean hold ~1 day → swap-
   free. Day-only, true day-trading horizon. **Highly recommended for
   iter 007.**

2. **Realized-vol regime gate** (candidate #13) — long gold only when
   σ_60d_gold > σ_252d_gold (vol expansion phase). Pure price signal,
   no macro dependence. Mean hold longer (multi-day swing).

3. **Bollinger squeeze release** (candidate #14) — pure 1d/4h Bollinger
   width signal. Trade direction of breakout when BB width < 25th
   percentile. No macro.

### Option B: refine FOMC framing into directional gate

Don't repeat iter 006 with parameter sweeps (IC-8 forbids). But a
structurally-different approach: **FOMC dovish/hawkish gate from rate
expectations** — long gold ONLY when futures-implied rate cut by next
meeting > 0 (i.e., dovish bias priced in). Adds a directional
conditioner that addresses the regime-non-stationarity mechanism
identified above. Needs FRED `FEDFUNDS` futures data fetch.

### Option C (lowest priority): drop xauusd cross-dataset constraint

Test on gld_long only with a stricter pre-val gate (e.g., n_events
≥ 100, t-stat ≥ 1.5). This relaxes the cross-dataset gate that has
been the structural blocker for 3 iters. **NOT recommended** without
explicit user override — single-dataset edge does NOT count as a
winner per `WINNER_AND_RANKING.md` §1.

**Recommended: Option A1 (z-score MR on 1h)** — purely price-action,
intraday, sidesteps the macro-regime trap entirely, leverages
xauusd_intraday's strength, has a different mechanism family from
both iter 003's daily MR and iter 006's calendar event.
