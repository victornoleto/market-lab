# Iter 004 — A3 KMLM Dose-Response (extend monotonic positive trend)

**Date**: 2026-04-30
**Tier**: Tier 2 (PROMISING_DIRECTIONS A3) — direct extension of iter 003 closest-to-winner
**Cumulative n_trials at iter start**: 14 → after iter: **17** (3 configs to slow DSR growth)

## Hypothesis

Iter 003 (`a3_lrs_split_kmlm20`: 40% UPRO + 40% SSO + 20% KMLM ON, IEF
OFF, SMA 200, no buffer) is the new closest-to-winner: bars 3/3 PASS
(CAGR 14.99%, MDD 41.87%, gates 6+6 cross_met), score **64/100**. KILL
#11 (KMLM monotonic harm) NOT FIRED — Sharpe rose monotonically from
KMLM 10% (0.681 / 0.665) to KMLM 20% (0.719 / 0.692) in BOTH datasets.

**Direct hypothesis**: KMLM dose-response is **monotonic positive in
the 10-30% range**. Extending to 25-30% should continue dropping MDD
toward 35-40% target while CAGR drag stays modest (KMLM long-term CAGR
~5-7%, so each 5% added to ON sleeve costs ~0.4-0.6pp CAGR but trims
MDD ~3-5pp via uncorrelated trend-following).

Score lever analysis (iter 003 → target):
- CAGR pts: 20/30 (mean 14.99%) — losing ~1pp per +5% KMLM is acceptable
- MDD pts: 10/20 (mean 41.87%) → target 13-14/20 (mean ~37-39%)
- Sharpe pts: 1/10 (mean 0.705) → target 3-4 (mean ~0.78-0.85) via MDD drop pulling Sharpe up
- DSR/Robustness/Gates: already maxed/near-max

**Realistic ceiling for this iter**: score 68-72.

## Citations

Primary: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d
SMA regime gate unchanged. Iter 003 validated.

Secondary: `[risk_parity, ch.5, p.10]` Carlson — capital-efficient
stacking validated empirically in iter 003 (KMLM 20% drops MDD 9.73pp
with only 1.24pp CAGR drag). Hypothesis: relationship continues 25-30%
KMLM region but eventually plateaus or inverts (KILL #13/#14 zone).

Tertiary: `studies/long_term_portfolio` PHASE_1_WINNERS F1+SPLIT ran
KMLM at 17.5% — that loop was Sharpe-anchored not CAGR-anchored, so
empirically suggests 17.5-20% is a known good zone. Going higher
(25-30%) is the unexplored frontier.

## Configs (3) — naming `a4_lrs_split_<crisis-alpha-mix>`

All configs use SPYSIM signal, SMA 200, no buffer, T+1 lag. ON sleeve
mixes leveraged equity (UPRO/SSO ~50/50 base) with crisis-alpha
diversifier; OFF sleeve stays 100% IEF.

1. **a4_lrs_split_kmlm25** — ON: 37.5% UPRO + 37.5% SSO + 25% KMLMSIM /
   OFF: 100% IEFSIM
   *Hypothesis: extending the iter 003 monotonic positive trend by +5%.
   Expected CAGR ~14.5%, MDD ~39%, Sharpe ~0.74.*
2. **a4_lrs_split_kmlm30** — ON: 35% UPRO + 35% SSO + 30% KMLMSIM /
   OFF: 100% IEFSIM
   *Hypothesis: probes for the inflection point. If still monotonic
   positive, KMLM dose can go higher in iter 005. Expected CAGR ~14%,
   MDD ~37%, Sharpe ~0.74-0.76. KILL #14 zone.*
3. **a4_lrs_split_tlt20** — ON: 40% UPRO + 40% SSO + 20% TLTSIM /
   OFF: 100% IEFSIM
   *Hypothesis: strict head-to-head with `a3_lrs_split_kmlm20` (same
   leverage budget, same %, swap KMLM↔TLT). Iter 003 KMLM 20% MDD
   41.87%; if `a4_tlt20` MDD > 41.87% AND Sharpe < 0.70 in BOTH ds,
   KILL #15 (TLT dominated at matched dose). Iter 003 a3_tlt15 was
   competitive with KMLM 10% — this iter tests TLT at the dose where
   KMLM peaked.*

## Bar conditions (strict, unchanged)

- Bar 1 (CAGR): mean ≥ **0.1121** (post-refactor: lh_56y + spy_real)
- Bar 2 (MDD):  mean ≤ **0.5517**
- Bar 3 (Gates): ≥ 2/2 datasets at threshold (lh_56y ≥ 5, spy_real ≥ 5)

## KILL conditions (pre-committed; numbers continue from #12)

- **KILL #6 (CAGR floor)** — if all 3 configs have mean CAGR < 11.21%,
  KMLM dose-response over-dilutes leveraged equity → cap at ≤ 20% in
  future iters. Unlikely (iter 003 KMLM 20% was 14.99%).
- **KILL #13 (KMLM dose-response inflection at 25%)** — if
  `a4_kmlm25` Sharpe < `a3_kmlm20` Sharpe (0.719 lh / 0.692 spy_real)
  in BOTH datasets, the inflection is between 20% and 25% → cap KMLM
  at 20% in future iters. Direction A3_kmlm_dose_response = CLOSED.
- **KILL #14 (KMLM monotonic harm beyond 25%)** — if `a4_kmlm30`
  Sharpe < `a4_kmlm25` Sharpe in BOTH datasets, the inflection is in
  25-30% range → next iter caps at 25%. (Distinct from #13: this fires
  even if 25% improved over 20% but 30% harmed vs 25%.)
- **KILL #15 (TLT structurally dominated at 20%)** — if `a4_tlt20`
  MDD > `a3_kmlm20` MDD (41.87%) AND `a4_tlt20` Sharpe < `a3_kmlm20`
  Sharpe (0.719 lh / 0.692 spy_real) in BOTH datasets, TLT loses to
  KMLM at matched dose → exclude TLT from future ON sleeves. Direction
  A3_tlt_dose_response = CLOSED.

## Expected outcomes

| config | CAGR | MDD | Sharpe (lh / spy) | bar 3/3? |
|---|---:|---:|---:|---|
| a4_lrs_split_kmlm25 | ~14.5% | ~39% | ~0.74 / 0.71 | likely PASS |
| a4_lrs_split_kmlm30 | ~14.0% | ~37% | ~0.74 / 0.72 | likely PASS |
| a4_lrs_split_tlt20  | ~14.8% | ~43% | ~0.70 / 0.68 | likely PASS |

Goal: at least one config (probably `a4_kmlm30`) crosses score 68-72
with bars 3/3 PASS, becoming new closest-to-winner. WINNER (≥ 90)
unrealistic in this iter — needs Sharpe > 0.95 and MDD < 30%, and the
MDD drop curve is decelerating (9.73pp from 0→20%, expect ~3-5pp from
20→30%).

## INCOMPLETE flags

- KMLMSIM real KMLM inception 2020-12 (~6y real history); pre-2020 is
  testfolio synth using FF MoM proxy. Iter 002/003 used same synth —
  comparison apples-to-apples.
- TLTSIM real TLT inception 2002-07 (lh_56y pre-2002 is synth).
- LRS rebalance instantaneous, no transaction costs modelled (ON sleeve
  with 4-ticker daily rebalance to fixed weights when gate flips). Real
  ETF spread + trading drag absent — iter 003 used same assumption.
- spy_real window (2003+) excludes 1973-74 stagflation / 2000-02 dot-com
  regimes; lh_56y synth is the only pre-2003 stress proxy.
- 3 configs (vs prior 4-6) deliberately to slow DSR cumulative inflation.
  At n_trials = 17, DSR penalty grows ~log(17)/log(14) ~10% tighter
  than iter 003 (worst p was 1.39e-02; bar is 5e-02). Headroom remains.
