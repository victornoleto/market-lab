# Phase 3.5b — V5-V8 expansão 3× testada: todas PASS, V8 ultra-aggressive, V4 mantém default

**Path tag:** [SWING BROKER] | **Tipo:** expansion | **Status:** ✅ 8/8 PASS gates
**Data:** 2026-04-18 ~15:30 (continuação direta da V4 promotion de 14:00)

## O que aconteceu

Após a promoção de V4 (SSO+QLD+UGL) como default em 14:00, user propôs testar 3× LETFs (UPRO + TQQQ) paralelamente a V2/V3/V4. Baixei dados UPROSIM + TQQQSIM via curl authenticated (mesmo token válido), adicionei 4 novas variantes V5-V8 ao pipeline, re-rodei gates (agora com n_trials=8) em ambas as janelas.

## Estrutura das 8 variantes

Extensão sistemática do espaço V1-V4 para incluir 3× na perna equity:

| V | Leg 1 | Leg 2 | Leg 3 | Nota |
|---|---|---|---|---|
| V1 | SSO 2× | QQQ 1× | GLD 1× | baseline |
| V2 | SSO 2× | QLD 2× | GLD 1× | +2× NDX |
| V3 | SSO 2× | QQQ 1× | UGL 2× | +2× gold |
| **V4** ⭐ | SSO 2× | QLD 2× | UGL 2× | **default 2026-04-18** |
| V5 | UPRO 3× | QQQ 1× | GLD 1× | 3× SSO only |
| V6 | UPRO 3× | TQQQ 3× | GLD 1× | 3× equity |
| V7 | UPRO 3× | QQQ 1× | UGL 2× | 3× SSO + 2× gold |
| V8 | UPRO 3× | TQQQ 3× | UGL 2× | max leverage |

Nota estrutural: **não existe ETF 3× gold** no mercado US (DGP foi 2× e descontinuado). V7/V8 ficam com UGL 2× por essa razão.

## Resultado (canonical 2004-2026, ordered by OOS Sharpe)

| Rank | Variant | OOS Sh | CAGR | MaxDD | Boot 99.9% lo | 5 gates |
|---:|---|---:|---:|---:|---:|:-:|
| 1 | V8 | **2.622** | **58.17%** | -17.14% | 1.309 | ✅ PASS |
| 2 | **V4** ⭐ | 2.609 | 39.19% | -12.22% | 1.274 | ✅ PASS |
| 3 | V2 | 2.595 | 35.03% | -12.62% | 1.304 | ✅ PASS |
| 4 | V6 | 2.573 | 53.02% | -17.05% | 1.325 | ✅ PASS |
| 5 | V1 | 2.478 | 26.53% | -9.39% | 1.043 | ✅ PASS |
| 6 | V7 | 2.428 | 38.98% | -12.38% | 1.176 | ✅ PASS |
| 7 | V3 | 2.392 | 30.89% | -10.88% | 1.081 | ✅ PASS |
| 8 | V5 | 2.354 | 34.46% | -14.06% | 1.024 | ✅ PASS |

**Extended 1986-2026:** ranking top-4 idêntico (V8 > V4 > V2 > V6). Todas 8 PASS. Máximo MaxDD extended: V8 com 22.84% (a 2.16pp do gate 25%).

## Achados brutos testfol.io (standalone CAGRs)

Dados raw revelam dois LETFs com alpha **negativo** isolado:

| Asset | 1× CAGR 40y | 2× CAGR 40y | 3× CAGR 40y | Multiplier efetivo (2× vs 1×) | (3× vs 1×) |
|---|---:|---:|---:|---:|---:|
| SPY → SSO → UPRO | 11.49% | 14.58% | 13.51% | 1.27× | 1.18× |
| QQQ → QLD → TQQQ | 14.58% | 17.27% | **12.16%** | 1.19× | **0.84×** |
| GLD → UGL → — | 6.92% | **6.34%** | N/A | **0.92×** | — |

- **TQQQ 3×** (buy-hold 40y) tem CAGR **< QQQ 1×**. Vol drag NDX em 3× daily rebal mata a alavancagem em período suficientemente longo.
- **UGL 2×** (buy-hold 40y) tem CAGR **< GLD 1×**. Gold tem regiões flat longas (2012-2018, 2020-2023) onde decay domina.
- **UPRO 3×** standalone é quase flat vs SSO 2× em CAGR (13.51% vs 14.58%) — 3× não compensa drag extra.

## ★ Por que V4 mantém default, não V8

V8 tem **OOS Sharpe +0.013** vs V4 (dentro do ruído bootstrap) e **CAGR +18.98pp**. Tentação é alta. Mas 3 razões operacionais concretas:

### 1. Margem ao gate MaxDD 25% `[mandate §5]`

| | V4 canonical | V4 extended | V8 canonical | V8 extended |
|---|---:|---:|---:|---:|
| MaxDD | -12.22% | -16.91% | -17.14% | **-22.84%** |
| Margem ao gate 25% | 12.78pp | 8.09pp | 7.86pp | **2.16pp** |

V8 extended está a 2.16pp do gate. Stress event tipo 1973-74 Volcker (fora da amostra) poderia levar V8 real a violar o gate. V4 tem margem ordens de magnitude maior.

### 2. Gayed drag real LETF

`[leverage_for_the_long_run, p.21, Table 12]` reportou UPRO real drag ~2%/yr vs teórico. Em V8 com 3× SSO + 3× QQQ + 2× gold empilhados, espera-se ~4-5pp CAGR reduzido + 3-5pp MaxDD aumentado em produção. V8 real MaxDD esperado ~27-30% → **provavelmente viola gate**.

### 3. Sharpe edge dentro do ruído

std(Sharpe) com T ≈ 5383 bars ≈ 0.014. V8-V4 Δ = 0.013 está no nível de ruído amostral. Não é diferença estatisticamente distinguível `[fortune_formula]`, `[leverage_space]` (half-Kelly argument).

## Decisão

- **V4 permanece default** (promovido em 14:00, confirmado agora após expansão 3×).
- **V8 documentado como ultra-aggressive alternative** — gate-passing em backtest, mas tight ao gate 25% em extended + frágil a drag real.
- **V1 permanece conservative fallback** (§13).
- V2/V3/V5/V6/V7 documentados como passing-mas-dominados — referência, não recommend.

## Interaction effect — observação preservada

Mesma lição de V1-V4 agora estendida: **LETFs com alpha negativo standalone** (UGL, TQQQ) viram positive em **blend EW com outros LETFs**, via interaction effect. O pricing correlacional domina os means isolados.

Lição para design futuro: pensar sempre em **pairs/triplets** de LETFs, não adições marginais. V5 (só UPRO 3×, resto 1×) tem Sharpe **menor** que V1 (baseline 2×/1×/1×) — adicionar leverage sozinho piora. V8 (todos alavancados) tem Sharpe **maior** que V1. Não-aditividade do Sharpe é o princípio chave.

## Mudanças nos docs

- `reports/phase3_5b/variants_letf_execution/README.md` — reescrito com 8 variantes, triplo ranking (V1-V8 canonical + extended), nova seção "Deploy recommendation por perfil de risco", interaction effect expandido.
- `reports/phase3_5b/variants_letf_execution/gates_verdict.md` — regenerado com 8 rows por janela, título atualizado.
- `reports/phase3_5b/PRODUCTION.md` §12 reescrito (V1-V8 em vez de V1-V4), §13 preservado (V1 fallback).
- `reports/phase3_5b/README.md` TL;DR bullet atualizado ("8 variants" + V8 ultra-aggressive doc).
- `data/testfolio/cache/history.parquet` — 9 tickers (adicionou UPROSIM + TQQQSIM).

## Artefatos

- `reports/phase3_5b/variants_letf_execution/` — completa com 8 rows no MD + 8 curvas no chart
- `scripts/run_plano_b_variants_letf_execution.py` — estendido V5-V8
- `scripts/run_plano_b_variants_gates.py` — estendido V5-V8, n_trials=8
- `data/testfolio/upro-tqqq.json` — raw download 3× data
- `data/testfolio/cache/history.parquet` — 9 tickers unificados

## Pytest

771 preservado (zero regressão).

## Citações

- 5-gate framework: `[advances_fin_ml, p.208-211, p.273-275, p.196-202]`.
- LETF drag theoretical vs real: `[leverage_for_the_long_run, p.16, p.21, Table 12]`.
- Half-Kelly parameter uncertainty: `[fortune_formula]`, `[leverage_space]`.
- Risk-of-ruin as abandonment: `[leverage_for_the_long_run, p.19-20]`.
- HRP correlation-structure: `[advances_fin_ml, p.298-313, ch.16]`.
- Mandate MaxDD 25%: `docs/investment-mandate.md` §5.

## Próximos passos

- ✅ Todos os docs atualizados.
- Override §7 mandate (pending user ratification) — registro V1 → V4 promotion + V8 ultra-aggressive documented.
- Phase 4 paper trading: deploy V1 inicial (6-12m), migrar V4 após track record, V8 apenas após ≥12-24m V4 live confirmado.
