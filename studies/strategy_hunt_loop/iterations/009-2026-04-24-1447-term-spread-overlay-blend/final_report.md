# Iteration 009 — Final Report

**Date:** 2026-04-24 14:47
**Hypothesis:** Term-spread (T10Y3M) binary-haircut macro overlay on iter 008's
single-cfg vol-managed SPY+TLT blend (`vt15_L21_cap20 + ts_inv21_h50`).
**Cumulative n_trials after iter 009:** 4243.

---

## Verdict

🥈 **PROMISING** (score **64/100**, winner_conditions_met=False, winner conditions 1/5).

**Kill criterion #3 TRIGGERED** — score 64 < 65 threshold. The overlay
is marginally harmful per the pre-committed threshold (score regresses
from iter 008's 74 → 64, Δ−10 pts). Three of five winner conditions
(Sharpe edge, gate battery, DSR) REGRESSED or held flat vs iter 008;
two (CAGR floor, MDD ceiling) held at 3/3.

The failure mode is **not catastrophic** — Sharpe regression is
bounded to Δ−0.02 / −0.01 / −0.03 on spy / ndx / educational; Kill #1
(Sharpe regression > 0.05 on real data) did NOT fire, and all datasets
stayed in 6/7 gates-passing territory. But the overlay fails the
primary claim of the iteration (push score ≥ 75 or push DSR through),
so the hypothesis as specified is **rejected for the iter 009 scope**.

---

## Headline metrics (pre-committed combined cfg `vt15_L21_cap20+ts_inv21_h50`)

| dataset | Sharpe (Δ vs bench) | Sharpe Δ vs iter 008 | CAGR | MDD | gates | DSR p |
|---|---|---|---|---|---|---|
| educational | 0.836 (+0.175) | **−0.029** | 12.06% | 36.09% | **6/7** | 0.340 |
| spy_real    | 0.979 (+0.079) | **−0.021** | 14.26% | 36.09% | **6/7** | 0.363 |
| ndx_real    | 1.007 (+0.052) | **−0.014** | 16.00% | 37.21% | **6/7** | 0.350 |

Benchmarks: edu custom SPY b&h 2002-07-29 → 2026-04-15 (Sharpe 0.662);
spy_real frozen SPY b&h Tiingo (Sharpe 0.900); ndx_real frozen QQQ b&h
Tiingo (Sharpe 0.955). Cumulative n_trials 4243.

Benchmark comparisons:

- **Sharpe edge**: edu Δ+0.175 (PASS +0.10 gate); spy Δ+0.079 (FAIL
  +0.10); ndx Δ+0.052 (FAIL +0.10). **Only 1 of 3 datasets clears
  +0.10 gate** vs iter 008's 2 of 3.
- **CAGR floor** (0.8 × bench): edu 12.06% > 8.9% PASS; spy 14.26% >
  12.0% PASS; ndx 16.00% > 15.3% PASS. **3/3 — held vs iter 008.**
- **MDD ceiling** (bench + 5pp): edu 36.1% ≤ 60.1% PASS; spy 36.1% ≤
  38.7% PASS; ndx 37.2% ≤ 40.1% PASS. **3/3 — held vs iter 008.**

## Gates breakdown (detailed)

| gate | educational | spy_real | ndx_real |
|---|---|---|---|
| G1 PBO | PASS (N=1 vacuous) | PASS (N=1 vacuous) | PASS (N=1 vacuous) |
| G2 DSR | FAIL (p=0.340) | FAIL (p=0.363) | FAIL (p=0.350) |
| G3 WF 6/8 | PASS (6/8) | PASS (7/8) | PASS (7/8) |
| G4 OOS 70/30 | PASS (+0.446) | PASS (+0.127) | PASS (+0.089) |
| G5 FWD post-2020 | PASS (+0.242) | PASS (+0.242) | PASS (+0.302) |
| G6 boot 99.9% CI | PASS (+0.178) | PASS (+0.195) | PASS (+0.194) |
| G7 cross-lib ±3pp | PASS (0.07 pp) | PASS (0.03 pp) | PASS (0.04 pp) |
| **total** | **6/7** | **6/7** | **6/7** |

**DSR slightly degraded** vs iter 008 (0.291 / 0.332 / 0.329 → 0.340 /
0.363 / 0.350). Direction is wrong — the overlay was supposed to move
DSR favourably via Sharpe uplift, but Sharpe slipped instead.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **10** | 25 | only 1 dataset beats +0.10 (down from 2 in iter 008); Δ−10 pts |
| 2 Gates | 19 | 25 | 6/6/6 same as iter 008; cross-dataset thresholds met; +4 bonus |
| 3 DSR | 0 | 15 | worst p 0.363 (iter 008 was 0.332) |
| 4 CAGR floor | 15 | 15 | 3/3 datasets pass |
| 5 MDD ceiling | 15 | 15 | 3/3 datasets pass |
| 6 Robustness | 5 | 5 | 9/9 sub-windows Sharpe > 0 (matches iter 008) |
| **total** | **64** | 100+5 | tier: **PROMISING** (one point below Kill #3 threshold) |

Delta vs iter 008: −10 pts. The full regression is concentrated in
**criterion 1 (Sharpe edge): 20 → 10**. All other criteria flat. DSR
would have flipped 5 pts favourably if worst_p had dropped below 0.20
(iter 008's 0.332 was already below; iter 009's 0.363 is still below
0.20-threshold boundary, but slightly worse — no change in DSR
crediting). Robustness unchanged at full 5/5.

## Winner conditions

| condition | met? | details |
|---|---|---|
| 1. Sharpe ≥ bench + 0.10 on ≥ 2/3 | **NO** | 1/3 (educational only) |
| 2. Gate battery cross-dataset | **YES** | edu 6/7≥5, spy 6/7≥4, ndx 6/7≥4 |
| 3. DSR worst p < 0.05 | **NO** | worst p = 0.363 |
| 4. CAGR floor on ≥ 2/3 | **YES** | 3/3 pass |
| 5. MDD ceiling on ≥ 2/3 | **YES** | 3/3 pass |

**Winner conditions: 3/5** (vs iter 008's 4/5). Regression of 1 (Sharpe
edge condition flipped from MET at 2/3 to UNMET at 1/3).

---

## Orthogonality pre-check diagnostic (post-mortem)

The hypothesis rested on the claim that T10Y3M macro signal is
*structurally orthogonal* to realized equity vol (iter 007's redundancy
limit). Diagnostics post-run:

| dataset | gate fire-rate | ρ(gate, blend_scale) | overlap with bottom-20% blend scale |
|---|---|---|---|
| educational | 16.3% | **+0.069** (low) | **100.0%** (fully redundant) |
| spy_real    | 17.8% | **+0.144** (low) | **100.0%** (fully redundant) |
| ndx_real    | 18.5% | **+0.221** (mod) | 40.3% (partially additive) |

**The low ρ(gate, scale) = +0.07 to +0.22 is MISLEADING.** It measures
linear correlation between a near-constant gate (1.0 most of the time)
and smooth blend_scale, which is insensitive to the *timing* of gate
fires. The informative diagnostic is **overlap with bottom-20% of
blend scale**:

- On educational and spy_real: **100% of gate-fire bars coincide with
  bars already in the bottom 20% of blend scale.** The blend had
  already de-levered naturally; the overlay only halves exposure a
  second time on bars where the blend was already conservative.
- On ndx_real: 40.3% overlap — gate fires during 60% of bars where
  the blend was NOT yet de-levering. This IS additive information,
  but on this tech-heavy universe the information is mistimed.

**Mechanism explanation**: The 21-day EMA smoothing we pre-committed
(to emulate Estrella-Mishkin's monthly-data regime) effectively
**erased the 6-18 month leading property** of the raw T10Y3M series.
By the time EMA21(T10Y3M) inverts, realized SPY / QQQ volatility is
already rising — which is exactly when the blend's σ²_port starts
climbing and variance-scaling de-levers. Result: both mechanisms fire
(nearly) concurrently; the overlay adds no early-warning information,
only duplicates the de-lever magnitude.

The four candidate yield-curve inversion episodes in the windows —
~2006-07, 2019 (brief), 2022 (mid-year), 2023 — all coincided within
1-2 months with realized SPY vol regime shifts visible to a 21-day
variance estimator. So the pre-committed smoothing destroyed the
ex-ante orthogonality claim. Raw (un-smoothed) T10Y3M might retain
more of the lead — but its daily-noise flipping around zero would
produce untradable whipsaw on the daily rebalance.

## Kill criteria post-mortem

- **Kill #1 (regression > 0.05)**: NOT triggered. spy Δ=−0.021,
  ndx Δ=−0.014 — both well within the 0.05 tolerance.
- **Kill #2 (CAGR drag < 0.75 × bench)**: NOT triggered. 3/3 datasets
  held above 0.80 × bench (stricter floor than the kill).
- **Kill #3 (score < 65)**: **TRIGGERED** (score = 64, exactly 1 pt
  below). Hypothesis rejected per pre-commit.
- **Kill #4 (WF < 5/8)**: NOT triggered. WF 6/7/7 across datasets.

Only Kill #3 fires — the one tailored to catch "overlay didn't add
value." This is the correct failure mode given the empirical evidence:
not catastrophic harm, but consistent 1-3% Sharpe + 1-2 pp CAGR drag
across all 3 datasets.

---

## What worked / what didn't

**What worked** (kept):

- **Cross-dataset structural soundness** — the combined mechanism
  passed 6/7 gates on all 3 datasets. No dataset broke. The 10 points
  lost are all on Sharpe edge magnitude, not on gate failures.
- **Robustness unchanged** — 9/9 sub-window Sharpe-positive held from
  iter 008. The overlay doesn't destabilise sub-windows.
- **MDD reduction** — edu MDD 36.1% (iter 008: 37.2%) is slightly
  *better* than iter 008 (Δ−1.1 pp). ndx MDD unchanged. spy MDD Δ−1.1
  pp — overlay DOES reduce drawdowns, just at cost that exceeds the
  risk-adjusted benefit.
- **Pre-committed cfg discipline** — one overlay cfg with 4 independently
  literature-anchored params (threshold=0.0 Estrella-Mishkin, haircut=0.5
  Carver tier-2, smoothing=21 monthly emulation, lag=1 AFML) — zero
  post-hoc tuning. The kill-criteria framework fired exactly as
  designed when the mechanism failed to deliver.
- **G7 cross-lib parity** — numpy reference agrees with pandas engine
  to 0.03-0.07 pp CAGR on all 3 datasets — confirms implementation
  correctness despite the mechanism's failure.

**What didn't work** (and why):

- **Orthogonality claim empirically false on this window + smoothing.**
  T10Y3M is canonically a 12-month leading indicator, but the
  pre-committed 21-day EMA smoothed the signal into a concurrent
  (not leading) state against realized vol. Result: the overlay fires
  during bars the blend is already de-leveraging on its own (100%
  bottom-20% overlap on 2/3 datasets).
- **Symmetric haircut on both legs.** Halving the bond leg during
  recession is counterproductive — bonds typically rally during
  equity crashes (ρ_stockbond −0.30). Asymmetric treatment (halve
  equity leg only, keep bond leg at full weight) might have
  preserved flight-to-quality, but this is a post-hoc hypothesis and
  cannot be tested within iter 009's pre-commitment.
- **Binary gate vs continuous.** A binary step loses information at
  the threshold boundary. A sigmoid-style soft gate would spread the
  haircut over a threshold band but adds 2-3 new pre-commit params
  (band width, curvature) — violates the single-cfg discipline.

---

## Main lesson (for future iterations)

**Macro overlays on vol-managed blends must preserve the signal's
LEADING property to be orthogonal.** The 21-day EMA smoothing on
T10Y3M — chosen ex-ante to emulate Estrella-Mishkin's monthly
frequency — erased the 6-18 month recession lead-time that is the
entire reason T10Y3M is canonically valuable. After smoothing, the
signal fires nearly concurrently with realized-vol regime shifts,
which the blend's variance-scaling (σ²_port) was already capturing.

**Structural principle for DEAD_ENDS.md (grid-design, not mechanism-
kill)**: Binary T10Y3M gates at threshold=0, haircut=0.5, with
monthly-scale smoothing (≥ 21 days) on a vol-managed 2-asset blend
produce score regression of ~10 pts vs un-gated iter 008 baseline.
The macro signal itself (T10Y3M as recession predictor) is NOT dead —
the combination of (a) smoothing scale ≥ 21 days, (b) binary threshold
at 0, and (c) symmetric haircut on equity + bond legs is. Three
distinct tweaks might un-kill this family:

1. **Raw (or 5-day) T10Y3M**: preserves lead property at cost of
   whipsaw.
2. **Asymmetric haircut** (halve equity leg only, keep bond leg 1.0):
   respects flight-to-quality.
3. **EBP overlay** instead of T10Y3M: Gilchrist-Zakrajšek excess bond
   premium `[data/external/macro/ebp_monthly.parquet]` captures credit-
   cycle risk that is structurally distinct from yield-curve slope.

All three are *untested iter 010+ candidates*, not dead-ends.

## Structural dead-ends discovered

Appending to `DEAD_ENDS.md`:

```markdown
## From iteration 009 — T10Y3M binary-haircut overlay on vol-managed SPY+TLT blend

### What failed (do NOT re-test)

1. **T10Y3M binary gate (threshold=0, haircut=0.5, smoothing=21 days)
   as a macro overlay on iter 008's single-cfg vol-managed SPY+TLT
   blend.** Score regressed 74 → 64 (−10 pts); Sharpe Δ−0.01 to
   −0.03 across all 3 datasets; 100% overlap with blend's own
   bottom-20% scale bars on edu + spy (gate fires only during bars
   the blend is already conservative).

2. **Monthly-scale smoothing (≥ 21 days EMA) on any macro leading
   indicator that derives its value from LEAD time.** The smoothing
   erases the lead; the smoothed signal correlates with concurrent
   realized vol, which the vol-managed blend already sees.

### Don't re-test

- T10Y3M binary-haircut overlay with threshold=0, haircut=0.5, and
  smoothing ≥ 21 days on any vol-managed 2-asset blend. Variants of
  this family are structurally similar enough to share the dead-end.
- EMA-smoothed macro signals (CAPE, EBP, T10Y3M, VIX) at smoothing
  windows ≥ 21 days on any vol-managed portfolio base — smoothing
  destroys what makes these signals valuable.

### Path forward (NOT dead)

- Raw (or ≤ 5-day smoothed) T10Y3M with *asymmetric* haircut (equity
  only, bond leg unchanged) — preserves lead-time at cost of whipsaw,
  respects flight-to-quality.
- **EBP overlay** on iter 008 blend — monthly-sampled Gilchrist-
  Zakrajšek excess bond premium, captures credit-cycle risk distinct
  from yield-curve slope.
- **3-asset blend extension** (SPY+TLT+GLD) — Option D in iter 008's
  ## Paths forward; structural extension rather than overlay.
- **Meta-labeling** (AFML ch.3) — secondary ML model predicts bar-
  level profitability of blend using cross-sectional + macro
  features. Orthogonal by construction.
```

## Citations used

**Books (absorbed knowledge base)**:

- `[regime_change, p.5-6, ch.2]` (Chen & Tsang 2020) — Regime Change
  framework, 2-state paradigm for macro indicators.
- `[quant_trading_chan, p.25, p.104, p.119-126]` — regime shift
  definition; Chan's skepticism of Markov-switching, openness to
  data-observable turning points.
- `[risk_parity, p.10-11, ch.1]` — naïve risk parity (inverse
  variance weighting) inherited from iter 006/008 base.
- `[systematic_trading, p.144, ch.9]` — tier-2 half-exposure de-lever
  (haircut = 0.5 anchor).
- `[systematic_trading, p.170-171, ch.11]` — IDM cap ≤ 2.5
  (max_leverage = 2.0).
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag; extended here to
  T10Y3M_{t-1}.
- `[advances_fin_ml, p.208-211]` — G1 PBO via CSCV; N=1 vacuous PASS.
- `[advances_fin_ml, p.222-223]` — G2 DSR with cumulative n_trials.
- `[advances_fin_ml, p.31-34]` — G7 cross-lib parity.
- Moreira & Muir (2017), *JoF* 72(4) DOI
  [10.1111/jofi.12513](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12513)
  — variance-scaling form (inherited).

**External (term-spread literature)**:

- Estrella & Mishkin (1998). *Review of Economics and Statistics* 80(1).
  Foundational 10Y-3M recession predictor.
- Estrella & Hardouvelis (1991). *Journal of Finance* 46(2) — earlier
  foundational term-structure / economic-activity work.
- Engstrom & Sharpe (2019) Fed FEDS note — modern refinement;
  near-term forward spread superior to 10Y-3M. Iter 009 used 10Y-3M
  (academic canonical).
- NY Fed recession-probability model (Estrella-Trubin 2006
  methodology).

## Next iteration suggestions

Iter 009 falsifies the specific Option B variant (monthly-smoothed
T10Y3M binary haircut, symmetric across legs). Three structurally
different directions remain live for iter 010:

1. **[OPTION B' — REFINED]** Asymmetric T10Y3M overlay. Haircut applied
   to equity leg only; bond leg keeps full weight (respects
   flight-to-quality during recessions). Smoothing reduced to 5-day
   or raw (preserves lead). Expected Sharpe uplift +0.03-0.08 if the
   asymmetry isolates the benefit. Single ex-ante cfg, preserves
   N=1 PBO.

2. **[OPTION D — STRUCTURAL]** 3-asset vol-managed SPY+TLT+GLD blend.
   Inverse-variance weighting extended to 3 legs with IDM cap ≤ 2.5.
   Gold adds real-asset / inflation factor with near-zero correlation
   to both. Different asset structure = different diversification
   return axis. Pre-committed single cfg.

3. **[OPTION E — ORTHOGONAL SIGNAL]** EBP (excess bond premium,
   Gilchrist-Zakrajšek 2012) overlay on iter 008 blend. Monthly
   data → one signal value per month, applied at month-end rebalance.
   Credit-cycle risk is structurally distinct from yield-curve
   slope — likely more orthogonal to realized vol than T10Y3M under
   smoothing.

Picking order for iter 010 (by expected information gain): **Option D
first** (3-asset structural extension is more likely to break
the DSR-unreachable ceiling than another overlay attempt);
**Option B'** if Option D also fails; **Option E** third.

The overall hunt-loop picture after iter 009: **iter 008's 74/100
remains the hunt-loop high.** DSR is still the unreachable gate at
cumulative_n_trials ≳ 4240; no overlay tried to date (momentum in
iter 007, term-spread in iter 009) has pushed Sharpe uplift toward
the +0.30 magnitude the deflator requires. The productive path is
structural extension (3-asset blend), not more overlays.
