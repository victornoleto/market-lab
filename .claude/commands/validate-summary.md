---
description: Validação completa e autônoma de um summary de livro (estrutural + citações determinísticas + juiz adversarial LLM com self-consistency). Substitui a revisão humana.
argument-hint: <slug>
---

Execute a pipeline de validação **completa** para o summary `$ARGUMENTS`, substituindo a revisão humana.

**Filosofia:** 3 camadas independentes. Cada uma precisa passar. Nenhuma isolada é suficiente.

---

## Camada 1 — Validação estrutural (determinística, ~0 tokens)

```bash
python scripts/validate_summary.py $ARGUMENTS
```

Se `FAIL` → aborte. Reporte ao usuário e PARE; não adianta rodar camadas superiores em summary estruturalmente quebrado.

## Camada 2 — Citações determinísticas (~0 tokens)

```bash
python scripts/check_citations.py $ARGUMENTS --json > /tmp/citecheck_$ARGUMENTS.json
python scripts/check_citations.py $ARGUMENTS
```

Leia o JSON. Se houver `failures`, colete-os — **você vai passar essa lista como `focus_claims` para os juízes adversariais** (prioridade máxima).

Esta camada pega mis-citations óbvias (página fora do range, zero overlap de tokens) sem gastar tokens LLM.

## Camada 3 — Juízes adversariais com self-consistency

Dispare **DOIS subagentes `summary-validator` EM PARALELO** (mesma mensagem, duas invocações `Task`). Ambos usam frame adversarial; a diferença é a DIVERSIDADE DE AMOSTRAGEM para cobrir seções complementares.

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

Rationale: calibração anterior mostrou que frame "paraphrase drift" é complacente demais. Dois ângulos adversariais com samplings complementares cobrem mais superfície; a sobreposição parcial (cada um também testa 2 claims do domínio do outro) valida self-consistency.

---

## Agregação e decisão final

Após os dois juízes retornarem:

1. Leia `books/summaries/.validation/$ARGUMENTS_judge_1.json` e `..._judge_2.json`.
2. Aplique a matriz:

| Judge 1 | Judge 2 | Camada 2 | Decisão final |
|---------|---------|----------|---------------|
| PASS    | PASS    | ok       | ✅ **PASS** — summary aprovado para o knowledge base |
| PASS    | BORDERLINE | ok    | ⚠️ **BORDERLINE** — aceito com nota; registre para auditoria futura |
| qualquer FAIL | — | — | ❌ **FAIL** — re-disparar book-reader com feedback específico |
| PASS    | PASS    | tem failures | ❌ **FAIL** — determinístico bateu; juízes foram complacentes, não confie |
| discordância forte | — | — | ❌ **FAIL** — self-consistency quebrou; requer re-extração |

3. Agregue as `hallucinations_found` de ambos os juízes em uma lista única (dedupe).

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
