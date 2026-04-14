---
description: Dispara o subagente book-reader em paralelo para todos os livros em books/extracted/ que ainda não têm summary. Usa ondas de 2-3 agentes em paralelo, com checkpoint e auto-retry em 5h caso bata rate limit ou esgotamento de saldo.
---

Processe em paralelo todos os livros que têm `books/extracted/<slug>/_metadata.json` mas ainda NÃO têm `books/summaries/<slug>.md`.

**Filosofia de execução (noite/autônomo):**
- Ondas pequenas (2-3 agentes) para minimizar risco de rate limit.
- Checkpoint persistente em `books/summaries/.progress.json` → retoma de onde parou.
- Log append-only em `books/summaries/.progress.log` para o usuário seguir com `tail -f`.
- Se bater rate limit / saldo expirar → `ScheduleWakeup(delaySeconds=18000)` com este mesmo comando.
- Nunca reporta PASS sem passar pela pipeline de 3 camadas (`/absorb-book` já faz isso).

## Log de progresso (tail -f friendly)

Todo evento importante deve ser appendado em `books/summaries/.progress.log` com formato:
```
<ISO-timestamp> <LEVEL> <event> <slug?> <detail?>
```

Eventos obrigatórios (1 linha cada, nunca sobrescreva, sempre append):
- `INFO  start          pending=<N>`
- `INFO  wave_start     slugs=[a,b,c]`
- `INFO  wave_dispatch  <slug> (size=<tokens>, mode=<mode>)`
- `INFO  book_pass_l12  <slug>  (layers 1+2 ok, starting adversarial)`
- `INFO  book_retry     <slug>  attempt=<n>/3 reason=<short>`
- `PASS  book_done      <slug>  claims=<N> citations=<R>%`
- `FAIL  book_done      <slug>  reason=<short>`
- `WARN  rate_limit     detail=<msg>  remaining_pending=<N>`
- `INFO  wakeup_set     delay=18000s  reason=<short>`
- `INFO  resume         from_checkpoint=true  pending=<N>`
- `INFO  finish         pass=<N> fail=<N> retries=<N>`

Use `echo "$(date -Iseconds) ..." >> books/summaries/.progress.log` via Bash. Nunca use `>` (truncate).

---

## Passo 1 — Apurar livros pendentes

```bash
cd /var/www/pessoal/ai-trade
comm -23 \
  <(ls books/extracted/ | sort) \
  <(ls books/summaries/ 2>/dev/null | sed 's/\.md$//' | sort)
```

Se lista vazia → reporte "nada a fazer" e encerre.

## Passo 2 — Gate de qualidade

Confirme que ≥1 livro já foi absorvido e validado pela pipeline de 3 camadas (`systematic_trading`, `time_series_hamilton` etc). Se não houver nenhum, PARE e peça ao usuário para rodar `/absorb-book <slug>` num livro primeiro — é a calibração inicial.

## Passo 3 — Carregue/crie o checkpoint

Arquivo: `books/summaries/.progress.json`

```json
{
  "started_at": "<ISO>",
  "last_updated_at": "<ISO>",
  "pending": ["slug1", "slug2", ...],
  "in_progress": [],
  "done_pass": [],
  "done_fail": [],
  "retries_scheduled": 0
}
```

Se o arquivo já existir, carregue-o. Sincronize `pending` com a lista real (remova slugs que agora têm summary). Não reprocesse `done_pass`. Slugs em `done_fail` entram no final da fila com retry restante.

## Passo 4 — Loop de ondas (2-3 agentes em paralelo)

Para cada onda, até `pending` estar vazia:

1. Selecione os próximos **2 a 3** slugs de `pending`.
   - Prefira 2 se algum for livro grande (>500k tokens estimados, veja `est_tokens` no metadata).
   - Use 3 se todos forem pequenos (<200k tokens).
2. Mova-os para `in_progress`, atualize `last_updated_at`, salve o checkpoint.
3. Dispare os subagentes **na mesma mensagem** (paralelo real):

   Para cada slug, use `Agent(subagent_type="book-reader")` com prompt auto-contido:
   ```
   Absorva o livro <slug>.

   - Leia books/extracted/<slug>/_metadata.json para decidir modo.
   - Produza books/summaries/<slug>.md no template de 9 seções.
   - Regra-mãe: CITE OU N/A. Toda afirmação factual precisa [p.X]/[ch.Y].
   - Ao terminar, rode:
     python scripts/validate_summary.py <slug>
     python scripts/check_citations.py <slug>
   - Reporte: PASS/FAIL + contagem de claims citadas.
   ```
4. Após a onda retornar:
   - Para cada slug com PASS nas camadas 1+2: rode `/validate-summary <slug>` (camada 3 adversarial com 2 juízes). Se PASS final → move para `done_pass`. Se FAIL → re-dispare `book-reader` com feedback específico (máx 3 retries por livro; após isso, mova para `done_fail`).
   - Para cada slug com FAIL estrutural: re-dispare `book-reader` com o erro (mesmo critério de 3 retries).
5. Atualize checkpoint.

## Passo 5 — Detecção de rate limit / saldo esgotado

Se QUALQUER tool call retornar erro identificável como:
- rate limit (HTTP 429, "rate_limit_exceeded", "overloaded_error")
- saldo esgotado ("credit_balance_too_low", "insufficient credits", "quota_exceeded")
- timeout sistêmico repetido (>3 falhas seguidas sem progresso)

Então, **imediatamente**:
1. Mova slugs `in_progress` de volta para `pending` (não confiar em estado parcial).
2. Incremente `retries_scheduled` no checkpoint e salve.
3. Agende o retry com `ScheduleWakeup`:
   ```
   delaySeconds: 18000       # 5h
   prompt: "/absorb-all-books"
   reason: "rate limit/credit exhausted; retrying batch in 5h — N livros pendentes"
   ```
4. Reporte ao usuário: "⏸️ Pausado por <motivo>. Retomarei em 5h. Restam N livros."
5. ENCERRE (não tente mais tool calls).

Se `retries_scheduled` já for ≥4 (mais de ~20h de pausas acumuladas sem progresso), PARE e reporte ao usuário para investigar manualmente (não fique em loop infinito).

## Passo 6 — Relatório final

Quando `pending` esvaziar:

```bash
python scripts/validate_summary.py --all
for slug in <done_pass>; do python scripts/check_citations.py "$slug" | head -2; done
```

Reporte:
- ✅ PASS: N livros
- ❌ FAIL (após 3 retries): lista
- ⏸️ Retries agendados durante a execução: N
- Próximo passo: `python scripts/build_skill.py` se tudo PASS

Remova `books/summaries/.progress.json` (ou renomeie para `.progress.<timestamp>.json.done` para auditoria).

---

## Restrições

- Nunca marque PASS sem ter rodado as 3 camadas de validação.
- Nunca edite summaries manualmente — sempre via book-reader.
- Ondas de 2-3 agentes, nunca mais.
- Se >3 livros falharem consecutivamente nos mesmos erros, PARE e reporte — indica problema sistêmico.
- `.progress.json` é append-safe; em dúvida, prefira reescrever o arquivo completo após cada mutação.
