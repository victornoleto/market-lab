# Iteration 004 — Final Report

## Verdict

❌ **FAIL** — score **16/100**, `winner_conditions_met=False`,
`hold_time_gate=PASS` (mean **5.00 d** exactly on gld_long, by
construction).

**Kill criterion: NOT fired** — Track-A Sharpe on `gld_long` (the
long-history dataset) is **+0.23**, above the 0.10 threshold. But the
strategy fails to GENERALIZE across datasets: Track-A Sharpe is
**negative on both xauusd_real (−0.16)** and **xauusd_intraday (−0.16)**,
the two 6.3-year datasets. Edge exists ONLY on the longer mixed-regime
window.

| dataset | iter 003 Sharpe | iter 004 Sharpe | iter 004 vs iter 003 |
|---|---:|---:|---:|
| gld_long           | +0.30 | +0.23 | −0.07 |
| xauusd_real        | +0.19 | **−0.16** | **−0.35** |
| xauusd_intraday    | +0.24 | **−0.16** | **−0.40** |

iter 003 (gold-momentum MR with SMA(200) gate) was robust across all 3
datasets; iter 004 (cross-asset VIX recovery) is robust on the 21-year
window only. Cross-asset risk-off framing is **regime-fragile** on
short data.

## Headline metrics (NET of Pepperstone CFD costs, Track A)

| dataset | Sharpe (Δ vs bench) | CAGR (Δ) | MDD (Δ) | gates | mean hold |
|---|---|---|---|:---:|---|
| gld_long          | +0.23 (Δ −0.45) |  +1.17 % (Δ −10.15 pp) | 13.65 % (vs 45.56 %, **−31.9 pp**) | 4/7 | 5.00 d |
| xauusd_real       | −0.16 (Δ −1.20) |  −1.03 % (Δ −20.96 pp) | 14.09 % (vs 20.36 %, −6.3 pp) | 2/7 | 5.00 d |
| xauusd_intraday   | −0.16 (Δ −1.26) |  −1.04 % (Δ −21.23 pp) | 14.09 % (vs 24.42 %, **−10.3 pp**) | 2/7 | 5.00 d |

**Trade counts**: gld_long 90 trades over 21.4 y (4.2/yr), xauusd
26 trades over 6.3 y (4.1/yr) — both below the GS-2 cliff of 15 tr/yr,
so Track-B is technically eligible but produces severely negative
post-FX/post-DARF returns (Sharpe −0.46 / −0.83 / −0.83).

**MDD remains a bright spot**: ≤ 14 % across all 3 datasets vs
benchmarks of 20-46 %. Rare time-in-market (~7-9 %) limits drawdown
exposure structurally.

## Per-dataset gate detail

| dataset | G1 PBO | G2 DSR (p) | G3 WF | G4 OOS (Sh) | G5 FWD (Sh) | G6 Boot (CI lo) | G7 ×lib | n_passed |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| gld_long          | ✓ | ✗ (0.491) | ✗ | ✓ (+0.236) | ✓ (+0.254) | ✗ (−0.370) | ✓ | **4/7** |
| xauusd_real       | ✓ | ✗ (0.934) | ✗ | ✗ (−0.606) | ✗ (−0.199) | ✗ (−1.333) | ✓ | **2/7** |
| xauusd_intraday   | ✓ | ✗ (0.934) | ✗ | ✗ (−0.607) | ✗ (−0.199) | ✗ (−1.333) | ✓ | **2/7** |

Pattern shifts vs iter 003: on `gld_long` the gates pass where iter
003 also passed (G1, G4, G5, G7) — same family of gates,
direction-positive but magnitude-weak. On the **6.3-year datasets,
G4 and G5 collapse hard** (OOS Sharpe −0.61, FWD Sharpe −0.20)
because the post-2024 forward window only contains ~2 stress events
and the strategy is whipsawed by them.

## Score breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge | 0 | 25 | 0/3 datasets beat bench + 0.10 |
| 2 Gates | 1 | 25 | gld 4/7 (threshold-1=4, +1pt); xauusd 2/7 (below threshold 4, 0pt); cross-bonus NOT met |
| 3 DSR | 0 | 15 | worst-p 0.934 (n_trials=4); ceiling far above 0.20 |
| 4 CAGR floor | 0 | 15 | all 3 ds way below 0.8 × bench (need ≥9.0 % / ≥15.9 % / ≥16.2 %) |
| 5 MDD ceiling | **15** | 15 | all 3 ds well below bench + 5 pp; second iter to max this criterion |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **16** | **100+5** | tier: **FAIL** |
| (hold-time gate) | **pass** | — | mean 5.00 d on gld_long — exact threshold by construction |

## Configuration tested

`vix_recovery_5d_hold` — single config (per IC-8):

- `z_peak_threshold = 2.0`, `z_exit_threshold = 1.0`
- `peak_window = 30`, `hold_days = 5`, `cooldown_days = 10`
- `zscore_lookback = 60`
- Long-only, binary {0, 1}, no leverage
- Track A: spread 8 bps RT + swap −1 bps/night × 5d/trade
- Track B: 100 bps FX RT + DARF 15 % monthly
- Multi-day swing (`intraday_close=False`)

Trade frequency: 4.1-4.2/yr across all 3 datasets, well below GS-2
cliff (15 tr/yr) — meaning the strategy is technically Track-B
eligible but Track B's post-tax returns are catastrophic
because the pre-tax returns are too small to survive 100 bps FX RT
+ 15 % DARF asymmetry.

## What worked / what didn't

**What worked.** The pre-validation IC-6 screen correctly flagged the
right framing (post-recovery cross of +1 sigma, not the simple +25
level or naive z>+2 spike). On `gld_long` the strategy delivered
**positive Track-A Sharpe (+0.23)** with **MDD only 13.7 % (vs 45.6 %
buy-hold)** — a real risk-adjusted edge on the longest dataset. G4
OOS and G5 FWD both pass (+0.24 and +0.25 Sharpe respectively),
confirming the signal is not pure in-sample artifact on the 21-y
window. Hold time is 5.00 d exact (HARD GATE PASS by design). Cost
model behaved as expected: ~50 bps/yr drag on Track A.

**What didn't.** Two structural issues:

1. **Cross-dataset replication failed catastrophically.** On the 6.3-y
   xauusd datasets, Track-A Sharpe is **negative (−0.16)**. The 2020-2026
   window contains the Mar-2020 COVID episode (where gold *crashed*
   alongside equities and recovered only after VIX peaked) and the
   2022 inflation regime (where VIX was elevated but gold also fell).
   These are exactly the cases where "long gold post-VIX-recovery" is
   wrong-footed: gold's selling pressure was correlated with the same
   risk-off flows that drove the VIX spike.

2. **Insufficient stress events on short windows.** Only ~5-7 distinct
   recovery cross events fired in the 6.3 y window (vs 90 in 21 y).
   The strategy needs many low-probability events to express its
   premium; a 6-year sample doesn't give the law of large numbers
   enough room. G2 DSR p=0.93 confirms statistical noise.

**The structural read**: the post-VIX-recovery flight-to-quality
premium is **regime-conditional** on (a) the type of stress event
(equity-only stress favors gold; inflation/dollar stress can hurt
gold) and (b) the post-stress monetary policy response (rate-cut
expectations during recovery → gold rallies; hawkish recovery
suppresses gold). The 2004-2020 sample is dominated by equity-stress
events (GFC, Eurozone, 2018-Q4); the 2020-2026 sample mixes
inflation-stress (2022) + central-bank-driven (2024 ATH on rate-cut
priors) regimes where the simple "VIX spike → gold rallies on
recovery" pattern breaks down.

## Main lesson (for future iterations)

**Cross-asset risk-off (VIX-derived) signals on single-asset gold are
regime-fragile and lose statistical power on short (≤ 6-7 year)
windows.** This lesson is structurally distinct from GS-3 (which
established that single-mech selective-entry signals on
gold's drift can't beat buy-hold) — here we have a CROSS-DATASET
ROBUSTNESS failure: the signal works on the 21-y mixed-regime window
but flips negative on the 6.3-y 2020+ window, indicating the safe-haven
premium is conditional on the *type* of stress event, not just the
*presence* of stress. Path forward: pivot to **fundamentally-driven**
overlays (DXY, real yields, FOMC) that capture gold's macro drivers
directly rather than indirectly via cross-asset stress proxies.

## Structural dead-ends discovered

**GS-4 (NEW)** — Cross-asset volatility-derived (VIX) signals as
primary gold-entry triggers fail on short (≤ 7 y) windows. The
post-VIX-recovery flight-to-quality framing has regime-conditional
edge: positive Track-A Sharpe on 21-y mixed-regime data (GFC, Eurozone,
2018-Q4 dominate), negative on 2020+ where the regime mix shifted to
inflation/policy-driven gold dynamics. Closes "VIX as primary gold
signal" sub-family on Tiingo's 6.3-y XAUUSD coverage. Does NOT close
VIX as a *secondary* component of a multi-stream Markowitz composition,
where the premium can be diversified away — but that requires the
primary stream to come from a different (and presumably more robust)
family.

This is a **new gold-specific dead-end**, distinct from inherited
sister-loop closures and from prior gold-loop closures (GS-1 / GS-2 /
GS-3).

## IC-7 composition prep (for iter 005-006)

The cross-iter correlation between iter 004's net-PnL series and iter
003's MR base PnL series:

| dataset | corr(iter 003 MR, iter 004 VIX) | n common bars |
|---|---:|---:|
| gld_long          | **0.043** | 5 384 |
| xauusd_real       | 0.222 | 1 700 |
| xauusd_intraday   | 0.223 | 1 700 |

On `gld_long` the correlation is **near-zero (0.04)** — exactly what
IC-7 wants. On the short xauusd datasets it's higher (0.22) but still
below the 0.30 IC-6 cointegration threshold.

**However, IC-7 composition is BLOCKED for now** because iter 004
delivers **negative Sharpe on 2/3 datasets**. Markowitz proportional-
Sharpe weighting (per IC-3) would give iter 004 a *negative* weight on
xauusd_real and xauusd_intraday — equivalent to shorting iter 004 on
those datasets, which inverts the strategy's actual signal direction
and reproduces the same regime-fragility from the long side. To
enable composition, we need a SECOND single-mech stream that delivers
**positive Sharpe across all 3 datasets simultaneously** (matching
iter 003's robustness).

Direction #2 from BASE_MEMORY (DXY z-score macro overlay) is the next
candidate.

## Citations used

- `[leverage_for_the_long_run, p.13]` — Gayed VIX flight-to-quality
  regime gate (primary)
- `[ilmanen_expected_returns, ch.10]` — Gold as carry / safe-haven
  asset
- Erb & Harvey 2006 *FAJ* 62(2), pp.69-97 — gold post-stress drift
  premium
- Baur & Lucey 2010 *Financial Review* 45(2) — gold safe-haven
  asymmetric
- `[short_term_trading_strategies, p.105-118]` — analogous trend-filter
  methodology (entry-gate pattern reused)
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
- DEAD_ENDS GS-3 escape hatch #2 (own loop) — switch-to-different-family
  attempted; outcome documented as new GS-4
- DEAD_ENDS IC-6 (sister loop) — pre-val screen mandatory; passed
  (correlations all ≪ 0.30)
- DEAD_ENDS IC-8 (sister loop) — single pre-committed cfg, no sweep

## Next iteration suggestions

Three structurally different directions, ranked by expected
information gain × cost:

1. **DXY z-score macro overlay** (#2 from BASE_MEMORY) — long gold
   when DXY 60-d EMA falling AND z<−1, where DXY is constructed as an
   inverse-weighted basket of `usdcad`/`usdchf`/`usdjpy` (cached). This
   is fundamentally different from iter 003 (gold-momentum) AND iter
   004 (cross-asset risk-off): it captures gold's PRIMARY MACRO DRIVER
   (USD weakness → gold strength). Expected 4-8 trades/yr → Track-B
   viable. Cited in `[ilmanen_expected_returns, ch.10]` and Bauer-
   Mertens 2018 FRBSF EL. **Strong candidate to be the second
   positive-Sharpe stream needed for IC-7 unlock.**

2. **Pre-FOMC drift T-2 to T+1** (#4 from BASE_MEMORY) — long gold 2
   days before FOMC, exit 1 day after. 8 events/yr (clean event-
   driven), trivially Track-B viable. Hold time = 4 days (within
   HARD GATE). Cited in `[trading_systems_methods, p.479]` and Lucca-
   Moench 2015 *JoF* 70(1). **NEEDS FOMC date list** (small one-shot
   fetch from FRED ANNUAL or NY Fed website). Highest event clarity
   among all candidates.

3. **Real yields filter (TIPS DFII10 falling AND <60d MA)** (#3 from
   BASE_MEMORY) — gold's primary fundamental driver per literature.
   Most-cited driver in academic gold studies (Bauer-Mertens 2018,
   AQR 2017). **NEEDS FRED `DFII10` fetch** (one-shot data-infra step).
   Cleanest fundamental signal but engineering cost slightly higher
   than #1.

**Recommended order**: 1 → 2 → 3 (cheapest first; DXY uses cached
data + tests gold's main macro driver; FOMC and TIPS need
small data fetches but are higher-conviction signal sources).

**IC-7 composition iter is DEFERRED to iter 006-007** — needs at
least one additional positive-Sharpe-across-all-3-ds stream to
unblock. iter 003's MR base remains the only such stream so far.

**Avoid** (for next iter):
- Repeating iter 004's framing with parameter tweaks (z=2.5 vs 2.0,
  hold=10 vs 5, cooldown=5 vs 10) — IC-8 DSR drain; the cross-dataset
  fragility is structural to the cross-asset signal source, not to the
  parameter tuning.
- Modulation on iter 003's MR base (e.g., adding VIX gate to the MR) —
  IC-4 modulation saturation; will not bridge the buy-hold gap.
- 5-σ gold-vol breakout entries — fat-tail data sparsity issue
  (anti-pattern §1 in DEAD_ENDS.md).
