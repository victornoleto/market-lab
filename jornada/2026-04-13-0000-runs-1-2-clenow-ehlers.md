# 2026-04-13 — Phase 2.5 Runs 1-2 (Clenow + Ehlers grids)

**O que aconteceu:**
- **Run 1 (Clenow grid):** 30 configurações do momentum de Clenow sobre
  SPX 2015-2023 (yfinance). Gates falham: PBO=0.524, DSR 0/30, WF 4/30.
  Melhor config: #15 (lookback 90d, top 20%, risk 0.2%) com Sharpe 0.58,
  CAGR 8.87%. **Underperforma SPY buy-and-hold.**
- **Run 2 (Ehlers Band-Pass Swing grid):** 24 configs em ^GSPC single-
  instrument. **PBO=0.468 passa** (estruturalmente menos overfit que
  Clenow), DSR 0/24 falha. Melhor: #6 (hp=48, lp=20, pct=0.80) Sharpe
  0.31 CAGR 2.17%.
- **Achado crítico:** Clenow × Ehlers têm correlação de equity curves
  ≈ −0.01. **Estratégias ortogonais.** Candidatas pra portfolio
  regime-aware no futuro.
