# spy_beater_hunt iter 025 — H5 meta-ensemble gate-composition 4-way (70/100, bars 3/3 PASS)

## O que foi feito

Testamos a 9ª iteração no eixo meta-ensemble (5 sequenciais agora: 018→019→020→021→025 = 70→71→67→70→70). A hipótese de iter 024 era que o gate composition do G3 4040 (KILL #94 NEW PRINCIPLE: dois efeitos ortogonais — bear-avoidance + redução de leverage efetivo via exposição tempo-média) STACKS com a meta-axis decorrelation do iter 019 (3-way A2 + G2 IEF + F1 stack).

5 configs sweeping (a) 4-way 25/25/25/25 substituindo G1 IEF por G3 4040; (b) substituições 3-way de F1 stack ou G2 IEF por G3; (c) 4-way assimétrico com dose menor de G3; (d) 3-way com F1 dominante compensando MDD do G3.

## Resultado

**Tier PROMISING 70/100, bars 3/3 PASS, winner_met = True.** Selecionado `h5_meta_4way_25a2_25g2_25f1_25g3` (4-way equal-weight): CAGR 15.37%, **MDD 30.43% IDÊNTICO entre os dois datasets (lh_56y E spy_real)**, Sharpe 1.027, gates 6/7+5/7. **Todas as 5 configs passam as 3 barras** — quinto sweep 100% bar-pass do hunt (depois de iter 019/020/021/024).

H5.1 em 70 é o **NEW 2nd-best score** do hunt inteiro (empate triplo com iter 018 H1 e iter 021 H4).

## Achado mais importante (KILL #96 NOT FIRED — NEW PRINCIPLE)

H5.1 4-way 25/25/25/25 (com G3 4040) score **70 > iter-020 H3 4-way 25/25/25/25 (com G1 IEF) score 67 por +3pts**. Empiricamente, **G3 4040 (CAGR-passing high-MDD) é um 4° constituinte MELHOR do que G1 IEF (CAGR-fail low-MDD) dentro da estrutura 4-way meta-axis**.

NEW PRINCIPLE: A estrutura 4-way meta-axis paga uma "diversification-tax" base de −1pt vs o 3-way (saturação rubric Sharpe + sensibilidade do eixo Gates ao PBO do constituinte adicional). MAS se o 4° constituinte FALHA na barra de CAGR, paga adicional −3pts via penalty no eixo CAGR. Conclusão: **a CAGR solo do 4° constituinte ≥ 11.21% é o critério primário pra seleção**. Mecanismo: o 15.79% solo do G3 lifta o CAGR do blend; o MDD 44.71% solo é diluído para 30.43% pelo absorption dos 3 outros constituintes.

## Por que não bate o teto de 71

Score breakdown vs iter-019 (71→70, −1pt): CAGR +1pt (15.04→15.37%), MDD −1pt (28.50→30.43%), **Gates −1pt dominante** (lh 6/7+spy 6/7 → lh 6/7+spy 5/7, provavelmente G1 PBO 0.786 strict-fail no grid N=5; cross_met preservado por threshold counting), DSR/Sharpe/Robustness empatados.

**Achado único**: MDD 30.43% **idêntico entre os dois datasets** sugere dominância do GFC 2008 compartilhada — sinal de robustez não capturado pela rubric. **5ª classe de rubric saturation documentada**: Gates+MDD-cross-axis-saturation — Sharpe lift (+0.002) + DSR mais apertado (1.55e-04 → 1.25e-04) + identidade cross-dataset de MDD são todos INVISÍVEIS à rubric.

## Outros resultados das KILLs

- KILL #95 FIRED: max 70 ≤ 71 → meta-axis ceiling DEFINITIVO em 71 (9ª confirmação)
- KILL #97 NOT FIRED: substituir F1 stack por G3 não Pareto-domina iter 019 (Sharpe 0.963 mais baixo dos 5)
- KILL #98 NOT FIRED HARD: substituir G2 IEF por G3 dá score similar (gate-source signal importa mais que sleeve composition)
- KILL #99 NOT FIRED: max 70 < 75 STRONG → ceiling claim STANDS
- KILL #100 NOT FIRED: max Sharpe 1.027 < 1.05 (3rd-best mean Sharpe entre CAGR-passers)

## Recomendação

9-axis architectural taxonomy + cross-product-hybrid-meta-integration test agora **COMPLETA**. Recomendação STRONGER que iter 024: declarar hunt EFFECTIVELY-CLOSED em iter 025 — ceiling validado em 5 iters sequenciais no meta-axis + integração de cross-product-hybrid testada. F1+SPLIT confirmado deploy fallback. 25 iters preservadas (50% do budget). Mandate §7 review case fortalecido pra 9ª iter (após 015 F1, 016 G1, 018+019+020+021 metas, 022 B5, 023 B7, 024 G3, agora 025 H5.1). Mandate §1 100% Plano C UNCHANGED — research only.

Citações: `[advances_fin_ml, ch.16, p.241-256]` portfolio construction; `[risk_parity, ch.5, p.10]` Carlson; `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed (triple-gate-source); `[ilmanen_expected_returns, ch.19]` MF crisis-alpha; HFEA Bogleheads 2019; Bridgewater All-Weather (Dalio 1996); `[advances_fin_ml, p.222-223]` DSR n_trials=96; `[advances_fin_ml, p.208-211]` PBO N=5.
