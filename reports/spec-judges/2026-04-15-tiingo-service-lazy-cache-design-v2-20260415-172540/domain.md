# Juiz Adversarial — Domínio & Literatura (v2, 2ª rodada)

**Spec:** `docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md` (v2)
**Data:** 2026-04-15 17:30
**Veredito:** PROCEED-WITH-CHANGES

## Resumo executivo

A v2 resolveu **parcialmente** os dois 🔴 da v1. Retention IEX agora está
correta (`~2000 bars = ~83 dias em 1h`, §5.2, com 3 URLs verificadas 200-OK)
e o `adj_close := close` foi movido de caveat para decisão v1 consciente
com citações (§3.3). Porém a "correção" do adj_close **introduz uma
fórmula matematicamente incorreta** que contradiz a citação canônica de
Chan p.37 usada para justificá-la — e 3 das 10 novas citações de livros
do knowledge base têm mismatch entre página citada e conceito do spec.
O gate retention ≥ 12 meses do Smoke #1 (§6.2) também tem lógica
inconsistente: é **fisicamente impossível** de atingir em 1h dado o limite
de 2000 bars documentado — ou seja, o spec embute um FAIL mecânico
garantido. Isto não invalida a arquitetura, mas **precisa de correção
antes do writing-plans** (não exige re-brainstorm).

## Citações auditadas (10 novas de §7.1 + fórmula de §3.3)

| # | Citação | Uso no spec | Verificação (grep em `books/summaries/`) | Status |
|---|---|---|---|---|
| 1 | `[quant_trading_chan, p.37]` | §3.3 fórmula split/dividend multiplier | `quant_trading_chan.md:93,100` — **EXISTE**, mas a fórmula é `multiplier = (Close(T-1) − d) / Close(T-1)` **aplicada multiplicativamente**, com explícito "**do not subtract $d$**, to preserve returns". Spec implementa `close × cumprod(splitFactor) − cumsum(divCash × splitFactor)` que **subtrai** divCash — exatamente o que Chan p.37 proíbe. | ❌ fórmula do spec contradiz a citação |
| 2 | `[trading_systems_methods, Kaufman, p.914]` | §3.3 split-adjusted stocks lose vol | `trading_systems_methods.md:453` — "1990 $50 stock with 2x splits becomes $12.50 — loses volatility characteristics". Confere **literal**. | ✅ OK |
| 3 | `[ml_for_algo_trading, ch.2, p.35-40]` | §3.3 dollar bars + price-level adjustment | `ml_for_algo_trading.md:35` — "dollar bars adjust for price level changes (stock splits, large moves)". Confere. | ✅ OK |
| 4 | `[ml_for_algo_trading, ch.8, p.223-224]` | §3.3 look-ahead bias de retroactive splits | `ml_for_algo_trading.md:22,379` — "Look-ahead bias from restated fundamentals, **retroactive splits**, incorrect EPS/price alignment". Confere. | ✅ OK |
| 5 | `[advances_fin_ml, López de Prado, ch.3]` | §3.3 "data structures para ML financeiro" | **AFML ch.3 é labeling** (triple-barrier p.78-80, meta-labeling p.84-89). **Data structures são ch.2** (dollar bars p.57-59, TIBs p.59-62, VRBs p.62-63). Capítulo errado. | ❌ mis-citation (deveria ser `ch.2`) |
| 6 | `[advances_fin_ml, p.59-62]` | §6.4 time bars vs dollar/tick-imbalance | `advances_fin_ml.md:21,52` — TIBs em `p.59-62`. Confere. | ✅ OK |
| 7 | `[algo_trading_chan, p.4, ch.1]` | §2.6 look-ahead bar-timestamp | `algo_trading_chan.md:19` — "using future information (e.g., intraday high/low before bar close)...a programming error that inflates returns [p.4, ch.1]". Confere. | ✅ OK |
| 8 | `[algo_trading_chan, p.10-11, ch.1]` | §2.6 IEX primary vs consolidated SIP | `algo_trading_chan.md:22` — "MOC/MOO orders execute on the primary exchange...using consolidated prices inflates mean-reversion backtest performance [p.10-11, ch.1]". Confere. | ✅ OK |
| 9 | `[systematic_trading, Carver, p.32-35]` | §1.4 "custo vs frequência skew" | `systematic_trading.md:37,50` — p.32-35 ch.2 cobre **skew de distribuição de retorno** (trend=+skew, carry=−skew) + Sharpe annualised. Não cobre "cost vs frequency". A **citação correta** para custo/turnover seria `p.185-188, ch.12` (Annual cost = Standardised cost × Annual turnover; speed limits 0.13 SR/year). | ❌ página errada / conceito diferente |
| 10 | `[trading_exchanges, Harris, p.33-34]` | §2.4 "taxonomia de sessões 24/7 vs 24/5 vs RTH" | `trading_exchanges.md:24-26,102-106,169,194` — p.33-34 é sobre **oral auctions, price priority, time precedence, tick size**. **NÃO** cobre market-session taxonomy. Harris cobre sessions em outras páginas (ex.: call auctions, opening procedures), mas p.33-34 não é isso. | ❌ página errada (conceito ausente) |
| 11 | **Fórmula §3.3** `cumprod(splitFactor) − cumsum(divCash × splitFactor)` | §3.3 "fórmula canônica de total-return adjustment" | CRSP (que Tiingo segue, confirmado por docs) usa **proporcional multiplicativo**; Chan p.37 explicitamente veda subtração de $d$. Google/Yahoo também aplicam fator proporcional multiplicativo. A fórmula proposta **mistura duas convenções incompatíveis** — gera `adj_close` diferente do daily `adjClose` Tiingo/CRSP que o projeto já usa. Quebra §5.7 "apples-to-apples". | ❌ matematicamente incorreta |

Score auditoria: **6/10 citações confirmam** + **3/10 têm mismatch
página↔conceito** + **1/10 fórmula contradiz a própria citação**.

## Decisões sem citação (análise v2)

- **§2.4 slacks numéricos específicos** (equity 1h=12h, crypto 1h=6h,
  forex 1h=48h) — spec reconhece explicitamente como "heurística de
  engenharia, não coberto por livro". Aceitável por honestidade.
- **§6.2 gate ≥ 365 dias (12 meses)** — parâmetro sem citação. Escolha
  razoável para viabilizar backtest de ciclo Ehlers 40-bar (warmup +
  train/test em resolução horária), mas não é derivado da literatura.
  Aceitável como decisão de engenharia explícita. 🟡
- **§1.4 alerta `median_hold > 48h`** — threshold arbitrário. Poderia
  citar Carver p.212 (semi-auto stop-loss X=4 → holding 6.5 semanas como
  design-by-turnover), ou ligar-se a swap cost CFD Pepperstone. 🟡

## Pitfalls ignorados (novos em v2)

1. **Fórmula §3.3 violando a própria citação.** A versão adversarial do
   crítico anterior levantou essa categoria exata. A resposta v2
   escreve "fórmula canônica de total-return adjustment
   `[quant_trading_chan, p.37]`" abaixo de uma expressão que Chan
   **explicitamente veda** ("do not subtract $d$, to preserve returns",
   `quant_trading_chan.md:100`). Se implementado literalmente,
   `adj_close_intraday` será sistematicamente **inferior** ao
   `adj_close_daily` CRSP do mesmo dia → quebra teste §5.7
   (apples-to-apples) e §6.2 gate "Split adjust integração tolerance
   1e-6". Correção: usar apenas `cumprod(splitFactor × divFactor)` onde
   `divFactor[T] = (Close(T-1) − divCash) / Close(T-1)` — a forma de
   Chan e CRSP. 🔴
2. **§6.2 gate retention ≥ 365d é FAIL mecânico garantido em 1h.** Dado
   docs públicas convergentes em 2000 bars × 1h ≈ 83 dias, Smoke #1
   **sempre** vai retornar retention < 365d. Isso significa que o spec
   v1 é **já-abortado em §6.2**; §6.3 "Cenário A" nunca é alcançável.
   Três leituras possíveis: (a) o gate é intencionalmente muro-contra-
   delírio para forçar pivot para scheduled-cron antes de refactor; (b)
   o spec depende de surpresa positiva (algum plano pago Tiingo tem
   retention > 2000 bars não documentada publicamente); (c) erro de
   calibração. O spec §6.3 Cenário B admite o risco ("~1h + re-brainstorm"),
   mas §1.3 "Assumindo retention compatível, o trabalho está entregue
   quando..." e §6.3 Cenário A (~8-9h) sugerem o usuário ainda espera
   atingir o gate. A **ambiguidade é o problema** — o spec deve afirmar
   claramente "não esperamos passar o gate em 1h; executar Smoke #1 é
   para confirmar e documentar, não para autorizar refactor". 🔴
3. **Gate 365d sem justificativa de domínio.** Por que 12 meses e não
   6 meses ou 24 meses? A citação disponível seria
   `[ml_for_algo_trading, ch.8, p.227]`: "2 years of daily data supports
   conclusions about at most ~7 strategy variants; 5 years supports ~45."
   Para intraday 1h, ≥ 12 meses equivaleria a ~1.600 bars úteis — o que
   ainda é magro para uma grid Chan/Ehlers sem walk-forward. Spec não
   traz essa ligação. 🟡
4. **§3.3 ignora `divFactor` pronto em Tiingo.** Tiingo API **expõe**
   `adjClose`/`adjOpen`/etc já calculados pela CRSP methodology. Se o
   projeto quer a série ajustada, o caminho canônico é chamar IEX raw +
   join com daily `adjClose/close` ratio, não reimplementar a fórmula de
   Chan p.37 em código próprio. Reimplementação aumenta superfície de
   bug vs. usar Tiingo's já-computado. 🟠
5. **§2.6 "IEX primary not consolidated" é CONTRA-INDICATION para Chan
   pairs em 1h.** A citação `[algo_trading_chan, p.10-11]` está correta,
   mas o spec a documenta como "para evitar surpresa futura" e não como
   **warning estrutural**. Chan diz explicitamente (p.27-28) que MOC/MOO
   mean-reversion **não deve** usar consolidated-tape; mas também: CFD
   Pepperstone cTrader NÃO é IEX — execução real é em preço derivado de
   venue próprio do broker. Usar IEX em backtest de Chan pairs 1h para
   depois executar em Pepperstone introduz **venue-mismatch bias** não
   discutido. 🟠
6. **§1.4 não enforça gate `median_hold_hours`.** Spec diz "**não
   enforçado neste spec** (é infra de dados, não de estratégia)" — ok,
   mas o ponto da introdução de §1.4 era "evitar repetir pivô em
   resolução maior". Delegar ao consumer significa que a proteção é
   opt-in, não opt-out. Consistent com o escopo v1 mas a **declaração de
   intenção** em §1.4 parágrafo 1 é mais forte do que o enforcement
   efetivo. 🟡

## Pitfalls ignorados (legados de v1, ainda abertos)

- **Timezone tz-naive em intraday** (§2.3, §2.4) — v2 mantém a decisão.
  `_normalize` já produz tz-naive, aceito como compatibilidade, mas
  equity ET→UTC + DST cria ambiguidade 1x/ano. Sem citação no knowledge
  base; aceitável se documentado como **intencional**. 🟡 (já era 🟡 em
  v1, persiste.)

## Preocupações

### 🔴 Críticas (bloqueiam)

1. **Fórmula §3.3 contradiz a citação `[quant_trading_chan, p.37]` que
   a justifica.** Chan p.37: "Apply the multiplier to all prices before
   T (**do not subtract $d$**, to preserve returns)". Spec subtrai
   `cumsum(divCash × splitFactor)`. Implementação literal produz
   `adj_close` incompatível com `adjClose` CRSP do daily (que o projeto
   já usa), quebrando §5.7 apples-to-apples e o gate §6.2 "tolerance
   1e-6". Correção: dividend multiplier é **proporcional multiplicativo**
   `(Close(T-1) − d) / Close(T-1)`, multiplicado com `splitFactor` em
   `cumprod`. Ou mais simples: não recalcular — usar `adjClose` do
   daily cache como fonte de `scale_ratio = adjClose/close` e aplicar
   ao intraday do mesmo dia (via forward-fill intra-day).
2. **Gate §6.2 retention ≥ 365d é impossível em 1h conforme docs
   citadas em §5.2 (2000 bars × 1h ≈ 83 dias).** Ou o spec afirma
   explicitamente "esperamos FAIL e a aprendizagem é documentar o FAIL"
   (honesto), ou calibra o gate para retention realista (ex.: ≥ 60 dias
   em 1h = `~1400 bars`, suficiente para smoke + 1ª grid exploratória
   Chan pairs 1h). A ambiguidade atual ("Cenário A = 8-9h ... Cenário B
   = 1h + re-brainstorm") é gerenciamento de expectativa inadequado.

### 🟠 Altas

3. **Citação `[advances_fin_ml, López de Prado, ch.3]` em §3.3 aponta
   ao capítulo errado.** AFML ch.3 é labeling (triple-barrier +
   meta-labeling), não data structures. Correto: `ch.2` (p.57-66).
4. **Citação `[trading_exchanges, Harris, p.33-34]` em §2.4 aponta à
   página errada.** Harris p.33-34 cobre oral-auction price/time
   precedence + tick size, não market-session taxonomy.
5. **Citação `[systematic_trading, Carver, p.32-35]` em §1.4 aponta à
   página errada para o conceito.** Carver p.32-35 cobre return
   distribution skew. O conceito correto (custo × turnover) está em
   p.185-188, ch.12.
6. **§3.3 reimplementa adjustment em vez de usar `adjClose` pronto do
   daily.** Redundância + superfície de bug maior do que necessário.

### 🟡 Médias

7. **Gate 365d sem citação de literatura.** Poderia ligar-se a AFML p.227
   (2y = 7 variants; 5y = 45).
8. **§1.4 declara requisito mas delega enforcement ao consumer.** Diluído;
   OK no MVP mas explicitar "v1 documenta, v1.x enforce" seria honesto.
9. **§2.6 warning de venue-mismatch (IEX vs Pepperstone CFD) ausente.**
   Chan p.10-11 é citação correta mas o insight "aplicar a Pepperstone
   downstream" não aparece.
10. **Threshold §1.4 `median_hold > 48h`** arbitrário sem citação.

### 🟢 Baixas

11. §5.2 agora com 3 URLs verificadas 200-OK e convergência de 3 fontes —
    excelente upgrade vs v1.
12. §3.3 estrutura (pré-condição daily cache, NotImplementedError se
    equity sem daily, `adj_close := close` correto para crypto/forex) —
    lógica de fluxo **está certa**; só a fórmula é que precisa de fix.
13. §6.6 unblock path claro e bem dimensionado (< 30 min por nova freq).
14. §8 changelog bem feito — auditabilidade alta.

## Pontos fortes (domínio) v2

- **§5.2 corrigido:** retention IEX agora reflete fielmente as 3 fontes
  públicas (riingo docs + tiingo-python #117 + QuantStart) — URLs testadas
  e retornam 200.
- **§3.3 intent correto:** mover `adj_close` de caveat para decisão v1
  com 5 citações é a resposta certa à preocupação #2 do v1. Fórmula
  específica é o único defeito remanescente.
- **6/10 citações novas confirmam literalmente** (Kaufman p.914, Jansen
  ch.2 p.35-40 + ch.8 p.223-224, Chan p.4 + p.10-11, AFML p.59-62). Isso
  é um **salto qualitativo vs. v1** (0 citações onde a área do
  knowledge base existia).
- **§6.6 Unblock path** mostra que o design é evolucionário — 5m/15m/1min
  entram com 3 passos bem-definidos.
- **§4 migração hardened:** pgrep guard + backup automático + lockfile +
  teste de rollback é excelente engenharia defensiva.
- **§2.4 slack per-(asset_class, freq)** é melhoria substantiva vs v1
  uniforme; reconhece 24/7 crypto, 24/5 forex, RTH equity como
  propriedades estruturais.
- **§1.4 instrumentação de holding-period** é a resposta certa ao
  gatilho do pivô (não-medir foi o que mascarou o problema).

## Sugestões concretas

1. **Corrigir fórmula §3.3** para um dos dois caminhos:
   - **Caminho A (puro Chan p.37):** usar **multiplicativo só** —
     `split_mult[t] = cumprod(splitFactor[t..hoje])`,
     `div_mult[t] = cumprod(div_factor[T_i])` onde
     `div_factor[T_i] = (close[T_i−1] − divCash[T_i]) / close[T_i−1]`,
     `adj_close[t] = close[t] × split_mult[t] × div_mult[t]`.
     Sem `cumsum`; sem subtração.
   - **Caminho B (reutilizar CRSP do daily):** para cada bar intraday
     em dia D, calcular `ratio_D = adjClose_daily[D] / close_daily[D]`
     (já no cache), aplicar `adj_close_intraday[t] = close_intraday[t] ×
     ratio_D`. Zero reimplementação; exata consistência com o pipeline
     existente; apples-to-apples automático.
   - **Recomendação:** Caminho B — menor superfície de bug e garantia
     de consistência com o daily.
2. **Re-calibrar gate §6.2** para retention realista. Opções:
   - `≥ 60 dias em 1h` (cobre smoke + 1ª grid exploratória; ~1.400 bars
     úteis, 3 meses).
   - `≥ 30 dias em 1h` (apenas smoke + validação de URL; citação
     implícita: não sustenta DSR mas sustenta infra probe).
   - Manter 365d e **explicitar** "esperamos FAIL; aprendizagem é
     quantificar janela + acionar plan B scheduled-cron".
3. **Corrigir capítulo AFML em §3.3 e §7.1:** `ch.3` → `ch.2`
   (data structures: dollar bars, TIBs, VRBs estão em p.52-72 do livro
   real, coberto em `advances_fin_ml.md:20-22`).
4. **Corrigir página Harris em §2.4 e §7.1:** `p.33-34` (auction
   precedence) → citar outras páginas onde Harris cobre sessions, ou
   mover para `pandas_market_calendars` docs (externo) + nota "não há
   cobertura direta de session taxonomy nos 33 livros".
5. **Corrigir página Carver em §1.4 e §7.1:** `p.32-35` (skew) →
   `p.185-188 ch.12` (cost/turnover trade-off + speed limits 0.13/0.08
   SR/year).
6. **Adicionar nota §2.6 sobre venue-mismatch Pepperstone.** Citação
   `[algo_trading_chan, p.10-11]` já está no spec; basta elevar do
   "documentar para evitar surpresa" para warning estrutural: "IEX
   backtest ↔ Pepperstone execução requer validação adicional de slippage".
7. **Ligar gate 365d a AFML p.227** (2y = 7 variants; 5y = 45) se
   mantido; caso contrário, citar decisão de engenharia.
8. **§7.1 atualizar Carver + Harris + AFML ch** com páginas corretas;
   audit interno do changelog §8 item 12 ("10 citações novas") precisa
   refletir que 3 dessas 10 são mis-cited.

## Evidência consultada

### Livros do projeto

- `quant_trading_chan.md` — linhas 93, 100: fórmula multiplier +
  proibição de subtração de $d$. Contradiz fórmula §3.3 do spec.
- `trading_systems_methods.md` — linha 453: "1990 $50 stock...$12.50".
  Confere §3.3.
- `ml_for_algo_trading.md` — linhas 22, 35, 379: dollar bars p.35-40,
  look-ahead retroactive splits p.223-224. Confere §3.3.
- `advances_fin_ml.md` — linhas 20-22, 52: dollar bars / TIBs / VRBs
  em **ch.2 / p.57-63**, NÃO ch.3. Mis-citation §3.3.
- `advances_fin_ml.md` — linhas 21, 52: TIBs em p.59-62. Confere §6.4.
- `algo_trading_chan.md` — linhas 19, 22, 304: look-ahead p.4 +
  primary/consolidated p.10-11. Confere §2.6.
- `systematic_trading.md` — linhas 30, 37, 78-88, 265-271: skew em
  p.32-35 (**NÃO** cost/turnover); cost/turnover em p.185-188 ch.12.
  Mis-citation §1.4.
- `trading_exchanges.md` — linhas 24-26, 102-106, 169, 194: p.33-34 é
  auction precedence + tick, **NÃO** session taxonomy. Mis-citation §2.4.

### Fontes externas

- [riingo_iex_prices reference](https://business-science.github.io/riingo/reference/riingo_iex_prices.html) — 200 OK.
  "most recent 2000 ticks at specified frequency; cannot request older
  than today − 2000 data points." Confere §5.2.
- [tiingo-python #117](https://github.com/hydrosquall/tiingo-python/issues/117) —
  200 OK. Endpoint shape confirmado.
- [QuantStart Tiingo review](https://www.quantstart.com/articles/evaluating-data-coverage-with-tiingo/) —
  200 OK. "30+ years stock data" + "intraday partnership IEX" — não
  detalha retention, mas consistente com §5.2.
- [quantmod issue #289](https://github.com/joshuaulrich/quantmod/issues/289) —
  Tiingo expõe `splitFactor` + `divCash` separados.
- Tiingo EOD docs (via web search) — "follows CRSP guidelines...
  proportional dividend adjustment factor multiplied against historical
  prices." **CRSP é multiplicativo**, reforça que fórmula §3.3 (com
  `cumsum` subtrativo) é incorreta.

## Veredito

**PROCEED-WITH-CHANGES.**

**Regra aplicada:** "PROCEED-WITH-CHANGES = lacunas ≥ 🟠."

Razões v1 → v2:
- ✅ 🔴 v1 #1 (retention inflada) **resolvido** — §5.2 agora correto.
- ⚠️ 🔴 v1 #2 (adj_close := close) **parcialmente resolvido** —
  decisão certa, fórmula errada. Não mais BLOCK porque o **intent** está
  correto (aplicar adjust, não swallow); mas a fórmula contradiz a
  citação e quebra apples-to-apples.

Razões novas v2:
- 🔴 Fórmula §3.3 contradiz `quant_trading_chan, p.37` (subtração de
  divCash explicitamente proibida).
- 🔴 Gate §6.2 ≥ 365d é mecânica FAIL em 1h — requer calibração ou
  explicit surrender.
- 🟠 3/10 citações novas têm página errada (AFML ch, Harris p.33-34,
  Carver p.32-35).

Correções necessárias antes de writing-plans (mecânicas, não
re-design):

1. Trocar fórmula §3.3 por Caminho B (ratio do daily adjClose) OU fix
   Caminho A (multiplicativo puro sem cumsum).
2. Re-calibrar gate §6.2 retention ou afirmar FAIL esperado.
3. Fix 3 mis-citations (AFML ch.2, Harris substituir, Carver
   p.185-188 ch.12).

Com essas 3 correções, spec passa a PROCEED. A arquitetura central
(freq axis, migração guarded, slack per-AC, unblock path) é sólida e
não precisa de re-trabalho.
