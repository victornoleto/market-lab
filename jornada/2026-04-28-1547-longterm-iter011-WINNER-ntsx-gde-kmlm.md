# Long-term portfolio iter 011: NTSX + GDE + KMLM — 🏆 WINNER 91/100

Depois de **10 iterações sem winner**, a estratégia mais simples possível —
um stack estático de 3 ETFs capital-eficientes — finalmente passou todas as
5 condições estritas da missão "bater a média de SPY+VT (Sharpe gross) por
≥0.10 em ≥2 de 3 datasets".

A configuração testada foi a **preferência arquitetural literal do usuário**
(NTSX+GDE+KMLM em variantes 40/30/30, 33/33/33, 50/25/25, 35/25/40), explicitamente
listada como "skipped across 10 iters" na memória do projeto. O codex nunca
tinha rodado essa hipótese diretamente porque o log de dead-ends DE-005 fechou
"static stacks" sob a missão antiga (bater HAA+Gold Sharpe 1.12). Sob a
missão redefinida (bater avg(SPY,VT) Sharpe ~0.67-0.92 conforme dataset), a
mesma família é vencedora.

## Resultado

Configuração selecionada: **`mf_tilted_352540`** (35% NTSX + 25% GDE + 40% KMLM).

| dataset | gross Sharpe | edge vs avg(SPY,VT) | CAGR | MDD | gates |
|---|---:|---:|---:|---:|---:|
| educational (31y) | 1.021 | **+0.350** | 11.58% | 26.04% | 7/7 |
| vt_real (17y) | 0.960 | **+0.253** | 10.95% | 21.22% | 6/7 |
| ndx_real (16y) | 1.104 | **+0.180** | 11.64% | 14.12% | 6/7 |

Score breakdown: Sharpe edge 25/25, gates 21/25, DSR 15/15 (worst p=1.36e-3),
CAGR floor 10/15 (ndx só perde por 0.46pp), MDD ceiling 15/15, robustness 5/5
(100% Sharpe positivo em 27 janelas rolantes de 5 anos). **Total 91/100,
todas as 5 condições estritas cumpridas → 🏆 WINNER**.

**Família-level robusto**: as 4 variantes testadas (40/30/30, 33/33/33,
50/25/25, 35/25/40) batem avg(SPY,VT) em 3/3 datasets. A preferência literal
do usuário (40/30/30) também passa: edu Sharpe 0.976 (+0.305), vt 0.944
(+0.237), ndx 1.107 (+0.184). A escolha entre as variantes é ruído estatístico
(G1 PBO falha em vt e ndx exatamente por isso — Sharpes estão dentro de 0.025
em ndx, o test não consegue resolver o ranking).

## Por que isso funciona

Três fontes estruturalmente independentes de prêmio de risco em um wrapper
sem custo de margem nem decay diário:

1. **NTSX** = 0.9 SPY + 0.6 IEF − 0.5 cash → US equity + Treasury duration
   embutidos via futuros (1.5× nocional sem alavancagem retail).
2. **GDE** = 0.9 SPY + 0.9 GLD − 0.8 cash → SPY + ouro empilhados (1.8×
   nocional via overlay de futuros).
3. **KMLM** = managed futures trend-following → "crisis alpha" descorrelacionado
   de equity drawdowns (1973-74, 2000-02, 2008, 2022).

`[risk_parity, ch.5, p.10]` chama isso de "return stacking" — atingir a
alocação de risco-alvo com menos capital, empilhando prêmios de risco
descorrelacionados em uma só ETF. `[stocks_on_the_move, p.21-30]` documenta
o premium momentum de futuros como diversificador de cauda.

## Tax-perfect sob Lei 14.754/2023

Net Sharpe = Gross Sharpe **a 9 casas decimais**. Razão estrutural: um buy-hold
estático via PF direta (Banco Inter Internacional) **não realiza ganho durante
o ano** — sold_fraction = 0 a cada dia. O `AnnualDarfEngine` só dispara DARF
na liquidação final, que não afeta a série de retornos diários.

Implicação prática: para um mandato de aposentadoria de longo prazo, este é o
arranjo mais tax-eficiente possível antes de planejamento sucessório. Toda a
"complicação" das estratégias HAA-style (canary VWOSIM, rotação mensal,
defensive switching) custa CAGR via DARF anual sobre realizações; um stack
estático escapa disso.

## Caveats honestos

- **G1 PBO falha em vt_real (0.758) e ndx_real (0.964)** — *não* é overfit
  da família, é seleção dentro da família ao nível do ruído. As 4 variantes
  estão todas dentro de 0.07 Sharpe; PBO vê o ranking embaralhar e classifica
  como overfit. O sinal robusto é "qualquer variante NTSX+GDE+KMLM passa", não
  "os 35/25/40 específicos passam". Para deploy: testar 2 variantes em paper
  trading antes de fixar pesos.
- **KMLMSIM é synth do testfolio até 2020-12** — KFA Mount Lucas live ETF só
  existe desde dez/2020. Pré-2020 é uma reconstrução do índice; live tracking
  é bom mas o período synth é teórico.
- **vt_real usa proxy VTSIM** — VT real ainda não foi puxado do Tiingo.
- **40% KMLM é alto** — variante selecionada tem 40% em managed futures, vs
  30% que o usuário tinha como preferência. Os 40/30/30 do usuário também
  ganham; usar a do usuário em deploy é mais conservador.

## Mandate context

Iter 011 vira candidato para **mandate §7 override** (Plano C). Não é
auto-deploy: precisa override assinado pelo usuário antes de qualquer alocação
real, conforme `docs/investment-mandate.md` §1 (mandate em MAINTENANCE para
estratégias short-hold; long-term portfolio é workstream LIVE mas qualquer
winner ainda passa pelo §7).

## Lição estrutural (vale para o próximo loop)

A missão importa mais que a engenharia. Sob a missão antiga (bater iter 009
HAA+Gold Sharpe 1.12), DE-005 fechou stacks estáticos como subordinados ao
canary HAA. Sob a missão correta (bater avg(SPY,VT) Sharpe ~0.7), a mesma
família é vencedora. Não foi a engenharia que mudou — foi o alvo.

Outra lição: **simplicidade é virtude, não defeito**. Um stack de 3 ETFs com
rebalance anual (ou nenhum) dominou 10 iterações de variantes
canary/tilt/throttle no objetivo redefinido. A complexidade não pagou.

## Próximos passos (não são uma nova iteração; o loop parou)

1. Puxar VT e KMLM live do Tiingo, re-rodar gates apenas no período live
   (KMLM live since 2020-12) para confirmar que o edge não vem só do synth.
2. Sensibilidade: trocar KMLM por DBMF ou RSST para ver se o efeito do sleeve
   MF generaliza ou é artefato KMLM.
3. Rascunhar request de mandate §7 override com a evidência iter 011.

Arquivos: `studies/long_term_portfolio/iterations/011-2026-04-28-1537-ntsx-gde-kmlm-static/`
(hypothesis.md, backtest.py, verdict.json, results.json, final_report.md, plots).
