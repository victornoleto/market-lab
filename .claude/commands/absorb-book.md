---
description: Absorve UM livro do knowledge base (books/raw/<slug>.pdf → books/summaries/<slug>.md) via book-reader + validação autônoma em 3 camadas (substitui revisão humana).
argument-hint: <slug> [--model sonnet|opus|haiku] [--hint "<texto>"]
---

Execute o pipeline de absorção para o livro com slug fornecido em `$ARGUMENTS`.

**Parsing dos argumentos:**

`$ARGUMENTS` pode conter:
- Apenas o slug: `math_money_mgmt`
- Slug + override de modelo: `math_money_mgmt --model sonnet`
- Slug + hint do operador: `cycle_analytics --hint "foque cap.3-8, conserte x-refs"`
- Combinação: `math_money_mgmt --model opus --hint "..."`

Extraia:
- `<slug>`: primeiro token não-flag.
- `<model>`: valor após `--model` (opcional). Valores aceitos: `sonnet`, `opus`, `haiku`. Default: NÃO passe `model` ao Agent (deixa o subagente usar o modelo definido na sua frontmatter ou herdar do parent).
- `<hint>`: valor após `--hint` (opcional, string entre aspas). Default: sem hint. Este é **contexto do operador** sobre gaps conhecidos ou correções específicas que o template default do book-reader não captura. Exemplos típicos: cross-refs quebrados a consertar, capítulos sub-minerados a priorizar, tópicos específicos a cobrir com mais densidade, formatação/convenções especiais do livro.

**Heurística automática se `--model` NÃO foi passado:**

Leia `books/extracted/<slug>/_metadata.json` e aplique:
- `recommended_mode == "map_reduce"` OU `est_tokens > 350000` → use `model: "opus"` (priorização estratégica)
- caso contrário → use `model: "sonnet"` (extração disciplinar, mais barato/rápido)

Reporte ao usuário no início qual modelo foi escolhido e por quê.

**Passos:**

1. Verifique que o texto extraído existe:
   ```bash
   ls books/extracted/<slug>/_metadata.json
   ```
   Se não existir, rode: `python scripts/extract_pdfs.py --slug <slug>` antes.

2. Decida o modelo (override explícito ou heurística acima).

3. Dispare o subagente `book-reader` (passando `model: "<model>"` ao Agent tool):
   - Passe o slug no prompt.
   - Instrua-o a seguir o template de 9 seções e a regra-mãe "CITE OU N/A".
   - O agente lê chapters/ ou _full.txt conforme o `recommended_mode` em `_metadata.json`.
   - **Inclua explicitamente no prompt:** "Para cada fórmula, regra ou citação literal: (1) localize o bloco `[PAGE N]` onde o conteúdo aparece no corpo do texto — não no ToC/Índice; (2) copie a fórmula/trecho literalmente daquele bloco; (3) extraia o printed page number do corpo daquele bloco. Nunca use o ToC como fonte de número de página."
   - **Se `<hint>` foi passado**, inclua um bloco adicional no prompt ANTES do template, com este formato exato:
     ```
     ## Instrução específica do operador

     <hint>

     ---

     Esta instrução vem do operador (usuário) e reflete conhecimento
     específico sobre este livro ou a base de conhecimento. Sobrepõe
     preferências padrão do template (ex: priorização de capítulos,
     correções de cross-refs, áreas sub-minerada a cobrir com mais
     densidade). Copie o hint literal — não reformule.
     ```
   - Registre o hint no log de execução:
     ```bash
     echo "[$(date '+%H:%M:%S')] operator hint: <hint>" >> books/summaries/.logs/<slug>.log
     ```

4. Rode a pipeline completa de validação (3 camadas, substitui revisão humana):
   ```
   /validate-summary <slug>
   ```

   Isso executa em sequência:
   - Camada 1: `validate_summary.py` (estrutural)
   - Camada 2: `check_citations.py` (mis-citations determinísticas)
   - Camada 3: 2 juízes adversariais `summary-validator` em paralelo (self-consistency)

   Os juízes adversariais devem rodar SEMPRE com `model: "sonnet"` (busca literal no source — não precisa Opus, economia clara).

5. Se `/validate-summary` retornar `FAIL` ou `BORDERLINE`:
   - Colete o retry hint estruturado:
     ```bash
     .venv/bin/python scripts/aggregate_judges.py <slug> --json > /tmp/retry_hint_<slug>.json
     ```
     O JSON contém `retry_hint_structured`: array de objetos com `claim`, `cited_page`, `actual_page`, `evidence_quote`, `action` — um por hallucination detectada pelos juízes.
   - Re-dispare o `book-reader` passando essas correções como bloco estruturado.
   - Re-dispatches usam o **mesmo modelo** da rodada inicial, salvo se o usuário pedir override.
   - **Se `<hint>` foi passado na invocação original, mantenha o hint no prompt do retry** (é instrução do operador e vale para todas as tentativas — não é algo que o retry "resolve").
   - **Monte o prompt de retry a partir do template abaixo**, renderizando cada item de `retry_hint_structured` como entrada numerada:

     ```
     # CORREÇÕES OBRIGATÓRIAS DO ROUND ANTERIOR

     Para cada item abaixo, siga EXATAMENTE a `action` indicada. Não presuma
     que o round anterior estava correto fora destes itens — mas também não
     reescreva seções inteiras sem motivo.

     {para cada item de retry_hint_structured, com índice 1-based:}

     {i}. **{action}**: {claim}
        - Citado como: {cited_page}
        - Página real: {actual_page}
        - Evidence do livro: "{evidence_quote}"
        - O que fazer segundo a action:
          * `remove` → apague a afirmação inteira do summary (não tente salvar versão parcial).
          * `relocate_to_p_X` → mude apenas a citação de {cited_page} para [p.X]. Mantenha o texto.
          * `rewrite_with_quote` → reescreva a afirmação aderente ao evidence_quote; preserve a citação.
          * `verify_formula` → releia o bloco [PAGE N] literalmente e corrija variável/sinal/expoente conforme o texto.
          * `verify` → recheck livre (hallucination era string legacy, sem action específica).

     ---

     # REGRAS PARA ESTE RETRY

     1. Consulte `books/extracted/<slug>/_page_index.json` antes de emitir
        qualquer `[p.X]`. O campo `pdf_to_printed` é fonte de verdade; não
        re-derive offset heuristicamente.
     2. Nunca cite uma página sem ter visto o termo literalmente no bloco
        `[PAGE N]` correspondente do extraído.
     3. Fórmulas: copie letra-por-letra do bloco. Inclua evidence quote literal
        ≤200 chars (regra inviolável #9 do book-reader).
     4. Self-audit (Passo 3.2): se `check_citations.py` retornar
        `systemic_offset.detected == true`, aplique a correção global
        in-session ANTES de reportar completion.
     ```

   - Rode `/validate-summary <slug>` de novo. Máximo 3 retries.
   - Após o 3º FAIL consecutivo, reporte ao usuário com histórico — provável problema na extração do PDF, no `_page_index.json`, ou limitação do modelo.

6. Reporte o resultado final ao usuário:
   - ✅ PASS / ⚠️ BORDERLINE / ❌ FAIL
   - Modelo usado no book-reader
   - Resumo por camada (estrutural / determinística / adversarial)
   - Self-consistency dos 2 juízes
   - Hallucinations corrigidas durante retries (se houve)
   - Caminho do summary e dos JSONs de auditoria

7. **Atualizar `books/TODO.md`** (apenas se PASS ou BORDERLINE — nunca atualizar em FAIL):

   a. Colete os dados frescos rodando:
      ```bash
      .venv/bin/python scripts/validate_summary.py <slug> 2>&1 | grep -E "result|citations|notes"
      .venv/bin/python scripts/check_citations.py <slug> 2>&1 | tail -1
      ```
      Extraia: `ratio` (ex: `93%`), `cit_total` (campo `total=N`), `cross_ref_issues` (campo `notes` do validate_summary).

   b. Calcule a nova **Qualidade** com base em `ratio` e densidade `cit_total / n_pages` (leia `n_pages` de `books/extracted/<slug>/_metadata.json`):
      - 🌟 **Perfeita** — ratio ≥95% E densidade ≥0.10 cit/p
      - ✅ **Boa** — ratio ≥87% E densidade ≥0.05 cit/p
      - ⚠️ **Regular** — ratio ≥80% mas fora dos limiares acima
      - 🔴 **Sub-minerada** — densidade < 0.05 cit/p (menos de 1 cit/20p)

   c. Determine as **Tarefas pendentes** atualizadas:
      - Remova `Re-abs P*` se a nova qualidade não for Sub-minerada.
      - Mantenha `X-refs` se o `validate_summary` ainda reportar cross-ref issues (campo `notes`).
      - Mantenha flags de ratio (`<85%`, `~85%`, etc.) se ainda aplicáveis.
      - Se todas as tarefas foram resolvidas → `—`.

   d. Localize a linha do `<slug>` na tabela "Status Geral dos Livros" de `books/TODO.md` e **substitua os campos** `Cit`, `Ratio`, `Qualidade` e `Tarefas pendentes` pelos valores novos. Não altere os campos `Importância`, `Autor` ou `pp`.

   e. Atualize a **linha de resumo** ao final da tabela contando os totais reais por categoria de qualidade após a edição.

   f. Se o `<slug>` aparecer na tabela do **item 0** com status `☐`, troque para `✅` e substitua o campo `Sintoma` por:
      ```
      Concluída: <cit_total> cit / <n_pages>p, <ratio> ratio
      ```

**Observações:**
- **Nunca reporte sucesso se `/validate-summary` falhou.**
- **Nunca modifique manualmente o summary** — toda correção via book-reader.
- **Revisão humana foi removida.** A pipeline autônoma de 3 camadas substitui o gate humano.
- JSONs de auditoria ficam em `books/summaries/.validation/` (gitignored).
- A heurística `map_reduce → opus` reflete: livros >400k tokens com 20+ capítulos exigem priorização estratégica que Sonnet faz pior. Para retries direcionados (lista explícita de capítulos a minerar), Sonnet é equivalente — passe `--model sonnet` manualmente nesse caso.
