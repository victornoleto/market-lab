# spy_beater iter 009 — HFEA + KMLM crisis-alpha não passa, B2 fechada

A hipótese da iter 009 era simples: HFEA estilo Bogleheads (UPRO 3× SPY
+ TMF 3× LTT) tinha morrido no 2022 (iter 008, MDD 67%), e o reflexo
natural da literatura era adicionar KMLM (managed-futures crisis-alpha)
para compensar a queda concorrente de bonds + stocks. Pegamos 50% UPRO
fixo e variamos KMLM em 15%/20%/25% (substituindo TMF 35%/30%/25%).

A KMLM cortou 6pp do MDD imediatamente — saiu de 67% (iter 008 só HFEA)
para 61% (iter 009 com 15% KMLM). Mas aí parou. Aumentando para 20% e
depois 25%, o MDD começou a SUBIR de novo (61.27% → 61.51% → 61.78%).
O Sharpe ficou flat-to-degrading. Score final: 63/100, mesmo número
da iter 008. A barra de MDD ≤ 55.17% NÃO foi atingida em nenhuma
config. **KILL #27 disparou** e B2 está fechada.

A descoberta interessante é que o KMLM se comporta de forma **oposta**
no HFEA versus no SPY-track. Nas iters 003-005 (KMLM em cima de SPY
buy-hold + LRS gate), aumentar KMLM de 0% até 30% cortou ~15pp de MDD
e fez o Sharpe subir monotonicamente. Aqui no HFEA, depois do "primeiro
dose" de 15%, mais KMLM só piora. A explicação: no HFEA, TMF e KMLM
estão competindo pelo mesmo "slot de diversificador" — ambos cobrem
regimes diferentes (TMF protege em 2008 quando juros caem; KMLM protege
em 2022 quando juros sobem) — então trocar um pelo outro só
reembaralha quais regimes você está hedgeado, não soma proteção.

Estado do hunt: 9 iters, ainda sem WINNER. Closest-to-winner continua
sendo iter 006 (TQQQ-track + KMLM30 + TLT10) com score 67. Já
fechamos: A1, A2 (faster signal, threshold buffer, lower-leverage,
TQQQ-track), A3 (mixed, dose, TLT-extension), B1 (HFEA classical) e
agora B2 (HFEA+KMLM). O único candidato Tier 1-2 que sobrou é C1
vol-targeted (escala leverage com vol realizada — geometria diferente,
não é gate de regime nem barbell estático).

Próxima sessão: iter 010 = C1. Se C1 também cap ar ~67, declaramos
IMPOSSIBILITY_RESULT — a barra é arquiteturalmente inalcançável dentro
do framework gross-of-tax 2-dataset, e F1+SPLIT da long_term_portfolio
fica como deploy fallback confirmado. O resultado negativo honesto
tem valor de policy.

**Citações**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed
LETF decay; `[ilmanen_expected_returns, ch.19]` MF crisis-alpha
(efeito "primeiro dose" saturado em 15% sobre HFEA, não documentado
em SPY-track); `[risk_parity, ch.5, p.10]` Carlson stacking não-aditivo
quando dois diversificadores cobrem regimes complementares;
`[advances_fin_ml, p.31-34]` factor framework — UPRO é o concentrated
risk (não TMF) a 165% notional, e KMLM/TMF são fatores distintos com
betas em regimes diferentes; `[advances_fin_ml, p.222-223]` DSR
cumulative n_trials=32, worst p 3.07e-03 << 0.05.
