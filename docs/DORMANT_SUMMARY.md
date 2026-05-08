# Reports DORMANT — Sumário consolidado (2026-04-24)

Este documento substitui **~15 subpastas de reports/** de estratégias DORMANT
(Plano A Pepperstone CFD + Plano B swing US LETF + Plano D BR ranking +
Plano E multi-market + micro-estudos early 2026-04) removidas no cleanup
de 2026-04-24. Ver `docs/CLEANUP_2026-04-24_LOG.md` pra audit trail
completo.

**Recuperação completa**: `git checkout pre-cleanup-2026-04-24 -- reports/<subpasta>/`

---

## Estado do mandate (2026-04-23)

**113/113 honest FAIL** em 2 semanas:
- Phase 3.5a-V2 revalidação: 6 FAIL
- Phase 3.6 (swing-broad hunt): 10 FAIL
- Phase 3.7 (literário intraday VIX+crypto): 8 FAIL
- Phase 3.8-1 (Plano B robustness sweep): 5 FAIL
- Phase D-MVP (BR ranking grid): 10 FAIL
- Phase E-MVP (multi-market extension): 43 FAIL
- Bollinger MR / ETF rotation micro-estudos: repeat FAIL early April
- Total cumulativo: 113

Consolidação: **100% Plano C passive factor-tilted**; A/B/D/E marcadas
**DORMANT** (mandate §1, 2026-04-23). Revisão programada 6-12 meses.

---

## Pastas PRESERVADAS (não removidas — still in repo)

| Pasta | Tamanho | Motivo |
|-------|---------|--------|
| `portfolio_aposentadoria_v2/` | 8.9M | **Plano C master** — única estratégia vencedora. TLDR + ANALYSIS (~900L) + REVISIONS audit trail |
| `phase3_5a_v2/` | 6.8M | Forensic: 6 V2 leads que salvaram engine de lookahead bug (commit 7b90a8f). Inclui `_DO_NOT_CLEANUP.md` |
| `phase3_5b/` | 4.2M | Canonical Plano B LETF reference — 13 configs, metodologia de referência futura |
| `phase_3_5c/` | 3.3M | **Cross-lib validation infra** (adapters backtrader/bt/vectorbt/quantstats + reference_prices). Importado por `tests/cross_lib/` — NÃO é dormant. Só `results/` (outputs de runs dormant) foi removido |
| `phase_3_5e/` | 820K | Plano B 7-family continuation (c06-c12 paused) |
| `phase_3_5f/` | 900K | Honest re-validation de Plano A V2 pós-fix lookahead (6 leads ALL FAIL) |

## Pastas REMOVIDAS (arquivos-chave copiados pra `_archive/`)

| Pasta removida | Tamanho liberado | Arquivo-chave preservado em `_archive/` |
|----------------|------------------|------------------------------------------|
| `phase_3_5c/results/` | 6.8M | (stage_1 + stage_2 outputs dormant — infra em `phase_3_5c/cross_lib/` preservada) |
| `phase_3_5d/` | 556K | `phase_3_5d_ESCALATION_PENDING.md` (d1-d8 + e1 grid) |
| `phase_3_6/` | 1.9M | `phase_3_6_BREADTH_NO_WINNER.md` (204L — 10 FAIL A-K swing-broad) |
| `phase_3_7/` | 1.4M | `phase_3_7_BREADTH_NO_WINNER.md` (243L — 8 FAIL H1-H3 literário) |
| `phase_3_8/` | 528K | `phase_3_8_BREADTH_NO_WINNER_B.md` (235L — 5 FAIL B1-B5 robustness) |
| `phase_d_mvp/` | 1.3M | `phase_d_mvp_BREADTH_NO_WINNER_D.md` (89L — 10 FAIL D1 BR ranking grid) |
| `phase_e_mvp/` | 4.8M | `phase_e_mvp_SUMMARY.md` (66L — 43 FAIL multi-market) |
| `phase4_0/` | 176K | `phase4_0_ENGINE_BIAS_FORENSIC.md` + index_cfd_validation removido |
| `bollinger_mr_mc_bootstrap/` | 140K | (summary.md recuperável via tag) |
| `bollinger_mr_overlap/` | 56K | (summary.md recuperável via tag) |
| `bollinger_mr_regime_decomp/` | 192K | (summary.md recuperável via tag) |
| `bollinger_mr_trades/` | 140K | (trade logs — analytic terminado) |
| `regime_decomp_phase_b/` | 100K | (summary.md recuperável via tag) |
| `etf_rotation_mc_bootstrap/` | 92K | (summary.md recuperável via tag) |
| `b2_benchmark/` | 328K | (benchmark suite — infra integrada ao core engine) |
| `spec-judges/` | 96K | (1 run 2026-04-21 E1 vol-tgt — snapshot in git) |
| `assets/` | 4.0K | (pasta vazia) |
| `__pycache__/` | 8.0K | (gerado) |

**Total liberado:** ~27MB em reports/.

---

## Killer gates observados (padrão entre 113 FAIL)

Citando `[advances_fin_ml, p.208-211, p.196-202]` e mandate §5:

1. **G1 PBO** (Probability of Backtest Overfitting) > 0.5 — falha em
   estratégias com grid fino em espaço parametrico pequeno (top ex:
   Phase 3.6 K_universal_trend PBO 0.68; Phase D-MVP 7/10 FAIL neste gate)
2. **G2 DSR** (Deflated Sharpe Ratio) p > 0.05 após deflate por
   n_trials — falha universal em phases com n_trials > 500
3. **G3 Walk-Forward** < 6/8 splits (threshold CAGR/MDD por janela) —
   killer estrutural Plano B (Phase 3.8-1 B1-B5); E-MVP 43/43 FAIL
4. **G7 Cross-lib** |ΔCAGR| > 3pp entre lib A (custom) e B (vectorbt/
   quantstats) — sinal de bug de engine; passou em 17/18 nos runs
   post-3.5c, indica engine clean; G1-G3 é que bloqueiam

---

## Conexão com Plano C (vencedor)

Todas as fases DORMANT convergiram pro mesmo insight:
> Single-asset trend-following com LETF não entrega edge robusto após
> honest gates. Backbone passivo factor-tilted (Plano C) foi a única
> tese que sobreviveu a bootstrap CI, OOS bloco único e cross-lib.

Literatura suportando pivot: `[leverage_for_the_long_run, p.4-6, 19-20]`
(LETF decay em trend-switching), `[risk_parity, p.5, ch.1]`
(risk-parity backbone), `[advances_fin_ml, p.302-308, ch.16]`
(overfit-deflate de resultados de grid).

Literatura acusando Plano D 43 FAIL:
> Cederburg 2024 (multi-market BR ranking not generalizable —
> momentum strong only in US, not emerging markets) + Asness AQR 2024
> (factor premia decay in EM since 2020).

---

## Recovery cheatsheet

```bash
# Recuperar 1 pasta específica pré-cleanup:
git checkout pre-cleanup-2026-04-24 -- reports/phase_3_6/

# Ver qualquer arquivo individual em tempo real:
git show pre-cleanup-2026-04-24:reports/phase_3_6/BREADTH_NO_WINNER.md

# Listar tudo que havia antes:
git ls-tree -r --name-only pre-cleanup-2026-04-24 | grep '^reports/'
```
