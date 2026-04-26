# Iteration 009 — Trend-follow XAU/XAG ratio at extreme z (sign-flip of iter 008)

## Hypothesis

When the rolling z-score of `log(XAU/XAG)` exceeds ±2σ on a 60-bar
window, the spread **continues in the same direction** for the next
~10 trading days (daily) or ~24 hours (1h). Therefore: enter LONG
ratio (long XAU + short XAG, dollar-neutral) when `z > +2`; enter
SHORT ratio (short XAU + long XAG) when `z < −2`. Exit at fixed
N-bar timeout matching the empirical fwd-N-bar measurement window.

This is the **sign-flipped twin** of iter 008's mean-reversion
hypothesis. Iter 008's pre-val data demonstrated — with statistical
significance ≥ |t| = 2.9 on 2 of 3 datasets — that the
**directional inversion** of the MR signal is empirically robust:
the ratio EXTENDS at extreme z, not reverts.

## Primary citation

`[algo_trading_chan, p.133, ch.6]` — "Time series momentum: past
returns of a single instrument are positively correlated with future
returns." Applied here with the **log-ratio of the XAU/XAG pair as
the "single instrument"**: extreme historical-z = past directional
move; the hypothesis is that the next N bars continue the move.

## Additional citations

- `[algo_trading_chan, p.51-58, ch.2]` — z-score grammar on pair spreads
  (signal construction inherited from iter 008; structurally novel here
  because the entry direction is sign-flipped from MR)
- `[algo_trading_chan, p.151, ch.6]` — "Momentum strategies tend to
  perform miserably for several years after a financial crisis."
  Acknowledges the regime fragility of TS momentum; relevant given
  the 2020+ window contains COVID + 2022 stagflation + 2024-25 rate-
  cut anticipation
- `[algo_trading_chan, p.153, ch.6]` — "Duration of momentum effects
  gets progressively shorter as more traders learn about them."
  Justifies the short fwd-horizon (10 trading days / 24 hours) of the
  test window
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
  (re-uses iter 008's pair-cost combined RT 30 bps stack)
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 9`
  (this iter increments to 9; same data, same engine, sign-flipped
  entry counts as 1 fresh trial)
- DEAD_ENDS GS-8 — direct empirical evidence: signed-fwd-N-bar return
  in trend-follow direction is +41.5 / +97.6 / +7.7 bps on the 3
  datasets (sign-flip of iter 008's pre-val measurements)

## Edge source

XAUUSD buy-hold captures gold's outright drift. This strategy
captures the **gold-vs-silver relative drift**: when XAU/XAG is
already at +2σ historical (gold rich relative to silver), macro
forces driving the divergence (e.g., gold's safe-haven flows
outpacing silver's industrial-demand response, or 2022-2026's
divergent flows of CB gold buying vs silver's industrial weakness)
**continue** to push the ratio further — at least for a 10-bar
horizon. This is a relative-strength bet, structurally different
from outright gold direction.

## Datasets

- gld_long (GLD daily 21.4y): tests on full-history mixed-regime
  data; iter 008 pre-val showed +41.5 bps mean fwd-10d in
  trend-direction (n=671, t=+1.00) — borderline magnitude
  (1.39× cost floor vs 1.5× required). Will likely PASS pre-val
  augmented gate strictly only if relaxed to 1.0× floor; with strict
  1.5× threshold it FAILS pre-val on this dataset alone, but the
  directional sign is correct.
- xauusd_real (XAUUSD daily 6.3y): iter 008 pre-val showed +97.6 bps
  mean fwd-10d (n=215, t=+3.05) — **clears 1.5× cost margin (45 bps
  required) by 2.17×; statistically very significant.** Strongest
  empirical case.
- xauusd_intraday (XAUUSD 1h 6.3y): iter 008 pre-val showed +7.67 bps
  mean fwd-24h (n=4346, t=+2.93) — magnitude below 30-bps cost floor
  (per-trade gross net of cost will be NEGATIVE on this dataset).
  Statistically significant but cost-dominated; expect Sharpe < 0.

## Timeframes used

- gld_long: 1d
- xauusd_real: 1d
- xauusd_intraday: 1h

All from cached Tiingo parquet — no cTrader fetch needed.

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A only).

Track B (Inter ETF) is BLOCKED for the same reason as iter 008:
pair MR/momentum requires shorting the silver leg (SLV), which is
not available for Brazilian retail US accounts under Inter
Internacional (long-only constraint per `INFRASTRUCTURE.md` Track B).

## Hold-time profile

- Expected mean hold: **timeout-only exit at N bars** → mean hold ≈
  N trading days
  - gld_long (1d, timeout=10): ~10 trading days → **swing-extended**
  - xauusd_real (1d, timeout=10): ~10 trading days → **swing-extended**
  - xauusd_intraday (1h, timeout=24): 24h ÷ 24h-per-trading-day = 1
    trading day → **passes hold gate**
- Primary dataset for hold-gate check (per iter 008 convention) =
  xauusd_intraday → **gate PASSES on primary**.
- Daily datasets carry "swing-extended" tag in tier output, but the
  HARD GATE (winner condition 6) checks primary only and PASSES.

This matches iter 008's (failed) hold-time profile exactly; the
swing-extended tag on the 2 daily datasets does not block WINNER per
the prompt's primary-dataset rule.

## Kill criteria (pre-committed)

If any of the following holds at end of testing, the hypothesis is
falsified regardless of secondary metrics:

1. **Pre-val magnitude inversion** (sign opposite of iter 008's data,
   i.e., signed-fwd-N-bar return in trend-follow direction is NEGATIVE
   on ≥ 2 of 3 datasets) → AUTO-ABORT.
2. **Track A net Sharpe negative on primary (xauusd_intraday)** AND
   negative on at least one daily dataset → FAIL (cost cliff dominated).
3. **3/3 dataset gates fail (n_passed < 4 each)** → FAIL.

## Pre-validation screen (mandatory per IC-6 + GS-7 augmentation)

Run augmented `cost_aware_pre_val_gate` from iter 008 with sign-flip:

- `signed_fwd = +sign(z) × (log_ratio[t+timeout] − log_ratio[t])`
  (sign flipped from iter 008)
- Threshold: `mean_fwd_bps > 1.5 × 30 = 45 bps` AND `t-stat > 1.0`
  AND `hit-rate > 0.50` AND `n_events ≥ 30`
- ADF stationarity test on log-ratio: **expected REJECTED** (matches
  iter 008's finding); for trend-follow strategies, non-stationarity
  is NOT a kill criterion (it's the signal regime). Reported but not
  gated.

Expected pre-val outcome (re-measurement; should match iter 008 ×
−1 within rounding):

| dataset | expected mean signed_fwd | expected t | expected verdict (1.5× gate) |
|---|---:|---:|:---:|
| gld_long          | +41.5 bps  | +1.00 | ✗ (45 bps required, 41.5 < 45) — FAIL strict but directionally correct |
| xauusd_real       | +97.6 bps  | +3.05 | ✓ |
| xauusd_intraday   | +7.7 bps   | +2.93 | ✗ (45 bps required, 7.7 << 45) — FAIL strict |

So we expect 1/3 datasets to clear the strict 1.5× gate, with 2/3
showing directionally correct signal but below cost margin. Iter 008
auto-aborted at 0/3; this iter at 1/3 means full backtest runs
(`passed_either` semantics from iter 008 — at least one dataset
passes).

## Cost model (per track)

**Track A (Pepperstone) — pair**: combined RT spread 30 bps (gold 8 +
silver 20 + slip 2 per side, conservative, matches iter 008). Pair
swap −0.8 bps/night long, +0.5 bps/night short (drag both directions;
long-gold leg dominates). Weekend 3× swap multiplier on Friday hold.

Per-night × 10 trading days ≈ 8 bps swap drag added to 30 bps RT
spread = ~38 bps total cost per trade on daily. On 1h with 24-bar
hold, 0.8 bps/24 × 24 = 0.8 bps swap, + 30 bps spread = ~31 bps RT.

Net per-trade gross-vs-cost (using iter 008 sign-flipped data):

| dataset | gross fwd-N (bps) | total cost (bps) | per-trade net (bps) |
|---|---:|---:|---:|
| gld_long          | +41.5 | ~38 | **+3.5** (marginal) |
| xauusd_real       | +97.6 | ~38 | **+59.6** ✓ |
| xauusd_intraday   | +7.7  | ~31 | **−23.3** ✗ |

This makes xauusd_real the only dataset structurally able to deliver
positive Sharpe; primary intraday will be cost-dominated; gld_long
borderline. Expected outcome: NEAR_FAIL or MARGINAL on overall score
(strong on 1 dataset only, hits cross-dataset gate).

## Expected budget

- Configs to test: **1** (single pre-committed cfg per IC-8)
- Wall-time: ~5 min (pre-val ~6s + full backtest ~2 min + scoring + report)
- Files to create: hypothesis.md, run_backtest.py (sign-flipped iter 008
  engine), pre_val.json, results.json, verdict.json, final_report.md

## Implementation plan

1. **Re-use iter 008's engine** — copy `run_backtest.py` from iter 008,
   modify the state machine entry sign (`+1`/`−1` swapped) and the
   pre-val signed-fwd sign (`+sign(z)` instead of `-sign(z)`).
2. **Set timeout-only exit** — set `Z_EXIT = -1.0` so `|z| ≤ z_exit`
   never fires (always false), making the state machine exit on
   `bars_held > timeout` exclusively. This matches the pre-val
   measurement window exactly.
3. **Same costs, same params** — z_entry=2.0, lookback=60, timeout=10
   (1d) / timeout=24 (1h). Same pair cost stack as iter 008.
4. **Run pre-val first** — confirm sign-flipped magnitudes match
   expectation. If pre-val auto-aborts (`passed_either == False`),
   close and document.
5. **Run full backtest** — Track A net of pair Pepperstone costs; G1
   PBO degenerate-pass (single-cfg IC-8); G2 DSR with n_trials=9; G3
   walk-forward 8-window; G4 OOS 70/30; G5 FWD post-2022; G6 bootstrap;
   G7 cross-lib pandas vs numpy.
6. **Score** with `scoring.py` + check hold gate on
   xauusd_intraday primary.
7. **Write final_report.md** — honest tier verdict, score breakdown,
   lessons, GS-9 closure if structural failure on what was empirically
   the strongest pre-val candidate to date.
