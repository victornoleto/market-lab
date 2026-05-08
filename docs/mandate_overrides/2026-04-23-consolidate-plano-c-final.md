# Mandate override — CONSOLIDAR PLANO C / fechar slots ativos

**Data:** 2026-04-23
**Proposto por:** Claude Code (após Phase E-MVP falhar 42/42; cumulativo 113/113)
**Status:** ✅ **Signed 2026-04-23** (usuário: "Ok, faça sua consolidação.
Vamos pausar o estudo/evolução dos planos A/B/D por enquanto.")
**Opção aplicada:** PRIMARY (consolidação imediata; TIMEWAIT implícito via
revisão programada 6-12 meses; R5-LAST meta-labeling ensemble NÃO executado).
**Afeta (APLICADO):** `docs/investment-mandate.md` §1 (realocação 100%
passive) + §7 (entrada histórica). `CLAUDE.md` + `.claude/CLAUDE.md`
sumário atualizados. Strategy A, B, D marcadas DORMANT (0% capital);
Strategy E infra retida como experimental.
**Reversibilidade:** Override não apaga a infra (engine cross-lib, gates,
33 livros, scripts Phase D/E). Muda apenas alocação de capital e congela
slots ativos. Futuros overrides podem reativar slots caso literatura/regime
sugiram novo signal promissor.

---

## Por que este override

**113 honest FAIL consecutivos em 2 semanas.**

| Phase | Leads testados | FAIL |
|-------|---------------|------|
| 3.5f V2 Plano A (6 families) | 6 | 6/6 |
| 3.6 broader hunt (10 families) | 10 | 10/10 |
| 3.7-3 top-tier literature (H1/H2/H3) | 8 | 8/8 |
| 3.8-1 Gayed canonical (B1-B5) | 5 | 5/5 |
| 3.6 legacy families (A-K) | 32 | all FAIL |
| D-MVP partial (BR-only) | 10 | 10/10 |
| **E-MVP (multi-market)** | **42** | **42/42** |
| **TOTAL** | **113** | **113/113** |

Com 33 livros absorvidos, engine cross-lib validada (bt + vectorbt + backtrader
+ numpy reference concordam a 1e-6), e gates PBO/DSR/WF/bootstrap/stress
rigorosamente aplicados, **nenhum dos factors globais testados produziu edge
que sobreviva honest multiple-testing correction**. Phase E confirmou que
ampliar universo pra US não salva o signal — PBO 0.786 mostra ranking IS→OOS
aleatório.

Isso é consistente com:

1. **Harvey & Liu (2015) JOIM, "Evaluating Trading Strategies"**: de 316
   factors publicados em top journals, ~60% não sobrevivem correção multiple-
   testing. Replicação out-of-sample dos "survivors" mostra Sharpe half-life
   de ~3 anos.

2. **Ilmanen (2011) "Expected Returns"**: apenas 5-6 factors robustos
   globalmente (value, momentum, carry, quality, trend, BAB). Todos têm
   janelas de 10-15 anos de underperformance. Retail não aguenta.

3. **López de Prado (2018) "Advances in Financial Machine Learning"** `p.31-34`:
   "the overwhelming majority of backtested strategies are false discoveries".
   PBO < 0.5 gate existe porque o default behavior é overfit.

4. **Real-world benchmarks**: retail active funds US 2010-2024 → 85%+
   underperform SP500 após custos (SPIVA reports). Hedge funds net-of-fees
   underperform 60-40 portfolio por 10+ anos (AQR, Brookings studies).

---

## Alterações propostas no mandate

### Opção PRIMARY — "Consolidar Plano C" (RECOMENDADA)

**`§1 Capital allocation`** — substituir a tabela:

| Compartimento | Alocação alvo | Função | Regras |
|---------------|---------------|--------|--------|
| **Passive buy&hold factor-tilted (Plano C)** | **100%** | Única alocação ativa. | Governado por `portfolio-aposentadoria.md`. Rebalanceamento por aportes. |
| **Strategy A** | **0% inativo** | Slot preservado pra research futura; sem live capital. | Pepperstone infra mantida. Reativa se novo signal emergir com 13 gates PASS. |
| **Strategy B** | **0% inativo** | Slot preservado; sem live capital. | Inter infra mantida. Reativa se LETF rotation signal emergir fora de 2020-2023 regime. |
| **Strategy D** | **0% inativo** | Slot preservado (override 2026-04-22 signed); sem live capital. | IBrX-100 BR infra mantida. Reativa se regime BR normalizar + signal passar gates. |
| **Strategy E** | **(never promoted to slot)** | Infra multi-market permanece como experimental script. | `scripts/phase_e_mvp/` retained for future re-runs. |

**`§2` Gates** — inalterado. Gates continuam válidos para QUALQUER future reativação.

**`§7` Histórico de overrides** — adicionar entrada:

> **2026-04-23:** Consolidação em Plano C 100% passive após 113/113 honest
> FAIL em 2 semanas. Evidência estatística cumulativa (Phase 3.5f-3.8 + D-MVP
> partial + E-MVP full grid) de que factor-based active alpha não está
> accessible pro setup atual (retail, capital < $1M, broker retail, dados
> free/yfinance). Slots A, B, D preservados como dormant. Strategy E infra
> (`scripts/phase_e_mvp/`) retida como experimental. Revisar em 6-12 meses.

### Opção ALTERNATIVE — "R5-LAST ensemble" (BAIXA probabilidade)

Rodar 1 última experiência antes de consolidar:

- **AFML Meta-Labeling ensemble sobre os 113 leads falhados**. Infra existe em
  `src/ai_trade/backtest/meta/` mas nunca foi testada como ensemble
  dinâmico sobre multiple weak signals simultaneamente.
- Hipótese: se combinarmos 113 signals-com-falha-individual em meta-labeled
  ensemble, o weak alpha cumulativo pode ter Sharpe > 0.5 net.
- **Probabilidade empírica: 10-20%** (meta-labeling literature geralmente
  vem depois de strong base signal; aqui não temos nenhum).
- **Timebox: 1 semana max**. Se falhar, default automático = consolidar Plano C.

### Opção TIMEWAIT — "R-WAIT"

- Arquivar tudo como está (Strategy E permanece com infra pronta).
- Re-rodar o mesmo grid em 2026-10-23 (6 meses) e 2027-04-23 (12 meses).
- Se o regime 2020-2023 foi anomalia e 2024-2027 normaliza, gates podem passar
  com os mesmos signals.
- **Risk**: capital parado em Plano C 60-80% não é "parado" (está rendendo
  factor-tilted), mas 100% passive pode ser mais eficiente.

---

## Recomendação

**Opção PRIMARY + TIMEWAIT combinadas**:

1. Assinar agora a consolidação em 100% Plano C.
2. Agendar (mental/cron) re-run dos grids existentes em 6 meses.
3. Se em 2026-10 algum signal acorda, ir pro R3 oficial (reativar slot).

Isso é:
- **Estatisticamente honesto**: respeita o sinal de 113/113 FAIL.
- **Financeiramente ótimo**: 100% passive factor-tilted tem Sharpe esperado
  ~0.45-0.55 net (benchmark SPY ~0.50), vs slots ativos com edge efetivo zero.
- **Não é "desistir"**: infra retida, revisão programada, novos livros futuros
  podem inspirar retomada.

---

## Como assinar

- **"aprovado primary"** → aplico mudanças literais em `investment-mandate.md §1,
  §7`, `CLAUDE.md` sumário. Marco este doc como Signed. Atualizo
  `jornada/README.md` → "FINAL: project moved to maintenance mode".
- **"aprovado primary+timewait"** → idem + adiciono entrada no `ROADMAP.md`
  pro re-run em 6-12 meses.
- **"R5-LAST primeiro"** → não aplico override ainda; começo semana de R5-LAST
  (meta-labeling ensemble). Se falhar, override automático.
- **"rejeitado"** → mantém tudo como está; aguarda nova diretriz.
- **"ajustes: X"** → reescrevo override.
