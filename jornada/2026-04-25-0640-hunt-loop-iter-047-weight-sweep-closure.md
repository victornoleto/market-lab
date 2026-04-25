# Hunt loop iter 047 — Weight sweep on iter 046 fecha o eixo de assimetria

## Contexto humano

Na iteração anterior (046), o loop achou pela primeira vez uma estratégia
combinada que cruza tudo: 7/7 portões em todos os 3 datasets e DSR sub-0.05
em todos os 3, com score 85/100 STRONG (NEW TOP-K #1). A combinação era
50/50 entre o "stack regime-gated" (iter 041 — pesos calmos vs estresse via
VIX) e a "cesta VRP" (iter 039 — venda de put credit spread em SPY+QQQ+IWM).

A única coisa que faltava para virar WINNER tier (90+) era a **CAGR floor**
— a estratégia tem retorno anual ~9-10%, e o "piso" do gate exige ≥ 80%
do CAGR do benchmark (9.18% edu, 11.98% spy, 15.35% ndx). 50/50 perdia o
piso edu por **0.02pp** (sim, dois centésimos) e os outros dois por
margens maiores.

A pergunta para iter 047 era simples e tentadora: **se eu mexer o peso
para o lado de iter 041 (que tem CAGR de ~13%), eu não recupero o
piso CAGR sem perder muito DSR?** Em outras palavras: existe um ponto
ótimo no meio da fronteira de Pareto entre 50/50 (max DSR) e 100/0
(max CAGR)?

## O experimento

Pré-comprometido grade de 3 configs antes de qualquer dado: `w_041 ∈
{0.50, 0.65, 0.80}` (com `w_039 = 1 − w_041`). Tudo o resto verbatim do
iter 046. Adicional: como agora são 3 configs em vez de 1, aplicar
correção de Bonferroni no DSR (α' = 0.05/3 ≈ 0.0167) — disciplina honesta
para preço de teste múltiplo.

## O resultado (e o que ele significa)

Sharpe e CAGR se moveram exatamente como Markowitz prevê: **Sharpe
desceu monotonicamente** (1.20 → 1.14 → 1.08 em edu) e **CAGR subiu
monotonicamente** (9.16% → 10.34% → 11.50%). Sem ponto ótimo no meio.

O detalhe que mata: o ganho na CAGR floor (apenas o piso edu cruza,
em 65/35 e 80/20) vale +5pts no score. Mas a perda no DSR (raw worst-p
sai de 0.042 → 0.074 → 0.133) vale −5 a −10 pts. Saldo zero ou negativo.

E no 80/20, o piso CAGR do spy ficou a **0.07pp** de passar (11.91% vs
11.98% requerido). Quase. Mas mesmo se passasse, o ndx (11.71% vs
piso 15.35%) continuaria fora — e o gate exige 2 de 3 datasets cruzando.

Pior: o pré-compromisso da grade de 3 configs custa 6 pts no critério
de gates (Bonferroni rejeita G2 em todos os datasets para todas as 3
configs, mesmo onde o iter 046 N=1 passava). O melhor cfg do iter 047
é cientificamente o mesmo 50/50 do iter 046, mas pontuou **79** em vez
de 85, puramente por causa da penalidade de teste múltiplo.

## Veredito

🥇 **STRONG 79/100 frozen / 84 custom-bench**, 2/6 kills firaram
(A: top score < iter 046's 85; B: todas as configs falham Bonferroni-DSR).

iter 046 segue como TOP-K #1. iter 047 fecha rigorosamente o eixo
"assimetria de peso na composição iter 046" — o ótimo era 50/50 desde
o começo, não há ponto melhor nessa direção.

## A lição (e onde focar a próxima)

Três axes que iter 046 deixou abertos para tentar quebrar 90:
1. **Sweep de peso** (FECHADO por iter 047 — o que esta entrada
   documenta)
2. **3-leg + factor-timing** (MTUM/QUAL/USMV momentum 12-1 como 3ª
   perna a 1/3 cada) — eleva a CAGR no NÍVEL DA BASE em vez de
   negociar via score function
3. **Gate de alavancagem na SAÍDA** (VIX<20 → 1.4× iter 046; ≥20 → 1.0×)
   — modula o stream combinado em vez de modificar inputs

iter 048 vai pegar #2 (3-leg + factor-timing). A ideia: se a 3ª perna
adiciona ~10% CAGR e correlaciona com iter 041 abaixo de 0.5, a CAGR
combinada passa de 9-10% para 10-12% no nível da BASE — antes de
qualquer trade-off. Risco: factor timing é também equity-based (pode
correlacionar > 0.5 com iter 041 via beta de mercado).

E uma micro-lição teórica que vale ouro: **uma varredura monotônica de
um parâmetro NÃO PODE revelar um Pareto-optimum não-trivial**. Quando
o score function negocia dois critérios monotônicos no mesmo parâmetro
(Sharpe ↓ vs CAGR ↑ aqui), o ótimo está em um dos dois extremos. Para
encontrar um interior optimum, precisaria de um critério não-linear/
descontínuo (ex: cruzamento de piso). Aqui só o piso edu cruza, e o
ganho de +5pp não compensa a perda de DSR. Isso explica por que o
50/50 (escolhido por iter 046 essencialmente por simetria) acabou
sendo de fato o ótimo do score function.

## Estado consolidado (mandate §1: maintenance)

Mandate §1 segue **MAINTENANCE 100% Plano C**. iter 046 (85 STRONG)
ainda é apenas um CANDIDATO científico — qualquer reativação de slot
de capital depende de override §7 separado, com paper trading prévio,
custos reais de execução, etc. A regra do loop é: produz candidatos,
não posições.

## Citações principais

- `[risk_parity, ch.5]` — base iter 041
- `[volatility_trading, p.218]` — base iter 039 (Sinclair 2013)
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (com N=3 desta vez)
- `[advances_fin_ml, p.222-223]` — DSR com cumulative n_trials
- Markowitz (1952), JoF 7(1) — fronteira Pareto convex-combo
- Bonferroni (1936) — correção α' = α/k para k testes pré-comprometidos

## Próximo passo

iter 048: 3-leg `iter 041 + iter 039 + factor-timing (MTUM/QUAL/USMV
12-1 momentum)` a 1/3 cada. Hipótese: 3ª perna positivamente-CAGR e
suficientemente descorrelada (ρ < 0.5 com iter 041) eleva CAGR combinada
para 10-12% sem perder DSR sub-0.05.

Detalhes técnicos: `studies/strategy_hunt_loop/iterations/047-2026-04-25-0619-iter046-weight-sweep/`
(hypothesis.md, final_report.md, verdict.json).
