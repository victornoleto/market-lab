# Iteration 012 — Final Report

## Verdict

🥉 **MARGINAL** (score **50/100**, winner_conditions_met=False, hold_time_gate=fail)

**Same score as iter 011 standalone — composition does NOT compound** for these
two bases. The IC-7 hypothesis as framed by BASE_MEMORY's iter 012 candidate
list (lift gld_long DSR p<0.05 via Markowitz combination of iter 011 inverse
vol-regime + iter 003 RSI(2)+SMA(200)) **failed its primary objective**:
gld_long DSR p improved from 0.275 → 0.201 but still fails the 0.05 threshold.

The composition successfully **halved gld_long MDD** (46.3% → 25.1%, a
−20 pp absolute improvement, the largest MDD reduction in any single iter
on gld_long), and **preserved the xauusd_real strong tier** (Sharpe +1.42,
DSR p=0.020, gates 7/7) — but **xauusd_intraday Sharpe degraded by −0.17**
(1.59 → 1.42) due to the daily-resampling required to align iter 011's
1h granularity with iter 003's daily frequency. **Net: same MARGINAL tier,
different shape of strengths and weaknesses.**

This iteration **closes** the IC-7 path for these specific bases on gold
(GS-12 candidate). The structural finding: with ρ ≈ +0.10 and a 5-7×
Sharpe-mismatch (iter 011 ~1.4-1.6 vs iter 003 ~0.2-0.3 on xauusd), the
Markowitz tangency formula concentrates 83-91% of capital on iter 011 and
delivers near-zero diversification compounding on the dominant-Sharpe
datasets. The DSR uplift hoped for on gld_long doesn't materialize because
**BOTH** base streams have weak gld_long standalone DSR (iter 011 p=0.275,
iter 003 p=0.30+) — combining two streams that individually fail the 0.05
threshold cannot rescue either.

## Headline metrics (NET of Pepperstone CFD costs, both components already cost-included)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | DSR p | weighted-avg hold |
|---|---:|---:|---:|---:|---:|---:|
| gld_long          | +0.542 (**−0.142**)  | +2.87% (−8.45 pp)  | **25.1%** (**−20.45 pp** ✓)  | 4/7 | 0.201 | 31.7 d |
| xauusd_real       | +1.419 (**+0.381**) | +12.86% (−7.07 pp) | 9.5%  (**−10.89 pp** ✓) | **7/7** | **0.020** | 43.0 d |
| xauusd_intraday   | +1.424 (**+0.321**) | +11.81% (−8.39 pp) | 8.8%  (**−15.64 pp** ✓) | **7/7** | **0.020** | 37.1 d |

OOS / FWD-2022 Sharpes (all positive, very strong on xauusd):

| dataset | OOS-30% Sharpe | FWD-2022+ Sharpe | Bootstrap CI low (99.9%) |
|---|---:|---:|---:|
| gld_long          | +0.993 | +1.433 | −0.075 |
| xauusd_real       | +2.513 | +1.665 | +0.168 |
| xauusd_intraday   | +2.499 | +1.667 | +0.159 |

## Composition vs iter 011 standalone (the apples-to-apples comparison)

| dataset | iter 011 alone Sharpe | iter 012 comp Sharpe | Δ | iter 011 DSR p | iter 012 DSR p | Δ |
|---|---:|---:|---:|---:|---:|---:|
| gld_long          | +0.481 | +0.542 | **+0.060** | 0.275 | 0.201 | −0.074 (fails 0.05) |
| xauusd_real       | +1.418 | +1.419 | +0.001 | 0.018 | 0.020 | +0.002 (∼flat) |
| xauusd_intraday   | +1.592 | +1.424 | **−0.168** | 0.009 | 0.020 | +0.011 (slight degradation) |

| dataset | iter 011 alone MDD | iter 012 comp MDD | Δ |
|---|---:|---:|---:|
| gld_long          | 46.3%  | **25.1%**  | **−21.2 pp** ✓ |
| xauusd_real       | 10.4% | 9.5%  | −0.9 pp |
| xauusd_intraday   | 11.1% | 8.8%  | −2.3 pp |

**Net effect**: iter 003's RSI(2)+SMA(200) MR adds risk-reduction to
gld_long (its dominant region of relative weight, w_003 = 0.58) and dampens
DSR drag, but it ADDS no Sharpe to xauusd (where it gets only 9-17% of weight
because Markowitz allocates by sharpe-ratio-density). And the daily
resampling required for the intraday dataset throws away exactly the
intraday Sharpe edge iter 011 captured. **Score 50/100 unchanged.**

## Markowitz weights + correlations (full-sample, in-sample)

| dataset | ρ(011, 003) | S_011 | S_003 | w_011 | w_003 |
|---|---:|---:|---:|---:|---:|
| gld_long          | **+0.104** | +0.481 | +0.299 | 0.4195 | 0.5805 |
| xauusd_real       | +0.097     | +1.418 | +0.193 | 0.9064 | 0.0936 |
| xauusd_intraday   | +0.091     | +1.419 | +0.242 | 0.8266 | 0.1734 |

The 41.95% / 58.05% gld_long allocation is **the only meaningful Markowitz
diversification** in the composition — on xauusd, the Sharpe gap is too
wide for ρ=0.09 to give iter 003 any non-trivial weight (formula:
`w_A ∝ (S_A − ρ·S_B)`; with S_A≈1.4 and ρ·S_B≈0.02, the term is essentially
S_A unchanged). This is **textbook IC-3** (sister 049): when Sharpes
differ by > 30%, Markowitz heavily favors the higher-Sharpe stream, even
at low correlation.

## Score breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge | **20** | 25 | 2/3 ds beat bench by ≥ 0.10 (xauusd_real Δ +0.381, xauusd_intraday Δ +0.321; gld_long Δ −0.142) |
| 2 Gates | **15** | 25 | gld_long 4/7 (1 pt), xauusd_real 7/7 (7 pts), xauusd_intraday 7/7 (7 pts); cross-dataset bonus FAILS (gld_long < 5 threshold) |
| 3 DSR | **0** | 15 | worst p = 0.201 on gld_long (`> 0.05`), n_trials=12; **the entire iter 012 bet was lifting this below 0.05 — failed** |
| 4 CAGR floor | **0** | 15 | All 3 ds fail floor (0.8 × bench): gld 2.87% < 9.05%, real 12.86% < 15.94%, intra 11.81% < 16.16%. CAGR floor regressed vs iter 011 standalone (gld 2.87% < 4.80%) — both streams flat ~50% of time → composition flat ~70% of time |
| 5 MDD ceiling | **15** | 15 | All 3 ds pass ceiling (bench + 5 pp): gld 25.1% ≤ 50.6%, real 9.5% ≤ 25.4%, intra 8.8% ≤ 29.4%. **gld_long MDD halved vs iter 011** |
| 6 Robustness | 0 | 5 | Not computed |
| **total** | **50** | **100+5** | tier: **MARGINAL** |
| (hold-time gate) | **fail** | — | weighted-avg hold 37.1d on xauusd_intraday (primary ds); composition inherits iter 011's swing-extended hold; cap at STRONG tier per condition #6 |

## Configuration tested

```
config_id              : composition_iter_003_iter_011_markowitz
method                 : full-sample Markowitz tangency on net-of-cost daily returns
streams                : iter 003 (connors_rsi2_sma200_filter) + iter 011 (vol_regime_inverse_60_252_long_only)
weight_constraint      : w_A + w_B = 1; clamped to corner if either < 0
intraday_handling      : aggregate iter 011's 1h net-returns to daily sums; combine at daily resolution
costs                  : already inside each component's net returns (no double-charging)
broker_track           : pepperstone_cfd (primary)
cumulative_n_trials    : 12
```

Single pre-committed cfg per IC-8. No grid sweep over weights / windows /
horizons. The Markowitz weights themselves are deterministic given the
sample, so this is **one trial** in DSR accounting (the deflator increment
12 vs 11 reduces all DSR p-values by ~0.005-0.010, which contributes to
the xauusd_real DSR p slight degradation 0.018 → 0.020).

## Pre-validation summary (IC-6: ρ < 0.30 on > 80% of bars)

iter 011 already measured the per-dataset full-sample correlations:

| dataset | ρ measured iter 011 | re-measured iter 012 | IC-6 threshold |
|---|---:|---:|---:|
| gld_long          | +0.104 | +0.104 | < 0.30 ✓ |
| xauusd_real       | +0.096 | +0.096 | < 0.30 ✓ |
| xauusd_intraday   | +0.004 (1h vs 1d) | +0.091 (daily-resampled) | < 0.30 ✓ |

The xauusd_intraday ρ shifts from +0.004 (iter 011 reported on 1h-vs-daily
mismatched indices) to +0.091 (iter 012 properly daily-aggregates iter 011
to daily and joins on daily index). The new ρ is the correct one for
composition; both still well within IC-6 sweet spot.

## What worked

1. **gld_long MDD halved** (46.3% → 25.1%, the largest single-iter MDD
   improvement on gld_long in the loop). The RSI(2)+SMA(200) component's
   short-period mean-reversion timing reduces gld_long drawdown depth
   exactly when iter 011's slow regime gate is in a low-vol bear stretch
   (2013-2018). The two streams complement on the loss-distribution side
   even though they don't compound on the Sharpe side.

2. **xauusd_real preserved 7/7 gates + DSR p<0.05**. Composition didn't
   destroy what iter 011 already had on xauusd_real — the 90.6% iter 011
   weight ensures the dominant signal carries. DSR p degraded from 0.018
   to 0.020 (≈+10% n_trials deflator + tiny variance increase) but stays
   below 0.05.

3. **All 3 OOS Sharpe + FWD Sharpe positive**. OOS-30%: +0.99 / +2.51 /
   +2.50; FWD-2022+: +1.43 / +1.66 / +1.67. Robustness across temporal
   slicing remains strong on xauusd; gld_long OOS Sharpe +0.99 hints
   that the composition's recent-period (post-2017) performance is much
   better than the full-sample 21-y average (2013-2018 stagnation drags
   gld_long full-sample down).

4. **All 7 G7 cross-lib parities exact (≤ 0.0001 pp)**. Composition is
   computed deterministically from saved net-return series; numpy and
   pandas paths agree to floating-point precision.

5. **No kill criterion fired**. Value-destruction kill threshold required
   2/3 ds with comp-Sharpe < iter011-0.10 — only xauusd_intraday hit that
   (1/3, kill not fired). DSR no-progress kill required gld_long not
   passing AND xauusd_real degrading by ≥0.020 — gld_long didn't pass but
   xauusd_real degraded only +0.002, so kill not fired. Total gates
   18/21 well above the 14/21 collapse threshold.

## What didn't work

1. **gld_long DSR did NOT cross below 0.05**. The composition's primary
   objective. p=0.201 vs threshold 0.05 — almost an order of magnitude
   away. The diagnostic insight is that iter 003 standalone has
   gld_long DSR p ≈ 0.30 (per iter 003 verdict), and iter 011 standalone
   has p = 0.275. **Combining two streams that individually fail DSR
   cannot lift either above the threshold via correlation reduction alone**
   — DSR penalty depends primarily on the combined Sharpe + variance, and
   the combined gld_long Sharpe (+0.542) is only marginally above iter 011's
   standalone (+0.481). The +0.06 Sharpe lift × n_obs=5384 still fails
   to clear the 12-trial Bonferroni-Sharpe deflator.

2. **xauusd_intraday Sharpe degraded by −0.17** because daily resampling
   throws away the per-1h-bar Sharpe density. iter 011's 1h Sharpe is
   computed at 1h frequency: Sharpe_1h × √5119 = 1.59. Daily aggregate of
   iter 011's 1h returns recovers daily Sharpe ≈ 1.42 (consistent with
   xauusd_real's daily Sharpe). The composition can only operate at the
   common frequency — daily — so the intraday-specific Sharpe gain is
   lost. This is **the structural cost** of cross-frequency composition:
   you can only combine at the slowest common timeframe.

3. **CAGR regressed across all 3 ds vs iter 011 standalone**. iter 011 had
   CAGR 4.80 / 14.15 / 14.24%; iter 012 has 2.87 / 12.86 / 11.81%. The
   composition is **flat ~70% of time** (vs iter 011 alone ~50%) because
   both components require their respective triggers to be ON. iter 003's
   RSI(2)<5 signal fires sparsely (~5% of bars), so when iter 011's
   regime is OFF, iter 003 is mostly OFF too — capital sits idle. CAGR
   floor at 0/3 (vs iter 011 alone 0/3) is the same outcome but at a
   lower absolute level.

4. **Hold-time gate hard-fails** (weighted-avg 37.1d on xauusd_intraday).
   Composition inherits iter 011's slow-regime hold profile (90% weight),
   so day-swing mission's 5d gate is irrecoverable. **STRONG tier ceiling
   regardless of score**. Composition is mission-mismatch.

5. **No DSR compounding observed where it was hoped**. IC-7's promise
   (sister 045/046: ρ=0.41 → DSR 0.222→0.041 = −81%) requires both
   streams to have INDIVIDUALLY DSR-passing standalone profiles on the
   target dataset. iter 011 + iter 003 are both gld_long-failures
   standalone; combination gets you 0.275 → 0.201 (−27%), which is the
   right *direction* of IC-7 effect but at half the magnitude needed to
   cross the 0.05 line. **Lesson for future composition iters: at least
   one base must be DSR-passing standalone on every dataset where you
   want the composition DSR to pass.**

## Main lesson (for future iterations)

**IC-7 composition cannot manufacture DSR significance from two
DSR-failing components.** This is a fundamental constraint on the
sister-loop's IC-7 framework — the composition's Sharpe is
∼√(S_A² + S_B² − 2ρ·S_A·S_B) / √(1−ρ²) ≈ √(S_A² + S_B²) at low ρ, so
the combined Sharpe gain is bounded by the lower-Sharpe component's
quadrature contribution. With S_A=0.48 and S_B=0.30 on gld_long, the
combined ceiling is √(0.231 + 0.090) = √0.321 ≈ 0.567 — and that's
exactly what we measured (+0.542). The DSR deflator at n_trials=12
needs Sharpe > ~0.65 to clear p<0.05 on gld_long's n_obs=5384. **Neither
component reaches there individually, and the quadrature sum doesn't
either.**

**The right path for gld_long is not composition but a stronger single-stream
filter.** BASE_MEMORY direction #2 — inverse vol-regime AND price > SMA(200)
— directly addresses iter 011's 2013-2018 bear-stagnation leak. That's
**one parameter, one new DSR trial, structurally complementary** to the
existing iter 011 mechanism (regime filter on top of regime filter). It
should be iter 013.

**For xauusd_intraday**, the Sharpe loss from daily-resampling tells us
that 1h-frequency operation matters. Future intraday compositions need
either (a) a partner stream that natively operates at 1h or finer, or
(b) acceptance that the composition test is at daily resolution only.

## Structural finding (for DEAD_ENDS.md as GS-12)

GS-12 closes IC-7 composition of **iter 011 (vol_regime_inverse_60_252) +
iter 003 (RSI(2)+SMA(200))** on gold for the gld_long-DSR-uplift goal.
The Markowitz weights are well-behaved (no clamping, all positive),
ρ is correctly in IC-7 sweet spot (+0.09 to +0.10), and the streams are
truly orthogonal in mechanism — **but the combined Sharpe is bounded by
quadrature of components, and both components have weak gld_long DSR**.

**Closes**:
- IC-7 (iter 003 + iter 011) at full-sample Markowitz tangency on gld_long
  with goal = lift DSR p<0.05.
- Variants of the same composition at proportional-Sharpe (no covariance
  term) weighting (would give even more concentrated weights on iter 011
  on xauusd → less iter 003 effect).
- IC-7 composition of any pair where BOTH bases fail standalone DSR on
  gld_long; the deflated-Sharpe penalty cannot be rescued by correlation
  alone when standalone Sharpes are too low.

**Does NOT close**:
- IC-7 composition where at least one base IS DSR-passing on the target
  dataset (e.g., a future iter 011-improved with SMA(200) regime gate
  that gets gld_long DSR < 0.05 standalone, then combined with iter 003).
- 3-stream IC-7 (iter 010 asymmetric + iter 011 + iter 003) per
  BASE_MEMORY direction #3 — different statistical regime; needs its
  own iter.
- IC-7 with a fundamentally different second stream that has DIFFERENT
  Sharpe distribution across datasets (e.g., one that's STRONG on
  gld_long but weak on xauusd, complementing iter 011's STRONG-on-xauusd
  / weak-on-gld_long profile).
- Composition gates / per-dataset MDD / OOS robustness — composition
  delivered a real MDD halving on gld_long; the iter is informative for
  risk-management even if not winner-eligible.

## Citations used

- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 12 (PRIMARY).
  Empirically demonstrated: at n_trials=12 with gld_long n_obs=5384,
  Sharpe ≥ ~0.65 needed for p<0.05; combined +0.542 falls short.
- `[modern_portfolio_theory]` — Markowitz tangency formula `w = Σ⁻¹μ`
  (normalized). Correct formula behavior verified against numpy
  linalg.solve in TDD test_markowitz_unequal_volatility.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest. Composition
  layered on top of already-cost-included net returns; no double-cost
  charging.
- IC-3 (sister iter 049) — 50/50 only when Sharpes similar; here Sharpe
  ratio (xauusd) is 1.4/0.2 ≈ 7×, so 50/50 closed; Markowitz proper
  required and used.
- IC-7 (sister iter 045/046) — out-of-family corr<0.50 compounds DSR.
  **Boundary condition discovered**: requires standalone DSR-passing
  component(s) on the target dataset; cannot manufacture DSR from two
  non-passing components.
- IC-8 (sister iter 046/047/050) — single pre-committed cfg; deflator
  increment from 11 → 12 contributed ~10% to the xauusd_real DSR p
  rise from 0.018 → 0.020.
- `[short_term_trading_strategies, p.105-118]` — iter 003 component basis
  (Connors RSI(2)+SMA(200) trend filter). Used unchanged.
- `[volatility_trading, p.58-59]` — iter 011 component basis (Sinclair
  vol cone σ_60<σ_252). Used unchanged.
- `[trading_systems_methods, p.13-14]` — Kaufman metals = low-noise →
  trending; iter 011 directional choice. Used unchanged.

## Next iteration suggestions (priorities updated by this iter's findings)

**Iter 012 outcome closes the IC-7 composition path for these specific
bases.** Future iter directions, in priority order:

1. **(NEW PRIORITY 1) iter 011 + SMA(200) regime gate on gld_long**
   (BASE_MEMORY direction #2, now PROMOTED to top after iter 012).
   `position[t] = 1 iff (σ_60 < σ_252) AND (close > SMA_200)`. Targets
   gld_long's 2013-2018 bear-stagnation leak directly. **One new
   parameter, one new DSR trial**. Hypothesis: gld_long DSR < 0.05
   standalone via lifting the strategy out of bear-regime drift. If
   this works, gld_long becomes the 3rd dataset with DSR-passing
   standalone — and ALL 5 strict winner conditions (except hold-time)
   become satisfied. STRONG tier likely; STRONG-with-swing-extended
   per the hold-time hard gate.
2. **(PRIORITY 2) Asymmetric vol regime — σ_60>σ_252 AND drawdown_60d<10%**
   (BASE_MEMORY direction #3). Completes the partition: separate
   vol-expansion-up from vol-expansion-down. If both halves of the
   high-vol side pass standalone, a 3-stream IC-7 (asymmetric-up-half,
   iter 011, iter 003) might compound where 2-stream didn't (more
   diversification, more orthogonal signals).
3. **(PRIORITY 3) Same iter 003 + iter 011 composition with
   cost-aware-realistic re-fit weights** (rolling Markowitz on 1y
   trailing window, OOS-style). Could rescue some of the in-sample-fit
   penalty in the n_trials=12 DSR deflator. But same fundamental
   ceiling: combined Sharpe bounded by quadrature; gld_long doesn't
   reach 0.65. Lower priority because (1) above directly addresses the
   gld_long bottleneck.
4. **(PRIORITY 4) DXY directional / TIPS DFII10** (BASE_MEMORY directions
   #5-6, frozen earlier as macro). With iter 011 as a STRONG xauusd base
   stream now, a fundamentally-different macro stream (gold ↔ real-yields
   inverse correlation) could be the IC-7 second component for xauusd
   compounding (where iter 003 added zero). This is a multi-iter
   investment because TIPS DFII10 needs FRED fetch first.

iter 013 should pursue priority #1.
