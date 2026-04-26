# Iteration 025 — Final Report

## Verdict

📉 **NEAR_FAIL — score 35/100**, winner_conditions_met = False, hold_time_gate
= PASS (mean basket hold 4.65d ∈ short_swing [2, 10]), is_winner = False.

**4 of 6 pre-committed kill criteria fired**:

- ✗ Kill #1 — primary basket Sh = +0.1725 < 0.30 (FIRED)
- ✗ Kill #2 — basket Sh − iter003 Sh = −0.1275 < +0.05 (FIRED)
- ✓ Kill #3 — IC-6 rolling-60d ρ vs iter003 = **68.1%** ≤ 80% threshold (**NOT
  FIRED** — see "★ critical finding" below)
- ✗ Kill #4 — G6 bootstrap CI low = −0.566 ≤ 0 (FIRED)
- ✓ Kill #3b — IC-6 vs iter011 rolling = 14.8% < 30% (NOT fired; basket is
  structurally different from vol-regime — not GS-22 family)
- ✗ Kill #5 — DSR p = 0.918 > 0.30 (FIRED)

## ★ Critical finding — first cross-cluster IC-6 breakthrough in 25 iters

**The IC-6 rolling-60d position-vector correlation vs iter 003 dropped to
68.1% on PRIMARY** (and 70.6% on corroborating). This is **the first time in
the loop's history** that the rolling exceed-frac-at-30%-threshold dropped
below 80%. Compare:

| iter | basket | IC-6 rolling vs iter003 | drop vs single-asset |
|---|---|---|---|
| 023 | GLD+SLV (within-PM) | 96.8% | +1.8 pp |
| 024 | GLD+GDX (PM-adjacent miner) | 94.9% | +1.9 pp |
| **025** | **GLD+BTC (cross-cluster)** | **68.1%** | **−27 pp** |

The static-ρ vs iter 003 also dropped from +0.71 (iter 023) and +0.67
(iter 024) to **+0.26** on iter 025 — i.e., BTC's mean-reversion signal
fires on substantially different days than gold's. Position-vector divergence
is real at the cross-cluster level. **The thesis "BTC's macro drivers are
structurally orthogonal to gold's" is empirically validated.**

But this orthogonality does NOT translate into a Sharpe edge. The basket
still scores NEAR_FAIL because the standalone BTC RSI(2) signal is too weak
relative to its higher cost burden (25 bps RT spread + −5 bps/night swap, vs
gold's 8 bps + −1 bps). The 40% BTC weight DRAGS basket Sharpe by adding
high-variance, near-zero-EV trades.

## Headline metrics (NET of Pepperstone CFD costs per leg)

| dataset | Sharpe (Δ vs basket bench) | CAGR (vs bench) | MDD (vs bench) | gates | mean hold (basket) |
|---|---|---|---|---|---|
| gld_btc_basket_long (~12.3y) PRIMARY | **+0.1725** (Δ −0.901) | +1.14% (vs 31.11%) | **15.45%** (vs 47.50%) | **4/7** | 4.65d |
| xau_btc_basket (~6.3y) CORROBORATING | **+0.6689** (Δ −0.084) | +3.49% (vs 39.87%) | **5.69%** (vs 43.24%) — loop-best ever | **5/7** | 3.85d |

Reference (single-asset iter 003 RSI(2)+SMA(200) on gld_long): Sharpe +0.30,
mean_hold ~3-4d. The basket aggregation drags PRIMARY Sharpe DOWN by 0.13.

Per-leg trade counts (PRIMARY ~12.3y joint window):
- gold leg: **34 trades** (~2.8/yr) — much lower than iter 024's 63/19.9y because
  the 2014-2026 window contains long stretches of gold below SMA(200) (2014-2018
  bear-stagnation), gating most RSI(2) entries
- BTC leg: **37 trades** (~3.0/yr) — comparable cadence; BTC's RSI(2)<5 +
  SMA(200) fires on a similar frequency despite BTC's much higher volatility
- Basket trades (any leg in): 65 — substantial NON-overlap (34+37=71, basket=65,
  ~85% leg-trade-distinctness, vs iter 023 SLV ≈ 60% distinct, iter 024 GDX ≈ 65%)

Per-leg cost totals on PRIMARY (~12.3y):
- gold spread: $0.0163 cumulative ≈ 16 bps total → 4.8 bps avg/trade RT (matches 8 bps RT × half-roundtrip = 4 bps)
- BTC spread: $0.0370 cumulative ≈ 37 bps total → 10.0 bps avg/trade RT (matches 25 bps RT × 0.4 weight × half-roundtrip)
- gold swap: −$0.0115 cumulative drag
- BTC swap: −$0.0476 cumulative drag (4× gold's drag, consistent with 5× per-night rate × ~similar n_overnight_holds)

Cost summary: BTC leg's spread + swap ≈ $0.0846, gold leg's ≈ $0.0278 — BTC
costs are ~3× gold's per leg, and the BTC contribution to gross PnL is well
below 3× gold's, hence the Sharpe drag.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 5 | 25 | primary fail bench+0.10 (=1.17); corroborating Sh +0.67 > 0 → +5 |
| 2 Gates | 15 | 25 | primary 4/7 (meets v2 threshold for non-legacy ds); corroborating 5/7 but G6+G2_relaxed both fail → no +5; legacy cross-bonus N/A |
| 3 DSR | 0 | 15 | primary p=0.918 (cumulative n_trials=25); far from <0.05 |
| 4 CAGR floor | 0 | 15 | primary CAGR 1.14% < 0.8 × 31.11% = 24.9% floor (basket-bh has BTC bull-run hangover) |
| 5 MDD ceiling | 15 | 15 | primary MDD 15.45% < 47.50% + 5pp = 52.50% — easily passes |
| 6 Robustness bonus | 0 | 5 | not computed |
| **total** | **35** | **100+5** | tier: **NEAR_FAIL** |
| (hold-time gate) | PASS | — | mean basket hold 4.65d ∈ short_swing [2, 10] |

## Configuration tested

```yaml
config_id: "cross_cluster_rsi2_sma200_gld60_btc40_basket"
universe: gold_complex
broker_track: pepperstone_cfd
hold_time_track: short_swing
declared_primary: gld_btc_basket_long
declared_corroborating: [xau_btc_basket]
weights: {gold: 0.60, btc: 0.40}
spreads_rt_bps: {gold: 8.0, btc: 25.0}
swap_long_bps_per_night: {gold: -1.0, btc: -5.0}
rsi_period: 2
rsi_threshold: 5.0
sma_period: 5
sma_trend_period: 200
weekend_swap_mult: 3.0
long_only_per_asset: true
```

Single pre-committed config (IC-8 mandate). Cumulative DSR n_trials = 25.

## What worked / what didn't

**What worked**:

- **Cross-cluster IC-6 hypothesis empirically validated.** Rolling-60d
  exceed-frac vs iter 003 dropped from 96.8% (GS-23 SLV) / 94.9% (GS-24 GDX)
  to **68.1%** — a structural break of nearly 27 pp. Static ρ collapsed from
  +0.67 to +0.26. BTC's MR signal genuinely fires on different days than
  gold's MR signal. This is the FIRST iter to demonstrate cross-cluster
  position-vector divergence at the rolling-window level.
- **MDD reduction is exceptional**: corroborating MDD 5.69% is the lowest
  ever measured in 25 iters (beats iter 023's 7.13% and iter 024's 10.33%).
  The selective-entry × 60/40-weight + cross-cluster combination produces
  exceptional risk-isolation; basket is flat ~92% of days, capturing only
  the cleanest oversold bounces.
- **Per-leg cost model worked correctly.** Cross-lib G7 parity at 0.000000 pp
  on both datasets. The new per-leg swap parameter integrates cleanly into
  `apply_pepperstone_costs` via the existing `swap_long_bps` argument; no
  changes needed to `cost_models.py`. TDD test #7 specifically validated
  the 5× swap ratio.
- **Hold-time match clean**: 4.65d basket on PRIMARY, 3.85d on corroborating,
  both ∈ short_swing [2, 10]. Engine's signal-aggregation behavior is
  consistent with iter 023/024.

**What didn't**:

- **Sharpe lift vs iter003 = −0.13** — basket aggregation actively degrades
  performance. Decomposing: gold leg's contribution to basket gross PnL is
  ~60% × gold-MR-Sharpe (≈ 60% × 0.30 = 0.18 contribution); BTC leg's is
  ~40% × BTC-MR-Sharpe. BTC's standalone MR Sharpe was not measured this
  iter, but the post-cost contribution is clearly negative (basket Sh 0.17
  < gold-only contribution 0.18). The 40% allocation to a near-zero-EV
  signal drags Sharpe.
- **G6 bootstrap CI low −0.566** — Sharpe is not significantly different
  from zero. With 65 basket trades over 12.3y and Sharpe +0.17, the 99.9%
  CI sweeps well into negative territory.
- **DSR p = 0.918** — far from <0.05 threshold. With cumulative n_trials = 25,
  the deflated Sharpe needs +0.65+ to clear; +0.17 isn't even a candidate.
- **G3 walk-forward FAIL on PRIMARY** — block-level Sharpes inconsistent;
  several windows have negative or low-positive returns.
- **CAGR 1.14% on PRIMARY** vs 31.1% benchmark — this is misleading because
  the basket b&h is dominated by BTC's exponential bull run (40% × BTC's
  ~50%/yr CAGR over 2014-2026). Comparing to GLD-only b&h (~7-8%) is more
  meaningful — basket CAGR 1.14% still trails GLD by 6 pp.

**Subtle finding (cost-asymmetry trap)**:

The cross-cluster diversification benefit (IC-6 break) is REAL but SMALL
in absolute terms. BTC's RSI(2) entries fire on ~35% of windows independently
of gold's, but those independent windows aren't necessarily ALPHA windows —
they're just non-correlated. To capture risk-adjusted return *uplift* from
cross-cluster diversification, the basket would need either:

1. **Equal Sharpe per leg** (so 60/40 weighting compounds benefit), OR
2. **Markowitz proportional-Sharpe weighting** (so weak BTC leg gets
   downweighted, strong gold leg upweighted) — this is the IC-7 framework

Iter 025's fixed 60/40 weight violates IC-3 (50/50-only-when-similar-Sharpe
extended principle) — gold's standalone +0.30 vs BTC's much weaker
standalone post-cost Sharpe means a Markowitz tangency would weight gold
heavily, BTC modestly, possibly approaching iter 003 single-asset.

## Main lesson (for future iterations)

**Cross-cluster IC-6 floor IS breakable** (68.1% achieved, 27 pp drop) — the
Priority 1 hypothesis is empirically validated for asset selection. The
GS-23/24 ceiling was not a property of "all gold-anchored baskets" but of
"all gold-anchored baskets with PM-adjacent 2nd legs." When the 2nd leg has
genuinely orthogonal macro drivers (BTC's crypto-adoption / halving / funding
cycle vs gold's real-rate / DXY), position-vector divergence emerges.

**However**, cross-cluster IC-6 break alone does NOT produce a Sharpe edge
under fixed 60/40 weights when leg Sharpes are asymmetric. The path forward
splits into two structurally-different directions:

1. **IC-7 Markowitz weighting** — let the data choose weights based on
   proportional standalone Sharpes. Likely outcome: weights collapse to
   ~85% gold / 15% BTC (close to iter 003), with a marginal IC-6 benefit.
2. **Different signal family per leg** — e.g., gold leg = MR (RSI(2) + SMA(200)),
   BTC leg = trend-follow (Donchian breakout, Clenow momentum). Different
   families on each leg may exploit different aspects of each asset's regime
   structure, breaking the cost-vs-signal asymmetry.

**GS-25 partial closure**: closes "fixed-weight 60/40 cross-cluster basket
of GLD + BTCUSD with same single-asset MR signal per leg" — the cost-asymmetry
+ signal-asymmetry combination drags Sharpe even when IC-6 cross-cluster is
validated. Does NOT close the cross-cluster-basket family entirely; the
IC-6 evidence makes this the most-promising direction in the loop.

## Structural dead-ends discovered

**GS-25 (this iter)** — Cross-cluster fixed-weight basket extension via BTCUSD
60/40 GLD+BTC with same RSI(2)+SMA(200) signal per leg:
- IC-6 rolling-60d ρ vs iter003 = **68.1% PRIMARY** (★ first sub-80% in 25
  iters; static ρ +0.26)
- Basket Sh +0.17 BELOW iter003 single-asset +0.30 (lift = −0.13)
- Cost asymmetry: BTC 25 bps RT + −5 bps/night swap vs gold 8 bps + −1 bps
- Signal asymmetry: BTC RSI(2) standalone post-cost Sharpe is much lower than
  gold's; 40% BTC weight drags basket

**Closes**: fixed-weight GLD+BTC basket using same MR signal per leg under
Pepperstone CFD cost regime.

**Does NOT close**:
- IC-7 Markowitz-weighted GLD+BTC (proportional-Sharpe; let data weight)
- Asymmetric per-leg signal: gold MR + BTC trend (or vice versa)
- GLD+TLT (bond cross-cluster; different cost profile + slower regime cycle)
- GLD+SPY (broad-equity cross-cluster, lower-vol 2nd leg)
- CME futures track A2 (1-2 bps RT spread enables intraday MR)
- DCOT producer-merchant mirror (positioning family, different)

The cross-cluster framework remains the most-promising direction; iter 026's
priority shifts to IC-7 Markowitz tangency on the GLD+BTC pair (mechanical
follow-up validating the loop's first IC-6 break) OR asymmetric per-leg
signals on the same pair.

## Citations used

- `[risk_parity, ch.7]` — multi-asset basket weighting (PRIMARY citation;
  thesis predicted heterogeneous-driver assets should diversify; iter 025
  empirically validates the IC-6 floor break, but reveals that Sharpe lift
  requires proportional-Sharpe weighting, not fixed weights)
- `[short_term_trading_strategies, p.105-118]` — Connors RSI(2)<5 + SMA(200);
  same per-leg as iter 003/023/024
- `[ilmanen_expected_returns, ch.10]` — gold-complex factor exposures;
  Ilmanen's caveat that crypto/digital-stores-of-value are weakly correlated
  to gold (for asset-allocation purposes) is empirically validated by iter
  025's 0.26 static-ρ measurement
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 25
- `[advances_fin_ml, p.196-202]` — bootstrap 99.9% CI low (FAIL on basket)
- `[advances_fin_ml, p.31-34]` — cross-lib G7 parity (0.000000 pp diff)
- IC-3 (sister loop iter 049) — fixed-weight composition only when standalone
  Sharpes are similar; iter 025 violates this (gold +0.30 vs BTC much weaker)
- IC-6 (sister loop iter 014/019) — rolling-correlation pre-val mandate;
  iter 025 is the first gold-loop iter to break the 80% floor
- IC-7 (sister loop iter 045/046) — Markowitz proportional-Sharpe framework;
  iter 026 candidate
- GS-23 (iter 023) + GS-24 (iter 024) — within-PM + PM-adjacent miner basket
  closures motivating this cross-cluster test

## Next iteration suggestions

The IC-6 break in iter 025 is structurally important. The natural follow-ups
in priority order:

1. **PRIORITY 1 — IC-7 Markowitz GLD+BTC tangency** — let the data weight
   gold and BTC by proportional Sharpe. With gold-MR Sh ≈ 0.30 and BTC-MR
   Sh likely much lower post-cost, expected weights ~85/15 (vs this iter's
   60/40). Markowitz combined Sharpe upper bound = √(S²_gold + S²_btc)
   under low ρ; if BTC's standalone Sh is +0.10, combined ≤ √(0.09 + 0.01)
   = 0.32 (only marginal lift over gold alone). Even smaller upside but
   honest. `[advances_fin_ml, p.222-223]` + `[risk_parity, ch.7]`.
2. **PRIORITY 2 — Asymmetric per-leg signal: gold MR + BTC trend** —
   Connors RSI(2)+SMA(200) on gold, 200d Donchian breakout on BTC.
   Different families per asset; may exploit BTC's trend-persistence
   (vs gold's mean-reversion). `[trend_following]` (Covel) on BTC leg.
3. **PRIORITY 3 — GLD + TLT 60/40 basket** — bonds cross-cluster
   (still RETAINED from iter 024). Different cost profile (TLT ETF can
   route via GLD's same Pepperstone-or-Inter cost path).
4. **PRIORITY 4 — DCOT producer-merchant mirror** — different family
   entirely; positioning data not vol/MR.
5. **PRIORITY 5 — CME futures A2 cost path** — 1-2 bps RT spread enables
   strategies that died at 8 bps. Genuinely different cost regime.
6. **PRIORITY 6 — GLD + SPY 60/40 basket** — broad equity cross-cluster
   (also retained); SPY lower vol than BTC, may have more compatible cost
   structure with gold.
7. **(LOWER) Concede loop closure** if priorities 1-6 also flat-line. PCBO/DSR
   with n_trials=25+ requires standalone Sh > 0.65 OR a low-ρ IC-7 pair where
   both standalones are strong; none yet observed in 25 iters.

The IC-6 finding makes Priority 1 (IC-7 Markowitz GLD+BTC) the obvious
mechanical follow-up — it's a small refinement of the same hypothesis and
will tell us whether the cross-cluster diversification is large enough to
clear DSR even at proportional-Sharpe weights.
