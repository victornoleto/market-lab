# Hypothesis — Iter 011 NTSX + GDE + KMLM Static Stack

## Hypothesis

A simple static capital-efficient stack of **40% NTSX + 30% GDE + 30%
KMLM** (the user's literal architectural preference, untested across 10
prior iters) achieves **gross Sharpe ≥ avg(SPY, VT) + 0.10 on ≥ 2 of 3
datasets** by combining 1.44× futures-overlay notional (US equity +
Treasury + gold) with a managed-futures crisis-alpha sleeve. No tactical
rotation, no daily-reset LETF decay, no margin call risk.

## Primary Citation

- `[risk_parity, ch.5, p.10]` — capital efficiency via futures overlay
  ("return stacking"): a target risk allocation can be reached with
  lower capital outlay by stacking uncorrelated risk premia in one ETF
  wrapper (NTSX = 90 SPY + 60 IEF – 50 cash; GDE = 90 SPY + 90 GLD – 80
  cash). The premise is risk-budget diversification rather than capital
  diversification.
- `[stocks_on_the_move, p.21-30]` — managed futures (KMLM) provides a
  trend/momentum-driven crisis-alpha sleeve that is structurally
  uncorrelated with equity drawdowns (1973-74, 2000-02, 2008, 2022).
- `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]` — gates
  G1 PBO, G2 DSR, G6 bootstrap, G7 cross-lib.

## Edge Source

The avg(SPY, VT) buy-hold benchmark per dataset misses two structurally
independent return sources:

1. **Treasury + gold risk premia at zero capital cost** — NTSX and GDE
   embed bond and gold exposure inside a futures-overlay wrapper, so
   the investor gets +60% IEF + +90% GLD notional without actually
   borrowing. Plain SPY/VT b&h carries 100% equity beta and nothing
   else.
2. **Crisis-alpha trend exposure (KMLM)** — managed futures earn the
   trend-following premium and historically produce positive returns
   in extended equity drawdowns (KMLM index +33% in 2022 vs SPY
   −18%). This sleeve is the risk-decorrelator that pure equity b&h
   lacks.

The combined 1.44× notional preserves CAGR while the diversified risk
budget compresses MDD relative to a 1.44× equity LETF, lifting Sharpe
without introducing tactical-rotation noise.

## Why this is structurally different from DE-005 (iter 003)

DE-005 closed plain static stacks **measured against iter 009 HAA+Gold
(Sharpe 1.120 / 1.061 / 0.954)** — a much higher bar than the now-active
avg(SPY, VT) bar (0.671 / 0.707 / 0.924). The closure rationale was
"static stacks don't control drawdown like HAA's canary"; under the
redefined gross-of-tax avg-of-passive mission the test is whether a
static stack beats *naïve buy-hold* by +0.10 Sharpe — not whether it
beats HAA. Different game, different edge bar.

DE-005 also tested **RSSB-anchored mixes** (RSSBSIM 0.25-0.40 across all
6 configs); none were anchored on **NTSX (US 90/60)**. NTSX's US-equity
+ duration profile differs materially from RSSB's global-equity +
Treasury profile (~0.63 SPY exposure here vs ~0.05-0.10 in DE-005's
configs). The user-flagged 40/30/30 mix in particular has not been
evaluated in any iter.

## Datasets (gating uses gross-of-tax)

- `educational` — VTSIM 56y synth, but constrained to 1995-2026 by KMLM
  inception 1987-12; GDESIM 1968+, NTSX synth from 1986+. Effective
  start ~1995-01-01 to align with KMLMSIM availability.
- `vt_real` — 2008-06 → 2026-04 (~17y).
- `ndx_real` — 2010-02 → 2026-04 (16y), QQQ stretch test.

VT-real proxy: VTSIM (no real VT data yet — flagged in BASE_MEMORY).

## Pre-Committed Kill Criteria

- **Primary kill**: best selected config has 0 datasets where gross
  Sharpe ≥ avg(SPY,VT)_dataset + 0.10. (No edge → close as DE-013 plain
  NTSX+GDE+KMLM stack.)
- **Drawdown kill**: best config educational gross MDD > 35%. (Crash
  exposure too high for "long-term portfolio" mandate.)
- **Robustness kill**: G1 PBO ≥ 0.5 on ≥ 2 of 3 datasets. (Grid
  selection unstable.)

Configs tested: **4** (small grid → DSR n_trials = 4; relaxed
per-iter convention per `WINNER_AND_RANKING.md` §3).

## Pre-Committed Grid (4 configs)

1. `user_primary_403030` — 40% NTSX + 30% GDE + 30% KMLM (user's literal
   architectural preference).
2. `equal_weight_333333` — 33% / 33% / 33% (sensitivity check around
   primary).
3. `equity_tilted_502525` — 50% NTSX + 25% GDE + 25% KMLM (equity-leaning).
4. `mf_tilted_352540` — 35% NTSX + 25% GDE + 40% KMLM (MF-leaning,
   crisis-alpha emphasis).

Selection rule: maximum mean gross Sharpe across the 3 datasets divided
by the per-dataset avg(SPY,VT) Sharpe.

## Datasets to Test

Three: `educational`, `vt_real`, `ndx_real`.

## Tax Reporting

Gross gates everything. Net-of-tax (Lei 14.754, AnnualDarfEngine) is
reported in `final_report.md` as deploy-readiness diagnostic only.
Static stacks rebalance only at year boundaries when forced by DARF
settlement → expected very low tax drag (annual variation captured once
per calendar year, no intra-year rotation events).

## Expected Budget

- Configs: 4
- Wall-time: ~10 min (matches iter 003 footprint, same simulator
  pattern, fewer configs).
- Tax engine: `studies/_shared/tax_engine.py` `AnnualDarfEngine`.

## Implementation Plan

1. Adapt iter 003 backtest scaffolding: keep loaders, gates, scoring
   wiring; replace CONFIGS with the 4 pre-committed grid mixes.
2. Expand stacked synths into testfolio legs:
   - `NTSXSIM = 0.90 SPYSIM + 0.60 IEFSIM − 0.50 CASHX`
   - `GDESIM` already a single ticker (no expansion needed)
   - `KMLMSIM` already a single ticker (no expansion needed)
3. Compute gross + net per config × dataset.
4. Select best by mean gross Sharpe / avg(SPY,VT) Sharpe across 3 datasets.
5. Run 7-gate battery on selected config per dataset using gross returns.
6. Score via `scoring.py:score_strategy` (gross metrics).
7. Persist `results.json`, `verdict.json`, `plot_vs_benchmark_*.png`,
   `final_report.md`. Update `BASE_MEMORY.md` and `DEAD_ENDS.md` per
   PROMPT.
