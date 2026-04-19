# Phase B Leads #7+#8: Vol-Sizing & Account Sensitivity [SWING BROKER] + [SHORT-HOLD CFD]

**Iteração 26 — 2026-04-16 15:07**

## Lead #7 — Vol-sizing para ETFRotation [SWING BROKER]

### O problema

ETFRotation é uma estratégia de tamanho fixo: always 100% em 1 ETF (top_n=1). Em mercados de alta volatilidade (ex: COVID mar/2020, tariffs abr/2025), a estratégia assume o mesmo nível de risco que em momentos de vol baixa. A pergunta: escalar posição pelo inverso da vol recente (`[machine_trading, p.126-127]`) melhora o Sharpe?

### Implementação

Adicionados parâmetros `vol_sizing`, `target_vol`, `vol_window` ao `ETFRotationStrategy`:
- `vol_sizing=True`: escala posição por `min(1.0, target_vol / realized_vol)`
- `realized_vol` = std(returns, 20 dias) × √252
- Cap em 1.0 — sem alavancagem (broker BR não permite)
- Script: `scripts/run_vol_sizing_etf_rotation_phase_b.py`

### Resultados

| Período | Variante | Sharpe | CAGR | MaxDD |
|---------|---------|--------|------|-------|
| IS (2003→2024) | Canonical | 0.729 | 11.03% | -28.6% |
| IS (2003→2024) | Vol-sized | 0.695 | 9.46% | -28.6% |
| OOS 2025 | Canonical | 1.477 | 23.71% | -8.11% |
| OOS 2025 | Vol-sized | 1.649 | 20.01% | -6.19% |
| Stress 2026-Q1 | Canonical | 1.073 | 40.60% | -19.21% |
| Stress 2026-Q1 | Vol-sized | 1.009 | 29.28% | -15.06% |

**IS delta Sharpe: -0.033 → NEUTRAL** (dentro do ruído).

Ambas passam nos gates (WF=8/8, DSR_p<<0.05). A versão vol-sized OOS tem Sharpe ligeiramente melhor (1.649 vs 1.477) e MaxDD menor (-6.19% vs -8.11%) — mas a diferença é pequena o suficiente para ser ruído.

### Veredito: OPCIONAL

A versão vol-sized não quebra os gates e reduz levemente o MaxDD em períodos OOS. Mas o ganho não é consistente (IS pior, OOS melhor). **Manter o canonical (100% fixed) como versão de produção**; vol-sizing disponível como variante conservadora para quem prefere menor MaxDD.

---

## Lead #8 — Account Size Sensitivity BollingerMR GARCH [SHORT-HOLD CFD]

### A pergunta

A estratégia BollingerMR GARCH SPY 1h funciona com $1k de capital inicial? Qual o mínimo viável dado os constraints da Pepperstone?

### Resultados

Testado IS (2019-11-25 → 2024-12-31) com custos Pepperstone (half_spread=$0.01, comm=$0.0186/share):

| Conta | Sharpe | CAGR% | MaxDD% | Lucro Líquido |
|-------|--------|-------|--------|---------------|
| $1k | 0.900 | ~5.9%* | -13.36% | $341 |
| $5k | 0.900 | ~5.9%* | -13.36% | $1,705 |
| $10k | 0.900 | ~5.9%* | -13.36% | $3,410 |
| $50k | 0.900 | ~5.9%* | -13.36% | $17,050 |
| $100k | 0.900 | ~5.9%* | -13.36% | $34,100 |

*Nota: script exibe 0.97% por usar 252 bars/year em dado 1h; CAGR real ≈ 5.9%/ano (~34% total em 5.1 anos).

**Resultado chave: perfeita invariância de escala.** Sharpe e MaxDD% idênticos em todos os tamanhos de conta.

### Mínimo Viável

- Pepperstone SPX500 min lot: 0.01 contrato = ~$50 notional
- Com $1k e risk_pct=0.95: notional = $950 >> $50 mínimo → **VIÁVEL**
- Mínimo viável: **$1.000** (inclusive com custos reais)
- Limite prático: custódia/margem Pepperstone exige ~$200 mínimo

### Veredito: GO a partir de $1k

A estratégia é viável desde $1k. O CAGR real de ~5.9%/ano com MaxDD -13.4% é realista e supera CDI em anos normais. Escalar para $10k+ é preferível para que comissões sejam proporcionalmente menores.

---

## Próximo passo

Lead #9 — Production Readiness Summary (consolidação final de GO/GO-WITH-CAVEATS/NO-GO por estratégia).
