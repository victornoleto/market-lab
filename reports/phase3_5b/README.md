# Phase 3.5b — Winners full validation (main index)

> **Path tag:** `[SWING BROKER]` (Plano B — Brazilian stock broker, 15% IR,
> swap = 0, daily rebalance).
>
> **Branch:** `phase3.5b/winners-validation-20260417`.
>
> **Status:** Phase 3.5b main **PASS** (closed 2026-04-17 10:58, iter 15).
> Phase 3.5b-addendum **PASS** (closed 2026-04-17, iter 23 — this index).

## TL;DR (one paragraph)

Phase 3 promoted four production-ready sleeves on the BR swing-broker
path: **LETF rotation EMA100/2x** on SPX_TR (Gayed regime filter), **QQQ
Donchian 20/10** (trend), **GLD Donchian 40/20** (uncorrelated
diversifier), and the **3-leg equal-weight portfolio** that blends them
with daily reset. Phase 3.5b re-validated all four end-to-end (standard
reports + trade logs + SPY benchmark) and ran a 7-task robustness battery
(FFR-aware LETF cost, isolated stress, slippage sweep, allocation 5-way
comparison, rolling correlation, vol-target sizing). Every test passed
without moving the winners. The addendum then generated three operational
variants requested by the user — a 2-leg LETF+QQQ blend (falls DR gate),
an LETF leverage sweep at 2×/2.5×/3× (only 2× passes every gate), and a
rebalance-cadence comparison (daily/monthly_sell/monthly_cashflow). The
winner deployment blueprint is **unchanged**: a 3-leg EW blend with daily
rebalance, OOS Sharpe 2.108 / CAGR 25.56% / MaxDD −10.86% over 21.36
years. `[advances_fin_ml, p.298-299]`, `[leverage_for_the_long_run, p.16]`.

## Official winners

All four validated on their LONGEST Tiingo-available window (`first_dt` →
`last_dt` per `data/tiingo/manifest.json`). Costs: 5 bps spread + 10 bps
commission round-trip, 15% BR IR per profitable exit, swap = 0. Numbers
below come from `summary.json`.

| Sleeve | Window | CAGR | Sharpe | MaxDD | Trades | IR vs SPY | Report |
|---|---|---|---|---|---|---|---|
| **LETF rotation EMA100/0%/2×** | 1970-01-02 → 2026-04-14 (20 556 d) | **44.69%** | 1.848 | 20.55% | 296 | **1.601** | [`letf_rotation_ema100_2x/`](letf_rotation_ema100_2x/standard_report.md) |
| **QQQ Donchian 20/10** | 2001-05-14 → 2026-04-14 (9 101 d) | 17.40% | 1.389 | 12.79% | 107 | 0.358 | [`qqq_donchian_20_10/`](qqq_donchian_20_10/standard_report.md) |
| **GLD Donchian 40/20** | 2004-11-18 → 2026-04-15 (7 818 d) | 11.46% | 0.937 | 14.35% | 48 | −0.013 | [`gld_donchian_40_20/`](gld_donchian_40_20/standard_report.md) |
| **Portfolio 3-leg EW** | 2004-11-18 → 2026-04-14 (7 817 d, common) | 25.56% | **2.108** | **10.86%** | 259 | 0.722 | [`portfolio_3leg_ew/`](portfolio_3leg_ew/standard_report.md) |
| _SPY buy-and-hold (benchmark)_ | _same 21.36 yrs_ | _10.66%_ | _0.629_ | _−55.20%_ | — | _0.000_ | — |

The portfolio sleeve is the **production default**: lowest MaxDD (10.86%),
highest Sharpe (2.108), and its drawdown in the 2008 / 2020 / 2022 / 2025
stress windows never exceeds 6.85% (Task 7b). The three single-sleeve
reports remain shipped mainly as accounting primitives — they document
where the alpha comes from and why removing any one of them hurts the
blend — but `docs/phase3_winners_allocation.md` commits the project to
**one** live portfolio, not three separate strategies.

### Per-sleeve TL;DR

1. **LETF rotation EMA100/2×** — Gayed regime filter on a 2× SSO-synthetic
   series [`leverage_for_the_long_run, p.16`]. The 56-year backtest is a
   stress test, not a claimed capital trajectory: the `$108 T` final
   equity is a pure compound artefact. What matters is that CAGR, Sharpe
   and MaxDD stay inside the gate in every walk-forward window
   (`reports/phase3_5b/letf_rotation_ema100_2x/standard_report.md`).

2. **QQQ Donchian 20/10** — classic trend breakout with 20-bar entry /
   10-bar exit. Exposure 49.9% ⇒ half the capital sits idle, but in the
   blend that idle cash becomes LETF/GLD exposure. 65.4% win rate, profit
   factor 5.63.

3. **GLD Donchian 40/20** — single-sleeve Sharpe is sub-1.0, and this
   is expected: GLD is included as a **decorrelator**, not a CAGR engine.
   Its role is confirmed in Task 7e — GLD's rolling-ρ vs both equity
   legs stays below 0.30 over 21 years `[expected_returns_ilmanen, p.353]`.

4. **Portfolio 3-leg EW** — daily reset to (1/3, 1/3, 1/3). Beats the
   best single sleeve on Sharpe (2.108 > 1.848) and collapses MaxDD from
   the LETF sleeve's 20.55% to 10.86%. Rebalance-tax incidence isolated
   in `variants/rebalance_modes/` (see below).

## Robustness battery (all PASS)

Each sub-report lives in [`robustness/`](robustness/). All seven checks
left the winner list unchanged.

| Task | Test | Verdict |
|---|---|---|
| 7a | FFR-aware LETF cost (Ken-French daily × 0.4% spread + 0.95% ER) | **PASS** — 13/13 passing configs identical; winner DSR p = 2.19e-05 |
| 7b | Isolated stress 2008 / 2020 / 2022 / 2025 | **PASS** — portfolio DD ≤ 6.85% in all four |
| 7c | Slippage sweep 0 / 1 / 5 / 10 bps | **PASS** — Sharpe sensitivity ~ −0.005 / bp |
| 7d | Allocation 5-way (EW / IVP / HRP / RP / MV) | **PASS** — EW retains by double-margin rule `[advances_fin_ml, p.298-299]` |
| 7e | Rolling-ρ 63d / 252d on 3 pairs | **PASS** — zero regime with 3 ρ ≥ 0.70 simultaneously in 21 yrs |
| 7f | Vol-target 10% (9 configs) | **PASS** — no challenger wins double margin; noted as opt-in defensive `[systematic_trading_carver, p.107-111]` |

## Operational variants (addendum 2026-04-17)

**Subdirectory:** [`variants/`](variants/README.md) — full comparative
sub-index.

The addendum answered three user questions without touching the winner.
Nothing here replaces the production default; everything runs end-to-end,
gate failures become ⚠️ FLAGs inside the per-variant `flags.md`. The rule
is *show all, flag failures* (`specs/phase_3_5b_addendum_operational.md` §0).

| Question | Output | Verdict (vs 3-leg EW daily) |
|---|---|---|
| **A.** What if I drop GLD (2-leg LETF+QQQ)? | [`variants/letf_qqq_2leg_ew/`](variants/letf_qqq_2leg_ew/standard_report.md) | Sharpe 1.888 (−0.22), MaxDD 14.41% (+3.55 pp). ⚠️ FAIL DR 1.121 < 1.20 — doubling-down on US equity. Deploy only if broker blocks GLD. |
| **B.** Could I go 2.5× or 3× instead of 2× on the LETF leg? | [`variants/letf_leverage_comparison/`](variants/letf_leverage_comparison/README.md) | Sharpe flat (1.848 → 1.882 → 1.910); MaxDD blows up (20.55 → 24.65 → 28.45). 3× fails WF MaxDD gate 3/8 windows; 2.5× passes but is synthetic-only (no listed ETF). **Keep 2×**. |
| **C.** Can I rebalance monthly instead of daily? | [`variants/rebalance_modes/`](variants/rebalance_modes/README.md) | Daily wins Sharpe on both 2-leg and 3-leg. Monthly_sell drops Sharpe by ~0.1 and pays $30 k–$145 k / yr in IR. Monthly_cashflow ($500 / mo) matches daily Sharpe on 2-leg (tax-free) but adds +3.74 pp to MaxDD. |

The addendum-specific artefacts are produced by three scripts under
`scripts/`: `run_phase3_5b_task_a_2leg.py`,
`run_phase3_5b_letf_leverage_variant.py`,
`run_phase3_5b_task_c{2,3}_rebalance_{3,2}leg.py`. The shared module
`src/ai_trade/backtest/metrics/rebalance_modes.py` (~320 loc, 3 pure
functions, 28 unit tests) implements the three cadences with proportional
cost-basis tax accounting.

## Directory map

```
reports/phase3_5b/
├── README.md                                  # this file
├── summary.json                               # consolidated metrics for the four winners
├── letf_rotation_ema100_2x/                   # LETF winner, 1970-2026
├── qqq_donchian_20_10/                        # QQQ winner, 2001-2026
├── gld_donchian_40_20/                        # GLD winner, 2004-2026
├── portfolio_3leg_ew/                         # 3-leg portfolio, common window
├── robustness/                                # Tasks 7a-7f: FFR / stress / slippage / allocation / ρ / vol-target
└── variants/                                  # Phase 3.5b-addendum (A/B/C)
    ├── README.md                              # sub-index, comparative tables
    ├── letf_qqq_2leg_ew/                      # A: drop GLD
    ├── letf_leverage_comparison/              # B: 2× / 2.5× / 3× sweep
    │   ├── letf_ema100_2x/                    # symlink reuse of winner
    │   ├── letf_ema100_2_5x/                  # synthetic-only, ⚠️ THEORY
    │   └── letf_ema100_3x/                    # ⚠️ FAIL WF MaxDD gate
    └── rebalance_modes/                       # C: daily / monthly_sell / monthly_cashflow
        ├── comparison_3leg.md
        ├── comparison_2leg.md
        └── implementation_notes.md
```

## Citations

- Naive EW's robustness to Σ-estimation error: `[advances_fin_ml, p.298-299]`.
- DR formula (Choueifaty-Coignard 2008): `[advances_fin_ml, p.310]`.
- LETF synthetic formula and leverage grid: `[leverage_for_the_long_run, p.16-17, Table 8]`.
- TSMOM Donchian params: `[stocks_on_the_move, p.81]`, `[following_the_trend, ch.3]`.
- Vol-target sizing reference: `[systematic_trading_carver, p.107-111]`.
- Gold diversification role: `[expected_returns_ilmanen, p.353]`.
- 15% BR IR on realized gains: `docs/investment-mandate.md` §4.
- WF MaxDD ≤ 25% gate: `docs/investment-mandate.md` §5.

## Related jornadas

- [`2026-04-17-2045-phase3.5b-full-validation-summary.md`](../../jornada/2026-04-17-2045-phase3.5b-full-validation-summary.md) — Phase 3.5b main summary (PASS verdict).
- [`2026-04-17-2100-phase3.5b-addendum-task-a-2leg-letf-qqq.md`](../../jornada/2026-04-17-2100-phase3.5b-addendum-task-a-2leg-letf-qqq.md) — Task A (2-leg DR FAIL).
- [`2026-04-17-2115-phase3.5b-addendum-task-b1-letf-2x-reuse.md`](../../jornada/2026-04-17-2115-phase3.5b-addendum-task-b1-letf-2x-reuse.md) — Task B1 (2× baseline reuse).
- [`2026-04-17-2130-phase3.5b-addendum-task-b2-letf-2_5x-synthetic.md`](../../jornada/2026-04-17-2130-phase3.5b-addendum-task-b2-letf-2_5x-synthetic.md) — Task B2 (2.5× synthetic).
- [`2026-04-17-2145-phase3.5b-addendum-task-b3-letf-3x.md`](../../jornada/2026-04-17-2145-phase3.5b-addendum-task-b3-letf-3x.md) — Task B3 (3× FAIL MaxDD gate).
- [`2026-04-17-2200-phase3.5b-addendum-task-c1-rebalance-modes-module.md`](../../jornada/2026-04-17-2200-phase3.5b-addendum-task-c1-rebalance-modes-module.md) — Task C1 (module + 28 tests).
- [`2026-04-17-2215-phase3.5b-addendum-task-c2-rebalance-3leg.md`](../../jornada/2026-04-17-2215-phase3.5b-addendum-task-c2-rebalance-3leg.md) — Task C2 (3-leg cadence sweep).
- [`2026-04-17-2230-phase3.5b-addendum-task-c3-rebalance-2leg.md`](../../jornada/2026-04-17-2230-phase3.5b-addendum-task-c3-rebalance-2leg.md) — Task C3 (2-leg cadence sweep).
- [`2026-04-17-2245-phase3.5b-addendum-summary.md`](../../jornada/2026-04-17-2245-phase3.5b-addendum-summary.md) — Task D (this index).

## Pytest baseline

550 (iter 0) → 670 (iter 15, Phase 3.5b main) → **698** (iter 20, addendum
Task C1). Zero flakiness, zero regression. Winners immutable throughout.
