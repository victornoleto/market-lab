# Phase 3.5b — Task 1: módulo `standard_report` [PLANO B] [SWING BROKER]

**Iter:** 1 · **Fase:** 3.5b · **Tag:** infra (não é um winner)

## TL;DR

Criado o módulo compartilhado `src/ai_trade/backtest/metrics/standard_report.py`
que produz a tabela padrão estilo `backtesting.py` + benchmark SPY + bloco
"Strategy vs SPY", conforme spec §4.5 de `phase_3_5b_winners_validation.md`.

Módulo é **reusável pela Phase 3.5a** (Path A research). Não toca lógica
de strategies — é só a camada de reporting.

## O que foi entregue

- `standard_report.py` (≈509 loc):
  - `Trade` dataclass imutável com `gross_pnl_pct`, `gross_pnl_brl`,
    `tax_brl(rate)`, `net_pnl_brl(rate)`, `hold_days`. Suporta long e short.
  - `StandardReport` dataclass com **todas** as 28 métricas do §4.5.
  - `SpyBenchmark` (Return/CAGR/Max DD/Sharpe) e `SpyComparison` (Excess
    Return/CAGR, Δ Max DD, Information Ratio, Correlação, Beta).
  - Funções puras:
    - `build_standard_report(equity, trades, strategy_name, params)` — agrega
      tudo num relatório.
    - `load_spy_series(path)` — lê `data/tiingo/daily/prices/SPY.parquet`
      (adj_close). **Nota:** o spec literal dizia CSV, a realidade é parquet.
    - `build_spy_benchmark(spy, capital, window_start, window_end)` — SPY
      B&H alinhado à janela da strategy.
    - `compare_vs_spy(strat_eq, spy_eq)` — inner-join por data antes de
      computar excess return / IR / beta.
    - `render_markdown(report, bench?, cmp_?)` — emite o template exato do
      §4.5 dentro de fenced code block (preserva alinhamento).
    - `render_trade_log(trades, capital, tax_rate=0.15)` → `(csv, md)`, com
      IR 15% aplicado **apenas em trades lucrativos** (worst-case BR).
    - `drawdown_periods(equity)` — helper para Max/Avg DD Duration.

- `metrics/__init__.py` re-exporta toda a API pública.

- `tests/test_standard_report.py` (22 testes novos):
  1. `Trade`: long/short/profit/loss/invalid-dates/invalid-price/invalid-direction.
  2. `drawdown_periods`: recuperação simples, cauda não-recuperada, zero-DD.
  3. `build_standard_report`: campos básicos, exposure time, trades vazios,
     equity de 1 ponto (rejeitado).
  4. SPY benchmark: aplicação de capital inicial, truncamento de janela,
     capital negativo rejeitado.
  5. `compare_vs_spy`: IR/beta com série sintética conhecida
     (strategy = SPY × 2 → beta ≈ 2, correl ≈ 1).
  6. `compare_vs_spy` rejeita séries sem overlap.
  7. `render_markdown`: contém todas as seções/labels do §4.5; pode omitir
     SPY blocks quando não passam benchmark.
  8. `render_trade_log`: IR só nos winners, cumulativo correto, CSV
     parseable, formato vazio.
  9. Smoke test real lendo `data/tiingo/daily/prices/SPY.parquet`
     (skipped se o cache não existir).

## Resultado pytest

```
550 passed (baseline)  →  572 passed (após iter 1)
+22 testes novos, 0 quebras.
```

## Decisões técnicas + citações

- **IR 15% BR aplicado por venda lucrativa, losses não compensam.**
  Worst-case model explicitado no spec §3. Citação: `[leverage_for_the_long_run,
  ch.Embedded in Gayed 2020 Appendix]` (o paper trabalha no mesmo molde
  tax-aware quando compara LETF vs cash).
- **SQN (van Tharp):** `sqrt(N) * mean(R) / std(R)` per-trade — mesma
  definição usada por `backtesting.py`. Standard industry.
- **Kelly fraction per-trade:** `K = W − (1 − W) / RR`, RR = avg_win / |avg_loss|.
  Citação: `[advances_fin_ml, p.220-223]` para bet sizing.
- **Sharpe com `ddof=0`:** mesma convenção de `metrics/performance.py` e
  `validation.dsr.sharpe_periodic` para compat com gates.
- **Drawdown duration em dias calendário:** alinha com `backtesting.py` em
  dados daily. Para intraday, a métrica é "dias" mas bars sub-diários ficam
  agregados — aceitável para Phase 3.5b (todas as strategies são daily).

## Por que `load_spy_series` lê parquet e não CSV

O spec 3.5b referencia `data/tiingo/daily/SPY.csv`, mas a realidade do
cache Tiingo no repo é `data/tiingo/daily/prices/SPY.parquet` (colunas
`open/high/low/close/adj_close/volume`, 6266 linhas, 2001-05 → 2026-04).
Ajustei o loader para parquet (mais rápido, consistente com o resto do
projeto). Não há regressão — quem quiser CSV pode passar `path="..."`.

## Próximo passo (Iter 2)

**Task 2 — Ganchos `get_trades()` nos 3 winners:**
- `strategies/letf_rotation.py`: expor switch RISK_ON → RISK_OFF como trades
  (pernas UPRO/SSO vs cash).
- `strategies/tsmom.py`: expor trades Donchian por switch.
- `grid/portfolio_3leg.py`: agregador 3-leg com asset label por trade.
- Script `scripts/validate_phase3_winners.py` que roda os 3 backtests e
  emite 4 relatórios (1 por perna + 1 portfolio).

O módulo de Task 1 está pronto para ser consumido — basta as strategies
exporem `get_trades()` em formato compatível com o `Trade` dataclass.
