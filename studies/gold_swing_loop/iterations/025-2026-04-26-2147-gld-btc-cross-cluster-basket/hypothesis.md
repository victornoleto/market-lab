# Iteration 025 — GLD + BTCUSD 60/40 cross-cluster RSI(2)+SMA(200) basket

## Hypothesis

Apply iter 003's per-asset Connors RSI(2)<5 + SMA(5)-exit + SMA(200)-trend-filter
signal independently to (a) gold ETF GLD and (b) Bitcoin spot BTCUSD; aggregate
at fixed weights 60% GLD / 40% BTC (XAU-anchor ≥ 40% per spec). The hypothesis is
that BTC's mean-reversion dips fire on **structurally orthogonal macro drivers**
(crypto-adoption cycles, halving-supply shocks, regulatory/banking events,
funding-rate-led liquidations) compared to gold's drivers (real rates / DXY /
safe-haven flows / central-bank reserve flows), and that this orthogonality
should manifest as **rolling-60d position-vector correlation vs iter 003 ≤ 80%**
on PRIMARY — i.e., the basket position vector must diverge enough from the pure
single-asset signal to validate cross-cluster diversification.

This is the FIRST GENUINELY cross-cluster test in 24 iters: GS-23 (GLD+SLV)
closed at IC-6 rolling-60d 96.8% and GS-24 (GLD+GDX) at 94.9%, both showing
that within-precious-metals and PM-adjacent miner-equity baskets share gold's
macro clock. Iter 025 substitutes a 2nd leg with documented low ρ to gold
(BTC-gold rolling-12m ρ historically ~0.10-0.30, vs GDX-gold's ~0.7-0.8).

## Primary citation

`[risk_parity, ch.7]` — multi-asset basket weighting motivates aggregating
heterogeneous-driver assets at fixed risk-budget weights. The thesis predicts
that lower-ρ-driver pairings produce more diversification benefit; iter 025
empirically tests whether GLD-BTC cross-cluster pairing breaks the GS-23/24
ceiling.

## Additional citations

- `[short_term_trading_strategies, p.105-118]` — Connors RSI(2)<5 + SMA(200)
  trend-filter long-only signal; reused unchanged from iter 003 per leg.
- `[ilmanen_expected_returns, ch.10]` — gold-complex factor exposures.
  Ilmanen documents gold-mining stocks ρ ~0.7-0.8 to spot gold (which iter 024
  empirically confirmed via GS-24); iter 025 escapes that constraint by
  selecting a genuinely-non-PM-cluster asset (BTC) for the 2nd leg.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 25.
- `[advances_fin_ml, p.196-202]` — bootstrap 99.9% CI low > 0 gate.
- `[advances_fin_ml, p.31-34]` — cross-lib parity (G7).
- IC-6 (sister loop iter 014/019) — rolling-correlation pre-val mandate.
- IC-3 / IC-7 — basket-aggregation framework (60/40 fixed weights, NOT
  Markowitz; structurally a basket extension of iter 003 single-asset).
- GS-23 (iter 023) + GS-24 (iter 024) — closures of within-PM and PM-adjacent
  basket extensions; iter 025 is the structurally-novel direction promoted as
  Priority 1 in BASE_MEMORY by their finalisation.

## Edge source

Gold's MR-RSI(2) signal alone (iter 003 +0.30 Sh on gld_long) trails buy-hold
by Δ −0.38 because gold's persistent drift is too steep for any selective-entry
signal to bridge. The hypothesis is that **basket-aggregating gold-MR with a
genuinely orthogonal-driver MR signal (BTC) lifts the basket's risk-adjusted
return** by exposing the portfolio to two largely independent oversold-bounce
populations. Concretely: when BTC dips on a halving-front-running rally exhaustion
(Q3 2017, Q1-Q2 2021, Q2 2024), gold may be flat or up on real-rate dynamics —
the BTC leg picks up edge on days the gold leg sits flat, lifting overall Sharpe.

## Datasets

- **PRIMARY**: `gld_btc_basket_long` = 60% GLD + 40% BTCUSD daily,
  joint window 2014-01-02 → 2026-04-14 (3 085 bars, 12.28 y).
  - Reason: longest joint window with BTC; covers 3 BTC halving cycles
    (2016, 2020, 2024) + 2 gold regimes (2014-2018 stagnation,
    2019-2026 revival).
- **CORROBORATING**: `xau_btc_basket` = 60% XAUUSD spot + 40% BTCUSD daily,
  joint window 2020-01-02 → 2026-04-14 (1 696 bars, 6.28 y).
  - Reason: actual instrument (XAUUSD spot CFD on Pepperstone) on shorter
    cost-realistic window; same regime-overlap with BTC's 2020+ era.

Per relaxed rules 2026-04-26-r1: PRIMARY gets full gate count (4/7 threshold
for non-legacy 12y dataset, matching iter 023/024 convention); CORROBORATING
gets relaxed gates (G6 bootstrap CI low > 0 + G2 DSR p < 0.20).

## Timeframes used

`["1d"]` only. RSI(2)+SMA(200)+SMA(5) signal is daily-bar; per-leg signals
generated independently on each asset's daily series, then weighted-aggregated
on the inner-joined date index. NO 30m/15m/1m fetch needed.

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A only).

- Track A (Pepperstone): GLD spot-CFD-equivalent + BTCUSD CFD; long-only;
  per-leg cost model with leg-specific spread + swap.
- Track B (Inter ETF): NOT applicable — Inter Internacional does NOT offer
  BTC ETF (or spot Bitcoin) for Brazilian retail; GBTC was a closed-end fund
  with significant tracking error and is being unwound. IBIT/FBTC spot BTC
  ETFs (post-Jan 2024) are technically listed but not in Inter's standard
  retail catalog. Track B excluded.

## Hold-time profile

- Expected mean hold (basket position any-leg-in): ~4-5 trading days
  (matches iter 023 4.15d, iter 024 4.91d basket).
- Hold-time track: `short_swing` (bounds [2.0, 10.0] trading days).
- Per-leg: gold leg ~3-4d (matches iter 003); BTC leg unknown (BTC's RSI(2)<5
  + SMA(200) gating frequency depends on BTC-specific volatility regime —
  needs empirical measurement).
- Pre-committed: PASS if observed basket mean hold ∈ [2, 10] on PRIMARY.

## Pre-validation screen (mandatory for overlays per IC-6)

This is a basket-extension, not a Markowitz overlay, but IC-6 still applies:
**rolling-60d position-vector correlation between basket-net-returns and
iter 003 net-returns must be measured** as part of Stage 3, with kill criterion
fired if exceed_frac(|ρ| > 0.30) > 80% on PRIMARY (relaxed from 95% standard
because cross-cluster expects measurable position divergence). 80% chosen
because:
- iter 023 (within-PM): 96.8% → cross-cluster must beat that
- iter 024 (PM-adjacent miner): 94.9% → cross-cluster must beat that
- IC-6 standard (overlay → 30%) too tight for basket-extension family
- 80% leaves 20 pp room for cross-cluster to demonstrate divergence

If rolling exceeds 80%, the cross-cluster hypothesis is falsified — BTC behaves
like just another PM-adjacent asset (which would be a surprise given documented
0.10-0.30 BTC-gold ρ).

## Cost model (per leg, Track A)

| component | gold leg | BTC leg | rationale |
|---|---:|---:|---|
| spread RT | 8 bps | 25 bps | Pepperstone XAUUSD baseline; BTCUSD CFD typically $50-100 spread on $60-70k BTC ≈ 7-15 bps single-leg, 15-30 bps RT; midpoint conservative |
| swap long (per night) | −1 bps | −5 bps | Gold standard; BTC long swap on Pepperstone is documented in the −10 to −25 bps/night range during normal carry; conservative −5 bps |
| swap short | +0.3 bps | +1.0 bps | N/A in long-only this iter |
| weekend swap mult | 3× | 3× | Pepperstone applies 3× weekend swap to all CFDs incl. BTCUSD even though BTC trades 24/7 (CFD position is held against PEP overnight book) |
| commission | 0 | 0 | Built into spread |
| slippage on stops | 5 bps | 10 bps | Not modeled in basket signal (no stops; SMA(5) exit on close) |

Per-leg cost is applied to the leg's position contribution (weight × asset
signal), exactly like iter 024. BTC's wider spread + heavier swap make this a
genuinely tougher cost regime than GDX (12 bps RT + −1 bps); even with low ρ,
BTC must add edge net of 2-3× higher costs to lift the basket.

## Expected budget

- Configs to test: **1** (single pre-committed cfg per IC-8 mandate).
- Wall-time: ~30-60 minutes (engine reuse from iter 024; new BTC fetch
  unnecessary — already cached).
- Files to create:
  - `hypothesis.md` (this file)
  - `run_backtest.py` (≈ iter 024 with BTC substitution + cost adjustments)
  - `test_basket_signal.py` (TDD; ≈ iter 024 test file with BTC substitution)
  - `results.json`
  - `verdict.json`
  - `final_report.md`

## Implementation plan

1. Copy `iterations/024-*/run_backtest.py` and `test_basket_signal.py` as
   starting templates.
2. Substitute `gdx → btcusd`:
   - DATASETS paths: `data/tiingo/daily/prices/btcusd.parquet`
   - Dataset names: `gld_btc_basket_long`, `xau_btc_basket`
   - Cost dict: `SPREADS_RT_BPS = {"gold": 8.0, "btc": 25.0}`
   - SWAP_LONG_BPS_PER_NIGHT: per-leg dict `{"gold": -1.0, "btc": -5.0}`
   - Update `apply_pepperstone_costs` calls to accept per-leg swap (extend
     cost_models.py if not already supported, OR fold swap into the same call
     by passing per-leg swap-bps).
3. Update the cross-lib G7 hand-roll to apply per-leg swap (currently iter 024
   hardcoded `swap_long = -1.0/1e4`; this iter must parameterise per-leg).
4. Update IC-6 baseline mapping: iter 003 gld_long → gld_btc_basket_long,
   iter 003 xauusd_real → xau_btc_basket; iter 011 same.
5. Run TDD tests (must pass; baseline pytest still green).
6. Execute `run_backtest.py` end-to-end; write results.json + verdict.json.
7. Compute mean basket hold + IC-6 rolling rho + 6 kill criteria.
8. Score via `score_strategy_v2`.
9. Write final_report.md.
10. Update BASE_MEMORY.md (frontmatter + iter log + top-K + dead-ends if applicable).

## Pre-committed kill criteria (binary, evaluated on PRIMARY)

| # | name | condition fires kill | rationale |
|---|---|---|---|
| 1 | sh_lt_0_30 | basket Sh < 0.30 | must beat iter 003 single-asset baseline |
| 2 | sh_lift_lt_0_05 | basket Sh − iter003 Sh < +0.05 | basket aggregation must show positive lift, not drag |
| 3 (HARD) | ic6_rho_v003_gt_80pct | IC-6 rolling-60d exceed-frac vs iter003 > 80% | THE cross-cluster test; must drop below GS-23/24 floor |
| 3b | ic6_rho_v011_gt_30pct | IC-6 rolling-60d vs iter011 > 30% | must NOT be vol-regime in disguise (GS-22 family) |
| 4 | g6_boot_fail | G6 bootstrap CI low ≤ 0 | Sharpe must be statistically significant |
| 5 | dsr_p_gt_0_30 | primary DSR p > 0.30 | DSR-deflator at n=25 needs Sh > ~0.65; iter 024 was 0.86, must show meaningful improvement |

Falsification rule: **kill #3 firing alone is sufficient** to close the
cross-cluster basket family for ALL iter-025-and-similar candidates. Other
kills firing without #3 leaves cross-cluster as a viable family but with
this specific signal underperforming. Both #1 AND #3 firing → close the
family decisively (consistent with GS-23/24).

## Structural novelty argument (vs DEAD_ENDS catalog)

This iter is structurally different from every catalogued closure:
- **GS-1 (iter 001)**: pure RSI(2) MR no regime → iter 025 includes SMA(200) regime gate
- **GS-3 (iter 002/003)**: single-mech standalone → iter 025 is multi-asset basket
- **GS-7 (iter 007)**: z-MR cost-dominated → iter 025 RSI(2) survived GS-1 closure
- **GS-11/12/13 (iter 011-013)**: vol-regime family → iter 025 is RSI-MR family (no σ_60/σ_252 input)
- **GS-14/15 (iter 014/015)**: macro-rate/DXY → iter 025 has no macro overlay
- **GS-17/18/19/20/21 (iter 017-021)**: COT positioning → iter 025 is price-MR
- **GS-22 (iter 022)**: GVZ implied-vol → iter 025 has no IV input
- **GS-23 (iter 023)**: GLD+SLV within-PM → iter 025 BTC is non-PM
- **GS-24 (iter 024)**: GLD+GDX PM-adjacent miner → iter 025 BTC has zero gold-loading
- **IC-1**: not vol-target wrapped
- **IC-2**: no double-counted regime gate (SMA(200) is input only)
- **IC-3**: 60/40 not 50/50; mandate-imposed weights, not equal
- **IC-4**: not modulating the iter 003 base; adding a NEW orthogonal-driver leg
- **IC-5**: gold/BTC are single-name positions, not cross-sectional ranking
- **IC-6**: pre-val rolling-ρ explicitly built into kill #3
- **IC-7**: this is fixed-weight basket, not Markowitz tangency (60/40 baseline; would invite a future iter 026 IC-7 Markowitz-weighted GLD+BTC)
- **IC-8**: single pre-committed cfg

The novelty is the **BTC leg** — first non-PM, non-equity-derivative,
non-bond asset entered as a 2nd leg in a gold-anchored basket in 25 iters.
