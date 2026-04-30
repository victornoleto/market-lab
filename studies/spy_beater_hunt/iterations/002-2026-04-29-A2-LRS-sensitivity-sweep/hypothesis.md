# Iter 002 — A2 LRS Sensitivity Sweep (SMA/EMA × window × buffer × leverage)

**Date**: 2026-04-29
**Tier**: Tier 1 follow-up (PROMISING_DIRECTIONS.md A1 sensitivity)
**Cumulative n_trials at iter start**: 4 → after iter: 10

## Hypothesis

Iter 001 (A1 Gayed LRS UPRO) produced PROMISING 67/100, 2/3 bars met:
CAGR ✓ (mean 19.01%), Gates ✓ (6/6/5), but **MDD ✗ (mean 50.57%, +9.72pp
above 40.85% ceiling)**. The 200d SMA was too laggy for tail-risk events,
all WF windows hit max_mdd 0.40-0.55.

This iter tests three orthogonal levers to reduce MDD without crashing
CAGR:

1. **Signal speed**: faster SMA/EMA windows exit earlier on crashes.
   Trade-off: more whipsaw in choppy markets.
2. **Threshold band (hysteresis)**: require breakout > MA × (1 + buffer)
   to enter and < MA × (1 - buffer) to exit, reducing flips in the
   "indifference zone".
3. **Lower leverage**: 2× SSO instead of 3× UPRO directly cuts MDD by
   ~33% (and CAGR proportionally less due to compounding asymmetry).

## Citation

Primary: prior project archive
`studies/_archive/ema_sma_threshold_nasdaq_real/FINAL.md` — ran 384
configs of {filter}_N{window}_th{threshold}_bL{lev} on QQQ 2010-2024.
Top finding: SMA_N150_th0_bL2 reached CAGR 25.32%, MDD 40.53% on QQQ.

Secondary: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed —
LRS rationale unchanged from iter 001.

## Configs (6) — naming `a2_{filter}{window}_th{buf}_{lev}`

1. **a2_sma100_3xupro** — SMA 100, 0% buffer, UPROSIM 1.0 / IEFSIM 1.0
   *Hypothesis: faster signal cuts MDD by exiting earlier*
2. **a2_sma200_th2_3xupro** — SMA 200, 2% buffer, UPROSIM 1.0 / IEFSIM 1.0
   *Hypothesis: anti-whipsaw via hysteresis preserves CAGR while reducing MDD*
3. **a2_sma200_th5_3xupro** — SMA 200, 5% buffer, UPROSIM 1.0 / IEFSIM 1.0
   *Hypothesis: stronger buffer eliminates whipsaw cost in 1995-2007*
4. **a2_ema150_th2_3xupro** — EMA 150, 2% buffer, UPROSIM 1.0 / IEFSIM 1.0
   *Hypothesis: EMA fast-react + buffer = best signal/whipsaw trade-off*
5. **a2_sma150_2xsso** — SMA 150, 0% buffer, SSOSIM 1.0 / IEFSIM 1.0
   *Hypothesis: lower leverage (2×) directly cuts MDD by ~33% with proportional CAGR drag*
6. **a2_ema100_th2_2xsso** — EMA 100, 2% buffer, SSOSIM 1.0 / IEFSIM 1.0
   *Hypothesis: fast + low-lev + buffer combo targets MDD bar*

All 6 configs use SPYSIM as signal ticker, T+1 lag.

## Bar conditions (strict, unchanged)

- Bar 1 (CAGR): mean ≥ 0.1380
- Bar 2 (MDD):  mean ≤ 0.4085
- Bar 3 (Gates): ≥ 2/3 datasets at threshold

## KILL conditions (pre-committed)

- KILL #6 (CAGR floor): if best aggressive config can't reach mean CAGR
  ≥ 13.80%. Iter 001 already passed; should still pass here at 3× lev.
- **KILL #7 (signal speed irrelevant)**: if SMA100 produces WORSE Sharpe
  than SMA200 across ≥ 2/3 datasets, signal speed is not the issue and
  faster gates do not help → close direction "faster signal".
- **KILL #8 (buffer doesn't help)**: if buffer 5% configs produce WORSE
  Sharpe than buffer 0% configs across ≥ 2/3 datasets, hysteresis adds
  no value → close direction "anti-whipsaw via threshold band".
- **KILL #9 (lower leverage backfires)**: if 2× SSO configs produce
  WORSE Sharpe than 3× UPRO configs (Sharpe should at minimum be
  preserved when lev decreases), then there's a synth/data problem.

## Expected outcomes

- Best CAGR likely from `a2_sma100_3xupro` (faster signal + max lev).
- Best MDD likely from `a2_sma150_2xsso` or `a2_ema100_th2_2xsso`.
- "Sweet spot" candidate: one of the 2× SSO configs hits MDD ≤ 40.85%
  bar while keeping CAGR ≥ 13.80%.

If any config produces winner_conditions_met = True, halt direction
exploration and run sensitivity analysis on the winner. Otherwise
proceed to iter 003 per PROMISING_DIRECTIONS.md ranking (B1 HFEA).

## INCOMPLETE flags

- UPROSIM/SSOSIM are testfolio synths (real LETF inception 2009/2006).
- KMLMSIM unused this iter (no off-regime KMLM mix).
- Threshold band hysteresis logic is sequential (O(n) loop) — verified
  against naive SMA gate at buffer_pct=0 (test
  `test_threshold_band_zero_buffer_matches_naive_gate`).
