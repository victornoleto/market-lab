# ai-trade — Fase 0: Knowledge Base a partir dos Livros

Pipeline que absorve 23 livros de trading algorítmico/ML quantitativa em uma
**Claude Skill** (`knowledge/SKILL.md`) consumível pelo Claude Code. Esta é a
Fase 0 do `TRADING_SYSTEM_PLAN.md` — pré-requisito das Fases 1-7 (data pipeline,
strategy engine, backtest, paper, live).

**Regra de ouro:** nenhuma afirmação sem referência ao livro (`[p.X]` ou
`[ch.Y]`). Alucinação destrói o valor da knowledge base.

---

## Arquitetura

```
Python (determinístico)         Claude Code (LLM)           Python (agrega)
┌─────────────────┐            ┌──────────────────┐        ┌────────────────┐
│ rename_books.py │            │  book-reader     │        │ build_skill.py │
│ extract_pdfs.py │ ──────────▶│  subagente       │───────▶│                │
│                 │   texto     │  (.claude/       │ summary│ knowledge/     │
│                 │   +         │   agents/)       │        │  SKILL.md      │
│                 │   chapters  │                  │        │  books/        │
│                 │             │  9 seções,       │        │  strategies/   │
│                 │             │  cite [p.X]      │        │  indicators/   │
│                 │             │                  │        │  validation/   │
└─────────────────┘            └──────────────────┘        └────────────────┘
      ↓                                                            ↑
validate_summary.py ─────────────────────────────────────────────────┘
(gate: rejeita summary sem citações)
```

Python NÃO usa Claude API. Toda inteligência LLM roda dentro do **Claude Code CLI**.

---

## Requisitos

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recomendado) ou `pip`
- Claude Code CLI instalado com o plugin `superpowers` (para
  `dispatching-parallel-agents`)

---

## Setup

```bash
cd /var/www/pessoal/ai-trade

# Instala deps Python (apenas pymupdf, pdfplumber, rich)
uv sync
# ou: python -m venv .venv && .venv/bin/pip install -e .
```

---

## Pipeline (ordem de execução)

### 1. Preparar PDFs

```bash
# Os PDFs originais já estão em books/ (nomes inconsistentes).
# rename_books.py mapeia cada arquivo ao seu slug canônico e move para books/raw/
python scripts/rename_books.py

# Gera também books/MAPPING.md (inventário human-readable)
```

### 2. Extrair companion code dos zips

```bash
python scripts/rename_books.py --unzip-only
# Cria books/code/masters-assessing/ e books/code/masters-testing-tuning/
```

### 3. Extrair texto dos PDFs

```bash
python scripts/extract_pdfs.py
# Gera books/extracted/<slug>/_full.txt + chapters/NN.txt + _metadata.json
#
# Se detectar PDF escaneado (>20% das páginas com <100 palavras),
# aborta com ScannedPDFError listando páginas problemáticas.
# Substitua o PDF e re-execute.
```

### 4. Absorver um livro (via Claude Code)

Abra o Claude Code neste projeto e rode:

```
/absorb-book systematic_trading
```

O subagente `book-reader` vai ler `books/extracted/systematic_trading/` e
produzir `books/summaries/systematic_trading.md` com o template de 9 seções.

**Valide manualmente o primeiro livro** antes de processar os outros em batch —
é o gate human-in-the-loop.

### 5. Validar summary

```bash
python scripts/validate_summary.py systematic_trading
# Rejeita se <80% das asserções faltam citação [p.X]/[ch.Y]
# ou se faltar alguma das 9 seções (sem N/A justificado)
```

### 6. Absorver todos os livros em batch

No Claude Code:

```
/absorb-all-books
```

Dispara os 22 restantes em ondas de 4-6 paralelos
(via `superpowers:dispatching-parallel-agents`). Cada summary é validado
automaticamente após o agente terminar.

### 7. Agregar em knowledge/

```bash
python scripts/build_skill.py
# Copia summaries/ → knowledge/books/
# Agrega por tema em knowledge/{strategies,indicators,validation}/
# Inclui cross-refs para books/code/*.cpp onde relevante
# Gera knowledge/SKILL.md com frontmatter
```

### 8. Testar a Skill

No Claude Code, invoque:

```
Skill trading-knowledge
```

e pergunte, por exemplo:
> "Qual é o PBO (Probability of Backtest Overfitting) e quando descartar uma estratégia?"

A resposta deve citar `advances_fin_ml.md` e `validation/cpcv.md`.

---

## Lista dos 23 Livros

| # | Slug | Título | Autor | Ano |
|---|---|---|---|---|
| 1 | `systematic_trading` | Systematic Trading | Carver | 2015 |
| 2 | `trading_systems_methods` | Trading Systems and Methods (5th ed) | Kaufman | 2013 |
| 3 | `advances_fin_ml` | Advances in Financial Machine Learning | López de Prado | 2018 |
| 4 | `leverage_space` | The Leverage Space Trading Model | Vince | 2009 |
| 5 | `math_money_mgmt` | The Mathematics of Money Management | Vince | 1992 |
| 6 | `rocket_science` | Rocket Science for Traders | Ehlers | 2001 |
| 7 | `cybernetic_analysis` | Cybernetic Analysis for Stocks and Futures | Ehlers | 2004 |
| 8 | `cycle_analytics` | Cycle Analytics for Traders | Ehlers | 2013 |
| 9 | `stat_sound_indicators` | Statistically Sound Machine Learning for Algorithmic Trading | Aronson & Masters | 2013 |
| 10 | `universal_trend_tactics` | Universal Tactics of Successful Trend Trading | Penfold | 2020 |
| 11 | `stocks_on_the_move` | Stocks on the Move | Clenow | 2015 |
| 12 | `cybernetic_trading` | Cybernetic Trading Strategies | Ruggiero | 1997 |
| 13 | `testing_tuning` | Testing and Tuning Market Trading Systems | Masters | 2018 |
| 14 | `numerical_recipes` | Numerical Recipes in C (2nd ed) | Press et al. | 1992 |
| 15 | `data_driven_science` | Data-Driven Science and Engineering | Brunton & Kutz | 2021 |
| 16 | `tech_analysis_patterns` | Technical Analysis for Algorithmic Pattern Recognition | Tsinaslanidis | 2016 |
| 17 | `regime_change` | Detecting Regime Change in Computational Finance | Chen & Tsang | 2020 |
| 18 | `trading_on_sentiment` | Trading on Sentiment | Peterson | 2016 |
| 19 | `evidence_based_ta` | Evidence-Based Technical Analysis | Aronson | 2007 |
| 20 | `trading_evolved` | Trading Evolved | Clenow | 2019 |
| 21 | `ml_for_asset_managers` | Machine Learning for Asset Managers | López de Prado | 2020 |
| 22 | `ml_for_algo_trading` | Machine Learning for Algorithmic Trading | Jansen | 2020 |

Código C++ complementar:
- `books/code/masters-assessing/` — Assessing and Improving Prediction (Masters 2013, PDF indisponível; código é a fonte primária)
- `books/code/masters-testing-tuning/` — Testing and Tuning (Masters 2018, complementa o PDF)

---

## Troubleshooting

**`extract_pdfs.py` lança `ScannedPDFError`:**
- Significa que o PDF não tem camada de texto (é imagem escaneada).
- Substitua por uma versão com OCR ou cópia digital. O pipeline **não** tenta OCR automaticamente (evita degradar qualidade silenciosamente).

**`validate_summary.py` rejeita o summary:**
- Leia o diagnóstico. Causas comuns:
  - Asserções sem `[p.X]` — ajuste o prompt do book-reader para ser mais rigoroso.
  - Seção faltando — agente precisa escrever `N/A — <razão>`, não omitir.
- Depois de ajustar o prompt, re-rode `/absorb-book <slug>`.

**Book-reader estoura contexto em livro grande:**
- `_metadata.json` deveria ter marcado `recommended_mode: "map_reduce"`.
- Se não marcou, ajuste o threshold em `extract_pdfs.py` (atualmente 400K tokens estimados).

---

## Referências

- Plano geral do sistema: `TRADING_SYSTEM_PLAN.md`
- Plano da Fase 0: `/home/victor/.claude/plans/synthetic-snuggling-wren.md`
- Plano aprovado anterior (base): `/home/victor/.claude/plans/mighty-mixing-porcupine.md`
