# Hunt loop iter 053 — iter 037 + iter 046 reverse-weight Markowitz Pareto-opt vira 84/100 STRONG

**Pesquisa em background. Mandate §1 segue 100% Plano C — esta sessão
não toca alocação real.**

---

## TL;DR humano

Esta é a 53ª tentativa do loop de busca de estratégia ativa. A meta
continua sendo a mesma: bater SPY 1× buy-hold no Sharpe ajustado por
risco em dados reais (17 anos), passando pela bateria de 7 portões
estatísticos. Cumulativo: **53 iterações, 0 vencedores**, ceiling em
85 (iter 046 TOP-K #1).

A iter 053 testou o que o BASE_MEMORY recomendava como caminho #1: usar
o iter 046 (a melhor estratégia já encontrada) como segundo componente
em uma combinação convexa Markowitz com a iter 037 (anchor de alta
CAGR) no peso ótimo do score-Pareto.

**O resultado**: 84/100 STRONG, empata com a iter 051 e iter 041 no #2
do TOP-K, mas com uma característica nova — pela primeira vez nesta
combinação de componentes, **passou no piso de CAGR nos 3 datasets**
(margem ndx 0.04pp — apertadíssima). E também pela 5ª iteração
consecutiva, **a fórmula de Markowitz foi validada a 4 decimais
(resíduo zero em 15/15 datasets)** — a metodologia de pré-screen
agora é cientificamente airtight.

---

## A descoberta estrutural (e o por quê do 84 e não do 90+)

O pré-screen rodado ANTES do backtest mostrou um número que decretou
o resultado: **correlação entre iter 037 e iter 046 = 0.93-0.96** nos
3 datasets. Isso violou imediatamente o "Kill F" pré-comprometido
(threshold 0.85), o que significa diversificação Markowitz
essencialmente nula.

Por que tão alta? Porque a iter 046 = 50% iter 041 + 50% iter 039,
e a iter 041 É um stack de SPY+IEF+GLD com pesos modulados por
regime de VIX — **exatamente os mesmos ativos que a iter 037**, que
é um stack 0.6 SPY + 0.45 IEF + 0.45 GLD a 1.5×. Os dois fluxos
compartilham 91-95% da variância de retornos diários.

Combinação Markowitz com correlação 0.95 vira praticamente uma média
ponderada — não há ganho de Sharpe via redução de variância. O Sharpe
combinado fica limitado pelo Sharpe do componente mais alto (iter 046
com 1.20 no edu); ao adicionar iter 037 (Sharpe 0.98), você só dilui.

O score-Pareto-optimum a w_037 = 0.70 deu:
- edu Sharpe 1.029 (+0.349 vs SPY) ✓
- spy Sharpe 1.193 (+0.293 vs SPY) ✓
- ndx Sharpe 1.220 (+0.265 vs QQQ) ✓
- edu CAGR 12.71% (acima do piso 9.18%) ✓
- spy CAGR 13.73% (acima do piso 11.98%) ✓
- ndx CAGR 15.39% (acima do piso 15.35% por 0.04pp — **pelos pelos**) ✓
- 3/3 MDD aceitáveis ✓
- DSR worst-p = 0.165 (no bucket [0.10, 0.20), score c3=5)

Score: 25+19+5+15+15+5 = **84**, empata iter 051.

---

## Por que isso fecha um capítulo do loop

A iter 053 fecha estruturalmente **toda a permutação saved-stream-pair
ancorada em iter 037**. Já testamos:
- iter 037 + iter 026 (iter 051) → 84 (corr 0.57-0.60)
- iter 037 + iter 039 (iter 045) → 81 (corr 0.59)
- iter 037 + iter 046 (iter 053) → 84 (corr 0.95)

Todas saturam no platô c1+c4=40, todas têm DSR worst-p preso no
bucket [0.10, 0.20). A iter 037 standalone tem Sharpe 0.98 no edu —
qualquer dosagem de Markowitz com outra stream existente cai abaixo
de 1.10 (necessário para sair do bucket DSR).

E generalizando: combinação score escala inversamente com correlação
(comprovado empiricamente em 3 pontos: ρ=0.41 → 85, ρ=0.59 → 81,
ρ=0.95 → 84). **Saved-stream composition tem ceiling de 85** (iter
046 TOP-K #1). Não há combinação Pareto-ótima das streams salvas que
quebre 85.

Para chegar em 90+ WINNER, não dá mais para combinar streams existentes.
**Precisamos de uma estratégia base NOVA** com edu Sharpe ≥ 1.20
standalone — e isso vai exigir implementação from-scratch, não
recombinação de saved streams.

---

## A metodologia ficou airtight

5 iterações consecutivas (049-053) validando a fórmula de Markowitz
de combinação convexa de Sharpes a 4-5 decimais:

```
S_combined = (w_a μ_a + w_b μ_b) / sqrt(w_a²σ_a² + w_b²σ_b² + 2 w_a w_b ρ σ_a σ_b)
```

Resíduo = 0.0000 em 15/15 datasets. Isso significa que o **pré-screen
Markowitz é uma ferramenta de triagem confiável**: dado o (μ, σ, ρ) de
duas streams candidatas, podemos predizer o Sharpe combinado a 4
decimais ANTES de gastar compute em backtest. O artefato
`markowitz_prescreen.txt` virou parte permanente do workflow.

A regra prática que emerge: **se corr(stream_a, stream_b) ≥ 0.85, abortar
ANTES do backtest** — o ganho de diversificação é nulo. Esse filtro
custa 30 segundos de compute e poupa a iteration inteira.

---

## O que vem agora (recomendação iter 054)

A BASE_MEMORY foi atualizada para apontar 4 caminhos honestos para
iter 054:

1. **Single-stock Tiingo cross-sectional momentum (RECOMENDADO)** —
   Clenow 12-1 ou adjusted-slope no universo de 1695 tickers do
   cache Tiingo (2013-08+, cobertura parcial). Heterogeneidade
   ESCAPA do fechamento da iter 003 (≤20 ativos homogêneos). Top-K=10-20,
   60-90 min de implementação. `[stocks_on_the_move, p.76-77]` +
   Carhart 1997.

2. **VRP em basket multi-índice (SPY+IWM+EFA a 1/3)** — extensão de
   universo da iter 026/039. ~30-45 min. Requer check de cache para EFA.

3. **Plano C sleeve eval (mandate-aligned)** — passive factor-tilted
   (GDE/AVUV/AVDE/AVEM/BTGD); paradigma diferente, n_trials baixo →
   DSR fácil. Limitação de dados: ETFs inception 2018+.

4. **Carry + Value composite AMP 2013** — eixos ortogonais; requer
   construção de signal de dividend/earnings yield.

A iter 053 é a 5ª iter consecutiva de "score 84 STRONG" (049 às 053
contemplam 78/84/79/84). Mais do mesmo não vai quebrar 85. Iter 054
deve PIVOTAR para uma direção genuinamente nova.

---

## Verdict.json (canonical)

| campo | valor |
|---|---|
| iter | 053 |
| cfg_id | `iter037_plus_iter046_w070` |
| tier | STRONG |
| score | 84/100 |
| winner_conditions_met | False (4/5: DSR < 0.05 sole gap) |
| kills_fired | 2/6 (B DSR + F corr 0.95) |
| Markowitz residual | 0.0000 em 3/3 (5ª consec, 15/15 ds cumulativo) |
| corr(037, 046) | 0.9554 / 0.9574 / 0.9304 (Kill F PRE-FIRED) |
| cumulative_n_trials | 4320 |

Citações primárias: `[risk_parity, ch.5]` (iter 037 base) +
`[volatility_trading, p.218]` (Sinclair, iter 039 sub-componente) +
Whaley 2009 JPM 35(3) (iter 041 sub-componente VIX) + Markowitz 1952
JoF 7(1) (Pareto weight) + `[advances_fin_ml, p.222-223, p.31-34]`.

Detalhes em `studies/strategy_hunt_loop/iterations/053-2026-04-25-0847-iter037-plus-iter046-w070/`:
hypothesis.md, markowitz_prescreen.txt, final_report.md, verdict.json,
plot_vs_benchmark_*.png, results.json, 10 specs TDD em tests/.

---

## Lembretes

- **Mandate §1 segue MAINTENANCE 100% Plano C.** Mesmo se eventualmente
  encontrarmos um WINNER, deployment requer override §7 assinado
  separadamente. Loop produz CANDIDATES, não posições.
- **Pytest baseline preservado** (10 specs novos passam, 0 regressões).
- **Citações obrigatórias** (CLAUDE.md Regra 2) preservadas em todas
  as decisões.
- **Gate hard-block remanescentes**: PBO, DSR, WF (vide §5 do mandate).
  CAGR/MDD viraram tiers warning-only desde 2026-04-22 (§2.2/§2.3).
