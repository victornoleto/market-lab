# Pre-deployment readiness — Crash-protected LETF candidate

> **Estratégia-alvo**: `EMA_N150_th5_bL3_sL0 + sl30_rec10_cape05`
> (EMA-150 regime filter + 5% threshold + 3× long UPRO + cash on bear,
> with 30% drawdown stop + 10% recovery-trigger re-entry + CAPE-based
> signal that scales position 0.5-1.0 via `pos = 1 − 0.5·CAPE_risk`).
>
> **Decisão**: mandate §1 atual (MAINTENANCE, 100% Plano C) bloqueia
> reativação de slot A/B/D. Este documento lista os blockers para
> destravar live trading — é input para uma decisão do usuário, NÃO uma
> recomendação para ir live.

---

## TL;DR — é pra ir ou não?

**Pela matemática do spec §0: NÃO.** Falha em 3/7 real-data gates.

**Pelo risk-adjusted real-data view (2009-2026)**:
* Candidate CAGR 18.09% vs SPY 14.99% (+3.10 pp real edge)
* Candidate Sharpe 0.68 vs SPY 0.90 — **SPY vence em Sharpe**
* Candidate MDD 43.77% vs SPY 33.70% — **SPY vence em MDD**
* Final equity em 17y: 16.28× vs SPY 10.43× (+56% wealth)

No universo real o candidate é um trade-off: 3 pp/yr extra de CAGR com
pior Sharpe e pior MDD. Para alguém com horizonte >10y que aceita dor
tática em troca de crescimento acumulado maior, faz sentido. Para
alguém sensível a dor intermediária, SPY vence risk-adjusted.

A decisão final é do usuário, mas ela tem que passar por **5 blockers
formais abaixo** antes de envolver dinheiro real.

---

## Os 5 blockers estruturais (go/no-go)

### 🔴 Blocker 1 — Mandate override §7 não assinado

* **Status atual**: Mandate §1 diz "100% Plano C passive factor-tilted;
  Strategy A/B/D = 0% DORMANT". Este candidate é uma reativação de slot
  B (swing LETF rotation, Gayed-anchored).
* **O que falta**: Template em
  `docs/mandate_overrides/2026-04-24-crash-protected-letf-open.md`
  (draft gerado junto com este README). Usuário precisa revisar +
  assinar (editar status para `**Signed**`).
* **Gate de desbloqueio**: até o arquivo de override existir com status
  Signed, qualquer código de live trading viola o mandate assinado.

### 🔴 Blocker 2 — Spec §0 gates não cumpridos em real data

* **Status atual**: Candidate passa **6/7 no educational synth** mas
  **3/7 em SPY real** e **4/7 em NDX real**. Spec §0 exige ≥ 5/7 synth
  E ≥ 4/7 real AND ≥ 4/7 ndx simultâneos.
* **Gates que falham em real data** (ver
  `phase3/cross_dataset_gates.md`):
  - G1 PBO grid-level: 0.78 no SPY real (>> 0.5 threshold)
  - G2 DSR com n_trials=4020: p-value > 0.05 universal no real
  - G3 Walk-Forward 6/8 MDD<25%: FAIL universal (synth e real)
* **Opções do usuário**:
  - (A) Override formal do mandate §5 aceitando gate-waiving
  - (B) Tentar Phase 3.5 do spec: re-calibrar combinação com mais bases
  - (C) Aceitar resultado negativo e fechar
* **Honesto**: G3 WF falha porque a estratégia não mantém MDD<25% em
  janelas OOS de 6 meses durante crashes. Essa gate foi definida pelo
  mandate §5 exatamente para bloquear estratégias com DD alto intermed.
  Ir live com G3 falhando é exatamente o cenário que o mandate preveniu.

### 🟡 Blocker 3 — Synth → real degradação confirmada (-3.4 pp CAGR)

* **Status atual**: Testado em 2009-2026 real UPRO vs sintético mesma
  janela. CAGR cai 21.49% → 18.09% (−3.40 pp). MDD piora 40.43% → 43.77%
  (+3.34 pp). Exatamente dentro do range previsto por Gayed
  `[leverage_for_the_long_run, p.21, Table 12]` (2-3 pp de drag).
* **Implicação**: Todos os plots de 40y synth devem ser lidos com −3 pp
  mental offset para estimar real. O CAGR 24% do synth 40y vira ~21%
  real; o MDD 44% vira ~47%; etc.
* **Não é bloqueante**, mas é essencial comunicar honestamente para
  expectativas.

### 🟡 Blocker 4 — CAPE pipeline estoicamente stale

* **Status atual**: Fonte atual é Shiller `ie_data.xls` (Yale), última
  atualização 2023-09. Para live trading pós-2024 o CAPE signal
  degrada para constante — overlay reduz a stop-loss only.
* **O que falta para live**:
  - (A) Pipeline automatizado para refresh CAPE mensal (scrape multpl.com
    ou baixar Shiller updated — ver spec §4.2 mention of ALFRED for
    vintage data).
  - (B) Aceitar que signal degrada para stop-only pós-2024 (realistic
    pois Phase 3 mostrou que a redução de MDD no top-1 vem mais do
    stop do que do CAPE).
* **Recomendação técnica**: Opção B é mais robusta — implementar
  primeiro stop-only, validar em paper trading, depois adicionar CAPE
  se valer a pena.

### 🟡 Blocker 5 — Phase 4 paper trading não executado

* **Status atual**: Spec §5.4 pede real-data validation em SPY/NDX com
  análises de rolling + worst-case + portfolio 50/50. Phase 4 nunca
  rodou porque Phase 3 não passou nas gates.
* **O que falta para live** (minimum viable):
  - 3-6 meses de paper trading via `scripts/paper_trading/` com
    broker scraping simulado
  - Logs de signal/stop/re-entry por dia
  - Comparação paper-equity vs backtest-equity (deve cruzar ±5%)
  - Cost model real (IBKR/Inter fees + spread + swap ou tax)
* **Reason**: backtest assume execução no close sem slippage.
  Real-time, ordens de stop disparam com gap se mercado abrir −3%.
  Circuit breakers podem impedir execução em crash dias. Spec §8.4.

---

## Outros itens operacionais (não blockers mas requisitos)

### ⚠️ Position sizing + capital allocation

* **Mandate §3** (pré-maintenance): Plano A permitido USD 500-1k staging,
  cap USD 5-10k Tier-3 SCB Bahamas. Para este candidate (swing LETF
  rotation, not short-hold CFD), aplicam-se regras Plano B: Inter
  Internacional, DARF 15%, T+1 settlement.
* **Question**: qual fração do capital vai para este candidate?
  Recomendação inicial conservadora: 5-10% do capital total alocado ao
  Plano B slot, o restante fica em Plano C passivo.

### ⚠️ Tax / DARF BR

* **Modelo atual**: `cfg.tax_rate = 0.0` nos backtests (pure view).
  Para live BR precisa modelar DARF 15% swing exit. Em backtest já
  rodei `tax15` (top-1 baseline ΔCAGR -2.64 pp por tax drag) — esperar
  algo similar no candidate.
* **Isenção R$20k/mês**: candidate tem baixa turnover (regime switches
  raros, stops raros). Provavelmente a maioria dos exits cai abaixo do
  limite de isenção. Mas PRECISA modelar explicitamente antes de live.

### ⚠️ Stop execução mecânica

* **Backtest assumption**: stop dispara no close do dia quando
  `equity/peak − 1 ≤ −30%`. Execução: vender UPRO no close.
* **Reality check** (spec §8.4):
  - Crashes rápidos (COVID-style) podem ter gap-down de 10-15% no open
    — stop efetivo dispara em DD 35-45%, não 30%
  - Circuit breakers level-1/2/3 param negociação; dia 1 você pode não
    conseguir executar
  - Broker scraping não é instantâneo; stop dispara em T+0 mas execução
    pode ser T+1 com spread desfavorável
* **Implicação**: real MDD vai ser 3-5 pp pior que backtest. Já
  contabilizado no real-data test mas merece comunicação clara.

### ⚠️ Broker execução path

* **Mandate §4** (pré-maintenance): Plano B usa Banco Inter Internacional
  (Inter&Co Securities FINRA). UPRO está no catálogo confirmado
  (memory: `project_plano_b_broker_inter`).
* **Ordem flow**:
  - Sinal calculado em T+0 após SPY close (UTC -5, ~17:00 EST)
  - Execução possível em T+1 pre-market ou open
  - Settlement T+1 (Inter)
  - Portanto: backtest "execute no close" vs real "execute T+1 open"
    introduz 1-2 pp/yr de slippage extra (over 10y ≈ 10-20% wealth)
* **Recomendação**: modelar essa slippage em cost model antes de live.

### ⚠️ Monitoring + alerta

* Stop triggers são raros (1 a cada ~4 anos). Usuário precisa de alerta
  confiável quando stop dispara para executar no T+1.
* **Infra necessária**:
  - Daily job que calcula signal + position target
  - Alerta (email/push) quando regime muda ou stop dispara
  - Dashboard com equity real vs backtest expected

---

## Expected returns — realistic scenarios

Assumindo que o usuário assina override e deploya com capital X:

| scenario | CAGR líquido (após DARF + slippage) | MDD esperado | wealth em 10y |
|---|---|---|---|
| **Otimista** (synth floor, no degradation) | ~21 % | ~45 % | 6.7× |
| **Realistic** (real-data extrapolated + 0.5 pp slippage) | ~17 % | ~48 % | 4.8× |
| **Pessimista** (sampling 2015-2020 style regime) | ~8 % | ~55 % | 2.2× |
| **SPY buy-hold benchmark** | ~10 % líquido | ~35 % | 2.6× |

**Leitura honesta**: realistic scenario dá ~70% mais wealth que SPY em
10y, a custo de +13 pp a mais de MDD esperado. Pessimistic scenario
(entrada em 2015-2020-equivalente) dá 15% MENOS wealth que SPY — esse
é o risco real.

---

## Decisão do usuário — 3 paths

### Path A — deploy com staging (requer blocker 1+2 resolvidos)

1. Assinar `docs/mandate_overrides/2026-04-24-crash-protected-letf-open.md`
2. Aceitar formalmente gate-waiving 3/7 em SPY real (or require
   resolution primeiro)
3. Configurar paper trading em `scripts/paper_trading/` por 3-6 meses
4. Se paper ok, deploy gradual: USD 500 → 1k → 3k → 10k se sinais
   saudáveis
5. Stop-loss pré-comprometido: se equity drawdown > 35% real (vs 30%
   backtest), fechar slot

### Path B — fix gaps primeiro (recomendado)

1. Investigar por que G3 Walk-Forward falha (diagnóstico, não waive)
2. Reproduzir Phase 2 com top-100 bases por dataset (não só top-20) —
   talvez existam combinações mais robustas em real data que top-20
   missed
3. Adicionar data nova: Tiingo updates pós-2024 para CAPE/EBP
4. Re-run Phase 3 com gates completos incluindo real data
5. Se algum combo passa spec §0 → Path A. Se não → Path C.

### Path C — aceitar resultado negativo, manter MAINTENANCE

1. Mandate §1 continua 100% Plano C
2. Este estudo fica arquivado como material educacional
3. Revisão programada: 6-12 meses (2026-10 / 2027-04)
4. Nenhuma mudança operacional

---

## O que eu (Claude) posso construir sem override

Sem blocker 1 resolvido eu NÃO vou construir:

- Código de live trading / broker integration
- Scheduled jobs que geram ordens reais
- Alertas configurados para dinheiro real

Posso construir (útil independente do caminho):

- **Paper trading scaffold** (mock orders, real data, track deviations)
- **Refresh pipeline para CAPE** (scrape multpl, save parquet vintage)
- **Diagnostic script para G3 WF** (entender qual janela falha e porque)
- **Cost model detalhado** (DARF + slippage + spread Inter)
- **Monitor/alert rascunho** (daily signal compute, slack/email trigger)

Qualquer dessas 5, pede que eu construa. Mas antes preciso saber qual
path você escolhe.

---

## Arquivos gerados nesta revisão

```
studies/ema_sma_threshold_crash_protected/
├── PRE_DEPLOYMENT_README.md           # este documento
├── analysis_top_candidate/             # Phase 3 top review (já existia)
├── deep_review/
│   ├── deep_review_report.md          # rolling windows + win rate vs SPY
│   ├── rolling_cagr_{1y,3y,5y,10y}.png
│   ├── rolling_sharpe_{1y,3y,5y,10y}.png
│   ├── rolling_mdd_{1y,3y,5y}.png
│   ├── rolling_excess_vs_spy.png       # excess CAGR por janela
│   ├── calendar_year_returns.png
│   ├── entry_year_sensitivity.png
│   ├── underwater.png
│   ├── real_vs_synth_equity.png        # real UPRO vs synth 2009-2026
│   ├── real_vs_synth_drawdown.png
│   ├── real_gap_report.md              # quantificação do synth→real drag
│   ├── win_rate_by_window.csv
│   ├── entry_year_sensitivity.csv
│   ├── calendar_year_returns.csv
│   ├── worst_windows.csv
│   └── real_gap_metrics.csv
└── ../../docs/mandate_overrides/
    └── 2026-04-24-crash-protected-letf-open.md  # template p/ assinar
```

---

## Citações

* Gayed synth→real drag `[leverage_for_the_long_run, p.21, Table 12]`
* Honest alignment `[advances_fin_ml, p.31-34]`
* Gates: PBO `[p.208-211]`, DSR `[p.222-223]`, WF `[ch.12]`,
  Bootstrap `[p.196-202]`
* Spec §0, §5.3, §5.4, §6.1, §6.2, §8.1-8.4 de
  `studies/SPEC_crash_protection_evolution.md`
* Mandate §1, §5, §7 de `docs/investment-mandate.md`
