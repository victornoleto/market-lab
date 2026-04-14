# TODO — Pré build_skill

Checklist de itens a revisar/corrigir antes de rodar `python scripts/build_skill.py`.
Status da base em `2026-04-14`: **33/33 livros com summary, 100% PASS estrutural, 33/33 PASS `check_citations.py` (0 fails)**.

**Sessão 2026-04-14 — P0+P1 re-absorptions pós pipeline hardening:**
- ✅ Item 0: `CITATION_RE` expandido para aceitar page-first, en-dash e paren-chapter (6 livros desbloqueados do n_total≈0); commit `6d445f1`.
- ✅ Item C: `eval_opt_strategies` → PASS retry3 (5 mis-citations corrigidas cirurgicamente).
- ✅ Item E: `systematic_trading` → PASS retry2 (4 mis-citations corrigidas: SR 0.08 p.196, Table 4 p.60, SR_realistic, EWMAC→early-loss-taker).
- ⚠️ Item F: `trading_systems_methods` → BORDERLINE (Market Profile p.798-800→826, 0 halluc).
- ⚠️ Item B: `advances_fin_ml` → BORDERLINE (quantificação 2-3x Sharpe removida, 0 halluc).
- ⚠️ Item D: `algo_trading_chan` → BORDERLINE (4 mis-citations de página corrigidas, 0 halluc).
- ✅ Item G: `time_series_hamilton` → ratio 95%→98% pós-pipeline-hardening (chapter_intro warn verdict limpou 2 false-positives).

**Sessão 2026-04-14 (tarde) — FU-1/2/3 zerados:**
- ✅ **FU-1 resolvido:** `compute_n_chapters_effective` usa `max(ch.N)` citado no summary como floor (commit `62edeea`). Desbloqueou `math_money_mgmt` (60→2 fails → 0 após fix cirúrgico) e `advances_fin_ml` (4→0 fails). +4 testes TDD em `tests/test_check_citations.py`.
- ✅ **FU-2 resolvido:** audit dos 4 livros pós FU-1 — `data_driven_science` e `sentiment_analysis_handbook` já PASS automaticamente; `adaptive_markets` 3 fails → 0 (CAPM/Alpha/Khandani-Lo re-pageadas para páginas reais de conteúdo); `cycle_analytics` 1 fail → 0 (EMA lag [p.35]→[p.19], PDF/printed confusão) (commit `76988c3`).
- ✅ **FU-3 resolvido:** convenção PT/EN documentada em `.claude/agents/book-reader.md` (regra 8, commit `1f7e912`) — 4 exemplos ✅/❌ cobrindo headings e REGRA lines.
- ✅ **Strict 100% halluc audit:** verificados `math_money_mgmt, regime_change, risk_parity, tech_analysis_patterns, testing_tuning` — 1 halluc real encontrada e corrigida em `regime_change` (Glattfelder 2008→2011 per bibliografia [27] = Quantitative Finance 2011, commit `a124f7a`). Demais livros têm apenas `ambiguous` verdicts (page-off ≤2 ou paráfrases semânticas) — não bloqueiam `build_skill`.

---

## Status Geral dos Livros

Estado atual de cada livro: qualidade da absorção e tarefas pendentes antes do `build_skill`.

**Legenda de importância** (para o pipeline de swing trading CFD — Pepperstone/cTrader):
- `⭐⭐⭐` **Crítico** — no critical path do sistema; citado no plano ou impacta múltiplos módulos-chave
- `⭐⭐` **Importante** — impacta fortemente um módulo específico (strategy, sizing, validation, signals)
- `⭐` **Complementar** — background teórico, referência numérica, ou módulo periférico

**Legenda de qualidade:**
- 🌟 **Perfeita** — ratio ≥95% e densidade ≥0.10 cit/p
- ✅ **Boa** — ratio ≥87% e densidade adequada, sem re-absorção pendente
- ⚠️ **Regular** — ratio 80–86% ou densidade suspeita; avaliar re-absorção após P0–P2
- 🔴 **Sub-minerada** — citações absolutas muito baixas (< 1 cit/20p); re-absorção na fila

**Legenda de tarefas:**
- `Re-abs Pn` = re-absorção pendente, prioridade n (ver item 0)
- `X-refs` = cross-references quebrados (ver item 1)
- `<85%` / `~85%` = ratio abaixo ou perto do limiar (ver item 4)
- `—` = sem tarefas pendentes

| Slug | Importância | Autor | pp | Cit | Ratio | Qualidade | Review (absorção) | Tarefas pendentes |
|---|---|---|---|---|---|---|---|---|
| `adaptive_markets` | `⭐` Complementar | Lo | 503 | 10 | 89% | ⚠️ Suspeita | J1 PASS 100%, 0 halluc, dens 0.02/p — sub-minerado; 3 mis-cit Ch.8 CAPM/Khandani fixadas | Densidade 0.02 cit/p — abaixo do limiar 1/20p; avaliar re-absorção enriquecida |
| `advances_fin_ml` | `⭐⭐⭐` Crítico | López de Prado | 489 | 119 | 96% | 🌟 Perfeita | J1 PASS 92% / J2 BORDER 88%, 0 halluc, dens 0.24/p | ⚠️ BORDERLINE adversarial (0 halluc); claim [p.148-149] já reescrito sem 2-3x Sharpe |
| `algo_trading_chan` | `⭐⭐` Importante | Chan | 225 | 131 | 100% | 🌟 Perfeita | J1 PASS 92% / J2 BORDER 75%, 0 halluc, dens 0.58/p, 4 mis-cit fixadas | ⚠️ BORDERLINE adversarial retry2 (0 halluc); 4 mis-cit corrigidas (VX, roll, momentum, stop-loss) |
| `big_data_ml_quant` | `⭐` Complementar | Guida (ed.) | 285 | 95 | 83% | ✅ Boa | J1 PASS 100%, 0 halluc, dens 0.33/p — sólido | — |
| `cybernetic_analysis` | `⭐⭐` Importante | Ehlers | 274 | 72 | 92% | ✅ Boa | J1 PASS 79%, 0 halluc, dens 0.26/p | — |
| `cybernetic_trading` | `⭐` Complementar | Ruggiero | 163 | 95 | 100% | ⚠️ Border | J1 BORDER 33% (amostra pequena, 0 halluc), dens 0.58/p | Ratio 100% em cit-check; juiz flagged vários paráfrases ambíguos — opcional re-validar |
| `cycle_analytics` | `⭐` Complementar | Ehlers | 252 | 59 | 88% | ✅ Boa | J1/J2 PASS 92%, 0 halluc, dens 0.23/p; EMA lag [p.35]→[p.19] fix FU-2 | — |
| `data_driven_science` | `⭐` Complementar | Brunton | 76 | 47 | 93% | 🌟 Perfeita | Sólido — 100% cit-check, dens 0.62/p; 1 fail FU-2 auto-resolvido pelo detector | — |
| `eval_opt_strategies` | `⭐⭐⭐` Crítico | Pardo | 367 | 97 | 100% | 🌟 Perfeita | J1 PASS 100% / J2 PASS 92%, 0 halluc, dens 0.26/p, 5 mis-cit fixadas | ✅ PASS retry3 (layer-2 clean); 5 mis-cit corrigidas (ver histórico) |
| `evidence_based_ta` | `⭐⭐` Importante | Aronson | 544 | 105 | 100% | 🌟 Perfeita | J1 PASS 100% / J2 PASS 97%, 0 halluc, dens 0.19/p | — |
| `fin_time_series_tsay` | `⭐⭐` Importante | Tsay | 714 | 36 | 88% | ✅ Boa | J1 PASS 100%, 0 halluc, dens 0.05/p — referência técnica enxuta | — |
| `leverage_space` | `⭐⭐` Importante | Vince | 206 | 46 | 100% | 🌟 Perfeita | J1 PASS 100%, 0 halluc, dens 0.22/p | — |
| `machine_trading` | `⭐⭐` Importante | Chan | 267 | 75 | 88% | ✅ Boa | J1 PASS 100%, 0 halluc, dens 0.28/p | — |
| `math_money_mgmt` | `⭐⭐` Importante | Vince | 109 | 16 | 97% | ✅ Boa | J1 PASS 100% / J2 BORDER 72%, 0 halluc; 2 mis-cit fixadas pós-FU-1 | Juiz J2 BORDERLINE (apenas ambíguas); 60 false fails eliminados por FU-1 |
| `ml_for_algo_trading` | `⭐⭐⭐` Crítico | Jansen | 821 | 190 | 93% | ✅ Boa | J1/J2 PASS 100%, 0 halluc, dens 0.23/p | — |
| `ml_for_asset_managers` | `⭐` Complementar | López de Prado | 45 | 39 | 82% | ✅ Boa | J1/J2 PASS 100%, 0 halluc, dens 0.87/p — muito denso | — |
| `numerical_recipes` | `⭐` Complementar | Press et al. | 1018 | 91 | 99% | ✅ Boa | J1/J2 PASS 100%, 0 halluc, dens 0.09/p — referência tomo | — |
| `quant_trading_chan` | `⭐⭐⭐` Crítico | Chan | 204 | 94 | 99% | 🌟 Perfeita | J1 PASS 100%, 0 halluc, dens 0.46/p | — |
| `regime_change` | `⭐⭐⭐` Crítico | Chen | 165 | 63 | 83% | ✅ Boa | J1 PASS 92% / J2 BORDER (pré-fix); Glattfelder 2008→2011 corrigido; 0 halluc reais | Re-validar J2 após fix Glattfelder (opcional; verdict atual stale) |
| `risk_parity` | `⭐` Complementar | Qian | 245 | 51 | 91% | ✅ Boa | J1/J2 BORDER 89%/86%, 0 halluc; paráfrases HY bonds flagged como ambiguous | — |
| `rocket_science` | `⭐` Complementar | Ehlers | 265 | 86 | 90% | ✅ Boa | J1 PASS 100%, 0 halluc, dens 0.32/p | — |
| `sentiment_analysis_handbook` | `⭐` Complementar | Mitra & Yu | 893 | 101 | 100% | 🌟 Perfeita | J1 PASS 100% / J2 PASS 92%, 0 halluc; 2 fails FU-2 auto-resolvidos | Ambiguidade interna p.705 (item 2, non-blocking) |
| `stat_sound_indicators` | `⭐⭐` Importante | Aronson | 519 | 116 | 100% | 🌟 Perfeita | J1 PASS 100%, 0 halluc, dens 0.22/p | — |
| `stocks_on_the_move` | `⭐⭐⭐` Crítico | Clenow | 249 | 61 | 97% | 🌟 Perfeita | J1 PASS 100%, 0 halluc, dens 0.24/p | — |
| `systematic_trading` | `⭐⭐⭐` Crítico | Carver | 326 | 91 | 99% | 🌟 Perfeita | J1/J2 PASS 92%, 0 halluc, dens 0.28/p, 4 mis-cit fixadas | ✅ PASS retry2 (layer-2 clean); 4 mis-cit corrigidas (ver histórico) |
| `tech_analysis_patterns` | `⭐` Complementar | Tsinaslanidis | 213 | 75 | 100% | ✅ Boa | J1/J2 BORDER 88%/83%, 0 halluc; 6 ambíguas (page-offs ≤13p não-bloqueantes) | Retry J2 opcional para limpar ambíguas de página (não bloqueia build) |
| `testing_tuning` | `⭐⭐` Importante | Masters | 353 | 119 | 80% | ✅ Boa | J1 PASS 90% / J2 BORDER 87%, 0 halluc; 6 ambíguas são page-off ≤6p | Ratio 80% estável após re-abs 2026-04-13 |
| `time_series_hamilton` | `⭐` Complementar | Hamilton | 814 | 87 | 98% | 🌟 Perfeita | J1/J2 BORDER 88%/88%, 0 halluc (self-consistency forte), dens 0.107/p | ⚠️ BORDERLINE adversarial (0 halluc); layer-2 limpo pós-`chapter_intro` warn |
| `trading_evolved` | `⭐⭐` Importante | Clenow | 467 | 111 | 91% | ✅ Boa | J1 PASS 100%, 0 halluc, dens 0.24/p | — |
| `trading_exchanges` | `⭐⭐` Importante | Harris | 113 | 129 | 91% | ✅ Boa | J1 PASS 92%, 0 halluc, dens 1.14/p — extremamente denso | — |
| `trading_systems_methods` | `⭐⭐⭐` Crítico | Kaufman | 1232 | 277 | 97% | 🌟 Perfeita | J1 PASS 92% / J2 BORDER 75%, 0 halluc pós-fix Market Profile; 28→277 cit | ⚠️ BORDERLINE retry3 (0 halluc); re-abs opus massiva concluída |
| `universal_trend_tactics` | `⭐` Complementar | Penfold | 409 | 75 | 100% | ✅ Boa | J1 PASS 90% / J2 BORDER 86%, 0 halluc, dens 0.18/p | — |
| `volatility_trading` | `⭐⭐` Importante | Sinclair | 298 | 130 | 80% | ✅ Boa | J1 BORDER 93% / J2 PASS 93%, 0 halluc pós-re-abs corretiva, dens 0.44/p | Ratio 80% estável; 9 halluc zeradas em re-abs corretiva 2026-04-13 |

**Resumo (2026-04-14 tarde):** 🌟 12 × Perfeita · ✅ 20 × Boa · ⚠️ 1 × Border (`cybernetic_trading` — only ambíguas, 0 halluc) · 🔴 0 × Sub-minerada  
**Importância:** `⭐⭐⭐` 7 × Crítico · `⭐⭐` 12 × Importante · `⭐` 14 × Complementar  
**Cit-check global:** 33/33 PASS (0 fails, ~40 warns, ~15 softs — todos esperados).

**Legendas complementares para a coluna Review:**
- `J1/J2 <verdict> Xx%` — support_ratio dos juízes adversariais (Layer-3); halluc = claims marcadas `unsupported`.
- `dens 0.Xy/p` — densidade de citações por página (referência: >0.20 é denso, <0.10 é enxuto, <0.05 é suspeito de mineração superficial).
- "mis-cit fixadas" — mis-citations corrigidas cirurgicamente nas sessões 2026-04-13/14.

> Colunas geradas em **2026-04-14** com `validate_summary.py --all` + `check_citations.py` em todos os 33 slugs, pós FU-1/2/3 e strict 100% halluc audit.
> Re-executar após cada re-absorção e atualizar a linha do livro afetado.

---

## 1. Cross-refs quebrados (alta prioridade) ✅ RESOLVIDO

Pointers entre summaries que apontam para arquivos inexistentes ou com nome errado.
Detectados por `scripts/validate_summary.py --all` + scan case-insensitive de `<slug>.md` nas seções 9.

### `books/summaries/cycle_analytics.md`
- [x] Linha 314: `trading_systems_methods.md` ✅ (corrigido na re-absorção 2026-04-13)
- [x] Linha 316: `quant_trading_chan.md` ✅ (corrigido)
- [x] Linha 318: `new_tech_trader.md` (LeBeau & Lucas) — resolvido com nota explícita "N/A: This slug does not exist in the current knowledge base. Chande and Kroll are referenced in Chapter 11 as the origin of VIDYA, but no corresponding summary file exists and no cross-reference can be established." Opção (b) escolhida — referência mantida com justificativa N/A. (Não absorver o livro: fora do escopo da base atual.)

### `books/summaries/time_series_hamilton.md`
- [x] Linha 383 (seção Cross-references): `analysis_financial_time_series.md` → renomear para `fin_time_series_tsay.md` *(corrigido na re-absorção 2026-04-13 retry 3 — agora linha 468 usa `fin_time_series_tsay.md`)*
- [x] Revisar nota "primeiro livro do pipeline; cross-refs serão adicionados em passes subsequentes" *(re-absorção 2026-04-13 retry 3 já enriqueceu cross-refs com `fin_time_series_tsay.md`, `numerical_recipes.md`, `advances_fin_ml.md`)*

### `books/summaries/trading_evolved.md`
- [x] Linha 314: `Systematic_trading.md` (S maiúsculo) → `systematic_trading.md` *(surfaced pelo scan case-insensitive em 2026-04-14; fix aplicado)*

**Scan final (2026-04-14):** `for s in books/summaries/*.md` + extract refs de seção 9 → 0 MISSING, 0 CASE MISMATCH. Todos os cross-refs resolvem para arquivos existentes.

**Regra:** preferir re-dispatch do `book-reader` a Edit manual, mesmo em cross-refs. Strings de pointer ainda são parte do summary; o rule-of-thumb "nunca modifique summary manualmente" reduz risco de introduzir drift silencioso.

---

## 2. Nota ambígua registrada pelo juiz adversarial

### `sentiment_analysis_handbook.md` (Judge #2)
- [ ] Inconsistência interna do próprio livro: novelty score em `p.705` define janela como "last 24 hours" mas o matching engine usa "last 12 hours". Summary capturou ambos — **não é hallucination**, é fidelidade ao fonte.
- Ação: nenhuma (flag informacional). Registrar em `books/summaries/.validation/KNOWN_AMBIGUITIES.md` se quisermos rastrear.

---

## 3. Verificações determinísticas finais ✅ EXECUTADO 2026-04-14

Rodar antes do build para confirmar que nada regrediu desde a última absorção:

- [x] `python scripts/validate_summary.py --all` → **33/33 PASS**, 10/10 seções em todos, nenhum `notes` não-vazio fora dos conhecidos.
- [x] `for s in books/summaries/*.md; do python scripts/check_citations.py "$(basename $s .md)" | tail -1; done` → **33/33 PASS** (0 fails, ~40 warns, ~15 softs esperados).
- [x] Paridade: `ls books/extracted/` = `ls books/summaries/*.md` = **33 = 33**.
- [x] `books/summaries/.progress.json` não existe — nenhuma wave pendente/interrompida.

---

## 4. Sanity checks de conteúdo ✅ VERIFICADO 2026-04-14

- [x] Cada summary tem **10/10 seções obrigatórias** preenchidas (Metadata + 9 seções). Nenhum N/A sem justificativa.
- [x] Citation ratio mínimo por livro: **80%** (threshold do `validate_summary.py`). Todos os 33 passam o threshold.
- [ ] **Ratios <85% (8 livros; opcional — não bloqueiam o build, são "considerar re-dispatch para enriquecer"):**
  - `testing_tuning` 80% *(re-abs 2026-04-13 — ratio estável; aceito)*
  - `volatility_trading` 80% *(re-abs corretiva 2026-04-13 zerou 9 halluc; ratio estável aceito)*
  - `eval_opt_strategies` 82% *(PASS retry3 com 100% J1, 92% J2, 0 halluc; aceito)*
  - `ml_for_asset_managers` 82% *(J1/J2 100%, 0 halluc; ratio baixo por ser livro enxuto 45p; aceito)*
  - `big_data_ml_quant` 83% *(J1 PASS 100%, 0 halluc; aceito)*
  - `regime_change` 83% *(Glattfelder 2008→2011 fix 2026-04-14; aceito)*

---

## 5. Higiene de repositório ✅ EXECUTADO 2026-04-14

- [x] `.gitignore` cobre `books/summaries/.validation/`, `.logs/`, `.progress.json`, `.progress.log`, `.progress.*.json.done`.
- [x] `.progress.1776077609.json.done` (runtime antigo de 2026-04-13) removido.
- [x] `books/README.md` reflete os 33 livros atuais (commit de hoje).
- [x] `.claude/commands/absorb-all-books.md` e `.claude/commands/validate-summary.md` alinhados com a pipeline de 3 camadas.

---

## 6. Metadados para o build_skill ✅ VERIFICADO 2026-04-14

Antes de gerar a skill, confirmar que cada summary expõe os campos esperados pelo `build_skill.py`:

- [x] `Autor` e `Ano` no bloco `## Metadata` — scan em todos os 33 summaries: 0 missing.
- [x] Seção `Cross-references` referencia apenas slugs existentes (scan case-insensitive: 0 MISSING, 0 CASE MISMATCH pós fix de `trading_evolved`).
- [x] Índice/TOC da skill não precisa entradas para livros externos não absorvidos (ex.: `new_tech_trader.md` marcado como N/A in-situ).

`build_skill.py` não oferece `--dry-run` (suporta `--skip-validation`), mas é determinístico e não faz LLM calls — efeito é reprodutível. Inspecionar output em `knowledge/` após o run e commitar.

---

## 7. Ordem sugerida de execução (atualizada 2026-04-14)

**Concluído:**
- ✅ Re-absorções P0/P1/P2 (10 livros): `math_money_mgmt`, `universal_trend_tactics`, `trading_systems_methods`, `time_series_hamilton`, `volatility_trading`, `eval_opt_strategies`, `regime_change`, `risk_parity`, `cycle_analytics`, `tech_analysis_patterns` — todos PASS em cit-check + structural; J1 ratios 0.875-1.0, J2 0.72-0.93, 0 hallucinations reais. Detalhes por livro na tabela **Status Geral dos Livros**.
- ✅ Cross-refs (item 1): todos corrigidos — `cycle_analytics`, `time_series_hamilton`, `trading_evolved` (case fix) — scan final 0 MISSING, 0 CASE MISMATCH.
- ✅ Decisão `new_tech_trader.md`: opção (b) — N/A com nota explícita.
- ✅ Camadas A/B/C de proteção contra `[Tool result missing]` — `scripts/aggregate_judges.py`, `summary-validator.md` shrink output, dispatch condicional por `est_tokens`.
- ✅ FU-1/2/3 zerados (2026-04-14): detector `n_chapters` fix + 4 livros com fails residuais corrigidos + convenção PT/EN documentada.
- ✅ Strict 100% halluc audit (2026-04-14): 5 livros revalidados, 1 halluc real corrigida (`regime_change` Glattfelder 2008→2011).
- ✅ Verificações finais (itens 3/4/5/6): 33/33 PASS em todos os checks, higiene de repositório limpa, metadados verificados.

**Próximos passos:**

1. `python scripts/build_skill.py` — determinístico, sem LLM calls.
2. Inspecionar o output em `knowledge/` (SKILL.md + books/ + strategies/ + indicators/ + validation/).
3. Commit final da skill gerada: "feat(knowledge): generate skill from 33-book base".

---

## Histórico

- **2026-04-14 (FU-1/2/3 + strict 100% halluc)**: Fix `compute_n_chapters_effective` em `check_citations.py` — usa `max(ch.N)` citado no summary como floor, desbloqueando `math_money_mgmt` (60 false fails → 0) e `advances_fin_ml` (4 → 0). 4 testes TDD. FU-2: `adaptive_markets`/`cycle_analytics` re-pageados; `data_driven_science`/`sentiment_analysis_handbook` auto-resolvidos. FU-3: convenção PT/EN em `book-reader.md`. Strict halluc: 1 fix em `regime_change` (Glattfelder 2011 per bibliografia Quant Finance 11:4).
- **2026-04-13 (onda P0/P1/P2 de re-absorções)**: 10 livros re-absorvidos em ordem priorizada para combater mineração superficial (densidade < 1 cit / 20p) e hallucinations detectadas por juízes adversariais. Ordem: `math_money_mgmt` → `universal_trend_tactics` → `time_series_hamilton` → `eval_opt_strategies`/`regime_change`/`risk_parity` → `cycle_analytics`/`tech_analysis_patterns` → `trading_systems_methods` (opus map_reduce, 28→277 cit) → `volatility_trading` (corretiva, 9 halluc → 0). Hints cirúrgicos usados estão preservados em `books/summaries/.logs/<slug>.log`.
- **2026-04-13 (Tier 2)**: Criado `scripts/build_page_index.py` — expõe o `build_offset_table` determinístico ao `book-reader` via `_page_index.json` por livro. Filtro de outliers por mediana-de-janela descarta ruído de páginas de índice/bibliografia. Rodado para `time_series_hamilton` (799/814 mapeadas, 98.2%, offset=15) e `trading_systems_methods` (1212/1232, 98.4%, offset=20). `.claude/agents/book-reader.md` atualizado para consumir o JSON no Passo 1 com fallback para heurística manual (livros antigos). Elimina a classe de retry observada em `volatility_trading.log` (offset não-uniforme).
- **2026-04-13**: Re-absorção de `ml_for_algo_trading` revelou bug no offset detector. Fix aplicado em `scripts/check_citations.py` (suporte a banner `[ N ]`). Summary expandido de 122→190 citações, 13→24 capítulos minerados, todas as 3 camadas PASS.

### Notas operacionais (para futuras re-absorções)

- **Tier 2**: `scripts/build_page_index.py` gera `_page_index.json` determinístico por livro. O `book-reader` consulta `pdf_to_printed[N]` em vez de re-derivar offset — elimina a maior classe de retries. Rodar UMA VEZ por livro antes do `/absorb-book`.
- O `/absorb-book` dispara o `book-reader` + `/validate-summary` (3 camadas). Wall-clock real: map_reduce com opus @ 600-685K tokens = ~13 min feliz path, 0 retries. Retry-hell sem `_page_index.json`: 1h30m+.
- Para livros `map_reduce` (>400k tokens): opus é necessário para priorização estratégica no reduce.
- Monitorar em paralelo: `tail -f books/summaries/.logs/<slug>.log` e `books/summaries/.progress.log`.
- Se retry 2+ ou wall-clock exceder o gate do livro: **parar**, investigar tipo de erro antes de retry 3 (que é caro e raramente resolve se os 2 primeiros falharam pelo mesmo motivo).
- Ratios <85% do validate_summary NÃO são bloqueantes para `build_skill` (threshold do validador é 80%); são sinais para "considerar re-dispatch para enriquecer" em uma próxima onda, não para esta.
