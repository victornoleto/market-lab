# JORNADA — ai-trade

> Diretório de sincronização para humanos. Conta em linguagem acessível o que
> este projeto é, onde está e pra onde vai. Formato: seções fixas abaixo
> (**atualizadas a cada sessão**) + entradas datadas em arquivos individuais
> (imutáveis).
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

## Onde estamos hoje (2026-04-16)

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
- **Pivô arquitetural + `tiingo_service` entregue (2026-04-15 noite)** ✅
  Os 5 ciclos diários eram incompatíveis com CFDs Pepperstone (swap
  overnight). A partir de agora, toda backtest opera em bars intraday
  (1h primeiro). `tiingo_service` lazy-cache refatorou
  `TiingoSource`/`TiingoStorage` para o eixo `frequency`, migrou os 1675
  tickers daily para `data/tiingo/daily/`, destravou IEX 1h + crypto 1h
  + forex 1h, e aplica split/dividend adjust em intraday via daily cache
  (evita re-introduzir bug do commit `5ca9410`). Smoke #1 retention PASS,
  Smoke #2 e2e PASS. **405 testes verdes.**
- **Primeira estratégia intraday do catálogo: Chan pairs GLD-SLV 1h**
  ❌ FAIL pelo gate de cointegração — o spread `log(GLD) − β·log(SLV)`
  tem half-life razoável (55 bars ≈ 8.5 dias) mas força de mean-reversion
  insuficiente (t_stat_OU=−2.956, threshold −3.4). Os 4 configs do grid
  abortam na construção da estratégia, antes do backtest. Confirma o
  warning de Chan `[algo_trading_chan, p.88-89, ch.4]` aplicado a ETFs
  intraday.
- **Segunda estratégia intraday: Vol-Expansion Breakout SPY+GLD+TLT 1h**
  ❌ FAIL em todos os gates — PBO=0.687 (>0.5), DSR 0/12, WF 0/12. A
  tese (Donchian channel breakout `[trading_systems_methods, p.353]`
  filtrado por Yang-Zhang vol cone `[volatility_trading, p.22-23, p.58-60]`,
  sized por Carver vol-targeting `[systematic_trading, p.144, p.159]`) não
  produz edge em ETFs 1h (2022-2026). Melhor config: Sharpe=0.19,
  CAGR=0.4% — compatível com ruído. Spec §7 hooks: Ehlers BP Swing 1h é
  o próximo do catálogo.
  Nota: Bundle original (SPY+XAU/USD+EUR/USD) abortado na pre-flight —
  Tiingo FX 1h tem gap de dados de 3.5 anos (2021-06→2025-01). Pivotamos
  pra Bundle γ ETF-only (SPY+GLD+TLT).
- **Fases 3-7** ⏳ Ainda à frente (rigor + paper + live + governança +
  escala).

**Fatos concretos úteis pra contexto:**
- **520 testes Python verdes** (pytest -q).
- **Winners Phase A COMPLETA → Phase B ativa (cost ablation concluído iter 22)**:
  - ✅ Winner 1: Bollinger MR (20,2) + GARCH SPY 1h [SHORT-HOLD CFD]. IS Sharpe 0.982, OOS 0.552, Stress +2.784. **CUSTO-ROBUSTO** (Pepperstone Razor: DSR p=0.0431, WF 6/8 com custos).
  - ✅ Winner 2: ETF Rotation top-1 diário [SWING BROKER]. IS Sharpe 0.708, OOS 1.477, Stress Q1 +8.34% net. **CUSTO-ROBUSTO** (15% IR + 0,10% comm: DSR p=0.0041, WF 7/8 com custos).
  - ⚠️ Winner 3: ETF Rotation top-2 diário [SWING BROKER]. **COSTS-SENSITIVE**: WF 5/8 (abaixo do mínimo 6/8) após aplicar custos reais. OOS positivo mas IS degradado.
- Tiingo bulk completo: 1660 tickers survivorship-free, 145 MB em backup.
- Cache intraday limpo (2026-04-16): 4296 bars placeholder removidos.
- Ativos cobertos intraday: SPY, QQQ, IWM, XLK/XLE/XLF, GLD, SLV, TLT, EEM, EFA, DIA (1h).
- **Phase B**: custo-ablação ✅, próximo: MC bootstrap CI + cross-asset transport + correlação entre strategies.

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

**Phase B ativa (2026-04-16).** Phase A completa com 3 winners: BollingerMR-GARCH SPY 1h + ETF Rotation top-1 e top-2. Fase B = validar, stress-testar e preparar os winners para produção.

1. ✅ **`tiingo_service` lazy-cache — ENTREGUE** (2026-04-15 noite).
   Refactor in-place de `TiingoSource`/`TiingoStorage`; migração dos 1675
   tickers daily + IEX 1h com split adjust; 405 testes verdes. Ver entrada
   de changelog abaixo.
2. **Catálogo de estratégias intraday short-hold** — começar em 1h
   (sweet spot entre ruído e frequência) e depois 15m/5m:
   - ❌ **Chan mean-reversion / cointegration pairs**
     `[algo_trading_chan]` — testado em GLD-SLV 1h (2026-04-15 noite),
     falhou no gate de cointegração (t_stat_OU=−2.956 > −3.4). Pode
     voltar em §7.2 como basket de 3 pares se algum outro pair passar.
   - ❌ **Volatility-expansion breakout (Donchian + YZ cone)**
     `[volatility_trading, Sinclair + trading_systems_methods, Kaufman]`
     — testado em SPY+GLD+TLT 1h (Bundle γ). FAIL: PBO=0.687, DSR 0/12,
     WF 0/12. Diagnostic em `reports/grid_vol_expansion_20260415-2301/`.
   - **Ehlers BP Swing em 1h** — **PRÓXIMO**. Recalibrar thresholds, a
     infra já suporta.
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

## ⚠️ Avisos de retratação (2026-04-16 12:45)

Entries marcadas com **⚠️ RETRACTED** ou **CONCLUSÃO INVÁLIDA** abaixo
foram afetadas por bug crítico nos dados Tiingo IEX (placeholder bars
em US holidays sem split-adjust). Veja
[2026-04-16-1245-data-bug-winners-retracted.md](2026-04-16-1245-data-bug-winners-retracted.md)
para detalhes. Conclusões dessas entries não são confiáveis.

Entries marcadas com **DATA TAINTED (mas conclusão permanece)** usaram
dados ruins mas chegaram à conclusão certa pelo motivo errado (e.g.,
demoção de strategies que já não passariam de qualquer jeito).

## Entradas (mais recente primeiro)

- [2026-04-16 1435 — Phase B Lead #2: Custo-ablação — BollingerMR PASS, ETFRotation_top1 PASS, ETFRotation_top2 ⚠️ costs-sensitive (WF 5/8)](2026-04-16-1435-cost-ablation-phase-b-winners.md)
- [2026-04-16 1416 — ★ WINNER #3 [SWING BROKER]: ETF Rotation top-2 — Sharpe 0.708, OOS 2025 1.611, Q1 0.481 — Phase A COMPLETA](2026-04-16-1416-etf-rotation-top2-PASS.md)
- [2026-04-16 1420 — ★ WINNER #2 [SWING BROKER]: ETF Monthly Rotation SPY/QQQ/IWM/GLD/TLT — Sharpe 0.708, OOS 2025 Sharpe 1.477, 2026-Q1 Sharpe 1.081](2026-04-16-1420-etf-rotation-monthly-PASS.md)
- [2026-04-16 1347 — ★ WINNER #1 [SHORT-HOLD CFD]: Bollinger MR + GARCH Sizing SPY 1h — Sharpe 0.982, OOS 2025 Sharpe 0.552, 2026-Q1 Sharpe 2.784](2026-04-16-1347-bollinger-mr-garch-spy-1h-PASS.md)
- [2026-04-16 1245 — 🚨 BUG CRÍTICO: TODOS os 3 winners retratados; bars-fake da Tiingo IEX em US holidays](2026-04-16-1245-data-bug-winners-retracted.md)
- [2026-04-16 1300 — Cross-asset overlap: XLK-XLE corr 0.83 → ~2 edges efetivos, não 3 ⚠️ RETRACTED](2026-04-16-1300-bollinger-mr-overlap.md)
- [2026-04-16 1230 — MC bootstrap dos winners: XLK robusto, SPY OOS Sharpe lower bound = 0.031 ⚠️ RETRACTED](2026-04-16-1230-bollinger-mr-mc-bootstrap.md)
- [2026-04-16 0833 — Tiingo cache audit: Q1-2026 stress é trustworthy + latent bug detectado ⚠️ CONCLUSÃO INVÁLIDA](2026-04-16-0833-tiingo-cache-audit.md)
- [2026-04-16 0130 — Kalman Pairs OOS 2025 FAIL: demoted de winner #2 ⚠️ DATA TAINTED (mas conclusão FAIL permanece)](2026-04-16-0130-kalman-pairs-oos-FAIL.md)
- [2026-04-16 0045 — Kalman Pairs SPY-IWM 1h: PASS (3 gates) ⚠️ RETRACTED](2026-04-16-0045-kalman-pairs-spy-iwm-PASS.md)
- [2026-04-16 0010 — OOS 2025 Hold-out: Bollinger MR edge CONFIRMA ⚠️ RETRACTED](2026-04-16-0010-bollinger-mr-oos-2025-PASS.md)
- [2026-04-15 2350 — PRIMEIRA ESTRATEGIA VENCEDORA: Bollinger MR 1h SPY PASS ⚠️ RETRACTED](2026-04-15-2350-bollinger-mr-1h-PASS.md)
- [2026-04-15 2301 — Vol-Expansion Breakout SPY+GLD+TLT 1h ❌](2026-04-15-2301-vol-expansion-1h.md)
- [2026-04-15 2109 — Chan pairs GLD-SLV 1h ❌](2026-04-15-2109-chan-pairs-1h.md)
- [2026-04-15 1830 — tiingo_service lazy-cache ✅](2026-04-15-1830-tiingo-service.md)
- [2026-04-15 1800 — Pivô intraday short-hold](2026-04-15-1800-pivot-intraday.md)
- [2026-04-15 1541 — F3.D Portfolio Clenow+Ehlers](2026-04-15-1541-portfolio-f3d.md)
- [2026-04-15 1353 — Long-history Ehlers SPY](2026-04-15-1353-long-history-ehlers.md)
- [2026-04-15 1349 — AFML meta-labeling Run 4 Step 1](2026-04-15-1349-afml-meta-run4s1.md)
- [2026-04-15 0900 — Sincronização + decisões](2026-04-15-0900-sincronizacao-decisoes.md)
- [2026-04-14 — Tiingo + Run 3](2026-04-14-0000-tiingo-run3.md)
- [2026-04-13 — Runs 1-2 (Clenow + Ehlers)](2026-04-13-0000-runs-1-2-clenow-ehlers.md)
- [2026-04-12 — Phase 2 concluída](2026-04-12-0000-phase2-backtest-done.md)
- [2026-04-11 — Phase 0 (knowledge base)](2026-04-11-0000-phase0-knowledge-base.md)
- [≤ 2026-03-31 — Decisões fundacionais](2026-03-31-0000-decisoes-fundacionais.md)
