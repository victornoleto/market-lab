---
description: Dispara o subagente book-reader em paralelo para todos os livros em books/extracted/ que ainda não têm summary. Usa ondas de 4-6 agentes para não estourar rate limits.
---

Processe em paralelo todos os livros que têm `books/extracted/<slug>/_metadata.json` mas ainda NÃO têm `books/summaries/<slug>.md`.

**Passos:**

1. Liste os slugs pendentes:
   ```bash
   cd /var/www/pessoal/ai-trade
   comm -23 \
     <(ls books/extracted/ | sort) \
     <(ls books/summaries/ 2>/dev/null | sed 's/\.md$//' | sort)
   ```
   Essa é a lista de livros a processar.

2. **Antes do batch**, confirme com o usuário se pelo menos 1 livro já foi absorvido e revisado humanamente (ex: `systematic_trading`). Se NÃO, pare e peça que rode `/absorb-book systematic_trading` primeiro. Esse é o gate de qualidade — calibrar o agente em 1 livro antes do batch.

3. Use a skill `superpowers:dispatching-parallel-agents` para disparar os `book-reader` em ondas de **4-6 agentes simultâneos** (não mais, para evitar rate limits).

4. Para cada livro, o sub-prompt deve seguir o modelo:
   ```
   Absorva o livro <slug>. Leia books/extracted/<slug>/_metadata.json para
   decidir modo (single_pass ou map_reduce), produza books/summaries/<slug>.md
   seguindo o template de 9 seções com citações obrigatórias [p.X]/[ch.Y],
   e execute python scripts/validate_summary.py <slug> ao terminar.
   Reporte PASS/FAIL.
   ```

5. Após todas as ondas terminarem, valide o conjunto:
   ```bash
   python scripts/validate_summary.py --all
   ```

6. Reporte:
   - Quantos passaram (PASS) / falharam (FAIL)
   - Lista dos que falharam, com o erro principal
   - Próximo passo: rodar `python scripts/build_skill.py` se todos passaram

**Restrições:**
- Nunca marque como concluído um livro que falhou em `validate_summary.py`.
- Não tente "consertar" summaries manualmente — apenas re-dispare o agente para aquele slug.
- Se >3 livros falharem consecutivamente, PARE e analise se há problema sistêmico (ex: prompt do agente precisa ajuste).
