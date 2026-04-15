# Juiz Adversarial — Fidelidade Estratégica (Rodada 2, spec v2)

**Spec:** `docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md` (v2)
**Data:** 2026-04-15 17:30
**Veredito:** PROCEED-WITH-CHANGES
**Juiz anterior (v1):** PROCEED-WITH-CHANGES (este mesmo juiz, o menos rigoroso da v1)

---

## Resumo executivo

A v2 endereça **genuinamente** as 3 preocupações 🟠 que escrevi na v1 — §1.4
holding-period hook foi adicionado como nova seção, §2.5 retention foi
corrigida de "tipicamente 2a" para "~2000 bars rolling" com o Smoke #1
como **gate de DESIGN** (não só de execução), e o slack virou per-
`(asset_class, frequency)` com valores empiricamente justificados. Além
disso, a v2 **excedeu meu escopo** ao corrigir dois problemas que os
outros juízes acharam (retention corrigido com URLs verificáveis; split-
adjust via daily cache em lugar de `adj_close := close` que re-
introduziria o bug `5ca9410`). As 10 citações novas de livros são
todas verificáveis em `books/summaries/` (confirmei 7 delas diretamente).
**Porém** três riscos remanescentes justificam PROCEED-WITH-CHANGES e
não PROCEED: (i) a nova §3.3 de split-adjust reinventa roda que já existe
em `src/ai_trade/backtest/data/adjust.py` (commit `5ca9410`) e o spec não
cita o módulo; (ii) o threshold "retention ≥ 12 meses" do Smoke #1 é
defensável mas o spec apresenta como número empírico sem derivar do caso
de uso limitante (Chan pairs half-life + CPCV N_splits=6); (iii) §6.5
item 4 admite que cancelar a subscrição Tiingo pode ser inviável para
intraday — isto contraria explicitamente o "Next steps" item 5 do
ROADMAP e o spec deveria escalar mais alto do que um bullet.

---

## Alinhamento com o pivô

| Aspecto | Spec v2 respeita? | Evidência |
|---|---|---|
| Habilita/preserva intraday | **Sim** | §2.6 roteamento IEX+resampleFreq; §2.3 layout `{freq}/prices`; v1 scope `{daily, 1hour}` disciplina MVP. |
| Não gera swap risk adicional | **Sim** | Infra neutra; §6.5 item 4 agora reconhece que retention curta pode forçar API sempre viva (nota sobre swap Pepperstone não aplicável). |
| Permite medir holding period | **Sim** (agora) | §1.4 nova documenta `entry_time`/`exit_time` em `engine/portfolio.py:61-62`; obriga `median_hold_hours`/`max_hold_hours` no diagnostic. Exatamente o guard-rail que pedi na v1. |
| Compatível com cTrader future | **Parcial** | §2.6 layout ainda encaixa em M1/M5/H1/D1. **Mas:** cTrader `ProtoOAGetTrendbarsReq` retorna price×100000 SEM adjust embutido (fonte: `community.ctrader.com`), então o módulo de split-adjust do spec vira ativo útil em Phase 4 — não débito. Precisa ser dito. |
| Gates anti-overfit intocados | **Sim** | Infra não toca CPCV/PBO/DSR/WF; N_trials é das estratégias consumidoras. |
| Fidelidade ao livro-regra | **Sim** | 10 citações novas, 7 verificadas (confirmei `[systematic_trading p.32-35 skew]`, `[trading_systems_methods p.914]`, `[quant_trading_chan p.37]`, `[algo_trading_chan p.4/p.10-11/p.94]`, `[trading_exchanges p.33-34]`, `[ml_for_algo_trading ch.2/ch.8]`). Regra 2 respeitada. |

---

## Verificação das preocupações v1 → v2

| v1 | Status v2 | Evidência em v2 |
|---|---|---|
| 🟠 Holding-period hook ausente | **Resolvido** | §1.4 nova (linhas 97-121) cita `engine/portfolio.py:61-62`; define alerta `median_hold > 48h`; define gate-de-descarte `median_hold > 72h`. "Não enforçado neste spec" é legítimo (infra de dados ≠ infra de estratégia). |
| 🟠 Retention "2a" sem evidência | **Resolvido com gate** | §5.2 corrigido com 3 URLs; §1.3 condicionado ao Smoke #1; §6.1 passo 1 é gate de DESIGN com critério quantitativo ≥ 12 meses; §6.3 cenário B (spec abortado em ~1h) é plano real de pivot. |
| 🟠 Slack per-AC ausente | **Resolvido** | §2.4 linhas 232-244: dict per-`(asset_class, freq)` com forex 48h/crypto 6h/equity 12h justificados por market hours `[trading_exchanges, Harris, p.33-34]`. |
| 🟡 Backup manual | **Resolvido** | §4.3 item 2 `skip_backup=False` default; §3.5 `run_tiingo_migrate.py` roda `tiingo_backup.py` como primeiro passo. |
| 🟡 Migração interrompível | **Resolvido** | §4.1 passo 5 adiciona lockfile `.migration.lock`; teste `test_lockfile_blocks_concurrent_storage_init` em §6.1 passo 2. |
| 🟡 URL IEX não verificada | **Resolvido com disclaimer** | §2.6 com nota explícita "premissa, não fato confirmado — Smoke #1 valida"; §5.1 go/no-go 404 revisita spec. |
| 🟢 Unblock path 5m/1min | **Resolvido** | §6.6 nova (linhas 874-903) com 3-4 passos concretos + regra prática "slack < 2 × bar_size". |

**Veredito sub-seção:** **todas as minhas 7 preocupações v1 foram
endereçadas materialmente**, não maquiadas. Não detectei regressões nas
novas seções contra outras.

---

## Preferências recentes do usuário que este spec respeita/viola

1. **Preocupação com swap Pepperstone** (reafirmada múltiplas vezes
   inclusive no `gh` do contexto desta rodada) → §1.4 agora torna
   explícito o mecanismo de enforcement. **Respeita**. O texto "nova
   regra de catálogo pós-pivô: todo diagnostic de estratégia intraday
   DEVE reportar `median_hold_hours`" é exatamente o guard-rail que
   previne repetir o erro do pivô em 1h/5m.
2. **Escolheu Q6-C (todos 3 asset classes em 1h)** → §2.6 + §2.4 tratam
   equity/crypto/forex como cidadãos first-class em v1. **Respeita**.
3. **Rejeitou "Smoke direto" em favor de "re-judge"** no último turno →
   mostra preferência por **validação adversarial antes de ação**. §6.1
   passo 1 (Smoke #1 como gate de DESIGN) + threshold ≥ 12 meses +
   Cenário B explicitado em §6.3 alinha com este instinto. O spec, se
   rodar Smoke #1 e o Smoke retornar retention curta, tem um plano
   **real** de voltar ao brainstorm. **Respeita a preferência por rigor
   em vez de optimism.**
4. **Usuário explicitou preocupação com custos em ciclos `/judge-spec`** — implícito no fato
   de ter escolhido re-judge (que custa tokens) em vez de Smoke direto.
   Isto sugere que o custo é aceito como seguro contra BLOCK tardio. O
   spec v2, por ter endereçado 12 mudanças dos 3 juízes, é justamente o
   retorno deste investimento. **Respeita.**

---

## Preocupações

### 🔴 Críticas (bloqueiam)

**Nenhuma crítica bloqueante nesta rodada.** A v1 não teve crítica e a
v2 remedeia todas as 🟠. O spec, implementado conforme descrito,
**move o projeto em direção ao pivô** (intraday short-hold Pepperstone)
sem introduzir atalhos multi-day escondidos.

### 🟠 Altas (dívida técnica significativa — remediar ANTES do plan)

1. **§3.3 reinventa `adjust.py` em vez de reusar.** O módulo
   `src/ai_trade/backtest/data/adjust.py` (criado no commit `5ca9410`,
   17 linhas + docstring) já implementa split/dividend adjustment via
   **approach ratio**:
   ```
   ratio = adj_close / close
   open, high, low, close = (o, h, l, c) * ratio
   ```
   A v2 §3.3 propõe re-derivar isto via `splitFactor`/`divCash` cumulado.
   Matematicamente equivalente, mas o spec **não cita `adjust.py` nem
   discute por que escolher approach `splitFactor`/`divCash` em vez do
   existente**. Problemas:
   - Se o daily cache tem `adj_close` populado (que é o caso após
     `5ca9410` — confirmei no `tiingo_source.py:72`), então o **approach
     ratio é mais simples**: lookup `adj_close/close` no bar diário
     do mesmo dia → multiplica OHLC intraday pelo ratio.
   - `divCash` no Tiingo EOD é o dividendo em $; o approach do spec v2
     re-subtrai dividendos (eq. `cumsum(divCash × splitFactor)`) o que
     é complementar ao split-factor. Se houver qualquer erro de sinal
     ou acumulação, os backtests silenciosamente divergem do daily.
   - **Recomendação:** §3.3 deve citar `adjust.py` explicitamente e
     escolher entre (a) **reusar `apply_ratio(daily_adj_close, daily_close,
     intraday_ohlc)`** ou (b) justificar por que reescrever. Se (b),
     um teste de equivalência com `adjust.py` é obrigatório.
   - **Impacto no pivô:** baixo se implementado corretamente. Alto se
     a aritmética divergir silenciosamente do daily (introduziria
     baseline drift entre `spec-phase2.5 daily` e `spec-tiingo_service 1h`).

2. **Threshold "retention ≥ 12 meses" não derivado do caso de uso.**
   §6.2 gate `observed_retention_days ≥ 365` para os 3 tickers é
   número redondo sem cadeia de derivação. Verifiquei empiricamente:
   - **Chan pairs (USD.CAD)** half-life = 115 dias daily
     `[algo_trading_chan, p.47-48, ch.2]`. Em 1h = 115 × 6.5 = ~748
     bars. Lookback recomendado = "small multiple of half-life" = 2-3×
     half-life = 1500-2200 bars. **Chan sozinho pede ~12-18 meses de
     retention em 1h (assumindo RTH only).**
   - **Chan buy-on-gap** usa lookback fixo 90 dias em daily
     `[algo_trading_chan, p.94, ch.4]`. Em 1h = 90 × 6.5 = 585 bars
     — cobre em ~5 meses.
   - **CPCV N_splits=6 + test_size=2** `[advances_fin_ml, p.163-165]`
     requer ~6× minimum usable sample → se base é ~750 bars, total =
     ~4500 bars = ~700 trading days = **~33 meses calendário**. 12
     meses é **insuficiente** para CPCV/PBO sério em Chan 1h.
   - **Vol breakouts / Ehlers 1h** consomem mais bars que Chan
     buy-on-gap porque Ehlers roofing filter precisa de ~2-3 ciclos
     completos para warmup.
   - **Tiingo IEX "83 days" ambíguo:** o cálculo `2000/24 = 83d` assume
     24h calendar; se for RTH-only (6.5h), é 2000/6.5 = 307 trading
     days ≈ 17 calendar months. **O spec precisa probe-ar isto** —
     Smoke #1 resolve empiricamente mas o spec não explicita que é
     esta a incerteza de primeira ordem.
   - **Recomendação:** §6.2 deve explicitar a derivação — "≥ 12 meses
     OK para Chan buy-on-gap-style (90d lookback) + vol breakouts mas
     **insuficiente** para cointegration pairs com CPCV N_splits=6 +
     purge. Se Smoke #1 der retention entre 12-24 meses, o spec não
     quebra mas a **escolha de primeira estratégia consumidora** é
     forçada a Chan buy-on-gap / vol breakouts — cointegration pairs
     ficam em lista de espera para v2". Neste momento, o ROADMAP §33 e
     o JORNADA §"próximo" listam Chan pairs como prioridade 1 —
     descompasso.

3. **§6.5 item 4 contradiz o ROADMAP "Next steps" item 5.**
   ROADMAP L38: *"**Cancel Tiingo subscription** — pushed out until
   `tiingo_service` is verified working against live endpoints (can't
   evaluate without fresh intraday data)."* Ou seja: a narrativa do
   ROADMAP era "cancela depois de verificar". A v2 §6.5 item 4 agora
   diz: *"Se retention curta (~83 dias rolling): subscrição **não
   pode** ser cancelada enquanto intraday for parte do catálogo."*
   Isto é **escalação de escopo não declarada em JORNADA**:
   - O usuário pode ter premissas financeiras para cancelar
     (subscrição é ~$50/mês Basic, $30/mês IEX). Mantê-la para
     intraday cria custo recorrente.
   - Alternativamente, "scheduled daily-append via cron" (mencionado
     em §6.4 fora-de-escopo) **poderia** viabilizar cancelamento, mas
     §6.5 não aponta para essa rota.
   - **Recomendação:** §6.5 item 4 deve:
     - Listar explicitamente as 3 rotas: (a) manter subscrição
       (atrito financeiro), (b) pré-download bulk intraday exhaustivo
       e cancelar (atrito de janela de oportunidade 12-17 meses
       somente), (c) scheduled daily-append via cron com subscrição
       mantida (híbrido).
     - Escalar ao usuário: "decisão financeira sobre subscrição Tiingo
       deve ser tomada **após Smoke #1** em vez de deferred". Isto é
       decisão de produto, não de infra — juiz estratégico deve flagar.
   - **Impacto no pivô:** médio. Não bloqueia intraday short-hold, mas
     pode bloquear a lógica de "bulk download only, no live API" que
     o usuário assumia desde pré-pivô.

### 🟡 Médias (risco gerenciável)

4. **Split adjust via daily cache cria dependência implícita na ordem
   de download.** §3.3 passo 4 diz: "Se é equity/etf e o daily cache
   não tem o ticker: `NotImplementedError`". Isto força o fluxo:
   - Passo 1: baixar daily (já feito para 1660 tickers).
   - Passo 2: baixar intraday via `tiingo_service`.

   **Problema:** uma estratégia futura quer rodar em ticker NOVO (ex.:
   IPO 2026, universo expandido) — ou em asset class nova (ex.:
   commodities via ETF, nova granularidade). O erro vai pipocar durante
   refactor de estratégia, não durante infra. Não é bloqueante mas
   precisa de test `test_iex_raises_notimplemented_if_equity_not_in_
   daily_cache_with_clear_error_message` que verifica que a mensagem
   de erro aponta para "rode `scripts/tiingo_bulk_download.py --ticker
   X` primeiro". **Está listado em §6.1 passo 4 — bom. Só preciso
   confirmar que a mensagem é acionável.**

5. **Spec v2 passou de ~17KB para ~40KB (mais que dobrou).** Risco de
   fadiga de leitor: o engenheiro que for executar o plan pode pular
   seções densas. Nota que §2.4 agora tem 11 tuplas em dict, §3.3 tem
   5 citações novas, §5.2 tem 3 URLs. Isto é *melhoria* em rigor, mas
   **sugiro** um TL;DR de 10 linhas no topo da §1 (ou logo depois do
   header) para leitor de fim-de-semana. Baixa prioridade.

6. **`_COVERAGE_SLACK[(forex, 1hour)] = 48h`** cobre weekend mas não
   cobre **holidays regionais forex** (ex.: New Year's Day nos feeds
   US+UK+AU ao mesmo tempo = gap de 72h). Pepperstone cTrader marca
   candles de holiday como ausentes — §2.4 não aborda. Provavelmente
   `pandas_market_calendars` é a rota certa (§6.4 lista como fora-de-
   escopo). Aceitável para v1; documente como caveat.

### 🟢 Baixas (observação de futuro)

7. **`logs/tiingo.log` como append-only global** (§4.1 passo 7) é boa
   prática mas §6.1 passo 1 e passo 8 geram linhas diferentes —
   sem schema, é difícil pós-processar. Se o smoke#1 retornar 3
   tickers × 3 resultados (first_dt/last_dt/retention), um JSON
   Lines em `logs/tiingo-smoke-1.jsonl` é mais útil que texto livre
   em `tiingo.log`.

8. **cTrader Open API retorna price × 100000 relative format.** O
   split-adjust do spec v2 é **asset** para Phase 4/5, não débito —
   cTrader **não** ajusta bars historicamente [source:
   community.ctrader.com forum]. A mesma lógica de
   `ratio = adj_close / close` serve para cTrader se o daily cache
   do Tiingo permanecer como source of truth para dividendos/splits.
   **Recomendação ao spec v2:** adicionar uma nota em §2.7 ou §6.5:
   "Este módulo de split-adjust **é reutilizável em Phase 4 (cTrader
   paper)** porque cTrader `ProtoOAGetTrendbarsReq` retorna
   price×100000 raw sem adjustment embutido. Daily cache Tiingo vira
   source of truth para corporate actions, mesmo após cancelamento
   de subscrição intraday (daily é storage-only pós-download)."

---

## Pontos fortes (estratégia)

1. **Smoke #1 como gate de DESIGN** (não só de execução) é o
   critério mais importante do spec v2. Se o retention for curto, o
   spec aborta antes de qualquer refactor. **Isto é o que a v1 não
   tinha e é o que torna a v2 adversarially honest.**

2. **§1.4 obriga instrumentação de holding-period** de toda estratégia
   intraday futura. Exatamente o que pedi na v1, exatamente como a
   literatura recomenda `[systematic_trading, Carver, p.32-35 skew
   custo vs frequência]`.

3. **Slack per-`(asset_class, freq)`** resolve estruturalmente o gap
   que apontei — crypto/forex/equity têm market hours fundamentalmente
   diferentes e o spec trata como cidadãos first-class.

4. **Split-adjust via daily cache é o right-thing-to-do** —
   re-introduzir o bug `5ca9410` em 1h teria sido desastre silencioso
   (Sharpe NVDA inflado 150%+). A v2 corrige o último juiz v1 aqui.

5. **Commit split em 3** (§6.1 passo 8) é pragmático — facilita
   revisão + reverts isolados. Corrige feedback do juiz methodology v1.

6. **Migration guardrails** — pgrep + backup auto + lockfile — é
   overkill de uma operação irreversível (1660 parquets, ~145 MB).
   **Com 1660 arquivos de trabalho de 2 dias atrás, overkill é o
   defeito certo.**

---

## Sugestões concretas

1. **§3.3 — Reusar `adjust.py` explicitamente.** Reescrever primeira
   linha de §3.3 como: *"`src/ai_trade/backtest/data/adjust.py` (commit
   `5ca9410`) já implementa approach ratio `(adj_close / close)` para
   daily. Para 1h, re-aplicar o MESMO módulo: o daily cache contém
   `adj_close`; lookup o ratio do bar diário do mesmo dia e multiplica
   o OHLC intraday."* Então os pontos 1-4 de §3.3 ficam corretos mas
   **a equação é o ratio, não `splitFactor`/`divCash` re-derivado**.
   Adicionar em §3.1 linha `adjust.py` → "sem mudança — reusado".
   **Motivação:** zero divergência entre daily e intraday baseline;
   1 fonte de verdade para corporate actions.

2. **§6.2 — Derivar threshold 12 meses do caso de uso.** Reescrever
   como:

   ```
   Gate: retention observada em 1h:
   - Caso-limite MÍNIMO (Chan buy-on-gap 90d lookback): ≥ 90 trading
     days = ~4.5 calendar months. PASS bloqueia bots-de-brinquedo.
   - Caso-limite LITERATURA (Chan pairs half-life 115d + CPCV N=6 +
     purge): ≥ 3 calendar years. IMPRATICÁVEL em Tiingo IEX.
   - Gate escolhido: ≥ 12 calendar months — viabiliza Chan buy-on-gap,
     Ehlers BP 1h, vol breakouts. Se observed < 12m: BLOCK.
   - Se observed entre 12-24 meses: PROCEED mas deferir cointegration
     pairs (§6.5 reorder: buy-on-gap primeiro, pairs em v2).
   ```

   **Motivação:** o threshold ganha auditabilidade e explicita qual
   estratégia é desbloqueada ou não.

3. **§6.5 item 4 — Escalar decisão financeira ao usuário.** Adicionar
   ao fim: *"**Decisão do usuário pós-Smoke #1:** (a) manter subscrição
   (~$X/mês) para intraday reactive; (b) bulk-download window inteiro
   de intraday e cancelar; (c) scheduled daily-append cron + subscrição
   mantida. ROADMAP item 5 `Cancel Tiingo subscription` depende desta
   decisão, não é fail-safe pós-entrega deste infra."* **Motivação:**
   juiz estratégico escala escopo financeiro que o spec esconde.

4. **§6.1 passo 1 + §6.2 — Smoke #1 grava JSON Lines, não texto livre.**
   Reescrever logo de smoke como:
   ```
   logs/tiingo-smoke-1.jsonl
   {"ticker":"SPY","ac":"equity","freq":"1hour","observed_first_dt":
    "2025-04-15T13:30","observed_last_dt":"2026-04-15T20:00",
    "observed_bars":1650,"observed_days":365}
   ```
   **Motivação:** smoke é gate crítico; dados estruturados facilitam
   decisão e pós-processamento.

5. **§2.7 — Adicionar nota cTrader.** Adicionar após o diagrama:
   *"Este módulo de split-adjust é reutilizável em Phase 4 (cTrader
   paper): `ProtoOAGetTrendbarsReq` retorna price × 100000 raw, sem
   ajuste de corporate actions. Daily cache Tiingo vira source of
   truth para splits/dividendos mesmo após cancelamento de subscrição
   intraday."* **Motivação:** dívida técnica positiva — o spec prepara
   Phase 4 em vez de criar atrito.

---

## Evidência consultada

### Artefatos do projeto

- `JORNADA.md` L32-72, L106-141 — contexto do pivô e "Onde estamos
  hoje"; §"O que vem a seguir" item 1 = `tiingo_service`.
- `ROADMAP.md` L25-40 — Current status + "Next steps" item 5
  (*Cancel Tiingo subscription*) — contrasta com §6.5 item 4 do spec.
- `src/ai_trade/backtest/data/adjust.py` (17 linhas + docstring) —
  approach ratio `(adj_close / close)` já implementado; spec §3.3
  **não cita nem discute reuso**. Confirma preocupação 🟠 #1.
- `src/ai_trade/backtest/engine/portfolio.py:61-62,74,111,151-152,159`
  — `entry_time`/`exit_time` persistidos como `pd.Timestamp`. Infra
  de holding-period existe; §1.4 v2 agora conecta ao gate.
- `books/summaries/systematic_trading.md` L37 + L50 — `[p.32-35]`
  Skew + Sharpe; verifica citação da §1.4.
- `books/summaries/trading_systems_methods.md` L452-453 — `[p.914]`
  "split-adjusted stocks lose volatility characteristics"; verifica
  §3.3.
- `books/summaries/quant_trading_chan.md` L93-100 — `[p.37]` fórmula
  split/dividend multiplier; verifica §3.3.
- `books/summaries/trading_exchanges.md` L24-34 — `[p.33-34]` price
  priority + tick size; **dúvida:** o spec v2 cita "taxonomia de
  sessões e 24/7 vs 24/5" `[p.33-34]`, mas as páginas citadas falam
  de price priority/tick. Pode estar errada a citação — verificar
  com o usuário se há outra página específica para market hours
  taxonomia no Harris. **Citação possivelmente imprecisa** mas
  conceito correto (24/7 vs RTH é real).
- `books/summaries/algo_trading_chan.md` L168-190, L277, L339, L26-
  28, L47 — todas as páginas citadas em §3.3 + §2.6 + §1.4 verificam.
- `books/summaries/ml_for_algo_trading.md` L35, L223-224, L353-368 —
  dollar bars, look-ahead splits; verifica §3.3 + §6.4.
- `scripts/tiingo_backup.py`, `scripts/tiingo_bulk_download.py`,
  `scripts/tiingo_smoke.py` — existentes; confirmam §3.5 e §4.
- `data/tiingo/manifest.json` 281KB — manifest flat atual; migração
  descrita em §4.1 é mecânica.

### Fontes externas

- [Tiingo IEX docs via riingo](https://business-science.github.io/riingo/reference/riingo_iex_prices.html) —
  confirmou "2000 ticks most recent" rolling; ambíguo se RTH-only ou
  24h; `after_hours` é opt-in. **Suporta conclusão:** "~83 dias" é
  pessimistic-end; realidade pode ser 307 trading days (~17 meses)
  com RTH-only contagem.
- [cTrader Open API — ProtoOAGetTrendbarsReq](https://help.ctrader.com/open-api/symbol-data/) —
  14000 bar hard limit; **price × 100000 sem adjustment embutido** —
  **cTrader NÃO faz split-adjust**. Reforça preocupação 🟢 #8 (asset,
  não débito).
- [Pepperstone Pricing](https://pepperstone.com/en/ways-to-trade/pricing/)
  (via v1 deste juiz) — swap overnight 22h UTC confirma urgência do
  pivô. Spec v2 continua neutro mas §1.4 agora tem o gate.

---

## Veredito

**PROCEED-WITH-CHANGES**

**Regra aplicada:**
- **Zero 🔴.** Infra é genuinamente neutra ao pivô; §1.4 virou agora
  um guard-rail ativo.
- **3 🟠 remediáveis antes do plan:** (a) §3.3 cita e reusa
  `adjust.py`; (b) §6.2 threshold 12 meses derivado do caso de uso
  Chan; (c) §6.5 item 4 escala decisão financeira sobre subscrição.
- **Comparado com v1:** das minhas 7 preocupações v1, 7 foram
  materialmente endereçadas. Estou mais rigoroso desta vez (juiz
  estratégico deve ser — v1 fui o mais leve; v2 busco rigor).

**Principal vetor estratégico:** o spec v2 **move o projeto em direção
ao pivô declarado** mais fortemente que v1. A infra habilita intraday
sem atalho multi-day, §1.4 conecta `entry_time`/`exit_time` ao gate
de holding-period (era o buraco central), split-adjust preserva
baseline daily→intraday. **As 3 🟠 restantes são refinamento**, não
bloqueio — o engenheiro que executar o plan pode aplicar as 3
mudanças em < 30 min cada. Recomendo re-escrever §3.3 + §6.2 + §6.5
item 4 e então `writing-plans`.

**Contraste explícito com a v1 deste juiz:** fui o **menos rigoroso**
na v1 (PROCEED-WITH-CHANGES vs 2 BLOCK dos colegas). Nesta rodada, os
dois BLOCK viraram PROCEED provavelmente (retention + adj_close
resolvidos); mantenho PROCEED-WITH-CHANGES porque achei 3
preocupações NOVAS (reuso de `adjust.py`, derivação do threshold 12
meses, decisão financeira sobre subscrição). Honesto com o contexto
"esta é a SEGUNDA rodada com rigor maior solicitado pelo usuário".
