# DEAD_ENDS — Abordagens descartadas com razao

Registrar aqui qualquer abordagem que foi tentada e nao deve ser reaberta sem
evidencia nova. Cada entrada precisa: titulo, sessao/data, motivo objetivo,
condicoes que reabririam.

## Pre-existentes (heranca do diagnostico 2026-05-03)

### M1 publico isolado para recuperar timing
- **Quando:** 2026-05-03 (`_diagnostics/5R1_M1_FORENSIC_REVIEW.md`)
- **Motivo:** Os 13 systems `needs_m1_review` mantiveram F1 timing < 0.03 mesmo
  no M1 publico. Granularidade sub-minuto sozinha nao recupera o gatilho do EA.
- **Reabre se:** combinarmos M1 com features adicionais (news calendar, tick
  volume, cross-asset). E o que a Fase 2A propoe — entao nao e re-abertura, e
  contexto novo.

### Multi-broker spread differential (A5)
- **Quando:** 2026-05-03 (decisao usuario)
- **Motivo:** Usuario optou por dados gratuitos apenas. Custo operacional de
  rodar 2-3 brokers MT5 demo + pareamento temporal exato e maior que beneficio
  esperado nesta fase.
- **Reabre se:** Fase 2 falhar timing recovery e usuario aprovar custo.

### Otimizar threshold apos ver resultado
- **Quando:** Sempre. Hard rule.
- **Motivo:** Inflar Sharpe in-sample, viola gates §2.4, gera PBO alto.
- **Reabre se:** Nunca. Pre-registro e contrato.

### Single-asset winner sozinho
- **Quando:** 2026-05-03 (mandate §3 reactivation gates Plano A)
- **Motivo:** Mandate exige multi-asset edge. EAs Gold-only com Sharpe alto in-
  domain nao satisfazem mesmo passando estatisticamente.
- **Reabre se:** Nunca dentro deste estudo. Multi-asset confirmation obrigatoria.

### Selecao ex-post por PnL futuro (oracle)
- **Quando:** 2026-05-03 (Tier 2 forensic)
- **Motivo:** Oracle 7/7 passa mas nao e regra executavel; usar future PnL como
  feature e leakage.
- **Reabre se:** Nunca.

### HappyForex como dataset de treino para outras estrategias
- **Quando:** Sempre.
- **Motivo:** Os 30+22 systems sao population biased (vendor selection bias) e
  nao representam mercado.
- **Reabre se:** Nunca. Trades sao apenas evidencia de comportamento do EA, nao
  ground truth de mercado.

---

## Aprendidos durante o estudo (preencher conforme avancamos)

### is_live como hard gate (rejeitado em review GPT-5.5)
- **Quando:** 2026-05-03 +1h (revisao do desenho v4 antes de rodar)
- **Motivo:** apenas 5/52 systems sao Demo; hard-gate em `is_live=Real`
  eliminaria material decodavel arbitrariamente sem ganho proporcional. Real
  exigido apenas downstream para reativacao Plano A (mandate §3).
- **Forma final:** `is_live` registrado em `pre_decode_screen.json` como
  warning-only tier, nao bloqueia decision="GO".
- **Reabre se:** Sempre. Decisao de mandate §3.

### DSR com M=1 na track record do EA (rejeitado em review GPT-5.5)
- **Quando:** 2026-05-03 +1h
- **Motivo:** DSR com M=1 e SR_0=0 reduz a PSR. Usar DSR aqui seria nominalmente
  errado e poderia confundir. PSR e o objeto certo para "track record do
  vendor" `[advances_fin_ml, p.260-263]`.
- **Forma final:** PSR no pre-screen (own track); DSR aparece na Fase 3a
  apos LightGBM mining N candidate rules (ai sim ha M tentativas).
- **Reabre se:** Nunca para o pre-screen. DSR no contexto correto sim.

### PBO substituindo WF8 (rejeitado em review GPT-5.5)
- **Quando:** 2026-05-03 +1h
- **Motivo:** PBO mede sorte na selecao entre N candidates; WF mede
  generalizacao temporal de UMA regra. Sao complementares, nao substitutos.
- **Forma final:** Mandate §2.4 hard gates incluem PBO < 0.5 E WF purgado >= 6/8.
  Sao avaliados em conjunto.
- **Reabre se:** Nunca. Conceitualmente distintos.

### Spec completo upfront para 12 semanas (rejeitado em review GPT-5.5)
- **Quando:** 2026-05-03 +1h
- **Motivo:** Specs detalhados de tasks 009-028 dependem do universo N≤10 que
  sai da Fase 1. Detalhar agora seria premature speculation.
- **Forma final:** Apenas tasks 001-008 (Fase 1) tem spec completo. STUBS.md
  enumera tasks 009-028 com goal + citacao guia. Cada sessao detalha proxima
  antes de encerrar (chain-planning).
- **Reabre se:** Apenas se o usuario explicitamente pedir spec completo.
