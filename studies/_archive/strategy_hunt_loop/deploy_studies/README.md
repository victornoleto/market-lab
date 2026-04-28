# Deploy Studies — sub-estudos pós-hunt loop

Estudos derivados do `strategy_hunt_loop` focados em **deploy-readiness**:
operacionalização, comparação empírica entre candidatos, e análise de
trade-offs vs alternativas externas (Plano C V3_1, NTSX+GDE, etc).

Cada sub-pasta é **self-contained**: validator + plotter + JSON +
markdown report + parquets de retornos. Scripts usam paths relativos
(`Path(__file__).parent`), então rodam de qualquer working directory.

## Sub-estudos (cronológico)

### 1. `iter035_variants/` — 4 caminhos de deploy do iter 035

V0 (IBKR margin direto) vs V1 (NTSX+GDE 67/33 Inter cash) vs V2 (2× LETF
Inter) vs V3 (3× LETF Inter). **Achado**: V1 NTSX+GDE empata Sharpe com V0
e tem o melhor MDD (44%) + melhor 2022 stress (−22% vs −38-40%).

### 2. `iter079_leveraged/` — alavancando o vencedor de momentum

Hipótese do user: "se SPY rendeu mais, comprar SSO/UPRO em vez de SPY".
**Refutado empiricamente**: 3× LETF chegou a MDD 96.58% (near-wipeout).
Leverage paradox confirmed.

### 3. `aporte_simulation/` — DCA $10k+$1.5k/mês × 40y

Money-weighted IRR de cada variante com FX cost real. **Achado crítico**:
V0 IBKR margin com 4%/yr de juros honestos PERDE pra todas variantes Inter.

### 4. `v1_vs_planoc/` — 3-way comparativo V1 vs Plano C V3_1 v3.5

Janela 32y (1994-2026), rolling 5y/10y, stress tests. V1 vence em 8/9
dimensões mas com proxies que subestimam V3_1 em ~150-300 bps/yr.

### 5. `us_vs_global/` — estudo academic-evidence pra US dominance question

DMS + Asness + Vanguard CMA framework. 2000-2013 lost decade: VT global
venceu SPY por 1.1pp/yr durante 13 anos.

### 6. `portfolio_4way/` — V1 vs V3_1 vs V_HYBRID vs V_HYBRID_SIMPLE

Define V_HYBRID como V3_1 com 12% AVUS substituído por 12% NTSX. Marginal
improvement sobre V3_1. AVNM custa 22 bps/yr (não recomendo).

### 7. `portfolio_variants/` — 6 variantes V_HYBRID + Managed Futures

**WINNER FINAL**: V_HYBRID + 10% MF (KMLM/DBMF). Sharpe 0.743, MDD 44.7%
(igual a V1!), P(rolling 10y < 5%) = 0.6%. Hurst-Ooi-Pedersen 2017
(trend-following premium) é o sleeve marginal mais valioso.

### 8. `letfs_5way/` — Reddit post (5-portfolio shootout 1986-2026)

NTSX vs NTSX+GDE blend vs SPY vs GDE vs SSO/ZROZ/GLD. NTSX+GDE blend
ganha Sharpe e rolling-window floor.

## Conclusão consolidada (final desta sessão)

**Recomendação**: V_HYBRID + 10% Managed Futures (12 ETFs):
```
22.5% GDE | 10.8% NTSX | 18% AVDE | 11.7% AVEM
9% AVUV | 4.5% AVDV | 6.3% SPMO | 2.7% IDMO
4.5% BTGD | 10% DBMF (ou KMLM)
```

Todas teses preservadas (factor + global + capital efficiency) + sleeve
orthogonal (managed futures) que protege em rate cycles (2022) sem
sacrificar CAGR.

⚠️ **Mandate maintenance §1 inalterado**. Estudos são deploy-readiness
research, não autorizam capital sem override §7.

## Rodando os scripts

Cada sub-pasta tem validator (gera JSON + parquet) e plotter (gera PNGs).
Order: validator antes do plotter. Scripts são portáveis:

```bash
# Exemplo — variante final:
uv run python studies/strategy_hunt_loop/deploy_studies/portfolio_variants/portfolio_variants_validator.py
uv run python studies/strategy_hunt_loop/deploy_studies/portfolio_variants/plot_portfolio_variants.py
```

Ou direto da pasta:
```bash
cd studies/strategy_hunt_loop/deploy_studies/portfolio_variants/
uv run python portfolio_variants_validator.py && uv run python plot_portfolio_variants.py
```

## Cross-references

- `aporte_simulation` lê `iter035_variants/iter035_variants_returns.parquet`
- Outros sub-estudos são self-contained
