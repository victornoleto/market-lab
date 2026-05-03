# Day/Swing Strategy Hunt Plan — FX, Gold, Crypto

Status: **draft operacional para executar somente depois** da auditoria Opus do estudo MyFxBook, commit/push dos artefatos pendentes, e autorização explícita do usuário.

Este plano abre uma trilha nova. Ele **não** continua o reverse engineering HappyForex, não reinterpreta as regras Gold falhadas, não reativa Plano A, e não autoriza capital. Capital permanece 100% Plano C; Plano A segue DORMANT até eventual override formal do mandato.

## Premissas

1. O estudo HappyForex falhou como fonte de lógica operacional: M5 e M1 tiveram `0` systems com `fidelity_score >= 0.60`, e o backtest derivado Gold não teve robustez bootstrap/OOS.
2. O Tier 2 Gold também falhou como explicação por over-fire: reduzir os trades sintéticos para `k = n_real_trades` por seleção temporal uniforme deixou os 7 systems com Sharpe, bootstrap e OOS negativos. O oracle ex-post passou em vários, mas só porque escolhe trades olhando PnL futuro; isso é upper bound diagnóstico, não regra executável.
3. A nova busca deve começar por hipóteses próprias, pré-registradas, simples e testáveis, não por tentativa de copiar EAs de vitrine.
4. Swing tem prioridade sobre day trade porque custos, slippage e microestrutura dominam horizontes curtos `[systematic_trading, p.182-197]`.
5. Multi-asset é obrigatório para qualquer hipótese de Strategy A: FX majors, XAUUSD, BTCUSD/ETHUSD e, se a infra permitir, índices líquidos. Single-asset edge não é aceito pelo mandato.
6. CAGR/MDD são tiers informativos; gates estatísticos continuam hard-block: PBO, DSR, walk-forward, OOS, bootstrap, stress e cross-lib `[advances_fin_ml, p.196-211]`.

## Objetivo

Encontrar, ou rejeitar rapidamente, uma estratégia própria e auditável de day/swing trade em FX/Gold/Crypto com:

| Dimensão | Alvo |
|---|---|
| Universo | Multi-asset: FX majors + XAUUSD + BTCUSD/ETHUSD |
| Horizonte preferido | H4/D1 swing primeiro; H1 apenas se custos suportarem; M1/M5 somente como diagnóstico |
| Execução | CFD/Pepperstone research-only; sem capital |
| Evidência mínima | OOS + WF + bootstrap + DSR + PBO quando houver grid |
| Resultado possível | WINNER / PROMISING / DEAD_END / KILL |

## Guardrails

1. **Não rodar antes** da auditoria Opus do MyFxBook terminar e do commit/push dos artefatos pendentes.
2. **Não usar HappyForex como dataset de treino** para novas regras. Pode ser citado apenas como evidência negativa.
3. **Não otimizar thresholds após olhar resultado**. Toda grade deve ser registrada antes do batch `[evidence_based_ta, p.247-260]`.
4. **Não aceitar single-asset winner**. XAU-only ou BTC-only pode virar diagnóstico, mas não candidate deployável.
5. **Não aceitar day trade sem custo realista**. Qualquer H1/sub-H1 precisa stress de spread/slippage e turnover `[systematic_trading, p.182-197]`.
6. **Não fazer paper/live** sem Stage 3 proper e override formal.
7. **Não criar narrativa vencedora com “quase passou”**. Hard-block falhou = FAIL.
8. **Não usar seleção ex-post por PnL**. Qualquer top-K/oracle/best-trades só pode aparecer como upper bound diagnóstico, nunca como estratégia, filtro ou ranking.
9. **Não mascarar over-fire com filtro posterior**. Se a regra dispara demais, o filtro de frequência deve ser pré-registrado por variável observável antes da entrada; `k=n_real` por si só não é regra executável.

## Fase 0 — Reabrir Ou Criar Estudo

Output esperado: `studies/day_swing_strategy_hunt/` ou nome equivalente.

Tarefas:

1. Criar `SPEC.md` com escopo, universo, dados, famílias, gates e kill-switches.
2. Criar `iterations/` para rodadas numeradas, uma hipótese por iteração.
3. Criar `DEAD_ENDS.md` para registrar kills e evitar reabrir ideias ruins.
4. Criar `README.md` humano com status atual e comandos.
5. Reusar infra comum de backtest quando possível; não acoplar ao MyFxBook.

Critério de saída:

| Gate | Critério |
|---|---|
| Spec existe | `SPEC.md` com citações e gates |
| Universo definido | símbolos + frequência + fonte de dados |
| Custos definidos | spread/slippage/commission por asset |
| Kill-switches definidos | antes de qualquer backtest |

## Fase 1 — Dados E Sanity Baseline

Objetivo: provar que os dados e custos não estão enganando o estudo.

Universo inicial recomendado:

| Classe | Símbolos |
|---|---|
| FX majors | EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD |
| Gold | XAUUSD |
| Crypto | BTCUSD, ETHUSD |

Frequências:

| Frequência | Uso |
|---|---|
| D1 | baseline swing, menor custo relativo |
| H4 | swing principal |
| H1 | só se H4/D1 mostrarem sinal |
| M15/M5/M1 | proibido no primeiro ciclo, exceto diagnóstico de execução |

Tarefas:

1. Verificar cobertura OHLC por símbolo/frequência.
2. Construir buy-and-hold/always-flat/always-long baselines por asset.
3. Construir random-entry baselines com mesma frequência de trade.
4. Construir baselines matched-turnover por ativo/frequência, incluindo seleção temporal uniforme e random subsample; isso evita confundir edge com mera redução de turnover.
5. Validar custo por asset e cenário: base, conservador, stress.
6. Produzir `DATA_AUDIT.md` com gaps, horário, timezone e survivorship disclaimer.

Critério de saída:

| Gate | Critério |
|---|---|
| Dados | sem gaps críticos no período testado |
| Custos | definidos para todos assets |
| Baselines | reproduzíveis e salvos |
| Turnover controls | random-entry e uniform-frequency baselines implementados |
| Timezone | UTC documentado |

## Fase 2 — Famílias De Hipóteses Pré-Registradas

Rodar no máximo 5 famílias inicialmente. Cada família precisa de tese, parâmetros congelados e motivo para existir antes de ver resultado.

### Família A — Time-Series Momentum H4/D1

Tese: ativos líquidos tendem a persistir em horizontes intermediários; trend following é uma das poucas anomalias robustas em múltiplos mercados `[systematic_trading, ch.10]`.

Parâmetros iniciais:

| Parâmetro | Grade |
|---|---|
| Lookback | 20, 60, 120 barras |
| Vol target | off, inverse-vol |
| Entry | retorno lookback > 0 |
| Exit | sinal cruza 0 ou trailing time stop |
| Frequência | H4, D1 |

Kill-switch específico: se não bater random-entry e buy-and-hold por Sharpe líquido em pelo menos 2 classes de ativos, encerrar família.

### Família B — Volatility Breakout H4

Tese: expansão de range após compressão pode capturar movimentos direcionais; breakout precisa ser testado com custos e falsos rompimentos `[trading_systems_methods, ch.14]`.

Parâmetros iniciais:

| Parâmetro | Grade |
|---|---|
| Donchian | 20, 55 barras |
| ATR filter | ATR percentile > 50, > 70 |
| Direction | breakout high/low |
| Exit | opposite channel ou fixed holding |
| Frequência | H4 |

Kill-switch específico: se turnover/custos eliminarem o edge em stress spread 2x, encerrar família.

### Família C — Carry/Trend Hybrid FX

Tese: FX pode combinar tendência com proxy de carry/rate differential; carregar sem tendência pode sofrer reversões abruptas `[quant_trading_chan, ch.6]`.

Parâmetros iniciais:

| Parâmetro | Grade |
|---|---|
| Assets | FX majors somente |
| Trend filter | D1 60/120 barras |
| Carry proxy | interest-rate differential se disponível; se não, pular família |
| Position | trend-aligned carry only |
| Rebalance | diário |

Kill-switch específico: se não houver dados confiáveis de carry/rates, não improvisar proxy; pular.

### Família D — Gold Regime Trend/MR Split

Tese: Gold alterna regimes de trend macro e mean reversion intraday; estratégia deve casar mercado e regime porque mercados de menor ruído favorecem tendência e mercados mais ruidosos favorecem countertrend `[trading_systems_methods, p.13-14]`.

Parâmetros iniciais:

| Parâmetro | Grade |
|---|---|
| Regime | realized vol percentile + D1 trend |
| Trend mode | breakout/trend only quando D1 trend positivo/negativo |
| MR mode | somente quando vol baixa e range-bound |
| Frequência | H4/D1, sem M1/M5 |

Kill-switch específico: XAU-only não pode virar winner; precisa melhorar portfólio multi-asset ou virar diagnóstico.

### Família E — Crypto Momentum With Volatility Throttle

Tese: crypto tem momentum forte, mas drawdowns e volatilidade exigem throttle; estratégia sem controle de volatilidade tende a overbet `[volatility_trading, ch.2]`.

Parâmetros iniciais:

| Parâmetro | Grade |
|---|---|
| Assets | BTCUSD, ETHUSD |
| Lookback | 20, 60 D1 |
| Vol throttle | target vol, max vol percentile |
| Cash filter | abs momentum > 0 |
| Rebalance | diário ou semanal |

Kill-switch específico: se performance vier só de long beta crypto sem proteção de drawdown, descartar como não-estratégia.

## Fase 3 — Backtest Honesto Por Família

Cada família deve gerar uma iteração com:

1. Pré-registro da grade.
2. Split temporal: train/validation/OOS ou walk-forward purged.
3. Custos base/conservador/stress.
4. Baselines: buy-and-hold, always-flat, random-entry matched turnover.
5. Over-fire check: `n_trades`, trades/ano e custo total precisam ser comparados contra baselines; estratégia que só funciona antes de custo ou dispara ordens demais morre aqui.
6. Métricas: CAGR, MDD, Sharpe, Sortino, turnover, trade count, exposure, skew, tail loss.
7. Gates: PBO, DSR, WF, OOS bootstrap, stress spread/slippage, cross-lib.

Gates mínimos:

| Gate | Pass |
|---|---|
| DSR | p < 0.05 `[advances_fin_ml, p.196-202]` |
| PBO | < 0.5 `[advances_fin_ml, p.208-211]` |
| WF | ≥ 6/8 positive windows |
| Bootstrap | 99.9% CI low > 0 |
| OOS | final block Sharpe > 0 and CI low > 0 |
| Cost stress | remains positive under conservative spread/slippage |
| Cross-lib | CAGR within ±3pp between implementations |
| Turnover sanity | edge survives matched-turnover random baseline |

## Fase 4 — Portfolio-Level Test

Não escolher estratégia isolada sem testar interação multi-asset.

Tarefas:

1. Combinar apenas famílias que passaram gates próprios.
2. Testar equal-risk, equal-weight e volatility target.
3. Medir correlação com Plano C e SPY/VT proxies.
4. Verificar se melhora risco/retorno após custos, não apenas aumenta alavancagem.
5. Rodar drawdown cluster analysis para crises: COVID, 2022 rates, crypto crashes, gold spikes.

Critério de saída:

| Resultado | Ação |
|---|---|
| 0 famílias passam | Encerrar hunt como DEAD_END |
| 1 família passa mas single-asset | Diagnóstico, sem deploy |
| ≥2 famílias passam em classes diferentes | Candidate para Stage 3 proper |
| Portfolio passa todos gates | Escrever `FINAL_REPORT.md`, ainda sem paper/live |

## Fase 5 — Paper Trading Somente Condicional

Paper só entra após Stage 3 proper e autorização explícita.

Pré-condições:

1. Gates hard-block todos PASS.
2. Código reproduzível com seed e ambiente fixos.
3. Cost model documentado e conservador.
4. Slippage stress documentado.
5. Broker constraints verificados.
6. Mandate §7 override draft preparado, mas não assinado automaticamente.

Paper mínimo:

| Item | Critério |
|---|---|
| Duração | 3-6 meses |
| Conta | demo ou micro capital aprovado |
| Métrica | paper vs expected distribution |
| Kill | drift de execução, slippage excessivo, drawdown fora CI |

## Primeira Sessão Recomendada

Executar somente após Opus finalizar e repo estar commitado/pushado.

Ordem:

1. Criar `studies/day_swing_strategy_hunt/` com `SPEC.md`, `README.md`, `DEAD_ENDS.md`, `iterations/`.
2. Escrever `DATA_AUDIT.md` para universo FX/Gold/Crypto em D1/H4.
3. Implementar baselines simples, random-entry matched-turnover e uniform-frequency controls.
4. Implementar uma proteção explícita contra oracle: qualquer função que selecione trades por PnL futuro deve ficar em módulo diagnóstico e marcada `nontradeable`.
5. Rodar apenas Família A em smoke com poucos parâmetros, sem tuning amplo.
6. Se smoke quebrar ou custos dominarem, corrigir infra antes de novas famílias.

Não fazer na primeira sessão:

1. Não rodar todas as famílias de uma vez.
2. Não usar M1/M5.
3. Não otimizar threshold manualmente.
4. Não criar conclusão de winner.
5. Não iniciar paper.
6. Não rodar top-K por PnL futuro como se fosse estratégia.

## Kill-Switches Globais

| Kill | Condição | Ação |
|---|---|---|
| K1 | Dados/custos não confiáveis | parar antes de backtest |
| K2 | Baseline random-entry iguala estratégia | DEAD_END da família |
| K3 | PBO ≥ 0.5 | DEAD_END da família |
| K4 | OOS bootstrap low ≤ 0 | FAIL, sem exceção |
| K5 | Edge some em spread/slippage stress | FAIL |
| K6 | Melhor resultado é single-asset | diagnóstico, sem deploy |
| K7 | 0 famílias passam | encerrar hunt |
| K8 | Edge depende de oracle/top-K ex-post | diagnóstico apenas, sem estratégia |
| K9 | Edge depende de reduzir turnover sem filtro observável pré-registrado | FAIL |

## Definição De Sucesso

Sucesso não é “achar algo a qualquer custo”. Sucesso é uma destas saídas:

1. **WINNER research-only**: estratégia multi-asset passa todos gates e justifica Stage 3/paper futuro.
2. **PROMISING**: passa parte relevante, mas tem lacuna explícita; não deployável.
3. **DEAD_END honesto**: falha rápido, documentada, sem consumir capital.

Depois do MyFxBook, o padrão correto é priorizar eliminação honesta. Uma estratégia interessante só existe se sobreviver a custos, OOS e anti-overfit; qualquer coisa abaixo disso é narrativa, não sistema.
