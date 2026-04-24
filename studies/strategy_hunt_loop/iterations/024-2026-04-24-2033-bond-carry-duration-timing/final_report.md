# Iteration 024 — Final Report

## Verdict

🥈 **PROMISING** (score 72/100, winner_conditions_met=**False**, 4/5
strict winner conditions met — DSR is the sole barrier).

**Headline finding**: Bond-curve carry-driven duration timing on a
0.9 SPY + 0.6 dynamic-bond stack (TLT ↔ SHV switch driven by 21-day
SMA of T10Y3M, 100 bps ramp, monthly rebalance) is **structurally
novel and mechanically sound** — turnover stays at 0.39-0.46 / yr
(50× lower than iter 023's TSM), no kill criterion triggers, and
the carry signal demonstrably allocates between TLT (steep curve,
70% of bars) and SHV (inverted curve, ~30% of bars). The strategy
**clears the +0.10 Sharpe edge gate on 3/3 datasets** — only the
fifth iteration in the hunt loop to do so cross-dataset, joining
iter 008/015/016/021. However, the carry-allocation layer adds
**effectively nothing** over iter 015's static SPY+IEF base
(Sharpe Δ +0.003 / +0.009 / −0.003 — within noise), while the
TLT/SHV legs introduce more variance than IEF, **regressing MDD
on 2/3 real-data datasets** by ~3 pp. The DSR ceiling at cumulative
n_trials = 4277 remains unbroken (worst p = 0.586 vs iter 016's
0.226 record).

## Headline metrics (top candidate: `bcdt_w90_60_t10y3m_sma21_ramp100bps_v1`)

| dataset | Sharpe (Δ frozen) | CAGR (Δ vs custom bench) | MDD (Δ vs bench) | gates |
|---|---|---|---|---|
| educational | **0.787 (+0.107)** | **12.51% (+1.80 pp vs custom 10.71%)** | 42.57% (**−12.63 pp vs custom 55.20%, IMPROVES**) | 5/7 |
| spy_real    | **1.054 (+0.154)** | **15.71% (+1.03 pp vs custom 14.68%)** | 33.95% (+0.25 pp vs bench 33.70%) | 6/7 |
| ndx_real    | **1.060 (+0.105)** | **19.41% (+0.69 pp vs custom 18.72%)** | 42.65% (+7.53 pp vs bench 35.12%, **WORSE**) | 6/7 |

Per-leg signal diagnostics (kill #B / #D check):

| dataset | mean alloc_TLT | std alloc_TLT | SHV-mode frac | bond-leg turnover / yr | leg corr eq·TLT |
|---|---|---|---|---|---|
| educational | 0.710 | 0.414 | 27.6% | 0.46 | −0.31 |
| spy_real    | 0.708 | 0.417 | 29.5% | 0.39 | −0.29 |
| ndx_real    | 0.697 | 0.421 | 29.8% | 0.45 | −0.22 |

Kill #B (signal too cautious, > 60% SHV bars) and Kill #D (turnover
> 8 / yr) are **clear** — the strategy spends ~70% of bars in TLT
mode and ~30% in SHV mode, with monthly rebalance keeping turnover
at 0.4 / yr. Equity-bond correlations match literature (eq·TLT ≈
−0.25 to −0.31), confirming the diversification axis is intact.

## Score breakdown (frozen benchmarks, canonical)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | beats bench+0.10 on **3/3** datasets (rare; ties iter 016/021's max c1) |
| 2 Gates | 17 | 25 | edu 5/7 (+3) + spy 6/7 (+5) + ndx 6/7 (+5) + cross-ds bonus +4; G2 DSR fails 3/3, G3 WF fails edu 5/8 |
| 3 DSR | **0** | 15 | worst p=0.586 (edu) — far below 0.20 threshold; n_trials=4277 |
| 4 CAGR floor | 15 | 15 | all 3 ds pass 0.8 × bench (edu 12.51% > 9.18%; spy 15.71% > 11.98%; ndx 19.41% > 15.35%) |
| 5 MDD ceiling | 10 | 15 | edu 42.57% ≤ 60.14% ✓; spy 33.95% ≤ 38.70% ✓; ndx 42.65% > 40.12% ✗ (kill C edge case but only 1/3, not triggered) |
| 6 Robustness | **5** | 5 | **9/9 sub-windows positive** — ties iter 013 record (best in hunt loop) |
| **total** | **72** | **100+5** | tier: **🥈 PROMISING** |

## Configuration tested

Single pre-committed cfg `bcdt_w90_60_t10y3m_sma21_ramp100bps_v1` —
NO grid, NO sweep. Cumulative n_trials advance 4276 → 4277 (+1).

```python
CFG = {
    "cfg_id": "bcdt_w90_60_t10y3m_sma21_ramp100bps_v1",
    "eq_w": 0.9,                  # NTSX prospectus equity leg
    "bd_w": 0.6,                  # NTSX prospectus bond leg
    "smoothing_days": 21,         # 21-day SMA on T10Y3M
    "lag_bars": 1,                # σ̂_{t-1} discipline (no look-ahead)
    "ramp_max_bps": 100.0,        # 0bps→0% TLT, 100bps→100% TLT
    "rebalance_bars": 21,         # monthly rebalance
    "carry_signal": "T10Y3M",     # FRED 10Y - 3M
    "cost_bps_per_leg": 0.0002,   # 2 bps/Δposition/leg
}
```

Datasets:
- educational: SPY+TLT+SHV 2007-01-12 → 2026-04-15 (4808 bars,
  SHV-inception aligned, ~19y).
- spy_real: SPY+TLT+SHV 2009-06-26 → 2026-04-15 (4194 bars).
- ndx_real: QQQ+TLT+SHV 2010-02-16 → 2026-04-15 (4036 bars).

## What worked / what didn't

**Worked**

- **3/3 Sharpe edge cross-dataset** — only the 5th iteration to
  achieve this (iter 008/015/016/021/024). The carry mechanism
  IS contributing positive risk-adjusted return.
- **Mechanism is structurally sound and orthogonal to dead-ends**:
  the carry signal (T10Y3M) drives the bond-leg duration mix
  (TLT ↔ SHV) without applying a haircut to total exposure
  (distinct from iter 009/012 closed family) and without
  σ²_port feedback (distinct from iter 013/019/020/021/022 closed
  variance-driven overlay family).
- **Turnover under control**: 0.39-0.46 / yr (vs iter 023's 35 / yr),
  cost drag negligible (~0.02% / yr), so "carry kills via cost" is
  NOT the failure mode here.
- **All 4 kill criteria untriggered**: A (Sharpe vs iter 015 not
  regressed), B (SHV-mode bars 28-30%, well below 60% threshold),
  C (only 1/3 datasets fail MDD ceiling, not 2), D (turnover trivial).
- **Robustness 9/9** — first-ever ≥ 9/9 ties iter 013's record
  in the hunt loop. Edge persists across early/mid/late thirds of
  every dataset (Sharpe range 0.59-1.85 across all 9 sub-windows).
- **G5 forward-stress post-2020** clears with Sharpe +0.71 / +0.71 /
  +0.79 — the 2022 TLT crash protection thesis (switch to SHV when
  curve inverts) IS validated empirically.
- **G7 cross-lib parity**: numpy reference matches pandas within
  0.04 pp on educational, 0.002 pp on spy_real, 0.03 pp on
  ndx_real. Engine is clean.
- **TDD specs**: 14/14 pass; baseline pytest preserved (898 passed,
  5 skipped, +14 new specs vs prior 884).

**Didn't work**

- **DSR ceiling unbroken**: worst p = 0.586 (educational), 0.265
  (spy_real), 0.282 (ndx_real). With n_trials = 4277, even the
  3/3-Sharpe-edge result fails DSR p < 0.05 by a wide margin. This
  is the same ceiling that capped iter 016 at 79/100 (DSR p =
  0.226 there — and that was the BEST DSR ever achieved).
- **Effectively tied with iter 015**: Sharpe Δ vs iter 015 is
  +0.003 / +0.009 / −0.003 — within DSR noise on 17-19 year samples.
  The dynamic carry-allocation layer adds **almost no Sharpe**
  over iter 015's static SPY+IEF (which uses intermediate IEF for
  the entire bond leg). The 2022 TLT-crash protection IS visible
  but is offset by TLT's higher volatility in the steep-curve
  ~70% of bars.
- **MDD regresses vs iter 015 on 2/3 real-data datasets**: spy
  +3.6 pp, ndx +3.1 pp. TLT's drawdown profile (e.g., 2013 taper
  tantrum, 2022 inflation shock) leaks through during steep-curve
  regimes when alloc_TLT ≈ 1. iter 015's static IEF (intermediate
  duration ~7y) absorbs less duration shock per bar.
- **Significantly worse than iter 016**: Sharpe Δ −0.20 / −0.08 /
  −0.13 vs iter 016. iter 016's Moreira-Muir vol-target dynamically
  scales total exposure when σ²_port spikes, providing crash
  protection that the static-leverage iter 024 cannot replicate.
- **G3 walk-forward fails on educational** (5/8 windows profitable
  with MDD < 25%): the 2008-2009 crash hits the leveraged stack
  hard (1.5× of −38% SPY = ~−57% gross before bond cushion). The
  2007-2008 inverted-curve regime forced SHV mode in the early
  data, but the timing was imperfect and one window's MDD exceeded
  25%.

### Mechanism: why carry-allocation barely beats static IEF

Three compounding observations explain why the dynamic carry layer
adds little:

1. **Most of the time the curve is steep** (T10Y3M > 100 bps
   ~70% of bars in 2009-2026). When alloc_TLT ≈ 1, the strategy
   reduces to **0.9 SPY + 0.6 TLT** static. Compared to iter 015's
   **0.9 SPY + 0.6 IEF**, TLT is ~2.5× more volatile than IEF,
   so the per-bar variance is higher AND the per-bar mean return
   is also higher in roughly the same proportion (term premium ~+2-3%
   /yr for TLT vs ~+1-1.5% /yr for IEF). The Sharpe is therefore
   approximately the same.
2. **The SHV-mode protection IS real but partial**. In 2022, the
   curve inverted on 2022-07-05 — but the smoothed signal triggered
   SHV mode only ~3-4 weeks after the actual TLT-yield-rise began
   in Q1 2022. iter 015's static IEF bought through the 2022 TLT
   crash AT INTERMEDIATE DURATION (loss ~13%), while iter 024's
   carry strategy first held TLT through the early-2022 yield-rise
   (loss ~25%) and only switched to SHV after that. Net: similar
   PnL, similar MDD on the spy_real / ndx_real windows.
3. **The signal lag-and-smooth is structurally constrained**. The
   T10Y3M signal must be smoothed to reduce day-to-day noise, but
   smoothing erases the lead-time of the inversion event itself
   (Estrella-Mishkin 1998 documents the lead at 6-18 months for
   recession; the curve-shape ITSELF inverts roughly when the rate-
   hike cycle peaks, with little lead vs the bond-price drawdown).
   Faster signals would be noisier; slower signals would miss the
   regime shift entirely.

The strategy therefore **demonstrates that carry IS a real, distinct
mechanism that adds a non-zero allocation signal**, but on a
0.9/0.6-leveraged 2-bond universe, the ALPHA from regime switching
is approximately equal to the EXTRA RISK from holding TLT (vs
intermediate IEF) most of the time. It's an instructive null
result: the mechanism is operational, the cost structure works, but
the realized PnL is nearly indistinguishable from the static IEF
baseline.

## Main lesson (for future iterations)

**Bond-curve carry as an allocation signal between TLT and SHV
within a 0.9/0.6 leveraged stock-bond stack is mechanically sound
and STRUCTURALLY DISTINCT from the dead-end T10Y3M-haircut family,
but it does not break the DSR ceiling at n_trials=4277, and on the
narrow 2-bond universe (TLT vs SHV) it produces approximately the
same Sharpe as iter 015's static SPY+IEF blend.**

The iteration delivers the FIRST positive 3/3 Sharpe-edge result
since iter 016/021, validating that "carry-as-allocation" is a
genuinely-different mechanism from "carry-as-haircut" (closed by
iter 009/012/013) and from variance-driven overlays (closed by iter
013/014/019/020/021/022). However, the carry premium captured on a
narrow 2-bond duration switch is approximately the same as the
intermediate-duration premium of static IEF, so the layer adds little
realised Sharpe.

Forward-direction implications:

1. **Cross-asset carry on a wider universe** (FX, commodity term-
   structure, equity carry via E/P) would have more independent
   carry signals and could break the saturation observed here. But
   data-availability is a constraint on retail ETF universes.
2. **Carry + value combo** (Asness-Moskowitz-Pedersen 2013 style)
   would add an orthogonal signal to compose with carry; potentially
   captures the cycles where carry alone is mute.
3. **The DSR ceiling at n_trials=4277 is now binding even for
   structurally-novel mechanisms with 3/3 Sharpe edge**. Path-T
   (pre-registered minimal-trial replay of iter 016) becomes more
   attractive as a §7 override artifact: if the goal is Sharpe edge
   under PSR/DSR with a SMALL n_trials prior, iter 016 already
   delivers and would test cleanly with n_trials = 1 (PSR p ~ 0.05
   on its 17y record).

**Specific structural extension** of past dead-ends: the iter
009/012/013 closed family is "T10Y3M (or any business-cycle proxy)
applied as a HAIRCUT/SCALER on a vol-managed blend". iter 024
extends this finding to "T10Y3M applied as ALLOCATION SWITCH on
a STATIC blend" — and the result is qualitatively different (no
σ²_port absorption, no 100% overlap with bottom-20% scale bars)
and quantitatively positive (3/3 Sharpe edge). The dead-end
boundary is therefore TIGHTER than previously assumed: it's not
"any T10Y3M-derived signal" that fails, only "T10Y3M applied as
a multiplicative scaler on a vol-managed base". The signal can
contribute when used as an allocation rule on a non-vol-managed
base.

## Structural finding (for `DEAD_ENDS.md`)

This iteration does NOT close a structural dead-end; it OPENS a
near-equivalent neighbourhood (carry-as-allocation on 2-bond
leveraged stacks). The result is a **plateau** at iter 015's
score (77 → 72 = approximately tied), suggesting that carry timing
and intermediate-duration static allocation are **substitutes**
on this universe, not complements.

A residual structural insight worth recording:

> **Carry-allocation on a 2-bond universe (long vs near-cash) with
> static equity leg saturates near iter 015's static-IEF Sharpe.**
> The mechanism is novel and works as designed, but the alpha
> harvested from regime switching ≈ the volatility cost of holding
> long-duration TLT in steep-curve regimes (~70% of bars). To
> escape the saturation, the bond universe must be widened (3+
> durations across the curve, OR cross-asset carry against
> commodity / FX) so that the regime-allocation signal has more
> than 1 binary axis to operate on.

Status: this is informational, not a blanket closure. Carry-as-
allocation on WIDER universes (e.g., 4-bond curve segmentation,
or cross-asset SPY/TLT/GLD/Cash with carry-rotation) is NOT
closed by this iteration.

## Citations used

Primary:
- `[ilmanen_expected_returns, ch.6-7]` — term premium and
  bond-curve roll-down carry. The specific premium being harvested.
- `[risk_parity, p.10-11, ch.1]` — naïve fixed-weight risk parity
  (basis ratio shared with iter 015/016).
- `[advances_fin_ml, p.31-34]` — cross-lib parity discipline (G7).
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag rule (no look-ahead).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- `[stocks_on_the_move, p.229]` — 2 bps cost model (held constant).
- `[systematic_trading, p.118-119, ch.7]` — slow-signal exit
  thresholds (background framework for 21-day smoothing).

Papers:
- Koijen, Moskowitz, Pedersen & Vrugt (2018). "Carry." *JFE* 127(2),
  197-225. — Cross-asset carry as systematic risk premium.
- Cochrane & Piazzesi (2005). "Bond Risk Premia." *AER* 95(1),
  138-160. — Term-structure factor predicts bond excess returns.
- Estrella & Mishkin (1998). "Predicting U.S. Recessions: Financial
  Variables as Leading Indicators." *Restat* 80(1), 45-61. — T10Y3M
  as recession indicator.
- Asness, Moskowitz & Pedersen (2013). "Value and Momentum
  Everywhere." *JF* 68(3), 929-985. — Forward direction (carry +
  value combo).
- Moskowitz, Ooi & Pedersen (2012). "Time Series Momentum." *JFE*
  104(2), 228-250. — Reference for iter 023's TSM context that
  this iteration's carry mechanism is structurally distinct from.

## Next iteration suggestions

The DSR ceiling at n_trials=4277 is now binding for any
structurally-novel mechanism that produces a 3/3 Sharpe edge.
Three forward directions remain:

1. **Option Z — Slow-EWMAC trend with exit thresholds (lower
   turnover variant of iter 023)**. Same TSM family closed at the
   FAST-signal boundary; slow signals (64/256-day with 5-15% exit
   thresholds) reduce turnover from ~35/yr to ~5-8/yr per leg.
   Structural risk: same basket-size constraint as iter 023, so
   the LoAM bound stays tight; but slow signals could capture the
   2008/2022 crashes more cleanly than the canonical 252/21.
   `[systematic_trading, p.118-119, ch.7]`. **Test before closing
   slow-signal trend.**

2. **Option V — VRP-primary portfolio (whole portfolio around
   short puts/spreads + cash collateral + Tbill yield)**. iter
   020/021 validated VRP overlay edge (+2.95-4.10%/yr) ON TOP of
   iter 016. Building the WHOLE portfolio around VRP changes the
   structure: no equity leg, ~100% T-bills + sold-options, monthly
   rebalance. Premium ~+3-4%/yr (Bondarenko 2014). Risk: tail event
   (2008 / 2020-style); explicit hedge needed. `[volatility_trading,
   ch.3]`.

3. **Option W — Wider-universe carry portfolio**. Extend iter 024's
   bond-curve mechanism to 3+ bond durations (SHV-IEF-TLT)
   simultaneously with cross-sectional carry ranking, OR add a
   cross-asset carry leg (FX or commodity term-structure if data
   becomes available). This addresses iter 024's saturation finding:
   carry on a single binary axis (TLT vs SHV) saturates; carry on
   N≥3 independent axes might break through. Constraint: data
   availability for FX / commodity term structure on retail ETFs.

**NOT recommended**:

- Tweaking iter 024 parameters (smoothing, ramp_max_bps, lag) —
  the saturation is structural, not parametric. iter 015's static
  IEF achieves nearly the same Sharpe with zero free parameters,
  so any iter 024 grid search would find values that match (not
  exceed) the iter 015 plateau.
- T10Y3M-derivatives applied as haircut/scaler (closed by iter
  009/012).
- Same-mechanism on TIP/TLT or BIL/TLT — TIP is 8y duration with
  inflation linkage, BIL is 1-3 mo cash; any 2-asset carry switch
  in this family will hit the same saturation as TLT/SHV.

## Conclusion

Iter 024 is a **structurally novel mechanism that delivers the rare
3/3 Sharpe edge but lands at a Sharpe-tied plateau with iter 015's
static IEF baseline**. It validates "carry-as-allocation" as a
distinct family from the closed "carry-as-haircut" dead-end, and
demonstrates that the DSR ceiling at cumulative n_trials = 4277
binds even on a fresh mechanism with 3/3 Sharpe edge. The path
forward is to widen the carry universe (more independent axes) or
to pivot to slow-trend / VRP-primary mechanisms.
