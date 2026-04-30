# spy_beater_hunt iter 034 — Score 73 que não é breach: descobrimos que o rubric depende do grid

**Data**: 2026-04-30 13:18
**Iter**: 034 / 50 — H14 META-ENSEMBLE 5-WAY × GOLD INTERACTION SUB-AXIS
**Tier**: PROMISING **73/100** com bars 3/3 — primeiro número 73 do hunt, mas com asterisco grande.

## O que testamos

Strategic Option C do iter 033: 5-way meta-ensemble com GLD-momentum-126d como **5º** constituinte (até agora era 4-way). Quatro configs: três 5-way variantes (com/sem vol-target no 4º slot, doses 20%/25% de GLD) e um 4-way ANCHOR de sanity-check que replica iter 030 H10.4 EXATAMENTE.

## O que aconteceu (pareceu breakthrough, era artefato)

O selected acabou sendo o 4-way anchor — score **73**, +1pt vs ceiling de 72 sustentado por 4 iters consecutivas. Olhei animado, depois fui investigar: a strategy é literalmente IDÊNTICA ao iter 030 H10.4. Mesmo blend spec. Sharpe 1.041/1.037 em ambos datasets, CAGR 17.03%/16.14%, MDD 33.77%/33.77% — replicado a 4 casas decimais agora 5 vezes (iter 030/031/032/033/034).

Como o score subiu 72→73 se a estratégia é a mesma? **G1 PBO no spy_real**. Esse gate computa overfit no nível do grid de configs siblings da iter — quando os siblings mudam (axis variants em iter 030 vs 5-way variants em iter 034), a ordem de ranking dos configs pelos folds de CV muda, e o PBO da MESMA estratégia varia drasticamente. Na sequência iter 030→034, spy_real PBO foi **0.5159 → 0.8214 → 0.7421 → 0.6905 → 0.1071** — a última passou de FAIL pra PASS, deu +1 gate, +1pt no score.

## Princípio M (novo)

Documentei como **Principle M — Rubric Score Is Grid-Composition-Dependent via G1 PBO**. Implicação grave: todos os deltas de ±1pt entre iters podem ser ruído metodológico, não diferença de estratégia. A própria iter 030 (que "achou" Principle A: GLD-orthogonality bonus +1pt sobre baseline iter 026) pode ter sido o mesmo artefato. Para checar de verdade, precisaria recomputar PBO num grid fixo.

## 5-way puro não quebrou ceiling

Os configs 5-way (H14.1/H14.2/H14.3) sozinhos pontuaram ~71 — empatam com baseline iter 026 H6.1. Decomposição linear validada: 5-way base tax (-1) + GLD bonus (+1) ≈ 0 net. Estrutura 5-way não dá ganho real sobre 4-way E1qqq.

## Decisão e direção

KILL #146 disparou (forma forte de falsificação) mas **não é breakthrough arquitetural** — é só ambiente de medição. iter 030 H10.4 segue como apex real da estratégia em score 72-73 (banda de ruído do rubric). Recomendação iter 035+ continua sendo **Option A** (declarar hunt re-fechado), agora com argumento ainda mais forte: 18 iters mostram ceiling estratégico em 72 com replicação quíntupla; o número 73 desta iter é cosmético.

F1+SPLIT permanece como deploy fallback. Mandate §1 100% Plano C inalterado. 34 iters preservaram 68% do budget. Hunt continua sob mandato §1 MAINTENANCE MODE.
