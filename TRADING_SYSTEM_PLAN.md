# Plano de Desenvolvimento: Sistema de Swing Trading Algorítmico

**Autor:** Victor (Noleto Dev)  
**Data:** Abril 2026  
**Status:** Planejamento / Pré-desenvolvimento  
**Stack alvo:** Python 3.11+ · Ubuntu 24 · PostgreSQL · Docker

---

## 1. Execução: Pepperstone via cTrader Open API

O broker escolhido é **Pepperstone**, usando a **cTrader Open API** (Protobuf sobre TCP persistente com OAuth2). Essa decisão substitui o plano anterior de usar MetaTrader 5 no XM (inviável em VPS Ubuntu headless — exigia Wine + VNC + `mt5linux` RPC, frágil na operação).

Histórico de alternativas descartadas:

| Broker/API | Por que foi descartado |
|---|---|
| **Alpaca** | Não aceita residência fiscal BR. Workarounds via LLC US / ITIN+W-8BEN desproporcionais ao capital de $1k. |
| **OANDA** | Encerrou cadastros para residentes BR. |
| **Interactive Brokers** | API não é REST nativa — exige IB Gateway ou Client Portal Gateway rodando como processo intermediário, 2FA recorrente, IBC para manter login. Comissões pesam mais em capital pequeno. |
| **XM via MetaTrader 5** | MT5 não tem cliente Linux nativo. Única via é Docker+Wine+VNC (imagem `gmag11/MetaTrader5-Docker` + `mt5linux`). Wine é historicamente frágil; VNC complica bootstrap e recovery numa VPS headless; falha de login = downtime manual. |

### Stack Pepperstone/cTrader

```
[Ubuntu Host - Python 3.12 nativo]
        │ TCP persistente (Protobuf)
        ▼
[cTrader Open API (Spotware)  :5035]
        │
        ▼
[Pepperstone — conta cTrader demo ou live]
```

**Setup resumido:**
1. Registrar app no portal `openapi.ctrader.com` (cTID) → obter `client_id` + `client_secret`.
2. OAuth2 bootstrap one-time na máquina local do dev (browser abre consent cTID; callback em `localhost:8080` captura `authorization_code`; troca por `access_token` + `refresh_token`).
3. Persistir `refresh_token` no `.env`; copiar pra VPS via rsync/scp.
4. No host Ubuntu: `pip install ctrader-open-api`.
5. Código no host: `from ctrader_open_api import Client, EndPoints, Protobuf` (SDK oficial Spotware, Twisted-based, async).
6. VPS usa `refresh_token` pra obter `access_token` novo (~30 dias de validade). Comportamento de rotação (se o refresh também rotaciona) a confirmar no smoke test.

**Refs:** `help.ctrader.com/open-api/` · `github.com/spotware/OpenApiPy` · `pepperstone.com/en-eu/platforms/integrations/ctrader-automate/`

### Cobertura de asset classes

Pepperstone via cTrader oferece, tudo como CFD:
- **Forex:** ~90 pares (majors, minors, exóticos).
- **Índices:** SPX500, NAS100, US30, GER40, UK100, JP225, etc.
- **Share CFDs:** majors globais (AAPL, TSLA, NVDA, MSFT, GOOG, etc. — coverage menor que XM mas suficiente pra universo curado de 5-15 instrumentos).
- **Crypto CFDs:** BTC, ETH, SOL, etc.
- **Commodities:** ouro, prata, petróleo (WTI/Brent), gás natural.

Lista exata é obtida via `ProtoOASymbolsListReq` na primeira conexão de dev e documentada em `docs/instruments_pepperstone.md` quando a Fase 2 abrir.

### Restrição estrutural: tudo é CFD

Como na XM, todos os instrumentos são CFDs — há swap/overnight cobrado diariamente. Isso impõe uma restrição de design sobre **toda** a camada de estratégia: holding típico de minutos a poucos dias, fechando posição antes do rollover (provavelmente 22h GMT, a confirmar com Pepperstone). Buy-and-hold multi-mês está **fora de escopo** enquanto o broker for CFD — o swap vira drag material sobre o alpha.

Essa restrição informa a sub-fase 2.0 (Universe Selector) e a seleção das estratégias candidatas (ver ROADMAP.md Fase 2).

---

## 2. Arquitetura Proposta do Sistema

```
┌─────────────────────────────────────────────────┐
│                 TRADING SYSTEM                   │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐   ┌──────────────────────┐    │
│  │ DATA LAYER   │   │ STRATEGY ENGINE      │    │
│  │              │   │                      │    │
│  │ cTrader Open │──▶│ Universe Selector    │    │
│  │ API (OHLCV + │   │ Signal Generator     │    │
│  │ tick stream) │   │ (indicators, ML,     │    │
│  │              │   │  regime detection)   │    │
│  │ Alpha Vantage│   │                      │    │
│  │ (enriquec.)  │   └──────────┬───────────┘    │
│  └──────────────┘              │                 │
│                                ▼                 │
│  ┌──────────────┐   ┌──────────────────────┐    │
│  │ BACKTEST     │   │ RISK MANAGEMENT      │    │
│  │              │   │                      │    │
│  │ VectorBT     │   │ Position Sizing      │    │
│  │ Backtesting  │   │ Kelly Criterion      │    │
│  │   .py        │   │ Stop Loss / TP       │    │
│  │              │   │ Max Drawdown Guard   │    │
│  └──────────────┘   └──────────┬───────────┘    │
│                                │                 │
│                                ▼                 │
│  ┌──────────────┐   ┌──────────────────────┐    │
│  │ STORAGE      │   │ EXECUTION LAYER      │    │
│  │              │   │                      │    │
│  │ PostgreSQL   │   │ cTrader Open API     │    │
│  │ (market_data,│   │ (Pepperstone demo    │    │
│  │  trades,     │   │  ou live — Protobuf  │    │
│  │  signals,    │   │  sobre TCP, OAuth2)  │    │
│  │  features)   │   │                      │    │
│  └──────────────┘   └──────────────────────┘    │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ MONITORING & ALERTS                       │   │
│  │ Telegram Bot · Grafana · Logs             │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
└─────────────────────────────────────────────────┘
```

A mesma conexão cTrader Open API serve para **market data** (histórico OHLCV + stream de ticks) e **execução** (ordens, posições, account info). Não há dependência de brokers adicionais (CCXT, MT5, Alpaca) — tudo converge num único fornecedor.

---

## 3. APIs de Dados de Mercado

### Primária: cTrader Open API (mesma conexão da execução)

Histórico OHLCV via `ProtoOAGetTrendbarsReq` (timeframes M1/M5/H1/D1+), stream de ticks via `ProtoOASubscribeSpotsReq`. Suficiente para os 5-15 instrumentos do universo curado. Latência baixa (servidor Spotware em Londres), sem rate limits relevantes para o caso de uso.

### APIs de enriquecimento (opcionais, para análise macro/contextual)

| API | Cobertura | Free Tier | MCP Server |
|---|---|---|---|
| **Alpha Vantage** | Stocks, Forex, Crypto, 60+ indicadores, fundamentals | 25 req/dia (free) | ✅ Oficial |
| **Finnhub** | Stocks, Forex, Crypto, Sentiment | 60 req/min | ✅ Community |
| **EODHD** | 70+ exchanges globais | Limitado | ✅ 77 tools |
| **FCS API** | Forex (2000+ pares), Crypto | Limitado | ❌ |
| **yfinance** | Stocks, ETFs (Yahoo Finance) | Ilimitado* | ❌ |

*yfinance é não-oficial e pode ter instabilidade. Essas APIs entram apenas quando o Claude precisa de contexto macro/fundamentalista que o cTrader não fornece (earnings, sentiment, macro regime). Não são dependência da infraestrutura de execução.

### MCP Servers para AI-Assisted Trading

Para usar com Claude Desktop/Claude Code e criar workflows de análise:

| MCP Server | Foco | Custo |
|---|---|---|
| **Alpha Vantage MCP** | Mais completo (preços + indicadores + fundamentals) | Free key |
| **Financial Datasets MCP** | Financials, SEC filings, screener | Free (OAuth) |
| **EODHD MCP** | 77 tools, comparação de stocks | Free + paid |
| **CCXT MCP** | Crypto-only, 100+ exchanges | Free (open source) |
| **Lambda Finance MCP** | All-in-one: earnings, options, Greeks | Pago |

**Recomendação:** Começar com Alpha Vantage MCP (grátis, mais versátil) + Financial Datasets MCP (análise fundamentalista via OAuth, sem API key).

---

## 4. Frameworks de Backtesting

### Comparativo para seu caso (swing trade)

| Framework | Velocidade | Live Trading | Melhor para |
|---|---|---|---|
| **VectorBT** | ⚡ Extrema | Via adapter custom | Otimização massiva de parâmetros |
| **Backtesting.py** | ⚡ Rápida | Via adapter custom | Simplicidade, prototipagem |
| **Backtrader** | 🔵 Média | Via adapter custom | Swing traders, evento-driven |
| **Custom loop** | — | Nativo | Loop Python direto com `ctrader_open_api` |

**Recomendação para swing trade com $1000:**
1. **Prototipar** com Backtesting.py (simples, rápido)
2. **Otimizar parâmetros** com VectorBT (testar milhares de combinações)
3. **Deploy para live** via loop Python custom que consome sinais do framework e envia ordens pela cTrader Open API (paper/demo primeiro!). StrateQueue não tem adapter oficial para cTrader em 2026; fazer o adapter direto é mais simples que integrar um bridge genérico.

---

## 5. Estratégias Baseadas na Literatura

Baseado nos livros que você listou, aqui estão os frameworks conceituais mais relevantes para swing trade:

### 5.1 Trend Following (Stocks on the Move — Clenow)

- Ranking de momentum relativo (Rate of Change de 90 dias)
- Filtro de regime: só opera long quando índice está acima da SMA 200
- Position sizing por ATR (Average True Range)
- Rebalanceamento semanal ou quinzenal
- **Ideal para:** SPY, ETFs setoriais, large caps

### 5.2 Cycle Analysis (Ehlers — Rocket Science / Cybernetic Analysis / Cycle Analytics)

- MESA Adaptive Moving Average (MAMA)
- Hilbert Transform para detecção de ciclo dominante
- Indicador Stochastic Cyber Cycle
- Bandpass filter para isolar frequências de preço
- Fisher Transform para normalização de sinais
- **Ideal para:** Forex, crypto (mercados cíclicos)

### 5.3 Regime Detection (Detecting Regime Change — Chen)

- Hidden Markov Models (HMM) para identificar bull/bear/sideways
- Troca dinâmica de estratégia conforme regime
- Volatility clustering para ajustar position sizing
- **Ideal para:** Adaptar estratégia ao contexto de mercado

### 5.4 Machine Learning (Advances in Financial ML — López de Prado)

- Triple Barrier Method para labeling
- Purged K-Fold Cross-Validation (evitar data leakage)
- Feature importance via MDI/MDA/SFI
- Meta-labeling: ML decide o sizing, não a direção
- Fractionally Differentiated Features (manter memória + estacionariedade)
- **Ideal para:** Refinar sinais de outras estratégias

### 5.5 Money Management (Vince — Leverage Space / Mathematics of Money Management)

- Optimal f (fração ótima do capital por trade)
- Kelly Criterion e fractional Kelly (1/4 Kelly para ser conservador)
- Risk of ruin analysis
- Drawdown management com circuit breakers
- **CRÍTICO para $1000:** com capital pequeno, o position sizing é tão importante quanto a estratégia

### 5.6 Statistical Validation (Permutation Tests — Timothy Masters)

- Walk-forward analysis
- Monte Carlo permutation tests para validar edge
- White's Reality Check para múltiplas comparações
- Evitar overfitting via complexidade controlada
- **Essencial:** Todo backtest deve passar por validação estatística

### 5.7 Sentiment Analysis (Trading on Sentiment — Peterson)

- Fear & Greed Index como filtro
- Put/Call ratio
- VIX como regime indicator
- News sentiment via NLP
- **Complementar:** Usar como filtro adicional, não como sinal primário

---

## 6. O Problema Central: Overfitting — Por Que 90% das Estratégias Falham

> *"Backtesting is not a research tool. It is a tool for measuring the risk of overfitting."*
> — Marcos López de Prado, Advances in Financial Machine Learning

### 6.1 O que é Overfitting em Trading (e por que é diferente de ML tradicional)

Overfitting em trading acontece quando uma estratégia "memoriza" os padrões específicos do histórico em vez de capturar uma dinâmica real do mercado. O resultado: backtests espetaculares, performance real desastrosa.

Em ML tradicional, dados são geralmente IID (independentes e identicamente distribuídos). Em finanças, **não são** — séries temporais têm autocorrelação, não-estacionariedade, mudanças de regime e dependências temporais complexas. Isso significa que as técnicas padrão de validação (como k-fold simples) **não funcionam** para dados financeiros.

**O ciclo vicioso do overfitting em trading:**
```
Criar estratégia → Backtestear → Resultado ruim →
Ajustar parâmetros → Backtestear de novo → Resultado melhor →
Ajustar mais → Backtestear mais → Resultado INCRÍVEL →
Ir para live → PERDER DINHEIRO →
Conclusão errada: "o mercado mudou"
Conclusão certa: "eu fiz overfit no histórico"
```

### 6.2 As Formas de Overfitting que Vamos Combater

| Tipo | Descrição | Fonte (livros) |
|---|---|---|
| **Parameter Overfitting** | Otimizar RSI=14, SMA=50 porque funcionou no passado | Masters (Testing & Tuning) |
| **Selection Bias** | Testar 100 estratégias, publicar a que funcionou | López de Prado (AFML) |
| **Temporal Overfitting** | Treinar em bull market, testar em bull market | Masters (Permutation Tests) |
| **Data Snooping** | Usar informação futura sem perceber (lookahead bias) | López de Prado (AFML) |
| **Complexity Overfitting** | Estratégia com 15 indicadores que "explica" tudo | Clenow (Systematic Trading) |
| **Survivorship Bias** | Testar em ativos que existem hoje, ignorar os que faliram | Kaufman (Trading Systems) |
| **Meta-Overfitting** | Usar CPCV em 50 estratégias e pegar a melhor — overfitting do processo de pesquisa | López de Prado (AFML) |

### 6.3 O Framework Anti-Overfitting do Sistema (7 Camadas de Defesa)

Nossa aplicação implementa proteção em **cada etapa** do pipeline:

#### CAMADA 1 — Princípio da Parcimônia (Design da Estratégia)

**Regra:** Quanto mais simples a estratégia, menor o risco de overfit.

- Máximo de 3-4 parâmetros por estratégia (não 15)
- Cada parâmetro deve ter justificativa econômica/física (não apenas "funcionou")
- Os indicadores de Ehlers (Rocket Science, Cybernetic Analysis) são preferidos justamente porque têm fundamentação matemática em processamento de sinais — não são curve-fitting arbitrário
- O momentum de Clenow (Stocks on the Move) usa apenas 2 parâmetros: período de lookback e SMA de regime

```python
# ❌ OVERFIT: 8 parâmetros sem justificativa
def strategy_overfit(rsi_period, rsi_upper, rsi_lower, macd_fast, 
                     macd_slow, macd_signal, bb_period, bb_std):
    # "Otimizei cada um desses no backtest"
    ...

# ✅ ROBUSTO: 2 parâmetros com fundamentação
def strategy_robust(cycle_length, regime_ma):
    # cycle_length: baseado no ciclo dominante detectado (Ehlers)
    # regime_ma: filtro de tendência macro
    ...
```

#### CAMADA 2 — Purged K-Fold Cross-Validation (Validação dos Dados)

O k-fold padrão do scikit-learn **não serve** para finanças porque ignora dependências temporais. Implementaremos o **Combinatorial Purged Cross-Validation (CPCV)** do López de Prado:

**Como funciona:**
1. **Purging:** Remove do treino qualquer amostra cujo timestamp se sobreponha ao label do teste — elimina data leakage
2. **Embargo:** Adiciona um buffer temporal entre treino e teste — proteção extra contra vazamento sutil
3. **Combinatorial:** Em vez de 1 caminho walk-forward, gera N caminhos out-of-sample — cada um simulando um cenário de mercado diferente

**O resultado não é um número (Sharpe = 2.1), mas uma DISTRIBUIÇÃO:**

```
Distribuição de Sharpe Ratios em 100 caminhos CPCV:
│
│        ▄▄██▄▄
│      ▄████████▄
│    ▄████████████▄
│  ▄████████████████▄
│▄████████████████████▄
└──────────────────────────
-0.5    0.3    0.8    1.5    2.0

Média: 0.82  │  Mediana: 0.78  │  P5: 0.15  │  P95: 1.45
→ "A estratégia é modestamente lucrativa na maioria dos cenários"
→ Muito mais honesto que "Sharpe = 2.1 no backtest"
```

**Implementação planejada:**
```python
from validation.cpcv import CombinatorialPurgedCV

cpcv = CombinatorialPurgedCV(
    n_splits=6,          # Dividir dados em 6 grupos
    n_test_splits=2,     # 2 grupos como teste por vez
    purge_window=5,      # Remover 5 barras ao redor do teste
    embargo_pct=0.01     # 1% de embargo adicional
)
# Gera C(6,2) = 15 combinações → 5+ caminhos walk-forward OOS
# Resultado: distribuição de métricas, não um número único

results = cpcv.backtest(strategy, data)
print(f"PBO (Probability of Backtest Overfitting): {results.pbo:.2%}")
# Se PBO > 50%, a estratégia provavelmente é overfit → DESCARTAR
```

#### CAMADA 3 — Permutation & Randomization Tests (Validação Estatística)

Baseado diretamente no livro do Timothy Masters (Permutation and Randomization Tests):

**Pergunta fundamental:** "Minha estratégia é melhor que o acaso?"

**Teste de Permutação:**
1. Rodar a estratégia nos dados reais → Sharpe real = S
2. Embaralhar os retornos aleatoriamente 1000x
3. Rodar a estratégia em cada versão embaralhada → 1000 Sharpes aleatórios
4. Se S está no top 5% dos Sharpes aleatórios → p-value < 0.05 → edge real
5. Se S NÃO está no top 5% → a estratégia é indistinguível de sorte → DESCARTAR

```python
from validation.permutation import PermutationTest

perm = PermutationTest(n_permutations=1000, seed=42)
result = perm.test(strategy, returns)

print(f"Sharpe real: {result.real_sharpe:.3f}")
print(f"Sharpe médio aleatório: {result.mean_random_sharpe:.3f}")
print(f"p-value: {result.p_value:.4f}")

if result.p_value > 0.05:
    print("⚠️ ESTRATÉGIA INDISTINGUÍVEL DE SORTE - DESCARTAR")
else:
    print("✅ Edge estatisticamente significativo")
```

**Monte Carlo Simulation (complementar):**
- Gera 10.000 equity curves sintéticas a partir dos trades reais
- Calcula distribuição de drawdowns, retornos, Sharpe
- Estima risk-of-ruin para o capital de $1000

#### CAMADA 4 — Walk-Forward Analysis (Validação Temporal)

Walk-forward simula como a estratégia seria operada na prática:

```
Dados: 2020 ──────────────────────────────── 2026

Janela 1: [===TREINO===][=TESTE=]
Janela 2:    [===TREINO===][=TESTE=]
Janela 3:       [===TREINO===][=TESTE=]
Janela 4:          [===TREINO===][=TESTE=]
...

Cada TESTE é puramente out-of-sample.
A estratégia é re-otimizada em cada janela de treino.
Performance final = concatenação de TODOS os testes.
```

**Limitação reconhecida:** Walk-forward testa apenas 1 caminho histórico. Por isso combinamos com CPCV (Camada 2) para ter múltiplos caminhos.

#### CAMADA 5 — Deflated Sharpe Ratio (Correção Estatística)

Quando você testa N estratégias e pega a melhor, o Sharpe Ratio reportado é inflado. O **Deflated Sharpe Ratio (DSR)** do López de Prado corrige isso:

```python
from validation.deflated_sharpe import deflated_sharpe_ratio

dsr = deflated_sharpe_ratio(
    sharpe_observed=1.8,        # Sharpe da "melhor" estratégia
    n_trials=50,                # Quantas estratégias você testou
    variance_of_sharpe=0.3,     # Variância dos Sharpes observados
    T=252 * 3,                  # Número de observações (3 anos diários)
    skewness=-0.5,              # Assimetria dos retornos
    kurtosis=4.2                # Curtose dos retornos
)

print(f"Sharpe observado: 1.80")
print(f"DSR (corrigido para {50} tentativas): {dsr:.3f}")
# Se DSR < 1.0, o Sharpe não é estatisticamente significativo
# dado o número de tentativas realizadas
```

**Na prática:** Manteremos um log de TODAS as estratégias testadas (mesmo as descartadas). Isso alimenta o DSR e nos protege contra selection bias.

#### CAMADA 6 — Regime Awareness (Proteção Estrutural)

Overfitting frequentemente ocorre porque a estratégia foi treinada em um único regime de mercado. Nossa defesa:

- **Hidden Markov Models (HMM)** para classificar regimes automaticamente (bull, bear, sideways, alta/baixa volatilidade)
- **Testar performance por regime:** a estratégia deve ser lucrativa (ou pelo menos não desastrosa) em TODOS os regimes, não apenas no que dominou o período de treino
- **Regime-conditional parameters:** parâmetros podem variar por regime, mas cada regime deve ter dados suficientes para evitar overfit dentro do regime

```python
# Não aceitar uma estratégia que só funciona em bull market
regime_results = backtest_by_regime(strategy, data)

for regime, metrics in regime_results.items():
    print(f"Regime {regime}: Sharpe={metrics.sharpe:.2f}, "
          f"MaxDD={metrics.max_drawdown:.1%}, "
          f"N_trades={metrics.n_trades}")

# Critério de aceitação:
# - Sharpe > 0 em pelo menos 3 dos 4 regimes
# - Max drawdown < 20% em TODOS os regimes
# - Mínimo de 30 trades por regime para significância
```

#### CAMADA 7 — O Papel do Claude como Guardião Anti-Overfit

Aqui é onde o Claude como agente de trading se torna uma vantagem real contra overfitting:

**7a. Auditoria de Racionalidade**
Antes de qualquer estratégia entrar em produção, Claude recebe a especificação completa e questiona:

```
Prompt para Claude:
"Analise esta estratégia e identifique riscos de overfitting:
- Parâmetros: [lista]
- Dados de treino: [período]
- Sharpe observado: [valor]
- Número de variantes testadas: [N]

Pergunte: 
1. Cada parâmetro tem justificativa econômica ou é curve-fitting?
2. O Sharpe sobrevive ao Deflated Sharpe Ratio com N tentativas?
3. Existem degrees of freedom excessivos?
4. A complexidade é justificável pela quantidade de dados?
"
```

**7b. Monitoramento de Drift em Live**
Uma vez em produção, Claude monitora indicadores de degradação:

```python
# Claude recebe métricas semanais e alerta sobre divergências
drift_check = {
    "sharpe_backtest": 1.2,
    "sharpe_live_30d": 0.3,    # ← ALERTA: degradação severa
    "win_rate_backtest": 0.58,
    "win_rate_live_30d": 0.41,  # ← ALERTA: divergência
    "avg_trade_backtest": "2.1%",
    "avg_trade_live_30d": "0.6%",
}
# Claude analisa e recomenda: pausar, re-otimizar, ou descontinuar
```

**7c. Second Opinion com Dados Reais**
Antes de cada trade, Claude pode cruzar os sinais da estratégia com dados em tempo real via MCP e questionar:

- "O sinal é consistente com o regime atual de mercado?"
- "Há eventos macro (FOMC, NFP, earnings) que invalidam o setup?"
- "O volume confirma o movimento ou é ruído?"

Essa camada de julgamento qualitativo complementa a validação quantitativa e é algo que algoritmos puramente sistemáticos não conseguem fazer bem.

### 6.4 Checklist Anti-Overfit (Gate de Produção)

Nenhuma estratégia entra em paper trading sem passar por TODOS estes critérios:

```
CHECKLIST ANTI-OVERFIT — GATE DE PRODUÇÃO
═══════════════════════════════════════════

□ PARCIMÔNIA
  □ ≤ 4 parâmetros livres
  □ Cada parâmetro tem justificativa econômica documentada
  □ Remoção de qualquer parâmetro degrada performance < 15%

□ VALIDAÇÃO CRUZADA
  □ CPCV executado com ≥ 5 caminhos OOS
  □ PBO (Probability of Backtest Overfitting) < 40%
  □ Sharpe mediano dos caminhos CPCV > 0.5

□ SIGNIFICÂNCIA ESTATÍSTICA
  □ Permutation test p-value < 0.05
  □ Deflated Sharpe Ratio > 1.0 (corrigido para N tentativas)
  □ ≥ 100 trades no período de teste

□ ROBUSTEZ TEMPORAL
  □ Walk-forward em ≥ 8 janelas consecutivas
  □ Lucrativo em ≥ 6 das 8 janelas
  □ Nenhuma janela com drawdown > 25%

□ ROBUSTEZ POR REGIME
  □ Testado em ≥ 3 regimes de mercado distintos
  □ Sharpe > 0 em ≥ 3 de 4 regimes
  □ ≥ 30 trades por regime

□ STRESS TEST
  □ Sobrevive a +50% nos custos de transação
  □ Sobrevive a slippage de 2x o estimado
  □ Sobrevive a delays de execução de até 1 minuto
  □ Monte Carlo: risk of ruin < 5% para capital de $1000

□ AUDITORIA CLAUDE
  □ Claude revisou e não identificou red flags de overfit
  □ Lógica econômica validada contra conhecimento dos livros
  □ Sem data snooping ou lookahead bias identificado

═══════════════════════════════════════════
RESULTADO: □ APROVADO  □ REPROVADO  □ REVISÃO
```

### 6.5 Como os Livros Alimentam Cada Camada

| Livro | Contribuição Anti-Overfit |
|---|---|
| **Advances in Financial ML** (López de Prado) | CPCV, Purged K-Fold, Triple Barrier, Meta-labeling, DSR |
| **Permutation and Randomization Tests** (Masters) | Testes de permutação, significância estatística |
| **Testing and Tuning Market Trading Systems** (Masters) | Walk-forward, stress testing, graus de liberdade |
| **Assessing and Improving Prediction** (Masters) | Métricas de avaliação, bootstrap confidence intervals |
| **Systematic Trading** (Clenow) | Parcimônia, position sizing robusto, simplicidade |
| **Trading Systems and Methods** (Kaufman) | Robustness testing, out-of-sample validation |
| **Rocket Science / Cybernetic Analysis** (Ehlers) | Indicadores com fundamentação em processamento de sinais (não são arbitrários) |
| **Detecting Regime Change** (Chen) | Regime-aware validation, HMM |
| **Statistically Sound Indicators** (Masters) | Indicadores com validação estatística incorporada |
| **Data-Driven Science and Engineering** | SVD, PCA para redução de dimensionalidade (menos parâmetros = menos overfit) |

### 6.6 O que o Sistema NÃO Fará (Disciplina)

Para evitar overfitting do processo de pesquisa (meta-overfitting):

1. **Não** testaremos mais de 10 variantes de estratégia no mesmo dataset sem aplicar DSR
2. **Não** descartaremos resultados negativos — todo teste é registrado no log
3. **Não** ajustaremos parâmetros após ver resultados out-of-sample (isso transforma OOS em in-sample)
4. **Não** usaremos dados de teste para tomar qualquer decisão de design
5. **Sempre** reservaremos 20% dos dados mais recentes como holdout final, intocável até a decisão final de go/no-go
6. **Preferiremos** estratégias com Sharpe modesto (0.5-1.0) mas robusto sobre estratégias com Sharpe alto (2.0+) mas frágil

---

## 7. Estratégia Inicial Sugerida: Momentum + Regime Filter

Para começar com $1000 e buscar ~10% ao mês (nota: isso é extremamente agressivo — mais detalhes na seção 10):

```python
# PSEUDOCÓDIGO - Estratégia Multi-Asset Swing

UNIVERSO = ["SPY", "QQQ", "BTC/USDT", "ETH/USDT"]
TIMEFRAME = "4h"  # ou diário para menos ruído
LOOKBACK_MOMENTUM = 20  # dias
REGIME_FILTER_MA = 50   # SMA para filtro de tendência

para cada ativo em UNIVERSO:
    # 1. Regime Detection
    regime = detectar_regime(ativo, método="HMM" ou "SMA_filter")
    
    # 2. Signal Generation
    se regime == "BULL":
        momentum = calcular_ROC(ativo, LOOKBACK_MOMENTUM)
        cyber_cycle = ehlers_stochastic_cyber_cycle(ativo)
        
        se momentum > threshold E cyber_cycle cruzou_acima(oversold):
            sinal = COMPRAR
    
    se regime == "BEAR":
        # Para crypto com short disponível
        se cyber_cycle cruzou_abaixo(overbought):
            sinal = VENDER_SHORT  # só crypto via CCXT
    
    # 3. Risk Management
    atr = calcular_ATR(ativo, 14)
    stop_loss = entrada - (2 * atr)
    take_profit = entrada + (3 * atr)  # R:R mínimo 1.5:1
    
    # 4. Position Sizing (Fractional Kelly)
    win_rate = calcular_win_rate_historico()
    avg_win_loss_ratio = calcular_ratio()
    kelly = (win_rate * avg_win_loss_ratio - (1 - win_rate)) / avg_win_loss_ratio
    position_size = capital * kelly * 0.25  # 1/4 Kelly (conservador)
    
    # 5. Execution
    executar_ordem(ativo, sinal, position_size, stop_loss, take_profit)
```

---

## 8. Claude como Agente de Decisão de Trade

### A ideia central

O sistema não é apenas "Claude escreve o código e vai embora". Claude participa ativamente do loop de decisão como um analista de mercado AI. Existem 3 arquiteturas possíveis:

### Arquitetura A — Claude Code + MCP Servers (⭐ RECOMENDADA)

Claude Code conecta-se diretamente a MCP servers de dados financeiros e ao broker. Você interage via terminal:

```
┌─────────────────────────────────────────────┐
│              CLAUDE CODE (terminal)          │
│                                              │
│  MCP Servers conectados:                     │
│  ├── Alpha Vantage MCP (contexto macro)      │
│  ├── TradingView MCP (screening, backtest)   │
│  ├── Financial Datasets MCP (fundamentals)   │
│  ├── cTrader (via ctrader_open_api Python,   │
│  │   não MCP — portfolio + execução)         │
│  └── Trading Skills (custom knowledge)       │
│                                              │
│  Você pergunta:                              │
│  "Analise SPX500 e BTCUSD. Devo entrar?"     │
│                                              │
│  Claude:                                     │
│  1. Puxa OHLCV via cTrader Open API          │
│  2. Calcula indicadores (Ehlers, regime)     │
│  3. Detecta regime de mercado                │
│  4. Avalia risk/reward                       │
│  5. Recomenda: BUY/HOLD/SELL + sizing        │
│  6. Você aprova → app executa via cTrader    │
│                                              │
└─────────────────────────────────────────────┘
```

**Setup do Claude Code com MCPs:**
```bash
# Adicionar Alpha Vantage MCP
claude mcp add alphavantage \
  --url "https://mcp.alphavantage.co/mcp?apikey=YOUR_KEY"

# Adicionar TradingView MCP (screening + 30+ indicadores)
claude mcp add tradingview \
  --command "uvx" --args "--from tradingview-mcp-server tradingview-mcp"

# Adicionar Financial Datasets MCP (OAuth, sem API key)
claude mcp add financial-datasets \
  --url "https://mcp.financialdatasets.ai/mcp"

# Execução (não há MCP para cTrader em 2026 — integração direta):
# pip install ctrader-open-api  (no container `app`)
```

**Projeto como referência conceitual:** O repositório `tradermonty/claude-trading-skills` no GitHub contém skills para Claude Code que podem inspirar nossa knowledge base:
- Market Environment Analysis (quanto capital alocar agora?)
- Position Sizing (Kelly Criterion, ATR-based)
- Technical Analyst (análise técnica completa)
- Portfolio Manager (adaptar de Alpaca para cTrader holdings)
- Sector Analysis, Macro Regime Detection
- Trade Journal (registra e analisa resultados)

### Arquitetura B — Agente Autônomo via Anthropic API

Um script Python que roda continuamente, chama a API do Claude com tool_use, e toma decisões:

```python
# PSEUDOCÓDIGO — Agente de Trading com Claude API
import anthropic
from ctrader_open_api import Client, EndPoints

client = anthropic.Anthropic()
ctrader = Client(EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_DEMO_PORT)
# autenticar app e conta via ProtoOAApplicationAuthReq + ProtoOAAccountAuthReq

# Tools disponíveis para o Claude
tools = [
    {"name": "get_market_data",    "description": "OHLCV via ProtoOAGetTrendbarsReq"},
    {"name": "get_portfolio",      "description": "Posições atuais via ProtoOAReconcileReq"},
    {"name": "analyze_regime",     "description": "Detecta bull/bear/sideways"},
    {"name": "calculate_signals",  "description": "Gera sinais de entrada/saída"},
    {"name": "execute_trade",      "description": "ProtoOANewOrderReq pela cTrader"},
    {"name": "get_news_sentiment", "description": "Analisa sentimento de notícias"},
]

# System prompt com todo o conhecimento dos livros
system_prompt = """
Você é um analista quantitativo especializado em swing trade.
Seu framework de decisão combina:
- Momentum (Clenow): ROC 90d + SMA 200 como regime filter
- Cycles (Ehlers): MAMA, Cyber Cycle, Fisher Transform
- Risk (Vince): Fractional Kelly, max drawdown 15%
- Validação (Masters): Nunca confie em backtest sem permutation test

REGRAS INVIOLÁVEIS:
1. Nunca arrisque mais de 2% do capital por trade
2. R:R mínimo de 1.5:1
3. Máximo 3 posições simultâneas com $1000
4. Se drawdown > 10%, pause e reavalie
5. Sempre explique o racional ANTES de sugerir execução

Capital atual: $1000
Modo: PAPER TRADING (NUNCA live sem aprovação explícita)
"""

# Loop de análise (roda a cada 4h ou sob demanda)
def analyze_market():
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=system_prompt,
        tools=tools,
        messages=[{
            "role": "user",
            "content": "Faça uma análise completa do mercado agora. "
                       "Avalie SPY, BTC/USDT, ETH/USDT. "
                       "Para cada ativo: regime, sinais, risk/reward. "
                       "Se houver oportunidade, sugira entrada com sizing."
        }]
    )
    # Processar tool_use calls, retornar dados reais, 
    # Claude sintetiza e recomenda
    return response
```

### Arquitetura C — Aqui no Claude.ai (mais simples, menos automação)

Você já pode usar Claude como consultor de trading AGORA:
1. Conecte o Alpha Vantage MCP nas configurações do Claude.ai
2. Pergunte: "Analise SPY para swing trade considerando momentum e ciclos"
3. Claude puxa dados reais via MCP e analisa
4. Você decide e executa manualmente

### Modelo de Decisão Humano-no-Loop (Human-in-the-Loop)

Para swing trade com capital real, a arquitetura segura é:

```
CLAUDE ANALISA → CLAUDE RECOMENDA → VICTOR APROVA → SISTEMA EXECUTA
      │                 │                  │               │
  (automático)  (com justificativa) (manual/Telegram) (cTrader Open API)
```

**Fluxo prático diário:**
1. **6h (pré-mercado):** Script roda análise automática com Claude API
2. **Claude envia via Telegram:** "📊 SPX500: Regime BULL, Cyber Cycle cruzou oversold. Sugiro LONG com 5% do capital. Stop: $XXX, TP: $YYY. R:R 2.1:1. Aprovar?"
3. **Victor responde:** "✅ Aprovado" ou "❌ Não, explique mais"
4. **Se aprovado:** Sistema executa via cTrader Open API automaticamente
5. **Fim do dia:** Claude gera relatório de performance

### Sobre Execução Automática Total (Sem Humano)

É tecnicamente possível — o projeto "Claude Prophet/Open Prophet" demonstrou isso com $100k em paper trading via Alpaca, usando Claude Code como agente autônomo que:
- Opera options multi-timeframe
- Faz scalping e hedging automático
- Armazena experiências em vector DB para aprender

**MAS** — o próprio autor alerta que não há guardrails suficientes para capital real. Para $1000 de capital inicial, o modelo human-in-the-loop é muito mais sensato.

---

## 9. Plano de Absorção dos Livros (Claude Skill/Agent) — Alimentando o Agente

### Sim, é possível criar um agent para absorver os livros!

**Abordagem recomendada:**

1. **Converter PDFs → Texto extraído** (usar PyMuPDF/pdfplumber)
2. **Criar uma Claude Skill** em `/mnt/skills/user/trading-knowledge/` com:
   - `SKILL.md` — Instruções para o agent
   - Resumos estruturados por livro (conceitos-chave, fórmulas, pseudocódigo)
   - Um banco de conhecimento indexado por tópico

3. **Workflow com Claude Code:**
   ```bash
   # O agent lê o PDF e gera um resumo estruturado
   claude "Leia o PDF do livro 'Advances in Financial ML' e extraia:
   1. Todas as fórmulas matemáticas
   2. Pseudocódigo de algoritmos
   3. Regras de trading explícitas
   4. Warnings sobre overfitting e pitfalls
   Salve em /mnt/skills/user/trading-knowledge/books/advances_fin_ml.md"
   ```

4. **Estrutura sugerida da skill:**
   ```
   /mnt/skills/user/trading-knowledge/
   ├── SKILL.md                    # Instruções do agent
   ├── books/
   │   ├── systematic_trading.md
   │   ├── advances_fin_ml.md
   │   ├── cycle_analytics.md
   │   ├── rocket_science.md
   │   └── ... (1 arquivo por livro)
   ├── strategies/
   │   ├── momentum.md
   │   ├── cycle_detection.md
   │   ├── regime_change.md
   │   └── risk_management.md
   ├── indicators/
   │   ├── ehlers_indicators.py
   │   ├── custom_momentum.py
   │   └── regime_hmm.py
   └── validation/
       ├── walk_forward.py
       ├── monte_carlo.py
       └── permutation_tests.py
   ```

5. **Ralph Loop para desenvolvimento iterativo:**
   Você já conhece o padrão — pode usar Claude Code em loop para:
   - Ler um livro → extrair conhecimento → implementar indicador → backtestear → validar → iterar

---

## 10. Nota sobre a Meta de 10% ao Mês

⚠️ **Transparência total:** 10% ao mês (~214% ao ano composto) é um target extremamente agressivo. Para contexto:

- Hedge funds top-tier (Renaissance Medallion) fazem ~66% ao ano antes de taxas
- A maioria dos traders profissionais considera 2-5% ao mês um resultado excelente
- Com $1000 de capital, as comissões e spreads podem consumir uma % significativa dos ganhos
- Leverage amplifica ganhos MAS também perdas — risco de perda total

**Abordagem realista recomendada:**
1. **Meses 1-3:** Paper trading apenas. Validar estratégia com dados reais
2. **Meta inicial:** 3-5% ao mês com drawdown máximo de 15%
3. **Scaling:** Aumentar tamanho de posição apenas após 3+ meses consistentes
4. **Capital:** Considerar que $1000 é capital de aprendizado, não renda

O sistema que estamos construindo vai te dar as ferramentas para maximizar suas chances, mas sem falsas promessas.

---

## 11. Roadmap de Implementação

### Fase 1 — Setup (Semana 1-2)
- [ ] Confirmar conta Pepperstone com plataforma cTrader (demo + live linkadas ao cTID)
- [ ] Registrar app no portal `openapi.ctrader.com` → `client_id` + `client_secret`
- [ ] OAuth bootstrap one-time na máquina local → persistir `refresh_token` no `.env`
- [ ] Obter API key Alpha Vantage (grátis, apenas para enriquecimento macro opcional)
- [ ] Setup projeto Python com uv
- [ ] Instalar: ctrader-open-api, vectorbt, backtesting, pandas-ta, scikit-learn
- [ ] Setup PostgreSQL (Docker) para armazenar market_data, trades, features
- [ ] Provisionar VPS Ubuntu (Hetzner CX22 ou Contabo VPS S, região Frankfurt/Londres)
- [ ] Configurar `docker-compose.yml` com 3 serviços: `app`, `postgres`, `grafana`
- [ ] Smoke test: `ProtoOAApplicationAuthReq` + `ProtoOAAccountAuthReq` + `ProtoOAGetTrendbarsReq` (EURUSD D1) + `ProtoOASubscribeSpotsReq` na VPS headless

### Fase 2 — Data Pipeline (Semana 2-3)
- [ ] Módulo de ingestão via cTrader Open API: `ProtoOASymbolsListReq` (universo), `ProtoOAGetTrendbarsReq` (OHLCV histórico), `ProtoOASubscribeSpotsReq` (ticks em tempo real)
- [ ] Armazenamento de OHLCV em PostgreSQL (TimescaleDB opcional)
- [ ] Scheduler para atualização periódica (APScheduler)
- [ ] Cache local para reduzir round-trips desnecessários à API
- [ ] Documentar instrumentos disponíveis da Pepperstone em `docs/instruments_pepperstone.md`

### Fase 3 — Claude como Agente (Semana 3-4)
- [ ] Instalar e configurar Claude Code com MCPs (Alpha Vantage, TradingView, Financial Datasets)
- [ ] Clonar e adaptar `claude-trading-skills` para seu contexto
- [ ] Criar system prompt com conhecimento dos livros processados
- [ ] Implementar script de análise automática via Anthropic API + tool_use
- [ ] Setup Telegram bot para receber recomendações e aprovar trades
- [ ] Testar fluxo completo: Claude analisa → recomenda → você aprova → executa

### Fase 4 — Strategy Engine (Semana 4-6)
- [ ] Implementar indicadores de Ehlers (MAMA, Cyber Cycle, Fisher Transform)
- [ ] Momentum ranking (Clenow style)
- [ ] Regime detection (SMA filter + HMM)
- [ ] Signal combiner (ensemble de sinais)
- [ ] Risk management module (position sizing, stops, drawdown guard)

### Fase 5 — Backtesting (Semana 6-8)
- [ ] Backtests com VectorBT (otimização de parâmetros)
- [ ] Walk-forward analysis
- [ ] Monte Carlo simulation para robustez
- [ ] Permutation tests para validação estatística
- [ ] Análise de drawdown e risk-of-ruin

### Fase 6 — Paper Trading com Claude Agent (Semana 8-14)
- [ ] Deploy em conta demo cTrader da Pepperstone (mesmo SDK, endpoint `demo.ctraderapi.com:5035`)
- [ ] Monitoramento via Telegram bot + Grafana
- [ ] Dashboard web simples (FastAPI + WebSocket)
- [ ] Logging detalhado de todas as decisões
- [ ] Análise semanal de performance vs backtest esperado (detecção de drift)

### Fase 7 — Live Trading (Após 3+ meses de paper)
- [ ] Transição gradual para live (começar com % pequena)
- [ ] Alertas de anomalia
- [ ] Circuit breakers automáticos
- [ ] Revisão mensal de estratégia

---

## 12. Stack Técnica Completa

```
# Ambiente
Python 3.11+
Ubuntu 24.04 (VPS headless — Hetzner CX22 ou Contabo VPS S)
PostgreSQL 16 (+ TimescaleDB extension) em container Docker
Docker + docker-compose
uv (gerenciamento de deps)

# Brokers/Execution
ctrader-open-api   # Pepperstone via cTrader Open API (Protobuf/TCP, OAuth2)
                   # Fornece: market data (OHLCV + ticks) + execução + portfolio
                   # Substitui todos os brokers anteriores (Alpaca, MT5, OANDA)

# Data (enriquecimento opcional — não crítico)
alpha_vantage      # Contexto macro + fundamentals (25 req/dia free)
pandas-ta          # 130+ indicadores técnicos
ta-lib             # Indicadores high-performance (C)

# Backtesting
vectorbt           # Backtesting vetorizado ultra-rápido
backtesting.py     # Backtesting simples e visual
                   # Nota: deploy para live é via loop Python custom + ctrader_open_api
                   # (sem StrateQueue — não há adapter cTrader em 2026)

# ML/Stats
scikit-learn       # ML clássico
hmmlearn           # Hidden Markov Models
statsmodels        # Testes estatísticos
scipy              # Otimização, estatística

# Infra
anthropic          # SDK para Claude API (agent de trading)
apscheduler        # Agendamento de tarefas
python-telegram-bot # Alertas + aprovação de trades
fastapi            # Dashboard API
sqlalchemy         # ORM para PostgreSQL

# Claude Agent / MCP
# Alpha Vantage MCP  (dados + indicadores)
# TradingView MCP    (screening + backtesting)
# Financial Datasets (fundamentals + SEC filings)
# claude-trading-skills (skills prontas)
```

---

## 13. Comandos para Setup Inicial (copiar quando estiver no PC)

```bash
# 1. Criar projeto
mkdir -p ~/projects/trading-system && cd ~/projects/trading-system
python -m venv .venv && source .venv/bin/activate

# 2. Instalar dependências principais
pip install ctrader-open-api vectorbt backtesting pandas-ta \
    scikit-learn hmmlearn statsmodels scipy \
    sqlalchemy psycopg2-binary apscheduler \
    python-telegram-bot fastapi uvicorn \
    python-dotenv rich

# 3. Instalar TA-Lib (requer lib C)
sudo apt-get install -y libta-lib-dev
pip install TA-Lib

# 4. Setup PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib
sudo -u postgres createdb trading_system
sudo -u postgres createuser trading_user -P

# 5. Criar .env
cat > .env << 'EOF'
CTRADER_CLIENT_ID=your_app_client_id
CTRADER_CLIENT_SECRET=your_app_client_secret
CTRADER_REFRESH_TOKEN=your_refresh_token_from_oauth_bootstrap
CTRADER_DEMO_ACCOUNT_ID=0000000
CTRADER_LIVE_ACCOUNT_ID=0000000
ALPHA_VANTAGE_KEY=your_key_here  # opcional — enriquecimento macro
DATABASE_URL=postgresql://trading_user:password@postgres:5432/trading_system
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EOF

# 6. Subir a stack inteira
docker-compose up -d  # containers: app, postgres, grafana
```

---

## 14. Análise do OpenProphet — Usar, Forkar ou Construir do Zero?

### 14.1 O que é o OpenProphet

Agente de trading autônomo com dashboard web, 45+ MCP tools e backend em Go. Roda em loop de heartbeat (o agente "acorda" periodicamente, analisa mercado, executa trades). Usa OpenCode CLI (não Claude Code) como runtime de AI, com Alpaca como broker.

### 14.2 Arquitetura

```
Dashboard (Node.js/Express, SSE) → Agent Server (heartbeat loop)
    → OpenCode CLI (Claude models) → MCP Server (45+ tools)
    → Go Backend (Gin, porta 4534) → Alpaca API
    → SQLite + sqlite-vec (vector search de trades passados)
```

**Stack:** Go 32% · JavaScript 40% · HTML 27% · Shell 0.4%

### 14.3 O que é BOM (vale como referência)

| Conceito | Detalhes | Aproveitável? |
|---|---|---|
| **MCP permission system** | `enforcePermissions()` com gates: blockedTools, allowLiveTrading, allowOptions, maxOrderValue, allow0DTE | ✅ Padrão de design excelente |
| **Heartbeat faseado** | Intervalos diferentes por fase de mercado (pré-market 15min, open 2min, midday 10min, close 2min, after-hours 30min) | ✅ Conceito direto |
| **Circuit breaker** | Auto-pausa quando P&L excede maxDailyLoss% | ✅ Essencial |
| **Vector DB para memória** | sqlite-vec com embeddings 384-dim para buscar trades similares passados | ✅ Ideia poderosa |
| **Agent self-modification** | Agent pode atualizar próprio prompt, strategy rules e heartbeat | ⚠️ Perigoso sem guardrails |
| **TRADING_RULES.md** | Regras de estratégia injetadas no system prompt | ✅ Padrão que já planejamos |
| **Dashboard SSE** | Streaming em tempo real de decisões, tool calls e resultados | ✅ Boa UX |
| **Multi-account** | Hot-swap de contas Alpaca (paper/live) | ✅ Útil |

### 14.4 O que é PROBLEMÁTICO (deal-breakers)

| Problema | Impacto | Severidade |
|---|---|---|
| **Licença CC BY-NC 4.0** | Proíbe uso comercial. Se você quiser monetizar (canal YouTube, vender sinais, operar para terceiros), está bloqueado legalmente | 🔴 Alto |
| **Stack incompatível** | Go + Node.js. Você trabalha com Python/Laravel/PHP. Todo o ecossistema ML (scikit-learn, VectorBT, pandas-ta, hmmlearn) é Python | 🔴 Alto |
| **Zero backtesting** | Nenhum framework de backtesting. Nenhuma validação estatística. Nenhum walk-forward, CPCV, permutation test | 🔴 Crítico |
| **Zero proteção anti-overfit** | O agente opera puramente com "vibes" do Claude. Sem validação quantitativa das decisões | 🔴 Crítico |
| **Sem crypto/forex** | Apenas Alpaca (stocks + options). Você precisa de CCXT (crypto) e MT5/OANDA (forex) | 🔴 Alto |
| **Usa OpenCode, não Claude Code** | Runtime diferente. Você precisaria aprender e manter outro toolchain | 🟡 Médio |
| **Usa Gemini para news** | Dependência de outra API de AI além do Claude, sem motivo claro | 🟡 Médio |
| **Análise técnica básica** | Apenas RSI, MACD, momentum. Sem Ehlers, sem ciclos, sem HMM, sem regime detection | 🟡 Médio |
| **SQLite** | Você já usa PostgreSQL. SQLite não escala para multi-asset com dados históricos densos | 🟡 Médio |
| **Projeto imaturo** | 6 commits, 1 contributor, 4 stars, 0 forks. Sem community, sem issues, sem releases | 🟡 Médio |
| **Sem testes** | Nenhum unit test ou integration test no repositório | 🟡 Médio |

### 14.5 O Problema Fundamental

O OpenProphet trata trading como um problema de **raciocínio de linguagem natural** — o Claude "pensa" sobre o mercado e decide. Nosso sistema trata trading como um problema de **estatística e processamento de sinais** — algoritmos quantificáveis que passam por validação rigorosa, com Claude como camada de julgamento complementar.

São filosofias opostas:

```
OpenProphet:
  Dados brutos → Claude "pensa" → Trade
  (sem validação, sem backtest, sem anti-overfit)

Nosso sistema:
  Dados brutos → Indicadores (Ehlers, momentum) → Sinais quantitativos
  → Validação CPCV/permutation → Claude audita e complementa → Trade
  (rigor estatístico + julgamento AI)
```

### 14.6 Veredicto

| Opção | Viável? | Justificativa |
|---|---|---|
| **Usar completo** | ❌ Não | Stack incompatível (Go vs Python), sem backtesting, sem anti-overfit, sem crypto/forex, licença restritiva |
| **Fork e evoluir** | ❌ Não | Reescrever o core em Python seria mais trabalho que construir do zero. O Go backend inteiro seria descartado. A arquitetura não suporta validação estatística |
| **Referência arquitetural** | ✅ Sim, seletivamente | 5-6 padrões de design valem como inspiração (ver lista abaixo) |
| **Construir do zero** | ✅ Recomendado | Python puro, com os padrões bons do OpenProphet incorporados nativamente |

### 14.7 O que Levaremos como Referência

Ao construir nosso sistema do zero em Python, incorporaremos estes conceitos do OpenProphet:

1. **Permission enforcement no MCP** — Cada tool call passa por um gate de permissões antes de executar. Implementaremos isso como um decorator Python.

2. **Heartbeat faseado** — O intervalo do loop varia conforme a fase do mercado. Implementaremos com APScheduler + calendário de mercado.

3. **Circuit breaker de daily loss** — Auto-pausa quando drawdown diário excede limite. Implementaremos como middleware no execution layer.

4. **Vector DB para memória de trades** — Embedding de trades passados para buscar setups similares. Implementaremos com pgvector (extensão PostgreSQL) em vez de sqlite-vec.

5. **TRADING_RULES.md como injeção de prompt** — Regras de estratégia em markdown injetadas no system prompt do Claude. Já está no nosso plano.

6. **Dashboard SSE** — Streaming em tempo real. Implementaremos com FastAPI + WebSocket (mais moderno que SSE).

---

## 15. Próximos Passos Imediatos

Quando você estiver no computador e abrir este arquivo:

1. **Envie este arquivo para o Claude** com o prompt:  
   _"Leia o TRADING_SYSTEM_PLAN.md e vamos começar pela Fase 1. Crie a estrutura do projeto e o setup inicial."_

2. **Para absorver os livros**, envie os PDFs um por um com:  
   _"Leia este PDF e extraia: fórmulas, algoritmos, regras de trading, e pitfalls. Salve como resumo estruturado."_

3. **Para configurar o MCP**, siga as instruções em mcp.alphavantage.co

4. **Paper trading primeiro** — sempre. Sem exceções.

---

*Este documento foi gerado como referência de planejamento. Nenhum conselho financeiro está sendo oferecido. Trading envolve risco de perda do capital investido. Teste extensivamente em paper trading antes de usar dinheiro real.*
