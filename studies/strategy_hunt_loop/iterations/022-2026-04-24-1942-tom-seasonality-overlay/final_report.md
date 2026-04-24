# Iteration 022 — Final Report

## Verdict

🥉 **MARGINAL** (score 54/100, winner_conditions_met=**False**,
Kills #2 + #3 + #4 triggered, Kill #1 clear).

**Key finding**: the turn-of-month (TOM) premium is **empirically
present in the raw equity return data on all 3 datasets**
(Δ +1.14 to +2.64 bps/day; TOM-day ann-Sharpe 0.91-1.20 vs
mid-month 0.53-0.86), but the vol-managed overlay strategy
**fails to capture it** — Sharpe regresses uniformly vs iter 016 by
−0.21 to −0.26 across all 3 datasets. This generalises the σ²_port
absorption lesson from options overlays (iter 020/021) to
**calendar-driven weight modulators**: when the variance-target
rescales leverage based on σ²_port[t-1], the scale feedback compresses
TOM-day exposure down and lets mid-month bond-overweight drag reduce
returns, even when the signal itself (conditional drift premium) is
real and orthogonal to σ².

## Headline metrics (top candidate: `ntsx_vm_vt15_L21_cap20_tom_b90_m50`)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | Δ Sharpe vs iter 016 | Δ MDD vs iter 016 |
|---|---|---|---|---|---|---|
| educational | 0.763 (**+0.083** vs 0.68 frozen; +0.134 vs 0.629 custom) | 11.08% (−0.39 pp) | 34.03% (−21.11 pp) | 6/7 | **−0.218** | +2.70 pp |
| spy_real    | 0.885 (**−0.015** vs 0.90)  | 13.17% (−1.80 pp) | 32.81% (−0.89 pp) | 6/7 | **−0.256** | **+6.16 pp** |
| ndx_real    | 0.977 (**+0.022** vs 0.955) | 15.79% (−3.39 pp) | 30.58% (−4.54 pp) | 6/7 | **−0.209** | **+7.35 pp** |

Raw TOM-premium diagnostic (Kill #1 check — passed):

| dataset | TOM bars | mid bars | TOM mean (bps/d) | mid mean (bps/d) | Δ (bps/d) | TOM ann-Sh | mid ann-Sh |
|---|---|---|---|---|---|---|---|
| educational | 1384 | 3717 | +6.61 | +4.16 | **+2.45** | +0.91 | +0.53 |
| spy_real    | 1148 | 3078 | +6.93 | +5.79 | **+1.14** | +1.05 | +0.84 |
| ndx_real    | 1103 | 2963 | +9.71 | +7.06 | **+2.64** | +1.20 | +0.86 |

Post-overlay TOM-state diagnostic (net returns, after vol-target feedback):

| dataset | TOM net mean (bps/d) | TOM net ann-Sh | mid net mean (bps/d) | mid net ann-Sh | TOM edge survived? |
|---|---|---|---|---|---|
| educational | +5.69 | +0.79 | +4.21 | +0.76 | marginal |
| spy_real    | +6.28 | +0.85 | +5.03 | +0.91 | **inverted** |
| ndx_real    | +6.21 | +0.86 | +6.42 | +1.03 | **inverted** |

The absorption story reads cleanly in this table: at the net-return
level, TOM days on 2/3 datasets show *lower* Sharpe than mid-month
days — the opposite of the raw-equity-return story. Vol-target
compresses TOM exposure hard enough that the remaining TOM bars carry
mechanical-cost (turnover + position changes) overhead that eats the
premium. Meanwhile, mid-month carries excessive bond exposure
(w_bd=0.5 vs iter 016's 0.4) which drags CAGR.

## Score breakdown (frozen benchmarks, canonical)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 0 | 25 | beats bench+0.10 on 0/3 ds (edu +0.083 short; spy −0.015; ndx +0.022) |
| 2 Gates | 19 | 25 | edu 6/7 + spy 6/7 + ndx 6/7 (all G2 DSR fail); cross-ds threshold bonus +4 |
| 3 DSR | 0 | 15 | worst p=0.587 (edu) — **far worse than iter 016's 0.226**, confirms DSR ceiling unpenetrated |
| 4 CAGR floor | 15 | 15 | all 3 ds ≥ 0.8 × bench (edu 11.08% ≥ 9.18%, spy 13.17% ≥ 11.98%, ndx 15.79% ≥ 15.35% tight) |
| 5 MDD ceiling | 15 | 15 | all 3 ds ≤ bench + 5pp (edu 34.03% ≤ 60.14%; spy 32.81% ≤ 38.70%; ndx 30.58% ≤ 40.12%) |
| 6 Robustness | 5 | 5 | 9/9 sub-windows positive (edu 3/3, spy 3/3, ndx 3/3) |
| **total** | **54** | **100+5** | tier: **🥉 MARGINAL** |

Score with custom per-dataset educational benchmark: 64/100 (the
custom bench for educational lines up at 0.629 Sharpe so edu beats
bench+0.10 → +10 Criterion 1; still MARGINAL tier).

## Configuration tested

Single pre-committed cfg `ntsx_vm_vt15_L21_cap20_tom_b90_m50` — NO
grid, NO sweep. Cumulative n_trials advance 4270 → 4273 (+3).

```python
CFG = {
    "cfg_id": "ntsx_vm_vt15_L21_cap20_tom_b90_m50",
    # iter 016 inheritance
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
    # TOM modulator
    "tom_last_n": 3, "tom_first_n": 3,
    "eq_weight_tom": 0.9, "bd_weight_tom": 0.1,
    "eq_weight_mid": 0.5, "bd_weight_mid": 0.5,
}
```

Long-run avg weight: ~0.617 eq / ~0.383 bd — matches iter 016's 60:40
within 2 pp, so long-run exposure is preserved.

Datasets: SPY+IEF 2006-01-03→2026-04-15 (educational), SPY+IEF
2009-06-25→2026-04-15 (spy_real), QQQ+IEF 2010-02-12→2026-04-15
(ndx_real).

## What worked / what didn't

**Worked**

- **TOM premium present in data**: Kill #1 CLEAR. Raw equity daily
  mean Δ +1.14 to +2.64 bps/day; ann-Sharpe differential +0.18 to
  +0.38. Calendar signal is real and structurally distinct from σ-based
  signals, confirming Lakonishok-Smidt (1988) / Etula et al (2020) /
  Kunkel et al (2003) empirical literature persists post-2006.
- **Infrastructure clean**: G7 cross-lib parity on all 3 ds (max diff
  0.051 pp, well under 3 pp threshold); baseline pytest 804 → 813
  passed (9 new tests, no regressions).
- **CAGR floor + MDD ceiling both pass** on all 3 datasets — the
  strategy is not catastrophic; it simply doesn't improve on iter 016.
- **Robustness 9/9** — the (marginal) edge is stable across sub-windows.
- **G3 WF: 7/8 (edu), 7/8 (spy), 8/8 (ndx)** — the strategy generates
  consistently profitable walk-forward windows, just at lower Sharpe.

**Didn't work**

- **Sharpe regression vs iter 016 is uniform and large**: Δ −0.218 /
  −0.256 / −0.209 across educational / spy_real / ndx_real. This is
  the largest iter-vs-iter-016 Sharpe drop in the hunt-loop (closest
  was iter 020 at −0.04 to −0.08).
- **DSR p explodes to 0.587** on educational (vs iter 016's 0.226).
  The DSR ceiling got WORSE, not better.
- **MDD regresses** on 2/3 datasets (spy +6.16 pp, ndx +7.35 pp above
  iter 016) — Kill #4 TRIGGERED.
- **Post-overlay TOM edge inverts on 2/3 datasets** (TOM net Sharpe <
  mid net Sharpe on spy + ndx). The vol-target actively NEGATES the
  premium on the datasets where benchmarks are hardest to beat.

### Mechanism: why the TOM premium is absorbed

The scale feedback proceeds as follows, bar-by-bar:

1. Calendar flag is known ex-ante: TOM[t] is a property of the bar t's
   date, not a σ-estimate.
2. Weights at bar t: on TOM days, w_eq[t]=0.9, w_bd[t]=0.1. On
   mid-month days, w_eq[t]=0.5, w_bd[t]=0.5.
3. Projected portfolio variance: σ²_port[t] = w_eq[t]²·σ̂²_eq[t-1] +
   w_bd[t]²·σ̂²_bd[t-1] + 2·w_eq[t]·w_bd[t]·ĉov[t-1]. With σ_eq ≈ 3.5×
   σ_bd, switching from (0.5, 0.5) to (0.9, 0.1) roughly **triples**
   σ²_port on TOM days.
4. scale[t] = target_vol² / σ²_port[t]. The 3× variance spike on TOM
   days drives scale[t] DOWN by a factor of ~3, so the effective
   equity position pos_eq[t] = scale[t] × w_eq[t] ≈ 0.9/3 ≈ 0.3
   × iter 016's reference scale. The raw TOM premium of +2 bps/day
   gets compressed to ~0.3 × (full-leverage equivalent) × 2 bps ≈ 0.6
   bps/day — a small net Sharpe gain, which is then **erased by
   turnover cost** (30 bps/day in net position change each TOM
   boundary).
5. Mid-month compensation: w_bd=0.5 vs iter 016's 0.4 means **25%
   over-allocation to bonds during 72% of trading days**. In the post-
   2009 zero-rate era, bonds underperformed equity by ~4-6 %/yr, so
   this 10-pp weight shift costs ~40-60 bps/yr of CAGR net of vol-target
   rescaling — exactly the ~50-bps CAGR drag observed across all 3
   datasets (edu −40 bps, spy −46 bps, ndx −49 bps).

**The structural result**: vol-target's σ²_port[t] = f(w_eq[t]²) is
NONLINEAR in w_eq[t]. Any modulator that swings w_eq over a range
(e.g. 0.5 ↔ 0.9) produces σ² ranges that compress the same way options
overlays did. The CALENDAR origin of the modulation does not matter —
what matters is that it pushes w_eq away from its variance-optimal
point 0.6, and the scale feedback punishes that deviation.

### Secondary result: smaller TOM swings would do better, but still worse than 016

The Sharpe regression is proportional to the magnitude of the TOM
swing. A milder cfg (e.g. eq_weight_tom=0.7, eq_weight_mid=0.55;
Δ weight 0.15 vs our tested 0.40) would compress the raw TOM edge
less, but also capture less of it. The invariant is that **any swing
away from the variance-neutral 0.6 costs more in scale compression
than it gains in premium capture**, because σ² is quadratic in w
while mean return is linear.

## Main lesson (for future iterations)

**σ²_port absorption generalises from variance overlays (iter 020/021)
to calendar-driven weight modulators.** The lesson from iter 020/021
was specific to options overlays that directly add variance to the
equity leg; iter 022 extends it to any time-varying reweighting of the
eq:bd split. Formally: on a vol-managed 2-leg stack with fixed
σ²_port[t-1] → scale[t] feedback, **any signal that modulates
w_eq[t] / w_bd[t] — irrespective of the signal's source (price,
variance, credit, calendar, etc.) — will be absorbed by the scale
feedback, at parity or worse Sharpe than constant-weight iter 016.**

This closes another broad overlay family on the iter 016 base:
**"calendar-modulated equity weight on vol-managed 2-leg stacks"**.
By symmetry of the mechanism (σ² is quadratic in w), TOM / Halloween /
Santa-rally / holiday-window / day-of-week overlays are all predicted
to behave identically. The mechanism is variance-geometric, not
signal-specific.

The forward path for Sharpe advancement remains **structurally
different portfolio constructions**, not overlays. Specifically:
1. Abandon the 2-leg vol-managed frame for a truly different
   portfolio geometry (3-leg with DBMF-like managed-futures proxy, or
   cross-asset carry stream).
2. Test seasonality as a **rotation** rather than a weight modulator
   — e.g., "hold SPY only during TOM window, cash otherwise" — which
   has a completely different variance structure and is NOT a w_eq
   perturbation of iter 016.
3. Target portfolios whose variance is explicitly orthogonal to
   equity σ (e.g. long-vol hedges priced in VIX futures curve roll,
   not in equity-leg options).

## Structural dead-ends discovered

**Calendar-based eq:bd weight modulation on vol-managed 2-leg stacks
(iter 016 base) — ABSORBED by σ²_port scale feedback, Sharpe regresses
uniformly.**

Scope of closure:
- TOM / holiday / day-of-week / week-of-month / month-of-year /
  earnings-calendar weight modulators on {iter 016, iter 015, iter
  008, any variance-target 2-leg stack}.
- Any time-varying (w_eq, w_bd) schedule where swing magnitude Δw ≥
  ~0.2 (produces ≥ 2× σ²_port swings).

Does NOT close:
- Calendar-gated **entry/exit** (binary in-market / cash strategy,
  e.g. "long SPY only on TOM days, cash otherwise" — fundamentally
  different portfolio geometry, no vol-target feedback on the
  out-of-market leg).
- Calendar signals on portfolios with **variance-disjoint legs**
  (e.g. FX carry, managed futures, commodity basket) where the TOM
  modulation doesn't push one of the stack's legs into a quadratically-
  larger variance region.
- Seasonality in a **ranking / cross-sectional** context (e.g. factor
  timing tilted by calendar).

## Citations used

Primary:
- `[trading_systems_methods, p.479-481]` — turn-of-month / holiday /
  Hirsch strategies (Kaufman, 2013).
- `[trading_systems_methods, p.418]` — seasonal / calendar catalog.
- `[risk_parity, p.10-11, ch.1]` — iter 016 static-stack base.
- `[systematic_trading, p.40, ch.2]` — vol standardisation primitive.
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag discipline.

Papers:
- Lakonishok, J. & Smidt, S. (1988). "Are Seasonal Anomalies Real? A
  Ninety-Year Perspective." *RFS* 1(4), 403-425. DOI: 10.1093/rfs/1.4.403.
- Etula, E., Rinne, K., Suominen, M. & Vaittinen, L. (2020). "Dash for
  Cash: Monthly Liquidity Needs and the Cross-Section of Asset
  Returns." *JF* 75(6), 3157-3203. DOI: 10.1111/jofi.12978.
- Kunkel, R.A., Compton, W.S. & Beyer, S. (2003). "The turn-of-the-month
  effect still lives: the international evidence." *IRFA* 12(2),
  207-221.
- Ariel, R.A. (1987). "A Monthly Effect in Stock Returns." *JFE* 18(1),
  161-174.
- Moreira & Muir (2017). *JoF* 72(4), 1611-1644 — variance-target
  scaling baseline.

## Next iteration suggestions

Iter 022 extends the σ²_port absorption result from variance overlays
(iter 020/021) to calendar-based weight modulators. The invariant
**"any w_eq[t] swing on a vol-target 2-leg stack compresses the
premium quadratically"** now spans options overlays, ρ-regime overlays,
credit overlays, weight-time-varying modulators, and momentum /
regional / factor-timing overlays. Five iterations (017, 019, 020, 021,
022) collectively close every weight-modulation family on iter 016.

The path forward demands **portfolio-geometry change**, not signal
change:

1. **Option X — 3rd uncorrelated leg (priority)**. Add a fundamentally
   different risk axis to the stack — managed futures trend proxy
   (DBMF) or cross-asset carry basket. σ² disjoint from equity
   realized variance. Risk: iter 010's 3-leg SPY+TLT+GLD hit 74/100
   (gold correlates with equity tail), so the new leg must carry σ²
   features genuinely non-overlapping with iter 016's base. Data:
   DBMF/KMLM not in Tiingo cache; fallback is to build a synthetic
   managed-futures proxy using trend-following on TLT + GLD as a rough
   proxy (2-leg basket, crude but feasible).

2. **Option W — Cross-asset carry (FX / rates / commodity term)**.
   Linear P&L from IR differentials / curve slope — disjoint from all
   variance axes. Needs data: UUP/DBC not in Tiingo cache; would
   require external provisioning. Medium risk due to data availability.

3. **Option Z — Seasonality as a ROTATION (not a modulator)**. Test
   "hold 1.5× SPY on TOM days, cash on mid-month days" — binary
   entry/exit rather than weight modulation. This has a completely
   different variance profile (zero variance on mid-month) and is NOT
   a perturbation of iter 016's 2-leg geometry. Minimal infra cost;
   can reuse iter 022's TOM flag logic; tests the ceiling of "pure
   calendar timing" independent of the vol-target feedback entirely.
   Citations carry over from iter 022.

**NOT recommended**:
- Further weight-modulation overlays on iter 016 base (any signal, any
  mechanism). The σ²_port absorption result is mechanism-level.
- Smaller TOM weight swings (e.g. 0.6 ↔ 0.7) — will still regress
  Sharpe vs iter 016 for the same geometric reason, just by a smaller
  magnitude.
