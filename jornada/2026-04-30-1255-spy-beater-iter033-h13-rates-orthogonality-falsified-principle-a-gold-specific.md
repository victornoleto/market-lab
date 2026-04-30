# spy_beater_hunt iter 033 — Rates Orthogonality FALSIFICA Principle A (Gold é único)

**Data**: 2026-04-30 12:55
**Iter**: 033 / 50 (66% do orçamento usado)
**Tier**: PROMISING
**Score**: 72/100 (empata com apex iter 030 via QUÁDRUPLA replicação)
**Bars**: 3/3 PASS

## O que testei

A descoberta de iter 030 (KILL #125) foi: trocar o sinal do 4º "constituinte"
do meta-ensemble de QQQ (equity) para GLD (ouro) deu +1pt no score (71→72).
Hipótese plausível: sinais de classes-de-ativos ortogonais à equity dão um
bônus genérico de decorrelação de gates. **Iter 033 testou se isso
generaliza para juros (TLT 20+y, IEF 7-10y) — outra classe ortogonal.**

Mantive filtro=momentum (Princípio G de iter 032) e lookback=126d (Princípio
D de iter 031) fixos; só variei o `signal_ticker` entre QQQ (baseline) /
GLD (âncora) / TLT (novo) / IEF (novo).

## O que achei

**Princípio A NÃO generaliza para juros — é específico do ouro.**

- GLD: score 72 (replica iter 030/031/032 EXATAMENTE — quádrupla repetição
  confirma que a medida é reproduzível)
- QQQ: score ~71 (baseline, sem bônus)
- TLT: score ~69 (PERDE 3pt vs GLD AND fica 2pt ABAIXO do baseline QQQ)
- IEF: score ~68 (idem, 4pt abaixo do GLD)

**Mecanismo (KILL #144 disparado):** ouro tem regime de hedge contra
inflação / ciclo do dólar que descola da bolsa em crises (Y2K, 2008, 2022).
Juros americanos co-movem com a bolsa numa era de política monetária
dominante (Fed sobe na alta, corta na baixa) — então TSMOM em juros NÃO
fornece gating fora-de-fase, ele REFORÇA o drawdown.

**Achado adicional (Princípio K):** o sinal de juros é regime-dependente.
1986-2002 foi a era do "secular bull" de juros (do pico de 1981 ao zero-bound
de 2020), então TLT-momentum-126d ficou predominantemente LIGADO durante
1990-91 e 2000-02 — exatamente quando a bolsa caía. Isso aparece como MDD
asimétrico: TLT lh_56y MDD 47.93% vs spy_real 28.76% (diferença 19pp).

## O que isso significa

- **Princípio A revisado**: o bônus +1pt de iter 030 é específico de ouro
  (mediado por descolamento inflação/dólar-vs-juros), NÃO uma propriedade
  genérica de "ortogonalidade de classe-de-ativo". Mata uma generalização
  promissora.
- **Princípio C revisado** (iter 030 KILL #126): "incoerência sinal-sleeve
  é Pareto-neutra" só vale para commodity-em-equity, não para juros-em-equity.
- **17ª confirmação do teto 72** ao longo de 13 iters sequenciais no eixo
  meta-ensemble. O hunt está plateaurado.

Recomendação para iter 034: **Opção A — declarar hunt re-encerrado**.
Mandato §1 (Plano C 100%) inalterado. iter 030 H10.4 segue como apex
documentado; F1+SPLIT segue como deploy fallback. Se for explorar mais,
(B) testar SLV/DBC ou (D) FX (DXY-momentum) seguindo Princípio J — só
ativos com decoupling estrutural devem reproduzir o bônus.

## Glossário

- **meta-ensemble 4-way**: blend de 4 estratégias (constituintes) com
  pesos iguais ou assimétricos, cada uma com gate próprio
- **gate (Gayed/Faber)**: regra liga/desliga regime-bull/regime-bear
  (ex: SMA-200d, momentum-126d)
- **TSMOM**: Time-Series Momentum (Moskowitz-Ooi-Pedersen 2012). Sinal
  baseado no retorno acumulado dos últimos N dias.
- **KILL condition**: hipótese pré-registrada que, se confirmada, fecha
  uma direção. Anti-overfit per `[advances_fin_ml]`.
- **bônus de ortogonalidade**: +1pt empírico que iter 030 descobriu ao
  trocar QQQ → GLD no 4º slot. Iter 033 mostrou que é específico do ouro.
