# Iteration 024 — Final Report

## Verdict

📉 **NEAR_FAIL — score 30/100**, winner_conditions_met = False, hold_time_gate
= PASS (mean_hold 4.91d ∈ short_swing [2, 10]), is_winner = False.

**5 of 6 pre-committed kill criteria fired**:
- ✗ Kill #1 — primary basket Sh = +0.2022 < 0.30 (FIRED)
- ✗ Kill #2 — basket Sh − iter003 Sh = −0.0978 < +0.05 (FIRED)
- ✗ Kill #3 — IC-6 rolling-60d ρ vs iter003 = **94.9%** > 80% threshold (FIRED HARD)
- ✗ Kill #4 — G6 bootstrap CI low = −0.454 ≤ 0 (FIRED)
- ✗ Kill #5 — DSR p = 0.860 > 0.30 (FIRED)
- ✓ Kill #3b — IC-6 vs iter011 rolling = 27.4% < 30% (NOT fired; basket
  doesn't ride vol-regime — different mechanism than GS-22)

**Cross-cluster diversification via gold-mining ETF (GDX) does NOT break
the GS-23 ceiling.** Basket Sharpe is *worse* than iter 003 alone (+0.20
vs +0.30), and the IC-6 rolling correlation only drops 1.9 pp (94.9% vs
iter 023's 96.8%) — far from the 20+ pp drop needed to validate cross-
cluster diversification.

## Headline metrics (NET of Pepperstone CFD costs per leg)

| dataset | Sharpe (Δ vs basket bench) | CAGR (vs bench) | MDD (vs bench) | gates | mean hold (basket) |
|---|---|---|---|---|---|
| gld_gdx_basket_long (~19.9y) PRIMARY | **+0.2022** (Δ −0.267) | +0.852% (vs 9.15%) | **13.94%** (vs 61.68%) | 4/7 | 4.91d |
| xau_gdx_basket (~6.3y) CORROBORATING | **−0.1064** (Δ −1.071) | −0.448% (vs 21.44%) | 10.33% (vs 31.64%) | 3/7 | 4.70d |

Reference (single-asset iter 003 RSI(2)+SMA(200) on gld_long): Sharpe +0.30,
mean_hold ~3-4d. The basket aggregation drags Sharpe DOWN by 0.10.

Per-leg trade counts (PRIMARY):
- gold leg: 63 trades over ~19.9y (~3.2/yr)
- GDX leg: 45 trades over ~19.9y (~2.3/yr) — 71% of gold leg's count
- Basket trades (any leg in): 80 (some non-overlap exists, but most days both legs concur or only the gold leg fires)

Per-leg cost totals on PRIMARY (~19.9y):
- gold spread: $0.030 cumulative ≈ 30 bps total ÷ 63 trades = ~5 bps avg/trade RT
- gdx spread:  $0.022 cumulative ≈ 22 bps total ÷ 45 trades = ~5 bps avg/trade RT
- gold swap:   $0.020 cumulative drag (negative)
- gdx swap:    $0.013 cumulative drag (negative)

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 0 | 25 | primary Sh +0.20 fails benchmark+0.10 (=0.57); 0/1 corroborating positive |
| 2 Gates | 15 | 25 | primary 4/7 (meets v2 threshold for 1.7y-class); corroborating 3/7 (G6+G2 strict-fail); legacy cross-bonus N/A (not legacy datasets) |
| 3 DSR | 0 | 15 | primary p = 0.860 (cumulative n_trials=24); far from <0.05 |
| 4 CAGR floor | 0 | 15 | primary CAGR 0.85% < 0.8 × 9.15% = 7.32% floor |
| 5 MDD ceiling | 15 | 15 | primary MDD 13.94% < 61.68% + 5pp = 66.68% ceiling — easily passes (basket is selective) |
| 6 Robustness bonus | 0 | 5 | not computed (no rolling-window subset analysis) |
| **total** | **30** | **100+5** | tier: **NEAR_FAIL** |
| (hold-time gate) | PASS | — | mean basket hold 4.91d ∈ short_swing [2, 10] |

## Configuration tested

```yaml
config_id: "cross_cluster_rsi2_sma200_gld60_gdx40_basket"
universe: gold_complex
broker_track: pepperstone_cfd
hold_time_track: short_swing
declared_primary: gld_gdx_basket_long
declared_corroborating: [xau_gdx_basket]
weights: {gold: 0.60, gdx: 0.40}   # GLD/XAU >= 40%
spreads_rt_bps: {gold: 8.0, gdx: 12.0}   # gold = Pepperstone XAUUSD baseline; gdx = US-equity CFD typical
rsi_period: 2
rsi_threshold: 5.0
sma_period: 5         # exit on close > SMA(5)
sma_trend_period: 200 # SMA(200) regime gate per Connors
swap_long_bps_per_night: -1.0
weekend_swap_mult: 3.0
long_only_per_asset: true
```

Single pre-committed config (IC-8 mandate). Cumulative DSR n_trials = 24.

## What worked / what didn't

**What worked**:
- Engine reuse from iter 023 was clean (~3 lines of substitutions plus
  a fresh GDX Tiingo fetch). All 7 TDD tests passed, cross-lib G7 parity
  identical (cagr_diff_pp = 0).
- Hold-time match (4.91d basket mean hold ∈ short_swing) — declaration
  + observation aligned cleanly. No track mismatch penalty.
- MDD reduction is real: basket MDD 13.94% vs basket-bh MDD 61.68% (−48
  pp) on PRIMARY. Selective entry via RSI+SMA(200) avoids prolonged
  drawdown windows. This is a portfolio-construction property, NOT a
  Sharpe edge.
- IC-6 vs iter011 rolling = 27.4% < 30% threshold — basket position
  vector is **structurally different from vol-regime signal**. So GS-22
  family closure doesn't apply. The basket has its own (failing) mechanism.

**What didn't**:
- **Sharpe lift vs iter003 = −0.098** — basket aggregation actively
  degrades performance. GDX is *more* volatile than GLD (~2x miner
  equity beta on gold price), so when GDX RSI(2) fires, the entry is
  riskier; SMA(5) exit is too short to ride a recovery. The 40% GDX
  allocation drags Sharpe by adding noise without adding edge.
- **IC-6 rolling vs iter003 = 94.9%** — only 1.9 pp lower than iter 023's
  GLD+SLV (96.8%). The cross-cluster hypothesis predicted ≤ 80% — falsified.
  GDX equity beta to S&P 500 (~0.45) is real, but the *dominant* driver
  for GDX is gold-price (miner cash-flows are levered to gold). When gold
  dips, GDX dips more; RSI(2) on GDX fires on the same days as on GLD.
- **G6 bootstrap CI low −0.454** — Sharpe is not significantly different
  from zero. With ~5 000 daily bars and ~80 trades, the empirical Sharpe
  +0.20 is well within sampling noise of a true zero.
- **DSR p = 0.860** — far from <0.05 threshold. The deflated Sharpe
  ratio at n_trials=24 needs Sharpe > ~0.65 to clear; +0.20 is not even
  close.
- **G3 walk-forward FAIL** on both datasets — block-level Sharpes are
  inconsistent; some windows bleed.
- **G5 FWD post-2022 fail on corroborating** (xau_gdx_basket fwd_Sh =
  −0.07) — the basket is actively losing in the recent regime.

## Main lesson (for future iterations)

**GDX is not a cross-cluster asset to GLD; it is gold-derivative.** The
documented S&P 500 ρ ~0.45 of GDX is real but *secondary*; the dominant
factor exposure is GOLD PRICE (miner cash-flows are levered ~2× on gold).
Consequently:

1. RSI(2)+SMA(200) MR signal on GDX fires on essentially the same days
   as on GLD (gold-price-driven dips trigger both).
2. Basket aggregation can reduce MDD (selective entry leaves more days
   flat) but does not produce a Sharpe edge over iter 003 alone.
3. **Within "gold-complex" universe, ALL precious-metals-adjacent assets
   (silver/SLV, miners/GDX, junior miners/GDXJ, royalty companies/RGLD,
   platinum-group/PPLT) are structurally bound to the same gold-stress
   macro clock.** Iter 023 closed within-PM (GLD+SLV); iter 024 closes
   PM-adjacent equity (GLD+GDX). The remaining direction is **truly
   orthogonal asset clusters**: BTC (digital scarcity), TLT/LQD (duration
   + inflation), or SPY/QQQ (broad equities — but those have negative or
   zero gold loading; basket tilts away from gold).

GS-23 + GS-24 jointly close the **"gold-complex universe" extension** as
a productive direction. The sister-loop "every winner was multi-asset"
lesson must be re-interpreted: cross-asset diversification needs
**genuinely orthogonal factor clusters** (not "gold + gold-derivatives").

## Structural dead-ends discovered

**GS-24 (this iter)** — Cross-cluster basket extension via gold-mining
ETF (GDX): IC-6 rolling-60d ρ vs iter003 = 94.9% (only 1.9 pp better
than within-PM iter 023's 96.8%). Basket Sharpe +0.20 is BELOW iter003
single-asset +0.30 (lift = −0.098). Closes:
- GLD+GDX 60/40 RSI(2)+SMA(200) per-leg basket
- Generalizes to all "gold-derivative equity" basket extensions:
  GLD+GDXJ (junior miners; even higher gold beta), GLD+RGLD (royalty
  company; nearly pure gold exposure), GLD+SIL/SILJ (silver miners),
  GLD+PPLT (platinum; PGM-correlated to gold)
- Does NOT close: cross-CLUSTER baskets where the 2nd asset has truly
  orthogonal driver (BTC, TLT, SPY/QQQ-not-miners), CME futures A2,
  DCOT producer-merchant mirror, 25Δ option RR skew

Pattern joins GS-23: "within gold complex, basket extensions of
single-asset signals fail because all gold-complex assets ride the same
gold-stress macro clock at MR-trigger frequency."

## Citations used

- `[risk_parity, ch.7]` — multi-asset basket weighting (PRIMARY citation;
  thesis predicted heterogeneous risk drivers should diversify; GDX
  was hypothesized as PM-adjacent equity with stock-beta — empirically
  the gold-loading dominates, falsifying the cross-cluster hypothesis
  for this asset)
- `[short_term_trading_strategies, p.105-118]` — Connors RSI(2)<5 +
  SMA(200) trend-filter signal; same as iter 003/023 per leg
- `[ilmanen_expected_returns, ch.10]` — gold complex factor exposures;
  Ilmanen actually notes that mining stocks correlate ~0.7-0.8 with
  spot gold and only ~0.3-0.4 with broad equities, **consistent with
  iter 024's empirical finding that GDX gold-loading dominates**
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 24
- `[advances_fin_ml, p.196-202]` — bootstrap 99.9% CI low > 0 gate
- `[advances_fin_ml, p.31-34]` — cross-lib parity (G7 passed at 0.000 pp diff)
- IC-6 (sister loop iter 014/019) — rolling-correlation pre-val mandate
- GS-23 (iter 023) — within-precious-metals basket extension closure
  (motivated this cross-cluster test, which now extends GS-23 to GS-24)

## Next iteration suggestions

The "gold-complex universe" cross-cluster path closed by GS-24 reshapes
priorities. Two directions remain genuinely structurally novel:

1. **PRIORITY 1 — GLD + BTCUSD 60/40 RSI(2)+SMA(200) basket
   (PROMOTED)** — BTC is the genuinely orthogonal "digital scarcity"
   counterpart to gold. BTCUSD cached (2014+, ~12y). Expected position-
   vector overlap with iter 003 << 50% rolling. NO Tiingo fetch needed.
   Same engine. `[risk_parity, ch.7]` + `[crypto_paper_secondary]`. **If
   GLD+BTC IC-6 rolling drops below 60%, this would be the first
   real cross-cluster validation in 24 iters.**
2. **PRIORITY 2 — GLD + TLT 60/40 RSI(2) basket** — bonds add duration
   + inflation drivers. TLT cached. Bond trend regimes are slower;
   may need adjusted SMA window per leg (gold leg SMA(200), TLT leg
   SMA(60) maybe, given different vol). `[risk_parity, ch.7]`.
3. **PRIORITY 3 — DCOT producer-merchant long-on-extreme-shorting**
   (RETAINED from iter 023 carry-over) — different family entirely
   (positioning, not basket). Data cached. `[trading_systems_methods,
   p.640]`.
4. **PRIORITY 4 — CME futures track A2 cost-path re-test** — re-run
   the cost-dominated intraday MR (iter 007 z-MR died at 8 bps RT)
   at futures' 1-2 bps RT. Genuinely different cost regime.
5. **(LOWER) Concede loop closure** if priorities 1-4 also flat-line.
   PCBO/DSR with n_trials=24+ requires standalone Sh > 0.65 OR an IC-7
   pair/triplet with strong-enough standalone Sharpes; none exhibited
   in 24 iterations across single-asset XAU + within-PM basket + PM-
   adjacent miner basket universes.

The remaining cross-cluster directions (BTC, bonds, equities-not-miners)
are the last unexplored test of the cross-cluster hypothesis. If those
also fail, the loop's strategic conclusion will be: **gold's persistent
drift is too steep for any selective-entry basket-aggregated MR signal
to bridge** — single-asset standalone (iter 003 +0.30) is the family
ceiling, and only a genuinely heterogeneous additive new stream (out of
gold-complex universe entirely, e.g., a non-gold strategy combined via
IC-7) could clear DSR.
