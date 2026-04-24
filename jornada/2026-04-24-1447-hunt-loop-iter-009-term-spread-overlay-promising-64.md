# Hunt loop iter 009 — Term-spread overlay no blend vol-managed dá 64/100 PROMISING, regressão vs iter 008 (Kill #3 TRIGGERED)

**Data:** 2026-04-24 14:47
**Contexto:** Mandate §1 MAINTENANCE mode segue 100% Plano C. Esta é
pesquisa de background — o que iter 009 descobre NÃO move capital.

---

## TL;DR

Tentei compor o blend vol-managed SPY+TLT do iter 008 (score 74/100, o
**recorde do loop**) com um sinal macro: o "term spread" T10Y3M
(diferença entre juros do Treasury de 10 anos vs 3 meses). A tese: quando
a curva de juros inverte, vale reduzir exposição antes da recessão
chegar. Resultado: **a sobreposição destruiu −10 pontos de score**. Iter
008's 74 → iter 009's 64. Kill #3 disparou (score < 65 era o ponto de
corte pré-comprometido).

Iter 008 continua sendo o melhor resultado do loop.

---

## O que iter 009 testou

O blend SPY+TLT do iter 008 pondera os dois ativos por risco (inverse
variance) e reescala o portfolio inteiro para variância-alvo constante.
Sozinho, ele bateu 6/7 gates em todos os 3 datasets e chegou a 4/5
condições de winner — o único gate que falha é o G2 DSR (deflator de
Sharpe estatístico).

O raciocínio do iter 009: se compuser o blend com um sinal **ortogonal**
que veja algo que o blend não vê, posso empurrar o Sharpe acima da
barreira do DSR. O blend reage depois da volatilidade subir; term spread
historicamente antecipa recessões por 6-18 meses. Logo, seriam sinais
complementares.

Sinal escolhido: **T10Y3M com EMA de 21 dias (≈1 mês), threshold 0.0
(inversão clássica), haircut 50% nas duas pernas quando invertido**.
Citação primária: Estrella & Mishkin 1998 *Review of Economics and
Statistics* (o paper seminal da inversão da curva como preditor de
recessão); framework de regime em `[regime_change, ch.2]` (Chen & Tsang
2020).

---

## O resultado

- Sharpe **caiu** em todos os datasets vs iter 008:
  - educational 0.836 (iter 008: 0.865) — Δ −0.029
  - spy_real 0.979 (iter 008: 1.000) — Δ −0.021
  - ndx_real 1.007 (iter 008: 1.021) — Δ −0.014
- Apenas **1/3** datasets cruza a barreira +0.10 Sharpe sobre o bench
  (iter 008 cruzava 2/3). Isso custou 10 pontos do rubric.
- CAGR caiu ~1.5-1.9 pp em cada dataset; MDD até melhorou 1 pp (o gate
  de fato reduz drawdown — mas o custo em CAGR foi maior).
- Gates 6/6/6 (mesma soma do iter 008); robustez 9/9 (igual); DSR
  piorou levemente (0.340/0.363/0.350 vs 0.291/0.332/0.329).
- **Score 64/100 PROMISING** — abaixo do Kill #3 threshold de 65.
  Hipótese rejeitada per pre-commit.

---

## Por que a sobreposição falhou

Diagnóstico post-mortem expôs a razão: **100% dos bars onde o gate
dispara (no educational e no spy_real) coincidem com bars em que o
blend já está no bottom-20% da escala** — ou seja, o sinal macro não
chegou *antes* do blend reagir; chegou *junto*. O gate só corta
exposição em momentos onde o blend, sozinho, já estava sendo
conservador. Resultado: a sobreposição só duplica o corte que o blend
já aplicou, sem adicionar informação.

A razão estrutural: a EMA de 21 dias que eu pré-comprometi (para
emular a frequência mensal do paper original do Estrella-Mishkin)
**apagou a propriedade-chave do sinal**. T10Y3M vale como preditor
porque antecipa recessões por 6-18 meses; a suavização de 21 dias
empurrou a inversão efetiva para perto do momento em que a volatilidade
realizada sobe. A mesma ação que tornou o dado "teoricamente limpo"
destruiu o que fazia o sinal ser interessante em primeiro lugar.

Lição geral: **sinais macro de lead-time longo precisam ser preservados
no estado cru (ou com smoothing ≤ 5 dias) para serem ortogonais a um
blend vol-managed.** Qualquer smoothing mensal joga o sinal no mesmo
espaço informacional que variance-scaling já cobre.

---

## Onde isso deixa o loop

Dois overlay-attempts falharam agora:
- iter 007: **momentum time-series** (sinal de preço correlacionado) —
  redundante com variance-scaling.
- iter 009: **term-spread suavizado 21d** (sinal macro "ortogonal"
  mas smoothed) — também redundante, por razão diferente.

O padrão: **qualquer overlay que colapsa para concorrente em timing
com o variance-scaling é redundante.** Lead-time é o eixo que
diferencia.

Iter 010 vai abandonar o caminho de overlay e tentar **extensão
estrutural**: 3-asset blend SPY+TLT+GLD. Gold adiciona fator real-asset
/ inflação com correlação ~zero com equity e bonds. Muda o eixo de
diversificação em vez de adicionar sinal. Provável que seja mais
produtivo do que um terceiro overlay.

Secundário: **asymmetric T10Y3M overlay** (haircut só na perna de
equity, bond mantém 100% — respeita flight-to-quality) com smoothing ≤ 5d
ou cru. Preserva o lead-time. Teoricamente pode funcionar; ficou como
candidato #2 no backlog.

---

## Material técnico

- Iteração: `studies/strategy_hunt_loop/iterations/009-2026-04-24-1447-term-spread-overlay-blend/`
- Score: **64/100 PROMISING** (winner_conditions_met=False, 3/5)
- Kill criteria pré-comprometidos: #1/#2/#4 não dispararam; **#3 (score < 65)
  disparou com score = 64 — 1 ponto abaixo do threshold**.
- Top-K atual (ranking estável pós iter 009):
  1. **iter 008 74/100 PROMISING** — vol-managed SPY+TLT single cfg
     ex-ante. Hunt-loop high.
  2. iter 006 67/100 PROMISING
  3. **iter 009 64/100 PROMISING** — term-spread overlay (este)
  4. iter 005 59/100 MARGINAL
  5. iter 004 51/100 MARGINAL
- Pytest baseline: 729 passed + 5 skipped (inalterado pelo iter 009).
- Mandate §1: continua 100% Plano C. **Iter 009 não produz recomendação
  de allocation.**
