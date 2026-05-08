# Docs DORMANT — Sumário consolidado (2026-04-24)

Este doc substitui **14 especificações/prompts** de estratégias e phases
DORMANT removidas no cleanup de 2026-04-24, + 3 documentos pontuais.
Estratégias A/B/D/E são todas DORMANT per mandate §1 (consolidação
2026-04-23). Recovery: `git checkout pre-cleanup-2026-04-24 -- docs/<path>`.

---

## Specs de estratégia (docs/strategies/ removido)

| Arquivo removido | Linhas | Família | Status |
|------------------|--------|---------|--------|
| `plano_a_pepperstone_index_cfd_rate_card.md` | 201 | Pepperstone rate card (CFD) | Plano A DORMANT |
| `plano_a_v2_l2_gayed_cfd.md` | 684 | Gayed canonical via CFD (V2-L2) | Plano A DORMANT — FAIL post-lookahead fix |
| `plano_b_3leg_letf_rotation.md` | 394 | 3-leg LETF+QQQ Donchian+GLD Donchian | Plano B DORMANT |
| `plano_b_pauchlyova_static_candidate.md` | 334 | Pauchlyova 2025 static+trend | Plano B DORMANT — Phase 3.8-1 B3 FAIL |

Total: 1613 linhas de spec técnico.

## Hunt prompts (docs/plans/ removido)

Executaram hunts 2026-04-22→23. Todos fecharam BREADTH_NO_WINNER.
Consolidado em `jornada/_archive/DORMANT_HUNTS.md`.

| Arquivo removido | Linhas | Target phase |
|------------------|--------|--------------|
| `2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md` | 716 | Phase 3.5f — engine bug fix plan |
| `2026-04-22-phase3.8-1-plano-b-hunt-prompt.md` | 456 | Phase 3.8-1 B1-B5 — 5/5 FAIL |
| `2026-04-22-phase3.9-composer-inspired-hunt-prompt.md` | 407 | Phase 3.9 (nunca executada) |
| `2026-04-22-resume-plano-b-letf-hunt-prompt.md` | 215 | Resume Plano B c06-c12 (nunca executada) |
| `2026-04-23-find-swing-winner-phase-3-6.md` | 282 | Phase 3.6 A-K swing-broad hunt — 10/10 FAIL |
| `2026-04-23-phase3.7-1-research-sprint-prompt.md` | 270 | Phase 3.7-1 literature (28 papers) |
| `2026-04-23-phase3.7-2-data-sprint-prompt.md` | 310 | Phase 3.7-2 data integration (4 feeds) |
| `2026-04-23-phase3.7-3-hunt-prompt.md` | 364 | Phase 3.7-3 H1/H2/H3 — 8/8 FAIL |

Total: 3020 linhas de prompts executáveis.

## Research outputs (docs/research/ removido)

| Arquivo removido | Linhas | Conteúdo |
|------------------|--------|----------|
| `2026-04-23-phase3.7-2-data-sprint.md` | 341 | VIX/VIXY/crypto/ETH feed integration |
| `2026-04-23-phase3.7-literature-sprint.md` | 947 | 28 papers sourced (Maróy, Božović, Gayed, Zarattini, Pauchlyova, Hsieh, Faber, Hurst-Ooi-Pedersen) |

Total: 1288 linhas de research material (papers citados sobrevivem em
`books/summaries/` + knowledge/).

## Root docs removidos

| Arquivo | Linhas | Justificativa |
|---------|--------|--------------|
| `docs/phase3_winners_allocation.md` | 229 | Phase 3 winners retracted 2026-04-22 (lookahead bug); allocation rules obsoletas |

## Mandate overrides arquivados (moved to _archive/, not deleted)

Overrides pontuais de estratégias DORMANT — preservados pra rastrear
decisões históricas, mas fora do workflow ativo:

| Arquivo | Status |
|---------|--------|
| `2026-04-22-strategy-d-open.md` | Strategy D opened → DORMANT |
| `2026-04-23-strategy-e-multimarket.md` | Strategy E multi-market opened → FAIL 43/43 |

**Preservado ativo em `docs/mandate_overrides/`**:
- `2026-04-23-consolidate-plano-c-final.md` — override signed que consolidou
  mandate §1 em 100% Plano C. Load-bearing.
- `2026-04-24-crash-protected-letf-open.md` — override novo (sessão studies
  paralela 2026-04-24).

---

## Total liberado

- 14 files removidos: 5921 linhas
- 1 file root removido: 229 linhas
- 2 mandate overrides movidos pra _archive: preservados

**~6150 linhas consolidadas neste overview (~120 linhas).**

Recovery cheatsheet:
```bash
# Recuperar 1 arquivo específico:
git checkout pre-cleanup-2026-04-24 -- docs/strategies/plano_a_v2_l2_gayed_cfd.md

# Ver conteúdo sem checkout:
git show pre-cleanup-2026-04-24:docs/strategies/plano_a_v2_l2_gayed_cfd.md

# Listar tudo que havia:
git ls-tree -r --name-only pre-cleanup-2026-04-24 | grep '^docs/'
```
