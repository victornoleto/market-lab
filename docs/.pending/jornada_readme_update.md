# DRAFT — pending user review

**Target file:** `jornada/README.md`
**Status:** NOT YET MERGED. This is a staged rewrite of the
"Onde estamos hoje" and "O que vem a seguir" sections, awaiting user
approval of the Phase 3.5f outcome and chosen next-step option.

Merge instructions: once the user selects an option (A/B/C/D per
`jornada/2026-04-23-0700-overnight-summary.md`), replace the current
"Onde estamos hoje (2026-04-22 — Phase 3.5f aberta, engine lookahead
bug descoberto)" block in `jornada/README.md` with the block below.
Update `<chosen-option>` and follow-up sentence accordingly.

The existing index list ("Entradas (mais recente primeiro)") has
already been updated in the F4 commit chain (3 new entries appended
for the bug narrative, honest re-validation, and overnight summary).
DO NOT touch the index again here.

---

## Draft "Onde estamos hoje" block

```markdown
## Onde estamos hoje (2026-04-23 — Phase 3.5f fechada, Plano A sem winner honest)

**Estado:** 🛑 **Plano A V2 concluído sem winner sob engine honest.**
- Phase 3.5f F0-F4 fechou: bug de look-ahead descoberto em `plano_a_leveraged_rotation.py:462`, consertado (commit `7b90a8f`), e as 6 leads V2 re-avaliadas.
- **Nenhuma das 6 passa os 13 gates sob engine honest.** V2-L2 Gayed ("winner" original) cai de Sharpe 2.28/CAGR 79% para Sharpe 0.56/CAGR ~14% — edge real existe mas modesto, não justifica 2× leverage (MDD piora pra −37%). Outras 5 já estavam DEAD e permanecem DEAD.
- **Escopo do bug: 1 arquivo, 1 linha.** F1 grep-audit confirmou que `letf_rotation.py` (Plano B) e todas as outras engines já estavam corretas. **Phase 3.5b/3.5c/3.5d/3.5e preservadas como clean canonical** — não precisam re-validação.
- **Banners forensic** aplicados apenas em `reports/phase3_5a_v2/v2_l2_*`, `phase3_5a_v2/v2_l4_*` (contaminação parcial, 4.8% blend weight) e `phase4_0/*`.
- **Decisão do usuário 2026-04-2X:** **<chosen-option>** — [se Opção A: desenhar V3 7ª família; se B: Phase-6 fallback Gayed 1× unleveraged; se C: abandonar Plano A permanente, realocar bucket A pro Plano C; se D: freezar Plano A e retomar Plano B c06-c12 no grid Phase 3.5e].

Entries relevantes:
- `jornada/2026-04-23-0700-overnight-summary.md` — sumário matinal ← ÚLTIMO
- `jornada/2026-04-22-plano-a-honest-revalidation.md` — 6 leads re-validadas
- `jornada/2026-04-22-engine-lookahead-bug.md` — narrativa do bug
- `jornada/2026-04-22-2212-engine-lookahead-bias-descoberto.md` — descoberta inicial
- `reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md` — matriz cross-lead
- `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md` — scope audit
- `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md` — plano executado

---
```

## Draft "O que vem a seguir" block

Insert this block (or a condensed version) immediately after the
"Onde estamos hoje" block, replacing whatever is there currently.
The content varies by chosen option:

### If Option A (V3) selected

```markdown
**Próxima fase:** Phase 3.5g — desenhar V3 (7ª família de lead Plano A). Candidatos science-based não testados nas 6 V2 anteriores: vol-surface skew signals (options-based), event-study pre-earnings `[algo_trading_chan]`, cross-asset lead-lag correlação defasada. Budget: 4-8 semanas spec + build + validate. Exit criterion: se V3 também não passar honest gates, abandonamento Plano A vira bloqueante (não mais opcional).
```

### If Option B (Gayed 1×) selected

```markdown
**Próxima fase:** Phase-6 fallback Gayed 1× unleveraged. Re-rodar V2-L2 Gayed sem alavancagem, documentar estimativas honest (~11%/ano CAGR, MDD ~16%, Sharpe ~0.7). Aceitar como "passive-like active" em bucket A, acknowledging CAGR abaixo do CDI BR. Ship em dias. **NB:** essa opção viola mandate §2 (CAGR < CDI) e precisa registro em §7 como override deliberado pelo usuário.
```

### If Option C (abandon) selected

```markdown
**Próxima fase:** encerramento Plano A. Invoca regra `project_plano_a_v2_last_attempt` (user memory: "se 3.5a-V2 falhar, abandonar permanente"). Realocação per mandate §4.7: bucket A (20-40%) vai 100% pro Plano C buy-hold. Mandate §3 (Plano A spec) marcado como "encerrado sem winner". Bandwidth liberada pra Plano B c06-c12 e refinamento Plano C. Plano A não recebe V3.
```

### If Option D (Plano B resume) selected

```markdown
**Próxima fase:** Phase 3.5e retomada — completar grid Plano B c06-c12 sob engine honest (Plano B engine já estava limpa per F1 audit). 106 trials pendentes em 7 families. Relançar `self_improve_loop.sh` sobre Phase 3.5e; budget 1-2 semanas. Plano A fica frozen (sem V3, sem abandono formal) até o grid Plano B terminar. Se um winner Plano B emergir e passar gates, ele cobre bucket A + B conjuntamente (mandate §1 re-interpretado).
```

---

## Notes for the merge operation

1. Choose exactly one of the 4 "O que vem a seguir" variants above,
   matching the option selected.
2. The previous "Onde estamos hoje" block (2026-04-22) should be
   moved down as "Estado anterior (2026-04-22 tarde — Phase 3.5f
   aberta, engine lookahead bug descoberto)" to preserve the
   chronological record pattern used in this README.
3. The glossary section should gain one term if not already present:
   - **Look-ahead bias:** usar informação do futuro (incluindo o
     próprio período que se está avaliando) pra tomar decisão
     retroativa. Erro clássico em backtest `[advances_fin_ml, p.31-34]`.

---

## Citations

- `[advances_fin_ml, p.31-34]` — look-ahead bias.
- Mandate §2, §2.5, §3, §4.7.
- `project_plano_a_v2_last_attempt` (user memory).
