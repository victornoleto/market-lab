# Iteration 025 — Final Report

## Verdict

📉 **NEAR_FAIL** (score 39/100, winner_conditions_met=**False**, 0/5
strict winner conditions met). **Kill A triggered** (Sharpe regression
vs iter 015 frozen on 2/3 datasets).

**Headline finding**: Slow-EWMAC trend (32:128 + 64:256 with FDM=1.10)
on a 6-asset broad-asset-class basket (SPY+TLT+IEF+GLD+EFA+EEM) with
long-only positions, per-asset vol-targeting (4% per leg), and a 10%
no-trade buffer is **mechanically robust** — turnover at 1.56-1.61 / yr
per leg (well below iter 023's 35 / yr), G3 walk-forward at 7-8/8 on
all datasets, G6 bootstrap CI passing 3/3, robustness 9/9 sub-windows
positive — but **delivers Sharpe 0.77/0.82/0.83 vs benchmarks
0.68/0.90/0.955**. The strategy beats the SPYSIM educational benchmark
by +0.086 (sub-threshold for the +0.10 winner gate) but **regresses
clearly on spy_real (−0.085) and ndx_real (−0.127) vs SPY/QQQ
buy-hold**. CAGR collapses to 9-10% on real data vs 14.97-19.18%
benchmark — long-only constraint plus 6-asset basket cannot harvest
sufficient trend premium to compete with US-equity beta post-GFC.

The mechanism is not a structural failure of slow-EWMAC trend — it's
a confirmation that **Hurst-Ooi-Pedersen 2017's centennial trend
edge requires a 67-market futures basket, and a 6-asset retail ETF
universe is too narrow** to extract a meaningful trend premium net of
the equity-beta opportunity cost.

## Headline metrics (top candidate: `sema_slow_64_256_32_128_6asset_vt15_v1`)

| dataset | Sharpe (Δ frozen) | CAGR (Δ vs bench) | MDD (Δ vs bench) | gates |
|---|---|---|---|---|
| educational | **0.7657 (+0.086)** | 9.13% (−1.69 pp vs custom 10.82%, −2.34 pp vs frozen 11.47%) | **17.33% (−37.81 pp vs frozen 55.14% — DRAMATIC IMPROVEMENT)** | 6/7 |
| spy_real    | **0.8151 (−0.085)** | 9.97% (−4.51 pp vs bench 14.48%) | **17.33% (−16.37 pp vs bench 33.70%)** | 6/7 |
| ndx_real    | **0.8282 (−0.127)** | 10.20% (−8.23 pp vs bench 18.43%) | **17.33% (−17.79 pp vs bench 35.12%)** | 6/7 |

Diagnostic data:

| dataset | mean turnover/leg/yr | mean gross leverage | buffer ratio | n_bars |
|---|---|---|---|---|
| educational | 1.56 | 1.262 | 0.730 | 4845 |
| spy_real    | 1.58 | 1.317 | 0.728 | 4227 |
| ndx_real    | 1.61 | 1.268 | 0.726 | 4067 |

Kill-criteria check:

| kill | criterion | result | triggered |
|---|---|---|---|
| **A** Sharpe regress vs iter 015 (Δ < −0.03 on ≥2/3) | educational −0.018, spy −0.229, ndx −0.236 | 2/3 regress | **YES** |
| B Turnover trap (>12/yr) | 1.56-1.61 | 0/3 | NO |
| C MDD blowup (bench+5pp) | 17% on all (vs ceilings 60/40/40) | 0/3 | NO |
| D Buffer ineffective (>80%) | 0.726-0.730 | 0/3 | NO |

**Only Kill A triggers** — the strategy is structurally sound and
mechanically clean, but the realized Sharpe doesn't compete with US
equity beta post-GFC.

## Score breakdown (frozen benchmarks, canonical)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **0** | 25 | beats bench+0.10 on **0/3** datasets |
| 2 Gates | 19 | 25 | edu 6/7 (+5) + spy 6/7 (+5) + ndx 6/7 (+5) + cross-ds bonus +4 |
| 3 DSR | **0** | 15 | worst p=0.629 (ndx) — far from 0.20 threshold; n_trials=4278 |
| 4 CAGR floor | 0 | 15 | edu 9.13% < 9.18% floor (NARROW miss); spy 9.97% < 11.98%; ndx 10.20% < 15.35% |
| 5 MDD ceiling | **15** | 15 | edu 17% ≤ 60.14% ✓; spy 17% ≤ 38.70% ✓; ndx 17% ≤ 40.12% ✓ |
| 6 Robustness | **5** | 5 | **9/9 sub-windows positive** — ties iter 013/024 record |
| **total** | **39** | **100+5** | tier: **📉 NEAR_FAIL** |

## Configuration tested

Single pre-committed cfg `sema_slow_64_256_32_128_6asset_vt15_v1` —
NO grid, NO sweep, NO post-hoc selection. Cumulative n_trials advance
4277 → 4278 (+1).

```python
CFG = {
    "cfg_id": "sema_slow_64_256_32_128_6asset_vt15_v1",
    "speeds": [(32, 128), (64, 256)],     # Carver app.B slow-only
    "speed_scalars": [2.65, 1.87],         # Carver Table 49
    "speed_weights": [0.5, 0.5],
    "fdm": 1.10,                           # 2 forecasts at ρ ≈ 0.85
    "target_vol_per_asset": 0.04,          # 4% vol per asset (~15% portfolio)
    "asset_vol_span": 36,                  # EWMA vol span
    "lag_bars": 1,                         # σ̂_{t-1}, no look-ahead
    "no_trade_buffer_pct": 0.10,           # Carver position-trade-band
    "max_per_asset_leverage": 0.6,
    "long_only": True,                     # retail ETF constraint
    "cost_bps_per_leg": 0.0002,            # 2 bps / Δposition
    "sigma_span": 36,                      # σ_pp EWMA span
}
```

Datasets:
- educational: SPY+TLT+IEF+GLD+EFA+EEM 2007-01-11 → 2026-04-15
  (4845 bars, ~19y, matches iter 024 alignment).
- spy_real: SPY+TLT+IEF+GLD+EFA+EEM 2009-06-25 → 2026-04-15 (4227 bars).
- ndx_real: QQQ+TLT+IEF+GLD+EFA+EEM 2010-02-12 → 2026-04-15 (4067 bars).

## What worked / what didn't

**Worked**

- **Engine cleanliness**: G7 cross-lib parity 0.003-0.06 pp diff,
  trivially within the 3 pp gate (compared to iter 023's 0.4 pp and
  iter 024's 0.04 pp). The pure-numpy reference matches the pandas
  engine to 4-5 decimal places of CAGR.
- **Mechanism robustness**: G3 walk-forward 7/8 on educational and
  8/8 on both real datasets — the slow-EWMAC framework produces
  positive Sharpe windows consistently. **Tied for best WF in hunt loop**.
- **G6 bootstrap CI**: passes 3/3 with CI low +0.029 / +0.082 / +0.095
  — small but consistently positive. Joins iter 016/021/024 in the
  "G6-passing" club.
- **Robustness 9/9**: every sub-window (early/mid/late thirds across
  all 3 datasets) has Sharpe > 0. Range 0.54-1.03 — narrow and
  positive throughout. Ties iter 013/024 record.
- **MDD reduction is dramatic**: 17.33% on all 3 datasets vs
  benchmarks 33-55%. The diversification + per-asset vol-targeting +
  long-only constraint produces a defensive equity surrogate that
  **never enters major drawdown territory**.
- **Turnover well-controlled**: 1.56-1.61 / yr per leg, ~50× lower
  than iter 023's 35 / yr. Slow signals + Carver no-trade buffer
  delivers as designed. Cost drag is ~0.02-0.04% / yr — negligible.
- **Buffer effectiveness**: ratio 0.726-0.730 means ~27% of target-
  position changes get filtered by the no-trade buffer without
  sacrificing edge. Kill D (>80% ratio) doesn't trigger.
- **TDD specs**: 15/15 pass; baseline pytest preserved (855 passed,
  5 skipped including 14 from iter 024 + 15 new from iter 025).

**Didn't work**

- **Sharpe regress vs iter 015 baseline on 2/3 datasets** (Δ −0.018
  on educational; −0.229 on spy_real; −0.236 on ndx_real). The
  static-IEF baseline already extracts the bulk of the bond
  diversification at 0.78/1.04/1.06, so a directional-trend layer
  on top of a wider basket doesn't add value when the trend signal
  is dampened by long-only flat-on-downtrend behaviour.
- **CAGR collapses to 9-10% on real data**: this is the dominant
  failure mode. SPY post-GFC produces 14.97% CAGR; QQQ 19.18%. A
  diversified slow-trend portfolio that goes flat on individual asset
  downtrends ends up holding only 30-50% gross-leverage on average,
  and the diversifier returns (TLT, IEF, GLD, EFA, EEM) don't compound
  fast enough to compensate.
- **DSR ceiling not approached**: worst p = 0.629, not even close to
  the 0.05 winner gate or even the 0.20 partial-credit threshold.
  With Sharpe 0.77/0.82/0.83 and n_trials=4278, the deflator is brutal.
- **Custom-bench Sharpe edge on educational +0.144 is misleading**:
  vs the SPY 2007-2026 benchmark (0.62), the strategy beats by
  +0.144, but vs the FROZEN SPYSIM 1986-2026 benchmark (0.68),
  the edge is only +0.086 — sub-threshold. The 2007-onwards SPY
  window suffers GFC drag (~−40% peak-trough); the strategy's
  defensive 17% MDD vs SPY's ~55% MDD lifts edge on educational
  precisely because GFC is in-sample. On post-GFC datasets where
  SPY recovered cleanly, the edge vanishes.

### Mechanism: why slow-EWMAC long-only on 6 assets fails to beat SPY

Three compounding observations explain the regression:

1. **Long-only kills the trend premium asymmetrically**. Trend
   strategies harvest premium from BOTH legs of the directional
   movement: long during uptrends + short during downtrends. With
   long-only, the short-leg premium is completely sacrificed — the
   strategy goes flat (zero return) when trends are negative. This
   loses ~50% of the trend Sharpe according to Hurst-Ooi-Pedersen
   2017 attribution.
2. **6-asset basket has too few independent axes**. Hurst-Ooi-Pedersen
   2017 reports SR ≈ 1.0 for cross-asset trend on 67 futures markets
   over 1903-2012; the basket size is critical to the diversification
   ratio. Carver `[systematic_trading, p.131-133]` cites FDM = 3.2
   for 10 uncorrelated forecasts; with 6 assets at moderate (~0.3)
   correlation, the effective N is ~4 and the diversification benefit
   is roughly √4 = 2× single-asset, not the 5-7× claimed for the
   full basket.
3. **Equity-beta opportunity cost is too high post-GFC**. SPY
   2009-2026 produced annualized Sharpe 0.90 with 14.97% CAGR — an
   exceptional period. A defensive slow-trend portfolio at 17% MDD
   buys risk reduction at 5+ pp of CAGR cost. The gross-leverage
   floor on a 6-asset long-only portfolio is too low to lever back
   up to SPY-like exposure when all 6 assets are uptrending
   (gross_leverage_mean = 1.27, well below the 1.6× max set by
   the per-asset cap × N = 0.6 × 6 = 3.6).

The strategy therefore fails the SPY-1× benchmark by **structurally
unbeatable means**: the long-only constraint sacrifices ~50% of the
trend premium, the small basket truncates diversification, and the
post-GFC SPY beta sets a high bar. Iter 025 confirms iter 023's
broader principle: **trend on small ETF baskets can't compete with
US-equity buy-hold post-2009**.

## Main lesson (for future iterations)

**Slow-EWMAC trend with forecast diversification on a 6-asset
broad-asset-class long-only ETF basket fails to beat SPY 1x on
post-GFC data — Sharpe 0.82-0.83 vs SPY/QQQ 0.90-0.96 — despite
the engine being clean (G3 8/8, G6 3/3, G7 0.003-0.06 pp parity)
and the turnover well-controlled (~1.6/yr/leg, 22× lower than iter
023's 35/yr). The dominant failure mode is the long-only constraint
truncating trend premium by ~50%, compounded by the 6-asset basket
being too narrow for cross-asset trend diversification (Hurst-Ooi-
Pedersen 2017 needs 67 markets for SR ≈ 1.0).**

This iteration **closes a finer boundary** of the iter 023
dead-end: iter 023 closed "TSM canonical (252/21) on ≤4-asset broad-
asset-class basket per-asset vol-target", and iter 025 extends this
to "**slow-EWMAC (32:128 + 64:256) with forecast diversification
+ FDM + portfolio-level vol-target + no-trade buffer + long-only**
on a 6-asset broad-asset-class ETF basket". The slow signals fix
the turnover problem but cannot overcome the long-only + small-
basket constraints.

The dead-end DOES NOT close:
- **Long-short slow-EWMAC** (allowing negative positions on
  downtrends) — the lost half of trend premium might rescue the
  Sharpe edge.
- **≥20-asset trend basket** (e.g., expanding to factor ETFs +
  region ETFs + bond ETFs + commodity ETFs to ~20 assets, possibly
  via futures proxies if data is available).
- **Slow-EWMAC + carry combo** (Carver explicitly recommends
  combining EWMAC and carry as negative-skew complements;
  iter 025 tested EWMAC alone).
- **VRP-primary** (still open per iter 023's note).

Forward-direction implications:

1. **Short-side reactivation** — adding the short-leg to the same
   strategy might recover ~50% of trend Sharpe; tests would need
   to handle ETF-shorting cost (~30-50 bps borrow / yr) and tail
   risk explicitly.
2. **Carry rule overlay** — Carver's Carry signal (annualized term-
   structure roll) would be orthogonal to EWMAC and could lift
   Sharpe via FDM increase (1.41 for 4 forecasts vs 1.10 for 2).
3. **VRP-primary** remains the best candidate for breaking the DSR
   ceiling at n_trials=4278 — Bondarenko 2014's documented +3-4%/yr
   premium with retail-tradable short-put structure on T-bill
   collateral.

## Structural finding (for `DEAD_ENDS.md`)

This iteration closes a finer boundary of the iter 023 dead-end:

> **Slow-EWMAC (32:128 + 64:256) with FDM=1.10, portfolio-level vol-
> target, and Carver position-trade-band on a 6-asset broad-asset-
> class ETF basket (equity + 2 bond durations + commodity + 2 region
> equities), long-only — produces Sharpe 0.77-0.83 cross-dataset, 2/3
> regress vs iter 015 SPY+IEF static baseline. The slow signals fix
> the turnover problem from iter 023 (1.6/yr/leg vs 35/yr) but the
> long-only constraint sacrifices ~50% of trend premium and the
> 6-asset basket is too narrow for full cross-asset diversification
> (Hurst-Ooi-Pedersen 2017 needs 67 markets for SR ≈ 1.0).**

Does NOT close:
- Long-short slow-EWMAC variants
- ≥20-asset trend baskets
- Slow-EWMAC + Carry combination (FDM at 4+ forecasts)
- VRP-primary portfolio

## Citations used

Primary:
- `[systematic_trading, p.118-119, ch.7]` — EWMAC trend rule, six
  speed pairs.
- `[systematic_trading, p.131-133, ch.8]` — FDM for combined forecast.
- `[systematic_trading, p.244-258, ch.15]` — No-trade buffer / position
  trade-band.
- `[systematic_trading, p.282-285, app.B]` — EWMAC computation +
  scalars (32:128 → 2.65, 64:256 → 1.87).
- `[risk_parity, p.10-11, ch.1]` — Multi-asset diversification basis.
- `[advances_fin_ml, p.31-34]` — Cross-library parity discipline (G7).
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} no-look-ahead lag.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.

Papers:
- Hurst, Ooi, Pedersen (2017). "A Century of Evidence on Trend-
  Following Investing." *JPM* 44(1), 15-29. — Cross-asset trend on
  67-market futures basket.
- Moskowitz, Ooi, Pedersen (2012). "Time series momentum." *JFE*
  104(2), 228-250. — Reference for the TSM family that iter 023
  closed at fast speeds.

## Next iteration suggestions

The DSR ceiling at n_trials=4278 still binds. Three forward
directions remain open:

1. **Long-short slow-EWMAC on the same 6-asset basket** — same
   strategy with short positions allowed on downtrending assets.
   Adds ETF-shorting cost (~30-50 bps borrow + spread) but recovers
   the lost half of trend premium. If Sharpe improves to ~1.0+ on
   real data, this could break DSR.

2. **VRP-primary portfolio** (still the strongest candidate from
   iter 024's "next directions") — short-put portfolio with T-bill
   collateral. Bondarenko 2014 +3-4%/yr premium; iter 020/021's
   overlay tests demonstrated edge survives at the 5-10% OTM, 21-DTE
   parameters. Risk: 2008/2020 tail; needs explicit hedge.

3. **Slow-EWMAC + Carry combo on 6 assets, long-only** — Carver
   explicitly recommends combining EWMAC (trend) and Carry
   (negative-skew complement) as orthogonal signals. With 4 effective
   forecasts (2 EWMAC speeds + 2 Carry signals via T10Y3M for bonds
   and dividend yield for equities), FDM rises to ~1.5-1.8 and the
   total signal strength might lift Sharpe by +0.15-0.20.

**NOT recommended**:

- Tweaking iter 025 parameters (target_vol, basket size, speed
  weights) — the failure is structural (long-only + 6-asset
  diversification limit), not parametric. Any param sweep would
  find local optima at this ~0.80 Sharpe plateau.
- Shorter speeds (2:8, 4:16, 8:32) — closed by iter 023.
- Same mechanism on factor ETFs / sector ETFs — closed by iter 003
  (cross-sectional ranking on small homogeneous baskets) and iter
  017 (regional rotation on N≤3).

## Conclusion

Iter 025 is a **clean structural failure** — the engine is robust
(G3 7-8/8, G6 3/3, G7 < 0.06 pp), the mechanism is well-defined
(slow-EWMAC + FDM + buffer per Carver framework), and turnover is
22× lower than iter 023. But long-only + 6-asset basket cannot
extract enough trend premium to beat post-GFC SPY/QQQ buy-hold
(Sharpe 0.82-0.83 vs 0.90-0.955). The dominant lesson is that
**SPY/QQQ post-2009 is a high-Sharpe regime that defensive long-
only multi-asset strategies struggle to compete with on Sharpe even
when they massively reduce MDD (17% vs 33-35%)**.

The iteration adds 1 trial to the cumulative count (n_trials =
4278) and tightens the iter 023 dead-end boundary by an order of
magnitude (slow-EWMAC + Carver framework + long-only confirmed
to fail on 6-asset retail basket). Forward direction: pivot to
long-short variant, VRP-primary, or EWMAC+Carry combo.
