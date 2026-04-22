# Abrindo Strategy D — swing-trade BR com ranking mensal

**Data:** 2026-04-22 17:34
**Tipo:** Decisão estratégica (abertura de novo slot ativo)
**Status:** Proposta — aguarda assinatura do usuário no override do mandate

## Contexto humano

Depois de 29 validações honest no total — 6 leads V2 Plano A (Phase 3.5f), 10
famílias amplas (Phase 3.6), 8 hipóteses de literatura top-tier (Phase 3.7-3),
5 variants canonical Plano B (Phase 3.8-1) — **29/29 FAIL**. Nenhuma estratégia
sobreviveu aos gates hard-block (PBO, DSR, bootstrap 99.9% CI, WF, cross-lib).

Motor limpo, engine cross-lib a 1e-6 em 23 de 24 strategies testadas. Não é
bug de implementação. É que **o edge estatístico procurado nos dois slots
ativos (Strategy A CFD Pepperstone e Strategy B LETF rotation Inter) não
existe sob os gates honestos** — pelo menos dentro da vizinhança conceitual
que testamos.

Diante disso, o usuário decidiu "mudar de ferramenta": abrir um terceiro slot
ativo, **Strategy D**, com tese diferente das anteriores.

## O que é Strategy D

Uma estratégia de **swing-trade de ações brasileiras** baseada em **ranking**.
Cada mês:

1. Olha o universo IBrX-100 (~100 ações mais negociadas da B3).
2. Aplica uma métrica de scoring (momentum Clenow, valor Greenblatt,
   multi-fator, ou low-vol+momentum — vamos testar todas).
3. Compra as top N ações (cesta típica: 15-30).
4. Mantém ~21 dias úteis (1 mês calendário).
5. No 1º dia útil do mês seguinte, recalcula ranking, sai das que caíram
   do top, entra nas novas.

O apelo específico é tributário: **vendas até R$20k/mês de ações no mercado
à vista são isentas de imposto de renda** (art. 3º II Lei 11.033/2004), desde
que não seja day-trade. Com capital pequeno-médio e cesta de ~20 ações, o
ticket fica baixo o suficiente pra ficar dentro da isenção na maior parte dos
meses.

## Por que agora

Os slots A e B estão **esgotados** em termos de conceitos testáveis de forma
rápida (não em termos de conceitos possíveis — sempre há mais papers). O
custo de oportunidade de continuar "mais uma hipótese B" está ficando alto, e
o mercado BR tem duas vantagens estruturais que não temos em US:

1. **Isenção R$20k/mês** permite compound líquido que offshore não oferece.
2. **Ações BR são diretamente negociáveis de corretora doméstica** (XP,
   Clear, Rico, Inter DTVM, BTG Pactual, Nubank) — sem fricção FX / DARF
   15% year-end (modelo Inter rota US).

A desvantagem óbvia é concentração setorial (IBOV ~50% em bancos +
commodities; IBrX-100 suaviza pra ~35-40%) e liquidez menor fora do top 30.

## Mudança de mandate proposta

Abrir Strategy D requer **override do mandate §1**. O mandate atual fixa 3
compartimentos: Plano C passivo (60-80%), Strategy A (parte dos 20-40%
ativos), Strategy B (parte dos 20-40% ativos). Strategy D seria um **3º
slot ativo**, pegando pedaço da alocação que era A+B.

A proposta detalhada (a ser assinada) está em
`docs/mandate_overrides/2026-04-22-strategy-d-open.md`. O mandate em si
não foi editado — a proposta é **reversível** até o usuário aprovar.

## Próximos passos imediatos

1. Usuário revisa o override proposal (`docs/mandate_overrides/`).
2. Usuário revisa o spec executável (`specs/strategy_d_br_ranking.md`).
3. Se aprovado, incorporar override no `docs/investment-mandate.md` e
   `CLAUDE.md`, e começar Fase D-1 (data layer BR).
4. Se reprovado, arquivar proposta e decidir outro caminho (R1-R5 do
   Phase 3.8-1 closure).

## Escolhas-chave já fixadas (via `AskUserQuestion` 2026-04-22)

| Escolha | Resposta |
|---------|----------|
| Escopo no mandate | **Strategy D = 3º slot ativo** (não "Phase 3.6 lead" nem "substitui A/B") |
| Universo | **IBrX-100** (liquidez ≥ R$5M/dia, ~100 ações) |
| Cadência | **Mensal** (alinha com isenção R$20k) |
| Sinais | **Testar todos** — Clenow momentum, Magic Formula, Multi-fator V+M+Q, Low-vol+mom hybrid, + mesclagens |
| Tax model | **R$20k isenção condicional** — ≤R$20k vendas/mês isento, >R$20k → 15% DARF sobre lucro total do mês |
| Data source | **yfinance `.SA` (OHLCV) + Fundamentus scrape (fundamentals) + fallback Oceans14 via Playwright** |

Brapi.dev free descartado — limita a 4 tickers teste (PETR4/VALE3/MGLU3/ITUB4),
não serve IBrX-100 inteiro.

## Citações âncora da tese (CLAUDE.md Regra 2)

- **Clenow momentum Adjusted Slope** = annualized slope × R², SMA₁₀₀ filter,
  gap filter 15%, ATR sizing 10 bps/day, rebal weekly → adaptado mensal
  `[stocks_on_the_move, p.76-77, 81-82, 88, 99]`
- **Greenblatt Magic Formula** = rank(ROIC) + rank(EY) composite
  `[quant_trading_chan, ch.1, p.7]`
- **Equal-weighted ranks** superior a conviction weights (Kahneman 2011 via
  Chan) `[quant_trading_chan, ch.1, p.7]`
- **Cesta 20-30** + position inertia 10% `[stocks_on_the_move, p.153,
  p.229-230]`, `[systematic_trading, p.174]`
- **PBO < 0.5 + DSR p < 0.05** mandatórios, DSR deflator ajustado pelo
  N_trials do grid (~64 configs) `[advances_fin_ml, p.208-211, p.275]`

## Riscos honestos

1. **Mandate override ainda não assinado.** Todo código ficará em branch
   separada até assinatura formal.
2. **Scraping frágil.** Fundamentus/Oceans14 podem bloquear. Fallback de
   snapshot congelado 2026-04-22 + backtest com fundamentals approximated.
3. **Survivorship bias yfinance.** Ações delistadas pré-2026-04 não aparecem.
   Disclaimer obrigatório em todo report (regra CLAUDE.md já existente).
4. **Isenção R$20k some com capital grande.** Sensitivity em R$50k/100k/500k
   obrigatória — se winner só passa com R$50k, o benefício é limitante.
5. **Multiple testing.** ~64 configs planejadas → DSR deflator com N_trials
   correto, senão PBO vai sobrestimar edge.
6. **Broker BR não aberto.** Paper-trade (Phase D-promotion) depende de
   abrir conta. Pré-requisito não-técnico.

## Registro histórico

Esta é a primeira abertura de slot ativo do projeto desde a fixação do
mandate (Plano C passivo + A CFD + B swing). Se Strategy D falhar como A e
B falharam, a decisão natural será consolidar em Plano C passivo e
documentar o projeto como "hunt completo, sem winner ativo". Este entry
serve como marco: **29/29 no momento da abertura; esperamos que esta seja
a 30ª que muda o placar**.
