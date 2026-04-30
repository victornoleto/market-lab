# spy_beater iter 015 — Levered All-Weather entra como 7ª família, vira Sharpe-king mas perde no rubric CAGR-anchored

A iter 014 fechou a pergunta de cross-product: o hybrid TSMOM-gate ×
TQQQ-sleeve scored 65, abaixo do teto 67, e a orthogonality assumption
do KILL #33 foi rejeitada (mas na direção errada — hybrid ABAIXO da
union-of-single-axis). Hunt continuou CLOSED. A última família formal
no `PROMISING_DIRECTIONS.md` que ainda **não** tinha sido testada
explicitamente era a **balanced multi-asset com leverage** — Dalio
All-Weather + Asness 1996 "Why Not 100% Equities?". Iter 015 fecha
esse buraco.

Três configs F1 (always-on, sem regime gate, sem vol-target):
`f1_aw_baseline_1x` (canônico Dalio: 30 SPY + 55 TLT + 15 GLD), 
`f1_aw_stack_15x` (capital-efficient: 35 NTSX + 30 GDE + 20 TLT + 15
KMLM, ~1.41× notional sem LETF decay) e `f1_aw_letf_2x` (LETF mix
agressivo: 30 UPRO + 25 TMF + 15 IEF + 15 UGL + 15 KMLM, ~2.25× notional
com 3-4%/y decay drag).

Resultado: **PROMISING 61/100 selected** (`f1_aw_stack_15x`), todas as
3 barras passam (`winner_conditions_met=True`), mas score 6 pts ABAIXO
do closest-to-winner (iter 006 = 67). **KILL #46 disparou** (best F1 ≤
67 — 7ª família reforça KILL #33). **KILL #47 não disparou** (best 61
< 70 — hunt não reabre). **KILL #48 disparou** (CAGR monotonicamente
positivo na alavancagem 1×→1.41×→2.25% nos DOIS datasets: lh
8.70→11.60→16.11%, spy 8.06→12.30→16.61%). **KILL #49 disparou** (1×
puro Dalio mean CAGR 8.38% < 11.21% — confirma 30+ anos de literatura
empírica do Bridgewater All-Weather).

**Achados-NOVOS (primeira vez no hunt)**: (1) **Sharpe > 1.0** — F1
stack mean Sharpe = **1.018** (1.004 lh, 1.032 spy_real). Todas as 14
iters anteriores em 6 famílias + 1 hybrid capeavam em ~0.804 (iter
006). (2) **Melhor MDD entre os configs que passam o CAGR bar**:
**26.82%** mean. D1 tem MDD geral melhor (35.27%) mas mal passa o CAGR
(12.83%). F1 stack 26.82% MDD com CAGR 11.95% é Pareto-superior em
risk-adjusted return. (3) **Capital-efficient stacking PARETO-DOMINA
LETF mix**: F1 stack 1.41× notional → Sharpe 1.018 / MDD 26.82%; F1
LETF 2.25× notional → Sharpe 0.90 / MDD 43.53%. Stack ganha com METADE
do notional. Confirma `[risk_parity, ch.5, p.10]` Carlson empiricamente.
(4) **Pela primeira vez no hunt, dois configs simultaneamente passam
todas as 3 barras** (stack + LETF), mas o rubric seleciona stack via
Sharpe.

**Por que F1 perde no rubric apesar de ser melhor em Sharpe + MDD**:
mean CAGR 11.95% fica só 0.74pp acima da barra 11.21%, dando 14/30
pontos no eixo CAGR (anchor 5-20%). Iter 006 closest-to-winner com
17.33% CAGR ganha 25/30. O rubric CAGR-anchored é **intencional** (vide
`WINNER_AND_RANKING.md`: "rubric prioritizes CAGR (30pts) over Sharpe
(10pts) intentionally — opposite of long_term_portfolio's Sharpe-first
rubric"), mas penaliza estruturalmente arquiteturas balanced-multi-asset.

**Padrão "All-Weather" empírico bonito**: F1 stack 5y rolling
pass-rate vs SPY = **33%** (subperforma SPY no bull recente), 10y =
46%, 15y = 62%, **20y = 100%** (BATE SPY em TODA janela rolling de 20
anos!). É o trade-off clássico que o usuário já manifestou
preocupação: matemática de longo prazo favorece, comportamento de curto
prazo dói.

Tabela final 7-famílias + 1-hybrid: A2 TQQQ-track **67**, A1/A3
SPY-track 66, E1 hybrid 65, B1/B2 HFEA 63, **F1 Levered All-Weather
61** (Sharpe 1.018 best in hunt; MDD 26.82% best entre passers), C1
vol-target 60, D1 concentrated+TSMOM 59 (MDD overall best 35.27%), D2
stacked equity 52.

**Possível trigger pra mandate §7 review**: F1 stack é empiricamente o
melhor config de risk-adjusted return + drawdown control no hunt
inteiro. Sob rubric Sharpe-anchored ou MDD-anchored seria WINNER. Vale
pergunta: a missão spy_beater "CAGR-mean-only" continua defensável, ou
risk-adjusted criteria devem disparar revisão de rubric? **Não decido
isso sozinho** — fica registrado como observação pra próxima sessão com
usuário.

Negative-result policy agora fica em "**7 single-axis families + 1
cross-product hybrid ≤ 67**", cumulative_n_trials = 47, worst DSR p =
**2.66e-05** (best margin do hunt inteiro por 2 ordens de grandeza —
F1 stack tem Sharpe tão alto que cumulative trials nem ameaçam).
F1+SPLIT incumbent fallback (que aliás é a MESMA família F1 com pesos
um pouco diferentes) permanece deploy-ready; mandate §1 100% Plano C
inalterado. Suggested iter 016+: NONE — hunt CLOSED.

Notas operacionais: zero código novo (`type=static` reusa
`portfolio_returns_from_config`), 765 testes baseline mantidos, 3
configs adicionando 3 ao n_trials cumulativo. NTSX/GDE/TMF/UGL todos
wired via testfolio cache + long_term_portfolio.proxies. PBO N=3
warning persiste (lh_56y 0.81 alto, spy_real 0.40 ok), G3 walk-forward
falha por 1.82pp em lh_56y mas spy_real passa 7/7 garantindo
cross_met.

Citações: Bridgewater All-Weather (Dalio 1996, public papers 2011) —
KILL #49 confirma ceiling histórico ~7-8% CAGR; Asness 1996 "Why Not
100% Equities?" JPM — leverage-balanced thesis confirmada no Sharpe
peak a 1.41× e refutada no LETF 2.25× pelo decay; `[risk_parity, ch.5,
p.10]` Carlson — capital-efficient stacking Pareto-domina LETF
empiricamente; `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed —
LETF decay magnitude confirmada (~10-15% drag em Sharpe a 2.25×);
`[ilmanen_expected_returns, ch.19]` — KMLM crisis-alpha necessário mas
não suficiente; `[advances_fin_ml, p.31-34]` factor framework —
risk-parity como família arquitetural distinta; `[advances_fin_ml,
p.222-223]` DSR n=47 worst p=2.66e-05; `[advances_fin_ml, p.208-211]`
PBO N=3 warning; `[advances_fin_ml, p.196-202]` bootstrap CI G6 passou
folgado (lh 0.569, spy 0.368).
