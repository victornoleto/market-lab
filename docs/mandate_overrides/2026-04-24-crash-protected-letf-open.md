# Mandate override proposal — Reativação de Strategy B via crash-protected LETF

**Data:** 2026-04-24
**Proposto por:** Claude Code (sob pedido do usuário em 2026-04-24 após
revisão profunda do estudo `ema_sma_threshold_crash_protected`).
**Status:** 🟡 **DRAFT — aguardando assinatura**.

Para aprovar: edite esta seção para
`✅ **Signed YYYY-MM-DD HH:MM**` com sua confirmação textual. Até que
isso aconteça, Claude NÃO executará nenhum código de live trading para
este slot.

**Afeta (se assinado):** `docs/investment-mandate.md` §1, §4, §5, §7;
`CLAUDE.md` + `.claude/CLAUDE.md` sumário.
**Reversível:** Não após assinatura. Este arquivo permanece imutável
como registro histórico.

---

## Por que este override

O mandate atual (§1, assinado em 2026-04-23 via override
`2026-04-23-consolidate-plano-c-final.md`) estabelece:

* **100% Plano C passive factor-tilted** (`portfolio-aposentadoria.md`)
* **Strategy A/B/D = 0% DORMANT** com infra preservada
* **Revisão programada 6-12 meses** sem hunt ativo planejado

Este override busca **reativar parcialmente Strategy B** sob uma
configuração específica (LETF Gayed com overlays de stop-loss e
risk-signal), conforme estudo
`studies/ema_sma_threshold_crash_protected/` completado em 2026-04-24.

**Contexto empírico honest**:

* Candidato `EMA_N150_th5_bL3_sL0 + sl30_rec10_cape05` (EMA-150
  threshold 5% + 3× UPRO synth + 30% DD stop + 10% recovery re-entry
  + CAPE λ=0.5 de-lever).
* **Educational synth 40y**: passa 6/7 gates, CAGR 24%, MDD 44.5%
* **SPY real 17y**: passa apenas 3/7 gates (G1 PBO 0.78, G2 DSR
  p > 0.05, G3 WF universal FAIL). CAGR 18.1%, MDD 43.8%, Sharpe
  0.68 — SPY buy-hold real tem Sharpe 0.90 e MDD 33.7% na mesma janela.
* **Spec §0 não cumprido**: exige ≥ 5/7 synth AND ≥ 4/7 real AND
  ≥ 4/7 ndx; candidate fica em 6/3/4. Não é cross-dataset winner.

**Riscos que o usuário assume explicitamente ao assinar**:

1. ✋ **Gate-waiving**: go-live mesmo sabendo que 3/7 gates em real data
   reprovam. Contra mandate §5 hard-block.
2. ✋ **Synth-vs-real degradation**: CAGR backtest 24% cai a ~18% real
   (−6 pp); MDD 44% piora a ~47% real
   `[leverage_for_the_long_run, p.21, Table 12]`.
3. ✋ **Worst-case 5y window**: pode vir período de −2.6% CAGR com SPY
   fazendo +9.6% (spread −12 pp/yr). Confirmado em dados synth 2015-2020.
4. ✋ **CAPE pipeline fragile**: signal source (Shiller) stale em
   2023-09; live pós-2024 degrada overlay para stop-only.
5. ✋ **Mecânica de stop em crashes rápidos**: spec §8.4 — crashes tipo
   COVID pode fazer stop disparar com equity −35 a −45% (not −30%) por
   gap de open e circuit breakers.

---

## Alterações propostas ao mandate

### §1 — Capital allocation (alteração parcial)

**De (atual, aprovado em 2026-04-23):**
> **Capital allocation (consolidado 2026-04-23):** **100% Plano C passive
> factor-tilted** (`portfolio-aposentadoria.md`). Strategy A, B, D =
> **0% DORMANT** com infra preservada. Strategy E = infra experimental
> retida em `scripts/phase_e_mvp/`. Revisão programada: 6-12 meses.

**Para:**
> **Capital allocation (parcial-reativação 2026-04-24):** **85-90% Plano C
> passive factor-tilted** (`portfolio-aposentadoria.md`). **10-15% Strategy
> B-crash-protected**: candidate `EMA_N150_th5_bL3_sL0 + sl30_rec10_cape05`
> em UPRO/SSO/SPY via Inter Internacional. Staging obrigatório: USD 500-1k
> inicial, cap USD 5k por **3 meses de paper trading** (mesmo
> sinal/stops, mock orders), upgrade para 50% do cap após validação
> paper↔backtest ± 5 pp. Strategy A, D = **0% DORMANT** continuam. Strategy E
> mantida experimental. Revisão: 6 meses (2026-10-24).

**Rationale do 10-15%**: position size conservadora reflete o gap
ainda aberto nas gates. Se paper trading mostrar reprodução clean do
backtest, upgrade gradual. Se divergir, reduzir.

### §4 — Strategy B (alteração)

**De (atual):**
> **Strategy B (swing broker US LETF rotation) DORMANT.** Caso reativada:
> Inter Internacional (§4.6), tese LETF rotation Gayed-anchored única fonte
> científica. CPCV + PBO + splits mutuamente exclusivos + bootstrap 0.001 +
> 15% DARF sempre. Goal tier Válido 17-25% líquido.

**Para:**
> **Strategy B (swing broker US LETF rotation) parcialmente reativada
> 2026-04-24** via candidate `EMA_N150_th5_bL3_sL0 + sl30_rec10_cape05`
> no UPRO (Tiingo cost model). Inter Internacional (§4.6). Gayed synth
> formula + EMA-150 threshold 5% regime filter + 30% drawdown stop-loss
> + 10% recovery-trigger re-entry + CAPE z-score sigmoid de-lever λ=0.5.
> CAPE signal via Shiller `ie_data.xls` (stale fallback: stop-only mode
> após 6 meses sem refresh). 15% DARF com isenção R$20k/mês modelada.
> Goal tier Válido 17-25% líquido (real-data expectation ~17% pós-DARF).
> Kill criteria: ver §5 atualizado.

### §5 — Gates (nova exceção documentada)

**Adicionar ao §5 atual (sem alterar gates hard-block):**
> **Exceção documentada 2026-04-24 para Strategy B-crash-protected**:
> go-live autorizado com apenas 6/7 gates no synth 40y + 3/7 em SPY
> real. Exceção limitada a este candidate específico e a cap de 15%
> do capital total. **Kill criteria**:
> - Paper trading 3-6 meses antes de qualquer dinheiro real
> - Se backtest vs paper equity divergir > 5 pp em 3 meses → reduzir
>   alocação pela metade ou abortar
> - Se live drawdown > 40% em qualquer ponto → fechar slot, retornar
>   capital a Plano C
> - Se em 2 anos live CAGR < 10% líquido (abaixo de SPY b&h), fechar
> - Se após 12 meses live G1 PBO estimado > 0.5 no running grid de
>   configs monitorados, fechar

Esta exceção é **único** registro formal de gate-waiving no projeto.
Qualquer novo caso requer override separado.

### §7 — Histórico de overrides (nova entry)

Adicionar ao final do §7:
> **2026-04-24 — Strategy B-crash-protected reativação parcial**
> `docs/mandate_overrides/2026-04-24-crash-protected-letf-open.md`.
> Aloca 10-15% em candidate `EMA_N150_th5_bL3_sL0 + sl30_rec10_cape05`
> após estudo `ema_sma_threshold_crash_protected/`. Autorização de
> gate-waiving ÚNICA, com kill criteria quantitativos em §5. Staging
> obrigatório: paper 3-6mo → USD 500-1k → cap USD 5k em 3 meses se
> validação ok.

---

## Checklist pré-execução (tem que bater TODOS antes de dinheiro real)

- [ ] Este arquivo de override assinado (`Signed YYYY-MM-DD`)
- [ ] `CLAUDE.md` + `.claude/CLAUDE.md` atualizados com reativação parcial
      (topo: "MAINTENANCE com exceção B-crash-protected 10-15%")
- [ ] `docs/investment-mandate.md` §1, §4, §5, §7 atualizados
- [ ] Pipeline CAPE automatizada: decisão (A) scrape automático ou (B)
      fallback stop-only aceito — documentado em código
- [ ] `scripts/paper_trading/ema_sma_threshold_stop_cape.py` rodando
      há ≥ 3 meses com logs completos
- [ ] Paper trading equity ± 5 pp do backtest expected em 3 meses
- [ ] Cost model detalhado (DARF + slippage + spread Inter) implementado
      no backtest e validado paper
- [ ] Monitor diário configurado (signal compute + alert em mudança de
      regime / stop fire)
- [ ] Cap de 15% aplicado: se capital total X, slot Strategy B ≤ 0.15·X
- [ ] Entry decision: USD 500 inicial, só escalar se paper ok + monitor ok

---

## O que o override NÃO autoriza

- ✗ Reativar Strategy A (Pepperstone CFD short-hold) — continua DORMANT
- ✗ Reativar Strategy D (swing BR) — continua DORMANT
- ✗ Aumentar cap acima de 15% sem override subsequente
- ✗ Ir live com qualquer outra combinação que não seja o candidate
  exato listado
- ✗ Skip paper trading

---

## Rationale honesto para assinar OU não assinar

### Assinar faz sentido se:

* Você aceita +3 pp/yr CAGR real em troca de 13 pp MDD pior que SPY
* Horizonte ≥ 10 anos (longer horizons = higher candidate win rate;
  95.9% de 10y rolling windows candidate bate SPY em synth)
* Você se compromete a executar stop/re-entry sem discricionário
  por décadas
* Você aceita que 29% dos 1y rolling windows vão ser piores que SPY —
  sem se retirar durante esses períodos

### NÃO assinar faz sentido se:

* Você tem horizonte < 10 anos
* Você é sensível a dor intermediária (5y worst-case: −2.6% CAGR vs SPY
  +9.6% = spread −12 pp/yr durante 5 anos inteiros)
* Você vai querer "rever" a estratégia em cada 1y de underperformance
* Plano C passivo atende seus objetivos de aposentadoria

---

## Assinatura do usuário

Para aprovar, substitua esta seção por:

```
✅ **Signed 2026-04-XX HH:MM**
Usuário: "[citação direta do texto de aprovação]"

Aplicado em:
- docs/investment-mandate.md §1, §4, §5, §7 — [commit hash]
- CLAUDE.md / .claude/CLAUDE.md — [commit hash]
```

Para rejeitar, substitua por:

```
❌ **Rejected 2026-04-XX**
Usuário: "[motivo]"

Mandate §1 MAINTENANCE 100% Plano C mantido. Sem alterações.
```

---

## Referências

* `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md` — veredicto
  global Phase 1+2+3
* `studies/ema_sma_threshold_crash_protected/phase3/cross_dataset_gates.md`
  — gate matrix 16 (base,combo) pairs × 3 datasets
* `studies/ema_sma_threshold_crash_protected/analysis_top_candidate/report.md`
  — deep dive top-1 candidate
* `studies/ema_sma_threshold_crash_protected/deep_review/deep_review_report.md`
  — rolling window + win rate vs SPY
* `studies/ema_sma_threshold_crash_protected/deep_review/real_gap_report.md`
  — synth→real degradation quantificada
* `studies/ema_sma_threshold_crash_protected/PRE_DEPLOYMENT_README.md`
  — checklist de 5 blockers
* Gates: `[advances_fin_ml, p.208-211, p.222-223, ch.12, p.196-202, p.31-34]`
* Synth-vs-real: `[leverage_for_the_long_run, p.21, Table 12]`
* CAPE: Campbell & Shiller 1988
