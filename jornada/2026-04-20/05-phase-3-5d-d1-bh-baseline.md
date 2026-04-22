# Phase 3.5d — Lead D1: O chão que precisa ser batido [SWING BROKER]

**Data:** 2026-04-20  
**Fase:** 3.5d — Plano B V2 3× LETF swing  
**Lead:** D1 — Buy-and-hold 3× LETF baseline (iter 0)

---

## O que foi feito

Antes de buscar uma estratégia de timing (entrar e sair do mercado no
momento certo), precisávamos saber: **só de comprar UPRO/TQQQ e segurar,
a gente já bate o SPY?**

Rodamos 6 carteiras de compra-e-segura (buy-and-hold) com 3× LETFs na
janela 2010-02-11 → 2026-04-14 (~16 anos), incluindo o imposto de 15%
da Receita Federal.

## Resultado

Resposta: **sim, buy-and-hold UPRO/TQQQ bate o SPY com folga**. O
SPY rendeu ~10.4%/ano líquido. O TQQQ sozinho rendeu ~35%/ano líquido.
A carteira EW 50/50 UPRO+TQQQ rendeu ~30.75%/ano líquido.

Mas — e aqui está o problema — os **drawdowns são absurdos**:
- UPRO sozinho caiu 76.8% no pior momento (crise 2022, COVID 2020)
- TQQQ caiu 81.7%
- Mesmo adicionando TMF (títulos do tesouro 3×) na carteira, a queda máxima
  ficou em 70.2%

O indicador "Calmar" mede CAGR/MaxDD. Para a carteira ter qualidade
aceitável, precisamos de Calmar > 0.5. Só o TQQQ sozinho chegou lá
(0.504) — os demais ficam entre 0.386 e 0.492.

## O que isso significa para as próximas estratégias

Este resultado estabelece o **chão**: qualquer estratégia de timing
(D2–D8) que não superar ~30%/ano líquido não vale a pena — é mais
simples só comprar e segurar.

Mas o **teto** também está definido: se a estratégia de timing reduzir
o MaxDD para ~40-50% (ao ficar em caixa nos crashes) enquanto mantém o
CAGR ≥ 30%, ela atingiria Calmar ≥ 0.6+ e venceria o buy-and-hold puro
em qualidade.

A estratégia D2 (MA regime filter de Gayed) é exatamente esse tipo de
candidato: quando o mercado entra em bear (SPY abaixo da média 200 dias),
o sistema vai para caixa ou ouro — potencialmente evitando -76% de perda
enquanto captura a maior parte do bull.

## Próximo passo

Lead D2 — testar MA regime filter (SMA200 / EMA100) sobre UPRO e TQQQ.
`[leverage_for_the_long_run, p.13]`

---

*Relatório completo: `reports/phase_3_5d/d1_bh_baseline/REPORT.md`*
