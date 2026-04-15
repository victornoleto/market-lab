# Juiz Adversarial — Engenharia & Metodologia

**Spec:** `docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md` (v2)
**Data:** 2026-04-15 17:35
**Veredito:** PROCEED-WITH-CHANGES

## Resumo executivo

A v2 endereça de forma **substantiva e verificável** as duas preocupações
🔴 da v1:
- §1.3 + §5.2 + §6.1 passo 1 + §6.2 **materializam o Smoke #1 como
  gate de DESIGN** (retention ≥ 12 meses = PROCEED; < 12 meses = BLOCK
  e volta a brainstorm), com URLs concretos em vez da hipótese "~2a".
- §3.3 **promove o adjust split/dividend de caveat v1.1 para decisão v1
  obrigatória**, com `NotImplementedError` explícito para equity sem
  daily cache — impede re-introdução do bug `5ca9410` silenciosamente.

As 5 🟠 da v1 também foram endereçadas (slack per-(AC,freq) §2.4,
`date | datetime` §2.4, `requested_range` v1 §2.5, pgrep guard + backup
automático + lockfile §4, teste de rollback §6.1 passo 2). Escopo e
TDD-ordering continuam limpos.

Porém, sobraram **3 problemas novos ou persistentes** que valem uma
revisão cirúrgica antes do plan — nenhum deles é BLOCK, mas um deles
(formula de adjust §3.3) é sensível porque é citado como "canônica" e
contradiz a fonte citada. O outro (mismatch de citações em §1.4 e §2.4)
viola a Regra 2 inviolável do projeto. O terceiro é uma contradição
interna residual em §2.7 (diagrama) com §2.4 (código).

## Preocupações

### 🔴 Críticas (bloqueiam o prosseguimento)

Nenhuma. As duas 🔴 da v1 foram endereçadas de forma verificável.

### 🟠 Altas (devem mudar antes de prosseguir)

- **[§3.3 fórmula de split/dividend contradiz a citação
  `[quant_trading_chan, p.37]`].** O spec §3.3 escreve:

  ```
  adj_close_intraday[t] = close[t] × cumprod(splitFactor em [t, hoje])
                                - cumsum(divCash em [t, hoje] × splitFactor)
  ```

  e chama isso de **"fórmula canônica de total-return adjustment
  `[quant_trading_chan, p.37]`"**. Mas a fórmula de Chan p.37, verificada
  em `books/summaries/quant_trading_chan.md:93-100`, é **multiplier-based**,
  não subtractive:

  ```
  multiplier = (Close(T-1) - d) / Close(T-1)
  Apply the multiplier to all prices before T (do not subtract d, to preserve returns).
  ```

  O spec está **subtraindo o dividend** — exatamente o que Chan diz para
  NÃO fazer. O resultado numérico pode ainda ser aceitável dependendo
  do uso downstream (Ehlers BP oscilador em retornos, p.ex.), mas
  **(i) a citação contradiz o texto** e **(ii) a escolha subtractive
  quebra a invariante "preservar returns"** — o que é relevante para
  Sharpe-based gates no projeto.

  **Impacto:** se o plan implementar a fórmula literal do spec, os
  testes `test_iex_applies_split_adjust_from_daily_cache` e o Smoke #2
  vão validar algo diferente da semântica Chan. A estratégia Chan
  mean-reversion 1h (primeiro consumidor — §6.5 item 3) depende
  justamente dessa invariante em retornos para não sinalizar entradas
  artificiais em dias ex-dividend.

  **Sugestão:** reescrever §3.3 ponto 2 como:

  ```
  # Splits: cumprod multiplier aplicado aos preços pré-split (canônico Chan p.37)
  split_multiplier[t] = cumprod(1/splitFactor em (t, hoje])
  # Dividends: multiplier de Chan p.37, NÃO subtração
  div_multiplier[t]   = prod( (Close_pre_ex(T) - divCash) / Close_pre_ex(T)
                              para cada ex-date T > t )
  adj_close[t] = close[t] × split_multiplier[t] × div_multiplier[t]
  ```

  Ou, mais simples: **reusar o `adj_close` do daily cache diretamente**
  (fold intraday close dentro do daily wrapper via ratio `adj_close/close`
  do dia, como `adjust.py::adjust_ohlc` já faz para OHLC). Isso é
  semanticamente idêntico ao que `5ca9410` introduziu para daily e
  garante apples-to-apples por construção — sem re-implementar a
  fórmula de adjustment do zero. Trocar §3.3 ponto 2 para "ratio
  `daily[date(t)].adj_close / daily[date(t)].close` aplicado a cada
  bar 1h do mesmo dia" + adicionar 1 citação específica
  `[quant_trading_chan, p.37]` correta no docstring.

- **[Citações mal-atribuídas violam Regra 2 inviolável]**

  **(a) §1.4 cita `[systematic_trading, Carver — skew custo vs
  frequência, p.32-35]`** para motivar warning de `median_hold > 48h`.
  Mas `books/summaries/systematic_trading.md:37` mostra que p.32-35 é
  sobre **SKEW de distribuições de retorno** (positive-skew vs
  negative-skew), NÃO sobre "cost vs frequency skew". A citação correta
  seria **p.182-188 (ch.12)** — "standardised cost (SR units)" e
  "annual cost = std_cost × turnover", ou p.185 ("turnover — key
  speed metric for cost management"), ou p.271 ("holding period ×
  turnover trade-off"). A forma atual junta palavras de duas páginas
  diferentes do livro numa citação só, sem base no summary.

  **(b) §2.4 cita `[trading_exchanges, Harris, p.33-34]`** para motivar
  slack per-(asset_class, freq) com base em "taxonomia de sessões e
  24/7 vs 24/5". Mas `books/summaries/trading_exchanges.md:24-26`
  mostra que p.33-34 é sobre **price priority, time precedence e tick
  size em oral auctions** — nada sobre sessões 24/7 vs RTH vs 24/5.
  A pesquisa completa no summary (grep `24/7|24/5|session|RTH`)
  retorna zero matches — o summary não documenta uma taxonomia de
  sessões. Logo, a citação é inválida; a decisão §2.4 seria honesta
  como "**decisão empírica de engenharia — sem citação de livro** (o
  summary de Harris p.33-34 não cobre market hours; não há livro do
  knowledge base que recomende slacks numéricos)". Isso é explicitamente
  permitido pela Regra 2 com o marcador "decisão empírica" (e o spec
  já usa essa construção corretamente na linha 279-280: "slack numérico
  é decisão empírica de engenharia").

  **Impacto:** Regra 2 inviolável do projeto exige que toda citação
  seja verificável na fonte. Citações erradas **são piores que
  ausência de citação** porque parecem fundamentação quando são
  decoração. Isso calibra erroneamente a confiança de quem lê
  (árbitro, future-self, PR reviewer).

  **Sugestão:** corrigir §1.4 para `[systematic_trading, Carver,
  p.182-188, p.271 — turnover × cost × holding period]` ou N/A com
  justificativa. Corrigir §2.4 para remover a citação inválida e
  manter apenas "decisão empírica" como já feito em linha 279-280 —
  ou, melhor, citar o livro que *de fato* trata sessões (não identifiquei
  um no knowledge base; aceitável marcar N/A). §7.1 entry para
  `trading_exchanges` precisa ser ajustada ou removida.

- **[§2.7 contradiz §2.4 — constante `_COVERAGE_SLACK_BY_FREQ` vs
  `_COVERAGE_SLACK`]**. §2.4 (linha 232) define o novo design:

  ```python
  _COVERAGE_SLACK: dict[tuple[str, str], timedelta] = { ... }
  ```

  Mas §2.7 (linha 375) ainda documenta a constante velha do design v1:

  ```
  - _COVERAGE_SLACK_BY_FREQ: {daily: 7d, 1hour: 1d}
  ```

  **Impacto:** o componente diagram em §2.7 é referência primária durante
  a implementação. Quem estiver olhando §2.7 vai criar uma constante
  com nome e shape diferentes do que §2.4 descreve. Em code review
  isso vira "qual seção vale?"; TDD-first pode até cobrir isso
  (`test_slack_per_asset_class_and_freq` em §6.1 passo 3 força a shape
  correta), mas ainda é **inconsistência interna** que levanta dúvida
  sobre quais outras partes de §2.7 ficaram desatualizadas.

  **Sugestão:** em §2.7 linha 375, substituir por:

  ```
  - _COVERAGE_SLACK: dict[(asset_class, freq), timedelta]
    (ver §2.4 — 9 entries cobrindo equity/etf/index/crypto/forex × daily/1hour)
  ```

### 🟡 Médias (recomendado mudar)

- **[§6.2 banda 250-364d "escalar ao usuário"] Contradiz §1.3 que diz
  "retention < 12 meses = volta ao brainstorm".** §1.3 é binary: ≥12m
  = PROCEED, <12m = BLOCK-design. §6.2 introduz um middle-band 250-364d
  que "escala ao usuário" — ambíguo sobre o que o usuário faz com isso
  (é PROCEED condicional? é pergunta de texto livre?). Para um gate
  de DESIGN, ambiguidade no critério derrota o propósito do gate.
  **Sugestão:** decidir — ou o middle-band vira PROCEED (com adjust
  de escopo: "backtests limitados a N meses" documentado), ou vira
  BLOCK (consistent com §1.3). Recomendo BLOCK por conservadorismo.

- **[§3.3 afirma "se o projeto já tem `src/ai_trade/backtest/data/adjust.py`,
  reusar"]** — o projeto tem, via `5ca9410`, mas `adjust_ohlc` (verificado
  em `src/ai_trade/backtest/data/adjust.py:28-43`) **requer `adj_close`
  já presente no DataFrame** (linha 35: `if "adj_close" not in df.columns
  return df`). IEX intraday NÃO traz `adj_close`, então `adjust_ohlc`
  **não é** reutilizável como está. §3.3 sugere reuso que não funciona
  sem adaptação. **Sugestão:** explicitar que será criada uma nova
  função `compute_adj_close_from_daily(intraday_df, daily_df)` em
  `adjust.py` — não reuso direto. Tempo extra trivial (já orçado em
  §6.3 "source refactor + split adjust logic 150min").

- **[§1.3 e §6.2 expectativa de Cenário A vs §5.2 evidência pública]**
  — §5.2 + fontes públicas dizem retention IEX ≈ 83 dias em 1h (rolling
  2000 bars). 12 meses em 1h equity RTH = 252 × 6.5 = ~1638 bars < 2000
  (tight cabe), **mas** 12 meses em 1h crypto 24/7 = 365 × 24 = 8760
  bars >> 2000 (BLOCK garantido se cap rolling for igual para crypto).
  Logo o critério ≥ 12 meses **é quase certamente violado pra crypto
  já no Smoke #1**. O cenário A (§6.3 "spec executável conforme
  descrito") é o cenário **pouco provável**. §6.3 Cenário B deveria ser
  o default expected, não a exceção. Minor: é uma questão de framing,
  não de correctness — a v2 ACEITA esse risco corretamente via
  gate-de-design.
  **Sugestão:** inverter o framing em §6.3 para "Cenário B (mais
  provável segundo evidência pública): spec abortado, re-brainstorm em
  sessão nova" + "Cenário A (aspiracional): ..."; setar expectativa de
  que a sessão pode terminar pós-Smoke #1.

- **[§3.3 ponto 4 `NotImplementedError` vs "--skip-adjust flag"
  pré-autorizado]** — a mensagem sugere "pré-autorize via flag
  `--skip-adjust`" mas esse flag não está definido em §3.5 (interface
  de `TiingoSource.fetch` não inclui `skip_adjust`). Flag fantasma.
  **Sugestão:** ou definir o flag explicitamente na assinatura do
  `TiingoSource.fetch` (kwarg `skip_adjust: bool = False`), ou remover
  a menção. Ou mais radical: fazer a mensagem apontar "baixe o daily
  primeiro com `tiingo_bulk_download` — por que não há flag de escape".

### 🟢 Baixas (opcional)

- **[§5.6 texto redundante com §3.3]** — §5.6 na v2 é basicamente "ver
  §3.3". Nada errado, mas caveat table fica inflada com items que já
  são decisões-v1, não caveats. Mover §5.6 para §5.3 ou consolidar.

- **[§6.1 passo 8 commit split em 3]** — ótimo, mas os 3 titles
  propostos misturam escopo. O #1 "add frequency axis + migrate script"
  combina refactor de storage + script novo; o #2 combina source
  refactor + split adjust + smoke; o #3 é quase só docs. Sugestão:
  `(1) feat(data): add frequency axis to tiingo storage`,
  `(2) feat(data): tiingo_migrate script + automated backup`,
  `(3) feat(data): route tiingo source to IEX for 1h + split adjust`,
  `(4) chore(data): smoke intraday + docs update`. 4 commits cada
  reversível em ~200 linhas.

- **[§7.1 entry `[advances_fin_ml, López de Prado, ch.3]`]** — cita
  "ch.3 (data structures para ML financeiro)" mas a citação não
  adiciona valor específico ao §3.3 — serve apenas como "AFML também
  fala sobre ajuste de splits como propriedade fundamental". O summary
  do livro (grep em `advances_fin_ml.md`) mostra ch.3 é sobre
  triple-barrier labeling e meta-labeling, NÃO dollar bars (esses
  ficam em ch.2 / p.57-62). Ou remover a linha, ou corrigir para
  `[advances_fin_ml, p.57-62, ch.2]`.

- **[§1.4 "gate de descarte (futuro): median_hold > 72h em 1h"]** — 72h
  em 1h = 72 bars, que é razoável, mas "72h" expresso em horas vs "48h"
  warning threshold vs 6.5h/dia RTH... a unidade é consistente em
  horas absolutas de calendário (não bars, não RTH hours). Documentar
  no parágrafo qual é a unidade para evitar ambiguidade.

## Pontos fortes

- **As 2 🔴 da v1 foram efetivamente resolvidas**, não apenas maquiadas.
  §1.3 Pré-condição inviolável + §6.2 critério ≥365d explícito dão
  teeth reais ao gate de design. §3.3 promoveu adj a requisito e
  proíbe fallback silencioso via `NotImplementedError`.
- **As 5 🟠 da v1 foram endereçadas com implementação concreta**, não
  "v2 futuro": slack per-(AC,freq) em §2.4, `date | datetime` em
  §2.4, `requested_range` no manifest v1 em §2.5, pgrep guard +
  backup auto + lockfile em §4, teste rollback em §6.1 passo 2.
- **Novas seções (§1.4 holding-period, §3.3 adj, §2.4 slack, §6.6
  unblock path) estão bem fundamentadas**, com citações a livros do
  knowledge base — a intenção de cumprir Regra 2 é visível (embora
  algumas citações estejam mal-atribuídas, como apontado).
- **§6.6 Unblock path** (novo em v2) é exatamente a dobradura correta
  para evitar que o layout α "prenda o projeto em 1h" — preocupação
  explícita da primeira rodada de juízes.
- **TDD-first ordering continua exemplar** — 11 testes novos em
  `test_tiingo_migrate.py`, 9 em storage, 8 em source, sempre antes
  da implementação.
- **Test de rollback (`test_migration_rollback_restores_layout`) agora
  existe**, cobrindo a lacuna crítica da v1 que fazia o rollback ser
  executado pela primeira vez em prod.
- **§8 Status changelog é honesto e rastreável** — lista 12 mudanças
  materiais com seção afetada, facilita auditoria v1→v2 (boa prática
  de spec evolution).

## Sugestões concretas

1. **§3.3 ponto 2 — reescrever a fórmula** para usar a abordagem
   multiplier de Chan p.37, OU (preferencial) trocar por "ratio
   `adj_close/close` do daily cache aplicado a cada bar intraday do
   mesmo dia", reusando a semântica de `adjust_ohlc` de `5ca9410`.
   Justificativa: a fórmula atual contradiz a própria citação canônica;
   Chan diz explicitamente "do not subtract d, to preserve returns".

2. **§1.4 — corrigir citação Carver** de `p.32-35 (skew custo vs
   frequência)` para `p.182-188, p.271 (turnover × cost × holding
   period)`. Ou marcar como N/A com "decisão de diagnóstico; sem
   página de livro específica". Justificativa: Regra 2 inviolável
   exige verificabilidade — p.32-35 é sobre skew, não cost vs frequency.

3. **§2.4 + §7.1 — remover ou corrigir citação `trading_exchanges,
   Harris, p.33-34`**. O summary não documenta taxonomia de sessões
   nessa página. Substituir por "decisão empírica de engenharia"
   (já é feito corretamente em linha 279-280 do mesmo spec — replicar
   a sinceridade) ou achar fonte correta e citar com página exata.
   Justificativa: Regra 2 inviolável.

4. **§2.7 linha 375 — atualizar diagrama para refletir §2.4.**
   Substituir `_COVERAGE_SLACK_BY_FREQ: {daily: 7d, 1hour: 1d}` por
   `_COVERAGE_SLACK: dict[(asset_class, freq), timedelta]` com
   referência a §2.4. Justificativa: inconsistência interna entre
   §2.4 (código) e §2.7 (diagrama) confunde implementação.

5. **§6.2 — resolver o middle-band 250-364d** para ser binary
   (consistente com §1.3). Sugestão: BLOCK conservador para <365d
   em qualquer dos 3 tickers; se usuário quiser escalar, é override
   manual fora do script. Justificativa: gate binário é gate — middle
   band ambíguo derrota o propósito.

6. **§3.3 ponto 4 — definir ou remover `--skip-adjust` flag.**
   Atualmente é flag fantasma na mensagem de `NotImplementedError`.
   Justificativa: a mensagem orienta o user a algo que não existe.

7. **§6.3 — inverter framing Cenário A/B.** Cenário B (spec abortado)
   é o mais provável dado retention pública ~83d vs critério ≥365d.
   Justificativa: calibra expectativa do usuário antes de começar a
   sessão (ele precisa saber que pode ter só 1h de smoke + 30min de
   postmortem, não 8-9h de refactor).

8. **§6.1 passo 8 — splitar em 4 commits** em vez de 3, separando
   `tiingo_migrate.py` (infra de uma-só-vez) do refactor de storage
   (mudança recorrente de API). Justificativa: migrate script é
   single-shot; storage é API pública. Escopos diferentes, revisões
   diferentes.

## Evidência externa consultada

### Arquivos do projeto
- `/var/www/pessoal/ai-trade/docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md` — spec v2 em revisão (1001 linhas).
- `/var/www/pessoal/ai-trade/reports/spec-judges/2026-04-15-tiingo-service-lazy-cache-design-20260415-170020/methodology.md` — meu relatório v1 (baseline para checar resolução).
- `/var/www/pessoal/ai-trade/.claude/CLAUDE.md` — Regra 2 inviolável (citação com `[book.slug, p.X]`).
- `/var/www/pessoal/ai-trade/books/summaries/quant_trading_chan.md:93-100` — verifica formula canônica p.37 é multiplier, NÃO subtractive. Contradição com §3.3 do spec.
- `/var/www/pessoal/ai-trade/books/summaries/algo_trading_chan.md:19,22,304` — verifica citações §2.6 (p.4 look-ahead bias, p.10-11 IEX primary vs consolidated) — corretas.
- `/var/www/pessoal/ai-trade/books/summaries/trading_systems_methods.md:452-453` — verifica citação Kaufman p.914 — correta.
- `/var/www/pessoal/ai-trade/books/summaries/ml_for_algo_trading.md:22,379-380` — verifica ch.8 p.223-224 (look-ahead + retroactive splits) — correta.
- `/var/www/pessoal/ai-trade/books/summaries/advances_fin_ml.md:20-22` — verifica dollar bars / TIBs em p.57-62 (§6.4 cita p.59-62 correto; §7.1 entry `ch.3` é mis-attributed a ch.2).
- `/var/www/pessoal/ai-trade/books/summaries/systematic_trading.md:37` — p.32-35 em Carver é **skew de distribuições**, NÃO "skew custo vs frequência". Citação §1.4 mal-atribuída.
- `/var/www/pessoal/ai-trade/books/summaries/trading_exchanges.md:24-26` — p.33-34 em Harris é **price priority + time precedence + tick size**, NÃO taxonomia de sessões 24/7 vs 24/5. Citação §2.4 + §7.1 mal-atribuída.
- `/var/www/pessoal/ai-trade/src/ai_trade/backtest/data/adjust.py:28-43` — `adjust_ohlc` requer `adj_close` já presente; não reutilizável diretamente para IEX intraday sem wrapper novo (§3.3 sugestão de reuso é incompleta).
- `/var/www/pessoal/ai-trade/scripts/tiingo_bulk_download.py:278` — confirma call-site do bulk (`storage.has(ticker, args.start, args.end)` sem `frequency`) — backwards-compat do spec válida.
- `/var/www/pessoal/ai-trade/scripts/tiingo_backup.py` — existe no repo (referenciado em §3.5 / §4.3 via `--skip-backup` é real, não vaporware).
- Commit `5ca9410` (`fix(strategies): use total-return adjusted OHLC`) — verificado existir; mensagem documenta fix para splits e dividends, motivação do §3.3.

### Web
- [riingo reference](https://business-science.github.io/riingo/reference/riingo_iex_prices.html) — "returns the most recent 2000 ticks of data at the specified frequency" (já citado em v1; spec v2 agora cita em §5.2 e §1.3).
- [QuantStart Tiingo review](https://www.quantstart.com/articles/evaluating-data-coverage-with-tiingo/) — 2000 rolling, histórico 1min desde 2016 (já citado em v1; spec v2 cita em §5.2).
- [Tiingo IEX docs](https://www.tiingo.com/documentation/iex) — URL oficial incluída pela v2 (atendendo 🟢 da v1).

## Veredito

**PROCEED-WITH-CHANGES**

**Regra aplicada:**
- PROCEED = zero preocupação 🔴 ou 🟠.
- PROCEED-WITH-CHANGES = zero 🔴, pelo menos uma 🟠.
- BLOCK = pelo menos uma 🔴.

Preocupações 🟠 dominantes: (1) §3.3 fórmula de adjust subtraí dividends
enquanto cita Chan p.37 que exige multiplier — rework pequeno mas
necessário; (2) §1.4 e §2.4 têm citações mal-atribuídas ao knowledge
base, violando Regra 2 inviolável; (3) §2.7 diagrama contradiz §2.4
nova constante de slack. Zero BLOCK: as duas 🔴 da v1 (retention IEX +
adj_close bug) foram endereçadas de forma verificável — Smoke #1 como
gate de DESIGN com critério quantitativo ≥365d, e adj split/dividend
promovido a requisito v1 com `NotImplementedError` se daily cache
ausente. Os 🟠 restantes são cirúrgicos (~5-10 linhas de edit) e não
mudam a forma nem o escopo do spec.
