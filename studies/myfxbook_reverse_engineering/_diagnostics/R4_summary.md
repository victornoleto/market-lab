# R4 — Stage 1 hold-extraction NaN fix (2026-05-02)

**Status**: ✅ done. Wallclock ~30min. Sob estimativa de 50min.
**Owner**: 5R-1-hardening, agendado pelo usuário pré-Wave B + R1.

## Problema

Fingerprint reportava `hold p50/p95/max (h): nan / nan / nan` em ~30 systems.
Causa: `shared/parser.py:128` extraía `duration` por posição (`text(10)`) na
tabela HTML do MyFxBook. Layouts não-FX (crypto/CFD) **omitem a coluna `pips`**,
deslocando "duration" para a posição que normalmente carrega `pct`. Resultado:
parser lia `"0.02%"` como duração → `_parse_duration` retornava `None` →
`duration_sec` all-NaN.

Confirmado por inspeção HTML:
- 10224499 (FX): 14 visible-tds, `text(10)='2h 0m'` ✅
- 10192401 (BTCUSD): 13 visible-tds, `text(10)='0.02%'` ❌ (era pct)

## Fix

`shared/parser.py`: `duration_sec` derivada de timestamp em vez de texto.

```python
# Antes (frágil, position-based)
df["duration_sec"] = df["duration"].apply(_parse_duration)

# Depois (R4, autoritativo via timestamps que sempre vêm em symbol-td.opentime/closetime)
df["duration_sec"] = (df["closetime_ms"] - df["opentime_ms"]) / 1000.0
df["duration_sec_text"] = df["duration"].apply(_parse_duration)  # mantido só para audit
```

## Validações pré-patch

| Check | Resultado |
|---|---|
| `opentime_ms` ausente | 0 systems |
| `closetime_ms` ausente | 0 systems |
| `closetime_ms < opentime_ms` (estrito) | 0 systems |
| `closetime_ms == opentime_ms` (delta=0, scalp sub-segundo) | 20 systems, 11-82 trades cada — **válido** (broker time minute-precision; trades <1s ficam todos em mesmo ms) |
| Open trades sem closetime | 0 |

Pré-patch: 31 systems com `duration_sec` fully-NaN, 2 mixed, 19 fully-good.

## Migração

- **Backup**: `data/trades/_pre_R4_2026-05-02/<sid>.parquet` (52 arquivos, criados antes do write).
- **Manifest SHA-256 pré + pós**: `_diagnostics/R4_migration_manifest.json` (52 entries).
- **Patched (sha changed)**: 52/52 (todos mudaram, mesmo os já corretos, porque adicionamos a coluna `duration_sec_text` mirror para audit).
- **Post-migração**: `all_post_nan_zero_check = True` — zero NaN em `duration_sec` em qualquer system.
- **Não tocados**: `candidates.json`, `signal_rule.md`, `frozen_rules/` (todos preservados; features OHLC-based independem de duration).

## Fingerprints

Decisão: surgical patch (re-render só da linha `hold p50/p95/max (h):`)
em vez de re-rodar `run_decoder_stage1.py` completo. Razão: Stage 1 oficial
puxa OHLC + minera candidatos = pesado; só essa linha depende do duration_sec.

- **51 fingerprints atualizados** (1 system não tem fingerprint.md — não rodou Stage 1).
- **Pós-patch grep `nan / nan / nan`**: 0 remaining em todos os fingerprints.
- Log detalhado: `_diagnostics/R4_fingerprint_patch_log.md`.

## Verificação — sanity-check vs Opus claims do Stage 1 sample test

| system_id | Opus claim (do sample test) | Ground truth pós-R4 | Match? |
|---|---|---|---|
| 8577442 | "median hold ~192h (~8 days), swing-H4-trend" | p50=**213.99h**, p95=2052.79h, max=5209.24h | ✅ Confirma — swing 9 dias |
| 1612420 | "clock-anchored 15:30 UTC NEWS, ret_3_H4 momentum" | p50=**0.01h** (~36s), p95=0.46h, max=5.83h | ✅ Confirma — entradas/saídas instantâneas em janela news |
| 10192401 | "BTC scalping/trend-follow, BB-driven" | p50=0.06h (~3.6min), p95=4.32h | ✅ Scalping confirmado |
| 10475089 | "97.4% trades fire 00:00 Tokyo, swing not scalp" | p50=66.47h (~2.8d), p95=627.89h | ✅ Swing confirmado, NOT intraday |

Par 6R sobrevivente:

| system_id | hold p50 | hold p95 | nota |
|---|---:|---:|---|
| 1407880 | 0.98h | 3.15h | LATE_NY_BREAKOUT confirmado intraday |
| 10224499 | 1.74h | 5.03h | LATE_NY_BREAKOUT confirmado intraday |

## Implicação para R1 (re-decode integral)

R4 valida o alarme do Stage 1 sample test **empiricamente**: o que o Sonnet
classificou como "intraday OVERLAP_NY_LONDON_RANGE" em 8577442 era na verdade
swing 9-day. O bug NaN bloqueava qualquer sanity-check de família vs hold.

R1 deve usar:
- Parser corrigido (já em vigor) → fingerprints corretos.
- Enum fechado v2 (Wave B item 2 incluindo SWING_TREND_MOMENTUM, NEWS_RELEASE_MOMENTUM provisórios — sem essas, 8577442 / 1612420 ficariam UNCAT por taxonomy_gap em vez de fit).
- Pool: 30 não-rechecados (23 DECODED + 7 PARTIAL).

## Citações

- `[testing_tuning, Pardo]` — reproducibilidade (não-NaN é pré-requisito de qualquer inferência sobre family vs hold).
- `[evidence_based_ta, Aronson, p.281]` — small-sample bias (com NaN como input, Sonnet "amostrava" zero evidência sobre hold).

## Arquivos tocados

- `shared/parser.py` — patch (1 linha autoritativa + 1 mirror audit)
- `data/trades/<sid>/trades.parquet` × 52 — coluna `duration_sec` recomputada + nova `duration_sec_text` audit
- `data/trades/_pre_R4_2026-05-02/<sid>.parquet` × 52 — backup completo
- `systems/<sid>/decoder/fingerprint.md` × 51 — linha hold p50/p95/max re-renderizada
- `_diagnostics/R4_migration_manifest.json` — SHA pré+pós manifest
- `_diagnostics/R4_fingerprint_patch_log.md` — log surgical patch antes/depois

## Não tocado (intencional)

- `candidates.json`, `signal_rule.md`, `frozen_rules/`, `data/ohlc/` — independentes
- Sanity flags em `OVERNIGHT_VALIDATION_REPORT.md` — esses não usavam hold (só DD/gap); ainda assim podem ser revistos pós-R1 se R1 refletir os novos hold values nas decisões de família.

## Próximo passo

Step 2 do plano consolidado: atualizar `5R-1-hardening.md` §1 + criar `5R-1-hardening-plan.md` §4.5 com D5/D6/D7, regra UNCAT reason_code, inserção de Wave A.5 (R4 + R1) entre Wave A e Wave B-original. Reporte separado per ordem do usuário.
