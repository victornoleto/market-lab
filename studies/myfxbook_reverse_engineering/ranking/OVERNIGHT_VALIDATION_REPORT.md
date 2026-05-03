# Overnight validation report — myfxbook reverse-engineering

Last update: 2026-05-02T15:00:00+00:00
Systems processed: 52  |  DECODED: 23  |  PARTIAL_DECODED: 7  |  NOT_DECODED: 22  |  FAIL: 0

> **⚠ Disclaimer obrigatório (consenso adversarial 2026-05-02):**
> Este score mede **decodabilidade** condicional ao timestamp de entrada real.
> **Replicabilidade** (predição de entry timing fora dos eventos reais) e **edge econômico** (sobrevivência a custos e gates §2.4) **não foram testados** neste relatório.
> Nenhum system aqui é candidato a paper trading. Próximas etapas em `specs/replicator_lite_pre_reg.md`.

### Renomeação de rótulos (consenso adversarial)

| Antigo | Novo | Significado |
|---|---|---|
| HIGH | **DECODED** | direção previsível condicional ao timestamp real (não implica edge) |
| MEDIUM | **PARTIAL_DECODED** | sinal direcional parcial; family_clarity baixa ou direction_predictability moderado |
| LOW | **NOT_DECODED** | sem regra recuperável OU martingale auto-flag |
| FAIL | FAIL | erro de pipeline (parsing, missing OHLC) |

### Coluna `tradeable_sanity_flag` (informativo, não exclui)

Aplicação dos sanity gates pré-score (DD<30%, p95_hold<168h, max_gap<30d). Falha em qualquer gate = system underwater / multi-week swing / inconsistência operacional.
Per `007-opus.md` micro-ajuste: flag NÃO altera o rótulo de decodabilidade. Replicator-lite (Etapa 1) e frozen-rule cross-system (Etapa 2) rodam em todos os top-10 DECODED independente do flag.
Flag bloqueia **somente** Stage 3 proper / paper trading downstream.

## 🟢 DECODED — direção decodável condicional (23)

Status: candidatos para Etapa 1 replicator-lite. Sanity flag informativo; não exclui.

| system_id | name | reliability | family | confidence | n_trades | account | dir_pred | timing_conc | age_fresh | sanity_flag |
|---|---|---|---|---|---|---|---|---|---|---|
| 10224499 | Happy Market Hours FM - REAL Forex Trading System by Forex T | 0.871 | LATE_NY_BREAKOUT | 0.68 | 221 | Real | 0.842 | 1.000 | 0.998 | DD=52.9% gap=41d |
| 11171596 | Happy Algorithm PRO FM - REAL (SET1) Forex Trading System by | 0.850 | NY_SESSION_REVERSAL | 0.62 | 1083 | Real | 1.000 | 0.645 | 0.973 | p95=561h gap=34d |
| 11155858 | Happy Brexit FM (HR) Forex Trading System by Forex Trader Ha | 0.801 | FACTOR_SCALPING | 0.38 | 197 | Real | 1.000 | 0.802 | 0.995 | DD=37.0% p95=973h gap=32d |
| 8647517 | Happy Gold - VTMarkets (M30) Forex Trading System by Forex T | 0.797 | FACTOR_SCALPING | 0.62 | 1024 | Real | 1.000 | 0.365 | 0.999 | ✓ |
| 2421356 | Happy Gold - ICMarkets (M30) Forex Trading System by Forex T | 0.784 | FACTOR_SCALPING | 0.72 | 1763 | Demo | 1.000 | 0.352 | 0.999 | gap=64d |
| 10281851 | Happy Gold - Eightcap (M30)  Forex Trading System by Forex T | 0.782 | OVERLAP_NY_LONDON_RANGE | 0.62 | 652 | Real | 1.000 | 0.367 | 0.999 | ✓ |
| 9912554 | Happy Brexit FM - REAL Forex Trading System by Forex Trader  | 0.779 | OVERLAP_NY_LONDON_RANGE | 0.57 | 103 | Real | 0.718 | 0.854 | 0.999 | DD=34.9% p95=4931h gap=189d |
| 11207608 | Happy Gold - BBM Forex Trading System by Forex Trader HappyF | 0.778 | FACTOR_SCALPING | 0.72 | 202 | Real | 1.000 | 0.371 | 0.849 | DD=32.9% |
| 11628637 | Happy Bitcoin - VM Forex Trading System by Forex Trader Happ | 0.776 | FACTOR_SCALPING | 0.62 | 232 | Real | 1.000 | 0.384 | 1.000 | ✓ |
| 9375654 | Happy Gold - TMGM (M30) Forex Trading System by Forex Trader | 0.774 | NY_SESSION_REVERSAL | 0.58 | 915 | Real | 1.000 | 0.366 | 0.999 | ✓ |
| 6541963 | Happy Gold - Tickmill (M15) Forex Trading System by Forex Tr | 0.760 | FACTOR_SCALPING | 0.62 | 2213 | Demo | 1.000 | 0.329 | 0.999 | DD=54.8% gap=64d |
| 10563761 | Happy Bitcoin - DecodeFX Forex Trading System by Forex Trade | 0.757 | FACTOR_SCALPING | 0.55 | 436 | Real | 1.000 | 0.385 | 0.949 | ✓ |
| 11355455 | Happy Gold - DooPrime Forex Trading System by Forex Trader H | 0.744 | FACTOR_SCALPING | 0.52 | 236 | Real | 1.000 | 0.326 | 0.999 | ✓ |
| 11206045 | Happy Japanese Market FM Forex Trading System by Forex Trade | 0.737 | LATE_NY_BREAKOUT | 0.50 | 212 | Real | 0.453 | 0.995 | 1.000 | p95=396h |
| 10734338 | Happy Bitcoin - ICMarkets Forex Trading System by Forex Trad | 0.734 | FACTOR_SCALPING | 0.52 | 591 | Demo | 1.000 | 0.374 | 1.000 | DD=37.1% |
| 10062918 | Happy Forex FM - REAL (Set 3) Forex Trading System by Forex  | 0.730 | UNCATEGORIZED | 0.52 | 731 | Real | 1.000 | 0.252 | 0.910 | DD=51.8% p95=960h |
| 1407880 | OLD Happy Market Hours v2.3.1 Forex Trading System by Forex  | 0.730 | LATE_NY_BREAKOUT | 0.72 | 3304 | Demo | 0.653 | 1.000 | 0.024 | gap=34d |
| 2373850 | OLD Happy Algorithm PRO v1.4 - REAL (SET1) Forex Trading Sys | 0.725 | UNCATEGORIZED | 0.44 | 1691 | Real | 1.000 | 0.678 | 0.016 | DD=39.5% p95=508h gap=222d |
| 10192401 | Happy Bitcoin - TMGM Forex Trading System by Forex Trader Ha | 0.712 | FACTOR_SCALPING | 0.52 | 420 | Real | 1.000 | 0.338 | 0.650 | DD=37.0% |
| 10475089 | Happy Japanese Market FM Forex Trading System by Forex Trade | 0.703 | UNCATEGORIZED | 0.38 | 117 | Real | 0.598 | 0.991 | 0.642 | DD=40.6% p95=628h |
| 1603276 | Happy Breakout v1.0 - (Closed AU account) Forex Trading Syst | 0.676 | LONDON_OPEN_MOMENTUM | 0.62 | 594 | Real | 1.000 | 0.333 | 0.000 | ✓ |
| 10249298 | Happy Trend FM - REAL Forex Trading System by Forex Trader H | 0.674 | UNCATEGORIZED | 0.38 | 280 | Real | 0.543 | 0.689 | 0.999 | p95=1461h gap=48d |
| 1152318 | OLD Happy Forex v2.4.1 - REAL (FortFS- set 3) Forex Trading  | 0.669 | UNCATEGORIZED | 0.62 | 1637 | Real | 0.976 | 0.246 | 0.016 | p95=872h gap=30d |

## 🟡 PARTIAL_DECODED — sinal direcional parcial (7)

Status: não vai para Etapa 1 (escopo top-10 DECODED). Pode ser revisitado se Etapa 1+2 passarem.

| system_id | name | reliability | family | confidence | n_trades | account | dir_pred | timing_conc | age_fresh | sanity_flag |
|---|---|---|---|---|---|---|---|---|---|---|
| 9843883 | Happy Algorithm PRO FM - REAL (SET2)  Forex Trading System b | 0.637 | UNCATEGORIZED | 0.32 | 2576 | Real | 0.355 | 0.674 | 0.998 | DD=52.4% p95=1014h gap=36d |
| 1612420 | OLD Happy News v1.4.1 Forex Trading System by Forex Trader H | 0.630 | OVERLAP_NY_LONDON_RANGE | 0.52 | 788 | Demo | 0.680 | 0.746 | 0.021 | DD=39.3% gap=35d |
| 8577442 | Happy Way FM - REAL Forex Trading System by Forex Trader Hap | 0.618 | OVERLAP_NY_LONDON_RANGE | 0.52 | 934 | Real | 0.476 | 0.303 | 0.997 | p95=2053h gap=41d |
| 10251631 | Happy Gold FM - REAL (GN) Forex Trading System by Forex Trad | 0.585 | FACTOR_SCALPING | 0.38 | 461 | Real | 0.447 | 0.536 | 0.653 | DD=33.7% |
| 10067081 | Happy Frequency FM - REAL Forex Trading System by Forex Trad | 0.551 | UNCATEGORIZED | 0.43 | 4000 | Real | 0.258 | 0.254 | 0.999 | DD=80.9% p95=214h gap=97d |
| 9830783 | Happy Galaxy FM - REAL Forex Trading System by Forex Trader  | 0.547 | OVERLAP_NY_LONDON_RANGE | 0.42 | 4000 | Real | 0.241 | 0.262 | 0.999 | DD=70.9% p95=676h |
| 9841939 | Happy Power FM Forex Trading System by Forex Trader HappyFor | 0.490 | FACTOR_SCALPING | 0.38 | 4000 | Real | 0.045 | 0.266 | 0.999 | DD=35.6% p95=726h |

## 🔴 NOT_DECODED — sem regra recuperável OU martingale (22)

| system_id | name | reliability | family | confidence | n_trades | account | sanity_flag |
|---|---|---|---|---|---|---|---|
| 8397136 | OLD Happy Algorithm PRO v1.4 - REAL (SET2) Forex Trading Sys | 0.533 | UNCATEGORIZED | 0.38 | 432 | Real | p95=753h |
| 8574205 | Happy MartiGrid (Multipairs) FM - REAL Forex Trading System  | 0.499 | UNCATEGORIZED | 0.28 | 3994 | Real | p95=1527h gap=64d |
| 2123808 | OLD Happy Way v1.2 - REAL Forex Trading System by Forex Trad | 0.452 | UNCATEGORIZED | 0.38 | 856 | Real | DD=32.3% p95=1914h |
| 8286716 | OLD Happy Power v1.0 (High Risk) Forex Trading System by For | 0.421 | UNCATEGORIZED | 0.35 | 1531 | Real | DD=54.4% p95=283h |
| 5542332 | OLD Happy Frequency v1.1 - REAL Forex Trading System by Fore | 0.408 | UNCATEGORIZED | 0.35 | 3995 | Real | DD=76.8% p95=351h gap=116d |
| 3568877 | OLD Happy Frequency v1.1 - REAL (9 pairs) Forex Trading Syst | 0.404 | UNCATEGORIZED | 0.28 | 3998 | Real | DD=74.0% p95=304h |
| 2483126 | OLD Happy MartiGrid v1.9.1 (Multipairs)- REAL Forex Trading  | 0.399 | UNCATEGORIZED | 0.22 | 1910 | Real | DD=63.0% p95=1823h |
| 10585558 | Happy News - 8EC Forex Trading System by Forex Trader HappyF | 0.300 | MARTINGALE_GRID | 0.88 | 1611 | Real | ✓ |
| 10716398 | Happy Frequency FM - REAL Forex Trading System by Forex Trad | 0.300 | MARTINGALE_GRID | 0.95 | 4000 | Real | p95=312h gap=308d |
| 10746260 | Happy News - UM Forex Trading System by Forex Trader HappyFo | 0.300 | MARTINGALE_GRID | 0.97 | 636 | Real | ✓ |
| 10814265 | Happy Breakout AdroFX Forex Trading System by Forex Trader H | 0.300 | MARTINGALE_GRID | 0.82 | 957 | Real | DD=34.7% |
| 10970107 | Happy News - DecodeFx Forex Trading System by Forex Trader H | 0.300 | MARTINGALE_GRID | 0.95 | 835 | Real | ✓ |
| 11504701 | Happy News - DPrime Forex Trading System by Forex Trader Hap | 0.300 | MARTINGALE_GRID | 0.92 | 314 | Real | ✓ |
| 612872 | OLD Happy MartiGrid v1.9.1 - REAL Forex Trading System by Fo | 0.300 | MARTINGALE_GRID | 0.95 | 3136 | Real | p95=219h gap=40d |
| 6603448 | OLD Happy Fast Money v1.3.1 - REAL (Hedge) Forex Trading Sys | 0.300 | MARTINGALE_GRID | 0.72 | 920 | Real | DD=32.4% p95=2035h gap=44d |
| 7603723 | OLD Happy Neuron v1.0 (Aggressive Risk) Forex Trading System | 0.300 | FACTOR_SCALPING | 0.52 | 3558 | Real | DD=72.7% p95=274h |
| 7942220 | OLD Happy Neuron v1.0 (Conservative  Risk) Forex Trading Sys | 0.300 | MARTINGALE_GRID | 0.82 | 3910 | Real | DD=45.9% p95=330h |
| 8577996 | Happy Fast Money FM - REAL (Hedge) Forex Trading System by F | 0.300 | MARTINGALE_GRID | 0.82 | 4000 | Real | DD=48.1% p95=1809h gap=30d |
| 8599269 | Happy MartiGrid FM - REAL Forex Trading System by Forex Trad | 0.300 | UNCATEGORIZED | 0.28 | 1123 | Real | p95=567h gap=42d |
| 8599392 | Happy Frequency Orbex - REAL  Forex Trading System by Forex  | 0.300 | FACTOR_SCALPING | 0.38 | 4000 | Real | DD=64.2% p95=680h |
| 9607500 | Happy Breakout VTMarkets Forex Trading System by Forex Trade | 0.300 | OVERLAP_NY_LONDON_RANGE | 0.48 | 1942 | Real | DD=36.4% |
| 10878805 |  | 0.000 | UNKNOWN | ? | 0 | None | ✓ |

## ⚠️ FAIL — pipeline error (0)


## Top families across all PASS systems

- `UNCATEGORIZED`: 15 systems
- `FACTOR_SCALPING`: 14 systems
- `MARTINGALE_GRID`: 10 systems
- `OVERLAP_NY_LONDON_RANGE`: 6 systems
- `LATE_NY_BREAKOUT`: 3 systems
- `NY_SESSION_REVERSAL`: 2 systems
- `UNKNOWN`: 1 systems
- `LONDON_OPEN_MOMENTUM`: 1 systems

## Próximas etapas (consenso adversarial)

1. **Etapa 0** ✅ — relabel + disclaimer + sanity flags (este arquivo).
2. **Etapa 1** — replicator-lite case-control nos top-10 DECODED. Spec: `specs/replicator_lite_pre_reg.md`.
3. **Etapa 2** — frozen-rule cross-system: `1407880 → 10224499` (primário) + `2373850 → 11171596` (diagnóstico).
4. **Etapa 3** — decisão binária Stage 3 sim/não + única `jornada/` entry.

Defer absoluto: Stage 3 proper, Opus re-review, RuleFit/SPA/features novas, agregação Happy Gold cohort.