# Weekly Momentum Final Report

## TL;DR

**Veredito final:** nenhuma estratégia semanal de momentum estudada aqui é
válida para deploy. A família stock chegou a parecer promissora, mas perdeu
força à medida que removemos vieses de universo e dados. O teste honesto de
Phase 4, com Tiingo backfill para removidos/renomeados e S&P 500 PIT aproximado,
rejeitou os leads congelados `lb80/k5/SMA200-250`. A reabertura posterior em
`dynamic_wf_all_stocks` ADV5M manteve CAGR alto, mas também falhou gates duros e
otimização local não melhorou o baseline `[advances_fin_ml, p.208-211]`.

**Resultado final das três estratégias ADV5M finais após Phase 5c:**

| estratégia | grid | CAGR | MDD | Sharpe | PBO | DSR p | bootstrap low CAGR | 10 bps + DARF CAGR | veredito |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `ADV5M baseline` | `60/80/100 × k=5/10/20 × SMA200/250` | 48.09% | -36.26% | 1.184 | 0.579 | 0.024 | -3.11% | 18.99% | FAIL |
| `focused optimization` | `50/60/70/80 × k=5/8/10/12 × SMA200/250` | 43.89% | -38.15% | 1.075 | 0.381 | 0.089 | -10.12% | 15.31% | FAIL |
| `aggressive neighborhood` | `40/50/60/70 × k=3/4/5/6/8 × SMA150/200/250` | 39.50% | -55.10% | 0.940 | 0.044 | 0.260 | -13.54% | 8.11% | FAIL |

**Resultado dos melhores leads S&P 500 após Phase 4:**

| estratégia | CAGR | MDD | Sharpe | SPY CAGR | SPY MDD | SPY Sharpe | DSR p | bootstrap low CAGR | veredito |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `lb80/k5/SMA200` | 17.44% | -27.64% | 0.766 | 14.44% | -33.70% | 0.884 | 0.491 | -1.57% | FAIL |
| `lb80/k5/SMA250` | 19.36% | -37.77% | 0.817 | 14.44% | -33.70% | 0.884 | 0.418 | -2.10% | FAIL |

**Por que falhou:**

- Ainda bate SPY em CAGR bruto, mas com Sharpe inferior ao SPY.
- Falha DSR, portanto não supera a penalidade de múltiplos testes `[advances_fin_ml, p.273-275]`.
- Falha bootstrap lower-CAGR, portanto não passa o gate estatístico mínimo `[advances_fin_ml, p.196-202]`.
- O edge caiu justamente quando o universo passou a incluir melhor os removidos/delistados.
- ETF replication já tinha sido fraca; não há motivo para portar esta tese para ETFs.
- A reabertura `dynamic_wf_all_stocks` ADV5M manteve CAGR alto, mas PBO/bootstrap
  continuaram bloqueando o baseline; as grades que melhoraram PBO perderam DSR,
  bootstrap e qualidade de drawdown.

**Recomendação:** encerrar esta família. Só reabrir com hipótese nova e pré-registrada, mudando sinal ou universo. Não fazer mais sweep local em `lb80/k5`.

## Plots Finais

### Phase 4 Leads vs SPY

![Phase 4 performance vs SPY](plots/final/combined_performance_vs_spy.png)

![Phase 4 equity over SPY](plots/final/combined_equity_over_spy.png)

![Phase 4 rolling windows](plots/final/combined_rolling_windows_1_3_5_10y.png)

### Phase 5c ADV5M Final Variants vs SPY

Comparação final das três estratégias ADV5M que chegaram ao fim do estudo:
baseline, focused optimization e aggressive neighborhood.

![Phase 5 ADV5M performance vs SPY](plots/phase5/phase5_adv5m_performance_vs_spy.png)

![Phase 5 ADV5M equity over SPY](plots/phase5/phase5_adv5m_equity_over_spy.png)

![Phase 5 ADV5M rolling CAGR vs SPY](plots/phase5/phase5_adv5m_rolling_cagr_1_3_5y.png)

![Phase 5 ADV5M rolling summary vs SPY](plots/phase5/phase5_adv5m_rolling_summary_vs_spy.png)

### Decisão Top-6 Antes Do Rerun Final

Este painel mostra por que a Phase 4 foi necessária: antes do backfill expandido,
os leads pareciam fortes, mas ainda estavam expostos a viés de dados/universo.

![Top-K equity vs SPY](plots/final/topk_equity_vs_spy.png)

![Top-K equity over SPY](plots/final/topk_equity_over_spy.png)

![Top-K rolling CAGR](plots/final/topk_rolling_cagr_1_3_5_10y.png)

![Top-K drawdown vs SPY](plots/final/topk_drawdown_vs_spy.png)

## Evolução Do Estudo

## Phase 0 — Hipótese E Setup Inicial

Hipótese inicial: momentum cross-sectional semanal poderia capturar força recente
entre ações/ETFs usando execução honesta com dados diários.

Decisões metodológicas iniciais:

- Sinal na quinta-feira usando dados disponíveis até o close de quinta.
- Venda na sexta se o vencedor mudasse.
- Compra após settlement, sem usar close de sexta para decidir venda de sexta.
- Benchmark SPY buy & hold obrigatório em todos os reports.
- Momentum ranking baseado em cross-sectional momentum `[stocks_on_the_move, p.60]`.
- Filtro de regime SPY/SMA testado como controle de risco `[stocks_on_the_move, p.66-67, p.81]`.

Resultado: a variante stock inicial pareceu promissora, mas ainda com universo
atual e sem PIT/delisted, portanto apenas diagnóstico.

## Phase 1 — Sweeps Controlados E Walk-Forward Inicial

Foram rodados sweeps controlados em stocks com variações de lookback, `top_k`,
filtro de mercado e regra de momentum negativo.

Resultados principais:

| trilha | resultado bruto | interpretação |
|---|---:|---|
| S&P 500 atual WF | CAGR 42.30%, MDD -50.84%, Sharpe 1.216 | Forte, mas current-membership biased |
| All-stocks WF | CAGR 61.83%, MDD -60.52%, Sharpe 1.200 | Alto CAGR, risco/viés ainda maiores |
| ETF WF | CAGR 6.41%, MDD -48.64%, Sharpe 0.459 | Fraco vs SPY |

Evolução: o estudo deixou de ser “sinal semanal curto” e passou para momentum
mais longo com filtros de regime, principalmente `lb60/k3/SMA200` e
`lb60/k10/SMA100`.

Problema identificado: resultados altos demais em current-membership S&P 500 e
all-stocks exigiam controle de overfit e survivorship bias.

## Phase 2 — Candidate Validation E Neighborhood

Foram congelados candidatos e adicionados custos, DARF proxy, liquidez, OOS,
bootstrap, DSR e PBO contextual.

Candidatos iniciais:

| candidato | papel | conclusão |
|---|---|---|
| `fixed_aggressive_sp500` (`lb60/k3/SMA200`) | primeiro lead agressivo | bom antes de PIT, depois enfraqueceu |
| `fixed_balanced_sp500` (`lb60/k10/SMA100`) | controle defensivo | tax/DSR fracos |
| `dynamic_wf_sp500` | seleção dinâmica S&P | colapsou sob PIT |
| `dynamic_wf_all_stocks` | controle all-stocks | alto CAGR, mas falhou PBO/DSR |

O neighborhood do lead agressivo encontrou uma ilha mais robusta em:

- `lookback=80`
- `top_k=5`
- `SPY>SMA200` ou `SPY>SMA250`

Resultado Phase 2: `lb80/k5/SMA200-250` substituiu `lb60/k3/SMA200` como lead.
Ainda assim, a família continuava sem dados PIT/delisted adequados.

## Phase 3 — S&P 500 PIT Aproximado

Phase 3 adicionou S&P 500 PIT aproximado via Wikipedia selected changes. O ranking
passou a ser filtrado pelo conjunto de membros na data do sinal `[advances_fin_ml, p.208-211]`.

Resultados sob PIT aproximado, ainda carregando majoritariamente o cache atual:

| candidato | CAGR | MDD | Sharpe | DSR p | bootstrap low CAGR | interpretação |
|---|---:|---:|---:|---:|---:|---|
| `lb60/k3/SMA200` | 14.26% | -38.91% | 0.608 | 0.728 | -8.47% | lead original rejeitado |
| `lb80/k5/SMA200` | 25.20% | -28.45% | 1.030 | 0.185 | 4.95% | melhor defensivo, mas DSR FAIL |
| `lb80/k5/SMA250` | 26.57% | -32.24% | 1.053 | 0.165 | 3.16% | melhor lead, mas DSR FAIL |
| `dynamic_wf_sp500` | -3.33% | -63.14% | -0.003 | 0.997 | -22.34% | rejeitado |

Evolução: o estudo ficou mais honesto e a maior parte do edge inicial evaporou.
Os únicos leads remanescentes eram `lb80/k5/SMA200-250`, mas ainda bloqueados por
DSR e por feed imperfeito.

## Phase 3 Deep Dive — DSR E Entry Timing

O deep dive de `lb80/k5/SMA250` mostrou que o problema era principalmente a
penalidade de múltiplos testes:

| trials | p-value | pass? |
|---:|---:|---|
| 1 | 0.00009 | yes |
| 10 | 0.01520 | yes |
| 25 | 0.04068 | yes |
| 50 | 0.07159 | no |
| 100 | 0.11312 | no |
| 200 | 0.16466 | no |

Entry-window robustness parecia boa em horizontes longos, mas as janelas são
sobrepostas e não independentes:

| janela | pct beating SPY | pior CAGR strategy | pior edge vs SPY |
|---:|---:|---:|---:|
| 1y | 70.01% | -23.94% | -41.11pp |
| 3y | 82.74% | 2.15% | -10.31pp |
| 5y | 100.00% | 15.48% | +2.39pp |
| 10y | 100.00% | 20.36% | +7.77pp |

Interpretação na época: bom lead de pesquisa, não deployable. A próxima etapa
correta era dados melhores, não mais sweep.

## Phase 4 — Tiingo Backfill E PIT Expandido

Phase 4 usou a assinatura Tiingo para reduzir o viés de survivorship no preço.
O universo foi expandido para:

```text
current S&P 500 ∪ start-date S&P 500 ∪ selected-change added/removed tickers
```

Auditoria de cobertura:

| métrica | valor |
|---|---:|
| Universo expandido | 769 tickers |
| Disponíveis após backfill | 745 |
| Cobertura total | 96.88% |
| Prováveis removidos/renomeados | 260 |
| Removidos/renomeados disponíveis | 240 |
| Cobertura removidos/renomeados | 92.31% |

Mudança metodológica crítica: carregar todo o cache equity e só então aplicar o
PIT membership no sinal. Isso permitiu que nomes removidos participassem quando
tinham histórico Tiingo.

Resultado final:

| candidato | CAGR | MDD | Sharpe | SPY CAGR | SPY MDD | SPY Sharpe | DSR p | bootstrap low CAGR | 10 bps + DARF CAGR | OOS positive |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `lb80/k5/SMA200` | 17.44% | -27.64% | 0.766 | 14.44% | -33.70% | 0.884 | 0.491 | -1.57% | -5.77% | 8/10 |
| `lb80/k5/SMA250` | 19.36% | -37.77% | 0.817 | 14.44% | -33.70% | 0.884 | 0.418 | -2.10% | 0.20% | 9/10 |

Conclusão Phase 4: o edge não desapareceu completamente em CAGR, mas perdeu
qualidade suficiente para falhar. O Sharpe ficou abaixo do SPY, e os gates duros
continuaram negativos.

## ETF Track

ETFs foram testados como replicação da tese stock, não como desenho próprio.

Resultado resumido:

| melhor variante ETF | CAGR | MDD | Sharpe | SPY CAGR | SPY MDD | SPY Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| `lb60/k10/SMA100` | 10.76% | -35.96% | 0.665 | 10.96% | -55.20% | 0.652 |

Walk-forward ETF: CAGR 6.41%, MDD -48.64%, Sharpe 0.459 vs SPY Sharpe 0.619.

Conclusão: a tese stock não migrou para ETFs. Se ETFs forem reabertos, deve ser
com hipótese ETF-specific, não com port direto desta regra.

## Phase 5/5b/5c — ADV5M Dynamic All-Stocks Reopen

Após a rejeição da família S&P 500, uma hipótese separada foi reaberta: momentum
semanal dinâmico em todos os equities cacheados, filtrando tradability
point-in-time por idade, preço e ADV20 >= $5M `[stocks_on_the_move, p.81]`.

Resultado ADV5M base:

| run | CAGR | MDD | Sharpe | PBO | DSR p | bootstrap low | 10 bps + DARF CAGR | veredito |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| ADV5M base | 48.09% | -36.26% | 1.184 | 0.579 | 0.024 | -3.11% | 18.99% | FAIL |

Resultado das três estratégias finais:

| estratégia | CAGR | MDD | Sharpe | PBO | PBO pass | DSR p | DSR pass | bootstrap low | bootstrap pass | rolling 1y beat SPY | rolling 3y beat SPY | veredito |
|---|---:|---:|---:|---:|---|---:|---|---:|---|---:|---:|---|
| `ADV5M baseline` | 48.09% | -36.26% | 1.184 | 0.579 | no | 0.024 | yes | -3.11% | no | 74.98% | 92.38% | FAIL |
| `focused optimization` | 43.89% | -38.15% | 1.075 | 0.381 | yes | 0.089 | no | -10.12% | no | 62.86% | 86.69% | FAIL |
| `aggressive neighborhood` | 39.50% | -55.10% | 0.940 | 0.044 | yes | 0.260 | no | -13.54% | no | 57.52% | 79.24% | FAIL |

O deep dive mostrou concentração material em winners especulativos/meme/high-beta
como `GME`, `MARA`, `SMCI`, `SEZL` e `BBBY`. Remover os top 10 contribuidores
derrubou o CAGR para 16.32% e o Sharpe para 0.659. A otimização Phase 5c testou
grades locais após stale-price guard: a baseline continuou com melhor performance,
enquanto grades com PBO melhor perderam DSR/bootstrap/performance.

Rolling-window final contra SPY:

| estratégia | 1y beat SPY | pior edge 1y | 3y beat SPY | pior edge 3y | 5y beat SPY | pior edge 5y |
|---|---:|---:|---:|---:|---:|---:|
| `ADV5M baseline` | 74.98% | -38.76pp | 92.38% | -6.02pp | 100.00% | +21.59pp |
| `focused optimization` | 62.86% | -48.25pp | 86.69% | -8.57pp | 100.00% | +13.85pp |
| `aggressive neighborhood` | 57.52% | -53.35pp | 79.24% | -20.82pp | 100.00% | +24.09pp |

Conclusão Phase 5c: ADV5M permanece lead de pesquisa interessante, mas não
deployable. O próximo passo válido seria dados survivorship-free all-listed com
delisting returns, não mais otimização local `[advances_fin_ml, p.196-202]`.

## Decisão Final

Esta família deve ser encerrada.

Motivos:

- Melhorar os dados reduziu o edge, em vez de confirmar a tese.
- O retorno excedente não compensa a perda de Sharpe versus SPY.
- DSR e bootstrap falham nos leads finais.
- Custos/tax deixam o resultado líquido fraco.
- ETFs não oferecem fallback natural.
- A reabertura ADV5M all-stocks falha PBO/bootstrap e depende demais de poucos
  winners especulativos.

O próximo estudo de momentum só deve começar se houver uma hipótese nova e
pré-registrada, por exemplo outro universo, outro horizonte, outra definição de
momentum ou outro mecanismo de regime. Continuar ajustando parâmetros desta
família seria data-mining, não pesquisa incremental válida `[advances_fin_ml, p.208-211]`.

## Artefatos Principais

- `reports/STUDY_REPORT.md`: estudo inicial stocks.
- `reports/ETF_STUDY_REPORT.md`: replicação ETF.
- `reports/DEPLOY_CANDIDATES.md`: congelamento inicial de candidatos.
- `reports/PHASE2_REPORT.md`: neighborhood e all-stocks filtered.
- `reports/PHASE3_REPORT.md`: PIT aproximado e deep dive.
- `reports/PHASE4_REPORT.md`: Tiingo backfill e rerun final expandido.
- `reports/PHASE5B_ROBUSTNESS_REPORT.md`: ADV20M, janelas WF alternativas e holdout.
- `reports/PHASE5C_ADV5M_OPTIMIZATION_REPORT.md`: otimização local ADV5M pós stale-price guard.
- `plots/phase5/`: performance, equity/SPY e rolling CAGR 1/3/5y para SPY vs ADV5M baseline, focused optimization e aggressive neighborhood.
- `reports/STRATEGY_TESTED_SUMMARY.md`: comparação top-6 decision-relevant.
- `plots/final/`: plots finais preservados.
- `evidence/phase4_tiingo_survivorship_audit/`: auditoria de cobertura Tiingo.
- `evidence/phase5_adv5m_deep_dive/`: deep dive ADV5M preservado.
- `evidence/phase5_single_holdout_adv5m/`: holdout ADV5M preservado.
