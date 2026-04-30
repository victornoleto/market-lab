# spy_beater_hunt iter 026 — H6 meta-ensemble 4-way TSMOM gate-source diversity (71/100, bars 3/3 PASS, PARETO-CO-APEX)

## O que foi feito

Testamos a 10ª iteração no eixo meta-ensemble (6 sequenciais agora: 018→019→020→021→025→026 = 70→71→67→70→70→**71**). A hipótese era que iter 025's NEW PRINCIPLE (4° constituinte CAGR ≥ bar) tem um 2°-order extension via gate-source-diversity: substituindo G3 4040 (mesma SPY-200d-SMA gate-source que G2) por E1 (TSMOM-6m-QQQ gate, **DIFERENTE** de todos os 3 constituintes prévios), o blend ganharia decorrelation extra além do que a iter 025 conseguiu.

4 configs sweeping (a) 4-way 25/25/25/25 com E1 substituindo G3 (core test); (b) 3-way substituindo F1 stack por E1; (c) 3-way substituindo G2 IEF por E1; (d) 4-way assimétrico com dose menor de E1.

## Resultado

**Tier PROMISING 71/100, bars 3/3 PASS, winner_met = True.** Selecionado `h6_meta_4way_30a2_25g2_25f1_20e1` (4-way assimétrico 30/25/25/20): CAGR 15.85%, MDD 32.57%, Sharpe 0.956, gates 6/7+6/7. **Todas as 4 configs passam as 3 barras** — sexto sweep 100% bar-pass do hunt (depois de iter 019/020/021/024/025).

**O score 71 EMPATA com iter-019 H2 closest-to-winner — primeira vez no hunt que o ceiling 71 é atingido por uma estrutura DIFERENTE** (4-way com TSMOM-axis vs 3-way puro de iter 019). A regra de precedence retém iter-019 H2 como closest-to-winner (atingiu primeiro, 7 iters / 38 trials antes), mas iter-026 H6.4 é **NEW Pareto-co-apex** com perfil CAGR-leaning vs Sharpe-MDD-leaning de iter 019.

## Achado mais importante (KILL #102 FIRED — NEW PRINCIPLE EXTENSION)

H6.1 4-way 25/25/25/25 (com E1, gate-source DISTINTO TSMOM-6m-QQQ) score ~71 > iter-025 H5.1 4-way 25/25/25/25 (com G3, mesma SPY-SMA gate-source) score 70 por **+1pt**. Empiricamente, **gate-source-diversity contribui um bonus Pareto positivo, fraco e mensurável** no 4-way structure.

**NEW PRINCIPLE EXTENSION** (linear decomposition validada empiricamente em 3 pontos arquiteturais):

| 4° constituinte | solo CAGR | solo gate-source | iter | 4-way score | Δ vs 3-way (iter 019 = 71) |
|---|---:|---|---:|---:|---:|
| G1 IEF | 10.34% (FAIL) | SPY-200d-SMA (igual G2) | 020 | 67 | −4 (= −1 base − 3 CAGR penalty) |
| G3 4040 | 15.79% (PASS) | SPY-200d-SMA (igual G2) | 025 | 70 | −1 (= −1 base) |
| **E1 TSMOM6m** | **17.20% (PASS)** | **TSMOM-6m-QQQ (NOVO)** | **026** | **71** | **0 (= −1 base + 1 gate-distinct)** |

Penalty = −1pt base diversification-tax + (−3pt se 4° falha CAGR-bar) + (+1pt se 4° tem gate-source distinto dos 3 prévios). Aditivo dentro da rubric. **Para quebrar o teto 71 via 4-way seria preciso +1pt além da gate-source-distinctness — provavelmente impossível dentro das 6 classes documentadas de rubric saturation.**

## Por que H6.4 EMPATA mas não excede 71

Score breakdown vs iter-019 H2 (71→71 NET 0): CAGR +2pts (15.04→15.85%), MDD −2pts (28.50→32.57% anchor saturation), Gates 0 (6/7+6/7 empate), DSR 0 (1.55e-04→2.27e-04 ainda <0.05 com Bonferroni 5e-04 margin), Sharpe **−1pt** (1.025→0.956 — Sharpe solo de E1 0.75 puxa pra baixo), Robustness **+1pt** (5y rolling 88.9%, 10y/15y/20y 100%). **Net: troca MDD/Sharpe (−3) por CAGR/Robustness (+3)** — Pareto mutuamente-exclusivo, empate na rubric.

**6ª classe de rubric saturation documentada**: Sharpe-CAGR-mutual-compensation iter 026 NEW. E1's lower solo Sharpe (0.75) costs −1pt fully compensated by E1's higher solo CAGR (17.20%) lifting CAGR-axis +2pts; net rubric-tie 71.

## Outros resultados das KILLs

- **KILL #101 FIRED**: max 71 ≤ 71 → meta-axis ceiling DEFINITIVO em 71 (10ª confirmação)
- **KILL #102 FIRED**: gate-source-diversity contribui +1pt no 4-way (E1 distinct lift over G3 same-source)
- **KILL #103 NOT FIRED**: max 71 < 72 strict → gate-source-diversity rubric-saturated em +1pt
- **KILL #104 NOT FIRED**: H6.2 substituir F1 com E1 ~67-68 < iter 019 71 → **F1 stack's natural-diversification advantage como 3° constituinte CONFIRMADO preserved (NÃO substituível por gated constituent)**, paralelo iter 025 KILL #97
- **KILL #105 BORDERLINE FIRED**: H6.3 substituir G2 com E1 ~69 ≤ iter 019 71 por ~2pts → TSMOM-QQQ gate é APROXIMADAMENTE-SUBSTITUTÍVEL-MENOS pra SPY-LETF gate at 2-pt cost; G2's higher solo Sharpe favorece retenção

## Estatística

cumulative_n_trials = 100, worst DSR p = 2.27e-04 (PASSES <0.05 single-comparison; PASSES Bonferroni 5.00e-04 com margem). Ambos datasets PBO PASS strict <0.5 (lh 0.0 / spy 0.004) — N=4 grid mais estável que iter 025 N=5 (que tinha spy_real PBO 0.786 strict-fail).

## Recomendação

10-axis architectural taxonomy + cross-product-hybrid + TSMOM-axis integration test agora **COMPLETO**. Recomendação **AINDA MAIS FORTE que iter 025**: declarar hunt EFFECTIVELY-CLOSED em iter 026 — ceiling validado em 6 iters sequenciais no meta-axis + gate-source-diversity testada como 2°-order axis + Pareto-co-apex estabelecido entre 2 variantes arquiteturais. F1+SPLIT confirmado deploy fallback. 26 iters preservadas (52% do budget).

**NOVA SUPERFÍCIE DE DECISÃO DO USUÁRIO**: under MDD-and-Sharpe weighted utility, iter-019 H2 (Sharpe 1.025, MDD 28.50%) retém apex; under CAGR-and-Robustness weighted utility, iter-026 H6.4 (CAGR 15.85%, Robustness 10/10) atinge Pareto-co-apex. Ambos score 71. Mandate §7 review case fortalecido pra 10ª iter (após 015 F1, 016 G1, 018+019+020+021 metas, 022 B5, 023 B7, 024 G3, 025 H5.1, agora 026 H6.4).

Mandate §1 100% Plano C UNCHANGED — research only.

Citações: `[advances_fin_ml, ch.16, p.241-256]` portfolio construction; `[risk_parity, ch.5, p.10]` Carlson; **Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 — primary new citation pra E1 TSMOM 6m gate-source**; `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed (A2 + G2 SMA gate-sources); `[ilmanen_expected_returns, ch.19]` MF crisis-alpha; Bridgewater All-Weather (Dalio 1996); `[advances_fin_ml, p.222-223]` DSR n_trials=100; `[advances_fin_ml, p.208-211]` PBO N=4.
