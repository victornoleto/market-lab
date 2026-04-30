# Iter 003 — A3 Mixed Gayed (Crisis-Alpha Buffer in ON Sleeve)

**Date**: 2026-04-30
**Tier**: Tier 2 (PROMISING_DIRECTIONS A3) extending iter 001 closest-to-winner
**Cumulative n_trials at iter start**: 10 → after iter: 14

## Hypothesis

Iter 001 (`a1_lrs_split`: 50% UPRO + 50% SSO ON, IEF OFF, SMA 200, no
buffer) is the closest-to-winner: bars 3/3 PASS (CAGR 16.23%, MDD 51.60%,
gates 6/5), score 60/100. Tier WINNER requires score ≥ 90.

Score breakdown (iter 001):
- CAGR pts 22/30 (mean 16.23%, anchor 5-20%) — already strong
- MDD pts **6/20** (mean 51.60%, anchor 70-15%) — biggest miss
- Sharpe pts 1/10 (mean 0.657, anchor 0.5-2.0) — limited by MDD
- DSR 10/10, Robustness 9/10, Gates 12/20 — already maxed or near-max

The **MDD criterion is the dominant lever**. Iter 002 confirmed:
- Faster signal CLOSED (KILL #7) — MDD got worse
- Buffer band CLOSED (KILL #8) — MDD got worse
- Lower leverage (2× SSO, KILL #9 NOT FIRED) drops MDD ~5pp but CAGR
  drops more pp — net score lower (~56 vs 60)

The unexplored lever: **add crisis-alpha to the ON sleeve**. The 200d
SMA gate has structural lag (5-15% drawdown before flipping OFF during
fast crashes like 2008/2020). Diluting the leveraged-equity ON sleeve
with always-on KMLM (managed-futures crisis-alpha) and/or TLT (long
duration) buffers that lag period without sacrificing the
gate's bull-regime exposure.

OFF state stays IEF (iter 001 a1_lrs_kmlm_off showed KMLM-on-OFF
helped little — OFF state is rare ~25% of time, so the lever is in ON).

## Citations

Primary: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d
SMA regime gate unchanged.

Secondary: `[risk_parity, ch.5, p.10]` Carlson — capital-efficient
stacking rationale (always-on KMLM as crisis-alpha diversifier in a
levered equity sleeve, mirroring the F1+SPLIT incumbent's KMLM 17.5%
allocation that drove its 16.76% MDD).

Prior loop context: `studies/long_term_portfolio` PHASE_1_WINNERS
showed KMLM 15-20% in always-on stacks dropped portfolio MDD from
~30% to ~17% with minimal CAGR drag (~0.3pp).

## Configs (4) — naming `a3_lrs_split_<crisis-alpha-mix>`

All configs use SPYSIM signal, SMA 200, no buffer, T+1 lag. ON sleeve
mixes leveraged equity (UPRO/SSO 50/50 base from iter 001 winner) with
crisis-alpha diversifier; OFF sleeve stays 100% IEF.

1. **a3_lrs_split_kmlm10** — ON: 45% UPRO + 45% SSO + 10% KMLMSIM /
   OFF: 100% IEFSIM
   *Hypothesis: 10% KMLM tilt cushions the 5-15% pre-gate-flip MDD
   gap with minimal CAGR drag (~0.3pp).*
2. **a3_lrs_split_kmlm20** — ON: 40% UPRO + 40% SSO + 20% KMLMSIM /
   OFF: 100% IEFSIM
   *Hypothesis: stronger KMLM tilt → MDD ≤ 40% but at the cost of
   more CAGR drag (~0.7pp). Tests dose-response.*
3. **a3_lrs_split_tlt15** — ON: 42% UPRO + 43% SSO + 15% TLTSIM /
   OFF: 100% IEFSIM
   *Hypothesis: long-duration TLT diversifies via interest-rate
   correlation; helped pre-2022 but hurt during stagflation. Tests
   whether TLT is dominated by KMLM in the ON sleeve.*
4. **a3_lrs_split_blend** — ON: 40% UPRO + 40% SSO + 10% KMLMSIM
   + 10% TLTSIM / OFF: 100% IEFSIM
   *Hypothesis: blended diversifier captures KMLM crisis-alpha +
   TLT rate-driven diversification; targets MDD ≤ 40% while keeping
   CAGR ≥ 13.80%.*

## Bar conditions (strict, unchanged)

- Bar 1 (CAGR): mean ≥ **0.1121** (post-refactor: lh_56y + spy_real)
- Bar 2 (MDD):  mean ≤ **0.5517**
- Bar 3 (Gates): ≥ 2/2 datasets at threshold (lh_56y ≥ 5, spy_real ≥ 5)

## KILL conditions (pre-committed)

- **KILL #6 (CAGR floor)** — already validated; iter 001 winner
  passes 16.23%. Should still pass at moderate KMLM/TLT dilution.
- **KILL #10 (no MDD relief)** — if **all 4 configs** have mean MDD
  ≥ 51.60% (iter 001 a1_lrs_split level), the crisis-alpha buffer
  doesn't help structurally → close direction "ON-sleeve crisis-alpha
  dilution".
- **KILL #11 (KMLM monotonic harm)** — if `a3_kmlm20` has WORSE Sharpe
  than `a3_kmlm10` across BOTH datasets, more KMLM strictly degrades →
  cap KMLM at 10% in future iters.
- **KILL #12 (TLT structurally subordinate)** — if `a3_tlt15` has
  WORSE MDD than `a3_kmlm10` across BOTH datasets (TLT supposed to
  diversify but doesn't help drawdowns), TLT is dominated by KMLM in
  the ON sleeve → exclude TLT from future ON sleeves.

## Expected outcomes

- **a3_lrs_split_kmlm10**: CAGR ~15.5-16%, MDD ~46-49%, Sharpe ~0.68.
  Marginal improvement over iter 001 winner; closest path to score 65-70.
- **a3_lrs_split_kmlm20**: CAGR ~14-15%, MDD ~40-44%, Sharpe ~0.70.
  Best MDD pts; CAGR may dip below SPY mean if dataset window unlucky.
- **a3_lrs_split_tlt15**: CAGR ~15-16%, MDD ~44-50%, Sharpe ~0.65.
  TLT helped pre-2022; spy_real (2003+) includes 2022 crash so MDD
  may not improve much.
- **a3_lrs_split_blend**: CAGR ~14.5-15.5%, MDD ~42-47%, Sharpe ~0.70.
  Likely the best Sharpe + lowest MDD trade-off.

Goal: at least one config crosses score 65-70 with bars 3/3 PASS,
becoming new closest-to-winner. WINNER (≥ 90) unrealistic in single
iter — need multi-iter convergence.

## INCOMPLETE flags

- KMLMSIM and TLTSIM are testfolio synths (real KMLM inception 2020-12;
  real TLT inception 2002-07). Iter 002 already used them in
  `a2_sma150_2xsso` etc. — same synth assumptions apply.
- All ON-sleeve mixing inherits the LRS engine's instantaneous
  rebalance (no transaction costs modelled). Iter 001 used same
  assumption — comparison apples-to-apples.
- No new module needed; reuses existing
  `studies.spy_beater_hunt.run_iter.run_iter_spy_beater` with `type=lrs`
  spec (multi-ticker `on_weights`).
