# Plano — Fechar absorção de `time_series_hamilton` após falha de transport nos juízes finais

> **Uso:** arquivo de referência para verificação cruzada com o agente paralelo que está rodando.
> Se o agente paralelo já aplicou todos os passos abaixo, nada a fazer. Caso contrário, listar gaps e decidir se completa manualmente.

## Contexto

`/absorb-book time_series_hamilton` foi rodado. O pipeline completou:
- Book-reader (map_reduce/opus, 421k tokens) gerou summary com 89 citações / 814p (densidade 0.11/p, acima do alvo 0.10).
- Camada 1 (estrutural): **PASS**, 10/10 seções, ratio 95%.
- Camada 2 (determinística): quase-PASS — apenas **1 falha residual confirmada como false positive** do offset detector em `[p.372]` (state-space), conteúdo real está na página citada. `[p.257]` (VAR) também foi citado pelo usuário como false positive, mas a execução atual do `check_citations.py` só reporta `[p.372]` (detector foi refinado durante os retries).
- Camada 3 rodou em 4 ondas: round 1 (J1 74% BORDERLINE / J2 65% FAIL), round 2 pós retry #1 (J1 76% / J2 76% FAIL, 3 novas halluc.), round 3 pós retry #2 (J1 85% PASS / J2 80% FAIL — 1 critical ARCH), round 4 pós retry #3 dispatched mas **ambos os juízes retornaram `[Tool result missing due to internal error]`**.
- 24 correções aplicadas ao longo de 3 retries (Hansen J, Newey-West, Wold, Engle-Granger, overdifferencing, Yule-Walker, Wiener-Kolmogorov, GMM, ARCH 1/4, DF críticos T-dependentes, etc.).

**Estado em disco (verificado em 2026-04-13 20:16):**
- `books/summaries/time_series_hamilton.md` existe (31 KB, Apr 13 20:15) com as 24 correções.
- `.validation/` tem `judge_1.json`, `judge_1_retry1.json`, `judge_1_retry2.json`, idem para judge_2 — confirmando que `judge_1_retry3.json` / `judge_2_retry3.json` **nunca foram gravados** (bateu com o erro de transport).
- `.logs/time_series_hamilton.log` termina em `[20:16:10] Retry #3 complete — re-running validation` — não há linha subsequente de "Camada 3 — Judge #X", confirmando que o parent agent morreu ou ficou suspenso sem fechar validação.
- `books/TODO.md` linha 58 ainda lista o livro como `🔴 Sub-minerada` com `Re-abs P1 + X-refs`; linha 89 ainda `☐`.

**Veredicto operacional:** o parent agent pode ser encerrado manualmente. O erro foi transport/tool (não falha de validação); o parent agent completou todo o trabalho caro (3 retries, todos os fixes aplicados). O que falta é cirurgicamente pequeno: **re-rodar SOMENTE Camada 3** sobre o summary atual. Isso não conta como retry #4 (essa política só existe quando o juiz retorna FAIL, não quando o tool-call perde resultado).

## Intenção

Fechar a absorção de `time_series_hamilton` honrando a regra "nunca declare PASS sem juízes" sem queimar um 4º retry caro de book-reader.

## Approach recomendado

**Passo 1 — Encerrar o parent agent parado.**

Não há cleanup de arquivo necessário (summary, JSONs parciais e log devem ficar). Se o `/absorb-book` ainda aparece como rodando na UI, cancele-o. Nenhum retry adicional do book-reader.

**Passo 2 — Re-despachar SOMENTE Camada 3 (juízes adversariais).**

Um único turno com **duas invocações `Agent` em paralelo** (mesma mensagem assistant), ambas com:
- `subagent_type: "summary-validator"`
- `model: "sonnet"` (sempre — busca literal no source)
- Prompt igual ao definido em `.claude/commands/validate-summary.md` linhas 60-74, mas passando `focus_claims: ["[p.372] state-space representation (false positive do offset detector, confirmar literalmente no bloco [PAGE 372/746])"]` para os dois. Judge #1 `seed_frame: frame_1a`, Judge #2 `seed_frame: frame_1b`.
- Output: gravar em `books/summaries/.validation/time_series_hamilton_judge_1_retry3.json` e `..._judge_2_retry3.json`.

Registrar no log:
```
[$(date '+%H:%M:%S')] Camada 3 round 4 — manual re-dispatch após tool transport error no round 3
```

**Passo 3 — Aplicar matriz de decisão (linhas 90-97 de `validate-summary.md`).**

Ler os dois JSONs e aplicar:
- **J1 PASS + J2 PASS** → `✅ PASS` (o false positive de `[p.372]` em Camada 2 é documentado; os juízes devem confirmar que o conteúdo existe no bloco `[PAGE 372/746]`).
- **J1 PASS + J2 BORDERLINE** → `⚠️ BORDERLINE` (aceitar, registrar nota).
- **qualquer FAIL ou discordância forte** → parar, reportar ao usuário o histórico (3 retries + round 4 manual); NÃO disparar retry #4 de book-reader. Nessa branch, consultar o usuário antes de qualquer ação (a política de 3 retries diz "provável problema na extração do PDF").

**Passo 4 — Atualizar `books/TODO.md`** (só se PASS ou BORDERLINE, nunca em FAIL):

Seguir o algoritmo em `.claude/commands/absorb-book.md` passo 7 (linhas 100-129):

a. Coletar números frescos:
   ```bash
   .venv/bin/python scripts/validate_summary.py time_series_hamilton 2>&1 | grep -E "result|citations|notes"
   .venv/bin/python scripts/check_citations.py time_series_hamilton 2>&1 | tail -1
   ```
   Valores esperados já verificados: `81/85 citações (95%)`, `89 total`, densidade `89/814 = 0.109 cit/p`.

b. Calcular qualidade: ratio 95% + densidade 0.109 ≥ 0.10 → **🌟 Perfeita**.

c. Tarefas pendentes novas:
   - Remover `Re-abs P1` (deixou de ser sub-minerada: 19 cit → 89 cit).
   - Remover `X-refs` (o hint mandou corrigir `analysis_financial_time_series.md` → `fin_time_series_tsay.md`; confirmar via `validate_summary.py` que `notes` está vazio para cross-refs — se ainda aparecer, manter `X-refs`).
   - Se `notes` vazio → `—`. Se BORDERLINE nos juízes → adicionar nota tipo `BORDERLINE adversarial (J1 X% / J2 Y%)`.

d. Editar `books/TODO.md` linha 58: substituir apenas `Cit`, `Ratio`, `Qualidade`, `Tarefas pendentes`. Não tocar `Importância`, `Autor`, `pp`.
   - Valor atual: `| 19 | 85% | 🔴 Sub-minerada | Re-abs P1 + X-refs |`
   - Valor novo (se PASS): `| 89 | 95% | 🌟 Perfeita | — |`

e. Atualizar linha 65 (resumo totais): `🌟 11` passa a `🌟 12`, `🔴 2` passa a `🔴 1`.

f. Item 0 linha 89: trocar `☐` por `✅` na linha de `time_series_hamilton` e substituir campo `Sintoma` por:
   `Concluída: 89 cit / 814p, 95% ratio — PASS (J1 X% / J2 Y%)`.

g. Item 1 linha 194 (cross-refs quebrados em `time_series_hamilton.md`): se o book-reader de fato corrigiu `analysis_financial_time_series.md → fin_time_series_tsay.md`, marcar checkbox `[x]`. Verificar:
   ```bash
   grep -n "analysis_financial_time_series" books/summaries/time_series_hamilton.md
   ```
   (espera-se zero matches).

**Passo 5 — NÃO commitar.** O TODO.md ainda tem outros itens P1 pendentes (`trading_systems_methods`, `volatility_trading` corretivo); commit separado só faz sentido quando o operador decidir.

## Arquivos críticos

- `books/summaries/time_series_hamilton.md` — summary atual (não tocar manualmente; validação confirma estado).
- `books/summaries/.validation/time_series_hamilton_judge_{1,2}_retry3.json` — a serem gerados pelos 2 juízes re-despachados.
- `books/summaries/.logs/time_series_hamilton.log` — append do round 4.
- `books/TODO.md` — edição de 3 linhas (58, 65, 89) + possível checkbox no item 1 (linha 194).
- `.claude/agents/summary-validator.md` — referência para saber o payload esperado pelos juízes.

## Verificação end-to-end

1. Após re-dispatch dos juízes, confirmar que os dois JSONs foram escritos:
   ```bash
   ls -la books/summaries/.validation/time_series_hamilton_judge_*_retry3.json
   ```
2. Ler `verdict` e `support_ratio` em cada um; aplicar matriz.
3. Re-rodar as 2 camadas determinísticas para capturar números finais ao TODO:
   ```bash
   .venv/bin/python scripts/validate_summary.py time_series_hamilton
   .venv/bin/python scripts/check_citations.py time_series_hamilton
   ```
4. Após editar `books/TODO.md`, re-ler as linhas editadas para confirmar que só os campos esperados mudaram (`git diff books/TODO.md`).
5. Sanity: `grep -c "time_series_hamilton" books/TODO.md` deve retornar o mesmo número de matches antes e depois (não adicionamos/removemos linhas, apenas substituímos campos).

## Não fazer

- **Não** disparar retry #4 do book-reader (24 correções já feitas; política esgotada).
- **Não** editar `time_series_hamilton.md` manualmente, mesmo que apenas para o cross-ref — viola a regra "nunca modifique summary manualmente".
- **Não** commitar até o usuário pedir (múltiplos P1 ainda pendentes no TODO).
- **Não** ignorar os false positives de Camada 2 — documentar `[p.372]` explicitamente no log para não contaminar a decisão dos juízes.

## Checklist de verificação cruzada (usar contra o agente paralelo)

Quando for comparar com o que o agente paralelo fez, cheque nesta ordem:

- [ ] `books/summaries/.validation/time_series_hamilton_judge_1_retry3.json` existe?
- [ ] `books/summaries/.validation/time_series_hamilton_judge_2_retry3.json` existe?
- [ ] Ambos têm `verdict: PASS` (ou um PASS + um BORDERLINE)?
- [ ] `books/summaries/.logs/time_series_hamilton.log` tem linha final com veredicto consolidado?
- [ ] `books/TODO.md` linha 58 foi atualizada para `| 89 | 95% | 🌟 Perfeita | — |` (ou equivalente consistente com os números reais)?
- [ ] `books/TODO.md` linha 65 (resumo) reflete o novo total?
- [ ] `books/TODO.md` linha 89 (item 0) tem `✅` e campo `Sintoma` atualizado?
- [ ] `books/TODO.md` linha 194 (item 1, cross-refs) tem checkbox marcado?
- [ ] `grep "analysis_financial_time_series" books/summaries/time_series_hamilton.md` retorna vazio?
- [ ] NÃO foi feito commit nem retry #4 do book-reader?

Se qualquer item acima estiver faltando quando o agente paralelo terminar, complete manualmente seguindo os Passos 2–4.
