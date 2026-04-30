# spy_beater iter 023 — NTSX low-leverage axis fecha em 57, taxonomy 7-axis completa

**Status**: MARGINAL 57/100, bars 2/3 (CAGR FALHA por 0.51pp), KILL #83 FIRED HARD,
KILL #85 FIRED (KILL #79 generalização confirmada e fortalecida), KILL #86 FIRED,
KILL #87 NOT FIRED — novo achado. closest-to-winner UNCHANGED (iter-019 71).

## O que foi testado

B7 NTSX-anchored low-leverage static — 7º eixo arquitetural. Pivô do iter 022 B5
(barbell modesto a 200% notional via 3× UPRO + 1× TLT) para um nível ainda mais
baixo: 150% notional via NTSX 100% (stack interno 90/60 SPY/UST por
`[risk_parity, ch.5]` Carlson). Hipótese central: a generalização KILL #79 do
iter 022 ("MF crisis-alpha effectiveness é INVERSAMENTE proporcional à backbone
notional leverage") deveria render lift de Sharpe ainda maior a 1.5× notional do
que a 2× notional. 6 configs sweep NTSX 100% baseline + KMLM/DBMF/TLT dose-
response.

## O que aconteceu

Selected `b7_ntsx70_kmlm20_tlt10`: CAGR mean 10.70% **FALHA** bar 11.21%, MDD
25.81% PASS, gates 6/7+7/7, Sharpe 0.968 — score 57. Apenas 2 de 6 configs
passam todos os 3 bars (b7_ntsx100 12.13%/44.98% + b7_ntsx80_kmlm20
11.29%/30.99%). O scorer escolheu o config com MDD/Sharpe melhor mesmo
falhando o CAGR-bar — **3ª classe de RUBRIC SATURATION documentada**: scorer
não é bar-aware, premia MDD+Sharpe sobre CAGR-bar-binário. KILL #85 disparou
forte: lift +0.130 (KMLM 20% sobre NTSX 100% baseline) — mais forte do que
+0.038-0.084 a 200% notional. **MF effectiveness MONOTONIC INCREASING in
inverse-leverage** confirmado em 3 pontos arquiteturais (300%→200%→150% =
0→0.084→0.130). KILL #87 NOT FIRED revelou achado oposto: split MF
(KMLM+DBMF) Sharpe 0.851 < single-source 0.912 — DBMF DILUI KMLM a 1.5×
backbone. No regime de baixa alavancagem, **MF concentration > MF
diversification**.

## Tradeoff fundamental confirmado

A trajetória 3-iter de leverage (300%/200%/150%) confirma: notional menor →
melhor Sharpe + MDD + lift de MF, MAS menor CAGR runway. O eixo estático não
consegue SIMULTANEAMENTE satisfazer CAGR bar e bater os 71 pontos do meta-
axis. Robustez 5y rolling colapsou de 88.9% (B5) para 33.3% (B7); 20y rolling
de 100% para **0%** — estratégia perde para SPY em TODA janela de 20 anos.

## Implicação

7-axis architectural taxonomy COMPLETO: Meta-ensemble 71 (H2), LRS-mono 67 (A2),
Cross-product hybrid 65 (E1), Static-multi 63 (B2), Vol-target 60 (C1),
Static-barbell modest 58 (B5), Static-low-leverage 57 (B7 NEW). Ceiling
arquitetural a 71 (meta-axis) é o máximo funcional dentro do rubric. F1+SPLIT
permanece deploy fallback. Mandate §1 inalterado. Próxima decisão (usuário): (A)
declarar hunt EFFECTIVELY-CLOSED — opção mais defensável; (B) testar C2 CAPE-
timing (low credibility, alto custo de infra); (C) pivot para mandate §7
rubric-revision (7º iter com config rubric-subótimo mas honest-attribute).

cumulative_n_trials = 86. Sem nova infra (reusa 'static' spec). 771 testes
preservados.
