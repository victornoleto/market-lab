# Phase 3.5a-V2 — DO NOT CLEANUP

**Marcador de proteção + guia de cleanup seletivo.**

---

## ⚠️ Nota sobre paths de jornadas

Jornadas citadas neste documento usam paths **pré-reorganização**
(formato flat `jornada/YYYY-MM-DD-HHMM-slug.md`). Quando o cleanup
executar `CLEANUP-PROMPT.md §A`, as jornadas serão movidas para
`jornada/YYYY-MM-DD/NN-slug.md`. O agente de cleanup é instruído a
**re-gravar este documento substituindo os paths pelos novos**
antes de prosseguir com §B-F.

Se você está lendo este arquivo pós-cleanup e os paths abaixo parecem
desatualizados, a reorganização foi concluída — use os paths novos
(consulte `jornada/README.md` para o mapeamento).

---

## Filosofia de cleanup (decidida com usuário 2026-04-18)

1. **V2 (winner encontrado):** preservar com **detalhamento máximo** — este é o
   código e docs do Plano A em produção próxima.
2. **V1 (framework errado, refutado):** preservar apenas **nível de sumário**
   — o que foi, por que falhou, quais problemas. O resto (per-ticker reports,
   per-ticker FAIL jornadas, V1 scripts) **pode ser removido** pra focar o
   repo no que é relevante.

Objetivo: repo compacto, sem ambiguidade sobre o que é produção (V2) vs
research log histórico (V1).

---

## Status (2026-04-18/19)

Phase 3.5a-V2 **encerrada com WINNER**:
- Winner: `gayed_ema100_L2_off_gld` — Sharpe OOS 2.285, CAGR 79.14%, MDD -21.02%
- 13/13 gates V2 pass (PBO 0.103, DSR p 0.000288, bootstrap 99.9% CI low 0.962)
- Stop rule binding NÃO dispara (1 PASS ≥ 1 requerido) — Plano A retido
- Próxima fase: `specs/phase_4_paper_trading.md` (paper dual-path, 4 meses)

Phase 3.5a (V1) encerrada como **refutada** em 2026-04-18:
- 42 iters / 143 runs em 6 famílias, 0 winners
- Framework errado: 1h FX retail, hold ≤5d, universe pequeno
- Diagnóstico completo em T6+T7 jornadas

---

## SEÇÃO A — IMMUTABLE (V2 — preservar TUDO)

### A.1 `reports/phase3_5a_v2/` (223 arquivos, 400+ KB)

**Regra: NADA abaixo deste diretório deve ser deletado.** Toda métrica, curva,
config, é evidência do winner e dos 5 DEADs estruturais.

```
reports/phase3_5a_v2/
├── AGGREGATE.md                           ← cross-lead L1-L6 (final verdict)
├── L0_universe_screener.md                ← 39 instrumentos validados
├── v2_l1_tsmom_multi_asset_daily/         ← TSMOM DEAD (38 files)
│   ├── AGGREGATE.md + registry.json
│   ├── 12 configs × JSON + parquet returns
├── v2_l2_gayed_transported_cfd/  ★★★      ← WINNER (84 files)
│   ├── AGGREGATE.md + AGGREGATE.json + registry.json
│   ├── 27 configs × JSON + MD + parquet returns
│   └── gayed_ema100_L2_off_gld.{json,md}  ← configuração canônica winner
├── v2_l3_afml_triple_barrier_meta/        ← AFML DEAD (38 files)
├── v2_l4_carver_risk_parity/              ← Carver RP DEAD (3 files)
├── v2_l5_equity_pairs/                    ← pairs DEAD (20 files)
└── v2_l6_vol_breakout/                    ← vol-breakout DEAD (38 files)
```

### A.2 Código fonte V2 (src/)

**Strategy implementation (imutável):**
- `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` — strategy do winner V2-L2
- `tests/test_plano_a_leveraged_rotation.py` — testes (preservar baseline pytest)

**Infra fan-out (criada em V2, reutilizada em futuras fases):**
- `src/ai_trade/backtest/sweeps/registry.py` + `__init__.py` — registry schema v1
- `tests/test_sweep_registry.py` — 32 testes de race condition + invariantes
- `scripts/smoke_fanout_protocol.py` — E2E smoke verifier (para regressão futura)
- `docs/self_improvement/fanout_protocol.md` — protocolo lido pelos agentes em SWEEP_MODE=fanout

**Loop self-improve (estendido em V2):**
- `scripts/self_improve_loop.sh` — com SWEEP_MODE branch adicionado

### A.3 Scripts V2 (iter scripts dos 6 leads)

Preservar todos — são os geradores reproduzíveis dos artefatos em `reports/phase3_5a_v2/`:

```
scripts/iter_v2_l1_run_config.py           (TSMOM, 534 LOC)
scripts/iter_v2_l2_run_config.py           (Gayed transport, 495 LOC) ★★★ winner
scripts/iter_v2_l3_run_ticker.py           (AFML meta-label, 461 LOC)
scripts/iter_v2_l4_carver_rp_atomic.py     (Carver RP blend, 317 LOC)
scripts/iter_v2_l5_run_pair.py             (equity pairs, 462 LOC)
scripts/iter_v2_l6_run_config.py           (vol breakout, 643 LOC)
```

### A.4 Specs e docs V2

- `specs/phase_3_5a_v2.md` — spec contrato executado (522 linhas)
- `specs/phase_4_paper_trading.md` — próxima fase, drafted T7 autônomo
- `specs/self_improve_fanout_mode.md` — spec da infra fan-out
- `docs/strategies/plano_a_v2_l2_gayed_cfd.md` — **living strategy doc canônico**

### A.5 Jornadas V2 (preservar TODAS)

**Narrativa humana e T7 agente (obrigatórios):**
- `jornada/2026-04-18-1900-phase3.5a-v2-WINNER-humana.md` ★ narrativa humana
- `jornada/2026-04-19-0510-phase3.5a-v2-summary-WINNER-FOUND.md` — T7 autônomo
- `jornada/2026-04-19-0020-phase3.5a-v2-L2-gayed-transported-PASS.md` ★ winner PASS

**DEAD aggregates V2 (um por lead refutado):**
- `jornada/2026-04-18-1407-phase3.5a-v2-L1-tsmom-DEAD.md`
- `jornada/2026-04-19-0115-phase3.5a-v2-L3-afml-triple-barrier-DEAD.md`
- `jornada/2026-04-19-0215-phase3.5a-v2-L4-carver-blend-DEAD.md`
- `jornada/2026-04-19-0310-phase3.5a-v2-L5-equity-pairs-DEAD.md`
- `jornada/2026-04-19-0410-phase3.5a-v2-L6-vol-breakout-DEAD.md`

**V2-L2 sweep trail (preservar — processo de descoberta do winner):**
- `jornada/2026-04-18-1324-phase3.5a-v2-L0-universe-screener.md`
- `jornada/2026-04-18-1341-phase3.5a-v2-L1-tsmom-lb1m-weekday-bug.md` (bug encontrado, instrutivo)
- `jornada/2026-04-18-1421-phase3.5a-v2-L2-gayed-sma200-L2-cash-baseline-strong.md`
- `jornada/2026-04-18-15*-phase3.5a-v2-L2-gayed-sma200-*.md` (3 arquivos, trail SMA200)
- `jornada/2026-04-18-16*-phase3.5a-v2-L2-gayed-ema100-*.md` (2 arquivos, 1ª SUBSET PASS)
- `jornada/2026-04-18-17*-phase3.5a-v2-L2-*.md` (1 arquivo)
- `jornada/2026-04-18-21*-phase3.5a-v2-L2-*.md` (1 arquivo)
- `jornada/2026-04-18-22*-phase3.5a-v2-L2-*.md` (3 arquivos, 2 SUBSET PASS + 1 FAIL)
- `jornada/2026-04-18-23*-phase3.5a-v2-L2-*.md` (2 arquivos, L3/L5 patterns)
- `jornada/2026-04-19-0240-phase3.5a-v2-L5-xlf-hyg-FAIL-sweep-complete.md`

Estes jornadas sweep documentam as **3 invariantes de leverage** descobertas +
a hipótese-verificação iterativa do agente (predições hit 3/3 em vários
iters). São evidência do processo — não deletar.

### A.6 Mandate e memory

- `docs/investment-mandate.md` — §7 histórico inclui entries V1 close + V2 launch + V2 close
- `docs/self_improvement/memory.md` — local state, já em gitignore (não afeta cleanup)

---

## SEÇÃO B — SALVAGE (V1 — preservar SÓ sumário)

Propósito: "não precisar revisitar isso de novo" — preservar o **aprendizado**,
não os dados detalhados.

### B.1 Jornadas V1 que DEVEM ser preservadas (7 arquivos)

Estas 7 jornadas contam a história V1 completa em nível de sumário:

```
jornada/2026-04-18-0130-phase3.5a-T1-bollinger-mr-fx-metals-DEAD.md   (T1 DEAD)
jornada/2026-04-18-1500-phase3.5a-T2-donchian-breakout-DEAD.md        (T2 DEAD)
jornada/2026-04-18-1420-phase3.5a-T3-pairs-statarb-DEAD.md            (T3 DEAD)
jornada/2026-04-18-1545-phase3.5a-T4-session-based-fx-DEAD.md         (T4 DEAD)
jornada/2026-04-18-1800-phase3.5a-T5-regime-filter-hybrid-DEAD.md     (T5 DEAD)
jornada/2026-04-18-2100-phase3.5a-T6-rebalance-meta-mandate-override.md  (T6 meta)
jornada/2026-04-18-2200-phase3.5a-T7-summary-close-PLANO-A-abandoned.md  (T7 summary)
```

**Justificativa:** cada DEAD aggregate explica por que uma família específica
(MR, breakout, pairs, session, regime-filter) não sobreviveu gates em 1h FX
retail. Juntos + T6+T7 = a história V1 completa em ~70 KB.

Se alguém um dia perguntar "por que não BollingerMR canonical?" ou "por que
não Donchian 1h?", a resposta está nesses 7 arquivos.

---

## SEÇÃO C — PRUNABLE (remover no cleanup)

Tudo abaixo pode ir com segurança. V1-específico, redundante com jornadas
preservadas, ou já superado por V2.

### C.1 `reports/phase3_5a/` inteiro (76 arquivos, ~700 KB)

```bash
rm -rf reports/phase3_5a/
```

Motivo: per-ticker reports (t1_*, t2_*, t3_*, t4_*, t5_*) são detalhes
granulares que não adicionam além do que o DEAD aggregate jornada já diz.
Se alguém precisar re-verificar um ticker específico de V1, pode re-rodar o
backtest (mas não há motivo — a família já foi refutada).

### C.2 Scripts V1 (6 arquivos, ~3580 LOC)

```bash
rm scripts/run_bollinger_mr_t1_multi_asset.py    # T1 generator
rm scripts/run_donchian_t2_multi_asset.py        # T2 generator (primeiro)
rm scripts/run_t2_fanout_ticker.py               # T2 fan-out runner
rm scripts/run_t3_fanout_pair.py                 # T3 fan-out runner
rm scripts/run_t4_fanout_ticker.py               # T4 fan-out runner
rm scripts/run_t5_fanout_ticker.py               # T5 fan-out runner
```

Motivo: geram artefatos em `reports/phase3_5a/` (já deletado em C.1). Nenhum
destes scripts é reutilizável em V2 — V2 tem seus próprios geradores em
`scripts/iter_v2_l*.py`. Strategies testadas por eles (BollingerMR canonical,
Donchian 1h, Kalman pairs FX, session-based FX, regime filter) são todas
DEAD e não vão ser re-testadas.

### C.3 Strategy e test V1 refutados (2 arquivos)

```bash
rm src/ai_trade/backtest/strategies/donchian_breakout.py
rm tests/test_donchian_breakout.py
```

Motivo: Donchian breakout foi implementado para V1-T2 (refutado 0/36 PASS).
Nunca foi usado em V2 — V2-L6 (vol breakout) usa um Donchian variant dentro
de `scripts/iter_v2_l6_run_config.py`, self-contained. Remoção abaixa pytest
baseline em ~13 tests — mas esses são testes de strategy refutada, aceitável.

**IMPORTANTE:** ao remover, **rodar** `.venv/bin/pytest -q` para garantir que
nenhum outro teste importa `donchian_breakout`. Se houver dependência, resolver
antes do rm.

### C.4 V1 spec (1 arquivo)

```bash
rm specs/phase_3_5a_plano_a_investigation.md
```

Motivo: este é o contrato V1 executado. A história do V1 está preservada
nas 7 jornadas DEAD (B.1). O spec V1 só tem valor retrospectivo como
"o que foi tentado" — já coberto pelas jornadas.

Alternativa mais conservadora: manter o arquivo mas adicionar header
`# [SUPERSEDED by specs/phase_3_5a_v2.md]` no topo. Usuário decide.

### C.5 Jornadas V1 per-ticker FAIL (2 arquivos)

```bash
rm jornada/2026-04-18-1015-phase3.5a-T2-eurgbp-FAIL.md
rm jornada/2026-04-18-1430-phase3.5a-T2-usdcad-FAIL.md
```

Motivo: per-ticker FAIL jornadas (apenas 2 foram geradas em V1 T2). Ambos
são redundantes com `T2-donchian-breakout-DEAD.md` que consolida os 12
tickers. Índice cross-ticker está na DEAD aggregate.

### C.6 Jornada T0 infra V1 (opcional)

```bash
rm jornada/2026-04-18-0105-phase3.5a-T0-tiingo-fx-pull.md
```

Motivo: este jornada documenta o pull inicial de Tiingo FX daily+1h. O
cache `data/tiingo/` permanece intacto e é o que importa. A jornada é só
narrativa histórica do pull (bugfixes no tiingo_source.py, pagination,
resampleFreq). Se alguém precisar entender esses bugfixes, git log nos
arquivos correspondentes dá a info.

**Alternativa:** manter (é apenas 1 arquivo compacto). Decisão estética.

### C.7 Atualizar índice de jornadas após cleanup

Após executar os `rm`s acima:

```bash
# Remover entries correspondentes em jornada/README.md
# (manual edit — grep + delete lines referenciando os arquivos prunados)
```

---

## Cleanup script copy-paste (executar em ordem)

```bash
cd /var/www/pessoal/ai-trade

# Safety: verificar que estamos em branch V2 (não merged em main ainda)
git branch --show-current
# Esperado: phase3.5a-v2/plano-a-last-attempt-20260418 (ou branch sucessora)

# Baseline pytest antes do cleanup
.venv/bin/pytest -q 2>&1 | tail -1
# Esperado: 796 passed (ou superior pós-V2)

# --- EXECUTE SOMENTE APÓS REVISÃO ---

# C.1: V1 reports
rm -rf reports/phase3_5a/

# C.2: V1 scripts
rm scripts/run_bollinger_mr_t1_multi_asset.py
rm scripts/run_donchian_t2_multi_asset.py
rm scripts/run_t2_fanout_ticker.py
rm scripts/run_t3_fanout_pair.py
rm scripts/run_t4_fanout_ticker.py
rm scripts/run_t5_fanout_ticker.py

# C.3: V1 strategy + test (CUIDADO: pytest drop esperado)
rm src/ai_trade/backtest/strategies/donchian_breakout.py
rm tests/test_donchian_breakout.py

# C.4: V1 spec
rm specs/phase_3_5a_plano_a_investigation.md

# C.5: V1 per-ticker FAIL jornadas
rm jornada/2026-04-18-1015-phase3.5a-T2-eurgbp-FAIL.md
rm jornada/2026-04-18-1430-phase3.5a-T2-usdcad-FAIL.md

# C.6 (opcional): T0 infra jornada
# rm jornada/2026-04-18-0105-phase3.5a-T0-tiingo-fx-pull.md

# Verificar pytest pós-cleanup
.venv/bin/pytest -q 2>&1 | tail -1
# Esperado: ~783 passed (796 - 13 tests de donchian_breakout). Zero errors/failures.

# Commit em branch cleanup dedicada
git checkout -b chore/cleanup-v1-artifacts-post-v2
git add -A
git commit --no-gpg-sign -m "chore: prune V1 artifacts after V2 winner consolidated

V1 refutated 2026-04-18 (42 iters, 143 runs, 0 PASS). V2 winner found
same day (gayed_ema100_L2_off_gld). V1 summary preserved in 7 jornadas
(T1-T5 DEAD + T6 meta + T7 summary). V1 per-ticker details + scripts
+ refutated strategy + spec pruned per reports/phase3_5a_v2/_DO_NOT_CLEANUP.md.

Pytest baseline: 796 → ~783 (lost 13 tests of refutated donchian_breakout
strategy). Zero functional regressions.
"

# Update jornada/README.md manual (remover entries dos arquivos prunados)
# depois commit separado
```

---

## Instruções para cleanup pós-cleanup (i.e., próximas fases)

Quando cleanup adicional rodar após Phase 4 ou Phase 5:

1. **Não mexer em nada sob `reports/phase3_5a_v2/`.**
2. **Não deletar** `scripts/iter_v2_l*.py`, `scripts/smoke_fanout_protocol.py`,
   `src/ai_trade/backtest/sweeps/`, `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py`,
   `tests/test_sweep_registry.py`, `tests/test_plano_a_leveraged_rotation.py`.
3. **Não mexer em jornadas `phase3.5a-v2`** (todas as 20+ arquivos).
4. **Não mexer em `docs/strategies/plano_a_v2_l2_gayed_cfd.md`** — living doc.
5. **Não mexer nas 7 jornadas V1 preservadas** (B.1) — são o sumário V1.
6. **Não mexer em `specs/phase_3_5a_v2.md`, `specs/phase_4_paper_trading.md`,
   `specs/self_improve_fanout_mode.md`.**
7. **Não mexer em `docs/self_improvement/fanout_protocol.md`.**

---

## Se precisar mexer (excepcionalmente)

Só modificar Phase 3.5a-V2 se:

1. **Bug genuíno** em `plano_a_leveraged_rotation.py` ou `sweeps/registry.py`
   (improvável — 13/13 gates + 32 testes de registry + race condition passados).
2. **Mudança de broker** (se Pepperstone SCB encerrar, impactando Plano A) —
   aí re-avaliar via novo jornada + update em `docs/strategies/plano_a_v2_l2_gayed_cfd.md §4`.
3. **Nova evidência empírica** (ex: SPY/QQQ share CFD delist em Pepperstone)
   que invalide execução — novo jornada + update mandate §7 + atualizar
   estratégia doc.
4. **Paper trading Phase 4** revelar divergência > 30% do backtest — aí
   **re-calibrar** (não re-otimizar — contrato V2 proíbe V3 da busca).
   Calibração de cost model é OK; re-busca de família é proibida.

Em qualquer outro caso: **não tocar**.

---

## Referência cruzada

- Plano B (`reports/phase3_5b/_DO_NOT_CLEANUP.md`) tem política análoga
  para os sleeves LETF em produção.
- Mandate §7 (`docs/investment-mandate.md`) tem histórico completo.
- Memory (`docs/self_improvement/memory.md`) está em gitignore — não afeta
  cleanup.
- Jornada README (`jornada/README.md`) deve ser atualizada pós-cleanup
  (remover entries de arquivos prunados em C.5, C.6).
