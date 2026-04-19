# Production Readiness Summary — Todos os Winners [SHORT-HOLD CFD + SWING BROKER]

**Iteração 27 — 2026-04-16 16:00 — Phase B Lead #9 (FINAL)**

Esta entrada consolida todos os resultados da Phase B em um veredito final de produção por estratégia. Após 8 leads de validação (max window, cost ablation, MC bootstrap, cross-asset transport, correlation, regime decomp, vol-sizing, account sensitivity), chegamos ao veredicto final.

---

## Winner 1 — BollingerMR GARCH SPY 1h [SHORT-HOLD CFD]

**Estratégia:** Bollinger Bands (window=20, std_mult=2.0) com EWMA-GARCH vol sizing (λ=0.94) no SPY horário. Entry quando preço toca a banda, exit por stop ou max_hold=24 horas. Median hold: 1.29 trading days.

**Broker alvo:** Pepperstone CFD via cTrader Open API. Swap modeled.

**Citações:** `[machine_trading, p.204-205]` (Bollinger canonical), `[machine_trading, p.126-127]` (EWMA-GARCH sizing), `[AFML, p.201-207]` (PSR N=1).

### Resumo dos gates (com custos reais Pepperstone)

| Gate | Valor | Resultado |
|------|-------|-----------|
| PBO (N=1, pré-especificado) | trivial | ✅ PASS |
| PSR p-value | 0.0431 | ✅ PASS (< 0.05) |
| Walk-forward | 6/8 janelas positivas | ✅ PASS |
| OOS 2025 (hold-out) | Sharpe 0.474 | ✅ Positivo |
| Stress 2026-Q1 | Sharpe 2.854 | ✅ Positivo |

### Resumo Phase B

| Teste | Resultado | Detalhe |
|-------|-----------|---------|
| Janela máxima | ✅ | 2019-11-25 → 2026-04-15 (6.4 anos, manifest máximo) |
| Custos Pepperstone | ✅ | IS Sharpe gross=0.995 → net=0.801; gates PASS com custo |
| MC Bootstrap CI | ⚠️ | Per-trade CI=[-0.134, 1.728] — inclui zero, mas sizing GARCH não capturado por trade; bar-level 0.995/0.945 é a métrica primária |
| Cross-asset transport | ❌ | SPY-only edge. 13 ETFs testados (QQQ/IWM/XLK/XLE/XLF/GLD/TLT/EEM/DIA etc.), todos FAIL |
| Correlação c/ ETFRotation | ✅ | ρ=0.252 — INDEPENDENTE. Blend 50/50 Sharpe=1.020 |
| Regime (VIX quintis) | ✅ | Sem quintil negativo com n≥5. 2022 único ano negativo (bear market) |
| Vol-sizing (GARCH extra) | NEUTRAL | GARCH já integrado; variante de vol adicional não melhora |
| Account sensitivity | ✅ | Scale-invariant $1k–$100k. Min viable: $1k (notional $950 > Pepperstone min $50) |

### Caveats de produção

1. **Edge SPY-específico:** A estratégia não funciona em outros ETFs — não diversifica por ativo, só pelo mecanismo Path A vs B. O edge provém da função de benchmark do SPY (arbitragem + creation/redemption ETF).
2. **Bootstrap CI por trade inclui zero:** Com 151 trades IS, o CI é estatisticamente wide. O bar-level Sharpe (0.995) depende do sizing GARCH e é a métrica correta. Aceito metodologicamente — `[advances_fin_ml, p.196-202]`.
3. **2022 bear market:** Único ano negativo IS (Sharpe -1.431). A estratégia não tem filtro de regime. SPY>SMA200 como gate qualitativo (não obrigatório) reduziria esse drawdown.
4. **WF marginal com custos:** 6/8 (gate mínimo). Sem custos é 7/8. A estratégia está no limite do gate WF quando custos são incluídos.
5. **CAGR real modesto:** ~5.9%/ano após custos Pepperstone. Supera CDI em anos normais mas não é um "home run" — é um edge consistente de baixo risco.

### Veredicto

> ### ✅ GO-WITH-CAVEATS — BollingerMR GARCH SPY 1h [SHORT-HOLD CFD]
>
> Pronto para produção com monitoramento ativo. Constraints operacionais: conta mínima $1k; SPY CFD via Pepperstone Razor; monitorar posição SPY vs SMA200 como trigger qualitativo de cautela em 2022-style bear markets. Não expandir para outros ativos — edge é SPY-only. Caveats aceitos e documentados.

---

## Winner 2 — ETFRotation Monthly Top-1 [SWING BROKER]

**Estratégia:** Rotação mensal entre SPY/QQQ/IWM/GLD/TLT. Ranking por adjusted_slope (slope anualizado 90d × R²). Filtros: SPY>SMA200 (regime) e ETF>SMA100 (individual). Investe 100% no ETF top-1. Median hold: ~5 meses.

**Broker alvo:** Corretora brasileira swing (XP, Clear, etc.). Sem swap. 15% IR sobre ganhos modelado.

**Citações:** `[stocks_on_the_move, p.81]` (adjusted_slope), `[stocks_on_the_move, p.66-67]` (SMA200 regime filter), `[stocks_on_the_move, p.81-82]` (SMA100 individual filter).

### Resumo dos gates (com custos BR + 15% IR)

| Gate | Valor | Resultado |
|------|-------|-----------|
| PBO (N=1, pré-especificado) | trivial | ✅ PASS |
| PSR p-value | 0.0041 | ✅ PASS (< 0.05) |
| Walk-forward | 7/8 janelas positivas | ✅ PASS |
| OOS 2025 (hold-out) | Sharpe net 1.570 | ✅ Positivo |
| Stress 2026-Q1 | Net +8.34% | ✅ Positivo |

### Resumo Phase B

| Teste | Resultado | Detalhe |
|-------|-----------|---------|
| Janela máxima | ✅ | 2003-01-02 → 2026-04-15 (23 anos, manifest máximo) |
| Custos BR | ✅ | IS Sharpe gross=0.729 → net=0.551; gates PASS. OOS net=1.570 |
| MC Bootstrap CI | ✅ | IS CI=[0.449, 1.254] — lower bound acima de zero em 22 anos de dados mensais. ROBUSTO |
| Cross-asset transport | ✅ | Expanded 8-ETF (+ XLK/XLF/EEM): IS PASS (Sharpe=0.609, WF 7/8, DSR p=0.0035), OOS=1.120 |
| Correlação c/ BollingerMR | ✅ | ρ=0.252 — INDEPENDENTE. Mecanismo diferente (momentum vs MR) |
| Regime (VIX quintis) | ✅ | Sem quintil negativo com n≥3. 2012/2016 únicos anos negativos em 22 anos IS |
| Vol-sizing opcional | NEUTRAL | IS delta=-0.033 (ruído). Canonical preferred; vol-sized disponível como opção conservadora |
| Account sensitivity | ✅ | Estratégia long-only sem alavancagem. Funciona desde qualquer valor acima do mínimo da corretora |

### Caveats de produção

1. **Mercados laterais:** 2012 e 2016 foram anos negativos (-11.7% e -3.5%). Nesses mercados laterais sem trend claro, a rotação pega momentum fraco e pode travar na posição errada. O filtro SMA200 protege de bear markets mas não de lateralidade.
2. **15% IR timing:** O modelo de IR é conservador (15% sobre meses positivos). Na prática, o IR incide sobre ganhos anuais de day-trade não financeiro — a frequência mensal de rebalanceamento deve ser verificada com o contador. Pode haver tratamento diferenciado para ETFs brasileiros vs americanos.
3. **ETFRotation_top2 FAIL com custos:** A variante top-2 passa sem custos mas falha WF (5/8) com 15% IR + comissão. Usar apenas top-1 em produção.
4. **Universo de ativos:** Estratégia opera ETFs americanos (SPY, QQQ, etc.) em USD. Para corretora brasileira, requer conta internacional (XP Internacional, Avenue, etc.) ou BDRs — verificar liquidez e spread dos BDRs antes de ir ao vivo.
5. **Lookback 90d:** No início de cada mês, o sistema precisa de 90 dias de dados para calcular o adjusted_slope. Implementação deve garantir that o dado histórico está disponível via Tiingo antes da execução.

### Veredicto

> ### ✅ GO — ETFRotation Monthly Top-1 [SWING BROKER]
>
> Pronto para produção. A estratégia tem 22+ anos de histórico, bootstrap CI acima de zero, transporte confirmado para universo expandido, e resistência a custos reais (15% IR + 0.10% comissão). Constraints operacionais: apenas top-1 (não top-2); verificar estrutura tributária exata dos ETFs via contador BR; conta internacional com acesso a ETFs americanos ou BDRs líquidos. Monitoramento: anual — verificar se IS/OOS Sharpe ainda acima de 0.4 após cada ano completo.

---

## Winner 3 — ETFRotation Monthly Top-2 [SWING BROKER] — STATUS: DEMOTED

**Status: COSTS-SENSITIVE → NÃO RECOMENDADO PARA PRODUÇÃO**

A variante top-2 (50/50 dois ETFs de maior score) passa os gates IS sem custos (WF 7/8, DSR p=0.0009) e tem excelente OOS (1.611). Mas com 15% IR + 0.10% comissão, o WF cai para 5/8 (abaixo do mínimo 6/8). Duas janelas WF que eram marginalmente positivas gross flippam para negativo após custos.

Mantida em `winners_swing` apenas para transparência histórica. Em produção, usar apenas top-1.

> ### ⚠️ NO-GO (production) — ETFRotation_top2 [SWING BROKER]
>
> Sensível a custos. WF 5/8 com custos reais. Pode ser reconsiderada se spread real da corretora BR for menor que modelado (< 0.05% RT) — mas requer re-validação antes de qualquer live trade.

---

## Blend recomendado para produção

| Componente | Alocação sugerida | Broker | Retorno esperado |
|------------|-------------------|--------|-----------------|
| BollingerMR GARCH SPY 1h | USD account (Pepperstone) | Path A | ~5.9%/yr após custos |
| ETFRotation top-1 | USD account (broker BR internacional) | Path B | ~9.1-9.6%/yr líquido IR |
| Correlação entre as duas | ρ=0.252 | — | Sharpe blend 1.020 |

As duas estratégias são **genuinamente independentes** (ρ=0.252, mecanismos opostos: MR intraday vs momentum mensal). Blend 50/50 tem Sharpe teórico ~1.020 — acima de qualquer estratégia individual.

---

## Checklist de produção por estratégia

### BollingerMR GARCH SPY 1h

- [ ] Conta Pepperstone Razor ativa com ≥$1k
- [ ] cTrader Open API credentials configurados
- [ ] Live data feed Tiingo IEX 1h (ou equivalent) para SPY
- [ ] Sistema de ordens: entry na abertura da barra seguinte após sinal, exit por stop ou max_hold
- [ ] Monitor: Sharpe rolling 30d deve ser > 0; pausar se 3 meses consecutivos negativos
- [ ] Gate qualitativo: aumentar cautela quando SPY < SMA200 (não stop automático — revisão humana)
- [ ] Máximo 95% do capital por posição (risk_pct=0.95)

### ETFRotation Monthly Top-1

- [ ] Conta internacional com acesso a SPY/QQQ/IWM/GLD/TLT (ou BDRs líquidos equivalentes)
- [ ] Calendário de rebalanceamento: primeiro dia útil de cada mês
- [ ] Data de cálculo: último dia útil do mês anterior (usar Tiingo daily para adjusted_slope)
- [ ] Verificar com contador: tratamento tributário exato para ETFs americanos via corretora BR
- [ ] Monitor: retorno anual; OK se ≥ 0% em ≥ 5/7 anos rolling

---

## Conclusão da Phase B

Todos os 9 leads da Phase B foram consumidos:

1. ✅ Max window validation
2. ✅ Cost ablation (Pepperstone + BR broker)
3. ✅ MC Bootstrap CI
4. ✅ Cross-asset transport
5. ✅ Cross-strategy correlation
6. ✅ Regime decomposition
7. ✅ Vol-sizing variant
8. ✅ Account size sensitivity
9. ✅ **Esta entrada** — Production readiness summary

**Resultado final da Phase B:**
- BollingerMR GARCH SPY 1h → **GO-WITH-CAVEATS** (edge real, custos OK, min $1k, SPY-only)
- ETFRotation top-1 → **GO** (edge robusto 22 anos, CI acima zero, custos OK, transport OK)
- ETFRotation top-2 → **NO-GO (production)** (costs-sensitive, WF 5/8 com IR)

O projeto ai-trade Phase B está concluído. Próxima fase: implementação do executor live (Phase 3 do ROADMAP).
