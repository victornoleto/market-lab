# Spec — Self-improve loop fan-out mode (per-ticker sub-iterations)

Adicionar um **modo fan-out** ao `scripts/self_improve_loop.sh` em que um
Lead que varre `N tickers × M configs` é quebrado em `N` sub-iterações
(uma por ticker), cada sub-iter gravando resultados em arquivos e
deixando um **registry.json** como continuidade entre sessões. Motivação
direta: iter 3 da Phase 3.5a (Lead T2 Donchian) **bateu timeout 1800s**
tentando rodar 12 FX × 9 configs num único processo.

**Branch de trabalho:** mesma em que a Phase que consumir o modo rodar
(não tem branch própria — é infra).

**Execução:** mudança no shell script + no prompt do loop + novo
protocolo documentado que o agente do loop segue. **Backwards-compat:**
modo legado (1 Lead / 1 iter) continua default; fan-out é opt-in via
`SWEEP_MODE=fanout`.

---

## 0. Contexto

O loop hoje tem um contrato simples: **1 iter = 1 Lead completo**.
Funciona bem para leads atômicos (ex: Phase 3.5b Task C4 —
`apply_threshold_rebalance()` + 6 testes + jornada → 1 iter gordo mas
fechado).

Falha em leads de **sweep multi-ticker** porque:

1. `ITER_TIMEOUT=1800s` é cap físico (`timeout 1800 claude -p ...`).
   Backtest Donchian em 12 FX × 9 configs × CPCV + PBO + stress roda
   bem acima disso, mesmo em foreground.
2. Mesmo quando cabe, o agente às vezes dispara em **background** e
   dorme esperando notificação — queima o timeout sem progresso
   observável.
3. Se o iter crasha ou dá timeout, **zero progresso persistido**: o
   próximo iter começa do zero. Sem checkpoint por ticker.
4. Commits atômicos ficam gigantes (50 arquivos num commit só),
   difíceis de inspecionar/reverter.

**Padrão análogo que já funciona:** `scripts/tiingo_bulk_download.py`
processa 1 ticker/call, escreve `manifest.json` como registry, retoma
do meio se interrompido. Este spec exporta esse padrão para backtests.

---

## 1. Scope

### Dentro do scope

- Novo modo `SWEEP_MODE=fanout` no `scripts/self_improve_loop.sh`.
- Protocolo documentado em `docs/self_improvement/fanout_protocol.md`
  que o agente do loop lê quando `SWEEP_MODE=fanout`.
- Schema do **registry.json** per-lead (§3).
- Schema do **per-ticker result file** (`<ticker>.json` + `<ticker>.md`)
  (§5).
- Aggregator protocol para o iter final de cada lead (§6).
- Loop prompt (`build_prompt()`) ganha branch condicional quando
  `SWEEP_MODE=fanout` — instrui agente a seguir o protocolo
  sub-iteration.
- Migration: retrofit dos leads T2-T5 da Phase 3.5a (T2 Donchian, T3
  pairs, T4 session, T5 regime filter) para usar fan-out. T0/T1/T6/T7
  ficam no modo legado.

### Fora do scope

- Paralelização de iters (1 iter por vez permanece).
- Cache compartilhado entre leads (cada lead tem seu próprio registry).
- Resumir registry em memory.md — registry é sidecar, memory.md só
  aponta para ele (§4).
- Retrofit de leads já consumidos (T0 DONE, T1 DEAD END ficam como
  estão).
- Framework genérico para outras fases — Phase 3.5a é o único
  consumidor imediato; generalização vira spec separada se outras fases
  precisarem.

---

## 2. Design decisions (resumo)

| Decisão | Escolha | Rationale |
|---------|---------|-----------|
| Granularidade da sub-iter | 1 ticker × todos os configs do lead | `[advances_fin_ml, ch.4]` trial-counting: configs do mesmo lead são uma única família (N_trials agregado por lead, não por ticker). Manter agregação por ticker mantém custos ≤ 10min/iter. |
| Registry location | `reports/phase3_5a/<lead_slug>/registry.json` | Scoped per-lead, commitado junto com os per-ticker files, não polui memory.md. |
| Memory.md tracking | Só aponta `active_lead_registry:` path + status (`pending`/`sweeping`/`aggregating`/`done`) | memory.md permanece < 15 KB; detalhe fica no registry. |
| Resumo por ticker | `<ticker>.md` + `<ticker>.json` | `.md` lê fácil no PR/review; `.json` é machine-readable pra aggregator. |
| Agregador | Iter final do lead, quando `tickers_pending == []` | Separação clara: sub-iters = worker, aggregator = reducer. |
| Citação | Aplicada a decisões de strategy dentro de cada sub-iter (mesmo gate do CLAUDE.md regra 2) | Infra deste spec não exige livro; strategy dentro sim. |
| Backwards-compat | `SWEEP_MODE` default `off` | Leads legacy (Phase 3, 3.5b) não mudam comportamento. |

---

## 3. Registry schema (`reports/<phase>/<lead_slug>/registry.json`)

Schema v1 — validado no início de cada sub-iter (fail-fast se
inconsistente). **Nunca editar `tickers_done` retroativamente;
append-only.** Writes atômicos via tmp→rename.

```json
{
  "schema_version": 1,
  "phase": "phase3_5a",
  "lead_id": "T2",
  "lead_slug": "t2_donchian_breakout_intraday",
  "lead_title": "Donchian/ATR breakout 1h FX + index CFD",
  "citations_seed": ["trading_systems_methods, p.353", "volatility_trading"],
  "started_at": "2026-04-18T02:00:00-03:00",
  "last_updated_at": "2026-04-18T02:15:33-03:00",
  "configs": [
    {"name": "donch_10_5_long",  "type": "donchian", "entry_lookback": 10, "exit_lookback": 5,  "direction": "long"},
    {"name": "donch_10_5_short", "type": "donchian", "entry_lookback": 10, "exit_lookback": 5,  "direction": "short"},
    {"name": "donch_20_10_long", "type": "donchian", "entry_lookback": 20, "exit_lookback": 10, "direction": "long"}
  ],
  "tickers_pending": ["GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "XAUUSD", "XAGUSD"],
  "tickers_done": [
    {
      "ticker": "EURUSD",
      "frequency": "1hour",
      "window_start": "2020-01-01",
      "window_end":   "2026-04-17",
      "iter": 4,
      "n_configs_tested": 3,
      "best_config": "donch_20_10_long",
      "best_sharpe_oos": 0.42,
      "best_cagr": 0.08,
      "best_maxdd": -0.17,
      "any_pass_5gate": false,
      "median_hold_days": 2.3,
      "result_file_md":   "reports/phase3_5a/t2_donchian_breakout_intraday/EURUSD.md",
      "result_file_json": "reports/phase3_5a/t2_donchian_breakout_intraday/EURUSD.json"
    }
  ],
  "tickers_errored": [],
  "status": "sweeping",
  "aggregation_iter": null,
  "aggregate_file_md":   null,
  "aggregate_jornada":   null
}
```

### Campos fundamentais

- **`status`** state machine: `pending` → `sweeping` → `aggregating` → `done`.
  - `pending`: registry recém-criado, nenhum ticker processado.
  - `sweeping`: pelo menos 1 ticker done, ≥ 1 pendente.
  - `aggregating`: `tickers_pending == []` mas aggregator ainda não rodou.
  - `done`: aggregator rodou, `aggregate_file_md` preenchido.

- **`configs`** é fixo após criação do registry. Se o agente quiser
  testar novas configs, cria **novo registry** com lead_id diferente
  (ex: `T2b`) — registry é imutável em sua configuração.

- **`tickers_errored`** guarda falhas (arquivo não encontrado, bug na
  strategy, etc) com `{ticker, iter, error_msg}`. Aggregator decide
  se re-queue ou marca como dead.

---

## 4. Per-iteration protocol (agent behavior)

Quando `SWEEP_MODE=fanout` está ativo, o prompt do loop instrui o
agente a seguir este protocolo (§7 implementa a branch do build_prompt).

### 4.1 Bootstrap (primeiro iter do lead)

1. Ler memory.md. Se `active_lead_registry` == null (ou aponta para
   lead já `done`): pegar próximo lead pendente, gerar `lead_slug`
   (snake_case), criar pasta `reports/<phase>/<lead_slug>/`.
2. Gerar registry inicial:
   - `configs`: listar explicitamente todas as configs que serão
     testadas no lead (deriva do spec da fase).
   - `tickers_pending`: universo completo (ex: 12 FX + metais para T2).
   - `tickers_done`: `[]`.
   - `status`: `pending`.
3. Escrever `registry.json` atomicamente.
4. Atualizar memory.md: `active_lead_registry: reports/<phase>/<lead_slug>/registry.json`.
5. Exit iter — não processa ticker nesse iter (bootstrap é separado
   do primeiro sweep pra deixar o diff pequeno/revisável).

### 4.2 Sweep iter (1 ticker por iter)

1. Ler `active_lead_registry` path em memory.md. Ler registry.
2. Pick `tickers_pending[0]` — primeiro pendente. **Não aleatório**,
   garante ordem determinística.
3. Rodar o backtest do ticker × `configs`. Aplicar os mesmos gates do
   spec da fase (5-gate framework, median hold, custos brokers, etc).
4. **Gravar dois arquivos atomicamente:**
   - `reports/<phase>/<lead_slug>/<ticker>.json` — full results
     (todas configs, todas métricas, trade logs).
   - `reports/<phase>/<lead_slug>/<ticker>.md` — summary humano
     (tabela formato `backtesting.py` + benchmark SPY para o best
     config, referências aos outros configs na tabela).
5. Atualizar registry:
   - `tickers_pending`: pop(0).
   - `tickers_done`: append `{ticker, iter, best_config, best_sharpe_oos, ..., result_file_md, result_file_json}` (campos §3).
   - `status`: `sweeping` (se `tickers_pending != []`) ou
     `aggregating` (se ficou vazio).
   - `last_updated_at`: agora.
6. Atualizar memory.md: só bumpar `iteration` + appending terse
   History entry (1 linha: `iter N — T2 swept EURUSD 1h: best donch_20_10_long Sharpe_oos=0.42 no PASS`).
7. Shell loop commita automaticamente (commit já contém registry +
   per-ticker files).

### 4.3 Aggregator iter (quando tickers_pending vazio)

1. Registry status == `aggregating`.
2. Ler todos os `<ticker>.json` do lead.
3. Gerar `reports/<phase>/<lead_slug>/AGGREGATE.md` (§6).
4. Criar jornada `jornada/<date>-<phase>-<lead_id>-<verdict>.md`
   (ex: `2026-04-18-phase3.5a-T2-donchian-DEAD.md`).
5. Atualizar registry:
   - `status`: `done`.
   - `aggregation_iter`: iter atual.
   - `aggregate_file_md`, `aggregate_jornada`: paths.
6. Atualizar memory.md:
   - `active_lead_registry`: null (libera próximo lead).
   - Se algum ticker PASS: append winner em `winners_short_hold:` ou
     `winners_swing:` com reference ao AGGREGATE.md.
   - Se 0 PASS: mover lead para `## Dead ends`.
   - Append `★ PASS` ou `DEAD END` History entry (5 linhas max).
7. Shell loop commita.

### 4.4 Error handling

- **Ticker falha** (strategy exception, dados corrompidos): gravar
  `{ticker, iter, error_msg}` em `tickers_errored`, pop do
  `tickers_pending`, seguir. Aggregator decide se re-queue manual ou
  marca como skip.
- **Iter bate timeout no meio do sweep** (improvável com 1 ticker): se
  per-ticker files não foram escritos atomicamente, registry fica
  inalterado → próximo iter retoma daquele ticker.
- **Registry corrompido** (JSON inválido): próximo iter trata como
  fatal, cria jornada documentando o blocker, seta memory.md
  `status: done` (loop para). Usuário investiga manualmente.

---

## 5. Per-ticker output schema

### 5.1 `<ticker>.json`

```json
{
  "ticker": "EURUSD",
  "frequency": "1hour",
  "window": {"start": "2020-01-01", "end": "2026-04-17", "n_bars": 38412},
  "costs_model": {
    "spread_half_bps": 2,
    "commission_per_side_usd": 3.5,
    "swap_daily_pct_long":  -0.005,
    "swap_daily_pct_short":  0.001,
    "citation": "pepperstone razor tier (docs/investment-mandate.md §3)"
  },
  "configs": [
    {
      "name": "donch_20_10_long",
      "metrics_is":  {"sharpe": 0.51, "cagr": 0.09, "maxdd": -0.15, "n_trades": 127, "median_hold_days": 2.3},
      "metrics_oos": {"sharpe": 0.42, "cagr": 0.08, "maxdd": -0.17, "n_trades": 54,  "median_hold_days": 2.1},
      "metrics_fwd": {"sharpe": 0.31, "cagr": 0.05, "maxdd": -0.09, "n_trades": 18,  "median_hold_days": 2.4},
      "gates": {"pbo": 0.42, "dsr_p": 0.031, "wf_win": 5, "wf_total": 8, "any_pass": false, "why_fail": "wf 5/8 < 6"},
      "benchmark_spy": {"sharpe": 0.63, "cagr": 0.11, "excess_cagr": -0.03, "beta": 0.12, "corr": 0.08}
    }
  ],
  "best_config": "donch_20_10_long",
  "any_pass_5gate": false
}
```

### 5.2 `<ticker>.md`

Standard report por §2.5 do spec Phase 3.5a (tabela `backtesting.py` +
benchmark SPY), aplicado ao **best config** deste ticker. Resto das
configs em tabela condensada embaixo:

```markdown
# EURUSD 1h — T2 Donchian breakout (iter 4)

**Window:** 2020-01-01 → 2026-04-17 (6.3y, 38 412 bars)
**Best config:** `donch_20_10_long` — **NO PASS** (wf 5/8 < 6)

## Standard report — donch_20_10_long (best)

Start                     2020-01-01 00:00:00
End                       2026-04-17 22:00:00
Duration                  2297 days 22:00:00
Exposure Time [%]         23.4
Equity Final [$]          1523.11
...
[tabela completa]
...

SPY Buy & Hold (same window):
  SPY Return [%]           76.4
  SPY CAGR [%]             10.87
  ...

Strategy vs SPY:
  Excess CAGR [%]          -2.91
  Correlation (daily)      0.08
  Beta vs SPY              0.12

## Todas configs testadas

| Config | Sharpe OOS | CAGR OOS | MaxDD OOS | PBO | DSR p | WF | PASS |
|--------|-----------|----------|-----------|-----|-------|----|------|
| donch_10_5_long  | 0.18 | 0.03 | -0.22 | 0.51 | 0.12 | 4/8 | ❌ |
| donch_10_5_short | -0.09 | -0.02 | -0.29 | 0.63 | 0.45 | 2/8 | ❌ |
| donch_20_10_long | 0.42 | 0.08 | -0.17 | 0.42 | 0.031 | 5/8 | ❌ (wf) |

## Cost sensitivity

(opcional — ablation spread/commission se aggregator quiser)
```

---

## 6. Aggregator output (`AGGREGATE.md`)

O iter aggregator produz **um arquivo consolidado** + **jornada**.

### 6.1 `AGGREGATE.md`

```markdown
# Lead T2 — Donchian/ATR breakout intraday (aggregate)

**Phase:** 3.5a | **Lead:** T2 | **Status:** DEAD END (0/12 PASS)
**Period:** 2020-01-01 → 2026-04-17 (6.3y, Tiingo FX longest window)
**Tested:** 12 tickers × 3 configs = 36 runs
**Aggregation iter:** 16 (after 12 sweep iters 4-15)

## Summary

0/12 tickers PASS all 5 gates. Best ticker by OOS Sharpe: **XAUUSD**
(donch_40_20_long, Sharpe_oos=0.58, PBO=0.38, DSR p=0.08 > 0.05 fails
deflation). Median hold 2-4 days across all winners candidates —
swap cost modelled but edge already too thin to survive.

## Cross-ticker table

| Ticker | Best config | Sharpe OOS | CAGR OOS | MaxDD | Median hold (d) | PASS |
|--------|-------------|-----------|----------|-------|-----------------|------|
| EURUSD | donch_20_10_long  | 0.42 | 8%  | -17% | 2.1 | ❌ |
| GBPUSD | donch_20_10_long  | 0.31 | 6%  | -19% | 2.3 | ❌ |
| XAUUSD | donch_40_20_long  | 0.58 | 12% | -14% | 3.8 | ❌ (DSR) |
...

## Citations

- Donchian canonical `[trading_systems_methods, p.353]`
- ATR channel `[volatility_trading]`
- Gate framework `[advances_fin_ml, ch.12+14]`

## Links

- Per-ticker reports: `reports/phase3_5a/t2_donchian_breakout_intraday/*.md`
- Registry: `reports/phase3_5a/t2_donchian_breakout_intraday/registry.json`
- Jornada: `jornada/2026-04-18-phase3.5a-T2-donchian-DEAD.md`
```

### 6.2 Jornada entry

Mesma estrutura das jornadas atuais — mas **short-form**: verdict,
tabela cross-ticker (copy do AGGREGATE.md), diagnóstico 1-2 parágrafos,
próximo lead. Tag obrigatória `[SHORT-HOLD CFD]` ou `[SWING BROKER]`.

---

## 7. Loop script changes

### 7.1 Novo env var

`SWEEP_MODE` no `scripts/self_improve_loop.sh`:
- default `off` (comportamento legacy — Lead = Iter).
- `fanout`: injeta seção "Fan-out sweep protocol" no prompt (§7.2).

### 7.2 `build_prompt()` branch

Adicionar ao final do prompt (antes de "Begin by reading memory.md"):

```bash
case "$SWEEP_MODE" in
    fanout)
        cat <<'SWEEP'

## Fan-out sweep protocol (ACTIVE — SWEEP_MODE=fanout)

You MUST follow `docs/self_improvement/fanout_protocol.md` for any
lead that sweeps multiple tickers. Summary:

1. If memory.md `active_lead_registry` is empty → BOOTSTRAP: create
   registry.json for the next pending lead, write it, update memory.md,
   EXIT (no ticker processed this iter).
2. If registry.status == "sweeping" or "pending-with-bootstrap-done":
   process EXACTLY ONE ticker (tickers_pending[0]). Write
   <ticker>.json + <ticker>.md. Pop from pending, append to done.
3. If registry.status == "aggregating": write AGGREGATE.md + jornada,
   set status to "done", clear active_lead_registry in memory.md.
4. NEVER process more than one ticker per iter in fanout mode.
5. Schema is v1 (see fanout_protocol.md §3). Atomic writes via
   tmp→rename pattern.
SWEEP
        ;;
    off|"") ;;  # legacy mode — no change
    *)
        echo "Unknown SWEEP_MODE: $SWEEP_MODE" >&2
        exit 2
        ;;
esac
```

### 7.3 Commit message helper

Ajustar `ITER_SUMMARY` parser no shell loop para, em fanout mode,
puxar a linha `- Hypothesis:` do history + concatenar com ticker:
`iter 4 — T2 swept EURUSD 1h` (já é curto o suficiente; sem mudança
real necessária se agent seguir formato).

### 7.4 Pre-flight check

Adicionar ao script (opcional):

```bash
if [[ "$SWEEP_MODE" == "fanout" && ! -f "docs/self_improvement/fanout_protocol.md" ]]; then
    echo "FATAL: SWEEP_MODE=fanout requer docs/self_improvement/fanout_protocol.md" >&2
    exit 1
fi
```

---

## 8. Tasks (implementação)

Cada task = 1+ iter (manual, não no loop self-improve). Executadas em
sessão interativa pelo Claude Code CLI antes de re-lançar o loop 3.5a.

### Task 1 — Criar `docs/self_improvement/fanout_protocol.md`

- [ ] Documento completo do protocolo (§4, §5, §6 deste spec) em
      Markdown autônomo. Linguagem direta para o agente do loop.
- [ ] Incluir schema JSON v1 completo com validação em pseudo-código.
- [ ] Exemplos concretos (ticker=EURUSD, lead=T2).
- **Conclusion:** _(preencher)_

### Task 2 — Patch `scripts/self_improve_loop.sh`

- [ ] Adicionar env var `SWEEP_MODE` (default off).
- [ ] Branch no `build_prompt()` quando `SWEEP_MODE=fanout` (§7.2).
- [ ] Pre-flight check (§7.4).
- [ ] **Zero mudança** no comportamento quando SWEEP_MODE unset/off
      (backwards-compat).
- **Conclusion:** _(preencher)_

### Task 3 — Registry schema validator (Python helper)

- [ ] `src/ai_trade/backtest/sweeps/registry.py`: `load_registry(path)`
      + `validate(registry_dict)` + `atomic_write(path, data)` +
      `append_done(ticker, summary)` + `pop_pending()`.
- [ ] Testes unitários (≥ 10 casos: valid/invalid schema, concurrent
      write safety via rename pattern, corruption detection).
- [ ] Pytest baseline não pode quebrar.
- **Conclusion:** _(preencher)_

### Task 4 — Smoke test end-to-end

- [ ] Criar lead dummy com 2 tickers × 2 configs (uso registry Python
      helper).
- [ ] Rodar `SWEEP_MODE=fanout MAX_ITER=4 bash scripts/self_improve_loop.sh`
      em branch sandbox.
- [ ] Verificar: iter 1 bootstrap → iter 2 ticker 1 → iter 3 ticker 2
      → iter 4 aggregator + memory.md limpo.
- [ ] 4 commits atômicos, cada um revisável.
- **Conclusion:** _(preencher)_

### Task 5 — Migration Phase 3.5a

- [ ] Atualizar `specs/phase_3_5a_plano_a_investigation.md` adicionando
      "§8 Modo de execução — fan-out" apontando para este spec.
- [ ] Memory.md da Phase 3.5a atual: adicionar campo
      `active_lead_registry: null` no frontmatter (próximo iter
      bootstraps T2).
- [ ] Re-lançar loop com `SWEEP_MODE=fanout MAX_ITER=60`
      (12 FX × 4 leads sweepable + aggregators = ~55 iters; +cushion).
- **Conclusion:** _(preencher)_

---

## 9. Gates e regras invioláveis

- **Backwards-compat total:** `SWEEP_MODE` unset/off ⇒ comportamento
  idêntico ao atual. Leads Phase 3, Phase 3.5b não são tocados.
- **Pytest baseline ≥ 709** permanece.
- **Atomic writes obrigatórios** em registry + per-ticker files
  (tmp → `os.rename`). Nunca escrever direto em arquivo live.
- **Append-only em `tickers_done`.** Nunca editar entry existente; se
  algo falhou, re-queue manual via novo lead_id.
- **Registry imutável em `configs`.** Nova config = novo lead_id.
- **1 ticker por iter em fanout mode.** Não batch, não paralelo.
- **Citação `[book.slug, p.X]`** continua obrigatória em decisões de
  strategy dentro de cada sub-iter (CLAUDE.md regra 2). Infra deste
  spec é isenta.
- **Commit message** de cada sub-iter deve identificar o ticker para
  inspecionabilidade no git log: `self-improve: iter N — <lead> sweep
  <ticker>`.

---

## 10. Budget & ETA

**Implementação (Tasks 1-4):** 1 sessão interativa (~2h) com Opus 4.7.

**Migration Phase 3.5a (Task 5 + re-launch):** ~60 iters × 6min =
**6h autônomas**. Comparar com tentativa atual (20 iters × 10-30min
com timeouts imprevisíveis).

**Quebra estimada do novo loop Phase 3.5a:**

| Iter | Ação |
|------|------|
| 1 | Bootstrap T2 registry |
| 2-13 | Sweep T2 nos 12 tickers (1/iter) |
| 14 | Aggregator T2 |
| 15 | Bootstrap T3 registry |
| 16-21 | Sweep T3 (6 pares cointegrados candidatos) |
| 22 | Aggregator T3 |
| 23-33 | T4 session-based (11 iters — 11 sessões × universo) |
| 34 | Aggregator T4 |
| 35-40 | T5 regime filter (6 tickers equity + crypto) |
| 41 | Aggregator T5 |
| 42-45 | T6 rebalance meta + T7 summary (leads não-sweep, modo legacy) |

Total: ~45 iters, ~4.5-6h autônomas. Margem de segurança:
`MAX_ITER=60`.

---

## 11. Out of scope (reiteração)

- Paralelização iter-a-iter.
- Cache compartilhado entre leads.
- Generalização para outras fases além de 3.5a (a decisão fica para
  spec futura, baseada em adoção real).
- Resumo de registry em memory.md (intencional: manter memory.md
  compacto; detalhe vive em `registry.json`).
- Substituição dos leads T0/T1/T6/T7 (que são atômicos, não sweeps).

---

## 12. Referências

- `specs/phase_3_5a_plano_a_investigation.md` — primeira fase consumidora.
- `scripts/tiingo_bulk_download.py` — padrão análogo (1 ticker/call +
  manifest registry).
- `scripts/self_improve_loop.sh` — loop a ser estendido.
- `docs/self_improvement/memory.template.md` — template atual,
  ganha campo `active_lead_registry`.
- `[advances_fin_ml, ch.4]` — disciplina de trial counting por família
  de configs (base pra agregação por lead, não por ticker).
