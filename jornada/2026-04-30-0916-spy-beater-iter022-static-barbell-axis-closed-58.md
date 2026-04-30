# spy_beater iter 022 — sexto eixo arquitetural fecha em 58, taxonomia completa

iter 022 testou um eixo que ainda estava em branco no spy_beater_hunt: a
**barbell estática modesta** (3× UPRO + 1× TLT, sem gate LRS, sem 3× TMF).
A motivação veio direto do WINNER_AND_RANKING.md: estratégias buy-hold
estáticas têm vantagem estrutural de ~1,5pp no rubric líquido vs LRS/blends,
porque o tax drag é só 0,6pp em vez de 1,9-2,1pp.

**Resultado**: a config selecionada (40% UPRO + 40% TLT + 20% KMLM)
passou as 3 barras (CAGR 14,13% / MDD 54,47% / gates 6/7+6/7), mas com
score 58 — o MAIS BAIXO entre todas as 22 iters que já passaram bars 3/3
no hunt. Margem MDD apertadíssima: 0,7pp abaixo da bar 55,17%.

**Achado mais relevante**: a hipótese implícita "o problema da HFEA é o
2022" estava ERRADA. O backtest 40-y mostra que 2008 GFC domina o MDD em
barbells alavancadas. A troca TMF→TLT eliminou o decay LETF mas tirou o
buoy de 2008 (TMF rallied +75%, TLT só +25%) — e por isso o pure 50/50
UPRO/TLT teve MDD 69% (1,6pp PIOR que a HFEA classical de iter 008).

**Achado teórico-prático (KILL #79 firou)**: KMLM crisis-alpha tem
efetividade INVERSAMENTE PROPORCIONAL à alavancagem nocional do backbone.
A HFEA classical (300% nocional) diluiu o KMLM (KILL #27 fechou); a
HFEA-modesta (200% nocional) aceitou KMLM e ganhou Sharpe. Generalização
útil para futuros stacks.

**Status do hunt**: 6 eixos arquiteturais agora mapeados (LRS-mono 67,
Hybrid 65, Static-multi 63, Meta-ensemble 71 = teto, Vol-target 60,
Static-barbell-modest 58 NOVO). Taxonomia ESTRUTURALMENTE COMPLETA.
22/50 iters usadas. Recomendação: opção (A) — declarar hunt
efetivamente fechado, F1+SPLIT confirmado como deploy fallback, 28
iters poupadas para hunts futuros. Mandate §1 100% Plano C inalterado.

**Score breakdown vs closest-to-winner (iter 019, gross 71→58, −13)**:
−10 do MDD (54% MDD pontua só 5/20 no rubric) + −2 Sharpe + −2 CAGR
+ +1 robustness. O eixo MDD do rubric (anchor [0.7, 0.15]) penaliza
barbells mesmo quando passam a bar — MDD 50%+ só rende 0-5pts.
