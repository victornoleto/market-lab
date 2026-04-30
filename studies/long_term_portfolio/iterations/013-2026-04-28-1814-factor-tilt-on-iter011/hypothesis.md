# Iter 013 — Factor tilt on iter 011 base (NTSX + GDE + KMLM + VBRSIM)

**Hypothesis (Direction B from `BASE_MEMORY.md`)**: iter 011's incumbent
winner (35% NTSX + 25% GDE + 40% KMLM, score 91/100) carries **zero
explicit factor exposure** — pure US large-cap beta (via NTSX), gold
(via GDE), and managed-futures (via KMLM). The user's literature
preference includes AVUV/AVDE/SPMO factor ETFs. Adding an explicit
small-cap value tilt (`VBRSIM`, the AVUV synth proxy) introduces an
**independent return source** that is **less correlated with SPY beta
than additional equity stacking** (`[risk_parity, ch.2, p.37-41]`), so
it should improve the portfolio's risk-adjusted return frontier.

**Edge source (1 sentence)**: avg(SPY 1× b&h, VT 1× b&h) is pure
market-beta exposure — it captures NONE of the cross-sectional
size+value premium documented in `[stocks_on_the_move, ch.6, p.21-30]`
(Clenow's whole momentum framework relies on cross-sectional ranking
edges that pure b&h does not capture); AVUV/VBRSIM gives a clean,
buy-hold-able factor sleeve at 1× notional, isolating that premium
without re-introducing the Treasury-overlap problem that killed iter 012.

**Why iter 012's kill ≠ iter 013's kill**: iter 012 (RSSB injection)
failed because RSSB's 200% notional overlay duplicated NTSX's IEFSIM
exposure → portfolio became 30-50% Treasury, post-2022 rate-hike drag.
VBRSIM is **1× notional**, **zero Treasury**, **US small-cap value**
— qualitatively different mechanism. The factor-tilt direction has
NOT been tested on the iter 011 architecture (closest dead-end is
DE-006 `haa-global-factor-tilt`, but that swapped HAA's INTL equity
sleeve for a small-cap blend; iter 013 ADDS a US factor sleeve to a
fundamentally different architecture, the iter 011 capital-efficient
stack).

**Citations**:

- `[risk_parity, ch.5, p.10]` — capital-efficient stacking rationale
  (NTSX/GDE retained from iter 011)
- `[risk_parity, ch.2, p.37-41]` — factor premium framework (carry as
  documented example; same conceptual scaffolding applies to
  size/value)
- `[stocks_on_the_move, ch.6, p.21-30]` — Clenow cross-sectional
  ranking edges (the conceptual basis for why factor-loaded indices
  beat market-beta on Sharpe in the long run)
- `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]` —
  G1 PBO / G2 DSR / G6 bootstrap / G7 cross-lib gates

## Datasets to test

All 3 datasets via `studies.long_term_portfolio.datasets.load_prices`:

- `lh_56y` (1970-01-02 → 2026-04-24, 56y) — KMLMSIM splice-aware
  (FF MoM proxy pre-1988); SPYSIM bottleneck makes effective window
  1986-2026 (40y) for any NTSX-using config. **Same effective window
  as iter 011/012.**
- `vt_real` (2008-06-01 → 2026-04-24, 17y)
- `ndx_real` (2010-02-01 → 2026-04-24, 16y)

## Pre-committed config grid (4 configs)

US-only factor tilt (`VBRSIM` = US Small-Cap Value, 99y synth) at
4 intensity levels. All keep NTSX_PROXY ≥ 20% (capital-efficient core)
and KMLMSIM ≥ 25% (crisis-alpha). VBRSIM weight sweeps 10% → 30%.

| config | NTSX | GDE | KMLM | VBRSIM | factor weight |
|---|---:|---:|---:|---:|---:|
| `factor_lite_30253510`     | 30% | 25% | 35% | 10% | 10% |
| `factor_moderate_25253020` | 25% | 25% | 30% | 20% | 20% |
| `factor_balanced_25202530` | 25% | 20% | 30% | 25% | 25% |
| `factor_heavy_20203030`    | 20% | 20% | 30% | 30% | 30% |

**Why no intl factor (VSSSIM/EFVSIM)**: both have inception 1994-12-29
and 1994-02-15, which would shrink lh_56y from 1986-2026 (40y eff)
to 1994-2026 (32y) — losing comparability with iter 011/012.
Deferred to Direction A1 (NTSI/NTSE proxy synthesis required).

**Selection rule**: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across
3 datasets — same as iter 011/012, ensures we pick the config that
maximizes the mission-relevant edge.

## Pre-committed kill criteria (falsify before claiming insight)

These fire BEFORE scoring — if any kills, the iter is FAIL with
structural lesson, not "almost made it" rationalization.

1. **Kill #1 (incumbent regression)**: best lh_56y Sharpe across the 4
   configs < **1.046** (iter 011 incumbent) → factor tilt FAILS to
   advance the incumbent on long-history; the size+value premium does
   not survive in a portfolio context once gold + MF are already
   present.

2. **Kill #2 (return degradation)**: best lh_56y CAGR across the 4
   configs < **11.58%** (iter 011 CAGR) AND best Sharpe also < 1.046
   → factor tilt is **monotonically degrading** the iter 011 stack
   on every axis (Sharpe + CAGR). Direction B closes.

3. **Kill #3 (catastrophic regression)**: selected config gross
   Sharpe < avg(SPY,VT) on ≥ 2 of 3 datasets (Sharpe < 0.671 / 0.707 /
   0.924 on lh_56y / vt_real / ndx_real respectively) → fails the
   loop's primary mission threshold; factor tilt is so noisy at the
   tested grid that even the SELECTED config can't beat passive b&h.

If kill #1 or #2 fires AND winner_conditions vs avg(SPY,VT) still
hold (PBO/DSR/CAGR-floor/MDD-ceiling pass on ≥ 2 of 3 datasets), the
iter ranks STRONG vs avg(SPY,VT) but does NOT advance incumbent →
DE-014 with structural insight added.

## Expected budget

- **Configs**: 4 (DSR n_trials=4, same convention as iter 011/012).
- **Datasets**: 3.
- **Wall-time estimate**: ~2-3 min total (static stack, no rolling
  optimization). Same engine path as iter 012, just one extra ticker
  in the mix.
- **Cumulative n_trials after this iter**: 44 + 4 = **48**.

## Implementation plan

1. Copy iter 012's `backtest.py` template; replace the config grid
   with the 4-config VBRSIM sweep above.
2. `expand_weights` retains NTSX_PROXY → SPYSIM/IEFSIM/CASHX expansion;
   VBRSIM is direct (no expansion).
3. Reuse `datasets.load_prices`, `tax_engine.AnnualDarfEngine`,
   `scoring.score_strategy`, `pbo`, `dsr`, `walk_forward` — no new
   modules, no new tests required (purely additive config change).
4. Run, generate verdict.json + results.json, write final_report.md,
   call `plot_helper.py --iter 013`.

## What this iter does NOT test (deferred)

- **Intl factor (AVDV proxy)** — requires VSSSIM/EFVSIM but those
  shrink lh_56y to 32y; defer to Direction A1 with NTSI/NTSE proxy
  synthesis.
- **Momentum factor overlay (UMD direct)** — Direction B5; only
  worth testing IF this iter shows positive factor-tilt signal.
- **Combined US+intl factor** — Direction B6; superset of this iter,
  same deferral.
- **Live AVUV vs VBRSIM proxy validation** — Direction C deploy
  diligence, post-winner only.
