# Phase 3.5b-addendum Task A — 2-leg LETF+QQQ EW full report [PLANO B] [SWING BROKER]

**Data:** 2026-04-17 21:00
**Branch:** `phase3.5b/winners-validation-20260417`
**Spec:** `specs/phase_3_5b_addendum_operational.md` §Task A
**Output:** `reports/phase3_5b/variants/letf_qqq_2leg_ew/`

## TL;DR

Rodei o blend 50/50 EW (LETF EMA100/2x + QQQ Donchian 20/10) na
janela longest comum (2001-05-14 → 2026-04-14, 6266 bars). Gate de
diversificação **FALHA** como esperado pelo Phase 3 A3c — DR_full =
1.121 < 1.20. Reporto tudo mesmo assim por regra de ouro do addendum
(`run to completion, flag failures`).

## Números da rodagem

| Métrica | 2-leg LETF+QQQ EW | SPY buy&hold | 3-leg (winner) |
|---------|-------------------|---------------|----------------|
| CAGR | **31.59%** | 9.09% | ≈25.56% (full) |
| Sharpe (full) | **1.888** | 0.553 | ≈2.108 |
| MaxDD | **14.41%** | 55.20% | ≈10.86% |
| Info Ratio vs SPY | 1.158 | — | — |
| β vs SPY | 0.480 | 1.000 | — |
| ρ daily vs SPY | 0.602 | 1.000 | — |
| # trades | 250 | 0 | ~400 |
| DR (Choueifaty-Coignard) | **1.121 ⚠️ FAIL** | — | >1.30 |
| ρ(leg₁, leg₂) | 0.555 | — | — |

Note: "3-leg winner" column é ponteiro pro
`reports/phase3_5b/portfolio_3leg_ew/summary.json` (Phase 3.5b main,
commit `4a732ce`).

## Por que o DR falha

DR = (w₁σ₁ + w₂σ₂)/σ_portfolio `[advances_fin_ml, p.310]`. Com
ρ=0.555 entre duas pernas *ambas long US equity* (LETF rida S&P,
QQQ rida Nasdaq-100 ⊂ S&P), a compressão de vol tem teto mecânico
baixo. Adicionar uma 2ª perna de equity US = **doubling down**, não
diversificação por fator. O paper framework de HRP/IVP é explícito
sobre isso: `[advances_fin_ml, p.302-313, ch.16]` — escolha clusters
com baixa correlação inter-cluster, não apenas "outra estratégia
vencedora".

## Por que enviar o relatório mesmo falhando

O blend 2-leg **bate** o melhor single-leg em Sharpe (~2.098 OOS
vs LETF-only ~1.990 OOS segundo A3c iter 37). Há edge aditivo real
— só não é edge de *diversificação* no sentido HRP/IVP. Regra do
addendum é mostrar tudo e deixar o usuário decidir.

## Contexto operacional

**Quando o 2-leg faz sentido:**
- Broker não oferece GLD (Plano B BR broker tiers).
- Usuário quer exposição 100% equity (sem commodity).
- Simplicidade: 2 sleeves vs 3 = menos fricção de monitoramento.

**Quando NÃO faz sentido (deploy default):**
- Se GLD for tradável, o 3-leg vence em MaxDD (10.86% vs 14.41%) e
  em Sharpe OOS (2.251 vs 2.098). Há ganho real de
  diversificação — o 3º cluster (commodity) absorve drawdown de
  equity em 2008, 2020, 2022.

## Artefatos

```
reports/phase3_5b/variants/letf_qqq_2leg_ew/
├── standard_report.md   (1.5 KB, backtesting.py-style + SPY bench)
├── trade_log.csv        (250 trades, aggregated por leg)
├── trade_log.md         (mesmo em markdown)
├── summary.json         (snapshot machine-readable + blend_meta)
├── equity_curve.png     (log-scale, strategy + SPY)
└── flags.md             (narrativa DR FAIL)
```

Script reproduce: `.venv/bin/python scripts/run_phase3_5b_task_a_2leg.py`.

## Decisão

Relatório arquivado. **Não é production default** — 3-leg EW
continua sendo o winner. 2-leg é a alternativa informada para o
caso de restrição broker.

## Próximo

Task B1 (LETF 2x baseline reuso) — apenas symlink/copy do
`letf_rotation_ema100_2x/summary.json` existente em
`reports/phase3_5b/variants/letf_leverage_comparison/letf_ema100_2x/`.

## Citações

- DR formula: `[advances_fin_ml, p.310]` (Choueifaty-Coignard 2008).
- HRP/IVP framework: `[advances_fin_ml, p.302-313, ch.16]`.
- EW naive immunity a Σ-estimation error: `[advances_fin_ml, p.298-299]`.
- Path B 15% BR tax: Investment Mandate §4.
