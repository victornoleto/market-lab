# Phase 3.5b — Production Deployment Runbook

> **Path tag:** `[SWING BROKER]` / Plano B.
> **Status:** ✅ Aprovado para produção (Phase 3.5b main + addendum + Task C4 closed 2026-04-17; broker Inter confirmado com SSO liberado 2026-04-18).
> **Audiência:** operador (você). Este é o runbook de deploy — não é tutorial educacional nem análise. Para rationale, siga os links.

---

## TL;DR (1 parágrafo)

Operar **um único portfólio 3-leg equal-weight** (33.3% cada em **SSO** = LETF EMA100/2x, **QQQ** = Donchian 20/10, **GLD** = Donchian 40/20) no **Banco Inter Global**, com **rebalance threshold 5-10 pp** (não diário — T+N settlement inviabiliza diário). Capital: **30% do total** em Plano B; dentro de Plano B, 100% neste portfolio. Expectativas validadas em janela 2004-2026 (21.4y): **CAGR 25.56% / Sharpe 2.108 / MaxDD -10.86%** vs SPY buy-and-hold (10.66% / 0.629 / -55.20%). 15% IR BR por venda lucrativa (DARF 6015); ~12-14 DARFs/ano total (12 inside-leg + 1-2 rebalance). Pre-deploy: abrir conta Inter Global, validar catálogo SSO, remeter capital (IOF 3.5%), montar planilha de cost basis em USD+PTAX.

---

## 1. Estratégia — Portfolio 3-leg EW

| Perna | ETF | Strategy interna | Sinal |
|-------|-----|------------------|-------|
| 1 | **SSO** (ProShares Ultra S&P500 2×) | LETF rotation EMA100 band 0% lev 2× | RISK_ON se close > EMA100 SPY; senão CASH |
| 2 | **QQQ** (Invesco Nasdaq-100) | Donchian 20/10 breakout | LONG no breakout 20d high; exit 10d low |
| 3 | **GLD** (SPDR Gold Shares) | Donchian 40/20 breakout | LONG no breakout 40d high; exit 20d low |

**Target weights:** 1/3, 1/3, 1/3. Cada perna opera **independentemente** com seu próprio sinal. Quando uma perna está em CASH (LETF off-regime), o cash permanece naquela "perna" — **não realoca para as outras pernas** (cross-leg rebalance só acontece em evento de threshold).

**Rationale:** Phase 3 iter 37-38 (jornadas [`a3d-3leg`](../../jornada/2026-04-17-0040-a3d-3leg-letf-qqq-gld-PASS.md)) + Phase 3.5b Task 6 ([`portfolio-3leg`](../../jornada/2026-04-17-1200-phase3.5b-task6-portfolio-3leg-full-validation.md)).

**Citações:** `[leverage_for_the_long_run, p.13, p.21]` (LETF rotation), `[machine_trading]` (Donchian canonical), `[advances_fin_ml, p.298-299]` (EW vs optimized blends).

---

## 2. Rebalance cadence — threshold 5-10 pp (não diário)

**Decisão operacional:** rebalance diário é **teoricamente ótimo mas fisicamente impossível** devido a T+N settlement (Inter = T+1 formal, mas cash only available para cross-buy após T+1). Além disso, diário implicaria 252 DARFs/yr — inviável.

**Default recomendado:** **threshold 5 pp** — rebalancear quando qualquer perna drifta > 5 pp do target (ex: > 38.3% ou < 28.3%).

| Threshold | Sharpe | ΔSh vs daily | Eventos/yr | DARFs/yr total | CAGR | MaxDD | Recomendado |
|-----------|--------|--------------|------------|----------------|------|-------|-------------|
| 5 pp ⭐ | **2.002** | -0.106 | 1.31 | ~13.3 | 24.66% | 11.10% | **Default produção** |
| 10 pp | 1.990 | -0.118 | 0.61 | ~12.6 | 25.47% | 11.12% | Alternativa se quiser menos DARFs |
| 15 pp | 1.972 | -0.136 | 0.37 | ~12.4 | 26.35% | 12.24% | Aceitável (drift notável) |
| annual-only | 1.967 | -0.141 | 1.08 | ~13.1 | 25.07% | 11.56% | Menos predictable |
| _daily (teto teórico)_ | _2.108_ | _—_ | _0_ | _12_ | _25.56%_ | _10.86%_ | _Referência_ |
| _never (BH puro)_ | _1.881_ | _-0.226_ | _0_ | _12_ | _40.33%*_ | _17.99%_ | _Não — drift explode_ |

**Regra operacional:** ao final de cada pregão, calcular `max(|actual_w_i - 1/3|)` por perna; se > threshold escolhido, rebalancear no próximo dia útil (não intraday). Rebalance = vender excedentes, comprar déficits com o cash da venda (T+1 settle).

**Rationale completo:** [`variants/rebalance_modes/threshold_sweep.md`](variants/rebalance_modes/threshold_sweep.md) (Task C4). Citação `[advances_fin_ml, p.275-278]`.

---

## 3. Broker — Banco Inter Global (locked)

**Decisão imutável** documentada em `docs/investment-mandate.md` §4.6.

| Item | Valor |
|------|-------|
| Plataforma | Inter Global Account + Inter&Co Securities (FINRA + Apex Clearing) |
| Acesso | Direto NYSE/NASDAQ (não BDR) |
| **SSO** | ✅ **Confirmado disponível** (usuário validou com Inter 2026-04-18) |
| QQQ, GLD | ✅ Catálogo padrão |
| Corretagem ETFs/ações US | **USD 0,00** |
| Spread FX BRL↔USD | 1.50% (Digital) / 1.25% (Black) / 0.99% (Win) |
| IOF câmbio remessa outbound | **3.50%** (Decreto 05/2025) |
| IOF retorno | 0.38% |
| Settlement | T+1 (industry US pós 2024-05-28) |
| Manutenção/custódia | USD 0,00 |
| Horário pregão | 10h30-17h Brasília (std) / 11h30-18h (DST US) |
| Fractional shares | Disponível em tickers selecionados (útil pra GLD ~$300) |

**Fragilidades documentadas:** informe rendimentos às vezes atrasa; dividendos esporadicamente não creditam; atendimento robotizado (~8d resposta). **Mitigação obrigatória:** manter planilha própria de cost basis USD + cotação PTAX do dia (não confiar no informe Inter).

---

## 4. Capital allocation

Seguindo `docs/investment-mandate.md` §1 e §4.7:

```
Capital total (100%)
├── 60-80% Passive (portfolio-aposentadoria, NÃO tocado por ai-trade)
└── 20-40% Active
    ├── Strategy A (Plano A) — Pepperstone CFD short-hold
    │   └── Status: Phase 3.5a pendente. Se não produzir winner → active cai pra 25%, tudo em Plano B.
    └── Strategy B (Plano B) — ESTE PORTFOLIO
        └── 100% no 3-leg EW (33.3% cada perna)
```

**Exemplo numérico — capital total $10k, active bucket 30%:**

| Allocation | Valor USD | Notas |
|------------|-----------|-------|
| Total | $10,000 | — |
| Passive (aposentadoria) | $7,000 (70%) | Fora do scope ai-trade |
| Active | $3,000 (30%) | — |
| — Plano A (Pepperstone) | $0 (por enquanto) | Phase 3.5a pending |
| — **Plano B (3-leg EW)** | **$3,000** | **100% do active até Strategy A landar** |
| — — SSO | $1,000 (33.3%) | — |
| — — QQQ | $1,000 (33.3%) | — |
| — — GLD | $1,000 (33.3%) | fractional shares Inter |

**Ajuste capital real:** $3,000 USD via Inter → remessa $3,000 × (1 + 3.5% IOF + 1.5% FX spread) ≈ **R$16-17k brutos pra depositar** (PTAX ~R$5.3). IOF é one-time; amortizado em 21y é ~0.16%/yr drag.

**Se Strategy A landar em Phase 3.5a:** re-split dentro dos 30% active conforme mandate rule 3 (mandate diz "parte do 20-40%" pra cada).

### 4.1 "Por que não majority em Plano B, se é tão bom?"

Pergunta recorrente e legítima: CAGR 25% + MaxDD 10% + Sharpe 2.1
**domina** passivo típico (CAGR 8-10%, MaxDD 30-40%, Sharpe ~0.6).
Intuição: "por que não 80% em Plano B?"

**Resposta curta:** os livros discordam. Mandate rule 1 (60-80% passivo)
NÃO é arbitrário — é hedge contra 5 riscos que o Sharpe isolado não
captura.

#### (a) Backtest ≠ live — leverage premium real

Gayed Table 12 `[leverage_for_the_long_run, p.21]` comparou **UPRO real
vs teórico (2009-2020)**: o ETF real teve ~2%/ano de drag vs o modelo
sintético (tracking error + gap risk + rebalance slippage
intra-diário). Nosso backtest usa `synthesize_letf_returns(fee=1%)`
pra SSO — realisticamente espere **drag ~1-1.5%/ano adicional** na
vida real. CAGR real esperado: ~23-24% (não 25.56%). MaxDD real:
~12-14% (não 10.86%). Ainda excelente — mas não é o que o backtest
mostra.

#### (b) Janela de backtest é benigna

GLD existe desde 2004. Nossa janela (2004-11 → 2026-04, 21.4y) **não
inclui** 1929 Great Depression, 1973-74 stagflação, 2000 dot-com crash.
Gayed 1928-2020 `[p.17, Table 8]` reportou 2× LRS com **MaxDD -78.7%**
em janela completa. Nossa janela cobre só o regime pós-Bretton-Woods-2
(2004+), atipicamente tranquilo. Tail events futuros (regime de
stagflação sustentada, Volcker-style rate hikes) podem levar MaxDD a
25-40%, não 10%.

#### (c) Kelly / frac-Kelly — parameter uncertainty

`[fortune_formula]` (Poundstone, Kelly criterion application) +
`[leverage_space]` (Vince): **full Kelly leva a ruína** quando os
parâmetros (edge, vol, correlação) são **estimados**, não conhecidos.
Backtest dá estimativa, não verdade. A recomendação prudente é
**half-Kelly** (metade do tamanho "ótimo"). Mesma lógica aplica ao
capital allocation: se você estima que Plano B tem Sharpe 2.1, **alocar
como se Sharpe fosse 1.05** é a decisão bayesiana-correta diante da
incerteza paramétrica.

#### (d) Failure modes não-correlacionados

Plano C (ETFs passivos) e Plano B (active LETF rotation) falham por
razões **diferentes**:

| Risco | Plano C (passivo) | Plano B (active) |
|-------|-------------------|-------------------|
| Colapso civilizacional / guerra | ❌ (falha) | ❌ (falha) |
| Inter remove SSO do catálogo | ✅ (imune) | ❌ (falha Plano B) |
| ProShares fecha SSO fund | ✅ (imune) | ❌ (falha Plano B) |
| FFR > 8% sustentado 5+ anos | ✅ (baixo impact) | ⚠️ (drag 6%+/yr LETF) |
| Mudança Lei 14.754 ou DARF 6015 | ⚠️ (médio) | ⚠️ (médio) |
| Regime shift (stagflação tipo 70s) | ⚠️ (baixo growth) | ❌ (MaxDD -40%+) |
| Model break (EMA100 para funcionar) | ✅ (imune) | ❌ (falha Plano B) |

Ter **ambos** = probabilidade de falha simultânea **muito menor** que
qualquer um isolado. Diversification across failure modes é a mesma
matemática de ter 3 pernas no portfolio (ρ baixo entre falhas), só que
um nível acima.

#### (e) Behavioral — risk of ruin literal

Gayed `[p.19-20]` define literalmente:
> "**Risk of Ruin** — Drawdown path where an investor **abandons** the
> strategy before recovery."

Kahneman/Tversky: **dor psicológica ≈ 2× o ganho equivalente**
(prospect theory). Se 80% do patrimônio total cai -15% (MaxDD realista
com drag), você sente o equivalente a **-24% de dor**. Probabilidade de
vender no pior momento sobe dramaticamente. 30% em Plano B com mesmo
-15% = -4.5% do total = tolerável.

**Traduzindo:** a estratégia tecnicamente otimal é irrelevante se você
não conseguir segurá-la durante drawdown.

#### (f) Mandate rule 1 — rationale documentado

`docs/investment-mandate.md` §1 estabeleceu 60-80% passivo por estas 5
razões ANTES de ter winner. Agora que temos winner, a tentação de
inverter é previsível — mas os 5 riscos (a)-(e) não mudaram. Winner
validado **não muda a distribuição de tail risk**.

### 4.2 Escalação gradual com track record (recomendação)

Pode-se AJUSTAR a allocation conforme Plano B acumula track record
live. Pode-se NÃO INVERTER pré-evidência:

| Fase | Passivo | Ativo (A+B) | Condição de avanço |
|------|---------|-------------|--------------------|
| **Hoje (0 meses live)** | **70-80%** | 20-30% | Zero track record real. Default mandate rule 1. |
| +6 meses live | 65-75% | 25-35% | Se Sharpe realizado ≥ 1.5 nos 6m |
| +12 meses live | 60-70% | 30-40% | Se continuar batendo backtest ±30% |
| +24 meses live | 55-65% | 35-45% | Se sobreviveu ≥1 drawdown ≥5% sem abandono |
| +60 meses live | **50-60%** | **40-50%** | Cap operacional pré-10y track record |
| **Nunca** | < 50% | > 50% | Mandate floor — requer 10y live + §7 override |

**Regra de polegar:** bucket ativo só cresce com **evidência live
equivalente**. Backtest de 21 anos ≠ 1 ano real. A tentação de
escalar rápido é o sinal de alarme.

### 4.3 Se Plano A (Phase 3.5a) não produzir winner

Mandate §4.7: active bucket cai para 25% (todo em Plano B). Allocation
fica **75% passivo / 25% Plano B**. Ainda mais conservador que os
20-40% originais, porque ter só Plano B = concentração de failure mode
tipo (d) acima.

---

## 5. Expected metrics (production default — threshold 5 pp)

**Janela de referência:** 2004-11-18 → 2026-04-14 (21.36 anos, 5383 bars, GLD-limited).
**Custos modelados:** 5 bps spread + 10 bps commission round-trip, 15% BR IR por saída lucrativa, swap = 0.

| Métrica | Valor (threshold 5pp) | vs daily | vs SPY B&H |
|---------|-----------------------|----------|-----------|
| CAGR | 24.66% | -0.9 pp | **+14.0 pp** |
| Sharpe | 2.002 | -0.106 | +1.373 |
| MaxDD | 11.10% | +0.24 pp | -44.1 pp (4.5× mais seguro) |
| Sortino | ~3.0 | ≈ daily | +2.4 |
| Calmar | ~2.2 | ≈ daily | +2.0 |
| Rebal events/yr | 1.31 | +1.31 | — |
| DARFs/yr total | ~13 | +1 | — |
| IR 15% paga/yr | ~$24k em $100k | — | — |

**Stress windows (Task 7b — [`robustness/stress_isolated.md`](robustness/stress_isolated.md)):** MaxDD do portfolio em 2008/2020/2022/2025 **nunca excedeu 6.85%**. LETF regime filter (EMA100) absorveu o grosso dos crashes (LETF ficou em cash durante 2008).

**Reality check sobre leverage:** nosso backtest mede 2× via `synthesize_letf_returns(fee=1%)`. Gayed Table 12 `[leverage_for_the_long_run, p.21]` reporta **"negative leverage premium" ~2% drag/yr** em UPRO real. Para SSO (2×), esperar **drag ~1-1.5%/yr** adicional na vida real — MaxDD real provavelmente ~12-14% em vez de 11%. Ainda dentro de tolerância.

---

## 6. Riscos e flags (awareness pré-deploy)

Todos os FLAGs foram documentados durante Phase 3.5b e **não invalidam o winner**, mas você precisa estar ciente:

| Flag | Severidade | Mitigação |
|------|-----------|-----------|
| **FFR regime sensitivity** do LETF | 🟡 média | Custo de leverage real sobe com FFR; Task 7a confirmou edge sobrevive ([`robustness/testfolio_vs_synthetic_letf.md`](robustness/testfolio_vs_synthetic_letf.md)) |
| **GLD standalone Sharpe < 1.0** (0.937) | 🟡 média | GLD só funciona como perna 3 (ρ~0 com equity); **não operar GLD sozinho** |
| **Real UPRO 3x tem MaxDD ~50%** (Gayed p.21 Table 12) | 🔴 alta (se tentar 3x) | **Mantemos 2× SSO**; 3× explicitamente rejeitado Task B3 |
| **2-leg sem GLD** falha DR gate | 🟡 média | Se Inter algum dia remover GLD, degrada para 2-leg LETF+QQQ (Sharpe -0.22) |
| **Inter informe rendimentos atrasa** | 🟡 média | Planilha própria obrigatória |
| **Cashflow rebalance** sozinho (sem sells) drift explode 65pp | 🟡 média | Não usar — threshold 5-10pp é o caminho |
| **Dividendos Inter às vezes não creditam** | 🟢 baixa | Monitorar mensalmente |

**Regra mãe:** se qualquer flag vira red (ex: Inter anuncia que SSO sai do catálogo, ou FFR sobe pra 8%+ sustentado), reavaliar. Não "apertar o gate" nem torturar os dados — **re-design do zero**, mandate §5.4.

---

## 7. Pre-deploy checklist (ordem de execução)

- [ ] **1. Validar conta Inter.** Abrir Inter Global Account se ainda não tem. Habilitar Inter&Co Securities (conta internacional). Tier Digital/Black/Win define spread FX.
- [ ] **2. Confirmar catálogo Inter** (✅ SSO, QQQ, GLD). Tela de busca Inter Global → testar cotação nos 3 tickers.
- [ ] **3. Definir capital Plano B.** Decidir % active bucket → capital USD → valor BRL a remeter (incluir 3.5% IOF + 1.5% FX spread).
- [ ] **4. Remessa inicial.** Enviar BRL para USD via Inter. Aguardar settlement (~1 dia útil).
- [ ] **5. Planilha cost basis.** Criar Google Sheets / Excel com colunas: `date, ticker, action (BUY/SELL), qty, price_usd, ptax_ask, cost_basis_brl, realized_gain_brl, darf_due_month`. Essa planilha é a fonte de verdade fiscal — NÃO o informe Inter.
- [ ] **6. Definir threshold.** Escolher 5 pp (default) ou 10 pp (menos DARFs).
- [ ] **7. Scripts de monitoramento.** Setup local: script Python que lê preços Inter (ou Yahoo/Tiingo manual) e calcula daily signal por perna + drift atual + threshold trigger. Placeholder: `scripts/plano_b_daily_check.py` (não implementado ainda — Phase 4).
- [ ] **8. Primeira compra.** Entry ≠ market open. Confirmar sinal LETF (SPY vs EMA100) antes de comprar SSO — se off-regime, começar em cash naquela perna.
- [ ] **9. Backup disaster recovery.** Como liquidar tudo em caso de emergência? Inter app → ordem market sell 3 tickers → settlement T+1 → FX retorno + IOF 0.38%.

---

## 8. Monitoring checklist (live operation)

### Diário (5 min)
- [ ] Abrir Inter Global → verificar saldos 3 pernas.
- [ ] Calcular `w_i = equity_i / equity_total` para as 3 pernas.
- [ ] Se `max(|w_i - 1/3|) > threshold_pp/100` → rebalance no próximo pregão.
- [ ] Checar sinais internos:
  - SSO: SPY close vs EMA100 (regime on/off).
  - QQQ: em posição? Exit no próximo 10-day low?
  - GLD: em posição? Exit no próximo 20-day low?
- [ ] Se algum sinal mudou, executar ordem correspondente no próximo dia.

### Mensal (30 min)
- [ ] Atualizar planilha cost basis com todas trades do mês (BUY, SELL, REBAL).
- [ ] Calcular ganho realizado (FIFO) nas vendas do mês.
- [ ] Se ganho > 0 → gerar DARF 6015 (15% do ganho). Pagar até último dia útil do mês seguinte.
- [ ] Backup planilha (Google Drive / email).

### Trimestral (1h)
- [ ] Rodar backtest ρ rolling 252d entre SSO/QQQ/GLD no período recente.
- [ ] Alerta: se qualquer par ρ > 0.70 sustentado por > 20 dias, flag. Diversification pode estar quebrando (Task 7e [`robustness/rolling_correlation.md`](robustness/rolling_correlation.md)).
- [ ] Comparar Sharpe realizado últimos 90d vs expectativa (2.002).
- [ ] Se Sharpe realizado < 0.5 por 90d consecutivos → investigar (model-reality gap).

### Anual (2h, fim de ano fiscal)
- [ ] Baixar informe rendimentos Inter Global (se disponível).
- [ ] Reconciliar com planilha própria. Divergências → planilha manda.
- [ ] Declaração IRPF: bens no exterior (ações/ETFs) + ganhos de capital (se houve).
- [ ] Rever allocation: capital cresceu? Manter 30% active ou ajustar?

---

## 9. Navegação rápida

**Main docs:**
- [Summary jornada](../../jornada/2026-04-17-2045-phase3.5b-full-validation-summary.md) — verdict completo
- [Addendum jornada](../../jornada/2026-04-17-2245-phase3.5b-addendum-summary.md) — variants
- [Task C4 jornada](../../jornada/2026-04-17-2315-phase3.5b-addendum-task-c4-threshold-rebalance.md) — threshold decision
- [Allocation doc](../../docs/phase3_winners_allocation.md) — "1 portfolio vs 3 strategies"
- [Investment mandate](../../docs/investment-mandate.md) §4.6 — broker Inter details

**Individual sleeves:**
- [LETF rotation EMA100/2x](letf_rotation_ema100_2x/standard_report.md)
- [QQQ Donchian 20/10](qqq_donchian_20_10/standard_report.md)
- [GLD Donchian 40/20](gld_donchian_40_20/standard_report.md)
- [Portfolio 3-leg EW](portfolio_3leg_ew/standard_report.md)

**Robustness:**
- [testfolio vs synthetic LETF](robustness/testfolio_vs_synthetic_letf.md) (Task 7a)
- [Stress isolated](robustness/stress_isolated.md) (Task 7b)
- [Slippage sensitivity](robustness/slippage_sensitivity.md) (Task 7c)
- [Allocation 5-way](robustness/allocation_comparison.md) (Task 7d)
- [Rolling correlation](robustness/rolling_correlation.md) (Task 7e)
- [Vol-target sizing](robustness/vol_target_sizing.md) (Task 7f)

**Variants (reference only):**
- [2-leg LETF+QQQ](variants/letf_qqq_2leg_ew/standard_report.md) — fallback se GLD sai
- [Leverage 2×/2.5×/3×](variants/letf_leverage_comparison/README.md) — 2× continua o único
- [Rebalance modes + threshold sweep](variants/rebalance_modes/README.md) — base da decisão §2

---

**Última atualização:** 2026-04-18 (SSO confirmado Inter → bloqueador removido).
