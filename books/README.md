# books/ — Knowledge Base dos Livros

Esta pasta contém os **33 livros absorvidos** que alimentam o "especialista em
trade" do ai-trade (Fase 0 do `TRADING_SYSTEM_PLAN.md`, **concluída**).

Pipeline:
`raw/<slug>.pdf` → `extracted/<slug>/` → `summaries/<slug>.md` (9 seções com
citação obrigatória `[p.X]`/`[ch.Y]`) → `../knowledge/SKILL.md` (Claude Skill
agregadora, gerada por `../scripts/build_skill.py`).

## Estrutura

```
books/
├── raw/              # PDFs com slugs canônicos (inventário em MAPPING.md)
├── extracted/        # texto extraído + capítulos + metadata (gitignored)
├── summaries/        # 1 MD validado por livro (versionado; gate via validate_summary)
├── code/             # código C++ complementar dos zips do Timothy Masters
│   ├── masters-assessing/         # Assessing and Improving Prediction (sem PDF)
│   └── masters-testing-tuning/    # complementa testing_tuning.pdf
├── MAPPING.md        # inventário canônico "nome original → slug" (gerado por rename_books.py)
└── README.md         # este arquivo
```

> **Compressão dos PDFs em `raw/`:** existe `../scripts/compress_pdfs.py` que
> tenta encolher os PDFs via Ghostscript, mas **só substitui o original se o
> texto extraído (via pymupdf) for equivalente palavra-a-palavra**. Na prática
> o Ghostscript re-renderiza streams de texto (normaliza caixa alta, junta
> espaços, troca ligaduras) e o script rejeita. Se precisar de ganho real em
> arquivos grandes (ex.: `evidence_based_ta.pdf`, `cycle_analytics.pdf`),
> o próximo passo é um recompressor baseado em `pikepdf` que toca apenas
> nos XObjects de imagem — fora de escopo até ser necessário.

---

## Catálogo dos livros (33/33 absorvidos)

Estado pós-pipeline completo (2026-04-14): **33/33 summaries PASS**
estrutural + `check_citations.py` (0 fails), com validação adversarial por
dois juízes LLM (Layer-3). Detalhes do pipeline em
`/home/victor/.claude/plans/synthetic-snuggling-wren.md`.

**Legenda de importância** (para swing trading CFD — Pepperstone/cTrader):
- `⭐⭐⭐` **Crítico** — no critical path do sistema; citado no plano ou impacta múltiplos módulos-chave
- `⭐⭐` **Importante** — impacta fortemente um módulo específico (strategy, sizing, validation, signals)
- `⭐` **Complementar** — background teórico, referência numérica, ou módulo periférico

**Legenda de qualidade:**
- 🌟 **Perfeita** — ratio ≥95% e densidade ≥0.10 cit/p
- ✅ **Boa** — ratio ≥87% e densidade adequada, sem re-absorção pendente
- ⚠️ **Regular** — ratio 80–86% ou densidade suspeita; re-absorção futura opcional
- 🔴 **Sub-minerada** — citações absolutas muito baixas (nenhum livro nesse estado)

| Slug | Importância | Autor | pp | Cit | Ratio | Qualidade | Review (absorção) |
|---|---|---|---|---|---|---|---|
| `adaptive_markets` | `⭐` | Lo | 503 | 10 | 89% | ⚠️ | J1 PASS 100%, 0 halluc, dens 0.02/p — sub-minerado; 3 mis-cit Ch.8 CAPM/Khandani fixadas. Flag futuro: considerar re-absorção enriquecida |
| `advances_fin_ml` | `⭐⭐⭐` | López de Prado | 489 | 119 | 96% | 🌟 | J1 PASS 92% / J2 BORDER 88%, 0 halluc, dens 0.24/p |
| `algo_trading_chan` | `⭐⭐` | Chan | 225 | 131 | 100% | 🌟 | J1 PASS 92% / J2 BORDER 75%, 0 halluc, dens 0.58/p, 4 mis-cit fixadas |
| `big_data_ml_quant` | `⭐` | Guida (ed.) | 285 | 95 | 83% | ✅ | J1 PASS 100%, 0 halluc, dens 0.33/p — sólido |
| `cybernetic_analysis` | `⭐⭐` | Ehlers | 274 | 72 | 92% | ✅ | J1 PASS 79%, 0 halluc, dens 0.26/p |
| `cybernetic_trading` | `⭐` | Ruggiero | 163 | 95 | 100% | ⚠️ | J1 BORDER 33% (amostra pequena, 0 halluc), dens 0.58/p |
| `cycle_analytics` | `⭐` | Ehlers | 252 | 59 | 88% | ✅ | J1/J2 PASS 92%, 0 halluc, dens 0.23/p; EMA lag fixado |
| `data_driven_science` | `⭐` | Brunton | 76 | 47 | 93% | 🌟 | 100% cit-check, dens 0.62/p |
| `eval_opt_strategies` | `⭐⭐⭐` | Pardo | 367 | 97 | 100% | 🌟 | J1 PASS 100% / J2 PASS 92%, 0 halluc, dens 0.26/p, 5 mis-cit fixadas |
| `evidence_based_ta` | `⭐⭐` | Aronson | 544 | 105 | 100% | 🌟 | J1 PASS 100% / J2 PASS 97%, 0 halluc, dens 0.19/p |
| `fin_time_series_tsay` | `⭐⭐` | Tsay | 714 | 36 | 88% | ✅ | J1 PASS 100%, 0 halluc, dens 0.05/p — referência técnica enxuta |
| `leverage_space` | `⭐⭐` | Vince | 206 | 46 | 100% | 🌟 | J1 PASS 100%, 0 halluc, dens 0.22/p |
| `machine_trading` | `⭐⭐` | Chan | 267 | 75 | 88% | ✅ | J1 PASS 100%, 0 halluc, dens 0.28/p |
| `math_money_mgmt` | `⭐⭐` | Vince | 109 | 16 | 97% | ✅ | J1 PASS 100% / J2 BORDER 72%, 0 halluc; 2 mis-cit fixadas pós FU-1 |
| `ml_for_algo_trading` | `⭐⭐⭐` | Jansen | 821 | 190 | 93% | ✅ | J1/J2 PASS 100%, 0 halluc, dens 0.23/p |
| `ml_for_asset_managers` | `⭐` | López de Prado | 45 | 39 | 82% | ✅ | J1/J2 PASS 100%, 0 halluc, dens 0.87/p — muito denso |
| `numerical_recipes` | `⭐` | Press et al. | 1018 | 91 | 99% | ✅ | J1/J2 PASS 100%, 0 halluc, dens 0.09/p — referência tomo |
| `quant_trading_chan` | `⭐⭐⭐` | Chan | 204 | 94 | 99% | 🌟 | J1 PASS 100%, 0 halluc, dens 0.46/p |
| `regime_change` | `⭐⭐⭐` | Chen | 165 | 63 | 83% | ✅ | J1 PASS 92%; Glattfelder 2008→2011 fixado; 0 halluc reais |
| `risk_parity` | `⭐` | Qian | 245 | 51 | 91% | ✅ | J1/J2 BORDER 89%/86%, 0 halluc; paráfrases HY bonds ambíguas |
| `rocket_science` | `⭐` | Ehlers | 265 | 86 | 90% | ✅ | J1 PASS 100%, 0 halluc, dens 0.32/p |
| `sentiment_analysis_handbook` | `⭐` | Mitra & Yu | 893 | 101 | 100% | 🌟 | J1 PASS 100% / J2 PASS 92%, 0 halluc |
| `stat_sound_indicators` | `⭐⭐` | Aronson | 519 | 116 | 100% | 🌟 | J1 PASS 100%, 0 halluc, dens 0.22/p |
| `stocks_on_the_move` | `⭐⭐⭐` | Clenow | 249 | 61 | 97% | 🌟 | J1 PASS 100%, 0 halluc, dens 0.24/p |
| `systematic_trading` | `⭐⭐⭐` | Carver | 326 | 91 | 99% | 🌟 | J1/J2 PASS 92%, 0 halluc, dens 0.28/p, 4 mis-cit fixadas |
| `tech_analysis_patterns` | `⭐` | Tsinaslanidis | 213 | 75 | 100% | ✅ | J1/J2 BORDER 88%/83%, 0 halluc; 6 page-offs ≤13p não-bloqueantes |
| `testing_tuning` | `⭐⭐` | Masters | 353 | 119 | 80% | ✅ | J1 PASS 90% / J2 BORDER 87%, 0 halluc; 6 ambíguas page-off ≤6p |
| `time_series_hamilton` | `⭐` | Hamilton | 814 | 87 | 98% | 🌟 | J1/J2 BORDER 88%/88%, 0 halluc, dens 0.107/p |
| `trading_evolved` | `⭐⭐` | Clenow | 467 | 111 | 91% | ✅ | J1 PASS 100%, 0 halluc, dens 0.24/p |
| `trading_exchanges` | `⭐⭐` | Harris | 113 | 129 | 91% | ✅ | J1 PASS 92%, 0 halluc, dens 1.14/p — extremamente denso |
| `trading_systems_methods` | `⭐⭐⭐` | Kaufman | 1232 | 277 | 97% | 🌟 | J1 PASS 92% / J2 BORDER 75%, 0 halluc pós fix Market Profile |
| `universal_trend_tactics` | `⭐` | Penfold | 409 | 75 | 100% | ✅ | J1 PASS 90% / J2 BORDER 86%, 0 halluc, dens 0.18/p |
| `volatility_trading` | `⭐⭐` | Sinclair | 298 | 130 | 80% | ✅ | J1 BORDER 93% / J2 PASS 93%, 0 halluc pós re-abs corretiva, dens 0.44/p |

**Resumo:** 🌟 12 × Perfeita · ✅ 20 × Boa · ⚠️ 1 × Border (`cybernetic_trading` — só ambíguas, 0 halluc) · 🔴 0 × Sub-minerada.
**Importância:** `⭐⭐⭐` 7 · `⭐⭐` 12 · `⭐` 14.
**Cit-check global:** 33/33 PASS (0 fails).

**Notas sobre a coluna Review:**
- `J1/J2 <verdict> Xx%` = support_ratio dos juízes adversariais (Layer-3); halluc = claims marcadas `unsupported`.
- `dens 0.Xy/p` = densidade de citações por página (referência: >0.20 denso, <0.10 enxuto, <0.05 mineração superficial).
- "mis-cit fixadas" = mis-citations corrigidas cirurgicamente durante re-absorções.
- BORDERLINE adversarial com 0 halluc e ratio ≥80% **não** bloqueia `build_skill` — são paráfrases/page-offs documentados.

**Livros deliberadamente não absorvidos** (registrados em `MAPPING.md`):
- `permutation_tests` (Masters) — coberto por `stat_sound_indicators` + `testing_tuning` (mesmo autor).
- `assessing_prediction` (Masters) — idem; código C++ está em `code/masters-assessing/`.
- `trading_on_sentiment` (Peterson) — substituído por `sentiment_analysis_handbook` (Mitra & Yu 2016).
- `new_tech_trader` (LeBeau & Lucas) — referenciado por `cycle_analytics` como origem do VIDYA; cross-ref mantida com nota `N/A`.

---

## Pipeline (como reproduzir / re-absorver)

Pré-requisito: `.venv/` ativo com deps (`uv sync` na raiz). Scripts em `../scripts/`.

### Re-absorver UM livro

```
/absorb-book <slug>
```

Dispara o subagente `book-reader` (em `../.claude/agents/book-reader.md`) sobre
`extracted/<slug>/`, reescreve `summaries/<slug>.md` e valida via 3 camadas
(estrutural + determinística + 2 juízes adversariais com self-consistency).

### Absorver em massa

```
/absorb-all-books
```

Dispara em ondas paralelas de 2-3 agentes (via
`superpowers:dispatching-parallel-agents`). Livros com PDF incompleto são
pulados automaticamente (sem `_metadata.json`).

### Validar

```bash
../.venv/bin/python ../scripts/validate_summary.py --all
../.venv/bin/python ../scripts/check_citations.py <slug>    # por livro
```

Regras: ≥80% das asserções com `[p.X]`/`[ch.Y]`; 9 seções presentes
(`N/A — <razão>` conta como presente); metadata com autor e ano.

### Regerar a Skill

```bash
../.venv/bin/python ../scripts/build_skill.py
```

Determinístico (zero LLM calls). Popula `../knowledge/`:
- `SKILL.md` (mestre — frontmatter + regras invioláveis + índice)
- `books/` (cópia dos 33 summaries validados)
- `strategies/`, `indicators/`, `validation/` (agregações temáticas)

### Antes de qualquer re-absorção: Tier 2

Rodar **uma vez por livro** para gerar `_page_index.json` (offset PDF↔impresso
determinístico — elimina a maior classe de retries do book-reader):

```bash
../.venv/bin/python ../scripts/build_page_index.py <slug>
```

---

## Arquivos legados na raiz de `books/` (podem ser removidos)

Os arquivos abaixo ficaram na raiz de `books/` após a migração para `raw/`.
**Nenhum deles é usado pelo pipeline** e podem ser removidos com segurança:

| Arquivo | Motivo |
|---|---|
| `assessing-and-improving-prediction-and-classification-master.zip` | Já extraído em `code/masters-assessing/` |
| `testing-and-tuning-market-trading-systems-master.zip` | Já extraído em `code/masters-testing-tuning/` |
| `brent-penfold-the-universal-principles-of-successful-tradingpdf_compress.pdf` | Livro **diferente** do que está na lista (Universal *Principles* 2010, não Universal *Tactics* 2020). Fora de escopo |
| `pdfcoffee.com_brent-penfold-the-universal-principles-of-successful-tradingpdf-pdf-free.pdf` | Duplicata exata do anterior |
| `The Universal Tactics of Successful Trend Trading - 2020 - Penfold - Front Matter.pdf` | Front matter apenas — substituído pelo PDF completo em `raw/universal_trend_tactics.pdf` |
| `Permutation Tests (Masters 2020).pdf` | **Não é** o livro do Masters — é Bachelor Thesis da Univ. Sevilla (2021). Tópico coberto por AFML + Testing & Tuning + código C++ |
| `Statistically_Sound_Machine_Learning_for.pdf` | Preview pequeno (454KB) — livro completo em `raw/stat_sound_indicators.pdf` |

Em `raw/` também há uma duplicata de edição anterior: `volatility_trading_2008.pdf`
(1ª ed, 2008) — o canônico absorvido é `volatility_trading.pdf` (2ª ed, 2013).
Pode ser removido.

---

## Troubleshooting

**`extract_pdfs.py` lança `ScannedPDFError`**
- O PDF não tem camada de texto (é imagem escaneada).
- Substitua por uma versão com OCR e rode de novo. Pipeline é idempotente.

**`extract_pdfs.py` lança `IncompleteBookError`**
- PDF tem <50 páginas e não tem TOC → provavelmente front matter / preview.
- Substitua pelo livro completo. Idem, idempotente.

**`validate_summary.py` retorna FAIL**
- Leia a saída: citation ratio baixo ou seção faltando.
- **NÃO edite o summary manualmente.** Re-dispare o agente com feedback
  específico (ex: "seção 3 com 4 fórmulas sem citação, corrija").

**`check_citations.py` reporta mis-citations**
- Quase sempre é offset PDF↔impresso. Rode `build_page_index.py <slug>`
  primeiro; depois re-dispare `/absorb-book <slug>` se o índice ficar muito
  diferente do usado na absorção original.

**Book-reader estoura contexto em livro grande**
- `_metadata.json` deveria ter marcado `recommended_mode: "map_reduce"`.
- Se não marcou, ajuste o threshold em `../scripts/extract_pdfs.py`
  (atualmente 400K tokens estimados para ativar map-reduce).

---

## Referências

- Plano geral do sistema: `../TRADING_SYSTEM_PLAN.md`
- Roadmap / estado das fases: `../ROADMAP.md`
- Plano da Fase 0: `/home/victor/.claude/plans/synthetic-snuggling-wren.md`
- Inventário canônico dos livros: `MAPPING.md`
- Summaries validados: `summaries/*.md`
- Auditoria de validação: `summaries/.validation/` (gitignored)
- Logs de absorção: `summaries/.logs/` (gitignored)
- Skill gerada: `../knowledge/SKILL.md`
