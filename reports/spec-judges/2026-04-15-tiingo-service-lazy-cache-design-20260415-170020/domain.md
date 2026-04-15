# Juiz Adversarial — Domínio & Literatura

**Spec:** `docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md`
**Data:** 2026-04-15 17:00
**Veredito:** BLOCK

## Resumo executivo

Spec de infra bem-estruturado e defensivo na maior parte, mas contém **duas afirmações
materialmente incorretas** sobre a API Tiingo IEX que derrubam a hipótese de sucesso v1
e tornam o design atual uma armadilha contra o pivô intraday short-hold. (1) Retention
IEX: spec afirma "tipicamente 2 anos" no caveat 5.2 — a documentação pública e o wrapper
`riingo` convergem em `~2000 bars` da frequência pedida (~83 dias em 1h, ~23h em 1min).
(2) `adj_close := close` para IEX: spec trata como caveat menor, mas fontes públicas
documentam explicitamente que **IEX intraday não é split/dividend-adjusted** — é
exatamente o bug que o commit `5ca9410` corrigiu em daily (`Sharpe 0.31 → 0.806` no SPY).
Além disso, a "regra inviolável" do projeto exige citação `[book.slug, p.X]` em toda
decisão técnica — o spec tem múltiplas decisões (slack per-freq, datetime tz-naive,
whitelist 1hour-only) apresentadas **sem citação** quando a literatura absorvida cobre o
ponto.

## Citações auditadas

| Afirmação no spec | Fonte citada | Verificação | Status |
|---|---|---|---|
| "URL structure `/iex/`, `/tiingo/daily/`, `/tiingo/crypto/`, `/tiingo/fx/`; `resampleFreq` param" §7.1 | `[Tiingo API docs]` (sem URL no spec) | WebSearch confirma endpoint `https://api.tiingo.com/iex/{ticker}/prices?resampleFreq=1Hour` (ver `tiingo-python` issue #117, riingo docs) — mas literal `1hour` (lowercase) do spec §2.6 pode não ser aceito pelo servidor — documentação usa `1Hour` / `1hour` inconsistentemente. | ⚠️ parcial — smoke #1 resolve, mas URL citada sem fonte nominável |
| "Janela IEX retention desconhecida. Free ~30d; paid varia, tipicamente 2a mas não documentado universalmente" §5.2 | — (auto-afirmado, sem fonte) | **FALSO.** Documentação oficial + riingo + tiingo-python convergem: IEX retorna **os 2000 ticks mais recentes da frequência pedida** — ~83 dias em 1hour, ~23h em 1min, ~6.9 dias em 5min. Não é "2 anos". Ver `https://business-science.github.io/riingo/reference/riingo_iex_prices.html`. | ❌ não confere — afeta hipótese de sucesso v1 |
| "IEX não fornece `adjClose` (splits não ajustados)" §5.6 | — (caveat sem citação) | **Confirmado por fonte externa** (`portfoliooptimizer.io/blog`, Tiingo docs EOD vs IEX). Mas a *mitigação* `adj_close := close` é exatamente o bug que o projeto já pagou: commit `5ca9410` descobriu que ler `close` (não-ajustado) triplicou o Sharpe do SPY quando corrigido para `adj_close`. Decisão da mitigação deveria citar `[advances_fin_ml, ch.3]` ou `[quant_trading_chan, p.37]` (fórmula do split multiplier) + `[trading_systems_methods, p.914]` (splits perdem volatility characteristics). | ❌ não confere — ver Pitfalls |
| "Slack por frequência: daily 7d, 1hour 1d" §2.4 | — (raciocínio narrativo "market open at 09:30") | Decisão numérica arbitrária. Literatura não cobre slack de cache — é infra — mas o *fenômeno subjacente* (sessões de mercado, DST, market holidays) tem tratamento canônico em `pandas_market_calendars` (mencionado só como "fora de escopo" §6.4). | ⚠️ parcial — decisão infra aceitável, mas ausência de `pandas_market_calendars` é racionalizada sem citação |
| "Lazy-cache contract" §1.2 | — (auto-afirmado) | Padrão canônico — não exige citação. Aceitável. | ✅ OK |
| `[advances_fin_ml, López de Prado]` — "N/A — infra sem gate estatístico" §7.1 | explicit N/A | AFML **cobre** adjust-for-splits em ch.3 (dollar bars "adjust for price level changes (stock splits)" — `[ml_for_algo_trading, ch.2, p.35-40]`) e lookahead bias em `[algo_trading_chan, p.4, ch.1]`. Citação N/A aqui mascara a existência de conteúdo do knowledge base diretamente aplicável. | ❌ N/A incorreto |

## Decisões sem citação (análise)

1. **`frequency="daily"` default** (§2.3, §5.8) — backward-compat pura. Canônica, não precisa citação. ✅
2. **Whitelist `{daily, 1hour}` v1, `5min/1min` via NotImplementedError** (§2.2) — decisão de escopo MVP. Justificado por brainstorming. ✅ aceitável como infra.
3. **Slack `{daily: 7d, 1hour: 1d}`** (§2.4) — decisão numérica arbitrária. Pitfall: crypto 24/7 nem tem "market open feriado" equivalente. Caveat 5.7 reconhece, defere para v2. **Deveria citar** `[algo_trading_chan]` (intraday mean-reversion, sem cobertura explícita de slack) ou pelo menos um racional vinculado à literatura de microstructure — `[trading_exchanges, Harris, p.33-34]` tem taxonomia de sessões. 🟡
4. **`adj_close := close` para IEX** (§3.3, §5.6) — esta é a mais grave. É **exatamente** o bug do commit `5ca9410` revivido em intraday. Deveria ser **decisão consciente com citação**:
   - `[ml_for_algo_trading, ch.2, p.35-40]` — dollar bars adjust for splits; tick-bar normality fails.
   - `[quant_trading_chan, p.37]` — fórmula canônica de split/dividend multiplier.
   - `[trading_systems_methods, p.914]` — "Back-adjusted split-adjusted stocks: 1990 $50 stock with 2x splits becomes $12.50 — loses volatility characteristics."
   - `[ml_for_algo_trading, ch.8, p.223-224]` — Look-ahead bias from restated fundamentals, retroactive splits.
   - A mitigação proposta ("v1.1 emitir warning se ticker teve split") é **tecnicamente realizável** porque o daily cache já tem `splitFactor` — mas não está no v1, ficando dívida oculta. 🔴
5. **`datetime tz-naive`** (§2.4) — decisão de compatibilidade com `_normalize`. Reasonable, mas para intraday (especialmente equities com DST + RTH windows, crypto 24/7 UTC, forex 24/5 Sydney open) tz-naive é **anti-pattern** documentado. Não há citação — e nenhum livro do knowledge base cobre timezone rigor explicitamente, mas ver Tiingo docs (timestamps retornam em ISO8601 com timezone). 🟡
6. **"asset_class intraday crypto/forex usa mesmos endpoints daily"** (§2.6) — aceitável pela documentação Tiingo (crypto/fx aceitam `resampleFreq`). Citação `[Tiingo API docs]` genérica demais — falta verificar se crypto `resampleFreq=1hour` tem a mesma limitação de retention ou se é efetivamente "sem limite" (crypto tem backfill profundo). 🟡

## Pitfalls ignorados

1. **Split não-ajustado em intraday é literalmente o bug do commit `5ca9410`** — spec o reconhece como caveat mas **não eleva ao nível de blocker**. Essa é a falha mais grave do spec na ótica do domínio, porque:
   - Estratégias short-hold intraday (Chan mean-reversion em 1h, Ehlers BP em 1h) são **extremamente sensíveis** a jumps artificiais. Um 2:1 split num day trade = sinal falso de crash de 50%.
   - `[trading_systems_methods, Kaufman, p.914]` documenta que percentage-based stops e vol calcs quebram em série não-ajustada.
   - `[algo_trading_chan, p.4, ch.1]` documenta look-ahead bias em intraday como erro de programação que infla retornos.
   - A mitigação v1 (`adj_close := close`) aceita silenciosamente este erro para rodar "grids de backtest" intraday. **Isso vai reproduzir o problema Sharpe-inflado-por-split que o projeto já pagou.**
2. **Retention IEX ~2000 bars ≠ "2 anos"** (`riingo docs`, GitHub tiingo-python issue #117):
   - Em 1hour, ~83 dias de história total. **Impossível** validar Ehlers BP swing 1h com ciclos de 40 bars + lookback warmup + test/train split em 83 dias.
   - Em 5min/1min, ainda menor — **inviável** para as estratégias Chan pairs que o pivô planeja.
   - Spec §5.2 minimiza ("aceita 1 re-fetch por repeat wide request"), mas o verdadeiro problema é **disponibilidade de história** para testar estratégias sérias, não custo de API.
   - **Esta é a incerteza de primeira ordem** — o spec reconhece que é (§5.1 + §5.2) e propõe o smoke para medir, o que é bom — mas a hipótese H1 ("v1 destrava Chan pairs, Ehlers 1h") **falha antes de começar** se retention for realmente ~83 dias.
3. **Crypto 24/7 vs slack datetime** — caveat 5.7 reconhece, defere. OK como infra, mas ao mesmo tempo que o pivô quer testar volatility breakouts em crypto (BTCUSD 1h), usar slack de 1d em série continuous é inadequado. `[volatility_trading, Sinclair, ch.9 p.218-220]` menciona high-frequency intraday para vol modeling — não cobre o slack mas reforça que intraday crypto é regime diferente.
4. **Look-ahead risk em bar close vs open timestamp** — `[algo_trading_chan, p.4, ch.1]` alerta explicitamente: "using future information (e.g., intraday high/low before bar close)". Spec §3.3 menciona "datetime com timestamp intradia" mas não explicita **em qual ponto da bar o timestamp é alinhado** (open? close?). Isso afeta triple-barrier labels intraday e sinais gerados via roofing filter. Spec deveria explicitar convention.
5. **Sem menção ao gap do pivô→daily→intraday**: os 5 ciclos diários que falharam DSR usaram dados ajustados (yfinance/Tiingo daily). Migrando para intraday sem ajuste, o spec torna a **comparação baseline inválida** — daily adj vs intraday raw.
6. **Primary exchange vs consolidated prices** — `[algo_trading_chan, p.10-11, ch.1]`: "MOC/MOO orders execute on the primary exchange (NYSE, Arca, Nasdaq), not at the consolidated tape price; using consolidated prices inflates mean-reversion backtest performance." IEX é **uma exchange específica**, não consolidated — spec não discute se isto é feature (benefício Chan documenta) ou bug (representatividade). Merece uma linha.
7. **`[advances_fin_ml, p.59-62]` dollar/tick-imbalance bars** — time bars (1h) são **subótimas** para ML pipelines segundo AFML ch.2. Spec escolhe 1h time bars sem mencionar este trade-off. Aceitável para MVP mas deveria reconhecer.

## Preocupações

### 🔴 Críticas (bloqueiam)

1. **Retention IEX inflada de ~83 dias para "~2 anos" no caveat §5.2.** Docs públicas convergem em 2000 bars, o que para 1hour é ~83 dias de trading — **insuficiente** para qualquer estratégia seriamente testável (Chan pairs precisa estimar half-life, Ehlers precisa 40-bar ciclo + warmup). Hipótese de sucesso v1 ("baixa bars IEX... segunda chamada hita cache") passa em smoke test mas **não habilita** o pivô intraday. Fonte: `https://business-science.github.io/riingo/reference/riingo_iex_prices.html`, GitHub tiingo-python issue #117.
2. **`adj_close := close` em intraday re-introduz o bug do commit `5ca9410` na camada intraday.** Este é o ponto em que "spec de infra" silenciosamente introduz dívida técnica no pivô: toda estratégia intraday subsequente herda série não-ajustada sem warning, sem citação, sem teste de regressão. Mitigação "v1.1 emitir warning" não é suficiente. O correto é v1: aplicar `splitFactor`/`divCash` do daily cache ao IEX intraday em pós-processamento (o projeto **já tem** esses dados no daily manifest).

### 🟠 Altas

3. **Decisão `adj_close := close` sem citação** das fontes que o knowledge base contém — `[quant_trading_chan, p.37]`, `[trading_systems_methods, p.914]`, `[ml_for_algo_trading, ch.2 p.35-40 + ch.8 p.223-224]`. Viola Regra 2 do projeto (`.claude/CLAUDE.md`).
4. **Reference §7.1 marca `[advances_fin_ml, López de Prado]` como "N/A"** em spec que altera a fundação de dados de todas as estratégias intraday futuras. AFML ch.3 é literalmente sobre data structures para ML financeiro.
5. **Crypto retention não verificado** — spec assume que endpoint `/tiingo/crypto/prices?resampleFreq=1hour` tem mesma limitação ou não. Smoke test (§6.1 passo 1) deve incluir probe explícito para crypto, não só SPY.

### 🟡 Médias

6. **Slack `1d` para 1hour** sem citação. Plausível (cobre market open gap, DST), mas crypto 24/7 quebra o invariante. Caveat 5.7 reconhece mas fica YAGNI — aceitável para v1 desde que a lista de "quando devo re-visitar" seja concreta.
7. **Timezone tz-naive para intraday** — anti-pattern documentado, mas ausência no knowledge base. Aceitável se documentado como "intencional por compatibilidade com pipeline existente".
8. **Bar timestamp convention (open vs close)** não explicitado em §3.3. `[algo_trading_chan, p.4]` alerta sobre look-ahead.
9. **Smoke gate §6.2 não testa retention observada vs esperada** — deveria ter critério quantitativo: "se retention observada < X meses para 1h, BLOCK spec e revisar antes de refatorar."

### 🟢 Baixas

10. Layout α vs alternativas é bem justificado (§2.3).
11. Migração idempotente + dry-run + backup é ótima prática (§4).
12. Caveat 5.5 (transacional parcial) bem tratado.

## Pontos fortes (domínio)

- **Reconhece a incerteza de primeira ordem** (§5.1 + §6.1 passo 1): smoke test antes de refactor. Isso é aplicação implícita do princípio de Chan (`[quant_trading_chan]`): "test before you build."
- **Bulk daily preservado** via migração — respeita o investimento do Tiingo bulk e permite cancelamento da subscrição após v1. Alinha com a preocupação do usuário (swap overnight + short-hold).
- **Schema extensível para 5m/1m** — layout `{freq}/{prices,meta}/{ticker}` escala naturalmente; adicionar 5min é só linha no whitelist + fixture.
- **Blast-radius `rm -rf data/tiingo/1hour/`** isolado — bom defensive engineering.
- **Manifest nested preserva invariante "single source of truth"** (§2.3) — consistente com `[advances_fin_ml]` "reproducibility" emphasis implícita.
- **YAGNI explícito em §6.4** — deferrals nomeados com critério de re-entrada.
- **TDD-first ordem em §6.1** — alinhado com Kaufman `[trading_systems_methods]` e Chan `[quant_trading_chan]` sobre rigor empírico.

## Sugestões concretas

1. **BLOCK até smoke retention probe**: antes de qualquer refactor, rode o smoke com `startDate=2020-01-01` e meça **quanto a API efetivamente retorna**. Se < 6 meses de 1h, hipótese v1 precisa ser re-escrita (ex.: "destravar daily → 1h com retention limitada, shift estrategia para baseline mensal, Phase 4 monetiza cache"). Fonte: `riingo` docs + tiingo-python issue #117.
2. **Remover `adj_close := close` como mitigação default.** Em v1, implementar split-adjust usando `splitFactor`/`divCash` já presentes no daily cache. Referência normativa: `[quant_trading_chan, p.37]` — fórmula do multiplier. Se splitFactor para um ticker não estiver no cache daily (ex.: BTCUSD crypto), `NotImplementedError` com mensagem clara, não fallback silencioso.
3. **Adicionar citações no spec** (Regra 2 do projeto):
   - `§3.3 "adj_close := close"` → `[trading_systems_methods, p.914]` (split-adjusted stocks lose vol characteristics) + `[quant_trading_chan, p.37]` (multiplier formula) + `[ml_for_algo_trading, ch.2 p.35-40]`.
   - `§2.4 "slack 1d"` → racional documentado como "heurística de sessão equity, override para crypto em v2" + citação de microstructure (`[trading_exchanges, Harris, p.33-34]` se sessões forem relevantes).
   - `§5.6 "v1.1 warning"` → `[advances_fin_ml, ch.3]` (data cleanliness).
   - `§7.1` substituir AFML N/A por referência a ch.3 para data structures + ch.8 look-ahead.
4. **Smoke §6.1 passo 1 deve retornar:** `observed_retention_bars`, `observed_first_dt`, `observed_last_dt` por endpoint, e `has_split_since_start` (cross-check com daily splitFactor). Gate go/no-go: se retention < 250 bars (~10 dias 1h), BLOCK.
5. **Documentar convenção de bar timestamp** em §3.3 — open ou close? `[algo_trading_chan, p.4, ch.1]` é a citação.
6. **Primary vs consolidated flag** — adicionar uma nota em §2.6 sobre IEX ser primary, com citação `[algo_trading_chan, p.10-11, ch.1]`.
7. **Fora de escopo explícito sobre `pandas_market_calendars`** (§6.4) deveria virar **caveat pró-ativo** com `[Harris, p.33-34]` como fundamento do porquê calendar-awareness importa.
8. **Hipótese H1 v1 deve ser re-escrita** após smoke retention, incluindo explicitamente: "se retention curta → v1 entrega infra + log de retention observada; estratégias intraday esperam v1.1 com rolling cache auto-refresh (crônica)."

## Evidência consultada

### Livros do projeto

- **`advances_fin_ml.md`** — ch.3 cobre data structures (dollar bars, tick-imbalance bars p.57-62) e data cleanliness. Citação N/A do spec §7.1 está incorreta; ch.3 é diretamente aplicável à decisão `adj_close := close`.
- **`ml_for_algo_trading.md`** — ch.2 p.35-40 "dollar bars adjust for price level changes (stock splits)"; ch.2 p.55 "back-adjust pre-split EPS"; ch.8 p.223-224 "look-ahead bias from retroactive splits"; ch.8 p.225-226 "NEVER backtest trades executing at close-price of same bar." Três citações diretas ausentes no spec.
- **`algo_trading_chan.md`** — p.4 ch.1 look-ahead bias em intraday; p.10-11 ch.1 primary vs consolidated prices; p.94 ch.4 Buy-on-Gap intraday mean reversion; p.183-184 ch.8 stop loss em mean-reversion (afeta Chan pairs 1h). Todas relevantes.
- **`quant_trading_chan.md`** — p.37 fórmula split/dividend multiplier (citação canônica ausente); p.141-142 half-life GLD-GDX (afeta Chan pairs 1h subsequente); p.159-160 ch.6 intraday compiled languages (afeta escolha Python runtime para Chan pairs — spec não discute).
- **`trading_systems_methods.md`** — p.914 "Back-adjusted split-adjusted stocks lose volatility characteristics" — citação perfeita para a decisão do spec sobre adj_close em intraday. Ausente.
- **`cycle_analytics.md`** — DSP Ehlers BP filter (p.47-51 ch.5), zero-lag quando tuned ao ciclo dominante. Relevante para Ehlers 1h no pivô, não cobre escolha de data infra diretamente.
- **`volatility_trading.md`** — ch.9 p.218-220 high-frequency intraday para vol forecasting. Intraday crypto/equity 1h relevante mas genérico.
- **`trading_exchanges.md`** — Harris p.33-34 tick size e time precedence; não cobre retention mas fundamenta microstructure arguments.
- **`machine_trading.md`** — p.159-160 ch.6 intraday holding minutes → capacity limit (ES NBBO ~$30M/touch, AAPL 189 shares). Relevante para viabilidade CFD Pepperstone downstream.

### Fontes externas (arXiv/SSRN/etc)

- [riingo_iex_prices reference](https://business-science.github.io/riingo/reference/riingo_iex_prices.html) — "the IEX feed returns the most recent 2000 ticks of data at the specified frequency... cannot request data older than today's date minus 2000 data points."
- [tiingo-python issue #117](https://github.com/hydrosquall/tiingo-python/issues/117) — historical intraday IEX endpoint request; confirma endpoint `/iex/{ticker}/prices` com `resampleFreq`.
- [Tiingo IEX documentation](https://www.tiingo.com/documentation/iex) — página acessada mas WebFetch só retornou título "Stock Market Tools | Tiingo" (conteúdo parece bloqueado ou render-heavy). Documentação EOD cita 50+ anos de história (1962) **apenas para daily**, não IEX intraday.
- [Tiingo EOD vs IEX split adjustment (external blog)](https://portfoliooptimizer.io/blog/selecting-a-stock-market-data-web-api-not-so-simple/) — "Split and dividend adjustment does not apply to intraday data (it's raw). This is a significant limitation when using Tiingo's IEX intraday data." Confirma a necessidade de tratamento explícito no v1.
- [Tiingo End-of-Day docs](https://www.tiingo.com/documentation/end-of-day) — confirma que EOD tem `adjClose`, `divCash`, `splitFactor`, e segue CRSP adjustment methodology — estes dados **já estão no daily cache** do projeto (usado no commit `5ca9410`), logo aplicar adjust ao IEX é computacionalmente viável.

## Veredito

**BLOCK.**

**Regra aplicada:** "BLOCK = alguma afirmação técnica contradiz a literatura OU citação falha em ponto crítico." Aplicável duas vezes:

1. Retention "tipicamente 2 anos" (§5.2) contradiz documentação pública (~2000 bars). Materialmente inválida a hipótese de sucesso H1 "destrava intraday para Chan pairs + Ehlers 1h".
2. Decisão `adj_close := close` (§3.3, §5.6) re-introduz o bug do commit `5ca9410` em intraday, com três citações do knowledge base ignoradas (Kaufman p.914, Chan p.37, Jansen ch.2 p.35-40), violando Regra 2 do projeto em ponto sensível downstream (métricas de toda estratégia intraday).

Desbloqueio é mecânico, não re-design:

- Rodar smoke retention probe antes de commitar o spec; se retention < 6 meses em 1h, atualizar hipótese H1 e escopo v1 no próprio spec.
- Mover `adj_close` de "caveat v1.1" para decisão v1 consciente com citação, usando `splitFactor`/`divCash` já presentes no daily cache como fonte de ajuste.
- Adicionar citações `[book.slug, p.X]` em todas as 4 decisões identificadas nas seções 🔴/🟠.
