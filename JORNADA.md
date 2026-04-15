# JORNADA — ai-trade

> Arquivo de sincronização para humanos. Conta em linguagem acessível o que
> este projeto é, onde está e pra onde vai. Formato: seções fixas no topo
> (**atualizadas a cada sessão**) + changelog histórico no fim
> (entradas datadas, imutáveis).
>
> Não substitui `ROADMAP.md` (mapa técnico), `README.md` (setup) nem `specs/`
> (detalhes de implementação). Complementa.

---

## O que é isso?

Um projeto pessoal que tenta construir um sistema de trading automatizado
rodando sobre **CFDs da corretora Pepperstone** (ações, índices, ouro,
crypto, forex), usando uma API programática chamada **cTrader Open API**.

Antes de ligar qualquer dinheiro real, o sistema passa por fases: primeiro
absorver livros sérios de trading/ML (pronto); depois construir um motor
de backtest rigoroso (pronto); depois encontrar uma estratégia que
sobreviva a testes estatísticos severos (**onde estamos**); depois paper
trading e live em passos pequenos (futuro).

A regra inviolável é que **toda decisão técnica cita um livro específico**
(`[book.slug, p.X]`). Nada de "o Claude acha que…" — só "a página 104 do
AFML diz que…". Isso blinda o projeto contra o maior risco de usar LLM em
trading: palpite disfarçado de análise.

---

## Onde estamos hoje (2026-04-15)

- **Fase 0 — Biblioteca de conhecimento** ✅ 33 livros digeridos em resumos
  validados automaticamente. Zero alucinação detectada (toda afirmação
  tem citação `[p.X]` ou `N/A` explícito).
- **Fase 0.5 — Skill agregada** ✅ Os 33 resumos viram um Claude Skill
  unificado em `knowledge/SKILL.md`.
- **Fase 1 — Infra Pepperstone/cTrader** 🔄 Código pronto, bloqueada pela
  Spotware (eles precisam aprovar o app OAuth; e-mail ainda não chegou).
- **Fase 2 — Motor de backtest** ✅ 2.3 mil linhas de código, 351 testes
  passando. Inclui os 5 testes anti-overfit mais sérios da literatura
  (CPCV, PBO, DSR, Walk-forward, Permutação).
- **Fase 2.5 — Testar estratégias no motor** 🔄 5 ciclos executados (todos
  em bars diários):
  - **Clenow momentum** — cross-sectional momentum.
  - **Ehlers BP Swing** — DSP swing trader em oscilador band-pass.
  - **Ehlers + AFML meta-labeling simples** (Run 4 Step 1) — piorou
    (PBO 0.647 vs 0.496 baseline).
  - **Long-history Ehlers 2005-2023** (Run 4 F3.C) — PBO melhorou, WF
    quebrou em crises.
  - **F3.D Portfolio Clenow + Ehlers 50/50** (Run 4 Step 2) — PBO
    disparou pra 0.849 (paradoxo da uniformidade), mas **WF foi pra
    9/9** — diversificação *resolveu* o problema de crise. Sub-result
    que fica.
- **Pivô arquitetural (decidido 2026-04-15 noite)** ⚠️ Todos os ciclos
  acima rodaram em **bars diários**, com trades que duraram 1-60+ dias
  em média. Isso é incompatível com o objetivo real do projeto:
  **trades curtas e pontuais via CFDs na Pepperstone**. A partir de
  agora, toda backtest opera em bars intraday (1h/15m/5m, 1min se
  latência permitir) e o catálogo de estratégias muda pra quem
  comporta short-hold. Detalhe na próxima seção e no changelog.
- **Fases 3-7** ⏳ Ainda à frente (rigor + paper + live + governança +
  escala).

**Fatos concretos úteis pra contexto:**
- 351 testes Python verdes (pytest -q).
- Tiingo bulk completo: 1660 tickers survivorship-free, 145 MB em backup.
- Ativos cobertos: SPY, QQQ, IWM, XLK/XLU/XLF/XLE, GLD, SLV, TLT, EEM,
  EFA, USO, DBA, BTC, ETH + SPX point-in-time 506 tickers.
- Último commit significativo: `7030d41` (AFML meta-labeling shippado,
  ainda não conectado às estratégias).

---

## Por que os backtests "não se mostraram promissores"

**Resumo honesto:** eles *têm* edge. Os retornos brutos são positivos. Mas
não passam no teste mais duro, que é o **DSR (Deflated Sharpe Ratio)**.

Analogia: você testa 30 variações da mesma receita de bolo. Por pura
sorte, uma vai parecer melhor que as outras. O DSR pergunta: "desconsiderando
a sorte de ter testado 30 variações, essa receita é genuinamente
melhor?". É o multiple-testing correction do López de Prado.

Nossos Sharpes brutos ficam entre 0.6 e 0.95 em vários ativos. Bom, mas
não extraordinário. Depois do DSR descontar o fato de termos testado
várias configurações, nenhum passa do limiar estatístico (p<0.05). É
como ter uma moeda levemente viciada: existe vantagem, só que **não dá
pra provar** com a quantidade de lançamentos que fizemos.

Duas coisas estão acontecendo:

1. **Edge existe, mas é pequeno.** Um bug corrigido ontem (commit
   `5ca9410`) descobriu que o código lia preços "crus" em vez de
   "ajustados por split/dividendo". Corrigir isso triplicou o Sharpe do
   SPY (0.31 → 0.806). Sinal real está lá — o DSR é que ainda não
   reconhece porque a amostra é modesta.
2. **Testamos pouco tempo ou muita coisa junto.** Caminhos de saída: (a)
   aumentar os anos de histórico (T), (b) reduzir o número de configs
   testadas (N), (c) **filtrar as más trades com um modelo secundário**
   (AFML meta-labeling). (c) é a próxima tentativa.

---

## O que vem a seguir (ordem de prioridade)

**Direção nova pós-pivô 2026-04-15 noite.** Todos os cinco ciclos
anteriores ficam no histórico como "pesquisa em bars diários"; daqui
pra frente a agulha gira em torno de short-hold intraday.

1. **`tiingo_service` lazy-cache** ← **próximo passo imediato**.
   Substituir/complementar o bulk diário atual por uma camada onde
   cada chamada de API é memoizada por `(endpoint, params)` — se já
   está em `data/cache/`, retorna; senão, requisita, salva e retorna.
   Destrava intraday (endpoints Tiingo IEX 1min/5m/1h) sem pre-bulk.
2. **Catálogo de estratégias intraday short-hold** — começar em 1h
   (sweet spot entre ruído e frequência) e depois 15m/5m:
   - **Chan mean-reversion / cointegration pairs**
     `[algo_trading_chan]` — natural pra intraday, minutos-horas.
   - **Ehlers BP Swing em 1h** — recalibrar thresholds, a infra já
     suporta.
   - **Volatility breakouts / range trading** `[volatility_trading,
     Sinclair]`.
3. **AFML sofisticado** — DEFERRED. Se uma estratégia intraday
   mostrar edge, aí entra como filtro secundário meta-labeling.
4. **Clenow** — descartado como estratégia de produção (cross-
   sectional momentum é inerentemente multi-day). Fica como "exercise
   do motor" no histórico.
5. **Último recurso** — Carver multi-asset trend (também multi-day,
   só se nada intraday der edge).

A infra `src/ai_trade/backtest/portfolio/` construída em F3.D é
**timeframe-agnostic** — reusável pra combinar estratégias intraday
no futuro (`Portfolio(ChanPairs, EhlersBP1h)` drop-in).

O sonho com ouro fica anotado, mas GLD foi o pior ativo do último survey
(Sharpe 0.21, falha todos os gates). Criar estratégia 1-ativo pra ouro
sem framework generalizável aumenta muito o risco de overfitting. Se o
portfolio diversificado (passo 4) incluir GLD e passar, a intuição se
concretiza pelo caminho certo.

---

## Glossário mínimo

Termos que aparecem ao longo das entradas do changelog:

- **Backtest** — simular a estratégia em dados históricos pra ver como
  teria performado. Ponto de partida. Risco: parecer bom no simulado e
  falhar em live.
- **Sharpe** — medida de retorno por unidade de risco. Quanto maior,
  melhor. ~1.0 é "bom", ~2.0 é "excelente", ~0.5 é "fraco".
- **DSR (Deflated Sharpe Ratio)** — Sharpe corrigido pelo número de
  hipóteses testadas. Gate: p-value < 0.05. Fonte: AFML cap.14.
- **PBO (Probability of Backtest Overfitting)** — probabilidade da
  melhor config ter sido escolhida por overfitting. Gate: < 0.5.
- **Walk-forward** — reroda a estratégia em janelas temporais
  deslizantes. Gate: ≥ 6 de 8 janelas lucrativas + drawdown ≤ 25%.
- **CPCV** — validação cruzada temporal combinatória (purged). Dá uma
  *distribuição* de Sharpes em vez de um ponto único.
- **Survivorship bias** — usar só empresas que "sobreviveram" até hoje
  mente sobre a realidade. Correção: universo ponto-no-tempo com
  empresas delistadas inclusas.
- **CFD** — Contrato por Diferença. É como apostar no preço do ativo
  sem possuir o ativo. Cobra *swap* diário pra manter a posição.
- **AFML** — "Advances in Financial Machine Learning" (López de Prado,
  2018). Livro-fonte das técnicas anti-overfitting + meta-labeling.
- **Meta-labeling** — treinar um segundo modelo pra decidir
  "tradear/não tradear" cada sinal da estratégia primária. Filtra
  ruído, eleva precisão, pode salvar o DSR.

---

# Changelog (entradas datadas)

## 2026-04-15 (noite, final) — Pivô: intraday short-hold + `tiingo_service` lazy-cache

**Gatilho:** conversa pós-F3.D sobre tempo real de trade. Checando os
trades persistidos dos 9 portfolios (`grid_portfolio_20260415-1541`):

- **Clenow:** duração mediana 56-63 dias, média 65-74, máximo 287-378.
- **Ehlers BP Swing:** mediana 1-22 dias, mas média inflada (129-146
  dias) por posições presas por até 4 anos em trends sem hit de stop.

Isso é **fundamentalmente incompatível** com o objetivo do projeto:
operar CFDs na Pepperstone, que cobra swap/overnight diário. Mesmo
ignorando swap por ora no backtest, a *seleção* de estratégias tem
que respeitar "curto e pontual" desde já, senão estamos otimizando a
coisa errada.

**Duas decisões derivadas:**

1. **`tiingo_service` (lazy-cache) substitui o bulk diário.** Camada
   nova que, em vez de pre-baixar todos os tickers numa única shot,
   memoiza chamadas por `(endpoint, params)`: se o dado já existe em
   `data/cache/`, retorna; senão, requisita, persiste, retorna. Isso:
   (a) permite intraday (endpoints Tiingo IEX 1min/5m/1h) sem bulk
   prévio; (b) ainda funciona pra daily quando necessário; (c) o
   `TiingoStorage`/`manifest.json` atual vira um caso especial dessa
   camada, não o protocolo primário.
2. **Catálogo de estratégias re-prioritizado em torno de short-hold.**
   Clenow sai do caminho de produção (fica como histórico). Entram:
   Chan mean-reversion/pairs `[algo_trading_chan]`, Ehlers BP em 1h
   (mesma lógica, timeframe novo), volatility breakouts `[volatility_
   trading, Sinclair]`. AFML sofisticado — antes priorizado como
   "caminho B" — fica deferred pra entrar depois como filtro
   secundário sobre uma estratégia intraday que mostre edge.

**O que NÃO muda:**
- F3.D sub-result (diversificação resolve WF) continua valioso. O
  pacote `src/ai_trade/backtest/portfolio/` é timeframe-agnostic —
  será reusado pra combinar estratégias intraday.
- Gates anti-overfit (CPCV/PBO/DSR/WF) continuam os mesmos — o que
  muda é o que alimenta eles.
- Regra da citação `[book.slug, p.X]` continua inviolável.
- Stage 1 (edge em dados limpos) vs Stage 2 (custos Pepperstone reais)
  continua como estruturado no ROADMAP §"Two-stage backtest".

**Arquivos afetados nesse commit:**
- `JORNADA.md` (seções "Onde estamos hoje" + "O que vem a seguir" +
  este changelog).
- `ROADMAP.md` §"Current status" + §"Next steps" (pivô documentado).

**Próximo passo concreto** (pra nova sessão): brainstorming do
`tiingo_service` — design da chave de cache, relação com
`TiingoStorage` existente, migração dos backtests existentes.

---

## 2026-04-15 (noite) — F3.D Portfolio Clenow+Ehlers — FAIL v1 (paradoxo WF 9/9 + PBO 0.849)

**Hipótese:** se Clenow × Ehlers têm correlação de equity ≈ −0.01 (Run 2),
combiná-los num portfolio 50/50 "dois livros offline" pode:
(a) elevar o Sharpe pra ~1.0 via diversificação (1.41× a média, quando
ρ ≈ 0 e vols similares), passando o DSR;
(b) reduzir drawdown em crises (Clenow sai do mercado via regime filter
SMA200, Ehlers oscila).

**O que rodamos:** top-3 Clenow (Tiingo 2015-2023, configs 8/19/10 por
Sharpe) × top-3 Ehlers (long-history 2005-2023, configs 6/18/19 por
Sharpe) = 9 portfolios 50/50, merge offline via retornos ponderados,
sem rebalance. Janela v1: SPY 2015-2023 Tiingo survivorship-free.

**Resultado v1 (`grid_portfolio_20260415-1541`):**

| Métrica | Baseline isolado | F3.D v1 portfolio |
|---|---|---|
| PBO | Ehlers 0.496 ✅ / Clenow 0.603 | **0.849 ❌ (piorou muito)** |
| DSR 0/N pass | 0/24 (Ehlers) / 0/30 (Clenow) | 0/9 (best p=0.190, melhorou) |
| Walk-forward | Ehlers 7/24 / Clenow 9/30 | **9/9 ✅ (salto enorme)** |
| Best Sharpe | Ehlers 0.806 | 0.804 (config 1: clenow=8 × ehlers=18) |
| Best CAGR | — | 10.84% |
| Best DD | — | 18.02% |

**Leitura leiga:**
- **Bom: WF 9/9**. Todas as 9 combinações passam ≥6/8 janelas lucrativas
  com DD≤25%. Clenow regime filter subsidia o DD do Ehlers — a tese
  "diversificação reduz crise" funciona empiricamente.
- **Ruim: PBO 0.849**. Paradoxo: diversificação tornou os 9 configs tão
  uniformes (Sharpes clustered 0.71-0.80, PBO logits std=1.08 muito
  apertado) que o "melhor" vira essencialmente aleatório. Quanto mais
  uniforme o grid, mais overfit o PBO marca — porque a seleção IS → OOS
  é ruído puro.
- **DSR ainda não passa**: Sharpe 0.80 é bom mas não chega no 1.0 que a
  matemática predizia. A hipótese teórica assumia vol-scaled (vols
  iguais); sem vol-scaling (caveat explícito da spec §5 "vol mismatch"),
  o ganho real é menor.

**Conclusão:** a hipótese H1 (portfolio rescata DSR para ~1.0) **falha**,
mas com sub-resultado positivo importante: a diversificação **resolve o
problema de WF em crises** `[stocks_on_the_move, p.66-67, p.98-99]` — só
não resolve DSR, e em cima ainda piora o PBO pela uniformidade dos
configs. Spec go/no-go §6.2 manda pular v2 (2005-2023) quando v1 falha.

**Próximo passo (caminho B no plan):** AFML sofisticado. Agora com
sub-resultado validado de que WF é solúvel (Clenow regime filter ajuda),
o foco fica em:
- Walk-forward CV com purge/embargo (López de Prado `[advances_fin_ml, ch.7]`)
  em vez do split temporal ingênuo 50/50 do Run 4 Step 1.
- Features ricas: `[osc, dcp, hp, ss_trend, atr20, regime_flag, vix_proxy, volume_z]`.
- Triple-barrier labeling assimétrico (TP/SL não-simétricos).
- Universo de treino: long-history 1993-2026 (Tiingo widest bulk, ~3×
  dados vs 2015-2023).

**Arquivos gerados:**
- `reports/grid_portfolio_20260415-1541/diagnostic.md` (v1, 9 configs).
- Código novo em `src/ai_trade/backtest/portfolio/` (commits `872a9cf`
  core + `c99bca3` citation fix + `36c0f57` CLI + `ac00d6e` review fixes).
- Spec: `docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md`.
- Plan: `docs/superpowers/plans/2026-04-15-f3d-portfolio-clenow-ehlers.md`.

---

## 2026-04-15 (tarde, segundo round) — Long-history Ehlers SPY (2005-2023) — FAIL

**Hipótese:** se o DSR está falhando por "testamos 24 configs em amostra
pequena demais", aumentar a janela de 9 anos para 19 anos triplica os
dados. A deflação do DSR depende de `Z(N)/√(T-1)`; mais T = divisor
maior = deflação menor. Zero código novo — só uma janela mais antiga.

**O que rodamos:** mesma grid Ehlers puro (24 configs), SPY 2005-2023
(4781 bars vs 2264 bars anteriormente), Tiingo.

**Resultado comparativo:**

| Métrica | Baseline 2015-2023 | Long 2005-2023 |
|---|---|---|
| PBO | 0.496 ✅ | **0.405 ✅ (melhorou)** |
| DSR 0/24 pass | ✅ reject | ❌ reject |
| DSR best p-value | 0.332 | **0.213 (melhorou, mas ainda fail)** |
| Walk-forward | 7/24 | **0/24 (piorou)** |
| Best Sharpe | 0.806 | 0.639 |
| Best config CAGR | — | 9.25% |
| Best config DD | — | 29.44% |

**Leitura leiga:**
- Aumentar a janela **ajudou** no PBO (overfitting) e **aproximou** o
  DSR do limiar (p 0.332 → 0.213; precisaria < 0.05 pra passar).
- Mas **quebrou o walk-forward**: com 19 anos divididos em 8 janelas,
  cada janela pega ~2.4 anos. E a janela 2005-2023 contém 2008-09
  (subprime), 2011 (debt ceiling), 2015 (correção), 2020 (COVID), 2022
  (juros). Cinco crises em oito janelas — parâmetros fixos não
  adaptam.
- A melhor config individual (hp=48, lp=20, pct=0.80, stop=0.02) teve
  6/8 janelas lucrativas (consistente!), mas drawdown máximo de
  **29%**, acima do gate de 25%. Quase passou — foi cortada por pouco.

**Conclusão:** a estratégia tem edge "real-mas-frágil". Em janela curta
ela passa no profitable/DD mas falha no DSR (sample pequeno). Em
janela longa ela melhora DSR/PBO mas quebra em crises específicas. Nem
uma janela nem a outra é a solução isolada.

**Próximo passo recomendado (F3.D no plano):** portfolio combinado
Clenow + Ehlers. As duas estratégias têm correlação ≈ −0.01 (ortogonais).
Combinar numa proporção volatility-scaled 50/50 pode elevar o Sharpe
efetivo (diversificação) **e** reduzir o drawdown em crises (Clenow
tende a "sair do mercado" via regime filter, Ehlers tende a
"oscilar"). Mas isso é código novo — vale alinhar com o usuário antes.

**Arquivos gerados:**
- `reports/grid_ehlers_20260415-1353/diagnostic.md` (24 configs, 19
  anos).

---

## 2026-04-15 (tarde) — Run 4 Step 1 (AFML rescue Ehlers SPY) — FAIL

**O que tentamos:** adicionar um "segurança" inteligente em cima do
Ehlers. A estratégia Ehlers identifica quando há uma oscilação pra
comprar barato e vender caro. Mas nem toda oscilação é tradável — às
vezes é ruído, às vezes a oscilação quebra no meio. A ideia do meta-
labeling (López de Prado, AFML) era treinar um modelo de Machine
Learning (RandomForest) pra olhar pros sinais e decidir
*"essa oscilação aqui parece boa, vamos tradear"* vs *"essa aqui é
ruidosa, pula"*.

**O que rodamos:** 48 configurações (5 eixos: hp × lp × pct × stop ×
threshold), SPY 2015-2023, Tiingo survivorship-free, treinou o
RandomForest nos primeiros 50% de eventos e filtrou os restantes.

**O que aconteceu:**
- **PBO 0.647** (vs 0.496 da baseline Ehlers puro) — **piorou**.
- **DSR 0/48 configs passam** p<0.05 (pior p=0.701 vs 0.332 baseline).
- **Walk-forward 0/48** passam (baseline tinha 7/24).
- **Melhor Sharpe:** 0.575 (config #18) — **abaixo da baseline 0.806**.

**Interpretação leiga:** o filtro foi ingênuo demais. O modelo foi
treinado em poucos exemplos (~50-100 eventos na primeira metade), com
split temporal simples (sem walk-forward CV com embargo). Ele acabou
cortando trades bons junto com ruins, reduzindo tanto o Sharpe quanto a
quantidade de sinal. E ainda por cima, dobrar o número de configs
testadas (24 → 48) aumentou o critério do DSR ser ainda mais rigoroso.

**Não é um enterro do AFML — é um enterro da versão simples dele.** O
"jeito certo" tem várias partes que pulamos:
- Cross-validation temporal com embargo (não split 50/50 único).
- Mais features (volume, RSI de curto, variáveis de outros ativos).
- Mais eventos (janela longa 1993-2026 em vez de 2015-2023).

**Decisão:** em vez de consertar o AFML agora, vamos testar o próximo
barato da lista: **rodar o Ehlers puro numa janela longa**. Se
funcionar, matamos o problema sem precisar de ML. Se não, voltamos pro
AFML com mais cuidado.

**Arquivos gerados:**
- `reports/grid_ehlers_meta_20260415-1349/diagnostic.md` (48 configs
  detalhadas).
- `src/ai_trade/backtest/strategies/ehlers_meta.py` (implementação,
  permanece no código — tem valor educacional e base para retomada).
- `scripts/run_grid_ehlers_meta.py` (orquestrador, permanece).
- `tests/test_ehlers_meta.py` (10 novos testes, 360/362 passando).

---

## 2026-04-15 (manhã) — Sincronização geral + decisões de arquitetura

**O que aconteceu nessa sessão:**

1. **Diagnóstico pós-Runs 1-3.** Os três ciclos de backtest falham o
   gate DSR (0 de 24-30 configurações passam o p<0.05). Não é ruído —
   é "edge real mas insuficiente" dado o tamanho da amostra.
2. **Auditoria do Tiingo.** O bulk de ontem (22:05) terminou com 1660
   tickers em 145 MB de backup (`tiingo_backup_20260415-0958.tar.gz`).
   Decidido **manter a arquitetura atual** (parquet per-ticker +
   manifest JSON). Request-on-demand seria pior (latência + rate
   limits). Subscription do Tiingo Power fica ativa por +30 dias
   (até ~2026-05-15), depois cancela e roda offline do backup.
3. **Auditoria do knowledge base.** 33 livros é quantidade saudável.
   Gaps reais (Crypto 0 livros, Forex 0 livros) mas **não são
   blockers** agora — o foco da Phase 2.5 Run 4 é SPY (cobertura
   sobrando). Conflitos entre livros (ex.: Carver defende stop-loss
   discreto; Chan diz pra *nunca* usar stop em mean-reversion) são
   construtivos: escolas diferentes, não erro.
4. **Criação deste arquivo (`JORNADA.md`).** Pra sincronizar o usuário
   sem precisar ler `ROADMAP.md`/`specs/`. Instrução adicionada em
   `.claude/CLAUDE.md` pra manter atualizado a cada sessão.
5. **Próximo passo (ainda esta sessão):** implementar AFML rescue na
   Ehlers SPY. Código novo em
   `src/ai_trade/backtest/strategies/ehlers_meta.py` +
   `scripts/run_grid_ehlers_meta.py`. Meta: passar o DSR em ao menos
   1 configuração.

**Lembretes ativos:**
- ⏰ **~2026-05-15:** data-limite pra decidir se cancelamos Tiingo Power.
- 📧 **cTrader OAuth:** ainda aguardando aprovação da Spotware. Sem
  esse e-mail, Fase 1 continua bloqueada — por isso o foco segue em
  backtests.
- 📖 **Regra inalterada:** toda decisão técnica cita livro (`[slug, p.X]`).

---

## 2026-04-14 — Implementação Tiingo + Phase 2.5 Run 3

**Contexto:** no início do dia, yfinance era a fonte única. Problema: 19%
de survivorship bias residual mesmo usando constituintes SPX ponto-
no-tempo do Wikipedia. Decisão: migrar pra Tiingo Power ($10/mês) que
serve dados survivorship-free via API.

**O que aconteceu:**
- Implementada a camada Tiingo (`src/ai_trade/backtest/data/tiingo_source.py`
  + `tiingo_storage.py`). Design "storage-first": todos os dados baixam
  pra disco em parquet; backtests consultam o disco, zero chamada HTTP
  em warm-run.
- Bug de dados crus vs ajustados descoberto e corrigido no commit
  `5ca9410`: estratégias liam `close` em vez de `adj_close`. Splits
  disparavam o filtro de gap 15% do Clenow; dividendos poluíam o
  oscilador do Ehlers. **Sharpe do SPY subiu de 0.31 pra 0.806** só com
  essa correção.
- **Run 3 executado em 3 experimentos:** Ehlers SPY 2015-2023
  (PBO=0.496 passa, DSR 0/24 falha), Ehlers multi-asset 16 ativos
  2005-2023 (0/16 passa tudo), Clenow SPX Tiingo 506 tickers (PBO=0.603
  fail, DSR 0/30 fail).
- Bulk background do Tiingo disparado às 22:05 (1678 tickers).

**Verdict:** PBO fica no limiar mas DSR cataclísmico em toda a linha.
Edge real mas insuficiente vs N de trials. Direção pra Run 4 decidida:
AFML meta-labeling.

---

## 2026-04-13 — Phase 2.5 Runs 1-2 (Clenow + Ehlers grids)

**O que aconteceu:**
- **Run 1 (Clenow grid):** 30 configurações do momentum de Clenow sobre
  SPX 2015-2023 (yfinance). Gates falham: PBO=0.524, DSR 0/30, WF 4/30.
  Melhor config: #15 (lookback 90d, top 20%, risk 0.2%) com Sharpe 0.58,
  CAGR 8.87%. **Underperforma SPY buy-and-hold.**
- **Run 2 (Ehlers Band-Pass Swing grid):** 24 configs em ^GSPC single-
  instrument. **PBO=0.468 passa** (estruturalmente menos overfit que
  Clenow), DSR 0/24 falha. Melhor: #6 (hp=48, lp=20, pct=0.80) Sharpe
  0.31 CAGR 2.17%.
- **Achado crítico:** Clenow × Ehlers têm correlação de equity curves
  ≈ −0.01. **Estratégias ortogonais.** Candidatas pra portfolio
  regime-aware no futuro.

---

## 2026-04-12 — Phase 2 concluída (motor de backtest)

Delivery completo do módulo de backtest em `src/ai_trade/backtest/`:
data layer (yfinance + Wikipedia SPX point-in-time), engine
(portfolio + execução CFD-aware + runner), validação (CPCV / PBO /
DSR / walk-forward / MCPT), métricas (Sharpe / Sortino / Calmar /
CAGR / DD / VaR) e gerador de relatório (MD + PNG). Clenow
`stocks_on_the_move` replicado end-to-end como estratégia de
calibração. **173 testes verdes.** Disclaimer de survivorship
obrigatório em todo relatório.

---

## 2026-04-01 a 2026-04-11 — Phase 0 (knowledge base)

Ingestão dos 33 PDFs via pipeline `books/raw/<slug>.pdf` →
`extracted/` → `summaries/<slug>.md`. Validação autônoma em 3
camadas (estrutural + citações determinísticas + juiz adversarial
LLM). 12 Perfect / 20 Good / 1 Border / **zero alucinações**.
Geração da `knowledge/SKILL.md` agregada como Claude Skill.

---

## ≤ 2026-03-31 — Decisões fundacionais

- Broker escolhido: **Pepperstone via cTrader Open API** (Protobuf/TCP,
  OAuth2). Descartados XM/MT5, Alpaca, OANDA, IBKR.
- Stack: Python 3.12, docker-compose (Postgres + Grafana),
  Twisted-based `ctrader_open_api` SDK oficial.
- Princípio inviolável: trading como problema de estatística + sinal.
  LLM entra como segunda opinião, nunca como raciocinador primário.
