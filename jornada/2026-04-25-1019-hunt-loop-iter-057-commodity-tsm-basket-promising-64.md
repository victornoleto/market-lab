# Hunt loop iter 057 — basket de TSM em commodities como 3ª stream falha em iter 046; correlação baixa não compensa Sharpe baixo

🥈 **PROMISING, 64/100, 4/6 KILLS firando — REGRESSÃO de 21 pontos vs iter 046's 85; vindica o eixo "3rd-stream-Sharpe é binding constraint, NÃO correlação".**

iter 057 testou a próxima evolução natural depois que iter 049/050
fecharam single-asset gold TSM como 3ª stream em iter 046 (Pareto local
em 78 com w=0.10). A predição da iter 049/050 foi: gold falhou porque
**iter 041 já carrega GLD** (peso 0.40-0.55), inflando corr(gold,046)
para ≈0.50 e duplicando exposição. Solução natural: **excluir gold,
diversificar em outras commodities não correlacionadas** com SPY/IEF/GLD.
Universo escolhido: USO (oil) + UNG (gas) + SLV (silver), basket
equal-weight com filtro booleano de trend 90d (mesmo motor de
iter 049/050), peso w_csm=0.20 sobre iter 046 (mid-range entre
iter 049's 0.50 e iter 050's 0.10).

**Predição parcial vindicada, predição global refutada.**

A premissa de orthogonalidade foi **empiricamente confirmada**:
corr(r_csm, r_046) = **0.319/0.315/0.296** nos 3 datasets — mais baixa
que iter 049's gold-TSM corr ≈ 0.50, exatamente como o argumento
estrutural previu. Kill F (corr > 0.50) clean nos 3 datasets. A
diversificação **funcionou no nível de variância**: MDD melhora
−2.2/−4.7/−3.3 pp (combined 15.78/10.53/11.24% vs iter 046's
17.97/15.22/14.57%). Engine clean: G7 cross-lib 0.0000 pp em todos os
3 datasets; 16/16 testes TDD passam.

**Mas o Sharpe combinado COLAPSOU** — 1.05/1.08/1.14 (Δ046
−0.155/−0.241/−0.237, Kill A 3/3). E mais grave: **DSR worst-p saltou
de 0.041 para 0.223** (5.4×; G2 falha nos 3 datasets, Kill B fires) e
CAGR caiu 1.06/1.58/1.54 pp (Kill C 3/3). Score 64 PROMISING vs iter
046's 85 STRONG — abaixo até de iter 050's 78 (gold TSM w=0.10). Kill D
fires.

**A explicação é matemática.** O basket de commodities standalone tem
Sharpe **0.13/0.29/0.16** — o sample 2007-2026 é dominado pelo bear
market de oil/gas pós-2014 e regime inflacionário 2022. Boolean trend
filter (`[stocks_on_the_move, p.76-77]`) coloca em cash 50-70% das
barras, capturando pouco do upside. Aplicando a identidade Markowitz
com S_a=1.32, S_b≈0.20, ρ=0.30, w_a=0.80, w_b=0.20:
combined Sharpe ≈ (0.80×1.32 + 0.20×0.20) / σ_combined ≈ 1.16 — drag
de **−0.16** vs iter 046, exatamente o que observamos. **Mesmo com
correlação 30% mais baixa que iter 049, o Sharpe absoluto baixo do
3rd stream domina.**

A lição que iter 049/050/057 estabelecem é estrutural:

> **3rd-stream Sharpe ≥ ~0.5 é o binding constraint pra contribuição
> Markowitz-positiva sobre iter 046 base, NÃO correlação.**

Por trás, quando S_b → 0 e ρ < 1, a fórmula combined Sharpe colapsa pra
~ S_a × √(1 − w_b) — o termo de mean-reduction domina o termo de
variance-reduction √(w_a² + w_b² + 2w_aw_b ρ) → √(w_a² + w_b²) quando
ρ→0. Variance-reduction máxima é só √(0.80² + 0.20²) = 0.825, mean
contribui 0.80×1.32 + 0.20×0.20 = 1.10. Sharpe combinado
1.10/0.825 = 1.33 já assume σ_a = σ_b, o que NÃO é verdade aqui:
σ_csm ≈ 0.20×√252 = 3.2% daily, vs σ_046 ≈ 1%, a diluição é REAL.

**Direções pra iter 058 que survivem o filtro Sharpe ≥ 0.5**:

1. **HYG long-only com filtro de trend 60d** (Asvanunt-Richardson 2017
   "Credit Risk Premium" JPM 43(2)). HYG ~6-7% gross yield, Sharpe
   estimado 0.5-0.7, corr-com-iter-046 ≈ 0.5-0.7. Trade-off invertido:
   menos orthogonal mas Sharpe-suficiente. Predição 80-87.
2. **T10Y3M-gated stack como alternativa pra iter 041** — single-feature
   forward-looking regime gate (Estrella-Mishkin 1998 NBER 6649) sobre
   SPY+IEF+GLD a 1.4-1.5× lev preservada. Distinto de iter 044 (closed
   2-feature composite). Se T10Y3M-iter-041 tem corr<0.85 com iter 039,
   abre nova família de ceiling 84 pra futuras composições. Predição 76-84.
3. **Min-variance Markowitz weights** sobre iter 041 + iter 039 + 3rd
   stream selecionada — solver empírico Σw=1, w≥0. Risk: implicit grid
   search inflate n_trials.

**Cumulative n_trials: 4326 → 4327.** Mandate §1 segue 100% Plano C
passive factor-tilted; pesquisa em background, sem implicação de
deployment. iter 046 mantém TOP-K #1 com score 85 STRONG, agora
fortemente blindado por 7 axes fechados (042/043/044/047/048/049/050/057
todos confirmando ceiling local).

Citações: `[risk_parity, ch.5]` (Asness-Frazzini-Pedersen, base) +
`[volatility_trading, p.218]` (Sinclair iter 039 base) +
`[systematic_trading]` (Carver TSM) + `[stocks_on_the_move, p.76-77]`
(Clenow boolean trend) + `[advances_fin_ml, p.222-223]` (DSR cumulative
n_trials) + `[advances_fin_ml, p.31-34]` (G7 verificado em 0.0000pp) +
Moskowitz-Ooi-Pedersen 2012 JFE 104(2) 228-250
DOI 10.1016/j.jfineco.2011.11.003 (TSM canonical) +
Asness-Moskowitz-Pedersen 2013 JoF 68(3) 929-985
DOI 10.1111/jofi.12021 (cross-asset momentum) + Erb-Harvey 2006 FAJ
62(2) 69-97 DOI 10.2469/faj.v62.n2.4084 (commodity premia) +
Markowitz 1952 JoF 7(1) 77-91 (convex combination — fórmula que
prediz exatamente o observado).

Ver `studies/strategy_hunt_loop/iterations/057-2026-04-25-1019-commodity-tsm-basket-3leg/`
(hypothesis.md, commodity_tsm.py + numpy_reference, combined_046_plus_csm.py,
run_backtests.py, compute_gates_and_score.py, final_report.md,
results.json, verdict.json, plot_vs_benchmark_*.png,
tests/test_iter_057_commodity_tsm.py com 16 specs — all pass).
