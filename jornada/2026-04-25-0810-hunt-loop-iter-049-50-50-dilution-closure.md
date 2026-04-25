# Hunt loop iter 049 — 50/50 dilução fecha o eixo "additive 3rd stream com Sharpe baixo" sobre iter 046

🥉 **MARGINAL, 59/100 frozen / 64 custom, 4/6 KILLS firando — REGRESSÃO de 26 pontos vs iter 046's 85, a maior queda single-iter da história do loop.**

iter 049 testou a primeira hipótese ADITIVA depois que iter 044/047/048
fecharam todos os 3 eixos de modulação no iter 046 (input gate /
weight asymmetry / output leverage). A predição da iter 048 era firme:
**caminho pra 90 deve ser ADITIVO** (3ª stream uncorrelated), não
modulativo. iter 049 implementou a versão mais natural: 50/50 convex
combo de iter 046 saved stream + **Gold TSM 90d** (filtro booleano de
trend sobre GLD; long se trailing-90d return > 0, cash em rf=2% caso
contrário).

A predição: corr(046, gold) ≈ 0.10-0.30 (iter 041 já tem GLD mas
estaticamente, sem filtro), Sharpe combinado ~1.11, score 80-86. A
realidade: **corr 0.52-0.53** em todos os 3 datasets (Kill C fires —
ceiling era 0.50). A razão estrutural: iter 041 carrega GLD em peso
0.40 (calm) / 0.55 (stress), e gold TSM está long 67% das barras —
quando ambos estão long GLD, o processo de preço é compartilhado e a
correlação não pode ser baixa.

Sharpe combinado **0.92/1.02/1.03** (vs iter 046's 1.20/1.32/1.38,
queda de **−0.29/−0.31/−0.35** — Kill A pelo maior margin do loop).
DSR worst-p **explode** de 0.044 → 0.32 (8× pior; G2 falha em todos
os 3 datasets; Kill B fires). Score regrediu de 85 para 59, com −15
pts no critério DSR (de 15→0, atravessando todos os buckets de uma
só vez), −6 pts em gates, −5 pts em Sharpe edge. Kill D fires (score
< 85). G7 cross-lib limpo em 0.0000pp; gold TSM standalone Sharpe
0.61-0.69 (consistente com Moskowitz-Ooi-Pedersen 2012; Kill F clean).

**A lição é matemática, não empírica.** Aplicando a identidade Markowitz
de portfolio combinado a S_a=1.32, S_b=0.69, ρ=0.53, w=0.5:
combined Sharpe = 1.03 (a fórmula prediz exatamente o observado 1.02).
Mais surpreendente: mesmo com **ρ = 0** (orthogonality perfeita), a
fórmula dá combined Sharpe = 1.25, **AINDA ABAIXO** do iter 046's 1.32
standalone. **A 50/50 weighting é sub-ótima REGARDLESS de ρ quando
os Sharpes são desiguais.** O peso ótimo sob utilidade quadrática é
w_gold ≈ 9%, NÃO 50%.

A lição retroativa: iter 046's 50/50 funcionou porque seus componentes
(iter 041, S=1.03; iter 039, S=1.05) tinham Sharpes quase iguais. iter
049 herdou o 50/50 simétrico SEM verificar que o novo componente
(gold TSM, S=0.69) era Sharpe-comparable. Não era. O pre-commitment
de 50/50 no spec foi o que armou o kill.

**5 eixos distintos agora fechados em iter 046**: input gate (044),
weight asymmetry (047), output leverage (048), 50/50 additive
lower-Sharpe stream (049), trivial gate-perturbation (042/043). O
iter 046 score=85 é diagnosticamente um **ponto Pareto-ótimo
apertado** — cada direção natural de enhancement foi testada e
dominada. Isso é informação utilíssima: estreita brutalmente o espaço
de hipóteses pra iter 050+.

Iter 050 PICK: **w_gold = 0.10 single cfg** sobre o mesmo gold TSM
(~Markowitz optimum dado os Sharpes/correlation observados). Predição:
score 86-88 (passa CAGR floor edu por margem pequena, sem DSR collapse,
small MDD melhora). Custo ~30 min wall-time, 1 cfg, sem Bonferroni.
Backup #2: pre-screen ρ < 0.30 candidate (TSM em USO/TLT/SLV) ANTES
de comprometer um backtest. #3: abandonar iter 046 base e testar
combinações alternativas (iter 037 + iter 026; iter 041 com asset-triple
diferente).

**Cumulative n_trials: 4315 → 4316.** Mandate §1 segue 100% Plano C
passive factor-tilted; pesquisa em background, sem implicação de
deployment.

Citações: `[systematic_trading]` (Carver TSM) + `[risk_parity, ch.5]`
+ `[volatility_trading, p.218]` (iter 046 base) + `[risk_parity,
p.27-29, ch.2]` (gold price-return dominates roll yield) +
`[advances_fin_ml, p.222-223]` (DSR cumulative n_trials) +
`[advances_fin_ml, p.31-34]` (G7) + Moskowitz-Ooi-Pedersen 2012 JFE
104(2) 228-250 DOI 10.1016/j.jfineco.2011.11.003 (TSM commodities)
+ Markowitz 1952 JoF 7(1) 77-91 (convex combination Sharpe identity
— a chave do post-mortem matemático).

Ver `studies/strategy_hunt_loop/iterations/049-2026-04-25-0705-iter046-plus-gold-tsm/`
(hypothesis.md, gold_tsm.py, run_backtests.py, compute_gates_and_score.py,
final_report.md, results.json, verdict.json, plot_vs_benchmark_*.png,
tests/test_iter_049_gold_tsm.py com 15 specs — all pass).
