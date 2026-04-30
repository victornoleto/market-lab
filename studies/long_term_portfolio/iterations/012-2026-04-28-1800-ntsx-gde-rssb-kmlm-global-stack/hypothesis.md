# Iter 012 — NTSX + GDE + RSSB + KMLM global capital-efficient stack

**Slug**: `ntsx-gde-rssb-kmlm-global-stack`
**Family**: A2 from BASE_MEMORY.md "Promising unexplored directions"
**Date**: 2026-04-28
**Author**: long-term portfolio loop iter 012

## Hypothesis

Adding RSSBSIM (Return Stacked Global Stocks & Bonds — 100% global equity
+ 100% Treasury at 200% notional) as a fourth sleeve to the iter 011
winner architecture (NTSX + GDE + KMLM) injects the missing international
equity + duration exposure without sacrificing the capital-efficient
stacking philosophy. iter 011 has **zero international equity** and
**zero explicit Treasury duration** — RSSB delivers both in a single
stacked vehicle.

The structural argument: iter 011 currently bundles US equity (via NTSX
+ GDE), gold (via GDE), short-duration Treasury (via NTSX 0.6 IEF), and
managed futures (KMLM). Replacing some KMLM weight with RSSB shifts the
mix from "pure US-stacked + crisis-alpha" to "global-stacked + reduced
crisis-alpha + duration", which:

1. **Lowers correlation with SPY/QQQ benchmarks** (RSSB has ~50% intl
   equity weight) → potential Sharpe edge on vt_real and ndx_real where
   the avg(SPY,VT) benchmark is concentrated US-heavy.
2. **Adds explicit long-duration via the 100% Treasury overlay** (RSSB's
   bond sleeve uses ~7y duration vs NTSX's IEF 7-10y; net effect adds
   duration without crowding out equity exposure at the same gross
   notional).
3. **Keeps the leverage signature similar to iter 011** (RSSB is 200%
   notional like NTSX and GDE — not adding more sleeve-leverage at the
   margin).

## Primary citation

`[risk_parity, ch.5, p.10]` — Carlson on capital-efficient stacking via
overlapping bond/equity exposures (RSSB is the canonical implementation
of this principle for global equity).

## Secondary citations

- `[ilmanen, ch.19]` — global equity diversification reduces sequence-of-
  returns risk; international equity adds an independent return axis.
- `[stocks_on_the_move, p.21-30]` — managed futures (KMLM) as crisis-alpha
  diversifier, justifying its retention in the new mix at lower weight.
- `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]` — gates
  G1 PBO, G2 DSR, G6 bootstrap, G7 cross-lib.

## Edge source (1 sentence)

The avg(SPY, VT) benchmark is a US-heavy 50/50 blend; replacing iter
011's pure-US stack with a 25-30% RSSB sleeve injects ~12-15% intl
equity weight and explicit Treasury duration, which **decouples the
strategy's beta to US equity** and adds two return drivers that the
benchmark partially captures via VT (not SPY) — generating the +0.10
Sharpe edge through correlation-reduction rather than higher leverage.

## Pre-committed kill criteria (1 specific observable that falsifies)

**Kill if ANY of these hold**:

1. **Sharpe regression on lh_56y**: best config across the 4-config grid
   has gross Sharpe < iter 011's lh_56y winner Sharpe (1.046) on
   `lh_56y`. (Adding RSSB lowering Sharpe in the long window means RSSB
   is a worse stacked sleeve than what iter 011 already had.)
2. **PBO failure on ≥ 2 datasets**: G1 PBO ≥ 0.5 on lh_56y AND vt_real,
   indicating intra-family weight selection is at noise level.
3. **CAGR floor violation on all 3 datasets**: candidate CAGR <
   0.8 × avg(SPY,VT) CAGR everywhere → strategy is too defensive to
   matter.

If any kill fires, declare CLOSED and append to DEAD_ENDS.md.

## Why this is NOT a re-test of any DEAD_END

Cross-checked against `DEAD_ENDS.md` and the 15 inherited families in
`_archive/strategy_hunt_loop/FINAL_REPORT.md`:

- **Not DE-005** (plain global/factor/CTA stack): DE-005 used RSSB +
  GDE + KMLM + VBR + VSS + VWO + SPY + RSST_PROXY (8-asset wide grid)
  selecting `stack_gde_heavy`. Result was MDD 27-42% on all datasets
  because the wide grid included thin sleeves and over-weighted GDE.
  Iter 012 is a **tight 4-asset stack** anchored on iter 011's proven
  NTSX+GDE+KMLM core, with only RSSB as the new sleeve at moderate
  weight (25-30%). Tight grids around a proven core are NOT structurally
  equivalent to wide blind grids.
- **Not DE-006** (HAA intl small/value tilt): DE-006 was an HAA-shell
  rotation strategy with a `VEASIM`/`VBR`/`VSS` blend in the offensive
  sleeve. Iter 012 is a static stack with no rotation/canary.
- **Not strategy_hunt_loop family 9** (NTSX/synth bond-carry): iter 033
  tested NTSX with TLT instead of IEF — no RSSB, no global equity.
- **Not strategy_hunt_loop family 10** (layered ensembles): iter 012 is
  a **single static portfolio**, not an ensemble of prior winners with
  Markowitz weights.
- **Not strategy_hunt_loop family 13** (cross-region rotation): iter 012
  has no rotation — RSSB delivers global exposure as a buy-hold
  position, not as a rotation between US/intl regimes.

The iter 011 architecture (US-stacked) succeeded — iter 012 tests
whether the **same architecture, internationalized via RSSB**, beats it.

## Datasets to test

All 3 datasets via `studies.long_term_portfolio.datasets.load_prices`:

- **lh_56y** (1970-2026): full 56y window. KMLMSIM column splice-aware
  via FF MoM proxy pre-1988. RSSBSIM has 56y data so the sleeve is
  fully populated. **lh_56y caveat to disclose** (per INFRASTRUCTURE.md):
  pre-1988 KMLMSIM-derived returns track UMD+RF, which has Sharpe ~1.9
  vs KMLM's long-run ~0.5; iter 012 has lower KMLM weight than iter 011
  so the overstatement effect should be **smaller** here.
- **vt_real** (2008-06 → 2026-04): 17y. RSSB live-fund inception is
  2023 → entire window uses RSSBSIM synth.
- **ndx_real** (2010-02 → 2026-04): 16y. NDX-aligned stretch test (will
  likely show smaller Sharpe edge — NDX is concentrated US tech so
  global tilt subtracts beta).

## Implementation plan

**Reuse iter 011 architecture** (`iterations/011-*/backtest.py`):

- Same engine: `gross_returns()`, 7-gate battery, AnnualDarfEngine net,
  rolling robustness, score_strategy.
- Same dataset loop: lh_56y / vt_real / ndx_real via
  `load_prices(name)`.
- Same config selection rule: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe)
  across 3 datasets.

**New piece**: 4-asset weight grid (4 configs) tightened around iter 011
winner (35% NTSX + 25% GDE + 0% RSSB + 40% KMLM):

| config_id | NTSX | GDE | RSSB | KMLM | rationale |
|---|---:|---:|---:|---:|---|
| `rssb_balanced_30303010` | 30% | 30% | 30% | 10% | equity-heavy global tilt; tests max RSSB sleeve |
| `rssb_moderate_25252525` | 25% | 25% | 25% | 25% | 4-way equal — neutral baseline |
| `rssb_iter011_clone_30202525` | 30% | 20% | 25% | 25% | iter 011 weights with 25% reallocated to RSSB |
| `rssb_lite_30253015` | 30% | 25% | 30% | 15% | reduce KMLM (which dominated iter 011); RSSB takes equity-side weight |

All weights sum to 100%. Selection: same rule as iter 011.

**Cross-lib G7**: numpy-pure reference reused from iter 011 (no new
simulator mechanism, same static buy-hold daily return calculation).

**Wall-time target**: ≤ 30 min (4 configs × 3 datasets × 7 gates with
2000 bootstrap iterations).

## Expected budget

- Configs: 4 (cumulative_n_trials = 40 + 4 = 44)
- Wall-time: ~5-15 min for backtests + 5 min for plots + 5 min for report
- New code: minimal; primarily a copy of iter 011 backtest.py with
  RSSBSIM added to the asset map and 4 new config tuples.

## Decision criteria (Stage 5)

- **WINNER (set beats_incumbent=true)**: score > 91 AND all 5 strict
  conditions met AND (Sharpe edge ≥ +0.10 vs iter 011 on ≥ 2 of 3
  datasets) AND (Sharpe edge ≥ +0.10 vs avg(SPY,VT) on ≥ 2 of 3
  datasets).
- **STRONG (75-89)**: passes 4-5/5 strict; close-but-not-incumbent.
- **PROMISING (60-74)**: 3/5 strict; document gap, leave incumbent.
- **MARGINAL (40-59)**: 2/5 strict; structural lesson; close family.
- **FAIL (<20)** OR kill criteria triggered: append DEAD_END.
