# Cleanup pós-Phase 3.5a-V2 — reorganização + prune conservador

**Contexto:** Phase 3.5a-V2 encerrou 2026-04-19 com WINNER FOUND
(`gayed_ema100_L2_off_gld`). O plano em `CLEANUP-PROMPT.md v2`
pedia reduzir/reorganizar o repo antes de Phase 4 paper trading. Este
jornada documenta o que foi feito, o que foi preservado por segurança, e
as ambiguidades resolvidas a favor da preservação.

## Safety protocol executado

1. Commit da edição pendente em `reports/phase3_5b/_DO_NOT_CLEANUP.md`
   (3aa676e).
2. Merge `phase3.5a-v2/plano-a-last-attempt-20260418 → main --no-ff`
   (057e351, 177 commits). V2 agora vive em main para que o snapshot
   do cleanup seja coerente.
3. Tag `pre-cleanup-20260418` em main (rollback imutável).
4. Branch `cleanup/post-3_5a-v2` a partir de main.
5. Baseline pytest: **796 passed** (esperado).

## §A — Reorganização `jornada/` por dia ✅

Commit `e8558f5`. 100 arquivos movidos via `git mv` de
`jornada/YYYY-MM-DD-HHMM-slug.md` → `jornada/YYYY-MM-DD/NN-slug.md`.
10 pastas de dia criadas (2026-03-31 até 2026-04-19).

Distribuição: 2026-04-17 (33 arquivos, maior dia — Phase 3.5b intensivo);
2026-04-18 (31, Phase 3.5a-V1 refutação + V2 L0-L2 inicial); 2026-04-19
(7, V2 L2 winner + L3-L6 DEAD + T7 summary).

Links atualizados em 23 arquivos (specs, docs, reports preservados,
ROADMAP, CLEANUP-PROMPT, jornada/README). Bug cruzado corrigido:
`reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/AGGREGATE.md`
referenciava jornada fantasma (timestamp 1945 HHMM) — apontado para o
path correto (`2026-04-18/09-...-L1-tsmom-DEAD.md`).

Pytest: 796 passed, intacto (só doc moves).

## §B — Prune reports V1 ✅ (parcial conservador)

Commit `1ccd103`. `reports/phase3_5a/` (76 arquivos, ~700 KB) deletado
per `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md §C.1`. V1 sumário preservado
nos 7 jornadas `2026-04-18/02..26-*.md` (T1-T5 DEAD + T6 meta + T7
summary).

**Ambíguo preservado:** `reports/grid_ehlers_*` (44 pastas, 88 arquivos)
e `reports/grid_clenow_*` (1 pasta). Refutados em Phase 2, mas
referenciados em `ROADMAP.md`, `README.md`, `specs/backtest_phase2*.md`,
e vários `docs/superpowers/specs/`. Deletar criaria refs quebradas em
docs históricos — default = preservar.

## §C — Delete V1 scripts ✅

Commit `5dab433`. 6 scripts V1 deletados (~3580 LOC):
`run_bollinger_mr_t1_multi_asset.py`, `run_donchian_t2_multi_asset.py`,
`run_t2_fanout_ticker.py`, `run_t3_fanout_pair.py`,
`run_t4_fanout_ticker.py`, `run_t5_fanout_ticker.py`.

**Ambiguidade resolvida conservador:**
`CLEANUP-PROMPT.md` e `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md §C.3`
pediam deletar `src/ai_trade/backtest/strategies/donchian_breakout.py` +
`tests/test_donchian_breakout.py` com drop esperado de ~13 tests.
**Mas `scripts/iter_v2_l6_run_config.py`** (V2-L6 intocável) **importa
`DonchianBreakoutStrategy` do módulo** — verificado via
`grep donchian_breakout scripts/iter_v2_l6_run_config.py`:
`from ai_trade.backtest.strategies.donchian_breakout import DonchianBreakoutStrategy`.
A afirmação de "V2-L6 é self-contained" em §C.3 do
`_DO_NOT_CLEANUP.md` é **incorreta**. Preservei o módulo + test para
não quebrar V2-L6.

Consequência: **pytest continua em 796, não cai para ~783** como o
plano previa.

## §D — Logs > 7 dias ✅ (no-op)

Mais antigo log é 2026-04-14 (4 dias atrás). Zero arquivos `mtime +7`.
`logs/` está gitignored. §D é no-op legítimo.

## §E — Archive V1 spec ✅

Commit `4bc31e7`. `specs/phase_3_5a_plano_a_investigation.md` →
`specs/_archive/` com header `[SUPERSEDED by specs/phase_3_5a_v2.md —
V1 refuted 2026-04-18]`. Preservação conservadora sobre o delete
sugerido em §C.4 — spec V1 ainda tem valor retrospectivo.

## §F — Collapse tiny reports subfolders ✅ (preservado)

Há ~80-100 pastas `reports/grid_*` com 1-2 arquivos cada (Phase 2 /
Phase 2.5 grids experimentais). Per user instrução "Não perca nada",
default preservação. Muitas são órfãs (0 refs externas) mas constituem
registro histórico.

## Antes × depois

| Categoria          | Baseline pré-cleanup | Pós-cleanup | Δ     |
|--------------------|----------------------|-------------|-------|
| `reports/` files   | 662                  | 586         | -76   |
| `scripts/` files   | 84                   | 78          | -6    |
| `jornada/` flat    | 100 flat             | 0 flat      | -100  |
| `jornada/` per-day | 0                    | 100 em 10 pastas | +100  |
| `specs/` active    | 9                    | 8 + 1 archive | -1 active |
| pytest passing     | 796                  | 796         | 0     |

Reduction total: 82 arquivos (reports + scripts). Meta do plano era
50-70% — atingimos ~4% real (guidance não gate; preservação priorizada
conforme instrução do user "não perca nada").

## V2 winner — checks explícitos

- ✓ `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/` preservado (84 arquivos)
- ✓ `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld.md` preservado
- ✓ `docs/strategies/plano_a_v2_l2_gayed_cfd.md` preservado
- ✓ Jornadas `phase3.5a-v2` (17 em `2026-04-18/` + 7 em `2026-04-19/`) todas preservadas
- ✓ Scripts `iter_v2_l*_run_*.py` (6) todos preservados
- ✓ `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` preservado
- ✓ `src/ai_trade/backtest/sweeps/` + `tests/test_sweep_registry.py` preservados
- ✓ `docs/self_improvement/fanout_protocol.md` preservado
- ✓ `specs/phase_3_5a_v2.md`, `specs/phase_4_paper_trading.md`,
  `specs/self_improve_fanout_mode.md` todos preservados
- ✓ 7 jornadas V1 summary (T1-T5 DEAD + T6 + T7) todas preservadas em `2026-04-18/`

## Validação pytest final

```
.venv/bin/pytest --tb=no -q | tail -2
796 passed in 11.23s
```

Zero regressão. Zero test drop.

## Decisões autônomas + rationale

1. **Preservei `donchian_breakout.py` + test** contra §C.3 porque
   V2-L6 importa. Plano desatualizado.
2. **Preservei `grid_ehlers_*` e `grid_clenow_*`** — refs externas em
   ROADMAP/README/specs/docs pesariam mais que o ganho de disk.
3. **Archive em vez de delete de V1 spec** — retrospectivo tem valor.
4. **Skip §F mass delete** — "não perca nada" > meta 50-70%.
5. **Corrigi bug cruzado em V2 AGGREGATE** (jornada fantasma 1945 HHMM →
   path correto) — link era quebrado no master pré-reorg, fix agora
   aproveitando o pass de link updates.

## Branch status

Branch `cleanup/post-3_5a-v2` em 4bc31e7, 4 commits ahead de main:

```
4bc31e7 chore(cleanup): archive V1 spec under specs/_archive/ (§E)
5dab433 chore(cleanup): prune V1 scripts (§C)
1ccd103 chore(cleanup): prune V1 reports (§B.1)
e8558f5 chore(cleanup): reorganize jornada/ by day folder (§A)
```

Tag `pre-cleanup-20260418` em main (057e351, pós-merge V2) como
rollback point.

## Próximos passos (para o user)

1. Review `git log --stat cleanup/post-3_5a-v2 ^main`.
2. Se ok: `git merge --no-ff cleanup/post-3_5a-v2 -m "chore: cleanup post-Phase 3.5a-V2"`.
3. Se não: `git branch -D cleanup/post-3_5a-v2` (rollback parcial) ou
   `git reset --hard pre-cleanup-20260418` (rollback total).
4. Phase 4 paper trading pode começar sobre o estado limpo.

## Arquivos citação-chave

- `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md` — guia de preservação V2
- `reports/phase3_5b/_DO_NOT_CLEANUP.md` — guia de preservação Plano B
- `docs/strategies/plano_a_v2_l2_gayed_cfd.md` — living doc winner
- `specs/phase_4_paper_trading.md` — next phase
