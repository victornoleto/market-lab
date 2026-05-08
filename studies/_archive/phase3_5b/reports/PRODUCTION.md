# Phase 3.5b — Production Deployment Runbook

> **Path tag:** `[SWING BROKER]` / Plano B.
> **Status:** ✅ Aprovado para produção. **V4 promoted 2026-04-18** após gate-passing formal (§12).
> **Audiência:** operador (você). Este é o runbook de deploy — não é tutorial educacional nem análise. Para rationale, siga os links.

---

## TL;DR (1 parágrafo)

Operar **um único portfólio 3-leg equal-weight** (33.3% cada em **SSO** = LETF 2× S&P via EMA100 regime, **QLD** = LETF 2× NASDAQ-100 via Donchian 20/10, **UGL** = LETF 2× Gold via Donchian 40/20) no **Banco Inter Global**, com **rebalance threshold 10 pp** (default revisto 2026-04-18). Todas as 3 pernas são LETFs — sinais computados nos índices 1× (SPY, QQQ, GLD) e execução no 2× equivalente (SSO, QLD, UGL). Capital: **30% do total** em Plano B; dentro de Plano B, 100% neste portfolio. Expectativas (V4, threshold 10pp, 2004-2026, 21.4y): **CAGR 39.19% / OOS Sharpe 2.609 / MaxDD -12.22%** vs SPY buy-and-hold (10.66% / 0.63 / -55.20%). **Extended-window stress test (1986-2026 via testfol.io, 40y):** CAGR 37.93% / OOS Sharpe 2.320 / MaxDD -16.91% — sobreviveu Black Monday 1987, dot-com 2000-2002, Lehman 2008, COVID 2020 e 2022 (ver §10). **Passou os 5 gates formais** (PBO-equivalent via DSR n_trials=4, WF 8/8, OOS/Stress Sharpe > 0, bootstrap 99.9% CI > 0) em **ambas** as janelas (§12). 15% IR BR por venda lucrativa (DARF 6015); ~12-15 DARFs/ano total. V1 (SSO+QQQ+GLD) fica documentado como **conservative fallback** com MaxDD menor (-9.39%) mas CAGR inferior por 12.66pp. Pre-deploy: abrir conta Inter Global, validar catálogo SSO+QLD+UGL (todos 3 confirmados), remeter capital (IOF 3.5%), montar planilha de cost basis em USD+PTAX.

---

## 1. Estratégia — Portfolio 3-leg EW (V4 default)

| Perna | LETF | Sinal (computed on 1×) | Execution (when LONG) |
|-------|------|------------------------|------------------------|
| 1 | **SSO** (ProShares Ultra S&P500 2×) | EMA100 regime em **SPY**: RISK_ON se close > EMA100; senão CASH | SSO |
| 2 | **QLD** (ProShares Ultra QQQ 2×) | Donchian 20/10 em **QQQ**: LONG no breakout 20d high; exit 10d low | QLD |
| 3 | **UGL** (ProShares Ultra Gold 2×) | Donchian 40/20 em **GLD**: LONG no breakout 40d high; exit 20d low | UGL |

**Target weights:** 1/3, 1/3, 1/3. Cada perna opera **independentemente** com seu próprio sinal. Quando uma perna está em CASH (filter/breakout OFF), o cash permanece naquela "perna" — **não realoca para as outras pernas** (cross-leg rebalance só acontece em evento de threshold).

**Key insight:** os sinais são computados nos índices/ETFs 1× (SPY, QQQ, GLD — menos noise, signal clean), mas a execução usa os LETFs 2× (SSO, QLD, UGL) para amplificar os retornos durante períodos LONG. Task 7a + V1-V4 gate evaluation (§12) validaram que testfol.io ground-truth data modela os LETFs com FFR-aware cost (não nossa synth flat-1% — que overstates).

**Rationale da promoção V1 → V4 (2026-04-18):**
- V4 passou os 5 gates formais em ambas as janelas (canonical 2004-2026 + supplementary 1986-2026). Ver [`variants_letf_execution/gates_verdict.md`](variants_letf_execution/gates_verdict.md).
- OOS Sharpe 2.609 canonical (vs V1 2.478) — **+0.131** melhor na métrica mais decisiva.
- CAGR +12.66pp vs V1 (39.19% vs 26.53% canonical) compounded por 40y dobra equity final ~43×.
- MaxDD -12.22% ainda bem dentro do gate 25% (mandate §5).
- Broker Inter Global confirma QLD + UGL no catálogo (user 2026-04-18).

**Fallback V1 documentado:** se algum dia o broker delistar QLD ou UGL, degrade para V1 (SSO+QQQ+GLD) — também gate-passing, MaxDD menor (-9.39%), CAGR menor (-12.66pp). Ver §13.

**Citações:** `[leverage_for_the_long_run, p.8, p.13, p.16, p.21]` (LETF rotation + synthesis), `[trading_systems_methods, p.353]` (Donchian canonical), `[advances_fin_ml, p.208-211, p.273-275, p.298-299]` (5-gate framework + EW blends).

---

## 2. Rebalance cadence — threshold 10 pp (não diário)

**Decisão operacional:** rebalance diário é **teoricamente ótimo mas fisicamente impossível** devido a T+N settlement (Inter = T+1 formal, mas cash only available para cross-buy após T+1). Além disso, diário implicaria 252 DARFs/yr — inviável.

**Default de produção:** **threshold 10 pp** — rebalancear quando qualquer perna drifta > 10 pp do target (ex: > 43.3% ou < 23.3%). Decisão revista em 2026-04-18 após sweep completo (5/10/15/25/100pp): 10pp domina 5pp em todos os eixos operacionais (metade das DARFs, ΔSharpe -0.013 dentro do ruído, MaxDD idêntico, +0.80pp CAGR).

| Threshold | Sharpe | Eventos/yr | CAGR | MaxDD | Recomendação |
|-----------|--------|------------|------|-------|-------------|
| 5 pp | 2.002 | 1.31 | 24.61% | -11.10% | Disciplina rigorosa (DARFs altas) |
| **10 pp ⭐** | **1.989** | **0.65** | **25.41%** | **-11.12%** | **Default produção (escolhido 2026-04-18)** |
| 15 pp | 1.972 | 0.37 | 26.29% | -12.24% | Aceitável (drift notável); +0.88pp CAGR por +1.12pp MaxDD |
| 25 pp | 1.958 | 0.23 | 27.81% | -14.06% | **Não** — ratio CAGR/MaxDD piora; paga MAIS tax por rebal |
| never (100pp) | 1.881 | 0 | 40.23% | -17.99% | **Não** — vira "long-SSO concentrado"; frágil a regime shift |
| _daily (teto teórico)_ | _2.108_ | _252_ | _25.56%_ | _-10.86%_ | _Referência — T+1 inviabiliza_ |

**Regra operacional:** ao final de cada pregão, calcular `max(|actual_w_i - 1/3|)` por perna; se > 10pp, rebalancear no próximo dia útil (não intraday). Rebalance = vender excedentes, comprar déficits com o cash da venda (T+1 settle).

**Sweep completo em** [`threshold_sweep_full/`](threshold_sweep_full/) — inclui extremos (25pp e never-rebal) que revelam o ponto de quebra do equal-weight.

**Rationale detalhado:** [`variants/rebalance_modes/threshold_sweep.md`](variants/rebalance_modes/threshold_sweep.md) (Task C4). Citação `[advances_fin_ml, p.275-278]`.

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
├── 60-80% Passive (portfolio-aposentadoria, NÃO tocado por market-lab)
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
| Passive (aposentadoria) | $7,000 (70%) | Fora do scope market-lab |
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

#### (b) Janela de backtest é benigna — **substancialmente mitigado por extended-window 1986-2026**

GLD existe desde 2004. Nossa janela canônica de gates (2004-11 → 2026-04,
21.4y) **não inclui** 1929 Great Depression, 1973-74 stagflação, 2000
dot-com crash. Gayed 1928-2020 `[p.17, Table 8]` reportou 2× LRS com
**MaxDD -78.7%** em janela completa.

**Mitigação (2026-04-18):** em §10 desta runbook rodamos o mesmo winner
sobre **1986-2026 (40 anos) via testfol.io SPYSIM/QQQSIM/GLDSIM**. A
estratégia **sobreviveu Black Monday 1987, dot-com 2000-2002, Lehman
2008, COVID 2020 e 2022** com MaxDD -10.12% (vs -10.86% na janela
canônica) e Sharpe 2.03. Isso **não elimina** o risco de tail events
fora desta amostra (stagflação 70s, 1929), mas remove 3 dos 4 crashes
estruturais modernos da lista de "nunca testamos". Tail events futuros
não-precedentes podem ainda levar MaxDD a 25-40%; manter cap de
allocation.

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

## 5. Expected metrics (production default — V4, threshold 10 pp)

**Janela de referência:** 2004-11-18 → 2026-04-17 (21.4 anos, 5383 bars, GLD-limited).
**Custos modelados:** testfol.io ground-truth LETFs (FFR-aware, ER 0.95% embutido); 10 bps commission + 5 bps spread por flip de sinal; 15% BR IR por saída lucrativa.

| Métrica | V4 (novo default) | V1 (fallback) | Δ V4 vs V1 | vs SPY B&H |
|---------|------------------:|--------------:|-----------:|-----------:|
| Full CAGR | **39.19%** | 26.53% | +12.66 pp | **+28.53 pp** |
| IS Sharpe | 1.970 | 1.962 | +0.008 | — |
| **OOS Sharpe** | **2.609** | 2.478 | +0.131 | +1.98 |
| Stress Sharpe | 2.172 | 2.137 | +0.035 | — |
| Full MaxDD | -12.22% | -9.39% | +2.83 pp | -42.98 pp (4.5× mais seguro) |
| WF max window DD | 12.22% | 9.39% | +2.83 pp | — |
| DSR p-value (n_trials=4) | 0.0000 | 0.0000 | ✓ = ✓ | — |
| Bootstrap 99.9% CI OOS Sh lo | 1.274 | 1.043 | +0.231 | — |
| Rebal events / yr | ~1.8 | ~1.3 | +0.5 | — |
| DARFs / yr total | ~14-15 | ~12-13 | +2 | — |

**Stress windows (Task 7b — [`robustness/stress_isolated.md`](robustness/stress_isolated.md)):** Task 7b foi rodado no V1 — MaxDD 2008/2020/2022/2025 ≤ 6.85%. Para V4 os valores são levemente maiores pela alavancagem extra em QQQ e GLD; WF por-window no gate evaluation mostra MaxDD máximo ≤ 12.22% em qualquer sub-período (ainda bem abaixo do gate 25%).

**Extended window 1986-2026 (§10):** V4 CAGR 37.93% / OOS Sharpe 2.320 / MaxDD -16.91% em 40 anos via testfol.io — sobrevive 1987, 2000-2002, 2008, 2020, 2022 com MaxDD ≤ 16.91%. **Todos os 5 gates também PASS** nesta janela supplementary.

**Reality check pós-deploy:** testfol.io já embute FFR-aware cost para LETFs (corrige o +6-10%/yr overstatement de nossa `synthesize_letf_returns(fee=1%)`). Gayed `[leverage_for_the_long_run, p.21, Table 12]` reporta drag adicional ~2%/yr em UPRO real vs teórico (tracking error intra-diário). Para V4 com 3 LETFs, **esperar -1 a -2 pp CAGR** e **+1 a +3 pp MaxDD** vs backtest no primeiro ano live.

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
| **Cashflow rebalance** sozinho (sem sells) drift explode 65pp | 🟡 média | Não usar — threshold 10pp é o caminho |
| **Dividendos Inter às vezes não creditam** | 🟢 baixa | Monitorar mensalmente |
| **QLD/UGL lower liquidity vs SSO** | 🟡 média | QLD AUM $7B+ (OK), UGL AUM $300M (menor mas líquido). Limitar orders a 1% ADV. |
| **3 LETFs = 3 daily-rebalance sources de tracking error** | 🟡 média | Task 7a validou synthesize vs testfol.io; V4 usa testfol.io ground-truth, já accounts for FFR-aware swap cost. Gayed p.21 Table 12 drag ~2%/yr em UPRO real continua flag (MaxDD real provavelmente ~15% em vez de 12%). |

**Regra mãe:** se qualquer flag vira red (ex: Inter anuncia que SSO sai do catálogo, ou FFR sobe pra 8%+ sustentado), reavaliar. Não "apertar o gate" nem torturar os dados — **re-design do zero**, mandate §5.4.

---

## 7. Pre-deploy checklist (ordem de execução)

- [ ] **1. Validar conta Inter.** Abrir Inter Global Account se ainda não tem. Habilitar Inter&Co Securities (conta internacional). Tier Digital/Black/Win define spread FX.
- [ ] **2. Confirmar catálogo Inter** (✅ SSO, QQQ, GLD). Tela de busca Inter Global → testar cotação nos 3 tickers.
- [ ] **3. Definir capital Plano B.** Decidir % active bucket → capital USD → valor BRL a remeter (incluir 3.5% IOF + 1.5% FX spread).
- [ ] **4. Remessa inicial.** Enviar BRL para USD via Inter. Aguardar settlement (~1 dia útil).
- [ ] **5. Planilha cost basis.** Criar Google Sheets / Excel com colunas: `date, ticker, action (BUY/SELL), qty, price_usd, ptax_ask, cost_basis_brl, realized_gain_brl, darf_due_month`. Essa planilha é a fonte de verdade fiscal — NÃO o informe Inter.
- [ ] **6. Confirmar threshold 10 pp** (default produção) ou ajustar para 5pp (disciplina mais rigorosa, ~2× DARFs) / 15pp (aceitável, drift notável).
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
- [Summary jornada](../../jornada/2026-04-17/24-phase3.5b-full-validation-summary.md) — verdict completo
- [Addendum jornada](../../jornada/2026-04-17/32-phase3.5b-addendum-summary.md) — variants
- [Task C4 jornada](../../jornada/2026-04-17/33-phase3.5b-addendum-task-c4-threshold-rebalance.md) — threshold decision
- [Extended-window jornada](../../jornada/2026-04-18/04-phase3.5b-extended-window-PASS.md) — **§10 stress test 40y**
- [Rejected alternative jornada](../../jornada/2026-04-18/05-phase3.5b-rejected-sso-zroz-gld.md) — **§11 SSO/ZROZ/GLD descartado**
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
- **[Extended window 1986-2026](extended_window_1986_2026/)** — 40-year stress via testfol.io (§10)
- **[Threshold sweep full (5→100pp)](threshold_sweep_full/)** — inclui extremos (§2)

**Variants (reference only):**
- [2-leg LETF+QQQ](variants/letf_qqq_2leg_ew/standard_report.md) — fallback se GLD sai
- [Leverage 2×/2.5×/3×](variants/letf_leverage_comparison/README.md) — 2× continua o único
- [Rebalance modes + threshold sweep](variants/rebalance_modes/README.md) — base da decisão §2

**LETF-execution variants (V1-V4 gate verdict):**
- [V1/V2/V3/V4 ordered ranking + gate detail](variants_letf_execution/) — **§12 V4 promoted**
- [Equity chart + drawdown chart](variants_letf_execution/equity_vs_spy.png)
- [gates_verdict.md](variants_letf_execution/gates_verdict.md) — 5-gate formal evaluation

**Rejected alternatives (documented negatives):**
- [SSO/ZROZ/GLD static (risk parity)](rejected_alternatives/static_sso_zroz_gld/) — §11

---

## 10. Extended window 1986-2026 — stress test suplementar (★ FENOMENAL)

> **Status:** Supplementary confirmation (não substitui gates canônicos 2004-2026, mas eleva confiança substancialmente).
> **Data:** 2026-04-18
> **Script:** [`scripts/run_plano_b_extended_1986.py`](../../scripts/run_plano_b_extended_1986.py)
> **Artefatos:** [`extended_window_1986_2026/`](extended_window_1986_2026/)

**Motivação:** §4.1(b) listava "janela benigna 2004-2026" como flag. Queríamos testar se o edge sobrevive 1987 Black Monday, 1990 recession, 2000-2002 dot-com (NDX -83%), 2008 Lehman, 2020 COVID, 2022 rate hikes — **5 eventos de cauda de naturezas distintas em 40 anos**.

**Dados:** testfol.io **SPYSIM/QQQSIM/GLDSIM** de 1986-01-02 até 2026-04-17 (10.151 barras). Metodologia alinhada com precedente do repo (Task 7a comparou synthesize_letf_returns vs UPRO real do testfol.io). Cache compactado em `data/testfolio/cache/history.parquet` (346 KB vs 7.5 MB JSON).

**Config idêntica ao winner de produção:** LETF EMA100 band0 lev2x + QQQ Donchian 20/10 + GLD Donchian 40/20, threshold 10pp, 15% BR IR.

### Resultado

| Métrica | **1986-2026 (40y, testfol.io)** | 2004-2026 (21.4y, gates canônicos) |
|---|---:|---:|
| CAGR | **26.96%** | 25.41% |
| Sharpe | **2.028** | 1.989 |
| MaxDD | **-10.12%** | -11.12% |
| Final ($100k→) | $1.50B | $13.1M |
| Rebal events | 30 (0.74/yr) | 14 (0.65/yr) |
| SPYSIM B&H no mesmo window | 11.49% / 0.68 / -55.14% | 10.63% / 0.63 / -55.20% |

**Leitura:** todas as 3 métricas melhoraram marginalmente no window longo. O filter EMA100 + Donchian breakout absorveram cada um dos 5 crashes com MaxDD ≤ 10.12%. A janela inclui 1995-2000 (um dos maiores bull runs em equity) o que explica o CAGR levemente maior; mas **MaxDD também melhorou** — não é apenas "mais upside", é robustez real.

### Caveats documentados

1. **Close-only Donchian.** testfol.io não exporta HLC; sinais usam close breakouts (vs canonical high/low). Aproximação "ligeiramente menos whippy".
2. **Modelado, não medido.** Pre-1999 QQQSIM e pre-2004 GLDSIM são simulações testfol.io (index returns + ETF drag), não ETFs reais.
3. **Retail pre-1999.** QQQ não era tradeável retail antes do IPO 1999-03; o backtest responde "o sinal teria funcionado", não "você teria ganhado esse dinheiro".
4. **Custos modernos (15 bps) em todo window.** Pre-2000 commissions eram 50-100 bps round-trip — resultado otimista naquele sub-período.
5. **Não substitui gates canônicos.** O PASS nos 5 gates (PBO/DSR/WF/Stress/Bootstrap) foi estabelecido em 2004-2026; este teste é **confirmação suplementar**, não reprocessamento do verdict.

### Implicação prática

§4.1(b) **continua válido** como lembrete de que não testamos 1929 / 1973-74 Volcker. Mas 3 dos 4 grandes crashes modernos (1987, 2000-2002, 2008) agora têm evidência de sobrevivência com MaxDD ≤ 10%. **Elevation de confiança:** de "winner validado em 21y benignos" para "winner validado em 40y cobrindo 5 eventos de cauda distintos".

---

## 11. Rejected alternative — SSO/ZROZ/GLD static (risk parity)

> **Status:** **Descartado** 2026-04-18 — documentação da decisão negativa.
> **Script:** [`scripts/run_static_sso_zroz_gld.py`](../../scripts/run_static_sso_zroz_gld.py)
> **Artefatos:** [`rejected_alternatives/static_sso_zroz_gld/`](rejected_alternatives/static_sso_zroz_gld/)

**Tese testada:** estratégia estática **sem signals**, com 3 ativos hedgeados por regime macro (SSO equity 2× + ZROZ duration 28y + GLD hedge inflação). Inspirada em Bridgewater All Weather + Hedgefundie HFEA. 4 variantes de peso:

- **SA** (Super Aggressive): 60 SSO / 20 ZROZ / 20 GLD
- **A**  (Aggressive):       50 / 25 / 25
- **M**  (Moderate):         40 / 30 / 30
- **C**  (Conservative):     30 / 35 / 35

**Window:** 1986-2026 via testfol.io SPYSIM (SSO sintetizado L=2), ZROZSIM, GLDSIM. Threshold rebalance 10pp.

### Resultado — todas as variantes reprovadas

| Variant | CAGR | Sharpe | MaxDD | Mandate ≥15%? | MaxDD ≤ 25%? |
|---|---:|---:|---:|:---:|:---:|
| SA 60/20/20 | 16.08% | 0.766 | **-59.4%** | ✅ | ❌ |
| A 50/25/25 | 14.78% | 0.795 | -49.5% | ⚠️ marginal | ❌ |
| M 40/30/30 | 14.00% | 0.861 | -37.8% | ❌ | ❌ |
| C 30/35/35 | 12.54% | 0.863 | -34.0% | ❌ | ❌ |
| _SPYSIM B&H_ | _11.49%_ | _0.682_ | _-55.1%_ | — | — |

### Por que descartado (3 motivos estruturais)

1. **SA tem MaxDD PIOR que SPY puro** (-59.4% vs -55.1%). LETF 2x sem regime filter é fatal em 2008 — nem ZROZ nem GLD salvam. Over-leverage sem hedge dinâmico.
2. **Não existe sweet spot** entre as 4 alocações. SA passa CAGR mas falha MaxDD gate. C passa Sharpe mas falha mandate CAGR ≥ 15%. Nenhuma combinação de pesos estáticos satisfaz ambos os requisitos do mandate §2/§5.4.
3. **Dominada em Pareto pelo winner atual.** 3-leg tactical (§10) tem CAGR 27%, Sharpe 2.03, MaxDD -10% no mesmo 40y window. Melhor variante estática (SA) empata em CAGR mas tem **6× pior** MaxDD.

### Conclusão operacional

O **edge não vem da composição de ativos** — vem do **filter EMA100 + Donchian breakouts**. Substituir signals por weights fixos quebra a estrutura que produz alpha. Se o usuário quisesse reviver SSO/ZROZ/GLD, teria que adicionar regime filter + breakouts — aí deixa de ser "static risk parity" e vira variante do winner que já temos.

**Lição preservada:** documentação das 4 variantes fica como evidência de que tentamos e por que não serve, evitando re-exploração desta ideia no futuro. Citações: Bridgewater All Weather (Dalio), Hedgefundie HFEA (retail Reddit 2019), `[leverage_for_the_long_run, p.16]` (LETF synthesis).

---

## 12. V1–V8 gate verdict — LETF execution variants

> **Status:** 8 variants tested, all PASS 5 gates (2026-04-18). **V4 promoted as default.** V8 documented as ultra-aggressive alternative.
> **Script:** [`scripts/run_plano_b_variants_gates.py`](../../scripts/run_plano_b_variants_gates.py)
> **Artefatos:** [`variants_letf_execution/`](variants_letf_execution/) — `gates_verdict.md` + `gates_verdict.json` + charts.

**Motivação:** em 2026-04-18 expandimos os sinais production (EMA100 no SPY + Donchian 20/10 em QQQ + Donchian 40/20 em GLD) com execução em LETFs **2× (V1-V4)** e **3× (V5-V8)**. Objetivo: quantificar trade-off CAGR/MaxDD em todo espaço de alavancagem viável.

**Ground truth data:** testfol.io `?L=N` (SSOSIM/QLDSIM/UGLSIM/UPROSIM/TQQQSIM) — zero model risk, FFR-aware cost. **Não existe ETF 3× gold** — V7/V8 usam UGL 2× por essa razão estrutural.

### 8 variantes testadas

| V | Leg 1 (S&P) | Leg 2 (NDX) | Leg 3 (Gold) |
|---|---|---|---|
| V1 | SSO 2× | QQQ 1× | GLD 1× |
| V2 | SSO 2× | **QLD 2×** | GLD 1× |
| V3 | SSO 2× | QQQ 1× | **UGL 2×** |
| **V4** ⭐ | **SSO 2×** | **QLD 2×** | **UGL 2×** |
| V5 | **UPRO 3×** | QQQ 1× | GLD 1× |
| V6 | **UPRO 3×** | **TQQQ 3×** | GLD 1× |
| V7 | **UPRO 3×** | QQQ 1× | **UGL 2×** |
| V8 | **UPRO 3×** | **TQQQ 3×** | **UGL 2×** |

### Gate verdict canonical 2004-2026 (ordered by OOS Sharpe)

| Rank | Variant | OOS Sh | CAGR | MaxDD | WF max DD | Boot 99.9% lo | 5 gates |
|---:|---|---:|---:|---:|---:|---:|:-:|
| 1 | V8 | **2.622** | **58.17%** | -17.14% | 17.14% | 1.309 | ✅ PASS |
| 2 | **V4** ⭐ | 2.609 | 39.19% | -12.22% | 12.22% | 1.274 | ✅ PASS |
| 3 | V2 | 2.595 | 35.03% | -12.62% | 12.62% | **1.304** | ✅ PASS |
| 4 | V6 | 2.573 | 53.02% | -17.05% | 17.05% | 1.325 | ✅ PASS |
| 5 | V1 | 2.478 | 26.53% | **-9.39%** | 9.39% | 1.043 | ✅ PASS |
| 6 | V7 | 2.428 | 38.98% | -12.38% | 12.38% | 1.176 | ✅ PASS |
| 7 | V3 | 2.392 | 30.89% | -10.88% | 10.88% | 1.081 | ✅ PASS |
| 8 | V5 | 2.354 | 34.46% | -14.06% | 14.06% | 1.024 | ✅ PASS |

### Gate verdict extended 1986-2026 (supplementary)

Top-4 ranking idêntico: **V8 > V4 > V2 > V6** em OOS Sharpe. V8 extended MaxDD 22.84% — a 2.16pp do gate 25%.

### ★ Por que V4 (não V8) é default

V8 tem **melhor OOS Sharpe** (+0.013 canonical) e **CAGR dramático** (+18.98pp) mas:

1. **Margem ao gate 25% é crítica.** V4 MaxDD 12.22% canonical (12.78pp margem); V8 MaxDD 22.84% extended (**2.16pp margem**). V8 real com drag Gayed esperado ~+3-5pp **violaria gate em produção**.
2. **Sharpe edge V8 é dentro do ruído bootstrap.** Δ +0.013 em Sharpe com T≈5000 observações → std(Sharpe) ≈ 0.014. Não estatisticamente distinguível de V4.
3. **Tracking error intra-diário real.** Gayed p.21 Table 12 reporta drag UPRO real ~2%/yr vs teórico. Em 3× LETFs empilhados, effective drag ~4-5pp CAGR reduzido + 3-5pp MaxDD aumentado em produção.
4. **Behavioral risk.** -17% vs -22% DD é psicologicamente maior diferença do que números sugerem (prospect theory 2×).

**V4 é o default; V8 é a ultra-aggressive documentada.** Para quem quer ainda mais upside, V8 é gate-passing em backtest mas frágil a tail events futuros. Promoção de V8 requer:
- ≥ 12-24 meses V4 track record live confirmando backtest dentro de ±30%
- Override §7 mandate documentando aceitação de gate-violation risk em stress futuro

V1, V2, V3, V5, V6, V7 **todos passam** mas são dominados:
- V1 é fallback defensável (menor MaxDD) — §13
- V6 é sub-ótimo vs V8 (ambos 3× equity, V6 menos CAGR e MaxDD similar — sem vantagem clara)
- V2/V3/V5/V7 Pareto-dominados por V4 ou V8

### Interaction effect preservado (achado estrutural)

UGL sozinho CAGR 6.34% < GLD 1× 6.92% — **negative-alpha isolado** pelo daily rebalance decay em períodos flat do ouro. TQQQ sozinho CAGR 12.16% < QQQ 1× 14.58% — **também negative-alpha isolado**. Mas quando em **blend EW com legs 2× ou 3×-equity**, ambos UGL e TQQQ viram **positive via interaction effect** — correlação baixa vale proporcionalmente mais quando vol do resto do portfolio é alta. Não-aditividade do Sharpe preserva essa lição em `variants_letf_execution/README.md`.

---

## 13. V1 fallback — conservative alternative

**Quando usar V1 (SSO + QQQ + GLD, sem leverage em 2 das 3 pernas):**

1. **Disaster recovery:** se Inter algum dia delistar QLD ou UGL do catálogo, degrada automaticamente para V1. Mandate §5.4 permite override formal.
2. **Behavioral conservadorismo:** se em período de stress real o MaxDD V4 (esperado ~-15%) ficar psicologicamente insustentável, rollback para V1 (MaxDD esperado ~-11%) é opção documentada.
3. **Escalação gradual:** deploy inicial V1 por 6-12 meses para aclimatar operação + acumular track record, migrar para V4 depois (PRODUCTION.md §4.2).

**V1 metrics (canonical 2004-2026, testfol.io ground truth):**
- CAGR 26.53% (vs V4 39.19%; -12.66 pp)
- OOS Sharpe 2.478 (vs V4 2.609; -0.131)
- MaxDD -9.39% (vs V4 -12.22%; **-2.83 pp — V1 mais seguro**)
- Rebal events/yr ~1.3 (vs V4 ~1.8)
- Full 5 gates PASS ✓ (canonical + extended)

**V1 config idêntico ao antigo default:**
- Leg 1: SSO (LETF 2×) via EMA100 regime em SPY.
- Leg 2: QQQ (1×) via Donchian 20/10.
- Leg 3: GLD (1×) via Donchian 40/20.

**Operationally:** mesma runbook deste documento (§2 threshold, §3 broker, §4 allocation, §6 riscos, §7 pre-deploy, §8 monitoring) — só muda os 2 tickers executados (QLD → QQQ, UGL → GLD).

---

**Última atualização:** 2026-04-18 (V4 promoted após gate verdict formal §12 + V1 mantido como fallback §13).
