# Iter 005 — A3 KMLM Extreme (probe inflection 35/40 + KMLM30+TLT10 blend)

**Date**: 2026-04-30
**Tier**: Tier 2 (PROMISING_DIRECTIONS A3) — direct extension of iter 004 closest-to-winner
**Cumulative n_trials at iter start**: 17 → after iter: **20** (3 configs to slow DSR growth)

## Hypothesis

Iter 004 (`a4_lrs_split_kmlm30`: 35% UPRO + 35% SSO + 30% KMLM ON, IEF
OFF, SMA 200, no buffer) is the new closest-to-winner: bars 3/3 PASS
(CAGR 14.39%, MDD 36.79%, gates 6+6 cross_met), score **66/100**. KILL
#13 and #14 (KMLM 25/30% inflection) NOT FIRED — Sharpe rose
monotonically across the dose grid (lh_56y / spy_real):
0% → 0.670 / 0.643, 10% → 0.681 / 0.665, 20% → 0.719 / 0.692,
25% → 0.741 / 0.706, 30% → 0.765 / 0.722. The dose curve is concave but
**has not inflected** in 0-30%.

**Direct hypothesis**: Probe the inflection point at KMLM 35% and 40%.
At some KMLM dose the leveraged equity sleeve gets diluted enough that
CAGR slips below the 11.21% bar OR Sharpe peaks and reverses (KMLM
long-term CAGR ~5-7% vs UPRO/SSO levered ~16-22%). Iter 004 marginal
costs: ~0.6pp CAGR per +5% KMLM, ~2.5-5pp MDD relief per +5% KMLM,
+0.018-0.024 Sharpe per +5% KMLM. Linear extrapolation predicts:
- 35%: CAGR ~13.8%, MDD ~34%, Sharpe ~0.78-0.80
- 40%: CAGR ~13.2%, MDD ~31%, Sharpe ~0.79-0.82

Plus a head-to-head blend test: **KMLM30 + TLT10** keeps the iter 004
winner architecture and adds 10pp of duration via TLT, replacing 10pp
of leveraged equity. Tests whether duration-on-top-of-trend gives
incremental MDD relief without sacrificing too much CAGR (TLT
unleveraged CAGR ~3-5%).

Score lever analysis (iter 004 → target):
- CAGR pts: 19/30 (mean 14.39%) — losing ~0.6pp per +5% KMLM still
  acceptable; bar floor 11.21% is far away
- MDD pts: 12/20 (mean 36.79%) → target 14-16/20 (mean ~30-34%)
- Sharpe pts: 2/10 (mean 0.744) → target 4-5 (mean ~0.85-0.95) via
  MDD drop pulling Sharpe up
- DSR/Robustness/Gates: already maxed/near-max

**Realistic ceiling for this iter**: score 70-74 if monotonic continues;
68-70 if inflection hits at 35-40%.

## Citations

Primary: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d
SMA regime gate unchanged. Iter 001-004 validated.

Secondary: `[risk_parity, ch.5, p.10]` Carlson — capital-efficient
stacking validated empirically across iter 003-004 (KMLM 0% → 30%
dropped MDD 14.81pp at only 1.84pp CAGR cost). Hypothesis: relationship
continues but eventually plateaus or inverts somewhere in 30-50% KMLM
zone (KILL #16/#17 zone).

Tertiary: `studies/long_term_portfolio` PHASE_1_WINNERS F1+SPLIT ran
KMLM at 17.5% — that loop was Sharpe-anchored. Iter 004 already ran
KMLM at 30% with monotonic Sharpe gain, so spy_beater_hunt has
empirically extended the known-good zone. 35-40% is the unexplored
frontier. `[ilmanen_expected_returns, ch.19]` MF crisis-alpha role
backs the hypothesis that uncorrelated trend exposure provides
diversification benefit beyond the F1+SPLIT 17.5% allocation.

## Configs (3) — naming `a5_lrs_split_<crisis-alpha-mix>`

All configs use SPYSIM signal, SMA 200, no buffer, T+1 lag. ON sleeve
mixes leveraged equity (UPRO/SSO ~50/50 base before crisis-alpha
allocation) with crisis-alpha diversifier; OFF sleeve stays 100% IEF.

1. **a5_lrs_split_kmlm35** — ON: 32.5% UPRO + 32.5% SSO + 35% KMLMSIM /
   OFF: 100% IEFSIM
   *Hypothesis: extending iter 004 monotonic positive trend by +5%.
   Expected CAGR ~13.8%, MDD ~33-34%, Sharpe ~0.78-0.80.*
2. **a5_lrs_split_kmlm40** — ON: 30% UPRO + 30% SSO + 40% KMLMSIM /
   OFF: 100% IEFSIM
   *Hypothesis: probes for inflection point. If still monotonic
   positive, KMLM dose can go higher in iter 006. If inflection hits,
   KILL #17 fires. Expected CAGR ~13.2%, MDD ~30-32%, Sharpe ~0.79-0.82.*
3. **a5_lrs_split_kmlm30_tlt10** — ON: 30% UPRO + 30% SSO + 30% KMLMSIM
   + 10% TLTSIM / OFF: 100% IEFSIM
   *Hypothesis: adds duration on top of iter 004 winner (a4_kmlm30).
   Tests whether 10pp of leveraged equity → 10pp TLT gives further MDD
   relief at acceptable CAGR cost. If `a5_kmlm30_tlt10` Sharpe <
   `a4_kmlm30` Sharpe (0.765/0.722) in BOTH datasets, KILL #18 fires
   (TLT-on-top doesn't help). Expected CAGR ~13.5%, MDD ~33-35%,
   Sharpe ~0.76-0.78.*

## Bar conditions (strict, unchanged)

- Bar 1 (CAGR): mean ≥ **0.1121** (post-refactor: lh_56y + spy_real)
- Bar 2 (MDD):  mean ≤ **0.5517**
- Bar 3 (Gates): ≥ 2/2 datasets at threshold (lh_56y ≥ 5, spy_real ≥ 5)

## KILL conditions (pre-committed; numbers continue from #15)

- **KILL #6 (CAGR floor)** — if all 3 configs have mean CAGR < 11.21%,
  KMLM dose-response over-dilutes leveraged equity → cap at ≤ 30% in
  future iters. Linear extrapolation puts iter 005 floor at ~13%, so
  KILL #6 unlikely unless concavity steepens sharply.
- **KILL #16 (KMLM 35% inflection)** — if `a5_kmlm35` Sharpe <
  `a4_kmlm30` Sharpe (0.765 lh / 0.722 spy_real) in BOTH datasets, the
  inflection is between 30% and 35% → cap KMLM at 30% in future iters.
  Direction A3_kmlm_extreme = CLOSED.
- **KILL #17 (KMLM 40% inflection)** — if `a5_kmlm40` Sharpe <
  `a5_kmlm35` Sharpe in BOTH datasets, the inflection is between
  35-40% → next iter caps at 35%. (Distinct from #16: this fires even
  if 35% improved over 30% but 40% harmed vs 35%.)
- **KILL #18 (TLT-on-top-of-KMLM30 doesn't help)** — if
  `a5_kmlm30_tlt10` Sharpe < `a4_kmlm30` Sharpe (0.765 lh / 0.722
  spy_real) in BOTH datasets, adding TLT on top of the iter 004 winner
  doesn't improve Sharpe → exclude TLT from KMLM-heavy ON sleeves in
  future iters. Direction A3_tlt_on_top_of_kmlm30 = CLOSED.

## Expected outcomes

| config | CAGR | MDD | Sharpe (lh / spy) | bar 3/3? |
|---|---:|---:|---:|---|
| a5_lrs_split_kmlm35 | ~13.8% | ~33% | ~0.78 / 0.75 | likely PASS |
| a5_lrs_split_kmlm40 | ~13.2% | ~31% | ~0.79 / 0.76 | likely PASS |
| a5_lrs_split_kmlm30_tlt10 | ~13.5% | ~34% | ~0.76 / 0.73 | likely PASS |

Goal: at least one config (probably `a5_kmlm40`) crosses score 70-74
with bars 3/3 PASS, becoming new closest-to-winner. WINNER (≥ 90)
unrealistic in this iter — needs Sharpe > 0.95 and MDD < 25%, and the
MDD drop curve is decelerating (5.08pp from KMLM 20% → 30%, expect
~3-4pp from 30% → 40%).

## INCOMPLETE flags

- KMLMSIM real KMLM inception 2020-12 (~6y real history); pre-2020 is
  testfolio synth using FF MoM proxy. Iter 002-004 used same synth —
  comparison apples-to-apples.
- TLTSIM real TLT inception 2002-07 (lh_56y pre-2002 is synth).
- LRS rebalance instantaneous, no transaction costs modelled (ON sleeve
  with 3-4 ticker daily rebalance to fixed weights when gate flips).
  Real ETF spread + trading drag absent — same assumption as iter
  001-004.
- spy_real window (2003+) excludes 1973-74 stagflation / 2000-02 dot-com
  regimes; lh_56y synth is the only pre-2003 stress proxy.
- 3 configs (vs 4-6 in earlier iters) deliberately to slow DSR
  cumulative inflation. At n_trials = 20, DSR penalty grows
  ~log(20)/log(17) ~6% tighter than iter 004 (worst p was 5.56e-03;
  bar is 5e-02). Headroom remains for ~2-3 more iters.
- KMLM 35-40% pushes the leveraged equity sleeve below 70% of ON
  exposure — at 40% KMLM the leveraged equity is only 60% of ON. If
  CAGR drops below 13% mean, the strategy is approaching the F1+SPLIT
  CAGR territory (10.76% mean) where KMLM dose-response delivers
  diminishing returns vs incumbent.
