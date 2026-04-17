# Investment Mandate registrado — direção agressiva pós-winners

Os 2 winners entregues pelo loop autônomo hoje (BollingerMR SPY 1h com
CAGR 5.9% e ETFRotation monthly top-1 com CAGR líquido 9.1-9.6%) são
tecnicamente sólidos — passam PBO, DSR, WF, OOS e stress — mas os
retornos são **insuficientes** para justificar o esforço científico
deste projeto. O CDI brasileiro paga ~13-14% ao ano sem risco.

O usuário fez a avaliação honesta: **"eu estou muito feliz e satisfeito
que conseguimos encontrar estratégias vencedoras, mas no entanto ainda
não é suficiente"**. A partir dessa frustração produtiva, nasce o
Investment Mandate.

## O que é o Mandate

Um documento permanente em `docs/investment-mandate.md` que define as
regras invioláveis de todo trabalho futuro no projeto. Resumo
sempre-carregado via `.claude/CLAUDE.md §📌 Investment Mandate` (nova
seção).

### Os 7 pontos invioláveis

1. **Capital allocation:** 60-80% em buy&hold passivo (governado por
   `portfolio-aposentadoria.md` — AVUS/SPMO/AVUV/AVDE/IDMO/AVDV/AVEM +
   IBIT + GLDM), 20-40% dividido entre 2 strategies ativas.
2. **CAGR mínimo = CDI BR (~13-14%/ano líquido).** Strategies abaixo
   desse chão são folclore, não produto.
3. **Strategy A (Pepperstone CFD)** precisa ser multi-asset obrigatório
   (SPY/QQQ/Gold/BTC/ETH/FX majors), com universe pre-screening
   (Hurst/ATR/spread/volume), e alavancagem ótima determinada via
   sweep empírico 1:1 → 1:200 cruzado com Kelly f/2 + prob-of-ruin MC.
   Target: **5-10%/mês a partir de $1k**.
4. **Strategy B (swing broker)** tese primária: **LETF rotation**
   (SPY-SMA → UPRO 3x / CASH), baseada em Gayed 2016/2020 —
   `books/summaries/leverage_for_the_long_run.md`. CPCV+PBO obrigatório
   nos params seed do usuário (EMA 125, band 5%); 15% IR sempre
   modelado; UPRO sintético pre-2009. Target: ≥15%/ano, ideal ≥20%.
5. **Gates sempre:** PBO<0.5 + DSR p<0.05 + WF≥6/8 + OOS + stress.
   Zero bypass.
6. **Threading model (Phase 4 live):** 1 thread por ativo monitorado,
   state isolado, perks opcionais por ativo (FX session filter, equity
   pre/post-market, news filter gold, crypto 24/7).
7. **Dynamic sizing:** position size decresce com equity — fase
   agressiva até 2× equity inicial, fase preservação depois.

### Anti-patterns proibidos

- Single-asset edges como winners finais de Strategy A.
- Strategy B = buy&hold não alavancado.
- CAGR < CDI BR tratado como winner.
- Gate bypass por "quase lá".
- Alavancagem sem prob-of-ruin.
- Retroajuste de params pós-OOS.
- Commit de Bearer tokens / credentials em qualquer arquivo.

## O que mais foi feito hoje (pós-winners)

1. **34º livro absorvido:** `leverage_for_the_long_run.pdf` (Michael
   Gayed 2016/2020, SSRN working paper). Modelo sonnet, 13k tokens,
   single_pass. Validação: J1 PASS 92% / J2 BORDER 75%, 3 page-off
   halluc menores (non-blocking). Catalog atualizado em
   `books/README.md` + `books/MAPPING.md`.
2. **Spec de cleanup atualizado** (`specs/post-winners-cleanup.md`)
   com Task 0 retrospectivo (já executado hoje) + §2 Preservation
   inclui mandate/portfolio/book refs + §7 citation audit força 4
   slugs protegidos + §8 reescrito com 5 Phase 3 leads (A1-A3, B1-B2)
   derivados do mandate.
3. **ROADMAP.md** atualizado: headline reflete 2 winners + mandate;
   nova seção "Post-cleanup evolution (Phase 3 leads)" com a tabela
   dos 5 leads.
4. **Placeholders** para o próprio usuário preencher antes de executar
   Lead B1:
   - `docs/reference/letf_rotation_testfol_payload.json` — payload
     do testfol.io (sem Bearer token).
   - `docs/reference/letf_rotation_reddit_analysis.md` — conteúdo do
     post do Reddit (WebFetch bloqueado).

## O que vem a seguir

Próxima sessão:
1. Executar o cleanup propriamente dito (tasks §4-§10 do spec).
2. Merge pra `main` com autorização explícita.
3. Preencher os 2 placeholders (testfol payload + Reddit post).
4. Criar branch `phase3/letf-and-multi-asset-<date>`.
5. Disparar o self-improve loop com os 5 leads nova memory.

## Links

- `docs/investment-mandate.md` — mandate completo
- `.claude/CLAUDE.md §📌 Investment Mandate` — sumário sempre-carregado
- `specs/post-winners-cleanup.md` — spec de cleanup atualizado
- `portfolio-aposentadoria.md` — compartimento passive 60-80%
- `books/summaries/leverage_for_the_long_run.md` — tese Strategy B
- `jornada/2026-04-16-1600-production-readiness-summary.md` — os 2
  winners que originaram a decisão de elevar a barra
