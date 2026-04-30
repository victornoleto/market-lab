# spy_beater iter 011 — IMPOSSIBILITY_RESULT, hunt fechado em 10 iters

A iter 011 não testou nenhuma estratégia nova. Foi uma **meta-iter
de síntese**: após 10 iters cobrindo 4 famílias arquiteturais
distintas (A1/A3 LRS sobre SPY, A2 LRS sobre TQQQ, B1/B2 HFEA, C1
vol-target), nenhuma chegou perto do score 90 que define o tier
WINNER no rubric do spy_beater. O melhor foi a iter 006/007 com
67/100 — uma diferença de 23 pontos para o WINNER, sendo que o
maximum aritmético plausível de melhoria por critério é só +19
(CAGR +5 + MDD +12 + Sharpe +2). Em outras palavras: o teto de
~75-86 está estruturalmente abaixo de 90, e nenhuma reorganização
de pesos vai fechar isso.

Disparei a **KILL #33** nova (estrutural — ceiling arquitetural)
para nomear esse padrão: "≥4 famílias × ≥3 iters/família ×
cumulativo ≥30 trials → se best-score < 75, fecha". Adicionalmente,
KILL #34 (estabilidade do rubric) e KILL #35 (sanity vs F1+SPLIT)
**não** dispararam, confirmando que o teto é real e não artefato
metodológico. O F1+SPLIT scoraria ~59 nesse mesmo rubric, abaixo
do closest-to-winner — o que faz sentido, já que ele troca CAGR
por MDD por design e o spy_beater pune especificamente o gap de
CAGR.

O hunt foi fechado em 10 iters dos 50 planejados. A razão não é
falta de paciência: é que os caminhos Tier 1-2 da literatura
foram **todos** testados (Gayed, HFEA, Carver vol-target,
crisis-alpha), e os Tier 3 (D1 momentum-only, C2 CAPE-timing, D2
NTSX+UPRO+AVUV stack) foram pré-marcados com ~5%/iter de
probabilidade de quebrar 67 — o custo de mais 40 sessões para um
ganho marginal não se justifica, e a inflação de `n_trials` na
penalidade DSR só piora a posição estatística.

Conclusão de policy: 53 iters cumulativos honestos
(long_term_portfolio 43 + spy_beater 10) **não acharam** uma
estratégia que bate SPY em CAGR **e** MDD simultaneamente no
framework de 2 datasets (lh_56y synth + spy_real Tiingo). O F1+SPLIT
(NTSX 25 + GDE 25 + KMLM 17.5 + DBMF 17.5 + TLT 15) se confirma
empiricamente como o melhor candidato honesto de deploy. Mandate §1
(100% Plano C passive factor-tilted) **não muda**. Sem pedido de
override §7 — a hunt simplesmente não produziu candidato WINNER.

O resultado negativo tem valor: agora sabemos, com 35 trials e
DSR worst p ≤ 5e-3 honestamente acumulados, que o CAGR-anchored
rubric de 30/20/20/10/10/10/5 sobre lh_56y+spy_real é incompatível
com o toolkit canônico de leverage + regime-gate + crisis-alpha +
vol-target. Próxima reabertura (se houver) precisará de
arquiteturas fora dessa caixa — vol-target sobre NTSX (não LETF),
HFEA com diversificador não-TMF (commodities/GLD), ou
multi-horizon-conditional rebalancing. Anotado em
`FINAL_REPORT_spy_beater_failed.md` no nível do loop.

**Citações:**
- `[advances_fin_ml, p.31-34]` — framework de fatores: 4 famílias
  cobrem o espaço leverage × timing × diversificação; ausência de
  WINNER é resultado negativo estrutural.
- `[advances_fin_ml, p.222-223]` — DSR cumulative_n_trials=35
  preservado; fechar mantém integridade estatística.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking
  (F1+SPLIT) é o fallback de deploy.
- HFEA Bogleheads 2019 — barbell falsificado em 2022 stress; claim
  risk-parity 55/45 é regime-específico de 1986-2019.
