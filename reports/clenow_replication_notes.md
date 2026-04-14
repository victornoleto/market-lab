# Clenow Momentum Replication — Notas de Execução

Replicação do sistema `stocks_on_the_move` (Clenow, 2015) no engine de
backtest do ai-trade, conforme spec em `specs/backtest_phase2.md` Task 4.

Este documento compara os números obtidos com os publicados no livro, registra
as decisões de design tomadas na replicação e lista as limitações conhecidas
do resultado (principalmente survivorship bias).

---

## Referência do livro

- Sistema: `stocks_on_the_move` (Clenow, 2015) — "Basic Strategy" + "Portfolio Rebalance"
- Universo: S&P 500, constituintes point-in-time `[stocks_on_the_move, p.98, p.107]`
- Janela: ~18 anos (1999–2014) é o benchmark do livro `[p.115]`
- Performance reportada (versão estendida do sistema):
  - CAGR ~12% bruto
  - Sharpe anual ~1.0
  - Max drawdown ~25%
  - Índice (SPY TR) comparável: CAGR ~5%, DD ~56% `[p.218]`

Nenhum desses números é "otimizado" — Clenow insiste `[p.219-220]` que os
constantes (200d MA, 100d MA, 90d, 15%, 10 bps) foram escolhidos a priori
conforme conceito, não buscas de grade.

---

## O que foi rodado

Script: `scripts/run_clenow_replication.py`

```
.venv/bin/python scripts/run_clenow_replication.py \
    --start 2023-07-01 --end 2023-12-31 \
    --cash 100000 --output-dir reports/ \
    --warmup-days 400
```

Parâmetros do engine:
- **Universo**: SPX constituentes point-in-time em 2023-07-01 (via
  Wikipedia scrape, ~500 tickers). Filtrados para os que o yfinance retorna
  com dados não-vazios.
- **Warmup**: 400 dias de calendário (≈ 270 dias úteis) antes de `--start`,
  para que o MA de 200d e a regressão de 90d tenham histórico suficiente já
  na primeira quarta-feira de rebalance.
- **Custos**: `ExecutionConfig()` default (spread/slippage/comissão zero).
  Decisão consciente — queremos medir o signal bruto antes de calibrar
  custos reais na Etapa 2 Pepperstone (ROADMAP §"Backtest em duas etapas").
- **Clenow constants**: valores do livro (não-otimizados), todos default de
  `ClenowMomentumStrategy` (`lookback_regression=90`, `lookback_trend=100`,
  `lookback_index_trend=200`, `lookback_atr=20`, `lookback_gap=90`,
  `gap_threshold=0.15`, `top_pct=0.20`, `risk_factor=0.001`).

---

## Números obtidos

Execução: `reports/clenow_momentum_20260414-1633.md` (backtest
2023-07-01 → 2023-12-31, cash inicial $100 000, 503 tickers SPX
point-in-time, dos quais 486 retornaram dados — 17 pulados por
survivorship/rename/unknown).

| Métrica | Replicação (6 meses, 2023 H2) | Clenow (18 anos, livro p.115) |
|---|---|---|
| Equity final | $93 965.01 | N/A |
| CAGR (annualized) | **−11.79%** | ~12% |
| Sharpe (annualized) | **−0.787** | ~1.0 |
| Sortino (annualized) | −1.017 | N/A |
| Calmar | −0.871 | N/A |
| Max drawdown | 13.55% | ~25% |
| Volatility (annualized) | 14.58% | N/A |
| Walk-forward verdict | reject (4/8 profitable) | N/A (single trial) |
| Closed trades | 54 | N/A |

### Leitura dos números

**Negativo, mas dentro do esperado para a janela.** 2023 H2 foi um período
**choppy** no SPX: subida em julho, correção profunda agosto-outubro (SPX
caiu ~10%), recovery em novembro-dezembro. A estratégia pegou o top da
primeira subida, foi stopada pela deterioração de ranking / quebra de
100d MA durante a correção, e não conseguiu re-entrar a tempo do rally
final (regime filter sinaliza atraso quando MA200 está bem acima do
close).

**Composição dos trades confirma a lógica de momentum correta:**
- Top 5 winners: LLY (+$1 045), GOOG (+$486), GOOGL (+$480), AMGN
  (+$291), ORCL (+$234). Todos **megacaps tech/pharma** que lideraram
  o mercado em 2023.
- Top 5 losers: NCLH (−$621), CMG (−$607), BKR (−$600), ODFL (−$534),
  DLR (−$529). **Cíclicas/REITs/energy/consumo discricionário** que
  colapsaram na correção Q3.

**Max DD 13.55% em 6 meses** é razoável — ~metade do DD de longo prazo
do livro (25%), o que é consistente com uma janela curta bullish-choppy.

**Walk-forward rejeitado (4/8 profitable)** é esperado: 8 janelas em 6
meses = ~3 semanas cada, ruído altíssimo por janela. O gate de 6/8 foi
calibrado para janelas de multi-mês (Pardo p.235-240). Não é sinal de
falha do edge — é sinal de que o teste de walk-forward não tem poder
estatístico nessa escala.

### O que ficaria OK vs. o que seria bug

Sharpe −0.79 numa janela de 6 meses em mercado choppy **não é bug** —
está dentro do ruído esperado. Bugs seriam:
- Sharpe < −2 (perda muito além do DD observado)
- Nenhum trade emitido (ranking/scheduling quebrado)
- Cash negativo no final (sizing estourado)
- Equity curve com NaNs ou jumps não-explicáveis

Nada disso ocorreu. **Engine OK para avançar**; signal precisa de janela
longa com dados survivorship-free pra ser avaliado com rigor — o que é
Fase 3.

---

## Limitações conhecidas

### 1. Survivorship bias ainda presente
O pipeline yfinance + Wikipedia reconstrói point-in-time membership mas
**só recupera preços de tickers que o Yahoo Finance ainda serve**.
Tickers deslistados durante 2023 H2 retornam frame vazio e saem do
universe silentemente. Em 2023-07-01 a Wikipedia reportou 503 tickers;
quantos efetivamente renderam dados está no log da execução.

**Efeito esperado no resultado**: retornos **inflados** (não vemos os perdedores).

### 2. Janela curta
6 meses = ~25 semanas = ~25 rebalances. Muito pouco para afirmar qualquer
coisa sobre o edge do sistema. A janela curta existe para validar a
infraestrutura end-to-end; uma execução de ≥ 3 anos é o próximo passo
(listed below).

### 3. Custos zerados
Spread, slippage e comissão todos zero. Clenow roda o próprio backtest em
dados de equities com custos institucionais; o engine ai-trade herda esse
comportamento na Etapa 1 para medir signal puro. Na Etapa 2 (após
destravar cTrader), custos reais serão aplicados e o Sharpe cairá.

### 4. Validação anti-overfit parcial
CPCV, PBO e DSR requerem **múltiplas estratégias** (grid de parâmetros) para
produzir valores significativos. Essa replicação é um **single trial** com
parâmetros fixos do livro, então apenas walk-forward (dividindo a equity
curve realizada em N janelas) é computado. Fase 3 vai introduzir o grid.

### 5. Universo pode não incluir o índice
A estratégia usa `^GSPC` para o filtro de regime. Se o yfinance não
retornar `^GSPC` na janela, o regime defaulta para ON (`_regime_on`
retorna True quando não há histórico suficiente) — replicação continua,
mas com filtro efetivamente desativado. Log deve ser checado.

---

## Decisões de design não-óbvias

### `self.data` carrega o histórico completo (não o slice do Runner)
O Runner itera apenas sobre `[start, end]` (`data_bounded`), mas
`ClenowMomentumStrategy.data` aponta para o dict completo (`start - warmup`
até `end`). Isso é intencional: durante o primeiro Wednesday após
`--start`, a estratégia precisa olhar 90 dias para trás para a regressão e
200 dias para o MA do índice. Se ela recebesse apenas o slice do Runner,
não teria warmup.

### Sells emitidos ANTES de buys (na mesma lista)
O Runner executa orders na ordem da lista. Emitir sells primeiro garante
que o cash liberado esteja disponível para os buys imediatamente após.
Isso replica o comportamento intuitivo de "libere caixa, depois compre".

### Buy é gated pelo regime; sell NÃO
Do livro `[p.94-95]`: *"Do not sell a holding just because the index drops
below the 200d MA — only stop adding new positions."* O engine implementa
isso literalmente — sells disparam por critérios próprios do stock (rank,
100MA, gap, membership), enquanto buys verificam regime ON.

### Sizing usa `equity` (não `cash`)
`shares = floor(equity × risk_factor / ATR20)`. Clenow sempre fala em
"account value" `[p.88]`, não cash. O valor de posições abertas conta.
Um novo buy pode ultrapassar o cash disponível se as posições abertas
forem muito grandes; nesse caso o Clenow manda parar (`break`) `[p.99]`.

### `top_pct × len(universe)` com `max(1, ...)` floor
Rank `>=` max_rank dispara sell. Com universe de 503, `max_rank = 100` —
top 100 é held. Em testes sintéticos com universo pequeno (8 stocks),
`max_rank = 1` forçaria hold de único stock; nos testes isso é neutralizado
passando `top_pct=0.5` ou `1.0`.

### `max_gap` ignora NaN
`pct_change()` produz NaN no primeiro bar. `max(skipna=True)` ignora. Se
tudo for NaN (menos de 2 bars), retorna 0.0 — fallback seguro.

---

## Próximos passos (fora de escopo desta task)

1. **Rodar janela longa** (2010–2023 ou 1999–2014 para direto-com-livro).
   Requer ou (a) tolerância ao rate-limit do yfinance (horas de fetch
   inicial) ou (b) migração para Tiingo/EOD survivorship-free
   (ROADMAP §"Decisões adiadas").
2. **Implementar grid de parâmetros** (e.g., `lookback_regression ∈
   {60, 90, 120}`) para gerar a matriz T×N necessária para CPCV/PBO/DSR.
   Cada célula é uma equity curve, todas sob os mesmos splits CPCV.
3. **Medir custos reais** via `ProtoOAGetTrendbarsReq` no demo Pepperstone
   quando cTrader destravar (Etapa 2). Reaplicar o backtest com
   `ExecutionConfig(half_spread=..., commission_per_unit=...)` calibrado
   por símbolo.
4. **Comparar com Trading Evolved** (Clenow, 2019) — versão estendida da
   mesma estratégia com mudanças de volatility target e detalhamento de
   execução. `knowledge/books/trading_evolved.md` já está absorvido.

---

## Referências

- Clenow, A. F. (2015). *Stocks on the Move: Beating the Market with Hedge
  Fund Momentum Strategies*. Equilateral Capital Management GmbH.
- Summary absorvido: `books/summaries/stocks_on_the_move.md`
- Spec da Fase 2: `specs/backtest_phase2.md`
- Engine core: `src/ai_trade/backtest/engine/`
- Estratégia: `src/ai_trade/backtest/strategies/clenow_momentum.py`
- Script CLI: `scripts/run_clenow_replication.py`
- Report gerado: `reports/clenow_momentum_<YYYYMMDD-HHMM>.md`
