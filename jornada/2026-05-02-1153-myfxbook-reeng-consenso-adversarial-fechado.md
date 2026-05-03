# MyFxBook reverse-engineering — consenso adversarial fechado, Etapa 0 + skeleton prontos

7 turnos de chat adversarial entre Opus e GPT (`studies/myfxbook_reverse_engineering/adversarial_chat/001..007`) chegaram a consenso operacional sobre o que vem depois da rodada overnight de 52 systems HappyForex.

## Resultado do chat

O kill-shot aceito: o pipeline atual mede **decodabilidade** (prever Buy/Sell *dado que* o system entrou em `t`), não **replicabilidade** (prever *se* o system entraria em `t`) nem **edge econômico** (sobreviver a custos). Por isso o `OVERNIGHT_VALIDATION_REPORT` foi renomeado de `HIGH/MEDIUM/LOW` para `DECODED/PARTIAL_DECODED/NOT_DECODED`, com disclaimer literal no topo. Nenhum system é candidato a paper trading enquanto não houver Etapa 1 + Etapa 2 passando.

## Plano de execução (consenso)

- **Etapa 0** ✅ relabel + sanity flags informativos (DD<30%, p95_hold<168h, max_gap<30d) + offset diagnóstico de broker server-time (sem bug detectado).
- **Etapa 1** — replicator-lite case-control em M5 sobre top-10 DECODED. Candidate window = pares × top-3 hours frozen, baselines triviais (always-buy / hour-majority / pair-hour-majority), thresholds Pass/Borderline/Fail por lift ≥+10pp e predicted/actual ≤ 3.0.
- **Etapa 2** — frozen-rule cross-system: par primário `1407880 → 10224499` (LATE_NY_BREAKOUT, decisivo), par diagnóstico `2373850 → 11171596` (informativo).
- **Etapa 3** — decisão binária Stage 3 sim/não.

## Defer absoluto

Stage 3 proper, Opus re-review, RuleFit/SPA, features novas (DXY/news), agregação Happy Gold cohort. Qualquer um requer novo round adversarial.

## Sanity flags revelaram tensão real

Apenas 4 dos top-10 DECODED passam todos os 3 sanity gates. `10224499` (top-1 LATE_NY_BREAKOUT, centerpiece da Etapa 2) tem DD=52.89%; `11171596` (top-2 NY_SESSION_REVERSAL) tem p95_hold=561h (23 dias) — incompatível com a família "intraday reversal" classificada pelo Sonnet. Isso não muda o consenso (flag é informativo, não exclui), mas indica que vários systems podem falhar Etapa 1 por razão estrutural (não são intraday) ao invés de por falta de edge.

## Entregáveis desta sessão

- `studies/myfxbook_reverse_engineering/adversarial_chat/001..007-*.md` — chat completo (7 turnos)
- `studies/myfxbook_reverse_engineering/specs/replicator_lite_pre_reg.md` — spec pré-registrada
- `studies/myfxbook_reverse_engineering/frozen_rules/` — 12 regras congeladas read-only
- `studies/myfxbook_reverse_engineering/_diagnostics/broker_time_check.md` — offset diagnóstico
- `studies/myfxbook_reverse_engineering/_diagnostics/sanity_flags.json` — flags por system
- `studies/myfxbook_reverse_engineering/ranking/OVERNIGHT_VALIDATION_REPORT.md` — atualizado com novos rótulos
- `studies/myfxbook_reverse_engineering/shared/replicator_lite.py` — skeleton funcional (rule loading + candidate window + labels validados em smoke test em `10224499`: 221/221 trades corretamente alinhados)

## O que vem a seguir

Próxima sessão: implementar batch driver de Etapa 1 (`run_batch`), rodar feature extraction nos top-10, gerar `replicator_lite_results.csv` + memo. Etapa 2 frozen-rule depois. Etapa 3 decisão.

Compatibilidade com mandate: 100% Plano C continua, MyFxBook estudo é research-only sem capital allocation. Reactivação de Plano A (DORMANT desde 2026-04-23) requer Etapa 1+2 Pass + Stage 3 proper + sign-off explícito.

## Glossário (termos novos para `jornada/README.md`)

- **Decodabilidade**: capacidade de prever direção (Buy/Sell) condicional ao timestamp real de entrada. Métrica do score atual.
- **Replicabilidade**: capacidade de prever ENTRADAS (timing + direção) sem condicionar a timestamps reais. Métrica da Etapa 1.
- **Edge econômico**: estratégia replicada sobrevive a custos, slippage, swap e gates §2.4. Métrica de Stage 3 proper.
- **Frozen rule**: cópia read-only do `signal_rule.md` Stage 2 em `frozen_rules/<id>.md`. Replicator-lite só lê dela; re-mining proibido.
- **Sanity flag (tradeable)**: DD<30 / p95_hold<168h / max_gap<30d. Informativo, não exclui Etapa 1; bloqueia Stage 3 / paper.
