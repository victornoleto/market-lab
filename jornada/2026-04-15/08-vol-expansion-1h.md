# 2026-04-15 (noite tarde) — ❌ Vol-Expansion Breakout SPY+GLD+TLT 1h: FAIL

**Tese:** Donchian channel breakout `[trading_systems_methods, p.353]`
filtrado por Yang-Zhang volatility cone `[volatility_trading, p.20-23,
p.58-60]`, com sizing via Carver vol-targeting Half-Kelly
`[systematic_trading, p.144, p.159]`. Mecânica: quando realized vol (YZ)
está no bottom-third do cone histórico (≤33rd percentile) E preço rompe
canal Donchian → entra na direção do breakout. 3 exit conditions:
opposite channel, 48h hard cap, 4σ disaster stop `[systematic_trading,
p.212]`.

**Bundle:** γ — SPY + GLD + TLT (ETF IEX 1h, 6y de dados, sessão
uniforme). Bundle β original (SPY + XAU/USD + EUR/USD) abortado na
pre-flight: Tiingo FX 1h tem gap massivo (2021-06→2025-01) tornando CPCV
inviável.

**Grid:** 4 configs (N_entry ∈ {20, 55} × N_exit ∈ {10, 20}) × 3 ETFs
= 12 trials. 5 parâmetros fixos a priori (K_filter=33, target_vol=10%,
disaster_4σ, cone_lookback=1700, YZ_window=20) — parsimônia deliberada
(lição PBO=0.849 do F3.D v1).

**Resultado:** FAIL em todos os gates.
- PBO = 0.687 (gate ≤ 0.5) — overfitting dos configs gridados.
- DSR: 0/12 configs passam p < 0.05 — edge compatível com ruído.
- Walk-forward: 0/12 configs ≥ 6/8 windows profitable.
- Best config (config 6, N_entry=55 N_exit=10): Sharpe=0.19, CAGR=0.4%,
  max DD=5.7%.

**Interpretação:** a hipótese central ("breakout emergindo de regime quiet
carrega informação") não se confirma neste universo ETF multi-asset × 1h ×
2022-2026. Possíveis razões: (i) breakouts em ETFs são absorvidos por
market makers mais rápido que o sinal 1h captura; (ii) YZ cone bottom-
third não é um filtro seletivo o bastante (necessitaria multi-horizon);
(iii) mecanismo é real mas edge é sub-Sharpe-0.2 — indistinguível de
ruído com N=12 trials.

**Próximo passo:** Ehlers BP Swing em 1h — terceiro e último item do
catálogo intraday antes de considerar pivot de timeframe/mecanismo.

**Arquivos:**
- `reports/grid_vol_expansion_20260415-2301/diagnostic.md`
- `docs/superpowers/specs/2026-04-15-vol-expansion-breakout-1h-design.md`
- `docs/superpowers/plans/2026-04-15-vol-expansion-breakout-1h.md`
