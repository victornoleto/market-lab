# Iter 024 — iter 011 + MDD-trigger defensive (regime-conditional)

**Hypothesis slug**: `iter011-MDD-trigger-defensive`
**Direction**: B.2 (regime-gated defensive — distinct from iter 017 B.6)
**Cumulative n_trials at start**: 87 (post-iter 023)

## Citação primária

`[systematic_trading, p.137-148]` — Carver position sizing / regime-conditional
weight allocation.
`[advances_fin_ml, p.208-211, p.222-223]` — PBO/DSR; ≤3 configs limita penalty.
`[risk_parity, ch.5, p.10]` — Carlson capital-efficient base.

## Hipótese

Quando SPY trailing-21d return < threshold negativo (drawdown signal), reduzir
50% do equity sleeve (NTSX) e adicionar TLT ou CASH no lugar; quando SPY 21d
voltar acima do threshold, voltar pra base iter 011.

**Crucial**: signal é forward-looking — trigger detecta past drawdown
(observable HOJE), action é next-day rebalance. Sem hindsight, sem peek.

Isso é **fundamentalmente diferente de iter 017** (B.6 VBRSIM regime-gated)
em duas dimensões:
1. **Signal source**: SPY 21d return (broad-market drawdown), não factor-specific.
2. **Action**: defensive shift na base, não factor weight binary.

E **fundamentalmente diferente de iter 022** (sintético tail-hedge): aqui usa
só ativos REAIS (TLT, CASHX), sem retornos modelados.

## 3 configs pre-committed (≤3 pra DSR penalty)

Base ON (default iter 011): 35% NTSX + 25% GDE + 40% KMLM
Quando trigger fires (SPY 21d < threshold), shift para:

| config | trigger | OFF state |
|---|---|---|
| `mdd_trigger_10pct_TLT` | SPY 21d < −10% | 17.5% NTSX + 25% GDE + 40% KMLM + **17.5% TLT** |
| `mdd_trigger_15pct_TLT` | SPY 21d < −15% | 17.5% NTSX + 25% GDE + 40% KMLM + **17.5% TLT** |
| `mdd_trigger_15pct_CASH` | SPY 21d < −15% | 17.5% NTSX + 25% GDE + 40% KMLM + **17.5% CASHX** |

50% reduction of NTSX → +17.5% defensive sleeve. Direção: defensive em
crashes, recovery quando rally retoma.

**Selection rule**: max mean(gross_Sharpe / SPY_Sharpe) sob NEW SPY-only.

## Datasets

`lh_56y`, `vt_real`, `ndx_real`. SPY 21d signal disponível em todos.

## Pre-committed KILLs

- **KILL #1 (whipsaw kill)**: signal fires > 30% of time on average; significa
  trigger overactive (capturando noise não crash). Threshold mal-calibrado.
- **KILL #2 (no-edge kill)**: best-of-grid loses iter 011 substantively em
  ≥2/3 datasets (Δ Sharpe ≤ 0).
- **KILL #3 (cross-config monotonic regression)**: tighter trigger
  (10%→15%) reduces Sharpe em 3/3 datasets.

## Probabilidade estimada

~20-25% — whipsaw cost + DSR penalty de 3 configs. Trigger 10% pode
fire 30+% of time (e.g., 2008 GFC tem multiple sub-10%-21d periods; 2022
correção sustentada também). Trigger 15% raro mas pode missar slow grinds.

## Saída esperada

- verdict.json + score_legacy
- results.json com pct_on por dataset
- final_report.md com whipsaw analysis
- equity curve + rolling Sharpe + signal time-series
