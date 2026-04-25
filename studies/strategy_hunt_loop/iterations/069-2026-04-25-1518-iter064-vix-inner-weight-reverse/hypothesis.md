# Iteration 069 — REVERSE VIX-cond INNER weight swap on iter 064 (calm `w_qqqt=0.05` / stress `w_qqqt=0.20`)

## Hypothesis

iter 068 ran the canonical "calm-trend, stress-defensive" inner-weight swap
on iter 064's two saved sub-streams (`r_046` risk-parity backbone +
`r_qqqt` Faber 2007 200d-SMA QQQ trend) — `w_qqqt_calm = 0.20`,
`w_qqqt_stress = 0.05`. That direction REGRESSED Sharpe by 0.04-0.05 vs
iter 064 on all 3 ds and KILL I fired with 3/3 misordered: **QQQ_TREND
Sharpe(stress) (0.95-1.20) is STRICTLY HIGHER than Sharpe(calm)
(0.71-0.76) on edu/spy/ndx**, and the same is true for `r_046`
(stress 1.43-1.93 > calm 1.05-1.09).

iter 069 directly tests the **opposite-direction** swap, motivated by
iter 068's empirical conditional-Sharpe ordering: `w_qqqt_calm = 0.05`,
`w_qqqt_stress = 0.20`. Mechanism, engine, costs, no-look-ahead
convention, and total-exposure invariant are all identical to iter 068
— the *only* change is the directional assignment of weights to
regimes. This is the cleanest possible information-theoretic test:
either the conditional-Sharpe ordering generalises OOS (Sharpe lift
+0.04-0.07 → potential breakout into 85-90) or it does not (closes
the inner-weight-swap axis on iter 064 in BOTH directions, forcing
iter 070 into structurally novel anchor / regime / cadence territory).

The reverse weights still average to ~0.10 over a 70/30 calm/stress
mix (`0.05·0.70 + 0.20·0.30 = 0.095 ≈ 0.10`), so the *time-mean*
exposure to QQQ_TREND matches iter 064's static `w=0.10` — but the
allocation is now regime-targeted onto the high-Sharpe-of-QQQ_TREND
bars.

## Primary citation

`[stocks_on_the_move, p.21-30]` — Clenow (2015), single-asset 200d SMA
filter as a regime gate inside a momentum portfolio. Foundational citation
for treating QQQ_TREND as a regime-conditional sleeve. The reverse swap
respects Clenow's principle "park in cash during downtrends, ride trend
during uptrends" — when VIX is high (stress, often coincident with
broad-equity downtrends), QQQ_TREND is in cash; the iter 069 swap
upweights this cash-parking sleeve precisely in stress, where its
defensive return profile is most diversifying.

## Additional citations

- **Faber (2007)**, SSRN 962461, *A Quantitative Approach to Tactical
  Asset Allocation*, J. Wealth Mgmt 9(4) — single-asset 200d SMA TAA
  primitive (preserved verbatim via iter 064's `qqq_trend.py`).
- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity;
  preserved as iter 046 base via the saved `r_046` stream.
- `[volatility_trading, p.218]` — Sinclair (2013), σ⁻² scaling
  primitive; preserved inside iter 046 via iter 016.
- **Whaley (2009)**, *J Portf Mgmt* 35(3): 98-105,
  DOI 10.3905/JPM.2009.35.3.098 — VIX as ex-ante regime indicator;
  threshold = 20 long-run median (preserved from iter 048/065/068).
- **Bekaert & Hoerova (2014)**, *J Econometrics* 183(2): 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition.
- **Moskowitz, Ooi & Pedersen (2012)**, *JFE* 104(2),
  DOI 10.1016/j.jfineco.2011.11.003 — TSM regime conditionality.
- `[advances_fin_ml, p.162-164]` — strict shift(1) on VIX (no peeking).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
- `[advances_fin_ml, p.196-202]` — bootstrap CI (G6).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1, vacuous at N=1).
- `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching.
- `[systematic_trading, ch.11]` — Carver IDM ≤ 2.5 (we sit at 1.0).
- **iter 068 final report** — empirical conditional-Sharpe ordering
  (KILL I) measured on edu/spy/ndx full-sample bars; iter 069 tests
  whether that ordering generalises onto the *blended* return path
  rather than just to the per-stream conditional split.

## Edge source

iter 064's two sub-streams are BOTH structurally defensive in stress
(QQQ_TREND parks in cash via 200d SMA; `r_046` de-risks via inner
iter_041 VIX gates), with HIGHER conditional Sharpe in stress than
calm on 3/3 datasets. SPY 1x buy-hold has flat conditional Sharpe
across regimes (no cash-park, no internal vol management). iter 069
captures the regime-conditional defensive premium of QQQ_TREND by
upweighting it precisely when its conditional Sharpe is largest
(stress, where its variance collapses to ~0 from cash-parking) and
downweighting it in calm where iter 046's risk-parity allocation
dominates. SPY can't replicate this — it is always 1.0 long with
no regime conditionality and no internal vol management.

## Datasets

- **educational** (SPYSIM synth ~20y, 2006-01-03 → 2026-04-15): same
  window as iter 068. Tests whether the directional flip preserves
  iter 064's edu CAGR-floor unlock (9.49% > 9.18% bench×0.8). Synth
  has different VIX dynamics from real data — mid-test of regime
  generalisation.
- **spy_real** (Tiingo SPY 17y, 2009-06-25 → 2026-04-15): primary
  real-data window; bench = SPY b&h S=0.90 / CAGR=14.97%.
- **ndx_real** (Tiingo QQQ 16y, 2010-02-12 → 2026-04-15): bench =
  QQQ b&h S=0.955 / CAGR=19.18%. Tests robustness on a different
  benchmark.

## Kill criteria (pre-committed)

If ANY of the following fires, the iteration is documented as a closure:

- **KILL A (Sharpe-lift criterion, NEW direction)** — Sharpe lift
  vs iter 064 < +0.02 on ≥ 2 of 3 ds (worst-case interpretation of
  iter 068's predicted +0.04-0.07 lift). If lift is below +0.02,
  the empirical conditional-Sharpe ordering DOES NOT generalise to
  the blended return path → axis closed in BOTH directions.
- **KILL B (DSR cutoff)** — DSR worst-p ≥ 0.05. iter 069 needs
  worst-p < 0.05 to even hold the line on iter 064's gates.
- **KILL C (score floor)** — Total score < 75 (drops below STRONG
  threshold). Indicates the swap doesn't pay for itself.
- **KILL D (CAGR-floor regression)** — edu CAGR < 9.18% (bench×0.8),
  i.e., iter 069 loses iter 064's 1st-ever non-LETF edu unlock.
- **KILL E (engine drift)** — G7 cross-lib max diff > 0.5 pp on
  any ds (engine bug; would invalidate the result).
- **KILL F (no-op switch)** — corr(iter_069, iter_064) > 0.995 on
  ≥ 2 ds. Means the regime gate doesn't move enough to register —
  cleanly closes the axis: ordering may be real but the leverage
  delta is too small to exploit.
- **KILL G (composition bug)** — max|Σw - 1| > 1e-9 anywhere.
- **KILL H (regime-flip pathology)** — flips/yr < 5 (no switching)
  or > 100 (overfit-flicker) on any ds.
- **KILL I (REVERSED direction symmetry test)** — iter 069 Sharpe
  WORSE than iter 068's Sharpe on ≥ 2 of 3 ds. The reverse direction
  was predicted to be strictly better given iter 068's KILL I
  finding; if iter 069 underperforms iter 068, the conditional-
  Sharpe ordering is sample-dependent (iter 068's per-stream
  full-sample finding doesn't survive into the BLENDED path with
  flip costs and OOS bars). Closes the axis BOTH directions.

**Hypothesis is empirically falsified** if KILL A OR KILL I fires —
both indicate the directional intuition (UPWEIGHT defensive sleeve
in stress) doesn't generalise. Hypothesis is **partially supported**
if Sharpe lifts but DSR or CAGR-floor still fail (KILL B / D), in
which case iter 069 is a 75-89 STRONG / 60-74 PROMISING result that
adds incremental evidence without breaking the 90 ceiling.
**Hypothesis succeeds** with a tier WINNER (score ≥ 90 + all 5 strict
conditions) only if Sharpe lifts AND DSR<0.05 AND CAGR floor passes
on ≥ 2 ds.

## Expected budget

- **Configs to test**: 1 (single pre-committed reverse-direction cfg
  `iter064_vix_inner_w_calm005_stress020_vix20`). N=1 keeps PBO
  vacuous and avoids re-introducing multi-cfg DSR penalty noise.
- **Wall-time**: ~5-10 minutes total (load saved iter 046 streams +
  recompute QQQ_TREND with warmup × 3 datasets, apply combiner,
  G3-G6 gates, G7 cross-lib).
- **Files to create**:
  - `hypothesis.md` (this file)
  - `iter069_reverse_blend.py` — thin wrapper re-exporting iter 068's
    combiner under iter 069-specific docstring + default reversed
    weights (engine BIT-IDENTICAL; only defaults change).
  - `run_backtests.py` — clone of iter 068's `run_backtests.py` with
    reversed CFG; saves `results.json` with the standard
    `returns_series` schema for plot helper compat.
  - `compute_gates_and_score.py` — clone with iter 069-specific KILL
    criteria (A includes a +0.02 lift floor; new I compares iter 069
    to iter 068).
  - `tests/test_iter069_reverse_blend.py` — TDD specs verifying the
    REVERSED weight assignment (calm gets 0.05, stress gets 0.20),
    cross-lib parity, total-exposure invariant, and engine bit-
    identity to iter 068's combiner under the matching swap.
  - `verdict.json` — produced by Stage 4.
  - `final_report.md` — Stage 5.
  - `plot_vs_benchmark_{spy,ndx}_real.png` — Stage 5 plot helper.
- **cumulative_n_trials advance**: 4338 → **4339** (+1).

## Implementation plan

1. **Stage 3a** — Write `iter069_reverse_blend.py`: thin
   `combine_reverse(r_046, r_qqqt, vix, w_qqqt_calm=0.05,
   w_qqqt_stress=0.20, ...)` that delegates to iter 068's
   `combine_with_vix_inner_weight`. The output series is renamed
   `iter069_vix_inner_reverse` for downstream identification.
2. **Stage 3b** — Write `tests/test_iter069_reverse_blend.py` (TDD
   FIRST): 5 tests covering (a) calm bars get `w_qqqt = 0.05`,
   (b) stress bars get `w_qqqt = 0.20`, (c) total exposure ≡ 1.0,
   (d) engine bit-identity to iter 068's combiner with matching
   reversed weights, (e) cross-lib parity (numpy reference).
3. **Stage 3c** — Run `pytest` baseline (currently ~796 tests). Add
   iter 069 tests; baseline must stay green; new tests must pass.
4. **Stage 3d** — Write `run_backtests.py`: clone iter 068's,
   change CFG to reverse direction. Save `results.json` matching
   iter 068's schema.
5. **Stage 3e** — Run `python run_backtests.py` end-to-end; verify
   per-dataset Sharpe / CAGR / MDD output is sensible (Sharpe within
   ±0.10 of iter 064's 1.22-1.38 expected).
6. **Stage 4** — Write `compute_gates_and_score.py` with iter 069
   KILL criteria; run; verify verdict.json output.
7. **Stage 5** — Run `plot_helper.py --iter 069`; write
   `final_report.md`; update `BASE_MEMORY.md` (iteration log +
   top-K + promising directions); append to `DEAD_ENDS.md` if any
   new structural axis closes.

This pre-commits N=1 cfg, exact reverse weights, exact iter 068
mechanism, and 9 kill criteria before running any code. No grid
search; no parameter sweep; no post-hoc cfg selection.
