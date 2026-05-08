# Iter 023 — iter 011 + 15% TLT sleeve

**Hypothesis slug**: `iter011-plus-TLT-sleeve`
**Direction**: B.1 (TLT sleeve diversifier; previously surfaced in iter 020 All-Weather)
**Cumulative n_trials at start**: 83 (post-iter 022)

## Citação primária

`[risk_parity, ch.5, p.10]` — Carlson capital-efficient stacking + TLT como
diversificador descorrelacionado em portfólios all-weather/risk-parity.
`[advances_fin_ml, p.208-211, p.222-223]` — PBO/DSR discipline para multi-config sweep.

## Contexto — por que TLT sleeve agora

iter 020 (C.3 All-Weather Bridgewater-mimic) testou 4 configs incluindo
`aw_levered_NTSX_GDE_TLT` (40% NTSX + 30% GDE + 15% KMLM + 15% TLT) e
encontrou ndx_real Sharpe **1.120** — a **única** config do loop a bater
iter 011's ndx_real (1.104) por +0.016. Iter 020 selecionou Browne
(`aw_browne_25252525`) que vence em mean-Sharpe-vs-bench mas falha CAGR floor.
TLT sleeve permaneceu como sub-finding não-isolado.

Esta iter testa TLT em isolamento sobre a base iter 011 (NTSX+GDE+KMLM)
sem o complexity overhead de inv-vol ou Browne 25/25/25/25.

## Hipótese H1 — sweep de intensidade TLT

**Hipótese**: 15-30% TLT sleeve substituído proporcionalmente de NTSX e KMLM
preserva o CAGR de iter 011 (~11.6%) enquanto adiciona duration alpha
descorrelacionado, melhorando Sharpe em ≥2/3 datasets.

**Mecanismo**: NTSX já contém 60% IEF (intermediate Treasury). TLT (long
Treasury 20+y) tem duration ~17y vs IEF ~7y. Em regimes de declining rates
ou flight-to-quality (2008, 2020-Q1), TLT tem convexidade maior que IEF.
KMLM portion absorve parte do shift (managed-futures ainda diversifica).

## 4 configs pre-committed (sweep TLT intensity)

iter 011 base = 35% NTSX + 25% GDE + 40% KMLM. Variantes:

| config | NTSX | GDE | KMLM | TLT | racional |
|---|---:|---:|---:|---:|---|
| `tlt_lite_30_25_30_15` | 30% | 25% | 30% | **15%** | TLT mínimo, NTSX+KMLM cada -5% |
| `tlt_mod_25_25_35_15` | 25% | 25% | 35% | **15%** | preserva KMLM, NTSX absorve perda |
| `tlt_balanced_30_25_25_20` | 30% | 25% | 25% | **20%** | TLT moderado |
| `tlt_heavy_25_20_25_30` | 25% | 20% | 25% | **30%** | TLT máximo, GDE também recua |

**Selection rule**: max mean(gross_Sharpe / SPY_Sharpe) across 3 datasets sob
**NEW SPY-only mandate** (post-reframing 2026-04-29). Esta é a primeira iter
sob novo critério — selection bar é SPY+0.05 (era avg(SPY,VT)+0.10).

## Datasets

`lh_56y` (1970+), `vt_real` (2008-06+), `ndx_real` (2010-02+).

TLTSIM (testfolio synth, 1962+) cobre todos os datasets sem bottleneck.

## Pre-committed KILLs

- **KILL #1**: best-of-grid loses iter 011's substantive Sharpe em ≥2/3
  datasets (Δ ≤ 0 vs lh_56y 1.046, vt_real 0.960, ndx_real 1.104).
- **KILL #2**: cross-config monotônico — TLT 15%→30% reduz Sharpe em 3/3
  datasets (mesma falha estrutural de iter 014 VXUSSIM).
- **KILL #3**: `winner_conditions_met=False` sob NEW scoring (SPY-only,
  +0.05) — i.e., não passa Sharpe edge na maioria dos datasets.

## Probabilidade estimada (pre-commit)

~30-35% — iter 020 mostrou um único dataset com edge marginal positivo;
isolando TLT sob nova baseline SPY mais discriminante (vt_real hurdle
sobe de 0.807 pra 0.950) há risco real de falhar vt_real.

## Saída esperada

- `verdict.json` — score sob NEW scoring + `score_legacy` reportado pra cross-iter compat
- `results.json` — full grid sweep + selected config
- `final_report.md` — análise + decisão (advance / KILL / tier)
- `equity_curve.png`, `rolling_sharpe.png`
