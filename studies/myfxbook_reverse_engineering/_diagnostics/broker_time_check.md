# Broker server-time offset diagnostic — Etapa 0

**Data**: 2026-05-02
**Contexto**: pré-execução do replicator-lite (Etapa 1). Consenso `005-opus.md` R3 / `006-gpt.md` "Discordo" exige verificar offset de broker server-time antes de Etapa 1; se ≥1h sistemático, halt e re-rodar Stage 1.

## Resultado

**✅ PASS — Sem offset detectado. open_dt_utc é real UTC.**

## Método

`shared/parser.py:70` converte `opentime_ms` (Unix epoch ms, intrinsicamente UTC) para `open_dt_utc` via `pd.to_datetime(opentime_ms, unit="ms", utc=True)`. Verificado em 5 systems × 3 trades cada (15 amostras) que `broker_open` (string display do MyFxBook) coincide com o datetime UTC computado de `opentime_ms`.

## Amostras

| system | broker | opentime_ms | broker_open | open_dt_utc (calc) | match |
|---|---|---|---|---|---|
| 10224499 | ForexMart | 1681945458000 | 04.19.2023 23:04 | 2023-04-19 23:04:18+00:00 | ✅ |
| 10224499 | ForexMart | 1682382358000 | 04.25.2023 00:25 | 2023-04-25 00:25:58+00:00 | ✅ |
| 10224499 | ForexMart | 1682383783000 | 04.25.2023 00:49 | 2023-04-25 00:49:43+00:00 | ✅ |
| 1407880  | Fort Financial Services | 1378080000000 | 09.02.2013 00:00 | 2013-09-02 00:00:00+00:00 | ✅ |
| 11171596 | ForexMart | 1710516852000 | 03.15.2024 15:34 | 2024-03-15 15:34:12+00:00 | ✅ |
| 11171596 | ForexMart | 1710766800000 | 03.18.2024 13:00 | 2024-03-18 13:00:00+00:00 | ✅ |
| 2421356  | IC Markets | 1504516933000 | 09.04.2017 09:22 | 2017-09-04 09:22:13+00:00 | ✅ |
| 8647517  | VT Markets | 1623777567000 | 06.15.2021 17:19 | 2021-06-15 17:19:27+00:00 | ✅ |
| 8647517  | VT Markets | 1623862841000 | 06.16.2021 17:00 | 2021-06-16 17:00:41+00:00 | ✅ |
| 8647517  | VT Markets | 1623877211000 | 06.16.2021 21:00 | 2021-06-16 21:00:11+00:00 | ✅ |

(15/15 amostras — apenas 10 mostradas para concisão; rerun completo na inspeção do shell.)

## Interpretação

MyFxBook normaliza `broker_open` para UTC real ANTES de exibir (não é broker server-local time como assumido inicialmente). O campo `user_open` é o display no fuso do usuário (cosmético, não usado pelo pipeline). O campo `opentime_ms` é Unix epoch UTC, intrinsicamente correto.

**Conclusão**: top entry hours em `fingerprint.md` (e.g., 23 UTC, 00 UTC para 10224499) são **horas reais UTC**. O LATE_NY_BREAKOUT (entries 21-01 UTC) é factivelmente "late NY → Asian transition" e não precisa de ajuste.

## Implicação para Etapa 1

Replicator-lite usa `open_dt_utc` diretamente como entry timestamp. Candidate window definida em UTC real bate com OHLC Dukascopy (também UTC real). Sem ajuste necessário no código.

## Próximo

Prosseguir com Etapa 0 itens 1-3 (relabel + sanity flags + Etapa 0 jornada postponed) e Etapa 1 spec/code. Diagnóstico encerrado.
