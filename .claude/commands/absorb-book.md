---
description: Absorve UM livro do knowledge base (books/raw/<slug>.pdf → books/summaries/<slug>.md) via book-reader + validação autônoma em 3 camadas (substitui revisão humana).
argument-hint: <slug>
---

Execute o pipeline de absorção para o livro com slug `$ARGUMENTS`.

**Passos:**

1. Verifique que o texto extraído existe:
   ```bash
   ls books/extracted/$ARGUMENTS/_metadata.json
   ```
   Se não existir, rode: `python scripts/extract_pdfs.py --slug $ARGUMENTS` antes.

2. Dispare o subagente `book-reader`:
   - Passe o slug `$ARGUMENTS` no prompt.
   - Instrua-o a seguir o template de 9 seções e a regra-mãe "CITE OU N/A".
   - O agente lê chapters/ ou _full.txt conforme o `recommended_mode` em `_metadata.json`.

3. Rode a pipeline completa de validação (3 camadas, substitui revisão humana):
   ```
   /validate-summary $ARGUMENTS
   ```

   Isso executa em sequência:
   - Camada 1: `validate_summary.py` (estrutural)
   - Camada 2: `check_citations.py` (mis-citations determinísticas)
   - Camada 3: 2 juízes adversariais `summary-validator` em paralelo (self-consistency)

4. Se `/validate-summary` retornar `FAIL`:
   - O comando já produz a lista de hallucinations com páginas corretas.
   - Re-dispare o `book-reader` passando essas correções como feedback específico.
   - Rode `/validate-summary $ARGUMENTS` de novo. Máximo 3 retries.
   - Após o 3º FAIL consecutivo, reporte ao usuário com histórico — provável problema na extração do PDF.

5. Reporte o resultado final ao usuário:
   - ✅ PASS / ⚠️ BORDERLINE / ❌ FAIL
   - Resumo por camada (estrutural / determinística / adversarial)
   - Self-consistency dos 2 juízes
   - Hallucinations corrigidas durante retries (se houve)
   - Caminho do summary e dos JSONs de auditoria

**Observações:**
- **Nunca reporte sucesso se `/validate-summary` falhou.**
- **Nunca modifique manualmente o summary** — toda correção via book-reader.
- **Revisão humana foi removida.** A pipeline autônoma de 3 camadas substitui o gate humano.
- JSONs de auditoria ficam em `books/summaries/.validation/` (gitignored).
