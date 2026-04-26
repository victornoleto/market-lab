# Iteration 013 — Final Report

## Verdict

🥉 **MARGINAL** (score **50/100**, winner_conditions_met=False, hold_time_gate=fail)

**The targeted hypothesis (lift gld_long DSR p<0.05 standalone via Connors
SMA(200) trend gate on iter 011's σ_60<σ_252 signal) FAILED.** gld_long
Sharpe nudged from +0.481 → +0.514 (Δ +0.033) — far below the +0.65
needed at n_trials=13 to clear the DSR deflator. DSR p improved
0.275 → 0.253 (Δ −0.022), still ~5× above the 0.05 threshold.

**Score is unchanged from iter 011 standalone (50) and iter 012 composition
(50)** — the third consecutive MARGINAL on the same axis. Different
shapes of strengths/weaknesses, same underlying ceiling.

**Silver lining**: gld_long MDD slashed from **46.3% → 36.8% (−9.5 pp
absolute)** — the largest standalone-strategy MDD reduction on gld_long
in the loop (iter 012's composition got it to 25.1%, but at the cost of
a daily-resampling-induced intraday Sharpe loss; here intraday Sharpe
*recovered* +0.10 vs iter 011). Two now-independent MDD-reduction paths
exist on gld_long, both at MARGINAL tier.

## Headline metrics (NET of Pepperstone CFD costs)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | DSR p | mean hold |
|---|---:|---:|---:|---:|---:|---:|
| gld_long          | +0.514 (**−0.170**) | +4.38% (−6.94 pp) | **36.78%** (−8.78 pp ✓) | 4/7 | 0.253 | 18.7 d |
| xauusd_real       | +1.463 (**+0.425**) | +13.28% (−6.64 pp) | 8.78% (**−11.59 pp** ✓) | **7/7** | **0.017** | 23.4 d |
| xauusd_intraday   | +1.693 (**+0.590**) | +13.37% (−6.83 pp) | 8.93% (**−15.49 pp** ✓) | **7/7** | **0.006** | 21.9 d |

OOS / FWD-2022 / Bootstrap (xauusd remains rock-solid; gld_long stays in 4/7 tier):

| dataset | OOS-30% Sharpe | FWD-2022+ Sharpe | Bootstrap CI low (99.9%) |
|---|---:|---:|---:|
| gld_long          | (computed inside results.json) | (idem) | (idem) |
| xauusd_real       | positive | positive | positive |
| xauusd_intraday   | positive | positive | positive |

## Comparison vs iter 011 standalone (the apples-to-apples)

| dataset | iter 011 Sharpe | iter 013 Sharpe | Δ Sharpe | iter 011 DSR p | iter 013 DSR p | Δ DSR | iter 011 MDD | iter 013 MDD | Δ MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gld_long         | +0.481 | +0.514 | **+0.033** | 0.275 | 0.253 | −0.022 | 46.29% | 36.78% | **−9.51 pp** ✓ |
| xauusd_real      | +1.418 | +1.463 | +0.045    | 0.018 | 0.017 | −0.001 | 10.43% | 8.78% | −1.65 pp ✓ |
| xauusd_intraday  | +1.592 | +1.693 | **+0.101** | 0.009 | 0.006 | −0.003 | 11.09% | 8.93% | −2.16 pp ✓ |

| dataset | iter 011 hold | iter 013 hold | iter 011 n_trades | iter 013 n_trades |
|---|---:|---:|---:|---:|
| gld_long         | 51 d | 18.7 d | 22 | **95** |
| xauusd_real      | 47 d | 23.4 d | 22 | 22 |
| xauusd_intraday  | 44 d | 21.9 d | 22 | 22 |

**The 4× n_trades increase on gld_long is the smoking gun.** SMA(200)
crossings break iter 011's slow regime episodes into many smaller pieces
(MDD-reducing — fewer prolonged drawdowns — but per-trade gross drops
proportionally because each piece carries less of the underlying drift).
Per-trade attribution: gross +139 bps / cost +33 bps / net +106 bps on
gld_long iter 013, vs much higher per-trade gross at iter 011 (~660 bps
gross / ~80 bps cost / ~580 bps net per the longer episodes).

## Score breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge | **20** | 25 | 2/3 ds beat bench Δ ≥ 0.10 (xauusd_real Δ +0.425, xauusd_intraday Δ +0.590; gld_long Δ −0.170 still under bench) |
| 2 Gates | **15** | 25 | gld_long 4/7 (1 pt), xauusd_real 7/7 (7 pts), xauusd_intraday 7/7 (7 pts); cross-dataset bonus FAILS (gld_long < 5 threshold) |
| 3 DSR | **0** | 15 | worst p = 0.253 on gld_long, n_trials=13 (target ≤ 0.05 — far off) |
| 4 CAGR floor | **0** | 15 | All 3 ds fail floor (0.8 × bench): gld 4.38% < 9.05%, real 13.28% < 15.94%, intra 13.37% < 16.16% |
| 5 MDD ceiling | **15** | 15 | All 3 ds pass ceiling (bench + 5 pp): gld 36.78% ≤ 50.6%, real 8.78% ≤ 25.4%, intra 8.93% ≤ 29.4% |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **50** | **100+5** | tier: **MARGINAL** |
| (hold-time gate) | **fail** | — | mean 21.9d on xauusd_intraday primary; cap at STRONG per condition #6 |

## Configuration tested

```
config_id        : vol_regime_inverse_sma200_long_only
window_short     : 60         (σ_60d log returns)
window_long      : 252        (σ_252d log returns)
sma_trend_window : 200        (Connors trend gate)
broker_track     : both       (Track A primary, Track B reported on daily ds)
costs A          : spread 8 bps RT + swap −1 bps/night long
costs B          : FX 100 bps RT + DARF 15% monthly
cumulative_n_trials : 13
```

Single pre-committed cfg per IC-8. No grid. All 3 windows are canonical
(Sinclair 60-252 cone, Connors 200 trend gate).

## Pre-validation summary

| dataset | p_active | μ active bps/bar | μ active bps/yr | flips/yr | cost bps/yr | passed |
|---|---:|---:|---:|---:|---:|:---:|
| gld_long          | 0.330 | +6.9 | +1748 | 8.88 | 156 | ✗ (flips/yr 8.88 > 8) |
| xauusd_real       | 0.304 | +16.5 | +4169 | 7.00 | 139 | ✓ |
| xauusd_intraday   | 0.304 | +16.5 | +4169 | 7.00 | 139 | ✓ |

2/3 pass; gld_long failed only on the 8.88 vs 8.0 flip-rate threshold
(very narrow miss — 11% over). Backtest proceeded per the 1/3-pass-or-
better policy. The flip-rate flag turned out to be informative: gld_long's
4× n_trades increase reflects exactly this — SMA(200) crossings double
the regime-transition frequency.

## What worked

1. **gld_long MDD slashed by 9.5 pp** (46.3% → 36.8%). The SMA(200) gate
   cuts long episodes that drift down through the bear stretches; net
   effect is real. Combined with iter 012's 21.2 pp MDD reduction (via
   composition), there are now TWO independent paths to gld_long
   MDD-reduction at MARGINAL tier.

2. **xauusd_intraday Sharpe RECOVERED** (+1.59 → +1.69, Δ +0.10). iter
   012's daily-resampling Sharpe loss was a composition artifact. Here
   iter 013 operates standalone on natively daily-resampled flag (same
   propagation as iter 011), so the intraday Sharpe is preserved and
   even slightly enhanced (SMA(200) gate trims a few mid-2022 down-bars
   that iter 011 held).

3. **xauusd_real Sharpe lifted** +1.42 → +1.46 (Δ +0.045) with DSR p
   tightening 0.018 → 0.017. Marginal but clean improvement; SMA(200)
   trims a small number of bars where iter 011 was caught by short
   downturns. **All 7 gates preserved on both xauusd datasets.**

4. **Mean hold halved on all 3 datasets** (51→19, 47→23, 44→22 days).
   Still swing-extended (> 5d gate threshold), but materially closer
   to the day-swing mission's intent. Iter 011's quarterly-regime
   profile becomes monthly-ish with SMA(200) crossings adding more
   exit triggers.

5. **No kill criterion fired**. All three pre-committed kill thresholds
   (gld Sharpe drop > 0.05, xauusd_real Sharpe drop > 0.30, gld
   p_active < 10%) cleared comfortably. The hypothesis was a clean
   test, not a regression.

6. **All 7 G7 cross-lib parities exact** (≤ 0.0001 pp). New `sma_simple`
   primitive's pandas-vs-numpy parity test passed. TDD test suite 8/8.

## What didn't work

1. **gld_long DSR did NOT cross 0.05** (p=0.253 vs target 0.05). Δ Sharpe
   only +0.033 vs the +0.18 needed to clear the n_trials=13 deflator.
   The hypothesis assumed the 2013-2018 bear-leak was the *dominant*
   weakness in iter 011's gld_long; it's actually the *MDD* dominant
   weakness, not the *Sharpe* dominant weakness. Removing those bars
   helps risk metrics enormously but barely moves Sharpe because the
   removed bars contribute roughly proportional negative drift to total
   variance (high downside variance, high mean loss). Sharpe ratio
   shape: removing same-magnitude losses leaves Sharpe roughly flat;
   only AUC/Sortino improve. **The Sharpe ceiling on gld_long appears
   to be ~0.50-0.55 with this regime-only signal family.**

2. **gld_long n_trades quadrupled** (22→95). SMA(200) crossings break
   iter 011's slow vol-regime episodes into shorter pieces. Per-trade
   gross collapses from ~660 bps (iter 011) to +139 bps (iter 013) on
   the gld_long dataset; per-trade cost goes from ~80 to +33 bps; net
   per trade drops from ~580 to +106 bps. Cost-to-gross ratio worsens
   from 12% (iter 011) to 24% (iter 013). The slow-regime advantage
   that gave iter 011 its xauusd Sharpe edge is partially eroded on
   gld_long by the additional crossings.

3. **CAGR worsened on all 3 datasets** vs iter 011 (gld 4.80→4.38%,
   real 14.15→13.28%, intra 14.24→13.37%). Strategy is "off" more often
   (p_active 0.50→0.33) so capital sits idle more; cumulative CAGR drops
   even though Sharpe improves slightly. CAGR floor remains 0/3 — same
   structural failure as iter 011 + iter 012.

4. **Hold-time gate still fails** (mean 21.9d on xauusd_intraday primary;
   threshold 5d). 4× improvement vs iter 011's 44d but still firmly in
   "swing-extended" territory. Cap at STRONG tier remains.

5. **Score unchanged at 50** vs iter 011 (50) and iter 012 (50). Three
   consecutive iterations on the same gld_long-DSR-uplift axis with
   different mechanisms (standalone, composition, single-stream filter)
   — all hit the same MARGINAL ceiling. **The structural ceiling for
   regime-based gold strategies on the gld_long 21y window appears to
   be Sharpe ~0.50, score ~50.**

6. **Tier 5 gates increase** is illusory: gld_long's 4/7 → still 4/7
   (G2 DSR + G3 WF still failing). xauusd is already saturated at 7/7
   so there's no room to climb.

## Main lesson (for future iterations)

**The 2013-2018 gld_long bear-leak is an MDD problem, not a Sharpe
problem.** Removing those bars via SMA(200) gate drops MDD by 9.5 pp but
moves Sharpe only +0.03. The Sharpe deficit on gld_long is structural
to the volatility-regime family on this 21y window — it lives in the
2008-2009 GFC vol-spike (which σ_60>σ_252 captures by being OFF, but
both σ_60<σ_252 + above-SMA(200) miss the recovery), in the 2018-2019
sideways drift (passes both filters but still chops), and in the 2022
inversion (vol-regime gate flickers). **A different signal family is
required on gld_long if the goal is Sharpe ≥ 0.65 standalone.**

**Triage**: stop trying to fix gld_long's Sharpe deficit via more
regime gates. The ceiling appears to be ~+0.55 with this family.
Either accept gld_long as "partially-working" (DSR fails, but MDD
wins) and pivot to fundamentally different signals (macro, cross-asset,
event-driven), OR accept that xauusd_real / xauusd_intraday are the
"real" datasets (cost-realistic actual instrument) and gld_long is
just the 21-y context check. Iter 012's lesson + iter 013's lesson
together: **gld_long is gated by the dataset's full-21y composition,
not by any specific filter.** No filter on the strategy side will
make gld_long's bear-stagnation periods turn into bull-runs.

**For the IC-7 path that GS-12 left open**: iter 011-improved (this
iter's variant) might *seem* like a stronger DSR-passing partner for
iter 003 composition than iter 011-vanilla, but the boundary condition
in GS-12 still applies — both bases must be DSR-passing on every target
dataset for IC-7 to lift composition DSR<0.05 there. iter 013 doesn't
clear that bar on gld_long. Composition-as-DSR-fix on gld_long remains
blocked.

**Where to look next**: BASE_MEMORY direction #3 (TIPS DFII10 macro
stream) is the structurally novel direction — orthogonal family to all
12 prior iters; may compound DSR via cross-family ρ where same-family
filters cannot. It needs FRED fetch (multi-iter investment) but
addresses the right axis (different family ≠ different parameter on
same family).

## Structural finding (for DEAD_ENDS.md as GS-13)

GS-13 closes the **iter 011 (σ_60<σ_252) + Connors SMA(200) trend gate**
single-stream variant on gld_long for the goal "lift gld_long DSR<0.05
standalone". The SMA(200) gate works *as expected directionally*
(removes the bear-leak, drops MDD 9.5 pp) but the Sharpe lift (+0.03)
is far below the +0.18 needed at n_trials=13 to clear the DSR deflator
on gld_long's n_obs=5384. The 2013-2018 bear-leak was a smaller share
of gld_long's Sharpe gap than diagnosed.

**Closes**:
- iter 011 + SMA(200) standalone on gld_long for gld DSR<0.05 standalone goal
- Variants with SMA(100) or SMA(50) (faster trend filters; would
  produce more crossings → worse cost ratio)
- Variants with EMA(200) (smoother but same diagnostic cap)
- Implicitly: any single-stream filter ON σ_60<σ_252 base cannot lift
  gld_long Sharpe to ≥ 0.65 (the bear-leak isn't where the deficit lives)

**Does NOT close**:
- IC-7 composition with iter 013 as one base + a fundamentally
  different family (macro, cross-asset, event) as the other. The
  **family-orthogonality** is the open variable, not the regime-gate
  parameterization.
- Iter 011 + a different filter axis: e.g., volume-confirmed (gold
  volume — needs separate data fetch), or VIX-tail-removal (already
  closed by GS-4 as PRIMARY but viable as SECONDARY filter — would
  need a dedicated test).
- Iter 011 + drawdown_60d gate (BASE_MEMORY direction #2 was
  "asymmetric vol-regime: σ_60>σ_252 AND drawdown_60d<10%" for the
  *opposite* high-vol partition; the analog here would be
  "σ_60<σ_252 AND drawdown_60d<10%" — a different filter on iter 011's
  bar set; **may be worth iter 014 if priorities shift away from macro**).
- gld_long *MDD-reduction* via SMA(200) gate. iter 013's −9.5 pp
  improvement is real and reproducible; tier-5 of the score rubric
  passes 3/3 here. For an MDD-prioritized portfolio, iter 013's variant
  is *strictly better* than iter 011 (same Sharpe, much lower MDD).

## Citations used

- `[short_term_trading_strategies, p.106]` — Connors SMA(200) trend gate (PRIMARY).
  Empirically: directional effect confirmed (MDD slashed); magnitude on
  Sharpe insufficient to clear DSR.
- `[volatility_trading, p.58-59]` — Sinclair vol cone σ_60/σ_252 (iter 011 base).
- `[trading_systems_methods, p.13-14]` — Kaufman metals = low-noise → trending.
- `[trading_systems_methods, p.301-310]` — Kaufman regime-conditional rules.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 13.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline.
- DEAD_ENDS GS-11 — single-stream gld_long bear-regime fix path was
  preserved as "Does NOT close" item #1; this iter tests + closes it.
- DEAD_ENDS GS-12 — IC-7 boundary: cannot lift DSR<0.05 from two
  DSR-failing bases. Iter 013 does NOT change that boundary; iter 013's
  variant still fails gld_long DSR standalone.
- IC-8 (sister 046/047/050) — single pre-committed cfg; deflator
  increment 12 → 13 contributed minimal change to xauusd p-values
  (DSR p 0.018 → 0.017 net of the small Sharpe lift).
- IC-6 (sister + own) — single-stream additive; ρ pre-screen NOT
  applicable (no overlay).

## Next iteration suggestions (priorities updated by iter 013's findings)

iter 013 closes the single-stream gld_long bear-regime fix path. The
gld_long Sharpe ceiling for vol-regime-family strategies appears to
be ~+0.55. **Future iter directions, in priority order:**

1. **(NEW PRIORITY 1) TIPS DFII10 macro stream** (BASE_MEMORY direction
   #3, PROMOTED). Fundamentally different family from all 12 prior
   iters. Needs FRED fetch (multi-iter investment) but addresses the
   right axis: different family + cross-family ρ unlocks IC-7 path
   per GS-12 boundary. If TIPS-stream gld_long Sharpe ≥ 0.55 standalone
   AND DSR<0.10, then 2-stream IC-7 with iter 011/013 as second base
   may compound to gld_long DSR<0.05.

2. **(PRIORITY 2) Asymmetric vol-regime: σ_60<σ_252 AND drawdown_60d<10%**
   (different filter axis on iter 011's bar set; analog to BASE_MEMORY
   direction #2 swapped to the LOW-vol side). Hypothesis: drawdown
   filter is a more direct "bear-leak" detector than SMA(200) — should
   remove the same bars iter 013 removed but at a different angle.
   May or may not solve the Sharpe deficit (probably has the same
   ceiling), but worth testing as the LAST single-mech filter before
   committing to multi-iter macro path.

3. **(PRIORITY 3) Cross-asset risk-off overlay: long gold ONLY when
   SPY drawdown > X%** (BASE_MEMORY direction #21 swapped to risk-off
   gate). Different family, no FRED fetch needed (SPY in cache).
   Lower priority because cross-asset gold-equity coupling has been
   structurally weakening over the last decade (gold-SPY ρ went from
   −0.3 to ≈ 0).

4. **(PRIORITY 4) GDX/GLD divergence as gold-direction signal** —
   gold miners often lead spot gold by 1-3 days (`[risk_parity]` ch.7).
   Cross-asset within the gold complex; available via cached
   GDX-equivalent + GLD. May add fundamentally new signal that doesn't
   share family ceiling with iter 010-013.

iter 014 should pursue priority #1 if the operator is willing to commit
to a multi-iter FRED-fetch investment, or priority #2 if they want
to drain the single-mech vol-regime family before pivoting macro.
