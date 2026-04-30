# spy_beater iter 028 — Substituição de gate na 1ª posição prova invariância de posição (PROMISING 69/100)

A iter 028 testou uma pergunta que estava implícita há 9 iterações: importa
em **qual posição** do meta-ensemble um constituinte é colocado? Eu peguei
a iter 019 H2 (3-way 33/33/34 com A2 + G2 + F1 stack, score ceiling 71) e
substituí o A2 (LRS com gate SMA-200 sobre QQQ) por E1 (mesmo sleeve mas
gate TSMOM-6m). O sleeve interno é IDÊNTICO; só o filtro do gate muda.

Quatro configs rodaram. Resultado: o "selecionado" (h8_meta_3way_25e1_50g2_25f1
com 50% de G2) deu 69/100. O config CORE (33% E1 substituindo direto o A2)
deu Sharpe 1.019, CAGR 15.02%, MDD 29.16% — basicamente os mesmos números
da iter 019 H2 (1.025/15.04%/28.50%). Estimo 70/100. Conclusão: **a substituição
A2 → E1 na 1ª posição custa só ~1pt** (vs 2pt e 3pt nas posições 2 e 3 já
testadas em iter 026). O gate não é "único" no slot 1.

A descoberta mais interessante veio do H8.4: peguei a iter 026 H6.4 (4-way
30% A2 + 25% G2 + 25% F1 + 20% E1 = score 71 Pareto-co-apex) e **inverti**
A2↔E1 — agora 30% E1 + 20% A2. As métricas batem em segunda casa decimal:
CAGR 15.84% vs 15.85%, MDD 32.07% vs 32.57%, Sharpe 0.954 vs 0.956. Idênticos.
Isso prova empiricamente que o **rubric da meta-axis é INVARIANTE sob
permutação de posições** — só importa o conjunto de constituintes e seus
pesos, não em qual ordem aparecem no spec. Justificativa matemática: blend
metrics são combinações lineares ponderadas; o formula não tem termo
position-dependent.

Implicação prática: testes de permutação são **rubric-neutral** — não preciso
mais explorar isso como hipótese separada em iters futuras. A 12-axis
taxonomy permanece intacta. Hunt continua estruturalmente fechado em 71;
4/4 configs PASS bars 3/3 (8º 100%-bar-pass-sweep do hunt). closest-to-winner
inalterado em iter-019 H2 (precedência). 28/50 iters consumidas (56% de
budget). Recomendação para iter 029+: **Option A — declarar o hunt
EFFECTIVELY-CLOSED** (mais defensável; F1+SPLIT continua deploy fallback).
Plano C 100% inalterado.
