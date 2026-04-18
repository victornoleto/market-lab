# Phase 3.5b — SSO/ZROZ/GLD static (risk parity) DESCARTADO

**Path tag:** [SWING BROKER] | **Tipo:** rejected alternative | **Status:** ❌ REJECTED (all 4 variants)
**Data:** 2026-04-18 ~13:15

## Decisão

A estratégia **SSO/ZROZ/GLD static** (inspirada em Bridgewater All
Weather + Hedgefundie HFEA) **não merece subir para "Strategy C"** do
mandate. Dominada em Pareto pelo winner tactical 3-leg atual em todas
as 4 variantes de peso testadas. Documentação preservada como evidência
de decisão negativa — evita re-exploração futura.

## Motivação do teste

Usuário perguntou se fazia sentido uma variante estratégica de
**portfolio estático sem signals** combinando:
- SSO (S&P 500 2× LETF) — equity leverage
- ZROZ (25+ Y zero-coupon UST, duration ~28y) — regime hedge equity-off
- GLD — inflation hedge ortogonal

Com 4 perfis de agressividade:

| Variant | SSO | ZROZ | GLD |
|---|---:|---:|---:|
| SA (Super Aggressive) | 60% | 20% | 20% |
| A  (Aggressive) | 50% | 25% | 25% |
| M  (Moderate) | 40% | 30% | 30% |
| C  (Conservative) | 30% | 35% | 35% |

Lineage teórica: Bridgewater All Weather (Dalio) + Hedgefundie HFEA
(Reddit 2019). Intuição: leverage equity com hedge via duration +
inflação, rebalanceado por threshold.

## Dados

Mesma fonte do extended window test (§10 PRODUCTION.md): testfol.io
SPYSIM/ZROZSIM/GLDSIM, 1986-2026 (40 anos). SSO sintetizado via
`synthesize_letf_returns(SPYSIM.pct_change(), L=2, fee=0.01)` seguindo
`[leverage_for_the_long_run, p.16]`.

## Script & resultado

`scripts/run_static_sso_zroz_gld.py` com threshold 10pp (alinhado com
winner tactical), 15% BR IR na rebal layer.

| Variant | CAGR | Sharpe | MaxDD | Mandate ≥15%? | Gate MaxDD ≤25%? | Verdict |
|---|---:|---:|---:|:---:|:---:|:---|
| SA 60/20/20 | **16.08%** | 0.766 | **-59.4%** | ✅ | ❌ | FAIL MaxDD |
| A 50/25/25 | 14.78% | 0.795 | -49.5% | ⚠️ marginal | ❌ | FAIL MaxDD |
| M 40/30/30 | 14.00% | 0.861 | -37.8% | ❌ | ❌ | FAIL ambos |
| C 30/35/35 | 12.54% | **0.863** | -34.0% | ❌ | ❌ | FAIL ambos |
| _SPYSIM B&H_ | _11.49%_ | _0.682_ | _-55.1%_ | — | — | _benchmark_ |

**Comparação com winner tactical atual (3-leg EW threshold 10pp no
mesmo 40y window):** CAGR 26.96% / Sharpe 2.028 / MaxDD -10.12%.

## Três problemas estruturais que os dados revelaram

### 1. SA (Super Aggressive) tem MaxDD PIOR que SPY puro

-59.4% vs -55.1%. LETF 2× **sem regime filter** é fatal em 2008 — nem
ZROZ (+30%+) nem GLD (flat) conseguiram compensar o mergulho do SSO
(-65% peak-to-trough). A alavancagem sem filter dinâmico concentra
risco no pior momento possível.

### 2. Não existe sweet spot entre as 4 alocações

- **SA passa CAGR, falha MaxDD.** -59% inaceitável.
- **C passa Sharpe (relativamente), falha mandate.** 12.5% abaixo
  do CDI BR (~13-14%).
- **A e M ficam no meio** sem satisfazer nenhum dos gates plenamente.

**Pareto-frontier das 4 variantes tem 0 pontos acima da barra do
mandate §2** (CAGR ≥ 15% + MaxDD ≤ 25%). Variar os pesos **não
resolve** — é uma falha estrutural da filosofia estática, não uma
falha de calibração.

### 3. Dominada em Pareto pelo 3-leg tactical atual

| | 3-leg tactical (§10, 40y) | Melhor variant estática |
|---|---:|---:|
| CAGR | 26.96% | 16.08% (SA) |
| Sharpe | 2.03 | 0.86 (C) |
| MaxDD | -10.1% | -34.0% (C) |
| Sobrevive 2008? | ✅ | ❌ (todas) |
| Sobrevive 2022? | ✅ | ⚠️ (todas DD ~-20-30%) |

Nenhuma allocation estática vence o tactical em **nenhum** dos 3
eixos principais. Não é que alguma variante empata — são todas
dominadas Pareto-estritamente.

## Por que o resultado faz sentido teoricamente

O **edge do Plano B não vem da composição de ativos** — vem dos
signals:

1. **Filter EMA100 na perna SSO.** Em 2008 Jan, SPY cruzou abaixo
   de EMA100; sinal flip para CASH. SSO ficou em cash Jan-2008 até
   Mar-2009. Sem essa trava, SSO teria caído ~-65% peak-to-trough.
2. **Donchian breakout na perna QQQ.** Em 2000 Set, QQQ quebrou
   para baixo do 10-day low; saída do breakout. Volta só em 2003.
   Perdeu os 83% de queda da NDX 2000-2002.
3. **Donchian breakout na perna GLD.** Padrão simétrico — entrada
   em alta sustentada, saída em reversão.

Uma alocação estática **não tem como replicar isso**. ZROZ é hedge
em cenários de *deflação*, não em *stagflação* (2022 matou). GLD
hedgeia *inflação*, não *risk-off sistêmico* (2008 GLD caiu -30%
brevemente). As correlações que sustentariam a tese de risk parity
**quebram exatamente nos momentos em que você precisava delas**.

## Decisão e documentação

- **Estratégia descartada.** Não entra no mandate como Strategy C
  nem como variante futura.
- **Scripts e reports preservados** em
  `reports/phase3_5b/rejected_alternatives/static_sso_zroz_gld/` +
  `scripts/run_static_sso_zroz_gld.py` para referência histórica.
- **PRODUCTION.md §11** documenta a decisão negativa com data e
  motivos, evitando re-exploração futura ("já testamos, não serve").
- **Lição preservada:** reforço da tese de que os signals
  (EMA100 + Donchian) **são** o edge, não accessories. Quem tentar
  simplificar o Plano B removendo signals vai destruir o alpha.

## Alternativa hipotética (NÃO implementar agora)

Se quisesse reviver o conceito SSO/ZROZ/GLD com alguma chance de
passar os gates, seria necessário **adicionar um regime filter**:

- SSO: EMA100 filter (igual ao winner atual).
- ZROZ: algum filter que detecta regime de taxas subindo (ex:
  10Y UST yield > EMA200 → CASH).
- GLD: Donchian breakout (igual ao winner atual).

Mas aí **deixa de ser "static risk parity"** e vira uma variante
4-leg do winner (SSO regime + ZROZ regime + QQQ breakout + GLD
breakout). Conceitualmente não é um produto diferente — é o mesmo
winner com 1 perna extra. Se algum dia valer investigar, seria
Phase 3.5c+ own task, não parte do Plano B atual.

## Citações

- Static risk-parity lineage: Bridgewater All Weather whitepapers
  (Dalio), Hedgefundie "Excellent Adventure" (Reddit /r/LETFs 2019).
  **Nenhuma destas fontes está na bibliografia absorvida em
  `books/summaries/`** — são sources externos não-acadêmicos.
- LETF synthesis: `[leverage_for_the_long_run, p.16]`.
- Threshold rebalance: `[advances_fin_ml, p.275-278]`.
- MaxDD ≤ 25% gate: `docs/investment-mandate.md` §5.
- CAGR ≥ 15% mandate: `docs/investment-mandate.md` §2.

## Artefatos

- `reports/phase3_5b/rejected_alternatives/static_sso_zroz_gld/equity_vs_spy.png`
- `reports/phase3_5b/rejected_alternatives/static_sso_zroz_gld/drawdown_vs_spy.png`
- `reports/phase3_5b/rejected_alternatives/static_sso_zroz_gld/summary.json`
- `scripts/run_static_sso_zroz_gld.py`
- `reports/phase3_5b/PRODUCTION.md` §11 (decision record)
