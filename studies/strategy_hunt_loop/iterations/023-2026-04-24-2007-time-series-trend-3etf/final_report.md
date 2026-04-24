# Iteration 023 — Final Report

## Verdict

📉 **NEAR_FAIL** (score 28/100, winner_conditions_met=**False**, **Kill #A
TRIGGERED on 3/3 datasets** — the largest cross-dataset Sharpe regression
in the entire hunt loop).

**Headline finding**: Time-series trend-following on a 3-asset basket
{equity, TLT, GLD} with per-asset vol-targeting **fails to beat SPY/QQQ
buy-hold** on every dataset by a wide margin (Δ Sharpe **−0.08 / −0.34
/ −0.34**), and regresses against iter 016 by **−0.43 / −0.59 / −0.58**
— roughly 2× the magnitude of iter 022's previous worst regression. The
"per-asset vol-target escapes σ²_port absorption" thesis is empirically
invalidated: even when the absorption mechanism *is* broken (kill C
clear, cap-hit only 67-75%), the trend signal's whipsaw cost on a small
basket dominates any orthogonal alpha. The hypothesis has been tested
honestly and falsified.

## Headline metrics (top candidate: `ts_trend_L252_skip21_vol10_cap20`)

| dataset | Sharpe (Δ frozen / Δ custom) | CAGR (Δ vs custom) | MDD (Δ vs bench) | gates | Δ Sharpe vs iter 016 |
|---|---|---|---|---|---|
| educational | 0.554 (**−0.126** / **−0.075**) | 8.08% (vs 10.82% custom; **−2.74 pp**) | 48.18% (vs 55.20% bench; **−7.02 pp**) | 5/7 | **−0.427** |
| spy_real    | 0.552 (**−0.348** / **−0.344**) | 7.86% (vs 14.92% custom; **−7.06 pp**) | 48.18% (vs 33.70% bench; **+14.48 pp**) | 5/7 | **−0.588** |
| ndx_real    | 0.610 (**−0.345** / **−0.341**) | 9.37% (vs 19.00% custom; **−9.63 pp**) | 36.31% (vs 35.12% bench; +1.19 pp) | 4/7 | **−0.576** |

Per-leg signal diagnostics (kill #B / #C check):

| dataset | SPY/QQQ long | TLT long | GLD long | any-short bars | cap-hit | turnover/yr |
|---|---|---|---|---|---|---|
| educational | 82.5% | 61.8% | 67.0% | 61.9% | 68.3% | 33.44 |
| spy_real    | 89.6% | 56.4% | 62.7% | 61.3% | 74.7% | 35.24 |
| ndx_real    | 90.8% | 54.6% | 61.2% | 63.1% | 67.8% | 35.10 |

Kill #B (always-long degeneracy) and Kill #C (cap saturation > 80%) are
**clear** — the strategy did exercise short positions ~62% of bars on
at least one leg, and cap binding stayed under 80%. So the geometry
change *did* happen mechanically. Kill #A regression is therefore NOT
explained by a degenerate signal; it's the result of the trend signal
on this universe + window genuinely **subtracting** rather than adding
risk-adjusted return.

Pairwise leg correlations (post-2009):

| dataset | eq · TLT | eq · GLD | TLT · GLD |
|---|---|---|---|
| educational | −0.308 | +0.059 | +0.157 |
| spy_real    | −0.295 | +0.070 | +0.195 |
| ndx_real    | −0.225 | +0.056 | +0.213 |

The basket has the expected cross-asset structure (equity-bond −0.25
to −0.31, equity-gold ~0, bond-gold mildly positive). So the universe
choice was sound; the failure is in the trend-signal layer, not in the
basket geometry.

## Score breakdown (frozen benchmarks, canonical)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **0** | 25 | beats bench+0.10 on 0/3 ds |
| 2 Gates | 15 | 25 | edu 5/7 + spy 5/7 + ndx 4/7; cross-ds threshold bonus +4 (edu meets 5, spy meets 4, ndx meets 4 minimums); G2 DSR fails 3/3, G6 bootstrap fails 3/3, G3 WF fails ndx (4/8) |
| 3 DSR | **0** | 15 | worst p=0.926 (spy_real) — **far worse** than iter 016's 0.226, iter 021's 0.217 |
| 4 CAGR floor | **0** | 15 | all 3 ds fail 0.8 × bench (edu 8.08% < 9.18%; spy 7.86% < 11.98%; ndx 9.37% < 15.35%) |
| 5 MDD ceiling | 10 | 15 | edu 48.18% ≤ 60.14% ✓; spy 48.18% > 38.70% ✗; ndx 36.31% ≤ 40.12% ✓ |
| 6 Robustness | 3 | 5 | 7/9 sub-windows positive (edu 2/3, spy 2/3, ndx 3/3) |
| **total** | **28** | **100+5** | tier: **📉 NEAR_FAIL** |

Custom-benchmark variant (uses iter 023's own SPY/QQQ b&h on the same
windows, slightly lower Sharpes) gives the same 28/100 — the verdict
is invariant to the small bench-Sharpe gap on edu/spy.

## Configuration tested

Single pre-committed cfg `ts_trend_L252_skip21_vol10_cap20` — NO
grid, NO sweep. Cumulative n_trials advance 4273 → 4276 (+3).

```python
CFG = {
    "cfg_id": "ts_trend_L252_skip21_vol10_cap20",
    "signal_lookback": 252,         # Moskowitz-Ooi-Pedersen 2012 canonical
    "signal_skip": 21,              # Jegadeesh-Titman 1993 skip-a-month
    "vol_lookback": 21,             # iter 016 / Carver canonical
    "target_vol_per_asset": 0.10,   # 10 % per leg
    "max_leverage": 2.0,            # match iter 016 cap
    "cost_bps_per_leg": 0.0002,     # 2 bps / unit Δposition / leg
    "rebalance": "daily",
}
```

Datasets:
- educational: SPY+TLT+GLD 2006-01-04 → 2026-04-15 (5101 bars).
- spy_real:    SPY+TLT+GLD 2009-06-26 → 2026-04-15 (4226 bars).
- ndx_real:    QQQ+TLT+GLD 2010-02-16 → 2026-04-15 (4066 bars).

## What worked / what didn't

**Worked**

- **Geometry change DID happen**: the strategy went short on bars (62%
  of bars had at least one short leg); cap binding stayed under 80%
  (kill #C clear). The "per-asset vol-target ≠ portfolio σ²" claim is
  *mechanically* true.
- **Cross-asset structure is sound**: leg correlations match
  literature (eq-bond ~−0.25 to −0.31, eq-gold ~0, bond-gold ~+0.2).
- **G7 cross-lib parity**: numpy reference matches pandas within 0.005
  pp (edu) / 0.12 pp (spy) / 0.09 pp (ndx) — all well under 3 pp gate.
  Engine is clean.
- **MDD on educational improved**: −7 pp vs 55% benchmark MDD, the
  trend-signal correctly de-levered through 2008. (But 2008-only edge
  doesn't translate to spy_real / ndx_real where the window starts
  post-GFC.)
- **Baseline pytest** unaffected: iter 023 tests pass cleanly (13 specs).

**Didn't work**

- **Sharpe regression is uniform and large**: Δ Sharpe −0.08 / −0.34 /
  −0.34 vs custom benchmarks; −0.43 / −0.59 / −0.58 vs iter 016.
  Worst-ever in the hunt loop.
- **DSR p explodes**: 0.89 / 0.93 / 0.90 on the 3 datasets — far worse
  than iter 016's 0.226, iter 021's 0.217, even iter 022's 0.587.
- **CAGR catastrophic**: 8% / 8% / 9% vs SPY / SPY / QQQ at 11% / 15%
  / 19%. Failing CAGR floor on 3/3 datasets.
- **MDD on spy_real worse**: 48% vs SPY's 33.70% (+14.5 pp). Trend
  whipsaw amplifies drawdowns when both the trend signal and the
  underlying are oscillating (2015 oil crash / 2018 vol-mageddon
  / 2022 inflation-shock — three regimes the signal got wrong).
- **G6 bootstrap CI low** is **negative on all 3 datasets** (-0.16 /
  -0.25 / -0.24) — the bootstrap puts most of the resampled-Sharpe
  distribution near or below zero, indicating the realised Sharpe is
  not statistically distinguishable from a noise null on this universe.

### Mechanism: why TSM on a 3-asset basket fails on this window

Three compounding issues, each individually significant:

1. **Whipsaw cost dominates premium on a thin basket**. Turnover is
   ~35 / yr / leg ≈ 105 / yr aggregated × 2 bps = **2.1 % / yr cost
   drag**. iter 016's turnover is ~6 / yr × 2 legs × 2 bps = **0.024 %
   / yr** — two orders of magnitude lower. The 12-1 momentum signal
   on TLT and GLD flips ~12-15 times / year on average; each flip is a
   complete position reversal. The thinner the basket, the more each
   flip dominates the portfolio P&L.

2. **The "Law of Active Management" upper bound is tight on N=3**.
   `[systematic_trading, p.42, ch.2]` — Sharpe ∝ sqrt(N_independent
   bets × IR). Hurst-Ooi-Pedersen 2017 backtested TSM on **67 markets**
   to get the documented +1.0 Sharpe; with N=3 effectively independent
   (ρ ~ 0.06 to −0.31), the upper bound is sqrt(3) / sqrt(67) ≈ 21% of
   the documented edge — i.e. Sharpe uplift bounded above by ~+0.21 vs
   single-asset baseline. Empirically we observed −0.43 to −0.59 vs
   iter 016, so even the optimistic theoretical bound is dwarfed by
   transaction-cost reality.

3. **Post-2009 equity bull suppresses TSM-on-equity edge**. SPY trend
   signal is long 90% of bars (and QQQ 91%). On the equity leg, trend
   ≈ buy-hold but **leveraged differently** (per-asset σ-target gives
   pos_eq ≈ 0.10/0.18 ≈ 0.56 vs iter 016's pos_eq ≈ 0.6 × 1.5 = 0.9).
   So equity exposure is **lower than iter 016 by ~30%**, dragging
   CAGR. The TLT and GLD legs flip more (45 / 39% short) and add
   noise without compensating premium in this window — TLT's worst
   trend regime was 2022 (only +1 year of −1 signal in a 17-year
   sample) and GLD's was 2013-2015 (3 years of bear).

The empirical outcome therefore matches what the theory says when
we apply the correct constraints (small basket, short window, high
turnover): TSM as the primary mechanism is a long-horizon, large-
universe risk premium, and a 3-asset 17-year backtest does not have
enough N-independent-bets × time-T-bars × premium-density to clear
the cost barrier on retail ETF universes.

## Main lesson (for future iterations)

**Time-series trend-following as the PRIMARY mechanism on a ≤ 4-asset
ETF basket cannot beat SPY/QQQ buy-hold in the post-2009 window.**
Documented in literature on 67-market global futures universes
(Hurst-Ooi-Pedersen 2017), the canonical TSM lookback (252-day / skip-21,
Moskowitz-Ooi-Pedersen 2012) does not transport to a small ETF
basket without a corresponding scale-up in N-markets. The basket
diversification factor (sqrt(3) ≈ 1.7×) is overwhelmed by the
transaction-cost footprint of frequent sign-flips on illiquid trend
signals.

**Specific structural extension of the iter 003 dead-end**: iter 003
closed cross-sectional ranking momentum on ≤ 20-asset homogeneous
baskets; iter 023 closes **time-series momentum (the structurally
distinct factor per Goyal-Jegadeesh 2018) on ≤ 4-asset broad-asset-
class baskets** when used as the primary mechanism. Both fail for
overlapping reasons (small N suppresses the diversification factor),
but the iter 023 finding rules out a separate dead-end branch.

The "per-asset vol-target escapes σ²_port absorption" thesis is
**partially validated mechanically** (cap kill clear, signal kill
clear) but **invalidated empirically** (the geometric change does not
translate to alpha because cost > premium at this scale). The path
forward MUST find a mechanism that:
1. Has lower turnover than 35 / yr / leg, OR
2. Has more independent bets than 3, OR
3. Captures a premium that does not require frequent re-positioning.

## Structural dead-ends discovered

**Time-series trend-following on ≤ 4-asset ETF baskets as the primary
mechanism** — Sharpe regresses by 0.43-0.59 vs iter 016 base on all 3
datasets; turnover of ~35/yr/leg × cost overwhelms basket diversification
(sqrt(3) ~1.7×) on retail ETF universes.

Scope of closure:
- TSM (any lookback in {3-24 months}, any skip in {0-2 months}) on any
  ≤ 4-asset broad-asset-class ETF basket {equity, bond, gold,
  commodity} as the primary portfolio mechanism (no carry / no
  blend overlay).
- Per-asset vol-targeting in {5%, 10%, 15%} per leg with leverage cap
  in {1.5×, 2.0×, 2.5×}.
- Daily / weekly rebalance (weekly will be worse — see iter 011).

Does NOT close:
- TSM as overlay-style **gate** on iter 016 (already closed by iter
  007).
- TSM on a genuinely larger basket (≥ 20 markets, e.g. global futures).
  — but this requires data outside the current Tiingo cache.
- TSM with explicit cost mitigation (slow signals: EWMAC 64/256, exit
  thresholds, holding-period constraint to lower turnover).
- Cross-asset CARRY-based portfolios (linear in IR / yield differential,
  no σ-feedback, uncorrelated with TSM premium per Asness-Moskowitz-
  Pedersen 2013).

## Citations used

Primary:
- `[algo_trading_chan, p.164, ch.6]` — Moskowitz-Yao-Pedersen 2012 /
  12-month TSM lookback. (This citation grounds the canonical 252-day
  formation; the iteration's mechanism faithfully reproduces it.)
- `[systematic_trading, p.40, ch.2]` — vol standardisation primitive.
- `[systematic_trading, p.42, ch.2]` — Law of Active Management
  (Sharpe ∝ sqrt(N independent bets)). The decisive constraint
  empirically.
- `[systematic_trading, p.159-160, ch.10]` — vol-scalar per
  instrument.
- `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 leverage cap.
- `[stocks_on_the_move, p.58, p.60]` — Levy 1967 / Jegadeesh-Titman
  1993 anchor.
- `[risk_parity, ch.5-7]` — multi-asset risk-parity framing.
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag discipline.

Papers:
- Moskowitz, Ooi & Pedersen (2012). "Time Series Momentum." *JFE*
  104(2), 228-250.
- Hurst, Ooi & Pedersen (2017). "A Century of Evidence on Trend-
  Following Investing." *JPM* 44(1), 15-29. — Source of the empirical
  upper bound that we did not approach.
- Baltas & Kosowski (2020). "Demystifying Time-Series Momentum
  Strategies: Volatility Estimators, Trading Rules and Pairwise
  Correlations." *Management Science* 66(10), 4567-4596. — Predicts
  per-asset vs portfolio vol-target makes little difference on small
  baskets, consistent with our finding.
- Goyal & Jegadeesh (2018). "Cross-Sectional and Time-Series Tests of
  Return Predictability: What is the Difference?" *RFS* 31(5),
  1784-1824.
- Asness, Moskowitz & Pedersen (2013). "Value and Momentum
  Everywhere." *JF* 68(3), 929-985 — relevant for forward direction.

## Next iteration suggestions

The TSM-as-primary-mechanism on a small basket is now closed. Three
structurally different forward paths remain:

1. **Option C — Cross-asset CARRY (FX / bond curve / commodity term)
   as primary mechanism**. Carry is **linear in yield differentials**,
   **NOT a function of variance**, and historically uncorrelated with
   TSM per Asness-Moskowitz-Pedersen 2013. Turnover is much lower
   (~3-6 / yr typical) so cost drag is manageable. **Data limitation**:
   FX, bond curve, commodity term-structure require external data
   feeds (UUP, DBC, USO+commodity-curve). Could potentially synthesise
   bond-curve carry from TLT + IEF spread (long bond yield − intermediate
   yield via price). Highest-priority forward direction.

2. **Option Z — Slow-signal trend with exit thresholds (lower turnover)**.
   Same TSM mechanism but with EWMAC slow variants (64/256-day, per
   `[systematic_trading, p.118-119, ch.7] + p.282-284 (appendix B)`)
   and a 5-15% exit threshold to suppress whipsaw. Turnover would drop
   from ~35/yr to ~5-8/yr per leg. Risk: if iter 023's diagnosis is
   correct (basket size ceiling, not lookback choice), slow signals
   won't fix the problem either. Worth one iteration to verify before
   closing the family entirely.

3. **Option V — Volatility-risk-premium harvest as primary
   mechanism**. iter 020/021 added options as overlays on iter 016;
   here build the WHOLE portfolio around short-puts / put-credit-spreads
   + cash collateral + Treasury yield. Premium is real and documented
   (Bondarenko 2014 ~+3-4 %/yr); no σ-feedback issue because vol-target
   isn't applied at portfolio level. Turnover is monthly → ~12 /yr,
   manageable. Risk: 2008-style tail events; need explicit hedge.

**NOT recommended**:
- Smaller-basket TSM variants (sub-2-asset, single-asset) — already
  closed by iter 004/005.
- Larger-basket TSM via concatenated sector ETFs — closed by iter 003
  (cross-sectional ranking on small homogeneous baskets fails).
- TSM with longer / shorter lookback variants on this same 3-asset
  basket — the lookback was already chosen at the literature-canonical
  optimum; alternative lookbacks would only re-test points the
  Hurst-Ooi-Pedersen 2017 paper covers.
