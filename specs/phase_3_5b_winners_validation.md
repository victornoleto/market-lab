# Spec — Phase 3.5b [PLANO B] Winners Full Validation

Validação exaustiva dos 3 winners da Phase 3 — LETF rotation EMA100/2x,
QQQ Donchian 20/10, GLD Donchian 40/20 — mais o portfolio blend 3-leg EW
que é o **alvo de produção do Plano B**. Produzir, por strategy e pelo
portfolio, um **relatório entrada/saída + tabela de métricas padrão
estilo `backtesting.py`** com **15% IR BR** aplicado em cada venda
lucrativa.

**Branch de trabalho:** `phase3.5b/winners-validation-<date>` (criar a
partir de `main` após merge do Phase 3).

**Execução:** loop autônomo `scripts/self_improve_loop.sh
CLAUDE_MODEL=claude-opus-4-7 MAX_ITER=16 SCOPE=code`. Pode rodar em
paralelo com Phase 3.5a.

---

## 0. Contexto

Phase 3 entregou 3 strategies individuais + 1 portfolio blend. O loop
aplicou os 5 gates (PBO/DSR/WF/OOS/Stress/bootstrap CI) mas:

1. **Não gerou relatório trade-a-trade** (entry/exit) para nenhuma das
   strategies. Usuário precisa auditar manualmente trades reais pra
   validar que não há bug de look-ahead, bar-alignment, etc.
2. **15% IR BR** foi modelado no Sharpe líquido a nível agregado, mas
   **não explicitado por trade** nem detalhado no relatório — usuário
   não vê o impacto real de cada venda.
3. **Tabela padrão tipo backtesting.py** (Win Rate, Profit Factor, SQN,
   Kelly, Max/Avg Drawdown Duration, etc.) **não foi produzida**.
4. **Testes de robustez extras** (real UPRO/SSO vs sintético pós-2009,
   stress 2008/2020/2022 isolados, slippage sensitivity, correlação
   rolling 252d, allocation comparativa EW/IVP/HRP) foram parciais.
5. **Confusão do usuário "3 strategies em paralelo vs 1 portfolio
   3-leg":** precisa ser resolvida e documentada na saída.

Phase 3.5b fecha esses 5 pontos. É **validação**, não busca — se algo
quebrar (p.ex. winner revela look-ahead bias), é melhor descobrir
agora do que em live.

---

## 1. Scope

### Dentro do scope

- Relatório trade-a-trade (entry/exit) por strategy, com 15% IR
  BR deduzido em cada venda lucrativa, por operação.
- Tabela padrão `backtesting.py` por strategy + pelo portfolio (ver
  §2.5 do spec Phase 3.5a — reutilizar o mesmo módulo).
- Módulo `src/ai_trade/backtest/metrics/standard_report.py` (NEW)
  compartilhado entre 3.5a e 3.5b.
- Validação de robustez: stress isolado, slippage, allocation
  alternativa, correlação rolling.
- Seção clara explicando: **"é 1 portfolio com 3 pernas, não 3
  strategies paralelas"**; mostrar como as pernas se comportariam
  stand-alone (referência), mas deixar o bottom-line = portfolio.

### Fora do scope

- Procurar novas strategies (Phase 3.5a é quem faz isso).
- Mexer em `strategies/letf_rotation.py` / `grid/portfolio_3leg.py`
  senão apenas para adicionar **hooks de report** (não alterar lógica).
- Paper trading / live — Phase 4, depois.

---

## 2. Tasks

### Task 1 — Módulo `standard_report.py` + SPY benchmark

- [ ] Criar `src/ai_trade/backtest/metrics/standard_report.py`.
- [ ] Função `build_standard_report(equity, trades, spy_series, costs)` que
      retorna `StandardReport` dataclass com **todas** as métricas da
      tabela `backtesting.py` (Start, End, Duration, Exposure Time %,
      Equity Final/Peak, Return %, Return Ann. %,
      Volatility Ann. %, CAGR %, Sharpe, Sortino, Calmar, Max/Avg
      Drawdown %, Max/Avg Drawdown Duration, # Trades, Win Rate %,
      Best/Worst Trade %, Avg Trade %, Max/Avg Trade Duration, Profit
      Factor, Expectancy %, SQN, Kelly Criterion, _strategy name).
- [ ] Função `build_spy_benchmark(spy_series, capital, window)` que calcula
      separadamente: SPY Return %, SPY CAGR %, SPY Max DD %, SPY Sharpe.
      **SPY é sempre a base de comparação** — independente do ativo da
      strategy — pedido explícito do usuário.
- [ ] Função `compare_vs_spy(strategy_equity, spy_equity)` que retorna
      `SpyComparison` dataclass: excess return, excess CAGR, delta max DD,
      information ratio (Sharpe do excesso), correlation, beta.
- [ ] Função `render_markdown(report, spy_comparison)` que emite
      **1 tabela de strategy** + **1 bloco SPY benchmark + comparação**
      no formato solicitado pelo usuário (ver §5 abaixo).
- [ ] Função `render_trade_log(trades, tax_rate=0.15)` que emite CSV +
      markdown table de entradas/saídas com colunas:
      `entry_date, entry_price, exit_date, exit_price, hold_days,
      gross_pnl_pct, gross_pnl_brl, tax_brl (15% se lucro), net_pnl_brl,
      cumulative_equity_brl`.
- [ ] SPY series: daily close do Tiingo cache (`data/tiingo/daily/SPY.csv`),
      adjusted close. Alinhar ao date range da strategy (truncar SPY para
      a janela da strategy, não o contrário).
- [ ] Testes unitários: (a) 2 synthetic trades (1 lucro, 1 prejuízo) —
      verificar IR aplicado só no lucrativo; (b) benchmark SPY com série
      sintética conhecida — verificar excess return + IR correto.
- **Conclusion:** _(preencher)_

### Task 2 — Ganchos nos 3 winners

- [ ] `strategies/letf_rotation.py`: expor `get_trades()` list of
      (entry_date, exit_date, entry_px, exit_px, asset) por switch.
- [ ] `grid/portfolio_3leg.py`: idem, para as 3 pernas (LETF, QQQ, GLD),
      com asset label por trade.
- [ ] Script `scripts/validate_phase3_winners.py` (NEW) que roda os 3
      backtests + emite os 4 relatórios (1 por leg + 1 portfolio).
- [ ] Saída em `reports/phase3_5b/<strategy>/{trade_log.csv,
      trade_log.md, standard_report.md, equity_curve.png}`.
- **Conclusion:** _(preencher)_

### Task 3 — Relatório individual LETF rotation EMA100/2x

- [ ] Trade log completo 1970-2026 (ou janela comum) com IR 15% BR por
      switch lucrativo.
- [ ] Tabela `standard_report.md`.
- [ ] Jornada `jornada/<date>-phase3.5b-letf-full-validation.md`.
- **Conclusion:** _(preencher)_

### Task 4 — Relatório individual QQQ Donchian 20/10

- [ ] Igual Task 3, com janela 2001-2026.
- [ ] Jornada correspondente.
- **Conclusion:** _(preencher)_

### Task 5 — Relatório individual GLD Donchian 40/20

- [ ] Igual Task 3, janela 2004-2026.
- [ ] Jornada.
- **Conclusion:** _(preencher)_

### Task 6 — Relatório portfolio 3-leg EW

- [ ] Trade log consolidado das 3 pernas + rebalance daily/weekly.
- [ ] Tabela standard report do portfolio (não somar métricas das pernas,
      recalcular sobre o equity consolidado).
- [ ] Deduzir 15% IR por venda lucrativa das 3 pernas individualmente
      (cada venda é evento tributável BR, não o portfolio).
- [ ] Jornada `jornada/<date>-phase3.5b-portfolio-3leg-full-validation.md`.
- **Conclusion:** _(preencher)_

### Task 7 — Robustez extra

Sub-tasks independentes (cada uma ≤ 1 iter):

- [ ] **7a Real vs synthetic UPRO/SSO.** Re-rodar LETF rotation substituindo
      sintético pós-2009 por UPRO real (dados Tiingo). Comparar Sharpe/CAGR
      e ver desvio. Documentar drag real vs modelado.
- [ ] **7b Stress isolado.** Sub-períodos 2008-2009 (crise), 2020-03
      (COVID crash), 2022 (bear + rate hikes), 2025-Q1 stress. Sharpe e
      drawdown por sub-período por strategy.
- [ ] **7c Slippage sensitivity.** Emitir tabela Sharpe/CAGR a 0 bps,
      1 bps, 5 bps, 10 bps de slippage round-trip.
- [ ] **7d Allocation alternativa.** Re-rodar o 3-leg com weights
      EW / IVP / HRP (já testados) + Risk-Parity simples + Min-Variance.
      Comparar e decidir se EW continua sendo o default (já é o PASS).
- [ ] **7e Correlação rolling.** Plotar ρ 63d e 252d entre as 3 legs.
      Identificar períodos de alta correlação (quando a diversificação
      quebra) e documentar.
- [ ] **7f Position sizing alternativo.** Testar vol-target 10% no
      portfolio e comparar com EW cash-neutral.
- **Conclusion (por sub-task):** _(preencher)_

### Task 8 — Allocation & multi-strategy clarification

- [ ] Documento `docs/phase3_winners_allocation.md` (NEW) respondendo
      a dúvida do usuário:
      - **"São 3 strategies paralelas?" → NÃO.** O alvo de produção é
        **1 portfolio com 3 pernas EW a 33.3% cada**. O usuário vê 3
        ordens simultâneas (1 por perna) mas é 1 allocation decision.
      - **Alternativas documentadas:** rodar só LETF (CAGR maior 41%
        mas Sharpe menor); rodar 3 pernas como 3 contas separadas (não
        recomendado — perde o benefício de rebalance).
      - **Proporção no capital total:** Plano B ocupa 20-40% do capital
        ativo (mandate rule 1). Dentro de Plano B → 100% no portfolio
        3-leg. O 33% EW é só dentro do portfolio, não do capital total.
- [ ] Exemplo numérico: $10k capital total com 30% em Plano B → $3k no
      portfolio → $1k em cada perna.
- **Conclusion:** _(preencher)_

### Task 9 — Summary Phase 3.5b

- [ ] Jornada `jornada/<date>-phase3.5b-full-validation-summary.md` com:
      verdict final (strategies confirmadas ou anomalies detectadas),
      links para os 4 relatórios, link para `phase3_winners_allocation.md`.
- [ ] Flip memory.md `status: done`.
- **Conclusion:** _(preencher)_

---

## 3. Gates e regras invioláveis

- **Pytest baseline:** 550 passed. Não pode quebrar.
- **NÃO alterar a lógica das strategies** — só adicionar hooks de
  export (`get_trades()`) ou novos módulos de report.
- **IR 15% BR** aplicado **por venda lucrativa**, não a agregado de ano.
  Perdas não compensam no modelo (o real BR compensa dentro do mês,
  mas simplificar para worst-case).
- **Swap = 0** (Plano B, broker BR não tem swap).
- **Citação obrigatória** nas decisões técnicas.
- **Winners imutáveis** — se alguma anomaly for detectada, documentar
  em jornada com tag `⚠️ FLAG` mas **não reverter** o PASS do Phase 3
  sem discussão com usuário.

---

## 4. Budget & ETA

- **Iter budget:** 16 iters cap.
- **Tempo estimado:** ~4-5 horas com Opus 4.7.
- **Paralelização com Phase 3.5a:** sim — branches + scripts separados,
  ambos leem `data/tiingo/` read-only.

---

## 4.5 Template de saída (obrigatório por strategy + portfolio)

Cada `reports/phase3_5b/<strategy>/standard_report.md` deve ter exatamente
este formato:

```
# <Strategy name + params>

## Metrics
Start                     YYYY-MM-DD HH:MM:SS
End                       YYYY-MM-DD HH:MM:SS
Duration                   XXXX days HH:MM:SS
Exposure Time [%]          ..
Equity Final [$]           ..
Equity Peak [$]            ..
Return [%]                 ..
Return (Ann.) [%]          ..
Volatility (Ann.) [%]      ..
CAGR [%]                   ..
Sharpe Ratio               ..
Sortino Ratio              ..
Calmar Ratio               ..
Max. Drawdown [%]          ..
Avg. Drawdown [%]          ..
Max. Drawdown Duration     .. days
Avg. Drawdown Duration     .. days
# Trades                   ..
Win Rate [%]               ..
Best Trade [%]             ..
Worst Trade [%]            ..
Avg. Trade [%]             ..
Max. Trade Duration        .. days
Avg. Trade Duration        .. days
Profit Factor              ..
Expectancy [%]             ..
SQN                        ..
Kelly Criterion            ..
_strategy                  <params>

## SPY Buy & Hold Benchmark (same window, same starting capital)
SPY Return [%]             ..
SPY CAGR [%]               ..
SPY Max. Drawdown [%]      ..
SPY Sharpe Ratio           ..

## Strategy vs SPY
Excess Return [%]          .. (strategy − SPY)
Excess CAGR [%]            ..
Delta Max DD [%]           .. (strategy − SPY; negativo = strategy mais segura)
Information Ratio          ..
Correlation (daily)        ..
Beta vs SPY                ..
```

---

## 5. Output artifacts

Ao fim, o repo deve ter:

```
reports/phase3_5b/
  letf_rotation/
    trade_log.csv
    trade_log.md
    standard_report.md
    equity_curve.png
  qqq_donchian/
    ...
  gld_donchian/
    ...
  portfolio_3leg/
    trade_log.csv (consolidado)
    standard_report.md
    equity_curve.png
    correlation_rolling.png
    allocation_comparison.md   # EW vs IVP vs HRP vs RP vs MV

docs/
  phase3_winners_allocation.md  # ★ resposta da dúvida do usuário

jornada/
  <date>-phase3.5b-letf-full-validation.md
  <date>-phase3.5b-qqq-donchian-full-validation.md
  <date>-phase3.5b-gld-donchian-full-validation.md
  <date>-phase3.5b-portfolio-3leg-full-validation.md
  <date>-phase3.5b-robustness-extras.md
  <date>-phase3.5b-full-validation-summary.md

src/ai_trade/backtest/metrics/standard_report.py  # ★ reusável

scripts/validate_phase3_winners.py
```
