# Task 006 — Wire Fase 1 modules em pipeline.py

**Phase:** 1 | **Effort:** 2 sessoes | **Depends on:** 002, 003, 004, 005

## Goal

Conectar `pre_decode_screen` e `adversarial_validator` em `workbench/pipeline.py`
e `scripts/run_replicator_batch.py` via flags opt-in. Garantir backward-compat:
pipeline antigo continua rodando sem flags.

## Mudancas em workbench/pipeline.py

Adicionar argumentos CLI:

```python
parser.add_argument("--enable-pre-screen", action="store_true",
    help="Roda pre_decode_screen antes do Stage 1; aborta se decision=STOP")
parser.add_argument("--enable-adversarial", action="store_true",
    help="Roda adversarial_validator no synthetic_trades.parquet apos backtest")
```

Quando `--enable-pre-screen`:
1. Chamar `screen_system(account_oid)` antes de `_load_trades()`
2. Salvar `systems/<id>/pre_decode_screen.json`
3. Se `decision="STOP"`, abortar com codigo 0 e log "EA rejeitado pelo pre-screen"
   (nao e erro — e comportamento esperado)

Quando `--enable-adversarial`:
1. Apos backtest produzir `synthetic_trades.parquet`, carregar tambem `real`
   (`trades.parquet`)
2. Chamar `adversarial_validate(real, synthetic)`
3. Adicionar `adversarial_auc`, `adversarial_auc_ci`, `adversarial_top_features`
   em `pipeline_summary.json`

## Mudancas em scripts/run_replicator_batch.py

Mesmas flags, propaga para `pipeline.py` por system. Acumular resultados no
`batch_summary.json` com novos campos.

## Mudancas em gates.py wiring

Quando `pipeline_summary.json` contem `dsr_p` e PBO disponivel, gates aplicam o
hard pass/fail novo (task 004).

## Smoke tests

```bash
# 1. Sem flags — deve rodar identico ao baseline antigo
uv run python -m studies.myfxbook_reverse_engineering.workbench.pipeline \
  --account-oid 10281851

# 2. Com pre-screen em EA Real estatisticamente forte (golden PASS)
#    Esperado: pre_decode_screen.json com decision=GO, is_live=True; pipeline segue normal.
uv run python -m studies.myfxbook_reverse_engineering.workbench.pipeline \
  --account-oid 10281851 --enable-pre-screen

# 3. Com pre-screen em EA Real martingale (golden STOP)
#    Esperado: pre_decode_screen.json com decision=STOP por K1 sanity FAIL; pipeline aborta cedo.
uv run python -m studies.myfxbook_reverse_engineering.workbench.pipeline \
  --account-oid 11504701 --enable-pre-screen

# 4. Demo warning-only: EA Demo pode passar (decision=GO se outros gates ok),
#    mas is_live=False e registrado.
uv run python -m studies.myfxbook_reverse_engineering.workbench.pipeline \
  --account-oid 1407880 --enable-pre-screen
# Verificar pre_decode_screen.json: is_live=False, decision pode ser GO ou STOP
# mas NAO por causa do flag Demo.

# 5. Full pipeline com pre-screen + adversarial
uv run python -m studies.myfxbook_reverse_engineering.workbench.pipeline \
  --account-oid 10281851 --enable-pre-screen --enable-adversarial
```

## Files to modify

- `workbench/pipeline.py` — adicionar flags e wiring
- `scripts/run_replicator_batch.py` — propaga flags
- (opcional) `shared/replicator.py` — apenas se interfacear com novo
  `pipeline_summary.json` schema

## Verificacao

```bash
# Testes existentes nao quebram
uv run pytest tests/ -q

# Smoke 1-4 acima rodam sem erro inesperado
```

## Aceite

- [ ] Flags `--enable-pre-screen` e `--enable-adversarial` funcionam
- [ ] Sem flags: pipeline antigo intacto (backward-compat)
- [ ] Smoke 1-4 passam
- [ ] `pipeline_summary.json` ganha campos novos quando flags ativas
- [ ] Baseline 461 testes preservado

## Kill-switches

- Pre-screen quebra pipeline em system com dados parciais → catch + skip + log
- Adversarial quebra quando synthetic vazio → catch + adversarial_auc=null + log
