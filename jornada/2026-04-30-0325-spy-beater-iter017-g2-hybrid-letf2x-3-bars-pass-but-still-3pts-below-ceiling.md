# Iter 017 — Adicionar gate à versão LETF da Levered All-Weather agora passa as 3 barras, mas score continua 3pts abaixo do teto

Continuação do spy_beater_hunt (fechado pela iter 011, seguimos em modo
sanity-check arquitetural). Iter 017 testou a "G2": pegamos a F1 LETF
2× do iter 015 (30 UPRO + 25 TMF + 15 IEF + 15 UGL + 15 KMLM, ~2.25×
notional) e adicionamos o mesmo gate Gayed 200d SMA do iter 016. Três
configs sweep no off-state defensivo (100% IEF, 100% KMLM, 50/50 blend),
exatamente como iter 016.

Resultado mais animador desde o iter 006: **TODAS as 3 configs passam
TODAS as 3 barras estritas** (CAGR ≥ 11.21%, MDD ≤ 55.17%, gates
≥ 5/7). Primeiro iter na história da hunt com sweep 3/3 em todos
configs. Selecionado g2_f1_letf_2x_sma200_ief: CAGR 14.02% (passa por
2.81pp), MDD 33.72% (passa por 21pp de margem), Sharpe 0.97, gates
6/7 + 6/7 — score **64/100** (PROMISING). Apenas **3pts abaixo** do
closest-to-winner iter 006 (67).

A descoberta é que o iter 016 path-to-90 analysis tinha previsto:
"adding regime gate to LETF 2x F1 → estimated 60-65, same architectural
ceiling". Observamos 64 — predição confirmada matematicamente. Isso
encerra o mapeamento da superfície gate × sleeve em 3 pontos do eixo
de decay (no-decay 1.41× → score 61, moderate-decay 2.25× → score 64,
decay-dominated 3× → score 65). Score é **não-monotônico** mas Sharpe,
MDD e CAGR são monotônicos com decay. Os 3 hybrids cluster em range
estreito 61-65, todos abaixo do A2 single-axis 67. Decay-axis fully
mapped — KILL #33 generaliza com confiança "8 fams + 3 hybrids".

Um achado surpresa importante: a G2 BLEND (50/50 IEF+KMLM off) tem
**MDD de 26.76% — segundo-melhor da hunt**, atrás só da G1 IEF
(18.57%). Isso quebra o padrão monotônico do iter 016 (IEF > 50/50 >
KMLM em todas as métricas) — no LETF 2× a contribuição do KMLM
crisis-alpha como defensivo virou material (deu 7pp de relief de MDD
extra). A magnitude do KMLM vale conforme a vol do sleeve: insignificante
no stack 1.41×, importante no LETF 2.25×.

Outra descoberta: o iter 016 mostrou que adicionar gate destruía o
20y rolling SPY-beating do F1 (100%→0%); o G2 não tem esse problema —
mantém 100% nas janelas de 20y. A alavancagem do LETF 2× compensa o
custo de "miss bull rally" do gate. Long-horizon SPY-beating depende
do CAGR runway do sleeve: stack 1.41× tem ~6-7% off-gate (insuficiente),
LETF 2.25× tem ~14% off-gate (sobra).

Hunt segue CLOSED. Pareto frontier de CAGR-passers atualizado: A2 67
(top), E1 65, **G2 IEF 64** (3rd, com Sharpe + MDD muito melhores que
top-2), G2 BLEND ~63, F1 LETF ~60, F1 stack 61. Sob rubric que valoriza
risk-control, G2 IEF/BLEND seriam preferidos. Caso para revisão §7 do
mandate fica reforçado: agora 4 configs textbook risk-control passing
3/3 bars todos travam abaixo do A2 67-cap. F1+SPLIT mantém deploy.
Mandate §1 100% Plano C unchanged. cumulative_n_trials = 53, worst DSR
p = 9.50e-05. 765 testes preservados (nenhum módulo novo).
