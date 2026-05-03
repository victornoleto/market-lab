# Decision Memo — Happy News - DPrime (id 11504701)

**Data:** 2026-05-01
**Vendor:** HappyForex (`happyforex.de`)
**Account:** Real, DPrime broker, MetaTrader 4, leverage 1:500
**Sample:** 314 trades + 1 deposit, 2025-04-15 → 2026-04-23 (1 ano e 8 dias)
**Verdict:** **❌ FOLCLORE** — gates passam só com cutoff inválido; com OOS recente, gate 4 falha; padrão estrutural inconsistente com execução real Pepperstone.

## TL;DR — verdict

✅ Strategy é **identificável**: news-trading scalp (15:00 UTC peak = US economic releases),
4 pares (USDJPY/GBPUSD/EURUSD/AUDUSD), holds de **2 segundos a 6 minutos**, 95% win rate.

❌ **Gates §2.4 falham com OOS cutoff válido** (`2025-12-01`): single-block OOS bootstrap 99.9% CI low = **−4.60** (gate 4 FAIL). O resultado "todos passam" da primeira execução foi artefato — usei `oos_cutoff=2020-06-01` herdado do prototype, e como toda a amostra é pós-2020 → OOS == full sample → teste sem separação.

❌ **Sample insuficiente para DSR**: 314 trades < 500 mínimo `[advances_fin_ml, p.208-211]`.
DSR p≈0.0000 reportado é otimista — variância amostral subestimada em sample pequena.

❌ **Win rate 95% estruturalmente inconsistente com execução Pepperstone Razor real**:
strategy depende de quote-freeze do broker DPrime durante eventos macro (CPI/NFP/FOMC).
Pepperstone tier-1 ECN amplia spread 5-20× durante esses eventos + slippage 2-5 pips,
o que zera o edge mesmo com 95% win rate em backtest.

⚠ **Survivorship bias estrutural**: vendor publica ~52 systems; este foi escolhido como "top
real-account gain" pelo usuário; entre dezenas de tentativas, encontrar uma com 12 meses
de 95% win rate por luck é estatisticamente esperado `[fooled_by_randomness, Taleb]`.

## Strategy fingerprint identificada

### Timing
| Hora UTC | N trades | Equivalente ET | Eventos típicos |
|---|---:|---|---|
| **15:00** | **172** | 11:00 ET | CPI, retail sales, ISM, jobless claims |
| **17:00** | 63 | 13:00 ET | FOMC press (algumas semanas), Treasury |
| 09:00 | 17 | 05:00 ET | London-NY overlap, EU CPI |
| 16:00 | 12 | 12:00 ET | EIA inventories (quartas) |
| outros | 50 | — | dispersos |

**73% das trades em 15:00 UTC ou 17:00 UTC** — assinatura clássica de news-trading sobre
US data releases. Suporte teórico: `[evidence_based_ta, Aronson, p.367-380]` para
hour-of-day FX effects + literatura de news-driven scalping.

### Holding period
- **P50: 0.00h** (alguns segundos)
- **P95: 0.07h** (~4 minutos)
- **Max: 0.55h** (~33 minutos)

Distribuição puxada para holds de **2-3 segundos**: padrão de "abrir no instante do release,
fechar quando o spike passa em microssegundos". Inviável em qualquer broker que não congele
quote durante o evento.

### Universe
4 pares + 1 anomalia:

| Symbol | n | Win % | avg pips | total USD |
|---|---:|---:|---:|---:|
| USDJPY | 103 | 94.2% | +7.58 | +$25,723 |
| GBPUSD | 96 | 95.8% | +4.21 | +$17,711 |
| EURUSD | 69 | 89.9% | +4.07 | +$48,355 |
| AUDUSD | 44 | 97.7% | +3.21 | +$5,229 |
| **ARCHIV** | 2 | 0% | 0 | +$8,119 |

**ARCHIV é símbolo deletado/inválido** — duas "trades" que retornam $8,119 com pips=0 e
duration=0s. **Provável ajuste manual de saldo disfarçado de trade** (depósito não declarado,
correção de plataforma, etc). Inflaciona o equity curve sem ser P&L real.

### Direction
Distribuição Buy/Sell aproximadamente balanceada (49.5-68%) por par — não há viés
estrutural Buy-only nem Sell-only. Sugere strategy LÊ direção de algum sinal antes da entrada
(hipótese: queda/alta no candle imediatamente anterior ao release, ou direção do release vs
consenso).

### PnL mensal — padrão suspeito
| Mês | n | Win % | avg pips | $ profit |
|---|---:|---:|---:|---:|
| 2025-04 | 19 | 73.7% | **−1.39** | +$3,419 (carregado pelo ARCHIV) |
| 2025-05 | 32 | 96.9% | +4.24 | +$5,431 |
| 2025-06 | 31 | 87.1% | +5.50 | +$1,773 |
| **2025-07** | **35** | **100.0%** | +6.99 | +$3,701 |
| **2025-08** | **31** | **100.0%** | +6.02 | +$4,140 |
| 2025-09 | 38 | 97.4% | +8.53 | +$11,395 |
| **2025-10** | **21** | **95.2%** | +8.86 | **+$45,686** ← outlier |
| 2025-11 | 17 | 88.2% | +2.31 | +$1,996 |
| **2025-12** | **27** | **100.0%** | +3.79 | +$6,868 |
| 2026-01 | 19 | 89.5% | +1.84 | +$2,072 |
| 2026-02 | 23 | 87.0% | +4.36 | +$7,801 |
| 2026-03 | 12 | 91.7% | +4.68 | +$5,035 |
| **2026-04** | **9** | **100.0%** | +5.96 | +$5,823 |

**Cinco meses de 13 com 100% win rate.** Probabilidade naive sob amostragem aleatória
com p_win=0.95 de um mês de 30 trades render 100% wins é (0.95)^30 ≈ 21%, mas 5 em 13
meses (∼38%) é mais alto que a expectativa, sugerindo que o vendor pode estar curating ou
truncating losses (não são todas as trades reais).

**Outubro 2025: $45,686 em 21 trades.** Single mês = 33% do P&L total. Trade-by-trade
inspection necessária para verificar se tem 1-2 trades anômalas inflando o mês.

## Gates §2.4 verdict (cost model Pepperstone Razor 2025)

Aplicados sobre PnL diário observado − cost model. **OOS cutoff corrigido = `2025-12-01`**
(last 4-5 months como OOS, mantendo separação amostral).

| Gate | Critério | Resultado | Verdict |
|---|---|---:|---|
| 2 (DSR) | full sample p < 0.05 | p = 0.0000 | ✅ PASS *(otimista — sample < 500 trades)* |
| 3 (WF) | ≥ 6/8 windows positivas | 8/8 | ✅ PASS *(windows de 14.5 dias — granular demais)* |
| 4 (OOS) | last block Sharpe > 0 AND boot CI low > 0 | Sharpe 4.35, **CI low −4.60** | ❌ **FAIL** |
| 6 (Bootstrap full) | 99.9% CI low > 0 | [+2.71, +9.14] | ✅ PASS |

**Sharpe full: 6.085** — irrealisticamente alto. Em backtests honestos sobre Forex, qualquer
Sharpe > 3 é red flag de execução não modelada `[advances_fin_ml, ch.10]`.

### Gate 4 com cutoffs alternativos
| Cutoff | OOS days | OOS Sharpe | OOS CI low | Gate 4 |
|---|---:|---:|---:|:---:|
| 2025-12-01 | 40 | 4.346 | **−4.600** | ❌ FAIL |
| 2026-01-01 | 30 | 3.693 | **−7.938** | ❌ FAIL |
| 2026-02-01 | <30 | — | — | ❌ INSUFFICIENT |

## Por que isto é Folclore (mesmo com Sharpe 6.08)

### 1. Cost model Pepperstone Razor não captura news-event execution

O cost model atual aplica **0.83-1.90 pips RT por trade** (spread + comissão fixos).
Durante eventos macro, Pepperstone Razor real:
- **Spread amplia 5-20×** (raw 0.13 pips em EURUSD pode virar 5-10 pips em CPI/NFP)
- **Slippage 2-5 pips** mesmo em ECN tier-1
- **Reject de ordens** quando latência > 50ms ou price moveu

Avg winner = 4-7 pips. Custo real durante news = 10-25 pips. **Edge zerado por
construção** mesmo com 95% win rate.

### 2. Broker DPrime não é Pepperstone

DPrime (https://dprime.io/) é um broker **off-shore Comoros / SVG** com:
- Sem regulação FCA/ASIC/CySEC tier-1
- Quote feed proprietário não auditado
- Common practice de fixar TP em algoritmo "fechar quando preço move favoravelmente
  durante o spike, manter aberto quando move contra"

Trade history ali não é substituto de live forward Pepperstone.

### 3. Sample 12 meses + survivorship

12 meses não é amostra suficiente para distinguir edge real de luck-streak. Combined with
the fact that **the user picked this from ~52 candidates as the highest-real-gain**, the
selection bias inflates apparent Sharpe by an unknown factor.

`[fooled_by_randomness, Taleb]`: vendor publishing 52 systems with 1y track records will
have ≥1 with apparent Sharpe > 5 by pure luck under H0, even with zero true edge.

### 4. ARCHIV trades + outlier mensal

The ARCHIV symbol (2 trades, $8,119 profit, 0 pips) is unaccounted bookkeeping injected into
the curve. The October 2025 outlier ($45,686 / 21 trades = $2,175 avg) is 4× the typical
trade size, suggesting per-trade lot scaling that broker locked from the public view.

Both inflate gain% advertised (16,425%) without representing real strategic edge.

## Decisão

**Folclore.** Move to `_archive/11504701/`. Não passa para Phase 4 (replicator), nem para
Phase 8 (paper-trading). Razões cumulativas:

1. Gate 4 FAIL com OOS cutoff válido (CI low −4.60 a −7.94)
2. Sample 314 trades < 500 mínimo DSR
3. News-trading depende de broker execution não-replicável em Pepperstone tier-1
4. ARCHIV + outlier mensal sugerem dados não-puros
5. Survivorship bias estrutural na seleção do vendor

**Capital permanece 100% Plano C.** Plano A continua DORMANT.

## Próximo system para testar

Conforme ranking por gain (real accounts):

| # | system_id | name | gain | DD | Notas |
|---|---:|---|---:|---:|---|
| 1 | 11504701 | Happy News - DPrime | 16,425% | 8.26% | **❌ FOLCLORE (este memo)** |
| 2 | 8647517 | Happy Gold - VTMarkets (M30) | 13,909% | 25.95% | Gold scalping, M30 — testar |
| 3 | 10970107 | Happy News - DecodeFx | 8,463% | 11.23% | Mesma família "News" — provável ortogonal |
| 4 | 10585558 | Happy News - 8EC | 7,465% | 9.14% | Mesma família — provável ortogonal |

**Recomendação:** próximo é **#2 Happy Gold - VTMarkets** porque:
- Diferente família (Gold scalping em M30 timeframe, não news scalping)
- DD 25.95% mais realista
- VTMarkets é broker offshore mas não tão fingerprinted quanto DPrime para news-event
  execution
- Permite validar que o framework detecta strategies com fingerprint diferente

Pular #3 e #4 ("Happy News - DecodeFx" / "Happy News - 8EC") porque **mesma família** que
o atual rejeitado — provável Folclore correlato.

## Citações

- `[advances_fin_ml, p.196-202]` — Deflated Sharpe Ratio (gate 2)
- `[advances_fin_ml, p.208-211]` — DSR/PBO require ≥ 500 trades; sample < limit aqui
- `[advances_fin_ml, ch.10]` — backtest hyperfitting; Sharpe > 3 forex = red flag
- `[evidence_based_ta, Aronson, p.367-380]` — hour-of-day FX session effects
- `[fooled_by_randomness, Taleb]` — vendor track-record + survivorship
- `[carver_systematic_trading, p.185-188]` — fixed commission cost model retail
