# B4-v2 Stacked-ETF Triage GA — Report

Status: **discovery-only triage.** Tests whether a 21-ticker universe including 8
locally-built stacked-ETF proxies (CTAPSIM, RSBTSIM, RSITSIM, HOLDSIM, MATESIM,
ESBGSIM, GDTSIM, ALLWSIM) plus 5 additional Testfol.io pulls (NTSXSIM, NTSDSIM,
NTSISIM, BTALSIM, IEISIM) can produce a static portfolio that beats the
**B4-v2 core (35% GDESIM / 40% RSSTSIM / 25% ZROZSIM)** under the
`core_relative_wealth_dominance` fitness. No deploy authorization, no mandate
change `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

## Headline

| | Fitness | CAGR | MDD | Calmar | Terminal wealth |
|---|---:|---:|---:|---:|---:|
| **B4-v2 core (35/40/25)** | **+0.3500** | 15.25% | **-28.02%** | **0.544** | 27.1× |
| GA best across 3 seeds | +0.2681 | 16.04% | -30.97% | 0.518 | 31.8× |
| Delta (GA - core) | **-0.0819** | +0.79pp | +2.95pp worse | -0.026 | +4.7× |

**Verdict:** core survived. No challenger from the expanded stacked-ETF universe
beat the core under the rolling-dominance objective across 3 independent seeds.

## Setup

| Parameter | Value |
|---|---|
| Universe | `core_beater_stacked_expansion` (21 tickers) |
| Common window | 2003-01-03 .. 2026-04-17 (23.25y, 5859 bars; binding: ALLWSIM/GDTSIM 2003+) |
| Fitness | `core_relative_wealth_dominance` |
| Population | 120 |
| Generations | 80 (early-stop patience 20) |
| Max active assets | 8 |
| Rolling step | 21 (monthly sampled discovery) |
| Finalist exact | Top 80 re-ranked at rolling step 1 |
| Seeds | 20260519, 20260520, 20260521 |
| Fast discovery | Yes (MDD/Calmar skipped during discovery) |

## Universe

| Family | Tickers |
|---|---|
| B4-v2 anchors | GDESIM, RSSTSIM, ZROZSIM |
| Alt stacked equity+MF | CTAPSIM, RSBTSIM, MATESIM, HOLDSIM |
| International stacked | RSITSIM, RSSBSIM, NTSXSIM, NTSISIM, NTSDSIM |
| All-weather/inflation | ESBGSIM, ALLWSIM, GDTSIM |
| Alpha sleeves | BTALSIM, DBMFSIM, KMLMSIM |
| Treasury | IEISIM, IEFSIM |
| Cash | CASHX |

## Top-5 across all 3 seeds (de-duped, sorted by fitness)

| Seed | Rank | Fitness | CAGR | MDD | Calmar | TW | Allocation |
|---|---:|---:|---:|---:|---:|---:|---|
| 20260521 | 1 | 0.2681 | 16.04% | -30.97% | 0.518 | 31.8× | 30 RSST / 25 ESBG / 20 GDE / 15 ZROZ / 5 CTAP / 5 MATE |
| 20260519 | 1 | 0.2650 | 16.17% | -31.70% | 0.510 | 32.6× | 30 RSST / 25 GDE / 20 ESBG / 15 ZROZ / 5 CTAP / 5 MATE |
| 20260519 | 2 | 0.2647 | 15.97% | -30.99% | 0.516 | 31.4× | 25 ESBG / 25 RSST / 20 GDE / 15 ZROZ / 10 MATE / 5 CTAP |
| 20260519 | 3 | 0.2642 | 15.92% | -30.84% | 0.516 | 31.0× | 35 GDE / 25 RSST / 20 ZROZ / 10 ESBG / 5 CTAP / 5 MATE |
| 20260521 | 3 | 0.2625 | 16.00% | -30.85% | 0.519 | 31.5× | 30 ESBG / 30 RSST / 15 GDE / 15 ZROZ / 10 CTAP |

## Benchmarks (same 2003-2026 window)

| Benchmark | CAGR | MDD | Calmar | TW | Fitness vs core |
|---|---:|---:|---:|---:|---:|
| SPY buy-hold | 11.36% | -55.14% | 0.206 | 12.2× | -2.169 |
| QQQ buy-hold | 15.79% | -53.41% | 0.296 | 30.2× | -0.773 |
| Equal-weight (21 tickers) | 10.35% | -23.31% | 0.444 | 9.9× | -2.213 |
| B4 original (25/25/25/25) | 13.78% | -27.28% | 0.505 | 20.1× | -1.344 |
| **B4-v2 core (35/40/25)** | **15.25%** | **-28.02%** | **0.544** | **27.1×** | **+0.350** |

## Convergence pattern

All 3 seeds converged on similar structure:

- **Anchors retained:** GDESIM (15-35%), RSSTSIM (15-30%), ZROZSIM (15%) — the core sleeves never disappear.
- **Common tilt:** ESBGSIM appears in **every** top-5 candidate across all seeds, usually 10-30%.
- **Small boosters:** CTAPSIM (5-10%) and MATESIM (5-15%) frequently selected as accents.
- **Never selected:** RSBTSIM, RSITSIM, HOLDSIM, ALLWSIM, GDTSIM, BTALSIM, NTSXSIM, NTSDSIM, NTSISIM, RSSBSIM, KMLMSIM, DBMFSIM, IEISIM, IEFSIM, CASHX. None of these survived into any seed's top-5.

Interpretation: GA prefers to substitute part of the core sleeves with `ESBGSIM`
(SPY + IEI + Gold stack) and accent with `CTAPSIM`/`MATESIM` (additional MF style
diversification). But these substitutions raise CAGR modestly while worsening
MDD and rolling dominance — net negative on `core_relative_wealth_dominance`.

The alpha sleeve (`BTALSIM`) and the all-weather/inflation stacks (`ALLWSIM`,
`GDTSIM`) failed to compete on this objective despite their conceptual appeal.
The international stacks (`RSSBSIM`, `NTSISIM`, `NTSDSIM`) also failed.

## Why the GA lost to the core

The core_relative_wealth_dominance fitness rewards:
1. Rolling 1/3/5/10/15/20y wealth dominance vs the core (win-rate p10/median).
2. Full-period CAGR spread vs core.
3. Calmar spread vs core.
4. MDD as guardrail/penalty.

GA candidates achieved (+0.79pp) CAGR over core but lost on:
- **MDD penalty:** all top candidates have MDD ~31% vs core's -28%.
- **Calmar:** lower (~0.51 vs 0.544) → penalty stacks.
- **Rolling win-rate:** failing to dominate core in enough monthly rolling windows means rolling p10 spreads are slightly negative — fitness penalty.

The core 35/40/25 is genuinely at a stable Pareto point: pushing CAGR up costs
disproportionately more in MDD/rolling dominance.

## Important caveats

This triage uses **locally-built proxy SIMs** for CTAP/RSBT/RSIT/HOLD/MATE/ESBG/GDT/ALLW.
A sanity check against the real RSST in the cache showed the proxy formula
(`SPY + DBMF - 1.0 × CASHX`) overestimates CAGR by approximately `5.5pp` versus
the real RSST over 2023-09 to 2026-04 (proxy: 25.54% vs real 19.98%).

Implications:

- The same overestimation bias likely applies to all 8 proxies, especially
  those using `DBMFSIM` to substitute proprietary MF strategies.
- **Real ETF returns will be materially lower** than these proxy backtests imply,
  due to fund-level ER (~0.85-1.20% pa), financing cost differences, and
  strategy implementation drift.
- This triage GA is therefore a discovery-only signal: the **conclusion that
  core wins is more robust than any specific candidate's absolute numbers**.
- Even with proxy-inflated CAGRs, no GA candidate beat the core — this is
  strong evidence the core is genuinely competitive, not a weak baseline.

## Recommendation

- **Stop expanding the static stacked-ETF universe** for now. The 35/40/25 core
  has resisted 4 separate GA challenges (Phase 1 levered-equity, factor probe
  with VBR/MTUM/EFV, no-margin Pareto search, and now this stacked expansion).
- **Maintenance-mode mandate §1 unchanged**: 100% capital remains in passive
  factor-tilted Plano C; B4-v2 remains discovery-only internal benchmark.
- **Next research direction (if any):** implementation realism checks on the
  core itself — drag/fee stress, rebalance frequency, BR broker availability,
  remove-one-asset tests — rather than more static optimization.
- **If a user wants to test a specific stacked variant operationally:** promote
  the proxy to a Testfol.io SIM pull (RSBT/CTAP do not exist as native Testfol.io
  SIMs, so this means committing to manual data construction with fund-level
  cost modeling) before any deploy claim.

## Artifacts

- Per-seed GA outputs: `core_beater_stacked_expansion_core_relative_wealth_dominance_seed{20260519,20260520,20260521}/`.
- Proxy build script: `scripts/build_stacked_sim_proxies.py`.
- Proxy formula metadata: `data/testfolio/cache/stacked_proxies.meta.json`.
- Universe definition: `studies/static_spy_beater_portfolio/scripts/universe.py` → `core_beater_stacked_expansion`.
- Core benchmark: `studies/static_spy_beater_portfolio/scripts/universe.py` → `CORE_35_40_25_WEIGHTS`.
- B4-v2 canonical writeup: `B4_V2_STRATEGY.md` (repo root).
