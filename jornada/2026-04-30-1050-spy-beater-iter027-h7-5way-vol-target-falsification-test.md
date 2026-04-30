# spy_beater iter 027 — H7 5-way meta-ensemble: vol-target gate-source-diversity FALSIFICATION TEST

**Tier**: PROMISING 70/100 (gross), 64/100 (net)
**Bars**: 3/3 PASS — winner_conditions_met=True
**closest-to-winner**: UNCHANGED — iter-019 H2 retém 71 (iter 026 H6.4 também retém Pareto-co-apex at 71)

## O que foi testado

A iteração 026 estabeleceu um **princípio de decomposição linear** para meta-ensembles 4-way: o teto de 71 pontos (do 3-way iter 019) é mantido se o 4° constituinte tem solo CAGR ≥ bar (11.21%) E gate-source distinto dos 3 prévios. A iter 027 testou se esse princípio se estende a 5-way: adicionar C1 vol-target (Carver, gate-mechanism distinto de SMA-cross e TSMOM-momentum) como 5° constituinte com diversidade máxima de gate-sources (5 mecanismos distintos: QQQ-200d-SMA × SPY-200d-SMA × always-on × TSMOM-6m × vol-target).

## Resultado

4 configs testadas — **todos os 4 PASSAM bars 3/3 (7° sweep 100% bar-pass na história do hunt)**. Selecionado: **H7.3 4-way 25/25/25/25 com C1** substituindo E1 — score **70**, 1pt abaixo do teto.

A configuração 5-way equal-weight (H7.1) e 5-way assimétrica (H7.2) ambas tiveram Sharpe 0.94 vs o 4-way 0.98, **mostrando que adicionar 5° constituinte custa mais que ganha**. KILL #107 disparada: linear decomposition CONFIRMADA como upper-bound; 5-way axis CLOSED.

## Achado novo (princípio empírico)

Pure gate-source-distinctness não é suficiente para o bônus +1pt completo: o constituinte adicional precisa TAMBÉM ter CAGR-runway competitivo com closest-to-winner (~15%+). E1 TSMOM com 17.20% solo CAGR ganhou +1pt completo (iter 026); C1 vol-target com 13.54% ganhou só parcial — perdeu 2pts no eixo CAGR que o +1pt distinct não compensou. Sub-princípio iter 027: 4-way meta selection tem 3 componentes (CAGR-floor + gate-source distinctness + **CAGR-runway adequacy NEW**).

## F1 stack triple-confirmation

H7.4 (3-way substituindo F1 stack por C1) também perdeu — Sharpe 0.922 mais baixo de todos os 4 configs. Isso é a **3ª confirmação** (após iter 025 vs G3, iter 026 vs E1, agora iter 027 vs C1) de que o F1 stack always-on multi-asset é uniquely-Pareto-optimal como 3° constituinte em meta-ensembles 3-way. Não é coincidência.

## Implicação prática

11 iterações no eixo meta-ensemble confirmam o teto em 71. Cumulative_n_trials = 104; DSR ainda passa Bonferroni 4.81e-04 com margem. Mandate §1 100% Plano C inalterado — research only. **Recomendação**: declarar hunt effectively-closed em iter 027 (54% do budget de 50 iters preservado).

## Citações

`[advances_fin_ml, ch.16, p.241-256]` portfolio construction (5-way); `[systematic_trading, ch.10]` Carver vol-targeting (C1 NEW gate-mechanism); `[risk_parity, ch.5, p.10]` Carlson stacking; Moskowitz-Ooi-Pedersen (2012) TSMOM (E1); `[leverage_for_the_long_run, ch.3-4]` Gayed (A2/G2); `[ilmanen_expected_returns, ch.19]` KMLM crisis-alpha; `[advances_fin_ml, p.222-223]` DSR Bonferroni; `[advances_fin_ml, p.208-211]` PBO; `[advances_fin_ml, p.31-34]` factor framework.
