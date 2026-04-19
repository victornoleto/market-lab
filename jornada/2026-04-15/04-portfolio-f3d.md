# 2026-04-15 (noite) — F3.D Portfolio Clenow+Ehlers — FAIL v1 (paradoxo WF 9/9 + PBO 0.849)

**Hipótese:** se Clenow × Ehlers têm correlação de equity ≈ −0.01 (Run 2),
combiná-los num portfolio 50/50 "dois livros offline" pode:
(a) elevar o Sharpe pra ~1.0 via diversificação (1.41× a média, quando
ρ ≈ 0 e vols similares), passando o DSR;
(b) reduzir drawdown em crises (Clenow sai do mercado via regime filter
SMA200, Ehlers oscila).

**O que rodamos:** top-3 Clenow (Tiingo 2015-2023, configs 8/19/10 por
Sharpe) × top-3 Ehlers (long-history 2005-2023, configs 6/18/19 por
Sharpe) = 9 portfolios 50/50, merge offline via retornos ponderados,
sem rebalance. Janela v1: SPY 2015-2023 Tiingo survivorship-free.

**Resultado v1 (`grid_portfolio_20260415-1541`):**

| Métrica | Baseline isolado | F3.D v1 portfolio |
|---|---|---|
| PBO | Ehlers 0.496 ✅ / Clenow 0.603 | **0.849 ❌ (piorou muito)** |
| DSR 0/N pass | 0/24 (Ehlers) / 0/30 (Clenow) | 0/9 (best p=0.190, melhorou) |
| Walk-forward | Ehlers 7/24 / Clenow 9/30 | **9/9 ✅ (salto enorme)** |
| Best Sharpe | Ehlers 0.806 | 0.804 (config 1: clenow=8 × ehlers=18) |
| Best CAGR | — | 10.84% |
| Best DD | — | 18.02% |

**Leitura leiga:**
- **Bom: WF 9/9**. Todas as 9 combinações passam ≥6/8 janelas lucrativas
  com DD≤25%. Clenow regime filter subsidia o DD do Ehlers — a tese
  "diversificação reduz crise" funciona empiricamente.
- **Ruim: PBO 0.849**. Paradoxo: diversificação tornou os 9 configs tão
  uniformes (Sharpes clustered 0.71-0.80, PBO logits std=1.08 muito
  apertado) que o "melhor" vira essencialmente aleatório. Quanto mais
  uniforme o grid, mais overfit o PBO marca — porque a seleção IS → OOS
  é ruído puro.
- **DSR ainda não passa**: Sharpe 0.80 é bom mas não chega no 1.0 que a
  matemática predizia. A hipótese teórica assumia vol-scaled (vols
  iguais); sem vol-scaling (caveat explícito da spec §5 "vol mismatch"),
  o ganho real é menor.

**Conclusão:** a hipótese H1 (portfolio rescata DSR para ~1.0) **falha**,
mas com sub-resultado positivo importante: a diversificação **resolve o
problema de WF em crises** `[stocks_on_the_move, p.66-67, p.98-99]` — só
não resolve DSR, e em cima ainda piora o PBO pela uniformidade dos
configs. Spec go/no-go §6.2 manda pular v2 (2005-2023) quando v1 falha.

**Próximo passo (caminho B no plan):** AFML sofisticado. Agora com
sub-resultado validado de que WF é solúvel (Clenow regime filter ajuda),
o foco fica em:
- Walk-forward CV com purge/embargo (López de Prado `[advances_fin_ml, ch.7]`)
  em vez do split temporal ingênuo 50/50 do Run 4 Step 1.
- Features ricas: `[osc, dcp, hp, ss_trend, atr20, regime_flag, vix_proxy, volume_z]`.
- Triple-barrier labeling assimétrico (TP/SL não-simétricos).
- Universo de treino: long-history 1993-2026 (Tiingo widest bulk, ~3×
  dados vs 2015-2023).

**Arquivos gerados:**
- `reports/grid_portfolio_20260415-1541/diagnostic.md` (v1, 9 configs).
- Código novo em `src/ai_trade/backtest/portfolio/` (commits `872a9cf`
  core + `c99bca3` citation fix + `36c0f57` CLI + `ac00d6e` review fixes).
- Spec: `docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md`.
- Plan: `docs/superpowers/plans/2026-04-15-f3d-portfolio-clenow-ehlers.md`.
