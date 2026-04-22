# Resumo da madrugada 2026-04-23 — Phase 3.5f completa

**Data:** 2026-04-23 07:00 (documento de handoff matinal)
**Escrito para:** você acordando sem memória da sessão anterior.
**Branch ativa:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`
**Pytest:** 918 green (914 baseline + 4 novos testes cirúrgicos).

---

## TL;DR em 3 linhas

1. Descobri um bug de look-ahead na engine do Plano A, consertei, e
   re-validei as 6 leads do V2 sob a engine honest.
2. **Nenhuma das 6 passa gates.** O "winner" V2-L2 Gayed cai de Sharpe
   2.28/CAGR 79% pra Sharpe 0.56/CAGR ~14%.
3. **Você precisa decidir entre 4 opções** (§"Decisão que você precisa
   tomar" abaixo). Nenhum doc canonical foi modificado até você
   escolher.

---

## O que foi feito durante a noite

- **F0** — 4 testes cirúrgicos de look-ahead bias em
  `tests/test_plano_a_lookahead_bias.py`. Commit `2b414d0`.
- **F1** — Scope audit (grep + leitura linha-a-linha). Bug está em
  **1 arquivo, 1 linha**. Commit `7c280a2`.
- **F2** — Engine fix (`.shift(1)` no vetor de pesos); pytest 918
  green; cross-lib concordance a 1e-6 com bt/vectorbt/backtrader.
  Commit `7b90a8f`.
- **F3** — 6 leads re-avaliadas: L1 (`1cd3895`), L2 (`02fe3ea`),
  L3 (junto com as outras, mesma branch), L4 (`55f7eca`),
  L5 (`2947bc4`), L6 (`c1542e5`). Todas FAIL.
- **F4** — este documento + BREADTH_SUMMARY + jornada bug + jornada
  revalidation + 3 forensic banners + 3 files em `.pending`.

---

## Estado do repositório

- **Baseline pytest:** 918 green (914 pre-F0 + 4 novos).
- **Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`.
- **Commits novos da madrugada:**
  - `2b414d0` — test (F0 surgical tests)
  - `7c280a2` — docs (F1 scope)
  - `7b90a8f` — fix (F2 engine)
  - `02fe3ea`, `2947bc4`, `1cd3895`, `c1542e5`, `55f7eca` — feat (F3 aggregates)
  - + F4 commits desta sessão (ver final deste doc).
- **Arquivos frozen (não tocados, per mandate §2.2):**
  - `docs/investment-mandate.md`
  - `docs/strategies/plano_a_v2_l2_gayed_cfd.md`
  - `docs/CURRENT_STATE.md`
  - `docs/self_improvement/memory.md`
  - `docs/self_improvement/trial_count.json`
  - `reports/phase_3_5e/*`, `reports/phase_3_5b/*`, `reports/phase_3_5d/*`
  - `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/*` (banner
    foi fora, como file novo)
  - Os 6 `reports/phase_3_5f/honest_revalidation/*/AGGREGATE.md`
    (commitados na F3, não mexidos na F4).
- **Pending files (aguardam sua aprovação pra virar canonical):**
  - `docs/.pending/mandate_section7_entry.md`
  - `docs/.pending/plano_a_v2_l2_gayed_cfd_banner.md`
  - `docs/.pending/jornada_readme_update.md`

---

## Veredito das 6 leads (sob engine honest)

| Lead | Sharpe OOS | CAGR OOS | MDD OOS | Veredito |
|---|---:|---:|---:|---|
| V2-L1 TSMOM | −0.21 | −0.49% | −10.24% | FAIL |
| V2-L2 Gayed | 0.56 | 12.58-14.29% | −37% | FAIL |
| V2-L3 AFML | 1.21 | 2.50% | −0.76% | FAIL |
| V2-L4 Carver RP | 0.62 | 4.99% | −12.77% | FAIL |
| V2-L5 Kalman | — | — | — | FAIL (estrutural: 0 pairs) |
| V2-L6 Donchian | neg | — | — | FAIL (12/12 neg) |

Detalhes completos:
`reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md` + as 6
AGGREGATE.md per lead.

---

## Decisão que você precisa tomar

O Plano A **não tem winner honest**. Per mandate §2.5 (zero bypass),
nenhum dos 6 passa limpo. Per plano §F3 gate (c), eu não auto-escalo
pra V3 nem auto-abandono; é sua escolha. 4 caminhos:

### Opção A — Desenhar V3 (7ª família de lead)

Nova family além das 6 testadas. Candidatos science-based: vol-surface
skew (options), event-study pre-earnings (Chan `algo_trading_chan`),
cross-asset lead-lag (correlação defasada).

**Pros:** preserva ambição Plano A (5-10%/mês leveraged short-hold).
Hypothesis space não foi exaurido — as 6 testadas eram as
literature-dense.
**Cons:** 4-8 semanas de ciclo. Candidato V3 vai se apoiar em citações
mais finas (as famílias fat-literature já foram).
**Custo imediato:** spec doc novo + registry + CPCV plumbing. Budget:
~1 science citation family + ~15 gate-passing attempts.

### Opção B — Phase-6 fallback (Gayed 1× unleveraged)

Mesma lead V2-L2 mas com alavancagem 1×. Estimativas honest:
~11%/ano CAGR, MDD ~16%, Sharpe ~0.7. Passa gate MDD (4) e bootstrap
(1) mas **abaixo do CDI BR** (mandate §2).

**Pros:** números na mão, passa 2 gates, dá pra shippar em dias.
Aceitar como "passive-like active" sem claim de alpha.
**Cons:** viola mandate §2 (CAGR < CDI). Tese Plano A era
"aggressive leveraged"; Gayed 1× não é isso. Na prática re-rotula
Plano A como Plano C com passos extra.
**Custo imediato:** dias. Re-rodar Gayed L=1, documentar, encerrar.

### Opção C — Abandonar Plano A permanente

Invoca regra `project_plano_a_v2_last_attempt` (sua memória: "se
3.5a-V2 falhar, abandonar permanente"). Realocação per mandate §4.7:
bucket A vai pro Plano C buy-hold.

**Pros:** honesto, encerra o experimento, libera bandwidth. Remove
tentação perene de re-alavancar um non-edge.
**Cons:** você já anulou essa regra uma vez (2026-04-18
`jornada/2026-04-18/23-phase3.5a-v2-WINNER-humana.md`). Pode querer
anular de novo. Bucket A capital vira passivo puro (20-40% → 60-80%
no Plano C).
**Custo imediato:** horas. Só docs — mandate §7 + strategy banner +
jornada closure (já staged em `.pending`).

### Opção D — Freezar Plano A, finalizar Plano B c06-c12

Phase 3.5e Plano B tem 38/144 trials feitos, 106 pendentes em 7
families. Engine do Plano B **está limpa** (F1 confirmou). Um winner
Plano B cobre o bucket 20-40% ativo sozinho (mandate §1).

**Pros:** engine pronta, grid pré-declarado, só relançar loop. Edge
Plano B ainda não exausto.
**Cons:** você mesmo pôs Plano B em stand-by em 2026-04-22 pra focar
no fix. Retomar exige você tirar o stand-by. Não entrega o perfil
agressivo-alavancado do Plano A (se isso importar).
**Custo imediato:** dias de setup + 1-2 semanas de iter budget.

---

## Files pendentes da sua aprovação

Todos staged em `docs/.pending/` (fora dos paths canonicais, então não
entram em mandate/strategy/jornada até você aprovar):

- **`docs/.pending/mandate_section7_entry.md`** — linha nova pro §7
  history table. Registra bug + fix + verdict "no winner".
- **`docs/.pending/plano_a_v2_l2_gayed_cfd_banner.md`** — banner pra
  ir no topo de `docs/strategies/plano_a_v2_l2_gayed_cfd.md`. Texto
  "REJECTED: look-ahead bias in prior engine. Honest: Sharpe
  0.56/CAGR 14%/MDD −37%. Original buggy numbers preserved at §9."
- **`docs/.pending/jornada_readme_update.md`** — rewrite das seções
  "Onde estamos hoje" + "O que vem a seguir" com a forquilha das 4
  opções. (Eu atualizei apenas a lista "Entradas" no jornada/README,
  o resto espera.)

---

## Minhas recomendações (informais, não vinculantes)

Se me pedisse pra rankear em ordem de esperança técnica × custo:

1. **Opção D (Plano B)** é a de maior esperança × menor custo — a
   engine existe, o grid existe, 7 families nunca testadas, e você já
   tinha interesse manifesto em Plano B antes de pausar.
2. **Opção C (abandonar)** é a mais limpa para o projeto — fecha um
   capítulo, libera bandwidth, honra sua própria regra do
   `last_attempt`.
3. **Opção A (V3)** é a mais ambiciosa mas a de pior prior — as 6
   families testadas já eram as canonicals; V3 se apoiaria em science
   mais fina, e eu projeto ~30% chance de passar gates.
4. **Opção B (Gayed 1×)** é a de pior custo-benefício — fica abaixo
   do CDI, viola mandate §2, e só existe pra salvar narrativa.

Mas é sua call, não minha.

---

## Anexos

- **Breadth summary** (main source of truth desta madrugada):
  `reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md`
- **Narrativa do bug** (como foi descoberto, analogia da moeda):
  `jornada/2026-04-22-engine-lookahead-bug.md`
- **Re-validação per lead** (o que cada uma fez):
  `jornada/2026-04-22-plano-a-honest-revalidation.md`
- **Scope audit** (file-by-file do raio do bug):
  `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md`
- **Confirmação técnica** (os 4 testes cirúrgicos):
  `docs/superpowers/findings/2026-04-22-engine-lookahead-confirmation.md`
- **Plano executável original** (referência):
  `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`
- **AGGREGATE per lead:**
  - `reports/phase_3_5f/honest_revalidation/v2_l1_tsmom/AGGREGATE.md`
  - `reports/phase_3_5f/honest_revalidation/v2_l2_gayed_cfd/AGGREGATE.md`
  - `reports/phase_3_5f/honest_revalidation/v2_l3_afml/AGGREGATE.md`
  - `reports/phase_3_5f/honest_revalidation/v2_l4_carver_rp/AGGREGATE.md`
  - `reports/phase_3_5f/honest_revalidation/v2_l5_kalman/AGGREGATE.md`
  - `reports/phase_3_5f/honest_revalidation/v2_l6_vol_breakout/AGGREGATE.md`
- **Forensic banners** (reports afetados):
  - `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/ENGINE_BIAS_FORENSIC.md`
  - `reports/phase3_5a_v2/v2_l4_carver_risk_parity/ENGINE_BIAS_FORENSIC.md`
  - `reports/phase4_0/ENGINE_BIAS_FORENSIC.md`

---

## Para retomar a sessão

Quando você decidir (A/B/C/D), me fale e eu:

1. Merge os files de `.pending/` pros paths canonicais (mandate §7,
   strategy banner, jornada README sections).
2. Fecho a Phase 3.5f com commit final.
3. Abre próxima phase (3.5g / 6.0 / Plano B retomada / encerramento)
   conforme a escolha.

Se quiser, também posso só te mostrar um mock do que cada `.pending`
vai gerar antes de merge.
