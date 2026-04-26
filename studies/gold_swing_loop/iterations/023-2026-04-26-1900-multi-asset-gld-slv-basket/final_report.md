# Iteration 023 — Final Report

## Verdict

📉 **NEAR_FAIL** — score **35/100**, `winner_conditions_met=false`,
`hold_time_gate_pass=true` (mean hold 4.15d on PRIMARY ∈ short_swing 2-10d).

**ALL 6 of 6 pre-committed kill criteria fired:**

- ❌ Kill #1 — primary Sh +0.2954 < +0.30 threshold (basket fails to even
  match iter 003's single-asset gold Sh +0.30).
- ❌ Kill #2 — Sh lift vs iter 003 = **−0.0046** (basket adds essentially
  zero edge over single-asset MR).
- ❌ Kill #3 — IC-6 rolling-60d ρ vs iter 003 (single-asset RSI MR) =
  **96.8% on PRIMARY** (vs 95% threshold) — silver leg does NOT
  diversify the gold leg's position vector.
- ❌ Kill #3b — IC-6 rolling-60d ρ vs iter 011 (vol-regime) = **33.1% on
  PRIMARY** (vs 30% threshold) — basket DOES partially ride the gold-
  vol-regime macro clock that trapped iters 014/015/022.
- ❌ Kill #4 — primary G6 bootstrap 99.9% CI low = **−0.378** (fragile).
- ❌ Kill #5 — primary DSR p = **0.7371** ≫ 0.30 threshold.

## Headline metrics (top candidate, NET of Pepperstone Track A per-leg costs)

| dataset | Sharpe (basket bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | mean hold | DSR p |
|---|---|---|---|---|---|---|
| **gld_slv_basket_long** PRIMARY (60% GLD + 40% SLV, 19.97y) | +0.2954 (Δ −0.137 vs 0.4323) | +1.17% (Δ −6.51% vs 7.68%) | **9.19%** (Δ −52.50% vs 61.69% bench) | **4/7** | 4.15d | 0.737 |
| **xau_xag_basket** CORROBORATING (60% XAU + 40% XAG, 6.29y) | +0.2569 (Δ −0.633 vs 0.8903) | +0.98% (Δ −22.67%) | **7.13%** (Δ −21.30%) | **4/7** | 4.00d | 0.897 |

Gates pattern (identical on both): G1_PBO ✓ G2_DSR ✗ G3_WF ✗ G4_OOS ✓
G5_FWD ✓ G6_boot ✗ G7_crosslib ✓.

Cross-lib G7: pandas vs numpy basket-CAGR difference < 1e-6 on both
datasets (clean parity; the per-leg aggregation engine is correct).

OOS Sharpe (last 30%): +0.216 / +0.226. FWD post-2022: +0.307 / +0.384.

## Score breakdown (rules_version `2026-04-26-relaxed-r1`)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 5 | 25 | primary 0.295 < 0.432+0.10 → 0pts; corroborating Sh +0.26 > 0 → +5 |
| 2 Gates | 15 | 25 | primary 4/7 ≥ threshold 4 → +15; corroborating G6 fail + G2 (relaxed) fail (p=0.897 > 0.20) → 0; no legacy ds bonus |
| 3 DSR | 0 | 15 | primary p=0.737 ≫ 0.20 → 0 |
| 4 CAGR floor | 0 | 15 | primary CAGR 1.17% < 0.8 × 7.68% = 6.14% → fail |
| 5 MDD ceiling | 15 | 15 | primary MDD 9.19% ≤ 61.69% + 5pp → pass (huge margin) |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **35** | **100+5** | tier: **NEAR_FAIL** |
| (hold-time gate) | pass | — | mean hold 4.15d ∈ short_swing 2-10d ✓ |

## Configuration tested

```python
cfg_id = "multi_asset_rsi2_sma200_gld60_slv40_basket"
weights = {"gold": 0.60, "silver": 0.40}      # XAU >= 40% per spec
spreads_rt_bps = {"gold": 8.0, "silver": 20.0}  # XAG ~2.5x wider in practice
swap_long_bps_per_night = -1.0                # both legs Pepperstone Track A
rsi_period = 2; rsi_threshold = 5.0; sma_period = 5; sma_trend_period = 200
long_only_per_asset = True                     # binary {0,1} signal per asset
broker_track = "pepperstone_cfd"
universe = "gold_complex"; hold_time_track = "short_swing"
declared_primary = "gld_slv_basket_long"   # 60% GLD + 40% SLV daily, 2006-04-28→2026-04-15
declared_corroborating = ["xau_xag_basket"]  # 60% XAUUSD + 40% XAGUSD daily, 2020-01-02→2026-04-17
```

Cumulative `n_trials = 23` (was 22 after iter 022).

## What worked / what didn't

**MDD reduction is the only structural improvement.** Basket MDD on
PRIMARY = 9.19% vs single-asset gold benchmark's 45.6% (and basket
buy-hold itself is 61.69% MDD because silver's bear depth in 2013-2015
amplified gold's). This is the lowest MDD ever seen in the loop on a
~20-year window, by a wide margin. The MR signal's selectivity is the
mechanism (basket only fires when both legs' SMA(200) gates are ON,
limiting exposure to high-vol bear regimes).

**But Sharpe doesn't lift, because both legs fire on essentially the
same days.** The 60/40 basket position vector has rolling-60d ρ = 96.8%
with iter 003's single-asset gold position vector — meaning the silver
leg's RSI(2)<5 AND `close > SMA(200)` conditions trigger on
overlapping bars with the gold leg's same conditions. **Both metals
are above SMA(200) at the same time** (joint precious-metals bull
regime); **both have RSI(2) oversold dips on the same days** (joint
stress-driven 1-2 bar pullbacks within those bull regimes). The
basket reduces to a noisier version of single-asset gold, with extra
silver-leg cost drag (silver spread 20 bps RT vs gold 8 bps × ~80
silver-leg trades/yr).

**Static ρ +0.714 vs +0.764**: confirms 60-70% of basket return
variation is gold-leg variation. Silver leg adds 30% noise on the
return side, but the SIGNALS fire at 96%+ overlap. Decoupling them
would require silver leg to use a DIFFERENT signal (e.g., gold MR +
silver breakout) — but that's no longer the same hypothesis.

**Why the basket benchmark itself has lower Sharpe than gold-only**
(0.43 vs 0.68): silver underperformed gold on Sharpe over 2006-2026
(silver buy-hold Sh ≈ 0.20; gold ≈ 0.68; 60/40 weighted ≈ 0.43). The
silver allocation drags the basket benchmark Sharpe BELOW gold-only,
making the basket ironically "easier to beat" in absolute Sharpe-edge
terms — but the strategy still doesn't beat the basket bench by 0.10
because it's just iter 003 with extra cost.

**Why DSR p = 0.74**: standalone Sh +0.295 with `n_trials = 23` over
20 years is well below the deflator-cleared threshold (~+0.65 at n=23+).
The basket's near-identical position vector to iter 003 means it
inherits iter 003's DSR weakness (iter 003 DSR p = 0.43).

**Why G6 bootstrap CI low = −0.378**: 20-year daily series has fat
lower tail when the strategy's positive return is concentrated in
joint precious-metals MR episodes (~80-100 per year per leg, but
clustered in stress windows). At α=0.001 the CI captures "what if
the 2-3 strongest stress windows hadn't happened" → heavily negative.

## Main lesson (for future iterations)

★ **GS-23**: A within-precious-metals multi-asset basket
(60% GLD + 40% SLV) extension of a single-asset MR signal IS NOT
structurally distinct from the single-asset version on the position-
vector level. **Basket position vector vs single-asset (iter 003): static
ρ = +0.714, rolling-60d ρ exceed-frac = 96.8% on PRIMARY** — silver
leg adds essentially zero structural diversification because both
precious metals are above SMA(200) at the same times (joint bull
regime) and have RSI(2) oversold dips on the same days (joint stress-
driven pullbacks). Basket Sh = +0.295 ≈ iter 003 alone +0.30 (lift
−0.005); MDD improves dramatically (9.19% vs 45.6% benchmark) but
DSR/G6 still fail (p=0.737, CI low −0.378).

**Closes**: any precious-metals-only multi-asset gold_complex basket
extension (GLD+SLV, IAU+SLV, XAU+XAG, GLD+SLV+PPLT) of a single-asset
MR or trend signal as a "structurally novel" direction. The position-
vector overlap is too high for the basket to escape the single-asset
DSR-deflator wall at n_trials=23+. Sister loop's "every winner was
multi-asset" lesson must specifically refer to baskets with **cross-
cluster diversification** (precious metals + equities, precious
metals + crypto, precious metals + bonds), NOT within-cluster
extension. The basket's only structural improvement is MDD reduction,
which is a portfolio-construction property orthogonal to the Sharpe
edge requirement.

**Does NOT close**:

- **Cross-cluster basket extension** (GLD + GDX miners): GDX has stock-
  market beta (S&P 500 ρ ~0.45) absent from spot gold; miner MR signal
  fires on a partially-different macro driver (equity stress + gold
  price). Requires GDX Tiingo fetch (single API call). Position-vector
  overlap with gold-MR signal expected ~0.55-0.65 (much lower than
  GLD+SLV's 0.96), giving real IC-7-eligible diversification.
- **Gold + BTC basket** (GLD + BTCUSD): different macro driver entirely
  (digital scarcity narrative). Cached in `data/tiingo/daily/prices/btcusd.parquet`
  (2014-01+). Position-vector overlap likely < 0.20.
- **Gold + bonds basket** (GLD + TLT): bonds = duration risk, gold =
  inflation/safe-haven. Different signal mechanisms entirely.
- **GLD + SLV with DIFFERENT signals per leg** (e.g., gold MR + silver
  breakout): not the same hypothesis as iter 023; structurally legit.
- **CME GC futures track A2** (BASE_MEMORY priority 1): cost-path
  branch with 1-2 bps RT spread; structurally different cost regime
  enables previously-cost-dominated MR strategies.
- **DCOT producer-merchant hedger-side mirror** (BASE_MEMORY priority 2).
- **All single-asset signal families not yet tested** (e.g., Bollinger
  squeeze + trend, breakout + RSI confirmation).

## Structural dead-ends discovered

GS-23 added below to DEAD_ENDS.md and BASE_MEMORY's "Structural dead-
ends" section. Cross-loop relevance: the IC-7 framework (sister loop)
requires component streams to be at ρ < 0.50; within-precious-metals
basket overlap at 0.96 is far above that bar. Confirms that "multi-
asset" is necessary but NOT sufficient for IC-7 lift; the assets must
be from different macro-driver clusters.

## Citations used

- `[risk_parity, ch.7]` — multi-asset basket weighting (PRIMARY)
- `[short_term_trading_strategies, p.105-118]` — Connors RSI(2)+SMA(200)
  trend filter (per-asset signal generator, identical to iter 003)
- `[ilmanen_expected_returns, ch.10]` — precious metals as a defensive
  asset-class basket
- `[trading_systems_methods, p.301-310]` — Kaufman regime-conditional MR
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 23`
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest (per-leg
  spread tier 8 bps gold / 20 bps silver)
- IC-6 sister-loop closure (014/019) — pre-val rolling-correlation
  diagnostic on PRIMARY
- IC-7 sister-loop framework (045/046) — Markowitz proportional-Sharpe
  weighting at ρ < 0.50; this iter shows ρ = 0.96 is the wrong basket
  composition

## Next iteration suggestions

The within-precious-metals path is now closed. The two remaining high-
priority paths (per BASE_MEMORY priority 1+2) plus a new cross-cluster
basket direction:

1. **(NEW PRIORITY 1, PROMOTED) Cross-cluster basket: GLD + GDX miners
   60/40 with same RSI(2)+SMA(200) signal per leg**. GDX (gold miners
   ETF) has stock-market beta absent from spot gold; the miner MR
   signal should fire on a partially-different macro driver
   (equity stress + gold price). Requires single Tiingo fetch for
   GDX (cheap). Expected position-vector overlap with iter 003
   gold-MR signal: ρ_static ~0.55-0.65, rolling exceed-frac < 80%.
   If overlap < 80%, basket may genuinely diversify and lift Sharpe
   beyond single-asset. `[risk_parity, ch.7]` + GDX fetch + iter 023
   engine reused unchanged.
2. **(PRIORITY 2, RETAINED) DCOT producer-merchant hedger-side mirror**
   — long when prod-merc z<−1 = producers crowded short. Different
   COT bucket than iter 021 (MM); data already cached in
   `cftc_dcot_gold_weekly.parquet`. May capture the hedging-pressure
   leverage that GS-21 attributed to legacy commercials.
3. **(PRIORITY 3, RETAINED) CME futures track A2 cost-path branch** —
   re-test cost-dominated intraday MR (iter 007 z-MR died at 8 bps;
   futures @ 1-2 bps may rescue it). Requires CME GC futures data
   (Quandl/Norgate/Yahoo continuous). Genuinely structurally different
   cost regime.
4. **(PRIORITY 4, NEW) Gold + BTC cross-cluster basket** — digital-
   scarcity narrative orthogonal to precious-metals macro driver.
   BTCUSD cached (2014-01+). Same engine as iter 023 with crypto
   substituted for silver leg.
5. **(PRIORITY 5, NEW) Gold + LQD/TLT cross-cluster basket** — bonds
   add duration/inflation drivers. Need to fetch LQD or TLT via Tiingo
   (cheap). Different mechanism for SMA(200) trend filter (bond trend
   regimes are slower).
6. **(LOWER PRIORITY) Concede loop closure** if priorities 1-5 flat-line.
   The 23-iter cumulative DSR-deflator wall on this single-asset XAU
   universe (and now gold_complex within-cluster) is structural;
   beyond cross-cluster basket extension, the path forward likely
   requires either a fundamentally different time horizon (intraday on
   tighter cost paths) or a fundamentally different signal family
   (ML-driven, e.g., AFML triple-barrier meta-labeling).
