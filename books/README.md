# books/ — Knowledge Base dos Livros

Esta pasta contém os 31 livros que alimentam o "especialista em trade" do ai-trade
(Fase 0 do `TRADING_SYSTEM_PLAN.md`): 22 originais + 9 adicionados conforme
`ai-trade-library-audit.md`.

## Estrutura

```
books/
├── raw/              # 31 PDFs com slugs canônicos (gitignored)
├── extracted/        # texto extraído + capítulos + metadata (gitignored, cache)
├── summaries/        # 1 MD validado por livro, saída do subagente book-reader (versionado)
├── code/             # código C++ complementar dos zips do Timothy Masters (versionado)
│   ├── masters-assessing/         # Assessing and Improving Prediction (sem PDF)
│   └── masters-testing-tuning/    # complementa testing_tuning.pdf
├── MAPPING.md        # inventário "nome original → slug" (gerado por rename_books.py)
└── README.md         # este arquivo
```

Para a lista completa dos 31 livros com autor/ano/tier, veja `MAPPING.md`.

---

## Passo a passo (do zero ao knowledge base pronto)

Pré-requisito: `.venv/` ativo com deps instaladas (`uv sync` na raiz). Os
scripts referenciados estão em `../scripts/`.

### 1. (Opcional) Substituir o livro incompleto restante

Falta **apenas 1** livro com PDF incompleto (front matter de 30pp):

- `trading_on_sentiment.pdf` (Peterson 2016, precisa ~400pp)
  - **Título completo:** *Trading on Sentiment: The Power of Minds Over Markets*
  - **Editora:** Wiley Finance
  - **ISBN:** 978-1-119-12276-0
  - Onde procurar: Wiley, archive.org, libraries acadêmicas

Quando conseguir o PDF completo: substitua em `raw/trading_on_sentiment.pdf` e
rode `../.venv/bin/python ../scripts/extract_pdfs.py --slug trading_on_sentiment --force`.

O pipeline é idempotente — pode rodar agora sem ele e adicionar depois.

**Histórico:** 3 outros livros (`cybernetic_analysis`, `cycle_analytics`,
`regime_change`) tinham o mesmo problema e já foram substituídos pelas
versões completas.

### 2. Absorver o PRIMEIRO livro como calibração ⭐

Abra o Claude Code no diretório raiz do projeto e execute:

```
/absorb-book systematic_trading
```

Isso dispara o subagente `book-reader` (em `../.claude/agents/book-reader.md`),
que lê `extracted/systematic_trading/` e produz `summaries/systematic_trading.md`
seguindo o template de 9 seções com **citações obrigatórias** (`[p.X]` / `[ch.Y]`).

Ao final o agente auto-valida via `validate_summary.py`.

### 3. REVISAR manualmente o primeiro summary (gate human-in-the-loop)

Abra `summaries/systematic_trading.md` e verifique:

- [ ] Título correto da capa
- [ ] Metadata preenchida com autor/ano/páginas reais (nada chutado)
- [ ] Fórmulas em LaTeX com `[p.X]`
- [ ] Regras de trading com `[p.X]`
- [ ] Nenhuma fórmula/regra que você sabe que não existe no Carver
- [ ] Seções vazias marcadas `N/A — <razão>`, não omitidas

**Se algo estiver errado**: reporte ao Claude Code e peça para re-disparar o
agente com o feedback específico. Não edite o summary manualmente — o
valor do pipeline está na reprodutibilidade.

### 4. Absorver 1-2 livros com cross-refs

Depois que o primeiro passar, rode mais um para validar que cross-refs (seção 9)
funcionam corretamente:

```
/absorb-book advances_fin_ml
```

Esse deve referenciar `systematic_trading.md` ao falar de parcimônia/design.
Se referenciar livros que ainda não foram processados → bug no agente.

### 5. Batch dos 15 restantes

```
/absorb-all-books
```

Dispara em ondas paralelas de 4-6 agentes (via
`superpowers:dispatching-parallel-agents`). Os 4 livros incompletos são
pulados automaticamente (não têm `_metadata.json`).

### 6. Validar o conjunto

```bash
../.venv/bin/python ../scripts/validate_summary.py --all
```

Tabela com PASS/FAIL por livro. Regras:
- ≥80% das asserções precisam ter citação `[p.X]` ou `[ch.Y]`.
- 9 seções presentes (com `N/A — <razão>` contando como presente).
- Metadata com autor e ano.

### 7. Construir o knowledge base final

```bash
../.venv/bin/python ../scripts/build_skill.py
```

Popula `../knowledge/`:
- `SKILL.md` (mestre, com frontmatter + regras invioláveis)
- `books/` (1 MD por livro, cópia dos summaries)
- `strategies/`, `indicators/`, `validation/` (agregações temáticas com
  cross-refs para os summaries + `books/code/*.cpp` quando relevante)

### 8. Testar

No Claude Code, invoque a skill e pergunte algo canônico:

> "Qual é o PBO (Probability of Backtest Overfitting) e quando devo descartar
> uma estratégia?"

Resposta boa cita `books/advances_fin_ml.md#cpcv` + `validation/cpcv.md` +
limiar PBO > 50%.

---

## Arquivos legados na raiz de `books/` (podem ser removidos)

Os arquivos abaixo ficaram na raiz de `books/` após a migração para `raw/`.
**Nenhum deles é usado pelo pipeline** e podem ser removidos com segurança:

| Arquivo | Motivo |
|---|---|
| `assessing-and-improving-prediction-and-classification-master.zip` | Já extraído em `code/masters-assessing/` |
| `testing-and-tuning-market-trading-systems-master.zip` | Já extraído em `code/masters-testing-tuning/` |
| `brent-penfold-the-universal-principles-of-successful-tradingpdf_compress.pdf` | Livro **diferente** do que está na lista (Universal *Principles* 2010, não Universal *Tactics* 2020). Fora de escopo |
| `pdfcoffee.com_brent-penfold-the-universal-principles-of-successful-tradingpdf-pdf-free.pdf` | Duplicata exata do anterior (mesmos 61MB) |
| `The Universal Tactics of Successful Trend Trading - 2020 - Penfold - Front Matter.pdf` | Apenas front matter, substituído pelo PDF completo em `raw/universal_trend_tactics.pdf` |
| `Permutation Tests (Masters 2020).pdf` | **Não é** o livro do Masters — é uma Bachelor Thesis da Univ. de Sevilla (2021). Tópico coberto por AFML + Testing & Tuning + código C++ em `code/` |
| `Statistically_Sound_Machine_Learning_for.pdf` | Preview pequeno (454KB) — o livro completo já está em `raw/stat_sound_indicators.pdf` |

Para limpar de uma vez:

```bash
cd books/
rm assessing-and-improving-prediction-and-classification-master.zip \
   testing-and-tuning-market-trading-systems-master.zip \
   brent-penfold-the-universal-principles-of-successful-tradingpdf_compress.pdf \
   pdfcoffee.com_brent-penfold-the-universal-principles-of-successful-tradingpdf-pdf-free.pdf \
   "The Universal Tactics of Successful Trend Trading - 2020 - Penfold - Front Matter.pdf" \
   "Permutation Tests (Masters 2020).pdf" \
   Statistically_Sound_Machine_Learning_for.pdf
```

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
- NÃO edite o summary manualmente. Re-dispare o agente com feedback
  específico (ex: "seção 3 com 4 fórmulas sem citação, corrija").

**Book-reader estoura contexto em livro grande**
- `_metadata.json` deveria ter marcado `recommended_mode: "map_reduce"`.
- Se não marcou, ajuste o threshold em `../scripts/extract_pdfs.py`
  (atualmente 400K tokens estimados para ativar map-reduce).

---

## Referências

- Plano geral do sistema: `../TRADING_SYSTEM_PLAN.md`
- Plano desta fase: `/home/victor/.claude/plans/synthetic-snuggling-wren.md`
- README do projeto: `../README.md`
- Mapa dos 22 livros: `MAPPING.md`
