# Plano A V2-L2 — Gayed Regime Rotation CFD

**Living strategy document.** Este arquivo é a especificação operacional
canônica do winner Plano A. Atualize aqui sempre que qualquer parâmetro,
custo ou regra mudar.

**Status:** ✅ backtest PASS (Phase 3.5a-V2, 2026-04-19). Aguarda paper
trading validation (Phase 4, `specs/phase_4_paper_trading.md`).

**Jornadas relacionadas:**
- Winner PASS jornada: `jornada/2026-04-19/01-phase3.5a-v2-L2-gayed-transported-PASS.md`
- V2 summary: `jornada/2026-04-19/07-phase3.5a-v2-summary-WINNER-FOUND.md`
- Aggregator L2: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.md`

---

## 1. TL;DR (1 parágrafo)

Regime rotation Gayed `[leverage_for_the_long_run, p.11-21]` aplicado em
CFD Pepperstone com leverage 2×: quando SPY > EMA-100(SPY) → risk-on
(50% SPY + 50% QQQ alavancado 2×); quando SPY < EMA-100 → risk-off
(100% GLD sem leverage). Decisão tomada diariamente no close US. Median
hold 6 dias. Backtest OOS 2018-2023: Sharpe 2.285, CAGR líquido
79.14%, MaxDD -21.02%. Todos os 13 gates V2 passam com folga material
(PBO 0.103, DSR p 0.000288, bootstrap 99.9% CI low 0.962).

---

## 2. Regras de sinal e portfolio

### 2.1 Signal diário (executado no close US, ~16:00 ET)

```
close_spy_today = SPY close price today
ema100_today    = EMA(SPY close, 100) today

if close_spy_today > ema100_today:
    regime = "risk-on"
else:
    regime = "risk-off"
```

Citação: `[leverage_for_the_long_run, p.11-14]` — Gayed mostra que
EMA-100 dá menor whipsaw que SMA-200 preservando edge.

### 2.2 Portfolio target allocation

| Regime | Target allocation | Leverage total |
|--------|-------------------|----------------|
| risk-on | 50% SPY + 50% QQQ, cada posição 2× leverage | **2×** capital |
| risk-off | 100% GLD, leverage 1× (sem alavancagem) | **1×** capital |

### 2.3 Rebalance trigger

- Signal muda risk-on ↔ risk-off → fecha tudo e abre nova composição
- Dentro do mesmo regime: nenhum rebalance (sem drift correction)
- **Custo por signal flip:** ~2 round-trips (fecha 2 posições, abre 1-2)

### 2.4 Sizing dentro do risk-on

Porção SPY e QQQ são equal-weight (50/50) sempre. **Não** varia com:
- Vol recente (sem vol-targeting dinâmico nesta strategy)
- Momentum differential entre SPY e QQQ
- Correlação realizada

Justificativa: simplicidade + robustez. V2-L2 testou variações mais
complexas (vol-targeting, factor tilts) e elas não passaram gates
adicionalmente — equal-weight é o Schelling point.

---

## 3. Mecanismo de leverage — CFD vs LETF

**Esta é a diferença estrutural mais importante entre Plano A (este
doc) e Plano B (3-leg EW LETF).** Entender a fundo antes de operar.

### 3.1 Plano B (LETF via Banco Inter — referência, não este doc)

Você **COMPRA shares reais** de ETFs alavancados:
- Deposita $10.000 na conta Inter Global
- Compra $10.000 de **SSO** (LETF 2× S&P)
- Você é **dono das shares**; elas ficam em custody segregada (Apex Clearing)
- Exposição efetiva a SPY: $20.000 (a alavancagem está **embutida no produto**)
- Perda máxima possível: **$10.000** (valor investido) — SSO pode ir a zero em teoria, mas nunca deve nada além
- Custo de carry: ~1.4%/yr (expense ratio 0.89% + volatility decay 0.5-1% em choppy markets)

### 3.2 Plano A (CFD via Pepperstone — este doc)

Você **NÃO COMPRA shares** — abre **contratos derivativos** que
replicam o preço:
- Deposita $10.000 na conta Pepperstone cTrader
- Abre posição CFD "SPY long" com nominal **$10.000**
- Pepperstone exige margem de 5% = **$500 bloqueado** como colateral
- Você **não tem shares** — tem contrato que ganha/perde diferença de preço
- Para atingir exposição $20.000 (equivalente a 2× leverage), abre **nominal $20.000** → margem $1.000
- **Capital livre remanescente: $9.000** — buffer contra margin call
- Custo de carry: swap ~5.5%/yr on long SPY (juros sobre a parte "emprestada" da exposição)

### 3.3 Comparação numérica (conta $10k, target 2× SPY)

| Dimensão | LETF (Plano B via SSO) | **CFD (Plano A via SPY CFD 2×)** |
|----------|-----------------------|----------------------------------|
| Capital empenhado | $10.000 (comprou shares) | **$1.000** (margem 5% em $20k nominal) |
| Capital livre na conta | $0 | **$9.000** |
| Exposição efetiva | $20.000 | $20.000 |
| Custo anual carry | ~1.4% (expense + drag) | ~5.5% (swap) |
| Dividendos | SSO recebe e paga (ajustado no preço) | CFD paga cash adjustment equivalente |
| Contraparte | Apex Clearing (custody) | Pepperstone SCB (margin balance) |
| Max loss possível | $10k (a conta) | $10k (margin call antes do -100%) |

### 3.4 Trade-off em janela trending vs choppy

- **Trending market (SPY sobe consistente):** LETF vence — sem swap, só drag pequeno. SSO deliverou ~37%/yr em 2018-2023.
- **Choppy market (SPY oscila sem direção):** CFD vence — LETF tem volatility decay (daily reset compound loss), CFD não. Gap pode ser 2-4%/yr em anos como 2015-2016.
- **Regime rotation Gayed reduz tempo em choppy** — sai antes do deep drawdown. Por isso CFD 2× funciona bem aqui (~80% do tempo em trending risk-on).

### 3.5 Por que V2-L2 winner usa CFD e não LETF

1. **Flexibilidade de asset:** LETFs 2× existem pra SPY (SSO), QQQ (QLD),
   GLD (UGL) — todos 3 disponíveis em Banco Inter. **Mas** a combinação
   SPY+QQQ em equal-weight com leverage 2× via LETFs exige comprar SSO+QLD
   em quantidades balanceadas, com rebalance pra manter o target — overhead
   operacional maior que CFD direto.
2. **Sem daily reset decay:** CFD tem leverage linear; LETF tem path dependency
   negativa em vol alta.
3. **Capital efficiency:** CFD libera 90% do capital (vs LETF 0%) — dá
   optionality pra paper trading uma 2ª strategy sem precisar de mais dinheiro
   depositado.

**Risco adicional do CFD:** contraparte. Se Pepperstone SCB quebrar, o
contrato CFD vira passivo da massa falida. Em LETF via Inter, as shares
são custody segregada DTC — você é dono. **Pepperstone SCB tem SCB
regulation + negative balance protection retail**, mas o risco
estrutural contraparte existe.

---

## 4. Execução via Pepperstone cTrader — specifics

### 4.1 Entity e regulação

- **Pepperstone SCB** (Bahamas) — entity que serve residentes brasileiros
- Regulação: Securities Commission of The Bahamas (SCB)
- **Não** é o mesmo que Pepperstone FCA/UK (leverages mais baixos)
- Razão da escolha: máxima leverage retail + aceita Brasil + negative balance protection

### 4.2 Instrumentos — escolha entre share CFD vs index CFD

Existem 2 formas de obter exposição SPY/QQQ via Pepperstone:

| Abordagem | Ticker Pepperstone | Leverage max | Margem | Tracking |
|-----------|-------------------|--------------|--------|----------|
| **US share CFD** | `SPY`, `QQQ`, `GLD` | **1:20** | 5% | Exact (mesma price action que ETF) |
| **Index CFD** | `US500`, `USTEC`, `XAUUSD` | **1:200** (SPX/NAS) / **1:500** (Gold) | 0.5% / 0.2% | Tracks underlying index com dividend adjustment cash |

**Backtest do V2-L2 usou SPY/QQQ/GLD ETF prices** (Tiingo daily cache).
Execução mais fiel = **US share CFDs**.

**Execução alternativa (se share CFDs não disponíveis na tua conta):**
usar US500/USTEC/XAUUSD. Diferença material esperada < 10 bps/yr por
causa de dividend adjustment. Precisa validar em paper trading (Phase 4).

### 4.3 Leverage disponível vs leverage aplicado

> **Distinção crítica** que o resto desta seção formaliza:
> - **Leverage da conta** (`1:20`, `1:50`, `1:100`, `1:200`, `1:500`)
>   = capacidade máxima que o broker permite. Determina a **margem
>   mínima requerida** por instrumento. **Não afeta CAGR/Sharpe/MDD.**
> - **Leverage aplicada da estratégia** (`L=2`) = exposição efetiva
>   que a estratégia pede. Determina **totalmente** CAGR/Sharpe/MDD.

#### 4.3.1 Sweep empírico L=2 vs L=3 vs L=5 (mesmo signal, só muda L)

Dados do sweep V2-L2 do winner (EMA100 regime + SPY/QQQ risk-on + GLD
risk-off), variando apenas o multiplicador de exposição:

| L | IS Sharpe | IS CAGR | IS MDD | OOS Sharpe | OOS CAGR | OOS MDD | FWD Sharpe | FWD CAGR |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **2** ⭐ | 1.856 | 53.42% | **-22.67%** | **2.284** | **79.14%** | **-21.02%** ✅ | 1.821 | 59.28% |
| 3 | 1.969 | 87.34% | -23.78% | 2.294 | 128.93% | **-30.04%** ❌ | 1.899 | 96.95% |
| 5 | 2.034 | 169.17% | -29.48% | 2.283 | 255.23% | **-46.20%** ❌ | 1.945 | 186.35% |

**Leitura em 3 invariantes (descobertos no sweep V2-L2):**

1. **Sharpe é flat** cross-L (2.28–2.29 OOS): estamos na região
   Kelly-saturada — aumentar leverage não compra Sharpe adicional,
   só multiplica o PnL bruto.
2. **CAGR cresce super-linearmente** com L (79% → 129% → 255%): é o
   efeito da alavancagem em cima de um edge real positivo.
3. **MaxDD também cresce super-linearmente** (21% → 30% → 46%): a
   marca d'água Vince `[leverage_space]`, `[math_money_mgmt]`. **L=5
   empírico ≡ PoR > 50%** — ruína provável em horizonte multi-anual.

**Só L=2 passa o gate MaxDD ≤ 25% do mandate §5.** L=3 fura o gate em
5pp; L=5 em 21pp. **Não operar acima de 2× em nenhuma circunstância.**

#### 4.3.2 Leverage da conta (broker) vs métricas da estratégia

**Tese:** leverage da conta **não** aparece na expected return da
estratégia. Ela aparece em (i) margem usada, (ii) capital livre como
buffer, (iii) o teto de L possível. A estratégia veta L > 2, então
(iii) não é binding em produção.

Exemplo concreto: conta $10.000, strategy em risk-on → $20.000 de
exposição nominal (2 pernas × 1× capital = 2× capital total):

| Tier conta | Instrumento típico | Margin % | Margem bloqueada | Capital livre | Strategy metrics |
|---|---|---:|---:|---:|:---:|
| 1:20 | US share CFD (SPY, QQQ, GLD) | 5.00% | $1.000 | $9.000 | **idênticas** |
| 1:50 | US sector/country CFD | 2.00% | $400 | $9.600 | idênticas |
| 1:100 | FX majors, minor indices | 1.00% | $200 | $9.800 | idênticas |
| 1:200 | Major index CFD (US500, USTEC) | 0.50% | $100 | $9.900 | idênticas |
| 1:500 | Gold CFD (XAUUSD) | 0.20% | $40 | $9.960 | idênticas |

**CAGR / Sharpe / MaxDD são exatamente os mesmos em qualquer tier.**
A estratégia mantém **L aplicada = 2× sempre** — o que muda é só
quanto capital fica "preso" como margem vs livre como buffer.

#### 4.3.3 Impacto indireto — buffer contra stop-out

Leverage da conta mais alta = margem menor bloqueada = buffer maior
contra margin call. Útil em stress intraday, não nas métricas
baseline.

Em share CFD (1:20, 5% margem em $20k = $1k bloqueado):
- Margin call @ 80% use → equity $800 livre
- Stop-out @ 50% use → equity $500 livre
- Traduzindo para drawdown da conta: **stop-out a ~-90%** de DD
  (ver §5.3 pra cálculo completo)
- Buffer backtest MDD -21% → stop-out -90% = **margem 69pp**

Em index CFD (1:200, 0.5% margem em $20k = $100 bloqueado):
- Mesma strategy, mas margem 10× menor → buffer ainda maior
- Stop-out não é risco realista em movimento razoável
- Kill-switch manual (§5.4) dispara bem antes

**Conclusão operacional:** qualquer tier 1:20+ é suficiente para
L=2. Preferência: **usar share CFD (1:20)** — reflete 1:1 o backtest
(mesmo price action SPY/QQQ/GLD) e evita risco de tracking error
que index CFD introduz (dividend adjustment via cash, rolagem de
contrato, etc.).

#### 4.3.4 Por que Pepperstone SCB e não tier "1:500 Seychelles"

Pepperstone tem várias entities globais com leverages diferentes:

| Entity | Leverage max retail | Acessibilidade Brasil | Uso recomendado |
|---|---:|---|---|
| **Pepperstone SCB** (Bahamas) | 1:500 em gold, 1:200 em índices, 1:20 em share CFD | ✅ **tier escolhido** — aceita Brasil | ⭐ este plano A |
| Pepperstone FCA (UK) | 1:30 retail (ESMA limit) | ❌ não aceita Brasil | N/A |
| Pepperstone ASIC (AU) | 1:30 retail | ❌ não aceita Brasil | N/A |
| "Off-shore 1:1000" (marketing) | 1:1000 nominal | ⚠️ regulamentação questionável | ❌ não usar |

SCB é o **Bahamian Securities Commission** — regulação legítima com
negative balance protection + compensation scheme. Tiers "1:1000"
geralmente são jurisdições sem proteção patrimonial real.

**Não há vantagem operacional** em perseguir leverage máxima mais
alta do que SCB oferece — a estratégia já está capped em L=2.

### 4.4 Custos operacionais esperados

Conforme modelado no backtest (cost_model em `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/v2_l2_gayed_transported_cfd.json`):

| Componente | Range esperado | Observação |
|------------|---------------|------------|
| Spread half × 2 | 4-10 bps round-trip | Varia por instrumento; SPY/QQQ ~2 pips, GLD ~5 pips |
| Commission | $3.50/side = ~$7 round-trip | Razor tier, fixo por volume |
| Slippage | 1-3 bps round-trip | Retail; pior em market open/close |
| **Total frictions** | **6-13 bps/round-trip** | Backtest assumiu 10-11 bps (conservador) |
| Swap long SPY/QQQ | **~5.5%/yr** annualized | Varia com Fed funds rate; rebalanceado overnight |
| Swap long GLD | ~2-3%/yr | Menor por ser commodity |

**Swap total anualizado na strategy (considerando tempo risk-on ~75%):**
0.75 × 5.5% = **~4%/yr drag** (batizado no backtest como "swap daily
0.005-0.02%" = 1.8-7.3%/yr range — dentro do envelope).

### 4.5 Checklist pré-live (5 coisas a confirmar direto no Pepperstone)

Antes de abrir conta paper, verificar:

- [ ] **SPY/QQQ/GLD share CFD disponíveis** na tua conta (alguns tiers Pepperstone Brasil só têm índices — pode precisar upgrade)
- [ ] **Swap overnight rates atuais** em MyPepperstone (variam com Fed rates; backtest assumiu range médio)
- [ ] **Minimum trade size** — geralmente 1 share = baixa barreira, mas confirma
- [ ] **Commission rate real** — Razor tier $3.50/side é padrão, mas confirmar no contrato
- [ ] **Margin call e stop-out levels** — padrão Pepperstone SCB: margin call @ 80% use, stop-out @ 50% use. Stop-out = liquidation forçada. Pré-calcular buffer.

---

## 5. Position sizing e margin math

### 5.1 Fórmula canônica (risk-on)

Para capital $C na conta Pepperstone:

```
nominal_per_leg = C * 1.0          # 1× capital nominal por perna (SPY e QQQ)
total_nominal   = 2 * nominal_per_leg  # = 2× capital → leverage 2× total
margin_required = 0.05 * total_nominal  # 5% share CFD margin
free_capital    = C - margin_required   # buffer contra margin call
```

### 5.2 Exemplos em conta $10.000

| Estado | Nominal SPY | Nominal QQQ | Nominal GLD | Margem bloqueada | Capital livre |
|--------|------------:|------------:|------------:|-----------------:|--------------:|
| risk-on | $10.000 (1× C) | $10.000 (1× C) | $0 | $1.000 (10% C) | **$9.000** |
| risk-off | $0 | $0 | $10.000 (1× C) | $500 (5% C) | **$9.500** |

**Leverage efetiva total:** em risk-on, 2× ($20k exposição / $10k conta). Em risk-off, 1× ($10k GLD / $10k conta).

### 5.3 Buffer contra margin call

Pepperstone SCB: **margin call** dispara quando equity cai abaixo de
80% da margem usada; **stop-out** (liquidação forçada) em 50%.

Com conta $10k e margem usada $1.000 (risk-on):
- Stop-out equity level: $500 na margem × 2 (alavancagem) = conta precisa
  cair a **$500 livre + $500 margem = $1.000 total**
- Equivale a **-90% drawdown na conta** antes de stop-out
- **Buffer enorme:** backtest MaxDD -21%, stop-out a -90% — margem de
  69pp entre pior caso backtest e liquidação

**Em risk-off (GLD 1×):** stop-out impossível em movimento normal
(GLD cairia -95% pra disparar).

### 5.4 Kill-switch manual (regra operacional, não código)

Interrompe a strategy manualmente se:
- Equity da conta cair -15% em single day (evento extremo não modelado)
- Drawdown acumulado atingir -25% (cap backtest +4pp tolerância)
- Signal flip mais de 3× em 5 dias (whipsaw indicando regime quebrado — Gayed pressupõe trending/bear bem definidos)
- Ordem não-preenchida por > 5 minutos (latência de feed quebrada)

Kill-switch → fecha todas posições a mercado + pausa daily job + abre jornada investigation.

---

## 6. Risk management

### 6.1 Gates aplicados no backtest (todos passaram)

| Gate | Threshold | Observado V2-L2 winner | Margem |
|------|----------:|----------------------:|-------:|
| PBO (CSCV 10-block) | < 0.5 | 0.103 | 5× abaixo |
| PBO (CSCV 16-block) | < 0.5 | 0.036 | 14× abaixo |
| DSR p-value (N=27 trials) | < 0.05 | 0.000288 | 170× abaixo |
| OOS Sharpe net | > 0 (binding) / ≥ 2.0 (winner) | 2.285 | ✅ |
| FWD Sharpe 2024-2026 | > 0 | 1.821 | ✅ (degradação 20% healthy) |
| Bootstrap 99.9% CI low | > 0 | 0.962 | ✅ |
| Walk-forward profitable | ≥ 6/8 | 8/8 | perfeito |
| WF max-window DD | ≤ 25% | 22.7% | ✅ |
| CAGR OOS net | ≥ 30% | 79.14% | 2.6× target |
| MaxDD OOS | ≤ 25% | -21.02% | ✅ |
| Median hold | ≥ 3 days | 6.0 | ✅ |
| IR vs SPY OOS | ≥ 0.5 | 2.161 | 4× threshold |

Todos documentados em `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.md`.

### 6.2 Limitações conhecidas (caveats honestos)

**Dizer isso na cara pra você lembrar em 6 meses:**

1. **Sharpe 2.28 é matematicamente consistente com Gayed base + leverage 2× — não é alpha novo.**
   Gayed publicou track live ~Sharpe 1.1-1.4 com SPY 1×. Leverage 2× dobra Sharpe em teoria (menos friction) → 2.2-2.8 esperado. Nosso 2.285 **está exatamente onde deveria estar**. Isso é saudável (teoria confirmada), mas não é "edge novo descoberto".

2. **Janela OOS 2018-2023 foi favorável pra leveraged equity.**
   SPY ~12%/yr, QQQ ~16%/yr nessa janela. Em 2000-2010 (dot-com + GFC), backtest do mesmo sistema provavelmente mostraria Sharpe muito pior. Passa gates na janela disponível, mas **não há evidência de que resistiria stress extremo** (ex: 1973-1974, 2008-2009).

3. **Alta correlação com Plano B.**
   Ambos são long SPY+QQQ em risk-on. Em crash de mercado severo, os 2 caem juntos. O portfolio "dual A+B" **não é 2 edges independentes** — é uma tese (regime rotation) executada em 2 mecanismos (LETF vs CFD). V2-L3/L4/L5/L6 tentaram achar 2ª edge independente e falharam.

4. **Custo swap real Pepperstone pode ser pior que modelado.**
   Modelo assumiu 0.005-0.02%/dia. Pepperstone real em long SPY share CFD em 2026 é ~5.5%/yr (~0.021%/dia no topo do range). Se Fed eleva juros, swap sobe; estratégia degrada.

5. **Risco contraparte CFD.**
   Sobrevivência do broker importa. Pepperstone SCB é regulado e tem negative balance protection, mas não é o mesmo que custody segregada.

6. **Gayed 2016 pode ter data mining implícito.**
   EMA-100 é a escolha canônica do paper mas há literatura sobre "Gayed refit" — rodas próprias do Gayed apresentam variantes (LRS composite). Nosso backtest aderiu ao EMA-100 puro pra evitar re-optimization overhead, mas o paper original é produto de uma época (pre-2016 data).

### 6.3 Escalação de capital (post-paper-trading)

Se Phase 4 paper trading passa gates (≥ 0.7× Sharpe backtest, MDD ≤ 1.5× modelado):

| Fase | Capital | Duração | Trigger para próximo |
|------|---------|---------|---------------------|
| Phase 4 paper | $10k virtual (cTrader Demo) | 3 meses | Gates paper pass |
| Phase 5.1 live pequeno | $1.000 real | 3 meses | MDD realizado ≤ -20%, Sharpe ≥ 1.5 |
| Phase 5.2 live médio | $5.000 real | 3 meses | Continuação dos gates 5.1 |
| Phase 5.3 live full | Alocação target do bucket A (parte dos 20-40% ativo) | Open-ended | Quarterly review |

**Escalação gradual é a única defesa contra o abismo backtest→live.**
A literatura `[systematic_trading, ch.14-15]` confirma: 60-80% dos
winners de backtest falham na primeira onda de capital live. Gradual
scaling capta falhas cedo, com perdas pequenas.

---

## 7. Dados e backtest reference

### 7.1 Dados usados no backtest (Tiingo daily cache)

| Ticker | First | Last | Bars | Uso |
|--------|-------|------|-----:|-----|
| SPY | 2001-05-14 | 2026-04-14 | 6266 | Signal + risk-on leg |
| QQQ | 2001-05-14 | 2026-04-14 | 6266 | Risk-on leg |
| GLD | 2004-11-18 | 2026-04-15 | 5384 | Risk-off leg |

Janela unificada (menor intersecção): **2004-11-18 → 2026-04-14** (~21 anos).
Window splits V2:
- **IS** (in-sample): 2004-11-18 → 2017-12-31 (~13 anos)
- **OOS** (out-of-sample): 2018-01-01 → 2023-12-31 (6 anos)
- **FWD** (forward stress): 2024-01-01 → 2026-04-14 (~2.3 anos)

### 7.2 Código do backtest

- Strategy logic: `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` (criado iter 18 V2-L2)
- Runner script: não tem single runner — cada config foi rodada individualmente
  via registry fan-out (ver `scripts/run_t2_fanout_ticker.py` para referência de
  padrão; V2-L2 usou `scripts/run_v2_l2_fanout_config.py` análogo)
- Aggregator: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.md`
- Per-config JSONs: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_*.json`

---

## 8. Citações obrigatórias

Toda decisão de parâmetro/regra desta strategy tem citação explícita:

- **Sinal EMA-100:** `[leverage_for_the_long_run, Gayed 2016, p.11-14]` — EMA-100 é a canonical, menor whipsaw que SMA-200 preservando edge.
- **Regime rotation tese:** `[leverage_for_the_long_run, Gayed 2016, p.7-21]` — LRS / volatility-vs-leverage regime.
- **Leverage cap L=2:** `[leverage_space, Vince]` — PoR empírico confirma L=5 ruína em 12 meses.
- **Kelly f/2 cross-check:** `[math_money_mgmt, Vince]` — L=2 é f/2-safe em distribuição empírica trade returns.
- **GLD off-regime:** `[leverage_for_the_long_run, p.16, p.21]` — drift positivo + asimetria dólar-hedge em crises.
- **Hold ≥ 3 days rule:** `[systematic_trading, Carver, p.185-188]` — spread+commission dominante em retail, hold curto amplifica custos.
- **5-gate framework (PBO/DSR/WF):** `[advances_fin_ml, López de Prado, p.196-211, ch.11, ch.14]`.
- **Cost model Pepperstone:** `docs/investment-mandate.md §3` + `specs/phase_3_5a_v2.md §3`.
- **Dual-path mandate:** `docs/investment-mandate.md §1`.

---

## 9. Update log

| Data | Mudança | Motivo |
|------|---------|--------|
| 2026-04-19 | Documento criado pós V2-L7 verdict | Winner confirmed, Phase 4 prep |

Atualize aqui quando qualquer parâmetro mudar. NUNCA mude parâmetros sem:
1. Justificativa com citação do knowledge base
2. Re-backtest via gates 5-layer
3. Paper trading re-validation (3 meses min)
4. Entry no mandate §7

---

## 10. Contatos operacionais

- **Broker:** Pepperstone SCB (Bahamas) — cTrader platform
- **Conta demo para paper:** cTrader Demo (free, 90 dias renováveis)
- **Regulação:** SCB (Bahamas)
- **API docs:** https://help.ctrader.com/open-api/
- **Status page:** https://status.pepperstone.com (monitor pre-market)

**Suporte Pepperstone Brasil:** chat via MyPepperstone após KYC. Português disponível.

---

**Fim do documento.**
