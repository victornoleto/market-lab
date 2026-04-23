# 2026-04-23 05h00 — Plano C v2: análise de otimização da aposentadoria

## Contexto

Usuário pediu durante a noite (antes de dormir): "revise meu
`portfolio-aposentadoria.md` (Plano C) com base no knowledge base e pesquisa
web, levando em conta factor investing, ETFs alavancados (SSO/UPRO/QLD/TQQQ),
e ETFs de return stacking (NTSX/NTSI/NTSE + família Return Stacked Global).
Me dê 4 carteiras finais, uma por função objetivo: Max CAGR / Max Sharpe /
Max terminal wealth com MDD ≤ 50% / Max SWR."

Contexto emocional: após 29/29 FAIL em Plano A+B e 10/42 FAIL em Plano D no
mesmo dia/semana, o usuário quer gastar energia otimizando o único Plano que
sobrou — o Plano C passive long-term. "Sei que o retorno não vai ser enorme,
mas vai ser honesto."

## O que foi produzido (noite 2026-04-23 00h44 → 05h00)

Pasta `reports/portfolio_aposentadoria_v2/`:

- `ANALYSIS.md` — documento principal (~750 linhas) com:
  - Avaliação quantitativa do Plano C atual
  - Análise da proposta SSO 50% do usuário
  - Universo de 37 ETFs analisados
  - Backtests de 12 carteiras × 3 janelas (2020-26, 2006-26, 1926-26)
  - 4 carteiras finais com pesos, métricas e racional
  - Glidepath 30 anos
  - **Alerta de US Estate Tax** (risco não-endereçado no plano original)
  - Operacional (broker, DARF, custos)
  - Citações dos 17 livros ativos do projeto
- `TLDR.md` — resumo em 2 páginas
- `data/web_research.md` — pesquisa 2024-2026 com 30+ links
- `data/returns_monthly.parquet` — panel 1926-2026 (50 ativos)
- `scripts/01–06_*.py` — pipeline reprodutível
- `results/backtest_summary.csv` — 36 linhas (12 carteiras × 3 janelas)
- `results/final_portfolios.json` — as 4 carteiras + bootstrap 30y

## Resultados principais

### Proposta SSO 50% do usuário: **não faça**

Backtest 2006-2026 (20 anos):
- CAGR +1,9pp vs plano atual ✅
- Sharpe PIOR (0,35 vs 0,39) ❌
- MDD +19pp pior (-69% vs -50%) ❌
- P(MDD>50% em 30 anos de bootstrap) = **53%** vs 4% atual (13× pior) ❌
- SWR aposentadoria -1,4pp pior ❌

**Kernel correto (eficiência de capital), execução errada.** A solução real
é return stacking, não LETFs puros.

### NTSX é o substituto "certo" pra SSO

NTSX 100% vs SSO 100% em 2006-2026:
- NTSX: CAGR 11,50% / Sharpe 0,71 / MDD -41%
- SSO: CAGR 12,91% / Sharpe 0,37 / MDD -81%

NTSX entrega quase o mesmo CAGR com metade do drawdown e quase 2× o Sharpe.
ER 0,20% vs SSO 0,91%.

### As 4 carteiras finais

Todas batem simultaneamente o plano atual em CAGR, Sharpe e MDD. Janela
referência: 2006-2026 (proxy-based, inclui 2008 + COVID + 2022).

| Carteira | CAGR | Sharpe | MDD | p50 TW 30y | SWR |
|----------|------|--------|-----|------------|-----|
| P0 Atual | 7,5% | 0,39 | -50% | $1,13M | 4,07% |
| FINAL_1 Max CAGR | 9,1% | 0,61 | -35% | **$2,23M** | 5,3% |
| FINAL_2 Max Sharpe | 9,2% | **0,70** | -28% | $1,47M | 5,0% |
| FINAL_3 Max TW/MDD50 | **9,4%** | 0,64 | -36% | $1,81M | 5,4% |
| FINAL_4 Max SWR | 8,6% | 0,73 | -24% | $1,11M | **5,4%** |

FINAL_3 é o default pro perfil do usuário (30 anos, tolerância a factor
investing complexity, sem aversão a risco). Terminal wealth 60% maior que
plano atual com MDD melhor (-36% vs -50%).

### ⚠️ Alerta de US Estate Tax (descoberta da pesquisa)

Investidor brasileiro (non-resident alien) com ETFs US-domiciliados >$60k
paga **até 40% de estate tax federal US** na morte. Em $1,5M = ~$576k de
perda. Solução: UCITS irlandeses na IBKR pra 60% do bucket equity (CSPX,
IWDA, VWCE, EIMI) + foreign corporation pra patrimônio >$500k.

Isso **não estava** no `portfolio-aposentadoria.md` original. Crítico pro
30 anos de planejamento.

## Decisões deferidas pro usuário

1. Escolha entre FINAL_1 (agressivo) vs FINAL_3 (meu default) pra
   acumulação.
2. Migração Inter→IBKR agora vs só quando aporte mensal >$500/mês.
3. Estate tax mitigation: UCITS migration vs limite $60k vs foreign corp.
4. Hedge cambial parcial (NTN-B) 0% / 10-20% / 30%.
5. Glidepath: Cederburg-puro (FINAL_1 vida toda) vs transições por idade.

## Notas de método

- **Janela primária 2006-2026** (20 anos, proxies OK) — inclui 2008/COVID/2022.
- Janela 1926-2026 (100 anos) usada só qualitativamente — tem viés-baixa
  para carteiras com MF/Return-Stacked (proxy fallback = SPY_1x_sim).
- Bootstrap: stationary block 12 meses, 2000 caminhos, $10k inicial + $1k/mês.
- SWR: busca binária, 30 anos horizonte, 95% success threshold.
- Custos por ativo: ER + 30% withholding em dividendos + cap gains distrib
  estimado por turnover classe.

## Próximos passos (se o usuário aprovar)

1. Revisar UCITS replacements 1:1 pros ETFs US-domiciliados.
2. Setup paper trading IBKR (12 meses simulados) antes de implementação real.
3. Eventual atualização do `portfolio-aposentadoria.md` com novo spec.
4. Se decidir por FINAL_3: planejamento de migração de patrimônio existente
   (hoje provavelmente em Plano A+B+D fail cash pool).
