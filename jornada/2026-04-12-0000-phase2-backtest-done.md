# 2026-04-12 — Phase 2 concluída (motor de backtest)

Delivery completo do módulo de backtest em `src/ai_trade/backtest/`:
data layer (yfinance + Wikipedia SPX point-in-time), engine
(portfolio + execução CFD-aware + runner), validação (CPCV / PBO /
DSR / walk-forward / MCPT), métricas (Sharpe / Sortino / Calmar /
CAGR / DD / VaR) e gerador de relatório (MD + PNG). Clenow
`stocks_on_the_move` replicado end-to-end como estratégia de
calibração. **173 testes verdes.** Disclaimer de survivorship
obrigatório em todo relatório.
