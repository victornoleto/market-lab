# 2026-04-01 a 2026-04-11 — Phase 0 (knowledge base)

Ingestão dos 33 PDFs via pipeline `books/raw/<slug>.pdf` →
`extracted/` → `summaries/<slug>.md`. Validação autônoma em 3
camadas (estrutural + citações determinísticas + juiz adversarial
LLM). 12 Perfect / 20 Good / 1 Border / **zero alucinações**.
Geração da `knowledge/SKILL.md` agregada como Claude Skill.
