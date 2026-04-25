# Hunt loop iter 045 — primeiro acerto da composição out-of-family STRONG-81 (NEW TOP-K #2)

**Status:** 🥇 STRONG, 81/100, **0/6 kills firando** — 1ª varredura limpa
desde iter 039. Mandate §1 segue 100% Plano C. Pesquisa em background.

---

## A pergunta que iter 042/043/044 deixaram

Iter 041 cravou um teto de **84/100** com a regime-stack VIX-binária
(0.7/0.4/0.4 calm × 0.3/0.55/0.55 stress). Quatro tentativas seguidas
de melhorar foram paradas:

- **042 amplitude** (compound 1.7×/1.0× × peso) → 74 (DSR regress)
- **043 frequência** (histerese Schmitt 18/22) → 79 (DSR regress 0.168→0.189)
- **044 input** (composto VIX + T10Y3M, 2 features) → 74 (DSR regress 0.168→**0.240** o pior de todos)

Os três fechavam por mecanismos diferentes — amplitude metia *path
variance* via swings de leverage; frequência introduzia *regime-lag
variance* via transições atrasadas; input enriquecido perdia precisão
porque T10Y3M tem SNR ruim em frequência diária. A conclusão estrutural
era: **iter 041 é um optimum local em 3 eixos ortogonais simultâneos**.

A direção restante, sugerida pela `BASE_MEMORY`: **out-of-family
return-stream addition** — em vez de mexer no portão da iter 041,
**adicionar uma fonte de retorno separada** e deixar a baixa
correlação compor o DSR.

---

## A receita testada

Combinação convexa **50/50** entre dois retornos STRONG-tier
qualitativamente diferentes:

- **iter 037** (3-leg static stack, score 79): 0.6 SPY + 0.45 IEF +
  0.45 GLD a 1.5× leverage. Captura prêmio de termo (IEF carry) +
  prêmio de commodity (GLD) + beta de equity. DSR worst-p 0.222.
- **iter 039** (VRP basket, score 76): T-bill collateral + 1/3 SPY +
  1/3 QQQ + 1/3 IWM em short put credit spread (5/10% OTM, 21 DTE).
  Captura o prêmio de risco de variância (Bondarenko 2014) cross-asset.
  DSR worst-p 0.075.

```
r_combined[t] = 0.5 × r_037[t] + 0.5 × r_039[t]
```

Single config pré-comprometido `iter039_on_iter037_50_50`. **Sem grid,
sem sweep, sem post-hoc tuning.** Os hiperparâmetros das duas
sub-estratégias herdaram verbatim de iter 037 e iter 039. Cumulative
n_trials avança 4309 → 4310 (+1).

A escolha de iter 037 (não iter 041) como base foi crítica: iter 041
já está num optimum local; combinar VRP em cima da regime-gate
reabriria a discussão "perturbação destrutiva". iter 037 é estática,
não-condicional — composição limpa.

---

## A descoberta — a hipótese central da `BASE_MEMORY` é vindicada

**Cross-correlação entre os dois retornos**: corr(r_037, r_039) =
**+0.587 / +0.582 / +0.569** (edu / spy / ndx). Bem abaixo do limiar
Kill F de 0.85 e bem distante da assinatura de iter 032 (corr 0.97
que destruiu a primeira tentativa de composição).

**DSR worst-p**: 0.222 (iter 037 isolado) → **0.0962** (iter 045) —
**redução de 57%**. Em ndx_real, DSR p=**0.0495 — passa sub-0.05 com
gates 7/7**, primeira vez em qualquer iter da família stack-static.

**Sharpe**: combined edu/spy/ndx = **1.10/1.28/1.33** — strict-domina
iter 041 (TOP-K #1) em **todos os 3 datasets** por +0.08/+0.15/+0.16.

**MDD**: combined 22.6/16.3/15.4% — strict-domina iter 041 em todos
3 (Δ −5/−8/−15pp). spy MDD 16.3% é o **2º melhor de qualquer iter
de stack** (depois de iter 039 isolado).

**Walk-forward**: 8/8 nos 3 datasets — **2ª iter da história** a
limpar 8/8 cross-dataset (a primeira foi iter 016).

**Robustness**: 9/9 sub-windows com Sharpe > 0.

**G7 cross-lib**: 0.0000pp em todos 3 (paridade pandas-numpy
perfeita).

**Todos os 6 kills pré-comprometidos limpos** — primeira varredura
completa desde iter 039.

---

## Por que isso não vira WINNER (87+ pontos)

Score breakdown:
- 25/25 Sharpe edge cross-dataset
- 21/25 Gates (edu 6/7, spy 6/7, ndx 7/7 + bonus cross-dataset)
- 10/15 DSR (worst-p 0.0962 cai na banda 0.05-0.10)
- **5/15 CAGR floor** ← o gargalo
- 15/15 MDD ceiling
- 5/5 Robustness

CAGR combinado é **9.7/10.4/10.6%**. O floor exige ≥ 0.8 × benchmark
= 9.18 / 11.98 / 15.35%. Educational passa por pouco; spy falha por
1.54pp; ndx falha por 4.72pp. **Causa direta**: 50% do portfolio é
T-bill collateral (iter 039 isolado tem CAGR 5-6%), arrastando o
combinado pra ~10%.

Os 3 pontos de gap pra iter 041 são **inteiramente no eixo CAGR**.
Iter 045 strict-domina iter 041 em Sharpe / MDD / DSR / gates /
robustness — o único lugar onde 041 ganha é CAGR (13-19%).

---

## O que iter 046 vai testar

A `BASE_MEMORY` vê o caminho direto: **sweep de pesos**. Se aumentar
o peso da iter 037 stack (mais equity exposure), CAGR sobe — mas
DSR pode cair com a queda da diversification benefit.

Pré-comprometido grid 3-4 cfgs:
- (0.4, 0.6) — mais VRP, menos CAGR ainda mas DSR melhor
- (0.5, 0.5) — iter 045 baseline
- (0.6, 0.4) — mais stack, recover CAGR
- (0.7, 0.3) — máximo recover CAGR, perde DSR margin

Bonferroni adjustment no PBO pra evitar grid-overfit. ~2h. Direct
attack on the single-axis blocker.

Se o sweep não conseguir cruzar 84 (i.e., trade-off CAGR↑×DSR↓ é
estrito demais), backup #2: **layer iter 039 sobre iter 041** (não
sobre iter 037) — Sharpe ceiling mais alto, mas risco de interação
com o gate. Backup #3: composição 3-leg com factor-timing
(MTUM/QUAL/USMV).

---

## A receita validada (vai pra knowledge base)

Esse é o primeiro framework de composição empiricamente válido do
loop. Os ingredientes:

1. **Dois componentes independently STRONG-tier** (Sharpe > 1.0 + DSR
   reasonable). Iter 037: 0.98-1.15 / 0.222. Iter 039: 1.14-1.56 / 0.075.
2. **Cross-correlation moderada** (ρ ∈ [0.4, 0.7]). 0.85+ é destrutiva
   (iter 032 falhou em 0.97). Abaixo de 0.4 é raro entre estratégias
   long-bias com equity beta.
3. **Componentes geram retorno via mecanismos qualitativamente
   diferentes** (term/commodity premium vs short-vol harvest). Misturar
   2 estratégias do mesmo "family" tende a ter ρ > 0.85.
4. **Convex combination** (50/50 ou similar), não overlay aditivo.
   Total leverage permanece bounded; iter 045 efetivo = 0.5×1.5 +
   0.5×1.0 = 1.25 vs iter 032 que ia a 2.5.
5. **Diversificação dentro de cada componente** (iter 039 é basket
   3-asset, iter 037 é 3-leg) reduz DD per-leg → composição de DDs
   tem escala manejável.

Iter 032 falhou em 4 dos 5 ingredientes (single-leg components, ρ=0.97,
overlay aditivo, leverage 2.5×). Iter 045 acerta os 5.

---

## Implicações pro mandate

**Nada muda**. Mandate §1 segue 100% Plano C. Mesmo que iter 046
encontre uma config 90+ via weight sweep, isso é **CANDIDATE**, não
deployment. Override §7 separado seria necessário, com paper trading,
slippage real, custos reais (funding cost dos 50% leverage não
modelado em iter 045 — provavelmente −50-80 bps/ano de drag).

A rota Strategy A (Pepperstone CFD) continua DORMANT. O hunt loop é
infraestrutura de proof-of-rigor — quando a estatística for forte o
suficiente pra exigir reativação, o gating §7 é separado.

---

## Files

- `studies/strategy_hunt_loop/iterations/045-2026-04-25-0528-iter039-overlay-on-iter037/`:
  - `hypothesis.md` — pré-commit + 6 kills
  - `combined_037_039.py` — pandas engine
  - `numpy_reference_combined.py` — numpy reference (G7 0.0000pp)
  - `tests/test_iter_045_combined.py` — 10/10 TDD specs
  - `run_backtests.py` — driver
  - `compute_gates_and_score.py` — gates + scoring
  - `results.json`, `verdict.json`
  - `final_report.md` — pleno
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
- `studies/strategy_hunt_loop/BASE_MEMORY.md` — atualizado: TOP-K #2,
  Iters log, Promising directions, structural dead-ends.

Citações: `[risk_parity, ch.5]` (iter 037 base) + `[volatility_trading,
p.218]` Sinclair 2013 (iter 039 base) + `[advances_fin_ml, p.222-223]`
(DSR cumulative) + `[advances_fin_ml, p.31-34]` (G7) + Markowitz 1952
(convex combo) + Erb-Harvey 2006 + Bondarenko 2014 + Carr-Wu 2009 +
Driessen-Maenhout-Vilkov 2009.
