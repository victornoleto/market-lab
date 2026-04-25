# Hunt loop iter 035 — Static stack SPY+GLD (drop-in IEF→GLD substitution) vira 77/100 STRONG, **TIES o teto iter 015 vindo de uma classe de ativo diferente** — 77 ceiling agora confirmado architecture-bound, NOT bond-specific

**Data:** 2026-04-25 01h42
**Contexto:** Pesquisa em background. Modo MAINTENANCE 100% Plano C
permanece o estado de produção (mandate §1). O hunt loop é
diagnóstico, não gera deployment.

---

## TL;DR

Iter 035 fez um teste *diagnóstico*: trocar o IEF (bond 7-10y) do
iter 015 por **GLD (ouro)** no exato mesmo formato 0.9/0.6 com
leverage 1.5×. A pergunta: o edge do iter 015 (77 STRONG, top-K #4)
vem do **carry de bonds** (term premium) ou da **diversificação em
si** (qualquer 2ª perna baixa-correlação serve)?

**Resultado**: 🥇 **STRONG 77/100** — empata o teto do iter 015
**vindo de uma classe de ativo qualitativamente diferente**.

- Sharpe edu/spy/ndx: **0.877 / 1.070 / 1.103** (Δ015 **+0.094 /
  +0.026 / +0.040** POSITIVO em todos os 3 — primeira vez no loop
  inteiro que uma variação de iter 015 BATE iter 015 em Sharpe nos
  3 datasets).
- DSR worst-p: **0.344** (edu) — **−0.205 absoluto vs iter 015's
  0.548**, a maior melhoria de DSR já vista na família static-stack.
- MDD: **3/3 datasets sob o ceiling** (iter 034 tinha breach de
  +1.99pp em ndx; iter 035 tem margem +3.17pp clean).
- Robustness: **9/9 sub-windows** Sharpe > 0.

Mas o score também trava em **77**, mesmo ponto byte-por-byte do
iter 015, porque o rubric só dá pontos quando os ganhos cruzam
gates ou DSR thresholds, e mesmo o DSR melhor de 0.344 ainda fica
acima do Kill C threshold (0.20) e MUITO acima do gate G2 (0.05).

---

## A descoberta estrutural (4 iters, mesmo arquitetura, mesmo teto)

| iter | diversificador | mecânica | Sharpe (edu/spy/ndx) | DSR worst-p | MDD ndx | score |
|---|---|---|---|---|---|---|
| 015 | IEF (7-10y bond) | base 2-leg static | 0.78/1.04/1.06 | 0.548 | 39.5% | **77** |
| 032 | IEF + VRP overlay | composição | 0.81/1.04/1.08 | 0.502 | 44.4% breach | **72** |
| 033 | TLT (20-30y bond) | substituição duração | 0.85/1.04/1.06 | 0.313 | 47.0% breach | **72** |
| 034 | IEF+TLT spread sleeve | composição duração | 0.79/1.06/1.08 | 0.529 | 42.1% breach | **72** |
| **035** | **GLD (gold)** | **substituição classe** | **0.88/1.07/1.10** | **0.344** | **37.0%** ✓ | **77** |

**A leitura honesta**:
- Iter 015 (bond) e iter 035 (ouro) **chegam ao mesmo teto 77** com
  decomposição quase idêntica: 1:25 + 2:17 + 3:0 + 4:15 + (5:15 ou
  5:15) + 6:5.
- A única diferença pontual entre iter 015's 77 e iter 035's 77 é
  que o iter 035 tem números **estritamente melhores** em todos os
  3 axes (Sharpe, DSR, MDD), mas o rubric não premia ganhos abaixo
  dos thresholds.
- Iter 032/033/034 (variações no eixo bond) caem todos em 72 porque
  cada um tem seu próprio breach: 032 explode MDD por composição
  com VRP (corr_SPY=+0.97), 033 explode MDD por dobrar variância de
  duração, 034 reduz MDD mas Sharpe mexe pouco demais pra DSR.

**Conclusão**: o platô do iter 015 a 77 **não tinha nada a ver com
bond carry** — é uma propriedade intrínseca da arquitetura
"static-stack 2-perna 90/60 com leverage 1.5×" no n_trials atual
(4294). Ouro (zero carry, ligeiro contango histórico) e bonds (term
premium positivo) extraem **a mesma quantidade de Sharpe per trial**
nessa caixa. O que importa é a diversificação, não a classe.

---

## A pegadinha do "Sharpe melhor mas mesmo score"

Por que iter 035 **bate iter 015 em todas as métricas mensuráveis**
mas tira o mesmo 77/100? Porque o rubric é categórico:

- Criterion 1 (Sharpe edge): só conta se Sharpe ≥ benchmark + 0.10.
  Tanto iter 015 quanto iter 035 cruzam isso em 3/3 datasets →
  ambos 25/25.
- Criterion 3 (DSR): só conta se p < 0.20 (5pts), p < 0.10 (10pts),
  ou p < 0.05 (15pts). Iter 015 (p=0.548) e iter 035 (p=0.344)
  estão ambos **acima de 0.20** → ambos 0/15.
- Criterion 5 (MDD ceiling): aqui SIM iter 035 ganhou — iter 034
  tinha breach em ndx; iter 035 (35.12% < 40.12% ceiling) ✓ →
  15/15 vs iter 034's 10/15.

Então se a comparação é iter 015 vs iter 035, ambos têm 77 idênticos
mas iter 035 está **estruturalmente mais perto da fronteira** — o
DSR caminhou ~1/3 do caminho até o threshold. Se iter 035 tivesse
movido edu DSR de 0.344 → 0.19 (cruzar Kill C threshold pra 5pts),
seriam **82**.

---

## O que isso significa pro hunt loop

**Direções FECHADAS** (definitivamente):
- Variações de classe-de-ativo no diversificador único do 2-perna
  static stack 90/60. Bond e ouro independentemente confirmam o teto
  77. DBC, GSG, USO (commodity baskets), VNQ (REITs), EMB (EM bonds),
  ZROZ/EDV (ultra-long bonds) — todos vão bater no mesmo teto.

**Direção REOPENADA**:
- **3-leg ADDITIVE static stack** (SPY + IEF + GLD compound, e.g.,
  0.9/0.4/0.4 com leverage 1.7×). Não substituição: empilhar bonds
  E ouro como diversificadores paralelos. Tese: dois diversificadores
  ortogonais (term premium + safe-haven/inflation hedge) podem
  *somar* Sharpe ao invés de saturar. Iter 010 testou isso em formato
  vol-managed (74); iter 034 testou em formato 3-leg static mas só
  com bonds (72). 3-leg static com cross-asset diversificadores
  paralelos ainda é UNTOUCHED. **~30 min, próxima iter.**

**F-FX morta por dados**: a recomendação top do iter 034 era FX
carry overlay (long AUDUSD + short USDJPY). Mas a Tiingo cache só
tem FX spots de 2020-01-01 em diante (1957 bars / 6 anos), o que é
insuficiente pra cross-dataset validation (spy_real precisa de
2009+, ndx_real de 2010+). Não é fechamento estrutural — é falta
de dados. Direção parqueada até identificar fonte alternativa
(KMPV 2018 supplementary, AQR factor library).

---

## Os números honestos vs SPY 1× buy-hold

Iter 035 backtested net (sem funding cost real, sem 15% DARF):

| dataset | strategy CAGR | benchmark CAGR | Δ | strategy MDD | bench MDD | gate? |
|---|---|---|---|---|---|---|
| educational | 17.42% | 11.47% (SPYSIM 40y) | +5.95pp | 48.67% | 55.14% | 5/7 |
| spy_real | 20.28% | 14.97% (SPY 17y) | +5.31pp | 32.44% | 33.70% | 6/7 |
| ndx_real | 23.67% | 19.18% (QQQ 16y) | +4.49pp | 36.95% | 35.12% | 6/7 |

Pegadinha 1: o stack sintético não modela funding cost dos futuros
(50% notional adicional). Em produto real (como NTSX) seria −50 a
−100 bps/ano. Sharpe haircut estimado: −0.05 a −0.10 em 17y. Pós
funding-cost, edge real provavelmente +0.10 a +0.15 Sharpe (ainda
no gate, mas borderline).

Pegadinha 2: ouro tem retornos altamente regime-dependentes. O
período 2004-2026 contém:
- 2004-2011 bull market clássico do ouro (+~17%/yr)
- 2011-2018 bear de ouro (−~3%/yr)
- 2019-2026 retorno do bull (+~10%/yr)

Se o sample fosse 2011-2018 only, GLD seria diversificador ruim e
o iter 035 ia regredir vs iter 015. O 21y window média desses
regimes mas em produção um sample 7-anos azarado pode invalidar a
tese.

---

## Próxima iter

Iter 036 PICK: **G-3LEG additive 3-leg static stack** —
0.9 SPY + 0.4 IEF + 0.4 GLD (lev 1.7×) ou 0.9 / 0.6 / 0.3 (lev 1.8×).
Reusa o `apply_static_stack_3leg` do iter 034 verbatim (só passa
GLD onde iter 034 passava TLT). Pre-committed outcomes:
- ≥80 = primeira ruptura real do teto 77 → família multi-leg cross-
  asset abre como direção viva.
- ~77 = teto não é asset-bound nem 2-vs-3-leg-bound mas leverage-
  bound (1.5× → 1.7× não muda nada). Só não-static (regime/ML/CS)
  pode quebrar.

Se G-3LEG ficar em 77 também, o hunt loop precisa fazer um pivô
hard pra **non-static architecture** — meta-labeling AFML ch.3,
HMM regime-aware leverage, ou cross-sectional factor timing (≥10
ETFs). Custo 2-4 h, mas é o único mecanismo não exaurido nesse
n_trials budget.
