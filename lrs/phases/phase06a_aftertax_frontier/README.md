# Phase 6A — After-Tax Frontier vs 3 Benchmarks (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Run order note:** the Phase 6 round executes 6C → 6B → 6D → **6A (last)**.

## Question (the user's actual question)

Phase 5 asked "does a satellite **strictly dominate** RSC on 5 metrics?" and
honestly answered no. The user's question is different: **is there a
static-core × LRS-satellite mix whose CAGR/Calmar trade-off is worth giving up
part of a 100%-static position, with portfolio MDD ≤ −50%?** — judged against
three benchmarks on the same window and, unlike Phase 5, with **both legs
after-tax** (Phase 5 mixed gross core with after-tax satellites)
`[testing_tuning, p.327-335]`.

## REVISION (2026-06-09, user correction — supersedes the first run)

The first run taxed the core's monthly rebalance turnover through a unified
`AnnualDarfEngine`. The user corrected the premise: **static portfolios are
rebalanced with new contributions (aportes), not with sells** — so the core
realizes no gains until final liquidation, and pays no intermediate DARF. The
revised tax model below replaces the unified-engine construction; the
`force_rebalance_mask` lib extension stays (generic, regression-guarded) but is
no longer used here. A second part was added per the user's request: a
contribution-based simulation (10k start + 1k/month) where each month buys only
the single most-underweight component — the minimal-trades policy the user
described for IBKR-style cost/tax optimization `[systematic_trading,
p.185-188]`.

## Part 1 — Time-weighted frontier (corrected tax model)

- **Window:** 2000-01-04+ (constrained by `DBMFSIM` inside `RSSTSIM`).
- **Components:** `GDESIM`/`RSSTSIM` from
  `studies/return_stacked_core/us_core/series/return_stacked_core_sleeve_returns.parquet`;
  everything else from the Testfol.io cache (`ZROZSIM` verified identical across
  the two sources, max abs diff 0).
- **Tax model (per leg):**
  - **Core leg (RSC 35/40/25):** gross monthly rebalancing (contribution-funded
    in practice → no realizations), 15% DARF applied **once at final
    liquidation** on the leg's cumulative gain.
  - **Satellite legs (LRS):** full `AnnualDarfEngine` (annual DARF + final
    liquidation) — the weekly rotation genuinely sells, contributions cannot
    avoid those realizations.
  - **Buy-and-hold benchmarks (SSO/SPY):** 15% DARF at final liquidation only.
  - **Mixes:** two-account convention — each leg settles its own taxes; the
    monthly core×satellite re-truing is treated as contribution-funded
    (tax-free) and the leg-level final tax is an approximation, disclosed in
    `tax_method` `[testing_tuning, p.327-335]`.
- **Satellites** (winners of 6B/6D where any, else committed headliners):
  1. `lrs_spy_headline` — Phase 2/4 SPY base (L2.00, 50/25/25, RV21≤30%, lag 3);
     6B SPY failed its screen, so the committed binary base carries.
  2. `lrs_qqq_voltarget` — the Phase 6B QQQ screen SUCCESS (σ_target 40%, RV21,
     lag 1, L_max 1.75, continuous sizing `[systematic_trading, p.137-148]`).
  3. `t3d_k2_saved` — saved letf-lab curve (returns-only; **two-account
     approximation**: after-tax core leg + after-tax saved satellite leg mixed
     via monthly rebalancing, inter-leg rebalance tax not modeled; labeled in
     the `tax_method` column). 6D failed → no inverse satellite.
- **Mix grid:** `w ∈ {0, 5, 10, 15, 20, 25, 30%}` satellite weight, monthly
  rebalanced. **+21 to the n_trials ledger** (18 mixes + 3 standalone satellite
  references on this window) → cumulative lineage 3984 + 21 = **4005**.
- **Benchmarks (all after-tax, same window):**
  1. RSC-US 35/40/25 monthly-rebalanced, taxed (= the `w=0` row);
  2. SSOSIM buy-and-hold, taxed (final liquidation);
  3. SPYSIM buy-and-hold, taxed (final liquidation).

## Part 2 — Contribution simulation (the user's real-world setup)

- **Cash flows:** start equity `USD 10,000`, contribution `USD 1,000` on the
  first trading day of every month thereafter, no withdrawals, **no sells**
  before final liquidation.
- **Buy policy (minimal trades):** each month the whole contribution buys the
  **single component with the largest underweight** vs target (in percentage
  points) — one order per month, minimizing broker friction, as the user
  specified; rebalancing quality is reported as mean absolute weight deviation
  `[systematic_trading, p.185-188]`.
- **Components:** RSC sleeves at `(1−w)·{35/40/25}` plus the satellite leg at
  `w` (satellite component uses its after-tax annual-DARF series; sleeves and
  B&H assets are gross with cost-basis tracking).
- **Final liquidation tax:** 15% on `(value − basis)` per gross component;
  satellite component exempt (its series is already after-tax).
- **Metrics:** net terminal wealth, total contributed, wealth ratio,
  **annualized money-weighted return (IRR)**, equity-path MDD (flagged: monthly
  inflows mechanically soften drawdowns), mean abs weight deviation.
- **Trials:** +0 — same 18 mixes under a different accounting lens (ledger
  stays 4005).

## Pre-registered screen (utility-based — NOT strict dominance)

- **Hard constraint:** portfolio MDD ≥ −50% (user decision for this round).
  Violators are flagged `constraint_ok = False` and still reported.
- **Ranking:** Calmar desc, then CAGR desc, among constraint-passing rows.
- **Reported per row:** CAGR, MDD, Sharpe, Sortino, Calmar, time underwater,
  max recovery days, spreads vs each benchmark, and the four pre-registered
  crisis windows (2000-03-24→2002-10-09, 2007-10-09→2009-03-09,
  2020-02-19→2020-03-23, 2022-01-03→2022-10-12).
- **Output:** a ranked decision table for the user. **No auto-promotion** —
  whatever ranks first still failed (or never ran) the mandate gates; any
  promotion claim would require the full §5 suite with `n_trials ≥ 4005`
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.

## Outputs

`lrs/results/phase06a_aftertax_frontier.csv`, `REPORT.md`, plots (frontier with
benchmarks and the −50% line, log equity, underwater, crisis bars),
`tests/test_lrs_phase06a.py`. Lib change: additive `force_rebalance_mask`
parameter in `lrs/lib/backtest.py::simulate_weight_frame` (default `None`
byte-preserves all existing callers; regression-guarded by test).
