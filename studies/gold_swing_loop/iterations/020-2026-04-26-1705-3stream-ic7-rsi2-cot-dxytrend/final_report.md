# Iteration 020 — Final Report

## Verdict

📉 **NEAR_FAIL** (score **35/100**, winner_conditions_met=False,
hold_time_gate=PASS, **kill #3 (DSR no-progress) AND kill #4 (IC-6
rolling-ρ on 003-015 pair) BOTH FIRED**)

The 3-stream IC-7 Markowitz tangency on iter 003 RSI MR + iter 018 COT
z-score + iter 015 DXY-MA-slope trend gate **achieved ~93% of its
analytical ceiling** (combined Sh +0.4865 on gld_long vs predicted
√(0.299² + 0.352² + 0.240²) = 0.520) and **set the loop's lowest-ever
MDD at 9.76% on xauusd_real** (gld_long 10.95% is also runner-up). But
two pre-committed kills fired:

- **Kill #3 (DSR no-progress, p > 0.20)**: combined p = 0.3646 at
  n_trials=20. This is technically *better* than iter 019's standalone
  p = 0.4055, but the marginal Sharpe lift from adding the 3rd stream
  (+0.028 on gld_long) is insufficient to offset the n_trials=20
  Bonferroni deflator growth, and remains far from the G2 threshold.
- **Kill #4 (IC-6 rolling-ρ pre-val on PRIMARY)**: the (003, 015)
  pair on gld_long shows |ρ_60d| > 0.30 on 21.9% of overlapping bars
  (459/2093) — exceeding the 20% IC-6 limit. This is the **first
  iteration in which a composed pair fails IC-6 on the primary
  dataset**. The static ρ ≈ +0.17 is regime-stable on average but
  drifts above 0.30 in long stretches (likely 2008 GFC, 2011 peak,
  2020 COVID) when both signals respond to the same dollar-weakness
  + risk-off compound regime.

GS-20 closes 3-stream IC-7 within the iter 001-019 catalog: any
addition of a third "low-ρ static" stream that turns out to have
non-stationary rolling ρ exposes IC-7 to a regime-correlation breakage
that destroys the diversification predicate.

## Headline metrics (NET of Pepperstone CFD costs, all components pre-deducted)

| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | weighted hold |
|---|---|---|---|---|---|
| gld_long (PRIMARY)         | **+0.4865** (Δ −0.198) | +2.06% (Δ −9.26) | **10.95%** (Δ −34.6 ↓ better) | **5/7** | 26.30 d |
| xauusd_real (CORROBORATING) | +0.4422 (Δ −0.596) | +1.86% (Δ −18.07) | **9.76%** (Δ −10.6 ↓ better, loop-best) | 4/7 | 33.80 d |

Bench (measured iter 001):
- gld_long: Sh 0.6844, CAGR 11.32%, MDD 45.56%
- xauusd_real: Sh 1.0382, CAGR 19.93%, MDD 20.36%

Per-dataset gate detail (gld_long PRIMARY):
- G1 PBO: PASS by IC-8 convention (single cfg, PBO degenerate)
- G2 DSR p = 0.3646 (n_trials=20) → **FAIL**
- G3 Walk-Forward 6+/8 windows → **PASS**
- G4 OOS 70/30 Sharpe > 0 → **PASS**
- G5 FWD post-2022 Sharpe > 0 → **PASS**
- G6 Bootstrap 99.9% CI low > 0 → **PASS**
- G7 Cross-lib ±3 pp CAGR → **PASS**

Per-dataset gate detail (xauusd_real CORROBORATING):
- G1 PASS (convention), G2 FAIL (p=0.7728), G3 PASS, G4 PASS,
  G5 PASS, G6 PASS, G7 PASS — **4/7**

IC-6 pre-val rolling-60d ρ exceedance per pair on PRIMARY (gld_long):
- (003, 018): 1.5% (32/2191) — PASS [3rd confirmation]
- (003, 015): **21.9%** (459/2093) — **FAIL** ← **kill #4**
- (018, 015): 18.0% (435/2412) — PASS

On CORROBORATING (xauusd_real):
- (003, 018): 0.0% (0/912) — PASS
- (003, 015): **29.6%** (193/653) — FAIL [primary already kills]
- (018, 015): 15.3% (105/688) — PASS

## Score breakdown (v2 scoring, rules_version=2026-04-26-relaxed-r1)

| criterion | points | max | detail |
|---|---:|---:|---|
| 1 Sharpe edge | 5 | 25 | primary not beat (Δ −0.198); corroborating Sh +0.442 > 0 → +5 |
| 2 Gates | 15 | 25 | primary 5/7 ≥ 5 → +15; corroborating fails G2 (p=0.77) → no +5 |
| 3 DSR | 0 | 15 | primary p=0.3646 (n_trials=20) |
| 4 CAGR floor | 0 | 15 | primary 2.06% < 0.8 × 11.32% = 9.06% → FAIL |
| 5 MDD ceiling | 15 | 15 | primary 10.95% ≤ 50.6% → PASS by 39.6 pp |
| 6 Robustness bonus | 0 | 5 | not computed |
| **total** | **35** | **100+5** | tier: **NEAR_FAIL** |
| (hold-time gate) | PASS | — | 26.30 d ∈ medium_swing [10, 30] |

## Configuration tested (single cfg, IC-8)

```yaml
cfg_id: ic7_3stream_iter003_iter018_iter015_markowitz_gld_primary
method: markowitz_tangency_full_sample_3asset
iter_003_cfg: connors_rsi2_sma200_filter
iter_015_cfg: dxy_sma_slope_falling_200_20_long_only
iter_018_iter: 018-2026-04-26-1628-cot-zscore-variant
weights:
  gld_long:    {w_iter_003: 0.547, w_iter_018: 0.320, w_iter_015: 0.133, clamped: false}
  xauusd_real: {w_iter_003: 0.346, w_iter_018: 0.434, w_iter_015: 0.220, clamped: false}
declared_primary: gld_long
declared_corroborating: [xauusd_real]
broker_track: pepperstone_cfd
universe: single_xau
hold_time_track: medium_swing
ic6_pre_val_3pair:
  rolling_rho_window: 60
  rolling_rho_limit: 0.30
  exceed_frac_limit: 0.20
  primary_per_pair_exceed_frac:
    (003, 018): 0.015  # PASS
    (003, 015): 0.219  # FAIL ← kill #4
    (018, 015): 0.180  # PASS
```

Cumulative `n_trials` 19 → **20** (this iter increments by 1; IC-8
honored — single 3-asset Markowitz tangency cfg pre-committed, no
grid).

## What worked / what didn't

**Worked**:

1. **3-stream IC-7 closed-form ceiling validated empirically.**
   Predicted gld_long combined Sh ≤ √(0.299² + 0.352² + 0.240²) =
   0.520; observed 0.4865 (93.6% of theoretical max). Iter 019 hit
   99.7% on its 2-stream pair; the 3-stream is slightly farther from
   ceiling because pairwise ρ are non-zero (rho_003_015 = +0.170 and
   rho_018_015 = +0.087 vs iter 019's 003-018 ρ = +0.013), so the
   diagonal-Σ approximation overshoots the achievable ceiling.
   `[advances_fin_ml, p.222-223]` formula is again descriptively
   accurate.
2. **Loop's lowest-ever MDD on a corroborating dataset**: xauusd_real
   9.76% (vs bench 20.4%) — a 10.6 pp drag-compression. Combined with
   gld_long's 10.95%, the 3-stream tangency builds the **best
   risk-of-loss profile in the loop's history at any tier**, by a wide
   margin. The diversification math is real; the regime concerns
   below are the cost.
3. **Markowitz weights are well-conditioned**: no clamp on either
   dataset; weights reasonable on both (gld_long: 003 = 0.55, 018 =
   0.32, 015 = 0.13; xauusd_real: 003 = 0.35, 018 = 0.43, 015 = 0.22).
   The 3-asset solver works as expected.
4. **Hold-time bucket matches declaration**: weighted-avg 26.30d ∈
   medium_swing [10, 30] PASS. (This was a pre-iter risk in the
   hypothesis — predicted ~33d would have downgraded to NEAR_FAIL by
   gate; the actual ~26d fits comfortably.)
5. **WF gate PASS** on both datasets (6+/8 windows). The composition's
   MDD compression carries through to per-window selection.
6. **TDD pre-implementation passed cleanly** (12 tests; all pass):
   3-asset tangency identity `Σw ∝ μ`, equal-μ identity-covariance
   equal-weights, corner-clamp for negative weights, triple
   inner-join NaN-handling, schema A/B loaders.

**Didn't work**:

1. **DSR no-progress kill #3 fired again.** Combined p = 0.3646 at
   n_trials=20. Marginal improvement vs iter 019's 0.4055 standalone,
   but ~7× too high vs G2 threshold p < 0.05. The Bonferroni deflator
   `SR₀(n_trials)` growth from 19 → 20 trials adds ~0.005 to required
   SR; the 3rd-stream Sharpe lift (+0.028) is below this growth rate.
   GS-19's prediction holds: the existing catalog can't reach DSR <
   0.05 within the n_trials regime.
2. **IC-6 rolling-ρ pre-val on PRIMARY (003, 015) FAILED.** 21.9%
   exceed-fraction (459/2093 60d windows on gld_long) → first
   loop-iter where the pre-val gate fails on the primary dataset. The
   static ρ ≈ +0.17 reported earlier (iter 015 ic7_diagnostic) is the
   AVERAGE; the 21-year window has substantial regime-driven episodes
   where both RSI MR (entries triggered by gold drawdowns) and DXY-MA-
   slope falling (signal triggered by dollar weakness) coincide
   (e.g., 2008 GFC liquidity crisis, 2011 sovereign-debt spike, 2020
   COVID). When they coincide, the diversification benefit collapses
   structurally. Iter 019's 003-018 pair did not have this issue
   because COT z-score and price-MR are mechanistically decoupled
   (futures positioning is weekly survey-derived, RSI is 2-bar price
   oscillation).
3. **Primary Sharpe edge gap unclosed.** Combined 0.4865 vs target
   bench + 0.10 = 0.7844 → still trails by 0.30. Even the analytical
   3-stream ceiling 0.520 is below 0.7844 — **no 3-stream
   construction within this catalog can clear winner condition #1
   on gld_long**. This is a mathematical-not-empirical closure.
4. **CAGR floor gap is large.** Combined 2.06% vs target 9.06% (0.8×
   bench). Same explanation as iter 019: the high-Sharpe / low-MDD
   profile is a *risk-adjusted* edge; absolute returns are small
   because the composite spends most calendar time near zero net
   exposure (RSI MR is rare, COT z-score gates ~25% of bars, DXY
   trend gates ~30% of bars; the union with weights is sparse).
5. **Corroborating xauusd_real does not clear relaxed gates** (G6 ✓
   but G2 DSR p=0.77). Same short-history limitation as iter 019.
6. **Score did not exceed iter 018/019's 35.** Three iterations now
   tied at the loop's NEAR_FAIL ceiling. The 3-stream additionally
   broke IC-6 on PRIMARY — a structurally new failure mode within
   the 003/018/015 catalog.

## Main lesson (for future iterations)

**GS-20 — 3-stream IC-7 closure on gold within the existing 19-iter
catalog**: extending iter 019's IC-7 003+018 pair with iter 015 DXY
trend as a 3rd stream **simultaneously fails DSR (kill #3) AND
fails IC-6 rolling-ρ pre-val on the PRIMARY dataset (kill #4)** —
the latter is qualitatively new vs iter 019. Combined Sh +0.4865 on
gld_long is 93.6% of analytical ceiling √(S₀₀₃² + S₀₁₈² + S₀₁₅²)
= 0.520, but the (003, 015) rolling-60d ρ exceedance at 21.9% (vs
20% IC-6 limit) reveals that the static ρ +0.17 measured under
GS-16's frequency-corrected diagnostic was an *average* — the
21-year sample contains substantial regime-driven episodes where
RSI-MR and DXY-trend coincide (likely 2008/2011/2020), erasing the
diversification predicate intermittently. The pair is "low-ρ in
expectation but regime-correlated in stress" — the worst possible
profile for IC-7 because the diversification benefit is highest in
the regimes where the gate fires.

**This means**:

- 2-stream IC-7 on gold within iter 001-019 catalog: closed by GS-19
  (DSR ceiling, ρ orthogonal).
- 3-stream IC-7 with iter 015 DXY-trend as 3rd stream: closed by
  GS-20 (DSR ceiling, IC-6 rolling-ρ pre-val fails on PRIMARY).
- 3-stream IC-7 with a *different* 3rd stream that has BOTH low
  static ρ AND stationary rolling-ρ: untested but unlikely within
  the existing catalog (iter 011 σ-regime, iter 013 σ-regime+SMA,
  iter 014 DFII10, iter 016 ic7-diag combo, iter 017 canonical Briese
  COT all measure pairwise ρ ≥ +0.20 with at least one of the 003/018
  pair, and several measured ρ > +0.50 to iter 011/014 — exceed IC-7
  upper bound).
- A WINNER on gld_long requires either (a) a genuinely new mechanism
  family delivering standalone Sh > 0.65, or (b) an IC-7 pair with
  both low static ρ AND stationary rolling-ρ on PRIMARY. Neither is
  visible within the closed dead-ends GS-1 to GS-20.

The path of least resistance for iter 021+ is to test **structurally
new mechanism families** (DCOT money-manager post-2009, CME GVZ
implied-vol regime, futures-track A2 cost re-evaluation) BEFORE
trying further IC-7 compositions. The DSR-deflator wall combined
with the IC-6 rolling-ρ failure suggests the catalog has been
exhausted for IC-7-style approaches.

## Structural dead-ends discovered

**GS-20** — *3-stream IC-7 Markowitz tangency of iter 003 (RSI(2)+SMA(200)
MR) + iter 018 (rolling-156w COT z-score) + iter 015 (DXY-MA-slope
falling 200/20 trend gate) at full-sample weights w_003=0.55 / w_018=0.32 /
w_015=0.13 on gld_long primary*: combined Sh **+0.4865** (93.6% of
analytical ceiling 0.520), CAGR +2.06%, MDD **10.95%** (xauusd_real
9.76% loop-best ever). Gates 5/7 + 4/7 (primary + corroborating);
DSR p **0.3646** (n_trials=20) > 0.05 — kill #3 fired (marginal lift
0.028 over 2-stream iter 019). **IC-6 rolling-60d ρ on (003, 015)
pair: 21.9% exceed on PRIMARY gld_long, 29.6% on corroborating
xauusd_real — both > 20% limit → kill #4 fired**. Hold time 26.30d
(weighted-avg) ∈ medium_swing PASS. Score 35 = NEAR_FAIL.

**Closes**: 3-stream IC-7 path on gold within the existing 19-iter
catalog when the 3rd stream has macro-FX origin (iter 015 DXY trend
family). The (003, 015) pair has low static ρ ≈ +0.17 but
non-stationary rolling-ρ — gold drawdown regimes (2008, 2011, 2020)
co-trigger both RSI-MR entries and DXY-MA-slope falling, breaking
the diversification predicate intermittently.

**Does NOT close**:

- 3-stream IC-7 with a different macro-orthogonal 3rd stream candidate
  IF such a stream exists with both low static ρ AND stationary
  rolling-ρ. None visible in iter 001-019 catalog (vol-regime/iter
  011 has static ρ +0.27 to iter 018 — borderline; positioning
  variants iter 017 same-family with iter 018 ρ > +0.80 — not
  IC-7-eligible).
- DCOT money-manager net longs (post-2009) — different stream, not
  yet tested. May exit the +0.35 single-stream plateau.
- CME GVZ implied-vol regime gate — options-derived family, not
  yet tested. Different from realized-vol (iter 011) and from
  positioning (iter 018).
- Genuinely new mechanism families (cross-asset risk-off, crypto-
  gold ρ, GDX-NEM proxy, microstructure 30m / 15m / 1m intraday
  via cTrader fetch).
- CME futures track A2 (1-2 bps spread) — re-test cost-dominated
  intraday MR families that died at 8 bps.

## Citations used

- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
  multi-asset tangency formula `w ∝ Σ⁻¹μ`; combined-Sharpe upper
  bound `S_combined ≤ √(Σ Sᵢ²)` for orthogonal streams.
- `[advances_fin_ml, p.31-34]` — cost realism (composition adds
  zero turnover; reuses pre-deducted Pepperstone CFD costs).
- `[risk_parity, ch.2]` — multi-asset efficient frontier; tangency
  generalization to N=3.
- `[short_term_trading_strategies, p.106]` — RSI(2) + SMA(200) MR
  base (iter 003 component).
- `[trading_systems_methods, p.639-640]` — COT z-score positioning
  (iter 018 component).
- `[trading_systems_methods, p.13-14]` — vol-regime + macro overlay
  conceptual grounding (iter 015 component family).
- de Roon, Nijman, Veld (2000) *Journal of Finance* — "Hedging
  Pressure Effects in Futures Markets" (z-score commercial net
  positioning theoretical anchor).
- IC-7 sister-loop empirical (`studies/strategy_hunt_loop/` 045/046)
  — out-of-family ρ < 0.50 + Markowitz proper compounds DSR.
- IC-3 sister-loop closure (049) — Markowitz proper, NOT 50/50/50,
  when Sharpes differ.
- IC-6 / GS-9 pre-val — rolling-ρ at PRIMARY dataset with 20% limit.
- IC-8 sister-loop closure (046) — single cfg per iter unless
  Bonferroni-justified.

## Correlation diagnostic (consistent daily granularity)

3-stream pairwise ρ on full-sample joined index:

| pair | gld_long static | gld_long 60d \|ρ\|>.30 frac | xauusd_real static | xauusd_real 60d \|ρ\|>.30 frac |
|---|---:|---:|---:|---:|
| (003, 018) | +0.0134 | 1.5% | +0.0043 | 0.0% |
| (003, 015) | **+0.1698** | **21.9%** ← kill | +0.2176 | 29.6% |
| (018, 015) | +0.0869 | 18.0% | +0.0450 | 15.3% |

The (003, 018) pair remains the loop's most thoroughly validated low-ρ
pair (4th confirmation now). The (003, 015) pair, despite low static
ρ +0.17, has **non-stationary rolling ρ** that exceeds 0.30 on 21.9%
of windows — IC-6 fail. The (018, 015) pair (COT z-score vs DXY trend)
is the next-best 2-pair candidate but borderline at 18.0% vs 20%
limit; its standalone Sharpes (S₀₁₈ ≈ 0.35, S₀₁₅ ≈ 0.24) cap a
2-stream IC-7 at √(0.35² + 0.24²) ≈ 0.42 — well below winner threshold.

## Next iteration suggestions

1. **(NEW PRIORITY 1) DCOT money-manager net longs (post-2009)** —
   replaces iter 018's legacy commercials bucket with the more
   refined "money-manager" speculative bucket. xauusd_real becomes
   natural primary (post-2009 cutoff = 2010+; gld_long downgraded
   to corroborating). Hypothesis: legacy commercials = miners hedge
   naturally short → producer-bucket signal partially anti-correlated
   with what we want; money-manager bucket isolates pure speculative
   flow. May exit the +0.35 single-stream plateau and provide a
   STRUCTURALLY DIFFERENT positioning signal that has both stationary
   rolling-ρ AND clean IC-7 candidate vs iter 003. Requires CFTC DCOT
   data fetch (separate). `[trading_systems_methods, p.640]`.

2. **(NEW PRIORITY 2) CME GVZ implied-vol regime gate** —
   options-derived family, FRED `GVZCLS` series 2008+. Different
   from realized-vol (iter 011) and from positioning (iter 018).
   Long when GVZ z-score < −1 (cheap implied vol → mean-revert
   into rising IV typical at gold rally starts). xauusd_real or
   post-2008 gld_long primary. May be IC-7-orthogonal to iter 003
   in a way iter 011/013 σ-regime aren't (different vol family
   entirely). `[volatility_trading]` (Sinclair).

3. **(NEW PRIORITY 3) CME futures track A2 — re-test cost-dominated
   intraday MR** — iter 007 z-MR died at 8 bps RT spread on
   xauusd_intraday (gross +3.5 bps, net −5+ bps). At CME GC futures
   1-2 bps RT spread (verified in INFRASTRUCTURE.md A2 model), the
   same z-MR signal has +1.5 to +2 bps net per trade — possibly
   intraday-MR-economic again. Track A2 strategies have tighter
   spread + 24h trading + DARF 15% (same as Inter ETF) but no
   long-only restriction. New cost-path branch.

4. **(LOWER PRIORITY) Concede loop closure** if PRIORITY 1-3 also
   flat-line. The mathematical argument is converging: PCBO/DSR
   with n_trials=20+ requires standalone Sh > 0.65 OR a IC-7 pair
   with both low static ρ AND stationary rolling-ρ; neither has been
   exhibited in 19 iterations; the absorbed-book + cached-data
   envelope is approaching exhaustion. A loop closure with detailed
   GS-N catalog and 19+ honest FAILs is a credible scientific
   product, fully aligned with mandate §1's MAINTENANCE 100% Plano C
   stance — research output, not deploy clearance.

The DCOT money-manager path (priority 1) has the highest informational
value: it directly tests whether positioning-family richness is
exhausted at iter 018's z-score variant, and it provides a
structurally different signal that (unlike DXY trend) does not
mechanistically co-trigger with RSI MR at gold drawdowns. The
n_trials=21+ test is still costly (DSR ceiling moves higher), but
DCOT's 17-year history (vs iter 015's 21y) gives partial corroboration.
