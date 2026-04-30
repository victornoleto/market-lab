# spy_beater_hunt iter 032 — Filter-type não substitui o joint-optimum

## O que rodamos

Iter 032 foi o 16º iter ao meta-ensemble axis. Mantivemos a estrutura
4-way (A2 QQQ-SMA + G2 SPY-SMA + F1 stack + GLD-source) com pesos
25/25/25/25, signal-asset fixo em GLDSIM e lookback no pico de 6m
(que iter 031 confirmou como ASSET-INVARIANT). Variamos apenas o
**filter-type** do 4º componente: momentum (baseline iter 030/031),
SMA-126d, EMA-126d, e SMA-200d (gate Faber-canônico de commodity).

## O que descobrimos

O iter 030 H10.4 alcançou ceiling 72 (única quebra em 9 iters
consecutivos). Iter 031 mostrou que esse +1pt **não vinha do
lookback** (todos os outros lookbacks em GLD perdiam o bônus).
Iter 032 mostra que **também não vem só do asset-class**: trocar de
momentum para SMA/EMA — mesmo mantendo gold + 126d — perde 1-3pt do
bônus.

O resultado mais interessante foi inverter Principle B (2/3-axis
sufficient): SMA-126d (asset+lookback distintos = 2/3 axes) acabou
**pior** que SMA-200d (só asset distinto = 1/3 axis). Ou seja, o
manifold de distinctness não é uniforme — o filtro slow-trend de 200d
preserva mais bônus na commodity gold do que filtros faster (126d
SMA/EMA), porque o gate-mechanism em si interage com a vol-profile do
ouro (~14-18%, ciclos longos, mercados sideways).

Três princípios novos saem disso:
- **G**: o bônus de orthogonality é FILTER-TYPE-COUPLED (só momentum
  no GLD entrega o +1pt no joint optimum).
- **H**: a distinctness é não-uniforme (axis-count não prevê retenção).
- **I**: filtros slow-trend preservam melhor o bônus em commodity-class
  signals que filtros fast-trend.

A leitura final: o ceiling de 72 alcançado em iter 030 é
**joint-optimum-specific** (asset × filter × lookback). Single-axis
substitution por qualquer eixo perde 1-3pt — confirmado agora ao longo
de 8 células sub-axis no GLD-source. F1+SPLIT segue como deploy
fallback. Mandate §1 Plano C 100% inalterado.

## Onde estamos

- 32/50 iters consumidas (64% do orçamento preservado)
- Ceiling 72 confirmado em 12 meta-axis iters consecutivos
- closest-to-winner segue iter 030 H10.4 (precedência)
- Recomendação minha (não decisão do usuário): hunt RE-CLOSED, mais
  iters single-axis no GLD são pouco produtivas. Opções alternativas
  (DBC/BCOM/USDJPY com momentum-126d) exigem nova infra de dados.
