# Opus re-decode targets (Phase 5R-0)

Lista pré-registrada dos **15 systems** que recebem re-decode com Opus 4.7 antes do batch 5R-1+.
Decisão consensuada com usuário 2026-05-02 (opção C: Opus seletivo, ~$5-6 estimado vs $15-25 nos 52).

## Critério de inclusão

**Pool A — 12 systems com frozen_rule existente (caminho crítico ranking)**

Já no `frozen_rules/` da Etapa 1; são os candidatos naturais ao topo do ranking 5R-4.
Re-decodificar cobre o risco de Sonnet ter errado família/regra Stage 2 — bug que se propagaria
em todos os termos da score formula.

**Pool B — 3 systems extras com inconsistência forte ou alto valor de informação**

DECODED com (a) inconsistência grave entre `family` classificada e hold distribution (sanity flag
contradiz a hipótese de família intraday), OU (b) `UNCATEGORIZED` com `reliability` alta (Sonnet
não classificou; Opus pode), OU (c) OLD/Gold sample largo que potencialmente entra em pares 6R futuros.

## Lista finalizada (15)

### Pool A — frozen_rules existentes (12)

| # | system_id | family Sonnet | reliability | n | sanity | nota |
|---:|---|---|---:|---:|---|---|
| 1 | 10224499 | LATE_NY_BREAKOUT | 0.871 | 221 | DD=52.9% gap=41d | top-1 DECODED, centerpiece 6R par primário |
| 2 | 11171596 | NY_SESSION_REVERSAL | 0.850 | 1083 | p95=561h gap=34d | ⚠ p95=23d incompatível com "intraday reversal" |
| 3 | 11155858 | FACTOR_SCALPING | 0.801 | 197 | DD=37% p95=973h | ⚠ p95=40d incompatível com "scalping" |
| 4 | 8647517 | FACTOR_SCALPING | 0.797 | 1024 | ✓ | Gold cohort, sanity OK |
| 5 | 2421356 | FACTOR_SCALPING | 0.784 | 1763 | gap=64d | Gold cohort, demo |
| 6 | 10281851 | OVERLAP_NY_LONDON_RANGE | 0.782 | 652 | ✓ | Gold cohort, sanity OK |
| 7 | 9912554 | OVERLAP_NY_LONDON_RANGE | 0.779 | 103 | DD=34.9% p95=4931h gap=189d | ⚠ p95=205d totalmente incompatível com "intraday range" |
| 8 | 11207608 | FACTOR_SCALPING | 0.778 | 202 | DD=32.9% | Gold cohort |
| 9 | 11628637 | FACTOR_SCALPING | 0.776 | 232 | ✓ | Bitcoin cohort |
| 10 | 9375654 | NY_SESSION_REVERSAL | 0.774 | 915 | ✓ | Gold cohort |
| 11 | 1407880 | LATE_NY_BREAKOUT | 0.730 | 3304 | gap=34d | OLD, par primário 6R (OLD→NEW = 1407880→10224499) |
| 12 | 2373850 | UNCATEGORIZED | 0.725 | 1691 | DD=39.5% p95=508h gap=222d | OLD, par diagnóstico 6R (OLD→NEW = 2373850→11171596) |

### Pool B — extras (3)

| # | system_id | family Sonnet | reliability | n | sanity | razão |
|---:|---|---|---:|---:|---|---|
| 13 | 11206045 | LATE_NY_BREAKOUT | 0.737 | 212 | p95=396h | ⚠ família intraday + p95=16d. Se Opus reclassificar, salva o 6R par primário (mesma família) de uma classificação ambígua |
| 14 | 6541963 | FACTOR_SCALPING | 0.760 | 2213 | DD=54.8% gap=64d | Gold cohort com **maior n** (2213 trades) — sample mais rico para validar regra de scalping |
| 15 | 10062918 | UNCATEGORIZED | 0.730 | 731 | DD=51.8% p95=960h | UNCAT com reliability=0.730 (alto). Sonnet falhou em classificar; Opus tem chance |

## Não-inclusos com justificativa

Os outros 11 DECODED ficam com regra Sonnet:
- 6 são Gold/Bitcoin FACTOR_SCALPING com sanity OK e reliability 0.71-0.76 (regra Sonnet provável OK).
- 3 são LONDON_OPEN_MOMENTUM / LATE_NY_BREAKOUT com sanity OK, baixo n; risco de Sonnet errar baixo.
- 2 são OLD UNCATEGORIZED de baixo reliability — improvável virar top de ranking mesmo com Opus.

7 PARTIAL_DECODED: ficam com Sonnet. Se algum surpreender no 5R-3 (`score ≥ 0.60`), fazer Opus re-decode targeted depois. Não justifica gastar Opus a priori.

22 NOT_DECODED: ficam com Sonnet (zero ou regra trivial). Sem ROI para Opus nessa pool — eles vão `score < 0.40` por construção (regras são triviais ou ausentes).

## Output esperado (5R-0d)

15 × `systems/<id>/decoder/signal_rule.md` atualizados (timestamp Opus 4.7).
Copiar para `frozen_rules/<id>.md` substituindo as 12 existentes + adicionando 3 novos.

`frozen_rules/CHANGELOG.md` documenta o re-decode (data, modelo, motivo).

## Custo estimado

15 systems × ~$0.30-0.50 por decode (Opus 4.7 com fingerprint+candidates context) = **$5-8**.

## Compliance mandate

- Plano A DORMANT continua. Re-decode é research-only.
- Citações Stage 2 mantêm `[advances_fin_ml ch.5]`, `[evidence_based_ta]`, `[chan_quant_trading]`,
  `[carver_st_systematic]` conforme protocolo decoder agent.
