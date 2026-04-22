# Estado atual — ai-trade (2026-04-22)

> **Propósito:** onboard rápido para humanos e agentes. Este doc é o
> índice de orientação — a verdade canônica vive nos arquivos
> referenciados.

---

## TL;DR (2026-04-22 — Phase 3.8-1 fechada, 29/29 honest FAIL, Phase 3.9 planejada-não-executada)

**Nenhum winner ativo. Nunca houve.** 29 validações honest sob 13 gates
em 3 phases (3.5f/3.6/3.7-3/3.8-1), 0 PASS. Pattern exato predito por
López de Prado DSR + Aronson 6402-rule + Li-Ferreira 2025 Network
Momentum state-of-art Sharpe 0.35 líquido.

**Phase 3.8-1 (Plano B hunt, 2026-04-22):** 5 hipóteses canonical-or-close
(B1 Gayed SMA-200 + UPRO/SSO, B2 MA-robustness sweep 16 configs, B3
Pauchlyova 5-asset static+trend, B4 Hsieh AR(1), B5 Faber 10-mo GTAA
unleveraged) FAIL sob mesmo killer estrutural — bootstrap OOS 99.9%
CI low cruza zero + DSR p > 0.05 em TODOS. B5 com turnover 1.39/ano
(tax-minimal) também falhou — DARF não é único killer; signal é
statistically weak per se sob multiple-testing. `reports/phase_3_8/BREADTH_NO_WINNER_B.md`
formaliza R1-R5 (R1 paper-trade B5 6-12m / R2 pivot Plano C 100% mandate
§4.7 default / R3 re-spec Válido=CDI-matcher / R4 wait+re-run / R5 Phase 3.9
composer-inspired layered-conditional).

**Phase 3.9 planejada mas NÃO executada** (usuário "dar um tempo" 2026-04-22).
Plan em `docs/plans/2026-04-22-phase3.9-composer-inspired-hunt-prompt.md`.

**Próxima fase ativa:** NENHUMA. Projeto em pausa, aguardando decisão
usuário entre R1/R2/R3/R4/R5 OR abrir tópico novo. Mandate intacto; nenhuma
relaxação de gates além das §2.2/§2.3 tier framework de 2026-04-22.

**Engine honest validada cross-lib em 23 strategies** (10 Phase 3.6 + 8
Phase 3.7-3 + 5 Phase 3.8-1). Fix commit `7b90a8f` Phase 3.5f preserved.
Pytest baseline 929 passed, 2 skipped.

---

## Status dos Planos (2026-04-23)

### Plano A — Pepperstone CFD (short-hold alavancado)

**Status:** 🛑 **V2 encerrado sem winner honest.** Phase 3.5f F0-F4
completou re-validação das 6 leads V2 sob engine patched:

| Lead | Família | Veredito honest |
|---|---|---|
| V2-L1 | TSMOM multi-asset | FAIL (engine era clean, DEAD confirmado) |
| V2-L2 | **Gayed regime rotation CFD** | **FAIL (79%→14% CAGR sob fix; 6/13 gates falham)** |
| V2-L3 | AFML triple-barrier meta-label | FAIL (engine era clean, DEAD confirmado) |
| V2-L4 | Carver Risk Parity blend | FAIL (surpresa: L2 só 4.8% do blend; rescue refutado) |
| V2-L5 | Kalman pair cointegration | FAIL (structural: 0 cointegrated pairs) |
| V2-L6 | Donchian vol-breakout | FAIL (12/12 OOS Sharpe negativo; engine era clean) |

**Decisão (2026-04-23):** abandonar Plano A V2 sem V3 isolado per
`project_plano_a_v2_last_attempt` memory rule. Phase 3.6 (broader hunt)
pode eventualmente produzir strategy tradeável em Pepperstone CFD como
sub-família — mas não é "V3 Plano A".

**Leia mais:**
- Living doc (com banner REJECTED):
  [`docs/strategies/plano_a_v2_l2_gayed_cfd.md`](strategies/plano_a_v2_l2_gayed_cfd.md)
- Phase 3.5f breadth summary:
  [`reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md`](../reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md)
- Morning summary (decisão 4-opções):
  [`jornada/2026-04-23-0700-overnight-summary.md`](../jornada/2026-04-23-0700-overnight-summary.md)
- Plano A DEAD historical per-lead: `reports/phase_3_5f/honest_revalidation/v2_l{1..6}_*/AGGREGATE.md`

---

### Plano B — Banco Inter Global (swing LETF rotation)

**Status:** 🟡 **V4 rejeitado em 2026-04-20 (Phase 3.5c cross-lib);
Phase 3.5e breadth-hunt c06-c12 pausado em 26% (iter 43).**

V4 original (3-leg EW SSO+QLD+UGL, Sharpe 2.25/CAGR 37.92% reportado em
Phase 3.5b) foi rejeitado após cross-lib showing CAGR real ~11.6% /
Sharpe 0.78 — baseline Phase 3.5b dependia de testfol.io proprietary
synthetics que não reproduzem na pipeline. Phase 3.5d tentou 3× LETF
search, encerrada sem winner em 2026-04-21 (E1 vol_target bloqueado por
arbitration adversarial: PBO reduction por grid shrinkage).

Phase 3.5e c06-c12 breadth-hunt em progresso quando Phase 3.5f descobriu
o engine bug (que NÃO afeta `letf_rotation.py` — F1 audit provou que
Plano B engine estava clean). Trial count 38/144 (26%). Pausado por
decisão explícita do usuário em 2026-04-22.

**Status engine (após Phase 3.5f F1 audit):** Plano B engine
(`letf_rotation.py`, `synthesize_letf_returns_ffr_aware`) **nunca teve
o bug** — usa compounding de return-series direto, não `w × r`
bar-level. Todos os reports Phase 3.5b/3.5c-adapters/3.5d/3.5e são
**canonical limpo**. Não precisam re-validação.

**Phase 3.6 pode retomar trabalho Plano B** como uma das candidates
(família LETF rotation / family C "GTAA 10-month SMA" no menu §4 do
plano 3.6). Não obrigatório — depende de quais candidates Phase 3.6
selecionar.

**Leia mais:**
- Living doc (V4 + rejection history):
  [`docs/strategies/plano_b_3leg_letf_rotation.md`](strategies/plano_b_3leg_letf_rotation.md)
- Phase 3.5c rejection:
  [`jornada/2026-04-20/03-phase-3-5c-cross-lib-exposed-baseline-mismatch.md`](../jornada/2026-04-20/03-phase-3-5c-cross-lib-exposed-baseline-mismatch.md)
- Phase 3.5e batch 1 summary:
  [`jornada/2026-04-21-1700-session-summary-phase-3-5e-batch1.md`](../jornada/2026-04-21-1700-session-summary-phase-3-5e-batch1.md)
- Engine clean confirmation:
  [`docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md`](superpowers/findings/2026-04-22-engine-lookahead-scope.md)

---

### Plano C — Buy-hold aposentadoria (passivo)

**Status:** ✅ Intocado. 60-80% do portfolio. Mandate §1.

Ver [`portfolio-aposentadoria.md`](../portfolio-aposentadoria.md).

---

## Próxima fase — Phase 3.6 (broader swing-winner hunt)

**Plano executável:**
[`docs/plans/2026-04-23-find-swing-winner-phase-3-6.md`](plans/2026-04-23-find-swing-winner-phase-3-6.md)
(271 linhas, self-contained).

**Branch:** `phase3.6/swing-winner-hunt-20260423` (já criada off 3.5f
pra herdar engine fix).

**Objetivo:** 1 swing strategy (hold 5-30d) que sobrevive 13 gates
relaxados pra swing (Sharpe ≥ 1.5, CAGR ≥ 13% CDI floor, MDD ≥ −25%,
hold ≥ 5d, IR ≥ 0.3, cross-lib concordance obrigatória).

**Broker-agnostic:** Pepperstone/cTrader OR Banco Inter, escolhido por
per-strategy fit. Tax model 15% BR se Inter; zero se Pepperstone.

**Menu 12 candidates** (§4 do plan) cobre equity cross-sectional
momentum (Clenow), risk parity (Bridgewater), GTAA (Faber), pairs MR
(Chan), Ehlers cycle filters, vol-target managed futures, evidence-
based TA (Aronson), adaptive markets regime-switching, stat-sound
indicators, ML-for-algo classical, universal trend tactics, PEAD.

**Stopping rule:** stop-at-first-winner (HOLD pro user approval) OU
10 FAIL → escalação com `BREADTH_NO_WINNER.md`.

---

## Phase 4 paper trading — status

**PAUSADA indefinidamente** até Phase 3.6 produzir winner OU user
decidir pivot alternativo (softer gates com sign-off / broadening
universe / passivo-only). Spec `specs/phase_4_paper_trading.md`
preservada mas não-ativa.

---

## Engine status (pós-2026-04-22)

| Componente | Status | Ref |
|---|---|---|
| `plano_a_leveraged_rotation.py` | ✅ HONEST (fix 7b90a8f) | `tests/test_plano_a_lookahead_bias.py` (4 tests) |
| `letf_rotation.py` | ✅ NEVER HAD BUG | F1 audit |
| `tsmom_multi_asset.py` | ✅ CLEAN | F1 audit |
| `afml_tb_meta.py` | ✅ CLEAN | F1 audit |
| `donchian_breakout.py` | ✅ CLEAN | F1 audit |
| `kalman_pair_cointegration.py` | ✅ CLEAN | F1 audit |
| Cross-lib validation | ✅ 1e-6 concordance | `reports/phase_3_5f/v2_l2_gayed_redo/cross_lib_report.md` |
| Pytest baseline | ✅ 918 green | 914 + 4 F0 surgical |

---

## Regras invioláveis (lembrete)

Todas as 7 regras do Investment Mandate continuam valendo:

1. Capital: 60-80% passivo (Plano C) + 20-40% ativas. Ativas =
   2 strategies (A short-hold agressiva, B swing moderada) — HOJE
   ambas as slots A+B estão **sem winner confirmado**.
2. CAGR mínimo = CDI BR (~13-14%/ano). Gate soft-lock em Phase 3.6.
3. Strategy A (CFD Pepperstone) é multi-asset obrigatório.
4. Strategy B é família LETF rotation ancorada em Gayed.
5. Gates sempre (PBO < 0.5, DSR p < 0.05, WF ≥ 6/8, single-block OOS,
   forward-window stress). Zero bypass.
6. Threading model live: 1 thread/ativo.
7. Citação obrigatória em toda decisão técnica: `[book.slug, p.X]`.

**Leia mais:** [`docs/investment-mandate.md`](investment-mandate.md)
(especialmente §7 Histórico de overrides — linha 2026-04-22 registra o
engine bug + V2 abandonment).

---

## Referências cruzadas

- **Roadmap técnico detalhado (fases + decisões diferidas):**
  [`ROADMAP.md`](../ROADMAP.md)
- **Setup + arquitetura do repo:**
  [`README.md`](../README.md)
- **Narrativa humana (newest first):**
  [`jornada/README.md`](../jornada/README.md)
- **Mandate completo (regras + §7 histórico):**
  [`docs/investment-mandate.md`](investment-mandate.md)
- **Knowledge base (34 livros, 16 active + 18 archived):**
  [`books/MAPPING.md`](../books/MAPPING.md)
  + Skill agregada [`knowledge/SKILL.md`](../knowledge/SKILL.md)
- **Convenções do projeto:**
  [`CLAUDE.md`](../CLAUDE.md)
- **Plano 3.6 (próxima fase):**
  [`docs/plans/2026-04-23-find-swing-winner-phase-3-6.md`](plans/2026-04-23-find-swing-winner-phase-3-6.md)
- **Phase 3.5f (overnight run fechada):**
  [`docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`](plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md)

---

## Changelog deste doc

- **2026-04-23:** rewrite total após Phase 3.5f fechar sem winner.
  Plano A V2 encerrado; Plano B c06-c12 pausado; Phase 3.6 aberta
  como broader hunt.
- **2026-04-19:** versão inicial — criado pós-cleanup, após V2
  winner (buggy-engine) + Phase 3.5b final. **SUPERSEDED 2026-04-23.**
