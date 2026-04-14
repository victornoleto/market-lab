---
description: Validação completa e autônoma de um summary de livro (estrutural + citações determinísticas + juiz adversarial LLM com self-consistency). Substitui a revisão humana.
argument-hint: <slug>
---

Execute a pipeline de validação **completa** para o summary `$ARGUMENTS`, substituindo a revisão humana.

**Filosofia:** 3 camadas independentes. Cada uma precisa passar. Nenhuma isolada é suficiente.

---

## Setup de log

```bash
mkdir -p books/summaries/.logs
echo "[$(date '+%H:%M:%S')] validate-summary START — $ARGUMENTS" >> books/summaries/.logs/$ARGUMENTS.log
```

## Camada 1 — Validação estrutural (determinística, ~0 tokens)

```bash
echo "[$(date '+%H:%M:%S')] Camada 1 — estrutural..." >> books/summaries/.logs/$ARGUMENTS.log
python scripts/validate_summary.py $ARGUMENTS
```

Após resultado:
```bash
echo "[$(date '+%H:%M:%S')] Camada 1: <PASS|FAIL> — <N>/10 seções, ratio <R>%" >> books/summaries/.logs/$ARGUMENTS.log
```

Se `FAIL` → aborte. Reporte ao usuário e PARE; não adianta rodar camadas superiores em summary estruturalmente quebrado.

## Camada 2 — Citações determinísticas (~0 tokens)

```bash
echo "[$(date '+%H:%M:%S')] Camada 2 — citações determinísticas..." >> books/summaries/.logs/$ARGUMENTS.log
python scripts/check_citations.py $ARGUMENTS --json > /tmp/citecheck_$ARGUMENTS.json
python scripts/check_citations.py $ARGUMENTS
```

Após resultado:
```bash
echo "[$(date '+%H:%M:%S')] Camada 2: <PASS|FAIL> — <F> falhas em <T> citações" >> books/summaries/.logs/$ARGUMENTS.log
```

Leia o JSON. Se houver `failures`, colete-os — **você vai passar essa lista como `focus_claims` para os juízes adversariais** (prioridade máxima).

Esta camada pega mis-citations óbvias (página fora do range, zero overlap de tokens) sem gastar tokens LLM.

## Camada 3 — Juízes adversariais com self-consistency

### Decisão de dispatch: paralelo vs serial (proteção H1 — API overload)

Antes de dispatchar, leia `est_tokens` do livro:

```bash
EST_TOKENS=$(python3 -c "import json; print(json.load(open('books/extracted/$ARGUMENTS/_metadata.json'))['est_tokens'])")
echo "[$(date '+%H:%M:%S')] Camada 3 — est_tokens=$EST_TOKENS" >> books/summaries/.logs/$ARGUMENTS.log
```

- **Se `est_tokens > 300_000`** → **dispatch SERIAL**: Judge #1 primeiro (espere terminar), `sleep 30`, depois Judge #2. Subagentes Task são contextualmente isolados, então serial NÃO contamina self-consistency — só adiciona latência. Trade-off aceitável: livros grandes esgotam API quando 2 subagentes paralelos lêem `_full.txt` de 400k+ tokens cada simultaneamente.
- **Caso contrário** → **dispatch PARALELO**: ambos na mesma assistant message (comportamento original).

Logue a escolha:
```bash
if [ "$EST_TOKENS" -gt 300000 ]; then
  echo "[$(date '+%H:%M:%S')] Camada 3 — SERIAL dispatch (est_tokens=$EST_TOKENS > 300k)" >> books/summaries/.logs/$ARGUMENTS.log
else
  echo "[$(date '+%H:%M:%S')] Camada 3 — PARALLEL dispatch (est_tokens=$EST_TOKENS)" >> books/summaries/.logs/$ARGUMENTS.log
fi
```

### Dispatch dos juízes

Dispare DOIS subagentes `summary-validator` (paralelo OU serial conforme acima). Ambos usam frame adversarial; a diferença é a DIVERSIDADE DE AMOSTRAGEM para cobrir seções complementares.

**Sempre passe `model: "sonnet"` ao Agent tool** para os juízes — a tarefa é busca literal no source, não exige Opus.

**Judge #1 (Frame 1a — focus fórmulas/regras/algoritmos):**
```
slug: $ARGUMENTS
judge_id: 1
seed_frame: frame_1a
focus_claims: <lista de failures da camada 2, se houver>
```

**Judge #2 (Frame 1b — focus parâmetros/pitfalls/conceitos):**
```
slug: $ARGUMENTS
judge_id: 2
seed_frame: frame_1b
focus_claims: <mesma lista>
```

Rationale: calibração anterior mostrou que frame "paraphrase drift" é complacente demais. Dois ângulos adversariais com samplings complementares cobrem mais superfície; a sobreposição parcial valida self-consistency.

**Importante (Camada B):** os juízes retornam APENAS `verdict|ratio|halluc|report_path` no texto (≤1 KB). O JSON completo em disco é o que importa — o agregador (`scripts/aggregate_judges.py`) lê de lá.

---

## Agregação e decisão final (Camada A — disk fallback)

Após dispatch (mesmo se um ou ambos juízes retornarem `[Tool result missing due to internal error]`), execute o agregador determinístico:

```bash
echo "[$(date '+%H:%M:%S')] Camada 3 — aggregating via aggregate_judges.py..." >> books/summaries/.logs/$ARGUMENTS.log
.venv/bin/python scripts/aggregate_judges.py $ARGUMENTS --citecheck /tmp/citecheck_$ARGUMENTS.json
AGG_EXIT=$?
echo "[$(date '+%H:%M:%S')] Camada 3 — aggregator exit=$AGG_EXIT" >> books/summaries/.logs/$ARGUMENTS.log
```

**Por quê via script Python:** Bug conhecido do Claude Code (issue #44068) faz tool results sumirem em trânsito mesmo quando o subagente executou e escreveu o JSON em disco. O script lê os JSONs diretamente, ignorando se o tool result chegou ou não.

**Tratamento dos exit codes:**

| Exit | Significado | Ação |
|------|-------------|------|
| `0` | PASS | Aplique a matriz abaixo, finalize com PASS |
| `1` | BORDERLINE | Aceito com nota; finalize com BORDERLINE |
| `2` | FAIL | Re-disparar book-reader (ver seção "Re-dispatch") |
| `3` | MISSING_JSON (juiz não escreveu — provável H3) | **RETRY**: ver fluxo abaixo |
| `4` | I/O / parse error | FAIL terminal — logar e abortar |

### Fluxo de retry para exit=3 (MISSING_JSON)

O agregador imprime no stderr quais juízes estão faltando (e se há orphan retry).

1. **1º retry (serial, ~60s depois):** dispatchar APENAS o(s) juiz(es) faltante(s) em SERIAL (uma mensagem por juiz, gap de 30s entre eles).
   ```bash
   echo "[$(date '+%H:%M:%S')] Camada 3 — RETRY 1: re-dispatching missing judge(s) serially" >> books/summaries/.logs/$ARGUMENTS.log
   sleep 60
   ```
   Re-rode o agregador.
2. **2º retry (serial novamente, ~180s depois):** se o 1º retry ainda não escreveu o JSON.
   ```bash
   echo "[$(date '+%H:%M:%S')] Camada 3 — RETRY 2: last attempt before terminal FAIL" >> books/summaries/.logs/$ARGUMENTS.log
   sleep 180
   ```
3. **Após 2 retries, se ainda MISSING_JSON:** terminal FAIL.
   ```bash
   echo "[$(date '+%H:%M:%S')] FATAL: judge JSON missing after 2 retries — aborting" >> books/summaries/.logs/$ARGUMENTS.log
   ```
   Reporte ao usuário com histórico do log e PARE (não re-dispare book-reader — problema é de pipeline, não de extração).

### Matriz de decisão (aplicada PELO SCRIPT, replicada aqui para referência)

| Judge 1 | Judge 2 | Camada 2 | Decisão final |
|---------|---------|----------|---------------|
| PASS    | PASS    | ok       | ✅ **PASS** — summary aprovado para o knowledge base |
| PASS    | BORDERLINE | ok    | ⚠️ **BORDERLINE** — aceito com nota; registre para auditoria futura |
| BORDERLINE | BORDERLINE | ok | ⚠️ **BORDERLINE** — aceito com nota |
| qualquer FAIL | — | — | ❌ **FAIL** — re-disparar book-reader com feedback específico |
| PASS    | PASS    | tem failures | ❌ **FAIL** — determinístico bateu; juízes foram complacentes |
| PASS vs FAIL (discordância forte) | — | — | ❌ **FAIL** — self-consistency quebrou |

O `aggregate_judges.py --json` também emite `hallucinations_consolidated` (lista única dedupe-friendly) — use para o feedback ao book-reader.

## Re-dispatch em caso de FAIL

Se final = FAIL, monte um prompt de feedback específico e re-dispare o `book-reader`:

```
A validação falhou. As seguintes hallucinations foram identificadas:

1. <claim> — cited [p.X] mas a ideia está em [p.Y] (evidence: "<quote>")
2. <claim> — fórmula incorreta (summary: X, livro: Y)
...

Corrija CADA uma individualmente:
- Se a ideia existe em outra página, atualize a citação.
- Se a ideia não existe, remova o claim ou marque N/A.
- NÃO chute páginas.

Depois rode novamente validate_summary.py e check_citations.py antes de reportar.
```

Rode `/validate-summary $ARGUMENTS` novamente. Máximo **3 retries**; após o 3º FAIL, reporte ao usuário com histórico completo — provavelmente é problema de extração do PDF, não do summary.

---

```bash
echo "[$(date '+%H:%M:%S')] validate-summary END — <PASS|BORDERLINE|FAIL> (<N> hallucinations)" >> books/summaries/.logs/$ARGUMENTS.log
```

## Relatório final ao usuário

```
<emoji> Validação: $ARGUMENTS — <PASS|BORDERLINE|FAIL>

Camada 1 (estrutural): <PASS|FAIL> — <N>/10 seções, citation ratio <R>%
Camada 2 (determinística): <PASS|FAIL> — <F> falhas em <T> citações
Camada 3 (adversarial):
  Judge #1: <veredicto> — support_ratio <R>%, <N> hallucinations
  Judge #2: <veredicto> — support_ratio <R>%, <N> hallucinations
  Self-consistency: <concordam|discordam>

Hallucinations consolidadas: <N>
<se FAIL: liste top 3 com páginas corretas>

Arquivo: books/summaries/$ARGUMENTS.md
Relatórios detalhados: books/summaries/.validation/$ARGUMENTS_judge_{1,2}.json
```

---

## Observações operacionais

- Os dois juízes DEVEM rodar em paralelo (mesma `assistant` message, duas tool calls). Se rodar em série, Judge #2 pode ser influenciado pelo #1 via cache de contexto.
- Nunca reporte PASS se camada 2 falhou, mesmo que juízes aprovem — o determinístico é ground truth para páginas.
- Nunca faça a validação você mesmo; use os agentes. Manter a camada 3 fora do contexto principal evita contaminação.
- O diretório `.validation/` é gitignored (adicione ao `.gitignore` se ainda não estiver).
