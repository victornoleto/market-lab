# Estado atual — market-lab (2026-05-05)

> **Propósito:** onboard rápido para humanos e agentes. Este doc é o
> snapshot vivo — a verdade canônica vive nos arquivos referenciados.

---

## TL;DR (2026-05-05)

🛑 **MAINTENANCE MODE** desde 2026-04-23 (mandate §1, §7).

- **Capital:** 100% **Plano C** passivo factor-tilted. Documentação pessoal movida para `victor-ia/verticals/investments/`.
- **Strategies A/B/D:** **DORMANT** (0% capital, infra retida).
- **113/113 honest FAIL** acumulado entre 2026-04-08 e 2026-04-23 (Phase 3.5f-3.8 + D-MVP + E-MVP). Pattern previsto por López de Prado DSR + Aronson 6402-rule + Li-Ferreira 2025 Network Momentum.
- **Sem hunt ativo;** revisão consolidada do mandato em 6-12 meses.

Ver `docs/investment-mandate.md` para regras canônicas, e `docs/CLEANUP_2026-04-24_LOG.md` + `docs/CLEANUP_2026-05-05_LOG.md` para audit trail dos cleanups.

---

## Status por linha de pesquisa (2026-05-05)

### Plano C — buy-hold passivo factor-tilted ✅ ATIVO
- **Status:** sole winner. 100% do capital. Zero alterações.
- **Refs:** documentação pessoal fora do repo público, em `victor-ia/verticals/investments/`.
- **Mandate §:** §1, §4.7

### Plano A (Pepperstone CFD short-hold) 🛑 DORMANT
- **Status:** V2 encerrado 2026-04-23 (6 leads honest re-validation FAIL após engine fix `7b90a8f`).
- **Reativação exige (mandate §3):** multi-asset (SPY/QQQ/Gold/BTC/ETH/FX), sweep alavancagem 1:1→1:200 × Kelly f/2, staging USD 500-1k → cap 5-10k. Single-asset edge não aceito.

### Plano B (Inter swing US LETF rotation) 🛑 DORMANT
- **Status:** Phase 3.5b/3.5c canonical preserved; Phase 3.5e c06-c12 pausado em 26%; Phase 3.8-1 hunt FAIL 5/5.
- **Reativação exige (mandate §4):** Inter Internacional, tese Gayed-anchored única fonte, CPCV+PBO+splits-mutex+bootstrap 0.001+15% DARF.

### Plano D (BR ranking mensal IBrX) 🛑 DORMANT
- **Status:** Phase E-MVP (2026-04-23) failed catastroficamente (PBO 0.786).
- **Reativação exige (mandate §4b):** literatura/regime novos. Specs novas devem viver em `docs/specs/`.

---

## Linhas exploratórias em studies/ (2026-05-05)

### studies/spy_beater_hunt/ 🛑 CLOSED 2026-04-30
- 55 iters; **B4 Conservative (25 NTSX / 25 GDE / 25 RSST / 25 ZROZ)** declared deploy-ready (Sharpe 0.745 net).
- Iters 040-055 = post-closure RSST-corrected validation.
- Refs: `studies/spy_beater_hunt/{TOP_STRATEGIES,WINNER_AND_RANKING,BASE_MEMORY}.md`.

### studies/myfxbook_reverse_engineering/ 🛑 CLOSED 2026-05-04
- Veredito final: `CLOSED_NO_OPERABLE_EDGE`.
- 55 systems avaliados Fase 1; 0 elegíveis Fase 2 (synthetics distinguíveis do real, decoder não captura regra robusta).
- Plano A continua DORMANT — não há base operacional.
- Refs: `studies/myfxbook_reverse_engineering/_diagnostics/PIPELINE_V4_CLOSURE.md`.
- Cleanup 2026-05-05: bulk OHLC (1.8GB) + trades (406MB) deletados (regeneráveis via Dukascopy se reativar).

### studies/long_term_portfolio/ ⚠️ BLOCKED ON SCORING FIX
- 14 iters completos (codex-cli); incumbent iter 011 (NTSX 35 / GDE 25 / KMLM 40, Sharpe 1.046-1.104).
- Bloqueio: `iter 009` scoring usa benchmarks gross-of-tax vs candidates net (`apples-to-oranges`).
- Status: `pending_scoring_rework` em `BASE_MEMORY.md`. Não rodar iter 011+ até fix.

### studies/global_factor_tilt_loop/ ❄️ FROZEN (pre-launch checklist)
- 14 iters (6 winners). iter 009 (HAA+Gold) Sharpe pareto frontier; iter 014 (annual-DARF) prova rotation tax-neutral sob Lei 14.754.
- Reativação aguarda completion de gold_swing_loop + sinal usuário.

### studies/day_swing_strategy_hunt/ 🌱 BOOTSTRAP
- Sem iter ainda. Docs/protocol prontos. Pode resumir a qualquer momento.

### studies/bestfolio_meta_wf_hunt/ 🛑 CLOSED 2026-04-29
- iter 001 dead-end: walk-forward solver sobre sleeves gate-screened com Sharpe density tight = noise (turnover 177-222%/ano sem edge).
- Lesson preservada (anti-pattern documentado).

### studies/_shared/ 🔒 CRITICAL INFRA
- `tax_engine.py` (espelho byte-identical de `global_factor_tilt_loop/tax_engine_v2.py`). AnnualDarfEngine canônico Lei 14.754. Não tocar.

### studies/_archive/ 📦 PRESERVED
- strategy_hunt_loop (78 iters, 1 strict winner iter 079); gold_swing_loop (25 iters, 0 winner, structural ceiling); ema_sma_threshold (Phase 1 legacy).

---

## Engine status (pós-2026-04-22)

| Componente | Status | Ref |
|---|---|---|
| `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` | ✅ HONEST (fix 7b90a8f) | `tests/test_plano_a_lookahead_bias.py` |
| `letf_rotation.py` | ✅ NEVER HAD BUG | F1 audit |
| Cross-lib validation (bt/vectorbt/backtrader/numpy) | ✅ 1e-6 concordance | `studies/_archive/phase_3_5f/reports/v2_l2_gayed_redo/cross_lib_report.md` |
| Pytest baseline | ✅ **813 collected** (5/5 cleanup 2026-05-05) | — |

---

## Regras invioláveis (lembrete operacional)

Sumário do mandate (`docs/investment-mandate.md` é canônico):

1. **Capital:** 100% Plano C; A/B/D = 0% DORMANT.
2. **CAGR/MDD = tiers warning-only** (mandate §2.2/§2.3 desde 2026-04-22).
3. **Plano A reativação:** multi-asset + sweep leverage + staging USD 500-1k → 5-10k.
4. **Plano B reativação:** Inter Internacional + Gayed-anchored + CPCV/PBO/15% DARF.
4b. **Plano D reativação:** literatura/regime novos exigidos.
5. **Gates hard-block (zero bypass):** PBO<0.5, DSR p<0.05, WF≥6/8, single-block OOS, FWD stress, bootstrap 99.9% CI low > 0, cross-lib ±3pp CAGR.
6. **Threading model live (Phase 4)** pausado.
7. **Dynamic sizing preservado.**

**Citação obrigatória** em toda decisão: `[book.slug, p.X]`. 33 livros em `books/summaries/`, skill em `knowledge/SKILL.md`.

---

## Referências cruzadas

- **Mandate canônico:** `docs/investment-mandate.md`
- **Setup + arquitetura:** `README.md`
- **Cleanup playbook:** `docs/CLEANUP.md`; logs forenses `docs/CLEANUP_2026-04-24_LOG.md` + `docs/CLEANUP_2026-05-05_LOG.md`
- **Histórico público:** `docs/PROJECT_HISTORY.md`
- **Knowledge base:** `books/MAPPING.md` + `knowledge/SKILL.md`
- **Convenções:** `CLAUDE.md`

---

## Changelog

- **2026-05-05:** refresh total. MAINTENANCE MODE consolidado; status de studies/ atualizado (myfxbook CLOSED 2026-05-04, spy_beater B4 deploy-ready, long_term_portfolio BLOCKED, factor_tilt FROZEN, day_swing bootstrap). Pytest baseline 813.
- **2026-04-23:** rewrite total após Phase 3.5f fechar sem winner. Plano A V2 encerrado; Plano B c06-c12 pausado.
- **2026-04-19:** versão inicial.
