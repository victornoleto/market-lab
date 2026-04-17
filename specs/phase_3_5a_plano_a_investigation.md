# Spec — Phase 3.5a [PLANO A] Investigation

Continuar a busca de uma strategy viável para **Plano A (Pepperstone CFD
short-hold, cTrader)** que supere Plano B com folga, respeitando a
hierarquia de retorno **A > B > C** imposta pelo mandate.

**Branch de trabalho:** `phase3.5a/plano-a-short-hold-<date>`
(criar a partir de `main` após merge do Phase 3).

**Execução:** via `scripts/self_improve_loop.sh` em loop autônomo com
`CLAUDE_MODEL=claude-opus-4-7 MAX_ITER=20 SCOPE=code`. Pode rodar em
paralelo com Phase 3.5b (branches isoladas, sem conflito).

---

## 0. Contexto

Phase 3 fechou com:
- **Plano A:** apenas BollingerMR GARCH SPY 1h (CAGR ~5.9%/ano, abaixo CDI).
  Expansão via A1 (leverage sweep) e A3a (transport) FALHOU: edge SPY-only,
  L=2 único nível de alavancagem que passa gates e ainda fica < CDI.
- **Plano B:** 3-leg blend {LETF+QQQ+GLD} com **CAGR 29%/ano OOS**,
  Sharpe 2.25.

Resultado: **Plano A rendendo menos que Plano B viola o mandate** (A é
o bucket mais arriscado — alavancagem, swap, cTrader, CFD — precisa
compensar com retorno maior). Phase 3.5a corrige esse gap.

Principais hipóteses para explicar a falha do Plano A:
1. **Universo restrito.** Só testamos 5 ETFs equity + crypto BTC/ETH via
   Tiingo IEX 1h. Pepperstone opera principalmente **FX majors** (EURUSD,
   GBPUSD, USDJPY, AUDUSD, etc) + **índices CFD** (SPX500, NAS100,
   DE40, UK100) + **commodities CFD** (XAUUSD, XAGUSD, WTI). Nenhum
   desses foi testado até aqui.
2. **Edge tipo "mean-reversion"** talvez não seja o mais adequado para
   short-hold — momentum intraday, breakout e event-driven podem ter
   edges mais naturais em CFD com leverage baixa.
3. **Frequência.** Tiingo IEX 1h pode ser lenta demais. 15m ou 5m podem
   revelar edges microstructure-based.

---

## 1. Scope

### Dentro do scope

- **Task 0 (pré-req):** Pull Tiingo FX majors + índices + commodities
  daily e intraday (1h mínimo, 15m se retention permitir).
- Testar ≥ 6 novas combinações (strategy × universe × frequency) via grid
  + 5-gate framework, todas com median hold ≤ 5 days (swap ≤ 0.13 SR/yr
  `[systematic_trading, p.185-188]`).
- Rebalancear meta de CAGR do Plano A para um número **tangível** e
  ainda **acima do Plano B**.
- Documentar pelo menos 2 winners NOVOS ou 1 winner + explicação honesta
  do porquê Plano A não suporta retorno > B (seria pivot material do
  mandate).
- Emitir o **standard metrics table** (§2.5 abaixo) para qualquer winner.

### Fora do scope

- Re-testar o BollingerMR SPY 1h atual (já é baseline conhecido).
- Modificar código de produção dos winners Path B (imutáveis).
- Mexer no `docs/investment-mandate.md` sem um jornada de override §7.
- Paper/live trading — Phase 4, fora.

---

## 2. Tasks

Cada task = 1+ iteração do loop. Checkbox + campo **Conclusion** por task.

### Task 0 — Tiingo FX/índices/commodities pull (pré-req crítico)

- [ ] Extend `scripts/tiingo_bulk.py` (ou criar `tiingo_bulk_fx.py`) para
      puxar: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, NZDUSD, USDCHF
      (forex) + SPX500, NAS100, US30, DE40, UK100, JP225 (índices via
      tickers Tiingo proxy) + XAUUSD, XAGUSD (gold/silver FX).
- [ ] Daily: longest window possível.
- [ ] Intraday: 1h primário, 15m se Tiingo permitir.
- [ ] Update `manifest.json` no formato atual.
- [ ] Smoke check: `_filter_orphan_intraday_bars` ativo; zero bars em
      días fechados.
- **Conclusion:** _(preencher com tickers baixados + sizes + ETA)_

### Task 1 — BollingerMR multi-asset FX/commodities 1h

- [ ] Rodar BollingerMR canonical (20, 2σ) no grid FX daily + 1h (longest
      window) + commodities 1h.
- [ ] Gate 5-layer + median hold ≤ 5 days.
- [ ] Se PASS em qualquer ticker → candidate Plano A.
- [ ] Se 0/N PASS → marcar como dead end, próxima task.
- **Conclusion:** _(preencher)_

### Task 2 — Breakout/momentum intraday (Donchian 1h / ATR breakout)

- [ ] Testar Donchian 10/5 e 20/10 em 1h sobre FX majors + índices CFD.
- [ ] Testar ATR-channel breakout (Kaufman/Chandelier) 1h.
- [ ] Citar `[trading_systems_methods, p.353]` (Donchian) e
      `[volatility_trading]` (ATR).
- [ ] Gate 5-layer + hold ≤ 5 days + swap cost modelado per-hold-day.
- **Conclusion:** _(preencher)_

### Task 3 — Intraday pairs / stat-arb

- [ ] Cointegração (ADF + Engle-Granger) em pares óbvios: EURUSD/GBPUSD,
      USDJPY/USDCHF, SPX500/NAS100.
- [ ] Se cointegrados → Kalman pair-trade 1h ou 15m.
- [ ] Gate 5-layer + hold ≤ 5 days.
- [ ] `[machine_trading, Chan]` para Kalman + `[advances_fin_ml, ch.7]`
      para CPCV.
- **Conclusion:** _(preencher)_

### Task 4 — Session-based FX strategies

- [ ] Testar estratégias de sessão (London open breakout, NY close MR,
      Asian range fade) em EURUSD/GBPUSD 1h.
- [ ] Citar `[quantitative_trading, Chan]` ou outro livro que trate
      sessões FX explicitamente (consultar `books/summaries/` antes).
- [ ] Gate 5-layer + hold intra-session (≤ 24h).
- **Conclusion:** _(preencher)_

### Task 5 — Gold/BTC news-regime filter (hybrid)

- [ ] Sobrepor filtro de regime (VIX para equity CFD, DXY para FX, BTC
      dominance para crypto) no BollingerMR SPY já existente.
- [ ] Avaliar se MR edge sobrevive + se a filtragem reduz hold-time
      (mantendo ≤ 5 days).
- [ ] `[advances_fin_ml, ch.17]` regime-aware features.
- **Conclusion:** _(preencher)_

### Task 6 — Rebalance meta Plano A

- [ ] Com os resultados das Tasks 1-5, calcular o **máximo CAGR
      sustentável** de Path A (CAGR do melhor candidate × ajuste para
      risco real com leverage viável).
- [ ] Definir **meta nova Plano A** respeitando A > B = 29%.
      Sugestão: **40-60%/ano CAGR** (≈ 3-4%/mês), acima de Plano B
      mas abaixo da pretensão original inviável de 5-10%/mês.
- [ ] Atualizar `docs/investment-mandate.md` §7 (override) + criar
      jornada documentando o re-target.
- **Conclusion:** _(preencher)_

### Task 7 — Summary Phase 3.5a

- [ ] Jornada `jornada/<date>-phase3.5a-plano-a-summary.md` com:
      lead-by-lead verdict, tabela de candidates testados, meta rebalanced,
      decisão GO/NO-GO por strategy, gap aberto para Phase 4.
- [ ] Flip memory.md `status: done`.
- **Conclusion:** _(preencher)_

---

## 2.5 Standard metrics table + SPY benchmark (output obrigatório por strategy winner)

Todo candidate que passa os gates deve emitir **1 tabela de métricas no
formato `backtesting.py`** + **1 bloco de comparação de benchmark vs
SPY buy&hold** (pedido explícito do usuário — **SPY é a base de
comparação de TODA strategy, não o ativo subjacente**).

**Tabela padrão:**

```
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
_strategy                  <nome + params>
```

**Bloco benchmark SPY (fixo, vai depois da tabela):**

```
SPY Buy & Hold (same window, same starting capital):
  SPY Return [%]           ..
  SPY CAGR [%]             ..
  SPY Max. Drawdown [%]    ..
  SPY Sharpe Ratio         ..

Strategy vs SPY:
  Excess Return [%]        .. (strategy − SPY)
  Excess CAGR [%]          ..
  Delta Max DD [%]         .. (strategy − SPY; negativo = melhor)
  Information Ratio        .. (Sharpe do excesso vs SPY)
  Correlation (daily)      ..
  Beta vs SPY              ..
```

Implementar em `src/ai_trade/backtest/metrics/standard_report.py` (NEW),
reutilizado pela Task 2 do Phase 3.5b. **Deduzir swap + spread
Pepperstone** em toda linha de equity (não só no Sharpe líquido).
O benchmark SPY usa os mesmos custos de Plano B (15% IR apenas no
exit final do buy&hold — por ser 1 venda no fim do período).

---

## 3. Gates e regras invioláveis

- **Median hold ≤ 5 days** (swap kills alpha — `[systematic_trading, p.185-188]`).
- **5-gate framework:** PBO<0.5 + DSR p<0.05 + WF≥6/8 + single-block OOS >0 +
  forward-stress >0 + bootstrap 99.9% CI low > 0.
- **Citação obrigatória** em toda decisão técnica (CLAUDE.md regra 2).
- **Custos Pepperstone modelados:** spread Razor (~0.1 pip EURUSD) +
  $3.50/side commission + **swap diário** (long/short assimétrico).
- **Pytest baseline:** 550 passed (após Phase 3). Não pode quebrar.
- **Winners Phase 3 imutáveis** — Phase 3.5a é EXTENDS, não modifica
  `strategies/letf_rotation.py` / `grid/portfolio_3leg.py` / infra B.

---

## 4. Budget & ETA

- **Iter budget:** 20 iters cap (loop `MAX_ITER=20`).
- **Tempo estimado:** ~5-7 horas autônomas com Opus 4.7.
- **Paralelização com Phase 3.5b:** sim — branches separadas, sem shared
  state além do Tiingo cache (read-only em `data/tiingo/`).
